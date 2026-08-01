---
phase: 38-structural-indentation-info-fields
plan: 08
subsystem: testing
tags: [sphinx, typst, translator, page-count, corpus-gate, test-census, phase-closeout]

# Dependency graph
requires:
  - phase: 38-structural-indentation-info-fields (38-05, 38-06, 38-07)
    provides: the landed desc_content/field_list indent wrappers, the single-value field-body reflow,
      and the literal_strong/literal_emphasis monospace leaves this plan re-measures and closes out
provides:
  - "Both page-count constants re-measured once against the post-Phase-38 build, with the misnamed
    constant (EXPECTED_PAGE_COUNT_PRE_PHASE) renamed to EXPECTED_PAGE_COUNT_CEILING, closing the
    second folded todo"
  - "D-08's whole-document claim checked against a real tox -e docs-pdf build (90 pages measured,
    versus the discussion session's exploratory 87-page prototype figure), with the divergence
    explained rather than absorbed"
  - "The full-corpus gate run explicitly and passing, with RESEARCH Open Question 1 checked and
    resolved (structurally unreachable, not merely absent from this corpus)"
  - "All milestone supply-chain invariants (zero new dependency, four preview packages, no new file
    under typsphinx/) verified mechanically with commands and output recorded"
  - "38-GATE-EVIDENCE.md consolidating the three wave-1 per-plan evidence files plus this plan's own
    Task 1/Task 2 evidence"
  - "38-TEST-CENSUS.md finalised against reality: Bucket A/B/C/D predicted-vs-actual tables, five
    honest misses folded in, D-13/D-14 dispositions restated with outcome, both folded todos verified
    closed via resolves_phase: 38"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A page-count constant whose name ties to a phase boundary ('PRE_PHASE') is renamed to describe
      its role instead (a ceiling for a <= guard) once a second phase moves it again, so the name
      cannot lie a second time over"

key-files:
  created:
    - .planning/phases/38-structural-indentation-info-fields/38-GATE-EVIDENCE.md
  modified:
    - tests/test_signature_page_boundary_render_gate.py
    - tests/test_signature_typography_multi_signature_page_count_gate.py
    - .planning/phases/38-structural-indentation-info-fields/38-TEST-CENSUS.md

key-decisions:
  - "EXPECTED_PAGE_COUNT_PRE_PHASE renamed to EXPECTED_PAGE_COUNT_CEILING rather than a
    phase-numbered alternative (e.g. EXPECTED_PAGE_COUNT_POST_PHASE_37), because a phase-tied name
    would only defer the same lying-name problem to whichever phase next re-measures this fixture;
    a role-describing name (it is the ceiling the <= guard checks) cannot go stale the same way."
  - "The D-08 whole-document divergence (90 measured vs. the session's 87-page prototype figure) is
    recorded as an explained real divergence, not investigated via a controlled ablation across
    D-01/D-03's narrowing pad wrapper, D-05's monospace widening, and D-07's reflow shortening --
    the reasoning is grounded in the emission contract's own documented per-effect facts (sections
    2.3, 4.4, 5.6), stated honestly as the best-supported explanation rather than an empirically
    isolated one."
  - "RESEARCH Open Question 1 (a single-paragraph field body whose paragraph contains non-inline
    content) is resolved both structurally (docutils' nodes.paragraph cannot contain Body-class
    block children at all) and empirically (163 real field-list lines in the corpus, zero fatal
    errors, empty unknown_visit catalogue) -- no follow-up todo filed."
  - "Both folded todos are verified closed via their resolves_phase: 38 frontmatter field rather than
    git mv'd from inside this worktree, per the orchestrator's explicit instruction: a worktree-local
    git mv registers as a file deletion, which worktree.cleanup-wave blocks unconditionally with no
    bypass -- the orchestrator's own close_phase_todos step performs the actual move on the main tree
    after this wave's worktree merges."

requirements-completed: [IND-01, IND-02, IND-03, IND-04, IND-05, FLD-01, FLD-02, FLD-03]

