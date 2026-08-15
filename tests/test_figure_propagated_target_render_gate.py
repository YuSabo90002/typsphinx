"""
Permanent figure-side regression gate for D-09/D-10 (Phase 42, 42-02-PLAN.md
Task 2).

This is NOT a RED-to-GREEN recording. Unlike the table-side gate
(``tests/test_captioned_table_propagated_target_render_gate.py``, 42-01),
the figure path is already correct today, so this module is GREEN from its
first run against unfixed production source. Its purpose is forward-looking:
Phase 25 modelled the table departure handler on the figure departure
handler (Phase 25 D-04), so this gate is the tripwire that fails loudly if
a FUTURE change ever copies a broken table-side ordering back onto the
figure side, or introduces an ``in_figure``-gated buffer diversion that does
not exist today.

Why the figure path is safe today, in code terms:

- ``add_text`` (``typsphinx/translator.py:423-437``) branches on exactly one
  flag, ``self.in_table`` -- it never consults ``self.in_figure``. There is
  no per-figure buffer for a stray anchor call to be diverted into.
- ``depart_figure`` (``typsphinx/translator.py:2480-2531``) emits its own
  self-anchor postfix (``) <label>]`` carrying ``ids[0]``) directly inside
  the markup block it is already building, then calls
  ``self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))`` for
  the propagated remainder, and only THEN clears ``self.in_figure = False``.
  Because ``add_text`` never gates on ``self.in_figure``, both calls append
  straight to ``self.body`` regardless of the flag's state at the time they
  fire -- the ordering that is load-bearing for tables (where
  ``self.in_table`` gates a per-cell buffer swap) is irrelevant here.

Covers exactly D-10's three measured shapes against the dedicated fixture
``tests/fixtures/figure_propagated_target_render_gate/`` -- a `:name:`-
carrying figure with a preceding target, a figure with no `:name:` and a
preceding target, and a figure inside a bullet-list item. D-10 explicitly
scopes the figure gate to three shapes; the two-consecutive-targets shape
measured on the table side was never measured for figures and is
deliberately absent here.

Fixture-scoping rule (do not merge with
``tests/fixtures/figure_target_caption_render_gate/``): that fixture's
figures carry the ``:target:`` DIRECTIVE OPTION, which docutils wraps as a
``reference`` node around the figure (a ``visit_reference``/
``depart_reference`` path) -- a different mechanism that never invokes
``PropagateTargets``. This gate's fixture uses only standalone
``.. _label:`` target directives, which DO invoke ``PropagateTargets``.

Drives the full ``-b typstpdf`` path -- NOT ``-b typst`` -- because the
dangling-label fatal this gate class guards against only fires inside
``TypstPDFBuilder.finish()``'s ``typst.compile()`` call; a ``-b typst`` build
would emit any dangling link but never compile it, proving nothing.
"""

import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
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

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a bare ``sphinx-build``) so the exact interpreter/venv running this
    test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard.
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


@dataclass
class _FigureGateArtifacts:
    """The single real build's outputs, shared read-only across every test
    method below via a class-scoped fixture."""

    result: subprocess.CompletedProcess
    typ_text: str
    pdf_path: Path


@pytest.fixture(scope="class")
def figure_gate_artifacts(tmp_path_factory):
    """
    Build the ``figure_propagated_target_render_gate`` fixture through
    ``-b typstpdf`` ONCE per class and return its artifacts. Asserts nothing
    itself -- every test method below makes its own assertion against the
    shared build so a failure names the specific behavior that broke.
    """
    source_dir = (
        Path(__file__).parent / "fixtures" / "figure_propagated_target_render_gate"
    )
    build_dir = tmp_path_factory.mktemp("fig_gate") / "_build"
    result = _run_sphinx_build_typstpdf(source_dir, build_dir)
    # Phase 47 (R1/R4): the translator-body markup assertions below read
    # the CONTENT file (docname-derived, "index.typ", unchanged); only the
    # compiled PDF moves to the WRAPPER's own output ("master.pdf", the
    # fixture's typst_documents target after de-collision).
    typ_output = build_dir / "index.typ"
    typ_text = typ_output.read_text(encoding="utf-8") if typ_output.exists() else ""
    pdf_path = build_dir / "master.pdf"
    return _FigureGateArtifacts(result=result, typ_text=typ_text, pdf_path=pdf_path)


