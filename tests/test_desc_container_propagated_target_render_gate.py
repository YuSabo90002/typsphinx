"""
Fast, offline regression gate for the desc-container propagated-target anchor
fix (Phase 15, GATE-02).

Deterministic, network-free reproduction of the twenty-second fatal the slow
full-corpus gate (``tests/test_corpus_gate.py::TestCorpusRenderGate``) surfaced
against Sphinx's own ``doc/`` tree (``man/sphinx-build.rst``) -- a
missing-anchor (dangling label) fatal on a propagated-target that lands on the
outer ``desc`` CONTAINER of an object-description directive (``.. option::``),
not on ``desc_signature``. After bugs #17-#21 unblocked the earlier label
fatals, ``typst.compile()`` reached the label-resolution pass and aborted
with::

    TypstError: label `<man_u2f_sphinx-build:make-mode>` does not exist in the document

Root cause: an explicit ``.. _make_mode:`` target sits immediately before
``.. option:: -M buildername`` (an object-description directive). docutils'
``PropagateTargets`` transform moves the target's id onto the FOLLOWING body
element -- for an object description, that is the outer ``desc`` node, a
DIFFERENT id than ``desc_signature``'s own id (e.g. ``cmdoption-M``, already
anchored by bug #17). ``visit_desc`` was a no-op and ``depart_desc`` only
appended spacing, so ``node["ids"]`` on the ``desc`` container was never
anchored, while a same-document ``:ref:`` to it renders
``link(<...>, ...)``. The reference therefore dangled.

Fix: ``visit_desc`` now routes ``node["ids"]`` through the shared
``_emit_id_anchors`` helper (bug #20), mirroring its use in
visit_bullet_list/visit_table/visit_block_quote/etc -- emitted BEFORE any
signature/content children are visited. A ``desc`` node with no ids (the
overwhelming common case -- no preceding explicit target) is byte-unchanged.

Confirmed both directions: FAILS against the pre-fix translator with the
exact ``label ... does not exist`` fatal (the link has no anchor to resolve
to), and PASSES with the fix. Also asserts, source-level, that the ``desc``
container emits a ``[#metadata(none) <index:my-opt-target>]`` anchor whose
name equals the ``link(<index:my-opt-target>`` reference, that the control
option (no preceding target) emits no anchor for itself, and that no
same-document ``link(<name>)`` dangles.

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
def desc_container_propagated_target_render_gate_dir():
    """Return the path to the desc-container render-gate fixture project."""
    return (
        Path(__file__).parent
        / "fixtures"
        / "desc_container_propagated_target_render_gate"
    )


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
    reason="typst-py is required for the desc-container propagated-target "
    "anchor render gate",
)
class TestDescContainerPropagatedTargetRenderGate:
    """
    Real-compile regression gate proving a same-document cross-reference to a
    propagated-target that lands on an object-description's outer ``desc``
    container resolves, because ``visit_desc`` now emits a Typst ``<label>``
    anchor for the propagated ``node["ids"]``.

    Requirements: GATE-02 (Phase 15 scope expansion -- the fast offline
    reproduction of the desc-container propagated-target dangling-label
    corpus fatal, #22).
    """

    def test_typstpdf_propagated_desc_container_anchor_resolves_reference(
        self, desc_container_propagated_target_render_gate_dir, temp_build_dir
    ):
        """
        Build the fixture through ``-b typstpdf`` and confirm:

        - the build exits cleanly (no fatal raised out of the subprocess);
        - ``typst.compile()`` did NOT abort with the semantic
          ``label ... does not exist`` fatal (nor any compilation failure);
        - the propagated-target ``desc`` container emits a
          ``[#metadata(none) <index:my-opt-target>]`` anchor;
        - the control option (no preceding target) emits no anchor for
          itself -- byte-unchanged regression control confirming the fix is
          additive, not a behavior change for the common case;
        - EVERY same-document ``link(<name>, ...)`` reference has a matching
          ``[#metadata(none) <name>]`` anchor -- anchor-name == reference-name
          for the same id;
        - ``index.pdf`` exists, is non-empty, and starts with the ``%PDF``
          magic bytes -- the only proof the document compiled to valid Typst
          and the dangling-label fatal is gone.
        """
        result = _run_sphinx_build_typstpdf(
            desc_container_propagated_target_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # A fatal inside TypstPDFBuilder.finish() is logged (not raised) as an
        # ERROR, so guard against the exact signatures explicitly rather than
        # trusting returncode alone.
        assert "does not exist in the document" not in result.stderr, (
            "typst.compile() reported a dangling label -- the desc-container "
            f"propagated-target anchor fix is not in effect:\nstderr: {result.stderr}"
        )
        assert "Typst compilation failed" not in result.stderr, (
            "TypstPDFBuilder.finish() logged a compilation failure:\n"
            f"stderr: {result.stderr}"
        )

        typ_output = temp_build_dir / "index.typ"
        assert typ_output.exists(), "index.typ was not emitted"
        typ_text = typ_output.read_text(encoding="utf-8")

        # The propagated-target desc container must now carry an anchor for
        # its id. Labels are namespaced per source document (bug #21), so the
        # id is emitted as <index:my-opt-target> in this single-doc
        # (docname=index) fixture.
        assert "[#metadata(none) <index:my-opt-target>]" in typ_text, (
            "The desc container did not emit a <index:my-opt-target> anchor "
            f"-- the desc-container propagated-target fix is not applied:\n{typ_text}"
        )

        # anchor-name == reference-name: EVERY same-document link(<name>, ...)
        # (bare-label refid form, distinct from the quoted external link("url"))
        # must have a matching [#metadata(none) <name>] anchor. An unmatched
        # link name is exactly the dangling label that aborts the compile.
        #
        # The fixture's own prose deliberately contains inline-literal
        # snippets like ``link(<my-opt-target>, ...)`` (rendered as raw("...")
        # string literals) to document the emitted form. Those are literal
        # text, NOT real Typst link expressions, so strip raw("...") segments
        # before scanning -- otherwise the un-namespaced snippet names would
        # masquerade as dangling references (a false positive exposed by
        # per-doc namespacing, bug #21).
        scan_text = re.sub(r'raw\("(?:[^"\\]|\\.)*"\)', "", typ_text)
        link_names = set(re.findall(r"link\(<([^>]+)>", scan_text))
        anchor_names = set(re.findall(r"\[#metadata\(none\) <([^>]+)>\]", scan_text))
        assert link_names, (
            "Expected at least one same-document link(<name>, ...) reference in "
            f"the emitted output:\n{typ_text}"
        )
        assert "index:my-opt-target" in link_names, (
            "Expected the propagated-target reference to be emitted as a "
            f"docname-namespaced link(<index:...>) form:\n{typ_text}"
        )
        dangling = link_names - anchor_names
        assert not dangling, (
            "Same-document references with no matching anchor (dangling labels): "
            f"{sorted(dangling)}\nanchors present: {sorted(anchor_names)}\n{typ_text}"
        )

        # Regression control: after stripping prose literals, "my-opt-target"
        # must appear EXACTLY twice -- once as the anchor definition, once as
        # the reference. The control option (--bar, no preceding explicit
        # target) must NOT gain a spurious third occurrence; only its
        # desc_signature's own cmdoption id (bug #17, a different string) is
        # anchored for that option.
        assert scan_text.count("my-opt-target") == 2, (
            "Expected exactly one anchor definition + one reference for "
            f"my-opt-target (got {scan_text.count('my-opt-target')}):\n{typ_text}"
        )

        # The emitted .typ must have compiled to a real, non-empty PDF.
        pdf_output = temp_build_dir / "index.pdf"
        assert pdf_output.exists(), (
            "index.pdf was not produced -- typst.compile() aborted, most likely "
            f"on a dangling label:\nstderr: {result.stderr}"
        )
        assert pdf_output.stat().st_size > 0, "PDF file is empty"
        with open(pdf_output, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"
