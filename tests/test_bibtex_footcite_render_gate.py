"""
M001 / S03 bibtex FOOTCITE render gate: SC1, SC2, SC4, SC5.

**What this module pins.** That a ``:footcite:`` citing site plus a trailing
``.. footbibliography::`` render as REAL Typst footnotes -- the
label-attached DEFINITION form ``[#footnote({...}) <label>]`` at a key's
first site, the bare REUSE form ``footnote(<label>)`` at a repeat site --
with ZERO Typst ``grid(`` anywhere in the emitted content file, with a
hand-written docutils footnote coexisting under a DISTINCT label, and with
no ``refs.bib`` entry the fixture never cites reaching the output at all.

**This gate is GREEN ON ARRIVAL, by design, and no RED was manufactured.**
S03 plan-time measurement already proved the footnote path works with ZERO
typsphinx production-code change: a real ``-W`` build of
``tests/fixtures/bibtex_footcite_render_gate/`` emits both footnote forms,
zero grid, and zero warnings against the UNTOUCHED translator. A
conventional RED-first gate therefore CANNOT go RED here without breaking
working translator code on purpose, which this task explicitly forbids
(``git diff --quiet -- typsphinx/`` is part of its own verification). This
is a *characterisation* gate in the established repo sense -- it locks
measured current behaviour so later slices cannot silently regress it.
Precedent for the shape and for the honesty of declaring it: this
milestone's own S01/T03 (``tests/test_bibtex_citation_render_gate.py``,
which documents the identical green-on-arrival position) and
``tests/test_typst_elements_pass_through_gate.py`` (GATE-01). Because the
gate cannot be proven by a RED, every assertion below was instead proven to
have TEETH by a sensitivity probe over mutated COPIES of the fixture --
removed footcite site, added ``.. bibliography::``, collapsed label,
deleted cited title -- each of which was measured to flip the corresponding
test to failure. The probe results are recorded in this task's summary; no
probe mutation is left in the tracked tree.

**Why this module exists separately from the S01/S02 gate.** The shared
``tests/fixtures/bibtex_citation_render_gate`` fixture CANNOT host the
footcite case: appending a footcite site plus footbibliography to it was
measured at plan time to give 2 failed / 11 passed, because a key's title
then legitimately appears both as a ``.. bibliography::`` grid row and as a
footnote body. See decision D008 and the fixture's own ``conf.py``
docstring. Worse, the shared gate's site parser regexes
``:cite:([a-z]*):``, which does **NOT** match the colonised footcite role
(measured: returns ``[]``), so it would have kept reporting its old site
counts while their meaning was silently redefined underneath it. That
measured blind spot is exactly why this module carries its OWN site parser
(:func:`_parse_footcite_sites`) rather than importing the shared one.

**Resolve-at-most-once discipline (MEM009).** This module resolves NO
doctree at all: there is no ``env.get_and_resolve_doctree()`` call and no
``SphinxTestApp``. Every assertion runs against the emitted ``.typ`` text of
a real ``sphinx-build`` subprocess, and no expectation anywhere is derived
from a node CHILD COUNT. The upstream sphinxcontrib-bibtex double-resolve
hazard (MEM009, R014) is live and unfixable from typsphinx, so this module
simply never enters the code path that exposes it. Do not add a resolve
here.

**Labels are computed, never transcribed.** Every expected Typst label is
produced by calling the translator's own
``TypstTranslator._namespace_label`` over a refid derived from
fixture-authored data -- the bibtex key for a footcite footnote, the parsed
footnote name for the hand-written one -- so a change to the project's
label-namespacing convention moves the expectation with it instead of
leaving a stale string literal behind.

**Assertions read ``index.typ``, never ``master.typ``.** The two-layer split
writes this docname's content to ``index.typ`` and only a wrapper to
``master.typ``; asserting over the wrapper would prove nothing about the
rendered body.
"""

import io
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
from docutils.nodes import make_id

from typsphinx.translator import TypstTranslator

try:
    import sphinxcontrib.bibtex  # noqa: F401

    BIBTEX_AVAILABLE = True
except ImportError:
    BIBTEX_AVAILABLE = False

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf  # noqa: F401

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


# The fixture's single document. A docname (a filename on disk), not a
# generated label token, so naming it here breaches no house rule: the
# fixture deliberately has no second document and no toctree.
DOCNAME = "index"

# The CONTENT file the two-layer split writes for DOCNAME. Every assertion in
# this module reads THIS file, never master.typ.
CONTENT_TYP = f"{DOCNAME}.typ"

# The refid template sphinxcontrib-bibtex uses for a footcite footnote, taken
# from upstream ``sphinxcontrib/bibtex/foot_roles.py`` (the default value of
# its ``bibtex_footcite_id`` config): the raw id is ``"footcite-{key}"`` run
# through docutils' ``make_id``, and docutils then derives the footnote node's
# id from that name. The fixture leaves ``bibtex_footcite_id`` unset, so this
# default is what applies. Formatted with the fixture's OWN parsed keys below
# -- never with a hardcoded key.
FOOTCITE_ID_TEMPLATE = "footcite-{key}"


