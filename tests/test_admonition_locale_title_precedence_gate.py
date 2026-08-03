"""
Phase 39, GATE-01: G-39-1 locale title precedence gate.

Proves that the Sphinx locale catalog title (``sphinx.locale.
admonitionlabels``, threaded through ``custom_title`` in
``_visit_admonition``) still beats gentle-clues' own per-id ``linguify``
default title for BOTH new red-family function ids G-39-1 introduces
(``danger``, ``memo``), in BOTH the English and Japanese catalogs.

Mechanism this gate protects (measured directly in
``~/.cache/typst/packages/preview/gentle-clues/1.3.1/lib/predefined.typ``,
``_predefined-clue``, lines 41-53): the caller's ``..args`` are spread
AFTER the linguify default ``title:`` keyword argument --

.. code-block:: typst

    #let _predefined-clue(id, ..args) = clue(
      accent-color: _get-accent-color-for(id),
      title: _get-title-for(id),
      icon: _get-icon-for(id),
      ..args,
    )

-- so an explicit ``title:`` argument in ``..args`` overrides the
positional default (Typst spread-argument overriding semantics: a later
named argument for the same parameter wins). If a call site ever stopped
passing an explicit title, the box would silently fall back to gentle-clues'
own linguified title for that function id instead of the Sphinx catalog
value -- exactly the regression this gate exists to catch the moment
``attention``/``danger`` start riding ``memo``/``danger`` instead of the
single folded ``error`` function.

This is a v0.7.0 GATE-01 module: every design defect asserted here
**compiles fine today** (there is no fatal to catch), so RED is a
structural region-scoped equality/absence mismatch, never a
``sphinx-build`` failure and never a ``typst.compile()`` error.

Region-scoping (``_clue_open_before``/``_title_arg_after``) is reused from
``tests.test_admonition_bucket_render_gate`` rather than reimplemented --
verified to resolve both standalone (``pytest
tests/test_admonition_locale_title_precedence_gate.py``) and as part of the
whole suite, because this project uses pytest's default ``prepend`` import
mode with no package marker under ``tests/``, so sibling test modules are
importable as top-level modules.

Against the tree this plan starts from, this module reports:

- RED (must flip GREEN once ``visit_danger``/``visit_attention`` are
  re-routed per G-39-1 / plan 39-11): all four box-open assertions
  (attention and danger, in both English and Japanese) -- today both
  resolve to the single folded ``error`` function in both locales.
- GREEN throughout, by design, as CONTROLS: every title-source assertion in
  both locales (D-04/D-05's catalog-title-wins-over-package-default
  mechanism was already satisfied by an earlier plan in this phase, and
  moving which FUNCTION boxes attention/danger does not change which
  SOURCE supplies the title argument), and the negative package-default
  guards (neither of gentle-clues' own English/Japanese ``memo`` titles nor
  its danger titles ever leaked into the emitted title argument, pre-phase
  or post-phase, because ``_visit_admonition`` always passes an explicit
  ``custom_title`` for every catalog-keyed type).

The Japanese half is proven at the emitted-Typst-SOURCE tier only -- no CJK
glyph is ever extracted from a compiled PDF anywhere in this module. This
is the same deliberate split ``tests/fixtures/typst_lang_gate/
ja_default/conf.py`` records for CONF-07, taken here for the same reason:
CJK glyph extraction depends on system font availability this project has
never pinned, so a green there would be a statement about the runner's
fonts rather than about the title source.

See ``.planning/phases/39-admonition-taxonomy-rubric-nesting/
39-GATE-EVIDENCE-05.md`` for the verbatim RED/CONTROL split recorded
against a named commit, and for the measured ``lang.toml``
``[lang.ja]`` ``memo`` value (which CONFIRMS -- does not contradict --
39-UAT.md's ``measured_context`` on this specific point; see that evidence
document for the full correction record).
"""

import subprocess
import sys
from pathlib import Path

