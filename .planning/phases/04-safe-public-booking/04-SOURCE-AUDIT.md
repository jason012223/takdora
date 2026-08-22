# Phase 4 Source Audit

| Source | ID | Requirement or decision | Planned coverage | Status | Notes |
|---|---|---|---|---|---|
| GOAL | Phase 4 | Customer makes one valid appointment and receives confirmation | 04-01, 04-02, 04-03 | COVERED | Public address and form, atomic booking, then durable confirmation complete the customer outcome. |
| REQ | BOOK-01 | Published business public page without account | 04-01 | COVERED | Publication boundary, canonical `/b/{slug}` resolver, active-service projection, and old-slug redirect contract. |
| REQ | BOOK-02 | Select an actually available service/date/time | 04-01, 04-02 | COVERED | Public adapter consumes the Phase 3 slot engine; transaction reruns it before persistence. |
| REQ | BOOK-03 | Customer contact, optional phone/note, privacy notice | 04-01 | COVERED | One focused accessible form provides direct optional fields and linked notice. |
| REQ | BOOK-04 | At most one appointment per submission | 04-02 | COVERED | Business-scoped opaque idempotency key returns the original durable result on replay. |
| REQ | BOOK-05 | Prevent concurrent active overlap | 04-02 | COVERED | Revalidation plus a PostgreSQL btree_gist/GiST exclusion constraint and real two-transaction test. |
| REQ | BOOK-06 | Clear success or error response | 04-03 | COVERED | Typed outcomes render success, validation, and conflict recovery with no data reset. |
| REQ | NOTF-01 | Email only after saved booking | 04-03 | COVERED | Booking transaction creates outbox; dispatch occurs only after commit. |
| RESEARCH | public tenant safety | Published-only resolver, reduced public projection, no public PII | 04-01 | COVERED | Public boundary exposes only booking-safe business, service, and slot data. |
| RESEARCH | timezone safety | UTC storage, IANA business zone, browser display boundary | 04-01, 04-02, 04-03 | COVERED | Slot/booking identity remains UTC; browser and email output include explicit zone handling. |
| RESEARCH | duplicate and racing submissions | Idempotency, transaction, PostgreSQL invariant | 04-02 | COVERED | Transaction command and database regression protect both retry and race cases. |
| RESEARCH | notification sequencing | durable outbox and post-commit mail | 04-03 | COVERED | Outbox creation shares booking transaction; dispatch is separate and idempotent. |
| CONTEXT | D-01 | One focused booking page | 04-01, 04-03 | COVERED | Compact form and feedback remain on one route. |
| CONTEXT | D-02 | Short privacy notice and policy link | 04-01 | COVERED | Notice appears beside submit with `/privacy` link and no consent step. |
| CONTEXT | D-03 | Direct optional note field | 04-01, 04-03 | COVERED | Note appears on the form and is retained on recoverable errors. |
| CONTEXT | D-04 | Details plus email status after success | 04-03 | COVERED | Success view includes appointment record and truthful sent/delayed state. |
| CONTEXT | D-05 | Preserve details when slot was taken | 04-02, 04-03 | COVERED | Typed conflict preserves inputs and refreshes only slot selection. |
| CONTEXT | D-06 | Concise summary email | 04-03 | COVERED | Rendered from customer-safe booking/business snapshots. |
| CONTEXT | D-07 | Browser-local display; unambiguous storage | 04-01, 04-02, 04-03 | COVERED | Visitor zone is display-only; persisted instants are UTC and business zone is retained. |
| CONTEXT | Deferred | Customer self-service changes | — | EXCLUDED | No public cancellation/reschedule route or confirmation link is planned. |
| CONTEXT | Deferred | Online booking payments | — | EXCLUDED | The public form has no payment collection or provider call. |

All Phase 4 source items are covered. The plans add no package-manager dependency; PostgreSQL, SQLAlchemy/Alembic, Python ZoneInfo, and browser Intl are already present in the approved Reflex foundation.
