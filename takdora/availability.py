"""The single timezone-aware availability policy and slot-calculation contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import reflex as rx
from sqlmodel import select

from takdora.models import (
    BookingRules,
    Business,
    BusinessService,
    DateClosure,
    OwnerAccount,
    WeeklyAvailabilityBlock,
)
from takdora.tenancy import WorkspaceAccessError, get_workspace_for_owner, require_owner

DEFAULT_SLOT_INTERVAL_MINUTES = 30
DEFAULT_MINIMUM_LEAD_MINUTES = 60
DEFAULT_BOOKING_HORIZON_DAYS = 30
DEFAULT_BUFFER_MINUTES = 0


@dataclass(frozen=True)
class WeeklyBlockInput:
    weekday: int | str
    start_time: time | str
    end_time: time | str


@dataclass(frozen=True)
class BookingRulesInput:
    slot_interval_minutes: int | str = DEFAULT_SLOT_INTERVAL_MINUTES
    minimum_lead_minutes: int | str = DEFAULT_MINIMUM_LEAD_MINUTES
    booking_horizon_days: int | str = DEFAULT_BOOKING_HORIZON_DAYS
    buffer_minutes: int | str = DEFAULT_BUFFER_MINUTES


@dataclass(frozen=True)
class OccupiedInterval:
    """Neutral future-booking input. Customer identity is intentionally impossible here."""

    start_at: datetime
    end_at: datetime
    state: str = "Booked"


@dataclass(frozen=True)
class AvailabilitySlot:
    start_at_utc: datetime
    end_at_utc: datetime
    local_label: str
    state: str = "Available"


def _authorized_business(owner: OwnerAccount | None) -> Business:
    authorized_owner = require_owner(owner)
    business = get_workspace_for_owner(authorized_owner)
    if business is None:
        raise WorkspaceAccessError("Workspace not found.")
    return business


def _parse_time(value: time | str) -> time:
    if isinstance(value, time):
        return value.replace(second=0, microsecond=0)
    try:
        return time.fromisoformat(value).replace(second=0, microsecond=0)
    except (TypeError, ValueError) as error:
        raise ValueError("Use a valid local time.") from error


def validate_weekly_block(data: WeeklyBlockInput) -> WeeklyBlockInput:
    try:
        weekday = int(data.weekday)
    except (TypeError, ValueError) as error:
        raise ValueError("Choose a valid weekday.") from error
    if weekday not in range(7):
        raise ValueError("Choose a valid weekday.")
    start = _parse_time(data.start_time)
    end = _parse_time(data.end_time)
    if start >= end:
        raise ValueError("End time must be after start time.")
    return WeeklyBlockInput(weekday=weekday, start_time=start, end_time=end)


def validate_booking_rules(data: BookingRulesInput) -> BookingRulesInput:
    try:
        interval = int(data.slot_interval_minutes)
        lead = int(data.minimum_lead_minutes)
        horizon = int(data.booking_horizon_days)
        buffer = int(data.buffer_minutes)
    except (TypeError, ValueError) as error:
        raise ValueError("Booking rules must use whole minutes and days.") from error
    if interval not in (15, 30, 60):
        raise ValueError("Slot interval must be 15, 30, or 60 minutes.")
    if not 0 <= lead <= 10080:
        raise ValueError("Lead time must be between 0 minutes and 7 days.")
    if not 1 <= horizon <= 180:
        raise ValueError("Booking horizon must be between 1 and 180 days.")
    if not 0 <= buffer <= 240:
        raise ValueError("Buffer must be between 0 and 240 minutes.")
    return BookingRulesInput(interval, lead, horizon, buffer)


def _assert_non_overlapping(blocks: list[WeeklyBlockInput]) -> None:
    ordered = sorted(blocks, key=lambda item: (int(item.weekday), item.start_time))
    for previous, current in zip(ordered, ordered[1:], strict=False):
        if previous.weekday == current.weekday and previous.end_time >= current.start_time:
            raise ValueError("Availability blocks cannot overlap or touch.")


def get_or_create_booking_rules(business_id: int) -> BookingRules:
    with rx.session() as session:
        rules = session.exec(
            select(BookingRules).where(BookingRules.business_id == business_id)
        ).first()
        if rules is None:
            rules = BookingRules(business_id=business_id)
            session.add(rules)
            session.commit()
            session.refresh(rules)
        return rules


def replace_weekly_blocks(
    owner: OwnerAccount | None, blocks: list[WeeklyBlockInput]
) -> list[WeeklyAvailabilityBlock]:
    """Validate the entire candidate schedule before replacing any persisted policy."""
    business = _authorized_business(owner)
    normalized = [validate_weekly_block(block) for block in blocks]
    _assert_non_overlapping(normalized)
    with rx.session() as session:
        existing = session.exec(
            select(WeeklyAvailabilityBlock).where(
                WeeklyAvailabilityBlock.business_id == business.id
            )
        ).all()
        for block in existing:
            session.delete(block)
        persisted = [
            WeeklyAvailabilityBlock(
                business_id=business.id or 0,
                weekday=int(block.weekday),
                start_time=_parse_time(block.start_time),
                end_time=_parse_time(block.end_time),
            )
            for block in normalized
        ]
        session.add_all(persisted)
        session.commit()
        for block in persisted:
            session.refresh(block)
        return persisted


def update_weekly_block(
    owner: OwnerAccount | None, block_id: int, candidate: WeeklyBlockInput
) -> WeeklyAvailabilityBlock:
    business = _authorized_business(owner)
    normalized = validate_weekly_block(candidate)
    with rx.session() as session:
        stored = session.get(WeeklyAvailabilityBlock, block_id)
        if stored is None or stored.business_id != business.id:
            raise WorkspaceAccessError("Schedule block not found.")
        current = session.exec(
            select(WeeklyAvailabilityBlock).where(
                WeeklyAvailabilityBlock.business_id == business.id
            )
        ).all()
        candidates = [
            WeeklyBlockInput(
                weekday=normalized.weekday if block.id == stored.id else block.weekday,
                start_time=normalized.start_time if block.id == stored.id else block.start_time,
                end_time=normalized.end_time if block.id == stored.id else block.end_time,
            )
            for block in current
        ]
        _assert_non_overlapping(candidates)
        stored.weekday = int(normalized.weekday)
        stored.start_time = _parse_time(normalized.start_time)
        stored.end_time = _parse_time(normalized.end_time)
        stored.updated_at = datetime.now(UTC)
        session.add(stored)
        session.commit()
        session.refresh(stored)
        return stored


def remove_weekly_block(owner: OwnerAccount | None, block_id: int) -> None:
    business = _authorized_business(owner)
    with rx.session() as session:
        block = session.get(WeeklyAvailabilityBlock, block_id)
        if block is None or block.business_id != business.id:
            raise WorkspaceAccessError("Schedule block not found.")
        session.delete(block)
        session.commit()


def weekly_blocks_for_owner(owner: OwnerAccount | None) -> list[WeeklyAvailabilityBlock]:
    business = _authorized_business(owner)
    with rx.session() as session:
        return list(
            session.exec(
                select(WeeklyAvailabilityBlock)
                .where(WeeklyAvailabilityBlock.business_id == business.id)
                .order_by(WeeklyAvailabilityBlock.weekday, WeeklyAvailabilityBlock.start_time)
            ).all()
        )


def has_weekly_working_hours_for_business(business_id: int) -> bool:
    with rx.session() as session:
        return (
            session.exec(
                select(WeeklyAvailabilityBlock.id).where(
                    WeeklyAvailabilityBlock.business_id == business_id
                )
            ).first()
            is not None
        )


def add_date_closure(owner: OwnerAccount | None, local_date: date) -> DateClosure:
    business = _authorized_business(owner)
    with rx.session() as session:
        existing = session.exec(
            select(DateClosure).where(
                DateClosure.business_id == business.id, DateClosure.local_date == local_date
            )
        ).first()
        if existing is not None:
            return existing
        closure = DateClosure(business_id=business.id or 0, local_date=local_date)
        session.add(closure)
        session.commit()
        session.refresh(closure)
        return closure


def update_booking_rules(owner: OwnerAccount | None, data: BookingRulesInput) -> BookingRules:
    business = _authorized_business(owner)
    validated = validate_booking_rules(data)
    rules = get_or_create_booking_rules(business.id or 0)
    with rx.session() as session:
        stored = session.get(BookingRules, rules.id)
        if stored is None or stored.business_id != business.id:
            raise WorkspaceAccessError("Booking rules not found.")
        stored.slot_interval_minutes = int(validated.slot_interval_minutes)
        stored.minimum_lead_minutes = int(validated.minimum_lead_minutes)
        stored.booking_horizon_days = int(validated.booking_horizon_days)
        stored.buffer_minutes = int(validated.buffer_minutes)
        stored.updated_at = datetime.now(UTC)
        session.add(stored)
        session.commit()
        session.refresh(stored)
        return stored


def booking_rules_for_owner(owner: OwnerAccount | None) -> BookingRules:
    """Load the sole rules record through the owner-derived business boundary."""
    business = _authorized_business(owner)
    return get_or_create_booking_rules(business.id or 0)


def _zone(value: str) -> ZoneInfo:
    try:
        return ZoneInfo(value)
    except ZoneInfoNotFoundError as error:
        raise ValueError("Business time zone is invalid.") from error


def calculate_slots(
    *,
    service: BusinessService | None,
    timezone_name: str,
    blocks: list[WeeklyAvailabilityBlock],
    rules: BookingRules,
    week_start: date,
    closures: set[date] | None = None,
    occupied: tuple[OccupiedInterval, ...] = (),
    now: datetime | None = None,
) -> tuple[AvailabilitySlot, ...]:
    """Return immutable UTC slots for a bounded local ISO week, never browser-derived times."""
    if service is None or not service.is_active or service.fixed_duration_minutes <= 0:
        return ()
    try:
        valid_rules = validate_booking_rules(
            BookingRulesInput(
                rules.slot_interval_minutes,
                rules.minimum_lead_minutes,
                rules.booking_horizon_days,
                rules.buffer_minutes,
            )
        )
    except ValueError:
        return ()
    zone = _zone(timezone_name)
    current = (now or datetime.now(UTC)).astimezone(UTC)
    local_today = current.astimezone(zone).date()
    earliest = current + timedelta(minutes=int(valid_rules.minimum_lead_minutes))
    last_date = local_today + timedelta(days=int(valid_rules.booking_horizon_days))
    closures = closures or set()
    output: list[AvailabilitySlot] = []
    for offset in range(7):
        local_date = week_start + timedelta(days=offset)
        if local_date in closures or local_date > last_date:
            continue
        for block in (item for item in blocks if item.weekday == local_date.weekday()):
            cursor = datetime.combine(local_date, block.start_time, tzinfo=zone)
            end_local = datetime.combine(local_date, block.end_time, tzinfo=zone)
            while cursor + timedelta(minutes=service.fixed_duration_minutes) <= end_local:
                end = cursor + timedelta(minutes=service.fixed_duration_minutes)
                start_utc = cursor.astimezone(UTC)
                end_utc = end.astimezone(UTC)
                padded_start = start_utc - timedelta(minutes=int(valid_rules.buffer_minutes))
                padded_end = end_utc + timedelta(minutes=int(valid_rules.buffer_minutes))
                conflict = any(
                    item.start_at.astimezone(UTC) < padded_end
                    and item.end_at.astimezone(UTC) > padded_start
                    for item in occupied
                )
                if start_utc >= earliest and not conflict:
                    output.append(
                        AvailabilitySlot(
                            start_at_utc=start_utc,
                            end_at_utc=end_utc,
                            local_label=(
                                f"{cursor.strftime('%a, %b')} {cursor.day} - "
                                f"{cursor.strftime('%I:%M %p').lstrip('0')}"
                            ),
                        )
                    )
                cursor += timedelta(minutes=int(valid_rules.slot_interval_minutes))
    return tuple(output)


def slots_for_owner_service(
    owner: OwnerAccount | None, service_id: int, week_start: date, *, now: datetime | None = None
) -> tuple[AvailabilitySlot, ...]:
    """Owner preview entrypoint: resolve all tenant data server-side before calculation."""
    business = _authorized_business(owner)
    with rx.session() as session:
        service = session.get(BusinessService, service_id)
        if service is None or service.business_id != business.id:
            raise WorkspaceAccessError("Service not found.")
        blocks = list(
            session.exec(
                select(WeeklyAvailabilityBlock).where(
                    WeeklyAvailabilityBlock.business_id == business.id
                )
            ).all()
        )
        rules = session.exec(
            select(BookingRules).where(BookingRules.business_id == business.id)
        ).first()
        closures = set(
            session.exec(
                select(DateClosure.local_date).where(DateClosure.business_id == business.id)
            ).all()
        )
    if rules is None:
        rules = BookingRules(business_id=business.id or 0)
    return calculate_slots(
        service=service,
        timezone_name=business.timezone,
        blocks=blocks,
        rules=rules,
        week_start=week_start,
        closures=closures,
        now=now,
    )
