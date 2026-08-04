"""
CONF-08: real-``sphinx-build`` subprocess gate proving that an unset
``typst_documents`` now resolves to a Sphinx-native derived default (Phase
44, D-01/D-02/D-04), and that an explicitly-set ``typst_documents`` still
wins (SC#2).

Unlike ``test_missing_and_malformed_master_gate.py`` (this suite's must-FAIL
gate), both test methods here are must-SUCCEED gates -- matching the
majority-pattern ``*_render_gate.py`` modules -- asserting
``returncode == 0``.
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
DEFAULT_GATE_FIXTURE_DIR = FIXTURES_DIR / "default_typst_documents_gate"
EXPLICIT_WINS_GATE_FIXTURE_DIR = FIXTURES_DIR / "explicit_typst_documents_wins_gate"


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
    reason="typst-py is required for the default-derivation gate",
)
class TestDefaultTypstDocumentsDerivationGate:
    """CONF-08: unset typst_documents still produces a PDF, named via
    make_filename_from_project; an explicit setting always wins (SC#2)."""

    def test_unset_typst_documents_produces_pdf(self, tmp_path):
        """
        With typst_documents absent from conf.py, sphinx-build -b typstpdf
        exits 0 and writes quickstartdefaultgate.typ / .pdf -- the target
        name derived from make_filename_from_project(config.project) --
        instead of the old index.typ/no-PDF-at-all behaviour.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(DEFAULT_GATE_FIXTURE_DIR, build_dir, "typstpdf")

        assert result.returncode == 0, (
            f"Expected a successful build with typst_documents unset:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        assert (build_dir / "quickstartdefaultgate.typ").exists(), (
            f"Expected the derived target quickstartdefaultgate.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        pdf_file = build_dir / "quickstartdefaultgate.pdf"
        assert pdf_file.exists(), (
            f"Expected the derived target quickstartdefaultgate.pdf:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert pdf_file.read_bytes()[:4] == b"%PDF", (
            f"Expected quickstartdefaultgate.pdf to start with the %PDF "
            f"magic bytes:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

        assert not (build_dir / "index.typ").exists(), (
            f"index.typ should not exist -- the root document's output is "
            f"renamed by the derived target name:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert not (build_dir / "index.pdf").exists(), (
            f"index.pdf should not exist -- the root document's output is "
            f"renamed by the derived target name:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        typ_content = (build_dir / "quickstartdefaultgate.typ").read_text(
            encoding="utf-8"
        )
        assert "_template.typ" in typ_content, (
            f"Expected the shared-template import a master document gets -- "
            f"root_doc must be treated as a master now that the derived "
            f"entry makes it one:\n{typ_content}"
        )
        assert "QSDEFAULTBODY" in typ_content, (
            f"Expected the fixture's sentinel body text in the emitted "
            f".typ:\n{typ_content}"
        )

        assert "Nothing to compile" not in result.stderr, (
            f"Expected no typsphinx nothing-to-compile warning:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
