# Phase 61 — Local Green-Tree Evidence (SC#3, local half, re-anchored per D-09)

## Provisioning and tree identity

Provisioning command (per `CLAUDE.md` § "Worktree-isolated execution"):

```
$ unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT
$ uv sync --extra dev
...
 + typsphinx==0.9.0 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a8497ee77be99419f)
...
```

Outcome: a fresh worktree-local `.venv` was created and `typsphinx` was installed editable
from this worktree's own path — not the main checkout's.

Four command-plus-output blocks confirming tree identity:

```
$ sed -n '7p' pyproject.toml
version = "0.9.0"
```

**This asserts the version is UNCHANGED** — the inverse of the assertion Phases 52 and 57
made when they proved a bump had landed. D-01 drops the version bump for this phase, so the
correct proof here is that line 7 has NOT moved.

```
$ sed -n '347p' README.md
**Status**: Stable (v0.9.0) - Production ready
```

Also unchanged, consistent with D-01.

```
$ awk '/^## \[Unreleased\]/,/^## \[0\.9\.0\]/' CHANGELOG.md | grep -oE '(PATH-01|IMG-0[4567]|MSG-0[2345])' | sort -u | wc -l
9
```

Nine distinct requirement IDs (PATH-01, IMG-04, IMG-05, IMG-06, IMG-07, MSG-02, MSG-03,
MSG-04, MSG-05) are cited inside the `## [Unreleased]` region — confirming this tree carries
plan 61-01's CHANGELOG bullets, not a pre-edit CHANGELOG.

```
$ uv run python -c "import typsphinx, os, sys; print('version=', typsphinx.__version__); print('file=', typsphinx.__file__); print('cwd=', os.getcwd()); print('inside_worktree=', os.path.abspath(typsphinx.__file__).startswith(os.getcwd()+os.sep))"
version= 0.9.0
file= /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a8497ee77be99419f/typsphinx/__init__.py
cwd= /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a8497ee77be99419f
inside_worktree= True
```

This is the load-bearing anti-stale-editable-install proof: the printed absolute path resolves
INSIDE this executing worktree (`.claude/worktrees/agent-a8497ee77be99419f/typsphinx/__init__.py`),
not the main checkout's `/home/yuta/Documents/typsphinx/typsphinx`. Every measurement below is
therefore taken against this worktree's own tree, not the unchanged main-tree package.

## Product-tree delta from the phase base

`PHASE_BASE_SHA` read back from `61-CLOSEOUT-GUARD.md` § "Baseline":

```
5e28fa9dac8576f1f1665560eb5c4ccbd2e13b41
```

```
$ git diff --stat 5e28fa9dac8576f1f1665560eb5c4ccbd2e13b41..HEAD -- . ':(exclude).planning'
 CHANGELOG.md | 28 ++++++++++++++++++++++++++++
 1 file changed, 28 insertions(+)

$ git diff --name-only 5e28fa9dac8576f1f1665560eb5c4ccbd2e13b41..HEAD -- . ':(exclude).planning' ':(exclude)CHANGELOG.md'
(no output)
```

This proves both halves of what the product-tree delta must show: the phase's product-tree
footprint is bounded to exactly one file, `CHANGELOG.md`, with a nonzero insertion count (28)
and zero deletions — and because the diff is non-empty, this is a real positive control on the
diff machinery, not a vacuous empty-diff claim that would look identical if `PHASE_BASE_SHA`
were wrong (e.g. pointed at HEAD itself).

## Division of authority

Following the Phase 52 precedent, this phase's evidence is split across three files by what
each is authoritative for:

- **`61-CHANGELOG-EVIDENCE.md`** is authoritative for the docs-html and docs-pdf warning-count
  comparison against the 3 / 5 baseline. That comparison is NOT repeated here — the
  product-tree delta measured above proves the two trees (this plan's worktree and
  `61-CHANGELOG-EVIDENCE.md`'s worktree) carry identical `CHANGELOG.md` content, so a docs
  render measured there applies equally here.
- **This file (`61-GREEN-TREE-EVIDENCE.md`)** is authoritative for the full pytest suite,
  `black --check`, `mypy`, and the version-sync guard family.
- **`61-CI-EVIDENCE.md`** is authoritative for the 3-OS CI matrix and for lint (`ruff`), which
  CI owns on this project per the standing convention recorded in `61-RESEARCH.md`.

## SC#3 — full pytest suite

Full suite (no `-m` filter):

```
$ uv run pytest
...
================= 1513 passed, 5 skipped in 122.08s (0:02:02) ==================
```

Corpus gate, per-test outcome:

```
$ uv run pytest tests/test_corpus_gate.py -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .../agent-a8497ee77be99419f/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a8497ee77be99419f
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 5 items

tests/test_corpus_gate.py::test_catalogue_unknown_visit_multiline PASSED [ 20%]
tests/test_corpus_gate.py::test_catalogue_unknown_visit_windows_crlf_and_prefix PASSED [ 40%]
tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED [ 60%]
tests/test_corpus_gate.py::test_count_empty_url_warnings PASSED          [ 80%]
tests/test_corpus_gate.py::test_empty_url_before_after SKIPPED (SC#3
before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1
to run it (RESEARCH Open Question 1))                                    [100%]

======================== 4 passed, 1 skipped in 13.24s =========================
```

Transcribed as printed: four `PASSED` and one `SKIPPED`. The skip is `test_empty_url_before_after`,
which is deliberately env-gated behind `TYPSPHINX_CORPUS_REPORT=1` (an opt-in before/after
measurement noted as RESEARCH Open Question 1) — not a failure and not evidence of a pass. It is
recorded here as a skip, exactly as printed, never as a pass.

<!-- gsd:write-continue -->
