"""Owner-only fixed-duration service catalog."""

from __future__ import annotations

import reflex as rx

from takdora.auth import AuthenticationError, AuthState
from takdora.services import ServiceInput, create_service, services_for_owner, set_service_active
from takdora.tenancy import WorkspaceAccessError
from takdora.ui.layouts import owner_layout
from takdora.ui.primitives import feedback, status_badge


class ServicesState(AuthState):
    name: str = ""
    duration: str = "60"
    description: str = ""
    price: str = ""
    catalog_message: str = ""
    service_rows: list[dict[str, str]] = []

    def load_services(self) -> rx.event.EventSpec | None:
        try:
            records = services_for_owner(self.require_owner())
        except (AuthenticationError, WorkspaceAccessError):
            return rx.redirect("/sign-in")
        self.service_rows = [
            {
                "id": str(item.id or 0),
                "name": item.name,
                "duration": f"{item.fixed_duration_minutes} minutes",
                "price": "Price on request" if item.price is None else f"₱{item.price:,.2f}",
                "state": "Active" if item.is_active else "Inactive",
            }
            for item in records
        ]
        return None

    def add_service(self) -> None:
        try:
            create_service(
                self.require_owner(),
                ServiceInput(self.name, self.duration, self.description, self.price),
            )
        except (AuthenticationError, WorkspaceAccessError, ValueError) as error:
            self.catalog_message = str(error)
            return
        self.name = self.description = self.price = ""
        self.duration = "60"
        self.catalog_message = "Service saved."
        self.load_services()

    def toggle_service(self, service_id: str, active: bool) -> None:
        try:
            set_service_active(self.require_owner(), int(service_id), active=active)
        except (AuthenticationError, WorkspaceAccessError, ValueError) as error:
            self.catalog_message = str(error)
            return
        self.catalog_message = "Service reactivated." if active else "Service deactivated."
        self.load_services()


def services_page() -> rx.Component:
    return owner_layout(
        rx.heading("Services", size="7"),
        rx.text("Add the fixed-duration services customers can book. Price is optional."),
        rx.card(
            rx.vstack(
                rx.input(
                    placeholder="Service name",
                    value=ServicesState.name,
                    on_change=ServicesState.set_name,
                ),
                rx.input(
                    type="number",
                    min="1",
                    max="720",
                    placeholder="Duration in minutes",
                    value=ServicesState.duration,
                    on_change=ServicesState.set_duration,
                ),
                rx.text_area(
                    placeholder="Description (optional)",
                    value=ServicesState.description,
                    on_change=ServicesState.set_description,
                ),
                rx.input(
                    placeholder="Price in PHP (optional)",
                    value=ServicesState.price,
                    on_change=ServicesState.set_price,
                ),
                rx.button("Add service", on_click=ServicesState.add_service),
                spacing="3",
                width="100%",
            ),
            width="100%",
        ),
        rx.foreach(
            ServicesState.service_rows,
            lambda item: rx.card(
                rx.hstack(
                    rx.vstack(
                        rx.heading(item["name"], size="4"),
                        rx.text(item["duration"]),
                        rx.text(item["price"]),
                        align="start",
                    ),
                    rx.vstack(
                        status_badge(item["state"], tone="success"),
                        rx.cond(
                            item["state"] == "Active",
                            rx.button(
                                "Deactivate",
                                variant="soft",
                                on_click=ServicesState.toggle_service(item["id"], False),
                            ),
                            rx.button(
                                "Reactivate",
                                variant="soft",
                                on_click=ServicesState.toggle_service(item["id"], True),
                            ),
                        ),
                        align="end",
                    ),
                    justify="between",
                    width="100%",
                ),
                width="100%",
            ),
        ),
        rx.cond(ServicesState.catalog_message != "", feedback(ServicesState.catalog_message)),
    )
