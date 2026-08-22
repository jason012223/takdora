# Phase 6 Source Audit

| Source | ID | Required outcome | Plan | Status |
|---|---|---|---|---|
| GOAL | — | Trustworthy invoice PDF and manual payment tracking | 06-01 through 06-03 | COVERED |
| REQ | INV-01 | Prefilled invoice draft from booking | 06-01 | COVERED |
| REQ | INV-02 | Editable draft fields before issue | 06-01 | COVERED |
| REQ | INV-03 | Exact Decimal totals in business currency | 06-01 | COVERED |
| REQ | INV-04 | Unique business number and immutable snapshots | 06-02 | COVERED |
| REQ | INV-05 | Authorized private PDF download | 06-02 | COVERED |
| REQ | INV-06 | Paid/void payment state | 06-03 | COVERED |
| REQ | INV-07 | Outstanding and paid invoice views | 06-03 | COVERED |
| REQ | INV-08 | Configurable invoice with no BIR-compliance claim | 06-01, 06-02 | COVERED |
| RESEARCH | — | Verified ReportLab binary-stream PDF renderer | 06-02 | COVERED |
| RESEARCH | — | Tenant-scoped invoice/document authorization | 06-01 through 06-03 | COVERED |
| CONTEXT | D-01 | Completed booking prerequisite | 06-01 | COVERED |
| CONTEXT | D-02 | Editable prefilled draft | 06-01 | COVERED |
| CONTEXT | D-03 | Automatic per-business sequential numbering | 06-02 | COVERED |
| CONTEXT | D-04 | Immediate frozen PDF | 06-02 | COVERED |
| CONTEXT | D-05 | Immutable issued invoice and void/redraft correction | 06-02 | COVERED |
| CONTEXT | D-06 | Outstanding, partially paid, paid, void | 06-03 | COVERED |
| CONTEXT | D-07 | One received-total payment input | 06-03 | COVERED |
| CONTEXT | D-08 | Owner-initiated invoice PDF email | 06-03 | COVERED |
| CONTEXT | D-09 | Optional payment-status email | 06-03 | COVERED |
| CONTEXT | D-10 | One professional branded template | 06-02 | COVERED |
| CONTEXT | D-11 | BIR-aware fields without compliance claim | 06-01 through 06-03 | COVERED |

Deferred BIR registration/reporting, online payments, and individual payment records are absent from these plans.
