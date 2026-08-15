---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
plan: 14
subsystem: builder
tags: [dead-code-deletion, requirements-bookkeeping, pytest, black, mypy, ruff]

# Dependency graph
requires:
  - phase: 47-12
    provides: "the WR-01 disposition precedent (writer.py::_resolve_entry_element() deleted, tests retargeted, module docstring records the deletions) this plan mirrors one file over"
  - phase: 47-13
    provides: "BLD-03's fifth-site predicate wiring, closing the BLOCKER that kept 47-VERIFICATION.md at gaps_found; this plan's BLD-02 checkbox flip and WR-01 (new) deletion are the two remaining non-blocking obligations that verification report left open"
provides:
  - "typsphinx/builder.py with exactly one target-normalization route (_resolve_target_stem()/_wrapper_output_relpath()); the superseded docname-first-match _resolve_output_stem() is gone, with zero remaining references anywhere in typsphinx/"
  - "tests/test_builder_output_stem.py retargeted onto the live resolvers -- 21 tests onto _resolve_target_stem(docname, target), 1 onto _wrapper_output_relpath(entry), 3 deleted with rationale recorded in the module docstring, 3 left unchanged with docstring corrections (28 -> 25 collected tests)"
  - ".planning/REQUIREMENTS.md with BLD-02 correctly checked (9/10 Phase 47 requirements now [x]; BLD-03 still open pending /gsd-verify-phase 47 re-measurement of 47-13's fix)"
affects: []

actuals:
  tokens: 9400
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Dead-code deletion over retention-with-docstring, applied a second time in the same phase: a superseded implementation with zero production call sites is deleted, not annotated, because a green 28-test suite over an unreachable code path reports false confidence -- the exact WR-01 disposition 47-12 gave the writer-side sibling, applied here to the builder-side twin."
    - "Production code carries zero references (even historical) to a deleted symbol; test files may retain historical framing naming the removal point. Confirmed against 47-12's own precedent (typsphinx/writer.py has zero _resolve_entry_element mentions; historical mentions survive only in tests/) before finalizing this plan's docstring edits -- an early draft left two historical mentions inside typsphinx/builder.py itself and both were reworked to state the same substance positively, with no reference to the deleted name."
    - "Bookkeeping-tool fallback: when gsd-tools.cjs is unreachable from a worktree (no .claude/ directory, not on PATH), the plan's mandated direct-edit fallback is taken and the mechanism used is recorded in the summary."

key-files:
  created: []
  modified:
    - typsphinx/builder.py
    - tests/test_builder_output_stem.py
    - tests/test_two_layer_output_gate.py
    - tests/test_corpus_gate.py
    - tests/fixtures/entry_title_author_render_gate/conf.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "DELETE, not retain-with-docstring: _resolve_output_stem() removed entirely from typsphinx/builder.py per the plan's locked decision -- it had zero production call sites, and the docname first-match search it performed is wrong for D-04's repeated-docname-different-target case, which is why _wrapper_output_relpath() was written to bypass it in the first place."
  - "Zero references left in typsphinx/, even historical: two docstrings I drafted first (in _resolve_target_stem() and _wrapper_output_relpath()) named the deleted method as history (\"was deleted in Phase 47 Plan 14\"). Checked against 47-12's own precedent -- typsphinx/writer.py has zero mentions of the deleted _resolve_entry_element(), historical or otherwise, per 47-REVIEW.md's own confirmation (\"no dangling references anywhere in typsphinx/ (only historical/comment references survive in test docstrings\") -- and reworked both to state the same substance positively with no reference to the deleted name at all, matching that precedent exactly."
  - "Task 2 mechanism: direct edit, not gsd-tools.cjs. Resolution was attempted in order (no .claude/ directory exists under this worktree root, gsd-tools not on PATH, RUNTIME_DIR unset) and none resolved -- identical finding to 47-12's Task 2 -- so the plan's mandated fallback was taken."
  - "For the two acceptance-criteria literal-string counts (>= 3 for \"v1.2-manual\", >= 2 for マニュアル), two retargeted tests intentionally keep a two-line form (a `target = \"...\"` variable line plus the assert) rather than a single merged line, because grep -c counts matching LINES not occurrences -- a single line containing the literal string twice only counts once. This preserves the baseline literal-occurrence count exactly (3 and 2 respectively) without changing any expected value."

requirements-completed: [BLD-02]
# NOTE: the plan's own frontmatter lists `requirements: [OUT-01, OUT-02, BLD-02]`,
# but OUT-01/OUT-02 were already checked off by 47-12 (their unit-level
# evidence is merely re-anchored here onto the live resolver, not newly
# satisfied). Task 2's own action explicitly forbids checking BLD-03 in
# this plan. BLD-02 is the only ID this plan's Task 2 actually flips.

