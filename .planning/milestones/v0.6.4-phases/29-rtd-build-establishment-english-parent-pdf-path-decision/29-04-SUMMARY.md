---
phase: 29-rtd-build-establishment-english-parent-pdf-path-decision
plan: 04
subsystem: infra
tags: [readthedocs, typst, pdf, ci, evidence-record]

requires:
  - phase: 29-rtd-build-establishment-english-parent-pdf-path-decision (Plan 03)
    provides: "The PDF-enabling .readthedocs.yaml commit (formats:[pdf], build.jobs.build.pdf override, fonts-noto-cjk) and the local D-12 baseline (93 pages, 9 fonts, 1,693,967 bytes) that this plan's log evidence is measured against"
provides:
  - "Machine-verified, executor-fetched raw RTD build log evidence for build 33756855 (the first build containing the PDF step), recorded verbatim in 29-VERIFICATION.md"
  - "An explicit branch-a decision with the following wave's routing stated: Plan 05 executes, Plan 06 is skipped"
  - "A/2/A4 RESEARCH assumptions each closed with quoted log text rather than assumed"
affects: [29-05-content-comparison]

tech-stack:
  added: []
  patterns:
    - "Evidence-type separation in verification records: quoted log text vs. owner-reported human_needed observation vs. file-plus-exit-code argument, each labelled distinctly rather than blurred together"

key-files:
  created: []
  modified:
    - .planning/phases/29-rtd-build-establishment-english-parent-pdf-path-decision/29-VERIFICATION.md

key-decisions:
  - "Branch A selected: RTD's registry fetch of the four @preview packages is treated as resolved, based on (a) the log's own conjunctive conditions (zero latexmk/pdflatex/.tex hits + PDF step exit 0), (b) owner's visual inspection (codly/gentle-clues confirmed rendered; mitex not determinable — no math in the document), and (c) the unconditional-import argument (base.typ's four #import lines are unguarded, conf.py sets no typst_template override, and a resolvable-import failure would abort the whole compile — so mitex's successful, exit-0 compile proves it resolved too)"
  - "The absence of any per-package @preview resolution line in the 1271-line log is recorded explicitly as a finding, not inferred around or hidden — this is the one point D-07 required care on"
  - "Plan 06 (Branch B fallback link edit) is recorded as skipped; no docs/source/index.rst or README.md edit was made by this plan"

patterns-established: []

requirements-completed: [RTD-02, RTD-03]

coverage:
  - id: D1
    description: "Raw RTD build log for the PDF-enabling commit fetched and searched directly by this executor (not reused from a staged copy), with byte size/line count/status independently re-confirmed"
    requirement: "RTD-02"
    verification:
      - kind: manual_procedural
        ref: "curl https://app.readthedocs.org/api/v2/build/33756855.txt -> code=200 size=157134; wc -l -> 1271"
        status: pass
    human_judgment: false
  - id: D2
    description: "Whole-log search for latexmk/pdflatex/.tex confirms zero hits, satisfying Branch A's LaTeX-exclusion precondition"
    requirement: "RTD-02"
    verification:
      - kind: manual_procedural
        ref: "grep -o -E 'latexmk|pdflatex|\\.tex' /tmp/p29-buildlog-33756855.txt | wc -l -> 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "@preview package-resolution verdict for the four Typst Universe packages (codly, codly-languages, mitex, gentle-clues) -- the log itself is silent, so the verdict rests on owner visual inspection (codly/gentle-clues) plus the unconditional-import file-plus-exit-code argument (mitex)"
    requirement: "RTD-02"
    verification:
      - kind: manual_procedural
        ref: "Owner-reported visual inspection of the served PDF (codly/gentle-clues rendered; mitex not determinable) -- recorded human_needed in 29-VERIFICATION.md SC#2 Excerpt (c)(i)"
        status: pass
    human_judgment: true
    rationale: "The log contains no per-package @preview resolution line, and the mitex portion of the verdict rests on an argument about Typst's import semantics plus the owner's visual read of rendered PDF content -- a human judgment call, not a machine-checkable assertion, even though the supporting premises (file content, exit code) were checked directly by this executor"
  - id: D4
    description: "Branch decision (branch-a) recorded with justifying excerpt and explicit Plan 05 (runs) / Plan 06 (skipped) routing"
    requirement: "RTD-03"
    verification:
      - kind: manual_procedural
        ref: "29-VERIFICATION.md ## Branch Decision section, automated marker check: python3 -c \"... s=t.split('## Branch Decision')[-1]; n=sum(k in s for k in (...)); ...\" -> branch_markers 1, exit 0"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-07-25
