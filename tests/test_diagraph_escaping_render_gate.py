"""
S01 real-render acceptance gate for the diagraph wiring and DOT escaping.

This module retires the slice's actual risk. It runs the full pipeline for
real against ``tests/fixtures/diagraph_escaping_render_gate/``:

    sphinx-build -b typst  ->  typst.compile()  ->  pypdf text-extraction

and asserts three separable things that no in-process substring check can
establish:

1. **Both emission paths carry the import.** ``master.typ`` (the templated
   master-document path, owned by ``template_engine.py``) and
   ``included.typ`` (the minimal-import included-document path, owned by
   ``writer.py``) must each declare ``@preview/diagraph:0.3.7``. The
   included half is the one that regresses silently if only
   ``template_engine.py`` were patched -- Typst's ``#include()`` does not
   inherit imports from the parent file, so each emitted file must
   re-declare its own.

2. **The escaped hostile DOT actually renders.** The fixture carries no
   diagraph import of its own, so the compile can only succeed if the
   builder emitted one -- which makes the compile itself a second,
   independent proof of (1). Beyond compiling, the extracted PDF text must
   positively contain the diagram's labels: a diagram that silently
   degraded to diagraph's red error block would still "compile", so a bare
   exit-0 proves nothing. The asserted labels cover the R013-hazardous
   character set -- an escaped double quote, a literal backslash, a ``\\n``
   escape that must become a real line break, and Japanese text.

3. **Nothing leaked as raw Typst syntax.** The emitted ``index.typ`` must
   keep the whole DOT inside ONE single-line string literal; a physical
   newline inside ``render("...")`` would mean ``escape_typst_string()``
   passed a raw newline straight through.

The build and compile are done ONCE per module via a module-scoped fixture
whose result every test reads, mirroring how ``test_pdf_render_gate.py``
shares a single extraction across its test methods.
"""

import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

# The diagraph package coordinate that must appear at every emission path.
# Kept as one literal so a version bump fails here loudly rather than
# half-matching. tests/test_preview_version_sync.py owns the three-site
# lockstep itself; this module only asserts the coordinate reaches OUTPUT.
DIAGRAPH_IMPORT = "@preview/diagraph:0.3.7"

# Diagram-label sentinels asserted in the extracted PDF text. Each is the
# rendered form of one R013-hazardous construct in the fixture's DOT, and
# each was measured to round-trip through a real compile:
#
#   'quote " x'    <- DOT `label="quote \" x"`  : escaped double quote
#   'back\slash'   <- DOT `label="back\\slash"` : literal backslash
#   'line1'/'line2'<- DOT `label="line1\nline2"`: \n became a real break
#   '日本語'        <- DOT `label="日本語"`       : non-ASCII passthrough
#
# All four are explicitly QUOTED labels in the DOT. Bare node identifiers
# (a .. e) are rendered by diagraph through Typst math mode and extract as
# math glyphs rather than ASCII -- deliberately not asserted on.
QUOTE_LABEL = 'quote " x'
BACKSLASH_LABEL = "back\\slash"
JAPANESE_LABEL = "日本語"


