---
phase: 46-v0-7-1-release-prep-prep-only
verified: 2026-08-11T00:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 46: v0.7.1 Release Prep (prep-only) Verification Report

**Phase Goal:** The v0.7.1 tree is ready to publish and proven green, with zero irreversible action
taken — no tag, nothing pushed to PyPI, no GitHub Release. REL-04 is deliberately scoped as
prep-plus-handoff and does not close in this phase; its acceptance evidence is a real tag push,
generated only at `/gsd-complete-milestone`.

**Verified:** 2026-08-11
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Phase 46 Success Criteria, verbatim)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `pyproject.toml` is the sole `0.7.1` version literal, `uv.lock`/`README.md` moved in lockstep, editable-install metadata regenerated, all three version-sync guard tests green | ✓ VERIFIED | Independently confirmed: `grep '^version = ' pyproject.toml` → `0.7.1`; `uv.lock`'s `typsphinx` entry → `version = "0.7.1"`; `README.md:342` → `Stable (v0.7.1)`; `uv run python -c "import typsphinx; print(typsphinx.__version__)"` → `0.7.1`; `uv run pytest tests/test_preview_version_sync.py tests/test_readme_version_sync.py -q` → 4 passed. |
| 2 | `CHANGELOG.md` carries a curated `## [0.7.1]` entry covering this milestone's requirements, explicitly calling out CONF-08 and CONF-09 as breaking, tail link block advances, `docs/source/changelog.rst` current | ✓ VERIFIED | Read `CHANGELOG.md` directly: `## [0.7.1] - 2026-08-11` heading present; lead paragraph states "this patch release can break a working configuration"; three `**Breaking:**` markers (CONF-11, CONF-12, `typst_authors`/CONF-10 removal); CONF-08 and CONF-09 both called out under `### Added`/`### Changed`; tail block has `[0.7.1]:` release-tag line and `[Unreleased]:` re-pointed to `v0.7.1...HEAD`. `docs/source/changelog.rst` structurally includes `CHANGELOG.md` verbatim via `myst_parser.sphinx_` (`.. include:: ../../CHANGELOG.md`), so it is current by construction. `tests/test_changelog_page_gate.py`'s `RELEASE_VERSIONS` tuple confirmed to include `"0.7.1"` (line 63); `uv run pytest tests/test_changelog_page_gate.py -q` → 6 passed. |
| 3 | Post-bump tree proven green **live**: full pytest, black/ruff/mypy, full-corpus `-b typstpdf` gate, both docs builds, milestone invariants asserted mechanically | ✓ VERIFIED | Live re-fetch of CI run `31458368833` via `gh run view 31458368833 --json jobs,conclusion,status,headSha` independently confirms `headSha=26b2e6c...` (the recorded post-bump commit) and all 12 jobs `success` (6 OS×version test lanes, Lint and Format Check, Type Check, Code Coverage, Build Package, Integration Test basic/advanced) — matches `46-CI-EVIDENCE.md` exactly, not merely trusted. Local half (`46-GREEN-TREE-EVIDENCE.md`) records both docs builds, the full-corpus gate, and a `ja` build, all green — figures internally consistent and cross-checked against the git-diff-derived file scope. |
| 4 | REL-04's in-phase share discharged (workflow carries `astral-sh/setup-uv` + `Set up Python` ahead of the extractor call; extractor runs correctly against `## [0.7.1]`), remainder explicitly owed, **not treated as REL-04 closed** | ✓ VERIFIED | Directly read `.github/workflows/release.yml` lines 156-200: `Install uv` (astral-sh/setup-uv@v7) at line 162 and `Set up Python` at line 167, both ahead of the `Generate release notes` step's `uv run python scripts/extract_changelog_section.py` call at line 197. `.planning/REQUIREMENTS.md` confirmed unedited by this phase (`git diff --name-only -- .planning/REQUIREMENTS.md` empty) — REL-04 and REL-06 both remain `[ ]`/"Pending" in Traceability. `46-HANDOFF.md` and `46-REL04-EVIDENCE.md` explicitly and repeatedly state REL-04 remains open. |
| 5 | No irreversible action: `git tag -l v0.7.1` and `git ls-remote --tags origin v0.7.1` both empty at phase end; standalone handoff checklist exists covering merge→tag→release.yml→PyPI+GitHub Release→second tag→RTD measurement | ✓ VERIFIED | Directly run in this verification session: `git tag -l v0.7.1` → empty (exit 0); `git ls-remote --tags origin v0.7.1` → empty (exit 0). `46-HANDOFF.md` exists as a 7-item checklist covering exactly this chain (PR merge → tag push → `release.yml` run-to-completion incl. `create-release` → translations-repo pin/tag → RTD `stable` confirmation → REQUIREMENTS.md flip → CHANGELOG re-date/extractor re-confirm). |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Note on Rule 3 (documented plan-verification-command bug)

