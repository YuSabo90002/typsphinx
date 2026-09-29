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

from typsphinx.translator import escape_typst_string

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

# S03 option-routing sentinels (R004, R005), one group per new diagram in
# the same fixture. Disjoint from the four S02 groups above so a failure
# localises to the option under test.
LAYOUT_SENTINELS = ("Brindlewockeighth", "Cavorteenninth", "Drimplenoxtenth")
ALT_SENTINELS = ("Ferrymantleeleventh", "Glaskivoretwelfth")

# S03 R003 regression-lock sentinels: the `:caption:`/`:name:` figure
# path was MEASURED ALREADY WORKING at plan time with no translator
# change, so these lock it rather than drive it. Disjoint from every
# group above so a caption/anchor regression localises here.
CAPTION_SENTINELS = ("Mordevainethirteenth", "Plexiturnofourteenth")
CAPTION_TEXT = "Wrenthalorvex caption sentinel"

# The `:name:` label as written in the fixture, and the anchor Sphinx
# derives from it. `figure_wrapper()` puts `:name:` on the FIGURE, never
# on the graphviz node (D-003/MEM003), and the writer namespaces it with
# the docname -- so the emitted anchor is `<index:grimsdale-figure>`.
FIGURE_NAME = "grimsdale-figure"
FIGURE_ANCHOR = "index:grimsdale-figure"

# The numref-generated caption prefix. With `numfig = True` the body
# reference renders as `Fig. 1`; asserting the prefix alone keeps the
# test from breaking if an earlier fixture diagram ever becomes a figure
# and shifts the number.
NUMREF_PREFIX = "Fig."

# The `:alt:` text itself. Asserted on the emitted .typ only -- see
# test_alt_option_reaches_diagraph_alt for why a PDF assertion on it is
# unsatisfiable.
ALT_TEXT = "Hoskrivendale alt sentinel"

