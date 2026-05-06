import sqlite3
import hashlib

DB_PATH = "elearning.db"

VALID_ROLES = ("Student", "Instructor", "Admin")


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    """Create users table if it does not exist, and migrate older copies that
    pre-date the `role` column."""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT    UNIQUE NOT NULL,
            name  TEXT    NOT NULL,
            pass  TEXT    NOT NULL,
            role  TEXT    NOT NULL DEFAULT 'Student'
        )
    """)
    # Migration: add `role` column to old DBs that don't have it yet.
    cols = {row[1] for row in cur.execute("PRAGMA table_info(users)")}
    if "role" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'Student'")
    con.commit()
    con.close()


def user_exists(email: str) -> bool:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT 1 FROM users WHERE email=?", (email.strip().lower(),))
    result = cur.fetchone()
    con.close()
    return result is not None


def check_credentials(email: str, password: str):
    """Return user dict (with role) if credentials match, otherwise None."""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "SELECT id, email, name, role FROM users WHERE email=? AND pass=?",
        (email.strip().lower(), _hash(password))
    )
    row = cur.fetchone()
    con.close()
    if row:
        return {"id": row[0], "email": row[1], "name": row[2], "role": row[3]}
    return None


def register_user(email: str, name: str, password: str, role: str = "Student"):
    """Returns (success, error_message)."""
    if role not in VALID_ROLES:
        return False, f"Invalid role: {role}"
    if user_exists(email):
        return False, "This e-mail is already registered"
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users (email, name, pass, role) VALUES (?,?,?,?)",
            (email.strip().lower(), name.strip(), _hash(password), role)
        )
        con.commit()
        con.close()
        return True, ""
    except Exception as ex:
        return False, str(ex)