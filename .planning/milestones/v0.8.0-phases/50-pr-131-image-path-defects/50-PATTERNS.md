# Phase 50: PR #131 Image Path Defects - Pattern Map

**Mapped:** 2026-08-14
**Files analyzed:** 4 (1 modified source file, 1 new fixture directory, 1 new render-gate test module, 1 modified unit-test file)
**Analogs found:** 4 / 4

This document extends RESEARCH.md — it does not restate the fix shape (RESEARCH.md's Code Examples
section already gives the literal `_track_image()` diff). Its job is the concrete excerpt-level
analog map for the NEW files this phase creates, per the orchestrator's scope note.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|---------------|
| `typsphinx/builder.py` (`_track_image()` widened) | builder / core-logic | transform (doctree-node mutation + dict tracking) | itself — `_escapes_outdir()`, `_collision_key()`, `_validate_output_path_collisions()` (same file, same module idiom) | exact (same file) |
| `tests/fixtures/<new-fixture>/` (conf.py, index.rst, 2 content docs, 2 PNGs) | test fixture (Sphinx project) | file-I/O / build-input | `tests/fixtures/absolute_image_render_gate/` | exact (same fixture family, D-10 explicitly extends it) |
| `tests/test_<new-fixture>_gate.py` (new render-gate module) | test / integration | request-response (subprocess build) + file-I/O (PDF read) | `tests/test_abbr_pep_separator_render_gate.py` (structure/scaffolding); `tests/test_absolute_image_render_gate.py` (domain — image tracking) | exact (scaffolding) / exact (domain) — two-analog case, see below |
| `tests/test_builder.py` (new unit tests appended) | test / unit | CRUD (in-memory `self.images` dict assertions) | `test_post_process_images_rehomes_absolute_uri` + `test_copy_image_files_uses_override_source_for_absolute_uri` (same file, D-12 pinned, sit beside without editing) | exact (same file) |

## Pattern Assignments

### `typsphinx/builder.py` — `_track_image()` (builder, transform)

**Analog:** the file's own existing guards — `_escapes_outdir()` (lines 63-104), `_is_drive_qualified()`
(lines 28-60), `_collision_key()` (lines 415-492), `_validate_output_path_collisions()` (lines
494-605+) — plus the method being modified itself (lines 840-876).

**Imports already present, no new imports needed** (lines 8-22):
```python
import posixpath
import shutil
from collections.abc import Iterator
from os import path
from typing import Dict, List, Set, Tuple

from docutils import nodes
from sphinx.builders import Builder
from sphinx.config import Config
from sphinx.errors import ExtensionError
from sphinx.util import logging
from sphinx.util.osutil import ensuredir, make_filename_from_project

from typsphinx.pdf import compile_typst_file_to_pdf
from typsphinx.translator import derive_master_edge_keys
from typsphinx.writer import TypstWriter

logger = logging.getLogger(__name__)
```
`_escapes_outdir()` is reusable as-is (RESEARCH.md Pattern 2) — no new helper import needed, and it
already lives above `_track_image()` in the same module, so no cross-module import is required either.

**Docstring idiom to match** (`_escapes_outdir()`, lines 63-96) — Google-style with an `Examples:`
doctest block, and a rationale paragraph explaining *why* the check is shaped the way it is (not just
what it does). `_track_image()`'s own current docstring (lines 841-866) already follows this style —
extend it in place rather than replacing the voice:
```python
def _escapes_outdir(stem: str) -> bool:
    """Whether a (suffix-stripped) ``typst_documents`` target stem
    attempts to escape the output directory (OUT-02): ...

    Args:
        stem: The already-suffix-stripped ``typst_documents`` target
            stem.

    Returns:
        True if the stem attempts to escape outdir, False otherwise.

    Examples:
        >>> _escapes_outdir("manuals/guide")
        False
        >>> _escapes_outdir("../escape")
        True
    """
```

