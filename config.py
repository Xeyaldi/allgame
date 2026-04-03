import re
import os
from pyrogram import filters
from dotenv import load_dotenv

load_dotenv()

# ── ƏSAS ──────────────────────────────────────────────
API_ID        = int(os.getenv("API_ID", 0))
API_HASH      = os.getenv("API_HASH", "")
BOT_TOKEN     = os.getenv("BOT_TOKEN", "")

# ── SAHİB ─────────────────────────────────────────────
OWNER_ID      = int(os.getenv("OWNER_ID", 0))
OWNER_IDS_STR = os.getenv("OWNER_IDS", str(OWNER_ID))
OWNERS        = [int(x.strip()) for x in OWNER_IDS_STR.split(",") if x.strip()]

# ── LİNKLƏR ───────────────────────────────────────────
OWNER_LINK    = os.getenv("OWNER_LINK",   "https://t.me/username")
CHANNEL_LINK  = os.getenv("CHANNEL_LINK", "https://t.me/HT_bots")
SUPPORT_CHAT  = os.getenv("SUPPORT_CHAT", "https://t.me/ht_bots_chat")
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "https://t.me/HT_bots")

# ── MUSİQİ BOTU ───────────────────────────────────────
# STRING_SESSION: @StringFatherBot-dan al (User account üçün)
STRING1       = os.getenv("STRING_SESSION",  None)
STRING2       = os.getenv("STRING_SESSION2", None)
STRING3       = os.getenv("STRING_SESSION3", None)

MONGO_DB_URI  = os.getenv("MONGO_DB_URI", None)
LOGGER_ID     = int(os.getenv("LOGGER_ID", 0))

DURATION_LIMIT_MIN  = int(os.getenv("DURATION_LIMIT", 600))
PLAYLIST_FETCH_LIMIT = int(os.getenv("PLAYLIST_FETCH_LIMIT", 25))

TG_AUDIO_FILESIZE_LIMIT = int(os.getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(os.getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))

SPOTIFY_CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID", None)
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", None)

# ── DOWNLOADER ────────────────────────────────────────
COOKIE_URL    = os.getenv("COOKIE_URL", "")

# ── AI ────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ── GÖRÜNTÜ ───────────────────────────────────────────
START_PIC      = os.getenv("START_PIC", "https://i.postimg.cc/mDTTvtxS/20260214-163714.jpg")
START_STICKER  = os.getenv("START_STICKER", "CAACAgQAAxkBAAEQhcppkc-7kbd_oDn4S9MV6T5vv-TL9AACQhgAAiRYeVGtiXa89ZuMAzoE")

YOUTUBE_IMG_URL  = os.getenv("YOUTUBE_IMG_URL",  "https://i.postimg.cc/mDTTvtxS/20260214-163714.jpg")
STREAM_IMG_URL   = os.getenv("STREAM_IMG_URL",   "https://files.catbox.moe/kvfeip.jpg")
TELEGRAM_IMG_URL = os.getenv("TELEGRAM_IMG_URL", "https://i.postimg.cc/mDTTvtxS/20260214-163714.jpg")

# ── HESABLAMALAR ──────────────────────────────────────
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

# ── FİLTRLƏR ─────────────────────────────────────────
BANNED_USERS = filters.user()
adminlist    = {}
