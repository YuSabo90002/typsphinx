# Phase 11: Issue #114 Fatal Fixes + Graceful-Degrade Net - Pattern Map

**Mapped:** 2026-07-12
**Files analyzed:** 2 modified + 4 new (translator.py, test_pdf_render_gate.py, 3 new fixture dirs)
**Analogs found:** 6 / 6 (single-file phase; every analog lives inside `typsphinx/translator.py`
itself or its sibling test/fixture files — no cross-module search was needed)

All line numbers below were re-confirmed by direct `Read` in this session (not carried forward
blind); they match the RESEARCH.md citations exactly.

## File Classification

| New/Modified Symbol / File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `_convert_length_to_typst()` (new method in `typsphinx/translator.py`) | utility (pure transform) | transform | `_compute_relative_image_path()` (`translator.py:1748-1775+`) | exact — same file, same "docstring+doctest, pure string helper called from a visit_* method" shape |
| `visit_caption`/`depart_caption`/`depart_figure` buffer-swap (modify `translator.py:1163-1227`) | translator visitor (state machine) | transform / deferred-emission | `visit_title`/`depart_title` admonition branch (`translator.py:190-238`) | exact — identical buffer-swap idiom already proven in this file |
| `visit_image` width/height emission (modify `translator.py:1527-1533`) | translator visitor | transform | current buggy code itself (`translator.py:1527-1533`) — being replaced by calls into `_convert_length_to_typst()` | exact (direct replacement) |
| `visit_reference` refid fallback branch (modify `translator.py:1970-1996`, insert before line 1976) | translator visitor | request-response (URL resolution) | the existing `#`-prefixed internal-label branch at `translator.py:1989-1992` in the same method | exact — same method, symmetric branch |
| `_visit_graphical_placeholder()` shared helper + `visit_graphviz`/`visit_inheritance_diagram` (new, near `translator.py:2483`) | translator visitor (event-driven degrade) | event-driven / graceful-degrade | `visit_index` (`translator.py:2483-2489`, `raise nodes.SkipNode`) for the skip idiom; `unknown_visit` (`translator.py:2038-2049`) for the "log a warning" idiom | role-match (skip idiom exact; warning-emission idiom exact; combined behavior is new) |
| New test classes in `tests/test_pdf_render_gate.py` (`TestFigureLengthRenderGate`, `TestFigureCaptionRenderGate`, `TestGraphvizDegradeRenderGate`) | test (integration, real-compile) | request-response (subprocess → compile → extract) | `TestAdmonitionPdfRenderGate` (`tests/test_pdf_render_gate.py:61-134`, the whole existing class) | exact — this is the file's only existing gate class, explicitly designated in CONTEXT.md as the D-04 pattern to extend |
| New fixture dirs: `tests/fixtures/figure_length_render_gate/`, `tests/fixtures/figure_target_caption_render_gate/`, `tests/fixtures/graphviz_degrade_render_gate/` | config (Sphinx fixture project) | file-I/O | `tests/fixtures/admonition_render_gate/{conf.py,index.rst}` | exact — minimal `conf.py` + `index.rst` shape to clone |

## Pattern Assignments

### `_convert_length_to_typst()` (new helper, place near `_compute_relative_image_path`, translator.py ~1748)

**Analog:** `_compute_relative_image_path` (`typsphinx/translator.py:1748-1775`)

