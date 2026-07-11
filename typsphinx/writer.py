"""
Typst writer for docutils.

This module implements the TypstWriter class, which converts docutils
document trees to Typst markup.
"""

from typing import Any

from docutils import writers

from typsphinx.template_engine import TemplateEngine
from typsphinx.translator import TypstTranslator


class TypstWriter(writers.Writer):
    """
    Writer class for Typst output format.

    This writer converts docutils document trees to Typst markup files.
    """

    supported = ("typst",)
    """Formats this writer supports."""

    def __init__(self, builder: Any) -> None:
        """
        Initialize the writer.

        Args:
            builder: The Sphinx builder instance
        """
        super().__init__()
        self.builder = builder

    def _is_master_document(self, docname: str) -> bool:
        """
        Check if the current document is a master document (defined in typst_documents).

        Master documents should have templates applied, while included documents
        (via #include()) should only contain body content.

        Args:
            docname: Document name (e.g., 'index', 'chapter1')

        Returns:
            True if this is a master document, False otherwise
        """
        config = self.builder.config
        typst_documents = getattr(config, "typst_documents", [])

        # Check if docname is in typst_documents
        # typst_documents format: [(sourcename, targetname, title, author), ...]
        for doc_tuple in typst_documents:
            if doc_tuple[0] == docname:
                return True

        return False

    def translate(self) -> None:
        """
        Translate the document tree to Typst markup.

        This method creates a TypstTranslator and visits the document tree,
        then wraps the output with a template using TemplateEngine.

        For master documents (defined in typst_documents), the full template
        is applied. For included documents, only the body content is output.
        """
        # Generate body content
        self.visitor = TypstTranslator(self.document, self.builder)
        self.document.walkabout(self.visitor)
        body = self.visitor.astext()

        # WORKAROUND: For some Sphinx documents, visit_document may not be called
        # Ensure body is wrapped in code mode block
        if not body.startswith("#{"):
            body = "#{\n" + body
        if not body.endswith("}\n"):
            body = body + "}\n"

        # Get current document name
        docname = self.builder.current_docname

        # Check if this is a master document
        is_master = self._is_master_document(docname)

        if not is_master:
            # For included documents, add essential imports but no template
            # Typst's #include() does not inherit imports from parent file,
            # so each file needs its own imports
            imports = []
            imports.append("// Essential imports for included document")
            imports.append('#import "@preview/codly:1.3.0": *')
            imports.append('#import "@preview/codly-languages:0.1.10": *')
            imports.append('#import "@preview/mitex:0.2.7": mi, mitex')
            imports.append('#import "@preview/gentle-clues:1.3.1": *')
            imports.append("")
            imports.append("// Initialize codly")
            imports.append("#show: codly-init.with()")
            imports.append("#codly(languages: codly-languages)")
            imports.append("")

            self.output = "\n".join(imports) + "\n" + body
            return

        # For master documents, apply template
        config = self.builder.config

        # Get template configuration from Sphinx config
        template_path = getattr(config, "typst_template", None)
        if template_path:
            # Resolve relative path from source directory
            import os

            source_dir = self.builder.srcdir
            template_path = os.path.join(source_dir, template_path)

        # Create template engine
        template_engine = TemplateEngine(
            template_path=template_path,
            search_paths=[self.builder.srcdir],
            parameter_mapping=getattr(config, "typst_template_mapping", None),
            typst_package=getattr(config, "typst_package", None),
            typst_template_function=getattr(config, "typst_template_function", None),
            typst_package_imports=getattr(config, "typst_package_imports", None),
            typst_authors=getattr(config, "typst_authors", None),
            typst_author_params=getattr(config, "typst_author_params", None),
        )

        # Gather Sphinx metadata
        sphinx_metadata = {
            "project": config.project,
            "author": config.author,
            "release": config.release,
            "copyright": config.copyright,
        }

        # Add custom elements from config
        typst_elements = getattr(config, "typst_elements", {})
        sphinx_metadata.update(typst_elements)

        # Map parameters
        params = template_engine.map_parameters(sphinx_metadata)

        # Extract toctree options and add to parameters
        toctree_options = template_engine.extract_toctree_options(self.document)
        params.update(toctree_options)

        # Render with template (using separate template file)
        self.output = template_engine.render(
            params, body, template_file="_template.typ"
        )
