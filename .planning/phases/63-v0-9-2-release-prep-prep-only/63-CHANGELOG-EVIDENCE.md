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