**Current method body to widen** (lines 840-876, verbatim — this is what the plan's diff starts from):
```python
    def _track_image(self, node: nodes.image, resolved_uri: str) -> None:
        """
        ... [existing docstring, Issue #130 framing] ...
        """
        if path.isabs(resolved_uri):
            rel_uri = path.relpath(resolved_uri, self.doctreedir).replace(path.sep, "/")
            node["uri"] = rel_uri
            if rel_uri not in self.images:
                self.images[rel_uri] = resolved_uri
            return

        # Store empty string as value to be compatible with parent class type
        if resolved_uri not in self.images:
            self.images[resolved_uri] = ""
```
RESEARCH.md's Code Examples section gives the literal widened replacement (wrap `path.relpath()` in
`try/except ValueError` for D-07, call `_escapes_outdir(rel_uri)` for D-05/D-06, and
`path.isfile(path.join(self.srcdir, rel_uri))` for D-01/D-03) — reuse that block; do not re-derive it
here.

**Warning-emission idiom to match** (D-06's warn-on-escape) — `post_process_images()`'s own existing
warning at lines 827-831 is the closest same-method-family precedent for a single-line, f-string
`logger.warning` naming the offending value:
```python
                    logger.warning(
                        f"a suitable image for typst builder not found: "
                        f"{mimetypes} ({node.get('uri', '')})"
                    )
```
`_validate_output_path_collisions()`'s own docstring (lines 518-525) documents a stricter rule worth
matching: name the specific offending value and state what happened, in one `logger.warning` call, at
the ONE call site that owns emitting it — do not duplicate the warning across call sites.

**Early-return / guard shape idiom** — every guard in this file (`_escapes_outdir`, `_is_drive_qualified`,
`_is_usable_typst_documents_entry`) is a small pure predicate returning `bool`, called from the
mutating method rather than inlined; `_track_image()` should keep calling `_escapes_outdir(rel_uri)`
as a plain boolean test, matching this module's established style of "guard is a named predicate, call
site is a plain `if`" rather than inlining the segment-split logic into `_track_image()` directly.

**Constant naming precedent for `RESERVED_IMAGE_NAMESPACE = "_typst_converted"`** — this file has no
existing module-level string constant of this shape (the closest precedent is
`_write_template_file()`'s literal `"_template.typ"` string used inline, not a named constant); a
new module-level constant near the top of the file (after the `logger = ...` line, alongside
`_is_drive_qualified`/`_escapes_outdir`) matches this file's pattern of defining small named helpers
before the class body that uses them.

---

### `tests/fixtures/<new-fixture>/` (test fixture, file-I/O)

**Analog:** `tests/fixtures/absolute_image_render_gate/` — copy this pattern; DO NOT mutate the
original (D-12).

**`conf.py` to adapt** (full file, `tests/fixtures/absolute_image_render_gate/conf.py`):
```python
import os
import shutil

from docutils import nodes
from sphinx.transforms import SphinxTransform

project = "Absolute Image Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

html_static_path = ["_static"]

typst_documents = [
    ("index", "master.typ", "Absolute Image Render Gate", "Test Author"),
]


class FakeImageConverter(SphinxTransform):
    """
    Mimics ``sphinx.transforms.post_transforms.images.ImageConverter``: it
    "converts" the ``.svg`` source to a PNG stand-in under
    ``<doctreedir>/images/`` and rewrites ``node["uri"]`` (and its single
    ``"*"`` candidate) to that ABSOLUTE destination path.
    """

    default_priority = 200

    def apply(self, **kwargs: object) -> None:
        imagedir = os.path.join(self.env.doctreedir, "images")
        os.makedirs(imagedir, exist_ok=True)

        for node in self.document.findall(nodes.image):
            uri = node.get("uri", "")
            if not uri.endswith(".svg"):
                continue

            destpath = os.path.join(imagedir, "diagram.png")
            standin = os.path.join(self.env.srcdir, "_static", "converted_stand_in.png")
            shutil.copyfile(standin, destpath)

            node["uri"] = destpath
            if "candidates" in node:
                node["candidates"] = {"*": destpath}


def setup(app):
    app.add_post_transform(FakeImageConverter)
```
**What must change for the D-10 fixture:** the target PNG basename (currently hardcoded
`"diagram.png"`) must equal the REAL source image's basename so the two collide at
`images/<basename>` — that is the entire point of D-10's fixture (the todo's IMG-01 collision), unlike
this analog fixture, which has no colliding real source image at all. Add a second `nodes.image`
match target if the fake converter needs to run against a different content doc's `.svg`; or simplify
by having only ONE document trigger the fake converter and the OTHER document reference the real
`<srcdir>/images/<basename>.png` directly via an ordinary `.. figure::`. `typst_documents` must still
name a `master.typ`-style de-collided target (per the fixture family's own Phase 47 rename comment,
lines 52-57) — copy that comment's framing if renaming the master target.

**`index.rst` to adapt** (full file, `tests/fixtures/absolute_image_render_gate/index.rst`):
```rst
Absolute Image Render Gate
============================

This fixture references an SVG figure. ...

.. figure:: _static/diagram.svg

   A figure whose URI is rewritten to an absolute path by the fixture's
   fake image converter.
```
D-10 requires a MASTER `index.rst` toctree'ing two content documents (not one inline figure) — the
closer structural shape to copy for the master is any of this repo's existing multi-doc toctree
fixtures (search `tests/fixtures/*/index.rst` for a `.. toctree::` directive if the toctree syntax
itself needs a second analog; not reproduced here since RESEARCH.md's Recommended Project Structure
already gives the target tree: `index.rst` (master toctree) → `converted_source.rst` (figures the
`.svg` that "converts") + `real_source.rst` (figures the REAL srcdir image directly) → `images/<colliding-name>.png`.

**Asset directory layout** (`tests/fixtures/absolute_image_render_gate/_static/`):
```
_static/converted_stand_in.png   # the fake "converted" stand-in PNG, copied by FakeImageConverter
_static/diagram.svg              # the SVG source that triggers the fake converter
```
For D-09 (pixel-dimension discrimination), the new fixture's two PNGs (the converted stand-in and the
real colliding source image) must be given DIFFERENT pixel dimensions — `converted_stand_in.png` in
the analog fixture is a generic 1x1 PNG (per its comment: "a valid 1x1 PNG so the emitted image() call
points at bytes Typst can decode"); the new fixture needs two real, differently-sized PNGs instead
(e.g. via Pillow in a one-off fixture-generation script, not committed as a 1x1 stand-in).

---

### `tests/test_<new-fixture>_gate.py` (new render-gate test module)

**Two analogs, different jobs:**
1. **`tests/test_abbr_pep_separator_render_gate.py`** — the more RECENT (Phase 21+) render-gate
   scaffolding: subprocess build helper, `TYPST_AVAILABLE`/`PYPDF_AVAILABLE` skip guards, fixture
   path/tmp-dir fixtures, and the two-test split (structural `.typ` assert in test 1, pypdf-extracted
   assert in test 2). Copy THIS for the module's shape.
2. **`tests/test_absolute_image_render_gate.py`** — the domain-specific analog: same `_track_image()`
   bug family, same "are the same file" / "file not found" stderr strings, same `master.pdf` wrapper
   output naming convention. Copy THIS for what to assert about images specifically.

**Imports + skip-guard pattern** (both analogs, identical shape — `tests/test_abbr_pep_separator_render_gate.py:38-56`):
```python
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
```

**Subprocess build helper — the mandatory `sys.executable -m sphinx` invocation** (identical in both
analogs; `tests/test_abbr_pep_separator_render_gate.py:71-94`):
```python
@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typstpdf`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``)
    so the exact interpreter/venv running this test is reused, sidestepping
    the documented NixOS-sandbox PATH-shadowing hazard.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typstpdf",
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )
```
This is CLAUDE.md's own standing rule ("never a console-script shim") restated at the test-code level
— every render-gate module in this repo re-derives this exact helper rather than sharing one; match
that, do not attempt to extract a shared conftest helper unless the plan explicitly decides to (no
existing precedent for doing so).

**`@pytest.mark.skipif` class-level guard + two-test split** (`tests/test_abbr_pep_separator_render_gate.py:97-101, 111, 177-181`):
```python
@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the <name> render gate",
)
class Test<Name>RenderGate:
    def test_typstpdf_<name>_produces_pdf_with_structural_<assertion>(
        self, <fixture_dir_fixture>, temp_build_dir
    ):
        ...  # structural .typ assertion + PDF-exists-and-starts-with-%PDF check

    @pytest.mark.skipif(
        not PYPDF_AVAILABLE,
        reason="pypdf is required for the extracted-<assertion>",
    )
    def test_pdf_extracted_<assertion>(
        self, <fixture_dir_fixture>, temp_build_dir
    ):
        ...  # pypdf.PdfReader() extraction assertion
