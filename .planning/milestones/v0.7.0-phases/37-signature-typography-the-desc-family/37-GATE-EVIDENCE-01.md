# Phase 37 Plan 01 — GATE-01 RED Evidence (SIG-01..SIG-05)

**Captured:** 2026-08-01
**Plan:** 37-01 (Wave 1)
**Not named `37-VERIFICATION.md`** deliberately — that filename is reserved for the
verify stage and is overwritten wholesale; this evidence file must survive
independently of any later `/gsd-verify-work` run and is merged into
`37-GATE-EVIDENCE.md` by plan 37-08 alongside its three Wave-1 siblings
(`37-GATE-EVIDENCE-02.md`..`-04.md`).

## Commit SHA the RED was captured against

`typsphinx/translator.py` is **completely untouched** by plan 37-01 (`git diff
--stat HEAD -- typsphinx/` is empty at every point in this plan's execution).
The RED below was captured at:

- **HEAD at capture time:** `6ca21d6f7ea6019c6748860e15663171977c7f67`
  (`test(37-01): ship per-sub-part SIG-01..05 gate module, recorded RED`)
- **Last commit that touched `typsphinx/translator.py`:**
  `995c78d20c47cf0bc3bc1d899538d1fd4531994b` (pre-dates this plan entirely —
  `visit_desc_name`, `visit_desc_annotation`, `visit_desc_sig_name` and
  `visit_desc_parameter` are all still `pass` at this SHA)
- **Worktree base (plan start):** `011b9265daf3389f3482b5efd96b4eaa16a94743`

## Intentionally-RED node ids (14)

Enumerated explicitly so a later wave can verify by **set difference**, never by
count (per STATE.md's Operator Next Steps and ROADMAP invariant #4):

```
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig01_leaf_desc_name_bold_monospace
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig01_nonleaf_desc_name_bold_via_nested_desc_sig_name
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_addname_plain_monospace_with_zwsp_and_no_enclosing_bold
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_addname_and_name_are_two_separate_expressions
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_empty_addname_emits_zero_bytes
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig03_annotation_and_name_wrapper_shapes_are_byte_identical
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_parameter_names_italic_type_and_default_plain
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_resolved_xref_type_annotation_keeps_hyperlink
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_generic_type_and_quoted_forward_ref_are_plain
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_delimiters_use_monospace_primitive
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_empty_parameter_list_no_comma_separator
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_optional_group_separator_lands_inside_bracket
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_nested_optional_groups_close_in_reverse_open_order
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_encoding_non_ascii_signature_round_trips_code_points
```

**NOT RED (documented invariance control, expected to PASS in every state):**

```
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_determinism_two_builds_produce_byte_identical_output
```

Every RED failure above is a **structural mismatch on the emitted `.typ`** — an
`assert ... in region` / `assert a == b` substring/equality failure — **never a
compile failure**. This module drives `-b typst` only (no `typst.compile()` leg);
the pre-phase output already compiles fine (milestone invariant #4), so there is
no compile-fatal RED available or expected here.

## Verbatim `uv run pytest tests/test_signature_typography_gate.py -v` output

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-afa998ce5b426e19e/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-afa998ce5b426e19e
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 15 items

tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig01_leaf_desc_name_bold_monospace FAILED [  6%]
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig01_nonleaf_desc_name_bold_via_nested_desc_sig_name FAILED [ 13%]
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_addname_plain_monospace_with_zwsp_and_no_enclosing_bold FAILED [ 20%]
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_addname_and_name_are_two_separate_expressions FAILED [ 26%]
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_empty_addname_emits_zero_bytes FAILED [ 33%]
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig03_annotation_and_name_wrapper_shapes_are_byte_identical FAILED [ 40%]
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_parameter_names_italic_type_and_default_plain FAILED [ 46%]
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_resolved_xref_type_annotation_keeps_hyperlink FAILED [ 53%]
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_generic_type_and_quoted_forward_ref_are_plain FAILED [ 60%]
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_delimiters_use_monospace_primitive FAILED [ 66%]
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_empty_parameter_list_no_comma_separator FAILED [ 73%]
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_optional_group_separator_lands_inside_bracket FAILED [ 80%]
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_nested_optional_groups_close_in_reverse_open_order FAILED [ 86%]
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_encoding_non_ascii_signature_round_trips_code_points FAILED [ 93%]
tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_determinism_two_builds_produce_byte_identical_output PASSED [100%]

=================================== FAILURES ===================================
_____ TestSignatureTypographyGate.test_sig01_leaf_desc_name_bold_monospace _____
E       AssertionError: SIG-01: expected the leaf desc_name 'LaTeXBuilder' to emit 'strong(raw("LaTeXBuilder"))' (contract §5.1 leaf branch), not found in region:
E         text("LaTeXBuilder Class With Nested Method")}) <index:latexbuilder-class-with-nested-method>]
E         strong({text("class")
E         text(" ")
E         text("sphinx.builders.latex.")
E         text("LaTeXBuilder")
E         text("(") + text("app") + text(", ") + text("env") + ... + text(")")})
E         [#metadata(none) <index:sphinx.builders.latex.LaTeXBuilder>]
E       assert 'strong(raw("LaTeXBuilder"))' in '...'
tests/test_signature_typography_gate.py:214: AssertionError

_ TestSignatureTypographyGate.test_sig01_nonleaf_desc_name_bold_via_nested_desc_sig_name _
E       AssertionError: SIG-01: expected the non-leaf desc_name's nested desc_sig_name 'cpp_probe' to emit 'strong(raw("cpp_probe"))' (contract §5.2 rule 1), not found in region:
E         text("C++ Non-Leaf Name")}) <index:c-non-leaf-name>]
E         strong({text("void")
E         text(" ")
E         text("cpp_probe")
E         text("(") + text("int") + text(" ") + text("x") + text(")")})
E       assert 'strong(raw("cpp_probe"))' in '...'
tests/test_signature_typography_gate.py:231: AssertionError