# ---------------------------------------------------------------------------
# Fixture-authored data, parsed from the fixture rather than transcribed.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def bibtex_footcite_gate_dir():
    """Return the path to the bibtex_footcite_render_gate fixture (S03/T01)."""
    return Path(__file__).parent / "fixtures" / "bibtex_footcite_render_gate"


def _parse_bib_titles(bib_text: str) -> dict[str, str]:
    """
    Return ``{entry_key: title}`` parsed from the fixture's ``refs.bib``.

    ``%``-comment lines are stripped first: the fixture's ``refs.bib`` carries
    a header comment block that itself quotes entry titles, which would
    otherwise be mistaken for entries.
    """
    without_comments = "\n".join(
        line for line in bib_text.splitlines() if not line.lstrip().startswith("%")
    )
    titles: dict[str, str] = {}
    for key, body in re.findall(
        r"@\w+\{\s*([^,\s]+)\s*,(.*?)\n\}", without_comments, re.S
    ):
        match = re.search(r'title\s*=\s*"([^"]+)"', body)
        if match:
            titles[key] = match.group(1)
    return titles


def _parse_footcite_sites(rst_text: str) -> list[str]:
    """
    Return the key named by every ``:footcite:`` site in ``index.rst``, one
    entry per citing SITE (so a key cited twice appears twice), in document
    order.

    This module needs its OWN parser: the shared S01/S02 gate's pattern
    ``:cite:([a-z]*):`` does **not** match the colonised footcite role --
    measured against this very fixture, it returns ``[]`` -- because the
    ``cite`` in ``footcite`` is not preceded by a colon. Reusing the shared
    parser here would have silently reported zero sites and degraded every
    count below into a vacuous pass.

    Like the shared gate, this regexes the RAW rst, so a fully-colonised role
    name written inside an rst comment would also count as a site; the fixture
    documents that trap in its own comments and deliberately writes the role
    name without its leading colon in prose.
    """
    return [match.strip() for match in re.findall(r":footcite:`([^`]+)`", rst_text)]


def _parse_handwritten_footnote_names(rst_text: str) -> list[str]:
    """
    Return the name of every hand-written (docutils-authored) auto-labelled
    footnote DEFINITION in ``index.rst``, e.g. ``.. [#plain]`` -> ``"plain"``.

    This is the coexistence subject for SC4: its emitted Typst label must stay
    distinct from every bibtex-generated footcite label. Parsed out of the
    fixture rather than typed in here (house rule), so renaming the footnote in
    the fixture moves the expectation with it.
    """
    return re.findall(r"^\.\.\s+\[#([^\]]+)\]_?\s", rst_text, re.M)


def _parse_handwritten_footnote_bodies(rst_text: str) -> list[str]:
    """
    Return the BODY text of every hand-written auto-labelled footnote
    definition in ``index.rst``, e.g. ``.. [#plain] This is the ...`` ->
    ``"This is the ..."``.

    SC4's PDF-level half needs the body, not the label: a Typst label is a
    compile-time anchor and never appears in extracted PDF text, so the only
    evidence that the docutils-authored footnote actually reached the page
    foot is its prose. Parsed out of the fixture (house rule) so rewording the
    footnote in ``index.rst`` moves the expectation with it.

    Single-line only, which is all the fixture has; the companion guard in
    ``footcite_fixture_data`` fails loudly if the parse ever comes back empty.
    """
    return [
        body.strip()
        for body in re.findall(r"^\.\.\s+\[#[^\]]+\]\s+(\S.*)$", rst_text, re.M)
    ]


def _footnote_label(refid: str) -> str:
    """
    Return the Typst label typsphinx emits for a footnote whose docutils id is
    ``refid``, computed by calling the translator's OWN helper rather than
    spelling the label out as a literal.

    ``translator.py``'s ``visit_footnote_reference`` has exactly one label
    derivation point, ``_namespace_label(docname, f"fn-{refid}")`` -- shared by
    both the definition and the reuse branch -- so reproducing that call here
    is the whole expectation.

    Passing the CLASS itself as ``self`` is safe and is the technique the other
    render-gate modules in this repo already document: ``_namespace_label``
    only calls ``self._sanitize_label(...)``, a ``staticmethod`` resolvable
    through the class object with no instance state.
    """
    return TypstTranslator._namespace_label(TypstTranslator, DOCNAME, f"fn-{refid}")


def _footcite_refid(key: str) -> str:
    """
    Return the docutils footnote id sphinxcontrib-bibtex assigns to the
    footnote it generates for bibtex ``key``.

    Derived, not transcribed: upstream formats :data:`FOOTCITE_ID_TEMPLATE`
    with the entry key and normalises it through docutils' own ``make_id``
    (which is what lowercases ``Smith2020`` into the ``smith2020`` seen in the
    emitted label), then notes the footnote as an explicit target so docutils
    derives the node id from that name.
    """
    return make_id(FOOTCITE_ID_TEMPLATE.format(key=key))


