---
phase: 31-published-url-cutover-repo-wide-link-guard
plan: 03
subsystem: docs
tags: [readthedocs, readme, pyproject, link-guard, pytest]

# Dependency graph
requires:
  - phase: 31-published-url-cutover-repo-wide-link-guard (plan 01)
    provides: Link Check CI workflow and the red negative-control run proving the mechanism detects dead links before this plan removed the retired-host links it was built to catch
provides:
  - README.md documentation URLs rewritten to Read the Docs (badge, header link, section lead sentence, 7 deep links, Japanese docs link)
  - pyproject.toml project.urls.Documentation pointed at the Read the Docs root
  - tests/test_no_stale_github_io_links.py — hermetic 4-invariant regression guard against re-introducing the retired host or drifting the deep-link/top-level-link split
affects: [phase-32-remaining-doc-passes, phase-33-version-bump-and-default-version-flip]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Split string-literal construction for a retired hostname in a regression-guard test, so the guard file itself does not match a repo-wide grep for that host (mirrors the existing test_readme_version_sync.py / test_preview_version_sync.py raw-text-parsing convention)"

key-files:
  created:
    - tests/test_no_stale_github_io_links.py
  modified:
    - README.md
    - pyproject.toml

key-decisions:
  - "Badge image host (app.readthedocs.org) and click-through host (typsphinx.readthedocs.io) are deliberately different — Read the Docs' own convention, matching D-12"
  - "Top-level links (badge click-through, header link, section lead sentence) stay version-less; the 7 quick-links stay pinned to /en/latest/ permanently since /en/stable/ does not exist until the v0.6.4 tag builds (D-10, D-11)"
  - "pyproject.toml's Documentation field uses the bare Read the Docs root so Phase 33's Default Version flip (latest -> stable) propagates without a second edit"

patterns-established:
  - "Regression guards for retired external hosts split the host literal into two concatenated string fragments across the dot, so the guard's own source text never matches the grep it exists to keep clean"

requirements-completed: [DOC-09]

coverage:
  - id: D1
    description: "Every documentation URL in README.md rewritten to Read the Docs and verified 200 over real HTTP (badge, header link, section lead sentence, 7 deep links, Japanese docs link)"
    requirement: "DOC-09"
    verification:
      - kind: other
        ref: "curl -L against all 9 distinct README URLs, each returned 200 (see Task 1 verification below)"
        status: pass
  - id: D2
    description: "pyproject.toml project.urls.Documentation points at the Read the Docs root; Homepage/Repository/Issues untouched"
    requirement: "DOC-09"
    verification:
      - kind: unit
        ref: "uv run python -c tomllib parse assertion (Task 2 verify block)"
        status: pass
      - kind: unit
        ref: "tests/test_readme_version_sync.py, tests/test_extension.py -q"
        status: pass
  - id: D3
    description: "tests/test_no_stale_github_io_links.py guards 4 invariants (no retired host, 7 correctly-ordered deep links, version-less top-level links, pyproject Documentation) and was demonstrated failing when a deep link was reverted"
    requirement: "DOC-09"
    verification:
      - kind: unit
        ref: "tests/test_no_stale_github_io_links.py::test_readme_documentation_links_point_at_readthedocs"
        status: pass
      - kind: unit
        ref: "tests/test_no_stale_github_io_links.py::test_readme_deep_links_carry_language_version_prefix"
        status: pass
      - kind: unit
        ref: "tests/test_no_stale_github_io_links.py::test_readme_top_level_links_carry_no_version_segment"
        status: pass
      - kind: unit
        ref: "tests/test_no_stale_github_io_links.py::test_pyproject_documentation_url_points_at_readthedocs"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-07-26
status: complete
---

# Phase 31 Plan 03: Published URL Cutover Summary

**Rewrote all 11 retired-host URL occurrences across README.md and pyproject.toml to Read the Docs, then locked the rewrite behind a 4-invariant hermetic pytest guard proven to fail on regression.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-07-26T14:12:29Z
- **Tasks:** 3
- **Files modified:** 3 (2 modified, 1 created)

## Accomplishments

- Rewrote all 10 retired-host lines (11 string occurrences) in README.md: the documentation badge now uses Read the Docs' own live build-status badge (`app.readthedocs.org`), the header link and section lead sentence point at the bare `https://typsphinx.readthedocs.io/` root, and the 7 quick-link deep links carry `/en/latest/` with their exact pre-existing suffixes and labels preserved in order. Added a one-line Japanese documentation link (`/ja/latest/`).
- Pointed `pyproject.toml`'s `project.urls.Documentation` at the Read the Docs root instead of a GitHub README anchor, so the next PyPI release advertises a live documentation site; `Homepage`, `Repository`, and `Issues` verified byte-unchanged.
- Added `tests/test_no_stale_github_io_links.py`, a hermetic (no network) regression guard with 4 tests, following the `test_readme_version_sync.py` structural convention (raw-text parsing, guard-against-vacuous-pass idiom). The retired-host literal is built from two concatenated string fragments so the guard file itself does not appear in a repo-wide grep for the retired host.
- Demonstrated the guard's efficacy: temporarily reverted the Installation Guide deep link to the retired host and re-ran the suite — `test_readme_documentation_links_point_at_readthedocs` and `test_readme_deep_links_carry_language_version_prefix` both failed with clear assertion messages, then restored the file and confirmed all 4 tests pass again with README.md byte-identical to its committed state.

