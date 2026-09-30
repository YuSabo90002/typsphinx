---
phase: 23-v0-6-2-release-prep-regression-gate-close
plan: 02
subsystem: infra
tags: [release-prep, regression-gate, pytest, corpus-gate, milestone-invariant]

# Dependency graph
requires:
  - phase: 23-01
    provides: pyproject.toml/uv.lock/README.md bumped to 0.6.2; tests/test_readme_version_sync.py green
provides:
  - "23-VERIFICATION.md — evidence record: SC#3 corpus-gate raw log (genuine 1 passed, not skipped, empty unknown_visit catalogue), SC#4 milestone-invariant diffs, SC#5 scope-fence assertions"
  - "Durable verbatim gate-log copy in this SUMMARY (survives /gsd-verify-work overwriting 23-VERIFICATION.md)"
affects: [23-03-changelog, gsd-complete-milestone, gsd-verify-work]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Evidence-only VERIFICATION.md frontmatter (record_type: execution-evidence, status: evidence-only) to distinguish a raw-evidence record from /gsd-verify-work's own verdict report that later overwrites the same filename."

key-files:
  created: [.planning/phases/23-v0-6-2-release-prep-regression-gate-close/23-VERIFICATION.md]
  modified: []

key-decisions:
  - "Ran the corpus gate twice: once exactly as the plan's literal command (no -s), and once with -s added, because pytest suppresses a passing test's print() output by default and the plan requires the printed 'Unknown Visit Catalogue:' line as evidence. No code was added to tests/test_corpus_gate.py in either case — both are read-only invocations of the existing test with different capture flags."
  - "Interpreted 'no @preview bump / 3-way surface untouched' per 23-RESEARCH.md's cited reading: isolate lines containing '@preview' in the git diff against v0.6.1, not require the three files to be byte-identical (writer.py legitimately changed in Phase 22.1 without being flagged as an SC#4 violation)."
  - "Did not create a separate 23-GATE.md report file, per D-10 — all evidence aggregated into 23-VERIFICATION.md."

requirements-completed: []  # Phase 23 plan 23-02 has requirements: [] per its own frontmatter (release/close phase)

coverage:
  - id: D1
    description: "Full-corpus typstpdf regression gate ran to completion and demonstrably PASSED (not skipped): 1 passed, zero SKIPPED lines, empty unknown_visit catalogue, plausible real-build elapsed time"
    verification:
      - kind: integration
        ref: "tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v"
        status: pass
    human_judgment: false
  - id: D2
    description: "SC#4 milestone invariant confirmed: zero new runtime dependencies since v0.6.1, no @preview version bump across the 3-way declaration surface, tests/test_preview_version_sync.py green"
    verification:
      - kind: other
        ref: "git diff v0.6.1..HEAD -- pyproject.toml (dependencies array unchanged)"
        status: pass
      - kind: unit
        ref: "tests/test_preview_version_sync.py -v (2 passed)"
        status: pass
    human_judgment: false
  - id: D3
    description: "SC#5 scope fence held: no v0.6.2 tag, no release.yml interaction since v0.6.1, no publish/release commands run"
    verification:
      - kind: other
        ref: "git tag --list 'v0.6.2' (empty); git diff v0.6.1..HEAD -- .github/workflows/release.yml (empty)"
        status: pass
    human_judgment: false

# Metrics
duration: ~10min
completed: 2026-07-23
status: complete
---

# Phase 23 Plan 02: Corpus-Gate + Milestone-Invariant Evidence Summary

**Ran the existing full-corpus `typstpdf` regression gate against the cached Sphinx v9.1.0 `doc/` corpus,
proved it genuinely PASSED (not skipped, `1 passed`, empty `unknown_visit` catalogue), and confirmed the
SC#4 milestone invariant (zero new runtime deps, no `@preview` bump) plus the SC#5 scope fence (no
`v0.6.2` tag, `release.yml` untouched) — all recorded as raw evidence in `23-VERIFICATION.md`.**

## Performance

- **Duration:** ~10 min
- **Tasks:** 2 completed
- **Files modified:** 1 (`23-VERIFICATION.md` — new file; zero source/test code touched)

## Accomplishments

- Provisioned the worktree's own venv (`uv sync --extra dev`) before running anything, per CLAUDE.md's
  worktree-isolated-execution convention — confirmed `typsphinx==0.6.2` installed editable from this
  worktree checkout.
- Ran `tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow
  -rs -v` against the cached corpus at `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc` (cache hit, no
  network clone needed) — genuine `1 passed in 14.10s`, zero `SKIPPED` lines.
- Re-ran the identical node id with `-s` added (no test code changed) to surface the test's own
  `print()` output, confirming `Unknown Visit Catalogue: []` — an empty, clean catalogue.
- Confirmed SC#4: `git diff v0.6.1..HEAD -- pyproject.toml`'s `dependencies` array is byte-identical to
  `v0.6.1` (only the version literal and two ruff-ignore comment edits changed); `@preview` diff across
  `writer.py`/`template_engine.py`/`templates/base.typ` is empty; `tests/test_preview_version_sync.py`
  passes (2 passed); `uv sync --extra dev --locked` exits 0; `tests/test_readme_version_sync.py` passes.
