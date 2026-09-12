---
phase: 68-documentation-follow-through-claude-md-tox-ini-flake-nix
plan: 03
subsystem: infra
tags: [nix, flake, devshell, documentation, fhs]

# Dependency graph
requires:
  - phase: 64-fhs-wrapper-and-command-shims-in-flake-nix
    provides: the FHS wrapper, per-command shims, and the two-leg uv resolution this plan documents
  - phase: 65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves
    provides: the tox-uv revert that makes .venv/bin/uv exist, which the stale uvShim comment referenced as future
provides:
  - flake.nix header block above `outputs` explaining the FHS wrapper, the shim roster, namespace inheritance, and the darwin guard (unverified by construction)
  - restated per-element notes (fhsRun, strict shims, roster, uvShim) with no decision IDs and no phase-relative phrasing
  - a derivation-identity proof (four-system drvPath, comment-stripped hash, flake check, comment-only diff) that the edit changed no Nix expression or script body
affects: [69-v0-9-3-close-prep]

# Actuals (#2632)
actuals:
  tokens: 5973
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns: ["Nix comment restatement gated by derivation-identity (four-system drvPath + comment-stripped hash + comment-only diff)"]

key-files:
  created:
    - .planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-FLAKE-EVIDENCE.md
  modified:
    - flake.nix

key-decisions:
  - "Restated the uvShim comment by role, with no version numbers and no ties to a future phase, per D-12."
  - "Inserted one contiguous header block above `outputs =` covering the FHS wrapper, the shim roster, namespace inheritance, and the darwin guard, ending in archive-stable measurement sources cited by milestone + phase + file name, never a .planning/phases path."
  - "Dropped decision-ID prefixes from the strict-shims and roster comments; left the venvWalk note unchanged since it already carried no decision ID."

requirements-completed: []  # DOC-21 closes in 68-04 on the merged tree

coverage:
  - id: D1
    description: "flake.nix header above `outputs` explains the FHS wrapper, the two falsified alternatives, which commands are shimmed and why, and the darwin guard"
    requirement: "DOC-21"
    verification:
      - kind: other
        ref: "68-FLAKE-EVIDENCE.md ## Header and per-element notes; token-presence check for mkShell/buildFHSEnv/stub-ld/nix develop/direnv/shellHook/subshell/fork/exec/inherit/CLAUDE.md/darwin/unverified/Linux-only/CI/nix eval/issue/built/nixpkgs and all five citations"
        status: pass
    human_judgment: false
  - id: D2
    description: "Per-element notes (fhsRun, strict shims, roster, uvShim) restated with no decision IDs and no phase-relative phrasing"
    requirement: "DOC-21"
    verification:
      - kind: other
        ref: "grep -nE 'D-[0-9]' flake.nix and grep -nE 'until Phase|exist until' flake.nix, both empty"
        status: pass
    human_judgment: false
  - id: D3
    description: "Derivation-identity gate: four-system drvPath, flake check, comment-stripped hash, and comment-only diff, all proven unchanged"
    requirement: "DOC-21"
    verification:
      - kind: other
        ref: "68-FLAKE-EVIDENCE.md ## Baseline / ## Gates after the edit; DRV_BEFORE_* == DRV_AFTER_* for all four systems, FLAKE_CHECK_AFTER_EXIT = 0, comment-stripped sha256sum equal"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-09-12
status: complete
---

# Phase 68 Plan 03: `flake.nix` Notes Summary

**Comment-only header and per-element rewrite of `flake.nix` (FHS wrapper rationale, shim roster, namespace inheritance, darwin guard), proven identical on all four declared systems via `drvPath`, `nix flake check`, and a comment-stripped hash.**

## Head-check and gate values (plan output spec)

