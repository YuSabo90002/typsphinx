---
phase: 37-signature-typography-the-desc-family
plan: 08
subsystem: testing
tags: [gate-evidence, closeout, milestone-invariants, owner-checkpoint, sig-01, sig-02, sig-03, sig-04, sig-05, sig-06, sig-07, sig-08, sig-09, d-11]

# Dependency graph
requires:
  - phase: 37-signature-typography-the-desc-family (plans 01-07, 09 -- all eight prior plans)
    provides: "every SIG-01..09 + D-11 requirement's RED/GREEN evidence, the whole-suite green state, and the four Wave-1 evidence files this plan consolidates"
provides:
  - "37-GATE-EVIDENCE.md: the phase's consolidated closeout record -- milestone invariants verified by command, a 10-row SIG-01..09 + D-11 requirement verdict table, the ROADMAP SC#1..SC#5 mapping (with SC#3's synthetic-fixture reasoning spelled out), the 8-item control roster, and the finalised blast-radius census"
  - "37-TEST-CENSUS.md: finalised against reality -- all predictions checked, plus the census's own honest miss (the two Phase 34 PDF-text goldens 37-09 touched)"
  - "37-VALIDATION.md: fully populated Per-Task Verification Map (23 rows across the eight executed plans), nyquist_compliant/wave_0_complete flipped true after the owner's checkpoint sign-off"
  - "Owner sign-off (2026-08-01, verbatim \"approved\") on the signature block's cosmetic defaults -- discharges RESEARCH.md Assumption A2, the phase's one Manual-Only Verification"
