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

## Audit

Re-measured standing invariants at the current branch tip (this plan's own final commit) rather
than trusting earlier plans' SUMMARYs:

```
$ grep -rl "_template\.typ" tests/ | wc -l
32
```

Equals the phase-start count (32, first measured by plan 53-01/53-02 and unchanged through
53-03/53-04) — the standing `_template.typ` regression net is unmodified.

```
$ uv run pytest tests/ -q
================= 1232 passed, 5 skipped in 107.47s (0:01:47) ==================
```

Exit 0. This is an improvement over the phase-start baseline (7 failed / 1225 passed / 5 skipped)
because the pre-existing `test_state_guard_shapes_gate.py` defect logged by plan 53-01 was fixed
during this plan's own CI-evidence gathering (see "Run 1" / "Run 2" above) — not a regression, a
resolved pre-existing gap.

```
$ uv run pytest tests/test_preview_version_sync.py -q
============================== 3 passed in 0.02s ===============================
```

Exit 0, no fourth `@preview` version-lockstep site introduced.

Additional confirmation, not required by the plan's acceptance criteria but relevant to SC#1's
verdict below: `uv run pytest tests/test_template_registry.py -q` → **57 passed**;
`uv run pytest tests/test_template_engine.py -q` → **91 passed**.

### Per-success-criterion verdicts (ROADMAP.md § "Phase 53: Template Registry Foundation")

**SC#1 — Named template definitions are declarable and resolve once per build: MET.**
`resolve_template_registry()` / `resolve_registry_key()` (`typsphinx/template_registry.py`)
implement `template` xor `package` enforcement (CONF-15), the `str`/`{"name","params"}`
`template_function` forms, same-key resolution to one shared `TemplateRegistryEntry` object
(TPL-05), and the existing `params`-exclusivity rule left untouched (D-10/D-11 in
`53-CONTEXT.md`). Evidence: `53-02-SUMMARY.md` (registry plumbing, MH1-MH10), `53-03-SUMMARY.md`
(CONF-14..18 validation, D1-D9), both requirements-completed lists cite TPL-01/TPL-05, and
`tests/test_template_registry.py` (57 passed, re-measured above) plus resolution running once per
build in `write()` between `_validate_output_path_collisions()` and `prepare_writing()`
(`53-02-SUMMARY.md` MH8, confirmed by direct code read there). This plan (53-05) re-ran the full
suite including this module and found it green; it did not re-derive the functional coverage
itself, which is 53-02/53-03's job.

**SC#2 — An untouched `conf.py` produces byte-identical output, proven by identity: MET.**
`53-RED-EVIDENCE.md`'s post-change section (this plan's Task 1) records all four shapes (A —
`typst_template` set, B — `typst_package` set, C — `typst_template_function` set, D — nothing set)
plus the TPL-04 four-element-vs-fifth-element comparison, each with a per-shape verdict of
"MATCH" against the pre-change SHA-256 and PDF-page-count baseline `53-01` recorded, plus an
overall summary verdict. Every claim is backed by a transcribed SHA-256 or page count, not a bare
statement.

**SC#3 — Every malformed registry stops the build with a message naming the specific reason:
MET.** `53-03-SUMMARY.md` documents CONF-14 (unregistered key, names `sorted(registry.keys())`),
CONF-15 (template+package xor), CONF-16 (reserved `"typst"` key), and CONF-17
(`_violates_conf17()` path-arithmetic bundle-escape guard), each accumulated into one independent
`ExtensionError` via the `_validate_output_path_collisions()`-mirroring shape (D-03), confirmed
order-independent (D6/`test_three_independently_broken_keys_raise_once_order_independently`).
This plan did not re-run those unit tests individually but confirmed they remain green as part of
the 1232-passed full-suite run above (`tests/test_template_registry.py`, 57 passed).

