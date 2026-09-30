# Phase 51: Two-Layer Output Documentation - Pattern Map

**Mapped:** 2026-08-14
**Files analyzed:** 17 (13 sweep-table edits from RESEARCH.md Part A + 4 net-new/structural files)
**Analogs found:** 17 / 17

This file does not repeat RESEARCH.md Part A's sweep table (the file:line list of falsified-claim
edits) or Part D's full read of `tests/test_quickstart_docs_gate.py` / `test_docs_contract_claims_gate.py`
— see RESEARCH.md for those. It concentrates on the four items RESEARCH.md flagged as needing a pattern
assignment: the new page, the new gate's fixtures, the helper-function import, and the README link style.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `docs/source/user_guide/output_layout.rst` (new, D-01) | documentation page | request-response (reader-facing prose) | `docs/source/user_guide/configuration.rst` | structural, best available |
| `docs/source/user_guide/index.rst` (toctree + Main Topics edit) | documentation index | request-response | itself (edit in place) | exact — see RESEARCH.md Part E for verbatim current content |
| `docs/source/changelog.rst` (new `Migrating from 0.7.x to 0.8.0` subsection, D-02) | documentation page | request-response | its own `Migrating from 0.7.0 to 0.7.1` subsection | exact |
| `docs/source/user_guide/builders.rst`, `configuration.rst`, `templates.rst`, `quickstart.rst` (prose fixes) | documentation page | request-response | RESEARCH.md Part A sweep table gives the exact edit per row | exact |
| `README.md` (false-claim fix + link, D-03) | documentation (root) | request-response | its own existing RTD-link list (lines 298-304) | exact |
| `examples/basic/README.md`, `examples/advanced/README.md` | documentation (example) | request-response | RESEARCH.md Part A rows 11-13 | exact |
| `tests/test_output_layout_docs_gate.py` (new, D-10/D-11/D-12) | test (gate) | request-response (subprocess build + file-set assert) | `tests/test_quickstart_docs_gate.py` | exact — same two-class shape, `-b typst` only instead of `-b typstpdf` |
| `tests/fixtures/output_layout_bare_target_gate/` (new fixture) | test fixture | file-I/O (sphinx-build over static `.rst`) | `tests/fixtures/quickstart_docs_gate/` (header-comment convention) + Part C build 1 (`"manual"`) | exact — content is a literal copy of a measured build |
| `tests/fixtures/output_layout_explicit_path_gate/` (new fixture) | test fixture | file-I/O | Part C build 2 (`"manuals/guide.typ"`) | exact |
| `tests/fixtures/output_layout_shared_child_gate/` (new fixture, optional — may just reuse existing) | test fixture | file-I/O | `tests/fixtures/state_guard_three_master_gate/` | exact — reuse, do not duplicate (see below) |

## Pattern Assignments

### `docs/source/user_guide/output_layout.rst` (new page, D-01)

**Analog:** `docs/source/user_guide/configuration.rst` (structural skeleton) with
`docs/source/user_guide/builders.rst`'s admonition-avoidance habit and `templates.rst`'s
cross-reference style.

**Heading hierarchy and adornment characters** (from `configuration.rst:1-24`):
```rst
Configuration
=============

Basic Configuration
-------------------

Project Information
~~~~~~~~~~~~~~~~~~~
```
Top level `=`, section level `-`, subsection level `~` — all three `user_guide/*.rst` pages agree on
this exact three-tier scheme. `output_layout.rst` should open the same way, e.g.:
```rst
Output Layout
=============

Wrapper and Content Files
--------------------------

Which File to Compile
~~~~~~~~~~~~~~~~~~~~~~
```

**How a config example sits next to its outcome** (`configuration.rst:37-52`, the closest existing
"config block immediately followed by prose describing the resulting file(s)" shape):
```rst
.. code-block:: python

   typst_documents = [
       ("index", "output", "Title", "Author", "typst"),
   ]

Each tuple contains:

1. **Source file** (without ``.rst`` extension)
2. **Output filename stem** -- governs both the emitted ``.typ`` file and,
   under the ``typstpdf`` builder, the compiled ``.pdf``. ...
```
For the new page's worked examples, follow this shape but describe BOTH emitted files (wrapper +
content), using RESEARCH.md Part C's measured file sets verbatim (e.g. build 1: `("index", "manual", ...)`
→ `manual.typ` (wrapper, outdir root) + `index.typ` (content, outdir root, unconditional)).