_ TestSignatureTypographyGate.test_sig02_addname_plain_monospace_with_zwsp_and_no_enclosing_bold _
E       AssertionError: SIG-02: expected the dotted qualifier to emit 'raw("sphinx.\u{200B}builders.\u{200B}latex.\u{200B}")' (contract §4 step 3's ZWSP escape after every '.'), not found in region:
E         text("LaTeXBuilder Class With Nested Method")}) <index:latexbuilder-class-with-nested-method>]
E         strong({text("class")
E         text(" ")
E         text("sphinx.builders.latex.")
E         text("LaTeXBuilder") ...
E       assert -1 != -1
tests/test_signature_typography_gate.py:252: AssertionError

_ TestSignatureTypographyGate.test_sig02_addname_and_name_are_two_separate_expressions _
E       AssertionError: SIG-02 adjacency: expected both the addname and name calls to be present in region: ...
E       assert (-1 != -1)
tests/test_signature_typography_gate.py:274: AssertionError

____ TestSignatureTypographyGate.test_sig02_empty_addname_emits_zero_bytes _____
E       AssertionError: SIG-02: expected the desc_name '--sep' to emit 'strong(raw("--sep"))', not found in region:
E         text("Option With Empty Addname")}) <index:option-with-empty-addname>]
E         strong({text("--sep")})
E         [#metadata(none) <index:cmdoption-sep>]
E       assert 'strong(raw("--sep"))' in '...'
tests/test_signature_typography_gate.py:294: AssertionError

_ TestSignatureTypographyGate.test_sig03_annotation_and_name_wrapper_shapes_are_byte_identical _
E       AssertionError: SIG-03: expected the rst-domain desc_name ':caption:' to emit 'strong(raw(":caption:"))' (contract §5.1 leaf branch), got 'text(":caption:")'
E       assert 'text(":caption:")' == 'strong(raw(":caption:"))'
E         - strong(raw(":caption:"))
E         + text(":caption:")
tests/test_signature_typography_gate.py:323: AssertionError

_ TestSignatureTypographyGate.test_sig04_parameter_names_italic_type_and_default_plain _
E           AssertionError: SIG-04: expected parameter name 'app' to emit 'emph(raw("app"))' (contract §5.2 rule 2), not found in region:
E             text("LaTeXBuilder Class With Nested Method")}) <index:latexbuilder-class-with-nested-method>]
E             strong({text("class") ... text("(") + text("app") + text(", ") + text("env") + ... + text(")")})
E           assert 'emph(raw("app"))' in '...'
tests/test_signature_typography_gate.py:354: AssertionError

