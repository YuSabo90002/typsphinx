"""
Phase 47 plan 01, task 3 (validator landed in plan 09): real-``sphinx-build``
subprocess gate for the unified pre-write collision validator -- BLD-02
(duplicate targets), BLD-03 (wrapper-vs-content self-collision) and BLD-04
(case-insensitive target/docname collision).

Structured like ``tests/test_typst_documents_collision_gate.py`` (one
fixture-directory constant per scenario, one ``_run_sphinx_build`` helper
duplicated per this repo's own convention) but with the OPPOSITE outcome
asserted: D-01/D-02/D-03 replace the old CR-01 warn-and-fall-back contract
with a pre-write ``ExtensionError`` and NO output file written.
``TypstBuilder._validate_output_path_collisions()`` (plan 09) is what makes
every assertion here pass -- the pre-fix RED evidence each test's docstring
paraphrases is recorded in full in ``47-RED-EVIDENCE.md``.
"""

import subprocess
import sys
import unicodedata
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

FIXTURES_DIR = Path(__file__).parent / "fixtures"
BLD02_DUPLICATE_TARGET_FIXTURE_DIR = FIXTURES_DIR / "bld02_duplicate_target_gate"
BLD03_SELF_COLLISION_FIXTURE_DIR = FIXTURES_DIR / "bld03_self_collision_gate"
BLD04_CASE_COLLISION_FIXTURE_DIR = FIXTURES_DIR / "bld04_case_collision_gate"

# Whatever the new ExtensionError names -- exact wording is Claude's
# Discretion per 47-CONTEXT.md; this is the substring D-03's unified
# validator's message must contain, per 47-CONTEXT.md's "New error/warning
# message identifiers" ("typst: N output path collision(s)").
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
    reason="typst-py is required for the collision validator gate tests",
)
class TestCollisionValidatorGate:
    """
    BLD-02, BLD-03, BLD-04 -- each asserted on BOTH ``-b typst`` and
    ``-b typstpdf``, proving the one validator is shared by both builders
    (Claude's Discretion in 47-CONTEXT.md: ``TypstBuilder`` owns it,
    ``TypstPDFBuilder`` inherits it).
    """

    # -- BLD-02: two entries resolving to the same target -----------------

    def test_bld02_duplicate_target_rejected_typst(self, tmp_path):
        """
        Pre-fix (measured this task, verbatim in 47-RED-EVIDENCE.md's
        BLD-02 section): exit 0, no collision warning anywhere in
        stdout/stderr; the surviving `manual.typ` contains
        OTHER-MASTER-MARKER-BBB (count 1) but NOT INDEX-MASTER-MARKER-AAA
        (count 0) -- the first master's body was silently overwritten by
        the second, sorted-order write.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            BLD02_DUPLICATE_TARGET_FIXTURE_DIR, build_dir, "typst"
        )

        assert result.returncode != 0, (
            f"Expected the build to FAIL on a duplicate-target collision "
            f"(D-01/D-02/D-03):\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert (
            "ExtensionError" in combined_output
        ), f"Expected an ExtensionError:\n{combined_output}"
        assert (
            COLLISION_ERROR_SUBSTRING in combined_output
        ), f"Expected the collision-error substring:\n{combined_output}"
        assert "index" in combined_output, (
            f"Expected the FIRST colliding entry's docname named in the "
            f"error:\n{combined_output}"
        )
        assert "other" in combined_output, (
            f"Expected the SECOND colliding entry's docname named in the "
            f"error:\n{combined_output}"
        )
        assert _no_typ_files_written(build_dir), (
            f"D-02: expected NO .typ file written when a collision is "
            f"found, found: {list(build_dir.rglob('*.typ')) if build_dir.exists() else []}"
        )

    def test_bld02_duplicate_target_rejected_typstpdf(self, tmp_path):
        """
        Pre-fix (measured this task): `-b typstpdf` of this fixture ALSO
        exits 0 and produces `manual.pdf` from whichever entry's `.typ`
        survived the silent overwrite -- the same defect, undetected by
        either builder today.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            BLD02_DUPLICATE_TARGET_FIXTURE_DIR, build_dir, "typstpdf"
        )

        assert result.returncode != 0, (
            f"Expected the build to FAIL on a duplicate-target collision "
            f"(D-01/D-02/D-03), both builders sharing one validator:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert (
            "ExtensionError" in combined_output
        ), f"Expected an ExtensionError:\n{combined_output}"
        assert (
            COLLISION_ERROR_SUBSTRING in combined_output
        ), f"Expected the collision-error substring:\n{combined_output}"

    # -- BLD-03: wrapper target colliding with its own content path -------

    def test_bld03_self_collision_rejected_typst(self, tmp_path):
        """
        Pre-fix (measured this task, verbatim in 47-RED-EVIDENCE.md's
        BLD-03 section): `[("index", "index.typ", ...)]` exits 0 with no
        warning today -- the exact configuration D-01 names as the one
        that builds successfully in v0.7.x and must stop building.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(BLD03_SELF_COLLISION_FIXTURE_DIR, build_dir, "typst")

        assert result.returncode != 0, (
            f"Expected the build to FAIL on the self-collision (D-01):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert (
            "ExtensionError" in combined_output
        ), f"Expected an ExtensionError:\n{combined_output}"
        assert (
            COLLISION_ERROR_SUBSTRING in combined_output
        ), f"Expected the collision-error substring:\n{combined_output}"
        assert not (build_dir / "index.typ").exists(), (
            f"D-01 + D-02: expected NO index.typ written when the wrapper "
            f"self-collides with its own content file"
        )

    def test_bld03_self_collision_rejected_typstpdf(self, tmp_path):
        """
        Pre-fix (measured this task): `-b typstpdf` of this fixture ALSO
        exits 0 and produces `index.pdf` -- the self-collision is
        undetected by either builder today.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            BLD03_SELF_COLLISION_FIXTURE_DIR, build_dir, "typstpdf"
        )

        assert result.returncode != 0, (
            f"Expected the build to FAIL on the self-collision (D-01), "
            f"both builders sharing one validator:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert (
            "ExtensionError" in combined_output
        ), f"Expected an ExtensionError:\n{combined_output}"
        assert (
            COLLISION_ERROR_SUBSTRING in combined_output
        ), f"Expected the collision-error substring:\n{combined_output}"

    # -- BLD-04: a target differing from a docname only by case -----------

    def test_bld04_case_collision_rejected_typst(self, tmp_path):
        """
        Pre-fix (measured this task, verbatim in 47-RED-EVIDENCE.md's
        BLD-04 section): `Manual.typ` (target) and `manual` (docname,
        content path `manual.typ`) coexist as two DISTINCT files on this
        (Linux, case-sensitive) filesystem -- exit 0, no warning. D-05
        mandates `casefold()`-normalized comparison on EVERY platform, so
        this must become a build-time error here too, not only on a
        physically case-insensitive filesystem.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(BLD04_CASE_COLLISION_FIXTURE_DIR, build_dir, "typst")

        assert result.returncode != 0, (
            f"Expected the build to FAIL on the case-insensitive collision "
            f"(D-05), even on Linux:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert (
            "ExtensionError" in combined_output
        ), f"Expected an ExtensionError:\n{combined_output}"
        assert (
            COLLISION_ERROR_SUBSTRING in combined_output
        ), f"Expected the collision-error substring:\n{combined_output}"

    def test_bld04_case_collision_rejected_typstpdf(self, tmp_path):
        """
        Pre-fix (measured this task): `-b typstpdf` of this fixture ALSO
        exits 0 and produces both `index-wrapper.pdf` and `Manual.pdf` --
        the case-collision is undetected by either builder today, on Linux.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            BLD04_CASE_COLLISION_FIXTURE_DIR, build_dir, "typstpdf"
        )

        assert result.returncode != 0, (
            f"Expected the build to FAIL on the case-insensitive collision "
            f"(D-05), both builders sharing one validator:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert (
            "ExtensionError" in combined_output
        ), f"Expected an ExtensionError:\n{combined_output}"
        assert (
            COLLISION_ERROR_SUBSTRING in combined_output
        ), f"Expected the collision-error substring:\n{combined_output}"


