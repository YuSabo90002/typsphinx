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

import hashlib
import os

from docutils import nodes
from docutils.parsers.rst import states
from docutils.utils import Reporter

from typsphinx.builder import (
    RESERVED_IMAGE_NAMESPACE,
    TypstBuilder,
    _bound_relocation_component,
    _build_relocation_key,
)


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

    # -- D-08(a)'s pure-string property gates ---------------------------
    #
    # Direct calls to _bound_relocation_component()/_build_relocation_key()
    # only -- no builder instance, no temp_sphinx_app, no filesystem -- so
    # every test below runs on every CI lane including windows-latest.

    def test_length_bound_boundary_246_byte_basename_untruncated(self):
        """A basename whose byte length exactly fills the 246-byte budget
        (255 minus the 9-byte `{digest}-` prefix) is returned untruncated,
        landing exactly at the 255-byte limit."""
        digest = "a1b2c3d4"
        basename = "x" * 246
        result = _bound_relocation_component(digest, basename)

        assert result == f"{digest}-{basename}"
        assert len(result.encode("utf-8")) == 255

    def test_length_bound_boundary_247_byte_basename_at_most_255(self):
        """One byte over the budget must still be bounded to at most 255
        bytes overall."""
        digest = "a1b2c3d4"
        basename = "x" * 247
        result = _bound_relocation_component(digest, basename)

        assert len(result.encode("utf-8")) <= 255

    def test_length_bound_boundary_245_byte_basename_exactly_254_unchanged(
        self,
    ):
        """One byte under the budget is returned exactly unchanged, one
        byte short of the 255-byte limit."""
        digest = "a1b2c3d4"
        basename = "x" * 245
        result = _bound_relocation_component(digest, basename)

        assert result == f"{digest}-{basename}"
        assert len(result.encode("utf-8")) == 254

    def test_length_bound_encoding_cjk_round_trips_and_stays_at_most_255(
        self,
    ):
        """A basename of 100 three-byte CJK characters plus `.png` yields a
        component whose `encode("utf-8").decode("utf-8")` round-trips
        without raising, is at most 255 bytes, and still ends `.png`.

        The contract here is BYTE-validity, not grapheme-cluster
        integrity -- a CJK character (a single Unicode code point in this
        basename) may be dropped whole by the truncation, but no partial,
        invalid UTF-8 byte sequence is ever returned.
        """
        digest = "deadbeef"
        basename = "図" * 100 + ".png"
        result = _bound_relocation_component(digest, basename)
        encoded = result.encode("utf-8")

        assert encoded.decode("utf-8") == result
        assert len(encoded) <= 255
        assert result.endswith(".png")

    def test_length_bound_empty_basename_yields_bare_digest_prefix(self):
        """An empty basename yields exactly the 9-byte `{digest}-` prefix
        and raises nothing."""
        digest = "a1b2c3d4"
        result = _bound_relocation_component(digest, "")

        assert result == f"{digest}-"
        assert len(result.encode("utf-8")) == 9

    def test_length_bound_precision_budget_and_extension_truncation(self):
        """The basename budget equals `255 - len(f"{digest}-".encode())`
        computed from the same expression the product uses, and an
        extension longer than the whole budget is itself truncated while
        at least one stem byte survives."""
        digest = "a1b2c3d4"
        prefix_byte_length = len(f"{digest}-".encode())
        budget = 255 - prefix_byte_length

        basename = "s" + "." + "e" * 300
        result = _bound_relocation_component(digest, basename)

        assert budget == 246
        assert result.startswith(f"{digest}-")
        stem_and_ext = result[len(f"{digest}-") :]
        assert stem_and_ext.startswith(
            "s"
        ), f"expected at least one stem byte to survive, got {result!r}"
        assert len(result.encode("utf-8")) <= 255

    def test_length_bound_multibyte_leading_stem_survives_tight_budget(self):
        """D-07's "never emptied" holds when the stem's FIRST character is
        multi-byte and the extension leaves it under one character of room.

        Regression gate for the pre-fix defect: reserving a single BYTE for
        the stem is not enough for a 3-byte leading character, so the UTF-8
        boundary walk-back landed on `b""` and dropped the whole stem while
        the lower-priority extension kept its allotment -- inverting the
        precedence `_bound_relocation_component` documents. The ASCII
        sibling below is what made the defect invisible: an ASCII stem fits
        the one reserved byte, so only a multi-byte leading character
        exposes it.
        """
        digest = "a1b2c3d4"

        multibyte = _bound_relocation_component(digest, "\u56f3" + "." + "e" * 244)
        ascii_sibling = _bound_relocation_component(digest, "a" + "." + "e" * 244)

        for label, result in (("multibyte", multibyte), ("ascii", ascii_sibling)):
            stem = result[len(f"{digest}-") :].rsplit(".", 1)[0]
            assert stem != "", (
                f"D-07 violated for the {label} stem: "
                f"the stem was emptied entirely, got {result!r}"
            )
            assert len(result.encode("utf-8")) <= 255

        assert multibyte[len(f"{digest}-") :].startswith("\u56f3")

    def test_length_bound_multibyte_stem_kept_when_extension_exceeds_budget(self):
        """The extension-truncation branch also preserves a multi-byte
        leading stem character, not only the untruncated-extension path."""
        digest = "a1b2c3d4"
        result = _bound_relocation_component(digest, "\u56f3" + "." + "e" * 300)

        stem = result[len(f"{digest}-") :].rsplit(".", 1)[0]
        assert stem.startswith("\u56f3"), (
            "the multi-byte stem character must survive even when the "
            f"extension alone exceeded the budget, got {result!r}"
        )
        assert len(result.encode("utf-8")) <= 255

    def test_length_bound_anchor_survives_truncation_with_extension(self):
        """Every truncated component still starts with `f"{digest}-"` and,
        when an extension survives at all, still ends with it."""
        digest = "a1b2c3d4"
        basename = "x" * 250 + ".png"
        result = _bound_relocation_component(digest, basename)

        assert result.startswith(f"{digest}-")
        assert result.endswith(".png")

    def test_length_bound_two_long_uris_sharing_a_basename_stay_distinct(
        self,
    ):
        """SC#3's collision re-proof: two distinct absolute URIs that
        differ only in a directory component and share a 250-character
        basename must produce two DISTINCT `_build_relocation_key()`
        results -- the collision property IMG-03 closed is preserved
        under IMG-06's truncation."""
        long_basename = "x" * 250 + ".png"
        uri_a = f"/some/escape/dir/a/{long_basename}"
        uri_b = f"/some/escape/dir/b/{long_basename}"

        # Expected digests computed from the same construction the
        # product uses -- never a hardcoded hex literal.
        digest_a = hashlib.sha1(uri_a.encode("utf-8")).hexdigest()[:8]
        digest_b = hashlib.sha1(uri_b.encode("utf-8")).hexdigest()[:8]

        key_a = _build_relocation_key(uri_a)
        key_b = _build_relocation_key(uri_b)

        assert key_a != key_b
        assert key_a.startswith(f"{RESERVED_IMAGE_NAMESPACE}/{digest_a}-")
        assert key_b.startswith(f"{RESERVED_IMAGE_NAMESPACE}/{digest_b}-")
