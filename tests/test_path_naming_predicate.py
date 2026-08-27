"""
MSG-01: durable meta-tests for `tests/_path_naming.py`'s `path_named_in`
predicate (D-05(a)).

This is the durable half of the falsification contract Phase 58 requires:
it turns RED if a future edit weakens the predicate, independently of
whether any product message site still carries a path at all. The
one-time recorded REAL falsification against a live, temporarily-edited
`typsphinx/builder.py` (D-05(b)) lives in `58-DECOUPLING-EVIDENCE.md`
instead -- that half proves the tests are actually WIRED to a message
that carries the path; this half proves the predicate itself is sound.

Every hand-built Windows-shaped string below is a Python literal, never
derived from a real Windows path resolution and never gated on the
running platform, matching `TestWindowsPathEscapingRegressionGuard`'s
established
POSIX-runnable convention (`tests/test_templates_path_collision_gate.py`).
"""

import pathlib

import pytest
from _path_naming import path_named_in


def test_raw_value_present_is_named():
    """The raw value, unwrapped, is a substring of the message."""
    assert path_named_in("/tmp/escape.typ", "target: /tmp/escape.typ") is True


def test_repr_quoted_value_is_named():
    """`!r`'s actual rendering -- Python's builtin representation doubles
    every backslash for a drive-shaped value. Built in a separate
    statement above the assert: a representation call or `!r` conversion
    placed inside the assert's own test expression would register as a
    NEW pass-criterion site in the Phase-58 census and turn 58-03's guard
    RED."""
    value = "C:\\escape.typ"
    message = f"target: {value!r}"
    assert path_named_in(value, message) is True


def test_hardcoded_single_quoted_value_is_named():
    """57-11's interim quoting shape: the raw value wrapped in literal
    single quotes with no escaping -- strictly subsumed by the raw-value
    disjunct."""
    value = "C:\\escape.typ"
    message = "target: 'C:\\escape.typ'"
    assert path_named_in(value, message) is True


def test_delimiter_wrapped_value_is_named():
    """A stand-in for MSG-02's eventual delimiter-aware helper output --
    Phase 60 fixes the actual delimiter character; the raw disjunct holds
    regardless of which character it picks."""
    value = "C:\\escape.typ"
    message = "target: |C:\\escape.typ|"
    assert path_named_in(value, message) is True


def test_d03_fallback_trap_is_not_a_false_positive():
    """The single most important assertion in this module -- it is what
    makes the whole rewrite non-tautological.

    The value under test (the drive-shaped `"C:\\escape.typ"`) is
    entirely ABSENT from the message; only its same-basename sibling
    (`"escape.typ"`, `fallback`'s value for the drive shape) is quoted.
    This is the VERBATIM shape `typsphinx/builder.py:695-698` produces
    when the `target` field is removed but `fallback` survives -- the
    D-03 trap that a basename-only, component-only, or any-substring
    predicate would fail to detect, staying GREEN when the real target
    value has been fully removed from the message. A predicate that
    passes this test cannot be satisfied by a same-basename sibling
    alone; it requires the FULL value.
    """
    value = "C:\\escape.typ"
    message = "using 'escape.typ' instead"
    assert path_named_in(value, message) is False


@pytest.mark.parametrize(
    "value",
    [
        "../escape.typ",
        "/tmp/escape.typ",
        "\\\\escape.typ",
        "C:\\escape.typ",
    ],
    ids=["traversal", "absolute-posix", "absolute-windows-unc", "drive"],
)
def test_all_escape_shapes_absent_from_falsified_line_are_not_named(value):
    """The unit-level twin of Task 2's integration-level falsification:
    the falsified warning line has the path field removed and the
    fallback still quoted, for all four escape shapes this suite's
    integration gates exercise. This survives after Task 2's transient
    product edit is gone -- it never touches `typsphinx/`."""
    message = "WARNING: a path is not supported in a typst_documents target name: -- using 'escape' instead"
    assert path_named_in(value, message) is False


def test_pathlike_value_accepted():
    """`os.PathLike` values (e.g. `pathlib.PurePosixPath`) are accepted --
    `os.fspath()` normalizes them before the containment check."""
    value = pathlib.PurePosixPath("/tmp/escape.typ")
    message = f"target: {value}"
    assert path_named_in(value, message) is True


def test_empty_value_raises_value_error():
    """Pins the edge-probe `empty` resolution: an empty value would match
    every text vacuously, which is exactly the tautology SC#2 forbids. A
    later refactor cannot reintroduce a vacuous `True` without this test
    catching it."""
    with pytest.raises(ValueError):
        path_named_in("", "any text at all")


def test_non_str_fspath_result_raises_type_error():
    """A `bytes` path does not normalize to `str` via `os.fspath()` --
    refused with `TypeError` naming the received type, rather than
    reaching the containment operator and raising an opaque error at the
    call site."""
    with pytest.raises(TypeError):
        path_named_in(b"/tmp/escape.typ", "target: /tmp/escape.typ")
