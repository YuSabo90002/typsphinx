# Phase 12: High-Volume Independent Node Handlers - Pattern Map

**Mapped:** 2026-07-12
**Files analyzed:** 3 (1 production file with ~10 new visitor pairs + 1 fix; 1 test file; N new fixture dirs)
**Analogs found:** 3 / 3 (all analogs live inside the same file being modified — this phase is self-referential pattern reuse, confirmed by RESEARCH.md's own live-doctree/compile verification)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `typsphinx/translator.py` (add `visit_versionmodified`/`depart_versionmodified`) | translator visitor | transform (doctree→markup) | `visit_index`/`depart_index` (translator.py:2645-2655) — transparent pass-through pair | exact (same "pass-through, exists only to silence `unknown_visit` warning" shape) |
| `typsphinx/translator.py` (extend `visit_inline`/`depart_inline`) | translator visitor | transform | `visit_inline`/`depart_inline` itself (translator.py:2621-2640) — being extended in place | exact (in-place extension, not a new file) |
| `typsphinx/translator.py` (fix `depart_term`) | translator visitor | transform | `visit_title`/`depart_title` bracket-wrap label pattern (translator.py:230-279, esp. 264-275) | exact (RESEARCH.md explicitly names this as the fix to mirror) |
| `typsphinx/translator.py` (add `visit_desc_returns`/`depart_desc_returns`) | translator visitor | transform | `depart_desc_parameter` literal-text-with-separator-bookkeeping (translator.py:2818-2827) + `visit_desc_name`/`depart_desc_name` (translator.py:2771-2781) | role-match (literal-prefix injection idiom) |
| `typsphinx/translator.py` (add `visit_desc_signature_line`/`depart_desc_signature_line` + `_is_first_desc_signature_line` state) | translator visitor | transform | `_desc_parameter_has_content` first-item-flag idiom (translator.py:2798-2800, 2805-2807) | role-match (same "is-first" flag idiom, new variable) |
| `typsphinx/translator.py` (add `visit_desc_optional`/`depart_desc_optional`) | translator visitor | transform | `visit_desc_parameterlist`/`depart_desc_parameterlist` (translator.py:2783-2808) — literal bracket/paren wrap reusing `_desc_parameter_has_content` | exact (same flag, same `+`-join wrap idiom, recursion-safe by construction) |
| `typsphinx/translator.py` (add `visit_desc_inline`/`depart_desc_inline`) | translator visitor | transform | `visit_desc_content`/`depart_desc_content` (translator.py:2735-2743) — pure `pass`/`pass` | exact |
| `typsphinx/translator.py` (add `visit_transition`) | translator visitor | transform | `visit_comment` (translator.py:419-432) — `raise nodes.SkipNode` after emitting literal content | exact (same emit-then-skip shape; comment emits nothing, transition emits one literal line first) |
| `typsphinx/translator.py` (add `visit_glossary`/`depart_glossary`) | translator visitor | transform | `visit_desc_content`/`depart_desc_content` (translator.py:2735-2743) — pure pass-through | exact |
| `typsphinx/translator.py` (add `visit_tabular_col_spec`) | translator visitor | transform | `visit_comment` (translator.py:419-432), `visit_index` (translator.py:2645-2651) — bare `raise nodes.SkipNode`, no depart needed | exact |
| `typsphinx/translator.py` (add `visit_abbreviation`/`depart_abbreviation`) | translator visitor | transform | `visit_literal_strong`/`visit_literal_emphasis` (translator.py:2913, 2977, 2989) dummy-node-delegation idiom | exact (per RESEARCH.md Pattern 4.4) |
| `tests/test_pdf_render_gate.py` (add 4 new test classes) | test | request-response (compile→assert) | existing Phase-11 GATE-01 fixture classes in the same file (same `LEAK_SIGNATURES`, `@pytest.mark.slow` + `skipif(not TYPST_AVAILABLE and PYPDF_AVAILABLE)` convention) | exact — RESEARCH.md confirms "same shape, unchanged since Phase 11" |
| `tests/fixtures/version_modified_render_gate/` (new dir: `conf.py`, `index.rst`) | fixture | file-I/O | existing Phase-11 `*_render_gate` fixture dirs | exact (mirror structure) |
| `tests/fixtures/xref_refid_render_gate/` (new dir) | fixture | file-I/O | existing Phase-11 `*_render_gate` fixture dirs | exact |
| `tests/fixtures/desc_signature_render_gate/` (new dir) | fixture | file-I/O | existing Phase-11 `*_render_gate` fixture dirs | exact |
| `tests/fixtures/trivial_blocks_render_gate/` (new dir) | fixture | file-I/O | existing Phase-11 `*_render_gate` fixture dirs | exact |

## Pattern Assignments

### VER-01 — `visit_versionmodified`/`depart_versionmodified` + `visit_inline`/`depart_inline` classed dispatch

**Analog 1 (pass-through pair shape):** `visit_index`/`depart_index`, translator.py:2645-2655
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
`versionmodified` is NOT skipped (its paragraph child must render) — so the shape to copy is "empty visit/depart pair that exists only to silence `unknown_visit`'s warning," not the `SkipNode` part. `visit_desc_content`/`depart_desc_content` (translator.py:2735-2743, both bare `pass`) is the truer analog for the body.

**Analog 2 (current `visit_inline`/`depart_inline` — extend in place):** translator.py:2621-2640
```python
def visit_inline(self, node: nodes.inline) -> None:
    """
    Visit an inline node.
    ...
    """
    # Inline nodes are transparent containers - we just process their children
    # The CSS classes (like 'xref', 'doc', 'std-ref') are mainly for HTML/CSS styling
    # For Typst output, we simply render the text content
    pass

def depart_inline(self, node: nodes.inline) -> None:
    """
    Depart an inline node.
    """
    pass
```

**Analog 3 (dummy-node delegation to reuse `visit_emphasis`'s full state-juggling):** `visit_emphasis`/`depart_emphasis`, translator.py:556-624 (full excerpt already captured; key lines: 556 `def visit_emphasis`, 589 `self.add_text(f"{prefix}emph({{")`, 597 `def depart_emphasis`, 607 `self.add_text("})")`). This is the exact function RESEARCH.md's recommended implementation delegates to via a dummy `nodes.emphasis()` instance — same idiom already used 4x elsewhere in the file (`visit_title_reference` at :2913, `visit_literal_strong` at :2977, `visit_literal_emphasis` at :2989).

**Concrete target implementation (from RESEARCH.md Pattern 1, verified via live doctree dump + confirmed against current line numbers above):**
```python
def visit_versionmodified(self, node: addnodes.versionmodified) -> None:
    pass

def depart_versionmodified(self, node: addnodes.versionmodified) -> None:
    pass

def visit_inline(self, node: nodes.inline) -> None:
    if "versionmodified" in node.get("classes", []):
        dummy_emph = nodes.emphasis()
        self.visit_emphasis(dummy_emph)
        return
    pass

def depart_inline(self, node: nodes.inline) -> None:
    if "versionmodified" in node.get("classes", []):
        dummy_emph = nodes.emphasis()
        self.depart_emphasis(dummy_emph)
        return
    pass
```
No `sphinx.domains.changeset.versionlabels` import needed — Sphinx bakes label wording into a `nodes.inline(classes=["versionmodified", <kind>])` at parse time (confirmed via live `sphinx-build` dump, RESEARCH.md Part 1).

---

### XREF-01 — confirm `visit_reference` refid branch + required `depart_term` label-anchor fix

**Analog (already-correct refid branch, DO NOT MODIFY, just verify/fixture):** `visit_reference`, translator.py:2072-2169, specifically the refid branch at 2119-2132:
```python
# Internal same-document :target: (e.g. a figure/image target)
# resolves to an empty/absent refuri with a populated refid instead
# of a "#"-prefixed refuri. Handle it before the empty-URL guard so
# it doesn't fall through to the plain-text fallback (FIG-02, D-03).
if not refuri and refid:
    prefix = "#" if self._in_markup_mode else ""
    self.add_text(f"{prefix}link(<{refid}>, ")

    # Replicate the method-end bookkeeping inline since this branch
    # returns early (mirrors the refuri branches below).
    if self._in_markup_mode:
        self._in_markup_mode = False
    self._in_link = True
    self._link_has_content = False
    self._reference_was_list_item_needs_separator = (
        was_list_item_needs_separator
    )
    return
```
And the empty-URL guard immediately after (2134-2145) — confirms the "never emit `link(\"\", …)`" contract (D-04) already holds:
```python
if not refuri:
    logger.warning(
        f"Reference node has empty URL. "
        f"Link will be rendered as plain text. "
        f"Check for broken references in source: {node.astext()}"
    )
    self._skip_link_wrapper = True
    return
```

**Required fix analog (bracket-wrap label attachment — the pattern to mirror):** `visit_title`/`depart_title`, translator.py:230-279 (full section already read):
```python
# visit_title, lines 230-242:
self._title_section_ids = (
    node.parent.get("ids") if isinstance(node.parent, nodes.section) else None
) or []
if self._title_section_ids:
    self.add_text(f"[#heading(level: {self.section_level}, ")
else:
    self.add_text(f"heading(level: {self.section_level}, ")

# depart_title, lines 264-279:
if self._title_section_ids:
    primary_id, *extra_ids = self._title_section_ids
    self.add_text(f") <{primary_id}>]\n")
    for extra_id in extra_ids:
        self.add_text(f"[#metadata(none) <{extra_id}>]\n")
    self.add_text("\n")
else:
    self.add_text(")\n\n")
self._title_section_ids = []
```

**Current buggy `depart_term`** (translator.py:1127-1163) — buffers term content but NEVER reads `node.get("ids")`, so no anchor is emitted:
```python
def visit_term(self, node: nodes.term) -> None:
    self.saved_body = self.body
    self.current_term_buffer = []
    self.body = self.current_term_buffer

def depart_term(self, node: nodes.term) -> None:
    if isinstance(self.current_term_buffer, list):
        term_content = "".join(self.current_term_buffer).strip()
    else:
        term_content = ""
    if self.saved_body is not None:
        self.body = self.saved_body
    self.saved_body = None
    # Store term for later (will be paired with definition)
    self.current_term_buffer = term_content   # <-- BUG: no label anchor emitted here
```

**Required fix (RESEARCH.md Pattern 2, verified via direct `typst.compile()` this session):**
```python
def depart_term(self, node: nodes.term) -> None:
    if isinstance(self.current_term_buffer, list):
        term_content = "".join(self.current_term_buffer).strip()
    else:
        term_content = ""

    if self.saved_body is not None:
        self.body = self.saved_body
    self.saved_body = None

    if node.get("ids"):
        label_id = node["ids"][0]
        term_content = f"[#{{{term_content}}} <{label_id}>]"

    self.current_term_buffer = term_content
```
**Anti-pattern confirmed to fail:** `+`-joining a bare `label("term-id")` onto content raises `TypstError: cannot add content and label` — always use the bracket-wrap markup form, never `+`.

---

### DESC-01 — `visit_desc_returns`/`depart_desc_returns`

**Analog (literal-prefix injection with list-item separator bookkeeping):** `depart_desc_parameter`, translator.py:2818-2827, and `visit_desc_parameterlist` opening-paren emission, translator.py:2789-2794:
```python
def depart_desc_parameter(self, node: addnodes.desc_parameter) -> None:
    """
    Depart a desc_parameter node.

    Add comma + space between parameters if not last.
    """
    if node.next_node(descend=False, siblings=True):
        self.body.append(' + text(", ")')
        self._desc_parameter_has_content = True
```
```python
# Add separator before opening paren
if self.in_list_item and self.list_item_needs_separator:
    self.body.append("\n")
self.body.append('text("(") + ')
```

**Target implementation (RESEARCH.md Part 3.1):**
```python
def visit_desc_returns(self, node: addnodes.desc_returns) -> None:
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")
    self.add_text('text(" -> ")')
    if self.in_list_item:
        self.list_item_needs_separator = True

def depart_desc_returns(self, node: addnodes.desc_returns) -> None:
    pass
```
Nested `reference` children inside `desc_returns` (resolved return-type xrefs) already stream through the unmodified `visit_reference` refid branch above — zero extra code needed for that case.

---

### DESC-02 — `visit_desc_signature_line`/`depart_desc_signature_line` + new `_is_first_desc_signature_line` state

**Analog (existing "is-first" flag idiom to mimic):** `_desc_parameter_has_content`, first set in `visit_desc_parameterlist` (translator.py:2798-2800):
```python
self.in_desc_parameter = True
self._desc_parameter_has_content = (
    False  # First parameter doesn't need + before it
)
```
and consumed in `depart_desc_parameterlist` (translator.py:2805-2807):
```python
if self._desc_parameter_has_content:
    self.body.append(" + ")
self.body.append('text(")")')
```

**Analog for where new instance state is declared:** `self._desc_parameter_has_content: bool = (...)` at translator.py:85 (in `__init__`).

**Target implementation (RESEARCH.md Part 3.2 — CRITICAL: uses Typst `linebreak()`, NOT a source `\n`, which is proven cosmetic-only via direct `typst.compile()`):**
```python
# In __init__, alongside other "is_first_*" state:
self._is_first_desc_signature_line: bool = True

def visit_desc_signature(self, node: addnodes.desc_signature) -> None:
    dummy_strong = nodes.strong()
    self.visit_strong(dummy_strong)
    self._is_first_desc_signature_line = True  # reset per signature

def visit_desc_signature_line(self, node: addnodes.desc_signature_line) -> None:
    if not self._is_first_desc_signature_line:
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
        self.add_text("linebreak()")
        if self.in_list_item:
            self.list_item_needs_separator = True
    self._is_first_desc_signature_line = False

def depart_desc_signature_line(self, node: addnodes.desc_signature_line) -> None:
    pass
```
Note this MODIFIES the existing `visit_desc_signature` (currently translator.py:2717-2725, dummy-`strong()`-delegation, do not otherwise change) to add the one-line reset. `linebreak()` is Typst stdlib, first use in this codebase — no new import.

---

### DESC-03 — `visit_desc_optional`/`depart_desc_optional`

**Analog (exact idiom — literal wrap reusing the shared flag, `+`-join convention):** `visit_desc_parameterlist`/`depart_desc_parameterlist`, translator.py:2783-2808 (full text already captured above under DESC-01/state section).

**Target implementation (RESEARCH.md Part 3.3 — recursion-safe by construction, no depth tracking needed since nested `desc_optional` is a structural sibling in the doctree, not something the handler needs to know about):**
```python
def visit_desc_optional(self, node: addnodes.desc_optional) -> None:
    if self._desc_parameter_has_content:
        self.add_text(" + ")
    self.add_text('text("[")')
    self._desc_parameter_has_content = True

def depart_desc_optional(self, node: addnodes.desc_optional) -> None:
    self.add_text(' + text("]")')
    self._desc_parameter_has_content = True
```
Reuses `_desc_parameter_has_content` (translator.py:85, :2798) — zero new state.

---

### DESC-04 — `visit_desc_inline`/`depart_desc_inline`

**Analog (pure pass-through pair):** `visit_desc_content`/`depart_desc_content`, translator.py:2735-2743:
```python
def visit_desc_content(self, node: addnodes.desc_content) -> None:
    """
    Visit a desc_content node (API description content).
    """
    pass

def depart_desc_content(self, node: addnodes.desc_content) -> None:
    """Depart a desc_content node."""
    pass
```

**Target implementation (RESEARCH.md Part 3.4 — D-06's predicate is simply node-type dispatch; `desc_inline` must NEVER delegate to `visit_strong` the way `visit_desc_signature` does at translator.py:2717-2725):**
```python
def visit_desc_inline(self, node: addnodes.desc_inline) -> None:
    pass

def depart_desc_inline(self, node: addnodes.desc_inline) -> None:
    pass
```
**Anti-pattern:** do not mimic `visit_desc_signature`'s dummy-`strong()` delegation for `desc_inline` — that reintroduces the `strong()` wrapper D-06 requires suppressed.

---

### BLK-01 — `visit_transition`

**Analog (emit-literal-then-SkipNode shape):** `visit_comment`, translator.py:419-432 (SkipNode-only variant, no literal emitted):
```python
def visit_comment(self, node: nodes.comment) -> None:
    """
    Visit a comment node.

    Comments are skipped entirely in Typst output as they are meant
    for source-level documentation only.
    """
    raise nodes.SkipNode
```
`visit_raw`'s conditional-content-then-SkipNode branch (translator.py:446-466) is the closer shape for "emit literal, then skip":
```python
if format_name == "typst":
    content = node.astext()
    if content:
        self.add_text(content)
        self.add_text("\n\n")
    raise nodes.SkipNode
```

**Target implementation (RESEARCH.md Part 4.1 — genuine content gap, `transition` renders nothing today):**
```python
def visit_transition(self, node: nodes.transition) -> None:
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")
    self.add_text("line(length: 100%)\n\n")
    if self.in_list_item:
        self.list_item_needs_separator = True
    raise nodes.SkipNode

def depart_transition(self, node: nodes.transition) -> None:
    pass  # unreached; kept for symmetry with visit_index/depart_index convention
```

---

### BLK-04 — `visit_glossary`/`depart_glossary` (thin pass-through; real fix is `depart_term` above)

**Analog:** `visit_desc_content`/`depart_desc_content`, translator.py:2735-2743 (pure `pass`/`pass`, same shape as above).

**Target implementation (RESEARCH.md Part 4.2):**
```python
def visit_glossary(self, node: addnodes.glossary) -> None:
    pass

def depart_glossary(self, node: addnodes.glossary) -> None:
    pass
```
Content already flows through `visit_definition_list` (translator.py:1070-1105) unmodified — do NOT duplicate the anchor fix here; it belongs solely in `depart_term` (XREF-01 section above).

---

### BLK-05 — `visit_tabular_col_spec`

**Analog (bare unconditional SkipNode, no depart):** `visit_index`, translator.py:2645-2651:
```python
def visit_index(self, node: addnodes.index) -> None:
    """
    Visit an index node.

    Index entries are skipped in Typst/PDF output as we don't generate indices.
    """
    raise nodes.SkipNode
```

**Target implementation (RESEARCH.md Part 4.3):**
```python
def visit_tabular_col_spec(self, node: nodes.Node) -> None:
    raise nodes.SkipNode
```
No `depart_tabular_col_spec` needed (unreached, matching `visit_index`'s convention where a depart is still defined for symmetry — optional here since node is self-closing with no children).

---

### BLK-06 — `visit_abbreviation`/`depart_abbreviation`

**Analog (dummy-Text-node delegation to reuse `visit_Text`'s escaping):** `visit_title_reference` (translator.py:2913) and `visit_literal_strong`/`visit_literal_emphasis` (translator.py:2977, 2989) — same file, same dummy-node-delegation idiom already used 3x; read the exact `visit_literal_strong` body if the executor needs the literal source (translator.py:2977-2989 region, not reproduced here since RESEARCH.md's target snippet below already demonstrates the pattern directly).

**Target implementation (RESEARCH.md Part 4.4 — D-08 stateless, expands every occurrence):**
```python
def visit_abbreviation(self, node: nodes.abbreviation) -> None:
    pass  # let the term's own Text child render via the normal chain

def depart_abbreviation(self, node: nodes.abbreviation) -> None:
    explanation = node.get("explanation", "")
    if explanation:
        # Route through the existing visit_Text escaping/separator regime
        # (dummy-node delegation, same idiom as visit_title_reference /
        # visit_literal_strong) rather than a bespoke f-string interpolation.
        dummy_text = nodes.Text(f" ({explanation})")
        self.visit_Text(dummy_text)
```
**Anti-pattern:** do not use `node.astext()` to build the expansion string — bypasses `visit_Text`'s escaping regime (carried-forward Pitfall 7 from Phase 11 research).

---

### Test file: `tests/test_pdf_render_gate.py` — 4 new test classes

**Analog:** existing Phase-11 GATE-01 fixture classes in the same file. Reuse the exact class-level decorator convention:
```python
LEAK_SIGNATURES = ("par({", 'text("', 'raw("')
# ... existing per-class pattern:
@pytest.mark.slow
@pytest.mark.skipif(not (TYPST_AVAILABLE and PYPDF_AVAILABLE), reason="...")
class TestXxxRenderGate:
    ...
```
New classes to add, one per handler group (per RESEARCH.md's Recommended Project Structure):
- `TestVersionModifiedRenderGate` — fixture dir `tests/fixtures/version_modified_render_gate/`
- `TestXrefRefidRenderGate` — fixture dir `tests/fixtures/xref_refid_render_gate/` (MUST include both a resolving `:ref:` section-anchor and a `:term:` glossary ref per D-04)
- `TestDescSignatureRenderGate` — fixture dir `tests/fixtures/desc_signature_render_gate/`
- `TestTrivialBlocksRenderGate` — fixture dir `tests/fixtures/trivial_blocks_render_gate/`

Each asserts: real `typst.compile()` succeeds (no fatal), expected content substrings present in `pypdf`-extracted text, and no `LEAK_SIGNATURES` present — never string-only assertions on the `.typ` source (Pitfall 9).

## Shared Patterns

### Dummy-node delegation (reuse existing visitor state machinery)
**Source:** `visit_emphasis`/`depart_emphasis` (translator.py:556-624); also used by `visit_title_reference`, `visit_literal_strong`, `visit_literal_emphasis`, `visit_desc_signature` (dummy `strong()`).
**Apply to:** VER-01 (`visit_inline` classed dispatch → dummy `nodes.emphasis()`), BLK-06 (`depart_abbreviation` → dummy `nodes.Text(...)`).
```python
dummy_emph = nodes.emphasis()
self.visit_emphasis(dummy_emph)
# ... later ...
self.depart_emphasis(dummy_emph)
```

### Bracket-wrap markup-mode label attachment
**Source:** `visit_title`/`depart_title` (translator.py:230-279), previously also applied to `visit_figure` in Phase 11.
**Apply to:** `depart_term` fix (XREF-01/BLK-04 companion fix — required, not optional).
```python
term_content = f"[#{{{term_content}}} <{label_id}>]"
```
**Never** use `+`-join to attach a `label(...)` to content — proven to raise `TypstError: cannot add content and label`.

### List-item separator bookkeeping (`in_list_item` / `list_item_needs_separator`)
**Source:** pervasive throughout the file; canonical instance at `visit_desc_parameterlist` (translator.py:2789-2794) and `depart_desc_parameter` (translator.py:2818-2827).
**Apply to:** every new literal-emitting visitor (`visit_desc_returns`, `visit_desc_signature_line`, `visit_transition`) — must check/set `self.in_list_item`/`self.list_item_needs_separator` around any `add_text` call so output composes correctly inside list items.

### `raise nodes.SkipNode` primitive
**Source:** `visit_comment` (translator.py:419-432), `visit_index` (translator.py:2645-2651), `visit_raw`'s non-typst branch.
**Apply to:** BLK-05 (`visit_tabular_col_spec`), BLK-01 (`visit_transition`, after emitting the literal `line(...)` content — it has no children to descend into).

### "Is-first" state-flag idiom for new instance state
**Source:** `_desc_parameter_has_content` (declared translator.py:85, set in `visit_desc_parameterlist` :2798-2800, consumed in `depart_desc_parameterlist` :2805-2807).
**Apply to:** the one genuinely new state variable this phase introduces, `_is_first_desc_signature_line` (DESC-02) — same declare-in-`__init__`, reset-per-container, consume-in-child-visitor shape.

## No Analog Found

None. Every file/handler in this phase has a strong, cited, same-file analog — consistent with RESEARCH.md's framing that this phase is "deliberately LOW-NOVELTY" and CONTEXT.md's mandate to reuse already-proven patterns rather than invent new machinery.

## Metadata

**Analog search scope:** `typsphinx/translator.py` (single file, ~2999 lines), `tests/test_pdf_render_gate.py`, `tests/fixtures/*_render_gate/` (Phase-11 fixture dirs as structural templates).
**Files scanned:** 1 production file (full grep of all `visit_*`/`depart_*`/`SkipNode` sites), plus targeted reads of 6 line ranges (556-655, 1060-1160, 2072-2200, 2621-2700, 2717-2836, 419-467, 230-284, 1159-1173).
**Pattern extraction date:** 2026-07-12
**Line-number caveat:** Line numbers cited above were re-verified against the current repository state in this session (post-Phase-11) via direct `grep -n` + `Read`, not carried forward from RESEARCH.md/CONTEXT.md's earlier pass — they matched RESEARCH.md's citations within ±3 lines in all cases checked.
