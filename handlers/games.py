import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatType
from database import get_db

# ============================================================
#  OYUN VƏZİYYƏTLƏRİ
# ============================================================
active_games = {}   # {chat_id: {"type": ..., "data": ...}}

# ============================================================
#  OYUN MENYUSU
# ============================================================
@Client.on_message(filters.command("menu") & filters.group)
async def game_menu(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 Söz İzahı",        callback_data="g_sozizahi"),
         InlineKeyboardButton("📝 Boşluq Doldurma",  callback_data="g_bosluq")],
        [InlineKeyboardButton("🔄 Söz Sarmalı",      callback_data="g_wordle"),
         InlineKeyboardButton("⚡ Sürətli Riyaziyyat",callback_data="g_riyaziyyat")],
        [InlineKeyboardButton("🎲 Rəqəm Tapmaca",    callback_data="g_reqem"),
         InlineKeyboardButton("❓ Tap Görəlim",       callback_data="g_tapgorelim")],
        [InlineKeyboardButton("🧠 Bilik Oyunu",       callback_data="g_bilik"),
         InlineKeyboardButton("🚩 Bayraq Oyunu",     callback_data="g_bayraq")],
        [InlineKeyboardButton("🔗 Söz Zənciri",      callback_data="g_sozzenciri"),
         InlineKeyboardButton("🏛 Paytaxt Tapmaca",  callback_data="g_paytaxt")],
        [InlineKeyboardButton("🚗 Plaka Oyunu",       callback_data="g_plaka"),
         InlineKeyboardButton("π Pi Oyunu",           callback_data="g_pi")],
        [InlineKeyboardButton("⭕ XOX",               callback_data="g_xox"),
         InlineKeyboardButton("🎭 Doğru/Cəsarət",   callback_data="g_dogru")],
        [InlineKeyboardButton("🎮 Buton Oyunu",       callback_data="g_buton"),
         InlineKeyboardButton("⚡ Yaddaş Şimşəyi",  callback_data="g_yaddas")],
        [InlineKeyboardButton("🌡 İsti-Soyuq",       callback_data="g_istisoyuq"),
         InlineKeyboardButton("📚 Əsər-Müəllif",     callback_data="g_eser")],
    ])
    await message.reply_text(
        "🎮 **OYUN MENYUSU**\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Oynamaq istədiyiniz oyunu seçin:\n"
        "• Yazılı oyunlarda cavabı **yazırsınız**\n"
        "• Butonlu oyunlarda **düyməyə basırsınız**\n"
        "━━━━━━━━━━━━━━━━━━",
        reply_markup=keyboard
    )


# ============================================================
#  XAL SİSTEMİ
# ============================================================
def add_score(user_id, chat_id, points):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO scores (user_id, chat_id, score) VALUES (%s,%s,%s) "
            "ON CONFLICT (user_id, chat_id) DO UPDATE SET score = scores.score + %s",
            (user_id, chat_id, points, points)
        )
        conn.commit(); cur.close(); conn.close()
    except:
        pass

