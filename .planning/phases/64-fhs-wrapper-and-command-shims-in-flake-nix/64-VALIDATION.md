---
phase: "64"
slug: "fhs-wrapper-and-command-shims-in-flake-nix"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-03"
---

# Phase 64 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> Seeded by plan-phase from `64-RESEARCH.md` § "Validation Architecture". This phase changes no
> `typsphinx/` behaviour and adds no test. D-05 routes every NIX-07/NIX-08 proof into evidence
> markdown, because a pytest test would be permanently skipped on every CI runner. What it validates
> instead:
> - (a) `flake.nix` builds a working, Linux-guarded FHS passthrough and seven absolute-path shims
> - (b) the documented commands and every tox environment run through them in a fresh worktree
> - (c) the sandbox's environment behaviour is measured rather than assumed
> - (d) the branch reaches `origin` with a completed 3-OS CI run
>
> **The unit of proof is a recorded observation.** Most rows are shell transcripts in phase evidence
> files, gated by commands that re-run the decisive check live, not by a test exit code alone.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml`), orchestrated by `tox` (`uv-venv-lock-runner`); the `nix` CLI (2.34) for flake evaluation and `nix develop` diagnostics; `gh` for the CI dispatch |
| **Config file** | `pyproject.toml`, `tox.ini`, `flake.nix` |
| **Quick run command** | `ruff --version` and `bash -x "$(command -v ruff)" --version` through the shim (seconds; wave 2+ only), or `nix develop . --command ruff --version` (wave 1 diagnostic) |
| **Full suite command** | `pytest -q -rs` through the pytest shim in a fresh worktree (NIX-04): 1548 collected, baseline 1543 passed / 5 skipped |
| **Estimated runtime** | full suite about 2 min · seven tox environments cold about 10-15 min (py312 includes a CPython download, unmeasured before this phase) · one CI dispatch about 7 min wall clock |

**Session boundary (STANDING for this phase):** the Claude Code session PATH is frozen at launch.
- Wave 1 (64-01) runs in a session that predates the `flake.nix` edit, so every shim run there is a
  labelled `nix develop` DIAGNOSTIC.
- Waves 2 and 3 run only in a session the maintainer relaunched from a direnv-loaded shell in
  `/home/yuta/Documents/typsphinx` after 64-01 merged.
- Plans 64-02 and 64-03 carry a `<precondition>` that halts at a blocking-human gate otherwise.
- Wave 4 (64-05, gap closure) runs in the session relaunched after 64-01. Its shims embed the old
  rootfs `/nix/store/dgddrdfkvigqsv48k563szqc8w7xlw2g-typsphinx-fhs-run`, which has no `libz.so.1`,
  so they serve as the old side for RED and the BEFORE audit. Every shim run after 64-05's own edit
  is a labelled `nix develop` DIAGNOSTIC.
- Wave 5 (64-06, gap closure) runs only in a session the maintainer relaunched from a direnv-loaded
  shell in `/home/yuta/Documents/typsphinx` after 64-05 merged. Every 64-06 task carries a
  `<precondition>` that discriminates on what the fix changed: the rootfs embedded in `command -v
  ruff`'s body must hold `/usr/lib/libz.so.1` and match 64-05's `New fhs-run:` line. "The shim
  contains typsphinx-fhs-run" is true in both sessions and is not a discriminator.

**Worktree note (CLAUDE.md, STANDING):** every executor runs
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` in its own worktree first. From
wave 2 on, that `uv` is the shim.

### Baselines carried in (re-measured, never inherited)

