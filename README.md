# SnapVaultsBot

A Telegram bot that downloads TikTok and YouTube videos from a pasted link — SnapSave-style.

## How it works
- Uses `python-telegram-bot` to talk to Telegram.
- Uses `yt-dlp` to actually fetch/download the video (handles both TikTok and YouTube).
- `ffmpeg` (installed via the Dockerfile) merges video/audio streams when needed.
- Only one environment variable is required: `BOT_TOKEN`.

## 1. Create the bot on Telegram
1. Open Telegram, message **@BotFather**.
2. Send `/newbot`, follow the prompts, choose a name and username (e.g. `SnapVaultsBot`).
3. BotFather gives you a token like `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` — save it, you'll need it in step 3.

## 2. Push this code to GitHub
```bash
git init
git add .
git commit -m "Initial commit - SnapVaultsBot"
git branch -M main
git remote add origin https://github.com/<your-username>/snapvaultsbot.git
git push -u origin main
```

## 3. Deploy on Railway
1. Go to [railway.app](https://railway.app) and sign in with GitHub.
2. Click **New Project → Deploy from GitHub repo** and select your `snapvaultsbot` repo.
3. Railway will detect the `Dockerfile` and build automatically.
4. Go to your service's **Variables** tab and add:
   - `BOT_TOKEN` = the token from BotFather
5. Deploy. Check the **Deployments → Logs** tab — you should see `SnapVaultsBot is starting...`.

That's it — no database, no other services, just the one variable.

## 4. Test it
Open a chat with your bot on Telegram and paste a TikTok or YouTube link. It should reply with the downloaded video.

## Notes & limits
- Telegram bots can only send files up to **50MB** — larger videos will be rejected with a message explaining why.
- Some TikTok/YouTube videos may be private, age-restricted, or region-locked, which will cause a download failure.
- Downloading content you don't have rights to may violate TikTok's and YouTube's Terms of Service — this bot is provided for personal/fair use; you're responsible for how it's used.
- `yt-dlp` occasionally needs updates when platforms change their internals. If downloads start failing, try bumping the `yt-dlp` version in `requirements.txt` and redeploying.
