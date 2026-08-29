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

## The remaining two defect families (IMG and MSG)

Authored in the same `### Fixed` subsection, after the PATH-01 bullet and before
`### Planned for Future Releases`, in the order CONTEXT specific idea #2 names them:

```markdown
- **A Windows-shaped absolute image URI now compiles instead of aborting the PDF build (IMG-04,
  IMG-05, IMG-06, IMG-07).** The relocation key built for a relocated image is now derived from a
  forward-slash-normalized basename, so no backslash or drive letter from the original URI
  survives into the emitted `image(...)` path value, and that value is now escaped as a Typst
  syntax literal before it is interpolated. The two halves are coupled — neither alone closes the
  compile-time failure, because Typst refuses a backslash in an `image()` path by value, not by
  syntax. The relocation basename is also bounded to 255 UTF-8 bytes, with the collision-avoidance
  digest kept whole so two images that would otherwise collide on a shared filename still resolve
  to distinct files.

- **A path named in a diagnostic message now reads exactly as it appears on disk (MSG-02, MSG-03,
  MSG-04, MSG-05).** Path-valued messages across the extension no longer double a Windows
  separator, and the quoting that wraps a path no longer closes early on a path containing a
  quote character — a POSIX path with an apostrophe in it (for example, a directory named
  `O'Brien`) was affected by the same defect family as a Windows-shaped path, so this is not a
  Windows-exclusive fix. Identifier-valued messages (registry keys, docnames) are unaffected;
  only path-valued messages route through the new quoting.
```

**Accuracy basis:** `.planning/phases/59-.../59-WINDOWS-URI-EVIDENCE.md` records IMG-04's
forward-slash normalization of the relocation-key basename, IMG-05's `escape_typst_string()`
call on the emitted `image()` path value, IMG-06's 255-UTF-8-byte bound with the digest kept
whole, and IMG-07's real `typst.compile()` gate proving the coupling (escaping the backslash
alone still fails with `TypstError: path must not contain a backslash`).
`.planning/phases/60-.../60-PATH-QUOTING-EVIDENCE.md` and `60-CONTEXT.md` § D-01 AMENDED record
that `quote_path()` closes an embedded apostrophe by SQL-style doubling rather than
backslash-escaping — the measured basis for naming a POSIX path with an apostrophe (e.g.
`O'Brien`) as an affected case, per CONTEXT specific idea #1's binding framing constraint.

**Exercised discretion (CONTEXT § "Claude's Discretion"):**
- **MSG-01 and the new internal module `typsphinx/pathfmt.py` do NOT earn their own bullets.**
  MSG-01 is test-side-only decoupling that produced no user-visible behavior change by
  construction (`58-REPR-CENSUS.md`), and `pathfmt.py` is an internal leaf module with zero
  `typsphinx`-internal imports — this project's CHANGELOG has historically described
  user-visible behavior, not internal module structure, so neither is named.
- **No `### Verified` subsection is authored this phase.** Per the discretion item and the
  cheaper-default guidance, its authorship is deliberately deferred to the v0.9.2 release-prep
  phase, which will write it against the whole 0.9.2 diff rather than against this
  prep-only phase's partial slice.

`### Planned for Future Releases` and its five entries are left exactly as they were —
untouched by this phase.

## Pure-addition proof

Command:
```
$ git diff 5e28fa9dac8576f1f1665560eb5c4ccbd2e13b41 -- CHANGELOG.md
```

Verbatim output:
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index ae518433..76aff137 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -7,6 +7,34 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 ## [Unreleased]
 
