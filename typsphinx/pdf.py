"""
PDF generation utilities using typst-py.

This module provides functionality for generating PDFs from Typst markup
using the typst Python package (Requirement 9).
"""

import logging
import os
import tempfile

logger = logging.getLogger(__name__)


class TypstCompilationError(Exception):
    """
    Exception raised when Typst compilation fails.

    This exception provides detailed information about compilation errors,
    including the original error from typst-py and contextual information.

    Attributes:
        message: Human-readable error message
        typst_error: Original error from typst compiler
        source_location: Location information if available

    Requirement 10.3: Error detection and handling
    Requirement 10.4: Error message parsing and user display
    """

    def __init__(
        self,
        message: str,
        typst_error: Exception | None = None,
        source_location: str | None = None,
    ):
        """
        Initialize TypstCompilationError.

        Args:
            message: Human-readable error description
            typst_error: Original exception from typst compiler
            source_location: Source file location information
        """
        self.message = message
        self.typst_error = typst_error
        self.source_location = source_location

        # Build full error message
        full_message = f"Typst compilation failed: {message}"
        if source_location:
            full_message += f"\nLocation: {source_location}"
        if typst_error:
            full_message += f"\nDetails: {str(typst_error)}"

        super().__init__(full_message)


def check_typst_available() -> None:
    """
    Check if typst package is available.

    Raises:
        ImportError: If typst package is not installed

    Requirement 9.1: Typst compiler functionality as dependency
    Requirement 9.7: Automatic availability of Typst compiler
    """
    try:
        import typst  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "typst package not found. Please install it:\n"
            "  pip install typst\n"
            "Or install typsphinx with PDF support:\n"
            "  pip install typsphinx[pdf]"
        ) from e


def get_typst_version() -> str:
    """
    Get the version of the typst package.

    Returns:
        Version string (e.g., "0.13.7")

    Requirement 9.7: Version information for Typst compiler
    """
    try:
        import typst

        # Try to get version from __version__ attribute
        if hasattr(typst, "__version__"):
            return typst.__version__

        # Try to get from package metadata
        try:
            from importlib.metadata import version

            return version("typst")
        except Exception:
            pass

        # Fallback
        return "unknown"
    except ImportError:
        return "not installed"


def compile_typst_to_pdf(typst_content: str, root_dir: str | None = None) -> bytes:
    """
    Compile Typst content to PDF bytes.

    Args:
        typst_content: Typst markup content
        root_dir: Root directory for resolving includes and images

    Returns:
        PDF content as bytes

    Raises:
        ImportError: If typst package not available
        TypstCompilationError: If compilation fails

    Requirement 9.2: Execute Typst compilation within Python environment
    Requirement 9.4: Generate PDF from Typst markup
    Requirement 10.3: Error detection and handling
    """
    check_typst_available()

    import typst

    # Create a temporary file for the Typst content
    # typst.compile() requires a file path, not string content
    temp_file = None
    try:
        # Create temporary file in root_dir if specified, otherwise use system temp
        temp_dir = root_dir if root_dir else None

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".typ", dir=temp_dir, delete=False, encoding="utf-8"
        ) as f:
            f.write(typst_content)
            temp_file = f.name

        # Compile Typst file to PDF
        # The typst.compile() function takes a file path and returns PDF bytes
        try:
            pdf_bytes = typst.compile(temp_file, root=root_dir)
            return pdf_bytes
        except Exception as typst_error:
            # Parse and wrap the error with more context
            error_msg = _parse_typst_error(typst_error)
            source_loc = temp_file if temp_file else "unknown"

            logger.error(f"Typst compilation failed at {source_loc}: {error_msg}")

            raise TypstCompilationError(
                message=error_msg, typst_error=typst_error, source_location=source_loc
            ) from typst_error

    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception:
                pass  # Ignore cleanup errors


def _parse_typst_error(error: Exception) -> str:
    """
    Parse Typst compiler error to extract useful information.

    Args:
        error: Original exception from typst compiler

    Returns:
        Human-readable error message

    Requirement 10.4: Error message parsing
    """
    error_str = str(error)

    # Extract meaningful information from error
    # Typst errors often contain detailed information
    if not error_str:
        return f"{type(error).__name__}"

    # Return the error string with type information
    return f"{type(error).__name__}: {error_str}"
