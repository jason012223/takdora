"""Owner-only dashboard entry with no workspace-switching surface."""

from __future__ import annotations

import reflex as rx

from takdora.auth import AuthenticationError, AuthState
from takdora.business_setup import evaluate_publish_readiness_for_owner, publish_business
from takdora.delivery import delivery_issues_for_owner, retry_delivery_for_owner
from takdora.demo import is_synthetic_demo_owner
from takdora.pages.demo import synthetic_demo_banner
from takdora.tenancy import WorkspaceAccessError, create_workspace, get_workspace_for_owner
from takdora.ui.layouts import owner_layout
from takdora.ui.primitives import feedback


class OwnerDashboardState(AuthState):
    """Derive the active workspace solely from the server-side authenticated owner."""

    workspace_name: str = ""
    dashboard_message: str = ""
    delivery_issues: list[dict[str, str | int]] = []
    is_synthetic_demo: bool = False
    readiness_steps: list[dict[str, str]] = []
    publish_ready: bool = False
    is_published: bool = False
    public_url: str = ""

    def load_dashboard(self) -> rx.event.EventSpec | None:
        try:
            owner = self.require_owner()
            workspace = get_workspace_for_owner(owner)
        except (AuthenticationError, WorkspaceAccessError):
            return rx.redirect("/sign-in")
        self.workspace_name = workspace.name if workspace else ""
        self.is_synthetic_demo = is_synthetic_demo_owner(owner)
        self.delivery_issues = delivery_issues_for_owner(owner)
        if workspace is not None:
            readiness = evaluate_publish_readiness_for_owner(owner)
            missing = set(readiness.missing_required)
            self.readiness_steps = [
                {
                    "title": "Business details",
                    "description": (
                        "Add your business name and public address. "
                        "Check your inbox to verify email."
                    ),
                    "href": "/owner/setup",
                    "action": "Finish details",
                    "status": "done"
                    if not bool(
                        {"Verify email", "Add business name", "Choose a public address"} & missing
                    )
                    else "todo",
                },
                {
                    "title": "Services",
                    "description": "Add at least one service customers can book.",
                    "href": "/owner/services",
                    "action": "Add service",
                    "status": "done" if "Add a service" not in missing else "todo",
                },
                {
                    "title": "Working hours",
                    "description": "Set the days and times customers can choose from.",
                    "href": "/owner/availability",
                    "action": "Set hours",
                    "status": "done" if "Set working hours" not in missing else "todo",
                },
            ]
            self.publish_ready = readiness.ready
            self.is_published = workspace.published_at is not None
            self.public_url = f"/b/{workspace.slug}" if workspace.slug else ""
        else:
            self.readiness_steps = []
            self.publish_ready = False
            self.is_published = False
            self.public_url = ""
        return None

    def start_workspace(self) -> rx.event.EventSpec | None:
        try:
            owner = self.require_owner()
            workspace = create_workspace(owner)
        except (AuthenticationError, WorkspaceAccessError) as error:
            self.dashboard_message = str(error)
            return None
        self.workspace_name = workspace.name
        self.dashboard_message = "Your workspace is ready. Add its essentials next."
        return rx.redirect("/owner/setup")

    def publish_workspace(self) -> None:
        try:
            business = publish_business(self.require_owner())
        except (AuthenticationError, WorkspaceAccessError, ValueError) as error:
            self.dashboard_message = str(error)
            self.load_dashboard()
            return
        self.is_published = business.published_at is not None
        self.public_url = f"/b/{business.slug}"
        self.dashboard_message = "Your public booking page is live. Preview it before sharing."
        self.load_dashboard()

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
        rx.cond(OwnerDashboardState.is_synthetic_demo, synthetic_demo_banner()),
        rx.cond(
            OwnerDashboardState.workspace_name != "",
            rx.vstack(
                rx.heading("Your workspace", size="7"),
                rx.text(OwnerDashboardState.workspace_name),
                rx.text(
                    "Complete the few essentials below, then preview your public booking page."
                ),
                rx.card(
                    rx.vstack(
                        rx.heading("Business readiness", size="5"),
                        rx.text("A clear path to your first public booking page."),
                        rx.foreach(
                            OwnerDashboardState.readiness_steps,
                            lambda step: rx.hstack(
                                rx.vstack(
                                    rx.hstack(
                                        rx.text(step["title"], weight="bold"),
                                        rx.cond(
                                            step["status"] == "done",
                                            rx.badge("Done", color_scheme="green", variant="soft"),
                                            rx.badge(
                                                "To do", color_scheme="orange", variant="soft"
                                            ),
                                        ),
                                        spacing="2",
                                    ),
                                    rx.text(step["description"], size="2"),
                                    spacing="1",
                                    align="start",
                                ),
                                rx.link(step["action"], href=step["href"], size="2", weight="bold"),
                                justify="between",
                                align="center",
                                width="100%",
                            ),
                        ),
                        rx.divider(),
                        rx.cond(
                            OwnerDashboardState.is_published,
                            rx.hstack(
                                rx.text("Your booking page is live.", weight="bold"),
                                rx.link(
                                    "Preview public page",
                                    href=OwnerDashboardState.public_url,
                                    size="2",
                                    weight="bold",
                                ),
                                spacing="3",
                                flex_wrap="wrap",
                            ),
                            rx.cond(
                                OwnerDashboardState.publish_ready,
                                rx.hstack(
                                    rx.text("Everything is ready to publish.", weight="bold"),
                                    rx.button(
                                        "Publish and preview",
                                        on_click=OwnerDashboardState.publish_workspace,
                                    ),
                                    spacing="3",
                                    flex_wrap="wrap",
                                ),
                                rx.text(
                                    "Finish the items above. "
                                    "We will recheck before anything goes public.",
                                    size="2",
                                ),
                            ),
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    width="100%",
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
            rx.card(
                rx.vstack(
                    rx.heading("Start your business workspace", size="4"),
                    rx.text(
                        "Create one private draft. You can complete the details when you are ready."
                    ),
                    rx.button("Create workspace", on_click=OwnerDashboardState.start_workspace),
                    align="start",
                    spacing="3",
                ),
                width="100%",
            ),
        ),
        rx.cond(
            OwnerDashboardState.dashboard_message != "",
            feedback(OwnerDashboardState.dashboard_message),
        ),
    )
