"""
SIG-07 real-render geometric acceptance gate (37-03-PLAN.md Task 1).

Proves that a long, fully-qualified dotted signature name stays inside the
real production text column (measured 453.54pt at A4 / default margins /
11pt -- 37-RESEARCH.md, 37-EMISSION-CONTRACT.md section 10), and that the
real Sphinx v9.1.0 ``doc/`` corpus's worst-case qualified name never
regresses.

Why this gate exists (37-RESEARCH.md Pitfall 2): no real corpus signature
overflows the production column even in monospace -- a corpus-derived RED
fixture would be GREEN against the untouched translator and prove nothing.
The RED case here is therefore a DELIBERATELY SYNTHETIC over-length dotted
identifier (see the SYNTHETIC rST comment in
tests/fixtures/signature_overflow_render_gate/index.rst); the real corpus's
worst case is carried alongside as a labelled non-regression CONTROL that
must stay green both before and after the fix.

Measurement method (contract section 4.2 / 4.1): every geometric value is
read from a real ``typst.compile()`` of the fixture's own emitted, fully
template-wrapped ``.typ`` (so it uses the real production page geometry),
via Typst's own ``context measure(...)``/``context layout(...)`` -- never
``pypdf``'s per-glyph position-callback extraction mode, which was measured
this session to report ``x=0, y=0`` for every glyph on Typst-generated PDFs
in this sandbox. Every compiled-PDF text read strips U+200B first -- once a
zero-width break opportunity exists anywhere in the document, ``pypdf``
emits it spuriously at unrelated glyph boundaries too (contract section
4.2).
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

# The zero-width space character itself -- stripped from every compiled-PDF
# text read (contract section 4.2's spurious-emission hazard).
ZWSP = "\u200b"  # U+200B, written as an explicit escape (not an invisible literal)

# The 8-character Typst escape form the translator emits (contract section
# 4.1) -- NOT a literal U+200B byte. Split on this exact string, never on
# the raw ZWSP character, when locating break opportunities in emitted
# `.typ` SOURCE (as opposed to compiled PDF text).
ZWSP_ESCAPE = "\\u{200B}"

# Measured 2026-08-01 at the project's real production geometry (A4,
# default margins, 11pt -- typsphinx/templates/base.typ, no margin
# override) -- 37-EMISSION-CONTRACT.md section 10. Used ONLY in the
# column-width sanity assertion below, never in the primary/control
# comparisons -- those always read the column width fresh from the same
# compiled probe they measure the signature against (D-06/D-07 binding
# constraint: never hardcode the column width in the comparison).
EXPECTED_COLUMN_WIDTH_PT = 453.54

# The SYNTHETIC over-length dotted identifier (contract section 10's
# worked 111-character example, reused verbatim per 37-03-PLAN.md Task 1's
# "reuse it or construct one of at least the same length"). Sphinx's
# py-domain splits a `py:class::` fully-qualified name at the LAST dot into
# desc_addname (everything up to and including that dot) and desc_name
# (the final segment) -- so this is authored here as the same split the
# fixture's index.rst produces, for cross-checking against what the
# translator actually emits.
SYNTHETIC_ADDNAME = (
    "typsphinx.overflow.probe.deeply.nested.package.namespace.segment."
    "alpha.beta.gamma.delta."
)
SYNTHETIC_NAME = "OverflowProbeDocumenter"
SYNTHETIC_IDENTIFIER = SYNTHETIC_ADDNAME + SYNTHETIC_NAME  # 111 chars

# The real-corpus non-regression CONTROL: Sphinx v9.1.0's own worst-case
# qualified name (37-RESEARCH.md Pitfall 2 / contract section 10),
# reproduced verbatim in index.rst as a real `py:function::` signature.
CONTROL_NAME_ANCHOR = "nested_parse_to_nodes"


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run `sphinx-build -b typst` as a subprocess and return the completed
    process. Invoked as `sys.executable -m sphinx` -- see
    tests/test_pdf_render_gate.py's `_run_sphinx_build_typst` for the full
    NixOS-sandbox PATH-shadowing rationale this mirrors.
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


def _extract_addname_and_name(typ_source: str, name_anchor: str) -> tuple[str, str]:
    """
    Locate the escaped-string content of TWO ADJACENT double-quoted Typst
    string literals: the one whose content is (or contains) ``name_anchor``
    -- desc_name, the dotted identifier's final segment -- and the
    literal immediately BEFORE it -- desc_addname, everything up to and
    including the last dot.

    ``name_anchor`` must be a substring that contains no ``.`` (so it
    survives U+200B injection unchanged both pre- and post-phase) and is
    unique to the signature's desc_name in the compiled document.

    Sphinx's py-domain always emits these as two SEPARATE text()/raw()
    calls with NOTHING between them (no space, no `+`) -- desc_signature
    treats its children like a list-item, joining consecutive children with
    a bare newline SEPARATOR in the .typ SOURCE, which is cosmetic-only in
    Typst code mode: two content values on consecutive lines with nothing
    joining them concatenate with ZERO added space in the rendered output.
    That is why the 111-character identifier in
    37-EMISSION-CONTRACT.md section 10 is measured as ONE continuous
    unbroken run spanning both literals, not two independent shorter runs
    -- verified this session (see the module docstring and Task 1's
    docstring below).

    Works whether the pre-phase ``text(...)`` or the post-phase
    ``raw(...)`` primitive wraps each literal: this only counts quote
    characters, agnostic to the surrounding function-call syntax, so the
    SAME assertion logic stays valid across the RED-to-GREEN transition.
    """
    anchor_idx = typ_source.index(name_anchor)
    name_open_q = typ_source.rindex('"', 0, anchor_idx)
    name_close_q = typ_source.index('"', anchor_idx)
    name_content = typ_source[name_open_q + 1 : name_close_q]

    addname_close_q = typ_source.rindex('"', 0, name_open_q)
    addname_open_q = typ_source.rindex('"', 0, addname_close_q)
    addname_content = typ_source[addname_open_q + 1 : addname_close_q]

    return addname_content, name_content


def _measure_widths(index_typ_path: Path, build_dir: Path, segments: list) -> tuple:
    """
    Append a Typst ``context`` probe -- reading the available column width
    via ``layout(size => size.width)`` and measuring each candidate
    ``segments`` entry via ``measure(raw(...))`` -- to the ALREADY
    template-wrapped, emitted ``index.typ``, compile the combined probe
    through the real ``typst.compile()``, and read the numeric results back
    via plain ``pypdf.extract_text()`` (never the per-glyph position-
    callback extraction mode -- measured unusable for per-glyph positions
    on Typst PDFs in this sandbox, contract section 4.2/RESEARCH.md).

    The probe is written and compiled INSIDE ``build_dir`` (not a separate
    scratch directory) so its relative ``#import "_template.typ": project``
    resolves -- this is what makes the measurement use the REAL production
    template and page geometry, not a hand-approximated stand-in.

    Returns ``(column_width_pt, [segment_width_pt, ...])``.
    """
    base_source = index_typ_path.read_text(encoding="utf-8")
    lines = [
        "",
        "#pagebreak()",
        "",
        "#context [COLWIDTH=#layout(size => size.width)]",
    ]
    for i, seg in enumerate(segments):
        escaped = seg.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'#context [SEG{i}WIDTH=#measure(raw("{escaped}")).width]')
    probe_source = base_source + "\n" + "\n".join(lines) + "\n"

    probe_path = build_dir / "sig07_probe.typ"
    probe_path.write_text(probe_source, encoding="utf-8")
    pdf_path = build_dir / "sig07_probe.pdf"
    typst.compile(str(probe_path), output=str(pdf_path))

    reader = pypdf.PdfReader(str(pdf_path))
    full_text = "\n".join(page.extract_text() for page in reader.pages)
    # Strip stray U+200B before parsing -- contract section 4.2.
    full_text = full_text.replace(ZWSP, "")
    # pypdf inserts spurious whitespace/newlines between separate
    # text-showing operations even when they render on the same visual
    # line (a sibling quirk to the U+200B one contract section 4.2
    # documents) -- flatten ALL whitespace before parsing the probe's own
    # LABEL=VALUE markers, which never contain whitespace themselves.
    search_text = re.sub(r"\s+", "", full_text)

    col_match = re.search(r"COLWIDTH=([\d.]+)pt", search_text)
    assert col_match, f"could not read COLWIDTH from probe PDF text:\n{full_text}"
    column_width = float(col_match.group(1))

    seg_widths = []
    for i in range(len(segments)):
        m = re.search(rf"SEG{i}WIDTH=([\d.]+)pt", search_text)
        assert m, f"could not read SEG{i}WIDTH from probe PDF text:\n{full_text}"
        seg_widths.append(float(m.group(1)))

    return column_width, seg_widths


@pytest.fixture(scope="class")
def signature_overflow_built(tmp_path_factory):
    """
    Build the signature_overflow_render_gate fixture through `-b typst`
    ONCE per class and return `(content_typ_path, wrapper_typ_path,
    build_dir)` -- every test method below reads a disjoint slice of the
    same real emission, rather than re-running sphinx-build once per test.

    Two paths, deliberately: the CONTENT file (index.typ, R1) carries the
    translator body markup `_extract_addname_and_name` scans, while the
    WRAPPER file (master.typ, R2/R3) carries the full template application
    -- `_measure_widths` needs the wrapper as its probe base so the
    appended context probe measures the REAL production page geometry
    (A4/margins/font), not Typst's untemplated default.

    Depends only on `tmp_path_factory` (session-scoped-compatible) -- not
    on a function-scoped fixtures-dir fixture, to avoid a pytest
    ScopeMismatch (a class-scoped fixture may not depend on a narrower,
    function-scoped one) -- mirrors
    tests/test_pdf_render_gate.py's `topic_line_block_render_gate_pdf_text`
    precedent.
    """
    source_dir = Path(__file__).parent / "fixtures" / "signature_overflow_render_gate"
    build_dir = tmp_path_factory.mktemp("sig07_gate") / "_build"
    result = _run_sphinx_build_typst(source_dir, build_dir)
    assert (
        result.returncode == 0
    ), f"sphinx-build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    content_typ = build_dir / "index.typ"
    assert content_typ.exists(), "index.typ (content) was not generated"
    wrapper_typ = build_dir / "master.typ"
    assert wrapper_typ.exists(), "master.typ (wrapper) was not generated"
    return content_typ, wrapper_typ, build_dir


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the SIG-07 render gate",
)
class TestSignatureOverflowRenderGate:
    """
    Real-compile geometric acceptance gate for SIG-07.

    Requirements: SIG-07 (37-CONTEXT.md D-06/D-07, 37-RESEARCH.md,
    37-EMISSION-CONTRACT.md section 10, 37-03-PLAN.md Task 1).
    """

    def test_fixture_identifier_is_synthetic_and_over_length(self):
        """
        Sanity check on the fixture's own authored constant (not on the
        translator's output): the synthetic identifier is at least 90
        characters, contains no space and no comma -- 37-03-PLAN.md Task 1
        acceptance criteria.
        """
        assert len(SYNTHETIC_IDENTIFIER) >= 90
        assert " " not in SYNTHETIC_IDENTIFIER
        assert "," not in SYNTHETIC_IDENTIFIER

    def test_primary_widest_segment_fits_column(self, signature_overflow_built):
        """
        SIG-07 primary: the widest ZWSP-delimited segment of the synthetic
        identifier must measure strictly less than the column width read
        from the SAME compiled probe.

        Pre-phase measured value (this session, contract section 10): the
        untouched translator injects NO break opportunity into the
        addname+name run, so `segments` here has length 1 (the whole
        111-character identifier) and its raw()-measured width is 588.08pt
        against a 453.54pt column -- overflow by 134.54pt. This assertion
        is EXPECTED TO FAIL (RED) against the untouched translator; a
        future plan (37-06) makes it pass by injecting U+200B after every
        period (D-07) and wrapping the signature in
        par(hanging-indent: ...) (D-06).
        """
        content_typ, wrapper_typ, build_dir = signature_overflow_built
        typ_source = content_typ.read_text(encoding="utf-8")
        addname, name = _extract_addname_and_name(typ_source, SYNTHETIC_NAME)
        combined = addname + name
        segments = combined.split(ZWSP_ESCAPE)
        column_width, seg_widths = _measure_widths(wrapper_typ, build_dir, segments)
        widest = max(seg_widths)
        assert widest < column_width, (
            f"widest unbreakable segment ({widest}pt) does not fit inside "
            f"the available production column ({column_width}pt) -- "
            f"segments measured: {list(zip(segments, seg_widths, strict=True))}"
        )

    def test_hanging_indent_present(self, signature_overflow_built):
        """
        SIG-07 / D-06 (half 1 of 2): the desc_signature wrapper must carry
        `par(hanging-indent: 2.5em, ...)` -- the SHARED_INDENT_STEP
        constant's value (contract section 1) -- specifically, not merely
        "some wrapping mechanism". D-06 measured and REJECTED
        `grid(columns: (auto, 1fr))` (starves the parameter column) and
        forbids font shrinking outright; a gate that accepted any wrapping
        mechanism would let a rejected one pass. "2.5em" is hardcoded here
        deliberately -- it is the plan-specified constant's value, not
        derived from the code under test.

        Pre-phase the wrapper is still `strong({...})` -- no hanging indent
        at all, so this assertion FAILS (RED) against the untouched
        translator.
        """
        content_typ, _, _ = signature_overflow_built
        typ_source = content_typ.read_text(encoding="utf-8")
        assert "par(hanging-indent: 2.5em" in typ_source, (
            "expected the desc_signature wrapper to carry "
            "par(hanging-indent: 2.5em, ...) -- D-06's chosen, "
            "non-negotiable overflow strategy (grid() and font-shrinking "
            "were measured and rejected)."
        )

    def test_break_opportunity_after_every_period(self, signature_overflow_built):
        """
        SIG-07 / D-07 (half 2 of 2): the break-opportunity escape must
        appear after EVERY period in the synthetic identifier's
        addname+name run, not just the first -- D-07 locks the scope as
        every long dotted name. Counts occurrences (not a bare presence
        check) so a partial injection (first period only) fails this
        assertion even though it would improve the measured width.

        Pre-phase: zero periods carry the escape (0 != 12), so this
        assertion FAILS (RED) against the untouched translator.
        """
        content_typ, _, _ = signature_overflow_built
        typ_source = content_typ.read_text(encoding="utf-8")
        addname, name = _extract_addname_and_name(typ_source, SYNTHETIC_NAME)
        combined = addname + name
        expected_periods = SYNTHETIC_IDENTIFIER.count(".")
        actual_zwsp = combined.count(ZWSP_ESCAPE)
        assert actual_zwsp == expected_periods, (
            f"expected the break-opportunity escape ({ZWSP_ESCAPE!r}) after "
            f"EVERY one of the {expected_periods} periods in the synthetic "
            f"identifier; found {actual_zwsp} occurrence(s) in the emitted "
            f"run {combined!r}."
        )

    def test_control_widest_segment_fits_column_before_and_after(
        self, signature_overflow_built
    ):
        """
        SIG-07 control: the real-corpus non-regression construct
        (`sphinx.util.parsing.nested_parse_to_nodes`, 37-RESEARCH.md
        Pitfall 2's measured worst-case qualified name in the Sphinx
        v9.1.0 `doc/` corpus) must fit inside the column both before and
        after the fix. This assertion PASSES pre-phase (and must keep
        passing post-phase) -- it is a non-regression control, never to be
        converted into the RED case.
        """
        content_typ, wrapper_typ, build_dir = signature_overflow_built
        typ_source = content_typ.read_text(encoding="utf-8")
        addname, name = _extract_addname_and_name(typ_source, CONTROL_NAME_ANCHOR)
        combined = addname + name
        segments = combined.split(ZWSP_ESCAPE)
        column_width, seg_widths = _measure_widths(wrapper_typ, build_dir, segments)
        widest = max(seg_widths)
        assert widest < column_width, (
            "Real-corpus non-regression control "
            f"({combined!r}) overflowed the column ({widest}pt >= "
            f"{column_width}pt) -- this must never happen; the real Sphinx "
            "v9.1.0 doc/ corpus's worst-case qualified name fits at "
            "production width both before and after the SIG-07 fix "
            "(37-RESEARCH.md Pitfall 2)."
        )

    def test_column_width_sanity(self, signature_overflow_built):
        """
        The column width read from the probe is a positive length and, at
        the project's default A4 geometry, matches the value recorded in
        contract section 10 -- so a silent page-geometry change is caught
        rather than silently absorbed by the primary/control comparisons
        above (which always read the column width fresh, never hardcoded).
        """
        _, wrapper_typ, build_dir = signature_overflow_built
        column_width, _ = _measure_widths(wrapper_typ, build_dir, ["x"])
        assert column_width > 0
        assert column_width == pytest.approx(EXPECTED_COLUMN_WIDTH_PT, abs=0.01), (
            f"expected the production A4/default-margin/11pt column width "
            f"to be {EXPECTED_COLUMN_WIDTH_PT}pt (measured 2026-08-01, "
            f"contract section 10); got {column_width}pt instead -- "
            "investigate a page-geometry change rather than updating this "
            "constant blindly."
        )
