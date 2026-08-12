# IGDB (Twitch) credentials

**IGDB** is a game database owned by Twitch. Backloggy uses **Twitch Developer** Client ID and Client Secret to access IGDB — the same setup as Playnite and other apps.

## What you need

- A Twitch account
- A Twitch **Client ID** and **Client Secret** from the Developer Console

## Used for

- **Game** category when IGDB is selected as the source

## Step-by-step

1. Log in to the [Twitch Developer Console](https://dev.twitch.tv/console) with your Twitch account.
2. Open the **Applications** tab (or **Register Your Application**).
3. Click **Register Your Application** and fill in:
   - **Name:** `Backloggy` (or any name)
   - **OAuth Redirect URLs:** add `http://localhost` (required by Twitch even for non-OAuth API use)
   - **Category:** choose **Application Integration** or **Other**
4. Create the application.
5. Open the application details page and copy the **Client ID**.
6. Click **New Secret** to generate a **Client Secret** and copy it immediately (Twitch may only show it once).
7. In Backloggy **Settings**, set **Game** source to **IGDB**.
8. Paste **Client ID** and **Client Secret** into the IGDB fields.
9. Tap **Save settings**.

## Tips

- IGDB does not use a separate IGDB.com API key — only Twitch credentials.
- If requests fail, regenerate the Client Secret and update Settings.
- **RAWG** or **Steam Store** are simpler alternatives if you do not need IGDB specifically.

## Official docs

- [Twitch Developer Console](https://dev.twitch.tv/console)
- [IGDB API (Twitch)](https://api-docs.igdb.com/#getting-started)
