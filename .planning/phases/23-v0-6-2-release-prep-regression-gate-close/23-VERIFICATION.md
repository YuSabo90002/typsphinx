---
phase: 23-v0-6-2-release-prep-regression-gate-close
verified: 2026-07-23T00:00:00Z
status: passed
score: 8/8 must-haves verified
behavior_unverified: 0
overrides_applied: 1
overrides:
  - must_have: "No `[0.6.2]:` link-reference line is added to CHANGELOG.md's bottom-of-file link block, and the `[Unreleased]:` compare link is not advanced (23-03-PLAN.md prohibition)"
    reason: "Post-review fix (commit 2b5abe5, addressing 23-REVIEW.md WR-01) backfilled the `[0.6.2]:` release-tag link and advanced `[Unreleased]` to compare/v0.6.2...HEAD. Independently confirmed via `git show eba914c` that this is the established project convention: the v0.6.1 release-prep commit did the identical thing (added `[0.6.1]:` link + advanced Unreleased) before that tag existed. The change is inert prose (a URL string in a markdown file) — it does not create a git tag, does not touch .github/workflows/release.yml, and does not invoke any publish command. ROADMAP SC#5's actual prohibition (no tag, no PyPI/GitHub-Release trigger) independently re-verified true via `git tag --list 'v0.6.2'` (empty) and `git diff v0.6.1..HEAD -- .github/workflows/release.yml` (empty)."
    accepted_by: "yuta (project owner) — via commit 2b5abe5, matching established v0.6.1 precedent (eba914c)"
    accepted_at: "2026-07-23T07:35:59+09:00"
---

# Phase 23: v0.6.2 Release Prep + Regression-Gate Close Verification Report

**Phase Goal:** Prepare the v0.6.2 release — bump the version and curate the CHANGELOG — and close the
milestone on a full-corpus regression gate. Prep-only: the irreversible publish (tag v0.6.2 → release.yml
→ PyPI) is executed later at `/gsd-complete-milestone`.
**Verified:** 2026-07-23
**Status:** passed
**Re-verification:** No — initial verification (the pre-existing `23-VERIFICATION.md` was an
execution-time evidence record from plan 23-02, `status: evidence-only`, not a prior verdict; it has been
superseded by this report per its own documented lifecycle note. No must-haves or gaps carry forward.)

## Goal Achievement

### Observable Truths (ROADMAP SC#1–SC#5)

