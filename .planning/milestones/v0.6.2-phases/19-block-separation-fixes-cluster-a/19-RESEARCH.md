# Phase 19: Block Separation Fixes (Cluster A) - Research

**Researched:** 2026-07-20
**Domain:** Typst code-mode block/paragraph layout — `typsphinx/translator.py` `visit_*`/`depart_*` separator emission
**Confidence:** HIGH — every recommendation below is grounded in a real `typst.compile()` (via `typst-py` 0.15.0, the project's pinned compiler) against a minimal reproduction of the exact corpus text, cross-checked against the full cached Sphinx `doc/` corpus (`~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0`, tag `v9.1.0`) translated with the CURRENT (pre-fix) translator.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01 (fidelity target level):** Match the `-b html` authority **per-construct** — do NOT apply a
  single uniform break everywhere. The break *kind* follows what HTML renders for that construct:
  paragraphs-in-list-items (F1) → paragraph break (`parbreak()`, vertical space); sibling
  `desc_signature`s (F7) → line break (`linebreak()`, stacked lines); rubric/option heading (F13)
  → heading on its own line, then the option separately; definition `term` (F14) → term on its own
  line, definition indented below; back-to-back body-less confvals (F15) → block separation between
  entries.
- **D-02:** Rejected the "minimum anti-collision" (one uniform light break / single space) approach.
- **D-03 (separator-fix structure):** Build **one small shared helper** reused at all five sites,
  parameterized by break kind. The helper respects and drives the existing
  `list_item_needs_separator` machinery. Each of the five call sites chooses its own break kind
  (per D-01).
- **D-04:** Rejected fully-independent 5-point fixes (zero sharing) AND a single monolithic
  primitive that emits an identical break everywhere.
- **D-05 (verification strategy, GATE-01):** Non-fatal visual fixes — a bare `%PDF`-magic /
  compile-success assert proves nothing. Each fixture MUST **structurally assert the generated
  `.typ`** contains the expected separator token (`parbreak()` / `linebreak()`) at the correct
  site, AND run a real `typst.compile()` producing a valid `%PDF`.
- **D-06:** Rejected rasterize-and-check-glyph-position; did NOT adopt pypdf text-extraction as a
  requirement. A planner MAY optionally add a pypdf extracted-text adjacency check (e.g. absence
  of "role.For") for the observable cases (F1/F13/F15) as a *strengthening*, but it is not
  required.

### Claude's Discretion

- **Fixture granularity/placement:** Recommended default is **one render-gate fixture per
  finding**, extending existing modules where a direct analog already exists
  (`tests/test_desc_signature_concat_render_gate.py` for F7,
  `tests/test_deflist_term_concat_render_gate.py` for F14) and adding new modules for F1/F13/F15.
  A planner may consolidate if a shared fixture project cleanly exercises multiple findings,
  provided each finding retains an assertion that would fail against the pre-fix translator.
- **Exact break-token choice per site** — `parbreak()` vs `linebreak()` vs a `par()`-wrap is fixed
  in intent by D-01 (kind per construct) but the precise Typst emission (and any interaction with
  the `{ }` list-item content block) was left for research/planning to settle against real
  compiles. **This research settles it — see "Architecture Patterns" below.**

### Deferred Ideas (OUT OF SCOPE)

- pypdf extracted-text adjacency assertions as an *optional* strengthening (F1/F13/F15) — not
  required this phase.
- Rasterized glyph-position verification — rejected for this milestone.
- Cluster B token-spacing (FID-07..FID-09) → Phase 20; Clusters C/D/E/F (FID-10..FID-14) →
  Phase 21; Issue #117 PDF naming (PDF-01) → Phase 22.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FID-02 (F1) | Consecutive `paragraph`s inside a `list_item` render with visible separation instead of concatenating ("role.For example" → "role. For example"). Corpus-wide. | Root cause + fix + real-compile-verified `parbreak()` mechanism documented under Architecture Patterns → Site 1. Reproduced against the CURRENT translator's real corpus output (`usage/referencing.typ`) and against the exact "First dot.Second word." pattern. |
| FID-03 (F7) | Multiple sibling `desc_signature`s render on separate lines instead of one line. | Root cause + fix + real-compile-verified `linebreak()` mechanism under Site 2. Reproduced against `usage/domains/python.typ`'s `compile()` overloads. |
| FID-04 (F13) | A `rubric` option-group heading (and directive-option "Options" heading) renders separated from the first following `option`/`:field:`. | Root cause + fix under Site 3. Reproduced against `man/sphinx-quickstart.typ` ("Structure Options"/"--sep") and `usage/restructuredtext/directives.typ` ("Options"/":class:"). |
| FID-05 (F14) | A `definition_list` `term` renders separated from its `definition` when nested in a `list_item` or the definition opens with a nested list. | Root cause (shares F1's early-return mechanism) + a DIFFERENT, non-list-item-machinery fix documented under Site 4. Reproduced against `usage/configuration.typ`'s `texinfo_elements` (case a) and `mecab` (case b) confvals. |
| FID-06 (F15) | Back-to-back body-less `confval` `desc` nodes render as distinct, separated entries. | Root cause + fix under Site 5. Reproduced against `usage/extensions/coverage.typ`'s four back-to-back confvals. Also proved harmless/idempotent on the body-present case (no regression). |

</phase_requirements>

## Summary

All five findings share ONE proven root cause (already documented in the repo at
`visit_desc_signature_line`, translator.py ~4392-4410): in Typst's unified code mode (the whole
document body is one `#{ ... }` block, opened in `visit_document` ~381 and closed in
`depart_document` ~393), a **bare source `\n`/`\n\n` between two top-level code-mode statements is
COSMETIC ONLY** — it satisfies Typst's parser (two statements need *some* separator to avoid
"expected semicolon or line break") but produces **zero visual break**. Content that isn't
already wrapped in a Typst block-level call (`par()`, `list()`, `raw()`, `table()`, `terms()`)
just concatenates onto one flowing line, because `strong()`/`text()`/`raw()` (inline, no
`block: true`) results simply join.

This research verified, via real `typst.compile()` calls (`typst-py` 0.15.0) against minimal
reproductions of the ACTUAL corpus text, that the two Typst stdlib calls named in D-01 —
`parbreak()` and `linebreak()` — are sufficient and correct for four of the five sites when
inserted as bare statements between siblings. The fifth (F14) is fixed differently: **not** via
an inserted break statement, but via the `terms()` function's own `separator:` parameter
(`terms(separator: linebreak(), ...)`), because F14's failure is not a missing-statement-boundary
problem but a Typst-layout-default problem (the built-in `terms()` separator between a term and
its description defaults to a *weak* `h(0.6em)` horizontal space, not a line break).

