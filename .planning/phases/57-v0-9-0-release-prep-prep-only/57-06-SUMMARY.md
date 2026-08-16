---
phase: 57-v0-9-0-release-prep-prep-only
plan: 06
subsystem: release-prep
tags: [pytest, black, ruff, mypy, tox, sphinx, typst-py, uv-build, corpus-gate, wheel-inspection]

# Dependency graph
requires:
  - phase: 57-01
    provides: "the version bump to 0.9.0 (pyproject.toml, README.md, uv.lock)"
  - phase: 57-03
    provides: "the curated ## [0.9.0] CHANGELOG section"
  - phase: 57-04
    provides: "the migration guide and D-10 documentation verification"
provides:
  - "SC#3's local half: full pytest suite (1421 passed, 1 skipped, 0 failed, 0 errors) on the post-bump tree"
  - "black/ruff/mypy transcripts, with a local NixOS ruff-binary mitigation recorded"
  - "both docs-html (3 warnings) and docs-pdf (5 warnings) build transcripts, matched exactly against the Phase 56 baseline"
  - "the full-corpus gate's outcome recorded as PASSED (not conflated with the file's unrelated env-gated skip)"
  - "a local built-wheel content check confirming typsphinx/templates/README.md and base.typ are packed"
affects: [57-07, 57-08, 57-09]

# Actuals (#2632)
actuals:
  tokens: 3164
  tasks: 3
  commits: 1

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Local NixOS ruff mitigation: symlink the main checkout's already-patched .venv/bin/ruff over a fresh worktree venv's broken generic-linux ELF, rather than skipping the lint transcript."
    - "Full-corpus gate outcome recorded as an unambiguous 'Outcome: PASSED' / 'Outcome: SKIPPED — <reason>' line, distinguishing the render gate's own result from an unrelated env-gated skip in the same test file."

key-files:
  created:
    - .planning/phases/57-v0-9-0-release-prep-prep-only/57-GREEN-TREE-EVIDENCE.md
  modified: []

key-decisions:
  - "ruff's exit-127 NixOS stub-loader rejection on the fresh worktree venv was mitigated by symlinking the main checkout's already-patched ruff binary (a .venv/bin substitution, not a tracked-file edit), per the standing project mitigation — rather than reporting lint as unrun."
  - "test_corpus_gate.py's PASSED render-gate result and its one unrelated SKIPPED (env-gated, opt-in TYPSPHINX_CORPUS_REPORT=1) test were kept explicitly separate in the evidence file so neither is mistaken for the other."

patterns-established: []

requirements-completed: []  # REL-08 closes at /gsd-complete-milestone, not in this plan — this plan does not flip any requirement checkbox.

coverage:
  - id: D1
    description: "Full local pytest suite proven green on the post-bump tree (1421 passed, 1 skipped, failures=0, errors=0), with the imported typsphinx package proven to resolve inside this worktree."
    requirement: "REL-08"
    verification:
      - kind: other
        ref: "uv run pytest -v --junit-xml=.../57-06-suite.xml -- testsuite errors=\"0\" failures=\"0\""
        status: pass
    human_judgment: false
  - id: D2
    description: "black --check, ruff check, and mypy all run and recorded on the post-bump tree; ruff's local availability re-measured today rather than assumed."
    requirement: "REL-08"
    verification:
      - kind: other
        ref: "uv run black --check . ; uv run ruff check . ; uv run mypy typsphinx/ -- all exit 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both docs-html and docs-pdf tox environments build successfully with warning counts (3 and 5) matched exactly against the Phase 56 close's recorded baseline — no new warning introduced."
    requirement: "REL-08"
    verification:
      - kind: other
        ref: "uv run tox -e docs-html ; uv run tox -e docs-pdf -- both 'build succeeded'"
        status: pass
    human_judgment: false
  - id: D4
    description: "The full-corpus gate's outcome is recorded honestly as PASSED, distinct from the file's one unrelated env-gated skip, supporting the release section's full-corpus ### Verified claim."
    requirement: "REL-08"
    verification:
      - kind: other
        ref: "uv run pytest tests/test_corpus_gate.py -v -- TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED"
        status: pass
    human_judgment: false
  - id: D5
    description: "A locally built wheel (uv build) is inspected via zipfile namelist and proven to carry typsphinx/templates/README.md and base.typ — the local copy of SC#3's built-wheel content check."
    requirement: "REL-08"
    verification:
      - kind: other
        ref: "uv build ; zipfile namelist inspection of dist/typsphinx-0.9.0-py3-none-any.whl"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-08-17
status: complete
---

# Phase 57 Plan 06: Local Green-Tree Evidence Summary

**The post-bump v0.9.0 tree proven green locally on the full suite, black/ruff/mypy, both docs builds, and a local wheel-content check — with the full-corpus gate's PASSED outcome kept explicit and un-conflated with an unrelated skip, and lint/type/matrix authority left to the dispatched CI run under D-13.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-08-16T16:35:22Z
- **Completed:** 2026-08-16T16:41:10Z (writing/verification continued after)
- **Tasks:** 3
- **Files modified:** 1 (created)

## Accomplishments

