"""Small, autosaving owner setup flow."""

from __future__ import annotations

import reflex as rx

from takdora.auth import AuthenticationError, AuthState
from takdora.business_setup import BusinessProfileInput, save_profile
from takdora.tenancy import WorkspaceAccessError
from takdora.ui.layouts import owner_layout
from takdora.ui.primitives import feedback


class OnboardingState(AuthState):
    name: str = ""
    slug: str = ""
    setup_message: str = ""

    def save_essentials(self) -> None:
        try:
            save_profile(self.require_owner(), BusinessProfileInput(name=self.name, slug=self.slug))
        except (AuthenticationError, WorkspaceAccessError, ValueError) as error:
            self.setup_message = str(error)
            return
        self.setup_message = "Saved. You can return anytime to finish setup."


def onboarding_page() -> rx.Component:
    return owner_layout(
        rx.heading("Set up your business", size="7"),
        rx.text("Start with the essentials. Optional details can wait."),
        rx.input(
            placeholder="Business name",
            value=OnboardingState.name,
            on_change=OnboardingState.set_name,
            aria_label="Business name",
        ),
        rx.input(
            placeholder="Public address, for example luna-studio",
            value=OnboardingState.slug,
            on_change=OnboardingState.set_slug,
            aria_label="Public address",
        ),
        rx.button("Save essentials", on_click=OnboardingState.save_essentials),
        rx.cond(OnboardingState.setup_message != "", feedback(OnboardingState.setup_message)),
        rx.divider(),
        rx.card(
            rx.vstack(
                rx.heading("Then finish your booking setup", size="5"),
                rx.text("Your public address will be takdora.app/b/"),
                rx.text(OnboardingState.slug, weight="bold"),
                rx.text(
                    "Next, add one service and your working hours. "
                    "The dashboard will show when you are ready to publish."
                ),
                rx.hstack(
                    rx.link("Add a service", href="/owner/services", weight="bold"),
                    rx.link("Set working hours", href="/owner/availability", weight="bold"),
                    rx.link("Review readiness", href="/owner", weight="bold"),
                    spacing="4",
                    flex_wrap="wrap",
                ),
                rx.text(
                    "Optional later: invoice identity, contact details, logo, and color.", size="2"
                ),
                spacing="3",
                width="100%",
            ),
            width="100%",
        ),
    )
