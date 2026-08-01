"""
Phase 37 GATE-01 structural gate for SIG-01..SIG-05 (Signature Typography).

This module records, PER SUB-PART (D-03 -- never as one blanket check over
``desc_parameter``), the structural RED evidence that the pre-phase
translator does not yet emit the Phase 37 signature typography design.
Every expected string below is hand-derived from
``.planning/phases/37-signature-typography-the-desc-family/37-EMISSION-CONTRACT.md``
sections 3-6 -- never from running the new translator code (which does not
exist yet: ``visit_desc_name``, ``visit_desc_annotation``,
``visit_desc_sig_name`` and ``visit_desc_parameter`` are all still ``pass``
on this branch). ROADMAP SC#5 / milestone invariant #4.

Escaping mechanics are computed via ``typsphinx.translator.escape_typst_string``
-- the SAME shared, Phase-37-untouched helper the contract's §4 step 2 names
as the one every new call site reuses (T-37-01: "no new escaping code is
written"). This is not "copying the new code's output" -- there is no new
output yet for any of these node types; it is reusing an existing, already
proven primitive to compute the contract's own documented algorithm. The
zero-width-space injection of contract §4.1/§4 step 3 (the LITERAL 8-character
Typst escape sequence ``\\u{200B}``, not an actual U+200B byte) is applied on
top of that, by hand, per the contract's own replace() description.

Region-slicing methodology: the plan text asks to "split on the wrapper
opening literal specified in contract §3". That literal
(``block(sticky: true, par(hanging-indent: 2.5em, {``, post-Wave-3
amendment, plan 37-09) does not exist anywhere in the PRE-PHASE output
(the current wrapper is
``strong({``), so splitting on it pre-phase collapses the whole document into
one un-isolated blob -- exactly the cross-signature contamination the plan
warns against. Instead this module slices per-signature regions using the
document's own section headings and desc_signature id-anchor labels
(``[#metadata(none) <index:...>]``) -- both emitted by handlers Phase 37 does
not touch (D-14's anchor-preservation guarantee), so the SAME slicing code
works unmodified whether the wrapper is the pre-phase ``strong({`` or the
post-fix ``block(...)`` form. This achieves the same "an assertion about one
sub-part cannot be satisfied by bytes belonging to a different signature"
goal the plan requires, robustly across both states.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

from typsphinx.translator import escape_typst_string

# The literal 8-character Typst escape sequence for U+200B (contract §4.1) --
# NOT an actual zero-width-space byte.
_ZWSP_ESCAPE = "\\u{200B}"


def _zwsp_after_dots(escaped_text: str) -> str:
    """
    Apply contract §4 step 3's zero-width-break injection to an
    ALREADY-escaped signature text run: replace every ``.`` with
    ``.`` + the literal escape sequence. Order is load-bearing (escape
    first, then inject) per the contract -- ``escape_typst_string`` doubles
    backslashes, so injecting first would double the backslash this
    function introduces.
    """
    return escaped_text.replace(".", "." + _ZWSP_ESCAPE)


def _expected_raw(text: str) -> str:
    """Hand-derive the Phase 37 ``raw("...")`` form (contract §4) for a
    signature text run that gets monospace "for free" (no bold, no
    italic)."""
    return f'raw("{_zwsp_after_dots(escape_typst_string(text))}")'


def _expected_bold(text: str) -> str:
    """Hand-derive the Phase 37 ``strong(raw("..."))`` form (contract §5.1
    leaf branch / §5.2 rule 1) for a text-only-leaf desc_name /
    desc_annotation / parent-desc_sig_name."""
    return f'strong(raw("{_zwsp_after_dots(escape_typst_string(text))}"))'


def _expected_italic(text: str) -> str:
    """Hand-derive the Phase 37 ``emph(raw("..."))`` form (contract §5.2
    rule 2) for a parameter's own name."""
    return f'emph(raw("{_zwsp_after_dots(escape_typst_string(text))}"))'


