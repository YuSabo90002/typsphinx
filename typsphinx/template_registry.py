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

import os
from dataclasses import dataclass
from typing import Any, Dict

from sphinx.errors import ExtensionError

from typsphinx.pathfmt import quote_path

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


def _violates_conf17(template_abs_path: str, srcdir: str) -> bool:
    """CONF-17/D-07: whether ``template_abs_path``'s resolved parent
    directory IS ``srcdir`` itself, or is an ANCESTOR of ``srcdir`` --
    pure path arithmetic on the DECLARED value, taking no
    filesystem-existence branch (D-09's "these two checks are structurally
    independent" requirement).

    Framed by the harm this predicate exists to prevent, not by the
    literal roadmap wording: "copy the parent directory" (Phase 54's
    future bundle copy) must never mean "copy the source tree". A single
    ``os.path.commonpath`` comparison covers BOTH of D-07's rejected
    shapes -- ``parent == srcdir`` and ``parent`` a proper ancestor of
    ``srcdir`` -- without two separate comparisons. Siblings of ``srcdir``
    (reached via ``..``) and absolute paths outside ``srcdir`` stay legal:
    ``os.path.join(srcdir, "/abs/x.typ")`` returns ``"/abs/x.typ"``
    verbatim (measured stdlib behaviour -- a later absolute component
    discards every earlier one), so an absolute ``template`` naturally
    evaluates against its own parent, not ``srcdir``'s. A cross-drive
    absolute ``template`` (e.g. Windows ``D:\\tpl.typ`` against a
    ``C:\\...`` ``srcdir``) also stays LEGAL -- see the ``except
    ValueError`` below -- so a future tightening of this function must not
    silently withdraw that guarantee.
    """
    parent = os.path.normpath(os.path.dirname(os.path.abspath(template_abs_path)))
    norm_srcdir = os.path.normpath(os.path.abspath(srcdir))
    try:
        return os.path.commonpath([norm_srcdir, parent]) == parent
    except ValueError:
        # 53-REVIEW.md CR-02 / D-07: os.path.commonpath() raises
        # ValueError("Paths don't have the same drive") when handed two
        # absolute paths on different Windows drives. Two paths on
        # different drives can never share an ancestor, so a cross-drive
        # `parent` is definitionally NOT `srcdir` itself and not an
        # ancestor of `srcdir` -- `False` is the correct answer here, not
        # a silent permissive default. This mirrors builder.py's
        # `_track_image()`, which guards its own `path.relpath()` call the
        # same way for the identical Windows cross-drive hazard (D-07:
        # "Windows cross-drive relpath() crash").
        return False


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
        srcdir: The build's source directory, consumed by Task 2's
            CONF-17/D-08 checks to resolve a declared ``template`` value
            to an absolute path.

    Returns:
        A mapping from registry key to its resolved ``TemplateRegistryEntry``,
        always containing at least the synthesized ``"typst"`` key.

    Raises:
        ExtensionError: When one or more declared keys fail CONF-18's
            key-shape denylist or CONF-16's reserved-key check (Task 1),
            or CONF-15/CONF-17/D-08's definition-level checks (Task 2), or
            (53-07 Task 2, 53-REVIEW.md WR-02/WR-03) a declared key is not
            a ``str`` or a declared definition is a truthy non-``dict``.
            The iteration key below is total across mixed key types, so a
            heterogeneous registry produces this module's own accumulated
            error rather than ``sorted()``'s ``TypeError``. (53-08 Task 1,
            53-REVIEW.md WR-01) When ``typst_document_templates`` itself is
            a TRUTHY non-``dict`` value (e.g. a `list`, the plausible
            copy-paste-from-``typst_documents`` typo), this is raised
            IMMEDIATELY, before the accumulate loop even starts -- see the
            container-guard comment below for why this is a container-level
            failure and not one more entry in the accumulated
            ``N invalid definition(s)`` summary. (53-08 Task 2,
            53-REVIEW.md WR-02) When a declared definition's ``template``
            field is truthy but neither a ``str`` nor an ``os.PathLike``
            (e.g. a `list`), that failure joins the SAME accumulated
            ``failures`` list as every other definition-level check.
    """
    declared = getattr(config, "typst_document_templates", None) or {}

    # 53-08 Task 1 (53-REVIEW.md WR-01; 53-VERIFICATION.md Anti-Patterns
    # row 2): Sphinx's own `add_config_value("typst_document_templates",
    # {}, "html", [dict])` (typsphinx/__init__.py:63) declares `[dict]` as
    # the expected type, but that declaration only *warns* on a mismatch --
    # it never coerces or rejects -- so a wrong-typed value reaches this
    # module completely unchanged. This guard therefore enforces exactly
    # the type the extension already publishes as its own contract, no
    # more and no less.
    #
    # It raises IMMEDIATELY here, before the accumulate-then-raise-once
    # loop below even starts, rather than joining `failures` (contrast
    # with the `template`-field guard inside the loop, which DOES join
    # `failures` -- see that guard's comment for why the two are
    # deliberately asymmetric). The accumulate loop's own precondition is
    # that `declared` is safely iterable AS A MAPPING (`declared.keys()`,
    # `declared[key]`); when the container itself is the wrong shape,
    # there is nothing to iterate and accumulate over, so raising
    # up front is the only structurally sound option. The message
    # deliberately does NOT reuse the `"typst_document_templates: N
    # invalid definition(s): ..."` prefix below -- a malformed CONTAINER
    # is not one more DEFINITION, and counting it as one would misreport
    # what actually went wrong.
    #
    # Because the preceding `or {}` has already normalized every FALSY
    # value (`{}`, `[]`, `None`, `""`, `0`) to `{}`, this `isinstance`
    # check provably fires only for a TRUTHY non-`dict` value -- exactly
    # the crash surface `declared.keys()` below would otherwise hit, and
    # nothing more. No separate truthiness test is needed here.
    if not isinstance(declared, dict):
        raise ExtensionError(
            "typst_document_templates must be a dict mapping registry key to definition,"
            f" got {declared!r}"
        )

    all_keys = {key for key in declared.keys() if isinstance(key, str)}

    failures: list[str] = []
    # 53-07 Task 2 (53-REVIEW.md WR-02): a total ordering key across mixed
    # key types. Slot 0 partitions `str` keys before non-`str` keys; slot 1
    # then compares `str` to `str` within each partition, so `sorted()` can
    # never raise its own `TypeError` for a heterogeneous key set (e.g. an
    # `int` beside a `str`). Deliberately NOT `repr(k)` for both partitions:
    # `repr()` switches to double quotes for a string containing an
    # apostrophe, which would silently reorder such a key relative to
    # today's plain `sorted()` and break D-03's published byte-identical
    # ordering for any config that has one. The all-`str` ordering below is
    # therefore byte-for-byte unchanged from before this edit.
    for key in sorted(
        declared.keys(),
        key=lambda k: (not isinstance(k, str), k if isinstance(k, str) else repr(k)),
    ):
        # 53-07 Task 2 (53-REVIEW.md WR-02): a non-`str` key is a TYPE
        # GUARD on this loop, not an eighth entry in
        # `_KEY_SHAPE_REJECTION_CASES` -- 53-03-PLAN.md's prohibition
        # freezes that denylist at exactly seven locked cases, and
        # `_validate_registry_key_shape()` keeps its `str`-only contract
        # unchanged, simply never reached with a non-`str` key.
        if not isinstance(key, str):
            failures.append(f"registry key {key!r} is not a string")
            continue
        shape_reason = _validate_registry_key_shape(key, all_keys)
        if shape_reason is not None:
            failures.append(shape_reason)
            continue
        if key == RESERVED_REGISTRY_KEY:
            failures.append(
                f"registry key {key!r} is reserved for the built-in "
                f"{RESERVED_REGISTRY_KEY!r} key and cannot be redeclared "
                "(CONF-16)"
            )
            # No further definition-level checks for this key: it is
            # already rejected, and -- since this `continue` means the
            # loop never runs the D-08 existence check below for a
            # user-DECLARED "typst" key -- the SYNTHESIZED built-in
            # "typst" entry (added after this loop, from global
            # `typst_template`, never from `declared`) is structurally
            # never subject to D-08's existence check either. That is
            # exactly D-08's contract: the built-in key's not-found path
            # keeps reaching `resolve_template()`'s existing
            # warn-and-fall-back behaviour, unobstructed by this module.
            continue

        # 53-07 Task 2 (53-REVIEW.md WR-03): a truthy non-`dict` definition
        # is a guard, not a silent `.get()` crash. The falsy path (`None`,
        # `""`, `0`) is unchanged -- it still normalizes to `{}` and
        # resolves exactly as it does today.
        raw_definition = declared[key]
        if raw_definition and not isinstance(raw_definition, dict):
            failures.append(
                f"registry key {key!r}'s definition must be a dict, got "
                f"{raw_definition!r}"
            )
            continue
        definition = raw_definition or {}
        template = definition.get("template")
        package = definition.get("package")

        # CONF-15: a definition carrying BOTH `template` and `package` is
        # rejected. One carrying only `template`, only `package`, or
        # NEITHER (flagged assumption 3) is accepted.
        if template and package:
            failures.append(
                f"registry key {key!r}'s definition sets both 'template' "
                "and 'package', which is unsupported (CONF-15)"
            )

        # 53-08 Task 2 (53-REVIEW.md WR-02; 53-VERIFICATION.md
        # Anti-Patterns row 3): a truthy `template` that `os.path.join`
        # cannot consume (e.g. a `list`) is a guard joining the
        # accumulated `failures` list, not a silent crash into
        # `os.path.join`'s raw `TypeError`. Three properties are
        # load-bearing here:
        #
        # 1. This branch is an `elif` of `if template and package:` above,
        #    NOT a `continue` -- so CONF-15's both-set check still runs
        #    for the SAME definition, and a definition carrying both a
        #    bad-typed `template` and a `package` reports BOTH failures
        #    in the one accumulated raise (D-09).
        # 2. The guard is gated on TRUTHINESS, matching this module's
        #    established convention that a falsy field means "absent"
        #    (`raw_definition or {}` above, this same `if template:`
        #    gate today). This is what keeps `template: None` / `""` /
        #    `0` / `[]` resolving exactly as they do today, unchanged --
        #    the guard covers precisely the crash surface and no more.
        # 3. The accepted types are `str` AND `os.PathLike`, deliberately
        #    NOT `str` alone as `53-REVIEW.md` WR-02's suggested fix
        #    reads. Measured: `os.path.join()` with a `str` `srcdir`
        #    succeeds for both `str` and `os.PathLike` and raises
        #    `TypeError` for `bytes` and everything else, and
        #    `TemplateEngine.resolve_template()`'s Priority 1 consumes
        #    the value through `_try_load_file()` and `Path(...)`, both
        #    of which accept `os.PathLike` -- so a `pathlib.Path`
        #    `template` works end to end TODAY, and blanket-rejecting it
        #    would withdraw a working shape rather than close a crash.
        #
        # MSG-05/SC#3: this branch's `template` interpolation below is a
        # DELIBERATE exclusion from MSG-05's path-quoting-helper rollout,
        # not an oversight. It is reached precisely when `template` is
        # neither `str` nor `os.PathLike` (a `list`, `bytes`, an `int`),
        # so the path-quoting helper would raise `TypeError` on the exact
        # values this branch exists to report. SC#3 measures this message
        # staying on Python's own repr conversion.
        if template and not isinstance(template, (str, os.PathLike)):
            failures.append(
                f"registry key {key!r}'s template {template!r} must be a path string or os.PathLike, "
                f"not a {type(template).__name__}"
            )
        elif template:
            # CONF-17 (D-07/D-09) and D-08's existence check are two
            # structurally INDEPENDENT checks on the declared `template`
            # value -- neither is an elif of the other -- so a value that
            # is both CONF-17-violating AND names a nonexistent file
            # reports BOTH failures in the same accumulated raise (D-09).
            template_abs_path = os.path.join(srcdir, template)
            if _violates_conf17(template_abs_path, srcdir):
                # MSG-05/D-06: `template` is PATH-valued here -- the
                # `isinstance(template, (str, os.PathLike))` guard above
                # (the `if` this `elif` follows) already establishes that
                # fact, so the path-quoting helper can never raise
                # `TypeError` at this call site. `key` stays `!r` -- it is
                # identifier-valued (D-07) and CONF-18 already forbids a
                # path separator in it, so it is never a filesystem
                # location.
                failures.append(
                    f"registry key {key!r}'s template {quote_path(template)} "
                    "resolves to a parent directory that is srcdir "
                    "itself, or an ancestor of srcdir (CONF-17)"
                )
            if not os.path.isfile(template_abs_path):
                # D-08: a BARE filesystem existence check, never routed
                # through `TemplateEngine.resolve_template()` -- that
                # method's multi-priority walk always succeeds via
                # fallback and can therefore never itself signal
                # "not found" (PITFALLS.md's Phase-53-specific pitfall).
                # MSG-05/D-06: `template` is PATH-valued here too, for the
                # same reason as the CONF-17 branch above.
                failures.append(
                    f"registry key {key!r}'s template {quote_path(template)} "
                    "does not exist"
                )

    if failures:
        summary = "; ".join(failures)
        raise ExtensionError(
            f"typst_document_templates: {len(failures)} invalid "
            f"definition(s): {summary}"
        )

    # 53-07 Task 2: this loop needs no new guard. It runs only when
    # `failures` is empty, by which point the accumulate loop above has
    # already proven every key is a `str` and every definition is a `dict`
    # or falsy -- a second, independent guard here would be redundant
    # state that could drift from the first.
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
    # globals the write-time and finish-time template resolution paths
    # (writer.py's render_wrapper(), builder.py's
    # _copy_used_template_bundles()) already read, unmodified -- this is
    # what makes an untouched conf.py produce byte-identical output.
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

    Because ``resolve_template_registry()`` already validates every
    DECLARED key up front (D-05), this lookup can never discover a NEW
    validation failure against a key that is genuinely IN the registry --
    it stays a plain presence check with a raise, not a second validation
    pass. The lookup is exact ``str`` equality, never case-folded: a
    registry declaring ``"Paper"`` does not satisfy an entry naming
    ``"paper"`` (CONF-14 encoding edge, D-04).

    Args:
        registry: The resolved registry, as returned by
            ``resolve_template_registry()``.
        entry: A single ``typst_documents`` tuple.

    Returns:
        The ``TemplateRegistryEntry`` this entry's fifth element (or its
        absence) names.

    Raises:
        ExtensionError: When element ``[4]`` is present but not a ``str``
            (D-06 -- this is the SAME CONF-14 class of error as an
            unregistered key, naming the offending value; it does NOT
            join ``_is_usable_typst_documents_entry()``'s tolerate-and-
            skip contract and is never silently coerced to the built-in
            key), or when it is a ``str`` absent from ``registry``
            (CONF-14 -- the message names the registered keys, sorted).
    """
    if len(entry) > 4:
        raw_key = entry[4]
        if not isinstance(raw_key, str):
            raise ExtensionError(
                f"typst_documents entry names registry key {raw_key!r}, "
                "which is not a string -- registered "
                f"typst_document_templates keys: {sorted(registry.keys())!r}"
            )
        key = raw_key
    else:
        key = RESERVED_REGISTRY_KEY

    if key not in registry:
        raise ExtensionError(
            f"typst_documents entry names registry key {key!r}, which is "
            "not a registered typst_document_templates key -- registered "
            f"keys: {sorted(registry.keys())!r}"
        )

    return registry[key]
