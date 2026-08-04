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


def _extract_paren_block(text: str, open_idx: int) -> str:
    """
    Return the substring from ``text[open_idx]`` (which MUST be an opening
    ``(``) to its matching closing ``)``, inclusive, using simple depth
    counting over ``(``/``)`` characters only.

    Used to isolate ONE specific ``table(...)`` call's own argument list
    from the flattened ``.typ`` text, even when that call's cell content
    contains further nested ``table(...)`` calls (which introduce their own
    balanced parens at a deeper level).
    """
    depth = 0
    for i in range(open_idx, len(text)):
        char = text[i]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[open_idx : i + 1]
    raise ValueError(f"Unbalanced parens starting at index {open_idx}")


def _count_top_level_brace_entries(text: str) -> int:
    """
    Count ``{...}`` groups that open and close at brace-DEPTH ZERO within
    ``text`` -- i.e. top-level cell entries, not brace pairs nested inside
    another cell's own content (e.g. a nested table's own cells, or a
    ``text(...)``/``par(...)`` call's argument braces one level deeper).

    Every table cell this translator emits (``_format_table_cell``) is
    wrapped in exactly one top-level ``{...}`` code block, so this count
    equals the number of cells a ``table(...)`` call actually emits --
    used to prove a full row's cell count (including empty cells) survived
    TBL-04's fix, since a naive per-line indentation count is unreliable
    once a cell's own content is itself a nested ``table(...)`` call (whose
    OWN cells also happen to use the same 2-space relative indent).
    """
    depth = 0
    count = 0
    for char in text:
        if char == "{":
            if depth == 0:
                count += 1
            depth += 1
        elif char == "}":
            depth -= 1
    return count


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

    def test_grid_table_in_list_table_preserves_outer_cells_and_caption(
        self, nested_table_render_gate_dir, temp_build_dir
    ):
        """
        Section 2 (grid table nested in list-table). D-01's second nesting
        shape: proves the fix generalizes across the OUTER table's directive
        TYPE (list-table) combined with an INNER table of a DIFFERENT
        directive type (grid ``.. table::``) -- not just the one shape
        (list-table in list-table) Task 1 measured.
        """
        result = _run_sphinx_build_typstpdf(
            nested_table_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        typ_text = typ_output.read_text(encoding="utf-8")

        for sentinel in (
            "NT2HEADA",
            "NT2HEADB",
            "NT2PLAIN",
            "NT2OUTERCAP",
            "NT2INNERA",
            "NT2INNERB",
        ):
            assert sentinel in typ_text, (
                f"Expected sentinel '{sentinel}' in emitted index.typ -- "
                f"TBL-04 nested-table state clobber regression (grid table "
                f"in list-table):\n{typ_text}"
            )

        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists() and pdf_output.stat().st_size > 0
        reader = pypdf.PdfReader(str(pdf_output))
        full_text = "\n".join(page.extract_text() for page in reader.pages)
        for sentinel in ("NT2HEADA", "NT2HEADB", "NT2PLAIN", "NT2INNERA"):
            assert sentinel in full_text, (
                f"Expected sentinel '{sentinel}' in extracted PDF text -- "
                "TBL-04 nested-table state clobber regression (grid table "
                f"in list-table):\n{full_text}"
            )

    def test_list_table_in_grid_table_keeps_leaked_cell_inside_outer_table(
        self, nested_table_render_gate_dir, temp_build_dir
    ):
        """
        Section 3 (list-table nested in a grid ``.. table::``). D-01's third
        nesting shape, PLUS the ordering edge CONTEXT.md's ``<specifics>``
        section 2 measured: the outer grid table's OTHER cell (``NT3OUTERD``)
        must render INSIDE the outer table rather than leaking out as a bare
        ``par(...)`` after it. Asserted POSITIONALLY: the offset of
        ``NT3OUTERD`` must be smaller than the offset of the ``kind: table``
        argument that closes THIS section's outer table's figure wrapper --
        proving the cell is inside the table() call, not after the closing
        figure().
        """
        result = _run_sphinx_build_typstpdf(
            nested_table_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        typ_text = typ_output.read_text(encoding="utf-8")

        for sentinel in ("NT3OUTERCAP", "NT3INNERA", "NT3INNERB", "NT3OUTERD"):
            assert sentinel in typ_text, (
                f"Expected sentinel '{sentinel}' in emitted index.typ -- "
                f"TBL-04 nested-table state clobber regression (list-table "
                f"in grid table):\n{typ_text}"
            )

        # Isolate this section's own slice of the document so the "kind:
        # table" search cannot accidentally match a DIFFERENT section's
        # figure close.
        section_start = typ_text.index(
            'Section 3: list-table in grid table")}) '
            "<index:section-3-list-table-in-grid-table>]"
        )
        section_end = typ_text.index(
            'Section 4: three-level nest")}) <index:section-4-three-level-nest>]'
        )
        section_text = typ_text[section_start:section_end]

        outerd_offset = section_text.find("NT3OUTERD")
        kind_table_offset = section_text.find("kind: table")
        assert outerd_offset != -1 and kind_table_offset != -1, (
            "Expected both 'NT3OUTERD' and 'kind: table' in section 3's "
            f"slice of the emitted index.typ:\n{section_text}"
        )
        assert outerd_offset < kind_table_offset, (
            "NT3OUTERD leaked OUTSIDE the outer table -- it must appear "
            "BEFORE the 'kind: table' argument that closes the outer "
            f"table's figure wrapper, not after it:\n{section_text}"
        )

    def test_three_level_nest_preserves_every_levels_own_cells(
        self, nested_table_render_gate_dir, temp_build_dir
    ):
        """
        Section 4 (a three-level table nest). D-01's depth-generalization
        case: the fix must generalize over NESTING DEPTH, not just over the
        one shape measured first -- if it passes the three two-level shapes
        but fails three-deep, that is a signal the fix shape is wrong.
        Asserts all three levels' own cells are present, AND that the three
        ``table(`` calls nest (their offsets are strictly increasing in
        source order), so a level cannot have been hoisted out of its
        parent.
        """
        result = _run_sphinx_build_typstpdf(
            nested_table_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        typ_text = typ_output.read_text(encoding="utf-8")

        for sentinel in (
            "NT4L1CAP",
            "NT4L1PLAIN",
            "NT4L2PLAIN",
            "NT4L3A",
            "NT4L3B",
        ):
            assert sentinel in typ_text, (
                f"Expected sentinel '{sentinel}' in emitted index.typ -- "
                f"TBL-04 three-level nest regression:\n{typ_text}"
            )

        section_start = typ_text.index(
            'Section 4: three-level nest")}) <index:section-4-three-level-nest>]'
        )
        section_end = typ_text.index(
            'Section 5: nested table inside a header cell")}) '
            "<index:section-5-nested-table-inside-a-header-cell>]"
        )
        section_text = typ_text[section_start:section_end]

        first_table = section_text.find("table(")
        assert (
            first_table != -1
        ), f"Expected at least one 'table(' call in section 4:\n{section_text}"
        second_table = section_text.find("table(", first_table + len("table("))
        assert second_table != -1, (
            "Expected a SECOND 'table(' call (level 2 nested inside level "
            f"1) in section 4:\n{section_text}"
        )
        third_table = section_text.find("table(", second_table + len("table("))
        assert third_table != -1, (
            "Expected a THIRD 'table(' call (level 3 nested inside level 2) "
            f"in section 4:\n{section_text}"
        )
        assert first_table < second_table < third_table, (
            "The three 'table(' calls in section 4 do not appear in "
            "strictly increasing source order -- a level may have been "
            f"hoisted out of its parent:\n{section_text}"
        )

    def test_nested_table_inside_header_cell_keeps_outer_header_classification(
        self, nested_table_render_gate_dir, temp_build_dir
    ):
        """
        Section 5 (a nested table inside the OUTER table's FIRST header
        cell). This is the RESEARCH Pitfall 1 / Assumption A2 falsification
        case: without restoring ``self.in_thead`` across the inner table's
        own ``depart_thead``, the outer table's SECOND header cell
        (``NT5HEADB``) is silently misclassified as a body cell once the
        inner table's ``depart_thead`` clears ``self.in_thead`` back to
        False.

        Asserts ``NT5HEADB`` is emitted INSIDE the outer table's
        ``table.header(`` group, while ``NT5BODYA`` (an outer BODY cell)
        appears only AFTER that group closes. Also asserts ``NT5INNERHEAD``
        (the inner table's own header cell) is present anywhere in the
        emitted ``.typ``.
        """
        result = _run_sphinx_build_typstpdf(
            nested_table_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        typ_text = typ_output.read_text(encoding="utf-8")

        assert "NT5INNERHEAD" in typ_text, (
            "Expected the inner table's own header cell 'NT5INNERHEAD' "
            f"anywhere in the emitted index.typ:\n{typ_text}"
        )

        section_start = typ_text.index(
            'Section 5: nested table inside a header cell")}) '
            "<index:section-5-nested-table-inside-a-header-cell>]"
        )
        section_end = typ_text.index(
            'Section 6: adjacency, empty cell, and sibling tables")}) '
            "<index:section-6-adjacency-empty-cell-and-sibling-tables>]"
        )
        section_text = typ_text[section_start:section_end]

        header_start = section_text.find("table.header(")
        bodya_pos = section_text.find("NT5BODYA")
        assert header_start != -1 and bodya_pos != -1, (
            "Expected both 'table.header(' and 'NT5BODYA' in section 5's "
            f"slice of the emitted index.typ:\n{section_text}"
        )
        header_region = section_text[header_start:bodya_pos]

        assert "NT5HEADB" in header_region, (
            "NT5HEADB (the outer table's SECOND header cell) was NOT "
            "classified as a header cell -- self.in_thead was not "
            "restored after the inner table's own depart_thead cleared "
            f"it (RESEARCH Assumption A2):\n{section_text}"
        )
        assert "NT5BODYA" not in header_region, (
            "NT5BODYA (an outer BODY cell) was found INSIDE the outer "
            f"table's table.header(...) group:\n{section_text}"
        )

    def test_adjacency_empty_cell_and_sibling_tables_all_render_correctly(
        self, nested_table_render_gate_dir, temp_build_dir
    ):
        """
        Section 6 (sibling text + a nested table in the SAME cell, an
        outer row with a deliberately EMPTY cell, and two SIBLING top-level
        tables following the main one).

        Asserts:

        - ``NT6TEXTBEFORE`` and ``NT6INNERA`` are both present, with
          ``NT6TEXTBEFORE`` preceding ``NT6INNERA`` (the sibling text in
          the same cell survives the nested table, in source order);
        - ``NT6ROWTWO`` is present, and the outer ``table(...)`` call still
          emits its FULL cell count (4 top-level ``{...}`` entries, matching
          its 2-column x 2-row shape) -- proving the deliberately empty
          cells were NOT dropped;
        - ``NT7SIBA``/``NT7SIBB`` are both present, each inside its OWN
          ``table(...)`` call (they are SIBLING top-level tables, not
          nested inside the main one).
        """
        result = _run_sphinx_build_typstpdf(
            nested_table_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        typ_text = typ_output.read_text(encoding="utf-8")

        section_start = typ_text.index(
            'Section 6: adjacency, empty cell, and sibling tables")}) '
            "<index:section-6-adjacency-empty-cell-and-sibling-tables>]"
        )
        section_end = typ_text.index(
            'Section 7: top-level control")}) <index:section-7-top-level-control>]'
        )
        section_text = typ_text[section_start:section_end]

        textbefore_pos = section_text.find("NT6TEXTBEFORE")
        innera_pos = section_text.find("NT6INNERA")
        assert textbefore_pos != -1 and innera_pos != -1, (
            "Expected both 'NT6TEXTBEFORE' and 'NT6INNERA' in section 6:\n"
            f"{section_text}"
        )
        assert textbefore_pos < innera_pos, (
            "NT6TEXTBEFORE must precede NT6INNERA in source order (the "
            "sibling text in the same cell must survive the nested "
            f"table):\n{section_text}"
        )

        assert (
            "NT6ROWTWO" in section_text
        ), f"Expected 'NT6ROWTWO' in section 6:\n{section_text}"

        # Isolate the main outer table(...) call's own argument list (the
        # FIRST 'table(' in this section, bounded by matching parens) and
        # count its top-level cell entries -- must be 4 (2 columns x 2
        # rows), proving the deliberately-empty cells were emitted, not
        # dropped.
        main_table_open = section_text.index("(", section_text.index("table("))
        main_table_block = _extract_paren_block(section_text, main_table_open)
        cell_count = _count_top_level_brace_entries(main_table_block)
        assert cell_count == 4, (
            "Expected the outer table's own table(...) call to emit 4 "
            "top-level cell entries (2 columns x 2 rows, including the "
            "deliberately empty cells) -- a dropped empty cell would "
            f"lower this count. Got {cell_count}. Block:\n{main_table_block}"
        )

        # The two SIBLING top-level tables: NT7SIBA and NT7SIBB must each
        # be present, inside their OWN separate table(...) call (found
        # AFTER the main outer table's own closing paren, i.e. outside
        # main_table_block).
        after_main_table = section_text[
            section_text.index(main_table_block) + len(main_table_block) :
        ]
        assert "NT7SIBA" in after_main_table and "NT7SIBB" in after_main_table, (
            "Expected NT7SIBA and NT7SIBB as SIBLING top-level tables "
            f"AFTER the main outer table's own close:\n{after_main_table}"
        )
        siba_table_count = after_main_table.count("table(\n  columns: (100fr),")
        assert siba_table_count >= 2, (
            "Expected NT7SIBA and NT7SIBB to each render inside their OWN "
            f"separate table(...) call:\n{after_main_table}"
        )

    def test_top_level_control_table_is_bare_table_no_figure_wrapper(
        self, nested_table_render_gate_dir, temp_build_dir
    ):
        """
        Section 7 (a caption-less top-level table, no nesting anywhere in
        it). ``NT8CTRLA``/``NT8CTRLB`` must be present, and the emitted
        ``.typ`` for this section must contain a bare ``table(`` call with
        NO ``figure(`` wrapper -- the caption-less top-level path stays
        completely untouched by TBL-04's fix.
        """
        result = _run_sphinx_build_typstpdf(
            nested_table_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        typ_text = typ_output.read_text(encoding="utf-8")

        section_start = typ_text.index(
            'Section 7: top-level control")}) <index:section-7-top-level-control>]'
        )
        section_text = typ_text[section_start:]

        assert (
            "NT8CTRLA" in section_text and "NT8CTRLB" in section_text
        ), f"Expected NT8CTRLA and NT8CTRLB in section 7:\n{section_text}"
        assert "figure(" not in section_text, (
            "The caption-less top-level control table must NOT be "
            f"figure-wrapped:\n{section_text}"
        )
        assert (
            "table(" in section_text
        ), f"Expected a bare table( call in section 7:\n{section_text}"
