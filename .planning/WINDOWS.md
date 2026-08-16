---
schema_version: 1
open_count: 3
waived_count: 0
fixed_count: 7
total_count: 10
last_updated: 2026-08-16T16:46:08.050Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 44 | unmet-truth | .planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-04.md |  | SC#4 recorded NOT-MET in 44-GATE-EVIDENCE-04.md: 44-GATE-EVIDENCE-03.md (plan 44-03, concurrent sibling) not visible from this worktree at HEAD | fixed |  | 2026-08-04T06:00:30.277Z | 2026-08-04T06:05:13.809Z |
| 2 | 44 | deviation | .planning/REQUIREMENTS.md |  | BLD-01 not flipped to Complete in REQUIREMENTS.md (still Pending) despite being implemented + evidenced in 44-GATE-EVIDENCE-02.md; no plan 44-02 final metadata commit marks it, unlike CONF-08's bea3549 | fixed |  | 2026-08-04T06:00:35.186Z | 2026-08-04T06:05:13.884Z |
| 3 | 52 | todo | tests/test_builder.py | 555 | Windows-only backslash-doubling in warning message breaks assert abs_uri in message on CI (discovered by phase 52-04 CI dispatch) | fixed |  | 2026-08-15T01:13:57.553Z | 2026-08-15T02:07:43.400Z |
| 4 | 52 | todo | tests/test_state_guard_shapes_gate.py | 781 | Locale-dependent baseline warning fragments (hardcoded Japanese) fail against English-locale CI runners in TestNoLostDiagnostics::test_warning_baseline_preserved (2 parametrized cases, all 6 OS/py lanes + Code Coverage, discovered by phase 52-04 CI dispatch) | fixed |  | 2026-08-15T01:14:02.516Z | 2026-08-15T02:07:49.645Z |
| 5 | 52 | lint-warning | tests/test_builder.py | 569 | ruff I001 unsorted import block fails Lint and Format Check on CI (never caught locally -- .venv/bin/ruff is a generic-linux ELF unrunnable on NixOS; discovered by phase 52-04 CI dispatch) | fixed |  | 2026-08-15T01:14:03.951Z | 2026-08-15T02:07:49.944Z |
| 6 | 52 | stub | typsphinx/builder.py |  | Python 3.13 changed ntpath.isabs() semantics on Windows for driveless-absolute paths (leading single backslash, no drive letter) -- TypstBuilder._track_image()'s 'if path.isabs(resolved_uri):' branch is skipped under CPython 3.13.15 on windows-latest CI, so the escape-relocation/warning path never runs; py3.12.14 on the same OS/lane is unaffected. Surfaced by CI run 31856929828 (Test Python 3.13 on windows-latest), not root-caused to a fix in Phase 52. | fixed |  | 2026-08-15T01:45:59.831Z | 2026-08-15T02:07:52.046Z |
| 7 | 53 | unrun-verify | tests/test_state_guard_shapes_gate.py |  | 7 tests reference archived .planning/phases/49-.../49-SHAPES-RED-EVIDENCE.md path; pre-existing, unrelated to 53-01's plan-verify pytest run | open |  | 2026-08-15T07:54:06.398Z |  |
| 8 | 54.1 | lint-warning | tests/test_templates_path_collision_gate.py |  | Pre-existing black-formatting defect (predates 54.1-03, authored by sibling 54.1-01); deferred to 54.1-05 or 54.1-01's own worktree merge | fixed |  | 2026-08-16T02:43:57.737Z | 2026-08-16T02:52:57.402Z |
| 9 | 57 | todo | tests/test_templates_path_collision_gate.py | 255 | Windows path-separator mismatch: aggregate collision message uses native backslash join, test asserted forward-slash substring '_templates/nested' (both windows-latest lanes, CI run 31956166848). Fix landed in plan 57-10 (assertion made separator-portable via pathlib.Path, see 57-WINDOWS-FIX-EVIDENCE.md); Windows-lane confirmation still pending plan 57-05's post-bump authority CI dispatch -- stays open until that run confirms. | open |  | 2026-08-16T15:46:01.324Z |  |
| 10 | 57 | todo | typsphinx/builder.py | 1296 | 57-10's separator-portability fix for entry 9 was measured incomplete: run 2 (CI 31959060298, both windows-latest lanes) still fails the same assertion. Root cause: builder.py:1296 builds the collision message with f"...{bundle_dir!r} collides..." -- the !r conversion means the raised message literally contains DOUBLED backslashes on Windows (Python repr() escapes each backslash char), not the single-backslash str(Path(...)) form 57-10's fix (tests/test_templates_path_collision_gate.py:262-263) assumed. 57-10 misread the doubled-backslash CI log excerpt as plain native os.sep rather than repr() escaping. Entry 9 stays open pending a corrected fix; this plan (57-05) is prohibited from touching typsphinx/ or the test file (prep-only fence) so does not attempt one. | open |  | 2026-08-16T16:46:08.050Z |  |

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
  },
  {
    "id": 3,
    "kind": "todo",
    "phase": "52",
    "file": "tests/test_builder.py",
    "line": 555,
    "description": "Windows-only backslash-doubling in warning message breaks assert abs_uri in message on CI (discovered by phase 52-04 CI dispatch)",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-08-15T01:13:57.553Z",
    "resolved_at": "2026-08-15T02:07:43.400Z"
  },
  {
    "id": 4,
    "kind": "todo",
    "phase": "52",
    "file": "tests/test_state_guard_shapes_gate.py",
    "line": 781,
    "description": "Locale-dependent baseline warning fragments (hardcoded Japanese) fail against English-locale CI runners in TestNoLostDiagnostics::test_warning_baseline_preserved (2 parametrized cases, all 6 OS/py lanes + Code Coverage, discovered by phase 52-04 CI dispatch)",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-08-15T01:14:02.516Z",
    "resolved_at": "2026-08-15T02:07:49.645Z"
  },
  {
    "id": 5,
    "kind": "lint-warning",
    "phase": "52",
    "file": "tests/test_builder.py",
    "line": 569,
    "description": "ruff I001 unsorted import block fails Lint and Format Check on CI (never caught locally -- .venv/bin/ruff is a generic-linux ELF unrunnable on NixOS; discovered by phase 52-04 CI dispatch)",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-08-15T01:14:03.951Z",
    "resolved_at": "2026-08-15T02:07:49.944Z"
  },
  {
    "id": 6,
    "kind": "stub",
    "phase": "52",
    "file": "typsphinx/builder.py",
    "line": null,
    "description": "Python 3.13 changed ntpath.isabs() semantics on Windows for driveless-absolute paths (leading single backslash, no drive letter) -- TypstBuilder._track_image()'s 'if path.isabs(resolved_uri):' branch is skipped under CPython 3.13.15 on windows-latest CI, so the escape-relocation/warning path never runs; py3.12.14 on the same OS/lane is unaffected. Surfaced by CI run 31856929828 (Test Python 3.13 on windows-latest), not root-caused to a fix in Phase 52.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-08-15T01:45:59.831Z",
    "resolved_at": "2026-08-15T02:07:52.046Z"
  },
  {
    "id": 7,
    "kind": "unrun-verify",
    "phase": "53",
    "file": "tests/test_state_guard_shapes_gate.py",
    "line": null,
    "description": "7 tests reference archived .planning/phases/49-.../49-SHAPES-RED-EVIDENCE.md path; pre-existing, unrelated to 53-01's plan-verify pytest run",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-08-15T07:54:06.398Z",
    "resolved_at": null
  },
  {
    "id": 8,
    "kind": "lint-warning",
    "phase": "54.1",
    "file": "tests/test_templates_path_collision_gate.py",
    "line": null,
    "description": "Pre-existing black-formatting defect (predates 54.1-03, authored by sibling 54.1-01); deferred to 54.1-05 or 54.1-01's own worktree merge",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-08-16T02:43:57.737Z",
    "resolved_at": "2026-08-16T02:52:57.402Z"
  },
  {
    "id": 9,
    "kind": "todo",
    "phase": "57",
    "file": "tests/test_templates_path_collision_gate.py",
    "line": 255,
    "description": "Windows path-separator mismatch: aggregate collision message uses native backslash join, test asserted forward-slash substring '_templates/nested' (both windows-latest lanes, CI run 31956166848). Fix landed in plan 57-10 (assertion made separator-portable via pathlib.Path, see 57-WINDOWS-FIX-EVIDENCE.md); Windows-lane confirmation still pending plan 57-05's post-bump authority CI dispatch -- stays open until that run confirms.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-08-16T15:46:01.324Z",
    "resolved_at": null
  },
  {
    "id": 10,
    "kind": "todo",
    "phase": "57",
    "file": "typsphinx/builder.py",
    "line": 1296,
    "description": "57-10's separator-portability fix for entry 9 was measured incomplete: run 2 (CI 31959060298, both windows-latest lanes) still fails the same assertion. Root cause: builder.py:1296 builds the collision message with f\"...{bundle_dir!r} collides...\" -- the !r conversion means the raised message literally contains DOUBLED backslashes on Windows (Python repr() escapes each backslash char), not the single-backslash str(Path(...)) form 57-10's fix (tests/test_templates_path_collision_gate.py:262-263) assumed. 57-10 misread the doubled-backslash CI log excerpt as plain native os.sep rather than repr() escaping. Entry 9 stays open pending a corrected fix; this plan (57-05) is prohibited from touching typsphinx/ or the test file (prep-only fence) so does not attempt one.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-08-16T16:46:08.050Z",
    "resolved_at": null
  }
]
````