import pytest
from sphinx import locale as sphinx_locale
from sphinx import package_dir as sphinx_package_dir
from sphinx.locale import admonitionlabels
from test_admonition_bucket_render_gate import _clue_open_before, _title_arg_after

# `admonitionlabels`' entries are lazy `_TranslationProxy` objects resolved
# at `str()` time against whichever translator is CURRENTLY installed for
# the "sphinx"/"general" namespace -- there is no separate translator per
# language living in this dict. This test process never runs a real Sphinx
# `Application` (every build below is a subprocess), so nothing installs a
# translator for us the way a live `language = "ja"` build does; each
# catalog read below must explicitly (re-)install the translator for the
# language it wants via `sphinx.locale.init`, passing Sphinx's OWN bundled
# locale directory (`package_dir/locale`, holding `sphinx.mo` per language)
# -- an empty `locale_dirs` list resolves every language to the same
# NullTranslations fallback (English), which was measured directly this
# planning session and is why this helper exists rather than a bare
# `str(admonitionlabels[key])`.
_SPHINX_LOCALE_DIRS = [None, Path(sphinx_package_dir) / "locale"]

# The ``(namespace, catalog)`` key ``sphinx.locale.init`` writes to by
# default (its own ``namespace="general"``/``catalog="sphinx"`` defaults) --
# named here so ``_catalog_title`` can save and restore exactly this one
# registry entry, never the whole ``sphinx_locale.translators`` dict.
_SPHINX_LOCALE_REGISTRY_KEY = ("general", "sphinx")


def _catalog_title(catalog_key: str, language: str) -> str:
    """
    Return the ``sphinx.locale.admonitionlabels[catalog_key]`` value,
    resolved in ``language`` by explicitly (re-)installing that language's
    translator first.

    Saves and restores ``sphinx.locale.translators``' pre-call entry for
    ``_SPHINX_LOCALE_REGISTRY_KEY`` around the read (T-39-22-adjacent test
    isolation: measured directly this planning session that leaving the
    Japanese translator installed process-wide leaks into unrelated,
    alphabetically-later test modules in the same pytest session --
    ``tests/test_admonitions.py``'s English title assertions turned up
    Japanese text -- because this test process never runs a real Sphinx
    ``Application`` to scope the translator per build the way a live
    ``language = "ja"`` build does).
    """
    previous = sphinx_locale.translators.get(_SPHINX_LOCALE_REGISTRY_KEY)
    try:
        sphinx_locale.init(_SPHINX_LOCALE_DIRS, language)
        return str(admonitionlabels[catalog_key])
    finally:
        if previous is not None:
            sphinx_locale.translators[_SPHINX_LOCALE_REGISTRY_KEY] = previous
        else:
            sphinx_locale.translators.pop(_SPHINX_LOCALE_REGISTRY_KEY, None)


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

# The literal-source-leak signatures every render-gate module in this
# project reuses (tests/test_pdf_render_gate.py's LEAK_SIGNATURES) -- a
# markup-mode regression must not hide behind this gate's title assertions.
LEAK_SIGNATURES = ("par({", 'text("', 'raw("')

# gentle-clues 1.3.1's OWN linguify default titles for the `memo` id,
# hand-transcribed from
# ~/.cache/typst/packages/preview/gentle-clues/1.3.1/lib/lang.toml
# `[lang.en]`/`[lang.ja]` tables this planning session. `danger`'s own
# default ("Danger"/"危険") is IDENTICAL to the Sphinx catalog value in
# both locales (see the module docstring above and
# 39-GATE-EVIDENCE-05.md), so it supplies no discriminating negative guard
# and is intentionally not asserted against here.
_GENTLE_CLUES_MEMO_TITLE_EN = "Memorize"
_GENTLE_CLUES_MEMO_TITLE_JA = "覚える"


# ---------------------------------------------------------------------------
# Fixture / build plumbing
# ---------------------------------------------------------------------------


