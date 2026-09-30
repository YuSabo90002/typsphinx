# Phase 74 — Local Gates and Scope Fence (SC4 local half)

## Head check and provisioning

Worktree HEAD check, run before any other command in this plan:
```
$ git rev-parse --abbrev-ref HEAD
worktree-agent-a605e9b5c3aaab348
$ git rev-parse HEAD
c043950b58ed5e1030c1b17449b46a7c9b4fe85b
```
Not detached, not a protected branch name, in the agent-*/worktree-agent-* namespace, matches
the orchestrator-supplied expected base exactly.

Provisioning command and exit:
```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
... (357 packages resolved/installed, including sphinx, sphinx-autodoc-typehints, myst-parser,
    furo, sphinx-intl from the docs extra) ...
PROVISION_EXIT:0
```

PYVENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
PYVENV_VERSION_INFO = 3.13.13

These are recorded, not compared with the main checkout's own `.venv` (a fresh worktree venv
may use a different uv-managed interpreter per CLAUDE.md's "Interpreters may differ" note).

BASE_74_06 = c043950b58ed5e1030c1b17449b46a7c9b4fe85b
SCRATCH_74_06 = /tmp/p7406_5rvNfk

## Wave 1-3 audit

Quoted verbatim from the wave 1-3 evidence files, read before any command in this plan ran:

```
$ sed -n 's/^RED_VERDICT = //p' 74-RED-EVIDENCE.md
MET
$ sed -n 's/^GREEN_VERDICT = //p' 74-RED-EVIDENCE.md
MET
$ sed -n 's/^QUA14_FIX_VERDICT = //p' 74-QUA14-EVIDENCE.md
MET
```

RED_TREE_SHA = 215e9715845bd2e8c744c994979b0b2ca1e31897
GREEN_TREE_SHA = 255d1648fa68421d5d10e6abfef68bd6cece8458
RED_VERDICT = MET
GREEN_VERDICT = MET
QUA14_FIX_VERDICT = MET

All three verdicts read MET. Proceeding to the local gates.

## Lint trio

```
$ uv run ruff check .
All checks passed!
RUFF_EXIT:0

$ uv run black --check .
All done! (no emoji reproduced here) 357 files would be left unchanged.
BLACK_EXIT:0

$ uv run mypy typsphinx/
Success: no issues found in 9 source files
MYPY_EXIT:0
```

RUFF_EXIT = 0
BLACK_EXIT = 0
MYPY_EXIT = 0

## Full pytest

Plain run (`uv run pytest -rs -p no:cacheprovider`, saved to `$SCRATCH_74_06/p7406_pytest.txt`):
```
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set
  TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
1562 passed, 1 skipped in 131.39s
exit:0
```

