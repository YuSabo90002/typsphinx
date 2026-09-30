---
phase: 28-v0-6-3-release-prep-regression-gate-close
reviewed: 2026-07-25T00:00:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - CHANGELOG.md
  - README.md
  - pyproject.toml
  - uv.lock
findings:
  critical: 0
  warning: 1
  info: 1
  total: 2
status: issues_found
---

# Phase 28: Code Review Report

**Reviewed:** 2026-07-25
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

This phase's entire change surface is a mechanical version bump (0.6.2 → 0.6.3) plus a new
`CHANGELOG.md` entry and link-block update — no Python source changed. Verified:

- **Version consistency**: `pyproject.toml:7` (`version = "0.6.3"`), `uv.lock`'s `typsphinx`
  self-entry (`version = "0.6.3"`), and `README.md:315`'s Status line (`Stable (v0.6.3)`) all agree.
  `typsphinx/__init__.py` resolves `__version__` dynamically via
  `importlib.metadata.version("typsphinx")` (confirmed by reading the file), so `pyproject.toml` is
  genuinely the sole hardcoded version literal, as the commit message claims — no other literal was
  found via a repo-wide grep for `0.6.2` outside `.planning/` and `CHANGELOG.md`'s own history.
- **`uv.lock` integrity**: the diff against the pre-phase commit touches exactly one line — the
  `typsphinx` package's own `version` field. No dependency specifier, hash, sdist/wheel URL, or
  transitive package entry changed; `sphinx`/`docutils`/`typst` and all other locked entries are
  byte-identical. No unintended dependency drift.
- **`pyproject.toml` correctness**: dependency specifiers (`sphinx>=9.1,<10`, `docutils>=0.21,<0.23`,
  `typst>=0.15.0,<0.16`), classifiers, and the `sphinx.builders` entry points (`typst`/`typstpdf` →
  `typsphinx`) are unchanged and internally consistent with README's stated requirements
  (Python 3.12+, Sphinx 9.1+, Typst 0.15+).
- **`CHANGELOG.md` link block**: the new `[0.6.3]: .../releases/tag/v0.6.3` entry follows the exact
  URL pattern of every prior version link, is correctly inserted above `[0.6.2]` (descending order
  preserved), and `[Unreleased]: .../compare/v0.6.3...HEAD` was correctly advanced from
  `v0.6.2...HEAD`. Heading format (`## [0.6.3] - 2026-07-25`) matches the `## [X.Y.Z] - YYYY-MM-DD`
  convention used by every other entry.

Two issues surfaced, detailed below — one warning about a structural defect discovered in
`CHANGELOG.md`, and one informational note about the not-yet-existing release tag (expected at this
stage of the release-prep workflow, not a defect).

## Warnings

### WR-01: `CHANGELOG.md` contains two `## [Unreleased]` headings

**File:** `CHANGELOG.md:8` and `CHANGELOG.md:771`
**Issue:** The file has a legitimate `## [Unreleased]` heading at the top (line 8, immediately above
the new `## [0.6.3]` entry — currently empty, which is correct going forward) and a second,
unrelated `## [Unreleased]` heading buried inside the historical pre-0.2.0 section (line 771,
followed by a stale "### Planned for Future Releases" list: BibTeX, Glossary, Index, pre-commit
hooks, Typst Universe template integration — several of which either shipped since or are tracked
elsewhere). This second occurrence predates this phase's diff (it was not touched by the reviewed
commits), but it is a genuine structural defect in one of the four files under review: any tooling
or human editor that does a naive "insert new entries after `## [Unreleased]`" (e.g. `sed`/`awk`
matching the first occurrence, or a future automated changelog-bump script) will target whichever
occurrence it finds first depending on search direction, and a top-anchored search is not guaranteed
by the heading text alone. A single `grep -n "^## \[Unreleased\]"` returns two hits, which is
itself a footgun for any future automation this project might add around the version-bump step this
phase implements.
**Fix:** Remove or retitle the stale second occurrence at line 771 (e.g. to `### Planned (historical,
pre-0.2.0)` or fold its still-relevant items into the top-level `## [Unreleased]` / a tracked
backlog item, since BibTeX/Glossary/Index are still listed as "Known Limitations" in the current
README). At minimum, rename it so `grep -c "^## \[Unreleased\]" CHANGELOG.md` returns 1.

## Info

### IN-01: `CHANGELOG.md`'s new `[0.6.3]` release-tag link does not yet resolve

**File:** `CHANGELOG.md:782`
**Issue:** `[0.6.3]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.6.3` points at a git
tag that does not exist yet (`git tag -l "v0.6*"` returns only `v0.6.0`, `v0.6.1`, `v0.6.2`). This
mirrors the same pattern used for every prior release entry (the CHANGELOG link is added in the
version-bump commit; the tag itself is presumably created later by the actual publish/release step),
so this is expected at this stage of the release-prep phase and is not a defect — noted only so the
release step that creates the `v0.6.3` tag is not skipped, since the "Verified" review context for
this phase (§`scope_note`) is mechanical/structural rather than end-to-end release verification.
**Fix:** No action needed in this phase; confirm the tag is created as part of the actual publish
step (e.g. `complete-milestone` / `release.yml`) before considering the CHANGELOG link resolvable
by external readers.

---

_Reviewed: 2026-07-25_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
