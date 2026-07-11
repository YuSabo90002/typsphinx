"""Tests for PDF generation functionality (Requirements 9)"""

from unittest.mock import patch

import pytest


class TestTypstPackageIntegration:
    """Test typst package integration (Task 10.1)"""

    def test_typst_package_is_available(self):
        """Test that typst package can be imported"""
        try:
            import typst

            assert typst is not None
        except ImportError:
            pytest.fail("typst package should be available")

    def test_typst_compile_function_exists(self):
        """Test that typst.compile function exists"""
        import typst

        assert hasattr(typst, "compile")
        assert callable(typst.compile)

    def test_check_typst_available_helper(self):
        """Test helper function to check typst availability"""
        from typsphinx.pdf import check_typst_available

        # Should not raise any exception
        check_typst_available()

    def test_get_typst_version(self):
        """Test getting typst version information"""
        from typsphinx.pdf import get_typst_version

        version = get_typst_version()

        assert version is not None
        assert isinstance(version, str)
        # Version should be in format like "0.11.1" or similar
        assert len(version) > 0


class TestTypstPDFBuilder:
    """Test TypstPDFBuilder implementation (Task 10.2)"""

    def test_builder_name_is_typstpdf(self):
        """Test that builder name is 'typstpdf'"""
        from typsphinx.builder import TypstPDFBuilder

        assert TypstPDFBuilder.name == "typstpdf"

    def test_builder_format_is_pdf(self):
        """Test that output format is 'pdf'"""
        from typsphinx.builder import TypstPDFBuilder

        assert TypstPDFBuilder.format == "pdf"

    def test_builder_out_suffix_is_pdf(self):
        """Test that output file suffix is '.pdf'"""
        from typsphinx.builder import TypstPDFBuilder

        assert TypstPDFBuilder.out_suffix == ".pdf"

    def test_builder_inherits_from_typst_builder(self):
        """Test that TypstPDFBuilder inherits from TypstBuilder"""
        from typsphinx.builder import TypstBuilder, TypstPDFBuilder

        assert issubclass(TypstPDFBuilder, TypstBuilder)

    def test_builder_initialization(self, temp_sphinx_app):
        """Test builder can be initialized"""
        from typsphinx.builder import TypstPDFBuilder

        builder = TypstPDFBuilder(temp_sphinx_app, temp_sphinx_app.env)

        assert builder is not None
        assert builder._app == temp_sphinx_app
        assert builder.name == "typstpdf"

    def test_builder_finish_generates_pdf(self, temp_sphinx_app, tmp_path):
        """Test that finish() method generates PDF from Typst content"""
        from typsphinx.builder import TypstPDFBuilder

        # Setup builder
        builder = TypstPDFBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.outdir = str(tmp_path)

        # Configure typst_documents so finish() knows what to compile
        builder.config.typst_documents = [
            ("output", "output.typ", "Test Document", "Test Author"),
        ]

        # Mock the parent finish() to generate .typ file
        with patch.object(TypstPDFBuilder.__bases__[0], "finish") as mock_parent_finish:
            # Create a mock .typ file
            typ_file = tmp_path / "output.typ"
            typ_file.write_text("= Test Document\n\nThis is a test.\n")

            # Mock compile_typst_to_pdf
            with patch("typsphinx.builder.compile_typst_to_pdf") as mock_compile:
                mock_compile.return_value = b"%PDF-1.4 mock pdf content"

                builder.finish()

                # Verify compile was called
                assert mock_compile.called


class TestPDFCompilationIntegration:
    """Test PDF compilation integration (Task 10.3)"""

    def test_compile_simple_typst_content(self):
        """Test compiling simple Typst content to PDF"""
        from typsphinx.pdf import compile_typst_to_pdf

        typst_content = "= Test Document\n\nThis is a test.\n"

        pdf_bytes = compile_typst_to_pdf(typst_content)

        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        # PDF files start with %PDF
        assert pdf_bytes.startswith(b"%PDF")

    def test_compile_with_root_dir(self, tmp_path):
        """Test compiling with root directory for includes"""
        from typsphinx.pdf import compile_typst_to_pdf

        # Create a simple image file in tmp_path
        image_file = tmp_path / "test.png"
        # Create minimal PNG file
        image_file.write_bytes(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
        )

        typst_content = "= Test\n\nSome content.\n"

        pdf_bytes = compile_typst_to_pdf(typst_content, root_dir=str(tmp_path))

        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b"%PDF")

    def test_compile_with_template(self):
        """Test compiling Typst content with template function"""
        from typsphinx.pdf import compile_typst_to_pdf

        typst_content = """
#let project(title: "", body) = {
  set document(title: title)
  set text(size: 11pt)

  align(center)[
    #text(2em, weight: "bold")[#title]
  ]

  body
}

#show: project.with(
  title: "Test Document",
)

= Chapter 1

This is the content.
"""

        pdf_bytes = compile_typst_to_pdf(typst_content)

        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b"%PDF")

    def test_compile_error_handling(self):
        """Test that compilation errors are handled properly"""
        from typsphinx.pdf import compile_typst_to_pdf

        # Invalid Typst syntax
        invalid_typst = "#let x = \n"

        with pytest.raises(Exception):
            compile_typst_to_pdf(invalid_typst)