**How file-set / directory listings are rendered:** none of the three existing pages render a
`find`-style directory listing inside a `.. code-block::` — they describe file sets in prose or bullet
lists only (e.g. `builders.rst:38-40`'s three-bullet "Output" section). The new page should follow this
convention (prose/bullets naming exact filenames) rather than inventing a tree-diagram block, since no
precedent for one exists anywhere in `docs/source/user_guide/`.

**Admonition usage — `.. note::` and `.. warning::` (both present, in `configuration.rst` and
`templates.rst`, absent from `builders.rst`):**
```rst
.. note::

   This setting only applies to local custom templates (``typst_template``).
   Typst Universe packages (``typst_package``) handle assets automatically.
```
(`configuration.rst:155-158`) — used for a short scoping caveat, one paragraph.
```rst
.. warning::

   A **partial** migration to the ``params`` route is a silent trap.
   Declaring ``params`` with only one key -- for example
   ``params: {"authors": [...]}`` -- to add rich author structure while
   expecting ``title`` and ``date`` to keep arriving from the auto-derived
   set does **not** work: declaring ``params`` at all replaces the entire
   set. ...
```
(`configuration.rst:259-272`) — used for "this looks like it should work but doesn't" content, which is
structurally the SAME shape D-07's `:numref:` case would have used had it been in scope, and the shape
D-08 explicitly REJECTS for the standalone-content behaviour. **Per D-08, do not reuse this `.. warning::`
pattern for the standalone-compile behaviour** — write it as plain prose inside the "which file to
compile" section instead, in the same declarative voice `configuration.rst:28-35` uses for the
`typst_documents`-unset derivation (no admonition wrapper at all):
```rst
Setting ``typst_documents`` is optional. When it is absent, typsphinx
derives a single entry from ``root_doc``, ``project``, and ``author``, with
the target stem produced by the same ``make_filename_from_project`` helper
Sphinx's own LaTeX builder uses. ...
```
This is the exact register the new page's standalone-content paragraph should match: stated as normal,
expected behaviour, no "Note"/"Warning" label.

**Cross-referencing other pages** — both `:doc:` and `.rst`-only footnote-style label references are in
use; `:doc:` is used for page-to-page and `See Also` links:
```rst
See :doc:`templates` for detailed examples.
...
See Also
--------

- :doc:`configuration` - Configuration options
- :doc:`templates` - Customizing templates
- :doc:`/examples/basic` - Basic usage examples
```
(`configuration.rst:160`, `builders.rst:184-189`) — a leading-slash form (`:doc:`/examples/basic`) is used
for cross-directory references, a bare form (`:doc:`templates`) for same-directory siblings. A single
underscore-suffixed inline reference to a same-page section is also in use (`configuration.rst:64`:
`` `Author Information`_ below ``) for forward-references within one page. `output_layout.rst` should
gain its own `See Also` section (pattern: `configuration.rst:405-410`) and `builders.rst` /
`configuration.rst` should each add one `:doc:`output_layout`` cross-reference per D-01 rather than
duplicating content.

**No `.. list-table::` precedent for file-set display** — `builders.rst:9-21` is the one `list-table`
in the three pages, used for the two-builder comparison (Builder / Output / Use Case columns). If the
planner wants a compact table for "target shape → wrapper path → content path" (RESEARCH.md Part B's own
table), this is the analog to copy the `:header-rows: 1` / `:widths:` shape from.

---

### `docs/source/changelog.rst` — new `Migrating from 0.7.x to 0.8.0` subsection (D-02)

**Analog:** the file's own `Migrating from 0.7.0 to 0.7.1` subsection, `docs/source/changelog.rst:6-45`
(full read; excerpt below covers the reusable shape).

**Section header + intro-sentence pattern:**
```rst
Migrating from 0.7.0 to 0.7.1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This patch release carries three breaking configuration changes. Each item below shows the
rewrite: the ``conf.py``/template fragment you have today, and the corrected fragment to replace
it with.
```
New subsection should read `Migrating from 0.7.x to 0.8.0` at the same `~~~` level, directly below the
0.7.0→0.7.1 subsection (same `Migration Guides` `-----` parent section, `changelog.rst:4`).

**Per-change bullet + before/after code-block pair:**
```rst
- **Breaking:** the ``typst_authors`` config value is removed. It was pure sugar over the
  ``typst_template_function`` ``params`` route ...

  .. code-block:: python

     # Old way -- typst_authors is gone in 0.7.1
     typst_authors = { ... }

  .. code-block:: python

     # New way -- the same dictionary through typst_template_function's params route
     typst_template_function = { ... }
```
D-02 requires one bullet per breaking change with this exact two-block shape. The two changes to cover
(per CONTEXT.md/RESEARCH.md): (a) the wrapper/content split (illustrate with Part C build 1's
`("index", "manual", ...)` → v0.7.x wrote `manual.typ` as the whole document, v0.8.0 writes `manual.typ`
as wrapper + `index.typ` as content — CONTEXT.md's own canonical illustration), (b) the target-as-path
reversal (OUT-01, illustrate with `"manuals/guide.typ"` being rejected pre-0.8.0 vs. accepted as-is now).
Comment convention inside each block: `# Old way -- X is gone in 0.7.1` / `# New way -- ...` — adapt the
tense/wording (`# v0.7.x behaviour` / `# v0.8.0 behaviour`) since this isn't a removed-setting case.

---

### `tests/test_output_layout_docs_gate.py` (new gate, D-10/D-11/D-12)

**Analog:** `tests/test_quickstart_docs_gate.py` (full file; RESEARCH.md Part D already extracted its
two-class shape and `_run_sphinx_build()` helper — reproduced here only where this phase's gate diverges).

**Diverges from the analog in exactly one way (D-12):** no `TYPST_AVAILABLE` / `import typst` skip guard
at all, and no `-b typstpdf` class. Use `-b typst` only, unconditionally, for both classes' build steps
(the analog's `TestQuickstartFirstPdfGate` skip-guard block, lines 33-38, should be DROPPED, not copied):
```python
try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False
```
Everything else — module docstring shape, `REPO_ROOT`/`FIXTURES_DIR` constants, `_run_sphinx_build()`
verbatim (reproduce independently per this suite's own per-module-copy convention, `test_quickstart_docs_
gate.py`'s docstring: "every gate module in this suite carries its own copy of this helper"), the
"build class" + "published-text class" two-class split — copy directly:
```python
import subprocess
import sys
from pathlib import Path

from sphinx.util.osutil import make_filename_from_project

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = Path(__file__).parent / "fixtures"

def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", builder, str(source_dir), str(build_dir)],
        capture_output=True,
        text=True,
    )
```

**Helper-function import (D-11's "derive from the same helpers the builder uses"):** import
`sphinx.util.osutil.make_filename_from_project` exactly as the analog does at module level (`test_
quickstart_docs_gate.py:29`), and compute the fixture's expected default-derivation stem the same way:
```python
_FIXTURE_PROJECT = "My Project"
_EXPECTED_STEM = make_filename_from_project(_FIXTURE_PROJECT)
```
For the bare-target and explicit-path fixtures (Part C builds 1/2), no helper call is needed — assert
`Path(build_dir / "manual.typ").exists()` / `Path(build_dir / "manuals" / "guide.typ").exists()` and
`Path(build_dir / "index.typ").exists()` directly against the real build output (per RESEARCH.md's
"Don't Hand-Roll" table: never reimplement `_resolve_target_stem()`'s decision tree inside the test).

**Prose-match class pattern** (`test_quickstart_docs_gate.py`'s `TestPublishedQuickstartTextMatchesBuild`,
adapt file targets to `output_layout.rst` instead of `quickstart.rst`/`README.md`):
```python
README_PATH = REPO_ROOT / "README.md"
QUICKSTART_RST_PATH = REPO_ROOT / "docs" / "source" / "quickstart.rst"
```
→ becomes `OUTPUT_LAYOUT_RST_PATH = REPO_ROOT / "docs" / "source" / "user_guide" / "output_layout.rst"`.
Assert literal substrings (exact filenames from Part C) appear in the page text via
`Path(...).read_text()`, no skip guard, no `typst-py` import — this class is what makes D-12's "must
never skip" true for the prose half.

**Do not extend `test_docs_contract_claims_gate.py`** — its own docstring states the D-J fence explicitly
(RESEARCH.md Part D); the new gate is a separate module.

---

### `tests/fixtures/output_layout_bare_target_gate/conf.py` and `output_layout_explicit_path_gate/conf.py` (new fixtures)

**Analog:** `tests/fixtures/quickstart_docs_gate/conf.py` (header-comment convention) — full text read;
key excerpt for the convention to reproduce:
```python
# Sphinx configuration for the DOC-11 published-Quick-Start gate.
#
# Mirrors docs/source/quickstart.rst's "Your First PDF" flow verbatim: ...
# Do not add a typst_documents line here; doing so would silently stop this
# fixture from exercising the published Quick Start's own steps.
#
# This fixture is NOT the same as tests/fixtures/default_typst_documents_gate/: ...
# Do not merge them and do not modify the existing fixture.

project = "My Project"
author = "Your Name"
release = "1.0.0"
copyright = "2026, Your Name"

extensions = ["typsphinx"]
```
Every fixture in this directory: (1) a header comment stating its ONE job and what NOT to touch/merge it
with, (2) minimal `project`/`author`/`release`/`copyright`/`extensions`, (3) the `typst_documents` line
(or its deliberate absence) as the single load-bearing config value. For the two new fixtures, the
`typst_documents` line is a literal copy of RESEARCH.md Part C's measured configs:
```python
typst_documents = [("index", "manual", "Title", "Author", "typst")]        # bare-target fixture
typst_documents = [("index", "manuals/guide.typ", "Title", "Author", "typst")]  # explicit-path fixture
```
Each fixture also needs one `index.rst` (any minimal body — no toctree needed, matching Part C's builds
which had none).

**For the shared-child / multi-master worked example: reuse `tests/fixtures/state_guard_three_master_gate/`
directly rather than creating a new fixture.** Its `conf.py` header comment (reproduced above in full)
already documents load-bearing properties the new gate must not disturb ("do NOT touch any of these").
RESEARCH.md Part C build 4 is this fixture's own measured `-b typst` output — the new gate's third test
method can point `_run_sphinx_build()` at this existing fixture and assert the same 10-file `.typ` set
(`_template.typ`, `common_a.typ`, `common_b.typ`, `m1.typ`, `m2.typ`, `m3.typ`, `manual1.typ`,
`manual2.typ`, `manual3.typ`, `mid.typ`) without adding a new directory under `tests/fixtures/`.

---

### `README.md` (D-03 correction + link)

**Analog:** README's own existing RTD-link list, `README.md:298-304`:
```markdown
- [Installation Guide](https://typsphinx.readthedocs.io/en/latest/installation.html)
- [Quick Start](https://typsphinx.readthedocs.io/en/latest/quickstart.html)
- [User Guide](https://typsphinx.readthedocs.io/en/latest/user_guide/)
- [Configuration Reference](https://typsphinx.readthedocs.io/en/latest/user_guide/configuration.html)
- [Examples](https://typsphinx.readthedocs.io/en/latest/examples/)
- [API Reference](https://typsphinx.readthedocs.io/en/latest/api/)
- [Contributing Guide](https://typsphinx.readthedocs.io/en/latest/contributing.html)
```
The new page's link follows this exact list's shape and RTD-absolute-URL convention:
`- [Output Layout](https://typsphinx.readthedocs.io/en/latest/user_guide/output_layout.html)`, inserted
adjacent to the existing `Configuration Reference` entry. A second, separate link convention also exists
in this file — a relative repo-path Markdown link used inline in prose, `README.md:226`:
`` see [docs/source/user_guide/configuration.rst](docs/source/user_guide/configuration.rst) for the full
reference ``. If D-03's "linking to the new page" is meant to sit inline in the corrected Quick Start
prose rather than in the RTD list, this second, relative-path form is the analog to copy instead — both
forms already coexist in the file, so either is precedented; the RTD-list form is preferred for a
standalone "see also"-style addition, the inline relative-path form for a correction embedded in running
prose right next to the fixed claim.

---

### `examples/advanced/README.md` (D-04 sweep, highest-value non-`docs/source` target)

RESEARCH.md Part A rows 12-13 give the exact false text and its replacement shape (state-guarded
`if "<edge_key>" in state(...).get() { include(...) }` per `translator.py:338-377`, reproduced verbatim
in RESEARCH.md's Code Examples section). No additional analog needed beyond RESEARCH.md's own citation —
flagged here only to confirm no separate structural pattern search was skipped for this file.

## Shared Patterns

### Heading adornment scheme (all `docs/source/user_guide/*.rst`)
**Source:** `docs/source/user_guide/configuration.rst:1-24`, consistent across `builders.rst` and
`templates.rst`.
**Apply to:** `output_layout.rst` (new page).
```
Page Title
==========

Section
-------

Subsection
~~~~~~~~~~
```

### Config-example-then-consequence prose shape
**Source:** `docs/source/user_guide/configuration.rst:37-52`.
**Apply to:** every worked example on `output_layout.rst`.
A `.. code-block:: python` showing the `typst_documents` entry immediately followed by a
numbered-or-bulleted prose block naming every file the config produces (not just the one element being
illustrated).

### `.. note::` vs. plain prose vs. `.. warning::` — do not conflate D-08's requirement
**Source:** `docs/source/user_guide/configuration.rst:155-158` (note), `:259-272` (warning),
`:28-35` (plain declarative prose, no admonition).
**Apply to:** `output_layout.rst`'s standalone-content-compile section MUST use the plain-prose form
(D-08); reserve `.. warning::` for genuinely broken/trap behaviour (none exists in this phase's scope —
`:numref:` is excluded by D-07) and `.. note::` for short scoping caveats only.

### `:doc:` cross-reference form
**Source:** `docs/source/user_guide/builders.rst:184-189`, `configuration.rst:405-410`.
**Apply to:** the new page's `See Also` section, and the one-line `:doc:`output_layout`` addition each
of `builders.rst` and `configuration.rst` needs per D-01.

### Gate two-class shape (real-build class + never-skip prose-match class)
**Source:** `tests/test_quickstart_docs_gate.py` (full file).
**Apply to:** `tests/test_output_layout_docs_gate.py`, with the `-b typst`-only divergence from D-12
noted above (drop the `TYPST_AVAILABLE` skip guard entirely).

### Fixture header-comment convention (job statement + do-not-touch note)
**Source:** `tests/fixtures/quickstart_docs_gate/conf.py`, `tests/fixtures/state_guard_three_master_gate/conf.py`.
**Apply to:** any new fixture directory this phase adds under `tests/fixtures/`.

### Migration-guide bullet + before/after code-block pair
**Source:** `docs/source/changelog.rst:10-45` (`Migrating from 0.7.0 to 0.7.1`).
**Apply to:** the new `Migrating from 0.7.x to 0.8.0` subsection (D-02).

## No Analog Found

None. Every file this phase touches or creates has a same-repository structural analog; RESEARCH.md
Part A already supplies the exact per-line edit for the 13 sweep-table files, so those needed no
additional pattern search here.

## Metadata

**Analog search scope:** `docs/source/user_guide/*.rst`, `docs/source/changelog.rst`, `README.md`,
`tests/test_quickstart_docs_gate.py`, `tests/test_docs_contract_claims_gate.py`,
`tests/fixtures/quickstart_docs_gate/`, `tests/fixtures/state_guard_three_master_gate/`.
**Files scanned:** 9 read in full or targeted-range, plus RESEARCH.md's own Part A/B/C/D/E (not
re-scanned, cited).
**Pattern extraction date:** 2026-08-14
