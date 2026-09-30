# Phase 37: Signature Typography — the `desc_*` Family - Pattern Map

**Mapped:** 2026-08-01
**Files analyzed:** 1 modified source file (`typsphinx/translator.py`, ~15 handlers) + ~9 test files
(2 new, 1 rewritten fixture set, several rewritten assertions)
**Analogs found:** all handlers and all new test files have an in-repo analog; no "no analog" entries

All line numbers below were re-read directly from the current tree this session (2026-08-01) and may
differ slightly from CONTEXT.md/RESEARCH.md's own citations, which were taken from an earlier revision
of the same session — trust these numbers over the ones in those documents if they conflict by a line
or two; the code shapes described are identical.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `typsphinx/translator.py` — `visit_desc_signature`/`depart_desc_signature` (4669-4808) | translator node-handler (visitor pair) | transform (doctree node → Typst text emission) | `visit_literal`/`depart_literal` (1282-1360) for the `raw()`/escaping primitive; `visit_strong`/`depart_strong` (1203-1280, the body these two currently copy) for the wrapper-management bookkeeping being replaced | exact (same file, same visitor-pair shape) |
| `typsphinx/translator.py` — `visit_desc_returns` (4810-4827) | translator node-handler | transform | `visit_literal` for the `raw()` primitive; itself (only the string literal changes) | exact |
| `typsphinx/translator.py` — `desc_annotation`/`desc_addname`/`desc_name` (4880-4916, currently `pass`) | translator node-handler | transform | `visit_literal`/`depart_literal` (raw() emission + escaping) | exact |
| `typsphinx/translator.py` — `desc_parameterlist`/`desc_parameter`/`desc_optional` (4918-4984) | translator node-handler | transform (concatenation machinery) | itself (existing `text(...)`+`+` concat idiom); `visit_literal` for the `raw()` swap-in | exact |
| `typsphinx/translator.py` — `desc_sig_*` family (5261-5301, currently `pass`) | translator node-handler | transform | `visit_literal`/`depart_literal` (raw() + `SkipNode` pattern for *leaf* nodes only — see Pitfall 3 in RESEARCH.md, do NOT reuse `SkipNode` for non-leaf `desc_sig_name`) | role-match (leaf case exact; non-leaf case has no direct analog and must be hand-built per RESEARCH.md Pattern 2) |
| `typsphinx/translator.py` — `visit_Text` new monospace-mode flag (1018-1091) | translator node-handler / instance-state flag | transform | `self.in_literal_block` early-return branch in the SAME function (1033-1036) | exact — this is the canonical analog named in the task guidance |
| `typsphinx/translator.py` — `depart_desc`'s unconditional `parbreak()` (4653-4667) | translator node-handler | transform (break emission) | `_emit_forced_break` helper (289-317) it already calls; `_is_first_desc_signature`-style boolean-flag idiom (4642-4651, `visit_desc`) for the D-12 suppression flag | exact |
| `typsphinx/translator.py` — module-level `SIGNATURE_INDENT`-style constant (D-08) | config (module constant) | — | no existing analog for a shared-style-constant module attribute; nearest precedent is the `LEAK_SIGNATURES`-style test constant pattern (test-side) or a plain `ZWSP = chr(0x200B)`-style local in `visit_literal` (1317, 1340) — no prior *shared, cross-phase* constant exists | no analog — new pattern, keep it simple (module-level `_SIGNATURE_HANGING_INDENT = "2.5em"` near the top of the class/module) |
| `tests/test_signature_overflow_render_gate.py` (new, SIG-07) | test (render-gate) | request-response (subprocess build → compile → assert) | `tests/test_pdf_render_gate.py` (`_run_sphinx_build_typst` helper + `TestFigureLengthRenderGate`-style class, 268-324) for the harness shape; `tests/test_desc_bodyless_concat_render_gate.py` for the "own dedicated small fixture + own test file" convention | exact |
| `tests/test_signature_page_boundary_render_gate.py` (new, SIG-09) | test (render-gate) | request-response | `tests/test_pdf_render_gate.py` (per-page `pypdf` extraction pattern — note: existing helper joins ALL pages' text; SIG-09 needs PER-PAGE containment, so this file needs a variant loop, not a straight copy) | role-match (harness identical, assertion shape must be extended per-page) |
| desc_parameter sub-part parametrized unit test (SIG-04, new) | test (unit) | transform-assertion | `tests/test_translator.py::test_desc_parameterlist` and `::test_desc_with_annotation_and_name` (existing doctree-construction + `translator.translate()` + substring-assert idiom) | exact |
| nested-`desc` break-count fixture (SIG-08, new/extended) | test (render-gate, structural) | request-response | `tests/test_desc_bodyless_concat_render_gate.py` in full (harness + `.count("parbreak()")`-style structural assert) — this is the fixture to clone and adapt from *sibling* body-less desc to *nested* `py:class::`/`py:method::` | exact |
| D-11 optional-group-separator fixture (new) | test (unit + render-gate) | transform-assertion | `tests/test_desc_signature_concat_render_gate.py` (existing `desc_optional` bracket-nesting assertions) for the unit half; `tests/test_pdf_render_gate.py::TestDescSignatureRenderGate` (the `printf(fmt[, args[, more]])` case, 731-810) for the compiled-PDF half | exact |
| `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` (rewritten, D-14) | test fixture (golden file) | file-I/O (static comparison fixture) | itself (in-place edit — see Shared Patterns → golden.typ migration below) | exact |

## Pattern Assignments

### `visit_desc_signature` / `depart_desc_signature` (4669-4808)

**Analog 1 — the `raw()`/escaping primitive: `visit_literal`/`depart_literal` (`typsphinx/translator.py:1282-1360`)**

```python
def visit_literal(self, node: nodes.literal) -> None:
    self._add_paragraph_separator()
    if not self._emit_inline_concat_separator():
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
    code_content = node.astext()
    if self.in_table:
        zwsp = chr(0x200B)
        code_content = code_content.replace(".", "." + zwsp).replace("_", "_" + zwsp)
    elif code_content and code_content[0] in ":;,)]}!?":
        zwsp = chr(0x200B)
        code_content = zwsp + code_content
    escaped_code = escape_typst_string(code_content)
    self.add_text(f'raw("{escaped_code}")')
    if not self._mark_inline_concat_content():
        if self.in_list_item:
            self.list_item_needs_separator = True
    raise nodes.SkipNode
```

**Every new `raw(...)` call site this phase adds (desc_name/addname/annotation, desc_sig_* leaves,
delimiters, arrow glyph) must call `escape_typst_string` exactly like this — do not re-derive
escaping.** Note the `raise nodes.SkipNode` at the end: this shortcut is valid ONLY for leaf text
nodes. RESEARCH.md's Pitfall 3 is explicit that a non-leaf `desc_sig_name` (a type annotation wrapping
a `reference`) must NOT use this shortcut — it must dispatch its children normally under the new
`in_signature_text` flag so `visit_reference` still fires.