@dataclass
class FootciteFixtureData:
    """The fixture's own authored data: which keys it footcites (per site),
    the title of every ``refs.bib`` entry, and the hand-written footnote's
    name."""

    footcite_sites: list[str]
    titles: dict[str, str]
    handwritten_names: list[str]
    handwritten_bodies: list[str]

    @property
    def cited_keys(self) -> list[str]:
        """The DISTINCT footcited keys, in first-citation order."""
        keys: list[str] = []
        for key in self.footcite_sites:
            if key not in keys:
                keys.append(key)
        return keys

    @property
    def repeated_key(self) -> str:
        """
        The single key the fixture footcites TWICE -- the subject of SC1's
        reuse form.

        ``footcite_fixture_data`` guards that exactly one such key exists, so
        this accessor cannot silently describe the wrong site.
        """
        return [key for key in self.cited_keys if self.footcite_sites.count(key) > 1][0]

    @property
    def uncited_keys(self) -> list[str]:
        """``refs.bib`` keys this fixture never footcites."""
        return [key for key in self.titles if key not in self.cited_keys]

    @property
    def uncited_titles(self) -> list[str]:
        """Titles of ``refs.bib`` entries this fixture never footcites."""
        return [self.titles[key] for key in self.uncited_keys]

    @property
    def handwritten_name(self) -> str:
        """The single hand-written footnote's name (guarded to exist once)."""
        return self.handwritten_names[0]

    @property
    def handwritten_body(self) -> str:
        """The single hand-written footnote's body text (guarded non-empty)."""
        return self.handwritten_bodies[0]

    @property
    def cited_titles(self) -> list[str]:
        """Titles of the footcited entries, in first-citation order."""
        return [self.titles[key] for key in self.cited_keys]


@pytest.fixture(scope="module")
def footcite_fixture_data(bibtex_footcite_gate_dir):
    """
    Parse the fixture's ``refs.bib`` and ``index.rst`` into the authored data
    every assertion below compares against, with VACUOUS-PASS GUARDS so a
    fixture edit that breaks the parse fails loudly right here instead of
    quietly degrading each count into a no-op.

    The guards are the reason this fixture is worth its length: the measured
    failure mode it protects against is precisely the one the shared S01/S02
    gate suffered (a parser that silently matched nothing while the fixture's
    meaning changed underneath it).
    """
    bib_text = (bibtex_footcite_gate_dir / "refs.bib").read_text(encoding="utf-8")
    titles = _parse_bib_titles(bib_text)
    rst_text = (bibtex_footcite_gate_dir / f"{DOCNAME}.rst").read_text(encoding="utf-8")
    footcite_sites = _parse_footcite_sites(rst_text)
    handwritten_names = _parse_handwritten_footnote_names(rst_text)
    handwritten_bodies = _parse_handwritten_footnote_bodies(rst_text)

    assert titles, (
        "Vacuous-pass guard: parsed NO entries out of the fixture's refs.bib, "
        "so every title-presence and title-absence assertion below would "
        "compare against nothing. Did refs.bib's entry formatting change?"
    )
    assert footcite_sites, (
        "Vacuous-pass guard: parsed NO :footcite: site out of the fixture's "
        "index.rst, so SC1's definition/reuse form assertions would iterate an "
        "empty key set and pass vacuously. Note this is the hazard that forced "
        "this module to own its parser: the shared gate's ':cite:([a-z]*):' "
        "pattern does not match the footcite role at all (measured: [])."
    )

    repeated = [key for key in footcite_sites if footcite_sites.count(key) > 1]
    assert len(set(repeated)) == 1, (
        "SC1's REUSE form needs exactly one key cited more than once (the "
        f"repeat site), but the parsed sites {footcite_sites!r} give repeated "
        f"keys {sorted(set(repeated))!r}. With none, the reuse-form assertion "
        "has no subject; with two, 'the' repeated key is ambiguous."
    )

    missing = [key for key in set(footcite_sites) if key not in titles]
    assert not missing, (
        f"Vacuous-pass guard: footcited key(s) {sorted(missing)!r} have no "
        f"entry in the parsed refs.bib titles {sorted(titles)!r}, so the "
        "per-key body assertion could not check anything. Either the rst cites "
        "a key refs.bib does not define (the build would fail) or the bib "
        "parse broke."
    )

    cited_titles = [titles[key] for key in set(footcite_sites)]
    assert len(set(cited_titles)) == len(cited_titles), (
        "The footcited entries must have PAIRWISE DISTINCT titles, otherwise a "
        "per-key footnote-body assertion can be satisfied by the wrong entry's "
        f"body: {sorted(cited_titles)!r}."
    )

    uncited = [key for key in titles if key not in set(footcite_sites)]
    assert uncited, (
        "Vacuous-pass guard: the fixture footcites EVERY refs.bib entry, so "
        "SC5's 'no uncited title reaches index.typ' assertion would iterate an "
        "empty set and pass vacuously. refs.bib must keep at least one entry "
        "that is never cited (Nobody2021 is that entry by design)."
    )

    assert len(handwritten_names) == 1, (
        "SC4's coexistence subject is the fixture's single HAND-WRITTEN "
        "docutils footnote definition, but parsed "
        f"{handwritten_names!r} from index.rst. Without exactly one, the "
        "distinct-label assertion has either no docutils-authored label to "
        "compare against or an ambiguous one."
    )

    assert len(handwritten_bodies) == len(handwritten_names) and all(
        handwritten_bodies
    ), (
        "Vacuous-pass guard: parsed "
        f"{handwritten_bodies!r} as the hand-written footnote BODIES against "
        f"names {handwritten_names!r}. SC4's PDF-level half searches extracted "
        "page text for that body (a Typst label never appears in a PDF), so an "
        "empty or mismatched parse would make it assert against the empty "
        "string -- which every document trivially contains."
    )

    return FootciteFixtureData(
        footcite_sites=footcite_sites,
        titles=titles,
        handwritten_names=handwritten_names,
        handwritten_bodies=handwritten_bodies,
    )


