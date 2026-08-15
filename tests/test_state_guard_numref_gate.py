"""
Phase 49 plan 06: the two-case ``:numref:`` MEASUREMENT gate for open
question #2 / D-01.

D-01 fixes the fix-or-document decision IN ADVANCE: a divergence is
recorded as a documented limitation and handed forward to Phase 51 (docs)
and Phase 52 (CHANGELOG) -- it is NOT fixed in this phase. This module is
therefore a MEASUREMENT gate, not an assertion gate for the numbering
outcome itself: it asserts only what is INVARIANT regardless of which way
the measurement comes out (the build succeeds, both PDFs exist, both
``:numref:`` reference sites render SOME text, and both figures render
with SOME Typst-assigned caption number), and EXTRACTS the rest -- the
reference's own rendered text and the figure's own Typst-assigned number,
per case, per master -- for the record in
``.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EVIDENCE.md``'s
``## numref measurement`` section, which this module's own printed output
feeds verbatim.

Fixture: ``tests/fixtures/state_guard_numref_two_case_gate`` (per
``49-EXPECTED-STRUCTURE.md`` fixture specification entry 10, the ONLY
source of this fixture's docnames, figure names, captions, reference sites
and traversal positions).

Case (a) -- differing numbers: figure ``fig-x`` (in ``shared_fig_doc``) is
reachable from BOTH masters, at DIFFERENT traversal positions. Sphinx's
own ``env.toc_fignumbers`` is populated by a SINGLE walk rooted only at
``root_doc`` (``index``), so it bakes ONE literal number into both
masters' ``:numref:`` reference text, while Typst's own ``figure()``
numbering is a separate per-compiled-wrapper counter.

Case (b) -- no number assigned at all: figure ``fig-y`` (in ``only_doc``)
is reachable ONLY through ``other_master`` (never through ``root_doc``),
so Sphinx's root-rooted walk never visits it and ``:numref:`` falls back
to the reference's own literal ``contnode`` text -- this module records
whatever text actually appears rather than asserting a predicted string
(research traced the fallback MECHANISM but not the exact node content
typsphinx's own pipeline renders in that position), and separately
records whether a warning accompanies the fallback (research's own
"zero warning" characterization is a hypothesis this module measures,
not assumes).
"""

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

from sphinx.testing.util import SphinxTestApp

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "state_guard_numref_two_case_gate"

pytestmark = pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are required for the numref measurement gate",
)


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never a package-manager ``run
    sphinx-build`` subprocess form), matching every other Phase 49 gate
    module's own copy of this helper -- sidesteps the documented
    NixOS-sandbox PATH-shadowing hazard and depends on no external PATH
    resolution at all.
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


def _pdf_text(pdf_path: Path) -> str:
    reader = pypdf.PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() for page in reader.pages)


def _slice_after_marker(text: str, marker: str, stop_markers: list) -> str:
    """
    Return the substring of ``text`` immediately following ``marker``, up
    to whichever comes first: the earliest of ``stop_markers``, the next
    newline, or the end of ``text`` -- then stripped of surrounding
    whitespace. Used to isolate one ``:numref:`` reference site's own
    rendered text from a PDF-extracted line that may carry more than one
    reference site (Case (a) and Case (b) share one sentence in
    ``other_master.rst``).
    """
    start_idx = text.index(marker) + len(marker)
    end_idx = len(text)
    for stop in stop_markers:
        idx = text.find(stop, start_idx)
        if idx != -1:
            end_idx = min(end_idx, idx)
    newline_idx = text.find("\n", start_idx)
    if newline_idx != -1:
        end_idx = min(end_idx, newline_idx)
    return text[start_idx:end_idx].strip()


def _figure_number_for_caption(text: str, caption_suffix: str) -> int:
    """
    Extract the Typst-assigned figure number from a ``Figure N: <caption>``
    line in the compiled PDF's own extracted text (Typst's default figure
    supplement/counter rendering, unrelated to Sphinx's own
    ``numfig_format``). Raises ``AssertionError`` (via the regex match's
    own failure) if no such line is found -- deliberately loud, since a
    missing match means the fixture's own figure did not render at all.
    """
    # Typst's own figure-supplement rendering separates "Figure" from the
    # number with a NON-BREAKING space (U+00A0), not an ASCII space --
    # measured directly against this fixture's own pypdf-extracted text
    # (`'Figure\xa01: Figure X Caption'`). `\s` in Python's `re` matches
    # `\xa0` too (it is whitespace per Unicode), so this pattern accepts
    # either.
    pattern = re.compile(r"Figure\s+(\d+):\s+" + re.escape(caption_suffix))
    match = pattern.search(text)
    assert match is not None, (
        f"expected a 'Figure N: {caption_suffix}' line in the compiled "
        f"PDF text, found none. Full text:\n{text}"
    )
    return int(match.group(1))