**Analog 2 — the wrapper/state-machine bookkeeping being replaced: `visit_strong`/`depart_strong`
(`typsphinx/translator.py:1203-1280`, and the verbatim copy at 4702-4779 that `visit_desc_signature`
currently IS)**

```python
# visit_strong (1203-1236ish) -- the exact block visit_desc_signature copies today:
self._add_paragraph_separator()
if not self._enter_inline_concat_element():
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")
was_in_paragraph = self.in_paragraph
self.in_paragraph = False
was_list_item_needs_separator = self.list_item_needs_separator
was_in_list_item = self.in_list_item
self.in_list_item = True
self.list_item_needs_separator = False
prefix = "#" if self._in_markup_mode else ""
self.add_text(f"{prefix}strong({{")
self._strong_was_in_paragraph = was_in_paragraph
self._strong_was_in_list_item = was_in_list_item
self._strong_was_list_item_needs_separator = was_list_item_needs_separator
```
```python
# depart_strong (1258-1280) -- what depart_desc_signature currently mirrors:
self.add_text("})")
if hasattr(self, "_strong_was_in_paragraph"):
    self.in_paragraph = self._strong_was_in_paragraph
    delattr(self, "_strong_was_in_paragraph")
if hasattr(self, "_strong_was_in_list_item"):
    self.in_list_item = self._strong_was_in_list_item
    delattr(self, "_strong_was_in_list_item")
if hasattr(self, "_strong_was_list_item_needs_separator"):
    if self.in_list_item:
        self.list_item_needs_separator = True
    delattr(self, "_strong_was_list_item_needs_separator")
self._exit_inline_concat_element()
```

