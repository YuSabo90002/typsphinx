"""
D-04 real-render acceptance gate for the admonition rendering fix (Phase 08.1).

This is the only place the original bug was ever visible: the translator's
loose in-process substring asserts (e.g. ``"info[" in output``) passed even
while the admonition body rendered as literal Typst source once compiled to
PDF. This module closes that gap by running the full pipeline for real:

    sphinx-build -b typst  ->  typst.compile()  ->  pypdf text-extraction

and asserting that none of the literal-source leak signatures (the
paragraph-call / text-call / raw-call open-paren forms) appear in the
extracted PDF prose.
"""

import re
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

# The literal-source-leak signatures from the Phase 7 deferred-items.md
# symptom (see 08.1-RESEARCH.md "D-04: PDF text-extraction acceptance gate").
# These three token strings appear only as this test's own negative-search
# literals -- they are NOT expected in any source file's body prose.
LEAK_SIGNATURES = ("par({", 'text("', 'raw("')

# Sentinel token for the TODO-01 todo-render-gate fixture -- distinctive,
# unlikely token chosen so `full_text.count(...)`/`in full_text` can prove
# the `.. todo::` body reached (or, in the disabled case, never reached) the
# compiled output. Must match the sentinel token embedded in
# todo_render_gate/index.rst.
TODO_BODY_SENTINEL = "TODOBODYSENTINEL9X4"


@pytest.fixture
def fixtures_dir():
    """Return the path to tests/fixtures/ directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def admonition_render_gate_dir(fixtures_dir):
    """Return the path to the admonition_render_gate fixture project."""
    return fixtures_dir / "admonition_render_gate"


@pytest.fixture
def figure_length_render_gate_dir(fixtures_dir):
    """Return the path to the figure_length_render_gate fixture project."""
    return fixtures_dir / "figure_length_render_gate"


@pytest.fixture
def figure_target_caption_render_gate_dir(fixtures_dir):
    """Return the path to the figure_target_caption_render_gate fixture project."""
    return fixtures_dir / "figure_target_caption_render_gate"


@pytest.fixture
def graphviz_degrade_render_gate_dir(fixtures_dir):
    """Return the path to the graphviz_degrade_render_gate fixture project."""
    return fixtures_dir / "graphviz_degrade_render_gate"


@pytest.fixture
def version_modified_render_gate_dir(fixtures_dir):
    """Return the path to the version_modified_render_gate fixture project."""
    return fixtures_dir / "version_modified_render_gate"


@pytest.fixture
def xref_refid_render_gate_dir(fixtures_dir):
    """Return the path to the xref_refid_render_gate fixture project."""
    return fixtures_dir / "xref_refid_render_gate"


@pytest.fixture
def desc_signature_render_gate_dir(fixtures_dir):
    """Return the path to the desc_signature_render_gate fixture project."""
    return fixtures_dir / "desc_signature_render_gate"


@pytest.fixture
def trivial_blocks_render_gate_dir(fixtures_dir):
    """Return the path to the trivial_blocks_render_gate fixture project."""
    return fixtures_dir / "trivial_blocks_render_gate"


@pytest.fixture
def topic_line_block_render_gate_dir(fixtures_dir):
    """Return the path to the topic_line_block_render_gate fixture project."""
    return fixtures_dir / "topic_line_block_render_gate"


@pytest.fixture
def todo_render_gate_dir(fixtures_dir):
    """Return the path to the todo_render_gate fixture project."""
    return fixtures_dir / "todo_render_gate"


@pytest.fixture
def manpage_render_gate_dir(fixtures_dir):
    """Return the path to the manpage_render_gate fixture project."""
    return fixtures_dir / "manpage_render_gate"


@pytest.fixture
def table_width_render_gate_dir(fixtures_dir):
    """Return the path to the table_width_render_gate fixture project."""
    return fixtures_dir / "table_width_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path, extra_args: tuple = ()
) -> subprocess.CompletedProcess:
    """
    Run `sphinx-build -b typst` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as `sys.executable -m sphinx` (the sphinx-build console entry
    point's module form) rather than shelling out to `uv run sphinx-build`:
    this guarantees the exact interpreter/venv already running this test is
    reused, with no dependency on external PATH resolution of a `uv`
    executable. This matters in this project's dev sandbox specifically -- a
    stray non-Nix `uv` binary installed into `.venv/bin` (shadowing the
    correct Nix-provided `uv` earlier on PATH for subprocess children) makes
    `["uv", "run", ...]` exit 127 ("Could not start dynamically linked
    executable") when invoked from inside a pytest-launched subprocess, even
    though the same command succeeds when run directly in a shell.
    `sys.executable -m sphinx` sidesteps that PATH-shadowing hazard entirely.

    `extra_args` is an optional tuple of additional sphinx-build CLI
    arguments (e.g. `("-D", "todo_include_todos=0")`) spliced into the
    command list before the source dir -- default `()` keeps every
    pre-existing call site unchanged.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typst",
            *extra_args,
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the D-04 render gate",
)
class TestAdmonitionPdfRenderGate:
    """
    Real-compile acceptance gate for the admonition markup/code-mode fix.

    Requirements: D-04 (08.1-RESEARCH.md, 08.1-VALIDATION.md).
    """

    def test_admonition_pdf_has_no_literal_source_leak(
        self, admonition_render_gate_dir, temp_build_dir
    ):
        """
        Compile the admonition render-gate fixture to PDF and confirm the
        extracted text contains typeset prose, not literal Typst source.
        """
        # 1. sphinx-build -b typst on the fixture.
        #
        # Invoked as `sys.executable -m sphinx` (the sphinx-build console
        # entry point's module form) rather than shelling out to `uv run
        # sphinx-build`: this guarantees the exact interpreter/venv already
        # running this test is reused, with no dependency on external PATH
        # resolution of a `uv` executable. This matters in this project's
        # dev sandbox specifically -- a stray non-Nix `uv` binary installed
        # into `.venv/bin` (shadowing the correct Nix-provided `uv` earlier
        # on PATH for subprocess children) makes `["uv", "run", ...]` exit
        # 127 ("Could not start dynamically linked executable") when invoked
        # from inside a pytest-launched subprocess, even though the same
        # command succeeds when run directly in a shell. `sys.executable -m
        # sphinx` sidesteps that PATH-shadowing hazard entirely.
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "sphinx",
                "-b",
                "typst",
                str(admonition_render_gate_dir),
                str(temp_build_dir),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"

        # 2. Compile the emitted .typ to PDF with typst-py.
        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(index_typ), output=str(pdf_output))

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        # 3. Extract text with pypdf and assert no literal-source leak.
        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into rendered "
                "PDF text -- admonition markup/code-mode mismatch regression"
            )


# ---------------------------------------------------------------------------
# GATE-01 (Phase 11, D-04): extend the D-04 render-gate pattern established
# above to prove the Issue #114 fatal fixes (FIG-01 length conversion,
# FIG-02 caption buffer-swap + :target: refid/refuri branching, DEG-01/DEG-02
# graceful-degrade placeholders) through the same real
# sphinx-build -> typst.compile() -> pypdf pipeline. String-agreement unit
# tests alone proved insufficient for this exact subsystem before (pitfall
# #9) -- these three classes are the standing acceptance bar every later
# node-handler phase (12-14) extends.
# ---------------------------------------------------------------------------


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class TestFigureLengthRenderGate:
    """
    Real-compile acceptance gate for the FIG-01 length-unit conversion fix.

    Requirements: GATE-01 (11-CONTEXT.md D-04, 11-RESEARCH.md).
    """

    def test_figure_length_pdf_converts_px_and_drops_unknown_unit(
        self, figure_length_render_gate_dir, temp_build_dir
    ):
        """
        Compile the figure-length render-gate fixture to PDF and confirm the
        px case was converted to a Typst-valid pt length in the generated
        .typ, with no raw px (or other unconvertible unit) ever reaching
        Typst source -- the FIG-01 fatal case (Issue #114).
        """
        result = _run_sphinx_build_typst(figure_length_render_gate_dir, temp_build_dir)
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"
        typ_source = index_typ.read_text()

        # The 200px case must have been converted to the CSS-canonical
        # 1px = 0.75pt Typst length (150pt) -- never emitted as a raw,
        # Typst-invalid "200px" string.
        assert "150pt" in typ_source, (
            "Expected the converted pt value for the 200px case; "
            "_convert_length_to_typst() may have regressed"
        )
        assert "200px" not in typ_source, (
            "Raw unconverted 'px' unit leaked into generated Typst source "
            "-- this is the exact FIG-01 fatal Issue #114 case"
        )

        # 2. Compile the emitted .typ to PDF with typst-py. Any
        # TypstCompilationError must propagate and fail this test loudly --
        # a real compile is the only way to prove the warn+drop unknown-unit
        # (1ex) case didn't also leak a raw unit that would abort the build.
        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(index_typ), output=str(pdf_output))

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"


