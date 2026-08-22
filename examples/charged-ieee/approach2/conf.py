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
# NOTE: typst_package is intentionally NOT set here. The file typst_template
# names below imports "@preview/charged-ieee:0.1.4" itself, and this
# approach's own template is the thing being copied to the output tree.
# Setting typst_package as well would switch typsphinx to the package-only
# route, under which no local bundle is copied at all -- so the template
# this project relies on would never reach the output directory and
# compilation would break.
typst_template = "_typst/_template.typ"
typst_template_function = "project"
