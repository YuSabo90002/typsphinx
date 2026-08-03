# Phase 38 Plan 01 — GATE-01 RED Evidence (IND-01..IND-05, FLD-01, D-04, D-11)

**Captured:** 2026-08-01
**Plan:** 38-01 (Wave 1)
**Not named `38-VERIFICATION.md`** deliberately — that filename is reserved for
the verify stage and is overwritten wholesale; this evidence file must survive
independently of any later `/gsd-verify-work` run and is merged into
`38-GATE-EVIDENCE.md` by a later closeout plan alongside its Wave-1 siblings.

## Commit SHA the RED was captured against

`typsphinx/` is **completely untouched** by plan 38-01 (`git diff --stat HEAD --
typsphinx/` is empty at every point in this plan's execution). The RED below
was captured at:

- **HEAD at capture time:** `d4251e70a830c2f088fca9670065908326f7e2b3` (`test(38-01):
  add IND/FLD-01 gate module with hand-derived expectations`) — short hash `d4251e7`
- **Previous commit (this plan's fixture):** `41dca3f` (`test(38-01): add
  IND/FLD-01 nesting fixture`)
- **Last commit that touched `typsphinx/`:** `76324bf` (`fix(37-09): drop the
  zeroed above/below override on the signature wrapper`) — pre-dates this
  plan entirely; `visit_desc_content`/`depart_desc_content` and
  `visit_field_list`/`depart_field_list`'s pad step are all still
  `pass`/untouched at this SHA.
- **Worktree base (plan start):** `c86afc5d9e254a0ee5253f46bcaf7159baa98545`

## Intentionally-RED node ids (6)

Enumerated explicitly so a later wave can verify by **set difference**, never
by count:

```
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ind01_structural_wrapper_token_and_position
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ind04_structural_shared_step_value_at_new_sites
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_fld01_empty_ind01_empty_bodyless_confval_siblings
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind01_body_indented_past_signature
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind02_nested_body_deeper_and_resumed_body_returns
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_fld01_field_list_deeper_than_method_body
```

**CONTROL-GREEN (7), expected to PASS in every state (pre- and post-phase):**

```
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ind04_structural_single_indent_literal_source_grep
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ind04_d04_block_quote_not_converted
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ind04_empty_no_desc_no_field_list_region_has_no_wrapper
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ordering_determinism_two_builds_byte_identical
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind03_nested_signature_equals_parent_body_column
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind05_sibling_top_level_returns_to_margin
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_d11_sig09_page_boundary_signature_body_and_continuation_indent
```

### Per-RED cause (one sentence each)

| Node id (short form) | Property that failed |
|---|---|
| `test_ind01_structural_wrapper_token_and_position` | The body wrapper's opening token `pad(left: 2.5em, {` is **absent** from the emitted `.typ` — `visit_desc_content` is still `pass`. |
| `test_ind04_structural_shared_step_value_at_new_sites` | `pad(left: 2.5em, {` occurs **0** times (expected ≥2, one for `desc_content` and one for `field_list`) — neither new consumer site exists yet. |
| `test_fld01_empty_ind01_empty_bodyless_confval_siblings` | The body-less confval's `desc_content` wrapper-pair count is **0** (expected ≥1) — the break count between siblings is already correct, but the wrapper itself does not exist. |
| `test_ind01_body_indented_past_signature` | The class body's leading column (**0**) is not strictly greater than the class signature's own column (**0**) — nothing is indented yet. |
| `test_ind02_nested_body_deeper_and_resumed_body_returns` | The nested method's body column (**0**) is not strictly greater than the class body's own column (**0**) — nothing is indented yet (the assertion's second half, the resumed-body equality, is already true and does not fail). |
| `test_fld01_field_list_deeper_than_method_body` | The field-list line's column (**0**) is not strictly greater than the method body's own column (**0**) — the field-list `pad` step does not exist yet. |

### None of the above is a compile failure

Every RED above is a **structural token-count / column-comparison mismatch on
already-compiled output** — `assert <count/column comparison>` — **never** a
`typst.TypstError` or any other compile-time exception. Confirmed by direct
count:

```
$ grep -c "TypstError" <verbatim pytest output below>
0
```

The compile step itself, run standalone against the SAME (untouched)
translator immediately before capturing this evidence:

```
$ uv run python -m sphinx -b typst tests/fixtures/desc_content_indent_render_gate /tmp/.../compile_check
...
writing output... [index] done
build succeeded.
sphinx-build exit status: 0

$ uv run python -c "import typst; typst.compile('.../index.typ', output='.../index.pdf')"
typst.compile() exit: success, no exception raised
typst.compile() python exit status: 0
```

`sphinx-build -b typst` exits **0** and `typst.compile()` raises **no
exception** — the SAME build every RED test above reads from. Milestone
invariant #4's structural-RED redefinition is satisfied: this phase's
defects compile fine today; the RED is entirely about missing tokens and
equal-instead-of-unequal columns.

## Verbatim `uv run pytest tests/test_desc_content_indent_render_gate.py -v` output

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a027db0e3eaadff90/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a027db0e3eaadff90
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 13 items

tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ind01_structural_wrapper_token_and_position FAILED [  7%]
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ind04_structural_shared_step_value_at_new_sites FAILED [ 15%]
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ind04_structural_single_indent_literal_source_grep PASSED [ 23%]
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ind04_d04_block_quote_not_converted PASSED [ 30%]
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ind04_empty_no_desc_no_field_list_region_has_no_wrapper PASSED [ 38%]
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_fld01_empty_ind01_empty_bodyless_confval_siblings FAILED [ 46%]
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ordering_determinism_two_builds_byte_identical PASSED [ 53%]
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind01_body_indented_past_signature FAILED [ 61%]
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind02_nested_body_deeper_and_resumed_body_returns FAILED [ 69%]
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind03_nested_signature_equals_parent_body_column PASSED [ 76%]
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind05_sibling_top_level_returns_to_margin PASSED [ 84%]
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_fld01_field_list_deeper_than_method_body FAILED [ 92%]
tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_d11_sig09_page_boundary_signature_body_and_continuation_indent PASSED [100%]

=================================== FAILURES ===================================
_ TestDescContentIndentStructuralGate.test_ind01_structural_wrapper_token_and_position _
E       AssertionError: IND-01: expected the desc_content body wrapper's opening token 'pad(left: 2.5em, {' somewhere in the emitted .typ -- not found (visit_desc_content is still `pass` pre-phase).
E       assert 'pad(left: 2.5em, {' in '// Essential package imports\n...'
tests/test_desc_content_indent_render_gate.py:278: AssertionError

_ TestDescContentIndentStructuralGate.test_ind04_structural_shared_step_value_at_new_sites _
E       AssertionError: IND-04: expected the shared indent step's value to appear at BOTH the desc_content wrapper and the field_list wrapper (at least 2 occurrences of 'pad(left: 2.5em, {') -- pre-phase neither site exists yet; got 0 occurrence(s).
E       assert 0 >= 2
tests/test_desc_content_indent_render_gate.py:316: AssertionError

_ TestDescContentIndentStructuralGate.test_fld01_empty_ind01_empty_bodyless_confval_siblings _
E       AssertionError: FLD-01/IND-01 empty: expected at least one desc_content wrapper pair for the first body-less confval sibling -- pre-phase none exists:
E         ind_bodyless_confval_one"))}))
E         [#metadata(none) <index:confval-ind_bodyless_confval_one>]
E         strong(text("Type") + text(": "))
E         text("str")
E
E         text("  ")
E         strong(text("Default") + text(": "))
E         raw("\"a\"")
E
E         parbreak()
E         block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("
E       assert 0 >= 1
tests/test_desc_content_indent_render_gate.py:419: AssertionError

_____ TestDescContentIndentPdfGate.test_ind01_body_indented_past_signature _____
E       AssertionError: IND-01: expected the class body's leading column (0) to be strictly greater than the class signature's own column (0).
E       assert 0 > 0
tests/test_desc_content_indent_render_gate.py:492: AssertionError

_ TestDescContentIndentPdfGate.test_ind02_nested_body_deeper_and_resumed_body_returns _
E       AssertionError: IND-02: expected the nested method's body column (0) to be strictly greater than the class body's own column (0).
E       assert 0 > 0
tests/test_desc_content_indent_render_gate.py:520: AssertionError

__ TestDescContentIndentPdfGate.test_fld01_field_list_deeper_than_method_body __
E       AssertionError: FLD-01: expected the field-list line's column (0) to be strictly greater than the method body's own column (0).
E       assert 0 > 0
tests/test_desc_content_indent_render_gate.py:601: AssertionError
=========================== short test summary info ============================
FAILED tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ind01_structural_wrapper_token_and_position
FAILED tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_ind04_structural_shared_step_value_at_new_sites
FAILED tests/test_desc_content_indent_render_gate.py::TestDescContentIndentStructuralGate::test_fld01_empty_ind01_empty_bodyless_confval_siblings
FAILED tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind01_body_indented_past_signature
FAILED tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_ind02_nested_body_deeper_and_resumed_body_returns
FAILED tests/test_desc_content_indent_render_gate.py::TestDescContentIndentPdfGate::test_fld01_field_list_deeper_than_method_body
========================= 6 failed, 7 passed in 1.58s ==========================
```

(Long inline representations of the full emitted `.typ` inside pytest's own
`assert ... in <value>` diff output are elided above with `...` for
readability; the full, unedited output was captured to
`/tmp/.../pytest_output.txt` during this session and every line quoted here
is copied verbatim from it.)

## SC#4 discovery grep (milestone invariant #6)

Contract §1.1 recorded this at **planning time** (2026-08-01). Re-run here at
**discovery time** for this plan, repo-wide over `typsphinx/`, per invariant
#6's "checked by a repo-wide grep at discovery time" requirement:

```
$ awk '$0 !~ /^[[:space:]]*#/ {print NR": "$0}' typsphinx/translator.py | grep -E '[0-9]+(\.[0-9]+)?em\b'
29: SHARED_INDENT_STEP = "2.5em"
```

(The `awk` form is used instead of the contract's literal
`grep -vE '^[[:space:]]*#' | grep -nE ...` pipeline because piping `grep -v`
into `grep -n` renumbers lines against the **filtered** stream, not the
original file — reproduced this session: that literal pipeline reports the
same single match at filtered-line 20, which does **not** match the
source file's real line 29. The `awk` form preserves original `NR` while
still skipping comment lines, and is the form whose line number is directly
checkable against `typsphinx/translator.py:29`.)

**Result: exactly ONE match, unchanged from contract §1.1's planning-time
run.** Disposition:

| Match | File:line | Is it a desc / field-list / block-quote indent? |
|---|---|---|
| `SHARED_INDENT_STEP = "2.5em"` | `typsphinx/translator.py:29` | Yes — the one definition. Its two Phase-38 consumers (`desc_content`'s wrapper, `field_list`'s wrapper) do not exist yet, so they contribute no additional literal (they will spell `SHARED_INDENT_STEP`, not a new number, once implemented — contract §1.1/§1.2). |

**No difference from the planning-time table.** SC#4's checkable property —
"a repo-wide grep over `typsphinx/` finds no second independent indent
literal at those sites" — is confirmed still true at this plan's close, and
this plan itself introduces zero new sites (it touches no file under
`typsphinx/`).

## Pre-phase left-edge column baseline

Every marker line the gate module compares, measured via `pypdf`
`extraction_mode="layout"` against the SAME pre-phase compiled PDF used by
the test run above (`document has 10 pages`):

| Marker | Page (0-indexed) | Column | Role |
|---|---|---|---|
| `class IndFldNestOuterClass` | 2 | 0 | class signature — IND-01/IND-05 baseline |
| `Outer class body first paragraph.` | 2 | 0 | class body first paragraph — IND-01/02/03 |
| `ind_fld_nest_inner_method(value)` | 2 | 0 | nested method signature — IND-03 |
| `Inner method body paragraph.` | 2 | 0 | nested method body — IND-02/FLD-01 |
| `Parameters:` | 2 | 0 | field-list line inside the nested method — FLD-01 |
| `Outer class body resumes here` | 3 | 0 | class body resumed paragraph — IND-02 |
| `ind_fld_nest_sibling_toplevel_function(x)` | 3 | 0 | sibling top-level function signature — IND-05 |
| `class IndPageBoundaryClass` | 6 | 0 | page-boundary class signature — D-11/SIG-09 |
| `ind_page_boundary_class_body_first_line_sentinel` | 6 | 0 | page-boundary body first line — D-11/SIG-09 |
| `ind_page_boundary_class_body_continuation_sentinel` | 8 | 0 | page-boundary body continuation — D-11/SIG-09 |

**Every marker above is flush at column 0 pre-phase** — consistent with
`visit_desc_content`/`depart_desc_content`/`visit_field_list`'s pad step all
being `pass`/untouched. This is the baseline the post-phase run (once
38-05/38-06 land) must diff against: per contract §2.3's measured table
(2.5em / 27.5pt step at this project's 11pt body), the post-phase columns are
expected to move from the flat `{0, 0, 0, 0, 0, 0, 0}` pattern above to a
pattern with real steps between signature/body/nested-body/field-list, while
the two equality properties (IND-03's `method_sig_col == class_body_col`,
IND-05's `sibling_sig_col == class_sig_col`) and D-11's cross-page equality
must all still hold — just no longer trivially, at `0 == 0`, but at their
real, non-zero shared values.

## `pypdf` layout-mode vs per-glyph position API — side-by-side comparison

For a marker line that pre-phase already carries a genuine **non-zero**
indent (Typst's own `quote(block: true, ...)` default on the block-quote
construct, D-04, measured 11.0pt in `38-EMISSION-CONTRACT.md` §1.2) — chosen
deliberately over a flush-left (column-0) marker so the two extraction
techniques' behavior actually diverges observably:

```
Marker: 'A block-quoted sentinel paragraph.' on page 8

layout-mode (extraction_mode="layout"):
  line: '  A block-quoted sentinel paragraph.'
  leading column: 2

visitor_text (per-glyph position API):
  results: [('A block-quoted sentinel paragraph. ', 0.0, 0.0)]
```

**Layout-mode correctly reconstructs a non-zero leading indent (column 2,
the text-grid-approximated form of the block quote's real 11.0pt inset).
The per-glyph position API reports `x=0.0, y=0.0` regardless of the glyph's
real position on the page** — confirming 38-RESEARCH.md Pattern 2's finding
and Phase 37's own prior documentation of the same limitation: `visitor_text`
is unusable on this project's Typst-generated PDFs, and every left-edge
assertion in `tests/test_desc_content_indent_render_gate.py` uses
layout-mode exclusively, never `visitor_text`.

## Reclassified non-regression controls (GREEN pre-phase, not RED)

This plan's acceptance criteria (38-01-PLAN.md Task 2) named IND-01, IND-02,
IND-03, IND-05 and FLD-01 as the properties expected to surface as FAILED.
Measured against the real untouched translator, **IND-03 and IND-05's own
compiled-PDF assertions come out GREEN pre-phase**, along with several purely
structural controls. Per the plan's own Task 3 instruction ("If any
assertion in the module comes out GREEN against the untouched translator, do
not adjust it into red... reclassify it... as a non-regression control"),
each is recorded here rather than silently omitted:

| Test | Why it is GREEN pre-phase | Why it must stay green post-phase |
|---|---|---|
| `test_ind03_nested_signature_equals_parent_body_column` | Both the class body (col 0) and the nested method's own signature (col 0) are flush — `0 == 0` is trivially true. | Post-phase both must land at the SAME non-zero column (contract §2.3: 47.5pt each). The equality assertion exists specifically to catch a NAIVE implementation that over-indents the nested signature to match the nested body's own column instead — the assertion's real job starts once real numbers are on both sides. |
| `test_ind05_sibling_top_level_returns_to_margin` | Both the top-level class signature (col 0) and the sibling function signature (col 0) are flush — `0 == 0` is trivially true. | D-01: there is no depth counter; depth cannot leak because the `pad` wrapper closes structurally. Post-phase this assertion is the operational proof that a real page-margin column (not merely "no counter exists") is what both signatures land on. FLAGGED per `must_haves.truths`: IND-05's edge-probe classification was left unresolved at plan time — this is the assertion the plan committed to as IND-05's operational cover. |
| `test_d11_sig09_page_boundary_signature_body_and_continuation_indent` | Phase 37's `block(sticky: true, ...)` already keeps the page-boundary signature and its body's first line on the same page; neither line carries any indent yet, so the cross-page column equality is `0 == 0`. | D-11 (binding): the wrapper must not fight `sticky: true`. This assertion must be RE-VERIFIED once the `pad` wrapper exists — a wrapper change is exactly what could break the keep-together/indent-persistence property, so it is asserted here, not assumed. |
| `test_ind04_structural_single_indent_literal_source_grep` | SC#4's grep (above) already finds exactly one `em`-literal, `SHARED_INDENT_STEP` itself. | Neither §2's nor §3's target shape introduces a new numeric literal (both spell `SHARED_INDENT_STEP`) — this must stay true through 38-05/38-06. |
| `test_ind04_d04_block_quote_not_converted` | `visit_block_quote`/`depart_block_quote` are untouched by this phase (D-04) — `quote(block: true, {` already exists and the forbidden composed form already does not. | D-04 is binding and explicitly "not to be re-opened at verify time." |
| `test_ind04_empty_no_desc_no_field_list_region_has_no_wrapper` | The no-desc/no-field-list section has nothing to wrap, pre- or post-phase. | The region's doctree content never changes; there is structurally nothing for a future `pad` wrapper to attach to there. |
| `test_ordering_determinism_two_builds_byte_identical` | Neither Sphinx nor this translator introduces non-determinism. | Must hold for any translator state, pre- or post-phase — a basic build-reproducibility invariant, not a per-requirement property. |

No assertion in this module was weakened, narrowed, or deleted to reach this
result — every GREEN above is the assertion **exactly as specified** in
38-01-PLAN.md Task 2, evaluated honestly against the real untouched
translator.

## Discovery: two pre-existing defects found while building this plan's fixture

Recorded in full in `tests/fixtures/desc_content_indent_render_gate/conf.py`
and `index.rst`'s own comments; summarized here since they materially shaped
Task 1's "Table-Cell CONTROL" construct and are relevant context for whoever
next touches a table-cell-adjacent fixture in this phase:

1. **`depart_desc_signature`'s two `self.body.append(...)` calls**
   (`typsphinx/translator.py:5051, 5053`, Phase 37) bypass table-cell
   routing unconditionally — reproduced with a minimal repro (a single bare
   `py:attribute::`, no id, no fields, no body) inside a `list-table` cell:
   the Typst compile aborts with `expected semicolon or line break`
   regardless of the signature's own content. Out of Phase 38's scope
   (`depart_desc_signature` is not in `38-CONTEXT.md`'s in-scope handler
   list) and this plan does not touch `typsphinx/`.
2. **The `field_list` family's five `self.body.append(...)` sites**
   (`38-EMISSION-CONTRACT.md` §3.1: `depart_field_list`,
   `depart_field`, `visit_field_name`, `depart_field_name`,
   `depart_field_body`) independently hit the same class of defect — a
   minimal `:FieldOne: value` / `:FieldTwo: value` field list inside a
   `list-table` cell also aborts the compile. These sites ARE in Phase 38's
   overall scope (per §3.1 and `38-CONTEXT.md`'s in-scope list) but are
   owned by a later plan (38-06 per the phase's artifact-ownership table),
   not this one.

Both findings mean "a desc or a field list inside a table cell" cannot
currently be exercised as a live, compiling fixture construct — the
Table-Cell CONTROL section was changed to plain, desc-free content so
Task 1's own compile-success acceptance criterion is met, and this finding
is carried forward here rather than silently worked around. A future plan
(38-05/38-06, once the underlying sites route through `self.add_text`) can
extend this fixture with the originally-intended desc/field-list-in-table-cell
falsifier.

A third, unrelated discovery: a docutils comment (`.. `) immediately followed
by an indented block with no intervening visible paragraph gets silently
swallowed as comment continuation, dropping the following content entirely
(reproduced with a minimal block-quote-after-comment repro). Fixed in the
fixture by inserting an intro paragraph before the block quote; not a
translator defect (a docutils/RST parsing property), so nothing to log as
out-of-scope.
