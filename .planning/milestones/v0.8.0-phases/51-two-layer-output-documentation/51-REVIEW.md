---
phase: 51-two-layer-output-documentation
reviewed: 2026-08-15T00:00:00Z
depth: standard
files_reviewed: 20
files_reviewed_list:
  - README.md
  - docs/source/changelog.rst
  - docs/source/user_guide/builders.rst
  - docs/source/user_guide/configuration.rst
  - docs/source/user_guide/index.rst
  - docs/source/user_guide/output_layout.rst
  - docs/source/user_guide/templates.rst
  - examples/advanced/README.md
  - examples/basic/README.md
  - tests/fixtures/output_layout_bare_target_gate/conf.py
  - tests/fixtures/output_layout_bare_target_gate/index.rst
  - tests/fixtures/output_layout_explicit_path_gate/conf.py
  - tests/fixtures/output_layout_explicit_path_gate/index.rst
  - tests/fixtures/output_layout_refused_absolute_gate/conf.py
  - tests/fixtures/output_layout_refused_absolute_gate/index.rst
  - tests/fixtures/output_layout_refused_drive_gate/conf.py
  - tests/fixtures/output_layout_refused_drive_gate/index.rst
  - tests/fixtures/output_layout_refused_parent_gate/conf.py
  - tests/fixtures/output_layout_refused_parent_gate/index.rst
  - tests/test_no_stale_github_io_links.py
  - tests/test_output_layout_docs_gate.py
findings:
  critical: 1
  warning: 1
  info: 0
  total: 2
status: issues_found
---

# Phase 51: Code Review Report

**Reviewed:** 2026-08-15T00:00:00Z
**Depth:** standard
**Files Reviewed:** 20
**Status:** issues_found

## Summary

Phase 51 is a documentation-only phase (confirmed: `git diff 30c8b289..HEAD -- typsphinx/` is
empty). Six prose pages, two READMEs, one new pytest gate module, and five new build fixtures
were reviewed against the authoritative, unchanged source (`typsphinx/builder.py`,
`typsphinx/writer.py`, `typsphinx/translator.py`, `typsphinx/template_engine.py`).

Almost every specific, checkable claim verifies correctly against the code: the wrapper-publishes
state / content-file-reads-state mechanism, the `render_include_guard()`/`render_include_edge_state()`
literal output, the `_resolve_target_stem()` refusal/fallback behaviour for parent-traversal,
absolute, and drive-qualified targets (including the exact `logger.warning` text), the
`_validate_output_path_collisions()` aggregated `ExtensionError` message shape, the
`_default_typst_documents()`/`make_filename_from_project()` derivation, and the
`derive_typst_lang()` derivation rule are all quoted or paraphrased accurately, and the eight
README quick-links (including the new Output Layout entry) resolve to real, existing doc pages in
the right order.

One systemic factual defect was found: a whole-build file **count**/file **list** claim that
undercounts by omitting `_template.typ`, repeated across four of the six changed pages and
directly contradicted both by the phase's own real-build fixture test and by a later section of
the very page making the claim. One test-quality defect was found in the new gate module: a
substring assertion intended to bind a specific published number to a real build is satisfiable by
unrelated prose already present on the page, defeating its own stated purpose.

## Critical Issues

### CR-01: Whole-build ".typ file count/list" claims omit `_template.typ`, contradicting the phase's own fixture test and a later section of the same page

**File:** `docs/source/user_guide/output_layout.rst:31-34`
**File:** `docs/source/user_guide/builders.rst:122-129`
**File:** `examples/basic/README.md:36-38`
**File:** `examples/advanced/README.md:59-63`

**Issue:**

Four places introduced or rewritten by this phase state an exact, named list of every `.typ` file
a described build writes, and every one of them omits the reserved `_template.typ` infrastructure
file that `TypstBuilder._write_template_file()` unconditionally writes on every non-`typst_package`
route (all four configs shown use the bundled default template or a custom `typst_template`, never
a package-alone route, so `_template.typ` is written in every one of these examples).

1. `output_layout.rst:31-34` (new in this phase):

   > "This configuration writes two files: ``manual.typ`` ... and ``index.typ`` ..."

   for `typst_documents = [("index", "manual", "Title", "Author", "typst")]`. This is the *exact*
   configuration the phase's own new fixture `tests/fixtures/output_layout_bare_target_gate/`
   builds, and the phase's own new test
   `TestOutputLayoutBuildFileSets.test_bare_target_emits_wrapper_and_content` in
   `tests/test_output_layout_docs_gate.py:114-154` asserts **three** files exist after this exact
   build: `manual.typ`, `index.typ`, **and** `_template.typ`. The prose's own test suite disproves
   the prose's own claim.

   This also self-contradicts the same page's later "Documents Shared by Several Masters" section
   (`output_layout.rst:153-157`), which states the correct, complete counting rule: "a build writes
   one wrapper per ``typst_documents`` entry, one content file for every document in the project,
   **and the reserved** ``_template.typ``" — and uses that rule to correctly arrive at "ten" files
   for the three-master fixture. The bare-target example two paragraphs earlier does not apply this
   same rule to itself.