status: complete
---

# Phase 29 Plan 04: RTD Build Log Evidence and Branch A/B Decision Summary

**Fetched and searched RTD build 33756855's raw log directly, found zero LaTeX-toolchain markers and a completed PDF step but no per-package `@preview` resolution line, and recorded that absence honestly alongside two independent lines of evidence (owner visual inspection + unconditional-import argument) that jointly justify selecting Branch A.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-07-25
- **Tasks:** 3 (Task 1 checkpoint already resolved by the orchestrator before this agent was spawned; Task 2 executed; Task 3 decision already resolved — branch-a — recorded)
- **Files modified:** 1 (`29-VERIFICATION.md`, append-only)

## Accomplishments

- Independently re-fetched the raw build log (`https://app.readthedocs.org/api/v2/build/33756855.txt`, `code=200 size=157134`, `1271` lines) and the API v3 status JSON (`state.code: finished`, `success: true`, `commit: dcc6a523fc2d16f3dae925e17d63a1a24318b6d7`) — not reused from the orchestrator's staged copy — so the recorded evidence is this executor's own machine observation
- Ran the whole-log LaTeX-toolchain marker search myself: `grep -o -E 'latexmk|pdflatex|\.tex' ... | wc -l` → `0`, satisfying Branch A's D-07 precondition
- Confirmed the apt (`fonts-noto-cjk is already the newest version`) and `build.jobs.build.pdf` (`mkdir`/`sphinx-build`/`mkdir`/`cp`, all `exit-code: 0`, `Generated PDF: .../typsphinx.pdf`) excerpts verbatim from the fetched log
- Grepped the whole log for `codly|mitex|gentle-clues|@preview|packages\.typst\.org` and found exactly one hit — a `conf.py` value echo (`typst_use_mitex = True`), not a resolution event — and recorded that absence explicitly rather than glossing over it
- Verified `typsphinx/templates/base.typ`'s four `#import "@preview/..."` lines are unconditional (no `#if` guard) and that `docs/source/conf.py` sets no `typst_template` override, supporting the unconditional-import argument that settles `mitex`
- Re-fetched RTD's Downloads-menu PDF myself: `code=200 content_type=application/pdf size=1697498`, `93 page(s)` (via `file`), `sha256=d86c31588356bd71500e5411fa0cfc09dddc69b88349b77159f58c635abe07a5`
- Appended `## SC#2 — raw build log, @preview verdict` and `## Branch Decision` to `29-VERIFICATION.md`, keeping Plans 02/03's prior seven sections untouched (append-only)
- Recorded the owner's pre-resolved branch selection (`branch-a`) with the justifying excerpt quoted inline, and stated explicitly that Plan 05 executes and Plan 06 is skipped

## Task Commits

