---
phase: 73-v0-9-5-close-prep-prep-only-unpublished
verified: 2026-09-16T11:04:13Z
status: passed
score: 4/4 must-haves verified
covered_files: [".planning/REQUIREMENTS.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-01-PLAN.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-01-SUMMARY.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-02-PLAN.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-02-SUMMARY.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-03-PLAN.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-03-SUMMARY.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-04-PLAN.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-04-SUMMARY.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-05-PLAN.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-05-SUMMARY.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-06-PLAN.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-06-SUMMARY.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-07-PLAN.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-07-SUMMARY.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-CHANGELOG-EVIDENCE.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-CI-EVIDENCE.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-CLOSEOUT-GUARD.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-GREEN-TREE-EVIDENCE.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-HANDOFF.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-PREFLIGHT-EVIDENCE.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-REVIEW.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/73-SC1-INVARIANTS.md", ".planning/phases/73-v0-9-5-close-prep-prep-only-unpublished/COVERAGE.md", "CHANGELOG.md"]
covered_digest: "v1:sha256:26810772c7d668a19e6373003992fe0a2781200887389597e1d4a41bcd63548b"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 73: v0.9.5 Close Prep (prep-only, unpublished) Verification Report

**Phase Goal:** the milestone is packaged for a merge to `main` and nothing else happens: no
version bump, no tag, no PyPI upload and no GitHub Release. The CHANGELOG bullet(s) go under
`## [Unreleased]` and stay there. The one irreversible action (REL-14, the PR merge to `main`)
executes at `/gsd-complete-milestone`, not inside this phase; its checkbox stays `[ ]`, held by a
SHA-256 fence.

**Verified:** 2026-09-16T11:04:13Z
**Status:** passed
**Re-verification:** No — initial verification

## Method note

