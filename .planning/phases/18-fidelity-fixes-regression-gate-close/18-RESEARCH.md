# Phase 18: Fidelity Fixes + Regression-Gate Close - Research

**Researched:** 2026-07-19
**Domain:** Typst `table()` column-sizing semantics (native Typst layout, no `@preview` package involved) + real-compile regression-fixture design for a *silent* (non-fatal, non-warning) rendering bug
**Confidence:** HIGH — every claim about Typst's column/wrap behavior below was verified empirically in this session by compiling real `.typ` files (hand-built AND translator-emitted) with `typst.compile()` and extracting the resulting PDF text with `pypdf`, not inferred from documentation alone. Documentation citations corroborate, they are not the primary evidence.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: Emit fractional-width (`fr`) columns derived from docutils `colspec['colwidth']`.** Change
  `depart_table`'s `columns: <integer>` (all-`auto`, overflows) to
  `columns: (Nfr, Mfr, …)` built from the per-column `colwidth` relative weights. `fr` columns share
  the available text-block width and wrap cell text, so wide tables fit the page instead of clipping.
  This is the most faithful match to Sphinx's HTML output (the D-04 fidelity authority), whose column
  widths come from `colwidth` (rendered `<col style="width:X%">`) with browser text-wrapping.
  **Implementation note:** `visit_colspec` currently `raise SkipNode` and throws the `colwidth` away —
  it must instead be captured (accumulated per-column, consumed at `depart_table`).

- **D-02: Apply `fr` columns to ALL tables uniformly — no width-based conditional.** Typst cannot know
  a table's natural width at translate time, so there is no reliable translate-time "is this table too
  wide" test. Every table becomes `fr`-columned. Accepted cost: narrow tables that currently render at
  natural content width will stretch to full text-block width — a cosmetic change (content stays
  faithful) that is actually *closer* to HTML's container-filling table behavior. The `measure`-at-
  compile-time alternative (keep narrow tables byte-identical, only fall back to `fr` on overflow) was
  considered and rejected as too complex to emit + verify on every table for a one-root-cause fix.

- **D-03: Honor `colwidth` only — do NOT parse `.. tabularcolumns::`.** `.. tabularcolumns::` is a
  **LaTeX-only** Sphinx directive; the HTML builder (our D-04 fidelity authority) **ignores it
  entirely**. Honoring it in Typst output would *diverge* from the HTML baseline, not converge on it
  (it would optimize for LaTeX/PDF parity — a different target than our stated fidelity basis).
  Therefore `visit_tabular_col_spec` stays `raise SkipNode` as today.

