"""
Phase 48 plan 02, Task 1: real-``sphinx-build``-plus-``typst.compile()`` gate
for the compile-time cross-reference guard (XREF-03, SC#1) -- the per-master
divergence a build-time union across ALL masters could not express, because
it could not know which master was currently asking.

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

Every asserted value in this module is taken from
``48-EXPECTED-STRUCTURE.md`` -- never read off a fresh build. Every test here
was originally recorded RED (as a strict ``xfail``) in plan 48-01, against
``48-RED-EVIDENCE.md``'s Failure mode 1 and Baseline 3 sections; plan 48-02
lands the compile-time guard and flips every one of these tests to a plain,
non-xfail assertion (SC#1).
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
# instruction for test 1). re.DOTALL: the emitted body streams across a
# real newline between the guard's open string and its first child (the
# SAME newline 48-RED-EVIDENCE.md's own pre-fix transcript already showed
# between `link(<label>, ` and `text(...)` -- an existing translator
# emission characteristic this phase does not touch), so `.` must match
# `\n` here or the pattern spuriously fails to match a correctly-guarded
# body.
_PER_MASTER_GUARD_PATTERN = re.compile(
    r"context \{ let __tsx_body = \[#\{.*?\}\]; "
    r"if query\(<target:guarded-target-section>\)\.len\(\) > 0 \{ "
    r"link\(<target:guarded-target-section>, __tsx_body\) \} else \{ __tsx_body \} \}",
    re.DOTALL,
)

# Same guard shape for the collision fixture's colliding label.
_COLLISION_GUARD_PATTERN = re.compile(
    r"context \{ let __tsx_body = \[#\{.*?\}\]; "
    r"if query\(<a_u2f_b:nested-target>\)\.len\(\) > 0 \{ "
    r"link\(<a_u2f_b:nested-target>, __tsx_body\) \} else \{ __tsx_body \} \}",
    re.DOTALL,
)


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
    content files' text. Deliberately does NOT assert
    ``result.returncode == 0`` here -- pre-fix, ``bravo``'s wrapper FATALS
    (so ``bravo_master.pdf`` never gets written); a fixture-level assertion
    would error every test in the class instead of letting each test record
    its own outcome. Post-fix (this plan), the build exits 0 and every test
    below is a plain assertion, but the fixture itself stays tolerant.
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
    destination change) and return the emitted content files' text plus the
    compiled PDF's bytes. ``a_u2f_b.typ`` is the decoy's own included
    content file -- its emitted anchor label lives there, not in
    ``index.typ`` (Phase 55 plan 01, XREF-05).
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
        "decoy_typ": _read_text("a_u2f_b.typ"),
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

    def test_label_collision_no_longer_links_to_decoy(self, collision_guard_build):
        """
        XREF-05 (Phase 55 plan 01, D-01/D-02/D-04): a CLOSED defect. Until
        this phase, ``_sanitize_label`` was not injective -- two distinct
        docnames (``a/b`` and the decoy ``a_u2f_b``) could sanitize to the
        SAME label, so a reference whose real target (``a/b``, ``:orphan:``,
        excluded from the toctree) was absent from the compiled master
        resolved to the DECOY's identically-spelled heading instead of
        degrading. That pre-fix behaviour is recorded verbatim, against the
        real pre-fix commit, in ``55-01-RED-EVIDENCE.md`` (binding
        constraint #6) -- this test is that RED evidence's assertion,
        inverted, plus the render gate this module is named for.

        Post-fix: ``-b typstpdf`` still exits 0, ``index.typ`` still carries
        the IDENTICAL guarded ``context { ... if query(...).len() > 0 { ...
        } ... }`` expression on ``a_u2f_b:nested-target`` (the REFERENCE
        side is namespaced by the TARGET docname ``a/b``, whose sanitized
        form does not move -- ``_COLLISION_GUARD_PATTERN`` is unchanged),
        the compiled PDF's link destinations no longer include
        ``a_u2f_b:nested-target`` (the guard's ``query()`` no longer finds a
        same-spelled decoy label, so the reference degrades to plain text),
        the decoy's OWN anchor label has moved to
        ``a_u5f_u2f_b:nested-target`` and appears in the emitted ``.typ``
        (the decoy still gets a label, just a different, non-colliding one),
        and the reference's visible text still renders (the Phase 48 D-02
        invariance -- a degraded reference looks identical to a linked one).
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
            f"reference's namespaced label a_u2f_b:nested-target:\n{index_typ}"
        )

        decoy_typ = _strip_raw_literals(collision_guard_build["decoy_typ"])
        assert "a_u5f_u2f_b:nested-target" in decoy_typ, (
            "a_u2f_b.typ does not carry the decoy's re-escaped, "
            "no-longer-colliding anchor label "
            f"a_u5f_u2f_b:nested-target:\n{decoy_typ}"
        )

        dests = _link_annotation_dests(collision_guard_build["manual_pdf"])
        assert "a_u2f_b:nested-target" not in dests, (
            "manual.pdf's link destinations unexpectedly still include the "
            f"formerly-colliding label a_u2f_b:nested-target: {sorted(dests)}"
        )

        reader = pypdf.PdfReader(io.BytesIO(collision_guard_build["manual_pdf"]))
        manual_text = "".join(page.extract_text() for page in reader.pages)
        assert "Alpha Nested Section" in manual_text, (
            "manual.pdf is missing the reference's visible text -- "
            "':ref:`nested-target`' resolves its default text from the "
            "label's REAL target (a/b.rst's 'Alpha Nested Section' title, "
            "resolved by Sphinx's own domain data at build time, "
            "independent of which document is actually compiled in) -- "
            "the Phase 48 D-02 invariance requires this text render "
            "identically whether the reference ends up linked or "
            f"degraded:\n{manual_text}"
        )
