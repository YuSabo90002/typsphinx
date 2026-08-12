"""
Phase 48 plan 01, Task 3: real-``sphinx-build``-plus-``typst.compile()`` gate
recording the pre-fix RED for the compile-time cross-reference guard
(XREF-03, SC#1) as strict ``xfail`` -- the per-master divergence
``builder.master_included_docnames`` (a union across ALL masters) cannot
express, because it cannot know which master is currently asking.

``tests/fixtures/xref_per_master_guard_gate/`` reproduces the divergence with
TWO masters (``alpha.typ`` for docname ``index``, ``bravo_master.typ`` for
docname ``bravo``) whose content files carry a BYTE-IDENTICAL ``:ref:``
sentence into a section reachable only from ``index``'s own toctree. A single
SHARED content file is deliberately NOT used here: the include-dedup ledger
this tree carries is per-BUILD, not per-master (defect A, Phase 49's own
scope), so a document toctree'd by two masters is ``#include()``d into only
ONE of them today -- unrelated to what this fixture proves. Two content
files carrying the identical reference line, asserted byte-identical, proves
the SAME thing without depending on defect A's eventual fix.

Because the fixture's own build FATALS on the unfixed tree (``bravo``'s
wrapper dangles on the label its content file shares with ``alpha``'s), the
class-scoped build fixture below deliberately does NOT assert
``result.returncode == 0`` -- a fixture-level assertion would error every
test in the class instead of letting each xfail record its own RED.

Every asserted value in this module is taken from
``48-EXPECTED-STRUCTURE.md`` -- never read off a fresh build. Every RED this
module records is traced to ``48-RED-EVIDENCE.md``'s Failure mode 1 and
Baseline 3 sections.

Deviation from ``48-01-PLAN.md``'s literal Task 3 text (documented in
``48-01-SUMMARY.md``): the plan's own action text lists all six tests here as
strict xfails, but ``alpha``'s own destination-based PDF assertion (test 2,
below) is TRUE on the unfixed tree today -- ``alpha.typ``'s wrapper legitimately
``#include()``s ``target.typ`` via its own toctree both before and after this
phase, so its compiled PDF's link destinations already carry
``target:guarded-target-section`` pre-fix. Marking it strict ``xfail`` would
XPASS on this plan's own tree, which is exactly the failure mode a strict
``xfail`` exists to catch -- the same principle the plan's own text applies
to test 4 in the opposite direction ("test 4 must NOT be written as a plain
non-xfail invariance guard"). Test 2 is therefore the mirror case: a plain,
non-xfail invariance guard, not a strict xfail.
"""

import io
import re
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
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

FIXTURES_DIR = Path(__file__).parent / "fixtures"
PER_MASTER_FIXTURE_DIR = FIXTURES_DIR / "xref_per_master_guard_gate"
COLLISION_FIXTURE_DIR = FIXTURES_DIR / "xref_label_collision_guard_gate"

# The 48-EXPECTED-STRUCTURE.md "Guard contract" fully-substituted form for
# label `target:guarded-target-section`, tolerant of the body's exact
# content bytes (`.*?`) since only the GUARD SHAPE -- not the body -- is
# under test here. Anchored so it can NEVER match a plain, unguarded
# `link(<target:guarded-target-section>, ` form (48-01-PLAN.md Task 3's own
# instruction for test 1).
_PER_MASTER_GUARD_PATTERN = re.compile(
    r"context \{ let __tsx_body = \[#\{.*?\}\]; "
    r"if query\(<target:guarded-target-section>\)\.len\(\) > 0 \{ "
    r"link\(<target:guarded-target-section>, __tsx_body\) \} else \{ __tsx_body \} \}"
)

# Same guard shape for the collision fixture's colliding label.
_COLLISION_GUARD_PATTERN = re.compile(
    r"context \{ let __tsx_body = \[#\{.*?\}\]; "
    r"if query\(<a_u2f_b:nested-target>\)\.len\(\) > 0 \{ "
    r"link\(<a_u2f_b:nested-target>, __tsx_body\) \} else \{ __tsx_body \} \}"
)

