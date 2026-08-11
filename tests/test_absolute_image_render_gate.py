"""
Fast, offline regression gate for the absolute-image-URI fix (Issue #130).

Reproduces the bug reported against a real-world project using an image
conversion extension (``sphinxcontrib.rsvgconverter`` / ``.inkscapeconverter``
/ ``sphinx.ext.imgconverter``) or Sphinx's own remote-image downloader. When
an image needs conversion or download, Sphinx's
``sphinx.transforms.post_transforms.images.ImageConverter`` /
``ImageDownloader`` post-transforms rewrite ``node["uri"]`` to an ABSOLUTE
filesystem path under ``<doctreedir>/images/...`` -- unlike ordinary images,
which stay source-root-relative (e.g. ``images/logo.png``).

Root cause: two places in this codebase assumed every tracked image URI was
source-root-relative:

- ``TypstBuilder.post_process_images()`` unconditionally stored
  ``self.images[resolved_uri] = ""``, regardless of whether ``resolved_uri``
  was absolute.
- ``TypstBuilder.copy_image_files()`` computed
  ``src = path.join(self.srcdir, imguri)`` and
  ``dest = path.join(self.outdir, imguri)``. Per ``os.path.join`` semantics,
  once ``imguri`` is absolute the first argument is discarded, so both
  ``src`` and ``dest`` collapsed to the SAME absolute path:

      WARNING: Failed to copy image ...: '<path>' and '<path>' are the same
      file

  and ``TypstTranslator._compute_relative_image_path()`` (fed the same raw
  absolute ``node["uri"]``) prepended a bogus ``../..`` depth prefix,
  producing a garbled path that made ``typst.compile()`` abort with
  "file not found".

Fix: ``post_process_images()`` now rehomes an absolute resolved URI to a
``doctreedir``-relative path (mirroring the source-root-relative convention
ordinary images use) and tracks the TRUE absolute source location as the
``self.images`` dict value; ``copy_image_files()`` uses that value as an
override copy source when present.

This fixture cannot depend on an external SVG converter binary
(``rsvg-convert`` / ImageMagick) being installed wherever this suite runs, so
``tests/fixtures/absolute_image_render_gate/conf.py`` registers a small
custom post-transform that reproduces the *exact* doctree-state mechanism
Sphinx's real image converters use (rewriting ``node["uri"]`` to an absolute
path under ``<doctreedir>/images/``), without requiring one.

Confirmed both directions: FAILS against the pre-fix builder with the exact
"are the same file" warning and a garbled/"file not found" Typst compile
fatal, and PASSES with the fix. Drives the full ``-b typstpdf`` path -- NOT
``-b typst`` -- on purpose: the fatal only aborts on the
``TypstPDFBuilder.finish()`` compile path.
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
def absolute_image_render_gate_dir():
    """Return the path to the absolute_image_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "absolute_image_render_gate"


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
    reason="typst-py is required for the absolute-image render gate",
)
class TestAbsoluteImageRenderGate:
    """
    Real-compile regression gate proving the ``typstpdf`` builder correctly
    copies and references an image whose ``uri`` was rewritten to an
    ABSOLUTE path by an image-conversion post-transform, instead of
    colliding ``src``/``dest`` into the same path and aborting the Typst
    compile with a garbled, unresolved path (Issue #130).
    """

    def test_typstpdf_handles_absolute_image_uri_and_produces_pdf(
        self, absolute_image_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly (no fatal raised out of the subprocess);
        - no "are the same file" copy warning is logged;
        - the emitted ``.typ`` references a clean, doctreedir-relative
          ``image("images/diagram.png")`` path -- not a garbled
          ``../..///...`` absolute-path leak;
        - the converted asset was actually copied into the output tree at
          that relative location;
        - no "file not found" fatal is logged by ``typst.compile()``;
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF``
          magic bytes.
        """
        result = _run_sphinx_build_typstpdf(
            absolute_image_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        assert "are the same file" not in result.stderr, (
            "copy_image_files() logged a same-file collision -- the "
            f"absolute image URI was not rehomed before copying:\n"
            f"stderr: {result.stderr}"
        )

        # A fatal inside TypstPDFBuilder.finish() is logged (not raised) as
        # an ERROR, so guard against it explicitly rather than trusting
        # returncode alone.
        assert "file not found" not in result.stderr, (
            "typst.compile() reported a missing file -- the absolute image "
            f"URI was not resolved to a valid relative path:\nstderr: "
            f"{result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        assert "../.." not in typ_text, (
            "The emitted image(...) call still contains a bogus '../..' "
            f"depth prefix prepended onto an already-absolute path:\n"
            f"{typ_text}"
        )
        assert 'image("images/diagram.png")' in typ_text, (
            "Expected the emitted image(...) call to reference the "
            f"rehomed, doctreedir-relative 'images/diagram.png' path:\n"
            f"{typ_text}"
        )

        # The converted asset must have been copied into the output tree at
        # the rehomed relative location -- this is the copy_image_files()
        # override-source behavior the fix depends on.
        copied_asset = temp_build_dir / "images" / "diagram.png"
        assert copied_asset.exists(), (
            "The converted images/diagram.png asset was not copied into "
            "the typstpdf output tree -- copy_image_files() must use the "
            "tracked absolute override source, not path.join(srcdir, uri)"
        )

        # The emitted .typ must have compiled to a real, non-empty PDF.
        # Phase 47 (R4): the PDF is the WRAPPER's own output ("master.pdf",
        # this fixture's typst_documents target after de-collision) --
        # only wrappers compile to PDF.
        pdf_output = temp_build_dir / "master.pdf"
        assert pdf_output.exists(), (
            "master.pdf was not produced -- typst.compile() aborted, most "
            f"likely on the absolute/garbled image path:\nstderr: "
            f"{result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
