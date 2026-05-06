"""
routers/students.py — Students CRUD endpoints.
"""
import sqlite3

from fastapi import APIRouter
from pydantic import BaseModel

from ._shared import get_connection, fail, ok

router = APIRouter(prefix="/students", tags=["students"])


def init_table():
    conn = get_connection()
    try:
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


init_table()


class Student(BaseModel):
    id:      str
    name:    str
    email:   str
    program: str
    status:  str


class StudentUpdate(BaseModel):
    name:    str
    email:   str
    program: str
    status:  str


@router.get("")
def list_students():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM students ORDER BY id").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.post("")
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

    ok("STUDENT ADDED", item.id, item.name)
    return {"message": "Student added successfully", "item": item}


@router.put("/{student_id}")
def update_student(student_id: str, item: StudentUpdate):
    if not item.name.strip():
        fail(400, "Name cannot be empty")

    conn = get_connection()
    try:
        cur = conn.execute(
            "UPDATE students SET name=?, email=?, program=?, status=? WHERE id=?",
            (item.name, item.email, item.program, item.status, student_id),
        )
        conn.commit()
        rowcount = cur.rowcount
    finally:
        conn.close()

    if rowcount == 0:
        fail(404, f"Student '{student_id}' not found")

    ok("STUDENT UPDATED", student_id, item.name)
    return {"message": "Student updated successfully",
            "item": {"id": student_id, **item.model_dump()}}


@router.delete("/{student_id}")
def delete_student(student_id: str):
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM students WHERE id=?", (student_id,))
        conn.commit()
        rowcount = cur.rowcount
    finally:
        conn.close()

    if rowcount == 0:
        fail(404, f"Student '{student_id}' not found")

    ok("STUDENT DELETED", student_id)
    return {"message": "Student deleted successfully", "id": student_id}