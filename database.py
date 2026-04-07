import sqlite3
import hashlib
import os

DB_PATH = "lumina.db"


def _hash(password: str) -> str:
    """SHA-256 ilə şifrəni hash edir."""
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
 
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT    UNIQUE NOT NULL,
            name  TEXT    NOT NULL,
            pass  TEXT    NOT NULL
        )
    """)
   
    con.commit()
    con.close()


def user_exists(email: str) -> bool:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT 1 FROM users WHERE email=?", (email.strip().lower(),))
    result = cur.fetchone()
    con.close()
    return result is not None


def check_credentials(email: str, password: str) -> dict | None:
   
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "SELECT id, email, name FROM users WHERE email=? AND pass=?",
        (email.strip().lower(), _hash(password))
    )
    row = cur.fetchone()
    con.close()
    if row:
        return {"id": row[0], "email": row[1], "name": row[2]}
    return None


def register_user(email: str, name: str, password: str) -> tuple[bool, str]:
 
    if user_exists(email):
        return False, "Bu e-mail artıq qeydiyyatdan keçib"
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users (email, name, pass) VALUES (?,?,?)",
            (email.strip().lower(), name.strip(), _hash(password))
        )
        con.commit()
        con.close()
        return True, ""
    except Exception as ex:
        return False, str(ex)