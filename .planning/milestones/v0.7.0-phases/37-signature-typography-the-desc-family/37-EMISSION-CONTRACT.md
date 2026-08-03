# Phase 37 — Emission Contract

**Authored:** 2026-08-01 (plan-phase)
**Status:** normative for every Phase 37 plan
**Purpose:** the single, hand-derivable specification of exactly what byte sequence each
`desc_*` handler emits after Phase 37. Every expected string in this phase — the new gates, the
migrated pre-existing assertions, and `golden.typ` — is derived **from this document**, never from
running the new code (ROADMAP SC#5, milestone invariant #4).

Every number and every Typst construct below was **measured this session (2026-08-01)** against the
real `typst-py` 0.15.0 compiler, the real `sphinx-build`, and real `pypdf` 6.14.2. Measurements are
labelled `[measured]`. Nothing here rests on recall.

---

## 0. Why this document exists

ROADMAP SC#5 and milestone invariant #4 forbid regenerating expected strings from the new code's own
output. That is only enforceable if there is a specification precise enough that a human (or an
executor with no access to the new code) can write the expected bytes down first. This document is
that specification. If an assertion and this document disagree, **fix the assertion by re-deriving
from this document** — never by pasting what the translator printed.

---

## 1. New module-level constant (D-08)

```python
# typsphinx/translator.py, module scope, immediately after _TYPST_PASSTHROUGH_UNITS
# (currently line 21) and before `def escape_typst_string`.

SHARED_INDENT_STEP = "2.5em"
```

- **Name:** `SHARED_INDENT_STEP` — public (no leading underscore) because D-08 designates it as *the*
  shared cross-phase indent quantum, and named for its role rather than its first consumer, so
  Phase 38's IND-04 can reuse it for `desc_content`, `field_list`, and `block_quote` without the name
  reading as signature-specific.
- **Value:** `"2.5em"` per D-06 (owner-chosen after compiling and comparing three renderings). This
  also sits inside REQUIREMENTS.md's measured reference quantum (≈2.2–2.5em at 10pt).
- **Docstring requirement:** the constant carries a comment stating that Phase 38 IND-04 reuses this
  exact constant and that a second indent number must not be introduced.

---

## 2. New translator state

| Attribute | Initialised | Set | Cleared | Read by |
|---|---|---|---|---|
| `self.in_signature_text` | `__init__`, `False` (alongside `self.in_literal_block`, currently line 139) | `visit_desc_signature`, immediately before the wrapper literal is emitted | `depart_desc_signature`, immediately after the closing literal is emitted and before the anchor loop | `visit_Text` |
| `self._param_name_seen` | `__init__`, `False` | `visit_desc_parameter` resets it to `False` on entry | — | `visit_desc_sig_name` |
| `self._desc_break_marker` | `__init__`, `None` | `depart_desc`, after a `parbreak()` is emitted | — | `depart_desc` |

`self.in_signature_text` is a plain scalar, not a stack: `desc_signature` never nests inside
`desc_signature`. `self._param_name_seen` is likewise a scalar: `desc_parameter` never nests inside
`desc_parameter` (a `desc_optional` group contains `desc_parameter` siblings, and each one resets the
flag on entry). Both mirror the non-reentrancy argument already documented at
`typsphinx/translator.py:4642-4651` for `_is_first_desc_signature`.

---

## 3. The `desc_signature` wrapper (D-10, SIG-07 + SIG-09)

> **Post-Wave-3 amendment (2026-08-01, plan 37-09, gap closure).** The post-merge gate caught a
> regression the original `above: 0pt, below: 0pt` mandate below introduced: every signature's
> glyphs overlapped the first line of its own description body, reproduced on a rasterised page
> on two independent fixtures (`37-SPACING-FINDING.md`). This section's wrapper-open string and
> its `[measured]` justification paragraph are REPLACED below with a corrected, independently
> re-measured wrapper and figures. The paragraph that follows is the amended text; nothing above
> this note or below the amended block was changed by this amendment.

**Open** — `visit_desc_signature`, replacing the single literal currently produced by
`f"{prefix}strong({{"` at the end of the verbatim-`visit_strong` block:

```
block(sticky: true, par(hanging-indent: 2.5em, {
```

built as `f"{prefix}block(sticky: true, par(hanging-indent: {SHARED_INDENT_STEP}, {{"`.

**Close** — `depart_desc_signature`, replacing the literal `"})"`:

```
}))
```

(one `}` closing the content block, one `)` closing `par(`, one `)` closing `block(`).

`above`/`below` are **no longer overridden** — Typst's own `block()` default spacing is used.
`[measured, re-verified 2026-08-01 in this worktree]` Measured via `context measure(...)` deltas
(`measure(preceding + signature) - measure(preceding) - measure(signature)`, at this project's own
11pt document text size, inside real paragraph flow — not an isolated probe): the current
`block(above: 0pt, below: 0pt, sticky: true, ...)` wrapper produces **exactly 0pt** of vertical gap
on BOTH the above-side (signature vs. the paragraph before it) and the below-side (signature vs. the
body paragraph after it). That is the defect: zeroing both removes ALL separation, not a redundant
amount, so the signature's own line box sits directly against the following paragraph's line box
with nothing between them. `block(sticky: true, ...)` (no `above`/`below` override) produces
**13.2pt** on both sides — and this is byte-for-byte identical to the gap between two ordinary,
un-wrapped paragraphs in sequence at the same text size (also measured at 13.2pt = Typst's default
1.2em block/paragraph spacing at 11pt), confirming that dropping the override restores exactly the
paragraph-to-paragraph spacing a signature had before Phase 37 wrapped it in a `block()` at all.

The original figures (14.39pt plain-flow baseline / 40.88pt with `block()` defaults / 14.48pt with
both zeroed) came from a probe that did not carry the surrounding paragraph flow. Reconstructing
that probe's likely shape in this worktree: placing a zero-height `context`/`metadata()` marker
directly after the block, with no intervening paragraph break, reports the SAME position regardless
of the block's `below` value (0pt, 0.5em, and 1.2em all queried identically) — the `below` margin
only materializes once genuine block-level content follows and collapses against it, so a probe
built that way cannot distinguish `0pt` from `1.2em` of `below` spacing and produces a number that
reflects the probe's own shape rather than the applied spacing. Because of that blind spot, the
original measurement could not have caught that zeroing both sides removes literally all
separation, not a supposed ~26.5pt "redundant" amount.

The original stated fear — "would reintroduce a SIG-08-shaped doubled-gap defect in a new form" —
is **SUPERSEDED**: plan 37-05 already removed the duplicate `parbreak()` at its emission source (the
`depart_desc` emission-position marker, contract §8), so a nested `py:method::` inside a
`py:class::` no longer emits two consecutive breaks for block-spacing collapse to double up on. This
was verified by re-rendering `tests/fixtures/signature_break_and_arrow_gate` (the SIG-08 nested-desc
fixture) under the corrected `block(sticky: true, ...)` wrapper via
`typst.compile(format="png", ppi=140)`: the outer class signature, its body, the nested method
signature, and its body all show uniform, single-gap spacing on the rasterised page — no doubled
gap, and (unlike the current zeroed wrapper) no overlap either.

The D-10 binding constraint remains satisfied: this is still ONE wrapper, carrying both SIG-07's
hanging indent and SIG-09's keep-with-next (`sticky: true`) — nothing in this amendment adds a
second wrapper for Phase 38's `desc_content` to nest inside redundantly.

`[measured]` The full wrapper compiles under `typst-py` 0.15.0 inside a real generated-document code
block, together with `strong(raw(...))`, `emph(raw(...))`, `raw("\u{2192}")`, and
`link(<label>, raw("Foo"))`.

**Everything else in `visit_desc_signature`/`depart_desc_signature` is byte-unchanged**: the
`_add_paragraph_separator()` / `_enter_inline_concat_element()` / `in_paragraph` / `in_list_item` /
`list_item_needs_separator` save-restore block, the FID-03 sibling `linebreak()`, the
`_is_first_desc_signature_line` reset, the `_exit_inline_concat_element()` call, and the
`[#metadata(none) <label>]` anchor loop plus its trailing `"\n"`.

---

## 4. Monospace propagation (D-04, D-05 Pattern 1)

`visit_Text` gains one new branch, placed **after** the existing `in_literal_block` early return and
**before** the FID-11 soft-wrap collapse:

1. collapse embedded newlines to a single space (same as the existing path);
2. `escaped = escape_typst_string(text_content)` — the shared helper, never re-derived;
3. `escaped = escaped.replace(".", ".\\u{200B}")` — **after** escaping (step order is load-bearing:
   `escape_typst_string` doubles backslashes, so injecting first would emit `\\u{200B}`, a literal
   backslash-u rather than the escape). `.` is neither produced nor consumed by escaping, so the
   order is safe in the other direction;
4. `self._add_paragraph_separator()`;
5. `if not self._emit_inline_concat_separator(): if self.in_list_item and self.list_item_needs_separator: self.add_text("\n")`;
6. emit `f'{prefix}raw("{escaped}")'` with the same `prefix = "#" if self._in_markup_mode else ""`;
7. `if not self._mark_inline_concat_content(): if self.in_list_item: self.list_item_needs_separator = True`;
8. `return`.

Steps 4, 5, 7 are byte-identical to the existing `text(...)` path — **only the wrapper call name and
the ZWSP injection differ.** Do not use `in_literal_block`'s bare `add_text(text_content)` shape: it
skips escaping and all separator bookkeeping, which is wrong here.

### 4.1 The ZWSP form (D-07, SIG-07)

The zero-width space is emitted as the **8-character Typst escape** `\u{200B}`, not as a literal
invisible U+200B byte. Rationale: the escape is greppable, diffable, and hand-derivable in a golden
file, where an invisible byte is none of those. `[measured]` `raw("a.\u{200B}b")` compiles and Typst
breaks the line at that point.

Injection is **blanket over every signature text run**, after each `.`, mirroring `visit_literal`'s
existing unconditional in-table injection (`typsphinx/translator.py:1317`). No length threshold —
a threshold is an untestable discontinuity.

### 4.2 ZWSP hazard for compiled-PDF assertions `[measured]`

Once ZWSP is present anywhere in a document, `pypdf.extract_text()` returns U+200B **both** where the
translator injected it **and, spuriously, at unrelated glyph boundaries** (a control document with no
ZWSP extracts clean; the same document with ZWSP present extracted, in Python `repr` notation,
`'453.<U+200B>54pt'` — from text containing no injected ZWSP at all). **Every compiled-PDF text
assertion in this phase must normalise
by stripping U+200B before comparing.** A test that omits the strip will flake in a way that looks
like a rendering bug.

### 4.3 Nodes that get monospace "for free"

These have no dedicated handler and must stay untouched — the flag alone gives them `raw(...)`:
`desc_sig_keyword`, `desc_sig_space`, `desc_sig_punctuation`, `desc_sig_operator`, `desc_addname`,
`inline.default_value`, `desc_sig_literal_string`, `desc_sig_literal_number`, and — found by
measurement this session, named in neither CONTEXT.md nor RESEARCH.md — **`desc_sig_keyword_type`**
(the C/C++ domain's `void`/`int`; `[measured]` present in
`tests/fixtures/desc_signature_render_gate/index.rst`'s `cpp:function` signature). Adding handlers for
any of these is out of scope.

`desc_addname` getting nothing but the flag **is** SIG-02: regular-weight monospace, no `strong(`.

---

## 5. Per-sub-part wrappers (D-01, SIG-01/SIG-03/SIG-04)

### 5.1 `visit_desc_name` and `visit_desc_annotation` — identical treatment (SIG-03)

Both handlers take the same shape, mirroring `visit_literal`'s preamble
(`typsphinx/translator.py:1282-1360`):

- If **every** child is a `nodes.Text` instance (the py / option / c / rst-domain case):
  `_add_paragraph_separator()`; the `_emit_inline_concat_separator()` fallback; emit
  `f'{prefix}strong(raw("{escaped}"))'` where `escaped = escape_typst_string(node.astext())` with the
  §4.1 ZWSP injection applied; the `_mark_inline_concat_content()` fallback; then
  `raise nodes.SkipNode`.
- Otherwise (`[measured]` the C++ case, where `desc_name` wraps a `desc_sig_name` which wraps `Text`):
  **stay `pass`**. The nested `desc_sig_name` picks up rule 5.2-(1) below and emits the bold form
  itself. This avoids `node.astext()` flattening a subtree, which is the RESEARCH Pitfall 3 hazard.

`depart_desc_name`'s existing `if self.in_list_item: self.list_item_needs_separator = True` is
**functionally preserved** through the `_mark_inline_concat_content()` fallback in the leaf branch
(`SkipNode` means `depart_desc_name` is not called), and remains reachable and unchanged in the
non-leaf branch.

### 5.2 `visit_desc_sig_name` — the D-05 discriminator

Three mutually exclusive rules, evaluated in order:

1. **Parent is `desc_annotation` or `desc_name`** → emit `strong(raw("<escaped>"))` and
   `raise nodes.SkipNode` (leaf only; if the node is not a text-only leaf, fall through to rule 3).
   This is what makes the C++ non-leaf `desc_name` bold.
2. **Parent is `desc_parameter`, the node is a text-only leaf, and `self._param_name_seen` is
   `False`** → set `self._param_name_seen = True`, emit `emph(raw("<escaped>"))`, and
   `raise nodes.SkipNode`. This is the parameter's own name (SIG-04's italic).
3. **Otherwise** → `pass`. Children dispatch normally under `in_signature_text`, so a type annotation
   that wraps a resolved cross-reference emits `link(<label>, raw("Foo"))` with the hyperlink intact.

Rule 2's leaf guard is the load-bearing safety property. `[measured]` across every shape in
RESEARCH.md's D-05 table plus the C++ domain, the **first** `desc_sig_name` direct child of a
`desc_parameter` is always the parameter's own name and always a leaf; every later one is part of the
type annotation and may be a non-leaf. Rule 3 is what keeps a non-leaf structural.

**Do not** discriminate on `addnodes.pending_xref`. `[measured]` the translator never sees one:
`Builder.write()` resolves references before `write_doc`, so an unresolved xref is stripped to plain
content and a resolved one becomes `nodes.reference`. A `pending_xref` check would silently never
fire.

`self._param_name_seen` is reset to `False` in `visit_desc_parameter` (currently `pass`), mirroring
the `_desc_parameter_has_content = False` reset idiom in `visit_desc_parameterlist`.

`[measured]` C++ parameters put the *type* in a `desc_sig_keyword_type` node, not a `desc_sig_name`,
so rule 2 correctly italicises `x` in `void f(int x)` and leaves `int` regular.

---

## 6. Delimiters (SIG-05) and the D-11 separator

Every delimiter literal in the parameter-list family swaps its call name from the text primitive to
`raw(...)`. The surrounding `+` / `_desc_parameter_has_content` bookkeeping is **unchanged**.

| Site (pre-phase line) | Pre-phase literal | Phase 37 literal |
|---|---|---|
| `visit_desc_parameterlist` (4926) | opening paren, text primitive, with a trailing `" + "` | `'raw("(") + '` |
| `depart_desc_parameterlist` (4941) | closing paren, text primitive | `'raw(")")'` |
| `depart_desc_parameter` (4961) | comma-space, text primitive | `' + raw(", ")'` |
| `visit_desc_optional` (4977) | open bracket, text primitive | `'raw("[")'` |
| `depart_desc_optional` (4983) | close bracket, text primitive | `' + raw("]")'` |

### 6.1 D-11 — the dropped optional-group separator

`depart_desc_optional` gains one guarded emission **before** the closing bracket:

```python
if node.next_node(descend=False, siblings=True):
    self.add_text(' + raw(", ")')
self.add_text(' + raw("]")')
self._desc_parameter_has_content = True
```

The sibling test is against **the `desc_optional` node itself**, mirroring what
`depart_desc_parameter` already does for a `desc_parameter`'s own following sibling — not against
`desc_optional`'s last child.

`[measured]` targets and controls:

| Source | Sphinx HTML renders `[measured]` | Pre-phase typsphinx `[measured]` | Phase 37 target |
|---|---|---|---|
| `connect(host, port=8080, [timeout], **kwargs)` | `connect(host, port=8080, [timeout, ]**kwargs)` | `connect(host, port=8080, [timeout]**kwargs)` | `connect(host, port=8080, [timeout, ]**kwargs)` |
| `printf(fmt[, args[, more]])` | — | `printf(fmt, [args, [more]])` | **unchanged** — both `desc_optional`s are last children, so neither gains a comma. This is the D-11 non-regression control. |

### 6.2 Correction to CONTEXT.md D-11's "cosmetic half" `[measured]`

CONTEXT.md D-11 states that the closing bracket and the following `**kwargs` are emitted as two
juxtaposed calls with no `+` joining them. **That is not reproducible on the current tree.** A real
`-b typst` build of exactly CONTEXT's source line emits an explicit ` + ` between them
(`... + text("[") + text("timeout") + text("]") + text("**kwargs") + text(")")`), because
`depart_desc_optional` already sets `_desc_parameter_has_content = True` and the next parameter's
text run therefore takes `_emit_inline_concat_separator()`'s `" + "` branch.

**Disposition:** the D-11 obligation is *not* dropped — it converts from a fix into a
**non-regression assertion**. The phase must assert that the closing bracket and the following
parameter expression remain explicitly `+`-joined after the rewrite. No code change is required for
that half.

---

## 7. The return arrow (D-13, SIG-06)

`visit_desc_returns` (4810-4823): the single emitted literal changes; the
`in_list_item`/`list_item_needs_separator` bookkeeping around it is unchanged.

Phase 37 literal: `'raw(" ") + raw("\\u{2192}") + raw(" ")'` — emitting the three-expression Typst
form `raw(" ") + raw("\u{2192}") + raw(" ")`.

`[measured]` this exact form compiles and `pypdf.extract_text()` reports `→` present and the ASCII
two-character arrow absent. The three-part form (rather than a single `raw(" → ")`) is the one that
was actually compiled and extracted, so it is the specified target.

---

## 8. `depart_desc`'s doubled break (D-12, SIG-08)

`[measured]` root cause reproduced on the current tree: a `py:method::` nested inside a `py:class::`
emits two consecutive `parbreak()` statements with nothing between them, because `depart_desc` fires
unconditionally for the inner `desc` and again for the outer one, and `depart_desc_content` is `pass`.

**Fix — emission-position marker, mirroring the `_is_first_desc_signature` scalar-flag idiom:**

```python
def depart_desc(self, node):
    if not getattr(self, "in_table", False) and self._desc_break_marker == len(self.body):
        return                      # nothing emitted since the previous desc's parbreak()
    self._emit_forced_break("parbreak()")
    self._desc_break_marker = len(self.body)
```

The early return deliberately does **not** update the marker, so three levels of nesting still yield
exactly one `parbreak()`.

**Do not implement this as a desc-nesting-depth counter.** A depth counter suppresses the *inner*
desc's break, which is wrong whenever the outer `desc_content` continues with more content after the
nested member (the method and the following paragraph would run together). The correct discriminator
is "was anything emitted between the two departs", not "how deep am I".

The `not self.in_table` guard exists because `add_text` routes into `table_cell_content` rather than
`self.body` inside a table, where `len(self.body)` would not advance and the suppression would fire
wrongly. Inside a table the pre-phase unconditional behaviour is retained.

**Sibling body-less `desc` nodes are unaffected** — `visit_desc` emits id anchors and the next
signature emits its wrapper, so `len(self.body)` always advances between two sibling departs. The
existing `tests/test_desc_bodyless_concat_render_gate.py` gate must stay green; it is the control.

The FID-03 sibling `linebreak()` mechanism in `visit_desc_signature` is a **different** mechanism
solving a different problem (separating signature *lines* within one visual block) and is left
untouched. The two do not converge.

---

## 9. Worked derivation — `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ`

`[measured]` doctree of that fixture's five `desc_signature` nodes (dumped this session via
`env.get_and_resolve_doctree`):

