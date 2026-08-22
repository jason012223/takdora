"""Review lifecycle audit and post-commit booking update persistence.

Revision ID: booking_operation_audit
Revises: booking_confirmation_outbox
"""

from collections.abc import Sequence

from alembic import op

revision: str = "booking_operation_audit"
down_revision: str | Sequence[str] | None = "booking_confirmation_outbox"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("SELECT 1")


def downgrade() -> None:
    op.execute("SELECT 1")
