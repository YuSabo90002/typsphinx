"""
Sphinx Typst Extension
=======================

A Sphinx extension that provides Typst output format support.

This extension allows you to generate Typst documents from reStructuredText
sources using Sphinx, which can then be compiled to PDF using the Typst compiler.

:copyright: Copyright 2024 by Sphinx Typst Contributors
:license: MIT, see LICENSE for details.
"""

import importlib.metadata
from typing import Any, Dict

from sphinx.application import Sphinx

try:
    __version__ = importlib.metadata.version("typsphinx")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"
__author__ = "YuSabo"

from typsphinx.builder import TypstBuilder, TypstPDFBuilder


def setup(app: Sphinx) -> Dict[str, Any]:
    """
    Sphinx extension setup function.

    This function will be called by Sphinx to register the extension.

    Args:
        app: The Sphinx application instance

    Returns:
        Extension metadata dictionary
    """
    app.add_builder(TypstBuilder)
    app.add_builder(TypstPDFBuilder)

    # Register configuration values
    app.add_config_value("typst_documents", [], "html", [list])
    app.add_config_value("typst_template", None, "html", [str, type(None)])
    app.add_config_value("typst_template_mapping", None, "html", [dict, type(None)])
    app.add_config_value("typst_toctree_defaults", None, "html", [dict, type(None)])
    app.add_config_value("typst_use_mitex", True, "html", [bool])
    app.add_config_value("typst_elements", {}, "html", [dict])
    # Task 13.4: Other configuration options (Requirement 8.6)
    app.add_config_value("typst_package", None, "html", [str, type(None)])
    app.add_config_value("typst_package_imports", None, "html", [list, type(None)])
    app.add_config_value(
        "typst_template_function", None, "html", [str, dict, type(None)]
    )
    # Issue #13: Author details configuration
    app.add_config_value("typst_authors", None, "html", [dict, type(None)])
    app.add_config_value("typst_author_params", None, "html", [dict, type(None)])
    # Task 13.4: Output directory and debug mode
    app.add_config_value("typst_output_dir", "_build/typst", "html", [str])
    app.add_config_value("typst_debug", False, "html", [bool])
    # Issue #75: Template asset support
    app.add_config_value("typst_template_assets", None, "html", [list, type(None)])

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
