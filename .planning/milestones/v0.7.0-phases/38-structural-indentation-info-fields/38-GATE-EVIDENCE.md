# Phase 38 — Consolidated Gate Evidence

**Consolidated:** 2026-08-01, by `38-08-PLAN.md` Task 2, from `38-GATE-EVIDENCE-01.md` (plan 38-01),
`38-GATE-EVIDENCE-02.md` (plan 38-02) and `38-GATE-EVIDENCE-03.md` (plan 38-03) — the three wave-1
per-plan RED evidence files — plus this plan's own closing-time evidence (the full-corpus gate, the
milestone supply-chain invariants, the whole-suite final state, and the per-requirement verdict table).

This file does not replace the three source files, which remain in place with their full verbatim
pytest output, per-node-id RED/CONTROL-GREEN tables, and discovery narratives. This file summarizes
each and adds what only exists once the whole phase has landed.

---

## 1. Wave-1 RED evidence, summarized

### 1.1 `38-GATE-EVIDENCE-01.md` (plan 38-01) — IND-01..05, FLD-01, D-04, D-11

- **Module:** `tests/test_desc_content_indent_render_gate.py`, 13 collected node ids.
- **Result at capture:** 6 failed, 7 passed — `typsphinx/` completely untouched (`git diff --stat`
  empty at capture time).
- **The 6 RED ids** (structural token/column mismatches, never a `TypstError`): the body wrapper's
  opening token absent; the shared-step value found 0 times where ≥2 was required; the first
  body-less confval sibling's wrapper pair absent; the class body's column not `>` its own signature's
  column; the nested method's body column not `>` the class body's; the field-list line's column not
  `>` the method body's.
- **7 reclassified non-regression controls** (GREEN pre-phase because the pre-phase state is a
  trivial `0 == 0` case, not because the property was already implemented): IND-03's and IND-05's own
  compiled-PDF equality assertions, the SIG-09/D-11 page-boundary cross-page equality, and four purely
  structural controls (the SC#4 single-literal grep, the D-04 block-quote non-conversion, the
  no-wrapper-in-empty-region check, build-determinism).
- **SC#4 discovery grep** (IND-04, milestone invariant #6): exactly one match,
  `SHARED_INDENT_STEP = "2.5em"` at `typsphinx/translator.py:29` — re-run at Task 2 below with an
  identical result.
