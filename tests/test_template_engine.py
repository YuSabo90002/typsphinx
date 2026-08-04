"""Tests for TemplateEngine (Requirement 8)"""

from pathlib import Path

import pytest

from typsphinx.template_engine import TemplateEngine


class TestTemplateLoading:
    """Test template loading and management (Task 9.1)"""

    def test_load_default_template(self):
        """Test loading the default Typst template"""
        engine = TemplateEngine()
        template = engine.load_template()

        # Default template should exist and contain basic structure
        assert template is not None
        assert isinstance(template, str)
        assert "#let project" in template  # Should define a project function
        assert "body" in template  # Should accept body parameter

    def test_load_custom_template_from_path(self, tmp_path):
        """Test loading a custom template from specified path"""
        # Create custom template
        custom_template_path = tmp_path / "custom.typ"
        custom_template_path.write_text(
            '#let custom(title: "", body) = {\n'
            "  text(2em)[#title]\n"
            "  body\n"
            "}\n"
        )

        engine = TemplateEngine(template_path=str(custom_template_path))
        template = engine.load_template()

        assert "#let custom" in template
        assert "title:" in template

    def test_load_template_from_sphinx_project_directory(self, tmp_path):
        """Test template search in Sphinx project directory"""
        # Create Sphinx-like directory structure
        project_dir = tmp_path / "docs"
        templates_dir = project_dir / "_templates" / "typst"
        templates_dir.mkdir(parents=True)

        custom_template = templates_dir / "custom.typ"
        custom_template.write_text("#let project() = {}")

        engine = TemplateEngine(
            template_name="custom.typ", search_paths=[str(templates_dir)]
        )
        template = engine.load_template()

        assert template is not None
        assert "#let project" in template

    def test_template_search_priority(self, tmp_path):
        """Test that user template directory has priority over default"""
        # Create two templates with different content
        user_dir = tmp_path / "user_templates"
        user_dir.mkdir()
        user_template = user_dir / "base.typ"
        user_template.write_text("#let project() = { /* user template */ }")

        default_dir = tmp_path / "default_templates"
        default_dir.mkdir()
        default_template = default_dir / "base.typ"
        default_template.write_text("#let project() = { /* default template */ }")

        # User directory should be searched first
        engine = TemplateEngine(
            template_name="base.typ", search_paths=[str(user_dir), str(default_dir)]
        )
        template = engine.load_template()

        assert "user template" in template
        assert "default template" not in template

    def test_template_not_found_fallback_to_default(self, tmp_path):
        """Test fallback to default template when custom template not found"""
        engine = TemplateEngine(template_path="/nonexistent/template.typ")

        # Should fall back to default template without raising error
        template = engine.load_template()
        assert template is not None
        assert "#let project" in template  # Default template content

    def test_template_not_found_warning(self, tmp_path, caplog):
        """Test that warning is logged when custom template not found"""
        import logging

        caplog.set_level(logging.WARNING)

        engine = TemplateEngine(template_path="/nonexistent/template.typ")
        template = engine.load_template()

        # Should log a warning
        assert any(
            "template" in record.message.lower()
            and "not found" in record.message.lower()
            for record in caplog.records
        )

    def test_get_default_template_path(self):
        """Test getting the path to default template"""
        engine = TemplateEngine()
        default_path = engine.get_default_template_path()

        assert default_path is not None
        assert Path(default_path).exists()
        assert Path(default_path).suffix == ".typ"


class TestTemplateResolutionProvenance:
    """CONF-07/D-06: resolve_template()/TemplateResolution record WHICH
    priority resolved, and uses_bundled_default_template() is the single
    judgment predicate built on top of that provenance. See
    27.1-CONTEXT.md D-06."""

    def test_resolve_template_explicit_source(self, tmp_path):
        """An engine built with an existing explicit template_path reports
        source 'explicit'."""
        custom_template_path = tmp_path / "custom.typ"
        custom_template_path.write_text("#let custom(body) = { body }")

        engine = TemplateEngine(template_path=str(custom_template_path))
        resolution = engine.resolve_template()

        assert resolution.source == "explicit"
        assert "#let custom" in resolution.content
        assert resolution.content == engine.load_template()

    def test_resolve_template_search_source(self, tmp_path):
        """An engine built with template_path=None and a search_paths
        directory that contains base.typ reports source 'search' -- the
        <srcdir>/base.typ shadow case."""
        srcdir = tmp_path / "docs"
        srcdir.mkdir()
        (srcdir / "base.typ").write_text("#let project(body) = { /* shadow */ }")

        engine = TemplateEngine(search_paths=[str(srcdir)])
        resolution = engine.resolve_template()

        assert resolution.source == "search"
        assert "shadow" in resolution.content
        assert resolution.content == engine.load_template()

    def test_resolve_template_default_source(self):
        """An engine built with template_path=None and no matching
        search-path file reports source 'default'."""
        engine = TemplateEngine()
        resolution = engine.resolve_template()

        assert resolution.source == "default"
        assert "#let project" in resolution.content
        assert resolution.content == engine.load_template()

    def test_resolve_template_fallthrough_reports_actual_source(self, tmp_path):
        """An engine built with a template_path that does NOT exist falls
        through exactly as today (warning emitted) and reports whichever
        later priority actually supplied the content."""
        engine = TemplateEngine(template_path="/nonexistent/template.typ")
        resolution = engine.resolve_template()

        assert resolution.source == "default"
        assert "#let project" in resolution.content

    def test_srcdir_shadow_reports_search_and_not_bundled_default(self, tmp_path):
        """The <srcdir>/base.typ shadow case reports 'search' and
        uses_bundled_default_template() is therefore False (D-06's central
        judgment boundary)."""
        srcdir = tmp_path / "docs"
        srcdir.mkdir()
        (srcdir / "base.typ").write_text("#let project(body) = { /* shadow */ }")

        engine = TemplateEngine(search_paths=[str(srcdir)])

        assert engine.resolve_template().source == "search"
        assert engine.uses_bundled_default_template() is False

    def test_package_configured_engine_never_uses_bundled_default(self):
        """uses_bundled_default_template() is False for an engine
        constructed with a typst_package even though its own priority walk
        would resolve to 'default' (template_path=None, no search hit)."""
        engine = TemplateEngine(typst_package="@preview/charged-ieee:0.1.4")

        assert engine.resolve_template().source == "default"
        assert engine.uses_bundled_default_template() is False

    def test_bare_engine_uses_bundled_default_template(self):
        """uses_bundled_default_template() is True for a bare engine with no
        template_path, no matching search path, and no package."""
        engine = TemplateEngine()

        assert engine.uses_bundled_default_template() is True

    def test_explicit_template_engine_does_not_use_bundled_default(self, tmp_path):
        """uses_bundled_default_template() is False for an engine with an
        explicit, existing template_path."""
        custom_template_path = tmp_path / "custom.typ"
        custom_template_path.write_text("#let custom(body) = { body }")

        engine = TemplateEngine(template_path=str(custom_template_path))

        assert engine.uses_bundled_default_template() is False