1. **Task 1 (checkpoint:human-action, `gate="blocking-human"`)** — Already presented and resolved by the orchestrator before this agent was spawned; not re-presented. Evidence carried into Task 2's recorded excerpts and independently re-verified by this executor's own fetch/grep commands.
2. **Task 2: Record the SC#2 evidence verbatim, with a machine-recorded whole-log search where possible** — `de0e9bc` (docs)
3. **Task 3 (checkpoint:decision, `gate="blocking"`)** — Already resolved by the owner (`branch-a`) before this agent was spawned; the `## Branch Decision` section recording that verdict was written as part of the same `de0e9bc` commit (Task 2's file edit and Task 3's decision record land in the same append to keep the file's append-only discipline in a single diff).

**Plan metadata:** (final metadata commit intentionally not made by this parallel executor — the orchestrator owns STATE.md/ROADMAP.md updates after all wave agents complete, per this plan's execution instructions)

## Files Created/Modified

- `.planning/phases/29-rtd-build-establishment-english-parent-pdf-path-decision/29-VERIFICATION.md` — appended `## SC#2 — raw build log, @preview verdict` (build identity, three verbatim excerpts, the executor's own whole-log searches, A1/A2/A4 verdicts, Downloads-menu observation, and a plain statement of what the log supports/does not) and `## Branch Decision` (branch-a selected, justifying excerpt, Plan 05/06 routing)

## Decisions Made

- **Branch A selected.** The two log-quoted conjunctive conditions (zero LaTeX-toolchain markers; PDF step exits 0 and produces `typsphinx.pdf`) are both satisfied by quoted log text. The third condition — the four `@preview` packages resolving — has no per-package log line at all (confirmed by this executor's own grep, one hit total, and that hit is a `conf.py` echo, not a resolution event). That gap is closed by two independent, clearly-labelled pieces of evidence rather than by inference: (i) the owner's visual inspection of the served PDF (codly and gentle-clues confirmed rendered; mitex explicitly reported as not determinable by inspection, because the PDF contains no math), and (ii) the unconditional-import argument — `typsphinx/templates/base.typ`'s four `#import` lines have no conditional guard, `docs/source/conf.py` sets no template override, and because an unresolvable `@preview` import fails Typst's whole compile regardless of whether the document uses math, the compile's exit-0 success proves `mitex` resolved too.
- **The log's silence on per-package `@preview` lines is recorded as a finding, not smoothed over.** This is the one place D-07 explicitly warned against inferring past a gap in the evidence; Excerpt (c) states the absence plainly before presenting the two supplementary evidence lines.
- **Plan 06 is recorded as skipped.** No edit was made to `docs/source/index.rst` or `README.md` in this plan — the Branch B fallback link is not needed because Branch A was taken.

## Deviations from Plan

None — plan executed exactly as written. Task 1 and Task 3's checkpoints were pre-resolved by the orchestrator/owner before this agent was spawned (per the `<checkpoint_already_resolved>` instruction), and this executor's job was to independently re-verify the evidence with its own commands (rather than trust the orchestrator's brief blindly) and record Task 2's SC#2 section plus Task 3's Branch Decision section. All of this executor's own fetch/grep/read commands agreed exactly with the orchestrator's brief — no divergence was found anywhere.

## Issues Encountered

None. The worktree-isolation harness rejected two initial Bash commands (a multi-statement `env -u ...` compound and a heredoc-style compound HEAD check) as "too complex to verify" or using disallowed wrapping; both were resolved by re-running the equivalent logic as separate, simpler commands, which the harness accepted.

## User Setup Required

None — no external service configuration required by this plan. (RTD project setup itself was completed in Plans 02/03; this plan only reads an already-produced build log and RTD's already-live Downloads endpoint.)

## Next Phase Readiness

- **Plan 05** (Branch A content comparison against the D-12 local baseline) is unblocked and should execute next — this plan's Downloads-menu PDF fetch (93 pages, `sha256=d86c31...`) is available as a starting point, though Plan 05 owns its own D-12 four-check comparison (page count, extracted text, CJK font coverage, owner visual tofu check) rather than reusing this plan's structural-only observation.
- **Plan 06** (Branch B fallback link edit) is confirmed skipped — no action needed from it in this phase.
- No blockers. `29-VERIFICATION.md`'s append-only invariant held: `git diff --stat` shows only insertions (275 lines added, 0 removed) relative to the plan's starting state, and `git status --porcelain typsphinx/ tests/ docs/ pyproject.toml .readthedocs.yaml` is empty.

## Self-Check

- `.planning/phases/29-rtd-build-establishment-english-parent-pdf-path-decision/29-VERIFICATION.md` exists and contains both new sections: confirmed via the plan's own automated verify commands (Task 2: `MISSING: [] CLOBBERED: []`, exit 0; Task 3: `branch_markers 1`, exit 0).
- Commit `de0e9bc` exists: confirmed via `git log --oneline -3` showing `de0e9bc docs(29-04): record SC#2 raw build log evidence and branch-a decision` as HEAD.
- `git status --porcelain typsphinx/ tests/ docs/ pyproject.toml .readthedocs.yaml` returned empty — no repository source file was modified by this plan.

## Self-Check: PASSED

---
*Phase: 29-rtd-build-establishment-english-parent-pdf-path-decision*
*Completed: 2026-07-25*
