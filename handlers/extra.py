import asyncio
import random
import requests
import urllib.parse
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import OWNERS
from database import get_db

# ============================================================
#  ƏLAVƏ FUNKSİYALAR
# ============================================================

# --- HELP ---
@Client.on_message(filters.command("help"))
async def help_cmd(client, message):
    text = (
        "📚 **BOT KOMANDALARI**\n\n"
        "🏷 **TAĞ:**\n"
        "`/tag`, `/utag`, `/flagtag`, `/tektag`, `/tagstop`\n\n"
        "🎮 **OYUNLAR:**\n"
        "`/menu` — Oyun menyusu\n"
        "`/xal` — Xalına bax\n"
        "`/dur` — Oyunu dayandır\n\n"
        "🎵 **MUSİQİ:**\n"
        "`/youtube [ad]` — Axtarış\n"
        "Sadəcə link göndər → format seç\n\n"
        "🛡 **MODERATOR:**\n"
        "`/stiker on/off` • `/seslimesaj off/on`\n"
        "`/link on/off` • `/icaze` (reply)\n\n"
        "🤖 **AI:**\n"
        "`/chatbot on/off` — Chatbot\n\n"
        "🔧 **DİGƏR:**\n"
        "`/sevgi` • `/slap` • `/zeka` • `/sans`\n"
        "`/masinlar` • `/font [mətn]`\n"
        "`/id` • `/info` • `/valyuta`\n"
        "`/namaz [şəhər]` • `/wiki [mövzu]`\n"
        "`/tercume [dil]` (reply)\n"
        "`/etiraf [mesaj]` • `/acetiraf [mesaj]`"
    )
    await message.reply_text(text)


# --- ID ---
@Client.on_message(filters.command("id"))
async def id_cmd(client, message):
    uid = message.from_user.id
    cid = message.chat.id
    await message.reply_text(
        f"👤 **Sizin ID:** `{uid}`\n"
        f"💬 **Chat ID:** `{cid}`"
    )


# --- INFO ---
@Client.on_message(filters.command("info"))
async def info_cmd(client, message):
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    mention = f"[{target.first_name}](tg://user?id={target.id})"
    uname = f"@{target.username}" if target.username else "Yoxdur"
    await message.reply_text(
        f"👤 **İstifadəçi Məlumatı**\n\n"
        f"🏷 Ad: {mention}\n"
        f"🔗 Username: {uname}\n"
        f"🆔 ID: `{target.id}`\n"
        f"🤖 Bot: {'✅' if target.is_bot else '❌'}"
    )


# --- HAVA ---
@Client.on_message(filters.command("hava"))
async def weather_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("🏙 Şəhər adı yazın: `/hava Baku`")
    city = message.command[1]
    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather"
            f"?q={urllib.parse.quote(city)}&appid=b6907d289e10d714a6e88b30761fae22"
            f"&units=metric&lang=az"
        ).json()
        await message.reply_text(
            f"🌤 **{city.capitalize()}**\n"
            f"🌡 Temperatur: {r['main']['temp']}°C\n"
            f"☁️ Vəziyyət: {r['weather'][0]['description']}\n"
            f"💧 Rütubət: {r['main']['humidity']}%\n"
            f"💨 Külək: {r['wind']['speed']} m/s"
        )
    except:
        await message.reply_text("❌ Şəhər tapılmadı.")


# --- VALYUTA ---
@Client.on_message(filters.command("valyuta"))
async def valyuta_cmd(client, message):
    try:
        r = requests.get("https://api.exchangerate-api.com/v4/latest/AZN").json()
        await message.reply_text(
            f"💰 **Məzənnə (AZN):**\n\n"
            f"🇺🇸 1 USD = {1/r['rates']['USD']:.4f} AZN\n"
            f"🇪🇺 1 EUR = {1/r['rates']['EUR']:.4f} AZN\n"
            f"🇷🇺 1 RUB = {1/r['rates']['RUB']:.4f} AZN\n"
            f"🇹🇷 1 TRY = {1/r['rates']['TRY']:.4f} AZN"
        )
    except:
        await message.reply_text("❌ Məzənnə alınmadı.")


