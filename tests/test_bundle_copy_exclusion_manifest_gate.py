"""
GATE-01 BLD-06/OUT-04 real-compile regression gate (Phase 54): proves the
per-key bundle copy (a) is a manifest-diff proof, not merely a
presence-only proof -- SC#3 requires "no file I didn't expect is present",
which only a set-equality assertion can show -- and (b) excludes exactly
D-04's four kinds (``.git``, ``.DS_Store``, ``Thumbs.db``, editor
backups) while still copying recursively.

D-01 (an existing destination bundle is overwritten in place, never
deleted first) is also encoded here as a test rather than left as prose:
``test_rerun_leaves_a_removed_source_file_in_place`` builds twice into the
SAME output directory and asserts a file removed from the source between
builds is still present at the destination -- accepted behaviour on an
incremental rebuild, not a defect.

Scaffolding is modelled on ``tests/test_typst_lang_gate.py``'s
``_run_sphinx_build()`` / ``TYPST_AVAILABLE`` idiom. This fixture's
class-scoped ``build`` fixture additionally ``shutil.copytree``s the
committed fixture into a FRESH ``tmp_path_factory``-scoped source
directory (D-01: the manifest claim is a claim about a CLEAN output
directory, so the build target must be fresh too) and injects the four
excluded kinds into the copy at runtime -- none of the four is committed
to this repository (a nested ``.git`` directory cannot be tracked by git
at all, and the other three are exactly the kinds a working tree
routinely gitignores).

This module is marked ``xfail(strict=False)`` -- see
``54-01-RED-EVIDENCE.md``'s ``## Handover`` section; ``54-04`` removes the
marker once the per-key bundle relocation lands and proves this gate
green.
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

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "bundle_exclusion_manifest_gate"

# D-04's exclusion set, named as literals (also asserted structurally by
# test_each_excluded_kind_is_named_in_the_expected_set_comment below):
# ".git" (a directory), ".DS_Store", "Thumbs.db", and an editor backup
# ("notes.txt~").


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text). Invoked as
    ``sys.executable -m sphinx`` -- copied near-verbatim from
    ``tests/test_typst_lang_gate.py::_run_sphinx_build``.
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


def _materialize_excluded_kinds(bundle_dir: Path) -> None:
    """
    Inject the four D-04 excluded kinds into ``bundle_dir`` (a COPY of the
    committed fixture's ``_typst/styled/`` under a fresh ``tmp_path``).
    """
    git_dir = bundle_dir / ".git"
    git_dir.mkdir(parents=True, exist_ok=True)
    (git_dir / "config").write_text("[core]\n\trepositoryformatversion = 0\n")

    (bundle_dir / ".DS_Store").write_bytes(b"\x00\x01\x02\x03")
    (bundle_dir / "Thumbs.db").write_bytes(b"\x00\x01\x02\x03")
    (bundle_dir / "notes.txt~").write_text("an editor backup file\n")


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the BLD-06/OUT-04 real-compile gate",
)
@pytest.mark.xfail(
    strict=False,
    reason=(
        "Phase 54: green only once the per-key bundle relocation lands in "
        "54-04; RED recorded in 54-01-RED-EVIDENCE.md"
    ),
)
class TestBundleCopyExclusionManifestGate:
    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        # CRITICAL: this fixture body performs no verification of its own
        # -- xfail (added in 54-01 Task 3) covers only the CALL phase; a
        # verification failure raised here would report as a setup ERROR,
        # which xfail does not swallow.
        src_dir = tmp_path_factory.mktemp("bundle_exclusion_manifest_gate_src")
        # D-01: the manifest claim is a claim about a CLEAN outdir, so the
        # committed fixture is copied into a fresh source tree rather than
        # built in place.
        shutil.copytree(FIXTURE_DIR, src_dir, dirs_exist_ok=True)

        bundle_dir = src_dir / "_typst" / "styled"
        _materialize_excluded_kinds(bundle_dir)

        build_dir = tmp_path_factory.mktemp("bundle_exclusion_manifest_gate_build")
        result = _run_sphinx_build(src_dir, build_dir, "typst")

        return {
            "result": result,
            "src_dir": src_dir,
            "bundle_dir": bundle_dir,
            "build_dir": build_dir,
        }

    def test_build_succeeds(self, build):
        result = build["result"]
        assert result.returncode == 0, (
            f"sphinx-build -b typst failed:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_bundle_manifest_is_exactly_the_expected_set(self, build):
        bundle_root = build["build_dir"] / "_template" / "styled"
        assert bundle_root.exists(), (
            f"the 'styled' bundle was not published to {bundle_root}:\n"
            f"stdout: {build['result'].stdout}\nstderr: {build['result'].stderr}"
        )
        actual_manifest = {
            p.relative_to(bundle_root).as_posix()
            for p in bundle_root.rglob("*")
            if p.is_file()
        }
        expected_manifest = {"base.typ", "assets/note.txt"}
        assert actual_manifest == expected_manifest, (
            f"published bundle manifest {actual_manifest!r} does not "
            f"equal the expected set {expected_manifest!r} -- an "
            "excluded VCS/OS metadata kind reached the output, or an "
            "expected file is missing"
        )

    def test_each_excluded_kind_is_named_in_the_expected_set_comment(self):
        """
        Source-level guard: D-04's exclusion set is enumerated in THIS
        module as literals, rather than merely implied by the runtime
        behaviour above.
        """
        module_text = Path(__file__).read_text(encoding="utf-8")
        for literal in (".git", ".DS_Store", "Thumbs.db", "~"):
            assert literal in module_text, (
                f"D-04 excluded-kind literal {literal!r} is not named "
                "anywhere in this module's own text"
            )

    def test_rerun_leaves_a_removed_source_file_in_place(self, build):
        """
        D-01: an existing destination bundle is overwritten in place,
        NEVER deleted first. A file removed from the source between two
        builds into the SAME output directory is accepted to linger at
        the destination -- this is accepted behaviour on an incremental
        rebuild, not a defect.
        """
        src_dir = build["src_dir"]
        build_dir = build["build_dir"]
        destination_note = build_dir / "_template" / "styled" / "assets" / "note.txt"
        assert destination_note.exists(), (
            "note.txt was not published by the first build at " f"{destination_note}"
        )

        source_note = src_dir / "_typst" / "styled" / "assets" / "note.txt"
        source_note.unlink()

        rerun_result = _run_sphinx_build(src_dir, build_dir, "typst")
        assert rerun_result.returncode == 0, (
            f"the incremental rebuild failed:\nstdout: {rerun_result.stdout}\n"
            f"stderr: {rerun_result.stderr}"
        )
        assert destination_note.exists(), (
            "note.txt, removed from the SOURCE bundle before the second "
            "build, was deleted from the DESTINATION -- this extension "
            "must never delete a file under outdir (D-01)"
        )
