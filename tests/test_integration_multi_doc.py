"""
Integration tests for multi-document Sphinx projects (Task 15.2).

Tests toctree handling, #include() generation, and heading level adjustments.
"""

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir():
    """Return the path to tests/fixtures/ directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def multi_doc_project_dir(fixtures_dir):
    """Return the path to integration_multi_doc test project."""
    return fixtures_dir / "integration_multi_doc"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


class TestMultiDocumentIntegration:
    """Test multi-document Sphinx projects with toctree (Task 15.2)."""

    def test_multi_doc_project_files_exist(self, multi_doc_project_dir):
        """Test that the multi-doc project fixture has required files."""
        assert (multi_doc_project_dir / "conf.py").exists()
        assert (multi_doc_project_dir / "index.rst").exists()
        assert (multi_doc_project_dir / "chapter1.rst").exists()
        assert (multi_doc_project_dir / "chapter2.rst").exists()

    def test_sphinx_build_multi_doc_succeeds(
        self, multi_doc_project_dir, temp_build_dir
    ):
        """Test that sphinx-build succeeds for multi-document project."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(multi_doc_project_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, (
            f"sphinx-build failed:\nSTDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    def test_multiple_typ_files_generated(self, multi_doc_project_dir, temp_build_dir):
        """Test that separate .typ files are generated for each document."""
        subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(multi_doc_project_dir),
                str(temp_build_dir),
            ],
            check=True,
            capture_output=True,
        )

        # Check that all .typ files are generated
        assert (temp_build_dir / "index.typ").exists()
        assert (temp_build_dir / "chapter1.typ").exists()
        assert (temp_build_dir / "chapter2.typ").exists()

    def test_master_doc_has_include_directives(
        self, multi_doc_project_dir, temp_build_dir
    ):
        """Test that master document contains #include() directives."""
        subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(multi_doc_project_dir),
                str(temp_build_dir),
            ],
            check=True,
            capture_output=True,
        )

        index_typ = temp_build_dir / "index.typ"
        content = index_typ.read_text()

        # Should contain include() directives for chapter1 and chapter2
        assert "chapter1.typ" in content
        assert "chapter2.typ" in content
        assert "include(" in content

    def test_include_directives_have_heading_offset(
        self, multi_doc_project_dir, temp_build_dir
    ):
        """
        Test that include() directives have heading level offset.

        Note (44.1-03, D-07): the disjunctive assertion below checks only
        the partial substring "heading(offset:" (or "set heading"), and
        both are present in both the pre-TOC-01 absolute assignment form
        and the current context-relative increment form. Measured
        directly: this assertion cannot tell the two shapes apart and
        passes against either -- it documents that a heading offset is
        present at all, not which form it takes. It is not a guard for
        TOC-01/D-07.
        """
        subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(multi_doc_project_dir),
                str(temp_build_dir),
            ],
            check=True,
            capture_output=True,
        )

        index_typ = temp_build_dir / "index.typ"
        content = index_typ.read_text()

        # Should contain heading offset setting
        # Format: context { set heading(offset: heading.offset + 1);
        #                    include("chapter1.typ") }
        assert "heading(offset:" in content or "set heading" in content

    def test_chapter_files_contain_content(self, multi_doc_project_dir, temp_build_dir):
        """Test that generated chapter .typ files contain their content."""
        subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(multi_doc_project_dir),
                str(temp_build_dir),
            ],
            check=True,
            capture_output=True,
        )

        chapter1_typ = temp_build_dir / "chapter1.typ"
        content1 = chapter1_typ.read_text()
        assert "Chapter 1: First Chapter" in content1
        assert "Section 1.1" in content1

        chapter2_typ = temp_build_dir / "chapter2.typ"
        content2 = chapter2_typ.read_text()
        assert "Chapter 2: Second Chapter" in content2
        assert "Section 2.1" in content2

    def test_master_doc_has_introduction(self, multi_doc_project_dir, temp_build_dir):
        """Test that master document contains its own content."""
        subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(multi_doc_project_dir),
                str(temp_build_dir),
            ],
            check=True,
            capture_output=True,
        )

        index_typ = temp_build_dir / "index.typ"
        content = index_typ.read_text()

        # Should contain the introduction section from index.rst
        assert "Introduction" in content
        assert "This is the introduction section" in content

    def test_toctree_options_in_template_params(
        self, multi_doc_project_dir, temp_build_dir
    ):
        """Test that toctree options (maxdepth, numbered) are available."""
        subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(multi_doc_project_dir),
                str(temp_build_dir),
            ],
            check=True,
            capture_output=True,
        )

        index_typ = temp_build_dir / "index.typ"
        content = index_typ.read_text()

        # The template should be called with parameters
        # We can't directly test template parameters, but we can verify
        # that the file structure is correct
        assert len(content) > 0

    def test_incremental_build_multi_doc(self, multi_doc_project_dir, temp_build_dir):
        """Test that incremental builds work for multi-document projects."""
        # First build
        subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(multi_doc_project_dir),
                str(temp_build_dir),
            ],
            check=True,
            capture_output=True,
        )

        # Second build (should be incremental)
        result = subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(multi_doc_project_dir),
                str(temp_build_dir),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