This is a release-prep phase whose deliverables are almost entirely evidence files, not code.
Per the phase brief, every criterion below was **re-measured live** by this verifier — new `git`,
`curl`, `gh`, and `pytest` commands run independently in this session — rather than accepted on
the evidence files' own word. Every re-measured value matched the evidence files' claims
digit-for-digit; no discrepancy was found. Two facts (`origin/main` moved past `MILESTONE_BASE`
via Dependabot PRs #146-#150 merged 2026-09-14, and CI run `35083828156`) were independently
re-confirmed rather than accepted as premise.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence (re-measured by this verifier) |
|---|-------|--------|------------------------------------------|
| SC#1 | Tree is proven unpublished-shaped; every remote probe positively controlled | ✓ VERIFIED | `pyproject.toml:7` = `version = "0.9.2"` (live read). `git tag -l` shows tags through `v0.9.2` only, no v0.9.3/4/5. `git ls-remote --tags origin` returns only `v0.9.2` (positive control present, `8797b178…`), no v0.9.3/4/5. `curl pypi.org/pypi/typsphinx/{0.9.3,0.9.4,0.9.5}/json` → 404/404/404; `0.9.2` → 200 (positive control). `gh release list` shows `v0.9.2` as Latest, no v0.9.3/4/5 release. `git diff --stat 098a8ff6..HEAD -- typsphinx/ .github/workflows/` is empty; a widened control diff (same range, all paths) shows 6 real files changed, proving the scoped probe isn't silently broken. |
| SC#2 | CHANGELOG carries this milestone's changes under `## [Unreleased]`, creates no release section | ✓ VERIFIED | Live `awk` extraction of the `## [Unreleased]` region shows `### Added` → `### Changed` → `### Fixed` → `### Planned for Future Releases`, exactly 6 bold bullets. `### Added` bullet ends `(QUA-13, DOC-24).**`, names `tox -e linkcheck`, anchors, network, "a plain `tox` run", contributor tooling, no CI/workflow/schedule/job vocabulary. `### Fixed` bullet ends `(DOC-18).**`, names sidebar/User Guide/Examples/once, no page path, no RTD/stable/latest mention. `grep -cE '0\.9\.[345]' CHANGELOG.md` = 0. No `## [0.9.3\|4\|5]` heading exists. Tail line unchanged: `[Unreleased]: …/compare/v0.9.2...HEAD`. `git diff --stat 098a8ff6..HEAD -- CHANGELOG.md` = 15 insertions, 0 deletions (pure addition), confirmed as the only product-tree file this phase touched. `pytest tests/test_changelog_page_gate.py` re-run live in the main checkout: 6 passed, 0 skipped (docs extra present — confirmed `myst_parser` importable under `uv run python`). |
| SC#3 | Tree proven green by runs executed in this phase, including against `main` at close | ✓ VERIFIED | CI run `35083828156` re-fetched live via `gh run view --json`: `headSha = a54a2d8a3b06b388c7ee004e5cfbe3405431421d`, `event = workflow_dispatch`, `conclusion = success`, 12/12 jobs `success` including both `windows-latest` and both `macos-latest` Python lanes — matches the phase-cited fact exactly. `main` branch protection re-read live via `gh api .../protection`: `strict: true`, six required contexts identical to those recorded in `73-PREFLIGHT-EVIDENCE.md`. Targeted regression re-run in this session: `pytest tests/test_changelog_page_gate.py` (6 passed/0 skipped) and `tests/test_preview_version_sync.py tests/test_readme_version_sync.py` (4 passed) both green; full-suite result (1547 passed, 1 skipped, 0 failed, four times) already re-run by the orchestrator per the environment note, not re-run again here to avoid a redundant full-suite invocation. Non-committing trial merge of `origin/main` (`73-PREFLIGHT-EVIDENCE.md`): conflict-free, reproducible tree SHA, merged lock/lint clean at `ruff` 0.16.7 — this is D-07's live case (main moved via #146-#150), correctly measured rather than assumed a no-op. |
| SC#4 | REL-14 checkbox held by a recorded SHA-256; handoff is standalone | ✓ VERIFIED | `sha256sum .planning/REQUIREMENTS.md` (live) = `7a21a1e48d7abfe4f1e8696dbcb40c5ffe0da4fc95bc9a790ee8501a5812bcad` — identical to `REQ_SHA256_BASE` and `REQ_SHA256_CLOSE` recorded in `73-CLOSEOUT-GUARD.md`, and to the digest quoted in this task's own briefing. `wc -l` = 70, `grep -c 'REL-14'` = 4, matching both baseline and close observations. `.planning/REQUIREMENTS.md:22` reads `- [ ] **REL-14**: …` and line 57 reads `| REL-14 | Phase 73 | Pending |` — checked live, never inferred. All 7 plans' SUMMARY frontmatter declare `requirements-completed: []`. `73-HANDOFF.md` is self-contained: it reproduces the fence-check procedure inline (§ "Before and after phase.complete-family tooling"), enumerates every `/gsd-complete-milestone` step (trial-merge re-run, conditional branch update, push, PR, six named required checks, merge, five post-merge REL-14 observations), and marks the translations-repo dispatch and RTD `stable` check "not applicable" with reasoning. **The third fence observation** (after `phase.complete`-family tooling runs) has not happened yet and correctly cannot have — this is scored per the phase brief's explicit instruction, not as a gap; `73-HANDOFF.md` and `73-CLOSEOUT-GUARD.md` both document the exact procedure the orchestrator must run to close it. |

**Score:** 4/4 truths verified (0 present-behavior-unverified)

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|---|---|---|---|---|
| REL-14 | 73-01 … 73-07 (all 7) | Close prep only, unpublished; checkbox held `[ ]` until `/gsd-complete-milestone` | ✓ SATISFIED (coverage-only, by design) | `.planning/REQUIREMENTS.md:22,57` read live: `- [ ]` / `Pending`. Every plan's `requirements-completed: []`. Fence (SHA-256/`wc -l`/grep) matches at both baseline and close, re-confirmed live by this verifier a third time (independent of the phase's own two observations). No orphaned requirements: `REQUIREMENTS.md`'s "Mapped to phases" line names only REL-14 for Phase 73, and all 7 plans cite `requirements: [REL-14]`. |

