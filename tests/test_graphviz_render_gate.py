"""
S02 real-render acceptance gate: graphviz directives produce real diagrams.

This module carries the slice's primary proof, against
``tests/fixtures/graphviz_render_gate/`` and through the full pipeline:

    sphinx-build -b typst  ->  typst.compile()  ->  pypdf text-extraction

It asserts, of one real compiled artifact, that:

1. all three directive spellings -- ``.. graphviz::`` with inline DOT,
   ``.. digraph::`` and ``.. graph::`` (undirected ``--`` edges) -- render
   as actual diagrams, proven by each diagram's own sentinel label
   surviving into the extracted PDF text (R001, R002);
2. a Japanese label extracts literally, with no font configuration anywhere
   in the fixture (R012);
3. the ``[graphviz diagram omitted]`` placeholder path is GONE for inline
   DOT -- neither the placeholder wording in the PDF nor its one warning in
   sphinx-build's stderr (DEG-01 / Issue #114);
4. no Graphviz binary was involved: ``shutil.which("dot") is None`` while
   every diagram above rendered anyway (R010).

**The assertion trap (MEM008).** diagraph renders *unquoted* DOT node
identifiers through Typst **math** mode. Measured by real compile plus
pypdf extraction: node ``a`` extracts as ``U+1D44E`` (math italic) and --
worse, because it is silent -- node ``alpha`` extracts as ``U+03B1``, since
math mode resolves Greek-letter *names* to Greek *symbols*. Multi-character
non-Greek identifiers such as ``bare_node`` happen to survive as ASCII,
which makes the trap intermittent and easy to "fix" by accident. Every
PDF-text assertion below therefore targets an explicitly QUOTED DOT label
(``x [label="SomeSentinel"];``), never a bare node identifier. An assertion
on a bare identifier is invalid even when it passes.

The build and compile are done ONCE per module via a module-scoped fixture,
mirroring ``tests/test_diagraph_escaping_render_gate.py``. A consequence
(MEM011): an import or emission regression surfaces here as a fixture-level
ERROR, not as a targeted assertion failure -- read the fixture's error, not
the test names, when this module goes red.
"""

import shutil
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

# Sentinel tokens, one pair per diagram, each the content of an explicitly
# QUOTED DOT label in tests/fixtures/graphviz_render_gate/index.rst. They
# are deliberately nonsense words so `in pdf_text` cannot be satisfied
# incidentally by template boilerplate, headings or Sphinx chrome.
INLINE_SENTINELS = ("Zylkefirst", "Quorbatsecond")
DIGRAPH_SENTINELS = ("Vandrimthird", "Pelunkofourth")
GRAPH_SENTINELS = ("Skarmelfifth", "Threbixsixth")
JAPANESE_SENTINELS = ("Ondricseventh",)

# The Japanese label, asserted to extract literally with NO font
# configuration in the fixture (R012).
JAPANESE_LABEL = "日本語ラベル"

# The graceful-degrade placeholder's two observable signatures, both of
# which must now be absent for inline DOT: the rendered wording, and the
# single warning _visit_graphical_placeholder() logs.
PLACEHOLDER_WORDING = "omitted"
PLACEHOLDER_WARNING = "graphviz is not supported in Typst output"


