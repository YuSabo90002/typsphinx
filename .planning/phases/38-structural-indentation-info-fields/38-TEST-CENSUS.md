# Phase 38 Plan 04 — SC#5 Test Census

**Produced:** 2026-08-01, by `38-04-PLAN.md` Task 1 and Task 2.
**Method:** every file named in this plan's `read_first` list was opened and its actual assertions
read — none of the rows below were produced by grepping `desc_content`/`field_list`/`literal_strong`
as node-name strings and trusting the match. `38-EMISSION-CONTRACT.md` §7 is the **starting** input;
per D-14, `37-TEST-CENSUS.md`'s own *content* is explicitly NOT inherited here — only its bucket shape
and its "disagreement between grep-by-name and read-the-assertion" evidence convention are mirrored.
Where reading disagreed with §7's starting list, this census is authoritative and the disagreement is
recorded in its own section below (there are several, in both directions — see "Disagreement").

---

## Bucket A — asserts on bytes this phase changes, WILL BREAK

| # | File:Line(s) | Test function | Current expected string (verbatim) | Driving contract section | Owning plan |
|---|---|---|---|---|---|
| A1 | `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` (lines 26-31, 36-45, 59-61), consumed by `tests/test_desc_rubric_decoupling_render_gate.py:267` `test_emitted_typ_is_byte_identical_to_golden` | full byte-identity of `golden.typ` against a fresh `-b typst` build | Every one of the fixture's three `desc_content` bodies (`connect`'s, the sibling-signature `compile`'s, and `--sep`'s) currently follows its signature block with no wrapper at all — e.g. `par({text("Connect to ")…})` sits flush after `block(sticky: true, …)` with only a `[#metadata(none) <index:connect>]` anchor between them. Post-phase each gains `pad(left: 2.5em, {` before and `})\n` after. | §2 (body wrapper) | 38-05 |
| A2 | `tests/test_desc_rubric_decoupling_render_gate.py:182-239` `TestDescRubricDecouplingRenderGate::test_desc_signature_and_rubric_do_not_delegate_to_visit_strong` | `RETAINED_DELEGATION_METHODS = ("visit_literal_strong", "depart_literal_strong")` must each still call `self.visit_strong`/`self.depart_strong` (`assert delegating_calls != []`, line ~221), and `DUMMY_STRONG_LITERAL` ("`dummy_strong = nodes.strong()`") must occur **exactly 2** times in `translator.py` (line 234) | D-09 removes the dummy-node delegation from `literal_strong`/`literal_emphasis` entirely — the two `RETAINED_DELEGATION_METHODS` assertions and the `== 2` count both invert to their opposite once §5's replacement (`strong(raw(...))`/`emph(raw(...))`, no delegation) lands. This is the exact "over-reach guard" SC#1 currently protects, and Phase 38 is now the change that legitimately trips it — the guard's OWN assertions must be rewritten in the same commit, not just the code under test. | §5 (D-05, D-09) | 38-07 |
| A3 | `tests/fixtures/inline_math_pdf_text_mitex.golden.txt` (all 41 lines, byte-for-byte) and `tests/fixtures/inline_math_pdf_text_native.golden.txt` (mirror), both consumed by `tests/test_inline_math_after_text_render_gate.py:496` `test_block_math_pdf_text_is_invariant_across_the_math02_fix` | full byte-for-byte pypdf-extracted-text equality against the committed baseline | Construct C's `math_inline_default` confval (golden lines 16-22 / 19-22) is exactly the shape §2+§3 reach: a `desc` whose `desc_content` contains a collapsed-inline `field_list` (`:type:`/`:default:`) **and** a following normal paragraph ("A description paragraph so the confval also exercises…"). Post-phase this body gets a 27.5pt `pad` (desc_content) and the field list inside it gets a further nested 27.5pt `pad` (field_list) — 55pt total for the field list, 27.5pt for the trailing paragraph. That paragraph's second line ("…and normal-paragraph \| path.") already wraps close to the column edge in the pre-phase baseline; narrowing the available width by 27.5–55pt is very likely to move where pypdf's extracted line-break falls, which this test compares character-for-character. See "Reached-or-not-reached" discussion below — this is the exact class of miss `37-09` found in the SAME two files. | §2, §3 | 38-05 / 38-06 jointly (38-06 is the later, deeper touch — treat it as the closing owner) |
| A4 | `tests/test_field_list_in_list_item_render_gate.py:113-181` `TestFieldListInListItemRenderGate::test_typstpdf_separates_field_list_in_list_item_and_produces_pdf` | `typ_text.index('par({text("Test Author")})')` (line 190) and everything downstream of it in the same function (`version_strong_idx`, the CR-01 `between_author_and_version`/`between_nested_fields` checks) | The fixture's top-level `:Author: Test Author` / `:Version: 1.0.0` field list is a **genuine RST field list** (not a confval directive-option collapse) — its own test comment (line 185-186) confirms both fields are "paragraph-wrapped (block field bodies)". This is exactly the single-`nodes.paragraph`-child shape §4.2 reclassifies: post-phase, `visit_paragraph`/`depart_paragraph` skip the `par({`/`})` wrapper for this field body, so the literal substring `'par({text("Test Author")})'` no longer exists in the emitted `.typ` at all — the `.index()` call raises `ValueError` and the whole test function errors before any of its later assertions run. | §4 (D-07, D-08) | 38-06 |

**Reached-or-not-reached decision for the two Phase-34 PDF-text goldens (required by this plan's `must_haves`):** REACHED. Row A3 above is the explicit finding. Unlike Phase 37's version of this same miss (a document-wide `block()`-wrapping side effect nobody predicted until `37-06` landed), this phase's own emission contract (§7's starting list) never named these two files at all — they were found here only because `read_first` explicitly pointed at them and Construct C's confval was read in full rather than assumed safe by analogy with `test_confval_field_spacing_render_gate.py` (row B1 below, which stays green for a different, contract-guaranteed reason — see the Disagreement section). Migration method is **re-measurement, not hand-derivation**: a PDF-extracted-text golden is not a `.typ`-source byte sequence this document can specify in advance the way §2-§6 specify `.typ` bytes; it is the output of a real Typst layout pass. The correct methodology, mirroring `37-09`'s own precedent for these same two files, is: rebuild with the phase's code once both 38-05 and 38-06 have landed, diff the extracted text against the committed baseline, and manually confirm the diff is *solely* the predicted line-wrap consequence of narrower available width before accepting the new baseline — never accept a re-capture without that manual confirmation step (this is the PDF-text analogue of the `golden.typ` hand-derivation rule below, not an exception to it).

