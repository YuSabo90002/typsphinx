"""
MSG-02: a delimiter-aware path-quoting helper, ``quote_path()``.

This is a LEAF module carrying ZERO ``typsphinx``-internal imports. Placement
here is FORCED, not stylistic: ``builder.py`` imports ``writer.py`` at module
scope, and ``template_registry.py`` avoids a cycle with ``builder.py`` only
via a lazy function-scoped import -- so placing this function in any of
those three existing modules would create an unconditional two-file import
cycle the moment either of the other two imported it back (ROADMAP
constraint 6). A brand-new leaf module is the only placement all three can
depend on without touching any existing edge in that graph.

This is the product-side counterpart of ``tests/_path_naming.py`` -- the
leaf test-support module Phase 58 wrote as this module's deliberate mirror.
D-04 is the ONE deliberate disagreement with that mirror: an empty value is
quoted (``''``), not refused (``path_named_in()`` raises ``ValueError`` on an
empty value, because an assertion predicate handed an empty needle would
match vacuously -- a formatter handed ``""`` must render something, and
``''`` is byte-identical to ``repr("")``).

D-01 (AMENDED 2026-08-29): the delimiter rule reproduces ``repr()``'s
exactly, minus the backslash doubling -- the value's own characters are
never touched except for the both-quotes branch's apostrophe escape, and
that escape inserts NO backslash. The branch doubles the apostrophe
(``'`` -> ``''``, SQL-style) rather than backslash-escaping it. This is
load-bearing, not stylistic: the original backslash escape violated D-01a
whenever the value itself placed a ``\\`` immediately before a ``'`` --
the inserted backslash concatenated with the pre-existing one and formed
a run of two, the exact shape this phase exists to eliminate (measured:
``C:\\'and"there`` carries zero adjacent-backslash runs, and the
backslash-escaping rule turned it into one run of two). D-01a: because
this function now inserts no backslash anywhere, its output can never
contain a longer backslash run than the value already did, so the
existing
``TestWindowsPathEscapingRegressionGuard._assert_no_doubled_separator``
guard stays green over this function's output UNCONDITIONALLY -- not
merely for the fixture shapes that happen to be tested. D-03: ``None`` renders as
the bare four-character string ``None`` (``writer.py``'s package-alone
build path really does hand this function a live ``None``); ``str`` and
``os.PathLike`` values are quoted; everything else raises ``TypeError``.
"""

import os


def quote_path(value: str | os.PathLike[str] | None) -> str:
    """Select a delimiter for ``value`` and return it quoted, mirroring
    ``repr()``'s own delimiter-selection rule (D-01) minus the backslash
    doubling that rule also applies.

    Contract (D-03): ``None`` renders as the bare string ``"None"``. A
    ``str`` or ``os.PathLike`` value is normalized via ``os.fspath()``
    BEFORE any quote-character inspection, so a ``pathlib.Path`` never
    leaks its ``PosixPath(...)``/``WindowsPath(...)`` class-name wrapper
    into the returned string. Anything else (``bytes``, ``list``, ``int``,
    ...) raises ``TypeError`` naming this function and the offending type --
    ``os.fspath()`` alone does NOT enforce this (measured:
    ``os.fspath(b"foo")`` returns ``b"foo"`` unchanged rather than
    raising), so an explicit ``isinstance`` check after the ``os.fspath()``
    call is load-bearing, not defensive redundancy.

    Delimiter rule (D-01), applied to the normalized string:
    - no apostrophe present -> wrap in apostrophes (``'...'``)
    - apostrophe present, no double quote -> wrap in double quotes
      (``"..."``) so an embedded apostrophe cannot close the delimiter
      early (57-REVIEW.md IN-01)
    - both quote characters present -> wrap in apostrophes, with each
      embedded apostrophe DOUBLED (``'`` -> ``''``, SQL-style) and NO
      backslash inserted anywhere -- a pre-existing backslash in the
      value is never doubled, never escaped, never touched, and the
      escape can never combine with one to form a run of two (D-01a, as
      amended 2026-08-29)

    D-04: an empty string is quoted as ``''`` and does NOT raise --
    deliberately unlike ``tests/_path_naming.py``'s ``path_named_in()``.

    This function selects a delimiter for a human-readable diagnostic. It
    is NOT a sanitizer: it must never be relied on to make a value safe for
    a shell, a Typst source string literal, or a filesystem operation.
    """
    if value is None:
        return "None"

    value_str = os.fspath(value)
    if not isinstance(value_str, str):
        raise TypeError(
            f"quote_path() requires a value that normalizes to str via "
            f"os.fspath(), got {type(value_str).__name__}"
        )

    if "'" not in value_str:
        return f"'{value_str}'"
    if '"' not in value_str:
        return f'"{value_str}"'
    escaped = value_str.replace("'", "''")
    return f"'{escaped}'"
