
import flet as ft

from theme import get_colors, PRIMARY, PRIMARY_BG
from ui_widgets import avatar, initials_of, page_footer
from lessons       import build_lessons_page, open_upload_lesson_dialog
from analytics     import build_analytics_page
from certificates  import build_certificates_page, open_manual_issue_dialog
from management    import build_management_page
from assessment    import build_assessment_page


def show_dashboard(page: ft.Page, user_email: str, on_logout, user_role: str = "Student"):
    page.window.width  = 1200
    page.window.height = 780
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.vertical_alignment   = ft.MainAxisAlignment.START

    def c():
        return get_colors(page)

    page.bgcolor = c()["bg"]
    page.controls.clear()

    name_part    = user_email.split("@")[0].replace(".", " ").title()
    display_name = name_part if name_part else "Instructor"

    current_page = {"name": "Dashboard"}

    # ─── Dashboard content 
    def stat_card(icon, icon_color, icon_bg, value, label, badge, badge_color):
        return ft.Container(
            expand=True, padding=ft.Padding.all(20),
            bgcolor=c()["card"], border_radius=12,
            shadow=ft.BoxShadow(
                blur_radius=8,
                color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK)
            ),
            content=ft.Column([
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Container(
                            bgcolor=icon_bg, border_radius=8,
                            padding=ft.Padding.all(8),
                            content=ft.Icon(icon, color=icon_color, size=20),
                        ),
                        ft.Container(
                            content=ft.Text(badge, size=11, weight=ft.FontWeight.BOLD,
                                            color=badge_color),
                            bgcolor=ft.Colors.with_opacity(0.15, badge_color),
                            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                            border_radius=20,
                        ),
                    ]
                ),
                ft.Text(value, size=26, weight=ft.FontWeight.BOLD, color=c()["text"]),
                ft.Text(label, size=12, color=c()["muted"]),
            ], spacing=6)
        )

    def score_chip(text, color):
        if "Needs" in text:
            return ft.Container(
                content=ft.Text(text, size=11, weight=ft.FontWeight.BOLD, color="white"),
                bgcolor=color, border_radius=20,
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
            )
        return ft.Text(text, size=12, weight=ft.FontWeight.W_500, color=color)

    def build_dashboard_content():
        students_data = [
            ("Emma Watson",  "Quantum Physics Intro",  "Excellent: 92%",    "#16a34a", "May 24, 2024"),
            ("John Boyega",  "Deep Learning Basics",    "Good: 78%",         "#2563eb", "May 23, 2024"),
            ("Oscar Isaac",  "Macroeconomics 101",      "Needs Review: 55%", "#dc2626", "May 23, 2024"),
            ("Daisy Ridley", "UI/UX Design Systems",    "Excellent: 88%",    "#16a34a", "May 22, 2024"),
            ("Adam Driver",  "Mobile App Security",     "Good: 64%",         "#2563eb", "May 21, 2024"),
        ]

        assessment_rows = []
        for name, module, score, score_color, date in students_data:
            assessment_rows.append(ft.Container(
                padding=ft.Padding.symmetric(vertical=10, horizontal=4),
                border=ft.Border.only(bottom=ft.BorderSide(1, c()["border"])),
                content=ft.Row(controls=[
                    ft.Row(expand=3, controls=[
                        avatar(initials_of(name)),
                        ft.Text(name, size=13, color=c()["text"],
                                weight=ft.FontWeight.W_500),
                    ]),
                    ft.Text(module, expand=3, size=12, color=c()["muted"]),
                    ft.Container(expand=3, content=score_chip(score, score_color)),
                    ft.Text(date, expand=2, size=12, color=c()["muted"]),
                ])
            ))

        activities = [
            ("MA", "Marcus Aurelius", "Completed Lesson: Advanced React Patterns", "2 MINS AGO"),
            ("HT", "Helena Troy",     "Submitted Assessment: Calculus II Final",   "15 MINS AGO"),
            ("JB", "Julian Black",    "Started Lesson: Introduction to Figma",     "1 HOUR AGO"),
            ("SC", "Sophie Chen",     "Earned Certificate: Data Science Pro",      "3 HOURS AGO"),
            ("LN", "Liam Neeson",     "Joined Course: Python for Automation",      "5 HOURS AGO"),
        ]
        activity_items = [
            ft.Container(
                padding=ft.Padding.symmetric(vertical=8),
                content=ft.Row([
                    avatar(ini, size=36),
                    ft.Column([
                        ft.Text(name,   size=13, weight=ft.FontWeight.W_600, color=c()["text"]),
                        ft.Text(action, size=11, color=c()["muted"]),
                        ft.Text(time,   size=10, color=PRIMARY),
                    ], spacing=1, expand=True),
                ], spacing=10)
            )
            for ini, name, action, time in activities
        ]

        def qa_outline_btn(icon, lbl, on_click):
            return ft.Container(
                bgcolor="transparent",
                border=ft.Border.all(1.5, PRIMARY),
                border_radius=30,
                padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                on_click=on_click,
                content=ft.Row([
                    ft.Icon(icon, color=PRIMARY, size=18),
                    ft.Text(lbl, size=13, color=PRIMARY, weight=ft.FontWeight.W_600),
                ], spacing=10)
            )

        def toast(msg, color=PRIMARY):
            page.show_dialog(ft.SnackBar(content=ft.Text(msg, color="white"),
                                         bgcolor=color))

        def deny_qa(action_name, allowed):
            allowed_str = " / ".join(allowed)
            toast(
                f"🔒 Only {allowed_str} can {action_name}. "
                f"You are signed in as {user_role}.",
                color="#dc2626",
            )

        def qa_upload_lesson(_e):
            if not has_access("Upload New Lesson", QA_ACCESS):
                deny_qa("upload lessons", QA_ACCESS["Upload New Lesson"])
                return
            open_upload_lesson_dialog(
                page, c,
                on_added=lambda: (switch_page("Lessons"))
            )

        def qa_issue_certificate(_e):
            if not has_access("Issue Certificate", QA_ACCESS):
                deny_qa("issue certificates", QA_ACCESS["Issue Certificate"])
                return
            open_manual_issue_dialog(
                page, c,
                on_added=lambda: (switch_page("Certificates"))
            )

        def qa_view_students(_e):
            if not has_access("View Student List", QA_ACCESS):
                deny_qa("view students", QA_ACCESS["View Student List"])
                return
            switch_page("Management")

        def qa_create_assessment(_e):
            if not has_access("Create Assessment", QA_ACCESS):
                deny_qa("create assessments", QA_ACCESS["Create Assessment"])
                return
            page.show_dialog(_create_assessment_dialog(page, c, switch_page, toast))

        quick_actions = ft.Container(
            bgcolor=PRIMARY, border_radius=12,
            shadow=ft.BoxShadow(
                blur_radius=12, spread_radius=0,
                offset=ft.Offset(0, 4),
                color=ft.Colors.with_opacity(0.10, ft.Colors.BLACK),
            ),
            content=ft.Column(spacing=0, tight=True, controls=[
                ft.Container(
                    padding=ft.Padding.only(left=20, right=20, top=18, bottom=18),
                    content=ft.Column([
                        ft.Text("Quick Actions", size=15,
                                weight=ft.FontWeight.BOLD, color="white"),
                        ft.Text("Manage your classroom efficiently",
                                size=11, color="#ccfbf1"),
                    ], spacing=4)
                ),
                ft.Container(
                    bgcolor=c()["card"],
                    border_radius=ft.BorderRadius(0, 0, 12, 12),
                    padding=ft.Padding.only(left=16, right=16, top=16, bottom=16),
                    content=ft.Column([
                        ft.Container(
                            bgcolor=PRIMARY, border_radius=30,
                            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                            content=ft.Row([
                                ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, color="white", size=18),
                                ft.Text("Upload New Lesson", size=13, color="white",
                                        weight=ft.FontWeight.BOLD),
                            ], spacing=10),
                            on_click=qa_upload_lesson,
                        ),
                        qa_outline_btn(ft.Icons.DESCRIPTION_OUTLINED,
                                       "Create Assessment", qa_create_assessment),
                        qa_outline_btn(ft.Icons.PEOPLE_OUTLINE,
                                       "View Student List", qa_view_students),
                        qa_outline_btn(ft.Icons.WORKSPACE_PREMIUM_OUTLINED,
                                       "Issue Certificate", qa_issue_certificate),
                    ], spacing=10)
                ),
            ])
        )

        recent_activity = ft.Container(
            bgcolor=c()["card"], border_radius=12, padding=ft.Padding.all(20),
            shadow=ft.BoxShadow(
                blur_radius=8,
                color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
            ),
            content=ft.Column([
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Recent Activity", size=15, weight=ft.FontWeight.BOLD,
                                color=c()["text"]),
                        ft.IconButton(
                            icon=ft.Icons.MORE_HORIZ, icon_color=c()["muted"],
                            tooltip="More",
                            on_click=lambda e: page.show_dialog(
                                _activity_options_dialog(page, c, switch_page, toast)
                            ),
                        ),
                    ]
                ),
                *activity_items,
                ft.Container(
                    margin=ft.Margin.only(top=8),
                    border=ft.Border.all(1, c()["border"]),
                    border_radius=8,
                    padding=ft.Padding.symmetric(vertical=8),
                    alignment=ft.Alignment(0, 0),
                    on_click=lambda e: page.show_dialog(
                        _all_activities_dialog(page, c, activities)
                    ),
                    content=ft.Text("View All Activities", size=12, color=c()["muted"],
                                    text_align=ft.TextAlign.CENTER),
                )
            ], spacing=4)
        )

        # Date-range picker on the dashboard header
        date_range_label = ft.Text("Last 30 Days", size=12, color=c()["text"])

        def pick_range(label):
            date_range_label.value = label
            page.pop_dialog()
            toast(f"Range: {label}")

        def open_range_picker(_e):
            def opt(label):
                return ft.Container(
                    padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                    border_radius=8,
                    bgcolor=PRIMARY_BG if date_range_label.value == label
                                        else "transparent",
                    on_click=lambda e, l=label: pick_range(l),
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
                    content=ft.Column(spacing=4, tight=True, controls=[
                        opt("Last 7 Days"), opt("Last 30 Days"),
                        opt("Last 90 Days"), opt("Year to Date"), opt("All Time"),
                    ])
                ),
                actions=[ft.TextButton("Close",
                                       on_click=lambda e: page.pop_dialog())],
            )
            page.show_dialog(dlg)

        return ft.Column(
            scroll=ft.ScrollMode.AUTO, spacing=20,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column([
                            ft.Text("Dashboard Overview", size=24,
                                    weight=ft.FontWeight.BOLD, color=c()["text"]),
                            ft.Text(f"Welcome back, Dr. {display_name}. Here is what's happening today.",
                                    size=13, color=c()["muted"]),
                        ], spacing=2),
                        ft.Row([
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color=c()["muted"]),
                                    date_range_label,
                                    ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=14, color=c()["muted"]),
                                ], spacing=6),
                                border=ft.Border.all(1, c()["border"]), border_radius=8,
                                padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                                on_click=open_range_picker,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.OPEN_IN_NEW, icon_size=16,
                                icon_color=c()["muted"],
                                tooltip="Export snapshot",
                                style=ft.ButtonStyle(
                                    side=ft.BorderSide(1, c()["border"]),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                on_click=lambda e: toast("Dashboard snapshot exported"),
                            ),
                        ], spacing=8),
                    ]
                ),

                ft.Row(spacing=16, controls=[
                    stat_card(ft.Icons.PEOPLE_ALT_ROUNDED,        "#2563eb", "#eff6ff",
                              "1,284", "Total Students",          "+12%", "#16a34a"),
                    stat_card(ft.Icons.MENU_BOOK_ROUNDED,         "#7c3aed", "#f5f3ff",
                              "42",    "Total Lessons",           "+3",   "#16a34a"),
                    stat_card(ft.Icons.TASK_ALT_ROUNDED,          PRIMARY,   PRIMARY_BG,
                              "856",   "Completed Assessments",   "+18%", "#16a34a"),
                    stat_card(ft.Icons.WORKSPACE_PREMIUM_ROUNDED, "#ea580c", "#fff7ed",
                              "312",   "Certificates Issued",     "+5%",  "#16a34a"),
                ]),

                ft.Row(spacing=16, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
                    ft.Container(
                        expand=True, bgcolor=c()["card"], border_radius=12,
                        padding=ft.Padding.all(20),
                        shadow=ft.BoxShadow(
                            blur_radius=8,
                            color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                        ),
                        content=ft.Column([
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Column([
                                        ft.Text("Recent Assessment Scores", size=16,
                                                weight=ft.FontWeight.BOLD, color=c()["text"]),
                                        ft.Text("Performance tracking across all active courses",
                                                size=11, color=c()["muted"]),
                                    ], spacing=2),
                                    ft.TextButton(
                                        "View Full Report",
                                        style=ft.ButtonStyle(color=PRIMARY),
                                        on_click=lambda e: switch_page("Analytics"),
                                    ),
                                ]
                            ),
                            ft.Row(controls=[
                                ft.Text("Student",         expand=3, size=11,
                                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                                ft.Text("Lesson Module",   expand=3, size=11,
                                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                                ft.Text("Score",           expand=3, size=11,
                                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                                ft.Text("Completion Date", expand=2, size=11,
                                        weight=ft.FontWeight.BOLD, color=c()["muted"]),
                            ]),
                            *assessment_rows,
                            ft.Row(spacing=24, controls=[
                                ft.Container(
                                    expand=True, bgcolor=c()["field_bg"],
                                    border_radius=10, padding=ft.Padding.all(16),
                                    content=ft.Row([
                                        ft.Container(
                                            bgcolor=ft.Colors.with_opacity(0.13, PRIMARY),
                                            border_radius=8, padding=ft.Padding.all(8),
                                            content=ft.Icon(ft.Icons.SCHOOL_ROUNDED,
                                                            color=PRIMARY, size=20)
                                        ),
                                        ft.Column([
                                            ft.Text("Average Student Grade", size=11,
                                                    color=c()["muted"]),
                                            ft.Text("84.2%", size=22,
                                                    weight=ft.FontWeight.BOLD, color=c()["text"]),
                                        ], spacing=2),
                                    ], spacing=12)
                                ),
                                ft.Container(
                                    expand=True, bgcolor=c()["field_bg"],
                                    border_radius=10, padding=ft.Padding.all(16),
                                    content=ft.Row([
                                        ft.Container(
                                            bgcolor=ft.Colors.with_opacity(0.13, "#2563eb"),
                                            border_radius=8, padding=ft.Padding.all(8),
                                            content=ft.Icon(ft.Icons.TIMER_ROUNDED,
                                                            color="#2563eb", size=20)
                                        ),
                                        ft.Column([
                                            ft.Text("Avg. Completion Time", size=11,
                                                    color=c()["muted"]),
                                            ft.Text("12h 45m", size=22,
                                                    weight=ft.FontWeight.BOLD, color=c()["text"]),
                                        ], spacing=2),
                                    ], spacing=12),
                                ),
                            ])
                        ], spacing=12)
                    ),
                    ft.Container(
                        width=280,
                        content=ft.Column(spacing=16, controls=[quick_actions, recent_activity])
                    ),
                ]),
                ft.Container(height=4),
                page_footer(c),
            ]
        )

    # ─── Layout / navigation ─────────────────────────────
    content_area = ft.Ref[ft.Container]()
    sidebar_nav_refs: dict = {}

    def nav_item(icon, label_text, page_name, active=False):
        ref = ft.Ref[ft.Container]()
        sidebar_nav_refs[page_name] = ref
        return ft.Container(
            ref=ref,
            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            bgcolor=c()["sidebar_active"] if active else "transparent",
            border_radius=8,
            on_click=lambda e, pn=page_name: switch_page(pn),
            content=ft.Row([
                ft.Icon(icon, size=18,
                        color=PRIMARY if active else c()["muted"]),
                ft.Text(label_text, size=13,
                        weight=ft.FontWeight.W_600 if active else ft.FontWeight.NORMAL,
                        color=PRIMARY if active else c()["muted"]),
            ], spacing=10)
        )

    # ── Role-based access control ────────────────────────
    # Maps each protected action/page to the roles that may use it.
    PAGE_ACCESS = {
        "Dashboard":    ["Student", "Instructor", "Admin"],
        "Lessons":      ["Student", "Instructor", "Admin"],   # all may view
        "Assessment":   ["Student", "Instructor"],
        "Analytics":    ["Student", "Instructor", "Admin"],
        "Certificates": ["Student", "Admin"],
        "Management":   ["Admin"],
    }
    # Protected Quick-Action handlers
    QA_ACCESS = {
        "Upload New Lesson":  ["Instructor"],
        "Create Assessment":  ["Instructor"],
        "View Student List":  ["Admin"],
        "Issue Certificate":  ["Admin"],
    }

    def has_access(target: str, table: dict) -> bool:
        return user_role in table.get(target, [])

    def access_denied_view(target: str, allowed):
        return ft.Container(
            expand=True, alignment=ft.Alignment(0, 0),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14,
                controls=[
                    ft.Container(
                        width=80, height=80,
                        bgcolor="#fee2e2", border_radius=40,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(ft.Icons.LOCK_OUTLINE,
                                        size=36, color="#dc2626"),
                    ),
                    ft.Text("Access Denied", size=22,
                            weight=ft.FontWeight.BOLD, color=c()["text"]),
                    ft.Text(f"You are signed in as {user_role}.",
                            size=13, color=c()["muted"]),
                    ft.Text(f"Only {' / '.join(allowed)} can access "
                            f"\u201C{target}\u201D.",
                            size=13, color=c()["muted"]),
                    ft.Container(height=4),
                    ft.ElevatedButton(
                        "Go back to Dashboard",
                        style=ft.ButtonStyle(
                            bgcolor=PRIMARY, color="white",
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        on_click=lambda e: switch_page("Dashboard"),
                    ),
                ]
            )
        )

    def switch_page(page_name):
        current_page["name"] = page_name

        if not has_access(page_name, PAGE_ACCESS):
            allowed = PAGE_ACCESS.get(page_name, [])
            inner = access_denied_view(page_name, allowed)
        elif page_name == "Dashboard":
            inner = build_dashboard_content()
        elif page_name == "Lessons":
            inner = build_lessons_page(page, c)
        elif page_name == "Analytics":
            inner = build_analytics_page(page, c)
        elif page_name == "Certificates":
            inner = build_certificates_page(page, c)
        elif page_name == "Management":
            inner = build_management_page(page, c)
        elif page_name == "Assessment":
            inner = build_assessment_page(page, c, on_back=lambda: switch_page("Lessons"))
        else:
            inner = ft.Text(f"Unknown page: {page_name}")

        content_area.current.content = ft.Container(
            expand=True, padding=ft.Padding.all(24), content=inner,
        )

        # Highlight active nav item
        for pn, ref in sidebar_nav_refs.items():
            is_active = (pn == page_name)
            if ref.current is not None:
                ref.current.bgcolor = c()["sidebar_active"] if is_active else "transparent"
                ref.current.content.controls[0].color = PRIMARY if is_active else c()["muted"]
                ref.current.content.controls[1].color = PRIMARY if is_active else c()["muted"]
                ref.current.content.controls[1].weight = (
                    ft.FontWeight.W_600 if is_active else ft.FontWeight.NORMAL
                )
        page.update()

    def toggle_theme_dash(e):
        page.theme_mode = (
            ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        # Re-render the whole shell to refresh colours
        show_dashboard(page, user_email, on_logout, user_role)

    sidebar = ft.Container(
        width=210, bgcolor=c()["sidebar"],
        border=ft.Border.only(right=ft.BorderSide(1, c()["border"])),
        padding=ft.Padding.symmetric(vertical=20, horizontal=12),
        content=ft.Column(
            expand=True,
            controls=[
                ft.Row([
                    ft.Container(
                        bgcolor=PRIMARY, border_radius=20,
                        padding=ft.Padding.all(8),
                        content=ft.Icon(ft.Icons.SHOW_CHART, color="white", size=18),
                    ),
                    ft.Text("E-Learning\nProgress Analytics", size=12,
                            weight=ft.FontWeight.BOLD, color=PRIMARY),
                ], spacing=8),
                ft.Container(height=20),
                nav_item(ft.Icons.GRID_VIEW_ROUNDED,            "Dashboard",     "Dashboard", active=True),
                nav_item(ft.Icons.MENU_BOOK_ROUNDED,            "Lessons",       "Lessons"),
                nav_item(ft.Icons.QUIZ_OUTLINED,                "Assessment",    "Assessment"),
                nav_item(ft.Icons.BAR_CHART_ROUNDED,            "Analytics",     "Analytics"),
                nav_item(ft.Icons.WORKSPACE_PREMIUM_ROUNDED,    "Certificates",  "Certificates"),
                nav_item(ft.Icons.ADMIN_PANEL_SETTINGS_ROUNDED, "Management",    "Management"),
                ft.Container(expand=True),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=16, vertical=10),
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOGOUT, size=18, color=c()["muted"]),
                        ft.TextButton(
                            "Logout",
                            style=ft.ButtonStyle(color=c()["muted"]),
                            on_click=lambda e: on_logout(),
                        ),
                    ], spacing=4)
                ),
            ]
        )
    )

    topbar = ft.Container(
        bgcolor=c()["card"],
        padding=ft.Padding.symmetric(horizontal=24, vertical=12),
        border=ft.Border.only(bottom=ft.BorderSide(1, c()["border"])),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Container(
                    expand=True,
                    content=ft.TextField(
                        hint_text="Search students, lessons, or scores...",
                        prefix_icon=ft.Icons.SEARCH,
                        border_radius=20, height=40, filled=True,
                        bgcolor=c()["field_bg"], border_color=c()["border"],
                        color=c()["text"], width=360,
                    )
                ),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.NOTIFICATIONS_NONE_ROUNDED,
                        icon_color=c()["muted"],
                        tooltip="Notifications",
                        on_click=lambda e: page.show_dialog(
                            _notifications_dialog(page, c)
                        ),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT
                             else ft.Icons.LIGHT_MODE,
                        icon_color=PRIMARY,
                        on_click=toggle_theme_dash,
                    ),
                    ft.Container(width=1, height=30, bgcolor=c()["border"]),
                    ft.Column([
                        ft.Text(f" {display_name}", size=13,
                                weight=ft.FontWeight.BOLD, color=c()["text"]),
                        ft.Text(user_role.upper(), size=10,
                                weight=ft.FontWeight.BOLD,
                                color={"Admin":      "#dc2626",
                                       "Instructor": PRIMARY,
                                       "Student":    "#2563eb"}.get(user_role, PRIMARY)),
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.END),
                    ft.Container(
                        width=36, height=36, border_radius=18, bgcolor=PRIMARY,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(display_name[0].upper(), color="white",
                                        weight=ft.FontWeight.BOLD),
                    ),
                ], spacing=8),
            ]
        )
    )

    main_content = ft.Container(
        ref=content_area,
        expand=True,
        content=ft.Container(
            expand=True, padding=ft.Padding.all(24),
            content=build_dashboard_content(),
        )
    )

    main_area = ft.Column(expand=True, spacing=0, controls=[topbar, main_content])
    layout    = ft.Row(expand=True, spacing=0,
                       controls=[sidebar, ft.VerticalDivider(width=0), main_area])

    page.controls.clear()
    page.add(layout)
    page.update()


