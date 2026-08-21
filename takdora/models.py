"""Minimal persistence model used only to prove the application foundation."""

from __future__ import annotations

from datetime import UTC, datetime

import reflex as rx
from sqlmodel import Field


class FoundationProbe(rx.Model, table=True):
    """A non-sensitive row written by the readiness diagnostic control."""

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


def record_probe() -> FoundationProbe:
    """Persist then retrieve a diagnostic row using Reflex's configured database session."""
    with rx.session() as session:
        probe = FoundationProbe()
        session.add(probe)
        session.commit()
        session.refresh(probe)
        return probe
