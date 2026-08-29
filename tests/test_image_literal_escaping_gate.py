"""
Phase 59 plan 03: IMG-05 -- ``visit_image()`` escape-last wiring gate.

Before this plan, ``visit_image()`` interpolated the return value of
``_compute_relative_image_path()`` directly into the emitted
``image("...")`` Typst string literal, with no escaping. A path whose
basename carries a literal double quote (a real, if unusual, filesystem
shape) therefore produced an emitted ``.typ`` string literal with an
unescaped ``"`` inside it -- a malformed literal Typst's parser rejects.

This gate proves ``visit_image()`` routes the adjusted URI through
``escape_typst_string()`` -- the codebase's single source of truth for
Typst string-literal safety -- before interpolation.

Load-bearing design choices (see the test's own docstring for the same
claims, restated at the point they matter):

1. The URI this gate rewrites a doctree node to is RELATIVE
   (``images/we"ird.png``), so ``_is_absolute_image_uri()`` is False and
   the node never reaches the escape branch inside
   ``typsphinx/builder.py::_track_image()`` that plan 59-02 rewrote. This
   gate therefore measures ``visit_image()`` alone, independent of every
   other plan in this phase.
2. No file with that name is ever created on disk, so this gate runs on
   every CI lane including ``windows-latest``, where a double quote is an
   illegal filename character. ``copy_image_files()`` logs
   ``Image file not found`` and the build continues -- that warning is
   expected and is never asserted against here.

This module carries its own local copy of the
``_run_sphinx_build_typst(srcdir, outdir)`` helper rather than importing a
sibling module's, per the convention every gate module in this suite
follows (see ``tests/test_package_template_routing.py``). It also invokes
Sphinx as ``sys.executable -m sphinx`` -- never a resolved builder-script
binary on PATH, nor via a package-manager-run wrapper -- per the documented
NixOS-sandbox PATH-shadowing hazard where a stray ``uv`` binary makes that
subprocess-level invocation fail even though the same command succeeds in
a plain shell.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from typsphinx.translator import escape_typst_string

_FIXTURE_PNG = (
    Path(__file__).parent
    / "fixtures"
    / "absolute_image_render_gate"
    / "_static"
    / "converted_stand_in.png"
)


def _run_sphinx_build_typst(srcdir: Path, outdir: Path) -> subprocess.CompletedProcess:
    """Run Sphinx's ``typst`` builder as a subprocess and return the result."""
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typst", str(srcdir), str(outdir)],
        capture_output=True,
        text=True,
    )


_CONF_PY = '''\
import os
import shutil

from docutils import nodes
from sphinx.transforms import SphinxTransform

project = "IMG-05 Escaping Gate"
author = "Test Author"
extensions = ["typsphinx"]
typst_documents = [("index", "master", "Test", "Author")]


class RelativeQuoteRewriter(SphinxTransform):
    """Rewrites every image node's ``uri`` (and its ``"*"`` candidate, when
    present) to a RELATIVE path whose basename carries one literal double
    quote and no backslash. Mirrors the post-transform pattern in
    tests/fixtures/absolute_image_render_gate/conf.py, but rewrites to a
    relative path rather than an absolute one -- IMG-05's gate must stay
    on the relative-URI branch, independent of the escape branch plan
    59-02 rewrote inside typsphinx/builder.py.
    """

    default_priority = 200

    def apply(self, **kwargs):
        for node in self.document.findall(nodes.image):
            node["uri"] = \'images/we"ird.png\'
            if "candidates" in node:
                node["candidates"] = {"*": \'images/we"ird.png\'}


def setup(app):
    app.add_post_transform(RelativeQuoteRewriter)
'''


def _make_source_tree(srcdir: Path) -> None:
    srcdir.mkdir(parents=True, exist_ok=True)
    (srcdir / "conf.py").write_text(_CONF_PY)
    (srcdir / "index.rst").write_text(
        "Test Document\n=============\n\n.. image:: original.png\n"
    )
    # Real PNG bytes so the read-phase ImageCollector accepts the
    # directive; the post-transform above rewrites the node's uri away
    # from this file before copy_image_files() ever runs, so the file at
    # this path is never actually read by the copy step.
    shutil.copy2(_FIXTURE_PNG, srcdir / "original.png")


class TestImageLiteralEscaping:
    """IMG-05: ``visit_image()`` escapes the adjusted URI exactly once,
    on the return value of ``_compute_relative_image_path()``, before
    interpolating it into the emitted ``image("...")`` literal."""

    def test_image_literal_escaping_quote_is_escaped_in_emitted_typ(self, tmp_path):
        """A relative image URI whose basename contains a literal double
        quote must emit an ESCAPED quote inside the ``image("...")``
        literal, never a raw one.

        Two properties of the chosen URI are load-bearing:

        1. It is RELATIVE (``images/we"ird.png``), so
           ``_is_absolute_image_uri()`` is False and the node never
           reaches the escape branch inside
           ``typsphinx/builder.py::_track_image()`` that plan 59-02
           already rewrote -- this test therefore measures
           ``visit_image()`` alone, independent of every other plan in
           this phase.
        2. No file named ``we"ird.png`` is ever created on disk, so this
           gate runs on every CI lane including ``windows-latest``, where
           a double quote is an illegal filename character.
           ``copy_image_files()`` logs ``Image file not found`` and the
           build continues -- that warning is expected and is never
           asserted against below.
        """
        srcdir = tmp_path / "source"
        _make_source_tree(srcdir)
        outdir = tmp_path / "build"

        result = _run_sphinx_build_typst(srcdir, outdir)

        assert result.returncode == 0, (
            f"Sphinx build failed:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        content_typ = outdir / "index.typ"
        assert (
            content_typ.exists()
        ), "index.typ (the content document) was not generated"
        emitted_text = content_typ.read_text()

        raw_uri = 'images/we"ird.png'
        escaped_fragment = f'image("{escape_typst_string(raw_uri)}"'
        raw_fragment = f'image("{raw_uri}"'

        assert escaped_fragment in emitted_text, (
            f"Expected the escaped literal {escaped_fragment!r} in the "
            f"emitted .typ, got:\n{emitted_text}"
        )
        assert raw_fragment not in emitted_text, (
            f"Found the RAW unescaped literal {raw_fragment!r} in the "
            f"emitted .typ -- the quote must be escaped:\n{emitted_text}"
        )