# --- NAMAZ ---
@Client.on_message(filters.command("namaz"))
async def namaz_cmd(client, message):
    city = message.command[1] if len(message.command) > 1 else "Baku"
    try:
        r = requests.get(
            f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=Azerbaijan&method=3",
            headers={'User-Agent': 'Mozilla/5.0'}, timeout=10
        ).json()
        if 'data' not in r:
            return await message.reply_text("❌ Şəhər tapılmadı (İngiliscə: `/namaz Ganja`)")
        t = r['data']['timings']
        await message.reply_text(
            f"🕋 **{city.capitalize()} Namaz Vaxtları**\n\n"
            f"🌅 Sübh: `{t['Fajr']}`\n"
            f"☀️ Günəş: `{t['Sunrise']}`\n"
            f"🕛 Zöhr: `{t['Dhuhr']}`\n"
            f"🕒 Əsr: `{t['Asr']}`\n"
            f"🌇 Axşam: `{t['Maghrib']}`\n"
            f"🌃 İşa: `{t['Isha']}`"
        )
    except:
        await message.reply_text("⚠️ Namaz vaxtları gətirmək mümkün olmadı.")


# --- TƏRCÜmə ---
@Client.on_message(filters.command("tercume") & filters.reply)
async def translate_cmd(client, message):
    text = message.reply_to_message.text
    if not text:
        return
    if len(message.command) > 1:
        lang = message.command[1].lower()
        try:
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={lang}&dt=t&q={urllib.parse.quote(text)}"
            r = requests.get(url).json()
            await message.reply_text(f"🌐 **{lang.upper()}:**\n`{r[0][0][0]}`")
        except:
            await message.reply_text("❌ Xəta.")
    else:
        langs = {"en": "🇬🇧 EN", "tr": "🇹🇷 TR", "ru": "🇷🇺 RU", "de": "🇩🇪 DE", "fr": "🇫🇷 FR"}
        res = "🌐 **5 Dilə Tərcümə:**\n\n"
        for code, name in langs.items():
            try:
                url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={code}&dt=t&q={urllib.parse.quote(text)}"
                r = requests.get(url).json()
                res += f"🔹 {name}: `{r[0][0][0]}`\n"
            except:
                continue
        await message.reply_text(res)


# --- WİKİ ---
@Client.on_message(filters.command("wiki"))
async def wiki_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Mövzu yazın: `/wiki Azərbaycan`")
    query = " ".join(message.command[1:])
    try:
        import wikipedia
        wikipedia.set_lang("az")
        summary = wikipedia.summary(query, sentences=3)
        await message.reply_text(f"📖 **{query}**\n\n{summary}")
    except Exception:
        await message.reply_text("❌ Tapılmadı.")