coverage:
  - id: D1
    description: "Both page-count constants re-measured once against the post-Phase-38 build; the
      misnamed constant renamed with its sole consumer updated and provenance comment extended"
    verification:
      - kind: unit
        ref: "tests/test_signature_page_boundary_render_gate.py::TestSignaturePageBoundaryRenderGate::test_page_count_does_not_inflate"
        status: pass
      - kind: unit
        ref: "tests/test_signature_typography_multi_signature_page_count_gate.py::TestSignatureTypographyMultiSignaturePageCountGate::test_multi_signature_document_page_count_at_real_geometry"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-08's whole-document claim checked against a real tox -e docs-pdf build rather than
      inherited, with the measured divergence from the session's prototype figure explained"
    verification:
      - kind: manual_procedural
        ref: "uv run tox -e docs-pdf; pypdf.PdfReader page count == 90 (see 38-GATE-EVIDENCE.md section 3)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Full-corpus gate run explicitly and passing; RESEARCH Open Question 1 checked and
      resolved with no instance found and a structural reason given"
    verification:
      - kind: integration
        ref: "tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error"
        status: pass
    human_judgment: false
  - id: D4
    description: "Milestone supply-chain invariants (zero new dependency, four preview packages, no
      new file under typsphinx/) verified mechanically"
    verification:
      - kind: unit
        ref: "tests/test_preview_version_sync.py (all 3 node ids)"
        status: pass
      - kind: other
        ref: "git diff <phase-base>..HEAD -- pyproject.toml uv.lock (empty); git diff --name-status <phase-base>..HEAD -- typsphinx/ (translator.py only)"
        status: pass
    human_judgment: false
  - id: D5
    description: "38-GATE-EVIDENCE.md consolidates the three wave-1 per-plan evidence files plus this
      plan's own Task 1/Task 2 evidence"
    verification:
      - kind: other
        ref: ".planning/phases/38-structural-indentation-info-fields/38-GATE-EVIDENCE.md (file exists, reviewed for completeness)"
        status: pass
    human_judgment: false
  - id: D6
    description: "38-TEST-CENSUS.md finalised against reality as a pure addition, with all five known
      misses folded in and both folded todos verified closed"
    verification:
      - kind: other
        ref: "git diff --stat .planning/phases/38-structural-indentation-info-fields/38-TEST-CENSUS.md (206 insertions, 0 deletions)"
        status: pass
    human_judgment: false
  - id: D7
    description: "The phase's aesthetic goal -- 'the page shows structure' -- checked by a human
      against the real rendered docs/_build/pdf/typsphinx.pdf, per the plan's own six-point
      human-check block. NOT YET PERFORMED as of this SUMMARY's writing."
    verification: []
    human_judgment: true
    rationale: "Automated gates prove the mechanics (indent columns, wrapper tokens, monospace
      calls); they cannot prove the rendered result reads well. The plan's own verify block names
      this a human-check explicitly and states it 'blocks nothing automatically' for other tasks,
      but this plan's own success_criteria still requires it: 'The phase's aesthetic goal has been
      looked at, not only measured.' Per this project's checkpoint protocol, an executor must not
      self-approve a human-judgment criterion."

# Metrics
duration: ~2h (interim, through Task 3's automatable work; human-check still pending)
completed: 2026-08-01
status: checkpoint-pending
---

# Phase 38 Plan 08: Phase Closeout — Page-Count Re-measure, Corpus Gate, Census Finalisation Summary

**Both page-count constants re-measured (unchanged), the misnamed constant renamed and its folded
todo closed, D-08's whole-document claim checked against a real build (90 pages, divergence from the
session's 87-page prototype explained), the full-corpus gate and every milestone supply-chain
invariant verified and consolidated into `38-GATE-EVIDENCE.md`, and `38-TEST-CENSUS.md` finalised
against reality with five honest misses folded in — Tasks 1-3's mechanical work is complete and
committed. This SUMMARY is written BEFORE the plan's own required human-check (paging through the
real rendered PDF against six aesthetic criteria), per this project's checkpoint protocol: an executor
does not self-approve a "looked at by a human" criterion. See "CHECKPOINT REACHED" in this executor's
own return message for what is being asked of the human/orchestrator next.**

