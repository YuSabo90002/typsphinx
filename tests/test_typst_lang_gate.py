"""
GATE-01: real-compile config->output regression gate for the Typst
`lang` typesetting-language parameter derived from Sphinx's ``language``
config (Phase 27.1, CONF-07).

Before this phase, ``templates/base.typ`` hardcoded
``set text(size: fontsize, lang: "en")`` -- so a project with
``language = "ja"`` or ``language = "de"`` still got English figure/table
supplement text ("Figure 1"/"Table 1") in its compiled PDF, even though
Sphinx's own i18n transform had already translated the surrounding prose
(verified separately, out of this module's scope). Plan 01 (Wave 1) wired
a new ``lang`` parameter into ``project()`` and a ``derive_typst_lang()``
conversion helper on the Python side; this module is the mandatory
real-``typst.compile()`` proof that the value actually reaches the
compiled artifact and changes Typst's generated labels -- the same defect
class ``tests/test_typst_elements_pass_through_gate.py`` (Phase 26,
CONF-04) closed for ``papersize``/``fontsize``, and the same discipline:
registration-only unit tests stay green whether or not the feature
actually works, so only a real compile (plus, where the proof requires
it, PDF text extraction) counts as acceptance evidence.

D-07 split-proof rationale (do not mistake the following for an
oversight): ROADMAP SC#1 is worded as a single Japanese-supplement
PDF-extraction proof. This module deliberately splits it in two instead:

- The ``ja`` case (``TestJapaneseSourceProof``) proves ONLY that the
  value reaches the emitted Typst SOURCE under a real compile -- a
  font-independent assertion on the ``#show: project.with(...)`` region,
  never on extracted PDF text.
- The supplement-LANGUAGE-LINKAGE proof -- the case that actually matters
  for Phase 25's captioned-table motivation -- is done with ``de``
  (``TestGermanLinkageProof``) plus real ``pypdf`` text extraction,
  because "Abbildung"/"Tabelle" are Latin-script and stable across every
  OS/font configuration, whereas CJK glyph extraction depends on system
  font availability the CI ubuntu runner has never confirmed. Vendoring a
  CJK font binary into this repository to make the ``ja`` case a
  PDF-extraction assertion was considered and explicitly rejected
  (27.1-CONTEXT.md D-07): it would add several megabytes of binary plus a
  redistribution-licence obligation to a pure-Python extension, to prove
  something the German case already proves.

Per this repository's established convention (mirrored from
``tests/test_typst_elements_pass_through_gate.py`` and
``tests/test_pdf_render_gate.py``), no assertion anywhere in this module
matches on the TEXT of a Typst compiler error message -- only that a real
compile / ``sphinx-build`` invocation succeeds, fails, or raises.
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

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "typst_lang_gate"
JA_DEFAULT_FIXTURE_DIR = FIXTURES_DIR / "ja_default"
DE_DEFAULT_FIXTURE_DIR = FIXTURES_DIR / "de_default"
PRECEDENCE_FIXTURE_DIR = FIXTURES_DIR / "precedence"
MALFORMED_LANGUAGE_FIXTURE_DIR = FIXTURES_DIR / "malformed_language"
CUSTOM_TEMPLATE_NO_LANG_FIXTURE_DIR = FIXTURES_DIR / "custom_template_no_lang"
SRCDIR_SHADOW_NO_LANG_FIXTURE_DIR = FIXTURES_DIR / "srcdir_shadow_no_lang"
PACKAGE_NO_LANG_FIXTURE_DIR = FIXTURES_DIR / "package_no_lang"


def _run_sphinx_build(
    source_dir: Path, build_dir: Path, builder: str
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b <builder>`` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``,
    never a resolved ``sphinx-build`` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard -- copied near-verbatim from
    ``tests/test_typst_elements_pass_through_gate.py::_run_sphinx_build``.
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
    isolation rather than the whole document. Copied near-verbatim from
    ``tests/test_typst_elements_pass_through_gate.py::_show_rule_call_region``.
    The ``\\w+`` in the opening pattern tolerates both the bundled
    ``project`` function name and a Typst-Universe package's own entry
    function name (e.g. ``ieee`` for the ``package_no_lang`` case).
    """
    start_match = re.search(r"^#show: \w+\.with\($", text, re.MULTILINE)
    assert start_match, f"Could not locate the show-rule call opening in:\n{text}"
    start = start_match.start()
    end_match = re.search(r"^\)$", text[start:], re.MULTILINE)
    assert end_match, f"Could not locate the show-rule call closing in:\n{text}"
    end = start + end_match.end()
    return text[start:end]


