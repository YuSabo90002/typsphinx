"""
CONF-11 / D-B / D-D: real-compile regression gate for the declared-params
exclusivity rule (Phase 45.1, plan 01).

Before this plan, ``TemplateEngine.render()`` merged an auto-derived
parameter set (title/authors/date, the ``typst_elements`` allowlist, the
``toctree_*`` extraction) with an explicit ``typst_template_function["params"]``
dict via an ADDITIVE UNION (``all_params.update(params)`` then
``all_params.update(self.typst_template_params)``) -- the auto-derived set
was the fallback and ``params`` merely won on a key collision. This made a
template declaring NO named parameters at all impossible to use: the
auto-derived ``title``/``authors``/``date`` always arrived and aborted the
compile with ``TypstError: unexpected argument: ...``.

D-B replaces the union with EXCLUSIVE, wholesale replacement: when
``params`` is declared, ONLY those keys are passed -- the auto-derived
remainder is discarded entirely, not merged. D-D makes the predicate the
PRESENCE of the ``params`` key, not its emptiness, so ``params: {}`` means
"pass nothing" and is distinguishable from an absent ``params`` (which still
gets the full auto-derived set).

This module proves the rule end to end on the thinnest possible slice: a
project whose custom template (``tests/fixtures/params_exclusivity_gate/
zero_params_template/_templates/zero_param.typ``) declares only the
trailing positional ``body`` -- no named parameters whatsoever -- with an
explicitly empty ``typst_template_function["params"]`` dict. The fixture's
``conf.py`` makes every auto-derived source live (a toctree with all three
``toctree_*`` options, both ``ELEMENTS_ALLOWLIST`` keys set), so a leaking
auto-derived key would fail this gate immediately.

Per this project's D-06 convention (restated in
``tests/test_package_only_config_gate.py``'s module docstring), no
assertion in this module matches on the TEXT of a Typst compiler error
message -- only that a real compile raises or succeeds.

The pre-fix RED run this gate was built against is recorded verbatim in
``.planning/phases/45.1-custom-template-parameter-contract-correction/
45.1-GATE-EVIDENCE-01.md`` (D-K, SC#3).

**Phase 45.1 plan 02 extends this module** with the two remaining routes
SC#7 names -- ``typst_package`` and the bundled default -- plus the
partial-``params`` case on the ``typst_template`` route, so the exclusivity
rule is proven on every route the requirement names, not only the
thinnest zero-parameter slice. ``-b typstpdf`` drives the primary,
real-compile assertions below (matching this module's own established
split); ``-b typst`` drives the faster source-text-only assertions (the
byte-identical-repeat-build check and the two "fresh build" acceptance
checks), mirroring ``tests/test_package_only_config_gate.py``'s module
docstring split. ``zero_params_default`` and ``package_params`` both
compile successfully PRE-fix too (see
``.planning/phases/45.1-custom-template-parameter-contract-correction/
45.1-GATE-EVIDENCE-02.md``) -- their RED is STRUCTURAL (the wrong
named-argument set), not a compile fatal, per the amended definition of
RED this project adopted in v0.7.0. ``partial_params_template`` DOES
produce a real pre-fix compile fatal (``TypstError: unexpected argument:
title``), so it keeps the classic RED.

Phase 47 migration (R2, ``47-EXPECTED-STRUCTURE.md``): template application
(the ``#show: <func>.with(...)`` call this module's assertions parse) lives
exclusively on the WRAPPER file since the content/wrapper split, so every
``.typ``/``.pdf``-reading assertion here reads the entry's resolved wrapper
(``master.typ``/``master.pdf``) instead of the docname content file. All
four fixture ``conf.py``s (and the two inline variant configs built at
test time) had their ``typst_documents`` target renamed from the identity
``'index'`` to ``'master'`` -- an identity target is now a BLD-03
self-collision (the wrapper would resolve onto the docname's own content
file and overwrite it with a self-referential ``#include()``, producing
``TypstError: cyclic import``), not merely a stylistic choice. These four
fixture directories are not listed in any Phase 47 plan's ``files_modified``
(a genuine gap in the plan corpus, not an overlap with another plan's
scope), so plan 47-08 de-collides them directly under deviation Rule 3
(blocking) -- see its SUMMARY.
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

FIXTURES_DIR = Path(__file__).parent / "fixtures"
GATE_FIXTURE_DIR = FIXTURES_DIR / "params_exclusivity_gate" / "zero_params_template"

# Plan 02's three remaining-route fixtures.
PARTIAL_PARAMS_FIXTURE_DIR = (
    FIXTURES_DIR / "params_exclusivity_gate" / "partial_params_template"
)
ZERO_PARAMS_DEFAULT_FIXTURE_DIR = (
    FIXTURES_DIR / "params_exclusivity_gate" / "zero_params_default"
)
PACKAGE_PARAMS_FIXTURE_DIR = FIXTURES_DIR / "params_exclusivity_gate" / "package_params"

# Every auto-derived / typst_elements / toctree_* key the pre-fix additive
# union would have emitted for this fixture (see 45.1-GATE-EVIDENCE-01.md's
# verbatim pre-fix `#show:` region) -- none of these may appear as a named
# argument in the post-fix emitted call.
AUTO_DERIVED_KEYS = (
    "title",
    "authors",
    "date",
    "papersize",
    "fontsize",
    "lang",
    "toctree_maxdepth",
    "toctree_numbered",
    "toctree_caption",
)


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never a resolved ``sphinx-build``
    binary), so the exact interpreter/venv running this test is reused --
    matching every other real-compile gate module in this suite.
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


def _show_rule_call_region(text: str) -> str:
    """
    Slice the emitted master text down to JUST the
    ``#show: <func>.with(...)`` call -- from its opening line through its
    closing ``)`` line -- so assertions search this region in isolation.
    """
    start_match = re.search(r"^#show: \w+\.with\($", text, re.MULTILINE)
    assert start_match, f"Could not locate the show-rule call opening in:\n{text}"
    start = start_match.start()
    end_match = re.search(r"^\)$", text[start:], re.MULTILINE)
    assert end_match, f"Could not locate the show-rule call closing in:\n{text}"
    end = start + end_match.end()
    return text[start:end]


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the CONF-11 params exclusivity gate",
)
class TestParamsExclusivityGate:
    """
    Real-compile regression gate proving a zero-named-parameter custom
    template builds and compiles end to end when ``typst_template_function
    ["params"]`` is explicitly set to ``{}``.

    Requirements: CONF-11.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        """
        Build the fixture ONCE via ``-b typstpdf`` (a real compile) and
        share the result across every assertion below.

        ``@staticmethod`` (no ``self``): a class-scoped fixture defined as
        an instance method runs once for the whole class but each test
        method gets its OWN instance, so state written onto ``self`` would
        not be visible to other tests -- this project's
        ``error::DeprecationWarning`` filter errors on exactly that shape.
        This fixture returns its result as a plain value instead.
        """
        build_dir = tmp_path_factory.mktemp("params_exclusivity_gate_build")
        result = _run_sphinx_build(GATE_FIXTURE_DIR, build_dir, "typstpdf")
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        typ_path = build_dir / "master.typ"
        assert typ_path.exists(), (
            f"master.typ (the wrapper) was not emitted:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        return {
            "build_dir": build_dir,
            "result": result,
            "typ_path": typ_path,
            "text": typ_path.read_text(encoding="utf-8"),
            "pdf_path": build_dir / "master.pdf",
        }

    def test_show_rule_call_carries_zero_named_arguments(self, build):
        """
        D-D: with ``params: {}``, the emitted ``#show: project.with(...)``
        call carries NO named arguments at all -- the opening line is
        immediately followed by the closing ``)`` line, not a call with
        empty-valued arguments.
        """
        region = _show_rule_call_region(build["text"])
        lines = region.splitlines()
        assert lines[0] == "#show: project.with("
        assert lines[1] == ")"
        assert len(lines) == 2, f"Expected exactly two lines, got:\n{region}"

    def test_no_auto_derived_key_appears_as_named_argument(self, build):
        """
        D-B: none of the nine auto-derived / typst_elements / toctree_*
        keys this fixture's ``conf.py`` makes live appears as a named
        argument in the show-rule call region -- the exclusive branch
        discards the auto-derived set wholesale rather than merging it.
        """
        region = _show_rule_call_region(build["text"])
        for key in AUTO_DERIVED_KEYS:
            assert f"{key}:" not in region, (
                f"{key!r} leaked into the show-rule call despite an "
                f"explicit empty params dict:\n{region}"
            )

    def test_real_compile_produces_valid_pdf(self, build):
        """
        A zero-named-parameter template really compiles: the build exited
        0, and a non-empty, well-formed PDF exists at the expected path.
        """
        assert build["result"].returncode == 0
        pdf_path = build["pdf_path"]
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0
        with open(pdf_path, "rb") as f:
            magic = f.read(4)
        assert magic == b"%PDF", "Generated file is not a valid PDF"


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the CONF-11 ordering/adjacency gates",
)
class TestParamsExclusivityOrderingAndAdjacency:
    """
    CONF-11 edge cases: ordering (byte-identical repeat builds) and
    adjacency (a declared params key that collides with an auto-derived key
    name emits exactly one argument, the params value).
    """

    def test_two_consecutive_typst_builds_are_byte_identical(self, tmp_path):
        """
        CONF-11 / edge: ordering -- with params present, the emitted
        named-argument sequence is the params dict's own conf.py insertion
        order, and two consecutive ``-b typst`` builds of the same fixture
        emit byte-identical ``.typ`` output.
        """
        build_dir_1 = tmp_path / "build1"
        build_dir_2 = tmp_path / "build2"
        result_1 = _run_sphinx_build(GATE_FIXTURE_DIR, build_dir_1, "typst")
        assert result_1.returncode == 0, (
            f"sphinx-build -b typst (run 1) failed:\n"
            f"stdout: {result_1.stdout}\nstderr: {result_1.stderr}"
        )
        result_2 = _run_sphinx_build(GATE_FIXTURE_DIR, build_dir_2, "typst")
        assert result_2.returncode == 0, (
            f"sphinx-build -b typst (run 2) failed:\n"
            f"stdout: {result_2.stdout}\nstderr: {result_2.stderr}"
        )

        text_1 = (build_dir_1 / "master.typ").read_text(encoding="utf-8")
        text_2 = (build_dir_2 / "master.typ").read_text(encoding="utf-8")
        assert text_1 == text_2

    def test_params_key_colliding_with_auto_derived_name_emits_once(self, tmp_path):
        """
        CONF-11 / edge: adjacency -- a params key whose name equals an
        auto-derived key name (here: "title") produces exactly one emitted
        argument carrying the params value, because the auto-derived set is
        discarded wholesale rather than merged.
        """
        variant_dir = tmp_path / "adjacency_variant"
        variant_dir.mkdir()
        (variant_dir / "index.rst").write_text(
            "Adjacency Gate\n==============\n\nNo toctree, no auto-derived leak.\n",
            encoding="utf-8",
        )
        (variant_dir / "_templates").mkdir()
        (variant_dir / "_templates" / "zero_param.typ").write_text(
            (GATE_FIXTURE_DIR / "_templates" / "zero_param.typ").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        collision_title = "THE ONLY TITLE THAT SHOULD APPEAR"
        conf_lines = [
            "project = 'Adjacency Gate'",
            "author = 'Adjacency Author'",
            "release = '1.0'",
            "extensions = ['typsphinx']",
            "typst_documents = [('index', 'master', project, author)]",
            "typst_template = '_templates/zero_param.typ'",
            "typst_template_function = {"
            "'name': 'project', "
            f"'params': {{'title': {collision_title!r}}}"
            "}",
        ]
        (variant_dir / "conf.py").write_text(
            "\n".join(conf_lines) + "\n", encoding="utf-8"
        )

        build_dir = tmp_path / "adjacency_build"
        result = _run_sphinx_build(variant_dir, build_dir, "typst")
        assert result.returncode == 0, (
            f"sphinx-build -b typst (adjacency variant) failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        text = (build_dir / "master.typ").read_text(encoding="utf-8")
        region = _show_rule_call_region(text)

        assert region.count("title:") == 1
        assert collision_title in region


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the CONF-11 predicate unit checks",
)
class TestParamsSpecifiedPredicate:
    """
    Unit-level checks (no sphinx-build needed) of
    ``TemplateEngine.typst_template_params_specified`` -- the D-D predicate
    itself, in isolation from the render()-stage branch it gates.
    """

    def test_empty_dict_params_is_specified(self):
        from typsphinx.template_engine import TemplateEngine

        engine = TemplateEngine(
            typst_template_function={"name": "project", "params": {}}
        )
        assert engine.typst_template_params_specified is True

    def test_absent_params_key_is_not_specified(self):
        from typsphinx.template_engine import TemplateEngine

        engine = TemplateEngine(typst_template_function={"name": "project"})
        assert engine.typst_template_params_specified is False

    def test_string_form_is_not_specified(self):
        from typsphinx.template_engine import TemplateEngine

        engine = TemplateEngine(typst_template_function="mytpl")
        assert engine.typst_template_params_specified is False

    def test_none_typst_template_function_is_not_specified(self):
        from typsphinx.template_engine import TemplateEngine

        engine = TemplateEngine()
        assert engine.typst_template_params_specified is False


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the CONF-11 typst_template partial-params gate",
)
class TestPartialParamsTemplateGate:
    """
    Real-compile regression gate proving D-B on the ``typst_template`` route
    with a NON-EMPTY, PARTIAL ``params`` declaration: the fixture's template
    (``partial_params_template/_templates/partial.typ``) declares exactly
    one named parameter, ``subtitle``, plus the trailing positional
    ``body`` -- deliberately no ``title``/``authors``/``date``. Pre-fix,
    this build is a real compile FATAL
    (``TypstError: unexpected argument: title``, recorded verbatim in
    ``45.1-GATE-EVIDENCE-02.md`` section 1) -- the additive union passes
    seven-plus auto-derived/element/toctree arguments into a
    one-parameter template. Post-fix, exactly one named argument
    (``subtitle``) is passed and the build compiles to a valid PDF.

    Requirements: CONF-11.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        """Real compile via ``-b typstpdf`` -- the "it compiles" criterion."""
        build_dir = tmp_path_factory.mktemp("partial_params_template_build")
        result = _run_sphinx_build(PARTIAL_PARAMS_FIXTURE_DIR, build_dir, "typstpdf")
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        typ_path = build_dir / "master.typ"
        assert typ_path.exists(), (
            f"master.typ (the wrapper) was not emitted:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        return {
            "build_dir": build_dir,
            "result": result,
            "typ_path": typ_path,
            "text": typ_path.read_text(encoding="utf-8"),
            "pdf_path": build_dir / "master.pdf",
        }

    def test_show_rule_call_carries_exactly_subtitle(self, build):
        """
        D-B: the emitted ``#show: project.with(...)`` call carries exactly
        ONE named argument, ``subtitle`` -- not the auto-derived
        ``title``/``authors``/``date`` alongside it, and not a merge of
        both.
        """
        region = _show_rule_call_region(build["text"])
        lines = region.splitlines()
        assert lines[0] == "#show: project.with("
        assert lines[1] == '  subtitle: "A Gate Subtitle",'
        assert lines[2] == ")"
        assert len(lines) == 3, f"Expected exactly three lines, got:\n{region}"

    def test_auto_derived_and_element_keys_are_absent(self, build):
        """
        D-B: ``title``, ``authors``, ``date``, ``papersize``,
        ``toctree_maxdepth`` and ``toctree_caption`` are each absent as
        named arguments -- every one of them WOULD have been live on this
        fixture's pre-fix additive union (see ``45.1-GATE-EVIDENCE-02.md``
        section 1's verbatim pre-fix ``#show:`` region).
        """
        region = _show_rule_call_region(build["text"])
        for key in (
            "title",
            "authors",
            "date",
            "papersize",
            "toctree_maxdepth",
            "toctree_caption",
        ):
            # Anchored to a line's own named-argument position (optional
            # leading whitespace, then the key, then ":") rather than a bare
            # substring check -- "title:" is a substring of the legitimately
            # emitted "subtitle:", so a plain `in` check would false-positive
            # on this fixture's own declared key.
            assert not re.search(rf"(?m)^\s*{re.escape(key)}:", region), (
                f"{key!r} leaked into the show-rule call despite a "
                f"partial, single-key params dict:\n{region}"
            )

    def test_real_compile_produces_valid_pdf(self, build):
        """
        The one-parameter template really compiles: the build exited 0,
        and a non-empty, well-formed PDF exists at the expected path.
        """
        assert build["result"].returncode == 0
        pdf_path = build["pdf_path"]
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0
        with open(pdf_path, "rb") as f:
            magic = f.read(4)
        assert magic == b"%PDF", "Generated file is not a valid PDF"

    def test_two_consecutive_typst_builds_are_byte_identical(self, tmp_path):
        """
        CONF-11 ordering edge: two consecutive ``-b typst`` builds of the
        same fixture, into different output directories, emit
        byte-identical ``master.typ`` (wrapper) files -- the emitted named-argument
        sequence is deterministic (the ``params`` dict's own conf.py
        insertion order), not incidentally order-dependent.
        """
        build_dir_1 = tmp_path / "build1"
        build_dir_2 = tmp_path / "build2"
        result_1 = _run_sphinx_build(PARTIAL_PARAMS_FIXTURE_DIR, build_dir_1, "typst")
        assert result_1.returncode == 0, (
            f"sphinx-build -b typst (run 1) failed:\n"
            f"stdout: {result_1.stdout}\nstderr: {result_1.stderr}"
        )
        result_2 = _run_sphinx_build(PARTIAL_PARAMS_FIXTURE_DIR, build_dir_2, "typst")
        assert result_2.returncode == 0, (
            f"sphinx-build -b typst (run 2) failed:\n"
            f"stdout: {result_2.stdout}\nstderr: {result_2.stderr}"
        )

        text_1 = (build_dir_1 / "master.typ").read_text(encoding="utf-8")
        text_2 = (build_dir_2 / "master.typ").read_text(encoding="utf-8")
        assert text_1 == text_2


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the CONF-11 bundled-default gate",
)
class TestZeroParamsDefaultGate:
    """
    Real-compile regression gate proving D-B/D-D on the BUNDLED-DEFAULT
    route: no ``typst_template`` and no ``typst_package`` are set, so
    ``typsphinx/templates/base.typ``'s inlined ``project()`` function
    (which declares defaults for all nine documented parameters) absorbs
    an empty argument list without complaint. This route's RED is
    STRUCTURAL, not a compile fatal -- pre-fix the emitted call carries
    the FULL nine-key auto-derived set even with ``params: {}`` explicitly
    declared (recorded verbatim in ``45.1-GATE-EVIDENCE-02.md`` section 2);
    post-fix it carries zero named arguments and still compiles, because
    ``base.typ``'s own parameter defaults fill the gap.

    Requirements: CONF-11.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        """Real compile via ``-b typstpdf`` -- the "it compiles" criterion."""
        build_dir = tmp_path_factory.mktemp("zero_params_default_build")
        result = _run_sphinx_build(
            ZERO_PARAMS_DEFAULT_FIXTURE_DIR, build_dir, "typstpdf"
        )
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        typ_path = build_dir / "master.typ"
        assert typ_path.exists(), (
            f"master.typ (the wrapper) was not emitted:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        return {
            "build_dir": build_dir,
            "result": result,
            "typ_path": typ_path,
            "text": typ_path.read_text(encoding="utf-8"),
            "pdf_path": build_dir / "master.pdf",
        }

    def test_show_rule_call_carries_zero_named_arguments(self, build):
        """
        D-D: with ``params: {}`` on the bundled-default route, the emitted
        ``#show: project.with(...)`` call carries NO named arguments at
        all, even though ``base.typ`` would happily accept all nine.
        """
        region = _show_rule_call_region(build["text"])
        lines = region.splitlines()
        assert lines[0] == "#show: project.with("
        assert lines[1] == ")"
        assert len(lines) == 2, f"Expected exactly two lines, got:\n{region}"

    def test_no_auto_derived_key_appears_as_named_argument(self, build):
        """
        D-B: none of the nine auto-derived / typst_elements / toctree_*
        keys this fixture's ``conf.py`` makes live appears as a named
        argument -- the exclusive branch discards the auto-derived set
        wholesale rather than merging it, exactly as on the
        ``zero_params_template`` tracer case (plan 01).
        """
        region = _show_rule_call_region(build["text"])
        for key in AUTO_DERIVED_KEYS:
            assert f"{key}:" not in region, (
                f"{key!r} leaked into the show-rule call despite an "
                f"explicit empty params dict on the bundled-default "
                f"route:\n{region}"
            )

    def test_real_compile_produces_valid_pdf(self, build):
        """
        A zero-named-parameter call against the bundled default really
        compiles: the build exited 0, and a non-empty, well-formed PDF
        exists at the expected path.
        """
        assert build["result"].returncode == 0
        pdf_path = build["pdf_path"]
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0
        with open(pdf_path, "rb") as f:
            magic = f.read(4)
        assert magic == b"%PDF", "Generated file is not a valid PDF"

    def test_fresh_typst_build_emits_show_rule_immediately_closed(self, tmp_path):
        """
        Acceptance criterion (source-text-only, no compile needed): a
        FRESH ``-b typst`` build of ``zero_params_default`` emits a
        ``#show: project.with(`` line immediately followed by a ``)``
        line -- independent of the class-scoped ``build`` fixture above.
        """
        build_dir = tmp_path / "zero_params_default_typst_build"
        result = _run_sphinx_build(ZERO_PARAMS_DEFAULT_FIXTURE_DIR, build_dir, "typst")
        assert result.returncode == 0, (
            f"sphinx-build -b typst failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        text = (build_dir / "master.typ").read_text(encoding="utf-8")
        region = _show_rule_call_region(text)
        lines = region.splitlines()
        assert lines[0] == "#show: project.with("
        assert lines[1] == ")"


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the CONF-11 typst_package gate",
)
class TestPackageParamsGate:
    """
    Real-compile regression gate proving D-B/D-C on the ``typst_package``
    route: ``typst_template_mapping = {"project": "title"}`` supplies an
    auto-derived ``title`` value that ``typst_template_function["params"]``
    does NOT name. This is the fixture that discharges D-C -- the
    package route needs no special-cased code once ``params`` is
    authoritative, because the mapping's output feeds the same
    auto-derived ``params`` dict the exclusive branch discards wholesale.
    This route ALSO compiles cleanly pre-fix (no toctree, and the
    existing D-05 ``if not self.typst_package:`` gate already withholds
    ``authors``/``date``) -- its RED is the STRUCTURAL presence of the
    mapped ``title`` key, recorded verbatim in
    ``45.1-GATE-EVIDENCE-02.md`` section 3.

    Requirements: CONF-11.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        """Real compile via ``-b typstpdf`` -- the "it compiles" criterion."""
        build_dir = tmp_path_factory.mktemp("package_params_build")
        result = _run_sphinx_build(PACKAGE_PARAMS_FIXTURE_DIR, build_dir, "typstpdf")
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        typ_path = build_dir / "master.typ"
        assert typ_path.exists(), (
            f"master.typ (the wrapper) was not emitted:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        return {
            "build_dir": build_dir,
            "result": result,
            "typ_path": typ_path,
            "text": typ_path.read_text(encoding="utf-8"),
            "pdf_path": build_dir / "master.pdf",
        }

    def test_show_rule_call_carries_exactly_declared_keys(self, build):
        """
        D-B/D-C: the emitted ``#show: ieee.with(...)`` call carries
        EXACTLY the two declared ``params`` keys (``abstract``,
        ``paper-size``) and no ``title`` -- the mapping-supplied
        auto-derived ``title`` is discarded wholesale, not merged in
        alongside the declared keys.
        """
        region = _show_rule_call_region(build["text"])
        assert region.count("abstract:") == 1
        assert region.count("paper-size:") == 1
        assert "title:" not in region, (
            f"the typst_template_mapping-supplied 'title' leaked into the "
            f"show-rule call despite a declared params dict that does not "
            f"name it:\n{region}"
        )

    def test_real_compile_produces_valid_pdf(self, build):
        """
        The package-route call with the mapped title withheld really
        compiles (including the real ``@preview/charged-ieee:0.1.4``
        network fetch): the build exited 0, and a non-empty, well-formed
        PDF exists at the expected path.
        """
        assert build["result"].returncode == 0
        pdf_path = build["pdf_path"]
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0
        with open(pdf_path, "rb") as f:
            magic = f.read(4)
        assert magic == b"%PDF", "Generated file is not a valid PDF"

    def test_fresh_typst_build_omits_mapped_title(self, tmp_path):
        """
        Acceptance criterion (source-text-only, no compile needed): a
        FRESH ``-b typst`` build of ``package_params`` emits an
        ``#show: ieee.with(`` region in which ``title`` does not appear
        as a named argument -- independent of the class-scoped ``build``
        fixture above.
        """
        build_dir = tmp_path / "package_params_typst_build"
        result = _run_sphinx_build(PACKAGE_PARAMS_FIXTURE_DIR, build_dir, "typst")
        assert result.returncode == 0, (
            f"sphinx-build -b typst failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        text = (build_dir / "master.typ").read_text(encoding="utf-8")
        region = _show_rule_call_region(text)
        assert region.splitlines()[0] == "#show: ieee.with("
        assert "title:" not in region


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the CONF-11 subset invariant guard",
)
class TestParamsSubsetOfAutoDerivedKeysInvariant:
    """
    The CONF-11 assumption-delta guard for D-B: given a ``params``
    declaration whose key set is a STRICT SUBSET of the bundled default
    template's nine-key auto-derived set (``AUTO_DERIVED_KEYS``), the
    emitted named-argument key set equals the DECLARED ``params`` key set
    EXACTLY -- not a superset padded back out by a merge. This is the
    assertion that goes RED the instant a per-key merge (the pre-45.1-01
    additive union: ``all_params.update(params)`` then
    ``all_params.update(self.typst_template_params)``) is reintroduced --
    such a merge would restore the other seven auto-derived keys around
    this two-key subset instead of discarding them wholesale.

    Uses the bundled-default route (no ``typst_template``/``typst_package``
    set) so the two declared keys, ``papersize`` and ``fontsize``, are
    genuinely a SUBSET of an auto-derivable superset the template itself
    would accept -- unlike ``partial_params_template``'s ``subtitle``,
    which names a key the auto-derived set never produces at all.
    """

    def test_declared_subset_of_autoderived_keys_emits_exactly_that_subset(
        self, tmp_path
    ):
        variant_dir = tmp_path / "subset_invariant_variant"
        variant_dir.mkdir()
        (variant_dir / "index.rst").write_text(
            "Subset Invariant Guard\n=======================\n\n"
            "No toctree; the bundled-default template supplies the "
            "auto-derived key superset directly.\n",
            encoding="utf-8",
        )
        declared_params = {"papersize": "a5", "fontsize": "9pt"}
        assert set(declared_params) < set(AUTO_DERIVED_KEYS), (
            "This test's own premise requires declared_params to be a "
            "STRICT subset of AUTO_DERIVED_KEYS -- update both together "
            "if this ever fails."
        )
        conf_lines = [
            "project = 'Subset Invariant Guard'",
            "author = 'Subset Invariant Author'",
            "release = '1.0'",
            "extensions = ['typsphinx']",
            "typst_documents = [('index', 'master', project, author)]",
            "typst_template_function = {"
            "'name': 'project', "
            f"'params': {declared_params!r}"
            "}",
        ]
        (variant_dir / "conf.py").write_text(
            "\n".join(conf_lines) + "\n", encoding="utf-8"
        )

        build_dir = tmp_path / "subset_invariant_build"
        result = _run_sphinx_build(variant_dir, build_dir, "typst")
        assert result.returncode == 0, (
            f"sphinx-build -b typst (subset invariant variant) failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        text = (build_dir / "master.typ").read_text(encoding="utf-8")
        region = _show_rule_call_region(text)

        emitted_keys = set(re.findall(r"^\s*([\w-]+):", region, re.MULTILINE))
        assert emitted_keys == set(declared_params.keys()), (
            f"Emitted key set {emitted_keys} != declared params key set "
            f"{set(declared_params.keys())} -- an additive union has been "
            f"reintroduced if this assertion fails."
        )
