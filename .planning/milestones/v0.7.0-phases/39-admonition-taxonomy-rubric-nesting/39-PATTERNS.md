# Phase 39: Admonition Taxonomy + Rubric Nesting - Pattern Map

**Mapped:** 2026-08-02
**Files analyzed:** ~14 (2 source edit sites + ~12 new/edited test artifacts)
**Analogs found:** 14 / 14 (one explicit "no precedent" finding — see "No Analog Found")

This phase is source-light (two edit zones inside `typsphinx/translator.py`, one
`pyproject.toml` line) and test-heavy (new fixtures, new render-gate modules, a
non-pytest artifact script). Pattern mapping below is weighted accordingly.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `typsphinx/translator.py` — 13 `visit_X` call sites + `_visit_admonition`/`_depart_admonition` (bucket routing + catalog title) | translator/emitter | transform (docutils node → Typst text) | itself (pre-phase code, `translator.py:4337-4559`) — this is a data-table edit, not a new pattern | exact (edit-in-place) |
| `typsphinx/translator.py` — `visit_rubric`/`depart_rubric` slot rename (Fix A) | translator/emitter | transform | `visit_strong`/`depart_strong` (`translator.py:1429-1501`) — the body Fix A diverges from | exact |
| `pyproject.toml` `[project.optional-dependencies] dev` — add `pillow` | config | batch (dependency manifest) | the existing `dev` array itself (`pyproject.toml:34-47`, e.g. the `pypdf>=6.14,<7` line) | exact |
| NEW: `tests/test_admonitions.py` edits (rename+re-derive 4 of 18 assertions) | test (unit, in-process doctree) | transform | itself, pre-phase (`tests/test_admonitions.py:1-80` shown; full file 434 lines) | exact |
| NEW: `tests/test_topics.py` edits (2 of 3 assertions: `clue({` → `abstract({`) | test (unit, in-process doctree) | transform | itself, pre-phase (`tests/test_topics.py:1-60`) | exact |
| NEW: fixture dir for ADM-01/ADM-02 (`seealso`/`attention`/`danger` real-compile) | test fixture (`.typ`-string + compiled-PDF gate) | request-response (sphinx-build subprocess) | `tests/fixtures/topic_line_block_render_gate/` (admonition-sentinel shape) — closest existing admonition-bearing fixture; **no fixture with these 3 types exists** | role-match (no type-exact analog exists — confirmed by repo-wide grep) |
| NEW: `.typ`-string gate module for ADM-01/ADM-02 | test (real-compile, `.typ`-string assertion) | request-response | `tests/test_desc_content_indent_render_gate.py`'s `.typ`-text fixture half (session-scoped `_run_sphinx_build_typst` → text) | exact (structural shape) |
| NEW: compiled-PDF gate extension for ADM-01/ADM-02 | test (real-compile, PDF text-extraction) | request-response | `tests/test_pdf_render_gate.py::TestTopicLineBlockRenderGate::test_admonitiontitleregression_multichild` | exact |
| NEW: `.typ`-string assertion added to `topic_line_block_render_gate`-backed test, for ADM-03's `notify({` half | test (real-compile, `.typ`-string) | request-response | same `test_pdf_render_gate.py` module — needs a NEW `.typ`-text-reading test alongside the existing PDF-text one (see gap below) | role-match |
| NEW: `tests/test_rubric_indent_invariance.py` (ADM-05, `pypdf` x-position, `py:class::`+nested `py:method::`+rubric) | test (real-compile, `pypdf` geometry) | request-response | `tests/test_desc_content_indent_render_gate.py` (session-scoped `.typ`/PDF fixtures, `_find_page_and_column`/`_leading_columns` helpers) | exact |
| NEW: `tests/test_rubric_strong_nesting_render_gate.py` (D-13 classic RED: `strong`-in-`rubric` → `par()` drop) | test (real-compile, `.typ`-string) | request-response | `tests/test_desc_rubric_decoupling_render_gate.py` (rubric+bold real-compile shape, `_run_sphinx_build_typst` helper) | exact |
| EXTEND: `tests/test_rubric_propagated_target_render_gate.py` or `tests/test_desc_rubric_decoupling_render_gate.py` (D-11 double-blank-line wart — newline-count regex) | test (real-compile, regex/count assertion) | request-response | `tests/test_desc_rubric_decoupling_render_gate.py` itself | exact |
| REGENERATE: `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` | test fixture (golden byte-identity file) | file-I/O (committed artifact) | itself, pre-phase — `test_emitted_typ_is_byte_identical_to_golden` (same file, lines 262-296) | exact |
| NEW: greyscale render-and-desaturate script (ADM-04, Pillow, non-pytest) | utility (build/verification tooling script) | file-I/O (render → PNG artifact) | **none in this repo** — see "No Analog Found" | no analog |

