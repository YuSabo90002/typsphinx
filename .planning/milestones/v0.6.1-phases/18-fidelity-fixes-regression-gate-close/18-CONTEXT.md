# Phase 18: Fidelity Fixes + Regression-Gate Close - Context

**Gathered:** 2026-07-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix every **high-severity** issue in the Phase 17 AUD-01 catalogue — each fix proven by a real
`typst.compile()` regression fixture (GATE-01 pattern) that would fail without the fix — then close
milestone v0.6.1 by re-running the full-corpus gate (GATE-03).

The audit found **exactly one** high-severity root cause:

- **FID-01a (F12): wide-table overflow.** A multi-column `table`/`tgroup` whose total content width
  exceeds the text block renders with (a) inter-column glyph collision (long cell text bleeds into
  the adjacent column, e.g. `sphinx.environment.BuildEnvironment` merging with `anpp`) AND (b) the
  rightmost column clipping off the right page margin (e.g. `…format_exception_cut_f` cut mid-word).
  Systemic — recurs for any table too wide for the text block, corpus-wide. Repro anchor:
  `extdev/deprecated` "Deprecated APIs" grid table (compiled pp.239–249); contrast the narrow
  `extdev/appapi` transform-priority tables (pp.186–188) which render correctly.

**Root cause:** `depart_table` emits `columns: <integer>`, which makes every column Typst `auto`
(sized to content, no wrapping) → the table overflows the page instead of wrapping cell text to fit.
`visit_colspec` and `visit_tabular_col_spec` both `raise SkipNode`, discarding all column-width hints.

