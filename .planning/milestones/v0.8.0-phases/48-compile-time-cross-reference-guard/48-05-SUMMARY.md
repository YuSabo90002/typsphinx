---
phase: 48-compile-time-cross-reference-guard
plan: 05
subsystem: docs-tooling
tags: [pypdf, docutils, sphinx, typst, cross-reference, gap-closure]

# Dependency graph
requires:
  - phase: 48-compile-time-cross-reference-guard (plans 01-04)
    provides: the D-07 compile-time label-existence guard contract and its three anchored-xref
      call sites, plus 48-EVIDENCE.md's guard-contract measurement this plan builds on
provides:
  - A reproducible, pasted pre-fix measurement of the G-48-4 dead-link population in the built
    documentation PDF (40 URI-action annotations / 20 distinct .pdf-suffixed targets), split by
    measurement into two sub-populations (35/15 real documents, 5/5 Sphinx-generated virtual pages)
  - The owner's decided policy for the 5 Sphinx-generated-page references (option-a: leave them
    as dead file links; guard only references that resolve onto a real document)
  - Every post-fix expected value plan 48-06's fixture/gate module and plan 48-07's end-to-end
    re-measurement will assert -- self-anchor token, definition-site form, reference-site form,
    fixture design, expected PDF shape, expected post-fix count (5), collateral-change budget --
    written down before any emitter change exists
affects: [48-06, 48-07]

# Actuals (#2632)
actuals:
  tokens: 8894
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Write-expected-values-first (D-03/47-EXPECTED-STRUCTURE.md convention) applied to a gap
      closure: every value a later plan's gates will assert is derived from the fixture design and
      the existing guard contract, never read off a fresh build."
    - "Collision-safety argued from measurement, not assumption -- a real docutils.nodes.make_id
      transcript over adversarial inputs, cross-checked against the real corpus's own domain-object
      label shapes."

key-files:
  created: []
  modified:
    - .planning/phases/48-compile-time-cross-reference-guard/48-RED-EVIDENCE.md
    - .planning/phases/48-compile-time-cross-reference-guard/48-EXPECTED-STRUCTURE.md

key-decisions:
  - "Owner selected option-a at the Task 2 blocking checkpoint: guard only references that resolve
    onto a real document (found_docs membership test); the 5 Sphinx-generated-page references
    (genindex/py-modindex/search, 2 of them via a `../`-prefixed form) remain unfixed dead file
    links by deliberate policy, not oversight."
  - "Self-anchor token fixed as __tsx-doc__, argued (not asserted) collision-safe against both
    docutils make_id output (measured: never emits '_', even from underscore-carrying input) and
    Sphinx domain object ids (measured against the real corpus: python-identifier-derived ids
    never carry '-') -- a token requiring both characters is unreachable from either source."
  - "Expected post-fix URI-action count is 5, not 0 -- the owner's option-a choice means
    sub-population B stays exactly as measured pre-fix; only sub-population A's 35 annotations
    across 15 targets close."

requirements-completed: [XREF-03]

coverage:
  - id: D1
    description: "Pre-fix G-48-4 dead-link population measured, bucketed, and split into two
      sub-populations by resolution (not assumption), with the UAT's own sub-population-B count
      re-derived and confirmed to agree with the UAT's already-corrected figure."
    requirement: XREF-03
    verification:
      - kind: other
        ref: ".planning/phases/48-compile-time-cross-reference-guard/48-RED-EVIDENCE.md#Baseline 4 -- pasted pypdf enumeration transcript against a real uv run tox -e docs-pdf build"
        status: pass
    human_judgment: false
  - id: D2
    description: "Owner decision obtained at a blocking checkpoint for the one genuinely open
      policy question (Sphinx-generated pages with no Typst counterpart), recorded verbatim rather
      than chosen by the executor."
    verification: []
    human_judgment: true
    rationale: "A policy choice with user-facing consequences (which dead links stay dead) --
      requires the project owner's judgment, not automated verification."
  - id: D3
    description: "Every post-fix expected value plan 48-06's fixture/gate module and plan 48-07's
      end-to-end re-measurement will assert is written into 48-EXPECTED-STRUCTURE.md, derived from
      the fixture design and the existing D-07 guard contract, before any emitter change exists."
    requirement: XREF-03
    verification:
      - kind: other
        ref: ".planning/phases/48-compile-time-cross-reference-guard/48-EXPECTED-STRUCTURE.md -- Phase 48 Plan 05 section, git diff shows additions-only against typsphinx/ and tests/ throughout"
        status: pass
    human_judgment: false

