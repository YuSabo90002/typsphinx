# 43-GATE-EVIDENCE-06.md — SC#5 Completed-CI Evidence and Phase 44 Handoff

**Phase:** 43 (Table State Correctness — Nested Tables + Empty-Title Anchors)
**Wave:** 4 (this refresh executed post-gap-closure, plan 43-06 having landed)
**Plan:** 43-05, Task 2 — **REGENERATED** against the current phase tip after `43-REVIEW.md`
CR-01 was fixed by gap-closure plan 43-06
**Executed:** 2026-08-04 (worktree agent, isolated worktree
`worktree-agent-a3ec4f2e4269654fa`)

Discharges the second half of roadmap SC#5: a COMPLETED GitHub Actions run against
`gsd/v0.7.1-bug-fix-round` at a tip that contains all four requirements' changes (TBL-04, FIG-01,
TBL-05, QUA-01) **and the CR-01 gap-closure fix**, with every Windows lane's conclusion recorded
by name, cross-checked against the lane set independently recorded at the wave-1 push in
`43-GATE-EVIDENCE-02.md`. Every command below was executed in THIS session, in this worktree.

## 0. Why this file supersedes the prior run, and the CI-trigger premise correction

**Supersession.** The previous version of this file (worktree `worktree-agent-aa3956ec1949a9fc1`)
recorded a COMPLETED run (`30868259060`) against `headSha 1f24e24973c21ac48c83f8e44ffe39cc5480921d`
— the phase tip immediately after plan 43-04. Phase 43's own code review (`43-REVIEW.md`) then
found CR-01, a BLOCKER in `visit_legend`/`depart_legend`, which gap-closure plan 43-06 fixed
(`typsphinx/translator.py` changed again, commit `4ea64006cb930bf1362a61dfa9052811f79617a6`,
merged to the milestone branch as `1a3b3c85ea4dbbdefade23ef43f0a9e758a93e52`). The prior run's
`headSha` therefore no longer carries the phase's full, correct diff — it predates the CR-01 fix.
This file re-pushes the true current tip and re-runs the completed-CI proof against it from
scratch.

**The premise correction, independently re-confirmed in this session.** Both this plan and the
roadmap assumed a `git push` of the milestone branch triggers the CI matrix. **It does not.**
Read directly from `.github/workflows/ci.yml` in this session:

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
plain push, confirmed directly in § 2 below, a third independent time (43-02's wave-1 push, the
prior 43-05 run, and now this refresh all observe the identical structural non-trigger). `ci.yml`
already declares `workflow_dispatch:` as a pre-existing, unmodified trigger, so this task uses
that mechanism explicitly (`gh workflow run ci.yml --ref gsd/v0.7.1-bug-fix-round`). **No file was
modified** — `.github/workflows/ci.yml`'s content is unchanged by this plan (confirmed, § 6).

---

## 1. Push the finished phase tip

**Pre-push baseline:**

**Command:** `git log -1 --oneline gsd/v0.7.1-bug-fix-round`
```
1a3b3c8 chore: merge executor worktree (worktree-agent-afa741a07b43df548)
```

**Command:** `git ls-remote --heads origin gsd/v0.7.1-bug-fix-round`
```
1f24e24973c21ac48c83f8e44ffe39cc5480921d	refs/heads/gsd/v0.7.1-bug-fix-round
```

The remote was still at `1f24e24` — the tip carried by the *prior* 43-05 evidence run, which
predates plan 43-06's CR-01 fix entirely (43-06's own commits — `4250e35`, `4ea6400`, `d4b5198`,
plus the phase's tracking/merge commits through `1a3b3c8` — had not yet reached `origin`).

**Command:** `git push origin gsd/v0.7.1-bug-fix-round`
```
To https://github.com/YuSabo90002/typsphinx.git
   1f24e24..1a3b3c8  gsd/v0.7.1-bug-fix-round -> gsd/v0.7.1-bug-fix-round
```

**Post-push effect:**

