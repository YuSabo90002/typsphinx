---
phase: 45-documentation-currency-carried-hygiene
reviewed: 2026-08-09T23:35:54Z
depth: standard
files_reviewed: 16
files_reviewed_list:
  - CHANGELOG.md
  - README.md
  - docs/source/changelog.rst
  - docs/source/conf.py
  - docs/source/quickstart.rst
  - docs/source/user_guide/configuration.rst
  - pyproject.toml
  - tests/fixtures/changelog_include_gate/changelog.rst
  - tests/fixtures/changelog_include_gate/conf.py
  - tests/fixtures/changelog_include_gate/index.rst
  - tests/fixtures/quickstart_docs_gate/conf.py
  - tests/fixtures/quickstart_docs_gate/index.rst
  - tests/test_changelog_page_gate.py
  - tests/test_quickstart_docs_gate.py
  - typsphinx/template_engine.py
  - uv.lock
findings:
  critical: 0
  warning: 3
  info: 0
  total: 3
status: issues_found
---

# Phase 45: Code Review Report

**Reviewed:** 2026-08-09T23:35:54Z
**Depth:** standard
**Files Reviewed:** 16
**Status:** issues_found

## Summary

This phase's stated production change — consolidating `derive_typst_lang()`'s rejection
warning to a single call site — was verified byte-identical to the two previously-duplicated
warning strings (`git diff` confirms the only change is control-flow restructuring; wording is
untouched). `mypy typsphinx/template_engine.py` and `black --check` both pass, and the full
`test_template_engine.py` + `test_preview_version_sync.py` suites (89 tests) pass, confirming no
regression to the `@preview` version-sync surfaces.

The `myst-parser>=5.0` dependency addition matches its stated intent exactly: it lands only in
`[project.optional-dependencies].docs` in both `pyproject.toml` and the regenerated `uv.lock`
(never in `dev` or base `dependencies`), and `docs-html`/`docs-pdf`/`docs` tox environments
already install `extras = docs`, so the new changelog-delegation build path is exercised
correctly by CI. I ran both new gate suites (`tests/test_changelog_page_gate.py`,
`tests/test_quickstart_docs_gate.py`) live with `uv run --extra dev --extra docs pytest`; all 11
tests pass, including the real `-b html` and `-b typstpdf` builds and the compiled-PDF
release-string coverage check — the changelog-delegation mechanism and the Quick Start
filename-derivation docs both hold up against a real build, not just static text assertions.

No Critical/security findings. Three Warning-level content-accuracy defects were found, two in
the delegated `CHANGELOG.md` content itself (one pre-existing, now exposed live via the new
delegation this phase ships) and one in a new test file's own explanatory comment (introduced by
this phase, does not affect test correctness).

## Warnings

### WR-01: Migration Guides page falsely claims 0.3.0 was non-breaking, directly contradicting the changelog content on the same page

**File:** `docs/source/changelog.rst:41-44`
**Issue:** The (pre-existing, untouched-by-this-diff) "Migrating from 0.2.x to 0.3.x" section
reads:

```rst
Migrating from 0.2.x to 0.3.x
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No breaking changes. Documentation site is a new feature.
```

This is factually wrong: `CHANGELOG.md`'s `## [0.3.0]` entry is headed `### Changed (Breaking)`
and describes a package rename (`sphinxcontrib-typst` → `typsphinx`) with an explicit 3-step
migration procedure (`pip uninstall sphinxcontrib-typst`, `pip install typsphinx`, update
`conf.py`'s `extensions` entry). Before this phase, `changelog.rst` rendered its own
hand-maintained (and separately stale) release history, so this contradiction was never visible
side-by-side. Phase 45's own change makes it directly visible: the page now `.. include::`s the
real `CHANGELOG.md` immediately above this "Migration Guides" section, so a reader sees the
"BREAKING: Package Rename" entry and then, a few paragraphs later on the exact same page, "No
breaking changes" for that same release. This is exactly the kind of drift the phase's own
delegation mechanism was built to eliminate, and it now ships live.
**Fix:** Correct the 0.2.x→0.3.x migration text to describe the package rename (or, better,
delete the redundant hand-maintained summary entirely now that the real `CHANGELOG.md` entry is
included verbatim above it, and let the Migration Guides section start from the next
transition). At minimum:

```rst
Migrating from 0.2.x to 0.3.x
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Breaking:** the package was renamed ``sphinxcontrib-typst`` → ``typsphinx``. Run
``pip uninstall sphinxcontrib-typst && pip install typsphinx`` and update ``conf.py``:
``extensions = ['sphinxcontrib.typst']`` → ``extensions = ['typsphinx']``.
```

### WR-02: `CHANGELOG.md`'s `[0.2.0]` entry is out of reverse-chronological order, contradicting the file's own stated convention

**File:** `CHANGELOG.md:868` (vs. `CHANGELOG.md:678,695`)
**Issue:** The file declares at the top that it follows "Keep a Changelog" (implicitly
reverse-chronological, newest first) and every other entry honors that. `## [0.2.0] -
2025-10-16` is placed after `## [0.1.0b1] - 2025-10-13` (line 695) — i.e., after an *older*
release — instead of between `## [0.2.1] - 2025-10-18` (line 678) and `## [0.1.0b1]`, where its
date would put it. This pre-dates phase 45 (confirmed via `git show <base>:CHANGELOG.md`, same
misplacement present before this phase's diff), but it is now surfaced on the live,
CI-content-verified `changelog.rst` page for the first time (the page previously never rendered
past `0.4.0`), so a reader browsing the published changelog in release order will hit an
out-of-order jump right at the end.
**Fix:** Move the `## [0.2.0] - 2025-10-16` section (and its content) to sit between the `##
[0.2.1]` and `## [0.1.0b1]` sections, and move its footnote link reference into chronological
position alongside the other version links.

### WR-03: New test file's explanatory comment misstates its own `RELEASE_VERSIONS` range

**File:** `tests/test_changelog_page_gate.py:47-49`
**Issue:**

```python
# The 12 releases the published page was frozen without (0.4.4 through 0.7.0,
# inclusive) -- shared by both the HTML and PDF content-coverage assertions
# below so the two builders are held to the identical bar.
RELEASE_VERSIONS = (
    "0.4.1",
    "0.4.2",
    "0.4.3",
    "0.4.4",
    ...
```

The comment says the frozen range is "0.4.4 through 0.7.0", but the tuple actually starts at
`0.4.1` (the page was frozen at `Version 0.4.0 (Current)`, confirmed via `git show
<base>^:docs/source/changelog.rst`, so the correct range is 0.4.1 through 0.7.0). The test's
own behavior is unaffected — it correctly checks all 12 listed versions — but the comment
misdescribes the data it sits next to, which will mislead a future maintainer who trusts the
comment over re-deriving the range from the old frozen page.
**Fix:**

```python
# The 12 releases the published page was frozen without (0.4.1 through 0.7.0,
# inclusive) -- shared by both the HTML and PDF content-coverage assertions
# below so the two builders are held to the identical bar.
```

---

_Reviewed: 2026-08-09T23:35:54Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
