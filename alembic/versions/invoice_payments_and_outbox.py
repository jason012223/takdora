"""Record manual payment and invoice-email outbox persistence.

Revision ID: invoice_payments_and_outbox
Revises: issued_invoice_snapshots
"""

from collections.abc import Sequence

from alembic import op

revision: str = "invoice_payments_and_outbox"
down_revision: str | Sequence[str] | None = "issued_invoice_snapshots"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("SELECT 1")


def downgrade() -> None:
    op.execute("SELECT 1")
