# Phase 20: Signature Token Spacing (Cluster B) - Research

**Researched:** 2026-07-20
**Domain:** Sphinx-doctree-to-Typst-markup token-level spacing (`typsphinx/translator.py`)
**Confidence:** HIGH — every recommendation below was validated with a real `sphinx-build -b
typstpdf` + real `typst.compile()` + real `pypdf` text-extraction round-trip against a
temporary experimental patch (applied and reverted this session; `git status` confirmed clean
before and after). This is not textbook/training-data guidance — it is empirically observed
translator + Typst behavior in this exact repo, this exact typst-py 0.15.0 pin.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**FID-09 field rendering shape**
- **D-01:** Render `:type:`/`:default:` object-description fields **inline with restored
  spacing** — keep the current inline structure and restore (a) the colon-space after each
  field name and (b) inter-field boundary separation — targeting the exact ROADMAP SC#3 string
  `"Type: int (a number)  Default: 42"`. Central edit: `depart_field_name` `text(":")` →
  colon-space.
- **D-02:** Rejected the stacked definition-list block form; SC#3 pins the inline target string,
  so inline-with-spacing IS the acceptance bar for this phase.

**FID-08 C/C++ scope / completeness**
- **D-03:** Fix **all audited C/C++ inter-token forms** — `*`/`&`-adjacent, type↔identifier,
  keyword prefix, operator spacing ("a * f(a)"), `const…*`, `template<typename T…>`. SC#2
  literally requires "preserve **all** inter-token spaces."
- **D-04:** Rejected the space-node-backed subset only (deferring rare operator/template forms
  to Phase 21).

**FID-07/08 space token kind (wrap behavior)**
- **D-05:** Restore spaces as **normal breakable spaces** — matches the `-b html` authority's
  natural wrapping and keeps blast radius minimal.
