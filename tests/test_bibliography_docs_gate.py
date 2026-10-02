"""
R012: prose + invariant + real-build gate binding the published bibliography
page (``docs/source/user_guide/bibliography.rst``) to the MEASURED behaviour
S01-S06 established, and binding D014's no-live-directive rule to the fact
that ``tox -e docs-pdf`` and Read the Docs cannot import sphinxcontrib-bibtex.

Why this module exists: a documentation page that nothing asserts rots
silently -- that is precisely how ``README.md`` came to ship claims about
bibliography support that measurement later falsified. Every claim the page
makes is therefore pinned here, so deleting or contradicting a claim is red.

Structured as the sibling ``tests/test_graphviz_docs_gate.py`` is, and for the
same reason -- a three-class split where the always-on classes carry no
external dependency:

* ``TestPublishedBibliographyProse`` reads the page from disk. No build, no
  skip, and in particular NO dependency on sphinxcontrib-bibtex, so it runs in
  EVERY CI lane including the docs-extra-only ones.
* ``TestBibliographyDogfoodInvariant`` encodes D014. No build, no skip.
* ``TestDogfoodedBibliographyPageBuild`` runs a real ``-b typstpdf`` build of
  typsphinx's OWN docs tree, and skips when the docs extras are absent.

Per this suite's established convention, this module carries its OWN copy of
the ``_run_sphinx_build`` helper rather than importing a sibling's.

MEASURED (D014, the invariant Class 2 protects): ``sphinxcontrib-bibtex`` is a
``dev``-extra-only dependency (``pyproject.toml``, R012), while ``tox.ini``'s
``docs-pdf`` env and ``.readthedocs.yaml`` both install only the ``docs``
extra. A column-0 ``.. bibliography::`` on this page would therefore hard-abort
those two builds with ``ExtensionError`` -- while still passing in the
maintainer's venv and in ``.github/workflows/docs.yml``, both of which install
dev+docs. That asymmetry is exactly what makes the breakage easy to ship and
hard to notice, so it is asserted rather than left to a comment. Indented
occurrences inside ``.. code-block:: rst`` are EXPECTED and must stay legal,
which is why Class 2 matches on line start and reads the page RAW (column
position is the whole point) rather than whitespace-collapsed.

MEASURED (skip-helper trap -- do not copy the sibling's helper unchanged):
``importlib.util.find_spec("sphinxcontrib.bibtex")`` RAISES
``ModuleNotFoundError`` rather than returning ``None`` when the
``sphinxcontrib`` namespace parent is absent, confirmed in a clean
interpreter. The sibling's ``_docs_extras_available()`` relies on ``find_spec``
returning ``None``, which holds only for its single-segment module names. The
docs-extras check below therefore uses only single-segment names
(``myst_parser``, ``sphinx_autodoc_typehints``) and keeps bibtex out of the
skip condition entirely -- Class 3 must NOT require bibtex, because the docs
build is required to work without it. The ``try/except ModuleNotFoundError``
below is belt-and-braces in case a dotted name is ever added.

MEASURED (locale): per CLAUDE.md, Sphinx localises warning/error BODIES to the
host ``LANG`` but never the severity token. No assertion in this module
inspects localisable build-output text; Class 3 asserts an exit code and the
emitted artifacts, both locale-stable.
"""

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_SOURCE_DIR = REPO_ROOT / "docs" / "source"
BIBLIOGRAPHY_RST_PATH = DOCS_SOURCE_DIR / "user_guide" / "bibliography.rst"
USER_GUIDE_INDEX_RST_PATH = DOCS_SOURCE_DIR / "user_guide" / "index.rst"
DOCS_CONF_PY_PATH = DOCS_SOURCE_DIR / "conf.py"

# Sphinx extensions the real docs build imports that are NOT in the `dev`
# extra -- see the skip-helper note in the module docstring. Single-segment
# names only, deliberately.
_DOCS_EXTRA_MODULES = ("myst_parser", "sphinx_autodoc_typehints")

# A column-0 reference-list directive: the one shape D014 forbids on this page.
_LIVE_DIRECTIVE_RE = re.compile(r"^\.\. (foot)?bibliography::", re.MULTILINE)

