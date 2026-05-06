"""
Certificates page – PDF page 6.

Wired interactions in this version:
  • Search filters live by student name, course, code, or ID.
  • Manual Issue opens a dialog and inserts a new certificate (Pending).
  • Download icon shows a snackbar simulating PDF export.
  • Open icon opens a "certificate preview" dialog.
  • More (⋮) menu: Verify / Mark Pending / Revoke (deletes).
  • Filter button opens a status filter popup.
  • Previous / Next pagination really pages (5 per page).
"""
import flet as ft
import requests

from theme import PRIMARY, PRIMARY_BG
from ui_widgets import avatar, initials_of, page_footer

API_URL = "http://127.0.0.1:8000"


PER_PAGE = 5


# Mutable list of dicts so edits actually take effect.
_CERTS = [
    {"id": "CERT-9901", "student": "Alex Rivera",     "course": "Advanced React Patterns",
     "code": "LMN-RE-2023-X92", "date": "Oct 24, 2023", "status": "Verified"},
    {"id": "CERT-8842", "student": "Sarah Chen",      "course": "Data Structures & Algorithms",
     "code": "LMN-DS-2023-A44", "date": "Nov 12, 2023", "status": "Verified"},
    {"id": "CERT-7731", "student": "Marcus Thorne",   "course": "UI/UX Foundations",
     "code": "LMN-UI-2023-B12", "date": "Dec 05, 2023", "status": "Pending"},
    {"id": "CERT-6610", "student": "Elena Rodriguez", "course": "Fullstack Web Development",
     "code": "LMN-FS-2023-Z01", "date": "Jan 15, 2024", "status": "Verified"},
    {"id": "CERT-5509", "student": "Jordan Smith",    "course": "Project Management Basics",
     "code": "LMN-PM-2024-C33", "date": "Feb 20, 2024", "status": "Verified"},
]


def _next_cert_id() -> str:
    nums = [int(x["id"].split("-")[1]) for x in _CERTS if x["id"].startswith("CERT-")]
    nxt = (max(nums) + 1) if nums else 9000
    return f"CERT-{nxt}"


def _toast(page: ft.Page, msg: str, color: str = PRIMARY):
    page.show_dialog(ft.SnackBar(content=ft.Text(msg, color="white"), bgcolor=color))


# ─────────────────────────────────────────────────────────
# Public helper (used by dashboard Quick Actions)
# ─────────────────────────────────────────────────────────
def open_manual_issue_dialog(page: ft.Page, c, on_added=None):
    page.show_dialog(_manual_issue_dialog(page, c, on_added or (lambda: None)))