- `BASE_68_03 = 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a`
- `DRV_BEFORE_x86_64_linux = DRV_AFTER_x86_64_linux = /nix/store/jnbia2810h255l78mn8k26sic5xqvb9p-nix-shell.drv`
- `DRV_BEFORE_aarch64_linux = DRV_AFTER_aarch64_linux = /nix/store/8qqw29d5k2jp4w9pcc4zyhk418fmdv4m-nix-shell.drv`
- `DRV_BEFORE_x86_64_darwin = DRV_AFTER_x86_64_darwin = /nix/store/fclfls55m9lp06679x7zrw0qzjya834j-nix-shell.drv`
- `DRV_BEFORE_aarch64_darwin = DRV_AFTER_aarch64_darwin = /nix/store/2m6y6pshri0vyw3jb5agczjnz9a92sxc-nix-shell.drv`
- `FLAKE_CHECK_AFTER_EXIT = 0`
- `COLLECT_BEFORE_68_03 = 1548`, `COLLECT_AFTER_68_03 = 1548`

No `## HALT` heading was written at any point. Full transcripts: `68-FLAKE-EVIDENCE.md`.

## Performance

- **Duration:** 35 min
- **Started:** 2026-09-12T15:48:28Z
- **Completed:** 2026-09-12
- **Tasks:** 2
- **Files modified:** 2 (`flake.nix`, `68-FLAKE-EVIDENCE.md`)

