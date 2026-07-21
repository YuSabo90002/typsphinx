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
docname-named artifacts (``index.typ`` / ``index.pdf``) are ABSENT. Both
halves are required -- without the absence assertions, this gate would also
pass against a naive fix that emits BOTH the target-named and docname-named
pairs (a compatibility shim), which violates the D-08 clean-break
requirement: a target name that differs from the docname must fully replace
the docname-derived filename, not merely supplement it.
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

        # (4) DOCNAME-NAMED ARTIFACTS ABSENT (D-08 clean-break requirement):
        assert not (temp_build_dir / "index.typ").exists(), (
            "index.typ was emitted alongside output.typ -- the builder must "
            "stop emitting the docname-named pair when a target name differs "
            "from the docname, not emit both. A failure here alongside a "
            "passing concern (2)/(3) means a compatibility shim was "
            "introduced instead of the required clean-break rename."
        )
        assert not (temp_build_dir / "index.pdf").exists(), (
            "index.pdf was emitted alongside output.pdf -- the builder must "
            "stop emitting the docname-named pair when a target name differs "
            "from the docname, not emit both. A failure here alongside a "
            "passing concern (2)/(3) means a compatibility shim was "
            "introduced instead of the required clean-break rename."
        )
