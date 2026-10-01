"""
S04 boundary gate: the external ``.dot`` file form refuses, and stays refused.

R007 scopes the external-file directive form -- ``.. graphviz:: some.dot`` --
OUT of this milestone. S02 deliberately kept ``visit_graphviz``'s
``filename`` branch routing to ``_visit_graphical_placeholder`` (D-005 /
D009) precisely so this slice could pin the refusal as an asserted outcome,
rather than let the scoped-out form start working by accident.

The subtlety worth stating: by the time ``visit_graphviz`` runs, Sphinx has
ALREADY read the external file into ``node['code']``. Nothing about the
external form is inherently un-renderable -- deleting the ``filename``
branch would silently widen the supported surface, and the DOT would render.
That is the regression this module exists to name. Its failure message says
so: a red gate here means the scoped-out form started working.

The proof runs against ``tests/fixtures/graphviz_external_dot_gate/`` through
the full pipeline::

    sphinx-build -b typst  ->  typst.compile()  ->  pypdf text-extraction

and asserts, of one real compiled artifact, that:

1. the refusal does not break the build (``returncode == 0``);
2. it logs EXACTLY one warning, in R007's wording;
3. no ``render("`` call was emitted at all, i.e. the refusal actually fired;
4. the bordered placeholder is visibly present in the compiled PDF;
5. neither quoted label sentinel from the ``.dot`` file leaks into that PDF
   -- the positive proof that Sphinx's already-read ``node['code']`` went
   nowhere.

**Fixture disjointness (MEM023).** This is its own Sphinx project rather
than a case added to ``tests/fixtures/graphviz_render_gate/``. That gate
asserts a clean build with ZERO degrade warnings; an intentionally-refusing
directive inside it would turn it red.

**Where the emitted calls live.** ``render()`` calls land in the
docname-derived CONTENT file ``index.typ``, never in the ``master.typ``
wrapper -- which carries only the template call and an ``#include()``. The
assertion in (3) therefore reads ``content_source``; the same assertion made
against ``master.typ`` would be unsatisfiable and would pass vacuously.

The build and compile are done ONCE per module via a module-scoped fixture,
mirroring ``tests/test_graphviz_render_gate.py``. A consequence (MEM011): an
import or emission regression surfaces here as a fixture-level ERROR, not as
a targeted assertion failure -- read the fixture's error, not the test
names, when this module goes red.
"""

import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


# R007's exact warning wording, as emitted by
# typsphinx/translator.py::_visit_graphical_placeholder for the "graphviz"
# node label. Asserted with .count(...) == 1 -- the same idiom as
# tests/test_pdf_render_gate.py's inheritance-diagram degrade gate -- so a
# second, duplicated warning is a failure rather than a silent pass.
PLACEHOLDER_WARNING = "graphviz is not supported in Typst output"

# The placeholder's rendered wording, asserted PRESENT in the PDF.
PLACEHOLDER_WORDING = "omitted"

# The two quoted label sentinels carried by
# tests/fixtures/graphviz_external_dot_gate/external.dot, asserted ABSENT
# from the extracted PDF text. Both are quoted DOT labels, never bare node
# identifiers: diagraph renders unquoted identifiers through Typst MATH
# mode, so an assertion on a bare identifier is invalid even when it passes
# (MEM008). Neither string is named anywhere in the fixture's visible prose
# -- index.rst's scope note is an rST comment for exactly that reason
# (MEM022), since otherwise the fixture would satisfy these absence
# assertions on its own words.
LEAK_SENTINEL = "Wexlorbprime"
SECOND_LEAK_SENTINEL = "Jontarbsecond"


