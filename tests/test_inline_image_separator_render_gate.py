"""
Real-compile regression gate for the inline-image-separator fix
(Phase 62, IMG-08, IMG-09, IMG-10, TEST-05).

An image node preceded by any sibling content in its container was emitted
adjacent to the preceding code-mode expression -- no separator at all --
so Typst refused the whole document with ``expected semicolon or line
break`` and ``TypstPDFBuilder.finish()`` raised ``ExtensionError``,
writing NO PDF for any master (including image-free masters that only
``#include()`` the poisoned content file transitively).

This module binds the FULL measured trigger matrix (62-02-PLAN.md): 16
FAIL documents (``.planning/research/FEATURES.md`` Q1 rows 1-16, each its
own master), 9 PASS documents (Q2 rows A-I, all toctree'd under one
``pass_parent`` master, the 18th master), and the image-free ``index``
root. All 18 masters are driven from ONE ``sphinx-build -b typstpdf``
invocation, shared across every test method in this module via a
module-scoped fixture -- measured cost is 1-2s per build, so a per-test
rebuild would multiply it by the method count for no additional signal.

Drives the full ``-b typstpdf`` path via a real ``typst.compile()`` --
NOT merely a structural/string check on the emitted ``.typ`` -- text-mode
reads with an explicit utf-8 encoding on both sides, never a binary read,
so a build's Windows CR-newline write-mode translation cannot spuriously
fail this gate.
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


# Module constants: the full 16 FAIL / 9 PASS / 18-master matrix
# (62-02-PLAN.md's fixture_document_map). FAIL_DOCNAMES is numeric order
# (FEATURES.md Q1 rows 1-16); PASS_DOCNAMES is a-i order (Q2 rows A-I).
FAIL_DOCNAMES = [
    "fail_01_sub_mid_sentence",
    "fail_02_two_subs_adjacent",
    "fail_03_sub_in_list_item",
    "fail_04_block_image_second_in_list_item",
    "fail_05_image_in_table_cell",
    "fail_06_image_in_definition_list_body",
    "fail_07_image_in_admonition",
    "fail_08_image_in_footnote_body",
    "fail_09_image_in_legend_mid_text",
    "fail_10_two_images_in_legend",
    "fail_11_image_after_inline_literal",
    "fail_12_image_after_emphasis",
    "fail_13_image_after_reference",
    "fail_14_image_in_field_list_body",
    "fail_15_image_in_section_title",
    "fail_16_image_with_width_mid_sentence",
]
PASS_DOCNAMES = [
    "pass_a_standalone_block_image",
    "pass_b_figure_with_caption",
    "pass_c_image_first_in_paragraph",
    "pass_d_image_with_dimensions_and_scale_align",
    "pass_e_image_with_propagated_target_id",
    "pass_f_figure_with_plain_legend",
    "pass_g_figure_in_list_item_after_paragraph",
    "pass_h_figure_first_in_list_item",
    "pass_i_bare_image_first_in_list_item",
]
# Exactly one definition of the 18-master list -- index + all 16 FAIL
# masters + pass_parent (the 9 PASS documents are toctree'd children of
# pass_parent only, never independent masters).
ALL_MASTER_DOCNAMES = ["index"] + FAIL_DOCNAMES + ["pass_parent"]


def _wrapper_pdf_path(build_dir: Path, docname: str) -> Path:
    """Return the expected wrapper PDF path for a master docname."""
    return build_dir / f"{docname}-out.pdf"


def _assert_pdf_magic(path: Path, docname: str) -> None:
    """
    Assert ``path`` is a non-empty file starting with the PDF magic bytes.

    ``docname`` is included in every assertion message so a single failing
    master out of 18 is attributable without re-running the build.
    """
    assert path.exists(), f"{docname}: {path} was not produced"
    assert path.stat().st_size > 0, f"{docname}: {path} is empty"
    with open(path, "rb") as f:
        magic = f.read(4)
        assert (
            magic == b"%PDF"
        ), f"{docname}: {path} is not a valid PDF (magic: {magic!r})"


@pytest.fixture(scope="module")
def inline_image_separator_render_gate_dir():
    """Return the path to the inline_image_separator_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "inline_image_separator_render_gate"


