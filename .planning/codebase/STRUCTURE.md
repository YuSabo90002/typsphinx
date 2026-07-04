# Codebase Structure

**Analysis Date:** 2026-07-04

## Directory Layout

```
typsphinx/
├── typsphinx/                 # Main package
│   ├── __init__.py            # Sphinx extension entry point (setup function)
│   ├── builder.py             # TypstBuilder and TypstPDFBuilder classes
│   ├── writer.py              # TypstWriter class (document translation coordinator)
│   ├── translator.py          # TypstTranslator class (docutils node visitor)
│   ├── template_engine.py     # TemplateEngine class (template loading, rendering)
│   ├── pdf.py                 # PDF compilation utilities
│   └── templates/             # Default Typst templates
│       └── base.typ           # Default base template
├── tests/                     # Test suite
│   ├── conftest.py            # pytest configuration and shared fixtures
│   ├── roots/                 # Test root directories for Sphinx projects
│   │   └── test-basic/        # Minimal test Sphinx project
│   ├── fixtures/              # Integration test fixtures
│   │   ├── integration_basic/
│   │   ├── integration_multi_doc/
│   │   ├── integration_nested_toctree/
│   │   ├── integration_multi_level/
│   │   ├── integration_sibling/
│   │   └── integration_math_figures/
│   ├── test_*.py              # Test files (unit, integration, documentation)
│   └── test_builder.py        # Builder tests
├── docs/                      # Documentation source
│   ├── source/                # Sphinx documentation source
│   │   ├── conf.py            # Sphinx configuration for documentation
│   │   ├── index.rst          # Documentation index
│   │   ├── api/               # API documentation
│   │   ├── examples/          # Example documentation
│   │   ├── user_guide/        # User guide documentation
│   │   ├── _static/           # Static assets
│   │   └── _templates/        # Sphinx templates
│   └── locale/                # i18n translation files
├── examples/                  # Example projects
│   ├── basic/                 # Basic example
│   ├── advanced/              # Advanced example with custom template
│   └── charged-ieee/          # IEEE template examples
├── pyproject.toml             # Project metadata and dependencies
├── tox.ini                    # tox test runner configuration
├── flake.nix                  # Nix development environment
├── README.md                  # Project README
├── CHANGELOG.md               # Version history
└── LICENSE                    # MIT License
```

## Directory Purposes

**typsphinx/ (main package):**
- Purpose: Core extension implementation
- Contains: Sphinx builder, translator, template engine, PDF utilities
- Key files: __init__.py (entry point), builder.py, writer.py, translator.py, template_engine.py, pdf.py
- Deployed: Installed to site-packages via setuptools

**tests/:**
- Purpose: Test suite for quality assurance
- Contains: Unit tests, integration tests, documentation tests, test fixtures
- Key files: conftest.py (shared fixtures), test_*.py files
- Structure: roots/ for Sphinx test projects, fixtures/ for integration test data
- Run: `pytest` or `tox`

**docs/:**
- Purpose: User-facing documentation
- Contains: Sphinx documentation source (RST files)
- Key files: conf.py (documentation build config), source/index.rst (manual homepage)
- Subdirectories: api/ (API reference), user_guide/ (tutorials), examples/ (sample usage)
- Deployment: Built to HTML/Typst for publication

**examples/:**
- Purpose: Example Sphinx projects demonstrating typsphinx usage
- Contains: Complete Sphinx project directories with source files, conf.py
- Key subdirectories:
  - basic/: Minimal example showing basic setup
  - advanced/: Example with custom template
  - charged-ieee/: IEEE template integration examples (approach1, approach2)

## Key File Locations

**Entry Points:**
- `typsphinx/__init__.py`: Sphinx extension setup function; registers builders and config values
- `typsphinx/builder.py:TypstBuilder.write()`: Main build orchestration loop

**Configuration:**
- `pyproject.toml`: Project metadata, dependencies, tool configs (black, ruff, mypy, pytest)
- `typsphinx/__init__.py`: Extension configuration value registration

**Core Logic:**
- `typsphinx/builder.py`: Build lifecycle management (TypstBuilder, TypstPDFBuilder)
- `typsphinx/writer.py`: Translation orchestration and template application
- `typsphinx/translator.py`: Node-to-Typst conversion (visitor pattern implementation)
- `typsphinx/template_engine.py`: Template loading, parameter mapping, rendering

**Templates:**
- `typsphinx/templates/base.typ`: Default Typst template bundled with package

**Testing:**
- `tests/conftest.py`: pytest fixtures (rootdir, sample_doctree, temp_sphinx_app)
- `tests/test_*.py`: Individual test modules
- `tests/roots/test-basic/`: Minimal Sphinx project for testing
- `tests/fixtures/integration_*/`: Integration test project structures

**Utilities:**
- `typsphinx/pdf.py`: Typst-to-PDF compilation wrapper (compile_typst_to_pdf function)

## Naming Conventions

