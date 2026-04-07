import flet as ft
from theme import get_colors


def show_dashboard(page: ft.Page, user_email: str, on_logout):
 
    page.window.width = 1100
    page.window.height = 750
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.vertical_alignment = ft.MainAxisAlignment.START

    def c():
        return get_colors(page)

    page.bgcolor = c()["bg"]
    page.controls.clear()

    name_part = user_email.split("@")[0].replace(".", " ").title()
    display_name = name_part if name_part else "Instructor"

    # ── stat card helper 
    def stat_card(icon, icon_color, icon_bg, value, label, badge, badge_color):
        return ft.Container(
            expand=True,
            padding=20, bgcolor=c()["card"], border_radius=12,
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK12),
            content=ft.Column([
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Container(
                            bgcolor=icon_bg, border_radius=8, padding=8,
                            content=ft.Icon(icon, color=icon_color, size=20)
                        ),
                        ft.Container(
                            content=ft.Text(badge, size=11,
                                            weight=ft.FontWeight.BOLD,
                                            color=badge_color),
                            bgcolor=f"{badge_color}22",
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=20
                        )
                    ]
                ),
                ft.Text(value, size=26, weight=ft.FontWeight.BOLD, color=c()["text"]),
                ft.Text(label, size=12, color=c()["muted"])
            ], spacing=6)
        )

    # ── assessment rows 
    students_data = [
        ("Emma Watson",  "Quantum Physics Intro",  "Excellent: 92%",     "#16a34a", "May 24, 2024"),
        ("John Boyega",  "Deep Learning Basics",   "Good: 78%",          "#2563eb", "May 23, 2024"),
        ("Oscar Isaac",  "Macroeconomics 101",      "Needs Review: 55%",  "#dc2626", "May 23, 2024"),
        ("Daisy Ridley", "UI/UX Design Systems",    "Excellent: 88%",     "#16a34a", "May 22, 2024"),
        ("Adam Driver",  "Mobile App Security",     "Good: 64%",          "#2563eb", "May 21, 2024"),
    ]

    def score_chip(text, color):
        if "Needs" in text:
            return ft.Container(
                content=ft.Text(text, size=11, weight=ft.FontWeight.BOLD, color="white"),
                bgcolor=color, border_radius=20,
                padding=ft.padding.symmetric(horizontal=10, vertical=4)
            )
        return ft.Text(text, size=12, weight=ft.FontWeight.W_500, color=color)

    assessment_rows = []
    for name, module, score, score_color, date in students_data:
        initials = "".join(n[0] for n in name.split()[:2]).upper()
        assessment_rows.append(ft.Container(
            padding=ft.padding.symmetric(vertical=10, horizontal=4),
            border=ft.border.only(bottom=ft.BorderSide(1, c()["border"])),
            content=ft.Row(controls=[
                ft.Row(expand=3, controls=[
                    ft.Container(
                        width=34, height=34, border_radius=17,
                        bgcolor="#0f766e22",
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(initials, size=12,
                                        weight=ft.FontWeight.BOLD, color="#0f766e")
                    ),
                    ft.Text(name, size=13, color=c()["text"],
                            weight=ft.FontWeight.W_500)
                ]),
                ft.Text(module, expand=3, size=12, color=c()["muted"]),
                ft.Container(expand=3, content=score_chip(score, score_color)),
                ft.Text(date, expand=2, size=12, color=c()["muted"])
            ])
        ))

    # ── recent activity 
    activities = [
        ("MA", "Marcus Aurelius", "Completed Lesson: Advanced React Patterns", "2 MINS AGO"),
        ("HT", "Helena Troy",    "Submitted Assessment: Calculus II Final",    "15 MINS AGO"),
        ("JB", "Julian Black",   "Started Lesson: Introduction to Figma",      "1 HOUR AGO"),
        ("SC", "Sophie Chen",    "Earned Certificate: Data Science Pro",        "3 HOURS AGO"),
        ("LN", "Liam Neeson",    "Joined Course: Python for Automation",        "5 HOURS AGO"),
    ]

    activity_items = []
    for initials, name, action, time in activities:
        activity_items.append(ft.Container(
            padding=ft.padding.symmetric(vertical=8),
            content=ft.Row([
                ft.Container(
                    width=36, height=36, border_radius=18,
                    bgcolor="#0f766e22",
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(initials, size=12,
                                    weight=ft.FontWeight.BOLD, color="#0f766e")
                ),
                ft.Column([
                    ft.Text(name, size=13, weight=ft.FontWeight.W_600, color=c()["text"]),
                    ft.Text(action, size=11, color=c()["muted"]),
                    ft.Text(time, size=10, color="#0f766e")
                ], spacing=1, expand=True)
            ], spacing=10)
        ))

    # ── sidebar 
    def nav_item(icon, label, active=False):
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            bgcolor="#f0fdf9" if active else "transparent",
            border_radius=8,
            content=ft.Row([
                ft.Icon(icon, size=18,
                        color="#0f766e" if active else c()["muted"]),
                ft.Text(label, size=13,
                        weight=ft.FontWeight.W_600 if active else ft.FontWeight.NORMAL,
                        color="#0f766e" if active else c()["muted"])
            ], spacing=10)
        )

    sidebar = ft.Container(
        width=200, bgcolor=c()["sidebar"],
        border=ft.border.only(right=ft.BorderSide(1, c()["border"])),
        padding=ft.padding.symmetric(vertical=20, horizontal=12),
        content=ft.Column(
            expand=True,
            controls=[
                ft.Row([
                    ft.Container(
                        bgcolor="#0f766e", border_radius=20, padding=8,
                        content=ft.Icon(ft.Icons.SHOW_CHART, color="white", size=18)
                    ),
                    ft.Text("Lumina Learn", size=16,
                            weight=ft.FontWeight.BOLD, color="#0f766e")
                ], spacing=8),
                ft.Container(height=20),
                nav_item(ft.Icons.GRID_VIEW_ROUNDED,         "Dashboard",    active=True),
                nav_item(ft.Icons.MENU_BOOK_ROUNDED,         "Lessons"),
                nav_item(ft.Icons.BAR_CHART_ROUNDED,         "Analytics"),
                nav_item(ft.Icons.WORKSPACE_PREMIUM_ROUNDED, "Certificates"),
                ft.Container(expand=True),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOGOUT, size=18, color=c()["muted"]),
                        ft.TextButton(
                            "Logout",
                            style=ft.ButtonStyle(color=c()["muted"]),
                            on_click=lambda e: on_logout()
                        )
                    ], spacing=4)
                )
            ]
        )
    )

    # ── topbar 
    def toggle_theme_dash(e):
        page.theme_mode = (
            ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        show_dashboard(page, user_email, on_logout)

    topbar = ft.Container(
        bgcolor=c()["card"],
        padding=ft.padding.symmetric(horizontal=24, vertical=12),
        border=ft.border.only(bottom=ft.BorderSide(1, c()["border"])),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Container(
                    expand=True,
                    content=ft.TextField(
                        hint_text="Search students, lessons, or scores...",
                        prefix_icon=ft.Icons.SEARCH,
                        border_radius=20, height=40, filled=True,
                        bgcolor=c()["field_bg"],
                        border_color=c()["border"],
                        color=c()["text"],
                        width=340
                    )
                ),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.NOTIFICATIONS_NONE_ROUNDED,
                        icon_color=c()["muted"]
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT
                        else ft.Icons.LIGHT_MODE,
                        icon_color="#0f766e",
                        on_click=toggle_theme_dash
                    ),
                    ft.Container(width=1, height=30, bgcolor=c()["border"]),
                    ft.Column([
                        ft.Text(f" {display_name}", size=13,
                                weight=ft.FontWeight.BOLD, color=c()["text"]),
                        ft.Text("INSTRUCTOR", size=10,
                                weight=ft.FontWeight.BOLD, color="#0f766e")
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.END),
                    ft.Container(
                        width=36, height=36, border_radius=18,
                        bgcolor="#0f766e",
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(display_name[0].upper(), color="white",
                                        weight=ft.FontWeight.BOLD)
                    )
                ], spacing=8)
            ]
        )
    )

    # ── quick actions card 
    def qa_outline_btn(icon, label):
        return ft.Container(
            bgcolor="transparent",
            border=ft.border.all(1.5, "#0f766e"),
            border_radius=30,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            content=ft.Row([
                ft.Icon(icon, color="#0f766e", size=18),
                ft.Text(label, size=13, color="#0f766e", weight=ft.FontWeight.W_600)
            ], spacing=10)
        )

   
    quick_actions = ft.Container(
        bgcolor="#0f766e",
        border_radius=12,
        shadow=ft.BoxShadow(
            blur_radius=12, spread_radius=0,
            offset=ft.Offset(0, 4),
            color=ft.Colors.with_opacity(0.10, ft.Colors.BLACK)
        ),
        content=ft.Column(
            spacing=0,
            tight=True,
            controls=[
                # Header text 
                ft.Container(
                    padding=ft.padding.only(left=20, right=20, top=18, bottom=18),
                    content=ft.Column([
                        ft.Text("Quick Actions",
                                size=15, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Text("Manage your classroom efficiently",
                                size=11, color="#ccfbf1"),
                    ], spacing=4)
                ),
        
                ft.Container(
                    bgcolor=c()["card"],
                    border_radius=ft.BorderRadius(
                        top_left=0, top_right=0,
                        bottom_left=12, bottom_right=12
                    ),
                    padding=ft.padding.only(left=16, right=16, top=16, bottom=16),
                    content=ft.Column([
                        ft.Container(
                            bgcolor="#0f766e",
                            border_radius=30,
                            padding=ft.padding.symmetric(horizontal=16, vertical=12),
                            content=ft.Row([
                                ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE,
                                        color="white", size=18),
                                ft.Text("Upload New Lesson",
                                        size=13, color="white",
                                        weight=ft.FontWeight.BOLD)
                            ], spacing=10)
                        ),
                        qa_outline_btn(ft.Icons.DESCRIPTION_OUTLINED,      "Create Assessment"),
                        qa_outline_btn(ft.Icons.PEOPLE_OUTLINE,             "View Student List"),
                        qa_outline_btn(ft.Icons.WORKSPACE_PREMIUM_OUTLINED, "Issue Certificate"),
                    ], spacing=10)
                ),
            ]
        )
    )

    
    recent_activity = ft.Container(
        bgcolor=c()["card"], border_radius=12, padding=20,
        shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK12),
        content=ft.Column([
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Recent Activity", size=15,
                            weight=ft.FontWeight.BOLD, color=c()["text"]),
                    ft.Icon(ft.Icons.MORE_HORIZ, color=c()["muted"])
                ]
            ),
            *activity_items,
            ft.Container(
                margin=ft.margin.only(top=8),
                border=ft.border.all(1, c()["border"]),
                border_radius=8,
                padding=ft.padding.symmetric(vertical=8),
                alignment=ft.Alignment(0, 0),
                content=ft.Text("View All Activities",
                                size=12, color=c()["muted"],
                                text_align="center")
            )
        ], spacing=4)
    )

   
    content = ft.Container(
        expand=True,
        padding=24,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[
                # Page header
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column([
                            ft.Text("Dashboard Overview", size=24,
                                    weight=ft.FontWeight.BOLD, color=c()["text"]),
                            ft.Text(f"Welcome back, {display_name}. "
                                    "Here is what's happening today.",
                                    size=13, color=c()["muted"])
                        ], spacing=2),
                        ft.Row([
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.CALENDAR_TODAY,
                                            size=14, color=c()["muted"]),
                                    ft.Text("Last 30 Days", size=12, color=c()["text"])
                                ], spacing=6),
                                border=ft.border.all(1, c()["border"]),
                                border_radius=8,
                                padding=ft.padding.symmetric(horizontal=14, vertical=8)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.OPEN_IN_NEW,
                                icon_size=16,
                                icon_color=c()["muted"],
                                style=ft.ButtonStyle(
                                    side=ft.BorderSide(1, c()["border"]),
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                )
                            )
                        ], spacing=8)
                    ]
                ),

                # Stat cards
                ft.Row(spacing=16, controls=[
                    stat_card(ft.Icons.PEOPLE_ALT_ROUNDED,           "#2563eb", "#eff6ff",
                              "1,284", "Total Students",        "+12%", "#16a34a"),
                    stat_card(ft.Icons.MENU_BOOK_ROUNDED,            "#7c3aed", "#f5f3ff",
                              "42",    "Total Lessons",         "+3",   "#16a34a"),
                    stat_card(ft.Icons.TASK_ALT_ROUNDED,             "#0f766e", "#f0fdf9",
                              "856",   "Completed Assessments", "+18%", "#16a34a"),
                    stat_card(ft.Icons.WORKSPACE_PREMIUM_ROUNDED,    "#ea580c", "#fff7ed",
                              "312",   "Certificates Issued",   "+5%",  "#16a34a"),
                ]),

                # Assessment table + right panel
                ft.Row(
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        # Assessment table
                        ft.Container(
                            expand=True,
                            bgcolor=c()["card"], border_radius=12, padding=20,
                            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK12),
                            content=ft.Column([
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Column([
                                            ft.Text("Recent Assessment Scores",
                                                    size=16, weight=ft.FontWeight.BOLD,
                                                    color=c()["text"]),
                                            ft.Text("Performance tracking across all active courses",
                                                    size=11, color=c()["muted"])
                                        ], spacing=2),
                                        ft.TextButton("View Full Report",
                                                      style=ft.ButtonStyle(color="#0f766e"))
                                    ]
                                ),
                                # Column headers
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
                                # Summary stats
                                ft.Row(spacing=24, controls=[
                                    ft.Container(
                                        expand=True,
                                        bgcolor=c()["field_bg"],
                                        border_radius=10, padding=16,
                                        content=ft.Row([
                                            ft.Container(
                                                bgcolor="#0f766e22", border_radius=8, padding=8,
                                                content=ft.Icon(ft.Icons.SCHOOL_ROUNDED,
                                                                color="#0f766e", size=20)
                                            ),
                                            ft.Column([
                                                ft.Text("Average Student Grade",
                                                        size=11, color=c()["muted"]),
                                                ft.Text("84.2%", size=22,
                                                        weight=ft.FontWeight.BOLD,
                                                        color=c()["text"])
                                            ], spacing=2)
                                        ], spacing=12)
                                    ),
                                    ft.Container(
                                        expand=True,
                                        bgcolor=c()["field_bg"],
                                        border_radius=10, padding=16,
                                        content=ft.Row([
                                            ft.Container(
                                                bgcolor="#2563eb22", border_radius=8, padding=8,
                                                content=ft.Icon(ft.Icons.TIMER_ROUNDED,
                                                                color="#2563eb", size=20)
                                            ),
                                            ft.Column([
                                                ft.Text("Avg. Completion Time",
                                                        size=11, color=c()["muted"]),
                                                ft.Text("12h 45m", size=22,
                                                        weight=ft.FontWeight.BOLD,
                                                        color=c()["text"])
                                            ], spacing=2)
                                        ], spacing=12)
                                    ),
                                ])
                            ], spacing=12)
                        ),

                        # Right panel
                        ft.Container(
                            width=260,
                            content=ft.Column(
                                spacing=16,
                                controls=[
                                    quick_actions,
                                    recent_activity,
                                ]
                            )
                        )
                    ]
                ),

                # Footer
                ft.Container(height=4),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("© 2026 E-Learning Progress Analytics. All rights reserved.",
                                size=11, color=c()["muted"]),
                        ft.Row([
                            ft.TextButton("Privacy Policy",
                                          style=ft.ButtonStyle(color=c()["muted"])),
                            ft.TextButton("Support",
                                          style=ft.ButtonStyle(color=c()["muted"]))
                        ])
                    ]
                )
            ]
        )
    )

    # ── assemble 
    main_area = ft.Column(expand=True, spacing=0, controls=[topbar, content])
    layout = ft.Row(
        expand=True, spacing=0,
        controls=[sidebar, ft.VerticalDivider(width=0), main_area]
    )

    page.controls.clear()
    page.add(layout)
    page.update()