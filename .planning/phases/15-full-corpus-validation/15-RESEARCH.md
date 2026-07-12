# Phase 15: Full-Corpus Validation - Research

**Researched:** 2026-07-12
**Domain:** Corpus-scale real-compile validation (git-cloned external test fixture, warning-stream capture/parsing, controlled before/after regression measurement)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Obtain Sphinx's `doc/` tree by **shallow `git clone` at a pinned tag**
  that matches the installed Sphinx version (the v9.1.x line typsphinx pins to).
  Sphinx's `doc/` tree is **not** shipped in the pip package — it exists only in
  the Sphinx source repo — so the corpus must be fetched. Prefer the tag matching
  `sphinx.__version__` so the corpus and the compiler-facing Sphinx agree.
- **D-02:** Scope is the **full `doc/` tree**, not a curated subset — faithful to
  the GATE-02 wording ("Sphinx's own `doc/` tree") and the "full-corpus" phase
  name. A subset was rejected as diverging from the milestone gate.
- **D-03:** Build with **Sphinx's real `doc/conf.py`** as-is (only adding the
  `typstpdf` builder / `typsphinx` to `extensions`), for real-world fidelity —
  not a stripped minimal conf. The real conf loads Sphinx-internal extensions
  and the source tree's local `sphinxext/` modules; those must be importable from
  the clone. **Researcher risk to resolve:** the real conf may pull doc-build-only
  extensions/deps not in typsphinx's env (e.g. `sphinxcontrib.*`,
  `sphinx-notfound-page`, local `sphinxext/`). Decide install-vs-degrade before
  planning; if a hard block, a documented minimal-conf fallback is the escape
  hatch (but the intent is the real conf).
- **D-04:** GATE-02 lands as a **`slow`-marked standing pytest test** (same
  `sphinx-build → typst.compile() → pypdf` lineage as the GATE-01 render gates),
  **excluded from the default/CI fast suite** via the existing `slow` marker
  (`-m "not slow"`). It stays reproducible and on-demand rather than burdening CI
  with a net-dependent, slow, corpus-scale build. Rejected: one-time throwaway
  script (loses regression re-runnability) and a dedicated always-on CI job
  (net-dependent, slow, flaky, high maintenance).
- **D-05:** When the corpus can't be obtained (**no network / clone failure**),
  the test **`pytest.skip`s** (does not fail) — standard slow-test hygiene so
  offline/CI/sandbox runs stay green. The gate is meaningful only when the corpus
  is actually present.
- **D-06:** Record both measurements in a committed **`15-CORPUS-REPORT.md`** in
  the phase directory: the frequency-ranked `unknown_visit` catalogue and the
  empty-URL before/after numbers. This report is the **next milestone's backlog
  input** — no separate GitHub issue or `.planning` backlog file for this phase.
- **D-07:** Measure empty-URL **before/after** by re-building the *same* corpus
  with the **XREF-01 change reverted via git** (revert/stash the Phase-12
  `translator.py` XREF-01 edits — `depart_reference` `refid` branch +
  `depart_term` `<label>` anchor, landed in `12-02-PLAN`; anchor commit
  `79c9d45 fix(12-02): emit bracket-wrap <label> anchor in depart_term`), then
  diffing the empty-URL / `link("", …)`-class warning counts against the
  as-shipped build. This produces a credible "before" number now that the fix is
  already landed, rather than trusting a remembered baseline.

  > **Research correction (verified via `git show`/`12-02-SUMMARY.md`):** the
  > single commit `79c9d45` touched **only `depart_term`** (14 lines). The
  > `refid` branch in `visit_reference` (`if not refuri and refid: ... link(<{refid}>, ...)`)
  > was landed earlier, in **Phase 11** (`f617944 feat(11-02): add refid
  > fallback branch to visit_reference`), and Phase 12's own plan explicitly
  > states it was **confirmed-and-covered, not modified**. Reverting
  > `visit_reference`'s refid branch too would conflate FIG-02 and XREF-01
  > effects and is out of scope for this measurement. **The correct, precise
  > revert target for D-07 is `git show 79c9d45` applied in reverse to
  > `typsphinx/translator.py` only** (see Pattern 3 / Code Examples below).

### Claude's Discretion

- Exact clone mechanism (subprocess `git`, cached temp dir, tag-resolution from
  `sphinx.__version__`), report table shape, and how warnings are captured from
  the Sphinx warning stream vs. typsphinx's own `logger.warning` — planner/
  researcher choice, as long as D-01…D-07 hold.

### Deferred Ideas (OUT OF SCOPE)

- **Measurement recording as a GitHub issue / `.planning` backlog file** —
  considered for D-06; chose an in-phase `15-CORPUS-REPORT.md` instead. If the
  next milestone wants a tracked backlog, promote the report's catalogue then.
- **Discussing the measurement details interactively** — user opted to lock
  D-06/D-07 via recommended defaults rather than a deep-dive; revisit only if the
  before/after revert proves impractical.
- Broadening `docs-pdf` CI to macOS/Windows (**XOS-01**) and configurable
  `@preview` versions (**CFG-01**) remain v2 out-of-scope (carried from PROJECT.md).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GATE-02 | Sphinx's own `doc/` tree compiles end-to-end through `typstpdf` with no fatal `TypstCompilationError`; the remaining `unknown_visit` warnings are catalogued by frequency and the empty-URL warning-count reduction is measured before/after | D-03 real-conf viability resolved (near-zero risk — see Summary); D-01 clone mechanism verified against the live GitHub tag; unknown_visit warning-format empirically captured (this session); D-07 before/after methodology corrected and made reproducible without a fatal-abort trap; GATE-01 harness pattern (`_run_sphinx_build_typst`) extended for a corpus-scale sibling test |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- Python 3.10+ compatibility required (installed dev env is 3.12/3.13 per `pyproject.toml`, but ruff intentionally targets 3.10-compatible syntax — do not "modernize" typing imports in any new test-helper code).
- Line length 88 (black); `E501` ignored in ruff (black owns wrapping) — apply to the new `tests/test_corpus_gate.py` module and `15-CORPUS-REPORT.md`-generation helper code.
- `N802` is ignored in ruff (docutils visitor PascalCase methods) — irrelevant to this phase (no new `visit_*`/`depart_*` methods; translator.py is read-only this phase except for the D-07 revert, which is a git-level operation on a worktree/patch, not a permanent source edit).
- `tox.ini` pins `tox-uv~=1.35` deliberately — not touched this phase.
- CI matrix (`ci.yml`) runs py310–py313 + lint + type + cov; the new corpus test MUST stay `slow`-marked so it is excluded from that matrix by the existing `-m "not slow"` fast-suite convention (already used by CI; no CI config change needed).
- This project's dev sandbox has a documented NixOS `uv run <compiled-binary>` hazard (see below) — any new subprocess invocation of Sphinx must use the `sys.executable -m sphinx` pattern already established in `_run_sphinx_build_typst`, never `["uv", "run", "sphinx-build", ...]`.

## Summary

This phase adds exactly one new capability: a `slow`-marked pytest module that
clones Sphinx's own `doc/` tree at the tag matching the installed `sphinx.__version__`,
builds it through typsphinx's `typstpdf` builder, and asserts no fatal
`TypstCompilationError` — plus a one-time (not CI-gated) measurement pass that
produces `15-CORPUS-REPORT.md`. No translator.py behavior changes, no new
runtime dependencies. All work is test/CI scaffolding.

