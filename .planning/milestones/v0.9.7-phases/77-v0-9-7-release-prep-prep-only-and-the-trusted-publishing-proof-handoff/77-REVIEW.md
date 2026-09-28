---
phase: 77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff
reviewed: 2026-09-28T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - CHANGELOG.md
  - README.md
  - pyproject.toml
  - tests/test_changelog_page_gate.py
  - uv.lock
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Phase 77: Code Review Report

**Reviewed:** 2026-09-28
**Depth:** standard
**Files Reviewed:** 5
**Status:** clean

## Summary

This is a single self-contained "chore(release): prepare 0.9.7" commit
(`39cb79f9`, `d872bafa63f10adbac2f0b3483cb201c5de0bf93^..HEAD` for the
reviewed file set): a version-literal bump in `pyproject.toml`/`uv.lock`,
a matching `README.md` Status-line edit, a curated `## [0.9.7]` CHANGELOG
section with a moved tail link block, and a `RELEASE_VERSIONS` tuple/comment
update in `tests/test_changelog_page_gate.py`. `git show --stat 39cb79f9`
confirms no file outside this five-file set was touched.

Every factual claim in scope was independently re-derived from the repo
rather than taken on trust:

- **Version-literal consistency.** `pyproject.toml` (`0.9.6` → `0.9.7`) and
  `uv.lock`'s `typsphinx` package version move together; `diff <(git show
  v0.9.6:uv.lock) <(git show HEAD:uv.lock)` shows the version line as the
  *only* difference in the entire lockfile versus the `v0.9.6` tag — matching
  the CHANGELOG's "Verified" claim that `uv.lock`'s package-name set is
  identical to the tag's, byte for byte. `README.md`'s Status line was the
  only other version literal found (`grep -n "0\.9\." README.md`); no stale
  `0.9.6` reference was left anywhere in the reviewed set. `docs/source/conf.py`
  reads `version` dynamically from `pyproject.toml`, so there is no
  fourth literal to have drifted.
- **`## [0.9.7]` CHANGELOG accuracy.**
  - The MSG-06 "Fixed" bullet ("two DEBUG-only diagnostic messages") matches
    `git diff v0.9.6..HEAD -- typsphinx/translator.py` exactly: both
    `up_path='{up_path}'` / `down_path='{down_path}'` f-string interpolations
    were changed to route through `quote_path()`, and no other file was
    touched for it.
  - `tests/test_translator_path_quoting_gate.py` exists and asserts against
    exactly those two call sites' DEBUG output, backing the "bound by a real
    regression gate" claim.
  - The Trusted Publishing / PEP 740 "Changed" bullet matches the current
    `.github/workflows/release.yml`: top-level `permissions: id-token: write`
    is present, and `git diff v0.9.6..HEAD -- .github/workflows/release.yml`
    shows the `publish-pypi` step's `with: password: ${{ secrets.PYPI_API_TOKEN }}`
    was removed, leaving a bare `pypa/gh-action-pypi-publish@release/v1`
    call — consistent with "authenticates with a short-lived OIDC token
    instead of a long-lived API token."
  - The "Verified" bullet about the four bundled `@preview` package versions
    being unchanged across `writer.py` / `template_engine.py` /
    `templates/base.typ` holds: `git diff v0.9.6..HEAD` for those three files
    is empty, and all three currently agree
    (`codly:1.3.0`, `codly-languages:0.1.10`, `mitex:0.2.7`, `gentle-clues:1.3.1`).
  - The release date `2026-09-28` in the heading matches both the commit's
    own author date (`2026-09-28T22:17:05+09:00`) and today's date.
- **Tail link block.** `[0.9.7]` was inserted above `[0.9.6]` in correct
  descending order, and `[Unreleased]` was advanced to
  `compare/v0.9.7...HEAD`. `grep -n "^## \["` confirms exactly one `[0.9.7]`
  heading and exactly one top-of-file `[Unreleased]` heading, with no
  duplicate or out-of-order section.
- **`RELEASE_VERSIONS` count/comment sync.** The comment says "The 18
  releases the published page was frozen without (0.4.1 through 0.9.7,
  inclusive)"; the tuple was counted by hand and holds exactly 18 entries
  ending in `"0.9.7"`, added directly below the pre-existing `"0.9.6"` entry
  — count and range statement agree with the actual tuple contents.

No defect — of any severity — was found in this diff. All reviewed claims
were traceable to and confirmed by the actual repository state rather than
merely "looking plausible."

All reviewed files meet quality standards. No issues found.

---

_Reviewed: 2026-09-28_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