# ---------------------------------------------------------------------------
# Real builds of the fixture, one subprocess each, module-scoped.
#
# Builds by BUILDERNAME/strictness, following S01's pattern:
#   * -b typst      -> the .typ-level form, grid and label assertions
#   * -b typst -W   -> SC5's strict-build half (warnings-as-errors)
#   * -b typstpdf   -> S03/T03's compiled-PDF half ONLY (typst-py + pypdf)
#
# The first two use `-b typst` rather than `-b typstpdf`, so the whole
# `.typ`-level half of this module still runs when typst-py / pypdf are
# absent; the `typstpdf` fixture lives behind its own skipif so a machine
# without those two SKIPS the PDF class rather than erroring it.
# ---------------------------------------------------------------------------


def _run_sphinx_build(
    source_dir: Path,
    build_dir: Path,
    extra_args: tuple[str, ...] = (),
    buildername: str = "typst",
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <buildername>`` (plus ``extra_args``) as a
    subprocess. ``buildername`` defaults to ``typst``; only S03/T03's
    compiled-PDF fixture passes ``typstpdf``.

    Invoked as ``sys.executable -m sphinx`` -- never ``uv run sphinx-build``
    and never a bare ``sphinx-build`` -- which is the NixOS PATH-shadowing
    hazard every render-gate module in this project restates. Under ``uv run``
    this resolves to the current venv's python, so ``import typsphinx`` binds
    to this checkout's (or worktree's) editable copy rather than another
    tree's.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            buildername,
            *extra_args,
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


