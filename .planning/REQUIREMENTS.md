# Requirements: Takdora

**Defined:** 2026-08-22
**Core Value:** Make it effortless for a service business to accept a customer booking and track the resulting invoice in one dependable place.

## v1 Requirements

### Foundation

- [ ] **FOUND-01**: A visitor can use Takdora as a responsive web application on desktop and mobile browsers.
- [ ] **FOUND-02**: An operator can deploy Takdora with PostgreSQL, environment-based secrets, and production-safe Django settings.
- [ ] **FOUND-03**: An operator can run automated linting and tests before deployment.
- [x] **UI-01**: Takdora provides a reusable, accessible Reflex/Radix UI foundation for responsive public, owner, and marketing surfaces.

### Accounts and Tenancy

- [x] **AUTH-01**: A business owner can create an account with an email address and password.
- [x] **AUTH-02**: A business owner can log in, log out, and remain authenticated across browser refreshes.
- [x] **AUTH-03**: A business owner can reset a forgotten password through an email link.
- [x] **TEN-01**: A business owner can create and access their own business workspace.
- [x] **TEN-02**: A business owner cannot view, modify, download, or enumerate another business's private data.

### Business Setup

- [x] **BIZ-01**: A business owner can set the business name, contact details, address, public URL slug, logo, and accent color.
- [x] **BIZ-02**: A business owner can set the business time zone and currency, with `Asia/Manila` and PHP as defaults.
- [x] **BIZ-03**: A business owner can configure the invoice identity fields displayed on newly issued invoices.
- [x] **BIZ-04**: A business owner can see a setup checklist showing which essentials are required before publishing their booking page.

### Services and Availability

- [ ] **SERV-01**: A business owner can create, edit, activate, and deactivate services with a name, duration, price, and description.
- [ ] **AVAIL-01**: A business owner can set weekly working hours, breaks, and date-specific closures.
- [ ] **AVAIL-02**: A business owner can set booking lead time, advance-booking horizon, slot interval, and between-booking buffer.
- [ ] **AVAIL-03**: Takdora calculates bookable times from the business's services, time zone, working hours, closures, and booking rules.

### Public Booking

- [x] **BOOK-01**: A customer can visit a published business's public URL and view its active services and booking information without creating an account.
- [x] **BOOK-02**: A customer can choose a service and an actually available date/time from the public booking flow.
- [x] **BOOK-03**: A customer can submit their name, email, optional phone number, and booking notes with appropriate privacy notice.
- [x] **BOOK-04**: Takdora creates at most one appointment for a submission, including when a customer retries the request.
- [x] **BOOK-05**: Takdora prevents overlapping active bookings for the business's v1 booking capacity, including simultaneous attempts.
- [x] **BOOK-06**: A customer sees a clear success or error result after trying to book.
- [x] **NOTF-01**: A customer receives an email confirmation only after their booking is successfully saved.

### Owner Booking Operations

- [ ] **OPS-01**: A business owner can view their bookings in an agenda or list with date and status filters.
- [ ] **OPS-02**: A business owner can view a booking's customer, service, scheduled time, notes, and status.
- [ ] **OPS-03**: A business owner can cancel a booking; Takdora preserves a record of that action and emails the customer an update.
- [ ] **OPS-04**: A business owner can reschedule a booking only to a genuinely available time; Takdora preserves a history and emails the customer an update.

### Invoicing

- [ ] **INV-01**: A business owner can create an invoice draft prefilled from a booking's customer and service details.
- [ ] **INV-02**: A business owner can edit an invoice draft's line items, issue date, due date, notes, and displayed invoice fields before issuing it.
- [ ] **INV-03**: Takdora calculates invoice totals using exact decimal money arithmetic and the business's configured currency.
- [ ] **INV-04**: A business owner can issue an invoice with a unique business-specific number and immutable snapshots of relevant business, customer, and line-item data.
- [ ] **INV-05**: A business owner can download an issued invoice as a PDF from the private dashboard.
- [ ] **INV-06**: A business owner can mark an issued invoice as paid or void and see its current payment status.
- [ ] **INV-07**: A business owner can view outstanding and paid invoices for their business.
- [ ] **INV-08**: Takdora labels generated documents as configurable invoices and does not claim automatic BIR compliance.

