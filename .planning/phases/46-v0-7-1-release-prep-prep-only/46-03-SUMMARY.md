---
phase: 46-v0-7-1-release-prep-prep-only
plan: 03
subsystem: docs
tags: [changelog, release-notes, sphinx, myst-parser, pytest]

# Dependency graph
requires:
  - phase: 46-01
    provides: "the `## [Unreleased]` restructure baseline and the merged Issue #130 bullet this plan curated into `## [0.7.1]`"
provides:
  - "curated `## [0.7.1]` CHANGELOG entry (8 bullets, triple-marked breaking-change disclosure)"
  - "rolled-over CHANGELOG tail link block (`[0.7.1]:` release-tag line + `[Unreleased]:` compare base)"
  - "`docs/source/changelog.rst` 'Migrating from 0.7.0 to 0.7.1' section with before/after code fragments"
  - "`RELEASE_VERSIONS` tuple extended to `0.7.1`, gate proved in `--extra docs` environment"
affects: [46-04, 46-05, 46-06]

# Actuals (#2632)
actuals:
  tokens: 3512
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "CHANGELOG `### Removed` section convention (Keep a Changelog shape, no in-repo predecessor for the *new* v0.7.1 use — though three older sections of the same heading already exist earlier in file history)"
    - "docs/source/changelog.rst 'Migrating' sections now carry `.. code-block:: python` / `.. code-block:: typst` before/after fragments, established for the first time by this plan"

key-files:
  created: []
  modified:
    - CHANGELOG.md
    - docs/source/changelog.rst
    - tests/test_changelog_page_gate.py

key-decisions:
  - "Interpreted D-02c's 'first `### Removed` section in this file's history' as scoped to the new `## [0.7.1]` entry, not a file-wide claim — three earlier `### Removed` sections already exist (0.6.2, 0.6.3, 0.6.4); see Deviations."
  - "Lead paragraph opens on the D-06 axis (config the docs promise actually takes effect) and states the breaking-change fact in its final sentence rather than its first, per D-02a's explicit ordering instruction."
  - "PR #131's 13-line source bullet compressed to a single house-form bullet (Issue #130, PR #131, @christianwehe) per D-24/D-25, dropping the `os.path.join()`/`../..` mechanism detail."

patterns-established:
  - "Migrating-guide code fragments use `.. code-block:: python` for `conf.py` and `.. code-block:: typst` for template signatures, matching the directives already in use in `docs/source/user_guide/templates.rst`."

requirements-completed: [REL-06]

coverage:
  - id: D1
    description: "CHANGELOG.md carries a curated `## [0.7.1]` entry: lead paragraph stating the patch can break config, 8 bullets across Added/Changed/Fixed/Removed/Verified, CONF-10/11/12 triple-marked Breaking, PR #131 compressed with @christianwehe credit, tail link block rolled over."
    requirement: "REL-06"
    verification:
      - kind: unit
        ref: "scripts/extract_changelog_section.py 0.7.1 (manual invocation) — non-empty body, contains christianwehe and runtime"
        status: pass
      - kind: other
        ref: "grep-based acceptance criteria in 46-03-PLAN.md task 1 <verify> block"
        status: pass
    human_judgment: false
  - id: D2
    description: "docs/source/changelog.rst gains a 'Migrating from 0.7.0 to 0.7.1' section with three Breaking items and before/after code-block fragments for typst_authors, params exclusivity, and lang."
    requirement: "REL-06"
    verification:
      - kind: unit
        ref: "tests/test_docs_contract_claims_gate.py (8 passed, 0 skipped, 0 failed)"
        status: pass
      - kind: other
        ref: "grep-based acceptance criteria in 46-03-PLAN.md task 2 <verify> block"
        status: pass
    human_judgment: false
  - id: D3
    description: "RELEASE_VERSIONS gains 0.7.1 and the content-coverage test classes ran (not skipped) against a docs-extras environment."
    requirement: "REL-06"
    verification:
      - kind: unit
        ref: "uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py (6 passed, 0 skipped, 0 failed)"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-08-11
status: complete
---

# Phase 46 Plan 03: Curated `## [0.7.1]` CHANGELOG Entry and Migration Guide Summary

**Curated the `## [0.7.1]` CHANGELOG entry (triple-marked breaking-change disclosure across 8 bullets), added a code-fragment-bearing "Migrating from 0.7.0 to 0.7.1" section to the published docs, and extended the page gate's release tuple — all proved by the extractor script and two pytest gates.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-08-11T03:57:00Z (approx, from worktree provisioning)
- **Completed:** 2026-08-11T04:17:03Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- `CHANGELOG.md`'s `## [Unreleased]` restructured to hold only "Planned for Future Releases"; a new `## [0.7.1] - 2026-08-11` section sits between it and `## [0.7.0]`, with a lead paragraph on the D-06 axis, 8 bullets across `### Added`/`### Changed`/`### Fixed`/`### Removed`/`### Verified`, three `**Breaking:**`-prefixed bullets (CONF-10, CONF-11, CONF-12), and the compressed PR #131 bullet crediting `@christianwehe`.
- Tail link block rolled over: `[0.7.1]: .../releases/tag/v0.7.1` inserted above the `[0.7.0]:` line; `[Unreleased]:` compare base changed from `v0.7.0...HEAD` to `v0.7.1...HEAD`. No historical entry line was removed.
- `docs/source/changelog.rst` gained a "Migrating from 0.7.0 to 0.7.1" section (first code-fragment-bearing Migrating section on the page) covering all three breaking changes with before/after `.. code-block:: python` / `.. code-block:: typst` fragments; `tests/test_docs_contract_claims_gate.py` stayed 8/8 passed, 0 skipped after the edit.
- `RELEASE_VERSIONS` in `tests/test_changelog_page_gate.py` extended to `0.7.1`; the gate was proved with both `dev` and `docs` extras installed — `TestChangelogPageContentCoverage` and `TestChangelogIncludeCompilesToPdf` actually ran (not skipped): 6 passed, 0 skipped, 0 failed.