- **D-06:** Rejected non-breaking spaces (would pre-empt Cluster C's margin-overflow work).

**Verification strategy (GATE-01)**
- **D-07:** Carry forward Phase 19's structural-floor requirement — every fixture MUST assert
  the generated `.typ` contains the expected content-space token at the correct site AND run a
  real `typst.compile()` producing a valid `%PDF`. **Additionally REQUIRED this phase:** a
  **pypdf extracted-text adjacency assertion** for the observable findings (e.g. "class sphinx"
  present / "classsphinx" absent for FID-07; "Py_ssize_t nitems" present / "Py_ssize_tnitems"
  absent for FID-08; "Type: int" / "Default: 42" spacing for FID-09).

### Claude's Discretion
- **Exact space-emission token & concat-awareness** — `text(" ")` vs a `+ text(" ") +` concat
  form vs `sym.space`/`~`; must be concat-context-aware (both `strong({…})` join block and
  `desc_inline` paragraph/inline-concat context). **RESOLVED by this research** — see
  "Architecture Patterns" below: neither a new concat form nor `sym.space`/`~` is needed. The
  fix is to STOP suppressing the existing `visit_Text` dispatch (see Pitfall 1).
- **Shared-idiom structure** (Phase 19's `_emit_forced_break` reaffirmed as default) — planner
  may keep FID-09's colon-space (`depart_field_name`) separate since it is a distinct mechanism.
  **RESOLVED by this research** — FID-07/FID-08 need **zero new helper code** (see below); no
  shared-idiom function is needed at all for this phase's fix.
- **Fixture granularity/placement** — one render-gate fixture per finding, recommended default;
  planner may consolidate if a shared fixture project cleanly exercises multiple findings.

### Deferred Ideas (OUT OF SCOPE)
- Stacked definition-list rendering for object-description fields (FID-09) — rejected (D-02);
  could be revisited as a future-milestone fidelity enhancement.
- Non-breaking-space signature cohesion — rejected (D-06); belongs to Cluster C (FID-10,
  Phase 21) if signature wrapping reads poorly.
- Cluster C margin overflow (FID-10) → Phase 21; Clusters D/E/F (FID-11..FID-14) → Phase 21;
  Issue #117 PDF naming (PDF-01) → Phase 22.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FID-07 | `desc_annotation` "class "/"exception " keyword prefix keeps its trailing space on every `py:class`/`py:exception`/`autoclass` | Root cause isolated to a single `SkipNode` short-circuit in `visit_desc_sig_space` (translator.py:4812-4817). Fix + real-compile validation below reproduces the exact pinned string "class sphinx.builders.html.StandaloneHTMLBuilder". |
| FID-08 | C/C++ `desc_signature` / inline `c:expr`/`cpp:expr` preserve ALL inter-token spaces | Empirically confirmed via a real Sphinx C/C++-domain AST dump (see "Architecture Patterns" → "Verified: FID-08 completeness") that EVERY audited form (`*`/`&`-adjacent, type↔identifier, keyword prefix, `a * f(a)` operator spacing, `const…*`, `template<typename T…>`) routes through `desc_sig_space` sibling nodes — the SAME single fix as FID-07 covers 100% of D-03's "all" requirement. No `desc_sig_operator`/`desc_sig_punctuation` change is needed. |
| FID-09 | `field_list` `:type:`/`:default:` fields render with colon-space and preserved field boundaries, matching the pinned string `"Type: int (a number)  Default: 42"` | Two small, independent edits (`depart_field_name` colon-space; `depart_field` inter-field double-space) reproduce the EXACT pinned string byte-for-byte, verified via `pypdf` text extraction against the audit's literal repro source (no-blank-line confval directive-option syntax) AND cross-checked against the real 219-confval Sphinx v9.1.0 corpus (`usage/configuration.rst`) — 100% of real confvals use the form these two edits fully resolve. |
</phase_requirements>

## Summary

All three findings trace to the SAME cosmetic-whitespace root-cause family Phase 19 already
proved and fixed at the block level ("a source `\n`/space between two Typst code-mode
statements is cosmetic-only — it satisfies the parser but produces zero rendered space").
Phase 20 is the *token*-level instance of that same bug, and — critically — the fix for FID-07
and FID-08 requires **writing zero new code**, only **deleting a bug**: `visit_desc_sig_space`
currently intercepts its own child `Text(" ")` node with `self.body.append(" ")` (raw Typst
*source* whitespace, syntactically insignificant) and then `raise nodes.SkipNode` (which
prevents the child `Text(" ")` node from ever reaching the translator's own fully
concat-context-aware `visit_Text` dispatch). Simply reducing `visit_desc_sig_space`/
`depart_desc_sig_space` to `pass`/`pass` (matching the four sibling `desc_sig_*` handlers
directly above and below it in the file) lets the existing, already-correct `visit_Text`
infrastructure emit a real `text(" ")` **content value** — which auto-joins into the visible
output exactly where the earlier bug swallowed it. This was proven end-to-end with a real
`typst.compile()` + `pypdf` extraction: "class sphinx.builders.html.StandaloneHTMLBuilder",
"PyObject \*PyType_GenericAlloc(PyTypeObject \*type, Py_ssize_t nitems)", "void f(int a,
double b = 5)", "const Data \*get() const", and "a \* f(a)" (the `cpp:expr` inline-concat
context) ALL render byte-correct with this one two-line diff.

FID-09 needs two small, genuinely separate edits (confirming CONTEXT.md's discretion note that
these mechanisms differ from `desc_sig_space`): (1) `depart_field_name`'s literal
`text(":")` becomes `text(": ")` (colon-space, D-01's "central edit"), and (2) `depart_field`
gains a four-line check that emits a standalone `text("  ")` statement (two spaces, matching
the EXACT pinned SC#3 string) between a field and its following sibling field. Both were
validated to reproduce `"Type: int (a number)  Default: 42"` **exactly**, via `pypdf` text
extraction, using the audit catalogue's own literal minimal-repro source.

**One pre-existing test WILL need updating as part of this phase, deliberately** (not a
regression to avoid, a locked byte-string that must change): `tests/test_
field_list_in_list_item_render_gate.py:165` currently asserts
`'strong(text("Author") + text(":"))' in typ_text` as a "must stay byte-unchanged" guarantee
for a top-level (non-confval) bibliographic field list. `depart_field_name` is a single global
choke point for EVERY `field_name` node in the codebase (docinfo fields, confval fields, and
any other field-list use) — the colon-space fix is unavoidably global, so this assertion must
become `text(": ")`. This is the ONLY test in the full suite (`grep 'text(":")'` across
`tests/*.py`) that references the old no-space colon form; every other test in the 483-test
"not slow" suite passed unmodified against the experimental patch.

**Primary recommendation:** Reduce `visit_desc_sig_space`/`depart_desc_sig_space` to `pass`/
`pass` (FID-07 + FID-08, one shared fix, zero new helper code); change `depart_field_name`'s
`text(":")` literal to `text(": ")` and add a four-line trailing-sibling check to `depart_field`
that emits `text("  ")` (FID-09, two small independent edits); update the one pre-existing
locked-string test; ship three new/extended GATE-01 fixtures with structural `.typ` asserts +
real-compile + pypdf-adjacency asserts per D-07.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Sphinx doctree → Typst source-text emission | Translator (`typsphinx/translator.py`, `visit_*`/`depart_*`) | — | This is a pure AST-to-text-generation pass; there is no browser/server/API/DB tier in this project — the whole "application" is a Sphinx builder extension. |
| Typst source → PDF compilation | `pdf.py` (`typst-py` wrapper) | — | Unmodified this phase; only consumes the corrected `.typ` output. |
| Regression proof (structural + visual fidelity) | Test suite (`tests/test_*_render_gate.py`) | pypdf (extracted-text verification) | GATE-01's standing bar: every node-handler change ships/extends a real-compile fixture; D-07 additionally requires pypdf adjacency assertion for Cluster B (horizontal spacing IS text-extractable, unlike Phase 19's vertical spacing). |

No browser/CDN/database tier exists in this project; the "Architectural Responsibility Map" is
degenerate by design (single-tier CLI/library extension) — recorded here for completeness per
the research contract, not because a misassignment risk exists.

## Standard Stack

No new dependencies of any kind. This phase is a pure edit to existing, already-imported code
in `typsphinx/translator.py`. Zero new runtime deps, no `@preview` version bump, the 3-way
version-sync surface (`writer.py`/`template_engine.py`/`templates/base.typ`) is untouched by
every one of the changes below (all fixes are inside `translator.py`'s existing `visit_*`/
`depart_*` methods; no new imports, no new template parameters).

**pypdf (test-only, D-07's gate requirement) is ALREADY a dev dependency** — verified:

```
$ grep -n "pypdf" pyproject.toml
46:    "pypdf>=6.14,<7",
```

Already used by 4 existing gate tests (`test_epigraph_render_gate.py`,
`test_substitution_definition_render_gate.py`, `test_wide_table_render_gate.py`,
`test_pdf_render_gate.py`) with the established `try: import pypdf; PYPDF_AVAILABLE = True;
except ImportError: PYPDF_AVAILABLE = False` graceful-skip pattern (mirrors the existing
`TYPST_AVAILABLE` pattern). No `pyproject.toml` edit needed for this phase.

**Version verification:** N/A — no package versions change this phase.

## Package Legitimacy Audit

**Not applicable.** This phase installs zero external packages (no new imports, no new
`pyproject.toml` entries, no `@preview` package version changes). Skipping the
Package-Legitimacy-Gate protocol per its own trigger condition ("whenever this phase installs
external packages" — it does not).

## Architecture Patterns

### System Architecture Diagram

```
Sphinx doctree (in-memory AST, built by docutils + Sphinx domain parsers)
        │
        │  TypstTranslator.dispatch_visit(node) / dispatch_departure(node)
        ▼
┌───────────────────────────────────────────────────────────────────────┐
│  visit_desc_signature → visit_strong                                  │
│    sets in_list_item=True for children (newline-statement join mode)  │
│    ┌─────────────────────────────────────────────────────────────┐   │
│    │ desc_annotation("class") → desc_sig_keyword("class")         │   │
│    │   → child Text("class")  → visit_Text: emits text("class")   │   │
│    │ desc_sig_space(" ")                                          │   │
│    │   → child Text(" ")      → visit_Text: emits text(" ")   ★FIX│   │
│    │ desc_addname/.../desc_name → Text("StandaloneHTMLBuilder")   │   │
│    │   → visit_Text: emits "\n" (list-item separator) + text(...) │   │
│    └─────────────────────────────────────────────────────────────┘   │
│  strong({ stmt1 \n stmt2 \n stmt3 \n ... })  ← Typst auto-joins       │
│  adjacent bare-expression statements in a { } content block with     │
│  ZERO added space — each statement's OWN text("…") payload is the    │
│  only source of visible characters. This is why the space needed a   │
│  real text(" ") VALUE, not source whitespace.                        │
└───────────────────────────────────────────────────────────────────────┘
        │
        │  same pattern inside desc_parameter (in_desc_parameter=True,
        │  "+" concat mode instead of "\n" statement mode) and inside
        │  desc_inline → paragraph (in_paragraph=True, also "\n"-joined
        │  bare statements inside par({ … }))
        ▼
  .typ source text  →  typst.compile()  →  PDF bytes  →  pypdf.extract_text()
                                                          (D-07 adjacency proof)
```

### Verified: the root cause and the fix (FID-07 + FID-08, ONE shared fix)

`typsphinx/translator.py:4812-4822` (current, buggy):

```python
def visit_desc_sig_space(self, node: addnodes.desc_sig_space) -> None:
    """Visit a desc_sig_space node (whitespace in signatures)."""
    # Output space directly, not as separate text() node
    self.body.append(" ")
    # Don't set list_item_needs_separator - space is connector
    raise nodes.SkipNode

def depart_desc_sig_space(self, node: addnodes.desc_sig_space) -> None:
    """Depart a desc_sig_space node."""
    # Handled in visit
    pass
```

**Verified fact (via `docutils.nodes.TextElement.__init__` inspection + a real Sphinx AST
dump):** `desc_sig_space` is a `desc_sig_element` (a `TextElement` subclass) constructed with
`text=' '` by default — it ALWAYS carries exactly one child `Text(" ")` node. `raise
nodes.SkipNode` in a `visit_*` method skips BOTH descending into children AND calls to the
matching `depart_*` — so that child `Text(" ")` is currently **never visited at all**. The bare
`self.body.append(" ")` instead writes a literal space character directly into the Typst
*source*, between two code-mode statements — syntactically harmless whitespace, but (per the
Phase 19-established invariant) it contributes ZERO rendered space, because it sits between two
independent bare-expression statements inside a `{ }` content block, which Typst auto-joins with
no implicit separator.

**Fix (validated with a real `typst.compile()` this session):**

```python
def visit_desc_sig_space(self, node: addnodes.desc_sig_space) -> None:
    """Visit a desc_sig_space node (whitespace in signatures)."""
    pass

def depart_desc_sig_space(self, node: addnodes.desc_sig_space) -> None:
    """Depart a desc_sig_space node."""
    pass
```

This is IDENTICAL in shape to the four sibling handlers immediately around it in the file
(`visit_desc_sig_keyword`/`depart_desc_sig_keyword`, `visit_desc_sig_name`/
`depart_desc_sig_name`, `visit_desc_sig_punctuation`/`depart_desc_sig_punctuation`,
`visit_desc_sig_operator`/`depart_desc_sig_operator` — all four are already bare `pass`/`pass`,
letting their own child `Text(...)` node stream through the normal, already fully
concat-context-aware `visit_Text` dispatch). No new helper function, no new state, no new
concat-context plumbing is needed — `visit_Text` (translator.py ~946) ALREADY branches
correctly on every context this node can appear in:

- Inside `desc_signature`'s `strong({…})` join block (`in_list_item=True` via `visit_strong`):
  emits a leading `"\n"` (if a prior sibling set `list_item_needs_separator`), then
  `text(" ")`, then sets `list_item_needs_separator = True` for the next sibling.
- Inside `desc_parameter` (`in_desc_parameter=True`, one of `_CONCAT_CONTEXTS`, checked FIRST
  before `in_list_item` even though both are simultaneously true — verified via
  `_inline_concat_context()`'s ordered tuple scan): emits `" + "` before `text(" ")` instead of
  `"\n"`.
- Inside `desc_inline` (transparent pass-through, per DESC-04) when the surrounding context is a
  `paragraph` (`in_paragraph=True`): `_add_paragraph_separator()` emits the same `"\n"`-then-join
  pattern, which — because `text(" ")` is now a real content VALUE, not source whitespace —
  correctly contributes a rendered space in the auto-joined paragraph content.

**Real-compile verification performed this session** (temporary experimental patch, applied via
`Edit`, tested via `sys.executable -m sphinx -b typstpdf`, verified via `pypdf.PdfReader(...)
.extract_text()`, then reverted via `git checkout` — `git status` confirmed clean before and
after):

```
$ python3 -m sphinx -b typstpdf src _build   # build succeeded, real typst.compile()

$ python3 -c "import pypdf; ...extract_text()..."
PyObject *PyType_GenericAlloc(PyTypeObject *type, Py_ssize_t nitems)
void f(int a, double b = 5)
const Data *get() const
template<typename T>
class Wrapper
class sphinx.builders.html.StandaloneHTMLBuilder
Expression: a * f(a).
```

Every one of these EXACTLY matches the `-b text`/`-b html` authority form cited in the audit
catalogue (rows 2 and 3): "class sphinx.builders…", "Py_ssize_t nitems", "a \* f(a)".

### Verified: FID-08 completeness (D-03's "all inter-token forms")

CONTEXT.md's open research question #2 asked whether `desc_sig_operator`/`desc_sig_punctuation`
need independent spacing logic. **Answer: no — confirmed by dumping a real Sphinx C/C++-domain
AST** (built directly via `sphinx.application.Sphinx` against a small real project, NOT
training-data guesswork) for every audited form:

| Audited form (CONTEXT.md) | Real AST structure observed | Space-node-backed? |
|---|---|---|
| `PyObject *PyType_GenericAlloc(...)` (leading pointer) | `desc_sig_name("PyObject")` → `desc_sig_space` → `desc_sig_punctuation("*")` → `desc_name` | Yes — space is BEFORE `*` only; `*` hugs the following name with no space node between them (matches expected "PyObject \*Name", not "PyObject\* Name") |
| `PyTypeObject *type` (parameter, same pattern) | identical shape, inside `desc_parameter` | Yes |
| `Py_ssize_t nitems` (type↔identifier) | `desc_sig_name` → `desc_sig_space` → `desc_sig_name` | Yes |
| keyword prefix (`void f(...)`, `class X`) | `desc_sig_keyword_type`/`desc_sig_keyword` → `desc_sig_space` → `desc_name` | Yes |
| operator spacing (`double b = 5`, default value) | `desc_sig_name` → `desc_sig_space` → `desc_sig_punctuation("=")` → `desc_sig_space` → `desc_sig_literal_number("5")` | Yes — `=` gets a space on BOTH sides, both are `desc_sig_space` |
| `a * f(a)` (cpp:expr operator) | `desc_sig_name("a")` → `desc_sig_space` → `desc_sig_operator("*")` → `desc_sig_space` → `reference→desc_sig_name("f")` | Yes — confirmed inside `desc_inline` (paragraph context), not `desc_signature` |
| `const Data *get() const` (leading + trailing qualifier) | `desc_sig_keyword("const")` → `desc_sig_space` → `desc_sig_name("Data")` → `desc_sig_space` → `desc_sig_punctuation("*")` → `desc_name` → `desc_parameterlist` → `desc_sig_space` → `desc_sig_keyword("const")` | Yes — including the AFTER-parameterlist trailing qualifier |
| `template<typename T> class Wrapper` (multi-line, `<`/`>` punctuation) | Line 1: `desc_sig_keyword("template")` → `desc_sig_punctuation("<")` (NO space) → `desc_sig_keyword("typename")` → `desc_sig_space` → `desc_name("T")` → `desc_sig_punctuation(">")` (NO space). Line 2 (separate `desc_signature_line`): `desc_sig_keyword("class")` → `desc_sig_space` → `desc_name("Wrapper")` | Yes for every space that SHOULD exist; correctly NO `desc_sig_space` node where NO space should render (`template<`, `T>`) |

**Conclusion: every audited spacing form is `desc_sig_space`-backed. `desc_sig_operator` and
`desc_sig_punctuation` never carry inherent spacing of their own** — punctuation/operator glyphs
are always emitted bare, immediately adjacent to whatever comes next, and a `desc_sig_space`
SIBLING node is inserted by Sphinx's own signature parser wherever (and only wherever) a real
space belongs. This means the single `visit_desc_sig_space` fix above satisfies D-03's "all"
requirement with **zero additional code** at the operator/punctuation handlers — they correctly
stay `pass`/`pass` exactly as they are today.

### Verified: FID-09 (two small, genuinely separate edits)

**Edit 1 — colon-space (D-01's "central edit"):**

`typsphinx/translator.py:4691-4694` (current):
```python
def depart_field_name(self, node: nodes.field_name) -> None:
    """Depart a field_name node."""
    # Close strong() and add colon
    self.body.append(' + text(":"))\n')
```

Fix: change the literal string to `' + text(": "))\n'` (space inside the colon's `text()`
content, not around it). This produces `strong(text("Type") + text(": "))` — a single
`+`-joined content EXPRESSION (not a content BLOCK — `field_name` uses `strong(...)`, not
`strong({...})`), so the space is a real content value from the start; no concat-context
awareness is needed here at all (unlike `desc_sig_space`, `field_name` only ever has this one
call site).

**Edit 2 — inter-field boundary double-space (D-01's "(b)"):**

`typsphinx/translator.py:4671-4673` (current):
```python
def depart_field(self, node: nodes.field) -> None:
    """Depart a field node."""
    pass
```

Fix (mirrors the existing `node.next_node(descend=False, siblings=True)` idiom already used at
`depart_desc_parameter`, translator.py:4610, for comma-separation):

```python
def depart_field(self, node: nodes.field) -> None:
    """Depart a field node."""
    if node.next_node(descend=False, siblings=True):
        self.add_text('\ntext("  ")\n')
```

**Both leading AND trailing `\n` are required** — this was caught by the real-compile
verification this session: a version with only a leading `\n` produced
`text("  ")strong(text("Default")...` on one physical source line (two adjacent statements with
no separator between them), which is a real Typst parse error: `expected semicolon or line
break`. The corrected two-`\n` form compiles and renders correctly.

**Why TWO spaces, not one:** ROADMAP SC#3 pins the literal string `"Type: int (a number)  Default:
42"` — a deliberate double space between fields (not derived from the `-b text` authority, which
renders this construct as a vertically-stacked definition list, not inline at all; D-02 already
locked the inline-with-double-space form as this phase's own acceptance bar, distinct from what
HTML/text literally render). `text("  ")` (two space characters inside one `text()` call) is the
correct emission — verified via pypdf extraction to match SC#3's pinned string byte-for-byte.

**Real-compile verification (using the audit catalogue's own literal minimal-repro source,
UNMODIFIED)**, `.. confval:: the_answer` immediately followed (no blank line) by `:type:`/
`:default:` fields:

```
$ python3 -m sphinx -b typstpdf src _build
build succeeded.
$ pypdf extract_text() on the resulting page:
the_answer Type: int (a number)  Default: 42
```

This is an EXACT byte match to ROADMAP SC#3's pinned string.

### Critical nuance discovered: which confval source form is real (matters for fixture design)

RST allows TWO syntactically valid forms for a `confval`'s `:type:`/`:default:` fields:

1. **No blank line** between the directive and the fields (docutils "directive option list"
   grammar) — `.. confval:: name`⏎`   :type: ...`. This is the audit catalogue's OWN literal
   repro AND is the form used by **100% of the real corpus**: `grep`-driven analysis of the
   cached Sphinx v9.1.0 corpus (`~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc/usage/
   configuration.rst`, the exact file audited at pp.313-374 for this finding) found **0 of 219**
   confvals use a blank line before their fields — **all 219** use this no-blank-line form. In
   this form, docutils collapses the field body's children to bare inline nodes DIRECTLY under
   `field_body` (no wrapping `paragraph`), which is exactly what the PRE-EXISTING `all_inline`
   fast path in `visit_field_body` (translator.py:4723-4728, from Phase 15's bug #8 fix)
   already detects and handles with its `+`-concat machinery.
2. **A blank line** between the directive and the fields (generic RST field-list-in-content
   grammar). In this form docutils WRAPS each field body's inline content in a real `paragraph`
   node, which the current `all_inline` check (checking `field_body`'s DIRECT children) does
   NOT detect — it falls through to the block `par({...})` path, and a real `typst.compile()`
   test this session showed `par(...)` renders as its own vertical paragraph (a real line
   break, verified via pypdf: "Type: " / "int (a number)" / "  Default: " / "42" each landed on
   separate visual lines, NOT the flowing single-line SC#3 target), even with Edits 1+2 applied.

**Since the no-blank-line form is (a) the audit's own literal repro and (b) empirically 100% of
the real corpus, Edits 1+2 above are SUFFICIENT to close FID-09 as observed in the actual
Sphinx v9.1.0 `doc/` tree** — no further change to `visit_field_body`/`visit_paragraph` is
required for GATE-01 compliance. An optional hardening (unwrap a lone all-inline
`paragraph`-wrapped `field_body` child, flattening it the same way `in_list_item` already
suppresses `par()` wrapping) was prototyped and DOES work — validated via a real compile
producing the identical exact SC#3 string for the blank-line variant too — but is **not required
by the corpus** and is offered only as optional discretionary robustness (see "Open Questions").

### Recommended Project Structure

No new files/directories for source code — all edits land in the existing
`typsphinx/translator.py`. New test fixtures follow the established convention:

```
tests/
├── test_desc_sig_space_render_gate.py         # NEW — FID-07 + FID-08 (shared fix, shared fixture project OK)
├── test_confval_field_spacing_render_gate.py  # NEW — FID-09 (or extend existing test_confval_field_body_render_gate.py)
├── test_field_list_in_list_item_render_gate.py # EDIT existing line 165 (see Pitfall 2)
└── fixtures/
    ├── desc_sig_space_render_gate/
    │   ├── conf.py
    │   └── index.rst      # py:class + c:function + cpp:function + cpp:expr repros
    └── confval_field_spacing_render_gate/
        ├── conf.py
        └── index.rst      # the audit's literal `the_answer` :type:/:default: repro
```

### Anti-Patterns to Avoid

- **Writing a new "emit a real space" helper function.** Unlike Phase 19's `_emit_forced_break`
  (genuinely needed because `parbreak()`/`linebreak()` are new tokens with no existing emission
  path), FID-07/FID-08's fix requires **deleting** code, not adding a helper. The existing
  `visit_Text` dispatch already does everything correctly once it is allowed to run.
- **Adding concat-context checks inside `visit_desc_sig_space` itself.** This would duplicate
  logic that `visit_Text` already owns as the single source of truth (per the file's own
  comments: "Shared with visit_Text via the concat helpers (single source of truth)").
- **Using `sym.space` or `~` (Typst's non-breaking space marker) instead of `text(" ")`.** D-05
  explicitly requires BREAKABLE spaces; `~` is Typst's non-breaking space and was explicitly
  rejected by D-06. Plain `text(" ")` content is breakable by default.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Concat-vs-list-item-vs-paragraph-aware space emission | A dedicated space-emission helper with its own context branching | The EXISTING `visit_Text` dispatch (just stop intercepting its input with `SkipNode`) | `visit_Text` is already the single source of truth for this exact branching (`_emit_inline_concat_separator`/`_mark_inline_concat_content`, `_add_paragraph_separator`, `list_item_needs_separator`) — duplicating it in `visit_desc_sig_space` would be a second, divergence-prone implementation of the same logic. |
| Field-boundary / comma-style trailing-sibling detection | A custom "is there a next field" walk | `node.next_node(descend=False, siblings=True)` | Already the established idiom at `depart_desc_parameter` (translator.py:4610) for the exact same "am I the last sibling" question. |

**Key insight:** every piece of "space in code mode" logic this codebase needs already exists
in `visit_Text` and its concat-context helpers. Cluster B's entire fix surface is: (1) stop
short-circuiting that dispatch for `desc_sig_space`, and (2) two tiny literal-string/boundary
edits for `field_name`/`field` that don't touch the concat machinery at all because they only
ever fire in one context each.

## Common Pitfalls

### Pitfall 1: `raise nodes.SkipNode` silently discards a node's only useful content
**What goes wrong:** `visit_desc_sig_space`'s `raise nodes.SkipNode` after a hand-written
`self.body.append(" ")` looks like a reasonable "shortcut" — the node's text IS just a space, so
why not write it directly? — but it bypasses `visit_Text`'s escaping, separator, and
concat-context logic, and (critically) writes SOURCE whitespace instead of a content VALUE.
**Why it happens:** the distinction between "a literal space character in the `.typ` file" and
"a `text(" ")` Typst expression that evaluates to a space glyph" is invisible unless you actually
inspect the generated `.typ` and reason about Typst's code-mode auto-join semantics (proven in
Phase 19 for `\n`, now proven again here for a bare space character).
**How to avoid:** for `desc_sig_element` subclasses that only exist to carry a fixed piece of
text, prefer letting the existing `Text` child stream through the normal Text dispatch (the
pattern EVERY sibling `desc_sig_*` handler already uses) over hand-writing `self.body.append(...)`.
**Warning signs:** a `visit_*` method that both writes raw text directly to `self.body` AND
raises `SkipNode` is worth auditing for this exact class of bug — anywhere a real content VALUE
was needed but only source-text whitespace was emitted.

### Pitfall 2: The colon-space fix is unavoidably global — one existing test WILL need a deliberate update
**What goes wrong:** `depart_field_name` is the single choke point for EVERY `field_name` node
in the codebase — confval `:type:`/`:default:` fields, generic top-level bibliographic field
lists (`:Author: ...`), and any future field-list use. Changing its literal string changes ALL
of them. `tests/test_field_list_in_list_item_render_gate.py:165` currently locks the OLD
no-space form as "must stay byte-unchanged" for a top-level (non-confval) field list —
`assert 'strong(text("Author") + text(":"))' in typ_text`.
**Why it happens:** that test predates this phase (Phase 15, GATE-02 — a different, unrelated
fatal-compile-error fix) and encoded the THEN-correct (buggy) behavior as its regression
baseline.
**How to avoid:** this is not a regression to work around — it is a **required, deliberate
update**. Change line 165's assertion to `'strong(text("Author") + text(": "))'`. Confirmed via
`grep -n 'text(":")' tests/*.py` that this is the ONLY assertion in the entire test suite
referencing the old no-space colon form (verified against the full 483-test "not slow" suite
run with the experimental patch applied — every other test passed unmodified).
**Warning signs:** any OTHER hard-coded `text(":")` (without trailing space) assertion anywhere
in the test suite would similarly need updating — the grep above is the exhaustive check to
re-run after implementing.

### Pitfall 3: A `field_body` wrapped in a real `paragraph` node renders as a vertical block, not flowing inline text
**What goes wrong:** if a confval's `:type:`/`:default:` field is written with a blank line
before it (valid RST, just not the form used anywhere in the real corpus or the audit's own
repro), docutils wraps the field body's content in a genuine `paragraph` node. `visit_paragraph`
(unmodified by this phase's edits) emits a real `par({...})` call, and Typst renders `par()`
values as their own vertical paragraph block even when embedded among otherwise-flowing
`strong()`/`text()` statements — verified via a real compile this session (the field value
landed on its own PDF text-extraction line, separate from the "Type:"/"Default:" labels).
**Why it happens:** the existing `all_inline` fast path in `visit_field_body` only inspects
`field_body`'s DIRECT children — it doesn't know to unwrap a single lone `paragraph` wrapper.
**How to avoid:** NOT required for GATE-01 (0/219 real corpus confvals hit this path — see
"Critical nuance discovered" above) — flag as an Open Question for the planner to explicitly
accept/decline as optional hardening, rather than silently under- or over-scoping the fix.
**Warning signs:** if a future corpus or hand-written test fixture uses the blank-line
`confval` form and its rendered output falls back to vertical stacking instead of the pinned
inline string, this is the mechanism — not a regression in Edits 1/2.

### Pitfall 4: Missing a trailing newline after an inserted bare statement causes a real Typst parse error
**What goes wrong:** inserting `text("  ")` as its own statement between two other statements
needs a newline (or semicolon) on BOTH sides — a leading-only newline produces
`text("  ")strong(...)` on one physical line, which Typst rejects with `expected semicolon or
line break` (the EXACT class of fatal GATE-01's fixtures already guard against for other sites,
per e.g. `test_desc_signature_concat_render_gate.py`'s own historical fatal).
**Why it happens:** easy to reason about "insert a value between these two things" without
tracing the exact adjacent-character boundary in the generated source.
**How to avoid:** ALWAYS real-compile a fixture after adding a new bare code-mode statement
(never trust "the .typ looks plausible" — `sys.executable -m sphinx -b typstpdf`, never
`-b typst` alone, since only the PDF-compile path actually invokes `typst.compile()`).
**Warning signs:** `TypstError: expected semicolon or line break` with two function calls glued
together on one line in the traceback.

## Code Examples

Verified patterns from this session's real-compile testing (not third-party docs — this is a
single-repo, in-house translator, so "official docs" for these idioms IS this codebase's own
established patterns, cross-checked against a real `typst.compile()`):

### FID-07/FID-08: the complete diff
```python
# typsphinx/translator.py — replace both methods with pass/pass,
# matching the four desc_sig_* siblings immediately around them.
def visit_desc_sig_space(self, node: addnodes.desc_sig_space) -> None:
    """Visit a desc_sig_space node (whitespace in signatures)."""
    pass

def depart_desc_sig_space(self, node: addnodes.desc_sig_space) -> None:
    """Depart a desc_sig_space node."""
    pass
```

### FID-09: colon-space
```python
def depart_field_name(self, node: nodes.field_name) -> None:
    """Depart a field_name node."""
    # Close strong() and add colon-space (FID-09)
    self.body.append(' + text(": "))\n')
```

### FID-09: inter-field boundary
```python
def depart_field(self, node: nodes.field) -> None:
    """Depart a field node.

    Emit a real two-space content statement between sibling fields (FID-09) --
    matches the ROADMAP SC#3 pinned inline target
    "Type: int (a number)  Default: 42". A bare cosmetic "\\n" between
    statements is insignificant in Typst code mode (Phase 19's proven
    invariant), so a real text("  ") VALUE is required. Both a leading AND
    trailing "\\n" are required so this statement never juxtaposes with its
    neighbors on one physical source line.
    """
    if node.next_node(descend=False, siblings=True):
        self.add_text('\ntext("  ")\n')
```

### GATE-01 fixture assertion patterns (structural `.typ` + pypdf, verified this session)
```python
# .typ structural asserts -- exact substrings observed in this session's
# real compile output, safe to assert verbatim:
assert 'text("class")\ntext(" ")\ntext("sphinx' in typ_text          # FID-07
assert 'text("PyObject")\ntext(" ")\ntext("*")\ntext("PyType_GenericAlloc")' in typ_text  # FID-08
assert 'text("PyTypeObject") + text(" ") + text("*") + text("type")' in typ_text          # FID-08 (desc_parameter concat form)
assert 'strong(text("Type") + text(": "))' in typ_text               # FID-09 colon-space
assert 'text("  ")\nstrong(text("Default")' in typ_text              # FID-09 field boundary

# pypdf extracted-text adjacency asserts (D-07 REQUIRED):
text = pypdf.PdfReader(pdf_path).pages[-1].extract_text()
assert "class sphinx" in text and "classsphinx" not in text          # FID-07
assert "Py_ssize_t nitems" in text and "Py_ssize_tnitems" not in text  # FID-08
assert "a * f(a)" in text                                            # FID-08 (cpp:expr)
assert "Type: int (a number)  Default: 42" in text                   # FID-09 (exact SC#3 string)
```

### Existing test that MUST be updated (Pitfall 2)
```python
# tests/test_field_list_in_list_item_render_gate.py:165 -- BEFORE (delete):
assert 'strong(text("Author") + text(":"))' in typ_text, (...)
# AFTER (required by this phase's colon-space fix):
assert 'strong(text("Author") + text(": "))' in typ_text, (...)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `visit_desc_sig_space` writes raw source whitespace + `SkipNode` | `pass`/`pass`, letting `visit_Text` handle the child `Text(" ")` normally | This phase | FID-07 + FID-08 fixed with zero new code, matching the already-established sibling-handler pattern |
| `depart_field_name` emits `text(":")` (no space) | `text(": ")` | This phase | FID-09(a); also changes ALL field-name rendering codebase-wide (docinfo included) |
| `depart_field` is a no-op | Emits `text("  ")` between sibling fields | This phase | FID-09(b) |

**No deprecated/outdated APIs involved** — this is an internal-code fix, not an
external-ecosystem version bump.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `exception ` (the sibling keyword to `class ` in `desc_annotation`) uses the IDENTICAL `desc_sig_keyword`+`desc_sig_space` node structure as `class ` (not independently re-verified with a live `py:exception` AST dump this session, only inferred by domain-source symmetry with the verified `py:class` case) | FID-07 "Verified: the root cause and the fix" | Very low — `py:exception` and `py:class` share the same Sphinx `PyObject`-family signature-parsing code path; if this assumption were wrong the fix would still be the identical single `desc_sig_space` change, just needing an extra fixture case to prove it, not a different code change. |

**All other claims in this research were empirically verified this session** via a real,
temporary experimental patch + `sys.executable -m sphinx -b typstpdf` + `typst.compile()` +
`pypdf.extract_text()`, then reverted (`git checkout -- typsphinx/translator.py`, confirmed
clean via `git status`). This includes the FID-08 completeness claim (verified via a real
Sphinx AST dump, not training-data inference) and the FID-09 exact-pinned-string claim (verified
byte-for-byte against ROADMAP SC#3's own quoted string).

## Open Questions

1. **Should the optional `field_body` paragraph-flatten hardening (Pitfall 3) be included this
   phase?**
   - What we know: 0/219 real-corpus confvals need it; the audit's own literal repro doesn't
     need it; GATE-01 does not require it. A working prototype (unwrap a lone all-inline
     `paragraph` child of `field_body`, suppress its `par()` wrap the same way `in_list_item`
     already does) was validated via a real compile to also produce the exact pinned string.
   - What's unclear: whether any OTHER real-world Sphinx project (beyond this milestone's
     `doc/` corpus target) commonly uses the blank-line confval-field form, which would make
     this a genuine future fidelity gap rather than a hypothetical one.
   - Recommendation: SKIP for this phase (keep the diff minimal, matching D-07's requirement
     that a fixture "would FAIL against the pre-fix translator" — the corpus doesn't exercise
     this path, so it can't be the basis of a corpus-based regression proof). Record as a
     Backlog candidate if a future audit surfaces the blank-line form as a real occurrence.

## Environment Availability

Skipped — this phase has no external tool/service dependencies beyond what's already
established project-wide (Sphinx, typst-py, pypdf — all already verified present and pinned;
see "Standard Stack" above).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (existing, configured in `pyproject.toml`) |
| Config file | `pyproject.toml` (existing `[tool.pytest.ini_options]`) |
| Quick run command | `pytest tests/ -m "not slow" -q` (verified this session: 483 passed, 23 deselected, 23s) |
| Full suite command | `pytest tests/` (includes `-m slow` corpus gate; verified this session: full-corpus compile-fatal-free gate passes with all three fixes applied, 13s) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FID-07 | `class `/`exception ` prefix keeps trailing space, real-compile + pypdf-adjacency proof | render-gate (structural + real-compile + pypdf) | `pytest tests/test_desc_sig_space_render_gate.py -x` | ❌ Wave 0 (new file) |
| FID-08 | ALL audited C/C++ inter-token forms preserve spacing, real-compile + pypdf-adjacency proof | render-gate (structural + real-compile + pypdf) | `pytest tests/test_desc_sig_space_render_gate.py -x` (same fixture project as FID-07, per discretion allowance) | ❌ Wave 0 (new file, or add cases to the FID-07 file) |
| FID-09 | Colon-space + inter-field double-space, exact SC#3 string match via pypdf | render-gate (structural + real-compile + pypdf) | `pytest tests/test_confval_field_spacing_render_gate.py -x` (or extend `test_confval_field_body_render_gate.py`) | ❌ Wave 0 (new file or extension) |
| GATE-01 (standing) | No regression across the two updated tests + the full real-corpus compile-fatal-free gate | regression / integration | `pytest tests/ -m "not slow" -q` then `pytest tests/test_corpus_gate.py -m slow -q` | ✅ existing |

### Sampling Rate
- **Per task commit:** `pytest tests/test_<new fixture>.py -x` + `pytest tests/test_field_list_in_list_item_render_gate.py -x` (the one deliberately-changed existing test)
- **Per wave merge:** `pytest tests/ -m "not slow" -q` (full fast suite; verified 23s runtime this session)
- **Phase gate:** `pytest tests/test_corpus_gate.py -m slow -q` (real 684-page corpus compile-fatal-free; verified 13s runtime, passes with all three fixes applied — confirmed this session)

### Wave 0 Gaps
- [ ] `tests/test_desc_sig_space_render_gate.py` — new fixture covering FID-07 (`class `/`exception ` prefix) + FID-08 (C/C++ signature + `cpp:expr` inline forms); reuse the audit catalogue's own minimal-repro sources verbatim where possible for direct traceability.
- [ ] `tests/fixtures/desc_sig_space_render_gate/{conf.py,index.rst}` — the fixture project itself.
- [ ] `tests/test_confval_field_spacing_render_gate.py` — new fixture covering FID-09, using the audit's literal `.. confval:: the_answer` no-blank-line repro (this exact source was verified this session to produce the exact pinned SC#3 string).
- [ ] `tests/fixtures/confval_field_spacing_render_gate/{conf.py,index.rst}` — the fixture project itself.
- [ ] `tests/test_field_list_in_list_item_render_gate.py:165` — REQUIRED edit (not a gap in coverage, a required update to a locked assertion — see Pitfall 2).

Framework install: none — pytest, typst-py, and pypdf are all already installed dev
dependencies; no `uv sync` changes needed.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | This is a build-time doctree-to-text translator with no runtime auth surface. |
| V3 Session Management | No | N/A — no sessions. |
| V4 Access Control | No | N/A — no access-controlled resources. |
| V5 Input Validation | No new surface | ALL text this phase's edits emit is either (a) a fixed constant literal (`" "`, `": "`, `"  "` — never derived from `node.astext()`, so no escaping is needed) or (b) content ALREADY routed through the existing `escape_typst_string()` helper via the unmodified `visit_Text` dispatch. No new user-controlled-content-to-Typst-source path is introduced. |
| V6 Cryptography | No | N/A — no cryptographic operations. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Typst source-injection via unescaped doctree text (e.g. a docstring containing `")` sequences that could break out of a `text("...")` string literal) | Tampering | Already fully mitigated project-wide by `escape_typst_string()` (translator.py:24, tested by `tests/test_typst_string_escape_gate.py`) — pre-existing, unmodified by this phase. This phase's own new literals (`": "`, `"  "`) are fixed Python string constants, not doctree-derived, so they carry no injection risk by construction. |

## Sources

### Primary (HIGH confidence — verified this session via direct tool execution)
- `typsphinx/translator.py` (this repo) — direct read of `visit_desc_sig_space`,
  `depart_desc_sig_space`, `visit_field_name`, `depart_field_name`, `visit_field`,
  `depart_field`, `visit_field_body`, `depart_field_body`, `visit_Text`,
  `_emit_inline_concat_separator`, `_mark_inline_concat_content`, `_enter_inline_concat_element`,
  `_exit_inline_concat_element`, `_inline_concat_context`, `visit_strong`, `depart_strong`,
  `visit_paragraph`, `depart_paragraph`, `_add_paragraph_separator`, `_emit_forced_break`,
  `visit_desc_signature`, `visit_desc_inline`, `visit_document` (the `#{`/`}` code-block wrap).
- `sphinx.addnodes.desc_sig_space` (installed sphinx 9.1.0 package source) — confirmed
  `TextElement` subclass with `text=' '` default, via `inspect.getsource()`.
- A real Sphinx AST dump (`sphinx.application.Sphinx('src','src','_build','_build/.doctrees',
  'pseudoxml')`) against a synthetic project exercising every audited C/C++ inter-token form —
  this session, this environment.
- A real `typst.compile()` round-trip (via `sys.executable -m sphinx -b typstpdf`) of a
  temporary experimental patch to `typsphinx/translator.py`, applied and reverted this session
  (`git checkout -- typsphinx/translator.py`, `git status` confirmed clean before/after).
- `pypdf.PdfReader(...).extract_text()` on the resulting real PDF — this session, confirming
  exact byte matches to the audit catalogue's cited target strings and ROADMAP SC#3's pinned
  string.
- The cached real Sphinx v9.1.0 corpus (`~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc/`) —
  `usage/configuration.rst` grepped/parsed for the 219-confval blank-line-vs-no-blank-line
  statistic.
- `pytest tests/ -m "not slow" -q` (483 passed) and `pytest tests/test_corpus_gate.py -m slow -q`
  (full real-corpus compile-fatal-free gate, 1 passed) — both run against the experimental patch
  this session, both confirming no unexpected regressions beyond the one deliberately-changed
  assertion.
- `.planning/milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md` (Issue
  Table rows 2, 3, 5) — source of record for every FID target string cited above.
- `tests/test_desc_signature_concat_render_gate.py`, `tests/test_wide_table_render_gate.py`,
  `tests/test_field_list_in_list_item_render_gate.py`, `tests/test_confval_field_body_render_gate.py`
  — GATE-01 fixture-shape precedents (structural assert + real compile + pypdf pattern).
- `pyproject.toml` — confirmed `pypdf>=6.14,<7` already present as a dev dependency (line 46).

### Secondary (MEDIUM confidence)
- None — every claim in this research was independently verified this session; no claim rests
  solely on an unverified web/training-data source.

### Tertiary (LOW confidence)
- A1 in the Assumptions Log (the `exception ` keyword's node structure, inferred by symmetry
  with the verified `class ` case, not independently AST-dumped this session).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new dependencies; pypdf presence directly confirmed in `pyproject.toml`.
- Architecture: HIGH — root cause and fix independently reproduced via a real, reverted experimental patch + real `typst.compile()` + real `pypdf` extraction, for all three findings.
- Pitfalls: HIGH — all four pitfalls were directly encountered and resolved during this session's verification work (not hypothetical); Pitfall 2's exact test/line was identified via a real full-suite run.

**Research date:** 2026-07-20
**Valid until:** No expiry driver — this is in-repo code, not an external API; stays valid until `translator.py`'s `desc_sig_*`/`field_*` handlers are next touched by an unrelated phase.
