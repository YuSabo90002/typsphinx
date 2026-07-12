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

import os
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


@pytest.mark.slow
@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the GATE-02 corpus render gate",
)
class TestCorpusRenderGate:
    """
    Real-compile acceptance gate for GATE-02: Sphinx's own `doc/` tree
    compiles end-to-end through typsphinx's `typstpdf` builder with no
    fatal `TypstCompilationError`.

    Requirements: GATE-02 (15-CONTEXT.md D-01..D-05, 15-RESEARCH.md).
    """

    def test_corpus_compiles_with_no_fatal_error(self, corpus_doc_dir, tmp_path):
        """
        Clone (cached), augment, build the FULL corpus (D-02) through
        `-b typstpdf`, and assert the compiled `index.pdf` exists, is
        non-empty, and starts with the `%PDF` magic bytes -- never relying
        on `returncode == 0` alone (RESEARCH Pitfall 1: a missing
        `typst_documents` entry would make `TypstPDFBuilder.finish()`
        silently no-op, passing a returncode-only check trivially without
        ever calling `typst.compile()`).

        As a byproduct of the same build's captured stderr, the SC#2
        `unknown_visit` catalogue is produced and printed to stdout.
        """
        wire_typsphinx_into_corpus_conf(corpus_doc_dir)

        # RESEARCH Pitfall 1 guard: a cheap, loud pre-check that the
        # append actually landed before spending minutes on a real build.
        conf_text = (corpus_doc_dir / "conf.py").read_text(encoding="utf-8")
        assert "typst_documents" in conf_text, (
            "wire_typsphinx_into_corpus_conf did not append typst_documents "
            "-- TypstPDFBuilder.finish() would silently no-op and this "
            "test would pass falsely (RESEARCH Pitfall 1)"
        )

        # Log the resolved tag and the clone's commit SHA for
        # reproducibility against a possibly force-moved tag (T-15-01).
        tag = resolve_corpus_tag()
        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=corpus_doc_dir,
            capture_output=True,
            text=True,
        )
        commit_sha = sha_result.stdout.strip()
        print(f"Corpus tag: {tag}")
        print(f"Corpus commit SHA: {commit_sha}")

        outdir = tmp_path / "_build"
        result = _run_corpus_sphinx_build("typstpdf", corpus_doc_dir, outdir)

        # SC#1 crux: the emitted PDF must actually exist -- docname-based
        # naming (builder.py:544/560), never the typst_documents "target"
        # field, never returncode == 0 alone. A fatal
        # TypstCompilationError raised inside the subprocess build
        # surfaces here as a nonzero return + a missing/empty PDF, failing
        # these asserts loudly -- this IS the GATE-02 pass/fail signal.
        pdf_path = outdir / "index.pdf"
        assert pdf_path.exists(), (
            "No index.pdf produced -- check typst_documents wiring landed "
            f"and no fatal TypstCompilationError occurred:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert pdf_path.stat().st_size > 0, "PDF file is empty"
        with open(pdf_path, "rb") as f:
            magic = f.read(4)
            assert magic == b"%PDF", "Generated file is not a valid PDF"

        # SC#2 byproduct: the unknown_visit frequency catalogue from the
        # same build's captured stderr.
        catalogue = catalogue_unknown_visit(result.stderr)
        assert catalogue, (
            "Expected the unknown_visit catalogue to be non-empty (SC#2 "
            "raw material) -- the full corpus is expected to exercise at "
            "least some not-yet-handled node types"
        )
        print(f"Unknown Visit Catalogue: {catalogue.most_common()}")


# ============================================================================
# SC#3: empty-URL before/after measurement (D-07)
# ============================================================================
#
# METHODOLOGY ADJUSTMENT (deviates from 15-02-PLAN.md's literal D-07 wording
# -- see 15-02-SUMMARY.md "Deviations" for the full rationale):
#
# The plan's original mechanism was `git worktree add --detach <dir>
# 79c9d45~1` -- checking out the WHOLE tree as it existed immediately before
# the XREF-01 fix. That was written before this phase's in-flight campaign
# fixed 25 pre-existing production bugs to get GATE-02 green: 55 commits
# landed AFTER 79c9d45, heavily overhauling translator.py's
# reference/anchor handling AND adding the entire Phase 13-14 node-handler
# surface. A `79c9d45~1`-vs-HEAD diff today would conflate the XREF-01
# effect with that whole campaign, violating D-07's actual INTENT
# ("quantify the reduction delivered by the XREF-01 fix") even though it
# matches D-07's literal original wording.
#
# The faithful isolation (D-07's exact mechanism is Claude's Discretion per
# CONTEXT.md): the "before" translator is current HEAD with ONLY XREF-01's
# `depart_term` id-anchor emission disabled. Concretely,
# `checkout_pre_xref01_translator` creates a `git worktree add --detach
# <dir> HEAD` (branched from HEAD, NOT `79c9d45~1`), then applies a minimal
# in-worktree source edit to that worktree's `typsphinx/translator.py`
# removing exactly the `if node.get("ids"):` label-anchor block XREF-01
# added to `depart_term` (see `git show 79c9d45`) -- reproducing
# pre-XREF-01 `depart_term` behavior on top of all current code. The
# "after" translator is HEAD as-installed, unmodified. This keeps Phases
# 11-14 and all 25 campaign fixes present in BOTH builds, varying ONLY the
# XREF-01 `depart_term` anchor -- a clean, single-variable isolation of the
# XREF-01 effect.
#
# `FIX_COMMIT` is retained as a documentation constant naming the commit
# whose `depart_term` behavior is reverted; it is no longer passed to `git
# worktree add` directly (that now targets `HEAD`).

FIX_COMMIT = "79c9d45"  # fix(12-02): emit bracket-wrap <label> anchor in depart_term

# The exact `depart_term` block `79c9d45` added (verified via `git show
# 79c9d45 -- typsphinx/translator.py`), as it stands in the CURRENT source
# (the `label_id` line gained a `self._namespace_label(...)` wrap in a later
# campaign commit -- matched verbatim against today's HEAD, not the literal
# 79c9d45 diff, since the worktree is created FROM HEAD). Matching verbatim
# means a future refactor of `depart_term` makes
# `checkout_pre_xref01_translator` fail loudly (ValueError) instead of
# silently no-op'ing and measuring "before" == "after".
_DEPART_TERM_LABEL_ANCHOR_BLOCK = (
    '        if node.get("ids"):\n'
    "            label_id = self._namespace_label(self._current_docname(), "
    'node["ids"][0])\n'
    '            term_content = f"[#{{{term_content}}} <{label_id}>]"\n'
    "\n"
    "        # Store term for later (will be paired with definition)\n"
    "        self.current_term_buffer = term_content"
)

_DEPART_TERM_REVERTED = (
    "        # Store term for later (will be paired with definition)\n"
    "        self.current_term_buffer = term_content"
)


def checkout_pre_xref01_translator(repo_root: Path, worktree_dir: Path) -> None:
    """Create an isolated worktree at HEAD, then apply a minimal in-place
    edit reverting ONLY XREF-01's `depart_term` id-anchor emission --
    reproducing pre-XREF-01 `depart_term` behavior on top of all current
    code (Phases 11-14 + this phase's 25 campaign fixes). See the
    METHODOLOGY ADJUSTMENT note above for why this checks out `HEAD`
    (not `79c9d45~1`).

    The worktree is a fully isolated, read-only-relative-to-the-main-tree
    checkout (T-15-04) -- NEVER `git stash`, which would mutate the live
    working tree an agent/user session may still be operating in. The
    in-worktree source edit only touches the worktree's own copy of
    `typsphinx/translator.py`; the main working tree's `typsphinx/translator.py`
    is never opened for writing by this function.
    """
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree_dir), "HEAD"],
        cwd=repo_root,
        check=True,
    )

    translator_py = worktree_dir / "typsphinx" / "translator.py"
    original_text = translator_py.read_text(encoding="utf-8")
    if _DEPART_TERM_LABEL_ANCHOR_BLOCK not in original_text:
        raise ValueError(
            "checkout_pre_xref01_translator: depart_term's id-anchor block "
            "was not found verbatim in the worktree's translator.py -- "
            "translator.py has likely been refactored since this helper "
            "was written; update _DEPART_TERM_LABEL_ANCHOR_BLOCK to match "
            "the current source before re-running the SC#3 measurement."
        )
    patched_text = original_text.replace(
        _DEPART_TERM_LABEL_ANCHOR_BLOCK, _DEPART_TERM_REVERTED, 1
    )
    translator_py.write_text(patched_text, encoding="utf-8")