class TestParameterMapping:
    """Test Sphinx metadata to template parameter mapping (Task 9.2)"""

    def test_map_basic_sphinx_metadata(self):
        """Test mapping basic Sphinx metadata (project, author, release)"""
        engine = TemplateEngine()

        sphinx_metadata = {
            "project": "My Project",
            "author": "John Doe",
            "release": "1.0.0",
            "copyright": "2024, John Doe",
        }

        params = engine.map_parameters(sphinx_metadata)

        assert params["title"] == "My Project"
        assert params["authors"] == ("John Doe",)
        assert params["date"] == "1.0.0"

    def test_map_parameters_with_default_values(self):
        """Test that default values are provided when metadata is missing"""
        engine = TemplateEngine()

        sphinx_metadata = {}  # Empty metadata

        params = engine.map_parameters(sphinx_metadata)

        # Should have default values
        assert "title" in params
        assert "authors" in params
        assert params["title"] == ""
        assert params["authors"] == ()

    def test_map_parameters_with_multiple_authors(self):
        """Test mapping when author is a comma-separated string"""
        engine = TemplateEngine()

        sphinx_metadata = {
            "project": "My Project",
            "author": "John Doe, Jane Smith, Bob Wilson",
        }

        params = engine.map_parameters(sphinx_metadata)

        # Should convert to tuple of authors
        assert params["authors"] == ("John Doe", "Jane Smith", "Bob Wilson")

    def test_map_parameters_custom_mapping(self):
        """Test custom parameter mapping from user config"""
        # Custom mapping: Sphinx name -> Template parameter name
        custom_mapping = {
            "project": "doc_title",
            "author": "doc_authors",
            "release": "version",
        }

        engine = TemplateEngine(parameter_mapping=custom_mapping)

        sphinx_metadata = {
            "project": "My Project",
            "author": "John Doe",
            "release": "1.0.0",
        }

        params = engine.map_parameters(sphinx_metadata)

        # Should use custom parameter names
        assert params["doc_title"] == "My Project"
        assert params["doc_authors"] == ("John Doe",)
        assert params["version"] == "1.0.0"

    def test_map_parameters_complex_structures(self):
        """Test mapping to complex structures (arrays, dicts)"""
        engine = TemplateEngine()

        sphinx_metadata = {
            "project": "My Project",
            "author": "John Doe",
            "html_theme_options": {
                "logo": "logo.png",
                "github_url": "https://github.com/user/repo",
            },
        }

        params = engine.map_parameters(sphinx_metadata)

        # Basic mapping should work
        assert params["title"] == "My Project"

        # Complex structures should be preserved or transformed
        # (Implementation may vary based on requirements)

    def test_map_parameters_standard_defaults(self):
        """Test standard mapping applies default transformations"""
        engine = TemplateEngine()

        sphinx_metadata = {
            "project": "Test Project",
            "author": "Author Name",
            "version": "0.1",
            "release": "0.1.0",
        }

        params = engine.map_parameters(sphinx_metadata)

        # Standard mapping should be applied
        assert "title" in params
        assert "authors" in params
        assert "date" in params