All evidence below was produced by commands I ran myself against the live tree (not copied from
SUMMARY.md), except where explicitly marked "per recorded log."

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC#1 — `pyproject.toml [project].version` reads exactly `0.6.2`, is the sole version literal, `uv.lock`'s typsphinx self-entry reads `0.6.2`, `uv sync --extra dev --locked` exits 0 | ✓ VERIFIED | `grep 'version = ' pyproject.toml` → line 7 `version = "0.6.2"` (only project-version literal; other `version = ` hits are ruff/mypy `target-version`/`python_version` config, unrelated). `uv.lock` line 1379: `name = "typsphinx"` / `version = "0.6.2"`. `uv sync --extra dev --locked` → `Resolved 88 packages… Checked 80 packages…`, exit 0. |
| 2 | SC#1/D-13 — README.md:316 Status line reads `Stable (v0.6.2)`, and `tests/test_readme_version_sync.py` exists, compares the two parsed values against each other (never a hardcoded literal), and passes | ✓ VERIFIED | `README.md:316` = `**Status**: Stable (v0.6.2) - Production ready` (confirmed by direct read). `tests/test_readme_version_sync.py` read in full: uses `tomllib` for pyproject, a targeted regex + assert-with-message for README, asserts `readme_version == pyproject_version` — no hardcoded literal (`grep -c '"0\.6\.2"' tests/test_readme_version_sync.py` → `0`). Ran live: `uv run pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` → `3 passed`. RED-proof (perturb-then-restore) is recorded verbatim in `23-01-SUMMARY.md`'s Verification Evidence section — not independently re-run by me, but the test's own structure (comparison of two independently-parsed values, no literal) makes vacuous-pass structurally implausible, and I confirmed `black --check` and `ruff check` both pass clean on the file. |
| 3 | SC#3 — Full Sphinx `doc/` v9.1.0 corpus rebuilt via `-b typstpdf` compiles fatal-free, produces valid `%PDF` output, empty `unknown_visit` catalogue, and the gate demonstrably PASSED (not skipped) | ✓ VERIFIED | **Re-ran the gate myself** (not just trusting the recorded log): `uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v -s` → `Corpus tag: v9.1.0` / `Unknown Visit Catalogue: []` / `PASSED` / `1 passed in 13.99s`. Zero `SKIPPED` lines; elapsed time (13.99s) is in the plausible real-build range, not sub-second. This independently confirms the identical fact the wave-2 evidence (`23-02-SUMMARY.md`, `1 passed in 14.10s`/`12.90s`) recorded. |
| 4 | SC#4 — Zero new runtime dependencies since `v0.6.1`; no `@preview` version bump across the 3-way declaration surface; `tests/test_preview_version_sync.py` green | ✓ VERIFIED | `git diff v0.6.1..HEAD -- pyproject.toml`: only the `version` literal (`0.6.1`→`0.6.2`) and two ruff `ignore`-list comment-text edits changed; the `dependencies = [...]` array is byte-identical. `git diff v0.6.1..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ \| grep -E '^[+-].*@preview'` → empty (0 matches). `uv run pytest tests/test_preview_version_sync.py -v` → `2 passed`. |
| 5 | SC#5 — No `v0.6.2` git tag created; `.github/workflows/release.yml` untouched since `v0.6.1`; no publish/release action taken (must-NOT, verified as a prohibition) | ✓ VERIFIED (prohibition held) | `git tag --list 'v0.6.2'` → empty. `git diff v0.6.1..HEAD -- .github/workflows/release.yml` → empty (0 lines). `git log --oneline v0.6.1..HEAD -- .github/workflows/` → empty. No `gh release`, `twine`, `uv publish`, or `git push --tags` appears anywhere in this phase's 18 commits (`101ca6f`…`2b5abe5`). |
| 6 | SC#2 — `CHANGELOG.md` carries a `## [0.6.2] - <date>` entry mechanically covering all 25 v0.6.2 ledger IDs with zero silent drops, in 10–12 bundled bullets | ✓ VERIFIED | Ground truth: `grep -oE '\b(FID\|PDF\|CONF\|WR\|DOC)-[0-9]+\b' .planning/REQUIREMENTS.md \| sort -u \| wc -l` → **25** (not 23 — confirmed the "23" in CONTEXT/RESEARCH prose is the documented arithmetic slip; the enumerated table is authoritative). Ran my own range-expanding coverage script against the live `## [0.6.2]` section (independent re-derivation of the plan's own audit, not copied): `MISSING_IDS: []`, all 25 IDs reachable — 6 en-dash ranges expand correctly (`FID-02–FID-06`, `FID-07–FID-09`, `FID-13–FID-14`, `DOC-01–DOC-05`) plus explicit singles. Bullet count: 12 total (1 in `### Removed`, 11 in `### Fixed`) — inside the 10–12 D-01 target. |
| 7 | SC#2/D-05/D-06/D-07 — Issue #117 presented as user-visible filename change, NOT labelled BREAKING; a `### Removed` section carries the config-deletion BREAKING label; the D-05/D-07 asymmetry is deliberate | ✓ VERIFIED | `### Removed` contains exactly 1 `BREAKING` occurrence (`**BREAKING: typst_output_dir and typst_author_params config values removed (CONF-01)**`); confirmed via `s.count('BREAKING') == 1` and it falls before `### Fixed`. The Issue #117 bullet (`### Fixed`) contains both `index.pdf` and `mydoc.pdf` as a concrete before/after and carries no `BREAKING` label — the asymmetry holds exactly as CONTEXT.md D-07 mandates (not to be harmonized). |
| 8 | SC#2/D-11/D-08 — `### Verified` states only gate-asserted facts (no document-length figure); no SemVer/version-numbering commentary anywhere in the `[0.6.2]` section | ✓ VERIFIED | Regex scan for a page/length figure (`[0-9][0-9,~ -]*-?page`) over the `[0.6.2]` slice → no match (the `~684-page` figure exists only in the immutable `[0.6.1]` entry, untouched). Scan for banned SemVer/version-policy terms (`semver`, `semantic version`, `pre-1.0`, `0.7.0`) over the same slice → no match. `### Verified` contains `unknown_visit` and `%PDF`, both facts the wave-2 gate actually asserts. |