# The 3-node CYCLE compiled twice, under two engines, by the differential
# test. A cycle has no ranking, so neato's force-directed placement and
# dot's ranked placement disagree -- which is what makes a dropped
# `engine:` parameter observable in the PDF bytes.
DIFFERENTIAL_DOT = (
    "digraph d { "
    'a [label="Ristovaneprobe"]; '
    'b [label="Sundralineprobe"]; '
    'c [label="Torbaxeneprobe"]; '
    "a -> b; b -> c; c -> a; }"
)

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
        # The wrapper master.typ carries only the template call and an
        # `#include("index.typ")`; every render() call the translator emits
        # lands in the docname-derived CONTENT file. Measured while
        # building the S03 option gates -- an assertion about emitted
        # render() parameters on `master_source` is unsatisfiable, so the
        # option tests read `content_source` instead.
        "content_source": (build_dir / "index.typ").read_text(encoding="utf-8"),
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

    def test_layout_option_reaches_diagraph_engine(self, graphviz_render_gate_build):
        """
        ``:layout: neato`` routes to diagraph's ``engine:`` parameter (R004).

        Sphinx normalises both ``:layout:`` and its ``:graphviz_dot:``
        alias onto ``node['options']['graphviz_dot']``, so this one
        directive spelling covers both. The emitted parameter is asserted
        alongside the diagram's own sentinels, so a diagram that carried
        the parameter but failed to render is distinguishable from one
        that rendered without it.
        """
        content_source = graphviz_render_gate_build["content_source"]
        assert 'engine: "neato"' in content_source, (
            "`:layout: neato` did not reach diagraph's `engine:` parameter; "
            "visit_graphviz emitted no engine for it. Emitted source:\n"
            f"{content_source}"
        )
        pdf_text = graphviz_render_gate_build["pdf_text"]
        for sentinel in LAYOUT_SENTINELS:
            assert sentinel in pdf_text, (
                f"`:layout: neato` diagram label {sentinel!r} missing from "
                f"the extracted PDF text -- the diagram did not render "
                f"under that engine. Extracted:\n{pdf_text}"
            )

    def test_layout_neato_actually_changes_the_render(self, tmp_path):
        """
        The differential: ``engine:`` is HONOURED, not merely present (D010).

        A sentinel-presence assertion cannot prove this. If diagraph
        silently ignored an unknown-to-it parameter, or if visit_graphviz
        dropped it, the fallback is ``dot`` and every label still extracts
        identically -- so a presence gate passes against a completely
        unimplemented ``:layout:``. Instead, compile the SAME DOT twice,
        changing only the engine, and require the PDF bytes to differ.

        Measured at plan time (diagraph 0.3.7, this 3-node cycle): default
        and ``engine: "dot"`` both hash to ``ac23bf32e0bb``, ``neato`` to
        ``9bc068aa7555``, ``circo`` to ``99d7bd95f807`` -- the engines are
        byte-distinguishable, which is what this test relies on.

        Deliberately independent of the module build fixture: it proves a
        property of diagraph itself, so coupling it to the Sphinx build
        would make a build failure look like an engine failure.
        """
        # The DOT carries QUOTED labels (MEM008), so it must go through the
        # same single escaping layer the translator uses before it is
        # embedded in a Typst string literal -- unescaped, typst.compile()
        # fails with "expected comma".
        escaped_dot = escape_typst_string(DIFFERENTIAL_DOT)

        pdfs = {}
        for engine in ("neato", "dot"):
            source = tmp_path / f"differential_{engine}.typ"
            source.write_text(
                '#import "@preview/diagraph:0.3.7": render\n'
                f'#render("{escaped_dot}", engine: "{engine}")\n',
                encoding="utf-8",
            )
            output = tmp_path / f"differential_{engine}.pdf"
            typst.compile(str(source), output=str(output))
            pdfs[engine] = output.read_bytes()
            assert pdfs[engine].startswith(b"%PDF"), (
                f"the {engine} differential probe did not compile to a real " "PDF"
            )

        assert pdfs["neato"] != pdfs["dot"], (
            'the same DOT compiled identically under `engine: "neato"` and '
            '`engine: "dot"` -- diagraph is not honouring the engine '
            "parameter, so the R004 gate above proves nothing about layout"
        )

    def test_alt_option_reaches_diagraph_alt(self, graphviz_render_gate_build):
        """
        ``:alt:`` routes to diagraph's ``alt:`` parameter (R005).

        Asserted on the emitted ``.typ``, NOT on ``pdf_text``, and
        deliberately so: alt text is accessibility metadata, invisible to
        pypdf text-extraction. Measured at plan time -- a probe carrying
        ``:alt: Alt text sentinel Zorbwick`` extracted ``Zorbwick`` as
        False from a correctly built PDF. Do not "strengthen" this into a
        PDF-text assertion; that assertion is unsatisfiable, not merely
        strict.

        The diagram's own quoted labels ARE asserted on the PDF, so an
        ``:alt:``-bearing diagram that failed to render is still caught.
        """
        content_source = graphviz_render_gate_build["content_source"]
        assert f'alt: "{ALT_TEXT}"' in content_source, (
            f"`:alt:` text {ALT_TEXT!r} did not reach diagraph's `alt:` "
            f"parameter. Emitted source:\n{content_source}"
        )
        pdf_text = graphviz_render_gate_build["pdf_text"]
        for sentinel in ALT_SENTINELS:
            assert sentinel in pdf_text, (
                f"`:alt:` diagram label {sentinel!r} missing from the "
                f"extracted PDF text -- that diagram did not render. "
                f"Extracted:\n{pdf_text}"
            )

    def test_plain_diagram_emits_no_engine_parameter(self, graphviz_render_gate_build):
        """
        An option-less diagram emits a bare ``render("...")`` (MEM009).

        diagraph's own signature already defaults ``engine: "dot"``, so a
        redundant default would be pure churn -- and churn in emitted
        ``.typ`` text is what breaks the byte-identity goldens elsewhere in
        the suite. The fixture's first four diagrams carry no options, so
        at least four of its render() calls must open with the DOT string
        and close immediately after it.
        """
        content_source = graphviz_render_gate_build["content_source"]
        total_renders = content_source.count('render("')
        engine_renders = content_source.count("engine: ")
        assert total_renders > engine_renders, (
            f"every one of the {total_renders} render() calls in the emitted "
            f"source carries an `engine:` parameter; visit_graphviz is "
            "emitting a redundant default for option-less diagrams. Emitted "
            f"source:\n{content_source}"
        )

    def test_caption_renders_as_figure_caption(self, graphviz_render_gate_build):
        """
        ``:caption:`` makes the diagram a real Typst figure (R003).

        A REGRESSION LOCK, not a driver: this path was measured working at
        plan time with no translator change. If it goes red, something
        else broke -- `visit_graphviz`, `visit_figure` or `depart_caption`
        -- and the fix belongs there, not in a re-implementation of a path
        that already worked.

        Both halves matter. The PDF half proves the caption and the
        diagram actually rendered; the emitted-source half proves the
        diagram became a ``#figure(...)`` carrying a ``caption:`` rather
        than a bare ``render()`` with the caption text merely printed
        somewhere nearby.
        """
        pdf_text = graphviz_render_gate_build["pdf_text"]
        assert CAPTION_TEXT in pdf_text, (
            f"caption text {CAPTION_TEXT!r} missing from the extracted PDF "
            f"text -- `:caption:` no longer renders. Extracted:\n{pdf_text}"
        )
        for sentinel in CAPTION_SENTINELS:
            assert sentinel in pdf_text, (
                f"captioned diagram label {sentinel!r} missing from the "
                f"extracted PDF text -- the diagram itself did not render, "
                f"so the caption assertion above proves nothing about the "
                f"figure path. Extracted:\n{pdf_text}"
            )

        # Emitted on the CONTENT file, not master.typ: this fixture's
        # master doc is a wrapper that only `#include`s index.typ (MEM026).
        content_source = graphviz_render_gate_build["content_source"]
        assert "#figure(" in content_source, (
            "the captioned diagram did not become a Typst `#figure(` at "
            f"all. Emitted source:\n{content_source}"
        )
        assert f'caption: {{text("{CAPTION_TEXT}")}}' in content_source, (
            f"no `caption:` carrying {CAPTION_TEXT!r} in the emitted "
            f"figure. Emitted source:\n{content_source}"
        )

    def test_name_yields_resolvable_numref_anchor(self, graphviz_render_gate_build):
        """
        ``:name:`` yields an anchor a ``numref`` actually resolves (R003).

        Presence of a ``<label>`` proves nothing on its own -- a dangling
        anchor nobody reaches looks identical. So this asserts three
        things that only hold together: the anchor exists, a ``link(<``
        targets the SAME label, and the rendered PDF carries the
        numref-generated figure number, which Sphinx emits only when it
        resolved the reference (an unresolved one warns and degrades).
        """
        content_source = graphviz_render_gate_build["content_source"]
        assert f"<{FIGURE_ANCHOR}>" in content_source, (
            f"`:name: {FIGURE_NAME}` produced no `<{FIGURE_ANCHOR}>` "
            f"anchor in the emitted source:\n{content_source}"
        )
        # Same label on both sides, so a link pointing at some OTHER
        # anchor cannot satisfy this pair.
        assert f"link(<{FIGURE_ANCHOR}>" in content_source, (
            f"no `link(<{FIGURE_ANCHOR}>` in the emitted source -- the "
            "`:numref:` reference did not target the figure's own anchor, "
            f"so the anchor is dangling. Emitted source:\n{content_source}"
        )

        pdf_text = graphviz_render_gate_build["pdf_text"]
        assert NUMREF_PREFIX in pdf_text, (
            f"the numref-generated figure number ({NUMREF_PREFIX!r}) is "
            "missing from the extracted PDF text -- Sphinx did not resolve "
            f"`:numref:` to a figure number. Extracted:\n{pdf_text}"
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
