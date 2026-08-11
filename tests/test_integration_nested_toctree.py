"""
Integration tests for nested toctree relative path generation (Issue #5).

Tests the complete build process with nested directory structures,
verifying that relative paths in #include() directives are correctly generated.

Requirements: 3.1, 3.2, 3.3, 5.1, 5.2
"""

import subprocess
from pathlib import Path

import pytest

# Check if typst-py is available for E2E compilation tests
try:
    import typst

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False


@pytest.fixture
def fixtures_dir():
    """Return the path to tests/fixtures/ directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def nested_toctree_dir(fixtures_dir):
    """Return the path to integration_nested_toctree test project."""
    return fixtures_dir / "integration_nested_toctree"


@pytest.fixture
def multi_level_dir(fixtures_dir):
    """Return the path to integration_multi_level test project."""
    return fixtures_dir / "integration_multi_level"


@pytest.fixture
def sibling_dir(fixtures_dir):
    """Return the path to integration_sibling test project."""
    return fixtures_dir / "integration_sibling"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


class TestNestedToctreeIntegration:
    """Test nested toctree with relative path generation (Task 4.1, Issue #5)."""

    def test_nested_toctree_fixture_exists(self, nested_toctree_dir):
        """Test that the nested toctree fixture has required files."""
        assert (nested_toctree_dir / "conf.py").exists()
        assert (nested_toctree_dir / "index.rst").exists()
        assert (nested_toctree_dir / "chapter1" / "index.rst").exists()
        assert (nested_toctree_dir / "chapter1" / "section1.rst").exists()
        assert (nested_toctree_dir / "chapter1" / "section2.rst").exists()

    def test_sphinx_build_succeeds(self, nested_toctree_dir, temp_build_dir):
        """Test that sphinx-build succeeds for nested toctree project."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(nested_toctree_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_chapter1_index_has_relative_includes(
        self, nested_toctree_dir, temp_build_dir
    ):
        """
        Test that chapter1/index.typ uses relative paths for same-directory files.

        Expected: include("section1.typ") and include("section2.typ")
        NOT: include("chapter1/section1.typ")

        Requirements: 3.1
        """
        # Build the project
        subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(nested_toctree_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
        )

        # Read generated chapter1/index.typ
        chapter1_index = temp_build_dir / "chapter1" / "index.typ"
        assert chapter1_index.exists(), "chapter1/index.typ was not generated"

        content = chapter1_index.read_text()

        # Verify relative paths (same directory - no "chapter1/" prefix)
        assert (
            'include("section1.typ")' in content
        ), 'Expected relative path include("section1.typ") not found'
        assert (
            'include("section2.typ")' in content
        ), 'Expected relative path include("section2.typ") not found'

        # Ensure absolute paths are NOT used
        assert (
            'include("chapter1/section1.typ")' not in content
        ), "Unexpected absolute path found (should be relative)"
        assert (
            'include("chapter1/section2.typ")' not in content
        ), "Unexpected absolute path found (should be relative)"

    def test_root_index_has_correct_include(self, nested_toctree_dir, temp_build_dir):
        """
        Test that index.typ correctly includes chapter1/index.typ.

        Requirements: 3.3
        """
        # Build the project
        subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(nested_toctree_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
        )

        # Read generated index.typ -- the CONTENT file (docname-derived,
        # unchanged by the content/wrapper split, R1/R5): a toctree
        # #include() is emitted where its own doctree is translated,
        # regardless of what this docname's own wrapper target is.
        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"

        content = index_typ.read_text()

        # Root directory should use subdirectory path
        assert (
            'include("chapter1/index.typ")' in content
        ), 'Expected include("chapter1/index.typ") not found in root index'

    def test_root_wrapper_has_exactly_one_include_of_its_content(
        self, nested_toctree_dir, temp_build_dir
    ):
        """
        Phase 47 (R2/R3): the WRAPPER file (this fixture's typst_documents
        target, "master.typ") must contain exactly one #include(, naming
        its own master's content file ("index.typ") -- the toctree's
        OWN includes stay on the content file per R5 and must not also
        appear on the wrapper.
        """
        subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(nested_toctree_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
        )

        master_typ = temp_build_dir / "master.typ"
        assert master_typ.exists(), "master.typ was not generated"

        content = master_typ.read_text()
        assert content.count("#include(") == 1, (
            "Expected exactly one #include( in the wrapper -- "
            f"got {content.count('#include(')}:\n{content}"
        )
        assert (
            '#include("index.typ")' in content
        ), 'Expected the wrapper to include("index.typ") (its own content file)'


class TestMultiLevelNestedToctree:
    """Test 3-level nested toctree (Task 4.2)."""

    def test_multi_level_fixture_exists(self, multi_level_dir):
        """Test that the multi-level fixture has required files."""
        assert (multi_level_dir / "conf.py").exists()
        assert (multi_level_dir / "index.rst").exists()
        assert (multi_level_dir / "part1" / "index.rst").exists()
        assert (multi_level_dir / "part1" / "chapter1" / "index.rst").exists()

    def test_sphinx_build_succeeds(self, multi_level_dir, temp_build_dir):
        """Test that sphinx-build succeeds for multi-level nested project."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(multi_level_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_deep_nested_relative_paths(self, multi_level_dir, temp_build_dir):
        """
        Test that part1/chapter1/index.typ uses relative paths for sections.

        Requirements: 3.2
        """
        # Build the project
        subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(multi_level_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
        )

        # Read generated part1/chapter1/index.typ
        chapter1_index = temp_build_dir / "part1" / "chapter1" / "index.typ"
        assert chapter1_index.exists(), "part1/chapter1/index.typ was not generated"

        content = chapter1_index.read_text()

        # Verify relative paths (same directory)
        assert (
            'include("section1.typ")' in content
        ), 'Expected relative path include("section1.typ") not found'
        assert (
            'include("section2.typ")' in content
        ), 'Expected relative path include("section2.typ") not found'

    def test_root_wrapper_has_exactly_one_include_of_its_content(
        self, multi_level_dir, temp_build_dir
    ):
        """
        Phase 47 (R2/R3): the WRAPPER file (this fixture's typst_documents
        target, "master.typ") must contain exactly one #include(, naming
        its own master's content file ("index.typ").
        """
        subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(multi_level_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
        )

        master_typ = temp_build_dir / "master.typ"
        assert master_typ.exists(), "master.typ was not generated"

        content = master_typ.read_text()
        assert content.count("#include(") == 1, (
            "Expected exactly one #include( in the wrapper -- "
            f"got {content.count('#include(')}:\n{content}"
        )
        assert (
            '#include("index.typ")' in content
        ), 'Expected the wrapper to include("index.typ") (its own content file)'


class TestSiblingDirectoryReferences:
    """Test cross-directory toctree references (Task 4.3)."""

    def test_sibling_fixture_exists(self, sibling_dir):
        """Test that the sibling directory fixture has required files."""
        assert (sibling_dir / "conf.py").exists()
        assert (sibling_dir / "index.rst").exists()
        assert (sibling_dir / "chapter1" / "doc1.rst").exists()
        assert (sibling_dir / "chapter2" / "doc2.rst").exists()

    def test_sphinx_build_succeeds(self, sibling_dir, temp_build_dir):
        """Test that sphinx-build succeeds for sibling directory project."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(sibling_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_cross_directory_relative_path(self, sibling_dir, temp_build_dir):
        """
        Test that chapter1/doc1.typ uses "../chapter2/doc2.typ" for sibling reference.

        Requirements: 3.2, 3.3
        """
        # Build the project
        subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(sibling_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
        )

        # Read generated chapter1/doc1.typ
        doc1_typ = temp_build_dir / "chapter1" / "doc1.typ"
        assert doc1_typ.exists(), "chapter1/doc1.typ was not generated"

        content = doc1_typ.read_text()

        # Verify cross-directory relative path
        assert (
            'include("../chapter2/doc2.typ")' in content
        ), 'Expected relative path include("../chapter2/doc2.typ") not found'

    def test_root_wrapper_has_exactly_one_include_of_its_content(
        self, sibling_dir, temp_build_dir
    ):
        """
        Phase 47 (R2/R3): the WRAPPER file (this fixture's typst_documents
        target, "master.typ") must contain exactly one #include(, naming
        its own master's content file ("index.typ").
        """
        subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(sibling_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
        )

        master_typ = temp_build_dir / "master.typ"
        assert master_typ.exists(), "master.typ was not generated"

        content = master_typ.read_text()
        assert content.count("#include(") == 1, (
            "Expected exactly one #include( in the wrapper -- "
            f"got {content.count('#include(')}:\n{content}"
        )
        assert (
            '#include("index.typ")' in content
        ), 'Expected the wrapper to include("index.typ") (its own content file)'


@pytest.mark.skipif(not TYPST_AVAILABLE, reason="typst-py not installed")
class TestE2ETypstCompilation:
    """
    End-to-end compilation tests using typst-py (Task 5.1).

    Verifies that generated Typst files can be successfully compiled to PDF.
    """

    def test_nested_toctree_compiles_to_pdf(self, nested_toctree_dir, temp_build_dir):
        """
        Test that nested toctree project compiles to PDF successfully.

        Requirements: 4.1, 4.2, 4.3, 5.3
        """
        # Build Typst files
        result = subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(nested_toctree_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Sphinx build failed: {result.stderr}"

        # Compile the root WRAPPER (this fixture's typst_documents target,
        # "master.typ") to PDF -- Phase 47 (R3/R4): only a wrapper is a
        # complete, self-contained document (template application +
        # #include() of its own content file); the content file
        # ("index.typ") carries no template and is not a compile target.
        master_typ = temp_build_dir / "master.typ"
        assert master_typ.exists(), "master.typ was not generated"

        pdf_output = temp_build_dir / "master.pdf"

        # Compile using typst-py
        typst.compile(str(master_typ), output=str(pdf_output))

        # Verify PDF was created
        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"

        # Verify PDF magic number
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

    def test_multi_level_nested_compiles_to_pdf(self, multi_level_dir, temp_build_dir):
        """
        Test that 3-level nested project compiles to PDF successfully.

        Requirements: 4.2, 5.3
        """
        # Build Typst files
        result = subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(multi_level_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Sphinx build failed: {result.stderr}"

        # Compile the root WRAPPER (this fixture's typst_documents target,
        # "master.typ") to PDF -- Phase 47 (R3/R4): only a wrapper is a
        # complete, self-contained document.
        master_typ = temp_build_dir / "master.typ"
        assert master_typ.exists(), "master.typ was not generated"

        pdf_output = temp_build_dir / "master.pdf"

        # Compile using typst-py
        typst.compile(str(master_typ), output=str(pdf_output))

        # Verify PDF was created
        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"

    def test_sibling_directory_compiles_to_pdf(self, sibling_dir, temp_build_dir):
        """
        Test that sibling directory project compiles to PDF successfully.

        Requirements: 4.3, 5.3
        """
        # Build Typst files
        result = subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(sibling_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Sphinx build failed: {result.stderr}"

        # Compile the root WRAPPER (this fixture's typst_documents target,
        # "master.typ") to PDF -- Phase 47 (R3/R4): only a wrapper is a
        # complete, self-contained document.
        master_typ = temp_build_dir / "master.typ"
        assert master_typ.exists(), "master.typ was not generated"

        pdf_output = temp_build_dir / "master.pdf"

        # Compile using typst-py
        typst.compile(str(master_typ), output=str(pdf_output))

        # Verify PDF was created
        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"

    def test_compilation_uses_correct_root_directory(
        self, nested_toctree_dir, temp_build_dir
    ):
        """
        Test that typst compilation correctly resolves include() paths.

        This ensures that the root directory is set correctly for typst.compile(),
        allowing include() directives to find nested files.

        Requirements: 5.3
        """
        # Build Typst files
        subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "typst",
                str(nested_toctree_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
        )

        # Compile chapter1/index.typ directly (should resolve includes)
        chapter1_index = temp_build_dir / "chapter1" / "index.typ"
        assert chapter1_index.exists()

        pdf_output = temp_build_dir / "chapter1_index.pdf"

        # Compile with correct root directory
        typst.compile(
            str(chapter1_index),
            output=str(pdf_output),
            root=str(temp_build_dir / "chapter1"),
        )

        # Verify compilation succeeded
        assert pdf_output.exists(), "Nested document PDF was not created"
        assert pdf_output.stat().st_size > 0, "Nested document PDF is empty"
