"""
Fast, offline regression gate for the propagated-target paragraph anchor fix
(Phase 15, GATE-02).

Deterministic, network-free reproduction of the twentieth fatal the slow
full-corpus gate (``tests/test_corpus_gate.py::TestCorpusRenderGate``) surfaced
against Sphinx's own ``doc/`` tree (``usage/referencing.rst``) -- a
missing-anchor (dangling label) fatal on a propagated-target paragraph. After
bugs #17/#18/#19 unblocked the earlier label fatals, ``typst.compile()``
reached the label-resolution pass and aborted with::

    TypstError: label `<xref-modifiers>` does not exist in the document

Root cause: an explicit ``.. _xref-modifiers:`` target sits before a PARAGRAPH
(not a section). docutils' ``PropagateTargets`` transform moves the target's id
onto that following paragraph's ``node["ids"]``. ``visit_paragraph`` emitted
``par({...})`` but read no ``node["ids"]`` -- so no ``<label>`` anchor was
emitted -- while a same-document ``:ref:`` renders
``link(<xref-modifiers>, ...)``. The reference therefore dangled: the label was
defined zero times and referenced once. This is a general class: docutils
propagates an explicit target's id onto whatever body element follows it
(paragraph, list, table, image, admonition, line-block, block-quote,
definition-list), and any element that emits no anchor for ``node["ids"]``
dangles when referenced.

Fix: ``visit_paragraph`` -- and the audited sibling body-element visitors --
route ``node["ids"]`` through a shared ``_emit_id_anchors`` helper that emits
the proven ``[#metadata(none) <id>]`` target-anchor form (bug #2) for every id,
each routed through ``_sanitize_label`` (bug #10) so the anchor name
byte-matches the reference side. A node with no ids emits nothing (output
byte-unchanged).

Confirmed both directions: FAILS against the pre-fix translator with the exact
``label ... does not exist`` fatal (the link has no anchor to resolve to), and
PASSES with the fix. Also asserts, source-level, that the paragraph target
emits a ``[#metadata(none) <my-para-target>]`` anchor whose name equals the
``link(<my-para-target>`` reference, and that no same-document ``link(<name>)``
dangles (covers the extended bullet-list case too).

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
def paragraph_propagated_target_render_gate_dir():
    """Return the path to the propagated-target render-gate fixture project."""
    return (
        Path(__file__).parent / "fixtures" / "paragraph_propagated_target_render_gate"
    )


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
    reason="typst-py is required for the propagated-target anchor render gate",
)
class TestParagraphPropagatedTargetRenderGate:
    """
    Real-compile regression gate proving a same-document cross-reference to a
    propagated-target paragraph (and bullet list) resolves, because
    ``visit_paragraph`` (and the audited sibling body visitors) now emit a Typst
    ``<label>`` anchor for the propagated ``node["ids"]``.

    Requirements: GATE-02 (Phase 15 scope expansion -- the fast offline
    reproduction of the propagated-target paragraph dangling-label corpus fatal).
    """

    def test_typstpdf_propagated_paragraph_anchor_resolves_reference(
        self, paragraph_propagated_target_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly (no fatal raised out of the subprocess);
        - ``typst.compile()`` did NOT abort with the semantic
          ``label ... does not exist`` fatal (nor any compilation failure);
        - the propagated-target paragraph emits a
          ``[#metadata(none) <my-para-target>]`` anchor;
        - EVERY same-document ``link(<name>, ...)`` reference has a matching
          ``[#metadata(none) <name>]`` anchor -- anchor-name == reference-name
          for the same id (covers both the paragraph and the extended
          bullet-list propagated target);
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF`` magic
          bytes -- the only proof the document compiled to valid Typst and the
          dangling-label fatal is gone.
        """
        result = _run_sphinx_build_typstpdf(
            paragraph_propagated_target_render_gate_dir, temp_build_dir
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
            "typst.compile() reported a dangling label -- the propagated-target "
            f"paragraph anchor fix is not in effect:\nstderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # The propagated-target paragraph must now carry an anchor for its id.
        # Labels are namespaced per source document (bug #21), so the id is
        # emitted as <index:my-para-target> in this single-doc (docname=index)
        # fixture.
        assert "[#metadata(none) <index:my-para-target>]" in typ_text, (
            "The paragraph did not emit a <index:my-para-target> anchor -- the "
            f"propagated-target paragraph fix is not applied:\n{typ_text}"
        )
        # The bullet-list extension case must anchor too.
        assert "[#metadata(none) <index:my-list-target>]" in typ_text, (
            "The bullet list did not emit a <index:my-list-target> anchor -- the "
            f"propagated-target list extension is not applied:\n{typ_text}"
        )

        # anchor-name == reference-name: EVERY same-document link(<name>, ...)
        # (bare-label refid form, distinct from the quoted external link("url"))
        # must have a matching [#metadata(none) <name>] anchor. An unmatched
        # link name is exactly the dangling label that aborts the compile.
        #
        # The fixture's own prose deliberately contains inline-literal snippets
        # like ``link(<my-list-target>, ...)`` (rendered as raw("...") string
        # literals) to document the emitted form. Those are literal text, NOT
        # real Typst link expressions, so strip raw("...") segments before
        # scanning -- otherwise the un-namespaced snippet names would masquerade
        # as dangling references (a false positive exposed by per-doc
        # namespacing, bug #21).
        scan_text = re.sub(r'raw\("(?:[^"\\]|\\.)*"\)', "", typ_text)
        link_names = set(re.findall(r"link\(<([^>]+)>", scan_text))
        anchor_names = set(re.findall(r"\[#metadata\(none\) <([^>]+)>\]", scan_text))
        assert link_names, (
            "Expected at least one same-document link(<name>, ...) reference in "
            f"the emitted output:\n{typ_text}"
        )
        assert {"index:my-para-target", "index:my-list-target"} <= link_names, (
            "Expected both propagated-target references to be emitted as "
            f"docname-namespaced link(<index:...>) forms:\n{typ_text}"
        )
        dangling = link_names - anchor_names
        assert not dangling, (
            "Same-document references with no matching anchor (dangling labels): "
            f"{sorted(dangling)}\nanchors present: {sorted(anchor_names)}\n{typ_text}"
        )

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most likely "
            f"on a dangling label:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
