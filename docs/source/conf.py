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
    "myst_parser",
    "typsphinx",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Internationalization (i18n) configuration -------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-locale_dirs


def _resolve_language():
    return os.getenv("READTHEDOCS_LANGUAGE", os.getenv("SPHINX_LANGUAGE", "en"))


# READTHEDOCS_LANGUAGE (RTD's Language setting) wins over SPHINX_LANGUAGE (local/CI override); defaults to "en".
language = _resolve_language()

locale_dirs = ["../locale/"]  # Path is relative to the conf.py file
gettext_compact = False  # Generate separate .pot files for each document
gettext_uuid = False  # Do not use UUIDs in .pot files
gettext_auto_build = True  # Automatically build gettext catalogs

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_title = f"{project} {release}"

# -- Options for typst/typstpdf output ---------------------------------------

typst_documents = [
    ("index", "typsphinx", project, author, "typst"),
]

# Use typsphinx for PDF generation (dogfooding!)
typst_use_mitex = True

# Gap-closure round (Phase 30.1, Plan 11, owner-selected option-b): a custom
# Typst template with explicit font selection, applying to BOTH the English
# and Japanese builds because this file is shared byte-for-byte between the
# `typsphinx` (en) and `typsphinx-doc-translations` (ja) Read the Docs
# projects (30.1-EVIDENCE.md SS "Gap round -- SC#4 root cause..." SS "A
# structural fact that bears directly on the option menu"). Typst's
# automatic font-fallback search silently failed to select a glyph for three
# ordinary CJK Unified Ideographs (発/単/釈) in the Japanese PDF, despite the
# RTD build container having several fonts -- including HanaMinA, the exact
# font Typst used for hundreds of other kanji in the same document -- that
# declare glyph coverage for all three
# (30.1-EVIDENCE.md SS "Gap round -- SC#4 font measurement inside the RTD
# build container"). This is an UNPROVEN fix attempt, owner-authorized via
# `fix_option=option-b` / `accept_phase29_impact=yes`
# (30.1-EVIDENCE.md SS "Gap round -- SC#4 fix decision, owner's reply").
# See docs/source/_typst/custom_template.typ for the font list and its
# measurement basis.
typst_template = "_typst/custom_template.typ"

# CONF-12/D-I: as of typsphinx 0.7.1, the extension itself auto-derives the
# `lang` template parameter from Sphinx's `language` config on every
# non-package template route, including the explicit `typst_template` set
# above -- `TemplateEngine.uses_bundled_default_template()` was narrowed to
# its `typst_package` guard alone. This file no longer needs to reconstruct
# `typst_elements["lang"]` by hand; do not re-add that workaround.

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
