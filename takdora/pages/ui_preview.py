"""Responsive internal preview of the reusable Takdora layouts."""

from __future__ import annotations

import reflex as rx

from takdora.ui.layouts import marketing_layout, owner_layout, public_layout
from takdora.ui.primitives import (
    availability_calendar,
    confirmation_dialog,
    data_table,
    feedback,
    field,
)


def ui_preview() -> rx.Component:
    """Render synthetic examples only, for design and regression review."""
    sample_form = rx.vstack(
        rx.badge("Synthetic preview", color_scheme="orange", variant="soft"),
        rx.heading("Sample service-business workflow", size="6"),
        rx.text("This preview uses generated neutral sample content, not customer information."),
        field("Sample customer name", "preview-customer-name", required=True),
        feedback("Sample request ready for review.", kind="success"),
        width="100%",
    )
    sample_table = data_table(
        ["Sample item", "State"], [["Sample booking", "Scheduled"], ["Sample invoice", "Draft"]]
    )
    calendar = availability_calendar(
        [("Monday, 9:00 AM", "Available"), ("Monday, 10:00 AM", "Blocked")]
    )
    return rx.vstack(
        rx.el.section(
            public_layout(sample_form, sample_table),
            aria_label="Public layout preview",
            width="100%",
        ),
        rx.el.section(
            owner_layout(rx.heading("Owner preview", size="6"), sample_table, calendar),
            aria_label="Owner layout preview",
            width="100%",
        ),
        rx.el.section(
            marketing_layout(
                rx.heading("Marketing preview", size="6"),
                confirmation_dialog(
                    "Confirm sample action", "No business data will be changed.", "Confirm sample"
                ),
            ),
            aria_label="Marketing layout preview",
            width="100%",
        ),
        spacing="0",
        width="100%",
    )
