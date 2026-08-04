# 43-GATE-EVIDENCE-06.md — SC#5 Completed-CI Evidence and Phase 44 Handoff

**Phase:** 43 (Table State Correctness — Nested Tables + Empty-Title Anchors)
**Wave:** 4
**Plan:** 43-05, Task 2
**Executed:** 2026-08-04 (worktree agent, isolated worktree
`worktree-agent-aa3956ec1949a9fc1`)

Discharges the second half of roadmap SC#5: a COMPLETED GitHub Actions run against
`gsd/v0.7.1-bug-fix-round` at a tip that contains all four requirements' changes (TBL-04, FIG-01,
TBL-05, QUA-01), with every Windows lane's conclusion recorded by name, cross-checked against the
lane set independently recorded at the wave-1 push in `43-GATE-EVIDENCE-02.md`. Every command
below was executed in THIS session, in this worktree.

---

## 0. A real premise correction, measured independently in this session

Both this plan and the roadmap assumed a `git push` of the milestone branch triggers the CI
matrix. **It does not.** Read directly from `.github/workflows/ci.yml` in this session:

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:
```

`gsd/v0.7.1-bug-fix-round` is neither `main` nor `develop`, so `push` events on it never satisfy
`ci.yml`'s branch filter — only the branch-unfiltered `links.yml` ("Link Check") fires from a
plain push, confirmed directly in § 2 below. `ci.yml` already declares `workflow_dispatch:` as a
pre-existing, unmodified trigger, so this task uses that mechanism explicitly
(`gh workflow run ci.yml --ref gsd/v0.7.1-bug-fix-round`) rather than relying on the push event.
**No file was modified to make this happen** — `.github/workflows/ci.yml`'s content is unchanged
by this plan (confirmed, § 6).

This is a second, independent reason (beyond "the branch was never pushed to origin before this
phase") that the v0.7.0 Windows lanes never ran against the milestone branch: even after a push,
`ci.yml` structurally cannot fire without either a PR into `main`/`develop` or an explicit
`workflow_dispatch`. **Phase 44 and the release process need to know this**: any future phase
that pushes a milestone branch and expects `ci.yml` to fire from the push alone will observe the
same silent non-trigger this plan diagnosed. The only two ways to get `ci.yml` to run against a
milestone branch before its release PR are (a) `workflow_dispatch`, as this task does, or (b)
retargeting the workflow's `on.push.branches` list, which is out of this plan's scope
(`files_modified` is exactly the two `.planning/` evidence files).

This premise correction was independently re-derived in this session by reading `ci.yml` directly
(§ 0 above), not transcribed from `43-GATE-EVIDENCE-02.md` or the plan prompt — both of which
already recorded the same finding when plan 43-02 hit it at the wave-1 push. The two independent
measurements (43-02's and this one) agree.

---

## 1. Push the finished phase tip

**Pre-push baseline:**

**Command:** `git log -1 --oneline gsd/v0.7.1-bug-fix-round`
```
1f24e24 docs(phase-43): update tracking after wave 3
```

**Command:** `git ls-remote --heads origin | grep gsd/v0.7.1-bug-fix-round`
```
7bdaf40ee131a63dc5cf9789d90668c54948a117	refs/heads/gsd/v0.7.1-bug-fix-round
```

The remote was still at `7bdaf40` — the wave-1 baseline tip plan 43-02 pushed
(`43-GATE-EVIDENCE-02.md` § 3), carrying none of this phase's four requirements' fixes. The local
`gsd/v0.7.1-bug-fix-round` branch had since advanced to `1f24e24` as waves 1-3 merged in (visible
from this worktree because git worktrees share the underlying ref store with the main checkout).

**Command:** `git push origin gsd/v0.7.1-bug-fix-round`
```
To https://github.com/YuSabo90002/typsphinx.git
   7bdaf40..1f24e24  gsd/v0.7.1-bug-fix-round -> gsd/v0.7.1-bug-fix-round
