---
phase: 64-fhs-wrapper-and-command-shims-in-flake-nix
verified: 2026-09-12T14:30:00Z
status: passed
score: 9/9 must-haves verified
covered_files:
  - ".planning/REQUIREMENTS.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-01-PLAN.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-01-SUMMARY.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-02-PLAN.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-02-SUMMARY.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-03-PLAN.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-03-SUMMARY.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-04-PLAN.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-04-SUMMARY.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-05-PLAN.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-05-SUMMARY.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-06-PLAN.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-06-SUMMARY.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-CI-EVIDENCE.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-FLAKE-EVIDENCE.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-GAP-REMEASURE-EVIDENCE.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-LIBZ-DIAGNOSIS.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-LIBZ-FIX-EVIDENCE.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-NIX05-WORKTREE-EVIDENCE.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-NIX07-RENAME-EVIDENCE.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-NIX08-ENV-EVIDENCE.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-REVIEW.md"
  - "flake.nix"
covered_digest: "v1:sha256:01ae6bbd4425a6b82048690a3a87192bcfaefc6979cc1fb89f5c674cfb8481d2"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 6/9
  gaps_closed:
    - "NIX-02: tox -e lint, tox -e type, tox -e py312 and tox -e py313 each run to completion"
    - "NIX-03: tox -e cov, tox -e docs-html and tox -e docs-pdf each run to completion, with docs-pdf producing a real PDF"
    - "NIX-04: the full test suite (1548 tests at milestone start) runs on that machine with no environment-caused failures"
  gaps_remaining: []
  regressions: []
advisory: []
---

# Phase 64: FHS Wrapper and Command Shims in `flake.nix` Verification Report

**Phase Goal:** Every documented bare command and every tox environment runs to completion on the
maintainer's NixOS machine through Linux-guarded `buildFHSEnv` shims that resolve the project's own
`.venv` binaries by absolute path, with the sandbox's environment behaviour measured rather than
assumed.

**Verified:** 2026-09-12
**Status:** passed
**Re-verification:** Yes — after gap closure (plans 64-05, 64-06)

## Goal Achievement

