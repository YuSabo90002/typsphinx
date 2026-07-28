"""
Fast, offline, real-``typst.compile()`` regression gate for MATH-01 / backlog
999.1 (Phase 34, GATE-01).

Root cause: ``visit_math`` (and ``visit_math_block``) never participate in
the code-mode inline-concat-context separator protocol
(``_emit_inline_concat_separator`` / ``_mark_inline_concat_content``) or the
list-item separator protocol (``self.in_list_item`` /
``self.list_item_needs_separator``) that every other inline leaf visitor
(``visit_Text``, ``visit_literal``, ...) already implements. ``visit_math``
only calls ``_add_paragraph_separator()``, which is a no-op in these
contexts (``self.in_paragraph`` is deliberately ``False`` there), so an
adjacent expression and the ``mi(...)``/``$...$`` call land with zero
characters between them -- rejected by Typst's parser with "expected comma"
(inside a code-mode concat-context argument like a def-list term or a
collapsed field body) or "expected semicolon or line break" (inside a
``list.item({...})`` content block).

The top-level-paragraph shape (construct A below) already compiled BEFORE
this fix -- ``_add_paragraph_separator()`` alone is sufficient there -- and
is present only as a byte-identical regression guard (RESEARCH.md
Pitfall 1), not a defect reproduction.

This gate deliberately drives ``-b typstpdf`` (never ``-b typst`` alone)
because the fatal only aborts the compile inside
``TypstPDFBuilder.finish()``; a ``-b typst`` build would emit the invalid
``.typ`` but never compile it, proving nothing.
"""

import subprocess
import sys
import unicodedata
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

# PDF text-fidelity sentinels (SC#3) -- prose that must survive the compile
# and appear in the extracted PDF text, adjacent to the math it surrounds.
PROSE_BEFORE_SENTINEL = "Text before math"
PROSE_AFTER_SENTINEL = "text after"
BLOCK_PROSE_SENTINEL = "Text before block math."

# Typst source tokens that must never leak into extracted PDF text -- their
# presence would mean the emitted .typ was never typeset (raw source dumped
# as literal text instead).
LEAK_SIGNATURES = ("mi(", "mitex(", "text(", "par({", "list(")


