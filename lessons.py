
import flet as ft
import requests

from theme import PRIMARY, PRIMARY_BG
from ui_widgets import colored_chip, page_footer, primary_button

API_URL = "http://127.0.0.1:8000"


PER_PAGE = 5


# In-memory lessons "database".
_LESSONS = [
    {
        "id": "LSN-001", "title": "Introduction to Neural Networks",
        "desc": "A comprehensive overview of the basic structures and algorithms",
        "category": "Computer Science", "level": "INTERMEDIATE", "level_kind": "info",
        "date": "Mar 15, 2024", "status": "Published",
    },
    {
        "id": "LSN-002", "title": "Advanced Data Visualisation with D3.js",
        "desc": "Master the art of creating dynamic, interactive, and",
        "category": "Data Science", "level": "ADVANCED", "level_kind": "purple",
        "date": "Mar 12, 2024", "status": "Published",
    },
    {
        "id": "LSN-003", "title": "Fundamentals of Macroeconomics",
        "desc": "Exploring the performance, structure, behavior, and",
        "category": "Economics", "level": "BEGINNER", "level_kind": "success",
        "date": "Mar 10, 2024", "status": "Draft",
    },
    {
        "id": "LSN-004", "title": "Biochemistry: The Chemistry of Life",
        "desc": "An introductory course covering the chemical processes within and",
        "category": "Science", "level": "INTERMEDIATE", "level_kind": "info",
        "date": "Mar 5, 2024", "status": "Published",
    },
    {
        "id": "LSN-005", "title": "Strategic Marketing Management",
        "desc": "Learn how to apply marketing theory and principles to",
        "category": "Business", "level": "ADVANCED", "level_kind": "purple",
        "date": "Feb 28, 2024", "status": "Archived",
    },
]


def _next_lesson_id() -> str:
    nums = [int(l["id"].split("-")[1]) for l in _LESSONS if l["id"].startswith("LSN-")]
    nxt = (max(nums) + 1) if nums else 1
    return f"LSN-{nxt:03d}"


def _toast(page: ft.Page, msg: str, color: str = PRIMARY):
    page.show_dialog(ft.SnackBar(content=ft.Text(msg, color="white"), bgcolor=color))


# ─────────────────────────────────────────────────────────
# Public helper (used by dashboard Quick Actions)
# ─────────────────────────────────────────────────────────
def open_upload_lesson_dialog(page: ft.Page, c, on_added=None):
    page.show_dialog(_upload_dialog(page, c, on_added or (lambda: None)))


