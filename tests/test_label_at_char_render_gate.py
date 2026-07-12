"""
Fast, offline regression gate for the label/ref @-sanitizer fix
(Phase 15, GATE-02).

Deterministic, network-free reproduction of the tenth fatal the slow
full-corpus gate (``tests/test_corpus_gate.py::TestCorpusRenderGate``) surfaced
against Sphinx's own ``doc/`` tree (``usage/domains/c.typ`` and two more files),
after bugs #1-#9 unblocked the compile path::

    error: unclosed label
       ┌─ usage/domains/c.typ:311

Root cause: the translator emitted Typst label NAMES -- in ``<...>`` anchors,
``label("...")`` strings, and ``link(<...>, ...)`` references -- DIRECTLY from
docutils/Sphinx node ids, without sanitizing them to Typst's valid label
character set. Typst 0.15 labels accept only ``[A-Za-z0-9_.:-]`` (verified
empirically); every other character makes Typst fail to close the label with
``error: unclosed label``, which aborts the ENTIRE compile. Sphinx's C-domain
**anonymous** entities (``@data`` / ``@alias``) produce ids like
``c.Data.@data.a`` -- the ``@`` is invalid in a label token.

Fix: one shared ``TypstTranslator._sanitize_label(name)`` maps every character
outside ``[A-Za-z0-9_.:-]`` to a collision-resistant codepoint token
``_u{ord:x}_`` (``@`` -> ``_u40_``), applied at EVERY site that emits a label
name -- both where a label is DEFINED (anchors, ``label("...")``) and where it
is REFERENCED (``link(<...>, ...)``, ``footnote(<...>)``). Because the SAME
function runs on both sides, a definition and its reference sanitize to the
SAME string, so cross-references keep resolving.

This fixture's ``conf.py`` injects (at ``doctree-resolved``, after docutils'
PropagateTargets transform) a ``target`` anchor and a same-document
``reference`` that both carry the ``@``-id ``myapp.@thing.a`` -- mirroring the
corpus's ``[#metadata(none) <...@...>]`` anchor + ``link(<...@...>)`` reference
pair. The test proves (a) the emitted ``.typ`` carries NO raw ``@`` inside any
``<...>`` label token, (b) the anchor's sanitized label name EQUALS the
reference's sanitized label name (the link still resolves), and (c) the whole
thing compiles to a real ``%PDF``.

Confirmed both directions: FAILS against the pre-fix translator (raw ``@`` in
both the anchor and the reference -> ``typst.compile()`` aborts with "unclosed
label"), and PASSES with the fix. Drives the full ``-b typstpdf`` path -- NOT
``-b typst`` -- on purpose: the fatal only aborts on the
``TypstPDFBuilder.finish()`` compile path, so a ``-b typst`` build would emit
the invalid ``.typ`` but never compile it and thus prove nothing.
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
def label_at_char_render_gate_dir():
    """Return the path to the label_at_char_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "label_at_char_render_gate"


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
    reason="typst-py is required for the label-@-char render gate",
)
class TestLabelAtCharRenderGate:
    """
    Real-compile regression gate proving a docutils id containing a
    Typst-label-invalid character (``@``) is sanitized identically at both its
    anchor DEFINITION and its cross-REFERENCE, so ``typst.compile()`` does not
    abort with "unclosed label" and the link still resolves.

    Requirements: GATE-02 (Phase 15 scope expansion -- the fast offline
    reproduction of the label/ref ``@`` corpus fatal).
    """

    # The anchor-definition and reference label tokens the emitted .typ must
    # carry. `@` (U+0040) sanitizes to `_u40_`, so the raw `myapp.@thing.a`
    # becomes `myapp._u40_thing.a` at BOTH sites.
    _SANITIZED = "myapp._u40_thing.a"

    def test_typstpdf_at_id_anchor_and_ref_sanitize_equal_and_compile(
        self, label_at_char_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly (no fatal raised out of the subprocess);
        - no ``<...>`` label token in the emitted ``.typ`` contains a raw
          ``@`` -- the exact "unclosed label" corpus fatal;
        - the anchor's sanitized label name (``[#metadata(none) <NAME>]``)
          EQUALS the reference's sanitized label name (``link(<NAME>, ...)``)
          -- proving def/ref were sanitized consistently, so the link still
          resolves (a mismatch would abort the compile with "label does not
          exist");
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF``
          magic bytes -- the only proof the sanitized labels compiled to valid
          Typst and ``typst.compile()`` did NOT abort.
        """
        result = _run_sphinx_build_typstpdf(
            label_at_char_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # A fatal inside TypstPDFBuilder.finish() is logged (not raised) as an
        # ERROR, so guard against the exact signatures explicitly rather than
        # trusting returncode alone.
        assert "unclosed label" not in result.stderr, (
            "typst.compile() rejected a label -- the @-sanitizer fix is not in "
            f"effect:\nstderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # (a) No `<...>` label token may contain a raw `@`. Scope the search to
        # angle-bracket label tokens (not arbitrary prose): a `@` inside a
        # raw()/text() content string is legitimate and must NOT trip this.
        at_labels = re.findall(r"<[^>\n]*@[^>\n]*>", typ_text)
        assert not at_labels, (
            "Found a raw '@' inside a Typst <label> token -- the exact "
            f"'unclosed label' corpus fatal was NOT sanitized:\n{at_labels}"
        )

        # (b) Extract the anchor-definition label name and the reference label
        # name, and assert they are EQUAL -- the critical def==ref property.
        anchor_names = re.findall(r"#metadata\(none\)\s*<([^>\n]+)>", typ_text)
        ref_names = re.findall(r"link\(<([^>\n]+)>", typ_text)
        assert anchor_names, (
            "No '[#metadata(none) <...>]' anchor was emitted -- the fixture's "
            f"injected @-id target did not render an anchor:\n{typ_text}"
        )
        assert ref_names, (
            "No 'link(<...>, ...)' reference was emitted -- the fixture's "
            f"injected @-id reference did not render a link:\n{typ_text}"
        )
        assert self._SANITIZED in anchor_names, (
            f"Anchor label name {self._SANITIZED!r} (from '@'->'_u40_') not "
            f"found among emitted anchors {anchor_names!r}"
        )
        assert self._SANITIZED in ref_names, (
            f"Reference label name {self._SANITIZED!r} (from '@'->'_u40_') not "
            f"found among emitted references {ref_names!r}"
        )
        # The def and the ref must share the identical sanitized name -- if they
        # sanitized inconsistently the link would dangle and the compile abort.
        assert set(ref_names) <= set(anchor_names), (
            "A reference label name has no matching anchor definition -- def "
            f"and ref sanitized inconsistently:\n"
            f"anchors={anchor_names!r}\nrefs={ref_names!r}"
        )

        # (c) The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most likely "
            f"on a raw '@' in a label token:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
