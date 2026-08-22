"""Add PostgreSQL's durable active-booking overlap guard.

Revision ID: booking_safety
Revises: 8a02ea306945
"""

from collections.abc import Sequence

from alembic import op

revision: str = "booking_safety"
down_revision: str | Sequence[str] | None = "8a02ea306945"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.execute(
        """
        DO $$
        BEGIN
          IF to_regclass('public.booking') IS NOT NULL
             AND NOT EXISTS (
               SELECT 1 FROM pg_constraint
               WHERE conname = 'booking_active_period_no_overlap'
             ) THEN
            ALTER TABLE booking ADD CONSTRAINT booking_active_period_no_overlap
            EXCLUDE USING gist (
              business_id WITH =,
              tsrange(starts_at, ends_at, '[)') WITH &&
            ) WHERE (status IN ('pending', 'scheduled', 'completed'));
          END IF;
        END $$
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE booking DROP CONSTRAINT IF EXISTS booking_active_period_no_overlap")
