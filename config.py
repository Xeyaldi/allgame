import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
# Config-dən yalnız lazım olan tək dəyişənləri çağırırıq
from config import OWNER_LINK, CHANNEL_LINK, SUPPORT_LINK, START_PIC
from database import get_db

@Client.on_message(filters.command("start"))
async def start_cmd(client, message):
    user = message.from_user
    
    # Database qeydiyyatı
    try:
        conn = get_db()
        if conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO broadcast_list (chat_id) VALUES (%s) ON CONFLICT DO NOTHING", (message.chat.id,))
            conn.commit()
            cur.close()
            conn.close()
    except:
        pass

    # İstədiyin o animasiya hissəsi (Qaldı)
    frames = ["⏳", "⏳ ʏüᴋʟəɴɪʀ...", "⏳ ██", "⏳ ████", "✅ ʜᴀᴢɪʀᴅɪʀ!"]
    anim = await message.reply_text(frames[0])
    for f in frames[1:]:
        await asyncio.sleep(0.35)
        await anim.edit_text(f)
    await asyncio.sleep(0.2)
    await anim.delete()

    bot_me = await client.get_me()
    caption = (
        f"✨ **sᴀʟᴀᴍ, {user.first_name}!**\n\n"
        "╔══════════════════╗\n"
        "  🤖 **ʜᴛ ᴜɴɪᴠᴇʀsᴀʟ ʙᴏᴛ**\n"
        "╚══════════════════╝\n\n"
        "🏷 **Tağ** • 🎮 **Oyunlar** • 🎵 **Musiqi**\n"
        "🎧 **Səsli Söhbət** • 🛡 **Moderator** • 🤖 **AI**\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📌 **Bütün funksiyalar bir botda!**"
    )

    # Linkləri təmizlədik: SUPPORT_CHAT və digər təkrarlar silindi
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

    # Şəkil işləyir, stiker yoxdur
    try:
        await client.send_photo(
            chat_id=message.chat.id, 
            photo=START_PIC,
            caption=caption, 
            reply_markup=keyboard
        )
    except:
        await client.send_message(
            chat_id=message.chat.id, 
            text=caption, 
            reply_markup=keyboard
        )