class TestPackagePathParameterSuppression:
    """Test D-05: package-configured engines do not receive injected default
    parameters (title/authors/date) unless explicitly mapped (BUG-B)."""

    def test_package_engine_no_explicit_mapping_returns_empty_dict(self):
        """A package-configured engine with no explicit mapping returns {}"""
        engine = TemplateEngine(typst_package="@preview/charged-ieee:0.1.4")

        sphinx_metadata = {
            "project": "P",
            "author": "A",
            "release": "1.0",
            "copyright": "c",
        }

        params = engine.map_parameters(sphinx_metadata)

        assert params == {}

    def test_package_engine_explicit_single_key_mapping_returns_only_that_key(self):
        """A package-configured engine with an explicit mapping returns exactly
        the mapped key(s), with no back-filled title/authors/date"""
        engine = TemplateEngine(
            typst_package="@preview/charged-ieee:0.1.4",
            parameter_mapping={"project": "title"},
        )

        sphinx_metadata = {
            "project": "P",
            "author": "A",
            "release": "1.0",
            "copyright": "c",
        }

        params = engine.map_parameters(sphinx_metadata)

        assert set(params.keys()) == {"title"}
        assert params["title"] == "P"

    def test_non_package_engine_still_backfills_title_authors_date(self):
        """A non-package engine's map_parameters() is untouched by D-05 --
        the template path still back-fills the three standard keys"""
        engine = TemplateEngine()

        sphinx_metadata = {
            "project": "P",
            "author": "A",
            "release": "1.0",
            "copyright": "c",
        }

        params = engine.map_parameters(sphinx_metadata)

        assert params["title"] == "P"
        assert params["authors"] == ("A",)
        assert params["date"] == "1.0"


class TestEssentialImportHoist:
    """Test D-02: every master's render() output carries the four essential
    @preview imports plus codly initialisation exactly once, whether or not a
    template file is imported (BUG-F)."""

    def test_package_only_render_contains_essential_imports_exactly_once(self):
        """A package-only render (no template_file) carries the essential
        imports and codly-init exactly once"""
        engine = TemplateEngine(
            typst_package="@preview/charged-ieee:0.1.4",
            typst_template_function="ieee",
        )

        params = {}
        body = "= Body\n"

        result = engine.render(params, body)

        assert "#show: codly-init.with()" in result
        assert result.count("@preview/codly:") == 1
        assert result.count("@preview/codly-languages:") == 1
        assert result.count("@preview/mitex:") == 1
        assert result.count("@preview/gentle-clues:") == 1

    def test_template_file_render_does_not_duplicate_essential_imports(self):
        """A template-file-set render carries the essential imports exactly
        once -- proving the D-02 hoist did not duplicate the block"""
        engine = TemplateEngine()

        params = {"title": "T", "authors": ()}
        body = "= Body\n"

        result = engine.render(params, body, template_file="_template.typ")

        assert result.count("@preview/mitex:") == 1
        assert result.count("@preview/codly:") == 1
        assert result.count("@preview/codly-languages:") == 1
        assert result.count("@preview/gentle-clues:") == 1

    def test_inline_default_template_render_does_not_duplicate_essential_imports(self):
        """CR-01: the inline-default-template path (no template_file AND no
        typst_package -- render()'s documented "old behavior") appends the whole
        of templates/base.typ, which already carries these imports and
        show-rules. The D-02 hoist must not emit them a second time there.

        Counting matters: the pre-existing tests on this path only asserted the
        markers were PRESENT, so a doubled emission stayed green.
        """
        engine = TemplateEngine()

        result = engine.render({"title": "T", "authors": ()}, "= Body\n")

        assert result.count("@preview/codly:") == 1
        assert result.count("@preview/codly-languages:") == 1
        assert result.count("@preview/mitex:") == 1
        assert result.count("@preview/gentle-clues:") == 1
        assert result.count("#show: codly-init.with()") == 1
        assert result.count("#codly(languages: codly-languages)") == 1


class TestTypstUniversePackages:
    """Test Typst Universe package template support (Task 9.3)"""

    def test_generate_package_import(self):
        """Test generating import statement for Typst Universe package"""
        engine = TemplateEngine(
            typst_package="@preview/charged-ieee:0.1.0", typst_template_function="ieee"
        )

        import_statement = engine.generate_package_import()

        assert import_statement is not None
        assert "#import" in import_statement
        assert "@preview/charged-ieee:0.1.0" in import_statement

    def test_generate_package_import_with_items(self):
        """Test generating import with specific items"""
        engine = TemplateEngine(
            typst_package="@preview/charged-ieee:0.1.0",
            typst_template_function="ieee",
            typst_package_imports=["ieee", "conference"],
        )

        import_statement = engine.generate_package_import()

        assert "#import" in import_statement
        assert "ieee" in import_statement
        assert "conference" in import_statement

    def test_no_package_import_when_not_specified(self):
        """Test that no import is generated when package not specified"""
        engine = TemplateEngine()

        import_statement = engine.generate_package_import()

        assert import_statement is None or import_statement == ""

    def test_template_function_call_generation(self):
        """Test generating template function call from package"""
        engine = TemplateEngine(
            typst_package="@preview/charged-ieee:0.1.0", typst_template_function="ieee"
        )

        # This should be used in render() method
        assert engine.typst_template_function_name == "ieee"

    def test_package_version_parsing(self):
        """Test parsing package name and version"""
        engine = TemplateEngine(typst_package="@preview/my-template:1.2.3")

        # Should be able to extract package info
        assert "@preview/my-template:1.2.3" in engine.generate_package_import()