@dataclass
class FootciteGateBuild:
    """One real build of the footcite fixture, captured once per module."""

    result: subprocess.CompletedProcess
    build_dir: Path

    def read_content_typ(self) -> str:
        """
        Return the text of the emitted CONTENT ``.typ`` (never ``master.typ``),
        failing with an ``AssertionError`` that names the missing artifact and
        quotes the build's own output rather than letting a caller hit
        ``FileNotFoundError``.
        """
        path = self.build_dir / CONTENT_TYP
        if not path.exists():
            raise AssertionError(
                f"{CONTENT_TYP} was never emitted (missing artifact) -- build "
                f"returncode={self.result.returncode}\n"
                f"stdout: {self.result.stdout}\nstderr: {self.result.stderr}"
            )
        return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def footcite_gate_build(bibtex_footcite_gate_dir, tmp_path_factory):
    """
    Build the fixture with ``-b typst`` EXACTLY ONCE for the whole module.

    Asserts a clean exit here: this gate is green on arrival, so a non-zero
    build IS the regression the module exists to catch, and reporting it once
    in the fixture is clearer than letting it surface as several unrelated
    assertion failures.
    """
    build_dir = tmp_path_factory.mktemp("footcite_gate_typ") / "_build"
    result = _run_sphinx_build(bibtex_footcite_gate_dir, build_dir)
    assert result.returncode == 0, (
        "sphinx-build -b typst over the footcite fixture must succeed (this "
        "gate locks measured-working behaviour and is green on arrival)\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return FootciteGateBuild(result=result, build_dir=build_dir)


@pytest.fixture(scope="module")
def footcite_gate_strict_build(bibtex_footcite_gate_dir, tmp_path_factory):
    """
    Build the fixture with ``-b typst -W`` (warnings-as-errors) EXACTLY ONCE,
    for SC5's strict half -- a SEPARATE build directory from
    ``footcite_gate_build`` so neither can mask the other through an
    incremental-rebuild cache.

    Deliberately does NOT assert the exit code: SC5's own test owns that
    assertion, so a future regression is reported as a named test failure
    rather than as a fixture error. Nor does it match any warning TEXT --
    Sphinx's messages are localised (this project's dev shell passes the
    host's ``LANG`` through), so ``-W``'s exit code is the only
    locale-independent evidence of "zero warnings" and is what SC5 uses.
    """
    build_dir = tmp_path_factory.mktemp("footcite_gate_typ_strict") / "_build"
    result = _run_sphinx_build(bibtex_footcite_gate_dir, build_dir, extra_args=("-W",))
    return FootciteGateBuild(result=result, build_dir=build_dir)


# ---------------------------------------------------------------------------
# Emitted-markup helpers.
# ---------------------------------------------------------------------------


def _definition_marker(label: str) -> str:
    """
    Return the tail of the label-attached footnote DEFINITION form for
    ``label``: the ``}) <label>]`` closing of ``[#footnote({...}) <label>]``.

    Counting this tail rather than the whole form is what makes "exactly one
    definition per key" checkable without brace-matching: the opening
    ``[#footnote({`` carries no label, so only this tail identifies WHICH
    footnote a definition belongs to. It also cannot be confused with the
    reuse form, which emits no ``}) <`` at all.
    """
    return f"}}) <{label}>]"


def _reuse_marker(label: str) -> str:
    """Return the bare REUSE form for ``label``: ``footnote(<label>)``."""
    return f"footnote(<{label}>)"


def _definition_body(content_typ: str, label: str) -> str:
    """
    Return the body text inside ``label``'s footnote DEFINITION form.

    Spans from the ``[#footnote({`` opening nearest BEFORE the definition tail
    to that tail. Asserts there is exactly one such definition and that the
    span contains no further label attachment -- a nested or mis-spanned
    extraction would otherwise let one entry's body satisfy another entry's
    assertion.
    """
    tail = _definition_marker(label)
    assert content_typ.count(tail) == 1, (
        f"Expected exactly one footnote DEFINITION form for label {label!r} in "
        f"{CONTENT_TYP}, found {content_typ.count(tail)} occurrences of "
        f"{tail!r}; cannot extract its body unambiguously."
    )
    tail_at = content_typ.index(tail)
    opening = "[#footnote({"
    open_at = content_typ.rfind(opening, 0, tail_at)
    assert open_at != -1, (
        f"Found the definition tail {tail!r} but no preceding {opening!r} "
        "opening, so the emitted form is not the documented bracket-wrapped "
        "definition shape [#footnote({...}) <label>]."
    )
    body = content_typ[open_at + len(opening) : tail_at]
    assert "}) <" not in body, (
        f"The extracted definition body for {label!r} contains another label "
        "attachment, so the span crossed a neighbouring footnote and the body "
        f"assertion would be meaningless: {body!r}"
    )
    return body


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required to resolve :footcite: sites",
)
class TestFootciteFootnoteForms:
    """
    SC1: a footcited key's FIRST site emits the label-attached definition form
    carrying that key's formatted body, and a repeat site emits the bare reuse
    form -- exactly one definition per cited key, never two.
    """

    def test_first_site_emits_the_definition_form_with_the_entry_body(
        self, footcite_gate_build, footcite_fixture_data
    ):
        """
        Each footcited key emits EXACTLY ONE definition form, attached to the
        label the translator's own ``_namespace_label`` computes for that key's
        upstream refid, and that definition's body carries that key's
        ``refs.bib`` title.

        "Exactly one" is the load-bearing half: a second definition for one key
        would mean the same footnote body is emitted twice, i.e. a doubled
        entry at the page foot.
        """
        content_typ = footcite_gate_build.read_content_typ()
        for key in footcite_fixture_data.cited_keys:
            label = _footnote_label(_footcite_refid(key))
            tail = _definition_marker(label)
            assert content_typ.count(tail) == 1, (
                f"Footcited key {key!r} must emit EXACTLY ONE footnote "
                f"definition form -- the bracket-wrapped, label-attached "
                f"[#footnote({{...}}) <{label}>] shape, whose tail is {tail!r} "
                f"-- but {CONTENT_TYP} carries {content_typ.count(tail)}. Zero "
                "means footbibliography stopped routing through the footnote "
                "path (or the label convention moved); two or more means the "
                "entry's body is emitted twice and the page foot shows it "
                "doubled."
            )
            title = footcite_fixture_data.titles[key]
            body = _definition_body(content_typ, label)
            assert title in body, (
                f"The footnote definition attached to {label!r} must carry "
                f"footcited key {key!r}'s own formatted body, but its "
                f"refs.bib title {title!r} is not inside the emitted body: "
                f"{body!r}"
            )

    def test_repeat_site_emits_the_bare_reuse_form(
        self, footcite_gate_build, footcite_fixture_data
    ):
        """
        The key cited twice emits the bare ``footnote(<label>)`` reuse form
        exactly once -- one reuse per repeat site -- while every
        singly-cited key emits no reuse form at all.
        """
        content_typ = footcite_gate_build.read_content_typ()
        for key in footcite_fixture_data.cited_keys:
            label = _footnote_label(_footcite_refid(key))
            expected_reuses = footcite_fixture_data.footcite_sites.count(key) - 1
            reuse = _reuse_marker(label)
            assert content_typ.count(reuse) == expected_reuses, (
                f"Footcited key {key!r} has "
                f"{footcite_fixture_data.footcite_sites.count(key)} site(s) in "
                f"index.rst, so it must emit {expected_reuses} bare reuse "
                f"form(s) {reuse!r} (every site after the first), but "
                f"{CONTENT_TYP} carries {content_typ.count(reuse)}. A missing "
                "reuse means the repeat site emitted a second definition (or "
                "nothing); an unexpected one means a single-site key reused a "
                "label it never defined."
            )

        # Stated positively as well, so the repeat subject is named rather than
        # only implied by the per-key loop above.
        repeated_label = _footnote_label(
            _footcite_refid(footcite_fixture_data.repeated_key)
        )
        assert content_typ.count(_reuse_marker(repeated_label)) == 1, (
            "The fixture's repeated footcite key "
            f"{footcite_fixture_data.repeated_key!r} must emit exactly one "
            f"bare reuse form {_reuse_marker(repeated_label)!r}."
        )


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required to resolve :footcite: sites",
)
class TestFootbibliographyEmitsNoGrid:
    """SC2: footbibliography does not route through the bibliography-GRID
    path."""

    def test_content_typ_contains_no_grid_call(self, footcite_gate_build):
        """
        ``index.typ`` carries ZERO ``grid(`` calls.

        This is the executable proof that ``.. footbibliography::`` renders via
        the footnote path and not via the two-column definition grid that
        ``.. bibliography::`` produces. Measured 0 at plan time.
        """
        content_typ = footcite_gate_build.read_content_typ()
        assert content_typ.count("grid(") == 0, (
            f"{CONTENT_TYP} must contain ZERO 'grid(' calls, but found "
            f"{content_typ.count('grid(')}. Either the fixture gained a "
            ".. bibliography:: directive -- forbidden in this fixture, the "
            "grid and COMBINED forms belong to S04/S06 -- or "
            ".. footbibliography:: started rendering as a bibliography grid "
            "instead of as real Typst footnotes, which is exactly the "
            "regression this gate exists to catch."
        )


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required to resolve :footcite: sites",
)
class TestHandwrittenAndGeneratedFootnotesCoexist:
    """SC4: the docutils-authored footnote and the bibtex-generated ones all
    reach the output under pairwise DISTINCT labels."""

    def test_all_footnote_labels_are_distinct_and_present(
        self, footcite_gate_build, footcite_fixture_data
    ):
        """
        The hand-written footnote's label and every footcite label are pairwise
        distinct AND all present in ``index.typ``.

        Distinctness alone would pass vacuously if a label were missing, and
        presence alone would pass if two namespaces collided onto one label, so
        both halves are asserted together. Each label is computed through
        ``_namespace_label``, never written out as a literal.
        """
        content_typ = footcite_gate_build.read_content_typ()
        handwritten_label = _footnote_label(
            make_id(footcite_fixture_data.handwritten_name)
        )
        footcite_labels = {
            key: _footnote_label(_footcite_refid(key))
            for key in footcite_fixture_data.cited_keys
        }

        all_labels = {"<handwritten>": handwritten_label, **footcite_labels}
        assert len(set(all_labels.values())) == len(all_labels), (
            "The docutils-authored footnote label and the bibtex-generated "
            "footcite labels must be PAIRWISE DISTINCT -- a collision would "
            "make one footnote's body answer for another's, and a duplicate "
            "Typst label is a hard compile abort. Computed: "
            f"{all_labels!r}"
        )
        for owner, label in all_labels.items():
            assert f"<{label}>" in content_typ, (
                f"The footnote label {label!r} for {owner} is absent from "
                f"{CONTENT_TYP}, so the distinctness check above proves "
                "nothing about it. Either that footnote stopped rendering or "
                "the label-namespacing convention moved."
            )


