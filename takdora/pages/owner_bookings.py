"""Agenda-first private booking operations, backed only by the owner session."""

from __future__ import annotations

from datetime import UTC, date, datetime

import reflex as rx

from takdora.auth import AuthenticationError, AuthState
from takdora.booking_operations import (
    BOOKING_STATUS_LABELS,
    cancel_booking,
    complete_booking,
    owner_booking_detail,
    owner_bookings,
    owner_week_bookings,
    replacement_slots,
    reschedule_booking,
)
from takdora.demo import is_synthetic_demo_owner
from takdora.invoicing import start_invoice_draft
from takdora.pages.demo import synthetic_demo_banner
from takdora.tenancy import WorkspaceAccessError
from takdora.ui.layouts import owner_layout
from takdora.ui.primitives import detail_group, feedback, status_badge


class OwnerBookingsState(AuthState):
    """Private UI state; booking data is always re-derived by server commands."""

    selected_date: str = ""
    selected_status: str = ""
    view_mode: str = "agenda"
    agenda: list[dict[str, str]] = []
    detail: dict[str, str] = {}
    message: str = ""
    cancel_message: str = ""
    cancel_open: bool = False
    reschedule_open: bool = False
    replacement_choices: list[str] = []
    selected_replacement: str = ""
    is_synthetic_demo: bool = False

    def _rows(self, records: tuple) -> list[dict[str, str]]:
        return [
            {
                "id": str(item.id),
                "service": item.service_name,
                "time": item.local_time,
                "status": item.status_label,
            }
            for item in records
        ]

    def load_bookings(self) -> rx.event.EventSpec | None:
        try:
            owner = self.require_owner()
            self.is_synthetic_demo = is_synthetic_demo_owner(owner)
            if not self.selected_date:
                self.selected_date = datetime.now(UTC).date().isoformat()
            records = (
                owner_week_bookings(
                    owner, selected_date=self.selected_date, status=self.selected_status
                )
                if self.view_mode == "calendar"
                else owner_bookings(
                    owner, selected_date=self.selected_date, status=self.selected_status
                )
            )
        except (AuthenticationError, WorkspaceAccessError):
            return rx.redirect("/sign-in")
        self.agenda = self._rows(records)
        return None

    def set_view(self, mode: str) -> None:
        self.view_mode = "calendar" if mode == "calendar" else "agenda"
        self.load_bookings()

    def apply_filters(self) -> None:
        self.view_mode = self.view_mode if self.view_mode in ("agenda", "calendar") else "agenda"
        self.load_bookings()

    def open_booking(self, booking_id: str) -> None:
        try:
            item = owner_booking_detail(self.require_owner(), booking_id)
        except (AuthenticationError, WorkspaceAccessError):
            self.message = "Please sign in to continue."
            return
        if item is None:
            self.message = "Booking not found."
            return
        self.detail = {
            "id": str(item.id),
            "service": item.service_name,
            "time": item.local_time,
            "status": item.status,
            "status_label": item.status_label,
            "name": item.customer_name,
            "email": item.customer_email,
            "phone": item.customer_phone,
            "note": item.customer_note,
        }
        self.message = ""

    def confirm_cancellation(self) -> None:
        result = cancel_booking(
            self.require_owner(), self.detail.get("id", ""), self.cancel_message
        )
        self.message = result.message
        self.cancel_open = False
        self.cancel_message = ""
        if result.booking:
            self.open_booking(str(result.booking.id))
        self.load_bookings()

    def mark_completed(self) -> None:
        result = complete_booking(self.require_owner(), self.detail.get("id", ""))
        self.message = result.message
        if result.booking:
            self.open_booking(str(result.booking.id))
        self.load_bookings()

    def create_invoice(self) -> rx.event.EventSpec | None:
        result = start_invoice_draft(self.require_owner(), self.detail.get("id", ""))
        self.message = result.message
        if result.invoice_id and result.outcome in {"draft_created", "already_invoiced"}:
            return rx.redirect(f"/owner/invoices/{result.invoice_id}")
        return None

    def open_reschedule(self) -> None:
        booking_id = self.detail.get("id", "")
        slots = replacement_slots(
            self.require_owner(),
            booking_id,
            date.fromisoformat(self.selected_date or date.today().isoformat()),
        )
        self.replacement_choices = [
            f"{item.start_at_utc.isoformat()} | {item.local_label}" for item in slots
        ]
        self.reschedule_open = True
        self.selected_replacement = ""

    def confirm_reschedule(self) -> None:
        result = reschedule_booking(
            self.require_owner(),
            self.detail.get("id", ""),
            self.selected_replacement.split(" | ", maxsplit=1)[0],
        )
        self.message = result.message
        if result.outcome == "rescheduled":
            self.reschedule_open = False
            self.open_booking(self.detail.get("id", ""))
            self.load_bookings()