def _slice(typ_text: str, start_marker: str, end_marker: str | None) -> str:
    """Return the substring of ``typ_text`` from ``start_marker``
    (inclusive) up to ``end_marker`` (exclusive), or to the end of the
    document if ``end_marker`` is ``None``."""
    start_idx = typ_text.index(start_marker)
    if end_marker is None:
        return typ_text[start_idx:]
    end_idx = typ_text.index(end_marker, start_idx + len(start_marker))
    return typ_text[start_idx:end_idx]


def _heading_marker(text: str) -> str:
    return f'text("{text}")'


def _anchor_marker(label: str) -> str:
    return f"<index:{label}>"


def _extract_wrapped_call(typ_text: str, content: str) -> str:
    """
    Locate the single quoted string literal containing ``content`` verbatim
    and return the whole call expression that wraps it -- without assuming
    which call wraps it. Pre-phase this could be ``text("...")``; post-fix
    it could be ``raw("...")`` or ``strong(raw("..."))`` or
    ``emph(raw("..."))``. Used for SIG-03's "compare the two extracted call
    prefixes for equality" instruction, where the wrapper shape itself
    (not just the content) is exactly what is under test.
    """
    quoted = f'"{content}"'
    idx = typ_text.index(quoted)
    start = idx
    while start > 0 and (typ_text[start - 1].isalnum() or typ_text[start - 1] in "_("):
        start -= 1
    end = idx + len(quoted)
    while end < len(typ_text) and typ_text[end] == ")":
        end += 1
    return typ_text[start:end]


