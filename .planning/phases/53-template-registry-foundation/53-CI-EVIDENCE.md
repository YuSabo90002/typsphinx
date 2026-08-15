# Phase 53: SC#5 Milestone Branch Push and CI Evidence

**Purpose:** SC#5 requires `gsd/v0.9.0-per-document-templates` on `origin` plus a completed
`workflow_dispatch` CI run over it whose `windows-latest` and `macos-latest` `test` job legs both
conclude `success`. This file records what was actually measured, including a first dispatched
run that failed for reasons unrelated to Phase 53's own code, and the second run that closed SC#5
after the failure's cause was fixed.

## Branch push

```
$ git push origin gsd/v0.9.0-per-document-templates
To https://github.com/YuSabo90002/typsphinx.git
 * [new branch]        gsd/v0.9.0-per-document-templates -> gsd/v0.9.0-per-document-templates
```

Confirmed landed with `git ls-remote --heads origin` (re-measured at the end of this evidence
session, after the fix commit below, so the SHA reflects the branch's current tip):

```
$ git ls-remote --heads origin | grep gsd/v0.9.0-per-document-templates
d1eff10076af99d50b9bbb90acd6054a6b09762c	refs/heads/gsd/v0.9.0-per-document-templates
```

Only that one ref was pushed. No force flag was used. No pull request was opened (the owner chose
`workflow_dispatch` over a draft PR):

```
$ gh pr list --head gsd/v0.9.0-per-document-templates
(no output -- zero open pull requests)
```

The stale local `gsd/v0.9.0-milestone` branch was left untouched, at its pre-existing SHA:

```
$ git branch --list 'gsd/v0.9.0-milestone'
  gsd/v0.9.0-milestone
$ git rev-parse gsd/v0.9.0-milestone
aed773c9807ab871468b1b2a7e1ec36b54e82907
```

## Run 1 — `31875380355` (this plan's dispatch, head `9172aa1c`) — FAILED

Dispatched with `gh workflow run CI --ref gsd/v0.9.0-per-document-templates`, against the branch
tip at that time: `9172aa1c` (this plan's Task 1 commit, the post-change byte-identity evidence).
Polled with `gh run list --branch gsd/v0.9.0-per-document-templates --limit 5` until `completed`.

```
$ gh run view 31875380355 --json status,conclusion,headSha,event,createdAt,updatedAt,url -q '.'
{
  "conclusion": "failure",
  "createdAt": "2026-08-15T08:48:09Z",
  "event": "workflow_dispatch",
  "headSha": "9172aa1ca755bf2156e881463ddb10b545d19471",
  "status": "completed",
  "updatedAt": "2026-08-15T08:53:59Z",
  "url": "https://github.com/YuSabo90002/typsphinx/actions/runs/31875380355"
}
```

Duration: ~5m50s (08:48:09Z -> 08:53:59Z).

Per-job conclusions, verbatim from `gh run view 31875380355 --json jobs -q '.jobs[] | {name, conclusion}'`:

```
{"conclusion":"failure","name":"Test Python 3.13 on macos-latest"}
{"conclusion":"success","name":"Lint and Format Check"}
{"conclusion":"success","name":"Type Check"}
{"conclusion":"success","name":"Integration Test - advanced"}
{"conclusion":"success","name":"Integration Test - basic"}
{"conclusion":"failure","name":"Test Python 3.12 on ubuntu-latest"}
{"conclusion":"failure","name":"Test Python 3.12 on macos-latest"}
{"conclusion":"failure","name":"Test Python 3.12 on windows-latest"}
{"conclusion":"failure","name":"Test Python 3.13 on windows-latest"}
{"conclusion":"failure","name":"Code Coverage"}
{"conclusion":"success","name":"Build Package"}
{"conclusion":"failure","name":"Test Python 3.13 on ubuntu-latest"}
```

**6 of the 6 `Test Python … on …` legs concluded `failure`** (both Python versions, all three OSes:
`ubuntu-latest`, `windows-latest`, `macos-latest`), plus `Code Coverage` (which runs the same
suite). `Lint and Format Check`, `Type Check`, `Integration Test - basic`, `Integration Test -
advanced`, and `Build Package` all concluded `success`.

**Root cause, confirmed by log excerpt** (`gh run view 31875380355 --log-failed`, `Test Python
3.13 on macos-latest` job, and identically on `Test Python 3.12 on ubuntu-latest`):

```
tests/test_state_guard_shapes_gate.py::TestNoLostDiagnostics::test_warning_baseline_preserved[state_guard_self_and_url_gate] FAILED [ 67%]
tests/test_state_guard_shapes_gate.py::TestNoLostDiagnostics::test_warning_baseline_preserved[state_guard_cycle_gate] FAILED [ 67%]
tests/test_state_guard_shapes_gate.py::TestNoLostDiagnostics::test_warning_baseline_preserved[state_guard_selfref_gate] FAILED [ 67%]
tests/test_state_guard_shapes_gate.py::TestNoLostDiagnostics::test_warning_baseline_preserved[state_guard_glob_gate] FAILED [ 67%]
tests/test_state_guard_shapes_gate.py::TestNoLostDiagnostics::test_warning_baseline_preserved[state_guard_orphan_ref_gate] FAILED [ 67%]
tests/test_state_guard_shapes_gate.py::TestNoLostDiagnostics::test_warning_baseline_preserved[state_guard_three_master_gate] FAILED [ 67%]
tests/test_state_guard_shapes_gate.py::TestNoLostDiagnostics::test_warning_baseline_preserved[state_guard_substring_key_gate] FAILED [ 67%]
============ 7 failed, 1225 passed, 5 skipped in 251.98s (0:04:11) =============
```

This is **exactly the 7-test pre-existing baseline** carried since plan 53-01 (documented there,
in `deferred-items.md`, and in `.planning/WINDOWS.md`): `EVIDENCE_PATH` in
`tests/test_state_guard_shapes_gate.py` was hardcoded to
`.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-SHAPES-RED-EVIDENCE.md`,
a path the v0.8.0 milestone archival commit (`2ea4db0f`) had relocated to
`.planning/milestones/v0.8.0-phases/49-.../49-SHAPES-RED-EVIDENCE.md`. **This is a pre-existing
defect that predates this plan's own commit and is identical across all three OSes** — it is not
caused by, and is not part of, Phase 53's own template-registry changes. Plans 53-01 through 53-04
had already logged it as an out-of-scope, deferred item because the local-suite runs those plans
performed never previously executed this gate against a real, fresh CI environment where the stale
path had never worked.

**Escalation and fix (outside this plan's declared scope — `.planning/phases/…/53-05-PLAN.md`
`files_modified` names only `53-RED-EVIDENCE.md` and `53-CI-EVIDENCE.md`).** Because SC#5's own
acceptance criteria require the `windows-latest`/`macos-latest` legs to conclude `success`, and
this failure blocked that criterion for a cause unrelated to any Phase 53 code, the orchestrator
escalated to the project owner, who authorized a fix. Commit `d1eff100` ("fix(53): locate
49-SHAPES-RED-EVIDENCE.md across archived milestones") replaced the hardcoded `EVIDENCE_PATH`
constant with a `_locate_evidence()` helper that searches `.planning/phases/` and every
`.planning/milestones/*/` root, so a future milestone archival cannot rebreak the same gate the
same way. This commit is **not** part of this plan's own deliverable; it is recorded here because
it is the fix that let SC#5 close, and omitting the failed-then-fixed sequence would misrepresent
what actually happened.

## Run 2 — `31875707734` (dispatched over the fix, head `d1eff100`) — SUCCESS

Re-measured directly (not transcribed from the escalation report):

```
$ gh run view 31875707734 --json status,conclusion,headSha,event,createdAt,updatedAt,url,displayTitle -q '.'
{
  "conclusion": "success",
  "createdAt": "2026-08-15T08:56:07Z",
  "displayTitle": "CI",
  "event": "workflow_dispatch",
  "headSha": "d1eff10076af99d50b9bbb90acd6054a6b09762c",
  "status": "completed",
  "updatedAt": "2026-08-15T09:02:21Z",
  "url": "https://github.com/YuSabo90002/typsphinx/actions/runs/31875707734"
}
```

Run ID: **31875707734**. URL: <https://github.com/YuSabo90002/typsphinx/actions/runs/31875707734>.
Triggering event: **`workflow_dispatch`**. Head SHA: **`d1eff10076af99d50b9bbb90acd6054a6b09762c`**
(the fix commit, on top of this plan's `9172aa1c`). Total duration: **~6m14s**
(2026-08-15T08:56:07Z -> 2026-08-15T09:02:21Z).

Per-job conclusions, verbatim from `gh run view 31875707734 --json jobs -q '.jobs[] | {name, conclusion}'`:

```
{"conclusion":"success","name":"Integration Test - basic"}
{"conclusion":"success","name":"Code Coverage"}
{"conclusion":"success","name":"Lint and Format Check"}
{"conclusion":"success","name":"Build Package"}
{"conclusion":"success","name":"Integration Test - advanced"}
{"conclusion":"success","name":"Type Check"}
{"conclusion":"success","name":"Test Python 3.13 on ubuntu-latest"}
{"conclusion":"success","name":"Test Python 3.12 on windows-latest"}
{"conclusion":"success","name":"Test Python 3.12 on ubuntu-latest"}
{"conclusion":"success","name":"Test Python 3.12 on macos-latest"}
{"conclusion":"success","name":"Test Python 3.13 on macos-latest"}
{"conclusion":"success","name":"Test Python 3.13 on windows-latest"}
```

**All 12 jobs concluded `success`.** Both `windows-latest` legs (`Test Python 3.12 on
windows-latest`, `Test Python 3.13 on windows-latest`) and both `macos-latest` legs (`Test Python
3.12 on macos-latest`, `Test Python 3.13 on macos-latest`) are present in that list and each shows
`"conclusion":"success"` — SC#5's literal requirement is met by this run.

**All six of the six `Test Python … on …` `test` job legs concluded `success`** (ubuntu/windows/
macos x Python 3.12/3.13), plus `Code Coverage`, `Lint and Format Check`, `Type Check`,
`Integration Test - basic`, `Integration Test - advanced`, and `Build Package`.

Local confirmation at the same head (`d1eff100`, this plan's branch tip at the time of writing this
artifact):

```
$ uv run pytest tests/ -q
================= 1232 passed, 5 skipped in 107.58s (0:01:47) ==================
```

No failures locally either, at the commit the green CI run measured.

## Lint and type coverage note

Per this phase's `key_links`, lint and type coverage for this phase come **only** from the
dispatched CI run — `ruff` cannot execute locally in this sandbox (NixOS cannot exec the
generic-linux `.venv`-installed `ruff` binary). Run 2's `Lint and Format Check` job (which runs
both `black --check .` and `ruff check .`) and `Type Check` job (`mypy typsphinx/`) both concluded
`success`, so this is the run that discharges lint/type coverage for Phase 53 as a whole, not a
local pytest pass.

## Summary

- `gsd/v0.9.0-per-document-templates` is present on `origin`, current tip `d1eff100`.
- Run 1 (`31875380355`, head `9172aa1c`) is a real `workflow_dispatch` CI run that **failed** —
  6 of 6 `test` legs (all platforms, all Python versions) failed on the exact same
  pre-existing 7-test baseline this phase's earlier plans had already logged as out-of-scope.
  This is recorded honestly rather than omitted.
- The root cause was fixed (commit `d1eff100`, outside this plan's declared file scope, owner-
  authorized) and pushed to the same branch.
- Run 2 (`31875707734`, head `d1eff100`) is a real `workflow_dispatch` CI run that **completed with
  conclusion `success`** on all 12 jobs, including both `windows-latest` and both `macos-latest`
  `test` legs. **This is the run SC#5's evidence cites as the completed, passing run.**
- No pull request was opened by either dispatch. No branch was renamed, merged, rebased,
  force-pushed, or deleted; `gsd/v0.9.0-milestone` remains at its pre-existing SHA
  `aed773c9807ab871468b1b2a7e1ec36b54e82907`.
