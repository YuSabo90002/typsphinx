# Configuration file for the Sphinx documentation builder (Advanced Example).
#
# This example demonstrates advanced features of typsphinx:
# - Multiple document support with toctree
# - Custom templates
# - Math support with mitex
# - Cross-references and labels
# - Code highlighting
# - Custom Typst elements

# -- Project information -----------------------------------------------------

project = "Advanced Sphinx-Typst Example"
copyright = "2024, Sphinx-Typst Contributors"
author = "Sphinx-Typst Contributors"
release = "1.0.0"

# -- General configuration ---------------------------------------------------

extensions = [
    "typsphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

html_theme = "alabaster"
html_static_path = []

# -- Options for Typst output ------------------------------------------------

# Define documents to be built as Typst files
# Format: (sourcename, targetname, title, author)
typst_documents = [
    (
        "index",
        "advanced-example.typ",
        "Advanced Sphinx-Typst Features",
        "Sphinx-Typst Contributors",
    ),
]

# Use mitex for LaTeX math support (default: True)
# When True, LaTeX math is converted using mitex package
# When False, LaTeX math is converted to Typst native math syntax
typst_use_mitex = True

# Custom elements for Typst templates
#
# Only keys that typsphinx allowlists are accepted -- currently
# `papersize` (string), `fontsize` (a Typst length, emitted unquoted) and
# `lang` (string). Any other key aborts the build with an ExtensionError
# naming the supported keys, rather than being silently dropped.
#
# On top of that, the *template in use* must declare a matching parameter in
# its `project()` function. `_typst/custom.typ` below declares all three;
# a template that did not would fail the Typst compile with
# `unexpected argument: papersize`. To pass template parameters beyond this
# allowlist, use `typst_template_function` with a `params` dict instead.
typst_elements = {
    "papersize": "a4",
    "fontsize": "11pt",
    "lang": "en",
}

# Custom template (optional)
# This example ships one; remove this line to fall back to the bundled default
#
# Lives in `_typst/`, a directory typsphinx owns -- deliberately NOT the
# Sphinx Jinja override directory named on line 24 above. Both directories
# coexist here on purpose: the Sphinx one keeps its own meaning (HTML theme
# overrides), while the Typst template lives somewhere that copying it
# wholesale to build output can never republish Sphinx's own directory.
typst_template = "_typst/custom.typ"

# Template parameter mapping (optional)
# Maps Sphinx metadata to custom template parameter names
# Useful when using templates that expect different parameter names
# typst_template_mapping = {
#     'project': 'doc_title',
#     'author': 'doc_authors',
#     'release': 'doc_version',
# }

# Template function name (optional)
# Specify the name of the template function to call
# Auto-detected if not specified
# typst_template_function = 'project'

# Typst Universe packages (optional)
# Import packages from Typst Universe
# Example: Import codly for enhanced code highlighting
# typst_package_imports = [
#     '#import "@preview/codly:1.3.0": *',
#     '#import "@preview/gentle-clues:1.3.1": *',
# ]

# Debug mode (optional)
# Enable detailed logging for troubleshooting
# Can also be enabled via SPHINX_TYPST_DEBUG=1 environment variable
# typst_debug = False