# Every strict-xfail `reason=` below is a short, INLINE string literal (not
# a named constant) so the reason text -- including the plan id that flips
# the test -- sits textually adjacent to the decorator call itself, and the
# whole decorator fits on one physical line under `black`'s 88-column
# limit. The FULL explanation for each is a comment directly above its
# decorator.


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typstpdf`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``)
    so the exact interpreter/venv running this test is reused, per this
    repo's established NixOS-sandbox-safe convention (every other gate
    module in this suite carries its own copy of this helper rather than
    importing a sibling module's).
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


def _strip_raw_literals(typ_text: str) -> str:
    """Drop ``raw("...")`` inline-literal segments before scanning for
    labels -- prose that quotes a label/reference form as an rST inline
    literal renders as a ``raw("...")`` string literal, not a real Typst
    label expression, and would masquerade as one in a naive scan."""
    return re.sub(r'raw\("(?:[^"\\]|\\.)*"\)', "", typ_text)


def _link_annotation_dests(pdf_bytes: bytes) -> list[str]:
    """
    Return the destination NAME of every ``/Link`` annotation across every
    page of the compiled PDF -- reading ``/Dest`` directly and falling back
    to the action dictionary's ``/D`` destination entry -- as a list of
    strings.

    Typst registers a NAMED PDF destination (recoverable here as a plain
    string) only for a label that participates in the document's
    ``#outline()`` (i.e. a heading anchor); a link to a label that is NOT a
    heading anchor still compiles and still produces a real, working
    ``/Link`` annotation, but its ``/Dest`` is an unnamed POSITIONAL array
    (page reference + ``/XYZ`` + coordinates) with no string to recover --
    such annotations contribute nothing to the returned list rather than
    raising. Every fixture this module drives (``xref_per_master_guard_gate``
    via ``sphinx.ext.autosectionlabel``, and ``xref_label_collision_guard_gate``
    via the decoy's own un-labelled heading) deliberately routes its ``:ref:``
    at a heading anchor for exactly this reason -- see each fixture's
    ``conf.py`` comment block.
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    dests: list[str] = []
    for page in reader.pages:
        annots = page.get("/Annots") or []
        for annot in annots:
            obj = annot.get_object()
            if obj.get("/Subtype") != "/Link":
                continue
            dest = obj.get("/Dest")
            if isinstance(dest, str):
                dests.append(dest)
                continue
            action = obj.get("/A")
            if action is not None:
                action_obj = action.get_object()
                action_dest = action_obj.get("/D")
                if isinstance(action_dest, str):
                    dests.append(action_dest)
    return dests


@pytest.fixture(scope="class")
def per_master_guard_build(tmp_path_factory):
    """
    Build ``xref_per_master_guard_gate`` ONCE per class via
    ``-b typstpdf`` and return both compiled PDFs' bytes plus both emitted
    content files' text -- tolerating a non-zero overall build result
    (``bravo``'s wrapper FATALS on the unfixed tree, so ``bravo_master.pdf``
    never gets written) rather than asserting success here, so each test's
    own ``xfail`` records the RED instead of every test in the class erroring
    at fixture setup.
    """
    build_dir = tmp_path_factory.mktemp("xref_per_master_guard")
    result = _run_sphinx_build_typstpdf(PER_MASTER_FIXTURE_DIR, build_dir)

    def _read_text(name: str) -> str:
        path = build_dir / name
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def _read_bytes(name: str) -> bytes:
        path = build_dir / name
        return path.read_bytes() if path.exists() else b""

    return {
        "result": result,
        "index_typ": _read_text("index.typ"),
        "bravo_typ": _read_text("bravo.typ"),
        "alpha_pdf": _read_bytes("alpha.pdf"),
        "bravo_pdf": _read_bytes("bravo_master.pdf"),
    }


@pytest.fixture(scope="class")
def collision_guard_build(tmp_path_factory):
    """
    Build ``xref_label_collision_guard_gate`` ONCE per class via
    ``-b typstpdf`` (this fixture compiles cleanly both before and after this
    phase -- only the emitted content's SHAPE and the link's ultimate
    destination change) and return the emitted content file's text plus the
    compiled PDF's bytes.
    """
    build_dir = tmp_path_factory.mktemp("xref_label_collision_guard")
    result = _run_sphinx_build_typstpdf(COLLISION_FIXTURE_DIR, build_dir)

    def _read_text(name: str) -> str:
        path = build_dir / name
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def _read_bytes(name: str) -> bytes:
        path = build_dir / name
        return path.read_bytes() if path.exists() else b""

    return {
        "result": result,
        "index_typ": _read_text("index.typ"),
        "manual_pdf": _read_bytes("manual.pdf"),
    }


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are required for the compile-time cross-reference guard gate",
)
class TestXrefCompileTimeGuardRenderGate:
    """
    XREF-03 / SC#1: the per-master divergence a build-time union across all
    masters cannot express, plus the one measured false-negative class
    (label-namespace collision) the compile-time guard accepts as a narrow,
    documented cost.
    """

    # Pre-fix, both content files already emit the IDENTICAL plain
    # link(<target:guarded-target-section>, ...) form (the identity half
    # already holds), but neither carries the guarded
    # context { ... if query(...).len() > 0 { ... } ... } shape yet
    # (48-RED-EVIDENCE.md Failure mode 1) -- fails on the guard-shape half.
    @pytest.mark.xfail(strict=True, reason="48-02 lands the guard (RED-EVIDENCE #1)")
    def test_guard_expression_identical_in_both_masters(self, per_master_guard_build):
        """
        48-EXPECTED-STRUCTURE.md "Fixture: xref_per_master_guard_gate" §1:
        both content files' emitted reference line is the IDENTICAL guarded
        expression -- the identity half already holds pre-fix (both files
        emit the same PLAIN link), so this test must fail on the GUARD-SHAPE
        half pre-fix, not the identity half, or the strict xfail below would
        XPASS.
        """
        index_typ = _strip_raw_literals(per_master_guard_build["index_typ"])
        bravo_typ = _strip_raw_literals(per_master_guard_build["bravo_typ"])

        index_match = _PER_MASTER_GUARD_PATTERN.search(index_typ)
        bravo_match = _PER_MASTER_GUARD_PATTERN.search(bravo_typ)

        assert index_match is not None, (
            "index.typ does not carry the guarded "
            f"context {{ ... if query(...).len() > 0 {{ ... }} ... }} "
            f"expression for target:guarded-target-section:\n{index_typ}"
        )
        assert bravo_match is not None, (
            "bravo.typ does not carry the guarded "
            f"context {{ ... if query(...).len() > 0 {{ ... }} ... }} "
            f"expression for target:guarded-target-section:\n{bravo_typ}"
        )
        assert index_match.group(0) == bravo_match.group(0), (
            "The guarded expression differs between the two masters' "
            f"content files -- expected byte-identical:\n"
            f"index: {index_match.group(0)!r}\nbravo: {bravo_match.group(0)!r}"
        )

    def test_alpha_pdf_links_to_target(self, per_master_guard_build):
        """
        48-EXPECTED-STRUCTURE.md §1: alpha's compiled PDF has the target's
        namespaced label among its link destinations. NOT an xfail (see
        module docstring): alpha's wrapper legitimately includes target.typ
        via its own toctree both before and after this phase, so this
        destination is present on the unfixed tree too -- an invariance
        guard, not a flip.
        """
        dests = _link_annotation_dests(per_master_guard_build["alpha_pdf"])
        assert "target:guarded-target-section" in dests, (
            "alpha.pdf's link destinations do not include "
            f"target:guarded-target-section: {sorted(dests)}"
        )

    # Pre-fix (48-RED-EVIDENCE.md Failure mode 1), bravo_master.typ's
    # compile FATALS outright (TypstError: label does not exist in the
    # document), so bravo_master.pdf is never written and this destination
    # check cannot even run against real PDF bytes.
    @pytest.mark.xfail(strict=True, reason="48-02 lands the guard (RED-EVIDENCE #1)")
    def test_bravo_pdf_does_not_link_to_target(self, per_master_guard_build):
        """
        48-EXPECTED-STRUCTURE.md §1: bravo's compiled PDF does NOT have the
        target's namespaced label among its link destinations -- bravo's
        wrapper never #include()s target.typ, so the guard's query() finds
        nothing and the reference degrades to plain text.
        """
        dests = _link_annotation_dests(per_master_guard_build["bravo_pdf"])
        assert "target:guarded-target-section" not in dests, (
            "bravo_master.pdf's link destinations unexpectedly include "
            f"target:guarded-target-section: {sorted(dests)}"
        )

    # Pre-fix (48-RED-EVIDENCE.md Failure mode 1), -b typstpdf over this
    # fixture exits non-zero and the combined output contains 'does not
    # exist in the document' -- the build-time union cannot express a
    # per-master answer, so bravo's reference is NOT degraded and its
    # wrapper compile fatals directly.
    @pytest.mark.xfail(strict=True, reason="48-02 lands the guard (RED-EVIDENCE #1)")
    def test_no_dangling_label_fatal_either_master(self, per_master_guard_build):
        """
        48-EXPECTED-STRUCTURE.md §1: neither compile raises a Typst error --
        the build exits 0 overall and the combined output contains no
        dangling-label error text. Written as a real invariance guard, NOT a
        plain non-xfail test, per the plan's own explicit instruction (a
        plain test here would fail Wave 1's own gate, since it is false on
        the unfixed tree).
        """
        result = per_master_guard_build["result"]
        combined = result.stdout + result.stderr
        assert result.returncode == 0, (
            f"Expected -b typstpdf to exit 0:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert (
            "does not exist in the document" not in combined
        ), f"Typst reported a dangling label:\n{combined}"

    # Pre-fix, bravo_master.pdf is never written (Failure mode 1's direct
    # compile fatal), so its pypdf text extraction cannot even run.
    @pytest.mark.xfail(strict=True, reason="48-02 lands the guard (RED-EVIDENCE #1)")
    def test_reference_text_identical_in_both_pdfs(self, per_master_guard_build):
        """
        D-02 invariance: a degraded reference renders exactly the same
        visible text as the linked form, with no visual marking -- the
        reader sees identical prose whether or not the reference happens to
        be clickable in that particular compiled wrapper.
        """
        alpha_reader = pypdf.PdfReader(io.BytesIO(per_master_guard_build["alpha_pdf"]))
        alpha_text = "".join(page.extract_text() for page in alpha_reader.pages)
        bravo_reader = pypdf.PdfReader(io.BytesIO(per_master_guard_build["bravo_pdf"]))
        bravo_text = "".join(page.extract_text() for page in bravo_reader.pages)

        assert (
            "Guarded Target Section" in alpha_text
        ), f"alpha.pdf is missing the reference's visible text:\n{alpha_text}"
        assert "Guarded Target Section" in bravo_text, (
            f"bravo_master.pdf is missing the reference's visible text "
            f"(D-02 invariance -- must render identically whether linked "
            f"or degraded):\n{bravo_text}"
        )

    # Pre-fix (48-RED-EVIDENCE.md Baseline 3), the reference degrades to
    # plain text via the build-time union (a/b is outside
    # master_included_docnames) -- no link at all is emitted, so neither
    # the guarded-expression half nor the PDF-destination half holds yet.
    @pytest.mark.xfail(strict=True, reason="48-02/03 land the guard (RED-EVIDENCE)")
    def test_label_collision_guard_links_to_decoy(self, collision_guard_build):
        """
        48-EXPECTED-STRUCTURE.md "Fixture: xref_label_collision_guard_gate":
        the measured, ACCEPTED false-negative. -b typstpdf exits 0, the
        emitted index.typ carries the guarded expression on the colliding
        label a_u2f_b:nested-target, and the compiled PDF's link
        destinations DO include a_u2f_b:nested-target -- resolving to the
        DECOY's heading, even though the reference's real intended target
        (a/b, :orphan:, excluded from the toctree) is absent from the
        compiled master. This is a characterization test of a known,
        narrow, documented limit (48-EXPECTED-STRUCTURE.md's own
        explanation of why), not a defect gate.
        """
        result = collision_guard_build["result"]
        assert result.returncode == 0, (
            f"Expected -b typstpdf to exit 0:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        index_typ = _strip_raw_literals(collision_guard_build["index_typ"])
        match = _COLLISION_GUARD_PATTERN.search(index_typ)
        assert match is not None, (
            "index.typ does not carry the guarded expression for the "
            f"colliding label a_u2f_b:nested-target:\n{index_typ}"
        )

        dests = _link_annotation_dests(collision_guard_build["manual_pdf"])
        assert "a_u2f_b:nested-target" in dests, (
            "manual.pdf's link destinations do not include the colliding "
            f"label a_u2f_b:nested-target: {sorted(dests)}"
        )