# ── module-level helper dialogs ──────────────────────────
def _create_assessment_dialog(page: ft.Page, c, switch_page, toast):
    title_f = ft.TextField(label="Assessment Title",
                           hint_text="e.g. Final Exam – Calculus II",
                           border_radius=8,
                           bgcolor=c()["field_bg"], border_color=c()["border"])
    course_f = ft.TextField(label="Linked Course",
                            hint_text="e.g. Computer Science 101",
                            border_radius=8,
                            bgcolor=c()["field_bg"], border_color=c()["border"])
    questions_f = ft.TextField(label="Number of Questions", value="10",
                               keyboard_type=ft.KeyboardType.NUMBER,
                               border_radius=8,
                               bgcolor=c()["field_bg"],
                               border_color=c()["border"])
    pass_f = ft.TextField(label="Passing Score (%)", value="70",
                          keyboard_type=ft.KeyboardType.NUMBER,
                          border_radius=8,
                          bgcolor=c()["field_bg"],
                          border_color=c()["border"])
    err = ft.Text("", color="#dc2626", size=11, visible=False)

    def save(_e):
        if not (title_f.value or "").strip():
            err.value = "Title is required"; err.visible = True
            page.update(); return
        try:
            int(questions_f.value or "0")
            int(pass_f.value or "0")
        except ValueError:
            err.value = "Questions and pass score must be numbers"
            err.visible = True
            page.update(); return
        page.pop_dialog()
        toast(f"Assessment \u201c{title_f.value.strip()}\u201d created")
        switch_page("Assessment")

    return ft.AlertDialog(
        modal=True,
        title=ft.Text("Create Assessment", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            width=440,
            content=ft.Column(spacing=12, tight=True, controls=[
                ft.Text("Build a new assessment for one of your courses.",
                        size=12, color=c()["muted"]),
                title_f, course_f,
                ft.Row(spacing=10, controls=[
                    ft.Container(expand=True, content=questions_f),
                    ft.Container(expand=True, content=pass_f),
                ]),
                err,
            ])
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
            ft.ElevatedButton(
                "Create & Open",
                style=ft.ButtonStyle(
                    bgcolor=PRIMARY, color="white",
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                on_click=save,
            ),
        ],
    )


def _activity_options_dialog(page: ft.Page, c, switch_page, toast):
    def go(target):
        page.pop_dialog()
        switch_page(target)

    def opt(icon, label, on_click):
        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            border_radius=8,
            on_click=on_click,
            content=ft.Row(spacing=10, controls=[
                ft.Icon(icon, size=18, color=c()["muted"]),
                ft.Text(label, size=13, color=c()["text"]),
            ]),
        )
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Activity Options", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            width=300,
            content=ft.Column(spacing=4, tight=True, controls=[
                opt(ft.Icons.BAR_CHART_ROUNDED, "Open Analytics",
                    lambda e: go("Analytics")),
                opt(ft.Icons.MARK_EMAIL_READ_OUTLINED, "Mark all as read",
                    lambda e: (page.pop_dialog(), toast("Activity feed cleared"))),
                opt(ft.Icons.FILE_DOWNLOAD_OUTLINED, "Export feed (CSV)",
                    lambda e: (page.pop_dialog(),
                               toast("Activity feed exported"))),
            ])
        ),
        actions=[ft.TextButton("Close", on_click=lambda e: page.pop_dialog())],
    )
    return dlg