**Also in this phase (mechanical, not discussed):** GATE-03 close — after the fix, the full
Sphinx-`doc/` corpus still compiles fatal-free through `typstpdf` (GATE-02 non-regression: `index.pdf`
produced, 0 errors) AND the `unknown_visit` catalogue no longer contains `todo_node` or `manpage`
(confirming Phase 16's handlers eliminated both drops on the real corpus).

**Milestone invariant (unchanged):** zero new runtime dependencies, no `@preview` version bump — the
3-way version-sync surface (`writer.py` / `template_engine.py` / `templates/base.typ`) stays untouched.

**Not in scope:** the 13 medium/low findings (F1–F11, F13–F15) recorded in the audit catalogue are
next-milestone candidates (D-11), NOT Phase 18 work. Only the single high-severity FID-01a is fixed here.

</domain>

<decisions>
## Implementation Decisions

### Wide-table fix strategy (FID-01a / F12)

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
  Therefore `visit_tabular_col_spec` stays `raise SkipNode` as today. Honoring tabularcolumns is only
  meaningful under a "match LaTeX PDF layout" goal, which v0.6.1 does not hold. *(This reverses an
  earlier in-discussion lean toward parsing tabularcolumns, once the HTML-ignores-it fact surfaced.)*

### Regression-gate close (GATE-03)

- **D-04: GATE-03 is mechanical, not a design decision.** Re-run the corpus gate: assert the corpus
  still compiles fatal-free (`index.pdf` produced, 0 errors — GATE-02 non-regression) AND the
  `unknown_visit` catalogue is empty of `todo_node`/`manpage`. Reuse the existing
  `tests/test_corpus_gate.py` machinery — its `test_corpus_compiles_with_no_fatal_error` already
  asserts the empty-`unknown_visit` catalogue (green in Phase 17's fresh run).

### Claude's Discretion (open for research/planning)

- **Regression-fixture proof design (deliberately left open by the user — for the researcher/planner).**
  SC#1 requires a real-compile fixture that "would fail without the fix," but wide-table overflow is
  **silent** — it produces no fatal error and no warning, so a naive "does it compile" fixture passes
  with OR without the fix. The researcher/planner must design a fixture that genuinely regresses on the
  unfixed translator. SC#1 also forbids relying on `.typ` string-agreement alone. Candidate approaches
  to evaluate (non-binding): assert on page-fit / right-margin overflow of the compiled repro (e.g. via
  a Typst construct that errors when content exceeds the block, or a measured-width check), combined
  with — not replaced by — a real compile of the `extdev/deprecated`-style wide grid table. Resolve
  during research; document the chosen mechanism in the fixture.
- **Edge cases for the `fr` conversion:** `colwidth` missing / zero / not summing → fall back to equal
  `1fr` per column. Interaction with the existing LEN-01 `block(width: …)[#table(…)]` wrapper (from an
  explicit `:width:` on the table) — the `fr` columns fill whatever block width wraps them, so the two
  compose; verify with a real compile. `table.header(…)` cell structure is unchanged by the columns
  change.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The fix backlog & audit evidence (read FIRST)
- `.planning/phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md` — the F12 issue record and the
  "Root-cause groups (D-10)" / "High-severity groups (→ FID-01x)" table. Carries the minimal-repro
  pointer (`doc/extdev/deprecated.rst`, compiled pp.239–249) that IS the Phase 18 fixture input, the
  narrow-table contrast case (`extdev/appapi` pp.186–188), and the F6 right-margin-overflow *kinship*
  note (medium, NOT in FID-01a — do not conflate).
- `.planning/REQUIREMENTS.md` §"Rendering Fidelity Audit" — **FID-01a** (full failure description +
  occurrences), **FID-01** (parent), **GATE-03** (§"Regression Gate"), and the **Out of Scope table**
  (autodoc/`py:meth` warnings, graphviz/inheritance placeholders, non-included-doc xrefs) that Phase 18
  must NOT try to fix.

### Requirements & roadmap
- `.planning/ROADMAP.md` §"Phase 18: Fidelity Fixes + Regression-Gate Close" — the 4 Success Criteria
  (SC#1 real-compile fixture per high issue; SC#2 GATE-02 non-regression; SC#3 `unknown_visit` clear of
  todo_node/manpage; SC#4 no new deps / no `@preview` bump) and the milestone invariants.
- `.planning/phases/17-rendering-fidelity-audit/17-CONTEXT.md` — D-04 (HTML build is the fidelity
  authority), D-05 (same cached corpus), D-08 (severity rubric), D-09 (per-issue repro = fixture input),
  D-10/D-11 (root-cause granularity; high-only → FID-01x). These frame *why* FID-01a is the sole target.

### Corpus & test machinery to reuse (do NOT reinvent)
- `tests/test_corpus_gate.py` — corpus clone/cache + `sphinx-build -b typstpdf` wiring +
  `test_corpus_compiles_with_no_fatal_error` (the GATE-03 mechanism: empty-`unknown_visit` assertion).
  Corpus cached at `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc` (tag v9.1.0, SHA `cc7c6f4…`).
- `tests/test_pdf_render_gate.py`, `tests/test_table_in_list_item_render_gate.py`, and the
  `tests/fixtures/*_render_gate/` dirs — the GATE-01 real-`typst.compile()` fixture pattern every
  Phase-18 fix must follow (mini Sphinx project + real compile assertion).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `typsphinx/translator.py` `depart_table` (~line 2266) — the single emission site to change; already
  branches on the LEN-01 `block(width: …)[#table(…)]` wrapper. The `columns: {self.table_colcount}`
  line (2292/2295) is what becomes `columns: (…fr, …fr)`.
- `typsphinx/translator.py` `visit_colspec` (~line 2347) — currently `raise SkipNode`; the place to
  start *capturing* `colwidth` instead of discarding it (accumulate into per-table state initialized in
  `visit_table` / `visit_tgroup`, consumed in `depart_table`).
- `typsphinx/translator.py` `visit_tgroup` (~line 2328) — sets `self.table_colcount = node.get("cols")`;
  a natural companion place to reset the per-column-width accumulator.
- `_convert_length_to_typst` (~line 3116, LEN-01 shared helper) — reuse for any absolute-width path;
  the fr-ratio path is a new, small helper (integer weights → `(Nfr, Mfr, …)`).
- Test-fixture harnesses above (`test_corpus_gate.py`, `test_pdf_render_gate.py`, `*_render_gate/`).

### Established Patterns
- Every node-handler change ships/extends a real `typst.compile()` acceptance fixture (GATE-01 standing
  bar) — string-agreement asserts never suffice.
- Table cell content is buffered (`self.table_cells`) and emitted at `depart_table`; use
  `self.body.append` directly at that site (NOT `self.add_text`) to avoid the stale
  `table_cell_content` buffer-misrouting hazard (documented inline at `depart_table`).
- Discovery-sized phase: exact plan count is audit-driven. Here the audit yields ONE fix (FID-01a) +
  the GATE-03 close, so expect a small plan set (roughly one fix plan + the gate close).

### Integration Points
- Local env can run real corpus compiles (typst 0.15.0 present; corpus cached). NixOS sandbox CANNOT
  run the real corpus builds (~45 integration tests fail environmentally) — GATE-03 measurement needs
  the full local env, as Phases 15 & 17 did. See memory `nixos-sandbox-test-env`.
- Typst's 3-way `@preview` version-sync surface must stay untouched (`tests/test_preview_version_sync.py`
  guards it) — the fr-columns fix is native Typst, no package involved.

</code_context>

<specifics>
## Specific Ideas

- The fix's visual target is Sphinx's **HTML** rendering of wide tables (text wraps within the
  container, no horizontal overflow) — NOT LaTeX PDF table layout. This is why colwidth (which HTML
  honors) is used and tabularcolumns (which only LaTeX honors) is not.
- Fixture repro seed: the multi-page "Deprecated APIs" grid table on `doc/extdev/deprecated.rst`
  (compiled pp.239–249). A distilled minimal wide grid table reproducing the column-collision +
  right-margin-clip is the fixture input; the narrow `extdev/appapi` tables are the "still renders fine"
  contrast.

</specifics>

<deferred>
## Deferred Ideas

- **Honoring `.. tabularcolumns::` (LaTeX explicit column widths / alignment).** Explicitly rejected for
  v0.6.1 because the HTML fidelity authority ignores it (D-03). Revisit only under a future "match LaTeX
  PDF layout" goal.
- **`measure`-at-compile-time conditional column sizing** (keep narrow tables byte-identical, fall back
  to `fr` only on overflow). Considered for D-02, deferred as over-engineering for a single-root-cause
  fix; uniform `fr` chosen instead.
- **F6 (medium): long inline `literal` runs overflow/clip the right margin** (`usage/domains/cpp` p.85).
  Kinship to F12 (both right-edge overflow) but a different node kind (`literal` inline vs `table`) and
  medium severity — NOT part of FID-01a. Next-milestone candidate. A shared "avoid right-margin
  overflow" primitive *could* later serve both, without conflating them into one requirement.
- **The 13 medium/low audit findings (F1–F11, F13–F15)** — fully recorded in
  `17-AUDIT-CATALOGUE.md`, pointed to from REQUIREMENTS.md "Future Requirements" (D-11). Not v0.6.1 work.

</deferred>

---

*Phase: 18-fidelity-fixes-regression-gate-close*
*Context gathered: 2026-07-19*
