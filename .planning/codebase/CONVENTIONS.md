# Coding Conventions

**Analysis Date:** 2026-07-22

## Naming Patterns

**Files:**
- Snake case for module files: `builder.py`, `translator.py`, `template_engine.py`, `pdf.py`, `writer.py`
- Test files follow pattern `test_*.py`: `test_translator.py`, `test_builder.py`, `test_config.py`
- Underscore prefix for internal/private modules: `_template.typ` (shared template artifact, not a module)

**Classes:**
- PascalCase for all classes: `TypstBuilder`, `TypstTranslator`, `TypstWriter`, `TemplateEngine`, `TypstCompilationError`
- Visitor pattern methods use PascalCase: `visit_section`, `depart_section`, `visit_title`, `depart_title` (required by docutils pattern, exception to naming rules)
- Test classes: `TestAdmonitionConversion`, `TestBasicSphinxProjectBuild` (prefix `Test`)

**Functions:**
- Snake case for all functions: `escape_typst_string()`, `resolve_package_for_engine()`, `check_typst_available()`, `get_typst_version()`, `compile_typst_file_to_pdf()`
- Helper functions with leading underscore: `_parse_typst_error()`, `_is_master_document()`, `_compute_master_included_docnames()`
- Test functions: `test_*()` pattern, e.g., `test_translator_state_initialization()`, `test_basic_project_files_exist()`

**Variables:**
- Snake case for local and module-level variables: `section_level`, `in_figure`, `in_table`, `list_stack`, `body`, `output`
- Boolean flags use clear affirmative names: `in_literal_block`, `in_definition_list`, `paragraph_has_content`, `is_first_list_item`
- State tracking variables: `_saved_body_for_figure_caption`, `_figure_block_width`, `_list_item_stack`, `_inline_concat_stack`
- Constants in UPPER_CASE with descriptive names: `_TYPST_PASSTHROUGH_UNITS`, `DEFAULT_PARAMETER_MAPPING`

**Types:**
- Generic types imported from `typing`: `List`, `Dict`, `Tuple`, `Any`, `Set`, `Iterator`
- Modern union syntax preferred when targeting Python 3.12+: `str | None` rather than `Optional[str]`
- Use `list[str]`, `dict[str, Any]` style type hints for Python 3.12+ (kept as `List`, `Dict` in some places for 3.10 compatibility per CLAUDE.md)

## Code Style

**Formatting:**
- **Tool:** Black (`black>=26,<27`)
- **Line length:** 88 characters (black default)
- **Run before commit:** `black --check .` (CI verifies; `black .` to format)

**Linting:**
- **Tool:** Ruff (`ruff>=0.15,<0.16`)
- **Selected rules:** E, F, W, I, N, UP, B, A, C4, T20
- **Ignored rules:**
  - `E501`: Line too long (black handles wrapping)
  - `T201`: Print statements (allowed in tests for debugging)
  - `B017`: Blind exception assertions (used in tests)
  - `UP035`, `UP006`: Deprecation upgrades (Python 3.10+ support)
  - `UP028`: Yield from optimization (minor, skipped)
  - `N802`: Function naming (docutils `visit_*`/`depart_*` methods use PascalCase by pattern)
  - `A001`: Shadowing builtins (`copyright` in conf.py is Sphinx convention)
  - `F841`: Unused variables (acceptable in tests and mocks)
- **Run:** `ruff check .`

**Type Checking:**
- **Tool:** mypy (`mypy>=1.13,<3.0`)
- **Config location:** `pyproject.toml` `[tool.mypy]`
- **Module-specific overrides:** `typsphinx.*` module has lenient error codes disabled:
  - `var-annotated`, `arg-type`, `override`, `misc`, `union-attr`, `attr-defined`, `list-item`
- **Run:** `mypy typsphinx/`

## Import Organization

**Order (strict):**
1. Standard library imports: `import os`, `from pathlib import Path`, `from typing import Any, Dict`
2. Third-party imports: `from docutils import nodes`, `from sphinx.builders import Builder`, `from sphinx.util import logging`
3. Local imports: `from typsphinx.builder import TypstBuilder`, `from typsphinx.translator import TypstTranslator`

**Example from `builder.py`:**
```python
import os
import shutil
from collections.abc import Iterator
from os import path
from typing import List, Set, Tuple

from docutils import nodes
from sphinx.builders import Builder
from sphinx.errors import ExtensionError
from sphinx.util import logging
from sphinx.util.osutil import ensuredir

from typsphinx.pdf import compile_typst_file_to_pdf
from typsphinx.writer import TypstWriter
```

**Path Aliases:**
- None currently used; use absolute imports from `typsphinx.*`

**Specific to Tests:**
- Sphinx test fixtures: `from sphinx.testing.util import SphinxTestApp`
- Sphinx fixtures plugin: `pytest_plugins = "sphinx.testing.fixtures"` (in `conftest.py`)

## Error Handling

**Pattern:**
- Define custom exceptions inheriting from `Exception` with detailed context
- Provide `message`, backing error (`typst_error`), and `source_location` attributes
- Log errors via the logging module before raising

**Example from `pdf.py`:**
```python
class TypstCompilationError(Exception):
    """Exception raised when Typst compilation fails."""
    
    def __init__(
        self,
        message: str,
        typst_error: Exception | None = None,
        source_location: str | None = None,
    ):
        self.message = message
        self.typst_error = typst_error
        self.source_location = source_location
        full_message = f"Typst compilation failed: {message}"
        if source_location:
            full_message += f"\nLocation: {source_location}"
        if typst_error:
            full_message += f"\nDetails: {str(typst_error)}"
        super().__init__(full_message)
```

