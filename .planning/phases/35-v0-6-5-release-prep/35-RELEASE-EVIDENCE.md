# Phase 35: v0.6.5 Release Prep — Release Evidence

This file records SC#1 (freshness re-run), SC#2 (cited), SC#3, SC#4, and SC#5 of ROADMAP Phase 35,
with verbatim command output backing every claim. Every command below was re-run live during this
plan's execution (2026-07-29); no output is carried forward from `35-CONTEXT.md`, `35-RESEARCH.md`,
`35-PATTERNS.md`, or a prior phase's evidence file as evidence — those documents are inputs to be
re-verified, not evidence themselves.

**Filename note:** this file is deliberately not named `35-VERIFICATION.md` — that name is reserved
by the `/gsd-verify-work` verifier, which overwrites it wholesale when it runs. The surviving
precedent for this naming choice is `33-RELEASE-EVIDENCE.md` from the previous release-prep phase.

**Provisioning note:** all commands below were run inside this plan's isolated git worktree, after
`unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync --extra dev --extra docs` and symlinking a
working `uv`/`ruff` binary into `.venv/bin/` (the standing NixOS dynamic-linker shim this project's
`CLAUDE.md` documents), and every command was invoked through `uv run`.

---

## SC#1: version-sync guards re-run for freshness (carried primarily from plan 35-03)

**Claim:** `pyproject.toml` declares `0.6.5` as the sole version literal, `uv.lock` is in lockstep,
`typsphinx.__version__` reports `0.6.5`, and README's Status line agrees. Full evidence — including
the `uv.lock` numstat and the `uv sync --extra dev --locked` regeneration proof — is recorded in
`35-03-SUMMARY.md`; that plan's own transcript is not re-typed here. This section only re-runs the
two guard commands fresh, for evidence-freshness per this plan's own convention.

### Step 1 — `__version__` probe

Command:
```
$ uv run python -c "import typsphinx; print(typsphinx.__version__)"
```
Verbatim output:
```
0.6.5
```

### Step 2 — the two version-sync guard tests

Command:
```
$ uv run pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -q
```
Verbatim output:
```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a27886969f004fcff
configfile: pyproject.toml
plugins: cov-7.1.0
collected 4 items

tests/test_readme_version_sync.py .                                      [ 25%]
tests/test_preview_version_sync.py ...                                   [100%]

============================== 4 passed in 0.02s ===============================
```

### SC#1 verdict

**SC#1: MET.** `typsphinx.__version__` reports `0.6.5` and both version-sync guards are green,
consistent with `35-03-SUMMARY.md`'s full evidence (the `uv.lock` numstat of exactly 1 insertion / 1
deletion, and `uv sync --extra dev --locked` exiting 0).

---

## SC#2: curated CHANGELOG entry (carried from plan 35-04)

