# Phase 38: Structural Indentation + Info Fields - Pattern Map

**Mapped:** 2026-08-01
**Files analyzed:** 1 modified source file (`typsphinx/translator.py`, ~8 handlers) + 4 test files
(1 new fixture family expected, 3 extended)
**Analogs found:** all handlers and all new-test shapes have an in-repo analog; no "no analog" entries

All line numbers below were re-read directly from the current tree this session (2026-08-01).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `typsphinx/translator.py` — `visit_desc_content`/`depart_desc_content` (5102-5110, currently `pass`) | translator node-handler (visitor pair) | transform (doctree node → Typst wrapper emission) | `visit_block_quote`/`depart_block_quote` (2920-2982) for the "wrap a run of code-mode body statements in a call taking a `{ … }` content block" shape | exact (same wrapping idiom, different call name) |
| `typsphinx/translator.py` — `visit_field_list`/`depart_field_list` (5332-5359) | translator node-handler | transform | itself (existing block-visitor separator pattern) + `visit_block_quote`'s `pad`-style wrap for the new indent step | exact |
| `typsphinx/translator.py` — `depart_desc` marker propagation (4798-4854) + `depart_desc_content` | translator node-handler | transform (break-suppression bookkeeping) | itself — the SIG-08 `_desc_break_marker` mechanism it must extend | exact (in-place extension, not a new pattern) |
| `typsphinx/translator.py` — `visit_field_body`/`depart_field_body` single-paragraph unwrap (5421-5464) | translator node-handler | transform | `visit_paragraph`'s existing `self.in_list_item` fast-path (800-837) — the precedent for "skip `par({`/`})`, let children dispatch inline" | exact — task guidance names this analog directly |
| `typsphinx/translator.py` — `visit_literal_strong`/`depart_literal_strong`, `visit_literal_emphasis`/`depart_literal_emphasis` (5745-5767, currently dummy-node delegation) | translator node-handler (leaf emission) | transform | `visit_literal`/`depart_literal` (1427-1522) for the `raw()` + `escape_typst_string` + `SkipNode` leaf shape | exact |
| `tests/fixtures/*_nesting_render_gate/index.rst` (new, IND-01..05 + FLD-01) | test fixture (Sphinx source) | request-response (subprocess build → compile → assert) | `tests/fixtures/signature_break_and_arrow_gate/index.rst` for the "one fixture, many labeled constructs, each with its own `.. defect case` / `.. CONTROL` docutils comment" convention | exact |
| `tests/test_*_indent_render_gate.py` (new, IND-01..05/FLD-01) | test (render-gate) | request-response | `tests/test_pdf_render_gate.py` (`_run_sphinx_build_typst` harness, 141-178) for the subprocess shape; `tests/test_signature_break_and_arrow_gate.py` for the "structural `.typ` assert + compiled-PDF layout-mode assert in the same module" split | exact |
| FLD-03 parametrized per-sub-part unit test (new) | test (unit, structural) | transform-assertion | `tests/test_signature_typography_gate.py` (`_expected_bold`/`_expected_italic`/`_slice`/`_extract_wrapped_call` hand-derivation helpers, 55-120) — the `test_sig04_*` family shape | exact |
| FLD-02 inline single-value adjacency test (new) | test (render-gate, PDF text adjacency) | request-response | `tests/test_confval_field_spacing_render_gate.py` (`PINNED_SC3_STRING` pattern, `_run_sphinx_build_typstpdf`, structural `.typ` assert + `pypdf` full-text adjacency assert) | exact |
| D-10 SIG-08 marker-propagation regression test (extend existing file) | test (structural, `parbreak()` count) | request-response | `tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate` (139-274) — the exact fixture (`SigBreakOuterClassOne`/`Two`) and count-derivation-in-docstring convention to extend, not clone | exact — same file, new/updated assertions |

## Pattern Assignments

### `visit_desc_content` / `depart_desc_content` (`typsphinx/translator.py:5102-5110`)

**Analog:** `visit_block_quote`/`depart_block_quote` (`typsphinx/translator.py:2920-2982`) — the
established, proven pattern for wrapping a run of code-mode body statements in a call that takes a
content block, and for routing every write through `self.add_text(...)` (never `self.body.append`,
per D-12's table-cell constraint — note `visit_block_quote` itself mixes `self.add_text` and does
NOT append directly, confirming the constraint is already the house style for this shape).

