"""
Template engine for Typst document generation.

This module implements template loading, parameter mapping, and rendering
for Typst documents (Requirement 8).
"""

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from sphinx.errors import ExtensionError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RawTypst:
    """Wraps a string that must be emitted into the ``.typ`` output
    VERBATIM -- no quoting, no escaping -- e.g. a Typst length literal like
    ``20pt``.

    Recognized by ``_format_typst_value()``, whose ``isinstance`` branch is
    checked BEFORE the ``str`` branch, so a ``RawTypst`` value never
    re-enters string quoting (the double-formatting trap, CONTEXT.md
    D-02/D-07). This is the type-safe alternative to pre-rendering a value
    to a Typst-source string inside ``map_parameters()`` -- a pre-rendered
    plain ``str`` is indistinguishable from any other string once it reaches
    ``_format_typst_value()`` and would be quoted a second time.
    """

    source: str


@dataclass(frozen=True)
class TemplateResolution:
    """Records which of ``TemplateEngine.resolve_template()``'s three
    priorities actually resolved, as a side effect of the SAME priority walk
    ``load_template()`` already performs -- never a second, independently
    derived check (CONF-07/D-06 explicitly rejects duplicating the priority
    logic in a second place).
    """

    content: str
    """The loaded template content, identical to what ``load_template()``
    returns for the same engine state."""

    source: str
    """One of the three literal values ``"explicit"`` (Priority 1, an
    explicit ``template_path`` that was found), ``"search"`` (Priority 2, a
    ``search_paths`` hit -- this is also where the ``<srcdir>/base.typ``
    shadow of the bundled default lives), or ``"default"`` (Priority 3, the
    bundled ``templates/base.typ``)."""


class _ElementsEmissionKind:
    """Enum-like sentinel values naming HOW an ``ELEMENTS_ALLOWLIST`` key
    must be formatted for Typst emission -- not the value itself."""

    STRING = "string"
    RAW = "raw"


# CONF-04/CONF-07: the curated, hand-maintained allowlist of `typst_elements`
# keys that `templates/base.typ`'s `project()` function (lines 39-49) actually
# declares as "element" parameters: `papersize: "a4"` (string), `fontsize:
# 11pt` (length/raw), and `lang: "en"` (string -- CONF-07, the Typst
# typesetting-language parameter). Keep this list EXACTLY in sync with that
# signature -- adding a key here WITHOUT a matching `base.typ` parameter
# would pass an undeclared kwarg and abort the Typst compile. Hand-maintained
# by design (D-03): a `.typ` function signature can't be reliably
# introspected from Python, and most `project()` params (title/authors/date/
# toctree_*) already arrive via `parameter_mapping`/`extract_toctree_options`
# -- adding them here would create a second, colliding source of truth.
ELEMENTS_ALLOWLIST: Dict[str, str] = {
    "papersize": _ElementsEmissionKind.STRING,
    "fontsize": _ElementsEmissionKind.RAW,
    "lang": _ElementsEmissionKind.STRING,
}


