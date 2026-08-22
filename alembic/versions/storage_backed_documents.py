"""Add durable private object metadata while retaining legacy bytes for resumable migration.

Revision ID: storage_backed_documents
Revises: invoice_payments_and_outbox
"""

from collections.abc import Sequence

from alembic import op

revision: str = "storage_backed_documents"
down_revision: str | Sequence[str] | None = "invoice_payments_and_outbox"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply only when upgrading a legacy schema with these tables already present."""
    op.execute(
        """
        DO $$
        BEGIN
          IF to_regclass('public.invoicedocument') IS NOT NULL THEN
            ALTER TABLE invoicedocument ADD COLUMN IF NOT EXISTS storage_key VARCHAR(320);
            ALTER TABLE invoicedocument ADD COLUMN IF NOT EXISTS byte_size INTEGER;
            ALTER TABLE invoicedocument ADD COLUMN IF NOT EXISTS checksum_sha256 VARCHAR(64);
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_invoice_document_storage_key') THEN
              ALTER TABLE invoicedocument ADD CONSTRAINT uq_invoice_document_storage_key UNIQUE (storage_key);
            END IF;
          END IF;
          IF to_regclass('public.business') IS NOT NULL THEN
            ALTER TABLE business ADD COLUMN IF NOT EXISTS logo_storage_key VARCHAR(320);
            ALTER TABLE business ADD COLUMN IF NOT EXISTS logo_content_type VARCHAR(80);
            ALTER TABLE business ADD COLUMN IF NOT EXISTS logo_byte_size INTEGER;
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_business_logo_storage_key') THEN
              ALTER TABLE business ADD CONSTRAINT uq_business_logo_storage_key UNIQUE (logo_storage_key);
            END IF;
          END IF;
        END $$
        """
    )


def downgrade() -> None:
    op.drop_constraint("uq_invoice_document_storage_key", "invoicedocument", type_="unique")
    op.drop_column("invoicedocument", "checksum_sha256")
    op.drop_column("invoicedocument", "byte_size")
    op.drop_column("invoicedocument", "storage_key")
    op.drop_constraint("uq_business_logo_storage_key", "business", type_="unique")
    op.drop_column("business", "logo_byte_size")
    op.drop_column("business", "logo_content_type")
    op.drop_column("business", "logo_storage_key")