```
Note this repo's convention: `TYPST_AVAILABLE` gates the whole class (every test needs a real compile
to produce the artifact under test), while `PYPDF_AVAILABLE` gates only the pypdf-specific test
individually — because the first test's structural `.typ` assertions don't need pypdf at all.

**Domain-specific stderr/structural assertions to copy from `test_absolute_image_render_gate.py`**
(lines 138-201) — the "are the same file" / "file not found" negative-assertions, the
`'image("images/diagram.png")' in typ_text` positive structural assertion, and the copied-asset
existence check are this phase's closest precedent for what a NEW render gate must assert for IMG-01
(no "are the same file" warning is the wrong signal for the collision case — see Pitfall framing
below):
```python
        assert "are the same file" not in result.stderr, (...)
        ...
        assert 'image("images/diagram.png")' in typ_text, (...)

        copied_asset = temp_build_dir / "images" / "diagram.png"
        assert copied_asset.exists(), (...)

        pdf_output = temp_build_dir / "master.pdf"
        assert pdf_output.exists(), (...)
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
```
**IMG-01-specific adaptation needed:** unlike the analog (one image, no collision), D-08's RED/GREEN
assertion is about a SET of extracted pixel-dimension pairs from `page.images`, not a single
`image("images/diagram.png")` string match — see RESEARCH.md's Code Examples for the exact
`extracted_sizes == {CONVERTED_STANDIN_DIMS, REAL_SOURCE_DIMS}` idiom and Pitfall 3's "assert on the
SET, not `page.images[N]` by index" warning. Do not copy the analog's single-image string-match
assertion verbatim — extend it into a two-image set-comparison.

**pypdf extraction pattern to copy** (`tests/test_pdf_render_gate.py:244-266`, referenced by
RESEARCH.md, and `tests/test_abbr_pep_separator_render_gate.py:212-213` for the text-extraction sibling
shape):
```python
        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)
