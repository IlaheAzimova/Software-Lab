
import hashlib
import sqlite3
import sys

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="E-Learning Progress Analytics API")

DB_NAME = "elearning.db"


def log_line(text: str):
    """Print line so it always reaches the terminal (buffer-safe)."""
    print(text, flush=True)
    sys.stdout.flush()


# ── Banner so it's obvious which version is running ─────
print("\n" + "=" * 60, flush=True)
print(" E-Learning API server starting (validation logging ON)", flush=True)
print("=" * 60 + "\n", flush=True)


# ── Database helpers ─────────────────────────────────────
def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False, timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=3000")
    return conn


def _hash(password: str) -> str:
    """Same hash database.py uses, so existing users can still log in."""
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT    UNIQUE NOT NULL,
                name  TEXT    NOT NULL,
                pass  TEXT    NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id       TEXT PRIMARY KEY,
                title    TEXT NOT NULL,
                category TEXT NOT NULL,
                level    TEXT NOT NULL,
                status   TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS certificates (
                id      TEXT PRIMARY KEY,
                student TEXT NOT NULL,
                course  TEXT NOT NULL,
                code    TEXT NOT NULL,
                status  TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id      TEXT PRIMARY KEY,
                name    TEXT NOT NULL,
                email   TEXT NOT NULL,
                program TEXT NOT NULL,
                status  TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


init_db()


# ── Pydantic models ──────────────────────────────────────
class LoginRequest(BaseModel):
    email:    str
    password: str


class RegisterRequest(BaseModel):
    email:    str
    name:     str
    password: str


class Lesson(BaseModel):
    id:       str
    title:    str
    category: str
    level:    str
    status:   str


class Certificate(BaseModel):
    id:      str
    student: str
    course:  str
    code:    str
    status:  str


class Student(BaseModel):
    id:      str
    name:    str
    email:   str
    program: str
    status:  str


# Tiny helper that prints the error AND raises HTTPException so uvicorn
# logs the proper 4xx status line.
def fail(status: int, message: str):
    log_line("")
    log_line("=" * 60)
    log_line(f"❌  VALIDATION ERROR {status}: {message}")
    log_line("=" * 60)
    raise HTTPException(status_code=status, detail=message)


# ── Auth endpoints ───────────────────────────────────────
@app.post("/login")
def login(req: LoginRequest):
    if not req.email.strip() or not req.password:
        fail(400, "Email and password are required")

    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, email, name FROM users WHERE email=? AND pass=?",
            (req.email.strip().lower(), _hash(req.password))
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        fail(401, f"Invalid credentials for {req.email}")

    log_line(f"✅  LOGIN OK: {row['email']} ({row['name']})")
    return {
        "message": "Login successful",
        "user": {"id": row["id"], "email": row["email"], "name": row["name"]},
    }


@app.post("/register")
def register(req: RegisterRequest):
    email = req.email.strip().lower()
    name  = req.name.strip()

    if not email or not name or not req.password:
        fail(400, "Email, name, and password are required")
    if "@" not in email or "." not in email:
        fail(400, f"Invalid email format: {email}")
    if len(req.password) < 6:
        fail(400, "Password must be at least 6 characters")

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (email, name, pass) VALUES (?, ?, ?)",
            (email, name, _hash(req.password)),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        fail(409, f"E-mail already registered: {email}")
    finally:
        conn.close()

    log_line(f"✅  REGISTER OK: {email} ({name})")
    return {"message": "Registration successful",
            "user": {"email": email, "name": name}}


# ── Lessons endpoints ────────────────────────────────────
@app.get("/lessons")
def get_lessons():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM lessons ORDER BY id").fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


@app.post("/lessons")
def add_lesson(item: Lesson):
    if not item.id.strip() or not item.title.strip():
        fail(400, "Lesson id and title are required")

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO lessons (id, title, category, level, status) "
            "VALUES (?, ?, ?, ?, ?)",
            (item.id, item.title, item.category, item.level, item.status),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        fail(409, f"Lesson ID '{item.id}' already exists")
    finally:
        conn.close()

    log_line(f"✅  LESSON ADDED: {item.id} – {item.title}")
    return {"message": "Lesson added successfully", "item": item}


# ── Certificates endpoints ───────────────────────────────
@app.get("/certificates")
def get_certificates():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM certificates ORDER BY id").fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


@app.post("/certificates")
def add_certificate(item: Certificate):
    if not item.id.strip() or not item.student.strip():
        fail(400, "Certificate id and student name are required")

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO certificates (id, student, course, code, status) "
            "VALUES (?, ?, ?, ?, ?)",
            (item.id, item.student, item.course, item.code, item.status),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        fail(409, f"Certificate ID '{item.id}' already exists")
    finally:
        conn.close()

    log_line(f"✅  CERT ISSUED: {item.id} – {item.student}")
    return {"message": "Certificate issued successfully", "item": item}


# ── Students endpoints 
@app.get("/students")
def get_students():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM students ORDER BY id").fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


@app.post("/students")
def add_student(item: Student):
    if not item.id.strip() or not item.name.strip():
        fail(400, "Student id and name are required")

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO students (id, name, email, program, status) "
            "VALUES (?, ?, ?, ?, ?)",
            (item.id, item.name, item.email, item.program, item.status),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        fail(409, f"Student ID '{item.id}' already exists")
    finally:
        conn.close()

    log_line(f"✅  STUDENT ADDED: {item.id} – {item.name}")
    return {"message": "Student added successfully", "item": item}

@app.get("/")
def root():
    return {
        "name":      "E-Learning Progress Analytics API",
        "endpoints": [
            "POST /login", "POST /register",
            "GET/POST /lessons",
            "GET/POST /certificates",
            "GET/POST /students",
        ],
        "docs":      "/docs",
    }