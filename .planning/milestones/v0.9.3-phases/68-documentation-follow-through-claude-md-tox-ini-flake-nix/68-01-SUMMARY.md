---
phase: 68-documentation-follow-through-claude-md-tox-ini-flake-nix
plan: 01
subsystem: docs
tags: [claude-md, tox-uv, nixos, flake-nix, worktree-provisioning]

# Dependency graph
requires:
  - phase: 65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves
    provides: the landed tox-uv~=1.35 pin this plan's D-08 rewrite documents
  - phase: 64-fhs-wrapper-and-command-shims-in-flake-nix
    provides: the seven FHS shims (uv, tox, ruff, black, mypy, pytest, sphinx-build) this plan's new NixOS development shell subsection documents
provides:
  - CLAUDE.md line 11 and the tox.ini Conventions bullet rewritten to name the landed tox-uv~=1.35 pin, with tox-uv-bare demoted to history only
  - a new "### NixOS development shell" subsection describing the seven shims, exit-127 failure mode, the uv two-leg bootstrap fallback, the launch prerequisite/check, locale passthrough, and interpreter divergence
  - a new boundary paragraph inside "### Worktree-isolated execution" restating ROADMAP SC#1's AMENDED reading (D-01) in CLAUDE.md's own words
  - 68-CLAUDEMD-EVIDENCE.md with verbatim transcripts for the D-02 vacuity claim, the D-08 rewrite, and the byte-identity/collect-count gates
affects: [68-04]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 4741
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Verbatim-transcript evidence convention (phase *-EVIDENCE.md, fenced $ command / output blocks, one-sentence conclusion) — same idiom as Phase 64/65"
    - "Historical fact kept, current-reasoning added idiom — applied to CLAUDE.md:77's tox-uv-bare -> tox-uv rewrite"

key-files:
  created:
    - .planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-CLAUDEMD-EVIDENCE.md
  modified:
    - CLAUDE.md

key-decisions:
  - "D-08 rewrite touches only line 11 and the tox.ini Conventions bullet — verified via git diff -U0 against BASE_68_01, whose only removed lines are the old 11 and 77."
  - "D-02's vacuity claim (no manual ln -sf / patchelf step ever existed in CLAUDE.md) is evidenced at base with three empty git log -S / git grep results, transcribed verbatim before the edit."
  - "New ### NixOS development shell subsection placed between the last Conventions bullet and ### Worktree-isolated execution; contains no digit-dot-digit version number per D-06."
  - "New boundary paragraph inside ### Worktree-isolated execution restates the AMENDED SC#1 reading without touching the Detection rule line or the provisioning recipe, both proven byte-identical to base via sha256sum."

patterns-established: []

requirements-completed: []  # DOC-19 closes in 68-04 on the merged tree, per this plan's own frontmatter and the project briefing.

coverage:
  - id: D1
    description: "CLAUDE.md line 11 and the tox.ini Conventions bullet name the landed tox-uv~=1.35 pin, with tox-uv-bare as history only and the old do-not-revert instruction removed"
    verification:
      - kind: other
        ref: "68-CLAUDEMD-EVIDENCE.md § D-08 rewrite (git diff -U0 against BASE_68_01; sed -n '11p;77p' after edit)"
        status: pass
    human_judgment: false
  - id: D2
    description: "New ### NixOS development shell subsection (D-02..D-07) and D-01 boundary paragraph inside ### Worktree-isolated execution, with the provisioning recipe byte-identical to base and the collected pytest count unchanged (1548 -> 1548)"
    verification:
      - kind: other
        ref: "68-CLAUDEMD-EVIDENCE.md § NixOS subsection and boundary paragraph, § Gates after the edit (token-presence checks, heading-order check, sha256sum recipe-tail match, pytest --collect-only re-run)"
        status: pass
    human_judgment: false

# Metrics
duration: 7min
completed: 2026-09-12
status: complete
---

# Phase 68 Plan 01: CLAUDE.md Documentation Follow-Through Summary

**Rewrote CLAUDE.md's stale `tox-uv-bare` references to the landed `tox-uv~=1.35` pin and added a new "NixOS development shell" subsection plus a worktree-boundary paragraph documenting the Phase 64 FHS shims, with the provisioning recipe proven byte-identical to base throughout.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-09-12T15:46:36Z
- **Completed:** 2026-09-12T15:53:49Z
- **Tasks:** 2
- **Files modified:** 2 (`CLAUDE.md`, `68-CLAUDEMD-EVIDENCE.md`)

