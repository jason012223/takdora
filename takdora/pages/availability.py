"""Owner schedule setup and privacy-safe availability preview."""

from __future__ import annotations

from datetime import date, timedelta

import reflex as rx

from takdora.auth import AuthenticationError, AuthState
from takdora.availability import (
    BookingRulesInput,
    WeeklyBlockInput,
    add_date_closure,
    booking_rules_for_owner,
    remove_weekly_block,
    replace_weekly_blocks,
    slots_for_owner_service,
    update_booking_rules,
    weekly_blocks_for_owner,
)
from takdora.services import services_for_owner
from takdora.tenancy import WorkspaceAccessError, get_workspace_for_owner
from takdora.ui.layouts import owner_layout
from takdora.ui.primitives import availability_calendar, feedback


class AvailabilityState(AuthState):
    weekday: str = "0"
    start_time: str = "09:00"
    end_time: str = "17:00"
    closure_date: str = ""
    slot_interval: str = "30"
    lead_minutes: str = "60"
    horizon_days: str = "30"
    buffer_minutes: str = "0"
    selected_service_id: str = ""
    schedule_message: str = ""
    timezone_label: str = ""
    blocks: list[dict[str, str]] = []
    services: list[str] = []
    preview_slots: list[tuple[str, str]] = []

    def load_availability(self) -> rx.event.EventSpec | None:
        try:
            owner = self.require_owner()
            business = get_workspace_for_owner(owner)
            if business is None:
                raise WorkspaceAccessError("Workspace not found.")
            records = weekly_blocks_for_owner(owner)
            service_records = [item for item in services_for_owner(owner) if item.is_active]
            rules = booking_rules_for_owner(owner)
        except (AuthenticationError, WorkspaceAccessError):
            return rx.redirect("/sign-in")
        self.timezone_label = business.timezone
        self.slot_interval = str(rules.slot_interval_minutes)
        self.lead_minutes = str(rules.minimum_lead_minutes)
        self.horizon_days = str(rules.booking_horizon_days)
        self.buffer_minutes = str(rules.buffer_minutes)
        self.blocks = [
            {
                "id": str(item.id or 0),
                "day": ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")[item.weekday],
                "time": f"{item.start_time.strftime('%H:%M')}–{item.end_time.strftime('%H:%M')}",
            }
            for item in records
        ]
        self.services = [f"{item.id or 0}: {item.name}" for item in service_records]
        if not self.selected_service_id and self.services:
            self.selected_service_id = self.services[0]
        return None

    def add_block(self) -> None:
        try:
            owner = self.require_owner()
            current = weekly_blocks_for_owner(owner)
            replace_weekly_blocks(
                owner,
                [
                    *[
                        WeeklyBlockInput(item.weekday, item.start_time, item.end_time)
                        for item in current
                    ],
                    WeeklyBlockInput(self.weekday, self.start_time, self.end_time),
                ],
            )
        except (AuthenticationError, WorkspaceAccessError, ValueError) as error:
            self.schedule_message = str(error)
            return
        self.schedule_message = "Working hours saved."
        self.load_availability()

    def delete_block(self, block_id: str) -> None:
        try:
            remove_weekly_block(self.require_owner(), int(block_id))
        except (AuthenticationError, WorkspaceAccessError, ValueError) as error:
            self.schedule_message = str(error)
            return
        self.schedule_message = "Working hours updated."
        self.load_availability()

    def save_booking_rules(self) -> None:
        try:
            update_booking_rules(
                self.require_owner(),
                BookingRulesInput(
                    self.slot_interval,
                    self.lead_minutes,
                    self.horizon_days,
                    self.buffer_minutes,
                ),
            )
        except (AuthenticationError, WorkspaceAccessError, ValueError) as error:
            self.schedule_message = str(error)
            return
        self.schedule_message = "Booking rules saved."

    def close_date(self) -> None:
        try:
            add_date_closure(self.require_owner(), date.fromisoformat(self.closure_date))
        except (AuthenticationError, WorkspaceAccessError, ValueError) as error:
            self.schedule_message = str(error)
            return
        self.schedule_message = "Date closed. Customers will not be able to book it."
        self.closure_date = ""

    def load_preview(self) -> None:
        try:
            service_id = int(self.selected_service_id.split(":", maxsplit=1)[0])
            today = date.today()
            monday = today - timedelta(days=today.weekday())
            slots = slots_for_owner_service(self.require_owner(), service_id, monday)
        except (AuthenticationError, WorkspaceAccessError, ValueError):
            self.preview_slots = []
            self.schedule_message = (
                "Choose an active service and working hours to preview availability."
            )
            return
        self.preview_slots = [(item.local_label, item.state) for item in slots]


