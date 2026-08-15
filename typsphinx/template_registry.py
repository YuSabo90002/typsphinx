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

from sphinx.errors import ExtensionError

# Phase 53 (CONF-16/D-04): the ONLY reserved registry key, compared as a
# literal string. "Typst"/"TYPST" are ordinary user-defined keys (D-04) --
# the case-collision check (plan 53-03's CONF-18 case 7) compares
# REGISTERED keys against each other, and this synthesized built-in key is
# never a member of that set.
RESERVED_REGISTRY_KEY = "typst"

# Phase 53 plan 03 (CONF-18/D-02, case 4): the canonical 22-name Windows
# reserved-device-name set, cited to
# learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file. `COM0`,
# `LPT0` and `CLOCK$` are DELIBERATELY absent -- Microsoft's own current
# documentation does not list them, and RESEARCH.md Q4 carries the single
# authoritative citation for that boundary. Do not add them "for safety";
# doing so would silently add an eighth denylist case, which D-02 forbids.
_WINDOWS_RESERVED_NAMES = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)

# CONF-18/SC#4: the seven -- and ONLY seven -- key-shape rejection reasons,
# in the fixed order `_validate_registry_key_shape()` checks them. Exposed
# as a module-level constant so the "exactly seven" property is assertable
# by an enumeration test, rather than merely reviewed by eye (T-53-03).
_KEY_SHAPE_REJECTION_CASES = (
    "empty_or_whitespace_only",
    "dot_or_dotdot",
    "contains_path_separator",
    "windows_reserved_device_name",
    "trailing_dot",
    "trailing_space",
    "case_collision",
)


def _is_windows_reserved_name(key: str) -> bool:
    """Whether ``key`` is a Windows reserved device name (CONF-18 case 4),
    compared case-insensitively against everything BEFORE the first ``.``
    -- ``"CON.txt"`` is reserved (the extension does not exempt it),
    ``"ICONIC"`` is not (no dot, and no match against the full string
    either).
    """
    stem = key.split(".", 1)[0]
    return stem.upper() in _WINDOWS_RESERVED_NAMES


def _has_case_collision(key: str, other_keys: "set[str]") -> bool:
    """Whether ``key`` differs from some OTHER key in ``other_keys`` only
    by case (CONF-18 case 7), folded through
    ``TypstBuilder._collision_key()`` -- ROADMAP SC#4 requires the SAME
    comparison CONF-18 uses for output-path collisions, not an equivalent
    one re-derived here. Imported locally (not at module scope) to avoid a
    circular import: ``builder.py`` imports this module at its own module
    scope, so importing ``typsphinx.builder`` back at THIS module's scope
    would deadlock the import graph. By the time this function is called
    at runtime, ``typsphinx.builder`` has always already finished
    importing this module, so the local import safely resolves against an
    already-fully-initialized ``sys.modules`` entry.
    """
    from typsphinx.builder import TypstBuilder

    folded = TypstBuilder._collision_key(key)
    return any(
        other != key and TypstBuilder._collision_key(other) == folded
        for other in other_keys
    )


def _validate_registry_key_shape(key: str, other_keys: "set[str]") -> str | None:
    """Return the case-specific rejection reason for ``key``'s SHAPE as a
    single path segment (CONF-18, D-01/D-02), or ``None`` if it passes all
    seven locked cases.

    Checked in the fixed order below, matching
    ``_KEY_SHAPE_REJECTION_CASES``'s order -- a key matching an earlier
    case is reported for that case only. No allowlist regex is used
    anywhere, not even as a trailing catch-all (D-01): every case is its
    own named predicate with its own message.
    """
    if not key.strip():
        return f"registry key {key!r} is empty or whitespace-only"
    if key in (".", ".."):
        return f"registry key {key!r} is '.' or '..', which is not a legal registry key"
    if "/" in key or "\\" in key:
        return (
            f"registry key {key!r} contains a path separator ('/' or "
            "'\\\\'), which is not legal in a single-segment registry key"
        )
    if _is_windows_reserved_name(key):
        return (
            f"registry key {key!r} is a Windows reserved device name "
            "(https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file)"
        )
    if key.endswith("."):
        return f"registry key {key!r} ends with a trailing dot"
    if key.endswith(" "):
        return f"registry key {key!r} ends with a trailing space"
    if _has_case_collision(key, other_keys):
        return (
            f"registry key {key!r} differs from another registered key " "only by case"
        )
    return None


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
    key -- after validating every declared key (D-05, order-independent
    per SC#3).

    Validation mirrors ``_validate_output_path_collisions()``'s
    accumulate-then-raise-once shape (D-03) through this module's OWN
    ``ExtensionError`` -- never appended into that method's ``failures``
    list, and never changing its ``"typst: N output path collision(s):"``
    message text. Keys are iterated via ``sorted()`` so the accumulated
    message is byte-identical across runs regardless of ``dict`` insertion
    order (D-03).

    Plan 53-03, Task 1 validates CONF-18's seven-case key-shape denylist
    and CONF-16's reserved key. CONF-15/CONF-17/D-08's definition-level
    checks (Task 2) accumulate into this SAME ``failures`` list, still
    raised once at the end.

    A user-defined key inherits nothing from global config (D-10); the
    synthesized ``"typst"`` key is the ONLY inheritance route (TPL-03).

    Called once per build, from ``write()``, between
    ``_validate_output_path_collisions()`` and ``prepare_writing()`` (D-03,
    D-09) -- and, lazily, from ``_write_typst_files()``'s own fallback for
    the direct-call write path several existing unit tests use.

    Args:
        config: The Sphinx ``Config`` object (or any object exposing the
            same ``typst_*`` attributes via ``getattr``).
        srcdir: The build's source directory. Unused by Task 1 -- kept in
            the signature so it does not churn between waves; Task 2's
            CONF-17/D-08 checks consume it.

    Returns:
        A mapping from registry key to its resolved ``TemplateRegistryEntry``,
        always containing at least the synthesized ``"typst"`` key.

    Raises:
        ExtensionError: When one or more declared keys fail CONF-18's
            key-shape denylist or CONF-16's reserved-key check (Task 1),
            or CONF-15/CONF-17/D-08's definition-level checks (Task 2).
    """
    declared = getattr(config, "typst_document_templates", None) or {}
    all_keys = {key for key in declared.keys() if isinstance(key, str)}

    failures: list[str] = []
    for key in sorted(declared.keys()):
        shape_reason = _validate_registry_key_shape(key, all_keys)
        if shape_reason is not None:
            failures.append(shape_reason)
        elif key == RESERVED_REGISTRY_KEY:
            failures.append(
                f"registry key {key!r} is reserved for the built-in "
                f"{RESERVED_REGISTRY_KEY!r} key and cannot be redeclared "
                "(CONF-16)"
            )

    if failures:
        summary = "; ".join(failures)
        raise ExtensionError(
            f"typst_document_templates: {len(failures)} invalid "
            f"definition(s): {summary}"
        )

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
