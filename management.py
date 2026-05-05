
import flet as ft
import requests

from theme import PRIMARY, PRIMARY_BG
from ui_widgets import colored_chip, page_footer

# Bridge to certificates module so "Issue Certificates" actually inserts
# certificates that show up on the Certificates page.
from certificates import _CERTS, _next_cert_id

API_URL = "http://127.0.0.1:8000"


_STUDENTS = [
    {"id": "STU-1001", "name": "Alice Thompson",  "email": "alice@elearning.edu",
     "program": "Computer Science 101", "status": "Active",    "date": "2023-09-15"},
    {"id": "STU-1002", "name": "Marcus Reed",     "email": "marcus@elearning.edu",
     "program": "Deep Learning Basics", "status": "Active",    "date": "2023-10-02"},
    {"id": "STU-1003", "name": "Sophia Lane",     "email": "sophia@elearning.edu",
     "program": "Macroeconomics 101",   "status": "Suspended", "date": "2023-08-20"},
    {"id": "STU-1004", "name": "David Kim",       "email": "david@elearning.edu",
     "program": "UI/UX Design Systems", "status": "Active",    "date": "2023-11-12"},
    {"id": "STU-1005", "name": "Elena Morris",    "email": "elena@elearning.edu",
     "program": "Mobile App Security",  "status": "Active",    "date": "2023-12-05"},
]

_COURSES = [
    {"id": "C-101", "title": "Computer Science 101",   "instructor": "Dr. Aisha Khan",     "students": 312, "status": "Active"},
    {"id": "C-202", "title": "Deep Learning Basics",   "instructor": "Prof. Liam Chen",    "students": 187, "status": "Active"},
    {"id": "C-303", "title": "Macroeconomics 101",     "instructor": "Dr. Maria Lopez",    "students": 142, "status": "Active"},
    {"id": "C-404", "title": "UI/UX Design Systems",   "instructor": "Prof. Daniel Park",  "students":  98, "status": "Active"},
    {"id": "C-505", "title": "Mobile App Security",    "instructor": "Dr. Reza Hosseini",  "students":  76, "status": "Archived"},
]

# Pending completions awaiting admin verification.
_PENDING_COMPLETIONS = [
    {"id": "P-9001", "student": "Hannah Wei",     "course": "Advanced React Patterns",  "score": 88, "submitted": "Today"},
    {"id": "P-9002", "student": "Tomas Reyes",    "course": "Mobile App Security",      "score": 92, "submitted": "Today"},
    {"id": "P-9003", "student": "Priya Anand",    "course": "Macroeconomics 101",       "score": 71, "submitted": "Yesterday"},
    {"id": "P-9004", "student": "Felix Brennan",  "course": "Deep Learning Basics",     "score": 84, "submitted": "Yesterday"},
]


_TAB_NAMES = ["Manage Students", "Manage Courses", "Issue Certificates", "Verify Completion"]


def _toast(page: ft.Page, msg: str, color: str = PRIMARY):
    page.show_dialog(ft.SnackBar(content=ft.Text(msg, color="white"), bgcolor=color))


def _next_student_id() -> str:
    nums = [int(s["id"].split("-")[1]) for s in _STUDENTS if s["id"].startswith("STU-")]
    return f"STU-{(max(nums) + 1) if nums else 1001}"


def _next_course_id() -> str:
    nums = [int(c["id"].split("-")[1]) for c in _COURSES if c["id"].startswith("C-")]
    return f"C-{(max(nums) + 1) if nums else 101}"


