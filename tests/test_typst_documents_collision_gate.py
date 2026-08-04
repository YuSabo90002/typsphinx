"""
CR-01: real-``sphinx-build`` subprocess gate proving that a ``typst_documents``
target name (derived or explicit) that collides with a real docname's own
output path, or with the reserved ``_template.typ`` infrastructure file, no
longer silently destroys a document or hard-fails the PDF compile.

44-VERIFICATION.md scored this gap FAILED: the CONF-08 derivation makes a
pre-existing collision mechanism reachable with ZERO configuration -- an
ordinary project named after its first chapter (``project = "Chapter 1"``
alongside ``chapter1.rst``) silently corrupts the ``-b typst`` output (exit 0,
no warning) and hard-fails ``-b typstpdf`` with ``TypstError: cyclic import``.

Every test in this module is a must-SUCCEED gate, matching the
``test_default_typst_documents_gate.py`` pattern: ``returncode == 0`` is
asserted, never a failure.
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

COLLISION_WARNING_SUBSTRING = "collides with an existing document"


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


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the collision-gate tests",
)
class TestTypstDocumentsCollisionGate:
    """CR-01: a typst_documents target name colliding with a real docname or
    the reserved _template.typ falls back to the docname with a WARNING,
    on both the derived-default and explicit typst_documents paths."""

    def test_derived_default_docname_collision_keeps_both_documents(self, tmp_path):
        """
        Zero-configuration collision: `project = "Chapter 1"` derives to the
        target `chapter1.typ`, identical to the real `chapter1.rst`
        document's own output path. `-b typst` must exit 0, write BOTH
        `index.typ` and `chapter1.typ`, keep `chapter1.rst`'s own body
        intact, and warn about the collision.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            DERIVED_DOCNAME_COLLISION_FIXTURE_DIR, build_dir, "typst"
        )

        assert result.returncode == 0, (
            f"Expected a successful build despite the docname collision:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        index_typ = build_dir / "index.typ"
        chapter1_typ = build_dir / "chapter1.typ"
        assert index_typ.exists(), (
            f"Expected index.typ (the degraded master fallback) on disk:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert chapter1_typ.exists(), (
            f"Expected chapter1.typ (the real chapter document) on disk:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        chapter1_content = chapter1_typ.read_text(encoding="utf-8")
        assert chapter1_content.count("UNIQUE-CHAPTER-MARKER-XYZ") == 1, (
            f"Expected chapter1.rst's own body marker exactly once in "
            f"chapter1.typ, but the document was overwritten:\n"
            f"{chapter1_content}"
        )

        index_content = index_typ.read_text(encoding="utf-8")
        assert "_template.typ" in index_content, (
            f"Expected the shared-template import in the degraded master "
            f"index.typ:\n{index_content}"
        )

        combined_output = result.stdout + result.stderr
        assert COLLISION_WARNING_SUBSTRING in combined_output, (
            f"Expected a collision WARNING naming the docname clash:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_derived_default_docname_collision_produces_pdf(self, tmp_path):
        """
        The `-b typstpdf` counterpart: the same zero-configuration collision
        must exit 0 and produce a real `index.pdf`, not hard-fail with
        `TypstError: cyclic import`.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            DERIVED_DOCNAME_COLLISION_FIXTURE_DIR, build_dir, "typstpdf"
        )

        assert result.returncode == 0, (
            f"Expected a successful PDF build despite the docname collision:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        combined_output = result.stdout + result.stderr
        assert "cyclic import" not in combined_output, (
            f"Expected no cyclic-import compile fatal:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        pdf_file = build_dir / "index.pdf"
        assert pdf_file.exists(), (
            f"Expected index.pdf (the degraded master's compiled output):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert pdf_file.read_bytes()[:4] == b"%PDF", (
            f"Expected index.pdf to start with the %PDF magic bytes:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        chapter1_typ = build_dir / "chapter1.typ"
        assert chapter1_typ.exists(), (
            f"Expected chapter1.typ (the real chapter document) on disk:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        chapter1_content = chapter1_typ.read_text(encoding="utf-8")
        assert "UNIQUE-CHAPTER-MARKER-XYZ" in chapter1_content, (
            f"Expected chapter1.rst's own body marker to survive:\n"
            f"{chapter1_content}"
        )

        assert COLLISION_WARNING_SUBSTRING in combined_output, (
            f"Expected a collision WARNING naming the docname clash:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_derived_default_template_collision_preserves_shared_template(
        self, tmp_path
    ):
        """
        Zero-configuration RESERVED-TEMPLATE clobber: `project = "_Template"`
        derives to the target `_template.typ`, identical to the reserved
        shared-template basename `_write_template_file()` writes at the
        outdir root. `-b typst` must exit 0, keep `_template.typ` defining
        `#let project` (every master's import target), write `index.typ`
        (the degraded fallback), and warn about the collision.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            DERIVED_TEMPLATE_COLLISION_FIXTURE_DIR, build_dir, "typst"
        )

        assert result.returncode == 0, (
            f"Expected a successful build despite the template collision:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        template_typ = build_dir / "_template.typ"
        assert template_typ.exists(), (
            f"Expected the shared _template.typ on disk:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        template_content = template_typ.read_text(encoding="utf-8")
        assert "#let project" in template_content, (
            f"Expected _template.typ to still define #let project -- the "
            f"exact string CR-01's clobber destroyed:\n{template_content}"
        )

        index_typ = build_dir / "index.typ"
        assert index_typ.exists(), (
            f"Expected index.typ (the degraded master fallback) on disk:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        combined_output = result.stdout + result.stderr
        assert COLLISION_WARNING_SUBSTRING in combined_output, (
            f"Expected a collision WARNING naming the template clash:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_explicit_target_docname_collision_keeps_both_documents(self, tmp_path):
        """
        Explicit-path docname collision: `typst_documents = [("index",
        "chapter1.typ", ...)]` names an existing docname's own output path
        as the master's target. `-b typst` must exit 0, write BOTH
        `index.typ` and `chapter1.typ`, keep `chapter1.rst`'s own body
        intact, and warn about the collision.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            EXPLICIT_DOCNAME_COLLISION_FIXTURE_DIR, build_dir, "typst"
        )

        assert result.returncode == 0, (
            f"Expected a successful build despite the explicit docname "
            f"collision:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

        index_typ = build_dir / "index.typ"
        chapter1_typ = build_dir / "chapter1.typ"
        assert index_typ.exists(), (
            f"Expected index.typ (the degraded master fallback) on disk:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert chapter1_typ.exists(), (
            f"Expected chapter1.typ (the real chapter document) on disk:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        chapter1_content = chapter1_typ.read_text(encoding="utf-8")
        assert "EXPLICIT-CHAPTER-BODY" in chapter1_content, (
            f"Expected chapter1.rst's own body marker to survive:\n"
            f"{chapter1_content}"
        )

        combined_output = result.stdout + result.stderr
        assert COLLISION_WARNING_SUBSTRING in combined_output, (
            f"Expected a collision WARNING naming the explicit docname "
            f"clash:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_explicit_target_template_collision_preserves_shared_template(
        self, tmp_path
    ):
        """
        Explicit-path reserved-template clobber: `typst_documents =
        [("index", "_template.typ", ...)]` names the reserved shared-
        template basename as the master's target. `-b typst` must exit 0,
        keep `_template.typ` defining `#let project`, write `index.typ`
        (the degraded fallback), and warn about the collision.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            EXPLICIT_TEMPLATE_COLLISION_FIXTURE_DIR, build_dir, "typst"
        )

        assert result.returncode == 0, (
            f"Expected a successful build despite the explicit template "
            f"collision:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

        template_typ = build_dir / "_template.typ"
        assert template_typ.exists(), (
            f"Expected the shared _template.typ on disk:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        template_content = template_typ.read_text(encoding="utf-8")
        assert "#let project" in template_content, (
            f"Expected _template.typ to still define #let project -- the "
            f"exact string CR-01's clobber destroyed:\n{template_content}"
        )

        index_typ = build_dir / "index.typ"
        assert index_typ.exists(), (
            f"Expected index.typ (the degraded master fallback) on disk:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        combined_output = result.stdout + result.stderr
        assert COLLISION_WARNING_SUBSTRING in combined_output, (
            f"Expected a collision WARNING naming the explicit template "
            f"clash:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
