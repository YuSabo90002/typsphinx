# Phase 14: Footnotes (doctree pre-pass) - Pattern Map

**Mapped:** 2026-07-12
**Files analyzed:** 4
**Analogs found:** 4 / 4

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `typsphinx/translator.py` (add `visit_document` index, `visit_footnote`, `visit_footnote_reference`) | translator/visitor (part of a larger `NodeVisitor` subclass) | transform (doctree node → Typst text, buffer-swap + bracket-wrap) | `typsphinx/translator.py` itself: `visit_document`/`depart_document` (~175-197), `visit_figure`/`depart_figure` (~1286-1339, bracket-wrap-for-label idiom), `visit_caption`/`depart_caption` (~1341-1385, buffer-swap idiom), `visit_topic` (~2712-2725, buffer-swap + `SkipNode`-adjacent state pattern), `visit_literal` (~766-810, `SkipNode` + own-content emission idiom) | exact (same file, same class, directly analogous handler shapes already present) |
| `tests/test_footnotes.py` | test (unit) | transform (doctree fragment → translator output string) | `tests/test_topics.py`, `tests/test_line_blocks.py` | exact |
| `tests/test_pdf_render_gate.py` (add `TestFootnoteRenderGate`) | test (integration / real-compile gate) | request-response (sphinx-build → typst.compile() → pypdf text-extraction → assert) | `TestTopicLineBlockRenderGate` (~991-1120), `TestFigureCaptionRenderGate` (~302-363) | exact |
| `tests/fixtures/footnote_render_gate/{conf.py,index.rst}` | config + fixture doc | file-I/O (static Sphinx project consumed by render-gate test) | `tests/fixtures/topic_line_block_render_gate/{conf.py,index.rst}` | exact |

## Pattern Assignments

### `typsphinx/translator.py` — `visit_document` pre-pass index (D-01)

**Analog:** `typsphinx/translator.py:175-197` (existing `visit_document`/`depart_document`)

**Current code** (lines 175-197):
```python
def visit_document(self, node: nodes.document) -> None:
    """
    Visit a document node.

    Generates opening code block wrapper for unified code mode.

    Args:
        node: The document node
    """
    # Start code block for unified code mode (all content uses function syntax without # prefix)
    self.add_text("#{\n")

def depart_document(self, node: nodes.document) -> None:
    """
    Depart a document node.
    ...
    """
    # Close code block for unified code mode
    self.add_text("}\n")
```

