#!/usr/bin/env python3
"""Restock and price watcher for the PokeBindr 401 Games watchlist.

Runs every 30 minutes from .github/workflows/store-watch.yml. The daily
price-history job (in the PokeBindr repo) resolves the wishlist to 401 listings
and publishes them as price-history/401/watchlist.json on gh-pages; this script
reads each listing's /products/{handle}.js, compares it with the last reading,
and pushes an ntfy notification when a watched condition comes back in stock,
drops in price, or is down to its last copy.

Each alert goes only to the people who asked for that card: users who turned on
401 alerts in the app's Settings and have it on their wishlist, each on the
ntfy topic their app generated. Those are read from Firestore every run and
never written anywhere, so the public repo holds no topic or wishlist-owner.
Cards in the PokeBindr repo's extras file alert NTFY_TOPIC instead.

State (the last reading of every listing) lives in the Actions cache, not in
git. price-history/401/stock.json — what the app shows — is rewritten only when
a price or stock count changed, or every few hours so the app can tell fresh
data from stale. Stdlib only, except google-cloud-firestore for the routing.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

STORE = "https://store.401games.ca"
CONDITIONS = ("NM", "SP", "MP", "HP", "DMG")
UA = {
    "User-Agent": "PokeBindr-401-watch/1.0 (personal watchlist; +https://herickchann.github.io)",
    "Accept": "application/json",
}
# A price drop smaller than this is 401 rounding, not news.
DROP_RATIO = 0.97
# stock.json is rewritten at least this often so "checked" stays meaningful.
HEARTBEAT = timedelta(hours=6)
MAX_ALERTS = 10
# Synced preferences (lib/data/services/user_prefs_service.dart in PokeBindr),
# stored on users/{uid}.preferences under these literal keys.
PREF_WATCH = "store401.watch"
PREF_TOPIC = "store401.topic"
PREF_CONDITIONS = "store401.conditions"
DEFAULT_CONDITIONS = ("NM", "SP", "MP")
# A topic is user-written data headed into a URL path.
TOPIC_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


class Blocked(Exception):
    pass


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


class Client:
    def __init__(self, pace: float) -> None:
        self.pace = pace
        self._last = 0.0

    def product(self, handle: str) -> dict | None:
        """The listing, or None once 401 has taken it down."""
        for attempt in range(3):
            wait = self._last + self.pace - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            req = urllib.request.Request(f"{STORE}/products/{handle}.js", headers=UA)
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.load(resp)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return None
                if e.code != 429:
                    raise
                backoff = 60 * (attempt + 1)
                print(f"429 on {handle} — backing off {backoff}s", file=sys.stderr)
                time.sleep(backoff)
        raise Blocked(handle)


def read_conditions(product: dict) -> dict[str, dict]:
    """`condition -> {price, qty, in_stock}`. A 0.00 price is 401's "unpriced"
    and is stored as None; qty is None when 401 doesn't track the count."""
    out = {}
    for v in product.get("variants", []):
        cond = v.get("option1")
        if cond not in CONDITIONS:
            continue
        cents = v.get("price") or 0
        qty = v.get("inventory_quantity") if v.get("inventory_management") else None
        out[cond] = {
            "price": round(cents / 100, 2) if cents > 0 else None,
            "qty": max(0, int(qty)) if isinstance(qty, (int, float)) else None,
            "in_stock": bool(v.get("available")),
        }
    return out


def changes(before: dict, now: dict) -> list[tuple[str, str, str]]:
    """`(kind, condition, line)` for every condition worth a notification."""
    out = []
    for cond in CONDITIONS:
        n = now.get(cond)
        if not n or not n["in_stock"]:
            continue
        p = before.get(cond)
        price = f"CA${n['price']:.2f}" if n["price"] is not None else "price —"
        count = f"{n['qty']} in stock" if n["qty"] is not None else "in stock"
        if p is None or not p["in_stock"]:
            out.append(("restock", cond, f"{cond} back in stock · {price} · {count}"))
        elif p["price"] and n["price"] and n["price"] < p["price"] * DROP_RATIO:
            out.append(
                ("drop", cond, f"{cond} dropped CA${p['price']:.2f} → {price} · {count}")
            )
        elif (p["qty"] or 0) >= 2 and n["qty"] == 1:
            out.append(("last", cond, f"{cond} down to its last copy · {price}"))
    return out


def firestore_client():
    """Firestore as the read-only service account, or None without its key."""
    key = os.environ.get("FIREBASE_SERVICE_ACCOUNT", "").strip()
    if not key:
        return None
    from google.cloud import firestore
    from google.oauth2 import service_account

    info = json.loads(key)
    creds = service_account.Credentials.from_service_account_info(info)
    return firestore.Client(project=info["project_id"], credentials=creds)


def user_routes(db) -> dict[str, list[tuple[str, frozenset[str]]]]:
    """`cardId -> [(topic, conditions)]` for every opted-in user's wishlist."""
    from google.cloud.firestore_v1.base_query import FieldFilter
    from google.cloud.firestore_v1.field_path import FieldPath

    watching = FieldPath("preferences", PREF_WATCH).to_api_repr()
    routes: dict[str, list[tuple[str, frozenset[str]]]] = {}
    users = 0
    for user in db.collection("users").where(filter=FieldFilter(watching, "==", True)).stream():
        prefs = (user.to_dict() or {}).get("preferences") or {}
        topic = prefs.get(PREF_TOPIC)
        if not isinstance(topic, str) or not TOPIC_RE.match(topic):
            continue
        raw = prefs.get(PREF_CONDITIONS)
        conditions = frozenset(
            c for c in (raw if isinstance(raw, list) else DEFAULT_CONDITIONS) if c in CONDITIONS
        )
        users += 1
        for doc in user.reference.collection("wishlist").stream():
            row = doc.to_dict()
            if row.get("cardId") and not row.get("deletedAt"):
                routes.setdefault(row["cardId"], []).append((topic, conditions))
    print(f"{users} users watching, {len(routes)} cards routed")
    return routes


