"""Deterministic slot engine contracts."""

from datetime import UTC, date, datetime, time, timedelta

from takdora.availability import AvailabilitySlot, OccupiedInterval, calculate_slots
from takdora.models import BookingRules, BusinessService, WeeklyAvailabilityBlock


def _defaults() -> BookingRules:
    return BookingRules(business_id=1)


def _service(*, active: bool = True) -> BusinessService:
    return BusinessService(
        business_id=1, name="Consultation", fixed_duration_minutes=60, is_active=active
    )


def test_active_service_returns_fitting_interval_aligned_slots_in_utc() -> None:
    slots = calculate_slots(
        service=_service(),
        timezone_name="Asia/Manila",
        blocks=[
            WeeklyAvailabilityBlock(business_id=1, weekday=0, start_time=time(9), end_time=time(12))
        ],
        rules=_defaults(),
        week_start=date(2026, 8, 24),
        now=datetime(2026, 8, 20, tzinfo=UTC),
    )
    assert [slot.start_at_utc.astimezone().minute for slot in slots] == [0, 30, 0, 30, 0]
    assert all(slot.start_at_utc.tzinfo is UTC for slot in slots)
    assert all(isinstance(slot, AvailabilitySlot) for slot in slots)


def test_inactive_service_and_occupied_intervals_remove_bookable_slots() -> None:
    block = WeeklyAvailabilityBlock(business_id=1, weekday=0, start_time=time(9), end_time=time(12))
    common = dict(
        timezone_name="Asia/Manila",
        blocks=[block],
        rules=_defaults(),
        week_start=date(2026, 8, 24),
        now=datetime(2026, 8, 20, tzinfo=UTC),
    )
    assert calculate_slots(service=_service(active=False), **common) == ()
    occupied = OccupiedInterval(
        start_at=datetime(2026, 8, 24, 1, tzinfo=UTC), end_at=datetime(2026, 8, 24, 2, tzinfo=UTC)
    )
    assert len(calculate_slots(service=_service(), occupied=(occupied,), **common)) < 5


def test_closure_and_lead_time_apply_in_the_business_local_date() -> None:
    slots = calculate_slots(
        service=_service(),
        timezone_name="Asia/Manila",
        blocks=[
            WeeklyAvailabilityBlock(business_id=1, weekday=0, start_time=time(9), end_time=time(12))
        ],
        rules=_defaults(),
        week_start=date(2026, 8, 24),
        closures={date(2026, 8, 24)},
        now=datetime(2026, 8, 20, tzinfo=UTC),
    )
    assert slots == ()


def test_buffer_blocks_adjacent_conflicts_without_customer_data() -> None:
    rules = BookingRules(business_id=1, buffer_minutes=30)
    occupied = OccupiedInterval(
        start_at=datetime(2026, 8, 24, 2, tzinfo=UTC),
        end_at=datetime(2026, 8, 24, 3, tzinfo=UTC),
    )
    slots = calculate_slots(
        service=_service(),
        timezone_name="Asia/Manila",
        blocks=[
            WeeklyAvailabilityBlock(business_id=1, weekday=0, start_time=time(9), end_time=time(12))
        ],
        rules=rules,
        week_start=date(2026, 8, 24),
        occupied=(occupied,),
        now=datetime(2026, 8, 20, tzinfo=UTC),
    )
    assert all(
        slot.start_at_utc + timedelta(hours=1, minutes=30) <= occupied.start_at
        or slot.start_at_utc >= occupied.end_at + timedelta(minutes=30)
        for slot in slots
    )