# ─────────────────────────────────────────────────────────
# Page builder
# ─────────────────────────────────────────────────────────
def build_lessons_page(page: ft.Page, c) -> ft.Control:
    rows_container = ft.Column(spacing=0)

    state = {"page": 1, "query": ""}
    result_count_ref = ft.Ref[ft.Text]()
    pagination_row   = ft.Row(spacing=8)

    search_field = ft.TextField(
        hint_text="Search lessons by title, description, or keyword...",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=20, height=42, filled=True,
        bgcolor=c()["field_bg"], border_color=c()["border"],
        color=c()["text"], expand=True,
    )

    def status_pill(status: str):
        kind = {"Published": "success", "Draft": "warn"}.get(status, "neutral")
        return colored_chip(status, kind)

    def header_row():
        return ft.Container(
            padding=ft.Padding.symmetric(vertical=10, horizontal=12),
            content=ft.Row(controls=[
                ft.Text("Lesson Title",  expand=4, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Description",   expand=4, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Category",      expand=3, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Upload Date",   expand=2, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Status",        expand=2, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Actions",       expand=2, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"],
                        text_align=ft.TextAlign.RIGHT),
            ])
        )

    def lesson_row(lesson: dict):
        def _mi(label, icon, on_click):
            return ft.PopupMenuItem(
                content=ft.Row(spacing=10, controls=[
                    ft.Icon(icon, size=16, color=c()["muted"]),
                    ft.Text(label, size=13, color=c()["text"]),
                ]),
                on_click=on_click,
            )

        more_menu = ft.PopupMenuButton(
            icon=ft.Icons.MORE_VERT, icon_size=18, icon_color=c()["muted"],
            tooltip="More actions",
            items=[
                _mi(
                    "Mark as Draft" if lesson["status"] == "Published"
                    else "Mark as Published",
                    ft.Icons.SWAP_HORIZ,
                    lambda e, lid=lesson["id"]: _toggle_status(lid),
                ),
                _mi("Duplicate", ft.Icons.CONTENT_COPY,
                    lambda e, lid=lesson["id"]: _duplicate_lesson(lid)),
                ft.PopupMenuItem(),  # divider
                _mi("Delete", ft.Icons.DELETE_OUTLINE,
                    lambda e, lid=lesson["id"]: _confirm_delete(lid)),
            ],
        )
        return ft.Container(
            padding=ft.Padding.symmetric(vertical=14, horizontal=12),
            border=ft.Border.only(bottom=ft.BorderSide(1, c()["border"])),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(expand=4, spacing=2, controls=[
                        ft.Text(lesson["title"], size=13,
                                weight=ft.FontWeight.W_600, color=c()["text"]),
                        ft.Text(lesson["id"], size=11, color=c()["muted"]),
                    ]),
                    ft.Text(lesson["desc"], expand=4, size=12,
                            color=c()["muted"], max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Column(expand=3, spacing=4, controls=[
                        ft.Text(lesson["category"], size=12,
                                weight=ft.FontWeight.W_500, color=c()["text"]),
                        ft.Container(
                            content=colored_chip(lesson["level"], lesson["level_kind"]),
                            alignment=ft.Alignment(-1, 0),
                        ),
                    ]),
                    ft.Text(lesson["date"], expand=2, size=12, color=c()["muted"]),
                    ft.Container(
                        expand=2,
                        content=status_pill(lesson["status"]),
                        alignment=ft.Alignment(-1, 0),
                    ),
                    ft.Row(
                        expand=2,
                        alignment=ft.MainAxisAlignment.END,
                        spacing=2,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.VISIBILITY_OUTLINED,
                                icon_size=18, icon_color=c()["muted"],
                                tooltip="Preview",
                                on_click=lambda e, lid=lesson["id"]:
                                    _open_preview(lid),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                icon_size=18, icon_color=c()["muted"],
                                tooltip="Edit",
                                on_click=lambda e, lid=lesson["id"]:
                                    _open_edit(lid),
                            ),
                            more_menu,
                        ],
                    ),
                ]
            )
        )

    def filtered_lessons():
        q = state["query"].strip().lower()
        if not q:
            return list(_LESSONS)
        return [
            l for l in _LESSONS
            if q in l["title"].lower()
            or q in l["desc"].lower()
            or q in l["category"].lower()
        ]

    def total_pages():
        n = max(1, len(filtered_lessons()))
        return (n + PER_PAGE - 1) // PER_PAGE

    def render_rows():
        rows_container.controls.clear()
        rows_container.controls.append(header_row())

        items = filtered_lessons()
        total = len(items)

        if state["page"] > total_pages():
            state["page"] = total_pages()
        if state["page"] < 1:
            state["page"] = 1

        start = (state["page"] - 1) * PER_PAGE
        end   = start + PER_PAGE
        page_items = items[start:end]

        if not page_items:
            rows_container.controls.append(
                ft.Container(
                    padding=ft.Padding.symmetric(vertical=30),
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text("No lessons match your search.",
                                    size=13, color=c()["muted"]),
                )
            )
        else:
            for lesson in page_items:
                rows_container.controls.append(lesson_row(lesson))

        if result_count_ref.current is not None:
            shown_from = (start + 1) if total else 0
            shown_to   = min(end, total)
            result_count_ref.current.value = (
                f"Showing {shown_from}-{shown_to} of {total} results"
            )

        # rebuild pagination row
        pagination_row.controls.clear()
        pagination_row.controls.append(
            ft.OutlinedButton(
                "Previous",
                style=ft.ButtonStyle(
                    color=c()["muted"] if state["page"] > 1 else c()["border"],
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                disabled=state["page"] <= 1,
                on_click=lambda e: (state.update(page=state["page"] - 1),
                                    render_rows()),
            )
        )
        for p in range(1, total_pages() + 1):
            is_active = (p == state["page"])
            pagination_row.controls.append(
                ft.Container(
                    width=32, height=32, border_radius=6,
                    bgcolor=PRIMARY if is_active else "transparent",
                    border=None if is_active else ft.Border.all(1, c()["border"]),
                    alignment=ft.Alignment(0, 0),
                    on_click=(None if is_active else
                              (lambda e, pp=p: (state.update(page=pp),
                                                render_rows()))),
                    content=ft.Text(
                        str(p),
                        color="white" if is_active else c()["muted"],
                        weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                    ),
                )
            )
        pagination_row.controls.append(
            ft.OutlinedButton(
                "Next",
                style=ft.ButtonStyle(
                    color=c()["muted"] if state["page"] < total_pages() else c()["border"],
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                disabled=state["page"] >= total_pages(),
                on_click=lambda e: (state.update(page=state["page"] + 1),
                                    render_rows()),
            )
        )
        page.update()

    # ── action handlers ──────────────────────────────────
    def _find(lid):
        for l in _LESSONS:
            if l["id"] == lid:
                return l
        return None

    def _open_preview(lid):
        l = _find(lid)
        if l is None:
            return
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(l["title"], weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=460,
                content=ft.Column(spacing=10, tight=True, controls=[
                    ft.Row(spacing=8, controls=[
                        colored_chip(l["status"],
                                     "success" if l["status"] == "Published"
                                     else ("warn" if l["status"] == "Draft" else "neutral")),
                        colored_chip(l["level"], l["level_kind"]),
                        ft.Text(l["category"], size=12, color=c()["muted"]),
                    ]),
                    ft.Divider(height=1),
                    ft.Text("Description", size=11, weight=ft.FontWeight.BOLD,
                            color=c()["muted"]),
                    ft.Text(l["desc"], size=13, color=c()["text"]),
                    ft.Divider(height=1),
                    ft.Row(spacing=24, controls=[
                        ft.Column(spacing=2, controls=[
                            ft.Text("ID", size=11, color=c()["muted"]),
                            ft.Text(l["id"], size=13, color=c()["text"]),
                        ]),
                        ft.Column(spacing=2, controls=[
                            ft.Text("Uploaded", size=11, color=c()["muted"]),
                            ft.Text(l["date"], size=13, color=c()["text"]),
                        ]),
                    ]),
                ])
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton(
                    "Edit Lesson",
                    style=ft.ButtonStyle(
                        bgcolor=PRIMARY, color="white",
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=lambda e: (page.pop_dialog(), _open_edit(lid)),
                ),
            ],
        )
        page.show_dialog(dlg)

    def _open_edit(lid):
        l = _find(lid)
        if l is None:
            return

        title_f = ft.TextField(label="Title", value=l["title"],
                               border_radius=8,
                               bgcolor=c()["field_bg"], border_color=c()["border"])
        desc_f  = ft.TextField(label="Description", value=l["desc"],
                               multiline=True, max_lines=3, border_radius=8,
                               bgcolor=c()["field_bg"], border_color=c()["border"])
        cat_f   = ft.TextField(label="Category", value=l["category"],
                               border_radius=8,
                               bgcolor=c()["field_bg"], border_color=c()["border"])
        status_dd = ft.Dropdown(
            label="Status", value=l["status"],
            options=[ft.dropdown.Option("Published"),
                     ft.dropdown.Option("Draft"),
                     ft.dropdown.Option("Archived")],
            border_radius=8,
            bgcolor=c()["field_bg"], border_color=c()["border"],
        )
        level_dd = ft.Dropdown(
            label="Level", value=l["level"],
            options=[ft.dropdown.Option("BEGINNER"),
                     ft.dropdown.Option("INTERMEDIATE"),
                     ft.dropdown.Option("ADVANCED")],
            border_radius=8,
            bgcolor=c()["field_bg"], border_color=c()["border"],
        )
        err = ft.Text("", color="#dc2626", size=11, visible=False)

        def save(_e):
            if not (title_f.value or "").strip():
                err.value = "Title cannot be empty"
                err.visible = True
                page.update()
                return
            l["title"]    = title_f.value.strip()
            l["desc"]     = (desc_f.value or "").strip() or "—"
            l["category"] = (cat_f.value or "General").strip()
            l["status"]   = status_dd.value or "Draft"
            l["level"]    = level_dd.value or "BEGINNER"
            l["level_kind"] = {
                "BEGINNER": "success",
                "INTERMEDIATE": "info",
                "ADVANCED": "purple",
            }.get(l["level"], "neutral")
            page.pop_dialog()
            render_rows()
            _toast(page, f"Lesson {l['id']} updated")

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Edit {l['id']}", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=440,
                content=ft.Column(spacing=12, tight=True, controls=[
                    title_f, desc_f, cat_f,
                    ft.Row(spacing=10, controls=[
                        ft.Container(expand=True, content=status_dd),
                        ft.Container(expand=True, content=level_dd),
                    ]),
                    err,
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

    def _toggle_status(lid):
        l = _find(lid)
        if l is None:
            return
        l["status"] = "Draft" if l["status"] == "Published" else "Published"
        render_rows()
        _toast(page, f"Lesson {lid} marked as {l['status']}")

    def _duplicate_lesson(lid):
        l = _find(lid)
        if l is None:
            return
        copy = dict(l)
        copy["id"]     = _next_lesson_id()
        copy["title"]  = l["title"] + " (Copy)"
        copy["status"] = "Draft"
        copy["date"]   = "Today"
        _LESSONS.append(copy)
        render_rows()
        _toast(page, f"Duplicated as {copy['id']}")

    def _confirm_delete(lid):
        l = _find(lid)
        if l is None:
            return

        def do_delete(_e):
            _LESSONS[:] = [x for x in _LESSONS if x["id"] != lid]
            page.pop_dialog()
            render_rows()
            _toast(page, f"Lesson {lid} deleted", "#dc2626")

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Lesson?", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=380,
                content=ft.Column(spacing=8, tight=True, controls=[
                    ft.Text(f"You are about to delete \u201c{l['title']}\u201d.",
                            size=13, color=c()["text"]),
                    ft.Text("This action cannot be undone.",
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

    # ── search wiring
    def on_search_change(e):
        state["query"] = search_field.value or ""
        state["page"]  = 1
        render_rows()

    search_field.on_change = on_search_change

    # ── filters / sort
    def on_category_change(e):
        v = category_dd.value or "All"
        state["query"] = "" if v == "All" else v
        search_field.value = "" if v == "All" else v
        state["page"] = 1
        render_rows()

    category_dd = ft.Dropdown(
        value="All",
        options=[
            ft.dropdown.Option("All",       "All Categories"),
            ft.dropdown.Option("Computer",  "Computer Science"),
            ft.dropdown.Option("Data",      "Data Science"),
            ft.dropdown.Option("Economics", "Economics"),
            ft.dropdown.Option("Science",   "Science"),
            ft.dropdown.Option("Business",  "Business"),
        ],
        width=180, height=42, border_radius=8,
        bgcolor=c()["field_bg"], border_color=c()["border"],
        color=c()["text"],
    )
    category_dd.on_change = on_category_change
    sort_btn = ft.Container(
        height=42, border=ft.Border.all(1, c()["border"]),
        border_radius=8, padding=ft.Padding.symmetric(horizontal=12),
        on_click=lambda e: (_LESSONS.reverse(), render_rows(),
                            _toast(page, "Sort order reversed")),
        content=ft.Row([
            ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color=c()["muted"]),
            ft.Text("Newest First", size=13, color=c()["text"]),
        ], spacing=6),
    )

    upload_btn = primary_button(
        "Upload Lesson", icon=ft.Icons.ADD_CIRCLE_OUTLINE,
        on_click=lambda e: page.show_dialog(
            _upload_dialog(page, c, on_added=render_rows)
        ),
    )

    # ── initial draw
    render_rows()

    return ft.Column(
        scroll=ft.ScrollMode.AUTO, spacing=20,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Column(spacing=2, controls=[
                        ft.Text("Lesson Management", size=24,
                                weight=ft.FontWeight.BOLD, color=c()["text"]),
                        ft.Text("Manage, update, and upload educational content for your students.",
                                size=13, color=c()["muted"]),
                    ]),
                    upload_btn,
                ]
            ),
            ft.Container(
                bgcolor=c()["card"], border_radius=12,
                padding=ft.Padding.all(16),
                shadow=ft.BoxShadow(
                    blur_radius=8,
                    color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                ),
                content=ft.Column(spacing=16, controls=[
                    ft.Row(spacing=12, controls=[
                        search_field,
                        category_dd,
                        sort_btn,
                    ]),
                    rows_container,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Showing 1-5 of 5 results", ref=result_count_ref,
                                    size=12, color=c()["muted"]),
                            pagination_row,
                        ]
                    )
                ])
            ),
            page_footer(c),
        ]
    )