| Signature | Children |
|---|---|
| `connect(host, port, timeout=30)` | `desc_name>Text`; `desc_parameterlist` → 3 × `desc_parameter`; params: `desc_sig_name['host']`, `desc_sig_name['port']`, (`desc_sig_name['timeout']`, `desc_sig_operator['=']`, `inline.default_value['30']`) |
| `compile(source)` | `desc_name>Text`; 1 × `desc_parameter>desc_sig_name` |
| `compile(source, filename)` | `desc_name>Text`; 2 × `desc_parameter>desc_sig_name` |
| `compile(source, filename, symbol)` | `desc_name>Text`; 3 × `desc_parameter>desc_sig_name` |
| `--sep` (`.. option::`) | `desc_name>Text['--sep']`; `desc_addname` with **zero children** |

Applying §3, §5.1 (all five `desc_name`s are text-only leaves), §5.2 rule 2 (every parameter's single
`desc_sig_name` is its first, and a leaf), and §6:

**Line 26–27 becomes:**

```
block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("connect"))
raw("(") + emph(raw("host")) + raw(", ") + emph(raw("port")) + raw(", ") + emph(raw("timeout")) + raw("=") + raw("30") + raw(")")}))
```

**Lines 36–37, 40–41, 43–44 become:**

```
block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("compile"))
raw("(") + emph(raw("source")) + raw(")")}))
```
```
block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("compile"))
raw("(") + emph(raw("source")) + raw(", ") + emph(raw("filename")) + raw(")")}))
```
```
block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("compile"))
raw("(") + emph(raw("source")) + raw(", ") + emph(raw("filename")) + raw(", ") + emph(raw("symbol")) + raw(")")}))
```

