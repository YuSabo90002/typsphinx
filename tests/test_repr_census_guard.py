"""
MSG-01/D-08/D-09: the AST-backed census guard that keeps the phase's
``repr()``/``!r`` pass-criterion enumeration honest at run time.

Milestone constraint 9 says that a plan in Phase 59 or 60 finding it must
edit a test is a signal the census was incomplete -- not a licence to edit.
This module is what makes that incompleteness *detectable* rather than
hypothetical: it re-derives the whole-tree set of ``repr()``/``!r``
occurrences that sit inside an ``assert`` statement's *test* expression
(i.e. decide GREEN/RED) and locks it to a recorded seven-site allowlist,
the exact set that remains after this phase rewrote the two path-valued
sites (D-08's census, ``58-REPR-CENSUS.md``).

The AST route is exact where a text search cannot be: a regular expression
cannot distinguish an assertion's test expression from its failure message,
its docstrings, or its comments -- and the failure-message f-strings in
this suite are precisely where the several-hundred *diagnostic-only*
``repr()``/``!r`` occurrences live. Walking ``ast.Assert(...).test`` only
(never ``.msg``) is the one mechanism that separates the two classes
exactly.
"""

import ast
import pathlib

import pytest

# D-09: the sweep root is derived from this module's own location, never
# from the process working directory, so the guard is invariant to where
# pytest is invoked from.
TESTS_ROOT = pathlib.Path(__file__).resolve().parent

# The seven non-path pass-criterion sites left after this phase's two
# rewrites (tests/test_out02_escape_target_gate.py and tests/test_builder.py
# both moved off repr()-format assertions in plans 58-01/58-02). Re-measured
# at plan time by running this module's own sweep helper against the live
# tree. Each entry is annotated with its D-08 value type on the trailing
# comment. Do NOT write a hardcoded total anywhere in this module -- the
# allowlist's own length (7) is the number.
PASS_CRITERION_REPR_ALLOWLIST: frozenset[tuple[str, int]] = frozenset(
    {
        ("test_registry_container_shape_gate.py", 142),  # list
        ("test_registry_prewrite_validation_gate.py", 278),  # identifier
        (
            "test_registry_prewrite_validation_gate.py",
            279,
        ),  # identifier (negative case)
        ("test_template_engine.py", 1317),  # identifier (language code)
        ("test_template_registry.py", 832),  # list
        ("test_template_registry.py", 847),  # bytes
        ("test_template_registry.py", 1001),  # other
    }
)

# The two modules this phase rewrote off a path-valued repr()/!r pass
# criterion. Used by the zero-path-valued assertion below -- a collected
# site whose file is a member of this set would mean the rewrite regressed.
REWRITTEN_PATH_VALUED_MODULES: frozenset[str] = frozenset(
    {
        "test_out02_escape_target_gate.py",
        "test_builder.py",
    }
)

# Non-vacuity floor for the sweep. Measured at plan time: 324 `.py` files
# exist under tests/ excluding __pycache__, so 100 has wide headroom for
# ordinary churn while still catching the failure mode it exists for -- a
# wrong sweep root or a broken glob returning nothing and letting the guard
# pass vacuously.
MINIMUM_FILES_SWEPT = 100


def _collect_pass_criterion_repr_sites() -> tuple[frozenset[tuple[str, int]], int]:
    """Sweep every ``tests/**/*.py`` file and return the set of
    ``repr()``/``!r`` occurrences that sit inside an ``assert`` statement's
    *test* expression, plus the number of files successfully parsed.

    Returns a ``(hit_set, files_parsed)`` tuple. ``hit_set`` entries are
    ``(relative_posix_path, lineno)`` pairs.
    """
    hits: set[tuple[str, int]] = set()
    files_parsed = 0

    for candidate in TESTS_ROOT.rglob("*.py"):
        if "__pycache__" in candidate.parts:
            continue
        # D-09: the guard's OWN file must be excluded from the sweep, by
        # resolved-path identity rather than a hardcoded filename string --
        # this module's own allowlist and docstring carry the very tokens
        # ("repr(", "!r") the sweep looks for in source form, and deriving
        # the exclusion from __file__ means renaming this module cannot
        # silently break the self-exclusion.
        if candidate.resolve() == pathlib.Path(__file__).resolve():
            continue

        # The explicit encoding is not optional: without it Python uses the
        # platform's locale encoding, and the windows-latest lane would
        # fail on any non-ASCII byte in any test file.
        source = candidate.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(candidate))
        except SyntaxError as exc:
            # An unparseable file under tests/ is itself a finding and must
            # never be silently skipped -- a silent skip is a hole in
            # exactly the enumeration this guard exists to keep honest.
            pytest.fail(
                f"Could not parse {candidate} as Python source during the "
                f"repr()/!r census sweep: {exc}"
            )
            continue  # pragma: no cover -- pytest.fail always raises
        files_parsed += 1

        for node in ast.walk(tree):
            if not isinstance(node, ast.Assert):
                continue
            # This is the single most important line in this module: walk
            # ONLY node.test, never node.msg. node.msg is where the
            # several-hundred diagnostic-only occurrences in failure-message
            # f-strings live, and including it would pollute the result
            # with constructs that cannot decide an assertion's verdict.
            for sub in ast.walk(node.test):
                is_repr_call = (
                    isinstance(sub, ast.Call)
                    and isinstance(sub.func, ast.Name)
                    and sub.func.id == "repr"
                )
                # FormattedValue.conversion integer encoding: 114 == ord("r")
                # is the `!r` conversion, 115 == `!s`, -1 == no conversion.
                # Per docs.python.org/3/library/ast.html.
                is_repr_conversion = (
                    isinstance(sub, ast.FormattedValue) and sub.conversion == 114
                )
                if is_repr_call or is_repr_conversion:
                    # as_posix() is mandatory: on Windows a raw relative
                    # path renders with backslashes and would never compare
                    # equal to the allowlist's forward-slash form.
                    rel_path = candidate.relative_to(TESTS_ROOT).as_posix()
                    hits.add((rel_path, sub.lineno))

    return frozenset(hits), files_parsed


