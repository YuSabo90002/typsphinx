"""
MSG-03: behavioural gate for the inline (non-extracted) path-quoting sites
in ``typsphinx/builder.py`` -- the v0.8.0-era output-path collision
family, ``_resolve_target_stem()``'s path-refusal warning, the
image-rehome warning, and the bundle-copy I/O messages. The three
extracted 57-11 message builders (``_conf17_violation_message()``,
``_templates_path_collision_message()``, ``_bundle_destination_collision_message()``)
have their own single-quote-half regression coverage added directly to
``tests/test_templates_path_collision_gate.py::TestWindowsPathEscapingRegressionGuard``
by this same plan (D-11) -- this module does not duplicate that.

Every Windows shape below is a hand-built string literal, so this module
runs on every CI lane, never gated on ``os.name`` (D-05's
platform-independence principle, applied here to a test rather than to
product code).

This module asserts ONLY on strings ``typsphinx/builder.py`` itself
emits -- never on a string emitted by the writer module or the template
registration module, which belong to the sibling wave-2 plans (60-03,
60-04) and would collide with them at merge even with disjoint
``files_modified``.
"""

import re
import types

import pytest
from docutils import nodes
from docutils.parsers.rst import states
from docutils.utils import Reporter
from sphinx.errors import ExtensionError

from typsphinx.builder import TypstBuilder


def _assert_no_doubled_separator(message: str) -> None:
    """Re-derives
    ``TestWindowsPathEscapingRegressionGuard._assert_no_doubled_separator``'s
    predicate LOCALLY rather than importing that class -- D-11 keeps this
    module's own gate self-contained, independent of
    ``tests/test_templates_path_collision_gate.py``'s internals. No run
    of two or more consecutive backslashes may appear -- that is what
    ``repr()``'s escaping would produce and what this guard exists to
    catch."""
    doubled = re.findall(r"\\\\+", message)
    assert not doubled, (
        f"Expected every backslash run to be a single unescaped "
        f"separator, found a doubled/escaped run in:\n{message!r}"
    )


def _build_single_image_document(uri: str) -> nodes.document:
    """A minimal one-image doctree, following
    ``tests/test_track_image_key_construction.py``'s
    ``Reporter``/``states.Struct`` document setup."""
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False
    img = nodes.image(uri=uri, candidates={"*": uri})
    doc += img
    return doc


class TestResolveTargetStemPathQuoting:
    """MSG-03/D-08a: ``_resolve_target_stem()``'s path-refusal warning.
    ``target`` is the raw ``typst_documents`` target, which
    ``_escapes_outdir()`` itself treats as path-bearing, and ``fallback``
    is a surviving path component (``posixpath.basename(fallback_source)``)
    -- both guaranteed ``str`` here because this warning sits inside the
    ``isinstance(target, str)`` branch. Pre-fix, ``target`` is
    interpolated with ``!r``, which doubles each of the three backslashes
    in a Windows-shaped target."""

    def test_path_refusal_warning_has_no_doubled_separator(
        self, temp_sphinx_app, caplog
    ):
        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)
        target = "C:\\Users\\runner\\escape.typ"

        with caplog.at_level("WARNING"):
            builder._resolve_target_stem("index", target)

        warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
        assert warning_records, "expected the path-refusal warning to fire"
        message = warning_records[0].getMessage()
        assert "a path is not supported in a typst_documents target" in message
        _assert_no_doubled_separator(message)
        # The raw target, with single (not doubled) separators, must
        # still be named in the message.
        assert target in message


class TestTrackImageRehomeWarningPathQuoting:
    """MSG-03/D-08c: the image-rehome warning at ``_track_image()``'s
    escape branch. After Phase 59 its ``key`` is the RELOCATION path
    (``_typst_converted/{sha1[:8]}-{basename}``) -- a path value, NOT the
    "registry key" SC#3 protects; D-08(c) names this distinction
    explicitly so an executor reading SC#3's "registry keys stay
    ``!r``-quoted" does not skip this site.

    Does not assert on the relocation key's digest or suffix -- Phase 59
    owns that value and this gate must stay green across it."""

    def test_rehome_warning_has_no_doubled_separator(self, temp_sphinx_app, caplog):
        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.init()
        uri = "C:\\Users\\runner\\assets\\sub\\image.png"
        doc = _build_single_image_document(uri)

        with caplog.at_level("WARNING"):
            builder.post_process_images(doc)

        warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
        assert warning_records, "expected the rehome warning to fire"
        message = warning_records[0].getMessage()
        assert "could not rehome image URI" in message
        _assert_no_doubled_separator(message)