def get_score(user_id, chat_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT score FROM scores WHERE user_id=%s AND chat_id=%s", (user_id, chat_id))
        r = cur.fetchone(); cur.close(); conn.close()
        return r[0] if r else 0
    except:
        return 0


@Client.on_message(filters.command("xal"))
async def show_score(client, message):
    uid = message.from_user.id
    cid = message.chat.id
    score = get_score(uid, cid)
    await message.reply_text(
        f"🏆 **{message.from_user.first_name}** xalı:\n"
        f"📊 **{score}** xal"
    )


@Client.on_message(filters.command("dur"))
async def stop_game(client, message):
    cid = message.chat.id
    if cid in active_games:
        del active_games[cid]
        await message.reply_text("🛑 **Oyun dayandırıldı.**")
    else:
        await message.reply_text("Hal-hazırda aktiv oyun yoxdur.")


# ============================================================
#  OYUN 1: RƏQƏm TAPMACA (1-100, 7 cəhd)
# ============================================================
@Client.on_callback_query(filters.regex("^g_reqem$"))
async def start_reqem(client, cq: CallbackQuery):
    chat_id = cq.message.chat.id
    secret = random.randint(1, 100)
    active_games[chat_id] = {"type": "reqem", "secret": secret, "tries": 7}
    await cq.message.reply_text(
        "🎲 **Rəqəm Tapmaca Başladı!**\n\n"
        "1 ilə 100 arasında bir rəqəm seçdim.\n"
        "7 cəhdınız var. Rəqəmi yazın!"
    )
    await cq.answer()


# ============================================================
#  OYUN 2: İSTİ-SOYUQ (1-50)
# ============================================================
@Client.on_callback_query(filters.regex("^g_istisoyuq$"))
async def start_istisoyuq(client, cq: CallbackQuery):
    chat_id = cq.message.chat.id
    secret = random.randint(1, 50)
    active_games[chat_id] = {"type": "istisoyuq", "secret": secret}
    await cq.message.reply_text(
        "🌡 **İsti-Soyuq Oyunu Başladı!**\n\n"
        "1 ilə 50 arasında rəqəm tutdum.\n"
        "Rəqəm yazın — 🔥 İsti ya 🧊 Soyuq deyim!"
    )
    await cq.answer()


# ============================================================
#  OYUN 3: SÜRƏTLİ RİYAZİYYAT
# ============================================================
@Client.on_callback_query(filters.regex("^g_riyaziyyat$"))
async def start_riyaziyyat(client, cq: CallbackQuery):
    await ask_math(client, cq.message.chat.id)
    await cq.answer()

async def ask_math(client, chat_id):
    a, b = random.randint(1, 50), random.randint(1, 50)
    op = random.choice(["+", "-", "*"])
    ans = eval(f"{a}{op}{b}")
    active_games[chat_id] = {"type": "riyaziyyat", "answer": ans}
    await client.send_message(chat_id, f"⚡ **{a} {op} {b} = ?**\n\nCavabı yazın!")


# ============================================================
#  OYUN 4: XOX (Tic-Tac-Toe)
# ============================================================
def make_xox_board(board):
    rows = []
    for i in range(0, 9, 3):
        row = []
        for j in range(3):
            cell = board[i+j]
            row.append(InlineKeyboardButton(cell or "⬜", callback_data=f"xox_{i+j}"))
        rows.append(row)
    return InlineKeyboardMarkup(rows)

@Client.on_callback_query(filters.regex("^g_xox$"))
async def start_xox(client, cq: CallbackQuery):
    chat_id = cq.message.chat.id
    active_games[chat_id] = {
        "type": "xox",
        "board": [""] * 9,
        "turn": "❌",
        "player1": cq.from_user.id,
        "player2": None
    }
    await cq.message.reply_text(
        "⭕ **XOX Oyunu Başladı!**\n\n"
        f"👤 {cq.from_user.first_name} ❌ oyunçusudur.\n"
        "İkinci oyunçu lütfən aşağıdakı lövhəyə bassın!",
        reply_markup=make_xox_board([""] * 9)
    )
    await cq.answer()

@Client.on_callback_query(filters.regex(r"^xox_\d$"))
async def xox_move(client, cq: CallbackQuery):
    chat_id = cq.message.chat.id
    game = active_games.get(chat_id)
    if not game or game["type"] != "xox":
        return await cq.answer("Oyun yoxdur!", show_alert=True)
    idx = int(cq.data.split("_")[1])
    uid = cq.from_user.id
    board = game["board"]
    turn = game["turn"]

    if board[idx]:
        return await cq.answer("Bu xana dolu!", show_alert=True)

    # İkinci oyunçunu təyin et
    if game["player2"] is None and uid != game["player1"]:
        game["player2"] = uid

    # Növbə yoxlama
    if turn == "❌" and uid != game["player1"]:
        return await cq.answer("Sizin növbəniz deyil!", show_alert=True)
    if turn == "⭕" and uid != game.get("player2"):
        return await cq.answer("Sizin növbəniz deyil!", show_alert=True)

    board[idx] = turn

    # Qazanma yoxla
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a,b,c in wins:
        if board[a] == board[b] == board[c] == turn:
            del active_games[chat_id]
            await cq.message.edit_text(
                f"🏆 **{cq.from_user.first_name} QAZANDI!** {turn}\n\n"
                + "".join(board[i] or "⬜" for i in range(9)),
            )
            add_score(uid, chat_id, 25)
            return await cq.answer("Siz qazandınız! 🏆")

    if all(board):
        del active_games[chat_id]
        await cq.message.edit_text("🤝 **Heç-heçə!**")
        return await cq.answer("Heç-heçə!")

    game["turn"] = "⭕" if turn == "❌" else "❌"
    await cq.message.edit_reply_markup(make_xox_board(board))
    await cq.answer(f"Növbə: {game['turn']}")


# ============================================================
#  OYUN 5: BUTON OYUNU
# ============================================================
@Client.on_callback_query(filters.regex("^g_buton$"))
async def start_buton(client, cq: CallbackQuery):
    chat_id = cq.message.chat.id
    active_games[chat_id] = {"type": "buton", "round": 1, "scores": {}}
    await run_buton_round(client, chat_id)
    await cq.answer()

async def run_buton_round(client, chat_id):
    game = active_games.get(chat_id)
    if not game or game["type"] != "buton":
        return
    r = game["round"]
    if r > 8:
        scores = game["scores"]
        if scores:
            winner_id = max(scores, key=scores.get)
            winner_score = scores[winner_id]
            result = "\n".join(f"• `{uid}`: {s} xal" for uid, s in sorted(scores.items(), key=lambda x: -x[1]))
            try:
                winner = await client.get_users(winner_id)
                await client.send_message(chat_id,
                    f"🏆 **Oyun Bitdi!**\n\n{result}\n\n"
                    f"🥇 **Qalib: {winner.first_name}** ({winner_score} xal)!"
                )
                add_score(winner_id, chat_id, 20)
            except:
                pass
        del active_games[chat_id]
        return

    await asyncio.sleep(random.uniform(1, 4))
    game = active_games.get(chat_id)
    if not game:
        return
    game["round"] += 1
    game["clicked"] = False
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🟢 BAS!", callback_data=f"buton_click")]])
    await client.send_message(chat_id, f"⚡ **Tur {r}/8** — İlk basan qazanır!", reply_markup=keyboard)

@Client.on_callback_query(filters.regex("^buton_click$"))
async def buton_click(client, cq: CallbackQuery):
    chat_id = cq.message.chat.id
    game = active_games.get(chat_id)
    if not game or game["type"] != "buton":
        return await cq.answer("Oyun yoxdur!")
    if game.get("clicked"):
        return await cq.answer("Gecikdiniz! 😅")
    game["clicked"] = True
    uid = cq.from_user.id
    game["scores"][uid] = game["scores"].get(uid, 0) + 1
    await cq.message.edit_text(f"✅ **{cq.from_user.first_name} ilk oldu!** (+1 xal)")
    await cq.answer("Xal qazandınız! 🎉")
    await run_buton_round(client, chat_id)


# ============================================================
#  OYUN 6: YADDAŞ ŞİMŞƏYİ (Emoji ardıcıllığı)
# ============================================================
MEMORY_EMOJIS = ["🌈","🪐","🎡","🍭","💎","🔮","⚡","🔥","🚀","🛸","🎈","🎨"]

@Client.on_callback_query(filters.regex("^g_yaddas$"))
async def start_yaddas(client, cq: CallbackQuery):
    chat_id = cq.message.chat.id
    seq = [random.choice(MEMORY_EMOJIS) for _ in range(3)]
    active_games[chat_id] = {"type": "yaddas", "sequence": seq, "level": 3}
    msg = await cq.message.reply_text(f"⚡ **Yaddaş Şimşəyi!**\n\nBu ardıcıllığı yadda saxla:\n{''.join(seq)}")
    await asyncio.sleep(3)
    await msg.edit_text("❓ **Ardıcıllığı yazın!** (Emojiləri sırayla yazın)")
    await cq.answer()


# ============================================================
#  OYUN 7: DOĞRU/CƏSARƏt
# ============================================================
TRUTH_DARE = {
    "truth": [
        "Həyatındakı ən utanc verici anı danış.",
        "Qrupda kimsini bəyənirsən?",
        "Ən böyük sirrini paylaş.",
        "Nə vaxt yalan dedin?",
        "Ən qorxduğun şey nədir?",
    ],
    "dare": [
        "Qrupda kimisə tərif et.",
        "İngiliscə bir şey yaz.",
        "Emojilə hisslərini ifadə et.",
        "Sevimli mahnının adını yaz.",
        "Özün haqqında 3 maraqlı fakt yaz.",
    ]
}

@Client.on_callback_query(filters.regex("^g_dogru$"))
async def start_dogru(client, cq: CallbackQuery):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Doğru", callback_data="dd_truth"),
         InlineKeyboardButton("💪 Cəsarət", callback_data="dd_dare")]
    ])
    await cq.message.reply_text(
        "🎭 **Doğru/Cəsarət!**\n\nSeçim edin:",
        reply_markup=keyboard
    )
    await cq.answer()

