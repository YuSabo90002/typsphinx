"""
OUT-02: real-``sphinx-build`` subprocess gate proving that a
``typst_documents`` target attempting to escape ``outdir`` -- a parent-
traversal segment, an absolute path, or a drive-qualified path -- is still
refused with a warning and a safe (basename) fallback after OUT-01's
separator-membership reversal, and that nothing is ever written outside
``outdir`` for any of the three escape shapes.

RESEARCH.md's Pitfall 4 names this the single highest-risk regression site
in the whole phase: all four conditions of the old ``is_guarded`` boolean
lived in one OR-expression, and a naive reading of OUT-01 risks deleting
OUT-02's security half along with the reversed separator-membership term.
A warning-text assertion alone cannot prove containment -- this module adds
the containment proof: every regular file under the build directory must
resolve, via ``Path.resolve()``, to a path under the resolved build
directory.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from _path_naming import path_named_in

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

FIXTURES_DIR = Path(__file__).parent / "fixtures"
ESCAPE_TARGET_GATE_FIXTURE_DIR = FIXTURES_DIR / "out02_escape_target_gate"

ESCAPE_WARNING_SUBSTRING = "a path is not supported in a typst_documents target name"


def _run_sphinx_build(
    source_dir: Path,
    build_dir: Path,
    builder: str,
    env: dict | None = None,
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard. Every gate module in this suite carries its own
    copy of this helper rather than importing a sibling module's.

    ``env``, when given, is a mapping of extra variables MERGED on top of a
    copy of the current process environment (not a replacement), so the
    subprocess still inherits PATH and the active venv.
    """
    subprocess_env = None
    if env is not None:
        subprocess_env = dict(os.environ)
        subprocess_env.update(env)

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
        env=subprocess_env,
    )


def _target_for_shape(shape: str) -> str:
    """The exact target string ``conf.py`` resolves ``TYPSPHINX_ESCAPE_SHAPE``
    to -- kept in one place so the warning-text assertion below can name the
    same string the fixture's own ``conf.py`` used, without re-implementing
    ``conf.py``'s ``os.name`` branch here."""
    if shape == "traversal":
        return "../escape.typ"
    if shape == "absolute":
        return "\\\\escape.typ" if os.name == "nt" else "/tmp/escape.typ"
    if shape == "drive":
        return "C:\\escape.typ"
    raise ValueError(f"unknown escape shape: {shape!r}")


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the escape-target-gate tests",
)
@pytest.mark.parametrize("shape", ["traversal", "absolute", "drive"])
def test_escape_shape_refused_with_containment_proof(shape, tmp_path):
    """OUT-02: each escape shape still exits 0, warns naming the offending
    target, writes the wrapper at the basename fallback inside the build
    directory, and -- the containment proof -- every regular file under
    the build directory resolves under the resolved build directory.

    Marked to run on every platform (including the drive-qualified case),
    per the plan's own instruction: the drive check is a string-shape
    check, not a filesystem behaviour, so D-05's platform-independence
    principle applies to it too.
    """
    build_dir = tmp_path / "build"
    target = _target_for_shape(shape)

    result = _run_sphinx_build(
        ESCAPE_TARGET_GATE_FIXTURE_DIR,
        build_dir,
        "typst",
        env={"TYPSPHINX_ESCAPE_SHAPE": shape},
    )

    combined_output = result.stdout + result.stderr
    assert result.returncode == 0, (
        f"Expected a successful build despite the {shape!r} escape "
        f"attempt:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )

    assert ESCAPE_WARNING_SUBSTRING in combined_output, (
        f"Expected the path-guard warning naming the refused target:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    # D-02: apply the naming predicate to the extracted warning LINE, not
    # to the whole captured output -- a raw path leaking from any other
    # source (a config echo, a traceback, a path Sphinx prints) would
    # otherwise keep this test green after the path is removed from the
    # warning itself, which would make Task 2's falsification prove
    # nothing about the thing under test.
    #
    # `_resolve_target_stem()` is invoked multiple times per build for the
    # SAME docname (once via `get_target_uri()`'s cross-reference/toctree
    # resolution calls, once via the wrapper-output-path resolution during
    # writing) -- measured live this session: an unmodified single-docname
    # fixture build emits the IDENTICAL warning line 3 times, not once.
    # De-duplicating before counting keeps D-02's actual guarantee (a
    # DIFFERENT raw path leaking from an unrelated source produces a
    # DIFFERENT line and still fails loudly here) without making this
    # assertion depend on how many internal call sites happen to log the
    # same message.
    warning_lines = list(
        dict.fromkeys(
            line
            for line in combined_output.splitlines()
            if ESCAPE_WARNING_SUBSTRING in line
        )
    )
    assert len(warning_lines) == 1, (
        f"Expected exactly one DISTINCT warning line naming the refused "
        f"target (repeats of the identical line are expected and "
        f"collapsed; a second, DIFFERENT line would indicate a raw path "
        f"leaking from an unrelated source):\n{combined_output}"
    )
    # D-01/D-03: assert MEANING, not representation format -- the
    # offending target is NAMED in the warning line, whether the message
    # site quotes it with `!r`, a hardcoded `'{value}'`, or a future
    # delimiter-aware helper. `path_named_in` requires the FULL target
    # value, never a basename, so a message that only still names the
    # same-basename `fallback` field (the D-03 trap) fails this assertion.
    assert path_named_in(target, warning_lines[0]), (
        f"Expected the warning to name the offending target {target!r} "
        f"(raw or repr()'d):\n{warning_lines[0]}"
    )

    wrapper_file = build_dir / "escape.typ"
    assert wrapper_file.exists(), (
        f"Expected the basename fallback 'escape.typ' inside the build "
        f"directory:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )

    # Containment proof: every regular file under build_dir resolves, via
    # Path.resolve(), to a path under the resolved build directory -- a
    # warning-text assertion alone cannot prove nothing escaped outdir.
    resolved_build_dir = build_dir.resolve()
    for candidate in build_dir.rglob("*"):
        if candidate.is_file():
            assert candidate.resolve().is_relative_to(resolved_build_dir), (
                f"File {candidate} escaped the build directory " f"{resolved_build_dir}"
            )

    # No file named escape.typ exists anywhere OUTSIDE the build directory
    # that this test itself can reach -- checking the build directory's own
    # parent is enough, since every escape shape this fixture exercises
    # traverses at most one level up.
    escaped_file = build_dir.parent / "escape.typ"
    assert (
        not escaped_file.exists()
    ), f"escape.typ leaked outside the build directory to {escaped_file}"
