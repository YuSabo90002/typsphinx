"""
CR-01 / D-07 (Phase 54.1 plan 03): real-``sphinx-build`` subprocess gate
proving that a DECLARED ``typst_document_templates`` registry key
differing from the reserved built-in registry key
(``RESERVED_REGISTRY_KEY = "typst"``) only by CAPITALISATION refuses the
build pre-write, instead of silently reaching ``finish()`` and only
surfacing there (and only then) as a bundle-destination collision.

CONF-16 rejects only the LITERAL spelling ``"typst"`` at declaration time.
CONF-18 compares declared keys only against EACH OTHER, never against the
synthesized built-in key -- so a lone declared key that merely case-folds
onto the reserved key passes both existing checks. This gate closes that
structural gap.

The comparison routes exclusively through the existing
``TypstBuilder._collision_key()`` case-folding primitive (D-07) -- never a
second ``.casefold()``/``.lower()`` helper.

Pre-fix RED transcript recorded verbatim in
``.planning/phases/54.1-bundle-directory-safety-templates-path-collision-refusal-and/54.1-03-RED-EVIDENCE.md``
(binding constraint #6).
"""

import subprocess
import sys
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "reserved_key_case_prewrite_gate"

# The fragment the new case-collision message must contain -- asserted by
# both tests below and reused as this gate's own marker constant so a
# future wording change is caught in exactly one place.
RESERVED_KEY_CASE_MARKER = "differs from the built-in 'typst' registry key only by case"


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


def test_reserved_key_case_collision_refuses_build(tmp_path):
    """D-07: a declared registry key ("Typst") differing from the reserved
    built-in key ("typst") only by case refuses the build with the
    RESERVED_KEY_CASE_MARKER sentence."""
    build_dir = tmp_path / "build"
    result = _run_sphinx_build(FIXTURE_DIR, build_dir, "typst")
    combined_output = result.stdout + result.stderr

    assert result.returncode != 0, (
        f"Expected the build to FAIL on the reserved-key case collision:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert RESERVED_KEY_CASE_MARKER in combined_output, (
        f"Expected the RESERVED_KEY_CASE_MARKER sentence "
        f"{RESERVED_KEY_CASE_MARKER!r} in the build output:\n{combined_output}"
    )


def test_no_typ_file_written_after_reserved_key_case_refusal(tmp_path):
    """The refusal happens in the pre-write pass, so zero .typ files reach
    disk -- RED today, since neither CONF-16 nor CONF-18 catches a case-
    only collision against the SYNTHESIZED built-in key at all, so
    nothing refuses this fixture pre-fix (it would build past write() and
    only collide with the built-in key's bundle destination at finish(),
    if the built-in key is even used)."""
    build_dir = tmp_path / "build"
    _run_sphinx_build(FIXTURE_DIR, build_dir, "typst")
    survivors = _typ_files(build_dir)
    assert not survivors, (
        f"Expected NO .typ file written when the reserved-key case "
        f"collision refuses, found: {survivors}"
    )