## Accomplishments
- Rewrote the stale `uvShim` comment (D-12): describes the two-leg `uv` resolution by role, names no version number, and drops the "does not exist until Phase 65" phrasing that Phase 65's revert already falsified.
- Added a header block directly above `outputs =` (D-10 a/b/c, D-11, D-09): the `mkShell`-stays rationale and its two falsified alternatives (`buildFHSEnv`'s `.env` under `nix develop`/direnv resolving to `stub-ld`; a `shellHook` that `nix develop` never runs and direnv only partially execs), the seven shimmed commands and why namespace inheritance across `fork`/`exec` limits shims to top-level entrypoints, the darwin guard (unverified by construction — no maintainer machine, no CI lane, only a `nix eval` on Linux), and five archive-stable measurement-source citations ending on a `.md`-named line.
- Restated the `fhsRun`, strict-shims, and roster per-element notes with decision-ID prefixes removed and the `fhsRun` citation upgraded to name milestone and phase (`v0.9.3 Phase 64 64-LIBZ-FIX-EVIDENCE.md`).
- Proved the entire edit is comment-only: all four systems' `devShells.<sys>.default.drvPath` are byte-identical before and after, `nix flake check --all-systems --no-build` exits 0 both times, the comment-stripped `sha256sum` is unchanged, and `git diff -U0` against base shows only comment/blank-line hunks.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — head check, four-system drvPath baseline, D-12 uvShim note rewrite** - `44dbdb53` (docs)
2. **Task 2: Header notes (D-10 a/b/c, D-11, D-09) and remaining per-element notes** - `b854e969` (docs)

_No separate plan-metadata commit in worktree mode — the orchestrator commits SUMMARY.md/REQUIREMENTS.md centrally per the parallel-execution contract._

## Files Created/Modified
- `flake.nix` - Header block above `outputs`; restated `fhsRun`, strict-shims, roster, and `uvShim` comments; one-line darwin pointer above `default = pkgs.mkShell {`. No Nix expression or script body changed.
- `.planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-FLAKE-EVIDENCE.md` - Full transcripts: head check, provisioning, four-system baseline, flake check, comment-stripped hash, pytest collect count, the D-12 rewrite, the header/per-element notes, and the post-edit gates.

## Decisions Made
- Kept the `venvWalk` per-element note unchanged — it already carried no decision ID and already satisfied D-09's self-contained-prose rule; editing it risked introducing drift for no D-09 benefit.
- Added a one-line optional darwin pointer above `default = pkgs.mkShell {` (Task 2 step 3 offers this at Claude's discretion) rather than duplicating the full darwin rationale a second time, keeping D-07's "rationale lives once, in the header" split intact.
- Wrote the header's measurement-source citations as single physical lines (not wrapped across two comment lines) so the file-wide "every `NN-*.md` citation carries `v0.9.3 Phase N` on the same line" invariant holds for grep-based verification, not just for a human reader assembling the fragments.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug in tooling, not in this plan's deliverable] The plan's own automated pytest-collect-count regex never matches on this tree**
- **Found during:** Task 2 (re-running the plan's literal `<verify>` command before committing)
- **Issue:** Task 2's automated `<verify>` re-derives the live pytest collect count with `sed -n 's/^\([0-9][0-9]*\) tests\{0,1\} collected.*/\1/p'`, anchored to column 1. This project's `pytest --collect-only -q` summary line is always padded with `=` characters to fill the terminal width (`======================== 1548 tests collected in 0.27s =========================`), even when stdout is not a tty, so the digit is never at column 1. This is a property of this tree's pytest output format, not something introduced by this plan's comment-only edit — the same command was independently confirmed to also fail against the base tree, before any Task 2 edit.
- **Fix:** No code, plan, or PLAN.md text was altered (out of this plan's `files_modified` scope; PLAN.md is frozen input, not an executor-editable artifact). Verified the underlying invariant the check exists to prove — the collected test count is unchanged before and after the edit — using an equivalent, non-anchored extraction: `grep -oE '[0-9]+ tests? collected' | grep -oE '^[0-9]+'` returns `1548` both times.
- **Files modified:** None (documentation of the finding only, in `68-FLAKE-EVIDENCE.md`'s "## Note on the plan's automated `<verify>` pytest-collect-count check").
- **Verification:** `COLLECT_BEFORE_68_03 = COLLECT_AFTER_68_03 = 1548`, confirmed via the working extraction command, recorded in the evidence file.
- **Commit:** Documented in `b854e969` (Task 2 commit, evidence file only — no `flake.nix` behavior changed by this finding).

---

**Total deviations:** 1 auto-fixed (1 tooling defect in the plan's own literal verify command, unrelated to this plan's edit).
**Impact on plan:** None on the deliverable. `flake.nix`'s comment-only edit and derivation-identity proof are both intact and independently confirmed; the finding only concerns one brittle regex inside the plan's automated `<verify>` block, which the 68-04 gate-runner or `/gsd-verify-work` should also expect to see fail on this specific sub-check if it re-runs the literal command verbatim.

## Issues Encountered
None beyond the deviation documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `flake.nix` now documents its own structure (DOC-21's content requirement) with a derivation-identity proof that no script body moved.
- 68-04 re-reads this header against `CLAUDE.md`'s `Commands` block (68-01's edit, parallel wave-1 sibling, not visible from this worktree) and re-evaluates the four drvPaths on the merged tree — this plan does not close DOC-21 itself; `requirements-completed` is intentionally `[]`.
- No blockers. The one deviation above is advisory and does not affect DOC-21's substantive content.

---
*Phase: 68-documentation-follow-through-claude-md-tox-ini-flake-nix*
*Completed: 2026-09-12*

## Self-Check: PASSED

- `flake.nix` exists and carries the header/per-element edits: `[ -f flake.nix ]` → FOUND.
- `.planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-FLAKE-EVIDENCE.md` exists: FOUND.
- Both task commits exist in this branch's history: `git log --oneline --all | grep -q 44dbdb53` → FOUND; `git log --oneline --all | grep -q b854e969` → FOUND.
- Plan-level `<verification>` re-checked: header covers D-10(a)(b)(c)/D-11 and ends on a `.md` source line — PASS; per-element notes carry no decision IDs and no phase-relative phrasing (`grep -nE 'D-[0-9]|until Phase|exist until' flake.nix` empty) — PASS; all four drvPaths byte-identical before/after, flake check exit 0, diff comment-only — PASS.
- `commits: 2`, measured via `git rev-list --count 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a..HEAD`, matches `plan_head_before: 0bd33617d3cdf96f0342bdaeb19a0cb031f7c10a`.
