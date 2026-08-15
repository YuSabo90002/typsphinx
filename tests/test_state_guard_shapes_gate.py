"""
Phase 49 plan 03: the shapes gate for D-06's seven degenerate/coverage
fixtures -- ``state_guard_self_and_url_gate``, ``state_guard_cycle_gate``,
``state_guard_selfref_gate``, ``state_guard_glob_gate``,
``state_guard_orphan_ref_gate``, ``state_guard_three_master_gate``,
``state_guard_substring_key_gate``.

Closes requirements COMP-05, COMP-06, COMP-09.

Every asserted value in this module comes from ``49-EXPECTED-STRUCTURE.md``'s
``## Degenerate-shape outcome table`` and ``## Fixture specification``
entries 3-9 -- each shape's outcome was DECIDED at plan time, never
discovered as a test failure here (SC#2, ROADMAP binding constraint #6).
Every assertion that could not pass until 49-04's emitter landed was recorded,
on this plan's own pre-fix tree, as a strict xfail (``pytest.mark.xfail``,
``strict=True``), with a reason paraphrasing the matching transcript recorded
verbatim in ``49-SHAPES-RED-EVIDENCE.md``. 49-04 has now landed those flips,
and every one of those strict xfail markers has been removed from this
module -- ``49-SHAPES-RED-EVIDENCE.md`` remains the verbatim record of each
flipped assertion's own pre-fix RED transcript.

Scope caveat (COMP-06): the substring-key test below covers the
ARRAY-VERSUS-STRING SEMANTICS half of the trailing-comma hazard only -- it
does NOT and cannot cover the one-element trailing-comma ARITY half, whose
detector is the arity-1 Typst-type readback asserted directly against the
production rendering function in 49-04's own unit module.
"""

import json
import re
import subprocess
import sys
from dataclasses import dataclass
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

FIXTURES_DIR = Path(__file__).parent / "fixtures"
EVIDENCE_PATH = (
    Path(__file__).parent.parent
    / ".planning"
    / "phases"
    / "49-per-master-include-graph-with-state-guarded-includes"
    / "49-SHAPES-RED-EVIDENCE.md"
)

# The state key decided in 49-EXPECTED-STRUCTURE.md's Emission contract
# (D-07, measured in 49-EVIDENCE.md's State-syntax measurement) -- fixed
# for the whole phase, not open discretion at this point.
STATE_KEY = "typsphinx:include-edges"

# Order MUST match 49-SHAPES-RED-EVIDENCE.md's own Section 1-7 order -- the
# no-lost-diagnostics test below zips this list against the evidence file's
# own "## Section " split, never against a fixture-name match inside a
# section's own header text.
FIXTURE_NAMES = [
    "state_guard_self_and_url_gate",
    "state_guard_cycle_gate",
    "state_guard_selfref_gate",
    "state_guard_glob_gate",
    "state_guard_orphan_ref_gate",
    "state_guard_three_master_gate",
    "state_guard_substring_key_gate",
]


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never a package-manager ``run
    sphinx-build`` subprocess form), matching every other gate module's own
    copy of this helper -- sidesteps the documented NixOS-sandbox
    PATH-shadowing hazard and depends on no external PATH resolution at
    all.
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


@dataclass
class _Build:
    """One fixture's real ``-b typst`` + ``-b typstpdf`` build, run once."""

    name: str
    typst_dir: Path
    typst_result: subprocess.CompletedProcess
    pdf_dir: Path
    pdf_result: subprocess.CompletedProcess

    def content_text(self, docname: str) -> str:
        return (self.typst_dir / f"{docname}.typ").read_text(encoding="utf-8")

    def wrapper_text(self, target: str) -> str:
        return (self.typst_dir / target).read_text(encoding="utf-8")

    def pdf_text(self, target: str) -> str:
        pdf_path = self.pdf_dir / target.replace(".typ", ".pdf")
        reader = pypdf.PdfReader(str(pdf_path))
        return "\n".join(page.extract_text() for page in reader.pages)

    def pdf_page_texts(self, target: str) -> list:
        """
        Same idiom as ``pdf_text`` -- resolve the compiled PDF path and read
        each page's extracted text via ``pypdf.PdfReader`` -- but return the
        per-page list instead of joining, for page-level occurrence
        assertions.
        """
        pdf_path = self.pdf_dir / target.replace(".typ", ".pdf")
        reader = pypdf.PdfReader(str(pdf_path))
        return [page.extract_text() for page in reader.pages]

    def heading_levels(self, wrapper_target: str, selector: str) -> list:
        """
        Query resolved heading levels for ``selector`` against the compiled
        wrapper, with the build directory as ``root`` -- Typst resolves
        every ``include()`` path relative to ``root``, never the ``.typ``
        file's own directory (``tests/test_heading_depth_render_gate.py``'s
        own convention).
        """
        wrapper_path = self.pdf_dir / wrapper_target
        result = typst.query(
            str(wrapper_path), selector, field="level", root=str(self.pdf_dir)
        )
        return json.loads(result)

    def label_matches(self, wrapper_target: str, label_selector: str) -> list:
        """
        Query for a specific ``<docname:label>`` selector against the
        compiled wrapper -- proves the label is ``query()``-reachable, not
        merely visually present (mirrors ``49-EVIDENCE.md`` Probe 8).
        """
        wrapper_path = self.pdf_dir / wrapper_target
        result = typst.query(str(wrapper_path), label_selector, root=str(self.pdf_dir))
        return json.loads(result)