# Anchored on the literal warning-line prefix emitted in visit_reference
# (translator.py's empty-URL guard: `logger.warning(f"Reference node has
# empty URL. ...")`), held constant across both the before and after builds.
EMPTY_URL_SIGNATURE = "Reference node has empty URL"


def count_empty_url_warnings(stderr_text: str) -> int:
    """Count `Reference node has empty URL` occurrences in captured stderr
    (SC#3). A plain substring count is safe here -- unlike `unknown_visit`
    (Pitfall 4), this warning does not embed a multi-line node dump; the
    counted signature is a fixed prefix on a single logical warning line.
    """
    return stderr_text.count(EMPTY_URL_SIGNATURE)


def test_count_empty_url_warnings():
    """
    Fast (non-slow, no network) unit test for the SC#3 counter: a synthetic
    3-occurrence stderr string and a zero-occurrence string.
    """
    three_occurrences = (
        "WARNING: Reference node has empty URL. Link will be rendered as "
        "plain text. Check for broken references in source: foo\n"
        "WARNING: Reference node has empty URL. Link will be rendered as "
        "plain text. Check for broken references in source: bar\n"
        "WARNING: Reference node has empty URL. Link will be rendered as "
        "plain text. Check for broken references in source: baz\n"
    )
    assert count_empty_url_warnings(three_occurrences) == 3

    zero_occurrences = "WARNING: unknown node type: <citation>\n"
    assert count_empty_url_warnings(zero_occurrences) == 0


