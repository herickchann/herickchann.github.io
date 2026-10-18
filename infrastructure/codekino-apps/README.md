# Codekino app domains

The app deployments remain on GitHub Pages. This Cloudflare Worker serves their published files through the following custom domains:

| App | Custom domain | Static origin folder |
| --- | --- | --- |
| App index | https://apps.codekino.org/ | https://herickchann.github.io/ (site root) |
| Backloggy | https://backloggy.codekino.org/ | https://herickchann.github.io/backloggy/ |
| PokeBindr | https://bindr.codekino.org/ | https://herickchann.github.io/bindr/ |
| Panju | https://panju.codekino.org/ | https://herickchann.github.io/panju/ |

CADar is a separate GitHub Pages project with its native custom-domain setting pointing to https://cadar.codekino.org/. Its DNS-only CNAME targets `herickchann.github.io`.

The Worker rewrites only the HTML base element so each Flutter app loads at its new origin root. Previously compiled absolute asset paths remain supported. GET and HEAD are the only allowed methods; cookies and authorization headers are never forwarded to the static origin. No API endpoints are proxied and no storage is bound.

New deployments to the existing app folders appear at the custom domains automatically. The original GitHub URLs for the three routed apps remain available. Browser data belongs to its original origin: local collections and preferences do not automatically migrate; use the apps' sync or export/import features when appropriate.

Authentication authorized domains must include each app's hostname in its own Firebase project. Backloggy's metadata service must also allow `https://backloggy.codekino.org` in its origin list. Keep the original GitHub origin allowed so existing installs continue working.

## Updating this router

The initial deployment was made through the signed-in Cloudflare dashboard. These files record that deployed source and configuration. Edit the `codekino-apps` Worker in the dashboard, or from this directory run `npx wrangler deploy` with an authorized Cloudflare login. Commit corresponding changes here so the stored configuration stays current. A Git push alone does not redeploy this Worker.

The apps host passes the site root through unchanged, with no base-element rewrite and no single-page fallback, so unknown paths return a real 404. The GitHub Pages custom-domain setting on `herickchann.github.io` is deliberately left unset: setting it would redirect every `herickchann.github.io` path, including this Worker's upstream requests.

`pokebindr.codekino.org` is retired: it stays attached to the Worker only to redirect (301) to `bindr.codekino.org`, keeping the path and query.

Only the Worker custom domains listed above, plus that redirect, belong to this service. The root domain and all other codekino.org records remain unchanged.
