"""Template registry resolution for Sphinx Typst builds (Phase 53).

Resolves the ``typst_document_templates`` config dict into a mapping of
registry key -> ``TemplateRegistryEntry``, plus the synthesized built-in
``"typst"`` key that carries the existing global ``typst_template`` /
``typst_package`` / ``typst_template_function`` values verbatim -- this is
what makes an untouched ``conf.py`` produce byte-identical output (TPL-03).

Why registry-key shape validation does NOT reuse ``_escapes_outdir()`` /
``_is_drive_qualified()`` (``typsphinx/builder.py:36-112``): those two
functions answer "is this a legal, possibly multi-segment, OUTPUT path" --
their own docstring examples show ``_escapes_outdir("manuals/guide")`` is
``False`` BY DESIGN, because a path-separator-bearing value is a legitimate
*output path* component under that contract. A registry key is the opposite
question: "is this value legal as a SINGLE path segment" -- a value
containing ``/`` or ``\\`` must always be rejected for a registry key,
which is the exact shape those two functions intentionally accept. Reusing
them here would silently accept `/`-bearing registry keys the moment
Phase 54 turns a key into a directory name. This is ROADMAP SC#4's written-
rationale requirement and PITFALLS.md Pitfall 1's anti-analog; registry-key
shape validation gets its own predicates (plan 53-03), never an extension
of those two.

This module adds zero new runtime dependencies -- only stdlib.
"""

from dataclasses import dataclass
from typing import Any, Dict

# Phase 53 (CONF-16/D-04): the ONLY reserved registry key, compared as a
# literal string. "Typst"/"TYPST" are ordinary user-defined keys (D-04) --
# the case-collision check (plan 53-03's CONF-18 case 7) compares
# REGISTERED keys against each other, and this synthesized built-in key is
# never a member of that set.
RESERVED_REGISTRY_KEY = "typst"


@dataclass(frozen=True)
class TemplateRegistryEntry:
    """One resolved ``typst_document_templates`` entry -- either declared
    by the user or synthesized for the reserved ``"typst"`` key. Carries
    exactly the fields ``render_wrapper()`` needs to build a
    ``TemplateEngine`` with no further lookup against ``config``.
    """

    key: str
    """The registry key this entry was resolved under -- ``"typst"`` for
    the synthesized built-in entry, or the user-declared key otherwise."""

    template: str | None
    """srcdir-relative path string, exactly as declared (or synthesized
    from global ``typst_template`` for the ``"typst"`` key). ``None``
    when the entry carries ``package`` instead, or when the definition
    declares neither."""

    package: str | None
    """Typst Universe package spec, exactly as declared (or synthesized
    from global ``typst_package`` for the ``"typst"`` key). ``None`` when
    the entry carries ``template`` instead, or when the definition
    declares neither."""

    template_function: Any | None
    """``str`` or ``{"name": str, "params": dict}``, passed straight to
    ``TemplateEngine.__init__``'s ``typst_template_function`` parameter
    unmodified -- that constructor already parses both shapes
    (``template_engine.py:251-264``). D-10: a user-defined key that omits
    this field gets ``None`` here, never an inherited copy of global
    ``typst_template_function``."""


def resolve_template_registry(
    config: Any, srcdir: str
) -> Dict[str, TemplateRegistryEntry]:
    """Resolve every declared ``typst_document_templates`` entry into a
    ``TemplateRegistryEntry``, plus the synthesized built-in ``"typst"``
    key.

    This task performs NO validation -- CONF-14..CONF-18's fail-loud
    checks are plan 53-03's expansion built on top of this proven slice.
    A user-defined key inherits nothing from global config (D-10); the
    synthesized ``"typst"`` key is the ONLY inheritance route (TPL-03).

    Called once per build, from ``write()``, between
    ``_validate_output_path_collisions()`` and ``prepare_writing()`` (D-03,
    D-09) -- and, lazily, from ``_write_typst_files()``'s own fallback for
    the direct-call write path several existing unit tests use.

    Args:
        config: The Sphinx ``Config`` object (or any object exposing the
            same ``typst_*`` attributes via ``getattr``).
        srcdir: The build's source directory. Unused by this task -- kept
            in the signature now so it does not churn between waves; plan
            53-03's CONF-17/D-08 checks need it.

    Returns:
        A mapping from registry key to its resolved ``TemplateRegistryEntry``,
        always containing at least the synthesized ``"typst"`` key.
    """
    del srcdir  # Unused in this task; kept for signature stability (D-08/CONF-17, 53-03).

    declared = getattr(config, "typst_document_templates", None) or {}

    registry: Dict[str, TemplateRegistryEntry] = {}
    for key, definition in declared.items():
        definition = definition or {}
        registry[key] = TemplateRegistryEntry(
            key=key,
            template=definition.get("template"),
            package=definition.get("package"),
            template_function=definition.get("template_function"),
        )

    # TPL-03: synthesize the built-in "typst" key from the SAME three
    # globals `_write_template_file()` (builder.py:1124-1132) already
    # reads, unmodified -- this is what makes an untouched conf.py produce
    # byte-identical output.
    registry[RESERVED_REGISTRY_KEY] = TemplateRegistryEntry(
        key=RESERVED_REGISTRY_KEY,
        template=getattr(config, "typst_template", None),
        package=getattr(config, "typst_package", None),
        template_function=getattr(config, "typst_template_function", None),
    )

    return registry


def resolve_registry_key(
    registry: Dict[str, TemplateRegistryEntry], entry: tuple
) -> TemplateRegistryEntry:
    """Resolve one ``typst_documents`` tuple's registry key (TPL-04) to
    its ``TemplateRegistryEntry``.

    Reads ``entry[4]`` when present (``len(entry) > 4``); an ABSENT fifth
    element means the built-in ``"typst"`` key (TPL-04) -- a four-element
    tuple and the same tuple with an explicit fifth element of the literal
    ``"typst"`` resolve to the identical object.

    This task's lookup assumes the key is already present in ``registry``
    -- the raise branches for an unregistered key (CONF-14) and for a
    present-but-non-``str`` element ``[4]`` (D-06) are plan 53-03's work.

    Args:
        registry: The resolved registry, as returned by
            ``resolve_template_registry()``.
        entry: A single ``typst_documents`` tuple.

    Returns:
        The ``TemplateRegistryEntry`` this entry's fifth element (or its
        absence) names.
    """
    key = entry[4] if len(entry) > 4 else RESERVED_REGISTRY_KEY
    return registry[key]