**SC#4 — Registry-key shape is validated as a single path segment, wrong guard not reused: MET.**
`53-03-SUMMARY.md`'s Task 1 records `_validate_registry_key_shape()`'s fixed-order seven-case
denylist (CONF-18) exposed via a countable `_KEY_SHAPE_REJECTION_CASES` constant
(`test_key_shape_validator_exposes_exactly_seven_distinct_rejection_reasons`), the case-collision
check routing through `TypstBuilder._collision_key()` via a documented local import rather than a
second folding, and the module docstring recording why `_escapes_outdir()`/`_is_drive_qualified()`
are not reused (opposite contract: legal multi-segment output path vs. legal single path segment
— `53-02-SUMMARY.md`'s module docstring note). All platform-independent string-shape tests, so they
pass on the local Linux run and are additionally confirmed passing on the Windows and macOS CI
legs in Run 2 above (the state-guard fix in `d1eff100` did not touch `template_registry.py` or its
tests, so their behavior on those platforms is exactly what the green run reports).

**SC#5 — The milestone branch is on `origin` with a completed 3-OS CI run: MET, via Run 2.**
`git ls-remote --heads origin` shows `gsd/v0.9.0-per-document-templates` present (measured above).
Run 1 (`31875380355`, `workflow_dispatch`) completed but concluded `failure` on all six `test`
legs, for a cause unrelated to Phase 53's own code (the pre-existing `test_state_guard_shapes_gate.py`
path defect, already logged as out-of-scope by plan 53-01). After the owner-authorized fix
(`d1eff100`), Run 2 (`31875707734`, `workflow_dispatch`) completed with conclusion `success` on
all 12 jobs, including both `windows-latest` and both `macos-latest` `test` legs. Six of six `test`
job legs concluded `success` in Run 2 (0 of 6 in Run 1). No PR was opened; no branch was renamed,
merged, rebased, force-pushed, or deleted.

