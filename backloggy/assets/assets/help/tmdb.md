# TMDB API key

**The Movie Database (TMDB)** powers rich movie and TV metadata, posters, and the **Explore** feeds for TV and movies.

## What you need

- A free TMDB account
- An **API Key (v3 auth)** — not the "API Read Access Token"

## Used for

- **TV** and **Movie** categories when TMDB is selected as the source
- **Explore** discovery for TV and movies (recommended even if you use TVMaze or Wikidata for search)

## Step-by-step

1. Open [themoviedb.org](https://www.themoviedb.org/signup) and create an account (desktop browser recommended).
2. Log in, click your avatar → **Settings**.
3. Open the **API** section in the sidebar.
4. Under **Request an API Key**, click the link and choose **Developer**.
5. Accept the terms and fill in the application form:
   - **Application name:** `Backloggy` (or any name you like)
   - **Application URL:** you can use `https://localhost` for personal use
   - **Application summary:** e.g. "Personal media backlog tracker"
6. Submit the form. Your **API Key (v3 auth)** appears on the API settings page.
7. Copy the key and paste it into **Settings → API keys → TMDB API key** in Backloggy.
8. Tap **Save settings**.

## Tips

- TMDB rate-limits requests. Personal backlog use is well within free limits.
- If search fails, confirm you copied the **API Key**, not the longer read-access token.
- For Explore, switch your TV/Movie source to TMDB in Settings for the best results.

## Official docs

- [TMDB API — Getting started](https://developer.themoviedb.org/docs/getting-started)
- [API terms of use](https://www.themoviedb.org/api-terms-of-use)