@pytest.mark.slow
def test_empty_url_before_after(corpus_doc_dir, tmp_path):
    """
    SC#3: measure the empty-URL cross-reference warning-count reduction
    delivered by the XREF-01 fix, by rebuilding the SAME corpus twice --
    once with `depart_term`'s XREF-01 label-anchor emission disabled (the
    "before" translator, see `checkout_pre_xref01_translator`'s
    METHODOLOGY ADJUSTMENT note above), once as-shipped HEAD (the "after"
    translator) -- diffing the `Reference node has empty URL` warning
    counts. Both builds use `-b typst` (translate-phase only, NEVER `-b
    typstpdf`/`typst.compile()`) so the reverted `depart_term`'s dangling
    `:term:` glossary label cannot fatally abort the measurement (RESEARCH
    Pitfall 2 -- the glossary IS in the corpus's toctree).

    Env-gated behind `TYPSPHINX_CORPUS_REPORT=1` so this does NOT add two
    extra corpus builds to a routine `pytest -m slow` run (RESEARCH Open
    Question 1) -- reproducible and git-tracked, but not folded into the
    standing SC#1 gate. No new pytest marker is introduced (pyproject.toml's
    `--strict-markers` would reject an unregistered one); the env var is
    the gate instead.
    """
    if os.environ.get("TYPSPHINX_CORPUS_REPORT") != "1":
        pytest.skip(
            "SC#3 before/after measurement is env-gated -- set "
            "TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)"
        )

    repo_root = Path(__file__).resolve().parents[1]
    worktree_dir = tmp_path / "pre-xref01-worktree"
    checkout_pre_xref01_translator(repo_root, worktree_dir)
    try:
        # Idempotent -- both builds share the same wired corpus conf.py.
        wire_typsphinx_into_corpus_conf(corpus_doc_dir)

        # BEFORE: PYTHONPATH prepended (our override wins over any
        # pre-existing PYTHONPATH in the inherited environment) so the
        # worktree's patched translator shadows the installed typsphinx for
        # THIS subprocess only (T-15-05) -- the after build and the rest of
        # the process are unaffected.
        before_env = {**os.environ, "PYTHONPATH": str(worktree_dir)}
        before_result = _run_corpus_sphinx_build(
            "typst", corpus_doc_dir, tmp_path / "before", env=before_env
        )

        # AFTER: as-installed typsphinx, no PYTHONPATH override.
        after_result = _run_corpus_sphinx_build(
            "typst", corpus_doc_dir, tmp_path / "after"
        )

        before = count_empty_url_warnings(before_result.stderr)
        after = count_empty_url_warnings(after_result.stderr)
        delta = before - after
        print(f"Empty-URL warnings BEFORE (XREF-01 anchor disabled): {before}")
        print(f"Empty-URL warnings AFTER  (as-shipped HEAD):         {after}")
        print(f"Delta (reduction): {delta}")

        # The fix cannot INCREASE empty-URL warnings. No exact-magnitude
        # assertion -- the corpus is external and may drift (SC#3 wording).
        assert after <= before, (
            "XREF-01 fix should not increase empty-URL warnings: "
            f"before={before}, after={after}"
        )
    finally:
        # Cleanup regardless of outcome (T-15-04) -- never leave a stray
        # worktree registered against the main repo.
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree_dir)],
            cwd=repo_root,
            check=False,
        )