# Sentinel tokens for the caption render gate -- distinctive, unlikely
# single words chosen so `full_text.count(...)` can prove each caption's
# text reached the compiled PDF exactly once (guarding against the FIG-02
# double-emission/juxtaposition fatal bug). Must match the sentinel tokens
# embedded in figure_target_caption_render_gate/index.rst.
INTERNAL_TARGET_CAPTION_SENTINEL = "FIGCAPINTERNALQ7X9"
EXTERNAL_TARGET_CAPTION_SENTINEL = "FIGCAPEXTERNALK3M2"


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class TestFigureCaptionRenderGate:
    """
    Real-compile acceptance gate for the FIG-02 caption buffer-swap fix and
    the internal-:target:/external-:target: refid/refuri branching.

    Requirements: GATE-01 (11-CONTEXT.md D-03/D-04, 11-RESEARCH.md).
    """

    def test_figure_caption_pdf_has_each_sentinel_exactly_once(
        self, figure_target_caption_render_gate_dir, temp_build_dir
    ):
        """
        Compile the figure-target-caption render-gate fixture (one figure
        with an internal refid :target:, one with an external refuri
        :target:, each carrying a caption with markup-special characters)
        to PDF and confirm each caption's sentinel token appears exactly
        once in the extracted text -- guarding against the FIG-02
        double-emission/juxtaposition fatal bug -- with no LEAK_SIGNATURES
        token present.
        """
        result = _run_sphinx_build_typst(
            figure_target_caption_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"

        # Any TypstCompilationError must propagate and fail this test
        # loudly -- this is the only way to prove the internal refid
        # :target: branch actually resolves to a real Typst label anchor.
        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(index_typ), output=str(pdf_output))

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        assert full_text.count(INTERNAL_TARGET_CAPTION_SENTINEL) == 1, (
            "Internal-:target: figure caption sentinel did not appear "
            "exactly once -- possible FIG-02 double-emission regression"
        )
        assert full_text.count(EXTERNAL_TARGET_CAPTION_SENTINEL) == 1, (
            "External-:target: figure caption sentinel did not appear "
            "exactly once -- possible FIG-02 double-emission regression"
        )

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into "
                "rendered PDF text -- figure-caption markup/code-mode "
                "mismatch regression"
            )


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class TestGraphvizDegradeRenderGate:
    """
    Real-compile acceptance gate for the DEG-01/DEG-02 graceful-degrade
    placeholder fix (graphviz and inheritance_diagram nodes).

    Requirements: GATE-01 (11-CONTEXT.md D-01/D-04, 11-RESEARCH.md).
    """

    def test_graphviz_degrade_pdf_has_placeholder_and_no_source_leak(
        self, graphviz_degrade_render_gate_dir, temp_build_dir
    ):
        """
        Compile the graphviz/inheritance-diagram render-gate fixture to PDF
        and confirm the visible placeholder wording is present, no raw
        DOT/diagram-spec source leaked, and exactly one degrade warning
        fired per out-of-scope node.
        """
        result = _run_sphinx_build_typst(
            graphviz_degrade_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # Exactly one degrade warning per out-of-scope node (D-01): the
        # graphviz directive and the inheritance-diagram directive each
        # log exactly one logger.warning naming the node type.
        assert result.stderr.count("graphviz is not supported in Typst output") == 1, (
            "Expected exactly one graphviz degrade warning:\n" f"{result.stderr}"
        )
        assert (
            result.stderr.count("inheritance diagram is not supported in Typst output")
            == 1
        ), (
            "Expected exactly one inheritance_diagram degrade warning:\n"
            f"{result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"

        # Any TypstCompilationError must propagate and fail this test
        # loudly -- proving the placeholder rect()/text() emission (and the
        # SkipNode that prevents descending into raw DOT/diagram-spec
        # source) never aborts the compile.
        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(index_typ), output=str(pdf_output))

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        assert "omitted" in full_text, (
            "Expected the visible graceful-degrade placeholder wording "
            "(D-01) to be present in the extracted PDF text"
        )
        assert "digraph" not in full_text, (
            "Raw DOT source keyword 'digraph' leaked into rendered PDF "
            "text -- DEG-01 SkipNode regression"
        )
        assert "->" not in full_text, (
            "Raw DOT edge-arrow syntax leaked into rendered PDF text -- "
            "DEG-01 SkipNode regression"
        )


# ---------------------------------------------------------------------------
# Phase 12 (VER-01): extend the GATE-01 render-gate pattern to prove the
# versionmodified pass-through + visit_inline classed-dispatch fix -- all
# four version directives must render as unboxed italic, Sphinx-worded
# labels (never a gentle-clues callout box) plus their inline body, proven
# through a real sphinx-build -> typst.compile() -> pypdf round-trip.
# ---------------------------------------------------------------------------

# Sentinel tokens for the version_modified render gate -- distinctive,
# unlikely single words chosen so their presence in the extracted PDF text
# proves each body-bearing directive's content reached the compiled PDF.
# Must match the sentinel tokens embedded in
# version_modified_render_gate/index.rst.
VERADDED_BODY_SENTINEL = "VERADDEDBODYSENTINEL7Q1"
VERCHANGED_BODY_SENTINEL = "VERCHANGEDBODYSENTINEL8Q2"
VERDEPRECATED_BODY_SENTINEL = "VERDEPRECATEDBODYSENTINEL9Q3"


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class TestVersionModifiedRenderGate:
    """
    Real-compile acceptance gate for the VER-01 versionmodified pass-through
    + visit_inline classed-dispatch fix.

    Requirements: VER-01, GATE-01 (12-CONTEXT.md D-01/D-02, 12-RESEARCH.md
    Pattern 1).
    """

    def test_version_modified_pdf_has_labels_bodies_and_no_source_leak(
        self, version_modified_render_gate_dir, temp_build_dir
    ):
        """
        Compile the version_modified render-gate fixture to PDF and confirm
        all four Sphinx-computed label wordings, plus every body sentinel,
        appear in the extracted text -- proving the classed inline rendered
        as unboxed italic prose (never dropped, never a raw source token,
        never a gentle-clues callout box) -- with no LEAK_SIGNATURES token
        present.
        """
        result = _run_sphinx_build_typst(
            version_modified_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"

        # Any TypstCompilationError must propagate and fail this test
        # loudly -- this is the only way to prove the classed-inline
        # dispatch never emits invalid Typst source.
        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(index_typ), output=str(pdf_output))

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        # The four Sphinx-computed label wordings, by their stable prefixes
        # (D-01/D-02) -- proving the classed inline rendered as prose, not
        # dropped and not a raw source token.
        for expected_label in (
            "Added in version",
            "Changed in version",
            "Deprecated",
            "Removed in version",
        ):
            assert expected_label in full_text, (
                f"Expected version-directive label '{expected_label}' "
                "in extracted PDF text -- versionmodified/visit_inline "
                "classed-dispatch regression"
            )

        # Every body sentinel from the fixture must reach the compiled PDF.
        for sentinel in (
            VERADDED_BODY_SENTINEL,
            VERCHANGED_BODY_SENTINEL,
            VERDEPRECATED_BODY_SENTINEL,
        ):
            assert sentinel in full_text, (
                f"Expected body sentinel '{sentinel}' in extracted PDF "
                "text -- version-directive body content regression"
            )

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into "
                "rendered PDF text -- the version label must be typeset "
                'italic prose, never leaked text("/par({ source'
            )


# ---------------------------------------------------------------------------
# Phase 12 (XREF-01): extend the GATE-01 render-gate pattern to prove that a
# same-document `:ref:` section-anchor cross-reference AND a `:term:`
# glossary cross-reference both resolve to working Typst links in a real
# compile. The `:term:` case is the must-fail-until-fixed guard for the
# depart_term bracket-wrap <label> anchor fix -- without it, Typst aborts
# the ENTIRE compile with "label <term-Widget> does not exist" (12-RESEARCH.md
# Part 2).
# ---------------------------------------------------------------------------

# Sentinel tokens for the xref/refid render gate -- distinctive, unlikely
# words chosen so their presence in the extracted PDF text proves each
# cross-reference's surrounding prose reached the compiled PDF. Must match
# the sentinel tokens embedded in xref_refid_render_gate/index.rst.
REF_SECTION_SENTINEL = "REFSECTIONSENTINEL"
TERM_SENTINEL = "TERMSENTINEL"


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class TestXrefRefidRenderGate:
    """
    Real-compile acceptance gate for XREF-01: the depart_term bracket-wrap
    <label> anchor fix, and confirmation that visit_reference's refid branch
    (D-03) resolves both a `:ref:` section anchor and a `:term:` glossary
    reference to working links.

    Requirements: XREF-01, GATE-01 (12-CONTEXT.md D-03/D-04, 12-RESEARCH.md
    Part 2).
    """

    def test_xref_refid_pdf_has_working_links_and_no_empty_link(
        self, xref_refid_render_gate_dir, temp_build_dir
    ):
        """
        Compile the xref_refid render-gate fixture to PDF and confirm both
        the `:ref:` section anchor and the `:term:` glossary reference
        resolve to working links -- with no `link("", ...)` leak (D-04) and
        no fatal abort on the (previously dangling) `:term:` anchor.
        """
        result = _run_sphinx_build_typst(xref_refid_render_gate_dir, temp_build_dir)
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"

        typ_source = index_typ.read_text()
        assert "link(<" in typ_source, (
            "Expected at least one refid link(<...>, ...) anchor reference "
            "in the generated Typst source -- the :ref:/:term: refid branch "
            "may have regressed"
        )
        assert 'link("",' not in typ_source, (
            'Found link("", ...) in generated Typst source -- the '
            'never-link("", ...) contract (D-04) has regressed'
        )

        # Compile the emitted .typ to PDF with typst-py, WITHOUT try/except:
        # this is the crux of the test. Before the depart_term anchor fix,
        # the :term: reference's link(<term-Widget>, ...) pointed at an
        # undefined label and Typst aborted the ENTIRE compile here with
        # "label <term-Widget> does not exist" -- so this call is the
        # must-fail-until-fixed guard for the anchor bug.
        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(index_typ), output=str(pdf_output))

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        # Both the :ref: and the :term: cross-reference's surrounding
        # sentinel prose, plus the link text itself, must have reached the
        # compiled PDF.
        assert REF_SECTION_SENTINEL in full_text, (
            f"Expected sentinel '{REF_SECTION_SENTINEL}' in extracted PDF "
            "text -- :ref: section-anchor cross-reference regression"
        )
        assert TERM_SENTINEL in full_text, (
            f"Expected sentinel '{TERM_SENTINEL}' in extracted PDF text -- "
            ":term: glossary cross-reference regression"
        )
        assert "Target Section" in full_text, (
            "Expected the :ref: link text ('Target Section') in extracted " "PDF text"
        )
        assert (
            "Widget" in full_text
        ), "Expected the :term: link text ('Widget') in extracted PDF text"

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into "
                "rendered PDF text -- xref/refid markup/code-mode regression"
            )


