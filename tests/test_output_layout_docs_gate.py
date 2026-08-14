"""
DOC-14, SC#3: real-``sphinx-build`` subprocess gate binding the published
two-layer output contract (``docs/source/user_guide/output_layout.rst``) to
the ``.typ`` file set a real build actually emits.

Phases 47 and 49 split every ``typst_documents`` entry's single emitted
``.typ`` file into two: a per-entry WRAPPER file (carrying the template
application and one ``#include()`` of its content file) and a per-docname
CONTENT file (unconditional, no template). The published documentation
never caught up with this shape -- this module is the machine-checked half
of DOC-14's fix.

``TestOutputLayoutBuildFileSets`` runs real ``-b typst`` builds of the
fixtures under ``tests/fixtures/output_layout_*_gate/`` and asserts the
exact emitted ``.typ`` file set on disk.

``TestPublishedOutputLayoutTextMatchesBuild`` reads
``docs/source/user_guide/output_layout.rst`` from disk and asserts the
published prose names those same filenames.

This module deliberately carries NO ``typst-py`` import guard (D-12). The
precedent module's (``tests/test_quickstart_docs_gate.py``) skip check
tests whether the ``typst`` package can be IMPORTED, not whether it can
actually COMPILE a document -- measured 2026-08-14, that package import
succeeds in this sandbox even though a real compile call fails with
``FileNotFoundError``. Inheriting that guard here would therefore RUN (not
skip) and then fail at the PDF-compiling subprocess step for an unrelated
reason. This module sidesteps the whole skip/import-vs-compile distinction
by building markup only (no PDF compilation), which needs no native Typst
binary at all -- only markup generation.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = Path(__file__).parent / "fixtures"
BARE_TARGET_FIXTURE_DIR = FIXTURES_DIR / "output_layout_bare_target_gate"
OUTPUT_LAYOUT_RST_PATH = (
    REPO_ROOT / "docs" / "source" / "user_guide" / "output_layout.rst"
)


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


class TestOutputLayoutBuildFileSets:
    """DOC-14, SC#3: real ``-b typst`` builds of the worked-example
    fixtures, asserting the exact emitted ``.typ`` file set."""

    def test_bare_target_emits_wrapper_and_content(self, tmp_path):
        """
        A real ``-b typst`` build of the bare-target fixture
        (``typst_documents = [("index", "manual", ...)]``) exits 0 and
        writes ``manual.typ`` (the wrapper, at the outdir root),
        ``index.typ`` (the content file, unconditional), and
        ``_template.typ`` (shared infrastructure). ``index.typ`` carries no
        template application; ``manual.typ`` does -- the measured
        wrapper/content discriminator (51-RESEARCH.md Part C build 5).
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(BARE_TARGET_FIXTURE_DIR, build_dir, "typst")

        assert result.returncode == 0, (
            f"Expected a successful build of the bare-target fixture:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        wrapper_typ = build_dir / "manual.typ"
        content_typ = build_dir / "index.typ"
        template_typ = build_dir / "_template.typ"

        assert wrapper_typ.exists(), (
            f"Expected the wrapper file manual.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert content_typ.exists(), (
            f"Expected the content file index.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert template_typ.exists(), (
            f"Expected the shared template file _template.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        assert "#show: project.with(" in wrapper_typ.read_text(
            encoding="utf-8"
        ), "Expected the wrapper file manual.typ to carry the template application."
        assert "#show: project.with(" not in content_typ.read_text(
            encoding="utf-8"
        ), "Expected NO template application in the content file index.typ."


class TestPublishedOutputLayoutTextMatchesBuild:
    """
    The assertion that binds the published prose to the measured build.

    No skip, no slow marker, no typst-py dependency, no PDF-compiling
    build -- this class must run in every CI lane and fail whenever the
    docs and a real ``-b typst`` build diverge again.
    """

    def test_page_names_the_bare_target_file_set(self):
        """docs/source/user_guide/output_layout.rst names both files the
        bare-target fixture build actually produces."""
        text = OUTPUT_LAYOUT_RST_PATH.read_text(encoding="utf-8")
        assert "manual.typ" in text, (
            "docs/source/user_guide/output_layout.rst does not contain the "
            "literal 'manual.typ' -- the wrapper file a real build of the "
            "bare-target worked example produces."
        )
        assert "index.typ" in text, (
            "docs/source/user_guide/output_layout.rst does not contain the "
            "literal 'index.typ' -- the content file a real build of the "
            "bare-target worked example produces."
        )
