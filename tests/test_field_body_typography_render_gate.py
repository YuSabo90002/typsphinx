"""
Phase 38 GATE-01 structural gate for FLD-01 (field-body share), FLD-02 and
FLD-03 (Field Body Typography).

This module records, PER SUB-PART for FLD-03 (D-06 -- never as one blanket
check over a field body), the structural RED evidence that the pre-phase
translator does not yet emit the Phase 38 field-body typography design.
Every expected string below is hand-derived from
``.planning/phases/38-structural-indentation-info-fields/38-EMISSION-CONTRACT.md``
sections 4 and 5 -- never from running the new translator code (which does
not exist yet: ``visit_desc_content``, ``visit_field_list`` and
``visit/depart_literal_strong``/``visit/depart_literal_emphasis`` are all
still ``pass`` or dummy-node delegations on this branch). ROADMAP SC#5 /
milestone invariant #4.

Escaping mechanics are computed via ``typsphinx.translator.escape_typst_string``
-- the SAME shared, untouched-by-this-plan helper the contract's section 5.2
names as the one every new call site reuses. Deliberately built on
``escape_typst_string`` ALONE, with NO dot-splitting and NO zero-width-space
injection step: contract section 5.3 identifies reusing Phase 37's
``_emit_signature_leaf_wrapper`` (which injects the SIG-07 zero-width-space
break after every ``.``) as the trap this module exists to catch, since no
FLD requirement or CONTEXT decision authorizes that injection in a field
body.

Region-slicing methodology mirrors ``tests/test_signature_typography_gate.py``:
this module slices per-construct regions using the fixture's own section
headings, which are stable and repo-wide unaffected by this phase, so one
construct's assertion cannot be satisfied by a different construct's bytes.

``typ_text`` and ``pdf_text`` share ONE real ``-b typstpdf`` build
(session-scoped), because the compiled-PDF adjacency assertions and the
structural ``.typ`` assertions are both needed from the exact same output.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

from typsphinx.translator import SHARED_INDENT_STEP, escape_typst_string

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


# ---------------------------------------------------------------------------
# Hand-derivation helpers (contract section 5.2) -- built on
# escape_typst_string ALONE.
# ---------------------------------------------------------------------------


def _expected_bold_mono(text: str) -> str:
    """Hand-derive the Phase 38 target ``strong(raw("..."))`` form (contract
    section 5.2 row 1) for a field-body parameter NAME (``literal_strong``).
    Built on ``escape_typst_string`` alone -- no zero-width-space injection,
    no dot-splitting step (contract section 5.3's trap: that step belongs
    only to Phase 37's signature escape helper, never authorized here)."""
    return f'strong(raw("{escape_typst_string(text)}"))'


def _expected_italic_mono(text: str) -> str:
    """Hand-derive the Phase 38 target ``emph(raw("..."))`` form (contract
    section 5.2 row 2) for a field-body parameter TYPE (``literal_emphasis``).
    Built on ``escape_typst_string`` alone, same no-injection constraint as
    :func:`_expected_bold_mono`."""
    return f'emph(raw("{escape_typst_string(text)}"))'


def _slice(typ_text: str, start_marker: str, end_marker: str | None) -> str:
    """Return the substring of ``typ_text`` from ``start_marker``
    (inclusive) up to ``end_marker`` (exclusive), or to the end of the
    document if ``end_marker`` is ``None``. Region-isolation helper so one
    construct's assertion cannot be satisfied by another construct's
    bytes."""
    start_idx = typ_text.index(start_marker)
    if end_marker is None:
        return typ_text[start_idx:]
    end_idx = typ_text.index(end_marker, start_idx + len(start_marker))
    return typ_text[start_idx:end_idx]


def _heading_marker(text: str) -> str:
    return f'text("{text}")'


def _section(typ_text: str, heading: str, next_heading: str | None) -> str:
    end_marker = _heading_marker(next_heading) if next_heading else None
    return _slice(typ_text, _heading_marker(heading), end_marker)


# ---------------------------------------------------------------------------
# Fixture / build plumbing
# ---------------------------------------------------------------------------


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typstpdf`` as a subprocess and return the completed
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
            "typstpdf",
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """Run ``sphinx-build -b typst`` as a subprocess (structural-only build,
    used by the determinism check). See :func:`_run_sphinx_build_typstpdf`
    for the ``sys.executable`` rationale."""
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


@pytest.fixture(scope="session")
def field_body_typography_render_gate_dir() -> Path:
    """Return the path to the field_body_typography_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "field_body_typography_render_gate"


@pytest.fixture(scope="session")
def _field_body_typography_build(
    field_body_typography_render_gate_dir: Path,
    tmp_path_factory: pytest.TempPathFactory,
) -> Path:
    """Build the fixture ONCE through ``-b typstpdf`` for the whole module:
    both the structural ``.typ`` assertions and the compiled-PDF adjacency
    assertions share this one real build."""
    build_dir = tmp_path_factory.mktemp("fldtypo_build")
    result = _run_sphinx_build_typstpdf(
        field_body_typography_render_gate_dir, build_dir
    )
    assert result.returncode == 0, (
        f"sphinx-build -b typstpdf failed:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert (build_dir / "index.typ").exists(), "index.typ was not emitted"
    assert (build_dir / "index.pdf").exists(), "index.pdf was not produced"
    return build_dir


@pytest.fixture(scope="session")
def typ_text(_field_body_typography_build: Path) -> str:
    """The emitted ``index.typ`` text, shared read-only across every
    structural test in this module."""
    return (_field_body_typography_build / "index.typ").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def pdf_text(_field_body_typography_build: Path) -> str:
    """The pypdf-extracted text of the compiled ``index.pdf``, shared
    read-only across every PDF-adjacency test in this module."""
    reader = pypdf.PdfReader(str(_field_body_typography_build / "index.pdf"))
    return "\n".join(page.extract_text() for page in reader.pages)


# Section headings, in source order, used to slice per-construct regions.
_H_MULTI = "Multi-Value Bulleted Control"
_H_SINGLE_ENTRY = "Single-Entry Collapsed Param"
_H_TRIO = "Single-Value Fields Returns Rtype Raises"
_H_XREF = "Resolvable Type Cross Reference"
_H_NOTYPE = "Name Without Type"
_H_NONASCII = "Non-ASCII Parameter Name"
_H_COLLAPSED = "Collapsed Inline Control"
_H_SINGLE_FIELD = "Single Field List"
_H_LI_BULLET = "List Item Bullet Single Value Field"
_H_LI_ENUM = "List Item Enumerated Consecutive Fields"

# The exact ROADMAP-hand-derived pinned adjacency string (contract section
# 4.3 property 1): the label and value of a single-value field share ONE
# line, separated by ": " -- one space after the colon, no line break. This
# fixture's :returns: text is "A short stable value." (the trio construct).
PINNED_FLD02_ADJACENCY_STRING = "Returns: A short stable value."

# 38-09 gap closure (38-VERIFICATION.md gap 1 / 38-REVIEW.md CR-01): the
# same hand-derivation as PINNED_FLD02_ADJACENCY_STRING above -- label text,
# a colon, ONE space, then the value text, no line break -- applied to the
# two new list-item constructs' :returns: values. Derived from D-07's
# stated property, never from reading a build's output (D-14, milestone
# invariant #4).
PINNED_FLD02_LIST_ITEM_BULLET_ADJACENCY_STRING = (
    "Returns: fld02 listitem bullet returns sentinel."
)
PINNED_FLD02_LIST_ITEM_ENUM_ADJACENCY_STRING = (
    "Returns: fld02 listitem enum returns sentinel."
)

# FLD-03 per-sub-part parametrize cases: (heading, next_heading, name, type).
# Spans the multi-value construct (both its entries), the single-entry
# construct and the non-ASCII construct, so one shape's success cannot mask
# another's failure (plan requirement).
_PARAM_NAME_TYPE_CASES = [
    pytest.param(_H_MULTI, _H_SINGLE_ENTRY, "alpha", "str", id="multi-value-alpha"),
    pytest.param(_H_MULTI, _H_SINGLE_ENTRY, "beta", "int", id="multi-value-beta"),
    pytest.param(_H_SINGLE_ENTRY, _H_TRIO, "only", "str", id="single-entry"),
    pytest.param(_H_NONASCII, _H_COLLAPSED, "名前", "str", id="non-ascii"),
]


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the field-body typography gate",
)
class TestFieldBodyTypographyGate:
    """
    Per-sub-part FLD-02/FLD-03 structural RED evidence (Phase 38, GATE-01),
    plus FLD-01's field-body-side positional check.

    Requirements: FLD-01, FLD-02, FLD-03.
    """

    # -- FLD-03, per sub-part (D-06): name / type / label, three separate
    #    checks, never one blanket check over the field body. --

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
        assert expected in region, (
            f"FLD-03: expected the parameter name {name!r} to emit "
            f"{expected!r} (contract section 5.2 row 1), not found in "
            f"region:\n{region}"
        )

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
        assert expected in region, (
            f"FLD-03: expected the type {type_text!r} to emit {expected!r} "
            f"(contract section 5.2 row 2), not found in region:\n{region}"
        )

    def test_fld03_field_label_unchanged_and_distinct_from_name_and_type(
        self, typ_text: str
    ) -> None:
        """FLD-03 sub-part LABEL (D-06): the field label keeps the
        unchanged, proportional-bold form
        (strong(text("Parameters") + text(": "))) and its wrapper SHAPE is
        byte-distinct from both the bold-monospace name call and the
        italic-monospace type call -- 'distinct from the plain-bold field
        label' is FLD-03's actual mechanical demand (contract section 5.2
        row 3). Asserted explicitly, not assumed."""
        region = _section(typ_text, _H_MULTI, _H_SINGLE_ENTRY)
        expected_label = 'strong(text("Parameters") + text(": "))'
        assert expected_label in region, (
            f"FLD-03: expected the field label's unchanged form "
            f"{expected_label!r} in region:\n{region}"
        )
        name_call = _expected_bold_mono("alpha")
        type_call = _expected_italic_mono("str")

        def _wrapper_shape(call: str) -> str:
            return re.sub(r'"[^"]*"', '"..."', call)

        label_wrapper = _wrapper_shape(expected_label)
        name_wrapper = _wrapper_shape(name_call)
        type_wrapper = _wrapper_shape(type_call)
        assert label_wrapper != name_wrapper, (
            "FLD-03: the field label's wrapper shape must be byte-distinct "
            f"from the name's bold-monospace wrapper shape; both were "
            f"{label_wrapper!r}"
        )
        assert label_wrapper != type_wrapper, (
            "FLD-03: the field label's wrapper shape must be byte-distinct "
            f"from the type's italic-monospace wrapper shape; both were "
            f"{label_wrapper!r}"
        )
        assert name_wrapper != type_wrapper, (
            "FLD-03: the name's bold-monospace wrapper shape and the "
            f"type's italic-monospace wrapper shape must themselves "
            f"differ; both were {name_wrapper!r}"
        )

    # -- FLD-03 edges --

    def test_fld03_typeless_param_exactly_one_bold_mono_zero_italic_mono(
        self, typ_text: str
    ) -> None:
        """FLD-03 empty edge: a :param: entry with a name but no :type:
        emits exactly one bold-monospace call and zero italic-monospace
        calls for that entry.

        Scoped to start at the field list's own label
        (``strong(text("Parameters") + text(": "))``), not at the section
        heading: the fixture's ``.. py:function:: field_name_without_type
        (untyped)`` signature shares the literal string "untyped" with the
        field-body parameter name it documents, and the signature's own
        parameter-name rule (SIG-04, 37-EMISSION-CONTRACT.md section 5.2
        rule 2) unconditionally italicises a bare parameter name regardless
        of whether it carries a type annotation -- an orthogonal Phase-37
        mechanism this plan does not touch. Including the ``desc_signature``
        block in the region would make the "zero italic-monospace calls"
        assertion fail on that unrelated ``emph(raw("untyped"))``, not on
        anything this plan's ``literal_emphasis`` handler emits."""
        section = _section(typ_text, _H_NOTYPE, _H_NONASCII)
        field_marker = 'strong(text("Parameters") + text(": "))'
        region = section[section.index(field_marker) :]
        bold_call = _expected_bold_mono("untyped")
        count = region.count(bold_call)
        assert count == 1, (
            f"FLD-03 empty edge: expected exactly ONE bold-monospace call "
            f"{bold_call!r}, found {count} in region:\n{region}"
        )
        assert "emph(raw(" not in region, (
            "FLD-03 empty edge: a typeless :param: entry must emit ZERO "
            f"italic-monospace calls, found at least one in region:\n{region}"
        )

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
        assert expected in region, (
            f"FLD-03 encoding: expected the non-ASCII name to round-trip "
            f"into {expected!r}, not found in region:\n{region}"
        )
        assert "名前" in expected, (
            "FLD-03 encoding: escape_typst_string must not mangle the "
            "non-ASCII code points of the parameter name"
        )

    def test_fld03_no_zero_width_space_anywhere_in_field_bodies(
        self, typ_text: str
    ) -> None:
        """FLD-03: no zero-width space -- neither the literal U+200B byte
        nor its Typst escape form -- appears anywhere inside a field
        body's emitted bytes (contract section 5.3, the OUTPUT-assertion
        form of the trap: this proves the wrong escape helper -- Phase
        37's _emit_signature_leaf_wrapper -- was not used, without grepping
        the source for a helper name)."""
        region = _slice(typ_text, _heading_marker(_H_MULTI), None)
        zwsp = chr(0x200B)
        assert zwsp not in region, (
            "FLD-03: found a literal U+200B zero-width-space byte inside a "
            f"field body's emitted bytes:\n{region!r}"
        )
        assert "\\u{200B}" not in region, (
            "FLD-03: found the 8-character Typst escape sequence for "
            f"U+200B inside a field body's emitted bytes:\n{region!r}"
        )

    # -- FLD-03 cross-reference composition (Pitfall 2) --

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
        assert re.search(pattern, region), (
            f"FLD-03 Pitfall 2: expected {expected_type!r} to compose "
            f"nested inside the emitted link() call immediately after "
            f"{link_open!r}, not found in region:\n{region}"
        )

    # -- FLD-02 inline half (D-07) --

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
        assert forbidden not in region, (
            "FLD-02/D-07: expected the single-value :returns: body to NOT "
            f"be wrapped in a block-level par(...) call ({forbidden!r} "
            f"must be absent):\n{region}"
        )

    def test_fld02_single_value_pdf_adjacency_matches_pinned_string(
        self, pdf_text: str
    ) -> None:
        """FLD-02 inline half, compiled-PDF adjacency (D-07): a
        single-value field's label and value are adjacent on ONE line of
        the compiled PDF's extracted text. Mirrors
        tests/test_confval_field_spacing_render_gate.py's pinned-constant
        convention; PINNED_FLD02_ADJACENCY_STRING is hand-derived from
        contract section 4.3 property 1."""
        assert PINNED_FLD02_ADJACENCY_STRING in pdf_text, (
            f"FLD-02: expected the pinned adjacency string "
            f"{PINNED_FLD02_ADJACENCY_STRING!r} in the extracted PDF "
            f"text -- label and value must share one line:\n{pdf_text!r}"
        )

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
        assert forbidden not in region, (
            "FLD-02/D-07: expected the single-entry :param:'s field body "
            f"to NOT be wrapped in a block-level par(...) call "
            f"({forbidden!r} must be absent):\n{region}"
        )

    # -- FLD-02 the D-07/D-08 trap --

    def test_fld02_consecutive_single_value_fields_stay_on_separate_lines(
        self, pdf_text: str
    ) -> None:
        """FLD-02 the D-07/D-08 trap: :returns:, :rtype: and :raises: do
        NOT all appear on one line of the extracted PDF text -- each label
        starts its own line. This is the assertion that fails if the
        implementation routes the newly-inlined bodies through the
        inter-field separator (FID-09) that the collapsed-inline case
        uses, which would produce a ZERO interval where D-08 measured
        20.438pt per field."""
        returns_idx = pdf_text.index("Returns:")
        rtype_idx = pdf_text.index("Return type:", returns_idx)
        raises_idx = pdf_text.index("Raises:", rtype_idx)
        between_returns_rtype = pdf_text[returns_idx:rtype_idx]
        between_rtype_raises = pdf_text[rtype_idx:raises_idx]
        assert "\n" in between_returns_rtype, (
            "FLD-02/D-08: expected 'Returns:' and 'Return type:' to "
            f"occupy separate lines; found no newline between them: "
            f"{between_returns_rtype!r}"
        )
        assert "\n" in between_rtype_raises, (
            "FLD-02/D-08: expected 'Return type:' and 'Raises:' to occupy "
            f"separate lines; found no newline between them: "
            f"{between_rtype_raises!r}"
        )

    # -- FLD-02 bulleted half -- NON-REGRESSION, expected GREEN both
    #    directions. Never convert this into a defect case. --

    def test_fld02_bulleted_multi_value_non_regression_control(
        self, typ_text: str
    ) -> None:
        """FLD-02 bulleted half -- NON-REGRESSION CONTROL. The multi-entry
        :param: group already emits ONE bulleted-list() call containing
        its entries in source order pre-phase; this must stay true, and
        this test must never be repaired into a defect case."""
        region = _section(typ_text, _H_MULTI, _H_SINGLE_ENTRY)
        list_open_count = region.count("list({")
        assert list_open_count == 1, (
            f"FLD-02: expected exactly one list({{ call wrapping both "
            f":param: entries, found {list_open_count} in region:\n{region}"
        )
        alpha_idx = region.find('"alpha"')
        beta_idx = region.find('"beta"')
        assert alpha_idx != -1 and beta_idx != -1, (
            "FLD-02 ordering: expected both 'alpha' and 'beta' present in "
            f"region:\n{region}"
        )
        assert alpha_idx < beta_idx, (
            "FLD-02 ordering: expected the bulleted :param: entries in "
            f"source order (alpha before beta); got alpha={alpha_idx}, "
            f"beta={beta_idx}"
        )

    # -- FLD-01's field-body-side positional check --

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
        assert desc_content_idx != -1, (
            "FLD-01: expected the enclosing desc_content wrapper's opening "
            f"token {pad_open!r} in region:\n{region}"
        )
        field_list_idx = region.find(pad_open, desc_content_idx + len(pad_open))
        assert field_list_idx != -1, (
            "FLD-01: expected a SECOND occurrence of the wrapper opening "
            f"token {pad_open!r} (the field_list's own nested pad) after "
            f"the desc_content wrapper's opening at index "
            f"{desc_content_idx}, region:\n{region}"
        )
        label_call = 'strong(text("Returns")'
        label_idx = region.find(label_call)
        assert label_idx != -1, (
            f"FLD-01: expected the first field label call {label_call!r} "
            f"in region:\n{region}"
        )
        assert desc_content_idx < field_list_idx < label_idx, (
            "FLD-01: expected desc_content wrapper open < field_list "
            f"wrapper open < first field label bytes; got "
            f"{desc_content_idx}, {field_list_idx}, {label_idx}"
        )

    # -- FLD-02 list-item nesting gap (38-09 gap closure; 38-VERIFICATION.md
    #    gap 1 / 38-REVIEW.md CR-01): visit_paragraph/depart_paragraph check
    #    self.in_list_item BEFORE self._field_body_unwrapped_paragraph, and
    #    nothing resets in_list_item for a field_list/field/field_body/
    #    paragraph nested inside a list item, so D-13's forced parbreak()
    #    fast-path fires first and reintroduces the pre-Phase-38 label/value
    #    split -- but only inside a list item. --

    def test_fld02_list_item_bullet_single_value_pdf_adjacency_matches_pinned_string(
        self, pdf_text: str
    ) -> None:
        """FLD-02 list-item adjacency edge (bullet context): a single-value
        field's label and value are adjacent on ONE line of the compiled
        PDF's extracted text even when the enclosing desc is documented
        inside a bullet list item. Mirrors
        test_fld02_single_value_pdf_adjacency_matches_pinned_string exactly,
        just nested one list item deeper."""
        assert PINNED_FLD02_LIST_ITEM_BULLET_ADJACENCY_STRING in pdf_text, (
            "FLD-02 list-item (bullet): expected the pinned adjacency "
            f"string {PINNED_FLD02_LIST_ITEM_BULLET_ADJACENCY_STRING!r} in "
            f"the extracted PDF text -- label and value must share one "
            f"line even inside a bullet list item:\n{pdf_text!r}"
        )

    def test_fld02_list_item_enum_single_value_pdf_adjacency_matches_pinned_string(
        self, pdf_text: str
    ) -> None:
        """FLD-02 list-item adjacency edge (enumerated context): the same
        property as the bullet-context test above, for the enumerated-list
        construct's :returns: field."""
        assert PINNED_FLD02_LIST_ITEM_ENUM_ADJACENCY_STRING in pdf_text, (
            "FLD-02 list-item (enumerated): expected the pinned adjacency "
            f"string {PINNED_FLD02_LIST_ITEM_ENUM_ADJACENCY_STRING!r} in "
            f"the extracted PDF text -- label and value must share one "
            f"line even inside an enumerated list item:\n{pdf_text!r}"
        )

    def test_fld02_list_item_single_value_emits_no_forced_break_between_label_and_value(
        self, typ_text: str
    ) -> None:
        """FLD-02 list-item adjacency edge, structural twin of the PDF
        assertion above: the emitted .typ contains no forced paragraph-break
        call between the label and the value inside the bullet-list-item
        construct. This is the assertion that names the defect's mechanism
        directly -- in_list_item's branch firing first inserts exactly this
        parbreak() between the label and the value."""
        region = _section(typ_text, _H_LI_BULLET, _H_LI_ENUM)
        label_call = 'strong(text("Returns") + text(": "))'
        label_idx = region.index(label_call)
        value_call = 'text("fld02 listitem bullet returns sentinel.")'
        value_idx = region.index(value_call, label_idx)
        between = region[label_idx + len(label_call) : value_idx]
        assert "parbreak()" not in between, (
            "FLD-02 list-item (bullet): expected NO forced paragraph-break "
            f"call between the label and the value inside a bullet list "
            f"item; found one in:\n{between!r}"
        )

    def test_fld02_list_item_lone_field_has_no_trailing_inter_field_break(
        self, typ_text: str
    ) -> None:
        """FLD-02 list-item empty edge: the bullet construct's :returns:
        field has no sibling field, so depart_field_body's D-07/D-08
        compensating parbreak() -- guarded on the parent field having a
        following sibling -- must not fire after its value either."""
        region = _section(typ_text, _H_LI_BULLET, _H_LI_ENUM)
        value_call = 'text("fld02 listitem bullet returns sentinel.")'
        value_idx = region.index(value_call)
        after = region[value_idx + len(value_call) :]
        assert "parbreak()" not in after, (
            "FLD-02 list-item (bullet) empty edge: expected NO trailing "
            f"inter-field parbreak() after the lone field's value; found "
            f"one in:\n{after!r}"
        )

    def test_fld02_list_item_consecutive_fields_stay_on_separate_lines(
        self, pdf_text: str
    ) -> None:
        """FLD-02 list-item ordering edge: :returns:, :rtype: and :raises:
        inside the enumerated list item stay in source order and on
        separate lines of the extracted PDF text -- mirrors
        test_fld02_consecutive_single_value_fields_stay_on_separate_lines,
        scoped to start from the enumerated construct's own 'Returns:'
        occurrence so the top-level trio's identical labels earlier in the
        document cannot satisfy this test by accident."""
        list_item_returns_idx = pdf_text.index(
            PINNED_FLD02_LIST_ITEM_ENUM_ADJACENCY_STRING
        )
        rtype_idx = pdf_text.index("Return type:", list_item_returns_idx)
        raises_idx = pdf_text.index("Raises:", rtype_idx)
        between_returns_rtype = pdf_text[list_item_returns_idx:rtype_idx]
        between_rtype_raises = pdf_text[rtype_idx:raises_idx]
        assert "\n" in between_returns_rtype, (
            "FLD-02 list-item ordering: expected 'Returns:' and 'Return "
            f"type:' to occupy separate lines; found no newline between "
            f"them: {between_returns_rtype!r}"
        )
        assert "\n" in between_rtype_raises, (
            "FLD-02 list-item ordering: expected 'Return type:' and "
            f"'Raises:' to occupy separate lines; found no newline "
            f"between them: {between_rtype_raises!r}"
        )

    # -- Determinism --

    def test_determinism_two_builds_produce_byte_identical_typ(
        self,
        field_body_typography_render_gate_dir: Path,
        tmp_path_factory: pytest.TempPathFactory,
    ) -> None:
        """Two builds into two different output directories produce
        byte-identical .typ."""
        build_dir_a = tmp_path_factory.mktemp("fldtypo_determinism_a")
        build_dir_b = tmp_path_factory.mktemp("fldtypo_determinism_b")
        result_a = _run_sphinx_build_typst(
            field_body_typography_render_gate_dir, build_dir_a
        )
        result_b = _run_sphinx_build_typst(
            field_body_typography_render_gate_dir, build_dir_b
        )
        assert result_a.returncode == 0, (
            f"sphinx-build -b typst (build A) failed:\n"
            f"stdout: {result_a.stdout}\nstderr: {result_a.stderr}"
        )
        assert result_b.returncode == 0, (
            f"sphinx-build -b typst (build B) failed:\n"
            f"stdout: {result_b.stdout}\nstderr: {result_b.stderr}"
        )
        text_a = (build_dir_a / "index.typ").read_text(encoding="utf-8")
        text_b = (build_dir_b / "index.typ").read_text(encoding="utf-8")
        assert text_a == text_b, (
            "Determinism: two builds of the same fixture produced "
            "different index.typ bytes"
        )
