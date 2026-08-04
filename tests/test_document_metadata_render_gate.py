"""
Real-compile regression gate for CONF-09 (Phase 44.2, plan 01, SC#1, D-01).

The shipping bug: an explicit ``typst_documents`` entry's title (``[2]``)
and author (``[3]``) were read by nothing -- ``TypstWriter.translate()``
always built ``sphinx_metadata`` from ``config.project`` / ``config.author``
directly, so a master document's rendered title and author were always the
project-wide config values, never the entry's own values, even when an
entry explicitly specified different ones.

Fix: ``_resolve_entry_element()`` (``typsphinx/writer.py``) resolves the
FIRST ``typst_documents`` entry whose ``entry[0] == docname`` and returns
``entry[index]`` when it is a ``str`` (including ``""`` -- D-01), falling
back silently to ``config.project`` / ``config.author`` when the element is
absent, too-short, or ``None`` (D-02), and warning-then-falling-back when
the element is present but not a ``str`` (D-02). ``TypstWriter.translate()``
now calls this helper twice when building ``sphinx_metadata``, so the
entry's title/author reach every template route (D-03).

Verification is end-to-end (SC#1's own requirement): a real
``sphinx-build -b typstpdf`` compile, read back through
``pypdf.PdfReader(...).metadata`` -- never inferred from the emitted
``.typ`` alone.
"""

import io
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    from pypdf import PdfReader

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


@pytest.fixture
def entry_title_author_render_gate_dir():
    """Return the path to the entry_title_author_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "entry_title_author_render_gate"


@pytest.fixture
def entry_empty_metadata_render_gate_dir():
    """Return the path to the entry_empty_metadata_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "entry_empty_metadata_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typstpdf`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``)
    so the exact interpreter/venv running this test is reused, sidestepping
    the documented NixOS-sandbox PATH-shadowing hazard.
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


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are required for the entry title/author render gate",
)
class TestEntryTitleAuthorRenderGate:
    """
    Real-compile regression gate proving an explicit ``typst_documents``
    entry's title and author reach the compiled PDF's own metadata,
    including D-01's asymmetric empty-string case.

    Requirements: CONF-09, GATE-01.
    """

    def test_entry_title_and_author_reach_the_compiled_pdf(
        self, entry_title_author_render_gate_dir, temp_build_dir
    ):
        """
        SC#1: a real ``-b typstpdf`` build of a fixture whose entry title
        AND author both differ from ``config.project`` / ``config.author``
        produces a PDF whose ``/Title`` and ``/Author`` are the ENTRY's
        values, not the config's.
        """
        result = _run_sphinx_build_typstpdf(
            entry_title_author_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced:\n" f"stderr: {result.stderr}"
        )

        reader = PdfReader(io.BytesIO(pdf_output.read_bytes()))
        metadata = reader.metadata

        # Positive: the entry's own values reached the PDF.
        assert (
            metadata.title == "My Handbook"
        ), f"Expected the entry's title 'My Handbook', got {metadata.title!r}"
        assert (
            metadata.author == "Jane Doe"
        ), f"Expected the entry's author 'Jane Doe', got {metadata.author!r}"

        # Negative: the config-wide fallback values must NOT be what came
        # back -- guards against a fallback regression passing by
        # coincidence (e.g. both strings happening to compare equal).
        assert metadata.title != "Config Project Must Not Win", (
            "The config.project fallback value leaked into the PDF title -- "
            "the entry's own title was not consumed."
        )
        assert metadata.author != "Config Author Must Not Win", (
            "The config.author fallback value leaked into the PDF author -- "
            "the entry's own author was not consumed."
        )

    def test_empty_entry_elements_are_values_not_fallback_signals(
        self, entry_empty_metadata_render_gate_dir, temp_build_dir
    ):
        """
        D-01: an empty-string ``entry[2]``/``entry[3]`` is a VALUE, not a
        fallback signal. These two assertions are DELIBERATELY ASYMMETRIC
        (RESEARCH.md Pitfall 6, verified via a real typst.compile() round
        trip): Typst omits the PDF ``/Title`` key entirely when the title
        string is empty, while an empty ``authors:`` array still yields a
        PRESENT, empty ``/Author`` value.
        """
        result = _run_sphinx_build_typstpdf(
            entry_empty_metadata_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced:\n" f"stderr: {result.stderr}"
        )

        reader = PdfReader(io.BytesIO(pdf_output.read_bytes()))
        metadata = reader.metadata

        # Title: an empty title string means Typst never emits a /Title
        # key at all -- pypdf reads this back as None, not "".
        assert metadata.title is None, (
            "Expected an empty entry title to produce an ABSENT /Title key "
            f"(metadata.title is None), got {metadata.title!r} -- measured "
            "this session, see RESEARCH.md Pitfall 6."
        )
        # Author: an empty authors array still yields a present, empty
        # /Author value -- the asymmetric counterpart to the title case.
        assert metadata.author == "", (
            "Expected an empty entry author to produce a PRESENT, empty "
            f"/Author value, got {metadata.author!r} -- measured this "
            "session, see RESEARCH.md Pitfall 6."
        )

    def test_emitted_typ_carries_the_entry_values(
        self, entry_title_author_render_gate_dir, temp_build_dir
    ):
        """
        A ``.typ``-level companion assertion so a future failure can be
        localised to either the emission side (writer.py/template_engine.py)
        or the compile side (typst.compile()).
        """
        result = _run_sphinx_build_typstpdf(
            entry_title_author_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        assert "My Handbook" in typ_text, (
            "Expected the entry's title 'My Handbook' to appear in the "
            f"emitted .typ:\n{typ_text}"
        )
