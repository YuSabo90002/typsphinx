---
phase: 64-fhs-wrapper-and-command-shims-in-flake-nix
plan: 03
subsystem: infra
tags: [nix, flake, buildFHSEnv, bubblewrap, worktree, locale, NixOS]

requires:
  - phase: 64-fhs-wrapper-and-command-shims-in-flake-nix (plan 01)
    provides: "flake.nix's typsphinx-fhs-run passthrough and the seven D-01 command shims, reachable on this session's inherited PATH after the Claude Code relaunch"
provides:
  - "NIX-07: proof that every shim resolves by absolute, un-shadowable path and cannot recurse or escape, via a rename-the-target experiment with a discriminating escape positive control"
  - "NIX-08: $HOME/TMPDIR/etc/locale measured for this project's exact invocation shape, and the locale-dependent-warning-text defect class stated as REPRODUCES"
affects: [65-tox-uv-bare-tox-uv-revert, 68-documentation-follow-through]

actuals:
  tokens: 7817
  tasks: 2
  commits: 3
  plan_head_before: e985c32d3e6cb990a19be9868a4f5a07e71adcf5

tech-stack:
  added: []
  patterns:
    - "Rename-the-target proof with a discriminating positive control (a runnable binary that WOULD print a plausible version if the walk escaped) rather than a bare --version smoke test"
    - "Definitions-before-measurement, enforced by committing the definitions section standalone ahead of any probe run, so a MASKS/INCONCLUSIVE finding cannot be reclassified after seeing the data"

key-files:
  created:
    - .planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-NIX07-RENAME-EVIDENCE.md
    - .planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-NIX08-ENV-EVIDENCE.md
  modified: []

key-decisions:
  - "This worktree's own .venv/bin/python cannot execute directly on the host at all (the identical RED class Phase 64-01 proved for ruff, since uv sync downloaded a manylinux-shaped CPython here rather than reusing the nix-native python3 the main checkout's long-lived venv happens to use). Documented as an unanticipated finding, then resolved with a stated substitution: the main checkout's already-runnable .venv/bin/python (identical sphinx==9.1.0 pin, same uv.lock) serves as the genuine unshimmed host leg for NIX-08's locale mechanics probe and four-cell matrix, since the plan's literal wording assumed a binary that cannot run standalone in a genuinely fresh worktree."
  - "NIX-08's finding is REPRODUCES, not MASKS or INCONCLUSIVE: the control holds (H-ja != H-C) and both through-shim cells match their host counterparts exactly, so the maintainer's existing LC_ALL=C pre-check keeps doing its job unchanged through the shims."

requirements-completed: [NIX-07, NIX-08]

coverage:
  - id: D1
    description: "Every shim resolves by absolute, un-shadowable path and cannot recurse or escape, proven by a rename-the-target experiment (not a --version smoke test) with a discriminating escape positive control, run from a worktree nested in the main checkout"
    requirement: "NIX-07"
    verification:
      - kind: other
        ref: "task 1 automated <verify> block (rename loop + uv leg xtrace + shim-body PATH-lookup-absence assertion), 64-NIX07-RENAME-EVIDENCE.md"
        status: pass
    human_judgment: false
  - id: D2
    description: "uv's two-leg resolution (bounded .venv walk, then the fixed nixpkgs store path), quoting, and nearest-.venv-wins ordering are each proven, including a boundary/encoding/ordering probe outside the repository with a space and non-ASCII path component"
    requirement: "NIX-07"
    verification:
      - kind: other
        ref: "64-NIX07-RENAME-EVIDENCE.md uv leg order and boundary/encoding/ordering probe sections"
        status: pass
    human_judgment: false
  - id: D3
    description: "$HOME, TMPDIR, /etc and the locale are measured host-side and through the shim for this project's exact command-shim-from-an-outer-mkShell invocation shape, each with a one-sentence passthrough statement"
    requirement: "NIX-08"
    verification:
      - kind: other
        ref: "task 2 automated <verify> block (env -u count, HOME match, /tmp stat match), 64-NIX08-ENV-EVIDENCE.md Environment measurement section"
        status: pass
    human_judgment: false
  - id: D4
    description: "The locale-dependent warning-text defect class is measured against definitions committed before any probe ran, via a four-cell H-ja/H-C/S-ja/S-C matrix on a scratch dummy-builder Sphinx project, and stated as exactly one Finding line"
    requirement: "NIX-08"
    verification:
      - kind: other
        ref: "64-NIX08-ENV-EVIDENCE.md Definitions + Four-cell matrix sections; git log -- 64-NIX08-ENV-EVIDENCE.md shows 2 commits, definitions-only then measurements"
        status: pass
    human_judgment: false
  - id: D5
    description: "TestNoLostDiagnostics passes 7/7 through the sphinx-build/pytest shims under both the maintainer's ja_JP.UTF-8 and LC_ALL=C"
    requirement: "NIX-08"
    verification:
      - kind: unit
        ref: "tests/test_state_guard_shapes_gate.py::TestNoLostDiagnostics (7 selected), run twice via the pytest shim"
        status: pass
    human_judgment: false