**Line 59 becomes:**

```
block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("--sep"))}))
```

(the empty `desc_addname` contributes zero bytes and no separator — as it does today).

**Lines that must remain byte-identical**, and whose unchanged state in the diff is itself the
evidence that Phase 37 touched only signatures (D-14 option 1):

- the three rubric lines at 57, 75, 87 (`Options`, `A Rubric In A List Item`, `Trailing Heading`) —
  Phase 39 territory, still routed through the unmodified `visit_rubric`;
- the plain-bold regression control at line 51;
- the `list({ … })` bullet structure at 66–82;
- every `par({text(...)})` body paragraph, every `[#metadata(none) <…>]` anchor, every `linebreak()`
  and every `parbreak()` (the fixture contains no nested `desc`, so §8 does not touch it);
- the whole preamble, lines 1–25.

**No ZWSP appears anywhere in this file** — none of the five signatures contains a `.` inside a
signature text run. If a `\u{200B}` shows up in the rebuilt output for this fixture, something is
wrong with §4.1's scope, not with the golden.

---

## 10. SIG-07 measurement basis `[measured]`

All widths read via Typst's own `context measure(...)` / `context layout(size => size.width)`
compiled through `typst.compile()`, at A4 / 2.5cm margins / 11pt — the project's own template
geometry. `pypdf`'s `extract_text(visitor_text=...)` is **not** usable for this (it reports
`x=0, y=0` for per-glyph positions on Typst PDFs in this sandbox).

