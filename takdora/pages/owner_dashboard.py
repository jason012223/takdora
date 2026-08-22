"""Owner-only dashboard entry with no workspace-switching surface."""

from __future__ import annotations

import reflex as rx

from takdora.auth import AuthenticationError, AuthState
from takdora.tenancy import WorkspaceAccessError, create_workspace, get_workspace_for_owner
from takdora.ui.layouts import owner_layout
from takdora.ui.primitives import empty_state, feedback


class OwnerDashboardState(AuthState):
    """Derive the active workspace solely from the server-side authenticated owner."""

    workspace_name: str = ""
    dashboard_message: str = ""

    def load_dashboard(self) -> rx.event.EventSpec | None:
        try:
            owner = self.require_owner()
            workspace = get_workspace_for_owner(owner)
        except (AuthenticationError, WorkspaceAccessError):
            return rx.redirect("/sign-in")
        self.workspace_name = workspace.name if workspace else ""
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


def owner_dashboard() -> rx.Component:
    return owner_layout(
        rx.cond(
            OwnerDashboardState.workspace_name != "",
            rx.vstack(
                rx.heading("Your business workspace", size="7"),
                rx.text(OwnerDashboardState.workspace_name),
                rx.text("Continue setup to make your public page ready."),
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
