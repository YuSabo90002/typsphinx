# Phase 38 Plan 02 — Gate Evidence: FLD-02 / FLD-03 Structural RED

**Recorded:** 2026-08-01, against the untouched translator (this plan does not touch `typsphinx/`).
**Command:** `uv run pytest tests/test_field_body_typography_render_gate.py -v`
**Result:** 15 failed, 5 passed in 1.02s (initial run, before the confval control cross-check below).

This file is the verbatim RED evidence required by ROADMAP SC#5 / milestone invariant #4: every
expected string in `tests/test_field_body_typography_render_gate.py` was hand-derived from
`38-EMISSION-CONTRACT.md` sections 4-5 (never from running new translator code, since none exists
yet), and this document records what that hand-derivation measures against the real, unmodified
tree.

## 1. Verbatim pytest output

Full, unedited output of `uv run pytest tests/test_field_body_typography_render_gate.py -v`:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-afc6f2d4e41d07293/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-afc6f2d4e41d07293
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 20 items

tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_name_bold_monospace[multi-value-alpha] FAILED [  5%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_name_bold_monospace[multi-value-beta] FAILED [ 10%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_name_bold_monospace[single-entry] FAILED [ 15%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_name_bold_monospace[non-ascii] FAILED [ 20%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_type_italic_monospace[multi-value-alpha] FAILED [ 25%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_type_italic_monospace[multi-value-beta] FAILED [ 30%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_type_italic_monospace[single-entry] FAILED [ 35%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_type_italic_monospace[non-ascii] FAILED [ 40%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_field_label_unchanged_and_distinct_from_name_and_type PASSED [ 45%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_typeless_param_exactly_one_bold_mono_zero_italic_mono FAILED [ 50%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_nonascii_param_name_roundtrips_codepoints FAILED [ 55%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_no_zero_width_space_anywhere_in_field_bodies PASSED [ 60%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_resolvable_type_composes_inside_link_unchanged_label FAILED [ 65%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_single_value_returns_no_block_paragraph_wrapper FAILED [ 70%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_single_value_pdf_adjacency_matches_pinned_string FAILED [ 75%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_single_entry_param_renders_inline_prose_never_bulleted FAILED [ 80%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_consecutive_single_value_fields_stay_on_separate_lines PASSED [ 85%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_bulleted_multi_value_non_regression_control PASSED [ 90%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld01_field_list_wrapper_nested_inside_desc_content_wrapper FAILED [ 95%]
tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_determinism_two_builds_produce_byte_identical_typ PASSED [100%]

=================================== FAILURES ===================================
_ TestFieldBodyTypographyGate.test_fld03_param_name_bold_monospace[multi-value-alpha] _

self = <test_field_body_typography_render_gate.TestFieldBodyTypographyGate object at 0x7d5ce40f0550>
typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...g(text("Returns") + text(": "))\npar({text("The only field in this function’s field list.")})\n\n\n\nparbreak()\n\n}\n'
heading = 'Multi-Value Bulleted Control'
next_heading = 'Single-Entry Collapsed Param', name = 'alpha', type_text = 'str'

    @pytest.mark.parametrize(
        "heading, next_heading, name, type_text", _PARAM_NAME_TYPE_CASES
    )
    def test_fld03_param_name_bold_monospace(
        self, typ_text: str, heading: str, next_heading: str, name: str, type_text: str
    ) -> None:
        """FLD-03 sub-part NAME: the parameter name's emitted call is
        exactly strong(raw("<escaped>")) -- bold monospace (contract
        section 5.2 row 1). The pre-phase delegation emits bold
        PROPORTIONAL (strong({text(...)})) instead."""
        region = _section(typ_text, heading, next_heading)
        expected = _expected_bold_mono(name)
>       assert expected in region, (
            f"FLD-03: expected the parameter name {name!r} to emit "
            f"{expected!r} (contract section 5.2 row 1), not found in "
            f"region:\n{region}"
        )
E       AssertionError: FLD-03: expected the parameter name 'alpha' to emit 'strong(raw("alpha"))' (contract section 5.2 row 1), not found in region:
E         text("Multi-Value Bulleted Control")}) <index:multi-value-bulleted-control>]
E         
E         block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_multi_value_bulleted"))
E         raw("(") + emph(raw("alpha")) + raw(", ") + emph(raw("beta")) + raw(")")}))
E         [#metadata(none) <index:field_multi_value_bulleted>]
E         strong(text("Parameters") + text(": "))
E         list({
E         parbreak()
E         
E         strong({text("alpha")})
E         text(" (")
E         emph({text("str")})
E         text(")")
E         text(" – ")
E         text("The first bulleted parameter.")
E         }, {
E         parbreak()
E         
E         strong({text("beta")})
E         text(" (")
E         emph({text("int")})
E         text(")")
E         text(" – ")
E         text("The second bulleted parameter.")
E         })
E         
E         
E         
E         parbreak()
E         
E         [#heading(level: 1, {
E       assert 'strong(raw("alpha"))' in 'text("Multi-Value Bulleted Control")}) <index:multi-value-bulleted-control>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_multi_value_bulleted"))\nraw("(") + emph(raw("alpha")) + raw(", ") + emph(raw("beta")) + raw(")")}))\n[#metadata(none) <index:field_multi_value_bulleted>]\nstrong(text("Parameters") + text(": "))\nlist({\nparbreak()\n\nstrong({text("alpha")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" \u2013 ")\ntext("The first bulleted parameter.")\n}, {\nparbreak()\n\nstrong({text("beta")})\ntext(" (")\nemph({text("int")})\ntext(")")\ntext(" \u2013 ")\ntext("The second bulleted parameter.")\n})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'

tests/test_field_body_typography_render_gate.py:255: AssertionError
_ TestFieldBodyTypographyGate.test_fld03_param_name_bold_monospace[multi-value-beta] _

self = <test_field_body_typography_render_gate.TestFieldBodyTypographyGate object at 0x7d5ce40f07d0>
typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...g(text("Returns") + text(": "))\npar({text("The only field in this function’s field list.")})\n\n\n\nparbreak()\n\n}\n'
heading = 'Multi-Value Bulleted Control'
next_heading = 'Single-Entry Collapsed Param', name = 'beta', type_text = 'int'

    @pytest.mark.parametrize(
        "heading, next_heading, name, type_text", _PARAM_NAME_TYPE_CASES
    )
    def test_fld03_param_name_bold_monospace(
        self, typ_text: str, heading: str, next_heading: str, name: str, type_text: str
    ) -> None:
        """FLD-03 sub-part NAME: the parameter name's emitted call is
        exactly strong(raw("<escaped>")) -- bold monospace (contract
        section 5.2 row 1). The pre-phase delegation emits bold
        PROPORTIONAL (strong({text(...)})) instead."""
        region = _section(typ_text, heading, next_heading)
        expected = _expected_bold_mono(name)
>       assert expected in region, (
            f"FLD-03: expected the parameter name {name!r} to emit "
            f"{expected!r} (contract section 5.2 row 1), not found in "
            f"region:\n{region}"
        )
E       AssertionError: FLD-03: expected the parameter name 'beta' to emit 'strong(raw("beta"))' (contract section 5.2 row 1), not found in region:
E         text("Multi-Value Bulleted Control")}) <index:multi-value-bulleted-control>]
E         
E         block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_multi_value_bulleted"))
E         raw("(") + emph(raw("alpha")) + raw(", ") + emph(raw("beta")) + raw(")")}))
E         [#metadata(none) <index:field_multi_value_bulleted>]
E         strong(text("Parameters") + text(": "))
E         list({
E         parbreak()
E         
E         strong({text("alpha")})
E         text(" (")
E         emph({text("str")})
E         text(")")
E         text(" – ")
E         text("The first bulleted parameter.")
E         }, {
E         parbreak()
E         
E         strong({text("beta")})
E         text(" (")
E         emph({text("int")})
E         text(")")
E         text(" – ")
E         text("The second bulleted parameter.")
E         })
E         
E         
E         
E         parbreak()
E         
E         [#heading(level: 1, {
E       assert 'strong(raw("beta"))' in 'text("Multi-Value Bulleted Control")}) <index:multi-value-bulleted-control>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_multi_value_bulleted"))\nraw("(") + emph(raw("alpha")) + raw(", ") + emph(raw("beta")) + raw(")")}))\n[#metadata(none) <index:field_multi_value_bulleted>]\nstrong(text("Parameters") + text(": "))\nlist({\nparbreak()\n\nstrong({text("alpha")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" \u2013 ")\ntext("The first bulleted parameter.")\n}, {\nparbreak()\n\nstrong({text("beta")})\ntext(" (")\nemph({text("int")})\ntext(")")\ntext(" \u2013 ")\ntext("The second bulleted parameter.")\n})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'

tests/test_field_body_typography_render_gate.py:255: AssertionError
_ TestFieldBodyTypographyGate.test_fld03_param_name_bold_monospace[single-entry] _

self = <test_field_body_typography_render_gate.TestFieldBodyTypographyGate object at 0x7d5ce40c4fc0>
typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...g(text("Returns") + text(": "))\npar({text("The only field in this function’s field list.")})\n\n\n\nparbreak()\n\n}\n'
heading = 'Single-Entry Collapsed Param'
next_heading = 'Single-Value Fields Returns Rtype Raises', name = 'only'
type_text = 'str'

    @pytest.mark.parametrize(
        "heading, next_heading, name, type_text", _PARAM_NAME_TYPE_CASES
    )
    def test_fld03_param_name_bold_monospace(
        self, typ_text: str, heading: str, next_heading: str, name: str, type_text: str
    ) -> None:
        """FLD-03 sub-part NAME: the parameter name's emitted call is
        exactly strong(raw("<escaped>")) -- bold monospace (contract
        section 5.2 row 1). The pre-phase delegation emits bold
        PROPORTIONAL (strong({text(...)})) instead."""
        region = _section(typ_text, heading, next_heading)
        expected = _expected_bold_mono(name)
>       assert expected in region, (
            f"FLD-03: expected the parameter name {name!r} to emit "
            f"{expected!r} (contract section 5.2 row 1), not found in "
            f"region:\n{region}"
        )
E       AssertionError: FLD-03: expected the parameter name 'only' to emit 'strong(raw("only"))' (contract section 5.2 row 1), not found in region:
E         text("Single-Entry Collapsed Param")}) <index:single-entry-collapsed-param>]
E         
E         block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_entry_param"))
E         raw("(") + emph(raw("only")) + raw(")")}))
E         [#metadata(none) <index:field_single_entry_param>]
E         strong(text("Parameters") + text(": "))
E         par({strong({text("only")})
E         text(" (")
E         emph({text("str")})
E         text(")")
E         text(" – ")
E         text("The lone parameter, collapsed to one paragraph body.")})
E         
E         
E         
E         parbreak()
E         
E         [#heading(level: 1, {
E       assert 'strong(raw("only"))' in 'text("Single-Entry Collapsed Param")}) <index:single-entry-collapsed-param>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_entry_param"))\nraw("(") + emph(raw("only")) + raw(")")}))\n[#metadata(none) <index:field_single_entry_param>]\nstrong(text("Parameters") + text(": "))\npar({strong({text("only")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" \u2013 ")\ntext("The lone parameter, collapsed to one paragraph body.")})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'

tests/test_field_body_typography_render_gate.py:255: AssertionError
_ TestFieldBodyTypographyGate.test_fld03_param_name_bold_monospace[non-ascii] __

self = <test_field_body_typography_render_gate.TestFieldBodyTypographyGate object at 0x7d5ce40c5220>
typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...g(text("Returns") + text(": "))\npar({text("The only field in this function’s field list.")})\n\n\n\nparbreak()\n\n}\n'
heading = 'Non-ASCII Parameter Name', next_heading = 'Collapsed Inline Control'
name = '名前', type_text = 'str'

    @pytest.mark.parametrize(
        "heading, next_heading, name, type_text", _PARAM_NAME_TYPE_CASES
    )
    def test_fld03_param_name_bold_monospace(
        self, typ_text: str, heading: str, next_heading: str, name: str, type_text: str
    ) -> None:
        """FLD-03 sub-part NAME: the parameter name's emitted call is
        exactly strong(raw("<escaped>")) -- bold monospace (contract
        section 5.2 row 1). The pre-phase delegation emits bold
        PROPORTIONAL (strong({text(...)})) instead."""
        region = _section(typ_text, heading, next_heading)
        expected = _expected_bold_mono(name)
>       assert expected in region, (
            f"FLD-03: expected the parameter name {name!r} to emit "
            f"{expected!r} (contract section 5.2 row 1), not found in "
            f"region:\n{region}"
        )
E       AssertionError: FLD-03: expected the parameter name '名前' to emit 'strong(raw("名前"))' (contract section 5.2 row 1), not found in region:
E         text("Non-ASCII Parameter Name")}) <index:non-ascii-parameter-name>]
E         
E         block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_nonascii_param"))
E         raw("(") + emph(raw("x")) + raw(")")}))
E         [#metadata(none) <index:field_nonascii_param>]
E         strong(text("Parameters") + text(": "))
E         par({strong({text("名前")})
E         text(" (")
E         emph({text("str")})
E         text(")")
E         text(" – ")
E         text("説明文です, a non-ASCII parameter name and description.")})
E         
E         
E         
E         parbreak()
E         
E         [#heading(level: 1, {
E       assert 'strong(raw("\u540d\u524d"))' in 'text("Non-ASCII Parameter Name")}) <index:non-ascii-parameter-name>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_nonascii_param"))\nraw("(") + emph(raw("x")) + raw(")")}))\n[#metadata(none) <index:field_nonascii_param>]\nstrong(text("Parameters") + text(": "))\npar({strong({text("\u540d\u524d")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" \u2013 ")\ntext("\u8aac\u660e\u6587\u3067\u3059, a non-ASCII parameter name and description.")})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'

tests/test_field_body_typography_render_gate.py:255: AssertionError
_ TestFieldBodyTypographyGate.test_fld03_param_type_italic_monospace[multi-value-alpha] _

self = <test_field_body_typography_render_gate.TestFieldBodyTypographyGate object at 0x7d5ce40b69f0>
typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...g(text("Returns") + text(": "))\npar({text("The only field in this function’s field list.")})\n\n\n\nparbreak()\n\n}\n'
heading = 'Multi-Value Bulleted Control'
next_heading = 'Single-Entry Collapsed Param', name = 'alpha', type_text = 'str'

    @pytest.mark.parametrize(
        "heading, next_heading, name, type_text", _PARAM_NAME_TYPE_CASES
    )
    def test_fld03_param_type_italic_monospace(
        self, typ_text: str, heading: str, next_heading: str, name: str, type_text: str
    ) -> None:
        """FLD-03 sub-part TYPE: the parameter type's emitted call is
        exactly emph(raw("<escaped>")) -- italic monospace (contract
        section 5.2 row 2). The pre-phase delegation emits italic
        PROPORTIONAL (emph({text(...)})) instead."""
        region = _section(typ_text, heading, next_heading)
        expected = _expected_italic_mono(type_text)
>       assert expected in region, (
            f"FLD-03: expected the type {type_text!r} to emit {expected!r} "
            f"(contract section 5.2 row 2), not found in region:\n{region}"
        )
E       AssertionError: FLD-03: expected the type 'str' to emit 'emph(raw("str"))' (contract section 5.2 row 2), not found in region:
E         text("Multi-Value Bulleted Control")}) <index:multi-value-bulleted-control>]
E         
E         block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_multi_value_bulleted"))
E         raw("(") + emph(raw("alpha")) + raw(", ") + emph(raw("beta")) + raw(")")}))
E         [#metadata(none) <index:field_multi_value_bulleted>]
E         strong(text("Parameters") + text(": "))
E         list({
E         parbreak()
E         
E         strong({text("alpha")})
E         text(" (")
E         emph({text("str")})
E         text(")")
E         text(" – ")
E         text("The first bulleted parameter.")
E         }, {
E         parbreak()
E         
E         strong({text("beta")})
E         text(" (")
E         emph({text("int")})
E         text(")")
E         text(" – ")
E         text("The second bulleted parameter.")
E         })
E         
E         
E         
E         parbreak()
E         
E         [#heading(level: 1, {
E       assert 'emph(raw("str"))' in 'text("Multi-Value Bulleted Control")}) <index:multi-value-bulleted-control>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_multi_value_bulleted"))\nraw("(") + emph(raw("alpha")) + raw(", ") + emph(raw("beta")) + raw(")")}))\n[#metadata(none) <index:field_multi_value_bulleted>]\nstrong(text("Parameters") + text(": "))\nlist({\nparbreak()\n\nstrong({text("alpha")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" \u2013 ")\ntext("The first bulleted parameter.")\n}, {\nparbreak()\n\nstrong({text("beta")})\ntext(" (")\nemph({text("int")})\ntext(")")\ntext(" \u2013 ")\ntext("The second bulleted parameter.")\n})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'

tests/test_field_body_typography_render_gate.py:273: AssertionError
_ TestFieldBodyTypographyGate.test_fld03_param_type_italic_monospace[multi-value-beta] _

self = <test_field_body_typography_render_gate.TestFieldBodyTypographyGate object at 0x7d5ce40dc6b0>
typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...g(text("Returns") + text(": "))\npar({text("The only field in this function’s field list.")})\n\n\n\nparbreak()\n\n}\n'
heading = 'Multi-Value Bulleted Control'
next_heading = 'Single-Entry Collapsed Param', name = 'beta', type_text = 'int'

    @pytest.mark.parametrize(
        "heading, next_heading, name, type_text", _PARAM_NAME_TYPE_CASES
    )
    def test_fld03_param_type_italic_monospace(
        self, typ_text: str, heading: str, next_heading: str, name: str, type_text: str
    ) -> None:
        """FLD-03 sub-part TYPE: the parameter type's emitted call is
        exactly emph(raw("<escaped>")) -- italic monospace (contract
        section 5.2 row 2). The pre-phase delegation emits italic
        PROPORTIONAL (emph({text(...)})) instead."""
        region = _section(typ_text, heading, next_heading)
        expected = _expected_italic_mono(type_text)
>       assert expected in region, (
            f"FLD-03: expected the type {type_text!r} to emit {expected!r} "
            f"(contract section 5.2 row 2), not found in region:\n{region}"
        )
E       AssertionError: FLD-03: expected the type 'int' to emit 'emph(raw("int"))' (contract section 5.2 row 2), not found in region:
E         text("Multi-Value Bulleted Control")}) <index:multi-value-bulleted-control>]
E         
E         block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_multi_value_bulleted"))
E         raw("(") + emph(raw("alpha")) + raw(", ") + emph(raw("beta")) + raw(")")}))
E         [#metadata(none) <index:field_multi_value_bulleted>]
E         strong(text("Parameters") + text(": "))
E         list({
E         parbreak()
E         
E         strong({text("alpha")})
E         text(" (")
E         emph({text("str")})
E         text(")")
E         text(" – ")
E         text("The first bulleted parameter.")
E         }, {
E         parbreak()
E         
E         strong({text("beta")})
E         text(" (")
E         emph({text("int")})
E         text(")")
E         text(" – ")
E         text("The second bulleted parameter.")
E         })
E         
E         
E         
E         parbreak()
E         
E         [#heading(level: 1, {
E       assert 'emph(raw("int"))' in 'text("Multi-Value Bulleted Control")}) <index:multi-value-bulleted-control>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_multi_value_bulleted"))\nraw("(") + emph(raw("alpha")) + raw(", ") + emph(raw("beta")) + raw(")")}))\n[#metadata(none) <index:field_multi_value_bulleted>]\nstrong(text("Parameters") + text(": "))\nlist({\nparbreak()\n\nstrong({text("alpha")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" \u2013 ")\ntext("The first bulleted parameter.")\n}, {\nparbreak()\n\nstrong({text("beta")})\ntext(" (")\nemph({text("int")})\ntext(")")\ntext(" \u2013 ")\ntext("The second bulleted parameter.")\n})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'

tests/test_field_body_typography_render_gate.py:273: AssertionError
_ TestFieldBodyTypographyGate.test_fld03_param_type_italic_monospace[single-entry] _

self = <test_field_body_typography_render_gate.TestFieldBodyTypographyGate object at 0x7d5ce40dc8d0>
typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...g(text("Returns") + text(": "))\npar({text("The only field in this function’s field list.")})\n\n\n\nparbreak()\n\n}\n'
heading = 'Single-Entry Collapsed Param'
next_heading = 'Single-Value Fields Returns Rtype Raises', name = 'only'
type_text = 'str'

    @pytest.mark.parametrize(
        "heading, next_heading, name, type_text", _PARAM_NAME_TYPE_CASES
    )
    def test_fld03_param_type_italic_monospace(
        self, typ_text: str, heading: str, next_heading: str, name: str, type_text: str
    ) -> None:
        """FLD-03 sub-part TYPE: the parameter type's emitted call is
        exactly emph(raw("<escaped>")) -- italic monospace (contract
        section 5.2 row 2). The pre-phase delegation emits italic
        PROPORTIONAL (emph({text(...)})) instead."""
        region = _section(typ_text, heading, next_heading)
        expected = _expected_italic_mono(type_text)
>       assert expected in region, (
            f"FLD-03: expected the type {type_text!r} to emit {expected!r} "
            f"(contract section 5.2 row 2), not found in region:\n{region}"
        )
E       AssertionError: FLD-03: expected the type 'str' to emit 'emph(raw("str"))' (contract section 5.2 row 2), not found in region:
E         text("Single-Entry Collapsed Param")}) <index:single-entry-collapsed-param>]
E         
E         block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_entry_param"))
E         raw("(") + emph(raw("only")) + raw(")")}))
E         [#metadata(none) <index:field_single_entry_param>]
E         strong(text("Parameters") + text(": "))
E         par({strong({text("only")})
E         text(" (")
E         emph({text("str")})
E         text(")")
E         text(" – ")
E         text("The lone parameter, collapsed to one paragraph body.")})
E         
E         
E         
E         parbreak()
E         
E         [#heading(level: 1, {
E       assert 'emph(raw("str"))' in 'text("Single-Entry Collapsed Param")}) <index:single-entry-collapsed-param>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_entry_param"))\nraw("(") + emph(raw("only")) + raw(")")}))\n[#metadata(none) <index:field_single_entry_param>]\nstrong(text("Parameters") + text(": "))\npar({strong({text("only")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" \u2013 ")\ntext("The lone parameter, collapsed to one paragraph body.")})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'

tests/test_field_body_typography_render_gate.py:273: AssertionError
_ TestFieldBodyTypographyGate.test_fld03_param_type_italic_monospace[non-ascii] _

self = <test_field_body_typography_render_gate.TestFieldBodyTypographyGate object at 0x7d5ce406e650>
typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...g(text("Returns") + text(": "))\npar({text("The only field in this function’s field list.")})\n\n\n\nparbreak()\n\n}\n'
heading = 'Non-ASCII Parameter Name', next_heading = 'Collapsed Inline Control'
name = '名前', type_text = 'str'

    @pytest.mark.parametrize(
        "heading, next_heading, name, type_text", _PARAM_NAME_TYPE_CASES
    )
    def test_fld03_param_type_italic_monospace(
        self, typ_text: str, heading: str, next_heading: str, name: str, type_text: str
    ) -> None:
        """FLD-03 sub-part TYPE: the parameter type's emitted call is
        exactly emph(raw("<escaped>")) -- italic monospace (contract
        section 5.2 row 2). The pre-phase delegation emits italic
        PROPORTIONAL (emph({text(...)})) instead."""
        region = _section(typ_text, heading, next_heading)
        expected = _expected_italic_mono(type_text)
>       assert expected in region, (
            f"FLD-03: expected the type {type_text!r} to emit {expected!r} "
            f"(contract section 5.2 row 2), not found in region:\n{region}"
        )
E       AssertionError: FLD-03: expected the type 'str' to emit 'emph(raw("str"))' (contract section 5.2 row 2), not found in region:
E         text("Non-ASCII Parameter Name")}) <index:non-ascii-parameter-name>]
E         
E         block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_nonascii_param"))
E         raw("(") + emph(raw("x")) + raw(")")}))
E         [#metadata(none) <index:field_nonascii_param>]
E         strong(text("Parameters") + text(": "))
E         par({strong({text("名前")})
E         text(" (")
E         emph({text("str")})
E         text(")")
E         text(" – ")
E         text("説明文です, a non-ASCII parameter name and description.")})
E         
E         
E         
E         parbreak()
E         
E         [#heading(level: 1, {
E       assert 'emph(raw("str"))' in 'text("Non-ASCII Parameter Name")}) <index:non-ascii-parameter-name>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_nonascii_param"))\nraw("(") + emph(raw("x")) + raw(")")}))\n[#metadata(none) <index:field_nonascii_param>]\nstrong(text("Parameters") + text(": "))\npar({strong({text("\u540d\u524d")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" \u2013 ")\ntext("\u8aac\u660e\u6587\u3067\u3059, a non-ASCII parameter name and description.")})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'

tests/test_field_body_typography_render_gate.py:273: AssertionError
_ TestFieldBodyTypographyGate.test_fld03_typeless_param_exactly_one_bold_mono_zero_italic_mono _

self = <test_field_body_typography_render_gate.TestFieldBodyTypographyGate object at 0x7d5ce4108140>
typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...g(text("Returns") + text(": "))\npar({text("The only field in this function’s field list.")})\n\n\n\nparbreak()\n\n}\n'

    def test_fld03_typeless_param_exactly_one_bold_mono_zero_italic_mono(
        self, typ_text: str
    ) -> None:
        """FLD-03 empty edge: a :param: entry with a name but no :type:
        emits exactly one bold-monospace call and zero italic-monospace
        calls for that entry."""
        region = _section(typ_text, _H_NOTYPE, _H_NONASCII)
        bold_call = _expected_bold_mono("untyped")
        count = region.count(bold_call)
>       assert count == 1, (
            f"FLD-03 empty edge: expected exactly ONE bold-monospace call "
            f"{bold_call!r}, found {count} in region:\n{region}"
        )
E       AssertionError: FLD-03 empty edge: expected exactly ONE bold-monospace call 'strong(raw("untyped"))', found 0 in region:
E         text("Name Without Type")}) <index:name-without-type>]
E         
E         block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_name_without_type"))
E         raw("(") + emph(raw("untyped")) + raw(")")}))
E         [#metadata(none) <index:field_name_without_type>]
E         strong(text("Parameters") + text(": "))
E         par({strong({text("untyped")})
E         text(" – ")
E         text("A parameter with no matching type field.")})
E         
E         
E         
E         parbreak()
E         
E         [#heading(level: 1, {
E       assert 0 == 1

tests/test_field_body_typography_render_gate.py:330: AssertionError
_ TestFieldBodyTypographyGate.test_fld03_nonascii_param_name_roundtrips_codepoints _

self = <test_field_body_typography_render_gate.TestFieldBodyTypographyGate object at 0x7d5ce4108230>
typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...g(text("Returns") + text(": "))\npar({text("The only field in this function’s field list.")})\n\n\n\nparbreak()\n\n}\n'

    def test_fld03_nonascii_param_name_roundtrips_codepoints(
        self, typ_text: str
    ) -> None:
        """FLD-03 encoding edge: field-body name text is escaped by
        escape_typst_string operating on Python str CODE POINTS -- not
        bytes, not grapheme clusters, with no Unicode normalisation. A
        non-ASCII parameter name round-trips its code points unchanged
        into the emitted .typ."""
        region = _section(typ_text, _H_NONASCII, _H_COLLAPSED)
        expected = _expected_bold_mono("名前")
>       assert expected in region, (
            f"FLD-03 encoding: expected the non-ASCII name to round-trip "
            f"into {expected!r}, not found in region:\n{region}"
        )
E       AssertionError: FLD-03 encoding: expected the non-ASCII name to round-trip into 'strong(raw("名前"))', not found in region:
E         text("Non-ASCII Parameter Name")}) <index:non-ascii-parameter-name>]
E         
E         block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_nonascii_param"))
E         raw("(") + emph(raw("x")) + raw(")")}))
E         [#metadata(none) <index:field_nonascii_param>]
E         strong(text("Parameters") + text(": "))
E         par({strong({text("名前")})
E         text(" (")
E         emph({text("str")})
E         text(")")
E         text(" – ")
E         text("説明文です, a non-ASCII parameter name and description.")})
E         
E         
E         
E         parbreak()
E         
E         [#heading(level: 1, {
E       assert 'strong(raw("\u540d\u524d"))' in 'text("Non-ASCII Parameter Name")}) <index:non-ascii-parameter-name>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_nonascii_param"))\nraw("(") + emph(raw("x")) + raw(")")}))\n[#metadata(none) <index:field_nonascii_param>]\nstrong(text("Parameters") + text(": "))\npar({strong({text("\u540d\u524d")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" \u2013 ")\ntext("\u8aac\u660e\u6587\u3067\u3059, a non-ASCII parameter name and description.")})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'

tests/test_field_body_typography_render_gate.py:349: AssertionError
_ TestFieldBodyTypographyGate.test_fld03_resolvable_type_composes_inside_link_unchanged_label _

self = <test_field_body_typography_render_gate.TestFieldBodyTypographyGate object at 0x7d5ce40cf070>
typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...g(text("Returns") + text(": "))\npar({text("The only field in this function’s field list.")})\n\n\n\nparbreak()\n\n}\n'

    def test_fld03_resolvable_type_composes_inside_link_unchanged_label(
        self, typ_text: str
    ) -> None:
        """FLD-03 Pitfall 2: the resolvable :type:'s italic-monospace call
        appears NESTED inside the emitted link() call, and the link's
        label argument is unchanged from the pre-phase build (visit_
        reference is untouched by this phase). A type that keeps its
        glyphs but loses its link must fail this test (T-38-06)."""
        region = _section(typ_text, _H_XREF, _H_NOTYPE)
        link_open = "link(<index:FieldXrefTarget>, "
        assert link_open in region, (
            "FLD-03 Pitfall 2: expected the link's label argument to stay "
            f"unchanged from the pre-phase build ({link_open!r}), not "
            f"found in region:\n{region}"
        )
        expected_type = _expected_italic_mono("FieldXrefTarget")
        pattern = re.escape(link_open) + r"\s*" + re.escape(expected_type) + r"\)"
>       assert re.search(pattern, region), (
            f"FLD-03 Pitfall 2: expected {expected_type!r} to compose "
            f"nested inside the emitted link() call immediately after "
            f"{link_open!r}, not found in region:\n{region}"
        )
E       AssertionError: FLD-03 Pitfall 2: expected 'emph(raw("FieldXrefTarget"))' to compose nested inside the emitted link() call immediately after 'link(<index:FieldXrefTarget>, ', not found in region:
E         text("Resolvable Type Cross Reference")}) <index:resolvable-type-cross-reference>]
E         
E         block(sticky: true, par(hanging-indent: 2.5em, {raw("class")
E         raw(" ")
E         strong(raw("FieldXrefTarget"))}))
E         [#metadata(none) <index:FieldXrefTarget>]
E         par({text("A class defined in this document so its name resolves as a cross-reference from the function below.")})
E         
E         parbreak()
E         block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_resolvable_xref_type"))
E         raw("(") + emph(raw("target")) + raw(")")}))
E         [#metadata(none) <index:field_resolvable_xref_type>]
E         strong(text("Parameters") + text(": "))
E         par({strong({text("target")})
E         text(" (")
E         link(<index:FieldXrefTarget>, 
E         emph({text("FieldXrefTarget")}))
E         text(")")
E         text(" – ")
E         text("A parameter whose type resolves to a local class.")})
E         
E         
E         
E         parbreak()
E         
E         [#heading(level: 1, {
E       assert None
E        +  where None = <function search at 0x7d5ceb17d080>('link\\(<index:FieldXrefTarget>,\\ \\s*emph\\(raw\\("FieldXrefTarget"\\)\\)\\)', 'text("Resolvable Type Cross Reference")}) <index:resolvable-type-cross-reference>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {raw("class")\nraw(" ")\nstrong(raw("FieldXrefTarget"))}))\n[#metadata(none) <index:FieldXrefTarget>]\npar({text("A class defined in this document so its name resolves as a cross-reference from the function below.")})\n\nparbreak()\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_resolvable_xref_type"))\nraw("(") + emph(raw("target")) + raw(")")}))\n[#metadata(none) <index:field_resolvable_xref_type>]\nstrong(text("Parameters") + text(": "))\npar({strong({text("target")})\ntext(" (")\nlink(<index:FieldXrefTarget>, \nemph({text("FieldXrefTarget")}))\ntext(")")\ntext(" \u2013 ")\ntext("A parameter whose type resolves to a local class.")})\n\n\n\nparbreak()\n\n[#heading(level: 1, {')
E        +    where <function search at 0x7d5ceb17d080> = re.search

tests/test_field_body_typography_render_gate.py:397: AssertionError
_ TestFieldBodyTypographyGate.test_fld02_single_value_returns_no_block_paragraph_wrapper _

self = <test_field_body_typography_render_gate.TestFieldBodyTypographyGate object at 0x7d5ce40f8d50>
typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...g(text("Returns") + text(": "))\npar({text("The only field in this function’s field list.")})\n\n\n\nparbreak()\n\n}\n'

    def test_fld02_single_value_returns_no_block_paragraph_wrapper(
        self, typ_text: str
    ) -> None:
        """FLD-02 inline half, structural (D-07): the single-value
        :returns: body's region of the .typ contains no block-level
        paragraph wrapper around the value. Pre-phase, the value is
        unconditionally wrapped in par({...}), which is intrinsically
        block-level and starts a new visual line (contract section 4.2's
        root cause)."""
        region = _section(typ_text, _H_TRIO, _H_XREF)
        forbidden = 'par({text("A short stable value.")})'
>       assert forbidden not in region, (
            "FLD-02/D-07: expected the single-value :returns: body to NOT "
            f"be wrapped in a block-level par(...) call ({forbidden!r} "
            f"must be absent):\n{region}"
        )
E       AssertionError: FLD-02/D-07: expected the single-value :returns: body to NOT be wrapped in a block-level par(...) call ('par({text("A short stable value.")})' must be absent):
E         text("Single-Value Fields Returns Rtype Raises")}) <index:single-value-fields-returns-rtype-raises>]
E         
E         block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_value_trio"))
E         raw("(") + raw(")")}))
E         [#metadata(none) <index:field_single_value_trio>]
E         strong(text("Returns") + text(": "))
E         par({text("A short stable value.")})
E         
E         
E         strong(text("Return type") + text(": "))
E         par({text("str")})
E         
E         
E         strong(text("Raises") + text(": "))
E         par({strong({text("ValueError")})
E         text(" – ")
E         text("If something goes wrong.")})
E         
E         
E         
E         parbreak()
E         
E         [#heading(level: 1, {
E       assert 'par({text("A short stable value.")})' not in 'text("Single-Value Fields Returns Rtype Raises")}) <index:single-value-fields-returns-rtype-raises>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_value_trio"))\nraw("(") + raw(")")}))\n[#metadata(none) <index:field_single_value_trio>]\nstrong(text("Returns") + text(": "))\npar({text("A short stable value.")})\n\n\nstrong(text("Return type") + text(": "))\npar({text("str")})\n\n\nstrong(text("Raises") + text(": "))\npar({strong({text("ValueError")})\ntext(" – ")\ntext("If something goes wrong.")})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'
E         
E         'par({text("A short stable value.")})' is contained here:
E           text("Single-Value Fields Returns Rtype Raises")}) <index:single-value-fields-returns-rtype-raises>]
E           
E           block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_value_trio"))
E           raw("(") + raw(")")}))
E           [#metadata(none) <index:field_single_value_trio>]
E           strong(text("Returns") + text(": "))
E           par({text("A short stable value.")})
E           
E           
E           strong(text("Return type") + text(": "))
E           par({text("str")})
E           
E           
E           strong(text("Raises") + text(": "))
E           par({strong({text("ValueError")})
E           text(" – ")
E           text("If something goes wrong.")})
E           
E           
E           
E           parbreak()
E           
E           [#heading(level: 1, {

tests/test_field_body_typography_render_gate.py:416: AssertionError
_ TestFieldBodyTypographyGate.test_fld02_single_value_pdf_adjacency_matches_pinned_string _

self = <test_field_body_typography_render_gate.TestFieldBodyTypographyGate object at 0x7d5ce40c9250>
pdf_text = 'Field Body Typography Render Gate\ntypsphinx tests\n0.0.0\n1\n1 Contents\nContents\n2 Field Body Typography Render Ga...ault: 99\n10 Single Field List\nfield_single_field_list()\nReturns: \nThe only field in this function’s field list.\n4'

    def test_fld02_single_value_pdf_adjacency_matches_pinned_string(
        self, pdf_text: str
    ) -> None:
        """FLD-02 inline half, compiled-PDF adjacency (D-07): a
        single-value field's label and value are adjacent on ONE line of
        the compiled PDF's extracted text. Mirrors
        tests/test_confval_field_spacing_render_gate.py's pinned-constant
        convention; PINNED_FLD02_ADJACENCY_STRING is hand-derived from
        contract section 4.3 property 1."""
>       assert PINNED_FLD02_ADJACENCY_STRING in pdf_text, (
            f"FLD-02: expected the pinned adjacency string "
            f"{PINNED_FLD02_ADJACENCY_STRING!r} in the extracted PDF "
            f"text -- label and value must share one line:\n{pdf_text!r}"
        )
E       AssertionError: FLD-02: expected the pinned adjacency string 'Returns: A short stable value.' in the extracted PDF text -- label and value must share one line:
E         'Field Body Typography Render Gate\ntypsphinx tests\n0.0.0\n1\n1 Contents\nContents\n2 Field Body Typography Render Gate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n3 Multi-Value Bulleted Control . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n4 Single-Entry Collapsed Param . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n5 Single-Value Fields Returns Rtype Raises . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n6 Resolvable Type Cross Reference . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n7 Name Without Type . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n8 Non-ASCII Parameter Name . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n9 Collapsed Inline Control . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4\n10 Single Field List . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4\n2\n2 Field Body Typography Render Gate\nThis fixture exists solely to be built through -b typst (structural assertions) and compiled to PDF \nvia typst.compile() (glyph and text-extraction assertions) by tests/\ntest_field_body_typography_render_gate.py (Phase 38, FLD-01, FLD-02, FLD-03, D-05, D-06, \nD-07, D-13). It is not meant to be read as prose.\n3 Multi-Value Bulleted Control\nfield_multi_value_bulleted(alpha, beta)\nParameters: \n• alpha (str) – The first bulleted parameter.\n• beta (int) – The second bulleted parameter.\n4 Single-Entry Collapsed Param\nfield_single_entry_param(only)\nParameters: \nonly (str) – The lone parameter, collapsed to one paragraph body.\n5 Single-Value Fields Returns Rtype Raises\nfield_single_value_trio()\nReturns: \nA short stable value.\nReturn type: \nstr\nRaises: \nValueError – If something goes wrong.\n6 Resolvable Type Cross Reference\nclass FieldXrefTarget\nA class defined in this document so its name resolves as a cross-reference from the function below.\nfield_resolvable_xref_type(target)\nParameters: \ntarget (FieldXrefTarget) – A parameter whose type resolves to a local class.\n7 Name Without Type\nfield_name_without_type(untyped)\nParameters: \nuntyped – A parameter with no matching type field.\n8 Non-ASCII Parameter Name\nfield_nonascii_param(x)\nParameters: \n3\n名前 (str) – 説明文です, a non-ASCII parameter name and description.\n9 Collapsed Inline Control\nfield_collapsed_inline_confval\nType: int (a number)  Default: 99\n10 Single Field List\nfield_single_field_list()\nReturns: \nThe only field in this function’s field list.\n4'
E       assert 'Returns: A short stable value.' in 'Field Body Typography Render Gate\ntypsphinx tests\n0.0.0\n1\n1 Contents\nContents\n2 Field Body Typography Render Gate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n3 Multi-Value Bulleted Control . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n4 Single-Entry Collapsed Param . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n5 Single-Value Fields Returns Rtype Raises . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n6 Resolvable Type Cross Reference . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n7 Name Without Type . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n8 Non-ASCII Parameter Name . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n9 Collapsed Inline Control . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4\n10 Single Field List . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4\n2\n2 Field Body Typography Render Gate\nThis fixture exists solely to be built through -b typst (structural assertions) and compiled to PDF \nvia typst.compile() (glyph and text-extraction assertions) by tests/\ntest_field_body_typography_render_gate.py (Phase 38, FLD-01, FLD-02, FLD-03, D-05, D-06, \nD-07, D-13). It is not meant to be read as prose.\n3 Multi-Value Bulleted Control\nfield_multi_value_bulleted(alpha, beta)\nParameters: \n\u2022 alpha (str) \u2013 The first bulleted parameter.\n\u2022 beta (int) \u2013 The second bulleted parameter.\n4 Single-Entry Collapsed Param\nfield_single_entry_param(only)\nParameters: \nonly (str) \u2013 The lone parameter, collapsed to one paragraph body.\n5 Single-Value Fields Returns Rtype Raises\nfield_single_value_trio()\nReturns: \nA short stable value.\nReturn type: \nstr\nRaises: \nValueError \u2013 If something goes wrong.\n6 Resolvable Type Cross Reference\nclass FieldXrefTarget\nA class defined in this document so its name resolves as a cross-reference from the function below.\nfield_resolvable_xref_type(target)\nParameters: \ntarget (FieldXrefTarget) \u2013 A parameter whose type resolves to a local class.\n7 Name Without Type\nfield_name_without_type(untyped)\nParameters: \nuntyped \u2013 A parameter with no matching type field.\n8 Non-ASCII Parameter Name\nfield_nonascii_param(x)\nParameters: \n3\n\u540d\u524d (str) \u2013 \u8aac\u660e\u6587\u3067\u3059, a non-ASCII parameter name and description.\n9 Collapsed Inline Control\nfield_collapsed_inline_confval\nType: int (a number)  Default: 99\n10 Single Field List\nfield_single_field_list()\nReturns: \nThe only field in this function\u2019s field list.\n4'

tests/test_field_body_typography_render_gate.py:431: AssertionError
_ TestFieldBodyTypographyGate.test_fld02_single_entry_param_renders_inline_prose_never_bulleted _

self = <test_field_body_typography_render_gate.TestFieldBodyTypographyGate object at 0x7d5ce40c9490>
typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...g(text("Returns") + text(": "))\npar({text("The only field in this function’s field list.")})\n\n\n\nparbreak()\n\n}\n'

    def test_fld02_single_entry_param_renders_inline_prose_never_bulleted(
        self, typ_text: str
    ) -> None:
        """FLD-02 inline half: docutils' TypedField.make_field
        can_collapse branch produces a single-paragraph field body for a
        lone :param: entry -- structurally identical to :returns:'s
        single-paragraph shape (contract section 4.2), so it must be
        exempted from the block-level par(...) wrapper exactly like
        :returns: is. It must never render as a one-item bulleted list()
        either (already true pre-phase; must stay true)."""
        region = _section(typ_text, _H_SINGLE_ENTRY, _H_TRIO)
        assert "list({" not in region, (
            "FLD-02: a single-entry :param: group must never render as a "
            f"one-item bulleted list:\n{region}"
        )
        forbidden = 'par({strong({text("only")})'
>       assert forbidden not in region, (
            "FLD-02/D-07: expected the single-entry :param:'s field body "
            f"to NOT be wrapped in a block-level par(...) call "
            f"({forbidden!r} must be absent):\n{region}"
        )
E       AssertionError: FLD-02/D-07: expected the single-entry :param:'s field body to NOT be wrapped in a block-level par(...) call ('par({strong({text("only")})' must be absent):
E         text("Single-Entry Collapsed Param")}) <index:single-entry-collapsed-param>]
E         
E         block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_entry_param"))
E         raw("(") + emph(raw("only")) + raw(")")}))
E         [#metadata(none) <index:field_single_entry_param>]
E         strong(text("Parameters") + text(": "))
E         par({strong({text("only")})
E         text(" (")
E         emph({text("str")})
E         text(")")
E         text(" – ")
E         text("The lone parameter, collapsed to one paragraph body.")})
E         
E         
E         
E         parbreak()
E         
E         [#heading(level: 1, {
E       assert 'par({strong({text("only")})' not in 'text("Single-Entry Collapsed Param")}) <index:single-entry-collapsed-param>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_entry_param"))\nraw("(") + emph(raw("only")) + raw(")")}))\n[#metadata(none) <index:field_single_entry_param>]\nstrong(text("Parameters") + text(": "))\npar({strong({text("only")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" – ")\ntext("The lone parameter, collapsed to one paragraph body.")})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'
E         
E         'par({strong({text("only")})' is contained here:
E           text("Single-Entry Collapsed Param")}) <index:single-entry-collapsed-param>]
E           
E           block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_entry_param"))
E           raw("(") + emph(raw("only")) + raw(")")}))
E           [#metadata(none) <index:field_single_entry_param>]
E           strong(text("Parameters") + text(": "))
E           par({strong({text("only")})
E           text(" (")
E           emph({text("str")})
E           text(")")
E           text(" – ")
E           text("The lone parameter, collapsed to one paragraph body.")})
E           
E           
E           
E           parbreak()
E           
E           [#heading(level: 1, {

tests/test_field_body_typography_render_gate.py:453: AssertionError
_ TestFieldBodyTypographyGate.test_fld01_field_list_wrapper_nested_inside_desc_content_wrapper _

self = <test_field_body_typography_render_gate.TestFieldBodyTypographyGate object at 0x7d5ce410c5f0>
typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...g(text("Returns") + text(": "))\npar({text("The only field in this function’s field list.")})\n\n\n\nparbreak()\n\n}\n'

    def test_fld01_field_list_wrapper_nested_inside_desc_content_wrapper(
        self, typ_text: str
    ) -> None:
        """FLD-01 adjacency (field-body view): the field-list wrapper's
        opening token appears strictly after the enclosing desc_content
        wrapper's opening token and strictly before the first field
        label's bytes (contract sections 2 and 3 -- both wrappers share
        the IDENTICAL pad(left: 2.5em, { opening literal, so this is a
        conjunction: two occurrences of the same token, correctly
        ordered)."""
        region = _section(typ_text, _H_TRIO, _H_XREF)
        pad_open = f"pad(left: {SHARED_INDENT_STEP}, {{"
        desc_content_idx = region.find(pad_open)
>       assert desc_content_idx != -1, (
            "FLD-01: expected the enclosing desc_content wrapper's opening "
            f"token {pad_open!r} in region:\n{region}"
        )
E       AssertionError: FLD-01: expected the enclosing desc_content wrapper's opening token 'pad(left: 2.5em, {' in region:
E         text("Single-Value Fields Returns Rtype Raises")}) <index:single-value-fields-returns-rtype-raises>]
E         
E         block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_value_trio"))
E         raw("(") + raw(")")}))
E         [#metadata(none) <index:field_single_value_trio>]
E         strong(text("Returns") + text(": "))
E         par({text("A short stable value.")})
E         
E         
E         strong(text("Return type") + text(": "))
E         par({text("str")})
E         
E         
E         strong(text("Raises") + text(": "))
E         par({strong({text("ValueError")})
E         text(" – ")
E         text("If something goes wrong.")})
E         
E         
E         
E         parbreak()
E         
E         [#heading(level: 1, {
E       assert -1 != -1

tests/test_field_body_typography_render_gate.py:530: AssertionError
=========================== short test summary info ============================
FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_name_bold_monospace[multi-value-alpha] - AssertionError: FLD-03: expected the parameter name 'alpha' to emit 'strong(raw("alpha"))' (contract section 5.2 row 1), not found in region:
  text("Multi-Value Bulleted Control")}) <index:multi-value-bulleted-control>]
  
  block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_multi_value_bulleted"))
  raw("(") + emph(raw("alpha")) + raw(", ") + emph(raw("beta")) + raw(")")}))
  [#metadata(none) <index:field_multi_value_bulleted>]
  strong(text("Parameters") + text(": "))
  list({
  parbreak()
  
  strong({text("alpha")})
  text(" (")
  emph({text("str")})
  text(")")
  text(" – ")
  text("The first bulleted parameter.")
  }, {
  parbreak()
  
  strong({text("beta")})
  text(" (")
  emph({text("int")})
  text(")")
  text(" – ")
  text("The second bulleted parameter.")
  })
  
  
  
  parbreak()
  
  [#heading(level: 1, {
assert 'strong(raw("alpha"))' in 'text("Multi-Value Bulleted Control")}) <index:multi-value-bulleted-control>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_multi_value_bulleted"))\nraw("(") + emph(raw("alpha")) + raw(", ") + emph(raw("beta")) + raw(")")}))\n[#metadata(none) <index:field_multi_value_bulleted>]\nstrong(text("Parameters") + text(": "))\nlist({\nparbreak()\n\nstrong({text("alpha")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" \u2013 ")\ntext("The first bulleted parameter.")\n}, {\nparbreak()\n\nstrong({text("beta")})\ntext(" (")\nemph({text("int")})\ntext(")")\ntext(" \u2013 ")\ntext("The second bulleted parameter.")\n})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'
FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_name_bold_monospace[multi-value-beta] - AssertionError: FLD-03: expected the parameter name 'beta' to emit 'strong(raw("beta"))' (contract section 5.2 row 1), not found in region:
  text("Multi-Value Bulleted Control")}) <index:multi-value-bulleted-control>]
  
  block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_multi_value_bulleted"))
  raw("(") + emph(raw("alpha")) + raw(", ") + emph(raw("beta")) + raw(")")}))
  [#metadata(none) <index:field_multi_value_bulleted>]
  strong(text("Parameters") + text(": "))
  list({
  parbreak()
  
  strong({text("alpha")})
  text(" (")
  emph({text("str")})
  text(")")
  text(" – ")
  text("The first bulleted parameter.")
  }, {
  parbreak()
  
  strong({text("beta")})
  text(" (")
  emph({text("int")})
  text(")")
  text(" – ")
  text("The second bulleted parameter.")
  })
  
  
  
  parbreak()
  
  [#heading(level: 1, {
assert 'strong(raw("beta"))' in 'text("Multi-Value Bulleted Control")}) <index:multi-value-bulleted-control>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_multi_value_bulleted"))\nraw("(") + emph(raw("alpha")) + raw(", ") + emph(raw("beta")) + raw(")")}))\n[#metadata(none) <index:field_multi_value_bulleted>]\nstrong(text("Parameters") + text(": "))\nlist({\nparbreak()\n\nstrong({text("alpha")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" \u2013 ")\ntext("The first bulleted parameter.")\n}, {\nparbreak()\n\nstrong({text("beta")})\ntext(" (")\nemph({text("int")})\ntext(")")\ntext(" \u2013 ")\ntext("The second bulleted parameter.")\n})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'
FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_name_bold_monospace[single-entry] - AssertionError: FLD-03: expected the parameter name 'only' to emit 'strong(raw("only"))' (contract section 5.2 row 1), not found in region:
  text("Single-Entry Collapsed Param")}) <index:single-entry-collapsed-param>]
  
  block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_entry_param"))
  raw("(") + emph(raw("only")) + raw(")")}))
  [#metadata(none) <index:field_single_entry_param>]
  strong(text("Parameters") + text(": "))
  par({strong({text("only")})
  text(" (")
  emph({text("str")})
  text(")")
  text(" – ")
  text("The lone parameter, collapsed to one paragraph body.")})
  
  
  
  parbreak()
  
  [#heading(level: 1, {
assert 'strong(raw("only"))' in 'text("Single-Entry Collapsed Param")}) <index:single-entry-collapsed-param>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_entry_param"))\nraw("(") + emph(raw("only")) + raw(")")}))\n[#metadata(none) <index:field_single_entry_param>]\nstrong(text("Parameters") + text(": "))\npar({strong({text("only")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" \u2013 ")\ntext("The lone parameter, collapsed to one paragraph body.")})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'
FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_name_bold_monospace[non-ascii] - AssertionError: FLD-03: expected the parameter name '名前' to emit 'strong(raw("名前"))' (contract section 5.2 row 1), not found in region:
  text("Non-ASCII Parameter Name")}) <index:non-ascii-parameter-name>]
  
  block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_nonascii_param"))
  raw("(") + emph(raw("x")) + raw(")")}))
  [#metadata(none) <index:field_nonascii_param>]
  strong(text("Parameters") + text(": "))
  par({strong({text("名前")})
  text(" (")
  emph({text("str")})
  text(")")
  text(" – ")
  text("説明文です, a non-ASCII parameter name and description.")})
  
  
  
  parbreak()
  
  [#heading(level: 1, {
assert 'strong(raw("\u540d\u524d"))' in 'text("Non-ASCII Parameter Name")}) <index:non-ascii-parameter-name>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_nonascii_param"))\nraw("(") + emph(raw("x")) + raw(")")}))\n[#metadata(none) <index:field_nonascii_param>]\nstrong(text("Parameters") + text(": "))\npar({strong({text("\u540d\u524d")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" \u2013 ")\ntext("\u8aac\u660e\u6587\u3067\u3059, a non-ASCII parameter name and description.")})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'
FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_type_italic_monospace[multi-value-alpha] - AssertionError: FLD-03: expected the type 'str' to emit 'emph(raw("str"))' (contract section 5.2 row 2), not found in region:
  text("Multi-Value Bulleted Control")}) <index:multi-value-bulleted-control>]
  
  block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_multi_value_bulleted"))
  raw("(") + emph(raw("alpha")) + raw(", ") + emph(raw("beta")) + raw(")")}))
  [#metadata(none) <index:field_multi_value_bulleted>]
  strong(text("Parameters") + text(": "))
  list({
  parbreak()
  
  strong({text("alpha")})
  text(" (")
  emph({text("str")})
  text(")")
  text(" – ")
  text("The first bulleted parameter.")
  }, {
  parbreak()
  
  strong({text("beta")})
  text(" (")
  emph({text("int")})
  text(")")
  text(" – ")
  text("The second bulleted parameter.")
  })
  
  
  
  parbreak()
  
  [#heading(level: 1, {
assert 'emph(raw("str"))' in 'text("Multi-Value Bulleted Control")}) <index:multi-value-bulleted-control>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_multi_value_bulleted"))\nraw("(") + emph(raw("alpha")) + raw(", ") + emph(raw("beta")) + raw(")")}))\n[#metadata(none) <index:field_multi_value_bulleted>]\nstrong(text("Parameters") + text(": "))\nlist({\nparbreak()\n\nstrong({text("alpha")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" \u2013 ")\ntext("The first bulleted parameter.")\n}, {\nparbreak()\n\nstrong({text("beta")})\ntext(" (")\nemph({text("int")})\ntext(")")\ntext(" \u2013 ")\ntext("The second bulleted parameter.")\n})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'
FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_type_italic_monospace[multi-value-beta] - AssertionError: FLD-03: expected the type 'int' to emit 'emph(raw("int"))' (contract section 5.2 row 2), not found in region:
  text("Multi-Value Bulleted Control")}) <index:multi-value-bulleted-control>]
  
  block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_multi_value_bulleted"))
  raw("(") + emph(raw("alpha")) + raw(", ") + emph(raw("beta")) + raw(")")}))
  [#metadata(none) <index:field_multi_value_bulleted>]
  strong(text("Parameters") + text(": "))
  list({
  parbreak()
  
  strong({text("alpha")})
  text(" (")
  emph({text("str")})
  text(")")
  text(" – ")
  text("The first bulleted parameter.")
  }, {
  parbreak()
  
  strong({text("beta")})
  text(" (")
  emph({text("int")})
  text(")")
  text(" – ")
  text("The second bulleted parameter.")
  })
  
  
  
  parbreak()
  
  [#heading(level: 1, {
assert 'emph(raw("int"))' in 'text("Multi-Value Bulleted Control")}) <index:multi-value-bulleted-control>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_multi_value_bulleted"))\nraw("(") + emph(raw("alpha")) + raw(", ") + emph(raw("beta")) + raw(")")}))\n[#metadata(none) <index:field_multi_value_bulleted>]\nstrong(text("Parameters") + text(": "))\nlist({\nparbreak()\n\nstrong({text("alpha")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" \u2013 ")\ntext("The first bulleted parameter.")\n}, {\nparbreak()\n\nstrong({text("beta")})\ntext(" (")\nemph({text("int")})\ntext(")")\ntext(" \u2013 ")\ntext("The second bulleted parameter.")\n})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'
FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_type_italic_monospace[single-entry] - AssertionError: FLD-03: expected the type 'str' to emit 'emph(raw("str"))' (contract section 5.2 row 2), not found in region:
  text("Single-Entry Collapsed Param")}) <index:single-entry-collapsed-param>]
  
  block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_entry_param"))
  raw("(") + emph(raw("only")) + raw(")")}))
  [#metadata(none) <index:field_single_entry_param>]
  strong(text("Parameters") + text(": "))
  par({strong({text("only")})
  text(" (")
  emph({text("str")})
  text(")")
  text(" – ")
  text("The lone parameter, collapsed to one paragraph body.")})
  
  
  
  parbreak()
  
  [#heading(level: 1, {
assert 'emph(raw("str"))' in 'text("Single-Entry Collapsed Param")}) <index:single-entry-collapsed-param>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_entry_param"))\nraw("(") + emph(raw("only")) + raw(")")}))\n[#metadata(none) <index:field_single_entry_param>]\nstrong(text("Parameters") + text(": "))\npar({strong({text("only")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" \u2013 ")\ntext("The lone parameter, collapsed to one paragraph body.")})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'
FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_param_type_italic_monospace[non-ascii] - AssertionError: FLD-03: expected the type 'str' to emit 'emph(raw("str"))' (contract section 5.2 row 2), not found in region:
  text("Non-ASCII Parameter Name")}) <index:non-ascii-parameter-name>]
  
  block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_nonascii_param"))
  raw("(") + emph(raw("x")) + raw(")")}))
  [#metadata(none) <index:field_nonascii_param>]
  strong(text("Parameters") + text(": "))
  par({strong({text("名前")})
  text(" (")
  emph({text("str")})
  text(")")
  text(" – ")
  text("説明文です, a non-ASCII parameter name and description.")})
  
  
  
  parbreak()
  
  [#heading(level: 1, {
assert 'emph(raw("str"))' in 'text("Non-ASCII Parameter Name")}) <index:non-ascii-parameter-name>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_nonascii_param"))\nraw("(") + emph(raw("x")) + raw(")")}))\n[#metadata(none) <index:field_nonascii_param>]\nstrong(text("Parameters") + text(": "))\npar({strong({text("\u540d\u524d")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" \u2013 ")\ntext("\u8aac\u660e\u6587\u3067\u3059, a non-ASCII parameter name and description.")})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'
FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_typeless_param_exactly_one_bold_mono_zero_italic_mono - AssertionError: FLD-03 empty edge: expected exactly ONE bold-monospace call 'strong(raw("untyped"))', found 0 in region:
  text("Name Without Type")}) <index:name-without-type>]
  
  block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_name_without_type"))
  raw("(") + emph(raw("untyped")) + raw(")")}))
  [#metadata(none) <index:field_name_without_type>]
  strong(text("Parameters") + text(": "))
  par({strong({text("untyped")})
  text(" – ")
  text("A parameter with no matching type field.")})
  
  
  
  parbreak()
  
  [#heading(level: 1, {
assert 0 == 1
FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_nonascii_param_name_roundtrips_codepoints - AssertionError: FLD-03 encoding: expected the non-ASCII name to round-trip into 'strong(raw("名前"))', not found in region:
  text("Non-ASCII Parameter Name")}) <index:non-ascii-parameter-name>]
  
  block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_nonascii_param"))
  raw("(") + emph(raw("x")) + raw(")")}))
  [#metadata(none) <index:field_nonascii_param>]
  strong(text("Parameters") + text(": "))
  par({strong({text("名前")})
  text(" (")
  emph({text("str")})
  text(")")
  text(" – ")
  text("説明文です, a non-ASCII parameter name and description.")})
  
  
  
  parbreak()
  
  [#heading(level: 1, {
assert 'strong(raw("\u540d\u524d"))' in 'text("Non-ASCII Parameter Name")}) <index:non-ascii-parameter-name>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_nonascii_param"))\nraw("(") + emph(raw("x")) + raw(")")}))\n[#metadata(none) <index:field_nonascii_param>]\nstrong(text("Parameters") + text(": "))\npar({strong({text("\u540d\u524d")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" \u2013 ")\ntext("\u8aac\u660e\u6587\u3067\u3059, a non-ASCII parameter name and description.")})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'
FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld03_resolvable_type_composes_inside_link_unchanged_label - AssertionError: FLD-03 Pitfall 2: expected 'emph(raw("FieldXrefTarget"))' to compose nested inside the emitted link() call immediately after 'link(<index:FieldXrefTarget>, ', not found in region:
  text("Resolvable Type Cross Reference")}) <index:resolvable-type-cross-reference>]
  
  block(sticky: true, par(hanging-indent: 2.5em, {raw("class")
  raw(" ")
  strong(raw("FieldXrefTarget"))}))
  [#metadata(none) <index:FieldXrefTarget>]
  par({text("A class defined in this document so its name resolves as a cross-reference from the function below.")})
  
  parbreak()
  block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_resolvable_xref_type"))
  raw("(") + emph(raw("target")) + raw(")")}))
  [#metadata(none) <index:field_resolvable_xref_type>]
  strong(text("Parameters") + text(": "))
  par({strong({text("target")})
  text(" (")
  link(<index:FieldXrefTarget>, 
  emph({text("FieldXrefTarget")}))
  text(")")
  text(" – ")
  text("A parameter whose type resolves to a local class.")})
  
  
  
  parbreak()
  
  [#heading(level: 1, {
assert None
 +  where None = <function search at 0x7d5ceb17d080>('link\\(<index:FieldXrefTarget>,\\ \\s*emph\\(raw\\("FieldXrefTarget"\\)\\)\\)', 'text("Resolvable Type Cross Reference")}) <index:resolvable-type-cross-reference>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {raw("class")\nraw(" ")\nstrong(raw("FieldXrefTarget"))}))\n[#metadata(none) <index:FieldXrefTarget>]\npar({text("A class defined in this document so its name resolves as a cross-reference from the function below.")})\n\nparbreak()\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_resolvable_xref_type"))\nraw("(") + emph(raw("target")) + raw(")")}))\n[#metadata(none) <index:field_resolvable_xref_type>]\nstrong(text("Parameters") + text(": "))\npar({strong({text("target")})\ntext(" (")\nlink(<index:FieldXrefTarget>, \nemph({text("FieldXrefTarget")}))\ntext(")")\ntext(" \u2013 ")\ntext("A parameter whose type resolves to a local class.")})\n\n\n\nparbreak()\n\n[#heading(level: 1, {')
 +    where <function search at 0x7d5ceb17d080> = re.search
FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_single_value_returns_no_block_paragraph_wrapper - AssertionError: FLD-02/D-07: expected the single-value :returns: body to NOT be wrapped in a block-level par(...) call ('par({text("A short stable value.")})' must be absent):
  text("Single-Value Fields Returns Rtype Raises")}) <index:single-value-fields-returns-rtype-raises>]
  
  block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_value_trio"))
  raw("(") + raw(")")}))
  [#metadata(none) <index:field_single_value_trio>]
  strong(text("Returns") + text(": "))
  par({text("A short stable value.")})
  
  
  strong(text("Return type") + text(": "))
  par({text("str")})
  
  
  strong(text("Raises") + text(": "))
  par({strong({text("ValueError")})
  text(" – ")
  text("If something goes wrong.")})
  
  
  
  parbreak()
  
  [#heading(level: 1, {
assert 'par({text("A short stable value.")})' not in 'text("Single-Value Fields Returns Rtype Raises")}) <index:single-value-fields-returns-rtype-raises>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_value_trio"))\nraw("(") + raw(")")}))\n[#metadata(none) <index:field_single_value_trio>]\nstrong(text("Returns") + text(": "))\npar({text("A short stable value.")})\n\n\nstrong(text("Return type") + text(": "))\npar({text("str")})\n\n\nstrong(text("Raises") + text(": "))\npar({strong({text("ValueError")})\ntext(" – ")\ntext("If something goes wrong.")})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'
  
  'par({text("A short stable value.")})' is contained here:
    text("Single-Value Fields Returns Rtype Raises")}) <index:single-value-fields-returns-rtype-raises>]
    
    block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_value_trio"))
    raw("(") + raw(")")}))
    [#metadata(none) <index:field_single_value_trio>]
    strong(text("Returns") + text(": "))
    par({text("A short stable value.")})
    
    
    strong(text("Return type") + text(": "))
    par({text("str")})
    
    
    strong(text("Raises") + text(": "))
    par({strong({text("ValueError")})
    text(" – ")
    text("If something goes wrong.")})
    
    
    
    parbreak()
    
    [#heading(level: 1, {
FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_single_value_pdf_adjacency_matches_pinned_string - AssertionError: FLD-02: expected the pinned adjacency string 'Returns: A short stable value.' in the extracted PDF text -- label and value must share one line:
  'Field Body Typography Render Gate\ntypsphinx tests\n0.0.0\n1\n1 Contents\nContents\n2 Field Body Typography Render Gate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n3 Multi-Value Bulleted Control . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n4 Single-Entry Collapsed Param . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n5 Single-Value Fields Returns Rtype Raises . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n6 Resolvable Type Cross Reference . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n7 Name Without Type . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n8 Non-ASCII Parameter Name . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n9 Collapsed Inline Control . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4\n10 Single Field List . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4\n2\n2 Field Body Typography Render Gate\nThis fixture exists solely to be built through -b typst (structural assertions) and compiled to PDF \nvia typst.compile() (glyph and text-extraction assertions) by tests/\ntest_field_body_typography_render_gate.py (Phase 38, FLD-01, FLD-02, FLD-03, D-05, D-06, \nD-07, D-13). It is not meant to be read as prose.\n3 Multi-Value Bulleted Control\nfield_multi_value_bulleted(alpha, beta)\nParameters: \n• alpha (str) – The first bulleted parameter.\n• beta (int) – The second bulleted parameter.\n4 Single-Entry Collapsed Param\nfield_single_entry_param(only)\nParameters: \nonly (str) – The lone parameter, collapsed to one paragraph body.\n5 Single-Value Fields Returns Rtype Raises\nfield_single_value_trio()\nReturns: \nA short stable value.\nReturn type: \nstr\nRaises: \nValueError – If something goes wrong.\n6 Resolvable Type Cross Reference\nclass FieldXrefTarget\nA class defined in this document so its name resolves as a cross-reference from the function below.\nfield_resolvable_xref_type(target)\nParameters: \ntarget (FieldXrefTarget) – A parameter whose type resolves to a local class.\n7 Name Without Type\nfield_name_without_type(untyped)\nParameters: \nuntyped – A parameter with no matching type field.\n8 Non-ASCII Parameter Name\nfield_nonascii_param(x)\nParameters: \n3\n名前 (str) – 説明文です, a non-ASCII parameter name and description.\n9 Collapsed Inline Control\nfield_collapsed_inline_confval\nType: int (a number)  Default: 99\n10 Single Field List\nfield_single_field_list()\nReturns: \nThe only field in this function’s field list.\n4'
assert 'Returns: A short stable value.' in 'Field Body Typography Render Gate\ntypsphinx tests\n0.0.0\n1\n1 Contents\nContents\n2 Field Body Typography Render Gate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n3 Multi-Value Bulleted Control . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n4 Single-Entry Collapsed Param . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n5 Single-Value Fields Returns Rtype Raises . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n6 Resolvable Type Cross Reference . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n7 Name Without Type . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n8 Non-ASCII Parameter Name . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3\n9 Collapsed Inline Control . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4\n10 Single Field List . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4\n2\n2 Field Body Typography Render Gate\nThis fixture exists solely to be built through -b typst (structural assertions) and compiled to PDF \nvia typst.compile() (glyph and text-extraction assertions) by tests/\ntest_field_body_typography_render_gate.py (Phase 38, FLD-01, FLD-02, FLD-03, D-05, D-06, \nD-07, D-13). It is not meant to be read as prose.\n3 Multi-Value Bulleted Control\nfield_multi_value_bulleted(alpha, beta)\nParameters: \n\u2022 alpha (str) \u2013 The first bulleted parameter.\n\u2022 beta (int) \u2013 The second bulleted parameter.\n4 Single-Entry Collapsed Param\nfield_single_entry_param(only)\nParameters: \nonly (str) \u2013 The lone parameter, collapsed to one paragraph body.\n5 Single-Value Fields Returns Rtype Raises\nfield_single_value_trio()\nReturns: \nA short stable value.\nReturn type: \nstr\nRaises: \nValueError \u2013 If something goes wrong.\n6 Resolvable Type Cross Reference\nclass FieldXrefTarget\nA class defined in this document so its name resolves as a cross-reference from the function below.\nfield_resolvable_xref_type(target)\nParameters: \ntarget (FieldXrefTarget) \u2013 A parameter whose type resolves to a local class.\n7 Name Without Type\nfield_name_without_type(untyped)\nParameters: \nuntyped \u2013 A parameter with no matching type field.\n8 Non-ASCII Parameter Name\nfield_nonascii_param(x)\nParameters: \n3\n\u540d\u524d (str) \u2013 \u8aac\u660e\u6587\u3067\u3059, a non-ASCII parameter name and description.\n9 Collapsed Inline Control\nfield_collapsed_inline_confval\nType: int (a number)  Default: 99\n10 Single Field List\nfield_single_field_list()\nReturns: \nThe only field in this function\u2019s field list.\n4'
FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld02_single_entry_param_renders_inline_prose_never_bulleted - AssertionError: FLD-02/D-07: expected the single-entry :param:'s field body to NOT be wrapped in a block-level par(...) call ('par({strong({text("only")})' must be absent):
  text("Single-Entry Collapsed Param")}) <index:single-entry-collapsed-param>]
  
  block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_entry_param"))
  raw("(") + emph(raw("only")) + raw(")")}))
  [#metadata(none) <index:field_single_entry_param>]
  strong(text("Parameters") + text(": "))
  par({strong({text("only")})
  text(" (")
  emph({text("str")})
  text(")")
  text(" – ")
  text("The lone parameter, collapsed to one paragraph body.")})
  
  
  
  parbreak()
  
  [#heading(level: 1, {
assert 'par({strong({text("only")})' not in 'text("Single-Entry Collapsed Param")}) <index:single-entry-collapsed-param>]\n\nblock(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_entry_param"))\nraw("(") + emph(raw("only")) + raw(")")}))\n[#metadata(none) <index:field_single_entry_param>]\nstrong(text("Parameters") + text(": "))\npar({strong({text("only")})\ntext(" (")\nemph({text("str")})\ntext(")")\ntext(" – ")\ntext("The lone parameter, collapsed to one paragraph body.")})\n\n\n\nparbreak()\n\n[#heading(level: 1, {'
  
  'par({strong({text("only")})' is contained here:
    text("Single-Entry Collapsed Param")}) <index:single-entry-collapsed-param>]
    
    block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_entry_param"))
    raw("(") + emph(raw("only")) + raw(")")}))
    [#metadata(none) <index:field_single_entry_param>]
    strong(text("Parameters") + text(": "))
    par({strong({text("only")})
    text(" (")
    emph({text("str")})
    text(")")
    text(" – ")
    text("The lone parameter, collapsed to one paragraph body.")})
    
    
    
    parbreak()
    
    [#heading(level: 1, {
FAILED tests/test_field_body_typography_render_gate.py::TestFieldBodyTypographyGate::test_fld01_field_list_wrapper_nested_inside_desc_content_wrapper - AssertionError: FLD-01: expected the enclosing desc_content wrapper's opening token 'pad(left: 2.5em, {' in region:
  text("Single-Value Fields Returns Rtype Raises")}) <index:single-value-fields-returns-rtype-raises>]
  
  block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("field_single_value_trio"))
  raw("(") + raw(")")}))
  [#metadata(none) <index:field_single_value_trio>]
  strong(text("Returns") + text(": "))
  par({text("A short stable value.")})
  
  
  strong(text("Return type") + text(": "))
  par({text("str")})
  
  
  strong(text("Raises") + text(": "))
  par({strong({text("ValueError")})
  text(" – ")
  text("If something goes wrong.")})
  
  
  
  parbreak()
  
  [#heading(level: 1, {
assert -1 != -1
========================= 15 failed, 5 passed in 1.02s =========================

```

## 2. Per-node-id RED / CONTROL-GREEN table

| Node ID | RED / CONTROL-GREEN | Property |
|---|---|---|
| `test_fld03_param_name_bold_monospace[multi-value-alpha]` | RED | bold PROPORTIONAL `strong({text("alpha")})` is emitted where bold MONOSPACE `strong(raw("alpha"))` is required (contract section 5.2 row 1). |
| `test_fld03_param_name_bold_monospace[multi-value-beta]` | RED | bold PROPORTIONAL `strong({text("beta")})` is emitted where bold MONOSPACE `strong(raw("beta"))` is required. |
| `test_fld03_param_name_bold_monospace[single-entry]` | RED | bold PROPORTIONAL `strong({text("only")})` is emitted where bold MONOSPACE `strong(raw("only"))` is required. |
| `test_fld03_param_name_bold_monospace[non-ascii]` | RED | bold PROPORTIONAL `strong({text("名前")})` is emitted where bold MONOSPACE `strong(raw("名前"))` is required. |
| `test_fld03_param_type_italic_monospace[multi-value-alpha]` | RED | italic PROPORTIONAL `emph({text("str")})` is emitted where italic MONOSPACE `emph(raw("str"))` is required (contract section 5.2 row 2). |
| `test_fld03_param_type_italic_monospace[multi-value-beta]` | RED | italic PROPORTIONAL `emph({text("int")})` is emitted where italic MONOSPACE `emph(raw("int"))` is required. |
| `test_fld03_param_type_italic_monospace[single-entry]` | RED | italic PROPORTIONAL `emph({text("str")})` is emitted where italic MONOSPACE `emph(raw("str"))` is required. |
| `test_fld03_param_type_italic_monospace[non-ascii]` | RED | italic PROPORTIONAL `emph({text("str")})` is emitted where italic MONOSPACE `emph(raw("str"))` is required. |
| `test_fld03_typeless_param_exactly_one_bold_mono_zero_italic_mono` | RED | zero bold-monospace calls are found (the proportional form is present instead), so the required count of exactly one fails (found 0). |
| `test_fld03_nonascii_param_name_roundtrips_codepoints` | RED | the non-ASCII name round-trips its code points into the proportional form, not into the required bold-monospace form. |
| `test_fld03_resolvable_type_composes_inside_link_unchanged_label` | RED | the resolvable type composes inside link() as italic PROPORTIONAL `emph({text("FieldXrefTarget")})`, not italic MONOSPACE; the link's label argument (`link(<index:FieldXrefTarget>, `) is already correct and unchanged. |
| `test_fld02_single_value_returns_no_block_paragraph_wrapper` | RED | the single-value :returns: body IS wrapped in a block-level `par({text("A short stable value.")})` -- this is D-07's defect itself, verbatim. |
| `test_fld02_single_value_pdf_adjacency_matches_pinned_string` | RED | the label and value render on SEPARATE lines in the compiled PDF's extracted text ("Returns: \nA short stable value."), not adjacent on one line. |
| `test_fld02_single_entry_param_renders_inline_prose_never_bulleted` | RED | the single-entry :param: field body IS still wrapped in a block-level `par({strong({text("only")})...})` -- the same D-07 defect reaching the TypedField can_collapse path. |
| `test_fld01_field_list_wrapper_nested_inside_desc_content_wrapper` | RED | the desc_content `pad(left: 2.5em, {` wrapper is entirely ABSENT pre-phase (visit_desc_content is still a no-op `pass`), so even the first occurrence of the opening token cannot be found. |
| `test_fld03_field_label_unchanged_and_distinct_from_name_and_type` | CONTROL-GREEN | the field label already emits the unchanged proportional-bold form `strong(text("Parameters") + text(": "))`, structurally distinct from both monospace forms; D-06 leaves this handler untouched by design. |
| `test_fld03_no_zero_width_space_anywhere_in_field_bodies` | CONTROL-GREEN | no zero-width-space injection exists anywhere in field bodies pre-phase (no code path reaches Phase 37's signature escape helper from a field body); this OUTPUT property must stay true post-phase too. |
| `test_fld02_consecutive_single_value_fields_stay_on_separate_lines` | CONTROL-GREEN | pre-phase each field's label AND its own value already sit on separate lines (both are separately block-wrapped), so the "labels never run together" property already holds. Reclassified as a non-regression control per this evidence file's own instruction: the property must SURVIVE the phase, when the label+value pair collapses onto one line. |
| `test_fld02_bulleted_multi_value_non_regression_control` | CONTROL-GREEN (required) | the multi-entry :param: group already emits exactly one `list({...}, {...})` call with alpha before beta -- the plan requires this specific test to be GREEN pre-phase, never a defect case. |
| `test_determinism_two_builds_produce_byte_identical_typ` | CONTROL-GREEN | the build is already deterministic; two builds of the untouched fixture produce byte-identical `.typ`. |

15 RED, 5 CONTROL-GREEN (of which one -- the bulleted-half non-regression control -- is REQUIRED to
be green by the plan's own acceptance criteria; the other four are genuine pre-existing GREEN
properties reclassified as non-regression controls per this file's own instruction, since they must
also survive the phase unchanged or in their strengthened post-phase form).

## 3. No RED is a compile failure

Every one of the 15 RED assertions above is an `AssertionError` from a Python string/regex
comparison inside the test body -- never a `TypstError`, never a `TypstCompilationError`, never the
string `"Typst compilation failed"` or `"expected semicolon or line break"` anywhere in the captured
output (grepped and confirmed absent). The fixture itself compiles cleanly both directions:

```
$ uv run python -m sphinx -b typstpdf tests/fixtures/field_body_typography_render_gate /tmp/fld38pdf
...
Compiling 1 master document(s) to PDF...
Generated PDF: /tmp/fld38pdf/index.pdf
build succeeded.
$ echo $?
0
```

`index.pdf` is produced (85,695 bytes, `%PDF` magic bytes confirmed by the gate module's own
`_field_body_typography_build` fixture assertion). Milestone invariant #4 is satisfied: RED is
structural (a monospace primitive absent, an adjacency absent, a wrapper token absent), never a
build/compile fatal.

## 4. Pre-phase emitted bytes for each FLD-03 sub-part

- **Parameter NAME's call** (multi-value construct, `alpha`): `strong({text("alpha")})`
- **Parameter TYPE's call** (multi-value construct, `str`): `emph({text("str")})`
- **Field LABEL's call** (unchanged both pre- and post-phase, D-06): `strong(text("Parameters") + text(": "))`

For completeness, the same three call shapes on the non-ASCII construct:

- Name: `strong({text("名前")})`
- Type: `emph({text("str")})`
- Label: `strong(text("Parameters") + text(": "))`

And the resolvable cross-reference construct's type call, nested inside its (already-correct,
untouched) link wrapper:

```
link(<index:FieldXrefTarget>,
emph({text("FieldXrefTarget")}))
```


The label call is byte-identical across every construct (D-06: unchanged, proportional, distinct from
both monospace forms) -- this is `test_fld03_field_label_unchanged_and_distinct_from_name_and_type`'s
CONTROL-GREEN baseline. The name and type calls above are each RED against their respective hand-
derived `strong(raw(...))` / `emph(raw(...))` targets.

## 5. Pre-phase extracted-PDF text for the single-value field block

```
Returns:
A short stable value.
Return type:
str
Raises:
ValueError – If something goes wrong.
```

(pypdf-extracted text of the "Single-Value Fields Returns Rtype Raises" construct, from the real
pre-phase compiled PDF -- the label and its value occupy separate lines, both for `Returns:` and for
`Return type:`, confirming contract section 4.1's measured starting state.)

This is the D-07 defect evidenced in the rendered output, not only in the source: `Returns:` and its
value never share a line pre-phase, which is exactly what
`test_fld02_single_value_pdf_adjacency_matches_pinned_string` records as RED against the hand-derived
pinned string `"Returns: A short stable value."`.

## 6. D-13 disposition record

**Decision, taken at plan time and re-confirmed here: the stray `parbreak()` at the head of each
bulleted field-list item is LEFT IN PLACE.**

Re-running the grep `38-RESEARCH.md` Open Question 2 asked for (recommendation: "grep existing
goldens for the exact `list({\nparbreak()` shape first"), against the current tree, 2026-08-01:

Command 1 (multiline literal match, source files only):

```
$ grep -rlPzo 'list\(\{\nparbreak\(\)' tests/
tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
tests/__pycache__/test_inline_math_after_text_render_gate.cpython-313-pytest-9.1.1.pyc
```

Command 2 (line-context cross-check, human-readable):

```
$ grep -rn 'list({' -A 1 tests/ | grep -B1 "parbreak()"
tests/test_deflist_definition_multiblock_render_gate.py-160-            "The multi-block definition should still emit its code fence and "
tests/test_inline_math_after_text_render_gate.py:291:        assert "list({\nparbreak()\n\nmi(`a+b`)" in typ_text, (
--
tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ:66:list({
tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ-67-parbreak()
```

Both commands confirm `38-EMISSION-CONTRACT.md` section 4.5's own citation: `tests/
test_inline_math_after_text_render_gate.py:291` pins the exact shape `"list({\nparbreak()\n\n
mi(\`a+b\`)"` --

```python
# tests/test_inline_math_after_text_render_gate.py:291
assert "list({\nparbreak()\n\nmi(`a+b`)" in typ_text, (
```

-- and `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ:66-67` independently carries the
same `list({` / `parbreak()` shape in a byte-identity golden file for a different phase's fixture.

**Decision: LEFT IN PLACE.** Two reasons, both from `38-EMISSION-CONTRACT.md` section 4.5:

1. The break is emitted by `visit_paragraph`'s `self.in_list_item` fast-path, which fires for EVERY
   list item in the document -- bullet, enumerated and definition lists alike -- not by anything
   field-list-specific. Removing it changes rendering repo-wide, far outside FLD-02's actual
   requirement.
2. An existing test (`tests/test_inline_math_after_text_render_gate.py:291`) already pins this exact
   shape as a passing assertion. Touching it would require migrating a control this plan has no
   mandate to touch, for a cosmetic gain.

**Accepted measured cost** (from `38-EMISSION-CONTRACT.md` section 4.5, itself sourced from
`38-CONTEXT.md` D-13): approximately **7.15pt** before the first bullet in a bulleted field-list
group (14.245pt with the stray break present, 7.15pt without it), and **nothing** between subsequent
items in the same group. This cost is accepted, not eliminated, and is recorded here explicitly per
D-13's requirement that the decision be stated rather than left silent.

## 7. Injection breadcrumb

Typst string-literal injection via unescaped field-body text is canon injection territory, owned by
the project-wide escaping boundary (`escape_typst_string`) and `/gsd-secure-phase`'s retroactive
threat-mitigation sweep -- it is therefore not minted as a bespoke prohibition in this plan's
`must_haves`; T-38-04/T-38-05/T-38-06 in the plan's own threat register cover the phase-specific
surface (the two new leaf-emission sites and the wrong-escape-helper trap) instead.

---

*Phase: 38 — Structural Indentation + Info Fields*
*Plan: 02 — FLD-02/FLD-03 gate (fixture + per-sub-part module + this evidence file)*
*Evidence recorded: 2026-08-01*