Per D-10 (confirmed in RESEARCH.md), the ONLY literal strings that change in this pair are:
- `visit`: `f"{prefix}strong({{"` → `f"{prefix}block(above: 0pt, below: 0pt, sticky: true, par(hanging-indent: {SIGNATURE_INDENT}, {{"` (exact spelling TBD by planner, but must zero `above`/`below` per the measured Pitfall 1 hazard)
- `depart`: `"})"` → the matching close, e.g. `"}))"` — one extra `)` per each of `block(` and `par(`.
- Set `self.in_signature_text = True` in visit (new flag, cleared in depart) alongside the existing
  state save/restore — this is the flag `visit_Text` reads (see below).

All the paragraph-separator / concat-element / list-item bookkeeping stays **byte-identical** — do
not touch it.

**Anchor emission (depart, 4781-4808) — must survive unchanged, byte-equivalent, this is explicitly
called out in CONTEXT.md D-10's binding constraint:**

```python
docname = self._current_docname()
seen_labels: set[str] = set()
for node_id in node.get("ids", []):
    label_id = self._namespace_label(docname, node_id)
    if label_id in seen_labels:
        continue
    seen_labels.add(label_id)
    self.body.append(f"\n[#metadata(none) <{label_id}>]")
self.body.append("\n")
```

This block is orthogonal to the D-10 wrapper change and must be copied forward verbatim.

**FID-03 sibling `linebreak()` mechanism (4698-4700), preserved as-is per D-12's recommendation:**
```python
if not self._is_first_desc_signature:
    self._emit_forced_break("linebreak()")
self._is_first_desc_signature = False
```

---

### `visit_desc_returns` (4810-4827)

**Analog:** itself, plus `visit_literal`'s escaping helper for the arrow glyph string.

Current:
```python
def visit_desc_returns(self, node: addnodes.desc_returns) -> None:
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")
    self.add_text('text(" -> ")')
    if self.in_list_item:
        self.list_item_needs_separator = True
```
Per D-13, the ONE literal string changes: `'text(" -> ")'` → a `raw(...)`-wrapped U+2192, e.g.
`self.add_text('raw(" → ")')` (exact spacing/escaping is the planner's call — verify via
`escape_typst_string` if the glyph or surrounding spaces need any escaping; RESEARCH.md's D-13
citation shows `raw(" ") + raw("\u{2192}") + raw(" ")` as the Typst-side shape actually compiled and
`pypdf`-verified this session — that three-part form is the proven target, not a guess). The
`in_list_item`/`list_item_needs_separator` bookkeeping is untouched.

---

### `desc_annotation` / `desc_addname` / `desc_name` (4880-4916, currently `pass`)

**Analog:** `visit_literal`/`depart_literal` for the `raw()` emission mechanics; D-01's table for which
wrapper (`strong(raw(...))` vs bare `raw(...)`) applies to which node.

These are currently `visit_*`/`depart_*` pairs that do nothing (the parent `desc_signature`'s
`strong({...})` wrapper used to cover the whole run via plain `text()` Text-node emission). Under the
new `in_signature_text` flag (see `visit_Text` below), `visit_Text` will already emit `raw(...)` for
descendant text — these three handlers' job is to add the EXTRA `strong(...)`/nothing wrapper around
their own children per D-01:

| Node | Wrapper to add in `visit_*`/`depart_*` |
|---|---|
| `desc_name` | open `strong({{` / close `}})` around children (bold monospace — children already emit `raw()` via the flag) |
| `desc_annotation` | same `strong({{`/`}})` pair — SIG-03 requires byte-identical treatment to `desc_name` |
| `desc_addname` | no extra wrapper — children's `raw()` emission from the flag alone gives regular-weight monospace |