# ─────────────────────────────────────────────────────────
# Page builder
# ─────────────────────────────────────────────────────────
def build_certificates_page(page: ft.Page, c) -> ft.Control:
    rows_container = ft.Column(spacing=0)
    state = {"page": 1, "query": "", "status_filter": "All"}
    pagination_row = ft.Row(spacing=8)

    showing_label = ft.Text("Showing 5 of 5 results", size=12, color=c()["muted"])

    search_field = ft.TextField(
        hint_text="Search by student or code...",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=20, height=42, filled=True,
        bgcolor=c()["field_bg"], border_color=c()["border"],
        color=c()["text"], expand=True,
    )

    def stat_card(icon, label, value):
        return ft.Container(
            expand=True, bgcolor=c()["card"], border_radius=12,
            padding=ft.Padding.all(20),
            shadow=ft.BoxShadow(
                blur_radius=8,
                color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
            ),
            content=ft.Row(spacing=14, controls=[
                ft.Container(
                    bgcolor=PRIMARY_BG, border_radius=10,
                    padding=ft.Padding.all(10),
                    content=ft.Icon(icon, color=PRIMARY, size=22),
                ),
                ft.Column(spacing=2, controls=[
                    ft.Text(label, size=12, color=c()["muted"]),
                    ft.Text(value, size=22, weight=ft.FontWeight.BOLD,
                            color=c()["text"]),
                ]),
            ])
        )

    def status_pill(status: str):
        if status == "Verified":
            return ft.Row(spacing=4, controls=[
                ft.Icon(ft.Icons.VERIFIED_OUTLINED, size=14, color="#16a34a"),
                ft.Text("Verified", size=11, weight=ft.FontWeight.BOLD,
                        color="#16a34a"),
            ])
        return ft.Row(spacing=4, controls=[
            ft.Icon(ft.Icons.SCHEDULE, size=14, color="#d97706"),
            ft.Text("Pending", size=11, weight=ft.FontWeight.BOLD,
                    color="#d97706"),
        ])

    def header_row():
        return ft.Container(
            padding=ft.Padding.symmetric(vertical=10, horizontal=12),
            content=ft.Row(controls=[
                ft.Text("Certificate ID", expand=2, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Student",        expand=3, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Certificate Code", expand=2, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Issued At",      expand=2, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Status",         expand=2, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                ft.Text("Actions",        expand=2, size=11,
                        weight=ft.FontWeight.BOLD, color=c()["muted"],
                        text_align=ft.TextAlign.RIGHT),
            ])
        )

    def cert_row(cert):
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
                    "Mark as Pending" if cert["status"] == "Verified"
                    else "Mark as Verified",
                    ft.Icons.VERIFIED_OUTLINED,
                    lambda e, cid=cert["id"]: _toggle_status(cid),
                ),
                _mi("Copy Code", ft.Icons.CONTENT_COPY,
                    lambda e, code=cert["code"]:
                        _toast(page, f"Code copied: {code}")),
                ft.PopupMenuItem(),
                _mi("Revoke", ft.Icons.BLOCK,
                    lambda e, cid=cert["id"]: _confirm_revoke(cid)),
            ],
        )
        return ft.Container(
            padding=ft.Padding.symmetric(vertical=14, horizontal=12),
            border=ft.Border.only(bottom=ft.BorderSide(1, c()["border"])),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(cert["id"], expand=2, size=12, color=PRIMARY,
                            weight=ft.FontWeight.BOLD),
                    ft.Row(expand=3, spacing=10, controls=[
                        avatar(initials_of(cert["student"]), size=32),
                        ft.Column(spacing=2, controls=[
                            ft.Text(cert["student"], size=12,
                                    weight=ft.FontWeight.W_600,
                                    color=c()["text"]),
                            ft.Text(cert["course"], size=11, color=c()["muted"]),
                        ]),
                    ]),
                    ft.Container(
                        expand=2,
                        content=ft.Container(
                            bgcolor=c()["field_bg"],
                            border=ft.Border.all(1, c()["border"]),
                            border_radius=6,
                            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                            content=ft.Text(cert["code"], size=11,
                                            color=c()["text"]),
                        ),
                        alignment=ft.Alignment(-1, 0),
                    ),
                    ft.Text(cert["date"], expand=2, size=12, color=c()["muted"]),
                    ft.Container(expand=2, content=status_pill(cert["status"]),
                                 alignment=ft.Alignment(-1, 0)),
                    ft.Row(
                        expand=2,
                        alignment=ft.MainAxisAlignment.END,
                        spacing=2,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.DOWNLOAD,
                                icon_size=18, icon_color=PRIMARY,
                                tooltip="Download PDF",
                                on_click=lambda e, cid=cert["id"]:
                                    _download(cid),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.OPEN_IN_NEW,
                                icon_size=18, icon_color=c()["muted"],
                                tooltip="Open Preview",
                                on_click=lambda e, cid=cert["id"]:
                                    _open_preview(cid),
                            ),
                            more_menu,
                        ],
                    ),
                ]
            )
        )

    def filtered_certs():
        q = state["query"].strip().lower()
        sf = state["status_filter"]
        out = []
        for cert in _CERTS:
            if q and q not in cert["student"].lower() \
                    and q not in cert["code"].lower() \
                    and q not in cert["id"].lower() \
                    and q not in cert["course"].lower():
                continue
            if sf != "All" and cert["status"] != sf:
                continue
            out.append(cert)
        return out

    def total_pages():
        n = max(1, len(filtered_certs()))
        return (n + PER_PAGE - 1) // PER_PAGE

    def render_rows():
        rows_container.controls.clear()
        rows_container.controls.append(header_row())

        items = filtered_certs()
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
                    content=ft.Text("No certificates match your search.",
                                    size=13, color=c()["muted"]),
                )
            )
        else:
            for cert in page_items:
                rows_container.controls.append(cert_row(cert))

        shown_from = (start + 1) if total else 0
        shown_to   = min(end, total)
        showing_label.value = f"Showing {shown_from}-{shown_to} of {total} results"

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
    def _find(cid):
        for x in _CERTS:
            if x["id"] == cid:
                return x
        return None

    def _download(cid):
        cert = _find(cid)
        if cert:
            _toast(page,
                   f"Exported {cert['id']} for {cert['student']} as PDF")

    def _open_preview(cid):
        cert = _find(cid)
        if cert is None:
            return
        body = ft.Container(
            width=480, padding=ft.Padding.all(20),
            bgcolor=PRIMARY_BG, border_radius=10,
            border=ft.Border.all(2, PRIMARY),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.WORKSPACE_PREMIUM_ROUNDED,
                            color=PRIMARY, size=40),
                    ft.Text("Certificate of Completion", size=16,
                            weight=ft.FontWeight.BOLD, color=PRIMARY),
                    ft.Text("This certifies that", size=11, color=c()["muted"]),
                    ft.Text(cert["student"], size=20,
                            weight=ft.FontWeight.BOLD, color=c()["text"]),
                    ft.Text("has successfully completed the course",
                            size=11, color=c()["muted"]),
                    ft.Text(cert["course"], size=14,
                            weight=ft.FontWeight.W_600, color=c()["text"]),
                    ft.Container(height=6),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(spacing=0, controls=[
                                ft.Text("Code", size=10, color=c()["muted"]),
                                ft.Text(cert["code"], size=11,
                                        color=c()["text"],
                                        weight=ft.FontWeight.BOLD),
                            ]),
                            ft.Column(spacing=0,
                                      horizontal_alignment=ft.CrossAxisAlignment.END,
                                      controls=[
                                          ft.Text("Issued", size=10, color=c()["muted"]),
                                          ft.Text(cert["date"], size=11,
                                                  color=c()["text"],
                                                  weight=ft.FontWeight.BOLD),
                                      ]),
                        ]
                    )
                ]
            )
        )
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(cert["id"], weight=ft.FontWeight.BOLD),
            content=body,
            actions=[
                ft.TextButton("Close", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton(
                    "Download",
                    style=ft.ButtonStyle(
                        bgcolor=PRIMARY, color="white",
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=lambda e: (page.pop_dialog(), _download(cid)),
                ),
            ],
        )
        page.show_dialog(dlg)

    def _toggle_status(cid):
        cert = _find(cid)
        if cert is None:
            return
        new_status = "Pending" if cert["status"] == "Verified" else "Verified"

        try:
            r = requests.put(f"{API_URL}/certificates/{cid}", json={
                "id":      cid,
                "student": cert["student"],
                "course":  cert["course"],
                "code":    cert["code"],
                "status":  new_status,
            }, timeout=2)
            api_result = r.json()
        except Exception:
            api_result = None
        if api_result and "detail" in api_result:
            _toast(page, api_result["detail"], "#dc2626")
            return

        cert["status"] = new_status
        render_rows()
        _toast(page, f"{cid} marked as {new_status}")

    def _confirm_revoke(cid):
        cert = _find(cid)
        if cert is None:
            return

        def do_revoke(_e):
            try:
                requests.delete(f"{API_URL}/certificates/{cid}", timeout=2)
            except Exception:
                pass
            _CERTS[:] = [x for x in _CERTS if x["id"] != cid]
            page.pop_dialog()
            render_rows()
            _toast(page, f"Certificate {cid} revoked", "#dc2626")

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Revoke Certificate?", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=380,
                content=ft.Column(spacing=8, tight=True, controls=[
                    ft.Text(f"Revoke {cid} for {cert['student']}?",
                            size=13, color=c()["text"]),
                    ft.Text("This permanently removes the certificate.",
                            size=11, color=c()["muted"]),
                ])
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton(
                    "Revoke",
                    style=ft.ButtonStyle(
                        bgcolor="#dc2626", color="white",
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=do_revoke,
                ),
            ],
        )
        page.show_dialog(dlg)

    # ── search wiring
    search_field.on_change = lambda e: (
        state.update(query=search_field.value or "", page=1), render_rows()
    )

    # ── filter button
    def open_filter_menu(e):
        def pick(s):
            state["status_filter"] = s
            state["page"] = 1
            page.pop_dialog()
            render_rows()

        def opt(label):
            return ft.Container(
                padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                border_radius=8,
                bgcolor=PRIMARY_BG if state["status_filter"] == label
                                    else "transparent",
                on_click=lambda _e, l=label: pick(l),
                content=ft.Row(spacing=8, controls=[
                    ft.Icon(
                        ft.Icons.CHECK if state["status_filter"] == label
                        else ft.Icons.CIRCLE_OUTLINED,
                        size=14,
                        color=PRIMARY if state["status_filter"] == label
                        else c()["muted"],
                    ),
                    ft.Text(label, size=13, color=c()["text"]),
                ])
            )
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Filter by Status", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=300,
                content=ft.Column(spacing=4, tight=True, controls=[
                    opt("All"), opt("Verified"), opt("Pending"),
                ])
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda e: page.pop_dialog()),
            ],
        )
        page.show_dialog(dlg)

    # Manual issue button
    manual_issue_btn = ft.Container(
        bgcolor=PRIMARY, border_radius=10,
        padding=ft.Padding.symmetric(horizontal=18, vertical=12),
        on_click=lambda e: page.show_dialog(
            _manual_issue_dialog(page, c, on_added=render_rows)
        ),
        content=ft.Row([
            ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, color="white", size=18),
            ft.Text("Manual Issue", color="white", size=13,
                    weight=ft.FontWeight.W_600),
        ], spacing=8, tight=True),
    )

    filter_btn = ft.Container(
        border=ft.Border.all(1, c()["border"]), border_radius=10,
        padding=ft.Padding.symmetric(horizontal=14, vertical=10),
        on_click=open_filter_menu,
        content=ft.Row([
            ft.Icon(ft.Icons.FILTER_LIST, size=16, color=c()["text"]),
            ft.Text("Filter", size=13, color=c()["text"]),
        ], spacing=6, tight=True),
    )

    # initial render
    render_rows()

    header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Row(spacing=10, controls=[
                ft.Icon(ft.Icons.WORKSPACE_PREMIUM_ROUNDED, size=24, color=c()["text"]),
                ft.Column(spacing=2, controls=[
                    ft.Text("Certificates", size=24,
                            weight=ft.FontWeight.BOLD, color=c()["text"]),
                    ft.Text("Manage and verify academic credentials and certifications.",
                            size=13, color=c()["muted"]),
                ]),
            ]),
            ft.Row(spacing=8, controls=[manual_issue_btn, filter_btn]),
        ]
    )

    return ft.Column(
        scroll=ft.ScrollMode.AUTO, spacing=20,
        controls=[
            header,
            ft.Row(spacing=16, controls=[
                stat_card(ft.Icons.WORKSPACE_PREMIUM_OUTLINED, "Total Issued", "1,284"),
                stat_card(ft.Icons.VERIFIED_OUTLINED,          "Verified",     "1,240"),
                stat_card(ft.Icons.SCHEDULE,                   "Pending",      "44"),
            ]),
            ft.Container(
                bgcolor=c()["card"], border_radius=12,
                padding=ft.Padding.all(16),
                shadow=ft.BoxShadow(
                    blur_radius=8,
                    color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                ),
                content=ft.Column(spacing=14, controls=[
                    ft.Row(spacing=12, controls=[search_field, showing_label]),
                    rows_container,
                    pagination_row,
                ])
            ),
            page_footer(c),
        ]
    )


