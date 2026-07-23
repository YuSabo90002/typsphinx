# Advanced Sphinx-Typst Example

This advanced example demonstrates the full capabilities of `typsphinx`, including:

- Multi-document projects with toctree
- Advanced mathematics with mitex
- Cross-references and labels
- Tables and figures
- Code highlighting with multiple languages
- Custom Typst templates (optional)

## Project Structure

```
advanced/
├── conf.py                 # Sphinx configuration with advanced options
├── index.rst               # Master document with toctree
├── chapter1.rst            # Chapter 1: Mathematical content
├── chapter2.rst            # Chapter 2: Figures and tables
├── _templates/             # Custom template directory
│   └── custom.typ          # Example custom Typst template
├── README.md               # This file
└── _build/                 # Build output (generated)
    ├── typst/              # Typst markup files (.typ)
    └── pdf/                # PDF files (if using typstpdf builder)
```

## Prerequisites

- Python 3.9 or higher
- Sphinx 5.0 or higher
- typsphinx installed

## Installation

If you haven't installed typsphinx yet:

```bash
pip install typsphinx
```

Or install from source:

```bash
cd /path/to/typsphinx
pip install -e .
```

## Building the Documentation

### Generate Typst Output

Build the multi-document project:

```bash
sphinx-build -b typst . _build/typst
```

This will generate:
- `_build/typst/advanced-example.typ` - Master document
- `_build/typst/chapter1.typ` - Chapter 1
- `_build/typst/chapter2.typ` - Chapter 2

The master document (`advanced-example.typ`) uses `#include()` directives to
combine all chapters into a single document structure.

### Generate PDF Output

To directly generate PDF files:

```bash
sphinx-build -b typstpdf . _build/pdf
```

This creates both `.typ` and `.pdf` files in `_build/pdf/`.

### Using Custom Template

To use the custom template, edit `conf.py` and uncomment:

```python
typst_template = '_templates/custom.typ'
```

Then rebuild:

```bash
sphinx-build -b typst . _build/typst
```

The custom template provides:
- Custom title page
- Styled headings with color
- Page headers and numbering
- Table of contents
- Custom typography

## Features Demonstrated

### 1. Multi-Document Organization

The project uses Sphinx's `toctree` directive to organize content:

```rst
.. toctree::
   :maxdepth: 2
   :numbered:

   chapter1
   chapter2
```

This generates Typst `#include()` directives:

```typst
{
  #set heading(offset: 1)
  #include("chapter1.typ")
}

{
  #set heading(offset: 1)
  #include("chapter2.typ")
}
```

### 2. Mathematical Content

Supports both inline and block mathematics:

**Inline:** `:math:`E = mc^2`` → `#mi(`E = mc^2`)`

**Block with label:**

```rst
.. math::
   :label: equation-name

   x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
```

Reference equations: `:eq:`equation-name``

### 3. Cross-References

- **Section references:** `:ref:`section-label``
- **Document references:** `:doc:`chapter1``
- **Equation references:** `:eq:`equation-label``
- **External links:** `` `Text <URL>`_ ``

### 4. Tables

Supports list-tables with headers, spanning, and mathematical content:

```rst
.. list-table:: Title
   :header-rows: 1
   :widths: 25 25 50

   * - Column 1
     - Column 2
     - Column 3
   * - Data
     - Data
     - Data
```

### 5. Code Highlighting

Multi-language syntax highlighting using codly:

```rst
.. code-block:: python

   def example():
       return "Code with syntax highlighting"
```

Supported languages: Python, Rust, JavaScript, C, C++, Java, and many more.

### 6. Admonitions

Special boxes for notes, warnings, tips using gentle-clues package:

```rst
.. note::
   This is a note (rendered as #info[]).

.. warning::
   This is a warning (rendered as #warning[]).

.. tip::
   This is a tip (rendered as #tip[]).

.. important::
   This is important (rendered as #warning(title: "Important")[]).

.. seealso::
   See also section (rendered as #info(title: "See Also")[]).
```

All admonitions are automatically converted to beautiful colored boxes using the
[gentle-clues](https://typst.app/universe/package/gentle-clues) package.

## Configuration Options

Key configuration options in `conf.py`:

### Basic Configuration

```python
# Typst builder extension
extensions = ['typsphinx']

# Define output documents
typst_documents = [
    ('index', 'advanced-example.typ', 'Title', 'Author'),
]

# Math rendering with mitex
typst_use_mitex = True

# Custom elements for templates
typst_elements = {
    'author': 'Author Name',
    'date': 'October 2024',
    'papersize': 'a4',
    'primary_color': 'rgb(0, 102, 204)',
}
```

### Advanced Configuration

This example demonstrates additional advanced options:

```python
# Custom template (optional)
typst_template = '_templates/custom.typ'

# Template parameter mapping (optional)
# Customize how Sphinx metadata maps to template parameters
# typst_template_mapping = {
#     'project': 'doc_title',
#     'author': 'doc_authors',
#     'release': 'doc_version',
# }

# Toctree defaults (optional)
# Set default options for all toctree directives
typst_toctree_defaults = {
    'maxdepth': 2,
    'numbered': True,
}

# Typst Universe packages (optional)
# Import additional packages from Typst Universe
# typst_package_imports = [
#     '#import "@preview/codly:0.1.0": *',
#     '#import "@preview/gentle-clues:0.3.0": *',
# ]

# Debug mode (optional)
# Enable for detailed logging
# typst_debug = False
```

See [Configuration Reference](../../docs/configuration.rst) for complete documentation of all options.

## Troubleshooting

### toctree Not Generating #include()

Make sure you're using the Typst builder (`-b typst`), not another builder.
The Typst builder preserves toctree nodes for conversion to `#include()`.

### Math Not Rendering

Ensure `typst_use_mitex = True` in `conf.py`. The mitex package must be
available in your Typst installation.

### Custom Template Not Applied

1. Check that `typst_template` points to the correct file
2. Verify the template file exists
3. Ensure the template uses the `project()` function signature

### Cross-References Not Working

1. Check that labels are defined with `.. _label-name:`
2. Use the correct reference syntax (`:ref:`, `:doc:`, `:eq:`)
3. Verify document names match file names (without `.rst` extension)

## Next Steps

After exploring this example:

1. Try modifying the custom template in `_templates/custom.typ`
2. Add your own chapters and content
3. Experiment with different Typst packages
4. Customize styling and layout

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [Typst Documentation](https://typst.app/docs/)
- [mitex Package](https://typst.app/universe/package/mitex)
- [codly Package](https://typst.app/universe/package/codly)
- [typsphinx Repository](https://github.com/your-repo/typsphinx)

## Support

For issues and questions:

- GitHub Issues: https://github.com/your-repo/typsphinx/issues
- Documentation: https://typsphinx.readthedocs.io/