# ---------------------------------------------------------------------------
# Fixture / build plumbing
# ---------------------------------------------------------------------------


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typst`` as a subprocess and return the completed
    process.

    Invoked as ``sys.executable -m sphinx`` (NEVER ``uv run sphinx-build``)
    so the exact interpreter/venv running this test is reused, sidestepping
    the documented NixOS-sandbox PATH-shadowing hazard
    (tests/test_pdf_render_gate.py:141-178).
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typst",
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope="module")
def signature_typography_gate_dir() -> Path:
    """Return the path to the signature_typography_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "signature_typography_gate"


@pytest.fixture(scope="module")
def typ_text(
    signature_typography_gate_dir: Path, tmp_path_factory: pytest.TempPathFactory
) -> str:
    """Build the fixture once through ``-b typst`` and return the emitted
    ``index.typ`` text, shared read-only across every test in this module."""
    build_dir = tmp_path_factory.mktemp("sigtypo_build")
    result = _run_sphinx_build_typst(signature_typography_gate_dir, build_dir)
    assert (
        result.returncode == 0
    ), f"sphinx-build -b typst failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    typ_path = build_dir / "index.typ"
    assert typ_path.exists(), "index.typ was not emitted"
    return typ_path.read_text(encoding="utf-8")


# Section headings, in source order, used to slice per-signature regions.
_H_LATEXBUILDER = "LaTeXBuilder Class With Nested Method"
_H_FOO = "Foo Class And Resolved Cross-Reference Function"
_H_STAR = "Star Args And Kwargs"
_H_CONNECT = "Optional Group Followed By A Parameter (D-11 Adjacency)"
_H_PRINTF = "Nested Optional Groups (SIG-05 Ordering)"
_H_CPP = "C++ Non-Leaf Name"
_H_EMPTY = "Empty Parameter List"
_H_OPTION = "Option With Empty Addname"
_H_RST = "RST Directive Option Text-Leaf Sameness Control"
_H_NONASCII = "Non-ASCII Signature"


def _section(typ_text: str, heading: str, next_heading: str | None) -> str:
    end_marker = _heading_marker(next_heading) if next_heading else None
    return _slice(typ_text, _heading_marker(heading), end_marker)


class TestSignatureTypographyGate:
    """
    Per-sub-part SIG-01..SIG-05 structural RED evidence (Phase 37, GATE-01).

    Every assertion message names its requirement id, so a RED failure is
    self-describing. Requirements: SIG-01, SIG-02, SIG-03, SIG-04, SIG-05.
    """

    # -- SIG-01: desc_name / non-leaf desc_name via desc_sig_name rule 1 --

    def test_sig01_leaf_desc_name_bold_monospace(self, typ_text: str) -> None:
        """LaTeXBuilder's desc_name is a text-only leaf (contract §5.1 leaf
        branch): expect strong(raw("LaTeXBuilder")), and the pre-phase
        text() primitive call must be gone."""
        region = _section(typ_text, _H_LATEXBUILDER, _H_FOO)
        expected = _expected_bold("LaTeXBuilder")
        assert expected in region, (
            f"SIG-01: expected the leaf desc_name 'LaTeXBuilder' to emit "
            f"{expected!r} (contract §5.1 leaf branch), not found in region:\n{region}"
        )
        assert 'text("LaTeXBuilder")' not in region, (
            "SIG-01: the pre-phase text() primitive call for 'LaTeXBuilder' "
            f"must not remain in the emitted region:\n{region}"
        )

    def test_sig01_nonleaf_desc_name_bold_via_nested_desc_sig_name(
        self, typ_text: str
    ) -> None:
        """cpp_probe's desc_name is NON-leaf (wraps a desc_sig_name, contract
        §5.1 'otherwise' branch): the nested desc_sig_name picks up rule
        5.2-(1) ('parent is desc_name') and emits the bold form itself."""
        region = _section(typ_text, _H_CPP, _H_EMPTY)
        expected = _expected_bold("cpp_probe")
        assert expected in region, (
            f"SIG-01: expected the non-leaf desc_name's nested desc_sig_name "
            f"'cpp_probe' to emit {expected!r} (contract §5.2 rule 1), not "
            f"found in region:\n{region}"
        )
        assert 'text("cpp_probe")' not in region, (
            "SIG-01: the pre-phase text() primitive call for 'cpp_probe' "
            f"must not remain in the emitted region:\n{region}"
        )

    # -- SIG-02: desc_addname plain monospace, adjacency, empty, ZWSP --

    def test_sig02_addname_plain_monospace_with_zwsp_and_no_enclosing_bold(
        self, typ_text: str
    ) -> None:
        """The dotted desc_addname 'sphinx.builders.latex.' gets monospace
        "for free" (contract §4.3) -- regular raw(...), never bold -- with
        the §4.1 zero-width-break escape injected after every period."""
        region = _section(typ_text, _H_LATEXBUILDER, _H_FOO)
        expected = _expected_raw("sphinx.builders.latex.")
        idx = region.find(expected)
        assert idx != -1, (
            f"SIG-02: expected the dotted qualifier to emit {expected!r} "
            f"(contract §4 step 3's ZWSP escape after every '.'), not found "
            f"in region:\n{region}"
        )
        prefix = region[:idx]
        assert "strong(" not in prefix, (
            "SIG-02: found an enclosing bold call between the wrapper's "
            f"content-block opening and the qualifier's own call: {prefix!r}"
        )

    def test_sig02_addname_and_name_are_two_separate_expressions(
        self, typ_text: str
    ) -> None:
        """desc_addname and desc_name never merge into a single monospace
        call -- they are two separate expressions, addname first (doctree
        order)."""
        region = _section(typ_text, _H_LATEXBUILDER, _H_FOO)
        addname_call = _expected_raw("sphinx.builders.latex.")
        name_call = _expected_bold("LaTeXBuilder")
        addname_idx = region.find(addname_call)
        name_idx = region.find(name_call)
        assert addname_idx != -1 and name_idx != -1, (
            "SIG-02 adjacency: expected both the addname and name calls to "
            f"be present in region:\n{region}"
        )
        assert addname_idx < name_idx, (
            "SIG-02 ordering: desc_addname must be emitted BEFORE desc_name "
            f"(doctree child order); addname at {addname_idx}, name at {name_idx}"
        )
        merged = 'raw("sphinx.builders.latex.LaTeXBuilder")'
        assert merged not in region, (
            "SIG-02 adjacency: the qualifier must never absorb the name into "
            f"a single call ({merged!r} must not appear):\n{region}"
        )

    def test_sig02_empty_addname_emits_zero_bytes(self, typ_text: str) -> None:
        """The --sep option's desc_addname has zero children (measured):
        it must contribute zero bytes and no separator, exactly as it does
        pre-phase."""
        region = _section(typ_text, _H_OPTION, _H_RST)
        expected = _expected_bold("--sep")
        assert expected in region, (
            f"SIG-02: expected the desc_name '--sep' to emit {expected!r}, "
            f"not found in region:\n{region}"
        )
        assert 'raw("")' not in region, (
            f"SIG-02 empty: an empty desc_addname must not emit an empty "
            f'raw("") call:\n{region}'
        )

    # -- SIG-03: desc_annotation / desc_name identical wrapper shape --

    def test_sig03_annotation_and_name_wrapper_shapes_are_byte_identical(
        self, typ_text: str
    ) -> None:
        """The rst-domain directive-option's desc_name (':caption:') and
        desc_annotation (' text') are BOTH text-only leaves in the SAME
        signature (contract §5.1's 'rst-domain case'). Their wrapper shapes
        must be byte-identical -- proving 'the same as desc_name', not
        merely 'also bold'."""
        rst_region = _section(typ_text, _H_RST, _H_NONASCII)
        probe_anchor = _anchor_marker("directive-probe")
        caption_anchor = _anchor_marker("directive-option-probe-caption")
        option_region = _slice(rst_region, probe_anchor, caption_anchor)

        name_call = _extract_wrapped_call(option_region, ":caption:")
        anno_call = _extract_wrapped_call(option_region, " text")

        expected_name = _expected_bold(":caption:")
        expected_anno = _expected_bold(" text")
        assert name_call == expected_name, (
            f"SIG-03: expected the rst-domain desc_name ':caption:' to emit "
            f"{expected_name!r} (contract §5.1 leaf branch), got {name_call!r}"
        )
        assert anno_call == expected_anno, (
            f"SIG-03: expected the rst-domain desc_annotation ' text' to "
            f"emit {expected_anno!r} (contract §5.1 leaf branch, 'identical "
            f"treatment' to desc_name per the section title), got {anno_call!r}"
        )

        name_wrapper = re.sub(r'"[^"]*"', '"..."', name_call)
        anno_wrapper = re.sub(r'"[^"]*"', '"..."', anno_call)
        assert name_wrapper == anno_wrapper == 'strong(raw("..."))', (
            "SIG-03: expected desc_annotation's wrapper shape to be "
            "byte-identical to desc_name's wrapper shape (both "
            f'strong(raw("...")) ) -- got desc_name wrapper={name_wrapper!r}, '
            f"desc_annotation wrapper={anno_wrapper!r}"
        )

    # -- SIG-04: parameter name italic; type/default plain; xref intact --

    def test_sig04_parameter_names_italic_type_and_default_plain(
        self, typ_text: str
    ) -> None:
        """Every parameter's own name is italic monospace (contract §5.2
        rule 2); its inline type annotation and default value are plain
        monospace, never inside an italic call."""
        region = _section(typ_text, _H_LATEXBUILDER, _H_FOO)

        for name in ("app", "env", "extra", "verbosity"):
            expected = _expected_italic(name)
            assert expected in region, (
                f"SIG-04: expected parameter name {name!r} to emit "
                f"{expected!r} (contract §5.2 rule 2), not found in "
                f"region:\n{region}"
            )

        # verbosity's type annotation "int" is the SECOND desc_sig_name
        # child of its desc_parameter -- _param_name_seen is already True,
        # so rule 2 does not fire; it falls to rule 3 (plain dispatch).
        assert _expected_raw("int") in region, (
            f"SIG-04: expected the type annotation 'int' to emit "
            f"{_expected_raw('int')!r} (plain monospace, contract §5.2 "
            f"rule 3), not found in region:\n{region}"
        )
        assert _expected_italic("int") not in region, (
            "SIG-04: the type annotation 'int' must NOT be inside an "
            f"italic call ({_expected_italic('int')!r} must be absent):\n{region}"
        )

        # extra's default value "None" (inline.default_value) is plain.
        assert _expected_raw("None") in region, (
            f"SIG-04: expected the default value 'None' to emit "
            f"{_expected_raw('None')!r} (plain monospace), not found in "
            f"region:\n{region}"
        )
        assert _expected_italic("None") not in region, (
            "SIG-04: the default value 'None' must NOT be inside an "
            f"italic call ({_expected_italic('None')!r} must be absent):\n{region}"
        )

        # The bare keyword-only separator parameter (desc_parameter whose
        # only child is desc_sig_operator[keyword-only-separator] wrapping
        # abbreviation '*', no desc_sig_name child at all) emits no italic
        # call at all. This is a pure absence invariant that is ALREADY
        # true pre-phase (nothing is italicized anywhere yet) -- it is
        # folded into this test (which fails above on the 'app' italic
        # check) rather than left as a standalone assertion, so it is not
        # reported as a false-positive GREEN of its own.
        assert _expected_italic("*") not in region, (
            "SIG-04: the bare keyword-only separator parameter has no "
            f"desc_sig_name child, so {_expected_italic('*')!r} must never "
            f"appear:\n{region}"
        )

    def test_sig04_resolved_xref_type_annotation_keeps_hyperlink(
        self, typ_text: str
    ) -> None:
        """A resolved cross-reference inside a type annotation
        ('a: Foo | None = None') must still emit a link(...) call wrapping
        the monospace primitive -- a substring check for 'Foo' alone would
        pass even if the hyperlink were silently dropped (Pitfall 3)."""
        region = _section(typ_text, _H_FOO, _H_STAR)
        expected = f'link(<index:Foo>, {_expected_raw("Foo")})'
        assert expected in region, (
            f"SIG-04: expected the resolved-xref type annotation to keep "
            f"its hyperlink, i.e. emit {expected!r}, not found in "
            f"region:\n{region}"
        )
        for name in ("a", "b", "c"):
            expected_name = _expected_italic(name)
            assert expected_name in region, (
                f"SIG-04: expected parameter name {name!r} to emit "
                f"{expected_name!r}, not found in region:\n{region}"
            )

    def test_sig04_generic_type_and_quoted_forward_ref_are_plain(
        self, typ_text: str
    ) -> None:
        """A generic type annotation ('list[int]') and a quoted forward
        reference ('"Bar"', a desc_sig_literal_string) both render plain
        monospace, never italic."""
        region = _section(typ_text, _H_FOO, _H_STAR)
        assert _expected_raw("list") in region, (
            f"SIG-04: expected the generic type's head 'list' to emit "
            f"{_expected_raw('list')!r}, not found in region:\n{region}"
        )
        assert (
            _expected_italic("list") not in region
        ), f"SIG-04: 'list' must not be italicized:\n{region}"
        assert _expected_raw("'Bar'") in region, (
            f"SIG-04: expected the quoted forward reference \"'Bar'\" to "
            f"emit {_expected_raw(chr(39) + 'Bar' + chr(39))!r}, not found "
            f"in region:\n{region}"
        )
        assert (
            _expected_italic("'Bar'") not in region
        ), f"SIG-04: the quoted forward reference must not be italicized:\n{region}"

    # -- SIG-05: delimiters, empty parameter list, D-11 adjacency, order --

    def test_sig05_delimiters_use_monospace_primitive(self, typ_text: str) -> None:
        """Every delimiter site from contract §6's table is emitted through
        the monospace primitive raw(...)."""
        for literal in ('raw("(")', 'raw(")")', 'raw(", ")', 'raw("[")', 'raw("]")'):
            assert literal in typ_text, (
                f"SIG-05: expected the delimiter {literal!r} (contract §6) "
                f"to appear somewhere in the emitted document"
            )

    def test_sig05_empty_parameter_list_no_comma_separator(self, typ_text: str) -> None:
        """An empty desc_parameterlist emits only its two delimiter calls
        with no separator between them."""
        region = _section(typ_text, _H_EMPTY, _H_OPTION)
        assert 'raw("(") + raw(")")' in region, (
            f"SIG-05: expected the empty parameter list to emit "
            f'\'raw("(") + raw(")")\' with no separator, not found in '
            f"region:\n{region}"
        )
        assert 'raw(", ")' not in region, (
            f"SIG-05: an empty parameter list must not emit a comma "
            f"separator:\n{region}"
        )

    def test_sig05_optional_group_separator_lands_inside_bracket(
        self, typ_text: str
    ) -> None:
        """D-11: a desc_optional group followed by a further parameter
        gets its separator INSIDE the closing bracket (matching Sphinx's
        own HTML), and the bracket is explicitly + joined to the following
        parameter -- never juxtaposed."""
        region = _section(typ_text, _H_CONNECT, _H_PRINTF)
        assert '+ raw(", ") + raw("]")' in region, (
            "SIG-05 D-11: expected the optional-group separator to land "
            'INSIDE the bracket (\'+ raw(", ") + raw("]")\'), not found in '
            f"region:\n{region}"
        )
        match = re.search(
            r'raw\("\]"\)(.*?)emph\(raw\("\*\*kwargs"\)\)', region, re.DOTALL
        )
        assert match, (
            "SIG-05 adjacency: expected the closing bracket call to be "
            f"followed (eventually) by the **kwargs parameter's own italic "
            f"call, not found in region:\n{region}"
        )
        assert "+" in match.group(1), (
            "SIG-05 adjacency: a closing optional-group bracket immediately "
            "followed by the next parameter must be joined by an explicit "
            f"concatenation operator, never juxtaposed -- got {match.group(1)!r} "
            "between them"
        )

    def test_sig05_nested_optional_groups_close_in_reverse_open_order(
        self, typ_text: str
    ) -> None:
        """printf(fmt[, args[, more]]): both desc_optional groups are last
        children, so D-11 does not add a comma to either (the non-regression
        control) -- and the inner 'more' bracket closes before the outer
        'args' bracket (reverse-open-order nesting), stable structure."""
        region = _section(typ_text, _H_PRINTF, _H_CPP)
        expected = (
            'raw("(") + '
            + _expected_italic("fmt")
            + ' + raw(", ") + raw("[") + '
            + _expected_italic("args")
            + ' + raw(", ") + raw("[") + '
            + _expected_italic("more")
            + ' + raw("]") + raw("]") + raw(")")'
        )
        assert expected in region, (
            f"SIG-05 ordering: expected the exact nested-bracket structure "
            f"{expected!r} (fmt/args/more each get their own italic name "
            f"call, and neither desc_optional gains a comma since both are "
            f"last children), not found in region:\n{region}"
        )

    # -- Encoding edges: non-ASCII round-trip --

    def test_encoding_non_ascii_signature_round_trips_code_points(
        self, typ_text: str
    ) -> None:
        """The non-ASCII signature's name ('café') and parameter name
        ('naïve') round-trip their code points unchanged into the emitted
        .typ -- escape_typst_string operates on Python str code points, no
        Unicode normalisation."""
        region = _section(typ_text, _H_NONASCII, None)
        expected_name = _expected_bold("café")
        expected_param = _expected_italic("naïve")
        assert expected_name in region, (
            f"Encoding: expected the non-ASCII desc_name to emit "
            f"{expected_name!r}, not found in region:\n{region}"
        )
        assert expected_param in region, (
            f"Encoding: expected the non-ASCII parameter name to emit "
            f"{expected_param!r}, not found in region:\n{region}"
        )

    # -- Determinism (SIG-02 ordering edge): byte-identical across builds --

    def test_determinism_two_builds_produce_byte_identical_output(
        self,
        signature_typography_gate_dir: Path,
        tmp_path_factory: pytest.TempPathFactory,
    ) -> None:
        """Two independent -b typst builds of the same fixture produce
        byte-identical .typ output. This is an invariance CONTROL -- it
        must PASS pre-phase (translator is deterministic today) as well as
        post-fix; it is not one of the intentional RED cases."""
        build_dir_a = tmp_path_factory.mktemp("sigtypo_determinism_a")
        build_dir_b = tmp_path_factory.mktemp("sigtypo_determinism_b")
        result_a = _run_sphinx_build_typst(signature_typography_gate_dir, build_dir_a)
        result_b = _run_sphinx_build_typst(signature_typography_gate_dir, build_dir_b)
        assert result_a.returncode == 0, f"build A failed: {result_a.stderr}"
        assert result_b.returncode == 0, f"build B failed: {result_b.stderr}"
        text_a = (build_dir_a / "index.typ").read_text(encoding="utf-8")
        text_b = (build_dir_b / "index.typ").read_text(encoding="utf-8")
        assert text_a == text_b, (
            "SIG-02 ordering (determinism control): two builds of the same "
            "fixture must produce byte-identical .typ output"
        )
