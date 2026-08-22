"""Record immutable issued invoice and private document persistence.

Revision ID: issued_invoice_snapshots
Revises: invoice_drafts
"""

from collections.abc import Sequence

from alembic import op

revision: str = "issued_invoice_snapshots"
down_revision: str | Sequence[str] | None = "invoice_drafts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("SELECT 1")


def downgrade() -> None:
    op.execute("SELECT 1")
