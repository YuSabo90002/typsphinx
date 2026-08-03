"""
Real-compile regression gate for the ``desc_sig_space`` intra-signature
spacing fix (Phase 20 Plan 01, GATE-01).

The shipping bug: ``visit_desc_sig_space`` hand-wrote a literal space
character directly to ``self.body`` and then ``raise nodes.SkipNode``,
discarding the node's own ``Text(" ")`` child before it could reach
``visit_Text``. That literal space is Typst code-mode SOURCE whitespace,
which Typst's code-mode auto-join swallows with zero rendered effect (the
token-level instance of Phase 19's proven "code-mode whitespace is
cosmetic-only" invariant) -- while the four sibling ``desc_sig_*`` handlers
(``desc_sig_keyword``, ``desc_sig_name``, ``desc_sig_punctuation``,
``desc_sig_operator``) are already ``pass``/``pass``, letting their own
``Text`` children stream through ``visit_Text`` and emit a real
``text(" ")`` content VALUE that renders.

Fix: reduce ``visit_desc_sig_space``/``depart_desc_sig_space`` to
``pass``/``pass`` to match its siblings -- deleting the ``self.body.append(" ")``
+ ``SkipNode`` short-circuit, nothing added.

This covers two requirements sharing one root cause and one fixture:

- FID-07: the ``class ``/``exception `` annotation-keyword prefix on a
  ``py:class``/``py:exception`` signature keeps its trailing space.
- FID-08: every audited C/C++ ``desc_signature`` and inline ``cpp:expr``
  inter-token space (return-type-to-pointer, pointer-to-name,
  parameter-type-to-parameter-name, and operator spacing in an inline
  ``desc_inline`` paragraph context) survives.

Confirmed both directions this session: FAILS against the pre-fix
translator (extracted PDF text merges tokens with zero space --
``classsphinx.builders...``, ``PyObject*PyType_GenericAlloc``,
``Py_ssize_tnitems``, ``a*f(a)``) and PASSES with the fix applied
(``self.body.append(" ")`` + ``SkipNode`` reverted to a real, temporary,
tracked-file edit, real-built, then restored -- confirmed clean via
``git diff``).
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
def desc_sig_space_render_gate_dir():
    """Return the path to the desc_sig_space_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "desc_sig_space_render_gate"


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

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``)
    so the exact interpreter/venv running this test is reused, sidestepping
    the documented NixOS-sandbox PATH-shadowing hazard.
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
    reason="typst-py is required for the desc-sig-space render gate",
)
class TestDescSigSpaceRenderGate:
    """
    Real-compile regression gate proving the ``desc_sig_space`` pass/pass
    fix restores every audited intra-signature space (FID-07 + FID-08).

    Requirements: FID-07, FID-08, GATE-01.
    """

    def test_typstpdf_desc_sig_space_produces_pdf_with_structural_spaces(
        self, desc_sig_space_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm, at the
        SOURCE (``.typ``) level:

        - the build exits cleanly and did not report a compile failure;
        - the ``class `` annotation prefix emits ``text("class")``,
          ``text(" ")``, then the dotted class name -- three separate
          statements, not a merged token (FID-07);
        - the C signature emits ``text("PyObject")``, ``text(" ")``,
          ``text("*")``, ``text("PyType_GenericAlloc")`` on the
          ``strong({...})`` return-type/pointer/name run (FID-08);
        - the parameter list's ``desc_parameter`` concat form keeps its
          ``+``-joined content spaces between the parameter's type and its
          name (FID-08);
        - ``index.pdf`` exists, is non-empty, and begins with the ``%PDF``
          magic bytes.
        """
        result = _run_sphinx_build_typstpdf(
            desc_sig_space_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # Phase 37 (37-EMISSION-CONTRACT.md section 3 + section 4): every
        # desc_sig_space / desc_sig_keyword_type / bare signature Text node
        # routes through the monospace branch, so text(...) becomes
        # raw(...) at each of these sites. The test's SUBJECT is the SPACE
        # surviving as its own separate statement -- migrated straight to
        # its raw(...) shape so the assertion still fails if the space
        # disappears, not just if the wrapper name changes.

        # FID-07: the 'class ' annotation prefix keeps its trailing space as
        # a real raw(" ") statement, not a merged 'raw("classsphinx...")'.
        assert 'raw("class")\nraw(" ")\nraw("sphinx' in typ_text, (
            "Expected the 'class ' annotation-prefix space as a separate "
            'raw(" ") statement between raw("class") and the dotted '
            f"class name (FID-07 regression):\n{typ_text}"
        )

        # FID-08: the C signature's return-type-to-pointer and
        # pointer-to-name spaces, on the signature wrapper's run.
        #
        # "PyType_GenericAlloc" is desc_name wrapping a desc_sig_name (a
        # non-leaf desc_name, the C++/measured case) -- SS5.1's "otherwise"
        # branch stays pass and the nested desc_sig_name's OWN parent is
        # desc_name, so SS5.2 rule 1 fires: strong(raw(...)), not plain
        # raw(...). "PyObject" (the return type) has no desc_annotation/
        # desc_name ancestor, so it stays flag-driven plain raw(...).
        assert (
            'raw("PyObject")\nraw(" ")\nraw("*")\nstrong(raw("PyType_GenericAlloc"))'
            in typ_text
        ), (
            "Expected the C signature's return-type/pointer/name run to "
            'keep every inter-token space as a separate raw(" ") '
            f"statement (FID-08 regression):\n{typ_text}"
        )

        # FID-08: the desc_parameter '+'-concat form keeps its content
        # spaces between the parameter's type and its name.
        #
        # MEASURED discrepancy from contract 37-EMISSION-CONTRACT.md section
        # 5.2's narrative ("the first desc_sig_name direct child of a
        # desc_parameter is always the parameter's own name"): this fixture
        # has NO intersphinx inventory, so "PyTypeObject" (the TYPE) never
        # resolves to a reference and is never wrapped by one -- it stays a
        # bare desc_sig_name DIRECT child of desc_parameter, making it (not
        # "type") the first such child. Rule 2 therefore fires on
        # "PyTypeObject" (emph) and "type" -- the second desc_sig_name for
        # this parameter, with self._param_name_seen already True -- falls
        # through to rule 3 (plain, flag-driven raw()). This is the mirror
        # image of the intspx-resolved "MyType *obj" case in
        # tests/test_desc_signature_concat_render_gate.py, where the type
        # DOES resolve and IS wrapped in a reference, leaving "obj" as the
        # first direct desc_sig_name child. Recorded as a discrepancy in the
        # 37-04-SUMMARY.md Deviations section -- do not "fix" this assertion
        # to italicise "type" instead; that is not what SS5.2 rule 2
        # mechanically produces for an unresolved C type.
        assert (
            'emph(raw("PyTypeObject")) + raw(" ") + raw("*") + raw("type")' in typ_text
        ), (
            "Expected the desc_parameter concat form to keep the "
            "parameter's type-to-pointer-to-name spaces as real "
            f'raw(" ") values (FID-08 regression):\n{typ_text}'
        )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced:\n" f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

    @pytest.mark.skipif(
        not PYPDF_AVAILABLE,
        reason="pypdf is required for the extracted-text adjacency assert",
    )
    def test_pdf_extracted_text_has_no_merged_tokens(
        self, desc_sig_space_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf``, extract the compiled
        PDF's text with pypdf, and confirm (D-07 required adjacency asserts):

        - ``"class sphinx"`` (a real rendered space) is present, and the
          merged pre-fix form ``"classsphinx"`` is absent (FID-07);
        - ``"Py_ssize_t nitems"`` is present, and the merged pre-fix form
          ``"Py_ssize_tnitems"`` is absent (FID-08);
        - ``"a * f(a)"`` is present (FID-08, inline ``cpp:expr`` operator
          spacing).

        This is the real, rendered-glyph-level proof: a structural ``.typ``
        assert alone cannot distinguish a real content space from cosmetic
        source whitespace, but a rendered PDF can (Phase 19/20's proven
        "code-mode whitespace is cosmetic-only" invariant -- confirmed this
        session for the token level by a real, temporary pre-fix build:
        the pre-fix translator's extracted text reads
        ``classsphinx.builders.html.StandaloneHTMLBuilder``,
        ``PyObject*PyType_GenericAlloc(PyTypeObject*type, Py_ssize_tnitems)``,
        and ``a*f(a)`` -- zero rendered space at every audited site).
        """
        result = _run_sphinx_build_typstpdf(
            desc_sig_space_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced:\n" f"stderr: {result.stderr}"
        )

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)
        # Phase 37 (37-EMISSION-CONTRACT.md section 4.2, deviation Rule 2):
        # this fixture's desc_addname contains a dotted name
        # ("sphinx.builders.html."). Once the ZWSP break opportunity exists
        # anywhere in the document, pypdf.extract_text() has been measured
        # to emit a spurious U+200B at UNRELATED glyph boundaries too, not
        # only at injection points -- every compiled-PDF text assertion in
        # this phase must normalise it away before comparing, or the test
        # will flake in a way that looks like a rendering bug. Currently a
        # no-op (no ZWSP exists pre-Phase-37); added defensively ahead of
        # 37-06 so this test does not regress once monospace propagation
        # lands.
        full_text = full_text.replace(
            "\u200b", ""
        )  # U+200B, written as an explicit escape

        # FID-07: the 'class ' annotation prefix renders with a real space.
        assert "class sphinx" in full_text, (
            "Expected 'class sphinx' (a real rendered space) in extracted "
            f"PDF text -- FID-07 regression:\n{full_text}"
        )
        assert "classsphinx" not in full_text, (
            "Found the merged 'classsphinx' form in extracted PDF text -- "
            f"the FID-07 fix is not in effect:\n{full_text}"
        )

        # FID-08: the C signature's parameter-type-to-name space renders.
        assert "Py_ssize_t nitems" in full_text, (
            "Expected 'Py_ssize_t nitems' (a real rendered space) in "
            f"extracted PDF text -- FID-08 regression:\n{full_text}"
        )
        assert "Py_ssize_tnitems" not in full_text, (
            "Found the merged 'Py_ssize_tnitems' form in extracted PDF "
            f"text -- the FID-08 fix is not in effect:\n{full_text}"
        )

        # FID-08: the inline cpp:expr operator spacing renders.
        assert "a * f(a)" in full_text, (
            "Expected 'a * f(a)' (real rendered operator spacing) in "
            f"extracted PDF text -- FID-08 regression:\n{full_text}"
        )