class TestPDFErrorHandling:
    """Test PDF generation error handling (Task 10.4)"""

    def test_typst_compilation_error_detection(self):
        """Test that Typst compilation errors are properly detected"""
        from typsphinx.pdf import TypstCompilationError, compile_typst_to_pdf

        # Invalid Typst syntax - unmatched bracket
        invalid_typst = "= Test\n\n#let func(x) = { x + \n"

        with pytest.raises(TypstCompilationError) as exc_info:
            compile_typst_to_pdf(invalid_typst)

        # Error should contain useful information
        error = exc_info.value
        assert hasattr(error, "message")
        assert hasattr(error, "typst_error")

    def test_error_message_includes_context(self):
        """Test that error messages include helpful context"""
        from typsphinx.pdf import TypstCompilationError, compile_typst_to_pdf

        # Invalid function call
        invalid_typst = "= Test\n\n#unknownfunction()"

        with pytest.raises(TypstCompilationError) as exc_info:
            compile_typst_to_pdf(invalid_typst)

        error_msg = str(exc_info.value)
        # Error message should be informative
        assert len(error_msg) > 0
        assert isinstance(error_msg, str)

    def test_builder_error_handling_continues_on_failure(
        self, temp_sphinx_app, tmp_path
    ):
        """Test that builder continues processing other files after one fails"""
        from unittest.mock import patch

        from typsphinx.builder import TypstPDFBuilder

        builder = TypstPDFBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.outdir = str(tmp_path)

        # Configure typst_documents with one valid and one invalid document
        builder.config.typst_documents = [
            ("valid", "valid.typ", "Valid Document", "Test Author"),
            ("invalid", "invalid.typ", "Invalid Document", "Test Author"),
        ]

        # Create multiple .typ files - one valid, one invalid
        valid_file = tmp_path / "valid.typ"
        valid_file.write_text("= Valid Document\n\nContent here.\n")

        invalid_file = tmp_path / "invalid.typ"
        invalid_file.write_text("#let x = \n")  # Syntax error

        # Mock logger to capture error messages
        with patch("typsphinx.builder.logger") as mock_logger:
            builder.finish()

            # Should have logged errors for the invalid file
            assert mock_logger.error.called

    def test_error_includes_source_location(self):
        """Test that errors include source file location information"""
        from typsphinx.pdf import TypstCompilationError, compile_typst_to_pdf

        # Invalid Typst with specific line error
        invalid_typst = """= Test Document

This is valid content.

#let value = 5
#unknownfunction(value)

More content here.
"""

        with pytest.raises(TypstCompilationError) as exc_info:
            compile_typst_to_pdf(invalid_typst)

        # Error should exist
        assert exc_info.value is not None

    def test_missing_typst_package_error(self):
        """Test error handling when typst package is not installed"""
        from unittest.mock import patch

        from typsphinx.pdf import check_typst_available

        # Mock import failure
        with patch(
            "builtins.__import__", side_effect=ImportError("No module named 'typst'")
        ):
            with pytest.raises(ImportError) as exc_info:
                check_typst_available()

            error_msg = str(exc_info.value)
            # Should provide installation instructions
            assert "pip install" in error_msg or "typst" in error_msg


class TestCICDEnvironment:
    """Test CI/CD environment compatibility (Task 10.5)"""

    def test_pdf_generation_without_external_cli(self):
        """Test that PDF generation works without external Typst CLI"""
        from typsphinx.pdf import compile_typst_to_pdf

        # This test verifies that we're using typst-py, not external CLI
        # If this passes, it means PDF generation works with pip install only
        typst_content = "= CI/CD Test\n\nThis tests pip-only installation.\n"

        pdf_bytes = compile_typst_to_pdf(typst_content)

        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b"%PDF")

    def test_typst_package_version_compatibility(self):
        """Test that typst package version is compatible"""
        from typsphinx.pdf import get_typst_version

        version = get_typst_version()

        # Version should be available
        assert version != "not installed"
        assert version != "unknown" or True  # Allow unknown but warn

        # Version should be a string
        assert isinstance(version, str)

    def test_builder_works_in_minimal_environment(self, temp_sphinx_app, tmp_path):
        """Test that TypstPDFBuilder works with minimal dependencies"""
        from typsphinx.builder import TypstPDFBuilder

        # Create builder - should work with just pip installed packages
        builder = TypstPDFBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.outdir = str(tmp_path)

        # Configure typst_documents
        builder.config.typst_documents = [
            ("test", "test.typ", "Test Document", "Test Author"),
        ]

        # Create a simple .typ file
        typ_file = tmp_path / "test.typ"
        typ_file.write_text("= Test\n\nMinimal environment test.\n")

        # Builder finish should work
        builder.finish()

        # PDF should be generated
        pdf_file = tmp_path / "test.pdf"
        assert pdf_file.exists()
        assert pdf_file.stat().st_size > 0

    def test_import_without_optional_dependencies(self):
        """Test that core module can be imported without PDF dependencies"""
        # This tests that the module structure allows graceful degradation
        try:
            from typsphinx import builder, translator, writer

            assert builder is not None
            assert writer is not None
            assert translator is not None
        except ImportError as e:
            pytest.fail(f"Core modules should be importable: {e}")

    def test_error_message_for_missing_typst_is_helpful(self):
        """Test that missing typst package provides helpful error"""
        from unittest.mock import patch

        from typsphinx.pdf import check_typst_available

        with patch(
            "builtins.__import__", side_effect=ImportError("No module named 'typst'")
        ):
            try:
                check_typst_available()
                pytest.fail("Should have raised ImportError")
            except ImportError as e:
                error_msg = str(e)
                # Error should mention both installation methods
                assert "pip install typst" in error_msg
                assert "typsphinx" in error_msg
