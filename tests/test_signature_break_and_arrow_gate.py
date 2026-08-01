"""
Phase 37, GATE-01: SIG-06 (real arrow glyph), SIG-08 (exactly one break) and
D-11 (optional-group separator) gates against the UNTOUCHED translator.

This module is a DELIBERATE RED window (37-02-PLAN.md). Every expected
string and every expected count below is hand-derived from
``37-EMISSION-CONTRACT.md`` sections 6.1, 6.2, 7 and 8 -- never copied from
running the translator (ROADMAP SC#5 / milestone invariant #4). Against the
pre-phase translator this module reports:

- RED (must flip GREEN in plan 37-05): the SIG-08 exact-break-count
  assertion, the SIG-08 no-adjacent-break assertion, the SIG-06 arrow-glyph
  assertion, the D-11 separator-placement assertion, and the D-11
  target-vs-defective PDF-text assertion.
- GREEN throughout, by design, as CONTROLS (must never be "fixed" into the
  defect case): the SIG-08 content-follows-nested-member assertion, the
  SIG-08 sibling-bodyless-desc assertion, the D-11 explicit-concatenation
  non-regression assertion, and the D-11 nested-optional (printf) control.

See ``.planning/phases/37-signature-typography-the-desc-family/
37-GATE-EVIDENCE-02.md`` for the verbatim RED/CONTROL split recorded against
a named commit.
"""

import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


def _strip_zwsp(text: str) -> str:
    """
    Strip U+200B (zero-width space) from PDF-extracted text before any
    comparison.

    37-EMISSION-CONTRACT.md section 4.2 [measured]: once ZWSP is present
    ANYWHERE in a document, ``pypdf.extract_text()`` returns U+200B both
    where the translator injected it AND, spuriously, at unrelated glyph
    boundaries. A compiled-PDF text assertion that skips this strip will
    flake in a way that looks like a rendering bug. Applied unconditionally
    on every compiled-PDF comparison in this module, even though this
    fixture's pre-phase output contains no ZWSP -- once Phase 37's D-07
    monospace/ZWSP injection lands, other fixtures compiled in the same
    process may have already exercised the hazard.
    """
    return text.replace("​", "")


