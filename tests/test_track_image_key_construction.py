"""
IMG-04/IMG-06: `_track_image()`'s escape branch must build its relocation
key from a forward-slash-normalized basename (IMG-04), and that key's
final path component must be bounded to 255 UTF-8 bytes with the
``{sha1[:8]}-`` collision anchor kept whole (IMG-06).

`TestRelocationKeyNoBackslash` is IMG-04's behavioural RED gate: it drives
a Windows-shaped absolute URI through the real product path
(`TypstBuilder.post_process_images()` -> `_track_image()`'s escape
branch), following `tests/test_builder.py`'s house pattern exactly
(`temp_sphinx_app` -> `TypstBuilder(app, app.env)` -> `builder.init()` ->
a hand-built `nodes.image` node -> `builder.post_process_images(doc)`
inside `caplog.at_level("WARNING")`).

`TestRelocationKeyLengthBound` starts as IMG-06's behavioural RED gate
(driven the same way) and later gains D-08(a)'s pure-string property gates
-- direct calls to the module-level helpers, no builder, no filesystem --
so every one of those runs on every CI lane including `windows-latest`.

Never asserts on the `logger.warning` message text -- its `!r` quoting is
MSG-03's site in Phase 60 (ROADMAP constraint 4).
"""

import os

from docutils import nodes
from docutils.parsers.rst import states
from docutils.utils import Reporter

from typsphinx.builder import RESERVED_IMAGE_NAMESPACE, TypstBuilder


def _build_single_image_document(uri: str) -> nodes.document:
    """A minimal one-image doctree, following `tests/test_builder.py`'s
    `Reporter`/`states.Struct` document setup."""
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False
    img = nodes.image(uri=uri, candidates={"*": uri})
    doc += img
    return doc


class TestRelocationKeyNoBackslash:
    """IMG-04's behavioural RED gate: a Windows-shaped absolute URI must
    never leave a literal backslash in the relocation key.

    Pitfall 3 (59-RESEARCH.md): a green `copy_image_files()` run is NOT
    evidence the key is backslash-free, because a POSIX filesystem happily
    creates a filename containing a literal backslash byte -- ext4 (and
    most POSIX filesystems) treat `\\` as an ordinary character, not a
    separator, so `shutil.copy2()` would succeed and log nothing even if
    the key still carried one. This class's assertion is on the KEY
    STRING itself (`node["uri"]`), independent of any filesystem
    operation -- the only observable that can actually catch a residual
    backslash on a POSIX CI host.
    """

    def test_relocation_key_no_backslash_for_windows_shaped_uri(
        self, temp_sphinx_app, caplog
    ):
        """A Windows-shaped absolute URI whose basename carries both a
        backslash-delimited directory structure and a literal double
        quote must relocate to a key containing no backslash at all."""
        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.init()

        # Raw string: exactly one backslash per Windows path separator,
        # plus one literal double quote in the basename (the D-01 shape
        # this phase's IMG-07 gate later reuses).
        uri = r"C:\Users\runner\assets\sub\we\"ird.png"
        doc = _build_single_image_document(uri)

        with caplog.at_level("WARNING"):
            builder.post_process_images(doc)

        img = doc[0]
        key = img["uri"]

        assert key.startswith(f"{RESERVED_IMAGE_NAMESPACE}/"), (
            f"expected the escape branch to fire and relocate under "
            f"{RESERVED_IMAGE_NAMESPACE!r}, got key {key!r}"
        )
        assert "\\" not in key, (
            f"relocation key must contain no backslash for a "
            f"Windows-shaped URI, got key {key!r}"
        )


class TestRelocationKeyLengthBound:
    """IMG-06's behavioural RED gate (this method) plus, from Task 3
    onward, D-08(a)'s pure-string property gates -- every test name in
    this class contains `length_bound` so the `-k length_bound` selector
    in `59-VALIDATION.md` picks all of them up."""

    def test_relocation_key_length_bound_through_track_image(
        self, temp_sphinx_app, tmp_path, caplog
    ):
        """A 250-character ASCII basename, rehomed through the real
        escape branch, must produce a final path component of at most
        255 UTF-8 bytes.

        Pre-fix this is 263 bytes (9 bytes of ``{digest}-`` plus the
        254-byte basename `"x" * 250 + ".png"`) -- D-06's measured
        "bounding the basename alone still fails" case; this gate proves
        the bound applies to the WHOLE final component, not merely
        caps at 255-minus-nothing.
        """
        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.init()

        long_basename = "x" * 250 + ".png"
        # Outside doctreedir (builddir/.doctrees) by construction --
        # tmp_path/"outside"/<basename> never lives under
        # tmp_path/"build"/.doctrees, so the escape branch always fires.
        uri = os.path.join(str(tmp_path), "outside", long_basename)
        doc = _build_single_image_document(uri)

        with caplog.at_level("WARNING"):
            builder.post_process_images(doc)

        img = doc[0]
        final_component = img["uri"].rsplit("/", 1)[-1]
        byte_length = len(final_component.encode("utf-8"))

        assert byte_length <= 255, (
            f"relocation key's final path component must be at most 255 "
            f"UTF-8 bytes, got {byte_length} bytes: {final_component!r}"
        )
