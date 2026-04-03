import asyncio
import os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus
from config import OWNERS, DURATION_LIMIT_MIN, YOUTUBE_IMG_URL, STREAM_IMG_URL

# ── Queue sistemi ─────────────────────────────────────
music_queues = {}   # {chat_id: [{"title":..,"url":..,"user":..}, ...]}
vc_clients   = {}   # {chat_id: pytgcalls instance}
now_playing  = {}   # {chat_id: {"title":..,"url":..,"user":..}}


# ── Admin yoxlama ─────────────────────────────────────
async def is_vc_admin(client, message):
    uid = message.from_user.id
    if uid in OWNERS:
        return True
    try:
        member = await client.get_chat_member(message.chat.id, uid)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except:
        return False


# ── URL-dən audio yolu al ─────────────────────────────
def get_audio_stream(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    os.makedirs("downloads", exist_ok=True)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        base = os.path.splitext(filename)[0]
        mp3_path = base + ".mp3"
        if os.path.exists(mp3_path):
            return mp3_path, info.get('title', 'Bilinməyən'), int(info.get('duration', 0))
        return filename, info.get('title', 'Bilinməyən'), int(info.get('duration', 0))


def get_video_stream(url):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    os.makedirs("downloads", exist_ok=True)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename, info.get('title', 'Bilinməyən'), int(info.get('duration', 0))


def search_youtube(query):
    ydl_opts = {'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        results = ydl.extract_info(f"ytsearch1:{query}", download=False)
        if results and results.get('entries'):
            entry = results['entries'][0]
            return entry.get('webpage_url'), entry.get('title'), int(entry.get('duration', 0))
    return None, None, 0


def format_duration(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02}" if h else f"{m:02}:{s:02}"


# ── Növbəti mahnını oxut ──────────────────────────────
async def play_next(client, chat_id):
    queue = music_queues.get(chat_id, [])
    if not queue:
        now_playing.pop(chat_id, None)
        if chat_id in vc_clients:
            try:
                call = vc_clients[chat_id]
                await call.leave_call(chat_id)
            except:
                pass
            vc_clients.pop(chat_id, None)
        return

    track = queue.pop(0)
    music_queues[chat_id] = queue
    now_playing[chat_id] = track

    try:
        from pytgcalls import PyTgCalls
        from pytgcalls.types import MediaStream, AudioQuality, VideoQuality

        call = vc_clients.get(chat_id)
        if not call:
            return

        if track.get("is_video"):
            stream = MediaStream(
                track["file"],
                video_flags=MediaStream.Flags.NO_RESIZE,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.SD_480p,
            )
        else:
            stream = MediaStream(
                track["file"],
                audio_parameters=AudioQuality.HIGH,
                video_flags=MediaStream.Flags.IGNORE,
            )

        await call.play(chat_id, stream)

        dur = format_duration(track.get("duration", 0))
        caption = (
            f"🎵 **İndi Oxunur:**\n\n"
            f"🎼 **{track['title']}**\n"
            f"⏱ Müddət: `{dur}`\n"
            f"👤 İstəyən: {track['user']}\n\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("⏸ Fasilə", callback_data=f"vc_pause"),
             InlineKeyboardButton("⏭ Növbəti", callback_data=f"vc_skip")],
            [InlineKeyboardButton("🔊 Səs +", callback_data="vc_vol_up"),
             InlineKeyboardButton("🔉 Səs -",  callback_data="vc_vol_down")],
            [InlineKeyboardButton("⏹ Dayandır", callback_data="vc_stop")],
        ])
        await client.send_photo(
            chat_id,
            photo=YOUTUBE_IMG_URL,
            caption=caption,
            reply_markup=buttons
        )
    except Exception as e:
        await client.send_message(chat_id, f"❌ Xəta: {str(e)}")
        now_playing.pop(chat_id, None)


