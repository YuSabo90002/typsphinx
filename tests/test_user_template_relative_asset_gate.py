"""
GATE-01 OUT-05 real-compile regression gate (Phase 54): proves a
USER-supplied template's own relative asset reference (``#image("logo.png",
...)``) survives the per-key bundle relocation this phase introduces.

ROADMAP constraint #7 measured that all three real templates already in
this repository (the bundled default ``typsphinx/templates/base.typ``,
``docs/source/_typst/custom_template.typ``, and
``tests/fixtures/typst_lang_gate/srcdir_shadow_lang/base.typ``) carry
font-family references only -- none of them proves a path-RELATIVE
reference survives relocation. SC#3 explicitly rejects the built-in
template as evidence for this gate, so this module's fixture
(``tests/fixtures/user_template_relative_asset_gate/``) is a genuinely new
real ``sphinx-build -b typstpdf`` -> ``typst.compile()`` proof, recorded
RED against the pre-relocation tree in ``54-01-RED-EVIDENCE.md``.

Scaffolding (subprocess-based ``sys.executable -m sphinx``,
``TYPST_AVAILABLE`` guard, class-scoped ``build`` fixture) is modelled on
``tests/test_typst_lang_gate.py``'s ``TestJapaneseSourceProof`` /
``TestGermanLinkageProof`` classes.

Made green by ``54-04`` (OUT-05): the per-key bundle relocation now copies
the user template's own directory wholesale to
``<outdir>/_template/<key>/``, so its same-directory ``logo.png`` sits
beside it, and the wrapper imports the template by its root-absolute
``/_template/<key>/<file>.typ`` path. RED recorded in
``54-01-RED-EVIDENCE.md``.
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

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "user_template_relative_asset_gate"


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard -- copied near-verbatim from
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


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the OUT-05 real-compile gate",
)
# Made green for real by 54-04 (OUT-05) -- the marker 54-01 recorded
# this module's RED under has been removed.
class TestUserTemplateRelativeAssetGate:
    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        # This fixture body performs no verification of its own -- every
        # test method below carries its own verification instead.
        build_dir = tmp_path_factory.mktemp("user_template_relative_asset_gate_build")
        result = _run_sphinx_build(FIXTURE_DIR, build_dir, "typstpdf")
        wrapper_path = build_dir / "master.typ"
        wrapper_text = (
            wrapper_path.read_text(encoding="utf-8") if wrapper_path.exists() else ""
        )
        pdf_path = build_dir / "master.pdf"
        return {
            "result": result,
            "build_dir": build_dir,
            "wrapper_path": wrapper_path,
            "wrapper_text": wrapper_text,
            "pdf_path": pdf_path,
        }

    def test_build_succeeds(self, build):
        result = build["result"]
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_pdf_is_valid(self, build):
        pdf_path = build["pdf_path"]
        result = build["result"]
        assert pdf_path.exists(), (
            f"PDF was not produced at {pdf_path}:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        pdf_bytes = pdf_path.read_bytes()
        assert len(pdf_bytes) > 0, "PDF is empty"
        assert pdf_bytes[:4] == b"%PDF", f"Not a valid PDF: {pdf_bytes[:16]!r}"

    def test_asset_reached_the_bundle_destination(self, build):
        build_dir = build["build_dir"]
        assert (build_dir / "_template" / "typst" / "logo.png").exists(), (
            "logo.png did not reach the bundle destination "
            "<outdir>/_template/typst/logo.png"
        )
        assert (build_dir / "_template" / "typst" / "branded.typ").exists(), (
            "branded.typ did not reach the bundle destination "
            "<outdir>/_template/typst/branded.typ"
        )

    def test_wrapper_imports_the_bundled_template(self, build):
        wrapper_text = build["wrapper_text"]
        assert "/_template/typst/branded.typ" in wrapper_text, (
            "wrapper does not import the bundled template at the expected "
            f"root-absolute path:\n{wrapper_text}"
        )
