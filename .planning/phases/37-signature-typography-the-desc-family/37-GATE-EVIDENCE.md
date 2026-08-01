# Phase 37 — Consolidated Gate Evidence

**Produced by:** `37-08-PLAN.md` (phase closeout), Task 1 + Task 2.
**Phase-start commit (before/after baseline):** `011b9265daf3389f3482b5efd96b4eaa16a94743`.
**This file is a consolidation, not a replacement.** The four Wave-1 evidence files
(`37-GATE-EVIDENCE-01.md`..`-04.md`) plus the Wave-5 gap-closure evidence file
(`37-GATE-EVIDENCE-09.md`) remain in place as the primary, per-plan record. This file adds the
requirement verdict table, the ROADMAP SC mapping, the control roster, and the milestone-invariant
checks that only become answerable once every wave is done.

**Plan census note (read this first):** `37-08-PLAN.md` was authored before plan `37-09` existed.
`37-09` is a gap-closure plan the orchestrator authored mid-execution, on the owner's explicit
decision (2026-08-01), after the post-merge gate following Wave 3 caught a real defect — the
`block(above: 0pt, below: 0pt, sticky: true, ...)` wrapper made every signature's glyphs overlap the
first line of its own description body. `37-09` amended `37-EMISSION-CONTRACT.md` §3, corrected the
translator's wrapper emission, hand-re-derived every dependent expected string, and closed the whole
suite green for the first time in the phase. This document treats `37-09` as a first-class member of
the phase's evidence, not an afterthought.

---

## 1. Milestone invariants, verified by command (all run in this worktree, 2026-08-01)

### 1.1 Whole suite, default run

```
$ uv run pytest -m "not slow" -q
================== 658 passed, 29 deselected in 43.85s ==================
```

Zero failures, zero errors.

### 1.2 Full-corpus `-b typstpdf` gate (slow-marked, excluded from the default run)

```
$ uv run pytest tests/test_corpus_gate.py -m slow -v
tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED [ 50%]
tests/test_corpus_gate.py::test_empty_url_before_after SKIPPED (SC#3 before/after
  measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it) [100%]
================= 1 passed, 1 skipped, 3 deselected in 13.65s ==================
```

This is the run where 1,445 real `desc_signature` nodes from Sphinx v9.1.0's `doc/` corpus exercise
the new emission end to end — the corpus is cached at `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0`
(shared with the main tree), so this was a real recompile against the real corpus, not a cache-only
no-op. **`test_corpus_compiles_with_no_fatal_error` also asserts the `unknown_visit` catalogue is
EMPTY** (`tests/test_corpus_gate.py:361-365`) — it passed, so the corpus run surfaced **zero** new
unknown-node warnings from the `desc_sig_*` family (`desc_sig_literal_string` /
`desc_sig_literal_number` / `desc_sig_keyword_type` get correct styling "for free" via the
`in_signature_text` flag per contract §4.3, with no dedicated handler and no warning). No todo was
needed for that channel.

One unrelated, pre-existing docs-build finding was discovered while running `tox -e docs-pdf` for
§1.4 below — see that subsection.

### 1.3 Lint / type trio

```
$ uv run black --check .
All done! (183 files would be left unchanged.)

$ uv run ruff check .
All checks passed!

$ uv run mypy typsphinx/
Success: no issues found in 6 source files
```

### 1.4 `tox -e docs-pdf` — the project dogfooding its own builders

```
$ uv run tox -e docs-pdf
...
writing output... [api/index] done
...
Generated PDF: .../docs/_build/pdf/typsphinx.pdf
build succeeded, 4 warnings.
  docs-pdf: OK (3.91=setup[0.48]+cmd[3.42] seconds)
```

Runnable in this environment; it built and compiled successfully. Of the 4 warnings:

- 2 are Sphinx/`sphinx-autodoc-typehints` deprecation notices (`RemovedInSphinx10Warning`,
  unrelated to typsphinx or Phase 37).
