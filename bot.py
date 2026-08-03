import os
import logging
import tempfile
import re

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import yt_dlp

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]

URL_REGEX = re.compile(
    r"(https?://)?(www\.)?(tiktok\.com|vt\.tiktok\.com|youtube\.com|youtu\.be)/\S+",
    re.IGNORECASE,
)

# Telegram's max upload size for bots is 50MB via the Bot API.
MAX_FILE_SIZE = 50 * 1024 * 1024


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to SnapVaultsBot!\n\n"
        "Just paste a TikTok or YouTube link and I'll download the video for you "
        "(no watermark, when possible).\n\n"
        "Example:\nhttps://www.tiktok.com/@user/video/123456789"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me a TikTok or YouTube video link and I'll send the video file back.\n"
        "Note: videos over 50MB can't be sent by the bot (Telegram Bot API limit)."
    )


def download_video(url: str, out_dir: str) -> str:
    """Download the video with yt-dlp and return the local file path."""
    output_template = os.path.join(out_dir, "%(id)s.%(ext)s")
    ydl_opts = {
        "outtmpl": output_template,
        "format": "mp4/bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "max_filesize": MAX_FILE_SIZE,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filepath = ydl.prepare_filename(info)
        # merge_output_format may change extension to mp4
        base, _ = os.path.splitext(filepath)
        mp4_path = base + ".mp4"
        if os.path.exists(mp4_path):
            return mp4_path
        return filepath


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    match = URL_REGEX.search(text)

    if not match:
        await update.message.reply_text(
            "Please send a valid TikTok or YouTube link."
        )
        return

    url = match.group(0)
    status_msg = await update.message.reply_text("⏳ Downloading your video...")
    await update.effective_chat.send_action(ChatAction.UPLOAD_VIDEO)

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            filepath = download_video(url, tmp_dir)

            if not os.path.exists(filepath):
                await status_msg.edit_text(
                    "❌ Couldn't download that video. It may be private, "
                    "region-locked, or too large."
                )
                return

            file_size = os.path.getsize(filepath)
            if file_size > MAX_FILE_SIZE:
                await status_msg.edit_text(
                    "❌ This video is larger than 50MB, which is the maximum "
                    "Telegram allows bots to send."
                )
                return

            await status_msg.edit_text("📤 Uploading to Telegram...")
            with open(filepath, "rb") as video_file:
                await update.effective_chat.send_video(
                    video=video_file,
                    caption="✅ Here's your video — downloaded via SnapVaultsBot",
                    supports_streaming=True,
                )
            await status_msg.delete()

    except yt_dlp.utils.DownloadError as e:
        logger.error("Download error: %s", e)
        await status_msg.edit_text(
            "❌ Couldn't download that video. Double check the link is public "
            "and correct, then try again."
        )
    except Exception as e:
        logger.exception("Unexpected error")
        await status_msg.edit_text(
            "❌ Something went wrong while processing your video. Please try again."
        )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("SnapVaultsBot is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
