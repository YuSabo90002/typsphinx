"""
Fast, offline regression gate for the duplicate-include-label fix
(Phase 15, GATE-02).

Deterministic, network-free reproduction of the nineteenth fatal the slow
full-corpus gate (``tests/test_corpus_gate.py::TestCorpusRenderGate``) surfaced
against Sphinx's own ``doc/`` tree. After bugs #17/#18 unblocked the semantic
label-resolution path, ``typst.compile()`` reached the label-uniqueness pass and
aborted with::

    TypstError: label `<module-sphinx.ext.apidoc>` occurs multiple times
    in the document

Root cause: NOT a within-document anchor bug. Sphinx's ``doc/index.rst`` lists
``usage/extensions/index`` in TWO places -- directly in its "Reference" toctree
AND nested under ``usage/index`` in its "User guide" toctree -- a diamond in the
include graph. ``visit_toctree`` emitted an ``include()`` for every toctree
entry with no deduplication across the master's whole include graph, so the same
``.typ`` was ``#include``d twice. Typst's ``#include()`` flattens each file's
content inline, so including one file twice re-emits EVERY ``<label>`` it defines
(here the ``.. py:module:: sphinx.ext.apidoc`` target id, which docutils
propagates onto apidoc's section, is emitted as the section-heading label). Typst
requires labels unique per compiled document and aborts at the first duplicate.

Fix (Phase 49, COMP-05/COMP-06): a per-master Typst ``state`` array,
published once by each wrapper and read by a static per-emission-site guard
in the shared content file, resolves which occurrence of a repeated toctree
entry is LIVE at Typst COMPILE time, not write time. Every emission site for
a repeated child still emits its own guard line unconditionally (so the same
docname can legitimately be reached and guarded from more than one parent),
but the graph side's DFS claims a child at its FIRST non-traversed appearance
in a master's own traversal, so only ONE of the possibly-several guards for
that child is ever live -- every OTHER guard is structurally dark and its
``include()`` never fires. Each document's content is therefore rendered at
most once per master, every label it defines is emitted exactly once in the
COMPILED document, and every reference (which is NEVER dropped) still
resolves to the single surviving anchor.

This fixture is a minimal diamond: the master ``index`` reaches ``shared`` both
directly and nested under ``sub``; ``shared`` defines a section label (via a
propagated ``.. _shared-anchor:`` explicit target) and a same-document
``:ref:`` back to it (emitted as ``link(<shared-anchor>, ...)``).

Confirmed both directions: FAILS against the pre-Phase-49 translator/builder
with the exact ``label ... occurs multiple times`` fatal (``shared.typ``
``#include``d twice, unconditionally, with no guard mechanism at all), and
PASSES with the fix (two STATIC guard sites for ``shared.typ`` remain on
disk -- one dark, one live -- but the compiled document renders ``shared``'s
content exactly once, compiles to ``%PDF``, and the same-document reference
still resolves).

Drives the full ``-b typstpdf`` path -- NOT ``-b typst`` -- on purpose: the
label-uniqueness fatal only fires inside ``TypstPDFBuilder.finish()``'s
``typst.compile()`` call, so a ``-b typst`` build would emit the duplicate
include but never compile it and thus prove nothing.
"""

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