**Raising:**
- Use `from` clause to chain exceptions: `raise TypstCompilationError(...) from typst_error`
- Catch broad exceptions in boundary functions, convert to domain-specific exceptions

**Example from `pdf.py`:**
```python
try:
    pdf_bytes = typst.compile(typ_path, root=root_dir)
    return pdf_bytes
except Exception as typst_error:
    error_msg = _parse_typst_error(typst_error)
    logger.error(f"Typst compilation failed at {typ_path}: {error_msg}")
    raise TypstCompilationError(
        message=error_msg, typst_error=typst_error, source_location=typ_path
    ) from typst_error
```

**Warnings:**
- Escalate deprecations as errors in tests: `filterwarnings = ["error::DeprecationWarning", "error::PendingDeprecationWarning"]` (see `pyproject.toml`)

## Logging

**Framework:** Python's standard `logging` module via `getLogger(__name__)`

**Pattern (per module):**
```python
import logging
logger = logging.getLogger(__name__)
```

**Use:**
- `logger.error()` for errors (e.g., "Typst compilation failed")
- `logger.warning()` for warnings (e.g., "Both typst_template and typst_package configured")
- `logger.info()` for informational messages
- Avoid `print()` except in test debugging (ruff allows `T201` in tests)

**Example from `pdf.py`:**
```python
logger.error(f"Typst compilation failed at {typ_path}: {error_msg}")
```

## Comments

**When to Comment:**
- Block comments for complex logic blocks explaining the "why"
- Inline comments for non-obvious single-line logic
- Algorithm-specific or bug-reference comments explaining decisions

**Example from `translator.py` (complex state management):**
```python
# Code-mode inline concatenation (single source of truth)
#
# A def-list term (the code-mode 1st arg of terms.item), a link body (the
# 2nd arg of link()), and a desc parameter list are all Typst code-mode
# positions where two juxtaposed expressions are a syntax error
# ("expected comma"). Adjacent inline sibling expressions in any of these
# contexts must therefore be joined with " + ". The helpers below are the
# ONE place that decides "which concat context is active" and "is this the
# first sibling or a following one", so every inline visitor -- the leaf
# visit_Text / visit_literal AND the block-opening visit_emphasis /
# visit_strong / visit_reference -- participates uniformly.
```

**Docstrings (Google style):**
- One-liner for simple functions/classes
- Multi-line with sections for complex functions

**Example from `pdf.py`:**
```python
def compile_typst_file_to_pdf(typ_path: str, root_dir: str | None = None) -> bytes:
    """
    Compile a Typst FILE (already on disk) to PDF bytes.

    Unlike compile_typst_to_pdf(), this takes a path directly -- no temporary
    file is created. The caller is responsible for ``typ_path`` already being
    at its real, intended location so that relative ``#include()`` /
    ``image()`` / ``read()`` paths inside it resolve correctly: Typst
    resolves relative paths against the file containing the call, not
    against ``root_dir``.

    Args:
        typ_path: Path to an existing .typ file to compile.
        root_dir: Typst project root (bounds relative/absolute path escape).

    Returns:
        PDF content as bytes.

    Raises:
        ImportError: If typst package not available.
        TypstCompilationError: If compilation fails. ``source_location`` is
            the real ``typ_path`` (not a temporary filename), so error
            locations are actionable for users.
    """
```

**Visitor Methods:**
- Docstrings include Args, no explicit Returns section (return is None)

**Example from `translator.py`:**
```python
def visit_section(self, node: nodes.section) -> None:
    """
    Visit a section node.

    Args:
        node: The section node
    """
```

## Function Design

**Size:**
- Aim for functions under 50 lines; break at logical boundaries
- Large visitor methods (e.g., `visit_paragraph`) may exceed this due to state tracking needs
- Helper methods extract reusable logic (e.g., `_parse_typst_error()`)

**Parameters:**
- Use type hints for all parameters
- Prefer explicit keyword arguments for configuration (e.g., `root_dir: str | None = None`)
- Avoid long parameter lists (>4); use config objects or dataclasses if needed

**Return Values:**
- Always specify return type, even if `None`
- Use `-> bytes` for binary, `-> str` for text, `-> None` for side effects
- Visitor methods return `None` by pattern

**Example from `writer.py` (static helper):**
```python
@staticmethod
def _compute_template_import_path(docname: str) -> str:
    """Compute the master document's import path for the shared _template.typ file."""
    depth = len(PurePosixPath(docname).parent.parts)
    return "".join(["../"] * depth) + "_template.typ"
```

## Module Design

**Exports:**
- Public API classes and functions defined at module top level
- Private helpers prefixed with underscore: `_parse_typst_error()`, `_is_master_document()`
- No explicit `__all__`, but convention is respected

**Module Docstrings:**
- Brief description of module purpose
- Example from `builder.py`:
```python
"""
Typst builder for Sphinx.

This module implements the TypstBuilder class, which is responsible for
building Typst output from Sphinx documentation.
"""
```

**Module Structure (typical):**
1. Module docstring
2. Imports (stdlib, third-party, local)
3. Logger setup
4. Private module-level constants
5. Private helper functions
6. Public classes
7. Public functions

---

*Convention analysis: 2026-07-22*