@pytest.mark.skipif(
    not BIBTEX_AVAILABLE,
    reason="sphinxcontrib-bibtex is required to resolve :footcite: sites",
)
class TestUncitedEntriesNeverReachOutput:
    """
    SC5: a strict build succeeds and no UNCITED ``refs.bib`` entry reaches
    ``index.typ``.

    Together these pin D-09 -- ``visit_footnote``'s documented silent drop of
    an unreferenced footnote definition (``typsphinx/translator.py``,
    ``visit_footnote``) -- as structurally UNREACHABLE via
    footbibliography: upstream omits uncited entries BEFORE populating the
    footnote container, so typsphinx never receives an unreferenced definition
    to drop in the first place.
    """

    def test_strict_build_succeeds_with_no_warnings(self, footcite_gate_strict_build):
        """
        ``sphinx-build -b typst -W`` over the fixture exits 0.

        Under ``-W`` any warning is promoted to an error, so exit 0 IS the
        zero-warning evidence -- and unlike grepping for "WARNING" it holds
        under a non-English ``LANG``. Measured exit 0 / zero warnings at plan
        time.
        """
        result = footcite_gate_strict_build.result
        assert result.returncode == 0, (
            "A strict (-W, warnings-as-errors) build of the footcite fixture "
            f"must succeed, but exited {result.returncode}. Under -W this "
            "means the build emitted at least one warning -- e.g. typsphinx "
            "logging a dangling footnote reference, or upstream starting to "
            "hand the translator an unreferenced footnote definition.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_uncited_titles_are_absent_from_content_typ(
        self, footcite_gate_build, footcite_fixture_data
    ):
        """
        No title of a ``refs.bib`` entry the fixture never footcites appears in
        ``index.typ``.

        Written as ``assert title not in content_typ`` rather than as a
        ``grep -c`` over the file, so the failure names the offending title and
        so the check cannot be satisfied by a shell-quoting accident. It
        catches an upstream change in EITHER direction: an upstream that starts
        emitting ALL entries into the footnote container fails here (an uncited
        title reaches the output), while an upstream that stops emitting cited
        ones fails SC1 above (a cited key loses its definition form). The
        companion ``footcite_fixture_data`` guard refuses to run at all if the
        fixture ever cites every entry, which would make this a no-op.
        """
        content_typ = footcite_gate_build.read_content_typ()
        for key in footcite_fixture_data.uncited_keys:
            title = footcite_fixture_data.titles[key]
            assert title not in content_typ, (
                f"refs.bib entry {key!r} is never footcited in the fixture, so "
                f"its title {title!r} must NOT appear in {CONTENT_TYP} -- but "
                "it does. That means sphinxcontrib-bibtex now hands the "
                "footnote container entries nobody cited, which would make "
                "the translator's documented silent drop of an unreferenced "
                "footnote definition (D-09) reachable through "
                "footbibliography for the first time."
            )


