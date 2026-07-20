"""
Real-compile regression gate for the narrow-scope abbr-title suppression fix
(FID-14, Phase 21 Plan 02, GATE-01).

The shipping bug: Sphinx's Python-domain signature renderer wraps the
auto-generated PEP 3102 keyword-only ``*`` and PEP 570 positional-only ``/``
signature separators in a genuine ``docutils.nodes.abbreviation`` node whose
own visible text (``node.astext()``) is exactly the single character ``*``
or ``/``. ``depart_abbreviation`` unconditionally appended the node's
``<abbr>`` hover-title explanation inline for EVERY ``abbreviation`` node,
so every affected signature rendered with the clutter ``"*
(Keyword-only parameters separator (PEP 3102))"`` / ``"/ (Positional-only
parameter separator (PEP 570))"`` inline.

Fix: ``depart_abbreviation`` now narrows its existing ``if explanation:``
guard to ``if explanation and node.astext() not in ("*", "/"):`` -- the
explanation is suppressed ONLY for the two auto-generated separators (whose
own node text is exactly ``"*"``/``"/"``); a genuine ``:abbr:`` role's
acronym text is never bare ``"*"``/``"/"``, so it keeps its inline
expansion unchanged (D-Disc-3, narrow scope).

Confirmed against the pre-fix translator this session: ``index.typ``
contained ``text(" (Positional-only parameter separator (PEP 570))")`` and
``text(" (Keyword-only parameters separator (PEP 3102))")`` inline in the
signature's parameter-list concat, and the extracted PDF text read
``"abbrpepsepfunc(pos_only, / (Positional-only parameter separator (PEP
570)), both, * (Keyword-only parameters separator (PEP 3102)), kw_only)"``
-- both fail the asserts below pre-fix. The genuine ``:abbr:`` usage in the
same fixture (``ABBRSENTINELACRONYM (ABBRSENTINELEXPANSIONPHRASE)``) already
passes pre-fix and must continue to pass post-fix (D-Disc-3 regression
guard).

Verification is Shape-B (structural + pypdf, D-10): a structural ``.typ``
assert plus a pypdf extracted-text adjacency assert, since FID-14's fix IS
text-extractable (unlike FID-11's non-extractable vertical-layout property).
"""

import subprocess
import sys
from pathlib import Path

import pytest

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


@pytest.fixture
def abbr_pep_separator_render_gate_dir():
    """Return the path to the abbr_pep_separator_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "abbr_pep_separator_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typstpdf`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``)
    so the exact interpreter/venv running this test is reused, sidestepping
    the documented NixOS-sandbox PATH-shadowing hazard.
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


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the abbr-pep-separator render gate",
)
class TestAbbrPepSeparatorRenderGate:
    """
    Real-compile regression gate proving the PEP 3102 ``*`` / PEP 570 ``/``
    signature separators no longer inject their ``<abbr>`` hover-title text
    inline, while a genuine ``:abbr:`` role usage in the same document keeps
    its inline expansion unchanged.

    Requirements: FID-14, GATE-01.
    """

    def test_typstpdf_abbr_pep_separator_produces_pdf_with_structural_suppression(
        self, abbr_pep_separator_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm, at the
        SOURCE (``.typ``) level:

        - the build exits cleanly and did not report a compile failure;
        - the signature's parameter-list concat does NOT append the
          PEP-separator hover-title explanation text for the ``*``/``/``
          cases;
        - the genuine ``:abbr:`` usage DOES still append its expansion
          text -- ``text(" (ABBRSENTINELEXPANSIONPHRASE)")`` is present;
        - ``index.pdf`` exists, is non-empty, and begins with the ``%PDF``
          magic bytes (real ``typst.compile()`` succeeded).
        """
        result = _run_sphinx_build_typstpdf(
            abbr_pep_separator_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # Structural: the PEP-separator hover-title text must not be
        # appended anywhere in the emitted .typ for the *"/"/ cases.
        assert "Keyword-only parameters separator" not in typ_text, (
            "Found the PEP 3102 '*' separator's hover-title text in the "
            f"emitted .typ -- the FID-14 fix is not applied:\n{typ_text}"
        )
        assert "Positional-only parameter separator" not in typ_text, (
            "Found the PEP 570 '/' separator's hover-title text in the "
            f"emitted .typ -- the FID-14 fix is not applied:\n{typ_text}"
        )

        # Regression: the genuine :abbr: usage in the SAME fixture must
        # still append its expansion (D-Disc-3's narrow-scope requirement).
        assert 'text(" (ABBRSENTINELEXPANSIONPHRASE)")' in typ_text, (
            "Expected the genuine :abbr: role's expansion to still be "
            "appended inline -- the FID-14 fix must not suppress a real "
            f":abbr: usage:\n{typ_text}"
        )

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced:\n" f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

    @pytest.mark.skipif(
        not PYPDF_AVAILABLE,
        reason="pypdf is required for the extracted-text adjacency assert",
    )
    def test_pdf_extracted_text_suppresses_pep_separator_titles_only(
        self, abbr_pep_separator_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf``, extract the compiled
        PDF's text with pypdf, and confirm (D-10 required adjacency
        assert):

        - ``"(Keyword-only parameters separator"`` is ABSENT from the
          extracted signature text;
        - ``"(Positional-only parameter separator"`` is ABSENT from the
          extracted signature text;
        - the plain ``/`` and ``*`` separator characters are still present
          in the signature (suppression removes only the appended
          explanation segment, not the separator itself);
        - the genuine ``:abbr:`` expansion sentinel phrase IS present.
        """
        result = _run_sphinx_build_typstpdf(
            abbr_pep_separator_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced:\n" f"stderr: {result.stderr}"
        )

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        assert "(Keyword-only parameters separator" not in full_text, (
            "Found the PEP 3102 '*' separator's hover-title text in the "
            f"extracted PDF text -- the FID-14 fix is not in effect:\n"
            f"{full_text}"
        )
        assert "(Positional-only parameter separator" not in full_text, (
            "Found the PEP 570 '/' separator's hover-title text in the "
            f"extracted PDF text -- the FID-14 fix is not in effect:\n"
            f"{full_text}"
        )

        # The separator characters themselves must remain in the signature.
        assert "abbrpepsepfunc(pos_only, /" in full_text, (
            "Expected the '/' positional-only separator to remain in the "
            f"rendered signature:\n{full_text}"
        )
        assert ", both, *" in full_text, (
            "Expected the '*' keyword-only separator to remain in the "
            f"rendered signature:\n{full_text}"
        )

        # The genuine :abbr: usage must keep its inline expansion.
        assert (
            "ABBRSENTINELACRONYM (ABBRSENTINELEXPANSIONPHRASE)" in full_text
        ), (
            "Expected the genuine :abbr: role's inline expansion to remain "
            f"present -- the FID-14 fix must not suppress it:\n{full_text}"
        )
