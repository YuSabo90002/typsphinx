---
phase: 45-documentation-currency-carried-hygiene
plan: 02
subsystem: docs
tags: [changelog, myst-parser, sphinx, docutils, typstpdf, pytest]

# Dependency graph
requires:
  - phase: 45-01
    provides: "docs/source/changelog.rst delegates to repo-root CHANGELOG.md via a myst-parser include; a pre-phase docs-build warning baseline"
provides:
  - "CHANGELOG.md carries a reconstructed ## [0.4.4] section (2026-07-05) with its matching link-reference line, closing the hole that made the published page miss 12 releases instead of 11"
  - "CHANGELOG.md has exactly one ## [Unreleased] heading -- the stray second one's body merged in, the heading and its now-doubled --- transition removed"
  - "CHANGELOG.md carries zero U+2705 check-mark characters (25 removed)"
  - "docs/source/changelog.rst's Migration Guides section covers 0.5.x-to-0.6.x and 0.6.x-to-0.7.0, and Release Process describes what .github/workflows/release.yml actually does today"
  - "tests/test_changelog_page_gate.py -- a real-build regression gate proving the published page delegates, carries every release, and both builders stay clean of changelog-attributable warnings"
  - "tests/fixtures/changelog_include_gate/ -- a minimal Sphinx project reading the REAL repo-root CHANGELOG.md, used by the PDF-compile assertion"
  - "45-GATE-EVIDENCE-02-docs-build-clean.md -- post-change warning counts measured at zero delta against plan 45-01's baseline"
affects: [45-04-plan, 46-plan]