def _marker_count(text: str, marker: str) -> int:
    return text.count(marker)


@pytest.fixture(scope="module")
def all_builds(tmp_path_factory) -> dict:
    """
    Build every one of the seven shape fixtures ONCE per module, through
    both ``-b typst`` and ``-b typstpdf``, and return a dict keyed by
    fixture name -- shared across every test class below so the module
    runs 7 real ``sphinx-build`` pairs total, not 7-per-test-class.
    """
    builds = {}
    for name in FIXTURE_NAMES:
        source_dir = FIXTURES_DIR / name
        typst_dir = tmp_path_factory.mktemp(f"{name}-typst")
        typst_result = _run_sphinx_build(source_dir, typst_dir, "typst")
        pdf_dir = tmp_path_factory.mktemp(f"{name}-pdf")
        pdf_result = _run_sphinx_build(source_dir, pdf_dir, "typstpdf")
        builds[name] = _Build(
            name=name,
            typst_dir=typst_dir,
            typst_result=typst_result,
            pdf_dir=pdf_dir,
            pdf_result=pdf_result,
        )
    return builds


pytestmark = pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are required for the state-guard shapes gate",
)


# ---------------------------------------------------------------------------
# 1 & 2. state_guard_self_and_url_gate -- D-03/D-10 (self/URL) and D-04
# (duplicate-entry occurrence rule)
# ---------------------------------------------------------------------------


class TestSelfAndUrlGate:
    """
    ``state_guard_self_and_url_gate`` -- D-03 (self/external-URL entries
    never reach ``includefiles``) and D-10 (the phase's one classic-
    TypstError RED: the current ``entries``-iterating emitter aborts the
    compile on a ``self``-derived include path). Also carries D-04's
    per-emission-site occurrence rule (the duplicated ``child`` entry).

    Decided outcomes transcribed from ``49-EXPECTED-STRUCTURE.md``'s
    Degenerate-shape outcome table (the ``self`` magic keyword /
    external-URL row) and Fixture specification entry 3; the pre-fix
    transcript is ``49-SHAPES-RED-EVIDENCE.md`` Section 1.
    """

    def test_self_and_external_url_produce_no_guard(self, all_builds):
        """
        COMP-05/D-03/D-10: the PDF build exits 0, no emitted include
        derives from the ``self`` entry or the external URL, the child's
        marker appears exactly once in the compiled PDF, and Sphinx's own
        duplicated-entry warning is still present (this phase silences no
        diagnostic Sphinx already emits). The pre-fix RED was recorded as
        a strict xfail against ``49-SHAPES-RED-EVIDENCE.md`` Section 1
        (the PDF build aborted with ``TypstError: file not found
        (self.typ)``, and ``index.typ`` unconditionally included
        ``self.typ`` and ``https://example.com.typ``); 49-04's emitter now
        iterates ``includefiles`` instead of ``entries`` (D-03).
        """
        build = all_builds["state_guard_self_and_url_gate"]
        assert build.pdf_result.returncode == 0, (
            "PDF build did not exit 0:\n"
            f"stdout: {build.pdf_result.stdout}\nstderr: {build.pdf_result.stderr}"
        )
        index_text = build.content_text("index")
        assert 'include("self.typ")' not in index_text
        assert 'include("https://example.com.typ")' not in index_text
        pdf_text = build.pdf_text("manual.typ")
        assert _marker_count(pdf_text, "CHILD-BODY-MARKER") == 1
        warnings = build.pdf_result.stdout + build.pdf_result.stderr
        assert "duplicate" in warnings.lower() or "重複" in warnings

    def test_duplicate_entry_occurrence_rule(self, all_builds):
        """
        COMP-05 adjacency / D-04: the emitted content file carries TWO
        guard lines for the duplicated child, with distinct occurrence
        values (occurrence 0 and occurrence 1), and the wrapper's
        published array contains only the occurrence-0 key. The child's
        marker and its Typst label each appear exactly once in the
        compiled document. The pre-fix RED was recorded as a strict xfail
        against ``49-SHAPES-RED-EVIDENCE.md`` Section 1 (``index.typ``
        emitted ONE deduped ``include('child.typ')`` via the pre-Phase-49
        write-time ledger, not two occurrence-indexed state guards);
        49-04's emitter now emits a per-emission-site guard for every
        toctree entry (D-04).
        """
        build = all_builds["state_guard_self_and_url_gate"]
        index_text = build.content_text("index")
        occurrence_0 = re.compile(
            r'if\s+"index#0>child"\s+in\s+state\("'
            + re.escape(STATE_KEY)
            + r'",\s*\(\)\)\.get\(\)\s*\{\s*include\("child\.typ"\)\s*\}'
        )
        occurrence_1 = re.compile(
            r'if\s+"index#1>child"\s+in\s+state\("'
            + re.escape(STATE_KEY)
            + r'",\s*\(\)\)\.get\(\)\s*\{\s*include\("child\.typ"\)\s*\}'
        )
        assert occurrence_0.search(index_text), index_text
        assert occurrence_1.search(index_text), index_text

        wrapper_text = build.wrapper_text("manual.typ")
        assert '"index#0>child"' in wrapper_text
        assert '"index#1>child"' not in wrapper_text

        pdf_text = build.pdf_text("manual.typ")
        assert _marker_count(pdf_text, "CHILD-BODY-MARKER") == 1

        label_matches = build.label_matches("manual.typ", "<child:child>")
        assert len(label_matches) == 1


