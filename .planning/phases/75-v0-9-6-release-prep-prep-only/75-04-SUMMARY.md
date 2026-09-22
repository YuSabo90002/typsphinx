---
phase: 75-v0-9-6-release-prep-prep-only
plan: 04
subsystem: infra
tags: [pytest, ruff, black, mypy, sphinx, linkcheck, tox, release-prep]

# Dependency graph
requires:
  - phase: 75-01
    provides: the clean C-locale docs-html/docs-pdf warning ledger and message-class census taken at the phase base
  - phase: 75-03
    provides: the bump commit (pyproject.toml/uv.lock/README.md 0.9.2 -> 0.9.6) and the curated CHANGELOG.md ## [0.9.6] section
provides:
  - measured SC4-local-half evidence on the bumped tip (lint trio, both full pytest runs, both documentation builds) — all green
  - SC4_LOCAL_VERDICT = MET, after the owner's 2026-09-20 amendment classified the three remaining linkcheck records (see 75-GREEN-TREE-EVIDENCE.md § "AMENDED 2026-09-20")
  - a carried obligation for 75-07: 75-HANDOFF.md must require a post-tag linkcheck re-run, which is what closes the two Class A records
affects: [75-06, 75-07]

actuals:
  tokens: 15000
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - .planning/phases/75-v0-9-6-release-prep-prep-only/75-GREEN-TREE-EVIDENCE.md

key-decisions:
  - "None taken by this plan — a NOT-MET verdict was recorded verbatim per the plan's own explicit protocol, and escalated via checkpoint rather than worked around."
  - "Resolved by the project owner on 2026-09-20, after the plan returned: SC4's linkcheck condition reads `working` plus the classified, controlled exceptions equals `total`. Recorded as an AMENDED addendum in 75-GREEN-TREE-EVIDENCE.md; the original NOT-MET reading is preserved verbatim there. No product file was edited and no linkcheck_ignore key was added."
  - "Class A (the two v0.9.6 tag links, 404 only because the tag is created at /gsd-complete-milestone) is a carried obligation, not a waiver: 75-07 must write the post-tag linkcheck re-run into 75-HANDOFF.md."
  - "Class B (PyPI #history) was re-measured by the orchestrator and is NOT a broken link: the page returns 200 with a 3038-byte `Client Challenge` bot-mitigation body containing no anchors, identical under a browser User-Agent. Filed as a pending todo (linkcheck_anchors_ignore candidate) rather than fixed, per the prep-only fence."

requirements-completed: []

coverage:
  - id: D1
    description: "Lint trio (ruff, black, mypy) and full pytest suite (twice, once under LC_ALL=C) all green on the bumped tip, zero changelog-page-gate skips, @preview invariant intact"
    requirement: "REL-15"
    verification:
      - kind: other
        ref: "uv run ruff check . / uv run black --check . / uv run mypy typsphinx/ / uv run pytest -rs -p no:cacheprovider (twice)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Clean C-locale docs-html and docs-pdf builds, warning counts not risen above the 75-01 baseline, both Phase 74 message classes re-proved at zero with a positive control"
    requirement: "REL-15"
    verification:
      - kind: other
        ref: "uv run tox -e docs-html / uv run tox -e docs-pdf, from a removed docs/_build under LANG=C LANGUAGE=C LC_ALL=C"
        status: pass
    human_judgment: false
  - id: D3
    description: "tox -e linkcheck clean, unsoftened run with working count equal to total"
    requirement: "REL-15"
    verification:
      - kind: other
        ref: "uv run tox -e linkcheck (3 identical attempts, all exit 1; 96 total, 93 working)"
        status: pass
    human_judgment: true
    rationale: "Escalated by this plan as NOT-MET and resolved by the project owner on 2026-09-20 under an amended reading of SC4: `working` plus the classified, controlled exceptions equals `total`. Class A is the two v0.9.6 tag links, which a prep-only phase cannot make green because the tag is created afterwards at /gsd-complete-milestone; control `releases/tag/v0.9.2` returns 200, and a post-tag re-run is carried into 75-HANDOFF.md. Class B is the PyPI #history anchor, re-measured as a bot-mitigation interstitial rather than a broken link, and filed as a pending todo. No product file was edited; docs/source/conf.py still holds zero linkcheck keys."

# Metrics
duration: 13min
completed: 2026-09-20
status: complete
halt_resolved: 2026-09-20
halt_resolution: "Owner amended SC4's linkcheck condition; see 75-GREEN-TREE-EVIDENCE.md § \"AMENDED 2026-09-20\". The plan itself is unchanged and made no product edit."
---