# ── Upload-lesson dialog ─────────────────────────────────
def _upload_dialog(page: ft.Page, c, on_added):
    title_field    = ft.TextField(label="Title",
                                  border_radius=8,
                                  bgcolor=c()["field_bg"], border_color=c()["border"])
    desc_field     = ft.TextField(label="Description",
                                  border_radius=8, multiline=True, max_lines=3,
                                  bgcolor=c()["field_bg"], border_color=c()["border"])
    category_field = ft.TextField(label="Category", value="General",
                                  border_radius=8,
                                  bgcolor=c()["field_bg"], border_color=c()["border"])
    level_dd       = ft.Dropdown(
        label="Level", value="BEGINNER",
        options=[ft.dropdown.Option("BEGINNER"),
                 ft.dropdown.Option("INTERMEDIATE"),
                 ft.dropdown.Option("ADVANCED")],
        border_radius=8,
        bgcolor=c()["field_bg"], border_color=c()["border"],
    )
    err = ft.Text("", color="#dc2626", size=11, visible=False)

    def save(e):
        if not (title_field.value or "").strip():
            err.value = "Title cannot be empty"
            err.visible = True
            page.update()
            return
        new_id = _next_lesson_id()
        lvl    = level_dd.value or "BEGINNER"
        new_lesson = {
            "id":         new_id,
            "title":      title_field.value.strip(),
            "desc":       (desc_field.value or "").strip() or "—",
            "category":   (category_field.value or "General").strip(),
            "level":      lvl,
            "level_kind": {"BEGINNER": "success",
                           "INTERMEDIATE": "info",
                           "ADVANCED": "purple"}.get(lvl, "neutral"),
            "date":       "Today",
            "status":     "Draft",
        }

        # Try POST to FastAPI first (5 fields the API stores)
        try:
            r = requests.post(f"{API_URL}/lessons", json={
                "id":       new_id,
                "title":    new_lesson["title"],
                "category": new_lesson["category"],
                "level":    new_lesson["level"],
                "status":   new_lesson["status"],
            }, timeout=2)
            api_result = r.json()
        except Exception:
            api_result = None

        if api_result and "detail" in api_result:
            err.value = api_result["detail"]
            err.visible = True
            page.update()
            return

        _LESSONS.append(new_lesson)
        page.pop_dialog()
        on_added()
        if api_result and "message" in api_result:
            _toast(page, f"Lesson {new_id} saved (API + local)")
        else:
            _toast(page, f"Lesson {new_id} saved locally (API offline)")

    return ft.AlertDialog(
        modal=True,
        title=ft.Text("Upload New Lesson", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            width=440,
            content=ft.Column(spacing=12, tight=True, controls=[
                ft.Text("Add a new lesson to your library.",
                        size=12, color=c()["muted"]),
                title_field, desc_field, category_field, level_dd, err,
            ])
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
            ft.ElevatedButton(
                "Save",
                style=ft.ButtonStyle(
                    bgcolor=PRIMARY, color="white",
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                on_click=save,
            ),
        ],
    )