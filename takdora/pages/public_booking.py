"""Single-screen anonymous booking page; commands remain server-authoritative."""

from __future__ import annotations

import secrets
from datetime import date

import reflex as rx

from takdora.booking import BookingRequest, create_public_booking
from takdora.booking_notifications import dispatch_confirmation
from takdora.public_booking import (
    PublicBookingUnavailable,
    format_slot_for_timezone,
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
    services: list[dict[str, str]] = []
    slots: list[dict[str, str]] = []
    selected_service_id: str = ""
    selected_service_label: str = ""
    selected_slot: str = ""
    selected_slot_label: str = ""
    customer_name: str = ""
    customer_email: str = ""
    customer_phone: str = ""
    customer_note: str = ""
    honeypot: str = ""
    booking_message: str = ""
    booking_message_kind: str = "warning"
    idempotency_key: str = ""
    booking_complete: bool = False
    confirmed_service: str = ""
    confirmed_time: str = ""
    email_delivery: str = ""
    name_error: str = ""
    email_error: str = ""

    def load_public_page(self) -> rx.event.EventSpec | None:
        result = resolve_public_business(self.business_slug)
        if result.redirect_slug:
            return rx.redirect(f"/b/{result.redirect_slug}")
        if result.business is None:
            self.booking_message = "This booking page is unavailable."
            self.booking_message_kind = "error"
            return None
        self.business_name = result.business.name
        self.contact_route = result.business.contact_email or result.business.contact_phone
        self.business_timezone = result.business.timezone
        self.timezone_label = result.business.timezone
        _legacy_service_labels = [
            f"{item.id}: {item.name} · {item.duration_label} · {item.price_label}"
            for item in result.business.services
        ]
        self.services = [
            {
                "id": str(item.id),
                "label": f"{item.name} · {item.duration_label} · {item.price_label}",
            }
            for item in result.business.services
        ]
        if self.services and not self.selected_service_id:
            self.select_service(self.services[0]["id"])
        if not self.idempotency_key:
            self.idempotency_key = secrets.token_urlsafe(32)
        return rx.call_script(
            "window.takdoraPublicBookingTimezone && window.takdoraPublicBookingTimezone()",
            callback=PublicBookingState.set_browser_timezone,
        )

    def set_browser_timezone(self, timezone_name: str) -> None:
        self.browser_timezone = timezone_name
        self.timezone_label = timezone_name or self.business_timezone
        if self.selected_service_id:
            self.load_slots()

    def select_service(self, service_id: str) -> None:
        """Retain a safe server ID while showing customers only a service label."""
        self.selected_service_id = service_id
        self.selected_service_label = next(
            (item["label"] for item in self.services if item["id"] == service_id), ""
        )
        self.selected_slot = ""
        self.selected_slot_label = ""
        self.load_slots()

    def select_slot(self, slot_start_utc: str) -> None:
        self.selected_slot = slot_start_utc
        self.selected_slot_label = next(
            (item["label"] for item in self.slots if item["id"] == slot_start_utc), ""
        )

    def load_slots(self) -> None:
        if not self.selected_service_id:
            self.booking_message = "Choose a service to see available times."
            self.booking_message_kind = "warning"
            return
        try:
            results = public_slots_for_day(
                self.business_slug,
                int(self.selected_service_id),
                date.today(),
                self.browser_timezone,
            )
        except (PublicBookingUnavailable, ValueError):
            self.slots = []
            self.booking_message = "No times are available for that day."
            self.booking_message_kind = "warning"
            return
        display_zone = self.browser_timezone or self.business_timezone
        self.slots = [
            {
                "id": item.start_at_utc.isoformat(),
                "label": format_slot_for_timezone(item, display_zone)[0],
            }
            for item in results
        ]
        self.booking_message = (
            "Choose a time that works for you."
            if self.slots
            else "No times are available for that day."
        )
        self.booking_message_kind = "success" if self.slots else "warning"

    def submit_booking(self) -> None:
        self.name_error = ""
        self.email_error = ""
        if not self.customer_name.strip():
            self.name_error = "Enter your name."
        if "@" not in self.customer_email or not self.customer_email.strip():
            self.email_error = "Enter a valid email address."
        if self.name_error or self.email_error:
            self.booking_message = "Check the highlighted details and try again."
            self.booking_message_kind = "error"
            return
        if not self.selected_slot or not self.selected_service_id:
            self.booking_message = "Choose a service and available time."
            self.booking_message_kind = "warning"
            return
        result = create_public_booking(
            BookingRequest(
                slug=self.business_slug,
                service_id=self.selected_service_id,
                slot_start_utc=self.selected_slot,
                idempotency_key=self.idempotency_key,
                customer_name=self.customer_name,
                customer_email=self.customer_email,
                customer_phone=self.customer_phone,
                customer_note=self.customer_note,
                browser_timezone=self.browser_timezone,
                honeypot=self.honeypot,
            )
        )
        if result.outcome == "slot_taken":
            self.selected_slot = ""
            self.selected_slot_label = ""
            self.idempotency_key = secrets.token_urlsafe(32)
            self.booking_message = "That time was just taken. Choose another available time."
            self.booking_message_kind = "warning"
            self.load_slots()
            return
        if result.outcome != "booked" or result.booking_id is None:
            self.booking_message = result.message
            self.booking_message_kind = "error"
            return
        self.booking_complete = True
        self.confirmed_service = self.selected_service_label
        self.confirmed_time = self.selected_slot_label
        self.email_delivery = dispatch_confirmation(result.booking_id)
        self.booking_message = "Booking confirmed."
        self.booking_message_kind = "success"


def _booking_feedback() -> rx.Component:
    return rx.cond(
        PublicBookingState.booking_message_kind == "success",
        feedback(PublicBookingState.booking_message, kind="success"),
        rx.cond(
            PublicBookingState.booking_message_kind == "error",
            feedback(PublicBookingState.booking_message, kind="error"),
            rx.cond(
                PublicBookingState.booking_message != "",
                feedback(PublicBookingState.booking_message, kind="warning"),
            ),
        ),
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
                    rx.select.root(
                        rx.select.trigger(id="public-service", width="100%"),
                        rx.select.content(
                            rx.foreach(
                                PublicBookingState.services,
                                lambda service: rx.select.item(
                                    service["label"], value=service["id"]
                                ),
                            )
                        ),
                        value=PublicBookingState.selected_service_id,
                        on_change=PublicBookingState.select_service,
                    ),
                    rx.el.label("Available time", html_for="public-slot"),
                    rx.select.root(
                        rx.select.trigger(
                            id="public-slot", width="100%", placeholder="Choose a time"
                        ),
                        rx.select.content(
                            rx.foreach(
                                PublicBookingState.slots,
                                lambda slot: rx.select.item(slot["label"], value=slot["id"]),
                            )
                        ),
                        value=PublicBookingState.selected_slot,
                        on_change=PublicBookingState.select_slot,
                    ),
                    rx.text(
                        "Times are shown in your time zone: ", PublicBookingState.timezone_label
                    ),
                    rx.cond(
                        PublicBookingState.selected_slot != "",
                        rx.card(
                            rx.vstack(
                                rx.text("Your appointment", size="2", weight="medium"),
                                rx.text(PublicBookingState.selected_service_label, weight="medium"),
                                rx.text(PublicBookingState.selected_slot_label),
                                rx.text("Review these details before booking.", size="2"),
                                align="start",
                                spacing="1",
                            ),
                            width="100%",
                        ),
                    ),
                    rx.el.label("Your name", html_for="customer-name"),
                    rx.input(
                        id="customer-name",
                        value=PublicBookingState.customer_name,
                        on_change=PublicBookingState.set_customer_name,
                        required=True,
                    ),
                    rx.cond(
                        PublicBookingState.name_error != "",
                        rx.text(PublicBookingState.name_error, color="red", role="alert"),
                    ),
                    rx.el.label("Email address", html_for="customer-email"),
                    rx.input(
                        id="customer-email",
                        type="email",
                        value=PublicBookingState.customer_email,
                        on_change=PublicBookingState.set_customer_email,
                        required=True,
                    ),
                    rx.cond(
                        PublicBookingState.email_error != "",
                        rx.text(PublicBookingState.email_error, color="red", role="alert"),
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
                    _booking_feedback(),
                    spacing="3",
                    width="100%",
                ),
                id="public-booking-form",
                on_submit=PublicBookingState.submit_booking,
            ),
            rx.cond(
                PublicBookingState.booking_complete,
                rx.card(
                    rx.vstack(
                        rx.heading("Your booking is confirmed", size="5"),
                        rx.text(PublicBookingState.business_name),
                        rx.text(PublicBookingState.confirmed_service),
                        rx.text(PublicBookingState.confirmed_time),
                        rx.cond(
                            PublicBookingState.email_delivery == "sent",
                            rx.text("A confirmation email was sent."),
                            rx.text(
                                "Your booking is confirmed, but email delivery is delayed. "
                                "Save these details and contact the business if you need help."
                            ),
                        ),
                    )
                ),
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
