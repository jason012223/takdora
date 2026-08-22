"""Accessible, composable Reflex primitives for Takdora workflows."""

from __future__ import annotations

from collections.abc import Sequence

import reflex as rx

from takdora.ui.theme import TOKENS


def field(
    label: str,
    field_id: str,
    *,
    description: str = "",
    error: str = "",
    required: bool = False,
    optional: bool = False,
    disabled: bool = False,
    value: str = "",
) -> rx.Component:
    """Create a labelled text input with explicit help and validation text."""
    help_id = f"{field_id}-help"
    error_id = f"{field_id}-error"
    described_by = " ".join(
        item for item in (help_id if description else "", error_id if error else "") if item
    )
    return rx.vstack(
        rx.el.label(
            label,
            rx.cond(required, rx.text("Required", as_="span", color=TOKENS["danger"], size="1")),
            rx.cond(optional, rx.text("Optional", as_="span", color=TOKENS["muted"], size="1")),
            html_for=field_id,
            weight="medium",
        ),
        rx.input(
            id=field_id,
            value=value,
            disabled=disabled,
            required=required,
            aria_describedby=described_by or None,
            aria_invalid="true" if error else "false",
            width="100%",
        ),
        rx.cond(
            description != "", rx.text(description, id=help_id, size="2", color=TOKENS["muted"])
        ),
        rx.cond(
            error != "", rx.text(error, id=error_id, role="alert", size="2", color=TOKENS["danger"])
        ),
        spacing="1",
        align="stretch",
        width="100%",
    )


def select_field(
    label: str, field_id: str, items: Sequence[str], *, required: bool = False
) -> rx.Component:
    """Create a labelled Radix select control."""
    return rx.vstack(
        rx.el.label(label, html_for=field_id, weight="medium"),
        rx.select(items=list(items), id=field_id, required=required, width="100%"),
        spacing="1",
        width="100%",
    )


def text_area(label: str, field_id: str, *, optional: bool = True) -> rx.Component:
    """Create a directly labelled optional note field."""
    return rx.vstack(
        rx.el.label(
            label,
            rx.cond(optional, rx.text("Optional", as_="span", color=TOKENS["muted"], size="1")),
            html_for=field_id,
            weight="medium",
        ),
        rx.text_area(id=field_id, width="100%", min_height="7rem"),
        spacing="1",
        width="100%",
    )


def action_button(label: str, *, loading: bool = False, disabled: bool = False) -> rx.Component:
    """Create a primary action that keeps its text when loading."""
    return rx.button(
        rx.cond(loading, "Working…", label),
        loading=loading,
        disabled=disabled,
        min_height=TOKENS["touch_target"],
    )


def feedback(message: str, *, kind: str = "success") -> rx.Component:
    """Create an announced inline outcome without diagnostic data."""
    colors = {"success": TOKENS["success"], "warning": TOKENS["warning"], "error": TOKENS["danger"]}
    return rx.callout(
        message,
        icon="circle_check" if kind == "success" else "triangle_alert",
        role="status" if kind != "error" else "alert",
        color_scheme="green" if kind == "success" else "orange" if kind == "warning" else "red",
        width="100%",
        border_left=f"4px solid {colors.get(kind, TOKENS['success'])}",
    )


def summary_card(title: str, value: str, detail: str) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text(title, size="2", color=TOKENS["muted"]),
            rx.heading(value, size="6"),
            rx.text(detail, size="2"),
            spacing="1",
        ),
        width="100%",
    )


def status_badge(label: str, *, tone: str = "neutral") -> rx.Component:
    colors = {"success": "green", "warning": "orange", "danger": "red", "neutral": "gray"}
    return rx.badge(label, color_scheme=colors.get(tone, "gray"), variant="soft")


def empty_state(title: str, detail: str, action_label: str) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading(title, size="4"),
            rx.text(detail, color=TOKENS["muted"]),
            action_button(action_label),
            align="start",
            spacing="3",
        ),
        width="100%",
    )


def detail_group(items: Sequence[tuple[str, str]]) -> rx.Component:
    return rx.vstack(
        *[
            rx.hstack(rx.text(label, weight="medium", width="8rem"), rx.text(value), width="100%")
            for label, value in items
        ],
        spacing="2",
        width="100%",
    )


def data_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> rx.Component:
    """Render a semantic scroll-safe table with explicit headers."""
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(*[rx.table.column_header_cell(header) for header in headers])
            ),
            rx.table.body(*[rx.table.row(*[rx.table.cell(cell) for cell in row]) for row in rows]),
            width="100%",
        ),
        overflow_x="auto",
        width="100%",
    )


def confirmation_dialog(title: str, description: str, confirm_label: str) -> rx.Component:
    """A labelled Radix dialog suitable for future confirmation actions."""
    return rx.dialog.root(
        rx.dialog.trigger(rx.button("Open sample confirmation", variant="soft")),
        rx.dialog.content(
            rx.dialog.title(title),
            rx.dialog.description(description),
            rx.flex(
                rx.dialog.close(rx.button("Cancel", variant="soft")),
                rx.dialog.close(rx.button(confirm_label, color_scheme="red")),
                spacing="3",
                justify="end",
            ),
            max_width="28rem",
        ),
    )


def availability_calendar(slots: Sequence[tuple[str, str]]) -> rx.Component:
    """Privacy-safe availability list: it deliberately excludes customer identity."""
    return rx.card(
        rx.vstack(
            rx.heading("Sample availability", size="4"),
            rx.text(
                "Synthetic slots only. Customer details are never shown here.",
                size="2",
                color=TOKENS["muted"],
            ),
            *[
                rx.hstack(
                    rx.text(label),
                    status_badge(status, tone="success" if status == "Available" else "neutral"),
                    justify="between",
                    width="100%",
                )
                for label, status in slots
            ],
            rx.text("No additional sample slots are available.", size="2", color=TOKENS["muted"]),
            spacing="3",
            width="100%",
        ),
        width="100%",
    )
