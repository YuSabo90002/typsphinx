"""
Fast, offline regression gate for the field-list colon-space + inter-field
boundary fix (Phase 20 Plan 02, FID-09).

Deterministic, network-free reproduction of the audit catalogue's literal
``the_answer`` repro (``17-AUDIT-CATALOGUE.md`` finding #5), the fifth of
the six systemic clusters cataloged in the v0.6.1 rendering-fidelity audit:

    the_answer Type:int (a number)Default:42

(no space after either colon; the two fields merge with no boundary at
all -- contrast the ``-b text`` authority, which renders each field on its
own line as a definition list: "Type:" / "int (a number)" / "Default:" /
"42").

Root cause: ``depart_field_name`` appended a bare colon
(``text(":")``) with no trailing space, and ``depart_field`` was a no-op
with no inter-field separator -- so sibling ``:type:``/``:default:``
fields concatenated in the code-mode content block with zero space
anywhere: the colon glued to the value, and the value glued to the next
field's ``strong(``.

Fix: ``depart_field_name`` now appends the colon-space form
(``text(": ")``) -- a real content-value space inside the ``+``-joined
``strong(...)`` expression. ``depart_field`` now emits a sibling-guarded
``text("  ")`` two-space separator (mirroring ``depart_desc_parameter``'s
``node.next_node(descend=False, siblings=True)`` "am I the last sibling"
idiom), wrapped in BOTH a leading AND a trailing newline so the two-space
statement never juxtaposes with the neighboring ``strong(...)`` on one
physical source line.

Uses the audit's own literal minimal-repro source (the docutils
"directive option list" no-blank-line form), which is also empirically
used by 100% of the real Sphinx v9.1.0 corpus (0 of 219 confvals in
``usage/configuration.rst`` use a blank line before their fields).

Confirmed both directions this session: FAILS against the pre-fix
translator (the structural ``.typ`` asserts below do not match the
no-space-colon / no-separator output, and the pypdf extracted text reads
"the_answer Type: int (a number)Default: 42" -- no double-space boundary,
which mismatches the SC#3 pinned target), and PASSES with the fix. Drives
the full ``-b typstpdf`` path -- NOT ``-b typst`` -- for the required real
``typst.compile()`` proof and pypdf extracted-text adjacency assert
(D-07).
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

# The exact ROADMAP Phase 20 SC#3 pinned string: a single space after each
# colon, and a DELIBERATE double space between sibling fields (D-01/D-02).
PINNED_SC3_STRING = "Type: int (a number)  Default: 42"


@pytest.fixture
def confval_field_spacing_render_gate_dir():
    """Return the path to the confval_field_spacing_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "confval_field_spacing_render_gate"


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


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the confval field-spacing render gate",
)
class TestConfvalFieldSpacingRenderGate:
    """
    Real-compile regression gate proving a confval's ``:type:``/``:default:``
    fields restore the colon-space and the inter-field double-space
    boundary (FID-09), matching the exact ROADMAP Phase 20 SC#3 pinned
    string byte-for-byte.

    Requirements: FID-09.
    """

    def test_typstpdf_confval_field_spacing_produces_pdf(
        self, confval_field_spacing_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly (no fatal raised out of the subprocess);
        - the emitted ``index.typ`` contains the colon-space field-name
          form (``strong(text("Type") + text(": "))``);
        - the emitted ``index.typ`` contains the inter-field double-space
          boundary, with the required surrounding newlines
          (``text("  ")\\nstrong(text("Default")``);
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF``
          magic bytes -- proof the fixture compiled to valid Typst.
        """
        result = _run_sphinx_build_typstpdf(
            confval_field_spacing_render_gate_dir, temp_build_dir
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

        # Structural (positive): the colon-space field-name form.
        assert 'strong(text("Type") + text(": "))' in typ_text, (
            "Expected depart_field_name to emit the colon-space form "
            f'\'strong(text("Type") + text(": "))\':\n{typ_text}'
        )

        # Structural (positive): the inter-field double-space boundary,
        # with the required leading+trailing newlines so the two-space
        # text() never juxtaposes with the following strong(...) on one
        # physical source line (Pitfall 4).
        assert 'text("  ")\nstrong(text("Default")' in typ_text, (
            "Expected depart_field to emit the sibling-guarded inter-field "
            "double-space separator immediately before the 'Default' "
            f"field, newline-separated from strong(:\n{typ_text}"
        )

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted:\n"
            f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

    @pytest.mark.skipif(
        not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
        reason=(
            "typst-py and pypdf are both required for the confval "
            "field-spacing pypdf adjacency gate"
        ),
    )
    def test_pdf_extracted_text_matches_pinned_sc3_string(
        self, confval_field_spacing_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture and confirm the pypdf-extracted text contains the
        exact ROADMAP Phase 20 SC#3 pinned string
        ``"Type: int (a number)  Default: 42"`` byte-for-byte (D-07): a
        single space after each colon, and a double space between the two
        sibling fields.
        """
        result = _run_sphinx_build_typstpdf(
            confval_field_spacing_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted:\n"
            f"stderr: {result.stderr}"
        )

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        assert PINNED_SC3_STRING in full_text, (
            f"Expected the exact pinned SC#3 string {PINNED_SC3_STRING!r} "
            f"in the extracted PDF text -- FID-09 colon-space / "
            f"inter-field boundary regression:\n{full_text!r}"
        )