def derive_typst_lang(sphinx_language: str | None) -> str | None:
    """Convert a Sphinx ``language`` config value into a Typst ``lang`` code.

    CONF-07/D-02: the conversion is a single generic rule, not a
    hand-maintained per-language mapping table -- take the substring before
    the first ``_``/``-``/``@`` separator and lowercase it. This covers every
    measured case (``"ja"`` -> ``"ja"``, ``"zh_CN"`` -> ``"zh"``,
    ``"pt-BR"`` -> ``"pt"``, ``"sr@latin"`` -> ``"sr"``, ``"en"`` -> ``"en"``,
    ``"JA"`` -> ``"ja"``) without needing to hand-maintain a table of Sphinx's
    ~70 supported languages, and survives new locales being added upstream.

    D-03: the converted head is accepted ONLY when it is 2-3 ASCII letters
    (``re.fullmatch(r"[a-z]{2,3}", head)`` -- deliberately NOT
    ``len(head) in (2, 3) and head.isalpha()``, because Python's
    ``str.isalpha()`` is Unicode-aware and answers True for CJK/Cyrillic code
    points; a ``language = "日本語"`` project would then forward a
    three-code-point value that Typst rejects with a hard
    ``TypstError: expected two or three letter language code``, exactly the
    abort SC#4 exists to prevent). Any rejection -- non-str/None input, an
    empty string, wrong length, or non-ASCII-alpha content -- logs a
    ``logger.warning`` naming the offending value via ``repr()`` and returns
    ``None``. Returning ``None`` (never raising, and never substituting a
    literal ``"en"`` fallback) is what lets ``base.typ``'s own ``lang: "en"``
    parameter default apply -- a hardcoded Python-side fallback would create
    a second source of truth that silently diverges the day that default
    changes.

    An unknown-but-well-formed 2-3-letter code (e.g. ``"xyz"``) is NOT
    rejected and does NOT warn: Typst itself falls back to English for a
    code it does not recognize, without aborting the compile, so this is not
    a value this helper needs to second-guess (D-03).

    This helper is applied ONLY to the auto-derived value computed from
    Sphinx's ``language`` config. It must never be applied to a user's
    explicit ``typst_elements["lang"]`` value -- that value is a Typst
    literal the user wrote directly for this builder-specific setting and
    passes through unvalidated, exactly like every other ``typst_elements``
    key (D-04, Phase 26 D-09 precedent).

    Args:
        sphinx_language: The Sphinx ``config.language`` value (normally a
            non-``None`` ``str``; defensively accepts ``None`` too).

    Returns:
        A lowercase 2-3-letter ASCII Typst ``lang`` code, or ``None`` if no
        such code could be derived.
    """
    if not isinstance(sphinx_language, str) or not sphinx_language:
        logger.warning(
            f"typsphinx: could not derive a Typst 'lang' from Sphinx "
            f"'language' = {sphinx_language!r} -- omitting 'lang' (falling "
            f"back to the template's own default)."
        )
        return None

    head = re.split(r"[_\-@]", sphinx_language, maxsplit=1)[0].lower()

    if re.fullmatch(r"[a-z]{2,3}", head):
        return head

    logger.warning(
        f"typsphinx: could not derive a Typst 'lang' from Sphinx "
        f"'language' = {sphinx_language!r} -- omitting 'lang' (falling "
        f"back to the template's own default)."
    )
    return None


def resolve_package_for_engine(
    typst_package: str | None, raw_template_path: str | None
) -> str | None:
    """
    Decide which ``typst_package`` value a TemplateEngine should be built with.

    D-01/D-03 routing rule: ``typst_template`` is the primary route. Whenever a
    custom template is configured it wins outright and the package import is
    suppressed entirely -- even if ``typst_package`` is ALSO set. Only when no
    custom template is configured does the package route apply.

    This is the SINGLE place that decision is made. ``writer.py`` (per-document
    rendering) and ``builder.py`` (the once-per-build shared template file) must
    not re-derive it independently: writer/builder disagreeing about
    package-vs-template routing is precisely the shape of BUG-A, the fatal
    defect phase 22.2 existed to fix (WR-04).

    Args:
        typst_package: The configured ``typst_package`` value, if any
        raw_template_path: The configured ``typst_template`` value, if any

    Returns:
        ``typst_package`` when the package route applies, otherwise ``None``
    """
    return None if raw_template_path else typst_package


