---
phase: 48-compile-time-cross-reference-guard
plan: 04
subsystem: translator
tags: [sphinx, typst, cross-reference, xref, compile-time, pytest, measurement]

# Dependency graph
requires:
  - phase: 48-compile-time-cross-reference-guard (plan 03)
    provides: "Every label-reference emission site routed through _label_existence_guard (visit_reference, visit_citation's back-reference loop, visit_pending_xref/depart_pending_xref), the D-06 same-document exemption, and the 16-test direct unit gate pinning the helper's contract"
provides:
  - "48-EVIDENCE.md's D-11 compile-time cost record: -2.37% (bottom tier, record only) against the pre-fixed tiers and the 28.93s/28.56s baseline"
  - "48-EVIDENCE.md's D-09 citation-marker delta measurement: the Sphinx doc/ corpus exercises zero citations, recorded plainly rather than presented as verification, with the project's own citation gates (26/26 passing) recorded as the only real D-09 coverage"
  - "48-EVIDENCE.md's accepted label-collision false-negative record, with a filed remediation todo"
  - "48-EVIDENCE.md's SC#2 site enumeration (query() string derives in exactly one place; all 3 sites route through it) and SC#3 build-time-mechanism-deleted grep discharge (typsphinx/-scoped, per ROADMAP.md's own SC#3 wording)"
  - "48-EVIDENCE.md's D-01 re-check (no published contract changed) and Phase green gate record (1062 passed/5 skipped, black+mypy clean, ruff NixOS-unrunnable documented)"
  - "REQUIREMENTS.md's XREF-03/XREF-04 checkboxes now carry the evidence-section parenthetical this plan's task 3 requires"
affects: []

# Actuals (#2632)
actuals:
  tokens: 9571
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Two-build BEFORE/AFTER corpus measurement via a detached git worktree + PYTHONPATH override, but with the subprocess cwd deliberately set OUTSIDE the repository root -- otherwise python -m/-c prepends the repo-root cwd ('') to sys.path ahead of PYTHONPATH, and since the repo root itself contains a top-level typsphinx/ directory, the override silently never takes effect. A real, measured hazard in the established test_empty_url_before_after methodology, worked around by invocation, not by inventing a new mechanism."

key-files:
  created:
    - .planning/todos/pending/2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md
  modified:
    - .planning/phases/48-compile-time-cross-reference-guard/48-EVIDENCE.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "D-11's tier decision: -2.37% (after-mean 28.065s vs. before-mean 28.745s) -- bottom tier (under +20%), record only, no todo filed, no Phase 49 blocker."
  - "D-09's corpus measurement found zero citations anywhere in Sphinx's own doc/ tree -- recorded plainly as 'the corpus does not exercise D-09' rather than presenting the 0-vs-0 delta as verification, with the project's own tests/test_citation_render_gate.py + tests/test_citation_degradation_gate.py (26/26 passing) recorded as the real D-09 coverage."
  - "SC#3's binding scope resolved to typsphinx/ alone (ROADMAP.md's own SC#3 sentence, and this project's own test_no_file_mentions_deleted_include_set_attribute's self_package_dir() scope) rather than the plan's literal combined typsphinx/+tests/ grep wording -- see Deviations."

patterns-established: []

requirements-completed: [XREF-03, XREF-04]