```

**Post-push effect:**

**Command:** `git ls-remote --heads origin | grep gsd/v0.7.1-bug-fix-round`
```
1f24e24973c21ac48c83f8e44ffe39cc5480921d	refs/heads/gsd/v0.7.1-bug-fix-round
```

The remote SHA now **equals** the local phase tip `1f24e24973c21ac48c83f8e44ffe39cc5480921d`.
This tip carries all four requirements' changes: TBL-04 (plan 43-01), FIG-01 (plan 43-03), TBL-05
and QUA-01 (plan 43-04) — verified by `git merge-base --is-ancestor` checks recorded in
`43-GATE-EVIDENCE-05.md` § 2 for the TBL-04/TBL-05 boundary, and by plan 43-03's own SUMMARY
recording its fix commit as an ancestor of plan 43-04's fork point (`43-03-SUMMARY.md`'s
self-check: `de01892^` confirmed `829b807`, itself a descendant of plan 43-03's fix commit
`50a3ed6`). This is the tip that carries all four requirements' changes — the wave-1 push in plan
43-02 carried only the phase's starting point (`7bdaf40`, identical to the phase's pre-fix RED
commit's tree for `typsphinx/`).

---

## 2. Triggered CI — polling record (including in-progress attempts)

**Command:** `gh run list --branch gsd/v0.7.1-bug-fix-round --limit 10` (immediately after the
push, before any dispatch)
```
in_progress		docs(phase-43): update tracking after wave 3	Link Check	gsd/v0.7.1-bug-fix-round	push	30868248789	5s	2026-08-04T01:16:35Z
completed	success	CI	CI	gsd/v0.7.1-bug-fix-round	workflow_dispatch	30863882894	4m25s	2026-08-03T23:55:14Z
completed	success	docs(43): add pattern map	Link Check	gsd/v0.7.1-bug-fix-round	push	30863834569	21s	2026-08-03T23:54:22Z
```

Only `links.yml` ("Link Check") registered from the push event (run `30868248789`) — confirming
§ 0's diagnosis directly, a second time, against this phase's own push. `30863882894` is plan
43-02's wave-1 `workflow_dispatch` run, already `completed`/`success` (the BASELINE run,
`headSha` = `7bdaf40`, not the tip carrying all four requirements — not this task's evidence).

**Manual dispatch of `ci.yml` against the pushed tip:**

**Command:** `gh workflow run ci.yml --ref gsd/v0.7.1-bug-fix-round`
```
https://github.com/YuSabo90002/typsphinx/actions/runs/30868259060
```

**Poll attempt 1** (~12s after dispatch) — **Command:** `gh run list --branch
gsd/v0.7.1-bug-fix-round --limit 10`
```
in_progress		CI	CI	gsd/v0.7.1-bug-fix-round	workflow_dispatch	30868259060	15s	2026-08-04T01:16:46Z
completed	success	docs(phase-43): update tracking after wave 3	Link Check	gsd/v0.7.1-bug-fix-round	push	30868248789	13s	2026-08-04T01:16:35Z
completed	success	CI	CI	gsd/v0.7.1-bug-fix-round	workflow_dispatch	30863882894	4m25s	2026-08-03T23:55:14Z
completed	success	docs(43): add pattern map	Link Check	gsd/v0.7.1-bug-fix-round	push	30863834569	21s	2026-08-03T23:54:22Z
```
**Triggered CI run: `30868259060`** (`CI` workflow, trigger `workflow_dispatch`), status
`in_progress`.

**Poll attempt 2** (immediately after dispatch registration, lane-list check) — **Command:**
`gh run view 30868259060`
```
* gsd/v0.7.1-bug-fix-round CI · 30868259060
Triggered via workflow_dispatch less than a minute ago

