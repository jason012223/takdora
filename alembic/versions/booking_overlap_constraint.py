"""Apply the booking overlap guard after the full schema exists.

Revision ID: booking_overlap_constraint
Revises: ab60c07336bf
"""

from collections.abc import Sequence

from alembic import op

revision: str = "booking_overlap_constraint"
down_revision: str | Sequence[str] | None = "ab60c07336bf"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.execute(
        """
        ALTER TABLE booking ADD CONSTRAINT booking_active_period_no_overlap
        EXCLUDE USING gist (
          business_id WITH =,
          tsrange(starts_at, ends_at, '[)') WITH &&
        ) WHERE (status IN ('pending', 'scheduled', 'completed'))
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE booking DROP CONSTRAINT IF EXISTS booking_active_period_no_overlap")
