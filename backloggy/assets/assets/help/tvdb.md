# TheTVDB API key

**TheTVDB** provides rich TV series metadata, posters, season counts, and episode totals.

## What you need

- A free [TheTVDB](https://www.thetvdb.com/) account
- An **API key** from your account dashboard

## Used for

- **TV** category search and detail auto-fill when TheTVDB is enabled as a source

## Step-by-step

1. Create an account at [thetvdb.com](https://www.thetvdb.com/signup).
2. Open [API Keys](https://www.thetvdb.com/dashboard/account/apikey) in your account dashboard.
3. Create a new project/API key (v4).
4. Copy the key and paste it into **Settings → Metadata sources → TV → TheTVDB**.
5. Tap **Test TheTVDB**, then **Save settings**.

## Tips

- TheTVDB uses a login token under the hood; Backloggy caches it and refreshes as needed.
- Prefer ranking TheTVDB above or below TVMaze/TMDB based on which catalog you trust more for a title.
- Explore discovery feeds still prefer TMDB when that key is configured.

## Official docs

- [TheTVDB v4 API](https://thetvdb.github.io/v4-api/)
- [API terms](https://thetvdb.com/api-information)