# Metrics
duration: ~50min (active execution; excludes the blocking-checkpoint owner-decision wait)
completed: 2026-08-14
status: complete
---

# Phase 48 Plan 05: Whole-Document Cross-Reference Gap Closure (G-48-4) — Measurement and Design Summary

**Measured the pre-fix G-48-4 dead-link population (40 annotations / 20 targets, split 35/5 by
whether the target resolves onto a real document), got the owner's policy decision on the 5
Sphinx-generated-page references at a blocking checkpoint, and wrote every post-fix expected value
— self-anchor token, definition/reference-site forms, fixture design, expected PDF shape, the
single expected post-fix count (5) — into `48-EXPECTED-STRUCTURE.md` before any emitter code
exists.**

## Performance

- **Duration:** ~50 min active execution (excludes the blocking-checkpoint wait for the owner's
  decision)
- **Completed:** 2026-08-14T03:46:46Z
- **Tasks:** 3 (Task 1 auto, Task 2 checkpoint:decision, Task 3 auto)
- **Files modified:** 2

## Accomplishments

- Rebuilt the documentation PDF via the pinned `uv run tox -e docs-pdf` invocation (exit 0, 5
  warnings, matching the UAT's own recorded baseline) and enumerated every `/Link` annotation with
  `pypdf`: 37 internal `/Dest`, 465 URI actions, 0 other (502 total).
- Filtered to the 40 URI actions ending in the typstpdf builder's `.pdf` `out_suffix` and split
  them, by measurement using `_resolve_xref_docname`'s own join/normalize/strip logic (not by eye),
  into sub-population A (15 targets / 35 annotations, resolves onto a real document) and
  sub-population B (5 targets / 5 annotations, Sphinx-generated `genindex`/`py-modindex`/`search`
  pages with no Typst counterpart). Re-derived sub-population B's count against the UAT gap entry's
  own already-corrected `measured_scope` figure — both agree at 5; no new divergence.
- Obtained the owner's decision at the Task 2 blocking checkpoint: **option-a** — guard only
  references resolving onto a real document; the 5 Sphinx-generated-page references stay dead file
  links by deliberate policy.
- Wrote the complete post-fix design into `48-EXPECTED-STRUCTURE.md`: the self-anchor token
  (`__tsx-doc__`) with its collision-safety argument run against a real `docutils.nodes.make_id`
  transcript and the real corpus's own domain-object label shapes; the exact definition-site and
  reference-site emitted forms (fully substituted for docnames `included` and `orphan`); the
  `tests/fixtures/xref_whole_document_guard_gate/` fixture design; the expected compiled-PDF shape;
  the owner's decision recorded verbatim with its single consequence (expected post-fix count: 5,
  not 0); and the corpus-wide collateral-change budget.

## Task Commits

Each task was committed atomically:

1. **Task 1: Enumerate the pre-fix dead-link population in the built documentation PDF** -
   `4b0ee584` (docs)
