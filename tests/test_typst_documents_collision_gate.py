"""
D-01/D-02/D-03 (Phase 47 plan 09): real-``sphinx-build`` subprocess gate
proving that a ``typst_documents`` target name (derived or explicit) that
collides with a real docname's own output path, or with the reserved
``_template.typ`` infrastructure file, now FAILS the build with a single
pre-write ``ExtensionError`` -- this REPLACES CR-01's warn-and-fall-back
behaviour, which used to keep both documents and merely warn.

The content/wrapper split (COMP-01/COMP-02) makes CR-01's old fallback
unusable: falling back to the docname lands the wrapper exactly on that
docname's own content file, which is the very collision it was trying to
avoid. D-01 accepts that a configuration such as
``typst_documents = [("index", "index.typ", ...)]`` -- which built
successfully, with a warning, before this phase -- now fails the build
outright; the user must rename the colliding target.

Every test in this module is a must-FAIL gate (the OPPOSITE polarity of
every other module in this suite named ``..._render_gate.py`` /
``..._gate.py`` that asserts a compile succeeds): ``returncode != 0`` is
asserted, never a success, and NO output ``.typ``/``.pdf`` file is ever
written (D-02's no-partial-write rule).
"""

import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

FIXTURES_DIR = Path(__file__).parent / "fixtures"
DERIVED_DOCNAME_COLLISION_FIXTURE_DIR = FIXTURES_DIR / "derived_docname_collision_gate"
DERIVED_TEMPLATE_COLLISION_FIXTURE_DIR = (
    FIXTURES_DIR / "derived_template_collision_gate"
)
EXPLICIT_DOCNAME_COLLISION_FIXTURE_DIR = (
    FIXTURES_DIR / "explicit_docname_collision_gate"
)
EXPLICIT_TEMPLATE_COLLISION_FIXTURE_DIR = (
    FIXTURES_DIR / "explicit_template_collision_gate"
)

# D-03's unified validator's message substring -- matches
# tests/test_collision_validator_gate.py's own constant of the same value.
COLLISION_ERROR_SUBSTRING = "output path collision"


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
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