| Quantity | Width |
|---|---|
| Available text column | **453.54pt** |
| Synthetic RED token: `typsphinx.overflow.probe.deeply.nested.package.namespace.segment.alpha.beta.gamma.delta.OverflowProbeDocumenter` (111 chars) as the pre-phase proportional text primitive | **542.16pt** — overflows by 88.62pt |
| The same token as `raw(...)` with no break opportunity | **588.08pt** — overflows by 134.54pt |
| Its longest ZWSP-delimited segment, `OverflowProbeDocumenter`, as `raw(...)` | **121.86pt** — fits |
| Real-corpus worst unbroken token (RESEARCH, Sphinx v9.1.0 `doc/`, 1,445 signatures) | 143pt — fits, before and after |

**Consequences that must survive into every SIG-07 assertion:**

- `measure()` of the *whole* identifier is **identical with and without** ZWSP (588.08pt either way) —
  ZWSP creates a break *opportunity*, it does not change measured width. An assertion that measures
  the whole token can therefore never go from RED to GREEN. The assertion must measure **each
  ZWSP-delimited segment** and bound the maximum.
- The RED fixture must be the **synthetic** identifier above. The real corpus does not overflow at
  production width, so a corpus-derived fixture is GREEN against the pre-phase translator and proves
  nothing. The real-corpus worst case is kept as a **non-regression control** — expected green both
  before and after — and must be labelled as such so nobody "repairs" it into the RED case.