## Pattern Assignments

### `typsphinx/translator.py` — bucket routing table edit (ADM-01/ADM-02/ADM-03/ADM-09/ADM-10, D-01..D-05)

**Analog:** the file's own pre-phase state (`typsphinx/translator.py:4337-4559`), already read in full above.

**Core pattern — the shared helper (unchanged plumbing, only call-site arguments move)** (`translator.py:4337-4399`):
```python
def _visit_admonition(
    self, node: nodes.Node, clue_type: str, custom_title: str = None
) -> None:
    self._emit_id_anchors(node)
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")
    self._pending_admonition_title = None
    self._custom_admonition_title = custom_title
    self.add_text(f"{clue_type}({{")

def _depart_admonition(self) -> None:
    self.add_text("}")
    title_expr = None
    if self._pending_admonition_title:
        title_expr = "{" + self._pending_admonition_title + "}"
    elif self._custom_admonition_title:
        title_expr = f'"{self._custom_admonition_title}"'
    if title_expr:
        self.add_text(f", title: {title_expr}")
    self.add_text(")\n\n")
    if self.in_list_item:
        self.list_item_needs_separator = True
```
RESEARCH.md's recommended shape centralizes the `admonitionlabels` lookup INSIDE this helper
(one edit, not 13) — see RESEARCH.md "Bucket Routing Table" code block, reproduced here as the
concrete edit target:
```python
from sphinx.locale import admonitionlabels

def _visit_admonition(self, node, clue_type, custom_title=None):
    ...
    default_title = admonitionlabels.get(node.__class__.__name__)
    if default_title is not None:
        custom_title = str(default_title)
    self._custom_admonition_title = custom_title
```

**Call-site pattern to copy per type (one-line `clue_type` argument change)**, e.g. `visit_seealso`
(`translator.py:4441-4444`, D-02 target):
```python
def visit_seealso(self, node: addnodes.seealso) -> None:
    """Visit a seealso admonition (converts to #info(title: "See Also")[])."""
    self._visit_admonition(node, "info", custom_title="See Also")
```
becomes (drop the now-dead `custom_title=` literal; the centralized catalog lookup supplies it):
```python
def visit_seealso(self, node: addnodes.seealso) -> None:
    self._visit_admonition(node, "tip")
```
Same one-line-argument-swap shape applies to `visit_danger` (`error`, D-03), `visit_attention`
(`error`, D-03), `visit_admonition` (`notify`, D-09), `visit_topic`'s non-contents branch
(`abstract`, D-10, `translator.py:4538-4559`).

**Escaping pattern (Pitfall 3 fix)** — `escape_typst_string` (`translator.py:32-63`) is the
project's single escaping helper; route the static-title branch through it:
```python
elif self._custom_admonition_title:
    title_expr = f'"{escape_typst_string(str(self._custom_admonition_title))}"'
```
No other admonition code changes; this is the ONE new leaf-emission call site this phase adds.

---

### `typsphinx/translator.py` — `visit_rubric`/`depart_rubric` slot rename (D-11/D-13, Fix A)

**Analog:** `visit_strong`/`depart_strong` (`translator.py:1429-1501` — read in full above via the
`visit_rubric` verbatim-copy docstring, which names it as the copy source).

**Pattern:** Fix A renames ONLY the three assignment lines in `visit_rubric`
(`translator.py:~5828-5830`) and the three `hasattr`/restore blocks in `depart_rubric`
(`~5859-5873`) from `_strong_was_*` to `_rubric_was_*`. `visit_strong`/`depart_strong` and
`visit_desc_signature`/`depart_desc_signature` are NOT touched — this is the load-bearing
constraint (Phase 37's `desc_signature` golden file is a fixed point; Phase 36 D-02's shared-name
triplication stays intact for the other two handlers).