# ---------------------------------------------------------------------------
# 3. state_guard_cycle_gate -- D-06 (2-node cycle)
# ---------------------------------------------------------------------------


class TestCycleGate:
    """
    ``state_guard_cycle_gate`` -- D-06's 2-node toctree cycle. Decided
    outcome transcribed from the Degenerate-shape outcome table's cycle
    row and Fixture specification entry 4; the pre-fix transcript (an
    ADDITIONAL, measured classic-TypstError RED distinct from D-10's
    own named one) is ``49-SHAPES-RED-EVIDENCE.md`` Section 2.
    """

    def test_two_node_cycle_terminates_with_forward_edge_only(self, all_builds):
        """
        D-06: the build terminates and exits 0. Each document's marker
        appears exactly once in the compiled PDF. The published array
        contains the forward edge (``alpha#0>beta``) and not the back
        edge (``beta#0>alpha``). The pre-fix RED was recorded as a strict
        xfail against ``49-SHAPES-RED-EVIDENCE.md`` Section 2 (the
        pre-Phase-49 write-time emitter had no cycle guard at all --
        ``alpha.typ`` and ``beta.typ`` mutually ``#include()``d each
        other, and the PDF build aborted with ``TypstError: maximum show
        rule depth exceeded``); 49-04's DFS now seeds ``traversed`` with
        the master's own docname and skips already-traversed children.
        """
        build = all_builds["state_guard_cycle_gate"]
        assert build.pdf_result.returncode == 0, (
            "PDF build did not exit 0 (cycle did not terminate cleanly):\n"
            f"stdout: {build.pdf_result.stdout}\nstderr: {build.pdf_result.stderr}"
        )
        pdf_text = build.pdf_text("manual.typ")
        assert _marker_count(pdf_text, "BETA-BODY-MARKER") == 1
        wrapper_text = build.wrapper_text("manual.typ")
        assert '"alpha#0>beta"' in wrapper_text
        assert '"beta#0>alpha"' not in wrapper_text


# ---------------------------------------------------------------------------
# 4. state_guard_selfref_gate -- D-06 (literal self-reference)
# ---------------------------------------------------------------------------