@pytest.fixture(scope="module")
def full_matrix_build(inline_image_separator_render_gate_dir, tmp_path_factory):
    """
    Drive ONE ``sphinx-build -b typstpdf`` over the full 18-master fixture
    and share the result across every test method in this module.

    This is the structural delta neither of this gate's two precedents has
    (``test_paragraph_concat_render_gate.py`` and
    ``test_abbr_pep_separator_render_gate.py`` each compile exactly one
    master per fixture): 18 independently configured masters compiled in
    ONE ``sphinx-build`` invocation. A module-scoped fixture (built on
    ``tmp_path_factory``, which is session-scoped and therefore safe to use
    from a module-scoped fixture) avoids rebuilding 18 masters per test.
    """
    build_dir = tmp_path_factory.mktemp("inline_image_separator_full_matrix") / "_build"
    result = _run_sphinx_build_typstpdf(
        inline_image_separator_render_gate_dir, build_dir
    )
    return result, build_dir


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the inline-image-separator render gate",
)
class TestInlineImageSeparatorFullMatrix:
    """
    Proves every one of the 18 masters in the full fixture -- including the
    image-free ``index`` root master and the ``pass_parent`` positive
    control -- writes a valid PDF post-fix (IMG-08, IMG-09, TEST-05).
    """

    def test_full_matrix_every_master_writes_a_pdf(self, full_matrix_build):
        result, build_dir = full_matrix_build
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        for docname in ALL_MASTER_DOCNAMES:
            pdf_path = _wrapper_pdf_path(build_dir, docname)
            _assert_pdf_magic(pdf_path, docname)

    def test_full_matrix_stderr_carries_no_typst_refusal(self, full_matrix_build):
        """
        Neither the leading-boundary refusal (``expected semicolon or line
        break``) nor the trailing concat-unaware refusal (``cannot apply
        unary``, which a trailing-newline-unaware fix produces on the
        field-list-body shape -- 62-RESEARCH.md's own finding) nor
        ``TypstPDFBuilder.finish()``'s aggregate ``master document(s)
        failed`` message may appear anywhere in the build's stderr.
        """
        result, _ = full_matrix_build
        assert "expected semicolon or line break" not in result.stderr, (
            "Found the unseparated-expression Typst refusal in stderr -- "
            f"the IMG-08 fix is not applied:\n{result.stderr}"
        )
        assert "cannot apply unary" not in result.stderr, (
            "Found the concat-unaware trailing-half refusal in stderr -- "
            "a trailing-newline-unaware fix produces this on the "
            f"field-list-body (fail_14) shape:\n{result.stderr}"
        )
        assert "master document(s) failed" not in result.stderr, (
            "Found TypstPDFBuilder.finish()'s aggregate failure message -- "
            f"one or more masters did not compile:\n{result.stderr}"
        )

    def test_full_matrix_pass_parent_positive_control(self, full_matrix_build):
        """
        D-03 / 62-RESEARCH.md Pitfall 2: ``TypstPDFBuilder.finish()``'s
        aggregate ``ExtensionError`` NEVER names a successful master --
        only a failed one. ``pass_parent``'s green verdict inside a build
        that also proves the 17 FAIL masters green must therefore be read
        from the filesystem (its own wrapper PDF) AND the build's stdout
        (its ``Generated PDF: ...`` log line), never from the (absent)
        exception text.
        """
        result, build_dir = full_matrix_build
        pdf_path = _wrapper_pdf_path(build_dir, "pass_parent")
        _assert_pdf_magic(pdf_path, "pass_parent")

        assert f"Generated PDF: {pdf_path}" in result.stdout, (
            "Expected pass_parent's success to be logged via stdout's "
            f"'Generated PDF: ...' line, not merely absent from any "
            f"failure text:\nstdout: {result.stdout}"
        )


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the inline-image-separator render gate",
)
class TestInlineImageSeparatorFailShapes:
    """
    Structural proof that every one of the 16 FAIL shapes' emitted content
    no longer juxtaposes a closing paren directly against ``image(`` -- the
    exact unseparated-expression shape the pre-fix defect produced -- and
    that fail_16's ``:width:`` conversion is untouched by this phase.
    """

    @pytest.mark.parametrize("docname", FAIL_DOCNAMES)
    def test_fail_shape_emits_a_separator_before_image(
        self, full_matrix_build, docname
    ):
        result, build_dir = full_matrix_build
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        content_typ = build_dir / f"{docname}.typ"
        assert content_typ.exists(), f"{docname}.typ was not emitted"
        body = content_typ.read_text(encoding="utf-8")

        assert ")image(" not in body, (
            f"{docname}: found an unseparated closing-paren-then-image( "
            f"juxtaposition -- the IMG-08 fix is not applied:\n{body}"
        )

    def test_fail_16_width_conversion_is_unchanged(self, full_matrix_build):
        """
        Pins that this phase changed nothing about dimension handling:
        fail_16's ``:width: 50px`` must still convert to ``width: 37.5pt``.
        """
        result, build_dir = full_matrix_build
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        content_typ = build_dir / "fail_16_image_with_width_mid_sentence.typ"
        assert (
            content_typ.exists()
        ), "fail_16_image_with_width_mid_sentence.typ was not emitted"
        body = content_typ.read_text(encoding="utf-8")

        assert "width: 37.5pt" in body, (
            "Expected fail_16's :width: 50px to still convert to "
            "width: 37.5pt -- this phase must not change dimension "
            f"conversion behaviour:\n{body}"
        )
