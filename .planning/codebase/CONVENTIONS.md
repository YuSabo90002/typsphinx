# Coding Conventions

**Analysis Date:** 2026-07-04

## Naming Patterns

**Files:**
- Snake case with lowercase letters: `builder.py`, `translator.py`, `template_engine.py`, `pdf.py`, `writer.py`
- Test files follow pattern: `test_*.py` (e.g., `test_builder.py`, `test_config.py`)
- Template files in `typsphinx/templates/` directory (e.g., `base.typ`)

**Classes:**
- PascalCase: `TypstBuilder`, `TypstPDFBuilder`, `TypstTranslator`, `TypstWriter`, `TemplateEngine`, `TypstCompilationError`
- Sphinx visitor pattern allowed exception: `SphinxTranslator`-derived classes use docutils visitor naming

**Functions:**
- Snake case: `setup()`, `get_outdated_docs()`, `get_target_uri()`, `prepare_writing()`, `write_doc()`, `astext()`, `add_text()`, `load_template()`
- Private methods: Leading underscore: `_try_load_file()`, `_is_master_document()`, `_add_paragraph_separator()`, `_write_template_file()`, `_extract_error_info()`

**Variables:**
- Snake case: `docnames`, `section_level`, `figure_caption`, `table_cell_content`, `list_stack`
- Boolean flags: Descriptive names: `in_figure`, `in_table`, `in_thead`, `in_caption`, `allow_parallel`
- Module-level constants: UPPER_SNAKE_CASE: `DEFAULT_PARAMETER_MAPPING` in `typsphinx/template_engine.py` (line 35)

**Types:**
- Type hints use standard Python typing module
- Union types: `Union[str, List[str], None]`
- Optional types: `Optional[Dict[str, Any]]`
- Generic containers: `List[str]`, `Dict[str, Any]`
- Collection types: Use `dict`, `list` (not deprecated `Dict`, `List` for Python 3.9+ support)

## Code Style

**Formatting:**
- Tool: `black` (version ≥ 23.0)
- Line length: 88 characters
- Configuration: See `pyproject.toml` lines 86-99
- Target versions: Python 3.9, 3.10, 3.11, 3.12

**Linting:**
- Tool: `ruff` (version ≥ 0.1.0)
- Configuration: See `pyproject.toml` lines 101-117
- Selected rules: E, F, W, I, N, UP, B, A, C4, T20
- Ignored rules include:
  - E501: Line too long (handled by black)
  - T201: print found (allowed in tests for debugging)
  - N802: Function naming (docutils visitor pattern uses PascalCase)
  - UP035, UP006, UP028: Python 3.9 compatibility exceptions

**Type Checking:**
- Tool: `mypy` (version ≥ 1.0)
- Configuration: See `pyproject.toml` lines 119-132
- Python version target: 3.9
- Mypy overrides for `typsphinx.*` modules disable several checks for compatibility

## Import Organization

**Order (as seen in `typsphinx/builder.py`, `typsphinx/translator.py`):**
1. Standard library imports: `import shutil`, `from os import path`, `from typing import ...`
2. Third-party imports: `from docutils import nodes`, `from sphinx.builders import Builder`, `from sphinx.util import logging`
3. Local imports: `from typsphinx.pdf import compile_typst_to_pdf`, `from typsphinx.writer import TypstWriter`

**Style:**
- Imports organized alphabetically within each group
- Use explicit imports over wildcard imports
- Module-level logging setup: `logger = logging.getLogger(__name__)` at module top

**Path Aliases:**
- Not detected in codebase; uses direct imports from `typsphinx.*` package

## Error Handling

**Patterns:**
- Custom exceptions: Define exception classes extending `Exception` with docstrings
  - Example: `TypstCompilationError` in `typsphinx/pdf.py` (lines 16-57)
  - Provides message, typst_error reference, and source_location
