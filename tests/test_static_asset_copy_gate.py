"""
Fast, offline regression gate for the typstpdf static-asset-copy fix
(Phase 15, GATE-02).

This is the deterministic, network-free reproduction of the fatal that the
slow full-corpus gate (``tests/test_corpus_gate.py::TestCorpusRenderGate``)
surfaced against Sphinx's own ``doc/`` tree:

    TypstError: file not found (searched at <build>/_static/python-logo.png)

Root cause: ``TypstPDFBuilder.write_doc()`` overrode the base
``TypstBuilder.write_doc()`` but omitted its ``self.post_process_images(doctree)``
call. So during a ``typstpdf`` build ``self.images`` was never populated,
``copy_image_files()`` early-returned on the empty dict, and any
``_static/``-referenced figure image was never copied into the output tree --
so ``typst.compile()`` inside ``TypstPDFBuilder.finish()`` aborted with
"file not found". The same build path under the ``typst`` builder always
worked (its ``write_doc`` DID call ``post_process_images``), which is exactly
why a ``-b typst`` gate could never have caught this -- this gate therefore
drives the full ``-b typstpdf`` path end-to-end:

    sphinx-build -b typstpdf  ->  typst.compile() (inside finish())  ->  %PDF

and asserts BOTH that the referenced ``_static/`` asset lands in the output
tree AND that a real, non-empty ``%PDF`` was produced with no fatal
``TypstCompilationError``.
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
def static_asset_copy_render_gate_dir():
    """Return the path to the static_asset_copy_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "static_asset_copy_render_gate"


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
    documented NixOS-sandbox PATH-shadowing hazard (see
    ``tests/test_pdf_render_gate.py::_run_sphinx_build_typst``). The builder is
    ``typstpdf`` -- NOT ``typst`` -- on purpose: the missing-asset fatal only
    exists on the ``TypstPDFBuilder.finish()`` compile path, so a ``-b typst``
    build would pass even against the unfixed code and prove nothing.
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
    reason="typst-py is required for the static-asset-copy render gate",
)
class TestStaticAssetCopyRenderGate:
    """
    Real-compile regression gate proving the ``typstpdf`` builder copies a
    ``_static/``-referenced figure image into the Typst output tree before
    compiling, so ``typst.compile()`` resolves the emitted
    ``image("_static/...")`` path instead of aborting "file not found".

    Requirements: GATE-02 (Phase 15 scope expansion -- the fast offline
    reproduction of the corpus fatal).
    """

    def test_typstpdf_copies_static_asset_and_produces_pdf(
        self, static_asset_copy_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly (no fatal raised out of the subprocess);
        - the ``_static/python-logo.png`` asset was copied into the output
          tree (the copy_image_files() path the fix restores);
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF``
          magic bytes -- the only proof the emitted ``image("_static/...")``
          path resolved and ``typst.compile()`` did NOT abort with the
          "file not found" fatal that GATE-02 surfaced against the corpus.
        """
        result = _run_sphinx_build_typstpdf(
            static_asset_copy_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # The build must NOT have logged a Typst compilation failure -- a fatal
        # inside TypstPDFBuilder.finish() is logged (not raised) as an ERROR,
        # so guard against it explicitly rather than trusting returncode alone.
        assert "file not found" not in result.stderr, (
            "typst.compile() reported a missing file -- the _static asset was "
            f"not copied into the output tree:\nstderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        # The referenced _static asset must have been copied into the output
        # tree -- this is the copy_image_files() behavior the fix restores for
        # the typstpdf builder.
        copied_asset = temp_build_dir / "_static" / "python-logo.png"
        assert copied_asset.exists(), (
            "The _static/python-logo.png asset was not copied into the typstpdf "
            "output tree -- TypstPDFBuilder.write_doc() must call "
            "post_process_images() so copy_image_files() has something to copy"
        )

        # The emitted .typ referencing image("_static/python-logo.png") must
        # have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most "
            f"likely on the missing _static asset:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
