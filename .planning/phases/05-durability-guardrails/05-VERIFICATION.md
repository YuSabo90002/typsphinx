---
phase: 05-durability-guardrails
verified: 2026-07-05T05:45:54Z
status: passed
score: 4/4 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 5: Durability Guardrails Verification Report

**Phase Goal:** CI enforces lockfile currency and proactively surfaces future dependency drift, so the silent multi-year rot this milestone fixes cannot recur unnoticed.
**Verified:** 2026-07-05T05:45:54Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | CI uses `uv sync --locked` (or equivalent gate) so a stale/silently-rewritten lockfile fails the build loudly. | VERIFIED | `grep -n "uv sync" .github/workflows/*.yml \| grep -v -- "--locked"` on disk returns empty; all 9 sites (ci.yml x6 @ lines 41/71/92/113/151/179, docs.yml x1 @ line 31, release.yml x2 @ lines 36/93) carry `--locked`, `--extra` flags preserved. Independently re-confirmed via `gh run view 28730645396` → `{"conclusion":"success","name":"CI"}` — the full 19-job matrix passed on the in-sync tree with the gate active. |
| 2 | A weekly, non-blocking scheduled CI job resolves latest deps and reports drift early without blocking merges. | VERIFIED | `.github/workflows/drift.yml` exists on disk, valid YAML, `on.schedule[0].cron == '0 0 * * 1'` + `workflow_dispatch` present; `permissions == {contents: read, issues: write}`; `uv lock --upgrade` (line 29) precedes `uv sync --extra dev --extra docs --locked` (line 32); `uv run tox -e cov,docs-pdf` present; `if: failure()` step wired with `gh issue list`/`create`/`comment` dedup keyed on `--label drift`; no `git add/commit/push` of the lock. Independently re-confirmed: `gh run view 28730876125` → `{"conclusion":"success","name":"Dependency Drift Check"}` (post-merge `workflow_dispatch` ran to completion on latest-resolved deps). Non-blocking independently re-confirmed: `gh api .../branches/main/protection/required_status_checks --jq '.contexts'` returns 8 contexts (Test Python 3.10-3.13 on ubuntu-latest, Lint and Format Check, Type Check, Code Coverage, Build Package) — no `drift`/`Dependency Drift Check` entry. |
| 3 | `dependabot.yml` groups the sphinx/docutils/typst cluster so a lone bump can't reintroduce the `kai`-class break. | VERIFIED | `.github/dependabot.yml` on disk: `pip` ecosystem entry has `groups.sphinx-typst-stack` with `patterns: [sphinx*, docutils*, typst*]` and `exclude-patterns: [sphinx-autodoc-typehints, sphinx-intl]` (confirmed via `yaml.safe_load` assertion, PASS). `github-actions` ecosystem entry has no `groups:` key (only one `groups:` block in the whole file) — untouched as required. |
| 4 | A CI status badge is visible on `README.md`. | VERIFIED | `README.md` line 3: `[![CI](https://github.com/YuSabo90002/typsphinx/actions/workflows/ci.yml/badge.svg)](https://github.com/YuSabo90002/typsphinx/actions/workflows/ci.yml)` — exactly one match for `actions/workflows/ci.yml/badge.svg` (`grep -c` == 1), correct image URL and link target (Actions page, not the raw SVG). Placed first in the badge row; five pre-existing badges (PyPI, Python Support, License, black, Documentation) intact. Live-render visual confirmation was performed by the developer per 05-04-SUMMARY (human-verify checkpoint) — the underlying markdown is independently confirmed correct here.

