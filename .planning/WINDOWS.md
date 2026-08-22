---
schema_version: 1
open_count: 6
waived_count: 0
fixed_count: 0
total_count: 6
last_updated: 2026-08-22T07:24:03.606Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 01.1 | unrun-verify | tests/e2e/test_design_system_smoke.py |  | Compose-backed Playwright verification was unrun because Reflex did not expose local HTTP ports after compilation. | open |  | 2026-08-22T06:37:58.464Z |  |
| 2 | 01.1 | unrun-verify | tests/e2e/test_responsive_ui_smoke.py |  | Compose-backed Playwright verification was unrun because Reflex did not expose local HTTP ports after compilation. | open |  | 2026-08-22T06:37:59.674Z |  |
| 3 | 02 | stub | takdora/business_setup.py |  | Public redirect resolution and service/hours records are intentionally owned by later phases. | open |  | 2026-08-22T06:56:44.675Z |  |
| 4 | 03 | unrun-verify | takdora/pages/availability.py |  | Owner availability drag-and-drop and preview browser verification was unrun because no Compose app port is available. | open |  | 2026-08-22T07:08:23.998Z |  |
| 5 | 04 | unrun-verify | tests/e2e/test_public_booking_smoke.py |  | Real browser smoke was not run because this Windows host cannot reach Compose browser ports. | open |  | 2026-08-22T07:24:02.360Z |  |
| 6 | 04 | unrun-verify | tests/test_booking_postgres.py |  | Real PostgreSQL concurrency test was not run through the inaccessible Compose host port. | open |  | 2026-08-22T07:24:03.606Z |  |

````json
[
  {
    "id": 1,
    "kind": "unrun-verify",
    "phase": "01.1",
    "file": "tests/e2e/test_design_system_smoke.py",
    "line": null,
    "description": "Compose-backed Playwright verification was unrun because Reflex did not expose local HTTP ports after compilation.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-08-22T06:37:58.464Z",
    "resolved_at": null
  },
  {
    "id": 2,
    "kind": "unrun-verify",
    "phase": "01.1",
    "file": "tests/e2e/test_responsive_ui_smoke.py",
    "line": null,
    "description": "Compose-backed Playwright verification was unrun because Reflex did not expose local HTTP ports after compilation.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-08-22T06:37:59.674Z",
    "resolved_at": null
  },
  {
    "id": 3,
    "kind": "stub",
    "phase": "02",
    "file": "takdora/business_setup.py",
    "line": null,
    "description": "Public redirect resolution and service/hours records are intentionally owned by later phases.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-08-22T06:56:44.675Z",
    "resolved_at": null
  },
  {
    "id": 4,
    "kind": "unrun-verify",
    "phase": "03",
    "file": "takdora/pages/availability.py",
    "line": null,
    "description": "Owner availability drag-and-drop and preview browser verification was unrun because no Compose app port is available.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-08-22T07:08:23.998Z",
    "resolved_at": null
  },
  {
    "id": 5,
    "kind": "unrun-verify",
    "phase": "04",
    "file": "tests/e2e/test_public_booking_smoke.py",
    "line": null,
    "description": "Real browser smoke was not run because this Windows host cannot reach Compose browser ports.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-08-22T07:24:02.360Z",
    "resolved_at": null
  },
  {
    "id": 6,
    "kind": "unrun-verify",
    "phase": "04",
    "file": "tests/test_booking_postgres.py",
    "line": null,
    "description": "Real PostgreSQL concurrency test was not run through the inaccessible Compose host port.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-08-22T07:24:03.606Z",
    "resolved_at": null
  }
]
````
