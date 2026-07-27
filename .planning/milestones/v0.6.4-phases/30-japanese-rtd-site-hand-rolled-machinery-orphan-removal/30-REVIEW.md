---
phase: 30-japanese-rtd-site-hand-rolled-machinery-orphan-removal
reviewed: 2026-07-26T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - tox.ini
  - .github/workflows/docs.yml
  - docs/Makefile
  - docs/source/conf.py
  - tests/test_readthedocs_config.py
findings:
  critical: 0
  warning: 1
  info: 0
  total: 1
status: issues_found
---

# Phase 30: Code Review Report

**Reviewed:** 2026-07-26T00:00:00Z
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Reviewed the five surviving modified files against the pre-phase baseline
(`git diff 458ffc8..HEAD -- <files>`) plus a full read of each file's
current state. The removal of the hand-rolled multi-language build
machinery is clean: no dangling references remain anywhere in the live
tree (outside `.planning/`) to `build_multilang.py`, the `docs-multilang`
tox env, the `multilang`/`serve-multilang`/`locale-init`/`locale-update`/
`html-ja`/`gettext` Makefile targets, `docs/_build/multilang`,
`html_context`, `html_sidebars`, `html_static_path`, `html_css_files`, or
the deleted `language-switcher.html`/`page.html`/`custom.css` templates.
CI's HTML upload/publish paths (`docs/_build/html`) correctly match the
`docs-html` tox env's output directory (`sphinx-build -b html source
_build/html` with `changedir = docs`), and the PDF paths
(`docs/_build/pdf/*.pdf`) correctly match `docs-pdf`. The one updated test
(`test_language_seam_precedence`) was correctly repointed from asserting
on the deleted `html_context` dict to asserting on
`typst_elements["lang"]`, and its assertion count (39), function count
(4), and `typst_elements[` occurrence count (4) all match the plan's own
verification gate. All 4 tests in `tests/test_readthedocs_config.py` pass
under `uv run pytest`.

One quality gap was found: two config values in `docs/source/conf.py` now
point at directories this phase deleted, and while both are confirmed
functionally inert (measured, documented in `.planning/`), the file itself
carries no comment explaining why — see WR-01.

## Warnings

### WR-01: Orphaned config values left with no in-file rationale

**File:** `docs/source/conf.py:44` and `docs/source/conf.py:58-61`
**Issue:** `templates_path = ["_templates"]` and the `locale_dirs`/
`gettext_*` block reference directories (`docs/source/_templates/`,
`docs/locale/`) that this phase deleted (commits `204f7ef` and `131ae4a`
respectively — confirmed via `git log` and `ls`, both directories are
gone). Both were deliberately left in place — per
`.planning/phases/30-*/30-02-SUMMARY.md` and `30-03-SUMMARY.md`, both were
measured to no-op harmlessly (Sphinx emits no build warning for either an
absent `templates_path` target or an absent `locale_dirs` target;
`locale_dirs` is additionally shared byte-for-byte with the
`typsphinx-doc-translations` repository's own copy of `conf.py`) — but the
file itself carries zero comment explaining this. A future contributor
reading only `conf.py` (not the `.planning/` archive) has no way to know
these are intentional dead references rather than leftover bugs from an
incomplete cleanup, and might reasonably "fix" them by deleting the lines
(breaking the deliberate byte-for-byte sharing with
`typsphinx-doc-translations` for `locale_dirs`) or by recreating the now
long-gone empty directories. This is inconsistent with how the same file
documents its *other* deliberate leftover decision: the `typst_template`
block a few lines below (lines 78-94) carries an 18-line comment
explaining exactly why it exists and what constraint it operates under,
while `locale_dirs`/`templates_path` get none.
**Fix:** Add a short in-file comment at each site, e.g.:
```python
# `docs/locale/` was removed in Phase 30 (typsphinx-doc-translations now
# owns the Japanese catalog) but this block stays: it is shared
# byte-for-byte with that repo's own copy of conf.py, and Sphinx no-ops
# harmlessly when the directory is absent (verified: no new build warning,
# see 30-03-SUMMARY.md).
locale_dirs = ["../locale/"]
gettext_compact = False  # Generate separate .pot files for each document
gettext_uuid = False  # Do not use UUIDs in .pot files
gettext_auto_build = True  # Automatically build gettext catalogs
```
and similarly above `templates_path = ["_templates"]`:
```python
# `docs/source/_templates/` was emptied by Phase 30's language-switcher
# removal; kept because Sphinx emits no warning for an absent
# templates_path target (unlike html_static_path, which is why that one
# was deleted -- see 30-02-SUMMARY.md).
templates_path = ["_templates"]
```

---

_Reviewed: 2026-07-26T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
