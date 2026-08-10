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
        typ_path = build_dir / "index.typ"
        assert typ_path.exists(), (
            f"index.typ was not emitted:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        return {
            "build_dir": build_dir,
            "result": result,
            "typ_path": typ_path,
            "text": typ_path.read_text(encoding="utf-8"),
            "pdf_path": build_dir / "index.pdf",
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

        text_1 = (build_dir_1 / "index.typ").read_text(encoding="utf-8")
        text_2 = (build_dir_2 / "index.typ").read_text(encoding="utf-8")
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
            "typst_documents = [('index', 'index', project, author)]",
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
        text = (build_dir / "index.typ").read_text(encoding="utf-8")
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
