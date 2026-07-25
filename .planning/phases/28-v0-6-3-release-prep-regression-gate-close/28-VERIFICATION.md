---
phase: 28-v0-6-3-release-prep-regression-gate-close
verified: 2026-07-25T08:27:17Z
status: in-progress
score: pending (Task 1 of 2 complete — SC#3 evidence recorded; SC#4/SC#5/Observable Truths pending Task 2)
behavior_unverified: 0
overrides_applied: 0
---

# Phase 28: v0.6.3 Release Prep + Regression-Gate Close — Verification Evidence

This is the durable, executor-owned evidence record for the wave-2 regression-gate close of the
v0.6.3 milestone. Every command below was run by this executor, from inside this worktree, against
the post-version-bump tree (HEAD includes plan 28-01's `pyproject.toml`/`uv.lock`/`README.md` version
bump 0.6.2 → 0.6.3). Nothing here is copied from `28-RESEARCH.md`'s earlier research session — that
session ran on a different commit (pre-version-bump) and is cited only for baseline comparison where
noted.

Worktree provisioning performed before any command below (per `CLAUDE.md` § "Worktree-isolated
execution"):

```bash
unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync --extra dev
ln -sf "$(command -v uv)" .venv/bin/uv   # NixOS ELF-exec shim, orchestrator-measured fix
```

All commands below were run via `.venv/bin/uv run ...` (the shimmed `uv`), executed from this
worktree's root.

## SC#3 — Full-Corpus Regression Gate

Command run (verbatim):

```
uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v -s
```

Full output (verbatim):

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 1 item

tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error Corpus tag: v9.1.0
Corpus commit SHA: cc7c6f435ad37bb12264f8118c8461b230e6830c
Unknown Visit Catalogue: []
PASSED

============================== 1 passed in 13.81s ==============================
```

**Read of this evidence:** summary line reads `1 passed in 13.81s` — not `1 skipped`. Zero `SKIPPED`
lines anywhere in the output. `Corpus tag: v9.1.0` and `Corpus commit SHA:
cc7c6f435ad37bb12264f8118c8461b230e6830c` are printed (the cached corpus was reachable from inside
this worktree at `~/.cache/typsphinx-corpus-gate/`, a user-global path). `Unknown Visit Catalogue: []`
— no node type was silently dropped rebuilding the full Sphinx `doc/` v9.1.0 corpus through
`-b typstpdf`. Elapsed time (13.81s) is in the real-build range (prior-session measurement: 13.08s;
Phase 23 precedent: 13.67s/13.99s) — a skip would have returned in well under a second, so this
duration is itself evidence the gate genuinely compiled the corpus rather than short-circuiting via
`pytest.skip`.

## SC#3 Evidence — Full pytest Suite

Command run (verbatim):

```
uv run python -m pytest -q -rs
```

Summary and skip-reason lines (verbatim, from the tail of the captured run):

```
tests/test_xref_orphan_degrade_render_gate.py .                          [100%]

=========================== short test summary info ============================
SKIPPED [1] tests/test_corpus_gate.py:529: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
======================= 656 passed, 1 skipped in 56.33s ========================
```

Bare summary line (stripped of pytest's decorative `===` padding, for machine-readable matching):

```
656 passed, 1 skipped in 56.33s
```

**Read of this evidence:** `656 passed, 1 skipped in 56.33s`, zero `failed`. This matches the
Phase 27.1-completion baseline (`656 passed / 1 skipped`) exactly, reproduced live against the
post-version-bump tree. `-m "not slow"` was deliberately **not** passed — this total includes the
slow-marked corpus-gate test above, per D-05.

**The single skip, named explicitly:** the `1 skipped` above is `tests/test_corpus_gate.py:529`,
which is `test_empty_url_before_after` — a standalone measurement function gated behind the
`TYPSPHINX_CORPUS_REPORT=1` environment variable (unset here, so it self-skips with the message shown
above). This is a **different test** from `TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`
(the SC#3 gate itself, verified PASSING above) and has **no bearing on SC#3's pass/fail verdict**.
Conflating this skip with "the corpus gate skipped again" would be a misread — the corpus gate's own
independent, single-node-id run (previous section) is unambiguously `1 passed`, not `1 skipped`.

## SC#3 Evidence — Docs Builds

Two independent tox environments, each with **its own** warning-count baseline (D-06) — `docs-pdf`
(English-only, single-language build) structurally caps at 2 lines; `docs-multilang` (English + 日本語,
2-language build) repeats the same 2 lines once per language, for 4 total. These are never compared
against a single shared number.

### `tox -e docs-pdf`

Command run (verbatim):

```
uv run tox -e docs-pdf
```

Warning-tally command and output:

```
$ grep -c '\[docutils\]' <captured docs-pdf output>
2
```

Raw warning lines (verbatim):

```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:7: ERROR: Unexpected indentation. [docutils]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:8: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
```

Build tail (verbatim):

```
Generated PDF: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/docs/_build/pdf/typsphinx.pdf
build succeeded, 2 warnings.
  docs-pdf: OK (3.83=setup[0.55]+cmd[3.28] seconds)
  congratulations :) (3.86 seconds)
```

**Machine-readable count line:**

docs-pdf warning lines: 2

Both lines are the pre-existing, out-of-scope `visit_toctree` docstring defect (`typsphinx/translator.py`
docstring parsed as RST by autodoc/Napoleon, producing an ERROR + WARNING pair) — unchanged from the
phase-entry baseline, not caused by anything this milestone touched. `build succeeded, 2 warnings.`
matches the RESEARCH.md-measured baseline exactly.

(Note: numerous `RemovedInSphinx10Warning` lines from the `sphinx_autodoc_typehints` third-party
package's own deprecation notice also appear in the raw build log — these are Python
`DeprecationWarning`s printed to stderr by a dependency, not Sphinx build warnings; Sphinx's own
warning counter reports `2 warnings`, matching the `[docutils]`-tagged line count above exactly.)

### `tox -e docs-multilang`

Command run (verbatim):

```
uv run tox -e docs-multilang
```

Warning-tally command and output:

```
$ grep -c '\[docutils\]' <captured docs-multilang output>
4
```

Raw warning lines (verbatim, English build then 日本語 build):

```
(English build)
:7: (ERROR/3) Unexpected indentation.
:8: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:7: ERROR: Unexpected indentation. [docutils]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:8: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]

