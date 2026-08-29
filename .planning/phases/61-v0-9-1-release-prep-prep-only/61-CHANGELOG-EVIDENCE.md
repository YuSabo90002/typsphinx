# Phase 61 — CHANGELOG Evidence (SC#2 as REWORDED by D-11)

## This plan's base SHA

```
$ git rev-parse HEAD
5e28fa9dac8576f1f1665560eb5c4ccbd2e13b41
```

## Pre-edit measurements (taken before touching CHANGELOG.md)

```
$ grep -cE '^## \[' CHANGELOG.md
22

$ grep -cE '^\[[^]]+\]: https' CHANGELOG.md
22

$ grep -cE '^### Known Limitations' CHANGELOG.md
1

$ tail -1 CHANGELOG.md
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.0...HEAD

$ awk '/^## \[Unreleased\]/,/^## \[0\.9\.0\]/' CHANGELOG.md | grep -cE '^- \*\*'
0
```

All five pre-edit measurements match the expected values recorded in `61-01-PLAN.md`'s
`must_haves.truths`: 22 release headings, 22 link-reference lines, 1 `Known Limitations`
subsection, the verbatim final line ending `v0.9.0...HEAD`, and 0 real change bullets under
`## [Unreleased]` — confirming D-03's premise that this is authoring from scratch, not
promotion.

## What this file is NOT

`scripts/extract_changelog_section.py` is deliberately NOT invoked in this phase. There is no
`## [0.9.1]` (or any other new versioned) section for it to extract — D-11 moves that
reproduction check to the v0.9.2 release-prep phase, once a versioned section actually exists
to extract from.

## The PATH-01 bullet (tracer slice)

Authored under a new `### Fixed` subsection inside the existing `## [Unreleased]` block, placed
ABOVE the existing `### Planned for Future Releases` subsection (left untouched, still five
entries):

```markdown
### Fixed

- **A Windows-shaped `typst_documents` target that reaches outside the output directory is now
  refused on the normalized path, matching its sibling image-URI check (PATH-01).** The
  `typst_documents` escape predicate now applies its absolute-path and drive-qualified checks to
  the same backslash-normalized string its sibling image-URI predicate already used, rather than
  to the raw stem. Neither of the predicate's two real call sites can currently reach the gap this
  closes — both normalize or otherwise guarantee a safe value before calling it — so this is
  contract hardening for a future caller, not the repair of a defect any user was hitting.
```

**Accuracy basis:** `.planning/REQUIREMENTS.md` records PATH-01 with a "Reachability, measured
2026-08-27" note stating the gap is not reachable from either real call site
(`_resolve_target_stem()` normalizes before calling; `_track_image()` passes a value that always
carries a parent-directory segment). The bullet's final sentence states this explicitly and does
not claim a user was affected by the pre-fix predicate.

## Fence assertions after the bullet landed

```
$ grep -cE '^## \[' CHANGELOG.md
22

$ grep -cE '^\[[^]]+\]: https' CHANGELOG.md
22

$ tail -1 CHANGELOG.md
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.0...HEAD

$ awk '/^## \[Unreleased\]/,/^## \[0\.9\.0\]/' CHANGELOG.md | grep -cE '^- \*\*'
1

$ awk '/^## \[Unreleased\]/,/^## \[0\.9\.0\]/' CHANGELOG.md | grep -c 'PATH-01'
1

$ git status --porcelain typsphinx/ tests/
(empty)
```

All byte-identical to the pre-edit measurements except the intended addition (1 bullet, citing
PATH-01). No file under `typsphinx/` or `tests/` changed.

## Docs render — tracer slice

Provisioned per `CLAUDE.md` § "Worktree-isolated execution":

```
$ unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT
$ uv sync --extra dev --extra docs
```

Command:
```
$ uv run tox -e docs-html
```

Verbatim tail (from a build executed AFTER the bullet landed):
```
build succeeded, 3 warnings.
```

**Comparison to baseline.** The measured pre-existing baseline (`57-GREEN-TREE-EVIDENCE.md` §
"SC#3 — documentation builds", carried forward from Phase 56's close) is 3 warnings for
`docs-html`. This run's count — 3 — matches that baseline exactly. No new warning was
introduced by the PATH-01 bullet's MyST rendering through
`docs/source/changelog.rst`'s `.. include:: ../../CHANGELOG.md` with
`:parser: myst_parser.sphinx_`.
