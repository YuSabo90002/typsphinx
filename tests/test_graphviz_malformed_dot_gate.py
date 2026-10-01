"""
S04 boundary gate: malformed DOT, pinned to MEASURED behaviour (D012).

**Read this before "fixing" any assertion below.** This module deliberately
contradicts the literal text of R006 and D002. Both state that malformed DOT
leaves the build succeeding and that diagraph renders Graphviz's error into
the compiled PDF as a red-highlighted raw block. That is factually false,
and was re-measured false on 2026-09-30: every malformed shape hard-fails
``typst.compile()``, and an end-to-end ``sphinx-build -b typstpdf`` exits
rc 2 producing zero PDFs.

The mechanism, confirmed in diagraph 0.3.7's own source: ``internals.typ``
calls ``plugin.get_labels(...)`` FIRST with **no status guard**, so a DOT
syntax error aborts the compile during the label-measurement pass. The
red-block recovery later in that file is guarded by ``output.at(0) != 0`` on
the SUBSEQUENT ``plugin.render(...)`` call, and is therefore unreachable for
syntax errors. D002 read real code, but the wrong call site.

**D012 is the governing decision: gate the measured behaviour, and change no
typsphinx source.** Accordingly this module asserts no red-highlighted
recovery block and no succeeding PDF build, because neither can ever go green. It also adds no
DOT pre-validation to typsphinx, which could not parse DOT without the
Graphviz binary whose absence is this milestone's entire point.

What is pinned instead splits into two halves that deliberately do not share
a fixture -- the first must succeed and the second must raise:

* **Half A -- translation is clean.** ``sphinx-build -b typst`` exits 0 and
  the emitted CONTENT file ``index.typ`` carries exactly one ``render("``
  call. typsphinx's own layer behaves correctly; the defect lives strictly
  downstream, in diagraph.
* **Half B -- the compile hard-fails, carrying Graphviz's own diagnostic.**
  ``typst.compile()`` raises, and the exception text contains BOTH
  ``"Diagraph error"`` and ``"syntax error"``. Both substrings matter: a bare
  ``pytest.raises`` would pass if the compile failed for some unrelated
  reason -- a missing package, a bad import, a template error -- which would
  make this gate worthless. Asserting Graphviz's own wording is what proves
  the user still receives a diagnostic naming the real cause, which is
  D002's surviving *intent* even though its stated mechanism is wrong.

**If this module goes red at Half B, do not reword it toward D002.** The
expected cause is upstream: should diagraph ever add a status guard to its
``get_labels`` call, the red-block recovery becomes reachable, the compile
stops failing, and this gate correctly goes red to demand re-measurement.
The honest response then is to measure the new behaviour and re-pin it --
never to assume the red block D002 described has appeared.

**Fixture disjointness (MEM023).** ``tests/fixtures/graphviz_malformed_dot_gate/``
is its own Sphinx project rather than a case added to
``tests/fixtures/graphviz_render_gate/``, whose gate asserts a build that
compiles cleanly to a PDF; a compile-breaking diagram inside it would turn
that gate red.

**Where the emitted calls live.** ``render()`` calls land in the
docname-derived CONTENT file ``index.typ``, never in the ``master.typ``
wrapper, which carries only the template call and an ``#include()``. Half
A's count assertion therefore reads ``index.typ``; made against
``master.typ`` it would be unsatisfiable. The compile in Half B, conversely,
must run against ``master.typ`` -- the wrapper is the document with the
template and the imports.

pypdf is deliberately not used or required anywhere here: there is no PDF to
read, and that absence is itself the finding.
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


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "graphviz_malformed_dot_gate"

# The two substrings asserted present in the compile failure. "Diagraph
# error" is diagraph's own prefix, proving the failure came from the plugin
# and not from Typst generally; "syntax error" is Graphviz's own wording for
# the invalid DOT, proving the diagnostic names the real cause. Measured
# together on 2026-09-30 as: "plugin errored with: Diagraph error: syntax
# error in line 2 near ';'".
DIAGRAPH_ERROR_MARKER = "Diagraph error"
GRAPHVIZ_SYNTAX_MARKER = "syntax error"


@pytest.fixture(scope="module")
def malformed_dot_typst_build(tmp_path_factory):
    """
    Run ``sphinx-build -b typst`` on the malformed-DOT fixture ONCE.

    Half A asserts against this; Half B reuses only the ``master_typ`` path
    from it and performs its own compile inside the test body. The compile is
    NOT done here on purpose: a raise at fixture level would ERROR the module
    rather than satisfy an assertion, which would report the expected failure
    as a broken test run.

    Depends only on ``tmp_path_factory``, which is module-scope-compatible,
    to avoid a pytest ScopeMismatch. Note the typst builder is used, not
    typstpdf: this build must be allowed to succeed so that Half A's claim --
    that translation is clean -- is separable from the downstream compile
    failure. Under ``-b typstpdf`` the compile runs inside sphinx-build and
    the two findings collapse into one opaque rc 2.
    """
    build_dir = tmp_path_factory.mktemp("graphviz_malformed_dot_gate") / "_build"

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
            str(FIXTURE_DIR),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )

    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "build_dir": build_dir,
        "master_typ": build_dir / "master.typ",
        "content_typ": build_dir / "index.typ",
    }


@pytest.mark.slow
@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the S04 malformed-DOT gate",
)
class TestMalformedDotTranslationIsClean:
    """Half A (R006): typsphinx's own layer is not at fault."""

    def test_malformed_dot_translation_succeeds(self, malformed_dot_typst_build):
        """
        Broken DOT does not break TRANSLATION.

        typsphinx never inspects the DOT body, so a syntax error inside it is
        invisible at this layer -- and must stay invisible. A non-zero rc here
        would mean typsphinx grew DOT validation it cannot honestly perform
        without the Graphviz binary this milestone exists to avoid (D012).
        """
        result = malformed_dot_typst_build
        assert result["returncode"] == 0, (
            "sphinx-build -b typst must still exit 0 on malformed DOT: the "
            "translator passes the body through untouched, so the defect "
            "belongs downstream in diagraph, not here.\n"
            f"stdout: {result['stdout']}\nstderr: {result['stderr']}"
        )

    def test_malformed_dot_emits_exactly_one_render_call(
        self, malformed_dot_typst_build
    ):
        """
        The sole diagram produced exactly one diagraph call, broken body and
        all.

        Read against the docname-derived CONTENT file, where render() calls
        land -- not against the master.typ wrapper, which never carries them.
        Exactly one, matching the fixture's single directive: zero would mean
        the diagram was silently dropped instead of emitted, and more than one
        would mean the fixture gained a second diagram, making it ambiguous
        which one aborts the compile in Half B.
        """
        result = malformed_dot_typst_build
        assert result["content_typ"].exists(), (
            "index.typ was not generated -- sphinx-build did not get far "
            f"enough for this gate to assert anything:\n"
            f"stdout: {result['stdout']}\nstderr: {result['stderr']}"
        )
        source = result["content_typ"].read_text(encoding="utf-8")
        assert source.count('render("') == 1, (
            "Expected exactly one diagraph render() call for the fixture's "
            "single malformed diagram -- zero means the body was silently "
            "dropped rather than passed through, more than one means the "
            f"fixture gained a second diagram:\n{source}"
        )


