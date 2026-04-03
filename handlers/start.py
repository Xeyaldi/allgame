import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import OWNERS, OWNER_LINK, CHANNEL_LINK, SUPPORT_CHAT, START_PIC, START_STICKER
from database import get_db

@Client.on_message(filters.command("start"))
async def start_cmd(client, message):
    user = message.from_user
    try:
        conn = get_db()
        if conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO broadcast_list (chat_id) VALUES (%s) ON CONFLICT DO NOTHING", (message.chat.id,))
            conn.commit(); cur.close(); conn.close()
    except: pass

    # Animasiya
    frames = ["⏳", "⏳ ʏüᴋʟəɴɪʀ...", "⏳ ██", "⏳ ████", "✅ ʜᴀᴢɪʀᴅɪʀ!"]
    anim = await message.reply_text(frames[0])
    for f in frames[1:]:
        await asyncio.sleep(0.35)
        await anim.edit_text(f)
    await asyncio.sleep(0.2)
    await anim.delete()

    # Sticker
    try:
        await client.send_sticker(message.chat.id, sticker=START_STICKER)
    except: pass

    bot_me = await client.get_me()
    caption = (
        f"✨ **sᴀʟᴀᴍ, {user.first_name}!**\n\n"
        "╔══════════════════╗\n"
        "  🤖 **ʜᴛ ᴜɴɪᴠᴇʀsᴀʟ ʙᴏᴛ**\n"
        "╚══════════════════╝\n\n"
        "🏷 **Tağ** • 🎮 **Oyunlar** • 🎵 **Musiqi**\n"
        "🎧 **Səsli Söhbət** • 🛡 **Moderator** • 🤖 **AI**\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📌 **Bütün funksiyalar bir botda!**\n"
        "⚙️ Ətraflı məlumat üçün düymələrə bas."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏷 Tağ Sistemi",    callback_data="info_tag"),
         InlineKeyboardButton("🎮 Oyunlar",        callback_data="info_games")],
        [InlineKeyboardButton("🎵 Media Yüklə",   callback_data="info_music"),
         InlineKeyboardButton("🎧 Səsli Söhbət",  callback_data="info_vc")],
        [InlineKeyboardButton("🛡 Moderator",      callback_data="info_mod"),
         InlineKeyboardButton("🤖 AI Chatbot",     callback_data="info_ai")],
        [InlineKeyboardButton("🔧 Digər",          callback_data="info_other")],
        [InlineKeyboardButton("➕ Məni Qrupa Əlavə Et",
                              url=f"https://t.me/{bot_me.username}?startgroup=true")],
        [InlineKeyboardButton("👨‍💻 Sahibi",  url=OWNER_LINK),
         InlineKeyboardButton("📢 Kanal",   url=CHANNEL_LINK)],
        [InlineKeyboardButton("💬 Dəstək Qrupu", url=SUPPORT_CHAT)],
    ])
    await client.send_photo(chat_id=message.chat.id, photo=START_PIC,
                            caption=caption, reply_markup=keyboard)