# ---------------------------------------------------------------------------
# Phase 12 (DESC-01..04): extend the GATE-01 render-gate pattern to prove
# the desc_returns/desc_signature_line/desc_optional/desc_inline handlers
# (12-03-PLAN.md) render correctly in a real compile -- the return arrow,
# a GENUINE multi-line linebreak() (proven via real pypdf text-extraction,
# never a `.typ`-source `"\n"` check, per New Pitfall 11), nested optional
# brackets, and an inline fragment with no strong() wrapper.
# ---------------------------------------------------------------------------

# Sentinel tokens for the DESC-02 multi-line signature case -- distinctive,
# unlikely words chosen so a real pypdf extraction can prove the two
# desc_signature_line siblings render on SEPARATE lines (not concatenated
# with no separator). Must match the tokens embedded in
# desc_signature_render_gate/index.rst (the template parameter name and the
# C++ function name of the confirmed multi-line construction).
DESC_LINE_ONE_SENTINEL = "DESCLINEONESENTINEL4Q1"
DESC_LINE_TWO_SENTINEL = "DESCLINETWOSENTINEL5Q2"

# Sentinel for the DESC-04 inline :cpp:expr: fragment case.
DESC_INLINE_FRAGMENT_SENTINEL = "DescInlineExprToken"


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class TestDescSignatureRenderGate:
    """
    Real-compile acceptance gate for DESC-01..04: desc_returns (return
    arrow), desc_signature_line (genuine multi-line linebreak()),
    desc_optional (nested bracket wrap), and desc_inline (transparent
    pass-through, no strong() wrapper).

    Requirements: DESC-01, DESC-02, DESC-03, DESC-04, GATE-01
    (12-CONTEXT.md D-05/D-06, 12-RESEARCH.md Pattern 3, 12-03-PLAN.md).
    """

    def test_desc_signature_pdf_has_arrow_linebreak_brackets_and_inline(
        self, desc_signature_render_gate_dir, temp_build_dir
    ):
        """
        Compile the desc_signature_render_gate fixture to PDF and confirm,
        via real pypdf text-extraction:
        - the ' -> ' return arrow is present adjacent to the return type
          (DESC-01);
        - the two DESC-02 multi-line sentinels appear in the extracted
          text on SEPARATE lines (i.e. NOT concatenated with no
          separator) -- a real-extraction proof per New Pitfall 11, never
          a .typ-source '\\n' check;
        - the nested `printf(fmt[, args[, more]])` optional brackets are
          present, correctly nested (DESC-03);
        - the inline `:cpp:expr:` fragment token appears inline, with no
          LEAK_SIGNATURES token (DESC-04).

        Any TypstCompilationError from the uncaught typst.compile() call
        below must propagate and fail this test loudly -- the DESC-03
        nested-optional case is the one most likely to expose a bracket
        mismatch that would abort the whole compile (Pitfall 1).
        """
        result = _run_sphinx_build_typst(desc_signature_render_gate_dir, temp_build_dir)
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"

        # Compile the emitted .typ to PDF with typst-py, WITHOUT try/except:
        # this is the crux of the test -- a mismatched desc_optional bracket
        # nesting would abort the ENTIRE compile here (Pitfall 1), not just
        # fail a string-agreement check (Pitfall 9).
        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(index_typ), output=str(pdf_output))

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        # DESC-01: the return arrow, adjacent to the return type.
        assert "-> int" in full_text, (
            "Expected the ' -> ' return arrow adjacent to the return type "
            "in extracted PDF text -- desc_returns regression"
        )

        # DESC-02: both multi-line sentinels present, and NOT concatenated
        # with no separator -- a real-extraction proof (New Pitfall 11)
        # that a genuine Typst linebreak() (not a cosmetic source '\n')
        # separated the two desc_signature_line children.
        assert DESC_LINE_ONE_SENTINEL in full_text, (
            f"Expected multi-line sentinel '{DESC_LINE_ONE_SENTINEL}' in "
            "extracted PDF text -- desc_signature_line regression"
        )
        assert DESC_LINE_TWO_SENTINEL in full_text, (
            f"Expected multi-line sentinel '{DESC_LINE_TWO_SENTINEL}' in "
            "extracted PDF text -- desc_signature_line regression"
        )
        concatenated = DESC_LINE_ONE_SENTINEL + DESC_LINE_TWO_SENTINEL
        assert concatenated not in full_text, (
            "The two desc_signature_line sentinels were concatenated with "
            "no separator in extracted PDF text -- linebreak() did not "
            "produce a real visual break (New Pitfall 11 regression: a "
            "source '\\n' alone is cosmetic-only)"
        )

        # DESC-03: the nested printf(fmt[, args[, more]]) optional brackets.
        assert "printf(fmt, [args, [more]])" in full_text, (
            "Expected the nested printf(fmt[, args[, more]]) optional-"
            "bracket rendering in extracted PDF text -- desc_optional "
            "regression"
        )

        # DESC-04: the inline :cpp:expr: fragment token, rendered inline
        # (transparent pass-through, no strong() wrapper -- D-06).
        assert DESC_INLINE_FRAGMENT_SENTINEL in full_text, (
            f"Expected inline fragment sentinel "
            f"'{DESC_INLINE_FRAGMENT_SENTINEL}' in extracted PDF text -- "
            "desc_inline regression"
        )

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into "
                "rendered PDF text -- desc_signature markup/code-mode "
                "regression"
            )


# ---------------------------------------------------------------------------
# Phase 12 (BLK-01/04/05/06): extend the GATE-01 render-gate pattern to
# prove the transition/glossary/tabular_col_spec/abbreviation handlers
# (12-04-PLAN.md) render/skip correctly in a real compile -- a transition
# rule, a glossary definition list, a safely-skipped tabularcolumns hint
# (no leak), and an inline abbreviation expansion.
# ---------------------------------------------------------------------------

# Sentinel tokens for the trivial-blocks render gate -- distinctive,
# unlikely words chosen so their presence (or, for the tabularcolumns
# case, deliberate absence) in the extracted PDF text proves each handler
# behaved correctly. Must match the tokens embedded in
# trivial_blocks_render_gate/index.rst.
GLOSSARY_DEF_SENTINEL = "GLOSSARYDEFSENTINEL"
LEAK_COL_SPEC_SENTINEL = "LEAKCOLSPECSENTINEL"
ABBR_EXPANSION_SENTINEL = "ABBREXPANSIONSENTINEL"


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class TestTrivialBlocksRenderGate:
    """
    Real-compile acceptance gate for BLK-01/04/05/06: visit_transition,
    visit_glossary/depart_glossary, visit_tabular_col_spec, and
    visit_abbreviation/depart_abbreviation.

    Requirements: BLK-01, BLK-04, BLK-05, BLK-06, GATE-01 (12-CONTEXT.md
    D-07/D-08, 12-RESEARCH.md Part 4, 12-04-PLAN.md).
    """

    def test_trivial_blocks_pdf_renders_rule_glossary_and_abbr_no_leak(
        self, trivial_blocks_render_gate_dir, temp_build_dir
    ):
        """
        Compile the trivial_blocks_render_gate fixture to PDF and confirm,
        via the generated .typ source and real pypdf text-extraction:
        - the transition compiled to a `line(length: 100%)` horizontal
          rule (BLK-01) -- a horizontal rule has no reliable extracted-text
          signature, so this is asserted in the emitted source, backed by
          a successful compile;
        - the glossary term and its definition text appear in the
          extracted PDF text (BLK-04);
        - the distinctive tabularcolumns column-spec token is ABSENT from
          the extracted PDF text -- the SkipNode no-leak proof (BLK-05);
        - the abbreviation renders inline as "term (expansion)": both the
          term and the parenthesized expansion sentinel appear in the
          extracted text (BLK-06).

        Any TypstCompilationError from the uncaught typst.compile() call
        below must propagate and fail this test loudly.
        """
        result = _run_sphinx_build_typst(trivial_blocks_render_gate_dir, temp_build_dir)
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"

        # BLK-01: the transition compiled to a real horizontal rule -- a
        # rule has no reliable extracted-text signature, so assert it in
        # the emitted source (backed by the successful compile below).
        typ_source = index_typ.read_text()
        assert "line(length: 100%)" in typ_source, (
            "Expected 'line(length: 100%)' in generated Typst source -- "
            "visit_transition regression"
        )

        # Compile the emitted .typ to PDF with typst-py, WITHOUT
        # try/except: this is the crux of the test -- any regression in
        # the transition/glossary/tabular_col_spec/abbreviation handlers
        # that emitted invalid Typst source would abort the ENTIRE compile
        # here (Pitfall 1), not just fail a string-agreement check.
        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(index_typ), output=str(pdf_output))

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        # BLK-04: the glossary term and its definition text reached the
        # compiled PDF.
        assert "Widget" in full_text, (
            "Expected the glossary term 'Widget' in extracted PDF text -- "
            "visit_glossary/depart_glossary regression"
        )
        assert GLOSSARY_DEF_SENTINEL in full_text, (
            f"Expected glossary definition sentinel '{GLOSSARY_DEF_SENTINEL}' "
            "in extracted PDF text -- visit_glossary/depart_glossary "
            "regression"
        )

        # BLK-05: the tabularcolumns column-spec token must NOT leak into
        # the compiled PDF text -- the SkipNode no-leak proof.
        assert LEAK_COL_SPEC_SENTINEL not in full_text, (
            f"Tabularcolumns column-spec token '{LEAK_COL_SPEC_SENTINEL}' "
            "leaked into rendered PDF text -- visit_tabular_col_spec "
            "SkipNode regression"
        )

        # BLK-06: the abbreviation renders inline as "term (expansion)".
        assert "API" in full_text, (
            "Expected the abbreviation term 'API' in extracted PDF text -- "
            "visit_abbreviation regression"
        )
        assert ABBR_EXPANSION_SENTINEL in full_text, (
            f"Expected abbreviation expansion sentinel "
            f"'{ABBR_EXPANSION_SENTINEL}' in extracted PDF text -- "
            "depart_abbreviation regression"
        )

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into "
                "rendered PDF text -- trivial-blocks markup/code-mode "
                "regression"
            )