**Files:**
- Module files: lowercase with underscores (`builder.py`, `template_engine.py`)
- Test files: `test_<subject>.py` (e.g., `test_builder.py`, `test_admonitions.py`)
- Template files: `.typ` extension (Typst markup)
- Config files: `conf.py` (Sphinx convention)

**Directories:**
- Package directory: singular module name (`typsphinx/`)
- Test directory: `tests/`
- Documentation: `docs/`
- Examples: `examples/`
- Fixtures: grouped in `tests/fixtures/<test_name>/`
- Test root projects: `tests/roots/test-<name>/`

**Classes:**
- Builder classes: CamelCase, end with "Builder" (`TypstBuilder`, `TypstPDFBuilder`)
- Translator classes: CamelCase, end with "Translator" (`TypstTranslator`)
- Writer classes: CamelCase, end with "Writer" (`TypstWriter`)
- Engine classes: CamelCase, end with "Engine" (`TemplateEngine`)
- Exception classes: CamelCase, end with "Error" or "Exception" (`TypstCompilationError`)

**Functions:**
- Builder methods: lowercase with underscores (`get_outdated_docs`, `write_doc`, `prepare_writing`)
- Visitor methods: `visit_<node_type>`, `depart_<node_type>` (e.g., `visit_paragraph`, `depart_emphasis`)
- Utility functions: lowercase with underscores (`compile_typst_to_pdf`, `check_typst_available`)

**Variables:**
- State flags: `in_<state>` (e.g., `in_table`, `in_figure`, `in_paragraph`)
- Content buffers: `<content>_buffer` or `<content>` (e.g., `body`, `figure_caption`)
- Stack/list tracking: `<item>_stack` (e.g., `list_stack`)
- Metadata/config: descriptive names (e.g., `sphinx_metadata`, `parameter_mapping`)

## Where to Add New Code

**New Feature (e.g., supporting a new docutils node type):**
- Primary code: Add visit_<node> and depart_<node> methods in `typsphinx/translator.py`
- Tests: Create or update test file (e.g., `tests/test_<feature>.py`)
- Integration: If affects output format, may need template updates
- Config: If feature requires configuration, add via setup() in `typsphinx/__init__.py`

**New Component/Module:**
- Implementation: Create new file in `typsphinx/` directory (e.g., `typsphinx/my_feature.py`)
- Follow naming: lowercase with underscores
- Export in `typsphinx/__init__.py` if needed by other modules
- Update imports in affected modules

**New Builder or Format:**
- Implementation: Extend `TypstBuilder` in `typsphinx/builder.py`
- Override methods: `write_doc()`, `finish()`, etc. as needed
- Register in setup() function in `typsphinx/__init__.py`
- Add to entry point in `pyproject.toml` if needed

**Utilities and Helpers:**
- Shared helpers: Place in relevant module (e.g., string escaping in `translator.py`, path handling in `builder.py`)
- Cross-module utilities: Create new module in `typsphinx/` (e.g., `typsphinx/utils.py`)
- Avoid creating separate utility module if only used once

**Tests:**
- Unit tests: Create `tests/test_<component>.py` for new component
- Integration tests: Add to `tests/fixtures/integration_<test_name>/` with conf.py and source RST
- Fixtures: Add pytest fixtures to `tests/conftest.py` if reusable
- Test structure: Follow existing patterns (use conftest fixtures, test apps)

**Documentation:**
- API docs: Add docstrings to classes/functions (parsed by sphinx-autodoc-typehints)
- User guide: Add to `docs/source/user_guide/`
- Examples: Create example project in `examples/<name>/` with README and source
- Configuration examples: Document in `docs/source/api/configuration.rst`

## Special Directories

**typsphinx/templates/:**
- Purpose: Bundled default Typst templates
- Generated: No (committed to git)
- Committed: Yes
- Usage: Loaded by TemplateEngine if no custom template specified
- Access: Via package_dir in `template_engine.py:TemplateEngine.get_default_template_path()`

**tests/roots/:**
- Purpose: Minimal Sphinx projects for unit tests
- Generated: No
- Committed: Yes
- Contents: Each test-<name>/ contains conf.py and index.rst
- Access: Referenced by SphinxTestApp fixture in tests

**tests/fixtures/:**
- Purpose: Test data structures for integration tests
- Generated: No
- Committed: Yes
- Structure: Each integration_<test_name>/ contains complete Sphinx project with source/ subdirectory
- Includes: conf.py, index.rst, and test-specific content (chapters, complex structures, images)

**docs/locale/:**
- Purpose: i18n translation files
- Generated: Partially (translations, pot files updated via Sphinx intl)
- Committed: Yes (for completed translations)
- Contents: Organized by language code (e.g., ja/, de/) with LC_MESSAGES subdirectories

**build/:**
- Purpose: Build output directory (created during tests and documentation builds)
- Generated: Yes (by sphinx-build, tox, etc.)
- Committed: No (.gitignore excludes)
- Contents: Generated artifacts (HTML, Typst, PDF, etc.)

---

*Structure analysis: 2026-07-04*