This is a re-verification of the prior `gaps_found` (6/9) report. That report's three gaps —
NIX-02, NIX-03, NIX-04, all traced to a single root cause (`libz.so.1` missing inside the FHS
rootfs for `uv`-managed CPython builds importing Pillow's `_imaging`) — were closed by two
gap-closure plans, and this pass re-measures every one of the nine truths from the codebase, not
from either plan's own SUMMARY narrative.

**64-05** added exactly one `targetPkgs = p: [ p.zlib ];` line to `fhsRun` in `flake.nix`, backed by
a RED (old rootfs fails)/GREEN (new rootfs succeeds) tracer across all three interpreter builds and
a BEFORE/AFTER ELF-`DT_NEEDED` residual audit. Per the phase's own binding rule, 64-05 ran in a
session that predated its own edit, so every post-edit observation in that plan is explicitly
labelled DIAGNOSTIC and does **not** count as closing NIX-02/03/04 — the plan says so itself, and
this verifier holds that line rather than accepting a diagnostic run as genuine evidence.

**64-06** is the genuine closure: it ran only after a session relaunch (its own precondition halts
otherwise), proved the relaunch was real via a `libz.so.1`-presence discriminator matching 64-05's
recorded `New fhs-run:` store path, then re-ran everything — NIX-01 regression, the exact node that
failed in 64-02, one full-suite run (`1543 passed, 5 skipped`, exact baseline match, the
previously-Pillow-gated skip confirmed gone), and all seven tox environments cold, including a real
`%PDF`-prefixed `docs-pdf` output. `64-GAP-REMEASURE-EVIDENCE.md`'s own `## Requirement closure`
table reads MET for NIX-01 through NIX-05.

Independent re-measurement in this verification session (not merely re-reading the evidence files)
confirms the shipped state: the main checkout's `ruff` shim embeds the exact `99fm4lqk…` rootfs
64-06 measured, `"$FHS" /bin/sh -c 'test -e /usr/lib/libz.so.1'` exits 0, all seven `command -v`
paths match the `New shim paths` table byte for byte, `ruff check .` and the previously-failing
`test_converted_image_collision_render_gate.py` node both pass live on the main tree post-merge,
`nix flake check --all-systems --no-build` exits 0 with both darwin drvPaths byte-identical to the
pre-edit baseline, and `git status --porcelain` / the commit log confirm `flake.nix`'s only change
since the prior verification is the one `targetPkgs` line plus its comment.

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | NIX-01: `ruff check .` and the other documented bare commands (`pytest`, `black --check .`, `mypy typsphinx/`, `sphinx-build`) run to completion out of the project's own `.venv`, `ruff` reporting exactly `0.15.20` | ✓ VERIFIED | `64-GAP-REMEASURE-EVIDENCE.md` § NIX-01: `ruff --version` → `ruff 0.15.20` (matches `uv.lock:1209-1210`), exec xtrace names this worktree's own `.venv/bin/ruff`, `ruff check .` → `All checks passed!`. Independently re-confirmed live in this session on the main checkout post-merge: `ruff 0.15.20`, `ruff check .` → `All checks passed!` |
| 2 | NIX-02: `tox -e lint`, `-e type`, `-e py312` and `-e py313` each run to completion | ✓ VERIFIED | `64-GAP-REMEASURE-EVIDENCE.md` § NIX-02, genuine D-09 shape (session relaunched after 64-05): all four environments end `<env>: OK`; `py312` header names `Python 3.12.13`, summary `1543 passed, 5 skipped`; `py313` matches identically; each `venv>` line names the new `uv` shim path; `.tox` absent before the first run (cold provisioning) |
| 3 | NIX-03: `tox -e cov`, `-e docs-html` and `-e docs-pdf` each run to completion, `docs-pdf` producing a real PDF | ✓ VERIFIED | `64-GAP-REMEASURE-EVIDENCE.md` § NIX-03: `cov: OK` (`TOTAL 2806 333 88%`, `1543 passed, 5 skipped`); `docs-html: OK` (3 warnings, exact baseline match, clean build); `docs-pdf: OK` (5 warnings, exact baseline match, clean build) with a real, non-empty PDF (2,776,960 bytes, begins `%PDF`); `@preview` cache count unchanged (9 before/after) |
| 4 | NIX-04: the full test suite runs with no environment-caused failures | ✓ VERIFIED | `64-GAP-REMEASURE-EVIDENCE.md` § NIX-04: one full-suite run, no locale variable set, `collected 1548 items`, summary exactly `1543 passed, 5 skipped` — the carried-in baseline byte-for-byte; all 5 skips itemised with verbatim reasons; the previously Pillow-gated 6th skip confirmed absent. Independently spot-checked live in this session on the main checkout: the previously-failing node `test_converted_image_collision_render_gate.py` passes `3 passed` through the shim |
| 5 | NIX-05: an executor in a freshly created git worktree can run the documented provisioning line and then every gate, with no manual `ln -sf` or `patchelf` step anywhere | ✓ VERIFIED | `64-GAP-REMEASURE-EVIDENCE.md` § D-09 head check + § NIX-05 procedure summary: `.venv`/`.tox` absent pre-provisioning; all seven `command -v` paths equal 64-05's `New shim paths` table, reached by pure session-PATH inheritance (no per-worktree `direnv allow`); single documented `env -u … uv sync --extra dev` line provisions; `typsphinx.__file__` resolves inside the worktree (tree-identity proof); no symlink or ELF-patch step appears anywhere |
| 6 | NIX-06: `flake.nix` evaluates successfully on all four declared systems, including both darwin ones, unchanged | ✓ VERIFIED | `64-LIBZ-FIX-EVIDENCE.md` § NIX-06 (final flake): `nix flake check --all-systems --no-build` exits 0; darwin drvPaths `fclfls55m9lp06679x7zrw0qzjya834j-nix-shell.drv` (x86_64) and `2m6y6pshri0vyw3jb5agczjnz9a92sxc-nix-shell.drv` (aarch64) unchanged from the pre-edit baseline; x86_64-linux census unchanged (11-name array). Independently re-run live in this session: `nix flake check --all-systems --no-build` exits 0, both darwin drvPaths byte-identical to the recorded values |
| 7 | NIX-07: each shim resolves its target by absolute path and cannot recurse into itself, proven by a check that would catch bare-name resolution | ✓ VERIFIED | `64-NIX07-RENAME-EVIDENCE.md` (unchanged since prior verification, no regression per `git log --since` check): all seven shim bodies contain no `command -v`/`which`/PATH lookup; rename test with a discriminating escape positive control, all six venv-shim rename cases exit 127. `64-LIBZ-FIX-EVIDENCE.md` § NIX-07 carry-over re-proves the seven shim bodies are byte-identical modulo the rootfs path on the final flake |
| 8 | NIX-08: the FHS sandbox's `$HOME`, `/etc` and locale behaviour is measured for this project's actual invocation, and its effect on the known locale-dependent test class is recorded | ✓ VERIFIED | `64-NIX08-ENV-EVIDENCE.md` (unchanged since prior verification): four-cell H-ja/H-C/S-ja/S-C matrix, `**Finding:** REPRODUCES`. `64-LIBZ-FIX-EVIDENCE.md` § NIX-08 carry-over re-proves `/etc/profile` byte-identical and the D-06 passthrough count still 0 on the final flake |
| 9 | SC#5: the milestone branch is on `origin` with a completed 3-OS CI run, the pre-revert baseline for Phase 65 | ✓ VERIFIED | `64-CI-EVIDENCE.md` (unchanged since prior verification): canonical branch pushed with tracking, run `34618719267` `status: completed`, `conclusion: success`, 12/12 jobs green. Independently re-confirmed live: `gh run list` shows the same run `completed`/`success`; no `.github/workflows/` file references `nix`/`flake`, so no push or CI dispatch was needed or made by the gap-closure plans, and this baseline is unaffected by them |

**Score:** 9/9 truths verified (0 present-but-behavior-unverified, 0 failed)

### Deferred Items

None — all nine truths are met within this phase; no item was pushed to a later milestone phase.

### Advisory (New Scope, Unevidenced)

The re-verification evidence gate (Step 7c) applies here since this is a re-verification pass.
`64-REVIEW.md` (re-run same session as this verification) reports 0 critical, 1 warning (WR-01), 3
info (IN-01, IN-02, IN-03). None of these rises to a 🛑 Blocker:

- **WR-01** (cold-`@preview`-cache TLS path unverified) is a tracked, deliberate deferral per
  `64-CONTEXT.md` D-07 ("add `cacert` only if a cold cache turns out to need TLS") — the condition
  never fired in either gap-closure plan (warm cache measured 9 packages before and after
  `docs-pdf` in `64-06`). This is not a new-scope finding; it is the same open item the prior
  review already carried, explicitly out of this phase's forced-fix rule.
- **IN-01, IN-02** are unchanged, info-level, no failing gate — carried over verbatim from the
  prior review.
- **IN-03** (new: the `targetPkgs` comment cites a phase-scoped evidence filename rather than a
  durable decision ID) is new-scope but info-level, with no failing test or reproducible defect
  behind it — not deterministic evidence per the Step 7c gate. It does not block and is recorded
  here for visibility only.

| # | Finding | Category | Why Advisory |
|---|---------|----------|--------------|
| 1 | `flake.nix`'s `targetPkgs` justifying comment names a phase-scoped evidence filename (`64-LIBZ-FIX-EVIDENCE.md`) instead of a durable decision ID, unlike every other planning-derived comment in the file | architectural (documentation durability) | info-level, no failing test or reproducible defect; a stylistic-consistency observation, not a functional gap |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `flake.nix` | `fhsRun` carries `targetPkgs = p: [ p.zlib ];`, plus the pre-existing wrapper/shim logic, unchanged otherwise | ✓ VERIFIED | Read directly: line 31 `targetPkgs = p: [ p.zlib ];` inside `fhsRun`, with an explanatory comment; `venvWalk`, `venvShimNames`, `uvShim`, `packages`/isLinux guard all textually unchanged from the prior verification pass |
| `64-LIBZ-FIX-EVIDENCE.md` | RED/GREEN tracer, BEFORE/AFTER residual audit, DIAGNOSTIC second-gap sweep, NIX-06/07/08 re-bindings, REVIEW dispositions, relaunch instruction | ✓ VERIFIED | Present, all sections found; explicitly and correctly self-labels every post-edit observation DIAGNOSTIC and states it closes none of NIX-02/03/04 |
| `64-GAP-REMEASURE-EVIDENCE.md` | Genuine D-09 shape re-measurement: session check, head check, provisioning, NIX-01 regression, tracer, NIX-04 full suite, NIX-02/03 tox environments with a real PDF, genuine residual audit, requirement closure table | ✓ VERIFIED | Present, all sections found; session-check discriminator matches 64-05's recorded rootfs; `## Requirement closure` reads MET for NIX-01 through NIX-05 |
| `64-NIX05-WORKTREE-EVIDENCE.md`, `64-NIX07-RENAME-EVIDENCE.md`, `64-NIX08-ENV-EVIDENCE.md`, `64-CI-EVIDENCE.md`, `64-FLAKE-EVIDENCE.md` | Unchanged since prior verification | ✓ VERIFIED | `git log --since=<prior verified timestamp>` over these five files returns no commits — no regression, still valid as of this pass |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `flake.nix` `fhsRun` `targetPkgs` | `/usr/lib/libz.so.1` inside `typsphinx-fhs-run` | `buildFHSEnv` links `targetPkgs` outputs into the rootfs `/usr/lib` | ✓ WIRED | Independently confirmed live: `"$FHS" /bin/sh -c 'test -e /usr/lib/libz.so.1'` exits 0 against the main checkout's current shim-embedded rootfs |
| Pillow `_imaging` (bare `NEEDED libz.so.1`) | the rootfs `libz.so.1` | dynamic loader default search inside the sandbox | ✓ WIRED | `64-GAP-REMEASURE-EVIDENCE.md` tracer: `import PIL._imaging` prints `PIL._imaging OK` with `-S` (import-order independent) |
| Shim body (`writeShellScriptBin`) | `fhsRun` (`typsphinx-fhs-run`) | `exec "${fhsRun}/bin/typsphinx-fhs-run" <absolute target> "$@"` | ✓ WIRED | Confirmed live: `ruff`'s shim body still embeds the new rootfs path; xtrace names this checkout's own `.venv/bin/ruff` |
| `tox` (inside sandbox) | `uv` shim (nested sandbox entry) | `tox-uv-bare`'s own PATH lookup of `uv`, re-entering `typsphinx-fhs-run` | ✓ WIRED | `64-GAP-REMEASURE-EVIDENCE.md`: every `venv>`/`uv-sync>` line across all seven tox environments names the new `uv` shim store path |
| `packages` list | `devShells.<system>.default` | `pkgs.lib.optionals pkgs.stdenv.hostPlatform.isLinux` guard | ✓ WIRED | Confirmed live: `nix flake check --all-systems --no-build` exits 0, darwin drvPaths unchanged |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| NIX-01 | 64-02, 64-04, 64-06 | `ruff check .` reports 0.15.20 (uv.lock, not nixpkgs) | ✓ SATISFIED | `64-GAP-REMEASURE-EVIDENCE.md` § NIX-01, live re-check |
| NIX-02 | 64-02, 64-05, 64-06 | `tox -e lint/type/py312/py313` each complete | ✓ SATISFIED | `64-GAP-REMEASURE-EVIDENCE.md` § NIX-02, genuine D-09 shape |
| NIX-03 | 64-02, 64-05, 64-06 | `tox -e cov/docs-html/docs-pdf` complete, real PDF | ✓ SATISFIED | `64-GAP-REMEASURE-EVIDENCE.md` § NIX-03, genuine D-09 shape |
| NIX-04 | 64-02, 64-05, 64-06 | Full suite, no environment-caused failures | ✓ SATISFIED | `64-GAP-REMEASURE-EVIDENCE.md` § NIX-04: `1543 passed, 5 skipped` exact match |
| NIX-05 | 64-02, 64-06 | Fresh-worktree provisioning, no manual step | ✓ SATISFIED | `64-GAP-REMEASURE-EVIDENCE.md` § D-09 head check + § NIX-05 procedure summary |
| NIX-06 | 64-01, 64-05 | `flake.nix` evaluates on all four systems, darwin unchanged | ✓ SATISFIED | `64-LIBZ-FIX-EVIDENCE.md` § NIX-06 (final flake), independently re-run |
| NIX-07 | 64-03, 64-05 | Absolute-path resolution, no recursion, proven by a catching check | ✓ SATISFIED | `64-NIX07-RENAME-EVIDENCE.md` (unchanged), `64-LIBZ-FIX-EVIDENCE.md` § NIX-07 carry-over |
| NIX-08 | 64-03, 64-05 | Sandbox `$HOME`/`/etc`/locale measured, locale-class effect recorded | ✓ SATISFIED | `64-NIX08-ENV-EVIDENCE.md` (unchanged), `64-LIBZ-FIX-EVIDENCE.md` § NIX-08 carry-over |

All eight `NIX-*` requirement IDs mapped to Phase 64 in `REQUIREMENTS.md` appear in at least one
plan's `requirements:` frontmatter (64-01: NIX-01/06/07; 64-02: NIX-01–05; 64-03: NIX-07/08; 64-04:
NIX-01 cross-check; 64-05: NIX-06/07/08; 64-06: NIX-01–05). No orphaned requirements.