@pytest.fixture
def signature_break_and_arrow_gate_dir():
    """Return the path to the signature_break_and_arrow_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "signature_break_and_arrow_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typst`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``)
    so the exact interpreter/venv already running this test is reused,
    sidestepping the documented NixOS-sandbox PATH-shadowing hazard (see
    ``tests/test_pdf_render_gate.py`` and
    ``tests/test_desc_bodyless_concat_render_gate.py`` for the established
    pattern this helper clones).
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


def _build_typ(signature_break_and_arrow_gate_dir: Path, temp_build_dir: Path) -> str:
    """Build the fixture through ``-b typst`` and return the emitted ``.typ``."""
    result = _run_sphinx_build_typst(signature_break_and_arrow_gate_dir, temp_build_dir)
    assert result.returncode == 0, (
        f"sphinx-build -b typst failed:\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    index_typ = temp_build_dir / "index.typ"
    assert index_typ.exists(), "index.typ was not generated"
    return index_typ.read_text(encoding="utf-8")


def _extract_pdf_text(typ_path: Path, temp_build_dir: Path) -> str:
    """
    Compile ``typ_path`` to PDF via a real ``typst.compile()`` call (no
    try/except -- a compilation failure must propagate and fail the test
    loudly) and return the U+200B-stripped extracted text.
    """
    pdf_output = temp_build_dir / "index.pdf"
    typst.compile(str(typ_path), output=str(pdf_output))
    assert pdf_output.exists(), "PDF file was not created"
    assert pdf_output.stat().st_size > 0, "PDF file is empty"
    reader = pypdf.PdfReader(str(pdf_output))
    full_text = "\n".join(page.extract_text() for page in reader.pages)
    return _strip_zwsp(full_text)


# ---------------------------------------------------------------------------
# SIG-08: exactly one break -- structural assertions on the emitted .typ.
# No typst/pypdf skip needed; these only require `-b typst`.
# ---------------------------------------------------------------------------


class TestSigBreakStructuralGate:
    """
    Structural SIG-08 assertions on the emitted ``.typ``.

    Requirements: SIG-08 (37-EMISSION-CONTRACT.md section 8).
    """

    def test_sig08_exact_break_count_after_fix(
        self, signature_break_and_arrow_gate_dir, temp_build_dir
    ):
        """
        SIG-08: the whole fixture must contain EXACTLY 8 ``parbreak()``
        statements once the emission-position-marker fix
        (37-EMISSION-CONTRACT.md section 8) lands.

        Derivation (from the fixture's doctree, measured this session via
        ``env.get_and_resolve_doctree`` -- 9 ``desc`` nodes total, 2 of
        which are nested):

        - Construct 1 (SigBreakOuterClassOne + its nested
          sig_break_inner_method_one): 2 ``desc`` departures. The inner
          method's body has nothing after it inside the outer class body,
          so nothing is emitted between the inner ``desc``'s own
          ``parbreak()`` and the outer ``desc``'s own departure -- the
          outer's break is SUPPRESSED by the fix. Contributes 1.
        - Construct 2 (SigBreakOuterClassTwo + its nested
          sig_break_inner_method_two + a trailing paragraph): 2 ``desc``
          departures, but the trailing paragraph's own ``par(...)`` emits
          content between the inner ``desc``'s break and the outer
          ``desc``'s departure, so the marker never matches -- NEITHER
          break is suppressed. Contributes 2.
        - Construct 3 (the two sibling body-less confvals): 2 ``desc``
          departures, non-nested; each confval's own signature/field
          content is emitted before its own departure, so the marker
          never matches. Contributes 2.
        - Construct 4 (sig_arrow_get_value): 1 ``desc`` departure,
          non-nested. Contributes 1.
        - Construct 5 (connect): 1 ``desc`` departure, non-nested.
          Contributes 1.
        - Construct 6 (printf): 1 ``desc`` departure, non-nested.
          Contributes 1.

        Total after the fix: 1 + 2 + 2 + 1 + 1 + 1 = 8.

        Pre-phase (the untouched translator emits an unconditional
        ``parbreak()`` per ``desc`` departure, with no suppression logic
        at all): the actual count is 9 (one per ``desc`` node) -- this
        assertion is EXPECTED TO FAIL pre-phase.
        """
        typ_text = _build_typ(signature_break_and_arrow_gate_dir, temp_build_dir)
        actual_count = typ_text.count("parbreak()")
        assert actual_count == 8, (
            "SIG-08: expected exactly 8 parbreak() statements after the "
            "emission-position-marker fix (37-EMISSION-CONTRACT.md section "
            f"8) -- got {actual_count}. See this test's docstring for the "
            "full per-construct derivation."
        )

    def test_sig08_no_adjacent_break_statements_anywhere(
        self, signature_break_and_arrow_gate_dir, temp_build_dir
    ):
        """
        SIG-08: no two ``parbreak()`` statements may appear adjacent with
        only whitespace between them ANYWHERE in the emitted ``.typ`` --
        this is the requirement's actual wording ("exactly one break") and
        is what fails pre-phase in construct 1 (SigBreakOuterClassOne's
        nested method, whose one-line body has nothing after it, so the
        inner and outer ``desc`` departures fire back-to-back).
        """
        typ_text = _build_typ(signature_break_and_arrow_gate_dir, temp_build_dir)
        lines = typ_text.splitlines()
        adjacent_positions = [
            i
            for i in range(len(lines) - 1)
            if lines[i].strip() == "parbreak()" and lines[i + 1].strip() == "parbreak()"
        ]
        assert adjacent_positions == [], (
            "SIG-08: found adjacent parbreak() statements with nothing but "
            f"whitespace between them at line(s) {adjacent_positions} -- "
            "the doubled-break defect (37-EMISSION-CONTRACT.md section 8) "
            f"is present:\n{typ_text}"
        )

    def test_sig08_content_follows_nested_member_stays_separated(
        self, signature_break_and_arrow_gate_dir, temp_build_dir
    ):
        """
        CONTROL -- must PASS both before and after the fix.

        SIG-08: the "content follows the nested member" shape (construct
        2). A naive desc-nesting-DEPTH-COUNTER fix (explicitly forbidden by
        37-EMISSION-CONTRACT.md section 8) would suppress the inner
        ``desc``'s break unconditionally based on nesting depth alone,
        running "Inner method two body." and "Trailing paragraph after the
        nested member." together with NO break between them. The correct
        emission-position-marker fix never does this, because the trailing
        paragraph's own content is emitted between the two `desc`
        departures. This assertion passes pre-phase (the unconditional
        current behaviour) AND must keep passing post-fix -- if this ever
        goes RED after a fix lands, the fix used a depth counter instead of
        the marker and must be corrected, not this assertion weakened.
        """
        typ_text = _build_typ(signature_break_and_arrow_gate_dir, temp_build_dir)
        member_idx = typ_text.index("Inner method two body.")
        trailing_idx = typ_text.index(
            "Trailing paragraph after the nested member.", member_idx
        )
        between = typ_text[member_idx:trailing_idx]
        assert between.count("parbreak()") >= 1, (
            "SIG-08 control: expected at least one parbreak() between the "
            "nested member's body and the trailing paragraph that follows "
            "it -- a naive depth-counter fix would run them together with "
            f"none:\n{between}"
        )

    def test_sig08_sibling_bodyless_control_keeps_one_break(
        self, signature_break_and_arrow_gate_dir, temp_build_dir
    ):
        """
        CONTROL -- must PASS both before and after the fix.

        SIG-08: the sibling body-less ``desc`` control (construct 3, mirrors
        ``tests/test_desc_bodyless_concat_render_gate.py``'s FID-06 gate).
        Two back-to-back body-less confval ``desc`` siblings are NOT nested,
        so the SIG-08 fix must never touch this shape -- exactly one
        ``parbreak()`` separates them, both before and after.
        """
        typ_text = _build_typ(signature_break_and_arrow_gate_dir, temp_build_dir)
        first_idx = typ_text.index("sig_break_confval_one")
        second_idx = typ_text.index("sig_break_confval_two", first_idx)
        between = typ_text[first_idx:second_idx]
        assert between.count("parbreak()") == 1, (
            "SIG-08 control: expected exactly one parbreak() between the "
            "two sibling body-less confval desc nodes -- got "
            f"{between.count('parbreak()')}:\n{between}"
        )


# ---------------------------------------------------------------------------
# SIG-06: the real arrow glyph -- compiled-PDF assertion.
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the SIG-06 render gate",
)
class TestSigArrowPdfGate:
    """
    Real-compile acceptance gate for SIG-06: a real arrow glyph (U+2192)
    must reach the compiled PDF's extracted text, and the ASCII two-
    character arrow sequence must be absent.

    Requirements: SIG-06 (37-EMISSION-CONTRACT.md section 7).
    """

    def test_sig06_arrow_glyph_present_ascii_arrow_absent(
        self, signature_break_and_arrow_gate_dir, temp_build_dir
    ):
        """
        SIG-06: presence of the real arrow glyph U+2192 in the compiled
        PDF's extracted text, and absence of the ASCII "->" sequence,
        anywhere in the extracted text.

        Pre-phase, ``visit_desc_returns`` emits the literal
        ``text(" -> ")`` (37-EMISSION-CONTRACT.md section 7's "pre-phase"
        state) -- the ASCII arrow is present and the real glyph is absent,
        so this assertion is EXPECTED TO FAIL pre-phase.
        """
        typ_text = _build_typ(signature_break_and_arrow_gate_dir, temp_build_dir)
        typ_path = temp_build_dir / "index.typ"
        full_text = _extract_pdf_text(typ_path, temp_build_dir)

        assert "→" in full_text, (
            "SIG-06: expected the real arrow glyph U+2192 in the compiled "
            f"PDF's extracted text -- not found:\n{full_text}"
        )
        assert "->" not in full_text, (
            "SIG-06: the ASCII two-character arrow '->' must be absent "
            f"from the compiled PDF's extracted text -- found it:\n{full_text}"
        )


# ---------------------------------------------------------------------------
# D-11: the dropped optional-group separator -- its own class, its own
# assertions, never merged into a SIG-05 check.
# ---------------------------------------------------------------------------


class TestD11SeparatorStructuralGate:
    """
    Structural D-11 assertions on the emitted ``.typ`` -- no typst/pypdf
    skip needed.

    Requirements: D-11 (37-EMISSION-CONTRACT.md section 6.1/6.2). D-11 is
    covered by no SIG requirement; it is never folded into a SIG-05
    assertion.
    """

    def test_d11_separator_lands_inside_the_bracket(
        self, signature_break_and_arrow_gate_dir, temp_build_dir
    ):
        """
        D-11: for the ``connect(host, port=8080, [timeout], **kwargs)``
        defect case (construct 5), the separator expression (the quoted
        string literal ``", "``, regardless of whether the pre-phase
        ``text(...)`` or the post-fix ``raw(...)`` wrapper carries it --
        37-EMISSION-CONTRACT.md section 6) must land strictly BETWEEN the
        last optional parameter ("timeout") and the closing bracket ``]``:
        its index must be greater than "timeout"'s index and less than the
        closing bracket's index.

        Pre-phase, ``depart_desc_optional`` emits no separator at all
        (37-EMISSION-CONTRACT.md section 6.1's "pre-phase typsphinx" row:
        ``connect(host, port=8080, [timeout]**kwargs)``) -- no ``", "``
        token exists in this region, so this assertion is EXPECTED TO FAIL
        pre-phase.
        """
        typ_text = _build_typ(signature_break_and_arrow_gate_dir, temp_build_dir)
        connect_region_start = typ_text.index('"connect"')
        connect_region_end = typ_text.index(
            "<index:d-11-nested-optional-non-regression-control>",
            connect_region_start,
        )
        region = typ_text[connect_region_start:connect_region_end]

        timeout_idx = region.index('"timeout"')
        bracket_close_idx = region.index('"]"', timeout_idx)
        separator_idx = region.find('", "', timeout_idx)

        assert timeout_idx < separator_idx < bracket_close_idx, (
            "D-11: expected the ', ' separator strictly between the last "
            "optional parameter ('timeout') and the closing bracket -- "
            f"timeout_idx={timeout_idx}, separator_idx={separator_idx}, "
            f"bracket_close_idx={bracket_close_idx}:\n{region}"
        )

    def test_d11_explicit_concatenation_non_regression(
        self, signature_break_and_arrow_gate_dir, temp_build_dir
    ):
        """
        CONTROL / NON-REGRESSION -- must PASS both before and after.

        D-11: 37-EMISSION-CONTRACT.md section 6.2 corrects CONTEXT.md
        D-11's claim that the closing bracket and the following parameter
        ("**kwargs") are juxtaposed with no ``+`` joining them. That claim
        does NOT reproduce on the current tree -- a real build already
        joins them with an explicit ``" + "`` (measured this session). No
        code change is required for this half of D-11; this assertion
        exists to PIN that behaviour so the rewrite never regresses it.
        Label: do not "fix" this into requiring a code change -- the
        contract records that none is needed.
        """
        typ_text = _build_typ(signature_break_and_arrow_gate_dir, temp_build_dir)
        connect_region_start = typ_text.index('"connect"')
        bracket_close_idx = typ_text.index('"]"', connect_region_start)
        kwargs_idx = typ_text.index('"**kwargs"', bracket_close_idx)
        between = typ_text[bracket_close_idx + len('"]"') : kwargs_idx]

        assert " + " in between, (
            "D-11 non-regression: expected the closing bracket expression "
            "and the following '**kwargs' expression to remain joined by "
            f"an explicit ' + ' concatenation operator -- got: {between!r}"
        )


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the D-11 render gate",
)
class TestD11SeparatorPdfGate:
    """
    Real-compile D-11 assertions on the compiled PDF's extracted text.

    Requirements: D-11 (37-EMISSION-CONTRACT.md section 6.1).
    """

    def test_d11_target_rendering_present_defective_rendering_absent(
        self, signature_break_and_arrow_gate_dir, temp_build_dir
    ):
        """
        D-11: the target rendering from 37-EMISSION-CONTRACT.md section
        6.1's table -- ``connect(host, port=8080, [timeout, ]**kwargs)`` --
        must be present in the compiled PDF's extracted text, and the
        current defective rendering -- ``connect(host, port=8080,
        [timeout]**kwargs)`` -- must be absent.

        Pre-phase, the defective rendering IS what is produced (measured
        this session), so this assertion is EXPECTED TO FAIL pre-phase.
        """
        typ_text = _build_typ(signature_break_and_arrow_gate_dir, temp_build_dir)
        typ_path = temp_build_dir / "index.typ"
        full_text = _extract_pdf_text(typ_path, temp_build_dir)

        assert "connect(host, port=8080, [timeout, ]**kwargs)" in full_text, (
            "D-11: expected the target rendering "
            "'connect(host, port=8080, [timeout, ]**kwargs)' in the "
            f"compiled PDF's extracted text:\n{full_text}"
        )
        assert "connect(host, port=8080, [timeout]**kwargs)" not in full_text, (
            "D-11: the defective rendering "
            "'connect(host, port=8080, [timeout]**kwargs)' (missing "
            "separator) must be absent from the compiled PDF's extracted "
            f"text:\n{full_text}"
        )

    def test_d11_nested_optional_control_unchanged(
        self, signature_break_and_arrow_gate_dir, temp_build_dir
    ):
        """
        CONTROL -- must PASS both before and after the fix.

        D-11: the nested-optional ``printf(fmt[, args[, more]])`` control
        (construct 6, 37-EMISSION-CONTRACT.md section 6.1's control row).
        Both ``desc_optional`` nodes here are LAST children, so the D-11
        fix's sibling test (against the ``desc_optional`` node, not its
        last child) never fires for either -- the rendering must stay
        byte-identical: ``printf(fmt, [args, [more]])``. This assertion
        passes pre-phase AND must keep passing post-fix -- never convert
        this into the defect case.
        """
        typ_text = _build_typ(signature_break_and_arrow_gate_dir, temp_build_dir)
        typ_path = temp_build_dir / "index.typ"
        full_text = _extract_pdf_text(typ_path, temp_build_dir)

        assert "printf(fmt, [args, [more]])" in full_text, (
            "D-11 control: expected the nested-optional printf rendering "
            "'printf(fmt, [args, [more]])' to stay byte-unchanged in the "
            f"compiled PDF's extracted text:\n{full_text}"
        )
