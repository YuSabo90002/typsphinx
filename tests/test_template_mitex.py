"""
Tests for mitex package integration in templates.

Task 6.1: mitex package integration
Design 3.3: mitex for LaTeX math support
Requirement 4.1: Template must import mitex from Typst Universe

The mitex import lives in the generated shared ``/_typsphinx/deps.typ``
(``typsphinx.typst_deps.render_default_deps()``), which ``base.typ`` imports.
"""

from pathlib import Path

import pytest

from typsphinx.typst_deps import render_default_deps


class TestTemplateMitexIntegration:
    """Test mitex integration in base template."""

    @pytest.fixture
    def template_path(self):
        """Get path to base template."""
        return Path(__file__).parent.parent / "typsphinx" / "templates" / "base.typ"

    @pytest.fixture
    def template_content(self, template_path):
        """Read template content."""
        assert template_path.exists(), "Base template should exist"
        return template_path.read_text()

    @pytest.fixture
    def deps_content(self):
        """The default generated deps.typ text."""
        return render_default_deps()

    def test_template_imports_mitex(self, template_content, deps_content):
        """
        Test that base template imports mitex package.

        Requirement 4.1: Template must import mitex from Typst Universe
        Design 3.3: mitex is used for LaTeX math support
        """
        assert (
            '#import "/_typsphinx/deps.typ": *' in template_content
        ), "Template should import the shared /_typsphinx/deps.typ"
        assert (
            '#import "@preview/mitex' in deps_content
        ), "deps.typ should import mitex package from Typst Universe"

        # Verify version specification
        assert (
            '#import "@preview/mitex:0.2.7": mi, mitex' in deps_content
        ), "mitex import should specify version"

    def test_mitex_import_order(self, deps_content):
        """
        Test that mitex import appears in correct order.

        Order should be:
        1. codly imports (for code highlighting)
        2. mitex imports (for math)
        3. show rules and configurations
        """
        codly_pos = deps_content.find('#import "@preview/codly')
        mitex_pos = deps_content.find('#import "@preview/mitex')

        assert codly_pos != -1, "codly import should exist"
        assert mitex_pos != -1, "mitex import should exist"

        # mitex should come after codly
        assert codly_pos < mitex_pos, "mitex import should appear after codly import"