`depart_desc_name`'s existing `list_item_needs_separator` bookkeeping (4914-4916) is preserved
unchanged; it's orthogonal to the wrapper.

---

### `desc_parameterlist` / `desc_parameter` / `desc_optional` (4918-4984)

**Analog:** itself — the existing `text("(")`/`+`/`text(", ")` concatenation idiom is the pattern to
follow, swapping `text(...)` for `raw(...)` per D-01's delimiter row. `visit_literal`'s escaping stays
the reference for any escaped delimiter content (though delimiters here are all literal ASCII with no
escaping concerns).

Current (delimiters):
```python
# visit_desc_parameterlist
self.body.append('text("(") + ')
# depart_desc_parameterlist
self.body.append('text(")")')
# depart_desc_parameter
if node.next_node(descend=False, siblings=True):
    self.body.append(' + text(", ")')
    self._desc_parameter_has_content = True
# visit_desc_optional
self.add_text('text("[")')
# depart_desc_optional
self.add_text(' + text("]")')
```
Mechanical change: every `text("...")` delimiter literal in this family becomes `raw("...")` (SIG-05).
The `+`/`_desc_parameter_has_content` bookkeeping is unchanged.

**D-11 fix site — `depart_desc_optional` (4981-4984):** RESEARCH.md's illustrative fix (Code Examples
section, quoted verbatim since it is the direct target for the D-11 fixture):
```python
def depart_desc_optional(self, node):
    if node.next_node(descend=False, siblings=True):
        self.add_text(' + raw(", ")')   # comma INSIDE the bracket, mirroring Sphinx HTML "[timeout, ]"
    self.add_text(' + raw("]")')
    self._desc_parameter_has_content = True
```
This is checked against the `desc_optional` node's own following-sibling (mirroring what
`depart_desc_parameter` already does for a `desc_parameter`'s own following sibling) — not against
`desc_optional`'s last child.

**SIG-04's per-sub-part italic name (D-05's discriminator, Pattern 2 in RESEARCH.md) is implemented in
`visit_desc_sig_name`, not here** — see below.

---

### `desc_sig_*` family (5261-5301, currently all `pass`)

**Analog for leaf nodes: `visit_literal`'s `astext()` + `raw()` + `SkipNode` shortcut** — but ONLY
for `desc_sig_keyword`, `desc_sig_space`, `desc_sig_punctuation`, `desc_sig_operator` (these are
always leaves in the measured corpus) and for a `desc_sig_name` node confirmed to be a leaf.

**Anti-pattern, explicitly flagged in RESEARCH.md Pitfall 3 — do NOT copy `visit_literal`'s
`SkipNode` shortcut onto a non-leaf `desc_sig_name`:**
```python
# WRONG for desc_sig_name when it wraps a `reference` (resolved type xref):
# node.astext() flattens the nested reference to plain text, silently
# discarding the link -- must NOT raise SkipNode here.
```
Correct shape (RESEARCH.md Pattern 2, illustrative):
```python
def visit_desc_sig_name(self, node: addnodes.desc_sig_name) -> None:
    is_leaf = len(node.children) <= 1 or all(
        isinstance(c, nodes.Text) for c in node.children
    )
    is_first_in_parameter = (
        isinstance(node.parent, addnodes.desc_parameter)
        and not self._param_name_seen
    )
    if is_first_in_parameter:
        self._param_name_seen = True
        self.add_text("emph(")
        self._sig_name_needs_emph_close = True  # per-node stack entry, mirror _strong_was_* idiom
    # else: fall through, let children dispatch normally under in_signature_text
```
The `_param_name_seen` reset belongs in `visit_desc_parameter` (currently `pass`, 4945-4951) — mirror
the existing `_desc_parameter_has_content = False` reset idiom already used in
`visit_desc_parameterlist` (4933-4935) for a per-scope boolean flag.

