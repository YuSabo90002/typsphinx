# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib

# Add typsphinx to path for autodoc
sys.path.insert(0, os.path.abspath("../.."))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# Read version from pyproject.toml
pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
with open(pyproject_path, "rb") as f:
    pyproject_data = tomllib.load(f)
    version = pyproject_data["project"]["version"]

project = "typsphinx"
copyright = "2025, YuSabo"
author = "YuSabo"
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "typsphinx",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Internationalization (i18n) configuration -------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-locale_dirs

# Language can be set via SPHINX_LANGUAGE environment variable
language = os.getenv("SPHINX_LANGUAGE", "en")

locale_dirs = ["../locale/"]  # Path is relative to the conf.py file
gettext_compact = False  # Generate separate .pot files for each document
gettext_uuid = False  # Do not use UUIDs in .pot files
gettext_auto_build = True  # Automatically build gettext catalogs

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_title = f"{project} {release}"

# Add custom CSS for language switcher
html_css_files = [
    "custom.css",
]

# Language switcher configuration
html_context = {
    "language": language,
    "languages": [
        ("en", "English"),
        ("ja", "日本語"),
    ],
}

# Add language switcher to sidebar
html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "language-switcher.html",
        "sidebar/navigation.html",
        "sidebar/scroll-end.html",
    ]
}

# -- Options for typst/typstpdf output ---------------------------------------

typst_documents = [
    ("index", "typsphinx", project, author, "typst"),
]

# Use typsphinx for PDF generation (dogfooding!)
typst_use_mitex = True

# -- Intersphinx configuration -----------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}

# -- Autodoc configuration ---------------------------------------------------

autodoc_typehints = "description"
autodoc_member_order = "bysource"
napoleon_google_docstring = True
napoleon_numpy_docstring = True
