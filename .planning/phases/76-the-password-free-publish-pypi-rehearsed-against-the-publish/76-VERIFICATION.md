---
phase: 76-the-password-free-publish-pypi-rehearsed-against-the-publish
verified: 2026-09-27T23:15:00Z
status: passed
score: 12/12 must-haves verified
covered_files:
  - .github/workflows/release.yml
  - .planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-01-PLAN.md
  - .planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-01-SUMMARY.md
  - .planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-02-PLAN.md
  - .planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-02-SUMMARY.md
  - .planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-03-PLAN.md
  - .planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-03-SUMMARY.md
  - .planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-ATT-EVIDENCE.md
  - .planning/phases/76-the-password-free-publish-pypi-rehearsed-against-the-publish/76-MSG06-EVIDENCE.md
  - tests/test_translator_path_quoting_gate.py
  - typsphinx/translator.py
covered_digest: "v2:sha256:314a62e959999a235c1d3aa96dc0f762758a8c678a4129848f1172db48f3d8c1"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 76: The `password:`-Free `publish-pypi`, Rehearsed Against the Published v0.9.6 — and MSG-06 Verification Report

**Phase Goal:** `release.yml`'s production publish step stops reading a long-lived secret and mints
its own OIDC token — proven to work against real PyPI before anything irreversible happens, by a
dispatch that reaches the upload endpoint and is turned away as a duplicate rather than as an unknown
publisher. In the same phase, `translator.py`'s two cross-directory relative-path DEBUG logs move to
`quote_path()`, closing the fourth and last module of the MSG-02 family.

**Verified:** 2026-09-27
**Status:** passed
**Re-verification:** No — initial verification

All evidence below was re-measured directly against the live GitHub run, live PyPI Simple JSON API,
the live GitHub Release, and the current worktree/git history — not read from `76-ATT-EVIDENCE.md` /
`76-MSG06-EVIDENCE.md` prose alone (those files were cross-checked, not trusted).

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | SC #1 — `publish-pypi`'s `Publish to PyPI` step carries no credential, nothing added in its place | ✓ VERIFIED | `git diff main -- .github/workflows/release.yml` shows exactly a 2-line deletion (`with:` / `password: ${{ secrets.PYPI_API_TOKEN }}`), no `+` lines. `grep -c PYPI_API_TOKEN` = 1 (only `TEST_PYPI_API_TOKEN` remains), `attestations`/`skip-existing` = 0, `@release/v1` = 2. `publish-testpypi` and top-level `permissions:` byte-identical to `main`. File parses as YAML with 5 jobs (`validate, build, publish-pypi, create-release, publish-testpypi`). |
| 2 | SC #2 — OIDC exchange exercised against production PyPI, turned away as duplicate not unknown-publisher | ✓ VERIFIED | Live `gh run view 36321530105`: exactly one `workflow_dispatch` run on `gsd/v0.9.7-trusted-publishing-and-release` (`headSha=987ec3fe…`, matches the pushed ref). Jobs: `Validate Release`=success, `Build Distribution`=success, `Publish to PyPI`=failure, `Publish to TestPyPI (Optional)`=skipped, `Create GitHub Release`=skipped. `grep -c "File already exists"` on `--log-failed` = 3; `grep -c invalid-publisher` = 0; `grep -c invalid-pending-publisher` = 0. |
| 3 | SC #3 — nothing reached PyPI, no release artifact created | ✓ VERIFIED | Live `curl` of PyPI Simple JSON: 38 files (matches evidence's `PRE_PYPI_FILE_COUNT`/`POST_PYPI_FILE_COUNT`), both 0.9.6 files `"provenance": null`. Live `gh release view v0.9.6`: still 3 assets, same digests/sizes as evidence's recorded fingerprint. `create-release`/`publish-testpypi` both `skipped` on the rehearsal run (confirmed above). |
| 4 | SC #4 (D-08 AMENDED) — disabling annotation absent at rehearsal, read against non-zero control | ✓ VERIFIED | Live full logs pulled independently: rehearsal run 36321530105 — `grep -c 'disabling Trusted Publishing'` = 0, `grep -c 'attestations input is ignored'` = 0. Control run 35730551619 — same two greps = 1 / 1. Evidence's own `## Rehearsal is not ATT-04` boundary sentence is present verbatim. |
| 5 | SC #5 (MSG-06) — literal single quote no longer closes DEBUG log delimiter early in either function | ✓ VERIFIED | `typsphinx/translator.py:5123` and `:5228` both interpolate `quote_path(up_path)`/`quote_path(down_path)`; `from typsphinx.pathfmt import quote_path` present at `:18`. Region-scoped grep for the old hardcoded pattern (`_compute_relative_include_path` → `_sanitize_label`) = 0; file-wide old-pattern count = 0. `tests/test_translator_path_quoting_gate.py` — 4/4 pass (re-run live). `builder.py`/`writer.py`/`template_registry.py`/`pathfmt.py` and their sibling gate tests plus `test_nested_toctree_paths.py` are byte-identical to `main` (`git diff main` empty); that test file's own 10 tests re-run and pass. |