# ---------------------------------------------------------------------------
# Phase 13 (BLK-02/BLK-03): extend the GATE-01 render-gate pattern to prove
# visit_topic/visit_title's generalized buffer-swap (topic clue box,
# box-less contents pass-through) and visit_line_block/visit_line
# (verbatim linebreak() + nested indent) render correctly together in one
# combined fixture -- alongside the SC#3 admonition-title regression
# (including a multi-child inline-markup title, the Pitfall-1 fix).
# ---------------------------------------------------------------------------

# Sentinel tokens for the topic_line_block render gate -- distinctive,
# unlikely words chosen so their presence (or, for the outline-leak counts,
# exact single occurrence) in the extracted PDF text proves each handler
# behaved correctly. Must match the tokens embedded in
# topic_line_block_render_gate/index.rst.
TOPIC_BODY_SENTINEL = "TOPICBODYSENTINEL"
ADDRESS_LINE_ONE_SENTINEL = "ADDRESSLINEONE"
ADDRESS_LINE_TWO_SENTINEL = "ADDRESSLINETWO"
POEM_LINE_ONE_SENTINEL = "POEMLINEONE"
POEM_NESTED_ONE_SENTINEL = "POEMNESTEDONE"
POEM_NESTED_TWO_SENTINEL = "POEMNESTEDTWO"
POEM_LINE_THREE_SENTINEL = "POEMLINETHREE"


@pytest.fixture(scope="class")
def topic_line_block_render_gate_pdf_text(tmp_path_factory):
    """
    Build + real-compile the topic_line_block_render_gate fixture ONCE per
    class and return the pypdf-extracted PDF text.

    Class-scoped so the three thin test methods below (test_topic_*,
    test_line_block_*, test_admonition_title_regression_*) each assert a
    disjoint slice of the SAME real-compile artifact rather than re-running
    sphinx-build/typst.compile() three times. Depends only on
    `tmp_path_factory` (session-scoped-compatible) -- not on the
    function-scoped `topic_line_block_render_gate_dir`/`fixtures_dir`
    fixtures, to avoid a pytest ScopeMismatch (a class-scoped fixture may
    not depend on a narrower, function-scoped one).
    """
    source_dir = Path(__file__).parent / "fixtures" / "topic_line_block_render_gate"
    build_dir = tmp_path_factory.mktemp("topic_line_block_gate") / "_build"

    result = _run_sphinx_build_typst(source_dir, build_dir)
    assert (
        result.returncode == 0
    ), f"sphinx-build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"

    index_typ = build_dir / "index.typ"
    assert index_typ.exists(), "index.typ was not generated"

    # Compile the emitted .typ to PDF with typst-py, WITHOUT try/except:
    # this is the crux of GATE-01 -- any fatal (a level-0 heading, a
    # multi-child-title concatenation, leaked markup) aborts the ENTIRE
    # compile here and fails every dependent test method loudly, rather
    # than merely failing a string-agreement check.
    pdf_output = build_dir / "index.pdf"
    typst.compile(str(index_typ), output=str(pdf_output))

    assert pdf_output.exists(), "PDF file was not created"
    assert pdf_output.stat().st_size > 0, "PDF file is empty"
    with open(pdf_output, "rb") as f:
        magic = f.read(4)
        assert magic == b"%PDF", "Generated file is not a valid PDF"

    reader = pypdf.PdfReader(str(pdf_output))
    return "\n".join(page.extract_text() for page in reader.pages)


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class TestTopicLineBlockRenderGate:
    """
    Real-compile acceptance gate for BLK-02/BLK-03: visit_topic/
    depart_topic (clue box + box-less contents pass-through) and
    visit_line_block/visit_line (verbatim linebreak() + nested indent),
    plus the SC#3 admonition-title regression (including a multi-child
    title, Pitfall 1).

    Requirements: BLK-02, BLK-03, GATE-01 (13-CONTEXT.md D-01..D-06,
    13-RESEARCH.md Verified Mechanisms 1-3, 13-03-PLAN.md).

    All three test methods share the SAME real-compile artifact via the
    class-scoped `topic_line_block_render_gate_pdf_text` fixture above --
    sphinx-build/typst.compile() run exactly once per class, not once per
    test method.
    """

    def test_topic_and_contents_render_no_outline_leak(
        self, topic_line_block_render_gate_pdf_text
    ):
        """
        BLK-02 / SC#1: the topic title and the `.. contents::` title each
        appear EXACTLY ONCE in the extracted PDF text -- proof neither
        leaked into Typst's auto-generated outline as a real heading()
        would (a real heading() always populates the outline, which would
        make its title text appear a SECOND time as an outline entry).
        """
        full_text = topic_line_block_render_gate_pdf_text

        assert full_text.count("A Topic Title") == 1, (
            "Expected the topic title to appear exactly once in extracted "
            "PDF text (not duplicated into Typst's auto-outline) -- "
            "visit_topic/visit_title generalization regression"
        )
        assert TOPIC_BODY_SENTINEL in full_text, (
            f"Expected topic body sentinel '{TOPIC_BODY_SENTINEL}' in "
            "extracted PDF text -- visit_topic/depart_topic regression"
        )

        # D-05: contents-topic renders box-less, title + list intact, and
        # is likewise absent from the auto-outline.
        assert full_text.count("Table of Contents") == 1, (
            "Expected the '.. contents::' title to appear exactly once in "
            "extracted PDF text (bold label, not boxed, not duplicated "
            "into Typst's auto-outline) -- D-05 box-less pass-through "
            "regression"
        )

    def test_line_block_address_and_poem_breaks(
        self, topic_line_block_render_gate_pdf_text
    ):
        """
        BLK-03 / SC#2: address (flat) and poem (one level of nesting)
        line_block sentinels each appear as SEPARATE extracted-text lines
        -- proof a real linebreak() fired for every `line`, not merely a
        cosmetic source '\\n' (New-Pitfall-11-style proof, DESC-02
        precedent).
        """
        full_text = topic_line_block_render_gate_pdf_text

        for sentinel in (
            ADDRESS_LINE_ONE_SENTINEL,
            ADDRESS_LINE_TWO_SENTINEL,
            POEM_LINE_ONE_SENTINEL,
            POEM_NESTED_ONE_SENTINEL,
            POEM_NESTED_TWO_SENTINEL,
            POEM_LINE_THREE_SENTINEL,
        ):
            assert sentinel in full_text, (
                f"Expected line_block sentinel '{sentinel}' in extracted "
                "PDF text -- visit_line_block/visit_line regression"
            )

        concatenated_address = ADDRESS_LINE_ONE_SENTINEL + ADDRESS_LINE_TWO_SENTINEL
        assert concatenated_address not in full_text, (
            "The two address line_block sentinels were concatenated with "
            "no separator in extracted PDF text -- linebreak() did not "
            "produce a real visual break (New Pitfall 11 regression: a "
            "source '\\n' alone is cosmetic-only)"
        )

        concatenated_poem = POEM_LINE_ONE_SENTINEL + POEM_NESTED_ONE_SENTINEL
        assert concatenated_poem not in full_text, (
            "The poem line_block's flat and nested sentinels were "
            "concatenated with no separator in extracted PDF text -- "
            "nested linebreak()/h() did not produce a real visual break"
        )

    def test_admonitiontitleregression_multichild(
        self, topic_line_block_render_gate_pdf_text
    ):
        """
        SC#3 (regression): `.. note::`/`.. warning::`/a generic
        `.. admonition:: Custom *Title*` (a multi-child inline-markup
        title) all render correctly inside the same real-compile gate --
        the Pitfall-1 fix proof on the pre-existing admonition-title path,
        plus the LEAK_SIGNATURES negative control.

        Named `test_admonitiontitleregression_multichild` (no underscore
        between the three words) so it is selected verbatim by
        `-k AdmonitionTitleRegression` (13-VALIDATION.md's per-requirement
        command) -- pytest's `-k` performs a case-insensitive CONTIGUOUS
        substring match against the test node id, so an underscore-
        separated `admonition_title_regression` would NOT match the
        selector (verified empirically: underscores are literal
        characters that break substring contiguity, unlike the `Topic`/
        `LineBlock` selectors above which already match because the
        enclosing class name `TestTopicLineBlockRenderGate` contains
        those exact substrings contiguously).
        """
        full_text = topic_line_block_render_gate_pdf_text

        assert "ADMONITIONNOTESENTINEL" in full_text, (
            "Expected the note admonition body sentinel in extracted PDF "
            "text -- visit_note regression"
        )
        assert "ADMONITIONWARNINGSENTINEL" in full_text, (
            "Expected the warning admonition body sentinel in extracted "
            "PDF text -- visit_warning regression"
        )
        assert "Custom Title" in full_text, (
            "Expected the multi-child admonition title 'Custom Title' in "
            "extracted PDF text -- Pitfall-1 multi-child-title regression "
            "on the pre-existing generic admonition path"
        )
        assert "ADMONITIONCUSTOMSENTINEL" in full_text, (
            "Expected the generic admonition body sentinel in extracted "
            "PDF text -- visit_admonition regression"
        )

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into "
                "rendered PDF text -- topic/line_block markup/code-mode "
                "regression"
            )


# ---------------------------------------------------------------------------
# Phase 14 (FN-01, GATE-01): extend the render-gate pattern to prove the
# Plan 14-01 footnote pre-pass handlers (visit_document's id->node index,
# visit_footnote's SkipNode suppression, and visit_footnote_reference's
# definition/reuse emission) render correctly through a real
# sphinx-build -> typst.compile() -> pypdf round-trip -- single-reference
# (SC#1), double-reference no-duplication (SC#2), inline-markup body (SC#3),
# and footnote-inside-a-list-item (SC#4).
# ---------------------------------------------------------------------------

# Sentinel tokens for the footnote render gate -- distinctive, unlikely
# ALLCAPS-no-space words chosen so `full_text.count(...)` can prove each
# footnote's body reached the compiled PDF exactly once (guarding against
# the D-03 double-emission fatal). Must match the sentinel tokens embedded
# in footnote_render_gate/index.rst.
FOOTNOTE_SINGLE_SENTINEL = "FOOTNOTESINGLESENTINEL"
FOOTNOTE_DOUBLE_SENTINEL = "FOOTNOTEDOUBLESENTINEL"
FOOTNOTE_MARKUP_SENTINEL = "FOOTNOTEMARKUPSENTINEL"
FOOTNOTE_LIST_SENTINEL = "FOOTNOTELISTSENTINEL"


