"""
WR-01/CR-01/D-03 (Phase 54.1 plan 05): real-``sphinx-build`` subprocess
gate proving the CR-01 ordering edge -- when one build carries pre-write
failures of MORE THAN ONE kind, they are accumulated into a SINGLE
``ExtensionError`` in a documented, deterministic order, and this holds
across INVERTED declaration order, not merely across repeated runs of one
project. Plans ``54.1-01``, ``54.1-03`` and ``54.1-04`` each proved their
own failure kind in isolation (or, in ``54.1-04``'s case, multiple
instances of the SAME ``templates_path``-collision kind); this is the
only gate in this suite exercising TWO DIFFERENT failure kinds -- the
reserved-key case collision (D-07) and the hoisted A-01/CONF-17 check
(D-04/D-05/D-06) -- in one build.

**Documented append order** (read directly from
``TypstBuilder._validate_used_template_paths()`` in ``typsphinx/builder.py``,
so a later reordering is a visible, intentional change rather than a
silent one): the reserved-key case-collision check (kind 3) runs FIRST,
iterating every DECLARED registry key in ``sorted()`` order; only THEN
does the per-used-key loop run, iterating ``sorted(used_keys)``, where
each key contributes EITHER a CONF-17 failure OR a ``templates_path``
failure (never both -- a CONF-17 violation ``continue``s past the
``templates_path`` check for that same key). Both fixtures below carry
exactly two keys: the DECLARED registry key ``"Typst"`` (reserved-key
case collision -- kind 3) and the SYNTHESIZED built-in ``"typst"`` key,
configured via the global ``typst_template = "aardvark.typ"`` setting
(CONF-17/A-01 violation -- kind 2, the hoisted check). A DECLARED
registry key can never itself carry a CONF-17 violation this gate
reaches: ``resolve_template_registry()``'s own declared-key validation
loop (``template_registry.py:420``) already catches that case, raising
its OWN separate error BEFORE ``_validate_used_template_paths()`` ever
runs -- the hoisted check exists SPECIFICALLY because that declared-key
loop never reaches the SYNTHESIZED key (appended after the loop
returns), which is why this fixture's CONF-17 half must come from the
global setting. Since ``'T' < 't'`` in Unicode code-point order,
``sorted(used_keys)`` always yields ``["Typst", "typst"]`` regardless of
which fixture declares which config statement first -- so the aggregate
names ``"Typst"``'s failure before ``"typst"``'s in BOTH fixtures, and
this gate asserts that ordering is genuinely produced by the
implementation's ``sorted()`` iteration, not merely copied from
declaration order.

Neither fixture sets ``templates_path``, so the ``templates_path``
containment check contributes nothing and the aggregate carries EXACTLY
these two kinds -- a failure count of 2.

Pre-fix RED transcript recorded verbatim in
``.planning/phases/54.1-bundle-directory-safety-templates-path-collision-refusal-and/54.1-05-EVIDENCE.md``
(binding constraint #6), measured via the swap-and-restore procedure
against the same pre-fix SHA (``9cc529b794563e57f2f070f93f0be9f141f8740e``)
``54.1-01-RED-EVIDENCE.md`` and ``54.1-04-RED-EVIDENCE.md`` used.
"""

import re
import subprocess
import sys
from pathlib import Path

FIXTURE_DIR_A = Path(__file__).parent / "fixtures" / "mixed_prewrite_failures_a_gate"
FIXTURE_DIR_B = Path(__file__).parent / "fixtures" / "mixed_prewrite_failures_b_gate"

# Copied VALUES (not imported) from tests/test_conf17_prewrite_gate.py and
# tests/test_reserved_key_case_prewrite_gate.py -- this suite's convention
# is per-module copies of shared marker constants, never cross-module
# imports between test modules.
CONF17_PREWRITE_MARKER = (
    "has a parent directory that is srcdir itself, or an ancestor of srcdir"
)
RESERVED_KEY_CASE_MARKER = "differs from the built-in 'typst' registry key only by case"