2. **Task 2: checkpoint:decision** — no commit (decision-only task; owner selected option-a,
   recorded verbatim in Task 3's commit)
3. **Task 3: Write every post-fix expected value down before the emitter changes** - `3ef57116`
   (docs)

_Note: this is a `type: execute` (not `tdd`) plan — commits use `docs(48-05): ...`, since every
change in this plan is planning-artifact prose, not source code or tests (binding constraint #6:
no `typsphinx/` or `tests/` change exists anywhere in this plan)._

## Files Created/Modified

- `.planning/phases/48-compile-time-cross-reference-guard/48-RED-EVIDENCE.md` - Appended "Baseline
  4 — G-48-4" section: build invocation, pasted enumeration snippet and verbatim output, the A/B
  split with resolution rule stated, the re-derivation against the UAT's figure, and the quickstart
  "What's Next?" page anchor confirming the reported symptom's four URIs are still present.
- `.planning/phases/48-compile-time-cross-reference-guard/48-EXPECTED-STRUCTURE.md` - Appended
  "Phase 48 Plan 05 — Whole-Document Reference Path" section, seven numbered parts covering the
  self-anchor token through the collateral-change budget.

## Decisions Made

- **Owner selected option-a** at the Task 2 blocking checkpoint (verbatim option text recorded in
  `48-EXPECTED-STRUCTURE.md` §6): "Leave them as they are — guard only references that resolve
  onto a real document." Consequence: the expected post-fix count of URI actions ending in `.pdf`
  is **5**, not 0 — sub-population B remains exactly as measured pre-fix.
- **Self-anchor token fixed as `__tsx-doc__`**, chosen (per the plan's own stated preference,
  matching the project-wide `__tsx_` prefix convention `48-EVIDENCE.md` already fixed for the
  guard's bound identifier) and its collision-safety RUN rather than asserted: a real `make_id`
  transcript over 9 adversarial inputs (including inputs already carrying underscores) proves
  `make_id` never emits `_`; a spot-check against the real corpus's own domain-object labels proves
  a Python-identifier-derived id never carries `-`. A token requiring both characters is therefore
  unreachable from either source.
- **The fixture design for `tests/fixtures/xref_whole_document_guard_gate/`** is fixed on paper
  (master `index`, toctree'd `included`, orphaned `orphan`, distinctive body markers) so plan
  48-06's fixture files are a direct transcription, not a fresh design decision.

## Deviations from Plan

None — plan executed exactly as written. The checkpoint task required an owner decision before
Task 3 could proceed; that decision was obtained externally (relayed by the coordinator) rather
than chosen by the executor, matching the plan's explicit prohibition against pre-empting the
owner's choice.

## Issues Encountered

None. Both `uv run tox -e docs-pdf` builds (env provisioning, then the actual build) completed
cleanly on the first attempt, matching the UAT's own recorded baseline exactly (exit 0, "build
succeeded, 5 warnings"). The worktree's own environment provisioning (`uv sync --extra dev
--extra docs`) was required and completed without incident; isolation was independently confirmed
via `import typsphinx` resolving to this worktree's own copy before any measurement was taken.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 48-06 can now transcribe `tests/fixtures/xref_whole_document_guard_gate/` directly from
  `48-EXPECTED-STRUCTURE.md` §4 and build its gate module's assertions directly from §2/§3/§5,
  with the honesty caveat about single-page PDF assertions already flagged for its own docstring.
- Plan 48-07's end-to-end re-measurement can re-run the SAME `uv run tox -e docs-pdf` invocation
  pinned in `48-RED-EVIDENCE.md` "Baseline 4" and assert the single expected post-fix number (5)
  recorded in `48-EXPECTED-STRUCTURE.md` §6, subtracted from the 40-annotation baseline.
- No blockers. The one open item carried forward by design (not a defect): sub-population B's 5
  dead file links remain unfixed after this gap closure, by the owner's own recorded policy choice
  — future work reopening this decision should start from `48-EXPECTED-STRUCTURE.md` §6, not
  re-derive the split from scratch.

---
*Phase: 48-compile-time-cross-reference-guard*
*Completed: 2026-08-14*
