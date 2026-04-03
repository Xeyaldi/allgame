import re
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNERS
from database import get_db

group_settings = {}  # {chat_id: {"sticker": bool, "voice": bool, "allowed": []}}
link_block_status = {}
BANNED_WORDS = []  # Yaddaşda saxlanılır + DB-dən yüklənir


async def has_permission(client, message):
    if message.chat.type == ChatType.PRIVATE:
        return True
    uid = message.from_user.id if message.from_user else 0
    if uid in OWNERS:
        return True
    try:
        member = await client.get_chat_member(message.chat.id, uid)
        if member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            return True
    except:
        pass
    allowed = group_settings.get(message.chat.id, {}).get("allowed", [])
    return uid in allowed


# --- STİKER KONTROL ---
@Client.on_message(filters.command("stiker") & filters.group)
async def stiker_control(client, message):
    if not await has_permission(client, message):
        return await message.reply_text("❌ Bu komanda yalnız qrup qurucusu üçündür!")
    chat_id = message.chat.id
    if chat_id not in group_settings:
        group_settings[chat_id] = {"sticker": False, "voice": False, "allowed": []}
    status = message.command[1].lower() if len(message.command) > 1 else ""
    if status == "off":
        group_settings[chat_id]["sticker"] = True
        await message.reply_text("🚫 Bütün stiker və GIF-lər bağlandı!")
    elif status == "on":
        group_settings[chat_id]["sticker"] = False
        await message.reply_text("✅ Stiker və GIF-lərə icazə verildi.")
    else:
        await message.reply_text("İstifadə: `/stiker on` və ya `/stiker off`")


# --- SƏSLİ MESAJ KONTROL ---
@Client.on_message(filters.command("seslimesaj") & filters.group)
async def voice_control(client, message):
    if not await has_permission(client, message):
        return await message.reply_text("❌ Bu komanda yalnız qrup qurucusu üçündür!")
    chat_id = message.chat.id
    if chat_id not in group_settings:
        group_settings[chat_id] = {"sticker": False, "voice": False, "allowed": []}
    status = message.command[1].lower() if len(message.command) > 1 else ""
    if status == "off":
        group_settings[chat_id]["voice"] = True
        await message.reply_text("🚫 Səsli mesajlar bağlandı!")
    elif status == "on":
        group_settings[chat_id]["voice"] = False
        await message.reply_text("✅ Səsli mesajlara icazə verildi.")
    else:
        await message.reply_text("İstifadə: `/seslimesaj off` (bağlamaq) ya `/seslimesaj on` (açmaq)")


# --- İCAZƏ VER ---
@Client.on_message(filters.command("icaze") & filters.group)
async def give_permission(client, message):
    if not await has_permission(client, message):
        return await message.reply_text("❌ Bu komandanı ancaq qurucu işlədə bilər.")
    if not message.reply_to_message:
        return await message.reply_text("Yetki vermək üçün istifadəçinin mesajına reply atın.")
    chat_id = message.chat.id
    new_user = message.reply_to_message.from_user.id
    if chat_id not in group_settings:
        group_settings[chat_id] = {"sticker": False, "voice": False, "allowed": []}
    if new_user not in group_settings[chat_id]["allowed"]:
        group_settings[chat_id]["allowed"].append(new_user)
        await message.reply_text(f"✅ {message.reply_to_message.from_user.first_name} artıq botu idarə edə bilər.")
    else:
        await message.reply_text("Bu şəxs artıq yetkilidir.")


# --- LİNK QORUMA ---
@Client.on_message(filters.command("link") & filters.group)
async def link_toggle(client, message):
    if not await has_permission(client, message):
        return
    if len(message.command) < 2:
        return await message.reply_text("/link on/off")
    s = message.command[1].lower()
    link_block_status[message.chat.id] = (s == "on")
    await message.reply_text(f"🛡 Link qoruması **{s}** edildi.")


# --- MESAJ SİL (SAHİB) ---
@Client.on_message(filters.command("mesajisil"))
async def mesaj_isil(client, message):
    if message.from_user.id not in OWNERS:
        return
    if not message.reply_to_message:
        return await message.reply_text("Silmək üçün bir mesaja reply atın.")
    try:
        await message.reply_to_message.delete()
        await message.delete()
    except:
        pass