```python
# Source: typsphinx/translator.py:2920-2958 (visit_block_quote) — the wrap-in-a-call pattern
def visit_block_quote(self, node: nodes.block_quote) -> None:
    self._emit_id_anchors(node)
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")
    # CODE-MODE body -- { ... } not [ ... ] (bug #15). Every child is a
    # code-mode function call.
    self.add_text("quote(block: true, {")

def depart_block_quote(self, node: nodes.block_quote) -> None:
    has_attribution = any(isinstance(child, nodes.attribution) for child in node)
    if has_attribution:
        self.add_text(")\n\n")
    else:
        self.add_text("})\n\n")
    if self.in_list_item:
        self.list_item_needs_separator = True
```

**D-01's target shape for `visit_desc_content`/`depart_desc_content`** (mechanical substitution —
`pad(left: SHARED_INDENT_STEP, { … })` instead of `quote(block: true, { … })`, no attribution branch,
routed through `self.add_text`, never `self.body.append`):

```python
# Target shape (RESEARCH.md Code Examples, verified via typst.compile() this session)
def visit_desc_content(self, node: addnodes.desc_content) -> None:
    self.add_text(f"pad(left: {SHARED_INDENT_STEP}, {{")

def depart_desc_content(self, node: addnodes.desc_content) -> None:
    # D-10: propagate the SIG-08 marker THROUGH this close — see the
    # depart_desc section below for why this is load-bearing.
    propagate = self._desc_break_marker == len(self.body)
    self.add_text("})")
    if propagate:
        self._desc_break_marker = len(self.body)
```

`SHARED_INDENT_STEP` is already defined at `typsphinx/translator.py:29` (`"2.5em"`, Phase 37's
constant, D-02 locks its value). No new constant is introduced.

---

### `visit_field_list` / `depart_field_list` (`typsphinx/translator.py:5332-5359`)

**Analog:** itself — the existing block-visitor separator idiom (the leading-newline-in-a-list-item
guard, bug #4) plus `visit_block_quote`'s wrap-in-`pad`, applied as FLD-01's independent second `pad`
nested inside `desc_content`'s.

```python
# Source: typsphinx/translator.py:5332-5359 (current — the separator bookkeeping to KEEP unchanged)
def visit_field_list(self, node: nodes.field_list) -> None:
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")
        self.list_item_needs_separator = False
    # NEW (FLD-01): self.add_text(f"pad(left: {SHARED_INDENT_STEP}, {{")

def depart_field_list(self, node: nodes.field_list) -> None:
    self.body.append("\n")          # PRE-EXISTING: bypasses add_text (D-12 latent-bug flag)
    if self.in_list_item:
        self.list_item_needs_separator = True
    # NEW (FLD-01): must close the pad — self.add_text("})\n") replacing
    # the bare self.body.append("\n") above (D-12: route through add_text,
    # not body.append, so a field_list inside a table cell doesn't misroute).
```

**Latent bug this phase's own touch surfaces (RESEARCH.md, D-12):** `depart_field_list`'s pre-phase
`self.body.append("\n")` bypasses `add_text` entirely — the planner must change this line to
`self.add_text(...)` regardless of the pad wrapper, since a `field_list` inside a table cell would
otherwise misroute (mirrors the same `add_text`-not-`body.append` constraint the SIG-08 marker
comment at 4845-4849 already documents for `depart_desc`).

---

### `depart_desc`'s SIG-08 marker (`typsphinx/translator.py:4798-4854`) — D-10

**Analog:** itself — the existing `_desc_break_marker` mechanism (Phase 37 D-12), which this phase
must extend, not replace, to survive `depart_desc_content` now emitting real bytes.

```python
# Source: typsphinx/translator.py:4851-4854 (current, UNCHANGED code — the docstring above it
# (4816-4849) states the premise D-10 invalidates and MUST be corrected in the same edit)
if not self.in_table and self._desc_break_marker == len(self.body):
    return
self._emit_forced_break("parbreak()")
self._desc_break_marker = len(self.body)
```

**The verified-working fix (RESEARCH.md Pitfall 1, reproduced this session restoring the
`tests/fixtures/signature_break_and_arrow_gate` count from 9 back to 8):** `depart_desc_content` must
propagate the marker through its own closing bytes — see the `visit_desc_content`/`depart_desc_content`
section above for the exact propagation shape. `depart_desc` itself needs **no code change** under
this fix; only its docstring's premise sentence needs correcting (the "if nothing has been appended to
`self.body` since..." wording is still literally true, but the *reason* nothing is appended past a
suppressed nested-desc's own break must now account for the pad-closer being a "counts as nothing"
byte, not "no bytes at all").