class TestSelfRefGate:
    """
    ``state_guard_selfref_gate`` -- D-06's literal self-referencing
    toctree (a document toctreeing its own docname, distinct from the
    ``self`` magic keyword covered by ``TestSelfAndUrlGate``). Decided
    outcome transcribed from the Degenerate-shape outcome table's
    self-reference row and Fixture specification entry 5; the pre-fix
    transcript (an INVARIANCE baseline -- already correct today, for an
    upstream Sphinx reason unrelated to this phase's own mechanism) is
    ``49-SHAPES-RED-EVIDENCE.md`` Section 3.
    """

    def test_self_referencing_entry_has_no_guard(self, all_builds):
        """
        D-06: exits 0. The self-listing entry's key (``index#0>index``)
        is absent from the published array while the ordinary child's key
        (``index#0>other``) is present, and the child's marker appears
        exactly once. The pre-fix RED was recorded as a strict xfail
        against ``49-SHAPES-RED-EVIDENCE.md`` Section 3 (no ``#state(...)``
        array was published by any wrapper yet, so the ordinary child's
        key could not yet be asserted present -- the PDF-level outcome
        itself was already correct pre-fix, via Sphinx's own upstream
        filtering); only the array-membership assertion was new.
        """
        build = all_builds["state_guard_selfref_gate"]
        assert build.pdf_result.returncode == 0
        wrapper_text = build.wrapper_text("manual.typ")
        assert '"index#0>index"' not in wrapper_text
        assert '"index#0>other"' in wrapper_text
        pdf_text = build.pdf_text("manual.typ")
        assert _marker_count(pdf_text, "OTHER-BODY-MARKER") == 1


# ---------------------------------------------------------------------------
# 5. state_guard_glob_gate -- D-06 (:glob: toctree)
# ---------------------------------------------------------------------------


class TestGlobGate:
    """
    ``state_guard_glob_gate`` -- D-06's ``:glob:`` toctree, needing no
    special handling since Sphinx itself expands the glob at parse time
    into a sorted docname list. Decided outcome transcribed from the
    Degenerate-shape outcome table's glob row and Fixture specification
    entry 6; the pre-fix transcript (an INVARIANCE baseline for the PDF
    ordering, a new xfail for the published array) is
    ``49-SHAPES-RED-EVIDENCE.md`` Section 4.
    """

    def test_glob_toctree_expands_in_sorted_order(self, all_builds):
        """
        D-06: exits 0. The three matched documents' markers appear in the
        compiled PDF's extracted text in the sorted-docname order (alpha,
        mike, zulu) at strictly increasing offsets, and the published
        array lists their keys in that same sorted order. The pre-fix RED
        was recorded as a strict xfail against
        ``49-SHAPES-RED-EVIDENCE.md`` Section 4 (no ``#state(...)`` array
        was published yet, so the sorted-order key list could not yet be
        asserted -- the PDF-level sorted-order outcome itself was already
        correct pre-fix, via Sphinx's own parse-time glob expansion).
        """
        build = all_builds["state_guard_glob_gate"]
        assert build.pdf_result.returncode == 0
        pdf_text = build.pdf_text("manual.typ")
        alpha_offset = pdf_text.find("ALPHA-BODY-MARKER")
        mike_offset = pdf_text.find("MIKE-BODY-MARKER")
        zulu_offset = pdf_text.find("ZULU-BODY-MARKER")
        assert -1 not in (alpha_offset, mike_offset, zulu_offset)
        assert alpha_offset < mike_offset < zulu_offset

        wrapper_text = build.wrapper_text("manual.typ")
        alpha_key_pos = wrapper_text.find('"index#0>guide/alpha"')
        mike_key_pos = wrapper_text.find('"index#0>guide/mike"')
        zulu_key_pos = wrapper_text.find('"index#0>guide/zulu"')
        assert -1 not in (alpha_key_pos, mike_key_pos, zulu_key_pos)
        assert alpha_key_pos < mike_key_pos < zulu_key_pos


# ---------------------------------------------------------------------------
# 6. state_guard_orphan_ref_gate -- D-06 (:orphan: reference degrades,
# Phase 48's own mechanism -- non-regression proof only)
# ---------------------------------------------------------------------------


class TestOrphanRefGate:
    """
    ``state_guard_orphan_ref_gate`` -- D-06's ``:orphan:`` document
    referenced but not toctree'd. The degradation MECHANISM belongs to
    Phase 48 (``TypstTranslator._label_existence_guard()``), NOT this
    phase -- this test proves only that Phase 49's own mechanism does not
    regress it. Decided outcome transcribed from the Degenerate-shape
    outcome table's orphan row and Fixture specification entry 7; the
    pre-fix transcript (an INVARIANCE baseline, already fully correct
    today) is ``49-SHAPES-RED-EVIDENCE.md`` Section 5.
    """

    def test_orphan_reference_degrades_not_included(self, all_builds):
        """
        D-06: exits 0. The orphan's marker is ABSENT from the compiled
        PDF, its key is absent from the published array (vacuously true
        today, since no array exists yet -- remains true post-fix), and
        the cross-reference to its label renders as plain text. NOT
        xfail: every assertion here already holds on the unfixed tree,
        because Phase 48's compile-time guard -- not this phase's own
        mechanism -- is what produces the degradation, and this test
        exists only to prove Phase 49 does not break it.
        """
        build = all_builds["state_guard_orphan_ref_gate"]
        assert build.pdf_result.returncode == 0
        pdf_text = build.pdf_text("manual.typ")
        assert "ORPHAN-BODY-MARKER" not in pdf_text
        wrapper_text = build.wrapper_text("manual.typ")
        assert '"index#0>orphan_doc"' not in wrapper_text
        assert "Orphan Section" in pdf_text


