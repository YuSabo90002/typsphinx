# Phase 53: SC#2 Pre-Change Byte-Identity Evidence

**Purpose:** Per D-12, this is a one-off evidence artifact proving SC#2's zero-edit-equivalence
claim by identity, not a new golden-file pytest gate. It records the pre-change state of all
four existing `typst_template` / `typst_package` / `typst_template_function` / nothing-set
configuration shapes, plus TPL-04's four-element-vs-fifth-element equivalence, BEFORE any
Phase 53 code lands.

**This file is named `53-RED-EVIDENCE.md`, not `53-VERIFICATION.md`** — the latter is reserved
by `gsd-verifier` and would be clobbered if evidence were written there (D-12).

## Pre-change commit SHA

Measured with `git rev-parse HEAD` in this worktree at capture time (not copied from any
planning document):

```
$ git rev-parse HEAD
222e1b9b81809ef31b06c897e6eae0efdadf2cf9
```

## Environment note — live `typst.compile()` probe (RESEARCH Assumption A1)

RESEARCH.md's Q6 environment note flagged that `typst.compile()`'s availability in this sandbox
had been observed to differ between sessions (2026-08-14 `FileNotFoundError` vs. a 2026-08-15
success), and instructed re-verifying live at evidence-gathering time rather than trusting the
note.

**Live probe run this session:**

```
$ uv run python -c "
import typst
try:
    pdf_bytes = typst.compile(input='<scratch>/probe/hello.typ', format='pdf')
    print('COMPILE OK, bytes:', len(pdf_bytes))
except Exception as e:
    print('COMPILE FAILED:', type(e).__name__, e)
"
COMPILE OK, bytes: 7751
```

(An earlier attempt in this same session passing a raw Typst source *string* as `input=` failed
with `FileNotFoundError: No such file or directory (os error 2)` — that failure is a usage error
on this probe's part, not an environment limitation: `typst.compile()`'s `input` parameter is a
**file path**, not inline content, confirmed by reading `typsphinx/pdf.py:143`
(`typst.compile(typ_path, root=root_dir)`) and its own docstring note at `pdf.py:185`
("typst.compile() requires a file path, not string content"). Once a real `.typ` file path was
passed, compilation succeeded immediately.)

**Path taken: the real PDF-compile path.** All four shapes below were built with
`sphinx-build -b typstpdf` and compiled to real PDFs (not the `-b typst` hash-only fallback),
with page counts read via `pypdf.PdfReader(...).pages` per shape.

## Four configuration shapes — `.typ` file inventory and SHA-256

All four builds ran via `uv run python -m sphinx -b typstpdf <source_dir> <scratch_dir>` inside
this worktree's own `uv sync --extra dev`-provisioned venv (mandatory per `CLAUDE.md`'s
Worktree-isolated execution section — otherwise the measurement would describe the main tree's
package, not this worktree's).

### Shape A — `typst_template` set

**Fixture:** `tests/fixtures/documented_params_contract_gate` (`conf.py` quoted verbatim
below). Builder: `-b typstpdf`.

```python
typst_documents = [
    ("index", "master.typ", project, author),
]

typst_template = "_templates/documented.typ"

typst_elements = {
    "papersize": "a4",
    "fontsize": "11pt",
}

# CRITICAL: do NOT set typst_template_function here.
```

Sorted `.typ` file list with SHA-256 (`find <scratch>/pre/shapeA -name '*.typ' | sort` then
`sha256sum` each):

```
22bc8c60c644fc5e809e58799fb52da82840c08b1e715c6fa8dab9d9d4571511  _template.typ
c160a6b5cd565ce452736d59b42b5f6d2a066e54608016dd9328232ff9b6e6d3  chapter.typ
f9fbfa8cacf58676ec6963370bc635dafc61410c0c83613a66f9e894cd2210dc  index.typ
ef419a0e6264f32a043c40154840ae926590495d1ec19c8241dce6a86579a21f  master.typ
```

PDF page count: `pypdf.PdfReader('<scratch>/pre/shapeA/master.pdf').pages` → **3 pages**.

### Shape B — `typst_package` set alone (no `typst_template`)

**Fixture:** `tests/fixtures/typst_lang_gate/package_no_lang` (`conf.py` quoted verbatim
below). Builder: `-b typstpdf`.

```python
typst_documents = [
    ("index", "master", project, author),
]

language = "ja"

typst_package = "@preview/charged-ieee:0.1.4"

typst_template_mapping = {
    "project": "title",
}

typst_template_function = {
    "name": "ieee",
    "params": {
        "abstract": "Package-path lang non-regression fixture abstract.",
        "index-terms": ["Fixture", "Gate", "Regression"],
        "paper-size": "a4",
    },
}
# CRITICAL: do NOT set `typst_template` here.
```