**Command:** `git ls-remote --heads origin gsd/v0.7.1-bug-fix-round`
```
1a3b3c85ea4dbbdefade23ef43f0a9e758a93e52	refs/heads/gsd/v0.7.1-bug-fix-round
```

The remote SHA now **equals** the local phase tip `1a3b3c85ea4dbbdefade23ef43f0a9e758a93e52`. This
tip carries all four requirements' changes (TBL-04, FIG-01, TBL-05, QUA-01 — themselves ancestors
of `4ea6400`, per `43-GATE-EVIDENCE-05.md` § 2's fresh ancestry check) **and** the CR-01
gap-closure fix (`4ea6400` itself is an ancestor of `1a3b3c8` — confirmed directly:
`git merge-base --is-ancestor 4ea64006cb930bf1362a61dfa9052811f79617a6
1a3b3c85ea4dbbdefade23ef43f0a9e758a93e52` exits `0`). This is the tip carrying the phase's
complete, reviewed, gap-closed diff — the prior 43-05 run's push (`1f24e24`) carried only the
pre-review state.

**Command:** `git merge-base --is-ancestor 4ea64006cb930bf1362a61dfa9052811f79617a6
1a3b3c85ea4dbbdefade23ef43f0a9e758a93e52 && echo "ANCESTOR: yes"`
```
ANCESTOR: yes
```

---

## 2. Triggered CI — polling record

**Command:** `gh run list --branch gsd/v0.7.1-bug-fix-round --limit 10` (immediately after the
push, before any dispatch)
```
in_progress		chore: merge executor worktree (worktree-agent-afa741a07b43df548)	Link Check	gsd/v0.7.1-bug-fix-round	push	30870535016	7s	2026-08-04T02:01:32Z
completed	success	CI	CI	gsd/v0.7.1-bug-fix-round	workflow_dispatch	30868259060	4m59s	2026-08-04T01:16:46Z
completed	success	docs(phase-43): update tracking after wave 3	Link Check	gsd/v0.7.1-bug-fix-round	push	30868248789	13s	2026-08-04T01:16:35Z
completed	success	CI	CI	gsd/v0.7.1-bug-fix-round	workflow_dispatch	30863882894	4m25s	2026-08-03T23:55:14Z
completed	success	docs(43): add pattern map	Link Check	gsd/v0.7.1-bug-fix-round	push	30863834569	21s	2026-08-03T23:54:22Z
```

Only `links.yml` ("Link Check") registered from the push event (run `30870535016`) — confirming
§ 0's diagnosis directly, a third time, against this refresh's own push. `30868259060` is the
PRIOR (now-superseded) 43-05 evidence run, already `completed`/`success` against the OLD tip
`1f24e24` — not this file's evidence.

**Manual dispatch of `ci.yml` against the newly pushed tip:**

**Command:** `gh workflow run ci.yml --ref gsd/v0.7.1-bug-fix-round`
```
https://github.com/YuSabo90002/typsphinx/actions/runs/30870536482
```

**Poll attempt 1** (immediately after dispatch registration) — **Command:** `gh run list --branch
gsd/v0.7.1-bug-fix-round --limit 10`
```
queued		CI	CI	gsd/v0.7.1-bug-fix-round	workflow_dispatch	30870536482	5s	2026-08-04T02:01:34Z
in_progress		chore: merge executor worktree (worktree-agent-afa741a07b43df548)	Link Check	gsd/v0.7.1-bug-fix-round	push	30870535016	7s	2026-08-04T02:01:32Z
completed	success	CI	CI	gsd/v0.7.1-bug-fix-round	workflow_dispatch	30868259060	4m59s	2026-08-04T01:16:46Z
completed	success	docs(phase-43): update tracking after wave 3	Link Check	gsd/v0.7.1-bug-fix-round	push	30868248789	13s	2026-08-04T01:16:35Z
completed	success	CI	CI	gsd/v0.7.1-bug-fix-round	workflow_dispatch	30863882894	4m25s	2026-08-03T23:55:14Z
completed	success	docs(43): add pattern map	Link Check	gsd/v0.7.1-bug-fix-round	push	30863834569	21s	2026-08-03T23:54:22Z
```
**Triggered CI run: `30870536482`** (`CI` workflow, trigger `workflow_dispatch`), status
`queued` at this poll — registered, not yet running.