# ---------------------------------------------------------------------------
# S03/T03: the compiled-PDF half (SC3, plus SC4's and SC5's PDF counterparts).
#
# Kept apart from the `-b typst` build above on purpose: a `.typ`-level count
# cannot see a Typst-LEVEL doubling (a footnote the compiler places twice, or
# a reuse marker the compiler expands into a second body), so the milestone's
# load-bearing "exactly once" property has to be measured on the artifact a
# reader actually opens. Its own build fixture and its own skipif mean a
# machine without typst-py / pypdf SKIPS this class while the whole `.typ`
# half above still runs.
# ---------------------------------------------------------------------------


def _normalise_whitespace(text: str) -> str:
    """
    Collapse every whitespace run to a single space.

    Mandatory before counting a title in PDF-extracted text: Typst breaks
    lines inside a justified footnote paragraph and pypdf reports those breaks
    literally, so an un-normalised ``str.count()`` of a multi-word title
    silently reads 0 and the assertion fails for a reason that has nothing to
    do with the contract.
    """
    return re.sub(r"\s+", " ", text)


def _pdf_text(pdf_path: Path) -> str:
    """Return whitespace-normalised text extracted from every page, joined."""
    reader = pypdf.PdfReader(io.BytesIO(pdf_path.read_bytes()))
    return _normalise_whitespace(" ".join(page.extract_text() for page in reader.pages))