---

## Bucket B — mentions the node family, asserts on something this phase does not change, MUST STAY GREEN

| File / test | Why it's safe (read, not assumed) |
|---|---|
| `tests/test_translator.py::test_desc_signature_rendering` (3354), `test_desc_with_annotation_and_name` (3390), `test_desc_parameterlist` (3420), `test_desc_signature_line_multiline_emits_one_linebreak` (3466), `test_desc_signature_line_single_line_emits_no_linebreak` (3506), `test_desc_signature_line_resets_per_signature` (3532) | None of these six synthetic doctrees construct a `desc_content` node at all (only `desc`/`desc_signature`/children) — `visit_desc_content`/`depart_desc_content` never fire, so §2's wrapper is structurally unreachable regardless of what it emits. |
| `tests/test_translator.py::test_field_list_rendering` (3579) | Standalone `field_list`/`field`/`field_name`/`field_body(paragraph("description text"))`, so BOTH §3 (field_list wrapper) and §4 (single-paragraph field body reflow) fire mechanically — but the test's own assertions (`'strong(text("Parameters")' in output or "Parameters" in output`, `"description text" in output`) are plain substring checks that name neither `pad(` nor `par(`. The wrapper adds bytes elsewhere in the string; the single-paragraph reflow changes HOW `"description text"` is emitted (drops the `par({`/`})` around it) but not THAT the substring `"description text"` appears. Both survive unchanged. |
| `tests/test_translator.py::test_full_api_description_structure` (3638) | Same reasoning as the row above, extended: this synthetic tree HAS a `desc_content` (with its own paragraph, "Builder class for Typst output.") containing a nested `field_list` whose single field body is again one `nodes.paragraph` ("app - Sphinx application"). §2, §3, AND §4 all mechanically fire. All four of the test's assertions are substring checks (`'strong(raw("class"))' in output and "TypstBuilder" in output`; `"Builder class for Typst output." in output`; `'strong(text("Parameters")' in output or "Parameters" in output`; `"app - Sphinx application" in output`) — none reference `pad(`, `par(`, or byte-adjacency, so all four survive the wrapper and the reflow unchanged. **Grep-by-name would flag this test as signature-adjacent AND field-list-adjacent (the file `desc_content += field_list` shape is exactly what §7's starting table cites test_translator.py for); reading shows every one of its four assertions is written loosely enough to survive.** |
| `tests/test_translator.py::test_rubric_rendering` (3608) | See Must-not-touch section — Phase 39 territory, not Phase 38's to edit, and not reachable by §2-§6 in any case (`rubric` is not `desc_content`). |
| `tests/test_translator.py::test_title_reference_rendering` (3623) | `title_reference`/`emph({text(...)})` — unrelated node, untouched handler. |
| `tests/test_confval_field_body_render_gate.py` (both confvals: `html_title`'s plain body paragraph, `html_sidebars`' collapsed `:type:`/`:default:` fields plus its own body paragraph, and the def-list-in-list-item construct) | Every `:type:`/`:default:` pair in this fixture is written immediately after the directive header with no blank line — docutils' directive-option collapsing form, contract §4.1's explicitly-named "confval `:default:` written on the field's own line" case — which §4.3 point 3 guarantees stays **byte-identical**, because the fix only reclassifies the paragraph-wrapped shape, never the collapsed-inline one. The four assertions (`'text("The value of ") + strong({text("html_title")})' in typ_text`; `")strong({text" not in typ_text`; `'")terms(' not in typ_text`; `"par({" in typ_text`) are all either about this untouched collapsed-inline shape or about unrelated def-list/negative-juxtaposition checks. `"par({" in typ_text` in particular stays true regardless of §4, because BOTH confvals' own body paragraphs (not their field bodies) still emit `par({...})` — desc_content's plain paragraph handling is untouched by §4, which only reclassifies `field_body`'s single-paragraph child. |
| `tests/test_confval_field_spacing_render_gate.py::TestConfvalFieldSpacingRenderGate::test_typstpdf_confval_field_spacing_produces_pdf` (the `.typ`-structural half only — see Bucket C for the PDF-text half of this same file) | `the_answer`'s `:type:`/`:default:` fields are the same "no blank line, directive-option collapse" shape as above — §4.3 point 3's byte-identical guarantee applies verbatim. The two structural assertions (`'strong(text("Type") + text(": "))' in typ_text`; `'text("  ")\nstrong(text("Default")' in typ_text`) are internal substrings of the field-body/inter-field emission that §2's outer `pad(...)` wrapper brackets around, not inside — wrapping never disturbs interior bytes. |
| `tests/test_desc_bodyless_concat_render_gate.py` | Named explicitly in `38-EMISSION-CONTRACT.md` §7 as a stays-green control and in §2.4 as the FID-06 body-less regression guard this phase's own wrapper must not break. Its `desc_content` nodes are genuinely empty (bare `confval`, no body) — `pad(left: 2.5em, {})` around zero content has zero characters and (Typst's `pad` default insets are 0pt on unspecified sides) no measurable vertical footprint, so the `parbreak()`-between-siblings ordering assertion this test checks is unaffected. |
| `tests/test_inline_math_after_text_render_gate.py` (every assertion EXCEPT `test_block_math_pdf_text_is_invariant_across_the_math02_fix`, row A3) | Constructs A/B/D/E/F/G/H all live inside bullet-list items, definition-list terms, or top-level paragraphs — none involve a `desc_content` or a `field_list`, so §2-§4 do not reach them. D-13's pinned stray-`parbreak()` shape (`"list({\nparbreak()\n\nmi(\`a+b\`)"`, line 291, Construct F, mitex path) is UNCHANGED by Phase 38 — see the dedicated D-13 row below. |
| `tests/test_pdf_render_gate.py::TestDescSignatureRenderGate::test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline` | All four signatures in `desc_signature_render_gate/index.rst` are genuinely body-less (bare `.. py:function::`/`.. cpp:function::` directives, no indented content) — same empty-`desc_content` reasoning as the row above. The assertions are PDF-extracted-text sentinel checks (`"→ int"`, the two `DESC_LINE_*_SENTINEL`s, the `printf(...)` bracket string, the inline-fragment sentinel, and the `LEAK_SIGNATURES` absence checks) with nothing that could be produced by an empty `pad(...)`. |
| `tests/test_rubric_option_concat_render_gate.py::TestRubricOptionConcatRenderGate::test_typstpdf_rubric_option_produces_pdf` | See Must-not-touch section. The `--sep` option IS a `desc_signature`, but this fixture's `.. option:: --sep` directive has a real body paragraph ("If specified, separate source and build directories.") that gains the §2 wrapper — however every assertion in this function (`rubric_idx`, `option_idx`, the `between` substring, `trailing_idx`) only inspects bytes STRICTLY BETWEEN the two rubric/option `strong(...)` markers and the `linebreak()` immediately after each, never reaching into the `--sep` option's own body content past its signature. Unaffected. |

