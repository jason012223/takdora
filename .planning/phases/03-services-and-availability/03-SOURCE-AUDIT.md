# Phase 3 Source Audit

| Source | ID | Requirement or decision | Planned coverage | Status | Notes |
|---|---|---|---|---|---|
| GOAL | Phase 3 | Owner configures offerings and sees legitimate bookable times | 03-01, 03-02, 03-03 | COVERED | Catalog, rules, and a single availability source deliver the outcome. |
| REQ | SERV-01 | Owner creates, edits, activates, and deactivates services | 03-01 | COVERED | Tenant-scoped catalog plus non-destructive deactivation. |
| REQ | AVAIL-01 | Weekly hours, breaks, and date closures | 03-02 | COVERED | Multiple weekly blocks and date-only closures. |
| REQ | AVAIL-02 | Lead time, horizon, interval, and buffer | 03-02, 03-03 | COVERED | Persisted validated rules feed slot calculation. |
| REQ | AVAIL-03 | Times use services, zone, hours, closures, and rules | 03-03 | COVERED | One server-side availability service and preview. |
| RESEARCH | tenant and scheduling safety | Tenant-scoped writes; IANA zone; explicit schedule validation | 03-01, 03-02, 03-03 | COVERED | All repositories take the authorized business; UTC instants are derived only at calculation boundaries. |
| RESEARCH | future booking safety | Reusable availability calculation and occupied-interval contract | 03-03 | COVERED | Phase 4 and 5 consume the same engine rather than duplicate slot logic. |
| CONTEXT | D-01 | Required name and fixed duration; optional description and price | 03-01 | COVERED | Server validation and owner form. |
| CONTEXT | D-02 | Blank price renders as Price on request | 03-01 | COVERED | Shared customer-safe service presentation helper. |
| CONTEXT | D-03 | Deactivate instead of delete | 03-01 | COVERED | Retained rows and active-only selection. |
| CONTEXT | D-04 | Multiple weekly blocks per weekday | 03-02 | COVERED | Calendar persistence and rules reject overlaps. |
| CONTEXT | D-05 | Defaults plus optional rule controls | 03-02, 03-03 | COVERED | Defaults persist at workspace creation and validated advanced controls drive the engine. |
| CONTEXT | D-06 | Visual drag-and-drop calendar; reject overlap | 03-02 | COVERED | Native local drag interaction, keyboard equivalent, and server validation. |
| CONTEXT | D-07 | Date-only closures | 03-02 | COVERED | Closure model has no reason field or displayed reason. |
| CONTEXT | D-08 | Week view shows available and privacy-safe blocked/booked periods | 03-03 | COVERED | Slot projection maps non-PII occupied intervals to neutral states. |
| CONTEXT | Deferred | Per-date special opening-hour overrides | — | EXCLUDED | Deferred after v1; date closures do not change a day's opening hours. |

All phase sources are covered. No package installation is planned; the visual drag interaction uses a local standards-based browser implementation and Reflex/Radix primitives rather than the paid Reflex Enterprise drag-and-drop module.