## Performance

- **Duration:** ~2h (interim; Tasks 1-3's automatable work only)
- **Tasks:** 3 of 3 tasks' automatable work completed and committed; Task 3's own human-check step
  is the checkpoint this SUMMARY stops at
- **Files modified:** 4 (2 page-count test files, 1 new consolidated evidence file, 1 census file)

## Accomplishments

- Both page-count constants (`tests/test_signature_page_boundary_render_gate.py`'s
  `EXPECTED_PAGE_COUNT_CEILING`, renamed from `EXPECTED_PAGE_COUNT_PRE_PHASE`, and
  `tests/test_signature_typography_multi_signature_page_count_gate.py`'s `EXPECTED_PAGE_COUNT`)
  re-measured once against the post-Phase-38 build via a real `sphinx-build`/`typst.compile()`/
  `pypdf.PdfReader` pipeline: both **unchanged** (7 pages, 4 pages), with the dominant reason recorded
  for each — neither fixture contains the specific content (a field list, a body-less single-value
  field) that Phase 38's two countervailing page-count-moving mechanisms act on.
- The second folded todo closed: `EXPECTED_PAGE_COUNT_PRE_PHASE` (which had already held a
  post-Phase-37 value since plan 37-09) renamed to `EXPECTED_PAGE_COUNT_CEILING`, its sole consumer
  updated in the same commit, and its provenance comment extended (not replaced) with this phase's
  own re-measure.
- D-08's whole-document claim checked against a real build rather than inherited: `tox -e docs-pdf`
  on this project's own docs (content confirmed unchanged since the discussion session) measures
  **90 pages**, below the pre-Phase-38 baseline but 3 pages above the discussion session's own
  exploratory 87-page prototype figure. The gap is explained (not absorbed): the 87-page figure is
  attributed specifically to D-07's field-body reflow effect in isolation
  (`38-EMISSION-CONTRACT.md` §4.4); the shipped build also includes D-01/D-03's column-narrowing
  `pad(...)` wrapper and D-05's proportional-to-monospace widening (§5.6), both countervailing effects
  not present in that isolated figure. No controlled ablation was performed; this is the
  best-supported explanation from the contract's own documented facts, stated honestly as such.
- Full-corpus gate run explicitly (`uv run pytest tests/test_corpus_gate.py -m slow`): **1 passed, 1
  skipped** (an unrelated, pre-existing, env-gated measurement), in 14s. `38-RESEARCH.md`'s Open
  Question 1 (a single-paragraph field body containing non-inline content) checked explicitly: no
  instance found, resolved both structurally (docutils' `nodes.paragraph` cannot contain a
  `Body`-class block child at all — the shape is unreachable via standard RST parsing, not merely
  absent from this specific corpus) and empirically (163 real field-list lines across 10 corpus files,
  zero compile fatals, empty `unknown_visit` catalogue).
- Every milestone supply-chain invariant verified mechanically against the phase base commit
  (`1fefe51`): `pyproject.toml`/`uv.lock` diff empty (zero new runtime dependency), the three-site
  `@preview` version-sync gate green with exactly four packages declared, and `git diff --name-status`
  shows only `typsphinx/translator.py` modified across the whole phase (no new file, no new module,
  no new template asset).
- Whole-suite final state: **700 passed, 0 failed, 29 deselected** — a set-difference of +41 net new
  node ids against plan 38-04's recorded pre-phase baseline (659 passed), cross-validated against
  every implementation plan's own recorded intermediate totals (`659+41=700`; `38-05: 683+17=700`;
  `38-06: 689+11=700`; `38-07: 700+0=700`).
- Requirement verdict table (`38-GATE-EVIDENCE.md` §4.4): one row per requirement, each backed by a
  named node id. IND-05 recorded explicitly as **ASSERTED, not implemented** (D-01: no depth counter
  exists, so the requirement's "counter resets" wording is satisfied by proving depth cannot leak).
  IND-04's closing SC#4 grep re-run and confirmed **identical** to the discovery-time run (one match,
  `SHARED_INDENT_STEP` at line 29).
- `38-GATE-EVIDENCE.md` created, consolidating `38-GATE-EVIDENCE-01/02/03.md` (which remain in place
  with their full verbatim detail) alongside this plan's own Task 1/Task 2 evidence into one closing
  record.
- `38-TEST-CENSUS.md` finalised against reality as a pure addition (verified via `git diff --stat`:
  206 insertions, 0 deletions): Bucket A 4/4 predictions held with commit hashes; Bucket B all 11
  stays-green groups re-confirmed at closeout; Bucket C all 3 conditional rows re-verified GREEN
  directly against the final tree; Bucket D both constants unchanged plus the D-08 outcome recorded;
  five honest misses folded in (two `38-EMISSION-CONTRACT.md` §7 disagreements resolved correctly by
  the census's own reading, one genuine census miss from 38-06, one folded-todo prose prediction
  contradicted by 38-03's own measurement, one earlier-plan fixture-authoring oversight fixed by
  38-07). D-13's leave-in-place disposition and D-14's hand-derivation strategy both restated with
  their outcome, quoting `38-05-SUMMARY.md`'s own golden-migration evidence directly.
- Both folded todos verified closed via their `resolves_phase: 38` frontmatter field (confirmed by
  `grep -l`, not `git mv`'d from inside this worktree per the orchestrator's explicit instruction —
  a worktree-local `git mv` registers as a deletion, which `worktree.cleanup-wave` blocks
  unconditionally with no bypass).

## Task Commits

Each task's automatable work was committed atomically:

1. **Task 1: Re-measure page counts, rename the misnamed constant, verify D-08's whole-document claim** - `75d69a0` (test)
2. **Task 2: Run the full-corpus gate and milestone supply-chain checks, consolidate gate evidence** - `25079ec` (docs)
3. **Task 3: Finalise the census against reality (mechanical portion)** - `7b9c58b` (docs)

**Plan metadata:** (this commit, forthcoming — see CHECKPOINT REACHED for what remains)

## Files Created/Modified

- `tests/test_signature_page_boundary_render_gate.py` — `EXPECTED_PAGE_COUNT_PRE_PHASE` renamed to
  `EXPECTED_PAGE_COUNT_CEILING`, provenance comment extended with this phase's re-measure, sole
  consumer (`test_page_count_does_not_inflate`) updated.
- `tests/test_signature_typography_multi_signature_page_count_gate.py` — provenance comment extended
  with this phase's re-measure (constant value and name unchanged — this constant was never the
  misnamed one).