@dataclass
class _NumrefMeasurement:
    """One (case, master) pair's own extracted values -- the row shape
    ``49-EVIDENCE.md``'s own table mirrors."""

    case: str
    master: str
    reference_text: str
    figure_number: int
    agrees: bool


@pytest.fixture(scope="module")
def pdf_build(tmp_path_factory):
    """
    Real ``-b typstpdf`` build of the fixture, run ONCE per module. Both
    the invariant assertions below and the extraction/recording test share
    this single build.
    """
    build_dir = tmp_path_factory.mktemp("numref-two-case-pdf")
    result = _run_sphinx_build(FIXTURE_DIR, build_dir, "typstpdf")
    return build_dir, result


class TestNumrefTwoCaseBuildInvariants:
    """
    Invariant assertions ONLY -- what must hold regardless of which way
    the numref divergence measurement comes out. The numbering OUTCOME
    itself is not asserted here (D-01: it is recorded, not fixed or
    gated on).
    """

    def test_build_succeeds_and_both_pdfs_exist(self, pdf_build):
        build_dir, result = pdf_build
        assert result.returncode == 0, (
            f"expected the two-master numref fixture to build+compile "
            f"successfully (COMP-12's own sibling fixture, unrelated to "
            f"the corpus gate):\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert (build_dir / "manual.pdf").exists(), "manual.pdf not produced"
        assert (build_dir / "manual2.pdf").exists(), "manual2.pdf not produced"
        for pdf_name in ("manual.pdf", "manual2.pdf"):
            pdf_path = build_dir / pdf_name
            assert pdf_path.stat().st_size > 0, f"{pdf_name} is empty"
            with open(pdf_path, "rb") as f:
                assert f.read(4) == b"%PDF", f"{pdf_name} is not a valid PDF"

    def test_both_case_a_reference_sites_render_some_text(self, pdf_build):
        build_dir, result = pdf_build
        assert result.returncode == 0
        index_text = _pdf_text(build_dir / "manual.pdf")
        other_text = _pdf_text(build_dir / "manual2.pdf")
        index_case_a = _slice_after_marker(
            index_text, "Case (a) reference: ", ["Case (b) reference:"]
        )
        other_case_a = _slice_after_marker(
            other_text, "Case (a) reference: ", ["Case (b) reference:"]
        )
        assert index_case_a, "index master's Case (a) reference rendered no text"
        assert other_case_a, "other_master's Case (a) reference rendered no text"

    def test_case_b_reference_site_renders_some_text(self, pdf_build):
        build_dir, result = pdf_build
        assert result.returncode == 0
        other_text = _pdf_text(build_dir / "manual2.pdf")
        other_case_b = _slice_after_marker(other_text, "Case (b) reference: ", [])
        assert other_case_b, "other_master's Case (b) reference rendered no text"

    def test_both_figures_carry_some_typst_assigned_number(self, pdf_build):
        build_dir, result = pdf_build
        assert result.returncode == 0
        index_text = _pdf_text(build_dir / "manual.pdf")
        other_text = _pdf_text(build_dir / "manual2.pdf")
        # fig-x in index's own compile.
        n = _figure_number_for_caption(index_text, "Figure X Caption")
        assert n >= 1
        # fig-x in other_master's own compile.
        n = _figure_number_for_caption(other_text, "Figure X Caption")
        assert n >= 1
        # fig-y in other_master's own compile.
        n = _figure_number_for_caption(other_text, "Figure Y Caption")
        assert n >= 1


class TestOnlyDocUnreachableFromRoot:
    """
    D-01's own load-bearing property, asserted by the gate rather than
    only by inspection: ``only_doc`` (Case (b)'s subject) is reachable
    from no path starting at the root document. Checked against THIS
    phase's own per-master edge-derivation mechanism
    (``TypstBuilder._master_include_edges``), the same attribute
    ``tests/test_include_ledger_removal_gate.py``'s assumption-delta
    contract test already inspects -- no edge key in the root master
    ``index``'s own published edge set may name ``only_doc`` as a child.
    """

    def test_index_edge_set_never_names_only_doc(self, tmp_path):
        outdir = tmp_path / "build"
        app = SphinxTestApp(buildername="typst", srcdir=FIXTURE_DIR, builddir=outdir)
        try:
            app.build()
            index_edges = app.builder._master_include_edges["index"]
            assert not any(edge.endswith(">only_doc") for edge in index_edges), (
                f"expected 'only_doc' unreachable from the root master "
                f"'index' -- found it in index's own published edge set: "
                f"{index_edges}"
            )
            # Sanity: other_master's own edge set DOES name it (the
            # fixture's own Case (b) precondition).
            other_edges = app.builder._master_include_edges["other_master"]
            assert any(edge.endswith(">only_doc") for edge in other_edges), (
                f"expected 'other_master' to reach 'only_doc' directly -- "
                f"got: {other_edges}"
            )
        finally:
            app.cleanup()


class TestNumrefTwoCaseExtractionForRecord:
    """
    The extraction/recording half (not an assertion gate for the
    numbering outcome): per case, per master, extracts the reference's
    own rendered text and the target figure's own Typst-assigned caption
    number, and prints them for the record -- this test's own printed
    output is what ``49-EVIDENCE.md``'s ``## numref measurement`` table
    transcribes verbatim.
    """

    def test_extract_and_print_both_cases_both_masters(self, pdf_build):
        build_dir, result = pdf_build
        assert result.returncode == 0

        index_text = _pdf_text(build_dir / "manual.pdf")
        other_text = _pdf_text(build_dir / "manual2.pdf")

        index_case_a_ref = _slice_after_marker(
            index_text, "Case (a) reference: ", ["Case (b) reference:"]
        )
        other_case_a_ref = _slice_after_marker(
            other_text, "Case (a) reference: ", ["Case (b) reference:"]
        )
        other_case_b_ref = _slice_after_marker(other_text, "Case (b) reference: ", [])

        fig_x_num_index = _figure_number_for_caption(index_text, "Figure X Caption")
        fig_x_num_other = _figure_number_for_caption(other_text, "Figure X Caption")
        fig_y_num_other = _figure_number_for_caption(other_text, "Figure Y Caption")

        measurements = [
            _NumrefMeasurement(
                case="a",
                master="index",
                reference_text=index_case_a_ref,
                figure_number=fig_x_num_index,
                agrees=(str(fig_x_num_index) in index_case_a_ref),
            ),
            _NumrefMeasurement(
                case="a",
                master="other_master",
                reference_text=other_case_a_ref,
                figure_number=fig_x_num_other,
                agrees=(str(fig_x_num_other) in other_case_a_ref),
            ),
            _NumrefMeasurement(
                case="b",
                master="other_master",
                reference_text=other_case_b_ref,
                figure_number=fig_y_num_other,
                agrees=(str(fig_y_num_other) in other_case_b_ref),
            ),
        ]

        print("\n=== numref two-case measurement (for 49-EVIDENCE.md) ===")
        for m in measurements:
            print(
                f"case={m.case} master={m.master} "
                f"reference_text={m.reference_text!r} "
                f"typst_figure_number={m.figure_number} agrees={m.agrees}"
            )

        # Full warning list from the SAME build's captured stderr, for the
        # record -- case (b)'s defining research hypothesis is "zero
        # warning"; this prints the actual list rather than assuming it.
        print("--- stderr (full, verbatim) ---")
        print(result.stderr)
        print("=== end measurement ===\n")

        # Load-bearing assertions (not merely a print statement): every
        # extracted reference text is non-empty and every figure number
        # is a positive int -- proven again here (redundant with the
        # invariants class above) so THIS test's own extraction path is
        # independently verified to have captured real values, not an
        # empty/garbage slice.
        for m in measurements:
            assert m.reference_text, f"empty reference_text for {m}"
            assert m.figure_number >= 1, f"non-positive figure_number for {m}"
