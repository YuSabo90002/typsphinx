"""
OUT-07 (Phase 54 plan 07): real-``sphinx-build`` subprocess gate proving
that ``_validate_output_path_collisions()``'s widened ``_template/``
prefix reservation refuses ANY content or wrapper file whose resolved
output path lives under the reserved template-bundle directory --
replacing the narrower exact-name claim on the single, now-nonexistent
``_template.typ`` infrastructure file (Phase 54 plans 04/05 deleted its
writer; this plan's Task 1 deleted the exact-name claim itself).

``tests/fixtures/template_prefix_reservation_gate/`` is
``tests/fixtures/template_named_dir_master/``'s NEGATIVE successor
(Phase 22.1/CR-01's original fixture, relocated): it keeps the ORIGINAL
docname layout verbatim -- both docnames living inside a source
directory literally named ``_template`` -- but where that layout used to
compile successfully (Phase 22.1 through Phase 54 plan 05), it is now a
build error. See that fixture's own ``conf.py`` comment block for the
full history of why the layout inverted from positive to negative, and
``tests/fixtures/nested_dir_multi_master/`` for the POSITIVE successor
that carries this fixture's other two regression intents (the
multi-entry and per-master author-divergence proofs) forward.

Every test in this module is a must-FAIL gate: ``returncode != 0`` is
always asserted, never a success, and NO output ``.typ``/``.pdf`` file is
ever written under the build directory (D-02's no-partial-write rule,
carried into OUT-07 -- the refusal happens before any write).
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "template_prefix_reservation_gate"

# Both entries' WRAPPER targets are bare filenames that resolve at the
# outdir root (template-dir-master.typ / template-dir-sub.typ) -- it is
# specifically the two docname-derived CONTENT paths that trip the
# reservation, since a docname gets a content file unconditionally
# (COMP-01/OUT-03), regardless of where either entry's wrapper resolves.
OFFENDING_DOCNAME_DEPTH1 = "_template/index"
OFFENDING_DOCNAME_DEPTH2 = "_template/sub/index"


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard.
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


def _no_typ_files_written(build_dir: Path) -> bool:
    """OUT-07/D-02: no output file at all when the reservation refuses."""
    if not build_dir.exists():
        return True
    return not any(build_dir.rglob("*.typ"))


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the template-prefix reservation gate",
)
class TestTemplatePrefixReservationGate:
    """OUT-07: a source tree whose docnames live under the reserved
    ``_template/`` directory stops the build, on both builders, naming
    every offending docname in one aggregated ``ExtensionError``, before
    any file is written."""

    def test_typst_build_fails(self, tmp_path):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(FIXTURE_DIR, build_dir, "typst")
        assert result.returncode != 0, (
            f"Expected the build to FAIL on docnames living under the "
            f"reserved _template/ directory:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_typstpdf_build_also_fails(self, tmp_path):
        """Both builders share ``_validate_output_path_collisions()`` --
        the reservation refuses identically regardless of which builder
        runs (D-03)."""
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(FIXTURE_DIR, build_dir, "typstpdf")
        assert result.returncode != 0, (
            f"Expected -b typstpdf to FAIL identically:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_error_is_extension_error(self, tmp_path):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(FIXTURE_DIR, build_dir, "typst")
        combined_output = result.stdout + result.stderr
        assert (
            "ExtensionError" in combined_output
        ), f"Expected an ExtensionError:\n{combined_output}"

    def test_error_names_both_offending_docnames(self, tmp_path):
        """Every offending docname in a whole subtree under the reserved
        name is named in ONE build's error -- not just the first."""
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(FIXTURE_DIR, build_dir, "typst")
        combined_output = result.stdout + result.stderr
        assert OFFENDING_DOCNAME_DEPTH1 in combined_output, (
            f"Expected the depth-1 offending docname "
            f"{OFFENDING_DOCNAME_DEPTH1!r} named:\n{combined_output}"
        )
        assert OFFENDING_DOCNAME_DEPTH2 in combined_output, (
            f"Expected the depth-2 offending docname "
            f"{OFFENDING_DOCNAME_DEPTH2!r} ALSO named -- the error must "
            f"aggregate every offender, not report only the first:\n"
            f"{combined_output}"
        )

    def test_error_names_the_reserved_directory(self, tmp_path):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(FIXTURE_DIR, build_dir, "typst")
        combined_output = result.stdout + result.stderr
        assert (
            "_template" in combined_output
        ), f"Expected the reserved directory named:\n{combined_output}"
        assert "reserved" in combined_output, (
            f"Expected the error to say the directory is reserved for "
            f"template bundles:\n{combined_output}"
        )

    def test_no_typ_file_written_after_refusal(self, tmp_path):
        """D-02, carried into OUT-07: the refusal happens BEFORE any
        write, so a refused project leaves no partial output behind."""
        build_dir = tmp_path / "build"
        _run_sphinx_build(FIXTURE_DIR, build_dir, "typst")
        assert _no_typ_files_written(build_dir), (
            f"Expected NO .typ file written when the reservation "
            f"refuses, found: "
            f"{list(build_dir.rglob('*.typ')) if build_dir.exists() else []}"
        )

    def test_case_variant_also_refused(self, tmp_path):
        """A-06: a differently-cased spelling of the reserved directory
        is refused on the same terms -- the predicate routes through
        ``_collision_key()``'s casefold, so a docname directory spelled
        ``_Template`` (rather than ``_template``) must be refused
        identically. Built via a TEMPORARY copy of the fixture (not a
        second committed fixture), since a repository cannot portably
        carry two directories differing only by case -- some filesystems
        cannot represent that."""
        source_copy = tmp_path / "source"
        shutil.copytree(FIXTURE_DIR, source_copy)
        (source_copy / "_template").rename(source_copy / "_Template")
        conf_py = source_copy / "conf.py"
        conf_py.write_text(
            conf_py.read_text(encoding="utf-8").replace("_template/", "_Template/"),
            encoding="utf-8",
        )

        build_dir = tmp_path / "build"
        result = _run_sphinx_build(source_copy, build_dir, "typst")
        assert result.returncode != 0, (
            f"Expected a differently-cased reserved-directory spelling "
            f"to be refused identically (A-06):\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert (
            "ExtensionError" in combined_output
        ), f"Expected an ExtensionError:\n{combined_output}"
        assert _no_typ_files_written(build_dir), (
            f"Expected NO .typ file written for the case variant either, "
            f"found: "
            f"{list(build_dir.rglob('*.typ')) if build_dir.exists() else []}"
        )
