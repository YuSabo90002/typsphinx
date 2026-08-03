---
phase: 41-v0-7-0-release-automation-release-prep
verified: 2026-08-03T12:36:46Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 41: v0.7.0 Release Automation + Release Prep Verification Report

**Phase Goal:** The release surface matches the work — a reader of the GitHub Release sees the
curated CHANGELOG section rather than a ~296-line commit dump — and the v0.7.0 tree is bumped,
documented, and proven green, with every irreversible action still fenced off behind
`/gsd-complete-milestone`.

**Verified:** 2026-08-03T12:36:46Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `release.yml` builds the release body from CHANGELOG's `## [X.Y.Z]` section, dump removed rather than fenced | ✓ VERIFIED | Re-read `.github/workflows/release.yml` directly: `create-release`'s "Generate release notes" step calls `scripts/extract_changelog_section.py`, no `git log --pretty`/`PREV_TAG` anywhere in the file (`grep` empty). Re-ran the extractor myself: `0.6.5` → exit 0, curated section on stdout; `9.9.9` → exit 1, stderr names the version. `validate` job's new "Verify CHANGELOG has a section for this version" step sits before `Run tests`, and job graph is `validate → build → publish-pypi → create-release` (re-confirmed by reading the file). |
| 2 | Version reads 0.7.0 as sole literal in `pyproject.toml`, `uv.lock`/`README.md` in lockstep, `__version__` reports it, curated `## [0.7.0]` CHANGELOG entry with tail link block rolled over | ✓ VERIFIED | `grep -n "^version" pyproject.toml` → `version = "0.7.0"` (only site). `uv run python -c "import typsphinx; print(typsphinx.__version__)"` → `0.7.0`. `README.md:317` → `Stable (v0.7.0)`. `uv.lock`'s `typsphinx` package block → `version = "0.7.0"`. `CHANGELOG.md` has `## [0.7.0] - 2026-08-03` with Added/Changed/Fixed/Verified sections and requirement IDs; tail block has `[0.7.0]: .../releases/tag/v0.7.0` and `[Unreleased]: .../compare/v0.7.0...HEAD` — both re-read directly. |
| 3 | Post-bump tree green: full suite, lint/type trio, full-corpus `-b typstpdf` gate, both docs dogfooding builds, `ja` four-check glyph bar | ✓ VERIFIED | Re-ran myself: `pytest tests/` → 805 passed, 1 skipped (matches evidence file). `black --check .` / `ruff check .` / `mypy typsphinx/` all clean. `tox -e docs-pdf` re-run independently → build succeeded, 2 pre-existing warnings, 93-page PDF (byte-identical page count to evidence file). `ja` glyph bar: `41-JA-GLYPH-BAR.md` + `41-JA-GLYPHBAR-SIGNOFF.md` show mechanical checks 1-3 (94/94 pages, CJK count delta +34 no drop, `/BaseFont` CJK-coverage font `NotoSerifCJKjp-ExtraLight` identical both sides) and the owner's verbatim one-word "approved" for check 4, per D-16's rule that no automated stand-in is accepted for the visual look. |
| 4 | Milestone invariants proven mechanically over SHA-anchored full diff: zero new runtime deps, `@preview` count still 4 with no new lockstep site, every node-handler change carries recorded-RED GATE-01 fixture | ✓ VERIFIED | Re-ran `git diff` over `merge-base main HEAD` (`51e02b6`) myself: only the version-bump hunk plus one dev-only `pillow` line in the `dev` extra (Phase 39, pre-dates this phase, explicitly and correctly disclosed as non-breaching in `41-SC4-INVARIANTS.md` rather than smoothed over); runtime `dependencies` array byte-identical. `@preview` count re-measured at 4 names/versions, line-for-line identical across `writer.py`/`template_engine.py`/`templates/base.typ` between BASE and HEAD. `41-SC4-INVARIANTS.md`'s 51-handler census and node-name coverage map spot-checked against the real `test_desc_sig_space_render_gate.py` assertions (`raw("class")\nraw(" ")\nraw("sphinx` line independently found at the file) — matches. Phase 40.1's 3 evidence files and 3 RED-commit SHAs independently confirmed to exist/resolve. |
| 5 | No irreversible action taken at phase close; local+remote `v0.7.0` tags both empty; standalone handoff checklist records exactly what `/gsd-complete-milestone` executes | ✓ VERIFIED | Re-ran myself: `git tag -l v0.7.0` and `git ls-remote --tags origin v0.7.0` both empty, exit 0. `41-HANDOFF.md` exists with an ordered 7-item checklist (merge → tag → release.yml run → translations-repo second tag → RTD confirm → REQUIREMENTS.md flip → todo filing), explicitly naming the `phase.complete` auto-flip hazard from prior project memory. |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `scripts/extract_changelog_section.py` | Stdlib-only positional CHANGELOG extractor | ✓ VERIFIED | Read in full; genuine positional algorithm (first-match, terminate at next `## [` or EOF), no name-based special-casing of "Unreleased", raises `RuntimeError` with version-naming messages on both failure modes. Not a stub. |
| `tests/test_changelog_extraction.py` | 6-case subprocess-invoked contract | ✓ VERIFIED | Re-ran: 6 passed, 0 failed. Covers both D-10 directions plus adjacency/empty/ordering. |
| `.github/workflows/release.yml` | Dump removed, CHANGELOG check in `validate` | ✓ VERIFIED | Re-read in full. `git log --pretty`/`PREV_TAG` fully absent. Existence check present in `validate`, upstream of `build`/`publish-pypi`/`create-release`. All `${{ }}` values are passed via `env:`/`with:`, never interpolated directly into `run:` script bodies (CR-01 fix confirmed applied). |
| `CHANGELOG.md` `## [0.7.0]` entry | Curated 5-6 bullet entry per D-01..D-05 | ✓ VERIFIED | Present with Added/Changed/Fixed/Verified sections, requirement IDs in trailing parens, no BREAKING label, lead paragraph on "API reference pages became readable." |
| `41-HANDOFF.md` | SC#5 checklist | ✓ VERIFIED | Present, ordered, names owners, cites the `phase.complete` auto-flip hazard explicitly. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `release.yml` (`validate`, `create-release`) | `scripts/extract_changelog_section.py` | `uv run python scripts/extract_changelog_section.py "$VERSION"` | WIRED | Confirmed by direct file read; both jobs call the same script, no duplicated inline logic. |
| `tests/test_changelog_extraction.py` | `scripts/extract_changelog_section.py` | `subprocess.run([sys.executable, ...])` | WIRED | Confirmed via passing test run — exercises the real script, not an import shortcut. |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|--------------|-------------|--------------|--------|----------|
| REL-04 | 41-01, 41-07 | GitHub Release body is curated CHANGELOG section | ✓ SATISFIED (implementation complete; checkbox correctly left unflipped — publish half is `/gsd-complete-milestone`'s job per this phase's own explicit scope decision) | `release.yml` re-read; extractor re-run |
| REL-05 | 41-02..41-07 | v0.7.0 released — prep half only in this phase | ✓ SATISFIED for the prep half (version bump, CHANGELOG, green tree, invariants, handoff); publish half correctly deferred and documented in `41-HANDOFF.md` | Version/CHANGELOG/tag-emptiness re-measured directly |

