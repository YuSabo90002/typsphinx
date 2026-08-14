---
phase: 49-per-master-include-graph-with-state-guarded-includes
plan: 06
subsystem: testing
tags: [sphinx, typst, corpus-gate, numref, figure-numbering, evidence]

# Dependency graph
requires:
  - phase: 49-04
    provides: "typsphinx/translator.py's five module-level derivation
      functions and rewritten visit_toctree(); typsphinx/builder.py's
      _build_include_edge_map()/_master_include_edges -- the composition
      this plan's corpus and numref measurements run against"
  - phase: 49-05
    provides: "tests/test_include_ledger_removal_gate.py; 49-EVIDENCE.md's
      Removal and invariant sweep / No lost diagnostics / Degenerate-shape
      closure / Handoff to Phase 51 and Phase 52 sections"
provides:
  - "49-EVIDENCE.md: two new appended sections -- ## Corpus convergence
    measurement (GATE-02 run unmodified, twice, both green, runtime
    recorded beside Phase 48's baseline) and ## numref measurement (the
    two-case D-01 measurement, extracted values FIRST, reading second)"
  - "tests/fixtures/state_guard_numref_two_case_gate/ and
    tests/test_state_guard_numref_gate.py: the live two-master numref
    fixture and its measurement gate, closing open question #2"
  - "REQUIREMENTS.md: COMP-12 marked Complete -- the last of Phase 49's
    eight requirements"
  - ".planning/todos/pending/2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md:
    the owner-requested tracked todo for the numref divergence,
    resolves_phase 52, naming both the Phase 51 doc obligation and the
    Phase 52 CHANGELOG obligation explicitly"
affects: [51-documentation, 52-changelog]

# Actuals (#2632)
actuals:
  tokens: 11800
  tasks: 3
  commits: 5

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Measurement gate (not assertion gate): tests/test_state_guard_numref_gate.py
      asserts only what is invariant regardless of which way a numbering
      divergence measurement comes out, and separately extracts/prints the
      actual values for the evidence record -- the same pattern D-01 fixed
      in advance (a divergence is documented, not fixed, so the test
      module cannot assert a predicted numbering outcome without
      contradicting its own plan)."
    - "Filler-figure construction to rule out accidental non-divergence:
      only_doc.rst carries one anonymous filler figure before fig-y so
      Typst's own per-compile figure counter and Sphinx's project-wide
      numbering cannot coincide by luck -- the measured divergence (1 vs
      3, not 1 vs 2) is a guaranteed structural consequence of the
      traversal-position difference, not a borderline result a
      differently-ordered fixture might have hidden."

key-files:
  created:
    - tests/fixtures/state_guard_numref_two_case_gate/conf.py
    - tests/fixtures/state_guard_numref_two_case_gate/index.rst
    - tests/fixtures/state_guard_numref_two_case_gate/other_master.rst
    - tests/fixtures/state_guard_numref_two_case_gate/shared_fig_doc.rst
    - tests/fixtures/state_guard_numref_two_case_gate/only_doc.rst
    - tests/fixtures/state_guard_numref_two_case_gate/_static/placeholder.png
    - tests/test_state_guard_numref_gate.py
  modified:
    - .planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EVIDENCE.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "The corpus gate's own runtime came in dramatically faster than Phase
    48's D-11 baseline (mean 14.08s vs. 28.745s pre-fix / 28.065s
    after-guard -- roughly -50% either way), not slower. Recorded as an
    observation per this plan's own instruction (this phase has no
    cost-tier decision of its own; a cost change is recorded, not acted
    on) rather than investigated to exhaustion -- a plausible contributor
    (corpus clone cache warmth, machine-load variance between worktree
    sessions) is named, but the magnitude is a large IMPROVEMENT, so
    D-02's escalation path (which exists for regressions) is not
    triggered regardless of how the gap is explained."
  - "Measured Case (b)'s actual fallback text as the raw target LABEL
    ('fig-y'), not the figure's own caption title ('Figure Y Caption') --
    closing 49-06-PLAN.md's own flagged planner assumption in favour of
    the raw-label reading, per direct read of Sphinx's own
    _resolve_numref_xref()'s contnode substitution."
  - "Measured that Case (b) DOES produce a build warning ('Failed to
    create a cross reference. Any number is not assigned: fig-y'),
    directly contradicting 49-CONTEXT.md D-01's own 'zero warning'
    characterization and 49-EXPECTED-STRUCTURE.md fixture specification
    entry 10's restatement of the same claim. Read directly from Sphinx
    9.1.0's installed source (sphinx/domains/std/__init__.py's
    _resolve_numref_xref, the except ValueError: clause) and reproduced
    in a real build's captured stderr. Recorded as measured, not
    suppressed to match the planning-time hypothesis -- binding
    constraint #6's discipline in reverse: a measured value is not
    amended to match a prediction any more than an expected value may be
    read off an emitter's output."
  - "COMP-12 marked Complete in REQUIREMENTS.md: the unmodified GATE-02
    gate actually ran and passed on this tree (verified twice), so the
    factual precondition the plan's own instruction names is satisfied
    independent of the Task 3 owner-review checkpoint below."

