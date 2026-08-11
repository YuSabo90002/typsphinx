"""
Phase 39, ADM-05: rubric-inherits-container-indent INVARIANCE GUARD.

This module is an INVARIANCE GUARD per D-12 (39-CONTEXT.md), NOT a GATE-01
RED. 39-CONTEXT.md measured, via a real ``-b typstpdf`` build of a
``py:class::``/``py:method::`` probe read back through ``pypdf``, that
ADM-05 already holds against pre-phase code: Phase 38's
``pad(left: SHARED_INDENT_STEP, {...})`` wrapper around ``desc_content``
already carries the rubric structurally, and ``visit_rubric`` performs no
indent logic of its own. A RED cannot be recorded against pre-phase code
for a property that is already true -- exactly the situation Phase 36's
SC#3 hit and resolved the same way (see ROADMAP.md "Roadmap Evolution",
Phase 36 edit). Every test in this module is therefore GREEN against the
untouched translator, by design, and exists to catch a future regression,
not to prove a fix.

Left-edge measurement technique, binding (copied from
``tests/test_desc_content_indent_render_gate.py``, which established the
technique): pypdf's per-glyph ``visitor_text`` callback returns
``x=0, y=0`` on this project's compiled PDFs and is unusable.
``extraction_mode="layout"`` reconstructs left-edge indentation as leading
whitespace and is the only usable technique.

Every column comparison below is RELATIVE (``==``, ``>`` or the
over-indent catcher's ``<=``) against another MEASURED column, never a
pinned point value or a character-column literal (D-12's own
prohibition; 39-CONTEXT.md's measured point table -- 70.87pt / 98.37pt /
125.87pt -- is evidence that the property holds, not a target to
re-assert here) -- the gate cannot be satisfied, or broken, by re-valuing
``SHARED_INDENT_STEP``.
"""

