"""
Render-and-desaturate pipeline for ADM-04's greyscale-distinguishability UAT.

ADM-04 (39-CONTEXT.md's greyscale-distinguishability requirement, the
milestone's only ``[V]`` -- visual-UAT -- requirement) asks whether the four
admonition colour buckets stay distinguishable once colour is removed,
because their header-band luminances sit close together (D-06 measured a
5.4-percentage-point spread). There is no mechanical assertion that can
substitute for the owner's eye, so this module exists to produce the real
artifact the owner looks at: it rasterises an already-emitted single-page
``.typ`` file to PNG via ``typst.compile(..., format="png", ppi=...)`` and
desaturates it via Pillow's ``Image.convert("L")``.

This module produces the PIPELINE only -- it does NOT produce the committed
ADM-04 artifact itself. That render must be taken from POST-fix code (after
plan 39-05..39-06's bucket-routing changes land) and is plan 39-07's job;
running this pipeline against the pre-fix translator would show the
pre-phase bucket assignments while claiming to evidence the post-phase ones
(39-RESEARCH.md's T-39-10 threat, mitigated by keeping the artifact out of
this plan entirely).

Chosen PPI (default): 150. Typst's own CLI default is 144 (its "one
CSS/print pixel per pt at 96 CSS dpi, scaled to Typst's 72pt/in base" ==
144dpi at 2x); 150 is a round, slightly higher value that keeps the small
gentle-clues icons (16-20pt square) legible at typical screen zoom without
producing an unreasonably large PNG for a single A4 page. Callable
programmatically via a different ``ppi`` argument if the owner wants a
higher-resolution look at the icon shapes.

BT.601 vs BT.709 (Pitfall 5, 39-RESEARCH.md): Pillow's ``Image.convert("L")``
desaturates using the ITU-R BT.601 luma weights (``L = R*299/1000 +
G*587/1000 + B*114/1000``), NOT the ITU-R BT.709 / sRGB relative-luminance
weights (``0.2126R + 0.7152G + 0.0722B``) that 39-CONTEXT.md's D-06
luminance table was computed with. The two formulas are close (both weight
green heaviest) but not identical -- BT.601 weights red more and green less
than BT.709. This means the rendered greys will not exactly match D-06's
analytical percentages, and that is EXPECTED, not a bug: D-06's table was
always scaffolding to predict the defect existed, never a target the real
render is graded against. The owner's ADM-04 sign-off is made against the
rendered PNG this module produces, never against the D-06 table.

Single-page requirement (Pitfall 4, 39-RESEARCH.md): ``typst.compile(...,
format="png", ppi=...)`` returns a single ``bytes`` object for a one-page
document, but a ``list`` of one ``bytes`` object per page for a multi-page
document (verified against the installed typst-py 0.15.0 this session: a
known 4-page fixture returned a 4-element ``list``). Multi-page PNG export
additionally requires a page-number template (``{n}``/``{p}``) in the
output filename, which this pipeline deliberately never supplies -- so a
multi-page input would silently write only a description of the FIRST
element rather than a real artifact. ``render_admonition_greyscale`` guards
against this explicitly and raises ``RuntimeError`` naming the page-template
requirement rather than producing a wrong artifact.
"""

from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

import typst
from PIL import Image

#: Typst's own CLI default is 144 PPI; 150 is a round, slightly higher value
#: -- see the module docstring's "Chosen PPI" paragraph for the rationale.
DEFAULT_PPI = 150


def render_admonition_greyscale(typ_path: Path, ppi: float, out_png: Path) -> Path:
    """
    Compile a single-page ``.typ`` file to PNG and desaturate it to greyscale.

    Args:
        typ_path: Path to an already-emitted, single-page ``.typ`` file
            (produced by ``sphinx-build -b typst``, NOT compiled by this
            function -- see the ``__main__`` guard below for the full
            sphinx-build-then-render pipeline).
        ppi: Pixels-per-inch to rasterise at. See the module docstring's
            "Chosen PPI" paragraph.
        out_png: Where to write the desaturated PNG.

    Returns:
        ``out_png``, unchanged, for chaining.

    Raises:
        RuntimeError: if the compiled document is not exactly one page. A
            multi-page document makes ``typst.compile(..., format="png")``
            return a sequence of per-page images rather than one ``bytes``
            object, and Typst's own PNG export additionally requires a
            page-number template in the output filename once a document has
            more than one page (Pitfall 4). Rather than silently writing
            only the first page's image under a filename that claims to be
            the whole document, this function fails loudly.
    """
    result = typst.compile(str(typ_path), format="png", ppi=ppi)

    # A single-page compile returns one `bytes` object directly (verified
    # against typst-py 0.15.0's installed behaviour this session). Anything
    # else -- a `list`/`tuple` of per-page `bytes` -- means the document has
    # more than one page.
    if not isinstance(result, bytes):
        raise RuntimeError(
            f"{typ_path} compiled to more than one page "
            f"(typst.compile returned {type(result).__name__} with "
            f"{len(result) if hasattr(result, '__len__') else '?'} "
            "element(s), not a single bytes object). Typst's PNG export "
            "requires a page-number template ({n}/{p}) in the output "
            "filename once a document exceeds one page; this pipeline "
            "deliberately does not support that shape. Keep the probe "
            "fixture to exactly one page instead."
        )

    image = Image.open(io.BytesIO(result))
    greyscale = image.convert("L")  # ITU-R BT.601 luma weights -- see docstring.
    greyscale.save(out_png)
    return out_png


def _build_typ(source_dir: Path, build_dir: Path) -> Path:
    """
    Run ``sphinx-build -b typst`` over ``source_dir`` and return the path to
    the emitted master document's ``.typ`` file.

    Invoked as ``sys.executable -m sphinx`` -- never a bare ``sphinx-build``
    and never through ``uv run`` -- so the exact interpreter/venv already
    running this script is reused, matching the convention documented in
    ``tests/test_desc_rubric_decoupling_render_gate.py``.
    """
    result = subprocess.run(
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
    if result.returncode != 0:
        raise RuntimeError(
            f"sphinx-build failed (exit {result.returncode}):\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

    typ_files = sorted(p for p in build_dir.glob("*.typ") if p.name != "_template.typ")
    if not typ_files:
        raise RuntimeError(f"No .typ file emitted into {build_dir}")
    return typ_files[0]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Build a Sphinx typst source directory and render its master "
            "document to a desaturated greyscale PNG (ADM-04's pipeline)."
        )
    )
    parser.add_argument(
        "source_dir", type=Path, help="Sphinx source directory to build."
    )
    parser.add_argument("output_png", type=Path, help="Output PNG path.")
    parser.add_argument(
        "--ppi",
        type=float,
        default=DEFAULT_PPI,
        help=f"Rasterisation PPI (default: {DEFAULT_PPI}).",
    )
    args = parser.parse_args()

    import tempfile

    with tempfile.TemporaryDirectory() as build_dir_str:
        build_dir = Path(build_dir_str)
        typ_path = _build_typ(args.source_dir, build_dir)
        out = render_admonition_greyscale(typ_path, args.ppi, args.output_png)
        print(f"Wrote {out}")