# Why a live directive breaks the two builds that matter -- reused verbatim in
# both D014 assertion messages so each failure explains itself.
_D014_WHY = (
    "sphinxcontrib-bibtex is dev-extra-only (pyproject.toml, R012) while "
    "tox.ini's docs-pdf env and .readthedocs.yaml install only the `docs` "
    "extra, so this would hard-abort both builds with ExtensionError while "
    "still passing the maintainer's venv and .github/workflows/docs.yml "
    "(both dev+docs). See D014."
)


def _docs_extras_available() -> bool:
    """True when every docs-only Sphinx extension the real docs build imports
    is installed in the running interpreter.

    ``find_spec`` is wrapped because it RAISES ``ModuleNotFoundError`` -- not
    returns ``None`` -- for a dotted name whose namespace parent is missing.
    """
    for name in _DOCS_EXTRA_MODULES:
        try:
            if importlib.util.find_spec(name) is None:
                return False
        except ModuleNotFoundError:
            return False
    return True


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard.
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
    completed process and output directory to every test in Class 3.

    Module-scoped because this is a full docs build plus a PDF compile; running
    it per test would multiply the slowest step in this module by the number of
    assertions that read it.

    Skips (never fails) when the docs extras are absent: ``docs/source/conf.py``
    loads ``myst_parser`` and ``sphinx_autodoc_typehints``, so under a dev-only
    environment the build aborts with ``ExtensionError`` before reaching any
    typsphinx code. Note this fixture does NOT require sphinxcontrib-bibtex --
    by D014 the docs tree must build without it.
    """
    if not _docs_extras_available():
        pytest.skip(
            "docs extras absent (myst-parser / sphinx-autodoc-typehints): the "
            "real docs build aborts with ExtensionError before reaching any "
            "typsphinx code -- install the `docs` extra to run this class."
        )

    build_dir = tmp_path_factory.mktemp("docs_bibliography_typstpdf_build")
    result = _run_sphinx_build(DOCS_SOURCE_DIR, build_dir, "typstpdf")
    return result, build_dir


class TestPublishedBibliographyProse:
    """
    R012: the published bibliography page states the required setup, names
    every supported citing form, states the ownership boundary, and documents
    all three constraints a user can actually trip.

    No build, no skip, no external dependency -- this class runs in every CI
    lane and fails whenever the page stops making a claim it must make.
    Assertions are semantic (a distinctive lowercase substring per claim), not
    whole-paragraph matches, so ordinary copy-editing does not redden them but
    deleting a claim does.
    """

    @staticmethod
    def _page_text() -> str:
        """
        The page, lowercased with every whitespace run collapsed to a single
        space.

        Collapsing matters: the page is hard-wrapped at ~88 columns, so a claim
        like "legitimately renders twice in the finished PDF" is split across a
        newline in the source. Asserting against the raw text would make these
        tests fail on a pure re-wrap that changed no words at all -- exactly the
        false positive a prose gate must not have.
        """
        return " ".join(
            BIBLIOGRAPHY_RST_PATH.read_text(encoding="utf-8").lower().split()
        )

    def test_page_states_the_user_installs_bibtex_themselves(self):
        """Setup claim 1: sphinxcontrib-bibtex is NOT a typsphinx dependency;
        the user installs it themselves."""
        text = self._page_text()
        assert "is **not** a typsphinx dependency" in text, (
            "bibliography.rst no longer states that sphinxcontrib-bibtex is "
            "NOT a typsphinx dependency."
        )
        assert "you install the bibliography extension yourself" in text, (
            "bibliography.rst no longer states that the user installs the "
            "bibliography extension themselves."
        )
        assert "pip install sphinxcontrib-bibtex" in text, (
            "bibliography.rst no longer shows the install command for "
            "sphinxcontrib-bibtex."
        )

    def test_page_states_bibtex_goes_in_the_users_own_extensions(self):
        """Setup claim 2: ``sphinxcontrib.bibtex`` must be added to the user's
        OWN conf.py extensions, alongside typsphinx."""
        text = self._page_text()
        assert '"sphinxcontrib.bibtex"' in text, (
            "bibliography.rst no longer shows 'sphinxcontrib.bibtex' being "
            "added to the user's own extensions list."
        )
        assert "enable it in your own ``conf.py``" in text, (
            "bibliography.rst no longer states that the extension is enabled "
            "in the user's own conf.py."
        )
        assert "bibtex_bibfiles" in text, (
            "bibliography.rst no longer names bibtex_bibfiles, so the setup "
            "section no longer points sphinxcontrib-bibtex at the .bib files."
        )

    def test_page_names_every_supported_citing_role(self):
        """Every supported citing role is named: :cite:p:, :cite:t: and
        :footcite:."""
        text = self._page_text()
        for role in (":cite:p:", ":cite:t:", ":footcite:"):
            assert role in text, (
                f"bibliography.rst no longer names the supported citing form "
                f"{role!r}."
            )

    def test_page_names_every_supported_reference_list_directive(self):
        """Both reference-list directives are named: .. bibliography:: and
        .. footbibliography::."""
        text = self._page_text()
        for directive in (".. bibliography::", ".. footbibliography::"):
            assert directive in text, (
                f"bibliography.rst no longer names the supported reference "
                f"list directive {directive!r}."
            )

    def test_page_documents_the_multi_key_form(self):
        """The multi-key form is documented, including that several keys in
        one role render as ONE bracketed group rather than one per key."""
        text = self._page_text()
        assert ":cite:p:`smith2020,tanaka2019`" in text, (
            "bibliography.rst no longer shows a multi-key citation example "
            "naming several keys in a single role."
        )
        assert "naming several keys renders as **one** bracketed group" in text, (
            "bibliography.rst no longer states that a multi-key role renders "
            "as one bracketed group rather than one group per key."
        )

    def test_page_states_citations_resolve_across_the_include_boundary(self):
        """Cross-document resolution: a citing site in an included document
        resolves against a reference list in a DIFFERENT document, and the
        link survives the Typst #include() boundary."""
        text = self._page_text()
        assert "living in a *different* document" in text, (
            "bibliography.rst no longer states that a citing site resolves "
            "against a reference list in a different document."
        )
        assert "survives the typst ``#include()`` boundary" in text, (
            "bibliography.rst no longer states that the resolved link "
            "survives the Typst #include() boundary."
        )

    def test_page_states_citation_format_is_owned_by_pybtex(self):
        """Ownership boundary, half 1: labels and entry bodies come from
        pybtex, and typsphinx emits them as-is."""
        text = self._page_text()
        assert "owned by pybtex" in text, (
            "bibliography.rst no longer states that citation style is owned "
            "by pybtex."
        )
        assert "bibtex_default_style" in text, (
            "bibliography.rst no longer names bibtex_default_style as the "
            "route by which the pybtex style is selected."
        )
        assert "typsphinx does not reformat" in text, (
            "bibliography.rst no longer states that typsphinx does not "
            "reformat pybtex's labels or entry bodies."
        )

    def test_page_states_typst_native_bibliography_and_csl_are_not_used(self):
        """Ownership boundary, half 2: Typst's own #bibliography() and #cite()
        are deliberately NOT used, so CSL styles are unavailable."""
        text = self._page_text()
        assert "``#bibliography()``" in text, (
            "bibliography.rst no longer names Typst's native #bibliography() "
            "function."
        )
        assert (
            "``#cite()``" in text
        ), "bibliography.rst no longer names Typst's native #cite() function."
        assert "deliberately not used" in text, (
            "bibliography.rst no longer states that Typst's native "
            "#bibliography()/#cite() functions are deliberately not used."
        )
        assert "csl styles are **unavailable**" in text, (
            "bibliography.rst no longer states that Typst's CSL styles are "
            "unavailable."
        )

    def test_page_states_exactly_once_is_per_reference_list(self):
        """Constraint 1: exactly-once is a PER reference list property, and a
        key owned by two directives legitimately renders twice."""
        text = self._page_text()
        assert "exactly-once is a *per reference list* property" in text, (
            "bibliography.rst no longer states that exactly-once is a per "
            "reference list property rather than a per document one."
        )
        assert "legitimately renders **twice**" in text, (
            "bibliography.rst no longer states that an entry owned by two "
            "bibliography directives legitimately renders twice."
        )
        assert "not a duplication bug" in text, (
            "bibliography.rst no longer states that rendering twice is "
            "correct output rather than a duplication bug."
        )

    def test_page_states_key_on_left_filter_degrades_silently(self):
        """Constraint 2: the key-on-left :filter: form is a SILENT failure --
        the grid empties while the build stays clean, even under -W."""
        text = self._page_text()
        assert (
            ":filter:" in text
        ), "bibliography.rst no longer mentions the :filter: option at all."
        assert "is a **silent** failure" in text, (
            "bibliography.rst no longer states that writing the :filter: "
            "comparison key-on-the-right is a silent failure."
        )
        assert "zero warnings, even under** ``-w``" in text, (
            "bibliography.rst no longer states that the degraded :filter: "
            "build emits zero warnings even under -W."
        )
        assert "build cleanliness therefore cannot detect this" in text, (
            "bibliography.rst no longer states that build cleanliness cannot "
            "detect the silent :filter: degradation."
        )

    def test_page_states_keyprefix_is_load_bearing(self):
        """Constraint 3: :keyprefix: is load-bearing -- removing it is a hard
        bibtex.duplicate_citation failure under a strict build."""
        text = self._page_text()
        assert (
            ":keyprefix:" in text
        ), "bibliography.rst no longer mentions the :keyprefix: option at all."
        assert "is load-bearing" in text, (
            "bibliography.rst no longer states that :keyprefix: is "
            "load-bearing rather than cosmetic."
        )
        assert "bibtex.duplicate_citation" in text, (
            "bibliography.rst no longer names the bibtex.duplicate_citation "
            "failure that removing :keyprefix: produces."
        )