_ TestSignatureTypographyGate.test_sig04_resolved_xref_type_annotation_keeps_hyperlink _
E       AssertionError: SIG-04: expected the resolved-xref type annotation to keep its hyperlink, i.e. emit 'link(<index:Foo>, raw("Foo"))', not found in region:
E         ... strong({text("g") text("(") + text("a") + text(":") + text(" ") + link(<index:Foo>, text("Foo")) + text(" ") + text("|") + text(" ") + text("None") ... + text(")")
E         text(" -> ")
E         link(<index:Foo>, text("Foo"))})
E       assert 'link(<index:Foo>, raw("Foo"))' in '...'
tests/test_signature_typography_gate.py:407: AssertionError

_ TestSignatureTypographyGate.test_sig04_generic_type_and_quoted_forward_ref_are_plain _
E       AssertionError: SIG-04: expected the generic type's head 'list' to emit 'raw("list")', not found in region: ...
E       assert 'raw("list")' in '...'
E        +  where 'raw("list")' = _expected_raw('list')
tests/test_signature_typography_gate.py:426: AssertionError

__ TestSignatureTypographyGate.test_sig05_delimiters_use_monospace_primitive ___
E       AssertionError: SIG-05: expected the delimiter 'raw("(")' (contract §6) to appear somewhere in the emitted document
E       assert 'raw("(")' in '// Essential package imports\n#import "@preview/codly:1.3.0": *\n...'
tests/test_signature_typography_gate.py:448: AssertionError

_ TestSignatureTypographyGate.test_sig05_empty_parameter_list_no_comma_separator _
E       AssertionError: SIG-05: expected the empty parameter list to emit 'raw("(") + raw(")")' with no separator, not found in region:
E         text("Empty Parameter List")}) <index:empty-parameter-list>]
E         strong({text("empty_params")
E         text("(") + text(")")})
E         [#metadata(none) <index:empty_params>]
E       assert 'raw("(") + raw(")")' in '...'
tests/test_signature_typography_gate.py:457: AssertionError

_ TestSignatureTypographyGate.test_sig05_optional_group_separator_lands_inside_bracket _
E       AssertionError: SIG-05 D-11: expected the optional-group separator to land INSIDE the bracket ('+ raw(", ") + raw("]")'), not found in region:
E         text("Optional Group Followed By A Parameter (D-11 Adjacency)")}) <index:optional-group-followed-by-a-parameter-d-11-adjacency>]
E         strong({text("connect")
E         text("(") + text("host") + text(", ") + text("port") + text("=") + text("8080") + text(", ") + text("[") + text("timeout") + text("]") + text("**kwargs") + text(")")})
E       assert '+ raw(", ") + raw("]")' in '...'
tests/test_signature_typography_gate.py:475: AssertionError

_ TestSignatureTypographyGate.test_sig05_nested_optional_groups_close_in_reverse_open_order _
E       AssertionError: SIG-05 ordering: expected the exact nested-bracket structure 'raw("(") + emph(raw("fmt")) + raw(", ") + raw("[") + emph(raw("args")) + raw(", ") + raw("[") + emph(raw("more")) + raw("]") + raw("]") + raw(")")' (fmt/args/more each get their own italic name call, and neither desc_optional gains a comma since both are last children), not found in region:
E         text("Nested Optional Groups (SIG-05 Ordering)")}) <index:nested-optional-groups-sig-05-ordering>]
E         strong({text("printf")
E         text("(") + text("fmt") + text(", ") + text("[") + text("args") + text(", ") + text("[") + text("more") + text("]") + text("]") + text(")")})
E       assert 'raw("(") + emph(raw("fmt")) + raw(", ") + raw("[") + emph(raw("args")) + raw(", ") + raw("[") + emph(raw("more")) + raw("]") + raw("]") + raw(")")' in '...'
tests/test_signature_typography_gate.py:512: AssertionError

