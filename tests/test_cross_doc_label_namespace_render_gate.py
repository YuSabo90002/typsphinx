"""
Fast offline regression gate for cross-document label namespacing (bug #21).

GATE-02 corpus fatal (21st):

    TypstError: label `<info-field-lists>` occurs multiple times in the document

Root cause: the multi-document corpus is flattened into ONE Typst master via
``#include()``. docutils/Sphinx ids are unique only WITHIN a document, so two
different documents can carry the SAME section slug (e.g. ``info-field-lists``).
Emitted bare as ``<info-field-lists>`` by both, that is a duplicate Typst label;
as soon as anything references it the compile aborts at the semantic pass with
``label ... occurs multiple times``. (Verified independently: a duplicated label
compiles fine until a ``link(<label>)`` / ``@label`` references it.)

Fix: namespace EVERY emitted label by its source docname
(``_sanitize_label(f"{docname}:{id}")``) at every DEFINITION site, and namespace
EVERY reference to MATCH -- same-document references with the current docname,
cross-document references with the TARGET docname parsed from the resolved
refuri. Distinct namespaces => no collision; matched namespaces => links still
land on the RIGHT anchor (a cross-document reference is also upgraded from a
dead ``link("...pdf#anchor", ...)`` string url into a real ``link(<b:anchor>)``
label link).

This gate proves CORRECTNESS, not merely compilation:

1. COLLISION: ``pagea`` and ``pageb`` both slug a section to ``shared-topic``;
   the two anchors are namespaced distinctly (``<pagea:shared-topic>`` vs
   ``<pageb:shared-topic>``) and no bare ``<shared-topic>`` survives.
2. CROSS-DOC LINK CORRECTNESS: ``pagea``'s ``:ref:`` to ``pageb``'s labelled
   section emits the EXACT namespaced label ``pageb`` defines as its anchor --
   grep both files and assert the reference label == the target doc's anchor
   label. NEGATIVE GUARD: ``pagea`` also has a same-slug LOCAL anchor
   (``<pagea:shared-topic>``), and the cross-doc ref must point at ``pageb``'s,
   never ``pagea``'s.
3. SAME-DOC REF: a ``:ref:`` within ``pagea`` still resolves (refid path
   regression guard).

Drives the full ``-b typstpdf`` path -- NOT ``-b typst`` -- on purpose: the
label-uniqueness fatal only fires inside ``TypstPDFBuilder.finish()``'s
``typst.compile()`` call, so a ``-b typst`` build would emit the collision but
never compile it and thus prove nothing.
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
def cross_doc_label_namespace_render_gate_dir():
    """Return the path to the cross_doc_label_namespace_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "cross_doc_label_namespace_render_gate"


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


