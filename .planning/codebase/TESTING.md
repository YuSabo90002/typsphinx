# Testing Patterns

**Analysis Date:** 2026-07-22

## Test Framework

**Runner:**
- pytest (`pytest>=8.4,<10`)
- Sphinx test fixtures plugin: `pytest_plugins = "sphinx.testing.fixtures"` in `tests/conftest.py`
- Config file: `pyproject.toml` `[tool.pytest.ini_options]`

**Assertion Library:**
- Standard `assert` statements with clear failure messages

**Run Commands:**
```bash
pytest                                    # Run all tests
pytest tests/test_translator.py           # Run single file
pytest tests/test_translator.py::TestClass::test_name  # Run single test
pytest -m "not slow"                      # Skip slow-marked tests
pytest --cov=typsphinx --cov-report=term-missing  # Coverage report
uv run pytest                             # In worktree isolation (see CLAUDE.md)
```

## Test File Organization

**Location:**
- `tests/` directory at repository root
- Test projects/fixtures in `tests/fixtures/` and `tests/roots/`
- Config: `tests/conftest.py`

**Naming:**
- Test files: `test_*.py` (pytest convention, configured in `pyproject.toml`)
- Test classes: `Test*` prefix (e.g., `TestAdmonitionConversion`, `TestBasicSphinxProjectBuild`)
- Test functions: `test_*()` prefix (e.g., `test_translator_state_initialization()`)

**File Count:**
- 145 test files total (as of 2026-07-22)
- Tests span integration, unit, configuration, and rendering validation

**Structure:**
```
tests/
├── conftest.py                    # Fixtures and configuration
├── fixtures/                      # Test project directories
│   ├── integration_basic/
│   └── [other test projects]
├── roots/                         # Sphinx test roots (required by framework)
├── test_*.py                      # Individual test files
├── test_translator.py             # Translator unit tests
├── test_builder.py                # Builder unit tests
├── test_config.py                 # Configuration tests
├── test_integration_*.py           # Integration tests
├── test_*_render_gate.py           # Rendering validation tests (gate pattern)
└── [145 test files total]
```

## Test Structure

**Suite Organization:**
```python
class TestAdmonitionConversion:
    """Test admonition node conversion using gentle-clues package."""

    def test_note_converts_to_info(self, temp_sphinx_app: SphinxTestApp):
        """Test that nodes.note converts to info[]."""
        # Arrange: create test data
        note = nodes.note()
        para = nodes.paragraph(text="This is a note.")
        note += para
        
        # Setup: create document
        doc = create_document()
        doc += note
        
        # Act: translate
        writer = TypstWriter(temp_sphinx_app.builder)
        writer.document = doc
        translator = TypstTranslator(doc, temp_sphinx_app.builder)
        doc.walkabout(translator)
        
        # Assert: verify output
        output = translator.astext()
        assert "info({" in output
        assert 'par({text("This is a note.")})' in output
```

**Patterns:**
- **Setup**: Create fixtures and test objects (docutils nodes, documents, builders)
- **Arrange-Act-Assert**: Clear separation between setup, execution, and verification
- **Fixtures**: Use `@pytest.fixture` for reusable test components
- **Assertions**: Plain `assert` with descriptive messages or string checks for output

**Example Setup Pattern (docutils document creation):**
```python
def create_document():
    """Helper function to create a minimal document with reporter."""
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False
    return doc
```

## Mocking

**Approach:** Minimal use of mocking libraries; prefer manual mock classes

**Mock Pattern from `conftest.py`:**
```python
class MockBuilder:
    """Create a mock builder for testing."""
    
    class MockConfig:
        pass
    
    class MockDomains:
        pass
    
    class MockEnv:
        domains = MockDomains()
    
    config = MockConfig()
    env = MockEnv()
```

**What to Mock:**
- Sphinx app/builder (use `temp_sphinx_app` fixture or `MockBuilder`)
- Environment/config when testing translator in isolation
- Minimal: only mock what's required to isolate the unit under test

**What NOT to Mock:**
- Docutils nodes (use real node objects for fidelity)
- Translator instances (test real translator behavior)
- Document trees (construct real trees with `nodes.document()`, `nodes.section()`, etc.)

## Fixtures and Factories

**Test Data:**

**Fixture Examples from `conftest.py`:**