# Actuals (#2632)
actuals:
  tokens: 7336
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Regression-gate test module proving already-correct behavior (Task 3's tests passed on first run, since Tasks 1-2 of this same plan had already landed the content/framing fixes) -- committed as a single commit rather than split RED/GREEN, matching this repo's standing GATE-01-style convention of proving a fix via a real build rather than literal test-first authorship when the fix and its proof are sequenced across tasks in one plan"

key-files:
  created:
    - tests/test_changelog_page_gate.py
    - tests/fixtures/changelog_include_gate/conf.py
    - tests/fixtures/changelog_include_gate/index.rst
    - tests/fixtures/changelog_include_gate/changelog.rst
    - .planning/phases/45-documentation-currency-carried-hygiene/45-GATE-EVIDENCE-02-docs-build-clean.md
  modified:
    - CHANGELOG.md
    - docs/source/changelog.rst

key-decisions:
  - "The ## [0.4.4] section body was reconstructed live from `git log v0.4.3..v0.4.4` (148 commits) and `gh release view v0.4.4 --json body`, curated to user-facing prose matching the surrounding entries' tone, not a commit dump"
  - "D-05's checkmark removal: deleted the '- ✅ ' prefix and left the line's existing '(100%)' / 'fully implemented' surrounding prose to carry the completion statement, rather than adding new wording -- the surrounding context already reads as complete. The single ⏳ line (Requirement 11, first block) was left untouched, out of D-05's scope"
  - "tests/fixtures/changelog_include_gate/changelog.rst omits :start-line: entirely, matching the REAL docs/source/changelog.rst shape shipped by plan 45-01's deviation (which dropped :start-line: to satisfy its own zero-warning bar) -- not the plan's literal action text, which predated that deviation and still described a :start-line: option that no longer exists on the real page"

patterns-established:
  - "Split-literal self-reference guard (tests/test_no_stale_github_io_links.py's precedent) applied to a new module: the per-release-heading regex and the '(Current)' marker in test_changelog_page_gate.py are built so the module cannot match itself if ever repo-wide-scanned"

requirements-completed: [DOC-12]

coverage:
  - id: D1
    description: "CHANGELOG.md backfilled with the missing 0.4.4 release section, merged to a single Unreleased heading, and stripped of all 25 U+2705 emoji that would render as tofu in the PDF"
    requirement: DOC-12
    verification:
      - kind: unit
        ref: "tests/test_changelog_extraction.py -v (6/6 passed, unaffected by the content edits)"
        status: pass
      - kind: other
        ref: "Task 1's own <verify> script (structural regex assertions over CHANGELOG.md, byte-identical extract_changelog_section.py 0.7.0 output before/after) -- printed 'OK changelog structure'"
        status: pass
    human_judgment: false
  - id: D2
    description: "docs/source/changelog.rst's Migration Guides extended to cover 0.5.x-to-0.6.x and 0.6.x-to-0.7.0, and Release Process restated to match .github/workflows/release.yml's real validate/build/publish-pypi/create-release job graph"
    requirement: DOC-12
    verification:
      - kind: other
        ref: "Task 2's own <verify> script (real -b html subprocess build, zero changelog-attributable WARNING lines) -- printed 'OK framing'"
        status: pass
    human_judgment: false
  - id: D3
    description: "tests/test_changelog_page_gate.py proves the published page delegates, carries all 12 previously-missing releases in both a real HTML build and a real compiled PDF, has exactly one Changelog heading, and both builders stay warning-clean"
    requirement: DOC-12
    verification:
      - kind: unit
        ref: "tests/test_changelog_page_gate.py -v (6/6 passed)"
        status: pass
      - kind: integration
        ref: "tests/test_changelog_page_gate.py -m 'not slow' -v (2 selected, 4 deselected -- confirms the slow/skipif gating works as specified)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Post-change docs-build warning delta measured against plan 45-01's baseline: zero new warnings on either builder, changelog_attributable_warning_count stays at 0"
    requirement: DOC-12
    verification:
      - kind: other
        ref: "45-GATE-EVIDENCE-02-docs-build-clean.md (real sphinx-build -b html / -b typstpdf subprocess runs against fresh output directories at HEAD 66304e2, both exit 0, html_warning_count=1/pdf_warning_count=1/changelog_attributable_warning_count=0, delta 0/0/0 against baseline)"
        status: pass
    human_judgment: false

duration: 41min
completed: 2026-08-10
status: complete
---

# Phase 45 Plan 02: Documentation Currency + Carried Hygiene (Changelog Content Completion) Summary

**`CHANGELOG.md` backfilled with the missing v0.4.4 release, deduplicated to one `[Unreleased]` heading, and emoji-free; the published changelog page's Migration Guides and Release Process sections corrected to match reality; a real-build regression gate proves all 12 previously-missing releases render clean on both `-b html` and `-b typstpdf` at zero warning delta against the pre-phase baseline.**

## Performance

- **Duration:** 41 min (Task 1 commit `07:33:40+09:00` → Task 3 commit `07:54:25+09:00`, plus upstream-context reading and worktree provisioning before Task 1)
- **Started:** 2026-08-10T07:15:00+09:00 (approx., first Read call)
- **Completed:** 2026-08-10T07:54:25+09:00
- **Tasks:** 3 (all `type="auto"`; Task 3 also `tdd="true"`)
- **Files modified:** 2 content files + 4 test-suite files + 1 evidence file created

## Accomplishments

- `CHANGELOG.md` gained a reconstructed `## [0.4.4] - 2026-07-05` section (Python floor raise to
  3.10-3.13, `softprops/action-gh-release` v2→v3, `--locked` on every `uv sync` site, weekly
  drift-detection workflow, `sphinx-typst-stack` Dependabot group + CI badge, i18n infrastructure,
  and a `tomllib`/`tomli` release-workflow fix), sourced live from `git log v0.4.3..v0.4.4` and the
  existing GitHub Release, with its `[0.4.4]:` link-reference line positioned between `[0.5.0]:`
  and `[0.4.3]:`
- The stray second `## [Unreleased]` heading (line 911, inside the `## [0.2.0]` section's body
  span) was merged into the top-of-file `[Unreleased]` and its now-doubled `---` transition
  removed, leaving exactly one `[Unreleased]` heading in the file
- All 25 U+2705 check-mark characters removed from the two Requirements-Status blocks (lines
  ~801-813, ~889-901); the single `⏳` line (Requirement 11, first block) was left untouched, out
  of D-05's scope
- `CHANGELOG.md` lines 1-7 verified byte-identical to `HEAD:CHANGELOG.md` throughout, and
  `extract_changelog_section.py`'s `0.7.0` extraction verified byte-identical before/after --
  REL-04's release-body pipeline is provably undisturbed
- `docs/source/changelog.rst`'s `Migration Guides` gained two newest-first subsections (0.6.x to
  0.7.0, 0.5.x to 0.6.x), sourced from the corresponding `CHANGELOG.md` sections; `Release Process`
  rewritten to name `validate`/`build`/`publish-pypi`/`create-release` -- the real job graph in
  `.github/workflows/release.yml` -- with no invented step
