"""
Typst writer for docutils.

This module implements the TypstWriter class, which converts docutils
document trees to Typst markup.
"""

import posixpath
from pathlib import PurePosixPath
from typing import Any

from docutils import writers
from sphinx.util import logging

from typsphinx.template_engine import (
    TemplateEngine,
    derive_typst_lang,
    resolve_package_for_engine,
)
from typsphinx.translator import TypstTranslator

logger = logging.getLogger(__name__)


def compute_content_include_path(
    wrapper_relative_dir: str, content_relative_path: str
) -> str:
    """Compute a wrapper's ``#include()`` argument for its own entry's
    content file (B-1/COMP-03 fix).

    This is a genuine two-endpoint ``posixpath.relpath`` computation, NOT
    a depth-only ``"../"`` counter like ``_compute_template_import_path``
    -- Typst's ``#include()`` resolves relative to the INCLUDING file's
    own directory (measured empirically; see 47-RESEARCH.md "Common
    Pitfalls" #3), so both the wrapper's resolved directory and the
    content file's own resolved path must be independently known. Reusing
    the depth-only shape for this job -- assuming the content file is
    always at the outdir root, and that the wrapper's directory equals
    its docname's directory -- is the literal root cause of B-1 and must
    not be reintroduced here.

    Args:
        wrapper_relative_dir: The wrapper's own resolved output
            directory, relative to the outdir root (``""`` for the
            outdir root itself).
        content_relative_path: The content file's own path, relative to
            the outdir root (e.g. ``"guide/index.typ"``).

    Returns:
        The relative path to hand to Typst's ``#include()``.

    Examples:
        >>> compute_content_include_path("", "index.typ")
        'index.typ'
        >>> compute_content_include_path("manuals", "guide/index.typ")
        '../guide/index.typ'
        >>> compute_content_include_path("guide", "guide/index.typ")
        'index.typ'
    """
    start = wrapper_relative_dir or "."
    return posixpath.relpath(content_relative_path, start=start)


def compute_template_import_path_for_dir(wrapper_relative_dir: str) -> str:
    """Compute a wrapper's import path for the shared ``_template.typ``
    file, from the WRAPPER's own resolved output directory.

    ``_write_template_file()`` (``typsphinx/builder.py``) always writes
    ``_template.typ`` at the outdir root, unconditionally, regardless of
    where any given wrapper is written -- so this is a pure function of
    the wrapper's own nesting depth. Unlike
    ``compute_content_include_path``, a depth-only ``"../"`` counter IS
    correct here, because the imported file's location (the outdir root)
    is a fixed, known constant rather than another entry's independently
    resolved path -- but the depth must come from the WRAPPER's resolved
    directory, not from the master's docname, or a wrapper written
    outside its docname's own directory would import a file that was
    never written at the depth the docname implied.

    Args:
        wrapper_relative_dir: The wrapper's own resolved output
            directory, relative to the outdir root (``""`` for the
            outdir root itself).

    Returns:
        The complete relative import path, including the ``.typ``
        suffix, e.g. ``"_template.typ"`` or ``"../_template.typ"``.

    Examples:
        >>> compute_template_import_path_for_dir("")
        '_template.typ'
        >>> compute_template_import_path_for_dir("manuals")
        '../_template.typ'
        >>> compute_template_import_path_for_dir("a/b")
        '../../_template.typ'
    """
    if not wrapper_relative_dir:
        depth = 0
    else:
        depth = len(PurePosixPath(wrapper_relative_dir).parts)
    return "".join(["../"] * depth) + "_template.typ"