1. **`sample_doctree`** (module-level fixture):
```python
@pytest.fixture
def sample_doctree() -> nodes.document:
    """Create a sample doctree for testing."""
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    doc.settings.env = None
    doc.settings.language_code = "en"
    doc.settings.strict_visitor = False
    
    section = nodes.section()
    title = nodes.title(text="Test Section")
    section += title
    para = nodes.paragraph(text="Test paragraph")
    section += para
    doc += section
    return doc
```

2. **`temp_sphinx_app`** (function-level fixture):
```python
@pytest.fixture
def temp_sphinx_app(tmp_path: Path) -> SphinxTestApp:
    """Create a temporary Sphinx application for testing."""
    srcdir = tmp_path / "source"
    srcdir.mkdir()
    
    conf_py = srcdir / "conf.py"
    conf_py.write_text("extensions = ['typsphinx']\n...")
    
    index_rst = srcdir / "index.rst"
    index_rst.write_text("Test Document\n=============\n...")
    
    builddir = tmp_path / "build"
    app = SphinxTestApp(srcdir=srcdir, builddir=builddir)
    return app
```

3. **`sphinx_config`** (function-level fixture):
```python
@pytest.fixture
def sphinx_config() -> Dict[str, Any]:
    """Sample Sphinx configuration for testing."""
    return {
        "project": "Test Project",
        "author": "Test Author",
        "version": "1.0",
        "release": "1.0.0",
        "typst_documents": [
            ("index", "output.typ", "Test Document", "Test Author"),
        ],
    }
```

4. **`rootdir`** (session-level fixture):
```python
@pytest.fixture(scope="session")
def rootdir():
    """Root directory for test files."""
    return Path(__file__).parent.absolute() / "roots"
```

**Location:**
- `tests/conftest.py`: Central fixture definitions
- Fixtures also defined inline in test files when specific to a test class

## Coverage

**Requirements:** 
- No explicit minimum enforced, but coverage tracked via CI
- `pytest-cov>=4.0` installed in dev dependencies

**View Coverage:**
```bash
pytest --cov=typsphinx --cov-report=term-missing    # Terminal report with missing lines
pytest --cov=typsphinx --cov-report=html             # HTML report in htmlcov/
tox -e cov                                            # Full coverage run via tox
```

**Configuration:**
- Config in `pyproject.toml` `[tool.pytest.ini_options]`
- Coverage section via tox: `tox -e cov`
- CI runs coverage matrix across py312, py313

## Test Types

**Unit Tests:**
- **Scope:** Individual functions, classes, translator methods
- **Example:** `test_translator_state_initialization()` in `test_translator.py`
- **Approach:** Create minimal inputs, assert on outputs
- **Isolation:** Mock external dependencies (app, builder, env)

```python
def test_translator_state_initialization(simple_document, mock_builder):
    """Test that translator initializes state variables correctly."""
    translator = TypstTranslator(simple_document, mock_builder)
    
    assert hasattr(translator, "section_level")
    assert translator.section_level == 0
    assert hasattr(translator, "in_figure")
    assert translator.in_figure is False
```

**Integration Tests:**
- **Scope:** Full Sphinx build pipeline, multiple components
- **Marker:** `@pytest.mark.integration`
- **Example:** `TestBasicSphinxProjectBuild` in `test_integration_basic.py`
- **Approach:** Invoke `sphinx-build` subprocess, check output artifacts

```python
class TestBasicSphinxProjectBuild:
    """Test building a basic Sphinx project with typst builder."""

    def test_sphinx_build_typst_succeeds(self, basic_project_dir, temp_build_dir):
        """Test that sphinx-build -b typst succeeds for basic project."""
        result = subprocess.run(
            ["uv", "run", "sphinx-build", "-b", "typst", 
             str(basic_project_dir), str(temp_build_dir)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"sphinx-build failed:\nSTDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )
```

**Rendering/Gate Tests (render_gate pattern):**
- **Scope:** Translator output validation against expected Typst syntax
- **Naming:** `test_*_render_gate.py`
- **Approach:** Build doctree, translate, assert output contains expected Typst syntax
- **Count:** 50+ gate tests validating specific rendering scenarios

**Configuration Tests:**
- **Scope:** Config value loading, defaults, custom settings
- **Example:** `test_config.py`, `test_config_template_mapping.py`
- **Approach:** Create Sphinx app with custom conf.py, verify config loaded

**E2E Tests:**
- **Not a separate category**, but integration tests serve E2E role
- Full build validation happens via subprocess invocation of `sphinx-build`

## Test Markers