(日本語 build)
:7: (ERROR/3) Unexpected indentation.
:8: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:7: ERROR: Unexpected indentation. [docutils]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:8: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
```

Build tail (verbatim):

```
======================================================================
✓ Multi-language build complete!
======================================================================

Output directory: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/docs/_build/multilang

Language versions:
  - English    (en): /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/docs/_build/multilang/en (22 HTML files)
  - 日本語        (ja): /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/docs/_build/multilang/ja (22 HTML files)

  docs-multilang: OK (5.30=setup[0.43]+cmd[4.87] seconds)
  congratulations :) (5.32 seconds)
```

**Machine-readable count line:**

docs-multilang warning lines: 4

Both language builds emit the identical `visit_toctree`-docstring ERROR+WARNING pair (source is
shared across languages), giving 2 lines × 2 languages = 4 total — exactly matching the
phase-entry baseline recorded in `28-RESEARCH.md`. Both builds ran via `uv run tox -e docs-multilang`
without hitting the NixOS `subprocess.run(["sphinx-build", ...])` ELF-exec hazard noted in
`28-RESEARCH.md` Pitfall 6 (the `.venv/bin/uv` symlink shim applied at session start resolved it
proactively; no `nix-shell` fallback was needed).

**D-08 record (no manual visual inspection performed):** No manual visual inspection of a 日本語 PDF
was performed or is claimed here. `tox -e docs-pdf` produces only an English PDF (`docs/source`'s
`conf.py` sets no `language`), and `tox -e docs-multilang` produces HTML only for both `en` and `ja` —
so "Table N" rendering as "表 N" in a 日本語 PDF is not observable in any tox environment run by this
plan. Phase 27.1's GATE-01 fixtures (21 tests: 日本語 `.typ`-source assertions + German PDF-text
extraction) mechanically cover this fact instead, and those fixtures are part of the 656-passed count
in the full-suite section above.

**Post-build working-tree note:** running `tox -e docs-pdf` / `tox -e docs-multilang` regenerated two
tracked `.mo` gettext catalogs (`docs/locale/ja/LC_MESSAGES/examples/advanced.mo`,
`docs/locale/ja/LC_MESSAGES/user_guide/builders.mo`) as a byte-identical-size but binary-different
recompilation side effect (same source `.po`, non-deterministic `.mo` byte layout). These were
reverted with `git checkout -- <path>` immediately after being observed via `git status --short`, so
no state survives from this build step: `git status --porcelain tests/ typsphinx/ docs/ examples/`
reads empty (confirmed below).

## Scope-Fence Assertions (Task 1)

```
$ git status --porcelain tests/ typsphinx/ docs/ examples/
(empty)

$ git tag --list 'v0.6.3'
(empty)

$ ls .planning/phases/28-v0-6-3-release-prep-regression-gate-close/28-GATE.md
ls: cannot access '...28-GATE.md': No such file or directory
```

No new test code was written (D-05–D-08), no source tree files were modified, no tag exists, and no
`28-GATE.md` was created — all evidence lands in this file.

<!-- Task 2 appends: ## SC#4 — Milestone Invariants / ## SC#5 — Scope Fence / ## Observable Truths -->