class TestBibliographyDogfoodInvariant:
    """
    D014: the published page must stay buildable by the two environments that
    install only the ``docs`` extra -- ``tox -e docs-pdf`` and Read the Docs.

    No build, no skip. This class is what stops a later well-meaning edit
    ("let's show a real reference list!") from silently breaking published
    documentation in environments the author never runs.

    Reads the page RAW, not whitespace-collapsed: column position is the whole
    point, since an INDENTED directive inside ``.. code-block:: rst`` is
    expected and legal while a column-0 one is not.
    """

    def test_page_embeds_no_live_reference_list_directive(self):
        """No line of the page starts a live .. bibliography:: or
        .. footbibliography:: directive at column 0."""
        raw = BIBLIOGRAPHY_RST_PATH.read_text(encoding="utf-8")
        matches = _LIVE_DIRECTIVE_RE.findall(raw)
        offending = [
            line
            for line in raw.splitlines()
            if line.startswith((".. bibliography::", ".. footbibliography::"))
        ]
        assert not matches, (
            f"bibliography.rst embeds a LIVE column-0 reference-list "
            f"directive ({offending!r}). {_D014_WHY} Indented occurrences "
            f"inside a `.. code-block:: rst` are fine -- only column-0 ones "
            f"are live."
        )

    def test_docs_conf_py_does_not_enable_bibtex(self):
        """docs/source/conf.py does not enable sphinxcontrib.bibtex."""
        text = DOCS_CONF_PY_PATH.read_text(encoding="utf-8")
        assert "sphinxcontrib.bibtex" not in text, (
            f"docs/source/conf.py now references sphinxcontrib.bibtex. " f"{_D014_WHY}"
        )

    def test_user_guide_index_references_the_bibliography_page_twice(self):
        """
        docs/source/user_guide/index.rst wires the bibliography page in BOTH
        places a user-guide page must appear: the toctree (as a bare indented
        docname line) and the "Main Topics" :doc: list. Asserted as two
        DISTINCT occurrences, so wiring it into only one place is red.
        """
        text = USER_GUIDE_INDEX_RST_PATH.read_text(encoding="utf-8")
        assert "\n   bibliography\n" in text, (
            "docs/source/user_guide/index.rst does not list `bibliography` as "
            "a bare indented toctree entry."
        )
        assert ":doc:`bibliography`" in text, (
            "docs/source/user_guide/index.rst does not reference "
            "``:doc:`bibliography``` in its Main Topics list."
        )