- **D-04: GATE-03 is mechanical, not a design decision.** Re-run the corpus gate: assert the corpus
  still compiles fatal-free (`index.pdf` produced, 0 errors — GATE-02 non-regression) AND the
  `unknown_visit` catalogue is empty of `todo_node`/`manpage`. Reuse the existing
  `tests/test_corpus_gate.py` machinery — its `test_corpus_compiles_with_no_fatal_error` already
  asserts the empty-`unknown_visit` catalogue (green in Phase 17's fresh run).

### Claude's Discretion

- **Regression-fixture proof design** — this is the primary output of this research document; see
  "Critical Finding" and "Validation Architecture" below.
- **Edge cases for the `fr` conversion:** `colwidth` missing / zero / not summing → fall back to equal
  `1fr` per column. Interaction with the existing LEN-01 `block(width: …)[#table(…)]` wrapper (from an
  explicit `:width:` on the table) — the `fr` columns fill whatever block width wraps them, so the two
  compose; verify with a real compile. `table.header(…)` cell structure is unchanged by the columns
  change.

### Deferred Ideas (OUT OF SCOPE)

- **Honoring `.. tabularcolumns::`** — rejected for v0.6.1 (D-03); the HTML fidelity authority ignores it.
- **`measure`-at-compile-time conditional column sizing** — rejected for D-02; uniform `fr` chosen instead.
- **F6 (medium): long inline `literal` runs overflow/clip the right margin** (`usage/domains/cpp` p.85) —
  kinship to F12 (both right-edge overflow) but a different node kind (inline `literal` run in prose, not
  a table), medium severity — NOT part of FID-01a. Next-milestone candidate.
- **The 13 medium/low audit findings (F1–F11, F13–F15)** — recorded in `17-AUDIT-CATALOGUE.md`, pointed
  to from REQUIREMENTS.md "Future Requirements" (D-11). Not v0.6.1 work.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FID-01a | `table`/`tgroup` wide-table rendering: inter-column glyph collision + rightmost-column right-margin clip, for any table whose cell content exceeds the text-block width. Repro: `extdev/deprecated` "Deprecated APIs" grid table. | Root cause confirmed (integer `columns:` → all-`auto` tracks, verified via official Typst grid docs + empirical compile). Fix design verified empirically in two parts: (1) `fr`-column conversion from `colwidth` — necessary but **not sufficient alone**; (2) zero-width-space injection in `visit_literal` for in-table literal content — the missing piece that makes the real corpus repro actually stop colliding. See "Critical Finding" below. Fixture design (real-compile, collision-absence PDF-text assertion) validated to fail red on the unfixed translator and pass green after both fix parts land. |
| GATE-03 | Full corpus still compiles fatal-free through `typstpdf` (GATE-02 non-regression) and `unknown_visit` catalogue stays empty of `todo_node`/`manpage`. | Mechanical: `tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error` already implements this exact check (green as of Phase 17's fresh run) — Phase 18 just needs to re-run it after the FID-01a fix lands and confirm it stays green, since the fr-column change touches every table in the ~684-page corpus. |
</phase_requirements>

## Summary

FID-01a's root cause is that `depart_table` emits `columns: <integer>` — per Typst's own grid-layout
documentation, an integer `columns:` value creates that many `auto`-sized tracks, and `auto` tracks size
to their content's natural width without wrapping; when several `auto` tracks together demand more space
than the container has, Typst compresses their *boxes* to fit but the *text inside* still does not
wrap, so cell content visually overlaps its neighbors — exactly the audit's "inter-column glyph
collision" (`BuildEnvironmentanpp`) and "rightmost column clipped" symptoms. This was reproduced from
scratch in this session, both with a hand-built `.typ` file and (more importantly) with the ACTUAL
translator output from a synthetic Sphinx fixture shaped like `extdev/deprecated`'s grid table.

D-01/D-02's fix — replace `columns: <integer>` with `columns: (colwidth[0]fr, colwidth[1]fr, …)` sourced
from `nodes.colspec['colwidth']` — is structurally correct and was verified to compose correctly with the
LEN-01 `block(width: …)[#table(…)]` wrapper (`fr` resolves against whatever container width it is placed
in). It also correctly fixes every table whose cell content is ordinary wrappable prose (has spaces) —
verified empirically: a normal sentence in a narrow `fr` column wraps onto multiple lines exactly like
HTML would.

**Critical finding (the one thing the CONTEXT.md discretion note did not anticipate): `fr`-columns alone
do NOT fix FID-01a's actual catalogued repro.** The `extdev/deprecated` table's cell content is not
prose — it is `` `` inline-literal `` `` Python dotted paths (`sphinx.environment.BuildEnvironment.app`,
rendered by `visit_literal` as `raw("...")`) with **no whitespace at all**. Typst's paragraph line-breaker
only inserts a line break at a whitespace (or hyphenation) opportunity; a single unbroken token wider than
its `fr` share still overflows into the neighboring column, reproducing the exact same collision the audit
found — verified by hand-editing a real translator-emitted `.typ` file's `columns: 4` line to
`columns: (3fr, 1.5fr, 1.5fr, 4fr)` and recompiling: **the collision was unchanged, byte-for-byte
identical PDF text.** This is a known, documented Typst limitation (Typst forum thread ["How to wrap long
'unbreakable' text in a table cell?"](https://forum.typst.app/t/how-to-wrap-long-unbreakable-text-in-a-table-cell/1224),
[typst/typst#674](https://github.com/typst/typst/issues/674) "Break apart overlong words without
hyphenating"), not a translator bug per se — but it means FID-01a is not actually closed by D-01/D-02
alone. The forum-documented, community-standard workaround — inserting a zero-width space (U+200B,
Typst's `sym.zws`) after natural break characters inside the unbreakable token — was verified in this
session to fully resolve it: inserting U+200B after every `.` and `_` in `visit_literal`'s
`code_content` (gated on `self.in_table`, so only table-cell literals are touched, not prose elsewhere)
made the identical repro wrap cleanly with zero collision.

**Primary recommendation:** Implement D-01/D-02 (colwidth → `fr` columns) exactly as locked, AND add a
second, narrowly-scoped change — zero-width-space injection at natural break points (`.`/`_`) for
`raw()` literal content emitted while `self.in_table` is true — as part of the SAME FID-01a fix plan (not
a separate requirement; it is the other half of the same root cause: "wide table content has no
column-fitting/wrapping strategy"). Prove both together with one real-compile PDF-text-extraction
fixture that asserts the ABSENCE of the exact glyph-collision signature the audit catalogued (a
concatenated-substring check, matching this codebase's existing DESC-02 idiom), not a `.typ`-string
comparison and not a bare "did it compile" check.

## Architectural Responsibility Map

typsphinx is a single-process Sphinx-extension pipeline, not a multi-tier web app; "tiers" here map to
pipeline stages instead of browser/server/API/DB.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Column-width capture (docutils `colspec['colwidth']`) | Translator (`visit_colspec`/`visit_tgroup`) | — | docutils already computes per-column relative widths for every table type (`.. table::`, `.. csv-table::`, `.. list-table::`); the translator's job is to capture, not recompute, this. |
| Column-width emission (`columns: (Nfr, …)`) | Translator (`depart_table`) | Typst compiler (layout) | The translator emits the Typst source; Typst's own grid-layout engine performs the actual proportional division at compile time. |
| Long-unbroken-token wrapping (`raw()` literal content) | Translator (`visit_literal`) | Typst compiler (line-breaker) | The translator must insert break opportunities (ZWSP) into the string it emits; Typst's Unicode-UAX#14 line-breaker then honors them at compile time — this is a data-shaping responsibility of the emitter, not something Typst can infer. |
| Corpus-wide non-regression proof (GATE-03) | Test suite (`tests/test_corpus_gate.py`) | — | Mechanical re-run of existing machinery; no new architecture. |
| Per-fix real-compile proof (GATE-01 pattern) | Test suite (new `tests/fixtures/*_render_gate/` + `tests/test_pdf_render_gate.py`) | pypdf (text extraction) | Established pattern in this codebase; the real-compile + real-extraction step is what makes the proof trustworthy for a *silent* bug. |

## Standard Stack

No new runtime or dev dependencies. This phase uses only what is already declared in `pyproject.toml`
and already used by every prior GATE-01 fixture in this codebase.

### Core (already present, no version change)

| Library | Version (installed, verified this session) | Purpose | Why Standard |
|---------|------|---------|--------------|
| `typst` (typst-py) | 0.15.0 (pinned `>=0.15.0,<0.16` in `pyproject.toml`) | Real PDF compile in tests (`typst.compile()`) | Already the project's only PDF-compile backend; no CLI Typst install needed. |
| `pypdf` | 6.14.2 (pinned `>=6.14,<7`) | Post-compile PDF text extraction for the regression assertion | Already used by every GATE-01 fixture in `tests/test_pdf_render_gate.py`. |
| `docutils` | 0.22.4 (pinned `>=0.21,<0.23`) | Source of `nodes.colspec['colwidth']` | Already the parser backend; `colwidth` is a stable docutils doctree attribute, verified present (non-`None`, non-zero) for `.. table::`, `.. csv-table::`, and `.. list-table::` (with or without an explicit `:widths:` option) in this session's direct docutils-parser tests. |
| `sphinx` | 9.1.0 (pinned `>=9.1,<10`) | Build pipeline | Unchanged. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| ZWSP (U+200B) injection at `.`/`_` boundaries | `#show regex(...): it => it.text.codepoints().join(sym.zws)` Typst-side show-rule (the exact pattern the Typst forum thread recommends) | Rejected: the translator already builds the exact string that goes into `raw("...")`; injecting the ZWSP characters in Python before escaping is strictly simpler than emitting a Typst show-rule that would need to run correctly on every table's raw-literal cells project-wide. Same visual result, fewer moving parts, and keeps the "no new `@preview` package, no template change" milestone invariant intact. |
| `set text(hyphenate: true)` | Typst's built-in hyphenation | Rejected: hyphenation uses a language dictionary (English words); it does **not** find break points inside a Python dotted identifier like `sphinx.environment.BuildEnvironment` — confirmed by the Typst forum thread itself recommending ZWSP specifically *because* hyphenation doesn't solve the unbreakable-token case. |
| Compile-time `measure()` + `panic()` overflow assertion embedded in the fixture's own Typst source | A geometric "does the frame width exceed the given width" check | Rejected as the *fixture's proof mechanism*: verified empirically that `measure(content, width: avail)` always returns a frame of exactly `avail` width regardless of whether content inside genuinely overflowed that box — a `fr`-column table and a broken `auto`-column table both measure identically. This dead end is documented in "Common Pitfalls" below so no one re-discovers it. |

## Package Legitimacy Audit

**Not applicable — this phase installs no new packages.** All libraries used (`typst`, `pypdf`,
`docutils`, `sphinx`) are pre-existing pinned dependencies already declared in `pyproject.toml` before
this phase began; the milestone invariant ("zero new runtime dependencies, no `@preview` version bump")
holds by construction. No `package-legitimacy` check is needed.

## Architecture Patterns

### System Architecture Diagram

```
docutils doctree (nodes.table > nodes.tgroup > [colspec]* > thead/tbody > row > entry > ...)
        │
        ▼
┌───────────────────────────────────────────────────────────────────┐
│ TypstTranslator (typsphinx/translator.py)                         │
│                                                                     │
│  visit_table        → self.in_table=True, self.table_cells=[],    │
│                        self.table_colwidths=[]  (NEW state)       │
│  visit_tgroup       → self.table_colcount = node.get("cols")      │
│  visit_colspec      → self.table_colwidths.append(colwidth)  ─────┼─── D-01: capture instead of SkipNode
│  visit_entry/visit_literal → cell content buffered into           │
│                        self.table_cells; visit_literal injects    │
│                        ZWSP at "." / "_" when self.in_table  ─────┼─── the missing piece (this research)
│  depart_table       → builds "columns: (W0fr, W1fr, …)" from      │
│                        self.table_colwidths (fallback: equal 1fr  │
│                        each if missing/zero/length-mismatch) ─────┼─── D-01/D-02: emission site
│                        emits table(columns: ..., table.header(…), │
│                        <body cells>) [wrapped in block(width:…)   │
│                        if the LEN-01 :width: wrapper applies]     │
└───────────────────────────────────────────────────────────────────┘
        │  .typ source string
        ▼
┌───────────────────────────────────────────────────────────────────┐
│ Typst compiler (typst-py, real compile — GATE-01 pattern)         │
│  grid/table layout: fr tracks divide remaining container width;   │
│  paragraph line-breaker wraps at whitespace / ZWSP break points   │
└───────────────────────────────────────────────────────────────────┘
        │  PDF bytes
        ▼
┌───────────────────────────────────────────────────────────────────┐
│ pypdf text extraction (regression-fixture assertion layer)        │
│  assert: no concatenated-cell-boundary substring (collision proof)│
│  assert: no LEAK_SIGNATURES; valid %PDF magic; page(s) produced   │
└───────────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure

No new source directories — this is a translator-internal change plus one new test fixture:

```
typsphinx/
├── translator.py            # depart_table, visit_colspec, visit_tgroup, visit_table, visit_literal edited
tests/
├── test_pdf_render_gate.py                       # extend with a new TestWideTableRenderGate class
├── test_table_in_list_item_render_gate.py         # EXISTING assertion needs updating (see Pitfall below)
├── test_translator.py                             # test_table_conversion already anticipates "columns: (1fr, 1fr)"
├── test_corpus_gate.py                            # unchanged; GATE-03 = re-run this
└── fixtures/
    └── wide_table_render_gate/                    # NEW fixture (conf.py + index.rst)
```

### Pattern 1: `colwidth` capture at `visit_colspec` (replaces `raise SkipNode`)

**What:** Accumulate each column's `colwidth` into a list on the translator instance instead of
discarding it.
**When to use:** Every table, unconditionally (D-02).
**Verified fact:** `colwidth` is populated by docutils for every table-directive type tested this
session, with or without an explicit `:widths:` option:

| Source construct | Observed `colwidth` values |
|---|---|
| `.. list-table:: :widths: 40, 10, 10, 40` (4 cols) | `[40, 10, 10, 40]` — exact author-given ratios |
| `.. list-table::` with NO `:widths:` (3 cols) | `[33, 33, 33]` (docutils' equal-share default) |
| `.. csv-table::` with NO `:widths:` (2 cols) | `[50, 50]` |
| `.. table::` (grid table, ASCII-art column widths, no `:widths:`) | `[5, 25]` — derived from the source markup's own character-column widths, giving a natural relative weight |
| Hand-built doctree in `tests/test_translator.py::test_table_conversion` (`colspec(colwidth=1)` × 2) | `[1, 1]` |

```python
# Source: this session's direct docutils.parsers.rst.Parser test (verified, not from docs)
def visit_colspec(self, node: nodes.colspec) -> None:
    """Capture colwidth instead of discarding it (D-01)."""
    colwidth = node.get("colwidth")
    self.table_colwidths.append(colwidth if colwidth else None)
    raise nodes.SkipNode
```

### Pattern 2: `fr`-column emission at `depart_table` (D-01/D-02)

```python
# Source: this session's empirical verification (typst.compile() + pypdf round-trip)
def _build_columns_fr_arg(self) -> str:
    """Build the Typst columns: (...) argument from captured colwidth values.

    Falls back to equal 1fr-per-column when colwidth data is missing, all
    zero, or its length does not match table_colcount (defensive path --
    not observed in any real docutils output tested this session, but
    nodes.colspec.colwidth is technically Optional per the docutils API).
    """
    widths = self.table_colwidths
    n = self.table_colcount
    valid = (
        len(widths) == n
        and n > 0
        and all(w and w > 0 for w in widths)
    )
    if not valid:
        widths = [1] * n
    return "(" + ", ".join(f"{w}fr" for w in widths) + ")"

# depart_table, replacing:
#     f"table(\n  columns: {self.table_colcount},\n"
# with:
#     f"table(\n  columns: {self._build_columns_fr_arg()},\n"
```

Verified: for `colwidth=[1, 1]` this emits `columns: (1fr, 1fr)` — this is EXACTLY the string
`tests/test_translator.py::test_table_conversion` already accepts (line 157: `assert "columns: 2" in
output or "columns: (1fr, 1fr)" in output`) — that test was evidently already written anticipating this
exact fix shape; no changes needed to it. Verified: `fr` columns correctly resolve against a `block(width:
50%)[...]` wrapper (LEN-01 composition) — a 1fr/1fr table inside a 50%-width block renders at exactly
half the width of the same table at top level, with the 1:1 proportion preserved (confirmed by real
compile + rasterized visual comparison this session).

### Pattern 3: ZWSP injection for in-table literal content (the missing piece — new pattern this research surfaces)

**What:** Insert a zero-width space (U+200B) after every `.` and `_` character in `visit_literal`'s
`code_content`, but ONLY when `self.in_table` is true (so `F6`'s out-of-scope prose-context inline-literal
overflow is untouched, and literal code elsewhere in the document — e.g. inline code in a paragraph, code
blocks — is unaffected).
**When to use:** Exactly the FID-01a repro shape: `raw()`-rendered inline-literal table-cell content with
long dotted/underscored identifiers and no natural whitespace break point.
**Verified, cited approach:** matches the Typst-community-documented workaround for "wrap long unbreakable
text" ([Typst forum](https://forum.typst.app/t/how-to-wrap-long-unbreakable-text-in-a-table-cell/1224);
tracked upstream as [typst/typst#674](https://github.com/typst/typst/issues/674), still open — this is a
known Typst limitation, not something a future Typst release is guaranteed to fix, so the workaround is
durable, not a stopgap).

```python
# Source: this session's empirical verification (before/after real-compile,
# pypdf-extracted-text comparison). Inserted BEFORE escape_typst_string() --
# U+200B is not one of the characters that function escapes, so ordering
# does not matter for correctness, but inserting first keeps the "raw
# content shaping" and "string-literal escaping" concerns separate.
def visit_literal(self, node: nodes.literal) -> None:
    ...
    code_content = node.astext()
    if self.in_table:
        # Zero-width space (U+200B) at natural break points so Typst's
        # line-breaker can wrap long unbroken dotted/underscored
        # identifiers inside a narrow fr-column table cell -- fr columns
        # alone do not wrap a single unbroken token (verified empirically,
        # see 18-RESEARCH.md "Critical Finding").
        zwsp = chr(0x200B)  # zero-width space
        code_content = code_content.replace(".", "." + zwsp).replace("_", "_" + zwsp)
    escaped_code = escape_typst_string(code_content)
    ...
```

**Verified end-to-end on real translator output:** a synthetic Sphinx fixture shaped exactly like
`extdev/deprecated` (a `.. list-table:: :widths: 30 15 15 40` with long unbroken cell content) compiled
through the REAL `sphinx-build -b typstpdf` → `typst.compile()` pipeline:
- **Before either fix** (current `columns: 4`, no ZWSP): `pypdf` extraction shows
  `"...anpp_something_long_target_path8.0 9.0 sphinx.util.format_exception..."` — the exact collision
  signature the audit catalogued, with zero separator between the Target cell and the Deprecated cell.
- **`fr`-columns alone** (hand-patched `columns: (3fr, 1.5fr, 1.5fr, 4fr)`, no ZWSP): **identical
  collision, byte-for-byte** — proves D-01/D-02 alone does not close FID-01a for this repro shape.
- **`fr`-columns + ZWSP together**: clean wrap, `"sphinx.environment.\nBuildEnvironment.anpp_\nsomething_long_target_\npath"` on separate visual lines within its own column, `"8.0 9.0"` in their own columns, `"sphinx.util.format_exception_cut_\nfrom_traceback_extremely_long_alt_\nname"` wrapped in its own column — zero cross-column collision. Rasterized to PNG and visually confirmed.

### Anti-Patterns to Avoid

- **Relying on `measure()`'s returned frame width as an overflow oracle.** `measure(content, width: X)`
  always reports a frame of size `X` regardless of whether the CONTENT INSIDE that frame actually
  overflowed its own sub-boxes (columns) — verified empirically this session (both a broken `auto`-column
  table and a correct `fr`-column table measured identically at exactly the given width). This looked
  like an elegant "panic on overflow" test design at first but is a dead end; do not spend planner/executor
  time on it.
- **Trusting "compile succeeded" alone as the regression proof.** FID-01a is silent by definition (no
  warning, no error, `returncode == 0` both before and after any fix) — this was the CONTEXT.md-flagged
  risk and it is real: a naive "does `typst.compile()` succeed" fixture is GREEN on the current, buggy
  translator RIGHT NOW. The fixture must assert on extracted PDF text content, not merely on successful
  compilation.
- **Applying the ZWSP injection outside `self.in_table`.** Would silently change every inline-literal's
  rendered text elsewhere in the document (code samples, cross-references, etc.) with invisible-but-real
  U+200B characters that are out of this phase's scope (F6 is explicitly deferred) and could introduce
  unintended copy-paste artifacts in unrelated PDF pages across the 684-page corpus.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Proportional column-width computation from source hints | A custom text-width estimation heuristic (e.g. counting characters per cell to guess a "fair" column width) | `nodes.colspec['colwidth']`, already computed by docutils from the directive's `:widths:` option or the source markup's own ASCII-art column widths | docutils already solves this exactly, for all three table-directive types, verified this session; re-deriving it in the translator would diverge from the HTML builder's own source of truth (same `colwidth` field HTML's `<col style="width:X%">` uses) and add a maintenance burden for zero benefit. |
| Long-unbroken-token line wrapping | A custom paragraph-reflow / character-wrapping algorithm in Python before emitting Typst source | Typst's own Unicode-UAX#14 line-breaker, fed break opportunities via ZWSP at `.`/`_` boundaries | Typst already implements correct, locale-aware line breaking; the translator's only job is to supply the missing break-opportunity signal at points Python identifiers naturally suggest (`.`, `_`), exactly as the Typst community documents doing for this exact scenario. |
| Regression-proof of a silent visual bug | A visual-diff / screenshot-comparison harness | Real `sphinx-build` → `typst.compile()` → `pypdf.extract_text()` → substring-collision assertion (the established GATE-01/DESC-02 idiom already used ~10 times in this codebase's `tests/test_pdf_render_gate.py`) | This codebase already has a proven, fast, CI-friendly pattern for exactly this class of proof (multi-line-separation assertions via "concatenated sentinel not in full_text" checks); no new tooling (image diffing, rasterization) is needed for the automated test suite — rasterization is a research/debugging aid only, used in THIS session via `nix-shell -p poppler-utils` (see memory `nixos-sandbox-test-env`), not a dependency of the fixture itself. |

**Key insight:** Both halves of the actual fix (fr-columns AND ZWSP injection) are "let the existing,
already-correct engine (docutils for widths, Typst for line-breaking) do the work; the translator's job is
only to stop throwing away information (`colwidth`) and to supply a missing signal (break opportunities)."
Neither half requires new hand-rolled layout logic.

## Common Pitfalls

### Pitfall 1: Believing D-01/D-02 (fr-columns) alone closes FID-01a

**What goes wrong:** A fix plan implements only the `columns: (Nfr, …)` emission, writes a fixture using
the audit's exact `extdev/deprecated`-style long-dotted-literal content, and the fixture's collision
assertion STILL FAILS after the "fix" — because it genuinely does, verified empirically this session.
**Why it happens:** `fr` columns correctly proportion the CONTAINER width, but Typst's paragraph
line-breaker only wraps at whitespace/hyphenation opportunities; a single unbroken token (a dotted Python
path with no spaces, rendered via `raw()`) has none, so it overflows its column regardless of how narrow
or wide that column's `fr` share is.
**How to avoid:** Implement Pattern 3 (ZWSP injection in `visit_literal`, gated on `self.in_table`) as
part of the SAME fix plan, not a follow-up. Both changes together are "the FID-01a fix" — do not split
them into separate plans/requirements; they address the one root cause the audit described
("no column-fitting/wrapping strategy for wide tables") from its two necessary angles (column
proportions + token-level wrapping).
**Warning signs:** A fixture's collision-absence assertion still fails after implementing only the
`columns:` change; the .typ diff shows `columns: (Nfr, …)` correctly but the PDF-extracted text still
shows a merged substring across a cell boundary.

### Pitfall 2: Existing hardcoded test assertions on `columns: <int>` will break

**What goes wrong:** `tests/test_table_in_list_item_render_gate.py` line 174 asserts the literal string
`"  columns: 2,\n" in typ_text` for BOTH tables in its fixture. After the D-01 fix lands, both tables in
that fixture (2-column `list-table`, no explicit `:widths:`) will emit `columns: (50fr, 50fr),` instead
(verified: parsing that exact fixture's `index.rst` through `docutils.parsers.rst.Parser` in this session
gives `colwidth = [50, 50]` for both tables). This test WILL fail after the fix lands unless updated.
**Why it happens:** The test was written when D-01 didn't exist yet; it was pinning the pre-fix emission
shape as a byte-exact regression guard for an unrelated bug (the table-in-list-item separator fix,
GATE-02/Phase 15), and incidentally hardcoded the column syntax too.
**How to avoid:** The FID-01a fix plan MUST update this assertion (line 174, and the neighboring
byte-exact block around lines 171-178 that also embeds `"  columns: 2,\n"`) to the new expected string
`"  columns: (50fr, 50fr),\n"` for BOTH the list-item-nested table and the top-level table in that
fixture — confirmed identical expected value for both, since neither has an explicit `:widths:` option.
**Warning signs:** `tests/test_table_in_list_item_render_gate.py` fails immediately after the `depart_table`
change lands, even though its actual purpose (list-item separator behavior) is unaffected.

### Pitfall 3: `tests/test_translator.py::test_table_conversion` already anticipates the fix — do not "fix" it unnecessarily

**What goes wrong:** A plan might "helpfully" tighten line 157's `assert "columns: 2" in output or
"columns: (1fr, 1fr)" in output` down to just the new form, assuming the `or` was leftover cruft.
**Why it happens:** The `or` branch looks unusual at first glance.
**How to avoid:** Leave it as-is, or simplify to just `assert "columns: (1fr, 1fr)" in output` once the
fix lands (either is fine) — but do NOT assume this test needs new content; it was clearly already written
in anticipation of exactly this fix shape (the hand-built doctree in that test uses `colspec(colwidth=1)`
× 2, which is the precise input that produces `(1fr, 1fr)`). No new test coverage is needed here beyond
optionally tightening the assertion.

### Pitfall 4: `measure()`-based overflow detection looks elegant but is a dead end

**What goes wrong:** Time spent designing a Typst-side `context { let sz = measure(...); assert(sz.width
<= avail) }` "hard panic on overflow" fixture mechanism, expecting it to fail red pre-fix and pass green
post-fix.
**Why it happens:** It is a natural first idea for "detect overflow via computation, not string
comparison" (which is exactly what SC#1 asks for).
**How to avoid:** Don't pursue it — verified this session that `measure(content, width: X)` returns a
frame of size `X` unconditionally, whether or not the table's own internal columns overflowed within that
frame. It cannot distinguish broken from fixed. Use the PDF-text-extraction collision-absence assertion
instead (Pattern 3 / Validation Architecture below), which WAS verified to distinguish them correctly.

### Pitfall 5: Header-row cells can also collide in extreme cases — cosmetic, not a new requirement

**What was observed:** In a narrow synthetic test (1fr/1fr columns for a 4-column table where 2 of the
4 columns are very narrow), the header words "Deprecated"/"Removed" (single words, no internal `.`/`_`)
visually touched at their column boundary. This is a DIFFERENT, narrower case than FID-01a's cataloged
finding (which is about body-cell literal content) and is inherent to any column-width system when a
single unbreakable word is wider than its allotted column — the same thing would happen in HTML/CSS
without `overflow-wrap: break-word`. It is not observed in the real corpus's `extdev/deprecated` header
row (whose header words `Target`/`Deprecated`/`Removed`/`Alternatives` fit their `40/10/10/40` colwidth
shares at normal page width) but is worth a one-line awareness note for the planner: header cells are
plain `text()`, not `raw()`, so the ZWSP fix (Pattern 3, scoped to `visit_literal`) does not touch them —
if a future audit finds a genuine header-collision instance, it is a distinct, narrower fix (word-level
ZWSP for plain Text nodes too), out of scope here since FID-01a's evidence is body-cell literal content.

## Code Examples

### Real-compile fixture pattern (verified to distinguish broken vs. fixed translator)

```python
# Source: this session's empirical verification. Mirrors the existing
# DESC-02 concatenated-sentinel idiom in tests/test_pdf_render_gate.py
# (see TestDescSignatureRenderGate.test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline,
# the "concatenated = DESC_LINE_ONE_SENTINEL + DESC_LINE_TWO_SENTINEL; assert
# concatenated not in full_text" pattern) applied to the table-collision case.

WIDE_TABLE_TARGET_SENTINEL = "WIDETABLETARGETSENTINELQ7X9"
WIDE_TABLE_DEPRECATED_SENTINEL = "8.7"  # a value unlikely to appear elsewhere
WIDE_TABLE_ALT_SENTINEL = "WIDETABLEALTSENTINELK3M2"

def test_wide_table_pdf_has_no_column_collision(
    self, wide_table_render_gate_dir, temp_build_dir
):
    """
    Real-compile acceptance gate for FID-01a. Fails RED on the pre-fix
    translator (columns: <int>, no ZWSP): the Target cell's sentinel and
    the Deprecated cell's sentinel concatenate with no separator in the
    extracted PDF text, reproducing the audit's F12 collision signature.
    Passes GREEN once BOTH the colwidth->fr conversion (depart_table) AND
    the ZWSP break-point injection (visit_literal, in_table-gated) land --
    verified empirically neither change alone is sufficient (18-RESEARCH.md
    "Critical Finding").
    """
    result = _run_sphinx_build_typstpdf(wide_table_render_gate_dir, temp_build_dir)
    assert result.returncode == 0, (...)

    pdf_output = temp_build_dir / "index.pdf"
    # Uncaught typst.compile() call -- any invalid-syntax regression in the
    # fr-columns or ZWSP emission aborts the whole compile here (GATE-01).
    typst.compile(str(temp_build_dir / "index.typ"), output=str(pdf_output))

    reader = pypdf.PdfReader(str(pdf_output))
    full_text = "\n".join(page.extract_text() for page in reader.pages)

    # The collision-absence proof (the crux of this test): before the fix,
    # these two cells' content is adjacent with NO separator in the
    # extracted text -- verified this session on real translator output.
    collided = WIDE_TABLE_TARGET_SENTINEL + WIDE_TABLE_DEPRECATED_SENTINEL
    assert collided not in full_text, (
        "Target/Deprecated cell content concatenated with no separator -- "
        "FID-01a column-collision regression (fr-columns and/or ZWSP "
        "break-point injection missing or broken)"
    )
    assert WIDE_TABLE_TARGET_SENTINEL in full_text
    assert WIDE_TABLE_ALT_SENTINEL in full_text

    # Structural sanity check, IN ADDITION to (never INSTEAD of, per SC#1)
    # the extraction-based proof above.
    typ_text = (temp_build_dir / "index.typ").read_text()
    assert "columns: (" in typ_text and "fr" in typ_text
```

### Recommended fixture `index.rst` content (mirrors the actual `extdev/deprecated` repro shape)

```rst
.. list-table:: Wide Table Render Gate
   :header-rows: 1
   :widths: 40, 10, 10, 40

   * - Target
     - Deprecated
     - Removed
     - Alternatives
   * - ``sphinx.environment.BuildEnvironment.WIDETABLETARGETSENTINELQ7X9_long_path``
     - 8.7
     - 11.0
     - ``sphinx.util.WIDETABLEALTSENTINELK3M2_alternative_function_name``
```

Use inline double-backtick literal roles (not plain text) — this is what makes the fixture reproduce the
REAL bug shape (`raw()` emission), not just the `fr`-columns-only case that a plain-text fixture would
falsely appear to "fix."

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `columns: <int>` (all-`auto` tracks, no wrap) | `columns: (Nfr, Mfr, …)` from `colwidth` + ZWSP-injected `raw()` literals | This phase (v0.6.1, Phase 18) | Wide tables wrap to fit the text block instead of colliding/clipping, matching the HTML fidelity authority; narrow tables now stretch to full text-block width (accepted cosmetic cost per D-02). |

**Deprecated/outdated:** N/A — no prior FID-01a fix existed; this is the first attempt.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The real `extdev/deprecated` corpus content's collision behavior, when run through the ACTUAL fixed translator (not this session's hand-patched `.typ` proxy), will behave identically to the synthetic fixture verified in this session. | Critical Finding / Validation Architecture | Low risk — the synthetic fixture used real `sphinx-build` output structurally identical to the translator's real emission (`par({raw("...")})` cell content, `table(columns: N, table.header(...), ...)` shape); only the specific dotted-path strings differ. GATE-03 (re-running the full corpus gate after the fix) is the final backstop that would catch any divergence. |
| A2 | No OTHER corpus table (beyond `extdev/deprecated`) contains inline-literal cell content long/unbroken enough to still collide after both fixes land. | Validation Architecture / GATE-03 | Medium risk — the corpus has 684 pages and many tables; GATE-03's full-corpus re-run is fatal-error-only (won't visually catch a NEW collision instance, only a compile-breaking regression). Mitigation: this is inherent to D-02's "apply uniformly, no per-table judgment" decision, already accepted by the user; a residual collision on some OTHER table is a new AUD-01-style finding for a future audit pass, not a Phase 18 regression, since FID-01a's locked scope is the `extdev/deprecated` root cause specifically. |

## Open Questions

1. **Should the ZWSP-in-`visit_literal` change also apply to `_` inside numbers/versions (e.g. `1_000`) or other non-identifier contexts inside a table?**
   - What we know: the audit's repro content is exclusively Python dotted/underscored identifiers.
   - What's unclear: whether any corpus table cell contains a different long-unbroken-token shape (e.g. a long URL, a long hex hash) that also needs a break point but has no `.`/`_` to hook.
   - Recommendation: ship the `.`/`_` version first (matches 100% of the catalogued FID-01a evidence); if GATE-03's full-corpus re-run surfaces a NEW residual collision on a different table, that is out of this phase's locked scope (it would be F12-adjacent but not the catalogued repro) and should be logged as a new candidate finding for a future audit pass, not silently expanded into this phase.

2. **Exact Nfr weight normalization: use raw `colwidth` ints directly, or reduce to a simpler ratio?**
   - What we know: using raw `colwidth` ints directly (e.g. `(40fr, 10fr, 10fr, 40fr)`) is confirmed correct by Typst semantics (fr weights don't need to sum to any particular total) and matches `tests/test_translator.py::test_table_conversion`'s already-anticipated `(1fr, 1fr)` expectation for `colwidth=[1,1]`.
   - What's unclear: nothing — this is settled; documenting only to make explicit that NO normalization/reduction step is needed (simpler implementation than it might first appear).
   - Recommendation: use raw `colwidth` values directly as the `fr` weights, no GCD-reduction or percentage conversion.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `typst` (typst-py) | Real-compile fixtures (GATE-01), GATE-03 corpus gate | ✓ | 0.15.0 | — |
| `pypdf` | PDF text-extraction assertions | ✓ | 6.14.2 | — |
| Corpus cache (`~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc`) | GATE-03 full-corpus re-run | ✓ (confirmed present this session) | tag `v9.1.0` | Re-clone via `tests/test_corpus_gate.py::get_or_clone_corpus` if the cache was cleared (needs network to `github.com/sphinx-doc/sphinx.git`). |
| `poppler-utils` (`pdftoppm`) | Optional visual-raster debugging aid used DURING this research session, NOT a test/fixture dependency | Available via `nix-shell -p poppler-utils` (not on default PATH — see memory `nixos-sandbox-test-env`) | 26.06.0 | Not needed for the automated test suite; `pypdf` text extraction is sufficient for the fixture's assertions. Only useful if a human wants to visually re-inspect a fixture's rendered PDF during implementation/debugging. |
| Full local (non-sandboxed) dev environment | GATE-03 full-corpus compile (~684-page real PDF build) | Required — NixOS sandbox environment cannot run these real corpus builds (~45 integration tests fail environmentally, per project memory `nixos-sandbox-test-env`) | — | None; must run in the full local env, as Phases 15 and 17 did. |

**Missing dependencies with no fallback:** none.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml`), plus `typst`/`pypdf` real-compile round-trip |
| Config file | `pyproject.toml` (existing `[tool.pytest.ini_options]`) |
| Quick run command | `pytest tests/test_pdf_render_gate.py -k WideTable -q` (new fixture, once added) |
| Full suite command | `pytest -q` (fast suite); `pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q` (GATE-03, real corpus, minutes-scale, needs full local env) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FID-01a | `columns: (Nfr, …)` emitted from `colwidth`; `visit_colspec` no longer discards width data | unit | `pytest tests/test_translator.py::test_table_conversion -x` | ✅ (already anticipates the fix; may need trivial tightening, see Pitfall 3) |
| FID-01a | Real-compile: no glyph collision across a table-cell boundary for long-unbroken-literal content, wide-table-shaped fixture matching the `extdev/deprecated` repro | integration (real compile + real PDF text extraction) | `pytest tests/test_pdf_render_gate.py -k WideTable -x` | ❌ Wave 0 — new fixture `tests/fixtures/wide_table_render_gate/` + new test class needed |
| FID-01a (regression) | `table_in_list_item_render_gate` fixture's byte-exact `columns:` assertions updated to the new `(50fr, 50fr)` shape for both tables in that fixture | fast/offline regression | `pytest tests/test_table_in_list_item_render_gate.py -x` | ✅ file exists, ❌ assertion content needs updating (see Pitfall 2) |
| GATE-03 | Full corpus still compiles fatal-free; `unknown_visit` catalogue empty of `todo_node`/`manpage` | slow/integration (real corpus, network + full local env) | `pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q` | ✅ already exists and already implements the exact GATE-03 assertion (mechanical re-run, D-04) |

### Sampling Rate

- **Per task commit:** `pytest tests/test_translator.py tests/test_pdf_render_gate.py tests/test_table_in_list_item_render_gate.py -q` (fast, offline, seconds-scale)
- **Per wave merge:** full fast suite (`pytest -q`, excludes `-m slow`)
- **Phase gate:** `pytest -m slow -q` (includes `test_corpus_gate.py`'s real ~684-page corpus build) MUST be green before `/gsd-verify-work` — this IS GATE-03, run once at the end after the FID-01a fix lands, in the full local (non-sandboxed) environment.

### Wave 0 Gaps

- [ ] `tests/fixtures/wide_table_render_gate/conf.py` + `index.rst` — the new FID-01a real-compile fixture (mirrors `table_width_render_gate`'s structure).
- [ ] A new test class in `tests/test_pdf_render_gate.py` (e.g. `TestWideTableRenderGate`) implementing the collision-absence assertion pattern shown in "Code Examples" above.
- [ ] Framework install: none — `typst`/`pypdf` already installed and pinned.

## Security Domain

`security_enforcement` is enabled in `.planning/config.json` (ASVS level 1, block on "high"). This phase
has no new external-input, authentication, session, or cryptography surface — it changes how a
already-parsed docutils doctree's existing `colwidth` attribute is emitted as Typst source, and reuses the
existing `escape_typst_string` string-literal escaping helper unchanged for the ZWSP-augmented content
(U+200B is not a character that helper treats specially; injecting it before escaping does not bypass or
weaken the existing escaping). No new ASVS category becomes applicable.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | N/A — no auth surface anywhere in typsphinx. |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | Already covered, unchanged | `escape_typst_string` (existing helper, reused as-is) continues to be the single sanitization point for all node-derived text reaching a Typst string literal, including the new ZWSP-augmented `code_content`. |
| V6 Cryptography | No | N/A |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Typst source-injection via unescaped node text (pre-existing class of bug, not introduced by this phase) | Tampering | `escape_typst_string` (existing, unchanged) — verified the ZWSP injection happens on the RAW content BEFORE this escaping step, so no new unescaped-text path is introduced. |

## Sources

### Primary (HIGH confidence — empirically verified in this session via `typst.compile()` + `pypdf` + direct `docutils.parsers.rst.Parser` inspection)

- Direct local verification: `depart_table`/`visit_colspec`/`visit_tgroup`/`visit_table`/`visit_literal`/`_format_table_cell` read from `typsphinx/translator.py` (this repo, current `main`, commit `840bed9`).
- Direct local verification: `nodes.colspec['colwidth']` values for `.. table::`, `.. csv-table::`, `.. list-table::` (with and without `:widths:`), via `docutils.parsers.rst.Parser` (docutils 0.22.4, installed).
- Direct local verification: real `sphinx-build -b typst` / `-b typstpdf` on a synthetic fixture shaped like `extdev/deprecated`, hand-patched `.typ` before/after comparisons, and `pypdf` text extraction — confirms the collision signature, confirms `fr`-columns-alone is insufficient, confirms `fr` + ZWSP together resolves it, confirms `fr` composes correctly with the LEN-01 `block(width: …)` wrapper.
- Direct local verification: `measure(content, width: X)` always returns frame width `X` regardless of internal overflow (dead end, documented as Pitfall 4).
- `tests/test_pdf_render_gate.py`, `tests/test_table_in_list_item_render_gate.py`, `tests/test_translator.py`, `tests/test_corpus_gate.py` — read directly (this repo).
- `.planning/phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md`, `17-CONTEXT.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `18-CONTEXT.md` — read directly (this repo).

### Secondary (MEDIUM confidence — official/community docs, corroborating this session's empirical findings)

- [Table — Typst Documentation](https://typst.app/docs/reference/model/table/) — `columns` parameter type (auto/int/relative/fraction/array).
- [Grid — Typst Documentation](https://typst.app/docs/reference/layout/grid/) — confirms an integer `columns:` value creates that many `auto`-sized tracks; confirms `auto` tracks "expand to fit their content, up to the available remaining space" and compete/compress when they exceed it (consistent with this session's observed collision behavior); confirms `fr` tracks divide remaining space by fraction, after other track types are sized.
- [How to wrap long "unbreakable" text in a table cell? — Typst Forum](https://forum.typst.app/t/how-to-wrap-long-unbreakable-text-in-a-table-cell/1224) — community-documented ZWSP (`sym.zws`) workaround, matching this session's independently-derived and empirically-verified fix.
- [typst/typst#674 — Break apart overlong words without hyphenating](https://github.com/typst/typst/issues/674) — confirms this is a known, currently-open upstream Typst limitation (hyphenation does not solve it), so the ZWSP workaround is durable rather than a stopgap for a soon-to-be-fixed compiler bug.

### Tertiary (LOW confidence)

- None — every claim in this document was either verified empirically this session or corroborated by official Typst documentation / the upstream Typst issue tracker.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies; existing pinned versions confirmed installed this session.
- Architecture / root cause / fix design: HIGH — verified empirically via real `typst.compile()` round-trips on both hand-built and actual-translator-emitted `.typ` source, not inferred.
- The "fr-alone insufficient, needs ZWSP" critical finding: HIGH — reproduced twice (isolated hand-built table AND real translator-shaped fixture), before/after compared, corroborated by an official Typst forum thread and an open upstream Typst issue.
- Pitfalls (existing test breakage, `measure()` dead end): HIGH — both confirmed by direct inspection/execution, not speculation.

**Research date:** 2026-07-19
**Valid until:** Tied to `typst-py` `0.15.x` and docutils `0.21`–`0.22.x` semantics; re-verify the `columns:`/`fr` grid-layout behavior claims if `typst` is ever bumped past the `<0.16` pin (would require a milestone-invariant exception) or docutils past `<0.23`.
