"""
GATE-01 TPL-02/OUT-06 real-compile regression gate (Phase 54): proves that
(a) each ``typst_documents`` entry actually selects its OWN template
through the ``typst_document_templates`` registry (TPL-02), and (b) two
wrappers sharing the SAME registry key at two DIFFERENT nesting depths
emit the IDENTICAL root-absolute import string, because OUT-06's
root-absolute path has no depth dependence (unlike the pre-Phase-54
depth-counted ``"../"`` relative path).

Scaffolding is modelled on ``tests/test_typst_lang_gate.py``'s
``_run_sphinx_build()`` / ``TYPST_AVAILABLE`` idiom.

Made green by ``54-04`` (TPL-02/OUT-06): every used registry key's bundle
is copied wholesale to ``<outdir>/_template/<key>/`` and every wrapper
imports its own key by a root-absolute path
(``compute_template_import_path()``), so two wrappers sharing a key at
different nesting depths now emit the identical string. RED recorded in
``54-01-RED-EVIDENCE.md``.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "two_key_selection_gate"


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


def _extract_template_import_path(text: str) -> str:
    """
    Return the quoted path argument of the ``#import "..."`` statement
    whose argument contains ``_template``, or an empty string if none is
    present.
    """
    match = re.search(r'#import\s+"([^"]*_template[^"]*)"', text)
    return match.group(1) if match else ""


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the TPL-02/OUT-06 real-compile gate",
)
# Made green for real by 54-04 (TPL-02/OUT-06) -- the marker 54-01
# recorded this module's RED under has been removed.
class TestTwoKeySelectionGate:
    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        # This fixture body performs no verification of its own -- every
        # test method below carries its own verification instead.
        build_dir = tmp_path_factory.mktemp("two_key_selection_gate_build")
        result = _run_sphinx_build(FIXTURE_DIR, build_dir, "typstpdf")

        master_typ = build_dir / "master.typ"
        guide_typ = build_dir / "manuals" / "guide.typ"
        memo_typ = build_dir / "memos" / "memo.typ"

        def _read(p: Path) -> str:
            return p.read_text(encoding="utf-8") if p.exists() else ""

        return {
            "result": result,
            "build_dir": build_dir,
            "master_pdf": build_dir / "master.pdf",
            "guide_pdf": build_dir / "manuals" / "guide.pdf",
            "memo_pdf": build_dir / "memos" / "memo.pdf",
            "master_text": _read(master_typ),
            "guide_text": _read(guide_typ),
            "memo_text": _read(memo_typ),
        }

    def test_build_succeeds(self, build):
        result = build["result"]
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_three_pdfs_produced(self, build):
        for name in ("master_pdf", "guide_pdf", "memo_pdf"):
            pdf_path = build[name]
            assert pdf_path.exists(), f"{name} was not produced at {pdf_path}"
            pdf_bytes = pdf_path.read_bytes()
            assert len(pdf_bytes) > 0, f"{name} is empty"
            assert pdf_bytes[:4] == b"%PDF", f"{name} is not a valid PDF"

    def test_both_report_wrappers_emit_an_identical_import_string(self, build):
        master_import = _extract_template_import_path(build["master_text"])
        guide_import = _extract_template_import_path(build["guide_text"])
        assert master_import == guide_import == "/_template/report/base.typ", (
            "the two 'report'-keyed wrappers do not emit an identical "
            f"root-absolute import string:\nmaster: {master_import!r}\n"
            f"guide: {guide_import!r}"
        )

    def test_memo_wrapper_imports_its_own_key(self, build):
        memo_import = _extract_template_import_path(build["memo_text"])
        assert (
            memo_import == "/_template/memo/base.typ"
        ), f"memo wrapper does not import its own key's bundle: {memo_import!r}"

    def test_both_bundles_are_published(self, build):
        build_dir = build["build_dir"]
        assert (build_dir / "_template" / "report" / "base.typ").exists(), (
            "the 'report' bundle was not published to "
            "<outdir>/_template/report/base.typ"
        )
        assert (build_dir / "_template" / "memo" / "base.typ").exists(), (
            "the 'memo' bundle was not published to " "<outdir>/_template/memo/base.typ"
        )

    def test_the_two_templates_produce_different_pdfs(self, build):
        """
        Manual companion check: 54-VALIDATION.md's Manual-Only
        Verifications table names "two visibly different templates"
        (TPL-02) as owner-verified -- a byte comparison cannot judge
        "visibly different" rendering (different fonts/margins), only that
        the bytes themselves differ, which is what this test asserts.
        """
        master_bytes = build["master_pdf"].read_bytes()
        memo_bytes = build["memo_pdf"].read_bytes()
        assert master_bytes != memo_bytes, (
            "the 'report'-templated and 'memo'-templated PDFs are " "byte-identical"
        )