# Copied VALUE from tests/test_templates_path_collision_gate.py: the
# aggregate summary prefix _validate_used_template_paths() raises with,
# capturing the failure count as group 1 and the semicolon-joined per-key
# summary as group 2. Failure-kind-neutral by design -- this same prefix
# is shared by every failure kind this validator reports.
AGGREGATE_PREFIX_RE = re.compile(
    r"typst: (\d+) pre-write template path failure\(s\): (.*)"
)


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str = "typst"
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard. Every gate module in this suite carries its own
    copy of this helper rather than importing a sibling module's.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            builder,
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


def _typ_files(build_dir: Path) -> list:
    """The LIST of ``.typ`` files under ``build_dir`` -- returned (not
    just a bool) so a failing assertion can name the survivors."""
    if not build_dir.exists():
        return []
    return sorted(build_dir.rglob("*.typ"))


def _extract_aggregate_message(combined_output: str) -> str:
    """Locate the aggregate ``ExtensionError`` sentence -- the substring
    beginning ``"typst: N pre-write template path failure(s): ..."`` --
    in ``combined_output`` and return it verbatim. Copied from
    ``tests/test_templates_path_collision_gate.py``'s
    ``_extract_aggregate_message()``."""
    match = AGGREGATE_PREFIX_RE.search(combined_output)
    return match.group(0) if match else ""


def _extract_normalized_aggregate_message(
    combined_output: str, fixture_dir: Path
) -> str:
    """Extract the aggregate message (via ``_extract_aggregate_message()``)
    and replace every occurrence of ``fixture_dir``'s OWN directory name
    (e.g. ``"mixed_prewrite_failures_a_gate"``) with a fixed placeholder
    token.

    The CONF-17 failure sentence embeds the RESOLVED absolute template
    path and the absolute ``srcdir`` (via ``_conf17_violation_message()``),
    so fixture A's and fixture B's raw aggregate messages differ in every
    absolute path they contain even though the two fixtures declare the
    SAME two violations -- the two fixture trees live at different
    absolute paths, and each path's directory name embeds which fixture
    it is. Replacing that one differing path component is what makes the
    two messages comparable for identity: everything ELSE in the message
    (the shared worktree prefix, the sub-path suffix, the key names, the
    static sentence text) is already byte-identical between the two
    fixtures."""
    message = _extract_aggregate_message(combined_output)
    return message.replace(fixture_dir.name, "FIXTURE_DIR")


