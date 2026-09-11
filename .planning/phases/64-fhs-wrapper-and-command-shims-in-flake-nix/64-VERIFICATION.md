---
phase: 64-fhs-wrapper-and-command-shims-in-flake-nix
verified: 2026-09-12T00:00:00Z
status: gaps_found
score: 6/9 must-haves verified
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
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-CI-EVIDENCE.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-FLAKE-EVIDENCE.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-NIX05-WORKTREE-EVIDENCE.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-NIX07-RENAME-EVIDENCE.md"
  - ".planning/phases/64-fhs-wrapper-and-command-shims-in-flake-nix/64-NIX08-ENV-EVIDENCE.md"
  - "flake.nix"
covered_digest: "v1:sha256:29778126cd4d3c380795cb4aa4393c5833206f03db5c35bcf8d77153fc33fdb1"
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "NIX-02: tox -e lint, tox -e type, tox -e py312 and tox -e py313 each run to completion"
    status: failed
    reason: "tox -e lint, -e type and -e py313 end OK, matching baselines exactly, but tox -e py312 ends FAIL code 1 inside the FHS sandbox: ImportError: libz.so.1: cannot open shared object file, raised from pypdf's lazy PIL import (test_converted_image_collision_render_gate.py::test_pdf_embeds_both_distinctly_sized_images). Reproduced identically under the bare pytest shim and tox -e cov; tox -e py313 (interpreter matching the pre-phase baseline) passes clean in the identical sandbox, narrowing this to a package/targetPkgs gap correlated with which CPython build uv resolves Pillow's wheel against, not a uniform sandbox defect."
    artifacts:
      - path: "flake.nix"
        issue: "fhsRun declares no targetPkgs; the FHS root lacks whatever provides libz.so.1 for uv-downloaded CPython builds (cp312, cp314), even though the identical sandbox with the nix-provided cp313 interpreter succeeds"
    missing:
      - "A flake.nix targetPkgs addition (zlib or equivalent) that makes libz.so.1 resolvable inside typsphinx-fhs-run for uv-downloaded interpreter builds, re-measured green in a session relaunched after that edit"
  - truth: "NIX-03: tox -e cov, tox -e docs-html and tox -e docs-pdf each run to completion, with docs-pdf producing a real PDF"
    status: failed
    reason: "docs-html and docs-pdf both end OK with warning counts matching the pre-phase baselines exactly (3 and 5) and docs-pdf produces a real, non-empty PDF beginning with the %PDF magic bytes. tox -e cov ends FAIL code 1 with the identical libz.so.1 ImportError documented under NIX-02, reproduced a third time with the same node id and first traceback frame."
    artifacts:
      - path: "flake.nix"
        issue: "Same targetPkgs gap as NIX-02 — cov's pytest runs under the uv-downloaded cpython-3.14.4 interpreter, which fails identically to py312's cpython-3.12.13"
    missing:
      - "Same fix as NIX-02's gap; tox -e cov must be re-measured green in the same gap-closure pass"
  - truth: "NIX-04: the full test suite (1548 tests at milestone start) runs on that machine with no environment-caused failures"
    status: failed
    reason: "One full-suite run through the bare pytest shim (pytest -q -rs, maintainer locale, no locale variable set) reads '1 failed, 1541 passed, 6 skipped' against the carried-in baseline of '1543 passed, 5 skipped'. 1548 collected still matches. The failing node (test_converted_image_collision_render_gate.py::test_pdf_embeds_both_distinctly_sized_images) and the sixth (new) skip both trace to the same libz.so.1 ImportError inside pypdf's lazy PIL import used only by the test's own assertion tooling, not by anything typsphinx emits. This is attributed as environment-caused, not product behaviour, but it is a real, measured, unmet gate — not zero environment-caused failures."
    artifacts:
      - path: "flake.nix"
        issue: "Same targetPkgs gap as NIX-02/NIX-03"
    missing:
      - "Same fix; NIX-04 must be re-measured at 1543 passed / 5 skipped (or an updated, justified baseline) after the flake.nix fix lands"
deferred: []
---

# Phase 64: FHS Wrapper and Command Shims in `flake.nix` Verification Report

