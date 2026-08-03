# Phase 40: Citations — Full Round Trip - Pattern Map

**Mapped:** 2026-08-02
**Files analyzed:** 6 (2 modified source-adjacent surfaces, 2 new test artifacts, 2 restored sample files; ROADMAP.md wording change tracked separately, not pattern-mapped)
**Analogs found:** 6 / 6

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `typsphinx/translator.py` — new `visit_citation`/`depart_citation` (run-scoped grid) | translator node-handler (Body-level block) | transform (doctree → Typst source, single pass) | `_visit_admonition`/`_depart_admonition` (`typsphinx/translator.py:4343-4426`) | exact (structural precedent, explicitly named by RESEARCH over the footnote handlers) |
| `typsphinx/translator.py` — new `visit_label` (or positional skip) for the citation's `label` child | translator node-handler (Inline/text, but structurally the citation's own first child) | transform | `visit_footnote_reference`'s `footnote_node.children[1:]` positional-skip idiom (`typsphinx/translator.py:2597-2600`) | role-match (mechanism only — footnote skips its `label` child positionally rather than via a real handler; same shape applies here) |
| `typsphinx/translator.py` — guarded addition inside `visit_reference` (D-14 citing-site anchor) | translator node-handler (Inline, hot path) | transform | `visit_reference`/`depart_reference` itself (`typsphinx/translator.py:3819-4031`), plus `next_is_target` sibling-lookahead idiom (`typsphinx/translator.py:3892-3898`) and the `[#... <label>]` bracket-wrap (`depart_term`, `typsphinx/translator.py:2249-2270`) | exact (same function, guarded addition — not a new handler) |
| `tests/test_citation_render_gate.py` (new) | test (pytest module, real-compile render gate) | request-response (subprocess `sphinx-build` invocation → structural + compiled-PDF assertions) | `tests/test_confval_field_body_render_gate.py` (RED→GREEN shape) + `tests/test_cross_doc_label_namespace_render_gate.py` (2-doc namespacing proof shape) | exact (RESEARCH names both explicitly; this module is a fusion of the two) |
| `tests/fixtures/citation_render_gate/` (new) | config/fixture (Sphinx mini-project: `conf.py` + `.rst` sources) | file-I/O (read by `sphinx-build` subprocess) | `tests/fixtures/cross_doc_label_namespace_render_gate/` (2-doc layout: `conf.py`, `index.rst`, `pagea.rst`, `pageb.rst`) | exact (RESEARCH's Wave 0 gaps require 2 documents — same shape) |
| `examples/charged-ieee/{approach1,approach2}/source/index.rst` | content (Sphinx source, restoration) | file-I/O (verbatim revert) | commits `8bed1a3` / `c014a0b` (the exact removal diffs) applied in reverse | exact (this IS the analog — a literal `git revert`-shaped diff, not a pattern to imitate) |
| `.planning/ROADMAP.md` SC#3 wording | config/docs | transform (prose edit) | Phase 36 SC#3 correction / Phase 39 D-12 (same "amend the criterion against measurement, record in Roadmap Evolution" convention) | role-match (process precedent, not code) |

## Pattern Assignments

### `typsphinx/translator.py` — `visit_citation`/`depart_citation` (new, Body-level, run-scoped)

**Analog:** `_visit_admonition`/`_depart_admonition` (`typsphinx/translator.py:4343-4426`)

**Structural open/close pattern to copy (read, adapt — NOT copy verbatim, per RESEARCH: citation is RUN-scoped, admonition is per-node):**
```python
# Source: typsphinx/translator.py:4343-4373 (existing, verified this session)
def _visit_admonition(
    self, node: nodes.Node, clue_type: str, custom_title: str = None
) -> None:
    # A propagated explicit target can land its id on this node; anchor it so
    # a same-document link(<id>, ...) resolves (no ids -> no-op).
    self._emit_id_anchors(node)

    # Add newline separator if in list item and not first element
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")

    ...
    # Open code-mode content-block (NOT markup-mode "[") so the body
    # evaluates in the translator's unified code mode.
    self.add_text(f"{clue_type}({{")

def _depart_admonition(self) -> None:
    self.add_text("}")
    ...
    self.add_text(")\n\n")
    if self.in_list_item:
        self.list_item_needs_separator = True
```

**Run-scoped adaptation required (per RESEARCH's Architecture Patterns § Pattern 1):**
- `visit_citation` must check whether the previous sibling is also a `citation` node — if so, do
  **not** re-open `grid(...)`, just start emitting the current row's two cells.
- `depart_citation` must check whether the next sibling is also a `citation` node — if so, do **not**
  close the grid yet; a `,` row-continuation follows.
- Use the `next_is_target`-style sibling-lookahead idiom (below) for both checks —
  `node.parent.index(node)` then bounds-checked `±1` into `node.parent.children`.

**Sibling-lookahead idiom to copy verbatim (already proven in this file):**
```python
# Source: typsphinx/translator.py:3892-3898 (existing, visit_reference)
next_is_target = False
if node.parent:
    node_index = node.parent.index(node)
    if node_index + 1 < len(node.parent.children):
        next_node = node.parent.children[node_index + 1]
        if isinstance(next_node, nodes.target):
            next_is_target = True
```
Adapt: replace `nodes.target` with `nodes.citation`, and mirror the same shape with `node_index - 1`
for the previous-sibling check in `visit_citation`.

**Anchor-before-open pattern (`_emit_id_anchors`) — read for the propagated-target precedent, but
D-13 requires the citation's OWN definition anchor to be `_namespace_label`-derived from
`node["docname"]`, not from `_current_docname()`, and to be attached via the label-attachment
bracket-wrap (Pattern 2 below), not via the `_emit_id_anchors` zero-width-metadata mechanism** (that
helper is for *propagated* targets landing on a node that already anchors itself another way — see
its own docstring, `typsphinx/translator.py:400-420`, describing the analogous `depart_figure` case).

---

### `typsphinx/translator.py` — `visit_label` (or positional skip) for the citation's `label` child

**Analog:** `visit_footnote_reference`'s positional child-skip (`typsphinx/translator.py:2597-2600`)

```python
# Source: typsphinx/translator.py:2597-2600 (existing, verified this session)
# Body sourced via buffer-swap through the normal visitor chain (D-02), never
# node.astext() -- skip only the footnote node's leading `label` child by
# position (D-06/14-RESEARCH.md Pitfall 3).
for child in footnote_node.children[1:]:
    child.walkabout(self)
```
CONTEXT.md's "Claude's Discretion" section explicitly frames this as a choice between a real
`visit_label` handler (fires for citations only, since `visit_footnote` raises `SkipNode` and never
reaches its own `label` child) and a positional skip identical in shape to the footnote's
`children[1:]` slice. Either is structurally sound per RESEARCH's Open Question 2 — pick one and keep
it consistent with however `visit_citation` iterates the citation's paragraph body.

---

### `typsphinx/translator.py` — guarded addition inside `visit_reference` (D-14)

**Analog:** `visit_reference`/`depart_reference` themselves (`typsphinx/translator.py:3819-4031`), the
`next_is_target` bracket-wrap branch inside the SAME function, and `depart_term`'s bracket-wrap anchor.

**The existing `next_is_target` markup-mode bracket-wrap branch — this is the closest in-function
precedent for "wrap the whole `link(...)` expression and attach a `<label>` postfix":**
```python
# Source: typsphinx/translator.py:3893-3907 (existing, verified this session)
next_is_target = False
if node.parent:
    node_index = node.parent.index(node)
    if node_index + 1 < len(node.parent.children):
        next_node = node.parent.children[node_index + 1]
        if isinstance(next_node, nodes.target):
            next_is_target = True

# If next is target, wrap in markup mode for label attachment
# In unified code mode, labels can only attach in markup mode blocks [...]
if next_is_target:
    self.add_text("[")
    self._in_reference_with_target = True
    self._in_markup_mode = True
```

**`depart_term`'s bracket-wrap anchor (the OTHER precedent for "attach `<label>` to buffered content
via `[#{...} <label>]`"):**
```python
# Source: typsphinx/translator.py:2249-2270 (existing, verified this session) —
# read the full depart_term body for the exact bracket-wrap emission shape;
# mirrors visit_title/depart_title's anchor pattern (Phase 11 precedent) —
# never `+`-join a bare label(...) onto content.
```

**D-14 guard to add (per RESEARCH's Architecture Diagram):** if `node["ids"]` is non-empty (verified
this session: only citation-derived references carry populated `ids`; a `:ref:` or toctree-generated
reference carries `ids=[]`), bracket-wrap the whole existing `link(...)` call and attach
`<{docname}:{ids[0]}>` (routed through `_namespace_label`/`_sanitize_label`, namespaced by the CITING
document — this is the citing site's own anchor, distinct from the definition's) so the
back-reference side of the round trip has a target. **Non-regression must be proven, not assumed** —
the full-corpus `-b typstpdf` gate (`tests/test_corpus_gate.py -m slow`) is the evidence D-14 requires,
because `visit_reference` is the hot path for every link in the codebase.

**Doctree evidence discriminating citation-derived references from ordinary ones (real
`env.get_and_resolve_doctree` dump, this session — use as fixture design reference):**
```
reference ids= []      refid= sec2            refuri= None                text= Section Two          # :ref: to a section
reference ids= ['id1']  refid= krizhevsky2012  refuri= None                text= [Krizhevsky2012]     # same-doc citing site
reference ids= ['id3']  refid= None            refuri= second.typ#same2020 text= [Same2020]           # cross-doc citing site
reference ids= []      refid= None             refuri= second.typ          text= Second Document       # toctree-generated ref
```

---

### `typsphinx/translator.py` — label namespacing (D-13, no new code — reuse only)

**Analog:** `_namespace_label`/`_sanitize_label` (`typsphinx/translator.py:3576-3600` docstring region,
`_sanitize_label` staticmethod at `3519-3567`)

```python
# Source: typsphinx/translator.py:3519-3567 (existing, verified this session) — sanitizer
@staticmethod
def _sanitize_label(name: str) -> str:
    return re.sub(
        r"[^A-Za-z0-9_.:-]",
        lambda m: f"_u{ord(m.group(0)):x}_",
        name,
    )
```
```python
# Source: typsphinx/translator.py:3576+ (existing, verified this session) — namespacer
def _namespace_label(self, docname: str | None, raw_id: str) -> str:
    """Namespace a docutils id/name by its owning document, then sanitize."""
    ...
```
**D-13 requires every new label this phase emits to route through these unchanged**, namespaced by
the **citation node's own `node["docname"]`** (Sphinx adds this attribute to `citation` nodes) — never
`self._current_docname()`. This is load-bearing for D-10 (duplicate-key-across-two-documents
correctness): using `node["docname"]` makes `index:same2020`/`second:same2020` correct by
construction, not by the coincidence that a definition's own docname usually matches the current one.

---

### `tests/test_citation_render_gate.py` (new)

**Analog 1 — the RED→GREEN real-compile gate shape:** `tests/test_confval_field_body_render_gate.py:111-192`

```python
# Source: tests/test_confval_field_body_render_gate.py:111-137 (existing, verified this session)
def test_typstpdf_concats_collapsed_field_body_and_produces_pdf(
    self, confval_field_body_render_gate_dir, temp_build_dir
):
    result = _run_sphinx_build_typstpdf(
        confval_field_body_render_gate_dir, temp_build_dir
    )
    assert result.returncode == 0, (
        f"sphinx-build -b typstpdf failed:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "expected semicolon or line break" not in result.stderr, (...)
    assert "Typst compilation failed" not in result.stderr, (...)

    typ_output = temp_build_dir / "index.typ"
    assert typ_output.exists(), "index.typ was not emitted"
    typ_text = typ_output.read_text(encoding="utf-8")
    # ... structural .typ-string assertions ...

    pdf_output = temp_build_dir / "index.pdf"
    assert pdf_output.exists(), (...)
    assert pdf_output.stat().st_size > 0, "PDF file is empty"
    with open(pdf_output, "rb") as f:
        magic = f.read(4)
        assert magic == b"%PDF", "Generated file is not a valid PDF"
```
This is the exact "the SAME test, run against the SAME fixture, fails today and passes after the
handler lands" shape RESEARCH's GATE-01 RED capture section names — CIT-01's test must mirror it,
NOT the `TestPreFixBasisFailureProof` durable-mechanical-reconstruction pattern in
`tests/test_typst_elements_pass_through_gate.py` (explicitly flagged as the wrong shape).

**Analog 2 — the 2-document namespacing proof + `/Annots`/`visitor_text` readback shape:**
`tests/test_cross_doc_label_namespace_render_gate.py` (full module read this session)

Key techniques to copy for CIT-04 (back-references) and D-13 (namespacing):
- Grep both emitted `.typ` files for the exact namespaced label strings and assert equality between
  a citing site's link target and the target document's own anchor label (never assert against a
  hard-coded guess — see RESEARCH Pitfall 3 on duplicate-key resolution direction).
- Negative guard: assert the WRONG same-slug local anchor is never the one a cross-document reference
  points at.
- Drives `-b typstpdf`, not `-b typst` — the label-uniqueness/compile fatal only fires inside
  `TypstPDFBuilder.finish()`'s `typst.compile()` call.

**Shared subprocess/fixture helpers to copy verbatim (present near-identically in every render-gate
module in this suite):**
```python
# Source: tests/test_cross_doc_label_namespace_render_gate.py:66-92 (existing, verified this session)
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

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``) so
    the exact interpreter/venv running this test is reused, sidestepping the
    documented NixOS-sandbox PATH-shadowing hazard.
    """
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typstpdf",
         str(source_dir), str(build_dir)],
        capture_output=True,
        text=True,
    )


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the ... render gate",
)
class TestCitationRenderGate:
    ...
```
The `TYPST_AVAILABLE` import-guard block (`try: import typst ... except ImportError:
TYPST_AVAILABLE = False`) at the top of every render-gate module should be copied verbatim too.

**PDF structural read-back for CIT-02/CIT-04/CIT-06** — no existing module reads `/Annots` +
`visitor_text`'s `cm[4]`/`cm[5]` yet in this test suite (RESEARCH's probes were hand-run, not
committed as a test helper); the exact `pypdf` calls to use are given verbatim in `40-RESEARCH.md`
§ "Code Examples" (`extract_text(extraction_mode="layout")`, `page.get('/Annots')`,
`extract_text(visitor_text=...)` reading `cm[4]`/`cm[5]`, NOT `tm[4]`/`tm[5]`).

---

### `tests/fixtures/citation_render_gate/` (new)

**Analog:** `tests/fixtures/cross_doc_label_namespace_render_gate/` — directory layout:
```
tests/fixtures/cross_doc_label_namespace_render_gate/
├── conf.py
├── index.rst
├── pagea.rst
└── pageb.rst
```

**`conf.py` pattern to copy** (from `tests/fixtures/confval_field_body_render_gate/conf.py`, adapted
for a 2-doc `typst_documents` master):
```python
# Source: tests/fixtures/confval_field_body_render_gate/conf.py:29-38 (existing, verified this session)
project = "Confval Field Body Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() actually compiles it to PDF -- the only build path
# where the fatal is observable.
typst_documents = [
    ("index", "index", "Confval Field Body Render Gate", "Test Author"),
]
```
(Every fixture `conf.py` in this suite opens with a comment block explaining the root cause the
fixture reproduces — copy that documentation convention too.)

**Fixture content requirements (from `40-VALIDATION.md` Wave 0, not an existing analog — this
combination of scenarios is new):** 2 documents; a forward reference (definition after first use);
2+ citations of the same key (multi-backref D-03 shape + CIT-04 proof); a cross-document citation; a
duplicate key defined in both documents (D-10); an uncited definition (D-07); a citation run broken by
a non-citation sibling (D-06); a citation nested inside a `list_item` (SC#5 — RESEARCH's independently
reproduced "different failure mode" case, `label ... does not exist in the document`, distinct from
the top-level syntax fatal).

---

### `examples/charged-ieee/{approach1,approach2}/source/index.rst` (restoration)

**Analog:** the removal commits themselves, applied in reverse — `git show 8bed1a3` /
`git show c014a0b` (both read in full this session; diffs are byte-identical between the two
approaches except for the top-of-file RST comment wording, per D-12).

**Exact restoration diff (both files, per D-11/D-12 — verbatim, not expanded):**
1. Delete the 5-line "This sample intentionally carries no citations..." RST comment block at the
   top of the file (wording differs slightly between `approach1` and `approach2` pre-restoration;
   D-12 requires BOTH deleted so the files become byte-identical again).
2. Revert:
   ```diff
   -breakthrough success of AlexNet. Subsequent architectures such as
   +breakthrough success of AlexNet [Krizhevsky2012]_. Subsequent architectures such as
   ```
3. Restore the trailing section (removed by both commits identically):
   ```rst
   References
   ----------

   .. [Krizhevsky2012] Krizhevsky, A., Sutskever, I., & Hinton, G. E. (2012).
      ImageNet classification with deep convolutional neural networks.
      *Advances in neural information processing systems*, 25.
   ```

**Regression proof — no new test needed, re-run only:** `tests/test_examples_charged_ieee_gate.py`
(read in full this session). Its `_assert_no_warnings` helper is the load-bearing assertion:
```python
# Source: tests/test_examples_charged_ieee_gate.py:124-129 (existing, verified this session)
def _assert_no_warnings(result: subprocess.CompletedProcess) -> None:
    combined = result.stdout + result.stderr
    assert "WARNING" not in combined, (
        f"Expected zero warnings building the shipped sample:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
```
This fails pre-fix (2 unknown-node warnings for `citation`/`label`) and passes post-fix, doubling as
SC#5's separator-protocol proof on real shipped content — per RESEARCH, this file needs NO code
change, only a re-run after the `.rst` restoration.

---

### `.planning/ROADMAP.md` SC#3 wording (D-09)

**Analog (process precedent, not code):** Phase 36's SC#3 correction and Phase 39's D-12 — "amend the
criterion against measurement rather than waive it, with the change recorded in the Roadmap Evolution
section." Apply the same edit shape: replace "back-references to every citing location" with
same-document-scoped wording per D-08, and add a Roadmap Evolution entry recording why.

## Shared Patterns

### Label attachment bracket-wrap (`[#expr <label>]`)
**Source:** `depart_term` (`typsphinx/translator.py:2249-2270`), `visit_footnote_reference`'s
definition branch (`typsphinx/translator.py:2597-2609`), `visit_reference`'s `next_is_target` branch
(`typsphinx/translator.py:3900-3907`)
**Apply to:** every DEFINITION-side anchor this phase creates (the citation row's own anchor; the
D-14 citing-site anchor). A `<label>` used as a plain call ARGUMENT (`link(<label>, ...)`) needs no
bracket-wrap — only the ATTACHMENT postfix does.

### Buffer-swap body rendering (never `node.astext()`)
**Source:** `visit_footnote_reference` (`typsphinx/translator.py:2597-2626`) — save `self.body`,
swap to a fresh list, walk children, join, restore; also save/restore `in_paragraph` and
`paragraph_has_content` around the nested walkabout (established convention shared with
`visit_emphasis`/`visit_strong`/`visit_subscript`/`visit_superscript`).
**Apply to:** the citation definition's body cells (`visit_citation`/`depart_citation`'s row-body
rendering) — the SAME reason this matters for footnotes applies: a nested `paragraph` child
unconditionally resets both flags on depart, silently clobbering the outer separator state if not
saved/restored.