**Critical correctness finding not stated in CONTEXT.md, discovered empirically this session:**
the shared helper (D-03) MUST append the break token followed by an **unconditional** `"\n"` —
not one gated on `self.in_list_item`. `visit_desc_signature_line`'s existing precedent gets its
trailing newline "for free" because it always fires *inside* an already-open `strong({...})`
block, where `visit_strong` has locally forced `in_list_item = True` for children. F7/F13/F15's
break points sit at SIBLING boundaries — outside any such block, where `in_list_item` is
typically `False` — so relying on the next node's own conditional separator check reproduces the
exact `"expected semicolon or line break"` fatal this phase is fixing. This was confirmed by a
real compile of `linebreak()strong({...})` (zero whitespace) failing, and the same content with an
explicit newline succeeding. See Common Pitfalls #1.

**Primary recommendation:** Add one shared translator method (suggested name
`_emit_forced_break(break_token: str)`) implementing the corrected idiom below, call it at four
sites with `"parbreak()"` (F1, F15) or `"linebreak()"` (F7, F13), and fix F14 with a one-line
`terms()` call-site change that does not use the helper at all.

## Architectural Responsibility Map

This project is a document-compiler pipeline, not a client/server web app; the table below maps
each capability to the pipeline stage that owns it instead of a browser/API/DB tier.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Paragraph/signature/rubric/definition-list/desc separator emission | Translator (`translator.py` `visit_*`/`depart_*`) | — | The doctree → Typst-source codegen step is the only place block/inline emission decisions are made; nothing downstream can recover lost structure. |
| Break-token correctness (does the emitted Typst actually compile/render) | External Compiler (`typst-py` via `pdf.py`) | Translator | The compiler is the ground truth for whether a break token is syntactically valid and visually correct — verified this session via real `typst.compile()`, not just structural `.typ` inspection. |
| Regression proof (GATE-01) | Test suite (`tests/test_*_render_gate.py`) | Translator | Each fix's fixture is the only artifact that proves the fix in a way a future refactor cannot silently regress. |
| Template/`@preview` surface | Template Engine (`template_engine.py`, `templates/base.typ`) | — | Explicitly OUT of scope this phase (milestone invariant) — no capability in this phase touches this tier. |

## Project Constraints (from CLAUDE.md)