coverage:
  - id: D1
    description: "The superseded docname-first-match output-stem resolver (_resolve_output_stem) is deleted from typsphinx/builder.py; _resolve_target_stem()/_wrapper_output_relpath() are the sole production output-path resolution routes"
    verification:
      - kind: unit
        ref: "git grep -c '_resolve_output_stem' -- 'typsphinx/' (0 matches)"
        status: pass
      - kind: unit
        ref: "uv run python -c \"from typsphinx.builder import TypstBuilder; print(hasattr(TypstBuilder, '_resolve_output_stem'))\" -> False"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every semantic that survives the deletion is retargeted onto _resolve_target_stem()/_wrapper_output_relpath() in tests/test_builder_output_stem.py with expected values verbatim; the three dead semantics are deleted with rationale recorded in the module docstring"
    verification:
      - kind: unit
        ref: "tests/test_builder_output_stem.py --collect-only -> 25 collected (28 before, 3 deleted); grep -c 'def test_resolve_target_stem' -> 21; grep -c 'def test_wrapper_output_relpath_accepts_five_element_tuple' -> 1"
        status: pass
      - kind: unit
        ref: "grep -c '\"v1.2-manual\"' -> 3 (>= 3 required); grep -c 'マニュアル' -> 2 (>= 2 required) -- expected values carried over verbatim"
        status: pass
      - kind: unit
        ref: "grep -cE 'def test_resolve_target_stem_guards_(parent_traversal|absolute_target|drive_qualified_target)' -> 3, all expecting \"manual\""
        status: pass
    human_judgment: false
  - id: D3
    description: "No tracked docstring/comment/test prose outside .planning/ still presents the deleted resolver as live code; typsphinx/ (production code) carries zero references at all, even historical"
    verification:
      - kind: unit
        ref: "git grep -c '_resolve_output_stem' -- 'typsphinx/' -> 0 matches (all 7 surviving docstring/comment sites repaired); git grep -c '_resolve_output_stem' -- ':!.planning' -> 9 matches, all in tests/ or tests/fixtures/, all explicitly framed as history naming this plan (47-14) as the removal point -- matching 47-12's own verified precedent that historical mentions survive only in test files, never in typsphinx/ itself"
        status: pass
    human_judgment: false
  - id: D4
    description: "AST-level diff over builder.py's surviving methods proves only the deleted method's body and prose (docstrings/comments) changed -- no other executable line was touched"
    verification:
      - kind: unit
        ref: "ast.dump() comparison (docstring node stripped) of _resolve_target_stem, _escapes_outdir, _is_drive_qualified, _collision_key, _validate_output_path_collisions, _content_output_path, _wrapper_output_relpath, _compute_master_included_docnames against HEAD~1 -- all 8 report UNCHANGED"
        status: pass
    human_judgment: false
  - id: D5
    description: ".planning/REQUIREMENTS.md's BLD-02 checkbox and phase-mapping row flip to [x]/Complete; BLD-03 stays [ ]/Pending; no other requirement ID or text is touched"
    verification:
      - kind: unit
        ref: "Task 2 <acceptance_criteria> -- all 6 checks pass (BLD-02 checked, BLD-03 unchecked, 8 other IDs undisturbed, both phase-mapping rows correct, diff-shape check returns 0, numstat shows exactly 2+/2-)"
        status: pass
    human_judgment: false
  - id: D6
    description: "Full suite, black --check, mypy typsphinx/, and ruff check (via nix-shell fallback) all green; the five named regression modules pass with zero source diff on the four that must stay unmodified"
    verification:
      - kind: unit
        ref: "uv run pytest -q -> 1039 passed, 5 skipped; uv run black --check . -> clean; uv run mypy typsphinx/ -> Success; nix-shell -p ruff --run 'ruff check .' -> All checks passed (uv-managed ruff is a generic-linux ELF unrunnable on this NixOS checkout, the pre-existing documented limitation)"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-08-12
status: complete
---

# Phase 47 Plan 14: WR-01 Dead-Code Deletion and BLD-02 Bookkeeping Closure Summary

