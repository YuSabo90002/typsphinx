---
phase: 64-fhs-wrapper-and-command-shims-in-flake-nix
plan: 01
subsystem: infra
tags: [nix, flake, buildFHSEnv, bubblewrap, devShell, NixOS, worktree]

requires: []
provides:
  - "One Linux-guarded pkgs.buildFHSEnv passthrough (typsphinx-fhs-run) in flake.nix"
  - "Seven D-01 command shims (uv, tox, ruff, black, mypy, pytest, sphinx-build) on the Linux devShell PATH"
  - "The bounded upward .venv walk (venvWalk) stopping at the first .git ancestor"
  - "D-02's uv two-leg resolution (venv walk, then fixed pkgs.uv store path)"
  - "64-FLAKE-EVIDENCE.md: RED, tracer GREEN, roster diagnostics, tox shakeout, D-07, NIX-06 all-systems"
affects: [65-tox-uv-bare-tox-uv-revert, 68-documentation-follow-through]

actuals:
  tokens: 6004
  tasks: 3
  commits: 3
  plan_head_before: 3e6df794dd001e37a103a664e48ef1b5369cbc12

tech-stack:
  added: []
  patterns:
    - "pkgs.steam-run idiom: one buildFHSEnv passthrough + N thin writeShellScriptBin shims"
    - "Bounded upward .venv walk stopping at the first ancestor holding .git, surviving tox's changedir=docs"
    - "Strict shim (no fallback, D-03) vs. uv's sole two-leg exception (D-02)"

key-files:
  created:
    - .planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-FLAKE-EVIDENCE.md
  modified:
    - flake.nix

key-decisions:
  - "The uv shim's leg-2 fixed pkgs.uv store path was accepted as documented debt (D-02); it drops once Phase 65 makes .venv/bin/uv always exist."
  - "No flake.nix fix was needed for the nested tox->uv-shim entry or for D-07's docs-pdf: both passed cleanly on the first attempt against the warm @preview cache, so pkgs.cacert was not added."

requirements-completed: [NIX-06]

coverage:
  - id: D1
    description: "One Linux-guarded pkgs.buildFHSEnv passthrough (typsphinx-fhs-run) added to flake.nix, reached only via pkgs.lib.optionals pkgs.stdenv.hostPlatform.isLinux"
    requirement: "NIX-06"
    verification:
      - kind: other
        ref: "nix flake check --all-systems --no-build (64-FLAKE-EVIDENCE.md NIX-06 section)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Seven D-01 command shims (uv, tox, ruff, black, mypy, pytest, sphinx-build) resolve by absolute path through the sandbox; six strict (D-03), uv two-leg (D-02)"
    verification:
      - kind: other
        ref: "xtrace + exec resolution transcripts, all seven names (64-FLAKE-EVIDENCE.md Roster expansion section)"
        status: pass
    human_judgment: false
  - id: D3
    description: "tox's own subprocess tree (nested sandbox entry via tox-uv-bare's PATH lookup of uv) and docs-pdf's font/preview-package resolution both run through the sandbox"
    verification:
      - kind: other
        ref: "tox -e lint (lint: OK) and tox -e docs-pdf (%PDF magic bytes) transcripts, 64-FLAKE-EVIDENCE.md"
        status: pass
    human_judgment: false
  - id: D4
    description: "The flake evaluates on all four declared systems with both darwin devShells byte-identical to the pre-edit baseline"
    requirement: "NIX-06"
    verification:
      - kind: other
        ref: "nix eval --raw .#devShells.<sys>.default.drvPath, all four systems (64-FLAKE-EVIDENCE.md NIX-06 section)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Darwin execution (as opposed to evaluation) is unverified by construction, and this plan's own session cannot observe the D-09 session-inheritance shape -- both require a maintainer action outside this plan's control"
    human_judgment: true
    rationale: "No darwin machine is available to this phase (ROADMAP constraint 8), and the D-09 session-PATH-inheritance shape can only be observed by a session launched after this plan's flake.nix edit reaches the main checkout -- neither is something this worktree-isolated plan can measure or auto-pass."

duration: 45min
completed: 2026-09-11
status: complete
---