INFO_TEXTS = {
    "info_tag": (
        "🏷 **TAĞ SİSTEMİ**\n\n━━━━━━━━━━━━━━━━\n"
        "• `/tag [mesaj]` — 💎 Brilyant tağ\n"
        "• `/utag [mesaj]` — 🎲 Emoji tağ\n"
        "• `/flagtag [mesaj]` — 🚩 Bayraq tağ\n"
        "• `/tektag [mesaj]` — 👤 Tək tağ\n"
        "• `/tagstop` — 🛑 Dayandır\n\n"
        "⚠️ Yalnız qruplarda, admin üçün işləyir."
    ),
    "info_games": (
        "🎮 **OYUNLAR**\n\n━━━━━━━━━━━━━━━━\n"
        "• `/menu` — Oyun menyusunu aç\n"
        "• `/xal` — Xalına bax\n"
        "• `/dur` — Oyunu dayandır\n\n"
        "🎯 Rəqəm tapmaca, İsti-soyuq\n"
        "⚡ Riyaziyyat, Yaddaş şimşəyi\n"
        "⭕ XOX, Doğru/Cəsarət\n"
        "🎮 Buton oyunu, Söz zənciri"
    ),
    "info_music": (
        "🎵 **MEDİA YÜKLƏYƏN**\n\n━━━━━━━━━━━━━━━━\n"
        "• Sadəcə link göndər → format seç\n"
        "• `/youtube [ad]` — YouTube axtarış\n\n"
        "✅ YouTube, TikTok, Instagram\n"
        "✅ Twitter/X, Facebook, SoundCloud\n"
        "✅ 1000+ sayt • 2GB-a qədər fayl"
    ),
    "info_vc": (
        "🎧 **SƏSLİ SÖHBƏT MUSİQİ**\n\n━━━━━━━━━━━━━━━━\n"
        "• `/play [ad/link]` — Musiqi oxut\n"
        "• `/vplay [link]` — Video oxut\n"
        "• `/pause` — Fasilə\n"
        "• `/resume` — Davam et\n"
        "• `/skip` — Növbəti\n"
        "• `/stop` — Dayandır\n"
        "• `/queue` — Növbə siyahısı\n"
        "• `/volume [1-200]` — Səs səviyyəsi\n\n"
        "⚠️ STRING_SESSION lazımdır!"
    ),
    "info_mod": (
        "🛡 **MODERATOR**\n\n━━━━━━━━━━━━━━━━\n"
        "• `/stiker off/on` — Stiker/GIF\n"
        "• `/seslimesaj off/on` — Səsli mesaj\n"
        "• `/link on/off` — Link qoruması\n"
        "• `/icaze` — Yetki ver (reply)\n"
        "• `/qadaga [söz]` — Söz qadağa\n\n"
        "⚠️ Bot qrupa admin olmalıdır!"
    ),
    "info_ai": (
        "🤖 **AI CHATBOT (NUNU)**\n\n━━━━━━━━━━━━━━━━\n"
        "• Azərbaycan dilində danışır\n"
        "• Mehriban, canım-balam deyir\n"
        "• `/chatbot on/off` — Aktivləşdir\n\n"
        "🔧 **Digər AI:**\n"
        "• `/wiki [mövzu]` — Vikipediya\n"
        "• `/tercume [dil]` — Tərcümə\n"
        "• `/hava [şəhər]` — Hava"
    ),
    "info_other": (
        "🔧 **DİGƏR**\n\n━━━━━━━━━━━━━━━━\n"
        "• `/sevgi` `/slap` `/zeka` `/sans`\n"
        "• `/masinlar` — Avto kataloq\n"
        "• `/font [mətn]` — Şrift\n"
        "• `/id` `/info` `/ping`\n"
        "• `/valyuta` `/namaz` `/wiki`\n"
        "• `/etiraf` `/acetiraf`\n"
        "• `/yonlendir` — Broadcast (sahibi)"
    ),
}


@Client.on_callback_query(filters.regex("^info_"))
async def info_cb(client, cq: CallbackQuery):
    text = INFO_TEXTS.get(cq.data, "Məlumat tapılmadı.")
    back = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Geri", callback_data="back_start")]])
    try:
        await cq.message.edit_caption(caption=text, reply_markup=back)
    except:
        await cq.message.edit_text(text=text, reply_markup=back)


@Client.on_callback_query(filters.regex("^back_start$"))
async def back_start(client, cq: CallbackQuery):
    bot_me = await client.get_me()
    caption = (
        f"✨ **sᴀʟᴀᴍ, {cq.from_user.first_name}!**\n\n"
        "╔══════════════════╗\n"
        "  🤖 **ʜᴛ ᴜɴɪᴠᴇʀsᴀʟ ʙᴏᴛ**\n"
        "╚══════════════════╝\n\n"
        "🏷 **Tağ** • 🎮 **Oyunlar** • 🎵 **Musiqi**\n"
        "🎧 **Səsli Söhbət** • 🛡 **Moderator** • 🤖 **AI**\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📌 **Bütün funksiyalar bir botda!**"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏷 Tağ Sistemi",    callback_data="info_tag"),
         InlineKeyboardButton("🎮 Oyunlar",        callback_data="info_games")],
        [InlineKeyboardButton("🎵 Media Yüklə",   callback_data="info_music"),
         InlineKeyboardButton("🎧 Səsli Söhbət",  callback_data="info_vc")],
        [InlineKeyboardButton("🛡 Moderator",      callback_data="info_mod"),
         InlineKeyboardButton("🤖 AI Chatbot",     callback_data="info_ai")],
        [InlineKeyboardButton("🔧 Digər",          callback_data="info_other")],
        [InlineKeyboardButton("➕ Məni Qrupa Əlavə Et",
                              url=f"https://t.me/{bot_me.username}?startgroup=true")],
        [InlineKeyboardButton("👨‍💻 Sahibi",  url=OWNER_LINK),
         InlineKeyboardButton("📢 Kanal",   url=CHANNEL_LINK)],
        [InlineKeyboardButton("💬 Dəstək Qrupu", url=SUPPORT_CHAT)],
    ])
    try:
        await cq.message.edit_caption(caption=caption, reply_markup=keyboard)
    except:
        await cq.message.edit_text(text=caption, reply_markup=keyboard)
