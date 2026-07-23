"""
GATE-01: real-compile config->output regression gate for `typst_elements`
`papersize`/`fontsize` pass-through (Phase 26, CONF-04).

Before this phase, `writer.py:207-209` did
``sphinx_metadata.update(typst_elements)`` -- laundering the user's
`typst_elements` dict into the SAME dict that also carried `project`/
`author`/`release`/`copyright`. `map_parameters()`'s narrow
`DEFAULT_PARAMETER_MAPPING` (project/author/release only) then silently
dropped `papersize`/`fontsize` (and, coincidentally, `copyright`) on the
floor -- so a documented
``typst_elements = {"papersize": "us-letter", "fontsize": "20pt"}`` never
took effect in the compiled PDF. This is the same defect class Phase 22.2
fixed for `typst_package`/`typst_authors` (CONF-02/03): registration-only
tests (`tests/test_config.py::test_typst_elements_config`,
`test_custom_typst_elements_config`) stay green whether or not the
feature actually works. CONF-04 requires assertions that a config value
CHANGES THE EMITTED OUTPUT via a real `typst.compile()`, mirroring
``tests/test_package_only_config_gate.py`` (the GATE-01 template named by
ROADMAP.md/STATE.md).

Four standing cases, each a real compile:

  SC#1 (``TestPapersizePositiveGate``): ``papersize`` reaches the
       ``#show: project.with(...)`` region as a QUOTED Typst string
       (D-01) and a real ``-b typstpdf`` build compiles a valid PDF.
  SC#2 (``TestFontsizePositiveGate``): a SEPARATE build proves
       ``fontsize`` reaches that region as an UNQUOTED Typst length
       (D-02, via the ``RawTypst`` marker) -- and never its quoted-string
       form (the double-formatting trap, Pitfall 1) -- and also compiles
       a valid PDF.
  SC#3 (``TestUnknownKeyNegativeGate``): an unrecognized
       ``typst_elements`` key makes ``sphinx-build`` abort (non-zero
       exit) via ``sphinx.errors.ExtensionError`` (D-06/D-07), never
       silently dropped or passed through as an undeclared kwarg.
  SC#4 (folded into ``TestPapersizePositiveGate``, which shares its build
       with SC#1 per the plan's own instruction to "build the positive
       fixture"): a distinctive ``copyright`` canary configured in that
       SAME fixture's ``conf.py`` never appears anywhere in the emitted
       show-rule region (D-08, structural non-leak).

Per D-06, no assertion anywhere in this module matches on the TEXT of a
Typst/Sphinx compiler error message -- only that a real compile /
``sphinx-build`` invocation raises or exits non-zero.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "typst_elements_pass_through_gate"
PAPERSIZE_FIXTURE_DIR = FIXTURES_DIR / "papersize_positive"
FONTSIZE_FIXTURE_DIR = FIXTURES_DIR / "fontsize_positive"
UNKNOWN_KEY_FIXTURE_DIR = FIXTURES_DIR / "unknown_key_negative"

# The copyright canary configured in papersize_positive/conf.py -- SC#4
# asserts this string never appears in the emitted show-rule region.
COPYRIGHT_CANARY = "2026, Copyright Non-Leak Canary -- Must Never Appear In Output"


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard -- mirrors
    ``tests/test_package_only_config_gate.py::_run_sphinx_build``.
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
    closing ``)`` line -- so per-case assertions search this region in
    isolation rather than the whole document. Mirrors
    ``tests/test_package_only_config_gate.py::_show_rule_call_region``.
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
    reason="typst-py is required for the GATE-01 typst_elements papersize gate",
)
class TestPapersizePositiveGate:
    """
    SC#1: a real ``-b typstpdf`` build emits ``papersize`` as a quoted
    Typst string in the show-rule region and compiles a valid PDF.

    SC#4 (shares this SAME build, per the plan's instruction to prove the
    copyright-non-leak case against "the positive fixture"): the
    ``copyright`` canary configured in this fixture's ``conf.py`` never
    appears anywhere in the show-rule region.

    Requirements: CONF-04.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        """
        Build the papersize-positive fixture ONCE via ``-b typstpdf`` (a
        real compile) and share the result across the SC#1/SC#4 assertions
        below -- one build, one compile, many independent assertions.

        ``@staticmethod`` (no ``self``): mirrors
        ``TestPackageOnlyConfigGate.build`` -- a class-scoped fixture
        defined as an instance method would run once for the class but
        give each test its OWN ``self``, so returning a plain value (not
        mutating ``self``) is the correct shape under this project's
        ``error::DeprecationWarning`` filter.
        """
        build_dir = tmp_path_factory.mktemp("papersize_positive_build")
        result = _run_sphinx_build(PAPERSIZE_FIXTURE_DIR, build_dir, "typstpdf")
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
            "result": result,
            "text": typ_path.read_text(encoding="utf-8"),
            "pdf_path": build_dir / "index.pdf",
        }

    def test_papersize_emitted_as_quoted_string(self, build):
        """
        D-01: ``papersize: "us-letter"`` (quoted) appears in the show-rule
        region -- the exact configured value, exactly once.
        """
        region = _show_rule_call_region(build["text"])
        assert 'papersize: "us-letter",' in region

    def test_real_compile_produces_valid_pdf(self, build):
        """
        A real ``-b typstpdf`` build of the papersize-positive fixture
        exited 0 and produced a non-empty, well-formed PDF.
        """
        assert build["result"].returncode == 0
        pdf_path = build["pdf_path"]
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0
        with open(pdf_path, "rb") as f:
            magic = f.read(4)
        assert magic == b"%PDF", "Generated file is not a valid PDF"

    def test_copyright_never_leaks_into_show_rule_region(self, build):
        """
        SC#4/D-08: the ``copyright`` canary configured in this fixture's
        ``conf.py`` never appears anywhere in the show-rule region --
        structural non-leak, not a filter. Checked both as the literal
        canary string and as a bare ``copyright:`` key, to catch either a
        full leak or a stray truncated one.
        """
        region = _show_rule_call_region(build["text"])
        assert COPYRIGHT_CANARY not in region
        assert "copyright:" not in region


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the GATE-01 typst_elements fontsize gate",
)
class TestFontsizePositiveGate:
    """
    SC#2: a SEPARATE real ``-b typstpdf`` build (never combined with the
    papersize case -- a combined case would hide a per-key emission-type
    bug) emits ``fontsize`` as an UNQUOTED Typst length in the show-rule
    region, never its quoted-string form, and compiles a valid PDF.

    Requirements: CONF-04.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        """
        Build the fontsize-positive fixture ONCE via ``-b typstpdf`` (a
        real compile), separately from the papersize fixture above.
        """
        build_dir = tmp_path_factory.mktemp("fontsize_positive_build")
        result = _run_sphinx_build(FONTSIZE_FIXTURE_DIR, build_dir, "typstpdf")
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
            "result": result,
            "text": typ_path.read_text(encoding="utf-8"),
            "pdf_path": build_dir / "index.pdf",
        }

    def test_fontsize_emitted_as_unquoted_length(self, build):
        """
        D-02: ``fontsize: 20pt`` (UNQUOTED) appears in the show-rule
        region -- the exact configured value, via the ``RawTypst`` marker.
        """
        region = _show_rule_call_region(build["text"])
        assert "fontsize: 20pt," in region

    def test_fontsize_quoted_form_never_appears(self, build):
        """
        Pitfall 1 (the double-formatting trap): the quoted-string form of
        the configured fontsize must NEVER appear anywhere in the
        show-rule region -- proof that ``fontsize`` did not re-enter
        ``_format_typst_value()``'s ``str`` branch after being pre-rendered.
        """
        region = _show_rule_call_region(build["text"])
        assert 'fontsize: "20pt"' not in region

    def test_real_compile_produces_valid_pdf(self, build):
        """
        A real ``-b typstpdf`` build of the fontsize-positive fixture
        exited 0 and produced a non-empty, well-formed PDF.
        """
        assert build["result"].returncode == 0
        pdf_path = build["pdf_path"]
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0
        with open(pdf_path, "rb") as f:
            magic = f.read(4)
        assert magic == b"%PDF", "Generated file is not a valid PDF"


class TestUnknownKeyNegativeGate:
    """
    SC#3: an unrecognized ``typst_elements`` key makes ``sphinx-build``
    exit non-zero via ``sphinx.errors.ExtensionError`` (D-06/D-07) --
    never silently dropped, and never passed through as an undeclared
    kwarg reaching ``project()``. Uses the faster ``-b typst`` builder --
    no real compile is needed to prove the BUILD itself aborts (the
    fail-loud raise happens during ``TypstWriter.translate()``, before any
    ``typst.compile()`` call could occur).

    Deliberately NOT skipped on ``not TYPST_AVAILABLE``: this case does
    not invoke ``typst.compile()`` at all -- the whole point is that the
    Python-side ``ExtensionError`` aborts the build before a compile step
    is ever reached.

    Requirements: CONF-04.
    """

    def test_build_exits_non_zero(self, tmp_path):
        build_dir = tmp_path / "unknown_key_build"
        result = _run_sphinx_build(UNKNOWN_KEY_FIXTURE_DIR, build_dir, "typst")

        assert result.returncode != 0, (
            f"Expected sphinx-build to abort on an unknown typst_elements "
            f"key, but it exited 0:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_no_master_carries_the_bogus_key_as_a_kwarg(self, tmp_path):
        """
        Even though the build aborts, defensively confirm that no emitted
        ``.typ`` file anywhere in the build directory carries the bogus
        key as a ``project.with(...)`` kwarg -- i.e. the unknown key was
        never allowed to reach the render step at all.
        """
        build_dir = tmp_path / "unknown_key_no_leak_build"
        _run_sphinx_build(UNKNOWN_KEY_FIXTURE_DIR, build_dir, "typst")

        for typ_file in build_dir.rglob("*.typ"):
            text = typ_file.read_text(encoding="utf-8")
            assert "bogus_unknown_key" not in text
