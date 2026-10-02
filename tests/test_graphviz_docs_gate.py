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
Sphinx extensions and names ``furo`` as its HTML theme, so a real docs build
under a dev-only environment aborts with ``ExtensionError: Could not import
extension sphinx_autodoc_typehints`` and ``rc=2`` before reaching any typsphinx
code. Both build classes below therefore skip when the docs extras are absent,
so neither reddens for a provisioning reason unrelated to the feature under
test. Class 1 carries no such dependency and runs in EVERY lane -- it is the
always-on, CI-enforced prose half of this gate.

MEASURED (the second guard, Class 3 only): ``shutil.which("dot")`` is ``None``
in the ambient shell and resolves to a real Graphviz binary inside the project's
nix devShell. The ``sys.executable -m sphinx`` child inherits this process's
PATH, so ``which`` here and the child always agree -- which is what makes the
guard sound rather than a guess about the subprocess's environment.

HTML (D014): this module deliberately asserts NOTHING about the HTML build. Had
it, the only safe assertion would be ``returncode == 0``; a zero-warning
assertion would be wrong, because ``dot command 'dot' cannot be run`` is EXPECTED
on any machine without Graphviz installed -- which is the very contrast the
diagrams page exists to explain. The HTML build additionally needs ``furo`` from
the same absent ``docs`` extra, so it is left to ``tox -e docs-html``.
"""

import html as html_mod
import importlib.util
import re
import shutil
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

# Sphinx extensions and the HTML theme the real docs builds import that are
# NOT in the `dev` extra -- see the dependency-guard note in the module
# docstring. `furo` is reached only by `-b html`, but it is guarded in the
# SHARED tuple rather than separately because all three ship in the same
# `docs` extra: there is no environment that has two of them and not the
# third, so one check covers every build class here.
_DOCS_EXTRA_MODULES = ("myst_parser", "sphinx_autodoc_typehints", "furo")

# The rendered diagram's `<img src>` in the built HTML, matched by REGEX and
# never by a hard-coded digest. Upstream names the file after a sha1 of the
# DOT source plus its options, so the digest is deterministic for a given
# diagram (MEASURED: graphviz-9d601b680ab94eac1febdc364a0d914f474368d3.png)
# but changes the moment the DOT body is edited -- a literal would turn an
# ordinary diagram edit into a mysterious gate failure.
GRAPHVIZ_PNG_SRC_RE = re.compile(r'src="([^"]*graphviz-[0-9a-f]{40}\.png)"')


# The raw DOT marker: the opening line of the dogfood diagram's own source,
# and the exact RED shape measured 2026-10-02 -- on a machine with no `dot`
# binary this string is served to the reader as page TEXT instead of a
# rendered image. Read as a literal rather than from diagrams.rst because the
# assertions below are about this one line, not about the whole DOT body.
DOT_SOURCE_MARKER = "digraph dogfood {"

# Any HTML tag, used to reduce a built page to its visible text.
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _visible_text(markup: str) -> str:
    """
    Reduce HTML markup to roughly what a reader SEES: drop every tag, then
    resolve character entities.

    The parameter is ``markup``, not ``html``, so the stdlib ``html`` module
    (imported here as ``html_mod``) is not shadowed.

    A regex strip is deliberate and sufficient -- neither BeautifulSoup nor
    lxml is a dependency of this project, and a regex is exactly what was
    measured when the RED/GREEN contrast was established by hand.

    Two ordering properties are load-bearing:

    * **Unescape AFTER stripping, never before.** Entities that live inside
      attribute values would otherwise be decoded while still inside a tag
      and then survive the strip as apparent text.
    * **Each tag becomes a SPACE, not the empty string**, so two words
      separated only by a tag boundary do not fuse into one token and
      invent a match (or hide one) that the reader never sees.

    The property the absence assertions below actually depend on: because the
    whole ``<img ...>`` tag goes, the text of its ``alt`` attribute goes with
    it. That matters concretely here -- the dogfood diagram's ``:alt:`` text
    names both node labels, so ``Vorthaneglim`` IS in the raw markup of a
    correctly-rendered page and is NOT in its visible text.
    """
    return html_mod.unescape(_HTML_TAG_RE.sub(" ", markup))


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
            "docs extras absent (myst-parser / sphinx-autodoc-typehints / "
            "furo): the real docs build aborts with ExtensionError before "
            "reaching any typsphinx code -- install the `docs` extra to run "
            "this class."
        )

    build_dir = tmp_path_factory.mktemp("docs_typstpdf_build")
    result = _run_sphinx_build(DOCS_SOURCE_DIR, build_dir, "typstpdf")
    return result, build_dir


@pytest.fixture(scope="module")
def docs_html_build(tmp_path_factory):
    """
    Build typsphinx's REAL docs tree once with ``-b html`` and hand the
    completed process and output directory to every test in Class 3.

    Module-scoped for DETERMINISM, not cost. Every assertion in Class 3 reads
    the SAME artifacts -- one ``diagrams.html`` and the one
    ``graphviz-<sha1>.png`` it points at -- so a per-test rebuild would let
    two assertions disagree about the page they are describing. MEASURED: a
    clean build (fresh outdir, fresh doctrees) takes ~2s, roughly two orders
    of magnitude cheaper than the sibling 144-page ``typstpdf`` build, so that
    fixture's "because it is slow" rationale does NOT transfer here.

    Skips, never fails, on either missing prerequisite:

    * the docs extras, exactly as Class 2 does; and
    * a real ``dot`` binary. ``sphinx.ext.graphviz`` shells out to it, so
      without it the page carries a warning placeholder instead of a PNG and
      this class would redden for a provisioning reason unrelated to the
      feature -- which is the very missing-Graphviz contrast the diagrams page
      exists to explain. See the module docstring for why checking ``which``
      in this process is sound for the subprocess.
    """
    if not _docs_extras_available():
        pytest.skip(
            "docs extras absent (myst-parser / sphinx-autodoc-typehints / "
            "furo): the real docs build aborts with ExtensionError before "
            "reaching any typsphinx code -- install the `docs` extra to run "
            "this class."
        )
    if shutil.which("dot") is None:
        pytest.skip(
            "no `dot` binary on PATH: sphinx.ext.graphviz cannot rasterise "
            "the dogfood diagram, so the built page would carry a warning "
            "placeholder rather than a PNG -- install Graphviz (or enter the "
            "project's nix devShell) to run this class."
        )

    build_dir = tmp_path_factory.mktemp("docs_html_build")
    result = _run_sphinx_build(DOCS_SOURCE_DIR, build_dir, "html")
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


class TestDogfoodedDiagramHTMLBuild:
    """
    R011: a real ``-b html`` build of typsphinx's OWN docs tree, proving the
    dogfooded diagram reaches the published HTML page as a real ``<img>``
    backed by an on-disk PNG -- the HTML counterpart to Class 2's PDF proof.

    S02 established this by hand; this class is what makes it durable, so a
    docs-source regression on that page cannot ship silently.

    Two things this class deliberately does NOT assert, both MEASURED:

    * **No warning count and no warning text.** Warning-based gating here is
      brittle and locale-dependent -- the build's own summary line is
      localised (``HTMLページは ... にあります。`` under a Japanese-locale
      shell). ``returncode == 0`` is the only build-outcome claim made.
    * **No node-label sentinel.** ``NODE_LABEL_SENTINELS`` has INVERTED
      polarity in HTML: the labels are pixels inside the PNG, so
      ``Vorthaneglim`` appears ZERO times in the GREEN page's tag-stripped
      visible text and once in a broken one. "The node label appears in the
      rendered HTML" would pass only on the broken page. The sentinels stay
      valid for the PDF, which is why Class 2 uses them.

    MEASURED weakness, by construction, and a recorded milestone decision
    rather than a defect to fix: GitHub Actions' ``ubuntu-latest`` image
    PREINSTALLS ``dot``, so in CI this class renders a real PNG and PASSES --
    it would have passed unchanged throughout the entire original defect,
    which was a missing Graphviz on the *Read the Docs* builder. What this
    class guards is therefore docs-SOURCE regression: the directive being
    removed, renamed, or reduced to a literal block. The
    environment-independent half -- the one that would actually have caught
    the original defect -- is the configuration gate in
    ``tests/test_readthedocs_config.py``, which asserts ``graphviz`` is in
    ``.readthedocs.yaml``'s ``build.apt_packages`` and needs no build at all.
    Detection is split across those two gates on purpose.
    """

    @staticmethod
    def _diagrams_page(build_dir: Path) -> Path:
        """The built diagrams page, asserted present before it is read."""
        page = build_dir / "user_guide" / "diagrams.html"
        assert (
            page.exists()
        ), f"Expected the built page user_guide/diagrams.html under {build_dir}."
        return page

    def test_html_build_succeeds(self, docs_html_build):
        """The real docs HTML build exits 0 (no warning assertion -- see the
        class docstring for why warning text is not gated here)."""
        result, _ = docs_html_build
        assert result.returncode == 0, (
            f"Expected the real docs html build to succeed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_page_carries_a_graphviz_img_backed_by_a_real_png(self, docs_html_build):
        """
        The page carries the graphviz ``<img>`` AND the file it points at is
        a real PNG on disk.

        The on-disk check is the load-bearing half: an ``src`` string alone
        proves only that upstream emitted a tag, not that Graphviz actually
        rasterised anything, so the ``src`` is resolved relative to the HTML
        file and the bytes behind it are inspected.
        """
        _, build_dir = docs_html_build
        page = self._diagrams_page(build_dir)
        html = page.read_text(encoding="utf-8")

        # MEASURED exactly 2: upstream puts the class on BOTH the wrapping
        # `div` and the `img` itself (`imgcls = ' '.join([imgcls, 'graphviz',
        # *node['classes']])`). Asserted as `>= 1` so a future upstream
        # reshuffle of either site does not redden a working page; `== 1`
        # would be WRONG today.
        assert html.count('class="graphviz"') >= 1, (
            "Expected a graphviz-classed element on the built diagrams page; "
            "the diagram did not reach the HTML output."
        )

        match = GRAPHVIZ_PNG_SRC_RE.search(html)
        assert match is not None, (
            "Expected an <img src> naming a graphviz-<sha1>.png on the built "
            "diagrams page -- sphinx.ext.graphviz emitted no rendered image."
        )

        png_path = (page.parent / match.group(1)).resolve()
        assert png_path.exists(), (
            f"The diagrams page points at {match.group(1)!r} but no such file "
            f"exists at {png_path} -- the <img> is dangling."
        )
        data = png_path.read_bytes()
        # MEASURED 11608 bytes; asserted against a small floor rather than the
        # exact size, which any Graphviz version bump would move.
        assert len(data) > 1024, (
            f"Expected a non-trivial rendered PNG at {png_path}, got "
            f"{len(data)} bytes."
        )
        assert data.startswith(b"\x89PNG"), (
            f"Expected PNG magic at the head of {png_path}; the file is not a "
            f"real PNG image."
        )

    def test_png_output_format_is_pinned(self, docs_html_build):
        """
        No ``<object>`` element on the page, which pins the ``png`` output
        format.

        ``graphviz_output_format`` defaults to ``png`` and the ``svg`` branch
        emits an ``<object>`` wrapper instead of a plain ``<img>`` -- so this
        is what keeps the sibling assertion above (which matches a ``.png``
        ``src``) meaningful rather than silently unsatisfiable. MEASURED 0.
        """
        _, build_dir = docs_html_build
        html = self._diagrams_page(build_dir).read_text(encoding="utf-8")
        assert "<object" not in html, (
            "Found an <object> element on the built diagrams page: the "
            "graphviz output format is no longer png, so the rendered-PNG "
            "assertions in this class no longer describe the real output."
        )

    def test_raw_dot_source_is_not_visible_page_text(self, docs_html_build):
        """
        PRIMARY RED-direction assertion: the raw DOT source line is NOT part
        of the page's visible text.

        MEASURED 0 on a correctly-rendered page and 1 on the reported broken
        one, where `sphinx.ext.graphviz` could not reach `dot` and served the
        reader the diagram's source instead of a picture of it. This is the
        primary absence check because it holds whether or not the directive
        carries an `:alt:` option -- see the raw-markup sibling below for why
        that distinction matters.
        """
        _, build_dir = docs_html_build
        html = self._diagrams_page(build_dir).read_text(encoding="utf-8")
        text = _visible_text(html)
        assert DOT_SOURCE_MARKER not in text, (
            f"Found the raw DOT source line {DOT_SOURCE_MARKER!r} in the "
            f"visible text of the built diagrams page: the diagram was not "
            f"rendered and its source is being shown to the reader instead."
        )

    def test_raw_dot_source_is_absent_from_the_raw_markup_too(self, docs_html_build):
        """
        Secondary absence check, over the RAW markup rather than the visible
        text. MEASURED 0 today -- but, unlike its sibling above, only because
        the dogfood directive carries an explicit `:alt:` option.

        `sphinx/ext/graphviz.py` computes the image's alt text as
        `node.get('alt', self.encode(code).strip())`: with NO `:alt:`,
        upstream falls back to the DOT SOURCE ITSELF as the attribute value.
        A perfectly rendered page would then still match a raw-markup grep
        while matching zero times in visible text. So this assertion is
        legitimately allowed to flip if that option is ever dropped, and
        asserting it ALONE would really be asserting "an `:alt:` option
        exists" -- which is why the visible-text check above, not this one,
        is the load-bearing half.
        """
        _, build_dir = docs_html_build
        html = self._diagrams_page(build_dir).read_text(encoding="utf-8")
        assert DOT_SOURCE_MARKER not in html, (
            f"Found the raw DOT source line {DOT_SOURCE_MARKER!r} in the raw "
            f"markup of the built diagrams page. Check whether the dogfood "
            f"directive still carries an `:alt:` option -- if it does not, "
            f"upstream uses the DOT source as the img alt text and this "
            f"assertion no longer indicates a rendering failure."
        )

    def test_node_labels_are_not_visible_page_text(self, docs_html_build):
        """
        Second RED-direction sentinel: the diagram's node labels are NOT in
        the page's visible text. MEASURED 0 in GREEN, 1 in RED.

        This is the exact INVERSE of how `NODE_LABEL_SENTINELS` is used in
        Class 2, and deliberately so. In the PDF the labels are real vector
        TEXT inside the drawn diagram, so pypdf extracts them and their
        presence proves the diagram rendered. In HTML the same labels are
        PIXELS inside a rasterised PNG, so visible text containing them means
        the opposite: the DOT source leaked onto the page. The labels do
        appear in the raw markup of a correct page, inside the `:alt:`
        attribute -- which the tag strip removes along with its tag.
        """
        _, build_dir = docs_html_build
        html = self._diagrams_page(build_dir).read_text(encoding="utf-8")
        text = _visible_text(html)
        for sentinel in NODE_LABEL_SENTINELS:
            assert sentinel not in text, (
                f"Found the node label {sentinel!r} in the visible text of "
                f"the built diagrams page: the label should be pixels inside "
                f"the rendered PNG, so its presence as text means the DOT "
                f"source leaked onto the page."
            )
