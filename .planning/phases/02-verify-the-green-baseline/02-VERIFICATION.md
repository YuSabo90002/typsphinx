---
phase: 02-verify-the-green-baseline
verified: 2026-07-04T00:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 4/5
  gaps_closed:
    - "All 12 test-matrix jobs (3 OS x 4 Python versions) pass to completion — not just the ubuntu-only jobs (ROADMAP Phase 2 success criterion 1; TEST-01)"
  gaps_remaining: []
  regressions: []
---

# Phase 2: Verify the Green Baseline Verification Report

**Phase Goal:** The Phase 1 pin is confirmed to turn every previously-red CI job green across the full platform/Python matrix, and the 3-way `@preview` version sync hazard is protected by an automated test rather than manual memory.
**Verified:** 2026-07-04
**Status:** passed
**Re-verification:** Yes — after gap closure (plan 02-03)

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All 12 test-matrix jobs (3 OS x 4 Python versions) pass to completion — not just ubuntu-only | ✓ VERIFIED | Independently re-queried (not taken from SUMMARY narrative): `gh run view 28702240846 --json conclusion,jobs` → overall `success`, headSha `3e3acdfb1053de32d481f81bd497fe61fb23f09c`, 18 total jobs, unique job-conclusion set = `["success"]`. Enumerated all 12 `Test Python <ver> on <os>` job names directly and confirmed each is `success`, including the 9 lanes (3.10/3.11/3.12 × ubuntu/windows/macos) that were red in the prior verification's run 28700980510. Confirmed the previously-red `Test Python 3.10 on macos-latest` lane actually executes the real test suite (not just resolving the tox env) by grepping its job log for individual `PASSED` lines. Root-cause fix confirmed in `.github/workflows/ci.yml`: `git diff main` shows only a `matrix.include` list (python-version → dotless tox-env) added and the run step changed to `uv run tox -e ${{ matrix.tox-env }}` — no other job/step touched, matching the plan's scope-boundary. |
| 2 | The 7 PDF-compilation integration tests pass (`TestPDFGenerationIntegration`, `TestE2ETypstCompilation`) | ✓ VERIFIED | Grepped the `Test Python 3.9 on ubuntu-latest` job log inside run 28702240846 directly: all 4 `TestPDFGenerationIntegration` tests and all 4 `TestE2ETypstCompilation` tests show `PASSED` (8 tests total — the plan/roadmap text says "7," collection shows 8; a pre-existing documentation-count discrepancy, not a test failure, already flagged in 02-01-SUMMARY.md). Full suite line: `402 passed, 447 warnings in 26.78s`. |
| 3 | The coverage job passes AND uploads to Codecov; Type Check and Build Package remain green with no regression | ⚠️ SATISFIED WITH CAVEAT (see reasoning below) | `gh run view 28702240846 --json jobs` confirms `Code Coverage: success`, `Type Check: success`, `Build Package: success`, `Lint and Format Check: success`, both `Integration Test - basic`/`advanced: success`. However, independently pulled the raw step log (`gh run view 28702240846 --log`) and confirmed the Codecov **upload itself fails**: `error - Upload queued for processing failed: {"message":"Token required - not valid tokenless upload"}`. Independently confirmed via `gh secret list --repo YuSabo90002/typsphinx` that the repo secrets are only `PYPI_API_TOKEN` and `TEST_PYPI_API_TOKEN` — **`CODECOV_TOKEN` is genuinely absent**, not merely unset in this run. The job stays green only because `fail_ci_if_error: false` (confirmed in the log: `CC_FAIL_ON_ERROR: false`). See "Criterion 3 reasoning" below for the disposition. |
| 4 | `sphinx-build -b typstpdf` produces a PDF and `docs.yml` completes end-to-end, including the multi-language PDF-copy step | ✓ VERIFIED | Independently re-queried `gh run view 28702240814 --json conclusion,jobs` → overall `success`, `build-docs: success`, same headSha `3e3acdfb1053de32d481f81bd497fe61fb23f09c` as the green CI run (same push). Pulled per-step conclusions directly: `Build PDF documentation (English only): success`, `Copy PDF to multi-language build (English version): success` (the exact step that previously errored on a missing PDF under the kai break). `Deploy to GitHub Pages: skipped`, `Upload PDF to Release: skipped` — correct for PR-mode (D-02), confirming no unintended side effects. |
| 5 | A new automated test asserts the `@preview` package versions in writer.py, template_engine.py, and templates/base.typ are identical | ✓ VERIFIED | `tests/test_preview_version_sync.py` exists (106 lines, stdlib `re`+`pathlib` only, no stub patterns, no debt markers). Re-ran locally as a regression check: `uv run pytest tests/test_preview_version_sync.py -v` → both `test_preview_versions_identical_across_declaration_sites` and `test_all_four_packages_declared` PASSED. (The prior verification already independently reproduced the desync-guard's failure behavior by simulating a single-file version bump; this re-verification performs the lighter-weight regression check per the re-verification optimization rule, since this truth was not part of the closed gap and nothing touched this file since.) Confirmed the test runs inside the real, now-green CI matrix job log (`Test Python 3.9 on ubuntu-latest`) as part of the 402-test run. |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Criterion 3 reasoning (Codecov upload — judgment call required by task)

The literal text of ROADMAP success criterion 3 is "the coverage job passes AND uploads to Codecov." Ground truth: the **job** passes; the **upload** does not — it fails with `Token required - not valid tokenless upload` because `CODECOV_TOKEN` is absent from repo secrets (confirmed via `gh secret list`, not inferred).

**Disposition: SATISFIED, not a phase-blocking gap.** Reasoning:
1. **Pre-existing, not introduced by this phase.** The absent `CODECOV_TOKEN` and the resulting tokenless-upload failure were present in the very first observed run of this phase (02-02-SUMMARY.md D3, run 28700980510) and remain identical in the final green run (28702240846). Nothing this phase did caused or could have fixed this — it is a repo-secret configuration gap, not a code defect in scope for Phase 2.
2. **The phase's own D-01/D-04 context explicitly pre-decided this exact scenario.** 02-CONTEXT.md states: "the coverage job sets `fail_ci_if_error: false` ... so the job passes even if the Codecov upload is skipped/unauthenticated. TEST-03's 'uploads to Codecov' is therefore best-effort at the job level; treat the job going green (with an upload attempt) as the pass condition, and note if the token is absent." This is precisely what happened: job green, upload attempted, absence noted.
3. **D-04 discipline was followed correctly across all three plans** — each SUMMARY explicitly surfaces this as a finding rather than silently patching or silently ignoring it, and none of them claim the actual Codecov dashboard reflects real coverage.
4. **Classification:** this is a config/follow-up item (add a `CODECOV_TOKEN` repo secret), not a code defect, and not attributable to the Phase 1 pin or any Phase 2 change. It should NOT block phase completion.

**Recommendation:** Track as a non-blocking WARNING / follow-up backlog item: "Add `CODECOV_TOKEN` repo secret so Codecov uploads actually succeed (job already green via `fail_ci_if_error: false`; only the live coverage dashboard/badge is affected)." This does not gate Phase 2 or Phase 3 and does not need a gap-closure plan.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tests/test_preview_version_sync.py` | Guard test for 3-way `@preview` version sync (D-03) | ✓ VERIFIED | Exists, substantive, wired (runs under standard pytest collection, confirmed executing inside the now-green CI matrix), no regressions since the prior verification. |
| `.github/workflows/ci.yml` (matrix.include mapping) | Maps each `python-version` to its dotless `tox-env` so `uv run tox -e ${{ matrix.tox-env }}` resolves on every lane | ✓ VERIFIED | Confirmed present via direct file read and `git diff main`: `matrix.include` list with 4 entries (3.9→py39, 3.10→py310, 3.11→py311, 3.12→py312); run step reads `uv run tox -e ${{ matrix.tox-env }}`. Diff is scoped to exactly this change — no other job/step modified, matching the plan's acceptance criteria. |
| GitHub PR against `main` with observed ci.yml + docs.yml runs | PR #104, both workflows triggered and observed fully green | ✓ VERIFIED | `gh pr view 104`: state `OPEN`, base `main`, head `gsd/phase-2-verify-green-baseline`. CI run 28702240846: `success`, 18/18 jobs success. Docs run 28702240814: `success`, `build-docs` job success including the PDF-copy step. Both share headSha `3e3acdfb1053de32d481f81bd497fe61fb23f09c` (the gap-closure push). |
| `.planning/REQUIREMENTS.md` TEST-01 row re-marked `[x]` / Complete | Re-marked only after the new green run was observed, citing the new run ID | ✓ VERIFIED | Line 28: `- [x] **TEST-01**: ... <!-- RESOLVED (Phase 2 gap-closure): 12/12 matrix jobs green in ci.yml run 28702240846 after mapping matrix.python-version to dotless tox env names. -->` — cites the correct new green run (28702240846), **not** the old red run 28700980510. Traceability row (line 96): `| TEST-01 | Phase 2 | Complete |`. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `ci.yml` `matrix.include` | `tox.ini` `env_list` | Each mapped `tox-env` (py39/py310/py311/py312) exists in tox.ini's dotless env_list (line 2) | ✓ WIRED | Confirmed by reading `tox.ini` line 2 directly (`env_list = py39, py310, py311, py312, lint, type, cov, docs`) against `ci.yml`'s 4 `matrix.include` entries — exact match, and the observed run proves resolution (no more exit-254 env-not-found errors on any lane). |
| PR base `main` | `docs.yml` trigger | PR-to-main dispatches docs.yml in PR mode (D-02) | ✓ WIRED | Docs run 28702240814 exists for the same push (headSha match), concludes success; Pages-deploy/release-upload steps confirmed `skipped`. |
| `ci.yml` 12 matrix jobs | `tox -e ${{ matrix.tox-env }}` → pytest collects `tests/test_preview_version_sync.py` | Standard pytest collection, no separate CI wiring needed | ✓ WIRED | All 12 lanes now resolve a real tox env and run the full 402-test suite (verified by grepping individual `PASSED` lines from multiple lanes' logs, not just the overall conclusion field). |
| `ci.yml` coverage job | Codecov upload | `fail_ci_if_error:false` lets the job pass even though the upload itself fails tokenless | ⚠️ PARTIAL (accepted — see Criterion 3 reasoning) | Job green; upload genuinely fails (`Token required - not valid tokenless upload`); `CODECOV_TOKEN` confirmed absent from repo secrets via `gh secret list`. Judged non-blocking per Criterion 3 reasoning above. |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|-----------------|-------------|--------|----------|
| TEST-01 | 02-01, 02-02, 02-03 | All matrix test jobs pass on ubuntu/macos/windows across the supported Python range | ✓ SATISFIED | 12/12 matrix jobs `success` in run 28702240846, independently confirmed via `gh run view`. REQUIREMENTS.md correctly re-marked `[x]` / Complete citing the correct new green run ID (28702240846), not the stale red run (28700980510). |
| TEST-02 | 02-01, 02-02 | The PDF-compilation integration tests pass | ✓ SATISFIED | 8/8 tests PASSED in the CI job log (confirmed above); also passing locally per 02-01-SUMMARY.md. |
| TEST-03 | 02-01, 02-02 | Coverage job passes and uploads to Codecov | ✓ SATISFIED (with recorded caveat) | Job green; upload attempted but rejected tokenless due to absent `CODECOV_TOKEN` — pre-existing, non-blocking, tracked as a follow-up (see Criterion 3 reasoning). |
| TEST-04 | 02-01, 02-02 | Type Check and Build Package jobs remain green | ✓ SATISFIED | `Type Check: success`, `Build Package: success` confirmed directly in run 28702240846. |
| DOCS-01 | 02-01, 02-02 | `docs.yml` completes end-to-end incl. the PDF-copy step | ✓ SATISFIED | `build-docs: success`, PDF-copy step `success`, confirmed in run 28702240814. |

**No orphaned requirements found.** REQUIREMENTS.md's Phase 2 traceability rows (TEST-01..04, DOCS-01) match exactly the requirement IDs declared across all three plans' frontmatter (`02-01-PLAN.md`/`02-02-PLAN.md`: all 5; `02-03-PLAN.md`: TEST-01 only, as a gap-closure plan). All 5 rows are now `Complete` in the traceability table, and all 5 checkbox lines under "Tests & Coverage" / "Docs Build" are `[x]`.

### Anti-Patterns Found

None. Files modified across this phase (`tests/test_preview_version_sync.py`, `.github/workflows/ci.yml`, `.planning/REQUIREMENTS.md`) contain no debt markers (TBD/FIXME/XXX/TODO/HACK/PLACEHOLDER), no stub returns, and the `ci.yml` diff against `main` is scoped exactly to the documented fix (a 9-line matrix.include addition + a 1-line run-step change), touching no other job.

### Deferred / Non-Blocking Follow-ups

- **`CODECOV_TOKEN` repo secret absent** (Criterion 3): Codecov uploads fail tokenless on every run; the coverage job itself stays green via `fail_ci_if_error: false`. Confirmed via `gh secret list` that only `PYPI_API_TOKEN`/`TEST_PYPI_API_TOKEN` exist. Recommended as a maintainer follow-up (add the secret), not a phase gap.
- **`codecov/codecov-action@v5` deprecated `file:` input** (cosmetic): logs a warning that `file` should be `files`; does not affect the job's pass/fail outcome. Noted in 02-02-SUMMARY.md, not fixed, out of scope.
- **PDF integration test count discrepancy** (documentation-only): ROADMAP/plan text says "7" PDF-compilation integration tests; actual collection is 8 (4 in each of the two named test classes). All 8 pass; this is a stale count in planning docs, not a functional gap.

### Human Verification Required

None. All 5 truths, all artifacts, and all key links were verified directly against live `gh run`/`gh secret`/`git diff` output and local test execution — no visual, real-time, or external-service judgment calls remain open.

### Gaps Summary

No gaps. The single gap from the prior verification (Observable Truth #1 / TEST-01: 9 of 12 matrix jobs red due to a `ci.yml`/`tox.ini` env-name mismatch) was closed by plan 02-03: the `matrix.include` mapping fix was applied, re-pushed onto PR #104, and the resulting run (28702240846) was independently confirmed fully green across all 18 jobs (12/12 matrix lanes + lint + type-check + coverage + build + 2 integration jobs), with `docs.yml` (run 28702240814) confirmed still green end-to-end including the PDF-copy step. `REQUIREMENTS.md`'s TEST-01 re-mark correctly cites the new green run ID rather than the stale red one.

The one open item — the Codecov upload failing tokenless due to an absent `CODECOV_TOKEN` repo secret — is judged non-blocking (pre-existing, config-only, explicitly pre-anticipated by this phase's own D-01/TEST-03 context notes) and is recorded as a follow-up rather than a phase-blocking gap.

**Phase goal achieved.** All 12 matrix jobs are green, the 8 PDF-compilation integration tests pass, coverage/type-check/build remain green with the Codecov caveat noted above, docs.yml completes end-to-end including the PDF-copy step, and the `@preview` version-sync guard test protects the 3-way hazard automatically.

---

*Verified: 2026-07-04*
*Verifier: Claude (gsd-verifier)*