+### Fixed
+
+- **A Windows-shaped `typst_documents` target that reaches outside the output directory is now
+  refused on the normalized path, matching its sibling image-URI check (PATH-01).** The
+  `typst_documents` escape predicate now applies its absolute-path and drive-qualified checks to
+  the same backslash-normalized string its sibling image-URI predicate already used, rather than
+  to the raw stem. Neither of the predicate's two real call sites can currently reach the gap this
+  closes — both normalize or otherwise guarantee a safe value before calling it — so this is
+  contract hardening for a future caller, not the repair of a defect any user was hitting.
+
+- **A Windows-shaped absolute image URI now compiles instead of aborting the PDF build (IMG-04,
+  IMG-05, IMG-06, IMG-07).** The relocation key built for a relocated image is now derived from a
+  forward-slash-normalized basename, so no backslash or drive letter from the original URI
+  survives into the emitted `image(...)` path value, and that value is now escaped as a Typst
+  syntax literal before it is interpolated. The two halves are coupled — neither alone closes the
+  compile-time failure, because Typst refuses a backslash in an `image()` path by value, not by
+  syntax. The relocation basename is also bounded to 255 UTF-8 bytes, with the collision-avoidance
+  digest kept whole so two images that would otherwise collide on a shared filename still resolve
+  to distinct files.
+
+- **A path named in a diagnostic message now reads exactly as it appears on disk (MSG-02, MSG-03,
+  MSG-04, MSG-05).** Path-valued messages across the extension no longer double a Windows
+  separator, and the quoting that wraps a path no longer closes early on a path containing a
+  quote character — a POSIX path with an apostrophe in it (for example, a directory named
+  `O'Brien`) was affected by the same defect family as a Windows-shaped path, so this is not a
+  Windows-exclusive fix. Identifier-valued messages (registry keys, docnames) are unaffected;
+  only path-valued messages route through the new quoting.
+
 ### Planned for Future Releases
 - BibTeX/bibliography support
 - Glossary generation
```

Zero lines in this diff begin with a single `-` followed by a non-`-` character — no source
line was removed. `### Planned for Future Releases` and every historical release section
(`## [0.9.0]` through `## [0.1.0b1]`) survive byte-identical, and the tail link-reference block
is untouched.

## Fence assertions over CHANGELOG.md and the version literals

Every assertion below is a command plus its output, not a claim.

```
$ grep -cE '^## \[' CHANGELOG.md
22

$ grep -cE '^### Known Limitations' CHANGELOG.md
1

$ grep -cE '^\[[^]]+\]: https' CHANGELOG.md
22

$ grep -c '0\.9\.1' CHANGELOG.md
0

$ tail -1 CHANGELOG.md
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.0...HEAD

$ sed -n '7p' pyproject.toml
version = "0.9.0"

$ sed -n '347p' README.md
**Status**: Stable (v0.9.0) - Production ready

$ git diff --name-only 5e28fa9dac8576f1f1665560eb5c4ccbd2e13b41 -- tests/test_changelog_page_gate.py
(empty)

$ git status --porcelain tests/ typsphinx/ docs/
(empty)
```

Every value above is byte-identical to the pre-edit measurement recorded at the top of this
file, except the intentional CHANGELOG.md addition. `RELEASE_VERSIONS` in
`tests/test_changelog_page_gate.py` is unmodified and still ends at the `"0.9.0"` entry — no
diff at all was produced against that file. No `typsphinx/` file, no `tests/` file, and no
`docs/` source page changed.

## Docs render — full comparison against the 3 / 5 baseline

Both builds below were run on the tree carrying all three defect-family bullets, after a clean
`rm -rf docs/_build` to guarantee a full (non-incremental) rebuild — an incremental rebuild
would only reprocess pages invalidated by the CHANGELOG.md edit and could under-report warnings
carried by unrelated pages (e.g. the pre-existing `visit_toctree` docstring warnings), producing
a count that looks clean without actually re-proving the baseline.

Command:
```
$ uv run tox -e docs-html
```

Verbatim tail:
```
build succeeded, 3 warnings.
```

Command:
```
$ uv run tox -e docs-pdf
```

Verbatim tail:
```
Generated PDF: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae2388e7b1825f8c4/docs/_build/pdf/typsphinx.pdf
build succeeded, 5 warnings.
```

**Comparison to baseline.** The measured pre-existing baseline (`57-GREEN-TREE-EVIDENCE.md` §
"SC#3 — documentation builds") is 3 warnings for `docs-html` and 5 warnings for `docs-pdf`. Both
counts from this run — 3 and 5 — match that baseline exactly. No new warning was introduced by
any of the three authored bullets across either builder.