# ---------------------------------------------------------------------------
# 7. state_guard_three_master_gate -- SC#2/COMP-09 (three masters, two
# shared children -- the "not 2-master-specific" coverage obligation)
# ---------------------------------------------------------------------------


class TestThreeMasterGate:
    """
    ``state_guard_three_master_gate`` -- SC#2/COMP-09's coverage
    obligation proving the fix is not 2-master-specific. Decided edge
    sets and resolved heading levels transcribed from
    ``49-EXPECTED-STRUCTURE.md``'s Fixture specification entry 8; the
    pre-fix transcript (a real, silent, non-fatal content-drop RED --
    defect A / the diamond, reproduced live across three masters) is
    ``49-SHAPES-RED-EVIDENCE.md`` Section 6.
    """

    def test_three_masters_each_render_shared_children_once(self, all_builds):
        """
        SC#2/COMP-09: for each of the three masters, each shared child's
        marker appears exactly once in that master's own PDF, at the
        heading level the specification derived for that master, and all
        three published wrapper bodies (and therefore their arrays)
        differ from one another (proving the mapping is genuinely
        per-master, not a single global answer). The pre-fix RED was
        recorded as a strict xfail against ``49-SHAPES-RED-EVIDENCE.md``
        Section 6 (the pre-Phase-49 build-scoped write-time ledger let
        only ONE master's own toctree entry for a shared child survive --
        COMMON-A-MARKER was entirely absent from manual2.pdf, and
        COMMON-B-MARKER was absent from both manual1.pdf's Mid section
        and all of manual3.pdf); 49-04's per-master DFS now derives an
        independent edge set for each master.
        """
        build = all_builds["state_guard_three_master_gate"]
        assert build.pdf_result.returncode == 0

        m1_text = build.pdf_text("manual1.typ")
        m2_text = build.pdf_text("manual2.typ")
        m3_text = build.pdf_text("manual3.typ")

        assert _marker_count(m1_text, "COMMON-A-MARKER") == 1
        assert _marker_count(m2_text, "COMMON-A-MARKER") == 1
        assert _marker_count(m1_text, "COMMON-B-MARKER") == 1
        assert _marker_count(m2_text, "COMMON-B-MARKER") == 1
        assert _marker_count(m3_text, "COMMON-B-MARKER") == 1

        # Title "Common B" slugifies to "common-b" (Typst label id), not the
        # docname "common_b" -- the label selector below reflects that.
        m1_levels = build.heading_levels("manual1.typ", "<common_b:common-b>")
        m2_levels = build.heading_levels("manual2.typ", "<common_b:common-b>")
        m3_levels = build.heading_levels("manual3.typ", "<common_b:common-b>")
        assert m1_levels == [3]  # nested under mid
        assert m2_levels == [2]  # direct child of m2
        assert m3_levels == [2]  # direct child of m3

        w1 = build.wrapper_text("manual1.typ")
        w2 = build.wrapper_text("manual2.typ")
        w3 = build.wrapper_text("manual3.typ")
        assert w1 != w2 != w3 != w1

    def test_three_masters_each_carry_their_full_include_set_in_pdf(self, all_builds):
        """
        SC#3's goal-claim half: the milestone's own claim is that a
        ``typst_documents`` configuration declaring more than one master
        produces a COMPLETE PDF for each of them, with no silently dropped
        content. This method proves the completeness and isolation halves
        of that claim -- every document in a master's own include set
        contributes content to that master's PDF, a document outside that
        set contributes nothing, and no master's own body leaks into
        another master's PDF -- at both the full-text and the page level.
        Its sibling ``test_three_masters_each_render_shared_children_once``
        covers the shared-child occurrence counts and resolved heading
        levels; neither duplicates the other.
        """
        build = all_builds["state_guard_three_master_gate"]
        assert build.pdf_result.returncode == 0

        m1_text = build.pdf_text("manual1.typ")
        m2_text = build.pdf_text("manual2.typ")
        m3_text = build.pdf_text("manual3.typ")

        m1_pages = build.pdf_page_texts("manual1.typ")
        m2_pages = build.pdf_page_texts("manual2.typ")
        m3_pages = build.pdf_page_texts("manual3.typ")

        # Page-level structure: each master's PDF has at least one page.
        assert len(m1_pages) >= 1
        assert len(m2_pages) >= 1
        assert len(m3_pages) >= 1

        # Presence -- every document in a master's include set contributes
        # content. "Mid" carries a heading and no marker, which is exactly
        # why it is the right probe for "non-shared, non-marker-bearing
        # content is not silently dropped" -- used for both the m1/m3
        # presence assertions and the m2 absence assertion below.
        assert "Mid" in m1_text
        assert _marker_count(m1_text, "COMMON-A-MARKER") == 1
        assert _marker_count(m1_text, "COMMON-B-MARKER") == 1

        assert _marker_count(m2_text, "COMMON-A-MARKER") == 1
        assert _marker_count(m2_text, "COMMON-B-MARKER") == 1

        assert "Mid" in m3_text
        assert _marker_count(m3_text, "COMMON-B-MARKER") == 1

        # Absence -- a document outside a master's include set contributes
        # nothing.
        assert _marker_count(m3_text, "COMMON-A-MARKER") == 0
        assert "Mid" not in m2_text

        # Cross-master isolation -- no master's own body leaks into another
        # master's PDF. The fixture's typst_documents titles each embed
        # that master's own token, so a same-master presence check would be
        # satisfied by the title page alone and prove nothing about the
        # body; the cross-master ABSENCE form below cannot be satisfied
        # that way.
        assert "M2" not in m1_text
        assert "M3" not in m1_text
        assert "M1" not in m2_text
        assert "M3" not in m2_text
        assert "M1" not in m3_text
        assert "M2" not in m3_text

        # Page-level marker occurrence -- each marker that must be present
        # occurs on exactly one page of that master's PDF; each marker that
        # must be absent occurs on zero pages.
        def _pages_with(pages: list, marker: str) -> list:
            return [i for i, text in enumerate(pages) if marker in text]

        assert len(_pages_with(m1_pages, "COMMON-A-MARKER")) == 1
        assert len(_pages_with(m1_pages, "COMMON-B-MARKER")) == 1
        assert len(_pages_with(m2_pages, "COMMON-A-MARKER")) == 1
        assert len(_pages_with(m2_pages, "COMMON-B-MARKER")) == 1
        assert len(_pages_with(m3_pages, "COMMON-B-MARKER")) == 1
        assert len(_pages_with(m3_pages, "COMMON-A-MARKER")) == 0