---

### `visit_field_body` / `depart_field_body` single-paragraph unwrap (`typsphinx/translator.py:5421-5464`) — D-07/FLD-02

**Analog 1 — the existing all-inline classification to extend:**

```python
# Source: typsphinx/translator.py:5440-5450 (current)
self._field_body_stack.append(
    (self._in_field_body, self._field_body_has_content)
)
all_inline = all(
    isinstance(child, (nodes.Text, nodes.Inline)) for child in node.children
)
if all_inline:
    self._in_field_body = True
    self._field_body_has_content = False
else:
    self._in_field_body = False
```

D-07's new second case: `len(node.children) == 1 and isinstance(node.children[0], nodes.paragraph)`
must also set `self._in_field_body = True`. Verify the downstream consequence on `depart_field`'s
FID-09 separator (5387-5390): `_last_field_body_was_inline` becomes `True` for `:returns:`/`:rtype:`/
`:raises:` too, which is D-08's intended vertical-rhythm collapse but is a real behavioural change
needing its own fixture assertion, not an assumption.

**Analog 2 — the canonical "skip the block wrapper inside a special context" precedent,
`visit_paragraph`'s existing list-item fast-path (`typsphinx/translator.py:800-837`):**

```python
# Source: typsphinx/translator.py:800-837 (current — the PATTERN to extend with a field-body case)
def visit_paragraph(self, node: nodes.paragraph) -> None:
    self._emit_id_anchors(node)
    if self.in_list_item:
        self._emit_forced_break("parbreak()")
        self.in_paragraph = False
        return
    self.in_paragraph = True
    self.paragraph_has_content = False
    self.add_text("par({")
```

An analogous NEW branch (keyed on the field-body single-paragraph classification set in
`visit_field_body`) must be added BEFORE the `par({` fall-through: skip the `par({`/`})` wrapper
entirely and let the paragraph's children dispatch through the existing `_in_field_body`/
`_emit_inline_concat_separator`/`_mark_inline_concat_content` machinery unmodified — the same
machinery the all-inline collapsed case (a confval `:default:`) already exercises successfully. Do
NOT invent a second state flag; reuse `_in_field_body`/`_field_body_has_content` (D-12/Anti-Patterns).

---

### `visit_literal_strong`/`depart_literal_strong`, `visit_literal_emphasis`/`depart_literal_emphasis` (`typsphinx/translator.py:5745-5767`) — D-05/D-09/FLD-03

**Analog — `visit_literal`/`depart_literal`'s leaf-emission shape (`typsphinx/translator.py:1427-1522`),
specifically the escaping + concat-separator + `SkipNode` idiom, NOT `_emit_signature_leaf_wrapper`
(the Phase 37 helper, which injects an unrelated ZWSP escape — RESEARCH.md Pattern 4/Pitfall,
explicit trap to avoid):**

```python
# Source: typsphinx/translator.py:1427-1505 (visit_literal, current — the shape to mirror,
# NOT delegate to)
def visit_literal(self, node: nodes.literal) -> None:
    self._add_paragraph_separator()
    if not self._emit_inline_concat_separator():
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
    code_content = node.astext()
    # (self.in_table / leading-punctuation ZWSP branches are literal-specific;
    # literal_strong/literal_emphasis do not need them per D-05/D-09 — no
    # ZWSP requirement exists for field-body parameter echoes)
    escaped_code = escape_typst_string(code_content)
    self.add_text(f'raw("{escaped_code}")')
    if not self._mark_inline_concat_content():
        if self.in_list_item:
            self.list_item_needs_separator = True
    raise nodes.SkipNode
```

**Current (pre-phase) dummy-node delegation being replaced — D-09's explicit target:**

```python
# Source: typsphinx/translator.py:5745-5767 (current — the delegation trick to remove)
def visit_literal_strong(self, node: nodes.inline) -> None:
    dummy_strong = nodes.strong()
    self.visit_strong(dummy_strong)

def depart_literal_strong(self, node: nodes.inline) -> None:
    dummy_strong = nodes.strong()
    self.depart_strong(dummy_strong)

def visit_literal_emphasis(self, node: nodes.inline) -> None:
    dummy_emph = nodes.emphasis()
    self.visit_emphasis(dummy_emph)

def depart_literal_emphasis(self, node: nodes.inline) -> None:
    dummy_emph = nodes.emphasis()
    self.depart_emphasis(dummy_emph)
```