**Docstring/doctest convention to copy** (lines 1748-1776):
```python
def _compute_relative_image_path(
    self, image_uri: str, current_docname: str | None
) -> str:
    """
    Compute relative path for image() function.

    Adjusts image URIs from source-root-relative to output-file-relative.
    This is similar to _compute_relative_include_path() but for images.

    Args:
        image_uri: Image URI from Sphinx (source-root-relative)
        current_docname: Current document name (e.g., "chapter1/section1")

    Returns:
        Adjusted relative path for Typst image()

    Examples:
        >>> _compute_relative_image_path("images/logo.png", "chapter1/section1")
        "../images/logo.png"
        >>> _compute_relative_image_path("images/logo.png", "index")
        "images/logo.png"
        >>> _compute_relative_image_path("images/logo.png", None)
        "images/logo.png"

    Notes:
        This implements Issue #69 fix for nested document image paths.
        Uses the same logic as _compute_relative_include_path() from Issue #5.
    """
```
Copy this exact shape (Args/Returns/Examples/Notes docstring sections, type-annotated signature
using `str | None`, not `Optional[str]` — matches the file's modern-3.12 style already used at line
86: `str | List[str] | None`). Place `_convert_length_to_typst()` as a sibling private method; call
it from `visit_image` at both the width and height call sites (replacing lines 1527-1533).

`re` is already imported at line 8 — no new import needed for the length regex.

**Imports pattern** (top of file, lines 8-16 — nothing new required):
```python
import re
from typing import Any, List

from docutils import nodes
from sphinx import addnodes
from sphinx.util import logging
from sphinx.util.docutils import SphinxTranslator

logger = logging.getLogger(__name__)
```

---

### `visit_image` — replace fatal verbatim width/height emission

**Current buggy code being replaced** (`typsphinx/translator.py:1527-1533`):
```python
        # Add optional attributes
        if "width" in node:
            width = node["width"]
            self.add_text(f", width: {width}")

        if "height" in node:
            height = node["height"]
            self.add_text(f", height: {height}")
```
Replace both branches with calls to `self._convert_length_to_typst(node["width"])` /
`self._convert_length_to_typst(node["height"])`, emitting `, width: {converted}` / `, height:
{converted}` only when the helper returns non-`None` (drop the attribute entirely on `None`, per D-02).
Rest of `visit_image` (lines 1501-1526, 1535-1546, including `_compute_relative_image_path` call and
the `in_figure` indentation branch) is unchanged.

---

### `visit_caption` / `depart_caption` / `depart_figure` — buffer-swap fix

**Analog:** `visit_title`/`depart_title` admonition branch (`typsphinx/translator.py:190-238`) — the
proven buffer-swap idiom already in this exact file.

**Buffer-swap precedent to mirror** (lines 205-212, `visit_title`):
```python
        # Admonition titles are deferred: buffer-swap the body so the title's
        # inline children render through the normal visitors (preserving
        # emphasis/literal/etc.) without touching the main output stream.
        if isinstance(node.parent, nodes.Admonition):
            self._saved_body_for_admonition_title = self.body
            self.body = []
            self._in_admonition_title = True
            return
```
**Restore-and-capture precedent** (lines 229-235, `depart_title`):
```python
        if self._in_admonition_title:
            self._pending_admonition_title = "".join(self.body)
            if self._saved_body_for_admonition_title is not None:
                self.body = self._saved_body_for_admonition_title
            self._saved_body_for_admonition_title = None
            self._in_admonition_title = False
            return
```
**Init-state precedent to mirror for the new figure-caption variable** (lines 93-100, `__init__`):
```python
        # Admonition title state (buffer-swap idiom, mirrors definition-list terms)
        self._pending_admonition_title: str | None = (
            None  # Rendered inline content of a dynamic (node-derived) title
        )
        self._in_admonition_title: bool = (
            False  # Track if currently buffering an admonition title node
        )
        self._saved_body_for_admonition_title: List[Any] | None = (
```
Add a new `self._saved_body_for_figure_caption: List[Any] | None = None` state var right after this
block (or near the existing `self.figure_caption = ""` at line 49), naming it symmetrically.