JOBS
* Lint and Format Check (ID 91864653633)
* Build Package (ID 91864653634)
* Code Coverage (ID 91864653645)
* Type Check (ID 91864653652)
✓ Integration Test - advanced in 11s (ID 91864653690)
✓ Integration Test - basic in 13s (ID 91864653695)
* Test Python 3.12 on ubuntu-latest (ID 91864653736)
* Test Python 3.12 on macos-latest (ID 91864653753)
* Test Python 3.12 on windows-latest (ID 91864653756)
* Test Python 3.13 on macos-latest (ID 91864653762)
* Test Python 3.13 on ubuntu-latest (ID 91864653767)
* Test Python 3.13 on windows-latest (ID 91864653782)
```
Full 12-job lane set already registered, matching `43-GATE-EVIDENCE-02.md` § 5's recorded set
exactly (6 `os × python-version` test lanes including both Windows lanes, `Lint and Format
Check`, `Type Check`, `Code Coverage`, `Build Package`, 2 `Integration Test` lanes). **Both
Windows lanes are present and explicitly named at this poll:**
- `Test Python 3.12 on windows-latest` (ID 91864653756)
- `Test Python 3.13 on windows-latest` (ID 91864653782)

**Poll attempt 3** (~54s elapsed) — **Command:** `gh run list --branch gsd/v0.7.1-bug-fix-round
--limit 5`
```
in_progress		CI	CI	gsd/v0.7.1-bug-fix-round	workflow_dispatch	30868259060	54s	2026-08-04T01:16:46Z
completed	success	docs(phase-43): update tracking after wave 3	Link Check	gsd/v0.7.1-bug-fix-round	push	30868248789	13s	2026-08-04T01:16:35Z
completed	success	CI	CI	gsd/v0.7.1-bug-fix-round	workflow_dispatch	30863882894	4m25s	2026-08-03T23:55:14Z
completed	success	docs(43): add pattern map	Link Check	gsd/v0.7.1-bug-fix-round	push	30863834569	21s	2026-08-03T23:54:22Z
```
Still `in_progress`.

**Poll attempt 4** (~1m1s elapsed) — **Command:** `gh run list --branch gsd/v0.7.1-bug-fix-round
--limit 5`
```
in_progress		CI	CI	gsd/v0.7.1-bug-fix-round	workflow_dispatch	30868259060	1m1s	2026-08-04T01:16:46Z
completed	success	docs(phase-43): update tracking after wave 3	Link Check	gsd/v0.7.1-bug-fix-round	push	30868248789	13s	2026-08-04T01:16:35Z
completed	success	CI	CI	gsd/v0.7.1-bug-fix-round	workflow_dispatch	30863882894	4m25s	2026-08-03T23:55:14Z
completed	success	docs(43): add pattern map	Link Check	gsd/v0.7.1-bug-fix-round	push	30863834569	21s	2026-08-03T23:54:22Z
```
Still `in_progress`. A background watcher (`gh run watch 30868259060 --interval 20`) and a
blocking poll loop (`until gh run view 30868259060 --json status -q .status | grep -q completed;
do sleep 15; done`) were started at this point and observed the run progress through the
per-step job logs (steps `Set up job` / `Run actions/checkout@v7` / `Install uv` / `Set up
Python` / `Install dependencies` completing, `Run tests with tox` in progress) for each of the
Windows/macOS/Ubuntu lanes before the run reached its terminal state.

**Poll attempt 5 — terminal state** (~5 minutes elapsed) — **Command:** `gh run view 30868259060
--json status,conclusion,headSha,headBranch,event,createdAt,updatedAt`
```json
{"conclusion":"success","createdAt":"2026-08-04T01:16:46Z","event":"workflow_dispatch","headBranch":"gsd/v0.7.1-bug-fix-round","headSha":"1f24e24973c21ac48c83f8e44ffe39cc5480921d","status":"completed","updatedAt":"2026-08-04T01:21:45Z"}
```

**Run `30868259060`'s status is `completed`, conclusion `success`, `headSha` equals
`1f24e24973c21ac48c83f8e44ffe39cc5480921d` exactly** — the tip pushed in § 1, carrying all four
requirements' changes. This is a COMPLETED run, not an in-progress one; SC#5's second half is
satisfied by this specific poll, not any earlier in-progress one.

---

## 3. Every lane's conclusion, named, cross-checked against `43-GATE-EVIDENCE-02.md`

**Command:** `gh run view 30868259060`
```
✓ gsd/v0.7.1-bug-fix-round CI · 30868259060
Triggered via workflow_dispatch about 5 minutes ago