- Provisioned this worktree's own `.venv` (`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs`) and confirmed `import typsphinx` resolves inside this worktree at version `0.9.0`, not the main checkout.
- Ran the full local pytest suite: **1421 passed, 1 skipped, 0 failed, 0 errors** (JUnit `testsuite` `tests="1422" failures="0" errors="0" skipped="1"`), matching the orchestrator's independently-measured baseline exactly.
- Ran `black --check .` (clean), `ruff check .` (clean, after a local NixOS-mitigation symlink swap — see Deviations), and `mypy typsphinx/` (clean) — all three transcripts captured with exit codes.
- Built both `tox -e docs-html` (3 warnings) and `tox -e docs-pdf` (5 warnings) — both counts matched exactly against the Phase 56 close's recorded baseline, so no new warning was introduced by this phase's CHANGELOG or migration-guide prose.
- Ran `tests/test_corpus_gate.py` and recorded the full-corpus render gate's outcome as `Outcome: PASSED`, explicitly distinguishing it from the file's one unrelated `SKIPPED` test (`test_empty_url_before_after`, gated on an opt-in env var unrelated to corpus availability).
- Built a wheel with `uv build` and inspected its zipfile namelist inline, confirming `typsphinx/templates/README.md` and `typsphinx/templates/base.typ` are both packed — the local copy of SC#3's built-wheel content check.
- Wrote `57-GREEN-TREE-EVIDENCE.md` with all eight required headings and the explicit `Outcome: PASSED` / `A pytest.skip is not evidence.` markers, then re-ran every `<verify>` grep against the written file before committing.

## Task Commits

Each task in this plan runs and records without editing any tracked source, test, or documentation file — Tasks 1 and 2 produced no diff to commit on their own; the single evidence-file write (Task 3) is the one commit for the whole plan:

1. **Tasks 1–3 combined (run, record, write evidence)** - `1e9d90e0` (docs) — `docs(57-06): record local green-tree evidence for SC#3's local half`

No separate plan-metadata commit was made beyond this one, per the worktree parallel-execution instructions (the orchestrator owns STATE.md/ROADMAP.md).

## Files Created/Modified

- `.planning/phases/57-v0-9-0-release-prep-prep-only/57-GREEN-TREE-EVIDENCE.md` - the local-half evidence record for SC#3 (full suite, format/lint/type trio, both docs builds, the corpus gate's honest outcome, and the local wheel-content check).

## Decisions Made

- **[Rule 3 - Blocking] Mitigated the NixOS ruff stub-loader rejection by symlinking the main checkout's already-patched `ruff` binary over the fresh worktree venv's broken copy**, rather than reporting local lint as unrun. This is a `.venv/bin` binary substitution only (`.venv/` is gitignored, outside every `<verify>`'s `git diff` check) — no tracked file was touched. `ruff` DOES run on this machine when a working binary is available; the exit-127 seen first is a fresh-venv provisioning artifact specific to a newly-created `.venv`, not a statement that local ruff is unavailable in general. Recorded honestly with both transcripts (the failing first attempt and the passing result after the swap) in the evidence file.
- Kept the corpus gate's `PASSED` render-gate result and its one unrelated env-gated `SKIPPED` test explicitly separate in the evidence file's prose, per the plan's threat register (T-57-31) — a `pytest.skip` on a different test in the same file must never be read as weakening the render gate's own proven result.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] NixOS ruff stub-loader rejection on the fresh worktree venv**
- **Found during:** Task 1 (format/lint/type trio)
- **Issue:** `uv run ruff check .` exited 127 with `Could not start dynamically linked executable: ruff` / `NixOS cannot run dynamically linked executables intended for generic linux environments out of the box.` — the freshly-synced worktree `.venv/bin/ruff` is a generic-linux ELF the NixOS stub loader rejects.
- **Fix:** Symlinked the main checkout's already-patched `ruff` binary (`/home/yuta/Documents/typsphinx/.venv/bin/ruff`, verified separately to run `ruff 0.15.20` exit 0) over the worktree's broken copy: `rm .venv/bin/ruff && ln -s /home/yuta/Documents/typsphinx/.venv/bin/ruff .venv/bin/ruff`. Re-ran `uv run ruff check .` — `All checks passed!`, exit 0.
- **Files modified:** none tracked — `.venv/bin/ruff` only, which is gitignored.
- **Verification:** `uv run ruff check .` exits 0 with `All checks passed!` after the swap; `git status --porcelain` and `git diff --name-only` both confirm no tracked file changed.
- **Committed in:** not applicable (no tracked-file change to commit for this fix; recorded as prose in `57-GREEN-TREE-EVIDENCE.md`'s "SC#3 — format, lint and type" section instead).

---

**Total deviations:** 1 auto-fixed (1 blocking, environmental — no code or test file touched)
**Impact on plan:** The mitigation restored an accurate `ruff check .` transcript instead of leaving lint unrun or asserting unavailability from a stale premise; no scope creep, no source/test/doc file modified.

## Issues Encountered

None beyond the ruff mitigation documented above. The full suite, both docs builds, the corpus gate, and the wheel inspection all ran cleanly on the first attempt.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- SC#3's local half is fully discharged and on disk at `57-GREEN-TREE-EVIDENCE.md`, ready for `57-08`'s SC#4 sweep and `57-09`'s handoff to cite.
- The full-corpus gate's `PASSED` outcome directly supports the release section's full-corpus `### Verified` claim without qualification — no "not locally re-proven this phase" caveat is needed.
- Both documentation build warning counts (3 / 5) are unchanged from the Phase 56 baseline, so no new documentation regression needs tracking into the next wave.
- No blockers. `git status --porcelain` is clean after the commit; `git tag -l v0.9.0` and remote tag checks were not re-run here (out of this plan's scope) but nothing in this plan took any irreversible action.

---
*Phase: 57-v0-9-0-release-prep-prep-only*
*Completed: 2026-08-17*
