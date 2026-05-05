import re
import flet as ft
from theme import get_colors, PRIMARY
from database import register_user
import requests

API_URL = "http://127.0.0.1:8000"

MIN_PASSWORD_LENGTH = 6
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def build_register(page: ft.Page, on_register_success, on_go_login):
    page.window.width  = 500
    page.window.height = 720
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment   = ft.MainAxisAlignment.CENTER

    def c():
        return get_colors(page)

    # ── status banner ────────────────────────────────────
    banner_text = ft.Text("", size=12)
    banner = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.ERROR_OUTLINE, size=16),
            banner_text,
        ], spacing=8),
        padding=ft.Padding.symmetric(horizontal=12, vertical=8),
        border_radius=8,
        visible=False,
    )

    def show_banner(msg, success=False):
        if success:
            banner_text.color = "#166534"
            banner.bgcolor = "#dcfce7"
            banner.content.controls[0].name  = ft.Icons.CHECK_CIRCLE_OUTLINE
            banner.content.controls[0].color = "#16a34a"
        else:
            banner_text.color = "#b91c1c"
            banner.bgcolor = "#fee2e2"
            banner.content.controls[0].name  = ft.Icons.ERROR_OUTLINE
            banner.content.controls[0].color = "#b91c1c"
        banner_text.value = msg
        banner.visible = True

    def hide_banner():
        banner.visible = False

    # ── fields ───────────────────────────────────────────
    name_field = ft.TextField(
        hint_text="Name Surname",
        border_radius=8, height=45, filled=True,
        bgcolor=c()["field_bg"], border_color=c()["border"],
    )
    email_field = ft.TextField(
        hint_text="name@institution.edu",
        border_radius=8, height=45, filled=True,
        bgcolor=c()["field_bg"], border_color=c()["border"],
        keyboard_type=ft.KeyboardType.EMAIL,
    )
    password_field = ft.TextField(
        hint_text="Minimum 6 characters",
        password=True, can_reveal_password=True,
        border_radius=8, height=45, filled=True,
        bgcolor=c()["field_bg"], border_color=c()["border"],
    )
    confirm_field = ft.TextField(
        hint_text="Confirm password",
        password=True, can_reveal_password=True,
        border_radius=8, height=45, filled=True,
        bgcolor=c()["field_bg"], border_color=c()["border"],
    )

    name_error    = ft.Text("", color="#dc2626", size=11, visible=False)
    email_error   = ft.Text("", color="#dc2626", size=11, visible=False)
    pass_error    = ft.Text("", color="#dc2626", size=11, visible=False)
    confirm_error = ft.Text("", color="#dc2626", size=11, visible=False)

    def ferr(field, label, msg):
        field.border_color = "#dc2626"
        label.value = msg
        label.visible = bool(msg)

    def fok(field, label):
        field.border_color = c()["border"]
        label.visible = False

    def on_name_change(e):
        if (name_field.value or "").strip():
            fok(name_field, name_error)
        hide_banner()
        page.update()

    def on_email_change(e):
        v = (email_field.value or "").strip()
        if v and not EMAIL_REGEX.match(v):
            ferr(email_field, email_error, "Please enter a valid e-mail")
        else:
            fok(email_field, email_error)
        hide_banner()
        page.update()

    def on_pass_change(e):
        v = password_field.value or ""
        if v and len(v) < MIN_PASSWORD_LENGTH:
            ferr(password_field, pass_error,
                 f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
        else:
            fok(password_field, pass_error)
        if confirm_field.value:
            on_confirm_change(None)
        hide_banner()
        page.update()

    def on_confirm_change(e):
        if confirm_field.value and confirm_field.value != password_field.value:
            ferr(confirm_field, confirm_error, "Passwords do not match")
        else:
            fok(confirm_field, confirm_error)
        if e is not None:
            hide_banner()
            page.update()

    name_field.on_change     = on_name_change
    email_field.on_change    = on_email_change
    password_field.on_change = on_pass_change
    confirm_field.on_change  = on_confirm_change

    # ── submit ───────────────────────────────────────────
    def register_click(e):
        nv = (name_field.value or "").strip()
        ev = (email_field.value or "").strip()
        pv = password_field.value or ""
        cv = confirm_field.value or ""
        ok = True

        if not nv:
            ferr(name_field, name_error, "Name cannot be empty")
            ok = False
        else:
            fok(name_field, name_error)

        if not ev:
            ferr(email_field, email_error, "E-mail cannot be empty")
            ok = False
        elif not EMAIL_REGEX.match(ev):
            ferr(email_field, email_error, "Please enter a valid e-mail")
            ok = False
        else:
            fok(email_field, email_error)

        if not pv:
            ferr(password_field, pass_error, "Password cannot be empty")
            ok = False
        elif len(pv) < MIN_PASSWORD_LENGTH:
            ferr(password_field, pass_error,
                 f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
            ok = False
        else:
            fok(password_field, pass_error)

        if not cv:
            ferr(confirm_field, confirm_error, "Please re-enter your password")
            ok = False
        elif cv != pv:
            ferr(confirm_field, confirm_error, "Passwords do not match")
            ok = False
        else:
            fok(confirm_field, confirm_error)

        page.update()
        if not ok:
            return

        # Try the API first
        try:
            r = requests.post(f"{API_URL}/register",
                              json={"email": ev, "name": nv, "password": pv},
                              timeout=2)
            api_result = r.json()
        except Exception:
            api_result = None

        if api_result is not None:
            if "detail" in api_result:
                show_banner(api_result["detail"])
                page.update()
                return
            # success
            show_banner("Registration completed successfully! Redirecting...", success=True)
            page.update()
            import time; time.sleep(1.0)
            on_register_success(ev)
            return

        # API offline → fall back to local SQLite
        success, err_msg = register_user(ev, nv, pv)
        if success:
            show_banner("Registration completed successfully! Redirecting...", success=True)
            page.update()
            import time; time.sleep(1.0)
            on_register_success(ev)
        else:
            show_banner(err_msg)
            page.update()

    for f in [name_field, email_field, password_field, confirm_field]:
        f.on_submit = register_click

    # ── theme toggle ─────────────────────────────────────
    def toggle_theme(e):
        page.theme_mode = (
            ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        theme_btn.icon = (
            ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.Icons.LIGHT_MODE
        )
        page.bgcolor = c()["bg"]
        card.bgcolor = c()["card"]
        for f in [name_field, email_field, password_field, confirm_field]:
            f.bgcolor = c()["field_bg"]
            f.color   = c()["text"]
            if f.border_color != "#dc2626":
                f.border_color = c()["border"]
        page.update()

    theme_btn = ft.IconButton(
        icon=ft.Icons.DARK_MODE, on_click=toggle_theme, icon_color=PRIMARY
    )

    def label(text):
        return ft.Text(text, size=11, weight=ft.FontWeight.BOLD, color="#6b7280")

    card = ft.Container(
        width=400, padding=30,
        bgcolor=c()["card"], border_radius=16,
        shadow=ft.BoxShadow(blur_radius=20, spread_radius=1,
                            color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        content=ft.Column(
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
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

                ft.Text("Create Account", size=22,
                        weight=ft.FontWeight.BOLD, color=c()["text"]),
                ft.Text("Sign up and join the platform",
                        size=12, color=c()["muted"], text_align=ft.TextAlign.CENTER),

                ft.Container(width=340, content=banner),

                ft.Container(width=340, content=ft.Column([label("NAME SURNAME"),     name_field,     name_error],    spacing=4)),
                ft.Container(width=340, content=ft.Column([label("EMAIL"),            email_field,    email_error],   spacing=4)),
                ft.Container(width=340, content=ft.Column([label("PASSWORD"),         password_field, pass_error],    spacing=4)),
                ft.Container(width=340, content=ft.Column([label("CONFIRM PASSWORD"), confirm_field,  confirm_error], spacing=4)),

                ft.ElevatedButton(
                    "Register", width=340, height=45,
                    style=ft.ButtonStyle(
                        bgcolor=PRIMARY, color="white",
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    on_click=register_click,
                ),

                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Already have an account?",
                                size=12, color=c()["muted"]),
                        ft.TextButton(
                            "Sign In",
                            style=ft.ButtonStyle(color=PRIMARY),
                            on_click=lambda e: on_go_login(),
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