## Session relaunch required before wave 2

The Claude Code session that ran this plan predates the `flake.nix` edit, and its PATH carries no
shim (orchestrator note 3) — every shim invocation recorded in `64-FLAKE-EVIDENCE.md` was routed
through `nix develop . --command …` and labelled DIAGNOSTIC for exactly this reason.

After this plan merges into the main checkout, the maintainer should open a terminal in
`/home/yuta/Documents/typsphinx` so direnv re-evaluates the flake. The maintainer then confirms
that `command -v ruff` prints a `/nix/store/…-ruff/bin/ruff` path, launches Claude Code from that
same shell, and re-runs `/gsd-execute-phase 64`.

Plans 64-02 and 64-03 carry a precondition that halts otherwise. No per-worktree `direnv allow` and
no `nix develop --command` wrapper around the provisioning line is involved; D-09 rejects both.

# Phase 64 Plan 01: FHS Wrapper and Command Shims — Foundation Summary

**One Linux-guarded `pkgs.buildFHSEnv` passthrough plus seven `writeShellScriptBin` command shims
(`uv`, `tox`, `ruff`, `black`, `mypy`, `pytest`, `sphinx-build`) added to `flake.nix`, proven by a
RED-then-GREEN tracer, a full roster diagnostic, tox's own subprocess tree through a nested sandbox
entry, a real PDF via `docs-pdf`, and `nix flake check --all-systems` with both darwin devShells
byte-identical to the pre-edit baseline.**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-09-11T14:57:03Z
- **Tasks:** 3
- **Files modified:** 2 (`flake.nix`, `64-FLAKE-EVIDENCE.md`)

## Accomplishments

- RED reproduced exactly at the D-04 locus (a freshly provisioned worktree): `.venv/bin/ruff
  --version` fails with the stub-ld rejection at rc 127, matching `file .venv/bin/ruff`'s report of a
  generic-linux dynamically-linked ELF.