patterns-established:
  - "Recording a divergence between a planning-time hypothesis and a
    measured result as its own finding, without suppressing either side --
    the 'zero warning' claim stays visible in 49-CONTEXT.md/
    49-EXPECTED-STRUCTURE.md as what was believed at plan time, and
    49-EVIDENCE.md records what was actually measured, with an explicit
    note that neither is edited to match the other."

requirements-completed: [COMP-12]

coverage:
  - id: D1
    description: "The full Sphinx doc/ corpus compiles fatal-free through
      the PDF builder under the new per-master state-guarded composition,
      run via the existing GATE-02 gate completely unmodified, twice"
    requirement: "COMP-12"
    verification:
      - kind: integration
        ref: "tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow (2 runs, both PASSED)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The corpus gate's own file carries no diff from this
      plan, and typsphinx/ carries no diff from this plan -- the gate was
      run, not modified, and no production code changed to produce the
      corpus result"
    requirement: "COMP-12"
    verification:
      - kind: other
        ref: "git diff --name-only HEAD -- tests/test_corpus_gate.py (empty); git diff --name-only HEAD -- typsphinx/ (empty)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Open question #2 closes on a live two-master fixture in
      both of its cases, with the extracted reference texts and
      Typst-assigned numbers recorded verbatim before any reading was
      written"
    requirement: null
    verification:
      - kind: integration
        ref: "tests/test_state_guard_numref_gate.py (6 tests, all pass)"
        status: pass
      - kind: other
        ref: "49-EVIDENCE.md ## numref measurement (extracted-values table precedes the Reading section)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The owner reviews the corpus convergence result and its
      cost, and the numref fix-or-document decision (including the
      zero-warning divergence from the planning-time hypothesis), and
      confirms both readings -- Task 3's own blocking checkpoint"
    verification: []
    human_judgment: true
    rationale: "D-02 and ROADMAP binding constraint #5 assign the
      corpus-cost design call to the owner explicitly; D-01's own
      fix-or-document call requires owner confirmation of the recorded
      reading per this plan's checkpoint protocol, regardless of whether
      the measured result is a null finding or a genuine divergence --
      this is not something a test can rubber-stamp. RESOLVED: owner
      responded 'approved' to both items, with the additional instruction
      to file the numref limitation as a tracked pending todo (done --
      see key-files/provides above)."

duration: ~80min
completed: 2026-08-14
status: complete
---

# Phase 49 Plan 06: Corpus Convergence and numref Two-Case Measurement Summary

**Ran the existing GATE-02 full-corpus gate unmodified (both runs green, ~50% faster than Phase 48's baseline), and closed open question #2 by building a live two-master figure-numbering fixture that measures both cases: Case (a) diverges (Sphinx bakes "Fig. 1." into both masters' text while Typst assigns fig-x number 1 in one master and 3 in the other), and Case (b) falls back to the raw label text with a build warning that contradicts D-01's own "zero warning" hypothesis.**

## Performance

- **Duration:** ~80 min (includes the checkpoint round-trip)
- **Started:** ~2026-08-14T09:10:00Z (estimated; provisioning and extensive `<read_first>` reading preceded the first commit)
- **Completed:** 2026-08-14T10:35:00Z
- **Tasks:** 3 of 3 — Task 3 (`checkpoint:human-verify`, `gate="blocking"`) is now RESOLVED: owner responded "approved" to both items, with the additional instruction to file the numref limitation as a tracked pending todo (done)
- **Files modified:** 10 (8 created, 2 modified)

## Accomplishments

