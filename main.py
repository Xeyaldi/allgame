import sys
import os
import asyncio
from types import ModuleType

# Python 3.13+ yamaq
try:
    import imghdr
except ImportError:
    imghdr = ModuleType('imghdr')
    sys.modules['imghdr'] = imghdr

from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, STRING1, STRING2, STRING3, OWNERS
from database import init_db, init_mongo

# ── Bot Client ────────────────────────────────────────
app = Client(
    "ht_unified_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="handlers"),
)

# ── Userbot Clients (Səsli Söhbət üçün) ──────────────
userbot_clients = []

async def start_userbots():
    strings = [s for s in [STRING1, STRING2, STRING3] if s]
    if not strings:
        print("⚠️  STRING_SESSION yoxdur — Səsli söhbət musiqi deaktivdir.")
        return

    from pytgcalls import PyTgCalls

    for i, session_str in enumerate(strings, 1):
        try:
            ub = Client(
                f"userbot_{i}",
                api_id=API_ID,
                api_hash=API_HASH,
                session_string=session_str,
            )
            await ub.start()
            call = PyTgCalls(ub)
            await call.start()
            userbot_clients.append((ub, call))
            print(f"✅ Userbot {i} hazırdır!")

            # music_vc handler-inə userbot-u ötür
            app._userbot = ub
            app._pytgcalls = call
        except Exception as e:
            print(f"❌ Userbot {i} xətası: {e}")


async def main():
    print("🔧 Database hazırlanır...")
    init_db()
    await init_mongo()

    print("🤖 Bot başladılır...")
    await app.start()

    print("🎧 Userbot-lar başladılır...")
    await start_userbots()

    me = await app.get_me()
    print(f"✅ Bot aktiv: @{me.username}")

    # Sahibə bildiriş göndər
    for owner_id in OWNERS:
        try:
            await app.send_message(
                owner_id,
                "✅ **HT Universal Bot aktiv oldu!**\n\n"
                f"🤖 Bot: @{me.username}\n"
                f"🎧 Userbot: {'✅ Aktiv' if userbot_clients else '❌ Yoxdur'}\n"
                f"🤖 AI: {'✅ OpenAI' if os.getenv('OPENAI_API_KEY') else '❌ Yoxdur'}"
            )
        except:
            pass

    await asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Bot dayandırıldı.")
    finally:
        for ub, call in userbot_clients:
            try:
                loop.run_until_complete(call.stop())
                loop.run_until_complete(ub.stop())
            except:
                pass
        loop.run_until_complete(app.stop())
