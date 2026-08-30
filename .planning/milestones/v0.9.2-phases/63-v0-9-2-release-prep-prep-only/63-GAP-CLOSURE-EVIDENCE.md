# Phase 63 Gap Closure — Green-Tree Re-Proof, CI-Dispatch Decision, D-24 Declination

**Timestamp:** 2026-08-30T13:28:28Z
**Worktree tip at time of measurement:** `41eb46be` (Task 2's commit); Task 1's commit
`2a0bc3be` carries the CHANGELOG.md correction this closure re-proves the tree against.

## Provisioning and tree identity

```
$ unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT
$ uv sync --extra dev
... typsphinx==0.9.2 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-aaf9146fc13f627a9)

$ uv run python -c "import typsphinx, sys; print(typsphinx.__file__)"
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aaf9146fc13f627a9/typsphinx/__init__.py
```

The imported `typsphinx.__file__` resolves inside THIS worktree, not the main checkout — the
precondition this task's own `<precondition>` requires. Every measurement below is therefore a
measurement of the corrected tree, not of the unchanged main-tree package.

## The test suite, run with the documentation extra

**Why the docs extra is added explicitly.** `tests/test_changelog_page_gate.py` guards
`TestChangelogPageContentCoverage` and `TestChangelogIncludeCompilesToPdf` on an importable
`myst_parser`, which lives in the `docs` extra only (`pyproject.toml`). A worktree provisioned
with `--extra dev` alone reports a fully green suite while silently skipping exactly the two
classes that bind CHANGELOG content to the rendered HTML page and to a real compiled PDF — the
precise class of gap this whole closure exists to prevent from recurring one level deeper. The
suite is therefore invoked with `--extra docs` added at the invocation:

```
$ uv run --extra dev --extra docs pytest -q -rs
...
=========================== short test summary info ============================
SKIPPED [1] tests/test_corpus_gate.py:530: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
================= 1547 passed, 1 skipped in 127.77s (0:02:07) ==================
[exited with code 0]
```

**1547 passed, 1 skipped — these counts differ from `63-GREEN-TREE-EVIDENCE.md`'s recorded 1543
passed / 5 skipped because the extras differ, not because the tree changed or the tests changed.**
`63-GREEN-TREE-EVIDENCE.md`'s run carried `--extra dev` only; four of its five recorded skips were
the `myst_parser`-gated classes (`TestChangelogPageContentCoverage`'s three tests and
`TestChangelogIncludeCompilesToPdf`'s one test), which execute here instead: 1543 + 4 = 1547
passed, 5 − 4 = 1 skipped. The one remaining skip (`test_empty_url_before_after`) is unrelated to
either extra — it is gated on the `TYPSPHINX_CORPUS_REPORT` environment variable. These two runs
are not presented as the same measurement; they are two different, both-correct measurements of
two different install surfaces.

**Zero failures.** No test in the suite reported a failure; the run's own exit code is 0 and no
`failed` line appears in the short summary.

**Why the full suite was run rather than a targeted subset.** `grep -rln 'CHANGELOG' tests/`:

```
$ grep -rln 'CHANGELOG' tests/
tests/test_bundle_layout_sweep_gate.py
tests/test_changelog_extraction.py
tests/test_changelog_page_gate.py
tests/test_no_stale_github_io_links.py
tests/test_state_guard_numref_gate.py
tests/fixtures/changelog_include_gate/changelog.rst
tests/fixtures/changelog_include_gate/conf.py
```

A grep-derived bound on "what could observe this diff" would need to trust that this file list is
complete and that none of the 350+ other test files reads `CHANGELOG.md` indirectly (for example
through a fixture, a doc build, or a golden-file comparison it does not name literally). The full
suite subsumes that bound entirely — it exercises the version-sync guard trio and every test file
that touches CHANGELOG content, named or not, so no separate trust decision about a subset's
completeness is required.

## Both documentation builds, from a removed build directory (D-21)

**Why both are re-run.** `docs/source/changelog.rst` includes the repo-root `CHANGELOG.md` through
the MyST parser, so both documentation builders consume exactly the prose this closure edited.
`63-GREEN-TREE-EVIDENCE.md` records both builders' warning counts (3 for `docs-html`, 5 for
`docs-pdf`) as part of this phase's SC#4 evidence; re-measuring them here — rather than assuming
the prose edit did not change anything — is what SC#2's "read rather than assumed" standard
requires applied to the build surface, not just the extractor's stdout.

**Why the build directory is removed before each build, as a command, not an assumption.** An
incremental rebuild reuses cached doctrees and can under-report warnings for pages it does not
re-parse, manufacturing a false "baseline match" — a repeat finding in this project
(`63-CONTEXT.md` D-21). Removing `docs/_build` immediately before each build forces a full,
freshly-invalidated rebuild.

```
$ rm -rf docs/_build && uv run tox -e docs-html
...
build succeeded, 3 warnings.
  docs-html: OK (3.84=setup[0.12]+cmd[3.72] seconds)
```

```
$ rm -rf docs/_build && uv run tox -e docs-pdf
...
Generated PDF: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-aaf9146fc13f627a9/docs/_build/pdf/typsphinx.pdf
build succeeded, 5 warnings.
  docs-pdf: OK (4.16=setup[0.11]+cmd[4.05] seconds)
```

Both exit successfully (`OK`). `docs-html` reports 3 warnings — matches
`63-GREEN-TREE-EVIDENCE.md`'s recorded baseline of 3 exactly. `docs-pdf` reports 5 warnings —
matches the recorded baseline of 5 exactly. Both counts match; there is no differing warning line
to transcribe as a finding.

## The CI-dispatch decision, measured rather than assumed

**Which extra each `ci.yml` job installs**, read from the workflow file itself:

```
$ grep -n 'uv sync' .github/workflows/ci.yml
37:        run: uv sync --extra dev --locked
67:        run: uv sync --extra dev --locked
88:        run: uv sync --extra dev --locked
109:        run: uv sync --extra dev --locked
174:          uv sync --extra dev --locked
202:        run: uv sync --locked
```

Every job that runs `pytest` via `tox` (`test`, `lint`, `type-check`, `coverage`) installs
`--extra dev` only. `build` (line 174) also installs `--extra dev` for its `twine check` step. No
job installs `--extra docs`. The `integration` job (line 202) installs no extra at all and never
invokes `pytest` — it drives `sphinx-build -b typst` directly against the bundled examples, so it
is out of scope for a `pytest`-based content-coverage class regardless.

**Which extra each `tox` environment `ci.yml` invokes declares:**

```
$ grep -n 'extras = ' tox.ini
35:extras = dev
42:extras = dev
50:extras = dev
57:extras = dev
64:extras = docs
72:extras = docs
80:extras = docs
```

`[testenv]` (covers `py312`/`py313`), `[testenv:lint]`, `[testenv:type]`, and `[testenv:cov]` — the
four tox environments `ci.yml` actually invokes (`py312`, `py313`, `lint`, `type`, `cov`) — all
declare `extras = dev`. Only `[testenv:docs-html]`, `[testenv:docs-pdf]`, and `[testenv:docs]`
declare `extras = docs`, and `ci.yml` invokes none of the three.

**The decision and its consequence.** Because no `ci.yml` job or the tox environment it invokes
ever installs the `docs` extra, `myst_parser` is never importable in any CI lane, so
`TestChangelogPageContentCoverage` and `TestChangelogIncludeCompilesToPdf` — the two classes that
actually read CHANGELOG content through a real build — skip in every one of the twelve jobs. No
`ci.yml` job reads CHANGELOG content at all. A fresh dispatch of `ci.yml` against this closure's
tip would therefore exercise nothing in this diff, at the cost of running twelve jobs end to end.
**No fresh CI dispatch was made in this closure.**

**Lint authority remains with the phase's existing green run.** `63-CI-EVIDENCE.md` records run id
`33309565005` (head SHA `225c6618ffd94ec5e1601de538438c47b4d558a9`) with all 12 jobs concluding
`success`, including the `Lint and Format Check` job (job id `99252047964`), whose transcribed
step log shows `ruff check .` executed and reported `All checks passed!`. `Lint and Format Check`'s
one substantive step is `Run lint with tox` (`ci.yml:69`), which runs `tox -e lint` —
`black --check .` then `ruff check .`. Neither command reads Markdown files, so a prose-only diff
confined to `CHANGELOG.md` cannot change either command's verdict. `ruff`'s verdict for this
closure is therefore taken from that same recorded run, not re-derived, and never substituted
locally:

```
$ uv run ruff check .
Could not start dynamically linked executable: ruff
NixOS cannot run dynamically linked executables intended for generic
linux environments out of the box.
(exit 127)
```

`ruff` remains a generic-linux ELF unrunnable on this NixOS host in a freshly `uv sync`-provisioned
worktree venv — the recorded, standing hazard. This local failure is never recorded as this
closure's lint verdict, and its silence is never recorded as a pass. `release.yml` is not
triggered for any reason in this closure — no tag, no `workflow_dispatch` on that workflow, no
push to a branch its triggers watch.

## Commits after the CI dispatch — a deliberate, recorded supersession

`63-SC5-INVARIANTS.md` § "Commits after the CI dispatch" states that every commit landing after
the recorded CI dispatch (run `33309565005`, head SHA `225c6618`) was confined to `.planning/`.
This closure adds a commit outside `.planning/` after that dispatch:

```
$ git diff --name-only 225c6618ffd94ec5e1601de538438c47b4d558a9..HEAD
.planning/ROADMAP.md
.planning/STATE.md
.planning/phases/63-v0-9-2-release-prep-prep-only/63-03-SUMMARY.md
.planning/phases/63-v0-9-2-release-prep-prep-only/63-04-SUMMARY.md
.planning/phases/63-v0-9-2-release-prep-prep-only/63-05-PLAN.md
.planning/phases/63-v0-9-2-release-prep-prep-only/63-06-PLAN.md
.planning/phases/63-v0-9-2-release-prep-prep-only/63-CHANGELOG-EVIDENCE.md
.planning/phases/63-v0-9-2-release-prep-prep-only/63-CI-EVIDENCE.md
.planning/phases/63-v0-9-2-release-prep-prep-only/63-CLOSEOUT-GUARD.md
.planning/phases/63-v0-9-2-release-prep-prep-only/63-CONTEXT.md
.planning/phases/63-v0-9-2-release-prep-prep-only/63-HANDOFF.md
.planning/phases/63-v0-9-2-release-prep-prep-only/63-REVIEW.md
.planning/phases/63-v0-9-2-release-prep-prep-only/63-SC5-INVARIANTS.md
.planning/phases/63-v0-9-2-release-prep-prep-only/63-VALIDATION.md
.planning/phases/63-v0-9-2-release-prep-prep-only/63-VERIFICATION.md
CHANGELOG.md
```

`CHANGELOG.md` now appears in that list — Task 1's correction commit. This **supersedes**
`63-SC5-INVARIANTS.md`'s all-`.planning/`-confined statement; the supersession is deliberate and
reasoned, not an omission. The CHANGELOG.md edit does not affect the recorded CI run's own
correctness (it was correct against the tip it ran on) and does not itself need a fresh CI run for
the reasons measured above (no lane reads CHANGELOG content). Plan `63-06` records the correction
inside `63-SC5-INVARIANTS.md` itself, so that file's own text is brought back into agreement with
the tree.

## D-24 — the declined finding, recorded visibly

`63-REVIEW.md` finding **IN-01** reads (quoted): "`RELEASE_VERSIONS` count-comment still says
'0.4.4 through 0.9.2' while the tuple starts at '0.4.1'" — `tests/test_changelog_page_gate.py:47`'s
comment states a range that omits the tuple's first three entries (`0.4.1`, `0.4.2`, `0.4.3`).

This finding is:
- **Info-severity** (`63-REVIEW.md` frontmatter: `info: 1`, and IN-01 is filed under the report's
  `## Info` heading, not `## Critical Issues`).
- **Pre-existing** — the prior text read "0.4.4 through 0.9.0" against the same `0.4.1`-first
  tuple; this phase only bumped the count and the upper-bound version, inheriting the inaccuracy
  rather than introducing it.
- **Absent from `63-VERIFICATION.md`'s `gaps:` block** — that block names exactly one gap, SC#2 /
  CR-01, and does not mention IN-01 or the range-comment inaccuracy anywhere.
- **Declined by the project owner for this closure** — `63-CONTEXT.md` D-24 records: "`63-REVIEW.md`
  IN-01 stays out of scope. ... No plan in this closure edits that file, and `63-05` gates on its
  being untouched."

**No plan in this closure edits `tests/test_changelog_page_gate.py`:**

```
$ git status --porcelain tests/test_changelog_page_gate.py
(empty; no output)

$ git diff --name-only v0.9.0..HEAD -- tests/test_changelog_page_gate.py | wc -l
1
```

The file's entire milestone-wide change count is the single commit `1129ee1a
test(63-01): extend RELEASE_VERSIONS to 0.9.2 and consolidate the byte-identity evidence` — D-24
held; this closure adds no second change to that file. A later reader must not read the absence of
an IN-01 fix here as an oversight: it is a recorded, owner-approved declination.

## Existing external-API declaration — confirmed, not rewritten

`.planning/phases/63-v0-9-2-release-prep-prep-only/COVERAGE.md` already declares no external API
integration for this phase, covering `pyproject.toml`, `uv.lock`, `README.md`, `CHANGELOG.md`, and
`tests/test_changelog_page_gate.py`, plus this project's own `pytest`/`black`/`ruff`/`mypy`/
`docs-html`/`docs-pdf` tooling and this project's own `ci.yml` (never `release.yml`). This
closure's scope — one Markdown file (`CHANGELOG.md`) plus planning documents, with the same local
test/lint/type/docs tooling and zero workflow dispatches — is a strict subset of `COVERAGE.md`'s
already-declared file set. The declaration therefore still holds without modification; no
capability matrix for an API this closure does not touch was authored.

## Targeted re-run: changelog gate, extractor contract tests, version-sync guard trio

```
$ uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py tests/test_changelog_extraction.py tests/test_extension.py::test_version_matches_pyproject_toml tests/test_readme_version_sync.py tests/test_preview_version_sync.py -q
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-aaf9146fc13f627a9
configfile: pyproject.toml
plugins: cov-7.1.0
collected 17 items

tests/test_changelog_page_gate.py ......                                 [ 35%]
tests/test_changelog_extraction.py ......                                [ 70%]
tests/test_extension.py .                                                [ 76%]
tests/test_readme_version_sync.py .                                      [ 82%]
tests/test_preview_version_sync.py ...                                   [100%]

============================== 17 passed in 4.00s ==============================
```

17 passed, 0 failed, 0 skipped — the changelog-content gate (all 6 of
`tests/test_changelog_page_gate.py`, including the two `docs`-extra-gated content-coverage
classes), the extractor's own contract tests (`tests/test_changelog_extraction.py`, 6), and the
version-sync guard trio (`test_version_matches_pyproject_toml`,
`test_readme_status_version_matches_pyproject`, and `test_preview_version_sync.py`'s 3 tests) all
pass against the corrected tree under the documentation extra.

## Final tree-state confirmation

```
$ git status --porcelain typsphinx/ .planning/REQUIREMENTS.md
(empty; no output)
```

Nothing under `typsphinx/` was touched by this closure, and `.planning/REQUIREMENTS.md` is
byte-unchanged — REL-09's checkbox remains `[ ]`, exactly as this prep-only phase requires.
