"""
Fast, offline regression gate for the rubric propagated-target anchor fix and
the broader missing-anchor sweep (Phase 15, GATE-02).

Deterministic, network-free reproduction of the twenty-third fatal the slow
full-corpus gate (``tests/test_corpus_gate.py::TestCorpusRenderGate``) surfaced
against Sphinx's own ``doc/`` tree (``man/sphinx-build.rst``) -- a
missing-anchor (dangling label) fatal on a propagated target that lands on a
``rubric`` node. After bugs #17-#22 unblocked the earlier label fatals,
``typst.compile()`` reached the label-resolution pass and aborted with::

    TypstError: label `<man_u2f_sphinx-build:makefile-options>` does not exist in the document

Root cause: an explicit ``.. _makefile_options:`` target sits immediately
before ``.. rubric:: Makefile Options``. docutils' ``PropagateTargets``
transform moves the target's id onto the FOLLOWING body element -- for a
rubric, the ``rubric`` node itself. ``visit_rubric`` rendered a bold heading
via a dummy ``strong`` node but never read ``node["ids"]``, so no anchor was
emitted, while a cross-document-safe ``:ref:`` to it renders
``link(<...>, ...)``. The reference therefore dangled.

Fix: ``visit_rubric`` now routes ``node["ids"]`` through the shared
``_emit_id_anchors`` helper (bug #20), and the same helper was swept across the
rest of the body/container visitors that could carry a propagated (or own
``:name:``/``:label:``) id but emitted no anchor -- or a BROKEN one:

- ``visit_container`` (generic container + the outer ``literal-block-wrapper``
  of a captioned ``:name:`` code block), guarded on ``names`` so the auto id a
  captioned block always carries stays byte-unchanged;
- ``visit_compound``, ``visit_glossary``, ``visit_transition``, and the
  box-less ``contents`` ``topic`` branch;
- ``depart_figure`` -- anchors the PROPAGATED ``ids[1:]`` while skipping the
  figure's own self-anchored ``ids[0]`` (no double-define);
- ``visit_literal_block`` and ``visit_math_block`` -- REPLACE a broken bare
  ` <label>` postfix (which aborted the compile with "cannot join content with
  label" / "expected semicolon or line break", and anchored the name rather
  than the id) with the clean, joinable ``[#metadata(none) <id>]`` form.

This gate exercises the rubric fatal plus the figure/captioned-block/plain-
block/labeled-equation cases in one build. It FAILS against the pre-fix
translator (dangling / non-joining labels) and PASSES with the fix; it asserts,
source-level, that the ``rubric`` emits a ``[#metadata(none) <index:...>]``
anchor whose name equals its ``link(<index:...>`` reference, that the control
rubric (no preceding target) adds no spurious anchor, and that NO same-document
reference dangles.

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
def rubric_propagated_target_render_gate_dir():
    """Return the path to the rubric propagated-target render-gate fixture."""
    return Path(__file__).parent / "fixtures" / "rubric_propagated_target_render_gate"


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


def _label_definitions(text: str) -> set[str]:
    """
    Collect every Typst label DEFINITION name in the emitted ``.typ``.

    Labels are defined in this translator by several forms, all captured here:

    - ``[#metadata(none) <name>]`` -- the zero-width anchor helper;
    - ``<name>]`` -- the postfix form on headings (``[#heading(...) <name>]``)
      and figures (``) <name>]``);
    - ``#label("name")`` -- the reference-with-adjacent-target markup path.
    """
    return set(re.findall(r"<([^>]+)>\]", text)) | set(
        re.findall(r'#label\("([^"]+)"\)', text)
    )


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the rubric propagated-target anchor render gate",
)
class TestRubricPropagatedTargetRenderGate:
    """
    Real-compile regression gate proving a same-document cross-reference to a
    propagated target that lands on a ``rubric`` (and the swept
    figure/container/literal_block/math_block cases) resolves, because the
    translator now emits a Typst ``<label>`` anchor for the propagated/own
    ``node["ids"]``.

    Requirements: GATE-02 (Phase 15 -- the fast offline reproduction of the
    rubric propagated-target dangling-label corpus fatal, #23, plus the
    missing-anchor sweep it shipped with).
    """

    def test_typstpdf_propagated_rubric_and_sweep_anchors_resolve(
        self, rubric_propagated_target_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly (no fatal raised out of the subprocess);
        - ``typst.compile()`` did NOT abort with the semantic
          ``label ... does not exist`` fatal, the ``cannot join content with
          label`` fatal (the old literal_block postfix), or the
          ``expected semicolon or line break`` fatal (the old math postfix);
        - the propagated-target ``rubric`` emits a
          ``[#metadata(none) <index:my-rubric-target>]`` anchor;
        - the control rubric (no preceding target) adds no spurious anchor --
          ``my-rubric-target`` appears exactly twice (one anchor, one ref);
        - EVERY same-document ``link(<name>, ...)`` reference has a matching
          label definition -- anchor-name == reference-name -- so nothing
          dangles;
        - ``index.pdf`` exists, is non-empty, and starts with ``%PDF``.
        """
        result = _run_sphinx_build_typstpdf(
            rubric_propagated_target_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # A fatal inside TypstPDFBuilder.finish() is logged (not raised) as an
        # ERROR, so guard against the exact signatures explicitly rather than
        # trusting returncode alone.
        for fatal in (
            "does not exist in the document",
            "cannot join content with label",
            "expected semicolon or line break",
        ):
            assert fatal not in result.stderr, (
                f"typst.compile() reported '{fatal}' -- the missing-anchor "
                f"sweep is not fully in effect:\nstderr: {result.stderr}"
            )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # The propagated-target rubric must now carry an anchor for its id.
        # Labels are namespaced per source document (bug #21); this single-doc
        # (docname=index) fixture emits <index:my-rubric-target>.
        assert "[#metadata(none) <index:my-rubric-target>]" in typ_text, (
            "The rubric did not emit a <index:my-rubric-target> anchor -- the "
            f"rubric propagated-target fix is not applied:\n{typ_text}"
        )

        # Strip inline-literal prose (raw("...")) before scanning so any
        # documentation snippet that mentions link(<...>) / <...> cannot
        # masquerade as a real reference/anchor (a false positive exposed by
        # per-doc namespacing, bug #21).
        scan_text = re.sub(r'raw\("(?:[^"\\]|\\.)*"\)', "", typ_text)

        link_names = set(re.findall(r"link\(<([^>]+)>", scan_text))
        anchor_names = _label_definitions(scan_text)
        assert link_names, (
            "Expected at least one same-document link(<name>, ...) reference "
            f"in the emitted output:\n{typ_text}"
        )
        # Every reference exercised by the fixture must be present and resolve.
        for expected in (
            "index:my-rubric-target",
            "index:my-fig-target",
            "index:captioned-block",
            "index:my-code-target",
            "index:equation-euler-eq",
            "index:my-list-target",
        ):
            assert (
                expected in link_names
            ), f"Expected a same-document link(<{expected}>) reference:\n{typ_text}"
        dangling = link_names - anchor_names
        assert not dangling, (
            "Same-document references with no matching anchor (dangling "
            f"labels): {sorted(dangling)}\ndefined: {sorted(anchor_names)}\n"
            f"{typ_text}"
        )

        # Regression control: after stripping prose literals, "my-rubric-target"
        # must appear EXACTLY twice -- once as the anchor definition, once as
        # the reference. The control rubric ("Plain Rubric", no preceding
        # target) must NOT gain a spurious third occurrence.
        assert scan_text.count("my-rubric-target") == 2, (
            "Expected exactly one anchor definition + one reference for "
            f"my-rubric-target (got {scan_text.count('my-rubric-target')}):\n"
            f"{typ_text}"
        )
        # The control rubric still renders (its heading text is present).
        assert "Plain Rubric" in typ_text, "Control rubric was not rendered"

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most "
            f"likely on a dangling/non-joining label:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
