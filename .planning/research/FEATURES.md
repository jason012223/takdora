# Feature Landscape

**Domain:** Configurable small-business appointment booking and invoicing web application
**Researched:** 2026-08-22
**Confidence:** MEDIUM overall; HIGH for Philippines invoice-content constraints.

## Product Boundary

Takdora v1 is a multi-business service-booking hub, not a full point-of-sale, accounting, or workforce-management system. A customer must be able to discover one business's public page, choose a service and genuinely free time, submit contact details, and receive an email confirmation. The business owner must configure that flow and turn a completed or scheduled service into a downloadable PDF invoice with a manually managed payment state.

## Table Stakes

Features users expect. Omitting any booking-core item makes the product unreliable; omitting any invoice-core item makes it unable to meet Takdora's stated value.

| Feature | Why expected | Complexity | V1 decision | Confidence | Notes |
|---|---|---:|---|---|---|
| Business account and private owner dashboard | Owners need a protected place to administer a public page and customer data. | Med | Build | HIGH | Scope every owner-facing record to the business tenant. |
| Public branded booking page with stable URL | Customers need a no-account route to book a specific business. Comparable products offer public online booking pages. | Med | Build | MEDIUM | Support business name, logo, color accent, contact details, and a slug; use accessible defaults when no logo exists. |
| Configurable service catalog | Different service businesses need name, duration, price, and active/inactive services. | Low | Build | HIGH | Start with one price and one duration per service; no add-ons, packages, or variants. |
| Working hours and bookable slot generation | Availability is the basic promise of a booking tool; mature schedulers configure availability, duration, buffers, booking window, and limits. | High | Build | MEDIUM | Weekly hours, timezone, lead-time, advance-booking horizon, slot interval, and optional buffer are sufficient. |
| Conflict-safe appointment creation | A displayed free slot cannot become two bookings. | High | Build | HIGH | This is a correctness requirement, not merely a feature: re-check availability inside the write transaction. |
| Customer booking form and clear confirmation screen | Collect a minimum usable customer record and acknowledge a successful booking. | Med | Build | HIGH | Name, email, optional phone, service, scheduled time, and notes with consent/privacy copy. |
| Email booking confirmation | User explicitly chose this; competitors make confirmations/reminders part of appointment communication. | Med | Build | HIGH | Send only after successful persistence; log delivery attempt and show the business's contact details for changes. |
| Owner calendar/list and booking detail | Owners must see, search, review, and change bookings without reading raw database data. | Med | Build | HIGH | Provide status filters and day/week or agenda view; a polished agenda view is enough before complex calendars. |
| Owner-controlled cancellation and rescheduling | This is an active Takdora requirement and keeps v1 changes controlled. | Med | Build | HIGH | Preserve original details/audit timestamps and notify the customer by email when a change occurs. |
| Invoice creation linked to booking | Booking-to-invoice is the core combined value proposition. | Med | Build | HIGH | Prefill customer and service data but let owner adjust description, quantity, unit price, issue date, due date, and notes. |
| Downloadable PDF invoice | Explicit Takdora v1 requirement; owners need a shareable record. | Med | Build | HIGH | Render from an immutable invoice snapshot, not live business/service fields. |
| Manual invoice payment state | Explicit decision: payment tracking without payment-gateway scope. | Low | Build | HIGH | Use `draft`, `issued`, `paid`, `void`; record paid date and optional payment reference/method. |
| Configurable invoice identity and currency | Philippines-first businesses need business identity and PHP defaults, while the product must stay configurable. | Med | Build | HIGH | Require business name/address; store currency per business, default PHP; never derive historical invoices from current settings. |

### Invoice compliance guardrail

The PDF generator must be described as a configurable invoice document, **not** as automatically BIR-compliant or a substitute for tax advice. BIR Revenue Regulations No. 7-2024 identify invoice content including seller registered name, VAT/Non-VAT status and TIN/branch code, registered business address, the word “Invoice,” transaction date, serial number, service description, quantity, unit cost, and sale total; buyer address/TIN are not required for B2C end users. Treat these as optional/configurable fields and require a later compliance review before commercial claims. **Confidence: HIGH** (primary BIR regulation).

## Differentiators

These improve the fit for small Philippine service businesses without changing the product into a wide operational suite.

| Feature | Value proposition | Complexity | V1 decision | Confidence | Notes |
|---|---|---:|---|---|---|
| Guided setup checklist | Lets a non-technical owner reach “ready to accept bookings” quickly. | Low | Build | HIGH | Ask for business profile, services, hours, booking rules, invoice details, then surface the public URL. |
| Configurable-but-opinionated defaults | One product works for tutors, salons, freelancers, and repair providers without a vertical-specific fork. | Med | Build | HIGH | Defaults: PHP, Asia/Manila timezone, 30-minute grid; all changeable. |
| Booking-to-invoice handoff | An owner can issue an invoice from a booking without retyping the customer/service. | Med | Build | HIGH | This is Takdora's clearest portfolio differentiator. |
| Payment-status clarity rather than fake payments | Gives owners an honest receivables view while avoiding gateway risk. | Low | Build | HIGH | Dashboard counts/unpaid list; no “Pay now” button in v1. |
| Invoice document preview before issuing | Reduces PDF mistakes before an external document is created. | Low | Consider if time permits | MEDIUM | Useful, but not required for the first end-to-end path. |
| Low-friction public flow | No customer account, only a small form and confirmation. | Low | Build | HIGH | Important for conversion and aligns with the v1 no-self-service decision. |

