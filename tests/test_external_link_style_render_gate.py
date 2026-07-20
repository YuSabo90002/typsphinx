"""
Real-compile regression gate for both halves of the FID-13 finding
(Cluster F, external hyperlink fidelity): the default-template link styling
half (D-01/D-02) and the reference/target boundary stray-space half (D-03).

Both halves share ONE fixture (``tests/fixtures/external_link_style_render_gate``)
so a single compile exercises the ``show link:`` rule's external-vs-internal
scoping AND the boundary fix in one pass (21-CONTEXT.md's "shared fixture"
default, RESEARCH.md's D-09/D-10 verification split).

FID-13 styling (D-01/D-02, structural-only per D-10 -- color+underline is not
text-extractable): the translator keeps emitting ``link(...)`` unchanged; the
DEFAULT template ``typsphinx/templates/base.typ`` carries a new
``#show link:`` rule that colors + underlines a link ONLY when ``it.dest`` is
a ``str`` (an external URL) -- an internal cross-reference's dest is a
``label``, so it stays unstyled. Verified structurally: the rule is present
in the rendered ``_template.typ``, and the external reference emits a
``link("http...`` call in ``index.typ``.

FID-13 boundary (D-03, structural + pypdf adjacency per D-09): docutils
generates a ``reference`` node followed by a sibling ``target`` node for
every *named* external hyperlink (```` `text <url>`_ ````). ``visit_target``'s
handling of that sibling wraps the reference in a markup-mode ``[...]`` block
for ``#label(...)`` attachment and previously prepended a leading ``\\n``
before that invisible call. A newline inside Typst MARKUP mode renders as a
visible SPACE, which combined with the genuinely-source-present following
space to produce a stray DOUBLE space before the next word/period -- exactly
reproducing the audit catalogue's "RTD  PDF" (two spaces) observation. Fix:
drop the leading ``\\n`` -- the preceding content is always the closing ``)``
of the ``link(...)`` call, so ``)#label(`` is unambiguous with no separator.

Confirmed both directions this session (real ``sphinx-build -b typstpdf``
compiles, both pre-fix and post-fix): pre-fix, the extracted PDF text reads
``"FIDTHIRTEENSENTINEL external reference  ."`` (two spaces before the
period); post-fix it reads ``"FIDTHIRTEENSENTINEL external reference ."``
(one space).
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
def external_link_style_render_gate_dir():
    """Return the path to the external_link_style_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "external_link_style_render_gate"


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
    reason="typst-py is required for the external-link-style render gate",
)
class TestExternalLinkStyleRenderGate:
    """
    Real-compile regression gate proving the default template distinguishes
    external hyperlinks with color+underline (external URLs only) and leaves
    internal cross-references unstyled.

    Requirements: FID-13, GATE-01.
    """

    def test_typstpdf_show_link_rule_present_and_scoped_to_external(
        self, external_link_style_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm, at the
        SOURCE (``.typ``/template) level (D-10, structural-only -- styling
        is not text-extractable):

        - the build exits cleanly and did not report a compile failure;
        - the rendered ``_template.typ`` (the build's copy of the default
          ``base.typ``) contains a ``show link:`` rule scoped by
          ``type(it.dest) == str`` (D-01/D-02);
        - the emitted ``index.typ`` contains a ``link("http...`` call for
          the external reference (the translator keeps emitting `link(...)`
          unchanged -- D-01);
        - ``index.pdf`` exists, is non-empty, and begins with the ``%PDF``
          magic bytes.
        """
        result = _run_sphinx_build_typstpdf(
            external_link_style_render_gate_dir, temp_build_dir
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

        # D-10: the show link: rule's presence in the rendered template is the
        # structural proof for the (non-text-extractable) styling half.
        template_output = temp_build_dir / "_template.typ"
        assert template_output.exists(), "_template.typ was not emitted"
        template_text = template_output.read_text(encoding="utf-8")
        assert "show link:" in template_text, (
            "Expected a 'show link:' rule in the rendered default template -- "
            f"the FID-13 styling fix is not applied:\n{template_text}"
        )
        assert "type(it.dest) == str" in template_text, (
            "Expected the show link: rule to scope by 'type(it.dest) == str' "
            "(external-URL-only, D-02) -- an unscoped rule would also style "
            f"internal cross-references:\n{template_text}"
        )

        # The translator itself keeps emitting link(...) unchanged (D-01) --
        # the external reference must still produce a plain string-url link.
        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")
        assert 'link("https://example.com/"' in typ_text, (
            'Expected the external reference to emit a link("http..." call '
            f"unchanged by the styling fix:\n{typ_text}"
        )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced:\n" f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the external-link boundary render gate",
)
class TestExternalLinkBoundaryRenderGate:
    """
    Real-compile regression gate proving a named external reference followed
    by a period renders with a single space, not a stray double space
    (FID-13 boundary, D-03).

    Requirements: FID-13, GATE-01.
    """

    def test_typstpdf_boundary_no_leading_newline_before_label(
        self, external_link_style_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm, at the
        SOURCE (``.typ``) level:

        - the build exits cleanly and did not report a compile failure;
        - the reference-with-target markup wrapper attaches its
          ``#label(...)`` call directly after the closing ``)`` of the
          ``link(...)`` call it decorates -- no ``\\n`` sits between them
          (D-03: a leading ``\\n`` there renders as a visible space in
          Typst MARKUP mode, the boundary bug's root cause).
        """
        result = _run_sphinx_build_typstpdf(
            external_link_style_render_gate_dir, temp_build_dir
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

        assert ")\n#label(" not in typ_text, (
            "Found a leading '\\n' between the link(...) call's closing "
            "')' and the following '#label(' -- the FID-13 boundary fix is "
            f"not applied (D-03):\n{typ_text}"
        )
        assert ")#label(" in typ_text, (
            "Expected the reference-with-target wrapper to attach "
            "'#label(...)' directly after the link(...) call's closing "
            f"')' with no separator:\n{typ_text}"
        )

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
    def test_pdf_extracted_text_has_single_space_boundary(
        self, external_link_style_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf``, extract the compiled
        PDF's text with pypdf, and confirm (D-09 required adjacency
        asserts):

        - the single-space form ``"FIDTHIRTEENSENTINEL external reference ."``
          is present (a real, single rendered space before the period);
        - the pre-fix double-space form
          ``"FIDTHIRTEENSENTINEL external reference  ."`` (two spaces) is
          ABSENT;
        - the same-document internal reference (``"Internal Target
          Section."``) is unaffected -- a single space, proving the fix is
          scoped to the reference-with-target wrapper only, not a global
          change to internal-reference rendering.

        This is the real, rendered-glyph-level proof: a structural ``.typ``
        assert alone cannot distinguish a genuinely single space from a
        Typst markup newline collapsing into an extra one, but a rendered
        PDF can (Phase 20's proven adjacency-assert pattern -- confirmed
        this session via a real, temporary pre-fix build: the pre-fix
        extracted text reads
        ``"FIDTHIRTEENSENTINEL external reference  ."`` with two spaces).
        """
        result = _run_sphinx_build_typstpdf(
            external_link_style_render_gate_dir, temp_build_dir
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

        assert "FIDTHIRTEENSENTINEL external reference ." in full_text, (
            "Expected a single rendered space before the period after the "
            f"named external reference -- FID-13 boundary fix regression:\n"
            f"{full_text}"
        )
        assert "FIDTHIRTEENSENTINEL external reference  ." not in full_text, (
            "Found the pre-fix stray DOUBLE space before the period -- the "
            f"FID-13 boundary fix (D-03) is not in effect:\n{full_text}"
        )

        # Internal cross-reference rendering (unstyled, un-fixed) stays
        # unaffected -- a plain single space precedes its trailing period.
        assert "Internal Target Section." in full_text, (
            "Expected the same-document internal reference to render "
            f"unaffected by the boundary fix:\n{full_text}"
        )