@Client.on_callback_query(filters.regex("^dd_(truth|dare)$"))
async def dd_choice(client, cq: CallbackQuery):
    choice = cq.data.split("_")[1]
    text = random.choice(TRUTH_DARE[choice])
    await cq.message.edit_text(
        f"{'✅ Doğru' if choice == 'truth' else '💪 Cəsarət'}:\n\n**{text}**"
    )
    await cq.answer()


# ============================================================
#  OYUN 8: SÖZ ZƏNCİRİ
# ============================================================
@Client.on_callback_query(filters.regex("^g_sozzenciri$"))
async def start_sozzenciri(client, cq: CallbackQuery):
    chat_id = cq.message.chat.id
    active_games[chat_id] = {"type": "sozzenciri", "last_word": None, "used": []}
    await cq.message.reply_text(
        "🔗 **Söz Zənciri Başladı!**\n\n"
        "Qaydalar:\n"
        "• Hər söz əvvəlki sözün son hərfi ilə başlamalıdır\n"
        "• Eyni söz iki dəfə istifadə edilə bilməz\n"
        "• İlk sözü siz yazın!"
    )
    await cq.answer()


# ============================================================
#  ƏSAS MESAJ TUTUCUSU (Oyun cavabları)
# ============================================================
@Client.on_message(filters.group & filters.text & ~filters.command(""))
async def game_answer_handler(client, message):
    chat_id = message.chat.id
    game = active_games.get(chat_id)
    if not game:
        return

    text = message.text.strip()
    uid = message.from_user.id
    fname = message.from_user.first_name

    # RƏQƏM TAPMACA
    if game["type"] == "reqem":
        try:
            guess = int(text)
        except:
            return
        secret = game["secret"]
        tries = game["tries"] - 1
        game["tries"] = tries
        if guess == secret:
            del active_games[chat_id]
            add_score(uid, chat_id, 15)
            await message.reply_text(f"🎉 **{fname} tapdı!** Rəqəm **{secret}** idi! (+15 xal)")
        elif tries == 0:
            del active_games[chat_id]
            await message.reply_text(f"😔 Cəhd bitmişdir! Rəqəm **{secret}** idi.")
        elif guess < secret:
            await message.reply_text(f"📈 **Çox az!** {tries} cəhd qaldı.")
        else:
            await message.reply_text(f"📉 **Çox böyük!** {tries} cəhd qaldı.")

    # İSTİ-SOYUQ
    elif game["type"] == "istisoyuq":
        try:
            guess = int(text)
        except:
            return
        secret = game["secret"]
        diff = abs(guess - secret)
        if guess == secret:
            del active_games[chat_id]
            add_score(uid, chat_id, 10)
            await message.reply_text(f"🎯 **{fname} tapdı!** Rəqəm **{secret}** idi! (+10 xal)")
        elif diff <= 3:
            await message.reply_text("🔥🔥🔥 **Çox İSTİ!**")
        elif diff <= 7:
            await message.reply_text("🔥 **İsti!**")
        elif diff <= 15:
            await message.reply_text("🌤 **İlıq...**")
        elif diff <= 25:
            await message.reply_text("🧊 **Soyuq!**")
        else:
            await message.reply_text("🧊🧊🧊 **Çox SOYUQ!**")

    # RİYAZİYYAT
    elif game["type"] == "riyaziyyat":
        try:
            ans = int(text)
        except:
            return
        if ans == game["answer"]:
            add_score(uid, chat_id, 5)
            await message.reply_text(f"✅ **{fname} düz cavab verdi!** (+5 xal)")
            await ask_math(client, chat_id)
        else:
            await message.reply_text(f"❌ Yanlış! Siz **{ans}** yazdınız.")

    # YADDAŞ ŞİMŞƏYİ
    elif game["type"] == "yaddas":
        seq = game["sequence"]
        seq_str = "".join(seq)
        if text == seq_str:
            add_score(uid, chat_id, game["level"])
            new_level = game["level"] + 1
            new_seq = seq + [random.choice(MEMORY_EMOJIS)]
            game["sequence"] = new_seq
            game["level"] = new_level
            msg = await message.reply_text(f"✅ **Düzgün!** Növbəti ardıcıllıq:\n{''.join(new_seq)}")
            await asyncio.sleep(3)
            await msg.edit_text("❓ **Yenidən yazın!**")
        else:
            del active_games[chat_id]
            await message.reply_text(f"❌ **Yanlış!** Düzgün ardıcıllıq: {''.join(seq)}")

    # SÖZ ZƏNCİRİ
    elif game["type"] == "sozzenciri":
        word = text.lower().strip()
        last = game.get("last_word")
        used = game.get("used", [])

        if word in used:
            return await message.reply_text("❌ Bu söz artıq istifadə edilib!")
        if last and word[0] != last[-1]:
            return await message.reply_text(f"❌ Söz **'{last[-1]}'** hərfi ilə başlamalıdır!")

        game["last_word"] = word
        game["used"].append(word)
        add_score(uid, chat_id, 5)
        await message.reply_text(f"✅ **{word}** — növbəti söz **'{word[-1]}'** hərfi ilə başlamalıdır! (+5 xal)")


