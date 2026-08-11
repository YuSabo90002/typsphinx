"""
SC#3 / D-K: the permanent regression lock for the documented custom-template
parameter contract (Phase 45.1, plan 06 closeout).

Complements ``tests/test_params_exclusivity_gate.py`` (CONF-11's exclusivity
branch, when ``typst_template_function["params"]`` IS declared): this module
proves the DEFAULT set (D-A) -- what a custom template receives when
``params`` is deliberately NOT declared. Its fixture
(``tests/fixtures/documented_params_contract_gate/``) is the "Basic
Structure" example published verbatim in
``docs/source/user_guide/templates.rst`` "Standard Parameters" / "Basic
Structure": a custom template declaring exactly the nine published named
parameters plus the trailing positional ``body``, built with
``sphinx-build -b typstpdf`` over a master document that carries BOTH a real
toctree AND a real ``typst_elements`` setting -- SC#1's literal shape.

**Which assertion is RED-proved, and which is a non-regression control.**
Two axes exist for this fixture and they are NOT both RED-proved:

- The **emitted named-argument key-set** assertion
  (``test_emitted_key_set_equals_published_key_set_exactly``, below) IS
  RED-proved. Recorded against the pre-45.1-01 commit
  (``e6d19cfe4c078bf691877090cf6f1b0bd09ee5c0``, the parent of plan 01's
  first code commit ``75ed1d4``, resolved via ``git rev-parse 75ed1d4^``) in
  a detached worktree with its own venv: the explicit ``typst_template``
  route at that SHA still carries the pre-D-I
  ``resolve_template().source == "default"`` guard, so
  ``uses_bundled_default_template()`` returns ``False`` for this fixture and
  ``lang`` never reaches the emitted call -- eight of the nine published
  names, not nine. Full command lines and verbatim pre-fix output are
  recorded in
  ``.planning/phases/45.1-custom-template-parameter-contract-correction/
  45.1-CONTRACT-ENUMERATION.md``.
- The **compile-success** assertion
  (``test_build_succeeds_and_produces_valid_pdf``, below) is a
  **non-regression control**, NOT a RED-proved gate. Every parameter this
  fixture's template declares carries a default, so the pre-fix eight-of-
  nine emission -- missing only ``lang`` -- still compiles cleanly (measured
  exit 0, real PDF produced, same evidence file). A compile-failure RED is
  therefore not available for this specific fixture, and this docstring
  says so rather than transcribing the post-fix green run into a false RED
  claim (D-K, mirroring the distinction Phase 37 drew for its
  corpus-derived signature-width fixture: a real corpus worst case that
  never overflowed either, so its compile assertion served the same
  non-regression role).

Per this project's D-06 convention (restated in
``tests/test_package_only_config_gate.py``'s module docstring), no
assertion in this module matches on the TEXT of a Typst compiler error
message -- only real, structural key-set/compile-success signals.
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
GATE_FIXTURE_DIR = FIXTURES_DIR / "documented_params_contract_gate"

# docs/source/user_guide/templates.rst "Standard Parameters" -- the nine
# published names, matching typsphinx/templates/base.typ:39-50 name for
# name and order for order.
PUBLISHED_PARAM_NAMES = frozenset(
    {
        "title",
        "authors",
        "date",
        "papersize",
        "fontsize",
        "lang",
        "toctree_maxdepth",
        "toctree_numbered",
        "toctree_caption",
    }
)

# The DOC-13 empty edge: with the toctree removed, the three toctree_*
# names drop out and exactly six remain (typst_elements is still set, so
# papersize/fontsize/lang stay live).
NON_TOCTREE_PARAM_NAMES = frozenset(
    {"title", "authors", "date", "papersize", "fontsize", "lang"}
)

TOCTREE_ONLY_PARAM_NAMES = frozenset(
    {"toctree_maxdepth", "toctree_numbered", "toctree_caption"}
)


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never a resolved
    ``sphinx-build`` binary), so the exact interpreter/venv running this
    test is reused -- matching every other real-compile gate module in this
    suite.
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
    closing ``)`` line -- so assertions search this region in isolation
    rather than the whole document.
    """
    start_match = re.search(r"^#show: \w+\.with\($", text, re.MULTILINE)
    assert start_match, f"Could not locate the show-rule call opening in:\n{text}"
    start = start_match.start()
    end_match = re.search(r"^\)$", text[start:], re.MULTILINE)
    assert end_match, f"Could not locate the show-rule call closing in:\n{text}"
    end = start + end_match.end()
    return text[start:end]