# ── /play komandası ───────────────────────────────────
@Client.on_message(filters.command(["play", "oynat"]) & filters.group)
async def play_cmd(client, message):
    if not await is_vc_admin(client, message):
        return await message.reply_text("❌ Bu komanda yalnız adminlər üçündür!")

    query = " ".join(message.command[1:])
    if not query:
        return await message.reply_text(
            "🎵 Musiqi adı və ya link yazın:\n`/play Röya`"
        )

    status = await message.reply_text("🔍 **Axtarılır...**")

    try:
        # URL yoxsa YouTube-da axtar
        if query.startswith("http"):
            url = query
            title = "Bilinməyən"
            duration = 0
        else:
            url, title, duration = await asyncio.to_thread(search_youtube, query)
            if not url:
                return await status.edit_text("❌ Nəticə tapılmadı!")

        await status.edit_text("⬇️ **Yüklənir...**")
        file_path, title, duration = await asyncio.to_thread(get_audio_stream, url)

        track = {
            "title": title,
            "url": url,
            "file": file_path,
            "duration": duration,
            "user": message.from_user.mention,
            "is_video": False,
        }

        chat_id = message.chat.id

        # pytgcalls client
        from pytgcalls import PyTgCalls
        from pytgcalls.types import MediaStream, AudioQuality

        if chat_id not in vc_clients:
            # userbot client-i tap
            userbot = getattr(client, "_userbot", None)
            if not userbot:
                return await status.edit_text(
                    "❌ **STRING_SESSION təyin edilməyib!**\n\n"
                    "Heroku Config Vars-a `STRING_SESSION` əlavə edin.\n"
                    "@StringFatherBot-dan alın."
                )
            call = PyTgCalls(userbot)
            await call.start()
            vc_clients[chat_id] = call

        if chat_id not in music_queues:
            music_queues[chat_id] = []

        if now_playing.get(chat_id):
            # Növbəyə əlavə et
            music_queues[chat_id].append(track)
            dur = format_duration(duration)
            pos = len(music_queues[chat_id])
            await status.edit_text(
                f"✅ **Növbəyə əlavə edildi!**\n\n"
                f"🎼 **{title}**\n"
                f"⏱ `{dur}` • Növbə: #{pos}"
            )
        else:
            # Birbaşa oxut
            music_queues[chat_id] = [track]
            await status.edit_text("🎵 **Qoşulunur...**")

            call = vc_clients[chat_id]
            stream = MediaStream(
                file_path,
                audio_parameters=AudioQuality.HIGH,
            )
            await call.join_group_call(chat_id, stream)
            now_playing[chat_id] = track
            music_queues[chat_id] = []

            dur = format_duration(duration)
            caption = (
                f"🎵 **İndi Oxunur:**\n\n"
                f"🎼 **{title}**\n"
                f"⏱ Müddət: `{dur}`\n"
                f"👤 İstəyən: {message.from_user.mention}\n\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("⏸ Fasilə",  callback_data="vc_pause"),
                 InlineKeyboardButton("⏭ Növbəti", callback_data="vc_skip")],
                [InlineKeyboardButton("🔊 Səs +",  callback_data="vc_vol_up"),
                 InlineKeyboardButton("🔉 Səs -",   callback_data="vc_vol_down")],
                [InlineKeyboardButton("⏹ Dayandır", callback_data="vc_stop")],
            ])
            await status.delete()
            await client.send_photo(
                chat_id,
                photo=YOUTUBE_IMG_URL,
                caption=caption,
                reply_markup=buttons
            )

    except Exception as e:
        await status.edit_text(f"❌ **Xəta:** `{str(e)}`")