```python
# visit_rubric — only these three lines change:
self._rubric_was_in_paragraph = was_in_paragraph
self._rubric_was_in_list_item = was_in_list_item
self._rubric_was_list_item_needs_separator = was_list_item_needs_separator

# depart_rubric — only these three hasattr/restore blocks change name:
if hasattr(self, "_rubric_was_in_paragraph"):
    self.in_paragraph = self._rubric_was_in_paragraph
    delattr(self, "_rubric_was_in_paragraph")
if hasattr(self, "_rubric_was_in_list_item"):
    self.in_list_item = self._rubric_was_in_list_item
    delattr(self, "_rubric_was_in_list_item")
if hasattr(self, "_rubric_was_list_item_needs_separator"):
    if self.in_list_item:
        self.list_item_needs_separator = True
    delattr(self, "_rubric_was_list_item_needs_separator")
```
Emitted bytes for `strong({...})` open/close are unchanged — verified against
`test_rubric_option_concat_render_gate.py`'s literal-lock comment ("Left byte-identical on
purpose; do not migrate this lookup").

---

### `pyproject.toml` `[project.optional-dependencies] dev` — add `pillow`

**Analog:** the array's own existing entries (`pyproject.toml:34-47`).

```toml
dev = [
    "pytest>=8.4,<10",
    ...
    "pypdf>=6.14,<7",
    "pillow>=11,<13",   # NEW — D-07, gated behind checkpoint:human-verify (SUS Package Legitimacy verdict)
]
```
Same array, same bound style (`>=`/`<` pair) as `pypdf`/`mypy`/etc. No new `[project.dependencies]`
entry — this stays dev-only (milestone invariant #1).

---

### `tests/test_admonitions.py` — 4 assertion + name edits (D-02/D-03/D-09, in-process unit tests)

**Analog:** the file itself (pre-phase, `tests/test_admonitions.py:1-80` read above; full 434-line
structure confirmed by RESEARCH.md's line-by-line census).

**Fixture-construction pattern to keep unchanged** (shared by every test in this file):
```python
def create_document():
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False
    return doc

# per-test:
node = nodes.seealso()  # or danger()/attention()/admonition()
para = nodes.paragraph(text="...")
node += para
doc = create_document()
doc += node
writer = TypstWriter(temp_sphinx_app.builder)
writer.document = doc
translator = TypstTranslator(doc, temp_sphinx_app.builder)
doc.walkabout(translator)
output = translator.astext()
assert "tip({" in output   # was "info({"
```

**Four RED-today assertions to re-derive by hand (D-14 — never copy failing output)**, per
RESEARCH.md's exact line map:
| Test (rename target) | Old assertion | New assertion |
|---|---|---|
| `test_seealso_converts_to_info_with_title` → e.g. `test_seealso_converts_to_tip_with_title` | `"info({" in output`, `', title: "See Also"' in output` | `"tip({" in output`, `', title: "See also"' in output` (D-05 lowercase "a") |
| `test_danger_converts_to_danger` → `test_danger_converts_to_error` | `"danger({" in output` | `"error({" in output` |
| `test_attention_converts_to_warning` → `test_attention_converts_to_error` | `"warning({" in output` | `"error({" in output` |
| `test_generic_admonition_converts_to_clue` → `test_generic_admonition_converts_to_notify` | `"clue({" in output` | `"notify({" in output` |

The other 13 assertions in this file stay green untouched (bucket unchanged, English title
byte-identical) — do not edit them.

---

### `tests/test_topics.py` — 2 of 3 assertions (D-10)

**Analog:** the file itself (`tests/test_topics.py:1-60` read above).

Same fixture-construction idiom as `test_admonitions.py` (the file's own docstring says so
explicitly: "Mirrors tests/test_admonitions.py's construction idiom exactly"). Two edits:
```python
# lines 59, 90 (both currently `assert "clue({" in output`):
assert "abstract({" in output
# line 134 (box-less .. contents:: control) — UNCHANGED, remains:
assert "clue({" not in output
```

---

### NEW fixture: ADM-01/ADM-02 real-compile gate (`seealso`/`attention`/`danger`)

**Analog:** `tests/fixtures/topic_line_block_render_gate/index.rst` — the closest existing
admonition-sentinel fixture (`SENTINEL` naming convention, one admonition type per subsection,
`.. admonition:: Custom *Title*` block at the end). No existing fixture contains `seealso`,
`attention`, or `danger` (confirmed by repo-wide grep in RESEARCH.md).

**Fixture directory shape to copy** (from `tests/fixtures/desc_rubric_decoupling_render_gate/`,
the minimal fixture-dir layout):
```
tests/fixtures/<new_name>_render_gate/
    conf.py       # project/author/release + extensions=["typsphinx"] + typst_documents=[(...)]
    index.rst     # sentinel-bearing content
```
`conf.py` pattern (`tests/fixtures/desc_rubric_decoupling_render_gate/conf.py`, full text read
above):
```python
project = "..."
author = "typsphinx tests"
release = "0.0.0"
extensions = ["typsphinx"]
typst_documents = [
    ("index", "index", "...", "typsphinx tests"),
]
```
`index.rst` sentinel pattern (from `topic_line_block_render_gate/index.rst`):
```rst
.. seealso::

   SEEALSOSENTINEL body text.

.. attention::

   ATTENTIONSENTINEL body text.

.. danger::

   DANGERSENTINEL body text.
```

---

### NEW `.typ`-string gate module + compiled-PDF gate extension for ADM-01/ADM-02/ADM-03

**Analog A (`.typ`-string real-compile gate structure):**
`tests/test_desc_content_indent_render_gate.py`'s session-scoped `.typ`-text fixture (lines ~140-175
read above):
```python
@pytest.fixture(scope="session")
def <name>_typ_text(<name>_gate_dir, tmp_path_factory):
    build_dir = tmp_path_factory.mktemp("<name>_typ") / "_build"
    result = _run_sphinx_build_typst(<name>_gate_dir, build_dir)
    assert result.returncode == 0, (
        f"sphinx-build -b typst failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    index_typ = build_dir / "index.typ"
    assert index_typ.exists(), "index.typ was not generated"
    return index_typ.read_text(encoding="utf-8")
```
Then assert directly: `assert "tip({" in typ_text` (seealso), `assert typ_text.count("error({") >= 2`
(attention+danger), `assert "notify({" in typ_text` (ADM-03 half).

**Analog B (compiled-PDF sentinel gate structure):**
`tests/test_pdf_render_gate.py::TestTopicLineBlockRenderGate::test_admonitiontitleregression_multichild`
(read in full above) — same session-scoped PDF-bytes fixture → `pypdf` text extraction → sentinel
`assert "...SENTINEL" in full_text` pattern, PLUS the `LEAK_SIGNATURES` negative-control loop:
```python
for leaked_token in LEAK_SIGNATURES:
    assert leaked_token not in full_text, (
        f"Literal Typst source '{leaked_token}' leaked into rendered PDF text -- ..."
    )
```
`LEAK_SIGNATURES` is defined once near the top of `test_pdf_render_gate.py` (paragraph-call/
text-call/raw-call open-paren forms) — reuse the SAME constant, do not redefine it.

**subprocess invocation pattern (mandatory — CLAUDE.md NixOS guidance), copy verbatim from either
analog:**
```python
def _run_sphinx_build_typst(source_dir: Path, build_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typst", str(source_dir), str(build_dir)],
        capture_output=True, text=True,
    )
```
Never bare `sphinx-build` / `uv run sphinx-build` — every render-gate module in this repo restates
this exact rationale in its own docstring.

**`slow` marker usage:** none of the read analogs apply a class-level `pytest.mark.slow` — the
`TYPST_AVAILABLE`/`PYPDF_AVAILABLE` `skipif` guard on the compiled-PDF-only test class is the
actual gating mechanism used throughout this repo (see `test_desc_rubric_decoupling_render_gate.py`'s
`@pytest.mark.skipif(not TYPST_AVAILABLE, ...)` on its compile-sanity leg). Follow that skipif
convention, not a `slow` marker, for the new compiled-PDF classes — `slow` is reserved in this repo
for the network-dependent full-corpus gate (`tests/test_corpus_gate.py`), per RESEARCH.md's own
"Sampling Rate" section.

---

### NEW `tests/test_rubric_indent_invariance.py` (ADM-05, `pypdf` x-position, D-12 invariance guard)

**Analog:** `tests/test_desc_content_indent_render_gate.py` (full geometry-measurement toolkit read
above, lines 1-260+).

**CRITICAL correction to CONTEXT.md/RESEARCH.md's stated measurement technique:** both upstream
documents describe the x-position method as pypdf's `visitor_text` callback reading `cm[4] + tm[4]`.
The actual, only precedent in this codebase (`test_desc_content_indent_render_gate.py`'s own
docstring, verified by grep across the whole `tests/` tree — zero other hits for `visitor_text`)
states plainly: **`visitor_text` reports `x=0, y=0` on this project's compiled PDFs and is
unusable.** The established, working technique is `extraction_mode="layout"` text reconstruction
+ leading-whitespace column counting:
```python
def _layout_lines(pdf_bytes: bytes, page_index: int) -> str:
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    return _strip_zwsp(reader.pages[page_index].extract_text(extraction_mode="layout"))

def _leading_columns(layout_text: str, marker_substring: str) -> int:
    for line in layout_text.splitlines():
        if marker_substring in line:
            return len(line) - len(line.lstrip(" "))
    raise AssertionError(f"{marker_substring!r} not found in the given page's layout text")

def _find_page_and_column(pdf_bytes: bytes, marker_substring: str, start_page: int = 0) -> tuple:
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    for i in range(start_page, len(reader.pages)):
        layout_text = _layout_lines(pdf_bytes, i)
        if marker_substring in layout_text:
            return i, _leading_columns(layout_text, marker_substring)
```
Use RELATIVE column comparisons (`==` between two markers' columns), never a pinned point value —
`_leading_columns` returns a character-column count, not a PDF-point x-coordinate; CONTEXT.md's
measured `70.87pt`/`98.37pt`/`125.87pt` table is evidence the property holds, not a value to
re-assert literally in this new test. The `ZWSP`-stripping helper (`_strip_zwsp`, module-level, one
line) must be copied too — other fixtures compiled in the same pytest process may leave ZWSP
residue per that module's own comment.

**Fixture shape:** a new small local `tests/fixtures/<name>/index.rst` with `py:class::` containing
nested `py:method::`, each carrying `.. rubric::`, mirroring CONTEXT.md's own measurement probe —
no autodoc/napoleon wiring needed (RESEARCH.md Open Question 2 recommends the hand-authored shape,
same node structure either way).

---

### NEW `tests/test_rubric_strong_nesting_render_gate.py` (D-13 classic RED)

**Analog:** `tests/test_desc_rubric_decoupling_render_gate.py` (`.typ`-string real-compile gate,
full structure read above) — specifically its `_run_sphinx_build_typst` helper and its
`golden.typ`-adjacent fixture-dir convention (though this new test does NOT need a golden file —
it needs a single positive string assertion).

**Fixture:** `.. rubric:: A **bold** rubric` immediately followed by an ordinary paragraph.

**Assertion (from RESEARCH.md D-13, GATE-01 RED Design table):**
```python
assert 'par({text("First paragraph after the rubric.")})' in typ_text
```
RED today (emits bare `text(...)` instead of `par({...})`); GREEN once Fix A (`_rubric_was_*`
rename) lands.

---

### EXTEND `tests/test_rubric_propagated_target_render_gate.py` or `tests/test_desc_rubric_decoupling_render_gate.py` (D-11 wart)

**Analog:** `tests/test_desc_rubric_decoupling_render_gate.py` — its fixture (`index.rst`, read in
full above) ALREADY contains the exact "rubric with a propagated target inside a list item" shape:
```rst
* First bullet text.

  .. _decoupling-rubric-in-list-target:

  .. rubric:: A Rubric In A List Item

  More text after the rubric.
```
Add a regex/count assertion on the emitted `.typ` text counting the newline run between the
anchor's close and the rubric's `strong({` open (currently 3, target 1) — do not create a new
fixture; extend the existing one, per RESEARCH.md's explicit recommendation.

**Also required (same plan, same commit):** regenerate `golden.typ` for
`test_desc_rubric_decoupling_render_gate.py::test_emitted_typ_is_byte_identical_to_golden` — this
IS an expected, in-scope byte change (D-11's fix touches the exact shape this golden file locks),
not a regression to chase. Hand-verify the new golden content per D-14's "never by copying failing
output" rule — do not `cp` the fixed code's own emitted `index.typ` over `golden.typ` without
reading the diff.

## Shared Patterns

### Real-compile subprocess invocation (every new/edited render-gate module)
**Source:** `tests/test_desc_rubric_decoupling_render_gate.py:63-104` (canonical form, restated
identically in `tests/test_desc_content_indent_render_gate.py` and `tests/test_pdf_render_gate.py`)
**Apply to:** every new fixture-driving test in this phase
```python
def _run_sphinx_build_typst(source_dir: Path, build_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typst", str(source_dir), str(build_dir)],
        capture_output=True, text=True,
    )

def _run_sphinx_build_typstpdf(source_dir: Path, build_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typstpdf", str(source_dir), str(build_dir)],
        capture_output=True, text=True,
    )
```
`sys.executable -m sphinx` — never bare `sphinx-build`/`uv run sphinx-build` (NixOS PATH-shadowing
hazard, CLAUDE.md/project memory).

### Optional-dependency skip guard
**Source:** every render-gate module in this repo (`test_desc_rubric_decoupling_render_gate.py:9-13`)
**Apply to:** any new class requiring `typst`/`pypdf`/`pillow`
```python
try:
    import typst
    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False
```
then `@pytest.mark.skipif(not TYPST_AVAILABLE, reason="typst-py is required for the compile-sanity leg")`
on the class or test. Apply the same pattern for a new `PILLOW_AVAILABLE` guard if the ADM-04
render script is wrapped in a pytest test (it is NOT required to be — see "No Analog Found" below).

### String-literal escaping (Pitfall 3)
**Source:** `typsphinx/translator.py:32-63` (`escape_typst_string`)
**Apply to:** the `_depart_admonition` static-title branch — the phase's one new leaf-emission site.
No other admonition/rubric code needs this; do not introduce a second escaping routine.

### Golden-file byte-identity gate
**Source:** `tests/test_desc_rubric_decoupling_render_gate.py::test_emitted_typ_is_byte_identical_to_golden`
(lines 262-296)
**Apply to:** the D-11 wart's expected `golden.typ` change (regenerate + hand-verify, not blind-copy)
```python
assert actual_typ == golden_typ, (
    "Emitted .typ differs from the committed golden ...\n"
    + "\n".join(difflib.unified_diff(
        golden_typ.splitlines(), actual_typ.splitlines(),
        fromfile="golden.typ", tofile="actual index.typ", lineterm="",
    ))
)
```

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| ADM-04 greyscale render-and-desaturate script (Pillow, `typst.compile(format="png")` → `Image.convert("L")`) | utility (build/verification tooling) | file-I/O (produces a committed PNG artifact) | **No precedent exists in this repo for a script or test that writes a committed binary/image artifact.** Repo-wide check: no `.png`/`.jpg`/binary artifact is committed anywhere under `.planning/` today (searched `tests/fixtures/` and `.planning/phases/*/`); every existing "artifact" this project commits under `.planning/` is a `.md` file. This is genuinely new infrastructure — RESEARCH.md's "Code Examples" section supplies the only available reference shape (a plain function, `render_admonition_greyscale(typ_path, ppi, out_png) -> Path`), not a codebase analog. The planner should treat this as a standalone script (not shoehorned into pytest's assertion model, since ADM-04 is `[V]`-manual-only per REQUIREMENTS.md's own legend — no automated assertion is possible or expected) and pick its own naming/location convention (Claude's Discretion per CONTEXT.md), suggested `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-GREYSCALE.png` alongside a small driver script under the same phase directory or `scripts/`. |

## Metadata

**Analog search scope:** `typsphinx/translator.py` (full read of both edit zones);
`tests/test_admonitions.py`, `tests/test_topics.py`, `tests/test_pdf_render_gate.py` (targeted
reads); `tests/test_desc_rubric_decoupling_render_gate.py` (full, 350 lines);
`tests/test_desc_content_indent_render_gate.py` (first 260 lines — geometry-measurement toolkit);
`tests/fixtures/desc_rubric_decoupling_render_gate/` (full, all 3 files);
`tests/fixtures/topic_line_block_render_gate/index.rst` (full); `pyproject.toml` (dev-extra
section); repo-wide grep for `visitor_text`/`cm[4]`/committed binary artifacts.
**Files scanned:** ~10 test modules, 2 fixture directories, 1 source file (2 zones), 1 config file.
**Pattern extraction date:** 2026-08-02