- The column width is **read from the compiled probe**, never hard-coded, so the assertion follows a
  future page-geometry change.

---

## 11. Pre-existing exact-string blast radius (SC#5 census input)

Verified by reading the assertions this session, not by grepping node names.

**Will break — hand-migrate to the shapes above:**

| File | Assertion | Breaks at |
|---|---|---|
| `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` | 7 signature lines (§9) | §3 + §5 + §6 |
| `tests/test_desc_signature_concat_render_gate.py:269,282` | `typ_text.index('strong({text("compile")')`, `('strong({text("solo")')` | §3 + §5.1 |
| `tests/test_rubric_option_concat_render_gate.py:134,150` | `'strong({text("--sep")})'`; check line 150's `Trailing Heading` — that one is a **rubric** and must stay | §3 + §5.1 |
| `tests/test_desc_sig_space_render_gate.py` | asserts spacing on the signature run (FID-08) | §3 + §4 |
| `tests/test_translator.py:3371` (`test_desc_signature_rendering`) | `"strong({" in output` | §3 |
| `tests/test_translator.py:3399` (`test_desc_with_annotation_and_name`) | `'strong({text("class")'` and `'text("TypstBuilder")'` | §3 + §5.1 |
| `tests/test_translator.py:3437` (`test_desc_parameterlist`) | `'strong({text("function")'` | §3 + §5.1 |
| `tests/test_translator.py:3679` (`test_full_api_description_structure`) | `'strong({text("class")'` | §3 + §5.1 |
| `tests/test_pdf_render_gate.py:780` (`test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline`) | `"-> int" in full_text` | §7 |

