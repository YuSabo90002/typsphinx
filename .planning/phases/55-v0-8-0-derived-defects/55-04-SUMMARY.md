---
phase: 55-v0-8-0-derived-defects
plan: 04
subsystem: docs
tags: [changelog, roadmap, evidence, phase-boundary-gate, keep-a-changelog]

# Dependency graph
requires:
  - phase: 55-01-xref-05-label-collision-fix
    provides: "XREF-05 fix, 55-01-RED-EVIDENCE.md"
  - phase: 55-02-bld-07-bld-08-include-graph-defects
    provides: "BLD-07/BLD-08 fixes, 55-02-RED-EVIDENCE.md"
  - phase: 55-03-bld-09-img-03-track-image-defects
    provides: "BLD-09/IMG-03 fixes, 55-03-RED-EVIDENCE.md, the SC#4 amendment replacement text and the checkpoint resolution to record"
provides:
  - "CHANGELOG.md's Unreleased section carries a Fixed subsection announcing all five phase-55 defects"
  - "ROADMAP.md Phase 55 SC#4 amended to match the backslash-normalized predicate that actually shipped"
  - "55-04-EVIDENCE.md — the phase-boundary green measurement, the D-05 requirement-to-gate map, the checkpoint resolution, and the two-item open list"
affects: [57-v0-9-0-release-prep, changelog-curation]

# Actuals (#2632)
actuals:
  tokens: 3733
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "A phase whose SC#4 wording diverged from what a sibling plan's checkpoint actually shipped gets a scoped ROADMAP amendment in the aggregation plan, with the precise replacement text pre-written by the plan that resolved the checkpoint rather than re-derived"
    - "Every number in a phase-boundary evidence file is produced by a command run in that task after the merge, never transcribed from a sibling plan's SUMMARY"

key-files:
  created:
    - .planning/phases/55-v0-8-0-derived-defects/55-04-EVIDENCE.md
  modified:
    - CHANGELOG.md
    - .planning/ROADMAP.md

key-decisions:
  - "Applied the ROADMAP SC#4 amendment verbatim from 55-03-SUMMARY.md's pre-written replacement text, per the owner's checkpoint decision recorded there — did not re-derive the wording"
  - "Used nix run nixpkgs#ruff -- check . as the ruff gate, since uv run ruff check . fails to exec on this NixOS worktree with the same pre-existing generic-linux-ELF hazard 55-01/55-02/55-03 all independently recorded"
  - "Left .planning/REQUIREMENTS.md and .planning/STATE.md untouched, per the plan's own scope fence — the phase-completion step owns those transitions"

patterns-established:
  - "The aggregation/CHANGELOG-and-evidence plan in a multi-plan phase reads its sibling plans' SUMMARYs for pre-written amendment text rather than re-deriving decisions the owner already made at a checkpoint"

requirements-completed: [XREF-05, BLD-07, BLD-08, BLD-09, IMG-03]

coverage:
  - id: D1
    description: "CHANGELOG.md's Unreleased section gains a Fixed subsection with exactly five entries, one per requirement ID, following the two existing Changed entries' voice, with the XREF-05 label-name note and the IMG-03 filename note stated explicitly, and the Changed section unmodified at exactly two entries"
    requirement: "XREF-05, BLD-07, BLD-08, BLD-09, IMG-03"
    verification:
      - kind: other
        ref: "uv run python -c \"...\" acceptance-criteria check (all five requirement IDs inside ### Fixed) — see plan Task 1 <verify>"
        status: pass
      - kind: other
        ref: "git diff -- CHANGELOG.md | grep -cE '^-[^-]' returns 0 (purely additive)"
        status: pass
    human_judgment: false
  - id: D2
    description: "ROADMAP.md Phase 55 SC#4's wording is amended to record the backslash-normalized predicate that actually shipped, with the stale builder.py:910 line-number citation removed, applied as a scoped replacement (not a rewrite)"
    requirement: "BLD-09"
    verification:
      - kind: other
        ref: "git diff -- .planning/ROADMAP.md | grep -c '910' returns 1; git diff --stat -- .planning/ROADMAP.md shows 18 changed lines (< 40)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The phase closes on an unconditional zero-failure suite (1366 passed, 5 skipped, 0 failed) with black/ruff/mypy all clean, measured in this worktree after the merge, and recorded in 55-04-EVIDENCE.md"
    requirement: "XREF-05, BLD-07, BLD-08, BLD-09, IMG-03"
    verification:
      - kind: unit
        ref: "uv run pytest -q (1366 passed, 5 skipped, 0 failed)"
        status: pass
      - kind: other
        ref: "uv run black --check .; nix run nixpkgs#ruff -- check .; uv run mypy typsphinx/ — all exit 0"
        status: pass
    human_judgment: false
  - id: D4
    description: "55-04-EVIDENCE.md's requirement-to-gate map shows all five requirements' D-05 evidence tiering honoured (real compile for XREF-05/BLD-07, unit for BLD-08/BLD-09/IMG-03), citing all three per-plan RED-EVIDENCE files by path, plus the checkpoint resolution and the two-item open list"
    requirement: "XREF-05, BLD-07, BLD-08, BLD-09, IMG-03"
    verification:
      - kind: other
        ref: "grep -c 'RED-EVIDENCE' 55-04-EVIDENCE.md returns 7 (>= 3); grep -c 'Checkpoint resolution' returns 1"
        status: pass
    human_judgment: false

