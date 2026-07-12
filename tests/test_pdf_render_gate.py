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
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
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
    """
    return subprocess.run(
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
