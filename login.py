import re
import flet as ft
from theme import get_colors
from database import check_credentials

MIN_PASSWORD_LENGTH = 6
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def build_login(page: ft.Page, on_login_success, on_go_register):

    page.window.width = 500
    page.window.height = 640
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def c():
        return get_colors(page)

    
    error_text = ft.Text("", color="#b91c1c", size=12)
    error_box = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.ERROR_OUTLINE, color="#b91c1c", size=16),
            error_text,
        ], spacing=8),
        bgcolor="#fee2e2",
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border_radius=8,
        visible=False,
    )

    # ── Fields 
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
        v = email_field.value.strip()
        if v and not EMAIL_REGEX.match(v):
            ferr(email_field, email_error, "Enter correct e-mail  (ex: ad@domain.com)")
        else:
            fok(email_field, email_error)
        hide_banner()
        page.update()

    def on_password_change(e):
        v = password_field.value
        if v and len(v) < MIN_PASSWORD_LENGTH:
            ferr(password_field, password_error,
                 f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
        else:
            fok(password_field, password_error)
        hide_banner()
        page.update()

    email_field.on_change    = on_email_change
    password_field.on_change = on_password_change

    # ── Submit
    def login_click(e):
        ev = email_field.value.strip()
        pv = password_field.value.strip()
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

        # SQLite credential check
        user = check_credentials(ev, pv)
        if user is None:
            show_banner("E-mail or password is incorrect")
        else:
            hide_banner()
            page.update()
            on_login_success(user["email"])
            return

        page.update()

    email_field.on_submit    = login_click
    password_field.on_submit = login_click

    # ── Theme 
    
    welcome_text  = ft.Text("Welcome back!", size=22,
                            weight=ft.FontWeight.BOLD, color=c()["text"])
    subtitle_text = ft.Text("Enter your e-mail and password",
                            size=12, color=c()["muted"], text_align="center")

    def refresh_theme():
        page.bgcolor        = c()["bg"]
        card.bgcolor        = c()["card"]
        welcome_text.color  = c()["text"]
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

    def toggle_theme(e):
        page.theme_mode = (
            ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        refresh_theme()

    theme_btn = ft.IconButton(
        icon=ft.Icons.DARK_MODE, on_click=toggle_theme, icon_color="#0f766e"
    )

    card = ft.Container(
        width=380, padding=30,
        bgcolor=c()["card"], border_radius=16,
        shadow=ft.BoxShadow(blur_radius=20, spread_radius=1, color=ft.Colors.BLACK12),
        content=ft.Column(
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                # Logo + theme
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(controls=[
                            ft.Container(
                                bgcolor="#0f766e", border_radius=20, padding=8,
                                content=ft.Icon(ft.Icons.SHOW_CHART, color="white", size=18)
                            ),
                            ft.Text("Lumina Learn", size=20,
                                    weight=ft.FontWeight.BOLD, color="#0f766e"),
                        ]),
                        theme_btn,
                    ]
                ),

                welcome_text,
                subtitle_text,
                error_box,

                # Email
                ft.Column([
                    ft.Text("E-MAİL", size=11,
                            weight=ft.FontWeight.BOLD, color="#6b7280"),
                    email_field,
                    email_error,
                ], spacing=4),

                # Password
                ft.Column([
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("PASSWORD", size=11,
                                    weight=ft.FontWeight.BOLD, color="#6b7280"),
                            ft.TextButton("Forgot password?",
                                          style=ft.ButtonStyle(color="#0f766e")),
                        ]
                    ),
                    password_field,
                    password_error,
                ], spacing=4),

                # Submit
                ft.ElevatedButton(
                    "Enter", width=320, height=45,
                    style=ft.ButtonStyle(
                        bgcolor="#0f766e", color="white",
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    on_click=login_click,
                ),

                ft.Divider(height=6, color="#e5e7eb"),

                

                # Go to register
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Already have an account?", size=12, color=c()["muted"]),
                        ft.TextButton(
                            "Sign In",
                            style=ft.ButtonStyle(color="#0f766e"),
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