def _entry_element_value(entry: tuple, index: int, default: str) -> str:
    """Read ``entry[index]`` positionally, off the SPECIFIC entry a
    wrapper is being generated for (D-08).

    A wrapper reads its title/author metadata off the specific entry it
    is being generated for, never by searching ``typst_documents`` for
    other entries that happen to share the same docname -- two entries
    naming one docname each keep their OWN title and author, so wrapper
    generation order can never decide metadata. (The docname first-match
    search that used to exist alongside this positional read was removed
    in 47-12-PLAN.md; see that plan and D-08 for the superseded shape and
    why it had no production consumer.)

    - Entry too short to have ``index``, or the element is ``None`` ->
      ``default`` (silent, D-02).
    - Element present and a ``str`` (including ``""``) -> returned
      verbatim (D-01: an empty string is a value, not a fallback signal).
    - Element present but not a ``str`` -> a logged warning naming the
      element index, the entry's docname and the value it is falling
      back to, then ``default`` (D-02).

    Args:
        entry: The specific ``typst_documents`` tuple this wrapper is
            being generated for.
        index: The tuple element to resolve (2 for title, 3 for author).
        default: The value to fall back to (``config.project`` or
            ``config.author``).

    Returns:
        The resolved ``str`` value.
    """
    if len(entry) <= index:
        return default
    value = entry[index]
    if value is None:
        return default
    if not isinstance(value, str):
        logger.warning(
            f"typst_documents element [{index}] for docname "
            f"{entry[0]!r} is not a str: {value!r} -- "
            f"falling back to {default!r}"
        )
        return default
    return value


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
        Translate the document tree to the CONTENT file's Typst markup.

        Every docname's content file is written unconditionally (COMP-01/
        OUT-03), carrying no template application -- template application
        now belongs exclusively to ``render_wrapper()``, which the
        builder calls separately, once per ``typst_documents`` entry
        naming this docname. D-06 makes the four ``@preview`` imports
        plus codly init unconditional here: this is exact status-quo
        preservation for what used to be an "included document", and it
        is only a NEW preamble for a docname that used to be a master's
        single undivided file.
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

        # D-06: unconditional for EVERY content file. Typst's #include()
        # does not inherit imports from the parent file, so each content
        # file needs its own imports regardless of whether it is also
        # #include()d by a wrapper.
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

    def render_wrapper(
        self,
        entry: tuple,
        doctree: Any,
        wrapper_relative_dir: str,
        content_relative_path: str,
    ) -> str:
        """
        Render a wrapper ``.typ`` document for one ``typst_documents``
        entry: the full template application plus a single
        ``#include()`` of that entry's own content file.

        This is the surviving half of what ``translate()`` used to do
        for a "master document" -- template application never changes
        shape, only its trigger (per-entry, not per-docname) and its
        body (an ``#include()``, not the translated doctree).

        Args:
            entry: The specific ``typst_documents`` tuple this wrapper
                is being generated for
                (docname, target, title, author[, format]).
            doctree: The master document's OWN doctree -- consulted only
                for ``extract_toctree_options()`` (toctree display
                options such as maxdepth/numbered/caption reach the
                template).
            wrapper_relative_dir: The wrapper's own resolved output
                directory, relative to the outdir root (``""`` for the
                outdir root itself).
            content_relative_path: The entry's content file's own path,
                relative to the outdir root (e.g. ``"guide/index.typ"``).

        Returns:
            The complete wrapper ``.typ`` document text.
        """
        docname = entry[0]
        include_path = compute_content_include_path(
            wrapper_relative_dir, content_relative_path
        )
        body = f'#include("{include_path}")\n'

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
        )

        # Gather Sphinx metadata. "copyright" is deliberately NOT included --
        # nothing in DEFAULT_PARAMETER_MAPPING names it and typst_elements no
        # longer rides along in this dict (D-08), so it can never reach
        # project() (structural non-leak, CONF-04/SC#4).
        #
        # D-08: "project"/"author" are read POSITIONALLY off THIS
        # wrapper's own entry tuple, via `_entry_element_value()` --
        # never via a docname first-match search over `typst_documents`.
        # Two entries naming the same docname must each keep their own
        # title/author, so wrapper generation order never decides
        # metadata.
        sphinx_metadata = {
            "project": _entry_element_value(entry, 2, config.project),
            "author": _entry_element_value(entry, 3, config.author),
            "release": config.release,
        }

        # CONF-04: typst_elements is passed to map_parameters() as its OWN
        # keyword argument -- never merged into sphinx_metadata (D-05). This
        # keeps the curated allowlist merge structurally separate from
        # baseline Sphinx metadata all the way to map_parameters(), which is
        # what makes the copyright/baseline non-leak (SC#4) a structural
        # guarantee rather than a filter (Pitfall 3).
        typst_elements = getattr(config, "typst_elements", {})

        # CONF-12/D-I: auto-derive the Typst typesetting `lang` from
        # Sphinx's `language` config on EVERY non-package route --
        # uses_bundled_default_template() is the single judgment
        # (narrowed by D-I to `not self.typst_package`), so it is now True
        # for the bundled default template, an explicit typst_template, AND
        # a <srcdir>/base.typ shadow alike; it stays False only for the
        # package-alone path, where typsphinx cannot introspect a
        # third-party function's signature (D-C) and so never hands it a
        # `lang` parameter that function never declared (SC#3). Read
        # `language` defensively via getattr and let derive_typst_lang()
        # handle a missing/malformed value -- never pre-validate or raise
        # here (D-03).
        auto_lang = None
        if template_engine.uses_bundled_default_template():
            sphinx_language = getattr(config, "language", None)
            auto_lang = derive_typst_lang(sphinx_language)

        # D-05: pre-merge the auto-derived value UNDER the user's typst_elements
        # via a plain dict union whose right-hand operand is the config
        # value -- so an explicit typst_elements["lang"] always wins on
        # collision, structurally, with zero new precedence logic inside
        # map_parameters() itself. Deliberately NEW dict/NEW name
        # (effective_elements): never reuse the bare `typst_elements` name
        # for the merged result (a copy-paste that keeps the old name
        # silently drops auto-derivation), and never mutate `typst_elements`
        # itself (it is the user's own live config value; `update()`/
        # `setdefault()` here would leak state across wrapper documents in a
        # multi-master build). The right operand is normalized with `or {}`
        # because Sphinx only WARNS on a wrong-typed config value -- a
        # conf.py setting `typst_elements = None` reaches us as None, and
        # map_parameters() has always normalized it the same way. Without
        # this, the union would raise TypeError and abort the whole build.
        effective_elements = ({"lang": auto_lang} if auto_lang else {}) | (
            typst_elements or {}
        )

        # Map parameters
        params = template_engine.map_parameters(
            sphinx_metadata, typst_elements=effective_elements
        )

        # Extract toctree options and add to parameters. Still reads the
        # MASTER's own doctree -- toctree display options belong to the
        # document that declares the toctree, unaffected by the
        # content/wrapper split.
        toctree_options = template_engine.extract_toctree_options(doctree)
        params.update(toctree_options)

        # Render with template (using separate template file).
        #
        # `_write_template_file()` (builder.py) always writes `_template.typ`
        # at the OUTDIR ROOT, regardless of where any given wrapper lives.
        # `compute_template_import_path_for_dir()` computes the import path
        # from the WRAPPER's own resolved directory (OUT-01) -- not from the
        # master's docname -- so a wrapper written outside its docname's own
        # directory still imports the file that was actually written.
        #
        # D-01: a package configured ALONE (no custom template) must not
        # reference that shared template file -- `_write_template_file()`
        # (builder.py) deliberately never writes it for that case, and an
        # unconditional computation here would produce a wrapper that
        # imports a file the builder refused to create, making the entire
        # package-alone path unbuildable.
        if typst_package and not raw_template_path:
            template_file = None
        else:
            template_file = compute_template_import_path_for_dir(wrapper_relative_dir)
        logger.debug(
            f"Rendering wrapper for docname {docname!r} at "
            f"wrapper_relative_dir={wrapper_relative_dir!r}, "
            f"include_path={include_path!r}, template_file={template_file!r}"
        )
        return template_engine.render(params, body, template_file=template_file)