- `.planning/phases/38-structural-indentation-info-fields/38-GATE-EVIDENCE.md` — new, consolidating
  the three wave-1 per-plan evidence files plus this plan's own Task 1/Task 2 evidence.
- `.planning/phases/38-structural-indentation-info-fields/38-TEST-CENSUS.md` — "Finalisation against
  reality" section appended (pure addition).

## Decisions Made

See `key-decisions` in the frontmatter above for the full list; the two most consequential:

- **The rename target, `EXPECTED_PAGE_COUNT_CEILING`, describes the constant's role (a `<=` guard's
  ceiling) rather than tying the name to Phase 38's own boundary** — a phase-numbered alternative
  would only defer the exact same lying-name problem to whichever phase next re-measures this
  fixture.
- **The D-08 divergence (90 vs. 87) is recorded as an explained real divergence, not chased down via
  a controlled ablation.** The explanation is grounded in the emission contract's own documented facts
  about each effect's direction (§2.3's narrowing pad, §4.4's reflow shortening, §5.6's monospace
  widening), stated as the best-supported reading rather than an empirically isolated one — building
  an ablation harness (reverting to intermediate wave commits without touching the worktree's own
  HEAD) was judged out of proportion to what this plan's acceptance criteria require, which ask for an
  explanation, not a full causal decomposition.

## Deviations from Plan

### Auto-fixed Issues

None — Task 1/Task 2/Task 3's mechanical work executed as planned, with no bugs, missing
functionality, or blocking issues encountered that required a Rule 1/2/3 auto-fix.

**Total deviations:** 0
**Impact on plan:** None.

## Issues Encountered

