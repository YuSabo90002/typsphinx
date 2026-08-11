"""
DOC-12: the published changelog page delegates to repo-root ``CHANGELOG.md``
(Phase 45 plan 45-01) and carries every release the delegation was meant to
surface (Phase 45 plan 45-02's D-03/D-04/D-05 content backfill).

``TestPublishedChangelogPageDelegates`` reads ``docs/source/changelog.rst``
as plain text -- no import, no build -- and is therefore the one class in
this module that always runs in CI, never skipped and never marked
``slow``.

``TestChangelogPageContentCoverage`` and ``TestChangelogIncludeCompilesToPdf``
both drive a real Sphinx build and are marked ``@pytest.mark.slow``. Both
skip honestly rather than failing spuriously when their build dependency is
unavailable: ``myst_parser`` lives in the ``docs`` extra only (D-01), so a
dev-only CI lane that installs just ``--extra dev`` skips both classes; the
PDF class additionally skips when ``typst`` (``typst-py``) is not
importable, matching this suite's standing ``TYPST_AVAILABLE`` pattern (see
``tests/test_default_typst_documents_gate.py``).
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import myst_parser  # noqa: F401

    MYST_PARSER_AVAILABLE = True
except ImportError:
    MYST_PARSER_AVAILABLE = False

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

REPO_ROOT = Path(__file__).resolve().parents[1]
CHANGELOG_RST_PATH = REPO_ROOT / "docs" / "source" / "changelog.rst"
FIXTURES_DIR = Path(__file__).parent / "fixtures"
CHANGELOG_INCLUDE_GATE_FIXTURE_DIR = FIXTURES_DIR / "changelog_include_gate"

# The 13 releases the published page was frozen without (0.4.4 through 0.7.1,
# inclusive) -- shared by both the HTML and PDF content-coverage assertions
# below so the two builders are held to the identical bar.
RELEASE_VERSIONS = (
    "0.4.1",
    "0.4.2",
    "0.4.3",
    "0.4.4",
    "0.5.0",
    "0.6.0",
    "0.6.1",
    "0.6.2",
    "0.6.3",
    "0.6.4",
    "0.6.5",
    "0.7.0",
    "0.7.1",
)

# A per-release heading pattern and a "current release" marker, built from
# split fragments -- following tests/test_no_stale_github_io_links.py's
# precedent -- so this module cannot match itself if it is ever scanned for
# the pattern it guards against. The page's old hand-maintained release
# history used a literal "Version 0.4.0 (Current)" heading; splitting the
# marker keeps a future repo-wide grep for it clean and honest.
_STALE_HEADING_PATTERN = re.compile(r"^Version \d", re.M)
_CURRENT_MARKER_PREFIX = "(Cur"
_CURRENT_MARKER_SUFFIX = "rent)"
_CURRENT_MARKER = f"{_CURRENT_MARKER_PREFIX}{_CURRENT_MARKER_SUFFIX}"


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


class TestPublishedChangelogPageDelegates:
    """No import, no build -- always runs. Reads docs/source/changelog.rst
    as text and asserts the delegation shape (D-01) is intact and that no
    hand-maintained release history has crept back onto the page (D-06's
    "one-line-addition" property depends on this staying true)."""

    def test_page_delegates_to_changelog_md(self):
        text = CHANGELOG_RST_PATH.read_text(encoding="utf-8")
        assert ".. include:: ../../CHANGELOG.md" in text, (
            "docs/source/changelog.rst no longer includes the repo-root "
            "CHANGELOG.md -- the D-01 delegation mechanism is broken"
        )
        assert ":parser: myst_parser.sphinx_" in text, (
            "docs/source/changelog.rst's include directive lost its "
            ":parser: myst_parser.sphinx_ option"
        )

    def test_page_carries_no_hand_maintained_release_history(self):
        text = CHANGELOG_RST_PATH.read_text(encoding="utf-8")
        stale_headings = _STALE_HEADING_PATTERN.findall(text)
        assert not stale_headings, (
            f"docs/source/changelog.rst carries a hand-maintained "
            f"per-release heading again: {stale_headings!r} -- this is "
            f"the exact drift channel D-01 exists to close"
        )
        assert _CURRENT_MARKER not in text, (
            f"docs/source/changelog.rst carries a stale current-release "
            f"marker ({_CURRENT_MARKER!r}) -- a future release would need "
            f"a second edit here, violating the one-line-addition property"
        )


@pytest.fixture(scope="module")
def html_build(tmp_path_factory):
    """Module-scoped (not a class instance method -- pytest deprecates
    that shape, see PytestRemovedIn10Warning) so the one real ``-b html``
    build this module needs runs once, shared by every content-coverage
    assertion below."""
    build_dir = tmp_path_factory.mktemp("changelog_page_gate_html")
    result = _run_sphinx_build(REPO_ROOT / "docs" / "source", build_dir, "html")
    assert result.returncode == 0, (
        f"docs/source -b html build failed:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return build_dir, result


@pytest.mark.skipif(
    not MYST_PARSER_AVAILABLE,
    reason=(
        "myst-parser is required to build docs/source; it lives in the "
        "docs extra only (D-01), so a dev-only CI lane skips this class"
    ),
)
@pytest.mark.slow
class TestChangelogPageContentCoverage:
    """Drives a real ``-b html`` build of the whole ``docs/source`` tree
    and inspects the rendered ``changelog.html`` output."""

    def test_rendered_page_carries_every_release(self, html_build):
        build_dir, result = html_build
        changelog_html = (build_dir / "changelog.html").read_text(encoding="utf-8")
        missing = [v for v in RELEASE_VERSIONS if v not in changelog_html]
        assert not missing, (
            f"changelog.html is missing release version string(s): "
            f"{missing}\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_rendered_page_has_one_changelog_heading(self, html_build):
        build_dir, result = html_build
        changelog_html = (build_dir / "changelog.html").read_text(encoding="utf-8")
        headings = re.findall(r"<h[1-6][^>]*>Changelog<", changelog_html)
        assert len(headings) == 1, (
            f"expected exactly one heading element with the text "
            f"'Changelog', found {len(headings)}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_build_emits_no_changelog_warnings(self, html_build):
        _build_dir, result = html_build
        combined = result.stdout + result.stderr
        noisy = [
            line
            for line in combined.splitlines()
            if "WARNING" in line and "changelog" in line
        ]
        assert not noisy, (
            f"changelog-attributable WARNING line(s) in the docs/source "
            f"-b html build: {noisy}"
        )


@pytest.mark.skipif(
    not MYST_PARSER_AVAILABLE,
    reason=(
        "myst-parser is required to build the changelog include fixture; "
        "it lives in the docs extra only (D-01)"
    ),
)
@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required to compile the fixture to PDF",
)
@pytest.mark.slow
class TestChangelogIncludeCompilesToPdf:
    """Drives a real ``-b typstpdf`` build of the small
    ``changelog_include_gate`` fixture -- which includes the REAL
    repo-root ``CHANGELOG.md``, not a copy -- and asserts the compiled PDF
    carries every release."""

    def test_included_changelog_reaches_the_pdf(self, tmp_path):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(
            CHANGELOG_INCLUDE_GATE_FIXTURE_DIR, build_dir, "typstpdf"
        )
        assert result.returncode == 0, (
            f"changelog_include_gate fixture -b typstpdf build failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        # R4: the wrapper (target "master.typ", de-collided per
        # 47-EXPECTED-STRUCTURE.md) is what TypstPDFBuilder.finish()
        # compiles.
        pdf_path = build_dir / "master.pdf"
        assert pdf_path.exists(), (
            f"expected master.pdf to be produced:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        pdf_bytes = pdf_path.read_bytes()
        assert pdf_bytes[:4] == b"%PDF", (
            f"master.pdf does not start with the %PDF magic bytes:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        import pypdf

        reader = pypdf.PdfReader(str(pdf_path))
        extracted_text = "".join(page.extract_text() for page in reader.pages)
        # U+200B (zero-width space) is known to poison pypdf extraction in
        # this project -- a spurious zero-width space can land at an
        # unrelated glyph boundary and split a version string in two.
        extracted_text = extracted_text.replace("​", "")

        missing = [v for v in RELEASE_VERSIONS if v not in extracted_text]
        assert not missing, (
            f"compiled PDF is missing release version string(s): "
            f"{missing}\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