@pytest.fixture(scope="module")
def graphviz_external_dot_gate_build(tmp_path_factory):
    """
    Build + real-compile the external-.dot gate fixture ONCE per module.

    Returns a dict with sphinx-build's captured streams, the emitted content
    file's source, and the pypdf-extracted PDF text, so each test below
    asserts a disjoint slice of the SAME real artifact. Depends only on
    ``tmp_path_factory``, which is module-scope-compatible, to avoid a
    pytest ScopeMismatch.

    Deliberately does NOT assert ``returncode == 0`` itself: that claim is
    R007's own first acceptance condition and gets its own named test below,
    so a broken build reports as a targeted failure rather than only as a
    fixture error.
    """
    source_dir = Path(__file__).parent / "fixtures" / "graphviz_external_dot_gate"
    build_dir = tmp_path_factory.mktemp("graphviz_external_dot_gate") / "_build"

    # Invoked as `sys.executable -m sphinx` rather than `uv run
    # sphinx-build`: this reuses the exact interpreter/venv already running
    # this test and depends on no PATH resolution at all.
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typst",
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )

    master_typ = build_dir / "master.typ"
    assert master_typ.exists(), (
        "master.typ was not generated -- sphinx-build did not get far enough "
        f"for this gate to assert anything:\nstdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )

    # Compile the WRAPPER (master.typ), not the docname-derived content file
    # (index.typ), and do it WITHOUT try/except: a fatal must abort the
    # whole module loudly rather than be swallowed into a soft assertion.
    pdf_output = build_dir / "master.pdf"
    typst.compile(str(master_typ), output=str(pdf_output))

    assert pdf_output.exists(), "PDF file was not created"
    assert pdf_output.stat().st_size > 0, "PDF file is empty"

    reader = pypdf.PdfReader(str(pdf_output))
    return {
        "returncode": result.returncode,
        "stderr": result.stderr,
        "content_source": (build_dir / "index.typ").read_text(encoding="utf-8"),
        "pdf_text": "\n".join(page.extract_text() for page in reader.pages),
    }


@pytest.mark.slow
@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are both required for the S04 external-.dot gate",
)
class TestGraphvizExternalDotGate:
    """Real-compile boundary gate for the scoped-out external-.dot form (R007)."""

    def test_external_dot_build_succeeds(self, graphviz_external_dot_gate_build):
        """The refusal degrades gracefully -- it does not break the build."""
        result = graphviz_external_dot_gate_build
        assert result["returncode"] == 0, (
            "A scoped-out external-.dot directive must degrade gracefully, not "
            f"fail the build:\nstderr: {result['stderr']}"
        )

    def test_external_dot_logs_exactly_one_warning(
        self, graphviz_external_dot_gate_build
    ):
        """The refusal is announced exactly once, in R007's wording."""
        result = graphviz_external_dot_gate_build
        assert result["stderr"].count(PLACEHOLDER_WARNING) == 1, (
            f"Expected exactly one {PLACEHOLDER_WARNING!r} warning for the sole "
            "external-.dot directive -- zero means the refusal stopped firing "
            "and the scoped-out form is now silently supported; more than one "
            f"means the degrade path runs twice:\n{result['stderr']}"
        )

    def test_external_dot_emits_no_render_call(self, graphviz_external_dot_gate_build):
        """
        The refusal actually fired: no diagraph call was emitted at all.

        Read against the docname-derived CONTENT file, where render() calls
        land -- not against the master.typ wrapper, which never carries them.
        """
        result = graphviz_external_dot_gate_build
        assert 'render("' not in result["content_source"], (
            "R007 scopes external .dot files OUT, but a diagraph render() call "
            "was emitted -- the supported surface has silently widened, most "
            "likely because visit_graphviz's `filename` branch was removed:\n"
            f"{result['content_source']}"
        )

    def test_external_dot_placeholder_is_visible_in_pdf(
        self, graphviz_external_dot_gate_build
    ):
        """The reader sees a visible trace of the refusal, not a silent gap."""
        result = graphviz_external_dot_gate_build
        assert PLACEHOLDER_WORDING in result["pdf_text"], (
            "The degrade placeholder must be reader-visible in the compiled PDF "
            "(D-01) -- a refused directive that leaves no trace is worse than "
            f"one that renders:\n{result['pdf_text']}"
        )

    def test_external_dot_source_does_not_leak_into_pdf(
        self, graphviz_external_dot_gate_build
    ):
        """
        Sphinx's already-read ``node['code']`` went nowhere.

        This is the assertion that catches a future regression deleting the
        ``filename`` branch: Sphinx has already loaded external.dot into the
        node by the time the visitor runs, so its labels would render as a
        real diagram the moment the refusal stops firing.
        """
        result = graphviz_external_dot_gate_build
        for sentinel in (LEAK_SENTINEL, SECOND_LEAK_SENTINEL):
            assert sentinel not in result["pdf_text"], (
                f"The external .dot file's label {sentinel!r} reached the "
                "compiled PDF. R007 scopes this form OUT, so the file's "
                "contents must not be rendered -- Sphinx pre-reads it into "
                "node['code'], so this leaks the moment visit_graphviz's "
                f"`filename` refusal is removed:\n{result['pdf_text']}"
            )
