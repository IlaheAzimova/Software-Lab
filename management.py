
import flet as ft
import sqlite3
from datetime import date
DB_PATH = "students.db"

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
   
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id      TEXT PRIMARY KEY,
                name    TEXT NOT NULL,
                email   TEXT NOT NULL,
                program TEXT NOT NULL,
                status  TEXT NOT NULL DEFAULT 'Active',
                date    TEXT NOT NULL
            )
        """)
        if conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
            demo = [
                ("STU-1001", "Alice Thompson",  "alice@lumina.edu",  "Computer Science 101",  "Active",    "2023-09-15"),
                ("STU-1002", "Marcus Reed",     "marcus@lumina.edu", "Deep Learning Basics",  "Active",    "2023-10-02"),
                ("STU-1003", "Sophia Lane",     "sophia@lumina.edu", "Macroeconomics 101",    "Suspended", "2023-08-20"),
                ("STU-1004", "David Kim",       "david@lumina.edu",  "UI/UX Design Systems",  "Active",    "2023-11-12"),
                ("STU-1005", "Elena Morris",    "elena@lumina.edu",  "Mobile App Security",   "Active",    "2023-12-05"),
            ]
            conn.executemany(
                "INSERT INTO students VALUES (?,?,?,?,?,?)", demo
            )


def _db_load_all(query: str = "") -> list:
    
    q = f"%{query.lower()}%"
    with _get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM students
            WHERE LOWER(name)    LIKE ?
               OR LOWER(email)   LIKE ?
               OR LOWER(program) LIKE ?
            ORDER BY id
        """, (q, q, q)).fetchall()
    return [dict(r) for r in rows]


def _db_next_id() -> str:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM students ORDER BY id DESC LIMIT 1"
        ).fetchone()
    if row:
        num = int(row["id"].split("-")[1]) + 1
    else:
        num = 1001
    return f"STU-{num}"


def _db_insert(student: dict):
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO students VALUES (:id,:name,:email,:program,:status,:date)",
            student,
        )


def _db_update(student: dict):
    with _get_conn() as conn:
        conn.execute("""
            UPDATE students
               SET name=:name, email=:email, program=:program, status=:status
             WHERE id=:id
        """, student)


def _db_delete(student_id: str):
    with _get_conn() as conn:
        conn.execute("DELETE FROM students WHERE id=?", (student_id,))

_init_db()