**Mentions the node family but asserts on something Phase 37 does not change — must stay green,
untouched, and serve as controls:**
`tests/test_confval_field_body_render_gate.py`, `tests/test_confval_field_spacing_render_gate.py`,
`tests/test_deflist_nested_definition_render_gate.py`, `tests/test_deflist_term_concat_render_gate.py`,
`tests/test_deflist_term_inline_children_gate.py`,
`tests/test_desc_container_propagated_target_render_gate.py`,
`tests/test_desc_signature_anchor_render_gate.py`, `tests/test_topics.py:133`,
`tests/test_translator.py:3597` (`test_rubric_rendering`), and every other function in
`tests/test_pdf_render_gate.py`.

**Conditionally at risk, re-verify after §8 lands:**
`tests/test_desc_bodyless_concat_render_gate.py` (sibling body-less `desc`, expected unaffected — it
is §8's control), and `tests/test_translator.py`'s three
`test_desc_signature_line_*_linebreak` functions (they count `linebreak()` and check bare content
substrings, both of which survive re-wrapping).

The `--sep` case in `tests/test_rubric_option_concat_render_gate.py` is an `.. option::`
**desc_signature**, not the rubric it is compared against — the rubric half of that same test
(`'strong({text("Structure Options")})'`) is Phase 39 territory and must not be touched.

---

## 12. Out of scope for Phase 37 (do not fold in)

- `visit_desc_content` / `depart_desc_content` — D-09, Phase 38 IND-01.
- New handlers for `desc_sig_literal_string` / `desc_sig_literal_number` / `desc_sig_keyword_type`
  (they are correct under §4.3's blanket flag; the `unknown_visit` warning is cosmetic). File a todo
  only if it proves noisy in the full-corpus gate log.
- Any `set text(font: …)` or font configuration — D-04 forbids it; `raw(...)` is the only monospace
  primitive.
- Renaming the shared `_strong_was_*` attributes — Phase 39's deferred `par()`-loss repair.
- Any new `@preview` package or version-lockstep site.

---

*Phase: 37 — Signature Typography — the `desc_*` Family*
*Emission contract authored: 2026-08-01, from direct measurement*
