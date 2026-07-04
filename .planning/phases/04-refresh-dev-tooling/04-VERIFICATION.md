---
phase: 04-refresh-dev-tooling
verified: 2026-07-05T00:00:00Z
status: passed
score: 8/8 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 4: Refresh Dev Tooling Verification Report

**Phase Goal:** Dev-tooling floors and CI action versions are refreshed conservatively, without introducing risky default-behavior flips unrelated to the CI-repair goal.
**Verified:** 2026-07-05
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Black/ruff/tox/tox-uv dev-tooling floors bumped to floor+ceiling bounds, deliberately staying under the next major (SC1, D-02/D-07) | ✓ VERIFIED | `pyproject.toml` line 41-43: `black>=26,<27`, `ruff>=0.15,<0.16`, `tox>=4.56,<5`, `tox-uv>=1.35,<2`; `tox.ini` mirrors identically ([testenv:lint] deps, [tox] requires) |
| 2 | pytest/mypy accept the already-green resolved versions (9.1.1/2.1.0) with a next-major guard ceiling, per D-01's user-owned deviation superseding the literal ROADMAP SC1/REQUIREMENTS wording | ✓ VERIFIED | `pyproject.toml`: `pytest>=8.4,<10`, `mypy>=1.13,<3.0`; `uv.lock`: `pytest` 9.1.1, `mypy` 2.1.0 resolved — ceilings do not force a downgrade (9.1.1<10, 2.1.0<3) |
| 3 | `pyproject.toml [dev]` and `tox.ini` per-env deps stay in lockstep (byte-identical constraint strings, D-02b) | ✓ VERIFIED | Direct diff of both files: `pytest>=8.4,<10`, `black>=26,<27`, `ruff>=0.15,<0.16`, `mypy>=1.13,<3.0` identical in both surfaces; `tox-uv` uses `~=1.35` in tox.ini (packaging-spec-equivalent workaround for a tox ini-parser comma-split bug, documented in a code comment in tox.ini itself) vs. literal `>=1.35,<2` in pyproject.toml — deliberate, documented, functionally equivalent |
| 4 | `uv.lock` regenerated with no unexpected resolved-version bumps | ✓ VERIFIED | `uv.lock` resolves black 26.5.1 / ruff 0.15.20 / tox 4.56.1 / tox-uv 1.35.2 / pytest 9.1.1 / mypy 2.1.0 — matches D-01/D-02/D-07/D-08 target versions exactly |
| 5 | GitHub Actions versions verified/refreshed for hosted-runner compatibility (SC2): `upload-artifact` and `download-artifact` bumped off Node-20 ahead of the 2026-09-16 removal; the other four actions confirmed current | ✓ VERIFIED | `ci.yml` (4x), `docs.yml` (2x), `release.yml` (1x) all `actions/upload-artifact@v7`; `release.yml` (3x) `actions/download-artifact@v8`. Independently fetched `action.yml` from GitHub for both tags: both declare `runs.using: node24` (confirmed live, not trusted from SUMMARY). `checkout@v6`, `setup-python@v6`, `setup-uv@v7`, `codecov-action@v5` unchanged and confirmed current in all workflow files |
| 6 | Node-20 straggler (`softprops/action-gh-release@v2`) explicitly tracked/deferred, not silently closed (RESEARCH A2 obligation) | ✓ VERIFIED | Independently fetched `action.yml` for `softprops/action-gh-release@v2`: confirmed `runs.using: "node20"`. Recorded in 04-02-SUMMARY.md and 04-04-SUMMARY.md as a tracked/deferred Phase-5 candidate — matches the required non-silent-closure obligation |
| 7 | CI remains green after the tooling refresh, no regression introduced (SC3) | ✓ VERIFIED | Live `gh` CLI query (not SUMMARY narration): PR #105 `state: OPEN`, `mergeable: MERGEABLE`, `mergeStateStatus: CLEAN`, base `main`, head `d99748d`. `ci.yml` run 28711976093: `conclusion: success`, 18/18 jobs unique-conclusion `["success"]` (full 3.10-3.13 x 3-OS matrix + lint/type/coverage/build/integration). `docs.yml` run 28711976097: `conclusion: success` |
| 8 | Phase-3 leftover Python-3.9 text references folded in and cleaned (D-04, part of TOOL-01) | ✓ VERIFIED | `README.md` line 36: "Python 3.10 or higher"; `pyproject.toml` lines 111-112: ruff `UP035`/`UP006` comments read "Python 3.10+ support" — no surviving 3.9 reference in either file |