Sorted `.typ` file list with SHA-256:

```
ce6842fcf4d122f2c5d0f21d711a967406f8357d7e54d1a013e86411c384aa00  index.typ
3e97a827a8ef0c9151eaf7bbbdb86f28b91a7ac16a0f35c7311a46e88a5831cb  master.typ
```

(This shape emits no `_template.typ` — the package-alone route does not write the shared
template file, unlike shapes A/C/D. This is the real, observed output; it is not adjusted.)

PDF page count: `pypdf.PdfReader('<scratch>/pre/shapeB/master.pdf').pages` → **1 page**.

### Shape C — `typst_template_function` set alone (no `typst_template`, no `typst_package`)

**Fixture:** `tests/fixtures/params_exclusivity_gate/zero_params_default` (`conf.py` quoted
verbatim below). Builder: `-b typstpdf`.

```python
typst_documents = [
    ("index", "master", project, author),
]

# Deliberately no typst_template and no typst_package -- this is the
# bundled-default route.

typst_elements = {
    "papersize": "a4",
    "fontsize": "11pt",
}

typst_template_function = {
    "name": "project",
    "params": {},
}
```

Sorted `.typ` file list with SHA-256:

```
3976ef36a1da147038b6dd51d6c73632a26454258733aac0c05502d91110a5cc  _template.typ
faaad8f821d381215b50eaa87ddb85f50810a6903b9555f101e507cc1bedefb2  index.typ
20d0162ec4e84fae8cc1af30e563746355efd4e2107360689a9335e6e6e40490  master.typ
```

PDF page count: `pypdf.PdfReader('<scratch>/pre/shapeC/master.pdf').pages` → **3 pages**.

### Shape D — nothing set (bundled `base.typ`, no `typst_template` / `typst_package` /
`typst_template_function`)

**Fixture:** `tests/roots/test-basic` (`conf.py` quoted verbatim below). Builder: `-b typstpdf`.

```python
extensions = ["typsphinx"]

project = "Test Project"
author = "Test Author"
copyright = "2025, Test Author"

typst_documents = [
    ("index", "output.typ", "Test Document", "Test Author"),
]
```

Sorted `.typ` file list with SHA-256:

```
3976ef36a1da147038b6dd51d6c73632a26454258733aac0c05502d91110a5cc  _template.typ
57b4af37eae8588497ecd0613d633facd0d3e1a24ad315802f4db469f638c43e  index.typ
8613bc8366e60145da1c12fa1d50596cf54799bcf1adefd502d7de1248119f3d  output.typ
```

PDF page count: `pypdf.PdfReader('<scratch>/pre/shapeD/output.pdf').pages` → **3 pages**.

(Note: Shape C's and Shape D's `_template.typ` share the same SHA-256
`3976ef36a1da147038b6dd51d6c73632a26454258733aac0c05502d91110a5cc` — both are the bundled
default template with zero custom parameters, which is the expected, unremarkable result of both
shapes resolving to `typsphinx/templates/base.typ` via `resolve_template()`'s Priority 3. This
is recorded as measured, not asserted from assumption.)

## TPL-04 equivalence (pre-change)

**Fixture used (per RESEARCH.md Q6 step 6):** `tests/fixtures/params_exclusivity_gate/
zero_params_default`, whose `conf.py:30` already authors a four-element `typst_documents` tuple
— confirmed by direct read before copying:

```python
typst_documents = [
    ("index", "master", project, author),
]
```

Two copies of this fixture tree were made into the session scratchpad:

- **Copy 1 (`tpl04_four`):** `typst_documents` left exactly as authored (four elements —
  `"index"`, `"master"`, `project`, `author`).
- **Copy 2 (`tpl04_five`):** every `typst_documents` tuple given a literal fifth element
  `"typst"` appended, changing nothing else:
  ```python
  typst_documents = [
      ("index", "master", project, author, "typst"),
  ]
  ```

Both copies were built with the same builder (`-b typstpdf`) used throughout this artifact, into
two separate scratch output directories (`<scratch>/pre/tpl04_four`, `<scratch>/pre/tpl04_five`).

### Copy 1 (`tpl04_four`, four-element tuple) — sorted `.typ` inventory

```
3976ef36a1da147038b6dd51d6c73632a26454258733aac0c05502d91110a5cc  _template.typ
faaad8f821d381215b50eaa87ddb85f50810a6903b9555f101e507cc1bedefb2  index.typ
20d0162ec4e84fae8cc1af30e563746355efd4e2107360689a9335e6e6e40490  master.typ
```