class TestToctreeOutlineIntegration:
    """Test toctree to #outline() integration (Task 9.4)"""

    def test_extract_toctree_options_from_doctree(self):
        """Test extracting toctree options from doctree"""
        from docutils import nodes
        from docutils.parsers.rst import states
        from docutils.utils import Reporter
        from sphinx import addnodes

        # Create doctree with toctree
        reporter = Reporter("", 2, 4)
        doctree = nodes.document("", reporter=reporter)
        doctree.settings = states.Struct()

        toctree = addnodes.toctree()
        toctree["maxdepth"] = 3
        toctree["numbered"] = True
        toctree["caption"] = "Table of Contents"
        doctree += toctree

        engine = TemplateEngine()
        options = engine.extract_toctree_options(doctree)

        assert options["toctree_maxdepth"] == 3
        assert options["toctree_numbered"] is True
        assert options["toctree_caption"] == "Table of Contents"

    def test_extract_toctree_options_defaults(self):
        """Test default values when toctree options not specified"""
        from docutils import nodes
        from docutils.parsers.rst import states
        from docutils.utils import Reporter
        from sphinx import addnodes

        # Create doctree with toctree but no options
        reporter = Reporter("", 2, 4)
        doctree = nodes.document("", reporter=reporter)
        doctree.settings = states.Struct()

        toctree = addnodes.toctree()
        doctree += toctree

        engine = TemplateEngine()
        options = engine.extract_toctree_options(doctree)

        # Should have default values
        assert "toctree_maxdepth" in options
        assert "toctree_numbered" in options
        assert "toctree_caption" in options
        assert options["toctree_maxdepth"] == 2  # Default
        assert options["toctree_numbered"] is False  # Default

    def test_extract_toctree_options_no_toctree(self):
        """Test when doctree has no toctree node"""
        from docutils import nodes
        from docutils.parsers.rst import states
        from docutils.utils import Reporter

        # Create doctree without toctree
        reporter = Reporter("", 2, 4)
        doctree = nodes.document("", reporter=reporter)
        doctree.settings = states.Struct()

        section = nodes.section()
        doctree += section

        engine = TemplateEngine()
        options = engine.extract_toctree_options(doctree)

        # Should return empty dict or defaults
        assert isinstance(options, dict)

    def test_toctree_options_passed_to_parameters(self):
        """Test that toctree options are added to template parameters"""
        from docutils import nodes
        from docutils.parsers.rst import states
        from docutils.utils import Reporter
        from sphinx import addnodes

        # Create doctree with toctree
        reporter = Reporter("", 2, 4)
        doctree = nodes.document("", reporter=reporter)
        doctree.settings = states.Struct()

        toctree = addnodes.toctree()
        toctree["maxdepth"] = 4
        toctree["numbered"] = True
        toctree["caption"] = "Contents"
        doctree += toctree

        engine = TemplateEngine()

        # Extract toctree options
        toctree_options = engine.extract_toctree_options(doctree)

        # Merge with standard parameters
        sphinx_metadata = {"project": "Test", "author": "Author"}
        params = engine.map_parameters(sphinx_metadata)
        params.update(toctree_options)

        # Should have both standard and toctree parameters
        assert params["title"] == "Test"
        assert params["toctree_maxdepth"] == 4
        assert params["toctree_numbered"] is True
        assert params["toctree_caption"] == "Contents"

    def test_toctree_maxdepth_unlimited_conversion(self):
        """Test that maxdepth=-1 is converted to None for Typst"""
        from docutils import nodes
        from docutils.parsers.rst import states
        from docutils.utils import Reporter
        from sphinx import addnodes

        # Create doctree with maxdepth=-1 (unlimited)
        reporter = Reporter("", 2, 4)
        doctree = nodes.document("", reporter=reporter)
        doctree.settings = states.Struct()

        toctree = addnodes.toctree()
        toctree["maxdepth"] = -1  # Unlimited depth in Sphinx
        toctree["numbered"] = False
        doctree += toctree

        engine = TemplateEngine()
        options = engine.extract_toctree_options(doctree)

        # Should convert -1 to None for Typst
        assert options["toctree_maxdepth"] is None

    def test_toctree_numbered_zero_conversion(self):
        """Test that numbered=0 is converted to false for Typst"""
        from docutils import nodes
        from docutils.parsers.rst import states
        from docutils.utils import Reporter
        from sphinx import addnodes

        # Create doctree with numbered=0 (not numbered in Sphinx)
        reporter = Reporter("", 2, 4)
        doctree = nodes.document("", reporter=reporter)
        doctree.settings = states.Struct()

        toctree = addnodes.toctree()
        toctree["maxdepth"] = 2
        toctree["numbered"] = 0  # Not numbered
        doctree += toctree

        engine = TemplateEngine()
        options = engine.extract_toctree_options(doctree)

        # Should convert 0 to False (boolean)
        assert options["toctree_numbered"] is False

    def test_toctree_numbered_positive_conversion(self):
        """Test that numbered>0 is converted to true for Typst"""
        from docutils import nodes
        from docutils.parsers.rst import states
        from docutils.utils import Reporter
        from sphinx import addnodes

        # Create doctree with numbered=3 (numbered depth in Sphinx)
        reporter = Reporter("", 2, 4)
        doctree = nodes.document("", reporter=reporter)
        doctree.settings = states.Struct()

        toctree = addnodes.toctree()
        toctree["maxdepth"] = 2
        toctree["numbered"] = 3  # Numbered with depth 3
        doctree += toctree

        engine = TemplateEngine()
        options = engine.extract_toctree_options(doctree)

        # Should convert positive int to True (boolean)
        assert options["toctree_numbered"] is True