@pytest.fixture(scope="class")
def footnote_render_gate_pdf_text(tmp_path_factory):
    """
    Build + real-compile the footnote_render_gate fixture ONCE per class and
    return the pypdf-extracted PDF text.

    Class-scoped so the four thin test methods below (one per SC) each
    assert a disjoint slice of the SAME real-compile artifact rather than
    re-running sphinx-build/typst.compile() four times. Depends only on
    `tmp_path_factory` (session-scoped-compatible) -- not on a
    function-scoped fixtures-dir fixture, to avoid a pytest ScopeMismatch (a
    class-scoped fixture may not depend on a narrower, function-scoped one).
    """
    source_dir = Path(__file__).parent / "fixtures" / "footnote_render_gate"
    build_dir = tmp_path_factory.mktemp("footnote_gate") / "_build"

    result = _run_sphinx_build_typst(source_dir, build_dir)
    assert (
        result.returncode == 0
    ), f"sphinx-build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"

    index_typ = build_dir / "index.typ"
    assert index_typ.exists(), "index.typ was not generated"

    # Compile the emitted .typ to PDF with typst-py, WITHOUT try/except:
    # this is the crux of GATE-01 -- any fatal (a leaked bodyless/duplicate-
    # label footnote call, a missing statement separator) aborts the ENTIRE
    # compile here and fails every dependent test method loudly, rather than
    # merely failing a string-agreement check. This is the verification that
    # the Plan 14-01 D-08 dangling-refid guard and D-03 emitted-ids set()
    # gate hold under a real compile.
    pdf_output = build_dir / "index.pdf"
    typst.compile(str(index_typ), output=str(pdf_output))

    assert pdf_output.exists(), "PDF file was not created"
    assert pdf_output.stat().st_size > 0, "PDF file is empty"
    with open(pdf_output, "rb") as f:
        magic = f.read(4)
        assert magic == b"%PDF", "Generated file is not a valid PDF"

    reader = pypdf.PdfReader(str(pdf_output))
    return "\n".join(page.extract_text() for page in reader.pages)


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class TestFootnoteRenderGate:
    """
    Real-compile acceptance gate for FN-01: visit_document's id->node
    pre-pass index, visit_footnote's SkipNode suppression, and
    visit_footnote_reference's definition/reuse emission.

    Requirements: FN-01, GATE-01 (14-CONTEXT.md D-01..D-09, 14-RESEARCH.md
    Verified Mechanisms 1-3, 14-02-PLAN.md).

    All four test methods share the SAME real-compile artifact via the
    class-scoped `footnote_render_gate_pdf_text` fixture above --
    sphinx-build/typst.compile() run exactly once per class, not once per
    test method.
    """

    def test_single_reference_body_once(self, footnote_render_gate_pdf_text):
        """
        SC#1: a footnote referenced ONCE renders its body sentinel EXACTLY
        ONCE in the extracted PDF text -- no floating body left at the
        docutils definition location.
        """
        full_text = footnote_render_gate_pdf_text

        assert full_text.count(FOOTNOTE_SINGLE_SENTINEL) == 1, (
            f"Expected single-reference footnote body sentinel "
            f"'{FOOTNOTE_SINGLE_SENTINEL}' to appear exactly once in "
            "extracted PDF text -- visit_footnote_reference regression"
        )

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into "
                "rendered PDF text -- footnote markup/code-mode regression"
            )

    def test_double_reference_body_not_duplicated(self, footnote_render_gate_pdf_text):
        """
        SC#2: a footnote referenced from TWO paragraphs renders a marker at
        both sites while its body sentinel appears exactly once -- the
        second citation reuses the placed note by label (D-03), it does not
        duplicate the body.
        """
        full_text = footnote_render_gate_pdf_text

        assert full_text.count(FOOTNOTE_DOUBLE_SENTINEL) == 1, (
            f"Expected double-reference footnote body sentinel "
            f"'{FOOTNOTE_DOUBLE_SENTINEL}' to appear exactly once in "
            "extracted PDF text (not duplicated by the reuse citation) -- "
            "D-03 set()-gated reuse-form regression"
        )
        assert (
            full_text.count("A footnote referenced from this first paragraph") == 1
        ), (
            "Expected the double-reference SC#2 first citing paragraph "
            "exactly once in extracted PDF text"
        )
        assert (
            full_text.count(
                "A second, separate paragraph citing the very same footnote again"
            )
            == 1
        ), (
            "Expected the double-reference SC#2 second citing paragraph "
            "exactly once in extracted PDF text -- both citation sites must "
            "be present even though the body renders only once"
        )

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into "
                "rendered PDF text -- footnote markup/code-mode regression"
            )

    def test_body_inline_markup_and_special_chars(self, footnote_render_gate_pdf_text):
        """
        SC#3: a footnote body containing `emph`/`literal` and markup-special
        characters (`@ # $ _ * < >`) renders correctly in the compiled
        PDF -- proof the buffer-swap through the normal visitor chain
        preserved inline markup and escaping.
        """
        full_text = footnote_render_gate_pdf_text

        assert FOOTNOTE_MARKUP_SENTINEL in full_text, (
            f"Expected inline-markup footnote body sentinel "
            f"'{FOOTNOTE_MARKUP_SENTINEL}' in extracted PDF text -- "
            "visit_footnote_reference buffer-swap regression"
        )
        assert "emphasis" in full_text, (
            "Expected the *emphasis* footnote-body content in extracted "
            "PDF text -- buffer-swap inline-markup regression"
        )
        assert "literal" in full_text, (
            "Expected the ``literal`` footnote-body content in extracted "
            "PDF text -- buffer-swap inline-markup regression"
        )
        assert "@ # $ _ * < >" in full_text, (
            "Expected the markup-special-character footnote-body content "
            "'@ # $ _ * < >' in extracted PDF text -- buffer-swap escaping "
            "regression"
        )

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into "
                "rendered PDF text -- footnote markup/code-mode regression"
            )

    def test_footnote_inside_list_item(self, footnote_render_gate_pdf_text):
        """
        SC#4: a footnote cited from inside a bullet-list item compiles
        cleanly and its body sentinel is present.
        """
        full_text = footnote_render_gate_pdf_text

        assert FOOTNOTE_LIST_SENTINEL in full_text, (
            f"Expected list-item footnote body sentinel "
            f"'{FOOTNOTE_LIST_SENTINEL}' in extracted PDF text -- "
            "footnote-inside-list-item regression"
        )

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into "
                "rendered PDF text -- footnote markup/code-mode regression"
            )


# ---------------------------------------------------------------------------
# GATE-02 corpus fatal #14 (Phase 15): codly's @preview 1.3.0 codly()
# function has no `start` parameter -- typsphinx emitted `codly(start: N)`
# for :linenos: code blocks with a known Sphinx `linenostart`, which
# codly 1.3.0 rejects with `TypstError: unexpected argument: start`. The
# correct parameter is `offset` (an additive delta: displayed number =
# line.number + offset, so offset = linenostart - 1). Sphinx's
# LiteralInclude directive always populates highlight_args['linenostart']
# (defaulting to 1) even without an explicit :lineno-start: option, so the
# fix also guards against emitting a spurious offset:0 call for that
# default case. This is a FAST (non-slow, offline) render gate -- no
# network/corpus dependency, following the TestAdmonitionPdfRenderGate
# pattern above rather than the @pytest.mark.slow GATE-01 pattern.
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the codly offset render gate",
)
class TestCodlyOffsetRenderGate:
    """
    Real-compile acceptance gate for the codly `start:` -> `offset:`
    API-mismatch fix (GATE-02 corpus fatal #14).

    Requirements: GATE-02 (15-CONTEXT.md), Issue #31 (:lineno-start:).
    """

    def test_codly_offset_pdf_compiles_and_uses_offset_not_start(
        self, fixtures_dir, temp_build_dir
    ):
        """
        Compile the codly_offset_render_gate fixture (an explicit
        :lineno-start: 5 code-block, a plain :linenos: code-block, and a
        plain :linenos: literalinclude -- the exact construct that produced
        20 fatal occurrences in the real Sphinx doc/ corpus) to PDF and
        confirm: (1) the emitted .typ source uses `codly(offset: ...)`,
        never the removed `codly(start: ...)`; (2) no spurious offset call
        is emitted for the default linenostart=1 case; (3) typst.compile()
        succeeds (no `unexpected argument: start` TypstError) and all three
        code blocks' content reaches the extracted PDF text.
        """
        source_dir = fixtures_dir / "codly_offset_render_gate"

        result = _run_sphinx_build_typst(source_dir, temp_build_dir)
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"

        typ_source = index_typ.read_text(encoding="utf-8")

        # Source-level check: the removed `start:` parameter must never be
        # emitted, and the explicit :lineno-start: 5 block must emit the
        # correct offset (5 - 1 = 4).
        assert "codly(start:" not in typ_source, (
            "codly 1.3.0 has no `start` parameter -- emitting it causes "
            "'TypstError: unexpected argument: start'"
        )
        assert "codly(offset: 4)" in typ_source, (
            "Expected codly(offset: 4) for the :lineno-start: 5 code-block "
            "(offset = linenostart - 1)"
        )

        # The plain :linenos: code-block (no explicit :lineno-start:) never
        # populates highlight_args['linenostart'] in Sphinx, so it must not
        # emit any offset call either.
        #
        # The literalinclude block DOES get linenostart=1 from Sphinx by
        # default -- this must be guarded against emitting `codly(offset: 0)`
        # (or the removed `codly(start: 1)`), matching codly's own default.
        assert "codly(offset: 0)" not in typ_source, (
            "linenostart=1 (the default) must not emit a spurious "
            "codly(offset: 0) call"
        )

        # 2. Compile the emitted .typ to PDF with typst-py, WITHOUT
        # try/except: a leaked codly(start:...) call must abort the compile
        # here and fail the test loudly (this is the crux of the fatal).
        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(index_typ), output=str(pdf_output))

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        # 3. Extract text with pypdf and confirm all three code blocks'
        # content reached the compiled PDF.
        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        for sentinel in (
            "CODLYEXPLICITSTARTSENTINEL",
            "CODLYPLAINLINENOSSENTINEL",
            "CODLYLITERALINCLUDESENTINEL",
        ):
            assert sentinel in full_text, (
                f"Expected code-block sentinel '{sentinel}' in extracted " "PDF text"
            )

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into "
                "rendered PDF text -- codly markup/code-mode regression"
            )


