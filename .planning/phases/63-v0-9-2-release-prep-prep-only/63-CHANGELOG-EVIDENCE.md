# Phase 63 — CHANGELOG and Version-Bump Evidence (SC#1, SC#2, REL-10)

## This plan's base SHA

```
$ git rev-parse HEAD
c31bb048bf5a92b7550bc2aa68efb114437533fa
```

## Pre-edit measurements

```
$ grep -c '^## \[' CHANGELOG.md
22
```

```
$ grep -c '^## \[Unreleased\]' CHANGELOG.md
1
```

```
$ grep -c '^\[[^]]\+\]: https' CHANGELOG.md
22
```

```
$ grep -c '^### Known Limitations' CHANGELOG.md
1
```

```
$ grep -c '^### Verified' CHANGELOG.md
9
```

```
$ tail -1 CHANGELOG.md
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.0...HEAD
```

```
$ sed -n '7p' pyproject.toml
version = "0.9.0"
```

```
$ sed -n '347p' README.md
**Status**: Stable (v0.9.0) - Production ready
```

```
$ sed -n '1466,1468p' uv.lock
name = "typsphinx"
version = "0.9.0"
source = { editable = "." }
```

## Version-literal lockstep (SC#1, Pattern 1)

```
$ uv lock
Resolved 89 packages in 912ms
Updated typsphinx v0.9.0 -> v0.9.2
```

```
$ uv sync --extra dev --locked
 - typsphinx==0.9.0 (from file:///…/agent-a29438298f7d544db)
 + typsphinx==0.9.2 (from file:///…/agent-a29438298f7d544db)
```

```
$ uv lock --check
Resolved 89 packages in 0.52ms
exit=0
```

```
$ uv run python -c 'import typsphinx; print(typsphinx.__version__)'
0.9.2
```

## The extractor, run and read (REL-10, D-20)

```
$ uv run python scripts/extract_changelog_section.py 0.9.2 > /tmp/63-extracted-t1.md
exit=0
$ wc -c /tmp/63-extracted-t1.md
3514
```