Between poll attempt 1 and the next check, the full `43-GATE-EVIDENCE-05.md` two-build
byte-invariance work (§§ 1-8 of that file: two `git archive` exports, two independent `uv sync`
provisions, the NixOS `uv` shim, the isolation proof, six corpus builds plus the positive control,
the production-diff isolation, and the milestone-invariant checks) was carried out end to end in
this same session while the run progressed in the background, per this plan's explicit
"dispatch-then-work-then-poll" ordering.

**Poll attempt 2 — terminal state** (~4m17s elapsed by the run's own recorded duration) —
**Command:** `gh run list --branch gsd/v0.7.1-bug-fix-round --limit 5`
```
completed	success	CI	CI	gsd/v0.7.1-bug-fix-round	workflow_dispatch	30870536482	4m17s	2026-08-04T02:01:34Z
completed	success	chore: merge executor worktree (worktree-agent-afa741a07b43df548)	Link Check	gsd/v0.7.1-bug-fix-round	push	30870535016	10s	2026-08-04T02:01:32Z
completed	success	CI	CI	gsd/v0.7.1-bug-fix-round	workflow_dispatch	30868259060	4m59s	2026-08-04T01:16:46Z
completed	success	docs(phase-43): update tracking after wave 3	Link Check	gsd/v0.7.1-bug-fix-round	push	30868248789	13s	2026-08-04T01:16:35Z
completed	success	CI	CI	gsd/v0.7.1-bug-fix-round	workflow_dispatch	30863882894	4m25s	2026-08-03T23:55:14Z
```
Run `30870536482` is now `completed` / `success`.

**Command:** `gh run view 30870536482 --json status,conclusion,headSha,headBranch,event,createdAt,updatedAt`
```json
{"conclusion":"success","createdAt":"2026-08-04T02:01:34Z","event":"workflow_dispatch","headBranch":"gsd/v0.7.1-bug-fix-round","headSha":"1a3b3c85ea4dbbdefade23ef43f0a9e758a93e52","status":"completed","updatedAt":"2026-08-04T02:05:51Z"}
```

**Run `30870536482`'s status is `completed`, conclusion `success`, `headSha` equals
`1a3b3c85ea4dbbdefade23ef43f0a9e758a93e52` exactly** — the tip pushed in § 1, carrying all four
requirements' changes AND the CR-01 gap-closure fix. This is a COMPLETED run, not an in-progress
one; this poll (poll attempt 2), not the earlier `queued` one, is what discharges SC#5's second
half for this refreshed evidence.

---

## 3. Every lane's conclusion, named, cross-checked against `43-GATE-EVIDENCE-02.md`

**Command:** `gh run view 30870536482`
```
✓ gsd/v0.7.1-bug-fix-round CI · 30870536482
Triggered via workflow_dispatch about 4 minutes ago

JOBS
✓ Build Package in 17s (ID 91871455415)
✓ Lint and Format Check in 15s (ID 91871455431)
✓ Type Check in 18s (ID 91871455432)
✓ Code Coverage in 2m48s (ID 91871455442)
✓ Integration Test - advanced in 14s (ID 91871455452)
✓ Test Python 3.12 on ubuntu-latest in 2m38s (ID 91871455477)
✓ Test Python 3.13 on macos-latest in 2m31s (ID 91871455487)
✓ Test Python 3.13 on ubuntu-latest in 2m13s (ID 91871455490)
✓ Integration Test - basic in 12s (ID 91871455492)
✓ Test Python 3.12 on macos-latest in 3m27s (ID 91871455496)
✓ Test Python 3.12 on windows-latest in 4m13s (ID 91871455518)
✓ Test Python 3.13 on windows-latest in 4m12s (ID 91871455556)

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
30870536482 --json jobs -q '.jobs[] | "\(.name)\t\(.status)\t\(.conclusion)"'`
```
Build Package	completed	success
Lint and Format Check	completed	success
Type Check	completed	success
Code Coverage	completed	success
Integration Test - advanced	completed	success
Test Python 3.12 on ubuntu-latest	completed	success
Test Python 3.13 on macos-latest	completed	success
Test Python 3.13 on ubuntu-latest	completed	success
Integration Test - basic	completed	success
Test Python 3.12 on macos-latest	completed	success
Test Python 3.12 on windows-latest	completed	success
Test Python 3.13 on windows-latest	completed	success
```

**Both Windows lanes named explicitly, both `success`:**
- **`Test Python 3.12 on windows-latest`** (ID 91871455518) — `completed` / **`success`** — 4m13s
- **`Test Python 3.13 on windows-latest`** (ID 91871455556) — `completed` / **`success`** — 4m12s

**Cross-check against `43-GATE-EVIDENCE-02.md` § 5's recorded lane set** (12 jobs: 6
`os × python-version` test lanes incl. both Windows lanes, `Lint and Format Check`, `Type Check`,
`Code Coverage`, `Build Package`, 2 `Integration Test` lanes `basic`/`advanced`): **the lane sets
are identical** — same 12 job names (verified by name-for-name comparison, order differs but the
set does not), same `strategy.matrix` (`os: [ubuntu-latest, windows-latest, macos-latest]`,
`python-version: ['3.12', '3.13']`), same two `Integration Test - {basic, advanced}` lanes. No
lane present in the wave-1 baseline run is missing here, and no lane here is narrower than that
recorded set. This is also identical to the lane set the prior (now-superseded) 43-05 run recorded
for `30868259060` — the lane composition has not changed across any of the three runs this
milestone has triggered.