def owner_bookings_page() -> rx.Component:
    rows = rx.foreach(
        OwnerBookingsState.agenda,
        lambda row: rx.card(
            rx.hstack(
                rx.vstack(
                    rx.text(row["service"], weight="medium"),
                    rx.text(row["time"], size="2"),
                    align="start",
                ),
                status_badge(row["status"]),
                rx.button(
                    "View details",
                    on_click=OwnerBookingsState.open_booking(row["id"]),
                    variant="soft",
                ),
                justify="between",
                width="100%",
            ),
            width="100%",
        ),
    )
    return owner_layout(
        rx.cond(OwnerBookingsState.is_synthetic_demo, synthetic_demo_banner()),
        rx.vstack(
            rx.heading("Bookings", size="7"),
            rx.text("Review appointments and make deliberate changes."),
            rx.hstack(
                rx.input(
                    type="date",
                    value=OwnerBookingsState.selected_date,
                    on_change=OwnerBookingsState.set_selected_date,
                    aria_label="Booking date",
                ),
                rx.select(
                    ["All statuses", *BOOKING_STATUS_LABELS.values()],
                    value=OwnerBookingsState.selected_status,
                    on_change=OwnerBookingsState.set_selected_status,
                    aria_label="Booking status",
                ),
                rx.button("Apply filters", on_click=OwnerBookingsState.apply_filters),
                spacing="3",
                wrap="wrap",
            ),
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("Agenda", value="agenda"),
                    rx.tabs.trigger("Week calendar", value="calendar"),
                ),
                value=OwnerBookingsState.view_mode,
                on_change=OwnerBookingsState.set_view,
            ),
            rx.cond(
                OwnerBookingsState.agenda.length() > 0,
                rx.vstack(rows, width="100%"),
                rx.card(rx.text("No bookings match these filters."), width="100%"),
            ),
            rx.cond(
                OwnerBookingsState.message != "",
                feedback(OwnerBookingsState.message, kind="warning"),
            ),
            rx.cond(
                OwnerBookingsState.detail != {},
                rx.card(
                    rx.vstack(
                        rx.heading("Booking details", size="5"),
                        detail_group(
                            [
                                ("Service", OwnerBookingsState.detail["service"]),
                                ("When", OwnerBookingsState.detail["time"]),
                                ("Customer", OwnerBookingsState.detail["name"]),
                                ("Email", OwnerBookingsState.detail["email"]),
                                ("Phone", OwnerBookingsState.detail["phone"]),
                                ("Note", OwnerBookingsState.detail["note"]),
                            ]
                        ),
                        status_badge(OwnerBookingsState.detail["status_label"]),
                        rx.cond(
                            OwnerBookingsState.detail["status"] == "completed",
                            rx.button("Create invoice", on_click=OwnerBookingsState.create_invoice),
                        ),
                        rx.cond(
                            OwnerBookingsState.detail["status"] == "scheduled",
                            rx.hstack(
                                rx.button(
                                    "Reschedule", on_click=OwnerBookingsState.open_reschedule
                                ),
                                rx.button(
                                    "Mark completed",
                                    on_click=OwnerBookingsState.mark_completed,
                                    variant="soft",
                                ),
                                rx.button(
                                    "Cancel booking",
                                    on_click=OwnerBookingsState.set_cancel_open(True),
                                    color_scheme="red",
                                    variant="soft",
                                ),
                                wrap="wrap",
                            ),
                        ),
                        rx.cond(
                            OwnerBookingsState.detail["status"] == "pending",
                            rx.button(
                                "Cancel booking",
                                on_click=OwnerBookingsState.set_cancel_open(True),
                                color_scheme="red",
                                variant="soft",
                            ),
                        ),
                        width="100%",
                        align="start",
                        spacing="3",
                    ),
                    width="100%",
                ),
            ),
            rx.dialog.root(
                rx.dialog.content(
                    rx.dialog.title("Cancel this booking?"),
                    rx.dialog.description(
                        "This releases the appointment time and sends an update after you confirm."
                    ),
                    rx.el.label("Message for the customer (optional)", html_for="cancel-message"),
                    rx.text_area(
                        id="cancel-message",
                        value=OwnerBookingsState.cancel_message,
                        on_change=OwnerBookingsState.set_cancel_message,
                    ),
                    rx.hstack(
                        rx.dialog.close(rx.button("Keep booking", variant="soft")),
                        rx.dialog.close(
                            rx.button(
                                "Confirm cancellation",
                                on_click=OwnerBookingsState.confirm_cancellation,
                                color_scheme="red",
                            )
                        ),
                        justify="end",
                    ),
                ),
                open=OwnerBookingsState.cancel_open,
                on_open_change=OwnerBookingsState.set_cancel_open,
            ),
            rx.dialog.root(
                rx.dialog.content(
                    rx.dialog.title("Choose a replacement time"),
                    rx.select(
                        OwnerBookingsState.replacement_choices,
                        value=OwnerBookingsState.selected_replacement,
                        on_change=OwnerBookingsState.set_selected_replacement,
                        placeholder="Available times",
                    ),
                    rx.text("The selected time is shown in the business time zone."),
                    rx.hstack(
                        rx.dialog.close(rx.button("Cancel", variant="soft")),
                        rx.button(
                            "Confirm new time",
                            on_click=OwnerBookingsState.confirm_reschedule,
                            disabled=OwnerBookingsState.selected_replacement == "",
                        ),
                        justify="end",
                    ),
                ),
                open=OwnerBookingsState.reschedule_open,
                on_open_change=OwnerBookingsState.set_reschedule_open,
            ),
            align="start",
            width="100%",
        ),
    )
