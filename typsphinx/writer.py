"""
Typst writer for docutils.

This module implements the TypstWriter class, which converts docutils
document trees to Typst markup.
"""

from pathlib import PurePosixPath
from typing import Any

from docutils import writers

from typsphinx.template_engine import TemplateEngine, resolve_package_for_engine
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

    @staticmethod
    def _compute_template_import_path(docname: str) -> str:
        """
        Compute the master document's import path for the shared
        ``_template.typ`` file, from the master's docname alone.

        `_write_template_file()` (``typsphinx/builder.py``) always writes
        ``_template.typ`` at the OUTDIR ROOT, unconditionally, regardless of
        where any given master document lives. The reference a master needs
        is therefore purely "climb from my own directory to the outdir root,
        then name the file" -- a function of nesting depth alone, with no
        dependence on string equality against the reserved ``_template``
        basename.

        Args:
            docname: Master document name (e.g. ``"index"``,
                ``"api/index"``, or ``"_template/index"``).

        Returns:
            The complete relative import path, including the ``.typ``
            suffix, e.g. ``"_template.typ"`` or ``"../_template.typ"``.

        Examples:
            >>> TypstWriter._compute_template_import_path("index")
            '_template.typ'
            >>> TypstWriter._compute_template_import_path("api/index")
            '../_template.typ'
            >>> TypstWriter._compute_template_import_path("_template/index")
            '../_template.typ'

        Notes:
            Closes gap ``G-22.1-4`` / review finding CR-01: the previous
            implementation relativized the master's docname against a
            synthetic sentinel target docname (the literal string
            ``"_template"``) via the translator's docname-to-docname
            relativization helper. When the master's own directory portion
            was ITSELF literally named ``_template``, that sentinel collided
            with a real path component, and the helper's same-directory
            resolution logic produced a stem-less result that, once
            concatenated with ``".typ"``, was malformed (e.g. a bare
            ``"..typ"`` or ``"../.typ"``). Computing the upward-segment count
            directly from the master's own directory depth removes the
            string-equality dependence entirely, so no directory name can
            ever collide with or impersonate the reserved basename.
        """
        depth = len(PurePosixPath(docname).parent.parts)
        return "".join(["../"] * depth) + "_template.typ"

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
        raw_template_path = getattr(config, "typst_template", None)
        typst_package = getattr(config, "typst_package", None)

        template_path = raw_template_path
        if template_path:
            # Resolve relative path from source directory
            import os

            source_dir = self.builder.srcdir
            template_path = os.path.join(source_dir, template_path)

        # D-01/D-03 routing decision -- see `resolve_package_for_engine()` for
        # the rule and why it lives in exactly one place (WR-04). The both-set
        # case is announced with a build warning in builder.py's
        # `_write_template_file()` (which runs once per build, unlike this
        # per-document method).
        package_for_engine = resolve_package_for_engine(
            typst_package, raw_template_path
        )

        # Create template engine
        template_engine = TemplateEngine(
            template_path=template_path,
            search_paths=[self.builder.srcdir],
            parameter_mapping=getattr(config, "typst_template_mapping", None),
            typst_package=package_for_engine,
            typst_template_function=getattr(config, "typst_template_function", None),
            typst_package_imports=getattr(config, "typst_package_imports", None),
            typst_authors=getattr(config, "typst_authors", None),
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

        # Render with template (using separate template file).
        #
        # `_write_template_file()` (builder.py) always writes `_template.typ`
        # at the OUTDIR ROOT, regardless of where the master document itself
        # lives. For a root-level master this is a same-directory reference
        # and a bare "_template.typ" resolves correctly, but for a master at
        # a nested docname (e.g. "api/index") a bare "_template.typ" would
        # resolve relative to the master's own directory ("api/_template.typ")
        # -- a file that was never written -- exactly the same docname-
        # relative-vs-outdir-root basis mismatch PDF-02 fixes for #include()/
        # image(). Reusing the translator's docname-to-docname relativizer
        # with a synthetic "_template" sentinel target was the CR-01 defect
        # (gap G-22.1-4): the sentinel can collide with a real directory
        # component of the master's own path (a master whose directory is
        # itself literally named "_template"), producing a malformed
        # reference. The depth-based computation below has no such string
        # dependence -- it is a pure function of the master's own nesting
        # depth to the outdir root.
        #
        # D-01: a package configured ALONE (no custom template) must not
        # reference that shared template file -- `_write_template_file()`
        # (builder.py) deliberately never writes it for that case, and the
        # previous unconditional computation below (BUG-A) produced a
        # master that imported a file the builder refused to create,
        # making the entire package-alone path unbuildable.
        if typst_package and not raw_template_path:
            template_file = None
        else:
            template_file = TypstWriter._compute_template_import_path(docname)
        self.output = template_engine.render(params, body, template_file=template_file)