- `tests/test_changelog_page_gate.py` added: a text-only always-runs class pinning the delegation
  shape and the absence of any hand-maintained release history or current-release marker, plus two
  `slow`+`skipif`-gated classes driving real `-b html` and `-b typstpdf` builds that assert all 12
  previously-missing version strings render, exactly one `Changelog` heading exists, and both
  builders stay clean of changelog-attributable warnings
- `tests/fixtures/changelog_include_gate/` added -- a 3-file Sphinx project whose `changelog.rst`
  reads the REAL repo-root `CHANGELOG.md` at `../../../CHANGELOG.md`, so the PDF-compile assertion
  is genuine rather than synthetic
- `45-GATE-EVIDENCE-02-docs-build-clean.md` records the post-change warning counts
  (`html_warning_count=1`, `pdf_warning_count=1`, `changelog_attributable_warning_count=0`) at zero
  delta against plan 45-01's baseline, plus the two carried consequences (ja translation lag, and
  the Phase 46 one-line-addition property confirmed by diff inspection)
- Full suite re-verified green after all three tasks: **952 passed, 1 pre-existing env-gated skip**
  (`TYPSPHINX_CORPUS_REPORT`, unrelated); `black --check .`, `ruff check .`, `mypy typsphinx/` all
  clean

## Task Commits

1. **Task 1: Backfill 0.4.4, merge the duplicate Unreleased, and strip the emoji from CHANGELOG.md** - `0fbfe1d` (docs)
2. **Task 2: Correct the changelog page's remaining framing sections** - `66304e2` (docs)
3. **Task 3: Changelog-page regression gate plus the clean-build delta evidence** - `13d7743` (test)

## Files Created/Modified

- `CHANGELOG.md` - backfilled `## [0.4.4]` section + link reference; merged duplicate
  `[Unreleased]`; removed 25 `✅` characters
- `docs/source/changelog.rst` - added two Migration Guides subsections (0.6.x→0.7.0, 0.5.x→0.6.x);
  rewrote Release Process against the real `release.yml` job graph
- `tests/test_changelog_page_gate.py` - new regression module (`TestPublishedChangelogPageDelegates`,
  `TestChangelogPageContentCoverage`, `TestChangelogIncludeCompilesToPdf`)
- `tests/fixtures/changelog_include_gate/conf.py`, `index.rst`, `changelog.rst` - new fixture
  project reading the real repo-root `CHANGELOG.md`
- `.planning/phases/45-documentation-currency-carried-hygiene/45-GATE-EVIDENCE-02-docs-build-clean.md` -
  post-change warning-delta evidence (created)

## Decisions Made

- **0.4.4 section content:** derived from the real commit range and GitHub Release, curated to
  user-facing prose in the `### Added`/`### Changed`/`### Fixed` convention the neighbouring entry
  uses, not a commit dump.
- **Checkmark rewording (D-05):** removing the `- ✅ ` prefix and relying on each line's existing
  `(100%)` plus the section's `Requirements Fulfilled` / `fully implemented` framing to carry the
  completion statement, rather than inserting new wording -- the lightest edit that still satisfies
  "reads as a completion statement without the glyph."
- **Fixture include shape (deviation from the plan's literal action text, Rule 1):** the plan's
  `<action>` for Task 3 said the fixture should use "the same `:parser:` and `:start-line:` options
  `docs/source/changelog.rst` uses." Plan 45-01 (which landed before this plan started) dropped
  `:start-line:` entirely from the real page, per its own documented Rule-1 deviation. The fixture
  was built to match the REAL current shape (`:parser:` only, no `:start-line:`) rather than the
  plan's now-stale literal text -- the plan's own acceptance criteria only assert `:parser:`
  presence, not `:start-line:`, so this is consistent with the plan's actual bar, and with the
  upstream-context instruction to follow reality over a since-superseded plan detail.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Local `.venv/bin/uv` is a broken NixOS-incompatible ELF, causing 45 pre-existing integration-test failures unrelated to this plan's changes**

- **Found during:** Task 3's full-suite `<verification>` sweep (`uv run pytest`, run to confirm no
  regression from the changelog changes)
- **Issue:** `tests/test_integration_basic.py`, `test_integration_advanced.py`,
  `test_integration_multi_doc.py`, and `test_integration_nested_toctree.py` (45 tests total, all
  unrelated to `CHANGELOG.md`/`changelog.rst`) invoke `["uv", "run", "sphinx-build", ...]` as a
  subprocess. This worktree's `uv sync`-installed `.venv/bin/uv` is a generic-linux dynamically
  linked ELF the NixOS host cannot execute (`Could not start dynamically linked executable`) --
  the same class of pre-existing environment hazard plan 45-01's own summary recorded for
  `.venv/bin/ruff`, and that CLAUDE.md/PROJECT.md's footers document for `.venv/bin/uv` generally.
