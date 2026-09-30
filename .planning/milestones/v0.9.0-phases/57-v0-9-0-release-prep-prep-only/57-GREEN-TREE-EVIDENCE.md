# Phase 57 — Local Green-Tree Evidence (SC#3, local half)

## Provisioning and tree identity

Command (per `CLAUDE.md` § "Worktree-isolated execution"):
```
$ unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT
$ uv sync --extra dev --extra docs
```

The un-set of those two vars is what stops `uv` from syncing into an already-activated main
venv and re-pointing it at this worktree; without it, `import typsphinx` would resolve to the
MAIN checkout's absolute path via its PEP-660 editable finder, and every command below would
measure a tree this plan did not build.

Transcript (tail — the resolved package set, truncated to the last block; full output installed
89 packages including this worktree's own editable `typsphinx`):
```
 + jeepney==0.9.0
 + jinja2==3.1.6
 + keyring==25.7.0
 + librt==0.12.0
 + markdown-it-py==4.2.0
 ...
 + pytest==9.1.1
 + pytest-cov==7.1.0
 + ruff==0.15.20
 + sphinx==9.1.0
 + tox==4.56.1
 + tox-uv-bare==1.35.2
 + twine==6.2.0
 + typing-extensions==4.16.0
 + typsphinx==0.9.0 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3585ee232160d75c)
 + typst==0.15.0
 + urllib3==2.7.0
 + virtualenv==21.5.1
```

`typsphinx==0.9.0 (from file:///.../worktrees/agent-a3585ee232160d75c)` on that line is the
provisioning proof itself: `uv` resolved the editable install against THIS worktree's absolute
path, not the main checkout's.

**Step 1 — confirm the tree, three commands:**

```
$ grep -n '^version = ' pyproject.toml
7:version = "0.9.0"

$ grep -c '^## \[0\.9\.0\]' CHANGELOG.md
1

$ uv run python -c "import typsphinx; print(typsphinx.__version__, typsphinx.__file__)"
0.9.0 /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3585ee232160d75c/typsphinx/__init__.py
```

The `__file__` path check matters because this project's editable-install hazard is silent: a
stale/main-checkout resolution would still print `0.9.0` and `import` cleanly, but every test
and lint result that followed would describe code this worktree never touched. Printing and
inspecting the absolute path is the only way to catch that silently-wrong outcome.

All three confirm: version `0.9.0`, exactly one `## [0.9.0]` CHANGELOG heading, and the imported
package resolves inside this worktree, not the main checkout.

## SC#3 — full pytest suite

Command:
```
$ uv run pytest -v --junit-xml="${TMPDIR:-/tmp}/57-06-suite.xml"
```

Summary line (verbatim):
```
- generated xml file: /tmp/claude-1000/-home-yuta-Documents-typsphinx/b8d29a27-ed57-466d-806c-1d077ba1666f/scratchpad/57-06-suite.xml -
================= 1421 passed, 1 skipped in 126.46s (0:02:06) ==================
```

JUnit `testsuite` attributes (verbatim):
```
<testsuite name="pytest" errors="0" failures="0" skipped="1" tests="1422" time="126.446" timestamp="2026-08-17T01:35:39.308797+09:00" hostname="Yuta-PC">
```

`tests="1422"`, `skipped="1"` (stated as a number, not glossed — the single skip is
`tests/test_corpus_gate.py::test_empty_url_before_after`, an opt-in `TYPSPHINX_CORPUS_REPORT=1`
before/after measurement unrelated to the full-corpus render gate itself; see the
"full-corpus gate" section below), `failures="0"`, `errors="0"`. No `-k`, `-m 'not ...'`,
`--deselect` or `--ignore` was used in this invocation. This matches the orchestrator's
independently-measured cross-check baseline of `1421 passed, 1 skipped` exactly.

## SC#3 — format, lint and type

Three commands, each captured separately with its exit code.

**`uv run black --check .`**
```
All done! ✨ 🍰 ✨
339 files would be left unchanged.
```
Exit code: `0`.

**`uv run ruff check .`** — first attempt, then the recorded local mitigation:
```
$ uv run ruff check .
Could not start dynamically linked executable: ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box. For more information, see:
https://nix.dev/permalink/stub-ld
```
Exit code: `127`.

This is the known NixOS stub-loader rejection of a fresh worktree venv's `.venv/bin/ruff` binary
(a generic-linux dynamically-linked ELF), not a code defect. Per the project's standing
mitigation, the main checkout's own already-patched `ruff` binary (verified separately to run:
`ruff 0.15.20`, exit `0`) was symlinked over the worktree's broken copy:
```
$ rm .venv/bin/ruff
$ ln -s /home/yuta/Documents/typsphinx/.venv/bin/ruff .venv/bin/ruff
$ uv run ruff check .
All checks passed!
```
Exit code: `0` (after the symlink swap). This is a `.venv/bin` binary substitution only —
`.venv/` is gitignored and outside every `git diff --name-only` check in this file's
`<verify>`; no source, test or documentation file was touched to make this work. `ruff` DOES
run on this machine when a working binary is available (re-measured this milestone in
`57-RESEARCH.md`'s Pitfall 2, and reconfirmed here on this specific day) — do not write "ruff
cannot run here" from this transcript; the exit-127 line above is a fresh-venv provisioning
artifact, not a statement about local ruff availability in general.

**`uv run mypy typsphinx/`**
```
Success: no issues found in 8 source files
```
Exit code: `0`.

**This trio is an additive local pre-flight.** Lint and type authority sits with the dispatched
CI run under D-13 — no local run reaches the Windows or macOS lanes, and that is the
independent ground for CI's authority regardless of whether ruff happens to run locally today.

## SC#3 — documentation builds

**`uv run tox -e docs-html`**

Final lines (verbatim):
```
build succeeded, 3 warnings.

HTMLページは_build/htmlにあります。
  docs-html: OK (3.81=setup[0.13]+cmd[3.68] seconds)
  congratulations :) (3.85 seconds)
```
Exit code: `0`. **3 warnings** — the three pre-existing `visit_toctree` docstring warnings
(`typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree`,
lines 5/6/21: two `ERROR: Unexpected indentation.` and one
`WARNING: Block quote ends without a blank line; unexpected unindent.`), unrelated to this
phase's CHANGELOG/migration-guide/README/version changes.

**`uv run tox -e docs-pdf`**

Final lines (verbatim):
```
typst: wrote 1 wrapper file(s) -- compile these: typsphinx.typ
Compiling 1 master document(s) to PDF...
Generated PDF: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3585ee232160d75c/docs/_build/pdf/typsphinx.pdf
build succeeded, 5 warnings.
  docs-pdf: OK (4.19=setup[0.11]+cmd[4.08] seconds)
  congratulations :) (4.23 seconds)
```
Exit code: `0`. **5 warnings** — the same 3 docstring warnings plus 2
`WARNING: unknown node type: <doctest_block ...>` lines from `user_guide/output_layout.rst`'s
REPL-style doctest blocks, which `typsphinx`'s translator degrades gracefully rather than
aborting on.

**Baseline comparison.** `.planning/STATE.md`'s Phase 56 close recorded `docs-html` 3 warnings
and `docs-pdf` 5 warnings as "the measured pre-existing baseline, none from any page this phase
touched." This run's counts — 3 and 5 — **match that baseline exactly**. No new warning appears;
neither the new `Migrating from 0.8.x to 0.9.0` changelog.rst subsection (57-04) nor the
promoted CHANGELOG prose (57-03) introduced a regression.

## SC#3 — full-corpus gate

Command:
```
$ uv run pytest tests/test_corpus_gate.py -v
```

Transcript (verbatim):
```
collected 5 items

tests/test_corpus_gate.py::test_catalogue_unknown_visit_multiline PASSED [ 20%]
tests/test_corpus_gate.py::test_catalogue_unknown_visit_windows_crlf_and_prefix PASSED [ 40%]
tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED [ 60%]
tests/test_corpus_gate.py::test_count_empty_url_warnings PASSED          [ 80%]
tests/test_corpus_gate.py::test_empty_url_before_after SKIPPED (SC#3
before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1
to run it (RESEARCH Open Question 1))                                    [100%]

======================== 4 passed, 1 skipped in 13.38s =========================
```

Outcome: PASSED

`TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error` — the class that clones (cached)
and builds the FULL Sphinx `doc/` corpus through `-b typstpdf`, asserting the compiled PDF is
real and fatal-free — is `PASSED`, in words, per the `-v` transcript above, not inferred from a
bare "0 failed" summary line. `A pytest.skip is not evidence.` The one SKIPPED test in this file,
`test_empty_url_before_after`, is a **different** test: it is gated on the opt-in
`TYPSPHINX_CORPUS_REPORT=1` environment variable for a before/after empty-URL-warning
measurement (RESEARCH Open Question 1), not on corpus availability, and it is unrelated to the
full-corpus render gate's own pass/fail criterion. No availability guard was loosened and no
marker was forced to reach this PASSED result — the corpus's shallow clone at the tag matching
the installed `sphinx.__version__` succeeded because network was reachable in this environment.

Because the render gate PASSED (not skipped), the release section's full-corpus `### Verified`
claim **is supported by this run**.

## SC#3 — built-wheel content check (local copy)

Command:
```
$ rm -rf dist
$ uv build
```

Transcript tail (verbatim):
```
Successfully built dist/typsphinx-0.9.0.tar.gz
Successfully built dist/typsphinx-0.9.0-py3-none-any.whl
```
Exit code: `0`. Inspected wheel: `dist/typsphinx-0.9.0-py3-none-any.whl`.

Namelist inspection (inline Python, no unpacking into the tree):
```python
>>> import glob, sys, zipfile
>>> w = sorted(glob.glob('dist/*.whl'))[-1]
>>> n = zipfile.ZipFile(w).namelist()
>>> t = 'typsphinx/templates/README.md'
>>> print('OK' if t in n else 'FATAL', w)
OK dist/typsphinx-0.9.0-py3-none-any.whl
```

Full wheel namelist (verbatim, sorted):
```
typsphinx-0.9.0.dist-info/METADATA
typsphinx-0.9.0.dist-info/RECORD
typsphinx-0.9.0.dist-info/WHEEL
typsphinx-0.9.0.dist-info/entry_points.txt
typsphinx-0.9.0.dist-info/licenses/LICENSE
typsphinx-0.9.0.dist-info/top_level.txt
typsphinx/__init__.py
typsphinx/builder.py
typsphinx/pdf.py
typsphinx/removed_config.py
typsphinx/template_engine.py
typsphinx/template_registry.py
typsphinx/templates/README.md
typsphinx/templates/base.typ
typsphinx/translator.py
typsphinx/writer.py
```

`typsphinx/templates/README.md` and `typsphinx/templates/base.typ` are both present — the
bundled template-directory files the CI Build Package job's own wheel-content step checks for.
`git status --porcelain` shows no untracked `dist/` entry (the repository's `dist/.gitignore`
ignores the whole directory), so nothing here is staged for commit.

This is a **local copy** of SC#3's built-wheel content check. The CI-side one is captured in
`57-CI-EVIDENCE.md` by plan 57-05 against a real packaging job; neither replaces the other — an
editable install (which every other command in this file runs against) never packs a wheel and
so cannot detect a narrowed `package-data` glob on its own.

## Executed versus skipped

- **A bare `tox`** (no `-e` selector) — NOT RUN. `tox.ini`'s `env_list = py312, py313, lint,
  type, cov, docs` includes environments this machine cannot provision standalone (see next
  item), so a bare run would fail before producing any useful signal.
- **`tox -e py312`** — NOT RUN. It downloads a standalone CPython 3.12 interpreter whose ELF the
  NixOS stub loader rejects, the same class of environmental defect as the fresh-venv `ruff`
  binary above (mitigated here by a symlink; the standalone-interpreter download has no
  equivalent local mitigation).

Full-matrix authority (py312/py313 × ubuntu/macos/windows, plus lint and type across that
matrix) belongs to the dispatched CI run under D-13 — no local run on this machine reaches the
Windows or macOS lanes regardless of whether any individual local tool happens to run.

## Division of authority

- **CI** (`57-CI-EVIDENCE.md`, plan 57-05) is authoritative for the six-lane py312/py313 ×
  ubuntu/macos/windows matrix, and for lint and type across that matrix.
- **This file** (`57-GREEN-TREE-EVIDENCE.md`, plan 57-06) is authoritative for both
  documentation builds (`docs-html`, `docs-pdf`), the full-corpus gate
  (`tests/test_corpus_gate.py`), and a local copy of the built-wheel content check — the three
  things `ci.yml` does not structurally cover.
- **`57-GOAL-CLAIM-EVIDENCE.md`** (plan 57-07) is authoritative for the multi-template PDF claim
  (D-14) — that `typst_documents` entries with different templates produce genuinely different
  PDFs.

## Repo cleanliness

```
$ git diff --name-only -- typsphinx/ tests/ docs/ .planning/REQUIREMENTS.md
```
(no output — nothing under those paths changed; this plan runs and records, it does not edit)
