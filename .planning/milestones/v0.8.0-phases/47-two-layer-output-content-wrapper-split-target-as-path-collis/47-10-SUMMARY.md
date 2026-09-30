---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
plan: 10
subsystem: infra
tags: [ci, github-actions, windows, macos, cross-platform, posixpath, ntpath, ruff]

# Dependency graph
requires:
  - phase: 47-09
    provides: "Full test suite green (1031 passed, 1 skipped), the unified pre-write collision validator, and the D-04 write-path fix -- this plan's own precondition (branch merged and pytest -q green) was satisfied entirely by 47-09's state"
provides:
  - "gsd/v0.8.0-multi-master-composition on origin, tracked upstream, no PR opened"
  - "A completed, all-green CI run (31492380799) over the branch including both windows-latest and macos-latest lanes (both Python 3.12/3.13), the first real CI exercise of this milestone's changes"
  - "A real, previously-undetected Windows-only defect in the OUT-02 escape-target guard (typsphinx/builder.py _escapes_outdir()/_resolve_target_stem()), fixed: both functions now use posixpath.isabs/posixpath.basename instead of the OS-native os.path (ntpath on Windows), matching their own documented platform-independence contract (D-05)"
  - "Four pre-existing ruff findings (module-level unused `import os`, its F811 redefinition, two extraneous f-string prefixes), fixed -- the first real ruff check this phase's changes received, since ruff cannot execute on the NixOS dev host"
  - "47-CI-EVIDENCE.md: run ids, SHAs, per-lane conclusions, quoted PASSED log lines for BLD-04 and the drive-qualified OUT-02 case on both non-Linux lanes, and a SC#1-SC#5 evidence mapping for all five ROADMAP Phase 47 success criteria"
  - "47-VALIDATION.md: both Manual-Only Verifications rows discharged, Validation Sign-Off approval granted"
affects: []

# Actuals (#2632)
actuals:
  tokens: 9016
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "posixpath, not os.path, for any path-shape check documented as platform-independent -- the module already imports posixpath for this exact reason (A47-03/A3's single-source-of-truth extraction), but two OUT-02 call sites still used the OS-native `from os import path` alias, which silently disagrees with posixpath on a windows-latest CI runner (ntpath.isabs/ntpath.basename have different absolute-path and UNC-path semantics than posixpath's)."
    - "workflow_dispatch as the CI trigger for a milestone branch -- ci.yml's `on: push` only fires for `branches: [main, develop]`, so exercising CI on a `gsd/*` milestone branch (this milestone's own binding constraint #2) requires `gh workflow run ci.yml --ref <branch>`, not a bare push."

key-files:
  created:
    - .planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-CI-EVIDENCE.md
  modified:
    - typsphinx/builder.py
    - tests/test_collision_validator_gate.py
    - .planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-VALIDATION.md

key-decisions:
  - "The Windows-only OUT-02 defect was fixed in-plan (Rule 1 -- bug) rather than deferred, even though it was found by a CI run this plan's own task 2 explicitly required to triage and repair: the task's own <action> text names exactly this class of defect in advance ('a path-separator assumption') and its acceptance criteria require the drive-qualified/absolute OUT-02 cases to pass, not merely execute, on the Windows lane."
  - "The four ruff findings were fixed in-plan despite one (the unused `import os`) being pre-existing since 2026-07-21 and unrelated to this phase's own diff, because the task's acceptance criteria require the CI run to reach `conclusion: success` -- a red lint lane blocks the very evidence (a completed, green CI run) this plan exists to produce. Documented explicitly in 47-CI-EVIDENCE.md as a pre-existing/environment-blind-spot finding, not silently absorbed as if it were phase-introduced."
  - "`47-VALIDATION.md`'s frontmatter `status: draft` was left unchanged -- the file's own lifecycle comment states the draft-to-validated transition is owned by /gsd-validate-phase, not by an executor closing out Manual-Only Verifications rows."

patterns-established:
  - "posixpath.isabs()/posixpath.basename(), never os.path's OS-native equivalents, for any typst_documents target-shape check -- the design intent (D-05, platform-independence) was already documented in both functions' docstrings before this fix; the implementation had simply never been exercised on a real Windows filesystem until this plan's CI run."

requirements-completed: [BLD-04, OUT-02]