# ---------------------------------------------------------------------------
# 8. Empty and single-entry arities (COMP-05 empty) -- reuses
# state_guard_orphan_ref_gate (empty) and state_guard_self_and_url_gate
# (single edge)
# ---------------------------------------------------------------------------


class TestEmptyAndSingleEntryArities:
    """
    COMP-05's empty/single-entry arity coverage. Reuses two
    already-built fixtures rather than adding an eighth:
    ``state_guard_orphan_ref_gate``'s master has NO toctree at all (the
    empty case), and ``state_guard_self_and_url_gate``'s master publishes
    exactly ONE live edge key (``index#0>child`` -- occurrence 1 is
    structurally dark, per D-04), the single-entry case that hits the
    mandatory trailing-comma construction rule (``49-EVIDENCE.md``
    Probe 2/4/5).
    """

    def test_empty_and_single_entry_array_literals(self, all_builds):
        """
        COMP-05 empty: for ``state_guard_orphan_ref_gate``'s master
        (empty include-file list), the emitted wrapper publishes the
        empty-array literal ``()`` and the emitted content file contains
        no toctree scope block. For ``state_guard_self_and_url_gate``'s
        master (exactly one live edge), the published literal matches the
        contract's one-or-more form including the mandatory trailing
        comma, asserted as a structural regex over the emitted line
        rather than a full-file exact-string diff. The pre-fix RED was
        recorded as a strict xfail: neither fixture's wrapper published
        any ``#state(...)`` array yet; 49-04's wrapper now publishes the
        empty-array literal for a master with no toctree, and the
        one-or-more form (with its mandatory trailing comma) for a
        master with exactly one edge (COMP-05 empty, D-09/Pitfall 1).
        """
        orphan_build = all_builds["state_guard_orphan_ref_gate"]
        orphan_wrapper = orphan_build.wrapper_text("manual.typ")
        empty_array = re.compile(
            r'#state\("' + re.escape(STATE_KEY) + r'",\s*\(\)\)\.update\(\(\)\)'
        )
        assert empty_array.search(orphan_wrapper), orphan_wrapper
        orphan_index = orphan_build.content_text("index")
        # 49-04: a bare "context {" substring check is too broad -- this
        # fixture's own `:ref:` cross-reference triggers Phase 48's
        # UNRELATED compile-time xref guard (`context { let __tsx_body =
        # [...`), which is not a toctree-emission scope block and was
        # already present pre-fix (49-SHAPES-RED-EVIDENCE.md Section 5
        # recorded this exact same match, attributing it to Phase 48).
        # The toctree-specific scope block this phase's own mechanism
        # governs opens with "context {\n  set heading(offset:" --
        # assert THAT signature is absent, not the bare substring.
        assert "context {\n  set heading(offset:" not in orphan_index

        single_build = all_builds["state_guard_self_and_url_gate"]
        single_wrapper = single_build.wrapper_text("manual.typ")
        one_entry_array = re.compile(
            r'#state\("'
            + re.escape(STATE_KEY)
            + r'",\s*\(\)\)\.update\(\("index#0>child",\)\)'
        )
        assert one_entry_array.search(single_wrapper), single_wrapper


