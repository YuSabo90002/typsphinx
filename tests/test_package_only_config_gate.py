"""
GATE-01: real-compile config->output regression gate for the Typst-Universe
package-alone path (Phase 22.2, CONF-02 / CONF-03).

Plans ``22.2-03`` and ``22.2-04`` fixed five defect classes on this path --
BUG-A (a package-alone master importing a shared ``_template.typ`` the
builder never writes), BUG-B (an unrequested ``date`` argument back-filled
into the package function call), BUG-C (``typst_authors`` rendered as a
quoted string rather than an array of dictionaries), BUG-E (auto-derived
Sphinx metadata winning over an explicit, colliding
``typst_template_function["params"]`` value), and BUG-F (the four essential
``@preview`` imports missing on the package-only path). Before this plan,
the only tests covering these configuration values asserted that they were
*registered* (``app.add_config_value(...)``) or that their name appeared in
the documentation -- both stay green whether or not the feature actually
works. CONF-03 requires assertions that a config value CHANGES THE EMITTED
OUTPUT, and D-09 requires a real ``typst.compile()`` on the package-alone
path specifically (this is a distinct compile-root basis from the
default-template and custom-template paths, which are already exercised
elsewhere in this suite).

``-b typstpdf`` (not ``-b typst``) is the builder driving the primary gate
in this module: it is CONF-02's literal wording, and -- per Phase 22.1 --
``TypstPDFBuilder.finish()`` aggregates every master's compile failure and
raises a single ``sphinx.errors.ExtensionError`` rather than silently
swallowing one, so ``returncode == 0`` is a meaningful, real signal that the
compile actually ran and actually succeeded. The config->output difference
matrix at the bottom of this module uses the faster ``-b typst`` builder
instead, since those tests only need to compare emitted *source* text
between two configurations -- they do not need a compile.

The standing pre-fix-basis failure proof (one test per defect class:
BUG-A, BUG-B, BUG-C) lives in ``TestPreFixBasisFailureProof`` below, not in
this docstring's prose -- reconstructing the pre-fix compile basis from the
POST-fix emitted master keeps the proof meaningful even after the original
buggy code is deleted, mirroring the convention already established by
``tests/test_nested_master_render_gate.py``.

Per D-06, no assertion anywhere in this module matches on the TEXT of a
Typst compiler error message -- only that a real compile raises. The
compiler's exact wording is not a contracted upstream API (Phase 22.3's
WR-02 exists to remove exactly this class of coupling elsewhere in the
suite), so this module must not add to it.
"""

import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

FIXTURES_DIR = Path(__file__).parent / "fixtures"
GATE_FIXTURE_DIR = FIXTURES_DIR / "package_only_config_gate"