**Markers defined in `pyproject.toml`:**

1. **`slow`**: Long-running tests (PDF compilation, complex integration)
   - Skip with: `pytest -m "not slow"`
   - Example: Tests invoking `sphinx-build -b typstpdf`

2. **`integration`**: Multi-component integration tests
   - Run only: `pytest -m "integration"`
   - Example: Full Sphinx build validation

**Custom pytest options:**
- `--strict-markers`: Unrecognized markers cause failure (configured via `addopts`)
- `python_files = ["test_*.py"]`: Pytest discovers test_*.py only
- `python_classes = ["Test*"]`: Test classes must start with Test
- `python_functions = ["test_*"]`: Test functions must start with test_

## Async Testing

**Not used:** This is a synchronous Sphinx extension (no async/await patterns)

## Error Testing

**Pattern:** Assert on exception type and message

```python
# Test that expected exception is raised
with pytest.raises(TypstCompilationError) as exc_info:
    compile_typst_file_to_pdf("nonexistent.typ")

# Verify exception details
assert "Typst compilation failed" in str(exc_info.value)

# Test exception chaining
assert exc_info.value.__cause__ is not None
```

**Example from error handling tests:**
```python
def test_check_typst_available_raises_import_error():
    """Test that missing typst package raises ImportError."""
    import sys
    # This would require mocking importlib, so real tests use subprocess
    pass
```

## Test Execution Environment

**Dependencies:**
- `pytest>=8.4,<10`
- `pytest-cov>=4.0`
- `sphinx>=9.1,<10` (required for SphinxTestApp)
- All dev dependencies from `pyproject.toml` `[project.optional-dependencies] dev`

**Worktree Isolation (CRITICAL):**
Per CLAUDE.md, when executing in an isolated git worktree (`.git` is a FILE, not directory):

```bash
# Step 1: Provision worktree venv
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev

# Step 2: Run all commands via uv run
uv run pytest tests/
uv run ruff check .
uv run black --check .
uv run mypy typsphinx/
```

Do **not** run tests sequentially in main tree or override isolation.

**Python Versions:**
- Tested on: Python 3.12, 3.13
- Minimum (from pyproject.toml): 3.12
- CI matrix: py312, py313 via tox

## Common Test Patterns

**Translator Testing Pattern:**

```python
def test_feature(simple_document, mock_builder):
    """Test a specific translation feature."""
    # 1. Create docutils node tree
    section = nodes.section()
    title = nodes.title(text="My Title")
    section += title
    doc = create_document()
    doc += section
    
    # 2. Walk the tree with translator
    translator = TypstTranslator(doc, mock_builder)
    doc.walkabout(translator)
    
    # 3. Get output and assert on Typst syntax
    output = translator.astext()
    assert 'heading(level: 1, {text("My Title")})' in output
```

**Configuration Testing Pattern:**

```python
def test_custom_config(tmp_path):
    """Test custom configuration loading."""
    srcdir = tmp_path / "source"
    srcdir.mkdir()
    
    # Create conf.py with custom setting
    conf_py = srcdir / "conf.py"
    conf_py.write_text("extensions = ['typsphinx']\ncustom_setting = True\n")
    
    # Create minimal index.rst
    index_rst = srcdir / "index.rst"
    index_rst.write_text("Test\n====\n\nContent.\n")
    
    builddir = tmp_path / "build"
    app = SphinxTestApp(srcdir=srcdir, builddir=builddir)
    
    # Verify config was loaded
    assert app.config.custom_setting is True
```

**Subprocess/Integration Pattern:**

```python
def test_build_succeeds(project_dir, temp_build_dir):
    """Test full build via subprocess."""
    result = subprocess.run(
        ["uv", "run", "sphinx-build", "-b", "typst",
         str(project_dir), str(temp_build_dir)],
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0, (
        f"Build failed:\n{result.stdout}\n{result.stderr}"
    )
    
    # Verify outputs exist
    assert (temp_build_dir / "index.typ").exists()
    assert len((temp_build_dir / "index.typ").read_text()) > 0
```

## Deprecation Testing

**Pattern:** Capture warnings as errors (configured in `pyproject.toml`)

```ini
[tool.pytest.ini_options]
filterwarnings = [
    "error::DeprecationWarning",
    "error::PendingDeprecationWarning",
]
```

This forces tests to fail if deprecated APIs are used, ensuring code stays current.

---

*Testing analysis: 2026-07-22*
