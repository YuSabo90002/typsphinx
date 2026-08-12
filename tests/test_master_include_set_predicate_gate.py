"""
Phase 47 gap-closure plan 13 (historical): real-``sphinx-build`` subprocess
gate that originally closed gap 9b / ``47-REVIEW.md`` CR-01 -- the BLOCKER
that the build-time toctree-closure computation this module's now-deleted
unit tests once exercised directly was a FIFTH site reading
``typst_documents`` and needing the "is this entry usable" answer, and it
never consulted ``_is_usable_typst_documents_entry()``. It instead built its
``masters`` list via a bare ``if entry`` truthiness filter (``builder.py``
line 269), which the four already-wired sites (47-11) abandoned.

Two independent consequences followed from that private, weaker spelling:

1. A silent wrong artifact escalating to a hard compile fatal -- an
   under-length ``typst_documents`` entry (e.g. ``("ghost",)``) still
   contributed its docname AND its whole toctree closure to the build-time
   include set, even though it correctly produced NO wrapper file. A real
   master's ``:ref:`` into that phantom-included subtree was judged "safe
   to link" and emitted a Typst ``link(<label>)`` that no compiled
   document would ever contain.
2. An uncaught crash -- a non-hashable ``entry[0]`` (e.g. a ``list``, a
   plausible ``conf.py`` typo, since Sphinx does not type-check config
   values) reached the BFS's unguarded ``docname in included`` /
   ``included.add(docname)`` ``set`` operations and raised a raw
   ``TypeError: unhashable type: 'list'``.

Structured like ``tests/test_collision_predicate_completeness_gate.py`` (one
fixture-directory constant per scenario, one ``_run_sphinx_build`` helper
duplicated per this repo's own convention). The original 8-test module
recorded the pre-fix RED via strict expected-failure markers; those markers
were removed when the Phase 47 fix landed (commit ``e422bfb``), so every
test in this module has been a plain, unmarked assertion since.

Phase 48 (XREF-04, D-09, SC#3) deletes that build-time toctree-closure
computation and its include-set builder attribute outright -- the
label-existence question they answered moved to Typst COMPILE time via
``TypstTranslator._label_existence_guard()`` (``48-EXPECTED-STRUCTURE.md``).
The FOUR unit tests that called the deleted method directly
(``TestGhostEntryIncludeSetUnit`` / ``TestUnhashableDocnameIncludeSetUnit`` /
``TestMasterIncludeSetInvarianceGuards``, each of which held exactly that
method's own unit coverage) lost their subject entirely and are removed, not
adapted, along with their now-empty containing classes and the ``types``
import they alone used.

Four tests remain, all end-to-end ``-b typst``/``-b typstpdf`` subprocess
gates, unrelated to the deleted builder method's own unit surface:

- ``TestGhostEntryXrefRenderGate::test_ghost_entry_subtree_xref_degrades_typst``
  -- flips (Phase 48): the phantom-included subtree's namespaced label now
  appears INSIDE the D-07 compile-time guard's conditional, never
  unconditionally suppressed by a build-time union.
- ``TestGhostEntryXrefRenderGate::test_ghost_entry_no_dangling_label_typstpdf``
  -- unchanged: the malformed ``('ghost',)`` entry is still separately
  reported by ``finish()``'s existing under-length-entry diagnostic,
  unrelated to the guard.
- ``TestUnhashableDocnameRenderGate::test_unhashable_docname_skipped_gracefully_typst``
  -- unchanged: a different fifth-site predicate-guard defect, already
  fixed in Phase 47.
- ``TestUnhashableDocnameRenderGate::test_unhashable_docname_reported_by_finish_typstpdf``
  -- unchanged: unrelated to the guard.

The verbatim pre-fix transcripts for all eight ORIGINAL tests (including the
four now-removed unit tests) are recorded in full in
``47-GAP2-RED-EVIDENCE.md``.
"""

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

FIXTURES_DIR = Path(__file__).parent / "fixtures"
BLD03_GHOST_ENTRY_FIXTURE_DIR = FIXTURES_DIR / "bld03_ghost_entry_xref_gate"
BLD03_UNHASHABLE_FIXTURE_DIR = FIXTURES_DIR / "bld03_unhashable_docname_gate"


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard. Every gate module in this suite carries its own
    copy of this helper rather than importing a sibling module's.
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


