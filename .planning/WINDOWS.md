---
schema_version: 1
open_count: 0
waived_count: 0
fixed_count: 2
total_count: 2
last_updated: 2026-08-04T06:05:13.884Z
---

# Broken Windows Ledger

> Cross-phase defect register. `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 44 | unmet-truth | .planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-04.md |  | SC#4 recorded NOT-MET in 44-GATE-EVIDENCE-04.md: 44-GATE-EVIDENCE-03.md (plan 44-03, concurrent sibling) not visible from this worktree at HEAD | fixed |  | 2026-08-04T06:00:30.277Z | 2026-08-04T06:05:13.809Z |
| 2 | 44 | deviation | .planning/REQUIREMENTS.md |  | BLD-01 not flipped to Complete in REQUIREMENTS.md (still Pending) despite being implemented + evidenced in 44-GATE-EVIDENCE-02.md; no plan 44-02 final metadata commit marks it, unlike CONF-08's bea3549 | fixed |  | 2026-08-04T06:00:35.186Z | 2026-08-04T06:05:13.884Z |

````json
[
  {
    "id": 1,
    "kind": "unmet-truth",
    "phase": "44",
    "file": ".planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-04.md",
    "line": null,
    "description": "SC#4 recorded NOT-MET in 44-GATE-EVIDENCE-04.md: 44-GATE-EVIDENCE-03.md (plan 44-03, concurrent sibling) not visible from this worktree at HEAD",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-08-04T06:00:30.277Z",
    "resolved_at": "2026-08-04T06:05:13.809Z"
  },
  {
    "id": 2,
    "kind": "deviation",
    "phase": "44",
    "file": ".planning/REQUIREMENTS.md",
    "line": null,
    "description": "BLD-01 not flipped to Complete in REQUIREMENTS.md (still Pending) despite being implemented + evidenced in 44-GATE-EVIDENCE-02.md; no plan 44-02 final metadata commit marks it, unlike CONF-08's bea3549",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-08-04T06:00:35.186Z",
    "resolved_at": "2026-08-04T06:05:13.884Z"
  }
]
````