**Annotations are non-blocking, pre-existing, unrelated to this phase's code.** The Codecov
action's `file:` input warning and the `.pytest_cache`/`test-results/` upload-artifact "no files
found" warnings are configuration-shape notices on already-`success`-concluded steps. No lane's
`conclusion` is anything other than `success`.

**No failing lane exists.** § 4 of this file (fetch failing-lane logs) is therefore empty by
construction — there is nothing to fetch.

---

## 4. Failing-lane logs

Not applicable — every one of the 12 lanes concluded `success` (§ 3). No `gh run view
30870536482 --log-failed` was needed.

---

## 5. Phase 44 handoff — per planner decision D-P2

**D-P2** (carried from plan 43-02, restated in `43-05-PLAN.md`'s `<planner_decisions>`): a RED
Windows lane BLOCKS handoff to Phase 44, so the v0.7.0 failure (Windows lanes never running
against the milestone branch) cannot recur one phase later.

**Both Windows lanes concluded `success`** (§ 3):
- `Test Python 3.12 on windows-latest` — `success`
- `Test Python 3.13 on windows-latest` — `success`

**Verdict: Phase 44 handoff is CLEAR.**

Supporting evidence: run `30870536482`, `status: completed`, `conclusion: success`, run against
`headSha: 1a3b3c85ea4dbbdefade23ef43f0a9e758a93e52` (the tip carrying all four of this phase's
requirements' changes — TBL-04, FIG-01, TBL-05, QUA-01 — **plus the CR-01 gap-closure fix from
plan 43-06**, the phase's own code-review BLOCKER), all 12 lanes `success`, including both named
Windows lanes above. No todo file was filed under `.planning/todos/pending/` for this handoff,
since D-P2's blocking condition (a RED Windows lane) did not occur.

**This handoff verdict is unchanged from the superseded evidence (also CLEAR), but is now backed
by a run against the phase's TRUE final tip** — including CR-01's fix — rather than the pre-review
tip the superseded run measured. Phase 44 inherits a translator that has already passed its own
phase's code review, not merely its own phase's plan-time gates.

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
`43-GATE-EVIDENCE-06.md` and, in the sibling task, `43-GATE-EVIDENCE-05.md`) was modified by this
plan. `.github/workflows/ci.yml` was read, never edited, per this plan's explicit scope
discipline.

---

## 7. Six roadmap Success Criteria mapped to their evidence

| SC | Statement | Discharged by | Status |
|----|-----------|----------------|--------|
| SC#1 | TBL-04: a table nested inside another table's cell no longer clobbers the enclosing table's cells, column count, column widths and caption | `43-GATE-EVIDENCE-01.md` | Met |
| SC#2 | TBL-05: a captioned table whose title renders to an empty or whitespace-only string emits its id anchors | `43-GATE-EVIDENCE-04.md` | Met |
| SC#3 | QUA-01: `_emit_id_anchors`'s docstring names its actual callers, verified by a repo-wide grep for its call sites | `43-GATE-EVIDENCE-04.md` | Met |
| SC#4 | Byte-invariance: every document with no nested table, no nested figure and no empty-titled caption emits byte-identical `.typ` across the phase's whole change (including the CR-01 gap closure), proven by the two-build method with isolation proof and positive control | `43-GATE-EVIDENCE-05.md` (this plan, Task 1, regenerated against the CR-01-fixed tip) — partial coverage also recorded per-plan in `43-GATE-EVIDENCE-01.md` (TBL-04's own three-fixture sweep) and `43-GATE-EVIDENCE-03.md` (FIG-01's image-only control) | Met |
| SC#5 | The milestone branch reaches `origin` and a COMPLETED CI run, including both Windows lanes, runs against it during this phase | First half (pushed during the phase): `43-GATE-EVIDENCE-02.md`. Second half (completed run against the phase's TRUE final tip, all lanes named): **this file** (`43-GATE-EVIDENCE-06.md`, regenerated) | Met |
| SC#6 | FIG-01: a figure nested inside another figure's legend keeps the outer figure's caption, ids and state; the inner figure renders inside the legend | Primary evidence `43-GATE-EVIDENCE-03.md` (FIG-01's own RED-to-GREEN record, cross-referenced from `43-GATE-EVIDENCE-04.md` §"D5"), with the CR-01 legend-in-legend gap closed by `43-GATE-EVIDENCE-07.md` (plan 43-06) | Met |

> **Numbering correction (orchestrator, post-verification).** An earlier revision of this table
> attached the wrong SC numbers to three rows — it mapped SC#2→FIG-01, SC#3→TBL-05 and SC#6→QUA-01.
> `.planning/ROADMAP.md` § Phase 43 is authoritative: SC#2 is TBL-05, SC#3 is QUA-01, and SC#6 is
> FIG-01 (appended by owner decision during phase discussion, hence last). Only the labels were
> wrong — every row already pointed at the correct evidence file, and every plan file and every
> other evidence file used the correct numbering. Corrected here so the mapping is safe to rely on
> at milestone close.

No criterion has a blank row. Every one of the six roadmap Success Criteria for Phase 43 is now
discharged with a named evidence file and section, against the phase's actual final tip (i.e.
including CR-01's fix, not merely the pre-review state).

---

## 8. Verdict

| Success criterion | Discharged by | Status |
|--------------------|----------------|--------|
| SC#5 (second half) — a COMPLETED GitHub Actions run exists against `gsd/v0.7.1-bug-fix-round` at a tip carrying all four requirements' changes AND the CR-01 gap-closure fix, with every Windows lane's conclusion recorded by name | § 1 (push + post-push `ls-remote` match + ancestry proof that CR-01's fix commit is an ancestor of the pushed tip), § 2 (poll record culminating in a `completed`/`success` run against the exact pushed `headSha`), § 3 (all 12 lanes named, both Windows lanes `success`, cross-checked against `43-GATE-EVIDENCE-02.md`'s lane set) | **MET** |
| Phase 44 handoff (D-P2) | § 5 — CLEAR, both Windows lanes green, now against the phase's true final tip | **CLEAR** |
