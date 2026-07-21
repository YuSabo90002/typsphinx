"""
Integration tests for examples/basic/ sample project.

Tests that the basic example project can be built successfully
and produces valid Typst output (Task 16.1, Requirement 12.3).
"""

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def basic_example_dir():
    """Return the path to examples/basic/ directory."""
    return Path(__file__).parent.parent / "examples" / "basic"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    build_dir = tmp_path / "_build"
    build_dir.mkdir()
    return build_dir


class TestBasicExampleStructure:
    """Test that examples/basic/ has the required structure."""

    def test_basic_directory_exists(self, basic_example_dir):
        """Test that examples/basic/ directory exists."""
        assert basic_example_dir.exists(), "examples/basic/ directory should exist"
        assert basic_example_dir.is_dir(), "examples/basic/ should be a directory"

    def test_conf_py_exists(self, basic_example_dir):
        """Test that conf.py exists in examples/basic/."""
        conf_py = basic_example_dir / "conf.py"
        assert conf_py.exists(), "examples/basic/conf.py should exist"
        assert conf_py.is_file(), "conf.py should be a file"

    def test_index_rst_exists(self, basic_example_dir):
        """Test that index.rst exists in examples/basic/."""
        index_rst = basic_example_dir / "index.rst"
        assert index_rst.exists(), "examples/basic/index.rst should exist"
        assert index_rst.is_file(), "index.rst should be a file"

    def test_readme_exists(self, basic_example_dir):
        """Test that README.md exists in examples/basic/."""
        readme = basic_example_dir / "README.md"
        assert readme.exists(), "examples/basic/README.md should exist"
        assert readme.is_file(), "README.md should be a file"


class TestBasicExampleConfiguration:
    """Test that conf.py has valid configuration."""

    def test_conf_py_has_sphinxcontrib_typst(self, basic_example_dir):
        """Test that conf.py includes 'typsphinx' extension."""
        conf_py = basic_example_dir / "conf.py"
        content = conf_py.read_text()
        assert (
            "typsphinx" in content
        ), "conf.py should include 'typsphinx' in extensions"

    def test_conf_py_has_project_metadata(self, basic_example_dir):
        """Test that conf.py defines project metadata."""
        conf_py = basic_example_dir / "conf.py"
        content = conf_py.read_text()
        assert "project" in content, "conf.py should define 'project'"
        assert "author" in content, "conf.py should define 'author'"

    def test_conf_py_is_valid_python(self, basic_example_dir):
        """Test that conf.py is valid Python code."""
        conf_py = basic_example_dir / "conf.py"
        try:
            compile(conf_py.read_text(), str(conf_py), "exec")
        except SyntaxError as e:
            pytest.fail(f"conf.py has syntax errors: {e}")


class TestBasicExampleContent:
    """Test that index.rst has basic reStructuredText content."""

    def test_index_rst_has_title(self, basic_example_dir):
        """Test that index.rst has a title."""
        index_rst = basic_example_dir / "index.rst"
        content = index_rst.read_text()
        # reStructuredText title uses === or similar
        assert "=" in content, "index.rst should have a title with === markup"

    def test_index_rst_is_not_empty(self, basic_example_dir):
        """Test that index.rst is not empty."""
        index_rst = basic_example_dir / "index.rst"
        content = index_rst.read_text()
        assert len(content) > 0, "index.rst should not be empty"
        assert len(content.strip()) > 0, "index.rst should have non-whitespace content"


class TestBasicExampleBuild:
    """Test that examples/basic/ can be built with sphinx-build."""

    def test_build_typst_succeeds(self, basic_example_dir, temp_build_dir):
        """Test that sphinx-build -b typst succeeds for examples/basic/."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(basic_example_dir),
                str(temp_build_dir / "typst"),
            ],
            capture_output=True,
            text=True,
        )

        # Check that the build succeeded
        assert result.returncode == 0, (
            f"sphinx-build -b typst failed:\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    def test_build_generates_typ_file(self, basic_example_dir, temp_build_dir):
        """Test that building examples/basic/ generates basic-example.typ.

        examples/basic/conf.py declares a non-identity typst_documents target
        ("basic-example.typ"), so the emitted artifact is named after that
        target, not the source docname ("index").
        """
        # Build the project
        subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(basic_example_dir),
                str(temp_build_dir / "typst"),
            ],
            check=True,
            capture_output=True,
        )

        # Check that basic-example.typ was generated
        output_file = temp_build_dir / "typst" / "basic-example.typ"
        assert output_file.exists(), "basic-example.typ should be generated"
        assert output_file.is_file(), "basic-example.typ should be a file"

        # The source-docname-derived artifact must NOT be present -- D-08
        # clean break, no compatibility shim.
        docname_file = output_file.parent / "index.typ"
        assert not docname_file.exists(), (
            "index.typ should not exist -- the emitted artifact must follow "
            "the typst_documents target name ('basic-example.typ'), not the "
            "source docname (D-08 clean break)."
        )

    def test_generated_typ_is_valid(self, basic_example_dir, temp_build_dir):
        """Test that the generated .typ file contains valid Typst markup."""
        # Build the project
        subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(basic_example_dir),
                str(temp_build_dir / "typst"),
            ],
            check=True,
            capture_output=True,
        )

        # Read the generated .typ file
        output_file = temp_build_dir / "typst" / "basic-example.typ"
        content = output_file.read_text()

        # Check for basic Typst syntax (headings, functions, etc.)
        assert len(content) > 0, "Generated .typ file should not be empty"
        # Should have #import or function calls
        assert "#" in content, "Typst file should contain # directives or functions"


class TestBasicExampleReadme:
    """Test that README.md provides build instructions."""

    def test_readme_mentions_sphinx_build(self, basic_example_dir):
        """Test that README.md mentions sphinx-build command."""
        readme = basic_example_dir / "README.md"
        content = readme.read_text()
        assert (
            "sphinx-build" in content
        ), "README.md should mention 'sphinx-build' command"

    def test_readme_mentions_typst_builder(self, basic_example_dir):
        """Test that README.md mentions the typst builder."""
        readme = basic_example_dir / "README.md"
        content = readme.read_text()
        assert "typst" in content.lower(), "README.md should mention 'typst' or 'Typst'"

    def test_readme_is_not_empty(self, basic_example_dir):
        """Test that README.md is not empty."""
        readme = basic_example_dir / "README.md"
        content = readme.read_text()
        assert len(content) > 0, "README.md should not be empty"
        assert len(content.strip()) > 0, "README.md should have non-whitespace content"