JOBS
✓ Lint and Format Check in 20s (ID 91864653633)
✓ Build Package in 15s (ID 91864653634)
✓ Code Coverage in 2m47s (ID 91864653645)
✓ Type Check in 18s (ID 91864653652)
✓ Integration Test - advanced in 11s (ID 91864653690)
✓ Integration Test - basic in 13s (ID 91864653695)
✓ Test Python 3.12 on ubuntu-latest in 2m41s (ID 91864653736)
✓ Test Python 3.12 on macos-latest in 3m19s (ID 91864653753)
✓ Test Python 3.12 on windows-latest in 4m53s (ID 91864653756)
✓ Test Python 3.13 on macos-latest in 3m26s (ID 91864653762)
✓ Test Python 3.13 on ubuntu-latest in 2m53s (ID 91864653767)
✓ Test Python 3.13 on windows-latest in 4m10s (ID 91864653782)

ANNOTATIONS
! Unexpected input(s) 'file', valid inputs are [...]
Code Coverage: .github#1

! No files were found with the provided path: .pytest_cache
test-results/. No artifacts will be uploaded.
Test Python 3.12 on ubuntu-latest: .github#18
[... same "no artifacts" annotation repeated for macos/windows/ubuntu x2/3.12/3.13 lanes ...]

ARTIFACTS
coverage-report
dist
example-basic-output
example-advanced-output
```

**Command (per-job JSON, authoritative status/conclusion for every lane):** `gh run view
30868259060 --json jobs -q '.jobs[] | "\(.name)\t\(.status)\t\(.conclusion)"'`
```
Lint and Format Check	completed	success
Build Package	completed	success
Code Coverage	completed	success
Type Check	completed	success
Integration Test - advanced	completed	success
Integration Test - basic	completed	success
Test Python 3.12 on ubuntu-latest	completed	success
Test Python 3.12 on macos-latest	completed	success
Test Python 3.12 on windows-latest	completed	success
Test Python 3.13 on macos-latest	completed	success
Test Python 3.13 on ubuntu-latest	completed	success
Test Python 3.13 on windows-latest	completed	success
```

**Both Windows lanes named explicitly, both `success`:**
- **`Test Python 3.12 on windows-latest`** (ID 91864653756) — `completed` / **`success`** — 4m53s
- **`Test Python 3.13 on windows-latest`** (ID 91864653782) — `completed` / **`success`** — 4m10s

**Cross-check against `43-GATE-EVIDENCE-02.md` § 5's recorded lane set** (12 jobs: 6
`os × python-version` test lanes incl. both Windows lanes, `Lint and Format Check`, `Type Check`,
`Code Coverage`, `Build Package`, 2 `Integration Test` lanes `basic`/`advanced`): **the lane sets
are identical** — same 12 job names, same `strategy.matrix` (`os: [ubuntu-latest, windows-latest,
macos-latest]`, `python-version: ['3.12', '3.13']`), same two `Integration Test - {basic,
advanced}` lanes. No lane present in the wave-1 baseline run is missing here, and no lane here is
narrower than that recorded set.

**Annotations are non-blocking, pre-existing, unrelated to this phase's code.** The Codecov
action's `file:` input warning and the `.pytest_cache`/`test-results/` upload-artifact "no files
found" warnings are configuration-shape notices on already-`success`-concluded steps (`Upload
test results` completed successfully; the referenced paths simply don't exist because this
project's pytest run doesn't populate `.pytest_cache` under that exact working directory in CI —
a pre-existing `ci.yml` characteristic, not something this phase's `translator.py` change could
affect). No lane's `conclusion` is anything other than `success`.

**No failing lane exists.** § 4 of this file (fetch failing-lane logs) is therefore empty by
construction — there is nothing to fetch.

---

## 4. Failing-lane logs

Not applicable — every one of the 12 lanes concluded `success` (§ 3). No `gh run view
30868259060 --log-failed` was needed.

---

## 5. Phase 44 handoff — per planner decision D-P2

**D-P2** (carried from plan 43-02, restated in `43-05-PLAN.md`'s `<planner_decisions>`): a RED
Windows lane BLOCKS handoff to Phase 44, so the v0.7.0 failure (Windows lanes never running
against the milestone branch) cannot recur one phase later.

**Both Windows lanes concluded `success`** (§ 3):
- `Test Python 3.12 on windows-latest` — `success`
- `Test Python 3.13 on windows-latest` — `success`

**Verdict: Phase 44 handoff is CLEAR.**

Supporting evidence: run `30868259060`, `status: completed`, `conclusion: success`, run against
`headSha: 1f24e24973c21ac48c83f8e44ffe39cc5480921d` (the tip carrying all four of this phase's
requirements' changes — TBL-04, FIG-01, TBL-05, QUA-01), all 12 lanes `success`, including both
named Windows lanes above. No todo file was filed under `.planning/todos/pending/` for this
handoff, since D-P2's blocking condition (a RED Windows lane) did not occur.

The premise correction recorded in § 0 — that `ci.yml` never fires from a plain push to a
non-`main`/`develop` branch, and `workflow_dispatch` must be invoked explicitly — is also part of
this handoff record: any phase after Phase 44 that intends to rely on CI running automatically
against `gsd/v0.7.1-bug-fix-round` (or any future milestone branch) from a push alone will observe
the same silent non-trigger unless it also dispatches `ci.yml` explicitly, or `ci.yml`'s
`on.push.branches` list is widened in a future phase (out of this plan's scope).

---

## 6. Working-tree state

**Command:** `git status --porcelain typsphinx/ tests/ .github/ pyproject.toml uv.lock`
```
(no output)
```

Empty — no file outside `.planning/` (specifically, only this task's own
`43-GATE-EVIDENCE-06.md`) was modified by this task. `.github/workflows/ci.yml` was read, never
edited, per this plan's explicit scope discipline.

---

## 7. Six roadmap Success Criteria mapped to their evidence

| SC | Statement | Discharged by | Status |
|----|-----------|----------------|--------|
| SC#1 | TBL-04: a table nested inside another table's cell no longer clobbers the enclosing table's cells, column count, column widths and caption | `43-GATE-EVIDENCE-01.md` | Met |
| SC#2 | FIG-01: a figure nested inside another figure keeps the outer figure's caption, ids and state; the inner figure renders inside the legend | `43-GATE-EVIDENCE-04.md` §"D5" cross-references `43-GATE-EVIDENCE-03.md` as FIG-01's own RED-to-GREEN record; primary evidence is `43-GATE-EVIDENCE-03.md` | Met |
| SC#3 | TBL-05: a captioned table whose title renders to the empty string still anchors its ids | `43-GATE-EVIDENCE-04.md` | Met |
| SC#4 | Byte-invariance: every document with no nested table, no nested figure and no empty-titled caption emits byte-identical `.typ` across the phase's whole change, proven by the two-build method with isolation proof and positive control | `43-GATE-EVIDENCE-05.md` (this plan, Task 1) — partial coverage also recorded per-plan in `43-GATE-EVIDENCE-01.md` (TBL-04's own three-fixture sweep) and `43-GATE-EVIDENCE-03.md` (FIG-01's image-only control) | Met |
| SC#5 | The milestone branch reaches `origin` and a COMPLETED CI run, including both Windows lanes, runs against it during this phase | First half (pushed during the phase): `43-GATE-EVIDENCE-02.md`. Second half (completed run, all lanes named): **this file** (`43-GATE-EVIDENCE-06.md`) | Met |
| SC#6 | QUA-01: `_emit_id_anchors`'s docstring no longer calls `depart_figure` the sole `skip_ids` user | `43-GATE-EVIDENCE-04.md` | Met |

No criterion has a blank row. Every one of the six roadmap Success Criteria for Phase 43 is now
discharged with a named evidence file and section.

---

## 8. Verdict

| Success criterion | Discharged by | Status |
|--------------------|----------------|--------|
| SC#5 (second half) — a COMPLETED GitHub Actions run exists against `gsd/v0.7.1-bug-fix-round` at a tip carrying all four requirements' changes, with every Windows lane's conclusion recorded by name | § 1 (push + post-push `ls-remote` match), § 2 (poll record culminating in a `completed`/`success` run against the exact pushed `headSha`), § 3 (all 12 lanes named, both Windows lanes `success`, cross-checked against `43-GATE-EVIDENCE-02.md`'s lane set) | **MET** |
| Phase 44 handoff (D-P2) | § 5 — CLEAR, both Windows lanes green | **CLEAR** |
