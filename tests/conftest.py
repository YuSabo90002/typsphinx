"""
pytest configuration and fixtures for typsphinx tests.
"""

from pathlib import Path
from typing import Any

import pytest
from docutils import nodes
from sphinx.testing.util import SphinxTestApp

pytest_plugins = "sphinx.testing.fixtures"


@pytest.fixture(scope="session")
def rootdir():
    """Root directory for test files."""
    return Path(__file__).parent.absolute() / "roots"


@pytest.fixture
def sample_doctree() -> nodes.document:
    """Create a sample doctree for testing."""
    from docutils.parsers.rst import states
    from docutils.utils import Reporter

    # Create a minimal reporter for the document
    reporter = Reporter("", 2, 4)

    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False

    section = nodes.section()
    title = nodes.title(text="Test Section")
    section += title
    para = nodes.paragraph(text="Test paragraph")
    section += para
    doc += section
    return doc


@pytest.fixture
def temp_sphinx_app(tmp_path: Path) -> SphinxTestApp:
    """
    Create a temporary Sphinx application for testing.

    Args:
        tmp_path: Pytest temporary path fixture

    Returns:
        SphinxTestApp instance
    """
    srcdir = tmp_path / "source"
    srcdir.mkdir()

    # Create minimal conf.py
    conf_py = srcdir / "conf.py"
    conf_py.write_text(
        "extensions = ['typsphinx']\n"
        "project = 'Test Project'\n"
        "author = 'Test Author'\n"
    )

    # Create minimal index.rst
    index_rst = srcdir / "index.rst"
    index_rst.write_text(
        "Test Document\n" "=============\n" "\n" "This is a test document.\n"
    )

    builddir = tmp_path / "build"

    app = SphinxTestApp(
        srcdir=srcdir,
        builddir=builddir,
    )

    return app


@pytest.fixture
def sphinx_config() -> dict[str, Any]:
    """Sample Sphinx configuration for testing."""
    return {
        "project": "Test Project",
        "author": "Test Author",
        "version": "1.0",
        "release": "1.0.0",
        "typst_documents": [
            ("index", "output.typ", "Test Document", "Test Author"),
        ],
    }


@pytest.fixture
def mock_builder():
    """Create a mock builder for testing."""

    class MockConfig:
        pass

    class MockDomains:
        pass

    class MockEnv:
        domains = MockDomains()

    class MockBuilder:
        config = MockConfig()
        env = MockEnv()

    return MockBuilder()