| Baseline | Value | Source | Obligation |
|----------|-------|--------|------------|
| Tests collected | **1548** | `--collect-only` at planning, 2026-09-11; no `tests/` or `typsphinx/` diff since `v0.9.2` | 64-02-T2 re-counts |
| Full suite, dev extra | **1543 passed, 5 skipped** | `63-GREEN-TREE-EVIDENCE.md` | 64-02-T2 re-runs once; a sixth skip or any failure is itemised and attributed |
| `docs-html` / `docs-pdf` warnings | **3 / 5** | `63-GREEN-TREE-EVIDENCE.md`, clean builds | 64-02-T3 compares from clean builds |
| `ruff` pin | **0.15.20** | `uv.lock:1209-1210` | exact string, never exit code |
| darwin drvPaths | x86_64-darwin `fclfls55m9lp06679x7zrw0qzjya834j`, aarch64-darwin `2m6y6pshri0vyw3jb5agczjnz9a92sxc` (`-nix-shell.drv`) | measured at planning, `flake.lock` unchanged | 64-01-T3 asserts byte identity after the edit; 64-05-T3 re-asserts it after the zlib edit |
| Interpreter provenance (gap closure) | worktree `.venv` → uv-managed cpython-3.14.4; `.tox/py312` → uv cpython-3.12.13; `.tox/py313` → nix python3-3.13.13. The 1543 / 5 baseline above was measured under nix python3-3.13.13 (the main checkout's `.venv`) | `64-NIX05-WORKTREE-EVIDENCE.md` § NIX-04; `64-LIBZ-DIAGNOSIS.md` § 3 | 64-05-T1 and 64-06-T1 record every `pyvenv.cfg` `home` and `version_info`; no plan pins the interpreter; a divergence attributable to cp3.14 is itemised, never normalised |
| Residual unresolved sonames after zlib | {`libcrypt.so.1` ← cp3.12 `_crypt`; `libtcl9.0.so`, `libtcl9tk9.0.so` ← `_tkinter`}, over the main checkout's cp313 wheel set and the uv interpreter trees only | `64-LIBZ-DIAGNOSIS.md` § 5 (DIAGNOSTIC, scratch rootfs) | 64-05-T1/T2 re-measure BEFORE and AFTER over the environments they provision; 64-06-T3 re-measures in the genuine shape; each residual gets a FORCED or UNREACHED verdict |
| x86_64-linux drvPath before the zlib edit | `vd4rms2m5kvjaazd3i78049k0s9a21g0-nix-shell.drv` (post-64-01) | `64-FLAKE-EVIDENCE.md` § NIX-06 | 64-05-T1 re-reads it into a `PRE_X86_LINUX:` line; 64-05-T3 asserts the final value differs |

---

## Sampling Rate

- **After every task commit:** the task's own `<automated>` block. Each one re-runs its decisive
  check live: a shim resolution, a version string, an xtrace `+ exec` path, an evaluation, a PDF's
  magic bytes, or a `gh run view` field.
- **After every plan wave:**
  - wave 1: `nix flake check --all-systems --no-build`
  - wave 2: the full suite through the shim, plus the seven tox environments
  - wave 3: the CI run's job census
  - wave 4 (gap closure): `nix flake check --all-systems --no-build` on the final flake, the
    BEFORE/AFTER residual sets, and the DIAGNOSTIC suite, `tox -e py312` and `tox -e cov`
  - wave 5 (gap closure): the full suite through the shim, plus the seven tox environments, in the
    session relaunched after 64-05 merged
- **Before `/gsd-verify-work`:** all seven plan-authored evidence files present; 64-06's
  `## Requirement closure` reads MET for NIX-01..NIX-05; the CI run completed and green.
- **Max feedback latency:** about 2 min for the suite; tox provisioning and CI are the long poles.

---

## Per-Task Verification Map

Task IDs are `64-{plan}-T{task}`. Every row's command is transcribed from the task's own `<automated>`
block in shortened form; the PLAN file carries the full gate.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 64-01-T1 (tracer) | 01 | 1 | NIX-01 (diagnostic) / D-03 / D-04 / D-06 | T-64-01, T-64-02 | a shim resolves only an absolute `.venv/bin/ruff` inside its own checkout | shell transcript + live re-check | `nix develop . --command ruff --version` = `ruff 0.15.20` from the root and from `docs/`; the xtrace `+ exec` line names `<worktree>/.venv/bin/ruff`; the chroot builder is absent; `flake.lock` unchanged; RED text or labelled non-reproduction in evidence | ✅ `flake.nix` exists; evidence created by the task | ⬜ pending |
| 64-01-T2 | 01 | 1 | D-01 / D-02 / D-03 | T-64-01 | seven names; six strict, `uv` with a store-path second leg | shell transcript + live re-check | inside `nix develop .`: six xtrace lines under `$PWD/.venv/bin/`, uv's under `/nix/store/…-uv-…/bin/uv`, `type -P uv` = the unversioned shim, version substrings match `uv.lock` | ✅ | ⬜ pending |
| 64-01-T3 | 01 | 1 | NIX-06 / D-07 / D-08 | T-64-04, T-64-05 | darwin never forces `buildFHSEnv`; tox's subprocess tree runs inside the sandbox | nix eval + tox + file magic | `nix flake check --all-systems --no-build`; darwin drvPaths equal the planning values; x86_64-linux and darwin censuses equal the stated arrays; `nix develop . --command tox -e lint`; PDF begins `%PDF`; no locale variable, env-clearing flag, ELF-patch tool or nixpkgs ruff in `flake.nix` | ✅ | ⬜ pending |
| 64-02-T1 (tracer) | 02 | 2 | NIX-05 / NIX-01 / D-04 / D-09 / D-02 / D-06 | T-64-06, T-64-07 | the shim PATH is inherited, never simulated; nothing measured against the main checkout | shell transcript + live re-check | `pwd -P` under `.claude/worktrees/`; both shim bodies contain `typsphinx-fhs-run`; `ruff --version` = `ruff 0.15.20`; xtrace path inside the worktree; `ruff check .`; `typsphinx.__file__` inside the worktree; evidence carries the measured-shape line and the direnv RC lines | ✅ N/A — evidence created by the task | ⬜ pending |
| 64-02-T2 | 02 | 2 | NIX-01 / NIX-04 / D-08 | T-64-07, T-64-08 | one full-suite run, maintainer locale, baseline gated literally | full suite + lint/type | `black --check .`; `mypy typsphinx/`; four xtrace paths inside the worktree; `pytest -q` → `1543 passed, 5 skipped`, zero `failed`; `uv run pytest tests/test_extension.py -q` | ✅ | ⬜ pending |
| 64-02-T3 | 02 | 2 | NIX-02 / NIX-03 / NIX-05 / D-07 | T-64-09 | cold provisioning inside the sandbox; a real PDF, never exit 0 alone | tox + file magic | re-run `tox -e lint` and a clean `tox -e docs-pdf`; `test -s` and `%PDF`; `.tox/{py312,py313,cov}` exist; seven `<env>: OK` lines, a `Python 3.12` header and two clean-build commands in evidence | ✅ | ⬜ pending |
| 64-03-T1 (tracer) | 03 | 2 | NIX-07 / D-02 / D-03 / D-05 / D-09 | T-64-11, T-64-12 | a missing target fails loud (127), never hangs, recurses or escapes | rename experiment, live | the six venv targets renamed and restored in turn, each `timeout 30` run → rc 127, a `typsphinx-shim:` line, empty stdout; ruff restored to `0.15.20`; no `.venv/bin/uv` left; uv xtrace → store path; no shim body performs a PATH lookup; evidence has the positive control, the leg-1 probe and the INNER result | ✅ N/A — evidence created by the task | ⬜ pending |
| 64-03-T2 | 03 | 2 | NIX-08 / D-06 / D-08 / D-05 | T-64-10, T-64-13 | no secret reaches committed evidence; the finding is defined before it is measured | env measurement + targeted tests | `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT "$FHS" /usr/bin/env` → 0 surviving lines; `$HOME` and `/tmp` device/inode identical inside; `TestNoLostDiagnostics` passes under the maintainer locale and under `LC_ALL=C`; definitions committed before the results (at least two commits); exactly one `**Finding:**`; no token-, key- or secret-shaped assignment | ✅ | ⬜ pending |
| 64-04-T1 (tracer) | 04 | 3 | SC#5 (constraint 9, 10) / NIX-01 cross-check | T-64-14, T-64-15, T-64-16 | only the canonical ref is pushed; no decoy, no tag, no release workflow | git + gh | upstream = `origin/<canonical>`; origin SHA non-empty; no decoy on origin; the run's `headSha` = the pushed SHA, `workflowName` = `CI`, `event` = `workflow_dispatch`; no tag at the tip | ✅ `.github/workflows/ci.yml` | ⬜ pending |
| 64-04-T2 | 04 | 3 | SC#5 / NIX-01 cross-check | T-64-16, T-64-17 | the green is observed on the pushed tip, never inherited | CI | run `completed` / `success`; at least 12 jobs, zero non-success; two windows-latest and two macos-latest jobs; `Lint and Format Check` success; the four lanes and `Run lint with tox` named in evidence; exactly one dispatch; no `release.yml` run at the SHA; the release-only lint step name absent | ✅ | ⬜ pending |
| 64-05-T1 (tracer) | 05 | 4 | gap root cause for NIX-02/03/04 (CR-01) / D-04 / D-05 / D-06 / D-08 | T-64-18, T-64-19, T-64-20 | a GREEN counts only once the new rootfs is proven in use; the old sandbox is RED for all three interpreter builds | shell transcript + live re-check (DIAGNOSTIC after the edit) | exactly one `targetPkgs = p: [ p.zlib …];` line; NEW rootfs ≠ `dgddrdfk…`, holds `/usr/lib/libz.so.1`, while the old one lacks it; `python -S … import PIL._imaging` OK under NEW for `.venv`, `.tox/py312`, `.tox/py313`; `nix develop . --command pytest tests/test_converted_image_collision_render_gate.py`; `flake.lock` unchanged; evidence has `BEFORE = {…libz.so.1…}` and `PRE_X86_LINUX:` | ✅ `flake.nix`; evidence created by the task | ⬜ pending |
| 64-05-T2 | 05 | 4 | NIX-02 / NIX-03 / NIX-04 (DIAGNOSTIC only, closes nothing) / D-08 | T-64-18, T-64-19 | no rootfs package without a failing gate; a second gap surfaces before a relaunch is requested | ldd audit + suite + tox (DIAGNOSTIC) | the last `AFTER = {…}` lacks libz.so.1; `## Residual verdicts`; two `scanned=` lines; collision-gate and greyscale-pipeline files pass with the Pillow-gated skip gone; `tox -e py312 -- <collision file>`; evidence shows `1543 passed, 5 skipped` or `## Baseline divergence`, plus `py312: OK` and `cov: OK` | ✅ | ⬜ pending |
| 64-05-T3 | 05 | 4 | NIX-06 / NIX-07 / NIX-08 / D-06 / D-07 / D-09 | T-64-21, T-64-22 | darwin never forces the rootfs; the shipped shims are 64-03's shims modulo the rootfs path | nix eval + shim-body diff + env probe | `nix flake check --all-systems --no-build`; darwin drvPaths equal; x86_64-linux ≠ `PRE_X86_LINUX`; both censuses exact; seven normalised shim-body diffs empty with OLD≠NEW; no locale pin, env-clearing flag, ELF-patch tool or nixpkgs ruff in `flake.nix`; no workflow mentions nix or flake; relaunch section, `New fhs-run:` line, `--gaps-only`; the four REVIEW ids; committed paths only `flake.nix` and `.planning/` | ✅ | ⬜ pending |
| 64-06-T1 (tracer) | 06 | 5 | NIX-05 / NIX-01 / D-04 / D-06 / D-09 | T-64-23, T-64-24 | measured only in the relaunched session; nothing measured against the main checkout | shell transcript + live re-check | the ruff shim's rootfs holds `/usr/lib/libz.so.1` and matches `New fhs-run:`; `pwd -P` under `.claude/worktrees/`; `ruff --version` = `ruff 0.15.20`; `ruff check .`; `typsphinx.__file__` inside the worktree; `uv run python -S … import PIL._imaging`; `pytest tests/test_converted_image_collision_render_gate.py`; evidence has the shape line, `version_info`, `Found RC` | ✅ N/A — evidence created by the task | ⬜ pending |
| 64-06-T2 | 06 | 5 | NIX-04 / D-08 | T-64-25 | one run, maintainer locale, baseline gated literally | full suite | `pytest --collect-only -q` → `1548 tests collected`; greyscale-pipeline Pillow skip gone; evidence has `collected 1548 items` and `1543 passed, 5 skipped in` or `## Baseline divergence` | ✅ | ⬜ pending |
| 64-06-T3 | 06 | 5 | NIX-02 / NIX-03 / NIX-05 / D-07 | T-64-26 | cold provisioning inside the fixed sandbox; a real PDF, never exit 0 alone | tox + file magic + ldd audit | live `tox -e lint`, `tox -e py312 -- <collision file>`, clean `tox -e docs-pdf`; `test -s` and `%PDF`; seven `<env>: OK` lines; `Python 3.12`; two clean-build commands; the last `GENUINE = {…}` lacks libz.so.1; `## Requirement closure` with no NOT MET row | ✅ | ⬜ pending |
| _(verifier, post-phase)_ | — | post | NIX-06 (darwin execution) | T-64-04 | — | none possible | darwin execution is unverified by construction (ROADMAP constraint 8); evaluation is the bounded mitigation. Recorded, not claimed | — | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

**None. Existing infrastructure covers every phase requirement.** The full pytest suite, the tox
environments, `ci.yml`'s 3-OS matrix, the `nix` CLI and `gh` are all in place. D-05 deliberately adds
no test file and no script. The evidence markdown files are each task's own deliverable, not Wave 0
scaffolding.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The Claude Code session is relaunched after 64-01 merges, from a shell where direnv loaded the new devShell | NIX-05 / D-09 (enables every wave-2 and wave-3 measurement) | The session PATH is frozen at launch, and no automation inside a running session can refresh it (orchestrator note 3) | Open a terminal in `/home/yuta/Documents/typsphinx`; confirm `command -v ruff` prints `/nix/store/…-ruff/bin/ruff`; launch Claude Code from that shell; run `/gsd-execute-phase 64`. The 64-02 and 64-03 preconditions confirm it mechanically |
| The NIX-08 consequence paragraph says what the finding means for the maintainer's workflow | NIX-08 / D-08 | Whether the prose draws the right workflow consequence is a judgment; the gate checks only that one finding exists | Read `64-NIX08-ENV-EVIDENCE.md` § Consequence against the four-cell matrix and the committed definitions |
| The CI run is this phase's own, on the pushed tip, started during this phase | SC#5 | Recency and identity beyond the `headSha` gate | Open the recorded run URL; confirm the head SHA, the start time and that the `Lint and Format Check` log shows `ruff check .` executing |
| The Claude Code session is relaunched after 64-05 merges, from a shell where direnv loaded the zlib-carrying devShell | NIX-02 / NIX-03 / NIX-04 re-measurement (enables every wave-5 task) | The session PATH is frozen at launch; the session that runs 64-05 predates 64-05's own edit, and no automation inside a running session can refresh it | Open a terminal in `/home/yuta/Documents/typsphinx`; set FHS to the `typsphinx-fhs-run` path grepped from `command -v ruff`'s body and confirm `"$FHS" /bin/sh -c 'test -e /usr/lib/libz.so.1'` exits 0 (it matches the `New fhs-run:` line in `64-LIBZ-FIX-EVIDENCE.md`); launch Claude Code from that shell; run `/gsd-execute-phase 64 --gaps-only`. The 64-06 preconditions confirm it mechanically |

---

## Evidence-file naming constraint

`64-VERIFICATION.md` is `gsd-verifier`'s reserved output name, and no plan writes it. The
plan-authored evidence set is:
- `64-FLAKE-EVIDENCE.md`
- `64-NIX05-WORKTREE-EVIDENCE.md`
- `64-NIX07-RENAME-EVIDENCE.md`
- `64-NIX08-ENV-EVIDENCE.md`
- `64-CI-EVIDENCE.md`
- `64-LIBZ-FIX-EVIDENCE.md` (64-05, gap closure)
- `64-GAP-REMEASURE-EVIDENCE.md` (64-06, gap closure)

The gap-closure plans never append to the first five files: their failing transcripts stay
byte-unchanged, and the re-measurement is a new record. `64-LIBZ-DIAGNOSIS.md` is the plan-phase
orchestrator's pre-planning DIAGNOSTIC, not a plan output, and closes nothing.

`COVERAGE.md` is the planner's plan-time external-API declaration, with a dated gap-closure addendum.

---

## Validation Sign-Off

The checked items are properties of the six authored plans, verified at plan time. The unchecked
item is `/gsd-validate-phase`'s to set.

- [x] All tasks have `<automated>` verify, each followed by a `<fails_when>`: 16/16 tasks across the six plans (10 in 64-01..64-04, 6 in the gap-closure plans 64-05 and 64-06)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify, because every task has one
- [x] Wave 0 covers all MISSING references: none; existing infrastructure suffices
- [x] No watch-mode flags: `gh run watch --exit-status` is a one-shot wait-for-completion with a 90-minute cap, not a watch loop
- [x] Diagnostics and genuine observations are separated: the `nix develop` runs of waves 1 and 4 are labelled DIAGNOSTIC; waves 2-3 run only behind 64-01's session precondition, and wave 5 only behind 64-05's libz discriminator
- [x] Evidence producers precede their consumer: 64-04 (wave 3) depends on 64-02 and 64-03 (wave 2), which depend on 64-01 (wave 1); 64-05 (wave 4) depends on 64-01..64-04; 64-06 (wave 5) depends on 64-05
- [x] No plan writes `64-VERIFICATION.md`
- [ ] `nyquist_compliant: true` set in frontmatter: set by `/gsd-validate-phase`, not at plan time

**Approval:** pending (`status: draft` until `/gsd-validate-phase` runs)