Bare `desc_sig_keyword`/`desc_sig_space`/`desc_sig_punctuation`/`desc_sig_operator` (never wrapping
non-Text children in the measured corpus) can use the full `visit_literal`-style shortcut:
```python
def visit_desc_sig_punctuation(self, node) -> None:
    self._add_paragraph_separator()
    if not self._emit_inline_concat_separator():
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
    escaped = escape_typst_string(node.astext())
    self.add_text(f'raw("{escaped}")')
    if not self._mark_inline_concat_content():
        if self.in_list_item:
            self.list_item_needs_separator = True
    raise nodes.SkipNode
```

---

### `visit_Text` monospace-mode flag (1018-1091)

**Canonical analog, exactly as the task guidance names it — the existing `in_literal_block` early
return in the SAME function:**

```python
def visit_Text(self, node: nodes.Text) -> None:
    text_content = node.astext()

    # Inside literal blocks, output text directly (no wrapping)
    if self.in_literal_block:
        self.add_text(text_content)
        return

    # ... FID-11 soft-wrap collapse ...
    text_content = text_content.replace("\n", " ")
    text_content = escape_typst_string(text_content)

    self._add_paragraph_separator()
    if not self._emit_inline_concat_separator():
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

    prefix = "#" if self._in_markup_mode else ""
    self.add_text(f'{prefix}text("{text_content}")')

    if not self._mark_inline_concat_content():
        if self.in_list_item:
            self.list_item_needs_separator = True
```

New branch to add, modeled directly on the `in_literal_block` shape but NOT using its bare
`add_text(text_content)` form (that skips escaping and paragraph/concat bookkeeping entirely, which is
wrong here — signature text still needs escaping, paragraph-separator, and concat bookkeeping, just a
different final wrapper call):

