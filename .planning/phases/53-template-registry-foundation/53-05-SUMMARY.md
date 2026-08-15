---
phase: 53-template-registry-foundation
plan: 05
subsystem: testing
tags: [sphinx, typst, typst-py, pypdf, evidence, byte-identity, ci, github-actions]

# Dependency graph
requires:
  - phase: 53-01
    provides: "53-RED-EVIDENCE.md's pre-change SHA-256/page-count baseline for the four configuration shapes plus the TPL-04 equivalence baseline"
  - phase: 53-02
    provides: "the registry plumbing (typsphinx/template_registry.py, write() resolution, render_wrapper() threading) that Task 1 measures post-change output against"
  - phase: 53-03
    provides: "CONF-14..18 validation, cited in the SC#3/SC#4 audit verdicts"
  - phase: 53-04
    provides: "TemplateResolution.path, cited in the SC#1 audit verdict's requirements-completed cross-reference"
provides:
  - "53-RED-EVIDENCE.md: complete post-change section diffing every emitted .typ SHA-256 and PDF page count against the pre-change baseline across all four configuration shapes, plus the post-change TPL-04 comparison -- all MATCH"
  - "53-CI-EVIDENCE.md: gsd/v0.9.0-per-document-templates pushed to origin; a full, honest two-run CI history (Run 1 failed on a pre-existing cross-platform defect unrelated to Phase 53, Run 2 succeeded on all 12 jobs after an owner-authorized fix); an Audit section verifying all five Phase 53 success criteria against ROADMAP.md's literal wording"
  - "SC#2 and SC#5 closed on measured evidence"
affects: ["Phase 54 (bundle copy phase, inherits a green tree and a landed milestone branch)"]

# Actuals (#2632)
actuals:
  tokens: 6367
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "one-off evidence artifact (D-12): measure-then-record post-change section, diffed against the recorded pre-change section, no new pytest gate"
    - "honest two-run CI evidence: record a failed dispatch and its unrelated root cause rather than only the eventual green run"

key-files:
  created: []
  modified:
    - .planning/phases/53-template-registry-foundation/53-RED-EVIDENCE.md
    - .planning/phases/53-template-registry-foundation/53-CI-EVIDENCE.md

key-decisions:
  - "The first CI dispatch (run 31875380355, head 9172aa1c) failed on all six test job legs -- not from any Phase 53 code, but from a pre-existing, cross-platform-identical defect in tests/test_state_guard_shapes_gate.py (a hardcoded path the v0.8.0 milestone archival had relocated, already logged out-of-scope by plan 53-01). Rather than treat this as this plan's own failure to fix, it was escalated to the orchestrator/owner, who authorized commit d1eff100 (outside this plan's declared files_modified scope) to fix the locator. A second dispatch (run 31875707734, head d1eff100) then closed SC#5 with all 12 jobs green."
  - "53-CI-EVIDENCE.md records both runs, not only the passing one -- the plan's own must_haves prohibit reconstructing or omitting measured evidence, and the failed-then-fixed sequence is the real, more useful history."
  - "The audit re-measured grep -rl \"_template\\.typ\" tests/ | wc -l, uv run pytest tests/ -q, and uv run pytest tests/test_preview_version_sync.py -q directly rather than trusting earlier plans' SUMMARYs, per the plan's own Task 3 instruction."

requirements-completed: [TPL-03, TPL-04]

