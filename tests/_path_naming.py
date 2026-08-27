"""
MSG-01: format-agnostic predicate for asserting that a path value is NAMED
in a message, independent of the quoting convention the message site uses.

D-01: exactly two disjuncts, not four. A four-form enumeration (raw /
``repr()`` / ``'{value}'`` / ``"{value}"``) is redundant: if a delimiter
form (single quotes, double quotes, or a future delimiter-aware helper's
output) wraps ``value``, the raw ``value`` is already a substring of the
message -- the delimiter characters add nothing the raw check doesn't
already catch. The ONE rendering the raw check does NOT subsume is
``repr()``'s backslash-doubling form: ``repr()`` does not merely add
delimiters, it mutates the VALUE itself (each ``\\`` becomes ``\\\\``).
That is why exactly one extra disjunct is needed, and why this predicate
holds across all three quoting regimes this milestone passes through:
``!r`` today, 57-11's hardcoded ``'{value}'`` in between, and MSG-02's
delimiter-aware helper after Phase 60.

D-03: the predicate must take the FULL path value, never its basename --
a basename-only or any-substring match would stay green when the real
value is removed from a message but a same-basename sibling field (e.g.
``builder.py:697``'s ``fallback``) is still present. That tautology is
exactly what this predicate exists to refuse.

D-04: this module carries ZERO product-package imports -- it is a leaf
test-support module, mirroring MSG-02's leaf-module discipline on the
product side. It must not be added to ``tests/conftest.py`` (fixtures
only) or duplicated inline in the modules that consume it.
"""

import os


def path_named_in(value: str | os.PathLike, text: str) -> bool:
    """True if ``value`` is named in ``text``, regardless of whether the
    message quotes it with ``!r`` (repr()'s backslash-doubling form), a
    hardcoded ``'{value}'``, or a future delimiter-aware helper. D-01: two
    disjuncts, not four -- the delimiter forms are strictly subsumed by
    the raw-value check; only repr()'s doubled-backslash rendering is NOT
    subsumed, hence exactly one extra disjunct.

    Holds across the three quoting regimes this milestone passes through:
    Python's builtin ``!r`` conversion, 57-11's hardcoded ``'{value}'``,
    and MSG-02's eventual delimiter-aware helper (Phase 60).

    Raises ``TypeError`` if ``os.fspath(value)`` does not normalize to a
    ``str`` (e.g. a ``bytes`` path), and ``ValueError`` if the normalized
    value is empty -- an empty value would match every ``text`` vacuously,
    which is exactly the tautology this predicate exists to refuse.
    """
    value_str = os.fspath(value)
    if not isinstance(value_str, str):
        raise TypeError(
            f"path_named_in() requires a value that normalizes to str via "
            f"os.fspath(), got {type(value_str).__name__}"
        )
    if value_str == "":
        raise ValueError(
            "path_named_in() refuses an empty value -- an empty value "
            "would match every text vacuously, which is never a "
            "meaningful naming proof"
        )
    return value_str in text or repr(value_str) in text