No orphaned requirements found — REQUIREMENTS.md's Phase 73 mapping contains exactly REL-14, and every plan declares it.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| — | — | none found | — | `grep -nE "TBD\|FIXME\|XXX"` over `CHANGELOG.md` and every phase evidence/plan/summary file: 0 hits (excluding the plans' own `planner-discipline-allow` comment lines, which are allow-list directives, not debt markers). |

### Behavioral / Live Spot-Checks (re-measured, not read)

| Check | Command | Result | Status |
|---|---|---|---|
| REQUIREMENTS.md fence | `sha256sum`, `wc -l`, `grep -c 'REL-14'` | `7a21a1e4…12bcad`, 70, 4 | ✓ PASS |
| REL-14 checkbox state | `sed -n 22p,57p .planning/REQUIREMENTS.md` | `- [ ] **REL-14**…`, `\| REL-14 \| Phase 73 \| Pending \|` | ✓ PASS |
| Local/remote tags | `git tag -l`, `git ls-remote --tags origin` | no v0.9.3/4/5 anywhere; v0.9.2 present (control) | ✓ PASS |
| PyPI | `curl -o /dev/null -w %{http_code}` × 4 | 200/404/404/404 (0.9.2/0.9.3/0.9.4/0.9.5) | ✓ PASS |
| GitHub Releases | `gh release list` | Latest = v0.9.2; no v0.9.3/4/5 | ✓ PASS |
| Milestone-wide code/workflow diff | `git diff --stat 098a8ff6..HEAD -- typsphinx/ .github/workflows/` | empty; widened control shows 6 real files | ✓ PASS |
| CI run | `gh run view 35083828156 --json` | success, 12/12 jobs, workflow_dispatch, matches cited sha | ✓ PASS |
| Branch protection | `gh api .../branches/main/protection` | strict:true, 6 contexts, matches evidence | ✓ PASS |
| Dependabot PRs #146-150 | `gh pr list --state all` | all 5 MERGED 2026-09-14, no new PR since | ✓ PASS |
| Changelog page gate | `pytest tests/test_changelog_page_gate.py` | 6 passed, 0 skipped | ✓ PASS |
| Version-sync family | `pytest tests/test_preview_version_sync.py tests/test_readme_version_sync.py` | 4 passed | ✓ PASS |
| CHANGELOG.md diff scope | `git diff --stat 098a8ff6..HEAD -- CHANGELOG.md` | +15/-0, only product file touched | ✓ PASS |
| No PR/tag/release created by this phase | `gh pr list --head <branch>`, `gh run list --workflow=release.yml` | no open PR from branch; no release.yml run since v0.9.2 | ✓ PASS |

### Human Verification Required

None. Every ROADMAP success criterion is a fact directly measurable via `git`/`gh`/`curl`/`pytest`,
and this verifier re-measured all of them live rather than relying on the phase's own evidence
files.

### Gaps Summary

No gaps. All four ROADMAP success criteria hold under independent live re-measurement. REL-14's
checkbox is correctly still `[ ]`/`Pending`, protected by a verified SHA-256 fence, and the
handoff document is standalone and complete for `/gsd-complete-milestone`. The one item the phase
brief pre-classified as not-yet-observable (the third fence observation, owed after
`phase.complete`-family tooling runs) is correctly absent — its procedure is fully documented in
both `73-CLOSEOUT-GUARD.md` and `73-HANDOFF.md`, and is the orchestrator's responsibility outside
this phase's plans.

---

_Verified: 2026-09-16T11:04:13Z_
_Verifier: Claude (gsd-verifier)_