def availability_page() -> rx.Component:
    return owner_layout(
        rx.heading("Availability", size="7"),
        rx.text("Set recurring working hours in your business time zone."),
        rx.text(AvailabilityState.timezone_label, weight="medium"),
        rx.card(
            rx.vstack(
                rx.select(
                    ["0", "1", "2", "3", "4", "5", "6"],
                    value=AvailabilityState.weekday,
                    on_change=AvailabilityState.set_weekday,
                    aria_label="Weekday",
                ),
                rx.input(
                    type="time",
                    value=AvailabilityState.start_time,
                    on_change=AvailabilityState.set_start_time,
                ),
                rx.input(
                    type="time",
                    value=AvailabilityState.end_time,
                    on_change=AvailabilityState.set_end_time,
                ),
                rx.button("Add working hours", on_click=AvailabilityState.add_block),
                spacing="3",
            ),
            width="100%",
        ),
        rx.foreach(
            AvailabilityState.blocks,
            lambda item: rx.hstack(
                rx.text(item["day"]),
                rx.text(item["time"]),
                rx.button(
                    "Remove", variant="soft", on_click=AvailabilityState.delete_block(item["id"])
                ),
                justify="between",
                width="100%",
                class_name="availability-block",
                draggable="true",
                data_schedule_block=item["id"],
            ),
        ),
        rx.details(
            rx.summary("Booking rules (optional)"),
            rx.vstack(
                rx.select(
                    ["15", "30", "60"],
                    value=AvailabilityState.slot_interval,
                    on_change=AvailabilityState.set_slot_interval,
                    aria_label="Slot interval in minutes",
                ),
                rx.input(
                    type="number",
                    value=AvailabilityState.lead_minutes,
                    on_change=AvailabilityState.set_lead_minutes,
                    aria_label="Minimum lead time in minutes",
                ),
                rx.input(
                    type="number",
                    value=AvailabilityState.horizon_days,
                    on_change=AvailabilityState.set_horizon_days,
                    aria_label="Booking horizon in days",
                ),
                rx.input(
                    type="number",
                    value=AvailabilityState.buffer_minutes,
                    on_change=AvailabilityState.set_buffer_minutes,
                    aria_label="Buffer between appointments in minutes",
                ),
                rx.button("Save booking rules", on_click=AvailabilityState.save_booking_rules),
                spacing="3",
            ),
        ),
        rx.card(
            rx.hstack(
                rx.input(
                    type="date",
                    value=AvailabilityState.closure_date,
                    on_change=AvailabilityState.set_closure_date,
                    aria_label="Date to close",
                ),
                rx.button("Close date", variant="soft", on_click=AvailabilityState.close_date),
            ),
            width="100%",
        ),
        rx.card(
            rx.vstack(
                rx.heading("Week preview", size="5"),
                rx.select(
                    AvailabilityState.services,
                    value=AvailabilityState.selected_service_id,
                    on_change=AvailabilityState.set_selected_service_id,
                    aria_label="Service to preview",
                ),
                rx.button("Show available times", on_click=AvailabilityState.load_preview),
                availability_calendar(AvailabilityState.preview_slots),
                spacing="3",
            ),
            width="100%",
        ),
        rx.cond(
            AvailabilityState.schedule_message != "", feedback(AvailabilityState.schedule_message)
        ),
    )