def build_management_page(page: ft.Page, get_colors) -> ft.Column:

    def c():
        return get_colors()

    def status_chip(status: str) -> ft.Container:
        color = "#16a34a" if status == "Active" else "#dc2626"
        bg    = "#dcfce7" if status == "Active" else "#fee2e2"
        return ft.Container(
            content=ft.Text(status, size=11, weight=ft.FontWeight.BOLD, color=color),
            bgcolor=bg, border_radius=20,
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
        )

    def avatar(initials: str, size=34) -> ft.Container:
        return ft.Container(
            width=size, height=size, border_radius=size // 2,
            bgcolor="#0f766e22", alignment=ft.Alignment(0, 0),
            content=ft.Text(initials, size=size // 3 + 2,
                            weight=ft.FontWeight.BOLD, color="#0f766e"),
        )

    def field_label(text: str) -> ft.Text:
        return ft.Text(text, size=13, weight=ft.FontWeight.BOLD, color=c()["text"])

    def make_textfield(hint: str) -> ft.TextField:
        return ft.TextField(
            hint_text=hint, border_radius=8, height=42,
            filled=True, bgcolor="#f9fafb", border_color="#e5e7eb",
        )


    active_tab  = {"index": 0}
    TABS        = ["Manage Students", "Manage Courses", "Issue Certificates", "Verify Completion"]
    tab_refs    = [ft.Ref[ft.Container]() for _ in TABS]


    student_list_col = ft.Ref[ft.Column]()
    filter_value     = {"text": ""}


    def close_any_dialog(e=None):
       
        for ctrl in page.overlay:
            if isinstance(ctrl, ft.AlertDialog):
                ctrl.open = False
        page.update()

   
    # yeni telebe burdan elvae edirik  
    add_name    = make_textfield("e.g. Jane Doe")
    add_email   = make_textfield("jane@example.com")
    add_program = make_textfield("Computer Science 101")
    add_error   = ft.Text("", color="#dc2626", size=11, visible=False)

    def _add_header_row() -> ft.Row:
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column([
                    ft.Text("Add New Student", size=17,
                            weight=ft.FontWeight.BOLD, color=c()["text"]),
                    ft.Text("Create a new student account.\nThey will receive an email invitation.",
                            size=11, color=c()["muted"]),
                ], spacing=2),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color=c()["muted"],
                    icon_size=18,
                    on_click=close_any_dialog,
                ),
            ]
        )

    def _create_student(e):
        name    = add_name.value.strip()
        email   = add_email.value.strip()
        program = add_program.value.strip()
        if not name or not email or not program:
            add_error.value   = "Zəhmət olmasa bütün xanaları doldurun."
            add_error.visible = True
            page.update()
            return
        new_student = {
            "id":      _db_next_id(),
            "name":    name,
            "email":   email,
            "program": program,
            "status":  "Active",
            "date":    str(date.today()),
        }
        _db_insert(new_student)          # ✅ DB-yə yazılır
        close_any_dialog()
        _refresh_list()

    def open_add_dialog(e=None):
        add_name.value = add_email.value = add_program.value = ""
        add_error.visible = False

        dlg = ft.AlertDialog(
            modal=True,
            bgcolor=c()["card"],
            shape=ft.RoundedRectangleBorder(radius=12),
            actions=[],
            content=ft.Container(
                width=380,
                content=ft.Column([
                    _add_header_row(),
                    ft.Divider(height=16, color=c()["border"]),
                    ft.Column([field_label("Full Name"),       add_name],    spacing=6),
                    ft.Column([field_label("Email Address"),   add_email],   spacing=6),
                    ft.Column([field_label("Initial Program"), add_program], spacing=6),
                    add_error,
                    ft.Divider(height=16, color=c()["border"]),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        spacing=10,
                        controls=[
                            ft.OutlinedButton(
                                "Cancel",
                                style=ft.ButtonStyle(
                                    color=c()["muted"],
                                    side=ft.BorderSide(1, c()["border"]),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                on_click=close_any_dialog,
                            ),
                            ft.ElevatedButton(
                                "Create Account",
                                style=ft.ButtonStyle(
                                    bgcolor="#0f766e", color="white",
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                on_click=_create_student,
                            ),
                        ],
                    ),
                ], spacing=12, tight=True),
            ),
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    
    def open_delete_dialog(student: dict):
        def _confirm_delete(e):
            _db_delete(student["id"])   
            close_any_dialog()
            _refresh_list()

        dlg = ft.AlertDialog(
            modal=True,
            bgcolor=c()["card"],
            shape=ft.RoundedRectangleBorder(radius=12),
            actions=[],
            content=ft.Container(
                width=340,
                content=ft.Column([
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Delete Student", size=17,
                                    weight=ft.FontWeight.BOLD, color=c()["text"]),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_color=c()["muted"],
                                icon_size=18,
                                on_click=close_any_dialog,
                            ),
                        ]
                    ),
                    ft.Divider(height=12, color=c()["border"]),
                    ft.Text(
                        f"«{student['name']}» can you sure to delete this student?\n"
                        "This action cannot be undone.",
                        size=13, color=c()["muted"],
                    ),
                    ft.Divider(height=12, color=c()["border"]),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        spacing=10,
                        controls=[
                            ft.OutlinedButton(
                                "Cancel",
                                style=ft.ButtonStyle(
                                    color=c()["muted"],
                                    side=ft.BorderSide(1, c()["border"]),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                on_click=close_any_dialog,
                            ),
                            ft.ElevatedButton(
                                "Delete",
                                style=ft.ButtonStyle(
                                    bgcolor="#dc2626", color="white",
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                on_click=_confirm_delete,
                            ),
                        ],
                    ),
                ], spacing=12, tight=True),
            ),
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    
    # edit edirik
 
    def open_edit_dialog(student: dict):
        edit_name    = make_textfield("Name Surname")
        edit_email   = make_textfield("email@example.com")
        edit_program = make_textfield("Program Name")
        edit_status  = ft.Dropdown(
            value=student["status"],
            options=[
                ft.dropdown.Option("Active"),
                ft.dropdown.Option("Suspended"),
            ],
            border_radius=8, height=42, filled=True,
            bgcolor="#f9fafb", border_color="#e5e7eb",
        )
        edit_error = ft.Text("", color="#dc2626", size=11, visible=False)

        edit_name.value    = student["name"]
        edit_email.value   = student["email"]
        edit_program.value = student["program"]

        def _save_edit(e):
            name    = edit_name.value.strip()
            email   = edit_email.value.strip()
            program = edit_program.value.strip()
            if not name or not email or not program:
                edit_error.value   = "Please fill out all fields."
                edit_error.visible = True
                page.update()
                return
            updated = {
                "id":      student["id"],
                "name":    name,
                "email":   email,
                "program": program,
                "status":  edit_status.value,
            }
            _db_update(updated)        
            close_any_dialog()
            _refresh_list()

        dlg = ft.AlertDialog(
            modal=True,
            bgcolor=c()["card"],
            shape=ft.RoundedRectangleBorder(radius=12),
            actions=[],
            content=ft.Container(
                width=380,
                content=ft.Column([
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column([
                                ft.Text("Edit Student", size=17,
                                        weight=ft.FontWeight.BOLD, color=c()["text"]),
                                ft.Text(f"ID: {student['id']}",
                                        size=11, color=c()["muted"]),
                            ], spacing=2),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_color=c()["muted"],
                                icon_size=18,
                                on_click=close_any_dialog,
                            ),
                        ]
                    ),
                    ft.Divider(height=16, color=c()["border"]),
                    ft.Column([field_label("Name Surname"),         edit_name],    spacing=6),
                    ft.Column([field_label("Email Address"),    edit_email],   spacing=6),
                    ft.Column([field_label("Program Name"),          edit_program], spacing=6),
                    ft.Column([field_label("Status"),           edit_status],  spacing=6),
                    edit_error,
                    ft.Divider(height=16, color=c()["border"]),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        spacing=10,
                        controls=[
                            ft.OutlinedButton(
                                "Cancel",
                                style=ft.ButtonStyle(
                                    color=c()["muted"],
                                    side=ft.BorderSide(1, c()["border"]),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                on_click=close_any_dialog,
                            ),
                            ft.ElevatedButton(
                                "Save",
                                style=ft.ButtonStyle(
                                    bgcolor="#0f766e", color="white",
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                on_click=_save_edit,
                            ),
                        ],
                    ),
                ], spacing=12, tight=True),
            ),
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

   
    def student_row(s: dict) -> ft.Container:
        initials = "".join(w[0] for w in s["name"].split()[:2]).upper()
        return ft.Container(
            padding=ft.padding.symmetric(vertical=10, horizontal=8),
            border=ft.border.only(bottom=ft.BorderSide(1, c()["border"])),
            content=ft.Row(controls=[
                ft.Text(s["id"],      expand=2, size=12, color=c()["muted"]),
                ft.Row(expand=3, controls=[
                    avatar(initials),
                    ft.Column([
                        ft.Text(s["name"],  size=13,
                                weight=ft.FontWeight.W_600, color=c()["text"]),
                        ft.Text(s["email"], size=11, color=c()["muted"]),
                    ], spacing=1),
                ], spacing=10),
                ft.Text(s["program"], expand=3, size=12, color=c()["muted"]),
                ft.Container(expand=2, content=status_chip(s["status"])),
                ft.Text(s["date"],    expand=2, size=12, color=c()["muted"]),

                # ── Actions: Edit + Delete ────────────────────────────────
                ft.Row(expand=1, spacing=0, controls=[
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        icon_color="#0f766e",
                        icon_size=16,
                        tooltip="Edit",
                        on_click=lambda e, st=s: open_edit_dialog(st),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                        icon_color="#dc2626",
                        icon_size=16,
                        tooltip="Delete",
                        on_click=lambda e, st=s: open_delete_dialog(st),
                    ),
                ]),
            ])
        )

    #
    # siyahini db dan oxuyur

    def _refresh_list():
        students = _db_load_all(filter_value["text"])   
        student_list_col.current.controls = [student_row(s) for s in students]
        page.update()

    def _on_filter_change(e):
        filter_value["text"] = e.control.value
        _refresh_list()

  
    def _make_tab(i: int, label_text: str) -> ft.Container:
        is_active = (i == active_tab["index"])
        return ft.Container(
            ref=tab_refs[i],
            padding=ft.padding.only(bottom=10, right=20),
            border=ft.border.only(
                bottom=ft.BorderSide(2, "#0f766e" if is_active else "transparent")
            ),
            content=ft.Text(
                label_text, size=13,
                weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.NORMAL,
                color="#0f766e" if is_active else c()["muted"],
            ),
            on_click=lambda e, idx=i: _switch_tab(idx),
        )

    tab_row = ft.Row(controls=[_make_tab(i, t) for i, t in enumerate(TABS)])

    def _switch_tab(idx: int):
        active_tab["index"] = idx
        tab_row.controls = [_make_tab(i, t) for i, t in enumerate(TABS)]
        page.update()


    header_row = ft.Container(
        padding=ft.padding.symmetric(vertical=10, horizontal=8),
        bgcolor=c()["field_bg"],
        border_radius=ft.BorderRadius(top_left=8, top_right=8,
                                      bottom_left=0, bottom_right=0),
        content=ft.Row(controls=[
            ft.Text("Student ID",      expand=2, size=11,
                    weight=ft.FontWeight.BOLD, color=c()["muted"]),
            ft.Text("Full Name",       expand=3, size=11,
                    weight=ft.FontWeight.BOLD, color=c()["muted"]),
            ft.Text("Program",         expand=3, size=11,
                    weight=ft.FontWeight.BOLD, color=c()["muted"]),
            ft.Text("Status",          expand=2, size=11,
                    weight=ft.FontWeight.BOLD, color=c()["muted"]),
            ft.Text("Enrollment Date", expand=2, size=11,
                    weight=ft.FontWeight.BOLD, color=c()["muted"]),
            ft.Text("Actions",         expand=1, size=11,
                    weight=ft.FontWeight.BOLD, color=c()["muted"]),
        ])
    )

    students_col = ft.Column(
        ref=student_list_col,
        controls=[student_row(s) for s in _db_load_all()],   
        spacing=0,
    )

    table_card = ft.Container(
        bgcolor=c()["card"], border_radius=12,
        shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK12),
        padding=0,
        content=ft.Column([
            ft.Container(
                padding=20,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.TextField(
                            hint_text="Filter students...",
                            prefix_icon=ft.Icons.SEARCH,
                            border_radius=8, height=38, filled=True,
                            bgcolor=c()["field_bg"],
                            border_color=c()["border"],
                            width=260,
                            on_change=_on_filter_change,
                        ),
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.PERSON_ADD_ALT_1_ROUNDED,
                                        color="white", size=16),
                                ft.Text("Add New Student", color="white",
                                        size=13, weight=ft.FontWeight.W_600),
                            ], spacing=8),
                            style=ft.ButtonStyle(
                                bgcolor="#0f766e",
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                            ),
                            on_click=open_add_dialog,
                        ),
                    ]
                )
            ),
            header_row,
            ft.Container(content=students_col),
            ft.Container(
                padding=ft.padding.symmetric(horizontal=20, vertical=14),
                border=ft.border.only(top=ft.BorderSide(1, c()["border"])),
                content=ft.Row([
                    ft.Container(
                        bgcolor="#f0fdf9", border_radius=8, padding=10,
                        content=ft.Icon(ft.Icons.VERIFIED_OUTLINED,
                                        color="#0f766e", size=20),
                    ),
                    ft.Column([
                        ft.Text("System Health: Optimal", size=13,
                                weight=ft.FontWeight.BOLD, color=c()["text"]),
                        ft.Text("All background processes for student credentialing are active.",
                                size=11, color=c()["muted"]),
                    ], spacing=2),
                ], spacing=12)
            ),
        ], spacing=0)
    )

    return ft.Column(
        scroll=ft.ScrollMode.AUTO, spacing=20,
        controls=[
            ft.Column([
                ft.Text("Admin Management", size=24,
                        weight=ft.FontWeight.BOLD, color=c()["text"]),
                ft.Text("Configure users, curriculum, and credentialing pipelines.",
                        size=13, color=c()["muted"]),
            ], spacing=2),
            tab_row,
            ft.Divider(height=1, color=c()["border"]),
            table_card,
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("© 2026 E-Learning Progress Analytics. All rights reserved.",
                            size=11, color=c()["muted"]),
                    ft.Row([
                        ft.TextButton("Privacy Policy",
                                      style=ft.ButtonStyle(color=c()["muted"])),
                        ft.TextButton("Support",
                                      style=ft.ButtonStyle(color=c()["muted"])),
                    ])
                ]
            )
        ]
    )