```
adapt to the embedded-image idiom (not text) per RESEARCH.md's Code Examples:
```python
        reader = pypdf.PdfReader(str(pdf_output))
        extracted_sizes = {
            image_file.image.size
            for page in reader.pages
            for image_file in page.images
            if image_file.image is not None
        }
```

---

### `tests/test_builder.py` — new unit tests (unit, CRUD)

**Analog:** the two D-12-pinned tests in the SAME file, lines 392-459 — sit new tests beside them
WITHOUT editing either. Full file's import block (lines 1-9):
```python
"""
Tests for TypstBuilder class.
"""

import os
from pathlib import Path

from docutils import nodes
from sphinx.builders import Builder
```
(the two pinned tests additionally do local imports of `docutils.parsers.rst.states`,
`docutils.utils.Reporter`, and `typsphinx.builder.TypstBuilder` inside the test body itself — match
that local-import style for new tests, not a module-level import, since that is this file's existing
convention for test-scoped imports.)

**`temp_sphinx_app` fixture usage** (both pinned tests' signature) — this fixture is provided by
`conftest.py` per CLAUDE.md's Tests section; new tests should take it as their sole fixture parameter,
exactly as both pinned tests do: `def test_<new_name>(temp_sphinx_app): ...`.

**Fake-Sphinx-builder construction idiom to copy** (`test_post_process_images_rehomes_absolute_uri`,
lines 407-423 — hand-built doctree via `docutils.parsers.rst.states`/`Reporter`):
```python
    from docutils.parsers.rst import states
    from docutils.utils import Reporter

    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    abs_uri = os.path.join(builder.doctreedir, "images", "converted.png")

    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False

    img = nodes.image(uri=abs_uri, candidates={"*": abs_uri})
    doc += img

    builder.post_process_images(doc)

    assert img["uri"] == "images/converted.png"
    assert builder.images.get("images/converted.png") == abs_uri
```
**Adaptation needed for the D-01/D-03 srcdir-collision branch:** the new test must additionally
create a REAL file at `path.join(builder.srcdir, "images", "converted.png")` before calling
`post_process_images(doc)`, then assert `img["uri"] == "_typst_converted/images/converted.png"` and
`builder.images.get("_typst_converted/images/converted.png") == abs_uri` — i.e. the collision case is
this exact same scaffold plus one `Path(...).write_bytes(...)` line before the call, and a different
expected key after it.

**Simpler dict-only construction idiom to copy for the escape/`ValueError` branch**
(`test_copy_image_files_uses_override_source_for_absolute_uri`, lines 429-458 — no doctree needed,
sets `builder.images` directly, "namespace-agnostic" per D-12's own framing):
```python
    from typsphinx.builder import TypstBuilder

    app = temp_sphinx_app
    builder = TypstBuilder(app, app.env)
    builder.init()

    real_src_dir = Path(builder.doctreedir) / "images"
    real_src_dir.mkdir(parents=True, exist_ok=True)
    real_src_file = real_src_dir / "converted.png"
    real_src_file.write_bytes(b"converted image content")

    builder.images["images/converted.png"] = str(real_src_file)

    builder.copy_image_files()

    img_dest_file = Path(builder.outdir) / "images" / "converted.png"
    assert img_dest_file.exists()
    assert img_dest_file.read_bytes() == b"converted image content"
