"""
Fast, offline regression gate for the glob-image-resolution fix
(Phase 15, GATE-02).

This is the deterministic, network-free reproduction of the thirteenth
fatal that the slow full-corpus gate
(``tests/test_corpus_gate.py::TestCorpusRenderGate``) surfaced against
Sphinx's own ``doc/`` tree (1 live occurrence, 1 file:
``usage/advanced/intl.typ:25``), after bugs #1-#12 unblocked the compile
path:

    TypstError: file not found (searched at <build>/_static/translation.*)

Construct: ``.. figure:: /_static/translation.*`` at
``usage/advanced/intl.rst:12``, emitted as
``image("../../_static/translation.*", width: 100%)`` -- the literal ``.*``
glob was never resolved to the concrete file (``translation.svg`` in the
real corpus) that exists on disk.

Root cause: ``sphinx.builders.Builder.post_process_images()`` (the base
implementation) resolves ``*``-glob image URIs to a concrete file by
consulting ``node["candidates"]`` (populated during Sphinx's read-phase
``ImageCollector`` for every builder) against the builder's own
``supported_image_types`` list, then rewrites ``node["uri"]`` to the
resolved concrete path. ``TypstBuilder.post_process_images()`` overrode this
with a bare ``node.get("uri", "")`` read that never consulted
``candidates`` at all, and the builder declared no ``supported_image_types``
-- so the literal, unresolved glob string flowed through unchanged to both
the translator's ``visit_image`` (emitted into the ``.typ``) and
``copy_image_files()`` (tried to copy a nonexistent literal ``pic.*`` file).

Fix: ``TypstBuilder`` now declares ``supported_image_types`` (Typst's
embeddable formats -- SVG, PNG, GIF, JPEG, in that preference order) and
``post_process_images()`` resolves a glob URI's ``candidates`` dict against
that list, rewriting ``node["uri"]`` to the concrete resolved path so both
the translator and ``copy_image_files()`` see the resolved file. Non-glob
URIs (``candidates["*"]`` already equals the existing ``node["uri"]``) stay
byte-unchanged. Doctrees with no ``candidates`` key at all (hand-built
doctrees in ``tests/test_builder.py`` that bypass Sphinx's
``ImageCollector``) fall back to the original bare-URI tracking, unchanged.

Confirmed both directions: FAILS against the pre-fix builder with the exact
"file not found" fatal on the unresolved ``pic.*`` path, and PASSES with the
fix. Drives the full ``-b typstpdf`` path -- NOT ``-b typst`` -- on purpose:
the fatal only aborts on the ``TypstPDFBuilder.finish()`` compile path, so a
``-b typst`` build would emit the invalid ``.typ`` but never compile it and
thus prove nothing.
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
def glob_image_render_gate_dir():
    """Return the path to the glob_image_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "glob_image_render_gate"


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
    reason="typst-py is required for the glob-image render gate",
)
class TestGlobImageRenderGate:
    """
    Real-compile regression gate proving the ``typstpdf`` builder resolves a
    ``*``-glob image URI to the one concrete candidate file present on disk,
    so ``typst.compile()`` resolves the emitted ``image(...)`` path instead
    of aborting "file not found" on the literal glob string.

    Requirements: GATE-02 (Phase 15 scope expansion -- the fast offline
    reproduction of the corpus glob-image fatal).
    """

    def test_typstpdf_resolves_glob_image_and_produces_pdf(
        self, glob_image_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly (no fatal raised out of the subprocess);
        - the emitted ``.typ`` references the concrete resolved path
          (``pic.png``), not the literal unresolved glob (``pic.*``);
        - the concrete ``_static/pic.png`` asset was copied into the output
          tree (the ``copy_image_files()`` path the fix depends on);
        - no ``TypstCompilationError`` / "file not found" signature is
          logged;
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF``
          magic bytes -- the only proof the glob resolved and
          ``typst.compile()`` did NOT abort with the fatal that GATE-02
          surfaced against the corpus.
        """
        result = _run_sphinx_build_typstpdf(glob_image_render_gate_dir, temp_build_dir)
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # A fatal inside TypstPDFBuilder.finish() is logged (not raised) as an
        # ERROR, so guard against it explicitly rather than trusting
        # returncode alone.
        assert "file not found" not in result.stderr, (
            "typst.compile() reported a missing file -- the glob URI was not "
            f"resolved to a concrete candidate:\nstderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # The emitted image(...) call must reference the CONCRETE resolved
        # path, not the literal, unresolved glob string.
        assert 'image("_static/pic.*")' not in typ_text, (
            "The emitted image(...) call still references the literal "
            f"unresolved glob 'pic.*' instead of the concrete resolved "
            f"file:\n{typ_text}"
        )
        assert 'image("_static/pic.png")' in typ_text, (
            "Expected the emitted image(...) call to reference the concrete "
            f"resolved 'pic.png' path:\n{typ_text}"
        )

        # The concrete resolved asset must have been copied into the output
        # tree -- this is the copy_image_files() behavior the fix depends on
        # now that node["uri"] is rewritten to the resolved path.
        copied_asset = temp_build_dir / "_static" / "pic.png"
        assert copied_asset.exists(), (
            "The resolved _static/pic.png asset was not copied into the "
            "typstpdf output tree -- post_process_images() must rewrite "
            "node['uri'] to the resolved candidate so copy_image_files() has "
            "the right file to copy"
        )

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most "
            f"likely on the unresolved glob image:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
