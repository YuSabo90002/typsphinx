"""
Multi-signature page-count acceptance gate for T-37-08 compounding detector.

The `desc_signature` wrapper's vertical spacing can compound across a document
if the spacing is set incorrectly. This gate proves that when the wrapper uses
Typst's own default block spacing (measured at 13.2pt, byte-identical to plain
paragraph flow), a multi-signature document (13 wrappers, the full Phase-37 SIG-
series test corpus) compiles to exactly 4 pages at A4 geometry, with no evidence
of spacing-induced page inflation.

This is the "compounding detector the register named and the suite lacks"
(37-SECURITY.md, "What would close T-37-08"). The existing single-signature
gate `test_signature_page_boundary_render_gate.py` cannot measure compounding;
this gate fills that gap by asserting multi-signature page count against a
hand-derived baseline.

Measurement method: build `signature_typography_gate` fixture through
`sphinx-build -b typst`, compile to PDF via `typst.compile()`, extract page
count via `pypdf.PdfReader`, and assert it equals the measured baseline. A
degenerate-pass guard asserts the fixture contains the expected number of
signature wrappers (13), so a silent fixture change cannot cause the test to
pass falsely.

Baseline derivation (2026-08-01, measured in this worktree):
  - Build: `uv run sphinx-build -b typst tests/fixtures/signature_typography_gate /tmp/sig_typography_build`
  - Compile: `uv run python3 -c "import typst; typst.compile(..., output='index.pdf')"`
  - Count pages: `pypdf.PdfReader().pages` → 4 pages
  - Count wrappers: `index.typ.count('block(sticky: true, par(hanging-indent:')` → 13 wrappers

Measured sensitivity — what this gate does and does NOT catch. The figures
below are a real sweep (2026-08-01): the emitted `.typ` above was rebuilt once,
its 13 wrapper-open strings substituted, and each variant recompiled and
page-counted. They are measurements, not estimates.

    shipped (defaults) -> 4    0pt   -> 4    0.5em -> 4    1.0em -> 4
    1.5em -> 4    2.0em -> 4    2.1em -> 4    2.2em -> 4
    2.3em -> 5    2.5em -> 5    3.0em -> 5    4em -> 5    6em -> 6

  - CAUGHT: symmetric inflation at or above **2.3em** per side (the 4->5
    crossover sits between 2.2em and 2.3em). That is the compounding direction
    this gate exists for, and it measures it across 13 real signatures — which
    `signature_page_boundary_render_gate` structurally cannot do, its fixture
    holding exactly one signature. For scale, the guard that threat T-37-08
    originally named fires only at >=16em after its 6->7 re-pin (37-SECURITY.md),
    so this gate is roughly 7x tighter.
  - NOT caught: the collapse direction. `block(above: 0pt, below: 0pt, ...)` —
    the Wave-3 form that made every signature's glyphs overlap its own body
    (37-SPACING-FINDING.md) — still renders 4 pages here, so page count cannot
    see it. That direction is pinned elsewhere, and automatically: the Phase 34
    MATH-02 golden `tests/fixtures/inline_math_pdf_text_mitex.golden.txt:19`
    keeps `math_inline_default` on its own extracted-text line, which re-merges
    with the preceding line the moment the overlap returns. The exact wrapper
    string is additionally pinned byte-for-byte by
    `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` and
    `tests/test_translator.py::test_desc_signature_rendering`, so any
    reintroduction of `above:`/`below:` from inside this repo breaks those first.
  - The residual exposure this gate is aimed at is therefore an *upstream*
    change — a `typst-py` bump altering Typst's default block spacing, which the
    repo re-resolves weekly via `drift.yml` — where no in-repo string pin fires.

Per 37-SECURITY.md: "add a committed multi-signature page-count assertion at
real geometry — the `signature_typography_gate` fixture (13 wrappers, measured
at 4 A4 pages) — which is the compounding detector the register named and the
suite lacks."
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

# Expected page count for signature_typography_gate fixture at A4 geometry
# (2.5cm margins, 11pt body text, no forced page-height override).
# Measured 2026-08-01 against real build + compile + pypdf extraction.
#
# Re-measured 2026-08-01 at Phase 38 close (38-08-PLAN.md Task 1), against
# the post-Phase-38 translator (this worktree's base commit, 7ae016d,
# already contains 38-05/38-06/38-07's landed changes). This fixture's 13
# signature wrappers include several with real bodies AND field lists
# (Python-domain autodoc-style directives), so BOTH of Phase 38's
# page-count-moving mechanisms have bytes to act on here, pulling in
# opposite directions: the body-less/single-value field-body reflow
# shortens the document, while moving field-list parameter names/types
# from proportional to monospace (FLD-03) widens those lines. Real
# `sphinx-build -b typstpdf` + `pypdf.PdfReader`:
#
#     $ uv run python <rebuild+compile+len(reader.pages) script, see
#       38-GATE-EVIDENCE.md Bucket D for the exact command run>
#     PAGE COUNT (multi-signature fixture): 4
#     WRAPPER COUNT: 13
#
# UNCHANGED at 4. Dominant reason: this fixture's page budget (4 pages at
# real A4 geometry) has enough slack that neither the shortening nor the
# widening effect crosses a page boundary -- the module docstring's own
# sensitivity sweep above shows the fixture only crosses to 5 pages at a
# per-signature inflation of >=2.3em, an order of magnitude larger than
# either of this phase's effects. This is a MEASUREMENT taken against the
# real post-phase build, never a hand-derived or regenerated expected
# string (milestone invariant #4).
EXPECTED_PAGE_COUNT = 4

# Expected number of desc_signature wrappers in the fixture.
# Counted by the pattern "block(sticky: true, par(hanging-indent:"
# in the emitted .typ file. This is the degenerate-pass guard:
# if the fixture changes, the wrapper count changes, and the test
# fails for the right reason (fixture changed), not silently passes
# with a different fixture.
EXPECTED_WRAPPER_COUNT = 13


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run `sphinx-build -b typst` as a subprocess via `sys.executable -m sphinx`.
    Returns the completed process.

    See tests/test_signature_page_boundary_render_gate.py's `_run_sphinx_build_typst`
    for the NixOS-sandbox PATH rationale this mirrors.
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


@pytest.mark.skipif(not TYPST_AVAILABLE, reason="typst module not available")
@pytest.mark.skipif(not PYPDF_AVAILABLE, reason="pypdf module not available")
class TestSignatureTypographyMultiSignaturePageCountGate:
    """Multi-signature page-count compounding detector gate (T-37-08)."""

    def test_multi_signature_document_page_count_at_real_geometry(self, tmp_path):
        """
        Signature wrapper spacing does not compound across a 13-signature
        multi-signature document when compiled at real A4 geometry.

        Assertion: page count == 4 (measured 2026-08-01).
        Degenerate-pass guard: wrapper count == 13 (cannot pass silently on
        a changed fixture).
        """
        # Build the fixture through sphinx-build -b typst
        fixture_dir = Path(__file__).parent / "fixtures" / "signature_typography_gate"
        build_dir = tmp_path / "build"

        result = _run_sphinx_build_typst(fixture_dir, build_dir)
        assert result.returncode == 0, f"Sphinx build failed:\n{result.stderr}"

        # Compile the emitted .typ to PDF
        typ_file = build_dir / "index.typ"
        assert typ_file.exists(), "Emitted index.typ not found"

        pdf_file = build_dir / "index.pdf"
        try:
            typst.compile(str(typ_file), output=str(pdf_file))
        except Exception as exc:
            pytest.fail(f"typst.compile failed: {exc}")

        assert pdf_file.exists(), "Compiled PDF not created"

        # Extract page count
        reader = pypdf.PdfReader(str(pdf_file))
        page_count = len(reader.pages)

        # Degenerate-pass guard: verify the fixture contains the expected
        # number of signature wrappers. If this fails, the fixture changed,
        # and the page count assertion is testing the wrong document.
        typ_content = typ_file.read_text()
        wrapper_pattern = "block(sticky: true, par(hanging-indent:"
        actual_wrapper_count = typ_content.count(wrapper_pattern)

        assert (
            actual_wrapper_count == EXPECTED_WRAPPER_COUNT
        ), f"Fixture wrapper count changed: expected {EXPECTED_WRAPPER_COUNT}, got {actual_wrapper_count}. Fixture may have changed."

        # Main assertion: page count must equal the hand-derived baseline.
        # If wrapper spacing inflates, this will fail with a higher page count.
        assert (
            page_count == EXPECTED_PAGE_COUNT
        ), f"Multi-signature page count mismatch (T-37-08 compounding detector): expected {EXPECTED_PAGE_COUNT}, got {page_count}"