affects: ["v0.7.0 milestone close (Phase 38 depends on Phase 37 being fully closed out)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Reconstruct a real before/after PDF comparison for a phase-closing owner checkpoint by temporarily swapping in the phase-start commit's translator.py, building the fixture, then restoring via `git checkout -- <path>` with a byte-identical diff confirmation before proceeding -- reusable whenever a closeout plan needs a visual before/after and the fixture itself did not exist at the comparison commit."

key-files:
  created:
    - .planning/phases/37-signature-typography-the-desc-family/37-GATE-EVIDENCE.md
    - .planning/todos/pending/2026-08-01-visit-desc-sig-name-docstring-unbalanced-asterisk-warning.md
    - .planning/todos/pending/2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md
  modified:
    - .planning/phases/37-signature-typography-the-desc-family/37-TEST-CENSUS.md
    - .planning/phases/37-signature-typography-the-desc-family/37-VALIDATION.md

key-decisions:
  - "Treated plan 37-09 (the gap-closure plan authored mid-execution, after this plan's own PLAN.md) as a first-class member of the phase throughout the evidence consolidation -- every table (requirement verdict, SC mapping, census) accounts for its commits, its re-derived wrapper text, and its EXPECTED_PAGE_COUNT_PRE_PHASE re-pin, rather than treating it as an afterthought bolted onto a census written before it existed."
  - "Filed two todos rather than fixing two discovered issues inline, because both required editing files outside this plan's own files_modified (37-GATE-EVIDENCE.md, 37-TEST-CENSUS.md, 37-VALIDATION.md): (1) an unbalanced '*' in visit_desc_sig_name's docstring (typsphinx/translator.py) that trips a docutils warning and a stray problematic node in the project's own API docs; (2) EXPECTED_PAGE_COUNT_PRE_PHASE (tests/test_signature_page_boundary_render_gate.py) now holding a post-phase value under a pre-phase name."
  - "Recorded the EXPECTED_PAGE_COUNT_PRE_PHASE re-pin (6->7, from plan 37-09) as a re-derived baseline with its full sweep-data justification in 37-GATE-EVIDENCE.md section 5.2, rather than treating it as a silently-moved goalpost -- per the executor's own honest-verifier standing instruction."
  - "For the Task 3 owner checkpoint, built the phase-start comparison PDF by temporarily overwriting typsphinx/translator.py with the phase-start commit's version, building the still-current-tree fixture (which did not exist at phase start), then restoring via `git checkout -- typsphinx/translator.py` and confirming a byte-identical diff against the committed HEAD version before proceeding -- since the fixture itself is a Phase 37 artifact, a literal `git show <phase-start>:tests/fixtures/...` checkout was not available."

patterns-established:
  - "Phase-closeout PDF-comparison technique (see tech-stack pattern above) for a plan whose owner checkpoint needs a real before/after render of a fixture that did not exist at the 'before' commit."

requirements-completed: []  # No new SIG requirement work -- all nine were already complete from plans 01-07/09; this plan closes out the phase's evidence and gets the owner's sign-off.

# Coverage metadata
coverage:
  - id: D1
    description: "Every gate the default suite does not reach run and captured verbatim: full suite (658 passed/0 failed), the slow-marked full-corpus -b typstpdf gate (1,445 real signatures, unknown_visit catalogue confirmed empty), black/ruff/mypy, and tox -e docs-pdf"
    verification:
      - kind: other
        ref: "37-GATE-EVIDENCE.md section 1 -- verbatim command output for every gate"
        status: pass
    human_judgment: false
  - id: D2
    description: "All four milestone invariants verified by command: zero new runtime dependencies, @preview count still four with no new lockstep site, no new font selection, no new .typ file under typsphinx/"
    verification:
      - kind: other
        ref: "37-GATE-EVIDENCE.md sections 1.5-1.8"
        status: pass
    human_judgment: false
  - id: D3
    description: "A 10-row requirement verdict table (SIG-01..09 + D-11) with a proving test node id, RED commit, GREEN commit, and contract section for every row"
    verification:
      - kind: other
        ref: "37-GATE-EVIDENCE.md section 2"
        status: pass
    human_judgment: false
  - id: D4
    description: "The census, control roster, and prohibition/edge-coverage accounting all account for plan 37-09 as a first-class phase member, with the census's own honest miss (the two Phase 34 goldens) recorded rather than silently absorbed"
    verification:
      - kind: other
        ref: "37-GATE-EVIDENCE.md sections 3-6; 37-TEST-CENSUS.md finalisation section"
        status: pass
    human_judgment: false
  - id: D5
    description: "The owner has looked at a compiled before/after rendering (plus the project's own docs-pdf build) and confirmed the block wrapper introduces no visible artifact beyond the intended spacing"
    verification:
      - kind: other
        ref: "Owner checkpoint response, 2026-08-01: \"approved\" -- see Owner Checkpoint section below"
        status: pass
    human_judgment: true
    rationale: "This is the phase's one genuinely manual-only verification (RESEARCH.md Assumption A2). The verdict is the owner's own judgment, not a mechanical check -- recorded verbatim, not paraphrased."

# Metrics
duration: ~40min
completed: 2026-08-01
status: complete
---

# Phase 37 Plan 08: Phase Closeout — Consolidated Gate Evidence and Owner Sign-Off Summary

**Ran the full-corpus gate and every milestone-invariant check by command, consolidated four Wave-1 evidence files plus plan 37-09's gap-closure evidence into one 10-row SIG-01..09 + D-11 verdict table with an honest accounting of the census's own predictive miss, and obtained the owner's verbatim "approved" sign-off on the signature block's cosmetic defaults — closing Phase 37 out fully green with a documented, owner-confirmed record.**

## Performance

- **Duration:** ~40 min (PLAN_START_TIME not captured at session start; estimated from the first Task 1 commit timestamp)
- **Completed:** 2026-08-01
- **Tasks:** 3 (Task 1 `type="auto"`, Task 2 `type="auto"`, Task 3 `type="checkpoint:human-verify"`)
- **Files modified:** 5 (1 created evidence file, 2 created todos, 2 modified planning docs)

## Accomplishments

- **Task 1 — gates the default suite does not reach:** `uv run pytest -m "not slow" -q` → 658 passed, 0 failed. `uv run pytest tests/test_corpus_gate.py -m slow` → 1 passed, 1 skipped, 13.65s — 1,445 real `desc_signature` nodes from Sphinx v9.1.0's `doc/` corpus compiled through the real pipeline, and the corpus gate's own `unknown_visit` catalogue assertion confirms **zero** new unknown-node warnings from the `desc_sig_*` family. `black`/`ruff`/`mypy` all clean. `tox -e docs-pdf` built and compiled the project's own documentation successfully. All four milestone invariants (zero new deps, `@preview` count still four with no new lockstep site, no new font selection, no new `.typ` under `typsphinx/`) verified by the actual command, not by assertion.
- **Discovered and filed (not fixed inline, out of this plan's `files_modified`):** an unbalanced `*` in `visit_desc_sig_name`'s docstring (added by plan `37-06`) trips a docutils warning and produces a stray `problematic` node in the project's own `docs/_build/pdf/typsphinx.pdf` API reference — filed as a todo.
- **Task 2 — consolidated evidence:** `37-GATE-EVIDENCE.md` now carries a 10-row SIG-01..09 + D-11 requirement verdict table (proving test node id, RED commit, GREEN commit, contract section for every row), the ROADMAP SC#1..SC#5 mapping with SC#3's synthetic-fixture reasoning spelled out explicitly (the corpus does NOT overflow at production width — that is why the RED fixture is synthetic and the corpus case is a non-regression control, not a shortcut), and the 8-item control roster (sibling body-less break, depth-counter trap, nested-optional rendering, explicit-concatenation non-regression, real-corpus width, page-count non-inflation, both rubric assertions, both anchor gates).
- **Finalised `37-TEST-CENSUS.md` against reality:** all 10 Bucket A predictions flipped exactly as predicted, at the plan named as owner; Bucket B (8 files) stayed green throughout; Bucket C (4 conditional node ids) re-verified green after every subsequent wave. Recorded the census's own honest miss: the two Phase 34 PDF-text goldens (`inline_math_pdf_text_mitex.golden.txt`, `inline_math_pdf_text_native.golden.txt`) that plan `37-09` had to hand-update were never predicted by this census, because they predate `37-09`'s own existence and are structurally Phase-34 assets — root-caused (block-vs-inline layout change from D-10) rather than silently folded into Bucket A after the fact.
- **Recorded the `EXPECTED_PAGE_COUNT_PRE_PHASE` re-pin (6→7) as a re-derived baseline, not a moved goalpost:** `37-GATE-EVIDENCE.md` section 5.2 carries the full sweep-data justification (the page count only crosses from 6 to 7 between 0.85em and 0.9em of added spacing on this deliberately adversarial-page-height fixture — specific to how much room ONE `sticky: true` keep-together unit needs, not a per-signature inflation that would compound). Filed the naming nit (the constant's own name no longer describes its post-phase value) as a todo rather than renaming a test file outside this plan's scope.
- **Populated `37-VALIDATION.md`'s Per-Task Verification Map with 23 rows** — one per task across all eight executed plans (`37-01`..`37-07`, `37-09`) — and checked off all five Wave 0 Requirements as delivered and later flipped green.
- **Task 3 — owner checkpoint:** built the current-state PDF (`/tmp/sig37/index.pdf`, 108,410 bytes, 4 pages) and, since the fixture itself did not exist at the phase-start commit, reconstructed a real phase-start comparison by temporarily overwriting `typsphinx/translator.py` with the phase-start commit's version, building the fixture with it, then restoring the file via `git checkout -- typsphinx/translator.py` and confirming a byte-identical diff against the committed HEAD version before proceeding (`/tmp/sig37-before/index.pdf`, 71,308 bytes, 4 pages). Both PDFs plus the project's own `tox -e docs-pdf` output (`docs/_build/pdf/typsphinx.pdf`) were presented to the owner in the checkpoint, focused specifically on RESEARCH.md Assumption A2 — the block wrapper's **non-spacing** cosmetic defaults (`inset`, `fill`, `stroke`) — since spacing itself had already been shown to and approved by the owner during `37-09`'s own gap-closure decision.

## Owner Checkpoint

**Task:** Owner visual confirmation of the signature block's cosmetic defaults (RESEARCH.md Assumption A2).

**What was shown:** `/tmp/sig37-before/index.pdf` (phase-start, commit `011b926`), `/tmp/sig37/index.pdf` (current), and `docs/_build/pdf/typsphinx.pdf` (the project's own API reference pages, from this plan's own `tox -e docs-pdf` run). Both fixture PDFs are 4 pages; page 3 is the signature-dense page. The orchestrator additionally recorded two objective findings alongside the checkpoint as narrowing evidence (not a substitute for the owner's own judgment): all 13 emitted signature wrappers are `block(sticky: true, par(hanging-indent: 2.5em, …))` with no `inset`/`fill`/`stroke`/`radius` argument, and no `set block(...)` or `show block:` rule exists anywhere in `typsphinx/templates/`, `typsphinx/*.py`, or the emitted `.typ`/`_template.typ` — so Typst's own `block` defaults (`fill: none`, `stroke: none`, `inset: 0pt`) apply unmodified.

**Owner's verbatim response (2026-08-01):**

```
approved
```

This is the owner's complete, literal response — recorded exactly, not paraphrased or embellished.

**Not auto-approved.** `workflow.auto_advance` was not used to skip this checkpoint. The executor halted at Task 3, returned the structured checkpoint block, and this record was written only after the owner's actual response was relayed back.

**Discharge:** `37-VALIDATION.md`'s "Manual-Only Verifications" row (D-10 / Assumption A2) is marked discharged, dated 2026-08-01, with the verdict "approved" recorded verbatim. `nyquist_compliant` and `wave_0_complete` flipped `true` — every other Validation Sign-Off box was already checked in the prior (Task 2) commit; this was the last outstanding item.

## Task Commits

1. **Task 1: Run the gates the default suite does not reach, verify the milestone invariants** — `a637c41` (docs)
2. **Task 2: Consolidate the evidence, finalise the census, build the requirement verdict table** — `457da09` (docs)
3. **Task 3: Owner visual confirmation of the signature block's cosmetic defaults** — `4116a88` (docs)

_No `feat`/`fix` commits — this plan is evidence-consolidation and closeout only; no production code was touched (`typsphinx/translator.py` was temporarily overwritten and restored during Task 3's checkpoint preparation, confirmed byte-identical to the committed state before any further action)._

## Files Created/Modified

- `.planning/phases/37-signature-typography-the-desc-family/37-GATE-EVIDENCE.md` — created: the phase's consolidated closeout record
- `.planning/phases/37-signature-typography-the-desc-family/37-TEST-CENSUS.md` — finalised against reality with a predicted-vs-actual reconciliation section
- `.planning/phases/37-signature-typography-the-desc-family/37-VALIDATION.md` — Per-Task Verification Map populated (23 rows), Wave 0 Requirements checked off, Manual-Only Verification discharged, `nyquist_compliant`/`wave_0_complete` flipped `true`
- `.planning/todos/pending/2026-08-01-visit-desc-sig-name-docstring-unbalanced-asterisk-warning.md` — created
- `.planning/todos/pending/2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md` — created

## Decisions Made

See `key-decisions` in frontmatter. Summary:
- Treated `37-09` as a first-class phase member throughout, not an afterthought bolted onto a pre-existing census.
- Filed two todos rather than fixing discovered issues inline, since both required editing files outside this plan's `files_modified`.
- Recorded the `EXPECTED_PAGE_COUNT_PRE_PHASE` re-pin with its full sweep-data justification rather than treating it as a silently-moved goalpost.
- Reconstructed a real phase-start PDF comparison for the owner checkpoint via a temporary `translator.py` swap + `git checkout --` restore, since the fixture itself post-dates the phase-start commit.

## Deviations from Plan

### Auto-fixed Issues

None in the Rule 1/2/3 sense — no bugs, missing critical functionality, or blocking issues were silently patched. Two Rule-2-adjacent discoveries were made and handled by filing todos (see above) rather than by inline fixes, since both required touching files outside this plan's own `files_modified` (`.planning/phases/37-signature-typography-the-desc-family/37-GATE-EVIDENCE.md`, `37-TEST-CENSUS.md`, `37-VALIDATION.md`):

**1. [Discovered, filed] Unbalanced `*` in `visit_desc_sig_name`'s docstring**
- **Found during:** Task 1's `tox -e docs-pdf` run.
- **Issue:** The docstring phrase `"PyTypeObject *type, no intersphinx"` (added by plan `37-06`) contains a bare `*` that docutils parses as an unterminated inline-emphasis marker, producing a docs-build warning and a stray `problematic` node in the compiled API reference.
- **Fix:** Not applied inline — `typsphinx/translator.py` is not in this plan's `files_modified`. Filed `.planning/todos/pending/2026-08-01-visit-desc-sig-name-docstring-unbalanced-asterisk-warning.md`.
- **Verification:** Confirmed via `tox -e docs-pdf`'s own warning output; confirmed the corresponding node type doesn't affect any Phase 37 test assertion.

**2. [Discovered, filed] `EXPECTED_PAGE_COUNT_PRE_PHASE` now holds a post-phase value**
- **Found during:** Task 2, while finalising the census and requirement verdict table.
- **Issue:** Plan `37-09` correctly re-pinned this constant from 6 to 7, but its own name still says "PRE_PHASE."
- **Fix:** Not applied inline — the constant lives in `tests/test_signature_page_boundary_render_gate.py`, outside this plan's `files_modified`. Filed `.planning/todos/pending/2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md`.
- **Verification:** N/A — pure naming hygiene, no behavior at stake; the existing code comment already prevents actual confusion about the value's provenance.

---

**Total deviations:** 2 discovered-and-filed (both process/scope, both handled by todo rather than inline fix per the scope fence).
**Impact on plan:** None on the delivered evidence — both findings are recorded transparently in `37-GATE-EVIDENCE.md` itself, not silently omitted.

## Issues Encountered

- **Worktree environment provisioning (NixOS sandbox):** the worktree's fresh `uv sync --extra dev` installed generic-linux ELF `uv`/`ruff` binaries incompatible with the NixOS sandbox's dynamic linker. Resolved per the documented pattern: symlinked the main checkout's Nix-store `uv` (via `command -v uv`) and the main `.venv`'s `ruff` into the worktree's `.venv/bin/`. No project file changed; pure environment setup.
- **Worktree-safety-checker rejected the compound `env -u ... uv sync` command** used in the plan's own `<environment_setup>` block ("too complex to verify that it stays inside the worktree"). Resolved with the documented `unset` workaround (same pattern used by prior plans in this phase).
- **Reconstructing the phase-start comparison PDF** required a temporary `typsphinx/translator.py` swap since the fixture itself is a Phase 37 artifact with no phase-start equivalent to check out directly. Handled carefully: content saved before overwrite, restored via `git checkout --` immediately after the comparison build, and the restore was confirmed byte-identical via `diff` before any further git operation — no risk to the committed state.

## User Setup Required

None — this plan's remaining "setup" was the owner's own visual review, which is complete (see Owner Checkpoint above).

## Next Phase Readiness

- **Phase 37 is fully closed out.** Every SIG-01..09 + D-11 requirement is green with recorded RED provenance and a contract section; all four milestone invariants verified by command; the full-corpus gate green; the owner's sign-off obtained and recorded verbatim.
- `37-GATE-EVIDENCE.md`, `37-TEST-CENSUS.md`, and `37-VALIDATION.md` are the phase's final evidence trio — the four `37-GATE-EVIDENCE-01..04.md` files and `37-GATE-EVIDENCE-09.md` remain in place as the primary per-wave record.
- Two todos were filed for follow-up (both low-priority hygiene, neither blocking): the docstring-asterisk docs-build warning, and the `EXPECTED_PAGE_COUNT_PRE_PHASE` naming nit.
- No blockers for Phase 38 (Structural Indentation + Info Fields), which depends on Phase 37's `desc_signature` shape being finalized — it is.
- STATE.md and ROADMAP.md are **not** updated by this plan (worktree mode) — the orchestrator owns those writes centrally after this wave merges.

## Known Stubs

None — this plan is evidence consolidation and documentation only; no placeholder or empty-value stub was introduced anywhere.

## Threat Flags

None — this plan touched only `.planning/` documentation and two `.planning/todos/pending/` files. The one production-code file that was touched (`typsphinx/translator.py`, temporarily, during Task 3's checkpoint preparation) was restored to its exact committed state via `git checkout --` before any commit was made, confirmed byte-identical by `diff`. No new escaping, network, file, subprocess, or dependency surface was introduced.

## Self-Check: PASSED

- `.planning/phases/37-signature-typography-the-desc-family/37-GATE-EVIDENCE.md` - FOUND
- `.planning/phases/37-signature-typography-the-desc-family/37-TEST-CENSUS.md` - FOUND, contains the finalisation section
- `.planning/phases/37-signature-typography-the-desc-family/37-VALIDATION.md` - FOUND, `nyquist_compliant: true` / `wave_0_complete: true`
- `.planning/todos/pending/2026-08-01-visit-desc-sig-name-docstring-unbalanced-asterisk-warning.md` - FOUND
- `.planning/todos/pending/2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md` - FOUND
- `typsphinx/translator.py` - confirmed byte-identical to committed HEAD state (no residual modification from the Task 3 comparison build)
- Commit `a637c41` (Task 1) - FOUND in `git log`
- Commit `457da09` (Task 2) - FOUND in `git log`
- Commit `4116a88` (Task 3) - FOUND in `git log`

---
*Phase: 37-signature-typography-the-desc-family*
*Completed: 2026-08-01*
