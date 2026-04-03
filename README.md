# 🤖 HT Universal Bot v2

Bütün botlar + Səsli Söhbət Musiqi — bir botda!

## 📦 Funksiyalar

| Modul | Funksiyalar |
|-------|------------|
| 🏷 Tağ | `/tag` `/utag` `/flagtag` `/tektag` |
| 🎮 Oyunlar | 8 oyun, `/menu` |
| 🎵 Downloader | YouTube, TikTok, Instagram, 1000+ sayt |
| 🎧 Səsli Söhbət | `/play` `/pause` `/skip` `/stop` `/queue` |
| 🛡 Moderator | Link, stiker, söyüş filtri |
| 🤖 AI (Nunu) | OpenAI ilə Azərbaycan dilində chatbot |
| 🔧 Əlavə | Sevgi, slap, font, maşınlar, namaz... |

---

## 🚀 Heroku Deploy

```bash
heroku create bot-adın
git init && git add . && git commit -m "init"
heroku git:remote -a bot-adın
git push heroku main
heroku ps:scale worker=1
```

### Postgres əlavə et:
```bash
heroku addons:create heroku-postgresql:mini
```

---

## ⚙️ Config Vars (Heroku → Settings → Config Vars)

| Dəyişən | Nümunə | Vacib? |
|---------|--------|--------|
| `BOT_TOKEN` | `123456:ABC...` | ✅ |
| `API_ID` | `12345678` | ✅ |
| `API_HASH` | `abcdef123` | ✅ |
| `DATABASE_URL` | Heroku Postgres avtomatik | ✅ |
| `OWNER_ID` | `123456789` | ✅ |
| `OWNER_IDS` | `123456789,987654321` | ✅ |
| `OWNER_LINK` | `https://t.me/username` | ✅ |
| `CHANNEL_LINK` | `https://t.me/kanal` | ✅ |
| `SUPPORT_CHAT` | `https://t.me/qrup` | ✅ |
| `STRING_SESSION` | `BQA...` | 🎧 Musiqi üçün |
| `OPENAI_API_KEY` | `sk-...` | 🤖 AI üçün |
| `COOKIE_URL` | `https://batbin.me/...` | 🎵 YouTube üçün |
| `START_PIC` | `https://i.postimg.cc/...` | ⭕ |
| `MONGO_DB_URI` | `mongodb+srv://...` | ⭕ |

---

## 🎧 STRING_SESSION Necə Alınır?

1. Telegram-da **@StringFatherBot**-a yazın
2. `/generate` göndərin
3. `Pyrogram v2` seçin
4. Telefon nömrənizi verin
5. Gələn kodu daxil edin
6. Alınan uzun mətni `STRING_SESSION`-a yapışdırın

> ⚠️ **Önemli:** Bu sizin real Telegram hesabınızın sessiyadır. Heç kimlə paylaşmayın!

---

## 🎵 Musiqi Komandaları

```
/play [ad/link]    — Səsli söhbətdə musiqi oxut
/vplay [ad/link]   — Video stream
/pause             — Fasilə ver
/resume            — Davam et
/skip              — Növbəti mahnı
/stop              — Dayandır + çıx
/queue             — Növbə siyahısı
/volume [1-200]    — Səs səviyyəsi
/np                — İndi oxunan
```

---

## 📋 Bütün Komandalar

```
🏷 TAĞ:
/tag /utag /flagtag /tektag /tagstop

🎮 OYUNLAR:
/menu /xal /dur

🎵 DOWNLOADER:
/youtube [ad]  •  link göndər

🛡 MODERATOR:
/stiker /seslimesaj /link /icaze /qadaga

🤖 AI:
/chatbot on/off

🔧 DİGƏR:
/help /id /info /ping /hava /valyuta
/namaz /wiki /tercume /sevgi /slap
/zeka /sans /masinlar /font /etiraf

👑 SAHİBİ:
/yonlendir /pissozplus /deleteqeyd /pisseyler /mesajisil
```