def _run_sphinx_build_typst(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typst`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (NEVER ``uv run sphinx-build``)
    -- the NixOS PATH-shadowing hazard every render-gate module in this
    project restates: a stray non-Nix ``uv`` binary shadowing the correct
    Nix-provided ``uv`` earlier on PATH for subprocess children makes
    ``["uv", "run", ...]`` exit 127 when invoked from inside a
    pytest-launched subprocess, even though the same command succeeds when
    run directly in a shell.
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "typst",
            str(source_dir),
            str(build_dir),
        ],
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope="session")
def locale_title_gate_en_dir() -> Path:
    """Return the path to the English admonition_locale_title_gate sub-project."""
    return Path(__file__).parent / "fixtures" / "admonition_locale_title_gate" / "en"


@pytest.fixture(scope="session")
def locale_title_gate_ja_dir() -> Path:
    """Return the path to the Japanese admonition_locale_title_gate sub-project."""
    return Path(__file__).parent / "fixtures" / "admonition_locale_title_gate" / "ja"


@pytest.fixture(scope="session")
def locale_title_gate_en_typ_text(
    locale_title_gate_en_dir: Path, tmp_path_factory: pytest.TempPathFactory
) -> str:
    """Build the English sub-project once through ``-b typst`` and return its
    emitted ``index.typ`` text."""
    build_dir = tmp_path_factory.mktemp("locale_title_gate_en_typ") / "_build"
    result = _run_sphinx_build_typst(locale_title_gate_en_dir, build_dir)
    assert result.returncode == 0, (
        f"sphinx-build -b typst failed:\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    index_typ = build_dir / "index.typ"
    assert index_typ.exists(), "index.typ was not generated"
    return index_typ.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def locale_title_gate_ja_typ_text(
    locale_title_gate_ja_dir: Path, tmp_path_factory: pytest.TempPathFactory
) -> str:
    """Build the Japanese sub-project once through ``-b typst`` and return its
    emitted ``index.typ`` text."""
    build_dir = tmp_path_factory.mktemp("locale_title_gate_ja_typ") / "_build"
    result = _run_sphinx_build_typst(locale_title_gate_ja_dir, build_dir)
    assert result.returncode == 0, (
        f"sphinx-build -b typst failed:\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    index_typ = build_dir / "index.typ"
    assert index_typ.exists(), "index.typ was not generated"
    return index_typ.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def locale_title_gate_en_pdf_text(
    locale_title_gate_en_dir: Path, tmp_path_factory: pytest.TempPathFactory
) -> str:
    """
    Build + real-compile the English sub-project ONCE per session and
    return the pypdf-extracted PDF text. English-only -- the module
    docstring and the acceptance criteria both require every ``pypdf`` use
    in this module to live inside a test named ``*_en``; the Japanese half
    is proven at the source tier only (see module docstring).
    """
    if not (TYPST_AVAILABLE and PYPDF_AVAILABLE):
        pytest.skip("typst-py and pypdf are both required for this render gate")

    build_dir = tmp_path_factory.mktemp("locale_title_gate_en_pdf") / "_build"
    result = _run_sphinx_build_typst(locale_title_gate_en_dir, build_dir)
    assert result.returncode == 0, (
        f"sphinx-build -b typst failed:\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
    index_typ = build_dir / "index.typ"
    assert index_typ.exists(), "index.typ was not generated"

    pdf_output = build_dir / "index.pdf"
    typst.compile(str(index_typ), output=str(pdf_output))
    assert pdf_output.exists(), "PDF file was not created"
    assert pdf_output.stat().st_size > 0, "PDF file is empty"
    with open(pdf_output, "rb") as f:
        magic = f.read(4)
        assert magic == b"%PDF", "Generated file is not a valid PDF"

    reader = pypdf.PdfReader(str(pdf_output))
    return "\n".join(page.extract_text() for page in reader.pages)


# ---------------------------------------------------------------------------
# English -- box-open (RED) assertions
# ---------------------------------------------------------------------------


def test_attention_box_opens_with_memo_en(locale_title_gate_en_typ_text: str) -> None:
    """G-39-1: in an English build, the attention box opens with the
    gentle-clues ``memo`` function. RED today: it opens with ``error``."""
    actual = _clue_open_before(locale_title_gate_en_typ_text, "LOCALEATTENTIONSENTINEL")
    assert actual == "memo", (
        f"G-39-1 violated: expected attention's box to open with 'memo' "
        f"in the English build, got {actual!r}"
    )


def test_danger_box_opens_with_danger_en(locale_title_gate_en_typ_text: str) -> None:
    """G-39-1: in an English build, the danger box opens with the
    gentle-clues ``danger`` function. RED today: it opens with ``error``."""
    actual = _clue_open_before(locale_title_gate_en_typ_text, "LOCALEDANGERSENTINEL")
    assert actual == "danger", (
        f"G-39-1 violated: expected danger's box to open with 'danger' "
        f"in the English build, got {actual!r}"
    )


# ---------------------------------------------------------------------------
# English -- title-source (CONTROL, GREEN today and after) assertions
# ---------------------------------------------------------------------------


def test_attention_title_is_catalog_value_en(
    locale_title_gate_en_typ_text: str,
) -> None:
    """
    CONTROL: the attention box's title argument equals the English
    ``sphinx.locale.admonitionlabels`` value ("Attention"), read inside
    this test -- never gentle-clues' own linguified "Warning" (today's
    folded function) or "Memorize" (memo's own default, post-routing).
    This is the discriminating case in English: the catalog says
    "Attention" where gentle-clues' memo id says "Memorize".
    """
    expected = f'"{_catalog_title("attention", "en")}"'
    actual = _title_arg_after(locale_title_gate_en_typ_text, "LOCALEATTENTIONSENTINEL")
    assert actual == expected, (
        f"D-04/D-05 title-source regression: expected {expected!r}, " f"got {actual!r}"
    )


def test_danger_title_argument_is_present_en(
    locale_title_gate_en_typ_text: str,
) -> None:
    """
    CONTROL: the danger box carries an explicit title argument at all
    (presence, not value). The Sphinx catalog and the gentle-clues package
    agree on danger's title string in both locales ("Danger"/"危険"), so a
    VALUE assertion here would pass regardless of which source produced it
    and would be a false witness for D-04/D-05's precedence mechanism --
    only presence of an explicit title argument on the emitted box proves
    the catalog lookup ran at all.
    """
    actual = _title_arg_after(locale_title_gate_en_typ_text, "LOCALEDANGERSENTINEL")
    assert actual is not None, (
        "D-04/D-05 title-source regression: expected an explicit title "
        "argument on danger's box, got none"
    )


# ---------------------------------------------------------------------------
# English -- compiled-PDF half (CONTROL, GREEN today and must stay GREEN
# after the routing lands -- that is the whole point of this half).
# ---------------------------------------------------------------------------


def test_attention_pdf_text_carries_catalog_title_not_package_default_en(
    locale_title_gate_en_pdf_text: str,
) -> None:
    """
    Real-compile discriminating case: the compiled PDF's extracted text
    contains the Sphinx catalog's "Attention" and does NOT contain gentle-
    clues' own English memo default title "Memorize". GREEN today
    trivially (attention rides ``error`` today, whose own default is
    "Warning", also absent) and must stay GREEN after G-39-1's routing
    lands and attention starts riding ``memo`` -- that transition is
    exactly what could silently swap "Attention" for "Memorize" if the
    explicit title argument were ever dropped.
    """
    full_text = locale_title_gate_en_pdf_text

    assert "LOCALEATTENTIONSENTINEL" in full_text, (
        "Expected sentinel 'LOCALEATTENTIONSENTINEL' in extracted PDF "
        "text -- body content regression, independent of bucket routing"
    )
    expected_title = _catalog_title("attention", "en")
    assert expected_title in full_text, (
        f"Expected the attention admonition's catalog title "
        f"{expected_title!r} in extracted PDF text -- D-04/D-05 "
        "title-source regression"
    )
    assert _GENTLE_CLUES_MEMO_TITLE_EN not in full_text, (
        f"gentle-clues' own English memo default title "
        f"{_GENTLE_CLUES_MEMO_TITLE_EN!r} leaked into extracted PDF text -- "
        "the explicit catalog title argument was lost"
    )
    for leaked_token in LEAK_SIGNATURES:
        assert leaked_token not in full_text, (
            f"Literal Typst source '{leaked_token}' leaked into rendered "
            "PDF text -- admonition markup/code-mode mismatch regression"
        )


# ---------------------------------------------------------------------------
# Japanese -- box-open (RED) assertions. Source tier only (see module
# docstring): no CJK glyph is extracted from any PDF anywhere in this
# module.
# ---------------------------------------------------------------------------


def test_attention_box_opens_with_memo_ja(locale_title_gate_ja_typ_text: str) -> None:
    """G-39-1: in a Japanese build, the attention box opens with the
    gentle-clues ``memo`` function. RED today: it opens with ``error``."""
    actual = _clue_open_before(locale_title_gate_ja_typ_text, "LOCALEATTENTIONSENTINEL")
    assert actual == "memo", (
        f"G-39-1 violated: expected attention's box to open with 'memo' "
        f"in the Japanese build, got {actual!r}"
    )


def test_danger_box_opens_with_danger_ja(locale_title_gate_ja_typ_text: str) -> None:
    """G-39-1: in a Japanese build, the danger box opens with the
    gentle-clues ``danger`` function. RED today: it opens with ``error``."""
    actual = _clue_open_before(locale_title_gate_ja_typ_text, "LOCALEDANGERSENTINEL")
    assert actual == "danger", (
        f"G-39-1 violated: expected danger's box to open with 'danger' "
        f"in the Japanese build, got {actual!r}"
    )


# ---------------------------------------------------------------------------
# Japanese -- title-source (CONTROL) assertions, source tier only.
# ---------------------------------------------------------------------------


def test_attention_title_is_catalog_value_ja(
    locale_title_gate_ja_typ_text: str,
) -> None:
    """
    CONTROL: the attention box's title argument equals the Japanese
    ``sphinx.locale.admonitionlabels`` value ("注意"), read inside this
    test -- never gentle-clues' own linguified Japanese memo default
    ("覚える"). This is the discriminating case in Japanese, mirroring the
    English half.
    """
    expected = f'"{_catalog_title("attention", "ja")}"'
    actual = _title_arg_after(locale_title_gate_ja_typ_text, "LOCALEATTENTIONSENTINEL")
    assert actual == expected, (
        f"D-04/D-05 title-source regression: expected {expected!r}, " f"got {actual!r}"
    )


def test_package_default_titles_never_appear_in_emitted_source_ja(
    locale_title_gate_ja_typ_text: str,
) -> None:
    """
    CONTROL, source-tier only: neither of gentle-clues' own memo titles --
    the English "Memorize" NOR the Japanese "覚える", both read out of
    ``lang.toml`` at planning time and transcribed as literals above with a
    comment naming the file and the table they came from -- appears
    anywhere in the emitted Typst source for the Japanese build. Either one
    appearing would mean the explicit catalog title argument was lost, in
    either direction (a stale English fallback or a leaked package
    default). No CJK glyph is extracted from a compiled PDF anywhere in
    this module -- this assertion runs on emitted Typst SOURCE text only.
    """
    full_text = locale_title_gate_ja_typ_text
    assert _GENTLE_CLUES_MEMO_TITLE_EN not in full_text, (
        f"gentle-clues' own English memo default title "
        f"{_GENTLE_CLUES_MEMO_TITLE_EN!r} leaked into the emitted Japanese "
        "build's Typst source -- the explicit catalog title argument was "
        "lost"
    )
    assert _GENTLE_CLUES_MEMO_TITLE_JA not in full_text, (
        f"gentle-clues' own Japanese memo default title "
        f"{_GENTLE_CLUES_MEMO_TITLE_JA!r} leaked into the emitted Typst "
        "source -- the explicit catalog title argument was lost"
    )