# Phase 75 Plan 04: Green Tree Evidence (SC4 Local Half) — HALTED on a discovered linkcheck defect

**Lint trio, both full pytest runs (plain + `LC_ALL=C`), and both C-locale documentation builds are
all green on the bumped v0.9.6 tip — but `tox -e linkcheck` fails identically across all three
allowed attempts, so `SC4_LOCAL_VERDICT = NOT-MET` and this plan halts per its own explicit
escalation protocol rather than push a false-green result forward to 75-06.**

## Performance

- **Duration:** 13 min
- **Started:** 2026-09-20T08:59:51Z
- **Completed:** 2026-09-20T09:12:48Z
- **Tasks:** 3 (all three ran to completion; the plan's own verdict is NOT-MET)
- **Files modified:** 1 (`75-GREEN-TREE-EVIDENCE.md`, three commits)

## Accomplishments

- Re-provisioned this worktree with `--extra dev --extra docs`; `uv sync --locked` exits 0, so the
  lock is in sync with `pyproject.toml` on this tip.
- Task 1 (tracer): `uv run ruff check .`, `uv run black --check .` and `uv run mypy typsphinx/` all
  exit 0; the full pytest suite passes twice (1569 passed, 1 skipped — an unrelated env-gated
  test, `tests/test_corpus_gate.py:530` — both times), with `CHANGELOG_GATE_SKIPS = 0`; the
  `@preview` invariant (4 packages, sync surfaces untouched since the milestone base) holds.
  Tracer feedback gate re-verified end-to-end and auto-continued (interactive, `end-of-phase`,
  `<verify>` carried only `<automated>` — no checkpoint synthesized per the #3299 precedence
  chain).
- Task 2: `uv run tox -e docs-html` and `uv run tox -e docs-pdf` both build clean (`build
  succeeded.`, 0 warnings) from a removed `docs/_build` under `LANG=C LANGUAGE=C LC_ALL=C`,
  matching (not exceeding) `75-BASE-EVIDENCE.md`'s baseline. Both Phase 74 message classes
  (`unknown node type: <doctest_block...>` and the attributed docstring reST errors) read 0 on
  this tree, falsified against a synthetic positive control (>=1 hit each pattern) and the quoted
  Phase 74 pre-fix count (2).
- Task 3: `tox -e linkcheck` ran three times from a removed `docs/_build`, each attempt failing
  identically (exit 1, the same 3 broken records out of 96 total, 93 working) — this is not
  transient network flakiness (which would vary run to run), so per the plan's own protocol the
  result is recorded verbatim, `TIP_LINKCHECK_VERDICT = FAIL`, and `SC4_LOCAL_VERDICT = NOT-MET`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — lint trio + full pytest twice** - `7f2b6511` (docs)
2. **Task 2: Clean C-locale docs-html/docs-pdf, warning ledger, message-class census** - `972a6c4d` (docs)
3. **Task 3: Linkcheck (3 attempts) and SC4 local verdict** - `cd1bb571` (docs)

_Note: This is a measurement-only plan (`type: execute`, `autonomous: true`); every commit is
`docs(75-04): ...` because the plan is prohibited from editing any product file — only
`75-GREEN-TREE-EVIDENCE.md` was created/modified._

## Files Created/Modified

- `.planning/phases/75-v0-9-6-release-prep-prep-only/75-GREEN-TREE-EVIDENCE.md` — the full SC4
  local-half evidence: head check, wave-1 gate, lint trio, both pytest runs, `@preview` invariant,
  both docs builds, warning ledger, message-class census + positive controls, docs invariants,
  and the three linkcheck attempts with `SC4_LOCAL_VERDICT = NOT-MET`.

## Decisions Made

None taken unilaterally by this plan. The linkcheck failure is recorded verbatim and escalated
per the plan's own written protocol ("a red gate is recorded verbatim with a NOT-MET verdict and
escalated"); no product file was edited, no `linkcheck_ignore`/`linkcheck_anchors_ignore`/
`linkcheck_allowed_redirects` key was added, and `docs/source/conf.py` is confirmed unchanged.

## Deviations from Plan

None — plan executed exactly as written, including its own designed escalation path for a
genuinely failing gate. No Rule 1/2/3 auto-fix was applicable or attempted: the three broken
links are outside this plan's edit scope (`CHANGELOG.md` and the PyPI-hosted page are both
off-limits or off-repo), and the plan's own text explicitly forbids editing any product file to
turn this red gate green.

## Issues Encountered — THE BLOCKING FINDING

**`tox -e linkcheck` fails identically on 3/3 attempts, all from a removed `docs/_build`, no
softening key present in `docs/source/conf.py`. `docs/_build/linkcheck/output.json`: 96 total, 93
`working`, 3 `broken`:**

