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

Fix: a builder-scoped ledger (``TypstBuilder._included_docnames``, shared across
every document composing one master) records each absolute docname the first time
it is emitted as an ``include()``; a repeat toctree entry for an
already-included docname is skipped. Each document is therefore ``#include``d at
most once, every label it defines is emitted exactly once, and every reference
(which is NEVER dropped) still resolves to the single surviving anchor.

This fixture is a minimal diamond: the master ``index`` reaches ``shared`` both
directly and nested under ``sub``; ``shared`` defines a section label (via a
propagated ``.. _shared-anchor:`` explicit target) and a same-document
``:ref:`` back to it (emitted as ``link(<shared-anchor>, ...)``).

Confirmed both directions: FAILS against the pre-fix translator/builder with the
exact ``label ... occurs multiple times`` fatal (``shared.typ`` ``#include``d
twice), and PASSES with the fix (``#include``d once, compiles to ``%PDF``, the
same-document reference still resolves).

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
    not TYPST_AVAILABLE,
    reason="typst-py is required for the duplicate-include-label render gate",
)
class TestDuplicateIncludeLabelRenderGate:
    """
    Real-compile regression gate proving a document reachable via more than one
    toctree path is ``#include``d exactly once, so the labels it defines are not
    duplicated in the compiled master and every reference still resolves.

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
          dangling ``label ... does not exist`` (the dedup must not orphan the
          same-document reference), nor any other compilation failure;
        - ``shared.typ`` -- reachable from the master both directly and nested
          under ``sub`` -- is emitted as an ``include("shared.typ")`` exactly
          ONCE across the whole emitted include graph (the dedup proof);
        - ``shared`` still defines its ``<shared-anchor>`` label exactly once and
          still carries the same-document ``link(<shared-anchor>, ...)``
          reference (the reference is preserved, not deduped away);
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF`` magic
          bytes -- the only proof the document compiled to valid Typst and the
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
            "typst.compile() reported a duplicated label -- the include-dedup "
            f"fix is not in effect:\nstderr: {result.stderr}"
        )
        assert "does not exist in the document" not in result.stderr, (
            "typst.compile() reported a dangling label -- the dedup orphaned a "
            f"reference (it must keep the first definition):\n"
            f"stderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        # The diamond-target document must be #included exactly ONCE across the
        # entire emitted include graph. Pre-fix it is emitted twice (once by the
        # master directly, once nested under sub); the dedup keeps the first.
        include_count = 0
        for typ_path in temp_build_dir.rglob("*.typ"):
            include_count += typ_path.read_text(encoding="utf-8").count(
                'include("shared.typ")'
            )
        assert include_count == 1, (
            "shared.typ must be #included exactly once after include-dedup, "
            f"but found {include_count} include() directives for it -- the "
            "diamond was not deduplicated."
        )

        shared_typ = temp_build_dir / "shared.typ"
        assert shared_typ.exists(), "shared.typ was not emitted"
        shared_text = shared_typ.read_text(encoding="utf-8")

        # The propagated explicit target must be defined exactly once as an
        # anchor, and the same-document :ref: must still be emitted as a
        # link(<...>) reference that resolves to it.
        assert shared_text.count("[#metadata(none) <shared-anchor>]") == 1, (
            "Expected exactly one <shared-anchor> anchor DEFINITION in "
            f"shared.typ:\n{shared_text}"
        )
        assert "link(<shared-anchor>" in shared_text, (
            "Expected the same-document :ref: to survive as a "
            f"link(<shared-anchor>, ...) reference in shared.typ:\n{shared_text}"
        )

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most likely "
            f"on the duplicated label:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