2. `builders.rst:122-129` (edited in this phase): for a two-entry example
   (`typst_documents = [("index", "main", ...), ("api", "api-ref", ...)]`), states "the builders
   emit four ``.typ`` files: wrappers ``main.typ`` and ``api-ref.typ``, plus content files
   ``index.typ`` and ``api.typ``". A real build of that configuration (project with exactly those
   two documents) writes **five** `.typ` files — the four named plus `_template.typ`.

3. `examples/basic/README.md:36-38` (rewritten in this phase): "This will create two files in
   ``_build/typst/``: ``basic-example.typ`` ... and ``index.typ`` ...". `examples/basic/conf.py`
   uses the bundled default template (no `typst_package`), so a real build of this project writes
   **three** files: `basic-example.typ`, `index.typ`, and `_template.typ`.

4. `examples/advanced/README.md:59-63` (rewritten in this phase): lists exactly four files
   (`advanced-example.typ`, `index.typ`, `chapter1.typ`, `chapter2.typ`). `examples/advanced/conf.py`
   sets `typst_template = "_templates/custom.typ"`, so `_write_template_file()` writes
   `_template.typ` regardless (the package-alone skip only applies when `typst_package` is set with
   no `typst_template`). A real build of this project writes **five** files, not four.

This is precisely the class of defect DOC-14 exists to eliminate: a statement about the emitted
file set that does not match what the builder actually writes to disk, in four of the six pages
this phase edited, using an example each page's own conf.py/fixture actually builds.

**Fix:** Add `_template.typ` to each list/count. For example, `output_layout.rst:31` could read:

```rst
This configuration writes three files: ``manual.typ`` at the output directory's root -- the
wrapper for the ``index`` docname's target ``manual`` -- ``index.typ``, also at the output
directory's root -- the content file for the ``index`` docname itself -- and the shared
``_template.typ`` infrastructure file every build writes once.
```

Apply the analogous correction to `builders.rst:124-126` ("five ``.typ`` files"), and to
the file-listing bullets in both example READMEs (add a ``_template.typ`` line/mention to each).

## Warnings

### WR-01: `test_page_states_the_shared_child_composition`'s "ten" assertion is a vacuous-pass substring check

**File:** `tests/test_output_layout_docs_gate.py:445-457`

**Issue:**

```python
def test_page_states_the_shared_child_composition(self):
    """docs/source/user_guide/output_layout.rst's shared-child section
    heading is present and the section publishes the literal 'ten'
    file-count claim (D-09, SC#3)."""
    text = OUTPUT_LAYOUT_RST_PATH.read_text(encoding="utf-8")
    assert "Documents Shared by Several Masters" in text, (...)
    assert "ten" in text, (
        "docs/source/user_guide/output_layout.rst does not publish the "
        "literal 'ten' file-count claim for the three-master example."
    )
```

The `"ten" in text` check is a bare substring test, and `"ten"` is a substring of ordinary English
words that appear unrelated to the file-count claim and occur many times elsewhere on the same
page — e.g. `"written"` (`wri-tten`) and `"content"` (`con-ten-t`) both contain the literal
substring `"ten"`. Both words occur repeatedly throughout `output_layout.rst` independent of the
three-master "ten `.typ` files" sentence (e.g. `"content file"` appears at lines 16, 18-22, 34, 45,
50, 81-82, 119-120, 131, 155; `"written"` appears at lines 13, 57, 120, 138). Verified directly:

```python
>>> "ten" in "written"
True
>>> "ten" in "content"
True
```

This means the assertion would still pass even if the actual "A three-master project over six
documents therefore writes ten ``.typ`` files" sentence at `output_layout.rst:157` were deleted
outright or the number silently changed to something that still contains the substring `"ten"`
elsewhere on the page (e.g. via any nearby occurrence of "written"/"content"/"often"/"listener"),
because the page will always contain "written" and "content" regardless. The docstring's stated
intent — binding the published "ten" file-count claim to reality — is not actually enforced by
this assertion; only the section-heading check on the preceding line does real binding work here.

This is exactly the "vacuous-pass risk" this gate module exists to avoid (the module's own
docstring states its purpose is to fail "whenever the docs and a real ``-b typst`` build diverge
again" with no skip). As written, a regression that removes or wrongs the "ten" claim specifically
would not be caught by this test.

**Fix:** Assert a more specific fragment that can only match the actual claim, e.g.:

```python
assert "writes ten" in text, (
    "docs/source/user_guide/output_layout.rst does not publish the "
    "literal 'writes ten .typ files' claim for the three-master example."
)
```

or better, derive the expected count from the same fixture
`TestOutputLayoutBuildFileSets.test_three_master_project_emits_ten_typ_files` already measures
(`len(expected_typ_names)`) and assert the spelled-out word for that count appears, so a future
change to the fixture's file count and a stale "ten" in prose are both caught mechanically instead
of by two independently-hardcoded literals.

---

_Reviewed: 2026-08-15T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