(Note: the bullet's IMG-08/09/10 citation was moved onto the bold lead's first line after an
initial draft placed it on the wrapped second line, which the automated verify's `grep -m1 | grep
-c IMG-08` check does not match a later line for. This byte length reflects the corrected,
committed text.)

D-20's three named greps, run against the final tree after the four-step edit:

```
$ grep -c '^## \[0\.9\.1\]' CHANGELOG.md
0
```

```
$ grep -c '^\[0\.9\.1\]:' CHANGELOG.md
0
```

```
$ grep -c 'Planned for Future Releases' /tmp/63-extracted-t1.md
0
```

No versioned heading and no tail link reference exist for the never-published version anywhere in
`CHANGELOG.md`, and the extracted 0.9.2 body carries zero occurrences of the scratch-block heading
text. Verbatim transcription of the extractor's full stdout is Task 3's consolidation work (see
"The extracted body, verbatim" below).

## Post-edit structural measurements

```
$ grep -c '^## \[' CHANGELOG.md
23
```

```
$ grep -n '^## \[' CHANGELOG.md | head -3
8:## [Unreleased]
17:## [0.9.2] - 2026-08-30
65:## [0.9.0] - 2026-08-17
```

```
$ grep -c '^\[[^]]\+\]: https' CHANGELOG.md
23
```

```
$ grep -c '0\.9\.1' CHANGELOG.md
0
```

```
$ tail -1 CHANGELOG.md
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.2...HEAD
```

```
$ uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml tests/test_readme_version_sync.py tests/test_preview_version_sync.py -q
5 passed in 0.05s
```

```
$ git status --porcelain typsphinx/ docs/
(empty)
```

No trim was made to any of the three promoted bullets — all three are carried verbatim from the
prior `## [Unreleased]` section, per D-04.

## Milestone-invariant sweep (D-06 bullets 1 and 2)

**Positive control — proving the `v0.9.0` anchor is reachable and real:**

```
$ git rev-list --count v0.9.0..HEAD
224
```

```
$ git diff --stat v0.9.0..HEAD -- typsphinx/
 typsphinx/builder.py           | 306 ++++++++++++++++++++++++++++++++++-------
 typsphinx/pathfmt.py           |  96 +++++++++++++
 typsphinx/template_registry.py |  25 +++-
 typsphinx/translator.py        |  33 ++++-
 typsphinx/writer.py            |   6 +-
 5 files changed, 408 insertions(+), 58 deletions(-)
```

Non-empty and matches the measurement recorded while this plan was written (5 files, 408
insertions, 58 deletions) — the anchor is reachable, so the three empty sweep results below are
genuine findings, not an artifact of an unreachable anchor.

**Measurement 1 — dependency arrays (`pyproject.toml`):**

```
$ git diff v0.9.0..HEAD -- pyproject.toml
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -4,7 +4,7 @@ build-backend = "setuptools.build_meta"

 [project]
 name = "typsphinx"
-version = "0.9.0"
+version = "0.9.2"
 description = "Sphinx extension for Typst output"
 readme = "README.md"
 requires-python = ">=3.12"
```

Exactly one added and one removed line, both the `version` assignment on line 7 — nothing inside
`[project.dependencies]` or `[project.optional-dependencies]`.

**Measurement 2 — lockfile (`uv.lock`):**

```
$ git diff v0.9.0..HEAD -- uv.lock
--- a/uv.lock
+++ b/uv.lock
@@ -1464,7 +1464,7 @@ wheels = [

 [[package]]
 name = "typsphinx"
-version = "0.9.0"
+version = "0.9.2"
 source = { editable = "." }
 dependencies = [
     { name = "docutils" },
```

Only the self-package `version` stanza changed; no dependency pin moves.

**Measurement 3 — bundled `@preview` package version strings:**

```
$ git diff v0.9.0..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ examples/ | grep -c '@preview'
0
```

```
$ grep -n '@preview' typsphinx/templates/base.typ
8:#import "@preview/codly:1.3.0": *
9:#import "@preview/codly-languages:0.1.10": *
14:#import "@preview/mitex:0.2.7": *
19:#import "@preview/gentle-clues:1.3.1": *
```

Zero diff lines mentioning `@preview`; the four current version strings are unchanged across this
milestone.

**Bullet-to-evidence mapping:**

- `### Verified` bullet 1 (zero new runtime or dev dependencies) is backed by Measurements 1 and 2
  above, in this section.
- `### Verified` bullet 2 (the four `@preview` version strings unchanged) is backed by Measurement
  3 above, in this section.
- `### Verified` bullet 3 (the TEST-05 gate result — 16 previously-failing plus 9
  must-keep-passing image shapes, 18/18 masters compiling) is backed by
  `.planning/phases/62-the-visit-image-separator-fix-and-its-real-compile-gate/62-VERIFICATION.md`
  § "Observable Truths", row 1 and the "Behavioral Spot-Checks" table's first row.

The full-corpus Sphinx `doc/` typstpdf re-run sentence that nine prior `### Verified` entries
carried is deliberately NOT copied here — this milestone did not run that corpus. This is the
break in that streak D-06 requires; see `grep -c 'full-corpus'` returning 0 inside the 0.9.2
section, verified above.

## RELEASE_VERSIONS proof (D-11), run with the docs extra

```
$ uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v
...
tests/test_changelog_page_gate.py::TestPublishedChangelogPageDelegates::test_page_delegates_to_changelog_md PASSED [ 16%]
tests/test_changelog_page_gate.py::TestPublishedChangelogPageDelegates::test_page_carries_no_hand_maintained_release_history PASSED [ 33%]
tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_rendered_page_carries_every_release PASSED [ 50%]
tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_rendered_page_has_one_changelog_heading PASSED [ 66%]
tests/test_changelog_page_gate.py::TestChangelogPageContentCoverage::test_build_emits_no_changelog_warnings PASSED [ 83%]
tests/test_changelog_page_gate.py::TestChangelogIncludeCompilesToPdf::test_included_changelog_reaches_the_pdf PASSED [100%]

============================== 6 passed in 4.75s ===============================
```

6 tests PASSED, 0 SKIPPED. This evidence took the local docs-extra run (not the dispatched CI docs
job) — the worktree was provisioned with `--extra dev` only, so `--extra docs` was added
explicitly for this invocation so that `myst_parser` is importable and the two content-coverage
classes (`TestChangelogPageContentCoverage`) actually execute rather than skip.

## The extracted body, verbatim

```
$ uv run python scripts/extract_changelog_section.py 0.9.2 > /tmp/63-e.md
exit=0
$ wc -c /tmp/63-e.md
4087
```

Complete stdout, transcribed verbatim:

```markdown
This release curates the Windows-shaped path-handling hardening accumulated since 0.9.0 — an
output-directory escape check, an absolute image URI that aborted the PDF build, and diagnostic
message quoting — together with a separate compile-blocking defect in the image visitor. A project
built with the published 0.9.0 release produced no PDF for any master document when an image was
not first in its container, and 0.9.0 users should upgrade to this release. The runtime changes are
confined to `typsphinx/translator.py`, with no other file under `typsphinx/` touched. Zero new
runtime dependencies; the bundled `@preview` version-sync surface is untouched.

### Fixed

- **An image not first in its container no longer aborts the `typstpdf` compile (IMG-08, IMG-09,
  IMG-10).** Whenever an image followed other content in the same container — mid-sentence, in a
  list item, a table cell, a definition-list body, an admonition, a footnote, a field-list body, a
  section title, or a figure's legend — the emitted Typst lacked a separator from the preceding
  expression, so Typst refused the file with `expected semicolon or line break` and the `typstpdf`
  builder raised an extension error, producing no PDF for any master document in the project,
  including masters that contained no image at all. `visit_image()` now joins the translator's
  existing separator discipline, so every one of those containers compiles.

- **A Windows-shaped `typst_documents` target that reaches outside the output directory is now
  refused on the normalized path, matching its sibling image-URI check (PATH-01).** The
  `typst_documents` escape predicate now applies its absolute-path and drive-qualified checks to
  the same backslash-normalized string its sibling image-URI predicate already used, rather than
  to the raw stem. Neither of the predicate's two real call sites can currently reach the gap this
  closes — both normalize or otherwise guarantee a safe value before calling it — so this is
  contract hardening for a future caller, not the repair of a defect any user was hitting.

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

### Verified

- Zero new runtime or dev dependencies across this milestone's diff (`v0.9.0..HEAD`) — the only
  change to `pyproject.toml` and `uv.lock` is the version literal itself.
- The four bundled `@preview` package version strings unchanged across all four sync surfaces
  (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`).
