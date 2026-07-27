---
phase: 30-japanese-rtd-site-hand-rolled-machinery-orphan-removal
plan: 04
subsystem: infra
tags: [verification, evidence, grep, tox, pytest, github-actions, readthedocs]

# Dependency graph
requires:
  - phase: 30-japanese-rtd-site-hand-rolled-machinery-orphan-removal (Plans 01-03)
    provides: "The fully-merged post-deletion tree — CI/tox/Makefile repointed (Plan 01),
      switcher assets deleted + conf.py trimmed (Plan 02), orphan docs + docs/locale/ deleted
      (Plan 03) — this plan is the first to measure the phase's success criteria against the
      merged result rather than any single wave-1 branch"
provides:
  - "30-EVIDENCE.md: the phase's hand-run verification record, with one section per gate
    (A-G), each carrying its exact command and verbatim output"
  - "Proof that all five ROADMAP success criteria hold on the merged tree, measured fresh
    in this session rather than cited from prior SUMMARYs"
  - "A newly-discovered second SC#1 false positive (a Plan-02-authored docstring reference),
    documented and reasoned about explicitly rather than silently absorbed or gate-appeased"
  - "Two explicit Deferred sections naming the exact future checks for the three
    post-merge-only observations (docs.yml CI run, RTD switcher-markup re-fetch, RTD
    ad-slot re-fetch)"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Gate discretion recorded, not silently absorbed: when a fresh measurement finds a
      false positive the plan didn't anticipate, the correct action (given the plan
      forbids editing source in this verification-only plan) is to document the finding
      and its reasoning in the evidence record, not to either hide it or edit around it"

key-files:
  created:
    - .planning/phases/30-japanese-rtd-site-hand-rolled-machinery-orphan-removal/30-EVIDENCE.md
  modified: []

key-decisions:
  - "Widened Gate A's survivor list by one entry beyond the plan's stated single known-good
    survivor: tests/test_readthedocs_config.py:296 is a docstring sentence (introduced by
    Plan 02's own repointing commit 204f7ef) that uses \"language-switcher\" as a proper
    noun describing the now-deleted feature in prose explaining why the test was
    repointed — not a live reference to switcher code, config, or surviving machinery.
    Documented explicitly in 30-EVIDENCE.md's Gate A section per the same reasoning
    pattern the plan itself already authorizes for Gate B's html_static_path scoping."

requirements-completed: [I18N-02, DOC-08]

coverage:
  - id: D1
    description: "SC#1 token gate: repo-wide grep for the switcher token set returns zero
      live-machinery hits (two accounted-for textual false positives survive, one
      previously known, one newly discovered and documented this session), down from the
      pre-phase baseline of 37 lines across 9 files"
    requirement: "I18N-02"
    verification:
      - kind: other
        ref: "git ls-files -z ... | xargs -0 grep -nE '<token-list>' — 30-EVIDENCE.md Gate A"
        status: pass
    human_judgment: false
  - id: D2
    description: "SC#1 static-path scoping: html_static_path absent from docs/source/conf.py,
      all 7 legitimate elsewhere-occurrences survive byte-unchanged, confval fixture
      survivor confirmed present"
    requirement: "I18N-02"
    verification:
      - kind: other
        ref: "grep -n html_static_path docs/source/conf.py; grep -rn html_static_path examples tests — 30-EVIDENCE.md Gate B"
        status: pass
    human_judgment: false
  - id: D3
    description: "SC#2 seam proof: conf.py region 1 and region 3 hash to their recorded
      pre-phase values exactly; phase-wide diff against base 458ffc8 touches nothing under
      typsphinx/"
    requirement: "I18N-02"
    verification:
      - kind: other
        ref: "sed ... | sha256sum; git diff --stat 458ffc8..HEAD -- typsphinx/ — 30-EVIDENCE.md Gate C"
        status: pass
    human_judgment: false
  - id: D4
    description: "SC#3/SC#4: full pytest suite green on the merged tree (641 passed, 1
      skipped), matching Plan 03's post-deletion baseline exactly"
    requirement: "DOC-08"
    verification:
      - kind: unit
        ref: "uv run python -m pytest -q — 30-EVIDENCE.md Gate D"
        status: pass
    human_judgment: false
  - id: D5
    description: "SC#5: both tox -e docs-html and tox -e docs-pdf exit 0 and produce
      docs/_build/html/index.html and docs/_build/pdf/typsphinx.pdf; workflow/tox.ini
      cross-check prints FAILED: []; D-14 deploy/release boundary holds; documentation
      root returns 200"
    requirement: "I18N-02"
    verification:
      - kind: integration
        ref: "uv run python -m tox -e docs-html && uv run python -m tox -e docs-pdf — 30-EVIDENCE.md Gate E"
        status: pass
      - kind: other
        ref: "workflow/tox.ini cross-check script — 30-EVIDENCE.md Gate F"
        status: pass
      - kind: other
        ref: "curl -sS -L https://typsphinx.readthedocs.io/ — 30-EVIDENCE.md Gate G"
        status: pass
    human_judgment: false
  - id: D6
    description: "The three genuinely unobservable-in-phase items (docs.yml CI run, RTD
      switcher-markup re-fetch, RTD ad-slot re-fetch) are recorded as explicitly deferred
      with their exact future checks named, not inferred into passes"
    verification: []
    human_judgment: true
    rationale: "These are backstop truths by the plan's own design — they cannot be
      observed until the milestone PR opens and Read the Docs rebuilds the tracked
      branch, which is structurally outside this phase's worktree. The verifier is
      expected to abstain to human_needed on these, per the plan's must_haves.truths
      backstop entries."