def test_fixture_a_refuses_with_two_failures_naming_both_markers(tmp_path):
    """Building fixture A refuses with ONE ``ExtensionError`` whose
    aggregate prefix reports a failure count of 2, and whose body
    contains both the CONF-17/A-01 sentence fragment and the reserved-key
    case sentence fragment."""
    build_dir = tmp_path / "build"
    result = _run_sphinx_build(FIXTURE_DIR_A, build_dir, "typst")
    combined_output = result.stdout + result.stderr

    assert result.returncode != 0, (
        f"Expected fixture A's build to FAIL on the cross-kind "
        f"aggregation:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )

    match = AGGREGATE_PREFIX_RE.search(combined_output)
    assert match, (
        f"Expected an aggregate 'typst: N pre-write template path "
        f"failure(s):' sentence in fixture A's build output:\n"
        f"{combined_output}"
    )
    assert match.group(1) == "2", (
        f"Expected fixture A's aggregate failure count to be 2 (read "
        f"from the aggregate prefix, not counted from substrings), got "
        f"{match.group(1)!r} in:\n{combined_output}"
    )

    assert CONF17_PREWRITE_MARKER in combined_output, (
        f"Expected the CONF17_PREWRITE_MARKER sentence "
        f"{CONF17_PREWRITE_MARKER!r} in fixture A's build output:\n"
        f"{combined_output}"
    )
    assert RESERVED_KEY_CASE_MARKER in combined_output, (
        f"Expected the RESERVED_KEY_CASE_MARKER sentence "
        f"{RESERVED_KEY_CASE_MARKER!r} in fixture A's build output:\n"
        f"{combined_output}"
    )


def test_fixture_b_refuses_with_two_failures_naming_both_markers(tmp_path):
    """Fixture B -- the SAME two violations declared in INVERTED order --
    also refuses with an aggregate failure count of 2, naming both
    markers. Proves the inverted-order fixture independently exercises
    both failure kinds before the identity comparison below relies on
    it."""
    build_dir = tmp_path / "build"
    result = _run_sphinx_build(FIXTURE_DIR_B, build_dir, "typst")
    combined_output = result.stdout + result.stderr

    assert result.returncode != 0, (
        f"Expected fixture B's build to FAIL on the cross-kind "
        f"aggregation:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )

    match = AGGREGATE_PREFIX_RE.search(combined_output)
    assert match, (
        f"Expected an aggregate 'typst: N pre-write template path "
        f"failure(s):' sentence in fixture B's build output:\n"
        f"{combined_output}"
    )
    assert match.group(1) == "2", (
        f"Expected fixture B's aggregate failure count to be 2 (read "
        f"from the aggregate prefix, not counted from substrings), got "
        f"{match.group(1)!r} in:\n{combined_output}"
    )

    assert CONF17_PREWRITE_MARKER in combined_output, (
        f"Expected the CONF17_PREWRITE_MARKER sentence "
        f"{CONF17_PREWRITE_MARKER!r} in fixture B's build output:\n"
        f"{combined_output}"
    )
    assert RESERVED_KEY_CASE_MARKER in combined_output, (
        f"Expected the RESERVED_KEY_CASE_MARKER sentence "
        f"{RESERVED_KEY_CASE_MARKER!r} in fixture B's build output:\n"
        f"{combined_output}"
    )


def test_message_identical_across_inverted_declaration_order(tmp_path):
    """D-03's core guarantee, exercised across declaration order rather
    than merely across repeated runs of one project: fixture A's and
    fixture B's aggregate messages are IDENTICAL once each fixture's own
    source-directory name is normalized out -- asserting message
    IDENTITY (``assert a == b``), not merely that both contain the same
    substrings. This is the assertion an ordering regression (e.g. a
    switch from ``sorted()`` iteration to declaration-order iteration)
    would actually break."""
    build_dir_a = tmp_path / "build_a"
    build_dir_b = tmp_path / "build_b"
    result_a = _run_sphinx_build(FIXTURE_DIR_A, build_dir_a, "typst")
    result_b = _run_sphinx_build(FIXTURE_DIR_B, build_dir_b, "typst")

    combined_a = result_a.stdout + result_a.stderr
    combined_b = result_b.stdout + result_b.stderr

    message_a = _extract_normalized_aggregate_message(combined_a, FIXTURE_DIR_A)
    message_b = _extract_normalized_aggregate_message(combined_b, FIXTURE_DIR_B)

    assert message_a, f"No aggregate message found in fixture A's output:\n{combined_a}"
    assert message_b, f"No aggregate message found in fixture B's output:\n{combined_b}"
    assert message_a == message_b, (
        f"Expected a byte-identical aggregate message across inverted "
        f"declaration order (after normalizing each fixture's own "
        f"directory name):\nA: {message_a}\nB: {message_b}"
    )

    # The two fixtures' conf.py files genuinely differ (declaration
    # order is inverted) -- this identity assertion is meaningful
    # precisely BECAUSE the inputs are not byte-identical.
    conf_a = (FIXTURE_DIR_A / "conf.py").read_text()
    conf_b = (FIXTURE_DIR_B / "conf.py").read_text()
    assert conf_a != conf_b, (
        "Expected fixture A's and fixture B's conf.py to genuinely "
        "differ in declaration order -- if they are identical, the "
        "message-identity assertion above is vacuous."
    )


def test_no_typ_file_written_after_either_refusal(tmp_path):
    """Both refused builds leave zero ``.typ`` files under their build
    directories -- the same "no partial output" property every other
    pre-write refusal in this suite carries."""
    build_dir_a = tmp_path / "build_a"
    build_dir_b = tmp_path / "build_b"
    _run_sphinx_build(FIXTURE_DIR_A, build_dir_a, "typst")
    _run_sphinx_build(FIXTURE_DIR_B, build_dir_b, "typst")

    survivors_a = _typ_files(build_dir_a)
    survivors_b = _typ_files(build_dir_b)
    assert not survivors_a, (
        f"Expected NO .typ file written when fixture A's cross-kind "
        f"aggregation refuses, found: {survivors_a}"
    )
    assert not survivors_b, (
        f"Expected NO .typ file written when fixture B's cross-kind "
        f"aggregation refuses, found: {survivors_b}"
    )