@pytest.fixture
def inline_math_after_text_render_gate_dir():
    """Return the path to the inline_math_after_text_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "inline_math_after_text_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path, extra_args: tuple = ()
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typstpdf`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never bare ``sphinx-build`` /
    ``uv run sphinx-build``) so the exact interpreter/venv already running
    this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard (project memory: "NixOS sandbox test env").

    ``extra_args`` is an optional tuple of additional sphinx-build CLI
    arguments (e.g. ``("-D", "typst_use_mitex=0")``) spliced into the
    command list before the source dir -- default ``()`` keeps the mitex
    (default) path unchanged.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typstpdf",
            *extra_args,
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the inline-math-after-text render gate",
)
class TestInlineMathAfterTextRenderGate:
    """
    Real-compile regression gate proving inline math immediately following
    text -- in a bullet list item, a collapsed confval field body, and a
    definition-list term -- compiles through ``typst.compile()`` on both the
    mitex default path and the native ``$...$`` path, without dropping the
    already-working top-level-paragraph shape.

    Requirements: MATH-01 (Phase 34 scope -- backlog 999.1).
    """

    def test_typstpdf_separates_inline_math_mitex_path(
        self, inline_math_after_text_render_gate_dir, temp_build_dir
    ):
        """Build the fixture with the mitex default and confirm every
        construct compiles, separates correctly, and round-trips through the
        PDF text extraction."""
        result = _run_sphinx_build_typstpdf(
            inline_math_after_text_render_gate_dir, temp_build_dir
        )

        # 1. The build must exit cleanly.
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        # 2. A fatal inside TypstPDFBuilder.finish() is logged (not raised)
        # as an ERROR, so guard against the exact signatures explicitly.
        for signature in (
            "expected semicolon or line break",
            "expected comma",
            "Typst compilation failed",
        ):
            assert signature not in result.stderr, (
                f"typst.compile() rejected the emitted .typ with the fatal "
                f"'{signature}' -- the separator fix is not in effect:\n"
                f"stderr: {result.stderr}"
            )

        # 3. index.typ must exist.
        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # 4. Construct B exact-string positive (bullet list item -- the
        # precision gate: exactly one newline separator, not zero, not two).
        assert (
            'text("Text before math ")\nmi(`E = m c^2`)\ntext(" text after.")'
            in typ_text
        ), (
            "Construct B (bullet list item) did not emit exactly one "
            f"newline separator around the inline math call:\n{typ_text}"
        )

        # 5. Construct C exact-string positive (collapsed confval field
        # body -- exactly one ' + ' between the prose sibling and math).
        assert 'text("The value of ") + mi(`x`)' in typ_text, (
            "Construct C (collapsed :default: field body) did not '+' "
            f"concatenate the prose sibling and the inline math call:\n"
            f"{typ_text}"
        )

        # 6. Construct D exact-string positive (definition-list term).
        assert 'text("Term ") + mi(`E = m c^2`)' in typ_text, (
            "Construct D (definition-list term) did not '+' concatenate "
            f"the term prose and the inline math call:\n{typ_text}"
        )

        # 7. Construct E exact-string positive (visit_math_block, D-01).
        assert 'text("Text before block math.")\nmitex(`E = m c^2`)' in typ_text, (
            "Construct E (display math in a list item) did not newline-"
            f"separate from the preceding paragraph:\n{typ_text}"
        )

        # 8. Construct A byte-identical control (RESEARCH.md Pitfall 1 --
        # the fix must NOT double-separate the already-working path).
        assert (
            'par({text("With space before math: ")\nmi(`E = m c^2`)\ntext(" after.")})'
            in typ_text
        ), (
            "Construct A (top-level paragraph, spaced form) regressed -- "
            f"the plain-paragraph shape must stay byte-identical:\n{typ_text}"
        )
        assert (
            'par({text("No space where")\nmi(`E = m c^2`)\ntext("immediately follows.")})'
            in typ_text
        ), (
            "Construct A (top-level paragraph, backslash-escaped no-space "
            f"form) regressed -- must stay byte-identical:\n{typ_text}"
        )

        # 9. Juxtaposition guards -- no bare abutment of a preceding
        # expression directly against the math call.
        assert ")mi(" not in typ_text, (
            f"A preceding expression is juxtaposed directly against mi( "
            f"with no separator:\n{typ_text}"
        )
        assert ")mitex(" not in typ_text, (
            f"A preceding expression is juxtaposed directly against "
            f"mitex( with no separator:\n{typ_text}"
        )

        # 10. Stray-leading-operator guards (the boundary edge: math as the
        # first expression in a concat context must not emit a leading
        # operator, e.g. the confval :type: field body's sole math).
        assert (
            "{ + " not in typ_text
        ), f"A concat context emitted a stray leading '+' operator:\n{typ_text}"
        assert (
            "( + " not in typ_text
        ), f"A concat context emitted a stray leading '+' operator:\n{typ_text}"

        # 11. index.pdf must exist and be a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted:\n"
            f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            assert f.read(4) == b"%PDF", "Generated file is not a valid PDF"

        # 12. SC#3 text fidelity via pypdf. NFKC-normalize before comparing
        # the math sentinel: mitex renders math letters as Mathematical
        # Alphanumeric Symbols (U+1D400 block), which are NOT code-point-
        # equal to the authored ASCII source. Prose sentinels are compared
        # as plain code points (they are never re-encoded by mitex).
        import pypdf

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)
        for sentinel in (
            PROSE_BEFORE_SENTINEL,
            PROSE_AFTER_SENTINEL,
            BLOCK_PROSE_SENTINEL,
        ):
            assert sentinel in full_text, (
                f"Expected prose sentinel {sentinel!r} missing from "
                f"extracted PDF text:\n{full_text}"
            )
        normalized_text = unicodedata.normalize("NFKC", full_text)
        assert "mc" in normalized_text, (
            "Expected the math body's 'mc' substring (NFKC-normalized, "
            "since mitex renders math letters as Mathematical Alphanumeric "
            f"Symbols) in the extracted PDF text:\n{normalized_text}"
        )

        # 13. SC#3 leakage guard -- no raw Typst source token in extracted
        # PDF text.
        for leak in LEAK_SIGNATURES:
            assert leak not in full_text, (
                f"Raw Typst source token {leak!r} leaked into extracted PDF "
                f"text -- the .typ was not typeset:\n{full_text}"
            )

        # 14. Construct G exact-string positive (mitex path, WR-02) -- the
        # id anchor and the mitex(...) call are newline-separated, never
        # juxtaposed on the same line.
        assert (
            "[#metadata(none) <index:equation-construct-g-labeled-eq>]\n\n"
            "mitex(`G = m a" in typ_text
        ), (
            "Construct G (labeled display math in a list item, mitex path) "
            f"did not newline-separate its id anchor from the mitex(...) "
            f"call:\n{typ_text}"
        )
        assert "]mitex(" not in typ_text, (
            "Construct G's id anchor (mitex path) is juxtaposed directly "
            f"against mitex( with no separator:\n{typ_text}"
        )

        # 15. Construct F exact-string positive (WR-03) -- no separator or
        # leading operator precedes the sole math expression in the list
        # item.
        assert "list({\nparbreak()\n\nmi(`a+b`)" in typ_text, (
            "Construct F (list item whose sole content is inline math) "
            f"emitted an unexpected separator or operator before the sole "
            f"math expression:\n{typ_text}"
        )

    def test_typstpdf_separates_inline_math_native_path(
        self, inline_math_after_text_render_gate_dir, temp_build_dir
    ):
        """Build the SAME fixture with ``-D typst_use_mitex=0`` (the native
        ``$...$`` math path) and confirm the same separator correctness."""
        result = _run_sphinx_build_typstpdf(
            inline_math_after_text_render_gate_dir,
            temp_build_dir,
            extra_args=("-D", "typst_use_mitex=0"),
        )

        # 1. The build must exit cleanly, with the same fatal signatures
        # absent.
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf (native math) failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        for signature in (
            "expected semicolon or line break",
            "expected comma",
            "Typst compilation failed",
        ):
            assert signature not in result.stderr, (
                f"typst.compile() rejected the emitted .typ (native math) "
                f"with the fatal '{signature}':\n{result.stderr}"
            )

        # 2. index.typ must exist and use the native $...$ form -- proving
        # the -D override actually reached the translator.
        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")
        assert "$E = m c^2$" in typ_text, (
            "Expected the native $...$ math form in the emitted .typ -- "
            f"the -D typst_use_mitex=0 override did not apply:\n{typ_text}"
        )
        assert "mi(`" not in typ_text, (
            "The mitex mi(`...`) form is still present -- the -D "
            f"typst_use_mitex=0 override did not reach the translator:\n"
            f"{typ_text}"
        )

        # 3. Construct B native exact-string positive.
        assert 'text("Text before math ")\n$E = m c^2$' in typ_text, (
            "Construct B (bullet list item, native path) did not emit "
            f"exactly one newline separator:\n{typ_text}"
        )

        # 4. Construct D native exact-string positive.
        assert 'text("Term ") + $E = m c^2$' in typ_text, (
            "Construct D (definition-list term, native path) did not '+' "
            f"concatenate the term prose and the native math span:\n{typ_text}"
        )

        # 5. Juxtaposition guard for the native path.
        assert ")$" not in typ_text, (
            f"A preceding expression is juxtaposed directly against a "
            f"native $...$ span with no separator:\n{typ_text}"
        )

        # 6. index.pdf must exist and be a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted "
            f"(native math path):\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            assert f.read(4) == b"%PDF", "Generated file is not a valid PDF"

        # 7. PDF text fidelity + leakage guard.
        import pypdf

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)
        for sentinel in (PROSE_BEFORE_SENTINEL, PROSE_AFTER_SENTINEL):
            assert sentinel in full_text, (
                f"Expected prose sentinel {sentinel!r} missing from "
                f"extracted PDF text (native path):\n{full_text}"
            )
        for leak in LEAK_SIGNATURES:
            assert leak not in full_text, (
                f"Raw Typst source token {leak!r} leaked into extracted PDF "
                f"text (native path):\n{full_text}"
            )

        # 8. Construct E native exact-string positive (WR-04) -- the
        # preceding text emission and the native display-math call are
        # newline-separated.
        assert 'text("Text before block math.")\n$ E = m c^2 $' in typ_text, (
            "Construct E (display math in a list item, native path) did "
            f"not newline-separate from the preceding paragraph:\n{typ_text}"
        )

        # 9. Construct G native exact-string positive (WR-02, native half)
        # -- the id anchor and the native $...$ call are newline-separated,
        # never juxtaposed on the same line.
        assert (
            "[#metadata(none) <index:equation-construct-g-labeled-eq>]\n\n"
            "$ G = m a" in typ_text
        ), (
            "Construct G (labeled display math in a list item, native "
            f"path) did not newline-separate its id anchor from the "
            f"native $...$ call:\n{typ_text}"
        )
        assert "]$" not in typ_text, (
            "Construct G's id anchor (native path) is juxtaposed directly "
            f"against a native $...$ span with no separator:\n{typ_text}"
        )