No orphaned requirements found — `.planning/REQUIREMENTS.md` maps only REL-04/REL-05 to Phase 41, and both appear in plan frontmatter across the 7 plans. Both remain `[ ]`/"Pending" in REQUIREMENTS.md, which is correct per this phase's own CONTEXT decision (flip belongs to `/gsd-complete-milestone`), not a gap — the orchestrator's brief and `41-HANDOFF.md` both flag the known `phase.complete` auto-flip hazard to watch for at that time.

### Anti-Patterns Found

None. `grep -n -E "TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER"` across all phase-touched files (`scripts/extract_changelog_section.py`, `tests/test_changelog_extraction.py`, `.github/workflows/release.yml`, `pyproject.toml`, `README.md`, `CHANGELOG.md`) returned nothing.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Extractor on real, present version | `python3 scripts/extract_changelog_section.py 0.6.5` | Curated section printed, exit 0 | ✓ PASS |
| Extractor on absent version | `python3 scripts/extract_changelog_section.py 9.9.9` | stderr names version, exit 1 | ✓ PASS |
| Extractor on the release-under-test's own version | `python3 scripts/extract_changelog_section.py 0.7.0` | Curated lead paragraph printed, exit 0 | ✓ PASS |
| CHANGELOG-extraction test module | `pytest tests/test_changelog_extraction.py -v` | 6 passed | ✓ PASS |
| Full regression suite | `pytest tests/` | 805 passed, 1 skipped | ✓ PASS |
| Lint/type trio | `black --check .` / `ruff check .` / `mypy typsphinx/` | All clean | ✓ PASS |
| Docs PDF dogfooding | `tox -e docs-pdf` | build succeeded, 2 pre-existing unrelated warnings, 93-page PDF | ✓ PASS |
| Tag emptiness | `git tag -l v0.7.0`, `git ls-remote --tags origin v0.7.0` | Both empty | ✓ PASS |
| `@preview` sync tests | `pytest tests/test_preview_version_sync.py tests/test_readme_version_sync.py -v` | 4 passed | ✓ PASS |
| PROJECT.md comment balance (D-13) | Node script counting `<!--`/`-->` | depth 0 (balanced) | ✓ PASS |

### Human Verification Required

None. SC#3's `ja` glyph bar check 4 (owner visual confirmation) was already collected as a phase close condition per D-16 — `41-JA-GLYPHBAR-SIGNOFF.md` records the owner's verbatim "approved" — so no outstanding human item remains for this verifier to route.

### Gaps Summary

No gaps found. All five ROADMAP success criteria hold under independent re-measurement, not merely under the phase's own evidence-file claims. One pre-existing, transparently-disclosed administrative loose end is worth carrying forward but does not block the phase goal: the todo `.planning/todos/pending/2026-07-29-project-md-unterminated-html-comments.md` describes a fix (`PROJECT.md`'s two unterminated HTML comments) that plan 41-03 already applied — re-confirmed directly (`<!--`/`-->` depth is 0) — but the todo file itself was not moved to `todos/completed/`. Plan 41-07's own SUMMARY already flags this explicitly as an intentional scope-boundary decision (the todo's filing was never promoted into v0.7.0 scope), so it is recorded here as an informational note, not a gap.

A second post-plan addition — the CR-01 shell-injection fix in `release.yml` (commits `e9044ec`/`0261085`) — was not covered by any plan's own SUMMARY (it happened in `execute:post` code review, after all 7 plans closed) but is fully evidenced in `41-REL04-EVIDENCE.md`'s addendum and `41-REVIEW.md`'s resolution note, and was independently re-verified against the live file during this pass: every `${{ }}` inside a `run:` block was converted to `env:`, the CHANGELOG-existence check's position in the job graph is unchanged, and the full regression suite plus lint/type trio remain green post-fix.

---

_Verified: 2026-08-03T12:36:46Z_
_Verifier: Claude (gsd-verifier)_