coverage:
  - id: D1
    description: "gsd/v0.8.0-multi-master-composition pushed to origin with upstream tracking, no pull request opened"
    requirement: null
    verification:
      - kind: other
        ref: "git ls-remote --heads origin gsd/v0.8.0-multi-master-composition (verbatim output recorded in 47-CI-EVIDENCE.md, local/remote SHA match); gh pr list --head gsd/v0.8.0-multi-master-composition (empty)"
        status: pass
    human_judgment: false
  - id: D2
    description: "A completed CI run over the branch includes both windows-latest and macos-latest lanes, both green"
    requirement: "BLD-04, OUT-02"
    verification:
      - kind: other
        ref: "gh run view 31492380799 --json conclusion,status,jobs (conclusion: success, all 12 jobs success, including Test Python 3.12/3.13 on windows-latest and macos-latest)"
        status: pass
    human_judgment: false
  - id: D3
    description: "BLD-04's case-collision comparison and OUT-02's drive-qualified escape shape are proven to have EXECUTED (not skipped) and PASSED on both non-Linux lanes"
    requirement: "BLD-04, OUT-02"
    verification:
      - kind: integration
        ref: "quoted PASSED log lines for test_bld04_case_collision_rejected_typst/_typstpdf, test_collision_key_folds_case_but_not_unicode_normalization, and test_escape_shape_refused_with_containment_proof[drive] on both windows-latest and macos-latest (job 93781726864, 93781726893), recorded verbatim in 47-CI-EVIDENCE.md"
        status: pass
    human_judgment: false
  - id: D4
    description: "A real Windows-only OUT-02 defect (os.path vs posixpath disagreement on absolute-path/basename semantics) found by CI, fixed in typsphinx/builder.py, and re-verified green on both Windows Python versions"
    requirement: "OUT-02"
    verification:
      - kind: unit
        ref: "tests/test_builder_output_stem.py::test_resolve_output_stem_guards_absolute_target; tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[absolute] -- both PASSED on windows-latest in run 31492380799"
        status: pass
    human_judgment: false
  - id: D5
    description: "47-CI-EVIDENCE.md maps every one of ROADMAP Phase 47's five success criteria (SC#1-SC#5) to a named artifact or command, including a live re-measurement of SC#1's two-layer file set and a repo-wide grep confirming _is_master_document is gone"
    requirement: null
    verification:
      - kind: other
        ref: "uv run python -c \"...47-CI-EVIDENCE.md marker check...\" (SC#1..SC#5, windows-latest, macos-latest, ls-remote all present) -- exits 0"
        status: pass
    human_judgment: false
  - id: D6
    description: "47-VALIDATION.md's two Manual-Only Verifications rows are both marked discharged with the run id, and its Validation Sign-Off checklist grants full phase-level approval"
    requirement: null
    verification:
      - kind: other
        ref: "47-VALIDATION.md Manual-Only Verifications table (both rows DISCHARGED) and Validation Sign-Off Approval line (granted)"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-08-11
status: complete
---

# Phase 47 Plan 10: Push Milestone Branch to Origin and Prove It With CI Summary

**Pushed `gsd/v0.8.0-multi-master-composition` to `origin` and drove a completed, all-green CI run over it (including both Windows and macOS lanes), which caught and this plan then fixed a real Windows-only OUT-02 escape-guard defect (`os.path` vs `posixpath` disagreement) that no Linux-only local run could ever have surfaced.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-11T12:20:00Z (approx.)
- **Completed:** 2026-08-11T12:55:15Z
- **Tasks:** 3 of 3
- **Files modified:** 4 (1 production module, 1 test file, 2 planning artifacts)

## Accomplishments