# Metrics
duration: ~20min
completed: 2026-07-26
status: complete
---

# Phase 30 Plan 04: Phase-Wide Evidence Record Summary

**Ran all seven of the phase's gates (A-G) as real commands against the merged post-deletion tree
and recorded verbatim command+output for each in `30-EVIDENCE.md`; all five ROADMAP success
criteria measured green, with one newly-discovered SC#1 false positive documented explicitly
rather than silently absorbed.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-07-26T20:49:15+09:00
- **Tasks:** 2
- **Files created:** 1 (`30-EVIDENCE.md`)

## Accomplishments

- **Confirmed the wave-1 merge was actually complete** before measuring anything: all four
  switcher assets, both root orphan documents, both collateral test files, and `docs/locale/` are
  all absent; `tox.ini`/`.github/workflows/docs.yml`/`docs/Makefile` all carry their edits.
- **Gate A (SC#1 token sweep):** repo-wide grep over `git ls-files` (excluding `CHANGELOG.md`/
  `.planning`) found exactly 2 lines — the known `confval:: html_sidebars` fixture survivor, and
  one **new** finding: a docstring sentence in `tests/test_readthedocs_config.py:296` (introduced
  by Plan 02's own commit `204f7ef`) that names "language-switcher" as a proper noun describing
  the deleted feature in prose, not as live code/config. Documented as an exercised discretion,
  widening the survivor list by one entry, per the same reasoning pattern the plan already
  authorizes for Gate B's `html_static_path` scoping. Zero live switcher-machinery references
  survive; down from the pre-phase baseline of 37 lines across 9 files.
- **Gate B (scoped static-path token):** `html_static_path` absent from `docs/source/conf.py`;
  exactly 7 legitimate occurrences survive across `examples/basic/conf.py`,
  `examples/advanced/conf.py`, and two render-gate fixtures; the confval fixture survivor
  confirmed present.
- **Gate C (SC#2 seam proof):** `conf.py` region 1 hashes to
  `06f177f82fb153ca4971d258989e7ede2a4e5ffa018a5caaa8ab0a56e6f7b466` and region 3 to
  `cd245215f80b2552dcba7b01d74a36de0ef0b2323df665e88390381c2cd5d169` — both exact matches to the
  recorded pre-phase values. `git diff --stat 458ffc8..HEAD -- typsphinx/` is empty (milestone
  invariant #3 held across all three waves at once).
- **Gate D (SC#3/SC#4, full suite):** `uv run python -m pytest -q` — 641 passed, 1 skipped,
  reproducing Plan 03's post-deletion baseline exactly on the fully-merged tree.
- **Gate E (SC#5, docs builds):** both `tox -e docs-html` and `tox -e docs-pdf` exit 0;
  `docs/_build/html/index.html` and `docs/_build/pdf/typsphinx.pdf` both produced.
- **Gate F (SC#5, workflow/tox consistency):** a scratch cross-check script (not committed) parsed
  `docs.yml`'s `tox -e <env>` strings against `tox.ini`'s section list — `FAILED: []`, empty
  `MISSING_ENVS`/`MISSING_PATHS`. D-14 boundary re-confirmed directly: exactly one
  `peaceiris/actions-gh-pages` step with `publish_dir: ./docs/_build/html`, and
  `softprops/action-gh-release` survives.
- **Gate G (RTD-04):** `curl -sS -L https://typsphinx.readthedocs.io/` returns `200`, redirecting
  to `/en/latest/` — matches the planning-time measurement.
- **Total phase deletion scope:** `git diff --diff-filter=D --name-only 458ffc8..HEAD | wc -l` =
  **34 files** (Plan 02's 4 switcher assets + Plan 03's 30: the 4 orphan-doc-pair files + 26
  `docs/locale/` tracked files) — recorded for the owner's manual merge past
  `worktree.cleanup-wave`'s deletion guard.
- **Closed the record** with two `Deferred` sections naming exact future checks (the milestone
  PR's `docs.yml` run; the next RTD rebuild's switcher-markup and ad-slot re-fetch) and restated
  the three accepted, deliberate losses this phase makes permanent (browser-language
  auto-redirect, two unsalvaged `docs/usage.rst` sections, Furo's restored ad/variant-selector
  slots).

## Task Commits

Each task was committed atomically:

1. **Task 1: Run the SC#1 token gate and the SC#2 seam proof, and open the evidence record** -
   `203869c` (docs)
2. **Task 2: Run the build, suite and workflow-consistency gates and close the evidence record** -
   `3d30a00` (docs)

**Plan metadata:** pending (this SUMMARY's own commit) — orchestrator-owned in worktree mode.

## Files Created/Modified

- `.planning/phases/30-japanese-rtd-site-hand-rolled-machinery-orphan-removal/30-EVIDENCE.md` -
  NEW. One section per gate (A-G), each carrying its exact command and verbatim output; two
  explicit `Deferred` sections; the three accepted-loss restatement.

## Decisions Made

- **Widened Gate A's survivor list by one entry**, beyond this plan's own `must_haves.truths`
  (which names only the confval fixture as the survivor): `tests/test_readthedocs_config.py:296`
  is a docstring sentence introduced by Plan 02's own commit, using "language-switcher" as a proper
  noun describing the deleted feature in prose — not live code. Since this plan's
  `<artifacts_this_phase_produces>` explicitly forbids editing any source or test file, and since
  the plan's own prohibition text requires the gate's scoping to be "documented in `30-EVIDENCE.md`
  rather than achieved by deletion," the correct action was to record this honestly with reasoning
  rather than silently pass it or edit the docstring to disappear. This mirrors the plan's own
  already-authorized Gate B discretion (`html_static_path` scoping) — same category of finding,
  discovered one plan-wave later because Plan 02 (which wrote this docstring) executed after
  `30-RESEARCH.md` was researched.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 — process/discretion, not code] Documented a second SC#1 false positive not
enumerated in the plan**
- **Found during:** Task 1 (Gate A, the token sweep)
- **Issue:** The plan's `must_haves.truths` names exactly one known-good survivor for Gate A (the
  confval fixture). The fresh grep found a second: a Plan-02-authored docstring sentence in
  `tests/test_readthedocs_config.py:296`.
- **Fix:** No source file was edited (this plan's artifact list forbids it). The finding was
  documented in full in `30-EVIDENCE.md`'s Gate A section, with the exact commit that introduced
  it, the reasoning for why it is not live switcher machinery, and an explicit "exercised
  discretion" note widening the survivor list by one entry, following the same pattern the plan
  itself already authorizes for Gate B's `html_static_path` scoping.
- **Files modified:** `.planning/phases/30-japanese-rtd-site-hand-rolled-machinery-orphan-removal/30-EVIDENCE.md`
  only (no source, test, workflow, or config file was touched).
- **Verification:** Confirmed via `git log --oneline -- tests/test_readthedocs_config.py` that the
  line was introduced by `204f7ef feat(30-02): delete hand-rolled language-switcher machinery, trim
  conf.py`, and via direct read of the surrounding docstring (lines 288-298) that it describes the
  deletion in prose, referencing no surviving code path.
- **Committed in:** `203869c` (Task 1 commit)

---

**Total deviations:** 1 auto-documented (a process/evidence-recording discretion, not a code
change — no Rule 1/2/3 fix touched any source, test, workflow, or config file).
**Impact on plan:** None on scope. The finding does not change any prior wave's work and required
no edit; it only widens what this plan's own evidence record documents as an accounted-for textual
survivor, exactly matching the discretion the plan itself already authorizes for the same class of
finding elsewhere (Gate B).

## Issues Encountered

None beyond the Gate A finding documented above. The sandbox's Bash safety checker flagged several
multi-command `bash -c`-style invocations as "too complex to verify" when the command mixed several
separate operations (e.g., `env -u ... uv sync`, a combined branch/base assertion one-liner) —
worked around by splitting each into single, plain commands (`unset VIRTUAL_ENV
UV_PROJECT_ENVIRONMENT; uv sync ...` on one line; separate `git rev-parse` calls instead of a
combined script), consistent with this project's documented sandbox hazards.

## User Setup Required

None — no external service configuration required.

## Known Stubs

None — this plan writes no code or stub of any kind; its sole output is a verification record.

## Threat Flags

None. This plan's own `<threat_model>` classifies its risks as evidence-integrity concerns
(repudiation, tampering-by-gate-appeasement, filename collision), all `mitigate`d directly by the
evidence record's structure (verbatim command+output per gate, explicit `Deferred` sections, the
`30-EVIDENCE.md` filename rather than the reserved `30-VERIFICATION.md`). No new attacker-facing
surface was introduced; the one live network read (Gate G's fetch of the public RTD root) is an
unauthenticated `GET` with no credential and no body, accepted per the plan's own T-30-16
disposition.

## Next Phase Readiness

- **All five ROADMAP success criteria for Phase 30 are measured green on the merged tree**, with
  commands and verbatim output on the record in `30-EVIDENCE.md`.
- **Three items remain genuinely open**, recorded as `Deferred` rather than inferred passes: (1) an
  observed `docs.yml` CI run — owed to the milestone pull request against `main`; (2) the published
  `/en/latest/` page losing the switcher wrapper class and stylesheet reference — owed to the next
  Read the Docs rebuild of the tracked branch; (3) whether Furo's restored ad-placement/
  variant-selector slots render on the hosted site — owed to the same rebuild. None of these can be
  closed from inside this phase's worktree; the verifier is expected to abstain to `human_needed`
  on all three per this plan's own backstop-truth design.
- **Total phase deletion scope (34 files across Plans 02-03) is ready for the owner's manual merge**
  past `worktree.cleanup-wave`'s deletion guard, which has no bypass (Phase 27 precedent,
  `PROJECT.md` D-13).
- No blockers. This plan modified no source, test, workflow, or configuration file — its only
  artifact is `30-EVIDENCE.md`, exactly as scoped.

---
*Phase: 30-japanese-rtd-site-hand-rolled-machinery-orphan-removal*
*Completed: 2026-07-26*

## Self-Check: PASSED

- FOUND: `.planning/phases/30-japanese-rtd-site-hand-rolled-machinery-orphan-removal/30-EVIDENCE.md`
- FOUND: `.planning/phases/30-japanese-rtd-site-hand-rolled-machinery-orphan-removal/30-04-SUMMARY.md`
- ABSENT (good): `.planning/phases/30-japanese-rtd-site-hand-rolled-machinery-orphan-removal/30-VERIFICATION.md`
- FOUND commit: `203869c` (Task 1)
- FOUND commit: `3d30a00` (Task 2)