coverage:
  - id: D1
    description: "Post-change byte-identity measurement across all four configuration shapes (typst_template set / typst_package set alone / typst_template_function set alone / nothing set), each diffed against the pre-change baseline with an explicit per-shape MATCH verdict, plus the post-change TPL-04 four-element-vs-fifth-element comparison (TPL-03, TPL-04, SC#2)"
    requirement: TPL-03
    verification:
      - kind: other
        ref: "53-RED-EVIDENCE.md § \"Post-change section\" -- measured via sphinx-build -b typstpdf against the same four real fixtures, sha256sum, pypdf.PdfReader; all four shapes and TPL-04 verdicts are MATCH"
        status: pass
    human_judgment: false
  - id: D2
    description: "gsd/v0.9.0-per-document-templates pushed to origin, evidenced by git ls-remote --heads origin, with the stale gsd/v0.9.0-milestone branch left untouched and no pull request opened (SC#5)"
    requirement: TPL-04
    verification:
      - kind: other
        ref: "53-CI-EVIDENCE.md § \"Branch push\" -- git ls-remote --heads origin hit, git branch --list / git rev-parse gsd/v0.9.0-milestone unchanged, gh pr list empty"
        status: pass
    human_judgment: false
  - id: D3
    description: "A completed workflow_dispatch CI run over the pushed branch with windows-latest and macos-latest test legs concluding success -- including the honest record of a first run that failed on an unrelated pre-existing defect (SC#5)"
    requirement: TPL-04
    verification:
      - kind: other
        ref: "53-CI-EVIDENCE.md § \"Run 1\" / \"Run 2\" -- gh run view 31875380355 (failure, 6/6 test legs failed, pre-existing defect) and gh run view 31875707734 (success, 12/12 jobs including both windows-latest and both macos-latest test legs), both independently re-measured via gh run view rather than transcribed"
        status: pass
    human_judgment: false
  - id: D4
    description: "Audit of both evidence artifacts against the literal text of all five Phase 53 success criteria, with re-measured standing invariants (regression-net file count, full suite, preview-version-sync)"
    verification:
      - kind: other
        ref: "53-CI-EVIDENCE.md § \"Audit\" -- grep -rl \"_template\\.typ\" tests/ | wc -l = 32 (unchanged); uv run pytest tests/ -q = 1232 passed / 5 skipped / 0 failed; uv run pytest tests/test_preview_version_sync.py -q = 3 passed; all five SC verdicts MET, each citing artifact and section"
        status: pass
    human_judgment: false

duration: ~40min
completed: 2026-08-15
status: complete
---

# Phase 53 Plan 05: SC#2/SC#5 Closing Evidence Summary

**Closed SC#2 (byte-identical output, all four shapes plus TPL-04, measured MATCH against the 53-01 pre-change baseline) and SC#5 (milestone branch pushed to `origin`, with an honestly-recorded first CI dispatch that failed on a pre-existing cross-platform defect unrelated to Phase 53, followed by an owner-authorized one-line-scope fix and a second dispatch that landed all 12 jobs green including both `windows-latest` and both `macos-latest` legs) — then audited both evidence artifacts against every Phase 53 success criterion's literal text.**

## Performance

- **Duration:** ~40 min (including ~14 min of CI run wall-clock time across the two dispatches)
- **Completed:** 2026-08-15T09:11:00Z
- **Tasks:** 3/3
- **Files modified:** 2 (`53-RED-EVIDENCE.md`, `53-CI-EVIDENCE.md`, both pre-existing artifacts extended, no new files)

## Accomplishments

- Re-verified the live `typst.compile()` real-PDF-compile path at the post-change commit, matching
  the pre-change probe's result with no divergence.
- Rebuilt all four existing configuration shapes (`typst_template` set / `typst_package` set alone
  / `typst_template_function` set alone / nothing set) against the same four real fixtures 53-01
  used, and diffed every emitted `.typ` file's SHA-256 and every compiled PDF's page count against
  53-01's recorded pre-change baseline — **every shape MATCH**, no file appeared or disappeared,
  no hash changed, no page count changed.
- Repeated the TPL-04 four-element-vs-fifth-element `"typst"` comparison at the post-change commit
  — byte-identical to itself and to the pre-change TPL-04 baseline.
- Pushed `gsd/v0.9.0-per-document-templates` to `origin` (single ref, no force, no PR opened,
  `gsd/v0.9.0-milestone` left untouched at its measured SHA).