```python
if self.in_signature_text:
    text_content = text_content.replace("\n", " ")
    escaped = escape_typst_string(text_content)
    self._add_paragraph_separator()
    if not self._emit_inline_concat_separator():
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
    prefix = "#" if self._in_markup_mode else ""
    self.add_text(f'{prefix}raw("{escaped}")')
    if not self._mark_inline_concat_content():
        if self.in_list_item:
            self.list_item_needs_separator = True
    return
```
Placed as a new `elif`/early check AFTER the `in_literal_block` check (that one must stay first and
unconditional — literal blocks and signatures are mutually exclusive contexts, order doesn't strictly
matter, but keep `in_literal_block` first since it's the existing, proven check). The flag itself:
`self.in_signature_text = True` set in `visit_desc_signature`, `False`/deleted in
`depart_desc_signature` — same lifecycle shape as `self.in_literal_block` (search for its own
set/unset sites in `visit_literal_block`/`depart_literal_block` if the planner wants that exact
symmetry).

---

### `depart_desc`'s unconditional `parbreak()` (4653-4667) — SIG-08 / D-12

**Analog 1 — the helper already called:** `_emit_forced_break` (289-317, quoted in full below).
**Analog 2 — the boolean-flag idiom for "is this the nested case":** `_is_first_desc_signature`,
reset in `visit_desc` (4642-4651) and consumed in `visit_desc_signature` (4698-4700) — the exact
pattern D-12 says to mirror rather than inventing new state machinery.

```python
def _emit_forced_break(self, break_token: str) -> None:
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")
    self.add_text(f"{break_token}\n")
    if self.in_list_item:
        self.list_item_needs_separator = True
```

```python
# visit_desc (4640-4651), the flag-reset idiom to mirror for D-12:
def visit_desc(self, node: addnodes.desc) -> None:
    self._emit_id_anchors(node)
    self._is_first_desc_signature = True

def depart_desc(self, node: addnodes.desc) -> None:
    self._emit_forced_break("parbreak()")
```

D-12's recommendation: track desc nesting depth (or a simple "did the desc I'm about to depart have a
nested `desc` as its last content" boolean) and suppress the OUTER `desc`'s `parbreak()` only when it
would be immediately preceded by the INNER `desc`'s own `parbreak()` with nothing emitted in between —
implemented as a scalar flag set in `visit_desc`/read+cleared in `depart_desc`, exactly like
`_is_first_desc_signature`'s scalar (not stack-based) design, justified by the same non-reentrancy
argument already documented at 4642-4651 (a desc's own signature children fully process before its
content, so no race with a nested desc's own reset).

---

## Shared Patterns

### The escaping helper — every new `raw(...)` site

**Source:** `escape_typst_string`, called from `visit_literal` (`typsphinx/translator.py:1348`) and
`visit_Text` (`typsphinx/translator.py:1057`).
**Apply to:** every new/changed `raw(...)` call site added in this phase — `desc_name`,
`desc_addname`, `desc_annotation`, `desc_sig_*` leaves, the D-13 arrow glyph, the D-11 comma/bracket
literals, and the new `visit_Text` monospace branch. Never hand-roll escaping for a new site; import
this single helper.

### The stack-based inline-concat bookkeeping — every visitor pair opening its own content block

**Source:** `_enter_inline_concat_element`/`_exit_inline_concat_element` (`typsphinx/translator.py:977-1016`), and the simpler `_emit_inline_concat_separator`/`_mark_inline_concat_content` pair used by leaf-emitting visitors like `visit_literal`/`visit_Text`.
**Apply to:** `visit_desc_signature`/`depart_desc_signature` (already uses `_enter_inline_concat_element`/`_exit_inline_concat_element` — keep as-is), and any new `desc_name`/`desc_annotation` `strong({{`/`}})` wrapper that opens its own content block should call the same pair rather than the simpler leaf-node helpers (`visit_literal`/`visit_Text` use the simpler pair because they don't open a nested content block).

```python
def _enter_inline_concat_element(self) -> bool:
    ctx = self._inline_concat_context()
    self._inline_concat_stack.append(ctx)
    if ctx is None:
        return False
    if getattr(self, ctx[1]):
        self.add_text(" + ")
    setattr(self, ctx[0], False)
    return True

def _exit_inline_concat_element(self) -> None:
    ctx = self._inline_concat_stack.pop()
    if ctx is None:
        return
    setattr(self, ctx[0], True)
    setattr(self, ctx[1], True)
```

### The forced-break helper — every place a real Typst `parbreak()`/`linebreak()` is needed

**Source:** `_emit_forced_break` (`typsphinx/translator.py:289-317`), already used by
`visit_desc_signature`'s FID-03 sibling break and `depart_desc`'s SIG-08 break.
**Apply to:** any D-12 suppression logic still needs to call this same helper when it DOES decide to
emit the (single) `parbreak()` — only the decision of *whether* to call it changes, not the mechanism.

### The render-gate test harness — `_run_sphinx_build_typst`

**Source:** `tests/test_pdf_render_gate.py:141-178`.
```python
def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path, extra_args: tuple = ()
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typst",
         *extra_args, str(source_dir), str(build_dir)],
        capture_output=True, text=True,
    )
```
**Apply to:** both new files `tests/test_signature_overflow_render_gate.py` and
`tests/test_signature_page_boundary_render_gate.py`. **Mandatory:** `sys.executable -m sphinx`, never
`["uv", "run", "sphinx-build", ...]` — the NixOS stub-ld/PATH-shadowing hazard documented at
141-158 and reiterated in 37-VALIDATION.md. For a `-b typstpdf` build (compiling to PDF directly
instead of compiling the `.typ` separately with `typst.compile()`), use
`tests/test_desc_bodyless_concat_render_gate.py:55-78`'s `_run_sphinx_build_typstpdf` variant instead
— same shape, `-b typstpdf` in place of `-b typst`.

### The fixture-directory convention

**Source:** `tests/fixtures/desc_rubric_decoupling_render_gate/{index.rst,golden.typ,conf.py}` and
`tests/fixtures/desc_signature_render_gate/index.rst` (referenced via the `fixtures_dir` /
`desc_signature_render_gate_dir` pytest fixtures at `tests/test_pdf_render_gate.py:52-97`).
**Apply to:** the new `tests/fixtures/signature_overflow_render_gate/` (SIG-07 synthetic long-dotted
identifier) and `tests/fixtures/signature_page_boundary_render_gate/` (SIG-09 forced page-break; per
RESEARCH.md's D-09 experiment, this fixture needs a `#set page(height:, margin:)` override — check
whether that's injected via a custom `conf.py` `typst_template`/`typst_elements` override or a raw
`.typ` post-processing step; no existing fixture does this exactly, so this is the one place planners
should double check against a fresh `typst.compile()` probe before committing to a mechanism).

### Structural `.typ` assertions over compiled-PDF text extraction — pick per requirement

**Source:** `tests/test_desc_bodyless_concat_render_gate.py`'s `"parbreak()" in typ_text` structural
check (D-05 in that file's own docstring) vs. `tests/test_pdf_render_gate.py`'s `pypdf` text-extraction
checks (arrow glyph, DESC-02 sentinel ordering).
**Apply to:** SIG-01/02/03/05 (monospace primitive presence/absence — structural `.typ` string checks,
per SIG-04's D-03 "per-sub-part" framing, are cheaper and more precise than a PDF round-trip); SIG-06
(arrow glyph survival — MUST be a compiled-PDF `pypdf` check per D-13's own precedent, since the goal
is proving the glyph is real, not just that `raw("→")` appears in source); SIG-07 (must use
Typst-side `context measure(...)` probes, NOT `pypdf` bounding boxes — RESEARCH.md's Environment
Availability section found `pypdf`'s `extract_text(visitor_text=...)` unreliable for x/y positions in
this sandbox); SIG-08 (structural `.typ` `output.count("parbreak()")`, mirroring
`test_desc_bodyless_concat_render_gate.py` exactly); SIG-09 (per-page `pypdf.extract_text()`
containment, extending the existing all-pages-joined pattern into a per-page loop).

### `golden.typ` migration (D-14)

**Source file to edit in place:** `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ`
(quoted in full above under Code Context).
**What changes:** only the `connect`/`compile`×3/`--sep` `strong({text(...` blocks (7 of ~35
content-bearing lines, per RESEARCH.md's own line audit) become the new D-10 wrapper shape plus
per-sub-part `strong(raw(...))`/`raw(...)`/`emph(raw(...))` — e.g. the `connect` line's exact
before/after diff is the concrete worked example planners should derive every other changed line from.
**What must NOT change:** the rubric lines (`Options`, `A Rubric In A List Item`, `Trailing Heading`),
the plain-`**bold text**` regression-control paragraph, and the `list({...})` bullet structure — these
must stay byte-identical, and the diff itself becomes evidence Phase 37 touched only signatures
(binding constraint, SC#5 hand-derivation — do not regenerate this file by running the new code and
copying its output).

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| Module-level `SIGNATURE_INDENT`/similar shared constant (D-08) | config | — | No prior shared, cross-phase Python-side style constant exists in this codebase; nearest precedent (`chr(0x200B)` inline literals in `visit_literal`) is a local, not a class/module-level named constant. Planner should place it near the top of `translator.py` (module scope, e.g. `_SIGNATURE_HANGING_INDENT = "2.5em"`) with a docstring noting Phase 38's IND-04 will import/reuse it — no existing file to model the *naming convention* on. |

## Metadata

**Analog search scope:** `typsphinx/translator.py` (full grep for `_emit_forced_break`,
`_emit_id_anchors`, `_enter_inline_concat_element`, `visit_literal`, `visit_Text`, `visit_strong`, the
full `desc_*`/`desc_sig_*` handler block); `tests/test_pdf_render_gate.py`,
`tests/test_desc_bodyless_concat_render_gate.py`,
`tests/fixtures/desc_rubric_decoupling_render_gate/{index.rst,golden.typ}`,
`tests/fixtures/desc_signature_render_gate/index.rst`.
**Files scanned:** 1 primary source file (targeted reads at 4640-5020, 5240-5310, 1000-1100,
1270-1370, 280-355, 960-1000) + 7 test files (existence/line-count check) + 2 fully read test files +
1 fixture pair fully read.
**Pattern extraction date:** 2026-08-01

---

*Phase: 37-Signature Typography — the `desc_*` Family*
*Patterns mapped: 2026-08-01*
