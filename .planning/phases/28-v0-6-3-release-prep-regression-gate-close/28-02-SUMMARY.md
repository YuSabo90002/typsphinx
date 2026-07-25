---
phase: 28-v0-6-3-release-prep-regression-gate-close
plan: 02
subsystem: release-engineering
tags: [pytest, tox, corpus-gate, regression-gate, v0.6.3, sphinx, typst]

# Dependency graph
requires:
  - phase: 28-01
    provides: "pyproject.toml/uv.lock/README.md version bump 0.6.2 -> 0.6.3 (SC#1)"
provides:
  - "Live-run evidence that the SC#3 full-corpus regression gate genuinely PASSED (not skipped) against the post-version-bump tree"
  - "Live full pytest suite green (656 passed, 1 skipped) with the single skip explicitly named (test_empty_url_before_after, not the corpus gate)"
  - "Live docs-build warning baselines for docs-pdf (2 lines) and docs-multilang (4 lines), each recorded per-environment"
  - "SC#4 milestone-invariant git-diff evidence: zero new runtime deps, no @preview version bump, base.typ diff confined to exactly 2 lang-parameter lines"
  - "SC#5 scope-fence negative assertions: no v0.6.3 tag, release.yml untouched, tests/typsphinx/docs/examples clean"
  - "28-VERIFICATION.md evidence record (new file) for plan 28-03's CHANGELOG ### Verified section to cite"
affects: [28-03]

# Tech tracking
tech-stack:
  added: []
  patterns: ["-rs pytest flag to distinguish genuine skip from genuine pass on gates with a pytest.skip escape hatch", "per-tox-environment warning-count baselines instead of one shared threshold"]

key-files:
  created:
    - .planning/phases/28-v0-6-3-release-prep-regression-gate-close/28-VERIFICATION.md
  modified: []

key-decisions:
  - "Ran the corpus gate as a standalone node-id invocation (-m slow -rs -v -s) separately from the full suite, so its own PASSED/1-passed verdict is unambiguous and cannot be confused with the full suite's unrelated single skip"
  - "Reverted two docs/locale/ja/LC_MESSAGES/*.mo files that were regenerated (byte-different, same size) as an unintentional side effect of running the docs-multilang/docs-pdf tox builds, to keep the docs/ scope-fence porcelain-clean"
  - "Restricted the SC#5 'files touched by Phase 28' list to Phase 28's own commit range (first Phase 28 commit..HEAD), not the full main..HEAD milestone diff, since main..HEAD naturally includes Phases 24-27.1's typsphinx/docs changes which are out of this plan's scope to re-litigate"

requirements-completed: []  # Phase 28 is a release/close phase; carries no requirement IDs (.planning/REQUIREMENTS.md:65)

coverage:
  - id: D1
    description: "SC#3 full-corpus regression gate demonstrably PASSED (not skipped) against the post-version-bump tree"
    verification:
      - kind: integration
        ref: "tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v -s"
        status: pass
    human_judgment: false
  - id: D2
    description: "Full pytest suite green with the single skip correctly identified as test_empty_url_before_after (env-gated), not the SC#3 gate"
    verification:
      - kind: unit
        ref: "pytest -q -rs (full suite)"
        status: pass
    human_judgment: false
  - id: D3
    description: "docs-pdf and docs-multilang tox builds each stay within their own per-environment warning baseline (2 lines / 4 lines)"
    verification:
      - kind: other
        ref: "tox -e docs-pdf and tox -e docs-multilang raw log inspection"
        status: pass
    human_judgment: false
  - id: D4
    description: "SC#4 milestone invariants hold: zero new runtime deps, no @preview version bump, base.typ diff confined to the lang parameter"
    verification:
      - kind: unit
        ref: "tests/test_preview_version_sync.py -v"
        status: pass
      - kind: other
        ref: "git diff main..HEAD -- pyproject.toml / typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ"
        status: pass
    human_judgment: false
  - id: D5
    description: "SC#5 scope fence held: no v0.6.3 tag, release.yml untouched, no tests/typsphinx/docs/examples modification"
    verification:
      - kind: other
        ref: "git tag --list 'v0.6.3'; git status --porcelain .github/workflows/release.yml typsphinx/ tests/ docs/ examples/"
        status: pass
    human_judgment: false

duration: ~10min (measured from worktree base commit 17:21:46+09:00 to final task commit 17:30:48+09:00)
completed: 2026-07-25
status: complete
---

# Phase 28 Plan 02: Regression-Gate Close — Corpus Gate, Full Suite, Docs Builds, SC#4/SC#5 Verification Summary

**Live re-ran the SC#3 full-corpus regression gate, full pytest suite, and both docs-build tox environments against the post-version-bump v0.6.3 tree, and recorded verbatim evidence plus SC#4/SC#5 git-diff assertions in a new `28-VERIFICATION.md`.**

## Performance

- **Duration:** ~10 min (worktree base commit `7e3d662` at 17:21:46+09:00 → final task commit `f0ca561` at 17:30:48+09:00)
- **Started:** 2026-07-25T08:21:46Z
- **Completed:** 2026-07-25T08:31:05Z
- **Tasks:** 2
- **Files modified:** 1 (new file: `28-VERIFICATION.md`)

## Accomplishments

