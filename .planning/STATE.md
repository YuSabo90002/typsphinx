---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
current_phase: 05
status: complete
stopped_at: Phase 5 verified (4/4 must-haves) & complete — milestone v1.0 complete (5/5 phases)
last_updated: "2026-07-05T05:47:03.232Z"
last_activity: 2026-07-05
last_activity_desc: Phase 05 complete
progress:
  total_phases: 5
  completed_phases: 5
  total_plans: 15
  completed_plans: 15
  percent: 100
current_phase_name: durability-guardrails
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-05)

**Core value:** Every CI job passes again on `main` — lint, the full test matrix, coverage, and the docs PDF build — with a dependency set that is pinned and reproducible so this rot doesn't silently recur.
**Current focus:** Milestone v1.0 complete — all 5 phases done; guarded, green, modernized CI on `main`

## Current Position

Phase: 05 — durability-guardrails (final phase)
Plan: 4/4 complete
Status: Milestone v1.0 complete — Phase 5 verified (VERIFICATION.md: passed, 4/4 must-haves); PR #106 merged to main
Last activity: 2026-07-05 — Phase 05 verified & complete; milestone v1.0 complete

Progress: [██████████] 100%

## Performance Metrics

**Velocity:**

- Total plans completed: 15
- Average duration: - min
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01 | 2 | - | - |
| 02 | 3 | - | - |
| 03 | 2 | - | - |
| 04 | 4 | - | - |
| 05 | 4 | - | - |

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
| Phase 04 P03 | 6min | 2 tasks | 2 files |
| Phase 04 P04 | 40min | 3 tasks | 0 files |
| Phase 05 P01 | 12min | 2 tasks | 3 files |
| Phase 05 P02 | 3min | 2 tasks | 2 files |
| Phase 05 P03 | 3min | 1 tasks | 1 files |
| Phase 05 P04 | 20min | 3 tasks | 0 files |

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
- [Phase 04-03]: Reused Phase 3/04-01's nix run nixpkgs#ruff local-execution workaround to verify the comment-only pyproject.toml edit was inert (NixOS cannot execute the uv-installed ruff binary directly)
- [Phase ?]: [Phase 04-04]: Opened NEW PR #105 to main (base=main, head d99748d) via gh pr create rather than reopening closed PR #104 (owner decision); titled to reflect the full Phases 2-4 green-baseline integration
- [Phase ?]: [Phase 04-04]: push->observe gate green — ci.yml run 28711976093 success (18 jobs, full 3.10-3.13 x 3-OS matrix + lint/type/coverage/build/integration) + docs.yml run 28711976097 success (incl. PDF step); developer approved the blocking human-verify gate
- [Phase ?]: [Phase 04-04]: Repaired main branch protection via gh api PATCH — removed stale required check 'Test Python 3.9 on ubuntu-latest' (Phase-3 leftover, root cause of PR #105 being un-mergeable despite all jobs green) and added 'Test Python 3.13 on ubuntu-latest'; PR #105 now MERGEABLE/CLEAN. Repo-settings change not a git commit
- [Phase ?]: Isolated Task 1 and Task 2 commits by temporarily reverting the softprops @v3 edit before committing Task 1, then reapplying it for Task 2 -- both tasks touch docs.yml/release.yml so this kept commits atomic per-task.
- [Phase ?]: [Phase 05-02] Used prefix-anchored globs sphinx*/docutils*/typst* with exclude-patterns for sphinx-autodoc-typehints/sphinx-intl (D-08 scoping); CI badge placed first in README badge row (D-09).
- [Phase ?]: [Phase 05-03] Implemented drift.yml exactly per RESEARCH.md Pattern 2 skeleton and PATTERNS.md's synthesized version -- no deviation from the plan's specified step order, permissions, or tox env selection.
- [Phase 05-04]: PR #106 merged to main; ci.yml (19 jobs) + docs.yml both green, empirically confirming DUR-01/03/04 and D-11 syntactic validity
- [Phase 05-04]: drift.yml validated post-merge via workflow_dispatch (run 28730876125, SUCCESS, no forward drift detected, no issue filed) -- confirms DUR-02 end-to-end
- [Phase 05-04]: D-11 (softprops/action-gh-release@v3 tag-gated runtime confirmation) deferred to the next real release tag with explicit developer sign-off, rather than smoke-tested via manual release.yml dispatch

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 1]: The exact typst 0.14.x patch that satisfies all four bundled `@preview` packages (codly, codly-languages, mitex, gentle-clues) simultaneously is not yet empirically confirmed — this is Phase 1's core deliverable, not a research-time conclusion. If no single 0.14.x version satisfies all four, the documented fallback is pinning one `@preview` package to an older release instead of moving the typst pin.
- [Phase 1]: Whether the `sphinx<9` / `docutils<0.22` ceilings are load-bearing or purely precautionary is unconfirmed — resolve by testing whether `typst<0.15` alone is sufficient, and document the finding regardless (PIN-06).
- [Phase 3, 03-02]: CI on PR #104 (head ee2f9ae) is RED for the Python-floor bump -- ci.yml 'Lint and Format Check' fails with 25 new ruff errors (20 UP045, 2 UP036, 1 UP007, 2 B905) unlocked by the ruff target-version py39->py310 bump (real D-03 trigger); docs.yml 'build-docs' fails with ModuleNotFoundError: No module named 'tomllib' in docs/source/conf.py because docs.yml's setup-python was lowered 3.11->3.10 and tomllib is stdlib-only on 3.11+. REMEDIATED 2026-07-04: both fixed in-batch (commits f2465ff, caf779d), re-pushed, ci.yml (18 jobs) + docs.yml both green on head caf779d. Still do not merge PR #104 -- pending the Task 3 human-verify checkpoint.
- [Phase 04-02]: softprops/action-gh-release@v2 (docs.yml:67, release.yml:177/212) still declares runs.using: node20 -- ahead of GitHub's 2026-09-16 hosted-runner Node-20 removal. Out of 04-02's scope (Task 1 only authorized upload-artifact/download-artifact edits). Upstream @v3 is node24. Tracked/deferred candidate for Phase 5 (durability-guardrails) or a follow-up bump plan.
- [Phase 04-04]: PR #105 (base=main, head d99748d) is MERGEABLE/CLEAN with ci.yml(18 jobs)+docs.yml green, but intentionally NOT merged — merge is a separate owner action. After merge owner closes dependabot #96/#97 (duplicate the 04-02 artifact bumps). Node-20 straggler softprops/action-gh-release@v2 carried to Phase 5 (@v3 is node24).

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| *(none)* | | | |

## Session Continuity

Last session: 2026-07-05T05:41:02.202Z
Stopped at: Completed 05-04-PLAN.md (Phase 5 complete, all 4/4 plans)
Resume file: None
