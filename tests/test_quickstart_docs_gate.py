"""
DOC-11: real-``sphinx-build`` subprocess gate binding the published Quick
Start's own steps (``README.md`` and ``docs/source/quickstart.rst``) to the
filename a real build of those exact steps actually produces.

Phase 44's CONF-08 changed what an unset ``typst_documents`` resolves to,
but the published docs still describe the pre-CONF-08 behaviour: the
README's Configuration Options bullet claims ``typst_documents`` is
required before any PDF can be produced, and ``quickstart.rst``'s
``Your First PDF`` step names ``build/pdf/index.pdf`` as the output path.
Both are now measurably false.

``TestQuickstartFirstPdfGate`` mirrors ``tests/test_default_typst_documents_
gate.py``'s must-SUCCEED pattern: a real ``-b typstpdf`` build of a fixture
that reproduces the Quick Start's own project/author/document values,
asserting the emitted files are named from ``make_filename_from_project``
rather than left at ``index``.

``TestPublishedQuickstartTextMatchesBuild`` is the assertion that binds that
measured behaviour to the published prose -- it never skips (no typst-py
dependency) and must fail loudly whenever the docs and the real build
diverge again.
"""

import subprocess
import sys
from pathlib import Path

import pytest
from sphinx.util.osutil import make_filename_from_project

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = Path(__file__).parent / "fixtures"
QUICKSTART_GATE_FIXTURE_DIR = FIXTURES_DIR / "quickstart_docs_gate"
README_PATH = REPO_ROOT / "README.md"
QUICKSTART_RST_PATH = REPO_ROOT / "docs" / "source" / "quickstart.rst"

# The fixture's own `project` string -- the exact value docs/source/
# quickstart.rst's Configuration Options block publishes -- run through the
# same helper typsphinx/builder.py's _default_typst_documents() calls, so
# this module cannot drift from the derivation it is asserting about.
_FIXTURE_PROJECT = "My Project"
_EXPECTED_STEM = make_filename_from_project(_FIXTURE_PROJECT)


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
    reason="typst-py is required for the quickstart docs gate",
)
class TestQuickstartFirstPdfGate:
    """DOC-11: a real build of the published Quick Start's own steps
    produces the filename the docs must name, not ``index.pdf``."""

    def test_quickstart_steps_produce_the_documented_pdf(self, tmp_path):
        """
        A real ``-b typstpdf`` build of the fixture mirroring the Quick
        Start's ``Your First PDF`` flow exits 0 and writes
        ``<stem>.typ`` / ``<stem>.pdf``, where ``<stem>`` is computed as
        ``make_filename_from_project("My Project")`` rather than hardcoded.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(QUICKSTART_GATE_FIXTURE_DIR, build_dir, "typstpdf")

        assert result.returncode == 0, (
            f"Expected a successful build of the Quick Start fixture:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        typ_file = build_dir / f"{_EXPECTED_STEM}.typ"
        assert typ_file.exists(), (
            f"Expected the derived target {_EXPECTED_STEM}.typ:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        pdf_file = build_dir / f"{_EXPECTED_STEM}.pdf"
        assert pdf_file.exists(), (
            f"Expected the derived target {_EXPECTED_STEM}.pdf:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert pdf_file.read_bytes()[:4] == b"%PDF", (
            f"Expected {_EXPECTED_STEM}.pdf to start with the %PDF magic "
            f"bytes:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_quickstart_steps_do_not_produce_index_pdf(self, tmp_path):
        """
        Neither ``index.typ`` nor ``index.pdf`` exists in the build
        directory -- the derived target renames the root document's output
        rather than leaving it at the pre-CONF-08 name.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(QUICKSTART_GATE_FIXTURE_DIR, build_dir, "typstpdf")

        assert result.returncode == 0, (
            f"Expected a successful build of the Quick Start fixture:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
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


def _read_readme_text() -> str:
    return README_PATH.read_text(encoding="utf-8")


def _extract_readme_quick_start_section(text: str) -> str:
    """
    Slice README.md's ``## Quick Start`` section out: from its own heading
    line up to (not including) the next ``## `` heading at the same level.

    A mention of ``typst_documents`` elsewhere in the README (e.g. the
    Configuration Options section further down) must not satisfy the
    Quick-Start-specific assertion, so this helper isolates the slice
    rather than searching the whole file.
    """
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == "## Quick Start":
            start = i
            break
    assert start is not None, "README.md has no '## Quick Start' heading"
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "\n".join(lines[start:end])


# The mandatory-setting clause CONF-08 made false, built from two
# concatenated fragments so this test module's own source text is never a
# match for a repo-wide grep of the phrase -- the same technique
# tests/test_no_stale_github_io_links.py uses for the retired host literal.
_MANDATORY_CLAUSE_PART1 = "required for"
_MANDATORY_CLAUSE_PART2 = "PDF output"
_MANDATORY_CLAUSE = f"{_MANDATORY_CLAUSE_PART1} {_MANDATORY_CLAUSE_PART2}"


class TestPublishedQuickstartTextMatchesBuild:
    """
    The assertion that binds the published prose to the measured build.

    No skip, no slow marker, no typst-py dependency -- this class must run
    in every CI lane and fail whenever the docs and the real build diverge.
    """

    def test_quickstart_names_the_measured_output_path(self):
        """docs/source/quickstart.rst names the path the fixture build in
        TestQuickstartFirstPdfGate actually produces."""
        expected_path = f"build/pdf/{_EXPECTED_STEM}.pdf"
        text = QUICKSTART_RST_PATH.read_text(encoding="utf-8")
        assert expected_path in text, (
            f"docs/source/quickstart.rst does not contain the literal "
            f"{expected_path!r} -- the output path a real build of its own "
            "steps produces."
        )

    def test_readme_quickstart_explains_typst_documents(self):
        """README.md's Quick Start section mentions typst_documents
        (ROADMAP SC#1)."""
        section = _extract_readme_quick_start_section(_read_readme_text())
        assert "typst_documents" in section, (
            "README.md's Quick Start section does not mention "
            "typst_documents -- ROADMAP SC#1 requires the Quick Start to "
            "name it."
        )

    def test_readme_no_longer_calls_typst_documents_mandatory(self):
        """README.md's Configuration Options bullet no longer claims
        typst_documents is mandatory for PDF output -- CONF-08 made that
        false."""
        text = _read_readme_text()
        assert _MANDATORY_CLAUSE not in text, (
            f"README.md still asserts typst_documents is "
            f"{_MANDATORY_CLAUSE!r} -- CONF-08 made this false; "
            "typst_documents is optional and derives a default when unset."
        )