**D-05's target shape (RESEARCH.md Pattern 4, verified this session against a real sphinx-build
probe, including the resolvable-cross-reference-inside-`link()` composition case):**

```python
# Target shape — two independent leaf-emission bodies (D-09's "deliberate triplication",
# citing Phase 36 D-01 as precedent), mirroring visit_literal but wrapped in strong()/emph()
def visit_literal_strong(self, node: nodes.inline) -> None:
    self._add_paragraph_separator()
    if not self._emit_inline_concat_separator():
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
    escaped = escape_typst_string(node.astext())
    prefix = "#" if self._in_markup_mode else ""
    self.add_text(f'{prefix}strong(raw("{escaped}"))')
    if not self._mark_inline_concat_content():
        if self.in_list_item:
            self.list_item_needs_separator = True
    raise nodes.SkipNode
# visit_literal_emphasis: identical shape, "emph" in place of "strong".
# depart_* are never called (SkipNode raised in visit_*).
```

`depart_literal_strong`/`depart_literal_emphasis` become dead code once `SkipNode` is raised in
`visit_*` (mirroring `visit_literal`'s own `depart_literal` docstring note: "This is not called when
SkipNode is raised in visit_literal" — same fate here, keep the depart stubs for docutils' dispatcher
contract but they will not fire).

**D-06's per-sub-part assertion discipline applies to this pair's tests, not the handlers
themselves** — see the FLD-03 test pattern below.

---

## Shared Patterns

### The escaping helper — every new/changed emission site

**Source:** `escape_typst_string`, called from `visit_literal` (`typsphinx/translator.py:1493`) and
`visit_Text`. **Apply to:** `literal_strong`/`literal_emphasis`'s new leaf bodies. Never
`_escape_signature_text` (the Phase 37 helper) — it unconditionally injects a `\u{200B}` ZWSP escape
that no FLD decision asks for here (D-09/D-05 explicit trap).

### The render-gate test harness — `_run_sphinx_build_typst`

**Source:** `tests/test_pdf_render_gate.py:141-178`, already reused verbatim by
`tests/test_signature_break_and_arrow_gate.py:76-102` and
`tests/test_confval_field_spacing_render_gate.py:84-107` (the latter's `_typstpdf` variant).
**Apply to:** any new IND-01..05/FLD-01 render-gate test file — clone the `sys.executable -m sphinx`
subprocess shape exactly; never `["uv", "run", "sphinx-build", ...]` (documented NixOS PATH-shadowing
hazard, restated in all three source files).

```python
def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typst", str(source_dir), str(build_dir)],
        capture_output=True, text=True,
    )
```

### The "one fixture, many labeled constructs" convention

**Source:** `tests/fixtures/signature_break_and_arrow_gate/index.rst` (full file read this session,
100 lines) — each construct gets its own `====` heading, a docutils comment (`.. `) explaining
whether it is "the defect case" or a "CONTROL", and a minimal directive tree exercising exactly one
requirement. **Apply to:** the new IND-01..05 nesting fixture — mirror the `SigBreakOuterClassOne`/
`SigBreakOuterClassTwo` shape (class → nested method → nested method's own field list, plus a
trailing-content control and a sibling-after-nest control) rather than building N separate fixture
files.

```rst
.. py:class:: SigBreakOuterClassOne

   Outer class one body.

   .. py:method:: sig_break_inner_method_one()

      Inner method one body.
```

### `pypdf` layout-mode extraction for relative left-edge assertions (IND-01..05/FLD-01, SC#1/SC#2)

**Source:** RESEARCH.md Pattern 2, this session's own verified probe — `pypdf`'s per-glyph
`visitor_text` remains unusable (`x=0, y=0`, re-confirmed this session, same limitation
`tests/test_pdf_render_gate.py` and Phase 37 already worked around).

```python
reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
layout_text = reader.pages[0].extract_text(extraction_mode="layout")
# Compare len(line) - len(line.lstrip(" ")) between known marker lines for
# a relative "strictly greater than" left-edge assertion.
```

### The `PINNED_SC3_STRING` PDF-text-adjacency pattern (FLD-02)

**Source:** `tests/test_confval_field_spacing_render_gate.py:69` (`PINNED_SC3_STRING = "Type: int (a
number)  Default: 42"`) plus its two-test split: one structural `.typ`-substring test
(`test_typstpdf_confval_field_spacing_produces_pdf`, asserting the exact emitted-source shape) and one
compiled-PDF full-text adjacency test (`test_pdf_extracted_text_matches_pinned_sc3_string`, asserting
`PINNED_SC3_STRING in full_text`). **Apply to:** FLD-02's inline single-value assertion — hand-derive
a pinned string like `"Returns: Nothing at all."` (label and value on the SAME line, single space
after the colon) and assert it both in the `.typ` structural form and in the compiled-PDF extracted
text, exactly mirroring this file's two-test split.

### The `test_sig04_*` per-sub-part hand-derivation family (FLD-03)

**Source:** `tests/test_signature_typography_gate.py:55-120` — `_expected_bold`/`_expected_italic`/
`_expected_raw` helper functions that hand-derive the expected Typst call shape from
`escape_typst_string` directly (never from running the new translator code), plus `_slice`/
`_extract_wrapped_call` region-isolation helpers so one sub-part's assertion cannot be satisfied by
bytes belonging to a different field. **Apply to:** FLD-03's parametrized test — D-06 is explicit that
the assertion must be written PER SUB-PART (name vs type vs label), never as one blanket check over
the field body; write `_expected_bold_mono(text) -> f'strong(raw("{escape_typst_string(text)}"))'` and
`_expected_italic_mono(text) -> f'emph(raw("{escape_typst_string(text)}"))'` analogs (no ZWSP injection
here, per D-09 — the Phase 37 helpers' `_zwsp_after_dots` step must NOT be reused for this phase's
values).

### `depart_field`'s FID-09 inter-field separator, gated on `_last_field_body_was_inline`

**Source:** `typsphinx/translator.py:5367-5390`, already covered structurally by
`tests/test_confval_field_spacing_render_gate.py`'s `PINNED_SC3_STRING` assertion. **Apply to:** D-07's
single-paragraph unwrap changes which bodies set `_last_field_body_was_inline = True` — re-run/extend
this existing test file's assertions as a non-regression check (the confval `:type:`/`:default:` case
must stay byte-identical; only the ordinary `:param:`/`:returns:` docstring case is new territory).

