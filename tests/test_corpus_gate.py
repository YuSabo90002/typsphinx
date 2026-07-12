"""
GATE-02 full-corpus real-render acceptance gate (Phase 15).

Requirements: GATE-02 (15-CONTEXT.md D-01..D-05, 15-RESEARCH.md).

This module closes the milestone's empirical gate -- "does Sphinx's own
`doc/` tree compile end-to-end through typsphinx's `typstpdf` builder with
no fatal Typst error." It does so by running the full pipeline for real,
against a shallow git clone of Sphinx's own documentation source tree
(never a curated subset, D-02):

    git clone (pinned tag) -> conf.py augment -> sphinx-build -b typstpdf
        -> typst.compile() (inside TypstPDFBuilder.finish()) -> %PDF check

The corpus is obtained by a shallow `git clone --depth 1 --branch` at the
tag matching the installed `sphinx.__version__` (D-01), cached by resolved
tag so repeated local runs don't re-clone. The real `doc/conf.py` is used
as-is, augmented only by a 2-line append wiring `typsphinx` in (D-03) --
never a stripped/minimal conf. This whole class is `@pytest.mark.slow` and
excluded from the default/CI fast suite via `-m "not slow"` (D-04), and
`pytest.skip`s (never fails) when the corpus is unavailable -- no network,
clone failure, or an unresolvable tag (D-05).

As a byproduct of the SAME build's captured stderr, the residual
`unknown_visit` warnings (nodes with no `visit_*`/`depart_*` handler) are
extractable as a frequency-ranked catalogue via a `re.MULTILINE`-anchored
regex, since a single warning's node dump can itself span multiple physical
lines (SC#2).
"""

import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest
import sphinx

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False


def resolve_corpus_tag() -> str:
    """Resolve the git tag matching the installed Sphinx version.

    Sphinx tags its releases as `vX.Y.Z` (verified: v9.1.0 exists on
    github.com/sphinx-doc/sphinx). A dev/pre-release suffix (e.g.
    "9.1.0.dev0") would not match any real tag -- callers must treat a
    clone failure at this tag as a D-05 skip condition, not a hard test
    failure.
    """
    return f"v{sphinx.__version__}"


def get_or_clone_corpus(cache_root: Path) -> Path | None:
    """Return the path to the cloned doc/ tree, or None if unavailable.

    Caches by resolved tag so repeated local runs don't re-clone (RESEARCH
    Pitfall 3). Returns None (never raises) on any failure -- callers
    pytest.skip (D-05).
    """
    tag = resolve_corpus_tag()
    dest = cache_root / f"sphinx-{tag}"
    doc_dir = dest / "doc"

    if doc_dir.exists() and (doc_dir / "conf.py").exists():
        return doc_dir

    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                tag,
                "https://github.com/sphinx-doc/sphinx.git",
                str(dest),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None

    if result.returncode != 0 or not doc_dir.exists():
        return None
    return doc_dir


@pytest.fixture(scope="session")
def corpus_doc_dir() -> Path:
    """
    Return the path to the cloned Sphinx `doc/` tree, cloning-and-caching
    on first use (session-scoped -- RESEARCH Pitfall 3: do NOT re-clone per
    test). `pytest.skip`s when the corpus is unavailable (no network, clone
    failure, or an unresolvable tag) per D-05.
    """
    cache_root = Path.home() / ".cache" / "typsphinx-corpus-gate"
    doc_dir = get_or_clone_corpus(cache_root)
    if doc_dir is None:
        pytest.skip(
            "Sphinx doc/ corpus unavailable (no network or clone failure) -- D-05"
        )
    return doc_dir