**Current buggy code being replaced** (`typsphinx/translator.py:1201-1227`):
```python
    def visit_caption(self, node: nodes.caption) -> None:
        """
        Visit a caption node.

        Handles captions for both figures and code blocks (Issue #20).

        Args:
            node: The caption node
        """
        # For captioned code blocks, caption is already extracted in visit_container
        # We should skip output to avoid duplicate caption text
        if self.in_captioned_code_block:
            raise nodes.SkipNode
        # For figures, start collecting caption text
        self.in_caption = True

    def depart_caption(self, node: nodes.caption) -> None:
        """
        Depart a caption node.

        Args:
            node: The caption node
        """
        # Store caption text for figures
        if self.in_figure:
            self.figure_caption = node.astext()
        self.in_caption = False
```
Fix: in `visit_caption`, after the existing `in_captioned_code_block` `SkipNode` guard, add `if
self.in_figure:` buffer-swap (`self._saved_body_for_figure_caption = self.body; self.body = []`)
before setting `self.in_caption = True`. In `depart_caption`, replace `self.figure_caption =
node.astext()` with `self.figure_caption = "".join(self.body)` plus the restore-`self.body` dance,
guarded by `if self.in_figure:`.

**`depart_figure` — code-mode wrapping change** (current, `typsphinx/translator.py:1179-1199`,
specifically line 1188):
```python
    def depart_figure(self, node: nodes.figure) -> None:
        """
        Depart a figure node.

        Args:
            node: The figure node
        """
        # Close the figure
        if self.figure_caption:
            self.add_text(f",\n  caption: [{self.figure_caption}]")
```
**Critical fix required here too:** line 1188 currently wraps `self.figure_caption` in `[...]`
(markup-mode brackets) — but once the buffer-swap fix is applied, `self.figure_caption` holds
*rendered code-mode output* (`text("...")` function-call source, produced by the buffer-swap
routing captions through `visit_Text`/`visit_emphasis` etc., the same as `_pending_admonition_title`
does for admonition titles — see `_visit_admonition`/`_depart_admonition` around line 2292 for how
that buffered content is consumed as a code-mode argument elsewhere in the file). This must become
`caption: {{{self.figure_caption}}}` (a `{...}` code block, matching RESEARCH.md Pattern 1's explicit
instruction), NOT `[{self.figure_caption}]` — using `[...]` here would reproduce the exact v0.5.0
admonition bug class (printing `text(...)` calls as literal markup instead of evaluating them).

---

### `visit_reference` — add `refid` fallback branch (FIG-02 `:target:` internal-doc support)

**Analog:** the existing `#`-prefixed internal-reference branch inside the same method
(`typsphinx/translator.py:1989-1992`).

**Full current context to modify** (`typsphinx/translator.py:1969-1996`):
```python
        # Get the reference URI
        refuri = node.get("refuri", "")

        # Handle empty URLs (Typst 0.14+ rejects empty URLs)
        # This can occur with unresolved references, broken cross-references,
        # or malformed reStructuredText. Instead of generating invalid link("", ...),
        # we skip the link wrapper and render content as plain text.
        if not refuri:
            logger.warning(
                f"Reference node has empty URL. "
                f"Link will be rendered as plain text. "
                f"Check for broken references in source: {node.astext()}"
            )
            self._skip_link_wrapper = True
            return

        # Determine if we need # prefix (in markup mode)
        prefix = "#" if self._in_markup_mode else ""

        # Check if it's an internal reference (starts with #)
        if refuri.startswith("#"):
            # Internal reference to a label
            label = refuri[1:]  # Remove the #
            self.add_text(f"{prefix}link(<{label}>, ")
        else:
            # External reference (HTTP/HTTPS URL or relative path)
            self.add_text(f'{prefix}link("{refuri}", ')
```
Insert a `refid` fallback check between the `refuri = node.get("refuri", "")` line and the
`if not refuri:` empty-URL guard:
```python
        refuri = node.get("refuri", "")
        refid = node.get("refid", "")

        if not refuri and refid:
            prefix = "#" if self._in_markup_mode else ""
            self.add_text(f"{prefix}link(<{refid}>, ")
            if self._in_markup_mode:
                self._in_markup_mode = False
            self._in_link = True
            self._link_has_content = False
            self.list_item_needs_separator = was_list_item_needs_separator
            return

        if not refuri:
            ...  # existing empty-URL branch unchanged
```
Note the `#`-prefixed branch at line 1991 (`label = refuri[1:]`) does zero sanitization of `label`
before interpolation — the new `refid` branch should follow the same convention (`refid` values are
docutils-generated ids, already label-safe; no `.replace()` needed).

