---
phase: 66-github-dependabot-yml-pip-uv-ecosystem
plan: 04
subsystem: infra
tags: [dependabot, uv, github-actions, ci, dependency-management, github-api]

# Dependency graph
requires:
  - phase: 66-github-dependabot-yml-pip-uv-ecosystem
    provides: "66-03's UV_PR_CANDIDATES (138-142), UV_RUN_ID (34688990228), UPDATER_UV_IMAGE, D03_BRANCH, and the owner's Dependabot-tab read (OWNER_TAB_ANNOTATION / OWNER_TAB_CONFIG_ERROR)"
provides:
  - "SC1_PR (#138) and SC1_SHA — a real dependabot/uv/ PR whose own head commit lists both pyproject.toml and uv.lock"
  - "D-05 legs 1 and 2 closed: dependabot's deployed uv (0.12.7) versus documented (v0.11) versus CI's own uv (0.12.13); D05_LEG2 = PASS"
  - "D-06 observations against the pip-era baseline, all six rows verdicted; Requirement closure table with DEP-01/DEP-03/DEP-04 MET"
affects: [67, 68]

# Actuals (#2632)
actuals:
  tokens: 7357
  tasks: 3
  commits: 3
  plan_head_before: 0796a4b72ad837a2a94e1ec36c93d059f95e070f

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Reading a bot-authored PR's head commit via git fetch origin refs/pull/<n>/head + git show --name-only, never gh pr checkout — same-commit content proof without moving HEAD"
    - "uv lock --check on a git archive export in a scratch tmpdir, run from the worktree's own cwd so the uv shim resolves correctly, as a zero-side-effect lock-compatibility probe"

key-files:
  created: []
  modified:
    - .planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-DEPENDABOT-EVIDENCE.md

key-decisions:
  - "SC1_PR = #138 (ruff bump) selected as the sole BOTH-class dependabot/uv/ PR; the other four open uv PRs (#139-142) are LOCK-ONLY and feed the D-06 lockfile-only-volume observation instead."
  - "D-06's grouping and exclusions rows verdicted unobserved-documented-support rather than behaves-as-before, because the sphinx-typst-stack group's docutils member failed dependency resolution and no dependabot/uv/ group PR ever opened to observe directly."

requirements-completed: [DEP-01, DEP-03, DEP-04]

coverage:
  - id: D1
    description: "SC#1 same-commit clause: every open dependabot/uv/ PR classified BOTH/LOCK-ONLY/OTHER from its own head commit; SC1_PR (#138) is on a dependabot/uv/ branch, authored by dependabot, based on main, head commit lists both pyproject.toml and uv.lock"
    requirement: DEP-01
    verification:
      - kind: other
        ref: "git/gh assertions in 66-DEPENDABOT-EVIDENCE.md § Same-commit classification, § SC#1 selection (D-04)"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-05 legs 1 and 2: documented (v0.11) vs dependabot-core main (0.12.7) vs deployed image (0.12.7) vs CI's own uv (0.12.13); lock header, local uv lock --check, and CI's Install dependencies step all confirm compatibility"
    requirement: DEP-04
    verification:
      - kind: other
        ref: "git/gh assertions in 66-DEPENDABOT-EVIDENCE.md § D-05 leg 1 documented and source uv versions, § D-05 leg 2 lock header, § D-05 leg 2 local lock check, § D-05 leg 2 CI uv on the PR head, § DEP-04 comparison"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-06 observations against the pip-era baseline (grouping, exclusions, labels, PR limit, lockfile-only volume, ruff range), all six verdicted; Requirement closure table reads MET for DEP-01, DEP-03, DEP-04"
    requirement: DEP-03
    verification:
      - kind: other
        ref: "gh/git assertions in 66-DEPENDABOT-EVIDENCE.md § D-06 observations against the pip-era baseline, § Requirement closure"
        status: pass
    human_judgment: false

duration: 15min
completed: 2026-09-12
status: complete
---

# Phase 66 Plan 04: SC#1 Same-Commit Read, D-05 Legs 1–2, D-06, Requirement Closure Summary

**`SC1_PR = 138`, `SC1_SHA = 88088071e02a7411800f504e06b1ded9d6891cc7` (dependabot/uv/ruff-0.16.6, the only BOTH-class PR among five open dependabot/uv/ PRs); `D05_LEG2 = PASS` — dependabot's deployed uv (`DEPENDABOT_UV_MAIN`/`DEPENDABOT_UV_DEPLOYED` both `0.12.7`) diverges from the documented `v0.11` (`DOCS_UV_ROW`) but matches CI's own uv (`CI_UV_VERSION = 0.12.13`, `LOCAL_UV = 0.12.13`), and the lock header (`version = 1` / `revision = 3`) and a local `uv lock --check` both held clean; D-06 recorded six verdicts (three `behaves-as-before`, two `unobserved-documented-support`, one `divergence-recorded`); `DEP-01`, `DEP-03` and `DEP-04` all closed `MET`.**

