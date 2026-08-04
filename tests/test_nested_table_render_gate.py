"""
Real-compile regression gate for TBL-04 (Phase 43) -- a table nested inside
another table's cell silently clobbers the enclosing table's accumulated
cells, column count, column widths, caption, header-row flag and span
counters, because the translator's table state is a set of
unconditionally-reset SCALARS (``self.table_cells``, ``self.table_colcount``,
``self.table_colwidths``, ``self.table_caption``,
``self.table_cell_content``, ``self.in_thead``,
``self.current_morecols``/``self.current_morerows``) rather than a stack
that survives nesting -- see
``.planning/todos/pending/2026-08-04-nested-table-clobbers-outer-table-state.md``.

**This is a STRUCTURAL defect, not a compile fatal.** The pre-fix build
exits 0 with no warning and produces a real, well-formed PDF -- the emitted
document is plausible-looking but states something FALSE: the INNER table's
body is emitted underneath the OUTER table's caption, with every outer cell
(including the header row) silently dropped. Every assertion below therefore
checks the emitted ``.typ`` text and/or the ``pypdf``-extracted PDF text
directly for sentinel presence, never the build's exit status alone.

The fix (``typsphinx/translator.py``): ``visit_table``/``depart_table`` push
a full snapshot of the enclosing table's scalar state onto a private
``self._table_state_stack`` when a table is already open (i.e. this table
node is NESTED), reset for the inner table's own use, and pop-and-restore
that snapshot in ``depart_table`` before deciding whether the inner table's
rendered markup goes into the restored enclosing cell's buffer (nested) or
``self.body`` (top-level) -- see ``_push_table_state``/``_pop_table_state``.

Requirements: TBL-04, GATE-01 (43-01-PLAN.md, 43-RESEARCH.md, 43-CONTEXT.md).
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
def nested_table_render_gate_dir():
    """Return the path to the nested_table_render_gate fixture."""
    return Path(__file__).parent / "fixtures" / "nested_table_render_gate"


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
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the GATE-01 render gate",
)
class TestNestedTableRenderGate:
    """
    Real-compile regression gate proving TBL-04's fix: a table nested inside
    another table's cell no longer clobbers the enclosing table's
    accumulated cells, column count, column widths, caption, header-row
    flag or span counters.

    Requirements: TBL-04, GATE-01 (43-01-PLAN.md Task 1).
    """

    def test_list_table_in_list_table_preserves_outer_cells_and_caption(
        self, nested_table_render_gate_dir, temp_build_dir
    ):
        """
        Section 1 (list-table nested in list-table). Build the fixture
        through ``-b typstpdf`` and confirm:

        - the build exits cleanly and produces a real, non-empty PDF (the
          pre-fix build ALSO does this -- the RED signal is not a nonzero
          exit code);
        - the OUTER table's header cells (``NT1HEADA``/``NT1HEADB``), its
          plain body cell (``NT1PLAIN``) and its caption (``NT1OUTERCAP``)
          are all present in the emitted ``index.typ``;
        - the INNER table's own cells (``NT1INNERA``/``NT1INNERB``) are
          present in the emitted ``index.typ``, rendering inside its own
          cell rather than replacing the outer table's body;
        - ``NT1HEADA``, ``NT1PLAIN`` and ``NT1INNERA`` all appear in the
          ``pypdf``-extracted PDF text -- the stronger, structural-loss-proof
          half, since the pre-fix build has no downstream error surface at
          all (it compiles to a real, well-formed PDF).
        """
        result = _run_sphinx_build_typstpdf(
            nested_table_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        for sentinel in (
            "NT1OUTERCAP",
            "NT1HEADA",
            "NT1HEADB",
            "NT1PLAIN",
            "NT1INNERA",
            "NT1INNERB",
        ):
            assert sentinel in typ_text, (
                f"Expected sentinel '{sentinel}' in emitted index.typ -- "
                f"TBL-04 nested-table state clobber regression "
                f"(list-table in list-table):\n{typ_text}"
            )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted:\n"
            f"stderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)

        for sentinel in ("NT1HEADA", "NT1PLAIN", "NT1INNERA"):
            assert sentinel in full_text, (
                f"Expected sentinel '{sentinel}' in extracted PDF text -- "
                "TBL-04 nested-table state clobber regression (list-table "
                f"in list-table):\n{full_text}"
            )