- Confirmed SC#5: `git tag --list 'v0.6.2'` is empty; `git diff v0.6.1..HEAD --
  .github/workflows/release.yml` is empty; no release-workflow commit landed since `v0.6.1`.
- Wrote all raw command output to `.planning/phases/23-v0-6-2-release-prep-regression-gate-close/23-VERIFICATION.md`
  with `status: evidence-only` frontmatter (not a verdict — `/gsd-verify-work` owns and will regenerate
  this filename with its own report later).

## Task Commits

Each task was committed atomically:

1. **Task 1: Run the full-corpus regression gate and prove it passed rather than skipped** - no
   repository file was modified by this task (produces a captured log consumed by Task 2, per the
   plan's own task spec); no standalone commit exists for it.
2. **Task 2: Confirm the SC#4 milestone invariant and SC#5 scope fence, and write the evidence record** -
   `14d6286` (docs)

**Plan metadata:** this SUMMARY commit itself is the plan-metadata commit (worktree mode — STATE.md/
ROADMAP.md are excluded and owned by the orchestrator).

## Files Created/Modified

- `.planning/phases/23-v0-6-2-release-prep-regression-gate-close/23-VERIFICATION.md` - new evidence
  record: corpus-gate raw log (SC#3), milestone-invariant diffs (SC#4), scope-fence assertions (SC#5),
  and a lifecycle note explaining this file will be overwritten by `/gsd-verify-work`.

## Decisions Made

- Ran the corpus gate with two invocations: the plan's exact literal command (`-rs -v`, no `-s`) to match
  the plan text verbatim, plus a second run with `-s` appended to surface the suppressed `print()` output
  containing the `Unknown Visit Catalogue:` line — both invocations are read-only test runs, zero code
  added to `tests/test_corpus_gate.py` in either case (confirmed via `git status --porcelain
  tests/test_corpus_gate.py` returning empty after both runs).
- Followed 23-RESEARCH.md's cited interpretation of "3-way `@preview` surface untouched": isolated
  `@preview`-containing diff lines rather than requiring the three files to be byte-identical, since
  `writer.py` legitimately changed in Phase 22.1 without being treated as an SC#4 violation.
- No `23-GATE.md` file created — all evidence aggregated into `23-VERIFICATION.md` per D-10.

## Deviations from Plan

None - plan executed exactly as written. The two-invocation corpus-gate run (base command + `-s` variant)
is not a deviation from plan intent — it is exactly what the plan's own Task 1 action text asks for
("Also capture, for the SUMMARY, the printed `Unknown Visit Catalogue:` line from the gate's stdout"),
and pytest's default output-capturing behavior on a passing test required the second invocation to
surface that line without modifying any test code.

## Issues Encountered

None. The cached corpus was present and offline-usable exactly as `23-RESEARCH.md` predicted; no network
clone was needed, and no environmental blocker was hit.

## Corpus-Gate Evidence (SC#3) — Verbatim Log (durable copy)

The following is the exact same verbatim output recorded in `23-VERIFICATION.md`'s "Corpus Gate Raw
Evidence" section, duplicated here as the non-clobberable durable record (per the plan's `<output>`
requirement and D-10's Threat T-23-09 mitigation).

```
$ uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ad2162bc5de5320d3/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ad2162bc5de5320d3
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 1 item

tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED [100%]

============================== 1 passed in 14.10s ==============================
```

```
$ uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v -s
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ad2162bc5de5320d3/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ad2162bc5de5320d3
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 1 item

tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error Corpus tag: v9.1.0
Corpus commit SHA: cc7c6f435ad37bb12264f8118c8461b230e6830c
Unknown Visit Catalogue: []
PASSED

============================== 1 passed in 12.90s ==============================
```

**Facts this log proves:** genuine `1 passed` (not `1 skipped`) in both runs; zero `SKIPPED` lines
anywhere; elapsed time (14.10s / 12.90s) is well inside the plausible 10-25s real-build range, not a
sub-second skip; `Unknown Visit Catalogue: []` is empty — no node type was silently dropped;
`tests/test_corpus_gate.py` was not modified (`git status --porcelain` returns empty for that file).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- SC#3 satisfied and evidenced: the full corpus rebuild is fatal-free with a valid `%PDF` and a clean
  `unknown_visit` catalogue, proven passed rather than skipped (D-12).
- SC#4 satisfied and evidenced: zero new runtime dependencies, no `@preview` bump, 3-way sync surface in
  lockstep — all confirmed against the `v0.6.1` git tag.
- SC#5 asserted negatively: no tag, no publish, no Release, no `release.yml` interaction — confirmed
  since `v0.6.1`.
- Plan 23-03 (the `[0.6.2]` CHANGELOG entry, including its `### Verified` section) can now cite the exact
  three facts this gate asserts (fatal-free compilation, valid `%PDF` magic bytes, empty `unknown_visit`
  catalogue) per D-11 — no document-length figure was derived or is available from this run to forward.
- `23-VERIFICATION.md` exists with `status: evidence-only` frontmatter; `/gsd-verify-work` will later
  overwrite this same filename with its own verdict — this SUMMARY's verbatim log copy is the durable
  record per D-10/T-23-09.

## Self-Check: PASSED

- FOUND: `.planning/phases/23-v0-6-2-release-prep-regression-gate-close/23-VERIFICATION.md`
- FOUND: `.planning/phases/23-v0-6-2-release-prep-regression-gate-close/23-02-SUMMARY.md`
- FOUND commit: `14d6286` (Task 2)
- No `.gate-run.log` scratch file left in the working tree (logs captured to the session scratchpad
  directory, outside the repository)
- `git tag --list 'v0.6.2'` empty (verified again after all commits)

---
*Phase: 23-v0-6-2-release-prep-regression-gate-close*
*Completed: 2026-07-23*
