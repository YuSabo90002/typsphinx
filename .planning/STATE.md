---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 04
current_phase_name: refresh-dev-tooling
status: executing
stopped_at: Completed 04-02-PLAN.md
last_updated: "2026-07-04T15:59:57.153Z"
last_activity: 2026-07-04
last_activity_desc: Completed 04-01-PLAN.md
progress:
  total_phases: 5
  completed_phases: 3
  total_plans: 11
  completed_plans: 9
  percent: 60
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-04)

**Core value:** Every CI job passes again on `main` — lint, the full test matrix, coverage, and the docs PDF build — with a dependency set that is pinned and reproducible so this rot doesn't silently recur.
**Current focus:** Phase 04 — refresh-dev-tooling

## Current Position

Phase: 04 (refresh-dev-tooling) — EXECUTING
Plan: 3 of 4
Status: Ready to execute
Last activity: 2026-07-04 — Completed 04-01-PLAN.md

Progress: [██████░░░░] 60%

## Performance Metrics

**Velocity:**

- Total plans completed: 7
- Average duration: - min
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01 | 2 | - | - |
| 02 | 3 | - | - |
| 03 | 2 | - | - |

**Recent Trend:**

- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
| Phase 02 P01 | 5min | 2 tasks | 1 files |
| Phase 02 P02 | 8min | 3 tasks | 1 files |
| Phase 02 P03 | 6min | 4 tasks | 2 files |
| Phase 03 P01 | 6min | 3 tasks | 6 files |
| Phase 04 P01 | 5min | 3 tasks | 3 files |
| Phase 04 P02 | 8min | 2 tasks | 3 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Pre-Phase 1]: Pin runtime deps to known-good rather than port forward to sphinx 9 / typst 0.15 — fastest, lowest-risk path to green CI in a maintenance cycle.
- [Pre-Phase 1]: Pin `typst` to a 0.14.x line compatible with the bundled `@preview` packages — the exact patch must be empirically confirmed during Phase 1 execution, not assumed.
- [Pre-Phase 1]: Modernize Python floor to 3.10–3.13 (drop EOL 3.9, add 3.13) as an atomic batch in Phase 3, sequenced after the pin fix is confirmed green.
- [Phase 02]: Scoped the @preview version-sync regex to actual #import statements only (not bare text matches) to avoid false-positive divergence from docstring examples — The naive regex matched a docstring example (charged-ieee) unrelated to the four essential imports
- [Phase 02]: Substituted tox -e cov (system Python) for tox -e py311 in the local pre-check — NixOS cannot execute tox-uv's downloaded standalone CPython 3.11 build; unrelated to the Phase 1 pin; GitHub Actions runners are unaffected
- [Phase 02]: Auto-fixed a black-formatting bug in Plan 01's sync-guard test (Rule 1) to unblock the Lint job, but left the pre-existing tox env-name mismatch (py3.10 vs py310, 9/12 matrix jobs) unpatched per D-04, surfacing it as a finding with a ready but unmerged fix on gsd/bugfix/github-ci-tox
- [Phase 02]: Applied the drafted tox-env matrix-mapping fix via git cherry-pick (64cd057) from gsd/bugfix/github-ci-tox rather than reimplementing by hand
- [Phase 02]: Left the CODECOV_TOKEN-absent codecov tokenless-upload failure unaddressed as pre-existing and out of scope (fail_ci_if_error: false keeps the job green)
- [Phase 03]: Ran plain uv lock (no --upgrade); verified the diff was only the <3.10 marker-branch collapse + incidental chardet drop, no unrelated version bumps
- [Phase 03]: black --check . confirmed a no-op both before and after the target-version bump to py310-py313 (D-03 does not trigger); no separate reformat commit needed
- [Phase 03-02]: Fixed both RED CI jobs in-batch on PR #104: ruff pyupgrade modernization (UP045/UP007/B905 strict=False/UP036) across translator.py/builder.py/pdf.py/template_engine.py/test_entry_points.py, and a tomllib->tomli backport in docs/source/conf.py + pyproject.toml docs group for the 3.10 docs floor — docs.yml setup-python floor drop (3.11->3.10) broke tomllib import; ruff target-version py39->py310 unlocked pyupgrade rules. Re-pushed to PR #104; ci.yml (18 jobs) and docs.yml both green on head caf779d. PR still open pending Task 3 human-verify.
- [Phase 04-01]: D-01/D-02/D-02b/D-07/D-08 applied verbatim in 04-01: floor+ceiling bounds for pytest/tox/tox-uv/black/ruff/mypy across pyproject.toml+tox.ini
- [Phase 04-01]: tox.ini [tox] requires uses tox-uv~=1.35 (not literal >=1.35,<2) -- tox ini-list loader splits single-entry requires values on comma, misparsing the ceiling; ~=1.35 is packaging-spec-equivalent and comma-free
- [Phase 04-02]: Bumped actions/upload-artifact@v5->v7 and actions/download-artifact@v6->v8 (node20->node24) uniformly across ci.yml/docs.yml/release.yml per D-03 amended; left the other four actions untouched — GitHub removes Node 20 from hosted runners 2026-09-16; runtime-verified via action.yml runs.using rather than trusting semver-major currency alone
- [Phase 04-02]: softprops/action-gh-release@v2 confirmed node20 via runtime check (RESEARCH A2 straggler); recorded as tracked/deferred TOOL-02 item (v3 exists and is node24) rather than fixed in-scope, since Task 1 only authorized upload-artifact/download-artifact edits — Plan Task 2 explicitly requires recording, not silently closing, any A2 straggler found to be node20

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 1]: The exact typst 0.14.x patch that satisfies all four bundled `@preview` packages (codly, codly-languages, mitex, gentle-clues) simultaneously is not yet empirically confirmed — this is Phase 1's core deliverable, not a research-time conclusion. If no single 0.14.x version satisfies all four, the documented fallback is pinning one `@preview` package to an older release instead of moving the typst pin.
- [Phase 1]: Whether the `sphinx<9` / `docutils<0.22` ceilings are load-bearing or purely precautionary is unconfirmed — resolve by testing whether `typst<0.15` alone is sufficient, and document the finding regardless (PIN-06).
- [Phase 3, 03-02]: CI on PR #104 (head ee2f9ae) is RED for the Python-floor bump -- ci.yml 'Lint and Format Check' fails with 25 new ruff errors (20 UP045, 2 UP036, 1 UP007, 2 B905) unlocked by the ruff target-version py39->py310 bump (real D-03 trigger); docs.yml 'build-docs' fails with ModuleNotFoundError: No module named 'tomllib' in docs/source/conf.py because docs.yml's setup-python was lowered 3.11->3.10 and tomllib is stdlib-only on 3.11+. REMEDIATED 2026-07-04: both fixed in-batch (commits f2465ff, caf779d), re-pushed, ci.yml (18 jobs) + docs.yml both green on head caf779d. Still do not merge PR #104 -- pending the Task 3 human-verify checkpoint.
- [Phase 04-02]: softprops/action-gh-release@v2 (docs.yml:67, release.yml:177/212) still declares runs.using: node20 -- ahead of GitHub's 2026-09-16 hosted-runner Node-20 removal. Out of 04-02's scope (Task 1 only authorized upload-artifact/download-artifact edits). Upstream @v3 is node24. Tracked/deferred candidate for Phase 5 (durability-guardrails) or a follow-up bump plan.

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| *(none)* | | | |

## Session Continuity

Last session: 2026-07-04T15:59:19.175Z
Stopped at: Completed 04-02-PLAN.md
Resume file: None
