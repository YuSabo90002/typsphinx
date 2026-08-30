---
phase: 63-v0-9-2-release-prep-prep-only
reviewed: 2026-08-30T00:00:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - pyproject.toml
  - README.md
  - CHANGELOG.md
  - tests/test_changelog_page_gate.py
findings:
  critical: 1
  warning: 0
  info: 1
  total: 2
status: issues_found
---

# Phase 63: Code Review Report

**Reviewed:** 2026-08-30T00:00:00Z
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

This is a release-prep-only phase: version literal bump (`pyproject.toml`, `README.md`),
promotion of the accumulated `## [Unreleased]` content into a new `## [0.9.2]` section in
`CHANGELOG.md` with its tail link, and an extension of `RELEASE_VERSIONS` in
`tests/test_changelog_page_gate.py`.

The mechanical parts check out: `pyproject.toml` version (`0.9.2`) matches `README.md`'s status
line and the new `## [0.9.2]` CHANGELOG heading; no stale `0.9.0` literal survives anywhere in
these four files outside of historical/backward references that are supposed to name 0.9.0 (the
old heading, the old release-tag link, and prose that legitimately discusses "the published 0.9.0
release"); no duplicate `## [x.y.z]` headings or duplicate `[x.y.z]:` link definitions were
introduced; the `[Unreleased]` compare link was correctly advanced from `v0.9.0...HEAD` to
`v0.9.2...HEAD`; and `RELEASE_VERSIONS` in the test file was correctly extended with `"0.9.2"` and
its count comment updated from 15 to 16 — the tuple's 16 entries match 16 of the 22 `##` version
headings actually present in `CHANGELOG.md` (the pre-`0.4.1` releases were already covered by the
docs page before its freeze point, per the existing test's own design intent, so their absence
from the tuple is not new to this phase).

However, one of the "Verified" claims newly written into the `## [0.9.2]` CHANGELOG entry by this
phase is checkable against git history and is false as written — see CR-01. I also flag one
pre-existing, lower-severity comment inaccuracy this phase had the opportunity to fix but did not
(IN-01).

## Critical Issues

### CR-01: `## [0.9.2]` release-note claims the runtime diff is confined to `translator.py`, but four other `typsphinx/` files also changed

**File:** `CHANGELOG.md:19-25`

**Issue:** The new `## [0.9.2]` section's intro paragraph states:

> "The runtime changes are confined to `typsphinx/translator.py`, with no other file under
> `typsphinx/` touched."

This is checkable and false. `git diff --stat v0.9.0..HEAD -- typsphinx/` shows five files
changed since the 0.9.0 tag, not one:

```
typsphinx/builder.py           | 306 ++++++++++++++++++++++++++++++++++-------
typsphinx/pathfmt.py           |  96 +++++++++++++ (new file)
typsphinx/template_registry.py |  25 +++-
typsphinx/translator.py        |  33 ++++-
typsphinx/writer.py            |   6 +-
5 files changed, 408 insertions(+), 58 deletions(-)
```

The paragraph itself describes four fixes bundled into this release — the output-directory escape
check (PATH-01), the absolute image URI fix (IMG-04..07), diagnostic message quoting (MSG-02..05),
and the image-visitor separator fix (IMG-08..10) — joined with "together with," so the natural
reading of "the runtime changes" is "the runtime changes that make up this release," which plainly
touches `builder.py` (306 lines), the brand-new `pathfmt.py` (96 lines), and
`template_registry.py` (25 lines) in addition to `translator.py`. Even under the most charitable
narrower reading — that the sentence means to scope only the image-visitor fix (which genuinely
was `translator.py`-only, confirmed via `git diff --stat` on the phase-62 commit range) — the
sentence as placed is dangerously ambiguous and will be read by anyone auditing the security-
relevant path-handling fixes (PATH-01, IMG-04..07, MSG-02..05 are exactly the kind of change a
downstream integrator would want to diff) as license to skip reviewing `builder.py`,
`pathfmt.py`, and `template_registry.py` entirely. A changelog is exactly the artifact a security-
conscious consumer reads to scope their own review of a release; asserting a false, narrower blast
radius for path-traversal/escaping-related fixes is a release-note defect that should block
publishing this CHANGELOG as-is.

**Fix:** Either scope the sentence explicitly to the one fix it is actually true for, or drop the
false generalization:

```markdown
- **An image not first in its container no longer aborts the `typstpdf` compile (IMG-08, IMG-09,
  IMG-10).** ... `visit_image()` now joins the translator's existing separator discipline, so
  every one of those containers compiles. This fix is confined to `typsphinx/translator.py`; no
  other file under `typsphinx/` was touched for it.
```

and remove (or generalize honestly) the blanket claim in the intro paragraph, e.g.:

```markdown
This release curates the Windows-shaped path-handling hardening accumulated since 0.9.0 ...
together with a separate compile-blocking defect in the image visitor. A project built with the
published 0.9.0 release produced no PDF for any master document when an image was not first in
its container, and 0.9.0 users should upgrade to this release. Zero new runtime dependencies; the
bundled `@preview` version-sync surface is untouched.
```

(dropping the file-confinement sentence entirely, since the milestone's actual runtime diff spans
`builder.py`, `pathfmt.py`, `template_registry.py`, `translator.py`, and `writer.py`).

## Info

### IN-01: `RELEASE_VERSIONS` count-comment still says "0.4.4 through 0.9.2" while the tuple starts at "0.4.1"

**File:** `tests/test_changelog_page_gate.py:47`

**Issue:** The comment above `RELEASE_VERSIONS` reads:

```python
# The 16 releases the published page was frozen without (0.4.4 through 0.9.2,
# inclusive) -- shared by both the HTML and PDF content-coverage assertions
```

but the tuple's first three entries are `"0.4.1"`, `"0.4.2"`, `"0.4.3"` before `"0.4.4"` — the
comment's stated range (`0.4.4 through 0.9.2`) omits three of the sixteen entries it claims to
describe. This inaccuracy pre-dates this phase (the prior text said "0.4.4 through 0.9.0" against
the same `0.4.1`-first tuple), but this phase touched this exact comment line (bumping the count
15→16 and the upper bound 0.9.0→0.9.2) and had the opportunity to correct the range while it was
already being edited.

**Fix:**

```python
# The 16 releases the published page was frozen without (0.4.1 through 0.9.2,
# inclusive) -- shared by both the HTML and PDF content-coverage assertions
# below so the two builders are held to the identical bar.
```

---

_Reviewed: 2026-08-30T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