### Copy 2 (`tpl04_five`, explicit fifth element `"typst"`) — sorted `.typ` inventory

```
3976ef36a1da147038b6dd51d6c73632a26454258733aac0c05502d91110a5cc  _template.typ
faaad8f821d381215b50eaa87ddb85f50810a6903b9555f101e507cc1bedefb2  index.typ
20d0162ec4e84fae8cc1af30e563746355efd4e2107360689a9335e6e6e40490  master.typ
```

### Comparison result

**Identical.** Every SHA-256 in Copy 1's inventory matches the corresponding file's SHA-256 in
Copy 2's inventory, file for file (`_template.typ`, `index.typ`, `master.typ` — same three
files, same three hashes, in both trees). PDF page counts also match:
`pypdf.PdfReader('<scratch>/pre/tpl04_four/master.pdf').pages` → **3 pages**;
`pypdf.PdfReader('<scratch>/pre/tpl04_five/master.pdf').pages` → **3 pages**.

This comparison is between the two trees directly (Copy 1 vs. Copy 2), independent of the
four-shapes pre/post baseline above — it is TPL-04's own equivalence claim: an absent element
[4] and an explicit `"typst"` fifth element produce byte-identical output, pre-change.

## Post-change section

Measured by plan 53-05 after Phase 53's registry plumbing (plans 53-01..53-04) landed.

### Post-change commit SHA

Measured with `git rev-parse HEAD` in the main working tree at capture time (not copied from any
planning document, distinct from the pre-change SHA above):

```
$ git rev-parse HEAD
eb445058858994744a29cda93548503c90c76462
```

### Environment note — live `typst.compile()` probe re-verified

Per the pre-change section's own instruction to re-verify live rather than trust a prior note:

```
$ uv run python -c "
import typst
try:
    pdf_bytes = typst.compile(input='<scratch>/probe/hello.typ', format='pdf')
    print('COMPILE OK, bytes:', len(pdf_bytes))
except Exception as e:
    print('COMPILE FAILED:', type(e).__name__, e)
"
COMPILE OK, bytes: 8552
```

**Path taken: the real PDF-compile path**, identical to the pre-change measurement — no divergence
to record. All four shapes below were built with `sphinx-build -b typstpdf` (via
`uv run python -m sphinx -b typstpdf <source_dir> <scratch_dir>`) and compiled to real PDFs, with
page counts read via `pypdf.PdfReader(...).pages`, matching the pre-change procedure exactly. This
measurement ran in the main working tree on branch `gsd/v0.9.0-per-document-templates` (not a
worktree), so no separate `uv sync` was required — the tree's own `.venv` is already provisioned
with the post-change `typsphinx` package.

### Four configuration shapes — post-change `.typ` file inventory and SHA-256

Same four fixtures, same builder, same shape labels as the pre-change section.

#### Shape A — `typst_template` set

**Fixture:** `tests/fixtures/documented_params_contract_gate`. Builder: `-b typstpdf`.

Sorted `.typ` file list with SHA-256:

```
22bc8c60c644fc5e809e58799fb52da82840c08b1e715c6fa8dab9d9d4571511  _template.typ
c160a6b5cd565ce452736d59b42b5f6d2a066e54608016dd9328232ff9b6e6d3  chapter.typ
f9fbfa8cacf58676ec6963370bc635dafc61410c0c83613a66f9e894cd2210dc  index.typ
ef419a0e6264f32a043c40154840ae926590495d1ec19c8241dce6a86579a21f  master.typ
```

PDF page count: `pypdf.PdfReader('<scratch>/post/shapeA/master.pdf').pages` → **3 pages**.

**Verdict: MATCH.** Sorted file list is identical (4 files, same names). Every SHA-256 matches
the pre-change value for the same file, exactly. Page count matches (3 = 3).

#### Shape B — `typst_package` set alone (no `typst_template`)

**Fixture:** `tests/fixtures/typst_lang_gate/package_no_lang`. Builder: `-b typstpdf`.

Sorted `.typ` file list with SHA-256:

```
ce6842fcf4d122f2c5d0f21d711a967406f8357d7e54d1a013e86411c384aa00  index.typ
3e97a827a8ef0c9151eaf7bbbdb86f28b91a7ac16a0f35c7311a46e88a5831cb  master.typ
```

(No `_template.typ` emitted, matching pre-change — this shape's package-alone route does not
write the shared template file, unchanged by Phase 53.)

PDF page count: `pypdf.PdfReader('<scratch>/post/shapeB/master.pdf').pages` → **1 page**.

**Verdict: MATCH.** Sorted file list is identical (2 files, same names, `_template.typ` absent in
both). Every SHA-256 matches the pre-change value for the same file, exactly. Page count matches
(1 = 1).

