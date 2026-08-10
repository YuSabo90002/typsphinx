# Sphinx configuration for the absolute-image-URI render-gate fixture
# (Issue #130 regression).
#
# Minimal self-contained project used by
# tests/test_absolute_image_render_gate.py to prove the `typstpdf` builder
# correctly handles an image node whose `uri` has been rewritten to an
# ABSOLUTE filesystem path -- exactly what Sphinx's real
# `sphinx.transforms.post_transforms.images.ImageConverter` /
# `ImageDownloader` post-transforms do for any image that needs conversion
# (e.g. via `sphinxcontrib.rsvgconverter`, `sphinx.ext.imgconverter`) or
# download: they rewrite `node["uri"]` to an absolute path under
# `<doctreedir>/images/...`, not a source-root-relative path like ordinary
# images get.
#
# Before the fix, this produced:
#
#     WARNING: Failed to copy image ...: '<path>' and '<path>' are the same
#     file
#     error: file not found (searched at <outdir>/<abs src path>)
#
# because `os.path.join(srcdir_or_outdir, uri)` silently discards the first
# argument once `uri` is absolute (both src and dest collapsed to the
# identical path), and `_compute_relative_image_path()` then prepended a
# bogus `../..` depth prefix onto the already-absolute path.
#
# Rather than depending on an external SVG converter binary (rsvg-convert /
# ImageMagick) being installed wherever this suite runs, a small custom
# post-transform below reproduces the *exact* mechanism real Sphinx image
# converters use -- without requiring one to be installed.

import os
import shutil

from docutils import nodes
from sphinx.transforms import SphinxTransform

project = "Absolute Image Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

html_static_path = ["_static"]

# index must be a master document (not merely an included one) so the writer
# emits the full template and TypstPDFBuilder.finish() actually compiles it
# to PDF -- the only build path where the "same file" / "file not found"
# fatals from Issue #130 are observable.
typst_documents = [
    ("index", "index", "Absolute Image Render Gate", "Test Author"),
]


class FakeImageConverter(SphinxTransform):
    """
    Mimics ``sphinx.transforms.post_transforms.images.ImageConverter``: it
    "converts" the ``.svg`` source to a PNG stand-in under
    ``<doctreedir>/images/`` and rewrites ``node["uri"]`` (and its single
    ``"*"`` candidate) to that ABSOLUTE destination path -- reproducing the
    doctree state real Sphinx produces after an image conversion, without
    requiring a real converter binary.
    """

    default_priority = 200

    def apply(self, **kwargs: object) -> None:
        imagedir = os.path.join(self.env.doctreedir, "images")
        os.makedirs(imagedir, exist_ok=True)

        for node in self.document.findall(nodes.image):
            uri = node.get("uri", "")
            if not uri.endswith(".svg"):
                continue

            destpath = os.path.join(imagedir, "diagram.png")
            # Stand in for a real SVG->PNG conversion: copy a valid 1x1 PNG
            # so the emitted image() call points at bytes Typst can decode.
            standin = os.path.join(self.env.srcdir, "_static", "converted_stand_in.png")
            shutil.copyfile(standin, destpath)

            node["uri"] = destpath
            if "candidates" in node:
                node["candidates"] = {"*": destpath}


def setup(app):
    app.add_post_transform(FakeImageConverter)