def _supplement_matches(full_text: str, supplement_word: str, number: int = 1) -> bool:
    """
    NBSP-tolerant match for a Typst-generated figure/table supplement
    label, e.g. ``"Tabelle\\xa01"`` or ``"Abbildung\\xa01"``.

    Typst separates the supplement word from its number with U+00A0
    (NO-BREAK SPACE), not an ASCII space -- confirmed by direct extraction
    during this phase's discuss session (27.1-CONTEXT.md's measured-fact
    table: extracted PDF text reads e.g. ``'\\u56f3\\xa01: cap'``). Python's
    regex ``\\s`` character class matches U+00A0 (it is whitespace per the
    Unicode database), so building the pattern with ``\\s+`` rather than a
    literal ASCII space is what makes this match real output. A plain
    ASCII-space substring check (``"Tabelle 1" in full_text``) would
    SILENTLY FAIL against perfectly correct Typst output -- it would never
    match ``"Tabelle\\xa01"`` -- which is exactly the kind of vacuously-red
    (or worse, false-negative-masking-a-real-pass) assertion this gate
    exists to avoid. Nothing in this codebase did NBSP-aware matching
    before this module.

    Args:
        full_text: The pypdf-extracted PDF text to search.
        supplement_word: The supplement word to look for (e.g.
            ``"Tabelle"``, ``"Abbildung"``, ``"Table"``, ``"Figure"``).
        number: The figure/table number expected immediately after the
            NBSP (defaults to ``1``, the only number either fixture ever
            produces).

    Returns:
        ``True`` if the NBSP-tolerant pattern matches; ``False`` otherwise.
    """
    pattern = rf"{re.escape(supplement_word)}\s+{number}"
    return re.search(pattern, full_text) is not None


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the GATE-01 typst lang gate",
)
class TestJapaneseSourceProof:
    """
    SC#1 (D-07 source half): a real ``-b typstpdf`` build of a
    ``language = "ja"`` project on the DEFAULT template path succeeds, and
    the emitted master's ``#show: project.with(...)`` region carries a
    quoted ``lang: "ja"`` entry -- a font-independent proof, deliberately
    NOT a PDF-text extraction of CJK glyphs (see this module's docstring
    for the D-07 rationale).

    Requirements: CONF-07.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        """
        Build the ja_default fixture ONCE via ``-b typstpdf`` (a real
        compile) and share the result across the assertions below.
        """
        build_dir = tmp_path_factory.mktemp("ja_default_build")
        result = _run_sphinx_build(JA_DEFAULT_FIXTURE_DIR, build_dir, "typstpdf")
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

    def test_lang_ja_emitted_in_show_rule_region(self, build):
        """
        D-02: ``language = "ja"`` converts to and is emitted as
        ``lang: "ja",`` (quoted) in the show-rule region.
        """
        region = _show_rule_call_region(build["text"])
        assert 'lang: "ja",' in region

    def test_real_compile_produces_valid_pdf(self, build):
        """
        A real ``-b typstpdf`` build of the ja_default fixture exited 0
        and produced a non-empty, well-formed PDF.
        """
        assert build["result"].returncode == 0
        pdf_path = build["pdf_path"]
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0
        with open(pdf_path, "rb") as f:
            magic = f.read(4)
        assert magic == b"%PDF", "Generated file is not a valid PDF"


@pytest.mark.skipif(
    not (TYPST_AVAILABLE and PYPDF_AVAILABLE),
    reason="typst-py and pypdf are required for the GATE-01 typst lang "
    "gate's German supplement-linkage proof",
)
class TestGermanLinkageProof:
    """
    SC#1 (D-07 linkage half): a real ``-b typstpdf`` build of a
    ``language = "de"`` project on the DEFAULT template path succeeds, and
    the pypdf-extracted PDF text carries the German table AND figure
    supplements ("Tabelle"/"Abbildung") -- via the NBSP-tolerant
    ``_supplement_matches()`` helper -- while the ENGLISH forms
    ("Table"/"Figure") do NOT appear. This is the actual proof that the
    text-language setting drives Typst's generated labels; a build that
    silently ignored ``language`` would still show the English forms and
    fail the negative assertion.

    Requirements: CONF-07.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        """
        Build the de_default fixture ONCE via ``-b typstpdf`` (a real
        compile) and extract its PDF text ONCE, sharing both across the
        assertions below.
        """
        build_dir = tmp_path_factory.mktemp("de_default_build")
        result = _run_sphinx_build(DE_DEFAULT_FIXTURE_DIR, build_dir, "typstpdf")
        assert result.returncode == 0, (
            f"sphinx-build -b typstpdf failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        pdf_path = build_dir / "index.pdf"
        assert pdf_path.exists(), (
            f"index.pdf was not produced:\nstdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        reader = pypdf.PdfReader(str(pdf_path))
        full_text = "\n".join(page.extract_text() for page in reader.pages)
        return {"result": result, "pdf_path": pdf_path, "full_text": full_text}

    def test_de_default_real_compile_produces_valid_pdf(self, build):
        """
        A real ``-b typstpdf`` build of the de_default fixture exited 0
        and produced a non-empty, well-formed PDF.
        """
        assert build["result"].returncode == 0
        pdf_path = build["pdf_path"]
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0
        with open(pdf_path, "rb") as f:
            magic = f.read(4)
        assert magic == b"%PDF", "Generated file is not a valid PDF"

    def test_de_default_german_table_supplement_present(self, build):
        """
        The captioned table's supplement reads "Tabelle<NBSP>1" in the
        extracted PDF text -- Phase 25's motivating case for this whole
        phase.
        """
        assert _supplement_matches(
            build["full_text"], "Tabelle"
        ), f"Expected 'Tabelle<NBSP>1' in extracted text:\n{build['full_text']}"

    def test_de_default_german_figure_supplement_present(self, build):
        """
        The captioned figure's supplement reads "Abbildung<NBSP>1" in the
        extracted PDF text.
        """
        assert _supplement_matches(
            build["full_text"], "Abbildung"
        ), f"Expected 'Abbildung<NBSP>1' in extracted text:\n{build['full_text']}"

    def test_de_default_english_supplements_do_not_appear(self, build):
        """
        Negative half of the linkage proof: if the build silently ignored
        ``language = "de"`` (e.g. the pre-fix hardcoded ``lang: "en"``
        shape), the supplements would read "Table 1"/"Figure 1" instead.
        Neither English form may appear.
        """
        assert not _supplement_matches(build["full_text"], "Table")
        assert not _supplement_matches(build["full_text"], "Figure")


class TestPrecedence:
    """
    SC#2: an explicit ``typst_elements = {"lang": "ja"}`` beats the value
    ("de") that would otherwise be auto-derived from Sphinx
    ``language = "de"``. Driven through the faster source-only ``-b typst``
    builder -- no real compile is needed to prove which value reaches the
    emitted show-rule region.

    Deliberately NOT skipped on ``not TYPST_AVAILABLE``: this case never
    invokes ``typst.compile()`` at all, mirroring
    ``TestUnknownKeyNegativeGate`` in the CONF-04 analog module.

    Requirements: CONF-07.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        build_dir = tmp_path_factory.mktemp("precedence_build")
        result = _run_sphinx_build(PRECEDENCE_FIXTURE_DIR, build_dir, "typst")
        assert result.returncode == 0, (
            f"sphinx-build -b typst failed:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        typ_path = build_dir / "index.typ"
        assert typ_path.exists()
        return typ_path.read_text(encoding="utf-8")

    def test_explicit_lang_wins_over_auto_value(self, build):
        """
        Exactly ONE ``lang:`` entry is emitted, and it carries the
        explicit ``"ja"`` value -- never the ``"de"`` that ``language``
        alone would have derived.
        """
        region = _show_rule_call_region(build)
        assert (
            region.count("lang:") == 1
        ), f"Expected exactly one lang: entry in:\n{region}"
        assert 'lang: "ja",' in region
        assert 'lang: "de"' not in region


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the GATE-01 typst lang gate",
)
class TestMalformedLanguage:
    """
    SC#4: a Sphinx ``language`` value that cannot be reduced to a two- or
    three-letter code (here, a CJK string -- the load-bearing case, since
    it is exactly the input a Unicode-aware ``str.isalpha()`` check would
    wrongly accept, per ``derive_typst_lang()``'s own docstring) does NOT
    abort the build, via a real ``-b typstpdf`` compile, and emits no
    ``lang`` entry at all -- the parameter is omitted so
    ``templates/base.typ``'s own ``lang: "en"`` default applies.

    Deliberately does NOT assert on the warning text in the subprocess's
    captured stderr: the warning is emitted through a stdlib module
    logger rather than Sphinx's own logging hierarchy, so its presence in
    a subprocess's output is not a contract worth pinning here. The
    warning is proven at the unit tier by Plan 01's ``caplog`` test
    (``tests/test_template_engine.py``).

    Requirements: CONF-07.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def build(tmp_path_factory):
        build_dir = tmp_path_factory.mktemp("malformed_language_build")
        result = _run_sphinx_build(
            MALFORMED_LANGUAGE_FIXTURE_DIR, build_dir, "typstpdf"
        )
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

    def test_build_does_not_abort(self, build):
        assert build["result"].returncode == 0

    def test_no_lang_entry_emitted(self, build):
        region = _show_rule_call_region(build["text"])
        assert "lang:" not in region

    def test_real_compile_produces_valid_pdf(self, build):
        """
        A real ``-b typstpdf`` build of the malformed_language fixture
        exited 0 and produced a non-empty, well-formed PDF, even though
        ``language`` could not be converted to a Typst ``lang`` code.
        """
        assert build["result"].returncode == 0
        pdf_path = build["pdf_path"]
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0
        with open(pdf_path, "rb") as f:
            magic = f.read(4)
        assert magic == b"%PDF", "Generated file is not a valid PDF"