- **Python 3.10+ compatibility required** — do not "modernize" `Dict`/`List` typing imports (ruff
  ignores `UP006`/`UP035` deliberately). Any new helper method must use plain `str`/`bool` params
  (no new typing-import surface needed for this phase's changes).
- **The `@preview` version-sync hazard is OUT OF SCOPE** — `writer.py` / `template_engine.py` /
  `templates/base.typ` must NOT be touched this phase (confirmed: none of the five fixes require
  touching any of these three files — all five sites live entirely in `translator.py`).
- **NixOS-sandbox PATH hazard** — invoke Sphinx via `sys.executable -m sphinx`, never
  `uv run <binary>`. The two existing render-gate fixtures already follow this convention exactly
  (see `_run_sphinx_build_typstpdf` in both); new fixtures MUST copy this helper verbatim.
- **`N802` ignored in ruff** — `visit_*`/`depart_*` PascalCase-after-underscore method names are
  fine as-is (docutils visitor convention).
- Line length 88 (black), `E501` ignored (black owns wrapping) — keep new docstrings/comments
  black-formatted.

## Standard Stack

No new runtime dependency is needed or permitted this phase (milestone invariant, reaffirmed in
REQUIREMENTS.md and STATE.md). The existing pinned stack already provides everything required:

| Library | Version (verified this session) | Purpose | Why Standard |
|---------|------|---------|--------------|
| `typst` (typst-py) | `0.15.0` `[VERIFIED: installed venv — uv run python3 -c "import typst; print(typst.__version__)"]` | The embedded Typst compiler; `typst.compile()` is what every GATE-01 fixture (existing and new) calls transitively via `TypstPDFBuilder.finish()`. | Already the project's sole compile path; `pdf.py` wraps it. Pinned `typst>=0.15.0,<0.16` in `pyproject.toml`. |
| `sphinx` | `>=9.1,<10` `[CITED: pyproject.toml]` | Doctree source; drives `visit_*`/`depart_*` dispatch via `SphinxTranslator`. | Existing pin, untouched this phase. |
| `docutils` | `>=0.21,<0.23` `[CITED: pyproject.toml]` | Doctree node types (`nodes.paragraph`, `nodes.definition_list`, `addnodes.desc*`). | Existing pin, untouched this phase. |
| `pytest` | `9.1.1` `[VERIFIED: uv run pytest --version]` | Test runner; the two existing render-gate modules and the corpus gate all run under it. | Existing pin. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `terms(separator: linebreak(), ...)` (F14) | Wrapping every definition body in `par({...})` unconditionally (removing the F1-style early-return for definitions specifically) | Verified empirically (see Site 4) to render IDENTICALLY for the currently-broken case, but is a bigger, riskier diff (touches the shared paragraph-wrapping logic definitions rely on) for no visual benefit. The `separator:` parameter is a strict one-line superset fix. |
| Inserting `parbreak()` between paragraphs (F1) | Wrapping every list-item paragraph in `par({...})` (matching top-level paragraph behavior) | Verified empirically (see Site 1) to render IDENTICALLY. `parbreak()`-inject is the smaller diff and is what D-01/D-03 already name explicitly. |

**Installation:** none — no new packages.

## Package Legitimacy Audit

**Not applicable.** This phase installs zero new packages (milestone invariant). No
`package-legitimacy check` run was needed; nothing to verify against a registry.

## Architecture Patterns

### System Architecture Diagram

```
docutils doctree (already parsed/resolved by Sphinx)
        │
        ▼
TypstTranslator.visit_document()          ── opens "#{\n" (unified code-mode block)
        │
        ▼
  visit_*/depart_* dispatch, per node  ◄── THIS PHASE'S 5 SITES LIVE HERE
        │  ├─ visit_paragraph/depart_paragraph .......... FID-02 (F1)
        │  ├─ visit_desc / visit_desc_signature .......... FID-03 (F7)
        │  ├─ depart_rubric ................................ FID-04 (F13)
        │  ├─ depart_definition_list (terms() emission) ... FID-05 (F14)
        │  └─ depart_desc ................................... FID-06 (F15)
        │
        ▼
self.body: list[str]  (joined by TypstWriter via astext())
        │
        ▼
TemplateEngine.render()  ── wraps body in #show: project.with(...) (UNTOUCHED this phase)
        │
        ▼
  emitted .typ file  ──► TypstPDFBuilder.finish() ──► typst.compile() ──► .pdf
                                                            │
                                                            ▼
                                              GATE-01 fixture assertions:
                                              (a) structural .typ token assert
                                              (b) %PDF magic on real compile output
```

Every one of this phase's fixes is a pure `self.body`-emission change inside step 2
(`visit_*`/`depart_*` dispatch). Nothing downstream (TemplateEngine, `pdf.py`) needs to change —
confirmed no site requires new template parameters or package imports.

### Recommended Code Location

All five fixes live in `typsphinx/translator.py` only (no other file touched):

```
typsphinx/translator.py
├── add_text() (~247)                         # unchanged; reused by all 5 fixes
├── visit_paragraph/depart_paragraph (~661-708)      # FID-02 fix site
├── visit_strong/depart_strong (~1070-1147)          # unchanged; understand this to reason about F7's list_item overload
├── visit_list_item/depart_list_item (~1409-1470)    # unchanged; understand list_item_needs_separator reset (~1434)
├── visit_definition_list/depart_definition_list (~1637-1719)  # FID-05 fix site (terms() call, ~1706-1713)
├── visit_desc/depart_desc (~4299-4324)              # FID-06 fix site (depart_desc, ~4318-4324); FID-03's "is this the first signature" flag reset goes in visit_desc
├── visit_desc_signature/depart_desc_signature (~4326-4371)  # FID-03 fix site
├── visit_desc_signature_line (~4392-4410)           # existing PRECEDENT — do not modify; the shared helper generalizes this idiom but fixes its "relies on being inside strong({})" limitation
└── visit_rubric/depart_rubric (~4655-4677)          # FID-04 fix site (depart_rubric, ~4671-4677)
```

### Shared Helper (D-03) — verified design

```python
# Source: designed and real-compile-verified this session (see "Sources" below for the
# exact experiments). Suggested placement: near add_text() (~261), as a sibling utility.
def _emit_forced_break(self, break_token: str) -> None:
    """
    Emit a real Typst stdlib break (``parbreak()`` / ``linebreak()``) as its own
    code-mode statement between two adjacent siblings.

    A source '\\n' between two code-mode statements is COSMETIC ONLY (proven at
    visit_desc_signature_line, DESC-02) -- it satisfies the parser but produces
    NO visual break, because bare text()/strong() results are inline content
    that simply concatenates. This helper generalizes the DESC-02 idiom, but
    fixes a gap in the original: DESC-02's site is always inside an
    already-open strong({...}) block (in_list_item forced True there by
    visit_strong for its children), so its trailing separator comes "for
    free" from the next child's own list_item_needs_separator check. A
    SIBLING-boundary break (between desc_signatures, after a rubric, after a
    desc) usually is NOT inside such a block (in_list_item is False there in
    the common case), so this helper appends its OWN unconditional trailing
    newline -- omitting it reproduces the "expected semicolon or line break"
    fatal (confirmed via a real compile of the juxtaposed form during
    research).
    """
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")
    self.add_text(f"{break_token}\n")
    if self.in_list_item:
        self.list_item_needs_separator = True
```

### Site 1 — FID-02 (F1): consecutive paragraphs in a `list_item`

**Current code** (translator.py ~661-708) early-returns in both `visit_paragraph` and
`depart_paragraph` when `self.in_list_item`, emitting NOTHING — not even the cosmetic `\n` every
other sibling type gets. Confirmed against the real (pre-fix) corpus output
(`usage/referencing.typ:53-54`):

```
text(") prevents the creation of a link\nbut otherwise keeps the visual output of the role.")
text("For example, writing ")
```
Rendered PNG of the minimal reproduction (`"First dot."` + `"Second word."`, no break):
concatenates to **"First dot.Second word."** — zero separation, exactly matching the audit's
"role.For example" symptom.

**Fix (D-01: `parbreak()`):**

```python
def visit_paragraph(self, node: nodes.paragraph) -> None:
    self._emit_id_anchors(node)
    if self.in_list_item:
        self._emit_forced_break("parbreak()")
        self.in_paragraph = False
        return
    self.in_paragraph = True
    self.paragraph_has_content = False
    self.add_text("par({")

def depart_paragraph(self, node: nodes.paragraph) -> None:
    if self.in_list_item:
        self.list_item_needs_separator = True
        return
    self.in_paragraph = False
    self.paragraph_has_content = False
    self.add_text("})\n\n")
```

`_emit_forced_break("parbreak()")` is a no-op (correctly) for the FIRST paragraph in a list item
(`list_item_needs_separator` is `False`, reset in `visit_list_item` ~1434). Adding
`self.list_item_needs_separator = True` to `depart_paragraph`'s early-return branch is the
**currently-missing piece** — without it the helper never fires for the 2nd+ paragraph.

**Real-compile proof (verified this session, `typst.compile(format="png")`):**

```
// Source: minimal repro compiled via typst-py 0.15.0 this session
#{
list({
text("First dot.")
parbreak()
text("Second word.")
})
}
```
Renders "First dot." on one line, "Second word." indented on the next, with a visible
paragraph-spacing gap — matching the `-b html` authority's separate `<p>` elements. Confirmed
`par()`-wrapping each paragraph individually (the OTHER candidate this research evaluated)
renders **pixel-identical** in this test — `parbreak()`-inject is strictly the smaller diff and is
what D-01 names, so it is the recommended approach; do not additionally wrap paragraphs in
`par({...})`.

**Do NOT reconcile this with the `{ }` list-item content-block concern raised in CONTEXT.md by
wrapping paragraphs in `par()`.** The `{ }` block (added by `visit_list_item`/`depart_list_item`,
~1409-1470, already in place) makes `par()`-wrapping syntactically legal now (the CONTEXT.md
worry about `"- par(...)"` being invalid syntax describes the OLD markup-mode list-item form, not
the current code-mode `{ }`-block form) — but it is unnecessary: `parbreak()`-inject achieves the
identical visual result with a far smaller diff.

### Site 2 — FID-03 (F7): sibling `desc_signature`s

**Current code** (translator.py ~4326-4343): `depart_desc_signature` appends only `"\n"`
(cosmetic). Confirmed against real corpus output (`usage/domains/python.typ:854-859`, the
`compile()` overload group) — three `strong({...})` blocks separated only by source `\n`, and a
minimal reproduction of the exact three signatures renders **"compile(source)compile(source,
filename)compile(source, filename, symbol)"** on one running line — matching the audit exactly.

**Fix (D-01: `linebreak()`):** add a per-`desc` "is this the first signature" flag (mirrors the
existing per-`desc_signature` `_is_first_desc_signature_line` flag one level up):