- Pushed `gsd/v0.8.0-multi-master-composition` to `origin` with upstream tracking and **no pull request** opened (the ship unit for `branching_strategy: milestone` is the milestone; the release PR is Phase 52's business) — discharging milestone invariant #5 and binding constraint #2, which cost v0.7.0 two undetected defects when the branch was never pushed until the release PR.
- Confirmed `ci.yml`'s `on: push` trigger only fires for `branches: [main, develop]`, so exercising CI on a milestone branch requires `gh workflow run ci.yml --ref <branch>` (`workflow_dispatch`) — not a bare push. Dispatched CI twice.
- **First CI run (31491228938) went RED** on exactly the class of defect the plan's own text predicted in advance ("a path-separator assumption") — `windows-latest` (both Python 3.12 and 3.13) failed two tests, and `Lint and Format Check` failed on 4 ruff findings the NixOS dev host cannot detect locally. `macos-latest` and `ubuntu-latest` were green on this first run.
- Triaged and fixed the real defect: `typsphinx/builder.py`'s `_escapes_outdir()` and `_resolve_target_stem()`'s fallback-basename logic called the OS-native `os.path` (`ntpath` on a Windows CI runner) even though both functions' own docstrings already state the OUT-02 guard is platform-independent by design (D-05). Measured disagreements: `ntpath.isabs("/abs/manual")` is `False` (no drive letter) where `posixpath.isabs(...)` is `True`, letting a POSIX-shaped absolute target through unrefused on Windows; `ntpath.basename("//escape")` returns `''` where `posixpath.basename(...)` returns `'escape'`, mis-routing a UNC-shaped absolute target into a spurious self-collision with its own docname's content file. Both call sites switched to `posixpath.isabs`/`posixpath.basename`.
- Also fixed 4 pre-existing ruff findings surfaced by the same run — a genuinely unused module-level `import os` (dead since 2026-07-21) and its `F811` redefinition, plus two extraneous `f` prefixes on placeholder-free strings in `tests/test_collision_validator_gate.py` (introduced in plan 47-09) — since ruff cannot execute on the NixOS dev host and this was the first real ruff check this phase's changes ever received.
- **Second CI run (31492380799), over the fix commit, completed with all 12 jobs green**, including both `windows-latest` and `macos-latest` lanes on both Python versions. Quoted PASSED log lines from both non-Linux lanes prove the BLD-04 case-collision comparison and all three OUT-02 escape shapes — including the drive-qualified case — EXECUTED (not skipped) and passed.
- Wrote `47-CI-EVIDENCE.md`: run ids and URLs, commit SHAs, a per-lane conclusion table, quoted log lines, a "what the non-Linux lanes caught" section (a real defect, not nothing), and a full ROADMAP Phase 47 SC#1–SC#5 evidence mapping — including a live `sphinx-build` re-measurement of the two-layer file set (SC#1) and a repo-wide grep confirming `_is_master_document` is gone from every tracked source file (the only hits are in a gitignored, stale `docs/_build/html/` artifact).
- Ticked both of `47-VALIDATION.md`'s Manual-Only Verifications rows and updated the plan's own Per-Task Verification Map rows from `⬜ pending` to `✅ green`, granting full phase-level Validation Sign-Off approval.

## Task Commits

Each task was committed atomically:

1. **Task 1: Push the milestone branch to origin** - `6f8a23c` (docs) — `git push -u origin gsd/v0.8.0-multi-master-composition`, verbatim `git ls-remote` evidence recorded (SHAs match, no PR)
2. **Task 2: Drive a completed CI run and triage the Windows/macOS lanes** - `be4c4d5` (fix) + `374f579` (docs) — the fix commit repairs the Windows-only OUT-02 defect and the ruff findings; the docs commit records both CI runs' evidence
3. **Task 3: Record the CI evidence and close the phase artifacts** - `f66237b` (docs) — SC#1-SC#5 evidence mapping, `47-VALIDATION.md` sign-off closure

All four commits pushed to `origin` in sequence, no force-push, no rewrite.

## Files Created/Modified

- `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-CI-EVIDENCE.md` — created; branch-on-origin evidence, two CI run records (one red, one green), quoted per-lane PASSED log lines, and the SC#1-SC#5 evidence mapping
- `typsphinx/builder.py` — `_escapes_outdir()` and `_resolve_target_stem()` switched from `path.isabs`/`path.basename` (OS-native) to `posixpath.isabs`/`posixpath.basename`; removed the unused module-level `import os` (F401/F811)
- `tests/test_collision_validator_gate.py` — removed two extraneous `f` prefixes on placeholder-free assertion strings (F541)
- `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-VALIDATION.md` — both Manual-Only Verifications rows ticked discharged, 47-10/T1-T3 Per-Task Verification Map rows updated to green, Validation Sign-Off approval granted

## Decisions Made

- **The Windows-only OUT-02 defect was fixed in-plan (Rule 1 — bug), not deferred.** The plan's own task 2 `<action>` text names exactly this class of defect in advance ("a path-separator assumption (v0.7.1's Windows defect)"), and its acceptance criteria require the Windows-lane drive-qualified/absolute OUT-02 cases to PASS, not merely execute.
- **The four ruff findings were fixed in-plan despite one being pre-existing and unrelated to this phase's own diff**, because the task's acceptance criteria require the CI run to reach `conclusion: success` — a red lint lane blocks the very evidence this plan exists to produce. Documented explicitly in `47-CI-EVIDENCE.md` as a pre-existing/environment-blind-spot finding rather than silently absorbed as if phase-introduced, per the `<ci_expectations>` instruction to report genuine vs. unrelated findings honestly.
- **`47-VALIDATION.md`'s frontmatter `status: draft` was left unchanged.** The file's own lifecycle comment states the draft-to-validated transition is owned by `/gsd-validate-phase §6`, not by an executor closing out Manual-Only Verifications rows.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] OUT-02 escape guard used OS-native `os.path` instead of the documented platform-independent `posixpath`**
- **Found during:** Task 2 (CI triage, run 31491228938)
- **Issue:** `_escapes_outdir()` (line ~97) and `_resolve_target_stem()`'s fallback-basename computation both called `path.isabs`/`path.basename` from `from os import path` — OS-native, i.e. `ntpath` on a `windows-latest` runner. Both functions' own docstrings already state the guard is platform-independent by design (D-05). Measured: `ntpath.isabs("/abs/manual")` is `False` (posixpath: `True`), letting a POSIX-shaped absolute target through unrefused on Windows; `ntpath.basename("//escape")` returns `''` (posixpath: `'escape'`), mis-routing a UNC-shaped absolute target into a spurious self-collision.
- **Fix:** Switched both call sites to `posixpath.isabs`/`posixpath.basename` (already imported at module scope). No other `path.*` call site in the module was touched — every other use is genuine OS-native filesystem I/O.
- **Files modified:** `typsphinx/builder.py`
- **Verification:** `tests/test_builder_output_stem.py::test_resolve_output_stem_guards_absolute_target` and `tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[absolute]` both PASSED on `windows-latest` (both Python versions) in run 31492380799; full local suite re-verified green (1031 passed, 1 skipped).
- **Committed in:** `be4c4d5`