# ---------------------------------------------------------------------------
# GATE-02 corpus fatal #15 (Phase 15): visit_block_quote emitted the
# markup-mode trailing content block `quote[ ... ]`, but every body child is
# a code-mode function call (par({text(...)}), raw(...), link(...)). Inside a
# markup `[...]` block those bytes are treated as LITERAL PROSE, so a lone
# markup-special char in a child string literal -- e.g. the `_` in an inline
# literal ``_t`` (Sphinx's `_t` static-template suffix) -- opens a stray
# inline-emphasis span that never closes and aborts the whole compile with
# `TypstError: unclosed delimiter`. The fix emits a CODE-MODE body,
# quote(block: true, { ... }), where the children are real function calls and
# their string-literal chars are inert. This is a FAST (non-slow, offline)
# render gate -- no network/corpus dependency, following the
# TestAdmonitionPdfRenderGate / TestCodlyOffsetRenderGate pattern.
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the block-quote render gate",
)
class TestBlockQuoteMarkupModeRenderGate:
    """
    Real-compile acceptance gate for the block-quote markup-mode ->
    code-mode body fix (GATE-02 corpus fatal #15).

    Requirements: GATE-02 (15-CONTEXT.md). Composes with bug #11 (the
    block-quote list-item leading separator) and the attribution handler.
    """

    def test_block_quote_pdf_compiles_with_markup_special_body(
        self, fixtures_dir, temp_build_dir
    ):
        """
        Compile the block_quote_markup_render_gate fixture (a plain block
        quote, a block quote nested inside a list item, and a block quote
        with an attribution -- each carrying an inline literal ``_t`` whose
        lone underscore would open a stray emphasis span in markup mode) to
        PDF and confirm:

        - (source) each block quote is emitted as the code-mode
          ``quote(block: true, { ... })`` body form, never the markup-mode
          ``quote[par(`` / ``quote[`` form -- the exact fatal shape;
        - (source) bug #11's list-item leading separator still fires: the
          list-item lead-in text and the following ``quote(block: true, {``
          are newline-separated, never juxtaposed;
        - (source) the attribution is appended as a CODE-MODE named argument
          on the same quote() call: ``}, attribution: {`` (never the
          markup-mode ``}, attribution: [``, whose code-mode children Typst
          typesets as literal prose);
        - typst.compile() succeeds (no ``unclosed delimiter`` TypstError)
          and every block quote's body sentinel reaches the extracted PDF
          text, the attribution renders as the clean ``-- Author`` prose form
          (NOT a leaked ``text("Author")``/typeset ``text(“Author”)``
          wrapper), and no leak signature -- straight OR curly quoted --
          appears (proof the ``_t`` literal AND the attribution children
          rendered as prose, not leaked Typst source).
        """
        source_dir = fixtures_dir / "block_quote_markup_render_gate"

        result = _run_sphinx_build_typst(source_dir, temp_build_dir)
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"

        typ_source = index_typ.read_text(encoding="utf-8")

        # Source-level: the markup-mode trailing content block form must never
        # be emitted -- inside `[...]` the code-mode par()/raw() children are
        # literal prose and a lone markup-special char aborts the compile.
        assert "quote[par(" not in typ_source, (
            "Block quote emitted the markup-mode quote[par(...] form -- inside "
            "markup the code-mode children are literal prose and a lone "
            "markup-special char opens an unclosed emphasis span (fatal #15)"
        )
        # ...and the code-mode body form must be present (three block quotes).
        assert typ_source.count("quote(block: true, {") == 3, (
            "Expected three code-mode quote(block: true, {...}) block quotes "
            f"in the generated source:\n{typ_source}"
        )

        # bug #11 interaction: the block quote inside the list item must NOT
        # juxtapose the preceding list-item lead-in text -- the leading
        # separator must keep them apart.
        assert (
            'text(" helpers BLOCKQUOTELISTSENTINEL:")quote(block: true, {'
            not in typ_source
        ), (
            "The list-item block quote juxtaposes the preceding lead-in text "
            "with NO separator -- bug #11's list-item separator regressed"
        )
        assert re.search(
            r"BLOCKQUOTELISTSENTINEL:\"\)\s*\nquote\(block: true, \{",
            typ_source,
        ), (
            "Expected a newline separator between the list-item lead-in text "
            "and the following block quote -- bug #11's list-item separator "
            "did not fire"
        )

        # The attribution must be appended as a CODE-MODE named argument on the
        # same quote() call (positional body first, then named attribution),
        # where its inline children are evaluated function calls. The
        # markup-mode `}, attribution: [` form must NEVER be emitted: inside a
        # markup `[...]` argument the code-mode children (text(...)/emph({...})/
        # raw(...)) are literal prose that Typst typesets verbatim (the
        # attribution source-leak) and a lone markup-special char aborts the
        # compile.
        assert "}, attribution: {" in typ_source, (
            "The block-quote attribution was not appended as a CODE-MODE named "
            "argument on the quote() call (`}, attribution: {`)"
        )
        assert "}, attribution: [" not in typ_source, (
            "The block-quote attribution was emitted as the markup-mode "
            "`}, attribution: [` argument -- its code-mode children are literal "
            "prose there (the attribution source-leak regression)"
        )

        # Compile the emitted .typ to PDF with typst-py, WITHOUT try/except:
        # a leaked markup-mode quote[...] body with the ``_t`` literal aborts
        # the compile here with `unclosed delimiter` -- the crux of the fatal.
        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(index_typ), output=str(pdf_output))

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        for sentinel in (
            "BLOCKQUOTEPLAINSENTINEL",
            "BLOCKQUOTELISTSENTINEL",
            "BLOCKQUOTEATTRSENTINEL",
        ):
            assert sentinel in full_text, (
                f"Expected block-quote body sentinel '{sentinel}' in "
                "extracted PDF text -- block-quote render regression"
            )
        # The attribution author must render as CLEAN PROSE on the em-dash
        # attribution line -- `— William Shakespeare` -- NOT wrapped in a
        # leaked `text(...)` call. A bare `"William Shakespeare" in full_text`
        # substring check is a BLIND SPOT: it is trivially true even when the
        # attribution leaked as `— text(“William Shakespeare”)`,
        # since the author name is a substring of that wrapper. Asserting the
        # exact em-dash + author line form rejects the leaked wrapper (the
        # leaked line reads `— text(“William...`, so the clean form is
        # absent), and the explicit wrapper checks below name the exact leak.
        assert "— William Shakespeare" in full_text, (
            "The block-quote attribution did not render as the clean prose form "
            "'— William Shakespeare' -- its inline child leaked as literal "
            f"source (attribution markup/code-mode regression):\n{full_text}"
        )
        for wrapper in ('text("William Shakespeare', "text(“William Shakespeare"):
            assert wrapper not in full_text, (
                f"The attribution author leaked wrapped in '{wrapper}...' -- the "
                "inline child was emitted as literal Typst source, not "
                f"evaluated content:\n{full_text}"
            )

        # Leak-signature sweep. Typst applies smart-quote typography, so a
        # leaked `text("...")` is TYPESET as `text(“...”)` in the
        # extracted PDF -- the straight-quote LEAK_SIGNATURES alone are a BLIND
        # SPOT for an attribution leak (which is exactly why the original test
        # false-passed). Sweep BOTH the straight-quote signatures AND the
        # curly-quote / bare function-call forms the attribution children would
        # typeset into.
        hardened_leak_signatures = LEAK_SIGNATURES + (
            "text(“",
            "raw(“",
            "emph(",
        )
        for leaked_token in hardened_leak_signatures:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into rendered "
                "PDF text -- block-quote markup/code-mode regression (the "
                "``_t`` body literal AND the attribution children must render "
                f"as prose, not leaked source):\n{full_text}"
            )


# ---------------------------------------------------------------------------
# Per-block codly config leak (captioned code block) + codly-range invalid-API
# fatal. Two related defects string-agreement tests never caught (they never
# real-compiled): (1) in a captioned code block, emitted as the MARKUP form
# `figure(caption: [...])[ ... ]`, a bare `codly(number-format: none)` /
# highlight call is typeset as LITERAL PROSE -- leaking the config text and
# never applying the highlight (the corpus bug). (2) The highlight call was
# `codly-range(highlight: (...))`, which is not a codly 1.3.0 API:
# `codly-range(start, end)` displays a line range and needs a positional
# `start`, so the call aborts the compile with `missing argument: start` the
# instant it executes (in ANY code-mode context -- top level, admonition,
# list). The fix (a) `#`-prefixes the config in markup context so Typst
# executes it, and (b) replaces codly-range with the correct
# `codly(highlights: ((line: N, start: 1, end: none, fill: ...), ...))` API.
# FAST (non-slow, offline) render gate, following the TestCodlyOffsetRenderGate
# / TestBlockQuoteMarkupModeRenderGate pattern.
# ---------------------------------------------------------------------------

