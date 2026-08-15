# Sphinx configuration for the converted-image-collision render-gate fixture
# (Phase 50, IMG-01).
#
# Sibling of tests/fixtures/absolute_image_render_gate/ (D-12 pins that
# fixture's own assertions unedited; this is a NEW, separate fixture
# directory, never a mutation of it).
#
# This fixture reproduces the IMG-01 collision: a converted image's
# absolute URI is rehomed by TypstBuilder._track_image() to the
# doctreedir-relative path "images/chart.png" -- the EXACT basename an
# ordinary, genuine source image at <srcdir>/images/chart.png already
# occupies. Before the Phase 50 fix, both tracking sites guard insertion
# with `if <key> not in self.images`, so whichever document is written
# first silently wins the key and the other document's real picture is
# never copied -- with no warning, and the build succeeds (D-10, D-08).
#
# As with tests/fixtures/absolute_image_render_gate/conf.py, this fixture
# avoids depending on an external SVG converter binary by reproducing the
# exact doctree-state mechanism Sphinx's real image converters use via a
# small custom post-transform.

import os
import shutil

from docutils import nodes
from sphinx.transforms import SphinxTransform

project = "Converted Image Collision Render Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

html_static_path = ["_static"]

# Phase 47 fixture de-collision: the target must not be "index" (whose
# resolved stem is identical to the docname "index" itself, a self-
# collision under the two-layer content/wrapper split). Renamed to
# "master.typ", matching the absolute_image_render_gate fixture's own
# precedent.
typst_documents = [
    ("index", "master.typ", "Converted Image Collision Render Gate", "Test Author"),
]


class FakeImageConverter(SphinxTransform):
    """
    Mimics ``sphinx.transforms.post_transforms.images.ImageConverter``: it
    "converts" the ``.svg`` source in ``converted_source.rst`` to a PNG
    stand-in under ``<doctreedir>/images/`` and rewrites ``node["uri"]``
    (and its single ``"*"`` candidate) to that ABSOLUTE destination path --
    reproducing the doctree state real Sphinx produces after an image
    conversion, without requiring a real converter binary.

    The stand-in's destination basename is deliberately ``chart.png`` --
    the SAME basename the real source image in ``real_source.rst`` already
    occupies at ``<srcdir>/images/chart.png``. That basename coincidence is
    the entire point of this fixture (D-10): it is the wire that makes
    ``_track_image()``'s rehome collide at all.
    """

    default_priority = 200

    def apply(self, **kwargs: object) -> None:
        imagedir = os.path.join(self.env.doctreedir, "images")
        os.makedirs(imagedir, exist_ok=True)

        for node in self.document.findall(nodes.image):
            uri = node.get("uri", "")
            if not uri.endswith(".svg"):
                continue

            destpath = os.path.join(imagedir, "chart.png")
            standin = os.path.join(
                self.env.srcdir, "_static", "converted_chart_stand_in.png"
            )
            shutil.copyfile(standin, destpath)

            node["uri"] = destpath
            if "candidates" in node:
                node["candidates"] = {"*": destpath}


def setup(app):
    app.add_post_transform(FakeImageConverter)