@pytest.fixture(scope="module")
def footcite_gate_pdf_build(bibtex_footcite_gate_dir, tmp_path_factory):
    """
    Compile the fixture through ``-b typstpdf`` EXACTLY ONCE for the whole
    module, for the compiled-PDF half only.

    Declared at module level rather than inside the PDF class: a class-scoped
    fixture defined in a class body and depending on these broader-scoped
    fixtures trips pytest's own ``assert not self._finalizers`` internal check
    (observed in the shared S01 gate as a fixture ERROR rather than a test
    failure, on pytest 8 / python 3.14).
    """
    build_dir = tmp_path_factory.mktemp("footcite_gate_pdf") / "_build"
    result = _run_sphinx_build(
        bibtex_footcite_gate_dir, build_dir, buildername="typstpdf"
    )
    assert result.returncode == 0, (
        "sphinx-build -b typstpdf over the footcite fixture must succeed "
        "(this gate is green on arrival)\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return FootciteGateBuild(result=result, build_dir=build_dir)


@pytest.fixture(scope="module")
def footcite_gate_pdf_single(footcite_gate_pdf_build):
    """
    Return the whitespace-normalised text of the fixture's single compiled
    PDF, extracting it ONCE for the whole class.

    The PDF is located by glob rather than by its filename: the fixture's
    ``typst_documents`` target owns that name, and asserting there is EXACTLY
    one compiled PDF is itself worth checking -- the fixture declares a single
    master, so a second PDF would mean the two-layer split or the master
    registry changed shape under this gate.
    """
    pdfs = sorted(footcite_gate_pdf_build.build_dir.glob("*.pdf"))
    assert len(pdfs) == 1, (
        "Expected exactly one compiled PDF for this single-master fixture, "
        f"found {[p.name for p in pdfs]} -- build "
        f"returncode={footcite_gate_pdf_build.result.returncode}\n"
        f"stderr: {footcite_gate_pdf_build.result.stderr}"
    )
    return _pdf_text(pdfs[0])


@pytest.mark.skipif(
    not (BIBTEX_AVAILABLE and TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="sphinxcontrib-bibtex, typst-py and pypdf are all required for the "
    "footcite render gate's compiled-PDF half",
)
class TestFootciteRenderGateCompiledPdf:
    """
    SC3 -- the milestone's load-bearing property, measured on the COMPILED
    PDF.

    Every assertion here counts the entry TITLE, never a label token and never
    a footnote MARKER: markers are bare numerals (``1``, ``2``) that collide
    with page numbers and section numbers in extracted text, and Typst labels
    are compile-time anchors that never appear in a PDF at all.

    Note how this differs from the shared citation gate: there the label
    appears at least twice by design (citing marker plus bibliography row),
    whereas in a footnote-rendered document there is NO grid row, so each
    entry's body appears exactly once -- at the page foot.
    """

    def test_cited_entry_appears_exactly_once_in_pdf(
        self, footcite_gate_pdf_single, footcite_fixture_data
    ):
        """
        SC3: each footcited entry's title appears EXACTLY ONCE in the compiled
        PDF's extracted text.

        Exactly once in BOTH directions. Two or more means the reader sees the
        same reference printed twice at the page foot -- which is precisely
        what a second definition form, or a Typst-level expansion of the reuse
        marker, would produce, and what no ``.typ``-level count can detect.
        Zero means the entry never reached the page even though its markup was
        emitted.
        """
        text = footcite_gate_pdf_single
        for key, raw_title in zip(
            footcite_fixture_data.cited_keys,
            footcite_fixture_data.cited_titles,
            strict=True,
        ):
            title = _normalise_whitespace(raw_title)
            occurrences = text.count(title)
            assert occurrences == 1, (
                f"SC3: footcited entry title {title!r} (key {key!r}) must "
                f"appear EXACTLY ONCE in the compiled PDF, found "
                f"{occurrences}. More than one means the footnote body is "
                "doubled at the page foot (a second definition form, or the "
                "reuse marker expanding into a body); zero means the entry "
                "never reached the page. Note the fixture cites this key "
                f"{footcite_fixture_data.footcite_sites.count(key)} time(s) "
                "-- repeat sites must add a MARKER, never another body."
                f"\nExtracted text:\n{text}"
            )

    def test_uncited_entry_appears_zero_times_in_pdf(
        self, footcite_gate_pdf_single, footcite_fixture_data
    ):
        """
        SC5's PDF-level counterpart: no title of a ``refs.bib`` entry the
        fixture never footcites appears in the compiled PDF at all.

        This pins upstream's own filtering from the reader's side: because
        sphinxcontrib-bibtex omits uncited entries BEFORE populating the
        footnote container, typsphinx is never handed an unreferenced footnote
        definition and so its documented silent drop of one (D-09,
        ``visit_footnote``) stays structurally unreachable through
        footbibliography. If upstream ever starts emitting every entry, this
        fails here rather than quietly changing what the PDF shows.
        """
        text = footcite_gate_pdf_single
        for key in footcite_fixture_data.uncited_keys:
            title = _normalise_whitespace(footcite_fixture_data.titles[key])
            occurrences = text.count(title)
            assert occurrences == 0, (
                f"refs.bib entry {key!r} is never footcited in this fixture, "
                f"so its title {title!r} must appear ZERO times in the "
                f"compiled PDF, found {occurrences}. That would mean upstream "
                "now hands the footnote container entries nobody cited, "
                "making D-09's silent-drop path reachable via "
                f"footbibliography for the first time.\nExtracted text:\n{text}"
            )

    def test_handwritten_footnote_body_reaches_the_page(
        self, footcite_gate_pdf_single, footcite_fixture_data
    ):
        """
        SC4 at PDF level: the hand-written docutils footnote's own prose
        reaches the page foot alongside the generated ones.

        The ``.typ``-level half of SC4 proves the two namespaces produce
        DISTINCT labels; distinct labels, however, would still be satisfied if
        the docutils-authored footnote were emitted and then dropped by the
        Typst compiler. Counting its body in extracted text is what closes
        that gap -- and it must be the body, since a Typst label never appears
        in a PDF.
        """
        body = _normalise_whitespace(footcite_fixture_data.handwritten_body)
        occurrences = footcite_gate_pdf_single.count(body)
        assert occurrences == 1, (
            "SC4 (PDF level): the hand-written footnote's body "
            f"{body!r} must appear exactly once in the compiled PDF, found "
            f"{occurrences}. Zero means the docutils-authored footnote was "
            "dropped even though its label was emitted -- coexistence with "
            "the bibtex-generated footnotes would then hold only in the .typ "
            "text and not on the page. More than one means it is duplicated "
            f"at the page foot.\nExtracted text:\n{footcite_gate_pdf_single}"
        )