```
This is the right shape for a `copy_image_files()`-level test that the escape/relocation key (whatever
it resolves to) still lands `dest` under `outdir` — set `builder.images["_typst_converted/..."] = ...`
by hand and assert the destination path, without needing a full doctree.

**D-07 Windows cross-drive `ValueError` unit test** — no existing analog constructs a
`path.relpath()` `ValueError` directly (this is a genuinely new test shape); the closest structural
precedent is `_escapes_outdir()`'s own doctest-style `Examples:` block (builder.py lines 86-94), which
enumerates boundary-shape inputs one assertion at a time — a new unit test can `monkeypatch` or
directly call the guard logic with an absolute URI on a different "drive" is not reproducible on POSIX
CI, so per RESEARCH.md's Pitfall 4 framing, the more portable unit-test route is to assert the
`try/except ValueError` clause's OUTCOME (relocation under the reserved namespace + warning) by mocking
`os.path.relpath` to raise `ValueError`, rather than by constructing genuinely different drive letters.

## Shared Patterns

### Logger usage (module-level, all warnings)
**Source:** `typsphinx/builder.py:25` (`logger = logging.getLogger(__name__)`) and the module's
existing `logger.warning(f"...")` call sites (e.g. lines 828-831, 1116, 1128).
**Apply to:** the new D-06 warning in `_track_image()` — single f-string, no multi-line format,
naming the offending value in the message body (matches every existing warning in this file).

### Sphinx invocation in tests: `sys.executable -m sphinx`, never a console-script shim
**Source:** every render-gate test module in `tests/` (`_run_sphinx_build_typstpdf()` helper,
duplicated per-module, not centralized in `conftest.py`).
**Apply to:** the new render-gate test module — copy the helper function verbatim (module-local, not
shared), per this repo's own established (if slightly repetitive) convention.

### `@pytest.mark.skipif` availability guards (`TYPST_AVAILABLE`, `PYPDF_AVAILABLE`)
**Source:** `tests/test_abbr_pep_separator_render_gate.py:44-56`, `tests/test_absolute_image_render_gate.py:44-49`.
**Apply to:** the new render-gate module's class-level and pypdf-test-level skip guards.

### Fixture-directory `pytest.fixture` returning `Path(__file__).parent / "fixtures" / "<name>"`
**Source:** both render-gate analogs' `<name>_render_gate_dir` fixture (e.g.
`tests/test_absolute_image_render_gate.py:67-70`).
**Apply to:** the new fixture's directory-path fixture, named to match the new fixture directory.

## No Analog Found

None — every new file this phase creates has a close, recently-modified analog already identified
above. RESEARCH.md's own "Don't Hand-Roll" table independently confirms the same conclusion at the
mechanism level (path-escape detection, PDF embedded-image extraction, fake-converter fixture
construction all reuse existing code/patterns).

## Metadata

**Analog search scope:** `typsphinx/builder.py` (full file read this session, offsets 28-138,
764-964, 1092-1162, 494-564); `tests/test_builder.py` (full-file grep + offsets 1-40, 380-459);
`tests/test_absolute_image_render_gate.py` (full file, 201 lines); `tests/test_abbr_pep_separator_render_gate.py`
(full file, 241 lines); `tests/fixtures/absolute_image_render_gate/conf.py` and `index.rst` (full
files) and its `_static/` directory listing.
**Files scanned:** 6 read in full or targeted sections, plus a repo-wide grep for
`typstpdf`/`@pytest.mark.slow`/`typst.compile`/`pypdf.PdfReader` across `tests/*.py` to confirm
`test_abbr_pep_separator_render_gate.py` as the most recent scaffolding precedent.
**Pattern extraction date:** 2026-08-14