class TestTemplateRendering:
    """Test template rendering and integration (Task 9.5)"""

    def test_render_with_default_template(self):
        """Test rendering document with default template"""
        engine = TemplateEngine()

        # Prepare parameters
        params = {
            "title": "Test Document",
            "authors": ("Test Author",),
            "date": "2024-01-01",
            "toctree_maxdepth": 2,
            "toctree_numbered": False,
            "toctree_caption": "Contents",
            "papersize": "a4",
            "fontsize": "11pt",
        }

        # Body content (Typst markup)
        body = "= Chapter 1\n\nThis is the content.\n"

        # Render
        result = engine.render(params, body)

        # Should contain template function call
        assert "#show: project.with(" in result
        assert 'title: "Test Document"' in result
        assert 'authors: ("Test Author",)' in result

        # Should contain body
        assert body in result

    def test_render_with_typst_universe_package(self):
        """Test rendering with external Typst Universe package"""
        engine = TemplateEngine(
            typst_package="@preview/charged-ieee:0.1.0", typst_template_function="ieee"
        )

        params = {
            "title": "IEEE Paper",
            "authors": ("Author One",),
        }
        body = "= Introduction\n\nContent here.\n"

        result = engine.render(params, body)

        # Should have import statement
        assert '#import "@preview/charged-ieee:0.1.0": ieee' in result

        # Should use template function from package
        assert "#show: ieee.with(" in result

    def test_render_with_paper_size_and_font_settings(self):
        """Test that paper size and font settings are included"""
        engine = TemplateEngine()

        params = {
            "title": "Document",
            "authors": (),
            "papersize": "letter",
            "fontsize": "12pt",
        }
        body = "Content"

        result = engine.render(params, body)

        assert 'papersize: "letter"' in result
        # fontsize is a string, so it's quoted
        assert 'fontsize: "12pt"' in result

    def test_render_formats_parameters_correctly(self):
        """Test that parameters are formatted correctly for Typst"""
        engine = TemplateEngine()

        params = {
            "title": "My Title",
            "authors": ("Author 1", "Author 2", "Author 3"),
            "date": "2024",
            "toctree_numbered": True,
        }
        body = "Content"

        result = engine.render(params, body)

        # Authors should be formatted as tuple (with trailing comma for Typst)
        assert 'authors: ("Author 1", "Author 2", "Author 3",)' in result

        # Boolean should be lowercase
        assert "toctree_numbered: true" in result

    def test_render_handles_special_characters_in_strings(self):
        """Test that special characters in parameters are escaped"""
        engine = TemplateEngine()

        params = {
            "title": 'Title with "quotes" and \\backslash',
            "authors": (),
        }
        body = "Content"

        result = engine.render(params, body)

        # Should escape quotes and backslashes
        # Typst uses standard escape sequences
        assert result is not None

    def test_render_with_empty_body(self):
        """Test rendering with empty body content"""
        engine = TemplateEngine()

        params = {"title": "Empty Doc", "authors": ()}
        body = ""

        result = engine.render(params, body)

        assert "#show: project.with(" in result
        # Empty body should still be valid


class TestTypstTemplateFunctionDictFormat:
    """Test typst_template_function dictionary format support (Issue #13)"""

    def test_typst_template_function_string_format(self):
        """Test backward compatibility: string format for template function"""
        engine = TemplateEngine(typst_template_function="project")

        params = {"title": "Test", "authors": ()}
        body = "Content"

        result = engine.render(params, body)

        # Should use string format function name
        assert "#show: project.with(" in result

    def test_typst_template_function_dict_format_basic(self):
        """Test dictionary format: basic case with name only"""
        engine = TemplateEngine(typst_template_function={"name": "ieee"})

        params = {"title": "Test", "authors": ()}
        body = "Content"

        result = engine.render(params, body)

        # Should use function name from dictionary
        assert "#show: ieee.with(" in result

    def test_typst_template_function_dict_format_with_params(self):
        """Test dictionary format: with additional template parameters"""
        engine = TemplateEngine(
            typst_template_function={
                "name": "ieee",
                "params": {
                    "abstract": "This paper presents novel approaches.",
                    "index-terms": ["AI", "Machine Learning"],
                    "paper-size": "a4",
                },
            }
        )

        params = {"title": "Test", "authors": ()}
        body = "Content"

        result = engine.render(params, body)

        # Should use function name from dictionary
        assert "#show: ieee.with(" in result

        # Should include template-specific parameters
        assert 'abstract: "This paper presents novel approaches."' in result
        assert 'index-terms: ("AI", "Machine Learning",)' in result
        assert 'paper-size: "a4"' in result

    def test_template_params_python_variable_reference(self):
        """Test that Python variables can be referenced in params (no special syntax needed)"""
        # Simulate conf.py variables
        ieee_abstract = "This is the abstract text."
        ieee_keywords = ["Keyword1", "Keyword2"]

        # User would write this in conf.py
        engine = TemplateEngine(
            typst_template_function={
                "name": "ieee",
                "params": {
                    "abstract": ieee_abstract,  # Direct Python variable reference
                    "index-terms": ieee_keywords,
                },
            }
        )

        params = {"title": "Test", "authors": ()}
        body = "Content"

        result = engine.render(params, body)

        # Should contain the referenced values
        assert 'abstract: "This is the abstract text."' in result
        assert 'index-terms: ("Keyword1", "Keyword2",)' in result

    def test_explicit_template_function_params_win_on_colliding_key(self):
        """D-08: explicit typst_template_function['params'] values beat
        auto-derived Sphinx metadata on a colliding key (BUG-E)"""
        engine = TemplateEngine(
            typst_template_function={
                "name": "ieee",
                "params": {"title": "Explicit Title"},
            }
        )

        params = {"title": "Auto Derived Title", "authors": ()}
        body = "Content"

        result = engine.render(params, body)

        assert 'title: "Explicit Title"' in result
        assert 'title: "Auto Derived Title"' not in result

    def test_colliding_key_emission_is_deterministic_and_single(self):
        """D-08 (edge/ordering, CONF-02): the colliding key is emitted exactly
        once, and repeated renders of identical inputs are byte-identical"""
        engine = TemplateEngine(
            typst_template_function={
                "name": "ieee",
                "params": {"title": "Explicit Title"},
            }
        )

        params = {"title": "Auto Derived Title", "authors": ()}
        body = "Content"

        result_1 = engine.render(params, body)
        result_2 = engine.render(params, body)

        assert result_1 == result_2

        # Scope the count to the emitted call region (between the #show:
        # line and its closing paren), not the whole document.
        call_start = result_1.index("#show: ieee.with(")
        call_end = result_1.index(")", call_start)
        call_region = result_1[call_start:call_end]
        assert call_region.count("title:") == 1