@pytest.fixture
def duplicate_include_label_render_gate_dir():
    """Return the path to the duplicate_include_label_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "duplicate_include_label_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typstpdf`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``) so
    the exact interpreter/venv running this test is reused, sidestepping the
    documented NixOS-sandbox PATH-shadowing hazard.
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


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are required for the duplicate-include-label "
    "render gate",
)
class TestDuplicateIncludeLabelRenderGate:
    """
    Real-compile regression gate proving a document reachable via more than one
    toctree path renders its content exactly ONCE in the compiled document, so
    the labels it defines are not duplicated in the compiled master and every
    reference still resolves -- delivered by Phase 49's occurrence-indexed
    compile-time guard rule rather than the deleted write-time ledger.

    Requirements: GATE-02 (Phase 15 -- the fast offline reproduction of the
    diamond-include duplicate-label corpus fatal).
    """

    def test_typstpdf_diamond_include_deduplicated(
        self, duplicate_include_label_render_gate_dir, temp_build_dir
    ):
        """
        Build the diamond-toctree fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly (no fatal raised out of the subprocess);
        - ``typst.compile()`` did NOT abort with the label-uniqueness fatal
          ``label ... occurs multiple times`` (the pre-fix failure), nor with a
          dangling ``label ... does not exist`` (the surviving guard must not
          orphan the same-document reference), nor any other compilation
          failure;
        - ``shared.typ`` -- reachable from the master both directly and nested
          under ``sub`` -- carries a literal ``include("shared.typ")`` STATIC
          text occurrence at exactly TWO emission sites (one inside
          ``index.typ``'s own guard for the direct entry, dark; one inside
          ``sub.typ``'s own guard for its nested entry, live) -- a structural
          sanity check on the emitted source, not the load-bearing dedup
          proof (Phase 49: text presence and runtime inclusion are now two
          different things, since only one of the two guards is ever live);
        - the LOAD-BEARING proof: ``shared``'s own body heading text
          ("Shared Chapter") appears exactly ONCE in ``master.pdf``'s
          ``pypdf``-extracted text -- proving the compiled document, not
          merely the on-disk source, renders the diamond target once;
        - ``shared`` still defines its ``<shared-anchor>`` label exactly once and
          still carries the same-document ``link(<shared-anchor>, ...)``
          reference (the reference is preserved, not deduped away);
        - ``master.pdf`` (the wrapper's compiled output -- R4:
          ``TypstPDFBuilder.finish()`` compiles only wrapper files) exists,
          is non-empty, and starts with the ``%PDF`` magic bytes -- the
          only proof the document compiled to valid Typst and the
          duplicate-label fatal is gone.
        """
        result = _run_sphinx_build_typstpdf(
            duplicate_include_label_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # A fatal inside TypstPDFBuilder.finish() is logged (not raised) as an
        # ERROR, so guard against the exact signatures explicitly rather than
        # trusting returncode alone.
        assert "occurs multiple times" not in result.stderr, (
            "typst.compile() reported a duplicated label -- the "
            f"compile-time guard is not in effect:\nstderr: {result.stderr}"
        )
        assert "does not exist in the document" not in result.stderr, (
            "typst.compile() reported a dangling label -- the surviving "
            "guard orphaned a reference (it must keep the live "
            f"occurrence's definition):\nstderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        # STRUCTURAL sanity check on the emitted SOURCE: two static guard
        # sites carry the literal include("shared.typ") text -- index.typ's
        # own (dark) guard for its direct entry, and sub.typ's own (live)
        # guard for its nested entry. This is NOT the dedup proof (text
        # presence and runtime inclusion are two different things post-
        # Phase-49) -- see the pypdf-extracted marker-count assertion below
        # for that.
        include_count = 0
        for typ_path in temp_build_dir.rglob("*.typ"):
            include_count += typ_path.read_text(encoding="utf-8").count(
                'include("shared.typ")'
            )
        assert include_count == 2, (
            "expected exactly TWO static guard sites carrying "
            'include("shared.typ") text (one dark, in index.typ\'s own '
            "direct entry; one live, in sub.typ's own nested entry), but "
            f"found {include_count} -- either a guard site is missing or "
            "an extra unconditional include() survived"
        )

        # LOAD-BEARING proof: shared's own body PROSE (not its heading --
        # the heading text also legitimately appears a second time, as the
        # outline's own TOC entry, and a third time as the same-document
        # :ref:'s own link text, so the heading is not a safe marker here)
        # renders exactly ONCE in the COMPILED document, proving the
        # diamond is resolved by the published per-master state, not
        # merely that the source text happens to contain the right
        # substring count. The marker substring is read literally from
        # shared.rst's own body, never derived from any build output --
        # deliberately apostrophe-free, since docutils' own smart-quotes
        # transform rewrites a straight "'" into a typographic "'" by the
        # time this text reaches the compiled PDF.
        body_marker = "toctree paths in the master"
        assert body_marker in (
            duplicate_include_label_render_gate_dir / "shared.rst"
        ).read_text(encoding="utf-8"), (
            "the body marker substring must be read literally from "
            "shared.rst's own source -- fixture content drifted"
        )
        pdf_path = temp_build_dir / "master.pdf"
        assert pdf_path.exists(), "master.pdf was not produced"
        reader = pypdf.PdfReader(str(pdf_path))
        pdf_text = "\n".join(page.extract_text() for page in reader.pages)
        marker_count = pdf_text.count(body_marker)
        assert marker_count == 1, (
            f"expected shared's own body prose ({body_marker!r}) to "
            f"appear exactly once in the compiled master.pdf, got "
            f"{marker_count} -- the diamond was not deduplicated in the "
            f"COMPILED document:\n{pdf_text}"
        )

        shared_typ = temp_build_dir / "shared.typ"
        assert shared_typ.exists(), "shared.typ was not emitted"
        shared_text = shared_typ.read_text(encoding="utf-8")

        # The propagated explicit target must be defined exactly once as an
        # anchor, and the same-document :ref: must still be emitted as a
        # link(<...>) reference that resolves to it. Labels are namespaced per
        # source document (bug #21): shared.rst's docname is `shared`, so the
        # anchor/ref token is <shared:shared-anchor>.
        assert shared_text.count("[#metadata(none) <shared:shared-anchor>]") == 1, (
            "Expected exactly one <shared:shared-anchor> anchor DEFINITION in "
            f"shared.typ:\n{shared_text}"
        )
        assert "link(<shared:shared-anchor>" in shared_text, (
            "Expected the same-document :ref: to survive as a "
            f"link(<shared:shared-anchor>, ...) reference in shared.typ:\n{shared_text}"
        )

        # The wrapper (target "master.typ", per this fixture's conf.py --
        # R4: only wrapper files are ever compiled) must have compiled to a
        # real, non-empty PDF.
        pdf_output = temp_build_dir / "master.pdf"
        assert pdf_output.exists(), (
            "master.pdf was not produced -- typst.compile() aborted, most "
            f"likely on the duplicated label:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