**State vars this branch must set, matching the "after markup-mode link()" bookkeeping done later in
this method** (context beyond the excerpted range, `translator.py:1997-2036` — the `_in_link`,
`_link_has_content`, and `list_item_needs_separator` restoration already exist as method-wide state;
the new early-return branch must replicate that bookkeeping inline since it returns before reaching
the shared code at the bottom of the method).

---

### `_visit_graphical_placeholder()` + `visit_graphviz` / `visit_inheritance_diagram` (new, DEG-01/02)

**Analog 1 — the "raise SkipNode, no depart needed" idiom** (`typsphinx/translator.py:2483-2493`):
```python
    def visit_index(self, node: addnodes.index) -> None:
        """
        Visit an index node.

        Index entries are skipped in Typst/PDF output as we don't generate indices.
        """
        raise nodes.SkipNode

    def depart_index(self, node: addnodes.index) -> None:
        """Depart an index node."""
        pass
```

**Analog 2 — the "log a warning" idiom** (`typsphinx/translator.py:2038-2049`, `unknown_visit`):
```python
    def unknown_visit(self, node: nodes.Node) -> None:
        """
        Handle unknown nodes during visit.

        Args:
            node: The unknown node
        """
        # Log a warning for unknown nodes but don't raise an exception
        from sphinx.util import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"unknown node type: {node}")
```
Note: the module already has a module-level `logger = logging.getLogger(__name__)` at line 16 — the
new `_visit_graphical_placeholder()` helper should use that existing module-level `logger`, not
re-import/re-instantiate `logging.getLogger` locally as `unknown_visit` redundantly does.

**Recommended new code** (place near `visit_index`, in the "API description nodes" /
out-of-scope-node neighborhood starting at line 2480):
```python
    def _visit_graphical_placeholder(self, node: nodes.Node, node_label: str) -> None:
        """
        Shared graceful-degrade helper for out-of-scope graphical nodes
        (graphviz, inheritance_diagram). Emits a visible bordered placeholder
        block naming the node type (D-01), logs exactly one warning, and
        skips the node's children -- never descends into raw DOT source /
        diagram spec attributes.
        """
        logger.warning(
            f"{node_label} is not supported in Typst output; rendering placeholder"
        )
        self.add_text(
            f'rect(text("[{node_label} diagram omitted]"), '
            f"stroke: 0.5pt, inset: 8pt, radius: 2pt)\n\n"
        )
        raise nodes.SkipNode

    def visit_graphviz(self, node: nodes.Node) -> None:
        self._visit_graphical_placeholder(node, "graphviz")

    def visit_inheritance_diagram(self, node: nodes.Node) -> None:
        self._visit_graphical_placeholder(node, "inheritance diagram")
```
**Verify-before-writing note (carried from RESEARCH.md Assumption A1, unresolved — planner/executor
must confirm):** the exact node class names registered by `sphinx.ext.graphviz` /
`sphinx.ext.inheritance_diagram` were not independently re-verified against the installed Sphinx
package source in this pattern-mapping pass either. First implementation step should be a throwaway
`.. graphviz:: digraph { a -> b }` + `inheritance-diagram::` fixture built with the *unmodified*
translator; `unknown_visit`'s own `logger.warning(f"unknown node type: {node}")` (line 2049) will
print the exact class name/repr needed to confirm `visit_graphviz`/`visit_inheritance_diagram` are
the correct method names before relying on them.

**Anti-pattern explicitly forbidden here (per D-01, locked):** do NOT reuse `_visit_admonition` /
gentle-clues `clue`/`note`/`warning` functions for this placeholder — visual confusion with real
admonitions is explicitly disallowed.

---

### `tests/test_pdf_render_gate.py` — extend with three new test classes

**Analog:** the entire existing `TestAdmonitionPdfRenderGate` class (`tests/test_pdf_render_gate.py:61-134`).