```python
def visit_desc(self, node: addnodes.desc) -> None:
    self._emit_id_anchors(node)
    self._is_first_desc_signature = True   # NEW — reset per desc, like DESC-02's own-line flag

def visit_desc_signature(self, node: addnodes.desc_signature) -> None:
    if not self._is_first_desc_signature:
        self._emit_forced_break("linebreak()")
    self._is_first_desc_signature = False
    dummy_strong = nodes.strong()
    self.visit_strong(dummy_strong)
    self._is_first_desc_signature_line = True
```

**Real-compile proof:** the three-overload reproduction with `linebreak()` inserted between each
`strong({...})` renders each signature on its own line, wrapping naturally where too long — the
correct "stacked lines" result. A `desc` with a single `desc_signature` (the overwhelming common
case) emits zero extra bytes (flag stays `True` through the only signature) — byte-for-byte
unchanged, matching existing `_is_first_desc_signature_line` precedent's single-line
backward-compat guarantee.

**Note on nested `desc` (class containing method `desc`s):** `_is_first_desc_signature` is a
scalar (not a stack), matching `_is_first_desc_signature_line`'s existing precedent. This is safe
because a `desc` node's own `desc_signature` children are always fully processed (doctree order)
BEFORE its `desc_content` (which may contain nested `desc` children) is entered — by the time a
nested `desc` resets the flag, the outer `desc`'s own signature-siblings loop has already
completed and will never re-check the flag.

### Site 3 — FID-04 (F13): rubric/option heading