Both plans 46-01 and 46-05 record that the literal acceptance command `git diff origin/main..HEAD --
typsphinx/` is non-empty (independently confirmed: 1383 diff lines) because `origin/main`'s
merge-base with this branch (`9b2b76b`) predates Phases 43–45.2's legitimate `typsphinx/` work under
this project's `branching_strategy: milestone`. The corrected anchor `c72be91..HEAD` (the tip
immediately after Phase 46's own D-20 merge commit) is independently confirmed empty:
`git diff c72be91..HEAD -- typsphinx/` → 0 lines, and `c72be91` resolves to a real commit
(`merge(46-01): merge origin/main (PR #131) and repair Windows claim-page keys`). This proves Phase 46
itself made zero `typsphinx/` edits. Per the task instructions, this is recorded as a documented plan
defect, not scored as a gap.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pyproject.toml` | sole `0.7.1` literal | ✓ VERIFIED | `version = "0.7.1"` at line 7, confirmed by direct read |
| `uv.lock` | `typsphinx` entry `0.7.1` | ✓ VERIFIED | Confirmed via `grep -A2 'name = "typsphinx"' uv.lock` |
| `README.md` | Status line `0.7.1` | ✓ VERIFIED | Line 342 confirmed |
| `CHANGELOG.md` | curated `## [0.7.1]` entry | ✓ VERIFIED | Read in full — breaking-change callouts, tail link block present |
| `docs/source/changelog.rst` | current at `0.7.1` | ✓ VERIFIED | Includes `CHANGELOG.md` directly via myst_parser; `RELEASE_VERSIONS` gate updated |
| `.github/workflows/release.yml` | `create-release` job carries uv setup | ✓ VERIFIED | Lines 162/167 directly read, ahead of the extractor call at line 197 |
| `46-HANDOFF.md` | standalone publish checklist | ✓ VERIFIED | 7-item checklist covering the full publish chain, read in full |
| `46-CI-EVIDENCE.md` | CI authority record | ✓ VERIFIED | Cross-checked live against `gh run view 31458368833` — exact match |
| `46-SC4-INVARIANTS.md` | milestone invariant sweep | ✓ VERIFIED | Read in full; dependency-array byte-identity and `@preview` count independently plausible given `pyproject.toml` diff shown |
| `46-REL04-EVIDENCE.md` | REL-04 precondition record | ✓ VERIFIED | Read in full; cross-checked against direct `release.yml` read |
| `.planning/REQUIREMENTS.md` | REL-04/REL-06 rows unedited (`Pending`) | ✓ VERIFIED | Confirmed via direct `grep` — both rows still `[ ]`/"Pending", no phase commit touches this file |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `release.yml` `create-release` job | `scripts/extract_changelog_section.py` | `uv run python scripts/... "${TAG#v}"` at line 197 | ✓ WIRED | Setup steps (uv, Python) present ahead of the call; confirmed by direct file read |
| `docs/source/changelog.rst` | `CHANGELOG.md` | `.. include:: ../../CHANGELOG.md` (myst_parser) | ✓ WIRED | Confirmed directly — DOC-12 lockstep is structural, not a manual copy |
| Pushed commit `26b2e6c` | GitHub Actions `ci.yml` run `31458368833` | `headSha` match | ✓ WIRED | Live `gh run view` confirms `headSha` equality and `conclusion: success` |

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REL-06 | 46-01–46-06 | v0.7.1 released (bump/curate/prove; publish deferred) | ✓ SATISFIED (prep-only scope) | All five SCs above; publish half explicitly deferred to `/gsd-complete-milestone`, matching REL-06's own wording |
| REL-04 | 46-05, 46-06 | GitHub Release body sourced from curated CHANGELOG, proven by real tag push | ✓ SATISFIED (in-phase preconditions only; requirement itself correctly left open) | `46-REL04-EVIDENCE.md`; `.planning/REQUIREMENTS.md` REL-04 row confirmed still `Pending` |

