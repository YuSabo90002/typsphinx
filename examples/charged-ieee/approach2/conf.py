# Configuration file for charged-ieee example (Approach 2)
# Approach 2: Use custom template with Typst code for transformation (Flexible)


# -- Project information -----------------------------------------------------
project = "Machine Learning Applications in Computer Vision"
copyright = "2025, John Doe"
author = "John Doe"
release = "1.0"

# -- General configuration ---------------------------------------------------
extensions = ["typsphinx"]

# -- Typst output options ----------------------------------------------------
typst_documents = [
    ("index", "paper", project, author, "typst"),
]

# -- Custom template configuration (Approach 2 - Flexible) ------------------
# Use custom template that wraps charged-ieee.
# NOTE: typst_package is intentionally NOT set here. _templates/_template.typ
# imports "@preview/charged-ieee:0.1.4" itself, and setting typst_package would
# switch typsphinx to the package-only path, which skips emitting _template.typ
# into the output directory and breaks compilation.
typst_template = "_templates/_template.typ"
typst_template_function = "project"
