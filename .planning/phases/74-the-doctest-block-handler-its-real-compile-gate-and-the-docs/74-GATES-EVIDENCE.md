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