class TestTypstAuthorsConfig:
    """Test typst_authors configuration for detailed author information (Issue #13)"""

    def test_author_config_backward_compatibility(self):
        """Test backward compatibility: traditional author string format"""
        engine = TemplateEngine()

        # Traditional Sphinx author configuration
        authors = ("John Doe", "Jane Smith")
        formatted = engine._format_typst_value(authors)

        # Should produce string tuple format
        assert formatted == '("John Doe", "Jane Smith",)'

    def test_typst_authors_through_pipeline_produces_native_array_of_dicts(self):
        """D-07/D-05: typst_authors reaches map_parameters()/render() as a
        native list[dict], never as a pre-rendered quoted string (BUG-C).

        CONF-09 (Phase 44.2, D-05): the `typst_authors` block was moved to
        run BEFORE the mapping loop instead of after it, so a mapped author
        value now overwrites the typst_authors seed on every route where
        "author" is an active `parameter_mapping` key -- which this test's
        PREVIOUS shape was (the default mapping maps "author", so
        `params["authors"]` ended up as the mapping loop's authors-tuple,
        not the typst_authors list[dict], measured RED this session:
        `isinstance(('Ada Lovelace',), list)` is False).

        typst_authors remains authoritative ONLY on a route where "author"
        is NOT an active mapping key -- the package-alone route with a
        custom mapping that omits "author", matching
        tests/fixtures/package_only_config_gate/conf.py's own shape. This
        test now exercises exactly that route so it still pins what it
        exists to pin: typst_authors reaches render() as a native array of
        dictionaries and never as a quoted string (the double-formatting
        regression guard below is unchanged)."""
        engine = TemplateEngine(
            typst_package="@preview/charged-ieee:0.1.4",
            parameter_mapping={"project": "title"},
            typst_authors={
                "Ada Lovelace": {
                    "department": "Computing",
                    "organization": "Analytical Engine Society",
                    "email": "ada@example.org",
                }
            },
        )

        sphinx_metadata = {
            "project": "P",
            "author": "Ada Lovelace",
            "release": "1.0",
            "copyright": "c",
        }

        params = engine.map_parameters(sphinx_metadata)

        assert isinstance(params["authors"], list)
        assert isinstance(params["authors"][0], dict)
        assert list(params["authors"][0].keys())[0] == "name"
        assert params["authors"][0]["name"] == "Ada Lovelace"

        body = "Content"
        result = engine.render(params, body)

        assert 'name: "Ada Lovelace"' in result
        assert "authors: (" in result
        # Double-formatting regression guard: authors must never be emitted
        # as a quoted Typst string.
        assert 'authors: "(' not in result

    def test_typst_authors_unset_or_empty_yields_no_authors_key_on_package_path(self):
        """A package-configured engine with no typst_authors produces no
        authors key; an empty typst_authors dict behaves identically"""
        sphinx_metadata = {
            "project": "P",
            "author": "A",
            "release": "1.0",
            "copyright": "c",
        }

        engine_unset = TemplateEngine(typst_package="@preview/charged-ieee:0.1.4")
        params_unset = engine_unset.map_parameters(sphinx_metadata)
        assert "authors" not in params_unset

        engine_empty = TemplateEngine(
            typst_package="@preview/charged-ieee:0.1.4", typst_authors={}
        )
        params_empty = engine_empty.map_parameters(sphinx_metadata)
        assert "authors" not in params_empty


