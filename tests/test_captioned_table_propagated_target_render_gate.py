"""
Real-compile regression gate for TBL-03 (Phase 42): a captioned table
immediately preceded by a standalone target drops the propagated target's
label, aborting the Typst compile.

Root cause (measured against the current, unfixed tree): docutils'
``PropagateTargets`` transform moves a standalone ``.. _label:`` target's id
onto the following captioned table's ``node["ids"]``. ``depart_table``'s
trailing anchor call for the propagated remainder ids --
``self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))`` --
fires while ``self.in_table`` is still ``True``. ``add_text`` (the shared
text-emission helper) routes EVERY append into ``self.table_cell_content``
whenever ``self.in_table`` is set, and that buffer is deleted a few
statements later (after ``self.in_table`` is finally cleared to ``False``)
without ever being read again. The anchor markup is therefore not merely
misplaced -- it is silently discarded. A same-document reference to the
propagated target's label then dangles, and ``typst.compile()`` aborts the
whole document at the semantic label-resolution pass with the real fatal::

    TypstError: label `<index:tbl-target>` does not exist in the document

This module is committed while that bug is still live in
``typsphinx/translator.py`` -- it is the classic-compile-fatal RED,
per milestone invariant #4's TBL-03 exception -- and stays RED until plan
42-04 moves the anchor call to fire after ``self.in_table`` is cleared.

Drives ``-b typstpdf``, never ``-b typst``: the semantic label-resolution
fatal only fires inside ``TypstPDFBuilder.finish()``'s ``typst.compile()``
call, so a ``-b typst`` build would emit the dangling reference but never
actually prove the fatal is (or is not) gone.
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
def captioned_table_propagated_target_render_gate_dir():
    """Return the path to this render-gate's fixture project."""
    return (
        Path(__file__).parent
        / "fixtures"
        / "captioned_table_propagated_target_render_gate"
    )


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


class _BuildArtifacts:
    """
    Small container exposing one class-scoped real build's results: the
    completed subprocess, the emitted ``index.typ`` text (``None`` if the
    build never emitted it), and the path where ``master.pdf`` would land.

    Deliberately asserts nothing itself -- pre-fix, the build fails and
    ``master.pdf`` never appears, and the RED must surface as named
    per-shape test failures rather than as one shared fixture error.
    """

    def __init__(
        self,
        result: subprocess.CompletedProcess,
        typ_text: str | None,
        pdf_path: Path,
    ) -> None:
        self.result = result
        self.typ_text = typ_text
        self.pdf_path = pdf_path


@pytest.fixture(scope="class")
def captioned_table_propagated_target_artifacts(tmp_path_factory):
    """
    Build the fixture through ``-b typstpdf`` ONCE per test class and return
    a small container exposing the result, so the nine thin test methods
    below share a single real compile rather than re-running it per method.
    """
    source_dir = (
        Path(__file__).parent
        / "fixtures"
        / "captioned_table_propagated_target_render_gate"
    )
    build_dir = tmp_path_factory.mktemp("captioned_table_propagated_target")
    result = _run_sphinx_build_typstpdf(source_dir, build_dir)
    typ_path = build_dir / "index.typ"
    typ_text = typ_path.read_text(encoding="utf-8") if typ_path.exists() else None
    pdf_path = build_dir / "master.pdf"
    return _BuildArtifacts(result, typ_text, pdf_path)


def _scan_text(typ_text: str) -> str:
    """
    Strip literal ``raw("...")`` string segments before every regex scan.

    The fixture's own prose contains an inline-literal snippet (`` `` ``
    ``depart_table`` `` `` ``) that the translator renders as a
    ``raw("depart_table")`` string literal -- literal text, not a real Typst
    label token, that must not be picked up by the label-definition or
    label-reference scans below.
    """
    return re.sub(r'raw\("(?:[^"\\]|\\.)*"\)', "", typ_text)