- The `visit_image()` separator fix is bound by a real `typst.compile()` gate covering the 16
  previously-failing and 9 must-keep-passing image shapes (TEST-05), with 18 of 18 master
  documents compiling.
```

## Byte-for-byte identity, with its positive control

**0.9.2 (the section under test):**

```
$ uv run python scripts/extract_changelog_section.py 0.9.2 > /tmp/63-e.md
$ awk '/^## \[0\.9\.2\]/{f=1;next} f&&/^## \[/{exit} f' CHANGELOG.md | sed -e '/./,$!d' | tac | sed -e '/./,$!d' | tac > /tmp/63-s.md
$ diff /tmp/63-e.md /tmp/63-s.md
(empty)
$ echo $?
0
$ wc -c /tmp/63-e.md /tmp/63-s.md
4087 /tmp/63-e.md
4087 /tmp/63-s.md
```

**0.6.5 (the positive control — an existing, previously-published section):**

```
$ uv run python scripts/extract_changelog_section.py 0.6.5 > /tmp/63-e65.md
$ awk '/^## \[0\.6\.5\]/{f=1;next} f&&/^## \[/{exit} f' CHANGELOG.md | sed -e '/./,$!d' | tac | sed -e '/./,$!d' | tac > /tmp/63-s65.md
$ diff /tmp/63-e65.md /tmp/63-s65.md
(empty)
$ echo $?
0
$ wc -c /tmp/63-e65.md /tmp/63-s65.md
1299 /tmp/63-e65.md
1299 /tmp/63-s65.md
```

The 0.6.5 control reproduces the exact 1299-byte-both-sides result measured while this plan was
written, confirming the comparison pipeline is sound (an empty diff means agreement, not a broken
pipeline) — so the 0.9.2 empty diff above can be trusted.

## Fence assertions over the final tree

```
$ grep -c '^## \[' CHANGELOG.md
23
```

```
$ grep -c '^\[[^]]\+\]: https' CHANGELOG.md
23
```

```
$ grep -c '^### Known Limitations' CHANGELOG.md
1
```

```
$ grep -c '^### Verified' CHANGELOG.md
10
```

```
$ grep -c '0\.9\.1' CHANGELOG.md
0
```

```
$ tail -1 CHANGELOG.md
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.2...HEAD
```

```
$ sed -n '7p' pyproject.toml
version = "0.9.2"
```

```
$ sed -n '347p' README.md
**Status**: Stable (v0.9.2) - Production ready
```

```
$ git log --format=%H -1 -- pyproject.toml
10d9d95d57c4c8154ddbd49463d6a904235aef72
$ git show --name-only --format= 10d9d95d57c4c8154ddbd49463d6a904235aef72
CHANGELOG.md
README.md
pyproject.toml
uv.lock
```

Exactly `CHANGELOG.md`, `README.md`, `pyproject.toml` and `uv.lock` — proving SC#1's
one-commit-four-files requirement rather than asserting it.

## REL-09 coverage declaration (D-16)

`63-01-SUMMARY.md`'s frontmatter declares `requirements-completed: []` for REL-09. This plan cites
REL-09 for coverage only, closes nothing, and does not touch its checkbox — REL-09 closes at
`/gsd-complete-milestone`, not here.

## Post-correction re-run (gap closure, SC#2)

**Timestamp:** 2026-08-30T13:20:55Z
**Resolving commit:** `2a0bc3bef1770a373fa48d122ba35a4d1de2417b` (`2a0bc3be`)

### The contradiction, and its resolution

This same file carries two sections that contradicted each other. § "Milestone-invariant sweep
(D-06 bullets 1 and 2)" above transcribes `git diff --stat v0.9.0..HEAD -- typsphinx/` showing
**five** files changed (`builder.py`, `pathfmt.py`, `template_registry.py`, `translator.py`,
`writer.py`). § "The extracted body, verbatim" above transcribes the `## [0.9.2]` intro paragraph
as it stood before this closure, which asserted "The runtime changes are confined to
`typsphinx/translator.py`, with no other file under `typsphinx/` touched" — a blanket claim that
sentence directly falsified. Both transcriptions are left exactly as they were recorded; neither is
edited by this section. `63-REVIEW.md` CR-01 (Critical) and `63-VERIFICATION.md` SC#2 both caught
this independently.

