"""
Real-compile regression gate for the ``doctest_block`` translator handler
(Phase 74, TRN-01, TRN-02, GATE-01).

``docutils`` builds a ``doctest_block`` node for any ``>>>``-led reST
fragment. ``TypstTranslator`` has never had a dedicated visitor for it, so
it falls through ``unknown_visit()``/``unknown_departure()`` -- which warn
but emit no separator at all -- and its ``Text`` children are visited as
ordinary inline text, collapsing every prompt/continuation/output line
onto one physical Typst source line. This module drives the two contexts
D-06 specifies through a real ``sphinx-build -b typstpdf`` compile:

- context (a): a plain-paragraph-position doctest block, with a leading
  paragraph before it and a trailing paragraph after it. The trailing
  paragraph is load-bearing -- it is what turns the missing-handler defect
  into a genuine ``typst.compile()`` refusal (``expected semicolon or line
  break``), not merely a content collapse.
- context (b): one master carrying shape (b1), a definition-list
  ``Examples:`` item (the sphinx-autoapi ``terms.item(...)`` position
  TRN-02 names) with a leading paragraph before the doctest block, and
  shape (b2), a bullet-list item with a leading paragraph, the doctest
  block, then a trailing paragraph -- the shape that genuinely exercises
  ``in_list_item``/``list_item_needs_separator``. Both shapes sit at a
  NON-FIRST position in their container.

All three masters are driven from ONE ``sphinx-build -b typstpdf``
invocation, shared across every test method in this module via a
module-scoped fixture.

Every expected doctest-text value comes from ``_source_doctest_block``,
which reads the fixture's own reST source -- never a value transcribed
from observed build output. Every ``.typ``/subprocess-output read in this
module is text-mode UTF-8 (``encoding="utf-8"``, and
``errors="replace"``/``text=True`` on the subprocess side) so a Windows
CR-newline write-mode translation cannot spuriously fail this gate.

The RED transcript -- this gate observed failing against the pre-handler
translator, on a commit whose ``typsphinx/`` tree equals the milestone
base -- is recorded verbatim in ``74-RED-EVIDENCE.md``.
"""

import re
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "doctest_block_render_gate"

MASTER_DOCNAMES = ["index", "context_a_paragraph", "context_b_nonfirst_positions"]
SHAPE_SENTINELS = ["ctx_a_paragraph", "ctx_b1_definition", "ctx_b2_bullet"]