def wire_typsphinx_into_corpus_conf(corpus_doc_dir: Path) -> None:
    """Append typsphinx wiring to the cloned doc/conf.py (mutates the
    EPHEMERAL clone only -- never the real upstream Sphinx repo).

    Idempotent: cached clones are re-augmented across runs, so this is a
    no-op if the wiring is already present.

    `extensions` is guaranteed to already be a list at this point in the
    real conf.py. `typst_documents` is a typsphinx-only config value that
    Sphinx's own conf.py never defines, so there is no collision risk
    appending it fresh.
    """
    conf_py = corpus_doc_dir / "conf.py"
    existing_text = conf_py.read_text(encoding="utf-8")
    if "extensions.append('typsphinx')" in existing_text:
        return

    with conf_py.open("a", encoding="utf-8") as f:
        f.write(
            "\n\n# --- typsphinx corpus-gate wiring (test-only, not upstream) ---\n"
        )
        f.write("extensions.append('typsphinx')\n")
        f.write(
            "typst_documents = [('index', 'sphinx-corpus', "
            "'Sphinx Documentation', 'the Sphinx developers')]\n"
        )


def _run_corpus_sphinx_build(
    builder: str, source_dir: Path, build_dir: Path, env: dict | None = None
) -> subprocess.CompletedProcess:
    """
    Run `sphinx-build -b <builder>` as a subprocess and return the
    completed process (stdout/stderr captured as text).

    Invoked as `sys.executable -m sphinx` (the sphinx-build console entry
    point's module form) rather than shelling out to `uv run sphinx-build`:
    this guarantees the exact interpreter/venv already running this test is
    reused, with no dependency on external PATH resolution of a `uv`
    executable -- sidesteps a documented NixOS sandbox PATH-shadowing
    hazard (see `tests/test_pdf_render_gate.py::_run_sphinx_build_typst`).

    `builder` is parameterized (`"typstpdf"` for SC#1, `"typst"` for a
    translate-only build) rather than hardcoded.
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
        env=env,
    )


# Anchored on the literal line-start warning prefix (never on the full,
# potentially multi-line node dump `str(node)` can produce) -- see
# typsphinx/translator.py's unknown_visit (logger.warning(f"unknown node
# type: {node}")). re.MULTILINE lets `^` match at the start of every
# physical line, not just the start of the whole string.
UNKNOWN_NODE_RE = re.compile(r"^WARNING: unknown node type: <(\w+)", re.MULTILINE)


def catalogue_unknown_visit(stderr_text: str) -> Counter:
    """Frequency-count unknown_visit warnings by outer node tag name.

    Anchored on the literal warning-line prefix (not on the full,
    potentially multi-line node dump) so embedded newlines in a node's own
    text content never cause a false split or a missed/duplicated count,
    and prose merely mentioning "unknown node type" (without the WARNING
    prefix at line-start) is never counted (false-positive immunity).
    """
    return Counter(UNKNOWN_NODE_RE.findall(stderr_text))


def test_catalogue_unknown_visit_multiline():
    """
    Fast (non-slow, no network) unit test for the SC#2 parser: a synthetic
    multi-line stderr string containing a 2-line `<citation>` node dump, a
    nested `<label>` child warning on its own line, and a prose line that
    merely mentions "unknown node type" without the WARNING prefix.
    """
    stderr_text = (
        'WARNING: unknown node type: <citation backrefs="id1" docname="index" '
        'ids="cit2002" names="cit2002"><label support_smartquotes="0">CIT2002'
        "</label><paragraph>A citation\n"
        "spanning multiple lines with some more descriptive content that is "
        "long.</paragraph></citation>\n"
        'WARNING: unknown node type: <label support_smartquotes="0">CIT2002'
        "</label>\n"
        "This prose mentions unknown node type but is not a WARNING line "
        "and must not be counted.\n"
    )

    catalogue = catalogue_unknown_visit(stderr_text)

    # The 2-line <citation> dump counts as exactly ONE citation (never
    # split by its embedded newline).
    assert catalogue["citation"] == 1
    # The nested <label> child fires its own independent warning line, so
    # it increments its own count too (expected double-counting per node
    # TYPE, not a bug).
    assert catalogue["label"] == 1
    # Prose text containing the substring "unknown node type" WITHOUT the
    # line-start "WARNING: unknown node type: <" prefix is not counted.
    assert "prose" not in catalogue
    assert sum(catalogue.values()) == 2