- Try/except blocks: Catch specific exceptions with appropriate logging
  - Example: `typsphinx/builder.py` line 277-281 catches generic `Exception` when copying image files
  - Example: `typsphinx/pdf.py` line 70-78 catches `ImportError` with `raise ... from e` pattern
- Logger usage: `logger.warning()` for non-fatal issues, `logger.error()` for failures, `logger.debug()` for detailed info
- Pre-condition checks: Check file existence before operations (e.g., `typsphinx/builder.py` line 268)

**Exception Messages:**
- Include context: File paths, configuration names, original error details
- Multiple causes: Chain exceptions with `raise ... from e` (line 78 in pdf.py)
- Structured error info: Exception attributes for programmatic access (TypstCompilationError attributes at line 23-27)

## Logging

**Framework:** `sphinx.util.logging`

**Pattern:** 
```python
logger = logging.getLogger(__name__)
```
- Set at module level immediately after imports
- Used throughout module methods

**Usage Patterns:**
- `logger.info()`: Build progress and general information (e.g., "preparing documents...")
- `logger.warning()`: Non-fatal issues that don't stop the build (e.g., "Image file not found")
- `logger.error()`: Fatal errors that stop processing (e.g., "Failed to compile")
- `logger.debug()`: Detailed diagnostic information (e.g., "Loaded template from...")
- Parameter `nonl=True`: Don't add newline for multi-part logging sequences (line 119 in builder.py)

## Comments

**When to Comment:**
- Complex logic that isn't self-evident: State management transitions, workarounds
- Requirement/Task/Issue references: Link to specifications
- Example: `typsphinx/__init__.py` line 46: `# Task 13.4: Other configuration options (Requirement 8.6)`
- Example: `typsphinx/writer.py` line 75-77: `# WORKAROUND: For some Sphinx documents, visit_document may not be called`

**JSDoc/Type Documentation:**
- Full docstrings for all public classes and functions
- RST-style format with sections: summary, extended description, Args, Returns, Raises
- Example: `typsphinx/builder.py` lines 37-42 (init method)
- Parameter descriptions include type and semantic meaning
- Requirement/Task references in docstrings when applicable

**Inline Comments:**
- Explain "why", not "what": Code already shows what it does
- Reference issue/task numbers for context
- Example: `typsphinx/builder.py` line 43-45: Explains why images dictionary tracks by URI

## Function Design

**Size:**
- Methods typically 10-50 lines; longer methods break down complex operations
- Example: `TypstBuilder.write()` is ~40 lines (lines 89-137)
- Private helper methods extract single concerns

**Parameters:**
- Explicit naming over positional arguments
- Type hints for all parameters
- Default values for optional configuration
- Example: `TemplateEngine.__init__()` uses 12 parameters with defaults (lines 41-51)

**Return Values:**
- Always type-hinted (including `None` for void functions)
- Clear semantic meaning: `bool` for checks, `str` for content, `dict` for configuration
- Example: `_is_master_document()` returns `bool` with clear True/False meaning (lines 36-58 in writer.py)
- Iterator/generator types: `Iterator[str]` for `get_outdated_docs()` (line 48 in builder.py)

## Module Design

**Exports:**
- Public API classes/functions at module level
- Example: `typsphinx/__init__.py` exports `setup()` function as extension entry point
- Private helpers use leading underscore

**Barrel Files:**
- Main package `typsphinx/__init__.py` handles Sphinx integration
- Individual modules handle specific concerns (builder, translator, writer, template_engine, pdf)
- No re-exports of public APIs through __all__

**State Management:**
- Class-level attributes for configuration (`TypstBuilder.name`, `TypstBuilder.format`, `TypstBuilder.out_suffix`)
- Instance attributes initialized in `__init__()` and `init()` methods
- Translator maintains state during tree traversal (section_level, list_stack, etc.)
- State properly reset between independent operations

---

*Convention analysis: 2026-07-04*
