import sqlite3

DB_PATH = "bot.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS warnings (
            user_id INTEGER,
            chat_id INTEGER,
            count INTEGER DEFAULT 0,
            reason TEXT DEFAULT '',
            PRIMARY KEY (user_id, chat_id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            chat_id INTEGER PRIMARY KEY,
            welcome_enabled INTEGER DEFAULT 1,
            antispam_enabled INTEGER DEFAULT 1,
            welcome_message TEXT DEFAULT 'Welcome, {user}!'
        )
    """)
    conn.commit()
    conn.close()


def get_warnings(user_id, chat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT count FROM warnings WHERE user_id = ? AND chat_id = ?", (user_id, chat_id))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0


def add_warning(user_id, chat_id, reason=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO warnings (user_id, chat_id, count, reason) VALUES (?, ?, 1, ?) "
              "ON CONFLICT(user_id, chat_id) DO UPDATE SET count = count + 1, reason = ?",
              (user_id, chat_id, reason, reason))
    conn.commit()
    count = get_warnings(user_id, chat_id)
    conn.close()
    return count


def reset_warnings(user_id, chat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM warnings WHERE user_id = ? AND chat_id = ?", (user_id, chat_id))
    conn.commit()
    conn.close()


def get_settings(chat_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM settings WHERE chat_id = ?", (chat_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"welcome_enabled": 1, "antispam_enabled": 1, "welcome_message": "Welcome, {user}!"}


def update_settings(chat_id, **kwargs):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for key, value in kwargs.items():
        c.execute(f"INSERT INTO settings (chat_id, {key}) VALUES (?, ?) "
                  f"ON CONFLICT(chat_id) DO UPDATE SET {key} = ?", (chat_id, value, value))
    conn.commit()
    conn.close()
