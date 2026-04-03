import os
import asyncio
from config import MONGO_DB_URI

# ── PostgreSQL (əsas bot üçün) ────────────────────────
def get_db():
    import psycopg2
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    if not DATABASE_URL:
        return None
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db()
    if not conn:
        print("⚠️ DATABASE_URL yoxdur, PostgreSQL skip edildi.")
        return
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS broadcast_list (chat_id BIGINT PRIMARY KEY)")
    cur.execute("CREATE TABLE IF NOT EXISTS qadaga_list (word TEXT PRIMARY KEY)")
    cur.execute("CREATE TABLE IF NOT EXISTS user_history (user_id BIGINT, old_name TEXT, old_username TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    cur.execute("CREATE TABLE IF NOT EXISTS user_stats (user_id BIGINT PRIMARY KEY, msg_count INT DEFAULT 0)")
    cur.execute("CREATE TABLE IF NOT EXISTS scores (user_id BIGINT, chat_id BIGINT, score INT DEFAULT 0, PRIMARY KEY (user_id, chat_id))")
    conn.commit()
    cur.close()
    conn.close()
    print("✅ PostgreSQL hazırdır!")

# ── MongoDB (musiqi botu üçün) ────────────────────────
mongo_client = None

async def init_mongo():
    global mongo_client
    if not MONGO_DB_URI:
        print("⚠️ MONGO_DB_URI yoxdur, MongoDB skip edildi.")
        return
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        mongo_client = AsyncIOMotorClient(MONGO_DB_URI)
        await mongo_client.admin.command('ping')
        print("✅ MongoDB hazırdır!")
    except Exception as e:
        print(f"❌ MongoDB xətası: {e}")

def get_mongo():
    return mongo_client

# ── Xal sistemi (PostgreSQL) ──────────────────────────
def add_score(user_id, chat_id, points):
    try:
        conn = get_db()
        if not conn: return
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO scores (user_id, chat_id, score) VALUES (%s,%s,%s) "
            "ON CONFLICT (user_id, chat_id) DO UPDATE SET score = scores.score + %s",
            (user_id, chat_id, points, points)
        )
        conn.commit(); cur.close(); conn.close()
    except: pass

def get_score(user_id, chat_id):
    try:
        conn = get_db()
        if not conn: return 0
        cur = conn.cursor()
        cur.execute("SELECT score FROM scores WHERE user_id=%s AND chat_id=%s", (user_id, chat_id))
        r = cur.fetchone(); cur.close(); conn.close()
        return r[0] if r else 0
    except: return 0
