"""
Real-compile regression gate for the IMG-01 converted-image-collision
defect (Phase 50).

The shipping bug (PR #131 review, filed
``.planning/todos/pending/2026-08-10-rehomed-converted-image-collides-with-
srcdir-images-dir.md``): ``TypstBuilder._track_image()`` rehomes a converted
image's ABSOLUTE URI to a ``doctreedir``-relative path
(``"images/<basename>"``) -- the exact same source-root-relative key an
ordinary source image genuinely at ``<srcdir>/images/<basename>`` already
claims. Both tracking sites guard insertion with ``if <key> not in
self.images``, so whichever document is written first silently wins the
key: the loser is never copied, both ``.typ`` files emit the IDENTICAL
``image("images/<basename>")`` call, one document renders a completely
different picture than the one its own source names, and the build
succeeds with **no warning**. This is also a regression in *failure mode*:
the same project used to abort loudly before PR #131 (Issue #130) and now
renders the wrong picture silently.

Per ROADMAP binding constraint #4 (GATE-01's non-fatal amendment) and
CONTEXT.md's D-08, "does not compile" is NOT an available RED for this
defect -- it compiles fine both before and after the fix. The RED this
module records instead (D-08) is an embedded-image assertion read out of
the compiled PDF: pre-fix, the single compiled PDF (Phase 47: only wrapper
files -- ``master.pdf`` here -- ever compile) embeds the SAME picture for
both documents, and only one of the two source image files was ever copied
into the output tree.

This defect's fixture is ``tests/fixtures/converted_image_collision_render_
gate/`` -- a SIBLING of ``tests/fixtures/absolute_image_render_gate/``,
never a mutation of it (D-12 pins that fixture's own assertions unedited).
One master (``index.rst``) toctrees two content documents:
``converted_source.rst`` (whose SVG figure a fake converter post-transform
rehomes to the absolute ``<doctreedir>/images/chart.png``) and
``real_source.rst`` (an ordinary figure genuinely at
``<srcdir>/images/chart.png``). The two PNGs are discriminated by PIXEL
DIMENSIONS -- 40x24 for the real source image, 16x64 for the converted
stand-in -- never by raw bytes, because Typst re-encodes what it embeds
(D-09).

The RED for this defect is recorded, verbatim, in
``.planning/phases/50-pr-131-image-path-defects/50-RED-EVIDENCE.md``, and
plan 50-02 removes the two ``xfail`` markers below once the fix lands.

**Contract binding plan 50-02 (ROADMAP binding constraint #6, no laundered
gates): the ONLY edit permitted to this file downstream is the removal of
the two ``xfail`` decorator lines below.** Every assertion in this module
was derived from D-01/D-02/D-08/D-09/D-10 BEFORE the fix existed; changing
an assertion to make an observed result pass is a laundered gate.
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
def converted_image_collision_render_gate_dir():
    """Return the path to the converted_image_collision_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "converted_image_collision_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run the ``typstpdf`` build as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never a console-script shim)
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