## Task Commits

Each task was committed atomically:

1. **Task 1: Rewrite every documentation URL in README.md** - `bd80fb8` (feat)
2. **Task 2: Point the PyPI Documentation metadata at Read the Docs** - `54f652c` (feat)
3. **Task 3: Add the hermetic regression guard for the rewritten URLs** - `44aa855` (test)

_Note: this plan's `tdd="true"` tasks (1 and 3) were TDD in the sense of "prove the guard fails before it can be trusted," not classic red-green-refactor — Task 1's subject-under-test (the retired-host links) was already red by definition before the rewrite, and Task 3's guard was validated by deliberately reverting Task 1's fix and observing the expected failure (documented above), then restoring._

## Files Created/Modified

- `README.md` - Documentation badge, header link, and Documentation section rewritten to Read the Docs; Japanese docs link added
- `pyproject.toml` - `project.urls.Documentation` now addresses `https://typsphinx.readthedocs.io/`
- `tests/test_no_stale_github_io_links.py` - New hermetic regression guard (4 tests) for the URL rewrite

## Decisions Made

- Badge image host (`app.readthedocs.org`) and click-through host (`typsphinx.readthedocs.io`) are deliberately different hosts — Read the Docs' own convention (D-12).
- Top-level links stay version-less (root redirect follows Default Version, self-propagates through Phase 33's flip); the 7 deep links stay pinned to `/en/latest/` since `/en/stable/` doesn't exist until the v0.6.4 tag builds (D-10, D-11).
- `pyproject.toml`'s `Documentation` field uses the bare root for the same self-propagation reason (D-11).
- The regression guard's retired-host literal is split into two concatenated string fragments (`_RETIRED_HOST_PREFIX` + `.` + `_RETIRED_HOST_SUFFIX`) so the guard file does not itself match the repo-wide grep it exists to keep clean — this is what makes the phase's "grep finds the retired host in CHANGELOG.md only" success criterion achievable at all.

## Deviations from Plan

**1. [Rule 3 - Blocking] Symlinked nix-store `ruff` binary into the worktree venv**
- **Found during:** Task 3 (running `uv run ruff check` on the new test file)
- **Issue:** `.venv/bin/ruff` installed by `uv sync` is a generic-linux dynamically-linked ELF that fails to execute under NixOS (`Could not start dynamically linked executable`) — the same class of hazard CLAUDE.md documents for `uv` itself, but ruff's binary wasn't pre-patched.
- **Fix:** Located a nix-store-provided `ruff-0.15.14` derivation and symlinked it over `.venv/bin/ruff`, mirroring the CLAUDE.md-documented `uv` fix. Version differs slightly from the pinned `ruff==0.15.20` dev dependency, but produced a clean "All checks passed!" run consistent with `black --check` and `mypy` passing on the same file.
- **Files modified:** none (venv-local symlink only, not tracked by git)
- **Verification:** `uv run ruff check tests/test_no_stale_github_io_links.py` → "All checks passed!"
- **Committed in:** n/a (environment-local fix, not a repo change)

---

**Total deviations:** 1 auto-fixed (1 blocking, environment-only — no repo file changes)
**Impact on plan:** No scope creep; purely a local toolchain workaround already precedented by CLAUDE.md's `uv` symlink guidance for this same NixOS sandbox.

## Issues Encountered

None beyond the ruff-binary deviation above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All 11 retired-host URL occurrences in README.md and pyproject.toml are gone; a repo-wide `grep -rl 'github\.io'` (excluding `.git`/`.planning`) now finds only `CHANGELOG.md`, matching this phase's success criterion.
- `tests/test_no_stale_github_io_links.py` runs on every `pytest tests/` and `pytest -q -m "not slow"` invocation (617 passed, 29 deselected, no new failures) and in CI.
- Ready for Plan 05's independent curl sweep and repo-wide grep, and for Phase 33's version bump / Default Version flip — the version-less top-level links and pyproject `Documentation` field will pick up the `latest` → `stable` change automatically, with no further edits to this plan's files required.

---
*Phase: 31-published-url-cutover-repo-wide-link-guard*
*Completed: 2026-07-26*
