"""
CONF-08: real-``sphinx-build`` subprocess gate proving that an unset
``typst_documents`` now resolves to a Sphinx-native derived default (Phase
44, D-01/D-02/D-04), and that an explicitly-set ``typst_documents`` still
wins (SC#2).

Unlike ``test_missing_and_malformed_master_gate.py`` (this suite's must-FAIL
gate), both test methods here are must-SUCCEED gates -- matching the
majority-pattern ``*_render_gate.py`` modules -- asserting
``returncode == 0``.

Phase 47 migration (R1/R2, ``47-EXPECTED-STRUCTURE.md``): the content/
wrapper split makes ``index.typ`` (the docname-derived CONTENT file)
unconditional (COMP-01) -- it now exists alongside the WRAPPER regardless
of what any ``typst_documents`` entry's target names, carrying the
translated body but no template application. The pre-split "``index.typ``
must NOT exist -- the root document's output is renamed" assertion is
therefore obsolete: it pinned a world where exactly one file existed per
docname, under its resolved stem. This module's assertions were re-derived
against the new shape -- ``index.typ`` (content) exists and carries the
sentinel body marker; the derived/explicit WRAPPER carries the template
application and an ``#include("index.typ")`` of that content file, not the
marker itself.
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

        # R1/COMP-01 (Phase 47): index.typ is now the docname-derived
        # CONTENT file -- unconditional, regardless of the derived
        # wrapper's target name. index.pdf, however, is never written for
        # a content file (COMP-02/R4: only wrappers compile to PDF).
        content_typ = build_dir / "index.typ"
        assert content_typ.exists(), (
            f"Expected the docname-derived content file index.typ to "
            f"exist unconditionally:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert not (build_dir / "index.pdf").exists(), (
            f"index.pdf should not exist -- only the wrapper "
            f"(quickstartdefaultgate.pdf) is ever compiled:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        content_text = content_typ.read_text(encoding="utf-8")
        assert "#show: project.with(" not in content_text, (
            f"Expected NO template application in the content file:\n" f"{content_text}"
        )
        assert "QSDEFAULTBODY" in content_text, (
            f"Expected the fixture's sentinel body text in the "
            f"docname-derived content file:\n{content_text}"
        )

        typ_content = (build_dir / "quickstartdefaultgate.typ").read_text(
            encoding="utf-8"
        )
        assert '#import "/_template/typst/base.typ"' in typ_content, (
            f"Expected the bundled-template import a wrapper carries -- "
            f"root_doc must be treated as a master now that the derived "
            f"entry makes it one:\n{typ_content}"
        )
        assert '#include("index.typ")' in typ_content, (
            f"Expected the wrapper to #include() its own entry's content "
            f"file:\n{typ_content}"
        )

        assert "Nothing to compile" not in result.stderr, (
            f"Expected no typsphinx nothing-to-compile warning:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_explicit_typst_documents_wins(self, tmp_path):
        """
        SC#2: an explicitly-set single-entry typst_documents naming target
        "manual.typ" produces exactly manual.typ and manual.pdf and nothing
        else -- the derived default (which would have named this project
        explicitwinsgate.typ) contributes no extra target and does not
        rename the explicit one.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            EXPLICIT_WINS_GATE_FIXTURE_DIR, build_dir, "typstpdf"
        )

        assert result.returncode == 0, (
            f"Expected a successful build with an explicit typst_documents:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        manual_typ = build_dir / "manual.typ"
        assert manual_typ.exists(), (
            f"Expected the explicit target manual.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        # R1/R2 (Phase 47): the sentinel body marker lives on the
        # docname-derived CONTENT file (index.typ); the wrapper
        # (manual.typ) carries the template application and an
        # #include("index.typ") of that content file, not the marker
        # itself.
        assert '#include("index.typ")' in manual_typ.read_text(encoding="utf-8"), (
            f"Expected the wrapper to #include() its own entry's content "
            f"file:\n{manual_typ.read_text(encoding='utf-8')}"
        )
        content_typ = build_dir / "index.typ"
        assert content_typ.exists(), (
            f"Expected the docname-derived content file index.typ to "
            f"exist unconditionally:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "EXPLICITWINSBODY" in content_typ.read_text(encoding="utf-8"), (
            f"Expected the fixture's sentinel body text in the "
            f"docname-derived content file index.typ:\n"
            f"{content_typ.read_text(encoding='utf-8')}"
        )
        manual_pdf = build_dir / "manual.pdf"
        assert manual_pdf.exists(), (
            f"Expected the explicit target manual.pdf:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert manual_pdf.read_bytes()[:4] == b"%PDF", (
            f"Expected manual.pdf to start with the %PDF magic bytes:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        # SC#2: nothing else WRAPPER-shaped. The derived default (which
        # would have named this project's target explicitwinsgate.typ/
        # .pdf) must not also appear alongside the explicit target -- the
        # explicit setting must be the ONLY typst_documents entry. R4/
        # COMP-02 (Phase 47): index.pdf must never appear either, since
        # only wrappers ever compile to PDF (index.typ, the content file,
        # is asserted present ABOVE -- it is no longer part of this "must
        # not exist" set, since content files are now unconditional).
        unexpected = [
            build_dir / "explicitwinsgate.typ",
            build_dir / "explicitwinsgate.pdf",
            build_dir / "index.pdf",
        ]
        still_present = [str(p) for p in unexpected if p.exists()]
        assert not still_present, (
            f"SC#2 violation: the explicit typst_documents setting must "
            f"produce exactly the wrapper it names and nothing else, but "
            f"found unexpected output(s): {still_present}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