# Held out of the decorators (rather than inlined) so `black` never needs to
# wrap either `@pytest.mark.xfail(...)` line across multiple physical lines
# -- this is what lets plan 50-02 prove, by filtering every line containing
# "xfail" out of both file versions and diffing the remainder, that its edit
# removed exactly these two decorator lines and touched nothing else.
_RED_REASON_STRUCTURAL = (
    "IMG-01 pre-fix RED (D-08, recorded in 50-RED-EVIDENCE.md): "
    "_track_image() has not yet been widened with the D-01/D-03 srcdir- "
    "collision probe, so the rehomed converted image and the real source "
    "image both resolve to the identical images/chart.png key -- the "
    "second document tracked silently loses. Plan 50-02 removes this "
    "marker once the fix lands."
)
_RED_REASON_EMBEDDED = (
    "IMG-01 pre-fix RED (D-08, recorded in 50-RED-EVIDENCE.md): the single "
    "compiled master.pdf embeds only ONE distinct picture for both "
    "documents (the extracted-image size set has one element, not two), "
    "and _typst_converted/ is absent from the pre-fix output tree because "
    "the D-02 reserved-namespace relocation does not exist yet. Plan 50-02 "
    "removes this marker once the fix lands."
)


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the converted-image-collision render gate",
)
class TestConvertedImageCollisionRenderGate:
    """
    Real-compile regression gate for IMG-01: a converted image rehomed to
    ``images/<basename>`` must stop colliding with a real source image of
    the same basename.
    """

    def test_typstpdf_build_succeeds_without_image_warnings(
        self, converted_image_collision_render_gate_dir, temp_build_dir
    ):
        """
        CONTROL (no xfail): records that IMG-01 is non-fatal -- the build
        exits 0, ``master.pdf`` exists, is non-empty and starts with the
        ``%PDF`` magic bytes, and stderr carries neither "are the same
        file" nor "Image file not found". Green both before and after the
        fix -- this is the written proof that "does not compile" was never
        available as a RED for IMG-01.
        """
        result = _run_sphinx_build_typstpdf(
            converted_image_collision_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx build (typstpdf) failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "are the same file" not in result.stderr, (
            "Unexpected same-file copy collision:\n" f"stderr: {result.stderr}"
        )
        assert "Image file not found" not in result.stderr, (
            "Unexpected missing-image error:\n" f"stderr: {result.stderr}"
        )

        pdf_output = temp_build_dir / "master.pdf"
        assert pdf_output.exists(), (
            "master.pdf was not produced:\n" f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

    def test_content_documents_emit_distinct_image_paths(
        self, converted_image_collision_render_gate_dir, temp_build_dir
    ):
        """
        STRUCTURAL RED (D-08): ``real_source.typ`` must reference the
        unchanged ``images/chart.png`` key (D-01: the common, non-
        colliding-target-would-be case is unchanged -- but here a REAL
        collision exists, so the real source image keeps the plain key and
        the converted image is the one relocated), while
        ``converted_source.typ`` must reference the D-02 reserved
        namespace ``_typst_converted/images/chart.png`` instead. The two
        emitted image arguments must differ from each other.
        """
        result = _run_sphinx_build_typstpdf(
            converted_image_collision_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx build (typstpdf) failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        converted_typ = temp_build_dir / "converted_source.typ"
        real_typ = temp_build_dir / "real_source.typ"
        assert converted_typ.exists(), "converted_source.typ was not emitted"
        assert real_typ.exists(), "real_source.typ was not emitted"

        converted_text = converted_typ.read_text(encoding="utf-8")
        real_text = real_typ.read_text(encoding="utf-8")

        assert 'image("images/chart.png")' in real_text, (
            "Expected real_source.typ to keep the unchanged "
            f"images/chart.png key:\n{real_text}"
        )
        assert 'image("_typst_converted/images/chart.png")' in converted_text, (
            "Expected converted_source.typ to reference the D-02 reserved "
            f"namespace after relocation:\n{converted_text}"
        )

        assert 'image("images/chart.png")' not in converted_text, (
            "converted_source.typ must not still reference the "
            f"collided images/chart.png key:\n{converted_text}"
        )

    @pytest.mark.skipif(
        not PYPDF_AVAILABLE,
        reason="pypdf is required for the embedded-image extraction assert",
    )
    def test_pdf_embeds_both_distinctly_sized_images(
        self, converted_image_collision_render_gate_dir, temp_build_dir
    ):
        """
        EMBEDDED-IMAGE RED (D-08/D-09): open ``master.pdf`` with
        ``pypdf.PdfReader`` and build the SET of ``image_file.image.size``
        pairs over every page and every entry of ``page.images`` (never by
        positional index -- pypdf's extraction order follows Typst's own
        PDF XObject enumeration, not doctree order). That set must equal
        ``{(40, 24), (16, 64)}`` -- both distinctly-sized pictures
        genuinely embedded. Also requires
        ``<build>/_typst_converted/images/chart.png`` to exist and
        ``<build>/images/chart.png`` to be byte-identical to the fixture's
        own ``images/chart.png`` -- proof that the REAL source image, not
        the converted stand-in, is the file that ends up at the ordinary
        location.
        """
        result = _run_sphinx_build_typstpdf(
            converted_image_collision_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx build (typstpdf) failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        pdf_output = temp_build_dir / "master.pdf"
        assert pdf_output.exists(), (
            "master.pdf was not produced:\n" f"stderr: {result.stderr}"
        )

        reader = pypdf.PdfReader(str(pdf_output))
        extracted_sizes = {
            image_file.image.size
            for page in reader.pages
            for image_file in page.images
            if image_file.image is not None
        }

        assert extracted_sizes == {(40, 24), (16, 64)}, (
            "Expected both distinctly-sized pictures to be embedded in "
            f"master.pdf; observed sizes: {extracted_sizes}"
        )

        relocated_asset = temp_build_dir / "_typst_converted" / "images" / "chart.png"
        assert relocated_asset.exists(), (
            "Expected the converted stand-in to be copied under the D-02 "
            f"reserved namespace at {relocated_asset}"
        )

        ordinary_asset = temp_build_dir / "images" / "chart.png"
        assert (
            ordinary_asset.exists()
        ), f"Expected the real source image to remain at {ordinary_asset}"
        fixture_real_source = (
            converted_image_collision_render_gate_dir / "images" / "chart.png"
        )
        assert ordinary_asset.read_bytes() == fixture_real_source.read_bytes(), (
            "Expected images/chart.png in the output tree to be the REAL "
            "source image, byte-identical to the fixture's own copy -- "
            "not the converted stand-in"
        )
