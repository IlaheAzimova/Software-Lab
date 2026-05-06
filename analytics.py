"""
Progress Analytics page – PDF page 5.

Wired interactions in this version:
  • "Filter by Student ID..." is a real text input – live-filters the score table.
  • "All Categories" opens a category-picker dialog – live-filters the table.
  • "Last 30 Days" opens a date-range picker – sets the active label.
  • "Export Report" writes a CSV snapshot and shows a toast.
  • "View All Records" opens a scrollable dialog of every row.

Charts are drawn with plain Flet primitives (Container / Stack) so the
page works without the optional ``flet-charts`` extension package.
"""
import csv
import os
import tempfile

import flet as ft

from theme import PRIMARY, PRIMARY_BG
from ui_widgets import avatar, initials_of, colored_chip, page_footer


# ── Demo data ────────────────────────────────────────────
_PERFORMANCE_TREND = [68, 70, 72, 78, 82, 85]   # Jan – Jun
_TREND_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]

_GROUPS = [
    ("Engineering", 95, 35),
    ("Design",      88, 28),
    ("Business",    72, 32),
    ("Arts",        55, 22),
    ("Science",     78, 30),
]

_SCORE_BREAKDOWN = [
    {"sid": "S001", "name": "Alex Johnson",  "module": "Intro to UI/UX",
     "category": "Design",      "score": 92, "attempt": 1, "status": "Completed",   "date": "Jun 12, 2024"},
    {"sid": "S002", "name": "Sarah Miller",  "module": "Advanced React",
     "category": "Engineering", "score": 85, "attempt": 2, "status": "Completed",   "date": "Jun 11, 2024"},
    {"sid": "S003", "name": "Michael Chen",  "module": "Intro to UI/UX",
     "category": "Design",      "score": 45, "attempt": 1, "status": "Failed",      "date": "Jun 11, 2024"},
    {"sid": "S004", "name": "Emma Wilson",   "module": "Data Science 101",
     "category": "Science",     "score": 76, "attempt": 1, "status": "In-Progress", "date": "Jun 10, 2024"},
    {"sid": "S005", "name": "James Brown",   "module": "Product Design",
     "category": "Design",      "score": 88, "attempt": 1, "status": "Completed",   "date": "Jun 9,  2024"},
    {"sid": "S006", "name": "Linda Park",    "module": "Macroeconomics 101",
     "category": "Business",    "score": 71, "attempt": 1, "status": "Completed",   "date": "Jun 8,  2024"},
    {"sid": "S007", "name": "Diego Rivera",  "module": "Quantum Physics Intro",
     "category": "Science",     "score": 64, "attempt": 2, "status": "In-Progress", "date": "Jun 7,  2024"},
    {"sid": "S008", "name": "Yuki Tanaka",   "module": "Strategic Marketing",
     "category": "Business",    "score": 90, "attempt": 1, "status": "Completed",   "date": "Jun 6,  2024"},
    {"sid": "S009", "name": "Olivia Reed",   "module": "Modern Sculpture",
     "category": "Arts",        "score": 81, "attempt": 1, "status": "Completed",   "date": "Jun 5,  2024"},
    {"sid": "S010", "name": "Hassan Ali",    "module": "Mobile App Security",
     "category": "Engineering", "score": 58, "attempt": 1, "status": "Failed",      "date": "Jun 4,  2024"},
]

_CATEGORIES   = ["All Categories", "Engineering", "Design", "Business", "Science", "Arts"]
_DATE_RANGES  = ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Year to Date", "All Time"]


def _toast(page: ft.Page, msg: str, color: str = PRIMARY):
    page.show_dialog(ft.SnackBar(content=ft.Text(msg, color="white"), bgcolor=color))