def _strip_raw_literals(typ_text: str) -> str:
    """Drop ``raw("...")`` inline-literal segments before scanning for labels.

    The fixtures deliberately quote label/reference forms (e.g.
    ``link(<shared-topic>)``) as prose inline literals, which render as
    ``raw("...")`` string literals in the ``.typ``. Those are literal text, NOT
    real Typst label expressions, so they must be excluded from any
    ``<label>`` / ``link(<...>)`` scan or they masquerade as bare/dangling
    labels.
    """
    return re.sub(r'raw\("(?:[^"\\]|\\.)*"\)', "", typ_text)


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the cross-doc label-namespace render gate",
)
class TestCrossDocLabelNamespaceRenderGate:
    """
    Real-compile regression gate proving cross-document label collisions are
    resolved by per-document namespacing, AND that cross-document references
    still land on the correct target anchor after namespacing.

    Requirements: GATE-02 (Phase 15 -- the fast offline reproduction of the
    systemic cross-document label-collision corpus fatal, bug #21).
    """

    def test_typstpdf_cross_doc_labels_namespaced_and_refs_resolve(
        self, cross_doc_label_namespace_render_gate_dir, temp_build_dir
    ):
        """
        Build the two-document, same-slug fixture through ``-b typstpdf`` and
        confirm the collision is gone and every reference lands correctly.
        """
        result = _run_sphinx_build_typstpdf(
            cross_doc_label_namespace_render_gate_dir, temp_build_dir
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
            "typst.compile() reported a duplicated label -- the per-document "
            f"label-namespacing fix is not in effect:\nstderr: {result.stderr}"
        )
        assert "does not exist in the document" not in result.stderr, (
            "typst.compile() reported a dangling label -- a namespaced reference "
            f"did not match its target's namespaced anchor:\nstderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        pagea = temp_build_dir / "pagea.typ"
        pageb = temp_build_dir / "pageb.typ"
        assert pagea.exists() and pageb.exists(), "pagea.typ/pageb.typ not emitted"
        pagea_text = _strip_raw_literals(pagea.read_text(encoding="utf-8"))
        pageb_text = _strip_raw_literals(pageb.read_text(encoding="utf-8"))

        # (1) COLLISION: the shared slug is namespaced distinctly per document,
        # and NO bare <shared-topic> label survives in either file.
        assert "<pagea:shared-topic>" in pagea_text, (
            "Page A's 'Shared Topic' section anchor was not namespaced with its "
            f"docname (expected <pagea:shared-topic>):\n{pagea_text}"
        )
        assert "<pageb:shared-topic>" in pageb_text, (
            "Page B's 'Shared Topic' section anchor was not namespaced with its "
            f"docname (expected <pageb:shared-topic>):\n{pageb_text}"
        )
        # A bare <shared-topic> is exactly the duplicated label that collides.
        # (raw("...") prose literals were stripped above, so this only matches a
        # genuine emitted label token.)
        assert not re.search(r"<shared-topic>", pagea_text + pageb_text), (
            "A bare, un-namespaced <shared-topic> label token survived -- this is "
            "the duplicated label that aborts the flattened master compile."
        )

        # (2) CROSS-DOC LINK CORRECTNESS (the critical one). Page A's cross-doc
        # :ref: must emit the EXACT label Page B defines as its anchor. Extract
        # every namespaced link target from Page A and every namespaced anchor
        # from Page B, and assert the cross-doc reference resolves across files.
        pagea_link_labels = set(re.findall(r"link\(<([^>\n]+)>", pagea_text))
        pageb_anchor_labels = set(re.findall(r"<([A-Za-z0-9_.:-]+)>", pageb_text))
        assert "pageb:shared-topic" in pagea_link_labels, (
            "Page A's cross-document reference did not emit a real label link to "
            "Page B's namespaced anchor (expected link(<pageb:shared-topic>)); "
            f"emitted link labels: {sorted(pagea_link_labels)}"
        )
        # The referenced label MUST actually be defined as an anchor in Page B --
        # this is the proof the link lands on the RIGHT target across files, not
        # merely that it compiles.
        assert "pageb:shared-topic" in pageb_anchor_labels, (
            "Page B does not define <pageb:shared-topic> as an anchor, so Page A's "
            f"cross-doc link would dangle:\n{pageb_text}"
        )
        # NEGATIVE GUARD: Page A has its OWN same-slug local anchor, but the
        # cross-doc reference must NOT be captured by it.
        assert "<pagea:shared-topic>" in pagea_text, (
            "Precondition for the negative guard missing: Page A should define a "
            "same-slug local <pagea:shared-topic> anchor."
        )
        assert "pagea:shared-topic" not in pagea_link_labels, (
            "The cross-document reference was mis-linked to Page A's OWN same-slug "
            "anchor <pagea:shared-topic> instead of Page B's -- a silent mis-link. "
            f"Page A link labels: {sorted(pagea_link_labels)}"
        )

        # (3) SAME-DOC REF: the refid path still resolves within Page A -- the
        # link is namespaced with Page A's docname and matches its own anchor.
        assert "pagea:local-a" in pagea_link_labels, (
            "Page A's same-document :ref: did not emit link(<pagea:local-a>):\n"
            f"{pagea_text}"
        )
        assert "[#metadata(none) <pagea:local-a>]" in pagea_text, (
            "Page A's same-document target anchor <pagea:local-a> is missing, so "
            f"its same-doc reference would dangle:\n{pagea_text}"
        )

        # (4) The emitted master must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most likely "
            f"on the duplicated <shared-topic> label:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            assert f.read(4) == b"%PDF", "Generated file is not a valid PDF"
