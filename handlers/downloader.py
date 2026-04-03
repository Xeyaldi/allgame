import os
import asyncio
import requests
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import COOKIE_URL


def get_cookies():
    """Cookie faylını URL-dən yükləyir"""
    if not COOKIE_URL:
        return None
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        r = requests.get(COOKIE_URL, headers=headers, timeout=15)
        if r.status_code == 200:
            content = r.text.strip()
            header = "# Netscape HTTP Cookie File"
            if not content.startswith(header):
                content = header + "\n" + content
            with open("cookies.txt", "w", encoding="utf-8") as f:
                f.write(content)
            return "cookies.txt"
    except:
        pass
    return None


def download_media(url, mode="video"):
    """Media yükləyir, (fayl_yolu, başlıq, video_mu) qaytarır"""
    cookie_file = get_cookies()
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
        },
    }

    if cookie_file:
        ydl_opts['cookiefile'] = cookie_file

    if mode == "music":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    os.makedirs("downloads", exist_ok=True)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if not info:
            raise Exception("Media tapılmadı.")
        filename = ydl.prepare_filename(info)
        if mode == "music":
            base = os.path.splitext(filename)[0]
            if os.path.exists(base + ".mp3"):
                filename = base + ".mp3"
        is_video = not (
            info.get('ext') in ['jpg', 'png', 'webp', 'jpeg'] or
            info.get('vcodec') == 'none' or
            mode == "music"
        )
        return filename, info.get('title', 'Media'), is_video


# --- YOUTUBE AXTAR ---
@Client.on_message(filters.command("youtube"))
async def youtube_search(client, message):
    if len(message.command) < 2:
        return await message.reply_text("🔎 Axtarılacaq sözü yazın:\n`/youtube Röya mahnı adı`")
    query = " ".join(message.command[1:])
    status = await message.reply_text("🔎 **YouTube-da axtarılır...**")
    cookie_file = get_cookies()
    ydl_opts = {'quiet': True, 'no_warnings': True}
    if cookie_file:
        ydl_opts['cookiefile'] = cookie_file
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(f"ytsearch5:{query}", download=False)['entries']
        if not results:
            return await status.edit_text("❌ Heç bir nəticə tapılmadı!")
        buttons = []
        for video in results:
            title = video.get('title', '')
            title = (title[:35] + "..") if len(title) > 35 else title
            v_url = video.get('webpage_url', '')
            buttons.append([InlineKeyboardButton(f"🎬 {title}", callback_data=f"yt_choice|{v_url}")])
        await status.edit_text(
            f"🔎 **'{query}' üçün nəticələr:**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        await status.edit_text(f"❌ Axtarış xətası: {str(e)}")


# --- SOSIAL ŞƏBƏKƏ LİNK TUTUCU ---
@Client.on_message(
    filters.regex(r"(https?://(?:www\.)?(?:youtube\.com|youtu\.be|instagram\.com|tiktok\.com|twitter\.com|x\.com|facebook\.com|soundcloud\.com|vimeo\.com|reddit\.com)\S+)") &
    filters.private
)
async def link_detector(client, message):
    url = message.matches[0].group(1)
    if "youtube.com" in url or "youtu.be" in url:
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 Video (MP4)", callback_data=f"vid|{url}"),
             InlineKeyboardButton("🎵 Musiqi (MP3)", callback_data=f"mus|{url}")]
        ])
        await message.reply_text("🎞 **YouTube aşkarlandı! Seçim edin:**", reply_markup=buttons)
    else:
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 Video (MP4)", callback_data=f"vid|{url}"),
             InlineKeyboardButton("🎵 Musiqi (MP3)", callback_data=f"mus|{url}")]
        ])
        await message.reply_text("🔗 **Link aşkarlandı! Formatı seçin:**", reply_markup=buttons)


# --- CALLBACK İDARƏÇİSİ ---
@Client.on_callback_query(filters.regex(r"^(yt_choice|vid|mus)\|"))
async def download_callback(client, callback_query: CallbackQuery):
    data = callback_query.data

    if data.startswith("yt_choice|"):
        url = data.split("|", 1)[1]
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 Video", callback_data=f"vid|{url}"),
             InlineKeyboardButton("🎵 Musiqi (MP3)", callback_data=f"mus|{url}")]
        ])
        return await callback_query.message.edit_text(
            "⏬ **Formatı seçin:**", reply_markup=buttons
        )

    mode_raw, url = data.split("|", 1)
    mode = "video" if mode_raw == "vid" else "music"

    await callback_query.message.edit_text("⏳ **Yüklənir, gözləyin...**")

    try:
        path, title, is_video = await asyncio.to_thread(download_media, url, mode)

        if mode == "video" and is_video:
            await callback_query.message.reply_video(
                path,
                caption=f"🎬 `{title}`\n📢 {(await client.get_me()).mention}"
            )
        elif mode == "music":
            final_path = path.rsplit('.', 1)[0] + ".mp3"
            if not os.path.exists(final_path):
                final_path = path
            await callback_query.message.reply_audio(
                final_path,
                caption=f"🎵 `{title}`\n📢 {(await client.get_me()).mention}"
            )
            if os.path.exists(final_path) and final_path != path:
                os.remove(final_path)
        else:
            await callback_query.message.reply_photo(
                path, caption=f"🖼 `{title}`"
            )

        if os.path.exists(path):
            os.remove(path)
        await callback_query.message.delete()

    except Exception as e:
        await callback_query.message.edit_text(f"❌ **Xəta:** {str(e)}")