**Full reusable scaffold to clone per new fixture** (imports/availability guards, lines 1-40):
```python
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

LEAK_SIGNATURES = ("par({", 'text("', 'raw("')
```
**Fixture-plumbing pattern to replicate per new fixture dir** (lines 43-58):
```python
@pytest.fixture
def fixtures_dir():
    """Return the path to tests/fixtures/ directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def admonition_render_gate_dir(fixtures_dir):
    """Return the path to the admonition_render_gate fixture project."""
    return fixtures_dir / "admonition_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"
```
Add sibling fixtures: `figure_length_render_gate_dir`, `figure_target_caption_render_gate_dir`,
`graphviz_degrade_render_gate_dir`, each `fixtures_dir / "<name>"`.

**Full test-method pattern to clone (subprocess → compile → pypdf → assert), lines 61-134:**
```python
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the D-04 render gate",
)
class TestAdmonitionPdfRenderGate:
    """
    Real-compile acceptance gate for the admonition markup/code-mode fix.

    Requirements: D-04 (08.1-RESEARCH.md, 08.1-VALIDATION.md).
    """

    def test_admonition_pdf_has_no_literal_source_leak(
        self, admonition_render_gate_dir, temp_build_dir
    ):
        """
        Compile the admonition render-gate fixture to PDF and confirm the
        extracted text contains typeset prose, not literal Typst source.
        """
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "sphinx",
                "-b",
                "typst",
                str(admonition_render_gate_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"

        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(index_typ), output=str(pdf_output))

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into rendered "
                "PDF text -- admonition markup/code-mode mismatch regression"
            )
```
Each new class (`TestFigureLengthRenderGate`, `TestFigureCaptionRenderGate`,
`TestGraphvizDegradeRenderGate`) follows this exact skeleton — same `@pytest.mark.skipif` guard, same
`subprocess.run([sys.executable, "-m", "sphinx", "-b", "typst", ...])` invocation (never shell out to
a bare `uv run sphinx-build`; see the in-code comment at lines 80-92 explaining the PATH-shadowing
hazard this avoids), same `typst.compile()` → `pypdf.PdfReader` → text-extraction chain. Vary only:
the fixture dir fixture, the specific assertions (caption exact-once-count via `full_text.count(...)`
for `TestFigureCaptionRenderGate`; converted-pt-value / absence-of-raw-unit-string checks for
`TestFigureLengthRenderGate`; placeholder-wording-present + raw-DOT-absent checks plus a
`caplog`-based single-warning assertion for `TestGraphvizDegradeRenderGate`).

Per D-04/CONTEXT.md: apply `@pytest.mark.slow` to the new classes (note this marker is **not**
currently used anywhere in the test suite — it is registered in `pyproject.toml`'s markers list but
applied nowhere yet; adding it here is a new but explicitly-sanctioned precedent, not a deviation).

---

### New fixture directories — clone the `admonition_render_gate` shape

**Analog:** `tests/fixtures/admonition_render_gate/{conf.py,index.rst}` (full contents read this
session).

**`conf.py` pattern to clone** (full file, `tests/fixtures/admonition_render_gate/conf.py`):
```python
# Sphinx configuration for the D-04 admonition render-gate fixture.
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove the admonition markup/code-mode fix in a real compile: sphinx-build
# -> typst.compile() -> pypdf text-extraction, asserting no literal Typst
# source (par(/text(/raw() leaks into rendered admonition prose.

project = "Admonition Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template plus the gentle-clues @preview import -- included
# documents only get a minimal import set (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Admonition Render Gate", "Test Author"),
]
```
For `graphviz_degrade_render_gate/conf.py`, add `"sphinx.ext.graphviz"` and
`"sphinx.ext.inheritance_diagram"` to the `extensions` list (both bundled with Sphinx core per
RESEARCH.md — no new dependency). The other two new fixtures (`figure_length_render_gate`,
`figure_target_caption_render_gate`) need no extra extensions beyond `"typsphinx"`.