- **Fix:** Resolved a Nix-store `uv` (`command -v uv` inside the ambient shell resolves
  `/nix/store/.../uv-0.11.25/bin/uv`) and symlinked it over `.venv/bin/uv`, following the same
  local-shim precedent plan 45-01 used for `ruff`. Local, gitignored `.venv/` change only -- no
  repository file was touched.
- **Files modified:** none (repo); `.venv/bin/uv` (local, gitignored)
- **Verification:** re-ran the previously-failing test individually (passed), then the full suite:
  952 passed, 1 pre-existing unrelated skip, 0 failures.
- **Committed in:** N/A (no repo change)

**2. [Rule 3 - Blocking, environment-local] Same NixOS-sandboxed `ruff` binary issue plan 45-01 hit**

- **Found during:** Task 3, running `ruff check` on the new test module as instructed by the
  plan's verify block
- **Issue:** identical to plan 45-01's Deviation 2 -- `.venv/bin/ruff` is a NixOS-incompatible ELF.
- **Fix:** Resolved a Nix-store `ruff` (`nix-shell -p ruff`, resolved version `0.15.14`, within
  this repo's `ruff>=0.15,<0.16` pin) and symlinked it over `.venv/bin/ruff`, same as 45-01.
- **Files modified:** none (repo); `.venv/bin/ruff` (local, gitignored)
- **Verification:** `uv run ruff check .` printed `All checks passed!`.
- **Committed in:** N/A (no repo change)

---

**Total deviations:** 2 auto-fixed (both Rule 1/3, both environment-local, no repo change)
**Impact on plan:** Neither deviation touched any tracked file. Both were necessary to actually run
the plan's own `<verification>` gates in this NixOS-sandboxed worktree; without them the full-suite
sweep would have reported 45 spurious failures unrelated to DOC-12's content edits, and `ruff check`
would not have run at all.

## Issues Encountered

- A first attempt at capturing the post-change warning delta reused an incremental Sphinx output
  directory, which under-reported warnings (Sphinx's incremental rebuild skips unchanged source
  files and their docutils/myst-parser warnings do not re-fire). Corrected by rebuilding into a
  fresh scratch directory before recording the final counts in
  `45-GATE-EVIDENCE-02-docs-build-clean.md`; the recorded numbers are from the from-scratch runs.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- DOC-12 is fully discharged by plans 45-01 + 45-02 together: the delegation mechanism (45-01) plus
  a complete, deduplicated, emoji-free `CHANGELOG.md` and a corrected framing set (45-02), proven by
  a standing regression gate and a zero-delta warning measurement.
- `docs/source/changelog.rst` now contains only the include directive plus evergreen framing (135
  lines total) -- confirmed by diff inspection and pinned mechanically by
  `TestPublishedChangelogPageDelegates`. Phase 46's `## [0.7.1]` entry is a `CHANGELOG.md`-only
  edit, with zero required edit to `changelog.rst`.
- No blockers for plan 45-04 (QUA-02, QUA-03) or Phase 46 -- neither depends on
  `CHANGELOG.md`/`docs/source/changelog.rst`/`tests/test_changelog_page_gate.py` beyond the
  one-line-addition property this plan confirmed.
- Carried forward (not this plan's scope, flagged per the plan's own instruction): the `ja` site
  will render every line this plan's edits newly surface as untranslated prose until
  `typsphinx-doc-translations`'s gettext catalogs are regenerated -- out of this repository's scope,
  to be flagged again at the milestone close.

## Self-Check: PASSED

All 8 created/modified files confirmed present on disk (`CHANGELOG.md`, `docs/source/changelog.rst`,
`tests/test_changelog_page_gate.py`, the 3 `tests/fixtures/changelog_include_gate/` files,
`45-GATE-EVIDENCE-02-docs-build-clean.md`, `45-02-SUMMARY.md`). All 4 commit hashes
(`0fbfe1d`, `66304e2`, `13d7743`, `ed18e6d`) confirmed present in `git log --oneline --all`.

---
*Phase: 45-documentation-currency-carried-hygiene*
*Completed: 2026-08-10*