**Score:** 8/8 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pyproject.toml` | `[dev]` block bumped, 6 constraint strings | ✓ VERIFIED | Confirmed all 6 strings present exactly as specced |
| `tox.ini` | `[testenv]`/`[testenv:lint]`/`[testenv:type]` deps + `[tox] requires` mirrored | ✓ VERIFIED | Confirmed; `tox-uv` uses documented `~=1.35` workaround |
| `uv.lock` | Regenerated, minimal diff, no resolved-version drift | ✓ VERIFIED | Confirmed resolved versions match target set exactly |
| `.github/workflows/ci.yml` | 4x `upload-artifact@v7` | ✓ VERIFIED | Lines 47, 126, 155, 188 |
| `.github/workflows/docs.yml` | 2x `upload-artifact@v7` | ✓ VERIFIED | Lines 46, 52 |
| `.github/workflows/release.yml` | 1x `upload-artifact@v7`, 3x `download-artifact@v8` | ✓ VERIFIED | Lines 100; 116, 137, 206 |
| `README.md` | Lines 36/323 updated to 3.10 | ✓ VERIFIED | Confirmed (line 323 content merged into current README structure — Python 3.10+ present, no 3.9 remnant) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `pyproject.toml [dev]` | `tox.ini` per-env `deps` | Byte-identical constraint strings (D-02b) | ✓ WIRED | 5/6 identical; tox-uv intentionally uses a documented `~=` equivalent to dodge a tox parser bug |
| `uv.lock` | CI (`ci.yml`, `docs.yml`) | `runner = uv-venv-lock-runner` resolves from lockfile | ✓ WIRED | Observed green CI run confirms the lock resolves and runs cleanly across the full matrix |
| Workflow files | GitHub Actions runtime | `actions/upload-artifact@v7` / `download-artifact@v8` pins | ✓ WIRED | Independently confirmed `node24` via live `action.yml` fetch; PR #105's green CI run also exercises `upload-artifact@v7` in the coverage/build jobs |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|--------------|----------------|--------------|--------|----------|
| TOOL-01 | 04-01, 04-03, 04-04 | Dev-tooling floors refreshed conservatively | ✓ SATISFIED | Floor+ceiling bounds on 6 tools verified in both surfaces; D-01 deviation (accept green pytest/mypy majors + guard ceiling) is the intended, superseding interpretation per orchestrator's critical_evaluation_context |
| TOOL-02 | 04-02, 04-04 | GitHub Actions versions verified/refreshed for hosted-runner compatibility | ✓ SATISFIED | Two genuinely-stale Node-20 actions bumped to Node-24; remaining four confirmed current; one known straggler (softprops) explicitly tracked, not silently closed |

No orphaned requirements: REQUIREMENTS.md traceability table maps exactly TOOL-01 and TOOL-02 to Phase 4, matching the `requirements:` fields declared across all 4 plans.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | None found (`TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` scan across all phase-modified files: `pyproject.toml`, `tox.ini`, `README.md`, `.github/workflows/{ci,docs,release}.yml`) | — | — |

### Behavioral Spot-Checks / Live Verification

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| PR #105 state/mergeability | `gh pr view 105 --json state,mergeable,mergeStateStatus,baseRefName,headRefOid` | `OPEN` / `MERGEABLE` / `CLEAN` / `main` / `d99748d` | ✓ PASS |
| ci.yml observed run | `gh run view 28711976093 --json conclusion,jobs` | `success`, 18/18 jobs unique `["success"]` | ✓ PASS |
| docs.yml observed run | `gh run view 28711976097 --json conclusion` | `success` | ✓ PASS |
| upload-artifact@v7 Node runtime | `curl raw.githubusercontent.com/actions/upload-artifact/v7/action.yml` | `runs.using: node24` | ✓ PASS |
| download-artifact@v8 Node runtime | `curl raw.githubusercontent.com/actions/download-artifact/v8/action.yml` | `runs.using: node24` | ✓ PASS |
| softprops/action-gh-release@v2 straggler | `curl raw.githubusercontent.com/softprops/action-gh-release/v2/action.yml` | `runs.using: "node20"` — confirms the tracked/deferred finding is real, not overstated | ✓ PASS |

### Human Verification Required

None. All must-haves are objectively verifiable via config-file inspection and live CI/PR state; no visual, UX, or judgment-dependent behavior is in scope for this infra/tooling phase.

### Non-Blocking Follow-Up Finding (does not affect phase status)

**PROJECT.md's Key Decisions table has not yet been updated to log the D-01 deviation (accepting pytest 9.1.1/mypy 2.1.0 as known-good with next-major ceilings, superseding the literal `pytest~=8.4`/`mypy<2.0` wording) or the D-03 amendment (upload-artifact/download-artifact Node-20 bump).** `04-CONTEXT.md` explicitly instructs both to be recorded there ("D-01 must be logged here at phase transition"). Checked directly: `.planning/PROJECT.md`'s Key Decisions table (last touched by the Phase-3 `a097ed3 docs(phase-03): evolve PROJECT.md after phase completion` commit) contains no pytest/mypy/D-01/D-03 entry, and its "Active" requirements section still shows the Phase-4 line item as an unchecked `[ ]` bullet.

This mirrors the established pattern from Phases 1-3, where the PROJECT.md "evolve after phase completion" commit is a distinct, later step in the GSD workflow (occurring after the phase's own VERIFICATION.md is written) — consistent with `STATE.md` currently showing `status: verifying` for Phase 4, i.e., the transition step has not run yet. It is **not** one of the three ROADMAP Success Criteria and is not listed as a `must_have` in any of the four PLAN frontmatters, so it does not block this phase's goal-achievement verdict. It **is** a required action before the milestone is considered fully closed — flagging it here so it is not lost. Recommend running `/gsd-transition` (or the equivalent PROJECT.md evolution step) before proceeding to Phase 5, adding rows for D-01 and the D-03 amendment.

### Gaps Summary

No gaps block phase goal achievement. All three ROADMAP success criteria (conservative dev-tooling floor bumps with next-major ceilings; GitHub Actions hosted-runner-compatibility refresh; CI remains green with no regression) are independently confirmed against the live codebase and live GitHub state — not merely asserted by SUMMARY.md. One non-blocking documentation follow-up (PROJECT.md Key Decisions table) is noted above for closure during phase transition.

---

_Verified: 2026-07-05_
_Verifier: Claude (gsd-verifier)_