---

## Bucket C — conditionally at risk, re-verify after a named plan lands

| File / test | Condition |
|---|---|
| `tests/test_confval_field_spacing_render_gate.py::TestConfvalFieldSpacingRenderGate::test_pdf_extracted_text_matches_pinned_sc3_string` | The `.typ`-source assertions in this same class are Bucket B (contract §4.3(3) guarantees the collapsed-inline `.typ` bytes are untouched), but THIS assertion is a real-compile pypdf-extracted-text check of `PINNED_SC3_STRING = "Type: int (a number)  Default: 42"`. The confval's field list sits inside `desc_content`, so it inherits §2's 27.5pt pad AND its own §3 27.5pt pad (55pt total left shift). The pinned string is short and unlikely to hit a line-wrap boundary at this indent, but that is a measured-layout claim this census cannot hand-verify without a real compile (which would violate D-14's "never regenerate from the new code's output" for a Bucket-A-style claim, and this row is deliberately NOT asserted as either "will break" or "stays green" for that reason). Re-verify once 38-06 lands. |
| `tests/test_field_list_in_list_item_render_gate.py` nested-field CR-01 checks (`org_id_idx`/`project_url_idx`/`between_nested_fields`, lines 203-212) and the top-level `between_author_and_version` check (once row A4's `par({text("Test Author")})` lookup is itself updated by 38-06) | This is precisely the trap `38-EMISSION-CONTRACT.md` §4.3 point 2 names: the newly-introduced "single-paragraph-unwrapped" inline classification must NOT set `_last_field_body_was_inline` (which is reserved for the genuinely collapsed-inline case), or the FID-09 inter-field `text("  ")` separator will erroneously re-fire between these paragraph-wrapped siblings — reproducing the exact CR-01 regression this file's own control was written to catch, under a new mechanism. Whether this holds is Claude's D-12 implementation choice at 38-06, decided by this exact fixture per the emission contract's own instruction ("decided by the fixture"). |
| `tests/test_pdf_render_gate.py::TestDescSignatureRenderGate::test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline` (DESC-02's ordering-sensitive checks specifically: `idx_line1`/`idx_break`/`idx_line2`-style relative-position reasoning, folded into the sentinel-adjacency assertions) | Bucketed B above on the reasoning that an empty `pad(...)` has zero footprint — that is a reasonable prediction from the `pad()` primitive's documented default insets, but it is not itself re-measured against a real compile in this census (doing so would require running the phase's own not-yet-written code). Listed here again as the one item in Bucket B carrying a residual, low-probability layout risk worth a fast re-check once 38-05 lands, rather than silently trusting the prediction through to phase close. |

---

## Bucket D — page counts and other MEASUREMENTS, not expected strings

Re-measuring a page count against the post-phase build is legitimate and required (contract §4.4: 97→87
pages on this project's own docs is the whole-document consequence of the D-07 field-body fix); pasting
an emitted `.typ` fragment or a freshly-compiled PDF-text extraction into a golden as if it were a
hand-derived expected string is not (D-14's non-negotiable constraint). The two constants below are the
named page-count consumers; both must be **re-measured**, never derived from this document alone,
because §2's indent literal (widens nothing but shifts everything) and §4's field-body fix (removes a
paragraph-boundary, shortening the field-list block) pull page count in opposite directions and only a
real compile resolves the net effect for each fixture.

| Constant | File:Line | Consuming test | What must happen |
|---|---|---|---|
| `EXPECTED_PAGE_COUNT_PRE_PHASE = 7` | `tests/test_signature_page_boundary_render_gate.py:109` | `test_page_count_does_not_inflate` (an `<=` ceiling check, not exact-equality) and indirectly `test_primary_signature_and_body_share_a_page` | The fixture's single signature has a real body (SIG-09's whole point is proving signature+body co-location), so §2's wrapper reaches it. This constant is ALSO the exact subject of the folded todo `2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md` (`38-CONTEXT.md` Folded Todos) — its name has held a post-`37-09` value since Phase 37, and Phase 38 measurably moves page counts again, so renaming it (to something like `EXPECTED_PAGE_COUNT_PRE_38`) in the same commit that re-measures it is in-scope and costs nothing extra. Re-measure at 38-08. |
| `EXPECTED_PAGE_COUNT = 4` | `tests/test_signature_typography_multi_signature_page_count_gate.py:90` | `test_multi_signature_document_page_count_at_real_geometry` (exact `==` equality, T-37-08's compounding detector) | The `signature_typography_gate` fixture has 13 signature wrappers, several with real bodies (confirmed by reading the fixture: e.g. the `TypstBuilder`-shaped class body at line 23-26). All 13 desc_content bodies gain §2's pad; several field lists (this fixture uses Python-domain autodoc-style directives with field lists) gain §3's nested pad on top. Whole-document consequence is not derivable from the single-fixture 97→87-page figure in §4.4 (different fixture, different proportions of body-vs-signature content) — must be independently re-measured. Re-measure at 38-08. |

---

## Counts

- **Bucket A (will break):** 4 rows — 1 golden-file byte-identity gate, 1 AST-based delegation-guard test, 1 pair of PDF-text goldens (counted as one row, two files), 1 real-compile structural/CR-01 test function.
- **Bucket B (mentions, stays green):** 11 files/test-groups, spanning 10 distinct `tests/*.py` modules.
- **Bucket C (conditionally at risk):** 3 rows across 3 files.
- **Bucket D (measurements, not expected strings):** 2 page-count constants across 2 files.
- **Total files opened during this census's reading pass:** 25 — `38-EMISSION-CONTRACT.md`, `38-CONTEXT.md`, `37-TEST-CENSUS.md`, `REQUIREMENTS.md` (milestone-invariants section), `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ`, `tests/fixtures/desc_rubric_decoupling_render_gate/index.rst`, `tests/test_desc_rubric_decoupling_render_gate.py`, `tests/test_confval_field_spacing_render_gate.py`, `tests/fixtures/confval_field_spacing_render_gate/index.rst`, `tests/test_confval_field_body_render_gate.py`, `tests/fixtures/confval_field_body_render_gate/index.rst`, `tests/test_field_list_in_list_item_render_gate.py`, `tests/fixtures/field_list_in_list_item_render_gate/index.rst`, `tests/test_translator.py` (the `desc`/`field_list`/`rubric` region, lines 3354-3712), `tests/test_pdf_render_gate.py` (`TestDescSignatureRenderGate`), `tests/fixtures/desc_signature_render_gate/index.rst`, `tests/test_desc_bodyless_concat_render_gate.py`, `tests/test_inline_math_after_text_render_gate.py`, `tests/fixtures/inline_math_pdf_text_mitex.golden.txt`, `tests/fixtures/inline_math_pdf_text_native.golden.txt`, `tests/fixtures/inline_math_after_text_render_gate/index.rst`, `tests/test_signature_page_boundary_render_gate.py`, `tests/test_signature_typography_multi_signature_page_count_gate.py`, `tests/fixtures/signature_typography_gate/index.rst` (structure check), `tests/test_rubric_option_concat_render_gate.py`.

---

## Disagreement between grep-by-name and read-the-assertion (required evidence, both directions)

**Direction 1 — a name/shape grep WOULD flag a file that reading clears.** `tests/test_translator.py::test_full_api_description_structure` and `::test_field_list_rendering` both construct a real `desc_content`/`field_list` tree containing exactly the shapes §2/§3/§4 change (a body paragraph, a nested field list, a single-paragraph field body) — a grep for `desc_content(` or `field_body` in `test_translator.py`, or a naive reading of `38-EMISSION-CONTRACT.md` §7's own citation of this file ("the `desc` and field-list structural assertions"), would flag both as breaking. Reading each assertion line-by-line (Bucket B above) shows all six assertions across the two tests are loose substring checks that survive both the wrapper and the reflow unchanged. **This is the single largest concrete instance of §7's starting list disagreeing with a full read** — the contract's own row for `tests/test_translator.py` predicted breakage; this census found none, and the disagreement is recorded rather than silently resolved by omitting the file.

**Direction 2 — reading surfaced breakage a name/shape grep would miss.** A grep for `desc_content|field_list|literal_strong|literal_emphasis` across `tests/*.py` returns `tests/test_desc_rubric_decoupling_render_gate.py` only for its already-known `golden.typ` byte-identity gate (SC#2) — nothing in that grep pattern surfaces `RETAINED_DELEGATION_METHODS` or `DUMMY_STRONG_LITERAL`, because SC#1's own assertion (`test_desc_signature_and_rubric_do_not_delegate_to_visit_strong`) never spells `literal_strong`/`literal_emphasis` as a bare grep-able string in a way that associates it with "this phase's changes" — it names them only as the METHODS THAT MUST KEEP delegating, i.e. a *stays-green* claim on its face. Only reading the full method body (per this plan's own `read_first` instruction to open the whole file) revealed that D-09 inverts this exact claim: literal_strong/literal_emphasis are D-05/D-09's own target, so the "must still delegate" guard becomes a "must no longer delegate" fact the moment 38-07 lands. This mirrors `37-TEST-CENSUS.md`'s own precedent exactly (its row A5, found the identical way, in the identical file's sibling class) — reading the whole file, not the line numbers a table happens to cite, is what surfaced it both times.

A third, smaller instance: the search run for "a name-based grep would flag but reading clears" ALSO checked `tests/test_desc_bodyless_concat_render_gate.py` and `tests/test_pdf_render_gate.py::TestDescSignatureRenderGate` (both grep-positive for `desc_signature`/`desc_content`-adjacent fixture names) and confirmed both are genuinely safe (Bucket B, empty-`desc_content` reasoning) — recorded as a confirmed-safe result of the same search, not a new disagreement, since the emission contract's own §7 already listed the bodyless-concat file among the "stays green" controls and this census agrees.

---

## MUST-NOT-TOUCH — rubric assertions (Phase 39 territory)

Phase 36 already decoupled `rubric` from `desc_signature` (`visit_rubric`/`depart_rubric` no longer delegate
to `visit_strong` via a dummy node — proven by `tests/test_desc_rubric_decoupling_render_gate.py`'s SC#1,
row A2 above, whose `DECOUPLED_METHODS` half — `visit_desc_signature`, `depart_desc_signature`,
`visit_rubric`, `depart_rubric` — stays green and is NOT touched by this phase; only the
`RETAINED_DELEGATION_METHODS` half changes). `rubric` restyling is Phase 39's (ADM-01..05); Phase 38
must not edit any of the three assertions below, and must not let 38-07's `RETAINED_DELEGATION_METHODS`
edit (row A2) touch `DECOUPLED_METHODS` or the count-of-2 guard's reasoning about `rubric`:

1. **`tests/test_rubric_option_concat_render_gate.py:138`** — `typ_text.index('strong({text("Structure Options")})')` (the autodoc "Options" rubric half of the FID-04 gate).
2. **`tests/test_rubric_option_concat_render_gate.py:162`** — `typ_text.index('strong({text("Trailing Heading")})')` (the true end-of-document rubric).
3. **`tests/test_translator.py:3620`** — `test_rubric_rendering`'s `'strong({text("Methods")]' in output or "Methods" in output` assertion.

Line numbers above are current (2026-08-01), and differ slightly from `37-TEST-CENSUS.md`'s own citations
of the same three assertions (`133`/`150`/`98-99` there) — files have shifted since Phase 37; re-read line
numbers, never trust a prior census's line citations across phases.

---

## D-13 row — the stray `parbreak()` at the head of each bulleted field-list item: LEFT IN PLACE, restated here

`38-EMISSION-CONTRACT.md` §4.5 and `38-CONTEXT.md` D-13 both record the decision: the `parbreak()` that
opens every bulleted field-list item (`list({\nparbreak()\n\n…`) is **not** touched by Phase 38. It is
Claude's discretion under D-13, and the decision taken at plan time was to leave it, because removing it
has a repo-wide blast radius (every bullet/enumerated/definition list, not only field-list bullets, since
the break comes from `visit_paragraph`'s `self.in_list_item` fast-path) for a cosmetic ~7.15pt change
outside FLD-02's actual requirement. **The test that already pins this exact shape, so a future migration
must not treat the pin as stale:** `tests/test_inline_math_after_text_render_gate.py:291`, inside
`test_typstpdf_separates_inline_math_mitex_path`, asserting `"list({\nparbreak()\n\nmi(\`a+b\`)" in typ_text`
(Construct F — a list item whose sole content is inline math). This assertion is untouched by Phase 38 and
stays green (Bucket B) precisely because D-13 leaves the mechanism it depends on alone.

---

## Migration strategy (D-14)

D-14 leaves the exact-string migration strategy to Claude under one non-negotiable constraint: hand-derived
expected strings plus a recorded census, never regeneration from the new code's own output (ROADMAP SC#5,
milestone invariant #4). This census adopts the following strategy, binding on 38-05 through 38-08:

- **Migration is owned per plan, at the point the bytes change (milestone invariant #5), not deferred to a
  single closing pass.** Each of 38-05 (§2 body wrapper + §6 break-marker fix), 38-06 (§3 field-list wrapper
  + §4 field-body reflow), and 38-07 (§5 monospace literal leaves) migrates the Bucket A rows assigned to
  it above, **in the same commit that changes the bytes**, so each commit's whole-suite delta is a set
  difference with a stated cause rather than a mixed bag. 38-08 (page counts) closes the wave.
- **The `golden.typ` byte-identity gate (row A1) is migrated by applying the contract's rules to the
  EXISTING golden by hand** — inserting `pad(left: 2.5em, {` immediately after each signature's closing
  `[#metadata(none) <index:…>]` anchor line and `})\n` immediately before the next paragraph/directive
  boundary, exactly per §2's specification — and only THEN rebuilding to confirm. If the rebuilt output and
  the hand-derived golden disagree, the diff is investigated and either the code or the contract is wrong
  (per `38-EMISSION-CONTRACT.md` §0); **the golden is never replaced with the build's own output as the
  resolution.** This rule is recorded here so 38-05's executor cannot reasonably read it any other way.
- **The two Phase-34 PDF-text goldens (row A3) are the one documented exception to "hand-derive first":**
  a PDF-extracted-text golden is fundamentally a measurement of a real Typst layout pass, not a `.typ`-source
  byte sequence this contract can specify character-for-character in advance. Their migration methodology
  is re-measure-then-verify, mirroring `37-09`'s own precedent for these SAME two files: rebuild once BOTH
  38-05 and 38-06 have landed, diff the freshly-extracted text against the currently-committed baseline, and
  manually confirm the diff is *solely* the predicted line-wrap consequence of the narrower available width
  (never accept a re-capture that also changes unrelated lines, or that changes MORE than the Construct C
  region) before committing the new baseline. This is not a license to treat every PDF-text assertion this
  way — see the next point.
- **Page counts (Bucket D) are re-measured, not re-derived, and stay in Bucket D.** Every commit that moves
  one states the measured before-and-after and the reason (widening from the indent vs. shortening from the
  field-body reflow are both expected, in either net direction, per contract §4.4/§5.6).
- **Bucket C rows are re-verified, not migrated, at the plan named in their own row** — a Bucket C row that
  turns out to still pass after its owning plan lands needs no commit; one that breaks is migrated by that
  same plan under the rules above, and the census is updated to say so (see the next rule).
- **If an unpredicted file breaks, it is migrated by the plan that broke it, and the census records the miss
  at closeout rather than being silently amended** — the Phase 37 convention (`37-TEST-CENSUS.md` "Finalisation
  against reality" / "The census's honest miss") that a census which was wrong in a recorded way is more
  useful than one silently corrected. 38-08 (or a gap-closure plan, if the orchestrator authors one) is
  responsible for writing that finalisation section into this file at phase closeout, mirroring
  `37-TEST-CENSUS.md`'s own shape.

---

## Whole-suite baseline

Run 2026-08-01, in this worktree, on the current (pre-Phase-38) tree, after `env -u VIRTUAL_ENV -u
UV_PROJECT_ENVIRONMENT uv sync --extra dev` and shimming both `uv` and `ruff` per `CLAUDE.md` §
"Worktree-isolated execution" / the NixOS-sandbox project memory:

```
$ uv run pytest -m "not slow" -q
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
collected 688 items / 29 deselected / 659 selected
...
===================== 659 passed, 29 deselected in 46.47s ======================
```

**Verbatim summary line:** `659 passed, 29 deselected in 46.47s`. **Zero failures.** No node id needs
listing under "failing" because there are none — the baseline this phase's plans diff against is a fully
green 659/659.

**Wave-1 gate plans (38-01, 38-02, 38-03) deliberately add failing node ids to this baseline** — their
REDs are structural (milestone invariant #4: every design defect this phase targets compiles fine today,
so RED must be written as a pre-existing structural/regex/`pypdf`-text assertion, not a compile fatal).
This census cannot enumerate those specific node ids (38-01/38-02/38-03 are sibling wave-1 plans, not read
by this plan), but per `38-EMISSION-CONTRACT.md` they belong to the following modules and MUST NOT be
mistaken for regressions when 38-05/38-06/38-07 next run the suite:

- a `tests/test_desc_content_indent_render_gate.py`-shaped new module for IND-01/02/03/05 (§2/§2.3) — new
  file, new RED, not present in the 659-passed baseline above.
- a `tests/test_field_list_indent_render_gate.py`-shaped new module for FLD-01 (§3) — same reasoning.
- a `tests/test_field_body_inline_render_gate.py`-shaped new module for FLD-02 (§4) — same reasoning.
- a `tests/test_literal_strong_emphasis_monospace_render_gate.py`-shaped new module for FLD-03 (§5) — same
  reasoning.
- the `depart_desc` marker-propagation fixture (§6/D-10) — likely a new class inside an existing module or
  a new module, per the RED-must-be-a-conjunction requirement (`.typ` wrapper tokens present AND
  `parbreak()` count exactly 8).

Exact module/class names are 38-01/38-02/38-03's own artifact, not this census's to invent; this section
exists so that once those wave-1 plans land, their new failing node ids are recognised as ADDED RED
(expected, by design) rather than compared against zero and flagged as a baseline drift.

**Lint/type baseline**, same session:

```
$ uv run black --check .
All done! 🍰 
184 files would be left unchanged.

$ uv run ruff check .
All checks passed!

$ uv run mypy typsphinx/
Success: no issues found in 6 source files
```

All three clean. `ruff` required the NixOS-sandbox shim (`ln -sf` the main tree's patchelf'd
`.venv/bin/ruff` copy into this worktree's `.venv/bin/ruff`, per the project's `nixos-sandbox-test-env`
memory) — a provisioning step, not a code issue; recorded here so a later plan's own baseline run does
not rediscover it as a surprise.

---

## Finalisation against reality (written by `38-08` Task 3, phase closeout)

Per row, whether the predicted outcome actually happened, cross-checked against every implementation
plan's own SUMMARY (`38-05-SUMMARY.md`, `38-06-SUMMARY.md`, `38-07-SUMMARY.md`) and the requirement
verdict table in `38-GATE-EVIDENCE.md` §4.4. Mirrors `37-TEST-CENSUS.md`'s "Finalisation against
reality" shape (bucket-by-bucket predicted-vs-actual, an honest-miss section, no earlier bucket row
edited) — per D-14, only that shape and its "disagreement between grep-by-name and read-the-assertion"
evidence convention are inherited from Phase 37; this census's own *content* above is unedited by this
section.

### Bucket A — predicted vs. actual

| # | File / test | Predicted owning plan | Actually flipped at | Match? |
|---|---|---|---|---|
| A1 | `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` byte-identity gate | 38-05 | `655cff1` (38-05 Task 3) — hand-migrated golden, byte-identical to a fresh rebuild on the first attempt, no reconciliation needed | Yes |
| A2 | `tests/test_desc_rubric_decoupling_render_gate.py::TestDescRubricDecouplingRenderGate::test_desc_signature_and_rubric_do_not_delegate_to_visit_strong` (SC#1 over-reach guard) | 38-07 | `eb16c20` (38-07 Task 2) — migrated in the file the census's own row A2 named, not the two files 38-07's own `files_modified` frontmatter listed (neither contains a `literal_strong`/`literal_emphasis` assertion, confirmed by grep before editing) | Yes |
| A3 | Both Phase-34 PDF-text goldens (`inline_math_pdf_text_mitex.golden.txt`, `inline_math_pdf_text_native.golden.txt`), jointly owned 38-05/38-06, 38-06 as closing owner | 38-06 | `edf90a2` (38-06 Task 3) — re-measured post both 38-05 and 38-06, hand-verified byte-for-byte identical to the prior baseline outside the one predicted Construct C line-wrap hunk | Yes |
| A4 | `tests/test_field_list_in_list_item_render_gate.py::TestFieldListInListItemRenderGate::test_typstpdf_separates_field_list_in_list_item_and_produces_pdf` (`par({text("Test Author")})` CR-01 marker) | 38-06 | `edf90a2` (38-06 Task 3) — marker migrated from the `par({text("Test Author")})` substring to `strong(text("Author") + text(": "))`, preserving the same underlying property | Yes |

**4/4 Bucket A predictions held** — every predicted node id flipped at the plan the census named as
owner, with no early, late, or unpredicted-plan flip. (This is a smaller Bucket A than Phase 37's
10/10 by design — Phase 38's blast radius is more concentrated, per `38-EMISSION-CONTRACT.md` §7's own
starting table.)

### Bucket B — predicted stays-green, held

Every predicted stays-green file/test-group held throughout every wave, evidenced by each plan's own
whole-suite set-difference statement (38-05: 683 passed/17 failed; 38-06: 689/11; 38-07: 700/0 — no
Bucket-B node id ever appears in a "flipped" or "new failure" list across any of the three plans) and
re-confirmed directly at this plan's closeout:

```
$ uv run pytest tests/test_translator.py -k "desc or field_list or rubric or full_api" -v
9 passed, 108 deselected in 0.03s
```

All nine of `test_translator.py`'s desc/field-list/rubric-adjacent assertions (the file `38-EMISSION-
CONTRACT.md` §7 predicted would break, and this census's own Bucket B disagreed with) stayed green
through the whole phase, confirming the census's Direction-1 disagreement (§ above) held to closeout.

### Bucket C — conditional, re-verified

All three conditional rows re-verified GREEN at this plan's closeout, run directly against the final
post-38-07 tree:

```
$ uv run pytest tests/test_confval_field_spacing_render_gate.py::TestConfvalFieldSpacingRenderGate::test_pdf_extracted_text_matches_pinned_sc3_string tests/test_field_list_in_list_item_render_gate.py tests/test_pdf_render_gate.py::TestDescSignatureRenderGate::test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline -v
tests/test_confval_field_spacing_render_gate.py::...::test_pdf_extracted_text_matches_pinned_sc3_string PASSED
tests/test_field_list_in_list_item_render_gate.py::...::test_typstpdf_separates_field_list_in_list_item_and_produces_pdf PASSED
tests/test_field_list_in_list_item_render_gate.py::...::test_pdf_extracted_text_has_no_stray_version_indent PASSED
tests/test_pdf_render_gate.py::TestDescSignatureRenderGate::test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline PASSED
4 passed
```

- **PINNED_SC3_STRING row**: re-verified GREEN once 38-06 landed (`38-06-SUMMARY.md` D2 coverage
  table lists this exact node id as `status: pass`) — the pinned string's short length stayed clear of
  the widened field-list column at the actual measured indent.
- **The CR-01 nested-field trap row** (D-12's `_field_body_unwrapped_paragraph` exclusion from
  `_last_field_body_was_inline`): settled by 38-06's own implementation choice, confirmed by the same
  file's two node ids above staying GREEN — the FID-09 inter-field separator did not erroneously fire
  between the newly-inlined single-value fields.
  38-06's own "Issues Encountered" section records that an early implementation attempt WOULD have
  tripped this exact trap (caught by `test_fld02_consecutive_single_value_fields_stay_on_separate_lines`
  going RED during development, never committed in that state) — the fixture did its job.
- **The empty-`pad(...)`-footprint row** (DESC-02 ordering-sensitive checks in
  `test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline`): re-verified GREEN directly at this
  plan's closeout (command above) — the prediction that an empty `pad(...)` has zero measurable
  footprint held through the real post-phase build, not merely assumed from the primitive's documented
  default insets.

### Bucket D — page counts, before/after and re-measuring plan

| Constant | Before (pre-Phase-38 baseline) | After (post-Phase-38, re-measured) | Re-measuring plan |
|---|---|---|---|
| `EXPECTED_PAGE_COUNT_CEILING` (renamed from `EXPECTED_PAGE_COUNT_PRE_PHASE`) | 7 | 7 (unchanged) | 38-08 Task 1 |
| `EXPECTED_PAGE_COUNT` (`signature_typography_gate`) | 4 | 4 (unchanged) | 38-08 Task 1 |
| This project's own docs (D-08 whole-document claim) | 97 (pre-Phase-38, cited via the discussion session's own prototype) | 90 (measured, `tox -e docs-pdf`) — versus the session's own exploratory 87-page prototype figure | 38-08 Task 1 |

Both named constants stayed at their pre-Phase-38 values because their specific fixtures lack the
content Phase 38's two page-count-moving mechanisms act on (see `38-GATE-EVIDENCE.md` §3 for the
per-fixture reasoning). The whole-document figure moved as predicted in direction (down from the
pre-Phase-38 baseline) with a magnitude that differs from the discussion session's own isolated
prototype measurement, explained (not absorbed) in `38-GATE-EVIDENCE.md` §3.

### Misses — folded in honestly, not silently absorbed

Five items, none of which this census correctly predicted at census-writing time (plan 38-04, wave 1),
folded in per this census's own binding instruction ("a census that was wrong in a recorded way is more
useful than one quietly fixed"). No earlier bucket row above was edited to make a prediction look
correct — this section is a pure addition, verified by `git diff --stat` on this file.

1. **`38-EMISSION-CONTRACT.md` §7's over-prediction on `test_translator.py`.** §7's starting table
   named `tests/test_translator.py` as expected-to-break ("the `desc` and field-list structural
   assertions"), attributing the prediction to §2, §3, §4, and §5 jointly. This census's own Bucket B
   (Direction 1 of its "Disagreement" section, written at census time) already found and recorded that
   all nine of that file's desc/field-list/rubric assertions are loose substring checks that survive
   every one of those sections' changes unchanged — read at census-writing time, not discovered
   post-hoc. Folded in here as an honest record that §7's starting prediction disagreed with the
   census, and the census was right: re-confirmed GREEN through all three implementation plans and
   again at this plan's own closeout (Bucket B above).

2. **`38-EMISSION-CONTRACT.md` §7's under-prediction on the SC#1 delegation guard (row A2).** §7's
   starting table did not name `tests/test_desc_rubric_decoupling_render_gate.py`'s SC#1
   `RETAINED_DELEGATION_METHODS` guard at all — this census's own row A2 (written by plan 38-04,
   reading the full method body per its own `read_first` instruction rather than trusting a
   name-grep) is what surfaced it, mirroring `37-TEST-CENSUS.md`'s own precedent (its row A5, found the
   identical way in the identical file's sibling class). Migrated by 38-07 as predicted. This is the
   census catching a real under-prediction in its own starting input, not a miss in the census's own
   Bucket A rows.

3. **38-06's own census miss, one assertion upstream of row A4.** Recorded in `38-06-SUMMARY.md`'s
   Deviations §1 (Rule 1 bug fix): row A4 predicted `tests/test_field_list_in_list_item_render_gate.py`
   would break at its downstream `par({text("Test Author")})` CR-01 marker (Task 2's field-body reflow).
   Task 1's own field-list indent wrapper landing independently broke an EARLIER assertion in the same
   test function first — the field list's own newline-separation proof against the preceding
   "For example:" paragraph (line 164 at the time) — which the census's row A4 did not separately
   flag, because it was reading forward from the CR-01 marker's own predicted cause (Task 2's reflow)
   without separately tracing Task 1's own wrapper-insertion consequence on the SAME file. **This is
   the census's own miss**, folded in honestly rather than silently absorbed into row A4 as if it had
   always been part of that row's prediction.

4. **38-03's buffer-swap fixture measured GREEN, contradicting the folded todo's own prose
   prediction.** The folded todo
   (`2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md`) predicted the glossary-nested
   `desc` pair fixture would measure RED pre-phase. It measured GREEN: both `depart_desc` calls for the
   nested pair run inside the SAME swapped `current_definition_buffer`, so no live cross-buffer
   comparison occurs for this specific reachable shape. `38-GATE-EVIDENCE-03.md`'s own "Buffer-swap
   fixture: measured pre-phase outcome" section already recorded this as the todo's own binding
   honest-measurement instruction requires (never retro-fit a fixture into a RED it did not produce).
   It became a non-regression control instead of a RED — folded in here as the census's own record of a
   prediction (the todo's, not this census's own Bucket A) that reality contradicted.

5. **38-07's Rule-1 test fix: the typeless-param FLD-03 test's naming collision.**
   `test_fld03_typeless_param_exactly_one_bold_mono_zero_italic_mono`'s region sliced from the section
   heading, which included the fixture's own `desc_signature` for
   `field_name_without_type(untyped)`. That signature's sole parameter shares the literal string
   "untyped" with the field-body parameter it documents, and Phase 37's SIG-04 rule unconditionally
   italicises a signature's bare parameter name regardless of type annotation — an orthogonal,
   untouched-by-Phase-38 mechanism. With 38-07's correct implementation in place, the region still
   contained `emph(raw("untyped"))` from the SIGNATURE, tripping the "zero italic-mono calls"
   assertion on unrelated bytes. Fixed by narrowing the region to start at the field list's own label.
   This is an authoring oversight in plan 38-02's own fixture/test-region design, surfaced only when
   38-07's correct implementation still failed the test — not a translator defect, and not itself a
   Bucket A row (the assertion's *intent* was always correct; only its region boundary was wrong).

### D-13 and D-14 dispositions, restated with their outcome

**D-13 — the stray `parbreak()` at the head of each bulleted field-list item: LEFT IN PLACE, and it
stayed that way through phase close.** No plan in this phase touched the `self.in_list_item` fast-path
in `visit_paragraph` that emits it. The still-green pinning test that proves the shape was never
disturbed: `tests/test_inline_math_after_text_render_gate.py::test_typstpdf_separates_inline_math_mitex_path`,
asserting `"list({\nparbreak()\n\nmi(\`a+b\`)" in typ_text` — re-confirmed passing in the final
`uv run pytest -m "not slow" -q` run (700 passed, 0 failed) at this plan's own closeout.

**D-14 — the migration strategy: per-plan hand-derivation with the golden file hand-edited and
confirmed by rebuild, not regenerated.** This held for the golden, quoting `38-05-SUMMARY.md`'s own
evidence directly: *"the hand-edited `golden.typ` (Task 3 commit `655cff1`) matched a fresh `-b typst`
rebuild on the first attempt — `tests/test_desc_rubric_decoupling_render_gate.py::...::
test_emitted_typ_is_byte_identical_to_golden` passed with no adjustment to the hand-derived bytes."*
No golden byte was ever pasted from a build's own output and then accepted as the expected string; the
one documented exception this census's own "Migration strategy (D-14)" section carved out in advance
— the two Phase-34 PDF-text goldens, re-measured rather than hand-derived, because a PDF-extracted-text
golden is fundamentally a measurement of a real Typst layout pass — was exercised exactly as specified,
with the required manual diff-confirmation step performed by 38-06 (`38-06-SUMMARY.md`'s "Authorized
Scope Extension" section quotes the byte-for-byte diff, confirmed to be solely the predicted Construct C
line-wrap consequence).

### Folded todos, closed

Both folded todos are closed following this project's standing closure convention: a todo carrying
`resolves_phase: N` in its frontmatter is moved from `.planning/todos/pending/` to
`.planning/todos/completed/` by the orchestrator's own `close_phase_todos` step once the phase
completes, on the main tree, after all wave worktrees merge — never by an individual plan's own
worktree agent (a `git mv` from inside a worktree registers as a file deletion, which
`worktree.cleanup-wave` blocks unconditionally with no bypass). Verified directly, both todos already
carry the field:

```
$ grep -l "resolves_phase: 38" .planning/todos/pending/2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md .planning/todos/pending/2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md
.planning/todos/pending/2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md
.planning/todos/pending/2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md
```

Both present; neither needed the field added. This is the closure evidence for both todos — the files
themselves are left in `.planning/todos/pending/` for the orchestrator's own post-merge step to move.

## Final counts (post-`38-07`, closed at `38-08`)

- Bucket A (predicted breaking, all flipped as predicted): **4/4**.
- Bucket B (predicted stays-green, held): **11/11** files/test-groups.
- Bucket C (predicted conditional, re-verified): **3/3**.
- Bucket D (page counts, measured before/after): **2/2** constants unchanged, plus the whole-document
  D-08 claim checked against a real build (moved as predicted in direction, differing in magnitude,
  explained in `38-GATE-EVIDENCE.md` §3).
- Misses (unpredicted, folded in honestly): **5** — two contract-§7-vs-census disagreements (one in
  each direction, both resolved correctly by the census's own reading), one genuine census miss
  (38-06, one assertion upstream of row A4), one prediction from OUTSIDE this census that reality
  contradicted (the folded todo's own prose, measured GREEN not RED by 38-03), and one authoring
  oversight in an earlier plan's own fixture design (38-07's typeless-param region fix).
- **Total node ids/files this census's full lifecycle accounts for: 20** (4 + 11 + 3 + 2), with 18/20
  (90%) correctly predicted at census-writing time and the remaining items discovered honestly during
  the phase's own implementation waves or at this plan's own closeout, never silently absorbed into an
  earlier bucket row.
