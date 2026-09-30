"""
R011: real-``sphinx-build`` subprocess gate binding the published graphviz
prose (``docs/source/user_guide/diagrams.rst``) and the dogfooded diagram on
that same page to a real ``-b typstpdf`` build of typsphinx's OWN docs tree.

Without this module the diagrams page is only a claim. ``TestPublishedGraphvizProse``
reads the page from disk and asserts it states each supported item and each of
the four deliberate exclusions; ``TestDogfoodedDiagramBuild`` builds the real
docs tree and asserts the diagram actually reaches the emitted Typst markup and
the compiled PDF. Prose that drifts from measured behaviour goes red here.

Follows the convention of ``tests/test_output_layout_docs_gate.py``: a real
``sys.executable -m sphinx`` subprocess, ``REPO_ROOT`` from ``parents[1]``, and
NO ``typst-py`` import guard (that module's docstring records why such a guard
misfires in this sandbox -- it tests importability, not compilability).

MEASURED, and the reason this module must NOT be "strengthened" in one specific
direction (D013): the string ``graphviz diagram omitted`` is ALREADY present in
the built docs PDF on a correct, unmodified tree -- pypdf extraction of the
144-page baseline finds it exactly once. It comes from ``visit_graphviz``'s own
docstring, pulled into ``api/index.typ`` by autodoc. Asserting that wording is
ABSENT from the docs PDF or from any docs ``.typ`` therefore fails on a correct
tree. Do not add such an assertion.

MEASURED (locale): Sphinx localises warning message BODIES to the host ``LANG``
but never the severity token itself, so the ``"WARNING"`` substring check below
is locale-robust -- verified by provoking a real warning under a Japanese-locale
shell and observing ``WARNING: 外部の Graphviz ファイル ... [docutils]``.

MEASURED (dependency guard), and why Class 2 skips rather than fails: the
``py312``/``py313``/``cov`` tox lanes provision ``extras = dev``, which does NOT
contain ``myst-parser``, ``sphinx-autodoc-typehints`` or ``furo`` -- those live
in the separate ``docs`` extra. ``docs/source/conf.py`` loads the first two as
Sphinx extensions, so a real docs build under a dev-only environment aborts with
``ExtensionError: Could not import extension sphinx_autodoc_typehints`` and
``rc=2`` before reaching any typsphinx code. Class 2 therefore skips when the
docs extras are absent, so it never reddens for a provisioning reason unrelated
to the feature under test. Class 1 carries no such dependency and runs in EVERY
lane -- it is the always-on, CI-enforced half of this gate.

HTML (D014): this module deliberately asserts NOTHING about the HTML build. Had
it, the only safe assertion would be ``returncode == 0``; a zero-warning
assertion would be wrong, because ``dot command 'dot' cannot be run`` is EXPECTED
on any machine without Graphviz installed -- which is the very contrast the
diagrams page exists to explain. The HTML build additionally needs ``furo`` from
the same absent ``docs`` extra, so it is left to ``tox -e docs-html``.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_SOURCE_DIR = REPO_ROOT / "docs" / "source"
DIAGRAMS_RST_PATH = DOCS_SOURCE_DIR / "user_guide" / "diagrams.rst"
USER_GUIDE_INDEX_RST_PATH = DOCS_SOURCE_DIR / "user_guide" / "index.rst"
DOCS_CONF_PY_PATH = DOCS_SOURCE_DIR / "conf.py"

# The dogfood diagram's sentinels, READ FROM the current on-disk
# diagrams.rst rather than predicted: two node labels and the figure
# caption. Each was verified absent repo-wide before being chosen (T01) and
# each extracts exactly ONCE from the built PDF, so they cannot be satisfied
# by incidental prose elsewhere in the 144-page document. The prose class
# below re-asserts all three against diagrams.rst, which is what keeps these
# constants bound to the page instead of drifting into stale literals.
NODE_LABEL_SENTINELS = ("Vorthaneglim", "Pellucidrane")
CAPTION_SENTINEL = "Thessomantic dogfood pipeline"

# Sphinx extensions the real docs build imports that are NOT in the `dev`
# extra -- see the dependency-guard note in the module docstring.
_DOCS_EXTRA_MODULES = ("myst_parser", "sphinx_autodoc_typehints")


def _docs_extras_available() -> bool:
    """True when every docs-only Sphinx extension the real docs build
    imports is installed in the running interpreter."""
    return all(
        importlib.util.find_spec(name) is not None for name in _DOCS_EXTRA_MODULES
    )


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard. Every gate module in this suite carries its own
    copy of this helper rather than importing a sibling module's.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            builder,
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope="module")
def docs_typstpdf_build(tmp_path_factory):
    """
    Build typsphinx's REAL docs tree once with ``-b typstpdf`` and hand the
    completed process and output directory to every test in Class 2.

    Module-scoped because this is a full 144-page build plus a PDF compile;
    running it per test would multiply the slowest step in this module by
    the number of assertions that read it.
    """
    if not _docs_extras_available():
        pytest.skip(
            "docs extras absent (myst-parser / sphinx-autodoc-typehints): the "
            "real docs build aborts with ExtensionError before reaching any "
            "typsphinx code -- install the `docs` extra to run this class."
        )

    build_dir = tmp_path_factory.mktemp("docs_typstpdf_build")
    result = _run_sphinx_build(DOCS_SOURCE_DIR, build_dir, "typstpdf")
    return result, build_dir


class TestPublishedGraphvizProse:
    """
    R011: the published diagrams page states each supported item and each
    deliberate exclusion.

    No build, no skip, no external dependency -- this class runs in every
    CI lane and fails whenever the page stops making a claim it must make.
    Assertions are semantic (a distinctive lowercase substring per claim),
    not whole-paragraph matches, so ordinary copy-editing does not redden
    them but deleting a claim does.
    """

    @staticmethod
    def _page_text() -> str:
        """
        The page, lowercased with every whitespace run collapsed to a single
        space.

        Collapsing matters: the page is hard-wrapped at ~88 columns, so a
        claim like "still degrades to a bordered placeholder" is split across
        a newline in the source. Asserting against the raw text would make
        these tests fail on a pure re-wrap that changed no words at all --
        exactly the false positive a prose gate must not have.
        """
        return " ".join(DIAGRAMS_RST_PATH.read_text(encoding="utf-8").lower().split())

    def test_page_states_no_system_graphviz_is_needed(self):
        """The page states typsphinx's defining diagram guarantee: no system
        Graphviz and no dot binary are needed for Typst/PDF output."""
        text = self._page_text()
        assert "no system graphviz installation" in text, (
            "diagrams.rst no longer states that no system Graphviz "
            "installation is needed for Typst/PDF output."
        )
        assert "binary are needed for typst or pdf output" in text, (
            "diagrams.rst no longer states that no ``dot`` binary is needed "
            "for Typst or PDF output."
        )
        assert "@preview/diagraph" in text, (
            "diagrams.rst no longer names the @preview/diagraph package that "
            "carries Graphviz compiled to WebAssembly."
        )

    def test_page_names_the_three_supported_directives(self):
        """The page names all three Sphinx graphviz directives as supported
        in their inline form."""
        text = self._page_text()
        for directive in (".. graphviz::", ".. digraph::", ".. graph::"):
            assert directive in text, (
                f"diagrams.rst no longer names the supported directive "
                f"{directive!r}."
            )
        assert "inline" in text, (
            "diagrams.rst no longer states that the DOT source must be "
            "written inline in the directive body."
        )

    def test_page_documents_the_supported_options(self):
        """The page documents the directive options that DO reach Typst
        output: :caption:, :name:, :layout:/:graphviz_dot: and :alt:."""
        text = self._page_text()
        for option in (":caption:", ":name:", ":layout:", ":graphviz_dot:", ":alt:"):
            assert option in text, (
                f"diagrams.rst no longer documents the supported option " f"{option!r}."
            )

    def test_page_states_align_is_discarded(self):
        """Exclusion 1: :align: is discarded silently, with no warning."""
        text = self._page_text()
        assert ":align:" in text, "diagrams.rst no longer mentions :align:."
        assert "is discarded silently, with no warning" in text, (
            "diagrams.rst no longer states that :align: is discarded "
            "silently and without a warning."
        )

    def test_page_states_external_dot_files_are_unsupported(self):
        """Exclusion 2: external .dot files are not supported -- the diagram
        degrades to a placeholder and the build warns."""
        text = self._page_text()
        assert (
            "only the inline form renders" in text
        ), "diagrams.rst no longer states that only the inline form renders."
        assert "only inline dot is supported" in text, (
            "diagrams.rst no longer quotes the build's own warning that only "
            "inline DOT is supported."
        )
        assert (
            ".dot" in text
        ), "diagrams.rst no longer names external ``.dot`` files at all."

    def test_page_states_inheritance_diagram_still_degrades(self):
        """Exclusion 3: .. inheritance-diagram:: is not routed through
        diagraph and still degrades to a bordered placeholder."""
        text = self._page_text()
        assert (
            "inheritance-diagram" in text
        ), "diagrams.rst no longer mentions .. inheritance-diagram::."
        assert "routed through diagraph" in text, (
            "diagrams.rst no longer states that inheritance-diagram is NOT "
            "routed through diagraph."
        )
        assert "still degrades to a bordered placeholder" in text, (
            "diagrams.rst no longer states that inheritance-diagram still "
            "degrades to a bordered placeholder."
        )

    def test_page_states_malformed_dot_fails_the_build(self):
        """Exclusion 4: malformed DOT hard-fails the PDF build, carrying
        Graphviz's own diagnostic (the MEASURED D012/R006 behaviour -- the
        page must not claim the build succeeds or that an in-page error
        block appears)."""
        text = self._page_text()
        assert "diagraph error: syntax error in line 2 near" in text, (
            "diagrams.rst no longer quotes Graphviz's own verbatim "
            "`Diagraph error: syntax error` diagnostic."
        )
        assert "fails the whole pdf build" in text, (
            "diagrams.rst no longer states that malformed DOT fails the "
            "whole PDF build rather than degrading in-page."
        )

    def test_page_states_html_remains_sphinx_ext_graphviz_job(self):
        """The page states HTML output remains sphinx.ext.graphviz's job and
        DOES require a real dot binary -- the contrast the page exists for."""
        text = self._page_text()
        assert "html output remains ``sphinx.ext.graphviz``'s responsibility" in text, (
            "diagrams.rst no longer states that HTML output remains "
            "sphinx.ext.graphviz's responsibility."
        )
        assert "require a real ``dot`` binary on the build machine" in text, (
            "diagrams.rst no longer states that the HTML side requires a "
            "real dot binary on the build machine."
        )
        assert "dot command 'dot' cannot be run" in text, (
            "diagrams.rst no longer quotes the HTML build's own "
            "missing-Graphviz log line."
        )

    def test_page_carries_the_dogfood_diagram_sentinels(self):
        """
        The dogfood diagram itself is still on the page, with the exact node
        labels and caption the PDF-extraction assertions below look for.

        This is what binds this module's sentinel constants to the page: if
        the diagram is edited or removed, this test names the drift directly
        instead of leaving the build-class failure to be diagnosed blind.
        """
        raw = DIAGRAMS_RST_PATH.read_text(encoding="utf-8")
        assert ".. graphviz::" in raw, (
            "diagrams.rst no longer contains a .. graphviz:: directive -- the "
            "dogfooded diagram is gone."
        )
        assert f":caption: {CAPTION_SENTINEL}" in raw, (
            f"diagrams.rst no longer carries the dogfood diagram's caption "
            f"{CAPTION_SENTINEL!r}."
        )
        for sentinel in NODE_LABEL_SENTINELS:
            assert sentinel in raw, (
                f"diagrams.rst no longer carries the dogfood diagram's node "
                f"label {sentinel!r}."
            )

    def test_user_guide_index_references_the_diagrams_page_twice(self):
        """
        docs/source/user_guide/index.rst wires the diagrams page in BOTH
        places a user-guide page must appear: the toctree (as a bare
        indented docname line) and the "Main Topics" :doc: list. Asserted as
        two DISTINCT occurrences, so wiring it into only one place is red.
        """
        text = USER_GUIDE_INDEX_RST_PATH.read_text(encoding="utf-8")
        assert "\n   diagrams\n" in text, (
            "docs/source/user_guide/index.rst does not list `diagrams` as a "
            "bare indented toctree entry."
        )
        assert ":doc:`diagrams`" in text, (
            "docs/source/user_guide/index.rst does not reference "
            "``:doc:`diagrams``` in its Main Topics list."
        )

    def test_docs_conf_enables_sphinx_ext_graphviz(self):
        """docs/source/conf.py enables sphinx.ext.graphviz -- without it the
        directives are not recognised at all and the dogfood diagram would
        never reach the builder."""
        text = DOCS_CONF_PY_PATH.read_text(encoding="utf-8")
        assert '"sphinx.ext.graphviz"' in text, (
            "docs/source/conf.py no longer lists 'sphinx.ext.graphviz' in "
            "its extensions."
        )


class TestDogfoodedDiagramBuild:
    """
    R011: a real ``-b typstpdf`` build of typsphinx's OWN docs tree, proving
    the dogfooded diagram survives the whole pipeline end to end -- doctree
    to Typst markup to compiled PDF.

    Skips (never fails) when the docs extras are absent; see the module
    docstring for the measurement behind that choice.
    """

    def test_docs_build_succeeds_with_no_warnings(self, docs_typstpdf_build):
        """
        The real docs build exits 0 and emits NO warnings.

        MEASURED baseline: the docs build is rc=0 with ZERO warnings both
        before and after the dogfood diagram was added, so a zero-warning
        assertion is safe here -- unlike the HTML build, which legitimately
        warns about the missing dot binary (see the module docstring).
        """
        result, _ = docs_typstpdf_build
        assert result.returncode == 0, (
            f"Expected the real docs typstpdf build to succeed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        combined_output = result.stdout + result.stderr
        assert "WARNING" not in combined_output, (
            f"Expected ZERO warnings from the real docs typstpdf build:\n"
            f"{combined_output}"
        )

    def test_diagrams_content_typ_carries_exactly_one_rendered_diagram(
        self, docs_typstpdf_build
    ):
        """
        The emitted CONTENT file ``user_guide/diagrams.typ`` carries exactly
        ONE ``render(`` call and imports ``@preview/diagraph``.

        Asserted on the CONTENT file, NOT on the ``typsphinx.typ`` wrapper:
        the wrapper holds only the template application and ``#include()``s
        of the per-docname content files, so the diagram markup is never in
        it. Counting (rather than merely testing membership) is what makes a
        duplicated or dropped diagram red -- the page documents several
        diagrams in ``code-block`` examples that must NOT render.
        """
        _, build_dir = docs_typstpdf_build
        content_typ = build_dir / "user_guide" / "diagrams.typ"
        assert (
            content_typ.exists()
        ), f"Expected the content file user_guide/diagrams.typ under {build_dir}."

        text = content_typ.read_text(encoding="utf-8")
        assert text.count("render(") == 1, (
            f"Expected EXACTLY one render( call in user_guide/diagrams.typ, "
            f"found {text.count('render(')} -- the page's code-block examples "
            f"must not render, and the dogfood diagram must."
        )
        assert (
            "@preview/diagraph" in text
        ), "Expected the @preview/diagraph import in user_guide/diagrams.typ."

    def test_built_pdf_contains_the_dogfood_diagram_sentinels(
        self, docs_typstpdf_build
    ):
        """
        The compiled ``typsphinx.pdf`` contains both dogfood node labels AND
        the figure caption -- the end-to-end proof that the diagram is a real
        vector drawing in the published PDF, not merely markup that compiled.

        The node labels prove the DOT graph itself was rendered by diagraph;
        the caption proves the surrounding Typst figure was built too.
        """
        _, build_dir = docs_typstpdf_build
        pdf_path = build_dir / "typsphinx.pdf"
        assert pdf_path.exists(), f"Expected the compiled PDF at {pdf_path}."

        from pypdf import PdfReader

        reader = PdfReader(str(pdf_path))
        pdf_text = "\n".join((page.extract_text() or "") for page in reader.pages)

        for sentinel in NODE_LABEL_SENTINELS:
            assert sentinel in pdf_text, (
                f"Expected the dogfood diagram's node label {sentinel!r} in "
                f"the built PDF -- the graph did not render."
            )
        assert CAPTION_SENTINEL in pdf_text, (
            f"Expected the dogfood diagram's caption {CAPTION_SENTINEL!r} in "
            f"the built PDF -- the figure caption did not render."
        )