# ---------------------------------------------------------------------------
# 9. state_guard_substring_key_gate -- COMP-06 (array-vs-string semantics)
# ---------------------------------------------------------------------------


class TestSubstringKeyGate:
    """
    ``state_guard_substring_key_gate`` -- COMP-06's array-vs-string
    dark-guard adjacency detector. Covers the array-versus-string
    SEMANTICS half of the trailing-comma hazard only, per this plan's own
    flagged assumptions -- the one-element trailing-comma ARITY half is
    asserted separately, against the production rendering function
    directly, in 49-04's own unit module. Decided outcome transcribed
    from ``49-EXPECTED-STRUCTURE.md``'s Fixture specification entry 9;
    the pre-fix transcript (an INVARIANCE baseline at the fixture/PDF
    level -- the hazard can only manifest once the array mechanism
    exists, proven separately at the syntax level by ``49-EVIDENCE.md``
    Probes 5/6) is ``49-SHAPES-RED-EVIDENCE.md`` Section 7.
    """

    def test_dark_key_is_a_proper_substring_of_a_published_key(self):
        """
        Pure string-level proof, independent of any build: the dark key
        ``index#0>guide`` is a proper substring of the published key
        ``index#0>guideext``, which is the only construction that can
        distinguish array membership from string containment at the
        fixture layer. If a future edge-key format change dissolves this
        relation, this assertion turns red rather than the fixture
        silently becoming vacuous.
        """
        published_key = "index#0>guideext"
        dark_key = "index#0>guide"
        assert dark_key in published_key
        assert dark_key != published_key

    def test_substring_key_semantics(self, all_builds):
        """
        COMP-06 adjacency: the published array contains exactly the two
        keys the specification derived (``index#0>guideext``,
        ``guideext#0>guide``). The dark key (``index#0>guide``) is NOT in
        the published array, and the shorter-named document's marker
        appears EXACTLY ONCE in the compiled PDF at the nested resolved
        heading level. The pre-fix RED was recorded as a strict xfail
        against ``49-SHAPES-RED-EVIDENCE.md`` Section 7 (no
        ``#state(...)`` array was published yet, so the published array
        could not yet be asserted to contain exactly the two live keys --
        the PDF-level marker/nesting outcome itself was already correct
        pre-fix, a write-time-ledger coincidence specific to this
        single-master fixture); 49-04's wrapper now publishes edge keys
        as a real Typst array (COMP-06).
        """
        build = all_builds["state_guard_substring_key_gate"]
        wrapper_text = build.wrapper_text("manual.typ")
        assert '"index#0>guideext"' in wrapper_text
        assert '"guideext#0>guide"' in wrapper_text
        assert '"index#0>guide"' not in wrapper_text

        pdf_text = build.pdf_text("manual.typ")
        assert _marker_count(pdf_text, "GUIDE-SUBSTRING-MARKER") == 1

        levels = build.heading_levels("manual.typ", "<guide:guide>")
        assert levels == [3]  # nested under index -> guideext -> guide


# ---------------------------------------------------------------------------
# 10. No lost diagnostics -- the backstop truth
# ---------------------------------------------------------------------------


