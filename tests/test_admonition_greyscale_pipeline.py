"""
Smoke test for ADM-04's greyscale render-and-desaturate PIPELINE
(``scripts/render_admonition_greyscale.py``).

This module proves the PIPELINE works end to end -- a single-page probe
compiles to PNG through ``typst.compile()`` and desaturates through Pillow,
producing a real single-channel image file. It does NOT prove ADM-04
itself: it is run against whatever the translator currently emits (the
pre-fix bucket routing), and the actual ADM-04 sign-off artifact must be
rendered from POST-fix code (after plan 39-05/39-06's bucket-routing
changes land) by plan 39-07, which owns the committed PNG and the owner's
visual UAT.

Both tests below run unguarded by any class-level skip, only per-test
``skipif`` on ``PILLOW_AVAILABLE``/``TYPST_AVAILABLE`` (the repo's
``try``/``except ImportError`` convention, see
``tests/test_desc_rubric_decoupling_render_gate.py``) -- a class-level skip
would let both pass silently by never running.
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
    from PIL import Image

    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "render_admonition_greyscale.py"
)
PROBE_DIR = Path(__file__).parent / "fixtures" / "admonition_greyscale_probe"


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typst`` as a subprocess and return the completed
    process. Invoked as ``sys.executable -m sphinx`` -- never a bare
    ``sphinx-build`` and never through ``uv run`` -- matching this repo's
    convention (see ``tests/test_desc_rubric_decoupling_render_gate.py``).
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


@pytest.mark.skipif(
    not (PILLOW_AVAILABLE and TYPST_AVAILABLE),
    reason="Pillow and typst-py are both required for the greyscale pipeline",
)
def test_pipeline_produces_single_channel_png(tmp_path):
    """
    Drives ``scripts/render_admonition_greyscale.py`` through ``sys.
    executable`` as a subprocess against the probe fixture, exactly as a
    real invocation would be run. Asserts the subprocess exits 0, the
    output PNG exists and is non-empty, and opening it with Pillow yields
    the single-channel greyscale mode with non-zero dimensions.
    """
    out_png = tmp_path / "probe_greyscale.png"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), str(PROBE_DIR), str(out_png)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"render_admonition_greyscale.py failed:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    assert out_png.exists(), f"{out_png} was not created"
    assert out_png.stat().st_size > 0, f"{out_png} is empty"

    image = Image.open(out_png)
    assert (
        image.mode == "L"
    ), f"expected single-channel greyscale mode 'L', got {image.mode!r}"
    width, height = image.size
    assert width > 0, "output PNG has zero width"
    assert height > 0, "output PNG has zero height"


@pytest.mark.skipif(
    not TYPST_AVAILABLE, reason="typst-py is required to compile the probe"
)
def test_probe_compiles_to_exactly_one_page(tmp_path):
    """
    Asserts the probe fixture compiles to exactly one page -- the property
    ``render_admonition_greyscale`` itself checks (Pitfall 4,
    39-RESEARCH.md: ``typst.compile(..., format="png")`` returns a single
    ``bytes`` object only for a one-page document). This is the assertion
    that keeps Pitfall 4 from becoming a silent surprise in plan 39-07: if
    a future edit to the probe fixture pushes it past one page, this test
    fails here rather than the render pipeline silently mis-behaving.
    """
    build_dir = tmp_path / "_build"
    result = _run_sphinx_build_typst(PROBE_DIR, build_dir)
    assert result.returncode == 0, (
        f"sphinx-build -b typst failed:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    typ_files = sorted(p for p in build_dir.glob("*.typ") if p.name != "_template.typ")
    assert typ_files, f"No .typ file emitted into {build_dir}"
    typ_path = typ_files[0]

    # Mirror render_admonition_greyscale's own single-page shape check
    # rather than importing the module and re-deriving the same assertion
    # through the internal function -- this test proves the fixture's
    # PROPERTY (compiles to one page), independent of the script's own
    # code path.
    result_bytes = typst.compile(str(typ_path), format="png", ppi=150)
    assert isinstance(result_bytes, bytes), (
        f"probe fixture compiled to more than one page "
        f"(typst.compile returned {type(result_bytes).__name__}, "
        "not a single bytes object)"
    )