def _all_activities_dialog(page: ft.Page, c, activities):
    items = []
    for ini, name, action, time in activities:
        items.append(
            ft.Container(
                padding=ft.Padding.symmetric(vertical=10, horizontal=8),
                border=ft.Border.only(bottom=ft.BorderSide(1, c()["border"])),
                content=ft.Row(spacing=10, controls=[
                    avatar(ini, size=34),
                    ft.Column(spacing=1, expand=True, controls=[
                        ft.Text(name,   size=13, weight=ft.FontWeight.W_600,
                                color=c()["text"]),
                        ft.Text(action, size=11, color=c()["muted"]),
                        ft.Text(time,   size=10, color=PRIMARY),
                    ]),
                ])
            )
        )
    return ft.AlertDialog(
        modal=True,
        title=ft.Text("All Activities", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            width=440, height=420,
            content=ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO,
                              controls=items),
        ),
        actions=[ft.TextButton("Close", on_click=lambda e: page.pop_dialog())],
    )


def _notifications_dialog(page: ft.Page, c):
    notes = [
        ("New assessment submission",
         "Helena Troy submitted Calculus II Final.",
         "15 mins ago", ft.Icons.QUIZ_OUTLINED, "#2563eb"),
        ("Certificate issued",
         "Sophie Chen earned Data Science Pro certificate.",
         "3 hours ago", ft.Icons.WORKSPACE_PREMIUM_ROUNDED, "#16a34a"),
        ("Course threshold reached",
         "Python for Automation just hit 100 enrolments.",
         "Yesterday", ft.Icons.TRENDING_UP, "#7c3aed"),
        ("System update",
         "Analytics pipeline finished its nightly refresh.",
         "Yesterday", ft.Icons.HEALTH_AND_SAFETY_OUTLINED, PRIMARY),
    ]
    items = []
    for title, body, when, icon, color in notes:
        items.append(ft.Container(
            padding=ft.Padding.symmetric(vertical=10, horizontal=8),
            border=ft.Border.only(bottom=ft.BorderSide(1, c()["border"])),
            content=ft.Row(spacing=12, controls=[
                ft.Container(
                    bgcolor=ft.Colors.with_opacity(0.12, color),
                    border_radius=8,
                    padding=ft.Padding.all(8),
                    content=ft.Icon(icon, size=18, color=color),
                ),
                ft.Column(spacing=2, expand=True, controls=[
                    ft.Text(title, size=13, weight=ft.FontWeight.W_600,
                            color=c()["text"]),
                    ft.Text(body, size=11, color=c()["muted"]),
                    ft.Text(when, size=10, color=PRIMARY),
                ]),
            ])
        ))
    return ft.AlertDialog(
        modal=True,
        title=ft.Text("Notifications", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            width=440, height=380,
            content=ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO,
                              controls=items),
        ),
        actions=[
            ft.TextButton("Mark all read",
                          on_click=lambda e: (
                              page.pop_dialog(),
                              page.show_dialog(ft.SnackBar(
                                  content=ft.Text("All notifications marked as read",
                                                  color="white"),
                                  bgcolor=PRIMARY)),
                          )),
            ft.ElevatedButton(
                "Close",
                style=ft.ButtonStyle(
                    bgcolor=PRIMARY, color="white",
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                on_click=lambda e: page.pop_dialog(),
            ),
        ],
    )