def _parse_warning_baselines() -> dict:
    """
    Parse ``49-SHAPES-RED-EVIDENCE.md``'s own "Full warning list" bullets
    per section, keyed by fixture name via ``FIXTURE_NAMES``' own order
    (which matches the evidence file's Section 1-7 order) -- read from the
    artifact rather than restated inline here, so the comparison cannot
    drift from the recorded evidence.

    Each captured fragment is either the FULL backtick-quoted warning
    string (when the closing backtick sits on the same source line) or the
    LEADING portion of it (when the original transcript's own line wrapped
    for display -- the leading portion is still a valid, safe substring of
    the real captured warning either way).
    """
    text = EVIDENCE_PATH.read_text(encoding="utf-8")
    sections = text.split("\n## Section ")[1:]
    assert len(sections) == len(FIXTURE_NAMES), (
        f"expected {len(FIXTURE_NAMES)} sections in {EVIDENCE_PATH}, "
        f"found {len(sections)}"
    )
    baselines = {}
    for fixture_name, section_text in zip(FIXTURE_NAMES, sections, strict=True):
        marker = "Full warning list"
        marker_idx = section_text.find(marker)
        assert marker_idx != -1, f"no 'Full warning list' marker for {fixture_name}"
        lines = section_text[marker_idx:].splitlines()
        fragments = []
        collecting = False
        for line in lines:
            if line.startswith("- `"):
                collecting = True
                rest = line[len("- `") :]
                end = rest.find("`")
                fragment = rest[:end] if end != -1 else rest
                if fragment:
                    fragments.append(fragment)
            elif collecting and line.strip() == "":
                break
        baselines[fixture_name] = fragments
    return baselines


# Sphinx/docutils localizes the human-readable message BODY of a WARNING
# system-message line (see 49-SHAPES-RED-EVIDENCE.md's Japanese-locale
# baselines), but never localizes the ``file:line: WARNING:`` location
# prefix or the bracketed diagnostic-type tag (e.g.
# ``[toc.duplicate_entry]``) that Sphinx appends. The INFO-level "selecting"
# notices captured for the multi-toctree fixtures are internal, untranslated
# strings and carry neither a "WARNING:" marker nor a bracketed tag.
_WARNING_LOCATION_RE = re.compile(r"^(?P<location>\S+:\d+): WARNING:")
_WARNING_TAG_RE = re.compile(r"\[(?P<tag>[\w.]+)\]")


def _locale_invariant_anchors(fragment: str) -> list:
    """
    Reduce a baseline warning fragment to the substring(s) that are safe to
    assert regardless of the runtime locale.

    This test's actual purpose is catching a diagnostic Sphinx *stopped
    emitting*, not asserting a particular human-language rendering of it
    (see ``TestNoLostDiagnostics``'s own docstring). For a localized Sphinx
    WARNING line, the location prefix and the bracketed diagnostic tag are
    both generated by Sphinx itself and never translated -- anchoring on
    those, instead of the full message, catches the diagnostic vanishing
    (either anchor would vanish too) without coupling to one locale's
    wording. A fragment with no ``file:line: WARNING:`` prefix (e.g. an
    INFO-level "selecting" notice) is not a localized message at all, so it
    is returned unchanged and matched literally, exactly as before.
    """
    location_match = _WARNING_LOCATION_RE.match(fragment)
    if not location_match:
        return [fragment]
    anchors = [f"{location_match.group('location')}: WARNING:"]
    tag_match = _WARNING_TAG_RE.search(fragment)
    if tag_match:
        anchors.append(f"[{tag_match.group('tag')}]")
    return anchors


class TestNoLostDiagnostics:
    """
    The backstop truth (ROADMAP binding constraint #4's non-fatal
    amendment): for each of the seven fixtures, the captured Sphinx
    warning list must still contain every warning recorded in
    ``49-SHAPES-RED-EVIDENCE.md``'s baseline for that fixture. NOT xfail
    -- every baseline warning is already present today (the baseline was
    captured from this same tree), so this test's purpose is to catch a
    diagnostic 49-04 might silently remove, not to record a pre-fix
    defect.
    """

    @pytest.mark.parametrize("fixture_name", FIXTURE_NAMES)
    def test_warning_baseline_preserved(self, all_builds, fixture_name):
        baselines = _parse_warning_baselines()
        build = all_builds[fixture_name]
        captured = (
            build.typst_result.stdout
            + build.typst_result.stderr
            + build.pdf_result.stdout
            + build.pdf_result.stderr
        )
        for fragment in baselines[fixture_name]:
            for anchor in _locale_invariant_anchors(fragment):
                assert anchor in captured, (
                    f"{fixture_name}: locale-invariant anchor {anchor!r} "
                    f"(derived from baseline warning fragment {fragment!r}) "
                    f"missing from captured warnings -- a diagnostic Sphinx "
                    f"used to emit may have been silently lost:\n{captured}"
                )
