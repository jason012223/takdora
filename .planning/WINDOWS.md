---
schema_version: 1
open_count: 2
waived_count: 0
fixed_count: 0
total_count: 2
last_updated: 2026-08-22T06:37:59.674Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 01.1 | unrun-verify | tests/e2e/test_design_system_smoke.py |  | Compose-backed Playwright verification was unrun because Reflex did not expose local HTTP ports after compilation. | open |  | 2026-08-22T06:37:58.464Z |  |
| 2 | 01.1 | unrun-verify | tests/e2e/test_responsive_ui_smoke.py |  | Compose-backed Playwright verification was unrun because Reflex did not expose local HTTP ports after compilation. | open |  | 2026-08-22T06:37:59.674Z |  |

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
  }
]
````