@pytest.fixture(scope="module")
def diagraph_render_gate_build(tmp_path_factory):
    """
    Build + real-compile the diagraph escaping fixture ONCE per module.

    Returns a dict with the emitted ``.typ`` sources and the pypdf-extracted
    PDF text, so each test below asserts a disjoint slice of the SAME real
    artifact instead of re-running sphinx-build/typst.compile() four times.
    Depends only on ``tmp_path_factory`` (module-scope-compatible), not on
    any function-scoped fixture, to avoid a pytest ScopeMismatch.
    """
    source_dir = Path(__file__).parent / "fixtures" / "diagraph_escaping_render_gate"
    build_dir = tmp_path_factory.mktemp("diagraph_escaping_render_gate") / "_build"

    # Invoked as `sys.executable -m sphinx` rather than `uv run
    # sphinx-build`: this reuses the exact interpreter/venv already running
    # this test and depends on no PATH resolution at all. See the longer
    # rationale at tests/test_pdf_render_gate.py:216-234.
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typst",
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )
    assert (
        result.returncode == 0
    ), f"sphinx-build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"

    master_typ = build_dir / "master.typ"
    index_typ = build_dir / "index.typ"
    included_typ = build_dir / "included.typ"
    for emitted in (master_typ, index_typ, included_typ):
        assert emitted.exists(), f"{emitted.name} was not generated"

    # Compile the WRAPPER (master.typ), not the content file (index.typ),
    # and do it WITHOUT try/except: a fatal must abort the whole module
    # loudly rather than be swallowed into a soft assertion.
    pdf_output = build_dir / "master.pdf"
    typst.compile(str(master_typ), output=str(pdf_output))

    assert pdf_output.exists(), "PDF file was not created"
    assert pdf_output.stat().st_size > 0, "PDF file is empty"
    with open(pdf_output, "rb") as f:
        assert f.read(4) == b"%PDF", "Generated file is not a valid PDF"

    reader = pypdf.PdfReader(str(pdf_output))
    return {
        "master_source": master_typ.read_text(encoding="utf-8"),
        "index_source": index_typ.read_text(encoding="utf-8"),
        "included_source": included_typ.read_text(encoding="utf-8"),
        "pdf_text": "\n".join(page.extract_text() for page in reader.pages),
    }


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the S01 render gate",
)
class TestDiagraphEscapingRenderGate:
    """Real-compile acceptance gate for diagraph wiring + DOT escaping."""

    def test_master_document_declares_diagraph_import(self, diagraph_render_gate_build):
        """
        The templated master-document path emits the diagraph import.

        This is the half owned by ``template_engine.py``'s generated import
        block.
        """
        assert DIAGRAPH_IMPORT in diagraph_render_gate_build["master_source"], (
            "master.typ does not declare "
            f"{DIAGRAPH_IMPORT}; the master-document import path "
            "(template_engine.py) regressed"
        )

    def test_included_document_declares_diagraph_import(
        self, diagraph_render_gate_build
    ):
        """
        The included-document path emits the diagraph import too.

        This is the half that regresses SILENTLY if only
        ``template_engine.py`` were patched: Typst's ``#include()`` does not
        inherit imports from the parent file, so ``writer.py``'s minimal
        import preamble for non-master documents must carry diagraph itself.
        """
        assert DIAGRAPH_IMPORT in diagraph_render_gate_build["included_source"], (
            "included.typ does not declare "
            f"{DIAGRAPH_IMPORT}; the included-document import path "
            "(writer.py) regressed"
        )

    def test_escaped_quote_label_survives_into_pdf(self, diagraph_render_gate_build):
        """
        A DOT label containing an escaped double quote renders as text.

        Positive assertion, not merely "it compiled": a diagram that
        degraded into diagraph's red error block would still compile, so
        only the presence of the label's own glyphs proves a real render.
        """
        pdf_text = diagraph_render_gate_build["pdf_text"]
        assert QUOTE_LABEL in pdf_text, (
            f"quote-bearing label {QUOTE_LABEL!r} missing from extracted PDF "
            "text -- the diagram likely rendered as an error block rather "
            f"than a graph. Extracted:\n{pdf_text}"
        )

    def test_backslash_and_newline_labels_survive_into_pdf(
        self, diagraph_render_gate_build
    ):
        """
        A literal backslash survives, and a DOT ``\\n`` becomes a real break.

        ``back\\slash`` proves the backslash was not eaten or doubled, and
        ``line1``/``line2`` appearing on separate extracted lines proves the
        ``\\n`` reached Graphviz as a line-break directive rather than
        arriving as a raw newline that would have broken the Typst literal.
        """
        pdf_text = diagraph_render_gate_build["pdf_text"]
        assert BACKSLASH_LABEL in pdf_text, (
            f"backslash label {BACKSLASH_LABEL!r} missing from extracted PDF "
            f"text. Extracted:\n{pdf_text}"
        )
        assert "line1\nline2" in pdf_text, (
            "the DOT '\\n' escape did not render as a line break inside the "
            f"label. Extracted:\n{pdf_text}"
        )

    def test_japanese_label_survives_into_typ_source(self, diagraph_render_gate_build):
        """
        A non-ASCII (Japanese) DOT label survives escaping into the .typ.

        Proven at the emitted-Typst-SOURCE tier only, not by PDF text
        extraction: CJK glyph extraction depends on system font
        availability this project has never pinned (typst-py's embedded
        fonts have no CJK coverage and Typst's fallback is silent), so a
        PDF-tier assertion passes on macOS and fails on the ubuntu and
        windows CI runners. Same split as
        ``tests/test_admonition_locale_title_precedence_gate.py``.
        """
        index_source = diagraph_render_gate_build["index_source"]
        render_lines = [
            line for line in index_source.splitlines() if 'render("' in line
        ]
        assert any(JAPANESE_LABEL in line for line in render_lines), (
            f"Japanese label {JAPANESE_LABEL!r} missing from the render() "
            f"literal in index.typ. render lines:\n{render_lines}"
        )

    def test_render_literal_has_no_physical_newline(self, diagraph_render_gate_build):
        """
        The whole DOT stays inside ONE single-line Typst string literal.

        Negative control for raw-syntax leakage: if
        ``escape_typst_string()`` let a real newline through, the literal
        opened on the ``render("`` line would not close on that same line
        and the emitted Typst would be syntactically broken. Asserted by
        walking the line character-by-character and requiring an unescaped
        closing quote before end-of-line.
        """
        index_source = diagraph_render_gate_build["index_source"]
        render_lines = [
            line for line in index_source.splitlines() if 'render("' in line
        ]
        assert len(render_lines) == 1, (
            f'expected exactly one render(" line in index.typ, found '
            f"{len(render_lines)}"
        )

        line = render_lines[0]
        start = line.index('render("') + len('render("')
        i = start
        closed = False
        while i < len(line):
            if line[i] == "\\":
                # Skip the escaped character: a \" here is DATA, not the
                # literal's terminator.
                i += 2
                continue
            if line[i] == '"':
                closed = True
                break
            i += 1

        assert closed, (
            "the render() string literal does not close on its own line -- a "
            "physical newline leaked into the Typst literal. Line was:\n"
            f"{line}"
        )
