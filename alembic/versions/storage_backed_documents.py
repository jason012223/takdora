"""Add durable private object metadata while retaining legacy bytes for resumable migration.

Revision ID: storage_backed_documents
Revises: invoice_payments_and_outbox
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "storage_backed_documents"
down_revision: str | Sequence[str] | None = "invoice_payments_and_outbox"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("invoicedocument", sa.Column("storage_key", sa.String(320), nullable=True))
    op.add_column("invoicedocument", sa.Column("byte_size", sa.Integer(), nullable=True))
    op.add_column("invoicedocument", sa.Column("checksum_sha256", sa.String(64), nullable=True))
    op.create_unique_constraint(
        "uq_invoice_document_storage_key", "invoicedocument", ["storage_key"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_invoice_document_storage_key", "invoicedocument", type_="unique")
    op.drop_column("invoicedocument", "checksum_sha256")
    op.drop_column("invoicedocument", "byte_size")
    op.drop_column("invoicedocument", "storage_key")
