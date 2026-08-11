"""
Fast offline regression gate for the typstpdf target-name bug (Issue #117).

GATE-01 render gate for PDF-01:

    typst_documents = [("index", "output.typ", ...)] must emit ``output.typ``
    AND ``output.pdf`` -- the CONFIGURED TARGET name -- not ``index.typ`` /
    ``index.pdf``, the source docname.

Before Plan 01's fix, every output-path site derived its filename from the
source docname (``docname + self.out_suffix``), silently ignoring the target
name element (tuple index ``[1]``) of a ``typst_documents`` entry. This meant
a user's explicit ``("index", "output.typ", ...)`` request was never honored:
the builder still wrote ``index.typ`` / ``index.pdf``.

Drives the full ``-b typstpdf`` path -- NOT ``-b typst`` -- on purpose: the
``.pdf`` half of the contract only materializes inside
``TypstPDFBuilder.finish()``'s ``typst.compile()`` call, so a ``-b typst``
build would never prove the PDF-naming half of Issue #117.

This gate is bidirectional by design: it asserts BOTH that the target-named
artifacts (``output.typ`` / ``output.pdf``) are PRESENT AND that the
docname-named ``.pdf`` (``index.pdf``) is ABSENT.

**Phase 47 amendment (COMP-01, ``47-EXPECTED-STRUCTURE.md``): the D-08
"clean-break" ``.typ`` half is REVERSED, not merely relaxed.** Pre-Phase-47,
a target name differing from the docname made the docname-named ``.typ``
disappear entirely (one file per docname, written at its resolved stem).
Post-split, ``index.typ`` (the docname-derived CONTENT file) is
UNCONDITIONAL (COMP-01) -- it always exists alongside ``output.typ`` (the
target-derived WRAPPER), carrying the translated body but no template
application. This is not a regression of Issue #117's fix: ``output.typ``/
``output.pdf`` still are, and remain, the target-named artifacts a user's
``typst_documents`` entry controls; ``index.pdf`` remains absent because
only wrappers are ever compiled to PDF (COMP-02/R4) -- the "docname-named
PDF must not silently reappear" half of the original gate is unaffected by
the split. Only the docname-named ``.typ``'s absence assertion, which
predates the two-layer model entirely, no longer holds.
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


@pytest.fixture
def target_name_render_gate_source_dir():
    """Return the path to the tests/roots/test-basic fixture."""
    return Path(__file__).parent / "roots" / "test-basic"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run a ``-b typstpdf`` Sphinx build as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never a PATH-resolved build
    console-script) so the exact interpreter/venv running this test is
    reused, sidestepping the documented NixOS-sandbox PATH-shadowing hazard.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typstpdf",
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the target-name render gate",
)
class TestTargetNameRenderGate:
    """
    Real-compile regression gate proving that a ``typst_documents`` target
    name (tuple element ``[1]``) governs the emitted ``.typ`` AND ``.pdf``
    filenames, not the source docname.

    Requirements: PDF-01 (Phase 22 -- Issue #117 typstpdf target-name fix).
    """

    def test_typstpdf_emits_target_named_artifacts_and_not_docname_named(
        self, target_name_render_gate_source_dir, temp_build_dir
    ):
        """
        Build ``tests/roots/test-basic`` (``typst_documents =
        [("index", "output.typ", ...)]``) through ``-b typstpdf`` and confirm
        the target-named artifacts are emitted while the docname-named
        artifacts are not.
        """
        # (1) BUILD:
        result = _run_sphinx_build_typstpdf(
            target_name_render_gate_source_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"Sphinx -b typstpdf build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # A fatal inside TypstPDFBuilder.finish() is logged (not raised) as an
        # ERROR, so guard against the exact signatures explicitly rather than
        # trusting returncode alone.
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )
        assert "Master document not found" not in result.stderr, (
            "TypstPDFBuilder.finish()'s read-back path and write_doc's write "
            "path disagreed on the resolved output stem -- the exact "
            "regression this phase's shared-helper factoring exists to "
            f"prevent:\nstderr: {result.stderr}"
        )

        # (2) TARGET-NAMED .typ PRESENT:
        output_typ = temp_build_dir / "output.typ"
        assert output_typ.exists(), (
            "tests/roots/test-basic/conf.py declares typst_documents = "
            "[('index', 'output.typ', ...)], so the build must emit "
            f"output.typ; it did not. Build dir contents: "
            f"{list(temp_build_dir.iterdir()) if temp_build_dir.exists() else '(missing)'}"
        )
        assert output_typ.stat().st_size > 0, "output.typ is empty"

        # (3) TARGET-NAMED .pdf PRESENT AND VALID:
        output_pdf = temp_build_dir / "output.pdf"
        assert output_pdf.exists(), (
            "tests/roots/test-basic/conf.py declares typst_documents = "
            "[('index', 'output.typ', ...)], so the compiled PDF must be "
            f"named output.pdf; it was not produced:\nstderr: {result.stderr}"
        )
        assert output_pdf.stat().st_size > 0, "output.pdf is empty"
        with open(output_pdf, "rb") as f:
            assert f.read(4) == b"%PDF", "Generated file is not a valid PDF"

        # (4) COMP-01 (Phase 47): index.typ is now the docname-derived
        # CONTENT file -- unconditional, alongside output.typ, carrying no
        # template application. index.pdf, however, must remain absent --
        # only wrappers are ever compiled to PDF (COMP-02/R4), so a target
        # name differing from the docname must never let a docname-named
        # PDF silently reappear.
        content_typ = temp_build_dir / "index.typ"
        assert content_typ.exists(), (
            "Expected the docname-derived content file index.typ to exist "
            "unconditionally alongside the target-derived wrapper "
            "output.typ (COMP-01)."
        )
        assert "#show: project.with(" not in content_typ.read_text(
            encoding="utf-8"
        ), (
            "Expected NO template application in the content file -- that "
            "belongs exclusively to the wrapper (output.typ)."
        )
        assert not (temp_build_dir / "index.pdf").exists(), (
            "index.pdf was emitted alongside output.pdf -- only the "
            "WRAPPER (output.typ/output.pdf) may ever be compiled "
            "(COMP-02/R4); a docname-named PDF must never silently "
            "reappear when a target name differs from the docname."
        )


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the OUT-01 directory-bearing-target case",
)
class TestOut01DirectoryBearingTarget:
    """
    OUT-01: a ``typst_documents`` target WITH a directory component
    (``"manuals/guide.typ"``) writes the WRAPPER at that exact path under
    ``outdir`` -- no truncation to a basename, no forced relocation into
    the docname's own directory (the reversed Phase 44 D-05/D-06/D-07
    behavior) -- while the CONTENT stays at its docname-derived path,
    completely independent of the target's own directory structure
    (COMP-01/OUT-03).

    Uses an inline ``tmp_path`` project (never ``tests/roots/test-basic``,
    which this module's sibling test above already exercises and which
    Phase 47 plan 47-08's own Task 3 migrates independently) so this
    addition cannot collide with another plan's fixture scope.
    """

    def test_directory_bearing_target_writes_wrapper_at_that_path(self, tmp_path):
        """
        ``typst_documents = [("index", "manuals/guide.typ", ...)]``: the
        expected paths below are DERIVED FROM THIS CONFIG, not observed
        from a prior build -- ``manuals/guide.typ``/``manuals/guide.pdf``
        for the wrapper (the target, taken as a literal outdir-relative
        path per OUT-01) and ``index.typ`` for the content (the docname,
        unconditionally, per COMP-01) -- and then checked against a real
        ``-b typstpdf`` build.
        """
        srcdir = tmp_path / "source"
        srcdir.mkdir()
        (srcdir / "index.rst").write_text(
            "OUT-01 Directory Target\n========================\n\n"
            "OUT01DIRTARGETBODY\n"
        )
        (srcdir / "conf.py").write_text(
            "project = 'OUT-01 Directory Target'\n"
            "author = 'Test Author'\n"
            "release = '1.0'\n"
            "extensions = ['typsphinx']\n"
            "typst_documents = [('index', 'manuals/guide.typ', project, author)]\n"
        )

        outdir = tmp_path / "build"
        result = _run_sphinx_build_typstpdf(srcdir, outdir)
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        # Wrapper: exactly where the target says, under outdir -- no
        # truncation to "guide.typ" at the outdir root, no relocation into
        # the docname's own directory (both reversed by OUT-01).
        wrapper_typ = outdir / "manuals" / "guide.typ"
        assert wrapper_typ.exists(), (
            f"Expected the wrapper at manuals/guide.typ (the literal "
            f"target path):\nstdout: {result.stdout}\nstderr: "
            f"{result.stderr}"
        )
        wrapper_text = wrapper_typ.read_text(encoding="utf-8")
        assert '#include("../index.typ")' in wrapper_text, (
            f"Expected the wrapper's #include() to climb one level back "
            f"to the outdir-root content file:\n{wrapper_text}"
        )
        assert '#import "../_template.typ"' in wrapper_text, (
            f"Expected the wrapper's template import to climb one level "
            f"back to the outdir-root _template.typ:\n{wrapper_text}"
        )
        wrapper_pdf = outdir / "manuals" / "guide.pdf"
        assert wrapper_pdf.exists(), (
            f"Expected the compiled PDF at manuals/guide.pdf:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert wrapper_pdf.read_bytes()[:4] == b"%PDF", (
            "Expected manuals/guide.pdf to start with the %PDF magic bytes"
        )

        # Content: still at the docname-derived path, unaffected by the
        # target's own directory (COMP-01/OUT-03).
        content_typ = outdir / "index.typ"
        assert content_typ.exists(), (
            f"Expected the docname-derived content file index.typ, "
            f"independent of the target's own directory:\nstdout: "
            f"{result.stdout}\nstderr: {result.stderr}"
        )
        assert "OUT01DIRTARGETBODY" in content_typ.read_text(encoding="utf-8")

        # No un-relocated/truncated forms of the old Phase 44 behavior.
        assert not (outdir / "guide.typ").exists(), (
            "The target must NOT be truncated to its basename at the "
            "outdir root (the reversed OUT-01 guard)."
        )
        assert not (outdir / "index" / "guide.typ").exists(), (
            "The target must NOT be force-relocated into the docname's "
            "own directory (the reversed Phase 44 D-05/D-06/D-07 "
            "behavior)."
        )
