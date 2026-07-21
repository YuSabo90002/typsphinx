"""
Tests for configuration reference documentation (Task 16.4)

Requirements tested:
- Requirement 12.5: Configuration documentation
"""

from pathlib import Path

import pytest


def test_configuration_rst_exists():
    """Test that configuration.rst file exists"""
    config_file = Path(__file__).parent.parent / "docs" / "configuration.rst"
    assert config_file.exists(), "docs/configuration.rst should exist"


def test_configuration_has_title():
    """Test that configuration.rst has a proper title"""
    config_file = Path(__file__).parent.parent / "docs" / "configuration.rst"
    content = config_file.read_text()

    # Check for title
    assert "Configuration" in content or "設定" in content
    # Check for RST title underline (==== or -----)
    assert "====" in content or "----" in content


def test_configuration_documents_all_config_values():
    """Test that all config values are documented"""
    config_file = Path(__file__).parent.parent / "docs" / "configuration.rst"
    content = config_file.read_text()

    # All config values that should be documented
    required_configs = [
        "typst_documents",
        "typst_template",
        "typst_template_mapping",
        "typst_toctree_defaults",
        "typst_use_mitex",
        "typst_elements",
        "typst_package",
        "typst_package_imports",
        "typst_template_function",
        "typst_authors",
        "typst_debug",
    ]

    for config in required_configs:
        assert config in content, f"Configuration '{config}' should be documented"


def test_configuration_has_examples():
    """Test that configuration.rst includes usage examples"""
    config_file = Path(__file__).parent.parent / "docs" / "configuration.rst"
    content = config_file.read_text()

    # Should have code blocks
    assert ".. code-block::" in content or "::" in content
    # Should mention conf.py
    assert "conf.py" in content


def test_configuration_has_default_values():
    """Test that default values are documented"""
    config_file = Path(__file__).parent.parent / "docs" / "configuration.rst"
    content = config_file.read_text()

    # Should mention default values
    assert "default" in content.lower() or "デフォルト" in content


def test_configuration_has_sections():
    """Test that configuration.rst has proper section organization"""
    config_file = Path(__file__).parent.parent / "docs" / "configuration.rst"
    content = config_file.read_text()

    # Should have multiple sections (check for multiple title underlines)
    title_markers = ["====", "----", "~~~~", "^^^^"]
    marker_count = sum(content.count(marker) for marker in title_markers)
    assert marker_count >= 3, "Should have at least 3 sections"


def test_configuration_mentions_requirements():
    """Test that configuration.rst mentions system requirements or dependencies"""
    config_file = Path(__file__).parent.parent / "docs" / "configuration.rst"
    content = config_file.read_text()

    # Should mention Sphinx or Typst
    assert "Sphinx" in content or "sphinx" in content
    assert "Typst" in content or "typst" in content


def test_configuration_is_valid_rst():
    """Test that configuration.rst is valid reStructuredText"""
    from docutils.core import publish_string
    from docutils.writers import get_writer_class

    config_file = Path(__file__).parent.parent / "docs" / "configuration.rst"
    content = config_file.read_text()

    # Try to parse as RST - should not raise exception
    try:
        publish_string(
            source=content,
            writer=get_writer_class("html")(),
            settings_overrides={"report_level": 2},  # Only report errors
        )
    except Exception as e:
        pytest.fail(f"configuration.rst is not valid RST: {e}")


def test_configuration_has_troubleshooting():
    """Test that configuration.rst includes troubleshooting guidance"""
    config_file = Path(__file__).parent.parent / "docs" / "configuration.rst"
    content = config_file.read_text()

    # Should have troubleshooting section or common issues
    assert any(
        keyword in content.lower()
        for keyword in [
            "troubleshooting",
            "トラブルシューティング",
            "common issues",
            "よくある問題",
            "faq",
            "tips",
        ]
    ), "Should include troubleshooting or common issues section"


def test_configuration_documents_typst_documents():
    """Test that typst_documents config is properly explained"""
    config_file = Path(__file__).parent.parent / "docs" / "configuration.rst"
    content = config_file.read_text()

    # Should explain the structure of typst_documents
    assert "typst_documents" in content
    # Should show example with tuple structure
    assert any(marker in content for marker in ["(", "tuple", "list"])


def test_configuration_documents_template_options():
    """Test that template-related configs are explained"""
    config_file = Path(__file__).parent.parent / "docs" / "configuration.rst"
    content = config_file.read_text()

    # Should document template configs
    assert "typst_template" in content
    assert "typst_template_mapping" in content
    # Should explain how to use custom templates
    assert any(
        keyword in content.lower()
        for keyword in ["custom", "カスタム", "template", "テンプレート"]
    )
