---
phase: 03-services-and-availability
plan: 02
subsystem: scheduling-policy
tags: [reflex, sqlmodel, timezone, availability]
requires:
  - phase: 03-services-and-availability
    provides: active services scoped to the owner business
provides:
  - weekly local-time blocks, booking rules, and date closures
  - authoritative hours adapter for publication readiness
affects: [public-booking, owner-booking-operations]
actuals:
  tokens: 12700
  tasks: 3
  commits: 1
tech-stack:
  added: []
  patterns: [validated schedule replacement, IANA-zone local-time policy]
key-files:
  created: [takdora/availability.py, tests/test_schedule_rules.py]
  modified: [takdora/models.py, takdora/tenancy.py]
key-decisions:
  - "Weekly policy stores local weekday and time-of-day rather than UTC appointment timestamps."
  - "Touching schedule blocks are rejected together with overlaps to keep owner policy unambiguous."
requirements-completed: [AVAIL-01, AVAIL-02]
coverage:
  - id: D1
    description: Weekly policy and advanced booking-rule validation.
    requirement: AVAIL-01
    verification:
      - kind: unit
        ref: tests/test_schedule_rules.py
        status: pass
    human_judgment: false
  - id: D2
    description: Date-only closures and bounded schedule policy.
    requirement: AVAIL-02
    verification:
      - kind: unit
        ref: tests/test_availability.py
        status: pass
    human_judgment: false
status: complete
---

# Phase 03 Plan 02: Scheduling Policy Summary

**Weekly local-time policy with conservative overlap validation, date-only closures, and low-friction booking defaults.**

## Accomplishments

- Added business-owned weekly blocks, one booking-rules record, and closures without a reason field.
- Seeded businesses with 30-minute slots, 60-minute lead time, 30-day horizon, and no buffer.
- Added bounded server-side rule validation and a single hours-presence adapter for publishing.

## Task Commits

1. **Tasks 1–3: schedule policy, closures, and rules** — `1478f39`

## Verification

- `uv run pytest tests/test_schedule_rules.py tests/test_availability.py tests/test_business_setup.py -q` — passed
- Ruff format and lint — passed

## Deviations from Plan

None - the pure slot contract was implemented alongside persisted policy to prevent a second scheduling algorithm downstream.

## Self-Check: PASSED