def _strip_raw_literals(typ_text: str) -> str:
    """Drop ``raw("...")`` inline-literal segments before scanning for
    labels -- prose that quotes a label/reference form as an rST inline
    literal renders as a ``raw("...")`` string literal, not a real Typst
    label expression, and would masquerade as one in a naive scan.
    """
    return re.sub(r'raw\("(?:[^"\\]|\\.)*"\)', "", typ_text)


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the master include-set predicate gate",
)
class TestGhostEntryXrefRenderGate:
    """
    BLD-03, failure mode 1: an under-length ``typst_documents`` entry
    (``("ghost",)``) still contributed its docname and its whole toctree
    closure to the (now-deleted, Phase 48) build-time include set, so a
    real master's ``:ref:`` into that phantom-included subtree was wrongly
    judged safe to link.
    """

    def test_ghost_entry_subtree_xref_degrades_typst(self, tmp_path):
        """
        FLIPS (Phase 48, XREF-04, ``48-EXPECTED-STRUCTURE.md``): the
        emitted ``index.typ`` now carries the phantom-included subtree's
        namespaced label INSIDE the D-07 compile-time guard's conditional
        -- never unconditionally suppressed by a build-time union, which
        is deleted. ``ghost_child.typ`` is never ``#include()``d into the
        compiled ``manual.typ`` (the malformed ``('ghost',)`` entry
        produces no wrapper regardless of its own toctree), so at Typst
        compile time ``query(<ghost_child:ghost-child-label>)`` genuinely
        finds nothing and the guard's ``else`` branch fires -- see
        ``test_ghost_entry_no_dangling_label_typstpdf`` below for the
        real-compile half of this same outcome, unchanged.
        """
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(BLD03_GHOST_ENTRY_FIXTURE_DIR, build_dir, "typst")

        assert result.returncode == 0, (
            f"Expected -b typst to still succeed (the under-length entry "
            f"is tolerated, not fatal):\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        index_typ = (build_dir / "index.typ").read_text(encoding="utf-8")
        scannable = _strip_raw_literals(index_typ)
        assert "link(<ghost_child:ghost-child-label>," in scannable, (
            "The guarded expression for the phantom-included 'ghost' "
            "subtree's label was not found -- expected it inside the "
            f"D-07 guard's conditional:\n{index_typ}"
        )
        assert "Ghost Child Target Section" in scannable, (
            f"The degraded cross-reference did not render its text as "
            f"plain inline content:\n{index_typ}"
        )
        combined_output = result.stdout + result.stderr
        assert "produces no wrapper file" in combined_output, (
            f"Expected the existing under-length-entry warning naming "
            f"the 'ghost' entry:\n{combined_output}"
        )

    def test_ghost_entry_no_dangling_label_typstpdf(self, tmp_path):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(BLD03_GHOST_ENTRY_FIXTURE_DIR, build_dir, "typstpdf")
        combined_output = result.stdout + result.stderr

        assert result.returncode != 0, (
            f"Expected -b typstpdf to fail overall (the under-length "
            f"'ghost' entry is still reported by finish()):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "does not exist in the document" not in combined_output, (
            f"Typst reported a dangling label -- the ghost-child "
            f"cross-reference was not degraded:\n{combined_output}"
        )
        assert "has no target element" in combined_output, (
            f"Expected finish()'s existing under-length-entry "
            f"diagnostic:\n{combined_output}"
        )
        pdf_path = build_dir / "manual.pdf"
        assert pdf_path.exists(), (
            f"D-02's attempt-all-then-raise contract: the well-formed "
            f"'index'/'manual.typ' master should still get its PDF even "
            f"though the malformed 'ghost' entry fails:\n{combined_output}"
        )
        assert pdf_path.read_bytes().startswith(
            b"%PDF"
        ), "manual.pdf does not start with the %PDF magic marker"


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the master include-set predicate gate",
)
class TestUnhashableDocnameRenderGate:
    """
    BLD-03, failure mode 2: a non-hashable ``entry[0]`` reaches the BFS's
    unguarded ``set`` operations and aborts the whole build with an
    uncaught ``TypeError``.
    """

    def test_unhashable_docname_skipped_gracefully_typst(self, tmp_path):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(BLD03_UNHASHABLE_FIXTURE_DIR, build_dir, "typst")
        combined_output = result.stdout + result.stderr

        assert result.returncode == 0, (
            f"Expected -b typst to still succeed (the non-hashable entry "
            f"is tolerated, not fatal):\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "TypeError" not in combined_output, (
            f"An uncaught TypeError leaked into the build output:\n"
            f"{combined_output}"
        )
        assert "unhashable type" not in combined_output, (
            f"An uncaught 'unhashable type' traceback leaked into the "
            f"build output:\n{combined_output}"
        )
        assert "produces no wrapper file" in combined_output, (
            f"Expected the existing entry-usability warning naming the "
            f"non-hashable entry:\n{combined_output}"
        )
        assert (build_dir / "index.typ").exists(), (
            f"Expected index.typ (the well-formed entry's content file) "
            f"to exist:\n{combined_output}"
        )
        assert (build_dir / "real.typ").exists(), (
            f"Expected real.typ (the well-formed entry's wrapper) to "
            f"exist:\n{combined_output}"
        )

    def test_unhashable_docname_reported_by_finish_typstpdf(self, tmp_path):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(BLD03_UNHASHABLE_FIXTURE_DIR, build_dir, "typstpdf")
        combined_output = result.stdout + result.stderr

        assert result.returncode != 0, (
            f"Expected -b typstpdf to fail overall (the non-hashable "
            f"entry is still reported):\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "non-str docname" in combined_output, (
            f"Expected finish()'s existing non-str-docname diagnostic:\n"
            f"{combined_output}"
        )
        assert "TypeError" not in combined_output, (
            f"An uncaught TypeError leaked into the build output:\n"
            f"{combined_output}"
        )
        real_pdf = build_dir / "real.pdf"
        assert real_pdf.exists(), (
            f"D-02's attempt-all-then-raise contract: the well-formed "
            f"'index'/'real.typ' master should still get its PDF:\n"
            f"{combined_output}"
        )