- Provisioned the worktree per `CLAUDE.md`'s mandatory protocol (`uv sync --extra dev --extra docs`, since the corpus gate needed no extra beyond dev but the standing green-bar re-measurement benefits from the `docs` extra being present — see "Deviations" below), fixed the NixOS ELF hazard for both `uv` and `ruff` (symlink + `patchelf --set-interpreter`), and confirmed `import typsphinx` resolves to this worktree's own copy before running anything.
- Ran `tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow` completely UNMODIFIED, twice: both runs exited 0 (`14.53s` / `13.63s`), the compiled `sphinx-corpus.pdf` (15,412,931 bytes, valid `%PDF` magic) was independently reproduced and measured, and the unsupported-node catalogue was empty in every build. `git diff --name-only HEAD -- tests/test_corpus_gate.py` and `-- typsphinx/` are both empty for this plan.
- Recorded the corpus runtime beside Phase 48's D-11 baseline: mean `14.08s` vs. `28.745s` (pre-fix) / `28.065s` (after-guard) — roughly `-50%` either way, a large improvement rather than a regression. Stated the green run's own scope honestly: convergence for THIS corpus at THIS version pin, not convergence in general; `PROJECT.md`'s named residual risk stays named.
- Built `tests/fixtures/state_guard_numref_two_case_gate/` exactly to `49-EXPECTED-STRUCTURE.md`'s fixture specification entry 10 (two masters, a figure reachable from both at different traversal positions for Case (a), a figure reachable only from a non-root master for Case (b)), adding one anonymous filler figure ahead of Case (b)'s own figure so the divergence measurement could not coincide with Sphinx's numbering by accident.
- Authored `tests/test_state_guard_numref_gate.py` as a MEASUREMENT gate (asserts only invariants — build succeeds, both PDFs exist, both reference sites render some text, both figures carry some Typst-assigned number — plus a structural gate proving `only_doc` is reachable from no path starting at the root master's own published edge set) and an extraction test that prints the per-case, per-master values for the evidence record.
- Measured and recorded, verbatim, in `49-EVIDENCE.md`'s new `## numref measurement` section (extracted-values table FIRST, reading second, per the plan's own ordering rule): Case (a) — Sphinx bakes `"Fig. 1."` into both masters' reference text; Typst assigns `fig-x` the number `1` in `index`'s own compile (agreeing by coincidence, since it is the only figure there) and `3` in `other_master`'s own compile (diverging, since two figures precede it there). Case (b) — the reference renders as the literal raw label `"fig-y."` (not the caption title, not any number), while Typst still assigns the figure its own number (`2`) in the same compiled PDF; and — contrary to D-01's own "zero warning" hypothesis — the build DOES emit exactly one warning naming the target directly, read from Sphinx 9.1.0's own installed source and reproduced in a real build.
- Applied D-01's fix-or-document decision: both findings are recorded as a documented limitation, handed forward to Phase 51 (documentation) and Phase 52 (CHANGELOG) — not fixed in this phase. No file under `typsphinx/` was touched to produce either measurement.
- Marked COMP-12 Complete in `REQUIREMENTS.md` — the unmodified corpus gate actually ran and passed on this tree, satisfying the plan's own factual precondition for that mark independent of the owner-review checkpoint below.
- Re-measured the standing green bar: full `uv run pytest -q` → **1153 passed, 1 skipped** (see "Deviations" for why the skip count differs from the wave-4/5 baseline of 5 skips), `black --check .`, `ruff check .`, `mypy typsphinx/` all clean.
- **Checkpoint resolved:** owner approved both items (the corpus result and the numref decision, including the "zero warning" correction) with one addition — file the numref limitation as a tracked pending todo. Filed `.planning/todos/pending/2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md` (`resolves_phase: 52`, naming both the Phase 51 doc obligation and the Phase 52 CHANGELOG obligation explicitly in its own body, per the owner's own instruction that closing at 51 alone would let the 52 half go dark).

## Task Commits

Each task was committed atomically:

1. **Task 1: Run the GATE-02 full-corpus gate unmodified and record the result** - `aa56b0d8` (docs)
2. **Task 2: Build the two-case numref fixture, measure both cases, record verbatim** - `e99f526f` (test)
3. **Plan metadata (SUMMARY.md + REQUIREMENTS.md, COMP-12 → Complete)** - `ae9ee37f` (docs)
4. **Task 3: Owner review** - `checkpoint:human-verify`, `gate="blocking"` — RESOLVED (owner: "approved", plus file the numref limitation as a todo)
5. **Todo filed per owner instruction** - `912faf41` (docs: file numref per-master divergence as a tracked todo)
6. **This SUMMARY update recording checkpoint resolution + final green bar** - see commit below

_No TDD tasks (plan `type="execute"`) — each of Tasks 1-2 is its own atomic committed artifact._

## Files Created/Modified

- `tests/fixtures/state_guard_numref_two_case_gate/conf.py` - two-master config, `numfig = True`, load-bearing-properties comment block
- `tests/fixtures/state_guard_numref_two_case_gate/index.rst` - root master, toctrees `shared_fig_doc`, Case (a) reference
- `tests/fixtures/state_guard_numref_two_case_gate/other_master.rst` - orphan master, toctrees `only_doc` then `shared_fig_doc`, both case references
- `tests/fixtures/state_guard_numref_two_case_gate/shared_fig_doc.rst` - `fig-x`, Case (a)'s subject
- `tests/fixtures/state_guard_numref_two_case_gate/only_doc.rst` - filler figure + `fig-y`, Case (b)'s subject, unreachable from root
- `tests/fixtures/state_guard_numref_two_case_gate/_static/placeholder.png` - 1x1 pixel PNG (reused from an existing fixture's own minimal image)
- `tests/test_state_guard_numref_gate.py` - the measurement gate (invariants) + extraction/recording test + reachability structural gate (created)
- `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EVIDENCE.md` - two appended sections: `## Corpus convergence measurement`, `## numref measurement`
- `.planning/REQUIREMENTS.md` - COMP-12 marked Complete
- `.planning/todos/pending/2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md` - owner-requested tracked todo (created, post-checkpoint)

## Decisions Made

See `key-decisions` in frontmatter above. In summary: the corpus gate's dramatically faster runtime (vs. Phase 48's baseline) was recorded as an observation with a named plausible contributor, not investigated to exhaustion, since this plan has no cost-tier decision of its own and the direction is an improvement, not a regression; Case (b)'s fallback text was measured as the raw label (closing the plan's own flagged assumption); and Case (b)'s warning presence was measured to directly contradict D-01's own "zero warning" characterization, recorded as a genuine finding rather than suppressed to match the planning-time text.