**Score:** 5/5 roadmap success criteria verified (0 present, behavior-unverified). Plan-level must-haves (12 truths across the three PLAN.md frontmatters) all resolve to VERIFIED on the same live re-measurement; no truth required an override or was left unexercised.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `.github/workflows/release.yml` | password-free `publish-pypi` step | ✓ VERIFIED | Two-line deletion only, confirmed byte-exact against `main`. |
| `.planning/phases/.../76-ATT-EVIDENCE.md` | D-08 fixed-name evidence file, ATT-01 + ATT-02 sections | ✓ VERIFIED | Present, contains `ATT01_SC1_VERDICT = MET`, `ATT02_VERDICT = MET`, and all D-08-mandated sections (measured line numbers, dispatch command + SHA, before/after `gh run list`, job conclusions + verbatim failing lines, SC#4 grep pair against control, post-dispatch capture diff, rehearsal-is-not-ATT-04 sentence). Cross-checked against live re-measurement, not merely present. |
| `typsphinx/translator.py` | both cross-directory DEBUG logs routed through `quote_path()` | ✓ VERIFIED | Confirmed at both call sites; import present; no other function in the file touched beyond the two f-strings. |
| `tests/test_translator_path_quoting_gate.py` | fourth `*_path_quoting_gate.py` family member | ✓ VERIFIED | 4 tests, all pass on live run. |
| `.planning/phases/.../76-MSG06-EVIDENCE.md` | recorded RED (2 failed/2 passed) then GREEN (4 passed) transcript | ✓ VERIFIED | Both transcripts present in file; RED/GREEN counts match what the gate module currently reports. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `.github/workflows/release.yml` `publish-pypi` step | `pypa/gh-action-pypi-publish` Trusted Publishing path | absence of `password:` + existing `id-token: write` + `environment: pypi` | ✓ WIRED | Live rehearsal run actually took the OIDC/Sigstore path (DSSE attestations generated, `Found and verified trusted root`) rather than failing at credential/auth — this is stronger evidence than static grep, since a misconfigured OIDC setup would have failed with `invalid-publisher` instead of reaching the upload/duplicate-rejection step. |
| `gh workflow run release.yml --ref <milestone-branch> -f tag=v0.9.6` | origin's copy of `release.yml` at the dispatched SHA | `workflow_dispatch` runs the dispatched ref's copy | ✓ WIRED | `gh run view 36321530105 --json headSha` = `987ec3fe…`, which is `origin/gsd/v0.9.7-trusted-publishing-and-release`'s current tip and — confirmed via `git show 987ec3fe:.github/workflows/release.yml` — carries zero `PYPI_API_TOKEN` refs and one `TEST_PYPI_API_TOKEN` ref. |
| `typsphinx/translator.py` | `typsphinx/pathfmt.py` | module-level import | ✓ WIRED | `from typsphinx.pathfmt import quote_path` at `:18`, invoked at both call sites; no import cycle (pathfmt is a leaf module, confirmed no `typsphinx`-internal imports in it). |
| `76-ATT-EVIDENCE.md` | Phase 77 handoff | fixed filename read by Phase 77 | ✓ WIRED (structural) | File exists at the exact fixed name D-08 mandates; contents verified above. Phase 77's own read of it is out of this phase's scope to verify. |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| ATT-01 | 76-01, 76-03 | password-free `publish-pypi` step + rehearsal proving the edit took effect | ✓ SATISFIED | SC #1 truth above (76-01); ATT-02 verdict's closing sentence in `76-ATT-EVIDENCE.md` explicitly closes ATT-01's rehearsal half, corroborated by the live run taking the OIDC path. |
| ATT-02 | 76-03 | one rehearsal dispatch against production PyPI, rejected as duplicate not unknown-publisher | ✓ SATISFIED | SC #2/#3/#4 truths above, all independently re-measured live. |
| MSG-06 | 76-02 | both cross-directory DEBUG logs quoted via `quote_path()` | ✓ SATISFIED | SC #5 truth above, live test re-run. |

No orphaned requirements: REQUIREMENTS.md's phase-placement table maps exactly ATT-01/ATT-02/MSG-06 to Phase 76 (lines 156–158), and all three appear in the plans' `requirements:` frontmatter. ATT-03/ATT-04/ATT-05/ATT-06/REL-17/DOC-25 are explicitly out of this phase's scope per ROADMAP's requirement-placement table and CONTEXT.md's phase boundary — none were claimed or touched here. Note the known, owner-acknowledged stale wording: ROADMAP SC #4's prose and REQUIREMENTS.md's ATT-04 entry still name the `attestations input ignored` grep target that D-08 AMENDED (2026-09-27) superseded with the two-grep pair actually used (`disabling Trusted Publishing` / `attestations input is ignored`); the alignment is explicitly deferred to Phase 77 by owner decision and is not a Phase 76 gap.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `typsphinx/translator.py` | 6347 | `TODO-01, T-16-01` in a docstring comment | none | Pre-existing (Phase 16, commit `5f3ec4c3`), references a formal requirement/task ID, far outside the two lines this phase touched (`:5123`, `:5228`). Not a Phase 76 debt marker. |

No blockers, no warnings. `76-REVIEW.md` (code-review, standard depth, 3 files) independently reports 0 findings across all severities.

### Behavioral Spot-Checks / Probe Execution

| Behavior | Command | Result | Status |
|---|---|---|---|
| MSG-06 gate module passes | `LC_ALL=C pytest -q tests/test_translator_path_quoting_gate.py` | 4 passed | ✓ PASS |
| Sibling family + nested-toctree tests unaffected | `LC_ALL=C pytest -q tests/test_nested_toctree_paths.py` | 10 passed | ✓ PASS |
| Full suite green | `LC_ALL=C pytest -q` (run once, per constraint) | 1573 passed, 1 skipped | ✓ PASS |
| Lint/format/type gates | `ruff check .`, `black --check .`, `mypy typsphinx/` | all exit 0 | ✓ PASS |
| release.yml YAML structural integrity | `uv run python3 -c "import yaml; ..."` | 5 jobs: validate, build, publish-pypi, create-release, publish-testpypi | ✓ PASS |
| Rehearsal run job conclusions (live) | `gh run view 36321530105 --json jobs,headSha,event,headBranch` | matches SC #2 exactly | ✓ PASS |
| Exactly-one dispatch on the milestone branch (live) | `gh run list --workflow=release.yml --branch gsd/v0.9.7-trusted-publishing-and-release --event workflow_dispatch` | 1 run (36321530105) | ✓ PASS |
| SC #4 control-paired greps (live, both runs) | `gh run view {36321530105,35730551619} --log \| grep -c ...` | rehearsal 0/0, control 1/1 | ✓ PASS |
| PyPI served state unchanged (live) | `curl pypi.org/simple/typsphinx/` | 38 files, both 0.9.6 `provenance: null` | ✓ PASS |
| GitHub Release unchanged (live) | `gh release view v0.9.6 --json assets` | 3 assets, same digests as evidence | ✓ PASS |

This is a migration/infra-verification phase whose own "probes" are the live `gh`/`curl` re-measurements above (there is no `scripts/*/tests/probe-*.sh` for this phase); all were executed directly, not read from SUMMARY narration.

### Human Verification Required

None. Every observable truth was independently re-measured against live systems (GitHub Actions run logs, PyPI's Simple JSON API, the GitHub Release, and the git history) rather than accepted from SUMMARY.md or the evidence files' prose. No truth in this phase is behavior-dependent in a way that requires a human to observe (the one-way dispatch, its approval, and its rejection have already occurred and are independently verifiable via API).

### Gaps Summary

None. All 5 roadmap success criteria and all plan-level must-haves for ATT-01, ATT-02, and MSG-06 verified against live re-measurement. Exactly the three files claimed as modified (`.github/workflows/release.yml`, `typsphinx/translator.py`, `tests/test_translator_path_quoting_gate.py`) are touched outside `.planning/`; no scope creep. The only known open item — ROADMAP SC #4 / REQUIREMENTS.md ATT-04's stale grep-target wording — is explicitly deferred to Phase 77 by owner decision (D-08 AMENDED) and is not treated as a Phase 76 gap.

---

*Verified: 2026-09-27T23:15:00Z*
*Verifier: Claude (gsd-verifier)*
