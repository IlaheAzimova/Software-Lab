import flet as ft



LIGHT = {
    "bg":             "#f3f6f5",
    "card":           "#ffffff",
    "text":           "#111827",
    "muted":          "#6b7280",
    "border":         "#e5e7eb",
    "field_bg":       "#f9fafb",
    "sidebar":        "#ffffff",
    "sidebar_active": "#f0fdf9",
}

DARK = {
    "bg":             "#0f172a",
    "card":           "#1e293b",
    "text":           "#f1f5f9",
    "muted":          "#94a3b8",
    "border":         "#334155",
    "field_bg":       "#273349",
    "sidebar":        "#1e293b",
    "sidebar_active": "#0f2d2a",
}

# Brand color (teal)
PRIMARY = "#0f766e"
PRIMARY_BG = "#f0fdf9"


def get_colors(page: ft.Page) -> dict:
    """Return current theme palette based on page.theme_mode."""
    return LIGHT if page.theme_mode == ft.ThemeMode.LIGHT else DARK