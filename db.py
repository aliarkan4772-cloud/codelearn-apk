import sqlite3, hashlib, json

def get_conn():
    conn = sqlite3.connect("codelearn_pro.db")
    conn.row_factory = sqlite3.Row
    return conn

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def auth_user(username, password, is_register=False):
    conn = get_conn(); c = conn.cursor()
    if is_register:
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_pw(password)))
            conn.commit()
        except: return {"ok": False, "msg": "نام کاربری تکراری است."}
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_pw(password)))
    row = c.fetchone(); conn.close()
    if not row: return {"ok": False, "msg": "نام کاربری یا رمز اشتباه است."}
    return {"ok": True, "user": {"username": row["username"], "xp": row["xp"], "is_premium": bool(row["is_premium"]), "is_admin": bool(row["is_admin"]), "completed": json.loads(row["completed"]), "last_daily": row["last_daily"]}}

def init_db():
    conn = get_conn(); c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, xp INTEGER DEFAULT 0, is_premium INTEGER DEFAULT 0, is_admin INTEGER DEFAULT 0, completed TEXT DEFAULT '[]', last_daily TEXT DEFAULT '')")
    c.execute("CREATE TABLE IF NOT EXISTS lessons (id INTEGER PRIMARY KEY, title TEXT, desc TEXT, starter TEXT, expected TEXT, stdin TEXT, hint TEXT, is_free INTEGER DEFAULT 1)")
    c.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password, is_premium, is_admin) VALUES (?, ?, 1, 1)", ("admin", hash_pw("1234")))
    conn.commit(); conn.close()

init_db()
print("✅ دیتابیس با موفقیت ساخته شد.")
