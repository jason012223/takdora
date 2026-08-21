# Phase 5: Owner Booking Operations - Context

**Gathered:** 2026-08-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Let a business owner inspect, cancel, reschedule, and complete their own bookings without compromising availability. This phase does not expose booking histories to customers or introduce customer self-service changes.

</domain>

<decisions>
## Implementation Decisions

### Booking Views
- **D-01:** Use an agenda/list with date and status filters as the default owner view. Offer a week-calendar view as an optional alternative.
- **D-02:** Owners can open a booking to inspect its full details before taking an action.

### Changes and Communication
- **D-03:** Rescheduling starts from booking details and uses an available-time picker; do not require drag-and-drop or manual time entry.
- **D-04:** Cancellation requires confirmation and offers an optional message for the customer.
- **D-05:** Keep cancellation and reschedule history as internal records, not an owner-facing activity timeline.

### Booking Status
- **D-06:** Support pending, scheduled, cancelled, and completed statuses with clear labels.
- **D-07:** A valid customer-submitted booking becomes scheduled immediately. Pending is reserved for exceptional manual handling rather than the normal customer flow.
- **D-08:** An owner manually marks a scheduled booking completed; do not auto-complete it when its end time passes.

### the agent's Discretion
- Choose calendar interaction details, exact filter defaults, internal audit-record representation, cancellation/reschedule email copy, and exceptional pending-state behavior.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project scope
- `.planning/PROJECT.md` - owner-managed changes and v1 scope boundaries.
- `.planning/REQUIREMENTS.md` - Phase 5 requirements OPS-01 through OPS-04.
- `.planning/ROADMAP.md` - Phase 5 goal and observable success criteria.

### Prior phase decisions
- `.planning/phases/02-owner-workspaces-and-business-setup/02-CONTEXT.md` - one-owner/one-workspace access and tenant boundary.
- `.planning/phases/03-services-and-availability/03-CONTEXT.md` - authoritative availability and blocked/booked preview rules.
- `.planning/phases/04-safe-public-booking/04-CONTEXT.md` - immediate scheduling, customer details, and confirmation behavior.
- `.planning/phases/01.1-reflex-ui-foundation-and-design-system/` - inserted Reflex/Radix design-system phase; use its future context before implementation when available.

### Research
- `.planning/research/ARCHITECTURE.md` - tenant isolation and atomic schedule-change guidance.
- `.planning/research/PITFALLS.md` - booking-concurrency and notification risks.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None yet - the project is greenfield pending the preceding implementation phases.

### Established Patterns
- All business-private records are restricted to the single owner workspace in v1.
- Public booking is immediately scheduled and customers do not self-manage changes in v1.

### Integration Points
- List/calendar views must draw only tenant-scoped bookings.
- Rescheduling must call the same authoritative availability calculation and concurrency protections as Phase 4 booking.
- Cancellation/reschedule messages should use the established email-delivery path after the action commits.
- Completed bookings become a natural starting point for Phase 6 invoice operations.

</code_context>

<specifics>
## Specific Ideas

- Prefer explicit details-page actions over gesture-heavy scheduling changes.
- Keep routine owner operations simple while retaining internal records for support and correctness.

</specifics>

<deferred>
## Deferred Ideas

- Customer-visible booking-change history.
- Customer self-service cancellation and rescheduling.

</deferred>

---

*Phase: 5-Owner Booking Operations*
*Context gathered: 2026-08-22*
