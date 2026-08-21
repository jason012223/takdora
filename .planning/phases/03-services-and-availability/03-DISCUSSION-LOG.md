# Phase 3: Services and Availability - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-08-22
**Phase:** 3-Services and Availability
**Areas discussed:** Service definition, pricing display, availability rules, closures, schedule editor, availability preview

---

## Service Definition

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed duration required | Each service has one set duration | x |
| Flexible duration | Owner chooses a duration per booking | |

**User's choice:** Fixed duration required.
**Notes:** Service price is optional so owners can quote later.

---

## Missing Price Display

| Option | Description | Selected |
|--------|-------------|----------|
| Price on request | Explain that the owner will quote later | x |
| Hide the price | Show no price field | |

**User's choice:** Price on request.

---

## Service Retirement

| Option | Description | Selected |
|--------|-------------|----------|
| Deactivate | Hide new bookings and retain history | x |
| Conditional deletion | Delete only never-booked services | |
| Archive list | Separate retired-service view | |

**User's choice:** Deactivate.

---

## Availability Defaults and Controls

| Option | Description | Selected |
|--------|-------------|----------|
| Defaults plus optional rules | Use defaults unless an owner needs changes | x |
| Setup requires all rules | Ask every owner to choose every rule | |
| Fixed defaults | Do not permit owner controls | |

**User's choice:** Defaults plus optional rules.
**Notes:** Default to 30-minute slots, one-hour lead time, a 30-day horizon, and no buffer.

---

## One-off Schedule Exceptions

| Option | Description | Selected |
|--------|-------------|----------|
| Date-only closures | Block entire dates without a reason | x |
| Per-date special hours | Override the normal schedule on one date | |
| Defer special hours | Record per-date overrides for later | x |

**User's choice:** Date-only closures in v1; special hours deferred.

---

## Schedule Editing

| Option | Description | Selected |
|--------|-------------|----------|
| Day-by-day time rows | Edit start/end times in forms | |
| Drag-and-drop calendar | Visually position weekly time blocks | x |

**User's choice:** Drag-and-drop calendar.
**Notes:** Overlapping blocks are prevented and explained; they are never automatically merged.

---

## Availability Preview

| Option | Description | Selected |
|--------|-------------|----------|
| Available slots only | Minimal schedule view | |
| Include blocked/booked periods | Give owners schedule context without customer data | x |

**User's choice:** Include blocked/booked periods.
**Notes:** Preview is a week calendar with available slots highlighted.

---

## the agent's Discretion

- Accessible drag-and-drop fallback, rule bounds, and exact validation messages.

## Deferred Ideas

- Per-date special opening-hour overrides.