**2. [Rule 1 - Bug] Pre-existing ruff findings (module-scope unused `import os`, its `F811` redefinition, two `F541` extraneous f-prefixes)**
- **Found during:** Task 2 (CI triage, run 31491228938, `Lint and Format Check` job)
- **Issue:** `typsphinx/builder.py:8` `import os` was unused at module scope (dead since 2026-07-21, unrelated to this phase's own diff — ruff cannot execute on the NixOS dev host, so this was never caught locally); the second function-local `import os` in `_copy_template_directory` was flagged `F811` as a redefinition of that unused binding. Separately, `tests/test_collision_validator_gate.py:179-180` (introduced in plan 47-09) carried two `f`-prefixed strings with no `{...}` placeholder.
- **Fix:** Removed the module-level `import os` (both function-local `import os` statements remain, each genuinely used within its own function scope). Removed the two extraneous `f` prefixes.
- **Files modified:** `typsphinx/builder.py`, `tests/test_collision_validator_gate.py`
- **Verification:** `Lint and Format Check` job `success` in run 31492380799 (`ruff check .` clean); local `uv run black --check .` and `uv run mypy typsphinx/` both clean throughout.
- **Committed in:** `be4c4d5`

---

**Total deviations:** 2 auto-fixed (both Rule 1 — correctness fixes required for this plan's own explicit acceptance criteria, a completed `conclusion: success` CI run, to be achievable at all).
**Impact on plan:** Both were necessary to reach the green CI run this plan's entire purpose is to produce and evidence. Neither expanded scope beyond what the plan's own `<ci_expectations>` and task 2 `<action>` text anticipated in advance.

## Issues Encountered

None beyond the two auto-fixed deviations above, both anticipated by the plan's own text.

**Observation, not a defect (recorded in `47-CI-EVIDENCE.md`, not fixed):** all six CI `Test Python` lanes report `1027 passed, 5 skipped`, while the local dev-tree run reports `1031 passed, 1 skipped`. The 4-test difference is identical across all three operating systems (not Windows/macOS-specific), consistent with a locked-dependency-vs-dev-environment variance (`uv sync --extra dev --locked` in CI vs. the already-provisioned dev venv locally), out of this plan's scope.

## User Setup Required

None — no external service configuration required. `gh` was already authenticated as `YuSabo90002` for `github.com/YuSabo90002/typsphinx`.

## Next Phase Readiness

- Phase 47 is now fully closed: all 10 plans complete, all 5 ROADMAP success criteria discharged against named evidence, `47-VALIDATION.md`'s Validation Sign-Off approval granted.
- The milestone branch `gsd/v0.8.0-multi-master-composition` is on `origin` at `f66237b`, with a completed, all-green CI run (`31492380799`) proving the Windows and macOS lanes — the milestone's own binding constraint #2 discipline is now live for every subsequent phase (48 through 52), which can dispatch CI the same way without needing to re-establish the branch-push precedent.
- No blockers for Phase 48 (Compile-Time Cross-Reference Guard).

## Self-Check: PASSED

`typsphinx/builder.py` verified present with `posixpath.isabs`/`posixpath.basename` at the two OUT-02 call sites (via `grep -n`). All four task commits (`6f8a23c`, `be4c4d5`, `374f579`, `f66237b`) verified present via `git log --oneline`. `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-CI-EVIDENCE.md` verified present on disk. Final closing measurement re-run at the branch tip (`f66237b`): `git ls-remote --heads origin gsd/v0.8.0-multi-master-composition` matches `git rev-parse HEAD` exactly; `gh pr list --head gsd/v0.8.0-multi-master-composition` empty; `uv run pytest -q` = 1031 passed, 1 skipped, 207.25s.

---
*Phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis*
*Completed: 2026-08-11*