def _emitted_named_argument_keys(region: str) -> set:
    """
    Extract the set of named-argument keys from a sliced show-rule call
    region -- one key per line of the form ``  key: value,``.
    """
    return set(re.findall(r"(?m)^\s*([\w-]+):", region))


def _extract_typ_function_param_names(text: str, func_name: str) -> list:
    """
    Extract the ordered parameter name list from a ``#let <func_name>(...)``
    signature in raw Typst source text -- used to prove the fixture
    template's declared parameter list matches
    ``typsphinx/templates/base.typ``'s own signature name for name.

    Only matches named (``key: default``) parameters, in the order they
    appear -- the trailing positional ``body`` is deliberately excluded
    (neither list names it as a "parameter" in the comparison sense).
    """
    pattern = rf"#let {re.escape(func_name)}\(\n(.*?)\n\) = \{{"
    match = re.search(pattern, text, re.DOTALL)
    assert match, f"Could not locate #let {func_name}(...) signature in:\n{text}"
    signature_body = match.group(1)
    return re.findall(r"^\s*([\w-]+):", signature_body, re.MULTILINE)


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the SC#3 documented-contract gate",
)
class TestDocumentedParamsContractGate:
    """
    Real-compile permanent regression gate proving SC#1's literal shape: a
    custom template declaring exactly the nine published parameters,
    over a master carrying both a toctree and a ``typst_elements`` setting,
    built with ``-b typstpdf``.

    Requirements: DOC-13.
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
        build_dir = tmp_path_factory.mktemp("documented_params_contract_gate_build")
        result = _run_sphinx_build(GATE_FIXTURE_DIR, build_dir, "typstpdf")
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        # The WRAPPER file (R2/R3): after the content/wrapper split the
        # template application -- the #show: ...with(...) call this module
        # asserts against -- is the wrapper's, not the content file's.
        typ_path = build_dir / "master.typ"
        assert typ_path.exists(), (
            f"master.typ (wrapper) was not emitted:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        return {
            "build_dir": build_dir,
            "result": result,
            "typ_path": typ_path,
            "text": typ_path.read_text(encoding="utf-8"),
            "pdf_path": build_dir / "master.pdf",
        }

    def test_build_succeeds_and_produces_valid_pdf(self, build):
        """
        Non-regression control (see module docstring -- NOT RED-proved):
        the documented contract's own worked example really compiles. The
        build exited 0, and a non-empty, well-formed PDF exists at the
        expected output path.
        """
        assert build["result"].returncode == 0
        pdf_path = build["pdf_path"]
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0
        with open(pdf_path, "rb") as f:
            magic = f.read(4)
        assert magic == b"%PDF", "Generated file is not a valid PDF"

    def test_emitted_key_set_equals_published_key_set_exactly(self, build):
        """
        SC#2 / SC#3's real proof, RED-proved against the pre-45.1-01 commit
        (see module docstring): the emitted ``#show: project.with(...)``
        call's named-argument key set equals the nine published names --
        SET EQUALITY in both directions on a single ``==`` between two
        sets, so an extra emitted argument and a missing one both fail this
        assertion. A containment check (``issubset``/``issuperset``) alone
        would not catch a leaked, undocumented tenth parameter.
        """
        region = _show_rule_call_region(build["text"])
        emitted_keys = _emitted_named_argument_keys(region)
        assert emitted_keys == PUBLISHED_PARAM_NAMES, (
            f"Emitted key set {emitted_keys} != published key set "
            f"{PUBLISHED_PARAM_NAMES} -- the documented contract and the "
            f"parameters typsphinx actually passes have drifted apart."
        )

    def test_show_rule_call_carries_exactly_nine_named_arguments(self, build):
        """
        A fresh ``-b typst`` build of the fixture emits a
        ``#show: project.with(`` region containing exactly nine named
        arguments -- independent of the class-scoped ``build`` fixture
        above, and independent of the set-equality assertion's own
        counting logic.
        """
        region = _show_rule_call_region(build["text"])
        lines = [line for line in region.splitlines() if line.strip().endswith(",")]
        assert (
            len(lines) == 9
        ), f"Expected exactly nine named-argument lines, got {len(lines)}:\n{region}"

    def test_documented_template_parameter_list_matches_base_typ(self):
        """
        ``_templates/documented.typ``'s parameter list matches
        ``typsphinx/templates/base.typ`` lines 39-50 name for name (and
        order for order), verified by comparing the two extracted name
        lists rather than by reading either file.
        """
        documented_typ = (GATE_FIXTURE_DIR / "_templates" / "documented.typ").read_text(
            encoding="utf-8"
        )
        base_typ = (
            Path(__file__).parent.parent / "typsphinx" / "templates" / "base.typ"
        ).read_text(encoding="utf-8")

        documented_names = _extract_typ_function_param_names(documented_typ, "project")
        base_names = _extract_typ_function_param_names(base_typ, "project")

        assert documented_names == base_names, (
            f"documented.typ's parameter list {documented_names} does not "
            f"match base.typ's {base_names} name for name / order for order."
        )
        assert set(documented_names) == PUBLISHED_PARAM_NAMES


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the SC#3 documented-contract ordering gate",
)
class TestDocumentedParamsContractGateOrdering:
    """
    CONF-11/DOC-13 ordering edge (verification: backstop): the emitted
    named-argument sequence is deterministic across repeated builds of the
    same fixture, and the published contract does not promise a particular
    order -- two consecutive builds of the documented-contract fixture
    emit byte-identical ``.typ`` output.
    """

    def test_two_consecutive_typst_builds_are_byte_identical(self, tmp_path):
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

        # The wrapper (R2), not the content file -- the show-rule call
        # whose argument ordering this test guards lives there.
        text_1 = (build_dir_1 / "master.typ").read_text(encoding="utf-8")
        text_2 = (build_dir_2 / "master.typ").read_text(encoding="utf-8")
        assert text_1 == text_2


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the DOC-13 no-toctree edge gate",
)
class TestDocumentedParamsContractGateNoToctree:
    """
    DOC-13's empty edge: removing the toctree from the fixture's master
    drops exactly the three ``toctree_*`` arguments -- asserted through a
    second, toctree-free build of the SAME template and ``typst_elements``
    configuration, rather than by reasoning about ``extract_toctree_
    options()`` in isolation.

    Requirements: DOC-13.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        """
        Build a toctree-free variant of the fixture: the SAME
        ``_templates/documented.typ`` and the SAME ``typst_elements``
        setting (via a copied ``conf.py``), with an ``index.rst`` that
        carries no toctree directive at all.
        """
        variant_dir = tmp_path_factory.mktemp(
            "documented_params_contract_gate_no_toctree_src"
        )
        (variant_dir / "_templates").mkdir()
        (variant_dir / "_templates" / "documented.typ").write_text(
            (GATE_FIXTURE_DIR / "_templates" / "documented.typ").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        (variant_dir / "conf.py").write_text(
            (GATE_FIXTURE_DIR / "conf.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (variant_dir / "index.rst").write_text(
            "Documented Params Contract Gate No Toctree\n"
            "============================================\n\n"
            "No toctree here -- the DOC-13 empty edge: this is the SAME "
            "template and the SAME typst_elements as the toctree-bearing "
            "fixture, minus the toctree directive.\n",
            encoding="utf-8",
        )

        build_dir = tmp_path_factory.mktemp(
            "documented_params_contract_gate_no_toctree_build"
        )
        result = _run_sphinx_build(variant_dir, build_dir, "typst")
        assert result.returncode == 0, (
            f"sphinx-build -b typst (no-toctree variant) failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        # The WRAPPER file (R2): the variant conf.py (copied from the
        # fixture's own de-collided conf.py) targets "master.typ".
        typ_path = build_dir / "master.typ"
        assert typ_path.exists()
        return {
            "build_dir": build_dir,
            "result": result,
            "typ_path": typ_path,
            "text": typ_path.read_text(encoding="utf-8"),
        }

    def test_emitted_key_set_equals_six_non_toctree_names(self, build):
        """
        With no toctree, the emitted key set equals exactly the six
        non-toctree names -- set equality, both directions.
        """
        region = _show_rule_call_region(build["text"])
        emitted_keys = _emitted_named_argument_keys(region)
        assert emitted_keys == NON_TOCTREE_PARAM_NAMES, (
            f"Emitted key set {emitted_keys} != the six non-toctree names "
            f"{NON_TOCTREE_PARAM_NAMES}."
        )

    def test_no_toctree_keys_present(self, build):
        """
        None of ``toctree_maxdepth``, ``toctree_numbered`` or
        ``toctree_caption`` appears as a named argument once the toctree is
        removed.
        """
        region = _show_rule_call_region(build["text"])
        emitted_keys = _emitted_named_argument_keys(region)
        assert emitted_keys.isdisjoint(TOCTREE_ONLY_PARAM_NAMES), (
            f"A toctree-* key leaked into a toctree-free build: "
            f"{emitted_keys & TOCTREE_ONLY_PARAM_NAMES}"
        )