### Dangling-label guard (warn + skip, never emit a link to nothing)
**Source:** `visit_footnote_reference`'s dangling-refid guard (`typsphinx/translator.py:2565-2571`)
```python
if footnote_node is None:
    logger.warning(
        "Dangling footnote reference: refid=%r not found in document",
        refid,
    )
    raise nodes.SkipNode
```
**Apply to:** any citing reference whose `refid` cannot be resolved to a same-document citation
(mirrors the Security Domain § "Known Threat Patterns" entry in `40-RESEARCH.md`) — though note
Sphinx itself already warns and leaves such references unresolved before the translator runs in the
common case; this is a defensive mirror, not necessarily new dead code.

### List-item leading/trailing separator bookkeeping
**Source:** `_visit_admonition`/`_depart_admonition` (`typsphinx/translator.py:4365-4367, 4425-4426`)
```python
if self.in_list_item and self.list_item_needs_separator:
    self.add_text("\n")
...
if self.in_list_item:
    self.list_item_needs_separator = True
```
**Apply to:** `visit_citation`/`depart_citation` — needed for the SC#5 list-item-nested-citation
fixture (RESEARCH's Pitfall 2 case).

### Render-gate test module skeleton (import guard + fixtures + subprocess runner)
**Source:** identical boilerplate across `tests/test_confval_field_body_render_gate.py`,
`tests/test_cross_doc_label_namespace_render_gate.py`, and every other `*_render_gate.py` in
`tests/`: the `try: import typst / except ImportError: TYPST_AVAILABLE = False` guard, the
`temp_build_dir` fixture, `_run_sphinx_build_typstpdf`, and the `@pytest.mark.skipif(not
TYPST_AVAILABLE, ...)` class decorator.
**Apply to:** `tests/test_citation_render_gate.py` in full — copy this scaffolding verbatim rather
than reinventing it.

## No Analog Found

None. Every file in the known-targets list has at least a role-match analog; the two "new construct"
elements (the run-scoped grid layout and the `/Annots`+`visitor_text` PDF read-back for citations
specifically) are documented in `40-RESEARCH.md` § Code Examples as hand-verified probes rather than
existing test code, and are called out above rather than omitted.

## Metadata

**Analog search scope:** `typsphinx/translator.py` (full-file targeted reads via grep-located line
ranges); `tests/` (fixture directory listing + 3 render-gate modules read in full: confval field-body,
cross-doc namespace, charged-ieee examples gate); `examples/charged-ieee/` (restoration diffs pulled
via `git show` on commits `8bed1a3`/`c014a0b`); `.planning/phases/39-*` (GATE-EVIDENCE convention,
spot-checked).
**Files scanned:** 2 translator regions (~700 lines total via targeted offset/limit reads), 3 test
modules (read in full), 2 fixture directories (listed + `conf.py`/`index.rst` read), 2 git commits.
**Pattern extraction date:** 2026-08-02

## PATTERN MAPPING COMPLETE