**Phase Goal:** Every documented bare command and every tox environment runs to completion on the
maintainer's NixOS machine through Linux-guarded `buildFHSEnv` shims that resolve the project's own
`.venv` binaries by absolute path, with the sandbox's environment behaviour measured rather than
assumed.

**Verified:** 2026-09-12
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

The mechanism (`buildFHSEnv` passthrough + seven absolute-path shims) is real, present in
`flake.nix`, evaluates on all four declared systems, resolves by absolute path with no bare-name
fallback, and cannot recurse or escape its own checkout — all independently re-confirmed below, not
just cited from SUMMARY.md. However, the phase's own success criterion that **every tox environment
and the full test suite run to completion with no environment-caused failures (SC#2 / NIX-02,
NIX-03, NIX-04)** is honestly measured and reported as **not met**: three of ten gates
(`tox -e py312`, `tox -e cov`, and the full pytest suite) fail inside the sandbox on a `libz.so.1`
`ImportError` affecting `uv`-downloaded CPython builds. This was discovered, attributed, and left
unfixed by design (64-02's scope fence forbade a `flake.nix` edit mid-plan), and the owner has
already decided to close it with a Phase 64 gap-closure plan. It is reported here as a gap, not
silently waved through, per the phase's own binding prohibition against adjusting baselines to
match a measurement.

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | NIX-01: `ruff check .` and the other documented bare commands (`pytest`, `black --check .`, `mypy typsphinx/`, `sphinx-build`) run to completion out of the project's own `.venv`, `ruff` reporting exactly `0.15.20` | ✓ VERIFIED | `64-NIX05-WORKTREE-EVIDENCE.md` § NIX-01: all seven names resolve via xtrace `+ exec` lines naming `<worktree>/.venv/bin/<tool>`; `ruff --version` → `ruff 0.15.20` (matches `uv.lock:1209-1210`); `ruff check .` → `All checks passed!`, exit 0; outside-sandbox control still fails rc 127. Cross-checked against CI's `Lint and Format Check` job (independently re-queried via `gh run view 34618719267`, `conclusion: success`, ruff `0.15.20`, `All checks passed!`) |
| 2 | NIX-02: `tox -e lint`, `-e type`, `-e py312` and `-e py313` each run to completion | ✗ FAILED | `64-NIX05-WORKTREE-EVIDENCE.md` § NIX-02: `lint: OK`, `type: OK`, `py313: OK` (`1543 passed, 5 skipped`, exact baseline match) — but `py312: FAIL code 1` (`1 failed, 1541 passed, 6 skipped`, `libz.so.1` `ImportError`) |
| 3 | NIX-03: `tox -e cov`, `-e docs-html` and `-e docs-pdf` each run to completion, `docs-pdf` producing a real PDF | ✗ FAILED | `64-NIX05-WORKTREE-EVIDENCE.md` § NIX-03: `docs-html: OK` (3 warnings, baseline match), `docs-pdf: OK` (5 warnings, baseline match, PDF 2,776,960 bytes beginning `%PDF`) — but `cov: FAIL code 1`, same `libz.so.1` defect as NIX-02 |
| 4 | NIX-04: the full test suite runs with no environment-caused failures | ✗ FAILED | `64-NIX05-WORKTREE-EVIDENCE.md` § NIX-04: `1 failed, 1541 passed, 6 skipped` vs. baseline `1543 passed, 5 skipped`; failing node and traceback itemised, attributed to the same `libz.so.1` `ImportError`, not adjusted to fit |
| 5 | NIX-05: an executor in a freshly created git worktree can run the documented provisioning line and then every gate, with no manual `ln -sf` or `patchelf` step anywhere | ✓ VERIFIED | `64-NIX05-WORKTREE-EVIDENCE.md` § D-09 head check + Provisioning: `.venv`/`.tox` absent pre-provisioning, single documented `env -u … uv sync --extra dev` line provisions the worktree, `typsphinx.__file__` resolves inside the worktree (tree-identity proof), `direnv status` shows the shim PATH reaches the worktree purely by session inheritance (this worktree's own `.envrc` was never individually allowed). No symlink or ELF-patch step appears in any of the four evidence files. The requirement text is about the provisioning *mechanism* (no manual step, reachability answered by observation) — distinct from NIX-02/03/04's own "runs to completion" gates, which fail independently and are tracked as separate, still-open requirements in `REQUIREMENTS.md` |
| 6 | NIX-06: `flake.nix` evaluates successfully on all four declared systems, including both darwin ones, unchanged | ✓ VERIFIED | `64-FLAKE-EVIDENCE.md` § NIX-06 + independently re-run in this session: `nix flake check --all-systems --no-build` exits 0; darwin drvPaths `fclfls55m9lp06679x7zrw0qzjya834j-nix-shell.drv` (x86_64) and `2m6y6pshri0vyw3jb5agczjnz9a92sxc-nix-shell.drv` (aarch64) match the pre-edit baseline exactly, re-confirmed live in this verification |
| 7 | NIX-07: each shim resolves its target by absolute path and cannot recurse into itself, proven by a check that would catch bare-name resolution | ✓ VERIFIED | `64-NIX07-RENAME-EVIDENCE.md`: all seven shim bodies read verbatim, none contains `command -v`/`which`/PATH lookup; rename test with a discriminating escape positive control (main checkout's own runnable `.venv/bin/ruff`, which WOULD print a plausible version on an escape) — all six venv-shim rename cases exit 127 with the `typsphinx-shim:` line, zero stdout, no hang, no fall-through; `uv`'s two-leg order, quoting (space + non-ASCII path) and nearest-`.venv`-wins ordering all proven in a scratch tree outside the repository |
| 8 | NIX-08: the FHS sandbox's `$HOME`, `/etc` and locale behaviour is measured for this project's actual invocation, and its effect on the known locale-dependent test class is recorded | ✓ VERIFIED | `64-NIX08-ENV-EVIDENCE.md`: definitions committed before measurement (2 separate commits, confirmed in `git log`); `$HOME`, `TMPDIR`, `/tmp` device/inode, and locale (`LANG=ja_JP.UTF-8`, `LOCALE_ARCHIVE`) all pass through unchanged; four-cell H-ja/H-C/S-ja/S-C matrix control holds and both shim cells match host exactly → `**Finding:** REPRODUCES`; `TestNoLostDiagnostics` passes 7/7 under both locales through the shim. One documented substitution (main checkout's `.venv/bin/python` used for the H-ja/H-C host leg, since this worktree's own uv-downloaded `.venv/bin/python` cannot execute unshimmed at all) is transparently recorded and does not affect validity — same `sphinx==9.1.0` pin, dummy build invoking no `typsphinx` extension code |
| 9 | SC#5: the milestone branch is on `origin` with a completed 3-OS CI run, the pre-revert baseline for Phase 65 | ✓ VERIFIED | `64-CI-EVIDENCE.md` + independently re-queried via `gh run view 34618719267`: canonical branch pushed with tracking (`origin/gsd/v0.9.3-toolchain-and-dependency-update-repair` at `7afbf5b2`), no decoy, no tag; run `34618719267` `status: completed`, `conclusion: success`, 12/12 jobs green (re-confirmed live), both `windows-latest` and both `macos-latest` lanes named individually; no `release.yml` run at the pushed SHA |

**Score:** 6/9 truths verified (3 failed — NIX-02, NIX-03, NIX-04)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `flake.nix` | One Linux-guarded `buildFHSEnv` passthrough (`typsphinx-fhs-run`) plus seven absolute-path command shims (`uv`, `tox`, `ruff`, `black`, `mypy`, `pytest`, `sphinx-build`) | ✓ VERIFIED | Read directly: `fhsRun` (`pkgs.buildFHSEnv`, `runScript = exec "$@"`), `venvWalk` (bounded upward walk stopping at `.git`), `venvShimNames`/`venvShims` (six strict shims), `uvShim` (D-02's two-leg exception), `packages` gated by `pkgs.lib.optionals pkgs.stdenv.hostPlatform.isLinux` with a matching non-Linux `[pkgs.uv]` branch. Matches the plan's described shape exactly |
| `64-FLAKE-EVIDENCE.md` | RED, tracer GREEN, roster diagnostics, tox shakeout, NIX-06 all-systems | ✓ VERIFIED | 454 lines; RED (`stub-ld` rejection, rc 127), tracer GREEN through the shim, all-seven-name roster diagnostics, `nix flake check --all-systems` transcript, darwin byte-identity |
| `64-NIX05-WORKTREE-EVIDENCE.md` | NIX-01/02/03/04/05 in the genuine D-09 shape | ✓ VERIFIED (content), gaps present | 638 lines; D-09 head check, provisioning, NIX-01 all green, NIX-02/03/04 honestly show the `libz.so.1` failures alongside the passing environments |
| `64-NIX07-RENAME-EVIDENCE.md` | Rename proof, escape positive control, uv leg order, boundary/encoding/ordering probe | ✓ VERIFIED | 376 lines; all seven shim bodies verbatim, discriminating positive control, 7-row rename table all rc 127, scratch-tree boundary probe with space + non-ASCII path |
| `64-NIX08-ENV-EVIDENCE.md` | Definitions, environment measurement, four-cell locale matrix, one Finding | ✓ VERIFIED | 278 lines; definitions committed ahead of measurement (2 commits), full env/locale measurement, REPRODUCES finding derived mechanically |
| `64-CI-EVIDENCE.md` | Branch census, push, dispatch, completed run, full job census | ✓ VERIFIED | 270 lines; independently re-confirmed via live `gh run view` query — status/conclusion/jobs all match |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| Shim body (`writeShellScriptBin`) | `fhsRun` (`typsphinx-fhs-run`) | `exec "${fhsRun}/bin/typsphinx-fhs-run" <absolute target> "$@"` | ✓ WIRED | Confirmed in `flake.nix` source and in every shim body transcribed in `64-NIX07-RENAME-EVIDENCE.md` |
| `venvWalk` | `<checkout root>/.venv/bin/<tool>` | Bounded upward walk stopping at first `.git` ancestor | ✓ WIRED | Confirmed by the rename test's boundary case (walk stops at inner `.git`, never reaches outer `.venv`) and by the nested-worktree nature of every wave-2 measurement |
| `tox` (inside sandbox) | `uv` shim (nested sandbox entry) | `tox-uv-bare`'s own PATH lookup of `uv`, re-entering `typsphinx-fhs-run` | ✓ WIRED | `64-FLAKE-EVIDENCE.md` and `64-NIX05-WORKTREE-EVIDENCE.md`: `tox -e lint`'s `venv>`/`uv-sync>` lines show `uv` resolving via the shim's nix-store path from inside the sandboxed `tox` process |
| `packages` list | `devShells.<system>.default` | `pkgs.lib.optionals pkgs.stdenv.hostPlatform.isLinux` guard | ✓ WIRED | Confirmed live: `nix flake check --all-systems --no-build` exits 0, darwin drvPaths unchanged |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| NIX-01 | 64-02, 64-04 | `ruff check .` reports 0.15.20 (uv.lock, not nixpkgs) | ✓ SATISFIED | `64-NIX05-WORKTREE-EVIDENCE.md`, `64-CI-EVIDENCE.md` cross-check |
| NIX-02 | 64-02 | `tox -e lint/type/py312/py313` each complete | ✗ BLOCKED | `py312` fails on `libz.so.1` |
| NIX-03 | 64-02 | `tox -e cov/docs-html/docs-pdf` complete, real PDF | ✗ BLOCKED | `cov` fails on `libz.so.1`; docs-html/docs-pdf pass |
| NIX-04 | 64-02 | Full suite, no environment-caused failures | ✗ BLOCKED | `1 failed, 1541 passed, 6 skipped` vs. `1543/5` baseline |
| NIX-05 | 64-02 | Fresh-worktree provisioning, no manual step | ✓ SATISFIED | `64-NIX05-WORKTREE-EVIDENCE.md` D-09 head check + provisioning section |
| NIX-06 | 64-01 | `flake.nix` evaluates on all four systems, darwin unchanged | ✓ SATISFIED | `64-FLAKE-EVIDENCE.md`, independently re-run |
| NIX-07 | 64-03 | Absolute-path resolution, no recursion, proven by a catching check | ✓ SATISFIED | `64-NIX07-RENAME-EVIDENCE.md` |
| NIX-08 | 64-03 | Sandbox `$HOME`/`/etc`/locale measured, locale-class effect recorded | ✓ SATISFIED | `64-NIX08-ENV-EVIDENCE.md` |

`REQUIREMENTS.md`'s own traceability table agrees exactly with this assessment: `NIX-01`, `NIX-05`,
`NIX-06`, `NIX-07`, `NIX-08` are checked `[x]`; `NIX-02`, `NIX-03`, `NIX-04` remain `[ ]` Pending. No
orphaned requirements — all eight `NIX-*` IDs mapped to Phase 64 in `REQUIREMENTS.md` appear in at
least one plan's `requirements:` frontmatter (64-01: NIX-01/06/07; 64-02: NIX-01–05; 64-03: NIX-07/08;
64-04: NIX-01 cross-check).

### Anti-Patterns Found

None. `grep -n -E "TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER"` over `flake.nix` and all five evidence files
returned no matches.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `flake.nix` evaluates on all four systems, darwin byte-identical | `nix flake check --all-systems --no-build` (run live in this verification session) | `all checks passed!`; darwin drvPaths `fclfls55m9lp06679x7zrw0qzjya834j-nix-shell.drv` / `2m6y6pshri0vyw3jb5agczjnz9a92sxc-nix-shell.drv` match evidence exactly | ✓ PASS |
| CI run 34618719267 is genuinely completed/green with 12/12 jobs | `gh run view 34618719267 --json status,conclusion,jobs,headSha` (run live) | `status: completed`, `conclusion: success`, 12 jobs, 0 non-success, `headSha` = `7afbf5b2c1c35d07fa775d194d4aaba6d575e1f5` | ✓ PASS |
| Current branch state matches CI-evidence's pushed tip, no unexpected `flake.nix` drift since | `git log --oneline -5`, `git diff 7afbf5b2 HEAD -- flake.nix` | HEAD is 5 commits ahead of the pushed SHA (tracking-doc commits only); `flake.nix` diff is empty — no undocumented code drift since the CI baseline | ✓ PASS |

Full test suite, `tox`, and `uv sync` were **not** re-run in this verification session per the
orchestrator's explicit instruction (main checkout's `.venv` is the old nix-3.13 venv; provisioning
or running the suite here would not reproduce the worktree conditions the phase measures and could
corrupt the main checkout's environment state).

### Gaps Summary

The FHS-shim mechanism itself is real, correctly wired, evaluates on all four declared Nix systems,
resolves by absolute path with a check that genuinely catches bare-name/recursive resolution, and the
sandbox's environment/locale behaviour is honestly measured — none of that is fabricated or
overstated in the SUMMARYs, and independent re-measurement (live `nix flake check`, live `gh run
view`) confirms the SUMMARY claims rather than merely trusting them.

However, the phase's own success criterion SC#2 — "every tox environment runs to completion, and the
full suite is clean of environment-caused failures" — is not met. Three gates (`tox -e py312`,
`tox -e cov`, and the bare full `pytest` run) fail identically on `ImportError: libz.so.1: cannot open
shared object file`, raised from `pypdf`'s own lazy `PIL` import (used only by one test's own
PDF-image-extraction assertion tooling — not by anything `typsphinx` itself emits). The three failing
plans (`64-02`) already recorded this honestly rather than silencing it: 64-02's own Self-Check is
`FAILED`, and `REQUIREMENTS.md` correctly leaves `NIX-02`/`NIX-03`/`NIX-04` unchecked. This is not a
fabricated SUMMARY claim slipping past verification — it is a real, already-disclosed, already-tracked
gap that the project owner has decided (per `STATE.md`, 2026-09-12) to close with a dedicated Phase 64
gap-closure plan before the phase can be considered fully complete.

Because this gap is native to this same phase's own success criteria — not addressed by any later
milestone phase's goal or success criteria in `ROADMAP.md` — it is reported here as a `gaps_found`
blocker, not deferred. The recommended next step is exactly what `STATE.md` and the plan summaries
already point to: `/gsd-plan-phase 64 --gaps`, adding a `targetPkgs` entry (most likely `zlib`, per
64-02's attribution) to `fhsRun` in `flake.nix`, followed by a session relaunch and a re-run of
`tox -e py312`, `tox -e cov`, and the full suite to confirm the `1543 passed, 5 skipped` baseline (or
an explicitly justified updated baseline) is restored.

---

_Verified: 2026-09-12_
_Verifier: Claude (gsd-verifier)_