## Deviations from Plan

### Auto-fixed Issues

None (Rules 1-4) — no bug fix, missing functionality, blocking fix, or architectural change was required in `typsphinx/` or in test-assertion logic beyond authoring new tests.

**Methodology note (not a Rule 1-4 deviation, recorded for transparency):** this plan's own worktree provisioning used `uv sync --extra dev --extra docs` (per the `<parallel_execution>` guidance, since the corpus gate touches the real PDF pipeline), where prior waves 49-04/49-05 used `--extra dev` only. This makes `myst-parser` available, so the 4 `test_changelog_page_gate.py` tests that were previously SKIPPED (docs-extra-gated) now RUN and PASS instead. Combined with this plan's own 6 new `test_state_guard_numref_gate.py` tests, the full-suite delta from the orchestrator's stated baseline (1143 passed, 5 skipped) to this plan's own close (1153 passed, 1 skipped) is fully accounted for: `1143 + 4 (unskipped, now passing) + 6 (new) = 1153`; `5 - 4 (unskipped) = 1` (the one remaining skip is the pre-existing `TYPSPHINX_CORPUS_REPORT=1`-gated SC#3 test). No test assertion changed and no production code changed to produce this delta — it is purely a consequence of which optional dependency group was installed.

**Measured finding, not a deviation from this plan's own action text (recorded, not corrected):** the numref fixture's own build produces exactly one warning for Case (b), directly contradicting `49-CONTEXT.md` D-01's and `49-EXPECTED-STRUCTURE.md` fixture specification entry 10's own "zero warning" characterization of the fallback. This is exactly the kind of divergence-from-hypothesis the plan's own measurement methodology exists to surface (`49-06-PLAN.md`'s own flagged planner assumption: "Case (b) ... research read the fallback mechanism ... but did not trace exactly what text that node carries"). Recorded verbatim in `49-EVIDENCE.md`, both readings preserved (the plan's own hypothesis, unedited, and the measured fact), per binding constraint #6's discipline applied symmetrically.

---

**Total deviations:** 0 auto-fixed. **Impact on plan:** None — zero scope creep, zero code changes beyond the two new test/fixture files this plan's own frontmatter names.

## Issues Encountered

- **The NixOS ELF hazard (documented standing project hazard, not a deviation)** required its usual remedy before any command could run: `uv` symlinked to its resolved `/nix/store` target, `ruff` fixed via `patchelf --set-interpreter` (the same two-tool remedy 49-02/49-04/49-05 each independently needed).
- **A non-breaking space (`\xa0`) in Typst's own `"Figure N: ..."` caption rendering** (measured directly against this fixture's own `pypdf`-extracted text, not an ASCII space between "Figure" and the number) required the extraction regex to use `\s+` rather than a literal ASCII space — caught immediately by the test module's own first run, fixed before commit, no separate deviation entry warranted (a one-line regex correction inside a test file this plan itself authored, not a pre-existing defect).