def build_management_page(page: ft.Page, c) -> ft.Control:
    state = {"tab": "Manage Students", "stu_query": "", "crs_query": ""}

    header = ft.Column(spacing=2, controls=[
        ft.Text("Admin Management", size=24,
                weight=ft.FontWeight.BOLD, color=c()["text"]),
        ft.Text("Configure users, curriculum, and credentialing pipelines.",
                size=13, color=c()["muted"]),
    ])

    tab_buttons: dict = {}
    body_container = ft.Container()

    # ─────────────────────────────────────────────────────
    # Manage Students
    # ─────────────────────────────────────────────────────
    def build_students_body():
        q = state["stu_query"].strip().lower()
        filtered = [s for s in _STUDENTS
                    if not q or q in s["name"].lower()
                    or q in s["email"].lower()
                    or q in s["program"].lower()
                    or q in s["id"].lower()]

        rows = [ft.Container(
            padding=ft.Padding.symmetric(vertical=10, horizontal=12),
            content=ft.Row(controls=[
                ft.Text("Student ID",      expand=2, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Full Name",       expand=3, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Email",           expand=3, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Program",         expand=3, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Status",          expand=2, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Enrollment Date", expand=2, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Actions",         expand=2, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"],
                        text_align=ft.TextAlign.RIGHT),
            ])
        )]

        if not filtered:
            rows.append(ft.Container(
                padding=ft.Padding.symmetric(vertical=30),
                alignment=ft.Alignment(0, 0),
                content=ft.Text("No students match.", size=13,
                                color=c()["muted"]),
            ))

        for stu in filtered:
            chip_kind = "success" if stu["status"] == "Active" else "danger"
            rows.append(ft.Container(
                padding=ft.Padding.symmetric(vertical=12, horizontal=12),
                border=ft.Border.only(bottom=ft.BorderSide(1, c()["border"])),
                content=ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(stu["id"],      expand=2, size=12, color=c()["text"]),
                        ft.Text(stu["name"],    expand=3, size=12,
                                weight=ft.FontWeight.W_500, color=c()["text"]),
                        ft.Text(stu["email"],   expand=3, size=12, color=c()["muted"]),
                        ft.Text(stu["program"], expand=3, size=12, color=c()["muted"]),
                        ft.Container(expand=2,
                                     content=colored_chip(stu["status"], chip_kind),
                                     alignment=ft.Alignment(-1, 0)),
                        ft.Text(stu["date"],    expand=2, size=12, color=c()["muted"]),
                        ft.Row(expand=2,
                               alignment=ft.MainAxisAlignment.END,
                               spacing=2,
                               controls=[
                                   ft.IconButton(
                                       icon=ft.Icons.EDIT_OUTLINED,
                                       icon_size=18, icon_color=c()["muted"],
                                       tooltip="Edit",
                                       on_click=lambda e, sid=stu["id"]: _open_edit_student(sid),
                                   ),
                                   ft.IconButton(
                                       icon=ft.Icons.PERSON_REMOVE_OUTLINED,
                                       icon_size=18, icon_color="#dc2626",
                                       tooltip="Delete",
                                       on_click=lambda e, sid=stu["id"]: _confirm_delete_student(sid),
                                   ),
                               ]),
                    ]
                )
            ))

        search = ft.TextField(
            hint_text="Filter students by name, email, or program...",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=20, height=42, filled=True,
            bgcolor=c()["field_bg"], border_color=c()["border"],
            color=c()["text"], expand=True,
            value=state["stu_query"],
            on_change=lambda e: (state.update(stu_query=search.value or ""), refresh()),
        )

        add_btn = ft.Container(
            bgcolor="transparent",
            border=ft.Border.all(1.5, PRIMARY),
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            on_click=lambda e: page.show_dialog(_add_student_dialog(page, c, refresh)),
            content=ft.Row(spacing=6, tight=True, controls=[
                ft.Icon(ft.Icons.PERSON_ADD_OUTLINED, color=PRIMARY, size=16),
                ft.Text("Add New Student", size=13, color=PRIMARY,
                        weight=ft.FontWeight.W_600),
            ]),
        )

        return ft.Column(spacing=14, controls=[
            ft.Row(spacing=12, controls=[search, add_btn]),
            ft.Container(
                bgcolor=c()["card"],
                border=ft.Border.all(1, c()["border"]),
                border_radius=12,
                content=ft.Column(spacing=0, controls=rows),
            ),
        ])

    # ─────────────────────────────────────────────────────
    # Manage Courses
    # ─────────────────────────────────────────────────────
    def build_courses_body():
        q = state["crs_query"].strip().lower()
        filtered = [crs for crs in _COURSES
                    if not q or q in crs["title"].lower()
                    or q in crs["instructor"].lower()
                    or q in crs["id"].lower()]

        rows = [ft.Container(
            padding=ft.Padding.symmetric(vertical=10, horizontal=12),
            content=ft.Row(controls=[
                ft.Text("Course ID",   expand=2, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Title",       expand=4, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Instructor",  expand=3, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Students",    expand=2, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Status",      expand=2, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Actions",     expand=2, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"],
                        text_align=ft.TextAlign.RIGHT),
            ])
        )]

        if not filtered:
            rows.append(ft.Container(
                padding=ft.Padding.symmetric(vertical=30),
                alignment=ft.Alignment(0, 0),
                content=ft.Text("No courses match.", size=13, color=c()["muted"]),
            ))

        for crs in filtered:
            chip_kind = "success" if crs["status"] == "Active" else "neutral"
            rows.append(ft.Container(
                padding=ft.Padding.symmetric(vertical=12, horizontal=12),
                border=ft.Border.only(bottom=ft.BorderSide(1, c()["border"])),
                content=ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(crs["id"],         expand=2, size=12, color=c()["text"]),
                        ft.Text(crs["title"],      expand=4, size=12,
                                weight=ft.FontWeight.W_500, color=c()["text"]),
                        ft.Text(crs["instructor"], expand=3, size=12, color=c()["muted"]),
                        ft.Text(str(crs["students"]), expand=2, size=12, color=c()["text"]),
                        ft.Container(expand=2,
                                     content=colored_chip(crs["status"], chip_kind),
                                     alignment=ft.Alignment(-1, 0)),
                        ft.Row(expand=2,
                               alignment=ft.MainAxisAlignment.END, spacing=2,
                               controls=[
                                   ft.IconButton(
                                       icon=ft.Icons.EDIT_OUTLINED,
                                       icon_size=18, icon_color=c()["muted"],
                                       tooltip="Edit",
                                       on_click=lambda e, cid=crs["id"]: _open_edit_course(cid),
                                   ),
                                   ft.IconButton(
                                       icon=ft.Icons.ARCHIVE_OUTLINED if crs["status"] == "Active"
                                            else ft.Icons.UNARCHIVE_OUTLINED,
                                       icon_size=18, icon_color=c()["muted"],
                                       tooltip="Toggle Archive",
                                       on_click=lambda e, cid=crs["id"]: _toggle_archive_course(cid),
                                   ),
                                   ft.IconButton(
                                       icon=ft.Icons.DELETE_OUTLINE,
                                       icon_size=18, icon_color="#dc2626",
                                       tooltip="Delete",
                                       on_click=lambda e, cid=crs["id"]: _confirm_delete_course(cid),
                                   ),
                               ]),
                    ]
                )
            ))

        search = ft.TextField(
            hint_text="Filter courses by title, instructor or ID...",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=20, height=42, filled=True,
            bgcolor=c()["field_bg"], border_color=c()["border"],
            color=c()["text"], expand=True,
            value=state["crs_query"],
            on_change=lambda e: (state.update(crs_query=search.value or ""), refresh()),
        )

        add_btn = ft.Container(
            bgcolor="transparent",
            border=ft.Border.all(1.5, PRIMARY),
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            on_click=lambda e: page.show_dialog(_add_course_dialog(page, c, refresh)),
            content=ft.Row(spacing=6, tight=True, controls=[
                ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, color=PRIMARY, size=16),
                ft.Text("Add New Course", size=13, color=PRIMARY,
                        weight=ft.FontWeight.W_600),
            ]),
        )

        return ft.Column(spacing=14, controls=[
            ft.Row(spacing=12, controls=[search, add_btn]),
            ft.Container(
                bgcolor=c()["card"],
                border=ft.Border.all(1, c()["border"]),
                border_radius=12,
                content=ft.Column(spacing=0, controls=rows),
            ),
        ])

    # ─────────────────────────────────────────────────────
    # Issue Certificates
    # ─────────────────────────────────────────────────────
    def build_certs_body():
        # Use pending completions as candidates to issue certs for.
        rows = []
        for p in _PENDING_COMPLETIONS:
            rows.append(ft.Container(
                bgcolor=c()["card"],
                border=ft.Border.all(1, c()["border"]),
                border_radius=12,
                padding=ft.Padding.all(16),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(spacing=4, controls=[
                            ft.Text(p["student"], size=14,
                                    weight=ft.FontWeight.BOLD, color=c()["text"]),
                            ft.Text(p["course"], size=12, color=c()["muted"]),
                            ft.Row(spacing=12, controls=[
                                ft.Text(f"Score: {p['score']}%", size=11,
                                        color="#16a34a", weight=ft.FontWeight.BOLD),
                                ft.Text(f"Submitted: {p['submitted']}", size=11,
                                        color=c()["muted"]),
                            ]),
                        ]),
                        ft.Container(
                            bgcolor=PRIMARY, border_radius=8,
                            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                            on_click=lambda e, pid=p["id"]: _issue_cert_for(pid),
                            content=ft.Row(spacing=6, tight=True, controls=[
                                ft.Icon(ft.Icons.WORKSPACE_PREMIUM_OUTLINED,
                                        color="white", size=16),
                                ft.Text("Issue Certificate", size=12,
                                        color="white", weight=ft.FontWeight.BOLD),
                            ])
                        ),
                    ]
                )
            ))

        if not rows:
            rows = [_placeholder(c, ft.Icons.WORKSPACE_PREMIUM_OUTLINED,
                                 "All caught up",
                                 "There are no completions waiting for a certificate.")]

        # Bulk-issue button
        bulk_btn = ft.Container(
            bgcolor="transparent",
            border=ft.Border.all(1.5, PRIMARY),
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            on_click=lambda e: _bulk_issue(),
            content=ft.Row(spacing=6, tight=True, controls=[
                ft.Icon(ft.Icons.PLAYLIST_ADD_CHECK, color=PRIMARY, size=16),
                ft.Text("Bulk-Issue All", size=13, color=PRIMARY,
                        weight=ft.FontWeight.W_600),
            ]),
        )

        return ft.Column(spacing=12, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(f"{len(_PENDING_COMPLETIONS)} students awaiting certificate issuance",
                            size=13, color=c()["muted"]),
                    bulk_btn,
                ]
            ),
            *rows,
        ])

    # ─────────────────────────────────────────────────────
    # Verify Completion
    # ─────────────────────────────────────────────────────
    def build_verify_body():
        rows = []
        for p in _PENDING_COMPLETIONS:
            rows.append(ft.Container(
                bgcolor=c()["card"],
                border=ft.Border.all(1, c()["border"]),
                border_radius=12,
                padding=ft.Padding.all(16),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(spacing=4, controls=[
                            ft.Text(p["student"], size=14,
                                    weight=ft.FontWeight.BOLD, color=c()["text"]),
                            ft.Text(p["course"], size=12, color=c()["muted"]),
                            ft.Row(spacing=12, controls=[
                                ft.Text(f"Score: {p['score']}%", size=11,
                                        color="#16a34a" if p["score"] >= 70 else "#dc2626",
                                        weight=ft.FontWeight.BOLD),
                                ft.Text(f"ID: {p['id']}", size=11,
                                        color=c()["muted"]),
                                ft.Text(f"Submitted: {p['submitted']}", size=11,
                                        color=c()["muted"]),
                            ]),
                        ]),
                        ft.Row(spacing=8, controls=[
                            ft.Container(
                                bgcolor="#16a34a", border_radius=8,
                                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                                on_click=lambda e, pid=p["id"]: _approve(pid),
                                content=ft.Row(spacing=4, tight=True, controls=[
                                    ft.Icon(ft.Icons.CHECK, color="white", size=14),
                                    ft.Text("Approve", color="white", size=12,
                                            weight=ft.FontWeight.BOLD),
                                ])
                            ),
                            ft.Container(
                                border=ft.Border.all(1.5, "#dc2626"), border_radius=8,
                                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                                on_click=lambda e, pid=p["id"]: _reject(pid),
                                content=ft.Row(spacing=4, tight=True, controls=[
                                    ft.Icon(ft.Icons.CLOSE, color="#dc2626", size=14),
                                    ft.Text("Reject", color="#dc2626", size=12,
                                            weight=ft.FontWeight.BOLD),
                                ])
                            ),
                        ]),
                    ]
                )
            ))

        if not rows:
            rows = [_placeholder(c, ft.Icons.FACT_CHECK_OUTLINED,
                                 "Nothing to verify",
                                 "No pending completions at the moment.")]

        return ft.Column(spacing=12, controls=[
            ft.Text(f"{len(_PENDING_COMPLETIONS)} pending completions",
                    size=13, color=c()["muted"]),
            *rows,
        ])

    BODIES = {
        "Manage Students":     build_students_body,
        "Manage Courses":      build_courses_body,
        "Issue Certificates":  build_certs_body,
        "Verify Completion":   build_verify_body,
    }

    # ── action helpers (closures over refresh + page) ────
    def refresh():
        body_container.content = BODIES[state["tab"]]()
        for name, btn_ref in tab_buttons.items():
            is_active = (name == state["tab"])
            if btn_ref.current is None:
                continue
            btn_ref.current.content.controls[0].color = (
                PRIMARY if is_active else c()["muted"]
            )
            btn_ref.current.content.controls[0].weight = (
                ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL
            )
            btn_ref.current.border = ft.Border.only(
                bottom=ft.BorderSide(2 if is_active else 0,
                                     PRIMARY if is_active else "transparent")
            )
        page.update()

    # Students
    def _find_student(sid):
        for s in _STUDENTS:
            if s["id"] == sid:
                return s
        return None

    def _open_edit_student(sid):
        s = _find_student(sid)
        if s is None:
            return
        name_f = ft.TextField(label="Full Name", value=s["name"],
                              border_radius=8, bgcolor=c()["field_bg"],
                              border_color=c()["border"])
        email_f = ft.TextField(label="Email", value=s["email"],
                               border_radius=8, bgcolor=c()["field_bg"],
                               border_color=c()["border"])
        program_f = ft.TextField(label="Program", value=s["program"],
                                 border_radius=8, bgcolor=c()["field_bg"],
                                 border_color=c()["border"])
        status_dd = ft.Dropdown(
            label="Status", value=s["status"],
            options=[ft.dropdown.Option("Active"),
                     ft.dropdown.Option("Suspended")],
            border_radius=8, bgcolor=c()["field_bg"],
            border_color=c()["border"],
        )
        err = ft.Text("", color="#dc2626", size=11, visible=False)

        def save(_e):
            if not (name_f.value or "").strip():
                err.value = "Name required"; err.visible = True
                page.update(); return
            s["name"]    = name_f.value.strip()
            s["email"]   = (email_f.value or "n/a").strip()
            s["program"] = (program_f.value or "General").strip()
            s["status"]  = status_dd.value or "Active"
            page.pop_dialog()
            refresh()
            _toast(page, f"{s['id']} updated")

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Edit {s['id']}", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=420,
                content=ft.Column(spacing=12, tight=True, controls=[
                    name_f, email_f, program_f, status_dd, err,
                ])
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton(
                    "Save Changes",
                    style=ft.ButtonStyle(
                        bgcolor=PRIMARY, color="white",
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=save,
                ),
            ],
        )
        page.show_dialog(dlg)

    def _confirm_delete_student(sid):
        s = _find_student(sid)
        if s is None:
            return

        def do_delete(_e):
            _STUDENTS[:] = [x for x in _STUDENTS if x["id"] != sid]
            page.pop_dialog()
            refresh()
            _toast(page, f"{sid} removed", "#dc2626")

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Remove Student?", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=380,
                content=ft.Column(spacing=8, tight=True, controls=[
                    ft.Text(f"Permanently remove {s['name']} ({sid})?",
                            size=13, color=c()["text"]),
                    ft.Text("All linked enrolment data will be detached.",
                            size=11, color=c()["muted"]),
                ])
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton(
                    "Remove",
                    style=ft.ButtonStyle(
                        bgcolor="#dc2626", color="white",
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=do_delete,
                ),
            ],
        )
        page.show_dialog(dlg)

    # Courses
    def _find_course(cid):
        for crs in _COURSES:
            if crs["id"] == cid:
                return crs
        return None

    def _open_edit_course(cid):
        crs = _find_course(cid)
        if crs is None:
            return
        title_f      = ft.TextField(label="Title", value=crs["title"],
                                    border_radius=8, bgcolor=c()["field_bg"],
                                    border_color=c()["border"])
        instructor_f = ft.TextField(label="Instructor", value=crs["instructor"],
                                    border_radius=8, bgcolor=c()["field_bg"],
                                    border_color=c()["border"])
        students_f   = ft.TextField(label="Enrolled Students",
                                    value=str(crs["students"]),
                                    keyboard_type=ft.KeyboardType.NUMBER,
                                    border_radius=8, bgcolor=c()["field_bg"],
                                    border_color=c()["border"])
        status_dd    = ft.Dropdown(
            label="Status", value=crs["status"],
            options=[ft.dropdown.Option("Active"),
                     ft.dropdown.Option("Archived")],
            border_radius=8, bgcolor=c()["field_bg"],
            border_color=c()["border"],
        )
        err = ft.Text("", color="#dc2626", size=11, visible=False)

        def save(_e):
            if not (title_f.value or "").strip():
                err.value = "Title required"; err.visible = True
                page.update(); return
            try:
                students_n = int(students_f.value or "0")
            except ValueError:
                err.value = "Students must be an integer"; err.visible = True
                page.update(); return
            crs["title"]      = title_f.value.strip()
            crs["instructor"] = (instructor_f.value or "—").strip()
            crs["students"]   = students_n
            crs["status"]     = status_dd.value or "Active"
            page.pop_dialog()
            refresh()
            _toast(page, f"{cid} updated")

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Edit {cid}", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=420,
                content=ft.Column(spacing=12, tight=True, controls=[
                    title_f, instructor_f, students_f, status_dd, err,
                ])
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton(
                    "Save Changes",
                    style=ft.ButtonStyle(
                        bgcolor=PRIMARY, color="white",
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=save,
                ),
            ],
        )
        page.show_dialog(dlg)

    def _toggle_archive_course(cid):
        crs = _find_course(cid)
        if crs is None:
            return
        crs["status"] = "Archived" if crs["status"] == "Active" else "Active"
        refresh()
        _toast(page, f"{cid} → {crs['status']}")

    def _confirm_delete_course(cid):
        crs = _find_course(cid)
        if crs is None:
            return

        def do_delete(_e):
            _COURSES[:] = [x for x in _COURSES if x["id"] != cid]
            page.pop_dialog()
            refresh()
            _toast(page, f"{cid} deleted", "#dc2626")

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Course?", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=380,
                content=ft.Column(spacing=8, tight=True, controls=[
                    ft.Text(f"Delete {crs['title']} ({cid})?",
                            size=13, color=c()["text"]),
                    ft.Text("Enrolled students will lose access.",
                            size=11, color=c()["muted"]),
                ])
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton(
                    "Delete",
                    style=ft.ButtonStyle(
                        bgcolor="#dc2626", color="white",
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=do_delete,
                ),
            ],
        )
        page.show_dialog(dlg)

    # Issue cert / verify
    def _issue_cert_for(pid):
        target = next((x for x in _PENDING_COMPLETIONS if x["id"] == pid), None)
        if target is None:
            return
        new_id = _next_cert_id()
        _CERTS.insert(0, {
            "id":      new_id,
            "student": target["student"],
            "course":  target["course"],
            "code":    f"LMN-{new_id[-3:]}-2026",
            "date":    "Today",
            "status":  "Verified",
        })
        _PENDING_COMPLETIONS[:] = [
            x for x in _PENDING_COMPLETIONS if x["id"] != pid
        ]
        refresh()
        _toast(page, f"Issued {new_id} to {target['student']}")

    def _bulk_issue():
        if not _PENDING_COMPLETIONS:
            _toast(page, "No pending completions"); return
        count = 0
        for pid in [x["id"] for x in list(_PENDING_COMPLETIONS)]:
            _issue_cert_for(pid)
            count += 1
        _toast(page, f"Bulk-issued {count} certificates")

    def _approve(pid):
        target = next((x for x in _PENDING_COMPLETIONS if x["id"] == pid), None)
        if target is None:
            return
        # Auto-issue a certificate on approval.
        _issue_cert_for(pid)
        _toast(page, f"Approved completion for {target['student']}")

    def _reject(pid):
        target = next((x for x in _PENDING_COMPLETIONS if x["id"] == pid), None)
        if target is None:
            return
        _PENDING_COMPLETIONS[:] = [
            x for x in _PENDING_COMPLETIONS if x["id"] != pid
        ]
        refresh()
        _toast(page, f"Rejected {target['student']}'s submission", "#dc2626")

    # ── tabs construction
    def make_tab(name: str):
        ref = ft.Ref[ft.Container]()
        tab_buttons[name] = ref
        is_active = (name == state["tab"])
        return ft.Container(
            ref=ref,
            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
            on_click=lambda e, n=name: (state.update(tab=n), refresh()),
            border=ft.Border.only(
                bottom=ft.BorderSide(2 if is_active else 0,
                                     PRIMARY if is_active else "transparent")
            ),
            content=ft.Row(spacing=6, tight=True, controls=[
                ft.Text(name, size=13,
                        color=PRIMARY if is_active else c()["muted"],
                        weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL),
            ]),
        )

    tabs_row = ft.Container(
        border=ft.Border.only(bottom=ft.BorderSide(1, c()["border"])),
        content=ft.Row(spacing=4, controls=[make_tab(n) for n in _TAB_NAMES]),
    )

    health_card = ft.Container(
        bgcolor=c()["field_bg"], border_radius=12,
        padding=ft.Padding.all(14),
        content=ft.Row(spacing=12, controls=[
            ft.Container(
                bgcolor=PRIMARY_BG, border_radius=10,
                padding=ft.Padding.all(8),
                content=ft.Icon(ft.Icons.HEALTH_AND_SAFETY_OUTLINED,
                                color=PRIMARY, size=18),
            ),
            ft.Column(spacing=2, controls=[
                ft.Text("System Health: Optimal", size=12,
                        weight=ft.FontWeight.BOLD, color=c()["text"]),
                ft.Text("All background processes for student credentialing are active.",
                        size=11, color=c()["muted"]),
            ]),
        ])
    )

    # Initial render
    body_container.content = BODIES[state["tab"]]()

    return ft.Column(
        scroll=ft.ScrollMode.AUTO, spacing=18,
        controls=[
            header,
            tabs_row,
            body_container,
            health_card,
            page_footer(c),
        ]
    )


