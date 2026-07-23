"""
Fast offline regression gate for cross-references to non-included documents
(bug #25).

GATE-02 corpus fatal (25th):

    TypstError: label `<usage_u2f_extensions_u2f_example_google:example-google>`
    does not exist in the document

Root cause: the multi-document corpus is flattened into ONE Typst master via
``#include()``. An ``:orphan:`` document (Sphinx's ``doc/usage/extensions/
example_google.rst``) is excluded from EVERY toctree, so its ``.typ`` is written
but never ``#include()``d into the compiled master -- its anchors do not exist
in the compiled document. An INCLUDED document (``napoleon.rst``) nevertheless
carries a ``:ref:`` to a labelled section in that orphan; after per-document
label namespacing (bug #21) that reference emits a REAL
``link(<orphan:anchor>)`` label link, which now dangles, and ``typst.compile()``
hard-fails at the semantic pass with ``label ... does not exist``. (Sphinx's own
LaTeX builder degrades the same construct to an "undefined reference" WARNING
with the ref text shown -- never a hard error.)

Fix: compute the master's transitive toctree closure up-front
(``builder.master_included_docnames``, from ``env.toctree_includes`` over each
``typst_documents`` master) and expose it to the translator. In
``visit_reference``'s resolved-cross-document branch, DEGRADE to plain text --
emit no ``link(<...>)`` label link, render the reference's text, and
``logger.warning`` Sphinx-style -- when the target docname lies OUTSIDE that
set. A cross-reference to an INCLUDED document is unaffected and still emits a
working label link.

This gate proves CORRECTNESS, not merely compilation:

1. NON-INCLUDED TARGET DEGRADES: ``included`` :ref:s a section in the ``:orphan:``
   ``orphan`` document; the emitted ``.typ`` carries NO ``link(<orphan:...>)``
   label link, yet the reference's text (``Orphan Target Section``) is still
   present as plain inline content.
2. INCLUDED TARGET STILL LINKS: ``included`` also :ref:s a section in ITSELF;
   that reference MUST still emit the exact working
   ``link(<included:included-target>)`` label link the target defines as its
   anchor (regression guard -- only the non-included target degrades).
3. NO FATAL: the whole project compiles to a real ``%PDF`` through
   ``-b typstpdf`` with no ``does not exist`` label error.

Drives the full ``-b typstpdf`` path -- NOT ``-b typst`` -- on purpose: the
dangling-label fatal only fires inside ``TypstPDFBuilder.finish()``'s
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
def xref_orphan_degrade_render_gate_dir():
    """Return the path to the xref_orphan_degrade_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "xref_orphan_degrade_render_gate"


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

    Prose that quotes label/reference forms as reStructuredText inline literals
    renders as ``raw("...")`` string literals in the ``.typ``. Those are literal
    text, NOT real Typst label expressions, so they must be excluded from any
    ``<label>`` / ``link(<...>)`` scan or they masquerade as real labels/links.
    """
    return re.sub(r'raw\("(?:[^"\\]|\\.)*"\)', "", typ_text)


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the orphan cross-reference degrade gate",
)
class TestXrefOrphanDegradeRenderGate:
    """
    Real-compile regression gate proving a cross-reference to a NON-INCLUDED
    (``:orphan:``) document degrades to plain text instead of emitting a
    dangling label link, while a cross-reference to an INCLUDED document still
    emits a working label link.

    Requirements: GATE-02 (Phase 15 -- the fast offline reproduction of the
    orphan / non-included cross-reference corpus fatal, bug #25).
    """

    def test_typstpdf_orphan_xref_degrades_included_xref_links(
        self, xref_orphan_degrade_render_gate_dir, temp_build_dir
    ):
        """
        Build the orphan-plus-included fixture through ``-b typstpdf`` and
        confirm the non-included cross-reference degrades to text while the
        included cross-reference still links -- and the project compiles to
        ``%PDF`` with no dangling-label fatal.
        """
        result = _run_sphinx_build_typstpdf(
            xref_orphan_degrade_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # No dangling-label fatal anywhere in the build output.
        combined = result.stdout + result.stderr
        assert "does not exist" not in combined, (
            "Typst reported a dangling label -- the orphan cross-reference was "
            f"not degraded:\n{combined}"
        )
        assert (
            "TypstCompilationError" not in combined
        ), f"typst.compile() failed:\n{combined}"

        # The master compiled to a real PDF.
        pdf_path = temp_build_dir / "index.pdf"
        assert pdf_path.exists(), (
            f"index.pdf was not produced:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert pdf_path.read_bytes().startswith(
            b"%PDF"
        ), "index.pdf does not start with the %PDF magic marker"

        # Inspect the emitted body of the INCLUDED document.
        included_typ = (temp_build_dir / "included.typ").read_text(encoding="utf-8")
        scannable = _strip_raw_literals(included_typ)

        # 1. NON-INCLUDED TARGET DEGRADES: no label link to the orphan doc, but
        #    the reference text is still rendered as plain inline content.
        assert "link(<orphan:" not in scannable, (
            "A link(<orphan:...>) label link to the NON-INCLUDED orphan document "
            "was emitted; the cross-reference must degrade to plain text:\n"
            f"{included_typ}"
        )
        assert 'text("Orphan Target Section")' in scannable, (
            "The degraded orphan cross-reference did not render its text as "
            f"plain inline content:\n{included_typ}"
        )

        # 2. INCLUDED TARGET STILL LINKS: the same-project cross-reference must
        #    still emit the exact working label link to the target's anchor.
        assert "link(<included:included-target>," in scannable, (
            "The cross-reference to the INCLUDED document lost its working "
            f"link(<included:included-target>) label link (regression):\n"
            f"{included_typ}"
        )

        # The included document's anchor for that target must actually exist.
        assert "<included:included-target>]" in included_typ, (
            "The included target anchor <included:included-target> is missing "
            f"from the emitted body:\n{included_typ}"
        )