**The contradiction is RESOLVED as of commit `2a0bc3be`.** The blanket sentence has been deleted
from the `## [0.9.2]` intro paragraph, and a narrower, measured claim now sits in the first
`### Fixed` bullet (the one citing IMG-08, IMG-09, IMG-10) — the one bullet whose fix genuinely is
confined to `typsphinx/translator.py`. The two sections above are no longer in tension with the
text currently on disk.

### The replacement claim's own proof

Scoped `--stat` over the phase-62 commit range, re-run in this closure:

```
$ git diff --stat e3399825..dd385436 -- typsphinx/
 typsphinx/translator.py | 23 +++++++++++++++++++++++
 1 file changed, 23 insertions(+)
```

Two-commit log over the same range:

```
$ git log --oneline e3399825..dd385436 -- typsphinx/
1adad07f docs(62): document depart_image()'s sibling-boundary bookkeeping (WR-02)
8430ca62 feat(62-01): join visit_image() to the separator triad, add tracer gate
```

Each commit's own single-file stat:

```
$ git show --stat --format= 8430ca62 -- typsphinx/
 typsphinx/translator.py | 9 +++++++++
 1 file changed, 9 insertions(+)
```

```
$ git show --stat --format= 1adad07f -- typsphinx/
 typsphinx/translator.py | 14 ++++++++++++++
 1 file changed, 14 insertions(+)
```

9 + 14 = 23, matching the scoped `--stat` total exactly.

**The milestone-wide figure, recorded alongside it, and why the two differ:**

```
$ git diff --stat v0.9.0..HEAD -- typsphinx/translator.py
 typsphinx/translator.py | 33 +++++++++++++++++++++++++++++++--
 1 file changed, 31 insertions(+), 2 deletions(-)
```

```
$ git log --oneline v0.9.0..HEAD -- typsphinx/translator.py
1adad07f docs(62): document depart_image()'s sibling-boundary bookkeeping (WR-02)
8430ca62 feat(62-01): join visit_image() to the separator triad, add tracer gate
756b9fad feat(59-03): route adjusted image URI through escape_typst_string()
```

```
$ git show --stat 756b9fad -- typsphinx/translator.py
 typsphinx/translator.py | 10 ++++++++--
 1 file changed, 8 insertions(+), 2 deletions(-)
```

