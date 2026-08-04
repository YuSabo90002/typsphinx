"""
D-03: real-``sphinx-build`` subprocess gate proving the corrected opt-out
wording for an explicit ``typst_documents = []`` (Phase 44, plan 44-02),
and pinning the resolved answer to Claude's Discretion (d): ``-b typst``
alone stays silent on the same explicit empty list.

Both test methods here are must-SUCCEED gates -- an explicit empty list is
a deliberate, supported opt-out, not an error condition. Since CONF-08
(plan 44-01) landed a derived default for an unset ``typst_documents``,
this fixture's ``typst_documents = []`` is the ONLY way left to reach
``TypstPDFBuilder.finish()``'s early-return branch.
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
GATE_FIXTURE_DIR = FIXTURES_DIR / "empty_typst_documents_optout_gate"


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
    reason="typst-py is required for the empty-typst_documents opt-out gate",
)
class TestEmptyTypstDocumentsOptoutGate:
    """D-03: the corrected opt-out wording, and Discretion (d)'s resolved
    answer that ``-b typst`` alone stays silent on the same explicit empty
    list."""

    def test_typstpdf_optout_wording(self, tmp_path):
        """
        The typstpdf side: an explicit empty typst_documents still opts
        out (exit 0, zero PDFs), and the WARNING now says the setting is
        present and empty, and how to restore the derived default.
        """
        build_dir = tmp_path / "build_typstpdf"
        result = _run_sphinx_build(GATE_FIXTURE_DIR, build_dir, "typstpdf")

        assert result.returncode == 0, (
            f"Expected a successful (opt-out) build with an explicit "
            f"empty typst_documents:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "explicitly set to an empty list" in result.stderr, (
            f"Expected the corrected D-03 wording naming the setting as "
            f"present and empty:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "Remove the setting entirely" in result.stderr, (
            f"Expected the D-03 remedy wording pointing at the derived "
            f"default:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

        assert (build_dir / "index.typ").exists(), (
            f"Expected index.typ (an explicit opt-out still writes .typ "
            f"for -b typstpdf's write phase, only the PDF compile is "
            f"skipped):\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "OPTOUTBODY" in (build_dir / "index.typ").read_text(
            encoding="utf-8"
        ), "Expected the fixture's sentinel body text in index.typ"

        pdf_files = list(build_dir.rglob("*.pdf"))
        assert pdf_files == [], (
            f"Expected zero PDFs anywhere in the build directory for an "
            f"explicit opt-out, found: {pdf_files}\nstdout: "
            f"{result.stdout}\nstderr: {result.stderr}"
        )

        assert not (build_dir / "emptyoptoutgate.typ").exists(), (
            f"The derived default (which would have produced "
            f"emptyoptoutgate.typ) must NOT be consulted when the user "
            f"explicitly opted out:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_typst_side_stays_silent_discretion_d(self, tmp_path):
        """
        Discretion (d), resolved NO: ``-b typst`` alone does not warn on
        the same explicit empty typst_documents. Three measured grounds
        (44-02-PLAN.md <discretion_resolution>), one sentence each: (1)
        -b typst still writes a .typ for every document regardless of
        typst_documents, so there is no missing output to warn about; (2)
        adding the warning would be a second undiscussed behaviour change
        riding along with CONF-08's rename in a patch release; (3) the
        LaTeX warning precedent does not transfer, because LaTeX's empty
        latex_documents means literally nothing is written, which is not
        true here.
        """
        build_dir = tmp_path / "build_typst"
        result = _run_sphinx_build(GATE_FIXTURE_DIR, build_dir, "typst")

        assert result.returncode == 0, (
            f"Expected a successful -b typst build with an explicit empty "
            f"typst_documents:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert (build_dir / "index.typ").exists(), (
            f"Expected index.typ to be written regardless of "
            f"typst_documents:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "OPTOUTBODY" in (build_dir / "index.typ").read_text(
            encoding="utf-8"
        ), "Expected the fixture's sentinel body text in index.typ"

        assert "explicitly set to an empty list" not in result.stderr, (
            f"Discretion (d): -b typst alone must stay silent on an "
            f"explicit empty typst_documents -- the opt-out message lives "
            f"only in TypstPDFBuilder.finish():\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
