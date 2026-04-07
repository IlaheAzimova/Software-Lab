import flet as ft
from database import init_db
from login import build_login
from register import build_register
from dashboard import show_dashboard


def main(page: ft.Page):
    page.title = "Lumina Learn"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0


    init_db()

  
    def go_login():
        build_login(
            page=page,
            on_login_success=go_dashboard,
            on_go_register=go_register,
        )

    def go_register():
        build_register(
            page=page,
            on_register_success=go_dashboard,   
            on_go_login=go_login,
        )

    def go_dashboard(email: str):
        show_dashboard(
            page=page,
            user_email=email,
            on_logout=go_login,
        )


    go_login()


ft.app(target=main)