"""Owner-only dashboard entry with no workspace-switching surface."""

from __future__ import annotations

import reflex as rx

from takdora.auth import AuthenticationError, AuthState
from takdora.delivery import delivery_issues_for_owner, retry_delivery_for_owner
from takdora.tenancy import WorkspaceAccessError, create_workspace, get_workspace_for_owner
from takdora.ui.layouts import owner_layout
from takdora.ui.primitives import empty_state, feedback


class OwnerDashboardState(AuthState):
    """Derive the active workspace solely from the server-side authenticated owner."""

    workspace_name: str = ""
    dashboard_message: str = ""
    delivery_issues: list[dict[str, str | int]] = []

    def load_dashboard(self) -> rx.event.EventSpec | None:
        try:
            owner = self.require_owner()
            workspace = get_workspace_for_owner(owner)
        except (AuthenticationError, WorkspaceAccessError):
            return rx.redirect("/sign-in")
        self.workspace_name = workspace.name if workspace else ""
        self.delivery_issues = delivery_issues_for_owner(owner)
        return None

    def start_workspace(self) -> None:
        try:
            owner = self.require_owner()
            workspace = create_workspace(owner)
        except (AuthenticationError, WorkspaceAccessError) as error:
            self.dashboard_message = str(error)
            return
        self.workspace_name = workspace.name
        self.dashboard_message = "Your workspace is ready to set up."

    def retry_delivery(self, kind: str, record_id: str) -> None:
        try:
            result = retry_delivery_for_owner(self.require_owner(), kind, int(record_id))  # type: ignore[arg-type]
        except (AuthenticationError, WorkspaceAccessError, ValueError):
            self.dashboard_message = "We could not retry that delivery. Please try again shortly."
            return
        self.dashboard_message = (
            "Confirmation email sent."
            if result == "sent"
            else "Email is still delayed. Please try again shortly."
        )
        self.delivery_issues = delivery_issues_for_owner(self.require_owner())


def owner_dashboard() -> rx.Component:
    return owner_layout(
        rx.cond(
            OwnerDashboardState.workspace_name != "",
            rx.vstack(
                rx.heading("Your business workspace", size="7"),
                rx.text(OwnerDashboardState.workspace_name),
                rx.text("Continue setup to make your public page ready."),
                rx.hstack(
                    rx.link("Manage services", href="/owner/services"),
                    rx.link("Set availability", href="/owner/availability"),
                    spacing="4",
                ),
                rx.foreach(
                    OwnerDashboardState.delivery_issues,
                    lambda issue: rx.card(
                        rx.text(issue["label"], weight="bold"),
                        rx.text(issue["status"]),
                        rx.button(
                            "Retry email",
                            on_click=OwnerDashboardState.retry_delivery(issue["kind"], issue["id"]),
                        ),
                    ),
                ),
                spacing="3",
            ),
            empty_state(
                "Start your business workspace",
                "Create one private draft. You can complete the details when you are ready.",
                "Create workspace",
            ),
        ),
        rx.button("Create workspace", on_click=OwnerDashboardState.start_workspace),
        rx.cond(
            OwnerDashboardState.dashboard_message != "",
            feedback(OwnerDashboardState.dashboard_message),
        ),
    )