class TestOutputPathCollisionMessagePathQuoting:
    """MSG-03/D-06 (AMENDED): the v0.8.0-era output-path collision
    family in ``_validate_output_path_collisions()``, including the two
    ``target`` interpolations D-06's original enumeration missed
    (``:1192``, ``:1199``)."""

    def test_collision_branch_message_has_no_doubled_separator(
        self, temp_sphinx_app
    ):
        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.env = types.SimpleNamespace(found_docs={"index", "chapter1"})
        builder.config.typst_documents = [
            ("index", r"manuals\guide.typ", "T", "A"),
            ("chapter1", r"manuals\guide.typ", "T", "A"),
        ]

        with pytest.raises(ExtensionError) as excinfo:
            builder._validate_output_path_collisions()

        _assert_no_doubled_separator(str(excinfo.value))

    def test_reserved_directory_branch_message_has_no_doubled_separator(
        self, temp_sphinx_app
    ):
        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.env = types.SimpleNamespace(found_docs={"index"})
        builder.config.typst_documents = [
            ("index", r"_template\x.typ", "T", "A"),
        ]

        with pytest.raises(ExtensionError) as excinfo:
            builder._validate_output_path_collisions()

        _assert_no_doubled_separator(str(excinfo.value))


class TestBundleCopyMessagePathQuoting:
    """MSG-03/D-08d: ``_copy_bundle_directory()``'s never-copied
    ``ExtensionError``. Driven directly (no builder init needed) with a
    ``src_dir`` that does not exist on this POSIX host, so ``os.walk()``
    yields nothing, the template is never copied, and the never-copied
    error fires with both Windows-shaped directory values in it."""

    def test_never_copied_message_has_no_doubled_separator(self, temp_sphinx_app):
        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)

        with pytest.raises(ExtensionError) as excinfo:
            builder._copy_bundle_directory(
                r"C:\Users\runner\project\_typst",
                r"C:\out\_template\mykey",
                "mykey",
                "base.typ",
            )

        _assert_no_doubled_separator(str(excinfo.value))


class TestBuilderIdentifierQuotingControl:
    """The falsification gate for task 2's type narrowing, and the
    adjacency control -- MUST be GREEN both before and after the fix.

    Measured: ``_is_usable_typst_documents_entry()`` checks only that the
    entry has at least two elements and that its first element (the
    docname) is a ``str`` -- it does NOT constrain the type of the
    target -- so an unconditional route of that value through
    ``quote_path()`` would turn a warned-about config typo into an
    unhandled ``TypeError`` on every build. This class drives both a
    ``None`` and an ``int`` target and asserts the raised error is still
    an ``ExtensionError``, never a ``TypeError``, and that the message
    still renders the bare Python repr of the non-``str`` value while the
    adjacent docname stays apostrophe-delimited.

    Selector: ``-k identifier_quoting_control`` picks up exactly these
    two methods and nothing else.
    """

    def test_identifier_quoting_control_none_target_still_raises_extension_error(
        self, temp_sphinx_app
    ):
        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.env = types.SimpleNamespace(found_docs={"index"})
        builder.config.typst_documents = [("index", None, "T", "A")]

        with pytest.raises(ExtensionError) as excinfo:
            builder._validate_output_path_collisions()

        assert not isinstance(excinfo.value, TypeError)
        message = str(excinfo.value)
        assert "None" in message
        assert "'index'" in message

    def test_identifier_quoting_control_int_target_still_raises_extension_error(
        self, temp_sphinx_app
    ):
        builder = TypstBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.env = types.SimpleNamespace(found_docs={"index"})
        builder.config.typst_documents = [("index", 123, "T", "A")]

        with pytest.raises(ExtensionError) as excinfo:
            builder._validate_output_path_collisions()

        assert not isinstance(excinfo.value, TypeError)
        message = str(excinfo.value)
        assert "123" in message
        assert "'index'" in message