**`index.rst` pattern** — the existing file is a flat sequence of section + directive pairs, each
section demonstrating one case (see full content read above: Golden Note, Note With A Bullet List,
Warning With A Literal Block, Hint Type, Danger Type, Nested Admonition). Clone this
"one section per case" structure:
- `figure_length_render_gate/index.rst`: one `.. figure::`/`.. image::` block per unit case
  (`200px`, `50%` width-only, `3em`, bare unitless, `2in`, one unknown unit e.g. `1ex`).
- `figure_target_caption_render_gate/index.rst`: one figure with an external `:target:` URL and a
  caption containing `` _ * ` [ ] ``, one figure with an internal `:target:` label reference and the
  same stress caption.
- `graphviz_degrade_render_gate/index.rst`: one `.. graphviz:: digraph { a -> b }` block and one
  `.. inheritance-diagram::` block (needs an actual importable class for
  `inheritance-diagram::` to target — the fixture's `conf.py`/`index.rst` will need a minimal
  in-fixture Python class or reference to a stdlib class rather than importing anything real from
  typsphinx itself, to keep the fixture self-contained).

## Shared Patterns

### Buffer-swap (defer rendered content to a later named argument)
**Source:** `typsphinx/translator.py:190-238` (`visit_title`/`depart_title`, admonition branch) —
also see the definition-list term buffer-swap using `self.saved_body` (line 89) as a second, older
instance of the same idiom in this file.
**Apply to:** `visit_caption`/`depart_caption`/`depart_figure` (FIG-02).
**Rule:** never use `node.astext()` for anything that must reach a named Typst argument
(`caption:`/`title:`) later — always swap `self.body` to `[]`, let children render through the
normal visitor chain, `"".join(self.body)` to capture, then restore `self.body`. Wrap the restored
buffer in `{...}` (code block) at the consumption site, never `[...]` (markup block).

### Log-and-skip for out-of-scope nodes
**Source:** `typsphinx/translator.py:2483-2489` (`visit_index`, `raise nodes.SkipNode`) combined
with `typsphinx/translator.py:2038-2049` (`unknown_visit`'s `logger.warning` idiom).
**Apply to:** `visit_graphviz`/`visit_inheritance_diagram` (DEG-01/02), via the new shared
`_visit_graphical_placeholder()` helper — extends the log+skip idiom with a visible placeholder,
which neither existing precedent does alone.

### Real-compile acceptance gate (sphinx-build → typst.compile() → pypdf)
**Source:** `tests/test_pdf_render_gate.py:61-134` (`TestAdmonitionPdfRenderGate`, the entire class).
**Apply to:** all three new GATE-01 test classes; reuse `LEAK_SIGNATURES`, the `TYPST_AVAILABLE`/
`PYPDF_AVAILABLE` skipif guard, the `sys.executable -m sphinx` subprocess-invocation convention (do
not shell out to a bare `uv run sphinx-build` — see the PATH-shadowing hazard documented in the
existing test's comment, lines 80-92), and the `admonition_render_gate/{conf.py,index.rst}` fixture
shape for the three new fixture directories.

## No Analog Found

None. Every symbol in this phase's scope maps to a concrete existing analog inside this same file (or
its sibling test/fixture files) — this is expected for a phase explicitly scoped as "apply patterns
this exact codebase already proved correct" (RESEARCH.md's own framing).

## Metadata

**Analog search scope:** `typsphinx/translator.py` (single file, ~2793 lines, read via targeted
non-overlapping `Read` calls at lines 1-100, 185-244, 1160-1240, 1495-1550, 1745-1780, 1925-2000,
2035-2065, 2478-2498); `tests/test_pdf_render_gate.py` (134 lines, read in full);
`tests/fixtures/admonition_render_gate/{conf.py,index.rst}` (read in full).
**Files scanned:** 3 (translator.py, test_pdf_render_gate.py, admonition_render_gate fixture pair)
**Pattern extraction date:** 2026-07-12

## PATTERN MAPPING COMPLETE
