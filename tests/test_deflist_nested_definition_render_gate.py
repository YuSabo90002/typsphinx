"""
Fast, offline regression gate for the nested-definition body-clobber fix
(Phase 15, GATE-02).

Deterministic, network-free reproduction of the eighteenth fatal the slow
full-corpus gate (``tests/test_corpus_gate.py::TestCorpusRenderGate``) surfaced
against Sphinx's own ``doc/`` tree. Once bugs #1-#17 unblocked the parse path and
the first semantic (label) pass, ``typst.compile()`` still aborted with::

    TypstError: label `<sphinx.domains.Domain>` does not exist in the document

Root cause (a buffer-management bug, distinct from bug #17's anchor-emission
gap -- the anchor IS emitted): ``visit_term`` / ``visit_definition`` saved and
restored the main body through a SINGLE-SLOT ``self.saved_body`` (plus
single-slot ``current_term_buffer`` / ``current_definition_buffer`` and a
single-slot ``definition_list_items``). When a definition list is NESTED inside
a definition -- e.g. an autodoc class whose docstring's first block is itself a
definition list whose definition holds a further nested list -- the inner list
overwrote every slot. On the outer ``depart_definition`` the ``saved_body``
restore was skipped (it had been ``None``-d by the inner depart), so
``self.body`` was left pointing at the orphaned inner buffer. Because
``astext()`` joins the CURRENT ``self.body``, everything written before the
orphaning point (headings, paragraphs, and a preceding API declaration's
``desc_signature`` + its ``[#metadata(none) <id>]`` anchor) was silently
discarded, while a later same-document ``link(<id>, ...)`` reference survived --
dangling with Typst's semantic ``label ... does not exist``.

Fix: stack-ify the term/definition buffer state -- ``_saved_body_stack`` (push
in ``visit_term`` / ``visit_definition``, pop in the departs),
``_pending_term_stack`` (captures the pending term on ``visit_definition`` before
a nested list can clobber it), and ``_deflist_items_stack`` (per-list item
collection; ``definition_list_items`` aliases its top). ``depart_definition``
reads its content from ``self.body`` (restored by the balanced stack), not the
clobberable slot. Each nesting level then saves/restores its own level -- nothing
is orphaned. Mirrors the ``_list_item_stack`` (bug #4) and ``_inline_concat_stack``
(bug #5) stack idiom already in the translator.

This fixture drives BOTH failure directions in one document, and is confirmed to
FAIL against the pre-fix translator and PASS with the fix:

* content-drop: an intro-paragraph sentinel (``PREDEF_SENTINEL``) and the outer
  ``Configuration`` term (whose definition begins with a leading paragraph then a
  NESTED definition list) are dropped pre-fix and survive post-fix; and
* dangling-label: a ``.. py:class::`` declaration whose content BEGINS with a
  nested definition list, referenced AFTER itself via ``:py:class:``, aborts the
  compile pre-fix (anchor discarded, ``link`` survives) and resolves post-fix.

Drives the full ``-b typstpdf`` path -- NOT ``-b typst`` -- on purpose: the
semantic label-resolution fatal only fires inside ``TypstPDFBuilder.finish()``'s
``typst.compile()`` call, so a ``-b typst`` build would emit the dangling link
but never compile it and thus prove nothing.
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


@pytest.fixture
def deflist_nested_definition_render_gate_dir():
    """Return the path to the deflist_nested_definition_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "deflist_nested_definition_render_gate"


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
    reason="typst-py is required for the nested-definition body-clobber render gate",
)
class TestDeflistNestedDefinitionRenderGate:
    """
    Real-compile regression gate proving a definition list NESTED inside a
    definition no longer orphans the main body, so its outer content survives and
    a later declaration's anchor is not discarded.

    Requirements: GATE-02 (Phase 15 scope expansion -- the fast offline
    reproduction of the nested-definition body-clobber corpus fatal #18).
    """

    def test_typstpdf_nested_definition_survives_and_reference_resolves(
        self, deflist_nested_definition_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm both failure
        directions of the body-clobber bug are fixed:

        - the build exits cleanly and ``typst.compile()`` did NOT abort with the
          semantic ``label ... does not exist`` fatal (nor any compilation
          failure);
        - CONTENT-DROP: the intro sentinel ``PREDEF_SENTINEL`` (emitted before the
          orphaning list) survives, and the outer ``Configuration`` term is paired
          with its definition -- whose leading paragraph ``OUTERSENTINEL_CONFIG``
          and nested ``terms(...)`` are both present INSIDE that item;
        - DANGLING-LABEL: the ``.. py:class:: WidgetGamma`` declaration's
          ``[#metadata(none) <WidgetGamma>]`` anchor survives, and EVERY
          same-document ``link(<name>, ...)`` reference has a matching anchor
          (anchor-name == reference-name), so nothing dangles;
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF`` magic
          bytes -- the only proof the document compiled to valid Typst.
        """
        result = _run_sphinx_build_typstpdf(
            deflist_nested_definition_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # A fatal inside TypstPDFBuilder.finish() is logged (not raised) as an
        # ERROR, so guard against the exact signatures explicitly rather than
        # trusting returncode alone.
        assert "does not exist in the document" not in result.stderr, (
            "typst.compile() reported a dangling label -- the nested-definition "
            f"body-clobber fix is not in effect:\nstderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # CONTENT-DROP direction: the intro paragraph before the orphaning list
        # must survive (pre-fix astext() joined the orphaned buffer, discarding
        # everything before it).
        assert "PREDEF_SENTINEL" in typ_text, (
            "The intro paragraph emitted before the nested-in-definition list was "
            f"dropped -- self.body was orphaned and astext() joined it:\n{typ_text}"
        )

        # The OUTER definition's term must be paired with its content. Pre-fix the
        # outer item was never appended (current_term_buffer clobbered), so the
        # outer list emitted a bare ``terms()``. Post-fix the term is present AND
        # its leading paragraph sentinel is inside the SAME terms.item.
        assert 'terms.item(text("Configuration")' in typ_text, (
            "The outer 'Configuration' term was dropped -- the nested list "
            f"clobbered the pending term:\n{typ_text}"
        )
        assert "OUTERSENTINEL_CONFIG" in typ_text, (
            "The outer definition's leading paragraph was dropped:\n" + typ_text
        )
        # The outer definition's leading paragraph and the nested terms(...) must
        # both live inside the outer terms.item -- i.e. OUTERSENTINEL_CONFIG must
        # appear AFTER the 'Configuration' item opens (proving the nested content
        # is nested, not leaked to the top level as it was pre-fix).
        config_item = typ_text.index('terms.item(text("Configuration")')
        assert typ_text.index("OUTERSENTINEL_CONFIG") > config_item, (
            "OUTERSENTINEL_CONFIG leaked outside its 'Configuration' item "
            f"(pre-fix orphan-leak signature):\n{typ_text}"
        )

        # DANGLING-LABEL direction: the declaration's anchor must survive and
        # anchor-name == reference-name for EVERY same-document link. Labels are
        # namespaced per source document (bug #21), so the id is emitted as
        # <index:WidgetGamma> in this single-doc (docname=index) fixture.
        assert "[#metadata(none) <index:WidgetGamma>]" in typ_text, (
            "The py:class declaration's <index:WidgetGamma> anchor was dropped -- "
            f"its desc_signature was written into an orphaned buffer:\n{typ_text}"
        )
        link_names = set(re.findall(r"link\(<([^>]+)>", typ_text))
        anchor_names = set(re.findall(r"\[#metadata\(none\) <([^>]+)>\]", typ_text))
        assert link_names, (
            "Expected at least one same-document link(<name>, ...) reference in "
            f"the emitted output:\n{typ_text}"
        )
        dangling = link_names - anchor_names
        assert not dangling, (
            "Same-document references with no matching anchor (dangling labels): "
            f"{sorted(dangling)}\nanchors present: {sorted(anchor_names)}\n{typ_text}"
        )
        assert "index:WidgetGamma" in link_names, (
            "Expected the forward :py:class: reference to WidgetGamma to be "
            f"emitted as a docname-namespaced same-document link:\n{typ_text}"
        )

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most likely "
            f"on the dangling <WidgetGamma> label:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