coverage:
  - id: D1
    description: "The compile-time guard's full-corpus cost is measured against pre-fixed tiers and recorded as a finding, not assumed (SC#4)"
    requirement: "XREF-04"
    verification:
      - kind: manual_procedural
        ref: "time uv run pytest tests/test_corpus_gate.py -m slow (2 runs, 28.92s/27.21s), recorded in 48-EVIDENCE.md ## D-11 compile-time cost"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-09's citation-marker output delta is measured corpus-wide rather than argued from design alone"
    requirement: "XREF-04"
    verification:
      - kind: manual_procedural
        ref: "48-EVIDENCE.md ## D-09 citation-marker delta (two-build BEFORE/AFTER measurement, zero citations found; fallback: uv run pytest tests/test_citation_render_gate.py tests/test_citation_degradation_gate.py -q, 26 passed)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The guard's one new false-negative class (label-collision) is measured, filed, and requires explicit owner acceptance"
    requirement: "XREF-04"
    verification: []
    human_judgment: true
    rationale: "48-04-PLAN.md's task 3 <human-check> explicitly requires OWNER SIGN-OFF (items 4/5/6) -- accepting the label-collision limit, the D-11 tier outcome, and the D-01 visibility loss. This is a deliberate human-judgment gate the plan itself names; an autonomous executor cannot supply it."
  - id: D4
    description: "SC#2 and SC#3 are discharged by repo-wide greps pasted verbatim (milestone invariant #4), and D-01's published-contract absence is re-measured"
    requirement: "XREF-04"
    verification:
      - kind: unit
        ref: "grep -rn master_included_docnames|_compute_master_included_docnames|degrade_xref_to_text typsphinx/ (zero matches, all three); grep -rn 'query(<' / '_label_existence_guard' typsphinx/ (single-derivation-point + 3 call sites); grep -rn 'non-included|degrade' docs/source (zero matches)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The phase closes green on the full suite plus black/mypy (ruff excepted, documented deferral) -- binding constraint #8"
    requirement: "XREF-04"
    verification:
      - kind: integration
        ref: "uv run pytest -q (1062 passed, 5 skipped); uv run black --check .; uv run mypy typsphinx/"
        status: pass
    human_judgment: false

# Metrics
duration: 42min
completed: 2026-08-12
status: complete
---

# Phase 48 Plan 04: D-11/D-09 Measurement, SC#2/SC#3 Grep Discharge, Phase Green Gate Summary