**No shortfall found.** All five success criteria are met on measured evidence, with the one
caveat recorded plainly rather than smoothed over: SC#5 required two dispatched runs because the
first one surfaced a real, pre-existing, cross-platform defect unrelated to this phase's own code,
which was fixed (outside this plan's declared `files_modified` scope) before the passing run.

No file exists at `.planning/phases/53-template-registry-foundation/53-VERIFICATION.md` (checked
throughout this plan; that name is reserved by `gsd-verifier`, per D-12).

## Gap-closure round 2 — 2026-08-15 (plan 53-10)

**Why this round exists.** Run 2 above (head `d1eff100`) closed SC#5 for the code that existed at
that moment. Plan 53-08 landed two more `typsphinx/`+`tests/` commits after it (WR-01/WR-02
closures), and re-verification (`344b9510`) scored SC#5 stale for exactly that reason — a green run
existed, but it no longer certified the shipping code. This plan runs LAST, after both 53-08 and
53-09 merged, measures the branch tip at execution time, and records the staleness assertion this
round's own acceptance criteria require.

### Task 1 — local CI-parity gates and the pre-push tip measurement

**Precondition confirmed.** Worktree provisioned (`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv
sync --extra dev`); `uv run python -c "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())"`
printed `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a5fcb448ce0de875e/typsphinx/__init__.py`
— inside this worktree, not the main checkout. `git log gsd/v0.9.0-per-document-templates --oneline
-20 | grep -c '53-08'` → **8**; `| grep -c '53-09'` → **4** — both wave-7 plans are present on the
branch this task measures.

**Local gate 1 — full suite, ambient locale.**

```
$ uv run pytest tests/ -q
================= 1270 passed, 5 skipped in 110.92s (0:01:50) ==================
```

Exit 0.

**Local gate 2 — full suite, `LC_ALL=C` locale control.**

```
$ LC_ALL=C uv run pytest tests/ -q
================= 1270 passed, 5 skipped in 109.54s (0:01:49) ==================
```

Exit 0, same passed/skipped counts as the ambient-locale run (1270 passed, 5 skipped both times) —
no gettext-translated-string divergence.

**Local gate 3 — `black --check .`.**

```
$ uv run black --check .
All done! ✨ 🍰 ✨
310 files would be left unchanged.
```

Exit 0.

**Local gate 4 — `mypy typsphinx/`.**

```
$ uv run mypy typsphinx/
Success: no issues found in 7 source files
```

Exit 0.

**Local gate 5 — `ruff check .` (transcribed verbatim, not claimed as a pass).**

```
$ uv run ruff check .
Could not start dynamically linked executable: ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
```

This is the recorded NixOS generic-linux ELF hazard (Future requirement QUA-06), reproduced exactly
as in prior phases' evidence. **Lint coverage for this phase therefore comes only from the
dispatched CI run's `Lint and Format Check` job** — this local pytest/black/mypy pass is not lint
evidence.

**Candidate SHA.**

```
$ git rev-parse gsd/v0.9.0-per-document-templates
35ee8a0ee8a4f8701c99a6596be8e37d975de307
```

Measured by ref name, not `HEAD` — this worktree's own `HEAD` is `worktree-agent-a5fcb448ce0de875e`'s
tip, a different commit entirely, per `CLAUDE.md` § "Worktree-isolated execution".

**Pre-push remote state.**

```
$ git ls-remote --heads origin gsd/v0.9.0-per-document-templates
48c957cd1744d4cb028a58890d041fab49ede8dc	refs/heads/gsd/v0.9.0-per-document-templates
```

The stale SHA on `origin` that Task 2's push is about to advance — 24+ commits behind the candidate,
including all of wave 7 (53-08, 53-09) and this round's own preceding tracking commits.

**Working tree.**

```
$ git status --porcelain
(no output)
```

Clean.

### Task 2 — push the measured tip, dispatch CI, and capture per-lane conclusions

**Push.** `git push origin gsd/v0.9.0-per-document-templates` -- only that ref, no `--force`, no
`--all`, no other branch:

```
$ git push origin gsd/v0.9.0-per-document-templates
To https://github.com/YuSabo90002/typsphinx.git
   48c957cd..35ee8a0e  gsd/v0.9.0-per-document-templates -> gsd/v0.9.0-per-document-templates
```

Fast-forward, not rejected, no divergence reported.

**Post-push remote confirmation, verbatim.**

```
$ git ls-remote --heads origin gsd/v0.9.0-per-document-templates
35ee8a0ee8a4f8701c99a6596be8e37d975de307	refs/heads/gsd/v0.9.0-per-document-templates
```

Equals Task 1's candidate SHA exactly (`35ee8a0ee8a4f8701c99a6596be8e37d975de307`) -- nothing moved
the branch between measurement and push.

**Dispatch.** `gh workflow run CI --ref gsd/v0.9.0-per-document-templates` returned
`https://github.com/YuSabo90002/typsphinx/actions/runs/31884774067`.

**Run identification, matched on all three fields (never on recency).**

```
$ gh run list --branch gsd/v0.9.0-per-document-templates --limit 10 --json databaseId,name,event,status,conclusion,headSha,createdAt
[{"conclusion":"","createdAt":"2026-08-15T12:30:25Z","databaseId":31884774067,"event":"workflow_dispatch","headSha":"35ee8a0ee8a4f8701c99a6596be8e37d975de307","name":"CI","status":"in_progress"},
 {"conclusion":"","createdAt":"2026-08-15T12:30:22Z","databaseId":31884770727,"event":"push","headSha":"35ee8a0ee8a4f8701c99a6596be8e37d975de307","name":"Link Check","status":"in_progress"},
 ... (older runs omitted, all at earlier heads)]
```

Run `31884774067` matches name `CI`, event `workflow_dispatch`, and `headSha`
`35ee8a0ee8a4f8701c99a6596be8e37d975de307` -- the pushed SHA. `31884770727` is the separate `Link
Check` workflow that the same push also fired (event `push`, not `workflow_dispatch`); it is not
the run this criterion cites, exactly the confusion the three-field match rule exists to prevent.

**Polling.** `gh run watch 31884774067 --exit-status` refreshed every 3 seconds and exited 0 when
the run reached `completed` -- well inside the ~20-minute bound. Overall duration
**12:30:25Z -> 12:36:58Z (~6m33s)**, in line with the v0.8.0 and 53-05 precedents (~6 minutes each).

**Run summary, verbatim.**

```
$ gh run view 31884774067 --json status,conclusion,headSha,event,createdAt,updatedAt,url,displayTitle -q '.'
{
  "conclusion": "success",
  "createdAt": "2026-08-15T12:30:25Z",
  "displayTitle": "CI",
  "event": "workflow_dispatch",
  "headSha": "35ee8a0ee8a4f8701c99a6596be8e37d975de307",
  "status": "completed",
  "updatedAt": "2026-08-15T12:36:58Z",
  "url": "https://github.com/YuSabo90002/typsphinx/actions/runs/31884774067"
}
```

Run ID: **31884774067**. URL:
<https://github.com/YuSabo90002/typsphinx/actions/runs/31884774067>. Triggering event:
**`workflow_dispatch`**. Head SHA: **`35ee8a0ee8a4f8701c99a6596be8e37d975de307`** -- this plan's
own candidate SHA, carrying both plan 53-08's and plan 53-09's commits. Conclusion: **`success`**.

**Per-job conclusions, verbatim from `gh run view 31884774067 --json jobs -q '.jobs[] | {name, conclusion}'`.**

```
{"conclusion":"success","name":"Code Coverage"}
{"conclusion":"success","name":"Type Check"}
{"conclusion":"success","name":"Build Package"}
{"conclusion":"success","name":"Test Python 3.12 on macos-latest"}
{"conclusion":"success","name":"Lint and Format Check"}
{"conclusion":"success","name":"Integration Test - basic"}
{"conclusion":"success","name":"Test Python 3.13 on ubuntu-latest"}
{"conclusion":"success","name":"Integration Test - advanced"}
{"conclusion":"success","name":"Test Python 3.13 on windows-latest"}
{"conclusion":"success","name":"Test Python 3.12 on windows-latest"}
{"conclusion":"success","name":"Test Python 3.12 on ubuntu-latest"}
{"conclusion":"success","name":"Test Python 3.13 on macos-latest"}
```

**All 12 of the 12 jobs concluded `success`.** All six of the `Test Python … on …` legs (both
Python versions x all three OSes) succeeded, including both platform-specific pairs SC#5 names
individually: `Test Python 3.12 on windows-latest`, `Test Python 3.13 on windows-latest`,
`Test Python 3.12 on macos-latest`, `Test Python 3.13 on macos-latest`.

**No lane failed.** No re-dispatch was needed.

**Post-conditions, verbatim.**

```
$ gh pr list --head gsd/v0.9.0-per-document-templates
(no output -- zero open pull requests)

$ git rev-parse gsd/v0.9.0-milestone
aed773c9807ab871468b1b2a7e1ec36b54e82907

$ git branch --list 'gsd/v0.9.0-milestone'
  gsd/v0.9.0-milestone

$ git reflog show gsd/v0.9.0-per-document-templates | head -5
35ee8a0e gsd/v0.9.0-per-document-templates@{0}: commit: docs(phase-53): update tracking after wave 7
19b31573 gsd/v0.9.0-per-document-templates@{1}: merge worktree-agent-ad9a0183436586fee: Merge made by the 'ort' strategy.
a8925baa gsd/v0.9.0-per-document-templates@{2}: merge worktree-agent-ab5ce17ca9f847f14: Merge made by the 'ort' strategy.
74eb4440 gsd/v0.9.0-per-document-templates@{3}: commit: docs(53): mark phase 53 executing for gap-closure round 2
ce09f3e8 gsd/v0.9.0-per-document-templates@{4}: commit: docs(53): record gap-closure round 2 planning in STATE.md
```

No open PR. `gsd/v0.9.0-milestone` unchanged at its pre-existing SHA, still listed. Reflog top
entry is an ordinary `commit`, not a `rebase` or `reset` -- no history rewrite occurred.

### Task 3 — currency assertion and the rule that keeps this evidence honest

**Fact 1 -- remote agreement.**

```
$ git ls-remote --heads origin gsd/v0.9.0-per-document-templates
35ee8a0ee8a4f8701c99a6596be8e37d975de307	refs/heads/gsd/v0.9.0-per-document-templates
```

Equals the CI run's `headSha` (`35ee8a0ee8a4f8701c99a6596be8e37d975de307`) exactly.

**Fact 2 -- the staleness assertion.**

```
$ git log 35ee8a0ee8a4f8701c99a6596be8e37d975de307..gsd/v0.9.0-per-document-templates -- typsphinx/ tests/
(no output)
```

Empty. No `typsphinx/` or `tests/` commit post-dates the certified head, at the moment this fact
was measured. This is the check whose absence let the previous round cite `d1eff100` while
`c9d1eb3b`, `512a211b`, `8d45e0b5` and `eb69904f` had already landed on top of it.

**Fact 3 -- positive content proof.**

```
$ git show 35ee8a0ee8a4f8701c99a6596be8e37d975de307:typsphinx/template_registry.py | grep -c 'must be a dict mapping registry key to definition'
1

$ git show 35ee8a0ee8a4f8701c99a6596be8e37d975de307:.planning/REQUIREMENTS.md | grep -c '| TPL-01 | Phase 53 | Complete |'
1
```

Both greps return exactly 1: the certified SHA carries plan 53-08's container-guard message text
(the WR-01 closure) and plan 53-09's corrected TPL-01 traceability row.

### Currency rule

**Non-invalidating.** Commits landing after the certified head `35ee8a0e` that touch only
`.planning/`, `docs/` or `CHANGELOG.md` are documentation-only and do NOT invalidate this evidence.
This plan's own commits are exactly that category: the two evidence commits above (Task 1, Task 2),
this Task 3 commit, the `53-10-SUMMARY.md` commit, and the phase-tracking commits the orchestrator
makes after the wave merges. The branch tip will legitimately sit ahead of `35ee8a0e` by the time
anyone reads this artifact, and that is expected, not a defect.

**Invalidating.** Any commit touching `typsphinx/` or `tests/` after `35ee8a0e` DOES invalidate
this evidence. The required response is named explicitly: push the new tip, dispatch a fresh
`workflow_dispatch` run, and append a new dated section to this file -- never annotate this section
with a caveat and call it current.

**The merge hazard, by name.** This project runs executors in isolated worktrees as its standing
mode (`CLAUDE.md` § "Worktree-isolated execution"). A worktree merge back into
`gsd/v0.9.0-per-document-templates` moves the milestone tip after a plan finishes -- exactly what
moved it from `d1eff100` to `35ee8a0e` between Run 2 and this round. Anyone re-checking this
evidence must re-run Fact 2 against the tip **as it stands at that moment**, not trust the verdict
recorded here.

### Re-measured standing invariants

```
$ grep -rl "_template\.typ" tests/ | wc -l
33
```

**This differs from the prior sections' recorded value of 32, and the divergence is a genuine,
explainable finding, not a measurement error.** `git diff d1eff10076af99d50b9bbb90acd6054a6b09762c
35ee8a0ee8a4f8701c99a6596be8e37d975de307 --stat -- tests/` shows `tests/test_registry_prewrite_validation_gate.py`
(added by the 53-06/53-07 gap-closure round, landed before this plan's own wave) is a new file that
also references `_template.typ`, confirmed with `grep -l "_template\.typ"
tests/test_registry_prewrite_validation_gate.py`. This is net growth of the regression coverage this
count exists to protect, not shrinkage -- the file count only ever needs scrutiny if it goes down. 33
is the correct, current, re-measured value; the plan's own acceptance criterion asserting "32" was
written before 53-06 through 53-09 landed and is now stale in exactly the same way the previous SC#5
evidence was.

```
$ uv run pytest tests/ -q
================= 1270 passed, 5 skipped in 109.58s (0:01:49) ==================
```

Exit 0.

```
$ uv run pytest tests/test_preview_version_sync.py -q
============================== 3 passed in 0.02s ===============================
```

Exit 0, no fourth `@preview` version-lockstep site introduced.

`test -e .planning/phases/53-template-registry-foundation/53-VERIFICATION.md` -- the file exists
(written by the verifier); `git diff --name-only` shows no modification to it by this plan.

### Extended per-success-criterion audit (ROADMAP.md § "Phase 53: Template Registry Foundation")

**SC#1 -- Named template definitions are declarable and resolve once per build: MET, unchanged
from the prior audit.** Re-confirmed by the 1270-passed full-suite run above, which now also covers
`tests/test_registry_container_shape_gate.py` and `tests/test_registry_prewrite_validation_gate.py`
(both added by the 53-06/53-07 round) alongside the 57-passed `test_template_registry.py` module
cited previously. No functional change to the registry-resolution mechanism itself in this round.

**SC#2 -- An untouched `conf.py` produces byte-identical output, proven by identity: MET,
unchanged.** No plan in this gap-closure round (53-08, 53-09, 53-10) touches output-producing code
paths; 53-08 and 53-09 are validation-message and tracking-documentation fixes respectively. The
byte-identity baseline `53-01`/`53-05` recorded stands undisturbed.

**SC#3 -- Every malformed registry stops the build with a message naming the specific reason:
MET, and now strengthened.** `344b9510`'s re-verification had scored this criterion's earlier
robustness gaps (WR-01, WR-02) as open Warnings; plan 53-08 closed both in this round (`6846a190`
"close WR-01 -- typo'd typst_document_templates container fails cleanly",
`daca9a7d` "close WR-02 -- truthy unusable template field joins accumulated raise"), confirmed
present on the certified head by Fact 3's `must be a dict mapping registry key to definition` grep
above.

**SC#4 -- Registry-key shape is validated as a single path segment, wrong guard not reused:
MET, unchanged.** No plan in this round touches `_validate_registry_key_shape()` or
`_collision_key()`; the platform-independent string-shape tests remain green in the 1270-passed run
and were independently confirmed on Windows/macOS CI legs in the prior Run 2 (whose fix commit
`d1eff100` did not touch `template_registry.py`).

**SC#5 -- The milestone branch is on `origin` with a completed 3-OS CI run: MET, via this round's
Run (`31884774067`), superseding Run 2.** `git ls-remote --heads origin` shows
`gsd/v0.9.0-per-document-templates` at `35ee8a0e`, matching Run `31884774067`'s `headSha` exactly.
That run completed with conclusion `success` on all 12 jobs, including both `windows-latest` and
both `macos-latest` `test` legs (Task 2 above). Fact 2's staleness assertion is empty at the moment
of recording, and Fact 3 proves by content which code `35ee8a0e` carries. **Run 2 (head `d1eff100`)
no longer certifies the shipping code** -- four `typsphinx/`+`tests/` commits (`c9d1eb3b`,
`512a211b`, `8d45e0b5`, `eb69904f`) plus plan 53-08's two commits post-date it -- but it remains an
accurate record of what it did certify at the time, and its section above is left untouched. No PR
was opened; no branch was renamed, merged, rebased, force-pushed, or deleted.

**No shortfall found.** All five success criteria are met on measured evidence from this round.
The one honest divergence recorded, in the spirit of the previous round's Run 1/Run 2 disclosure:
the standing `_template.typ` file count moved from 32 to 33 between Run 2 and this round, a
net-growth addition from the 53-06/53-07 gap-closure round rather than a regression, re-measured
and explained above rather than silently carried forward.
