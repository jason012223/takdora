"""Idempotent maintenance commands for due workspace deletion."""

from __future__ import annotations

from datetime import UTC, datetime

import reflex as rx
from sqlmodel import select

from takdora.delivery import process_due_deliveries
from takdora.models import Business


def purge_due_workspaces(now: datetime | None = None) -> int:
    """Permanently remove only inactive tenant roots whose retention deadline is due."""
    due_at = now or datetime.now(UTC)
    with rx.session() as session:
        due_businesses = session.exec(
            select(Business).where(
                Business.is_active.is_(False),
                Business.purge_after.is_not(None),
                Business.purge_after <= due_at,
            )
        ).all()
        for business in due_businesses:
            session.delete(business)
        session.commit()
        return len(due_businesses)


if __name__ == "__main__":
    purge_due_workspaces()
    process_due_deliveries()
