
import flet as ft
from theme import PRIMARY


def avatar(initials: str, size: int = 34, bg: str = "#0f766e22", fg: str = PRIMARY):
    """A circular avatar with initials."""
    return ft.Container(
        width=size, height=size, border_radius=size // 2,
        bgcolor=bg, alignment=ft.Alignment(0, 0),
        content=ft.Text(
            initials, size=max(10, size // 3 + 1),
            weight=ft.FontWeight.BOLD, color=fg,
        ),
    )


def initials_of(name: str) -> str:
    parts = name.split()[:2] if name else []
    return "".join(p[0] for p in parts).upper() or "?"


def status_chip(label: str, color: str, bg: str):
    return ft.Container(
        content=ft.Text(label, size=11, weight=ft.FontWeight.BOLD, color=color),
        bgcolor=bg, border_radius=20,
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
    )


def colored_chip(label: str, kind: str = "neutral"):
    """
    kind ∈ {success, info, warn, danger, neutral}
    """
    palette = {
        "success": ("#16a34a", "#dcfce7"),
        "info":    ("#2563eb", "#dbeafe"),
        "warn":    ("#d97706", "#fef3c7"),
        "danger":  ("#ffffff", "#dc2626"),
        "neutral": ("#374151", "#f3f4f6"),
        "teal":    (PRIMARY,  "#ccfbf1"),
        "purple":  ("#7c3aed", "#f5f3ff"),
        "orange":  ("#ea580c", "#ffedd5"),
    }
    fg, bg = palette.get(kind, palette["neutral"])
    return ft.Container(
        content=ft.Text(label, size=10, weight=ft.FontWeight.BOLD, color=fg),
        bgcolor=bg, border_radius=6,
        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
    )


def section_header(title: str, subtitle: str | None, c, action: ft.Control | None = None):
    """Standard "Title / subtitle / right-side action" header used at top of pages."""
    left = ft.Column(
        spacing=2,
        controls=[
            ft.Text(title, size=24, weight=ft.FontWeight.BOLD, color=c()["text"]),
        ] + ([ft.Text(subtitle, size=13, color=c()["muted"])] if subtitle else []),
    )
    right_controls = [action] if action is not None else []
    return ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[left, ft.Row(spacing=8, controls=right_controls)],
    )


def primary_button(text: str, icon=None, on_click=None, width: int | None = None):
    row_controls = []
    if icon is not None:
        row_controls.append(ft.Icon(icon, color="white", size=18))
    row_controls.append(ft.Text(text, size=13, color="white", weight=ft.FontWeight.W_600))
    return ft.Container(
        width=width,
        bgcolor=PRIMARY, border_radius=30,
        padding=ft.Padding.symmetric(horizontal=18, vertical=12),
        on_click=on_click,
        content=ft.Row(
            controls=row_controls, spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True,
        ),
    )


def outline_button(text: str, icon=None, on_click=None, color: str = PRIMARY, width: int | None = None):
    row_controls = []
    if icon is not None:
        row_controls.append(ft.Icon(icon, color=color, size=18))
    row_controls.append(ft.Text(text, size=13, color=color, weight=ft.FontWeight.W_600))
    return ft.Container(
        width=width,
        bgcolor="transparent",
        border=ft.Border.all(1.5, color),
        border_radius=30,
        padding=ft.Padding.symmetric(horizontal=18, vertical=10),
        on_click=on_click,
        content=ft.Row(
            controls=row_controls, spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True,
        ),
    )


def card_container(content, c, padding: int = 20):
    return ft.Container(
        bgcolor=c()["card"],
        border_radius=12,
        padding=ft.Padding.all(padding),
        shadow=ft.BoxShadow(
            blur_radius=8,
            color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
        ),
        content=content,
    )


def page_footer(c):
    return ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Text("© 2026 E-Learning Progress Analytics. All rights reserved.",
                    size=11, color=c()["muted"]),
            ft.Row([
                ft.TextButton("Privacy Policy",
                              style=ft.ButtonStyle(color=c()["muted"])),
                ft.TextButton("Support",
                              style=ft.ButtonStyle(color=c()["muted"])),
            ])
        ]
    )