**Current code** (translator.py ~4655-4677): `depart_rubric` appends only `"\n"` (cosmetic).
Confirmed against real corpus output twice: `man/sphinx-quickstart.typ:57-58` ("Structure
Options" rubric directly followed by the `--sep` option's `strong({...})`) and
`usage/restructuredtext/directives.typ:151-152` ("Options" rubric directly followed by the
`:class:` field's `strong({...})`) — both are the SAME underlying pattern (rubric renders via
`strong()`, delegate `visit_strong`/`depart_strong`; whatever follows ALSO renders via `strong()`
whether it's a true `option` `desc_signature` or a synthesized field). One fix at `depart_rubric`
covers both audit sub-cases.

**Fix (D-01: `linebreak()`, unconditional — rubric always needs separation from what follows):**

```python
def depart_rubric(self, node: nodes.rubric) -> None:
    dummy_strong = nodes.strong()
    self.depart_strong(dummy_strong)
    self._emit_forced_break("linebreak()")
```

**Real-compile proof:** `strong({text("Structure Options")})` + `linebreak()` +
`strong({text("--sep")})` + `par({text("If specified, separate source and build
directories.")})` renders "Structure Options" / "--sep" / description, matching the `-b text`
authority's `-[ Structure Options ]-` then `--sep` layout exactly.

Verified harmless at true end-of-document (nothing follows a trailing `linebreak()`) — no compile
error, no visible artifact.

### Site 4 — FID-05 (F14): definition_list `term`/`definition`

**Root cause is the SAME early-return as F1** (translator.py `visit_paragraph`/`depart_paragraph`
~683-703), but manifests differently and needs a DIFFERENT, non-`list_item_needs_separator` fix.

Confirmed via real corpus output (`usage/configuration.typ:5458`, the `texinfo_elements`
`'paragraphindent'` case — F14 sub-case (a), def-list nested in a `list_item`):
```
terms(terms.item(raw("'paragraphindent'"), {text("Number of spaces to indent the first line of each paragraph,\ndefault ")...}), ...)
```
The definition arg is `{text(...)}` — a `{ }`-wrapped run of BARE INLINE `text()` calls (no
`par()`), because `_wrap_definition_arg` (~1765-1788) only wraps the ALREADY-assembled buffer; it
does not make inline content block-level. Contrast the currently-WORKING case
(`usage/configuration.typ:3383`, `'sphinx.search.ja.DefaultSplitter'`, NOT nested in a list item):
`terms.item(raw(...), {par({text(...)})})` — the definition IS `par()`-wrapped there (block-level),
because that definition_list sits outside any `list_item`, so `visit_paragraph` does NOT
early-return.

**Why this matters:** Typst's built-in `terms()` function's `separator` parameter — the content
placed between a term and its description — **defaults to `h(0.6em, weak: true)`, a horizontal
space, NOT a line break** `[CITED: https://typst.app/docs/reference/model/terms/]`. When the
definition's first content is a block (`par()`), Typst's block-layout rules force it onto a new
line regardless of the weak separator (a block cannot share a line with preceding inline flow) —
this is WHY the non-nested case "happens to" render correctly today. When the definition's first
content is inline (the F1-early-return case), nothing forces a break, so the weak separator lets
it flow directly after the term on the same visual line — exactly the F14(a) bug. F14(b) (a
definition that opens with a NESTED list/field-list, whose own first rendered content is ALSO
inline `strong()`/`text()`, not a block) is the identical mechanism one level deeper — confirmed
against `usage/configuration.typ:3401`, the `mecab` case:
`terms.item(text("Options for ") + raw("'mecab'") + text(":"), {strong(text("dic_enc") + text(":")) par({...}) ...})`.

**Fix — do NOT use the shared `_emit_forced_break` helper here.** Set the `terms()` call's own
`separator` parameter to `linebreak()`, unconditionally, for every definition list (translator.py
`depart_definition_list`, ~1706-1713):

```python
if items:
    items_str = ", ".join(
        f"terms.item({term}, {self._wrap_definition_arg(definition)})"
        for term, definition in items
    )
    self.add_text(f"terms(separator: linebreak(), {items_str})\n\n")
else:
    self.add_text("terms(separator: linebreak())\n\n")
```

**Real-compile proof (both sub-cases and the no-regression check):**
- F14(a) reproduction (`'paragraphindent'`/`'exampleindent'` nested in a `list()` item, bare-inline
  definitions): WITHOUT the fix, renders "'paragraphindent'  Number of spaces to indent the first
  line..." merged on one line (exact audit match). WITH `separator: linebreak()`, renders the term
  on its own line, definition indented below, for BOTH terms — fixed.
- Regression check on the currently-working top-level case
  (`'sphinx.search.ja.DefaultSplitter'`, `par()`-wrapped definition): with
  `separator: linebreak()` added, renders **identically** to the current (correct) output — no
  visual regression, and it becomes deterministic rather than incidental.
- Empty-items edge case (`terms(separator: linebreak())`, zero positional args) compiles cleanly —
  Typst accepts a named-only call.
- F14(b) is fixed by the same one-line change since the separator applies uniformly to the OUTER
  term regardless of what the definition's first child renders as.

**This is a one-line, self-contained change independent of `in_list_item`/
`list_item_needs_separator` state** — do not force it through the shared helper; it is not a
statement-boundary insertion, it is a function-call parameter.

### Site 5 — FID-06 (F15): back-to-back body-less `confval` `desc` nodes

**Current code** (translator.py `depart_desc`, ~4318-4324) appends only `"\n\n"` (cosmetic).
Confirmed against real corpus output (`usage/extensions/coverage.typ:126-153`, four confvals with
only `Type:`/`Default:` fields, no body paragraph): each confval's content
(`strong({name}) strong("Type:") raw(...) strong("Default:") raw(...)`) is entirely inline (no
`par()` anywhere, since there is no body text), so consecutive `desc` siblings concatenate with
zero separation. Minimal reproduction confirms the exact blob:
**"coverage_c_pathType:Sequence[str]Default:()coverage_c_regexesType:dict[str, str]Default:{}"**.

**Fix (D-01: `parbreak()`, unconditional — safe to always emit):**

```python
def depart_desc(self, node: addnodes.desc) -> None:
    self._emit_forced_break("parbreak()")
```

**Real-compile proof:** the four-confval reproduction with `parbreak()` inserted between `desc`
siblings renders each confval as a visually distinct block — matching the HTML authority's
separate `<dl class="std confval">` elements. **Verified idempotent/harmless on the
WITH-body-content case** (a confval whose last content is already a `par()`): adding a redundant
`parbreak()` after an already-block-ending confval produces a **pixel-identical** render to the
unmodified version — no double-gap artifact. This means the fix can be applied unconditionally at
EVERY `depart_desc`, with no need to detect "was this confval body-less" — significantly
simplifying the implementation and removing an entire class of conditional-logic risk.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Forcing a visible paragraph/line break in Typst code mode | Any heuristic based on counting `\n`/`\n\n` in the emitted string, or post-processing the `.typ` text to insert blank lines | `parbreak()` / `linebreak()` (Typst stdlib, already imported implicitly — no `#import` needed, they're global functions) | Confirmed via real compile this session that bare newlines between code-mode statements are COSMETIC ONLY regardless of count (`\n` and `\n\n` render identically) — any fix based on newline-counting cannot work, only the two stdlib break calls do. |
| Detecting "does this definition/paragraph already end in a block" to conditionally apply a break | A content-inspection heuristic (regex/string-suffix check on the assembled buffer for `par({`/`list(`/etc.) | Emit the break token UNCONDITIONALLY (verified harmless when redundant, Site 5) | The unconditional approach was empirically proven byte-for-visual-identical to the conditional one in every case tested this session, and is far less code/risk. |
| Forcing "term always on its own line" in a Typst `terms()` list | Manually inserting a `linebreak()` INTO the term or definition buffer string | The `terms()` function's own `separator:` parameter (`terms(separator: linebreak(), ...)`) | This is a first-class Typst API for exactly this purpose — `[CITED: typst.app/docs/reference/model/terms/]`; string-splicing a break into a buffer is fragile against future buffer-assembly changes (e.g. the `_wrap_definition_arg`/multi-block-definition logic) and duplicates logic across every one of the ~30 `terms.item(...)` emission call sites instead of the ONE `terms(...)` call site. |

**Key insight:** every one of these five findings is a variant of the SAME underlying Typst
behavior (code-mode statement adjacency is not visual layout adjacency) — the fix is always "emit
the stdlib primitive Typst provides for this exact purpose," never a string-manipulation
workaround.

## Common Pitfalls

### Pitfall 1: Relying on a downstream node's own separator check instead of an unconditional trailing newline

**What goes wrong:** copying `visit_desc_signature_line`'s exact pattern (emit `break_token` with
NO trailing newline, relying on the next child's own `if self.in_list_item and
self.list_item_needs_separator: add_text("\n")` check) verbatim to a SIBLING-boundary site (F7,
F13, F15) reproduces the EXACT `"expected semicolon or line break"` Typst fatal this phase exists
to fix — but as a NEW regression, not the old bug.

**Why it happens:** `visit_desc_signature_line`'s break always fires *inside* an already-open
`strong({...})` block, where `visit_strong` has locally forced `self.in_list_item = True` for its
own children (translator.py ~1101, "treat it like list_item"). That forced state is what makes
the NEXT child's own separator check reliably fire. At a sibling boundary (between two
`desc_signature`s, after a `rubric`, after a `desc`) there is no such open block — the ambient
`self.in_list_item` reflects the OUTER context (usually `False`, unless the whole construct
happens to be nested inside a real bullet list item), so the next node's conditional check
silently does nothing, and `linebreak()`/`parbreak()` ends up directly abutting the following
`strong({`/`text(` call with zero separating characters.

**How to avoid:** the shared helper MUST append `f"{break_token}\n"` (unconditional trailing
newline baked into the same `add_text` call), never just `break_token` alone. Confirmed via real
compile this session: `linebreak()strong({text("x")})` (zero whitespace) fails with `expected
semicolon or line break`; the identical content with a newline between the two compiles cleanly.

**Warning signs:** a GATE-01 fixture (or the corpus gate) failing with `TypstError: expected
semicolon or line break` pointing at a line combining `linebreak()`/`parbreak()` immediately
followed by another function call with no whitespace between them.

### Pitfall 2: Assuming F1's fix requires reconciling with the `{ }` list-item block by `par()`-wrapping

**What goes wrong:** CONTEXT.md flags a real historical concern (paragraphs in list items used to
risk invalid `"- par(...)"` markup syntax) as something the F1 fix "must reconcile." A planner
might over-engineer the fix into a full `par()`-wrap-every-paragraph change.

**Why it happens:** the concern is stale relative to the current architecture — `visit_list_item`
now wraps item content in a code-mode `{ }` block (translator.py ~1431), inside which a `par()`
call is syntactically ordinary (it's just a function-call statement, not markup-mode `"- "`
syntax). The `{ }`-block change already resolved the syntax hazard; it just didn't fix the missing
VISUAL break, which is F1's actual bug.

**How to avoid:** use `parbreak()`-inject (Site 1's fix), not full `par()`-wrap. Verified this
session to render pixel-identical to the `par()`-wrap alternative, with roughly 1/10th the diff
size and zero risk to the many other list-item call sites that assume paragraphs stay unwrapped.

**Warning signs:** a PLAN.md task that proposes removing/inverting the
`if self.in_list_item: ... return` early-return in `visit_paragraph`/`depart_paragraph` — that is
the `par()`-wrap approach and is unnecessary.

### Pitfall 3: Treating F14 as a fifth instance of the shared `_emit_forced_break` helper

**What goes wrong:** D-03 says "one small shared helper reused at all five sites" — a planner
might force F14's fix through the same statement-boundary-insertion helper used at the other four
sites, either by inserting a `linebreak()` INTO the term or definition buffer string, or by trying
to make `depart_definition_list` call `_emit_forced_break` somehow.

**Why it happens:** taking D-03's "all five sites" literally without accounting for F14's fix
being structurally different (a function-CALL-PARAMETER change, not a statement-boundary
insertion).

**How to avoid:** F14's fix is a one-line, self-contained change to the `terms(...)` call
assembly in `depart_definition_list` (`terms(separator: linebreak(), ...)`), independent of
`in_list_item`/`list_item_needs_separator`. Present this to the planner explicitly as the
correct reading of D-03 (the "one small shared helper... parameterized by break kind" language is
satisfied by all five sites choosing a `linebreak()`/`parbreak()`-flavored fix in intent; it does
not require identical call-site mechanics for F14, whose bug is not a missing-statement-separator
bug at all).

### Pitfall 4: Corpus-gate blast radius from touching `visit_paragraph`

**What goes wrong:** `visit_paragraph`/`depart_paragraph` is one of the highest-traffic node
handlers in the translator (every paragraph in the ~684-page corpus passes through it). A subtle
mistake in the F1 fix (e.g. forgetting the `depart_paragraph` early-return also needs
`self.list_item_needs_separator = True`, or getting the helper's leading-separator-vs-trailing-flag
order wrong) risks a corpus-wide regression, not a localized one.

**Why it happens:** F1 has "highest blast radius" per CONTEXT.md's own framing — it's the only one
of the five findings confirmed "corpus-wide" rather than at specific docnames.

**How to avoid:** run the FULL `tests/test_corpus_gate.py::TestCorpusRenderGate` (not just the
new/extended per-finding fixtures) as a phase-gate step, not just a task-level check. Confirmed
this session: the full corpus gate currently passes in ~14s against the pre-fix translator
(`pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow`, `1 passed in 13.88s` — the
corpus clone is already cached at `~/.cache/typsphinx-corpus-gate`, so this is fast, not the
minutes a cold clone would take). Re-run it after EVERY wave, not only at phase end.

## Code Examples

### Verified minimal reproduction harness (recommended for the planner/executor to keep using)

```python
# Source: built this session at
# /tmp/.../scratchpad/typst_experiments/gen.py — a reusable pattern for verifying
# break-token placement against a REAL typst.compile() before writing a GATE-01 fixture.
import typst

def render_to_png(typst_source_path: str, out_png_path: str) -> None:
    png = typst.compile(typst_source_path, format="png", ppi=150)
    data = png if isinstance(png, bytes) else png[0]
    with open(out_png_path, "wb") as f:
        f.write(data)
```

Remember: a `.typ` file's TOP LEVEL is markup mode by default. To reproduce the translator's
actual output faithfully, any minimal `.typ` reproduction MUST wrap the body in `#{ ... }` (the
same wrapper `visit_document`/`depart_document` emit) — a bare `list(...)` / `strong(...)` call at
top level with no `#` prefix is parsed as literal prose, not a function call (this cost real time
to discover this session; a `.typ` reproduction that omits the `#{ }` wrapper will silently
"verify" the WRONG thing, since it just echoes the source text back as a page of prose instead of
executing it).

### Verified GATE-01 fixture skeleton (mirrors the two existing modules exactly)

```python
# Source: pattern extracted from tests/test_desc_signature_concat_render_gate.py and
# tests/test_deflist_term_concat_render_gate.py (both currently passing, confirmed this
# session: `pytest tests/test_desc_signature_concat_render_gate.py
# tests/test_deflist_term_concat_render_gate.py -q` -> "2 passed in 0.59s").
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401
    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

def _run_sphinx_build_typstpdf(source_dir: Path, build_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typstpdf", str(source_dir), str(build_dir)],
        capture_output=True, text=True,
    )

@pytest.mark.skipif(not TYPST_AVAILABLE, reason="typst-py is required")
class TestParagraphConcatRenderGate:
    def test_typstpdf_paragraphs_in_list_item_produce_pdf(self, fixture_dir, tmp_path):
        build_dir = tmp_path / "_build"
        result = _run_sphinx_build_typstpdf(fixture_dir, build_dir)
        assert result.returncode == 0
        typ_text = (build_dir / "index.typ").read_text(encoding="utf-8")
        # D-05: structural assert -- the pre-fix translator emits NO parbreak() at all
        # between two list-item paragraphs, so this string is absent pre-fix and
        # present post-fix.
        assert "parbreak()" in typ_text
        pdf_path = build_dir / "index.pdf"
        assert pdf_path.exists() and pdf_path.stat().st_size > 0
        assert pdf_path.read_bytes()[:4] == b"%PDF"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Bare `\n`/`\n\n` between code-mode statements as the ONLY separator (the pattern still used at ~25 of the ~30 `list_item_needs_separator` call sites for non-paragraph/non-signature siblings, e.g. `literal_block`, `bullet_list`) | Real Typst stdlib break (`parbreak()`/`linebreak()`) as a standalone statement | This phase (v0.6.2 Phase 19) for the 5 findings in scope; NOT retrofitted to the other ~25 sites this phase (out of scope — those sites' targets are already block-level Typst calls like `list()`/`raw()`/`table()`, which get automatic block-to-block spacing regardless of the cosmetic `\n`, so they were never broken the way F1/F7/F13/F14/F15 are). | Establishes the idiom Phase 20 (`desc_*`/signature surface) will build directly on, per CONTEXT.md's stated Phase 20 handoff note. |

**Deprecated/outdated:** none — no external API/library version changes are involved in this
phase; the "old approach" row above is a proven-insufficient PATTERN within this codebase, not an
external tool.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `terms()`'s default `separator` value (`h(0.6em, weak: true)`) and its `separator` parameter's documented semantics come from the official Typst docs page fetched this session (`typst.app/docs/reference/model/terms/`) — tagged `[CITED]` rather than `[VERIFIED]` because it is doc-page content, not something re-derived from Typst's source code. | Site 4 / Don't Hand-Roll | LOW — independently reproduced empirically via 3 real compiles (broken case, fixed case, no-regression case) in this same session, so even if the doc-page prose were imprecise, the EMPIRICAL behavior (verified via PNG rendering) is what the recommendation is actually grounded in. |
| A2 | Every one of the ~30 existing `list_item_needs_separator` call sites NOT touched by this phase (e.g. `literal_block`, `bullet_list`, `table`) is safe from the F1/F7/F13/F14/F15 class of bug because their emitted Typst call is already block-level (`raw()`, `list()`, `table()`) and therefore gets automatic block-spacing regardless of the cosmetic-only `\n`. This was reasoned from Typst's general block-layout behavior, not exhaustively re-verified against every one of those ~30 sites this session (only a representative literal_block/bullet_list-adjacent case was inspected, per the `test_list_item_nested_block_render_gate.py` precedent read this session). | State of the Art table; Pitfall 4 | MEDIUM — if wrong, there could be a 6th latent finding outside this phase's five, but the Phase 17 audit (an exhaustive human-confirmed visual pass over the full corpus, D-01a) did NOT flag any such 6th finding, so the risk is that the audit missed something already, not that this research invented a new gap. |

## Open Questions

1. **Should the shared helper be a single `_emit_forced_break(break_token: str)` or two
   thin named wrappers (`_emit_parbreak()`/`_emit_linebreak()`)?**
   - What we know: D-03 asks for "one small shared helper... parameterized by break kind" — the
     single-parameter design above satisfies this literally and was what was compile-verified this
     session.
   - What's unclear: whether the planner/executor prefers the ergonomics of two zero-arg wrappers
     (marginally more readable call sites: `self._emit_parbreak()` vs
     `self._emit_forced_break("parbreak()")`) at the cost of two extra tiny methods.
   - Recommendation: either is fine; this is a pure style choice with zero behavioral difference.
     The plan should pick one and apply it consistently across all four sites that use it (F1, F7,
     F13, F15 — NOT F14, which does not use this helper at all per Pitfall 3).

2. **Fixture consolidation** (CONTEXT.md's "Claude's Discretion" gray area) — one fixture module
   per finding (5 new/extended modules) vs. a shared multi-finding fixture project.
   - What we know: the two existing analog modules (F7, F14) are each single-concern, single-finding
     modules; this repo's established convention (11+ existing `*_render_gate.py` modules, all
     single-concern) strongly favors one-module-per-finding.
   - What's unclear: nothing technical blocks consolidation; it is purely a maintainability
     preference.
   - Recommendation: follow the established one-gate-module-per-finding convention (extend
     `test_desc_signature_concat_render_gate.py` for F7 and `test_deflist_term_concat_render_gate.py`
     for F14 with additional test methods in the SAME module since they already exist for
     adjacent-but-distinct GATE-02 bugs on the same node kinds; add three new modules for F1/F13/F15,
     e.g. `test_paragraph_concat_render_gate.py`, `test_rubric_option_concat_render_gate.py`,
     `test_desc_bodyless_concat_render_gate.py`).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `typst` (typst-py) | GATE-01 fixtures, corpus gate, all research verification this session | ✓ | 0.15.0 | — |
| `sphinx` console entry (`sys.executable -m sphinx`) | GATE-01 fixtures | ✓ | 9.1.0 (installed) | — |
| Cached corpus clone (`~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0`) | `tests/test_corpus_gate.py` full-corpus regression check | ✓ (already cloned, tag `v9.1.0`) | git-cloned working tree | Cold clone if cache absent (network required); the corpus gate `pytest.skip`s gracefully rather than failing if unavailable (D-05 in its own prior-phase context). |
| `pypdf` | Optional strengthening (D-06, not required) | ✓ (6.14.2, already a transitive/available dependency in this venv) | 6.14.2 | Not needed — GATE-01's required check is the structural `.typ` assert + `%PDF` magic, not text extraction. |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** none — everything required is already present and
verified working in this environment.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (config in `pyproject.toml` `[tool.pytest.ini_options]`) |
| Config file | `pyproject.toml` (testpaths=`tests`, markers `slow`/`integration` registered, `--strict-markers`) |
| Quick run command | `uv run pytest tests/test_translator.py tests/test_paragraph_concat_render_gate.py tests/test_desc_signature_concat_render_gate.py tests/test_rubric_option_concat_render_gate.py tests/test_deflist_term_concat_render_gate.py tests/test_desc_bodyless_concat_render_gate.py -q` (module names for the 3 new modules are this research's recommendation — see Open Questions #2; adjust to whatever the plan finalizes) |
| Full suite command | `uv run pytest -q` (excludes `-m slow` by default only if the plan adds that filter; currently `pyproject.toml` has no default `-m` exclusion, so a plain `pytest` run DOES include the corpus gate — confirmed this session it completes in ~14s with the corpus already cached, so this is acceptable as the default) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FID-02 | Consecutive paragraphs in a list item render `parbreak()`-separated, real compile succeeds | render-gate (GATE-01) | `pytest tests/test_paragraph_concat_render_gate.py -x` | ❌ Wave 0 (new module) |
| FID-03 | Sibling `desc_signature`s render `linebreak()`-separated | render-gate (GATE-01), extend existing module | `pytest tests/test_desc_signature_concat_render_gate.py -x` | ✅ module exists (extend with a new test method + fixture variant) |
| FID-04 | Rubric-then-option/field renders `linebreak()`-separated | render-gate (GATE-01) | `pytest tests/test_rubric_option_concat_render_gate.py -x` | ❌ Wave 0 (new module) |
| FID-05 | `terms()` emits `separator: linebreak()`; term/definition render on separate lines in both sub-cases | render-gate (GATE-01), extend existing module | `pytest tests/test_deflist_term_concat_render_gate.py -x` | ✅ module exists (extend with 2 new test methods, one per sub-case) |
| FID-06 | Back-to-back body-less confvals render `parbreak()`-separated | render-gate (GATE-01) | `pytest tests/test_desc_bodyless_concat_render_gate.py -x` | ❌ Wave 0 (new module) |
| (all 5, non-regression) | Full corpus (~684 pages) still compiles fatal-free, no new `unknown_visit` entries | full-corpus regression | `pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q` | ✅ exists; confirmed passing (13.88s) against the pre-fix translator this session — MUST still pass post-fix |

### Sampling Rate

- **Per task commit:** the specific finding's render-gate test (`pytest tests/test_X_render_gate.py -x`) — each is < 1s per the two existing modules' measured runtime (`0.59s` for both combined this session).
- **Per wave merge:** all render-gate modules for findings completed so far, plus
  `tests/test_translator.py` (existing unit-test coverage for `visit_paragraph`/`visit_desc`/etc.,
  to catch a non-render structural regression the render-gate's PDF-level assert might not
  surface).
- **Phase gate:** `pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q` green
  before `/gsd-verify-work` — confirmed this session it runs in ~14s with the corpus cache warm,
  so there is no reason to skip it at the phase gate.

### Wave 0 Gaps

- [ ] `tests/test_paragraph_concat_render_gate.py` + `tests/fixtures/paragraph_concat_render_gate/{conf.py,index.rst}` — covers FID-02. Fixture `index.rst` needs a bullet item with 2+ paragraphs, e.g. mirroring the real corpus text at `usage/referencing.rst` ("Suppressed link:" item).
- [ ] `tests/test_rubric_option_concat_render_gate.py` + `tests/fixtures/rubric_option_concat_render_gate/{conf.py,index.rst}` — covers FID-04. Fixture needs a `.. rubric::` immediately followed by `.. option::` (mirrors `man/sphinx-quickstart.rst`'s "Structure Options"/`--sep` pattern) — a plain `.rst` project (no `man` builder needed; `option` directive is available without the `std` domain being anything special).
- [ ] `tests/test_desc_bodyless_concat_render_gate.py` + `tests/fixtures/desc_bodyless_concat_render_gate/{conf.py,index.rst}` — covers FID-06. Fixture needs 2+ back-to-back `.. confval::` directives with ONLY `:type:`/`:default:` fields, no body paragraph.
- [ ] Extend `tests/test_desc_signature_concat_render_gate.py` with a new fixture/test method for FID-03 (multiple sibling signatures under one directive — can reuse the module's existing offline-intersphinx pattern, or use a plainer construct like `.. py:function::` with two signature lines, which needs no intersphinx at all).
- [ ] Extend `tests/test_deflist_term_concat_render_gate.py` with two new fixture/test methods for FID-05: (a) a definition list nested inside a bullet `list_item`, (b) a definition list term whose definition opens with a nested field/definition list.

## Security Domain

`security_enforcement` is `true` in `.planning/config.json`, so this section is required even
though this phase has no plausible new attack surface — documented explicitly rather than
omitted.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | This phase touches only offline document-to-document markup translation; no auth surface exists in this tool. |
| V3 Session Management | No | N/A — CLI/library, no sessions. |
| V4 Access Control | No | N/A. |
| V5 Input Validation | No new surface | Input is an already-parsed docutils doctree (Sphinx has already validated/resolved it before the translator runs); this phase adds no new external input path, only changes WHICH Typst stdlib tokens are emitted for already-trusted node content. String content itself continues to flow through the EXISTING `escape_typst_string()` helper (unchanged this phase) at every `text()`/`raw()` emission site touched. |
| V6 Cryptography | No | N/A — no crypto in this tool. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Typst code-mode injection via unescaped user-controlled string content reaching a raw `text("...")`/`raw("...")` call | Tampering | Already mitigated by the existing `escape_typst_string()` helper (used at every string-emission site touched by this phase — `visit_Text` ~924, and unchanged in this phase's new `_emit_forced_break` calls, which only ever emit the FIXED literal strings `"parbreak()"`/`"linebreak()"`/`"terms(separator: linebreak(), "` — never user-controlled content). No new injection surface is introduced because none of the five fixes interpolates document content into the break-token strings themselves. |

## Sources

### Primary (HIGH confidence)

- Real `typst.compile()` calls this session (`typst-py` 0.15.0, matching the project's pinned
  `typst>=0.15.0,<0.16`) — every break-token recommendation in "Architecture Patterns" was
  compiled and, where a visual claim is made, rendered to PNG (`format="png", ppi=150`) and
  visually inspected. Experiment files (session-scratch, not committed):
  `/tmp/.../scratchpad/typst_experiments/{A2,B2,C2,C3,D2,E2,G,H,I,J,K,L,M,N,O,P,Q,R,S,T}*.typ`
  and corresponding `.png` outputs.
- Full Sphinx `doc/` corpus (`~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0`, tag `v9.1.0`)
  translated end-to-end with the CURRENT (pre-fix) translator via
  `uv run python3 -m sphinx -b typst <corpus>/doc <scratch>/build_typst` this session — every
  "Current code" claim above cites an exact line number in the resulting `.typ` output, not a
  guess.
- `tests/test_desc_signature_concat_render_gate.py`,
  `tests/test_deflist_term_concat_render_gate.py`, `tests/test_corpus_gate.py`,
  `tests/test_list_item_nested_block_render_gate.py` (all read in full this session) — the
  established GATE-01/GATE-02 fixture and idiom precedents this research's recommendations extend.
- `typsphinx/translator.py` (read in full at every cited line range this session): `add_text`
  (~247-261), `_emit_id_anchors` (~275-346), `visit_paragraph`/`depart_paragraph` (~661-708),
  `visit_Text` (~903-948), `visit_strong`/`depart_strong` (~1070-1147),
  `visit_list_item`/`depart_list_item` (~1409-1470),
  `visit_definition_list`/`depart_definition_list`/`_wrap_definition_arg`/`visit_term`/
  `depart_term`/`visit_definition`/`depart_definition` (~1637-1921),
  `visit_desc`/`depart_desc`/`visit_desc_signature`/`depart_desc_signature`/
  `visit_desc_signature_line` (~4299-4415), `visit_rubric`/`depart_rubric` (~4655-4677).

### Secondary (MEDIUM confidence)

- Typst official docs, `terms` element reference —
  `[CITED: https://typst.app/docs/reference/model/terms/]`, fetched via `tavily_extract` this
  session — the `separator` parameter default (`h(0.6em, weak: true)`) and its documented
  semantics. Cross-checked against 3 independent real compiles this session (broken case, fixed
  case, no-regression case), so the empirical behavior is independently confirmed, not solely
  relying on the doc-page prose.

### Tertiary (LOW confidence)

- None — every claim in this document is either grounded in a real compile performed this
  session, a direct read of the current repository source, or the official Typst docs page cited
  above.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies; existing pins verified installed and working.
- Architecture (5 fix designs): HIGH — every fix was compiled and, for visual claims, rendered and
  inspected this session against a minimal reproduction of the ACTUAL corpus text at the cited
  file/line.
- Pitfalls: HIGH — Pitfall 1 (the trailing-newline requirement) was DISCOVERED this session via a
  real compile failure, not inferred from documentation; it is the single most important
  correction to CONTEXT.md's stated precedent ("mirrors `visit_desc_signature_line`") that this
  research surfaces.

**Research date:** 2026-07-20
**Valid until:** 30 days (stable, self-contained translator logic; not tied to any fast-moving
external dependency — the only external surface, `typst-py`/Typst semantics, is pinned and its
relevant behavior (code-mode statement adjacency, `terms()` default separator) was independently
verified against the actual compiler this session rather than assumed from a changelog).