UNKNOWN_DOCTEST_BLOCK = "unknown node type: <doctest_block"
FENCE_OPEN = "codly(number-format: none)\n```python\n"


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typstpdf`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``) so
    the exact interpreter/venv running this test is reused, sidestepping the
    documented NixOS-sandbox PATH-shadowing hazard. The explicit
    ``encoding="utf-8", errors="replace"`` decode keeps a non-ASCII warning
    text from raising on a Windows runner.
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
        encoding="utf-8",
        errors="replace",
    )


def _wrapper_pdf_path(build_dir: Path, docname: str) -> Path:
    """Return the expected wrapper PDF path for a master docname."""
    return build_dir / f"{docname}-out.pdf"


def _assert_pdf_magic(path: Path, docname: str) -> None:
    """
    Assert ``path`` is a non-empty file starting with the PDF magic bytes.

    ``docname`` is included in every assertion message so a single failing
    master is attributable without re-running the build.
    """
    assert path.exists(), f"{docname}: {path} was not produced"
    assert path.stat().st_size > 0, f"{docname}: {path} is empty"
    with open(path, "rb") as f:
        magic = f.read(4)
        assert (
            magic == b"%PDF"
        ), f"{docname}: {path} is not a valid PDF (magic: {magic!r})"


def _read_typ(build_dir: Path, docname: str) -> str:
    """Read the emitted ``.typ`` content file for ``docname``, text-mode UTF-8."""
    return (build_dir / f"{docname}.typ").read_text(encoding="utf-8")


def _source_doctest_block(rst_name: str, sentinel: str) -> str:
    """
    Read the doctest block whose first prompt line contains ``sentinel``
    directly from the fixture's own reST source (never from observed build
    output).

    Finds the first line whose ``lstrip()`` starts with ``">>> " + sentinel``,
    collects lines until the first whitespace-only line, and returns
    ``textwrap.dedent("\\n".join(lines))``. Fails with a clear message when
    the sentinel is absent.
    """
    text = (FIXTURE_DIR / rst_name).read_text(encoding="utf-8")
    lines = text.splitlines()
    prefix = ">>> " + sentinel
    start = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith(prefix):
            start = i
            break
    assert start is not None, (
        f"sentinel {sentinel!r} not found as a doctest prompt (line starting "
        f"with {prefix!r}) in {rst_name}"
    )
    collected = []
    for line in lines[start:]:
        if line.strip() == "":
            break
        collected.append(line)
    return textwrap.dedent("\n".join(collected))


def _unknown_doctest_chunks(output: str) -> list[str]:
    """
    Return every ``unknown node type: <doctest_block ...>...</doctest_block>``
    warning chunk in ``output``. A warning spans several lines, because the
    node's text follows the tag.
    """
    return re.findall(
        r"unknown node type: <doctest_block.*?</doctest_block>", output, flags=re.DOTALL
    )


@pytest.fixture(scope="module")
def doctest_block_build(tmp_path_factory):
    """Drive ONE ``sphinx-build -b typstpdf`` over the fixture, shared across tests."""
    build_dir = tmp_path_factory.mktemp("doctest_block_render_gate") / "_build"
    result = _run_sphinx_build_typstpdf(FIXTURE_DIR, build_dir)
    return result, build_dir


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the doctest_block render gate",
)
class TestDoctestBlockRenderGate:
    """
    Real-compile regression gate proving TRN-01/TRN-02: a ``>>>`` doctest
    block renders as a codly-styled ``python`` fence with its line structure
    intact, in both D-06 contexts, through a real ``typst.compile()``.
    """

    def test_build_exits_zero_without_compile_failure(self, doctest_block_build):
        result, _ = doctest_block_build
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        combined = result.stdout + result.stderr
        assert "master document(s) failed" not in combined, (
            "Found TypstPDFBuilder.finish()'s aggregate failure message -- "
            f"one or more masters did not compile:\n{combined}"
        )
        assert "expected semicolon or line break" not in combined, (
            "Found the unseparated-expression Typst refusal -- the doctest_block "
            f"handler is not applied:\n{combined}"
        )

    def test_build_reports_no_doctest_block_unknown_node(self, doctest_block_build):
        result, _ = doctest_block_build
        combined = result.stdout + result.stderr
        assert UNKNOWN_DOCTEST_BLOCK not in combined, (
            "Found the unknown-node warning for doctest_block -- the handler "
            f"is not applied:\n{combined}"
        )

    @pytest.mark.parametrize("sentinel", SHAPE_SENTINELS)
    def test_no_unknown_node_warning_for_shape(self, doctest_block_build, sentinel):
        result, _ = doctest_block_build
        combined = result.stdout + result.stderr
        chunks = _unknown_doctest_chunks(combined)
        for chunk in chunks:
            assert sentinel not in chunk, (
                f"Found shape sentinel {sentinel!r} inside an unknown-node warning "
                f"chunk -- the handler is not applied for this shape:\n{chunk}"
            )

    @pytest.mark.parametrize("docname", MASTER_DOCNAMES)
    def test_master_writes_pdf(self, doctest_block_build, docname):
        _, build_dir = doctest_block_build
        _assert_pdf_magic(_wrapper_pdf_path(build_dir, docname), docname)

    def test_context_a_paragraph_line_structure(self, doctest_block_build):
        _, build_dir = doctest_block_build
        typ_text = _read_typ(build_dir, "context_a_paragraph")
        block = _source_doctest_block("context_a_paragraph.rst", "ctx_a_paragraph")

        assert FENCE_OPEN + block + "\n```\n" in typ_text, (
            "Expected the doctest block inside a codly-styled python fence, "
            f"lines verbatim and in source order:\n{typ_text}"
        )
        assert 'text(">>> ' not in typ_text, (
            'Found a collapsed text(">>> ...") run -- the doctest block was '
            f"not routed through the code-block emission path:\n{typ_text}"
        )
        fence_index = typ_text.index(FENCE_OPEN)
        trailing_index = typ_text.index("Trailing paragraph after the doctest block.")
        assert trailing_index > fence_index, (
            "Expected the trailing paragraph to appear AFTER the fence in "
            f"source order:\n{typ_text}"
        )

    def test_context_b1_definition_list_line_structure(self, doctest_block_build):
        _, build_dir = doctest_block_build
        typ_text = _read_typ(build_dir, "context_b_nonfirst_positions")
        block = _source_doctest_block(
            "context_b_nonfirst_positions.rst", "ctx_b1_definition"
        )

        assert 'terms.item(text("Examples:")' in typ_text, (
            "Expected the definition-list term 'Examples:' to appear as a "
            f"terms.item(...) call:\n{typ_text}"
        )
        assert FENCE_OPEN + block + "\n```" in typ_text, (
            "Expected shape (b1)'s doctest block inside a codly-styled python "
            f"fence, lines verbatim and in source order:\n{typ_text}"
        )
        assert 'text(">>> ' not in typ_text, (
            'Found a collapsed text(">>> ...") run -- the doctest block was '
            f"not routed through the code-block emission path:\n{typ_text}"
        )
        leading_index = typ_text.index("Leading paragraph of the definition.")
        fence_index = typ_text.index(FENCE_OPEN)
        assert leading_index < fence_index, (
            "Expected the leading paragraph of the definition to appear BEFORE "
            f"the fence in source order:\n{typ_text}"
        )

    def test_context_b2_bullet_list_item_line_structure(self, doctest_block_build):
        _, build_dir = doctest_block_build
        typ_text = _read_typ(build_dir, "context_b_nonfirst_positions")
        block = _source_doctest_block(
            "context_b_nonfirst_positions.rst", "ctx_b2_bullet"
        )

        # The list-item `{ }` wrapper visit_literal_block opens only when
        # in_list_item is true.
        assert "{\n" + FENCE_OPEN + block + "\n```\n}" in typ_text, (
            "Expected shape (b2)'s doctest block inside the list-item { } "
            f"wrapper AND a codly-styled python fence:\n{typ_text}"
        )
        assert 'text(">>> ' not in typ_text, (
            'Found a collapsed text(">>> ...") run -- the doctest block was '
            f"not routed through the code-block emission path:\n{typ_text}"
        )
        leading_index = typ_text.index("Leading paragraph in the list item.")
        fence_index = typ_text.index(FENCE_OPEN + block)
        trailing_index = typ_text.index("Trailing paragraph in the same list item.")
        assert leading_index < fence_index < trailing_index, (
            "Expected leading paragraph, then the fence, then the trailing "
            f"paragraph, in that source order:\n{typ_text}"
        )
