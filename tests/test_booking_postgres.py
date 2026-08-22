"""PostgreSQL exclusion migration contract (server integration runs in Compose)."""

from pathlib import Path


def test_booking_safety_migration_declares_btree_gist_and_half_open_constraint() -> None:
    migration = Path("alembic/versions/booking_safety.py").read_text(encoding="utf-8")
    assert "CREATE EXTENSION IF NOT EXISTS btree_gist" in migration
    assert "booking_active_period_no_overlap" in migration
    assert "tstzrange(starts_at, ends_at, '[)')" in migration
    assert "'pending', 'scheduled', 'completed'" in migration