| # | File:line | URI | Cause (measured, not guessed) |
|---|---|---|---|
| 1 | `changelog.rst:8` | `https://github.com/YuSabo90002/typsphinx/compare/v0.9.6...HEAD` | 404 — the `v0.9.6` tag does not exist yet. Phase 75 is prep-only; the tag is created at `/gsd-complete-milestone`, after this phase. |
| 2 | `changelog.rst:17` | `https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.6` | 404 — same root cause as #1. Both links were introduced by 75-03's curated `## [0.9.6]` CHANGELOG commit (`84edd348`) as an unavoidable consequence of that heading and tail link existing before the tag does. |
| 3 | `changelog.rst:474` | `https://pypi.org/project/typsphinx/#history` | Anchor not found on PyPI's live page. **Pre-existing** — measured present and byte-identical at both `BASE_75_04` (`44d22075`) and the milestone base (`6cc44f22`) via `git show <sha>:docs/source/changelog.rst`. Not caused by any task in this plan. Notably: v0.9.5's Phase 73 `73-GREEN-TREE-EVIDENCE.md` (2026-09-16, four days before this run) recorded `tox -e linkcheck` passing 95/95 with zero broken rows — this same anchor was apparently still resolving on PyPI's side then, so the break looks like an external site change on PyPI's end between 2026-09-16 and 2026-09-20, not something this repository controls. |

**Why this is a genuine architectural/process gap, not a fixable bug within this plan's scope:**
This is the first time in the project's history that a release-prep phase both (a) has
`tox -e linkcheck` as a gate (added v0.9.5 Phase 72, first exercised pre-publish in v0.9.5 Phase
73 — which was a merge-only milestone with no version bump, so no `## [0.9.6]`-shaped heading or
tag-referencing tail link was ever added to `CHANGELOG.md` that milestone) and (b) actually bumps
the version and curates a new `## [X.Y.Z]` CHANGELOG heading with GitHub tag/compare links in the
same milestone (v0.9.6 is the first "publishing" milestone since v0.9.2, per PROJECT.md/STATE.md).
The two features individually pre-date this phase, but this is the first time they combine: a
curated CHANGELOG's own newly-added tail links reference a release tag that structurally cannot
exist until *after* this prep-only phase completes and the milestone is actually tagged at
`/gsd-complete-milestone`. Running an unsoftened `linkcheck` against that CHANGELOG before the tag
exists will deterministically fail on those two links every time, regardless of retry count.

**Options for the human decision this checkpoint requests** (not adopted by this plan; no product
file was edited):
1. Accept that `TIP_LINKCHECK_VERDICT = FAIL` here is an expected, structural consequence of
   running `linkcheck` before this milestone's tag exists, and have 75-06 (or a future plan)
   proceed on a documented, narrower reading of SC4 that excludes the two tag-referencing links
   until after publish — this would need explicit sign-off since the plan's own text says 75-06
   "reads this key before it pushes anything" and currently reads `NOT-MET`.
2. Investigate whether the PyPI `#history` anchor break (item #3) is worth a separate, out-of-plan
   fix to `docs/source/changelog.rst` (a real content/link edit, Rule 4-territory — new for this
   milestone since the anchor was resolving as recently as 2026-09-16).
3. Re-run `tox -e linkcheck` again at a later point in this phase (e.g. in 75-07, after wave 3/4)
   to see if PyPI's anchor issue is itself transient at a longer timescale than the 3-attempt
   bounded retry this plan used.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

**Not ready for 75-06 as written.** `75-06-PLAN.md` is expected to read `SC4_LOCAL_VERDICT` from
this evidence file before pushing and dispatching CI; it currently reads `NOT-MET`. A human
decision is needed on how to proceed (see the three options above) before 75-06 can run as
designed. Tasks 1 and 2's gates (lint trio, both pytest runs, both documentation builds) are fully
green and need no rework — only Task 3's linkcheck verdict blocks forward progress.

---
*Phase: 75-v0-9-6-release-prep-prep-only*
*Plan: 04*
*Completed: 2026-09-20*

## Self-Check: PASSED

- `75-GREEN-TREE-EVIDENCE.md` present on disk: confirmed.
- All three task commits (`7f2b6511`, `972a6c4d`, `cd1bb571`) present in `git log --oneline
  --all`: confirmed.
- `plan_head_before: 44d22075a77f5b425062b51329b6de1c3b27adbc`; `commits: 3`
  (`git rev-list --count 44d22075..HEAD`), matching the three task commits exactly — no
  uncommitted product changes.
