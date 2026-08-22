"""Single-screen anonymous booking page; commands remain server-authoritative."""

from __future__ import annotations

from datetime import date

import reflex as rx

from takdora.public_booking import (
    PublicBookingUnavailable,
    public_slots_for_day,
    resolve_public_business,
)
from takdora.ui.layouts import public_layout
from takdora.ui.primitives import feedback


class PublicBookingState(rx.State):
    business_name: str = ""
    contact_route: str = ""
    business_timezone: str = "Asia/Manila"
    browser_timezone: str = ""
    timezone_label: str = ""
    services: list[str] = []
    slots: list[str] = []
    selected_service_id: str = ""
    selected_slot: str = ""
    customer_name: str = ""
    customer_email: str = ""
    customer_phone: str = ""
    customer_note: str = ""
    honeypot: str = ""
    booking_message: str = ""

    def load_public_page(self) -> rx.event.EventSpec | None:
        result = resolve_public_business(self.business_slug)
        if result.redirect_slug:
            return rx.redirect(f"/b/{result.redirect_slug}")
        if result.business is None:
            self.booking_message = "This booking page is unavailable."
            return None
        self.business_name = result.business.name
        self.contact_route = result.business.contact_email or result.business.contact_phone
        self.business_timezone = result.business.timezone
        self.timezone_label = result.business.timezone
        self.services = [
            f"{item.id}: {item.name} · {item.duration_label} · {item.price_label}"
            for item in result.business.services
        ]
        if self.services and not self.selected_service_id:
            self.selected_service_id = self.services[0]
        return rx.call_script(
            "window.takdoraPublicBookingTimezone && window.takdoraPublicBookingTimezone()"
        )

    def set_browser_timezone(self, timezone_name: str) -> None:
        self.browser_timezone = timezone_name
        self.timezone_label = timezone_name or self.business_timezone

    def load_slots(self) -> None:
        if not self.selected_service_id:
            self.booking_message = "Choose a service to see available times."
            return
        try:
            results = public_slots_for_day(
                self.business_slug,
                int(self.selected_service_id.split(":", maxsplit=1)[0]),
                date.today(),
                self.browser_timezone,
            )
        except (PublicBookingUnavailable, ValueError):
            self.slots = []
            self.booking_message = "No times are available for that day."
            return
        self.slots = [f"{item.start_at_utc.isoformat()} | {item.local_label}" for item in results]
        self.booking_message = (
            "Choose a time that works for you."
            if self.slots
            else "No times are available for that day."
        )


def public_booking_page() -> rx.Component:
    return public_layout(
        rx.vstack(
            rx.script(src="/public_booking_timezone.js"),
            rx.heading(PublicBookingState.business_name, size="8"),
            rx.text("Choose a service and time, then confirm your details."),
            rx.form(
                rx.vstack(
                    rx.el.label("Service", html_for="public-service"),
                    rx.select(
                        PublicBookingState.services,
                        value=PublicBookingState.selected_service_id,
                        on_change=PublicBookingState.set_selected_service_id,
                        id="public-service",
                    ),
                    rx.button(
                        "Show available times",
                        type="button",
                        on_click=PublicBookingState.load_slots,
                    ),
                    rx.el.label("Available time", html_for="public-slot"),
                    rx.select(
                        PublicBookingState.slots,
                        value=PublicBookingState.selected_slot,
                        on_change=PublicBookingState.set_selected_slot,
                        id="public-slot",
                    ),
                    rx.text(
                        "Times are shown in your time zone: ", PublicBookingState.timezone_label
                    ),
                    rx.el.label("Your name", html_for="customer-name"),
                    rx.input(
                        id="customer-name",
                        value=PublicBookingState.customer_name,
                        on_change=PublicBookingState.set_customer_name,
                        required=True,
                    ),
                    rx.el.label("Email address", html_for="customer-email"),
                    rx.input(
                        id="customer-email",
                        type="email",
                        value=PublicBookingState.customer_email,
                        on_change=PublicBookingState.set_customer_email,
                        required=True,
                    ),
                    rx.el.label("Phone number (optional)", html_for="customer-phone"),
                    rx.input(
                        id="customer-phone",
                        value=PublicBookingState.customer_phone,
                        on_change=PublicBookingState.set_customer_phone,
                    ),
                    rx.el.label("Note (optional)", html_for="customer-note"),
                    rx.text_area(
                        id="customer-note",
                        value=PublicBookingState.customer_note,
                        on_change=PublicBookingState.set_customer_note,
                    ),
                    rx.input(
                        id="website",
                        value=PublicBookingState.honeypot,
                        on_change=PublicBookingState.set_honeypot,
                        display="none",
                        tab_index=-1,
                    ),
                    rx.text(
                        "We use your details only to manage this appointment. ",
                        rx.link("Privacy policy", href="/privacy"),
                        size="2",
                    ),
                    rx.button("Book appointment", type="submit"),
                    rx.cond(
                        PublicBookingState.booking_message != "",
                        feedback(PublicBookingState.booking_message, kind="warning"),
                    ),
                    spacing="3",
                    width="100%",
                ),
                id="public-booking-form",
            ),
            align="start",
            width="100%",
            max_width="42rem",
        )
    )


def privacy_page() -> rx.Component:
    return public_layout(
        rx.heading("Privacy", size="7"),
        rx.text("Takdora uses booking contact details only to manage the appointment you request."),
    )
