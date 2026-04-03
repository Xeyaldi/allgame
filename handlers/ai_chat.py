import asyncio
import random
from pyrogram import Client, filters, enums
from pyrogram.enums import ChatMemberStatus
from config import OWNERS, OPENAI_API_KEY

chatbot_status = {}

NUNU_PROMPT = (
    "Sənin adın Nunudur. Sən çox mehriban, şirin və köməkçil bir Azərbaycanlı qızsan. "
    "İstifadəçilərlə danışarkən 'canım', 'balam', 'şirinim', 'əzizim' kimi səmimi sözlər işlədirsən. "
    "Sən robot deyilsən, sanki bir insanın yaxın dostusan. "
    "Azərbaycan dilində çox təbii danışırsan və həmişə pozitivsən."
)


async def get_ai_response(text):
    if not OPENAI_API_KEY:
        return None
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": NUNU_PROMPT},
                {"role": "user", "content": text}
            ],
            max_tokens=500,
            temperature=0.8,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI xəta: {e}")
        return None


@Client.on_message(filters.command("chatbot"))
async def chatbot_toggle(client, message):
    uid = message.from_user.id
    chat_id = message.chat.id
    is_admin = uid in OWNERS
    if not is_admin:
        try:
            member = await client.get_chat_member(chat_id, uid)
            is_admin = member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
        except:
            pass
    if not is_admin:
        return

    if len(message.command) < 2:
        return await message.reply_text("İstifadə: `/chatbot on` və ya `/chatbot off`")

    s = message.command[1].lower()
    if s == "on":
        chatbot_status[chat_id] = True
        await message.reply_text("✅ **Chatbot aktiv edildi!**\n🤖 Nunu hazırdır, canım!")
    elif s == "off":
        chatbot_status[chat_id] = False
        await message.reply_text("❌ **Chatbot söndürüldü.**")


@Client.on_message(filters.text & ~filters.bot, group=0)
async def nunu_handler(client, message):
    if not OPENAI_API_KEY:
        return

    chat_id = message.chat.id
    is_private = message.chat.type == enums.ChatType.PRIVATE

    is_reply_to_me = False
    if message.reply_to_message and message.reply_to_message.from_user:
        me = await client.get_me()
        if message.reply_to_message.from_user.id == me.id:
            is_reply_to_me = True

    in_group_active = (
        not is_private and
        chatbot_status.get(chat_id, False) and
        (is_reply_to_me or random.random() < 0.15)
    )

    if not (is_private or in_group_active):
        return

    if message.text and message.text.startswith("/"):
        return

    try:
        await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
        answer = await get_ai_response(message.text)
        if answer:
            await asyncio.sleep(0.8)
            await message.reply_text(answer)
    except Exception as e:
        print(f"Nunu xəta: {e}")