## Anti-Features

These features are deliberately excluded because they either contradict approved scope, multiply operational/legal complexity, or dilute the evidence-seeking v1.

| Anti-feature | Why avoid it in v1 | What to do instead |
|---|---|---|
| Online payments, deposits, refunds, payment-provider webhooks | Brings money movement, reconciliation, refunds, fraud, PCI/provider dependencies, and support obligations before the booking/invoice flow is validated. | Export/share PDF invoice and let owner record payment manually; retain a future payments domain boundary. |
| Customer self-service cancellation/rescheduling | Explicitly deferred; secure action links, policy enforcement, and calendar recomputation broaden the public attack surface. | Show business contact details in confirmation; owner performs the change and sends an update. |
| Native Android/iOS apps | Duplicates UI, push-notification, distribution, and release work. | Build responsive web pages and test the public booking flow on mobile browsers. |
| Multi-staff, resource, location, and rota scheduling | Staff assignment, capacity and resource collisions change the availability model substantially. | Treat each business as one booking capacity in v1; design schema so a future provider/resource can be added. |
| External calendar sync (Google/Outlook), social booking, SMS | OAuth, sync conflict resolution, provider quotas, messaging consent/costs, and support complexity. | Email confirmations only; expose future integration seams after real use validates demand. |
| Recurring bookings, classes, group capacity, waitlists | Each requires distinct conflict/cancellation/payment rules. | One service, one customer, one time range per appointment. |
| Accounting, tax filing, inventory, payroll, CRM/marketing automation | Takdora would become a business suite and invite regulatory/accounting claims. | Keep invoices as documents plus payment status; store minimal customer booking history only. |
| “BIR-compliant” certification/guarantee | Compliance depends on taxpayer registration, invoice format/numbering, and use conditions outside app configuration. | Provide configurable fields and a compliance disclaimer; obtain qualified Philippine tax/legal review before making claims. |
| Marketplace/discovery across businesses | Requires search ranking, moderation, business verification, and a different acquisition model. | Give each owner a direct public page URL. |

## Feature Dependencies

```text
Business/owner authentication
  -> business profile and public slug
  -> public booking page

Service catalog + availability rules + timezone/booking rules
  -> available-slot calculation
  -> conflict-safe booking creation
  -> confirmation email
  -> owner booking management

Business invoice identity + customer record + service/booking data
  -> invoice draft
  -> immutable issued invoice + PDF
  -> manual payment status and receivables view
```

## MVP Recommendation

Prioritize this thin, demonstrable path:

1. **Owner onboarding and configuration:** create account, business public slug, brand basics, PHP/Asia-Manila defaults, service(s), working hours, and booking limits.
2. **Reliable public booking:** display genuine available slots, create exactly one booking, show confirmation, and send one email.
3. **Owner operations:** agenda/list, booking details, owner cancellation/reschedule with customer update email.
4. **Booking-linked invoicing:** create/edit invoice draft from a booking, issue/download a PDF, mark it manually paid, and show unpaid/paid status.
5. **Deployment-quality baseline:** tenant authorization, privacy copy/minimal collection, error states, responsive public page, and a seeded demo business.

Defer invoice preview, advanced reporting, customer directory notes, deposit rules, staff/location support, reminders, integrations, self-service changes, online payments, and accounting functions. The MVP is credible once an owner can configure a business, a customer can book, and the owner can issue/track an invoice without spreadsheets.

## Sources

- [Square Appointments — online booking and centralized services, availability, appointments, and customer directory](https://squareup.com/us/en/appointments) — MEDIUM; current competitor documentation used to establish common scheduling expectations.
- [Square Appointments — confirmations/reminders and customer booking communication](https://squareup.com/gb/en/appointments/features/reminders) — MEDIUM; current competitor documentation.
- [Square Support — calendar, staff/service availability and booking settings](https://squareup.com/help/us/en/article/5351-manage-your-square-appointments-account-settings) — MEDIUM; current competitor documentation.
- [Calendly — availability, durations, buffers, booking limits and booking window](https://calendly.com/help/how-to-fine-tune-your-availability-settings) — MEDIUM; current scheduling-product documentation.
- [BIR Revenue Regulations No. 7-2024](https://bir-cdn.bir.gov.ph/BIR/pdf/RR%20No.%207-%202024.pdf) — HIGH; primary Philippines invoice-content regulation.
- [BIR invoice format guidance, RMC 77-2024 Annex A](https://orus.bir.gov.ph/files/RMC_No_77_2024_Annex_A1_B6.pdf) — HIGH; primary format guidance.

## Research Gaps

- Confirm the exact BIR treatment of Takdora-generated PDFs, serial-numbering/registration expectations, and e-invoicing requirements with a Philippine tax professional before a business relies on it for statutory invoices.
- Conduct user interviews with at least 3–5 Philippine service owners to validate whether reminders, staff scheduling, deposits, or online payment is the next valuable capability.
- Phase-specific research is required before enabling payment providers, customer action links, SMS, or third-party calendar synchronization.