class TestCollisionKeyUnit:
    """
    BLD-04's load-bearing unit half: Linux cannot observe the physical
    case-insensitive overwrite (its own filesystem is case-sensitive), so
    the fixture proving BLD-04's fix must assert the COMPARISON itself
    folds case, independent of any real filesystem behavior -- per
    47-RESEARCH.md's Validation Architecture table.
    """

    def test_collision_key_folds_case_but_not_unicode_normalization(self):
        """
        D-05 (locked): comparison is `casefold()`-normalized on both sides,
        on every platform -- but Unicode normalization (NFC/NFD) is
        deliberately NOT applied, only case folding.
        """
        from typsphinx.builder import TypstBuilder

        assert TypstBuilder._collision_key("Manual.typ") == (
            TypstBuilder._collision_key("manual.typ")
        ), "Expected casefold()-normalized equality across case"
        assert TypstBuilder._collision_key("MANUAL") == (
            TypstBuilder._collision_key("manual")
        ), "Expected casefold()-normalized equality across case"

        # D-05's explicit exclusion: NFC vs NFD normalization is NOT
        # applied -- these two strings are canonically equivalent Unicode
        # (both render as "Å", capital A with ring above) but are
        # DIFFERENT code point sequences, and casefold() alone does not
        # unify them.
        nfc_angstrom = unicodedata.normalize("NFC", "Å")
        nfd_angstrom = unicodedata.normalize("NFD", "Å")
        assert nfc_angstrom != nfd_angstrom, (
            "Test setup invariant: NFC and NFD forms must be different "
            "code point sequences for this assertion to be meaningful"
        )
        assert TypstBuilder._collision_key(nfc_angstrom) != (
            TypstBuilder._collision_key(nfd_angstrom)
        ), "Expected NO Unicode normalization -- D-05's explicit exclusion"