def _manual_issue_dialog(page: ft.Page, c, on_added):
    student_field = ft.TextField(label="Student name",
                                 border_radius=8,
                                 bgcolor=c()["field_bg"],
                                 border_color=c()["border"])
    course_field  = ft.TextField(label="Course",
                                 border_radius=8,
                                 bgcolor=c()["field_bg"],
                                 border_color=c()["border"])
    err = ft.Text("", color="#dc2626", size=11, visible=False)

    def issue(_e):
        if not (student_field.value or "").strip():
            err.value = "Student name required"
            err.visible = True
            page.update()
            return
        new_id = _next_cert_id()
        new_cert = {
            "id":      new_id,
            "student": student_field.value.strip(),
            "course":  (course_field.value or "Custom Course").strip(),
            "code":    f"LMN-{new_id[-3:]}-2026",
            "date":    "Today",
            "status":  "Pending",
        }

        try:
            r = requests.post(f"{API_URL}/certificates", json={
                "id":      new_cert["id"],
                "student": new_cert["student"],
                "course":  new_cert["course"],
                "code":    new_cert["code"],
                "status":  new_cert["status"],
            }, timeout=2)
            api_result = r.json()
        except Exception:
            api_result = None

        if api_result and "detail" in api_result:
            err.value = api_result["detail"]
            err.visible = True
            page.update()
            return

        _CERTS.insert(0, new_cert)
        page.pop_dialog()
        on_added()
        if api_result and "message" in api_result:
            _toast(page, f"Issued {new_id} (API + local)")
        else:
            _toast(page, f"Issued {new_id} locally (API offline)")

    return ft.AlertDialog(
        modal=True,
        title=ft.Text("Manual Issue", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            width=380,
            content=ft.Column(spacing=12, tight=True, controls=[
                ft.Text("Issue a certificate manually for a student.",
                        size=12, color=c()["muted"]),
                student_field, course_field, err,
            ])
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
            ft.ElevatedButton(
                "Issue",
                style=ft.ButtonStyle(
                    bgcolor=PRIMARY, color="white",
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                on_click=issue,
            ),
        ],
    )