The milestone-wide diff (31 insertions, 2 deletions) is larger than the phase-62 range's 23
insertions because commit `756b9fad` (a different fix family, IMG-04..07's escape routing) also
touched `translator.py`: 23 + 8 = 31 insertions, and the 2 deletions are entirely `756b9fad`'s.
The IMG-08/IMG-09/IMG-10 bullet's replacement claim scopes itself to the phase-62 range only, so
its narrower figure (23 insertions, one file, two commits) is visibly deliberate — it is not a
second undermeasurement of the milestone-wide figure.

### SC#2's structural set, re-run against the corrected text

Extractor exit status and stdout size, from a run executed in this closure:

```
$ uv run python scripts/extract_changelog_section.py 0.9.2 > /tmp/63g-e.md
exit=0
$ wc -c /tmp/63g-e.md
4083 /tmp/63g-e.md
```

4083 is a **byte** count (`wc -c`, not `wc -m`). The `## [0.9.2]` section carries 9 U+2014 em
dashes, each 3 bytes in UTF-8; a character count would read 18 bytes lower than this figure, which
is why the byte-vs-character distinction matters for any future byte-identity comparison against
the published GitHub Release body.

D-20's three named greps, re-run against the corrected tree:

```
$ grep -c '^## \[0\.9\.1\]' CHANGELOG.md
0
$ grep -c '^\[0\.9\.1\]:' CHANGELOG.md
0
$ grep -c 'Planned for Future Releases' /tmp/63g-e.md
0
```

Byte-identity `diff`, with the `## [0.6.5]` section as positive control, both sizes recorded:

```
$ awk '/^## \[0\.9\.2\]/{f=1;next} f&&/^## \[/{exit} f' CHANGELOG.md \
    | sed -e '/./,$!d' | tac | sed -e '/./,$!d' | tac > /tmp/63g-s.md
$ diff -q /tmp/63g-e.md /tmp/63g-s.md
(empty; no output)
$ wc -c /tmp/63g-e.md /tmp/63g-s.md
4083 /tmp/63g-e.md
4083 /tmp/63g-s.md
8166 total
```

```
$ uv run python scripts/extract_changelog_section.py 0.6.5 > /tmp/63g-e65.md
$ awk '/^## \[0\.6\.5\]/{f=1;next} f&&/^## \[/{exit} f' CHANGELOG.md \
    | sed -e '/./,$!d' | tac | sed -e '/./,$!d' | tac > /tmp/63g-s65.md
$ diff -q /tmp/63g-e65.md /tmp/63g-s65.md
(empty; no output)
$ wc -c /tmp/63g-e65.md /tmp/63g-s65.md
1299 /tmp/63g-e65.md
1299 /tmp/63g-s65.md
2598 total
```

Both comparisons are empty `diff`s; the 0.6.5 positive control reproduces the same 1299-byte
both-sides result recorded earlier in this file, confirming the pipeline is sound rather than
vacuously matching.

Whole-file heading count, and absence of any heading or tail link for the never-published version:

```
$ grep -c '^## \[' CHANGELOG.md
23
$ grep -n '^## \[' CHANGELOG.md | head -3
8:## [Unreleased]
17:## [0.9.2] - 2026-08-30
74:## [0.9.0] - 2026-08-17
$ grep -c '0\.9\.1' CHANGELOG.md
0
$ grep -c '^## \[0\.9\.1\]' CHANGELOG.md
0
$ grep -c '^\[0\.9\.1\]:' CHANGELOG.md
0
```

Tail block's unreleased compare base:

```
$ tail -1 CHANGELOG.md
[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.2...HEAD
```

### The corrected body, transcribed verbatim

```markdown
This release curates the Windows-shaped path-handling hardening accumulated since 0.9.0 — an
output-directory escape check, an absolute image URI that aborted the PDF build, and diagnostic
message quoting — together with a separate compile-blocking defect in the image visitor. A project
built with the published 0.9.0 release produced no PDF for any master document when an image was
not first in its container, and 0.9.0 users should upgrade to this release. Zero new runtime
dependencies; the bundled `@preview` version-sync surface is untouched.

### Fixed

- **An image not first in its container no longer aborts the `typstpdf` compile (IMG-08, IMG-09,
  IMG-10).** Whenever an image followed other content in the same container — mid-sentence, in a
  list item, a table cell, a definition-list body, an admonition, a footnote, a field-list body, a
  section title, or a figure's legend — the emitted Typst lacked a separator from the preceding
  expression, so Typst refused the file with `expected semicolon or line break` and the `typstpdf`
  builder raised an extension error, producing no PDF for any master document in the project,
  including masters that contained no image at all. `visit_image()` now joins the translator's
  existing separator discipline, so every one of those containers compiles. This fix is confined
  to `typsphinx/translator.py`; no other file under `typsphinx/` was touched for it.

- **A Windows-shaped `typst_documents` target that reaches outside the output directory is now
  refused on the normalized path, matching its sibling image-URI check (PATH-01).** The
  `typst_documents` escape predicate now applies its absolute-path and drive-qualified checks to
  the same backslash-normalized string its sibling image-URI predicate already used, rather than
  to the raw stem. Neither of the predicate's two real call sites can currently reach the gap this
  closes — both normalize or otherwise guarantee a safe value before calling it — so this is
  contract hardening for a future caller, not the repair of a defect any user was hitting.

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

### Verified

- Zero new runtime or dev dependencies across this milestone's diff (`v0.9.0..HEAD`) — the only
  change to `pyproject.toml` and `uv.lock` is the version literal itself.
- The four bundled `@preview` package version strings unchanged across all four sync surfaces
  (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`).
