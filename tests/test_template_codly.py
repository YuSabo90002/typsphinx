"""
Tests for codly package integration in templates.

Task 4.2.1: Template codly integration (forced usage)
Design: design.md 3.5 - codly forced usage for all code blocks
Requirement 7.4: codly package integration for code highlighting

The codly imports and initialisation live in the generated shared
``/_typsphinx/deps.typ`` (``typsphinx.typst_deps.render_default_deps()``);
the bundled ``base.typ`` imports that file, and every content file and
wrapper applies ``#show: typsphinx-init``.
"""

from pathlib import Path

import pytest

from typsphinx.typst_deps import render_default_deps


class TestTemplateCodelyIntegration:
    """Test codly integration in base template and the shared deps.typ."""

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

    def test_template_imports_codly(self, template_content, deps_content):
        """
        Test that base template imports codly package (through deps.typ).

        Requirement 7.4: Template must import codly from Typst Universe
        Design 3.5: codly is mandatory for all code blocks
        """
        assert (
            '#import "/_typsphinx/deps.typ": *' in template_content
        ), "Template should import the shared /_typsphinx/deps.typ"
        assert (
            '#import "@preview/codly:1.3.0": *' in deps_content
        ), "deps.typ should import codly 1.3.0 from Typst Universe"

    def test_template_imports_codly_languages(self, deps_content):
        """
        Test that deps.typ imports codly-languages package.

        Requirement 7.4: Template must import codly-languages for language definitions
        Design 3.5: codly-languages provides comprehensive language support
        """
        assert (
            '#import "@preview/codly-languages:0.1.10": *' in deps_content
        ), "deps.typ should import codly-languages 0.1.10 from Typst Universe"

    def test_template_initializes_codly(self, deps_content):
        """
        Test that typsphinx-init initializes codly.

        Requirement 7.4: codly must be initialized with a show rule
        Design 3.5: codly-init must be called before code blocks
        """
        assert (
            "show: codly-init.with()" in deps_content
        ), "typsphinx-init should initialize codly with show: codly-init"

    def test_template_configures_codly(self, deps_content):
        """
        Test that typsphinx-init configures codly.

        Requirement 7.4: Template should configure codly settings
        Design 3.5: Default configuration with codly-languages
        """
        assert (
            "codly(languages: codly-languages)" in deps_content
        ), "codly configuration should use codly-languages for language definitions"

    def test_codly_setup_before_body(self, template_content, deps_content):
        """
        Test that codly setup occurs before document body.

        Requirement 7.4: codly must be imported and initialized before body content.
        The template imports deps.typ before defining its project function,
        and typsphinx-init sets up codly before yielding the body.
        """
        import_pos = template_content.find('#import "/_typsphinx/deps.typ"')
        project_pos = template_content.find("#let project(")
        assert import_pos != -1, "deps.typ import should exist"
        assert project_pos != -1, "project function should exist"
        assert (
            import_pos < project_pos
        ), "deps.typ import should appear before project function definition"

        init_def_pos = deps_content.find("#let typsphinx-init(body)")
        init_pos = deps_content.find("show: codly-init")
        body_pos = deps_content.find("  body\n")
        assert -1 < init_def_pos < init_pos < body_pos

    def test_codly_configuration_order(self, deps_content):
        """
        Test that codly configuration appears in correct order in deps.typ.

        Expected order:
        1. #import "@preview/codly:1.3.0"
        2. #import "@preview/codly-languages:0.1.10"
        3. show: codly-init.with()
        4. codly(languages: codly-languages)
        """
        codly_import_pos = deps_content.find('#import "@preview/codly:1.3.0')
        languages_import_pos = deps_content.find(
            '#import "@preview/codly-languages:0.1.10'
        )
        init_pos = deps_content.find("show: codly-init")
        config_pos = deps_content.find("codly(languages: codly-languages)")

        assert codly_import_pos != -1, "codly import should exist"
        assert languages_import_pos != -1, "codly-languages import should exist"
        assert init_pos != -1, "codly-init should exist"
        assert config_pos != -1, "codly configuration should exist"

        # Verify order
        assert (
            codly_import_pos < languages_import_pos
        ), "codly import must appear before codly-languages import"
        assert (
            languages_import_pos < init_pos
        ), "codly-languages import must appear before codly-init"
        assert (
            init_pos < config_pos
        ), "codly-init must appear before codly configuration"