# --- SÖYÜş SİYAHISI (SAHİB) ---
@Client.on_message(filters.command("pisseyler"))
async def pisseyler(client, message):
    if message.from_user.id not in OWNERS:
        return
    if not BANNED_WORDS:
        return await message.reply_text("Siyahı hazırda boşdur.")
    await message.reply_text("🚫 Qeyd olunan söyüşlər:\n\n" + ", ".join(BANNED_WORDS))


@Client.on_message(filters.command("pissozplus"))
async def pissozplus(client, message):
    if message.from_user.id not in OWNERS:
        return
    if not message.command[1:]:
        return await message.reply_text("İstifadə: `/pissozplus söz1 söz2`")
    added = []
    for w in message.command[1:]:
        w = w.lower()
        if w not in BANNED_WORDS:
            BANNED_WORDS.append(w)
            added.append(w)
    await message.reply_text(f"✅ Əlavə edildi: {', '.join(added)}" if added else "Artıq var idi.")


@Client.on_message(filters.command("deleteqeyd"))
async def deleteqeyd(client, message):
    if message.from_user.id not in OWNERS:
        return
    if len(message.command) < 2:
        return await message.reply_text("İstifadə: `/deleteqeyd söz`")
    word = message.command[1].lower()
    if word in BANNED_WORDS:
        BANNED_WORDS.remove(word)
        await message.reply_text(f"🗑️ '{word}' siyahıdan silindi.")
    else:
        await message.reply_text("Bu söz siyahıda tapılmadı.")


# --- QADAQA (DB-dən) ---
@Client.on_message(filters.command("qadaga"))
async def qadaga_cmd(client, message):
    if message.from_user.id not in OWNERS:
        return await message.reply_text("⚠️ Bu əmrdən yalnız sahibi istifadə edə bilər")
    if len(message.command) < 2:
        return await message.reply_text("Zəhmət olmasa qadağan ediləcək sözü yazın.")
    word = message.text.split(None, 1)[1].lower()
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO qadaga_list (word) VALUES (%s) ON CONFLICT DO NOTHING", (word,))
        conn.commit(); cur.close(); conn.close()
    except:
        pass
    await message.reply_text(f"✅ **{word}** sözü qadağan olunanlara əlavə edildi.")


# --- ƏSAS MESAJ İDARƏÇİSİ ---
@Client.on_message(filters.group & ~filters.bot, group=2)
async def mod_handler(client, message):
    if not message.from_user:
        return
    chat_id = message.chat.id
    uid = message.from_user.id
    privileged = await has_permission(client, message)

    # Link silmə
    if not privileged and message.text:
        if re.search(r'(https?://[^\s]+|t\.me/[^\s]+)', message.text.lower()):
            if link_block_status.get(chat_id, False):
                try:
                    await message.delete()
                    return
                except:
                    pass

    # Stiker/GIF blok
    if not privileged and group_settings.get(chat_id, {}).get("sticker", False):
        if message.sticker or message.animation:
            try:
                await message.delete()
            except:
                pass
            return

    # Səsli mesaj blok
    if not privileged and group_settings.get(chat_id, {}).get("voice", False):
        if message.voice or message.video_note:
            try:
                await message.delete()
            except:
                pass
            return

    # Söyüş filtri
    if message.text:
        text_lower = message.text.lower()
        # Yaddaşdakı sözlər
        for word in BANNED_WORDS:
            if word in text_lower:
                try:
                    await message.delete()
                    await client.send_message(
                        chat_id,
                        f"⚠️ {message.from_user.mention}, normal danışın!",
                        parse_mode="html"
                    )
                except:
                    pass
                return
        # DB qadağa sözlər
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT word FROM qadaga_list")
            db_words = [r[0] for r in cur.fetchall()]
            cur.close(); conn.close()
            for word in db_words:
                if word in text_lower and uid not in OWNERS:
                    try:
                        await message.delete()
                    except:
                        pass
                    return
        except:
            pass