C-locale run (`LC_ALL=C uv run pytest -rs -p no:cacheprovider`, saved to
`$SCRATCH_74_06/p7406_pytest-c.txt` — this is the run matching CI's English locale):
```
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set
  TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
1562 passed, 1 skipped in 128.42s
exit:0
```

Both runs report the identical single skip — the `test_corpus_gate.py` env-gated report skip,
unrelated to this phase — and zero skips naming `tests/test_changelog_page_gate.py`, because the
`docs` extra is present in this worktree venv (ROADMAP constraint 11).

FULL_PYTEST_EXIT = 0
FULL_PYTEST_C_EXIT = 0
FULL_PYTEST_PASSED = 1562
FULL_PYTEST_C_PASSED = 1562
FULL_PYTEST_FAILED = 0
FULL_PYTEST_C_FAILED = 0
FULL_PYTEST_ERRORS = 0
CHANGELOG_GATE_SKIPS = 0

Interpreters recorded on both sides: this worktree venv is `3.13.13` per
`PYVENV_VERSION_INFO` above; these counts are recorded, not compared with the main checkout's.

## @preview invariant

```
$ uv run pytest tests/test_preview_version_sync.py -v -p no:cacheprovider
tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED
3 passed in 0.02s
exit:0
```

PREVIEW_SYNC_EXIT = 0

```
$ grep -ho '@preview/[a-z-]*:' typsphinx/templates/base.typ | sort -u | wc -l
4
```

PREVIEW_PACKAGE_COUNT = 4

```
$ git diff --name-only 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b HEAD -- typsphinx/templates typsphinx/writer.py typsphinx/template_engine.py
(empty)
```

None of the three `@preview` declaration sites (`typsphinx/templates/base.typ`,
`typsphinx/writer.py`, `typsphinx/template_engine.py`) changed since the milestone base
`6cc44f22`.

## Scope fence: typsphinx/

All ranges below are `6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b..HEAD`, the milestone base per
constraint 10.

```
$ git diff --stat 6cc44f22..HEAD -- typsphinx/
 typsphinx/pathfmt.py    |  1 +
 typsphinx/translator.py | 60 ++++++++++++++++++++++++++++++++++++++++++++++---
 2 files changed, 58 insertions(+), 3 deletions(-)
```

TYPSPHINX_DIFF_FILES = typsphinx/pathfmt.py|typsphinx/translator.py

Pathspec control — `git diff --name-only 6cc44f22..HEAD -- typsphinx/translator.py` is
non-empty (`typsphinx/translator.py`), proving the pathspec matches a real change.

Widened-diff control — `git diff --name-only 6cc44f22..HEAD` (no pathspec) lists 33 files
across three top-level directories: `.planning` (25), `tests` (6), `typsphinx` (2), including
`tests/test_doctest_block_render_gate.py` — proving the range carries this phase's work and the
fence is not vacuous.

Region scope. Anchor lines in the tip: `visit_literal_block` at line 2431, `visit_definition_list`
at line 2667 (handler region is `[2431, 2667)`), `visit_toctree` at line 5466 (docstring region
is `(5466, 5526)`, i.e. within 60 lines after `def visit_toctree`).

`translator.py` hunks (new-side start line, via `git diff -U0`), each tabulated with its region:

| New-side start | Region |
|---|---|
| 2431 | handler region (`visit_literal_block`/`visit_doctest_block` signature widening) |
| 2572 | handler region (language-resolution fallback line) |
| 2586 | handler region (`depart_literal_block` signature widening) |
| 2628 | handler region (new `visit_doctest_block`/`depart_doctest_block` methods) |
| 5471 | `visit_toctree` docstring (within 60 lines after `def visit_toctree`) |
| 5485 | `visit_toctree` docstring |
| 5488 | `visit_toctree` docstring |

`pathfmt.py` hunks: anchor `def quote_path` at line 46 (in-scope window `(46, 86)`).

| New-side start | Region |
|---|---|
| 63 | within 40 lines after `def quote_path` |

The single `pathfmt.py` hunk (`@@ -62,0 +63 @@ ... +`) adds exactly one empty line and removes
nothing.

TRANSLATOR_HUNKS_OUTSIDE_SCOPE = 0

## Standing invariants

```
$ git diff --name-only 6cc44f22..HEAD -- .github flake.nix
(empty)
$ git ls-files -- .github/workflows/ci.yml flake.nix
.github/workflows/ci.yml
flake.nix
$ git diff --name-only 6cc44f22..HEAD -- pyproject.toml uv.lock typsphinx/__init__.py
(empty)
$ git show HEAD:pyproject.toml | grep -m1 '^version = '
version = "0.9.2"
$ git show 6cc44f22:pyproject.toml | grep -m1 '^version = '
version = "0.9.2"
```

WORKFLOWS_FLAKE_UNTOUCHED = yes
PYPROJECT_UV_LOCK_INIT_UNTOUCHED = yes
VERSION_AT_CLOSE = 0.9.2

## Test-edit census

```
$ git diff --name-status 6cc44f22..HEAD -- tests/
A	tests/fixtures/doctest_block_render_gate/conf.py
A	tests/fixtures/doctest_block_render_gate/context_a_paragraph.rst
A	tests/fixtures/doctest_block_render_gate/context_b_nonfirst_positions.rst
A	tests/fixtures/doctest_block_render_gate/index.rst
A	tests/test_doctest_block_render_gate.py
M	tests/test_translator.py
$ git diff --numstat 6cc44f22..HEAD -- tests/test_translator.py
72	0	tests/test_translator.py
```

Every row is `A` except one `M` row for `tests/test_translator.py`, whose numstat deletions are 0.

PREEXISTING_TEST_DELETIONS = 0
MODIFIED_TEST_FILES = tests/test_translator.py

## API coverage declaration

`COVERAGE.md` (this phase directory) holds exactly one line:
```
No external API integration: typsphinx translator node handler, test fixture and docstring text only.
```

```
$ node gsd-core/bin/gsd-tools.cjs check api-coverage.verify-pre .planning/phases/74-the-doctest-block-handler-its-real-compile-gate-and-the-docs
{
  "block": false,
  "passed": true,
  "coverage_present": true,
  "matrix": "COVERAGE.md",
  "counts": { "surface": 0, "integrate": 0, "optout": 0 },
  "none_declared": true,
  "detected": true,
  "signals": [
    { "verb": "(surface)", "noun": "api" },
    { "verb": "integration", "noun": "api" }
  ],
  "message": "api-coverage: COVERAGE.md declares no external API integration, overriding 2 detected signal(s) — confirm the declaration is accurate"
}
```

API_COVERAGE_PASSED = true

## SC4 local verdict

Every Task 1 key reads 0 (or 4 for the package count), `TRANSLATOR_HUNKS_OUTSIDE_SCOPE = 0`, the
three standing-invariant keys hold, and `PREEXISTING_TEST_DELETIONS = 0`.

SC4_LOCAL_VERDICT = MET
