# Sphinx configuration for the Windows-shaped image URI gate fixture
# (IMG-07, Phase 59 plan 04).
#
# Two-mode fixture, selected by the TYPSPHINX_WIN_URI_MODE environment
# variable, serving both this phase's gates:
#
# - "string" mode (default): the image node's URI is rewritten to a
#   hand-built Windows-shaped absolute STRING literal. No file is ever
#   created -- a double quote and a backslash are both illegal NTFS
#   filename characters, so creating one would make this mode unrunnable
#   on windows-latest. _track_image() decides purely from the path
#   SHAPE, so the file need not exist. Used by the all-lane
#   TestWindowsShapedImageUriStringShape gate (test_windows_image_uri_
#   render_gate.py), which asserts on the emitted image("...") literal
#   from a real "-b typst" build with no filesystem support required.
#
# - "file" mode: a REAL file is created outside self.env.doctreedir
#   (a sibling directory), with a raw basename carrying both a literal
#   backslash and a literal double quote, and the node's URI is
#   rewritten to that file's absolute path. Used by the
#   TestWindowsShapedImageUriCompileGate real typst.compile() gate,
#   which can only run on a filesystem able to hold that basename.
#
# D-01's measured four-combination table (59-CONTEXT.md), reproduced
# here so the reason for this exact basename shape travels with the
# fixture. Raw basename: sub\we"ird.png -- normalized basename:
# we"ird.png.
#
# | tree        | emitted image(...) literal                | Typst refusal                |
# |-------------|--------------------------------------------|-------------------------------|
# | unfixed     | ..._typst_converted/{d}-sub\we"ird.png      | path must not contain a backslash |
# | IMG-04 only | ..._typst_converted/{d}-we"ird.png          | unclosed delimiter           |
# | IMG-05 only | ..._typst_converted/{d}-sub\\we\"ird.png    | path must not contain a backslash |
# | both        | ..._typst_converted/{d}-we\"ird.png         | compiles                     |
#
# A backslash-only fixture would already be green with the key
# normalization (IMG-04) alone and could therefore not prove SC#2's
# "neither alone would have closed it" -- the literal double quote in
# the basename is what keeps the escaping fix (IMG-05) load-bearing
# too. Only when BOTH the backslash-free key AND the escaped quote are
# present does the emitted literal compile.

import os
import shutil

from docutils import nodes
from sphinx.transforms import SphinxTransform

project = "Windows Shaped Image URI Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

html_static_path = ["_static"]

# Target stem "master.typ" deliberately differs from the docname "index"
# to avoid the self-collision the analog fixture
# (absolute_image_render_gate/conf.py) explains in its own comment.
typst_documents = [
    ("index", "master.typ", "Windows Shaped Image URI Gate", "Test Author"),
]

_MODE = os.environ.get("TYPSPHINX_WIN_URI_MODE", "string")

# The raw Windows-shaped basename this whole fixture exercises: one
# literal backslash directory separator per component, plus one literal
# double quote in the final component.
_WIN_DRIVE_PREFIX = "C:"
_WIN_DIR_COMPONENTS = ["Users", "runner", "assets", "sub"]
_WIN_BASENAME = 'we"ird.png'


class WindowsShapedImageUriTransform(SphinxTransform):
    """
    Rewrites every image node's ``uri`` (and its ``"*"`` candidate, when
    present) to a Windows-shaped absolute path -- either a pure string
    literal ("string" mode, no file created) or a real absolute path to
    a file genuinely created outside ``self.env.doctreedir`` ("file"
    mode) -- selected by ``TYPSPHINX_WIN_URI_MODE``.
    """

    default_priority = 200

    def apply(self, **kwargs: object) -> None:
        for node in self.document.findall(nodes.image):
            if _MODE == "file":
                new_uri = self._rehome_to_real_file()
            else:
                new_uri = self._string_only_uri()

            node["uri"] = new_uri
            if "candidates" in node:
                node["candidates"] = {"*": new_uri}

    def _string_only_uri(self) -> str:
        """Build the hand-written Windows-shaped absolute string literal.

        No file is created in this mode -- see the module docstring for
        why. ``copy_image_files()`` will log ``Image file not found``
        and the build continues; that warning is expected here.
        """
        return (
            _WIN_DRIVE_PREFIX
            + "\\"
            + "\\".join(_WIN_DIR_COMPONENTS)
            + "\\"
            + _WIN_BASENAME
        )

    def _rehome_to_real_file(self) -> str:
        """Copy the stand-in PNG to a real file with the Windows-shaped
        raw basename, outside ``doctreedir``, and return its absolute
        path.

        The destination directory is a SIBLING of ``self.env.doctreedir``
        (a distinguishing suffix appended to the doctreedir path) so the
        rewritten URI genuinely lands outside ``doctreedir`` and
        ``path.relpath()`` therefore carries a ``..`` segment into
        ``_escapes_outdir()`` -- exercising the exact escape branch
        ``_build_relocation_key()`` was written for.

        Per 59-CONTEXT.md Specific Idea #3, the file must genuinely
        exist: ``copy_image_files()`` copies from the raw
        ``resolved_uri`` and skips a missing source with a warning, and
        a compile that then failed for "file not found" would be
        indistinguishable from a fixture bug.
        """
        # os.fspath(), never a direct str method on env.doctreedir --
        # Sphinx 9.1 warns (RemovedInSphinx10Warning) on implicit
        # str-conversion of its own PathLike config/env attributes.
        doctreedir = os.fspath(self.env.doctreedir)
        sibling_dir = doctreedir.rstrip(os.sep) + "_win_uri_sibling"
        os.makedirs(sibling_dir, exist_ok=True)

        # A single filename COMPONENT (never a subdirectory) carrying
        # one literal backslash and one literal double quote -- POSIX
        # permits both bytes in a filename; NTFS permits neither, which
        # is exactly why this mode is the one that skips on
        # windows-latest (D-03).
        raw_basename = "sub\\" + _WIN_BASENAME
        standin = os.path.join(self.env.srcdir, "_static", "converted_stand_in.png")
        destpath = os.path.join(sibling_dir, raw_basename)
        # Stand in for a real image conversion/download: copy a valid
        # 1x1 PNG so the emitted image() call points at bytes Typst can
        # decode.
        shutil.copyfile(standin, destpath)
        return destpath


def setup(app):
    app.add_post_transform(WindowsShapedImageUriTransform)