- A single tracer shim (`ruff`) proved the mechanism end to end: shim → `typsphinx-fhs-run` (the
  `pkgs.buildFHSEnv` passthrough, `runScript = exec "$@"`) → this worktree's own `.venv/bin/ruff`,
  printing `ruff 0.15.20` from both the worktree root and `docs/` (surviving `tox.ini`'s `changedir
  = docs`), with the xtrace `+ exec` line naming the worktree's absolute `.venv/bin/ruff` path — no
  bare-name lookup, no self-recursion.
- Expanded to the full D-01 seven-name roster: `venvShimNames` maps six strict shims (`tox`, `ruff`,
  `black`, `mypy`, `pytest`, `sphinx-build`, D-03's no-fallback contract) over `venvWalk`, plus
  `uvShim` (D-02's sole two-leg exception — `.venv/bin/uv` walk, then the fixed `${pkgs.uv}` store
  path since `.venv/bin/uv` does not exist until Phase 65). All seven resolved by absolute path with
  versions matching `uv.lock`'s pins exactly; `type -P uv` confirmed the shim is the sole `uv`
  provider on the Linux devShell PATH (the NIX-06 ordering edge).
- Proved the design against tox's real subprocess tree: `tox -e lint` ran inside the sandbox,
  `tox-uv-bare` resolved `uv` from PATH to the shim, which re-entered the sandbox a second time (a
  nested entry) — passed cleanly (`lint: OK`) on the first attempt, no `flake.nix` fix needed.
  `tox -e docs-pdf` produced a real PDF (`%PDF` magic bytes) against the already-warm
  `~/.cache/typst/packages/preview` cache; the cold-cache TLS path stayed unexercised, so
  `pkgs.cacert` was not added (D-07 closed with no gap found).
- `nix flake check --all-systems --no-build` and `nix flake show --all-systems` both exit 0 on the
  final `flake.nix`. Both darwin `devShells.<sys>.default.drvPath` values are byte-identical to the
  pre-edit baseline (`fclfls55m9lp06679x7zrw0qzjya834j-nix-shell.drv`,
  `2m6y6pshri0vyw3jb5agczjnz9a92sxc-nix-shell.drv`) and to the planning-time record; both Linux
  drvPaths changed. The `x86_64-linux` package census reads exactly the eleven-name array
  (`nodejs-24.16.0, pnpm-11.9.0, git-2.54.0, python3-3.13.13, uv, tox, ruff, black, mypy, pytest,
  sphinx-build`); both darwin censuses are unchanged, byte-for-byte.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — ruff RED in a fresh worktree, then one ruff shim through one FHS passthrough,
   GREEN from the root and from docs/** - `493a0b82` (feat)
2. **Task 2: Expand to the full seven-name roster — uv's two legs, five more strict venv shims,
   nixpkgs uv dropped from the Linux list** - `350108b7` (feat)
3. **Task 3: Prove the final flake — tox's subprocess tree through the sandbox (nested entry, D-07),
   all four systems evaluate, darwin byte-identical** - `26e53041` (test)

**Plan metadata:** committed alongside this SUMMARY (see final commit).

## Files Created/Modified

- `flake.nix` - Adds `fhsRun` (`pkgs.buildFHSEnv` named `typsphinx-fhs-run`, `exec "$@"`
  passthrough), `venvWalk` (bounded upward `.venv` walk), `venvShimOnStop` (D-03's stderr message +
  `exit 127`), `venvShimNames`/`venvShims` (the six strict shims), `uvShim` (D-02's two-leg
  exception). `packages` on Linux becomes `[uvShim] ++ venvShims`; darwin keeps
  `nodejs, pnpm, git, python3, uv` unconditionally via a matching `optionals (!isLinux)` branch.
- `.planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-FLAKE-EVIDENCE.md` - RED,
  pre-edit baselines (four drvPaths, two censuses), tracer GREEN (DIAGNOSTIC), roster expansion
  (DIAGNOSTIC, all seven names), tox subprocess-tree shakeout (DIAGNOSTIC), D-07, and NIX-06 across
  all four systems, closing with the session-relaunch instruction for wave 2.

## Decisions Made

- **D-02's `uv` two-leg exception was implemented exactly as scoped**: the `.venv/bin/uv` walk is
  identical machinery to the six strict shims (`venvWalk`'s own bounded loop); only the on-stop
  fragment differs — `uvShim` execs the fixed `${pkgs.uv}/bin/uv` store path instead of printing
  D-03's not-found message. This is accepted debt: the fallback leg drops once Phase 65 makes
  `.venv/bin/uv` always present.
- **No `flake.nix` fix was needed for the nested-entry or D-07 shakeout tasks.** Both `tox -e lint`
  (nested `tox` → `uv` shim entry) and `tox -e docs-pdf` (warm `@preview` cache) passed cleanly on
  the first attempt, so `pkgs.cacert` was not added to `fhsRun`'s `targetPkgs` — D-07's
  investigation found no TLS gap, only an unexercised path.
- **Dropped `pkgs.uv` from the Linux `packages` list** (the discretion item, taken as recommended):
  the Linux branch is exactly `[uvShim] ++ venvShims`, with no unconditional `pkgs.uv` alongside it,
  so exactly one `uv` provider exists on the Linux devShell PATH — confirmed via `type -P uv`.

## Deviations from Plan

None - plan executed exactly as written. All three tasks' automated `<verify>` blocks passed on the
first run with no fix-forward needed; no Rule 1-3 auto-fix, no Rule 4 architectural question, no
auth gate.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required. The one action required before wave 2 is the
Claude Code session relaunch documented above and in `64-FLAKE-EVIDENCE.md`, which is a maintainer
procedural step, not an external service.

## Next Phase Readiness

`flake.nix` carries the full D-01 seven-name shim roster and evaluates cleanly on all four declared
systems with darwin unchanged. NIX-06 is proven and closed by this plan; NIX-01 and NIX-07 are
proven by plans 64-02 and 64-03 in the genuine D-09 session-inheritance shape, not by this plan's
`nix develop --command` diagnostics — those plans carry a precondition that halts until the
Claude Code session relaunch above has happened. No blockers; the only concern is procedural (the
relaunch itself must actually occur before wave 2 is dispatched).

---
*Phase: 64-fhs-wrapper-and-command-shims-in-flake-nix*
*Plan: 01*
*Completed: 2026-09-11*