# codly-config tokens that must NEVER reach the extracted PDF prose -- each is
# a per-block config call that must be EXECUTED (invisible), not typeset. The
# fixture's own descriptive prose deliberately avoids naming these so this
# sweep is unambiguous.
CODLY_CONFIG_LEAK_SIGNATURES = (
    "codly(",
    "codly-range(",
    "number-format",
    "highlights:",
    "highlight:",
)


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the codly config leak render gate",
)
class TestCodlyConfigLeakRenderGate:
    """
    Real-compile acceptance gate for the per-block codly-config markup/
    code-mode leak (captioned code block) and the codly-range invalid-API
    compile fatal.

    Requirements: GATE-02 class ("code-mode function call leaks as text"),
    Sphinx :emphasize-lines: / :caption: support.
    """

    def test_codly_config_executed_not_leaked_and_highlight_valid(
        self, fixtures_dir, temp_build_dir
    ):
        """
        Compile the codly_config_leak_render_gate fixture (a captioned code
        block with :emphasize-lines: -- the MARKUP-context corpus bug -- and a
        plain top-level code block with :emphasize-lines: -- the code-mode
        codly-range compile-fatal) to PDF and confirm:

        - (source) the invalid ``codly-range(`` API is NEVER emitted;
        - (source) the captioned block's config is emitted as EXECUTED markup
          calls ``#codly(number-format: none)`` and ``#codly(highlights: ...)``
          (with the leading ``#``), never bare;
        - (source) the top-level block's highlight is the bare code-mode
          ``codly(highlights: ...)`` call (no ``#`` inside ``#{ ... }``);
        - typst.compile() succeeds (no ``missing argument: start`` TypstError);
        - no codly-config token (``codly(`` / ``codly-range(`` /
          ``number-format`` / ``highlights:`` / ``highlight:``) leaks into the
          extracted PDF prose, and no LEAK_SIGNATURES token appears;
        - every code-block sentinel reaches the compiled PDF.
        """
        source_dir = fixtures_dir / "codly_config_leak_render_gate"

        result = _run_sphinx_build_typst(source_dir, temp_build_dir)
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"

        typ_source = index_typ.read_text(encoding="utf-8")

        # The removed invalid API must never be emitted anywhere.
        assert "codly-range(" not in typ_source, (
            "codly 1.3.0 has no codly-range(highlight: ...) API -- "
            "codly-range(start, end) requires a positional `start` and aborts "
            "the compile with 'missing argument: start' when executed"
        )

        # Captioned (markup) context: the config must be EXECUTED with a
        # leading `#`, or it leaks as literal prose inside figure(...)[...].
        assert "figure(caption:" in typ_source, (
            "Expected the captioned code block to emit a figure(caption: ...) "
            "wrapper -- fixture/handler regression"
        )
        assert "#codly(number-format: none)" in typ_source, (
            "The captioned code block's number-format config was not emitted "
            "as an executed markup call (#codly(...)) -- it would leak as "
            "literal prose inside figure(...)[...]"
        )
        assert "#codly(highlights: ((line: 2, start: 1, end: none," in typ_source, (
            "The captioned code block's emphasize-lines highlight was not "
            "emitted as an executed markup call (#codly(highlights: ...)) with "
            "the correct codly(highlights: ...) API"
        )

        # Top-level (code-mode) context: the highlight is the bare
        # codly(highlights: ...) call -- a `#`-prefixed call would be invalid
        # inside the document's `#{ ... }` code block.
        assert "\ncodly(highlights: ((line: 3, start: 1, end: none," in typ_source, (
            "The top-level code block's emphasize-lines highlight was not "
            "emitted as the bare code-mode codly(highlights: ...) call"
        )

        # Compile the emitted .typ to PDF with typst-py, WITHOUT try/except:
        # before the fix the top-level codly-range(highlight: ...) call aborted
        # the ENTIRE compile here with 'missing argument: start' -- this is the
        # must-fail-until-fixed guard for the invalid-API fatal.
        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(index_typ), output=str(pdf_output))

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        # Every code-block sentinel must reach the compiled PDF.
        for sentinel in (
            "CODLYCAPFIRSTSENTINEL",
            "CODLYCAPEMPHSENTINEL",
            "CODLYCAPTHIRDSENTINEL",
            "CODLYTOPFIRSTSENTINEL",
            "CODLYTOPSECONDSENTINEL",
            "CODLYTOPEMPHSENTINEL",
        ):
            assert sentinel in full_text, (
                f"Expected code-block sentinel '{sentinel}' in extracted PDF "
                "text -- codly config leak render regression"
            )

        # No codly-config token may leak into the rendered prose (the exact
        # captioned-block corpus symptom), and no generic LEAK_SIGNATURES form.
        for leaked_token in CODLY_CONFIG_LEAK_SIGNATURES + LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"codly-config token '{leaked_token}' leaked into rendered PDF "
                "text -- the per-block config must be EXECUTED, not typeset as "
                f"literal prose (captioned markup/code-mode regression):\n{full_text}"
            )


# ---------------------------------------------------------------------------
# Phase 16 (TODO-01, GATE-01): extend the GATE-01 render-gate pattern to
# prove visit_todo_node/depart_todo_node -- a `.. todo::` body renders inside
# a gentle-clues task() box titled "Todo" in the compiled PDF when
# todo_include_todos=True (D-01), gated on config.todo_include_todos exactly
# like every official Sphinx builder (planner decision per 16-RESEARCH.md
# Open Question 1 / Assumption A2). Before the handler exists, todo_node is
# silently unknown_visit-dropped with an "unknown node type" warning -- this
# is the TODO-01 corpus symptom (x10).
# ---------------------------------------------------------------------------


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class TestTodoRenderGate:
    """
    Real-compile acceptance gate for TODO-01: visit_todo_node/
    depart_todo_node rendering as a gentle-clues task() box titled "Todo",
    gated on config.todo_include_todos.

    Requirements: TODO-01, GATE-01 (16-CONTEXT.md, 16-RESEARCH.md D-01/D-01a,
    16-01-PLAN.md).
    """

    def test_todo_pdf_renders_body_and_title(
        self, todo_render_gate_dir, temp_build_dir
    ):
        """
        Compile the todo_render_gate fixture (todo_include_todos=True, the
        fixture's own default) to PDF and confirm, via the generated .typ
        source and real pypdf text-extraction:
        - no "unknown node type" warning on stderr (the TODO-01 warning is
          eliminated);
        - the emitted .typ source contains the task() clue's code-mode open
          ("task({");
        - typst.compile() succeeds;
        - the body sentinel and the box title ("Todo", exactly once --
          sourced only from the node's own dynamic title child, per
          16-RESEARCH.md Pitfall 2) both reach the extracted PDF text;
        - no LEAK_SIGNATURES token leaked into the rendered PDF text.
        """
        result = _run_sphinx_build_typst(todo_render_gate_dir, temp_build_dir)
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "unknown node type" not in result.stderr, (
            "Expected no 'unknown node type' warning on stderr -- the "
            f"TODO-01 warning should be eliminated:\n{result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"
        typ_source = index_typ.read_text(encoding="utf-8")

        assert "task({" in typ_source, (
            "Expected the task() clue's code-mode content-block open "
            "('task({') in the generated Typst source -- "
            "visit_todo_node/_visit_admonition regression"
        )

        # Compile the emitted .typ to PDF with typst-py, WITHOUT try/except:
        # this is the crux of the test -- any invalid Typst source emitted
        # by visit_todo_node would abort the compile here.
        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(index_typ), output=str(pdf_output))

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        assert TODO_BODY_SENTINEL in full_text, (
            f"Expected todo body sentinel '{TODO_BODY_SENTINEL}' in "
            "extracted PDF text -- visit_todo_node/depart_todo_node "
            "regression"
        )
        assert full_text.count("Todo") == 1, (
            "Expected the box title 'Todo' to appear exactly once in "
            "extracted PDF text (from the node's own dynamic title child) "
            f"-- fixture contains no other 'Todo' source:\n{full_text}"
        )

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into "
                "rendered PDF text -- todo markup/code-mode regression"
            )

    def test_todo_typ_omits_body_when_todo_include_todos_false(
        self, todo_render_gate_dir, temp_build_dir
    ):
        """
        Build the SAME fixture with -D todo_include_todos=0 (the Sphinx
        default False) and confirm the generated .typ contains neither the
        body sentinel nor a task( call -- mirroring every official Sphinx
        builder's SkipNode gating (16-RESEARCH.md A2). No compile needed --
        absence is a .typ-level proof; test_todo_pdf_renders_body_and_title
        owns the compile.

        This is a permanent regression guard for the internal-work-notes
        prohibition (T-16-01): draft `.. todo::` content must never leak
        into published output when todo_include_todos is False.
        """
        result = _run_sphinx_build_typst(
            todo_render_gate_dir,
            temp_build_dir,
            extra_args=("-D", "todo_include_todos=0"),
        )
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "unknown node type" not in result.stderr, (
            "Expected no 'unknown node type' warning on stderr even when "
            f"todo_include_todos is False:\n{result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"
        typ_source = index_typ.read_text(encoding="utf-8")

        assert TODO_BODY_SENTINEL not in typ_source, (
            f"Todo body sentinel '{TODO_BODY_SENTINEL}' leaked into "
            "generated Typst source with todo_include_todos=False -- "
            "internal work-notes must never leak into published output "
            "(T-16-01)"
        )
        assert "task({" not in typ_source, (
            "Found the task() clue's code-mode open in generated Typst "
            "source with todo_include_todos=False -- the "
            "config.todo_include_todos SkipNode gate regressed"
        )


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class TestManpageRenderGate:
    """
    Real-compile acceptance gate for MAN-01: visit_manpage/depart_manpage
    delegating to visit_emphasis/depart_emphasis so the :manpage: role
    renders its literal page-reference text italic, in all three
    separator/mode contexts a manpage role can appear in.

    Requirements: MAN-01, GATE-01 (16-CONTEXT.md D-02/D-02a,
    16-RESEARCH.md Pattern 2 / Pitfall 4, 16-02-PLAN.md).
    """

    def test_manpage_pdf_renders_italic_text(
        self, manpage_render_gate_dir, temp_build_dir
    ):
        """
        Compile the manpage_render_gate fixture to PDF and confirm, via the
        generated .typ source and real pypdf text-extraction:
        - no "unknown node type" warning on stderr (the MAN-01 warning is
          eliminated);
        - the emitted .typ source contains exactly 3 emph({ wrappers (one
          per :manpage: use -- the fixture contains no other emphasis
          source) and no link( (D-02a: no linkification);
        - typst.compile() succeeds without try/except (proving the mode
          toggle/separator state machine is correct in all three contexts:
          paragraph, list item, figure caption);
        - "ls(1)", "grep(1)", and "tar(1)" each appear in the extracted PDF
          text;
        - no LEAK_SIGNATURES token leaked into the rendered PDF text.
        """
        result = _run_sphinx_build_typst(manpage_render_gate_dir, temp_build_dir)
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "unknown node type" not in result.stderr, (
            "Expected no 'unknown node type' warning on stderr -- the "
            f"MAN-01 warning should be eliminated:\n{result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"
        typ_source = index_typ.read_text(encoding="utf-8")

        assert typ_source.count("emph({") == 3, (
            "Expected exactly 3 emph({ wrappers in the generated Typst "
            "source (one per :manpage: use) -- visit_manpage/depart_manpage "
            f"regression; got {typ_source.count('emph({')}"
        )
        assert "link(" not in typ_source, (
            "Found a link( call in generated Typst source -- D-02a "
            "prohibits linkification; the fixture has no manpages_url "
            "configured and contains no references, so any link( is a "
            "fabricated URL"
        )

        # Compile the emitted .typ to PDF with typst-py, WITHOUT try/except:
        # this is the crux of the test -- any invalid Typst source emitted
        # by visit_manpage (e.g. a mishandled mode toggle inside the figure
        # caption's markup-mode context) would abort the compile here.
        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(index_typ), output=str(pdf_output))

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        for manpage_text in ("ls(1)", "grep(1)", "tar(1)"):
            assert manpage_text in full_text, (
                f"Expected manpage text '{manpage_text}' in extracted PDF "
                "text -- visit_manpage/depart_manpage regression"
            )

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into "
                "rendered PDF text -- manpage delegation regression"
            )