def build_analytics_page(page: ft.Page, c) -> ft.Control:
    state = {
        "sid_query":  "",
        "category":   "All Categories",
        "date_range": "Last 30 Days",
    }

    # ── Stat tile ────────────────────────────────────────
    def stat_card(label, value, delta, delta_color, icon):
        delta_arrow = "↗" if not delta.startswith("-") else "↘"
        return ft.Container(
            expand=True, bgcolor=c()["card"], border_radius=12,
            padding=ft.Padding.all(20),
            shadow=ft.BoxShadow(
                blur_radius=8,
                color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
            ),
            content=ft.Column(spacing=6, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(label, size=12, color=c()["muted"]),
                        ft.Container(
                            bgcolor=PRIMARY_BG,
                            border_radius=8,
                            padding=ft.Padding.all(6),
                            content=ft.Icon(icon, color=PRIMARY, size=16),
                        ),
                    ]
                ),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=c()["text"]),
                ft.Row(spacing=4, controls=[
                    ft.Text(f"{delta_arrow} {delta}", size=11,
                            weight=ft.FontWeight.BOLD, color=delta_color),
                    ft.Text("since last month", size=11, color=c()["muted"]),
                ])
            ])
        )

    # ── Trend area chart (custom-drawn) ──────────────────
    def area_chart():
        chart_h = 180
        col_w   = 60
        v_min, v_max = 30, 100

        def y_for(v):
            return chart_h - ((v - v_min) / (v_max - v_min)) * chart_h

        line_segments = []
        for i in range(len(_PERFORMANCE_TREND) - 1):
            x1 = i * col_w + col_w / 2
            y1 = y_for(_PERFORMANCE_TREND[i])
            y2 = y_for(_PERFORMANCE_TREND[i + 1])
            line_segments.append(ft.Container(
                left=x1, top=min(y1, y2),
                width=col_w,
                height=chart_h - min(y1, y2),
                bgcolor=ft.Colors.with_opacity(0.08, PRIMARY),
            ))

        dots = []
        for i, v in enumerate(_PERFORMANCE_TREND):
            cx = i * col_w + col_w / 2
            cy = y_for(v)
            dots.append(ft.Container(
                left=cx - 4, top=cy - 4,
                width=8, height=8,
                bgcolor=PRIMARY, border_radius=4,
            ))

        connectors = []
        for i in range(len(_PERFORMANCE_TREND) - 1):
            x1 = i * col_w + col_w / 2
            x2 = (i + 1) * col_w + col_w / 2
            y1 = y_for(_PERFORMANCE_TREND[i])
            y2 = y_for(_PERFORMANCE_TREND[i + 1])
            connectors.append(ft.Container(
                left=min(x1, x2), top=min(y1, y2) + (abs(y2 - y1) / 2),
                width=abs(x2 - x1), height=2,
                bgcolor=PRIMARY,
            ))

        y_grid = []
        for v in [25, 50, 75, 100]:
            y_grid.append(ft.Container(
                left=0, top=y_for(v),
                width=col_w * len(_PERFORMANCE_TREND),
                height=1,
                bgcolor=ft.Colors.with_opacity(0.5, c()["border"]),
            ))

        x_axis = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[ft.Text(lb, size=11, color=c()["muted"]) for lb in _TREND_LABELS],
            width=col_w * len(_PERFORMANCE_TREND),
        )

        y_axis = ft.Column(
            spacing=0,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=ft.CrossAxisAlignment.END,
            controls=[
                ft.Text("100", size=10, color=c()["muted"]),
                ft.Text("75",  size=10, color=c()["muted"]),
                ft.Text("50",  size=10, color=c()["muted"]),
                ft.Text("25",  size=10, color=c()["muted"]),
                ft.Text("0",   size=10, color=c()["muted"]),
            ],
            height=chart_h,
        )

        plot = ft.Stack(
            width=col_w * len(_PERFORMANCE_TREND),
            height=chart_h,
            controls=y_grid + line_segments + connectors + dots,
        )

        return ft.Container(
            content=ft.Column(spacing=4, controls=[
                ft.Row(spacing=10, controls=[y_axis, plot]),
                ft.Row(spacing=10, controls=[
                    ft.Container(width=20),
                    x_axis,
                ]),
                ft.Row([
                    ft.Container(width=10, height=10, bgcolor=PRIMARY,
                                 border_radius=5),
                    ft.Text("Average Score", size=11, color=c()["muted"]),
                ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
            ])
        )

    def perf_card():
        return ft.Container(
            expand=True, bgcolor=c()["card"], border_radius=12,
            padding=ft.Padding.all(20),
            shadow=ft.BoxShadow(
                blur_radius=8,
                color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
            ),
            content=ft.Column(spacing=12, controls=[
                ft.Text("Performance Trends", size=15,
                        weight=ft.FontWeight.BOLD, color=c()["text"]),
                ft.Text("Average student scores vs. institutional benchmark over 6 months.",
                        size=11, color=c()["muted"]),
                area_chart(),
            ])
        )

    # ── Completion bar chart (horizontal, custom-drawn) ──
    def completion_card():
        max_v = max(max(a, b) for _, a, b in _GROUPS) or 100
        rows  = []
        for label, completed, in_progress in _GROUPS:
            rows.append(ft.Column(spacing=4, controls=[
                ft.Text(label, size=11, color=c()["text"]),
                ft.Row(spacing=4, controls=[
                    ft.Container(
                        width=200 * completed / max_v, height=10,
                        bgcolor=PRIMARY, border_radius=5,
                    ),
                    ft.Container(
                        width=200 * in_progress / max_v, height=10,
                        bgcolor="#86efac", border_radius=5,
                    ),
                    ft.Text(f"{completed} / {in_progress}", size=10,
                            color=c()["muted"]),
                ]),
            ]))
        return ft.Container(
            expand=True, bgcolor=c()["card"], border_radius=12,
            padding=ft.Padding.all(20),
            shadow=ft.BoxShadow(
                blur_radius=8,
                color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
            ),
            content=ft.Column(spacing=12, controls=[
                ft.Text("Lesson Completion by Group", size=15,
                        weight=ft.FontWeight.BOLD, color=c()["text"]),
                ft.Text("Completed vs. in-progress lessons per academic group.",
                        size=11, color=c()["muted"]),
                ft.Column(spacing=12, controls=rows),
                ft.Row(spacing=14, alignment=ft.MainAxisAlignment.CENTER, controls=[
                    ft.Row([
                        ft.Container(width=10, height=10, bgcolor=PRIMARY,
                                     border_radius=5),
                        ft.Text("Completed", size=11, color=c()["muted"]),
                    ], spacing=4),
                    ft.Row([
                        ft.Container(width=10, height=10, bgcolor="#86efac",
                                     border_radius=5),
                        ft.Text("In Progress", size=11, color=c()["muted"]),
                    ], spacing=4),
                ]),
            ])
        )

    # ── Score-breakdown table ────────────────────────────
    def score_status_chip(status):
        if status == "Completed":
            return colored_chip("Completed", "success")
        if status == "Failed":
            return colored_chip("Failed", "danger")
        return colored_chip("In-Progress", "info")

    def progress_bar(value: int):
        color = "#16a34a" if value >= 70 else "#dc2626"
        return ft.Stack(
            controls=[
                ft.Container(
                    width=120, height=6,
                    bgcolor=c()["border"], border_radius=3,
                ),
                ft.Container(
                    width=120 * value / 100, height=6,
                    bgcolor=color, border_radius=3,
                ),
            ],
            width=120, height=6,
        )

    def score_row(r):
        return ft.Container(
            padding=ft.Padding.symmetric(vertical=12, horizontal=4),
            border=ft.Border.only(bottom=ft.BorderSide(1, c()["border"])),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(r["sid"], expand=1, size=12, color=c()["text"]),
                    ft.Row(expand=3, spacing=8, controls=[
                        avatar(initials_of(r["name"]), size=30),
                        ft.Text(r["name"], size=12,
                                weight=ft.FontWeight.W_500,
                                color=c()["text"]),
                    ]),
                    ft.Text(r["module"], expand=3, size=12, color=c()["muted"]),
                    ft.Column(expand=2, spacing=2, controls=[
                        ft.Text(f"{r['score']}%", size=12,
                                weight=ft.FontWeight.W_600,
                                color="#16a34a" if r["score"] >= 70 else "#dc2626"),
                        progress_bar(r["score"]),
                    ]),
                    ft.Text(str(r["attempt"]), expand=1, size=12, color=c()["text"],
                            text_align=ft.TextAlign.CENTER),
                    ft.Container(expand=2, content=score_status_chip(r["status"])),
                    ft.Text(r["date"], expand=2, size=12, color=c()["muted"]),
                ]
            )
        )

    score_table_header = ft.Row(controls=[
        ft.Text("ID",             expand=1, size=11,
                weight=ft.FontWeight.BOLD, color=c()["muted"]),
        ft.Text("Student",        expand=3, size=11,
                weight=ft.FontWeight.BOLD, color=c()["muted"]),
        ft.Text("Lesson Module",  expand=3, size=11,
                weight=ft.FontWeight.BOLD, color=c()["muted"]),
        ft.Text("Score (%)",      expand=2, size=11,
                weight=ft.FontWeight.BOLD, color=c()["muted"]),
        ft.Text("Attempt",        expand=1, size=11,
                weight=ft.FontWeight.BOLD, color=c()["muted"],
                text_align=ft.TextAlign.CENTER),
        ft.Text("Status",         expand=2, size=11,
                weight=ft.FontWeight.BOLD, color=c()["muted"]),
        ft.Text("Last Activity",  expand=2, size=11,
                weight=ft.FontWeight.BOLD, color=c()["muted"]),
    ])

    table_rows_container = ft.Column(spacing=0)
    result_label         = ft.Text("", size=11, color=c()["muted"])

    def filtered_rows():
        q   = state["sid_query"].strip().lower()
        cat = state["category"]
        out = []
        for r in _SCORE_BREAKDOWN:
            if q and q not in r["sid"].lower() \
                    and q not in r["name"].lower():
                continue
            if cat != "All Categories" and r["category"] != cat:
                continue
            out.append(r)
        return out

    def render_table():
        table_rows_container.controls.clear()
        rows = filtered_rows()
        if not rows:
            table_rows_container.controls.append(
                ft.Container(
                    padding=ft.Padding.symmetric(vertical=24),
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text("No records match the current filters.",
                                    size=13, color=c()["muted"]),
                )
            )
        else:
            # only show the first 5 in the inline table
            for r in rows[:5]:
                table_rows_container.controls.append(score_row(r))
        result_label.value = (
            f"{len(rows)} of {len(_SCORE_BREAKDOWN)} records "
            f"· filter: {state['category']} · range: {state['date_range']}"
        )
        page.update()

    # ── Header controls (the 4 buttons the user wanted wired) ──

    # 1) Student-ID search
    sid_search = ft.TextField(
        hint_text="Filter by Student ID...",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=8, height=40, filled=True, width=200,
        bgcolor=c()["field_bg"], border_color=c()["border"],
        color=c()["text"], text_size=12,
    )

    def on_sid_change(e):
        state["sid_query"] = sid_search.value or ""
        render_table()
    sid_search.on_change = on_sid_change

    # 2) Category dropdown – clickable container that opens a picker
    category_label_text = ft.Text(state["category"], size=12, color=c()["text"])

    def open_category_picker(_e):
        def pick(cat):
            state["category"] = cat
            category_label_text.value = cat
            page.pop_dialog()
            render_table()

        def opt(label):
            return ft.Container(
                padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                border_radius=8,
                bgcolor=PRIMARY_BG if state["category"] == label else "transparent",
                on_click=lambda e, l=label: pick(l),
                content=ft.Row(spacing=8, controls=[
                    ft.Icon(
                        ft.Icons.CHECK if state["category"] == label
                        else ft.Icons.CIRCLE_OUTLINED,
                        size=14,
                        color=PRIMARY if state["category"] == label
                        else c()["muted"],
                    ),
                    ft.Text(label, size=13, color=c()["text"]),
                ])
            )
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Filter by Category", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=300,
                content=ft.Column(spacing=4, tight=True,
                                  controls=[opt(x) for x in _CATEGORIES]),
            ),
            actions=[ft.TextButton("Close",
                                   on_click=lambda e: page.pop_dialog())],
        )
        page.show_dialog(dlg)

    category_btn = ft.Container(
        height=40,
        border=ft.Border.all(1, c()["border"]),
        border_radius=8,
        padding=ft.Padding.symmetric(horizontal=12),
        on_click=open_category_picker,
        content=ft.Row([
            category_label_text,
            ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=16, color=c()["muted"]),
        ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
    )

    # 3) Date-range button – opens a range picker
    date_label_text = ft.Text(state["date_range"], size=12, color=c()["text"])

    def open_date_picker(_e):
        def pick(label):
            state["date_range"] = label
            date_label_text.value = label
            page.pop_dialog()
            render_table()
            _toast(page, f"Range: {label}")

        def opt(label):
            return ft.Container(
                padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                border_radius=8,
                bgcolor=PRIMARY_BG if state["date_range"] == label else "transparent",
                on_click=lambda e, l=label: pick(l),
                content=ft.Row(spacing=8, controls=[
                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color=c()["muted"]),
                    ft.Text(label, size=13, color=c()["text"]),
                ]),
            )
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Date Range", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=280,
                content=ft.Column(spacing=4, tight=True,
                                  controls=[opt(x) for x in _DATE_RANGES]),
            ),
            actions=[ft.TextButton("Close",
                                   on_click=lambda e: page.pop_dialog())],
        )
        page.show_dialog(dlg)

    date_btn = ft.Container(
        height=40,
        border=ft.Border.all(1, c()["border"]),
        border_radius=8,
        padding=ft.Padding.symmetric(horizontal=12),
        on_click=open_date_picker,
        content=ft.Row([
            ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color=c()["muted"]),
            date_label_text,
            ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=14, color=c()["muted"]),
        ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
    )

    # 4) Export Report – writes a real CSV file and toasts the path
    def export_report(_e):
        rows = filtered_rows()
        try:
            tmp_dir = tempfile.gettempdir()
            path = os.path.join(tmp_dir, "analytics_report.csv")
            with open(path, "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(["ID", "Name", "Module", "Category",
                            "Score", "Attempt", "Status", "Date"])
                for r in rows:
                    w.writerow([r["sid"], r["name"], r["module"], r["category"],
                                r["score"], r["attempt"], r["status"], r["date"]])
            _toast(page, f"Exported {len(rows)} rows → {path}")
        except Exception as ex:
            _toast(page, f"Export failed: {ex}", "#dc2626")

    export_btn = ft.Container(
        height=40,
        bgcolor=PRIMARY, border_radius=8,
        padding=ft.Padding.symmetric(horizontal=14),
        on_click=export_report,
        content=ft.Row([
            ft.Icon(ft.Icons.DOWNLOAD, color="white", size=16),
            ft.Text("Export Report", color="white", size=12,
                    weight=ft.FontWeight.W_600),
        ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
    )

    # ── View-All-Records dialog
    def open_view_all(_e):
        rows = filtered_rows() or _SCORE_BREAKDOWN
        items = [score_table_header]
        for r in rows:
            items.append(score_row(r))
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"All Records ({len(rows)})", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=820, height=460,
                content=ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO,
                                  controls=items),
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton(
                    "Export These",
                    style=ft.ButtonStyle(
                        bgcolor=PRIMARY, color="white",
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=lambda e: (page.pop_dialog(), export_report(None)),
                ),
            ],
        )
        page.show_dialog(dlg)

    score_card = ft.Container(
        bgcolor=c()["card"], border_radius=12, padding=ft.Padding.all(20),
        shadow=ft.BoxShadow(
            blur_radius=8,
            color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
        ),
        content=ft.Column(spacing=8, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(spacing=2, controls=[
                        ft.Text("Score Breakdown", size=15,
                                weight=ft.FontWeight.BOLD, color=c()["text"]),
                        ft.Text("Detailed audit of individual student assessment records.",
                                size=11, color=c()["muted"]),
                    ]),
                    ft.TextButton("View All Records",
                                  style=ft.ButtonStyle(color=PRIMARY),
                                  on_click=open_view_all),
                ]
            ),
            score_table_header,
            table_rows_container,
            result_label,
        ])
    )

    # initial render of the score table
    render_table()

    # ── Page header ──────────────────────────────────────
    header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Column(spacing=2, controls=[
                ft.Text("Progress Analytics", size=24,
                        weight=ft.FontWeight.BOLD, color=c()["text"]),
                ft.Text("Real-time performance metrics and student engagement insights.",
                        size=13, color=c()["muted"]),
            ]),
            ft.Row(spacing=8, controls=[
                sid_search,
                category_btn,
                date_btn,
                export_btn,
            ]),
        ]
    )

    return ft.Column(
        scroll=ft.ScrollMode.AUTO, spacing=20,
        controls=[
            header,
            ft.Row(spacing=16, controls=[
                stat_card("Avg. Assessment Score", "82.4%", "+4.2%",
                          "#16a34a", ft.Icons.TRENDING_UP),
                stat_card("Lesson Completion Rate", "76.8%", "+1.5%",
                          "#16a34a", ft.Icons.TASK_ALT),
                stat_card("Active Students", "1,284", "-2.1%",
                          "#dc2626", ft.Icons.PEOPLE_OUTLINE),
                stat_card("Total Assessments", "4,592", "+12.3%",
                          "#16a34a", ft.Icons.ARTICLE),
            ]),
            ft.Row(spacing=16,
                   vertical_alignment=ft.CrossAxisAlignment.START,
                   controls=[perf_card(), completion_card()]),
            score_card,
            page_footer(c),
        ]
    )