**Deleted the superseded docname-first-match `TypstBuilder._resolve_output_stem()` from `typsphinx/builder.py` (WR-01, mirroring 47-12's deletion of the writer-side sibling), retargeted its 22 surviving semantics onto the live `_resolve_target_stem()`/`_wrapper_output_relpath()` resolvers with expected values verbatim, and flipped `BLD-02`'s requirement checkbox while leaving `BLD-03` open for the next re-verification.**

## Performance

- **Duration:** ~50 min
- **Started:** 2026-08-12 (worktree provisioning + Task 1)
- **Completed:** 2026-08-12
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- `typsphinx/builder.py::TypstBuilder._resolve_output_stem()` — a fully-documented, extensively-tested docname-based first-match lookup with **zero production call sites** — is gone. `_resolve_target_stem()` (called directly, per entry, via `_wrapper_output_relpath()`) is now the sole target-normalization route in the package.
- `tests/test_builder_output_stem.py` retargeted: 21 of 28 original tests converted to call `_resolve_target_stem(docname, target)` directly instead of pre-loading `builder.config.typst_documents` and calling the deleted search; 1 test (the five-element-tuple case) retargeted onto `_wrapper_output_relpath(entry)` and renamed since it is an entry-shape property, not a target-normalization one; 3 tests whose semantic existed only because the deleted method's docname SEARCH could fail to match (two search-shaped fallbacks, plus one asserting a contract BLD-03 deliberately reversed) were deleted, with the rationale for each recorded in the module docstring. Net: 28 → 25 collected tests, exactly 3 lower.
- Seven stale docstring/comment sites in `typsphinx/builder.py` repaired so none presents the deleted method as live code, including `47-REVIEW.md`'s IN-01 finding (`_is_drive_qualified()`'s docstring naming the wrong caller). `typsphinx/` now has **zero** references to `_resolve_output_stem`, even historical ones — verified against 47-12's own precedent that historical framing belongs only in test files.
- Three prose sweeps outside the resolver's own module: `tests/test_corpus_gate.py`'s comment now names `_resolve_target_stem` (via `_wrapper_output_relpath`); `tests/test_two_layer_output_gate.py`'s pre-fix description now reads unambiguously as history naming this plan; the `entry_title_author_render_gate` fixture's `conf.py` comment gained the parallel note that the builder-side method was deleted here, alongside its existing writer-side note naming `47-12-PLAN.md`.
- `.planning/REQUIREMENTS.md`'s `BLD-02` checkbox and phase-mapping row flipped from `[ ]`/`Pending` to `[x]`/`Complete`, matching `47-VERIFICATION.md`'s Requirements Coverage table. `BLD-03` deliberately left `[ ]`/`Pending` — it is blocked on `/gsd-verify-phase 47` re-measuring `47-13`'s fix, not this plan's to check.
- Full suite (1039 passed / 5 skipped / 0 failed), `black --check .`, `mypy typsphinx/`, and `ruff check .` (via `nix-shell -p ruff` fallback — the uv-managed ruff binary is a generic-linux ELF unrunnable on this NixOS checkout, a pre-existing documented limitation) all green. AST-level diff confirms every surviving method's executable body is byte-identical to before this plan.

## Task Commits

Each task was committed atomically:

1. **Task 1: Delete the dead output-stem resolver, retarget its surviving coverage onto the live resolvers, and sweep the tracked tree** — `2a82454` (feat)
2. **Task 2: Flip BLD-02's requirement checkbox and phase-mapping row, leaving BLD-03 open** — `8146916` (docs)

_No plan-metadata commit from this executor — worktree mode; the orchestrator makes the shared-file/final metadata commit after merge._

## Files Created/Modified

- `typsphinx/builder.py` — Deleted `_resolve_output_stem()` (method body + docstring, 42 lines); repaired `_is_drive_qualified()`'s docstring (IN-01), `_resolve_target_stem()`'s own docstring, `get_target_uri()`'s docstring, `_content_output_path()`'s docstring, `_wrapper_output_relpath()`'s docstring, and both `TypstPDFBuilder.finish()` comments so none names the deleted method — all seven repaired to state their substance positively, with **zero** remaining reference to the deleted name anywhere in this file
- `tests/test_builder_output_stem.py` — Retargeted 21 tests onto `_resolve_target_stem()`, 1 onto `_wrapper_output_relpath()` (renamed `test_wrapper_output_relpath_accepts_five_element_tuple`); deleted 3 search-shaped/BLD-03-reversed tests; 3 tests left byte-identical in body with docstring corrections; module docstring rewritten to record all three deletions with reason and surviving-coverage pointer, and to name what now carries OUT-01/OUT-02's unit-level evidence
- `tests/test_two_layer_output_gate.py` — One docstring passage (line ~91) rewritten to read unambiguously as history, naming this plan (47-14) as the removal point
- `tests/test_corpus_gate.py` — One comment (line ~328) corrected to name `_resolve_target_stem`/`_wrapper_output_relpath` as the live mechanism
- `tests/fixtures/entry_title_author_render_gate/conf.py` — One comment corrected to add the builder-side deletion note alongside its existing writer-side note
- `.planning/REQUIREMENTS.md` — Flipped `BLD-02` from `[ ]` to `[x]` in both the v1 checkbox list and the phase-mapping table; `BLD-03` left `[ ]`/`Pending`; all other IDs (`COMP-01..04`, `OUT-01..03`, `BLD-04`) untouched; coverage tally line unchanged

