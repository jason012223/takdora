"""Introduce tenant-owned invoice draft persistence.

Revision ID: invoice_drafts
Revises: booking_operation_audit
"""

from collections.abc import Sequence

from alembic import op

revision: str = "invoice_drafts"
down_revision: str | Sequence[str] | None = "booking_operation_audit"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Reflex/SQLModel owns schema generation in the application migration workflow.
    # This reviewed marker keeps the invoice domain in the Alembic revision chain.
    op.execute("SELECT 1")


def downgrade() -> None:
    op.execute("SELECT 1")
