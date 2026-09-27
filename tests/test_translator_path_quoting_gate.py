"""MSG-06: `typsphinx/translator.py`'s two cross-directory relative-path
DEBUG logs (`_compute_relative_include_path` and `_compute_relative_image_path`)
route their `up_path`/`down_path` interpolations through
`typsphinx.pathfmt.quote_path()`, so a path carrying a literal `'` no longer
closes the hardcoded apostrophe delimiter early.

The site is a `logger.debug()` call, so the only observable is `caplog` at
DEBUG level -- this module asserts ONLY on strings `typsphinx/translator.py`
itself emits, never on a string emitted by `typsphinx/builder.py`,
`typsphinx/writer.py` or `typsphinx/template_registry.py` (the sibling
`*_path_quoting_gate.py` modules own those). It constructs
`TypstTranslator(mock_document, mock_builder)` directly, mirroring
`tests/test_nested_toctree_paths.py`, because neither
`_compute_relative_include_path` nor `_compute_relative_image_path` touches
`self` beyond `logger` -- no `temp_sphinx_app` / `SphinxTestApp` is needed.
"""

import pytest
from docutils import nodes
from docutils.parsers.rst import states
from docutils.utils import Reporter

from typsphinx.translator import TypstTranslator

RECORD_PREFIX = "Cross-directory path calculation:"


def _single_cross_directory_message(caplog) -> str:
    """Filter `caplog.records` to DEBUG records whose message starts with
    `RECORD_PREFIX`, assert exactly one exists, and return its message."""
    debug_records = [r for r in caplog.records if r.levelname == "DEBUG"]
    cross_directory_records = [
        r for r in debug_records if r.getMessage().startswith(RECORD_PREFIX)
    ]
    assert len(cross_directory_records) == 1, (
        f"Expected exactly one cross-directory debug record, found "
        f"{len(cross_directory_records)}: "
        f"{[r.getMessage() for r in debug_records]}"
    )
    return cross_directory_records[0].getMessage()


@pytest.fixture
def mock_document():
    """Create a mock document for testing, mirroring
    `tests/test_nested_toctree_paths.py`."""
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False
    return doc


@pytest.fixture
def mock_builder():
    """Create a mock builder for testing, mirroring
    `tests/test_nested_toctree_paths.py`."""

    class MockConfig:
        typst_use_mitex = True

    class MockDomains:
        pass

    class MockEnv:
        domains = MockDomains()

    class MockBuilder:
        name = "typst"
        current_docname = None
        config = MockConfig()
        env = MockEnv()

    return MockBuilder()


class TestIncludePathDebugLogQuoting:
    """MSG-06's gate for `_compute_relative_include_path`'s cross-directory
    DEBUG log."""

    def test_apostrophe_in_down_path_does_not_close_the_quote_early(
        self, mock_document, mock_builder, caplog
    ):
        translator = TypstTranslator(mock_document, mock_builder)

        with caplog.at_level("DEBUG"):
            result = translator._compute_relative_include_path(
                "chapter2/o'brien", "chapter1/doc1"
            )

        assert result == "../chapter2/o'brien"
        message = _single_cross_directory_message(caplog)
        assert message == (
            "Cross-directory path calculation: up_count=1, up_path='../', "
            "down_path=\"chapter2/o'brien\", result: ../chapter2/o'brien"
        )

    def test_empty_down_path_renders_two_apostrophes_before_and_after(
        self, mock_document, mock_builder, caplog
    ):
        translator = TypstTranslator(mock_document, mock_builder)

        with caplog.at_level("DEBUG"):
            result = translator._compute_relative_include_path(
                "chapter1", "chapter1/sub/doc"
            )

        assert result == "../"
        message = _single_cross_directory_message(caplog)
        assert message == (
            "Cross-directory path calculation: up_count=1, up_path='../', "
            "down_path='', result: ../"
        )


class TestImagePathDebugLogQuoting:
    """MSG-06's gate for `_compute_relative_image_path`'s cross-directory
    DEBUG log."""

    def test_apostrophe_in_down_path_does_not_close_the_quote_early(
        self, mock_document, mock_builder, caplog
    ):
        translator = TypstTranslator(mock_document, mock_builder)

        with caplog.at_level("DEBUG"):
            result = translator._compute_relative_image_path(
                "images/o'brien.png", "chapter1/doc1"
            )

        assert result == "../images/o'brien.png"
        message = _single_cross_directory_message(caplog)
        assert message == (
            "Cross-directory path calculation: up_count=1, up_path='../', "
            "down_path=\"images/o'brien.png\", result: ../images/o'brien.png"
        )

    def test_empty_down_path_renders_two_apostrophes_before_and_after(
        self, mock_document, mock_builder, caplog
    ):
        translator = TypstTranslator(mock_document, mock_builder)

        with caplog.at_level("DEBUG"):
            result = translator._compute_relative_image_path(
                "chapter1", "chapter1/sub/doc"
            )

        assert result == "../"
        message = _single_cross_directory_message(caplog)
        assert message == (
            "Cross-directory path calculation: up_count=1, up_path='../', "
            "down_path='', result: ../"
        )
