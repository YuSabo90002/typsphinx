---
phase: 73-v0-9-5-close-prep-prep-only-unpublished
reviewed: 2026-09-16T00:00:00Z
depth: standard
files_reviewed: 1
files_reviewed_list:
  - CHANGELOG.md
findings:
  critical: 0
  warning: 0
  info: 1
  total: 1
status: issues_found
---

# Phase 73: Code Review Report

**Reviewed:** 2026-09-16T00:00:00Z
**Depth:** standard
**Files Reviewed:** 1
**Status:** issues_found

## Summary

This phase's only product-tree change is a 15-line, pure-addition edit to `CHANGELOG.md`: a new
`### Added` subsection (the `tox -e linkcheck` environment, QUA-13/DOC-24) and a new `### Fixed`
subsection (the HTML sidebar toctree-duplication fix, DOC-18), both inserted under the existing
`## [Unreleased]` heading.

Every substantive claim in the added text was independently checked against the current
repository state, since `CHANGELOG.md` is published documentation (included wholesale into
`docs/source/changelog.rst` via MyST):

- `[testenv:linkcheck]` exists in `tox.ini`, runs `sphinx-build -b linkcheck source
  _build/linkcheck`, and is correctly excluded from `env_list = py312, py313, lint, type, cov,
  docs` — matching the "not part of a plain `tox` run" claim.
- `docs/source/conf.py` sets no `linkcheck_anchors` override, so Sphinx's linkcheck builder
  checks anchors by default — matching the "including their `#anchor` targets" claim.
- `CLAUDE.md`, `README.md`, and `docs/source/contributing.rst` all list `tox -e linkcheck`
  immediately beside `docs-html`/`docs-pdf` — matching the "listed alongside" claim.
- `docs/source/index.rst`'s User Guide and Examples toctrees list only `user_guide/index` and
  `examples/index` respectively (the flat child entries are gone) — matching the DOC-18 claim
  that each page now appears exactly once, nested under its section.
- Requirement IDs QUA-13, DOC-24, and DOC-18 all exist in `.planning/REQUIREMENTS.md`, are marked
  `[x]` complete, and are attributed to Phase 72 — the phase that actually implemented the
  underlying `tox.ini` and `index.rst` changes this changelog text describes.
- No version string this phase introduces (0.9.3/0.9.4/0.9.5, with or without `v`) appears
  anywhere in the diff; the entries correctly stay under `## [Unreleased]`.
- `git tag -l "v0.9.*"` confirms `v0.9.2` is the latest released tag, so the untouched
  `[Unreleased]: .../compare/v0.9.2...HEAD` link at the end of the file remains correct — this
  phase did not need to (and did not) touch it.
- Heading order (`Added` → `Changed` → `Fixed` → `Planned for Future Releases`) matches Keep a
  Changelog's canonical ordering and the register/bullet shape (`**Bold headline (ID).**
  Explanation…`, ending in "This has no effect on installing or using typsphinx." where
  applicable) matches every neighboring entry in the same `## [Unreleased]` section and in the
  released `[0.9.2]` section below it.
- No malformed Markdown: both new subsections have correct blank-line separation before/after,
  consistent list-continuation indentation (2 spaces), and no dangling or broken link references.

No Critical or Warning findings. One Info-level observation below.

## Info

### IN-01: DOC-18 entry omits the still-live HTML/Typst parent-structure divergence noted in REQUIREMENTS.md

**File:** `CHANGELOG.md:57-60`
**Issue:** The `REQUIREMENTS.md` "Non-Goals" table (line 46) records that DOC-18's dedup may
leave a residual "HTML-vs-Typst parent divergence for `examples/basic`" to be re-measured and
"filed separately only if it survives." The changelog's Fixed entry states unconditionally that
the sidebar issue is resolved and that "Sphinx no longer reports them as referenced in multiple
toctrees," which is accurate as far as it goes, but a reader relying solely on the changelog has
no signal that a related, narrower structural question was deliberately left open rather than
verified closed. This is not a false claim — everything stated is independently confirmed true —
but it is a case where the published changelog is less complete than the internal requirements
record about the boundary of what was fixed.
**Fix:** Optional, since this is documentation-completeness rather than an inaccuracy. If the
owner wants the changelog to be self-sufficient on this point, a trailing clause could be added,
e.g.: "...multiple toctrees. A separate, narrower `examples/basic` parent-structure question
between the HTML and Typst outputs was checked and found not to reproduce after this fix." No
change is required if the project intends REQUIREMENTS.md/ROADMAP.md to be the system of record
for that level of detail and the changelog to stay reader-facing.

---

_Reviewed: 2026-09-16T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
