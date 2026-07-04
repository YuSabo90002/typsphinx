# Testing Patterns

**Analysis Date:** 2026-07-04

## Test Framework

**Runner:**
- pytest (version ≥ 7.0)
- Configuration: `pyproject.toml` lines 75-84
- Config file: `pyproject.toml` (pytest.ini_options section)

**Assertion Library:**
- Built-in pytest assertions (`assert` statements)
- Error messages use f-strings and context: `assert result.returncode == 0, f"sphinx-build failed:\nSTDOUT:\n{result.stdout}..."`

**Run Commands:**
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=typsphinx --cov-report=term-missing --cov-report=html tests/

# Run specific test file
pytest tests/test_builder.py

# Run tests matching pattern
pytest tests/ -k "config"

# Watch mode (use pytest-watch plugin)
ptw
```

**Tox environments (from tox.ini):**
```bash
# Run all test environments
tox

# Run specific environment
tox -e py311      # Python 3.11 tests
tox -e lint       # Code style checks (black, ruff)
tox -e type       # Type checking (mypy)
tox -e cov        # Tests with coverage
tox -e docs       # Build documentation
```

## Test File Organization

**Location:**
- Tests co-located in `/home/yuta/Documents/typsphinx/tests/` directory
- Separate from source code (not alongside source files)
- Fixture directory: `tests/fixtures/` for sample Sphinx projects
- Fixture root: `tests/roots/` for sphinx.testing.fixtures

**Naming:**
- Test files: `test_*.py` pattern
- Test classes: `Test*` pattern (e.g., `TestBasicSphinxProjectBuild`)
- Test functions: `test_*` pattern (e.g., `test_typst_builder_can_be_imported`)
- Fixtures: Function names describe what they provide (e.g., `temp_sphinx_app`, `sample_doctree`)

**Structure:**
```
tests/
├── conftest.py                        # Global fixtures and configuration
├── fixtures/                          # Sample Sphinx projects for integration tests
│   └── integration_basic/
│       ├── conf.py
│       └── index.rst
├── test_admonitions.py               # Feature tests (admonitions rendering)
├── test_builder.py                   # Builder class tests
├── test_config.py                    # Configuration handling
├── test_entry_points.py              # Package entry points
├── test_integration_basic.py          # Full build process tests
├── test_integration_advanced.py       # Complex feature integration
├── test_template_*.py                 # Template engine features
├── test_math_*.py                     # Math rendering variants
└── ... (40+ test files total)
```

## Test Structure

**Global Setup (conftest.py):**
```python
pytest_plugins = "sphinx.testing.fixtures"

@pytest.fixture(scope="session")
def rootdir():
    """Root directory for test files."""
    return Path(__file__).parent.absolute() / "roots"
```

**Session-scoped Fixtures:**
- `rootdir`: Returns path to test roots directory (persistent for entire test session)

**Function-scoped Fixtures:**
- `sample_doctree`: Creates minimal docutils document with section and paragraph
- `temp_sphinx_app`: Creates temporary Sphinx app with conf.py and index.rst
- `sphinx_config`: Dictionary with sample Sphinx configuration
- `mock_builder`: Mock builder object for unit testing translator/writer

**Test Class Pattern:**
```python
class TestBasicSphinxProjectBuild:
    """Test building a basic Sphinx project with typst builder (Task 15.1)."""

    def test_basic_project_files_exist(self, basic_project_dir):
        """Test that the basic project fixture has required files."""
        assert (basic_project_dir / "conf.py").exists()

    def test_sphinx_build_typst_succeeds(self, basic_project_dir, temp_build_dir):
        """Test that sphinx-build -b typst succeeds for basic project."""
        result = subprocess.run([...], capture_output=True, text=True)
        assert result.returncode == 0
```

## Mocking

**Framework:** 
- Manual mocks using class definitions (no pytest-mock)
- Example: `conftest.py` lines 98-114 (MockConfig, MockDomains, MockEnv, MockBuilder)

**Mock Patterns:**
```python
class MockConfig:
    pass

class MockBuilder:
    config = MockConfig()
    env = MockEnv()

# Usage in tests
def mock_builder():
    """Create a mock builder for testing."""
    return MockBuilder()
```

**What to Mock:**
- Sphinx application dependencies for unit tests
- Builder config and env objects when testing translator logic
- File system operations when testing configuration loading (use tmp_path)

**What NOT to Mock:**
- docutils nodes: Use real nodes for document tree testing
- Sphinx builders: Use SphinxTestApp for realistic builder behavior
- File I/O in integration tests: Use actual temporary files (tmp_path fixture)

## Fixtures and Factories

**Test Data Patterns:**

Directory-based fixtures (conftest.py):
```python
@pytest.fixture(scope="session")
def rootdir():
    """Root directory for test files."""
    return Path(__file__).parent.absolute() / "roots"