class TestTypstElementsPassThrough:
    """CONF-04: `typst_elements` (papersize/fontsize) reach `map_parameters()`
    / `_format_typst_value()` with correct per-key emission typing, a
    fail-loud unknown-key raise, and structural non-leak of baseline Sphinx
    metadata (e.g. copyright). See 26-CONTEXT.md D-01..D-09."""

    def test_format_typst_value_raw_typst_emits_unquoted(self):
        """_format_typst_value(RawTypst("20pt")) returns the bare string
        `20pt` -- no surrounding quotes (D-02)."""
        from typsphinx.template_engine import RawTypst

        engine = TemplateEngine()
        formatted = engine._format_typst_value(RawTypst("20pt"))

        assert formatted == "20pt"
        assert '"' not in formatted

    def test_format_typst_value_str_unchanged(self):
        """_format_typst_value("us-letter") is unchanged -- still returns
        the quoted string form (D-01)."""
        engine = TemplateEngine()
        formatted = engine._format_typst_value("us-letter")

        assert formatted == '"us-letter"'

    def test_map_parameters_papersize_is_plain_str(self):
        """map_parameters(md, typst_elements={"papersize": ...}) returns
        params["papersize"] as a plain str (D-01)."""
        engine = TemplateEngine()
        sphinx_metadata = {"project": "P", "author": "A", "release": "1.0"}

        params = engine.map_parameters(
            sphinx_metadata, typst_elements={"papersize": "us-letter"}
        )

        assert params["papersize"] == "us-letter"
        assert isinstance(params["papersize"], str)

    def test_map_parameters_fontsize_is_raw_typst(self):
        """map_parameters(md, typst_elements={"fontsize": ...}) returns
        params["fontsize"] as a RawTypst wrapping the value, NOT a plain
        str (D-02)."""
        from typsphinx.template_engine import RawTypst

        engine = TemplateEngine()
        sphinx_metadata = {"project": "P", "author": "A", "release": "1.0"}

        params = engine.map_parameters(
            sphinx_metadata, typst_elements={"fontsize": "20pt"}
        )

        assert isinstance(params["fontsize"], RawTypst)
        assert not isinstance(params["fontsize"], str)
        assert params["fontsize"].source == "20pt"

    def test_map_parameters_unknown_element_key_raises(self):
        """An unknown typst_elements key raises ExtensionError naming the
        offending key and listing both supported keys (D-06/D-07)."""
        from sphinx.errors import ExtensionError

        engine = TemplateEngine()
        sphinx_metadata = {"project": "P", "author": "A", "release": "1.0"}

        with pytest.raises(ExtensionError) as exc_info:
            engine.map_parameters(sphinx_metadata, typst_elements={"bogus": "x"})

        message = str(exc_info.value)
        assert "bogus" in message
        assert "papersize" in message
        assert "fontsize" in message

    def test_map_parameters_unknown_key_does_not_emit_wrong_quoted_form(self):
        """Negative-form regression guard: the wrong quoted-length output
        (`fontsize: "20pt"`) must never be what an unknown key produces --
        it must raise instead of falling through to any emission path."""
        from sphinx.errors import ExtensionError

        engine = TemplateEngine()
        sphinx_metadata = {"project": "P", "author": "A", "release": "1.0"}

        with pytest.raises(ExtensionError):
            engine.map_parameters(sphinx_metadata, typst_elements={"bogus": "20pt"})

    def test_map_parameters_copyright_never_in_params(self):
        """copyright is never present in map_parameters()'s returned params
        -- structural non-leak, not a filter (D-08)."""
        engine = TemplateEngine()
        sphinx_metadata = {
            "project": "P",
            "author": "A",
            "release": "1.0",
            "copyright": "2026, Someone",
        }

        params = engine.map_parameters(sphinx_metadata)

        assert "copyright" not in params

    def test_map_parameters_copyright_never_leaks_even_with_elements(self):
        """copyright stays absent even when typst_elements is also
        provided (D-08, guards against a future re-merge regression)."""
        engine = TemplateEngine()
        sphinx_metadata = {
            "project": "P",
            "author": "A",
            "release": "1.0",
            "copyright": "2026, Someone",
        }

        params = engine.map_parameters(
            sphinx_metadata, typst_elements={"papersize": "a4"}
        )

        assert "copyright" not in params
        assert params["papersize"] == "a4"

    def test_map_parameters_no_typst_elements_argument_still_works(self):
        """map_parameters(md) called with NO typst_elements argument still
        works exactly as today -- default None treated as empty (Pitfall 4,
        every existing one-positional-arg call site is unaffected)."""
        engine = TemplateEngine()
        sphinx_metadata = {"project": "P", "author": "A", "release": "1.0"}

        params = engine.map_parameters(sphinx_metadata)

        assert params["title"] == "P"
        assert "papersize" not in params
        assert "fontsize" not in params

    def test_render_papersize_and_fontsize_emission_shapes(self):
        """End-to-end through render(): papersize emits quoted, fontsize
        emits unquoted -- the two emission shapes this phase exists to
        produce (D-01/D-02)."""
        engine = TemplateEngine()
        sphinx_metadata = {"project": "P", "author": "A", "release": "1.0"}

        params = engine.map_parameters(
            sphinx_metadata,
            typst_elements={"papersize": "us-letter", "fontsize": "20pt"},
        )
        result = engine.render(params, "Content")

        assert 'papersize: "us-letter",' in result
        assert "fontsize: 20pt," in result
        # Double-formatting regression guard: fontsize must never be
        # emitted as a quoted string.
        assert 'fontsize: "20pt"' not in result