`REQUIREMENTS.md`'s own checkboxes and status column (`[ ]` / "Pending" or "Gaps Found" for all
eight IDs) are stale relative to this verification's findings, but this is expected and by design:
per this project's standing rule (recorded in `64-06-SUMMARY.md` and confirmed by
`01b51ded`/`d49459c5`, "keep NIX-06/07/08 unchecked until phase completes"), the phase's own
tracking commits deliberately hold every `NIX-*` checkbox unflipped until the orchestrator flips
them centrally once the phase is marked complete — this verification pass is the gate that
authorizes that flip, not a discrepancy to fix here.

### Decision Coverage

All nine `64-CONTEXT.md` decisions (D-01 through D-09) appear in shipped phase artifacts (plans,
SUMMARYs, or evidence files): D-01 (11 files), D-02 (16), D-03 (13), D-04 (13), D-05 (12), D-06
(14), D-07 (15), D-08 (12), D-09 (22). None vanished during execution.

### Anti-Patterns Found

None. `grep -n -E "TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER"` over `flake.nix`, `64-LIBZ-FIX-EVIDENCE.md`
and `64-GAP-REMEASURE-EVIDENCE.md` returned no matches.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `ruff` shim resolves the fixed rootfs and `libz.so.1` is present | `command -v ruff` → grep rootfs → `"$FHS" /bin/sh -c 'test -e /usr/lib/libz.so.1'` (run live) | rootfs `99fm4lqkp4kab20d3blfbwajnprmlbfx-typsphinx-fhs-run`, matches `New fhs-run:`; `exit:0` | ✓ PASS |
| All seven shims resolve the expected store paths | `command -v` for `uv tox ruff black mypy pytest sphinx-build` (run live) | Byte-identical to `64-GAP-REMEASURE-EVIDENCE.md`'s `New shim paths` table for all seven | ✓ PASS |
| `ruff check .` runs to completion on the main tree post-merge | `ruff --version && ruff check .` (run live) | `ruff 0.15.20`; `All checks passed!` | ✓ PASS |
| The node that failed in 64-02 passes on the main tree post-merge | `pytest tests/test_converted_image_collision_render_gate.py -q` (run live) | `3 passed in 0.98s` | ✓ PASS |
| `flake.nix` evaluates on all four systems, darwin byte-identical | `nix flake check --all-systems --no-build` (run live) | exits 0; darwin drvPaths `fclfls55m9lp06679x7zrw0qzjya834j-nix-shell.drv` / `2m6y6pshri0vyw3jb5agczjnz9a92sxc-nix-shell.drv` match baseline exactly | ✓ PASS |
| CI baseline run is unaffected by the gap-closure plans | `gh run list --branch <branch> --limit 3`, `grep -rliE 'nix\|flake' .github/workflows/` | run `34618719267` still `completed`/`success`; no workflow references nix/flake | ✓ PASS |