**Score:** 4/4 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.github/workflows/ci.yml` | All `uv sync` sites carry `--locked`; `softprops@v3` | VERIFIED | 6/6 sites locked; `softprops/action-gh-release` not referenced in this file (N/A — only docs.yml/release.yml use it) |
| `.github/workflows/docs.yml` | `uv sync --locked`; `softprops@v3` at line 67 | VERIFIED | 1/1 site locked; `softprops/action-gh-release@v3` confirmed at line 67; zero `@v2` refs anywhere |
| `.github/workflows/release.yml` | `uv sync --locked` x2; `softprops@v3` at line 177 | VERIFIED | 2/2 sites locked; `softprops/action-gh-release@v3` confirmed at line 177 |
| `.github/workflows/drift.yml` | New standalone weekly+dispatch drift detector | VERIFIED | Exists, valid YAML, all required elements present (see Truth #2); wired to run via `gh run view 28730876125` success |
| `.github/dependabot.yml` | `sphinx-typst-stack` group under `pip`; `github-actions` untouched | VERIFIED | Confirmed via YAML-parse assertion (see Truth #3) |
| `README.md` | CI badge in badge row | VERIFIED | Confirmed via grep + line inspection (see Truth #4) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `uv sync --locked` (all 9 sites) | `uv.lock` / `pyproject.toml` | Fails build on desync | WIRED | CI run 28730645396 all 19 jobs green — the gate is active and does not break the in-sync tree (proves the check runs, not a no-op) |
| `drift.yml` `uv lock --upgrade` → `uv sync ...--locked` → `tox -e cov,docs-pdf` | Latest PyPI resolution | Exercises forward drift | WIRED | Run 28730876125 success — full step chain executed end-to-end on latest-resolved deps |
| `drift.yml` failure path | GitHub Issues API | `gh issue list/create/comment --label drift` | WIRED (code path present; not exercised this run since run succeeded — no forward drift found, correctly no issue filed) | Static presence + correct `if: failure()` gating confirmed; this is the expected "no issue on success" behavior per D-06, not a gap |
| `dependabot.yml` `sphinx-typst-stack` group | Future Dependabot PR grouping | Bundles sphinx/docutils/typst bumps | WIRED (config-level; behavioral proof requires an actual Dependabot PR, which is a future/scheduled event outside this phase's window — reasonable given DUR-03's nature) | YAML config correctly scoped and validated |
| `README.md` CI badge | `ci.yml` Actions page | Markdown badge link | WIRED | Correct image URL + link target; developer visually confirmed live render per 05-04-SUMMARY |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| DUR-01 | 05-01 | `uv sync --locked` gate at all 9 sites | SATISFIED | Static grep on disk + CI run 28730645396 success |
| DUR-02 | 05-03, 05-04 | Weekly non-blocking drift-detection job | SATISFIED | `drift.yml` static checks + `gh run view 28730876125` success + required-checks API confirms non-blocking |
| DUR-03 | 05-02 | `dependabot.yml` sphinx/docutils/typst grouping | SATISFIED | YAML-parse assertion PASS |
| DUR-04 | 05-02, 05-04 | CI status badge on README | SATISFIED | grep + line confirmation; live render confirmed by developer |

No orphaned requirements — REQUIREMENTS.md traceability table maps all four DUR-01..04 to Phase 5, and all four appear in plan frontmatter (`05-01: [DUR-01]`, `05-02: [DUR-03, DUR-04]`, `05-03: [DUR-02]`, `05-04: [DUR-01, DUR-02, DUR-03, DUR-04]`).

### Anti-Patterns Found

None. Scanned all six phase-modified files (`ci.yml`, `docs.yml`, `release.yml`, `drift.yml`, `dependabot.yml`, `README.md`) for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` — zero matches.

### Behavioral Spot-Checks / Probe Execution

This phase's verification model is CI-native (the plan explicitly defers empirical proof to GitHub Actions runs, since the local NixOS environment cannot run the project's uv/tox toolchain). In place of local spot-checks, the following live GitHub state was independently re-queried by this verifier (not taken from SUMMARY narration):

| Check | Command | Result | Status |
|-------|---------|--------|--------|
| PR #106 merged to main | `gh pr view 106 --json state,mergeCommit,mergedAt` | `state: MERGED`, commit `733067f19d417e96721835b234a8ac526d5812f9`, merged `2026-07-05T05:35:39Z` | PASS |
| ci.yml green on the merge-carrying PR | `gh run view 28730645396 --json status,conclusion,name` | `conclusion: success`, `name: CI` | PASS |
| drift.yml post-merge dispatch completes | `gh run view 28730876125 --json status,conclusion,name` | `conclusion: success`, `name: Dependency Drift Check` | PASS |
| drift job absent from required checks | `gh api .../branches/main/protection/required_status_checks --jq '.contexts'` | 8 contexts listed, no `drift`/`Dependency Drift Check` entry | PASS |
| Local branch matches merged main | `git diff origin/main HEAD --stat` | Only `.planning/` tracking files differ (ROADMAP.md, STATE.md, 05-04-SUMMARY.md) — zero source-file drift | PASS |

## Human Verification Required

None outstanding. The plan's own human-verify checkpoints (05-04 Task 2 and Task 3 — CI-visible confirmation and drift.yml/D-11 sign-off) were already completed by the developer during phase execution, per 05-04-SUMMARY.md, and this verifier independently re-confirmed the underlying GitHub state (PR merge, CI run, drift run, branch-protection contexts) rather than trusting the SUMMARY narration alone.

One item is explicitly and correctly recorded as a **deferred, signed-off item** rather than a gap: D-11's `softprops/action-gh-release@v3` runtime behavior (docs.yml:67, release.yml:177) is tag-gated and was not exercised by the merged PR (Pitfall 3, honestly disclosed in both 05-01-SUMMARY and 05-04-SUMMARY). This is not a DUR-01..04 requirement — it is a carried-over D-11 hardening item explicitly out of this phase's success-criteria scope, deferred to the next real release tag with developer sign-off. It does not block phase-goal achievement.

## Gaps Summary

None. All four ROADMAP success criteria (SC-1..SC-4) and all four requirement IDs (DUR-01..04) are independently verified against the live codebase and live GitHub state — not merely asserted by SUMMARY.md. Static artifacts on disk match what was merged to `main` (verified via `git diff origin/main HEAD --stat`, `gh pr view 106`). Runtime evidence (CI run 28730645396, drift run 28730876125, required-status-checks API) was re-queried directly by this verifier, not taken on faith from the SUMMARY.

---

_Verified: 2026-07-05T05:45:54Z_
_Verifier: Claude (gsd-verifier)_