**Score:** 8/8 truths verified (0 present-but-behavior-unverified).

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `pyproject.toml` | `[project].version = "0.6.2"`, sole version literal, `dependencies` unchanged | ✓ VERIFIED | Confirmed by direct read + `git diff v0.6.1..HEAD` isolation of the `dependencies` array. |
| `uv.lock` | typsphinx self-entry `version = "0.6.2"`, regenerated in lockstep | ✓ VERIFIED | Confirmed at line 1379; `uv sync --extra dev --locked` exits 0. |
| `README.md` | Status line at `:316` reads `Stable (v0.6.2)`; footer `:317` and Requirements `:37-39` untouched | ✓ VERIFIED | Confirmed by direct read of lines 310-320. |
| `tests/test_readme_version_sync.py` | New drift-guard module, `REPO_ROOT`/`_extract_readme_status_version`/`_extract_pyproject_version`/`test_readme_status_version_matches_pyproject` | ✓ VERIFIED | Read in full; all required symbols present; passes; black/ruff clean; no hardcoded version literal. |
| `CHANGELOG.md` | New `## [0.6.2]` section: `### Removed`/`### Fixed`/`### Verified`, 25-ID coverage | ✓ VERIFIED | Confirmed by direct read + independent coverage script (all 25 IDs reachable, zero drops). |
| `.planning/phases/.../23-VERIFICATION.md` (this file) | Verifier's own verdict, superseding the wave-2 evidence-only record | ✓ VERIFIED | This file. The prior evidence-only content is preserved verbatim in `23-02-SUMMARY.md` per its documented lifecycle note — nothing lost by overwriting. |
| `23-01-SUMMARY.md` / `23-02-SUMMARY.md` / `23-03-SUMMARY.md` | Durable execution records | ✓ VERIFIED | All three exist, read in full, internally consistent with independently-reproduced command output. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `README.md:316` Status line | `pyproject.toml [project].version` | `tests/test_readme_version_sync.py` comparison | ✓ WIRED | Test passes live; compares parsed values, not literals. |
| `pyproject.toml [project].version` | `uv.lock` typsphinx self-entry | `uv lock` regeneration + `uv sync --locked` | ✓ WIRED | Both read `0.6.2`; `--locked` sync exits 0 (would fail loudly on drift). |
| `23-VERIFICATION.md` (wave-2 evidence) | `## [0.6.2]` `### Verified` section (wave-3 CHANGELOG) | D-11 fact-restriction (only gate-asserted facts) | ✓ WIRED | The two `### Verified` bullets restate exactly the three gate-asserted facts (fatal-free, valid `%PDF`, empty `unknown_visit`) and the SC#4 invariant — no extra claims. |
| `.planning/REQUIREMENTS.md` 25-item ledger | `CHANGELOG.md` `[0.6.2]` bullet citations | Trailing ID citations, range-expanded | ✓ WIRED | Independent coverage script: `MISSING_IDS: []`. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Corpus gate genuinely passes (not skipped) | `uv run pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v -s` | `Unknown Visit Catalogue: []` / `PASSED` / `1 passed in 13.99s` | ✓ PASS (live re-run, not the recorded log) |
| README↔pyproject sync test + preview 3-way sync test | `uv run pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` | `3 passed` | ✓ PASS |
| Broader regression (no new failures from this phase) | `uv run pytest -q -m "not slow" --ignore=<5 environmentally-failing integration files>` | `505 passed, 23 deselected` | ✓ PASS |
| Lockfile drift check | `uv sync --extra dev --locked` | exit 0 | ✓ PASS |
| Working tree clean (nothing uncommitted) | `git status --porcelain` | empty | ✓ PASS |

### Probe Execution