# --- SEVGİ ---
@Client.on_message(filters.command("sevgi") & filters.group)
async def love_cmd(client, message):
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    else:
        return await message.reply_text("💖 Analiz üçün birinə reply atın.")
    if target.id == message.from_user.id:
        return await message.reply_text("😅 Özünə eşq elan etmək?")
    status = await message.reply_text("🧪 **Analiz edilir...**")
    await asyncio.sleep(1)
    p = random.randint(0, 100)
    bar = "❤️" * (p // 10) + "🖤" * (10 - (p // 10))
    await status.edit_text(
        f"╔════════════════════╗\n"
        f"  ❤️ SEVGİ HESABATI\n"
        f"╚════════════════════╝\n\n"
        f"👤 **Aşiq:** {message.from_user.first_name}\n"
        f"👤 **Məşuq:** {target.first_name}\n\n"
        f"📊 **Uyğunluq:** `{p}%`\n"
        f"**[{bar}]**"
    )


# --- ŞAPALAQ ---
SLAPS = [
    "{me}, {him} şəxsini **Osmanlı şilləsi** ilə yerə sərdi! 🧤",
    "{me}, {him} üzünə **45 razmer yaş krossovka** tulladı! 👟",
    "{me}, {him} şəxsini **Xəzər nərəsi** ilə döydü! 🐟",
    "{me}, {him} şəxsinə **Mayk Tayson** zərbəsi vurdu! 🥊",
    "{me}, {him} şəxsini **Marsa** fırlatdı! 🛸",
    "{me}, {him} başına **isti tava** ilə vurdu (DANNG!) 🍳",
    "{me}, {him} şəxsini **raketlə** Aya göndərdi! 🚀",
    "{me}, {him} üstünə **ac bir T-Rex** buraxdı! 🦖",
]

@Client.on_message(filters.command("slap") & filters.group)
async def slap_cmd(client, message):
    if message.reply_to_message:
        t_user = message.reply_to_message.from_user
    else:
        return await message.reply_text("👊 Kimi vuraq? (Birinin mesajına reply at)")
    me = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    him = f"[{t_user.first_name}](tg://user?id={t_user.id})"
    txt = random.choice(SLAPS).format(me=me, him=him)
    await message.reply_text(txt)


# --- ZEKA ---
@Client.on_message(filters.command("zeka") & filters.group)
async def zeka_cmd(client, message):
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    status = await message.reply_text("🌀 **Skan edilir...**")
    await asyncio.sleep(1)
    iq = random.randint(30, 200)
    await status.edit_text(f"🧠 **IQ Analizi:**\n👤 {target.first_name}\n📊 Nəticə: `{iq}` IQ")


# --- ŞANS ---
@Client.on_message(filters.command("sans") & filters.group)
async def sans_cmd(client, message):
    love = random.randint(10, 100)
    money = random.randint(10, 100)
    health = random.randint(10, 100)
    await message.reply_text(
        f"🍀 **Günün Şansı:**\n\n"
        f"❤️ Sevgi: %{love}\n"
        f"💰 Pul: %{money}\n"
        f"🍏 Sağlamlıq: %{health}"
    )


# --- MAŞINLAR ---
CAR_INFO = {
    "ferrari": ("🏎️ FERRARI (İtaliya)", "Yarış dünyasının (Formula 1) kralı. Qırmızı rəngi və 'Şahə qalxmış at' loqosu ilə tanınır. Sürət, lüks və aerodinamikanın zirvəsi."),
    "lambo":   ("🐃 LAMBORGHINI (İtaliya)", "Aqressiv dizaynı ilə tanınır. Loqosundakı qəzəbli buğa gücün rəmzidir. 'Aventador' və 'Huracan' modelləri məşhurdur."),
    "bmw":     ("🌀 BMW (Almaniya)", "Şüar: 'Sürmə həzzi'. Arxa çəkişli balansı ilə məşhurdur. M seriyası dünyada ən çox sevilən idman sedanlarıdır."),
    "merc":    ("⭐️ MERCEDES-BENZ (Almaniya)", "Şüar: 'The Best or Nothing'. Lüksün və təhlükəsizliyin pioneridir. S-Class dövlət başçılarının seçimidir."),
    "bugatti": ("💎 BUGATTI (Fransa)", "1500+ at gücü, W16 mühərrik. 400 km/saat üstü sürət. Hər biri əllə yığılır — sənət əsəri hesab olunur."),
    "tesla":   ("⚡ TESLA (ABŞ)", "Plaid modeli 0-100 km/saat 2 saniyədə. Avtopilot sistemi var. Dünyanı elektrikli nəqliyyata keçirməkdə liderdir."),
    "porsche": ("🐎 PORSCHE (Almaniya)", "911 modeli 50+ ildir mükəmməlləşdirilir. Gündəlik şəhər sürüşünə uyğun yeganə superkardır."),
    "rolls":   ("👑 ROLLS-ROYCE (Böyük Britaniya)", "Ən lüks sedan. Salonda saatin çıqqıltısını eşitmək olar. 'Spirit of Ecstasy' fiquru simvoludur."),
}

@Client.on_message(filters.command("masinlar"))
async def cars_cmd(client, message):
    buttons = [
        [InlineKeyboardButton("🏎️ Ferrari",    callback_data="car_ferrari"),
         InlineKeyboardButton("🐃 Lamborghini", callback_data="car_lambo")],
        [InlineKeyboardButton("🌀 BMW",         callback_data="car_bmw"),
         InlineKeyboardButton("⭐️ Mercedes",   callback_data="car_merc")],
        [InlineKeyboardButton("💎 Bugatti",     callback_data="car_bugatti"),
         InlineKeyboardButton("⚡ Tesla",       callback_data="car_tesla")],
        [InlineKeyboardButton("🐎 Porsche",     callback_data="car_porsche"),
         InlineKeyboardButton("👑 Rolls-Royce", callback_data="car_rolls")],
    ]
    await message.reply_text("🚗 **PREMİUM AVTO KATALOQ**\nSeçim edin:", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^car_"))
async def car_info_cb(client, cq: CallbackQuery):
    key = cq.data.split("_")[1]
    if key == "back":
        return await cars_cmd(client, cq.message)
    info = CAR_INFO.get(key)
    if not info:
        return await cq.answer("Tapılmadı")
    title, desc = info
    await cq.message.edit_text(
        f"**{title}**\n\n{desc}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Geri", callback_data="car_back")]])
    )
    await cq.answer()


# --- FONT ---
FONTS = {
    "f1": "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫",
    "f2": "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃",
    "f3": "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷",
    "f4": "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ",
    "f5": "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ",
}
NORMAL = "abcdefghijklmnopqrstuvwxyz"

