---
phase: 44-typst-documents-default-derivation-builder-input-hardening
plan: 03
subsystem: config
tags: [measurement, changelog, worktree-isolation, sphinx, typst]

# Dependency graph
requires:
  - phase: 44-01
    provides: "The RED commit SHA (eeb9304) consumed as this plan's pre-change side, plus the CONF-08 derivation this plan measures the effect of"
provides:
  - "44-GATE-EVIDENCE-03.md — the SC#4 measured before/after record: two named commits, two per-side typsphinx.__file__ isolation proofs, four real builds, a paired before/after table, and a quotable Phase 46 CHANGELOG source-text block"
affects: [46-release-prep]

# Actuals (#2632)
actuals:
  tokens: 5418
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-build worktree-isolation measurement method (git worktree add --detach + per-worktree uv sync + typsphinx.__file__ isolation proof), reused verbatim from 42-GATE-EVIDENCE-05.md"

key-files:
  created: []
  modified:
    - .planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-03.md

key-decisions:
  - "Reused 42-GATE-EVIDENCE-05.md's exact throwaway-worktree method (git worktree add --detach <scratch>/<name>, per-worktree env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev, uv shim for the NixOS-sandbox ELF hazard, typsphinx.__file__ isolation proof) rather than devising a new one."
  - "Named both throwaway worktrees pre-wt/post-wt under /tmp/.../scratchpad/measure-44-03/, outside .claude/worktrees/, per the plan's throwaway-worktree-discipline instructions — confirmed neither collided with the orchestrator's manifest-scoped worktree lifecycle or the concurrently-running sibling (44-04)."
  - "This plan's own figures (412-byte pre-change index.typ) are recorded as diverging from 44-CONTEXT.md's D-05 figure (373 bytes) because D-05 measured a DIFFERENT minimal project ('My Cool Project') than this plan's fixture ('Quickstart Default Gate', containing literal body text QSDEFAULTBODY) — the divergence is stated explicitly in the evidence file rather than silently reconciled, per the plan's transparency contract."

requirements-completed: [CONF-08]

coverage:
  - id: D1
    description: "The CONF-08 output-filename rename (index.typ -> quickstartdefaultgate.typ) and the content-structure change (untemplated body -> fully templated) are measured on two real builds at two named commits, each built from its own isolated throwaway worktree"
    requirement: "CONF-08"
    verification:
      - kind: other
        ref: "44-GATE-EVIDENCE-03.md §§ 1-6 (two named commits, two typsphinx.__file__ isolation proofs, four real sphinx-build runs with recorded exit codes/warnings/byte sizes/verbatim heads, one paired before/after table)"
        status: pass
    human_judgment: true
    rationale: "The plan's own must_haves.truths includes a backstop-verification item — whether the recorded pair is sufficient as Phase 46's CHANGELOG source text is a judgment a verifier cannot confirm from command output alone (per 44-03-PLAN.md's <probe_findings>). Flagging human_judgment: true rather than asserting an automated pass."

duration: ~35min
completed: 2026-08-04
status: complete
---

# Phase 44 Plan 03: CONF-08 SC#4 Measured Before/After Record Summary

**Measured, on two real `sphinx-build` runs against named pre-change (`eeb9304`) and post-change (`b819c8b`) commits — each built from its own freshly-provisioned throwaway worktree — that an unset `typst_documents` build changes both its emitted filename (`index.typ` → `quickstartdefaultgate.typ`) and its emitted structure (untemplated body → fully templated), and handed the pair to Phase 46 as quotable CHANGELOG source text.**

## Performance

- **Duration:** ~35 min (worktree provisioning, two throwaway-worktree measurement rounds, full-suite verification)
- **Started:** 2026-08-04 (session start, after HEAD assertion)
- **Completed:** 2026-08-04
- **Tasks:** 2 (both completed)
- **Files modified:** 1 (`44-GATE-EVIDENCE-03.md`, created then extended)