**Pattern to apply:** insert the D-01 pre-pass **before** the existing `self.add_text("#{\n")` line, following the exact idiom RESEARCH.md's Code Examples section already worked out:
```python
self._footnote_index = {
    n["ids"][0]: n for n in self.document.traverse(nodes.footnote) if n.get("ids")
}
self._emitted_footnote_ids = set()  # D-03: tracks first-cite vs. reuse

self.add_text("#{\n")
```
Use `self.document`, not the `node` parameter (Pitfall 4). Initialize `self._footnote_index`/`self._emitted_footnote_ids` here — mirrors how other per-document state (`self.figure_content`, `self.list_stack`, etc.) is initialized in `__init__` rather than per-visit, but D-01 explicitly requires the traverse to happen inside `visit_document` (not `__init__`, since `self.document` isn't guaranteed populated at `__init__` time in the same way) — follow CONTEXT.md/RESEARCH.md literally.

---

### `typsphinx/translator.py` — `visit_footnote` (D-05, definition-node suppression)

**Analog:** `typsphinx/translator.py` — `visit_literal`'s `raise nodes.SkipNode` idiom (~805-810) and `visit_caption`'s `if self.in_captioned_code_block: raise nodes.SkipNode` early-skip (~1349-1352)

**Core pattern to copy** (skip-entirely idiom, `visit_literal` lines ~805-810):
```python
# Skip processing child text nodes (we already got the content)
raise nodes.SkipNode
```

**New code:**
```python
def visit_footnote(self, node: nodes.footnote) -> None:
    """Visit a footnote definition node (D-05).

    Emits nothing at the definition's natural (docutils) location -- the
    body is reached only via the D-01 pre-pass index + D-02 lazy render at
    the footnote_reference site. See 14-RESEARCH.md Verified Mechanism 2
    finding 5 for why definitions cannot be rendered in place.
    """
    raise nodes.SkipNode
```
No `depart_footnote` is needed (never reached — mirrors `depart_literal`, which is a documented no-op reachable only when `SkipNode` is NOT raised; here it should simply be omitted, since `SkipNode` in `visit_footnote` guarantees `depart_footnote` never fires).

---

### `typsphinx/translator.py` — `visit_footnote_reference` (D-02/D-03/D-06/D-08)

**Analog 1 — buffer-swap idiom:** `depart_caption` (~1369-1385):
```python
def depart_caption(self, node: nodes.caption) -> None:
    """..."""
    # Capture the buffered caption content and restore the main output
    # stream (buffer-swap idiom; never node.astext(), which bypasses the
    # escaping applied by the normal visitor chain and caused the
    # double-emission/juxtaposition fatal bug).
    if self.in_figure:
        self.figure_caption = "".join(self.body)
        if self._saved_body_for_figure_caption is not None:
            self.body = self._saved_body_for_figure_caption
        self._saved_body_for_figure_caption = None
    self.in_caption = False
```
and the `visit_caption` swap-in half (~1353-1361):
```python
if self.in_figure:
    self._saved_body_for_figure_caption = self.body
    self.body = []
```

**Analog 2 — bracket-wrap-for-label idiom:** `visit_figure`/`depart_figure` (~1286-1339):
```python
if node.get("ids"):
    self.add_text("[#figure(\n")
else:
    self.add_text("figure(\n")
...
if node.get("ids"):
    label = node["ids"][0]
    self.add_text(f"\n) <{label}>]\n\n")
else:
    self.add_text("\n)\n\n")
```
This is the exact precedent RESEARCH.md's locked emission mirrors: `[#footnote({...}) <fn-id>]` for the definition (bracket-wrapped, label-attached) vs. bare `footnote(<fn-id>)` for reuse (no bracket, label as call-argument — RESEARCH.md Verified Mechanism 1 finding 1).

**Analog 3 — separator convention:** `visit_emphasis`/`visit_strong`/`visit_literal` all open with:
```python
self._add_paragraph_separator()

if self.in_list_item and self.list_item_needs_separator:
    self.add_text("\n")
...
if self.in_list_item:
    self.list_item_needs_separator = True
```
(seen at `visit_strong` lines ~707-716 and ~761-767, `visit_literal` lines ~773-778 and ~800-802).

**New code:** the exact design RESEARCH.md's Code Examples section already verified end-to-end (17 real `typst.compile()` runs) — copy verbatim, adjusting only style to match this file's docstring conventions:
```python
def visit_footnote_reference(self, node: nodes.footnote_reference) -> None:
    """Visit a footnote_reference node (D-02/D-03/D-06/D-08).

    First reference to an id: buffer-swap-renders the footnote body
    (skipping its leading `label` child, D-06) and emits the
    bracket-wrapped, label-attached definition form
    `[#footnote({...}) <fn-id>]` -- the `<label>` markup-mode postfix
    requires the Phase 11 bracket-wrap idiom (mirrors visit_figure's
    `[#figure(...) <label>]`; 14-RESEARCH.md Verified Mechanism 1).

    Repeat reference to an already-emitted id: emits the bare reuse form
    `footnote(<fn-id>)` -- no bracket-wrap, since `<label>` used as a
    plain call ARGUMENT is a code-mode Label value, not markup-mode
    attachment syntax (14-RESEARCH.md Verified Mechanism 1 finding 1).

    Dangling refid (D-08): logs a warning and skips emitting anything --
    a `footnote(<missing-label>)` call for a label that was never
    attached is a FATAL Typst compile abort ("label `<..>` does not
    exist in the document"), not a cosmetic issue (14-RESEARCH.md
    Pitfall 1).

    The footnote_reference node's own child (docutils' rendered marker
    number, e.g. "1"/"2") is never rendered -- Typst supplies its own
    marker via footnote()'s auto-numbering (D-04, D-06).
    """
    refid = node.get("refid")
    footnote_node = self._footnote_index.get(refid)

    if footnote_node is None:
        logger.warning(
            "Dangling footnote reference: refid=%r not found in document", refid
        )
        raise nodes.SkipNode

    label = f"fn-{refid}"

    self._add_paragraph_separator()
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")

    if refid in self._emitted_footnote_ids:
        self.add_text(f"footnote(<{label}>)")
    else:
        self._emitted_footnote_ids.add(refid)
        saved_body = self.body
        self.body = []
        # D-06: skip the footnote node's own leading `label` child --
        # walk only the body children, through the normal visitor chain
        # (buffer-swap idiom; never node.astext() -- see depart_caption).
        for child in footnote_node.children[1:]:
            child.walkabout(self)
        body_content = "".join(self.body)
        self.body = saved_body
        self.add_text(f"[#footnote({{{body_content}}}) <{label}>]")

    if self.in_list_item:
        self.list_item_needs_separator = True

    raise nodes.SkipNode
```
No `depart_footnote_reference` is needed (SkipNode short-circuits it, same as `visit_literal`/`depart_literal`).

**Error handling / degrade pattern:** `logger.warning` + `raise nodes.SkipNode` on a bad/missing reference — same shape as the existing `logger` import at top of `translator.py` (`logger = logging.getLogger(__name__)`, line 15) already used elsewhere in the file's graceful-degrade net (Phase 11 DEG-01/02 precedent, not separately excerpted here since no other `logger.warning` call site was read this pass — CONTEXT.md/RESEARCH.md confirm the precedent exists).

---

### `tests/test_footnotes.py` (new unit-test module)

**Analog:** `tests/test_topics.py` (full file structure read; excerpt below), plus `tests/test_line_blocks.py` (same construction idiom, Phase 13 precedent).

**Module docstring + imports + helper pattern** (`tests/test_topics.py` lines 1-32):
```python
"""
Tests for topic node conversion to Typst (BLK-02).

Phase 13 Plan 01: covers D-02 (...), D-05 (...), D-06 (...), and the
Pitfall-1 fix (...).

Mirrors tests/test_admonitions.py's construction idiom exactly: build a
docutils doctree fragment via `nodes`, run the translator via
`doc.walkabout(translator)`, and assert on `translator.astext()`.
"""

from docutils import nodes
from docutils.parsers.rst import states
from docutils.utils import Reporter
from sphinx.testing.util import SphinxTestApp

from typsphinx.translator import TypstTranslator
from typsphinx.writer import TypstWriter


def create_document():
    """Helper function to create a minimal document with reporter."""
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False
    return doc


class TestTopicConversion:
    """Test `.. topic::` node conversion to a clue box (D-02)."""

    def test_topic_converts_to_clue_box(self, temp_sphinx_app: SphinxTestApp):
        """..."""
        topic = nodes.topic()
        title = nodes.title(text="A Topic Title")
        para = nodes.paragraph(text="Topic body text.")
        topic += title
        topic += para

        doc = create_document()
        doc += topic

        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)

        output = translator.astext()
        assert "clue({" in output
        assert ", title: {" in output
```

**Apply this pattern for each RESEARCH.md test-map row:**
- **index test** (`-k index`): build a `nodes.document` containing a `nodes.footnote(ids=["f1"])` with a `label` + `paragraph` child, `doc.walkabout(translator)`, then assert `translator._footnote_index == {"f1": <the footnote node>}` (built by `visit_document`).
- **skip test** (`-k skip`): a lone `footnote` node with no referencing `footnote_reference` — assert `translator.astext()` contains no leaked body text (D-09 allows silent drop) and the definition-location body never appears verbatim.
- **definition test** (`-k definition`): a `paragraph` containing a `footnote_reference(refid="f1")` followed by a `footnote(ids=["f1"])` with `label` + `paragraph("BODY")` children — assert output contains `footnote({` and `<fn-f1>` and the emitted body (`BODY`), and does NOT contain the `label` node's own marker text.
- **reuse test** (`-k reuse`): two `footnote_reference(refid="f1")` nodes citing the same id — assert the definition form appears exactly once (`output.count("footnote({") == 1` scoped to that id) and a second, bare `footnote(<fn-f1>)` call (no `{`) appears for the repeat.
- **dangling test** (`-k dangling`): a `footnote_reference(refid="missing")` with no matching `footnote` node anywhere — assert `nodes.SkipNode`-driven skip (no `footnote(` text emitted for it) and that a `logger.warning` fired (use `caplog` or monkeypatch `typsphinx.translator.logger.warning`).

Use `temp_sphinx_app` fixture (already provided by `conftest.py`, used by `test_topics.py`) for translator construction.

---

### `tests/test_pdf_render_gate.py` — new `TestFootnoteRenderGate` class

**Analog:** `TestTopicLineBlockRenderGate` (lines 991-1120+), including the shared class-scoped fixture that runs the real compile once per class (defined just above the class, not shown in this excerpt but present in the file — grep for `topic_line_block_render_gate_pdf_text` fixture definition immediately preceding line 991).

**Class structure pattern to copy** (from `TestTopicLineBlockRenderGate`, lines 991-1092+):
```python
class TestTopicLineBlockRenderGate:
    """
    Real-compile acceptance gate for BLK-02/BLK-03: ...

    Requirements: BLK-02, BLK-03, GATE-01 (13-CONTEXT.md D-01..D-06,
    13-RESEARCH.md Verified Mechanisms 1-3, 13-03-PLAN.md).

    All three test methods share the SAME real-compile artifact via the
    class-scoped `topic_line_block_render_gate_pdf_text` fixture above --
    sphinx-build/typst.compile() run exactly once per class, not once per
    test method.
    """

    def test_topic_and_contents_render_no_outline_leak(
        self, topic_line_block_render_gate_pdf_text
    ):
        """..."""
        full_text = topic_line_block_render_gate_pdf_text
        assert full_text.count("A Topic Title") == 1, (
            "Expected the topic title to appear exactly once ..."
        )
        assert TOPIC_BODY_SENTINEL in full_text, (
            f"Expected topic body sentinel '{TOPIC_BODY_SENTINEL}' in "
            "extracted PDF text -- visit_topic/depart_topic regression"
        )
    # ...more assertion methods, each ending with the shared
    # LEAK_SIGNATURES loop:
    for leaked_token in LEAK_SIGNATURES:
        assert leaked_token not in full_text, (
            f"Literal Typst source '{leaked_token}' leaked into "
            "rendered PDF text -- ... regression"
        )
```

**`LEAK_SIGNATURES` constant** (module-level, line 40, reuse unchanged):
```python
LEAK_SIGNATURES = ("par({", 'text("', 'raw("')
```

**New class, `TestFootnoteRenderGate`:** copy the class-scoped-fixture + multi-method shape exactly, mapping methods to CONTEXT.md's four SCs:
- `test_single_reference_footnote_renders_once` (SC#1): body sentinel present, `full_text.count(<body sentinel>) == 1`, no floating body left at the definition location (nothing appears twice).
- `test_double_reference_footnote_body_not_duplicated` (SC#2): two markers present (`full_text.count("1") ...` is unreliable — prefer checking a distinctive reference-site sentinel appears twice while the shared body sentinel's `.count(...) == 1`).
- `test_footnote_body_with_inline_markup_and_special_chars` (SC#3): emphasis/literal + `@ # $ _ * < >` sentinel text extracted correctly.
- `test_footnote_inside_list_item` (SC#4): list-item-cited footnote compiles and its body sentinel is present once.
- Each method ends with the `LEAK_SIGNATURES` negative-control loop (guards against `footnote({`/`text(`/`par({` leaking as literal prose — same idiom, adjust wording).

Also add the class-scoped pytest fixture immediately above the class (mirror the `topic_line_block_render_gate_pdf_text` fixture definition — grep the lines directly preceding 991 for its exact shape: `@pytest.fixture(scope="class")`, calls `_run_sphinx_build_typst(...)`, `pypdf.PdfReader(...).extract_text()`, and the `@pytest.mark.slow` / `@pytest.mark.skipif(not (TYPST_AVAILABLE and PYPDF_AVAILABLE), ...)` markers applied at class level, consistent with every other GATE-01 class in the file).

---

### `tests/fixtures/footnote_render_gate/{conf.py,index.rst}` (new fixture project)

**Analog:** `tests/fixtures/topic_line_block_render_gate/conf.py` and `index.rst` (full contents read).

**`conf.py` pattern to copy** (full file, `tests/fixtures/topic_line_block_render_gate/conf.py`):
```python
# Sphinx configuration for the BLK-02/BLK-03 topic+line_block render-gate
# fixture.
#
# Minimal self-contained project used by tests/test_pdf_render_gate.py to
# prove, in a real compile (sphinx-build -> typst.compile() -> pypdf text-
# extraction), that ... render correctly together ...

project = "Topic Line Block Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document (not merely an included one) so the writer
# emits the full template -- included documents only get a minimal import
# set (see typsphinx/writer.py).
typst_documents = [
    ("index", "index", "Topic Line Block Render Gate", "Test Author"),
]
```
For the new fixture: rename `project`/`typst_documents` title to `"Footnote Render Gate"`, keep the same `extensions`/`typst_documents` shape verbatim (single master document `index`).

**`index.rst` pattern to copy** (structural shape from `topic_line_block_render_gate/index.rst`): a top-level title, then a section per success criterion, each containing a distinctive ALLCAPS-no-space sentinel token (e.g. `FOOTNOTESINGLESENTINEL`, `FOOTNOTEDOUBLESENTINEL`, `FOOTNOTEMARKUPSENTINEL`, `FOOTNOTELISTSENTINEL`) so render-gate assertions can `count()` them unambiguously. Use real docutils footnote syntax (`.. [#name]` autonumbered footnote + `[#name]_` reference, or `.. [1]` manual + `[1]_`) for:
- a single-reference footnote (SC#1),
- a footnote referenced twice from two different paragraphs (SC#2),
- a footnote body containing `*emphasis*` / `` `literal` `` and markup-special characters `@ # $ _ * < >` (SC#3),
- a footnote referenced from inside a bullet-list item (SC#4).

RESEARCH.md's Wave 0 Gaps section confirms this exact combination of shapes was verified to compile cleanly this research session (t4/t5/t6/t7/t15) — the fixture RST should combine all four cases into one document, mirroring how `topic_line_block_render_gate/index.rst` combines BLK-02/BLK-03/SC#3 into one document with a section per concern.

## Shared Patterns

### Buffer-swap idiom (never `astext()`)
**Source:** `typsphinx/translator.py` `visit_caption`/`depart_caption` (~1341-1385), also `visit_title` (Phase 13, ~2660-2740 region)
**Apply to:** the D-02 lazy footnote-body render in `visit_footnote_reference` — save `self.body`, swap in `[]`, walk children via `child.walkabout(self)`, join, restore. Never `node.astext()` (bypasses escaping and caused a prior fatal bug per multiple docstrings in this file).

### Bracket-wrap-for-label idiom (Phase 11 precedent)
**Source:** `typsphinx/translator.py` `visit_figure`/`depart_figure` (~1286-1339)
**Apply to:** the D-03 definition-form emission (`[#footnote({...}) <fn-id>]`) — any markup-mode `<label>` attachment postfix under this translator's unified `#{ ... }` code-mode wrapper must be bracket-wrapped; a bare code-mode `<label>`-attachment statement is a Typst parse error that aborts the whole compile.

### Statement-separator convention
**Source:** `typsphinx/translator.py` `visit_emphasis`/`visit_strong`/`visit_literal` (~626-810), specifically the `self._add_paragraph_separator()` + `if self.in_list_item and self.list_item_needs_separator: self.add_text("\n")` opening pair and the `if self.in_list_item: self.list_item_needs_separator = True` closing line.
**Apply to:** both branches of `visit_footnote_reference`, before emitting either the definition or reuse form (verified necessary by RESEARCH.md's t8-fail/t9-fix).

### `SkipNode` short-circuit for "own content already emitted" nodes
**Source:** `typsphinx/translator.py` `visit_literal` (~805-810)
**Apply to:** `visit_footnote` (D-05, always skip) and `visit_footnote_reference` (D-02/D-03/D-08, always skip after emitting the Typst call or the dangling-refid warning) — no corresponding `depart_*` method is needed in either case.

### Graceful-degrade warn+skip net
**Source:** referenced by CONTEXT.md/RESEARCH.md as the Phase 11 DEG-01/02 precedent (module-level `logger = logging.getLogger(__name__)` at `typsphinx/translator.py:15`); not separately re-excerpted this pass since no other in-file `logger.warning` call site was read.
**Apply to:** D-08's dangling-refid case in `visit_footnote_reference` — `logger.warning(...)` naming the refid, then `raise nodes.SkipNode`, never a fatal.

### GATE-01 real-compile class fixture + `LEAK_SIGNATURES` negative control
**Source:** `tests/test_pdf_render_gate.py` module-level `LEAK_SIGNATURES = ("par({", 'text("', 'raw("')` (line 40) and every `Test*RenderGate` class's shared class-scoped fixture + per-method `for leaked_token in LEAK_SIGNATURES: assert leaked_token not in full_text` closing block.
**Apply to:** the new `TestFootnoteRenderGate` class — every test method should end with this same loop.

## No Analog Found

None — all four files in scope have exact analogs already present in the codebase from Phases 11-13.

## Metadata

**Analog search scope:** `typsphinx/translator.py` (single translator module — the phase's only source file), `tests/test_pdf_render_gate.py`, `tests/test_topics.py`, `tests/fixtures/topic_line_block_render_gate/`
**Files scanned:** 4 read directly (translator.py excerpts at multiple line ranges, test_pdf_render_gate.py excerpts, test_topics.py full, fixture conf.py + index.rst full) plus 1 directory listing (`tests/fixtures/`)
**Pattern extraction date:** 2026-07-12
</content>