## User Setup Required

None - no external service configuration required.

## Checkpoint Resolution

**Task 3 (`checkpoint:human-verify`, `gate="blocking"`) is RESOLVED.** Owner response, verbatim
intent: **approved**, with one addition — "2はapprovedだがtodo化しておいて欲しい" (item 2, the
`:numref:` fix-or-document decision, is approved AND must additionally be filed as a tracked
pending todo). Item 1 (the corpus convergence result and its recorded cost) carried no objection
and no escalation request, and is accepted as recorded.

1. **Corpus convergence result and cost — accepted as recorded, no escalation.** The orchestrator
   additionally reported independent corroboration performed on the main tree (a second GATE-02
   run, and a byte-level diff of the corpus PDF and `.typ` output between the pre-phase commit and
   current HEAD, confirming no content was silently dropped). That corroboration is orchestrator-side
   verification, not new plan scope — it is recorded HERE, in the SUMMARY, as the audit trail for
   why no further action was needed, and is NOT added to `49-EVIDENCE.md`'s own recorded evidence
   (which stays exactly what this plan itself measured).
2. **`:numref:` fix-or-document decision — accepted as recorded, INCLUDING the "zero warning"
   correction, PLUS filed as a tracked todo per the owner's explicit instruction.** The orchestrator
   independently re-read the same Sphinx source lines this plan cited
   (`sphinx/domains/std/__init__.py`'s `_resolve_numref_xref()` `except ValueError:` clause calling
   `logger.warning(...)`, and `sphinx/environment/collectors/toctree.py:373`'s single
   `_walk_doc(env.config.root_doc, ())` call) and confirmed both directly. The todo is filed at
   `.planning/todos/pending/2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`
   with `resolves_phase: 52` (deliberately, since the obligation has two halves — Phase 51
   documentation and Phase 52 CHANGELOG — and closing at 51 alone would let the 52 half go dark;
   both halves are named explicitly in the todo's own `## Solution` section).

No amendment was requested to any recorded evidence. `49-EVIDENCE.md`'s `## Corpus convergence
measurement` and `## numref measurement` sections are exactly as this plan itself measured them,
unmodified by the checkpoint round-trip.

## Standing Green Bar (final, post-checkpoint re-measurement, ROADMAP binding constraint #8)

Pasted verbatim, re-run after the checkpoint resolved (identical to the pre-checkpoint measurement
— no code changed in the interim, only the todo file and this SUMMARY):

```
$ time uv run python -m pytest -q
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a7a7bacfe8f502177
configfile: pyproject.toml
testpaths: tests
plugins: cov-7.1.0
collected 1154 items

tests/test_abbr_pep_separator_render_gate.py ..                          [  0%]
... (full per-file progress omitted for length; every file printed only '.'/'s') ...
tests/test_xref_whole_document_guard_render_gate.py ........             [100%]

================= 1153 passed, 1 skipped in 107.73s (0:01:47) ==================

real	1m48.021s
user	1m37.794s
sys	0m9.086s
```

```
$ uv run black --check .
All done! ✨ 🍰 ✨
294 files would be left unchanged.
```

```
$ uv run python -m ruff check .
All checks passed!
```

```
$ uv run python -m mypy typsphinx/
Success: no issues found in 6 source files
```

`git status --porcelain typsphinx/` prints nothing; `git diff --name-only HEAD -- tests/test_corpus_gate.py`
prints nothing — both invariants hold through the checkpoint round-trip.

## Next Phase Readiness

- **Measured numbers at the end of this plan** (compare against the orchestrator's stated wave-4/5 baseline):
  - `uv run pytest -q` (full suite, `--extra docs` installed): **1153 passed, 1 skipped, 0 failed** (baseline was 1143 passed, 5 skipped with `--extra dev` only — see "Deviations" for the full accounting: +4 previously-docs-gated tests now running+passing, +6 this plan's own new tests, -4 skips correspondingly).
  - `uv run black --check .`: **294 files would be left unchanged** (baseline 292 — the two new files this plan added).
  - `uv run python -m ruff check .`: **All checks passed!**
  - `uv run python -m mypy typsphinx/`: **Success: no issues found in 6 source files** (unchanged — `typsphinx/` carries no diff from this plan).
- `git status --porcelain typsphinx/` printed nothing throughout both tasks — this plan touched zero files under the production package, matching its own scope boundary and `49-EXPECTED-STRUCTURE.md`'s own instruction that no numbering mechanism be added.
- COMP-12 is now marked Complete in `REQUIREMENTS.md` — all eight of Phase 49's requirements (COMP-05 through COMP-12) are Complete. `49-EVIDENCE.md` now carries seven sections total (the five from waves 1/4/5 plus this plan's own two), none overwritten.
- **Phase 49's five success criteria, walked one by one, with the artifact and measurement that discharges each:**
  1. **Defect A closed on generated evidence** — discharged by 49-04 (`test_state_guard_composition_gate.py::TestStateGuardTwoMasterComposition::test_shared_chapter_appears_in_both_masters_pdf`, both PDFs carry `SHARED-CHAPTER-MARKER` exactly once, against the measured pre-fix 0/1 baseline). Not re-verified by this plan; carried forward unchanged.
  2. **The diamond compiles correctly, neighbouring shapes have decided outcomes** — discharged by 49-04/49-05 (`test_state_guard_composition_gate.py`'s diamond test; `49-EVIDENCE.md`'s `## Degenerate-shape closure` table, all 7 rows MATCH). Not re-verified by this plan.
  3. **The traversal matches Sphinx's own selection rule, heading depth follows it** — discharged by 49-04 (`test_state_guard_composition_gate.py::TestStateGuardMirrorPairComposition`, resolved heading levels `[1,2,3]` vs `[1,2,2]` for the two traversal orders). Not re-verified by this plan.
  4. **Prose keeps its position, write-time machinery is gone** — discharged by 49-04 (interleaving, `test_state_guard_composition_gate.py`) and 49-05 (`test_include_ledger_removal_gate.py`'s structural absence gates, proven able to go RED). Not re-verified by this plan.
  5. **Holds at real corpus scale; `:numref:` answered by measurement** — **discharged by THIS plan**: the corpus half by Task 1 (`## Corpus convergence measurement`, two green GATE-02 runs, unmodified gate, empty unsupported-node catalogue, runtime recorded beside Phase 48's baseline with honest scope-stated convergence); the `:numref:` half by Task 2 (`## numref measurement`, both cases measured live, extracted values recorded before the reading, D-01's fix-or-document decision applied — documented limitation, handed to Phase 51/52).
- **No criterion is undischarged.** All five have an artifact and a measurement on the record.
- **Owner review RESOLVED (Task 3, `checkpoint:human-verify`, `gate="blocking"`)**: owner approved both items — (a) the corpus convergence result and its cost, accepted as recorded with no escalation, and (b) the `:numref:` recorded limitation (including the measured "zero warning" correction), accepted as the text Phase 51 documents and Phase 52 announces, with the additional instruction to file it as a tracked pending todo — done, see "## Checkpoint Resolution" above.
- No blockers. This plan's own `autonomous: false` frontmatter's checkpoint requirement is fully discharged.

---
*Phase: 49-per-master-include-graph-with-state-guarded-includes*
*Completed: 2026-08-14*

## Self-Check: PASSED

- FOUND: `tests/fixtures/state_guard_numref_two_case_gate/conf.py`
- FOUND: `tests/test_state_guard_numref_gate.py`
- FOUND: `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-EVIDENCE.md`
- FOUND: `.planning/phases/49-per-master-include-graph-with-state-guarded-includes/49-06-SUMMARY.md`
- FOUND: `.planning/todos/pending/2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`
- FOUND commit: `aa56b0d8`
- FOUND commit: `e99f526f`
- FOUND commit: `ae9ee37f`
- FOUND commit: `912faf41`