**The #1 flagged risk (D-03: does the real `doc/conf.py` pull deps typsphinx's
env doesn't have?) is resolved to near-zero.** This session fetched Sphinx's
actual `doc/conf.py` at tag `v9.1.0` (the exact tag this repo's installed
`sphinx==9.1.0` resolves to — confirmed to exist via `git ls-remote`) directly
from GitHub and inspected it in full: `extensions` contains **only
`sphinx.ext.*` built-ins** (`autodoc`, `doctest`, `todo`, `autosummary`,
`extlinks`, `intersphinx`, `viewcode`, `inheritance_diagram`, `coverage`,
`graphviz`) — all of which ship inside the `sphinx` package itself, already
installed. There is **no `sphinxcontrib.*` extension, no `sphinx-notfound-page`,
and no local `doc/sphinxext/` package** referenced anywhere in `extensions` or
imported at module level (confirmed both by reading the file and by listing the
full `doc/` tree at that tag via the GitHub API — no `sphinxext/` directory
exists). `html_theme`/`html_theme_path` reference a **local, in-repo** theme
(`doc/_themes/sphinx13`) that is HTML-builder-specific and never touched by a
non-HTML builder like `typstpdf`. **Conclusion: D-03's install-vs-degrade
decision is "install nothing extra — the real conf.py already just works" —
no minimal-conf fallback is needed.** This contradicts the CONTEXT.md's
flagged assumption (which was written from training-data recall, not a live
check) and should be treated as the corrected, verified finding.

The one thing the real `doc/conf.py` genuinely lacks — because it was never
written with typsphinx in mind — is the `typsphinx`-specific `extensions`
entry and a `typst_documents` config value (a typsphinx-only config value;
`TypstPDFBuilder.finish()` silently no-ops with a warning and compiles
**nothing** if it's absent, which would make GATE-02 pass trivially without
ever exercising `typst.compile()` — this is the single most important
implementation landmine in this phase, see Pitfall 1). The fix is a **two-line
append** to the cloned conf.py (`extensions.append("typsphinx")` +
`typst_documents = [...]`) done programmatically after cloning, into the
ephemeral clone only — never touching the upstream Sphinx repo, and still
"the real conf.py" per D-03's fidelity intent (append-only, no rewrite/strip).

A second major finding concerns **D-07's before/after methodology**: because
`index.rst`'s toctree transitively includes `doc/glossary.rst` (confirmed via
GitHub raw fetch), the full-corpus PDF **will** contain `:term:` cross-references
into the glossary. Reverting `79c9d45` (the `depart_term` label-anchor fix) and
then running `typst.compile()` against the full corpus would hit the *exact*
fatal `label <term-id> does not exist` abort the fix was written to close —
Typst's `#include()` compile is all-or-nothing, so the "before" PDF-compile
step would never complete, making a warning-*count* diff impossible if compile
is attempted. The fix: the empty-URL warning is emitted during the
**translate/write phase** (`sphinx-build -b typst`, in `visit_reference`),
which is a **separate, earlier phase** from the **PDF-compile phase**
(`typst.compile()`, only invoked in `TypstPDFBuilder.finish()` for `typstpdf`).
The before/after measurement should run **`-b typst`** (not `-b typstpdf`) for
**both** the before and after builds — this captures the warning stream
without ever needing `typst.compile()` to succeed on the reverted "before"
translator, sidestepping the fatal-abort trap entirely. SC#1's fatal-compile
proof remains a separate, `-b typstpdf`, as-shipped-only (HEAD) build.

Two more empirically-verified findings for the warning catalogue (SC#2):
`unknown_visit`'s `logger.warning(f"unknown node type: {node}")` call uses
Python's `str()` on the docutils node, which for `Element` subclasses returns
the node's **full untruncated XML-ish subtree serialization**, potentially
spanning multiple physical lines if the node's text content contains newlines
(reproduced empirically this session with a `citation` node). Frequency
counting must extract only the outer tag name via a regex anchored on the
literal `"WARNING: unknown node type: <"` prefix, never attempt to treat the
whole multi-line warning as a single log line. Also empirically confirmed:
these warnings carry **no docname:line location prefix** (Sphinx only attaches
that automatically during the *reading* phase; `unknown_visit` fires during
*writing*), so the catalogue is necessarily corpus-wide, not per-file — which
matches SC#2's "catalogued by frequency" wording exactly (no per-file breakdown
required).