## Accomplishments
- Line 11 and the `tox.ini` Conventions bullet now name `tox-uv~=1.35`, keeping the ini-parser comma-splitting explanation and adding a short history note that `tox-uv-bare` was only ever needed because the bundled `uv` could not exec on NixOS — the do-not-revert instruction is removed.
- A new `### NixOS development shell` subsection (between the last Conventions bullet and `### Worktree-isolated execution`) documents the seven shimmed commands, the exit-127 failure mode, the `uv` two-leg nixpkgs-fallback bootstrap, the launch prerequisite and `grep -q typsphinx-fhs-run "$(command -v uv)"` check, the vacuous D-02 "no manual step" claim, locale passthrough, and interpreter divergence — with a single pointer sentence to `flake.nix`'s own header notes for rationale, and no version numbers anywhere in it.
- A new boundary paragraph inside `### Worktree-isolated execution` restates ROADMAP SC#1's `AMENDED 2026-09-12` reading in CLAUDE.md's own words: the recipe stays mandatory, `flake.nix` does not substitute for it, and the shims reach a worktree only by PATH inheritance from the launching session, never by direnv inside the worktree.
- `68-CLAUDEMD-EVIDENCE.md` records the D-02 vacuity evidence at base (three empty `git log -S` / `git grep` results), the D-08 rewrite diff, and the recipe-tail `sha256sum` match both before and after Task 2's additive edit, plus the unchanged `pytest --collect-only` count (1548 → 1548).

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — head check, baseline, D-02 evidence at base, D-08 rewrite** - `b6cbeebf` (docs)
2. **Task 2: New NixOS development shell subsection and D-01 boundary paragraph** - `322b8a4f` (docs)

_Note: Task 1 is `type="tracer"`; its own `<verify>` was re-run per the end-of-phase tracer feedback gate (row 3 — interactive, `end-of-phase`, automated-only verify) and passed, so execution proceeded directly to Task 2 with no checkpoint._

## Files Created/Modified
- `CLAUDE.md` - line 11 and the Conventions `tox.ini` bullet rewritten (D-08); new `### NixOS development shell` subsection added (D-02..D-07); new boundary paragraph added inside `### Worktree-isolated execution` (D-01)
- `.planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-CLAUDEMD-EVIDENCE.md` - new evidence file with verbatim transcripts for both tasks

## Decisions Made
- Kept the subsection name at Claude's discretion (per CONTEXT.md) as `### NixOS development shell`, matching the plan's own working title and satisfying the `NIXOS_SUBSECTION_HEADING` evidence key exactly.
- Followed the existing `**Bold label.** sentence.` structure from `### Worktree-isolated execution` for both the new subsection's internal paragraphs and the boundary paragraph, per 68-PATTERNS.md's style precedent.
- Placed the D-02 "no manual step" sentence entirely inside the new subsection so the file-wide `ln -sf` / `patchelf` grep count matches the subsection-only count exactly (required by the plan's Task 2 gate).

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- The scratchpad directory (`/tmp/claude-1000/.../scratchpad`) is shared across sibling worktree agents in this wave; a verification script I wrote under a generic filename (`verify_task1.sh`) was overwritten mid-session by a sibling agent's own script for a different plan (68-03, `flake.nix`). No project files were affected — this only touched a throwaway shell script in `/tmp`. Recovered by re-running all verification under a filename namespaced with this worktree's own agent id (`agent-a2eb538334cf0cc75-verify68-01.sh`) before finalizing, confirming both tasks' gates pass independently of the collision.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `CLAUDE.md`'s half of DOC-19 is delivered: the landed `tox-uv~=1.35` pin is named, the NixOS mechanism is documented operationally, and the SC#1 boundary is stated per the AMENDED reading — all while the provisioning recipe stays byte-identical and mandatory.
- 68-04 (wave 2) re-reads this against the merged tree alongside 68-02's `tox.ini`/test-file changes and 68-03's `flake.nix` changes, and closes DOC-19/DOC-20/DOC-21 together.
- No blockers. `requirements-completed` is intentionally empty here per this plan's own `<output>` spec — DOC-19 is recorded complete in 68-04.

---
*Phase: 68-documentation-follow-through-claude-md-tox-ini-flake-nix*
*Completed: 2026-09-12*

## Self-Check: PASSED

- `CLAUDE.md` exists on disk: FOUND
- `.planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-CLAUDEMD-EVIDENCE.md` exists on disk: FOUND
- Task 1 commit `b6cbeebf` present in `git log --oneline --all`: FOUND
- Task 2 commit `322b8a4f` present in `git log --oneline --all`: FOUND
- Both tasks' `<acceptance_criteria>` re-verified via a fresh worktree-scoped script (`agent-a2eb538334cf0cc75-verify68-01.sh`) after a scratchpad collision with a sibling agent: TASK1 VERIFY PASS, TASK2 VERIFY PASS
- Plan-level `<verification>` (D-08 wording, subsection/boundary content, recipe byte-identity, unchanged collected-test count) re-confirmed by the same script