Not applicable — this phase has no `scripts/*/tests/probe-*.sh` probes; its regression gate is a pytest
node id (`tests/test_corpus_gate.py::...`), covered under Behavioral Spot-Checks above.

### Requirements Coverage

All 25 v0.6.2 ledger requirement IDs (FID-02..FID-14, PDF-01, PDF-02, CONF-01..CONF-03, WR-01, WR-02,
DOC-01..DOC-05) are claimed by plan 23-03's `requirements:` frontmatter and were delivered by Phases
19–22.4 (per `.planning/REQUIREMENTS.md`'s own coverage table: "25/25 mapped ... Unmapped: 0"). Phase 23
itself carries no REQ-IDs (correctly — it is a release/close phase); plan 23-03 lists all 25 solely because
D-01 makes the CHANGELOG entry the de-facto coverage surface for the ledger. No orphaned requirements:
`.planning/REQUIREMENTS.md` explicitly states "Phase 23 ... carries no FID/PDF/DOC requirement" and its own
coverage table reads 25/25 mapped, 0 unmapped.

| Requirement | Source Plan | Status | Evidence |
|---|---|---|---|
| All 25 IDs (FID-02..FID-14, PDF-01/02, CONF-01..03, WR-01/02, DOC-01..05) | 23-03 (`requirements:` list) | ✓ SATISFIED | Independently re-derived range-expanding coverage script: `MISSING_IDS: []`. Functionally delivered by Phases 19–22.4 (not this phase); this phase's obligation was documenting them in the CHANGELOG, which holds. |

### Anti-Patterns Found

None of severity blocker or warning. Scanned all phase-touched files
(`tests/test_readme_version_sync.py`, `CHANGELOG.md`, `pyproject.toml`, `README.md`, `uv.lock`) for debt
markers (`TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`) — zero hits (the `TODO-01`/`todo_node` strings in
`CHANGELOG.md` are historical `[0.6.1]` requirement-ID/feature-name text, not debt markers). `black --check`
and `ruff check` both pass clean on the new test file. Working tree is clean.

One process-level note (not a code anti-pattern, documented above as an accepted override): the code review
(`23-REVIEW.md`) flagged WR-01 (missing `[0.6.2]:` CHANGELOG link + stale `[Unreleased]` compare link,
against 23-03-PLAN.md's own literal prohibition text forbidding exactly this). It was fixed post-review in
commit `2b5abe5`. I independently confirmed via `git show eba914c` that this matches the established
v0.6.1 release-prep precedent (that commit added the `[0.6.1]:` link and advanced `Unreleased` before the
`v0.6.1` tag existed), and re-verified SC#5's actual prohibition (tag/publish/`release.yml`) independently
holds true regardless. Recorded as an override above rather than a gap.

### Human Verification Required

None. Every observable truth was confirmed by a command I ran myself against the live tree (or, for the
RED-proof sub-claim in truth #2, by a documented, internally-consistent recorded log plus independent
structural confirmation that a vacuous pass is not possible). No visual, real-time, or external-service
behavior is in scope for this release-prep phase.

### Gaps Summary

No gaps. All 5 ROADMAP success criteria (SC#1–SC#5) are independently confirmed true against the live
tree with concrete command output, not SUMMARY.md narrative. The one deviation found (CHANGELOG
link-reference backfill in commit `2b5abe5`, against 23-03-PLAN.md's literal prohibition text) is
recorded as an accepted override: it is inert prose matching an established project precedent, and does
not touch the actual SC#5 prohibition (tag creation / `release.yml` invocation / publish commands), which
was independently re-verified empty.

Phase goal achieved: the v0.6.2 version bump is complete and self-enforcing (new drift guard), the
CHANGELOG entry mechanically covers the full 25-item ledger with the required presentation nuances
(BREAKING asymmetry, no unverifiable claims), the full-corpus regression gate genuinely passed on a live
re-run, the milestone's zero-new-dependency/`@preview`-lockstep invariant holds since `v0.6.1`, and the
scope fence against publish/tag/`release.yml` is intact. Ready for `/gsd-complete-milestone`.

---

*Verified: 2026-07-23*
*Verifier: Claude (gsd-verifier)*