def _label_definitions(scan_text: str) -> list[str]:
    """
    Collect every ``index:``-namespaced label DEFINITION occurrence: an
    ``<index:NAME>`` token NOT immediately preceded by ``link(``.

    Restricted to ``index:``-prefixed labels so unrelated markup elsewhere
    (e.g. the template preamble) can never masquerade as a label; dropping
    the negative lookbehind on ``link(`` would count REFERENCES as
    definitions instead. Duplicates are preserved (D-03 needs the raw
    count, not just the distinct set) -- callers that only need the set of
    defined names should wrap the result in ``set(...)``.
    """
    return re.findall(r"(?<!link\()<(index:[^>]+)>", scan_text)


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the propagated-target anchor render gate",
)
class TestCaptionedTablePropagatedTargetRenderGate:
    """
    Real-compile regression gate proving a same-document cross-reference to
    a target propagated onto a captioned table (D-01's four shapes: named,
    unnamed, list-item-nested, two consecutive targets) resolves once
    ``depart_table``'s trailing anchor call for the propagated remainder ids
    fires after ``self.in_table`` is cleared, instead of being discarded
    into the stale ``table_cell_content`` buffer.

    Requirement: TBL-03 (Phase 42).
    """

    def test_compile_clean(self, captioned_table_propagated_target_artifacts):
        """
        The subprocess itself exits 0, and ``TypstPDFBuilder.finish()``
        logs neither the dangling-label fatal nor a generic compilation
        failure.

        A fatal inside ``TypstPDFBuilder.finish()`` is logged (not raised)
        as an ERROR, so this guards against the exact signatures explicitly
        rather than trusting ``returncode`` alone.
        """
        artifacts = captioned_table_propagated_target_artifacts
        result = artifacts.result
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "does not exist in the document" not in result.stderr, (
            "typst.compile() reported a dangling label -- the captioned-table "
            f"propagated-target anchor fix is not in effect:\nstderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

    def test_shape_a_named_target_anchor(
        self, captioned_table_propagated_target_artifacts
    ):
        """
        Shape A (target + ``:name:``-carrying table): the propagated
        ``tbl-target`` anchor and the table's own ``tbl-name`` figure
        self-anchor postfix must both be present in the emitted source.
        """
        typ_text = captioned_table_propagated_target_artifacts.typ_text
        assert typ_text is not None, "index.typ was not emitted"
        assert "[#metadata(none) <index:tbl-target>]" in typ_text, (
            "The propagated target before the named captioned table did not "
            f"emit an <index:tbl-target> anchor:\n{typ_text}"
        )
        assert " <index:tbl-name>]" in typ_text, (
            "The named captioned table did not emit its own <index:tbl-name> "
            f"figure self-anchor postfix:\n{typ_text}"
        )

    def test_shape_b_noname_target_anchor(
        self, captioned_table_propagated_target_artifacts
    ):
        """
        Shape B (target + table with no ``:name:``): the propagated
        ``tbl-target-noname`` anchor must be present. No assertion may name
        the docutils auto id that owns ``ids[0]`` here -- its exact
        spelling is unstable across document changes.
        """
        typ_text = captioned_table_propagated_target_artifacts.typ_text
        assert typ_text is not None, "index.typ was not emitted"
        assert "[#metadata(none) <index:tbl-target-noname>]" in typ_text, (
            "The propagated target before the unnamed captioned table did "
            f"not emit an <index:tbl-target-noname> anchor:\n{typ_text}"
        )

    def test_shape_c_list_item_target_anchor(
        self, captioned_table_propagated_target_artifacts
    ):
        """
        Shape C (target + table nested in a bullet-list item): the
        propagated ``tbl-target-li`` anchor and the table's own
        ``tbl-name-li`` figure self-anchor postfix must both be present.
        """
        typ_text = captioned_table_propagated_target_artifacts.typ_text
        assert typ_text is not None, "index.typ was not emitted"
        assert "[#metadata(none) <index:tbl-target-li>]" in typ_text, (
            "The propagated target before the list-item-nested captioned "
            f"table did not emit an <index:tbl-target-li> anchor:\n{typ_text}"
        )
        assert " <index:tbl-name-li>]" in typ_text, (
            "The list-item-nested captioned table did not emit its own "
            f"<index:tbl-name-li> figure self-anchor postfix:\n{typ_text}"
        )

    def test_shape_d_two_consecutive_targets_anchor(
        self, captioned_table_propagated_target_artifacts
    ):
        """
        Shape D (two consecutive standalone targets before one captioned
        table): BOTH propagated anchors -- ``tbl-target-a`` and
        ``tbl-target-b`` -- must be present, matched by name rather than by
        list position (the chained-target order arrives reversed relative
        to source order).
        """
        typ_text = captioned_table_propagated_target_artifacts.typ_text
        assert typ_text is not None, "index.typ was not emitted"
        assert "[#metadata(none) <index:tbl-target-a>]" in typ_text, (
            "The first of two consecutive targets before the captioned "
            f"table did not emit an <index:tbl-target-a> anchor:\n{typ_text}"
        )
        assert "[#metadata(none) <index:tbl-target-b>]" in typ_text, (
            "The second of two consecutive targets before the captioned "
            f"table did not emit an <index:tbl-target-b> anchor:\n{typ_text}"
        )

    def test_no_duplicate_label_definition(
        self, captioned_table_propagated_target_artifacts
    ):
        """
        D-03: no ``index:``-namespaced label may be DEFINED more than once.
        The fix must anchor the propagated remainder ids without trading
        the dangling-label fatal for the duplicate-label fatal the in-code
        TBL-02 rationale warns against (Typst "label ... occurs multiple
        times").
        """
        typ_text = captioned_table_propagated_target_artifacts.typ_text
        assert typ_text is not None, "index.typ was not emitted"
        scan_text = _scan_text(typ_text)
        definitions = _label_definitions(scan_text)
        assert len(definitions) == len(set(definitions)), (
            "A label is defined more than once: "
            f"{sorted({name for name in definitions if definitions.count(name) > 1})}"
            f"\n{typ_text}"
        )

    def test_no_dangling_same_document_reference(
        self, captioned_table_propagated_target_artifacts
    ):
        """
        Generic sweep: every same-document ``link(<name>, ...)`` reference
        must have a matching label definition. The set difference (links
        minus definitions) is empty exactly when nothing dangles.
        """
        typ_text = captioned_table_propagated_target_artifacts.typ_text
        assert typ_text is not None, "index.typ was not emitted"
        scan_text = _scan_text(typ_text)
        definition_names = set(_label_definitions(scan_text))
        link_names = set(re.findall(r"link\(<([^>]+)>", scan_text))
        assert link_names, (
            "Expected at least one same-document link(<name>, ...) reference "
            f"in the emitted output:\n{typ_text}"
        )
        dangling = link_names - definition_names
        assert not dangling, (
            "Same-document references with no matching label definition "
            f"(dangling labels): {sorted(dangling)}\n"
            f"definitions present: {sorted(definition_names)}\n{typ_text}"
        )

    def test_caption_less_control_table_not_figure_wrapped(
        self, captioned_table_propagated_target_artifacts
    ):
        """
        The caption-less control table (no caption, no name, no preceding
        target) is not figure-wrapped: ``kind: table`` occurs exactly 4
        times -- once per captioned shape (A, B, C, D), never for the
        control.
        """
        typ_text = captioned_table_propagated_target_artifacts.typ_text
        assert typ_text is not None, "index.typ was not emitted"
        count = typ_text.count("kind: table")
        assert count == 4, (
            f"Expected exactly 4 figure-wrapped (kind: table) occurrences "
            f"(the four captioned shapes only), found {count}:\n{typ_text}"
        )

    def test_pdf_magic_bytes(self, captioned_table_propagated_target_artifacts):
        """
        ``master.pdf`` exists, is non-empty, and starts with the ``%PDF``
        magic bytes -- the only proof the document compiled to a valid PDF
        and the dangling-label fatal is gone.
        """
        pdf_path = captioned_table_propagated_target_artifacts.pdf_path
        result = captioned_table_propagated_target_artifacts.result
        assert pdf_path.exists(), (
            "master.pdf was not produced -- typst.compile() aborted, most "
            f"likely on a dangling label:\nstderr: {result.stderr}"
        )
        assert pdf_path.stat().st_size > 0, "PDF file is empty"
        with open(pdf_path, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
