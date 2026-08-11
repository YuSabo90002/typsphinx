"""
Phase 47 gap-closure plan 11: real-``sphinx-build`` subprocess gate closing
the two BLD-02/BLD-03 false negatives ``47-VERIFICATION.md`` found --
``_collision_key()`` did not normalize path SHAPE (a redundant ``./``
prefix, a doubled ``//`` separator, an embedded ``/./`` segment), and the
entry-usability PREDICATE deciding whether a ``typst_documents`` entry can
produce a wrapper file was re-derived independently at four sites instead
of being owned once.

Structured like ``tests/test_collision_validator_gate.py`` (one fixture-
directory constant per scenario, one ``_run_sphinx_build`` helper duplicated
per this repo's own convention) but recording the pre-fix RED as
``xfail(strict=True)`` rather than a separate un-asserted measurement pass --
nine of the eleven tests below fail on the unfixed tree; two are invariance
guards that already pass and must keep passing. The verbatim pre-fix
transcripts each xfail's ``reason=`` paraphrases are recorded in full in
``47-GAP-RED-EVIDENCE.md``.
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
BLD02_PATH_SHAPE_FIXTURE_DIR = FIXTURES_DIR / "bld02_path_shape_collision_gate"
BLD02_TEMPLATE_CLOBBER_FIXTURE_DIR = FIXTURES_DIR / "bld02_template_clobber_gate"
BLD03_UNDER_LENGTH_FIXTURE_DIR = FIXTURES_DIR / "bld03_under_length_entry_gate"

# Whatever the unified validator names -- exact wording is Claude's
# Discretion per 47-CONTEXT.md; this is the substring the collision
# ExtensionError's message must contain, matching
# tests/test_collision_validator_gate.py's own constant.
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
    reason="typst-py is required for the collision predicate completeness gate",
)
class TestBld02PathShapeCollisionGate:
    """
    BLD-02, shape 1: two ``typst_documents`` targets differing only in a
    redundant ``./`` prefix (``./manual.typ`` vs ``manual.typ``) must
    collide -- pre-fix, ``_collision_key()`` folded separator style and
    case (D-05) but not path SHAPE, so this pair evaded the validator
    entirely.
    """

    def test_bld02_path_shape_duplicate_rejected_typst(self, tmp_path):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(BLD02_PATH_SHAPE_FIXTURE_DIR, build_dir, "typst")

        assert result.returncode != 0, (
            f"Expected the build to FAIL on a path-shape-equivalent "
            f"duplicate target:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
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
            f"found, found: "
            f"{list(build_dir.rglob('*.typ')) if build_dir.exists() else []}"
        )

    def test_bld02_path_shape_duplicate_rejected_typstpdf(self, tmp_path):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(BLD02_PATH_SHAPE_FIXTURE_DIR, build_dir, "typstpdf")

        assert result.returncode != 0, (
            f"Expected the build to FAIL on a path-shape-equivalent "
            f"duplicate target, both builders sharing one validator:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert (
            "ExtensionError" in combined_output
        ), f"Expected an ExtensionError:\n{combined_output}"
        assert (
            COLLISION_ERROR_SUBSTRING in combined_output
        ), f"Expected the collision-error substring:\n{combined_output}"


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the collision predicate completeness gate",
)
class TestBld02TemplateClobberGate:
    """
    BLD-02, shape 2: a target that, once './'-shape normalized, IS the
    reserved ``_template.typ`` infrastructure file must collide -- pre-fix
    the wrapper silently overwrites the template every content and wrapper
    file imports.
    """

    def test_bld02_dot_slash_template_clobber_rejected_typst(self, tmp_path):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            BLD02_TEMPLATE_CLOBBER_FIXTURE_DIR, build_dir, "typst"
        )

        assert result.returncode != 0, (
            f"Expected the build to FAIL on a './'-prefixed target "
            f"clobbering the reserved _template.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert (
            "ExtensionError" in combined_output
        ), f"Expected an ExtensionError:\n{combined_output}"
        assert (
            COLLISION_ERROR_SUBSTRING in combined_output
        ), f"Expected the collision-error substring:\n{combined_output}"
        assert "_template" in combined_output, (
            f"Expected '_template' named in the collision error:\n" f"{combined_output}"
        )
        assert _no_typ_files_written(build_dir), (
            f"D-02: expected NO .typ file written when a collision is "
            f"found, found: "
            f"{list(build_dir.rglob('*.typ')) if build_dir.exists() else []}"
        )

    def test_bld02_dot_slash_template_clobber_rejected_typstpdf(self, tmp_path):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            BLD02_TEMPLATE_CLOBBER_FIXTURE_DIR, build_dir, "typstpdf"
        )

        assert result.returncode != 0, (
            f"Expected the build to FAIL on a './'-prefixed target "
            f"clobbering the reserved _template.typ, both builders "
            f"sharing one validator:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert (
            "ExtensionError" in combined_output
        ), f"Expected an ExtensionError:\n{combined_output}"
        assert (
            COLLISION_ERROR_SUBSTRING in combined_output
        ), f"Expected the collision-error substring:\n{combined_output}"


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the collision predicate completeness gate",
)
class TestBld03UnderLengthEntryGate:
    """
    BLD-03: a ``typst_documents`` entry with fewer than two elements
    (``("index",)``) must produce NO wrapper file, so ``index``'s own
    translated content survives -- pre-fix, the entry-usability predicate
    was spelled differently at the validator (which tolerates it) than at
    the write-phase wrapper loop (which does not), so the wrapper loop
    wrote a self-referential wrapper directly over the docname's own
    content file.
    """

    def test_bld03_under_length_entry_preserves_content_typst(self, tmp_path):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(BLD03_UNDER_LENGTH_FIXTURE_DIR, build_dir, "typst")

        assert result.returncode == 0, (
            f"Expected -b typst to still succeed for a tolerated "
            f"under-length entry:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        index_typ = build_dir / "index.typ"
        assert index_typ.exists(), f"Expected index.typ to exist:\n{result.stderr}"
        index_typ_content = index_typ.read_text(encoding="utf-8")
        assert "UNDERLENGTH-CONTENT-SENTINEL-CCC" in index_typ_content, (
            f"Expected index's own content sentinel to survive in "
            f"index.typ:\n{index_typ_content}"
        )
        assert "#show: project.with(" not in index_typ_content, (
            f"index.typ must stay a plain content file -- it must NOT "
            f"carry the template-application marker a wrapper would:\n"
            f"{index_typ_content}"
        )
        manual_typ = build_dir / "manual.typ"
        assert manual_typ.exists(), (
            f"Expected the well-formed 'other' entry's wrapper "
            f"manual.typ to exist:\n{result.stderr}"
        )
        manual_typ_content = manual_typ.read_text(encoding="utf-8")
        assert '#include("other.typ")' in manual_typ_content, (
            f"Expected manual.typ to include other.typ:\n" f"{manual_typ_content}"
        )
        combined_output = result.stdout + result.stderr
        assert "produces no wrapper file" in combined_output, (
            f"Expected a warning stating the under-length entry produces "
            f"no wrapper file:\n{combined_output}"
        )

    def test_bld03_under_length_entry_not_named_in_wrapper_report_typst(self, tmp_path):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(BLD03_UNDER_LENGTH_FIXTURE_DIR, build_dir, "typst")
        combined_output = result.stdout + result.stderr

        assert "wrote 1 wrapper file(s)" in combined_output, (
            f"Expected the D-07 report to name exactly ONE wrapper file "
            f"(the under-length entry produces none):\n{combined_output}"
        )
        assert "compile these: manual.typ" in combined_output, (
            f"Expected the D-07 report to name only manual.typ:\n" f"{combined_output}"
        )

    def test_bld03_under_length_entry_reported_by_finish_typstpdf(self, tmp_path):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            BLD03_UNDER_LENGTH_FIXTURE_DIR, build_dir, "typstpdf"
        )
        combined_output = result.stdout + result.stderr

        assert result.returncode != 0, (
            f"Expected -b typstpdf to fail on the under-length entry:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "has no target element" in combined_output, (
            f"Expected finish()'s aggregate error to name the "
            f"under-length entry's missing target element:\n"
            f"{combined_output}"
        )
        assert "master document(s) failed" in combined_output, (
            f"Expected the aggregate ExtensionError summary:\n" f"{combined_output}"
        )
        assert (build_dir / "manual.pdf").exists(), (
            f"D-02's attempt-all-then-raise contract: the well-formed "
            f"'other' entry should still get its PDF even though the "
            f"build as a whole fails:\n{combined_output}"
        )


class TestCollisionKeyPathShapeUnit:
    """
    BLD-02's load-bearing unit half: the comparison itself must fold path
    SHAPE, independent of any real filesystem behavior -- importing
    ``TypstBuilder`` INSIDE the test body so a missing method lands as an
    xfail rather than a module-level collection error.
    """

    def test_collision_key_normalizes_path_shape(self):
        from typsphinx.builder import TypstBuilder

        assert TypstBuilder._collision_key("./manual.typ") == (
            TypstBuilder._collision_key("manual.typ")
        ), "Expected a redundant './' prefix to normalize away"
        assert TypstBuilder._collision_key("a//b.typ") == (
            TypstBuilder._collision_key("a/b.typ")
        ), "Expected a doubled '//' separator to normalize away"
        assert TypstBuilder._collision_key("a/./b.typ") == (
            TypstBuilder._collision_key("a/b.typ")
        ), "Expected an embedded '/./' segment to normalize away"
        assert TypstBuilder._collision_key("./_template.typ") == (
            TypstBuilder._collision_key("_template.typ")
        ), "Expected a './'-prefixed reserved-file target to normalize away"

    def test_collision_key_still_folds_case_and_ignores_unicode_normalization(
        self,
    ):
        """
        Not xfail -- passes today and must keep passing after Task 2's
        path-shape normalization is added: D-05's two existing comparison
        behaviours (casefold() on, Unicode NFC/NFD normalization off) are
        unaffected by adding posixpath.normpath() to the same function.
        """
        from typsphinx.builder import TypstBuilder

        assert TypstBuilder._collision_key("Manual.typ") == (
            TypstBuilder._collision_key("manual.typ")
        ), "Expected casefold()-normalized equality across case"
        assert TypstBuilder._collision_key("MANUAL") == (
            TypstBuilder._collision_key("manual")
        ), "Expected casefold()-normalized equality across case"

        nfc_angstrom = unicodedata.normalize("NFC", "Å")
        nfd_angstrom = unicodedata.normalize("NFD", "Å")
        assert nfc_angstrom != nfd_angstrom, (
            "Test setup invariant: NFC and NFD forms must be different "
            "code point sequences for this assertion to be meaningful"
        )
        assert TypstBuilder._collision_key(nfc_angstrom) != (
            TypstBuilder._collision_key(nfd_angstrom)
        ), "Expected NO Unicode normalization -- D-05's explicit exclusion"

    def test_collision_key_does_not_collapse_leading_parent_traversal(self):
        """
        Not xfail -- passes today (a bare casefold() cannot collapse
        '..') and must keep passing after Task 2: posixpath.normpath()
        preserves a leading parent-traversal segment rather than
        resolving it away, which is what keeps T-47-11-01's containment
        argument (b) (monotonicity) true -- the key can never fold an
        escaping path into a non-escaping one.
        """
        from typsphinx.builder import TypstBuilder

        key = TypstBuilder._collision_key("../x.typ")
        assert key.startswith("../"), (
            f"Expected the collision key to preserve a leading "
            f"parent-traversal segment, got: {key!r}"
        )


class TestIsUsableTypstDocumentsEntryUnit:
    """
    BLD-03's load-bearing unit half: the entry-usability predicate itself,
    importing it INSIDE the test body so a missing symbol lands as an
    xfail rather than a module-level collection error.
    """

    def test_is_usable_typst_documents_entry_predicate(self):
        from typsphinx.builder import _is_usable_typst_documents_entry

        assert _is_usable_typst_documents_entry(()) is False
        assert _is_usable_typst_documents_entry(("index",)) is False
        assert _is_usable_typst_documents_entry((123, "t.typ")) is False

        assert _is_usable_typst_documents_entry(("index", "t.typ")) is True
        assert (
            _is_usable_typst_documents_entry(
                ("index", "t.typ", "Title", "Author", "extra")
            )
            is True
        )
