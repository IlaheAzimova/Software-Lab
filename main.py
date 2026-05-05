

import flet as ft

from database import init_db
from login import build_login
from register import build_register
from dashboard import show_dashboard


def main(page: ft.Page):
    # ---------- App-wide page settings ----------
    page.title = "E-Learning Progress Analytics"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#f8fafc"

    # Window settings (desktop)
    try:
        page.window.width = 1280
        page.window.height = 820
        page.window.min_width = 1100
        page.window.min_height = 720
        page.window.center()
    except Exception:
        # Window object may not be available on web target
        pass

    # ---------- Database ----------
    init_db()

    # ---------- Navigation handlers ----------
    def go_login(_=None):
        build_login(
            page,
            on_login_success=go_dashboard,
            on_go_register=go_register,
        )

    def go_register(_=None):
        build_register(
            page,
            on_register_success=go_login,
            on_go_login=go_login,
        )

    def go_dashboard(user_email: str):
        show_dashboard(
            page,
            user_email=user_email or "user@example.com",
            on_logout=go_login,
        )

    # ---------- Start at login ----------
    go_login()


if __name__ == "__main__":
    ft.run(main)