**Primary recommendation:** Add `tests/test_corpus_gate.py` (a new sibling
module, not a class appended to `test_pdf_render_gate.py`) containing a
`slow`-marked, skip-on-unavailable test class that (1) resolves the corpus tag
from `sphinx.__version__`, (2) shallow-clones it to a cached temp dir, (3)
appends the two-line typsphinx wiring to the clone's `conf.py`, (4) runs
`sphinx-build -b typstpdf` via the established `sys.executable -m sphinx`
subprocess pattern, (5) asserts `returncode == 0` and every `typst_documents`
PDF exists/is non-empty/starts with `%PDF` (the SC#1 fatal-free proof), and (6)
parses `unknown node type` warnings from stderr into a frequency table. A
second, separate one-time procedure (documented as a repeatable script/helper,
not a CI-gated assertion) performs the D-07 before/after `-b typst` comparison
using a `git worktree` checkout of `79c9d45~1`. Both outputs are written into
`15-CORPUS-REPORT.md` per D-06.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Corpus acquisition (git clone) | Test/CI scaffolding | — | Not part of the shipped package; lives entirely in `tests/` as a fixture-acquisition helper, same tier as existing `tests/fixtures/*` conventions |
| conf.py augmentation (extensions + typst_documents) | Test/CI scaffolding | — | Mutates only the ephemeral clone, never the shipped `typsphinx` config surface (`__init__.py`'s `add_config_value` calls are untouched) |
| `sphinx-build -b typstpdf` execution | Builder (existing, unmodified) | Test/CI scaffolding (invocation only) | Exercises `typsphinx.builder.TypstPDFBuilder` exactly as shipped; the test only drives it via subprocess, no builder code changes |
| `typst.compile()` fatal-check | Builder (existing, unmodified) | Test/CI scaffolding (assertion) | `TypstPDFBuilder.finish()` already calls `compile_typst_to_pdf`; the test asserts on its outcome, doesn't reimplement it |
| Warning-stream capture/parsing | Test/CI scaffolding | — | New regex/Counter logic lives in the test module only; `typsphinx/translator.py`'s `logger.warning` calls are read, not modified |
| D-07 before/after revert | Test/CI scaffolding (git worktree) | — | A git-level operation over a second checkout; no `typsphinx/translator.py` edit ships in this phase's final state |
| Report generation (`15-CORPUS-REPORT.md`) | Planning documentation | — | Consumed by the next milestone's scoping, not by any runtime code path |

## Standard Stack

### Core

No new dependencies. This phase reuses the project's existing runtime and dev
dependencies exclusively:

| Library | Version (verified installed) | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `sphinx` | 9.1.0 `[VERIFIED: uv run python -c "import sphinx; print(sphinx.__version__)"]` | Drives the corpus build via `sphinx-build -b typstpdf` | Already the project's pinned Sphinx version (`>=9.1,<10`); the corpus tag is resolved FROM this exact version, guaranteeing compiler/corpus agreement (D-01 intent) |
| `typst` (typst-py) | 0.15.0 `[VERIFIED: uv run python -c "import typst; print(typst.__version__)"]` | Compiles the master `.typ` to PDF via `typst.compile()` (already wrapped by `typsphinx/pdf.py`) | Existing project dependency; no version change |
| `pypdf` | 6.14.2 `[VERIFIED: uv run python -c "import pypdf; print(pypdf.__version__)"]` | Optional — only needed if the report wants to text-extract the compiled corpus PDF for a spot-check; not required for the fatal-check itself (which only needs the PDF file to exist/be non-empty/start with `%PDF`, per the GATE-01 harness convention) | Existing dev dependency (`pyproject.toml` `dev` extras) |
| `git` (system) | 2.54.0 `[VERIFIED: git --version]` | Shallow-clones the corpus, and (for D-07) provides `git worktree` to check out the pre-fix translator revision | Already used by the dev workflow; no new install |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `re` (stdlib) | — | Regex extraction of `unknown node type: <TAG` from multi-line stderr | Frequency catalogue parsing (SC#2) |
| `collections.Counter` (stdlib) | — | Tally warning-tag frequency | Frequency catalogue (SC#2) |
| `subprocess` (stdlib) | — | Invoke `sys.executable -m sphinx` (existing pattern) | All corpus builds — never `["uv", "run", ...]` (sandbox hazard) |
| `tempfile`/`pathlib` (stdlib) | — | Cached clone location, `git worktree` target | D-01 clone caching, D-07 revert checkout |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `git clone --depth 1 --branch <tag>` (D-01, locked) | `pip download sphinx==X --no-binary :all:` and extract `doc/` from the sdist | Sphinx's PyPI sdist does **not** include `doc/` (confirmed by D-01's own rationale in CONTEXT.md — "not shipped in the pip package"); rejected, not viable |
| `git worktree add <tmp> 79c9d45~1` (recommended for D-07) | `git stash` the local working tree, revert, build, `git stash pop` | Stash mutates the actual working tree the agent/user is operating in — any concurrent session or uncommitted work is at risk; worktree is a fully isolated, zero-risk read-only checkout that can be deleted afterward with no side effects on the main tree |
| `git worktree add` (recommended) | In-process `monkeypatch.setattr` on `TypstTranslator.depart_term` | Monkeypatch state does **not** cross the `subprocess.run(["sys.executable", "-m", "sphinx", ...])` process boundary the existing harness uses, so it would require abandoning the proven subprocess pattern in favor of an in-process `sphinx.application.Sphinx()` instantiation — which carries its own Sphinx-testing pitfall (global extension/domain registry state can leak across repeated in-process `Sphinx()` instantiations without careful cleanup). Worktree keeps the subprocess model intact |
| `-b typstpdf` for the D-07 before/after build (rejected) | `-b typst` for the D-07 before/after build (recommended) | `-b typstpdf` would additionally invoke `typst.compile()` in `finish()`, which the reverted "before" translator will fatal-abort on (dangling `:term:` label — the glossary IS in the toctree, confirmed via GitHub fetch); `-b typst` only runs the translate/write phase where the empty-URL warning is actually emitted, with no compile step to fail |

**Installation:** None — no new packages.

**Version verification:** All versions above were confirmed live against the
project's `uv`-managed environment in this session (`uv run python3 -c "import X; print(X.__version__)"` for each), not assumed from training data or `pyproject.toml` version ranges.

## Package Legitimacy Audit

**N/A — no new external packages are introduced by this phase.** All tooling
(`sphinx`, `typst`, `pypdf`, `git`) is either an existing project dependency
already vetted in prior milestones, or a system tool (`git`) with no
package-registry supply-chain surface. No `package-legitimacy check` run was
needed; no packages were removed or flagged.

## Architecture Patterns

### System Architecture Diagram

```
sphinx.__version__ (installed, e.g. "9.1.0")
        |
        v
  [tag resolution]  ---->  "v9.1.0"  (verified live: exists as a real tag
        |                             on github.com/sphinx-doc/sphinx)
        v
  [git clone --depth 1 --branch v9.1.0 ...]
        |                       \
        | (network / clone       \--> FAILS --> pytest.skip (D-05)
        |  failure path)
        v
  <cached-tmp>/sphinx-v9.1.0/doc/   (154 .rst files, real doc/conf.py)
        |
        v
  [append 2 lines to conf.py:
     extensions.append("typsphinx")
     typst_documents = [("index", ..., ...)]]
        |
        v
  ================== SC#1: fatal-compile proof (AS-SHIPPED translator) ==================
  sphinx-build -b typstpdf <clone>/doc <outdir>      (subprocess: sys.executable -m sphinx)
        |                                    \
        | writes N .typ files                 \--> writes to stderr: unknown_visit warnings,
        | (write phase, ALWAYS completes)          empty-URL warnings, etc. for EVERY docname
        v
  TypstPDFBuilder.finish()
        |
        v
  typst.compile(index.typ) --------> [FATAL?] --> TypstCompilationError --> test FAILS (GATE-02 broken)
        |
        v (no fatal)
  index.pdf exists, non-empty, starts with %PDF --> SC#1 PASS
        |
        v
  [parse captured stderr with regex: r"WARNING: unknown node type: <(\w+)"]
        |
        v
  Counter({tag: count, ...}) sorted desc --> SC#2 catalogue
  ================== SC#3: before/after empty-URL count (translate-phase ONLY) ===========
  git worktree add <tmp2> 79c9d45~1        git worktree at HEAD (or plain checkout)
        |                                          |
        v                                          v
  sphinx-build -b typst  <clone>/doc  <out-before>   sphinx-build -b typst  <clone>/doc  <out-after>
  (PYTHONPATH prepended with <tmp2> so the           (as-installed typsphinx, no override)
   pre-79c9d45 translator.py shadows the
   installed one for THIS subprocess only)
        |                                          |
        v                                          v
  count "Reference node has empty URL" in stderr    count "Reference node has empty URL" in stderr
        \_______________________  diff  ___________________/
                                v
                    15-CORPUS-REPORT.md (D-06)
```

### Recommended Project Structure

```
tests/
├── test_pdf_render_gate.py         # UNCHANGED — self-contained fixture-project
│                                    #   gates only (GATE-01 lineage); do not
│                                    #   append the corpus class here (see Pitfall 5)
├── test_corpus_gate.py             # NEW — GATE-02, imports LEAK_SIGNATURES /
│                                    #   _run_sphinx_build_typst-style helpers
│                                    #   from test_pdf_render_gate for reuse
├── conftest.py                     # UNCHANGED (or extend with a
│                                    #   `sphinx_corpus_clone` session-scoped
│                                    #   fixture if the planner wants to share
│                                    #   the clone across the corpus module —
│                                    #   optional, see Pitfall 3)
└── fixtures/                       # UNCHANGED — the corpus is NOT added here;
                                     #   it is an ephemeral external clone in a
                                     #   cached tmp dir, not a committed fixture

.planning/phases/15-full-corpus-validation/
├── 15-RESEARCH.md                  # this file
├── 15-CORPUS-REPORT.md             # NEW — D-06 output (SC#2 catalogue +
                                     #   SC#3 before/after numbers), committed
```

### Pattern 1: Tag resolution from `sphinx.__version__` (D-01)

**What:** Resolve the exact git tag to shallow-clone from the live, installed
Sphinx version string.
**When to use:** At test-setup time, before attempting the clone.
**Verified this session:** `sphinx.__version__` in this environment is the
clean string `"9.1.0"` (no dev/local suffix), and `git ls-remote --tags
https://github.com/sphinx-doc/sphinx.git` confirms `refs/tags/v9.1.0` exists.
```python
# Source: verified this session via `uv run python3 -c "import sphinx; ..."`
# and `git ls-remote --tags https://github.com/sphinx-doc/sphinx.git`
import sphinx

def resolve_corpus_tag() -> str:
    """Resolve the git tag matching the installed Sphinx version.

    Sphinx tags its releases as `vX.Y.Z` (confirmed live: v9.1.0 exists).
    A dev/pre-release suffix (e.g. "9.1.0.dev0") would not match any real
    tag -- callers must treat a clone failure at this tag as a D-05 skip
    condition, not a hard test failure.
    """
    return f"v{sphinx.__version__}"
```
**Pitfall guard:** if `sphinx.__version__` ever carries a `.devN`/`+local`
suffix (e.g. an editable/pre-release install), `git clone --branch
v9.1.0.dev0` will fail with a normal "couldn't find remote ref" error —
this must flow into the SAME `pytest.skip` path as a network failure (D-05
generalizes to "tag not resolvable", not just "no network").

### Pattern 2: Real-conf augmentation via append, not overlay (D-03)

**What:** Wire `typsphinx` into the cloned, unmodified `doc/conf.py` by
appending two lines to the end of the file after cloning — never replacing or
stripping the original content.
**When to use:** Once per clone, before invoking `sphinx-build`.
**Verified reasoning:** Sphinx's config loader execs the *entire* `conf.py`
source into one namespace dict in a single pass (`eval_config_file`-style),
so appended lines see the fully-populated `extensions` list already defined
earlier in the same file, and the resulting `typst_documents`/mutated
`extensions` are both present in the final namespace Sphinx reads — order of
appearance in the file doesn't matter once the whole file has executed.
```python
# Source: derived from typsphinx/__init__.py's add_config_value("typst_documents", [], ...)
# and empirical inspection of doc/conf.py's structure (this session, GitHub raw fetch).
from pathlib import Path

def wire_typsphinx_into_corpus_conf(corpus_doc_dir: Path) -> None:
    """Append typsphinx wiring to the cloned doc/conf.py (mutates the
    EPHEMERAL clone only -- never the real upstream Sphinx repo).

    `extensions` is guaranteed to already be a list at this point in the
    real conf.py (verified: `extensions = ['sphinx.ext.autodoc', ...]` is
    defined near the top of the file). `typst_documents` is a name Sphinx's
    own conf.py never defines (typsphinx-only config value), so there is no
    collision risk appending it fresh.
    """
    conf_py = corpus_doc_dir / "conf.py"
    with conf_py.open("a", encoding="utf-8") as f:
        f.write("\n\n# --- typsphinx corpus-gate wiring (test-only, not upstream) ---\n")
        f.write("extensions.append('typsphinx')\n")
        f.write(
            "typst_documents = [('index', 'sphinx-corpus', "
            "'Sphinx Documentation', 'the Sphinx developers')]\n"
        )
```
**Alternative (not recommended as primary):** a separate `-c <overlay_confdir>`
pointing Sphinx at a small `conf.py` that does `from conf import *` after
`sys.path.insert(0, str(corpus_doc_dir))`. This keeps the clone byte-for-byte
untouched, but relies on Sphinx's `eval_config_file`'s `cd()`/sys.path
handling behaving as expected for a `from X import *` inside an exec'd
namespace — a mechanism this research did **not** empirically verify (LOW
confidence). Prefer the append-in-place technique above; it was reasoned
through Sphinx's actual config-loading model and needs no import-machinery
assumptions. If the append technique is rejected for auditability reasons,
verify the overlay alternative with a real dry run before relying on it.

### Pattern 3: D-07 before/after via `git worktree` + `-b typst` only

**What:** Get a clean, isolated checkout of the translator.py revision
immediately before the XREF-01 fix, and measure empty-URL warnings using only
the translate phase (never `typst.compile()`) so the reverted translator's
known-fatal `:term:` case cannot abort the measurement.
**When to use:** Once, for the SC#3 measurement recorded into
`15-CORPUS-REPORT.md` — not a per-run CI assertion (D-06 routes this to a
report, not a standing regression gate).
```python
# Source: reasoned from `git show 79c9d45 --stat` (14 insertions, 1 deletion,
# single file typsphinx/translator.py) and the empirical finding that
# doc/index.rst's toctree transitively includes doc/glossary.rst (this
# session, GitHub raw fetch) -- meaning a :term: xref WILL reach the
# reverted depart_term during any typst.compile() attempt.
import subprocess
import sys
from pathlib import Path

FIX_COMMIT = "79c9d45"  # fix(12-02): emit bracket-wrap <label> anchor in depart_term

def checkout_pre_fix_translator(repo_root: Path, worktree_dir: Path) -> None:
    """Create an isolated worktree at the commit immediately BEFORE the
    XREF-01 depart_term fix. Read-only relative to the main working tree --
    safe to run alongside an active session (unlike `git stash`)."""
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree_dir), f"{FIX_COMMIT}~1"],
        cwd=repo_root, check=True,
    )

