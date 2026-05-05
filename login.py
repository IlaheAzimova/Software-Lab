import re
import flet as ft
import requests
from theme import get_colors, PRIMARY
from database import check_credentials

API_URL = "http://127.0.0.1:8000"

MIN_PASSWORD_LENGTH = 6
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def build_login(page: ft.Page, on_login_success, on_go_register):
    page.window.width  = 500
    page.window.height = 680
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment   = ft.MainAxisAlignment.CENTER

    def c():
        return get_colors(page)

    # ── error banner ─────────────────────────────────────
    error_text = ft.Text("", color="#b91c1c", size=12)
    error_box = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.ERROR_OUTLINE, color="#b91c1c", size=16),
            error_text,
        ], spacing=8),
        bgcolor="#fee2e2",
        padding=ft.Padding.symmetric(horizontal=12, vertical=8),
        border_radius=8,
        visible=False,
    )

    # ── fields ───────────────────────────────────────────
    email_field = ft.TextField(
        hint_text="name@institution.edu",
        border_radius=8, height=45, filled=True,
        bgcolor=c()["field_bg"], border_color=c()["border"],
        keyboard_type=ft.KeyboardType.EMAIL,
    )
    password_field = ft.TextField(
        hint_text="Enter password",
        password=True, can_reveal_password=True,
        border_radius=8, height=45, filled=True,
        bgcolor=c()["field_bg"], border_color=c()["border"],
    )

    email_error    = ft.Text("", color="#dc2626", size=11, visible=False)
    password_error = ft.Text("", color="#dc2626", size=11, visible=False)

    def show_banner(msg):
        error_text.value = msg
        error_box.visible = True

    def hide_banner():
        error_box.visible = False

    def ferr(field, label, msg):
        field.border_color = "#dc2626"
        label.value = msg
        label.visible = bool(msg)

    def fok(field, label):
        field.border_color = c()["border"]
        label.visible = False

    def on_email_change(e):
        v = (email_field.value or "").strip()
        if v and not EMAIL_REGEX.match(v):
            ferr(email_field, email_error, "Enter a correct e-mail (e.g. name@domain.com)")
        else:
            fok(email_field, email_error)
        hide_banner()
        page.update()

    def on_password_change(e):
        v = password_field.value or ""
        if v and len(v) < MIN_PASSWORD_LENGTH:
            ferr(password_field, password_error,
                 f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
        else:
            fok(password_field, password_error)
        hide_banner()
        page.update()

    email_field.on_change    = on_email_change
    password_field.on_change = on_password_change

    # ── submit handler ───────────────────────────────────
    def login_click(e):
        ev = (email_field.value or "").strip()
        pv = (password_field.value or "").strip()
        ok = True

        if not ev:
            ferr(email_field, email_error, "E-mail cannot be empty")
            ok = False
        elif not EMAIL_REGEX.match(ev):
            ferr(email_field, email_error, "Please enter a valid e-mail")
            ok = False
        else:
            fok(email_field, email_error)

        if not pv:
            ferr(password_field, password_error, "Password cannot be empty")
            ok = False
        elif len(pv) < MIN_PASSWORD_LENGTH:
            ferr(password_field, password_error,
                 f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
            ok = False
        else:
            fok(password_field, password_error)

        if not ok:
            page.update()
            return

        # Try the FastAPI server first
        try:
            r = requests.post(f"{API_URL}/login",
                              json={"email": ev, "password": pv},
                              timeout=2)
            result = r.json()
        except Exception:
            result = None

        if result is not None:
            # API responded
            if "detail" in result:
                show_banner(result["detail"])
                page.update()
                return
            else:
                hide_banner()
                page.update()
                on_login_success(result["user"]["email"])
                return

        # API unreachable – fall back to local SQLite check
        user = check_credentials(ev, pv)
        if user is None:
            show_banner("Invalid credentials")
        else:
            hide_banner()
            page.update()
            on_login_success(user["email"])
            return

        page.update()

    email_field.on_submit    = login_click
    password_field.on_submit = login_click

    # ── theme & static texts ─────────────────────────────
    welcome_text = ft.Text("Welcome back", size=22,
                           weight=ft.FontWeight.BOLD, color=c()["text"])
    subtitle_text = ft.Text("Enter your credentials to access your dashboard",
                            size=12, color=c()["muted"], text_align=ft.TextAlign.CENTER)

    def toggle_theme(e):
        page.theme_mode = (
            ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        page.bgcolor       = c()["bg"]
        card.bgcolor       = c()["card"]
        welcome_text.color = c()["text"]
        subtitle_text.color = c()["muted"]
        for f in [email_field, password_field]:
            f.bgcolor = c()["field_bg"]
            f.color   = c()["text"]
            if f.border_color != "#dc2626":
                f.border_color = c()["border"]
        theme_btn.icon = (
            ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.Icons.LIGHT_MODE
        )
        page.update()

    theme_btn = ft.IconButton(
        icon=ft.Icons.DARK_MODE, on_click=toggle_theme, icon_color=PRIMARY
    )

    # ── card ─────────────────────────────────────────────
    card = ft.Container(
        width=400, padding=30,
        bgcolor=c()["card"], border_radius=16,
        shadow=ft.BoxShadow(blur_radius=20, spread_radius=1,
                            color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        content=ft.Column(
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                # Brand + theme toggle
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(controls=[
                            ft.Container(
                                bgcolor=PRIMARY, border_radius=20, padding=8,
                                content=ft.Icon(ft.Icons.SHOW_CHART, color="white", size=18)
                            ),
                            ft.Text("E-Learning Progress Analytics", size=15,
                                    weight=ft.FontWeight.BOLD, color=PRIMARY),
                        ], spacing=8),
                        theme_btn,
                    ]
                ),

                welcome_text,
                subtitle_text,
                ft.Container(width=340, content=error_box),

                # Email
                ft.Container(
                    width=340,
                    content=ft.Column([
                        ft.Text("EMAIL OR USERNAME", size=11,
                                weight=ft.FontWeight.BOLD, color="#6b7280"),
                        email_field,
                        email_error,
                    ], spacing=4),
                ),

                # Password
                ft.Container(
                    width=340,
                    content=ft.Column([
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("PASSWORD", size=11,
                                        weight=ft.FontWeight.BOLD, color="#6b7280"),
                                ft.TextButton("Forgot password?",
                                              style=ft.ButtonStyle(color=PRIMARY)),
                            ]
                        ),
                        password_field,
                        password_error,
                    ], spacing=4),
                ),

                # Submit
                ft.ElevatedButton(
                    "Sign In", width=340, height=45,
                    style=ft.ButtonStyle(
                        bgcolor=PRIMARY, color="white",
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    on_click=login_click,
                ),

                ft.Divider(height=6, color="#e5e7eb"),

                # Role-based notice
                ft.Container(
                    padding=ft.Padding.all(4),
                    content=ft.Row(controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, color=PRIMARY, size=16),
                        ft.Column([
                            ft.Text("ROLE-BASED LOGIN", size=10,
                                    weight=ft.FontWeight.BOLD, color=c()["muted"]),
                            ft.Text("Administrators should use the Institutional SSO. "
                                    "Instructors and Students can login with their portal credentials.",
                                    size=10, color=c()["muted"]),
                        ], spacing=2, expand=True),
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.START),
                ),

                # Go to register
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Don't have an account?", size=12, color=c()["muted"]),
                        ft.TextButton(
                            "Register",
                            style=ft.ButtonStyle(color=PRIMARY),
                            on_click=lambda e: on_go_register(),
                        ),
                    ]
                ),
            ]
        )
    )

    page.bgcolor = c()["bg"]
    page.controls.clear()
    page.add(card)
    page.update()