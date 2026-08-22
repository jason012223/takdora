# Roadmap: Takdora

## Overview

Takdora will grow from a deployable Reflex foundation into a configurable, tenant-safe booking-to-invoice workflow. Owners will set up their businesses and availability, customers will book real slots from a public page, and owners will manage changes and issue private PDF invoices. A dedicated Reflex/Radix design-system phase establishes the shared UI before the owner and customer flows are built.

## Phases

**Phase Numbering:**

- Integer phases are planned MVP work; decimal phases are reserved for urgent insertions.

- [ ] **Phase 1: Deployable Foundation** - Establish the secure, testable production base for the application.
- [ ] **Phase 2: Owner Workspaces and Business Setup** - Let owners securely create isolated, configurable business workspaces.
- [ ] **Phase 3: Services and Availability** - Let owners define services and produce valid bookable times.
- [ ] **Phase 4: Safe Public Booking** - Let customers book an available time once and receive confirmation.
- [ ] **Phase 5: Owner Booking Operations** - Let owners see, cancel, and safely reschedule their appointments.
- [ ] **Phase 6: Invoice Lifecycle and Manual Payments** - Turn bookings into immutable downloadable invoices with manual payment tracking.
- [ ] **Phase 7: Reliability and Launch Hardening** - Make delivery, storage, security, and recovery operationally dependable.
- [ ] **Phase 8: Portfolio Validation and Responsive Release** - Validate the complete public product experience across devices.

## Phase Details

### Phase 1: Deployable Foundation

**Goal**: An operator can run, test, and deploy a secure Takdora application foundation.
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: FOUND-02, FOUND-03
**Success Criteria** (what must be TRUE):

  1. An operator can configure Takdora with environment-based secrets and connect it to PostgreSQL without exposing development settings in production.
  2. An operator can build and deploy the application with its migrations and static assets using the documented runtime configuration.
  3. An operator can run automated linting and tests before deployment and receive a clear pass/fail result.

**Plans**: 3/3 plans executed

Plans:

- [x] 01-01-PLAN.md — Build the Reflex/PostgreSQL foundation and Docker Compose development workflow.
- [x] 01-02-PLAN.md — Add lint, tests, coverage, dependency audit, and Playwright CI gates.
- [x] 01-03-PLAN.md — Package the Render deployment, health monitoring, Sentry, and operator runbook.

### Phase 01.1: Reflex UI Foundation and Design System (INSERTED)

**Goal:** Public, owner, and marketing surfaces share an accessible, responsive, non-generic Takdora UI foundation built with Reflex and Radix components.
**Requirements**: UI-01
**Depends on:** Phase 1
**Plans:** 3/3 plans executed

Plans:

- [x] 01.1-01-PLAN.md — Establish the Takdora theme, global styling, and rendered foundation shell.
- [x] 01.1-02-PLAN.md — Deliver reusable form, feedback, status, card, and table primitives with a component gallery.
- [x] 01.1-03-PLAN.md — Add responsive public/owner layouts, dialog/calendar primitives, and browser coverage.

### Phase 2: Owner Workspaces and Business Setup

**Goal**: A business owner can securely create an isolated workspace and configure the business information needed to publish it.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: AUTH-01, AUTH-02, AUTH-03, TEN-01, TEN-02, BIZ-01, BIZ-02, BIZ-03, BIZ-04
**Success Criteria** (what must be TRUE):

  1. A business owner can register, log in, stay signed in after refreshing, log out, and reset a forgotten password through email.
  2. A business owner can create and enter their own business workspace, while another owner cannot view, alter, download, or discover its private records.
  3. A business owner can configure the business name, contact details, address, public slug, logo, accent color, time zone, and currency, with Asia/Manila and PHP preselected.
  4. A business owner can provide the invoice identity fields and see a checklist of the essentials still needed before the public page can be published.

**Plans**: 3/3 plans executed
**UI hint**: yes

Plans:

- [x] 02-01-PLAN.md — Secure owner accounts, persistent sessions, verification, and password resets.
- [x] 02-02-PLAN.md — One-owner workspaces, tenant isolation, and deliberate scheduled deletion.
- [x] 02-03-PLAN.md — Resumable business setup, publish readiness, and durable public-address redirects.

### Phase 3: Services and Availability

**Goal**: A business owner can configure what they offer and see the times customers can legitimately book.
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: SERV-01, AVAIL-01, AVAIL-02, AVAIL-03
**Success Criteria** (what must be TRUE):

  1. A business owner can create, edit, activate, and deactivate services with a name, duration, price, and description.
  2. A business owner can define weekly working hours, breaks, and one-off closures.
  3. A business owner can set lead time, booking horizon, slot interval, and a buffer between bookings.
  4. The availability view shows only times calculated from the active service, configured time zone, hours, closures, and booking rules.

**Plans**: 3 plans
**UI hint**: yes

Plans:

- [ ] 03-01-PLAN.md — Build the tenant-safe service catalog and publishing-readiness service contract.
- [ ] 03-02-PLAN.md — Persist weekly hours, closures, booking rules, and the accessible visual schedule editor.
- [ ] 03-03-PLAN.md — Calculate authoritative availability and render the privacy-safe owner week preview.

### Phase 4: Safe Public Booking

