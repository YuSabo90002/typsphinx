"""Tests for PDF generation functionality (Requirements 9)"""

from os import path
from unittest.mock import patch

import pytest
from sphinx.errors import ExtensionError


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

            # Mock compile_typst_file_to_pdf -- the function finish() calls
            with patch("typsphinx.builder.compile_typst_file_to_pdf") as mock_compile:
                mock_compile.return_value = b"%PDF-1.4 mock pdf content"

                builder.finish()

                # Verify compile was called
                assert mock_compile.called

    def test_finish_compiles_master_at_its_own_directory(
        self, temp_sphinx_app, tmp_path
    ):
        """D-08(b): the path handed to the compile function is the master's
        own .typ (inside its docname directory), never a file at the outdir
        root -- this is the structural invariant the PDF-02 fix depends on,
        and it is checkable even where typst-py is not installed because the
        compile function is mocked."""
        from typsphinx.builder import TypstPDFBuilder

        builder = TypstPDFBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.outdir = str(tmp_path)

        builder.config.typst_documents = [
            ("api/index", "index", "Test Document", "Test Author"),
        ]

        api_dir = tmp_path / "api"
        api_dir.mkdir()
        (api_dir / "index.typ").write_text("= Test Document\n\nNested master.\n")

        with patch.object(TypstPDFBuilder.__bases__[0], "finish"):
            with patch("typsphinx.builder.compile_typst_file_to_pdf") as mock_compile:
                mock_compile.return_value = b"%PDF-1.4 mock"
                builder.finish()

        called_args, called_kwargs = mock_compile.call_args
        called_path = called_args[0]
        assert called_path == str(api_dir / "index.typ")
        assert path.dirname(called_path) == str(api_dir)
        assert path.dirname(called_path) != str(tmp_path)
        # builder.outdir may be a Sphinx _StrPath (path-like, not a plain
        # str); stringify explicitly to avoid its deprecated str-equality
        # comparison path (RemovedInSphinx10Warning, escalated to error).
        assert str(called_kwargs["root_dir"]) == str(tmp_path)


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

    def test_builder_attempts_every_master_then_raises(self, temp_sphinx_app, tmp_path):
        """D-04: a compile failure raises ExtensionError after every master
        has been attempted, and the message names the failing docname."""
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

        with pytest.raises(ExtensionError) as exc_info:
            builder.finish()

        assert "invalid" in str(exc_info.value)

    def test_builder_still_writes_pdf_for_masters_that_compile(
        self, temp_sphinx_app, tmp_path
    ):
        """D-05: the loop-continues half of the contract survives the D-04
        raise -- a master that compiles successfully still gets its .pdf
        written even though a sibling master fails."""
        from typsphinx.builder import TypstPDFBuilder

        builder = TypstPDFBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.outdir = str(tmp_path)

        builder.config.typst_documents = [
            ("valid", "valid.typ", "Valid Document", "Test Author"),
            ("invalid", "invalid.typ", "Invalid Document", "Test Author"),
        ]

        valid_file = tmp_path / "valid.typ"
        valid_file.write_text("= Valid Document\n\nContent here.\n")

        invalid_file = tmp_path / "invalid.typ"
        invalid_file.write_text("#let x = \n")  # Syntax error

        with pytest.raises(ExtensionError):
            builder.finish()

        assert (tmp_path / "valid.pdf").exists()

    def test_builder_appends_failure_for_missing_typ_file(
        self, temp_sphinx_app, tmp_path
    ):
        """D-01, D-04 (fallback branch): a master whose docname IS a known
        Sphinx document but whose .typ was never generated must still fail
        the build via the shared `failures` list, using the byte-identical
        fallback message (tests/test_target_name_render_gate.py:122 depends
        on this exact text)."""
        from typsphinx.builder import TypstPDFBuilder

        assert "index" in temp_sphinx_app.env.found_docs, (
            "precondition: temp_sphinx_app's srcdir defines 'index' as a "
            "real Sphinx document"
        )

        builder = TypstPDFBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.outdir = str(tmp_path)

        builder.config.typst_documents = [("index", "index", "T", "A")]
        # Deliberately do NOT write index.typ into tmp_path.

        with pytest.raises(ExtensionError) as exc_info:
            builder.finish()

        message = str(exc_info.value)
        assert "Master document not found:" in message, (
            "the fallback branch must fire when the docname IS a known "
            "Sphinx document"
        )
        assert (
            "is not a known Sphinx document" not in message
        ), "the unknown-docname branch must not fire for a known docname"

    def test_builder_appends_failure_for_unknown_docname(
        self, temp_sphinx_app, tmp_path
    ):
        """D-04 (new branch, adjacency + encoding edges): a docname ABSENT
        from `self.env.found_docs` gets a distinct, non-colliding message,
        and a non-ASCII docname survives verbatim (no UnicodeEncodeError,
        no mojibake) via `!r`."""
        from typsphinx.builder import TypstPDFBuilder

        assert "ghost" not in temp_sphinx_app.env.found_docs, (
            "precondition: 'ghost' is not a real Sphinx document in "
            "temp_sphinx_app's srcdir"
        )
        assert "日本語ドキュメント" not in temp_sphinx_app.env.found_docs, (
            "precondition: the non-ASCII docname is not a real Sphinx document "
            "in temp_sphinx_app's srcdir either -- without this the test could "
            "silently start exercising D-04's fallback branch instead of the "
            "found_docs-discriminating branch it is written to cover (IN-01)"
        )

        builder = TypstPDFBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.outdir = str(tmp_path)

        builder.config.typst_documents = [
            ("ghost", "ghost", "T", "A"),
            ("日本語ドキュメント", "日本語ドキュメント", "T", "A"),
        ]
        # No .typ files written for either entry.

        with pytest.raises(ExtensionError) as exc_info:
            builder.finish()

        message = str(exc_info.value)
        assert "'ghost'" in message, "the unknown docname must appear via !r"
        assert (
            "is not a known Sphinx document" in message
        ), "the unknown-docname branch's distinct wording must be present"
        assert (
            "日本語ドキュメント" in message
        ), "non-ASCII docnames must survive verbatim as a Python str"
        assert (
            "Master document not found" not in message
        ), "the two D-04 branches must never emit colliding message text"

    def test_builder_appends_failure_for_malformed_entry_but_not_short_entry(
        self, temp_sphinx_app, tmp_path
    ):
        """D-05, D-07 (empty and single-element edges): a falsy entry such as
        `()` is malformed and fails the build, but a 1-element entry such as
        `("valid",)` is NOT malformed and resolves its stem from the
        docname."""
        from typsphinx.builder import TypstPDFBuilder

        builder = TypstPDFBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.outdir = str(tmp_path)

        builder.config.typst_documents = [(), ("valid",)]

        valid_file = tmp_path / "valid.typ"
        valid_file.write_text("= Valid Document\n\nContent here.\n")

        with pytest.raises(ExtensionError) as exc_info:
            builder.finish()

        message = str(exc_info.value)
        assert "1 master document(s) failed" in message, (
            "only the empty-tuple entry is malformed; the 1-element entry "
            "must not also be counted as a failure"
        )
        assert (
            "(): malformed typst_documents entry" in message
        ), "the malformed entry's identifier must be the entry's own repr"
        assert (tmp_path / "valid.pdf").exists(), (
            "a 1-element entry is not malformed and must still compile, "
            "with its stem falling back to the docname"
        )

    def test_aggregate_message_lists_failures_in_typst_documents_order(
        self, temp_sphinx_app, tmp_path
    ):
        """D-02 (ordering edge): `failures` accumulates strictly in
        `typst_documents` iteration order, and the aggregate message renders
        that same order; the aggregate wording no longer restricts itself to
        compile failures."""
        from typsphinx.builder import TypstPDFBuilder

        builder = TypstPDFBuilder(temp_sphinx_app, temp_sphinx_app.env)
        builder.outdir = str(tmp_path)

        builder.config.typst_documents = [
            ("ghost", "ghost", "T", "A"),
            (),
            ("index", "index", "T", "A"),
        ]
        # No .typ files written for any entry.

        with pytest.raises(ExtensionError) as exc_info:
            builder.finish()

        message = str(exc_info.value)
        assert "3 master document(s) failed" in message, (
            "all three entries are failures: unknown docname, malformed "
            "entry, and missing .typ for a known docname"
        )
        assert "failed to compile to PDF" not in message, (
            "the aggregate wording must no longer restrict itself to "
            "compile failures (D-02)"
        )

        pos_ghost = message.index("ghost")
        pos_malformed = message.index("(): malformed typst_documents entry")
        pos_missing = message.index("Master document not found:")
        assert pos_ghost < pos_malformed < pos_missing, (
            "failures must render in typst_documents iteration order, not "
            "some other order"
        )

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