#### Shape C — `typst_template_function` set alone (no `typst_template`, no `typst_package`)

**Fixture:** `tests/fixtures/params_exclusivity_gate/zero_params_default`. Builder: `-b typstpdf`.

Sorted `.typ` file list with SHA-256:

```
3976ef36a1da147038b6dd51d6c73632a26454258733aac0c05502d91110a5cc  _template.typ
faaad8f821d381215b50eaa87ddb85f50810a6903b9555f101e507cc1bedefb2  index.typ
20d0162ec4e84fae8cc1af30e563746355efd4e2107360689a9335e6e6e40490  master.typ
```

PDF page count: `pypdf.PdfReader('<scratch>/post/shapeC/master.pdf').pages` → **3 pages**.

**Verdict: MATCH.** Sorted file list is identical (3 files, same names). Every SHA-256 matches
the pre-change value for the same file, exactly. Page count matches (3 = 3).

#### Shape D — nothing set (bundled `base.typ`)

**Fixture:** `tests/roots/test-basic`. Builder: `-b typstpdf`.

Sorted `.typ` file list with SHA-256:

```
3976ef36a1da147038b6dd51d6c73632a26454258733aac0c05502d91110a5cc  _template.typ
57b4af37eae8588497ecd0613d633facd0d3e1a24ad315802f4db469f638c43e  index.typ
8613bc8366e60145da1c12fa1d50596cf54799bcf1adefd502d7de1248119f3d  output.typ
```

PDF page count: `pypdf.PdfReader('<scratch>/post/shapeD/output.pdf').pages` → **3 pages**.

**Verdict: MATCH.** Sorted file list is identical (3 files, same names). Every SHA-256 matches
the pre-change value for the same file, exactly. Page count matches (3 = 3).

### TPL-04 equivalence (post-change)

Repeated plan 53-01 Task 2's procedure exactly: two copies of
`tests/fixtures/params_exclusivity_gate/zero_params_default` in the session scratchpad — Copy 1
(`tpl04_four`) with `typst_documents` left as authored (four elements), Copy 2 (`tpl04_five`) with
a literal fifth element `"typst"` appended to every tuple — both built with `-b typstpdf` into
separate scratch output directories.

#### Copy 1 (`tpl04_four`, four-element tuple) — sorted `.typ` inventory

```
3976ef36a1da147038b6dd51d6c73632a26454258733aac0c05502d91110a5cc  _template.typ
faaad8f821d381215b50eaa87ddb85f50810a6903b9555f101e507cc1bedefb2  index.typ
20d0162ec4e84fae8cc1af30e563746355efd4e2107360689a9335e6e6e40490  master.typ
```

#### Copy 2 (`tpl04_five`, explicit fifth element `"typst"`) — sorted `.typ` inventory

```
3976ef36a1da147038b6dd51d6c73632a26454258733aac0c05502d91110a5cc  _template.typ
faaad8f821d381215b50eaa87ddb85f50810a6903b9555f101e507cc1bedefb2  index.typ
20d0162ec4e84fae8cc1af30e563746355efd4e2107360689a9335e6e6e40490  master.typ
```

#### Post-change comparison result

**Identical.** Every SHA-256 in Copy 1's inventory matches the corresponding file's SHA-256 in
Copy 2's inventory, file for file (`_template.typ`, `index.typ`, `master.typ`), confirmed with a
direct `diff` of the two sorted hash listings (empty diff). PDF page counts also match:
`pypdf.PdfReader('<scratch>/post/tpl04_four/master.pdf').pages` → **3 pages**;
`pypdf.PdfReader('<scratch>/post/tpl04_five/master.pdf').pages` → **3 pages**.

Both copies are additionally byte-identical to the pre-change TPL-04 baseline above (same three
hashes, same three page counts) — the registry resolver now performs this resolution
(`resolve_registry_key()` mapping an absent element [4] and an explicit `"typst"` fifth element to
the same `TemplateRegistryEntry`, per plan 53-02/53-03), and produces the same output the
pre-registry code path produced.

### Post-change summary verdict

All four shapes (A, B, C, D) and the TPL-04 four-element-vs-fifth-element comparison are
byte-identical between the pre-change commit (`222e1b9b81809ef31b06c897e6eae0efdadf2cf9`) and the
post-change commit (`eb445058858994744a29cda93548503c90c76462`). No file list changed (no file
appeared or disappeared in any shape), no SHA-256 changed, and no PDF page count changed. SC#2's
zero-edit-equivalence claim for TPL-03/TPL-04 is proven by measured identity, not assumption.
