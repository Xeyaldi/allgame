import asyncio
import random
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNERS

tag_process = {}

BAYRAQLAR = [
    "🇦🇿","🇹🇷","🇵🇰","🇺🇿","🇰🇿","🇰🇬","🇹🇲","🇦🇱","🇩🇿","🇦🇲",
    "🇦🇺","🇦🇹","🇧🇷","🇧🇬","🇨🇦","🇨🇳","🇨🇴","🇨🇺","🇨🇾","🇨🇿",
    "🇩🇰","🇩🇴","🇪🇬","🇪🇪","🇫🇮","🇫🇷","🇩🇪","🇬🇭","🇬🇷","🇭🇺",
    "🇮🇳","🇮🇩","🇮🇷","🇮🇪","🇮🇱","🇮🇹","🇯🇵","🇯🇴","🇰🇪","🇰🇼",
    "🇱🇻","🇱🇧","🇱🇾","🇱🇹","🇲🇾","🇲🇻","🇲🇽","🇲🇦","🇳🇱","🇳🇿",
    "🇳🇬","🇳🇴","🇴🇲","🇵🇦","🇵🇾","🇵🇪","🇵🇭","🇵🇱","🇵🇹","🇶🇦",
    "🇷🇴","🇷🇺","🇸🇦","🇷🇸","🇸🇬","🇸🇰","🇸🇮","🇸🇴","🇿🇦","🇰🇷",
    "🇪🇸","🇱🇰","🇸🇩","🇸🇪","🇨🇭","🇸🇾","🇹🇼","🇹🇯","🇹🇿","🇹🇭",
    "🇹🇳","🇺🇬","🇺🇦","🇦🇪","🇬🇧","🇺🇸","🇺🇾","🇻🇳","🇾🇪","🇿🇲"
]

EMOJILER = [
    "🌈","🪐","🎡","🍭","💎","🔮","⚡","🔥","🚀","🛸","🎈","🎨",
    "🎭","🎸","👾","🧪","🧿","🍀","🍿","🎁","🔋","🧸","🎉","✨",
    "🌟","🌙","☀️","☁️","🌊","🌋","☄️","🍄","🌹","🌸","🌵","🌴",
    "🍁","🍎","🍓","🍍","🥥","🍔","🍕","🍦","🍩","🥤","🚲","🏎️",
    "🚁","⛵","🛰️","📱","💻","💾","📸","🎥","🏮","🎬","🎧","🎤",
    "🎹","🎺","🎻","🎲","🎯","🎮","🧩","🦄","🦁","🦊","🐼","🦋"
]


async def is_admin(client, message):
    if message.chat.type == ChatType.PRIVATE:
        return True
    if message.from_user and message.from_user.id in OWNERS:
        return True
    try:
        from pyrogram.enums import ChatMemberStatus
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except:
        return False


@Client.on_message(filters.command(["tag", "utag", "flagtag", "tektag"]) & filters.group)
async def tag_handler(client, message):
    if not await is_admin(client, message):
        return await message.reply_text("❌ Bu komanda yalnız adminlər üçündür!")

    chat_id = message.chat.id
    tag_process[chat_id] = True
    cmd = message.command[0]
    user_msg = " ".join(message.command[1:]) if len(message.command) > 1 else ""

    await message.reply_text(f"✅ **{cmd} başladı!**")

    async for m in client.get_chat_members(chat_id):
        if not tag_process.get(chat_id, False):
            break
        if m.user and not m.user.is_bot:
            try:
                name = m.user.first_name
                uid  = m.user.id
                if cmd == "tag":
                    tag_text = f"💎 [{name}](tg://user?id={uid}) {user_msg}"
                elif cmd == "utag":
                    tag_text = f"{random.choice(EMOJILER)} [{name}](tg://user?id={uid}) {user_msg}"
                elif cmd == "flagtag":
                    tag_text = f"{random.choice(BAYRAQLAR)} [{name}](tg://user?id={uid}) {user_msg}"
                elif cmd == "tektag":
                    tag_text = f"👤 [{name}](tg://user?id={uid}) {user_msg}"
                await client.send_message(chat_id, tag_text.strip())
                await asyncio.sleep(2.5)
            except:
                pass


@Client.on_message(filters.command("tagstop") & filters.group)
async def stop_tag(client, message):
    if not await is_admin(client, message):
        return
    tag_process[message.chat.id] = False
    await message.reply_text("🛑 **Tağ dayandırıldı.**")
