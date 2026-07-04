---
phase: 02-verify-the-green-baseline
verified: 2026-07-04T00:00:00Z
status: gaps_found
score: 4/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "All 12 test-matrix jobs (3 OS x 4 Python versions) pass to completion — not just the ubuntu-only jobs (ROADMAP Phase 2 success criterion 1; TEST-01)"
    status: failed
    reason: "ci.yml's test job invokes `uv run tox -e py${{ matrix.python-version }}`, which for matrix.python-version values '3.10'/'3.11'/'3.12' produces the dotted env names `py3.10`/`py3.11`/`py3.12`. tox.ini's env_list only defines the dotless names `py39, py310, py311, py312`. tox exits 254 with `provided environments not found in configuration file: py3.10 - did you mean py310?` before a single test runs. Only the 3 Python-3.9 matrix jobs (ubuntu/macos/windows) succeed — coincidentally, because 3.9's single-digit minor form happens to be accepted. Independently reproduced by fetching job logs directly from GitHub Actions (not taken from SUMMARY narrative): run 28700980510 overall conclusion = failure; per-job conclusions show 9 of 12 `Test Python <ver> on <os>` jobs = failure (all 3.10/3.11/3.12 lanes x 3 OS), 3 = success (all three 3.9 lanes); job 85118834587 (`Test Python 3.10 on ubuntu-latest`) log confirms the exact tox error text and exit code 254. This bug pre-dates the Phase 1 pin (introduced in the tox-migration commit `063a2be`) and is unrelated to typst/sphinx/docutils pinning, but it is still a currently-red CI job, so the phase's own goal statement — 'confirmed to turn every previously-red CI job green across the full platform/Python matrix' — is not true as of this PR."
    artifacts:
      - path: ".github/workflows/ci.yml"
        issue: "The `Run tests with tox` step runs `uv run tox -e py${{ matrix.python-version }}` verbatim against the dotted matrix value, with no name-mapping layer."
      - path: "tox.ini"
        issue: "`env_list = py39, py310, py311, py312, ...` uses dotless names that never match the dotted `matrix.python-version` string for any Python other than 3.9."
    missing:
      - "Merge (or reimplement) the fix already prepared and sitting unmerged on branch `gsd/bugfix/github-ci-tox` (commit `64cd057`), which adds an explicit `matrix.include` mapping `python-version -> tox-env` (e.g. `3.10 -> py310`) so `tox -e ${{ matrix.tox-env }}` resolves correctly on every lane."
      - "Re-push/re-observe the full 12-job matrix and confirm all 12 conclude success, per this phase's own D-01 definition of done."
      - "Correct `.planning/REQUIREMENTS.md`'s TEST-01 row: it is currently checked `[x]` / marked 'Complete' in the traceability table, but ground-truth CI evidence shows this requirement is NOT satisfied. The plan-02 executor's self-marking of REQUIREMENTS.md is inaccurate and must not be trusted as evidence of completion."
---

# Phase 2: Verify the Green Baseline Verification Report