- The `visit_image()` separator fix is bound by a real `typst.compile()` gate covering the 16
  previously-failing and 9 must-keep-passing image shapes (TEST-05), with 18 of 18 master
  documents compiling.
```

This is byte-identical to the on-disk `## [0.9.2]` section (see the `diff -q` above) and is the
exact text `/gsd-complete-milestone` will publish as the GitHub Release body and that the Read the
Docs changelog page will render via `docs/source/changelog.rst`'s MyST include.

**Every remaining checkable claim in this body was read, not skimmed.** The 255-UTF-8-byte
relocation bound (IMG-04..07 bullet) is confirmed present in `typsphinx/builder.py`
(`MAX_PATH_COMPONENT_BYTES = 255`, `builder.py:49`). The TEST-05 gate result (16
previously-failing / 9 must-keep-passing / 18-of-18 masters compiling) is independently verified
in `62-VERIFICATION.md` § "Observable Truths", row 1. The zero-new-dependency and
`@preview`-version-strings claims in the `### Verified` bullets are backed by this same file's
§ "Milestone-invariant sweep" Measurements 1–3, re-run above. No remaining checkable claim in the
body was found that could not be checked; there is no open question to record.

### Adjacency, ordering and encoding observations

```
$ sed -n '17,26p' CHANGELOG.md
## [0.9.2] - 2026-08-30

This release curates the Windows-shaped path-handling hardening accumulated since 0.9.0 — an
output-directory escape check, an absolute image URI that aborted the PDF build, and diagnostic
message quoting — together with a separate compile-blocking defect in the image visitor. A project
built with the published 0.9.0 release produced no PDF for any master document when an image was
not first in its container, and 0.9.0 users should upgrade to this release. Zero new runtime
dependencies; the bundled `@preview` version-sync surface is untouched.

### Fixed
```

The intro remains exactly one paragraph, separated from `### Fixed` by exactly one blank line
(line 25), with no orphaned short line and no double space at the sentence join (`grep -n '  '`
over the paragraph region returns no hits). The three leading `^## [` headings are unchanged in
order (`[Unreleased]`, `[0.9.2]`, `[0.9.0]`). The section's em-dash count is unchanged at 9
(`grep -o '—' | wc -l` over the `## [0.9.2]` region).

### The verification report's gaps, discharged

`63-VERIFICATION.md`'s `gaps:` block records exactly two `missing:` items for SC#2, quoted
verbatim:

1. "Correct or remove the false file-confinement sentence in CHANGELOG.md's ## [0.9.2] intro
   paragraph, per 63-REVIEW.md CR-01's suggested fix (scope the claim to the one fix it's true
   for, or drop the blanket claim entirely)."

   **Discharged by:** the two edits in commit `2a0bc3be` — the blanket sentence is deleted from
   the intro paragraph (§ "Adjacency, ordering and encoding observations" above shows the
   corrected paragraph in full) and a scoped, measured version now sits in the IMG-08/IMG-09/
   IMG-10 bullet, proven true by the `git diff --stat e3399825..dd385436` re-run recorded above.

2. "Re-run the extractor and re-verify SC#2's byte-identity/structural checks against the
   corrected text before this is handed to /gsd-complete-milestone, since the GitHub Release body
   and RTD changelog page publish this text verbatim."

   **Discharged by:** § "SC#2's structural set, re-run against the corrected text" above — the
   extractor was re-run against the corrected `CHANGELOG.md`, its exit status and byte-count
   captured, its stdout proven byte-identical to the on-disk section with the `## [0.6.5]` section
   as positive control, and every one of D-20's structural greps re-verified at 0.

A reader can re-derive the closure from the measurements above without taking this paragraph's
word for it.