**D-11's full-corpus compile-time cost measured at -2.37% (bottom tier, record only); D-09's citation-marker delta found the external corpus exercises zero citations (recorded plainly, project's own 26/26-passing citation gates cited as the real coverage); the label-collision false negative filed as an accepted, owner-sign-off-pending limit; SC#2/SC#3 discharged by repo-wide grep (typsphinx/-scoped, reconciling a plan-vs-reality gap in the combined typsphinx/+tests/ wording); D-01 re-confirmed; full suite green (1062 passed/5 skipped, black+mypy clean).**

## Performance

- **Duration:** 42 min
- **Started:** 2026-08-12T14:55:00+09:00 (approximate)
- **Completed:** 2026-08-12T15:37:02+09:00
- **Tasks:** 3
- **Files modified:** 3 (2 modified, 1 created)

## Accomplishments

- **D-11 compile-time cost** (`## D-11 compile-time cost`): quoted D-11's three tiers verbatim above the after-number; ran `time uv run pytest tests/test_corpus_gate.py -m slow` twice (28.92s, 27.21s) against the recorded 28.93s/28.56s pre-fix baseline. Percentage change: **-2.37%** (after-mean 28.065s vs. before-mean 28.745s) — the corpus build is, if anything, marginally faster after the guard landed. Falls in the **bottom tier**: recorded only, no todo filed, no `STATE.md` blocker added.
- **D-09 citation-marker delta** (`## D-09 citation-marker delta`): resolved `BEFORE_SHA` (`09f5d7f`, the commit immediately preceding plan 48-02's TRACER commit `8184f4d`) via `git log --reverse` filtering for the earliest `translator.py`-touching commit naming `48-02`. Built the same wired Sphinx `doc/` corpus twice (`-b typst`) — a detached pre-guard worktree with `PYTHONPATH` shadowing for BEFORE, as-installed HEAD for AFTER. Counted zero citation label cells and zero citation grid-open markers (`columns: (auto, 1fr)`) in BOTH builds: **the corpus exercises no citations at all**. Recorded that finding plainly rather than presenting the 0-vs-0 delta as verification, per the task's own instruction, and ran the project's own citation gates (`tests/test_citation_render_gate.py` + `tests/test_citation_degradation_gate.py`, 26/26 passing) as the real, committed D-09 coverage.
- **A real PYTHONPATH-shadowing hazard found and worked around, not assumed to work**: the established `test_empty_url_before_after` two-build methodology's `PYTHONPATH` override silently fails to shadow the installed `typsphinx` package when the BEFORE subprocess's working directory is the repository root — `python -m`/`-c` prepends the cwd (`''`) to `sys.path` ahead of any `PYTHONPATH` entry, and the repo root itself contains a top-level `typsphinx/` package. Confirmed empirically both ways (shadowing fails from repo root, succeeds from a cwd outside it) and recorded in `48-EVIDENCE.md`'s Step 2. Both D-09 builds were run from a scratchpad cwd to make the override actually take effect — the invocation was corrected, not the methodology itself.
- **Accepted limit — label-collision false negative** (`## Accepted limit — label-collision false negative`): re-ran the collision characterization test (`uv run pytest tests/test_xref_compile_time_guard_render_gate.py -q -k collision`, 1 passed) and rebuilt `tests/fixtures/xref_label_collision_guard_gate/` to paste its emitted `index.typ` reference line. Recorded, in four sentences, what the guard asks, the measured consequence, the `docname:id` + `/`→`_u2f_` narrowing, and the contrast with the deleted docname-membership mechanism. Filed a todo naming the class and the remediation direction (carry the target docname into the guard's decision).
- **SC#2 — site enumeration** (`## SC#2 — site enumeration`): confirmed the `query(<{label}>)` f-string construction appears exactly once in `typsphinx/translator.py` (inside `_label_existence_guard` itself); enumerated all three emission sites plus the two SC#4/D-06-exempt same-document branches in a 5-row table with current line numbers; closed open question #1 (`translator.py:4291`'s nature) by cross-referencing `48-RED-EVIDENCE.md`'s enumerated impossibility argument — confirmed a fourth independent degradation site, guarded as defence in depth per D-04, not routed through `_reference_anchor_decision`.
- **SC#3 — the build-time mechanism is gone** (`## SC#3 — the build-time mechanism is gone`): zero matches for `master_included_docnames`, `_compute_master_included_docnames`, and `degrade_xref_to_text` across `typsphinx/` — the binding bar per ROADMAP.md's own SC#3 wording. The combined `typsphinx/ tests/` grep for `master_included_docnames` (per the plan's literal acceptance-criteria wording) is also pasted and every one of its 7 matches shown to be either historical-narrative prose or the deletion-detection unit test's own necessary literal search string — reconciled explicitly as a deviation (below).
- **D-01 — no published contract changed** (`## D-01 — no published contract changed`): re-ran `grep -rn 'non-included|degrade' docs/source` — zero matches, confirming the discussion-time finding still holds at implementation time. Recorded the diagnostic-visibility consequence explicitly: a reference to an `:orphan:` target now degrades with zero diagnostic at any layer, per Fable's review LOW finding; no replacement diagnostic added (D-01 forbids it).
- **Phase green gate** (`## Phase green gate`): `uv run pytest -q` → 1062 passed, 5 skipped, 0 failed; `uv run black --check .` clean; `uv run mypy typsphinx/` clean; `uv run ruff check .` unrunnable on this NixOS host (documented pre-existing deferral, `ruff-generic-linux-elf-unrunnable-on-nixos`), recorded plainly rather than claimed clean.
- **REQUIREMENTS.md**: XREF-03/XREF-04 (already checked off in plan 48-02, ahead of this plan's schedule) gained the evidence-section parenthetical this plan's task 3 requires, with no other requirement line touched.

## Task Commits

Each task was committed atomically:

1. **Task 1: Take the D-11 after-measurement against pre-fixed tiers and record the cost decision** - `57dcd4c` (docs)
2. **Task 2: Measure D-09's citation-marker delta corpus-wide and record the label-collision limit as accepted** - `b6f4f6e` (docs)
3. **Task 3: Discharge SC#2/SC#3 by repo-wide grep, re-check the published contract, and close the phase green** - `549fa6b` (docs)

**Plan metadata:** (this commit, following) - `docs: complete plan`

_Note: this plan's tasks are all `type="auto"`, non-TDD -- each task's action/verify loop lands in a single commit._

## Files Created/Modified

- `.planning/phases/48-compile-time-cross-reference-guard/48-EVIDENCE.md` — appended `## D-11 compile-time cost`, `## D-09 citation-marker delta`, `## Accepted limit — label-collision false negative`, `## SC#2 — site enumeration`, `## SC#3 — the build-time mechanism is gone`, `## D-01 — no published contract changed`, `## Phase green gate`
- `.planning/REQUIREMENTS.md` — XREF-03/XREF-04 gained the evidence-section parenthetical; no other line touched
- `.planning/todos/pending/2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md` (new) — the accepted label-collision false-negative class, its characterizing fixture, and the remediation direction

## Decisions Made

- D-11's tier: bottom (under +20%), applied mechanically from the measured -2.37% — record only, no todo, no blocker.
- D-09's corpus finding (zero citations in Sphinx's own `doc/` tree) is recorded plainly, not presented as verification; the project's own citation gates are cited as the real coverage instead.
- The BEFORE/AFTER build subprocess's working directory is deliberately set outside the repository root for both D-09's measurement builds, to make the established `PYTHONPATH`-override methodology actually shadow the installed package (a hazard measured and worked around, not a new methodology invented).
- SC#3's binding scope is `typsphinx/` alone (ROADMAP.md's own SC#3 sentence, and the project's own `test_no_file_mentions_deleted_include_set_attribute`'s scope), not the plan's literal combined `typsphinx/+tests/` grep wording — see Deviations.

## Deviations from Plan

### Auto-fixed Issues

None — no bugs, missing critical functionality, or blocking issues encountered that required code changes. This plan touches only `.planning/` artifacts; `git status --porcelain typsphinx/` and `git diff --stat tests/` both print nothing throughout, confirmed after each task.

### Discretionary Reconciliations

**1. [Discretion — plan-vs-reality reconciliation] Task 3's acceptance criteria and the plan's top-level `<verification>` block both state `grep -rn master_included_docnames typsphinx/ tests/` "exits 1" — measured to actually exit 0 (7 non-code matches in `tests/`)**
- **Found during:** Task 3, SC#3 grep
- **Issue:** The plan's literal wording (both in task 3's `acceptance_criteria` and the plan-level `<verification>` block) was written before plan 48-03 landed. Plan 48-03 added `tests/test_label_existence_guard_unit.py`'s own `test_no_file_mentions_deleted_include_set_attribute` (whose detection logic necessarily contains the literal string `"master_included_docnames"` as its search target) and updated two other test docstrings to narrate the deletion using the literal old name (historical-reference prose, never live code). A combined `typsphinx/ tests/` grep for `master_included_docnames` therefore returns 7 matches (exit 0), not zero (exit 1).
- **Resolution:** ROADMAP.md's own SC#3 wording is scoped to `typsphinx/` alone ("`grep -rn master_included_docnames typsphinx/` returns nothing"), and this project's own committed `test_no_file_mentions_deleted_include_set_attribute` independently scopes its own sweep to `typsphinx/` only (`self._package_dir()`, line 388) — both confirm the actual, binding "zero occurrences" bar is `typsphinx/`-scoped. `48-EVIDENCE.md`'s SC#3 section pastes BOTH the `typsphinx/`-only grep (zero matches, matching ROADMAP.md and the acceptance bar) and the combined `typsphinx/ tests/` grep (7 matches, per the plan's literal instruction to "paste every transcript"), and explains why every `tests/` match is inert prose or the deletion-detection test's own necessary literal string — never live code consulting the deleted attribute. No file was modified to force the literal combined-grep criterion to pass (that would mean either deleting the deletion-detection test's own search string, which would break the test whose entire job is asserting the deletion, or rewriting `48-02`/`48-03`'s already-committed historical-narrative docstrings, which is out of this plan's stated scope — task 3's action explicitly forbids modifying `typsphinx/`, and modifying already-landed prior-plan test docstrings to chase a literal grep count was judged out of proportion to the actual risk, since zero of the matches are live code).
- **Files modified:** None (this is a reconciliation recorded in `48-EVIDENCE.md`'s SC#3 section and here, not a code or test change).
- **Verification:** `grep -rn master_included_docnames typsphinx/` exits 1 (zero matches) — the binding, ROADMAP-scoped bar is met. `tests/test_label_existence_guard_unit.py::TestSingleDerivationPointStructural` (2 tests, including the deletion-detection test) passes.
- **Committed in:** `549fa6b` (Task 3 commit)

---

**Total deviations:** 1 discretionary reconciliation (a plan-vs-reality wording gap, resolved against the phase's own authoritative ROADMAP.md wording and a pre-existing committed structural test's own scope). Zero auto-fixed bugs, zero missing-functionality additions, zero blocking-issue fixes.
**Impact on plan:** No code or test file was touched to force a literal-but-outdated acceptance wording to pass. The actual binding success criterion (SC#3, ROADMAP.md) is fully met.

## Issues Encountered

- The PYTHONPATH-shadowing hazard (documented above under Accomplishments and Decisions) required empirical debugging before the D-09 two-build measurement could proceed — resolved by running both subprocess builds from a cwd outside the repository, not by inventing a new before/after methodology.

## User Setup Required

None — no external service configuration required.

**Owner sign-off still outstanding (task 3's `<human-check>`, not dischargeable by this autonomous executor):**

1. Open `48-EVIDENCE.md` and confirm by reading: the SC#2 table's line numbers resolve in the current tree (confirmed by this executor via direct `grep -n`/`awk` reads); the D-11 tiers are quoted above the measured number (confirmed structurally); the D-04 answer in `48-RED-EVIDENCE.md` reads as an enumerated impossibility argument (present, unchanged by this plan).
2. Build the project's own documentation with `tox -e docs-pdf` and confirm the produced PDF still opens and its internal cross-reference links still navigate — **not run by this executor**; this is the plan's own designated manual dogfooding check with no automated equivalent in this phase.
3. **OWNER SIGN-OFF required on three items**, per the plan's explicit instruction (both cross-AI reviewers asked for this rather than leaving the residual risk implicit):
   - Accept the label-collision false-negative as a real, narrow, measured, accepted limit (`## Accepted limit — label-collision false negative`).
   - Accept the D-11 tier outcome (bottom tier reached — this one carries no additive Phase 49 obligation, unlike the middle/top tiers, but still names the finding for the record).
   - Accept the D-01 visibility loss (an `:orphan:`-target reference now degrades with zero diagnostic at any layer).

## Next Phase Readiness

- Phase 48 is functionally complete: all three of this plan's tasks landed, the full suite is green (1062 passed, 5 skipped), `black`/`mypy` are clean, and both requirements (XREF-03, XREF-04) are checked off in `REQUIREMENTS.md` against named evidence sections.
- `ruff` remains unrunnable on this NixOS host — a standing, documented deferral (`ruff-generic-linux-elf-unrunnable-on-nixos`, QUA-06) that does not block this phase per that deferral's own terms (CI carries lint authority).
- One new todo filed: `2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md`, carrying the remediation direction (carry the target docname into the guard's decision) for a future phase to pick up.
- **Phase 48 must land no later than Phase 49** (binding constraint #1, milestone's one hard ordering constraint) — this plan's completion, pending the three owner sign-offs above, clears that gate.
- The three owner-sign-off items and the `tox -e docs-pdf` dogfooding check remain outstanding — these are the plan's own designated human checkpoints, not dischargeable by an autonomous executor, and should be surfaced at the phase's UAT/verify-work step.

---
*Phase: 48-compile-time-cross-reference-guard*
*Completed: 2026-08-12*