def notify(topic: str, item: dict, lines: list[tuple[str, str]]) -> None:
    kinds = {k for k, _ in lines}
    title = ("Back in stock at 401: " if "restock" in kinds else "401 Games: ") + item["title"]
    req = urllib.request.Request(
        f"https://ntfy.sh/{topic}",
        data="\n".join(line for _, line in lines).encode(),
        headers={
            # Headers are latin-1; the title can carry é / ♀ — RFC 2047 encode it.
            "Title": "=?UTF-8?B?" + base64.b64encode(title.encode()).decode() + "?=",
            "Click": item["url"],
            "Tags": "shopping_cart" if "restock" in kinds else "chart_with_downwards_trend",
            "Priority": "high" if "restock" in kinds else "default",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20):
        pass


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--site", type=Path, required=True, help="gh-pages price-history/401")
    ap.add_argument("--state", type=Path, required=True)
    ap.add_argument("--pace", type=float, default=4.0, help="seconds between requests")
    ap.add_argument("--max-items", type=int, default=150)
    ap.add_argument("--budget-minutes", type=float, default=18)
    ap.add_argument("--probe", help="fetch one handle, print it, touch nothing")
    args = ap.parse_args()

    client = Client(args.pace)
    if args.probe:
        product = client.product(args.probe)
        print(json.dumps(read_conditions(product) if product else None, indent=1))
        return 0 if product else 1

    watch = load_json(args.site / "watchlist.json", {"items": []})["items"]
    stock_path = args.site / "stock.json"
    stock = load_json(stock_path, {"items": {}})
    state = load_json(args.state, None)
    if state is None:
        # Cache evicted: start from what was last published. Listings missing
        # from it get a baseline reading this run, never an alert.
        state = {h: {k: e.get(k) for k in ("checked", "conditions", "gone")}
                 for h, e in stock.get("items", {}).items()}
        print(f"no cached state — seeded {len(state)} listings from stock.json")

    by_handle = {i["handle"]: i for i in watch}
    order = sorted(by_handle, key=lambda h: (state.get(h) or {}).get("checked") or "")
    store_topic = os.environ.get("NTFY_TOPIC", "").strip()
    # A routing failure fails the run before any reading is recorded, so the
    # next run sees the same change again rather than a silent miss.
    db = firestore_client()
    routes = user_routes(db) if db is not None else {}
    if db is None:
        print("::warning::FIREBASE_SERVICE_ACCOUNT unset — only NTFY_TOPIC is alerted")

    deadline = time.monotonic() + args.budget_minutes * 60
    sent: dict[str, int] = {}
    alerts = checked = 0
    try:
        for handle in order[: args.max_items]:
            if time.monotonic() > deadline:
                break
            item = by_handle[handle]
            prev = state.get(handle) or {}
            product = client.product(handle)
            checked += 1
            if product is None:
                state[handle] = {**prev, "checked": iso(utcnow()), "gone": True}
                continue
            now = read_conditions(product)
            if prev.get("checked") and prev.get("conditions") is not None:
                news = changes(prev["conditions"], now)
                if news:
                    alerts += 1
                    print(f"{handle}: " + "; ".join(line for _, _, line in news))
                    targets = list(routes.get(item.get("card"), []))
                    if store_topic and item.get("conditions"):
                        targets.append((store_topic, frozenset(item["conditions"])))
                    by_topic: dict[str, list[tuple[str, str]]] = {}
                    for topic, wanted in targets:
                        for kind, cond, line in news:
                            if cond in wanted and (kind, line) not in by_topic.get(topic, []):
                                by_topic.setdefault(topic, []).append((kind, line))
                    for topic, lines in by_topic.items():
                        if sent.get(topic, 0) >= MAX_ALERTS:
                            continue
                        try:
                            notify(topic, item, lines)
                            sent[topic] = sent.get(topic, 0) + 1
                        except Exception as e:  # noqa: BLE001 - never lose the reading
                            print(f"ntfy failed for {handle}: {e}", file=sys.stderr)
            state[handle] = {"checked": iso(utcnow()), "conditions": now, "gone": False}
    except Blocked:
        print("::warning::401 kept answering 429 — stopping this run early")
    print(
        f"checked {checked} of {len(watch)} listings, {alerts} with news, "
        f"{sum(sent.values())} notifications to {len(sent)} topics"
    )

    args.state.parent.mkdir(parents=True, exist_ok=True)
    args.state.write_text(json.dumps(state, separators=(",", ":")))

    items = {}
    for handle, item in sorted(by_handle.items()):
        s = state.get(handle)
        if not s or not s.get("checked"):
            continue
        items[handle] = {
            "card": item.get("card"),
            "finish": item.get("finish"),
            "title": item["title"],
            "url": item["url"],
            "checked": s["checked"],
            "gone": bool(s.get("gone")),
            "conditions": s.get("conditions") or {},
        }

    def content(entries: dict) -> dict:
        return {h: {k: v for k, v in e.items() if k != "checked"} for h, e in entries.items()}

    last = stock.get("checked_at")
    due = last is None or utcnow() - datetime.fromisoformat(last) >= HEARTBEAT
    if content(items) != content(stock.get("items", {})) or due:
        stock_path.parent.mkdir(parents=True, exist_ok=True)
        stock_path.write_text(
            json.dumps({"v": 1, "checked_at": iso(utcnow()), "items": items}, indent=1)
        )
        print(f"wrote {stock_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
