"""
Phase 38, GATE-01: IND-01..IND-05, FLD-01, D-04, D-11 structural and
left-edge gates against the UNTOUCHED translator.

This module is a DELIBERATE RED window (38-01-PLAN.md). Every expected
``.typ`` token and every column comparison below is hand-derived from
``.planning/phases/38-structural-indentation-info-fields/
38-EMISSION-CONTRACT.md`` sections 1, 1.1, 1.2, 2, 2.3, 2.4, 2.5 and 3 --
never copied from running the translator (``visit_desc_content`` /
``depart_desc_content`` and ``visit_field_list`` / ``depart_field_list``'s
own pad step are the handlers this phase adds; they are still ``pass`` /
untouched on this branch). ROADMAP SC#5 / milestone invariant #4.

Left-edge measurement technique, binding (38-RESEARCH.md Pattern 2): pypdf's
per-glyph ``visitor_text`` callback returns ``x=0, y=0`` on this project's
compiled PDFs and is unusable. ``extraction_mode="layout"`` reconstructs
left-edge indentation as leading whitespace and is the only usable
technique. Every column comparison below is RELATIVE (``>`` or ``==``),
never a pinned point value (D-02) -- the gate cannot be satisfied by
re-valuing ``SHARED_INDENT_STEP``.

Page-index-agnostic by design: once this phase's pad() wrapper actually
lands, every ``desc_content``/``field_list`` gains extra vertical space, so
the fixture's page COUNT and the page each marker lands on will shift.
``_find_page_and_column`` therefore locates every marker by CONTENT across
however many pages the compiled PDF has, rather than a hard-coded page
index -- only the page-boundary construct's OWN cross-page-ness (D-11) is
asserted directly.

Against the pre-phase translator this module reports:

- RED (must flip GREEN once ``visit_desc_content``/``depart_desc_content``
  and ``visit_field_list``'s pad step land): the IND-01 structural token
  test, the IND-04 structural shared-step-at-new-sites test, the FLD-01
  empty/IND-01 empty wrapper-pair-count test, the IND-01 compiled-PDF
  column test, the IND-02 compiled-PDF column test (its first half), and
  the FLD-01 compiled-PDF column test.
- GREEN throughout, by design, as CONTROLS (must never be "fixed" into the
  defect case, and reclassified here rather than forced red): the IND-04
  SC#4 source-grep test (already true pre-phase, contract section 1.1),
  the D-04 block-quote-not-converted test (block_quote is untouched by
  this phase), the IND-04 empty no-wrapper test (there is nothing there
  to wrap either side of the fix), the ordering/determinism test, the
  IND-03 compiled-PDF equality test (0 == 0 pre-phase; the assertion
  exists to catch a NAIVE over-indenting implementation, not to fail
  today), the IND-05 compiled-PDF equality test (0 == 0 pre-phase; D-01
  records IND-05 is asserted, not implemented -- there is no depth
  counter to fail to reset), the second half of the IND-02 compiled-PDF
  test (the resumed class body returns to column 0, trivially, because
  nothing is indented yet), and the D-11/SIG-09 page-boundary test (Phase
  37's ``block(sticky: true, ...)`` already keeps the signature and its
  body's first line together, and neither line carries any indent yet, so
  the equal-column half is trivially true pre-phase too).

See ``.planning/phases/38-structural-indentation-info-fields/
38-GATE-EVIDENCE-01.md`` for the verbatim RED/CONTROL split recorded
against a named commit, the SC#4 discovery grep, and the pre-phase
left-edge column baseline.
"""

import io
import re
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


ZWSP = "\u200b"  # U+200B, written as an explicit escape (not an invisible literal)


def _strip_zwsp(text: str) -> str:
    """
    Strip U+200B (zero-width space) from PDF-extracted text before any
    comparison, defensively -- this fixture's own content injects no
    ZWSP, but other fixtures compiled in the same pytest process may
    already have exercised Phase 37's D-07 monospace/ZWSP injection
    hazard (``tests/test_signature_break_and_arrow_gate.py``'s
    ``_strip_zwsp``, the precedent this mirrors).
    """
    return text.replace(ZWSP, "")


