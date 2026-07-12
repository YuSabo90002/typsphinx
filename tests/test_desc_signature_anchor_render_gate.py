"""
Fast, offline regression gate for the desc-signature anchor fix
(Phase 15, GATE-02).

Deterministic, network-free reproduction of the seventeenth fatal the slow
full-corpus gate (``tests/test_corpus_gate.py::TestCorpusRenderGate``) surfaced
against Sphinx's own ``doc/`` tree (``usage/domains/c.typ``) -- the FIRST
*semantic* (non-parse) fatal. After bugs #1-#16 unblocked the parse path,
``typst.compile()`` reached the label-resolution pass and aborted with::

    TypstError: label `<c._u40_alias.data>` does not exist in the document

Root cause: an API-declaration signature (``desc_signature``) carries docutils
ids, and ``depart_reference``'s ``refid`` branch emits a same-document
``link(<_sanitize_label(id)>, ...)`` for a cross-reference to it -- but
``depart_desc_signature`` wrapped the signature in ``strong({...})`` and never
read ``node["ids"]`` to emit a matching ``<id>`` anchor. Every ``:c:func:`` /
``:py:func:`` style refid link to a declaration therefore dangled. Unlike
``visit_target`` / ``visit_title`` / ``depart_term`` (which DO emit anchors from
their ids), ``desc_signature`` -- the node type carrying API-declaration ids --
emitted none.

Fix: ``depart_desc_signature`` now emits the proven target-anchor form
``[#metadata(none) <id>]`` for every id on the signature, each routed through
``_sanitize_label`` so the anchor name byte-matches the reference side (both
sides use the same helper). A signature with multiple ids (the ``.. c:alias::``
construct assigns one per listed entity) gets an anchor for each; a signature
with no ids emits nothing.

Confirmed both directions: FAILS against the pre-fix translator with the exact
``label ... does not exist`` fatal (the link has no anchor to resolve to), and
PASSES with the fix. Also asserts, source-level, that every same-document
``link(<name>, ...)`` has a matching ``[#metadata(none) <name>]`` anchor -- i.e.
anchor-name == reference-name for the same id.

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
def desc_signature_anchor_render_gate_dir():
    """Return the path to the desc_signature_anchor_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "desc_signature_anchor_render_gate"


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
    reason="typst-py is required for the desc-signature anchor render gate",
)
class TestDescSignatureAnchorRenderGate:
    """
    Real-compile regression gate proving a same-document cross-reference to an
    API declaration resolves, because ``desc_signature`` now emits a Typst
    ``<label>`` anchor for its ids.

    Requirements: GATE-02 (Phase 15 scope expansion -- the fast offline
    reproduction of the desc-signature dangling-label corpus fatal).
    """

    def test_typstpdf_signature_anchor_resolves_reference(
        self, desc_signature_anchor_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly (no fatal raised out of the subprocess);
        - ``typst.compile()`` did NOT abort with the semantic
          ``label ... does not exist`` fatal (nor any compilation failure);
        - the clean-id signature emits a ``[#metadata(none) <c.foo>]`` anchor;
        - EVERY same-document ``link(<name>, ...)`` reference has a matching
          ``[#metadata(none) <name>]`` anchor -- anchor-name == reference-name
          for the same id (the ``@alias`` ids exercise ``_sanitize_label`` on
          both sides: ``c._u40_alias.data`` / ``c._u40_alias.f``);
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF`` magic
          bytes -- the only proof the document compiled to valid Typst and the
          dangling-label fatal is gone.
        """
        result = _run_sphinx_build_typstpdf(
            desc_signature_anchor_render_gate_dir, temp_build_dir
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
            "typst.compile() reported a dangling label -- the desc-signature "
            f"anchor fix is not in effect:\nstderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # The clean-id signature must now carry an anchor for its id.
        assert "[#metadata(none) <c.foo>]" in typ_text, (
            "The c:function signature did not emit a <c.foo> anchor -- the "
            f"fix is not applied:\n{typ_text}"
        )

        # anchor-name == reference-name: EVERY same-document link(<name>, ...)
        # (bare-label refid form, distinct from the quoted external link("url"))
        # must have a matching [#metadata(none) <name>] anchor. An unmatched
        # link name is exactly the dangling label that aborts the compile.
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
        # The exact corpus id must be among the resolved pairs.
        assert "c._u40_alias.data" in link_names, (
            "Expected the @alias reference c._u40_alias.data to be emitted "
            f"(the exact corpus fatal id):\n{typ_text}"
        )
        assert "c._u40_alias.data" in anchor_names, (
            "Expected a matching anchor for c._u40_alias.data (@ sanitized to "
            f"_u40_ on the anchor side, byte-matching the reference):\n{typ_text}"
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