def convert_font(text, fid):
    if fid == "f6":
        return text[::-1]
    font_chars = FONTS.get(fid, "")
    result = ""
    for ch in text.lower():
        idx = NORMAL.find(ch)
        result += font_chars[idx] if idx != -1 and font_chars else ch
    return result

@Client.on_message(filters.command("font"))
async def font_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Mətn yazın: `/font Salam`")
    user_text = " ".join(message.command[1:])
    buttons = [
        [InlineKeyboardButton("𝕯𝖔𝖚𝖇𝖑𝖊", callback_data=f"fn_f1"),
         InlineKeyboardButton("𝓢𝓬𝓻𝓲𝓹𝓽",  callback_data=f"fn_f2")],
        [InlineKeyboardButton("𝔉𝔯𝔞𝔨𝔱𝔲𝔯",  callback_data=f"fn_f3"),
         InlineKeyboardButton("Ⓒⓘⓡⓒⓛⓔ",  callback_data=f"fn_f4")],
        [InlineKeyboardButton("sᴍᴀʟʟ",     callback_data=f"fn_f5"),
         InlineKeyboardButton("pǝʇɹǝʌuI",  callback_data=f"fn_f6")],
    ]
    await message.reply_text(
        f"📝 **Mətniniz:** `{user_text}`\nŞrift seçin:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^fn_"))
async def font_cb(client, cq: CallbackQuery):
    fid = cq.data.split("_")[1]
    try:
        original = cq.message.text.split("`")[1]
    except:
        return await cq.answer("Mətn tapılmadı")
    converted = convert_font(original, fid)
    await cq.message.edit_text(f"✨ **Yeni şriftlə:**\n\n`{converted}`")
    await cq.answer()


# --- ETİRAF ---
@Client.on_message(filters.command(["etiraf", "acetiraf"]))
async def etiraf_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Etirafınızı yazın: `/etiraf sözünüz`")
    is_anon = message.command[0] == "etiraf"
    etiraf_text = message.text.split(None, 1)[1]
    sender = "Anonim" if is_anon else message.from_user.mention
    for owner_id in OWNERS:
        try:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Yayımla", callback_data=f"pub_etiraf|{etiraf_text[:50]}|{message.chat.id}"),
                 InlineKeyboardButton("❌ Rədd Et",  callback_data="rej_etiraf")]
            ])
            await client.send_message(
                owner_id,
                f"📩 **Yeni Etiraf:**\n\n{sender}: {etiraf_text}",
                reply_markup=keyboard
            )
        except:
            pass
    await message.reply_text("✅ Etirafınız sahibə göndərildi. Yayımlanmağı gözləyin.")

@Client.on_callback_query(filters.regex("^(pub|rej)_etiraf"))
async def etiraf_decision(client, cq: CallbackQuery):
    if cq.data.startswith("pub_etiraf"):
        parts = cq.data.split("|")
        text = parts[1] if len(parts) > 1 else "?"
        chat_id = int(parts[2]) if len(parts) > 2 else None
        if chat_id:
            try:
                await client.send_message(chat_id, f"📢 **Etiraf:**\n\n{text}")
            except:
                pass
        await cq.message.edit_text("✅ Etiraf yayımlandı.")
    else:
        await cq.message.edit_text("❌ Etiraf rədd edildi.")


# --- YÖNLƏNDIRMƏ (SAHİB) ---
@Client.on_message(filters.command("yonlendir") & filters.user(OWNERS))
async def broadcast_cmd(client, message):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Yönləndirilәcək mesajı yazın!")
    status_msg = await message.reply_text("📢 Yönləndirilir...")
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT chat_id FROM broadcast_list")
        chats = cur.fetchall()
        cur.close(); conn.close()
    except:
        chats = []
    success = 0
    for (cid,) in chats:
        try:
            if message.reply_to_message:
                await message.reply_to_message.copy(cid)
            else:
                await client.send_message(cid, message.text.split(None, 1)[1])
            success += 1
            await asyncio.sleep(0.3)
        except:
            continue
    await status_msg.edit_text(f"✅ Yönləndirmə tamamlandı: {success} yerə göndərildi.")


# --- PING ---
@Client.on_message(filters.command("ping"))
async def ping_cmd(client, message):
    import time
    start = time.time()
    msg = await message.reply_text("🏓 Pong!")
    ms = round((time.time() - start) * 1000)
    await msg.edit_text(f"🏓 Pong! `{ms}ms`")