def _strip_raw_segments(text: str) -> str:
    """
    Strip ``raw("...")`` segments before every regex scan below. The
    fixture's own prose can legitimately contain inline-literal snippets
    documenting emitted Typst forms; those are literal text, not real Typst
    expressions, and must not masquerade as label references or
    definitions.
    """
    return re.sub(r'raw\("(?:[^"\\]|\\.)*"\)', "", text)


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the figure propagated-target render gate",
)
class TestFigurePropagatedTargetRenderGate:
    """
    Permanent D-09/D-10 regression gate: a captioned figure preceded by a
    standalone target emits BOTH the figure's own self-anchor and the
    propagated target's anchor, so the compile never aborts on a dangling
    label. Green against unfixed production source -- see the module
    docstring for why.

    Requirements: TBL-03 (Phase 42, D-09/D-10).
    """

    def test_typstpdf_build_compiles_without_dangling_label(
        self, figure_gate_artifacts
    ):
        """
        The build exits cleanly and ``typst.compile()`` reports neither the
        semantic dangling-label fatal nor a general compilation failure.
        """
        result = figure_gate_artifacts.result
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "does not exist in the document" not in result.stderr, (
            "typst.compile() reported a dangling label on the figure path -- "
            f"the figure regression gate has regressed:\nstderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            f"TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

    def test_shape1_named_figure_with_preceding_target_emits_both_anchors(
        self, figure_gate_artifacts
    ):
        """
        D-10 shape 1: a `:name:`-carrying figure preceded by a standalone
        target must emit BOTH its own self-anchor (``ids[0]``, the
        `:name:`-derived id) and the propagated target's ``metadata(none)``
        anchor.
        """
        typ_text = figure_gate_artifacts.typ_text
        assert "[#metadata(none) <index:fig-target>]" in typ_text, (
            "The propagated target before the named figure did not emit an "
            f"<index:fig-target> anchor:\n{typ_text}"
        )
        assert " <index:fig-name>]" in typ_text, (
            "The named figure did not emit its own <index:fig-name> "
            f"self-anchor postfix:\n{typ_text}"
        )

    def test_shape2_unnamed_figure_with_preceding_target_emits_anchor(
        self, figure_gate_artifacts
    ):
        """
        D-10 shape 2: a figure with NO `:name:` option, preceded by a
        standalone target, must still emit the propagated target's
        ``metadata(none)`` anchor. No assertion names the docutils
        auto-generated id that becomes ``ids[0]`` here -- its spelling
        depends on how many auto ids the document has already consumed.
        """
        typ_text = figure_gate_artifacts.typ_text
        assert "[#metadata(none) <index:fig-target-noname>]" in typ_text, (
            "The propagated target before the unnamed figure did not emit "
            f"an <index:fig-target-noname> anchor:\n{typ_text}"
        )

    def test_shape3_figure_in_list_item_emits_both_anchors(self, figure_gate_artifacts):
        """
        D-10 shape 3: a `:name:`-carrying figure inside a bullet-list item,
        preceded by a standalone target, must emit BOTH its own self-anchor
        and the propagated target's anchor -- the in-list-item bookkeeping
        must not interfere with either.
        """
        typ_text = figure_gate_artifacts.typ_text
        assert "[#metadata(none) <index:fig-target-li>]" in typ_text, (
            "The propagated target before the list-item figure did not "
            f"emit an <index:fig-target-li> anchor:\n{typ_text}"
        )
        assert " <index:fig-name-li>]" in typ_text, (
            "The list-item figure did not emit its own <index:fig-name-li> "
            f"self-anchor postfix:\n{typ_text}"
        )

    def test_no_duplicate_index_label_definitions(self, figure_gate_artifacts):
        """
        No `index:`-namespaced label is DEFINED twice. A definition is any
        ``<index:name>`` occurrence NOT immediately preceded by ``link(``
        (that pattern is a reference, not a definition) -- this covers both
        the figure self-anchor form (``) <index:name>]``) and the
        ``[#metadata(none) <index:name>]`` propagated-anchor form. A
        duplicate definition would trade the dangling-label fatal for
        Typst's `label ... occurs multiple times` fatal (Phase 25 Critical
        Pitfall 3).
        """
        scan_text = _strip_raw_segments(figure_gate_artifacts.typ_text)
        definitions = re.findall(r"(?<!link\()<(index:[^>]+)>", scan_text)
        counts = Counter(definitions)
        duplicated = {name: n for name, n in counts.items() if n > 1}
        assert (
            not duplicated
        ), f"Label(s) defined more than once: {duplicated}\n{scan_text}"

    def test_no_dangling_same_document_references(self, figure_gate_artifacts):
        """
        Every same-document ``link(<name>, ...)`` reference has a matching
        anchor -- either the ``[#metadata(none) <name>]`` propagated-target
        form or a figure's own ``) <name>]`` self-anchor postfix form. The
        anchor set is the same negative-lookbehind-on-``link(`` scan the
        duplicate-definition test uses, so both anchor forms count. An
        unmatched link name is exactly the dangling label that aborts the
        compile.
        """
        scan_text = _strip_raw_segments(figure_gate_artifacts.typ_text)
        link_names = set(re.findall(r"link\(<([^>]+)>", scan_text))
        anchor_names = set(re.findall(r"(?<!link\()<(index:[^>]+)>", scan_text))
        assert link_names, (
            "Expected at least one same-document link(<name>, ...) "
            f"reference in the emitted output:\n{scan_text}"
        )
        dangling = link_names - anchor_names
        assert not dangling, (
            "Same-document references with no matching anchor (dangling "
            f"labels): {sorted(dangling)}\nanchors present: "
            f"{sorted(anchor_names)}\n{scan_text}"
        )

    def test_wrapper_has_exactly_one_include_of_its_content(
        self, figure_gate_artifacts
    ):
        """
        Phase 47 (R2/R3): the WRAPPER file (this fixture's typst_documents
        target, "master.typ") must contain exactly one #include(, naming
        its own master's content file ("index.typ").
        """
        result = figure_gate_artifacts.result
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        master_typ = figure_gate_artifacts.pdf_path.with_suffix(".typ")
        assert master_typ.exists(), "master.typ was not generated"
        content = master_typ.read_text(encoding="utf-8")
        assert content.count("#include(") == 1, (
            "Expected exactly one #include( in the wrapper -- "
            f"got {content.count('#include(')}:\n{content}"
        )
        assert (
            '#include("index.typ")' in content
        ), 'Expected the wrapper to include("index.typ") (its own content file)'

    def test_pdf_compiles_to_valid_pdf(self, figure_gate_artifacts):
        """
        The emitted ``.typ`` must have compiled to a real, non-empty PDF
        starting with the ``%PDF`` magic bytes -- the only proof the
        document compiled successfully and the dangling-label fatal is
        gone.
        """
        pdf_path = figure_gate_artifacts.pdf_path
        assert pdf_path.exists(), (
            "master.pdf was not produced -- typst.compile() likely aborted "
            f"on a dangling label:\nstderr: {figure_gate_artifacts.result.stderr}"
        )
        assert pdf_path.stat().st_size > 0, "PDF file is empty"
        with open(pdf_path, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
