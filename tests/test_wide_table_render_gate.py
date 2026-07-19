"""
Real-compile regression gate for FID-01a (F12 wide-table overflow) -- the
sole high-severity issue in the Phase 17 AUD-01 catalogue.

Root cause (18-RESEARCH.md): ``depart_table`` emitted ``columns: <integer>``,
making every column an all-``auto`` Typst grid track -- ``auto`` tracks size
to their content's natural width without wrapping, so a wide table's cell
text visually collides across column boundaries and the rightmost column
clips off the right page margin.

Critical finding (18-RESEARCH.md "Critical Finding"): converting to
``columns: (Nfr, Mfr, ...)`` from docutils ``colspec['colwidth']`` alone is
NOT sufficient. The audit's actual repro content (``extdev/deprecated``) is
not wrappable prose -- it is ``raw()``-rendered inline-literal Python dotted
paths with no whitespace at all, so Typst's paragraph line-breaker (which
only breaks at whitespace/hyphenation opportunities) still cannot wrap a
single unbroken token wider than its ``fr`` share. The fix requires BOTH:

1. ``fr``-column emission from ``colwidth`` (``depart_table``/``visit_colspec``).
2. A zero-width space (U+200B) injected after every ``.``/``_`` in in-table
   inline-literal content (``visit_literal``, gated on ``self.in_table``) so
   Typst's line-breaker has break opportunities inside otherwise-unbreakable
   dotted/underscored identifiers.

This is a *silent* bug -- no fatal, no warning, ``returncode == 0`` both
before and after the fix -- so the proof below asserts on real
``pypdf``-extracted PDF text (the DESC-02 collision-absence idiom already
used in ``tests/test_pdf_render_gate.py``), never on ``.typ``-string
agreement or bare compile success alone (SC#1).

Requirements: FID-01a, GATE-01 (18-CONTEXT.md D-01/D-02/D-03,
18-RESEARCH.md "Critical Finding" / "Validation Architecture", 18-01-PLAN.md).
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


# Sentinel tokens for the wide_table_render_gate fixture -- distinctive,
# unlikely tokens chosen so their presence/absence in extracted PDF text
# proves the fr-columns + ZWSP fix closed FID-01a's column-collision bug.
# Must match the tokens embedded in wide_table_render_gate/index.rst.
WIDE_TABLE_TARGET_SENTINEL = "WIDETABLETARGETSENTINELQ7X9"
WIDE_TABLE_ALT_SENTINEL = "WIDETABLEALTSENTINELK3M2"
WIDE_TABLE_DEPRECATED_SENTINEL = "8.7"
# The literal suffix following the sentinel in the Target cell's raw()
# content (matches wide_table_render_gate/index.rst) -- the pre-fix
# collision is glued to THIS tail, not directly to the sentinel token.
WIDE_TABLE_TARGET_TAIL = "_long_path"


@pytest.fixture
def wide_table_render_gate_dir():
    """Return the path to the wide_table_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "wide_table_render_gate"


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

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``) so
    the exact interpreter/venv running this test is reused, sidestepping the
    documented NixOS-sandbox PATH-shadowing hazard.
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


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class TestWideTableRenderGate:
    """
    Real-compile acceptance gate for FID-01a: wide-table fr-columns +
    in-table ZWSP break-point injection (18-RESEARCH.md "Critical Finding").

    Requirements: FID-01a, GATE-01 (18-CONTEXT.md D-01/D-02,
    18-RESEARCH.md "Critical Finding" / "Validation Architecture").
    """

    def test_wide_table_pdf_has_no_column_collision(
        self, wide_table_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` (the builder already
        compiles the PDF in ``TypstPDFBuilder.finish()`` -- no redundant
        manual ``typst.compile()`` call here) and confirm, via real
        ``pypdf`` text-extraction:

        - the Target and Alternatives cell sentinels are each present in the
          extracted PDF text;
        - the Target sentinel is NOT concatenated with no separator against
          the adjacent Alternatives cell's sentinel, nor against the
          adjacent Deprecated cell's "8.7" value -- the exact
          cross-column glyph-collision signature the audit catalogued
          (FID-01a/F12). Fails RED on the pre-fix translator (integer
          ``columns:``, no ZWSP); passes GREEN only once BOTH fix halves
          land (18-RESEARCH.md "Critical Finding": fr-columns alone are
          necessary but NOT sufficient).
        """
        result = _run_sphinx_build_typstpdf(wide_table_render_gate_dir, temp_build_dir)
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"
        typ_text = index_typ.read_text(encoding="utf-8")

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced by TypstPDFBuilder.finish() -- "
            f"typst.compile() aborted:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        assert WIDE_TABLE_TARGET_SENTINEL in full_text, (
            f"Expected Target-cell sentinel '{WIDE_TABLE_TARGET_SENTINEL}' "
            "in extracted PDF text -- wide-table content regression"
        )
        assert WIDE_TABLE_ALT_SENTINEL in full_text, (
            f"Expected Alternatives-cell sentinel '{WIDE_TABLE_ALT_SENTINEL}' "
            "in extracted PDF text -- wide-table content regression"
        )

        # The collision-absence proof (the crux of this test, DESC-02
        # idiom): before the fix, the Target cell's LAST rendered token
        # ("_long_path", the tail of its dotted/underscored raw() content --
        # matches wide_table_render_gate/index.rst) is directly adjacent to
        # the Deprecated cell's "8.7" with NO separator in the extracted
        # text -- verified empirically this session (identical shape to
        # 18-RESEARCH.md's "Critical Finding" repro: "..._long_target_path8.0
        # 9.0 sphinx.util...", zero separator at exactly this one cell
        # boundary while the OTHER cell boundaries in the same row keep a
        # space). A sentinel-only concatenation check (TARGET+ALT sentinels,
        # non-adjacent columns 1 and 4) would never reproduce this, so the
        # tail-based boundary check is the one that actually distinguishes
        # broken from fixed.
        target_alt_collision = WIDE_TABLE_TARGET_SENTINEL + WIDE_TABLE_ALT_SENTINEL
        assert target_alt_collision not in full_text, (
            "Target/Alternatives cell content concatenated with no "
            "separator -- FID-01a column-collision regression (fr-columns "
            "and/or ZWSP break-point injection missing or broken)"
        )
        target_deprecated_collision = (
            WIDE_TABLE_TARGET_TAIL + WIDE_TABLE_DEPRECATED_SENTINEL
        )
        assert target_deprecated_collision not in full_text, (
            "Target/Deprecated cell content concatenated with no "
            "separator (expected boundary text "
            f"'{target_deprecated_collision}' to be absent) -- FID-01a "
            "column-collision regression (fr-columns and/or ZWSP "
            f"break-point injection missing or broken):\n{full_text}"
        )

        # Structural sanity check, IN ADDITION to (never INSTEAD of, per
        # SC#1) the extraction-based proof above.
        assert "columns: (" in typ_text and "fr" in typ_text, (
            "Expected an fr-weighted columns: (...) tuple in the emitted "
            f"Typst source -- FID-01a fr-column emission regression:\n{typ_text}"
        )