import io
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
def rubric_indent_invariance_gate_dir():
    """Return the path to the rubric_indent_invariance_gate fixture."""
    return Path(__file__).parent / "fixtures" / "rubric_indent_invariance_gate"


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typst`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``
    and never a bare ``sphinx-build``) -- the NixOS PATH-shadowing hazard
    restated in every render-gate module in this project
    (``tests/test_pdf_render_gate.py``'s own ``_run_sphinx_build_typst``
    is the canonical form this clones).
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
def rubric_indent_invariance_typ_text(
    rubric_indent_invariance_gate_dir, tmp_path_factory
):
    """
    Build the fixture through ``-b typst`` ONCE for the whole session and
    return the emitted ``.typ`` text. No ``typst``/``pypdf`` dependency --
    every purely structural (``.typ``-text-level) test in this module uses
    this fixture, so those tests run even when the optional compiled-PDF
    dependencies are unavailable.
    """
    build_dir = tmp_path_factory.mktemp("rubric_indent_invariance_typ") / "_build"
    result = _run_sphinx_build_typst(rubric_indent_invariance_gate_dir, build_dir)
    assert not result.returncode, (
        f"sphinx-build -b typst failed:\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    index_typ = build_dir / "index.typ"
    assert index_typ.exists(), "index.typ was not generated"
    return index_typ.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def rubric_indent_invariance_pdf_bytes(
    rubric_indent_invariance_gate_dir, tmp_path_factory
):
    """
    Build the fixture through ``-b typst`` and compile it to PDF via a
    REAL ``typst.compile()`` call ONCE for the whole session (no
    try/except -- a compilation failure must propagate and fail loudly).
    Only requested by tests inside the ``TYPST_AVAILABLE``/
    ``PYPDF_AVAILABLE``-skipif-gated class below, so this fixture never
    runs (and never requires the optional dependencies) when that class
    is skipped.

    Phase 47 (R3): a ``typst.compile()`` call targeting a complete,
    self-contained document must target the WRAPPER file, not the
    docname-derived content file -- only the wrapper carries the
    template application (title/page setup). This fixture's own
    ``typst_documents`` entry targets ``master.typ`` (de-collided from
    the pre-Phase-47 ``"index"``, which self-collided with the
    docname-derived content file, ``index.typ``).
    """
    build_dir = tmp_path_factory.mktemp("rubric_indent_invariance_pdf") / "_build"
    result = _run_sphinx_build_typst(rubric_indent_invariance_gate_dir, build_dir)
    assert not result.returncode, (
        f"sphinx-build -b typst failed:\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    wrapper_typ = build_dir / "master.typ"
    assert wrapper_typ.exists(), "master.typ was not generated"
    pdf_path = build_dir / "master.pdf"
    typst.compile(str(wrapper_typ), output=str(pdf_path))
    assert pdf_path.exists(), "PDF file was not created"
    assert pdf_path.stat().st_size, "PDF file is empty"
    return pdf_path.read_bytes()


def _layout_lines(pdf_bytes: bytes, page_index: int) -> str:
    """
    Return the ``extraction_mode="layout"`` text for ONE page, U+200B-
    stripped. Layout-mode reconstructs a monospace-like character grid
    from the PDF's real glyph positions and preserves left-edge
    indentation as leading whitespace -- the per-glyph position API
    (``visitor_text``) reports ``x=0, y=0`` on this project's PDFs and
    cannot be used for this measurement.
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
    Search pages ``start_page..`` onward for ``marker_substring`` and
    return ``(page_index, leading_column)`` for the first page it is found
    on. Page-index-agnostic by design: every column assertion in this
    module locates its marker by CONTENT, not a hard-coded page number. A
    marker renamed in the fixture and not here makes this raise
    ``AssertionError`` rather than silently pass.
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
    ``tests/test_desc_content_indent_render_gate.py``'s ``_slice`` helper
    exactly, so a region-isolation assertion cannot be satisfied by bytes
    belonging to a different construct.
    """
    start_idx = typ_text.index(start_marker)
    if end_marker is None:
        return typ_text[start_idx:]
    end_idx = typ_text.index(end_marker, start_idx + len(start_marker))
    return typ_text[start_idx:end_idx]


# ---------------------------------------------------------------------------
# Structural (.typ-text-level) assertion -- no typst/pypdf skip needed.
# ---------------------------------------------------------------------------


class TestRubricIndentInvarianceStructuralGate:
    """
    The structural half of the guard: the rubric emits NO indent wrapper
    of its own. Requires only ``-b typst`` (no compiled-PDF dependency),
    so it passes even when ``typst``/``pypdf`` are not installed --
    provable by ``pytest tests/test_rubric_indent_invariance.py -k typ``.
    """

    def test_typ_top_level_control_rubric_emits_no_indent_wrapper(
        self, rubric_indent_invariance_typ_text
    ):
        """
        ADM-05 / STATE.md IND-04 bar: the direct statement that a rubric
        consumes its container's shared indent step, it does not redefine
        it. The emitted ``.typ`` region between the end of the second
        top-level paragraph's own emission and the top-level control
        rubric's own wrapper open must contain no invocation of the
        padding function ``visit_desc_content`` opens -- the top-level
        rubric sits outside any description body, so nothing should ever
        wrap it. ALREADY TRUE pre-phase (this is what D-12 asserts): a
        non-regression CONTROL, not a per-requirement RED.
        """
        typ_text = rubric_indent_invariance_typ_text
        second_top_level_paragraph = (
            'text("RIITOPSECOND precedes the top-level control rubric, '
            'outside any description body.")'
        )
        control_rubric_wrapper_open = 'strong({text("RIICTRLRUBRIC")})'
        region = _slice(
            typ_text, second_top_level_paragraph, control_rubric_wrapper_open
        )
        pad_open_prefix = "pad(left: "
        assert pad_open_prefix not in region, (
            "ADM-05/IND-04: expected NO indent-wrapper invocation between "
            "the second top-level paragraph and the top-level control "
            f"rubric's own wrapper open -- found one:\n{region}"
        )


# ---------------------------------------------------------------------------
# Compiled-PDF left-edge assertions -- ADM-05, D-12.
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the ADM-05 left-edge invariance gate",
)
class TestRubricIndentInvariancePdfGate:
    """
    Real-compile left-edge invariance gate for ADM-05, using ``pypdf``'s
    layout-mode text-grid reconstruction, extraction_mode="layout". Every
    column comparison is RELATIVE to another measured column (``==``,
    ``>`` or ``<=``), never a pinned point value -- the gate cannot be
    satisfied by re-valuing ``SHARED_INDENT_STEP``. ALREADY GREEN
    pre-phase throughout this class (D-12): these assertions exist to be
    ASSERTED, not assumed -- a future rubric-indent change is exactly
    what could break them.
    """

    def test_adm05_class_rubric_equals_class_body_column(
        self, rubric_indent_invariance_pdf_bytes
    ):
        """
        The class-level rubric's column EQUALS the class body
        paragraph's column -- the rubric inherits the containing
        description body's own indent, adding none of its own.
        """
        pdf_bytes = rubric_indent_invariance_pdf_bytes
        _, class_body_col = _find_page_and_column(pdf_bytes, "RIICLASSBODY")
        _, class_rubric_col = _find_page_and_column(pdf_bytes, "RIICLASSRUBRIC")
        assert class_rubric_col == class_body_col, (
            "ADM-05: expected the class-level rubric's column "
            f"({class_rubric_col}) to equal the class body paragraph's "
            f"own column ({class_body_col})."
        )

    def test_adm05_method_rubric_equals_method_body_column(
        self, rubric_indent_invariance_pdf_bytes
    ):
        """
        The method-level rubric's column EQUALS the method body
        paragraph's column -- the same inheritance holds one nesting
        level deeper.
        """
        pdf_bytes = rubric_indent_invariance_pdf_bytes
        _, method_body_col = _find_page_and_column(pdf_bytes, "RIIMETHODBODY")
        _, method_rubric_col = _find_page_and_column(pdf_bytes, "RIIMETHODRUBRIC")
        assert method_rubric_col == method_body_col, (
            "ADM-05: expected the method-level rubric's column "
            f"({method_rubric_col}) to equal the method body paragraph's "
            f"own column ({method_body_col})."
        )

    def test_adm05_class_body_deeper_than_top_level_reference(
        self, rubric_indent_invariance_pdf_bytes
    ):
        """
        The class body paragraph's column is STRICTLY GREATER than the
        top-level reference paragraph's column -- the class body really
        is indented past the page margin, so the equalities above are
        not trivially true at column 0.
        """
        pdf_bytes = rubric_indent_invariance_pdf_bytes
        _, top_level_reference_col = _find_page_and_column(pdf_bytes, "RIITOPREF")
        _, class_body_col = _find_page_and_column(pdf_bytes, "RIICLASSBODY")
        assert class_body_col > top_level_reference_col, (
            "ADM-05: expected the class body paragraph's column "
            f"({class_body_col}) to be strictly greater than the "
            f"top-level reference paragraph's column "
            f"({top_level_reference_col})."
        )

    def test_adm05_method_body_deeper_than_class_body(
        self, rubric_indent_invariance_pdf_bytes
    ):
        """
        The method body paragraph's column is STRICTLY GREATER than the
        class body paragraph's column -- the second nesting level really
        is one further step in, so the method-level equality above is
        not trivially true at the same column as the class-level one.
        """
        pdf_bytes = rubric_indent_invariance_pdf_bytes
        _, class_body_col = _find_page_and_column(pdf_bytes, "RIICLASSBODY")
        _, method_body_col = _find_page_and_column(pdf_bytes, "RIIMETHODBODY")
        assert method_body_col > class_body_col, (
            "ADM-05: expected the method body paragraph's column "
            f"({method_body_col}) to be strictly greater than the class "
            f"body paragraph's own column ({class_body_col})."
        )

    def test_adm05_top_level_control_rubric_equals_preceding_paragraph_column(
        self, rubric_indent_invariance_pdf_bytes
    ):
        """
        The top-level control rubric's column EQUALS its preceding
        top-level paragraph's column -- the CONTROL that a rubric with
        no containing description body gets no indent rule of its own.
        An implementation that gave the rubric a private indent would
        fail this pair.
        """
        pdf_bytes = rubric_indent_invariance_pdf_bytes
        _, top_level_second_col = _find_page_and_column(pdf_bytes, "RIITOPSECOND")
        _, control_rubric_col = _find_page_and_column(pdf_bytes, "RIICTRLRUBRIC")
        assert control_rubric_col == top_level_second_col, (
            "ADM-05: expected the top-level control rubric's column "
            f"({control_rubric_col}) to equal its preceding top-level "
            f"paragraph's own column ({top_level_second_col})."
        )

    def test_adm05_neither_rubric_over_indents_its_container(
        self, rubric_indent_invariance_pdf_bytes
    ):
        """
        The over-indent catcher, distinct from the equality assertions
        above: neither the class-level nor the method-level rubric's
        column is GREATER than the column of the description body
        containing it. An implementation that gave the rubric an indent
        rule of its own (over-indenting past its container) would fail
        this as loudly as an under-indenting one fails the equality
        assertions.
        """
        pdf_bytes = rubric_indent_invariance_pdf_bytes
        _, class_body_col = _find_page_and_column(pdf_bytes, "RIICLASSBODY")
        _, class_rubric_col = _find_page_and_column(pdf_bytes, "RIICLASSRUBRIC")
        _, method_body_col = _find_page_and_column(pdf_bytes, "RIIMETHODBODY")
        _, method_rubric_col = _find_page_and_column(pdf_bytes, "RIIMETHODRUBRIC")
        assert class_rubric_col <= class_body_col, (
            "ADM-05 over-indent catcher: expected the class-level "
            f"rubric's column ({class_rubric_col}) to be no greater than "
            f"the class body's own column ({class_body_col})."
        )
        assert method_rubric_col <= method_body_col, (
            "ADM-05 over-indent catcher: expected the method-level "
            f"rubric's column ({method_rubric_col}) to be no greater "
            f"than the method body's own column ({method_body_col})."
        )