**Claim:** `CHANGELOG.md` carries a curated `## [0.6.5]` entry (lead paragraph + `### Fixed` +
`### Verified`) directly above `## [0.6.4]`, and the tail link block is rolled over (`[0.6.5]:`
release-tag line added, `[Unreleased]:` compare advanced to `v0.6.5...HEAD`). This is fully evidenced
in `35-04-SUMMARY.md` (whole-plan `CHANGELOG.md` diff: 25 insertions, exactly 1 deletion). No
re-transcription is needed here — this is a prose/structural artifact with no dedicated automated
guard in this repository (per `35-VALIDATION.md`'s own Requirements → Test Map: "manual / prose —
N/A"). The three `### Verified` bullets that CHANGELOG entry states are each given a matching
evidence section below (SC#3 and SC#4).

### SC#2 verdict

**SC#2: MET** (per `35-04-SUMMARY.md`'s verification; not re-run here as there is no mechanical
guard to re-run).

---

## SC#3: the post-bump tree is proven green end to end on a live run

**Claim:** the full pytest suite, `black`, `ruff`, `mypy`, the full-corpus `-b typstpdf` regression
gate, and (per D-12) the two docs dogfooding builds `tox -e docs-html` / `tox -e docs-pdf` are all
green on the post-bump tree.

### Step 1 — full pytest suite

Command:
```
$ uv run python -m pytest -q --tb=no -rf
```
Verbatim tail output:
```
======================= 649 passed, 1 skipped in 56.86s ========================
```
649 passed / 1 skipped / 0 failed — matches the `35-RESEARCH.md` baseline (`649 passed, 1 skipped`)
exactly, and matches `35-03-SUMMARY.md`'s post-bump re-run. Exit code 0.

### Step 2 — `black --check .`

Command:
```
$ uv run black --check .
```
Verbatim output:
```
All done! ✨ 🍰 ✨
173 files would be left unchanged.
```
Exit code 0.

### Step 3 — `ruff check .`

Command:
```
$ uv run ruff check .
```
Verbatim output:
```
All checks passed!
```
Exit code 0.

### Step 4 — `mypy typsphinx/`

Command:
```
$ uv run mypy typsphinx/
```
Verbatim output:
```
Success: no issues found in 6 source files
```
Exit code 0.

### Step 5 — full-corpus `-b typstpdf` regression gate, isolated confirmation

This isolated run exists purely as an **evidence-legibility step, not a coverage step**. A plain
full-suite run (Step 1 above) applies no `-m "not slow"` filter anywhere in this repository's
`pyproject.toml` `addopts`, its `tox.ini`, or `.github/workflows/ci.yml` — despite
`tests/test_corpus_gate.py`'s own module docstring claiming the slow-marked class is excluded from
the default suite. **That docstring claim is stale and does not match this repository's actual
configuration**: no marker filter is applied anywhere, so the plain `pytest -q` run in Step 1 already
executed the corpus gate and every other slow-marked test in the suite. The isolated run below is
recorded only because it is easier evidence-file prose to point at a 2-item run than at one line
inside a 650-item run; the next release-prep phase should not re-derive this correction from
scratch.

Command:
```
$ uv run pytest tests/test_corpus_gate.py -q -m slow
```
Verbatim output:
```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a27886969f004fcff
configfile: pyproject.toml
plugins: cov-7.1.0
collected 5 items / 3 deselected / 2 selected

tests/test_corpus_gate.py .s                                             [100%]

================= 1 passed, 1 skipped, 3 deselected in 12.70s ==================
```
1 passed, 1 skipped (the pre-existing env-gated `test_empty_url_before_after`, unrelated to this
phase), 3 deselected (the non-`slow` tests in the same file, already covered by Step 1). Exit code 0.

### Step 6 — `tox -e docs-html` (D-12)

Command:
```
$ uv run tox -e docs-html
```
Verbatim tail output:
```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a27886969f004fcff/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:7: ERROR: Unexpected indentation. [docutils]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a27886969f004fcff/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:8: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
...
build succeeded, 2 warnings.

HTMLページは_build/htmlにあります。
  docs-html: OK (3.69=setup[0.49]+cmd[3.20] seconds)
  congratulations :) (3.72 seconds)
```
Exit code 0 (independently re-confirmed via a captured `$?` on a second invocation: `EXIT:0`). The
two warnings are a pre-existing docstring-formatting nit in `visit_toctree`'s own docstring
(unrelated to this milestone's translator change, which touched only the math visitors) — they do
not fail the build.

### Step 7 — `tox -e docs-pdf` (D-12)

Command:
```
$ uv run tox -e docs-pdf
```
Verbatim tail output:
```
preparing documents... Template written to /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a27886969f004fcff/docs/_build/pdf/_template.typ
done
writing output... [api/index] done
writing output... [changelog] done
writing output... [contributing] done
writing output... [examples/advanced] done
writing output... [examples/basic] done
writing output... [examples/index] done
writing output... [index] done
writing output... [installation] done
writing output... [quickstart] done
writing output... [user_guide/builders] done
writing output... [user_guide/configuration] done
writing output... [user_guide/index] done
writing output... [user_guide/templates] done
Copying template assets...
Compiling 1 master document(s) to PDF...
Generated PDF: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a27886969f004fcff/docs/_build/pdf/typsphinx.pdf
build succeeded, 2 warnings.
  docs-pdf: OK (3.63=setup[0.51]+cmd[3.12] seconds)
  congratulations :) (3.65 seconds)
```
Exit code 0. The project's own documentation set builds through the `typstpdf` builder and produces
`docs/_build/pdf/typsphinx.pdf`. This is D-12's addition to the three runs SC#3 names — since this
milestone touched the translator (the two math visitors), rebuilding the project's own documentation
through `typstpdf` is worth doing rather than ceremonial: it is the closest thing this project has to
a live consumer of the fix.

### Step 8 — working-tree cleanliness after both docs builds

Command:
```
$ git status --porcelain -- docs/
```
Verbatim output:
```
(empty)
```
Both tox environments build out of `docs/` into `docs/_build/`, which is gitignored; the empty
output confirms neither build wrote anything unexpected outside that path. Nothing under `docs/` is
committed by this phase.

### SC#3 verdict

**SC#3: MET.** All seven live runs (full pytest suite, `black --check .`, `ruff check .`,
`mypy typsphinx/`, the isolated corpus-gate confirmation, `tox -e docs-html`, `tox -e docs-pdf`) exit
0 on the post-bump tree, and the docs builds leave the working tree clean under `docs/`.