@pytest.fixture(scope="session")
def desc_content_indent_gate_dir():
    """Return the path to the desc_content_indent_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "desc_content_indent_render_gate"


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typst`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``)
    -- the NixOS PATH-shadowing hazard restated in every render-gate module
    in this project (``tests/test_pdf_render_gate.py``'s own
    ``_run_sphinx_build_typst`` is the canonical form this clones).
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


@pytest.fixture(scope="session")
def desc_content_indent_typ_text(desc_content_indent_gate_dir, tmp_path_factory):
    """
    Build the fixture through ``-b typst`` ONCE for the whole session and
    return the emitted ``.typ`` text. No ``typst``/``pypdf`` dependency --
    every purely structural (``.typ``-text-level) test in this module uses
    this fixture, so those tests run even when the optional compiled-PDF
    dependencies are unavailable.
    """
    build_dir = tmp_path_factory.mktemp("desc_content_indent_typ") / "_build"
    result = _run_sphinx_build_typst(desc_content_indent_gate_dir, build_dir)
    assert result.returncode == 0, (
        f"sphinx-build -b typst failed:\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    index_typ = build_dir / "index.typ"
    assert index_typ.exists(), "index.typ was not generated"
    return index_typ.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def desc_content_indent_pdf_bytes(desc_content_indent_gate_dir, tmp_path_factory):
    """
    Build the fixture through ``-b typst`` and compile it to PDF via a
    REAL ``typst.compile()`` call ONCE for the whole session (no
    try/except -- a compilation failure must propagate and fail loudly).
    Only requested by tests inside the ``TYPST_AVAILABLE``/
    ``PYPDF_AVAILABLE``-skipif-gated class below, so this fixture never
    runs (and never requires the optional dependencies) when that class
    is skipped.
    """
    build_dir = tmp_path_factory.mktemp("desc_content_indent_pdf") / "_build"
    result = _run_sphinx_build_typst(desc_content_indent_gate_dir, build_dir)
    assert result.returncode == 0, (
        f"sphinx-build -b typst failed:\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    index_typ = build_dir / "index.typ"
    assert index_typ.exists(), "index.typ was not generated"
    pdf_path = build_dir / "index.pdf"
    typst.compile(str(index_typ), output=str(pdf_path))
    assert pdf_path.exists(), "PDF file was not created"
    assert pdf_path.stat().st_size > 0, "PDF file is empty"
    return pdf_path.read_bytes()


def _layout_lines(pdf_bytes: bytes, page_index: int) -> str:
    """
    Return the ``extraction_mode="layout"`` text for ONE page, U+200B-
    stripped (38-RESEARCH.md Pattern 2). Layout-mode reconstructs a
    monospace-like character grid from the PDF's real glyph positions and
    preserves left-edge indentation as leading whitespace -- the per-glyph
    position API (``visitor_text``) reports ``x=0, y=0`` on this project's
    PDFs and cannot be used for this measurement.
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    return _strip_zwsp(reader.pages[page_index].extract_text(extraction_mode="layout"))


def _leading_columns(layout_text: str, marker_substring: str) -> int:
    """
    Return ``len(line) - len(line.lstrip(" "))`` for the first line of
    ``layout_text`` containing ``marker_substring``. Raises
    ``AssertionError`` (not a bare ``ValueError``/``StopIteration``) if the
    marker is not present on this page, so a missing marker fails as a
    clear, structural pytest assertion rather than an uncaught exception.
    """
    for line in layout_text.splitlines():
        if marker_substring in line:
            return len(line) - len(line.lstrip(" "))
    raise AssertionError(
        f"{marker_substring!r} not found in the given page's layout text"
    )