No orphaned requirements found — `.planning/REQUIREMENTS.md`'s "Phase 46" mapping lists exactly REL-06 and REL-04, both claimed across the six plans' `requirements:` frontmatter.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `CHANGELOG.md` | 381 | `TODO-01` | ℹ️ Info | Not a debt marker — a pre-existing (pre-Phase-46) requirement-ID cross-reference inside an older changelog entry (`todo_node` handler), unrelated to this phase's own edits |

No blocker- or warning-level anti-patterns found in any of the 7 non-`.planning/` files this phase
touched after the D-20 merge (`CHANGELOG.md`, `README.md`, `docs/source/changelog.rst`,
`pyproject.toml`, `tests/test_changelog_page_gate.py`, `tests/test_toolchain_config_gate.py`,
`uv.lock`). The two test-file edits are exactly the two non-planning code edits the phase's own
evidence claims (D-22's Windows repair predates the `c72be91` anchor; the ruff `B904` `from e` fix
and the `RELEASE_VERSIONS` tuple append are the only diffs in this range) — both read and confirmed
directly, no scope creep found.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| No tag exists locally | `git tag -l v0.7.1` | empty, exit 0 | ✓ PASS |
| No tag exists on remote | `git ls-remote --tags origin v0.7.1` | empty, exit 0 | ✓ PASS |
| Version literal correct | `uv run python -c "import typsphinx; print(typsphinx.__version__)"` | `0.7.1` | ✓ PASS |
| Version-sync guards green | `uv run pytest tests/test_preview_version_sync.py tests/test_readme_version_sync.py -q` | 4 passed | ✓ PASS |
| Changelog page gate + toolchain gate green | `uv run pytest tests/test_changelog_page_gate.py tests/test_toolchain_config_gate.py -q` | 10 passed | ✓ PASS |
| Live CI authority run matches recorded evidence | `gh run view 31458368833 --json jobs,conclusion,status,headSha` | `conclusion: success`, `headSha` matches, 12/12 jobs `success` | ✓ PASS |
| Corrected fence anchor (Rule 3) is empty | `git diff c72be91..HEAD -- typsphinx/` | 0 lines | ✓ PASS |
| Original fence command is non-empty for the documented reason | `git diff origin/main..HEAD -- typsphinx/` | 1383 lines (matches merge-base predating Phases 43-45.2) | ✓ PASS (confirms Rule 3, not a gap) |

### Human Verification Required

None. This phase's deliverables (version literals, CHANGELOG content, CI evidence, git-tag fence,
handoff checklist) are all mechanically verifiable and were independently re-derived above rather
than trusted from SUMMARY/evidence-file prose.

### Gaps Summary

No gaps found. All five ROADMAP Success Criteria were independently re-verified against the live
repository state (not the evidence files' prose): version literals match across all three surfaces;
the CHANGELOG's curated `0.7.1` entry exists with both required breaking-change callouts; the CI
authority run was re-fetched live and matches the recorded evidence exactly (12/12 jobs `success`
against the correct `headSha`); the `release.yml` `create-release` job's `uv` setup steps were read
directly and confirmed ahead of the extractor call; `.planning/REQUIREMENTS.md`'s REL-04/REL-06 rows
remain unflipped; and the git-tag fence (local + remote) was independently probed and found empty.
The one documented plan-verification-command defect (Rule 3) was independently reproduced (both the
non-empty literal command and the empty corrected anchor) and is not scored as a gap, per the task's
explicit instruction. REL-04 is correctly left open — this is the criterion being satisfied exactly
as ROADMAP Phase 46 specifies, not a shortfall.

---

_Verified: 2026-08-11_
_Verifier: Claude (gsd-verifier)_