### The SIG-08 fixture to extend, not clone (D-10)

**Source:** `tests/fixtures/signature_break_and_arrow_gate/index.rst` +
`tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate` (139-274) — already
contains `SigBreakOuterClassOne` (the "nothing after nested member" defect shape) and
`SigBreakOuterClassTwo` (the "trailing paragraph after nested member" control). **Apply to:** D-10 —
once `depart_desc_content` starts emitting bytes, re-run `test_sig08_exact_break_count_after_fix`
(expects exactly 8 `parbreak()`) and `test_sig08_no_adjacent_break_statements_anywhere`; if the marker-
propagation fix (see `depart_desc` section above) is correctly applied, both stay green with NO
fixture changes needed — this file's existing fixture already contains the exact reproduction shape
D-10 requires. Do not build a new fixture for this specific regression; extend the assertions'
docstrings to note Phase 38's `pad()` closer is now part of what the marker must see through.

## No Analog Found

None — every file/handler this phase touches has a direct, previously-established in-repo pattern to
copy from (the block-visitor wrap-in-a-call idiom, the leaf-emission `raw()`+`SkipNode` idiom, the
list-item paragraph fast-path idiom, the SIG-08 marker mechanism itself, and all four test-harness/
fixture conventions).

## Metadata

**Analog search scope:** `typsphinx/translator.py` (targeted reads: 1427-1522, 800-845, 2920-2984,
4780-4860, 5080-5480, 5730-5768); `tests/test_pdf_render_gate.py` (130-230),
`tests/test_confval_field_spacing_render_gate.py` (full file, 223 lines),
`tests/test_signature_typography_gate.py` (1-120),
`tests/test_signature_break_and_arrow_gate.py` (1-280),
`tests/fixtures/signature_break_and_arrow_gate/index.rst` (full file, 100 lines);
`.planning/phases/37-signature-typography-the-desc-family/37-PATTERNS.md` (full file, for shape and
naming-convention precedent).
**Files scanned:** 1 primary source file (targeted reads across ~600 lines total) + 4 test files (3
fully or near-fully read, 1 partially) + 1 fixture file (fully read) + 1 prior-phase pattern map
(fully read).
**Pattern extraction date:** 2026-08-01

---

*Phase: 38-Structural Indentation + Info Fields*
*Patterns mapped: 2026-08-01*
