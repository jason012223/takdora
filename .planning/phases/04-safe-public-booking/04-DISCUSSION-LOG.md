# Phase 4: Safe Public Booking - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-08-22
**Phase:** 4-Safe Public Booking
**Areas discussed:** Booking flow, privacy, confirmation, slot conflicts, email, notes, time zones

---

## Booking Flow

| Option | Description | Selected |
|--------|-------------|----------|
| One focused page | Service, time, details, and confirmation in one compact flow | x |
| Step-by-step screens | Separate screens for each stage | |

**User's choice:** One focused page with fewer use cases.

---

## Privacy Notice

| Option | Description | Selected |
|--------|-------------|----------|
| Short notice and policy link | Inform without adding a form interaction | x |
| Required agreement checkbox | Explicit checkbox before submit | |
| Terms step | Separate terms-and-conditions stage | |

**User's choice:** Short notice and policy link.

---

## Successful Booking Confirmation

| Option | Description | Selected |
|--------|-------------|----------|
| Appointment details and email status | Give the customer a useful record immediately | x |
| Simple received message | Minimal acknowledgement only | |

**User's choice:** Appointment details and email status.

---

## Slot Taken During Submit

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve details and reselect | Explain the conflict and keep customer input | x |
| Blank-form generic error | Discard input and provide no specific recovery | |

**User's choice:** Preserve details and reselect.

---

## Confirmation Email

| Option | Description | Selected |
|--------|-------------|----------|
| Concise appointment summary | Business, service, date/time, and contact details | x |
| Detailed branded message | Includes policies, location, and extra instructions | |

**User's choice:** Concise appointment summary.

---

## Optional Customer Note

| Option | Description | Selected |
|--------|-------------|----------|
| Direct field | Show the optional field on the booking form | x |
| Expandable control | Hide it behind an extra interaction | |
| Exclude it | Remove notes from v1 | |

**User's choice:** Direct field.

---

## Customer Time Zone

| Option | Description | Selected |
|--------|-------------|----------|
| Business-zone display | Show the business time zone throughout | |
| Selection-only label | Show time zone only near time selection | |
| Browser-local display | Convert and show times in the visitor's browser time zone | x |

**User's choice:** Browser-local display.

---

## the agent's Discretion

- Validation copy, email presentation, and anti-abuse details.

## Deferred Ideas

- Customer self-service booking changes.
- Online payment at booking time.