- Dispatched CI, and when the first run (`31875380355`) failed on all six `test` job legs — a
  pre-existing, cross-platform-identical defect (`test_state_guard_shapes_gate.py`'s hardcoded
  path, already logged out-of-scope by plan 53-01) unrelated to Phase 53's own code — recorded
  that failure honestly rather than silently retrying, escalated it, and, after the owner
  authorized a fix (commit `d1eff100`, outside this plan's declared file scope), dispatched a
  second run (`31875707734`) that completed with conclusion `success` on all 12 jobs, including
  both `windows-latest` and both `macos-latest` `test` legs.
- Audited both evidence artifacts against ROADMAP.md's literal Phase 53 success-criteria text,
  re-measuring (not trusting) the standing invariants: the 32-file `_template.typ` regression net,
  the full test suite, and `test_preview_version_sync.py`. All five success criteria verdicts:
  MET.

## Task Commits

Each task was committed atomically:

1. **Task 1: Post-change byte-identity measurement across all four shapes, diffed against the baseline** - `9172aa1c` (docs)
2. **Task 2: Push the milestone branch and land a completed 3-OS CI run** - `80fe6b32` (docs)
3. **Task 3: Audit both evidence artifacts against the literal success criteria** - `a6398818` (docs)

_Executed on the main working tree (not an isolated worktree) per this plan's explicit
sequential-execution instructions, since SC#5's branch push and CI dispatch had to run from the
branch that CI actually measures. This SUMMARY's own metadata commit follows below; STATE.md /
ROADMAP.md updates are applied by this same execution (not deferred to an orchestrator merge)._

**Note on scope:** commit `d1eff100` ("fix(53): locate 49-SHAPES-RED-EVIDENCE.md across archived
milestones") is on the branch between this plan's Task 1 and Task 2 commits but is **not** part of
this plan's own deliverable — it was authored and pushed by the orchestrator, out of this plan's
declared `files_modified` scope (`53-RED-EVIDENCE.md`, `53-CI-EVIDENCE.md` only), after owner
authorization. `53-CI-EVIDENCE.md` documents it in full rather than treating it as this plan's own
work.

## Files Created/Modified

- `.planning/phases/53-template-registry-foundation/53-RED-EVIDENCE.md` - appended the post-change
  section: post-change commit SHA, live `typst.compile()` re-probe, all four shapes' `.typ`
  inventories with SHA-256 and PDF page counts plus per-shape MATCH verdicts, the post-change
  TPL-04 comparison, and an overall summary verdict.
- `.planning/phases/53-template-registry-foundation/53-CI-EVIDENCE.md` - new artifact (this plan's
  own): branch-push evidence, both CI runs' full `gh run view` transcripts (failure then success),
  the root-cause analysis and fix reference, and the Task 3 Audit section covering all five
  success criteria.

## Decisions Made

- **Recorded the failed CI run in full rather than only the eventual green one.** The plan's own
  `must_haves` prohibit reconstructing or omitting measured evidence; a single clean green run
  presented without its preceding failure would misrepresent what actually happened and would hide
  a real defect this phase's evidence-gathering surfaced.
- **Treated the `d1eff100` fix as out-of-scope work to document, not to claim.** It falls outside
  this plan's `files_modified` (`53-RED-EVIDENCE.md`, `53-CI-EVIDENCE.md` only) and was authored by
  the orchestrator after owner authorization — recorded verbatim in `53-CI-EVIDENCE.md` with its
  own commit hash and diff stat, distinguished clearly from this plan's own three task commits.
- **Independently re-measured every figure the orchestrator's escalation report cited** (`gh run
  view` for both run IDs' status/conclusion/headSha/jobs, `git ls-remote`, `gh pr list`, local
  `uv run pytest`) rather than transcribing the report — all figures matched exactly, and the
  artifact records the executor's own measurement commands and output.

## Deviations from Plan

### Auto-fixed Issues

None — no bug, missing-critical-functionality, or blocking issue was found in this plan's own
scope that required a Rule 1/2/3 fix. All four shapes and TPL-04 came back MATCH on the first
measurement; no divergence to investigate.

### Noted, Not Auto-fixed (out of scope, escalated instead)

**1. [Rule 4 — architectural/escalation, not auto-fixable within this plan's declared scope]
Pre-existing `test_state_guard_shapes_gate.py` failure blocked SC#5's own acceptance criteria**
- **Found during:** Task 2's CI dispatch (run `31875380355`).
- **Issue:** all six `test` job legs (ubuntu/windows/macos × Python 3.12/3.13) failed with the
  exact same 7-test baseline plans 53-01 through 53-04 had already logged as a pre-existing,
  out-of-scope defect (a hardcoded evidence-file path the v0.8.0 milestone archival relocated).
  Because it reproduced identically on all three OSes in a real CI environment (not just locally),
  it directly blocked SC#5's literal "windows-latest and macos-latest legs conclude success"
  requirement.
- **Why not auto-fixed here:** this plan's `files_modified` frontmatter names only the two
  evidence artifacts; the fix belongs to `tests/test_state_guard_shapes_gate.py`, a file outside
  this plan's declared scope, and touching it would have exceeded the plan's own boundary.
- **Action taken:** escalated to the orchestrator, who escalated to the project owner; the owner
  authorized the fix, which the orchestrator applied directly (commit `d1eff100`) and pushed to
  the same branch. This plan then dispatched a second CI run over the fixed commit and recorded
  both runs' full evidence.
- **Effect on this plan's stated acceptance criteria:** all of Task 2's and Task 3's acceptance
  criteria are met by the second run; the first run's failure and its cause are additionally
  documented in `53-CI-EVIDENCE.md` rather than omitted.

---

**Total deviations:** 0 auto-fixed; 1 escalated (Rule 4 — out of this plan's declared file scope,
resolved by owner-authorized action outside the plan, then fully documented).
**Impact on plan:** SC#5 closes cleanly on the second run's evidence. The escalation added CI
wall-clock time (~14 min across two dispatches) but no scope creep — this plan touched only its
two declared evidence artifacts.

## Issues Encountered

None beyond the escalated deviation above. `ruff check .` was not run locally (this plan changed
no `typsphinx/` or `tests/` source — lint/type coverage for the whole phase already comes from the
CI run per this plan's `key_links`, confirmed `success` in both the `Lint and Format Check` and
`Type Check` jobs of Run 2).

## User Setup Required

None beyond the plan's own precondition, which was already satisfied: `gh auth status` reported an
authenticated account (`YuSabo90002`) with push access to `origin` before Task 2 ran.

## Next Phase Readiness

SC#2 and SC#5 are both closed on measured evidence. `53-RED-EVIDENCE.md` now carries a complete
pre-change and post-change section with matching hashes across all four shapes plus TPL-04.
`53-CI-EVIDENCE.md` carries the full branch-push and two-run CI history plus a per-success-criterion
audit finding no shortfall. `gsd/v0.9.0-per-document-templates` is on `origin` at commit
`a6398818` (this plan's own final commit; the fix commit `d1eff100` sits between this plan's Task 1
and Task 2). Phase 54 inherits a green tree (1232 passed / 5 skipped / 0 failed locally, matching
the CI-confirmed state) and a landed, CI-proven milestone branch — no known gaps carried forward
from this plan.

The pre-existing `test_state_guard_shapes_gate.py` defect that plans 53-01/53-02/53-03/53-04 had
each logged and carried forward is now **resolved** (by `d1eff100`, not by this plan) — the local
full suite improved from the previously-carried 7-failed baseline to 0 failed. `WINDOWS.md`'s
corresponding entry should be closed by whichever process next reconciles that ledger; this plan
did not itself edit `WINDOWS.md` (out of its declared file scope) but records the resolution here
for that purpose.

---
*Phase: 53-template-registry-foundation*
*Completed: 2026-08-15*

## Self-Check: PASSED

- FOUND: `.planning/phases/53-template-registry-foundation/53-RED-EVIDENCE.md`
- FOUND: `.planning/phases/53-template-registry-foundation/53-CI-EVIDENCE.md`
- FOUND commit `9172aa1c` (Task 1)
- FOUND commit `80fe6b32` (Task 2)
- FOUND commit `a6398818` (Task 3)