# ---------------------------------------------------------------------------
# Phase 16 (LEN-01, GATE-01): extend the GATE-01 render-gate pattern to prove
# the figwidth wiring in visit_figure/depart_figure -- a :figwidth: length
# now routes through the single shared _convert_length_to_typst() helper and
# wraps the whole figure() call in a block(width: ...)[...] wrapper (Typst's
# figure() rejects a direct width: kwarg -- 16-RESEARCH.md Pitfall 3). Before
# this wiring, :figwidth: was silently ignored (no wrapper, no warning).
# ---------------------------------------------------------------------------


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class TestFigureFigwidthRenderGate:
    """
    Real-compile acceptance gate for LEN-01: the visit_figure/depart_figure
    :figwidth: wiring through _convert_length_to_typst(), wrapped in the
    verified-by-real-compile block(width: ...)[#figure(...)] shape.

    Requirements: LEN-01, GATE-01 (16-RESEARCH.md Pitfall 3, 16-03-PLAN.md).
    """

    def test_figwidth_pdf_wraps_block_and_compiles(
        self, figure_length_render_gate_dir, temp_build_dir
    ):
        """
        Compile the (extended) figure_length_render_gate fixture to PDF and
        confirm, via the generated .typ source and stderr:
        - the 400px :figwidth: case wraps block(width: 300pt)[#figure( (the
          exact CSS-canonical 0.75 px->pt ratio);
        - the 75% :figwidth: case wraps block(width: 75%)[#figure( (pass
          through unchanged);
        - neither the raw "5ex" unit nor the raw "400px" unit ever reaches
          the generated Typst source;
        - exactly 2 "Unsupported length unit" warnings fire on stderr (the
          pre-existing :width: 1ex image case + the new :figwidth: 5ex
          case) -- proving no double-conversion at the new call site;
        - typst.compile() succeeds without try/except.
        """
        result = _run_sphinx_build_typst(figure_length_render_gate_dir, temp_build_dir)
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"
        typ_source = index_typ.read_text(encoding="utf-8")

        assert "block(width: 300pt)[#figure(" in typ_source, (
            "Expected the :figwidth: 400px case to wrap "
            "'block(width: 300pt)[#figure(' in the generated Typst source -- "
            "visit_figure figwidth wiring regression"
        )
        assert "block(width: 75%)[#figure(" in typ_source, (
            "Expected the :figwidth: 75% case to wrap "
            "'block(width: 75%)[#figure(' in the generated Typst source -- "
            "visit_figure figwidth wiring regression"
        )
        assert "5ex" not in typ_source, (
            "Raw unconverted 'ex' unit leaked into generated Typst source "
            "from the :figwidth: 5ex case"
        )
        assert "400px" not in typ_source, (
            "Raw unconverted 'px' unit leaked into generated Typst source "
            "from the :figwidth: 400px case"
        )

        assert result.stderr.count("Unsupported length unit") == 2, (
            "Expected exactly 2 'Unsupported length unit' warnings (the "
            "pre-existing :width: 1ex image case + the new :figwidth: 5ex "
            f"case):\n{result.stderr}"
        )

        # Compile the emitted .typ to PDF with typst-py, WITHOUT try/except:
        # a mismatched block(width: ...)[...] wrapper would abort the
        # compile here (Pitfall 3).
        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(index_typ), output=str(pdf_output))

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"


# ---------------------------------------------------------------------------
# Phase 16 (LEN-01, GATE-01): extend the GATE-01 render-gate pattern to prove
# the width wiring in depart_table -- a :width: length on .. table::/
# .. csv-table::/.. list-table:: (all converging on the single nodes.table
# type via Table.set_table_width()) now routes through
# _convert_length_to_typst() and wraps the whole table() call in a
# block(width: ...)[#table(...)] wrapper (Typst's table() also rejects a
# direct width: kwarg -- 16-RESEARCH.md Pitfall 3).
# ---------------------------------------------------------------------------

# Sentinel tokens for the table-width render gate -- distinctive, unlikely
# words chosen so their presence in the extracted PDF text proves each
# table's content reached the compiled PDF, inside or without the width
# wrapper. Must match the sentinel tokens embedded in
# table_width_render_gate/index.rst.
TABLEPXSENTINEL7Q4 = "TABLEPXSENTINEL7Q4"
TABLELISTSENTINEL8Q5 = "TABLELISTSENTINEL8Q5"
TABLECSVSENTINEL9Q6 = "TABLECSVSENTINEL9Q6"


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class TestTableWidthRenderGate:
    """
    Real-compile acceptance gate for LEN-01: the depart_table :width: wiring
    through _convert_length_to_typst(), covering .. table::/.. csv-table::/
    .. list-table:: uniformly through the single nodes.table type, wrapped
    in the verified-by-real-compile block(width: ...)[#table(...)] shape.

    Requirements: LEN-01, GATE-01 (16-RESEARCH.md Pitfall 3, 16-03-PLAN.md).
    """

    def test_table_width_pdf_wraps_block_and_compiles(
        self, table_width_render_gate_dir, temp_build_dir
    ):
        """
        Compile the table_width_render_gate fixture to PDF and confirm, via
        the generated .typ source, stderr, and real pypdf text-extraction:
        - the .. table:: :width: 200px case wraps
          block(width: 150pt)[#table( (the CSS-canonical 0.75 px->pt ratio);
        - the .. list-table:: :width: 50% case wraps
          block(width: 50%)[#table( (pass through unchanged);
        - neither the raw "1ex" unit nor the raw "200px" unit ever reaches
          the generated Typst source;
        - exactly 1 "Unsupported length unit" warning fires on stderr (the
          .. csv-table:: :width: 1ex case, warn-and-drop, no wrapper);
        - typst.compile() succeeds without try/except;
        - all three sentinel tokens (proving the table content itself
          renders, inside or without the wrapper) reach the extracted PDF
          text, with no LEAK_SIGNATURES token present.
        """
        result = _run_sphinx_build_typst(table_width_render_gate_dir, temp_build_dir)
        assert result.returncode == 0, (
            f"sphinx-build failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        index_typ = temp_build_dir / "index.typ"
        assert index_typ.exists(), "index.typ was not generated"
        typ_source = index_typ.read_text(encoding="utf-8")

        assert "block(width: 150pt)[#table(" in typ_source, (
            "Expected the .. table:: :width: 200px case to wrap "
            "'block(width: 150pt)[#table(' in the generated Typst source -- "
            "depart_table width wiring regression"
        )
        assert "block(width: 50%)[#table(" in typ_source, (
            "Expected the .. list-table:: :width: 50% case to wrap "
            "'block(width: 50%)[#table(' in the generated Typst source -- "
            "depart_table width wiring regression"
        )
        assert "1ex" not in typ_source, (
            "Raw unconverted 'ex' unit leaked into generated Typst source "
            "from the .. csv-table:: :width: 1ex case"
        )
        assert "200px" not in typ_source, (
            "Raw unconverted 'px' unit leaked into generated Typst source "
            "from the .. table:: :width: 200px case"
        )

        assert result.stderr.count("Unsupported length unit") == 1, (
            "Expected exactly 1 'Unsupported length unit' warning (the "
            f".. csv-table:: :width: 1ex case):\n{result.stderr}"
        )

        # Compile the emitted .typ to PDF with typst-py, WITHOUT try/except:
        # a mismatched block(width: ...)[...] wrapper would abort the
        # compile here (Pitfall 3).
        pdf_output = temp_build_dir / "index.pdf"
        typst.compile(str(index_typ), output=str(pdf_output))

        assert pdf_output.exists(), "PDF file was not created"
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        for sentinel in (
            TABLEPXSENTINEL7Q4,
            TABLELISTSENTINEL8Q5,
            TABLECSVSENTINEL9Q6,
        ):
            assert sentinel in full_text, (
                f"Expected table sentinel '{sentinel}' in extracted PDF "
                "text -- table content must render inside/without the "
                "width wrapper"
            )

        for leaked_token in LEAK_SIGNATURES:
            assert leaked_token not in full_text, (
                f"Literal Typst source '{leaked_token}' leaked into "
                "rendered PDF text -- table-width markup/code-mode "
                "regression"
            )
