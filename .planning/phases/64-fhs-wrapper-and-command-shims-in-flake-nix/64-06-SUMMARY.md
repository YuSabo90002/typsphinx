---
phase: 64-fhs-wrapper-and-command-shims-in-flake-nix
plan: 06
subsystem: infra
tags: [nix, flake, buildFHSEnv, tox, pytest, ruff, docs-pdf, gap-closure]

requires:
  - phase: 64 (waves 1-4, plans 01-05)
    provides: the FHS wrapper, seven command shims, and the targetPkgs = p.zlib fix that resolved
      libz.so.1 for uv-managed CPython's Pillow import
provides:
  - "genuine D-09 shape re-measurement of NIX-02, NIX-03 and NIX-04 in a session relaunched after
    64-05 merged — the observations 64-VERIFICATION.md's three gaps required"
  - "NIX-01 regression re-confirmed (ruff 0.15.20), and the exact node that failed in 64-02
    (test_converted_image_collision_render_gate.py) now passing 3/3 through the bare pytest shim"
  - "one full NIX-04 suite run: 1543 passed, 5 skipped (1548 collected) — exact baseline match, the
    Pillow-gated skip confirmed gone"
  - "all seven tox environments (lint, type, py312, py313, cov, docs-html, docs-pdf) OK cold in the
    fixed sandbox; docs-pdf produced a real, non-empty %PDF PDF"
  - "genuine residual audit over every environment this plan provisioned: GENUINE =
    {libcrypt.so.1, libtcl9.0.so, libtcl9tk9.0.so}, no libz.so.1, every soname cites its 64-05
    verdict"
  - "## Requirement closure: NIX-01 through NIX-05 all MET"
affects: [65]

actuals:
  tokens: 6185
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns: ["genuine-shape re-measurement gated by a session-relaunch precondition (halt at
    blocking-human if the discriminator is false, never silently degrade to a diagnostic run)"]

key-files:
  created:
    - .planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-GAP-REMEASURE-EVIDENCE.md
  modified: []

key-decisions:
  - "The session-relaunch precondition (libz.so.1 present in the ruff shim's embedded rootfs,
    matching the New fhs-run: line) was verified true before any task ran — this is the relaunched
    session, so every observation in this evidence is genuine D-09 shape, not a nix develop
    DIAGNOSTIC."
  - "No flake.nix edit was needed or made: the genuine residual audit found the same three
    UNREACHED/FORCED-in-letter-only sonames 64-05 already dispositioned (libcrypt.so.1,
    libtcl9.0.so, libtcl9tk9.0.so), and no step-3 gate failed on any of them."
  - "D-07's @preview cache count stayed unchanged (9 before, 9 after) — the warm cache served
    docs-pdf without needing network access from inside the sandbox."

requirements-completed: [NIX-01, NIX-02, NIX-03, NIX-04, NIX-05]

coverage:
  - id: D1
    description: "Session-relaunch precondition confirmed, D-09 head check (fresh worktree,
      .venv/.tox absent, all seven command -v paths matching 64-05's New shim paths table),
      one-line provisioning, NIX-01 regression (ruff 0.15.20, exec xtrace inside this worktree,
      ruff check . clean), and the tracer (PIL._imaging import + the exact 64-02 failing node
      passing 3/3)"
    requirement: NIX-01
    verification:
      - kind: integration
        ref: "64-GAP-REMEASURE-EVIDENCE.md#NIX-01 — ruff (regression) — ruff --version, ruff check ."
        status: pass
      - kind: integration
        ref: "64-GAP-REMEASURE-EVIDENCE.md#Tracer — the path that failed in 64-02 — pytest tests/test_converted_image_collision_render_gate.py -q -rs, 3 passed"
        status: pass
    human_judgment: false
  - id: D2
    description: "NIX-04: one full-suite run through the bare pytest shim under the maintainer
      locale, no locale variable set — collected 1548, 1543 passed/5 skipped exactly matching the
      carried-in baseline, every skip itemised, Pillow-gated skip confirmed gone"
    requirement: NIX-04
    verification:
      - kind: integration
        ref: "64-GAP-REMEASURE-EVIDENCE.md#NIX-04 — full suite (one run, maintainer locale) — pytest -q -rs"
        status: pass
    human_judgment: false
  - id: D3
    description: "NIX-02: four tox environments (lint, type, py312, py313) provisioned cold in the
      fixed sandbox, each ending <env>: OK, py312/py313 reproducing the baseline under their own
      interpreters"
    requirement: NIX-02
    verification:
      - kind: integration
        ref: "64-GAP-REMEASURE-EVIDENCE.md#NIX-02 — four tox environments, cold in the fixed sandbox"
        status: pass
    human_judgment: false
  - id: D4
    description: "NIX-03: cov/docs-html/docs-pdf all OK, each docs build preceded by rm -rf
      docs/_build, warning counts matching the 3/5 baseline exactly, docs-pdf producing a real
      non-empty %PDF PDF (2776960 bytes), @preview cache count unchanged (D-07)"
    requirement: NIX-03
    verification:
      - kind: integration
        ref: "64-GAP-REMEASURE-EVIDENCE.md#NIX-03 — cov, docs-html, docs-pdf, real PDF"
        status: pass
    human_judgment: false
  - id: D5
    description: "Genuine residual audit over 1974 objects across every environment this plan
      provisioned (GENUINE = {libcrypt.so.1, libtcl9.0.so, libtcl9tk9.0.so}, no libz.so.1, every
      soname cites its 64-05 verdict), NIX-05 procedure summary, no-dispatch record, and the
      Requirement closure table (NIX-01..NIX-05 all MET)"
    requirement: NIX-05
    verification:
      - kind: other
        ref: "64-GAP-REMEASURE-EVIDENCE.md#Genuine residual audit and #Requirement closure"
        status: pass
    human_judgment: false

