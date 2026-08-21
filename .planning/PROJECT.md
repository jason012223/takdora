# Takdora

## What This Is

Takdora is a web-based booking and invoicing hub for configurable service businesses in the Philippines, such as salons, tutors, freelancers, and repair providers. Each business receives a public booking page for customers and a private dashboard to manage services, schedules, bookings, and invoices.

## Core Value

Make it effortless for a service business to accept a customer booking and track the resulting invoice in one dependable place.

## Business Context

- **Customer**: Owners of small, appointment-based service businesses and their customers.
- **Revenue model**: Portfolio project initially; a subscription model may be evaluated after real-world validation.
- **Success metric**: A business can configure its page, receive a booking, email confirmation, and issue a PDF invoice without using a spreadsheet.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Businesses can configure their public presence, services, availability, booking rules, and invoice details.
- [ ] Customers can make an available appointment from a business's public page and receive an email confirmation.
- [ ] Business owners can manage bookings, including customer-requested cancellations and reschedules.
- [ ] Business owners can generate downloadable PDF invoices and manually record payment status.

### Out of Scope

- Customer self-service cancellation and rescheduling — business owners will manage changes in v1.
- Online customer payments — deliberately deferred until the core booking and invoice workflow is validated.
- Native mobile applications — responsive web application first.

## Context

Takdora is a new, deployable portfolio project with a Philippines-first audience. The name is inspired by *takda* (an appointment or scheduled time) and *oras* (time). The product should be configurable rather than tied to one business type: a business needs to control services, working hours, booking rules, logo/colors, invoice details, and currency.

The v1 workflow is deliberately practical: a customer visits a business's public page, selects a service and free slot, submits the booking, and receives email confirmation. The business owner uses a private dashboard to manage the booking and generate a PDF invoice, then manually marks that invoice paid when appropriate.

## Constraints

- **Market**: Philippines-first — defaults should suit local small service businesses while remaining adaptable.
- **Product scope**: Configurable multi-business platform — avoid hard-coding assumptions for salons, tutors, or any single sector.
- **Payments**: Manual payment-status workflow only in v1 — avoid payment-provider complexity before validating core operations.
- **Deployment**: Publicly deployable web application — the finished project must be usable by real people, not only a local demo.
- **Security**: Public booking and private business data require authorization, tenant isolation, and safe handling of customer data.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Product name: Takdora | Filipino-inspired name connecting scheduled appointments and time. | — Pending |
| Public booking page plus private owner dashboard | Supports customers without requiring an account while protecting business operations. | — Pending |
| Configurable business setup | Enables salons, tutors, freelancers, repair providers, and other service businesses. | — Pending |
| PDF invoices with manual paid status in v1 | Delivers invoicing value without payment-gateway complexity. | — Pending |
| Customer changes handled by business owners in v1 | Keeps booking changes controlled and initial scope manageable. | — Pending |
| Customer booking confirmations are emailed | Gives customers a clear record after booking. | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-08-22 after initialization*