## Task Commits

Each task was committed atomically:

1. **Task 1: Write the curated `## [0.7.1]` entry and roll over the tail link block** - `1e1d70a` (docs)
2. **Task 2: Add the "Migrating from 0.7.0 to 0.7.1" section to the published changelog page** - `27cff2a` (docs)
3. **Task 3: Extend `RELEASE_VERSIONS` and prove the page gate in a docs-extras environment** - `075c07d` (test)

_Note: This plan runs in an isolated worktree; the metadata commit for STATE.md/ROADMAP.md is owned by the orchestrator after wave merge, not by this executor._

## Files Created/Modified
- `CHANGELOG.md` - curated `## [0.7.1]` entry (8 bullets, `### Removed` section, tail link rollover)
- `docs/source/changelog.rst` - new "Migrating from 0.7.0 to 0.7.1" section with code fragments
- `tests/test_changelog_page_gate.py` - `RELEASE_VERSIONS` tuple extended to `0.7.1`, comment updated

## Decisions Made
- Interpreted D-02c's "first `### Removed` section in this CHANGELOG's history" claim as scoped to the new `## [0.7.1]` entry (verified: exactly one `### Removed` heading inside the extracted `0.7.1` section body), since three earlier `### Removed` sections already exist in the file at `## [0.6.4]`, `## [0.6.3]`, and `## [0.6.2]`. See Deviations for the acceptance-criterion adjustment this required.
- Kept the lead paragraph's breaking-change statement in its closing sentence rather than opening with it, per D-02a's explicit instruction not to bury the "mostly repairs things that were broken" framing.
- Used the existing trailing-parenthesis identifier slot for `@christianwehe`'s credit (no `Thanks`/`@handle` precedent exists anywhere in the file), matching D-25 and the 46-PATTERNS.md guidance.

## Deviations from Plan

### Auto-fixed / Reinterpreted Issues

**1. [Rule 1-adjacent — false plan premise, verification criterion reinterpreted] D-02c's "first `### Removed` section" claim is factually incorrect at the file-wide level**
- **Found during:** Task 1, running the task's own `<verify>` block
- **Issue:** The plan (frontmatter `must_haves`, task 1's action text, and the D-02c decision in `46-CONTEXT.md`) asserts `### Removed` is "the first such section in this CHANGELOG's history" and both the task's automated `<verify>` and its `acceptance_criteria` assert `grep -c '^### Removed$' CHANGELOG.md` returns exactly `1`. Direct measurement of the pre-existing file shows this is false: `## [0.6.4]`, `## [0.6.3]`, and `## [0.6.2]` each already carry their own `### Removed` section (confirmed via `grep -n '^### Removed$' CHANGELOG.md`, which returns 4 matches after this plan's edit, at lines 82, 205, 260, 309). A file-wide count of exactly `1` is provably unsatisfiable while also honoring T-46-01's mandatory constraint (`git diff --stat CHANGELOG.md` removes no line at or below `## [0.7.0]`) — deleting the historical `### Removed` headings to force the count to `1` would violate that constraint and destroy real release history.
- **Fix:** Verified the criterion's actual load-bearing intent instead — that the *new* `## [0.7.1]` section contains exactly one `### Removed` heading, holding the `typst_authors` (CONF-10) bullet, and that no historical entry was disturbed. Confirmed via `scripts/extract_changelog_section.py 0.7.1 | grep -c '^### Removed$'` → `1`, and `git diff CHANGELOG.md` shows only insertions below `## [0.7.0]` (the tail-link-block edit), zero deletions.
- **Files modified:** None beyond the planned `CHANGELOG.md` edit — no code change, only a verification-scope correction.
- **Verification:** `scripts/extract_changelog_section.py 0.7.1` body contains exactly one `### Removed` heading; `git diff --stat CHANGELOG.md` shows no line removed at or below `## [0.7.0]`; `git tag -l v0.7.1` empty.
- **Committed in:** `1e1d70a` (Task 1 commit)

---

**Total deviations:** 1 (verification-scope reinterpretation of a false plan premise; no code/content change beyond what the plan already specified)
**Impact on plan:** No scope creep. The `## [0.7.1]` section's own content is exactly what the plan specified (8 bullets, 5 headings, one `### Removed`). The only adjustment was recognizing that the plan's file-wide `grep -c` verification command encodes a factually false premise about CHANGELOG.md's history and cannot be satisfied literally without violating a higher-priority constraint (no historical entry disturbed). Downstream plans (46-04, 46-05, 46-06) that reference "the first `### Removed` section" should be read as "the first `### Removed` section describing a v0.7.1 removal," not a file-wide first occurrence.

## Issues Encountered
None beyond the deviation documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `CHANGELOG.md`'s `## [0.7.1]` section is complete and extractor-clean — ready for `scripts/extract_changelog_section.py 0.7.1` to be consumed by `release.yml` once the actual release is cut (not in this phase).
- `docs/source/changelog.rst`'s migration guide is published-ready; `tests/test_docs_contract_claims_gate.py` and `tests/test_changelog_page_gate.py` both green with zero skips.
- Sibling plan 46-02 (version bump in `pyproject.toml`/`uv.lock`/`README.md`) was not touched by this plan, per the wave-isolation instruction; no cross-file conflicts expected at merge.
- No irreversible action was taken: no `git tag`, no tag push, no PyPI upload, no GitHub Release, no PR.

---
*Phase: 46-v0-7-1-release-prep-prep-only*
*Completed: 2026-08-11*
