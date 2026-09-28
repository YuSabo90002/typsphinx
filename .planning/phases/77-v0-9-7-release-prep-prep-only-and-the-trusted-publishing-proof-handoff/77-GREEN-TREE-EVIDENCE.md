# Phase 77 — Green Tree Evidence (SC#3 local half)

## Head check and provisioning

```
date -u +%FT%TZ  -> 2026-09-28T13:25:55Z
pwd -P            -> /home/yuta/Documents/typsphinx/.claude/worktrees/agent-adef113a85ee57dc2
test -f .git; echo "exit:$?"  -> exit:0
```

Shim check:

```
grep -q typsphinx-fhs-run "$(command -v uv)" && echo shim-ok  -> shim-ok
```

Provisioning:

```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
```
exited 0 (fresh worktree venv resolved 91 packages, `typsphinx==0.9.7` built and installed
editable from this worktree's own checkout, plus every `dev`/`docs`-extra dependency).

```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --locked
Resolved 91 packages in 2ms
Checked 90 packages in 0.52ms
```
exit:0 — the lock is in sync with the manifest, matching what every CI job starts with.

```
sed -n 's/^home = //p;s/^version_info = //p' .venv/pyvenv.cfg
```

PYVENV_HOME = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
PYVENV_VERSION_INFO = 3.14

```
git rev-parse HEAD   (before any commit this plan makes)
```

BASE_77_04 = 44f9c6a2045b4943664b1a3473dc3b4422ac3ad3

```
mktemp -d /tmp/p7704.XXXXXX
```

SCRATCH_77_04 = /tmp/p7704.IybIFc

## Wave-1 gate

Quoted from `77-BUMP-EVIDENCE.md`:

BUMP_COMMIT_SHA = 39cb79f970c4137d4238023e1df7291c7c282c3a
BUMP_COMMIT_FILES = CHANGELOG.md|README.md|pyproject.toml|tests/test_changelog_page_gate.py|uv.lock

Quoted from `77-CHANGELOG-EVIDENCE.md`:

EXTRACT_MATCHES_SECTION = yes

```
git merge-base --is-ancestor 39cb79f970c4137d4238023e1df7291c7c282c3a HEAD; echo "exit:$?"
exit:0

sed -n 7p pyproject.toml
version = "0.9.7"
```

`BUMP_COMMIT_SHA` is confirmed an ancestor of this worktree's HEAD and the bumped version literal
is in place — wave 1 has landed, so the measurements below are taken on the correct tree.

## Lint trio

```
uv run ruff check .
All checks passed!
```

RUFF_EXIT = 0

```
uv run ruff --version
ruff 0.16.8
```

RUFF_VERSION = 0.16.8

```
uv run black --check .
All done! ✨ 🍰 ✨
359 files would be left unchanged.
```

BLACK_EXIT = 0

```
uv run mypy typsphinx/
Success: no issues found in 9 source files
```

MYPY_EXIT = 0

## Full pytest

Host-locale run:

```
uv run pytest -rs -p no:cacheprovider > "$S/p7704_pytest.txt" 2>&1; echo "exit:$?"
exit:0
```

C-locale run (matching CI's English locale):

```
LANG=C LC_ALL=C uv run pytest -rs -p no:cacheprovider > "$S/p7704_pytest-c.txt" 2>&1; echo "exit:$?"
exit:0
```

Final summary line, verbatim, from each saved log:

```
$S/p7704_pytest.txt:   1573 passed, 1 skipped in 124.46s (0:02:04)
$S/p7704_pytest-c.txt: 1573 passed, 1 skipped in 121.21s (0:02:01)
```

Every `SKIPPED` line of the `-rs` summary, from each saved log (identical in both):

```
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
```

The single standing skip is `tests/test_corpus_gate.py`, env-gated on
`TYPSPHINX_CORPUS_REPORT=1` — not `tests/test_changelog_page_gate.py`. Zero changelog-page-gate
skip lines in either saved log.

FULL_PYTEST_EXIT = 0
FULL_PYTEST_C_EXIT = 0
FULL_PYTEST_PASSED = 1573
FULL_PYTEST_C_PASSED = 1573
FULL_PYTEST_FAILED = 0
FULL_PYTEST_C_FAILED = 0
FULL_PYTEST_ERRORS = 0
CHANGELOG_GATE_SKIPS = 0

These counts are recorded against the interpreter named above (`PYVENV_VERSION_INFO = 3.14`,
`PYVENV_HOME` as above) and are not compared with the main checkout's own counts — only with
readings taken on a named interpreter, per `CLAUDE.md` § "Interpreters may differ".

## @preview invariant

```
LC_ALL=C uv run pytest tests/test_preview_version_sync.py -v -p no:cacheprovider
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-adef113a85ee57dc2
configfile: pyproject.toml
plugins: cov-7.1.0
collected 3 items

tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 33%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [ 66%]
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED [100%]

============================== 3 passed in 0.01s ===============================
```

PREVIEW_SYNC_EXIT = 0

```
grep -ho '@preview/[a-z-]*:' typsphinx/templates/base.typ | sort -u | wc -l
4
```

PREVIEW_PACKAGE_COUNT = 4

```
git diff --name-only 9fa1cb894137933f4dbb49d1668fc193e2ef1bc8 HEAD -- typsphinx/templates typsphinx/writer.py typsphinx/template_engine.py
```
prints nothing — the three `@preview` sync sites are untouched across the milestone.

## Commit

This file alone, staged and committed by explicit path, `.planning/` only.

## Tip docs-html

```
rm -rf docs/_build
LANG=C LANGUAGE=C LC_ALL=C uv run tox -e docs-html > "$S/p7704_html.log" 2>&1; echo "exit:$?"
exit:0
```

TIP_HTML_EXIT = 0

Verbatim `build succeeded` line from `$S/p7704_html.log`:

```
LC_ALL=C grep -E '^build succeeded' "$S/p7704_html.log"
build succeeded.
```

The exact-zero form `build succeeded.` does not match the
`build succeeded, N warnings.` pattern, so the warning count is taken as `0` per the plan's own
rule — the same idiom `77-BASE-EVIDENCE.md` used.

TIP_HTML_WARNINGS = 0

## Tip docs-pdf

```
rm -rf docs/_build
LANG=C LANGUAGE=C LC_ALL=C uv run tox -e docs-pdf > "$S/p7704_pdf.log" 2>&1; echo "exit:$?"
exit:0
```

TIP_PDF_EXIT = 0

Verbatim `build succeeded` line from `$S/p7704_pdf.log`:

```
LC_ALL=C grep -E '^build succeeded' "$S/p7704_pdf.log"
build succeeded.
```

TIP_PDF_WARNINGS = 0

Both builds removed the whole `docs/_build` output tree before running — not an incremental
rebuild, which would under-report warnings.

## Warning ledger

| Build | Base (77-01, `77-BASE-EVIDENCE.md`) | Tip (this plan) |
|---|---|---|
| docs-html warnings | `BASE_HTML_WARNINGS = 0` | `TIP_HTML_WARNINGS = 0` |
| docs-pdf warnings | `BASE_PDF_WARNINGS = 0` | `TIP_PDF_WARNINGS = 0` |

Interpreters: the base ledger's `PYVENV_VERSION_INFO` (from `77-CLOSEOUT-GUARD.md`) is `3.14`;
this plan's own `PYVENV_VERSION_INFO` above is also `3.14` — both readings were taken on the same
named interpreter version, so the comparison is not crossing interpreters.

HTML_WARNINGS_NOT_RISEN = yes
PDF_WARNINGS_NOT_RISEN = yes

## Docs invariants

```
git diff --name-only 44f9c6a2045b4943664b1a3473dc3b4422ac3ad3 HEAD -- docs
```
prints nothing — nothing under `docs/` changed by this plan.

```
git diff --name-only 3984b231e30fbb76ba156d2f9b2abe475231bccf HEAD -- docs/source
```
prints nothing — no documentation source changed anywhere in this phase, and no `linkcheck_*` key
was added.
