# typsphinx

[![CI](https://github.com/YuSabo90002/typsphinx/actions/workflows/ci.yml/badge.svg)](https://github.com/YuSabo90002/typsphinx/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/typsphinx.svg)](https://badge.fury.io/py/typsphinx)
[![Python Support](https://img.shields.io/pypi/pyversions/typsphinx.svg)](https://pypi.org/project/typsphinx/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://app.readthedocs.org/projects/typsphinx/badge/?version=latest)](https://typsphinx.readthedocs.io/)

Sphinx extension for Typst output format support.

**[📖 Documentation](https://typsphinx.readthedocs.io/)** | **[🐛 Issue Tracker](https://github.com/YuSabo90002/typsphinx/issues)** | **[📦 PyPI](https://pypi.org/project/typsphinx/)**

## Overview

typsphinx is a Sphinx extension that enables generating Typst documents from reStructuredText sources. Typst is a modern typesetting system designed as an alternative to LaTeX, offering faster compilation and a more intuitive syntax.

## Features

- **Convert Sphinx documentation to Typst format**: Seamlessly transform your reStructuredText/Markdown documents
- **Standard docutils nodes**: Full support for paragraphs, sections, lists, tables, admonitions, and more
- **Mathematical expressions**: LaTeX syntax via mitex, or native Typst math syntax
- **Code blocks with syntax highlighting**: Using the codly package, with line numbers and highlighted lines
- **Images and figures**: Embed images with captions and references
- **Cross-references**: Maintain document structure with internal links
- **Customizable templates**: Use default or custom Typst templates
- **Direct PDF generation**: Self-contained PDF generation via typst-py (no external Typst CLI required)
- **Multi-document support**: Generate multiple Typst files with toctree integration using `#include()`
- **Graphviz diagrams**: `.. graphviz::`, `.. digraph::` and `.. graph::` DOT diagrams compile into Typst/PDF output without a Graphviz installation ([guide](https://typsphinx.readthedocs.io/en/latest/user_guide/diagrams.html))
- **Bibliographies and citations**: Plain reStructuredText citations and sphinxcontrib-bibtex `:cite:` / `.. bibliography::` render in the output ([guide](https://typsphinx.readthedocs.io/en/latest/user_guide/bibliography.html))

## Requirements

- Python 3.12 or higher
- Sphinx 9.1 or higher
- typst-py 0.15.0 or higher

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

## Documentation

**📖 Full documentation is available at [typsphinx.readthedocs.io](https://typsphinx.readthedocs.io/)**

日本語ドキュメントは [typsphinx.readthedocs.io/ja/latest/](https://typsphinx.readthedocs.io/ja/latest/) にあります。

Quick links:

- [Installation Guide](https://typsphinx.readthedocs.io/en/latest/installation.html)
- [Quick Start](https://typsphinx.readthedocs.io/en/latest/quickstart.html)
- [User Guide](https://typsphinx.readthedocs.io/en/latest/user_guide/)
- [Configuration Reference](https://typsphinx.readthedocs.io/en/latest/user_guide/configuration.html)
- [Output Layout](https://typsphinx.readthedocs.io/en/latest/user_guide/output_layout.html)
- [Examples](https://typsphinx.readthedocs.io/en/latest/examples/)
- [API Reference](https://typsphinx.readthedocs.io/en/latest/api/)
- [Contributing Guide](https://typsphinx.readthedocs.io/en/latest/contributing.html)

## Contributing

See the [Contributing Guide](https://typsphinx.readthedocs.io/en/latest/contributing.html).

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on top of [Sphinx](https://www.sphinx-doc.org/)
- Uses [Typst](https://typst.app/) for typesetting
- Integrates [mitex](https://github.com/mitex-rs/mitex) for LaTeX math
- Uses [codly](https://typst.app/universe/package/codly) for code highlighting
- Uses [gentle-clues](https://typst.app/universe/package/gentle-clues) for admonitions
- Uses [diagraph](https://typst.app/universe/package/diagraph) to render Graphviz diagrams
- Uses [typst-py](https://github.com/messense/typst-py) to perform the Typst compilation
- Developed with [Claude Code](https://claude.com/product/claude-code) and [GSD Path](https://github.com/open-gsd/gsd-path)

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

---

**Status**: Stable (v0.10.0) - Production ready
**Python**: 3.12+ | **Sphinx**: 9.1+ | **Typst**: 0.15+