# ── /vplay - video stream ─────────────────────────────
@Client.on_message(filters.command(["vplay", "voynat"]) & filters.group)
async def vplay_cmd(client, message):
    if not await is_vc_admin(client, message):
        return await message.reply_text("❌ Admin lazımdır!")

    query = " ".join(message.command[1:])
    if not query:
        return await message.reply_text("🎥 Video link ya ad yazın: `/vplay link`")

    status = await message.reply_text("🔍 **Axtarılır...**")
    try:
        if query.startswith("http"):
            url = query
        else:
            url, _, _ = await asyncio.to_thread(search_youtube, query)
            if not url:
                return await status.edit_text("❌ Tapılmadı!")

        await status.edit_text("⬇️ **Video yüklənir...**")
        file_path, title, duration = await asyncio.to_thread(get_video_stream, url)

        track = {
            "title": title, "url": url, "file": file_path,
            "duration": duration, "user": message.from_user.mention,
            "is_video": True,
        }

        chat_id = message.chat.id
        if chat_id not in music_queues:
            music_queues[chat_id] = []

        music_queues[chat_id].append(track)

        if not now_playing.get(chat_id):
            await play_next(client, chat_id)
            await status.delete()
        else:
            await status.edit_text(f"✅ **Video növbəyə əlavə edildi:**\n🎬 **{title}**")

    except Exception as e:
        await status.edit_text(f"❌ **Xəta:** `{str(e)}`")


# ── /pause ────────────────────────────────────────────
@Client.on_message(filters.command(["pause", "duraklat"]) & filters.group)
async def pause_cmd(client, message):
    if not await is_vc_admin(client, message): return
    chat_id = message.chat.id
    call = vc_clients.get(chat_id)
    if not call:
        return await message.reply_text("❌ Aktiv musiqi yoxdur!")
    try:
        await call.pause_stream(chat_id)
        await message.reply_text("⏸ **Fasilə verildi.**")
    except Exception as e:
        await message.reply_text(f"❌ {e}")


# ── /resume ───────────────────────────────────────────
@Client.on_message(filters.command(["resume", "devam"]) & filters.group)
async def resume_cmd(client, message):
    if not await is_vc_admin(client, message): return
    chat_id = message.chat.id
    call = vc_clients.get(chat_id)
    if not call:
        return await message.reply_text("❌ Aktiv musiqi yoxdur!")
    try:
        await call.resume_stream(chat_id)
        await message.reply_text("▶️ **Davam etdirildi.**")
    except Exception as e:
        await message.reply_text(f"❌ {e}")


# ── /skip ─────────────────────────────────────────────
@Client.on_message(filters.command(["skip", "atla"]) & filters.group)
async def skip_cmd(client, message):
    if not await is_vc_admin(client, message): return
    chat_id = message.chat.id
    call = vc_clients.get(chat_id)
    if not call:
        return await message.reply_text("❌ Aktiv musiqi yoxdur!")
    try:
        await call.change_stream(chat_id, None)
    except:
        pass
    await message.reply_text("⏭ **Növbəti mahnıya keçildi.**")
    await play_next(client, chat_id)


# ── /stop ─────────────────────────────────────────────
@Client.on_message(filters.command(["stop", "durdur"]) & filters.group)
async def stop_cmd(client, message):
    if not await is_vc_admin(client, message): return
    chat_id = message.chat.id
    music_queues.pop(chat_id, None)
    now_playing.pop(chat_id, None)
    call = vc_clients.pop(chat_id, None)
    if call:
        try:
            await call.leave_call(chat_id)
        except:
            pass
    await message.reply_text("⏹ **Musiqi dayandırıldı və bot səsli söhbətdən çıxdı.**")


# ── /queue ────────────────────────────────────────────
@Client.on_message(filters.command(["queue", "sira"]) & filters.group)
async def queue_cmd(client, message):
    chat_id = message.chat.id
    current = now_playing.get(chat_id)
    queue = music_queues.get(chat_id, [])

    if not current:
        return await message.reply_text("🎵 Hal-hazırda heç nə oxunmur.")

    text = f"🎵 **İndi:** {current['title']}\n\n"
    if queue:
        text += "📋 **Növbə:**\n"
        for i, t in enumerate(queue[:10], 1):
            text += f"{i}. {t['title']}\n"
        if len(queue) > 10:
            text += f"...və {len(queue)-10} daha"
    else:
        text += "📋 Növbə boşdur."

    await message.reply_text(text)


