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

This module also carries the FID-13 boundary (D-03) tests -- see the second
class below, added alongside the ``visit_target`` one-line fix.
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