- Proved the SC#3 corpus gate genuinely **passed** (not silently skipped) on a live re-run against this worktree's post-version-bump tree: `1 passed in 13.81s`, `Unknown Visit Catalogue: []`, zero `SKIPPED` lines.
- Proved the full pytest suite is green (`656 passed, 1 skipped in 56.33s`, 0 failed) and explicitly named the single skip as `test_empty_url_before_after` (env-gated behind `TYPSPHINX_CORPUS_REPORT=1`) — distinct from and unrelated to the SC#3 gate, preventing the documented misread risk (T-28-05).
- Recorded two independent, per-environment docs-build warning baselines: `tox -e docs-pdf` (English-only) at exactly 2 warning lines, `tox -e docs-multilang` (English + 日本語) at exactly 4 (2 languages × 2 lines) — both matching the phase-entry baseline with zero growth.
- Confirmed SC#4's milestone invariants via live `git diff main..HEAD`: the `pyproject.toml` diff is confined to the single version-literal line-pair, the `@preview` package-version grep across all three declaration sites returns zero matches, and `templates/base.typ`'s diff is confined to exactly 2 lines (the Phase 27.1 `lang` parameter and its wiring) — `git diff --numstat` reads `2\t1\ttypsphinx/templates/base.typ`.
- Confirmed SC#5's scope fence negatively: no `v0.6.3` git tag exists, `.github/workflows/release.yml` is untouched, and `typsphinx/`/`tests/`/`docs/`/`examples/`/`.github/` are all porcelain-clean.

## Task Commits

Each task was committed atomically:

1. **Task 1: Run 3-point regression gate (corpus gate / full suite / 2 docs builds), paste raw logs into 28-VERIFICATION.md** - `5a8b342` (docs)
2. **Task 2: Append SC#4 invariant git-diffs and SC#5 negative asserts, complete the Observable Truths table** - `f0ca561` (docs)

_No feat/fix commits — this plan modifies zero source, test, docs, or examples files; it runs existing gates and records evidence only._

## Files Created/Modified

- `.planning/phases/28-v0-6-3-release-prep-regression-gate-close/28-VERIFICATION.md` - New evidence record: SC#3 corpus-gate log, full-suite summary with named single skip, per-environment docs-build warning tallies, SC#4 invariant `git diff` evidence, SC#5 negative assertions, and the completed Observable Truths table.

## Decisions Made

- Ran the corpus gate as its own standalone `-m slow -rs -v -s` invocation, separate from the full-suite run, so its `1 passed in N.NNs` verdict is unambiguous and cannot be conflated with the full suite's unrelated single skip (`test_empty_url_before_after`).
- Reverted two `docs/locale/ja/LC_MESSAGES/*.mo` files that `tox -e docs-pdf`/`tox -e docs-multilang` regenerated as a byte-different (same-size) recompilation side effect of the same source `.po` files, via `git checkout -- <path>`, to keep the `docs/` scope-fence porcelain-clean per SC#5.
- Restricted the "files touched by Phase 28" list in the SC#5 section to Phase 28's own commit range (`git diff --name-only <first-phase-28-commit>^..HEAD`) rather than the full `main..HEAD` milestone diff, since the latter naturally includes Phases 24–27.1's `typsphinx/`/`docs/` changes that are legitimately out of this plan's scope — using the wider diff would have produced a false-positive "docs/typsphinx touched" reading.

## Deviations from Plan

None — plan executed exactly as written. The `.mo`-file revert above is a corrective action within Task 1's own scope (undoing an unintended build-time side effect before its acceptance criteria were checked), not a deviation from the plan's instructions.

## Issues Encountered

None. Both gate runs, both docs builds, and all `git diff`/pytest assertions reproduced their expected values from `28-RESEARCH.md`'s prior (pre-version-bump) session on the first attempt, after the mandatory worktree provisioning (`uv sync --extra dev` + the `.venv/bin/uv` NixOS-ELF-exec shim per orchestrator instructions).

## User Setup Required

None - no external service configuration required.

## Verbatim Corpus-Gate Log (durable executor-owned copy, per plan `<output>` spec)

This is the exact same log recorded in `28-VERIFICATION.md`'s `## SC#3 — Full-Corpus Regression Gate`
section, duplicated here so it survives even if `/gsd-verify-work` overwrites `28-VERIFICATION.md`.

Command run:

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

Full pytest suite summary (verbatim, second live run against this same tree, re-confirmed via
`grep -Ec` acceptance criteria after the fact):

```
SKIPPED [1] tests/test_corpus_gate.py:529: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
656 passed, 1 skipped in 56.33s
```

## Docs Build Warning Tallies (durable copy)

- **docs-pdf warning lines: 2** (English-only build; both lines are the pre-existing, out-of-scope `visit_toctree` docstring defect in `typsphinx/translator.py`, unchanged from the phase-entry baseline). Build tail: `build succeeded, 2 warnings.`
- **docs-multilang warning lines: 4** (English + 日本語 build; the same 2-line defect repeated once per language). Build tail: `✓ Multi-language build complete!` — `English (en): ... (22 HTML files)`, `日本語 (ja): ... (22 HTML files)`.

## Next Phase Readiness

`28-VERIFICATION.md` now carries the live-run evidence plan 28-03's CHANGELOG `### Verified` section
is required (by D-11) to cite — the gate ran and passed *before* that section is written, satisfying
the wave-2-before-wave-3 ordering rationale in this plan's `<objective>`. SC#2 (the `[0.6.3]`
CHANGELOG entry itself) remains undone and is explicitly out of this plan's scope — that is plan
28-03's job. No blockers for wave 3.

---
*Phase: 28-v0-6-3-release-prep-regression-gate-close*
*Completed: 2026-07-25*