duration: 40min
completed: 2026-08-16
status: complete
---

# Phase 55 Plan 04: CHANGELOG Fixed Entries and Phase-Boundary Green Evidence Summary

**Announced all five phase-55 fixes (XREF-05, BLD-07, BLD-08, BLD-09, IMG-03) under CHANGELOG.md's `Unreleased` → `Fixed`, amended ROADMAP SC#4's wording to match the backslash-normalized predicate `55-03` actually shipped (per the owner's checkpoint decision), and closed the phase on a measured 1366 passed / 5 skipped / 0 failed suite with all three CI-matching gates green and a requirement-to-gate map showing D-05's per-defect evidence tiering honoured.**

## Performance

- **Duration:** ~40 min
- **Tasks:** 2 completed (Task 1 auto, Task 2 auto)
- **Files modified/created:** 3 (2 docs modified, 1 new evidence artifact)

## Accomplishments

- `CHANGELOG.md`'s `## [Unreleased]` gained a new `### Fixed` subsection with exactly five entries,
  one per requirement (XREF-05, BLD-07, BLD-08, BLD-09, IMG-03), positioned after `### Changed` and
  before `### Planned for Future Releases` per Keep-a-Changelog ordering. The `### Changed` section
  is untouched, still carrying exactly its two existing breaking entries — no third breaking axis
  was introduced. The XREF-05 entry states explicitly that a label name changes for an identifier
  literally spelling the sanitizer's own escape token and that PDF appearance is otherwise
  unchanged; the IMG-03 entry states explicitly that the relocated file's emitted name now carries
  a short digest prefix.
- `.planning/ROADMAP.md` Phase 55 SC#4 amended, applying `55-03-SUMMARY.md`'s pre-written
  replacement text verbatim: the stale `builder.py:910` line-number citation was replaced with
  "grep the literal call," and the sentence recording that the shipped predicate applies to a
  **backslash-normalized** copy of the URI — not the raw URI SC#4 originally specified — was added,
  with a pointer to `55-03-RED-EVIDENCE.md` § "Predicate measurement". This records the owner's two
  Task-2 checkpoint decisions from plan `55-03` (option-b predicate spelling; yes, amend SC#4).
- `.planning/phases/55-v0-8-0-derived-defects/55-04-EVIDENCE.md` created: every number measured in
  this task, in this worktree, after the merge — full suite **1366 passed, 5 skipped, 0 failed**
  (unconditional zero failures, the stale 7-failure carve-out not cited); `black --check .`,
  `ruff check .` (via the documented nix-store workaround for this NixOS worktree's ELF-exec
  hazard), and `mypy typsphinx/` all exit 0; `@preview` package count confirmed still four across
  all three lockstep sites with no fourth site introduced; zero dependency-array changes in
  `pyproject.toml` across the whole phase (`git diff --stat` against the phase's pre-fix SHA is
  empty); zero typing-import modernization lines; and the milestone branch
  `gsd/v0.9.0-per-document-templates` confirmed present on `origin` by a real `git ls-remote`.
- The requirement-to-gate map (5 rows) shows D-05's per-defect evidence tiering honoured and
  traceable from one place: XREF-05 and BLD-07 both cite a real-compile RED-EVIDENCE file and a
  real-compile gate command; BLD-08, BLD-09, and IMG-03 each cite a unit-level RED-EVIDENCE file
  and a unit gate command. Every gate command was re-run in this task and its pass count recorded.
- The plan `55-03` checkpoint resolution is recorded in full: which option the owner selected
  (option-b, the backslash-normalized predicate), the predicate that shipped, and that ROADMAP
  SC#4's wording was amended in this plan's Task 1 (not left alone).
- The "Open after this phase" list names exactly two deliberately-open, non-blocking items: the
  `_escapes_outdir()` backslash-normalization gap `55-03` filed as a todo, and the residual
  truncated-digest collision probability for IMG-03's relocation key, recorded as a flagged
  assumption (T-55-10) rather than measured.
- No product or test code was touched — `git diff --stat -- typsphinx/ tests/` is empty across both
  tasks, confirming this plan added no product code as its objective states.

## Task Commits

Each task was committed atomically:

1. **Task 1: Author the Unreleased Fixed entries for all five defects (+ conditional ROADMAP SC#4 amendment)** — `d0394773` (docs)
2. **Task 2: Measure and record the phase-boundary green bar and the D-05 evidence map** — `b5826a99` (docs)

## Files Created/Modified

- `CHANGELOG.md` — new `### Fixed` subsection under `## [Unreleased]` with five entries (XREF-05,
  BLD-07, BLD-08, BLD-09, IMG-03); `### Changed` unmodified.
- `.planning/ROADMAP.md` — Phase 55 SC#4's wording amended (scoped replacement, 18 changed lines)
  to record the backslash-normalized predicate that shipped and remove the stale line-number
  citation.
- `.planning/phases/55-v0-8-0-derived-defects/55-04-EVIDENCE.md` — new: the phase-boundary green
  measurement (suite, three CI gates, `@preview` invariant, zero-new-deps, no-typing-modernization,
  milestone-branch-on-remote), the requirement-to-gate map, the checkpoint resolution, and the
  two-item open list.

## Decisions Made

- Applied `55-03-SUMMARY.md`'s pre-written SC#4 replacement text verbatim rather than re-deriving
  the wording — the checkpoint resolution and its measured basis were already recorded there
  precisely so this plan would not have to reconstruct them.
- Used `nix run nixpkgs#ruff -- check .` in place of `uv run ruff check .` for the ruff gate,
  since the `.venv`-bundled ruff binary is a generic-linux ELF that cannot execute directly in
  this NixOS sandbox — the same pre-existing, project-known hazard `55-01-SUMMARY.md`,
  `55-02-SUMMARY.md`, and `55-03-SUMMARY.md` all independently recorded in this same worktree
  lineage. Produced the identical clean result (`All checks passed!`).
- Left `.planning/REQUIREMENTS.md` and `.planning/STATE.md` untouched throughout, per the plan's
  own scope fence — the phase-completion step owns the requirement checkbox transition, which has
  mis-flipped a requirement against a recorded decision four consecutive times in this project's
  history; leaving it untouched here keeps that later diff readable.

## Deviations from Plan

None — plan executed exactly as written. The plan's own conditional instruction (amend ROADMAP
SC#4 only if the `55-03` checkpoint resolved that way) was satisfied on the "amend" branch, per the
explicit owner instruction recorded in this plan's own objective and confirmed by `55-03-SUMMARY.md`.

## Issues Encountered

`uv run ruff check .` fails to exec on this NixOS worktree (`Could not start dynamically linked
executable: ruff`) — the same pre-existing, project-known environment hazard every sibling plan in
this phase (`55-01`, `55-02`, `55-03`) independently recorded. Worked around identically, via
`nix run nixpkgs#ruff -- check .`, which produced the identical clean result (`All checks passed!`)
this plan's own `<verify>` block requires.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- All five phase-55 requirements (XREF-05, BLD-07, BLD-08, BLD-09, IMG-03) are announced in
  `CHANGELOG.md`'s `Unreleased` `Fixed` subsection, ready for Phase 57's curation pass.
- `.planning/ROADMAP.md` Phase 55 SC#4 now matches what shipped — no drift for a future reader to
  reconcile.
- `.planning/phases/55-v0-8-0-derived-defects/55-04-EVIDENCE.md` gives Phase 57 (release prep) a
  single, already-measured phase-boundary green record to cite rather than re-measuring.
- `typsphinx/` and `tests/` are provably untouched by this plan (`git diff --stat` against both
  task commits is empty) — this plan added no product code, as its objective states.
- `.planning/REQUIREMENTS.md` checkbox flips for these five requirements are intentionally left to
  the phase-completion step, per this plan's own scope fence.
- No blockers for Phase 56 (documentation) or Phase 57 (release prep).

## Self-Check: PASSED

All created/modified files exist (`CHANGELOG.md`, `.planning/ROADMAP.md`,
`.planning/phases/55-v0-8-0-derived-defects/55-04-EVIDENCE.md`,
`.planning/phases/55-v0-8-0-derived-defects/55-04-SUMMARY.md`) and both task commit hashes
(`d0394773`, `b5826a99`) resolve in `git log --oneline --all`.

---
*Phase: 55-v0-8-0-derived-defects*
*Completed: 2026-08-16*