```

Temporary directory fixtures:
```python
def test_custom_config(tmp_path):
    """Test custom configuration loading."""
    srcdir = tmp_path / "source"
    srcdir.mkdir()
    conf_py = srcdir / "conf.py"
    conf_py.write_text("...")  # Write test config
```

Document tree factory:
```python
@pytest.fixture
def sample_doctree() -> nodes.document:
    """Create a sample doctree for testing."""
    from docutils.parsers.rst import states
    from docutils.utils import Reporter
    
    reporter = Reporter("", 2, 4)
    doc = nodes.document("", reporter=reporter)
    doc.settings = states.Struct()
    # ... setup document
    return doc
```

**Sphinx App Factory:**
```python
@pytest.fixture
def temp_sphinx_app(tmp_path: Path) -> SphinxTestApp:
    """Create a temporary Sphinx application for testing."""
    srcdir = tmp_path / "source"
    srcdir.mkdir()
    
    # Create minimal conf.py
    conf_py = srcdir / "conf.py"
    conf_py.write_text("extensions = ['typsphinx']\n...")
    
    # Create minimal index.rst
    index_rst = srcdir / "index.rst"
    index_rst.write_text("Test Document\n...")
    
    builddir = tmp_path / "build"
    app = SphinxTestApp(srcdir=srcdir, builddir=builddir)
    return app
```

**Location:**
- Shared fixtures in `tests/conftest.py`
- Test-specific fixtures defined in individual test modules with `@pytest.fixture` decorator
- Example: `test_integration_basic.py` lines 14-29 define `fixtures_dir`, `basic_project_dir`, `temp_build_dir`

## Coverage

**Requirements:** No specific coverage target enforced, but cov environment available

**View Coverage:**
```bash
# Generate HTML coverage report
tox -e cov

# Open report
open htmlcov/index.html

# View in terminal
pytest --cov=typsphinx --cov-report=term-missing tests/
```

**Command from tox.ini (line 45):**
```bash
pytest --cov=typsphinx --cov-report=term-missing --cov-report=html tests/
```

## Test Types

**Unit Tests:**
- Scope: Single class or function in isolation
- Location: `tests/test_*.py` files testing specific modules
- Example: `test_builder.py` tests TypstBuilder class methods independently
- Approach: Use mock fixtures for dependencies, assert on return values
- Sample: Lines 11-15 test TypstBuilder can be imported and inherits from Builder

**Integration Tests:**
- Scope: Multiple components working together or full build process
- Location: `tests/test_integration_*.py` files (e.g., test_integration_basic.py)
- Approach: Use SphinxTestApp to build actual Sphinx projects, subprocess.run for sphinx-build
- Sample: Lines 40-59 in test_integration_basic.py run actual sphinx-build command and verify .typ file generation
- Subprocess pattern:
  ```python
  result = subprocess.run(
      ["uv", "run", "sphinx-build", "-b", "typst", str(basic_project_dir), str(temp_build_dir)],
      capture_output=True,
      text=True,
  )
  assert result.returncode == 0, f"sphinx-build failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
  ```

**E2E Tests:**
- Not formalized; integration tests serve as E2E validation
- Full build + verification pattern in test_integration_*.py files

## Common Patterns

**Async Testing:**
- Not used; this is a synchronous Python library

**Error Testing:**
- Verify error conditions raise expected exceptions
- Assert on exception attributes
- Example: Test that missing required module raises ImportError with helpful message (pdf.py lines 70-78)

**File System Testing:**
- Use pytest's `tmp_path` fixture for temporary directories
- Write test files and assert on generated outputs
- Example: `test_integration_basic.py` line 77-79 verifies generated .typ file exists

**Parametrized Tests:**
- Not detected in current test suite
- Could be used for testing multiple input variations

**Markers:**
From `pyproject.toml` lines 81-84:
```ini
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]
```

Usage:
```python
@pytest.mark.slow
def test_slow_operation():
    pass

@pytest.mark.integration
def test_full_build():
    pass

# Run without slow tests
pytest -m "not slow"

# Run only integration tests
pytest -m integration
```

## Test Execution Details

**Test Discovery:**
- Python files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*` (configured in pyproject.toml line 79)

**Test Settings (pyproject.toml lines 75-84):**
- testpaths: ["tests"]
- python_files: ["test_*.py"]
- python_classes: ["Test*"]
- python_functions: ["test_*"]
- addopts: "-v --strict-markers" (verbose output, enforce marker registration)

**Error Message Format:**
- Multi-line detailed output on assertion failure
- Context provided via f-strings: `f"sphinx-build failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"`

---

*Testing analysis: 2026-07-04*
