# Phase 5: Owner Booking Operations - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-08-22
**Phase:** 5-Owner Booking Operations
**Areas discussed:** Booking views, rescheduling, cancellation, history, status

---

## Default Booking View

| Option | Description | Selected |
|--------|-------------|----------|
| Agenda/list only | Date and status filtering in one list | x |
| Week calendar only | Calendar as the sole view | |
| Both views | Support list and calendar views | x |

**User's choice:** Agenda/list as default, with an optional week-calendar view.

---

## Rescheduling

| Option | Description | Selected |
|--------|-------------|----------|
| Booking details picker | Select a new available time from the booking | x |
| Drag on calendar | Move bookings directly with drag-and-drop | |
| Manual entry | Type a new date/time | |

**User's choice:** Booking details picker with as few use cases as possible.

---

## Cancellation

| Option | Description | Selected |
|--------|-------------|----------|
| Confirmation only | Cancel with a confirmation prompt | |
| Optional customer message | Confirm and optionally write a message | x |
| Required reason | Require a reason before cancellation | |

**User's choice:** Optional customer message.

---

## Booking History

| Option | Description | Selected |
|--------|-------------|----------|
| Details-page timeline | Show a short activity history | |
| Separate tab | Put history on a dedicated tab | |
| Internal records only | Retain it but do not show it in the owner UI | x |

**User's choice:** Internal records only.

---

## Status and Completion

| Option | Description | Selected |
|--------|-------------|----------|
| Scheduled/cancelled/completed | Lean operational lifecycle | |
| Pending/scheduled/cancelled/completed | Includes exceptional manual handling | x |
| Scheduled/cancelled only | Do not track completion | |

**User's choice:** Pending, scheduled, cancelled, completed.
**Notes:** Normal valid customer bookings are scheduled immediately; an owner manually marks a booking completed.

---

## the agent's Discretion

- Calendar behavior, status filter defaults, internal audit storage, and email copy.

## Deferred Ideas

- Customer-facing booking history and self-service changes.
