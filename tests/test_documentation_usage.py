"""
Tests for usage guide documentation (Task 16.5)

Requirements tested:
- Requirement 12.3: Example projects and documentation
- Requirement 12.5: Configuration documentation
"""

from pathlib import Path

import pytest


def test_usage_rst_exists():
    """Test that usage.rst file exists"""
    usage_file = Path(__file__).parent.parent / "docs" / "usage.rst"
    assert usage_file.exists(), "docs/usage.rst should exist"


def test_usage_has_title():
    """Test that usage.rst has a proper title"""
    usage_file = Path(__file__).parent.parent / "docs" / "usage.rst"
    content = usage_file.read_text()

    # Check for title
    assert "Usage" in content or "使用" in content or "Getting Started" in content
    # Check for RST title underline
    assert "====" in content or "----" in content


def test_usage_has_sphinx_build_examples():
    """Test that usage.rst includes sphinx-build command examples"""
    usage_file = Path(__file__).parent.parent / "docs" / "usage.rst"
    content = usage_file.read_text()

    # Should have sphinx-build command
    assert "sphinx-build" in content
    # Should show -b typst option
    assert "typst" in content.lower()


def test_usage_has_basic_workflow():
    """Test that usage.rst explains basic workflow"""
    usage_file = Path(__file__).parent.parent / "docs" / "usage.rst"
    content = usage_file.read_text()

    # Should mention conf.py
    assert "conf.py" in content
    # Should have code blocks
    assert ".. code-block::" in content or "::" in content


def test_usage_has_common_use_cases():
    """Test that usage.rst includes common use cases"""
    usage_file = Path(__file__).parent.parent / "docs" / "usage.rst"
    content = usage_file.read_text()

    # Should discuss use cases or examples
    assert any(
        keyword in content.lower()
        for keyword in [
            "example",
            "use case",
            "tutorial",
            "例",
            "チュートリアル",
            "使用例",
        ]
    )


def test_usage_mentions_pdf_generation():
    """Test that usage.rst mentions PDF generation"""
    usage_file = Path(__file__).parent.parent / "docs" / "usage.rst"
    content = usage_file.read_text()

    # Should mention PDF or typstpdf
    assert "pdf" in content.lower() or "typstpdf" in content


def test_usage_has_sections():
    """Test that usage.rst has proper section organization"""
    usage_file = Path(__file__).parent.parent / "docs" / "usage.rst"
    content = usage_file.read_text()

    # Should have multiple sections (check for multiple title underlines)
    title_markers = ["====", "----", "~~~~", "^^^^"]
    marker_count = sum(content.count(marker) for marker in title_markers)
    assert marker_count >= 3, "Should have at least 3 sections"


def test_usage_is_valid_rst():
    """Test that usage.rst is valid reStructuredText"""
    from docutils.core import publish_string
    from docutils.writers import get_writer_class

    usage_file = Path(__file__).parent.parent / "docs" / "usage.rst"
    content = usage_file.read_text()

    # Try to parse as RST - should not raise exception
    try:
        publish_string(
            source=content,
            writer=get_writer_class("html")(),
            settings_overrides={"report_level": 2},  # Only report errors
        )
    except Exception as e:
        pytest.fail(f"usage.rst is not valid RST: {e}")


def test_usage_links_to_configuration():
    """Test that usage.rst references configuration documentation"""
    usage_file = Path(__file__).parent.parent / "docs" / "usage.rst"
    content = usage_file.read_text()

    # Should reference configuration.rst
    assert "configuration" in content.lower()


def test_usage_links_to_examples():
    """Test that usage.rst references example projects"""
    usage_file = Path(__file__).parent.parent / "docs" / "usage.rst"
    content = usage_file.read_text()

    # Should mention examples
    assert "example" in content.lower()


def test_usage_has_quickstart():
    """Test that usage.rst includes a quickstart section"""
    usage_file = Path(__file__).parent.parent / "docs" / "usage.rst"
    content = usage_file.read_text()

    # Should have quickstart or getting started
    assert any(
        keyword in content.lower()
        for keyword in [
            "quick start",
            "quickstart",
            "getting started",
            "クイックスタート",
            "はじめに",
        ]
    )


def test_usage_shows_typst_builder():
    """Test that usage.rst demonstrates typst builder usage"""
    usage_file = Path(__file__).parent.parent / "docs" / "usage.rst"
    content = usage_file.read_text()

    # Should show -b typst
    assert "-b typst" in content or "-b typstpdf" in content