@pytest.mark.slow
@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the S04 malformed-DOT gate",
)
class TestMalformedDotCompileFailsWithGraphvizDiagnostic:
    """Half B (D012): the compile hard-fails, naming the real cause."""

    def test_malformed_dot_compile_raises_with_graphviz_diagnostic(
        self, malformed_dot_typst_build
    ):
        """
        ``typst.compile()`` raises, and its text carries Graphviz's own words.

        The compile runs here in the test body rather than in the fixture so
        that the expected raise is an ASSERTED outcome, not a module-level
        ERROR. Both substrings are required: the raise alone would pass on any
        unrelated compile failure (missing package, bad import, template
        error), making the gate worthless, so the wording is what proves the
        user still gets a diagnostic pointing at the invalid DOT.
        """
        result = malformed_dot_typst_build
        master_typ = result["master_typ"]
        assert master_typ.exists(), (
            "master.typ was not generated -- sphinx-build did not get far "
            f"enough for this gate to assert anything:\n"
            f"stdout: {result['stdout']}\nstderr: {result['stderr']}"
        )

        # Compile the WRAPPER (master.typ), not the docname-derived content
        # file: the wrapper is the document carrying the template and the
        # @preview imports diagraph's render() call depends on.
        output_pdf = result["build_dir"] / "master.pdf"
        with pytest.raises(Exception) as excinfo:
            typst.compile(str(master_typ), output=str(output_pdf))

        message = str(excinfo.value)
        assert DIAGRAPH_ERROR_MARKER in message, (
            f"The compile failure must carry {DIAGRAPH_ERROR_MARKER!r}, "
            "proving it came from the diagraph plugin rather than from some "
            "unrelated Typst problem (a missing package, a bad import, a "
            f"template error) that would make this gate worthless:\n{message}"
        )
        assert GRAPHVIZ_SYNTAX_MARKER in message, (
            f"The compile failure must carry Graphviz's own "
            f"{GRAPHVIZ_SYNTAX_MARKER!r} wording, which is what proves the "
            "user still receives a diagnostic naming the REAL cause -- D002's "
            "surviving intent, even though its stated red-block mechanism is "
            f"unreachable (see this module's docstring, D012):\n{message}"
        )

    def test_malformed_dot_produces_no_pdf(self, malformed_dot_typst_build):
        """
        No PDF survives the failed compile.

        This is the finding that falsifies D002's literal text: there is no
        artifact in which any such recovery block could be shown to a reader.
        Asserted separately so the absence is a named, standing claim rather
        than an incidental side effect of the raise above.
        """
        result = malformed_dot_typst_build
        output_pdf = result["build_dir"] / "malformed_no_pdf_probe.pdf"
        with pytest.raises(Exception):
            typst.compile(str(result["master_typ"]), output=str(output_pdf))

        assert not output_pdf.exists(), (
            "The failed compile left a PDF behind. If diagraph ever gains a "
            "status guard on its get_labels call, the compile stops failing "
            "and a real artifact appears -- at which point this gate must be "
            "RE-MEASURED, not reworded toward D002 (see module docstring)."
        )