- **Two pre-existing defects found while building the fixture**, both out of this plan's own scope and
  carried forward: `depart_desc_signature`'s two `self.body.append(...)` sites bypass table-cell
  routing unconditionally (fixed by 38-06's authorized scope extension, see §2.2 below); the
  `field_list` family's five `self.body.append(...)` sites independently hit the same class of defect
  (fixed by 38-06 as originally planned).

### 1.2 `38-GATE-EVIDENCE-02.md` (plan 38-02) — FLD-02/FLD-03 structural RED

- **Module:** `tests/test_field_body_typography_render_gate.py`, 20 collected node ids.
- **Result at capture:** 15 failed, 5 passed, against the untouched translator.
- **15 RED ids**, every one an `AssertionError` from a Python string/regex comparison on a `.typ` build
  that itself succeeded (`sphinx-build -b typst` exit 0, `typst.compile()` producing a real
  85,695-byte PDF) — never a compile fatal: bold/italic PROPORTIONAL emitted where bold/italic
  MONOSPACE is required (8 parametrized FLD-03 name/type cases), the typeless-param zero-italic-mono
  count, the non-ASCII round-trip, the resolvable-cross-reference composition, the single-value
  `:returns:` body still block-wrapped (D-07's defect verbatim), the PDF-extracted adjacency check,
  the single-entry `:param:` prose check, and the field-list wrapper's opening token (absent, since
  `visit_desc_content` was still `pass` at this plan's capture time).
- **5 CONTROL-GREEN ids**, one of which (`test_fld02_bulleted_multi_value_non_regression_control`) is
  a plan-mandated always-green case; the other four are genuine pre-existing GREEN properties
  (field-label distinctness, no stray zero-width space, per-field line separation, build determinism)
  reclassified as non-regression controls that must survive the phase.
- **D-13 disposition recorded and re-confirmed**: the stray `parbreak()` at the head of each bulleted
  field-list item is LEFT IN PLACE — grep evidence
  (`tests/test_inline_math_after_text_render_gate.py:291`,
  `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ:66-67`) confirms an existing pinned
  assertion already depends on the shape, and the mechanism (`visit_paragraph`'s
  `self.in_list_item` fast-path) fires repo-wide, not only for field-list bullets.

### 1.3 `38-GATE-EVIDENCE-03.md` (plan 38-03) — D-10 conjunction + folded buffer-swap todo

- **Modules:** `tests/test_signature_break_and_arrow_gate.py` (4 pre-existing SIG-08/SIG-06/D-11 ids,
  all PRE-EXISTING-GREEN, docstring-only changes; 3 new `TestD10BodyWrapperBreakMarkerGate` ids) and
  the new `tests/test_desc_break_marker_buffer_swap_gate.py` (5 ids).
- **Result at capture:** 1 failed, 16 passed, against the untouched translator (`git status --porcelain
  typsphinx/` empty).
- **The sole RED**, `test_d10_wrapper_present_and_break_count_still_eight`, is a conjunction by design
  (D-10's own requirement): the wrapper-open token absent (pre-phase) AND the `parbreak()` count must
  stay exactly 8 (already true pre-phase) — the RED fires on the first clause, not the second, so the
  count assertion alone could never have been RED.
- **Buffer-swap fixture measured GREEN, not RED** — the folded todo's own prose predicted RED, but the
  measurement shows the nested `desc` pair placed entirely inside one glossary definition's body has
  both `depart_desc` calls run inside the SAME swapped buffer, so the pre-phase marker comparison stays
  internally consistent for this specific reachable shape. Declared a non-regression control, honestly
  recorded as a measurement that contradicted the todo's own prediction rather than retro-fitted into a
  RED it did not produce, per the todo's own binding instruction.
- **D-10 resolution adopted at plan time**: marker propagation through `depart_desc_content`'s close
  (contract §6.2); `depart_desc` itself needed no code change, only its docstring premise corrected —
  both delivered by plan 38-05 (§1.1 below).

---

## 2. Wave 2-4 GREEN evidence, summarized (from each plan's own SUMMARY)

### 2.1 Plan 38-05 — `desc_content` body wrapper + D-10 marker propagation

- `visit_desc_content`/`depart_desc_content` wrap the body in `pad(left: SHARED_INDENT_STEP, {...})`
  via `self.add_text` — zero depth-tracking state (D-01). Flips all 6 of §1.1's RED ids GREEN.
- D-10's marker-propagation fix lands; `_desc_break_marker` becomes `(id(self.body), len(self.body))`
  — closes the folded buffer-swap todo, no sixth per-site guard added.
- `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` hand-migrated (never regenerated) and
  confirmed byte-identical to a fresh rebuild on the first attempt.
- Whole-suite state after this plan: **683 passed, 17 failed, 29 deselected** (17 failures: FLD-01's
  own PDF assertion, FLD-02/FLD-03's 15 ids, and the Phase-34 A3 golden re-measured-not-migrated here
  — all explicitly owned by 38-06/38-07 per the census).

### 2.2 Plan 38-06 — `field_list` indent wrapper + single-value field-body reflow

- `visit_field_list`/`depart_field_list` wrap the field list in its own nested `pad(...)` (FLD-01).
- `visit_field_body`/`visit_paragraph` gain the single-paragraph-unwrapped classification (FLD-02);
  the D-07/D-08 trap closed by excluding the new classification from `_last_field_body_was_inline`.
- The field-list family's five pre-existing `self.body.append` sites, plus (authorized scope
  extension) `depart_desc_signature`'s two remaining sites, converted to `self.add_text` — closing
  both table-cell compile defects §1.1 discovered.
- Both Phase-34 PDF-text goldens re-measured as closing owner and hand-verified to differ from the
  prior baseline by exactly the predicted Construct C line-wrap consequence, nothing else.
- One census miss folded in (an assertion one line upstream of row A4's own prediction, in
  `tests/test_field_list_in_list_item_render_gate.py`) plus row A4's own predicted break, both migrated
  in this plan.
- Whole-suite state after this plan: **689 passed, 11 failed, 29 deselected** (11 failures: all
  `test_fld03_*`, owned by 38-07).

### 2.3 Plan 38-07 — `literal_strong`/`literal_emphasis` monospace leaves

- Both handlers stop delegating through the dummy-node trick (D-09); a new shared private helper,
  `_emit_field_body_monospace_leaf`, emits `strong(raw(...))`/`emph(raw(...))` directly, escaped via
  `escape_typst_string` alone (never the SIG-07 zero-width-space-injecting signature helper).
- `38-TEST-CENSUS.md` row A2's SC#1 over-reach guard migrated in
  `tests/test_desc_rubric_decoupling_render_gate.py` (not `test_translator.py`/`test_pdf_render_gate.py`
  as the plan's own frontmatter listed — neither file contains a `literal_strong`/`literal_emphasis`
  assertion, confirmed by grep before editing; the census's own authority names the correct file).
- One Rule-1 test-region fix: the typeless-param test's region narrowed past the fixture's own
  `desc_signature`, whose orthogonal SIG-04 rule was tripping the "zero italic-mono" assertion on
  unrelated bytes.
- Whole-suite state after this plan: **700 passed, 0 failed, 29 deselected.**

---

## 3. Task 1 evidence (this plan) — page-count re-measure

See `tests/test_signature_page_boundary_render_gate.py` (constant renamed
`EXPECTED_PAGE_COUNT_PRE_PHASE` → `EXPECTED_PAGE_COUNT_CEILING`, closing the second folded todo) and
`tests/test_signature_typography_multi_signature_page_count_gate.py`, both with the full re-measurement
narrative recorded in their own provenance comments above the constant. Summary:

| Fixture | Constant | Pre-measure value | Post-Phase-38 measured value | Moved? |
|---|---|---|---|---|
| `signature_page_boundary_render_gate` | `EXPECTED_PAGE_COUNT_CEILING` (renamed) | 7 | 7 | No — no field list, no body-less single-value field in this fixture |
| `signature_typography_gate` | `EXPECTED_PAGE_COUNT` | 4 | 4 | No — page budget has slack an order of magnitude larger than either of this phase's effects |

Both re-measured via a real `sphinx-build -b typst`/`-b typstpdf` + `typst.compile()` +
`pypdf.PdfReader` page count against the post-Phase-38 translator (this worktree's base commit,
`7ae016d`, already contains 38-05/38-06/38-07's landed changes) — never derived from this document or
regenerated from the build's own output as a golden.

**D-08's whole-document claim, checked against a real build:**

```
$ uv run tox -e docs-pdf
...
build succeeded, 4 warnings.
  docs-pdf: OK

$ uv run python -c "import pypdf; r = pypdf.PdfReader('docs/_build/pdf/typsphinx.pdf'); print(len(r.pages))"
90
```

`docs/source` content confirmed unchanged since the discussion session (`git log -- 'docs/sourc[e]'`
against this branch's own history shows no commit touching it). Measured: **90 pages**, versus the
discussion session's exploratory prototype figure of **97 → 87**. Divergence explained, not absorbed:
the 97-to-87 figure (`38-EMISSION-CONTRACT.md` §4.4) is attributed specifically to D-07's field-body
reflow effect in isolation; the shipped implementation additionally includes D-01/D-03's
`pad(left:, {...})` wrapper (which narrows the available line-wrapping column) and D-05's
proportional-to-monospace field-list move (§5.6's own width note) — both countervailing widening
effects not present in that isolated figure. No controlled ablation across the three effects was
performed in this plan; this is the best-supported explanation from the contract's own documented
facts, recorded honestly rather than assumed. The **direction** the session predicted (net shortening
versus the pre-Phase-38 baseline) is confirmed by the 90-page result sitting below the pre-Phase-38 page
count; the shipped **magnitude** differs from the isolated prototype figure because the shipped build
combines effects the prototype measurement did not.

---

## 4. Task 2 evidence (this plan) — full-corpus gate + milestone supply-chain invariants

### 4.1 Full-corpus gate

```
$ uv run pytest tests/test_corpus_gate.py -m slow -v
collected 5 items / 3 deselected / 2 selected

tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED [ 50%]
tests/test_corpus_gate.py::test_empty_url_before_after SKIPPED (SC#3
before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1
to run it (RESEARCH Open Question 1))                                    [100%]

1 passed, 1 skipped, 3 deselected in 14.10s
```

The skip is an unrelated, pre-existing, env-gated SC#3 measurement (a different "Open Question 1" —
`test_corpus_gate.py`'s own module docstring's SC#3 before/after URL count, not
`38-RESEARCH.md`'s Open Question 1 addressed below). The corpus gate itself (real `git clone --depth 1`
of Sphinx's own `doc/` tree at the matching tag, `-b typstpdf`, real `typst.compile()`, `%PDF` check)
**passed** — no `TypstError`, no `unknown_visit` catalogue entry.

**`38-RESEARCH.md` Open Question 1**, checked explicitly: "does the D-07 single-paragraph-unwrap
mechanism need to also handle a field body whose one paragraph itself contains a nested block element?"
No instance of this shape was found in the corpus. Two independent lines of evidence:

1. **Structural**: docutils' `nodes.paragraph` is an `Inline`-container element per docutils' own node
   class hierarchy — it can only contain `Inline`-class children (Text, `emphasis`, `strong`,
   `reference`, `literal`, inline `math`, footnote/substitution references, inline `image`), never a
   `Body`-class block child (`literal_block`, `bullet_list`, an admonition, a block `math`). A "paragraph
   that wraps a literal block" is therefore not reachable through standard RST parsing at all, regardless
   of what any specific corpus happens to contain — this resolves the open question structurally, not
   just empirically.
2. **Empirical**: `grep -rE '^\s*:param|^\s*:returns:|^\s*:type '
   ~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc/` finds 163 field-list lines across 10 files —
   real, non-trivial field-list content — and the corpus build above compiled with zero fatal errors
   and an empty `unknown_visit` catalogue, consistent with no anomalous case being hit.

**Finding: the corpus contains no instance of Open Question 1's shape, and the shape is structurally
unreachable in general.** No fix or follow-up todo required; `38-RESEARCH.md`'s own recommendation
("the `isinstance` check is safe regardless") is confirmed rather than merely assumed.

### 4.2 Supply-chain invariants (milestone invariants 1 and 2)

Phase base commit: `1fefe51` (the commit immediately before `b70385f docs(38): capture phase context`,
the first Phase 38 commit).

```
$ git diff 1fefe51 -- pyproject.toml uv.lock
(empty — 0 lines)
```

No runtime dependency added. Confirmed empty (`wc -l` = 0).

```
$ grep -c "@preview" typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ
typsphinx/templates/base.typ:4
typsphinx/writer.py:4
typsphinx/template_engine.py:5
```

```
$ uv run pytest tests/test_preview_version_sync.py -v
test_preview_versions_identical_across_declaration_sites PASSED
test_all_four_packages_declared PASSED
test_example_templates_match_canonical_versions PASSED
3 passed in 0.02s
```

The standing three-site lockstep gate is green: all three declaration sites agree, and exactly four
packages (`codly`, `codly-languages`, `mitex`, `gentle-clues`) are declared. No new version-lockstep
site was introduced by Phase 38.

```
$ git diff --name-status 1fefe51 -- typsphinx/
M	typsphinx/translator.py
```

Only `typsphinx/translator.py` was modified across the whole phase. No file was added or removed under
`typsphinx/` — no new template asset, no new module.

### 4.3 Whole-suite final state

```
$ uv run pytest -m "not slow" -q
700 passed, 29 deselected in 47.61s
```

**Zero failures.** Set-difference against plan 38-04's recorded pre-phase baseline
(`659 passed, 29 deselected`, collected 688 items, recorded in `38-TEST-CENSUS.md` before any
wave-1 gate module existed): **+41 net new passing node ids**, all newly added by the three wave-1
gate modules (13 from `test_desc_content_indent_render_gate.py`, 20 from
`test_field_body_typography_render_gate.py`, 8 net-new from `test_signature_break_and_arrow_gate.py`'s
new `TestD10BodyWrapperBreakMarkerGate` class plus `test_desc_break_marker_buffer_swap_gate.py`;
`13 + 20 + 8 = 41`). Cross-validated against each plan's own recorded intermediate totals:
`659 + 41 = 700` matches the collected-item accounting exactly at every wave boundary
(38-05: `683 passed + 17 failed = 700` selected; 38-06: `689 + 11 = 700`; 38-07: `700 + 0 = 700`);
deselected stayed at 29 throughout (no slow-marked test added or removed). Every flipped id is
accounted for by a named plan's own SUMMARY (§2 above) or a census row (§5 below); none is
unaccounted-for.

### 4.4 Requirement verdict table

| Requirement | Verdict | Proving node id(s) |
|---|---|---|
| IND-01 | PASS | `tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ind01_structural_wrapper_token_and_position`, `::TestDescContentIndentPdfGate::test_ind01_body_indented_past_signature` |
| IND-02 | PASS | `tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind02_nested_body_deeper_and_resumed_body_returns` |
| IND-03 | PASS | `tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind03_nested_signature_equals_parent_body_column` |
| IND-04 | PASS | `tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ind04_structural_shared_step_value_at_new_sites` + the SC#4 discovery grep (below) |
| IND-05 | **ASSERTED, not implemented** — see reasoning below | `tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind05_sibling_top_level_returns_to_margin` |
| FLD-01 | PASS | `tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_fld01_field_list_deeper_than_method_body`, `tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld01_field_list_wrapper_nested_inside_desc_content_wrapper` |
| FLD-02 | PASS | `tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_single_value_returns_no_block_paragraph_wrapper`, `::test_fld02_single_value_pdf_adjacency_matches_pinned_string`, `::test_fld02_single_entry_param_renders_inline_prose_never_bulleted`, `::test_fld02_consecutive_single_value_fields_stay_on_separate_lines`, `::test_fld02_bulleted_multi_value_non_regression_control` |
| FLD-03 | PASS | `tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_name_bold_monospace[*]`, `::test_fld03_param_type_italic_monospace[*]`, `::test_fld03_field_label_unchanged_and_distinct_from_name_and_type`, `::test_fld03_typeless_param_exactly_one_bold_mono_zero_italic_mono`, `::test_fld03_resolvable_type_composes_inside_link_unchanged_label` |

**IND-05 row, stated explicitly**: under D-01, `desc_content`'s indent wrapper carries **no depth
counter** — nesting composes structurally because each `pad(...)` closes on `depart_desc_content`, not
because a counter increments and decrements correctly. REQUIREMENTS.md's own wording ("the
nesting-depth counter resets correctly across sibling `desc` nodes") is therefore satisfied by proving
depth **cannot leak** (there is nothing to leak), not by building a counter and testing that it resets.
`test_ind05_sibling_top_level_returns_to_margin` is the operational proof: a sibling top-level `desc`
after a nested pair lands back at the page margin, the same column as the first class's own signature,
confirmed at real (non-trivial, post-wrapper) column values.

**IND-04 row, closing grep quoted and compared to discovery time:**

```
$ awk '$0 !~ /^[[:space:]]*#/ {print NR": "$0}' typsphinx/translator.py | grep -E '[0-9]+(\.[0-9]+)?em\b'
29: SHARED_INDENT_STEP = "2.5em"
```

**Identical** to the discovery-time run recorded in `38-GATE-EVIDENCE-01.md` (`38-EMISSION-CONTRACT.md`
§1.1's planning-time run, and 38-01's own discovery-time run): exactly one match, the same
`SHARED_INDENT_STEP = "2.5em"` definition at the same line. No second independent indent literal was
introduced anywhere in `typsphinx/translator.py` across the whole phase, at any of its wave-1/2/3/4
touch points — the desc_content wrapper (§2) and the field_list wrapper (§3) both spell
`SHARED_INDENT_STEP`, never a new literal.

---

## 5. Cross-reference to the finalised test census

`38-TEST-CENSUS.md`'s own "Finalisation against reality" section (added by this plan's Task 3) is the
authoritative predicted-versus-actual record, including the honest misses this evidence file's §1-§2
narrative already names in passing (the census miss `38-06` found one assertion upstream of row A4, the
`38-EMISSION-CONTRACT.md` §7 over-prediction on `test_translator.py`, and the under-prediction on row
A2's SC#1 guard). This file is the gate-pass record; the census is the prediction-accuracy record. Read
both together.

## 6. Human sign-off (Task 3's human-check)

**Verdict: APPROVED.** The reviewer opened `docs/_build/pdf/typsphinx.pdf` (90 pages, the same build
measured in §3 above) and approved the plan's own six-point aesthetic checklist.

**One question raised and resolved by measurement, recorded here rather than silently dropped:**
page 37, the `typsphinx.pdf` module's docstring (produced by `.. automodule:: typsphinx.pdf`) renders
flush left, unindented, unlike the surrounding class/function bodies. Dismissed as NOT a Phase 38
defect:

- No `desc`/`desc_content` node exists for a module docstring — `automodule` emits only an index entry
  and a target; the docstring becomes plain `paragraph` children of the enclosing `section`. IND-01's
  wrapper is structurally inapplicable, not merely unapplied. Confirmed in the emitted
  `docs/_build/pdf/api/index.typ`: `[#metadata(none) <api_u2f_index:module-typsphinx.pdf>]` is followed
  directly by bare `par({text(...)})` with no `pad(left: 2.5em, {`, unlike the adjacent
  `TypstCompilationError` class, which shows the wrapper immediately after its own signature.
- Phase 38 only ADDED wrappers around `desc_content` and `field_list`; a node inside neither cannot
  have changed behaviour. Pre-Phase-38 unchanged.
- Cross-checked against the reference renderer: `sphinx -b latex` on the same `docs/source` puts the
  identical module docstring in bare `\sphinxAtStartPar` paragraphs with no `\begin{fulllineitems}`,
  while the adjacent class body IS wrapped in `fulllineitems` — typsphinx's Typst output matches
  upstream Sphinx's own LaTeX convention here.
- **Disposition: no todo filed, no code change.** Full detail in `38-08-SUMMARY.md`'s "Human-Check
  Verdict" section and `38-TEST-CENSUS.md`'s finalisation section.

---

*Phase: 38 — Structural Indentation + Info Fields*
*Consolidated: 2026-08-01, by plan 38-08 Tasks 2-3*