def run_translate_only(corpus_doc_dir: Path, outdir: Path, typsphinx_pythonpath: Path) -> str:
    """Run sphinx-build -b typst (NOT typstpdf) so no typst.compile() step
    is attempted -- the reverted translator's dangling :term: label would
    otherwise abort compilation of the corpus's glossary-referencing pages
    before any warning count could be captured. Returns captured stderr."""
    env = {"PYTHONPATH": str(typsphinx_pythonpath)}  # prepend, don't replace
    result = subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typst", str(corpus_doc_dir), str(outdir)],
        capture_output=True, text=True, env=env,
    )
    return result.stderr

# Usage: build "before" with checkout_pre_fix_translator()'s worktree on
# PYTHONPATH, build "after" with the normally-installed typsphinx (no
# PYTHONPATH override), then count "Reference node has empty URL" in each
# stderr and diff.
```

### Pattern 4: `unknown_visit` frequency catalogue parsing (SC#2)

**What:** Robustly extract per-node-type counts from a warning stream where
each warning may itself be multi-line (the node's own text content can embed
literal newlines).
**Empirically verified this session** (constructed a `citation` fixture with
no `visit_citation` handler and ran a real `sphinx-build -b typst`):
```
WARNING: unknown node type: <citation backrefs="id1" docname="index" ids="cit2002" names="cit2002"><label support_smartquotes="0">CIT2002</label><paragraph>A citation
spanning multiple lines with some more descriptive content that is long.</paragraph></citation>
WARNING: unknown node type: <label support_smartquotes="0">CIT2002</label>
```
Two key findings from this output:
1. **No `docname:line` location prefix** — `logger.warning()` here is called
   without a `location=` kwarg, and no ambient location context is attached
   during the *writing* phase (unlike the *reading* phase, where Sphinx
   often auto-prefixes warnings with the source file). The catalogue is
   necessarily corpus-wide, not per-file.
2. **Nested unknown nodes each fire their own independent warning** — the
   `<label>` child of the unhandled `<citation>` got its own separate
   warning line, because `unknown_visit` does not raise `SkipNode`/
   `SkipChildren` (confirmed in `.planning/research/ARCHITECTURE.md`), so
   docutils' default traversal continues descending and re-triggers
   `unknown_visit` for every unhandled descendant too. This is expected and
   correct for frequency counting per node TYPE (a `<citation>` containing an
   unhandled `<label>` correctly increments both `citation` and `label`).
```python
# Source: verified empirically this session (ad hoc citation fixture +
# `uv run python3 -m sphinx -b typst ...`).
import re
from collections import Counter