def test_pass_criterion_repr_sites_match_recorded_allowlist():
    """The collected pass-criterion set must equal the recorded allowlist
    exactly. A new entry means a test grew a pass criterion coupled to a
    value's representation format and 58-REPR-CENSUS.md is now stale; a
    missing entry means a site moved or was removed and the census must be
    re-derived, not the allowlist quietly edited."""
    collected, _ = _collect_pass_criterion_repr_sites()

    found_but_not_allowlisted = collected - PASS_CRITERION_REPR_ALLOWLIST
    allowlisted_but_not_found = PASS_CRITERION_REPR_ALLOWLIST - collected

    assert collected == PASS_CRITERION_REPR_ALLOWLIST, (
        "The repr()/!r pass-criterion census has drifted from the recorded "
        "allowlist in 58-REPR-CENSUS.md.\n"
        f"Sites found but NOT allowlisted (new pass-criterion site -- "
        f"58-REPR-CENSUS.md is stale): {sorted(found_but_not_allowlisted)}\n"
        f"Allowlisted sites no longer found (a site moved or was removed -- "
        f"re-derive the census, do not quietly edit the allowlist): "
        f"{sorted(allowlisted_but_not_found)}"
    )


def test_no_path_valued_pass_criterion_site_remains():
    """SC#3's 'the path-valued count is zero', asserted as a property of
    the live sweep rather than merely inferred from the allowlist's
    contents."""
    collected, _ = _collect_pass_criterion_repr_sites()

    path_valued_survivors = {
        (rel_path, lineno)
        for rel_path, lineno in collected
        if rel_path in REWRITTEN_PATH_VALUED_MODULES
    }

    assert not path_valued_survivors, (
        f"Expected zero path-valued pass-criterion sites (both "
        f"{sorted(REWRITTEN_PATH_VALUED_MODULES)} were rewritten off "
        f"repr()-format assertions in this phase), found: "
        f"{sorted(path_valued_survivors)}"
    )


def test_sweep_is_not_vacuous():
    """A low files-parsed count means the sweep root or the glob is wrong,
    not that the suite shrank -- this guards against the guard passing
    vacuously by finding nothing."""
    _, files_parsed = _collect_pass_criterion_repr_sites()

    assert files_parsed >= MINIMUM_FILES_SWEPT, (
        f"Expected at least {MINIMUM_FILES_SWEPT} files parsed under "
        f"tests/, found only {files_parsed}. A count this low means the "
        f"sweep root or glob is broken, not that the test suite shrank -- "
        f"a broken sweep that finds nothing would make the allowlist "
        f"assertion above pass vacuously."
    )


def test_allowlist_entries_point_at_real_lines():
    """Every allowlist entry must name a file that exists under TESTS_ROOT
    and has at least that many lines. Catches an allowlist gone stale
    against a deleted or truncated file, which the equality assertion alone
    would report only as a confusing missing entry."""
    for rel_path, lineno in sorted(PASS_CRITERION_REPR_ALLOWLIST):
        candidate = TESTS_ROOT / rel_path
        assert candidate.is_file(), (
            f"Allowlist entry names a file that does not exist under "
            f"TESTS_ROOT: {rel_path} (line {lineno})"
        )
        line_count = len(candidate.read_text(encoding="utf-8").splitlines())
        assert line_count >= lineno, (
            f"Allowlist entry {rel_path}:{lineno} points past the end of "
            f"the file, which has only {line_count} lines -- the file was "
            f"likely truncated or the entry is stale."
        )
