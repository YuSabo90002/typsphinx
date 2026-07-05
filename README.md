# typsphinx

[![CI](https://github.com/YuSabo90002/typsphinx/actions/workflows/ci.yml/badge.svg)](https://github.com/YuSabo90002/typsphinx/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/typsphinx.svg)](https://badge.fury.io/py/typsphinx)
[![Python Support](https://img.shields.io/pypi/pyversions/typsphinx.svg)](https://pypi.org/project/typsphinx/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://yusabo90002.github.io/typsphinx/)

Sphinx extension for Typst output format support.

**[📖 Documentation](https://yusabo90002.github.io/typsphinx/)** | **[🐛 Issue Tracker](https://github.com/YuSabo90002/typsphinx/issues)** | **[📦 PyPI](https://pypi.org/project/typsphinx/)**

## Overview

typsphinx is a Sphinx extension that enables generating Typst documents from reStructuredText sources. Typst is a modern typesetting system designed as an alternative to LaTeX, offering faster compilation and a more intuitive syntax.

## Features

- **Convert Sphinx documentation to Typst format**: Seamlessly transform your reStructuredText/Markdown documents
- **Standard docutils nodes**: Full support for paragraphs, sections, lists, tables, admonitions, and more
- **Mathematical expressions**:
  - LaTeX syntax via mitex (`@preview/mitex:0.2.4`)
  - Native Typst math syntax
- **Code blocks with syntax highlighting**: Using codly package (`@preview/codly:1.3.0`)
  - Automatic line numbering
  - Syntax highlighting for multiple languages
  - Highlight specific lines
- **Images and figures**: Embed images with captions and references
- **Cross-references and citations**: Maintain document structure with internal links
- **Customizable templates**: Use default or custom Typst templates
- **Direct PDF generation**: Self-contained PDF generation via typst-py (no external Typst CLI required)
- **Multi-document support**: Generate multiple Typst files with toctree integration using `#include()`

## Requirements

- Python 3.10 or higher
- Sphinx 5.0 or higher
- typst-py 0.11.1 or higher

## Installation

### From PyPI

```bash
pip install typsphinx
```

### Using uv (recommended for development)

```bash
# Clone the repository
git clone https://github.com/YuSabo90002/typsphinx.git
cd typsphinx

# Install dependencies with uv
uv sync

# For development dependencies
uv sync --extra dev
```

## Quick Start

### Basic Configuration

Configure Typst output in your `conf.py`:

```python
# conf.py

# Note: typsphinx is auto-discovered via entry points.
# Adding to extensions list is optional but recommended for clarity.
# extensions = ['typsphinx']

# Optional: Configure Typst builder
typst_use_mitex = True  # Use mitex for LaTeX math (default: True)
```

### Build Typst Output

```bash
# Generate Typst files
sphinx-build -b typst source build/typst

# Generate PDF directly
sphinx-build -b typstpdf source build/pdf
```

### Example Document

Create a simple reStructuredText document:

```rst
==============
My Document
==============

This is a paragraph with **bold** and *italic* text.

Math Example
============

Inline math: :math:`E = mc^2`

Block math:

.. math::

   \int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}

Code Example
============

.. code-block:: python

   def hello_world():
       print("Hello, Typst!")
```

This will generate a Typst file with:
- Proper heading hierarchy
- Formatted text with emphasis
- LaTeX math via mitex (or native Typst math)
- Syntax-highlighted code blocks with codly

## Advanced Usage

### Custom Templates

Create a custom Typst template:

```python
# conf.py
typst_template = '_templates/custom.typ'

typst_elements = {
    'papersize': 'a4',
    'fontsize': '11pt',
    'lang': 'ja',
}
```

### Template Parameter Mapping

Map Sphinx metadata to template parameters:

```python
# conf.py
typst_template_mapping = {
    'title': 'project',
    'authors': ['author'],
    'date': 'release',
}
```

### Multi-Document Projects

Use toctree to combine multiple documents:

```rst
.. toctree::
   :maxdepth: 2
   :numbered:

   intro
   chapter1
   chapter2
```

This generates `#include()` directives in Typst with proper heading level adjustments.

### Working with Third-Party Extensions

typsphinx integrates with Sphinx's standard extension mechanism. For custom nodes from third-party extensions (e.g., sphinxcontrib-mermaid), you can register Typst handlers in your `conf.py`:

```python
# conf.py
def setup(app):
    # Example: Support sphinxcontrib-mermaid diagrams
    if 'sphinxcontrib.mermaid' in app.config.extensions:
        from sphinxcontrib.mermaid import mermaid
        from docutils import nodes

        def typst_visit_mermaid(self, node):
            """Render Mermaid diagram as image in Typst output"""
            # Export diagram as SVG and include in Typst
            diagram_path = f"diagrams/{node['name']}.svg"
            self.add_text(f'#image("{diagram_path}")\n\n')
            raise nodes.SkipNode

        # Register with Sphinx's standard API
        app.add_node(mermaid, typst=(typst_visit_mermaid, None))
```

**How it works**:
- typsphinx uses Sphinx's standard `app.add_node()` API (no custom registry needed)
- Unknown nodes trigger `unknown_visit()` which logs a warning and extracts text content
- Users can add Typst support for any extension by registering handlers in `conf.py`

For more details, see the [Sphinx Extension API documentation](https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx.application.Sphinx.add_node).

## Configuration Options

See [docs/configuration.rst](docs/configuration.rst) for all available configuration options:

- `typst_use_mitex`: Enable/disable mitex for LaTeX math
- `typst_template`: Custom template path
- `typst_elements`: Template parameters (paper size, fonts, etc.)
- `typst_template_mapping`: Sphinx metadata to template parameter mapping
- `typst_toctree_defaults`: Default toctree options

## Development

This project uses uv for fast package management and follows TDD (Test-Driven Development) practices.

### Setup Development Environment

```bash
# Install with development dependencies
uv sync --extra dev

# Run tests (375 tests, 91% coverage)
uv run pytest

# Run tests with coverage report
uv run pytest --cov=typsphinx --cov-report=html

# Run tests across multiple Python versions
uv run tox

# Run specific tox environments
uv run tox -e lint          # Run linters (black, ruff)
uv run tox -e type          # Run type checking (mypy)
uv run tox -e py311         # Run tests on Python 3.11
uv run tox -e docs-html     # Build HTML documentation
uv run tox -e docs-pdf      # Build PDF documentation
uv run tox -e docs          # Build both HTML and PDF docs
```

### Testing Strategy

- **Unit tests**: 375 tests covering all major components
- **Integration tests**: Full build process validation
- **Example projects**: `examples/basic/` and `examples/advanced/`
- **Code coverage**: 93% overall

### Project Structure

```
typsphinx/
├── typsphinx/              # Main package
│   ├── builder.py          # Typst builder
│   ├── writer.py           # Doctree writer
│   ├── translator.py       # Node translator
│   ├── template_engine.py  # Template processor
│   ├── pdf.py              # PDF generation
│   └── templates/          # Default templates
├── tests/                  # Test suite
├── docs/                   # Documentation
├── examples/               # Example projects
└── pyproject.toml          # Project configuration
```

## Known Limitations

- **Bibliography**: BibTeX integration not yet supported
- **Glossary**: Glossary generation not yet supported

See full requirements verification in project documentation.

## Documentation

**📖 Full documentation is available at [yusabo90002.github.io/typsphinx](https://yusabo90002.github.io/typsphinx/)**

Quick links:

- [Installation Guide](https://yusabo90002.github.io/typsphinx/installation.html)
- [Quick Start](https://yusabo90002.github.io/typsphinx/quickstart.html)
- [User Guide](https://yusabo90002.github.io/typsphinx/user_guide/)
- [Configuration Reference](https://yusabo90002.github.io/typsphinx/user_guide/configuration.html)
- [Examples](https://yusabo90002.github.io/typsphinx/examples/)
- [API Reference](https://yusabo90002.github.io/typsphinx/api/)
- [Contributing Guide](https://yusabo90002.github.io/typsphinx/contributing.html)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass: `uv run pytest`
5. Submit a pull request

### Development Guidelines

- Follow TDD (Test-Driven Development)
- Maintain 80%+ code coverage
- Use black for code formatting
- Follow Sphinx extension conventions
- Add tests for all new features

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on top of [Sphinx](https://www.sphinx-doc.org/)
- Uses [Typst](https://typst.app/) for typesetting
- Integrates [mitex](https://github.com/mitex-rs/mitex) for LaTeX math
- Uses [codly](https://typst.app/universe/package/codly) for code highlighting
- Uses [gentle-clues](https://typst.app/universe/package/gentle-clues) for admonitions
- Developed with [Claude Code](https://claude.ai/code) and Kiro-style Spec-Driven Development

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

---

**Status**: Stable (v0.4.2) - Production ready
**Python**: 3.10+ | **Sphinx**: 5.0+ | **Typst**: 0.11.1+