@pytest.fixture(scope="module")
def graphviz_render_gate_build(tmp_path_factory):
    """
    Build + real-compile the graphviz render-gate fixture ONCE per module.

    Returns a dict with sphinx-build's captured streams and the
    pypdf-extracted PDF text, so each test below asserts a disjoint slice of
    the SAME real artifact rather than re-running the (WASM-Graphviz-backed,
    four-diagram) compile once per test. Depends only on
    ``tmp_path_factory``, which is module-scope-compatible, to avoid a
    pytest ScopeMismatch.
    """
    source_dir = Path(__file__).parent / "fixtures" / "graphviz_render_gate"
    build_dir = tmp_path_factory.mktemp("graphviz_render_gate") / "_build"

    # Invoked as `sys.executable -m sphinx` rather than `uv run
    # sphinx-build`: this reuses the exact interpreter/venv already running
    # this test and depends on no PATH resolution at all. See the longer
    # rationale at tests/test_pdf_render_gate.py:150-180.
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
    assert master_typ.exists(), "master.typ was not generated"

    # Compile the WRAPPER (master.typ), not the docname-derived content file
    # (index.typ), and do it WITHOUT try/except: a fatal must abort the
    # whole module loudly rather than be swallowed into a soft assertion.
    pdf_output = build_dir / "master.pdf"
    typst.compile(str(master_typ), output=str(pdf_output))

    assert pdf_output.exists(), "PDF file was not created"
    assert pdf_output.stat().st_size > 0, "PDF file is empty"
    with open(pdf_output, "rb") as f:
        magic = f.read(4)

    reader = pypdf.PdfReader(str(pdf_output))
    return {
        "returncode": result.returncode,
        "stderr": result.stderr,
        "magic": magic,
        "master_source": master_typ.read_text(encoding="utf-8"),
        "pdf_text": "\n".join(page.extract_text() for page in reader.pages),
    }


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the S02 render gate",
)
class TestGraphvizRenderGate:
    """Real-compile acceptance gate for graphviz -> diagraph rendering."""

    def test_build_and_pdf_are_well_formed(self, graphviz_render_gate_build):
        """sphinx-build exits 0 and the compiled artifact is a real PDF."""
        assert graphviz_render_gate_build["returncode"] == 0
        assert graphviz_render_gate_build["magic"] == b"%PDF", (
            "the compiled artifact does not start with the %PDF magic bytes; "
            f"got {graphviz_render_gate_build['magic']!r}"
        )

    def test_inline_graphviz_directive_renders(self, graphviz_render_gate_build):
        """
        ``.. graphviz::`` with inline DOT produces a real diagram (R001).

        Proven by its QUOTED labels reaching the extracted PDF text: a
        diagram that degraded into diagraph's red error block would still
        compile, so a bare exit-0 proves nothing.
        """
        pdf_text = graphviz_render_gate_build["pdf_text"]
        for sentinel in INLINE_SENTINELS:
            assert sentinel in pdf_text, (
                f"inline `.. graphviz::` label {sentinel!r} missing from the "
                f"extracted PDF text. Extracted:\n{pdf_text}"
            )

    def test_digraph_directive_renders(self, graphviz_render_gate_build):
        """``.. digraph:: name`` produces a real diagram (R002)."""
        pdf_text = graphviz_render_gate_build["pdf_text"]
        for sentinel in DIGRAPH_SENTINELS:
            assert sentinel in pdf_text, (
                f"`.. digraph::` label {sentinel!r} missing from the "
                f"extracted PDF text. Extracted:\n{pdf_text}"
            )

    def test_graph_directive_renders(self, graphviz_render_gate_build):
        """
        ``.. graph:: name`` with undirected ``--`` edges renders (R002).

        Kept separate from the digraph case: the two directives take
        different edge operators, and an undirected graph is the spelling
        most likely to be missed by an implementation that only ever saw
        ``digraph``.
        """
        pdf_text = graphviz_render_gate_build["pdf_text"]
        for sentinel in GRAPH_SENTINELS:
            assert sentinel in pdf_text, (
                f"`.. graph::` label {sentinel!r} missing from the extracted "
                f"PDF text. Extracted:\n{pdf_text}"
            )

    def test_japanese_label_is_legible(self, graphviz_render_gate_build):
        """
        A Japanese QUOTED label extracts literally, with no font config
        anywhere in the fixture (R012).

        Its ASCII neighbour is asserted alongside it so a wholesale failure
        of this fourth diagram is distinguishable from a Japanese-specific
        one.
        """
        pdf_text = graphviz_render_gate_build["pdf_text"]
        for sentinel in JAPANESE_SENTINELS:
            assert sentinel in pdf_text, (
                f"ASCII label {sentinel!r} from the Japanese diagram is "
                f"missing -- that diagram did not render at all. Extracted:\n"
                f"{pdf_text}"
            )
        assert JAPANESE_LABEL in pdf_text, (
            f"Japanese label {JAPANESE_LABEL!r} missing from the extracted "
            f"PDF text. Extracted:\n{pdf_text}"
        )

    def test_placeholder_is_gone_for_inline_dot(self, graphviz_render_gate_build):
        """
        The graceful-degrade placeholder path no longer fires (DEG-01).

        Both of its observable signatures must be absent: the rendered
        ``[graphviz diagram omitted]`` wording in the PDF text, and the
        single warning ``_visit_graphical_placeholder()`` logs to stderr.
        The stderr half is the one that would still catch a regression in
        which the placeholder fired but its text happened not to extract.
        """
        pdf_text = graphviz_render_gate_build["pdf_text"]
        assert PLACEHOLDER_WORDING not in pdf_text, (
            "the graceful-degrade placeholder wording is still in the "
            f"compiled PDF -- visit_graphviz regressed. Extracted:\n{pdf_text}"
        )
        stderr = graphviz_render_gate_build["stderr"]
        assert PLACEHOLDER_WARNING not in stderr, (
            "visit_graphviz still logged the graceful-degrade warning:\n" f"{stderr}"
        )


@pytest.mark.slow
def test_no_graphviz_binary_is_installed():
    """
    R010: the diagrams above rendered with NO Graphviz binary present.

    Asserted rather than narrated, and kept as its own module-level test --
    outside the class and independent of the shared build fixture -- so its
    failure message is unambiguous on a machine that happens to have
    Graphviz installed. A failure here does not mean typsphinx regressed; it
    means this environment can no longer prove R010, because `dot` on PATH
    would make the rendering evidence above ambiguous.
    """
    assert shutil.which("dot") is None, (
        "a Graphviz `dot` binary is on PATH at "
        f"{shutil.which('dot')!r}; R010 (diagrams render with no Graphviz "
        "binary present) cannot be proven in this environment"
    )