# The two candidate "title" strings this fixture's BUG-E test discriminates
# between -- see conf.py's own comment for why they collide on purpose.
EXPLICIT_TITLE = "The Explicitly Configured Title Wins"
METADATA_TITLE = "Config Metadata Title Must Not Leak Into Output"


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard (see tests/test_preview_smoke_gate.py's fuller
    explanation).
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
    closing ``)`` line -- so per-defect assertions search this region in
    isolation rather than the whole document (which could otherwise, e.g.,
    accidentally match "date:" inside a paragraph of prose or a docstring
    reproduced in the body).
    """
    start_match = re.search(r"^#show: \w+\.with\($", text, re.MULTILINE)
    assert start_match, f"Could not locate the show-rule call opening in:\n{text}"
    start = start_match.start()
    end_match = re.search(r"^\)$", text[start:], re.MULTILINE)
    assert end_match, f"Could not locate the show-rule call closing in:\n{text}"
    end = start + end_match.end()
    return text[start:end]


def _load_fixture_conf_values() -> dict:
    """
    Import ``tests/fixtures/package_only_config_gate/conf.py`` as a module
    and return its ``typst_*``-relevant values as a plain dict.

    This is the single source of truth the config->output difference
    matrix below builds variants from -- each variant re-serializes these
    SAME values (via ``repr()``) with exactly one value removed or changed,
    so a variant can never silently drift out of sync with the real,
    committed fixture config.
    """
    spec = importlib.util.spec_from_file_location(
        "package_only_config_gate_conf", GATE_FIXTURE_DIR / "conf.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {
        "project": module.project,
        "author": module.author,
        "release": module.release,
        "copyright": module.copyright,
        "extensions": module.extensions,
        "typst_documents": module.typst_documents,
        "typst_package": module.typst_package,
        "typst_template_mapping": module.typst_template_mapping,
        "typst_authors": module.typst_authors,
        "typst_template_function": module.typst_template_function,
    }


def _write_variant_project(directory: Path, overrides=None, removals=None) -> Path:
    """
    Write a minimally-varied copy of the GATE-01 fixture project into
    ``directory``: the SAME ``index.rst``, and a ``conf.py`` built from the
    real fixture's own config values with ``removals`` deleted and/or
    ``overrides`` applied.

    Returns the directory (now a valid Sphinx source directory) for
    convenience.
    """
    values = _load_fixture_conf_values()
    for key in removals or ():
        values.pop(key, None)
    if overrides:
        values.update(overrides)

    directory.mkdir(parents=True, exist_ok=True)
    lines = [f"{key} = {value!r}" for key, value in values.items()]
    (directory / "conf.py").write_text("\n".join(lines) + "\n", encoding="utf-8")
    shutil.copy2(GATE_FIXTURE_DIR / "index.rst", directory / "index.rst")
    return directory


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the GATE-01 package-alone config gate",
)
class TestPackageOnlyConfigGate:
    """
    Real-compile regression gate proving a Typst-Universe package-alone
    master builds and compiles for real, and that five previously-dead
    configuration values each provably affect the emitted output (rather
    than merely being registered).

    Requirements: CONF-02, CONF-03.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        """
        Build the GATE-01 fixture ONCE via ``-b typstpdf`` (a real compile)
        and share the result across every named per-defect test below --
        one build, one compile, many independent assertions on its output.

        Declared as a ``@staticmethod`` (no ``self``): a class-scoped
        fixture defined as an instance method runs once for the whole
        class but each test method gets its OWN instance, so any state
        written onto ``self`` would not be visible to other tests --
        pytest deprecates (and, under this project's
        ``error::DeprecationWarning`` filter, errors on) exactly that
        shape. This fixture returns its result as a plain value instead of
        mutating instance state, so the staticmethod form is correct, not
        just warning-suppression.
        """
        build_dir = tmp_path_factory.mktemp("package_only_config_gate_build")
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

    def test_bug_a_no_shared_template_reference(self, build):
        """
        The package-alone master imports the package directly and carries
        NO reference to the shared ``_template.typ`` file -- which the
        builder deliberately never writes for this path -- and no such
        file exists on disk in the build output directory.
        """
        text = build["text"]
        assert '#import "@preview/charged-ieee:0.1.4": ieee' in text
        assert "_template.typ" not in text
        assert not (build["build_dir"] / "_template.typ").exists()

    def test_bug_b_no_date_argument_in_show_rule_call(self, build):
        """
        Within the show-rule call region ONLY, no ``date`` argument is
        back-filled, and the ``authors`` argument present is the
        explicitly-configured one, not a back-filled empty tuple.
        """
        region = _show_rule_call_region(build["text"])
        assert "date:" not in region
        assert "authors: (" in region
        assert "authors: (),\n" not in region

    def test_bug_c_authors_are_array_of_dicts_not_a_string(self, build):
        """
        ``typst_authors`` reaches the emitted output as a Typst array whose
        single element is a dictionary keyed by ``name`` (plus the other
        configured detail fields) -- never as a pre-rendered, quoted string.
        """
        text = build["text"]
        assert "authors: (" in text
        assert 'name: "' in text
        assert 'authors: "(' not in text

    def test_bug_e_explicit_title_wins_over_metadata(self, build):
        """
        The EXPLICIT ``typst_template_function["params"]["title"]`` value
        wins over the auto-derived ``project`` -> ``title`` mapping on their
        deliberately-colliding key.
        """
        text = build["text"]
        assert EXPLICIT_TITLE in text
        assert METADATA_TITLE not in text

    def test_bug_f_essential_imports_present_exactly_once(self, build):
        """
        All four essential ``@preview`` imports, plus the codly
        initialisation show-rule, are present -- and each import line
        occurs EXACTLY ONCE -- even though this master takes the
        package-only routing path (no template file import).
        """
        text = build["text"]
        assert text.count("@preview/codly:") == 1
        assert text.count("@preview/codly-languages:") == 1
        assert text.count("@preview/mitex:") == 1
        assert text.count("@preview/gentle-clues:") == 1
        assert "#show: codly-init.with()" in text

    def test_real_compile_produces_valid_pdf(self, build):
        """
        D-09: ``-b typstpdf`` really compiled the package-alone master --
        the build exited 0, and a non-empty, well-formed PDF exists at the
        expected output path. Because ``-b typstpdf`` compiles during the
        build itself (Phase 22.1's D-04 aggregate-and-raise change makes a
        compile failure a non-zero exit, never a silently swallowed one),
        this exit/artifact pair is a genuine real-compile signal, not a
        stand-in for one.
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
    reason="typst-py is required for the GATE-01 pre-fix-basis failure proof",
)
class TestPreFixBasisFailureProof:
    """
    Standing pre-fix-basis failure proof (D-06, D-09): reconstructs each of
    three pre-fix defect shapes FROM the post-fix emitted master (built
    once, shared read-only across all three reconstructions) and proves a
    real ``typst.compile()`` RAISES against each one. This stays meaningful
    after the original buggy code is deleted, because each reconstruction
    is derived mechanically from the current emitted output rather than
    hand-authored to match a historical bug.

    Only ``pytest.raises`` is asserted -- never the exception's message
    text (D-06). Manually weakening any ONE of these three reconstructions
    (e.g. commenting out its single mutation) makes that reconstruction
    compile successfully instead of raising, which turns exactly that one
    test red -- this was confirmed manually while writing this module and
    is recorded in the plan's SUMMARY rather than re-asserted here as a
    standing test (a test that verifies its own absence is not
    expressible).

    Requirements: CONF-02, CONF-03, D-06.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def emitted_master_text(tmp_path_factory):
        """
        Build the GATE-01 fixture ONCE via the faster ``-b typst`` builder
        (no compile needed to obtain the source text these reconstructions
        mutate) and return the emitted master's text.

        ``@staticmethod`` for the same reason as ``TestPackageOnlyConfigGate
        .build`` above: this fixture returns a plain value rather than
        mutating ``self``, so it is correct (not just warning-silencing)
        under this project's ``error::DeprecationWarning`` filter.
        """
        build_dir = tmp_path_factory.mktemp("prefix_basis_source_build")
        result = _run_sphinx_build(GATE_FIXTURE_DIR, build_dir, "typst")
        assert result.returncode == 0, (
            f"sphinx-build -b typst failed:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        typ_path = build_dir / "index.typ"
        assert typ_path.exists()
        return typ_path.read_text(encoding="utf-8")

    def test_bug_a_basis_shared_template_import_raises(
        self, emitted_master_text, tmp_path
    ):
        """
        BUG-A basis: prepend a shared-template import line referencing a
        file that is never written anywhere in this temporary directory.
        Reproduces the pre-fix shape where a package-alone master
        unconditionally imported ``_template.typ``.
        """
        reconstructed = '#import "_template.typ": project\n' + emitted_master_text
        target = tmp_path / "bug_a_basis.typ"
        target.write_text(reconstructed, encoding="utf-8")

        with pytest.raises(Exception):
            typst.compile(str(target), root=str(tmp_path))

    def test_bug_b_basis_unrequested_date_argument_raises(
        self, emitted_master_text, tmp_path
    ):
        """
        BUG-B basis: insert an unrequested ``date`` argument into the
        show-rule call. Reproduces the pre-fix unconditional back-fill of
        ``date`` into a package function that never asked for it.
        """
        lines = emitted_master_text.split("\n")
        opening = [i for i, line in enumerate(lines) if "#show: ieee.with(" in line]
        assert (
            len(opening) == 1
        ), f"Expected exactly one show-rule call opening, found {len(opening)}"
        lines.insert(opening[0] + 1, "  date: none,")
        reconstructed = "\n".join(lines)
        assert "date: none," in reconstructed

        target = tmp_path / "bug_b_basis.typ"
        target.write_text(reconstructed, encoding="utf-8")

        with pytest.raises(Exception):
            typst.compile(str(target), root=str(tmp_path))

    def test_bug_c_basis_authors_as_string_tuple_raises(
        self, emitted_master_text, tmp_path
    ):
        """
        BUG-C basis: replace the authors array-of-dictionaries with a bare
        tuple of author-name strings. Reproduces the pre-fix shape where
        ``typst_authors`` was rendered as (or replaced by) a plain string
        rather than a dict the package's own ``ieee`` function maps over
        reading a ``name`` field -- which fails precisely because a string
        has no such field.
        """
        lines = emitted_master_text.split("\n")
        authors_lines = [
            i for i, line in enumerate(lines) if line.strip().startswith("authors: (")
        ]
        assert len(authors_lines) == 1, (
            f"Expected exactly one authors assignment line, found "
            f"{len(authors_lines)}"
        )
        lines[authors_lines[0]] = '  authors: ("Ada Fixture Researcher",),'
        reconstructed = "\n".join(lines)
        assert 'authors: ("Ada Fixture Researcher",),' in reconstructed

        target = tmp_path / "bug_c_basis.typ"
        target.write_text(reconstructed, encoding="utf-8")

        with pytest.raises(Exception):
            typst.compile(str(target), root=str(tmp_path))


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the GATE-01 config->output difference matrix",
)
class TestConfigOutputDifferenceMatrix:
    """
    D-10 / CONF-03: proves that each configuration value this phase touches
    provably CHANGES THE EMITTED OUTPUT between two configurations -- never
    merely that a value is registered, or that a build succeeds. Each test
    below builds a second, minimally-varied project (derived from the SAME
    real fixture config via ``_write_variant_project``) and asserts a
    concrete difference against the unmodified fixture's own emitted output.

    Uses ``-b typst`` (not ``-b typstpdf``): these tests compare *emitted
    source text*, so a real compile is not needed here -- it is already
    covered by ``TestPackageOnlyConfigGate.test_real_compile_produces_valid_pdf``
    above.

    Requirements: CONF-03, D-10.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def baseline_text(tmp_path_factory):
        build_dir = tmp_path_factory.mktemp("diff_matrix_baseline_build")
        result = _run_sphinx_build(GATE_FIXTURE_DIR, build_dir, "typst")
        assert result.returncode == 0, (
            f"sphinx-build -b typst (baseline) failed:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        typ_path = build_dir / "index.typ"
        assert typ_path.exists()
        return typ_path.read_text(encoding="utf-8")

    def test_removing_package_config_changes_output(self, baseline_text, tmp_path):
        """
        Removing ``typst_package`` changes the emitted output: the package
        import line disappears, and a shared-template import reappears
        (the routing this phase's plan 04 repaired).
        """
        variant_dir = _write_variant_project(
            tmp_path / "no_package_variant", removals=["typst_package"]
        )
        build_dir = tmp_path / "no_package_build"
        result = _run_sphinx_build(variant_dir, build_dir, "typst")
        assert result.returncode == 0, (
            f"sphinx-build -b typst (no-package variant) failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        variant_text = (build_dir / "index.typ").read_text(encoding="utf-8")

        assert '#import "@preview/charged-ieee:0.1.4"' in baseline_text
        assert '#import "@preview/charged-ieee:0.1.4"' not in variant_text

        assert "_template.typ" not in baseline_text
        assert "_template.typ" in variant_text
        assert variant_text != baseline_text

    def test_removing_authors_config_changes_output(self, baseline_text, tmp_path):
        """
        Removing ``typst_authors`` changes the emitted authors value: the
        array-of-dictionaries no longer appears, and (because the package
        path never back-fills a default) no ``authors`` argument is emitted
        at all.
        """
        variant_dir = _write_variant_project(
            tmp_path / "no_authors_variant", removals=["typst_authors"]
        )
        build_dir = tmp_path / "no_authors_build"
        result = _run_sphinx_build(variant_dir, build_dir, "typst")
        assert result.returncode == 0, (
            f"sphinx-build -b typst (no-authors variant) failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        variant_text = (build_dir / "index.typ").read_text(encoding="utf-8")

        baseline_region = _show_rule_call_region(baseline_text)
        variant_region = _show_rule_call_region(variant_text)

        assert "authors: (" in baseline_region
        assert "authors:" not in variant_region
        assert variant_text != baseline_text

    def test_changing_template_function_param_changes_output(
        self, baseline_text, tmp_path
    ):
        """
        Changing one ``typst_template_function["params"]`` value (here:
        ``abstract``) changes THAT value in the emitted call -- proving the
        params dict is not merely accepted but actually threaded through
        to the rendered output.
        """
        original_values = _load_fixture_conf_values()
        original_function = original_values["typst_template_function"]
        new_abstract = (
            "A DELIBERATELY DIFFERENT abstract proving the "
            "typst_template_function params dict changes the emitted "
            "output rather than being silently ignored."
        )
        changed_function = dict(original_function)
        changed_function["params"] = dict(original_function["params"])
        changed_function["params"]["abstract"] = new_abstract
        assert (
            changed_function["params"]["abstract"]
            != original_function["params"]["abstract"]
        )

        variant_dir = _write_variant_project(
            tmp_path / "changed_param_variant",
            overrides={"typst_template_function": changed_function},
        )
        build_dir = tmp_path / "changed_param_build"
        result = _run_sphinx_build(variant_dir, build_dir, "typst")
        assert result.returncode == 0, (
            f"sphinx-build -b typst (changed-param variant) failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        variant_text = (build_dir / "index.typ").read_text(encoding="utf-8")

        assert new_abstract in variant_text
        assert new_abstract not in baseline_text
        assert original_function["params"]["abstract"] in baseline_text
        assert original_function["params"]["abstract"] not in variant_text