# ── /volume ───────────────────────────────────────────
@Client.on_message(filters.command(["volume", "ses"]) & filters.group)
async def volume_cmd(client, message):
    if not await is_vc_admin(client, message): return
    chat_id = message.chat.id
    call = vc_clients.get(chat_id)
    if not call:
        return await message.reply_text("❌ Aktiv musiqi yoxdur!")
    try:
        vol = int(message.command[1]) if len(message.command) > 1 else 100
        vol = max(1, min(200, vol))
        await call.change_volume_call(chat_id, vol)
        await message.reply_text(f"🔊 **Səs: {vol}%**")
    except:
        await message.reply_text("İstifadə: `/volume 80`")


# ── /np - indi oxunan ─────────────────────────────────
@Client.on_message(filters.command(["np", "nowplaying"]) & filters.group)
async def np_cmd(client, message):
    chat_id = message.chat.id
    current = now_playing.get(chat_id)
    if not current:
        return await message.reply_text("🎵 Hal-hazırda heç nə oxunmur.")
    dur = format_duration(current.get("duration", 0))
    await message.reply_text(
        f"🎵 **İndi Oxunur:**\n\n"
        f"🎼 **{current['title']}**\n"
        f"⏱ `{dur}`\n"
        f"👤 {current['user']}"
    )


# ── Callback düymələri ────────────────────────────────
@Client.on_callback_query(filters.regex("^vc_"))
async def vc_callback(client, cq: CallbackQuery):
    chat_id = cq.message.chat.id
    data = cq.data
    call = vc_clients.get(chat_id)

    if data == "vc_pause":
        if call:
            try:
                await call.pause_stream(chat_id)
                await cq.answer("⏸ Fasilə verildi!")
                buttons = InlineKeyboardMarkup([
                    [InlineKeyboardButton("▶️ Davam",   callback_data="vc_resume"),
                     InlineKeyboardButton("⏭ Növbəti", callback_data="vc_skip")],
                    [InlineKeyboardButton("⏹ Dayandır", callback_data="vc_stop")],
                ])
                await cq.message.edit_reply_markup(buttons)
            except Exception as e:
                await cq.answer(f"Xəta: {e}", show_alert=True)
        else:
            await cq.answer("Aktiv musiqi yoxdur!", show_alert=True)

    elif data == "vc_resume":
        if call:
            try:
                await call.resume_stream(chat_id)
                await cq.answer("▶️ Davam etdirildi!")
                buttons = InlineKeyboardMarkup([
                    [InlineKeyboardButton("⏸ Fasilə",  callback_data="vc_pause"),
                     InlineKeyboardButton("⏭ Növbəti", callback_data="vc_skip")],
                    [InlineKeyboardButton("🔊 Səs +",  callback_data="vc_vol_up"),
                     InlineKeyboardButton("🔉 Səs -",   callback_data="vc_vol_down")],
                    [InlineKeyboardButton("⏹ Dayandır", callback_data="vc_stop")],
                ])
                await cq.message.edit_reply_markup(buttons)
            except Exception as e:
                await cq.answer(f"Xəta: {e}", show_alert=True)

    elif data == "vc_skip":
        await cq.answer("⏭ Növbəti!")
        await play_next(client, chat_id)

    elif data == "vc_stop":
        music_queues.pop(chat_id, None)
        now_playing.pop(chat_id, None)
        if call:
            try:
                await call.leave_call(chat_id)
            except:
                pass
        vc_clients.pop(chat_id, None)
        await cq.message.edit_caption("⏹ **Musiqi dayandırıldı.**")
        await cq.answer("Dayandırıldı!")

    elif data == "vc_vol_up":
        if call:
            try:
                await call.change_volume_call(chat_id, 150)
                await cq.answer("🔊 Səs artırıldı!")
            except:
                await cq.answer("Xəta!", show_alert=True)

    elif data == "vc_vol_down":
        if call:
            try:
                await call.change_volume_call(chat_id, 50)
                await cq.answer("🔉 Səs azaldıldı!")
            except:
                await cq.answer("Xəta!", show_alert=True)