**Goal**: A customer can use a published business page to make one valid appointment and receive confirmation.
**Mode:** mvp
**Depends on**: Phase 3
**Requirements**: BOOK-01, BOOK-02, BOOK-03, BOOK-04, BOOK-05, BOOK-06, NOTF-01
**Success Criteria** (what must be TRUE):

  1. A customer can open a published business URL without an account and view its active services and booking information.
  2. A customer can select a service and a genuinely available date and time, then submit their name, email, optional phone number, notes, and a privacy-aware booking request.
  3. A booking submission creates at most one appointment even when the customer retries, and simultaneous attempts cannot reserve overlapping active times.
  4. A customer receives an unambiguous success or error response, and an email confirmation is sent only after a successful booking is saved.

**Plans**: 3/3 plans executed
**UI hint**: yes

Plans:

- [x] 04-01-PLAN.md — Publish and resolve safe public business pages with a compact browser-local booking form.
- [x] 04-02-PLAN.md — Make booking submission idempotent and enforce PostgreSQL non-overlap.
- [x] 04-03-PLAN.md — Deliver post-commit confirmation email and customer conflict recovery.

### Phase 5: Owner Booking Operations

**Goal**: A business owner can oversee appointment activity and make customer-requested changes without compromising the schedule.
**Mode:** mvp
**Depends on**: Phase 4
**Requirements**: OPS-01, OPS-02, OPS-03, OPS-04
**Success Criteria** (what must be TRUE):

  1. A business owner can view only their bookings in an agenda or list and filter them by date and status.
  2. A business owner can open a booking to see its customer, service, scheduled time, notes, and current status.
  3. A business owner can cancel a booking, preserving the action in its history and emailing the customer an update.
  4. A business owner can reschedule only to a genuinely available time, with the change retained in history and emailed to the customer.

**Plans**: TBD
**UI hint**: yes

### Phase 6: Invoice Lifecycle and Manual Payments

**Goal**: A business owner can turn a booking into a trustworthy invoice PDF and track its manual payment state.
**Mode:** mvp
**Depends on**: Phase 5
**Requirements**: INV-01, INV-02, INV-03, INV-04, INV-05, INV-06, INV-07, INV-08
**Success Criteria** (what must be TRUE):

  1. A business owner can start an invoice draft from a booking with customer and service details already filled in, then edit its line items, dates, notes, and displayed identity fields before issuing.
  2. Invoice totals use exact decimal arithmetic in the configured business currency.
  3. When issued, an invoice receives a unique number for that business and preserves the relevant business, customer, and line-item details as immutable snapshots.
  4. A business owner can download an issued invoice as an authorized private PDF, mark it paid or void, and distinguish outstanding from paid invoices; generated documents clearly avoid an automatic BIR-compliance claim.

**Plans**: 3 plans

Plans:

- [ ] 06-01-PLAN.md — Create completed-booking invoice drafts with exact editable totals.
- [ ] 06-02-PLAN.md — Issue immutable numbered, branded private PDFs and correction flow.
- [ ] 06-03-PLAN.md — Track received-total payments and intentional invoice email delivery.
**UI hint**: yes

### Phase 7: Reliability and Launch Hardening

**Goal**: An operator and owner can detect recoverable delivery failures while the public service protects stored data and is ready for launch.
**Mode:** mvp
**Depends on**: Phase 6
**Requirements**: REL-01, REL-02, REL-03, REL-04
**Success Criteria** (what must be TRUE):

  1. An owner or operator can see email and PDF generation/delivery failures and safely retry failed work without creating duplicates.
  2. Business logos and issued PDFs persist outside ephemeral application storage, and only authorized owners can download a private PDF.
  3. Automated regression checks demonstrate that one business cannot access another's data and simultaneous booking attempts do not create an overlap.
  4. Before launch, an operator can verify migrations, static assets, health checks, backups, and production configuration through a repeatable release check.

**Plans**: 3 plans

Plans:

- [ ] 07-01-PLAN.md â€” Make delivery failures tenant-safe, visible, monitored, and retryable.
- [ ] 07-02-PLAN.md â€” Persist private PDFs and logos in durable object storage with owner authorization.
- [ ] 07-03-PLAN.md â€” Add maintenance, Windows-safe browser smoke, staging release gates, and recovery evidence.

### Phase 8: Portfolio Validation and Responsive Release

**Goal**: Visitors can use a polished Takdora experience across desktop and mobile browsers and evaluate its end-to-end value.
**Mode:** mvp
**Depends on**: Phase 7
**Requirements**: FOUND-01
**Success Criteria** (what must be TRUE):

  1. A visitor can complete the public booking experience and an owner can use the private dashboard on current desktop and mobile browsers without layout or navigation failures.
  2. A portfolio reviewer can access a clear deployed demonstration of the booking-to-invoice workflow and understand the supported v1 boundaries.
  3. A service-business owner can follow the setup and booking flow using understandable copy, empty states, and error feedback.

**Plans**: TBD
**UI hint**: yes

## Progress

**Execution Order:** Phases execute in numeric order: 1 -> 01.1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Deployable Foundation | 3/3 | In Progress|  |
| 2. Owner Workspaces and Business Setup | 3/3 | In Progress|  |
| 3. Services and Availability | 0/TBD | Not started | - |
| 4. Safe Public Booking | 3/3 | In Progress|  |
| 5. Owner Booking Operations | 0/TBD | Not started | - |
| 6. Invoice Lifecycle and Manual Payments | 0/TBD | Not started | - |
| 7. Reliability and Launch Hardening | 0/TBD | Not started | - |
| 8. Portfolio Validation and Responsive Release | 0/TBD | Not started | - |
