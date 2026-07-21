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
# These can be referenced in custom templates
typst_elements = {
    # Document metadata
    "author": "Sphinx-Typst Contributors",
    "date": "October 2024",
    # Page layout (examples - actual usage depends on template)
    "papersize": "a4",
    "fontsize": "11pt",
    "margin": "2.5cm",
    # Custom styling
    "primary_color": "rgb(0, 102, 204)",
    "code_font": "Fira Code",
}

# Custom template (optional)
# Uncomment to use a custom Typst template
typst_template = "_templates/custom.typ"

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

# Toctree defaults (optional)
# Set default options for all toctree directives
# Individual directives can override these
typst_toctree_defaults = {
    "maxdepth": 2,
    "numbered": True,
}

# Typst Universe packages (optional)
# Import packages from Typst Universe
# Example: Import codly for enhanced code highlighting
# typst_package_imports = [
#     '#import "@preview/codly:0.1.0": *',
#     '#import "@preview/gentle-clues:0.3.0": *',
# ]

# Debug mode (optional)
# Enable detailed logging for troubleshooting
# Can also be enabled via SPHINX_TYPST_DEBUG=1 environment variable
# typst_debug = False
