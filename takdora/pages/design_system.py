"""Synthetic, developer-facing gallery for shared interface patterns."""

from __future__ import annotations

import reflex as rx

from takdora.ui.primitives import (
    action_button,
    data_table,
    detail_group,
    empty_state,
    feedback,
    field,
    select_field,
    status_badge,
    summary_card,
    text_area,
)
from takdora.ui.shell import application_shell


def design_system() -> rx.Component:
    """Render only synthetic examples; never render customer or account data."""
    return application_shell(
        rx.vstack(
            rx.badge("Developer preview", color_scheme="orange", variant="soft"),
            rx.heading("Takdora interface patterns", size="8"),
            rx.text("All content below is synthetic demo data, not customer or business records."),
            rx.divider(),
            rx.heading("Booking request sample", size="5"),
            rx.box(
                field(
                    "Customer name",
                    "demo-customer-name",
                    description="Use the name the business should use.",
                    required=True,
                ),
                select_field(
                    "Service",
                    "demo-service",
                    ["Consultation", "Service appointment"],
                    required=True,
                ),
                text_area("Booking note", "demo-booking-note"),
                action_button("Submit sample request"),
                display="grid",
                gap="1rem",
                width="100%",
                max_width="42rem",
            ),
            rx.heading("Feedback states", size="5"),
            feedback("Sample request saved.", kind="success"),
            feedback("This sample slot needs attention.", kind="warning"),
            feedback("Sample validation message.", kind="error"),
            rx.heading("Operations patterns", size="5"),
            rx.hstack(
                summary_card("Sample bookings", "4", "Synthetic summary only"),
                summary_card("Sample balance", "₱0.00", "No real payment data"),
                width="100%",
                flex_direction={"base": "column", "md": "row"},
            ),
            rx.hstack(
                status_badge("Scheduled", tone="success"),
                status_badge("Needs review", tone="warning"),
            ),
            detail_group([("Example service", "Consultation"), ("Example status", "Synthetic")]),
            data_table(
                ["Sample record", "Status"],
                [["Sample appointment", "Scheduled"], ["Sample invoice", "Draft"]],
            ),
            empty_state("No sample bookings", "This is a synthetic empty state.", "Create sample"),
            spacing="6",
            width="100%",
        )
    )