## Decisions Made

- **DELETE over retention-with-docstring** (locked in the plan, executed here): `_resolve_output_stem()` removed entirely rather than kept as a documented-but-dead function, mirroring 47-12's disposition of the writer-side sibling one file over.
- **Zero references, even historical, inside `typsphinx/`**: two docstring drafts (in `_resolve_target_stem()` and `_wrapper_output_relpath()`) initially named the deleted method as history ("deleted in Phase 47 Plan 14"). Cross-checked against `typsphinx/writer.py`, which — per `47-12-SUMMARY.md` and `47-REVIEW.md`'s own confirmation — carries **zero** mentions of the deleted `_resolve_entry_element()`, historical or otherwise; only test files retain historical framing. Both drafts were reworked to state the same substance without naming the deleted method at all, matching that verified precedent exactly (Rule 1 — self-caught inconsistency during the sweep, corrected before commit, no separate commit needed).
- **Task 2 mechanism: direct edit** (plan's mandated fallback). `gsd-tools.cjs` was not resolvable from this worktree — no `.claude/` directory exists under the worktree root, `gsd-tools` is not on `PATH`, and `RUNTIME_DIR` is unset — identical to 47-12's own Task 2 finding. The checkbox and table-row edits were made directly with the Edit tool.
- **Two-line form for two literal-count acceptance criteria**: `test_resolve_target_stem_preserves_period_in_stem` and `test_resolve_target_stem_preserves_non_ascii_target` use a `target = "..."` variable line followed by the assert, rather than a single merged call line, specifically to preserve the baseline literal-string occurrence counts (`grep -c` counts matching lines, not occurrences) that the plan's acceptance criteria check mechanically. No expected value changed.
- **`ruff` via `nix-shell -p ruff` fallback**: `uv run ruff check .` fails on this NixOS environment (pre-existing, documented `ruff-generic-linux-elf-unrunnable-on-nixos` limitation). Ran `nix-shell -p ruff --run "ruff check ."` instead, which passed clean.

## Deviations from Plan

None — plan executed exactly as written. The docstring self-correction described above (dropping historical mentions of the deleted method from `typsphinx/builder.py` itself) was caught and fixed during Task 1's own sweep, before the task's verification pass or commit — it is not a deviation from the plan's action (which explicitly offered "drop the contrast entirely ... either is acceptable" as one of the two sanctioned options for exactly this docstring), just the specific option chosen after checking the established precedent.

## Issues Encountered

- `uv run ruff check .` cannot execute in this worktree's NixOS sandbox (`Could not start dynamically linked executable: ruff`) — the same pre-existing, already-acknowledged environmental limitation as 47-11/47-12/47-13 (`.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`; STATE.md Deferred Items: "Does not block SC#3, which takes lint authority from CI"). Worked around with `nix-shell -p ruff --run "ruff check ."`, which passed clean.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- WR-01 (new, from `47-REVIEW.md`) has a concrete disposition on disk: the builder-side dead resolver is gone, not annotated, exactly mirroring how 47-12 closed the writer-side sibling. No test in the suite can report confidence in a code path no real build reaches.
- OUT-01's and OUT-02's unit-level evidence is re-anchored onto `_resolve_target_stem()`/`_wrapper_output_relpath()` and explicitly named in the module docstring, so the next verification pass has a citation that does not dangle.
- `.planning/REQUIREMENTS.md` now shows 9/10 Phase 47 requirements `[x]`, with `BLD-03` still visibly open pending `/gsd-verify-phase 47` re-measuring `47-13`'s fifth-site predicate wiring fix.
- No blockers for the next phase. This plan touched no runtime behavior — Task 1 removed unreachable code and retargeted its tests (AST-diff confirms every surviving method's executable body is byte-identical); Task 2 edited a planning document.
- With both `47-13` (BLD-03's fix) and `47-14` (WR-01's deletion + BLD-02's bookkeeping) landed, Phase 47's remaining open item is a fresh `/gsd-verify-phase 47` pass to confirm the fifth-site predicate wiring closes gap 9b/CR-01 and to flip `BLD-03`'s checkbox on that measured evidence.

---
*Phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis*
*Completed: 2026-08-12*

## Self-Check: PASSED

All modified files confirmed present on disk: `typsphinx/builder.py`,
`tests/test_builder_output_stem.py`, `tests/test_two_layer_output_gate.py`,
`tests/test_corpus_gate.py`,
`tests/fixtures/entry_title_author_render_gate/conf.py`,
`.planning/REQUIREMENTS.md`. Both task commit hashes (`2a82454`, `8146916`)
confirmed present in `git log --oneline --all`.