The full 1548-test suite and all seven `tox` environments were **not** re-run in this verification
session over the main checkout: `64-GAP-REMEASURE-EVIDENCE.md`'s fresh-worktree run is the
authoritative, genuine-D-09-shape evidence the phase's own decisions (D-04) require, and re-running
the ~2-minute suite seven times in the main checkout (a different interpreter/venv shape, per
CLAUDE.md's worktree-isolation guidance) would not add discriminating evidence beyond the two spot
checks above, which independently corroborate the worktree measurement on the shipped rootfs.

### Human Verification Required

N/A — Infrastructure/tooling phase (Nix flake, sandbox shims, CI baseline) with no user-facing
elements. All nine truths are verifiable programmatically and were independently re-measured, not
merely cited from SUMMARY.md.

### Gaps Summary

None. All three gaps from the prior `gaps_found` (6/9) pass — NIX-02, NIX-03, NIX-04 — are closed:
64-05 root-caused and fixed the shared `libz.so.1` defect with a minimal `targetPkgs = p.zlib`
addition (correctly self-labelling its own post-edit runs as DIAGNOSTIC, not closure), and 64-06
re-measured all five affected requirements (NIX-01 through NIX-05) in a session genuinely relaunched
after that fix, producing a `MET` verdict for every row in its own closure table. Independent
re-measurement in this verification session — live shim/rootfs checks, a live `ruff check .`, a live
re-run of the previously-failing test node, and a live `nix flake check --all-systems` — corroborates
every claim rather than merely trusting the evidence files. `64-REVIEW.md`'s one open Warning
(WR-01) is a pre-existing, explicitly-deferred item (D-07's TLS condition never fired) and does not
block; its one new Info finding (IN-03) is a documentation-durability observation with no functional
defect behind it, correctly downgraded to advisory by the re-verification evidence gate (Step 7c) for
lacking deterministic evidence.

The phase goal — every documented bare command and every tox environment runs to completion on the
maintainer's NixOS machine through the FHS shims, with the sandbox's environment behaviour measured
rather than assumed — is achieved and independently confirmed.

---

_Verified: 2026-09-12_
_Verifier: Claude (gsd-verifier)_