def _find_page_and_column(
    pdf_bytes: bytes, marker_substring: str, start_page: int = 0
) -> tuple:
    """
    Search pages ``start_page..``  onward for ``marker_substring`` and
    return ``(page_index, leading_column)`` for the first page it is found
    on. Page-index-agnostic by design (see module docstring): every
    column assertion in this module locates its marker by CONTENT, not a
    hard-coded page number, so the fixture's page count is free to change
    once this phase's wrapper actually adds vertical space.
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    for i in range(start_page, len(reader.pages)):
        layout_text = _layout_lines(pdf_bytes, i)
        if marker_substring in layout_text:
            return i, _leading_columns(layout_text, marker_substring)
    raise AssertionError(
        f"{marker_substring!r} not found on any page from index "
        f"{start_page} onward (document has {len(reader.pages)} pages)"
    )


def _slice(typ_text: str, start_marker: str, end_marker: str | None) -> str:
    """
    Return the substring of ``typ_text`` from ``start_marker`` (inclusive)
    up to ``end_marker`` (exclusive), or to the end of the document if
    ``end_marker`` is ``None``. Mirrors
    ``tests/test_signature_typography_gate.py``'s ``_slice`` helper
    exactly, so a region-isolation assertion cannot be satisfied by bytes
    belonging to a different construct.
    """
    start_idx = typ_text.index(start_marker)
    if end_marker is None:
        return typ_text[start_idx:]
    end_idx = typ_text.index(end_marker, start_idx + len(start_marker))
    return typ_text[start_idx:end_idx]


# ---------------------------------------------------------------------------
# Structural (.typ-text-level) assertions -- no typst/pypdf skip needed.
# ---------------------------------------------------------------------------


class TestDescContentIndentStructuralGate:
    """
    Structural assertions on the emitted ``.typ``, requiring only
    ``-b typst`` (no compiled-PDF dependency).

    Requirements: IND-01, IND-04, D-04, FLD-01 (38-EMISSION-CONTRACT.md
    sections 1, 1.1, 1.2, 2, 2.4, 3).
    """

    def test_ind01_structural_wrapper_token_and_position(
        self, desc_content_indent_typ_text
    ):
        """
        IND-01 (38-EMISSION-CONTRACT.md section 2): the ``desc_content``
        body wrapper's opening token ``pad(left: 2.5em, {`` and its
        closing token ``})\\n`` must both appear in the emitted ``.typ``,
        with the opening token positioned AFTER the class signature's own
        closing anchor (``<index:IndFldNestOuterClass>``, emitted by
        ``depart_desc_signature`` -- a handler Phase 38 does not touch,
        D-14's anchor-preservation guarantee) and BEFORE the class body's
        own ``par(`` call -- a positional-index assertion, not a bare
        substring check. Pre-phase, ``visit_desc_content`` /
        ``depart_desc_content`` are both ``pass`` (contract section 2), so
        NEITHER token exists at all: EXPECTED TO FAIL pre-phase.
        """
        typ_text = desc_content_indent_typ_text
        assert "pad(left: 2.5em, {" in typ_text, (
            "IND-01: expected the desc_content body wrapper's opening "
            "token 'pad(left: 2.5em, {' somewhere in the emitted .typ -- "
            "not found (visit_desc_content is still `pass` pre-phase)."
        )
        assert "})\n" in typ_text, (
            "IND-01: expected the desc_content body wrapper's closing "
            "token '})\\n' somewhere in the emitted .typ -- not found."
        )
        signature_close_idx = typ_text.index("<index:IndFldNestOuterClass>")
        pad_open_idx = typ_text.index("pad(left: 2.5em, {", signature_close_idx)
        body_par_idx = typ_text.index(
            'par({text("Outer class body first paragraph', pad_open_idx
        )
        assert signature_close_idx < pad_open_idx < body_par_idx, (
            "IND-01: expected the body wrapper's opening token to land "
            f"AFTER the class signature's closing anchor (index "
            f"{signature_close_idx}) and BEFORE the class body's own "
            f"par( call (index {body_par_idx}) -- got "
            f"pad_open_idx={pad_open_idx}."
        )

    def test_ind04_structural_shared_step_value_at_new_sites(
        self, desc_content_indent_typ_text
    ):
        """
        IND-04 (38-EMISSION-CONTRACT.md sections 1, 2, 3): the shared
        indent step's value (``SHARED_INDENT_STEP`` = ``2.5em``) must
        appear at BOTH new consumer sites this phase adds -- the
        ``desc_content`` body wrapper (section 2) and the ``field_list``
        wrapper (section 3) -- not just at the pre-existing
        ``desc_signature`` hanging-indent site (Phase 37). Pre-phase
        neither new site exists (both handlers are ``pass``/untouched),
        so the wrapper literal ``pad(left: 2.5em, {`` appears ZERO times
        anywhere in the document: EXPECTED TO FAIL pre-phase.
        """
        typ_text = desc_content_indent_typ_text
        occurrences = typ_text.count("pad(left: 2.5em, {")
        assert occurrences >= 2, (
            "IND-04: expected the shared indent step's value to appear "
            "at BOTH the desc_content wrapper and the field_list wrapper "
            "(at least 2 occurrences of 'pad(left: 2.5em, {') -- "
            f"pre-phase neither site exists yet; got {occurrences} "
            "occurrence(s)."
        )

    def test_ind04_structural_single_indent_literal_source_grep(self):
        """
        IND-04 / SC#4 (38-EMISSION-CONTRACT.md section 1.1, the milestone
        invariant #6 "anywhere under X" repo-wide-grep-at-discovery-time
        property): over ``typsphinx/translator.py``, with full-line and
        indented comments filtered out (mirroring
        ``grep -vE '^[[:space:]]*#'``), a search for a numeric
        ``em``-suffixed literal must find EXACTLY ONE line -- the
        ``SHARED_INDENT_STEP`` assignment at line 29. ALREADY TRUE
        pre-phase (contract section 1.1's own measurement, re-verified
        here) and must stay true post-phase, since neither section 2's
        nor section 3's target shape introduces a NEW numeric ``em``
        literal (both spell ``SHARED_INDENT_STEP``): a non-regression
        CONTROL, not a per-requirement RED.
        """
        translator_path = Path(__file__).parent.parent / "typsphinx" / "translator.py"
        source_lines = translator_path.read_text(encoding="utf-8").splitlines()
        filtered = [line for line in source_lines if not re.match(r"^\s*#", line)]
        em_literal_re = re.compile(r"\d+(?:\.\d+)?em\b")
        matches = [line for line in filtered if em_literal_re.search(line)]
        assert len(matches) == 1, (
            "IND-04/SC#4: expected exactly ONE numeric em-suffixed "
            "literal line in typsphinx/translator.py (comments filtered) "
            f"-- the SHARED_INDENT_STEP assignment -- got {len(matches)}: "
            f"{matches}"
        )
        assert "SHARED_INDENT_STEP" in matches[0], (
            "IND-04/SC#4: the sole numeric em-literal line must be the "
            f"SHARED_INDENT_STEP assignment -- got: {matches[0]!r}"
        )

    def test_ind04_d04_block_quote_not_converted(self, desc_content_indent_typ_text):
        """
        IND-04 / D-04 non-conversion (38-EMISSION-CONTRACT.md section
        1.2): the block-quote construct must still emit Typst's own
        ``quote(block: true, {`` form and must NEVER be wrapped in the
        shared indent step -- the composed literal
        ``pad(left: 2.5em, {quote(block: true,`` must never appear.
        ALREADY TRUE pre-phase (``visit_block_quote`` /
        ``depart_block_quote`` are untouched by this phase, D-04) and
        must stay true post-phase: a non-regression CONTROL, not a
        per-requirement RED. Not to be re-opened at verify time (D-04).
        """
        typ_text = desc_content_indent_typ_text
        assert "quote(block: true, {" in typ_text, (
            "D-04: expected the block quote's own quote(block: true, { "
            "form somewhere in the emitted .typ -- not found."
        )
        assert "pad(left: 2.5em, {quote(block: true," not in typ_text, (
            "D-04: block_quote must NEVER be wrapped in the shared "
            "indent step -- found the forbidden composed form in the "
            "emitted .typ."
        )

    def test_ind04_empty_no_desc_no_field_list_region_has_no_wrapper(
        self, desc_content_indent_typ_text
    ):
        """
        IND-04 empty (38-EMISSION-CONTRACT.md sections 2, 3): a document
        region containing no ``desc`` and no ``field_list`` must emit NO
        indent wrapper token at all. ALREADY TRUE pre-phase (there is
        nothing there to wrap) and must stay true post-phase (there is
        STILL nothing there to wrap -- the region is plain prose only):
        a non-regression CONTROL, not a per-requirement RED.
        """
        typ_text = desc_content_indent_typ_text
        region = _slice(
            typ_text,
            'text("No-Desc, No-Field-List CONTROL (IND-04 Empty)")',
            'text("Block Quote (D-04)")',
        )
        assert "pad(left:" not in region, (
            "IND-04 empty: expected NO indent wrapper token in the "
            f"no-desc/no-field-list region -- found one:\n{region}"
        )

    def test_fld01_empty_ind01_empty_bodyless_confval_siblings(
        self, desc_content_indent_typ_text
    ):
        """
        FLD-01 empty / IND-01 empty (38-EMISSION-CONTRACT.md section
        2.4): the two body-less confval siblings (mirroring
        ``tests/test_desc_bodyless_concat_render_gate.py``'s FID-06
        control) must each emit a wrapper pair around their (empty)
        ``desc_content``, and exactly one ``parbreak()`` must separate
        the two siblings. Pre-phase, ``visit_desc_content`` /
        ``depart_desc_content`` are both ``pass``, so NO wrapper pair
        exists for either sibling: EXPECTED TO FAIL pre-phase on the
        wrapper-pair count, even though the break count between them is
        already correct today.
        """
        typ_text = desc_content_indent_typ_text
        first_sibling_region = _slice(
            typ_text, "ind_bodyless_confval_one", "ind_bodyless_confval_two"
        )
        assert first_sibling_region.count("pad(left: 2.5em, {") >= 1, (
            "FLD-01/IND-01 empty: expected at least one desc_content "
            "wrapper pair for the first body-less confval sibling -- "
            f"pre-phase none exists:\n{first_sibling_region}"
        )
        between = first_sibling_region
        assert between.count("parbreak()") == 1, (
            "FLD-01/IND-01 empty: expected exactly one parbreak() "
            "between the two body-less confval siblings -- got "
            f"{between.count('parbreak()')}:\n{between}"
        )

    def test_ordering_determinism_two_builds_byte_identical(
        self, desc_content_indent_gate_dir, tmp_path_factory
    ):
        """
        Ordering / determinism (38-EMISSION-CONTRACT.md section 0's
        "hand-derived, never copied from output" discipline requires a
        stable target to derive against): two independent ``-b typst``
        builds of this fixture must produce byte-identical ``.typ``
        output. ALREADY TRUE pre-phase (neither Sphinx nor this
        translator introduces non-determinism) and must stay true
        post-phase: a non-regression CONTROL, not a per-requirement RED.
        """
        build_dir_a = tmp_path_factory.mktemp("desc_content_indent_det_a") / "_build"
        build_dir_b = tmp_path_factory.mktemp("desc_content_indent_det_b") / "_build"
        result_a = _run_sphinx_build_typst(desc_content_indent_gate_dir, build_dir_a)
        result_b = _run_sphinx_build_typst(desc_content_indent_gate_dir, build_dir_b)
        assert result_a.returncode == 0, (
            f"build A failed:\nstdout: {result_a.stdout}\n" f"stderr: {result_a.stderr}"
        )
        assert result_b.returncode == 0, (
            f"build B failed:\nstdout: {result_b.stdout}\n" f"stderr: {result_b.stderr}"
        )
        typ_a = (build_dir_a / "index.typ").read_text(encoding="utf-8")
        typ_b = (build_dir_b / "index.typ").read_text(encoding="utf-8")
        assert typ_a == typ_b, (
            "Two independent -b typst builds of the SAME fixture produced "
            "DIFFERENT .typ output -- non-deterministic build."
        )


# ---------------------------------------------------------------------------
# Compiled-PDF left-edge assertions -- IND-01..IND-05, FLD-01, D-11.
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the IND/FLD-01 left-edge render gate",
)
class TestDescContentIndentPdfGate:
    """
    Real-compile left-edge acceptance gate for IND-01..IND-05, FLD-01 and
    D-11, using ``pypdf``'s layout-mode text-grid reconstruction
    (38-RESEARCH.md Pattern 2). Every column comparison is RELATIVE
    (``>`` or ``==``), never a pinned point value (D-02) -- the gate
    cannot be satisfied by re-valuing ``SHARED_INDENT_STEP``.
    """

    def test_ind01_body_indented_past_signature(self, desc_content_indent_pdf_bytes):
        """
        IND-01 (38-EMISSION-CONTRACT.md section 2, section 2.3's measured
        table): the class body paragraph's leading-space column must be
        STRICTLY GREATER than the class signature's own column. Pre-phase
        both are flush at column 0 (no wrapper exists): EXPECTED TO FAIL
        pre-phase (0 > 0 is False).
        """
        pdf_bytes = desc_content_indent_pdf_bytes
        _, sig_col = _find_page_and_column(pdf_bytes, "class IndFldNestOuterClass")
        _, body_col = _find_page_and_column(
            pdf_bytes, "Outer class body first paragraph."
        )
        assert body_col > sig_col, (
            "IND-01: expected the class body's leading column "
            f"({body_col}) to be strictly greater than the class "
            f"signature's own column ({sig_col})."
        )

    def test_ind02_nested_body_deeper_and_resumed_body_returns(
        self, desc_content_indent_pdf_bytes
    ):
        """
        IND-02 (38-EMISSION-CONTRACT.md section 2.3's measured table):
        the nested method's body column must be STRICTLY GREATER than
        the class body's own column, AND the class body paragraph that
        RESUMES after the nested member closes must be BACK at the class
        body's own column. Pre-phase everything is flush at column 0:
        EXPECTED TO FAIL pre-phase on the first half (0 > 0 is False);
        the second half (0 == 0) is trivially true pre-phase.
        """
        pdf_bytes = desc_content_indent_pdf_bytes
        _, class_body_col = _find_page_and_column(
            pdf_bytes, "Outer class body first paragraph."
        )
        _, method_body_col = _find_page_and_column(
            pdf_bytes, "Inner method body paragraph."
        )
        _, resumed_col = _find_page_and_column(
            pdf_bytes, "Outer class body resumes here"
        )
        assert method_body_col > class_body_col, (
            "IND-02: expected the nested method's body column "
            f"({method_body_col}) to be strictly greater than the class "
            f"body's own column ({class_body_col})."
        )
        assert resumed_col == class_body_col, (
            "IND-02: expected the class body's RESUMED paragraph column "
            f"({resumed_col}) to equal the class body's own column "
            f"({class_body_col})."
        )

    def test_ind03_nested_signature_equals_parent_body_column(
        self, desc_content_indent_pdf_bytes
    ):
        """
        IND-03 (38-EMISSION-CONTRACT.md section 2.3's measured table):
        the nested method's OWN signature column must be EXACTLY EQUAL
        to the class body's own column -- equality, not ``>``. This is
        the assertion that fails if a naive implementation over-indents
        the nested signature. Pre-phase both are flush at column 0
        (0 == 0): ALREADY TRUE pre-phase -- a non-regression CONTROL for
        this fixture (reclassified in 38-GATE-EVIDENCE-01.md), not a
        per-requirement RED.
        """
        pdf_bytes = desc_content_indent_pdf_bytes
        _, class_body_col = _find_page_and_column(
            pdf_bytes, "Outer class body first paragraph."
        )
        _, method_sig_col = _find_page_and_column(
            pdf_bytes, "ind_fld_nest_inner_method(value)"
        )
        assert method_sig_col == class_body_col, (
            "IND-03: expected the nested method's own signature column "
            f"({method_sig_col}) to equal the class body's own column "
            f"({class_body_col}) -- a naive over-indent would fail this."
        )

    def test_ind05_sibling_top_level_returns_to_margin(
        self, desc_content_indent_pdf_bytes
    ):
        """
        IND-05 (38-EMISSION-CONTRACT.md section 2.3's measured table,
        38-CONTEXT.md D-01): the sibling top-level ``py:function::``
        immediately after the three-level nest closes must be at the
        SAME column as the top-level class signature -- i.e. back at the
        page margin. There is no depth counter (D-01); depth cannot leak
        because the wrapper closes when the outer ``desc_content``
        departs. Pre-phase both are flush at column 0 (0 == 0): ALREADY
        TRUE pre-phase -- a non-regression CONTROL (reclassified in
        38-GATE-EVIDENCE-01.md), not a per-requirement RED. FLAGGED per
        this plan's ``must_haves.truths``: IND-05's edge-probe
        classification was left unresolved at plan time; this assertion
        is the operational proof the plan committed to.
        """
        pdf_bytes = desc_content_indent_pdf_bytes
        _, class_sig_col = _find_page_and_column(
            pdf_bytes, "class IndFldNestOuterClass"
        )
        _, sibling_sig_col = _find_page_and_column(
            pdf_bytes, "ind_fld_nest_sibling_toplevel_function(x)"
        )
        assert sibling_sig_col == class_sig_col, (
            "IND-05: expected the sibling top-level function's column "
            f"({sibling_sig_col}) to equal the top-level class "
            f"signature's own column ({class_sig_col}) -- depth leaked."
        )

    def test_fld01_field_list_deeper_than_method_body(
        self, desc_content_indent_pdf_bytes
    ):
        """
        FLD-01 (38-EMISSION-CONTRACT.md section 3, 38-CONTEXT.md D-03):
        the method's field-list line column must be STRICTLY GREATER
        than the method body's own column. Pre-phase both are flush at
        column 0: EXPECTED TO FAIL pre-phase (0 > 0 is False).
        """
        pdf_bytes = desc_content_indent_pdf_bytes
        _, method_body_col = _find_page_and_column(
            pdf_bytes, "Inner method body paragraph."
        )
        _, field_list_col = _find_page_and_column(pdf_bytes, "Parameters:")
        assert field_list_col > method_body_col, (
            "FLD-01: expected the field-list line's column "
            f"({field_list_col}) to be strictly greater than the method "
            f"body's own column ({method_body_col})."
        )

    def test_d11_sig09_page_boundary_signature_body_and_continuation_indent(
        self, desc_content_indent_pdf_bytes
    ):
        """
        D-11 / SIG-09 (38-EMISSION-CONTRACT.md section 2.5): on the
        page-boundary construct, the signature and the first line of its
        body must be on the SAME compiled page, and the body's
        continuation on a FOLLOWING page must have the SAME leading-space
        column as its first line. Pre-phase: ``block(sticky: true, ...)``
        (Phase 37) already keeps the signature and the first body line
        together, and neither line is indented at all (0 == 0): ALREADY
        TRUE pre-phase -- a non-regression CONTROL (reclassified in
        38-GATE-EVIDENCE-01.md), not a per-requirement RED. It exists to
        be ASSERTED, not assumed (D-11): a wrapper change is exactly what
        could break it.
        """
        pdf_bytes = desc_content_indent_pdf_bytes
        sig_page, _ = _find_page_and_column(pdf_bytes, "class IndPageBoundaryClass")
        first_line_page, first_line_col = _find_page_and_column(
            pdf_bytes, "ind_page_boundary_class_body_first_line_sentinel"
        )
        continuation_page, continuation_col = _find_page_and_column(
            pdf_bytes,
            "ind_page_boundary_class_body_continuation_sentinel",
            start_page=first_line_page,
        )
        assert sig_page == first_line_page, (
            "D-11/SIG-09: expected the signature "
            f"(page {sig_page}) and the first line of its body "
            f"(page {first_line_page}) to be on the SAME page."
        )
        assert continuation_page > first_line_page, (
            "D-11/SIG-09: expected the body's continuation "
            f"(page {continuation_page}) to be on a LATER page than the "
            f"first line (page {first_line_page}) -- the page-boundary "
            "construct did not actually cross a page break."
        )
        assert continuation_col == first_line_col, (
            "D-11/SIG-09: expected the body's continuation column "
            f"({continuation_col}) to equal its first line's own column "
            f"({first_line_col}) -- the indent must survive the page "
            "break."
        )