_ TestSignatureTypographyGate.test_encoding_non_ascii_signature_round_trips_code_points _
E       AssertionError: Encoding: expected the non-ASCII desc_name to emit 'strong(raw("café"))', not found in region:
E         text("Non-ASCII Signature")}) <index:non-ascii-signature>]
E         strong({text("café")
E         text("(") + text("naïve") + text(":") + text(" ") + text("int") + text(" ") + text("=") + text(" ") + text("0") + text(")")
E         text(" -> ")
E         text("None")})
E       assert 'strong(raw("caf\xe9"))' in '...'
tests/test_signature_typography_gate.py:531: AssertionError

=========================== short test summary info ============================
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig01_leaf_desc_name_bold_monospace - AssertionError: SIG-01: expected the leaf desc_name 'LaTeXBuilder' to emit 'strong(raw("LaTeXBuilder"))' (contract §5.1 leaf branch), not found in region: ...
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig01_nonleaf_desc_name_bold_via_nested_desc_sig_name - AssertionError: SIG-01: expected the non-leaf desc_name's nested desc_sig_name 'cpp_probe' to emit 'strong(raw("cpp_probe"))' (contract §5.2 rule 1), not found in region: ...
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_addname_plain_monospace_with_zwsp_and_no_enclosing_bold - AssertionError: SIG-02: expected the dotted qualifier to emit 'raw("sphinx.\u{200B}builders.\u{200B}latex.\u{200B}")' (contract §4 step 3's ZWSP escape after every '.'), not found in region: ...
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_addname_and_name_are_two_separate_expressions - AssertionError: SIG-02 adjacency: expected both the addname and name calls to be present in region: ...
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_empty_addname_emits_zero_bytes - AssertionError: SIG-02: expected the desc_name '--sep' to emit 'strong(raw("--sep"))', not found in region: ...
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig03_annotation_and_name_wrapper_shapes_are_byte_identical - AssertionError: SIG-03: expected the rst-domain desc_name ':caption:' to emit 'strong(raw(":caption:"))' (contract §5.1 leaf branch), got 'text(":caption:")'
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_parameter_names_italic_type_and_default_plain - AssertionError: SIG-04: expected parameter name 'app' to emit 'emph(raw("app"))' (contract §5.2 rule 2), not found in region: ...
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_resolved_xref_type_annotation_keeps_hyperlink - AssertionError: SIG-04: expected the resolved-xref type annotation to keep its hyperlink, i.e. emit 'link(<index:Foo>, raw("Foo"))', not found in region: ...
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_generic_type_and_quoted_forward_ref_are_plain - AssertionError: SIG-04: expected the generic type's head 'list' to emit 'raw("list")', not found in region: ...
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_delimiters_use_monospace_primitive - AssertionError: SIG-05: expected the delimiter 'raw("(")' (contract §6) to appear somewhere in the emitted document
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_empty_parameter_list_no_comma_separator - AssertionError: SIG-05: expected the empty parameter list to emit 'raw("(") + raw(")")' with no separator, not found in region: ...
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_optional_group_separator_lands_inside_bracket - AssertionError: SIG-05 D-11: expected the optional-group separator to land INSIDE the bracket ('+ raw(", ") + raw("]")'), not found in region: ...
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_nested_optional_groups_close_in_reverse_open_order - AssertionError: SIG-05 ordering: expected the exact nested-bracket structure 'raw("(") + emph(raw("fmt")) + raw(", ") + raw("[") + emph(raw("args")) + raw(", ") + raw("[") + emph(raw("more")) + raw("]") + raw("]") + raw(")")' (fmt/args/more each get their own italic name call, and neither desc_optional gains a comma since both are last children), not found in region: ...
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_encoding_non_ascii_signature_round_trips_code_points - AssertionError: Encoding: expected the non-ASCII desc_name to emit 'strong(raw("café"))', not found in region: ...
========================= 14 failed, 1 passed in 0.85s =========================
```

Note: the full untruncated version of each `AssertionError` (with the complete
emitted-region text, not the `...`-elided excerpts above) was captured
verbatim in the executor's session output at capture time; the excerpts above
preserve every assertion's diagnostic head and tail (the load-bearing
`assert X in/== Y` line and the requirement id) while eliding the repeated
full-region dumps for document length. The elision never removes a distinct
failure — all 14 node ids above have a corresponding block.

## Pre-change whole-suite baseline

```
uv run pytest -m "not slow" -q
```

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-afa998ce5b426e19e
configfile: pyproject.toml
testpaths: tests
plugins: cov-7.1.0
collected 669 items / 29 deselected / 640 selected

[... 626 passed across every other test file, unaffected by this plan ...]

FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig01_leaf_desc_name_bold_monospace
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig01_nonleaf_desc_name_bold_via_nested_desc_sig_name
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_addname_plain_monospace_with_zwsp_and_no_enclosing_bold
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_addname_and_name_are_two_separate_expressions
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig02_empty_addname_emits_zero_bytes
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig03_annotation_and_name_wrapper_shapes_are_byte_identical
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_parameter_names_italic_type_and_default_plain
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_resolved_xref_type_annotation_keeps_hyperlink
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig04_generic_type_and_quoted_forward_ref_are_plain
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_delimiters_use_monospace_primitive
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_empty_parameter_list_no_comma_separator
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_optional_group_separator_lands_inside_bracket
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_sig05_nested_optional_groups_close_in_reverse_open_order
FAILED tests/test_signature_typography_gate.py::TestSignatureTypographyGate::test_encoding_non_ascii_signature_round_trips_code_points
================ 14 failed, 626 passed, 29 deselected in 45.92s ================
```

**The failure count (14) matches EXACTLY this plan's intentional REDs, enumerated
by node id above.** No other test file regressed — `typsphinx/translator.py` is
untouched, so every pre-existing render-gate/unit/integration test stays green.
A later wave verifies by set difference over these 14 node ids, never by count
(the count will change again as plans 37-02..04 add their own RED node ids in
the same wave).

## Pre-change lint/type trio

```
$ uv run black --check .
All done! ✨ 🍰 ✨
177 files would be left unchanged.
Exit: 0

$ uv run ruff check .
All checks passed!
Exit: 0

$ uv run mypy typsphinx/
Success: no issues found in 6 source files
Exit: 0
```

All three pass. This plan adds only tests and docs (a fixture project and a
gate module); a lint failure here would indicate the new test module is
malformed, and there is none.

## BEFORE state — emitted `index.typ` (pre-phase, untouched translator)

Full pre-phase output of `uv run python -m sphinx -b typst
tests/fixtures/signature_typography_gate <tmp>`, quoted in full, labelled BEFORE.
This is the byte-for-byte baseline every SIG-01..05 assertion above measures
against; the AFTER state (once `typsphinx/translator.py` is edited in later
waves) is expected to differ at every RED node id and nowhere else.

```typst
// Essential package imports
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

#show: codly-init.with()
#codly(languages: codly-languages)

#import "_template.typ": project

#show: project.with(
  title: "Signature Typography Gate",
  authors: ("typsphinx tests",),
  date: "0.0.0",
  lang: "en",
)

#{
[#heading(level: 1, {text("Signature Typography Gate")}) <index:signature-typography-gate>]

par({text("This fixture exists solely to be built through ")
raw("-b typst")
text(" and to produce, in ONE build, every doctree shape SIG-01..SIG-05 (Phase 37) must be judged on: ")
raw("desc_annotation")
text(", ")
raw("desc_addname")
text(", a leaf ")
raw("desc_name")
text(", a non-leaf (C++) ")
raw("desc_name")
text(", all eight measured ")
raw("desc_parameter")
text(" shapes, an empty ")
raw("desc_parameterlist")
text(", an empty ")
raw("desc_addname")
text(", and a non-ASCII signature. It is not meant to be read as prose – ")
raw("tests/test_signature_typography_gate.py")
text(" slices this document’s emitted ")
raw(".typ")
text(" by the section headings below, each of which is deliberately distinctive so an assertion about one sub-part cannot be satisfied by bytes belonging to a different signature.")})

par({text("No ")
raw(".. rubric::")
text(" directive and no ")
raw("**bold**")
text(" inline markup appear anywhere in this file (Phase 36/Phase 39 territory, kept out on purpose).")})

[#heading(level: 2, {text("LaTeXBuilder Class With Nested Method")}) <index:latexbuilder-class-with-nested-method>]

strong({text("class")
text(" ")
text("sphinx.builders.latex.")
text("LaTeXBuilder")
text("(") + text("app") + text(", ") + text("env") + text(", ") + text("*") + text(", ") + text("extra") + text("=") + text("None") + text(", ") + text("verbosity") + text(":") + text(" ") + text("int") + text(" ") + text("=") + text(" ") + text("0") + text(")")})
[#metadata(none) <index:sphinx.builders.latex.LaTeXBuilder>]
par({text("A builder. Supplies a bold ")
raw("desc_annotation")
text(" (“class”), a dotted ")
raw("desc_addname")
text(" (")
raw("sphinx.builders.latex.")
text("), a leaf ")
raw("desc_name")
text(", the bare keyword-only separator parameter, a defaulted parameter, and an annotated-plus-defaulted parameter.")})

strong({text("write_documents")
text("(") + text("docnames") + text(":") + text(" ") + text("set") + text("[") + text("str") + text("]") + text(", ") + text("*") + text(", ") + text("force") + text(":") + text(" ") + text("bool") + text(" ") + text("=") + text(" ") + text("False") + text(")")
text(" -> ")
text("None")})
[#metadata(none) <index:sphinx.builders.latex.LaTeXBuilder.write_documents>]
par({text("Write docs. Supplies a generic subscript type annotation (")
raw("set[str]")
text(") and a ")
raw("desc_returns")
text(".")})

parbreak()
parbreak()

[#heading(level: 2, {text("Foo Class And Resolved Cross-Reference Function")}) <index:foo-class-and-resolved-cross-reference-function>]

strong({text("class")
text(" ")
text("Foo")})
[#metadata(none) <index:Foo>]
par({text("A class used as a resolved cross-reference target.")})

parbreak()
strong({text("g")
text("(") + text("a") + text(":") + text(" ") + link(<index:Foo>, text("Foo")) + text(" ") + text("|") + text(" ") + text("None") + text(" ") + text("=") + text(" ") + text("None") + text(", ") + text("b") + text(":") + text(" ") + text("list") + text("[") + text("int") + text("]") + text(" ") + text("=") + text(" ") + text("[]") + text(", ") + text("c") + text(":") + text(" ") + text("'Bar'") + text(" ") + text("=") + text(" ") + text("None") + text(")")
text(" -> ")
link(<index:Foo>, text("Foo"))})
[#metadata(none) <index:g>]
par({text("A function with a resolved cross-reference inside a type annotation (")
raw("Foo")
text("), a union type, a generic type (")
raw("list[int]")
text("), and a quoted forward reference (")
raw("\"Bar\"")
text(", a ")
raw("desc_sig_literal_string")
text(").")})

parbreak()

[#heading(level: 2, {text("Star Args And Kwargs")}) <index:star-args-and-kwargs>]

strong({text("h")
text("(") + text("*") + text("args") + text(", ") + text("**") + text("kwargs") + text(")")})
[#metadata(none) <index:h>]
par({text("A function with the star operator forms.")})

parbreak()

[#heading(level: 2, {text("Optional Group Followed By A Parameter (D-11 Adjacency)")}) <index:optional-group-followed-by-a-parameter-d-11-adjacency>]

strong({text("connect")
text("(") + text("host") + text(", ") + text("port") + text("=") + text("8080") + text(", ") + text("[") + text("timeout") + text("]") + text("**kwargs") + text(")")})
[#metadata(none) <index:connect>]
par({text("A function whose trailing optional-parameter group is immediately followed by a further parameter – the D-11 dropped-separator case (Sphinx’s own HTML renders the comma ")
emph({text("inside")})
text(" the closing bracket).")})

parbreak()

[#heading(level: 2, {text("Nested Optional Groups (SIG-05 Ordering)")}) <index:nested-optional-groups-sig-05-ordering>]

strong({text("printf")
text("(") + text("fmt") + text(", ") + text("[") + text("args") + text(", ") + text("[") + text("more") + text("]") + text("]") + text(")")})
[#metadata(none) <index:printf>]
par({text("A function with two nested optional-parameter groups, both of which are trailing (last children) – the D-11 non-regression control, and the SIG-05 nested-bracket close-order case (inner ")
raw("more")
text(" closes before outer ")
raw("args")
text(").")})

parbreak()

[#heading(level: 2, {text("C++ Non-Leaf Name")}) <index:c-non-leaf-name>]

strong({text("void")
text(" ")
text("cpp_probe")
text("(") + text("int") + text(" ") + text("x") + text(")")})
[#metadata(none) <index:_CPPv49cpp_probei>]
[#metadata(none) <index:_CPPv39cpp_probei>]
[#metadata(none) <index:_CPPv29cpp_probei>]
[#metadata(none) <index:cpp_probe__i>]
par({text("Supplies ")
raw("desc_sig_keyword_type")
text(" and a NON-LEAF ")
raw("desc_name")
text(" (the C++ domain nests a ")
raw("desc_sig_name")
text(" inside ")
raw("desc_name")
text(").")})

parbreak()

[#heading(level: 2, {text("Empty Parameter List")}) <index:empty-parameter-list>]

strong({text("empty_params")
text("(") + text(")")})
[#metadata(none) <index:empty_params>]
par({text("Supplies the empty-parameter-list edge.")})

parbreak()

[#heading(level: 2, {text("Option With Empty Addname")}) <index:option-with-empty-addname>]

strong({text("--sep")})
[#metadata(none) <index:cmdoption-sep>]
par({text("If specified, separate source and build directories. Supplies a ")
raw("desc_name")
text(" with an EMPTY sibling ")
raw("desc_addname")
text(".")})

parbreak()

[#heading(level: 2, {text("RST Directive Option Text-Leaf Sameness Control")}) <index:rst-directive-option-text-leaf-sameness-control>]

strong({text(".. probe::")})
[#metadata(none) <index:directive-probe>]
par({text("A probe directive, only to host an option beneath it.")})

strong({text(":caption:")
text(" text")})
[#metadata(none) <index:directive-option-probe-caption>]
par({text("Caption text. Both the directive-option name (")
raw("desc_name")
text(") and its argument (")
raw("desc_annotation")
text(") arrive as text-only leaves in the SAME signature – the concrete “sameness” pair SIG-03 is judged on (contract section 5.1’s “rst-domain case”).")})

parbreak()
parbreak()

[#heading(level: 2, {text("Non-ASCII Signature")}) <index:non-ascii-signature>]

strong({text("café")
text("(") + text("naïve") + text(":") + text(" ") + text("int") + text(" ") + text("=") + text(" ") + text("0") + text(")")
text(" -> ")
text("None")})
[#metadata(none) <index:cafe>]
par({text("A function whose name and one parameter name both carry accented Latin characters (present in DejaVu Sans Mono) – the SIG-01/SIG-04 encoding edge.")})

parbreak()


}
```

## Structural, not compile, RED

`tests/test_signature_typography_gate.py` drives `sys.executable -m sphinx -b
typst` only — there is no `typst.compile()` leg in this module, so a compile
failure is structurally impossible here. Every one of the 14 REDs above is a
Python-level `assert` on the emitted `.typ` string (substring presence,
equality, or negative-absence), matching milestone invariant #4's amendment:
"every design defect in this milestone compiles fine today, so RED is a
structural / regex / pypdf-text assertion defined before any code is written."