**Phase Goal:** The Phase 1 pin is confirmed to turn every previously-red CI job green across the full platform/Python matrix, and the 3-way `@preview` version sync hazard is protected by an automated test rather than manual memory.
**Verified:** 2026-07-04
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All 12 test-matrix jobs (3 OS x 4 Python) pass to completion (TEST-01, ROADMAP SC1) | ✗ FAILED | Independently re-queried `gh run view 28700980510`: overall conclusion `failure`; unique job conclusions `["failure","success"]`. Only `Test Python 3.9 on {ubuntu,macos,windows}-latest` succeeded (3/12). All 9 `3.10`/`3.11`/`3.12` x 3-OS jobs failed. Job log for `Test Python 3.10 on ubuntu-latest` (id 85118834587) shows `tox` exiting 254 with `provided environments not found in configuration file: py3.10 - did you mean py310?` — confirms the ci.yml/tox.ini env-name mismatch diagnosis in 02-02-SUMMARY.md D5. |
| 2 | The PDF-compilation integration tests pass (TEST-02) | ✓ VERIFIED | Ran in the passing `Test Python 3.9 on ubuntu-latest` job log: `====== 402 passed, 447 warnings in 26.78s ======`, and locally confirmed 8 PDF-integration tests pass (per SUMMARY; test count is 8 not the plan's stated "7", a documentation-accuracy note, not a defect). These tests never get a chance to run at all in the 9 red matrix jobs (tox errors before pytest starts) — but the requirement's text asserts the tests themselves pass, which they do wherever tox actually invokes pytest. |
| 3 | Coverage job passes and uploads to Codecov; Type Check and Build Package remain green (TEST-03, TEST-04) | ✓ VERIFIED | Re-queried `gh run view 28700980510 --json jobs`: `Code Coverage: success`, `Type Check: success`, `Build Package: success`, `Lint and Format Check: success`, `Integration Test - basic: success`, `Integration Test - advanced: success`. `CODECOV_TOKEN` absence is expected/documented (job has `fail_ci_if_error: false`); job green with upload attempted satisfies TEST-03 per the phase's own D-01 context note. |
| 4 | `docs.yml` completes end-to-end incl. the PDF-copy step (DOCS-01) | ✓ VERIFIED | Re-queried `gh run view 28700980497 --json conclusion,jobs`: overall `success`; `build-docs: success`. SUMMARY additionally documents the `Build PDF documentation (English only)` and `Copy PDF to multi-language build (English version)` steps both succeeded, and Pages-deploy/release-upload both `skipped` (correct for PR mode). |
| 5 | A new automated test guards the 3-way `@preview` version-sync hazard (ROADMAP SC5, D-03) | ✓ VERIFIED | `tests/test_preview_version_sync.py` exists (105 lines, stdlib-only `re`+`pathlib`, no stub patterns). Ran locally: `uv run pytest tests/test_preview_version_sync.py -v` → 2 passed. Independently confirmed via job log that both tests ran and passed inside a real CI job (`Test Python 3.9 on ubuntu-latest`: `test_preview_versions_identical_across_declaration_sites PASSED`, `test_all_four_packages_declared PASSED`). Independently reproduced the desync-guard behavior myself (not trusting the SUMMARY's claim): temporarily bumped `mitex` to `0.2.5` in `templates/base.typ` only, re-ran the test — it correctly FAILED with diagnostic `@preview version desync detected across declaration sites: mitex: {'writer.py': '0.2.4', 'template_engine.py': '0.2.4', 'base.typ': '0.2.5'}`; file restored, `git status` clean afterward. |

**Score:** 4/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tests/test_preview_version_sync.py` | Guard test for 3-way `@preview` version sync (D-03) | ✓ VERIFIED | Exists, substantive (regex-based cross-file comparison, no hardcoded oracle), wired (collected by standard pytest, confirmed executing and passing inside a real CI job log), and independently proven to fail loudly on a simulated desync. |
| GitHub PR against `main` with observed ci.yml + docs.yml runs | PR #104, both workflows triggered and observed | ⚠️ MIXED | PR #104 is open, base `main`, head `gsd/phase-2-verify-green-baseline` (`gh pr view 104` confirms). `docs.yml` run 28700980497: fully green. `ci.yml` run 28700980510: overall `failure` — 9/12 matrix jobs red. The artifact (the PR + its runs) exists and was genuinely observed, but the observed *result* for ci.yml does not meet the phase's own success bar. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| PR base `main` | `docs.yml` trigger | PR-to-main dispatches docs.yml in PR mode (D-02) | ✓ WIRED | Confirmed: docs run 28700980497 exists and is green; Pages-deploy/release-upload steps skipped as expected in PR mode. |
| `ci.yml` coverage job | Codecov upload | `fail_ci_if_error:false` lets job pass even with absent token (TEST-03) | ✓ WIRED | `Code Coverage: success`; token absence recorded, consistent with documented semantics. |
| `ci.yml` 12 matrix jobs | `tox -e py{ver}` → pytest collects `tests/test_preview_version_sync.py` | Standard pytest collection, no separate CI wiring needed (TEST-01) | ⚠️ PARTIAL | WIRED and confirmed passing for the 3 Python-3.9 lanes (job log shows both sync-test cases PASSED). NOT_WIRED for the other 9 lanes: `tox` itself fails to resolve the env name (`py3.10` vs `py310`) and exits before pytest ever starts, so the sync test (and the rest of the 402-test suite) never executes on those 9 jobs. The must-have's own phrasing — "all 12 matrix jobs run tox -e py{ver} which collects the new sync test" — is true for only 3 of the 12 job instances. |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| TEST-01 | 02-01, 02-02 | All matrix test jobs pass on ubuntu/macos/windows across the supported Python range | ✗ BLOCKED | 9/12 matrix jobs fail (tox env-name mismatch, pre-existing, unrelated to Phase 1 pin but still currently red). **REQUIREMENTS.md marks this `[x]` Complete — this marking is incorrect and must not be trusted; ground truth from `gh run view` contradicts it.** |
| TEST-02 | 02-01, 02-02 | The PDF-compilation integration tests pass | ✓ SATISFIED | Confirmed passing both locally and inside a real (Python 3.9) CI job log. |
| TEST-03 | 02-01, 02-02 | Coverage job passes and uploads to Codecov | ✓ SATISFIED | `Code Coverage: success` observed directly; upload attempted, absence of token documented and consistent with `fail_ci_if_error:false` semantics. |
| TEST-04 | 02-01, 02-02 | Type Check and Build Package jobs remain green | ✓ SATISFIED | `Type Check: success`, `Build Package: success` observed directly. |
| DOCS-01 | 02-01, 02-02 | `docs.yml` completes end-to-end incl. the PDF-copy step | ✓ SATISFIED | `docs.yml` run 28700980497 overall `success`, confirmed directly. |

No orphaned requirements found — REQUIREMENTS.md's Phase 2 row set (TEST-01..04, DOCS-01) matches exactly what both plans declared.

### Anti-Patterns Found

None. The single file modified by this phase (`tests/test_preview_version_sync.py`) contains no debt markers (TBD/FIXME/XXX/TODO/HACK/PLACEHOLDER), no stub returns, and its logic was independently exercised and behaves correctly (see Observable Truth #5).

### Human Verification Required

None — all must-haves were verifiable directly against `gh run` data and local test execution; no visual/real-time/external-service judgment calls remain open.

### Gaps Summary

**The phase's core claim is not fully true.** Phase 2's stated goal is that the Phase 1 pin "turns every previously-red CI job green across the full platform/Python matrix." The observed ground truth (re-queried independently, not taken from SUMMARY.md) is that `ci.yml` run 28700980510 has overall conclusion **failure**, with **9 of the 12** `Test Python <ver> on <os>` matrix jobs still red. Only the 3 Python-3.9 lanes (ubuntu/macos/windows) are green.

The root cause is real and precisely diagnosed by the 02-02-SUMMARY.md finding (independently confirmed here via direct job-log inspection): `ci.yml` invokes `tox -e py${{ matrix.python-version }}`, producing dotted env names (`py3.10`, `py3.11`, `py3.12`) that do not match `tox.ini`'s dotless `env_list` (`py310`, `py311`, `py312`). This is a **pre-existing, unrelated** defect (introduced in the tox-migration commit `063a2be`, well before the Phase 1 pin) — it is not a regression caused by this phase or Phase 1, and the plan's D-04 discipline (surface, don't silently patch) was correctly followed by the executor. A ready-made fix already exists, unmerged, on branch `gsd/bugfix/github-ci-tox` (commit `64cd057`), adding an explicit `matrix.include` python-version→tox-env mapping.

However, "pre-existing and unrelated" does not make the job green, and the phase's own success criterion #1 is explicit: "All 12 test-matrix jobs ... pass to completion — not just the ubuntu-only jobs." That criterion is false today. The remaining 4 truths (PDF integration tests, coverage, type-check/build, docs.yml end-to-end, and the new `@preview` sync-guard test) are all genuinely verified — independently re-confirmed here via direct `gh run view`/job-log queries and a local reproduction of the sync-test's desync-detection behavior, not merely accepted from the SUMMARY narrative.

`.planning/REQUIREMENTS.md` currently marks **TEST-01** as `[x]` / "Complete" in its traceability table. This marking is **not supported by ground truth** and should not be trusted — it must be reverted to reflect the actual blocked state until the 12-job matrix is observed fully green.

**Recommended remediation (not performed by this verifier):** merge (or reimplement) the `gsd/bugfix/github-ci-tox` fix into `ci.yml`, re-push, and re-observe the full 12-job matrix before this phase can be considered to have met its own goal. This is a small, well-scoped, already-drafted fix — likely a single short follow-up plan rather than a full re-plan of the phase.

---

*Verified: 2026-07-04*
*Verifier: Claude (gsd-verifier)*