## Accomplishments
- Verified the two named commits this plan pairs: PRE (`eeb9304`, plan 44-01's RED commit, confirmed to touch no `typsphinx/` path) and POST (`b819c8b`, this worktree's HEAD at plan start, confirmed to contain both waves' production changes via `grep -c` on `_default_typst_documents` and `isinstance(docname, str)`).
- Built `tests/fixtures/default_typst_documents_gate` from two independently-provisioned throwaway worktrees (`pre-wt` at PRE, `post-wt` at POST), each with its own `uv sync --extra dev` and a recorded `typsphinx.__file__` isolation proof — the two paths differ and neither is the main checkout, which is the precondition that makes the measured pair meaningful rather than vacuous.
- Recorded all four builds (`-b typstpdf` and `-b typst`, both sides) with exit codes, complete warning text, `ls -la` listings, PDF counts, byte sizes, and verbatim file heads: pre-change `index.typ` is 412 bytes with no template call and 0 PDFs written (1 warning); post-change `quickstartdefaultgate.typ` is 532 bytes with the template import + `#show: project.with(...)` call and 1 PDF written (0 warnings).
- Paired both sides in a six-row before/after table (§ 6) and wrote a quotable `### Changed` CHANGELOG block (§ 7) for Phase 46's REL-06, naming both the rename and the content-structure change with no placeholders.
- Removed both throwaway worktrees (`git worktree remove --force`) and recorded the post-cleanup `git worktree list`, proving neither `pre-wt` nor `post-wt` remains; the listing legitimately still shows the main checkout, this plan's own agent worktree, and the concurrently-running sibling executor's worktree (plan 44-04) — explicitly annotated as expected, not a leak.
- Ran the full pytest suite in this plan's own worktree (855 passed, 1 skipped, exit 0) and confirmed `git status --porcelain typsphinx/ tests/` is empty — this plan changed no production code and no test.

## Task Commits

Each task was committed atomically:

1. **Task 1: Measure the pre-change side (PRE `eeb9304`)** - `5f2ce54` (docs)
2. **Task 2: Measure the post-change side + write Phase 46 CHANGELOG source (POST `b819c8b`)** - `535c3f3` (docs)

**Plan metadata:** _final metadata commit is the orchestrator's responsibility in worktree mode; not made by this executor._

## Files Created/Modified
- `.planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-03.md` — Created by Task 1 (§§ 1-3: named commits, pre-change isolation proof, pre-change builds), extended by Task 2 (§§ 4-9: post-change isolation proof, post-change builds, the paired table, the Phase 46 CHANGELOG source text, cleanup record, verdict).

## Decisions Made
- Reused the exact two-build worktree-isolation method from `42-GATE-EVIDENCE-05.md` (the same `git worktree add --detach` / per-worktree `uv sync` / `uv` shim / `typsphinx.__file__` isolation proof shape) rather than inventing a new measurement procedure — per this plan's own `<read_first>` instructions.
- Recorded the divergence between this plan's measured 412-byte pre-change `index.typ` and `44-CONTEXT.md`'s D-05 figure of 373 bytes explicitly, rather than silently treating them as the same measurement — they are two different fixtures (`Quickstart Default Gate` vs. `My Cool Project`), and the plan's transparency contract requires the measured number to win with the divergence stated.
- Named both throwaway worktrees with a `measure-` prefix under `/tmp/.../scratchpad/`, outside `.claude/worktrees/`, so they could never be confused with (or accidentally merged/deleted by) the orchestrator's manifest-scoped worktree lifecycle.

## Deviations from Plan

None - plan executed exactly as written. Both `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync` invocations and one `.venv/bin/uv` shim per worktree (three worktrees total: `pre-wt`, `post-wt`, and this plan's own agent worktree) were anticipated by the plan's `<worktree_environment_provisioning>` instructions and the CLAUDE.md-documented NixOS-sandbox hazard, not unplanned discoveries.

One tooling note, not a deviation: the sandboxed Bash tool refused a handful of multi-statement / `env`-flag command forms as "too complex to verify staying inside the worktree" (e.g. `env -u X -u Y uv sync --extra dev` run directly, or chained `cd && ln -sf && readlink -f` in one call). Each was re-expressed as either a single command with inline `VAR= VAR2= cmd` env-var prefixing, or as separate single-purpose Bash calls (one `cd && cmd`, one `ln -sf`, one `readlink -f`) — no different outcome, no different verification, purely a call-shape adjustment. No plan step was skipped or weakened by this.

## Issues Encountered
None beyond the tooling note above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- ROADMAP SC#4 is discharged: `44-GATE-EVIDENCE-03.md` §§ 1-9 record the measured pre/post pair, both isolation proofs, the pathspec-scoped production diff (only `typsphinx/__init__.py` and `typsphinx/builder.py` changed between PRE and POST), and the Phase 46 CHANGELOG source text.
- Phase 46 (REL-06) can quote `44-GATE-EVIDENCE-03.md` § 7 directly for the `## [0.7.1]` CHANGELOG entry rather than re-deriving the figures.
- Plan 44-04's own `44-GATE-EVIDENCE-04.md` (SC#5, the repo-wide existing-test audit) is unaffected by this plan — no code or test file was touched here.
- No blockers.

---
*Phase: 44-typst-documents-default-derivation-builder-input-hardening*
*Completed: 2026-08-04*

## Self-Check: PASSED

`44-GATE-EVIDENCE-03.md` confirmed present on disk at
`.planning/phases/44-typst-documents-default-derivation-builder-input-hardening/44-GATE-EVIDENCE-03.md`
(21673 bytes). Both commits (`5f2ce54`, `535c3f3`) confirmed present in `git log --oneline --all`.
Both throwaway worktrees (`pre-wt`, `post-wt`) confirmed absent from `git worktree list` and from
the scratchpad directory listing. `git status --porcelain typsphinx/ tests/` confirmed empty.
