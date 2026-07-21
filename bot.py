import os
import tempfile
import yt_dlp

from telegram import Update
from telegram.request import HTTPXRequest
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")	
def is_instagram_url(text):
    return (
        "instagram.com/reel/" in text
        or "instagram.com/p/" in text
        or "instagram.com/share/" in text
    )

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    url = update.message.text.strip()

    if not is_instagram_url(url):
        return

    msg = await update.message.reply_text("⬇️ Downloading...")	

    with tempfile.TemporaryDirectory() as temp:

        ydl_opts = {
                    "outtmpl": os.path.join(temp, "%(id)s.%(ext)s"),
                    "format": "bv*+ba/b",
                    "merge_output_format": "mp4",
                    "verbose": True,
                    "ffmpeg_location": "/usr/bin/ffmpeg",
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

            filename = ydl.prepare_filename(info)

            await update.message.reply_video(
                video=open(filename, "rb")
            )

            await msg.edit_text("✅ Done!")

        except Exception as e:
            await msg.edit_text(f"❌ Error:\n{e}")

request = HTTPXRequest(
    connect_timeout=30,
    read_timeout=120,
    write_timeout=120,
    pool_timeout=30,
)

app = (
    Application.builder()
    .token(BOT_TOKEN)
    .request(request)
    .build()
)

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, download)
)

print("🤖 Bot started...")

app.run_polling()