class TestDogfoodedBibliographyPageBuild:
    """
    R012: a real ``-b typstpdf`` build of typsphinx's OWN docs tree, proving
    the published page actually reaches the emitted Typst output -- the
    end-to-end counterpart to D014's static invariant.

    Skips (never fails) when the docs extras are absent; see the module
    docstring for the measurement behind that choice. Deliberately does NOT
    require sphinxcontrib-bibtex: that it builds without it IS the claim.
    """

    def test_docs_typstpdf_build_succeeds(self, docs_typstpdf_build):
        """The real docs build exits 0 with the bibliography page present --
        the direct refutation of the D014 failure mode, measured rather than
        reasoned about."""
        result, _ = docs_typstpdf_build
        assert result.returncode == 0, (
            f"Expected the real docs typstpdf build to succeed with the "
            f"bibliography page present:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_bibliography_page_reaches_the_emitted_typst_output(
        self, docs_typstpdf_build
    ):
        """
        The emitted CONTENT file ``user_guide/bibliography.typ`` exists and
        carries the page's own section headings.

        Asserted on the CONTENT file, NOT on the ``typsphinx.typ`` wrapper:
        the wrapper holds only the template application and ``#include()``s of
        the per-docname content files.
        """
        _, build_dir = docs_typstpdf_build
        content_typ = build_dir / "user_guide" / "bibliography.typ"
        assert content_typ.exists(), (
            f"Expected the content file user_guide/bibliography.typ under "
            f"{build_dir} -- the published page never reached the builder."
        )

        text = content_typ.read_text(encoding="utf-8")
        for heading in (
            "Bibliography and Citations",
            "Constraints You Can Trip",
            "Citation Style Is Owned By pybtex",
        ):
            assert heading in text, (
                f"Expected the published heading {heading!r} in the emitted "
                f"user_guide/bibliography.typ."
            )

    def test_bibliography_page_is_reachable_from_the_master_document(
        self, docs_typstpdf_build
    ):
        """
        The page is part of the compiled document rather than an orphan
        ``.typ`` sitting beside it.

        MEASURED include shape -- the master does NOT include leaf pages
        directly, so asserting ``user_guide/bibliography.typ`` in
        ``typsphinx.typ`` is wrong and was corrected here. The real chain has
        two links, and both are asserted:

        1. ``typsphinx.typ`` registers the edge
           ``user_guide/index#0>user_guide/bibliography`` in its
           ``typsphinx:include-edges`` state, and
        2. the intermediate ``user_guide/index.typ`` carries the guarded
           ``include("bibliography.typ")`` that the edge unlocks.

        Asserting both is what makes this meaningful: the guard in (2) is a
        no-op unless the edge in (1) is present, so a test that checked only
        one of them would pass on a page that never renders.
        """
        _, build_dir = docs_typstpdf_build

        master_typ = build_dir / "typsphinx.typ"
        assert master_typ.exists(), f"Expected the master document at {master_typ}."
        master_text = master_typ.read_text(encoding="utf-8")
        assert "user_guide/index#0>user_guide/bibliography" in master_text, (
            "Expected typsphinx.typ to register the include edge "
            "'user_guide/index#0>user_guide/bibliography' -- without it the "
            "guarded include in user_guide/index.typ never fires and the page "
            "is absent from the compiled document."
        )

        parent_index_typ = build_dir / "user_guide" / "index.typ"
        assert (
            parent_index_typ.exists()
        ), f"Expected the intermediate index at {parent_index_typ}."
        parent_text = parent_index_typ.read_text(encoding="utf-8")
        assert 'include("bibliography.typ")' in parent_text, (
            "Expected user_guide/index.typ to carry "
            'include("bibliography.typ") -- the page is an orphan otherwise.'
        )

    def test_compiled_pdf_carries_the_published_page(self, docs_typstpdf_build):
        """The compiled ``typsphinx.pdf`` exists and contains the page's own
        distinctive prose -- the end-to-end proof the page is in the published
        PDF, not merely markup that compiled."""
        _, build_dir = docs_typstpdf_build
        pdf_path = build_dir / "typsphinx.pdf"
        assert pdf_path.exists(), f"Expected the compiled PDF at {pdf_path}."

        from pypdf import PdfReader

        reader = PdfReader(str(pdf_path))
        pdf_text = " ".join(
            " ".join((page.extract_text() or "").split()) for page in reader.pages
        )
        assert "Citation Style Is Owned By pybtex" in pdf_text, (
            "Expected the bibliography page's ownership-boundary heading in "
            "the built PDF -- the page did not render."
        )
