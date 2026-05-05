
import flet as ft

from theme import PRIMARY, PRIMARY_BG
from ui_widgets import page_footer


def build_assessment_page(page: ft.Page, c, on_back) -> ft.Control:
    # Track answered count so the dialog can change its warning state
    state = {"answered": 0, "total": 5}

    # ─── Final-submission dialog ─────────────────────────
    def submission_dialog():
        warning_box = ft.Container(
            bgcolor="#fee2e2",
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            content=ft.Row([
                ft.Icon(ft.Icons.ERROR_OUTLINE, color="#b91c1c", size=18),
                ft.Text(
                    "Warning: You still have unanswered questions.\n"
                    "Submitting now may result in a lower score.",
                    size=12, color="#b91c1c",
                ),
            ], spacing=8),
            visible=state["answered"] < state["total"],
        )

        body = ft.Column(spacing=14, tight=True, width=380, controls=[
            ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color="#dc2626", size=22),
                ft.Text("Final Submission", size=18, weight=ft.FontWeight.BOLD,
                        color=c()["text"]),
            ], spacing=8),

            ft.Text(
                f"Are you sure you want to submit your answers? "
                f"You have answered {state['answered']} of {state['total']} questions.",
                size=12, color=c()["muted"],
            ),

            warning_box,

            ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINED, color="#16a34a", size=18),
                ft.Text("Answers are automatically saved.",
                        size=12, color=c()["muted"]),
            ], spacing=8),
        ])

        def do_submit(e):
            page.pop_dialog()
            page.show_dialog(_result_dialog(page, c, state, on_back))

        return ft.AlertDialog(
            modal=True,
            content=ft.Container(padding=ft.Padding.all(8), content=body),
            actions=[
                ft.TextButton(
                    "Review Answers",
                    style=ft.ButtonStyle(color=c()["muted"]),
                    on_click=lambda e: page.pop_dialog(),
                ),
                ft.ElevatedButton(
                    "Yes, Submit",
                    style=ft.ButtonStyle(
                        bgcolor=PRIMARY, color="white",
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=do_submit,
                ),
            ],
        )

    # ─── Big assessment-start card ───────────────────────
    answered_text = ft.Text(
        f"Answered {state['answered']} of {state['total']} questions",
        size=12, color=c()["muted"]
    )

    def fake_answer_one(e):
        if state["answered"] < state["total"]:
            state["answered"] += 1
            answered_text.value = (
                f"Answered {state['answered']} of {state['total']} questions"
            )
            page.update()

    start_card = ft.Container(
        width=460,
        bgcolor=c()["card"],
        border_radius=14,
        padding=ft.Padding.all(28),
        shadow=ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.with_opacity(0.07, ft.Colors.BLACK),
        ),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14,
            controls=[
                ft.Container(
                    width=64, height=64,
                    bgcolor=PRIMARY_BG, border_radius=32,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(ft.Icons.MENU_BOOK_ROUNDED,
                                    size=28, color=PRIMARY),
                ),
                ft.Text("UI/UX Design Fundamentals", size=20,
                        weight=ft.FontWeight.BOLD, color=c()["text"]),
                ft.Text("Module: Foundations of Design",
                        size=12, color=c()["muted"]),

                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=40,
                    controls=[
                        ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text("PASSING SCORE", size=10,
                                        weight=ft.FontWeight.BOLD,
                                        color=c()["muted"]),
                                ft.Text("70%", size=22,
                                        weight=ft.FontWeight.BOLD,
                                        color=c()["text"]),
                            ], spacing=2,
                        ),
                        ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text("QUESTIONS", size=10,
                                        weight=ft.FontWeight.BOLD,
                                        color=c()["muted"]),
                                ft.Text(str(state["total"]), size=22,
                                        weight=ft.FontWeight.BOLD,
                                        color=c()["text"]),
                            ], spacing=2,
                        ),
                    ]
                ),

                answered_text,

                ft.Row(spacing=10, alignment=ft.MainAxisAlignment.CENTER, controls=[
                    ft.OutlinedButton(
                        "Answer one (demo)",
                        icon=ft.Icons.ADD_TASK,
                        on_click=fake_answer_one,
                        style=ft.ButtonStyle(
                            color=PRIMARY,
                            side=ft.BorderSide(1.5, PRIMARY),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
                ]),

                ft.Container(
                    width=380,
                    bgcolor=PRIMARY,
                    border_radius=10,
                    padding=ft.Padding.symmetric(vertical=14),
                    alignment=ft.Alignment(0, 0),
                    on_click=lambda e: page.show_dialog(submission_dialog()),
                    content=ft.Text("Start Assessment", color="white",
                                    weight=ft.FontWeight.BOLD, size=14),
                ),

                ft.TextButton(
                    "Skip directly to Final Submission",
                    style=ft.ButtonStyle(color=c()["muted"]),
                    on_click=lambda e: page.show_dialog(submission_dialog()),
                ),
            ]
        )
    )

    # ─── breadcrumbs / header ────────────────────────────
    breadcrumb = ft.Row(spacing=6, controls=[
        ft.TextButton(
            "Lessons",
            style=ft.ButtonStyle(color=c()["muted"]),
            on_click=lambda e: on_back(),
        ),
        ft.Icon(ft.Icons.CHEVRON_RIGHT, size=14, color=c()["muted"]),
        ft.Text("Assessment", size=13, color=c()["text"],
                weight=ft.FontWeight.W_600),
    ])

    return ft.Column(
        scroll=ft.ScrollMode.AUTO, spacing=24,
        controls=[
            breadcrumb,
            ft.Container(
                alignment=ft.Alignment(0, 0),
                content=start_card,
            ),
            ft.Container(height=20),
            page_footer(c),
        ]
    )


# ─── Optional success dialog after submitting ───────────
def _result_dialog(page: ft.Page, c, state: dict, on_back):
    score = int((state["answered"] / max(1, state["total"])) * 100)
    passed = score >= 70
    return ft.AlertDialog(
        modal=True,
        content=ft.Container(
            width=360,
            padding=ft.Padding.all(8),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Icon(
                        ft.Icons.CHECK_CIRCLE_ROUNDED if passed
                        else ft.Icons.CANCEL_ROUNDED,
                        size=48,
                        color="#16a34a" if passed else "#dc2626",
                    ),
                    ft.Text("Submission Received!" if passed else "Submitted",
                            size=18, weight=ft.FontWeight.BOLD,
                            color=c()["text"]),
                    ft.Text(f"Your score: {score}%", size=14, color=c()["muted"]),
                    ft.Text(
                        "You passed!" if passed else "You did not reach the passing score.",
                        size=12,
                        color="#16a34a" if passed else "#dc2626",
                    ),
                ]
            ),
        ),
        actions=[
            ft.ElevatedButton(
                "Back to Lessons",
                style=ft.ButtonStyle(
                    bgcolor=PRIMARY, color="white",
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                on_click=lambda e: (page.pop_dialog(), on_back()),
            ),
        ],
    )