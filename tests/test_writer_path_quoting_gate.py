"""MSG-04: `typsphinx/writer.py`'s wrapper-render debug log routes its
three path-valued interpolations (`wrapper_relative_dir`, `include_path`,
`template_file`) through `typsphinx.pathfmt.quote_path()`.

The site is a `logger.debug()` call, so the only observable is `caplog` at
DEBUG level (D-12) -- no existing test drives this log at all, so this
whole module is new coverage. It asserts ONLY on strings
`typsphinx/writer.py` itself emits -- never on a string emitted by
`typsphinx/builder.py` or `typsphinx/template_registry.py`, which belong
to the sibling wave-2 plans (D-11).
"""

import re

from docutils import nodes
from docutils.parsers.rst import states
from docutils.utils import Reporter

from typsphinx.template_registry import TemplateRegistryEntry
from typsphinx.writer import TypstWriter


def _assert_no_doubled_separator(message: str) -> None:
    """Re-derives the guard predicate locally, importing nothing from
    the sibling `builder.py` wiring plan's own collision-gate test
    module (that module's shared-class extension is its exclusive
    privilege, D-11). No run of consecutive backslashes longer than 1
    may appear -- that is what `repr()` escaping would produce and what
    this guard exists to catch."""
    doubled = re.findall(r"\\\\+", message)
    assert not doubled, (
        f"Expected every backslash run to be a single unescaped "
        f"separator, found a doubled/escaped run in:\n{message!r}"
    )


def _build_single_section_document() -> nodes.document:
    """A minimal one-section doctree, following
    `tests/test_template_registry.py`'s `render_wrapper()` call
    precedent: a `Reporter`/`states.Struct`-built `nodes.document` with
    one empty `nodes.section()` child."""
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc += nodes.section()
    return doc


class TestWrapperDebugLogPathQuoting:
    """MSG-04's RED gate: the wrapper-render debug log must not double a
    backslash for a Windows-shaped `wrapper_relative_dir` /
    `content_relative_path`."""

    def test_wrapper_debug_log_has_no_doubled_separator_for_windows_shaped_paths(
        self, temp_sphinx_app, caplog
    ):
        """Pre-fix, this record carries eleven doubled runs (three `!r`
        conversions each doubling every backslash in a Windows-shaped
        value)."""
        app = temp_sphinx_app
        writer = TypstWriter(app.builder)
        doctree = _build_single_section_document()

        wrapper_relative_dir = "C:\\Users\\runner\\out\\sub"
        content_relative_path = "C:\\Users\\runner\\out\\sub\\index.typ"

        with caplog.at_level("DEBUG"):
            writer.render_wrapper(
                ("index", "manual.typ", "T", "A"),
                doctree,
                wrapper_relative_dir,
                content_relative_path,
            )

        debug_records = [r for r in caplog.records if r.levelname == "DEBUG"]
        wrapper_records = [
            r
            for r in debug_records
            if r.getMessage().startswith("Rendering wrapper for docname")
        ]
        assert len(wrapper_records) == 1, (
            f"Expected exactly one wrapper-render debug record, found "
            f"{len(wrapper_records)}: {[r.getMessage() for r in debug_records]}"
        )
        message = wrapper_records[0].getMessage()

        _assert_no_doubled_separator(message)
        assert wrapper_relative_dir in message, (
            f"Expected the raw wrapper_relative_dir value with its single "
            f"separators to still be present in the message, got: {message!r}"
        )


class TestWrapperDebugLogTemplateFileNone:
    """D-03's byte-identity pin for the live `None` build path: a package
    configured ALONE (no custom template) makes `writer.py` bind
    `template_file` to `None`. `writer.py` binds `template_file` to
    `None` whenever a package is configured with no custom template, so
    a helper that raised on `None` would turn a supported build shape
    into a crash inside a debug log -- the worst possible place to
    discover it. This method must be GREEN both before and after the
    fix."""

    def test_wrapper_debug_log_template_file_none_renders_bare_none_on_the_package_alone_path(
        self, temp_sphinx_app, caplog
    ):
        app = temp_sphinx_app
        writer = TypstWriter(app.builder)
        doctree = _build_single_section_document()

        template_entry = TemplateRegistryEntry(
            key="typst",
            template=None,
            package="@preview/charged-ieee:0.1.3",
            template_function="charged-ieee",
        )

        with caplog.at_level("DEBUG"):
            writer.render_wrapper(
                ("index", "manual.typ", "T", "A"),
                doctree,
                "",
                "index.typ",
                template_entry=template_entry,
            )

        debug_records = [r for r in caplog.records if r.levelname == "DEBUG"]
        wrapper_records = [
            r
            for r in debug_records
            if r.getMessage().startswith("Rendering wrapper for docname")
        ]
        assert len(wrapper_records) == 1
        message = wrapper_records[0].getMessage()

        assert "template_file=None" in message, (
            f"Expected the bare four-character word None with no delimiter "
            f"around it, got: {message!r}"
        )
        assert "wrapper_relative_dir=''" in message, (
            f"Expected the empty wrapper_relative_dir to render as two "
            f"apostrophes, got: {message!r}"
        )