- **The initial attempt to independently re-derive the pre-Phase-38 docs page count via a
  `PYTHONPATH`-shadowed copy of the pre-phase `translator.py` did not work**: this project's editable
  install uses a PEP 660 meta-path finder (not a plain `sys.path` entry), which is consulted before
  `PYTHONPATH`-prepended directories regardless of `sys.path` order — the "shadow" build silently used
  the real, current worktree code both times. No repository file was touched by this attempt (confirmed
  via `git status --short typsphinx/` showing clean before and after); the attempt was abandoned in
  favor of the explanation recorded in Task 1's commit and `38-GATE-EVIDENCE.md` §3, which does not
  depend on an independently re-derived pre-phase count.
- **The worktree's `uv` and `ruff` shims needed re-applying after `uv sync --extra dev --extra docs`**
  (adding the `docs` extra to provision `tox -e docs-pdf` re-created `.venv/bin/uv` as a
  dynamically-linked ELF the NixOS sandbox cannot execute, overwriting the earlier shim). Re-symlinked
  both `uv` and `ruff` to their NixOS-store / main-tree patchelf'd counterparts; a provisioning
  detail, not a code issue.

## User Setup Required

None — no external service configuration required.

## CHECKPOINT: Human-check pending

This plan's Task 3 has one remaining step this executor cannot perform: paging through the rendered
`docs/_build/pdf/typsphinx.pdf` (90 pages, built fresh during Task 1 via `tox -e docs-pdf`, unchanged
since — `typsphinx/` was not touched by any task in this plan) against the plan's own six-point
aesthetic check, and replying "approved" or describing what reads wrong. See this executor's own
"CHECKPOINT REACHED" return message for the full text of what is being asked.

Once the human-check is answered, a continuation agent (or this same agent, if resumed) should:
1. Record the human's verdict in this SUMMARY (replacing this section).
2. If "approved": update coverage item D7's `verification` to a `manual_procedural` entry with
   `status: pass`, set this frontmatter's `status:` to `complete`, run the final self-check, update
   STATE.md/ROADMAP.md/REQUIREMENTS.md per the standard state_updates step (note: `requirements
   mark-complete` for FLD-01/FLD-02/FLD-03 is still outstanding — IND-01..05 were already marked by
   plan 38-05's own commit `3e27097`, confirmed by `git log -- .planning/REQUIREMENTS.md`; FLD-01/02/03
   remain unchecked in `.planning/REQUIREMENTS.md` as of this SUMMARY), and make the final
   `docs(38-08): complete phase closeout plan` commit.
2. If the human describes something that reads wrong: apply Rule 1/2/3 deviations as appropriate
   (documenting them in this SUMMARY), or escalate to Rule 4 if it requires an architectural change
   to `typsphinx/translator.py` — which this plan's own `<objective>` states makes no change to
   `typsphinx/`, so any real rendering defect found here is very likely to be a Phase 39+ finding, not
   a same-plan fix, and should be filed as a todo per this project's standing convention rather than
   patched inside a plan explicitly scoped to make no translator change.

## Next Phase Readiness

- Blocked on the human-check above. All of this plan's mechanically-verifiable acceptance criteria are
  satisfied and committed; only the aesthetic sign-off remains before this phase can be marked
  complete and the milestone can proceed past Phase 38.
- No other blockers.

---
*Phase: 38-structural-indentation-info-fields*
*Interim summary written: 2026-08-01 (Tasks 1-3 mechanical work only; human-check pending)*

## Self-Check: PASSED

- FOUND: tests/test_signature_page_boundary_render_gate.py
- FOUND: tests/test_signature_typography_multi_signature_page_count_gate.py
- FOUND: .planning/phases/38-structural-indentation-info-fields/38-GATE-EVIDENCE.md
- FOUND: .planning/phases/38-structural-indentation-info-fields/38-TEST-CENSUS.md
- FOUND: .planning/phases/38-structural-indentation-info-fields/38-08-SUMMARY.md
- FOUND: commit 75d69a0 (Task 1)
- FOUND: commit 25079ec (Task 2)
- FOUND: commit 7b9c58b (Task 3, mechanical portion)
