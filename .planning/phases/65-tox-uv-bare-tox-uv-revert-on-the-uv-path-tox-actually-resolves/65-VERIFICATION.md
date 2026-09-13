---
phase: 65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves
verified: 2026-09-12T17:20:00Z
status: passed
score: 8/8 must-haves verified
covered_files:
  - .planning/REQUIREMENTS.md
  - .planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-01-PLAN.md
  - .planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-01-SUMMARY.md
  - .planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-02-PLAN.md
  - .planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-02-SUMMARY.md
  - .planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-CI-EVIDENCE.md
  - .planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-CONTEXT.md
  - .planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-REVERT-EVIDENCE.md
  - .planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-REVIEW.md
  - pyproject.toml
  - tests/test_toolchain_config_gate.py
  - tox.ini
  - uv.lock
covered_digest: "v1:sha256:6ba654ebedfe3ff435cbebc817871c028d23e6e0e195bfe0942300e31ce04043"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 65: `tox-uv-bare` → `tox-uv` Revert, on the uv Path tox Actually Resolves — Verification Report

**Phase Goal:** the QUA-04 constraint that forced `-bare` (the bundled `uv` wheel cannot exec on
NixOS) is dissolved by Phase 64's FHS wrapper, so the repository returns to the upstream `tox-uv`
package. The swap itself is mechanical; the primary verification target is which `uv` binary a real
tox run resolved, plus an isolated outside-FHS control that fails on the uv path rather than
earlier, plus one completed all-lanes-green CI run on the post-revert tip (SC#1–SC#4).

**Verified:** 2026-09-12
**Status:** passed
**Re-verification:** No — initial verification

All measurements below were re-run live against the actual codebase and live GitHub state in this
session — none are transcribed from SUMMARY.md or the evidence files without independent
re-confirmation.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC#1 — `pyproject.toml` declares `tox-uv` (not `tox-uv-bare`), `uv.lock` regenerated in the same commit, `uv sync --extra dev --locked` accepts it | ✓ VERIFIED | `pyproject.toml:38` = `"tox-uv>=1.35,<2",` (re-read live); `git show --name-only d32eb5db…` lists exactly `pyproject.toml`, `tox.ini`, `uv.lock`, `tests/test_toolchain_config_gate.py`; `uv.lock` header `version = 1`/`revision = 3`, `tox-uv` 1.36.0, `tox-uv-bare` 1.36.0 (same version), `uv` 0.12.13 block present (re-grepped live) |
| 2 | SC#2 — `tox.ini`'s `requires` names `tox-uv` in the comma-free `~=` form and `tox` starts | ✓ VERIFIED | `tox.ini:11` = `requires = tox-uv~=1.35` (re-read live); `tox config -e py312 --core -k requires` re-run live, prints `  tox-uv~=1.35` |
| 3 | SC#3 (D-02) — from inside a real, cold `tox -e py312` run, the resolved `uv` is observed: bundled branch, this worktree's/checkout's own `.venv/bin/uv`, at exactly the `uv.lock` version, no `TOX_UV_PATH` | ✓ VERIFIED | Live re-run in this session (`tox -vv -e py312 -r --notest`) in the main checkout: `using bundled uv from: <cwd>/.venv/bin/uv`, unique banner `DEBUG uv 0.12.13` (= `uv.lock`'s `uv` version), zero PATH/TOX_UV_PATH/self-provisioning lines |
| 4 | SC#3 (D-03) — the isolated outside-FHS control (nix-interpreter venv) fails exactly on the `uv` exec (`exit 127`, `Could not start dynamically linked executable`) and nothing earlier | ✓ VERIFIED | Independently reproduced in this session: built a fresh venv on `/nix/store/…-python3-3.13.13`, installed `tox==4.56.1 tox-uv==1.36.0 tox-uv-bare==1.36.0 uv==0.12.13` (the exact `uv.lock` versions), ran outside FHS (`/usr/lib/libz.so.1` absent) by absolute path against this tree's `tox.ini` → `using bundled uv from: <ctrl>/bin/uv`, then `Could not start dynamically linked executable: <ctrl>/bin/uv`, `exit 127`, `py312: FAIL code 127`, with the bundled-branch discovery line preceding it and nothing failing earlier |
| 5 | SC#3 — both the literal and amended readings of SC#3 are reported separately (D-01) | ✓ VERIFIED | `65-REVERT-EVIDENCE.md` § "SC#3 literal and amended readings" states the literal dichotomy is falsified (both mechanisms name one file) and reports the amended reading (branch/path/version/outcome/isolation) separately, exactly as ROADMAP's AMENDED block requires |
| 6 | SC#4 — one CI run dispatched on the post-revert tip has completed, every job's conclusion transcribed, both `windows-latest` and both `macos-latest` lanes named individually, ruff's verdict from `Lint and Format Check`/`Run lint with tox` | ✓ VERIFIED | Live `gh run view 34681968010 --json status,conclusion,workflowName,headSha,url` → `completed`/`success`/`CI`/`headSha` = `d9c7555323e843b5a389ed4354ce656d2fd05ca2`; live `gh run view … --json jobs` → 12/12 `success`, including `Test Python 3.12/3.13 on windows-latest` and `on macos-latest`, all `success`; `65-CI-EVIDENCE.md` quotes ruff's/black's CI verdict verbatim from the `Run lint with tox` step |
| 7 | The revert is fenced: no change under `typsphinx/`, `.github/workflows/`, `flake.nix`, `flake.lock`, `CLAUDE.md` since the milestone's merge-base with `main`; no tracked file outside `.planning/` names `TOX_UV_PATH`; no decoy branch pushed | ✓ VERIFIED | Live `git diff --name-only $(git merge-base HEAD main) HEAD -- typsphinx .github/workflows` empty; live `git diff --name-only d32eb5db… d9c75553… -- .github/workflows CLAUDE.md flake.nix flake.lock` empty; `git grep TOX_UV_PATH` outside `.planning/`: no match; `git ls-remote --heads origin \| grep milestone`: no decoy present |
| 8 | Origin's canonical branch is fast-forwarded to the post-revert tip with no force, no tag | ✓ VERIFIED | Live `git ls-remote --heads origin refs/heads/gsd/v0.9.3-toolchain-and-dependency-update-repair` → `d9c7555323e843b5a389ed4354ce656d2fd05ca2`, matches recorded `PUSHED_SHA`; `d32eb5db…` and `d9c75553…` both confirmed ancestors of current HEAD via live `git merge-base --is-ancestor` |

**Score:** 8/8 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pyproject.toml` | dev extra names `tox-uv`, not `tox-uv-bare` | ✓ VERIFIED | Line 38 = `"tox-uv>=1.35,<2",`; full dev list re-read, no `tox-uv-bare` literal entry |
| `tox.ini` | comma-free `requires = tox-uv~=1.35` | ✓ VERIFIED | Line 11 exact match; lines 4-10 rationale comment intentionally still names `tox-uv-bare` (Phase 68 DOC-20, per D-06 — not a defect of this phase) |
| `uv.lock` | regenerated by plain `uv lock`, carries `tox-uv`, `tox-uv-bare` (same version), `uv` | ✓ VERIFIED | Header `version=1`/`revision=3` unchanged; all three package blocks present at matching versions (`tox-uv`/`tox-uv-bare` both 1.36.0, `uv` 0.12.13) |
| `tests/test_toolchain_config_gate.py` | inverted G5 gate `test_dev_extra_pins_tox_uv_not_tox_uv_bare` | ✓ VERIFIED | Function present; live `pytest tests/test_toolchain_config_gate.py -q` → `4 passed`; old name (`test_dev_extra_pins_tox_uv_bare_not_tox_uv`) absent |
| `65-REVERT-EVIDENCE.md` | head check, RED/GREEN gate, lock regen, D-02/D-03 observations, SC#3 readings, requirement closure, D-05 addendum | ✓ VERIFIED | All sections present; transcripts cross-checked against live re-measurement (see Behavioral Spot-Checks) |
| `65-CI-EVIDENCE.md` | branch census, fence, push, dispatch, 12-job census, per-lane uv resolution, TOX-04 closure | ✓ VERIFIED | All sections present; run ID, headSha, and job census cross-checked live via `gh` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `pyproject.toml` dev extra | `uv.lock` | one plain `uv lock`, same commit | ✓ WIRED | `git show --name-only` on `d32eb5db…` lists `pyproject.toml` and `uv.lock` together |
| `tox.ini [tox] requires` | tox startup | tox's ini-list loader | ✓ WIRED | `tox config -e py312 --core -k requires` parses one clean requirement, `tox --showconfig -e py312` exits 0 |
| `tox_uv/_venv.py` bundled branch | this checkout's `.venv/bin/uv` | `from uv import find_uv_bin` | ✓ WIRED (behaviorally proven) | Live cold `tox -vv -e py312 -r --notest` logs `using bundled uv from: <cwd>/.venv/bin/uv` |
| local canonical branch | `origin/gsd/v0.9.3-…` | `git push`, fast-forward | ✓ WIRED | Live `git ls-remote` matches `PUSHED_SHA`; ancestor checks hold |
| `gh workflow run CI --ref …` | `ci.yml` 12 jobs | `workflow_dispatch` | ✓ WIRED | Live `gh run view` confirms `event: workflow_dispatch`, `headSha` match, 12/12 success |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Gate inversion holds at HEAD | `uv run pytest tests/test_toolchain_config_gate.py -q` | `4 passed` | ✓ PASS |
| tox parses the comma-free `requires` | `tox config -e py312 --core -k requires` | lists `  tox-uv~=1.35` | ✓ PASS |
| ruff/black clean at HEAD | `ruff check .` / `black --check .` | `All checks passed!` / `355 files would be left unchanged.` | ✓ PASS |
| Bundled `uv` resolution inside FHS, cold | `tox -vv -e py312 -r --notest` (live, main checkout) | `using bundled uv from: <cwd>/.venv/bin/uv`, `DEBUG uv 0.12.13`, no PATH/TOX_UV_PATH/self-provisioning line | ✓ PASS |
| Isolated outside-FHS control fails exactly on the uv exec | independently built nix-interpreter venv, lock-pinned installs, `python -m tox -vv -e py312 --workdir … -r` outside FHS | `using bundled uv from: <ctrl>/bin/uv` → `Could not start dynamically linked executable` → `exit 127` → `py312: FAIL code 127`, nothing earlier failed | ✓ PASS |
| Origin CI run for TOX-04 is real and green | `gh run view 34681968010 --json status,conclusion,jobs` | `completed`/`success`, 12/12 jobs `success` | ✓ PASS |
| `@preview` version-sync gate unaffected | `pytest tests/test_preview_version_sync.py -q` | `3 passed` | ✓ PASS |
| Main-checkout re-sync to lock-pinned uv (D-05) actually happened | `uv --version`; `test -x .venv/bin/uv` | `uv 0.12.13`; `exit:0` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| TOX-01 | 65-01 | `pyproject.toml` declares `tox-uv`, `uv.lock` regenerated in lockstep | ✓ SATISFIED | Live re-read of `pyproject.toml`/`uv.lock`; `uv sync --extra dev --locked` behavior confirmed by the recorded transcript and the fact the main checkout now runs on `.venv/bin/uv` |
| TOX-02 | 65-01 | `tox.ini` comma-free `~=` form, tox starts | ✓ SATISFIED | Live `tox config`/`tox --showconfig` |
| TOX-03 | 65-01 | uv resolution observed from inside a real tox run + isolated outside-FHS control | ✓ SATISFIED | Both D-02 and D-03 independently reproduced live in this session (see Behavioral Spot-Checks) |
| TOX-04 | 65-02 | CI green on the revert across every lane, CI is the authority | ✓ SATISFIED | Live `gh run view` confirms run `34681968010` completed, 12/12 success, correct `headSha` |

**Tracking discrepancy (non-blocking, Info):** `.planning/REQUIREMENTS.md` still shows `TOX-04` as
`[ ]` unchecked and "Pending" in its coverage table (lines 48, 138), even though the technical
evidence for TOX-04 is fully satisfied. `git log` shows `TOX-01`..`TOX-03` were flipped to
`[x]`/"Complete" by plan `65-01`'s completion commit (`dfcc4616`), but no subsequent commit updated
the `TOX-04` line after plan `65-02` completed. This is a tracking/bookkeeping gap in
`REQUIREMENTS.md`, not a functional defect in the revert or the CI proof — recommend it be corrected
(checkbox + coverage table row) before this phase/milestone is marked complete, so `REQUIREMENTS.md`
does not silently drift from what was actually verified.

### Anti-Patterns Found

None. `pyproject.toml`, `tox.ini`, and `tests/test_toolchain_config_gate.py` (the only files this
phase's revert commit touches) were grepped live for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` — zero
matches. `65-REVIEW.md` (0 critical / 0 warning / 2 info) independently confirms this; both Info
items (IN-01: `tox.ini`'s stale rationale comment, deferred to Phase 68 DOC-20 per D-06; IN-02:
docstring duplication, pre-existing pattern) are pre-existing/deferred, not new defects, and are not
blocking.

### Human Verification Required

None. Every truth in this phase is either a static/config fact (SC#1, SC#2) or a state-transition /
isolation-boundary invariant that was independently re-exercised live in this verification session
(SC#3's D-02 bundled-branch observation and D-03 outside-FHS control) or a remote CI state directly
queried via `gh` (SC#4). No visual, UX, or unreproducible-external-service judgment is required.

### Gaps Summary

No gaps. All four requirements (TOX-01..TOX-04) and all four ROADMAP success criteria (including
SC#3's AMENDED block, read separately per D-01) are met, each confirmed by live re-measurement in
this verification session rather than by trusting SUMMARY.md or the evidence files' own prose. The
sole finding is the non-blocking `REQUIREMENTS.md` tracking discrepancy noted above (TOX-04's
checkbox/coverage-table row not yet flipped), which does not affect the phase goal's achievement.

---

_Verified: 2026-09-12_
_Verifier: Claude (gsd-verifier)_
