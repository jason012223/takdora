# Phase 3: Services and Availability - Context

**Gathered:** 2026-08-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Let an owner define bookable services and weekly availability, then inspect the times that would be bookable. This phase establishes service and availability rules; it does not let customers submit bookings or let owners operate existing bookings.

</domain>

<decisions>
## Implementation Decisions

### Service Catalog
- **D-01:** A service has a required name and one required fixed duration; description is supported and price is optional.
- **D-02:** When an owner leaves price blank, customer-facing pages display "Price on request."
- **D-03:** Owners deactivate a service when they stop offering it. Deactivation removes it from new bookings while preserving all historical booking and invoice references.

### Availability Rules and Editing
- **D-04:** Owners define a weekly schedule per day, with multiple available time blocks to represent breaks.
- **D-05:** Default rules are a 30-minute slot interval, one-hour minimum lead time, 30-day booking horizon, and no buffer. Keep these defaults but offer an optional Booking rules section for owners who need to adjust them.
- **D-06:** Use a visual drag-and-drop weekly calendar to edit schedule blocks. Reject overlapping blocks with a clear explanation rather than merging them.
- **D-07:** One-off closures are date-only; do not collect or display a closure reason in v1.

### Availability Preview
- **D-08:** Show an owner-facing week calendar that highlights available slots and also renders blocked/booked periods without customer details.

### the agent's Discretion
- Choose drag-and-drop interaction details, keyboard-accessible alternatives, exact validation copy, the permitted booking-rule ranges, and how schedule blocks are persisted.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project scope
- `.planning/PROJECT.md` - Philippines-first configurable business model and v1 boundaries.
- `.planning/REQUIREMENTS.md` - Phase 3 requirements SERV-01 and AVAIL-01 through AVAIL-03.
- `.planning/ROADMAP.md` - Phase 3 goal and observable success criteria.

### Prior phase decisions
- `.planning/phases/01-deployable-foundation/01-CONTEXT.md` - deployment, test, and operational-quality constraints.
- `.planning/phases/02-owner-workspaces-and-business-setup/02-CONTEXT.md` - owner/workspace boundary and publish prerequisites.
- `.planning/phases/01.1-reflex-ui-foundation-and-design-system/` - inserted Reflex/Radix design-system phase; use its future context before implementation when available.

### Research
- `.planning/research/ARCHITECTURE.md` - tenant-scoped data and scheduling safety guidance.
- `.planning/research/FEATURES.md` - service and availability expectations.
- `.planning/research/PITFALLS.md` - booking-concurrency and time-zone risks.
- `.planning/research/STACK.md` - Reflex supersession note and infrastructure candidates to revalidate during planning.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None yet - the project is greenfield pending the preceding foundation and design-system phases.

### Established Patterns
- One verified owner controls one isolated business workspace in v1.
- A business needs at least one service and working hours before it can publish.

### Integration Points
- Service and availability records must belong to the current business workspace and use its configured time zone.
- The availability calculation will become the single source of truth for public booking in Phase 4 and owner rescheduling in Phase 5.
- The schedule editor must use the Reflex/Radix conventions set by Phase 01.1.

</code_context>

<specifics>
## Specific Ideas

- Favor the fewest owner choices needed for a clear booking setup: sensible defaults first, advanced rules only when needed.
- Preserve booked/blocked visual context without exposing customer details in the availability preview.

</specifics>

<deferred>
## Deferred Ideas

- Per-date special opening-hour overrides - future release after v1.

</deferred>

---

*Phase: 3-Services and Availability*
*Context gathered: 2026-08-22*