- 1 (`visit_toctree`'s docstring, "Unexpected indentation") **pre-dates Phase 37** — confirmed by
  reading the same docstring at the phase-start commit (`011b926`); `visit_toctree` is untouched by
  this phase.
- 1 is **new, introduced by this phase's own docstring authoring** (plan `37-06`):
  `visit_desc_sig_name`'s docstring contains the phrase `"PyTypeObject *type, no intersphinx"`,
  whose bare `*` docutils parses as an unterminated inline-emphasis marker
  (`WARNING: Inline emphasis start-string without end-string`), which in turn produces a stray
  `problematic` node and an `unknown node type` warning during `writing output... [api/index]`
  (confirmed: `WARNING: unknown node type: <problematic ids="id2" refid="id1">*</problematic>`).
  This is a docs-build cosmetic defect, not a Phase 37 requirement failure — no SIG assertion covers
  a translator docstring's own prose, and `typsphinx/translator.py` is not in this plan's
  `files_modified`. Filed as a todo rather than fixed inline:
  `.planning/todos/pending/2026-08-01-visit-desc-sig-name-docstring-unbalanced-asterisk-warning.md`.

### 1.5 Standing invariant: zero new runtime dependencies

```
$ git diff 011b926..HEAD -- pyproject.toml
(empty)
```

No dependency was added, removed, or version-changed anywhere in the phase.

### 1.6 Standing invariant: `@preview` package count still four, no new lockstep site

```
$ uv run pytest tests/test_preview_version_sync.py -v
test_preview_versions_identical_across_declaration_sites PASSED
test_all_four_packages_declared PASSED
test_example_templates_match_canonical_versions PASSED
3 passed in 0.02s

$ git diff 011b926..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ
(empty)
```

None of the three `@preview`-version declaration sites CLAUDE.md names (`writer.py`,
`template_engine.py`, `templates/base.typ`) was touched by any Phase 37 plan. The package count and
versions are unchanged.

### 1.7 No new font selection

```
$ git diff 011b926..HEAD -- typsphinx/translator.py | grep -n "font"
299:+        and font-shrinking were both measured and rejected by the owner) --

$ grep -rn "set text(font\|text(font:" typsphinx/
(no matches)
```

The only "font" occurrence in the whole-phase diff is a docstring *comment* recording that font
shrinking was measured and rejected as an overflow strategy (D-06) — not a `set text(font: ...)`
call. D-04's prohibition holds: `raw(...)` is the only monospace primitive introduced this phase, and
a repo-wide search finds no font-family selection anywhere under `typsphinx/`. STATE.md's risk (a
font selection silently shadowing the `ja` build's CJK fallback) does not materialize.

### 1.8 No bundled Typst style module

```
$ git diff --name-only 011b926..HEAD -- typsphinx/
typsphinx/translator.py
```

`typsphinx/translator.py` is the **only** file under `typsphinx/` touched by the whole phase (all
eight executed plans, including the `37-09` gap closure). No new `.typ` file was added anywhere
under `typsphinx/`.

---

## 2. Requirement verdict table (SIG-01..SIG-09 + D-11)

Every row names the test node id that proves the requirement, the commit at which it was recorded
RED, the commit at which it turned GREEN, and the emission-contract section that specified its
expected shape. A requirement with no named RED commit would not count as verified — every row below
has one.

| Req | Proving test node id | RED commit | GREEN commit | Contract section |
|---|---|---|---|---|
| SIG-01 | `tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig01_leaf_desc_name_bold_monospace` | `6ca21d6` (37-01 Task 2) | `f63fe8f` (37-06 Task 3) | §5.1, §5.2 rule 1 |
| SIG-02 | `tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_addname_plain_monospace_with_zwsp_and_no_enclosing_bold` | `6ca21d6` (37-01 Task 2) | `7674e3f` (37-06 Task 2) | §4, §4.3 |
| SIG-03 | `tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig03_annotation_and_name_wrapper_shapes_are_byte_identical` | `6ca21d6` (37-01 Task 2) | `f63fe8f` (37-06 Task 3) | §5.1 |
| SIG-04 | `tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_parameter_names_italic_type_and_default_plain` | `6ca21d6` (37-01 Task 2) | `f63fe8f` (37-06 Task 3) | §5.2 |
| SIG-05 | `tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_delimiters_use_monospace_primitive` | `6ca21d6` (37-01 Task 2) | `7c8dce0` (37-07 Task 1) | §6 |
| SIG-06 | `tests/test_signature_break_and_arrow_gate.py::TestSigArrowPdfGate::test_sig06_arrow_glyph_present_ascii_arrow_absent` | `e846227` (37-02 Task 2) | `6c1d63b` (37-07 Task 3) | §7 |
| SIG-07 | `tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_primary_widest_segment_fits_column` | `dab9a60` (37-03 Task 1) | `550b04a` (37-06 Task 1) | §3 (amended `626a4d7`, 37-09 Task 1), §4.1, §10 |
| SIG-08 | `tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_exact_break_count_after_fix` | `e846227` (37-02 Task 2) | `ebf7e18` (37-05 Task 1) | §8 |
| SIG-09 | `tests/test_signature_page_boundary_render_gate.py::TestSignaturePageBoundaryRenderGate::test_primary_signature_and_body_share_a_page` | `6113429` (37-03 Task 2) | `550b04a` (37-06 Task 1); wrapper corrected `76324bf` (37-09 Task 2) | §3 (amended `626a4d7`, 37-09 Task 1) |
| D-11 | `tests/test_signature_break_and_arrow_gate.py::TestD11SeparatorStructuralGate::test_d11_separator_lands_inside_the_bracket` | `e846227` (37-02 Task 2) | `816e252` (37-07 Task 2) | §6.1, §6.2 (correction to CONTEXT.md D-11) |

**SIG-07/SIG-09 note on the `37-09` amendment.** Both requirements' own primary assertions
(`test_primary_widest_segment_fits_column`, `test_primary_signature_and_body_share_a_page`) turned
GREEN at `550b04a` (37-06) and **stayed** green through `37-07` and `37-09` — neither requirement was
ever re-broken. What `37-09` corrected was a *different* defect the SIG-07/SIG-09 assertions do not
cover (vertical spacing/overlap, caught instead by the Phase-34 MATH-02 golden — see §4 below), and
in doing so it re-derived the wrapper text that contract §3 specifies and that SIG-07's
`test_hanging_indent_present` / SIG-09's `test_page_count_does_not_inflate` assertions check against.
Both are recorded here for completeness, not because SIG-07/SIG-09 themselves regressed.

---

## 3. ROADMAP SC#1..SC#5 mapping

| SC | Text (paraphrased) | Discharged by |
|---|---|---|
| SC#1 | Each signature sub-part emits a distinct, structurally-asserted treatment (bold/regular/italic monospace via `raw`/`strong(raw(...))`/`emph(raw(...))`, never bare `text(...)`), recorded RED before any code existed | SIG-01..05's 15 structural assertions in `tests/test_signature_typography_gate.py`, all RED at `6ca21d6` (37-01), all GREEN by `7c8dce0` (37-07 Task 1) |
| SC#2 | `desc_returns` renders a real arrow glyph in the compiled PDF's extracted text, no ASCII `->` remaining anywhere | SIG-06: RED at `e846227` (37-02), GREEN at `6c1d63b` (37-07 Task 3); `tests/test_pdf_render_gate.py::TestDescSignatureRenderGate::test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline` independently confirms no ASCII arrow survives |
| SC#3 | A long fully-qualified signature drawn from the real corpus stays inside the margin, overflow strategy derived from real corpus measurements, not assumed to transfer from the v0.6.1 wide-table fix | See §3.1 below — the criterion's own wording is honoured by a synthetic RED fixture plus a real-corpus GREEN control, not a corpus-derived RED fixture |
| SC#4 | A signature at a page boundary keeps its name, parameter list, and the first line of its body on the same page | SIG-09: RED at `6113429` (37-03), GREEN at `550b04a` (37-06); `sticky: true` keep-together re-verified GREEN after the `37-09` wrapper correction (`76324bf`) |
| SC#5 | Sibling signatures separated by exactly one break; this phase's own exact-string blast radius migrated within the phase, hand-derived, with a recorded file/class census | SIG-08: RED at `e846227` (37-02), GREEN at `ebf7e18` (37-05). Blast radius: `37-TEST-CENSUS.md` (finalised in this plan's Task 2, §5 below) plus `37-09`'s own additionally-measured blast radius (§5.3) |

### 3.1 SC#3's synthetic-fixture reasoning, spelled out

SC#3's own wording says the overflow strategy "must be derived from measurements of actual corpus
signatures" — and it was. `37-RESEARCH.md`'s Pitfall 2 and `37-GATE-EVIDENCE-03.md`'s
"SYNTHETIC-by-necessity" section both record the same measured fact: **the real Sphinx v9.1.0
`doc/` corpus (1,445 signatures scanned) does not overflow the 453.54pt production text column at
all.** Its own worst case — `sphinx.util.parsing.nested_parse_to_nodes`, a 41-character qualname —
measures only 217.22pt as an unbroken run, comfortably under the column. A corpus-derived RED
fixture is structurally impossible: the untouched translator would already pass it, proving nothing.

The measurement is the point, not a shortcut around it. Because the corpus does not overflow, the
correct derivation FROM that measurement is: (a) keep the real-corpus worst case as a
**non-regression control**, expected GREEN both before and after (`test_control_widest_segment_fits_column_before_and_after`,
`37-01-PLAN.md`/`37-03-SUMMARY.md`), and (b) build the RED case from a **synthetic** 111-character
identifier reused verbatim from `37-EMISSION-CONTRACT.md` §10's own measurement session, so the fix
(hanging indent + ZWSP break injection) is proven against a case that actually exercises it. A reader
comparing the fixture's synthetic identifier against a "corpus signatures" checklist item without
this context would misread it as a shortcut; it is the measured, correct response to what the corpus
turned out to show.

---

## 4. Control roster

Every assertion below was GREEN before AND after by design — each exists to prove something did
**not** regress, not to gate a fix.

| # | Control | Node id / location | Why it exists |
|---|---|---|---|
| 1 | Sibling body-less `desc` break control (FID-06) | `tests/test_desc_bodyless_concat_render_gate.py::TestDescBodylessConcatRenderGate::test_typstpdf_bodyless_desc_siblings_get_parbreak_and_produce_pdf` | Proves the SIG-08 emission-position-marker fix (`depart_desc`, 37-05) does not disturb the pre-existing sibling body-less `desc` separator it shares a code path with |
| 2 | Depth-counter trap control | `tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_content_follows_nested_member_stays_separated` | Proves the SIG-08 fix used "was anything emitted since" (correct) rather than a desc-nesting-depth counter (wrong) — a nested member followed by more parent-body content still keeps its separating break |
| 3 | Nested-optional rendering control (D-11) | `tests/test_signature_break_and_arrow_gate.py::TestD11SeparatorPdfGate::test_d11_nested_optional_control_unchanged` | `printf(fmt[, args[, more]])` — both `desc_optional`s are last children, so neither gains a comma; proves the D-11 sibling-guard fix does not over-fire |
| 4 | Explicit-concatenation non-regression control (D-11) | `tests/test_signature_break_and_arrow_gate.py::TestD11SeparatorStructuralGate::test_d11_explicit_concatenation_non_regression` | Contract §6.2's correction: the closing bracket and the following parameter were ALREADY `+`-joined on the untouched tree — this control converts what CONTEXT.md's D-11 mis-described as a fix into a documented non-regression assertion |
| 5 | Real-corpus width control (SIG-07) | `tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_control_widest_segment_fits_column_before_and_after` | See §3.1 — proves the real corpus's own worst-case signature fits the column both before and after, so nobody mistakes the synthetic RED fixture for the whole story |
| 6 | Page-count non-inflation control (SIG-09) | `tests/test_signature_page_boundary_render_gate.py::TestSignaturePageBoundaryRenderGate::test_page_count_does_not_inflate` | Guards against `block()`'s spacing silently growing every document's page count. Re-pinned by `37-09` from 6 to 7 — see §5.2, a real re-measurement, not a regression |
| 7 | Two rubric assertions (Phase 39 territory) | `tests/test_rubric_option_concat_render_gate.py` (`Structure Options`, `Trailing Heading` lookups); `tests/test_translator.py::test_rubric_rendering` | Phase 36 already decoupled `rubric` from `desc_signature`; these prove Phase 37's `desc_signature` restyling did not reach back into the rubric handler |
| 8 | Anchor gates | `tests/test_desc_container_propagated_target_render_gate.py`; `tests/test_desc_signature_anchor_render_gate.py` | Prove the `[#metadata(none) <label>]` anchor-emission loop in `depart_desc_signature`, explicitly documented as byte-unchanged by contract §3, really is unchanged |

---

## 5. Blast-radius census — finalised (SC#5)

`37-TEST-CENSUS.md` (written by `37-04` in Wave 2, re-measured against the current tree in this
plan's Task 2) already carries a predicted-vs-owning-plan table for its 10 Bucket-A node ids. Cross-
checked against every plan's own SUMMARY: **all 10 flipped exactly as predicted**, at the plan named
as the owner (6 at `37-06`, 4 at `37-07` — matching `37-TEST-CENSUS.md`'s "Owning plan" column
exactly; see the requirement verdict table in §2 above for the individual commits).

Bucket C's 4 conditional node ids (`tests/test_desc_bodyless_concat_render_gate.py` and the three
`test_desc_signature_line_*_linebreak` functions) were re-verified GREEN after `37-05` (per
`37-05-SUMMARY.md`'s "Set-Difference Verification") and stayed GREEN through every subsequent wave,
confirmed again in `37-09-GATE-EVIDENCE-09.md` §5.4's "Named falsifiers" run.

### 5.1 golden.typ reconciliation

`37-04` (Wave 2) hand-derived `golden.typ`'s five `desc_signature`-driven blocks and discovered its
own plan text's "seven changed lines" claim was arithmetically wrong (the plan's own block-by-block
description already implies 9: one 2-line `connect` block + three 2-line `compile` blocks + one
1-line `--sep` block = 9) — reported rather than silently forced to 7 (`37-GATE-EVIDENCE-04.md` §1).
`37-07` (Wave 4) turned the byte-identity gate GREEN with **zero reconciliation** — the golden file
itself was untouched by that plan, and the fresh build agreed with the Wave-1 hand-derivation
exactly, which is the phase's own evidence that the 9-line hand-derivation was correct on first
build. `37-09` (Wave 5) then touched `golden.typ` again — mechanically substituting only the wrapper
text on the same five signature lines (`block(above: 0pt, below: 0pt, sticky: true, ...)` →
`block(sticky: true, ...)`), confirmed via `git diff` to be confined to exactly those five lines with
zero other bytes changed.

### 5.2 The `EXPECTED_PAGE_COUNT_PRE_PHASE` re-pin (6 → 7) — a re-derived baseline, not a moved goalpost

`tests/test_signature_page_boundary_render_gate.py`'s `EXPECTED_PAGE_COUNT_PRE_PHASE` was originally
measured (Wave 1, `37-03`) against the truly untouched translator at 6 pages, on a fixture
deliberately built with almost no page slack (`PAGE_HEIGHT_PT=200pt`, `PAGE_MARGIN_PT=20pt`) so the
pre-Phase-37 SIG-09 split defect would reproduce. `37-09` discovered, while restoring correct
vertical spacing (see §5.3), that the boundary signature and its `sticky: true`-bound body no longer
fit in the remaining room on page 6 — `sticky: true`'s keep-together then correctly pushes the whole
unit onto page 7, together, one page later (`test_primary_signature_and_body_share_a_page` stays
GREEN throughout — the unit lands together, just later).

This was investigated, not absorbed: `37-09` swept `above`/`below` from 0em to 1.2em against the real
fixture (real `sphinx-build` + real `typst.compile()`, same tight page geometry) and found the page
count only crosses from 6 to 7 between 0.85em and 0.9em of added spacing — a **step specific to how
much room this one `sticky: true` keep-together unit needs on a deliberately adversarial page
height**, not a per-signature inflation that would compound across a real, non-adversarial document.
Independently corroborated by the orchestrator on normal A4 geometry: the wrapper fix changes the
typography fixture's page count 4→4 and the break-and-arrow fixture's page count 3→3 — unchanged.

The baseline was re-pinned from 6 to 7 with the full reasoning recorded in both the constant's own
code comment and the test's docstring (`76324bf`, 37-09 Task 2) — a real re-measurement of a pinned
integration threshold, not a golden regenerated from output to hide a regression (SIG-01's
hand-derivation prohibition targets typographic string goldens, not integer page-count regression
thresholds, and this constant was itself originally established the same way: a real compile and
measure).

**Naming nit, not left unmentioned:** the constant is still named `EXPECTED_PAGE_COUNT_PRE_PHASE` but
now holds the **post**-phase (post-`37-09`) value. The comment directly above it records the full
history (why 6 was originally measured, why it moved to 7), so the value is not undocumented — only
the identifier's own name no longer describes what it holds. Filed as a todo rather than renamed in
this plan (renaming touches a test file outside `37-08`'s `files_modified`):
`.planning/todos/pending/2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md`.

### 5.3 `37-09`'s own additionally-measured blast radius (the census's honest miss)

`37-TEST-CENSUS.md`'s Bucket A/B/C tables, written in Wave 2, could not have predicted `37-09` — it
did not exist yet; it is a gap-closure plan the orchestrator authored **after** the post-merge gate
following Wave 3 caught the wrapper-overlap defect. `37-09`'s own measured blast radius (5 files,
recorded in `37-SPACING-FINDING.md` §4 and re-confirmed in `37-09-PLAN.md`'s frontmatter) was:

| File | Predicted by `37-TEST-CENSUS.md`? |
|---|---|
| `typsphinx/translator.py` | N/A — production code, not a test census row |
| `.planning/phases/37-signature-typography-the-desc-family/37-EMISSION-CONTRACT.md` | N/A — planning doc |
| `tests/test_signature_typography_gate.py` | Yes — already Bucket A (row A1-A4 family), correctly predicted to be signature-wrapper-sensitive |
| `tests/test_signature_page_boundary_render_gate.py` | Yes — already Bucket A equivalent (SIG-09 fixture, `37-03`'s own gate), but the SPECIFIC re-pin of `EXPECTED_PAGE_COUNT_PRE_PHASE` (§5.2) was not itself predicted — only the fixture's general sensitivity to the wrapper was |
| `tests/test_translator.py` | Yes — already Bucket A (rows A1-A4) |
| `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` | Yes — already Bucket A (row A10) |
| `tests/fixtures/inline_math_pdf_text_mitex.golden.txt` | **No** — genuinely unpredicted |
| `tests/fixtures/inline_math_pdf_text_native.golden.txt` | **No** — genuinely unpredicted |

**The two Phase 34 PDF-text goldens are the census's honest miss.** They were never in Bucket A, B,
or C — `37-TEST-CENSUS.md`'s own methodology (reading every assertion in the 13 files named in
`37-CONTEXT.md`'s starting blast-radius list) had no reason to include them, because they are Phase
34's MATH-02 assets, structurally unrelated to the `desc_signature` family at the time the census was
written. They were affected for a genuinely structural reason discovered only by `37-06`'s
implementation and root-caused by `37-09`: pre-Phase-37, `desc_signature`'s `strong({...})` wrapper
was an INLINE Typst call, so a confval signature could join the same visual line as adjacent content;
Phase 37 (from Wave 3 onward) wraps it in a genuine `block(...)`, an intrinsically block-level
construct that can never again share a visual line with a neighbor, regardless of spacing amount.
This is recorded here rather than silently folded into Bucket A after the fact — a census that was
wrong in a documented way is more useful than one silently corrected. `37-09` handled it directly
(hand-updating both goldens surgically, with the pre-fix baselines preserved verbatim in
`37-GATE-EVIDENCE-09.md` §4.3) rather than leaving it for this plan to discover fresh.

---

## 6. Prohibitions and edge-coverage accounting (re-verified)

`37-01-PLAN.md`'s `must_haves.prohibitions` block records four recalled prohibitions, all authored
descriptor-less (no `check_*` scalar), so each disposes flagged-unverified by construction — none was
silently dismissed. Re-read directly for this plan:

1. SIG-01: MUST NOT copy the new translator's own output into a golden/expected string. Verified
   throughout the phase by construction — every RED assertion across all four Wave-1 evidence files
   and `37-GATE-EVIDENCE-09.md` states its derivation source (a contract section), never "ran the
   code and pasted the result." `37-09`'s own Task 2 re-states this explicitly per site.
2. SIG-09 (from `37-09`'s own prohibitions block, added mid-phase): MUST NOT restore vertical spacing
   by dropping `sticky: true`. Verified — `37-09`'s fix drops only `above: 0pt, below: 0pt`;
   `sticky: true` survives byte-for-byte (confirmed in `37-GATE-EVIDENCE-09.md` §3.1).
3/4. The two remaining `37-01`-authored prohibitions (recalled, descriptor-less) are re-read here and
   found to still apply with no new information changing their disposition — flagged-unverified is
   the correct final state; nothing in Waves 2-5 discharged or contradicted them.

The 17-edge accounting table in `37-08-PLAN.md`'s own `<edge_coverage_accounting>` block (11
`covered`, 1 `backstop`, 5 `unresolved`/flagged) was authored by reading `37-01-PLAN.md`..`37-03-PLAN.md`
directly and matches the probe's `applicable: 17` total; re-checked here against the same four plans
and found unchanged — no edge was silently dropped between planning and this closeout.

---

## 7. Pointers to the primary per-wave evidence

- `37-GATE-EVIDENCE-01.md` — SIG-01..05 RED capture (Wave 1, `37-01`)
- `37-GATE-EVIDENCE-02.md` — SIG-06/SIG-08/D-11 RED/CONTROL capture (Wave 1, `37-02`)
- `37-GATE-EVIDENCE-03.md` — SIG-07/SIG-09 geometric RED capture (Wave 1, `37-03`)
- `37-GATE-EVIDENCE-04.md` — golden.typ + pre-existing test migration RED capture (Wave 2, `37-04`)
- `37-GATE-EVIDENCE-09.md` — the wrapper spacing gap-closure fix, corrected measurement, and the
  first fully-green whole-suite result of the phase (Wave 5, `37-09`)

Each stays the primary record for its own wave; this file does not copy their verbatim pytest output.

---

*Phase: 37-signature-typography-the-desc-family*
*Consolidated: 2026-08-01, by 37-08 Tasks 1-2*
