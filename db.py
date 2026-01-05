import sqlite3

DB_PATH = "users.db"

def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            plan TEXT,
            datejoin TEXT,
            lastpayment TEXT
        )
    """)
    conn.commit()
    conn.close()