# ============================================================
#  Sadə oyunlar üçün placeholder-lər (callback)
# ============================================================
SIMPLE_GAMES = {
    "g_sozizahi": "🎯 Söz İzahı oyunu tezliklə əlavə ediləcək!",
    "g_bosluq": "📝 Boşluq Doldurma oyunu tezliklə əlavə ediləcək!",
    "g_wordle": "🔄 Söz Sarmalı oyunu tezliklə əlavə ediləcək!",
    "g_tapgorelim": "❓ Tap Görəlim oyunu tezliklə əlavə ediləcək!",
    "g_bilik": "🧠 Bilik Oyunu tezliklə əlavə ediləcək!",
    "g_bayraq": "🚩 Bayraq Oyunu tezliklə əlavə ediləcək!",
    "g_paytaxt": "🏛 Paytaxt Tapmaca tezliklə əlavə ediləcək!",
    "g_plaka": "🚗 Plaka Oyunu tezliklə əlavə ediləcək!",
    "g_pi": "π Pi Oyunu tezliklə əlavə ediləcək!",
    "g_eser": "📚 Əsər-Müəllif oyunu tezliklə əlavə ediləcək!",
}

@Client.on_callback_query(filters.regex("^g_(sozizahi|bosluq|wordle|tapgorelim|bilik|bayraq|paytaxt|plaka|pi|eser)$"))
async def simple_game_placeholder(client, cq: CallbackQuery):
    key = cq.data
    await cq.message.reply_text(SIMPLE_GAMES.get(key, "Tezliklə!"))
    await cq.answer()