## Performance

- **Duration:** 15 min
- **Tasks:** 3 (tracer, auto, auto)
- **Files modified:** 1 (`66-DEPENDABOT-EVIDENCE.md`)

## Accomplishments

- **Task 1 (tracer)** re-asserted the wave-3 gate (all five 66-03 keys present, no `## HALT` heading in either evidence file), then re-listed dependabot PRs — no `dependabot/uv/` PR is new since 66-03. For each of the five open `dependabot/uv/` PRs (#138–#142), fetched the head via `git fetch origin refs/pull/<n>/head` (asserting `FETCH_HEAD == headRefOid`) and read `git show --name-only` on the head commit: #138 (`ruff`) is **BOTH** (`pyproject.toml` + `uv.lock`); #139 (`tox`), #140 (`sphinx-intl`), #141 (`pre-commit`), #142 (`mypy`) are all **LOCK-ONLY**. `SC1_PR = 138`, `SC1_SHA = 88088071e02a7411800f504e06b1ded9d6891cc7` — on branch `dependabot/uv/ruff-0.16.6`, authored by `app/dependabot`, based on `main`, one commit. The `pyproject.toml` hunk quoted (`ruff>=0.15,<0.16` → `ruff>=0.15,<0.17`) feeds D-06's range-behaviour row. Tracer `<verify>` (automated-only, `human_verify_mode: end-of-phase`) was re-run and passed, so execution proceeded directly to Task 2 without a synthesized checkpoint.
- **Task 2** closed D-05's two legs. **Leg 1:** GitHub's own docs (`dependabot-options-reference.md:618`, `supported-package-managers.md:59,61`) still read `DOCS_UV_ROW = v0.11`, but dependabot-core's `main` branch (`uv/Dockerfile:15`, `uv/helpers/requirements.txt:10`) and the exact deployed image tag from 66-03's `UPDATER_UV_IMAGE` (`ebbc4f6a…`, confirmed to resolve as a real dependabot-core commit) both pin `uv==0.12.7` (`DEPENDABOT_UV_MAIN = DEPENDABOT_UV_DEPLOYED = 0.12.7`) — a stale-documentation finding, `REQUIREMENTS.md` left literal. **Leg 2:** `SC1_SHA`'s and `MERGE_SHA`'s `uv.lock` both read `version = 1` / `revision = 3`; a `git archive` export of `SC1_SHA` into a scratch tmpdir passed `uv lock --check --directory` with `exit:0` under `LOCAL_UV = 0.12.13`; and `SC1_PR`'s own CI run (`SC1_RUN_ID = 34689041575`, `conclusion: success`) logged `Successfully installed uv version 0.12.13` (`CI_UV_VERSION`) in its `Install uv` step, with `Install dependencies` (`uv sync --extra dev --locked`) concluding `success`. All three legs held: `D05_LEG2 = PASS`. The `DEP-04 comparison` table compares all six version/lock keys by string equality only (the precision edge) and notes the ROADMAP's stale `0.11.25` local-uv figure is superseded by the measured `LOCAL_UV = 0.12.13`. No workflow was created or edited; no dependabot head was checked out.
- **Task 3** recorded D-06 against the pip-era baseline. No `dependabot/uv/sphinx-typst-stack-*` PR ever opened (the group's `docutils` member hit `dependency_file_not_resolvable`, per 66-03), so grouping and exclusions both verdict **unobserved-documented-support** (the docs' `patterns`/`exclude-patterns` carry no per-ecosystem restriction, unlike `dependency-type`). Labels: all five `uv` PRs carry `labels: []`, matching #123/#128's pip-era empty array — **behaves-as-before**. `open-pull-requests-limit`: exactly 5 open `dependabot/uv/` PRs, at the configured limit; the run log's own "limit" grep hit is unrelated `docutils`-hint prose, not a PR-count message (the real PR-limit error is UI-only, per 66-03's `OWNER_TAB_ANNOTATION`) — **behaves-as-before**. Lockfile-only volume: 4 of 5 `uv` PRs (#139–#142) touch only `uv.lock`, a class that did not exist under `pip` — **divergence-recorded** by construction. `ruff` range: PR #138 widens `<0.16` → `<0.17`, identical to #123's pip-era widening, confirming dependabot-core #15693's expectation — **behaves-as-before**. The `## Requirement closure` table reads `DEP-01`, `DEP-03` and `DEP-04` all `MET`, naming their deciding sections; `DEP-02` and `DEP-05` are named as Phase 67's, whose SC#2 inputs (`66-MAIN-PR-EVIDENCE.md` § D-02 pre-merge snapshot, this file's § D-02 post-merge snapshot and § uv pull requests) are pointed to without re-judging them. Nothing was fixed: no `versioning-strategy` key, no label created, no `.github/dependabot.yml` edit.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — wave-3 gate, classify every dependabot/uv/ PR by its own head commit, select SC#1** - `afaa070d` (docs)
2. **Task 2: D-05 legs 1 and 2 — documented vs source vs deployed uv, lock header, local lock check, CI's own uv sync --locked** - `0557bda2` (docs)
3. **Task 3: D-06 observations against the pip-era baseline, requirement closure for DEP-01/DEP-03/DEP-04** - `f41391b3` (docs)

**Plan metadata:** committed separately after this SUMMARY (worktree mode — STATE.md/ROADMAP.md excluded, orchestrator owns those).

## Files Created/Modified

- `.planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-DEPENDABOT-EVIDENCE.md` - extended with `## Wave-3 gate`, `## Same-commit classification`, `## SC#1 selection (D-04)`, `## D-05 leg 1 documented and source uv versions`, `## D-05 leg 2 lock header`, `## D-05 leg 2 local lock check`, `## D-05 leg 2 CI uv on the PR head`, `## DEP-04 comparison`, `## D-06 observations against the pip-era baseline`, `## Requirement closure`

## Decisions Made

- `SC1_PR = #138` selected as the lowest-numbered (and only) BOTH-class `dependabot/uv/` PR among the five 66-03 candidates; the other four are recorded as LOCK-ONLY and feed the D-06 lockfile-only-volume divergence rather than closing SC#1 themselves.
- Grouping and exclusions verdicted `unobserved-documented-support` rather than `behaves-as-before`, since the `sphinx-typst-stack` group PR never opened under `uv` (blocked by the `docutils` resolution conflict already recorded in 66-03) — the documented mechanism is intact but unproven by a live PR this run.

## Deviations from Plan

None - plan executed exactly as written, including the AMENDED 2026-09-12 acceptance-key substitutions (`UV_RUN_ACCEPTED = yes`, `OWNER_TAB_CONFIG_ERROR = none`) that were already present in the plan text and in 66-03's prior evidence — this plan only read those keys, it did not need to apply any new amendment.

## Issues Encountered

None. `SC1_PR`'s CI run (`SC1_RUN_ID = 34689041575`) was already `completed`/`success` at the first `gh run list` query, so no `gh run watch` foreground wait was needed for Task 2's leg 2(c).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `DEP-01`, `DEP-03` and `DEP-04` are closed `MET` in `66-DEPENDABOT-EVIDENCE.md`'s `## Requirement closure` table. Phase 66 (all four plans) is ready for phase-level verification.
- Phase 67 (`DEP-02`, `DEP-05`) has its inputs ready: `66-MAIN-PR-EVIDENCE.md` § D-02 pre-merge snapshot, this file's § D-02 post-merge snapshot and § uv pull requests, plus the `docutils`/`sphinx-typst-stack` resolution conflict recorded in 66-03 as input for #128's disposal, and the deferred correction that #128 is itself a grouped bump (66-CONTEXT.md `<deferred>`), carried to Phase 67 discuss.
- No blockers. `.github/dependabot.yml`, every workflow file, and the repository's label list are unchanged by this plan — only the evidence file was written. No dependabot PR (`uv` or `pip`) was merged, approved, closed, commented on, rebased or sent an `@dependabot` command.

## Self-Check: PASSED

- `.planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-DEPENDABOT-EVIDENCE.md` exists: FOUND
- Commit `afaa070d` (Task 1 evidence) found in `git log --oneline --all`: FOUND
- Commit `0557bda2` (Task 2 evidence) found in `git log --oneline --all`: FOUND
- Commit `f41391b3` (Task 3 evidence) found in `git log --oneline --all`: FOUND
- Task 1's `<verify>` automated block re-run individually: PASSED (`SC1_PR=138 SC1_SHA=88088071e02a7411800f504e06b1ded9d6891cc7`)
- Task 2's `<verify>` automated block re-run individually: PASSED
- Task 3's `<verify>` automated block re-run individually: PASSED
- Plan-level `<verification>` re-confirmed: SC#1 read from a real head commit (both files listed); D-05 leg 1 recorded from docs/source/deployed tag; D-05 leg 2 `PASS` on lock header, local check, CI's `uv sync --locked`; D-06 carries six verdicts; closure table `MET` for DEP-01/DEP-03/DEP-04
- `git status --short` clean after all three commits; no unexpected deletions (`git diff --diff-filter=D`) — PASSED

---
*Phase: 66-github-dependabot-yml-pip-uv-ecosystem*
*Completed: 2026-09-12*
