# Metadata source setup

Backloggy ships with **free, keyless** sources for every category. You only need API keys if you switch a category to an optional provider.

## No API key required (defaults)

| Category | Default source |
|----------|----------------|
| Anime / Manga | AniList (manga also falls back to MyAnimeList via Jikan) |
| TV | TVMaze |
| Movie | Wikidata |
| Game | Steam Store |
| Book | Open Library |

## Optional sources that need keys

| Source | Best for | Guide |
|--------|----------|-------|
| TMDB | TV & movies, Explore feeds | See TMDB guide |
| TheTVDB | TV series search & details | See TheTVDB guide |
| RAWG | Games, Explore game dates | See RAWG guide |
| OMDb | Movie search (IMDb-style) | See OMDb guide |
| SteamGridDB | Game search + artwork | See SteamGridDB guide |
| IGDB | Game database (via Twitch) | See IGDB guide |

## How to configure

1. Open **Settings**.
2. Under **Metadata sources**, pick a provider for each category.
3. If a key is required, fill in the **API keys** section that appears.
4. Tap **Save settings**.

Keys are stored securely on your device (Keychain / Encrypted storage). They are never uploaded except when calling the provider's API.

## Explore without extra keys

**Anime** and **manga** Explore work with no keys (AniList). For **TV**, **movies**, and **games**, adding **TMDB** and/or **RAWG** keys unlocks much better discovery feeds.