def _no_typ_files_written(build_dir: Path) -> bool:
    """D-02: no output file at all when any collision is found."""
    if not build_dir.exists():
        return True
    return not any(build_dir.rglob("*.typ"))


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the collision-gate tests",
)
class TestTypstDocumentsCollisionGate:
    """D-01/D-02/D-03: a typst_documents target name colliding with a real
    docname's own content path, or the reserved _template.typ, now FAILS
    the build with a single ExtensionError and writes NO output file, on
    both the derived-default and explicit typst_documents paths."""

    def test_derived_default_docname_collision_fails_build(self, tmp_path):
        """
        Zero-configuration collision: `project = "Chapter 1"` derives to the
        target `chapter1.typ`, identical to the real `chapter1.rst`
        document's own content path. `-b typst` must exit non-zero, raise
        an ExtensionError naming the collision, and write NO `.typ` file
        at all (D-02) -- REPLACES the old "exit 0, both documents kept,
        warning only" contract (D-03).
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            DERIVED_DOCNAME_COLLISION_FIXTURE_DIR, build_dir, "typst"
        )

        assert result.returncode != 0, (
            f"Expected the build to FAIL on the derived-default docname "
            f"collision (D-01):\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert (
            "ExtensionError" in combined_output
        ), f"Expected an ExtensionError:\n{combined_output}"
        assert (
            COLLISION_ERROR_SUBSTRING in combined_output
        ), f"Expected the collision-error substring:\n{combined_output}"
        assert "chapter1" in combined_output, (
            f"Expected the colliding docname 'chapter1' named in the "
            f"error:\n{combined_output}"
        )
        assert _no_typ_files_written(build_dir), (
            f"D-02: expected NO .typ file written when a collision is "
            f"found, found: "
            f"{list(build_dir.rglob('*.typ')) if build_dir.exists() else []}"
        )

    def test_derived_default_docname_collision_fails_pdf_build(self, tmp_path):
        """
        The `-b typstpdf` counterpart: the same zero-configuration collision
        must ALSO exit non-zero, with no PDF produced at all -- both
        builders share the one validator (D-03).
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            DERIVED_DOCNAME_COLLISION_FIXTURE_DIR, build_dir, "typstpdf"
        )

        assert result.returncode != 0, (
            f"Expected the build to FAIL on the derived-default docname "
            f"collision (D-01), both builders sharing one validator:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert (
            "ExtensionError" in combined_output
        ), f"Expected an ExtensionError:\n{combined_output}"
        assert (
            COLLISION_ERROR_SUBSTRING in combined_output
        ), f"Expected the collision-error substring:\n{combined_output}"
        assert "cyclic import" not in combined_output, (
            f"Expected the NEW pre-write ExtensionError, not the OLD "
            f"cyclic-import compile fatal:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        pdf_file = build_dir / "index.pdf"
        assert not pdf_file.exists(), (
            f"D-02: expected NO index.pdf written when a collision is "
            f"found:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert _no_typ_files_written(build_dir), (
            f"D-02: expected NO .typ file written when a collision is "
            f"found, found: "
            f"{list(build_dir.rglob('*.typ')) if build_dir.exists() else []}"
        )

    def test_derived_default_template_collision_fails_build(self, tmp_path):
        """
        Zero-configuration RESERVED-TEMPLATE clobber: `project = "_Template"`
        derives to the target `_template.typ`, identical to the reserved
        shared-template basename `_write_template_file()` writes at the
        outdir root. `-b typst` must exit non-zero, raise an
        ExtensionError naming the collision, and write NO `.typ` file at
        all -- including `_template.typ` itself (D-02).
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            DERIVED_TEMPLATE_COLLISION_FIXTURE_DIR, build_dir, "typst"
        )

        assert result.returncode != 0, (
            f"Expected the build to FAIL on the derived-default template "
            f"collision (D-01):\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert (
            "ExtensionError" in combined_output
        ), f"Expected an ExtensionError:\n{combined_output}"
        assert (
            COLLISION_ERROR_SUBSTRING in combined_output
        ), f"Expected the collision-error substring:\n{combined_output}"
        assert "_template.typ" in combined_output, (
            f"Expected the reserved _template.typ named in the error:\n"
            f"{combined_output}"
        )
        assert _no_typ_files_written(build_dir), (
            f"D-02: expected NO .typ file written when a collision is "
            f"found (including _template.typ itself), found: "
            f"{list(build_dir.rglob('*.typ')) if build_dir.exists() else []}"
        )

    def test_explicit_target_docname_collision_fails_build(self, tmp_path):
        """
        Explicit-path docname collision: `typst_documents = [("index",
        "chapter1.typ", ...)]` names an existing docname's own content path
        as the master's target. `-b typst` must exit non-zero, raise an
        ExtensionError naming the collision, and write NO `.typ` file.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            EXPLICIT_DOCNAME_COLLISION_FIXTURE_DIR, build_dir, "typst"
        )

        assert result.returncode != 0, (
            f"Expected the build to FAIL on the explicit docname "
            f"collision (D-01):\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert (
            "ExtensionError" in combined_output
        ), f"Expected an ExtensionError:\n{combined_output}"
        assert (
            COLLISION_ERROR_SUBSTRING in combined_output
        ), f"Expected the collision-error substring:\n{combined_output}"
        assert "chapter1" in combined_output, (
            f"Expected the colliding docname 'chapter1' named in the "
            f"error:\n{combined_output}"
        )
        assert _no_typ_files_written(build_dir), (
            f"D-02: expected NO .typ file written when a collision is "
            f"found, found: "
            f"{list(build_dir.rglob('*.typ')) if build_dir.exists() else []}"
        )

    def test_explicit_target_template_collision_fails_build(self, tmp_path):
        """
        Explicit-path reserved-template clobber: `typst_documents =
        [("index", "_template.typ", ...)]` names the reserved shared-
        template basename as the master's target. `-b typst` must exit
        non-zero, raise an ExtensionError naming the collision, and write
        NO `.typ` file at all -- including `_template.typ` itself.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            EXPLICIT_TEMPLATE_COLLISION_FIXTURE_DIR, build_dir, "typst"
        )

        assert result.returncode != 0, (
            f"Expected the build to FAIL on the explicit template "
            f"collision (D-01):\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert (
            "ExtensionError" in combined_output
        ), f"Expected an ExtensionError:\n{combined_output}"
        assert (
            COLLISION_ERROR_SUBSTRING in combined_output
        ), f"Expected the collision-error substring:\n{combined_output}"
        assert "_template.typ" in combined_output, (
            f"Expected the reserved _template.typ named in the error:\n"
            f"{combined_output}"
        )
        assert _no_typ_files_written(build_dir), (
            f"D-02: expected NO .typ file written when a collision is "
            f"found (including _template.typ itself), found: "
            f"{list(build_dir.rglob('*.typ')) if build_dir.exists() else []}"
        )