class TestDeriveTypstLang:
    """CONF-07: derive_typst_lang() -- D-02's generic split-and-lowercase
    conversion rule plus D-03's ASCII-scoped accept test and warn-and-omit
    fallback. See 27.1-CONTEXT.md."""

    @pytest.mark.parametrize(
        "sphinx_language,expected",
        [
            ("ja", "ja"),
            ("en", "en"),
            ("zh_CN", "zh"),
            ("pt-BR", "pt"),
            ("sr@latin", "sr"),
            ("zh_TW", "zh"),  # D-01's accepted limitation: no region support
            ("JA", "ja"),
            ("en_US", "en"),
        ],
    )
    def test_conversion_table(self, sphinx_language, expected):
        """D-02: the measured conversion table is pinned exactly."""
        from typsphinx.template_engine import derive_typst_lang

        assert derive_typst_lang(sphinx_language) == expected

    def test_unknown_but_well_formed_code_accepted_silently(self, caplog):
        """An unknown-but-well-formed 3-letter code is accepted and does NOT
        warn -- Typst itself falls back to English without aborting, so this
        helper does not need to know the set of codes Typst supports (D-03)."""
        import logging

        from typsphinx.template_engine import derive_typst_lang

        caplog.set_level(logging.WARNING)
        assert derive_typst_lang("xyz") == "xyz"
        assert not any(
            "typsphinx" in record.message and "lang" in record.message.lower()
            for record in caplog.records
        )

    @pytest.mark.parametrize(
        "malformed",
        ["日本語", "", None, "a", "abcd", "_"],
    )
    def test_malformed_inputs_return_none_and_warn(self, malformed, caplog):
        """D-03: every structurally invalid value returns None and emits a
        logger.warning naming the offending value via repr() -- never
        raises. The ASCII-scoped accept test rejects CJK code points even
        though they are 2-3 code points long (str.isalpha() would wrongly
        accept them)."""
        import logging

        from typsphinx.template_engine import derive_typst_lang

        caplog.set_level(logging.WARNING)
        result = derive_typst_lang(malformed)

        assert result is None
        assert any(repr(malformed) in record.message for record in caplog.records)

    def test_elements_allowlist_has_exactly_three_keys(self):
        """ELEMENTS_ALLOWLIST contains exactly papersize, fontsize, and lang
        -- lang tagged STRING (D-05, same emission kind as papersize)."""
        from typsphinx.template_engine import (
            ELEMENTS_ALLOWLIST,
            _ElementsEmissionKind,
        )

        assert set(ELEMENTS_ALLOWLIST) == {"papersize", "fontsize", "lang"}
        assert ELEMENTS_ALLOWLIST["lang"] == _ElementsEmissionKind.STRING

    def test_map_parameters_explicit_lang_is_plain_str(self):
        """map_parameters(md, typst_elements={"lang": "ja"}) puts the plain
        string "ja" into params, quoted like papersize (not RawTypst)."""
        from typsphinx.template_engine import RawTypst

        engine = TemplateEngine()
        sphinx_metadata = {"project": "P", "author": "A", "release": "1.0"}

        params = engine.map_parameters(sphinx_metadata, typst_elements={"lang": "ja"})

        assert params["lang"] == "ja"
        assert isinstance(params["lang"], str)
        assert not isinstance(params["lang"], RawTypst)

    def test_map_parameters_explicit_lang_not_validated(self):
        """D-04: an explicit typst_elements["lang"] value never passes
        through derive_typst_lang() or any other Python-side validation --
        it reaches params exactly as written, unraised."""
        engine = TemplateEngine()
        sphinx_metadata = {"project": "P", "author": "A", "release": "1.0"}

        params = engine.map_parameters(
            sphinx_metadata,
            typst_elements={"lang": "definitely not a language code"},
        )

        assert params["lang"] == "definitely not a language code"


class TestEffectiveElementsMerge:
    """CONF-07/D-05 + the adjacency/ordering edges: exercise map_parameters()
    through the same merged-dict shape writer.py's effective_elements
    pre-merge produces (``{"lang": auto_lang} if auto_lang else {}) |
    typst_elements``), without needing a full Sphinx build. See
    27.1-CONTEXT.md D-05."""

    def test_auto_derived_entry_alone_lands_in_params(self):
        """When only an auto-derived value is present (no explicit
        typst_elements), it lands in params."""
        engine = TemplateEngine()
        sphinx_metadata = {"project": "P", "author": "A", "release": "1.0"}

        auto_lang = "ja"
        typst_elements: dict = {}
        effective_elements = ({"lang": auto_lang} if auto_lang else {}) | typst_elements

        params = engine.map_parameters(
            sphinx_metadata, typst_elements=effective_elements
        )

        assert params["lang"] == "ja"

    def test_explicit_entry_alone_lands_in_params(self):
        """When only an explicit typst_elements["lang"] is present (no
        auto-derivation, e.g. a non-default-template path), it lands in
        params."""
        engine = TemplateEngine()
        sphinx_metadata = {"project": "P", "author": "A", "release": "1.0"}

        auto_lang = None
        typst_elements = {"lang": "de"}
        effective_elements = ({"lang": auto_lang} if auto_lang else {}) | typst_elements

        params = engine.map_parameters(
            sphinx_metadata, typst_elements=effective_elements
        )

        assert params["lang"] == "de"

    def test_both_present_exactly_one_entry_survives_holding_explicit_value(self):
        """Adjacency edge: when both an auto-derived and an explicit value
        are present, the result carries exactly ONE lang entry, and it
        holds the explicit value (D-05 precedence)."""
        engine = TemplateEngine()
        sphinx_metadata = {"project": "P", "author": "A", "release": "1.0"}

        auto_lang = "de"
        typst_elements = {"lang": "ja"}
        effective_elements = ({"lang": auto_lang} if auto_lang else {}) | typst_elements

        assert list(effective_elements.keys()).count("lang") == 1
        assert effective_elements["lang"] == "ja"

        params = engine.map_parameters(
            sphinx_metadata, typst_elements=effective_elements
        )

        assert params["lang"] == "ja"

    def test_merge_order_stable_across_repeated_calls(self):
        """Ordering edge: the merge order is stable across repeated calls
        with identical inputs -- no accumulation, no drift."""
        engine = TemplateEngine()
        sphinx_metadata = {"project": "P", "author": "A", "release": "1.0"}

        auto_lang = "de"
        typst_elements = {"lang": "ja"}

        results = []
        for _ in range(3):
            effective_elements = (
                {"lang": auto_lang} if auto_lang else {}
            ) | typst_elements
            params = engine.map_parameters(
                sphinx_metadata, typst_elements=effective_elements
            )
            results.append(params["lang"])

        assert results == ["ja", "ja", "ja"]
        # typst_elements itself is never mutated across repeated merges.
        assert typst_elements == {"lang": "ja"}