# ── helpers ──────────────────────────────────────────────
def _placeholder(c, icon, title, subtitle):
    return ft.Container(
        bgcolor=c()["card"], border_radius=12,
        padding=ft.Padding.all(40),
        alignment=ft.Alignment(0, 0),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Container(
                    width=64, height=64,
                    bgcolor=PRIMARY_BG, border_radius=32,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(icon, color=PRIMARY, size=28),
                ),
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD,
                        color=c()["text"]),
                ft.Text(subtitle, size=12, color=c()["muted"],
                        text_align=ft.TextAlign.CENTER),
            ]
        )
    )


def _add_student_dialog(page: ft.Page, c, on_added):
    full_name = ft.TextField(
        label="Full Name", hint_text="e.g. Jane Doe",
        border_radius=8, bgcolor=c()["field_bg"], border_color=c()["border"],
    )
    email = ft.TextField(
        label="Email Address", hint_text="jane@example.com",
        border_radius=8, bgcolor=c()["field_bg"], border_color=c()["border"],
    )
    program = ft.TextField(
        label="Initial Program", hint_text="Computer Science 101",
        border_radius=8, bgcolor=c()["field_bg"], border_color=c()["border"],
    )
    err = ft.Text("", color="#dc2626", size=11, visible=False)

    def create(_e):
        if not (full_name.value or "").strip():
            err.value = "Name is required"
            err.visible = True
            page.update()
            return
        new_id = _next_student_id()
        new_student = {
            "id":      new_id,
            "name":    full_name.value.strip(),
            "email":   (email.value or "n/a").strip(),
            "program": (program.value or "General").strip(),
            "status":  "Active",
            "date":    "Today",
        }

        try:
            r = requests.post(f"{API_URL}/students", json={
                "id":      new_student["id"],
                "name":    new_student["name"],
                "email":   new_student["email"],
                "program": new_student["program"],
                "status":  new_student["status"],
            }, timeout=2)
            api_result = r.json()
        except Exception:
            api_result = None

        if api_result and "detail" in api_result:
            err.value = api_result["detail"]
            err.visible = True
            page.update()
            return

        _STUDENTS.append(new_student)
        page.pop_dialog()
        on_added()
        if api_result and "message" in api_result:
            _toast(page, f"Student {new_id} saved (API + local)")
        else:
            _toast(page, f"Student {new_id} saved locally (API offline)")

    return ft.AlertDialog(
        modal=True,
        title=ft.Text("Add New Student", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            width=400,
            content=ft.Column(spacing=12, tight=True, controls=[
                ft.Text("Create a new student account. They will receive an "
                        "email invitation.",
                        size=12, color=c()["muted"]),
                full_name, email, program, err,
            ])
        ),
        actions=[
            ft.TextButton("Cancel",
                          style=ft.ButtonStyle(color=c()["muted"]),
                          on_click=lambda e: page.pop_dialog()),
            ft.ElevatedButton(
                "Create Account",
                style=ft.ButtonStyle(
                    bgcolor=PRIMARY, color="white",
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                on_click=create,
            ),
        ],
    )


def _add_course_dialog(page: ft.Page, c, on_added):
    title_f      = ft.TextField(label="Course Title",
                                border_radius=8, bgcolor=c()["field_bg"],
                                border_color=c()["border"])
    instructor_f = ft.TextField(label="Instructor",
                                border_radius=8, bgcolor=c()["field_bg"],
                                border_color=c()["border"])
    students_f   = ft.TextField(label="Enrolled Students", value="0",
                                keyboard_type=ft.KeyboardType.NUMBER,
                                border_radius=8, bgcolor=c()["field_bg"],
                                border_color=c()["border"])
    err = ft.Text("", color="#dc2626", size=11, visible=False)

    def create(_e):
        if not (title_f.value or "").strip():
            err.value = "Title required"; err.visible = True
            page.update(); return
        try:
            students_n = int(students_f.value or "0")
        except ValueError:
            err.value = "Students must be an integer"; err.visible = True
            page.update(); return
        new_id = _next_course_id()
        _COURSES.append({
            "id":         new_id,
            "title":      title_f.value.strip(),
            "instructor": (instructor_f.value or "TBD").strip(),
            "students":   students_n,
            "status":     "Active",
        })
        page.pop_dialog()
        on_added()
        _toast(page, f"Course {new_id} created")

    return ft.AlertDialog(
        modal=True,
        title=ft.Text("Add New Course", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            width=420,
            content=ft.Column(spacing=12, tight=True, controls=[
                title_f, instructor_f, students_f, err,
            ])
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
            ft.ElevatedButton(
                "Create Course",
                style=ft.ButtonStyle(
                    bgcolor=PRIMARY, color="white",
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                on_click=create,
            ),
        ],
    )