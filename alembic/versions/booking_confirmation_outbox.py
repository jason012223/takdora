"""Declare booking confirmation outbox as a reviewed post-commit boundary.

Revision ID: booking_confirmation_outbox
Revises: booking_safety
"""

from collections.abc import Sequence

from alembic import op

revision: str = "booking_confirmation_outbox"
down_revision: str | Sequence[str] | None = "booking_safety"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Reflex owns model table creation in local development; this revision retains
    # an explicit reviewed migration chain for production schema review.
    op.execute("SELECT 1")


def downgrade() -> None:
    op.execute("SELECT 1")