duration: 13min
completed: 2026-09-11
status: complete
---

# Phase 64 Plan 03: NIX-07 Rename Proof and NIX-08 Environment/Locale Measurement Summary

**The rename-the-target experiment proves every `flake.nix` shim resolves by absolute,
un-shadowable path (a discriminating escape positive control makes a silent fall-through to the
main checkout observable), and a definitions-before-measurement four-cell locale matrix finds the
FHS sandbox REPRODUCES this repository's known locale-dependent warning-text defect class exactly
as the host does.**

## Performance

- **Duration:** 13 min
- **Started:** 2026-09-11T15:17:47Z
- **Completed:** 2026-09-11T15:31:01Z
- **Tasks:** 2
- **Files modified:** 2 (both new evidence files)

## Accomplishments

- **NIX-07 rename proof, from a worktree nested in the main checkout.** All seven shim bodies
  recorded verbatim: each `exec`s through the absolute `typsphinx-fhs-run` path with no
  `command -v`/`which`/bare-name lookup anywhere. The main checkout's own runnable
  `.venv/bin/ruff` (`ruff 0.15.20`, exit 0) is the discriminating positive control — an escape
  past this worktree's `.git` boundary WOULD print a plausible version, not a hang or a crash.
  Seven rename cases (`tox`, `ruff`, `black`, `mypy`, `pytest`, `sphinx-build` from the root, plus
  `ruff` from `docs/`) all exit 127 with exactly one `typsphinx-shim: <tool>:` stderr line, empty
  stdout, and a correctly restored version afterward — no rc 124 hang, no fall-through version
  string.
- **uv's two-leg resolution proven.** With no `.venv/bin/uv`, the xtrace names the fixed nixpkgs
  store path (leg 2). A two-line leg-1 probe script wins from both the worktree root and `docs/`;
  after deletion, leg 2 resolves again.
- **Boundary/encoding/ordering probe outside the repository**, path containing a space and a
  non-ASCII component (`nix07 probe/外側`): the walk stops at an inner `.git` boundary before an
  outer `.venv` is reachable, the nearest `.venv` wins once one exists at the inner level, and the
  path (space + `外側` intact) survives the `exec` chain in `$0` throughout. Scratch tree removed
  and confirmed absent.
- **NIX-08's `## Definitions (written before measuring)` section was committed standalone**,
  before any locale probe ran — `git log` on the evidence file shows exactly the definitions
  commit followed by the measurements commit, satisfying T-64-13's anti-reclassification gate.
- **An unanticipated but significant finding, documented rather than worked around silently:**
  this worktree's own `.venv/bin/python` cannot execute directly on the host at all — the
  identical RED class Phase 64-01 already proved for `ruff` — because a genuinely fresh
  `uv sync --extra dev` downloads uv's own managed CPython (a manylinux-shaped build), unlike the
  main checkout's long-lived venv, which happens to be built against the nix-native `python3` on
  `PATH`. The main checkout's already-runnable `.venv/bin/python` (confirmed identical
  `sphinx==9.1.0` pin) substitutes as the genuine unshimmed host leg for the locale mechanics
  probe and the four-cell matrix's H-ja/H-C cells; `sphinx-build` (S-ja/S-C) is unaffected and
  uses this worktree's own `.venv` throughout.
- **Four-cell locale matrix: REPRODUCES.** H-ja ≠ H-C (the control holds — Japanese vs. English
  `toc.not_included` warning body on the host), and S-ja = H-ja, S-C = H-C exactly. The sandbox
  neither hides nor introduces a divergence in this defect class.
- **`TestNoLostDiagnostics` passes 7/7** through the `pytest` shim under both the maintainer's
  `ja_JP.UTF-8` and a `LC_ALL=C` prefix.
- **D-06's passthrough measured at 0 surviving lines**: `env -u VIRTUAL_ENV -u
  UV_PROJECT_ENVIRONMENT` unsets survive fully into the sandbox. `$HOME`, `TMPDIR` and `/tmp`'s
  device/inode are identical host-side and inside; `/etc` shows the curated `/.host-etc` overlay
  for the security/locale-relevant entries and a handful of FHS-closure-native files for the rest.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — NIX-07 rename proof from a nested worktree, with the escape positive
   control, uv leg order, and the boundary/encoding/ordering probe** - `a23f1b1b` (test)
2. **Task 2: NIX-08 — define reproduces/masks first, then measure $HOME, TMPDIR, /etc, the
   locale and D-06's passthrough, then the four-cell locale matrix** - two commits:
   `82d53891` (docs, definitions-only, committed before any probe) and `0b6cae92` (test, the
   full measurement results)

**Plan metadata:** committed alongside this SUMMARY (see final commit).

## Files Created/Modified

- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-NIX07-RENAME-EVIDENCE.md` -
  Head check/provisioning, all seven shim bodies verbatim, the escape positive control, the seven
  rename cases, uv's two-leg proof, and the outside-repository boundary/encoding/ordering probe.
- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-NIX08-ENV-EVIDENCE.md` -
  Definitions committed ahead of measurement, the documented host-leg substitution finding, the
  full environment measurement ($HOME/TMPDIR/etc/locale/D-06), the four-cell locale matrix with
  its REPRODUCES finding, both `TestNoLostDiagnostics` locale runs, and the Phase 68 consequence
  note.

## Decisions Made

- **Host-leg substitution for NIX-08 (documented, not silent).** This worktree's own
  `.venv/bin/python` cannot run at all on the host; the main checkout's already-runnable
  `.venv/bin/python` (identical `sphinx==9.1.0` pin) was used instead for the H-ja/H-C legs. The
  substitution changes only which CPython build executes Sphinx (not the Sphinx version, and no
  `typsphinx` extension is even invoked by the `-b dummy` scratch build), so the measurement's
  validity is preserved. Recorded prominently in the evidence file before the measurements that
  depend on it, and in this SUMMARY's key-decisions.
- **Finding: REPRODUCES**, derived mechanically from the pre-committed definitions against the
  measured four-cell matrix — the control held and both through-shim cells matched their host
  counterparts exactly. No MASKS or INCONCLUSIVE result was concealed or reclassified.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking, resolved via documented substitution] This worktree's `.venv/bin/python`
cannot execute directly on the host**
- **Found during:** Task 2, step 2 (environment measurement) — attempting the plan's literal
  `.venv/bin/python -c "..."` host-leg probe.
- **Issue:** `.venv/bin/python` in a genuinely fresh worktree is itself a generic-linux ELF
  (uv's own managed CPython download) that NixOS's `stub-ld` refuses to execute — the identical
  defect class Phase 64-01 already proved for `.venv/bin/ruff`. The plan's NIX-08 task assumed
  this binary would run standalone for the "host, unshimmed" leg of both the locale mechanics
  probe and the four-cell matrix.
- **Fix:** Substituted the main checkout's already-runnable `.venv/bin/python` (confirmed
  identical `sphinx==9.1.0` pin via the same `uv.lock`) as the genuine unshimmed host leg. The
  `sphinx-build` shim (S-ja/S-C) is unaffected and continues to use this worktree's own `.venv`
  throughout, matching D-09's genuine invocation shape.
- **Files modified:** none (measurement-only; no code or flake.nix change).
- **Verification:** the substitute's Sphinx version was confirmed identical (`9.1.0`) before use;
  the resulting four-cell matrix cleanly produced a control-holding, mechanically-derived
  REPRODUCES finding, consistent with what a genuinely runnable host leg would have shown.
- **Committed in:** `0b6cae92` (documented in the evidence file itself, ahead of the dependent
  measurements).

---

**Total deviations:** 1 auto-fixed (1 blocking, resolved with a documented, non-silent
substitution). **Impact:** none on scope or correctness — the substitution preserves NIX-08's
actual measurement intent (comparing Sphinx's own locale-dependent behavior host vs. through-shim)
and is transparently recorded rather than hidden. No code, `flake.nix`, or product file was
touched.

## Issues Encountered

None beyond the documented deviation above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

NIX-07 and NIX-08 are both proven and closed by this plan, completing Phase 64's measurement
requirements alongside 64-01's NIX-06 and 64-02's remaining coverage. `flake.nix` itself is
untouched by this plan (evidence-only, per D-05's scope). Phase 65 (`tox-uv-bare` → `tox-uv`
revert) can proceed once Phase 64's wave 2 fully merges — no blockers from this plan. One
observation worth carrying forward for Phase 68 (DOC-19/DOC-20): a genuinely fresh worktree's
`uv sync` downloads a different (uv-managed, non-nix-native) CPython than the main checkout's
long-lived venv happens to use, which is why this worktree's own `.venv/bin/python` cannot run
unshimmed at all — the main checkout's apparent "it just works" status for bare Python execution
is itself an artifact of an old venv, not a general property maintainers should rely on.

## Self-Check: PASSED

- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-NIX07-RENAME-EVIDENCE.md` — FOUND
- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-NIX08-ENV-EVIDENCE.md` — FOUND
- Commit `a23f1b1b` (Task 1) — FOUND in `git log --oneline --all`
- Commit `82d53891` (Task 2, definitions) — FOUND in `git log --oneline --all`
- Commit `0b6cae92` (Task 2, measurements) — FOUND in `git log --oneline --all`
- Both tasks' automated `<verify>` blocks re-ran clean; the plan-level `<verification>` block's
  four items all confirmed above (rename proof + positive control; boundary/encoding/ordering
  probe cleaned up; NIX-08 definitions precede measurement in `git log` with exactly one
  `**Finding:**` line; D-06's `env -u` passthrough measured at 0 surviving lines, no full
  environment values recorded).

---
*Phase: 64-fhs-wrapper-and-command-shims-in-flake-nix*
*Plan: 03*
*Completed: 2026-09-11*