### Reliability and Launch Readiness

- [ ] **REL-01**: Takdora records email/PDF delivery or generation failures so an owner or operator can detect and retry them safely.
- [ ] **REL-02**: Takdora stores logos and issued PDFs outside ephemeral application storage and authorizes private PDF downloads.
- [ ] **REL-03**: Takdora has automated regression tests for cross-business access control and simultaneous booking attempts.
- [ ] **REL-04**: An operator can verify migrations, static assets, health checks, backups, and production configuration before public launch.

## v2 Requirements

### Payments

- **PAY-01**: A customer can pay an invoice online through an approved payment provider.
- **PAY-02**: Takdora records payment-provider events, refunds, and reconciliation status safely.

### Customer Self-Service

- **CUST-01**: A customer can securely cancel or reschedule an appointment from a confirmation link.
- **CUST-02**: A customer can receive configurable booking reminders.

### Scheduling Expansion

- **SCHED-01**: A business owner can schedule named staff, rooms, or other booking resources.
- **SCHED-02**: A business owner can offer recurring, group, or capacity-based bookings.

### Integrations

- **INTG-01**: A business owner can synchronize availability with external calendars.
- **INTG-02**: A business owner can send SMS notifications or integrate with accounting software.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Online payments, deposits, refunds, and payment webhooks | Money movement and reconciliation are deliberately deferred until the core workflow is validated. |
| Customer self-service cancellation and rescheduling | v1 keeps schedule changes under business-owner control. |
| Native mobile applications | A responsive web application reaches customers first without duplicate platform work. |
| Multi-staff, rooms, locations, groups, or recurring bookings | They materially change capacity and conflict rules; v1 has one business booking capacity. |
| Marketplace/discovery across businesses | Takdora provides direct public business pages, not a consumer marketplace. |
| Accounting, tax filing, payroll, CRM, or inventory features | These dilute the focused booking-to-invoice value proposition. |
| Claims that generated PDFs are BIR-compliant | Compliance depends on facts and review outside the v1 application. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | Phase 8 | Pending |
| FOUND-02 | Phase 1 | Pending |
| FOUND-03 | Phase 1 | Pending |
| UI-01 | Phase 01.1 | Complete |
| AUTH-01 | Phase 2 | Complete |
| AUTH-02 | Phase 2 | Complete |
| AUTH-03 | Phase 2 | Complete |
| TEN-01 | Phase 2 | Complete |
| TEN-02 | Phase 2 | Complete |
| BIZ-01 | Phase 2 | Complete |
| BIZ-02 | Phase 2 | Complete |
| BIZ-03 | Phase 2 | Complete |
| BIZ-04 | Phase 2 | Complete |
| SERV-01 | Phase 3 | Pending |
| AVAIL-01 | Phase 3 | Pending |
| AVAIL-02 | Phase 3 | Pending |
| AVAIL-03 | Phase 3 | Pending |
| BOOK-01 | Phase 4 | Complete |
| BOOK-02 | Phase 4 | Complete |
| BOOK-03 | Phase 4 | Complete |
| BOOK-04 | Phase 4 | Complete |
| BOOK-05 | Phase 4 | Complete |
| BOOK-06 | Phase 4 | Complete |
| NOTF-01 | Phase 4 | Complete |
| OPS-01 | Phase 5 | Pending |
| OPS-02 | Phase 5 | Pending |
| OPS-03 | Phase 5 | Pending |
| OPS-04 | Phase 5 | Pending |
| INV-01 | Phase 6 | Pending |
| INV-02 | Phase 6 | Pending |
| INV-03 | Phase 6 | Pending |
| INV-04 | Phase 6 | Pending |
| INV-05 | Phase 6 | Pending |
| INV-06 | Phase 6 | Pending |
| INV-07 | Phase 6 | Pending |
| INV-08 | Phase 6 | Pending |
| REL-01 | Phase 7 | Pending |
| REL-02 | Phase 7 | Pending |
| REL-03 | Phase 7 | Pending |
| REL-04 | Phase 7 | Pending |

**Coverage:**

- v1 requirements: 40 total
- Mapped to phases: 40
- Unmapped: 0

---
*Requirements defined: 2026-08-22*
*Last updated: 2026-08-22 after roadmap creation*
