"""
Phase 47 gap-closure plan 13: real-``sphinx-build`` subprocess gate closing
gap 9b / ``47-REVIEW.md`` CR-01 -- the BLOCKER that
``TypstBuilder._compute_master_included_docnames()`` is a FIFTH site reading
``typst_documents`` and needing the "is this entry usable" answer, and it
never consults ``_is_usable_typst_documents_entry()``. It instead builds its
``masters`` list via a bare ``if entry`` truthiness filter (``builder.py``
line 269), which the four already-wired sites (47-11) abandoned.

Two independent consequences follow from that private, weaker spelling:

1. A silent wrong artifact escalating to a hard compile fatal -- an
   under-length ``typst_documents`` entry (e.g. ``("ghost",)``) still
   contributes its docname AND its whole toctree closure to
   ``master_included_docnames``, even though it correctly produces NO
   wrapper file. A real master's ``:ref:`` into that phantom-included
   subtree is judged "safe to link" and emits a Typst ``link(<label>)``
   that no compiled document will ever contain.
2. An uncaught crash -- a non-hashable ``entry[0]`` (e.g. a ``list``, a
   plausible ``conf.py`` typo, since Sphinx does not type-check config
   values) reaches the BFS's unguarded ``docname in included`` /
   ``included.add(docname)`` ``set`` operations and raises a raw
   ``TypeError: unhashable type: 'list'``.

Structured like ``tests/test_collision_predicate_completeness_gate.py`` (one
fixture-directory constant per scenario, one ``_run_sphinx_build`` helper
duplicated per this repo's own convention) but recording the pre-fix RED as
``xfail(strict=True)``: six of the eight tests below fail on the unfixed
tree; two are invariance guards that already pass and must keep passing. The
verbatim pre-fix transcripts each xfail's ``reason=`` paraphrases are
recorded in full in ``47-GAP2-RED-EVIDENCE.md``.
"""

import re
import subprocess
import sys
import types
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
    (``("ghost",)``) still contributes its docname and its whole toctree
    closure to ``master_included_docnames``, so a real master's ``:ref:``
    into that phantom-included subtree is wrongly judged safe to link.
    """

    def test_ghost_entry_subtree_xref_degrades_typst(self, tmp_path):
        build_dir = tmp_path / "build"
        result = _run_sphinx_build(BLD03_GHOST_ENTRY_FIXTURE_DIR, build_dir, "typst")

        assert result.returncode == 0, (
            f"Expected -b typst to still succeed (the under-length entry "
            f"is tolerated, not fatal):\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        index_typ = (build_dir / "index.typ").read_text(encoding="utf-8")
        scannable = _strip_raw_literals(index_typ)
        assert "link(<ghost_child:" not in scannable, (
            f"A link(<ghost_child:...>) label link into the "
            f"phantom-included 'ghost' subtree was emitted; it must "
            f"degrade to plain text instead:\n{index_typ}"
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


class TestGhostEntryIncludeSetUnit:
    """
    BLD-03 failure mode 1's load-bearing unit half -- importing
    ``TypstBuilder`` INSIDE the test body so a signature change lands as an
    xfail rather than a module-level collection error.
    """

    def test_ghost_entry_excluded_from_master_include_set(self, temp_sphinx_app):
        from typsphinx.builder import TypstBuilder

        app = temp_sphinx_app
        builder = TypstBuilder(app, app.env)
        builder.env = types.SimpleNamespace(toctree_includes={"ghost": ["ghost_child"]})
        builder.config.typst_documents = [
            ("index", "manual.typ", "T", "A"),
            ("ghost",),
        ]

        result = builder._compute_master_included_docnames()

        assert result == {"index"}, (
            f"Expected the under-length ('ghost',) entry to contribute "
            f"NEITHER 'ghost' NOR its toctree child 'ghost_child' to the "
            f"include set, got: {sorted(result)}"
        )


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


class TestUnhashableDocnameIncludeSetUnit:
    """
    BLD-03 failure mode 2's load-bearing unit half -- importing
    ``TypstBuilder`` INSIDE the test body so a signature change lands as an
    xfail rather than a module-level collection error.
    """

    def test_compute_master_included_docnames_tolerates_unhashable_docname(
        self, temp_sphinx_app
    ):
        from typsphinx.builder import TypstBuilder

        app = temp_sphinx_app
        builder = TypstBuilder(app, app.env)
        builder.env = types.SimpleNamespace(toctree_includes={})
        builder.config.typst_documents = [
            (["weird"], "manual.typ", "T", "A"),
            ("index", "real.typ", "T", "A"),
        ]

        result = builder._compute_master_included_docnames()

        assert result == {"index"}, (
            f"Expected the non-hashable entry to be skipped without "
            f"raising, leaving only 'index', got: {sorted(result)}"
        )


class TestMasterIncludeSetInvarianceGuards:
    """
    NOT xfail -- these pass today and must keep passing after the fifth
    site is routed through the shared predicate, proving the new filter
    does not over-reject any currently-working configuration.
    """

    def test_well_formed_masters_still_yield_full_toctree_closure(
        self, temp_sphinx_app
    ):
        from typsphinx.builder import TypstBuilder

        app = temp_sphinx_app
        builder = TypstBuilder(app, app.env)
        builder.env = types.SimpleNamespace(
            toctree_includes={
                "master_one": ["child_one"],
                "master_two": ["child_two"],
            }
        )
        builder.config.typst_documents = [
            ("master_one", "one.typ", "T1", "A1"),
            ("master_two", "two.typ", "T2", "A2"),
        ]

        result = builder._compute_master_included_docnames()

        assert result == {
            "master_one",
            "child_one",
            "master_two",
            "child_two",
        }, (
            f"Expected the full transitive closure of both well-formed "
            f"masters, unchanged by the predicate filter, got: "
            f"{sorted(result)}"
        )

    def test_empty_typst_documents_still_yields_empty_set(self, temp_sphinx_app):
        from typsphinx.builder import TypstBuilder

        app = temp_sphinx_app
        builder = TypstBuilder(app, app.env)
        builder.env = types.SimpleNamespace(toctree_includes={})

        builder.config.typst_documents = []
        assert builder._compute_master_included_docnames() == set(), (
            "Expected an empty typst_documents list to yield an empty "
            "include set -- the documented 'no masters / unknown' "
            "degraded case translator.py relies on to suppress "
            "degradation"
        )

        builder.config.typst_documents = None
        assert builder._compute_master_included_docnames() == set(), (
            "Expected typst_documents=None to also yield an empty " "include set"
        )