UNKNOWN_NODE_RE = re.compile(r"^WARNING: unknown node type: <(\w+)", re.MULTILINE)

def catalogue_unknown_visit(stderr_text: str) -> Counter:
    """Frequency-count unknown_visit warnings by outer node tag name.

    Anchored on the literal warning-line prefix (not on the full,
    potentially multi-line node dump) so embedded newlines in a node's own
    text content never cause a false split or a missed/duplicated count.
    """
    return Counter(UNKNOWN_NODE_RE.findall(stderr_text))
```

### Anti-Patterns to Avoid

- **Parsing `unknown_visit` warnings by splitting stderr on `"\n"` and
  counting matching lines:** the node's own text content can contain literal
  newlines (verified this session), silently under/over-counting. Always
  anchor on the `"WARNING: unknown node type: <"` prefix with `re.MULTILINE`.
- **Running `typst.compile()` against the D-07 "before" (reverted) build:**
  will fatally abort on the corpus's `:term:`→glossary cross-references
  (verified via `git show 79c9d45` + the toctree-includes-glossary finding),
  making a warning-count diff impossible. Use `-b typst` only for that
  specific measurement.
- **`git stash` for the D-07 revert:** mutates the live working tree an
  agent/user session may still be operating in. Use `git worktree add
  --detach <tmp> 79c9d45~1` instead — fully isolated, no side effects,
  trivially cleaned up with `git worktree remove`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Real-compile fatal-error detection | A custom Typst-error-string classifier | The existing `TypstCompilationError` from `typsphinx/pdf.py`, raised (uncaught, per the GATE-01 harness convention) by `typst.compile()` | Already the project's proven fatal-vs-warning boundary; every prior GATE-01 render-gate class relies on it propagating uncaught |
| Sphinx-build subprocess invocation | A new subprocess pattern | The existing `_run_sphinx_build_typst`-style `sys.executable -m sphinx` helper in `tests/test_pdf_render_gate.py` (import/reuse it, parameterized for `-b typstpdf` vs `-b typst`) | Already routes around the documented NixOS `uv run` compiled-binary PATH-shadowing hazard; reinventing it risks reintroducing that failure mode |
| Corpus fixture project scaffolding | A new `tests/fixtures/<name>/{conf.py,index.rst}` pair | The git-cloned Sphinx `doc/` tree itself, augmented in-place (Pattern 2) | D-02 mandates the FULL real tree, not a hand-authored fixture; a fixture-project approach would silently violate D-02's scope |

**Key insight:** every piece of infrastructure this phase needs (subprocess
pattern, fatal-error propagation contract, `slow`-marker convention) already
exists from Phases 11–14. The only genuinely new logic is the corpus
clone/tag-resolution, the conf.py append, and the warning-stream parsing —
each of which is a self-contained ~10-20 line helper with no existing
project precedent to reuse, but also no external library that would help
(these are `git`/`re`/`subprocess` stdlib-level concerns, not a domain a
package should own).

## Common Pitfalls

### Pitfall 1: Forgetting `typst_documents` makes GATE-02 pass trivially without ever compiling

**What goes wrong:** If the corpus's augmented `conf.py` adds `typsphinx` to
`extensions` but never sets `typst_documents`, `TypstPDFBuilder.finish()`
(verified by reading `typsphinx/builder.py:531-538`) logs
`"No documents defined in typst_documents. Nothing to compile."` and
`return`s — **no `typst.compile()` call is ever made**. A test that only
asserts `result.returncode == 0` on the `sphinx-build` subprocess would pass
even though the PDF-compile fatal-check (the actual point of GATE-02) never
ran.
**Why it happens:** `typst_documents` is a typsphinx-only config value
(`app.add_config_value("typst_documents", [], "html", [list])`, verified in
`typsphinx/__init__.py:44`) that Sphinx's real `doc/conf.py` has no reason to
ever define — it doesn't exist in vanilla Sphinx.
**How to avoid:** the corpus test MUST explicitly assert the compiled PDF
file exists, is non-empty, and starts with the `%PDF` magic bytes (the exact
GATE-01 harness convention) — never rely solely on `returncode == 0` from the
`sphinx-build` subprocess. Additionally assert the augmented `conf.py`
actually contains the `typst_documents` line before running the build (a
cheap sanity check that fails loudly and immediately if the append step
silently didn't happen).
**Warning signs:** the corpus test passes suspiciously fast (a real 154-file
Sphinx docs build + PDF compile of that scale should take a non-trivial
number of seconds/minutes, not sub-second); `result.stdout` contains
`"Nothing to compile"`.

### Pitfall 2: D-07's "before" build fatally aborts if `typst.compile()` is invoked

**What goes wrong:** Attempting to measure the empty-URL before/after
reduction by running the FULL `-b typstpdf` pipeline (including
`typst.compile()`) against the reverted (pre-`79c9d45`) translator will hit
the exact `label <term-id> does not exist` `TypstCompilationError` the fix
was written to close — because `doc/index.rst`'s toctree transitively
includes `doc/glossary.rst` (verified via GitHub raw fetch of `doc/index.rst`
at `v9.1.0`), so the corpus genuinely exercises `:term:` cross-references.
**Why it happens:** conflating "warning capture" (happens during the
translate/write phase, always completes) with "compile success" (happens
only in `finish()`, for `typstpdf` only) — they are separate phases with
separate failure characteristics.
**How to avoid:** use `-b typst` (not `-b typstpdf`) for BOTH the before and
after builds in the D-07 measurement specifically. This still exercises the
exact same `visit_reference` code path that emits the empty-URL warning
(confirmed: the warning fires in `visit_reference`, called during
`writer.py`'s `translate()`, which runs identically regardless of builder —
`typst` and `typstpdf` share the same `write_doc`/translate machinery,
they differ only in whether `finish()` additionally compiles to PDF).
**Warning signs:** the "before" build subprocess returns a non-zero exit
code or its stderr contains a Python traceback mentioning
`TypstCompilationError`/`label ... does not exist` — a sign `-b typstpdf` was
used instead of `-b typst` for this specific measurement.

### Pitfall 3: Re-cloning the corpus on every test run (slow, redundant, and rate-limit-risky)

**What goes wrong:** A naive implementation clones fresh into `tmp_path` (a
function-scoped pytest fixture) on every invocation — for a 154-file Sphinx
`doc/` tree this is wasteful, slows local iteration during plan execution,
and repeated clones from CI-like environments can hit GitHub's unauthenticated
clone rate limits.
**Why it happens:** copying the function-scoped `tmp_path` convention from
the existing small, self-contained render-gate fixtures without considering
the very different cost profile of a full external corpus clone.
**How to avoid:** cache the clone in a stable location outside pytest's
per-test `tmp_path` — e.g. a session-scoped fixture writing to
`~/.cache/typsphinx-corpus-gate/<tag>/` (or equivalent), keyed by the resolved
tag, and skip re-cloning if that directory already exists and looks valid
(e.g. `(cache_dir / "doc" / "conf.py").exists()`). Since the corpus test is
`slow`-marked and run on-demand (not CI-gated), a small amount of staleness
between runs is acceptable — D-01's "prefer the tag matching
`sphinx.__version__`" already ties the cache key to the installed version, so
a `sphinx` upgrade naturally invalidates the cache via a new tag/directory.
**Warning signs:** every local re-run of the corpus test takes minutes
even when nothing changed; CI-adjacent environments intermittently fail with
GitHub "unauthenticated clone" 429s.

### Pitfall 4: Treating `unknown_visit` warning text as safely `grep`-able per-line

**What goes wrong:** Counting `"unknown node type"` occurrences via
`stderr.count("unknown node type")` (a naive substring count) undercounts
whenever a node's dumped subtree contains ANOTHER occurrence of the literal
substring `"unknown node type"` inside actual document prose (unlikely but
possible for a 154-file real-world corpus that includes Sphinx's own
extension-development documentation, which literally discusses `unknown_visit`
in `extdev/`). More commonly, naive per-line splitting undercounts/miscounts
because a single warning can legitimately span multiple physical lines
(verified this session).
**Why it happens:** the log message embeds unbounded, untruncated node
content (`str(node)`, not `repr(node)`) rather than a short structured
summary.
**How to avoid:** use the anchored-regex approach in Pattern 4
(`re.MULTILINE`, matching only at the start of a line on the literal
`"WARNING: unknown node type: <"` prefix) — this is immune to both false
positives from prose mentioning "unknown node type" (since it requires the
exact `WARNING: ` prefix at line-start, which prose text will not have) and
to multi-line node dumps (since only the match anchored at line start is
counted, regardless of how many more lines of node content follow).
**Warning signs:** the catalogue's total warning count doesn't match
`stderr.count("WARNING:")`-style cross-checks; a spot-check of a specific
high-frequency tag's count looks implausibly high or low relative to a
manual `grep -c` sanity check.

### Pitfall 5: Appending the corpus test class to `test_pdf_render_gate.py`

**What goes wrong:** growing an already ~1300-line file (verified via
`Read` this session) with a structurally different kind of test (external
git-clone acquisition + report-generation side effects vs. the existing
file's self-contained `tests/fixtures/*_render_gate/` convention) makes the
file harder to navigate and conflates two different "fixture" concepts for
future readers (a committed `tests/fixtures/` directory vs. an ephemeral
external clone).
**How to avoid:** create `tests/test_corpus_gate.py` as a new sibling module
(no `tests/__init__.py` exists — confirmed this session — so pytest's
rootless import discovery allows `from test_pdf_render_gate import
LEAK_SIGNATURES` or similar cross-module reuse without any package
plumbing).
**Warning signs:** none yet (this is a structure-quality pitfall, not a
correctness one) — but the planner should decide this up front since a later
"move it to its own file" refactor is pure overhead.

## Code Examples

Verified/reasoned patterns for this phase's actual implementation:

### Corpus clone with caching + D-05 skip-on-unavailable

```python
# Source: reasoned from D-01/D-05 + verified `git ls-remote` behavior this
# session (network egress confirmed available in THIS sandbox instance,
# though the phase should not assume that holds for every environment).
import subprocess
import sys
from pathlib import Path

import pytest


def get_or_clone_corpus(cache_root: Path) -> Path | None:
    """Return the path to the cloned doc/ tree, or None if unavailable.

    Caches by resolved tag so repeated local runs don't re-clone (Pitfall 3).
    Returns None (never raises) on any failure -- callers pytest.skip (D-05).
    """
    import sphinx

    tag = f"v{sphinx.__version__}"
    dest = cache_root / f"sphinx-{tag}"
    doc_dir = dest / "doc"

    if doc_dir.exists() and (doc_dir / "conf.py").exists():
        return doc_dir

    dest.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            "git", "clone", "--depth", "1", "--branch", tag,
            "https://github.com/sphinx-doc/sphinx.git", str(dest),
        ],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0 or not doc_dir.exists():
        return None
    return doc_dir


@pytest.fixture(scope="session")
def corpus_doc_dir(tmp_path_factory):
    cache_root = Path.home() / ".cache" / "typsphinx-corpus-gate"
    doc_dir = get_or_clone_corpus(cache_root)
    if doc_dir is None:
        pytest.skip("Sphinx doc/ corpus unavailable (no network or clone failure) -- D-05")
    return doc_dir
```

### SC#1 fatal-check assertion shape (mirrors the GATE-01 harness convention)

```python
# Source: pattern verified against tests/test_pdf_render_gate.py's existing
# TestFigureLengthRenderGate / TestXrefRefidRenderGate classes (this session).
def test_corpus_compiles_with_no_fatal_error(corpus_doc_dir, tmp_path):
    wire_typsphinx_into_corpus_conf(corpus_doc_dir)  # idempotent-checked or done once at clone time
    outdir = tmp_path / "_build"
    result = subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typstpdf", str(corpus_doc_dir), str(outdir)],
        capture_output=True, text=True,
    )
    # SC#1 crux: the PDF must actually exist -- NOT just returncode == 0
    # (Pitfall 1: a missing typst_documents entry would make this pass
    # trivially without ever calling typst.compile()).
    pdf_path = outdir / "sphinx-corpus.pdf"
    assert pdf_path.exists(), (
        f"No PDF produced -- check typst_documents wiring landed:\n{result.stdout}\n{result.stderr}"
    )
    assert pdf_path.stat().st_size > 0
    assert pdf_path.read_bytes()[:4] == b"%PDF"

    # Catalogue as a byproduct of this same build (SC#2).
    from collections import Counter
    counts = catalogue_unknown_visit(result.stderr)
    # ... write counts into 15-CORPUS-REPORT.md (D-06) ...
```

## State of the Art

Not applicable in the usual "library X replaced library Y" sense — this
phase is validation scaffolding over an already-finalized translator. The one
relevant "old vs. new" axis is methodological:

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Assume the empty-URL reduction from XREF-01 without measuring (the state left after Phase 12) | Measure it directly via a controlled before/after rebuild of the real corpus (D-07, this phase) | This phase (15) | Turns a plausible-but-unverified `.planning/research/SUMMARY.md` claim ("×596 figure is a strong signal... actual post-fix reduction should be measured") into a real number for the milestone close-out |
| Assume the real `doc/conf.py` needs a minimal-conf fallback (the CONTEXT.md's flagged risk) | Verified: the real conf.py's `extensions` are 100% `sphinx.ext.*` built-ins, no fallback needed | This research session (2026-07-12) | Removes an entire branch of planning complexity (no install-vs-degrade decision tree needed in the plan) |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Network egress to `github.com` will be available when the corpus test is actually run for the real GATE-02 measurement | Environment Availability, Pattern 1 | If unavailable, D-05's `pytest.skip` path handles it gracefully — low risk, already the designed fallback. Confirmed available in *this* research session, but the phase's actual execution environment may differ (CONTEXT.md explicitly flags "outside the sandbox" as the intended execution context) |
| A2 | The `-c <overlay_confdir>` alternative to Pattern 2's append-in-place technique (mentioned as a non-primary alternative) works as described re: `from conf import *` inside an exec'd Sphinx config namespace | Pattern 2 | Low risk — this alternative is explicitly NOT the recommended primary technique; the append-in-place technique (Pattern 2's main path) was reasoned through Sphinx's actual `eval_config_file` exec model, not assumed |
| A3 | `sphinx.ext.graphviz`/`sphinx.ext.inheritance_diagram`'s HTML/LaTeX-format-specific node visitors (registered via `app.add_node(..., html=..., latex=...)`) are never invoked for the `typstpdf`/`typst` builder formats, so the absence of the `dot` CLI binary (confirmed absent in this sandbox) is harmless | Environment Availability | If wrong (i.e. Sphinx's dispatch mechanism does fall back to a format-specific visitor unexpectedly), the corpus build could hit an unexpected code path when processing the two `.. graphviz::`/inheritance-diagram-bearing pages in Sphinx's own docs (`extdev/` uses inheritance diagrams). Low risk given typsphinx's own `visit_graphviz`/`visit_inheritance_diagram` (DEG-01/02) are already proven live in `TestGraphvizDegradeRenderGate`; this assumption is about Sphinx's dispatch order, not typsphinx's own handlers |

**If this table is empty:** N/A — see entries above; none are HIGH risk given the corroborating evidence already gathered.

## Open Questions

1. **Should the SC#1 fatal-check test and the SC#2/SC#3 report-generation share one test function, or be split?**
   - What we know: SC#1 (fatal-check) naturally produces the stderr needed for SC#2's catalogue as a byproduct of the same build — no need for a second corpus build just to get warnings. SC#3 (before/after) genuinely needs TWO additional separate builds (before + after, both `-b typst`) beyond the SC#1 `-b typstpdf` build.
   - What's unclear: whether the planner wants SC#3's before/after builds triggered automatically by the same `slow`-marked pytest run (making the full `pytest -m slow` invocation noticeably longer — three corpus-scale Sphinx builds instead of one) or as a documented, separately-invoked one-off script/test (kept out of the routine `slow` suite, run only when producing/refreshing the report).
   - Recommendation: given D-06 frames the report as a one-time milestone artifact (not a regression-guarded number), split SC#3 into a separate, explicitly-invoked test function or small script — not folded into the routine `pytest -m slow` run alongside SC#1. This keeps the routine slow-suite runtime to "one corpus build" instead of "three," while still keeping the D-07 methodology fully reproducible and git-tracked (not a throwaway one-off, satisfying D-04's "loses regression re-runnability" rejection rationale for the OVERALL gate, while SC#3 itself was never meant to be a standing regression gate per D-06).

2. **Exact PDF filename/target string for `typst_documents`'s second tuple element.**
   - What we know: `TypstPDFBuilder.finish()` (verified by reading `builder.py`) actually names the output PDF from `doc_tuple[0]` (the source docname, `"index"`), NOT `doc_tuple[1]` (the nominal "target") — the target field appears vestigial/unused for PDF file naming in the current implementation.
   - What's unclear: whether this is intentional (target reserved for future use) or a latent inconsistency; irrelevant to this phase either way since the test only needs to know the actual output filename (`index.pdf`, per the source docname) to assert existence.
   - Recommendation: the corpus test should assert on `outdir / "index.pdf"` (matching the source docname), not on whatever string is used for the tuple's second element, to avoid a false assumption about naming.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Network egress to github.com | D-01 clone, D-07 worktree fetch (if not already local) | ✓ (confirmed this session: `git ls-remote`, `curl -o /dev/null https://github.com` both succeeded) | — | `pytest.skip` (D-05) if unavailable in the actual execution environment |
| `git` (with `worktree` subcommand) | D-01 clone, D-07 revert checkout | ✓ | 2.54.0 | None needed — `git` is a hard dependency of the dev workflow already |
| `sphinx` (installed package) | Drives the corpus build itself | ✓ | 9.1.0 | None — already a pinned runtime dependency (`>=9.1,<10`) |
| `typst` (typst-py) | PDF compile step (SC#1) | ✓ | 0.15.0 | None — already a pinned runtime dependency |
| `pypdf` | Optional text-extraction spot-check of the corpus PDF | ✓ | 6.14.2 | Not required for SC#1's core assertion (file-exists/non-empty/`%PDF`-magic-bytes is sufficient, matching the GATE-01 harness's own minimal-proof convention for large fixtures) |
| `dot` (Graphviz CLI) | NOT required — `sphinx.ext.graphviz`'s format-specific rendering hooks are never invoked for `typst`/`typstpdf` builders (A3) | ✗ (confirmed absent: `command -v dot` failed) | — | None needed; typsphinx's own DEG-01 graceful-degrade placeholder handles these nodes regardless |
| `sphinx_notfound_page` / `notfound` package | NOT required — confirmed absent from the real `doc/conf.py`'s `extensions` list (D-03 finding) | ✗ (confirmed absent: `import sphinx_notfound_page` fails) | — | None needed — was never actually a dependency of the real corpus build |
| `sphinxcontrib.*` extensions | NOT required for the build path — `sphinxcontrib.applehelp/devhelp/htmlhelp/jsmath/qthelp/serializinghtml` ARE installed (Sphinx's own transitive deps) but confirmed absent from `doc/conf.py`'s `extensions` list, so irrelevant either way | ✓ (all present, verified via `importlib.import_module`) | — | N/A |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:** `git ls-remote`/clone network access —
falls back to D-05's `pytest.skip` if unavailable in the actual execution
environment (this session's sandbox happened to have working egress, but the
phase's CONTEXT explicitly anticipates running outside a more restricted
sandbox for the real measurement — plan for both).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.4+ (`pyproject.toml` `dev` extras, `>=8.4,<10`) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (existing `slow` marker already registered, no new marker needed) |
| Quick run command | N/A for this phase's own gate — GATE-02 is `slow`-marked and excluded from the fast suite by design (D-04) |
| Full suite command | `pytest tests/test_corpus_gate.py -m slow -v` (new module; requires network + the real Sphinx `doc/` corpus) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| GATE-02 (SC#1) | Full corpus `-b typstpdf` compiles with no fatal `TypstCompilationError` | integration (`slow`) | `pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v` | ❌ Wave 0 — new file |
| GATE-02 (SC#2) | `unknown_visit` warnings catalogued by frequency, written to `15-CORPUS-REPORT.md` | integration (`slow`), report side-effect | same test as SC#1 (byproduct of the same build's captured stderr) | ❌ Wave 0 — same new file |
| GATE-02 (SC#3) | Empty-URL warning count measured before/after XREF-01, written to `15-CORPUS-REPORT.md` | integration (`slow`), one-time/report-only per D-06 | either a dedicated `slow`-marked test function in `test_corpus_gate.py`, or a documented standalone script invoked once (planner's call — see Open Question 1) | ❌ Wave 0 — new |

### Sampling Rate

- **Per task commit:** N/A — this phase produces no code under `typsphinx/` that the fast suite exercises; `pytest -m "not slow"` (the existing fast suite) should remain unaffected and green throughout.
- **Per wave merge:** run the new `tests/test_corpus_gate.py -m slow` module manually (network + time required) at least once before considering the phase's plans complete, to confirm SC#1 genuinely passes against the real corpus — not merely well-formed as code.
- **Phase gate:** the `15-CORPUS-REPORT.md` (D-06) IS the phase's completion artifact for SC#2/SC#3 — its presence with concrete numbers (not placeholders) is itself part of `/gsd-verify-work`'s check for this phase, alongside the `slow`-marked test passing for SC#1.

### Wave 0 Gaps

- [ ] `tests/test_corpus_gate.py` — new module; covers GATE-02 SC#1/SC#2/SC#3
- [ ] Corpus clone/cache helper (`get_or_clone_corpus`-style) — new, no existing precedent
- [ ] `conf.py` augmentation helper (`wire_typsphinx_into_corpus_conf`-style) — new
- [ ] D-07 `git worktree` before/after helper — new
- [ ] `15-CORPUS-REPORT.md` — new, phase-completion artifact (D-06)
- Framework install: none — `pytest`/`slow` marker already fully set up; no `tox.ini`/CI changes needed (the `slow` marker is already excluded from the existing CI matrix via whatever invocation already uses `-m "not slow"`, confirmed as the established convention in `nixos-sandbox-test-env` memory and `test_pdf_render_gate.py`'s existing `@pytest.mark.slow` classes)

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A — no auth surface in this phase |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | yes (narrow) | The resolved tag string (`f"v{sphinx.__version__}"`) is passed to `git clone --branch <tag>`; since `sphinx.__version__` comes from the installed package (trusted, not user/network input), injection risk is negligible, but the helper should still avoid `shell=True` (use the list-argument `subprocess.run([...])` form throughout, matching the existing `_run_sphinx_build_typst` convention) so no shell metacharacter interpretation is possible even in principle |
| V6 Cryptography | no | N/A — no crypto operations in this phase |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Git tag mutability (a tag can be force-moved on GitHub after the fact, unlike an immutable commit SHA) — a corpus test could silently start building against different content than what was verified in this research session | Tampering | Low severity for this phase (the gate is a `slow`, on-demand, non-CI test measuring typsphinx's own robustness, not a security-sensitive supply-chain artifact) — acceptable as-is, but the report/test SHOULD log the resolved commit SHA (`git rev-parse HEAD` inside the clone after checkout) alongside the tag, so a future re-run's report can be diffed against a known-good SHA if Sphinx's `v9.1.0` tag were ever unexpectedly force-moved |
| Executing a git-cloned, untrusted-origin `conf.py` via `sphinx-build` (Sphinx conf.py files are arbitrary Python, executed with full process privileges) | Elevation of Privilege (in the general case of untrusted corpora) | **Accepted risk, not mitigated**: the corpus is Sphinx's own official GitHub repository at a specific pinned release tag — the same trust level as installing `sphinx` itself from PyPI (already a direct runtime dependency of this project). No additional sandboxing is warranted; treat exactly as trusted as the `sphinx` package already is |
| Subprocess argument injection via constructed file paths (clone destination, tag string) | Tampering | All subprocess invocations use the list-argument form (`subprocess.run([...])`, never `shell=True`/string-interpolated shell commands) — matching the existing, already-audited `_run_sphinx_build_typst` pattern exactly |

## Sources

### Primary (HIGH confidence)

- `typsphinx/translator.py` (this repo, read in full relevant sections this session) — `visit_reference`/`depart_reference` (lines 2296-2422), `unknown_visit`/`unknown_departure` (2424+), `visit_term`/`depart_term` (1220-1267)
- `typsphinx/builder.py` (this repo, read in full this session) — `TypstPDFBuilder.finish()` (514-568), the `typst_documents` no-op-if-empty warning path (534-538)
- `typsphinx/pdf.py` (this repo, read in full this session) — `TypstCompilationError`, `compile_typst_to_pdf`
- `typsphinx/writer.py` (this repo, read in full this session) — `TypstWriter.translate()`, confirming `-b typst` and `-b typstpdf` share the identical translate/write code path
- `typsphinx/__init__.py` (this repo, `add_config_value` calls grepped this session) — confirms `typst_documents` is typsphinx-only, default `[]`
- `tests/test_pdf_render_gate.py` (this repo, read in full this session, ~1324 lines) — the `_run_sphinx_build_typst` subprocess pattern, `LEAK_SIGNATURES`, class-scoped fixture pattern (`TestTopicLineBlockRenderGate`/`TestFootnoteRenderGate`), the existing `@pytest.mark.slow` usage precedent
- `raw.githubusercontent.com/sphinx-doc/sphinx/v9.1.0/doc/conf.py` — fetched live this session (`curl`), full content inspected: `extensions` list is 100% `sphinx.ext.*` built-ins
- `raw.githubusercontent.com/sphinx-doc/sphinx/v9.1.0/doc/index.rst` — fetched live this session, confirms the master doc's toctree transitively includes `usage/`, `tutorial/`, `development/`, `extdev/`, `latex`, `support`, `internals/`, `faq`, `authors`, `man/`, `usage/configuration`, `usage/extensions/`, `usage/restructuredtext/`, `glossary`, `changes/`, `examples`
- GitHub API `repos/sphinx-doc/sphinx/git/trees/v9.1.0?recursive=1` — fetched live this session: confirms 234 files under `doc/` (154 `.rst`), no `doc/sphinxext/` directory
- `git ls-remote --tags https://github.com/sphinx-doc/sphinx.git` — run live this session, confirms `refs/tags/v9.1.0` exists
- `git show 79c9d45 --stat` — run live this session, confirms the single-commit, single-file (`typsphinx/translator.py`, 14 insertions/1 deletion) scope of the XREF-01 `depart_term` fix
- Empirical `uv run python3 -m sphinx -b typst` runs against ad hoc fixtures this session — confirmed live: (1) `visit_rubric`/`visit_seealso` already implemented (not unknown), (2) `citation`/`label` nodes trigger the exact `"WARNING: unknown node type: <TAG ...>"` multi-line format with nested-node double-counting behavior
- `.planning/phases/12-high-volume-independent-node-handlers/12-02-PLAN.md` and `12-02-SUMMARY.md` (this repo) — confirms `visit_reference`'s refid branch predates and is untouched by XREF-01/commit `79c9d45`

### Secondary (MEDIUM confidence)

- `.planning/research/SUMMARY.md`, `ARCHITECTURE.md`, `PITFALLS.md` (this repo, prior milestone research) — provenance of the ×972/×596 frequency figures (no reproducible methodology documented for those specific numbers; this phase's own SC#2/SC#3 measurements supersede them with a freshly reproducible methodology)
- `.claude/gsd-core` memory note `nixos-sandbox-test-env.md` — documents the `uv run <compiled-binary>` PATH-shadowing hazard this phase's subprocess helpers must continue to route around

### Tertiary (LOW confidence)

- The `-c <overlay_confdir>` alternative technique in Pattern 2 (explicitly flagged as unverified/non-primary in the Assumptions Log, A2)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new dependencies, all versions verified live against the installed environment this session
- Architecture: HIGH — every pattern (clone/tag-resolution, conf.py augmentation, warning parsing, D-07 before/after) is either directly verified via live commands this session or reasoned through source code read in full this session, not assumed
- Pitfalls: HIGH — Pitfalls 1, 2, and 4 are all grounded in specific, cited source-code reads or empirical command runs from this session, not generic domain knowledge
- D-03 risk resolution: HIGH — the real `doc/conf.py` was fetched and read in full live this session, not recalled from training data

**Research date:** 2026-07-12
**Valid until:** Tied to Sphinx's `v9.1.x` release line and this repo's own `typsphinx/translator.py` state at commit `4875fad` (Phase 14 complete) — re-verify the `doc/conf.py` extensions list and the toctree-includes-glossary finding if the project's pinned Sphinx dependency range (`pyproject.toml`) ever moves past `<10`, since a new major Sphinx release could change `doc/conf.py`'s `extensions` list or the corpus's toctree structure. For the currently pinned range, valid indefinitely (no fast-moving external dependency here — the corpus IS the thing being measured, not a moving target itself).