duration: 62min
completed: 2026-09-12
status: complete
---

# Phase 64 Plan 06: Gap Re-Measurement (NIX-02/03/04) Summary

**All five NixOS requirements (NIX-01 through NIX-05) re-measured MET in a session genuinely relaunched after 64-05's `targetPkgs = p.zlib` fix — full suite, all seven tox environments, and a real docs-pdf PDF, all clean.**

## Performance

- **Duration:** 62 min
- **Started:** 2026-09-12T04:37:55Z
- **Completed:** 2026-09-12T05:40:00Z (approx.)
- **Tasks:** 3
- **Files modified:** 1 (`64-GAP-REMEASURE-EVIDENCE.md`, created)

## Accomplishments

- Confirmed the session-relaunch precondition true before doing any work: the `ruff` shim's
  embedded rootfs carries `/usr/lib/libz.so.1` and its store hash
  (`99fm4lqkp4kab20d3blfbwajnprmlbfx`) matches the `New fhs-run:` line 64-05 recorded — this is the
  genuine D-09 shape, not a `nix develop` diagnostic.
- Re-confirmed NIX-01: `ruff --version` prints `ruff 0.15.20`, the shim's exec xtrace names this
  worktree's own `.venv/bin/ruff`, and `ruff check .` passes clean.
- Re-ran the exact node that failed in 64-02 (`test_converted_image_collision_render_gate.py`) —
  now 3 passed, 0 failed — and the `PIL._imaging` `-S` import probe printed `OK`.
- Ran the full 1548-test suite once, no locale variable, and matched the carried-in baseline
  exactly: `1543 passed, 5 skipped`, with the previously Pillow-gated skip confirmed gone.
- Ran all seven tox environments (`lint`, `type`, `py312`, `py313`, `cov`, `docs-html`,
  `docs-pdf`) cold in the fixed sandbox — every one ended `OK`; `docs-html`/`docs-pdf` matched the
  3/5 warning baseline exactly, and `docs-pdf` produced a real 2,776,960-byte `%PDF`-prefixed PDF.
- Ran the genuine residual audit over every environment this plan actually provisioned (1974
  objects) — `GENUINE = {libcrypt.so.1, libtcl9.0.so, libtcl9tk9.0.so}`, no `libz.so.1`, every
  soname citing its existing 64-05 verdict.
- Closed the loop: `## Requirement closure` reads MET for NIX-01 through NIX-05.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — relaunched-session check, D-09 head check, provisioning, NIX-01 regression,
   64-02 tracer** - `2ba1d4c5` (fix)
2. **Task 2: NIX-04 — one full-suite run, baseline matched exactly, Pillow skip gone** -
   `7e1d323f` (test)
3. **Task 3: NIX-02/NIX-03 — seven tox environments cold, real PDF, genuine residual audit,
   requirement closure** - `bbb05ba1` (docs)

## Files Created/Modified

- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-GAP-REMEASURE-EVIDENCE.md` -
  the full genuine-shape re-measurement: session check, D-09 head check, provisioning/interpreter
  provenance, NIX-01, tracer, NIX-04 full suite, NIX-02/NIX-03 tox environments with a real PDF,
  genuine residual audit, NIX-05 procedure summary, no-dispatch record, and the requirement
  closure table.

## Decisions Made

- The session-relaunch precondition (D-09 discriminator: `libz.so.1` present in the shim's
  embedded rootfs, matching the `New fhs-run:` line) was verified true before any provisioning —
  per the plan's design, a false result would have halted at a `blocking-human` gate instead.
- No `flake.nix` edit was made or needed: the genuine residual audit reproduced the exact same
  three dispositioned sonames from 64-05 (`libcrypt.so.1`, `libtcl9.0.so`, `libtcl9tk9.0.so`), and
  no step-3 gate (full suite, `tox -e py312`, `tox -e cov`, `tox -e lint`, `tox -e type`,
  `tox -e py313`, `tox -e docs-html`, `tox -e docs-pdf`) failed on any of them.
- The interpreter-provenance divergence (this worktree's `.venv` is uv-managed cpython-3.14 vs.
  the `1543 passed, 5 skipped` baseline's nix python3-3.13.13) was recorded as an assumption per
  the plan's flagged edge-probe section, not normalised away — both interpreters (and `.tox/py312`'s
  uv cpython-3.12, and `.tox/py313`'s nix python3-3.13.13) produced the identical summary.

## Deviations from Plan

None - plan executed exactly as written. The session-relaunch precondition was true on the first
check, so no `blocking-human` halt occurred, and no `flake.nix` edit was forced by any gate.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None - this plan produced only an evidence markdown file; no code, no stub, no placeholder.

## Self-Check: PASSED

- `64-GAP-REMEASURE-EVIDENCE.md` exists on disk: FOUND
- Commit `2ba1d4c5` exists in `git log --oneline --all`: FOUND
- Commit `7e1d323f` exists in `git log --oneline --all`: FOUND
- Commit `bbb05ba1` exists in `git log --oneline --all`: FOUND
- Re-ran all three tasks' `<automated>` verify checks live (split into individual commands per the
  worktree-isolation guard's constraints): all passed — session/rootfs checks, `ruff` version and
  exec xtrace, `ruff check .`, the `PIL._imaging` probe, the 64-02 node, `pytest --collect-only`
  (`1548 tests collected`), the greyscale-pipeline skip absence, `tox -e lint`, `tox -e py312 --
  tests/test_converted_image_collision_render_gate.py`, a fresh `rm -rf docs/_build && tox -e
  docs-pdf` (PDF re-generated, `%PDF`, 5 warnings), and `git status --porcelain` over every
  scope-fenced path returning empty.
- Re-ran the plan-level `<verification>` claims: session/head/provisioning/gates ran in that order
  in one fresh nested worktree in the genuine D-09 shape; `ruff 0.15.20` confirmed; the 64-02 node
  passes; the full suite reads `1543 passed, 5 skipped`; all seven tox environments read `OK`; the
  PDF begins `%PDF`; the genuine residual set carries no `libz.so.1`; `## Requirement closure`
  reads `MET` for NIX-01 through NIX-05; `git status --porcelain` over the scope-fenced paths is
  empty.

## Next Phase Readiness

- Phase 64's five NixOS requirements measured by this plan (NIX-01, NIX-02, NIX-03, NIX-04,
  NIX-05) are all MET, alongside NIX-06/NIX-07/NIX-08 already closed by 64-05. All eight NIX-*
  requirements are now measured MET; per this project's standing rule (commit `4e130c80`), the
  REQUIREMENTS.md checkboxes stay unchecked until the phase completes — the orchestrator flips them
  centrally.
- No `flake.nix` change is outstanding from this plan. Phase 65 (`tox-uv-bare` → `tox-uv` revert)
  can proceed once Phase 64 is closed, per the ROADMAP's 64 → 65 hard ordering.
- No push and no CI dispatch occurred in this plan (no workflow references `nix`/`flake`); the
  pre-revert CI baseline recorded in `64-CI-EVIDENCE.md` remains what Phase 65's TOX-04 compares
  against.

---
*Phase: 64-fhs-wrapper-and-command-shims-in-flake-nix*
*Completed: 2026-09-12*
