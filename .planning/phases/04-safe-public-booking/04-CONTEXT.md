# Phase 4: Safe Public Booking - Context

**Gathered:** 2026-08-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Let a customer submit one valid booking from a published business page and receive a clear confirmation. This phase owns the public booking interaction, duplicate/concurrency safety, and confirmation email; it does not give customers self-service cancellation/rescheduling or introduce online payments.

</domain>

<decisions>
## Implementation Decisions

### Compact Booking Flow
- **D-01:** Use one focused booking page: select service, select date/time, enter customer details, and confirm. Avoid a multi-screen wizard.
- **D-02:** Display a short privacy notice beside submission with a link to the privacy policy; do not add a required checkbox or a separate terms step.
- **D-03:** Show the optional customer note field directly on the form.

### Confirmation and Failure Feedback
- **D-04:** After a successful booking, show the appointment details and clearly state that a confirmation email was sent.
- **D-05:** If a slot becomes unavailable during submission, preserve customer-entered details, explain that the slot was just taken, and let the customer select another time.
- **D-06:** Send a concise confirmation email with the business, service, date/time, and business contact details; do not make policies/location/extra instructions part of the default email.

### Time Display
- **D-07:** Display selectable times and confirmation details in the visitor's browser time zone. Store and validate the booking as one unambiguous instant, retaining the business time zone for owner operations and availability calculations. â€” **Reversibility:** costly - changing public time-zone behavior can confuse customers and affect communication expectations.

### the agent's Discretion
- Choose exact inline validation, accessibility behavior, anti-abuse protections, availability refresh mechanics, and email layout/copy within the decisions above.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project scope
- `.planning/PROJECT.md` - public booking, privacy, security, and v1 scope boundaries.
- `.planning/REQUIREMENTS.md` - Phase 4 requirements BOOK-01 through BOOK-06 and NOTF-01.
- `.planning/ROADMAP.md` - Phase 4 goal and observable success criteria.

### Prior phase decisions
- `.planning/phases/01-deployable-foundation/01-CONTEXT.md` - deployment and quality gates.
- `.planning/phases/02-owner-workspaces-and-business-setup/02-CONTEXT.md` - publication prerequisites, public URL contract, and business defaults.
- `.planning/phases/03-services-and-availability/03-CONTEXT.md` - service lifecycle and the availability calculation that public booking must use.
- `.planning/phases/01.1-reflex-ui-foundation-and-design-system/` - inserted Reflex/Radix design-system phase; use its future context before implementation when available.

### Research
- `.planning/research/ARCHITECTURE.md` - transaction-safe booking, tenant scoping, and notification sequencing.
- `.planning/research/PITFALLS.md` - time-zone, duplicate-submission, and concurrent-booking failure modes.
- `.planning/research/FEATURES.md` - public booking experience guidance.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None yet - the project is greenfield pending preceding implementation phases.

### Established Patterns
- Customers do not need accounts in v1.
- Public pages use the business's published path-based URL.
- Services, working hours, closures, rules, and the business time zone define legitimate booking slots.

### Integration Points
- Public booking must call the same authoritative availability calculation used by owner preview and later owner rescheduling.
- Booking persistence must enforce tenant isolation and concurrency safety, then trigger email only after a successful committed booking.
- Browser-local display must be converted reliably to the stored booking instant and business-local owner view.

</code_context>

<specifics>
## Specific Ideas

- Keep customer effort minimal while still explaining privacy and giving useful success/failure feedback.
- Never make customers re-enter their details because another customer claimed the slot first.

</specifics>

<deferred>
## Deferred Ideas

- Customer self-service cancellation and rescheduling links - v2.
- Online payment during booking - future release after manual invoice workflow validation.

</deferred>

---

*Phase: 4-Safe Public Booking*
*Context gathered: 2026-08-22*