class TemplateEngine:
    """
    Manages Typst templates for document generation.

    Responsibilities:
    - Load default or custom Typst templates
    - Search templates in multiple directories with priority
    - Provide fallback to default template when custom template not found
    - Map Sphinx metadata to template parameters
    - Render final Typst document with template and content

    Requirement 8.1: Default Typst template included in package
    Requirement 8.2: Support custom template specification
    Requirement 8.7: Priority search in user project directory
    Requirement 8.9: Fallback to default template with warning
    """

    # Standard mapping from Sphinx metadata to template parameters
    # Requirement 8.3: Sphinx metadata passed to template
    # Requirement 8.5: Standard metadata name transformation
    DEFAULT_PARAMETER_MAPPING = {
        "project": "title",
        "author": "authors",
        "release": "date",
    }

    def __init__(
        self,
        template_path: str | None = None,
        template_name: str | None = None,
        search_paths: List[str] | None = None,
        parameter_mapping: Dict[str, str] | None = None,
        typst_package: str | None = None,
        typst_template_function: Any | None = None,
        typst_package_imports: List[str] | None = None,
        typst_authors: Dict[str, Dict[str, Any]] | None = None,
    ):
        """
        Initialize TemplateEngine.

        Args:
            template_path: Absolute path to template file (highest priority)
            template_name: Template filename to search in search_paths
            search_paths: List of directories to search for templates (priority order)
            parameter_mapping: Custom mapping from Sphinx metadata to template parameters
                             (Requirement 8.4: different parameter names)
            typst_package: Typst Universe package specification (e.g., "@preview/charged-ieee:0.1.0")
                          (Requirement 8.6: external template packages)
            typst_template_function: Template function name (str) or dict with {"name": str, "params": dict}
            typst_package_imports: Specific items to import from package
            typst_authors: Author details as dict with author name as key (recommended)
        """
        self.template_path = template_path
        self.template_name = template_name or "base.typ"
        self.search_paths = search_paths or []
        self.typst_package = typst_package
        if parameter_mapping is not None:
            self.parameter_mapping = parameter_mapping
        elif self.typst_package:
            # D-05: on the package-only path, only pass what the user explicitly
            # mapped -- a Typst function signature cannot be introspected from
            # Python, so "pass nothing by default" is the only sound rule.
            self.parameter_mapping = {}
        else:
            self.parameter_mapping = self.DEFAULT_PARAMETER_MAPPING.copy()
        self.typst_package_imports = typst_package_imports or []
        self.typst_authors = typst_authors or {}

        # Parse typst_template_function: support both string and dict formats
        if isinstance(typst_template_function, dict):
            self.typst_template_function_name = typst_template_function.get(
                "name", "project"
            )
            self.typst_template_params = typst_template_function.get("params", {})
        elif isinstance(typst_template_function, str):
            self.typst_template_function_name = typst_template_function
            self.typst_template_params = {}
        else:
            self.typst_template_function_name = None
            self.typst_template_params = {}

    def get_default_template_path(self) -> str:
        """
        Get the path to the default template bundled with the package.

        Returns:
            Absolute path to default template file
        """
        # Template is located in sphinxcontrib/typst/templates/base.typ
        package_dir = Path(__file__).parent
        template_dir = package_dir / "templates"
        default_template = template_dir / "base.typ"

        return str(default_template)

    def resolve_template(self) -> TemplateResolution:
        """
        Resolve Typst template with priority order:

        1. Explicit template_path if provided
        2. Search for template_name in search_paths (first match wins) --
           this is also where a ``<srcdir>/base.typ`` shadow of the bundled
           default template is discovered (CONF-07/D-06).
        3. Default template bundled with package

        This is the SINGLE priority walk both ``load_template()`` (below,
        which now delegates here) and ``uses_bundled_default_template()``
        rely on -- CONF-07/D-06 explicitly rejects a second, independently
        hand-written existence check duplicating this same logic elsewhere,
        because such a duplicate would drift the moment ``search_paths``/
        ``template_name`` semantics change.

        Returns:
            A ``TemplateResolution`` recording both the loaded content and
            WHICH priority actually supplied it (``"explicit"``,
            ``"search"``, or ``"default"``).

        Requirement 8.1: Load default template
        Requirement 8.2: Load custom template
        Requirement 8.7: Search in user project directory
        Requirement 8.9: Fallback to default with warning
        """
        # Priority 1: Explicit template path
        if self.template_path:
            template_content = self._try_load_file(self.template_path)
            if template_content is not None:
                return TemplateResolution(template_content, "explicit")
            logger.warning(
                f"Custom template not found: {self.template_path}. "
                f"Falling back to default template."
            )

        # Priority 2: Search in search_paths
        if self.search_paths:
            for search_dir in self.search_paths:
                candidate_path = Path(search_dir) / self.template_name
                template_content = self._try_load_file(str(candidate_path))
                if template_content is not None:
                    logger.debug(f"Loaded template from: {candidate_path}")
                    return TemplateResolution(template_content, "search")

        # Priority 3: Default template
        default_path = self.get_default_template_path()
        template_content = self._try_load_file(default_path)
        if template_content is None:
            # This should never happen if package is properly installed
            raise FileNotFoundError(
                f"Default template not found at: {default_path}. "
                f"Package installation may be corrupted."
            )

        return TemplateResolution(template_content, "default")

    def load_template(self) -> str:
        """
        Load Typst template content.

        UNCHANGED public contract: still returns just the content ``str``,
        for every existing caller (``get_template_content()``,
        ``render()``, and every pre-existing test in
        ``tests/test_template_engine.py``). Delegates the actual priority
        walk to ``resolve_template()``.

        Returns:
            Template content as string
        """
        return self.resolve_template().content

    def uses_bundled_default_template(self) -> bool:
        """
        CONF-07/D-06: the single judgment point for "is the default
        (bundled) template actually going to be used for this build?".

        Returns True only when this engine carries no ``typst_package`` AND
        ``resolve_template().source == "default"``.

        Why judged from an actual resolution result rather than a
        declaration check (``typst_template is None and typst_package is
        None``): a ``<srcdir>/base.typ`` shadow leaves BOTH
        ``typst_template`` and ``typst_package`` unset while still routing
        the build onto a user-authored template (Priority 2's search-path
        hit). A declaration-based check would miss this shadow entirely,
        inject a parameter (``lang``) that shadow template never declared,
        and manufacture the exact undeclared-kwarg Typst compile fatal
        (``unexpected argument: lang``) this predicate exists to prevent
        (SC#3).

        Why the ``typst_package`` guard is load-bearing and NOT redundant
        with the priority walk: on the package-alone path, this engine is
        constructed with ``template_path=None``, so its OWN priority walk
        legitimately resolves to ``"default"`` even though ``render()``
        never loads that template at all -- the emitted ``#show`` rule
        calls the package's own entry function instead. Passing a
        bundled-template-only parameter (``lang``) into a package function
        that never declared it would be the exact same undeclared-kwarg
        fatal, just reached via a different route.

        Returns:
            ``True`` only for a package-free engine whose priority walk
            resolves to the bundled default template; ``False`` for
            ``"explicit"``, ``False`` for ``"search"`` (including the
            ``<srcdir>/base.typ`` shadow case), and ``False`` whenever
            ``typst_package`` is configured.
        """
        if self.typst_package:
            return False
        return self.resolve_template().source == "default"

    def map_parameters(
        self,
        sphinx_metadata: Dict[str, Any],
        typst_elements: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Map Sphinx metadata to template parameters.

        Args:
            sphinx_metadata: Dictionary of Sphinx configuration metadata
                           (project, author, release, etc.)
            typst_elements: CONF-04 curated pass-through values (e.g.
                           ``papersize``/``fontsize``), kept structurally
                           separate from ``sphinx_metadata`` so baseline
                           Sphinx metadata (e.g. ``copyright``) can never
                           reach ``project()`` (D-05/D-08). Defaults to
                           ``None`` (treated as empty) so every existing
                           one-positional-argument call site is unaffected
                           (Pitfall 4).

        Returns:
            Dictionary of template parameters ready to pass to template

        Requirement 8.3: Pass Sphinx metadata to template
        Requirement 8.4: Support different parameter names
        Requirement 8.5: Standard metadata name transformation
        Requirement 8.8: Convert to arrays and complex structures

        Raises:
            sphinx.errors.ExtensionError: if ``typst_elements`` contains a
                key not present in ``ELEMENTS_ALLOWLIST`` (D-06/D-07).
        """
        params = {}

        # Apply mapping
        for sphinx_key, template_key in self.parameter_mapping.items():
            if sphinx_key in sphinx_metadata:
                value = sphinx_metadata[sphinx_key]

                # Special handling for authors (both standard "authors" and custom names)
                if sphinx_key == "author" or template_key in ("authors", "doc_authors"):
                    value = self._convert_to_authors_tuple(value)

                params[template_key] = value

        # D-05, gate 2: on the package path, do not back-fill title/authors/date
        # -- a package function's signature is whatever the user explicitly
        # mapped, and injecting these defaults would pass unexpected arguments
        # to a package function that never asked for them.
        if not self.typst_package:
            # Provide default values for missing required parameters
            if "title" not in params:
                params["title"] = ""
            if "authors" not in params:
                params["authors"] = ()
            if "date" not in params:
                params["date"] = None

        # D-07: typst_authors (explicit config) overrides whatever "authors"
        # already resolved to -- a native Python list[dict] that
        # _format_typst_value()'s existing list/dict recursion serializes as
        # a Typst array of dictionaries. Must stay a native Python structure;
        # never pre-render it to Typst source here, or it re-enters
        # _format_typst_value()'s string branch and comes out as a quoted
        # string literal instead of an array (the double-formatting trap).
        # Applies on both the package path and the template path -- runs
        # after the package-aware back-fill guard above, so on the package
        # path "authors" is present only when the user actually configured
        # typst_authors.
        if self.typst_authors:
            params["authors"] = [
                {"name": name, **details}
                for name, details in self.typst_authors.items()
            ]

        # CONF-04: additive elements merge -- runs LAST, after the
        # typst_authors override above, without disturbing the
        # `if not self.typst_package` back-fill guard or the typst_authors
        # override itself. Validate each key against ELEMENTS_ALLOWLIST
        # BEFORE it is ever added to params (D-06/D-07, Pitfall 2): an
        # unrecognized key raises loudly here instead of being silently
        # dropped (today's bug) or passed through as an undeclared kwarg
        # that would abort the Typst compile with a far less actionable
        # error.
        for key, value in (typst_elements or {}).items():
            if key not in ELEMENTS_ALLOWLIST:
                supported = ", ".join(sorted(ELEMENTS_ALLOWLIST))
                raise ExtensionError(
                    f"typst_elements: unknown key {key!r} -- "
                    f"supported keys: {supported}"
                )
            emit_kind = ELEMENTS_ALLOWLIST[key]
            params[key] = (
                RawTypst(value) if emit_kind == _ElementsEmissionKind.RAW else value
            )

        return params

    def generate_package_import(self) -> str:
        """
        Generate Typst package import statement.

        Returns:
            Import statement string, or empty string if no package specified

        Requirement 8.6: Typst Universe external template packages
        """
        if not self.typst_package:
            return ""

        # Generate import statement
        if self.typst_package_imports:
            # Import specific items: #import "@package:version": item1, item2
            items = ", ".join(self.typst_package_imports)
            return f'#import "{self.typst_package}": {items}'
        elif self.typst_template_function_name:
            # Import template function: #import "@package:version": template_func
            return (
                f'#import "{self.typst_package}": {self.typst_template_function_name}'
            )
        else:
            # Import entire module: #import "@package:version"
            return f'#import "{self.typst_package}"'

    def extract_toctree_options(self, doctree: Any) -> Dict[str, Any]:
        """
        Extract toctree options from doctree for template parameters.

        Args:
            doctree: Docutils document tree

        Returns:
            Dictionary of toctree options for template

        Requirement 8.12: toctree options passed as template parameters
        Requirement 8.13: template reflects toctree options in #outline()
        Requirement 13.8: #outline() managed at template level
        Requirement 13.9: toctree options mapped to template parameters
        """
        from sphinx import addnodes

        # Try to find toctree node in doctree
        toctree_nodes = list(doctree.findall(addnodes.toctree))

        if not toctree_nodes:
            # No toctree found - return empty dict
            return {}

        # Use first toctree node found
        toctree = toctree_nodes[0]

        # Extract options with defaults
        # Note: Sphinx toctree numbered can be False, True, or int
        # Convert to bool for Typst (0 means False, positive means True)
        numbered_value = toctree.get("numbered", False)
        if isinstance(numbered_value, int):
            numbered_value = numbered_value > 0

        # Note: Sphinx toctree maxdepth can be -1 (unlimited)
        # Typst outline() requires positive depth or none
        # Convert -1 to none for unlimited depth
        maxdepth_value = toctree.get("maxdepth", 2)
        if maxdepth_value == -1:
            maxdepth_value = None

        return {
            "toctree_maxdepth": maxdepth_value,
            "toctree_numbered": numbered_value,
            "toctree_caption": toctree.get("caption", ""),
        }

    def get_template_content(self) -> str:
        """
        Get the template content for writing to a separate file.

        Returns:
            Template content as string

        This is used when templates are written as separate files
        instead of being inlined in the main document.
        """
        template = self.load_template()
        return template

    def render(
        self, params: Dict[str, Any], body: str, template_file: str = None
    ) -> str:
        """
        Render final Typst document with template and body.

        Args:
            params: Template parameters (title, authors, etc.)
            body: Document body content (Typst markup)
            template_file: Path to template file for import (relative to output dir).
                          If None, template is inlined (old behavior).
                          If specified, template is imported from file.

        Returns:
            Complete Typst document string

        Requirement 8.2: Use custom template
        Requirement 8.10: Pass document settings to template
        Requirement 8.14: #outline() in template, not body
        """
        # Build output parts
        output_parts = []

        # Add package import if using Typst Universe package
        package_import = self.generate_package_import()
        if package_import:
            output_parts.append(package_import)
            output_parts.append("")  # Blank line

        # D-02: hoisted out of `if template_file:` so every master gets these
        # essential imports -- closes BUG-F, where a package-only master (no
        # template_file) previously got none of them.
        #
        # Exception: the inline-default-template path below appends the whole
        # of `templates/base.typ`, which already carries these same imports and
        # show-rules. Emitting the hoisted block there too would duplicate every
        # line (CR-01). So hoist for the two paths that do NOT inline the full
        # template, keeping exactly one emission site in every case.
        will_inline_default_template = not template_file and not self.typst_package
        if not will_inline_default_template:
            output_parts.append("// Essential package imports")
            output_parts.append('#import "@preview/codly:1.3.0": *')
            output_parts.append('#import "@preview/codly-languages:0.1.10": *')
            output_parts.append('#import "@preview/mitex:0.2.7": mi, mitex')
            output_parts.append('#import "@preview/gentle-clues:1.3.1": *')
            output_parts.append("")  # Blank line
            output_parts.append("#show: codly-init.with()")
            output_parts.append("#codly(languages: codly-languages)")
            output_parts.append("")  # Blank line

        if template_file:
            # Import template from separate file
            template_func = self.typst_template_function_name or "project"
            output_parts.append(f'#import "{template_file}": {template_func}')
            output_parts.append("")  # Blank line
        else:
            # Load template inline (old behavior)
            # For external packages, we skip loading the template
            if not self.typst_package:
                template = self.load_template()
                output_parts.append(template)
                output_parts.append("")  # Blank line

        # Generate #show statement with template function call
        template_func = self.typst_template_function_name or "project"
        output_parts.append(f"#show: {template_func}.with(")

        # Merge template-specific params with standard params.
        # D-08: auto-derived Sphinx metadata is the fallback; explicit
        # typst_template_function["params"] configuration is authoritative
        # and wins on a key collision. Applies on both the template path and
        # the package path.
        all_params = {}
        all_params.update(params)  # Auto-derived params first (fallback)
        all_params.update(self.typst_template_params)  # Explicit config wins

        # Format parameters
        for key, value in all_params.items():
            formatted_value = self._format_typst_value(value)
            output_parts.append(f"  {key}: {formatted_value},")

        output_parts.append(")")
        output_parts.append("")  # Blank line

        # Add body content
        output_parts.append(body)

        return "\n".join(output_parts)

    def _format_typst_value(self, value: Any) -> str:
        """
        Format Python value as Typst value.

        Args:
            value: Python value (str, int, bool, tuple, etc.)

        Returns:
            Typst-formatted value string
        """
        if value is None:
            return "none"
        elif isinstance(value, RawTypst):
            # CONF-04/D-02: emitted verbatim, no quoting/escaping -- checked
            # BEFORE the str branch so a RawTypst never re-enters string
            # quoting (the double-formatting trap, Pitfall 1).
            return value.source
        elif isinstance(value, bool):
            # Typst uses lowercase true/false
            return "true" if value else "false"
        elif isinstance(value, str):
            # Escape quotes and backslashes
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, (list, tuple)):
            # Format as Typst array/tuple
            formatted_items = [self._format_typst_value(item) for item in value]
            return f'({", ".join(formatted_items)},)' if formatted_items else "()"
        elif isinstance(value, dict):
            # Format as Typst dictionary (not commonly used in templates)
            items = [f"{k}: {self._format_typst_value(v)}" for k, v in value.items()]
            return f'({", ".join(items)})'
        else:
            # Default: convert to string and quote
            return f'"{str(value)}"'

    def _convert_to_authors_tuple(self, author_value: Any) -> tuple:
        """
        Convert author metadata to tuple of authors.

        Args:
            author_value: Author metadata (string or list)

        Returns:
            Tuple of author names

        Requirement 8.8: Convert to arrays and complex structures
        """
        if isinstance(author_value, (list, tuple)):
            return tuple(author_value)
        elif isinstance(author_value, str):
            # Split comma-separated authors
            authors = [a.strip() for a in author_value.split(",")]
            return tuple(authors)
        else:
            return (str(author_value),)

    def _try_load_file(self, file_path: str) -> str | None:
        """
        Try to load content from file.

        Args:
            file_path: Path to file

        Returns:
            File content as string, or None if file doesn't exist or can't be read
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except (FileNotFoundError, OSError):
            return None
