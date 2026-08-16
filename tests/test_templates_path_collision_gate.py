"""
WR-01 (Phase 54.1 plan 01): real-``sphinx-build`` subprocess gate proving
that a used ``typst_document_templates`` registry key whose resolved
template bundle directory collides with Sphinx's own ``templates_path``
(D-01) refuses the build with an ``ExtensionError`` instead of copying
that directory into build output.

Detection is a path-relationship test against the LIVE
``self.config.templates_path`` values, resolved against ``self.srcdir``
-- never a name match on the literal string ``_templates`` (D-02). The
refusal happens in a pre-write pass at the top of ``write()``, so a
refused build leaves ZERO ``.typ`` files anywhere under the build
directory (D-04) -- the same "no partial output" property
``tests/test_template_prefix_reservation_gate.py``'s
``test_no_typ_file_written_after_refusal`` already established for
OUT-07's reservation refusal.

Pre-fix RED transcript recorded verbatim in
``.planning/phases/54.1-bundle-directory-safety-templates-path-collision-refusal-and/54.1-01-RED-EVIDENCE.md``
(binding constraint #6) -- both tests below FAIL against the pre-fix
tree, because nothing in ``typsphinx/`` reads ``templates_path`` today.
"""

import subprocess
import sys
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "templates_path_collision_gate"

# D-01: the exact sentence fragment the new ``ExtensionError`` message
# must contain, naming this specific failure kind -- asserted by both
# tests below and reused as the gate's own marker constant so a future
# wording change is caught in exactly one place.
TEMPLATES_PATH_COLLISION_MARKER = "collides with the Sphinx templates_path entry"


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


def test_collision_refuses_build(tmp_path):
    """D-01: a used key's resolved bundle directory that collides with
    ``templates_path`` refuses the build, naming the offending registry
    key, the resolved bundle directory, and the colliding
    ``templates_path`` entry."""
    build_dir = tmp_path / "build"
    result = _run_sphinx_build(FIXTURE_DIR, build_dir, "typst")
    combined_output = result.stdout + result.stderr

    assert result.returncode != 0, (
        f"Expected the build to FAIL on a templates_path collision:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert TEMPLATES_PATH_COLLISION_MARKER in combined_output, (
        f"Expected the collision marker {TEMPLATES_PATH_COLLISION_MARKER!r} "
        f"in the build output:\n{combined_output}"
    )
    assert "paper" in combined_output, (
        f"Expected the offending registry key 'paper' named:\n{combined_output}"
    )
    assert "_templates" in combined_output, (
        f"Expected the resolved bundle directory (containing "
        f"'_templates') named:\n{combined_output}"
    )
    assert "_typst" in combined_output, (
        f"Expected the non-colliding remedy directory '_typst' named:\n"
        f"{combined_output}"
    )


def test_no_typ_file_written_after_refusal(tmp_path):
    """D-04: the refusal happens in a pre-write pass at the top of
    ``write()``, so a refused build leaves NO ``.typ`` file anywhere
    under the build directory."""
    build_dir = tmp_path / "build"
    _run_sphinx_build(FIXTURE_DIR, build_dir, "typst")
    survivors = _typ_files(build_dir)
    assert not survivors, (
        f"Expected NO .typ file written when the templates_path "
        f"collision refuses the build, found: {survivors}"
    )
