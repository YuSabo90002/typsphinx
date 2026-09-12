---
phase: 68-documentation-follow-through-claude-md-tox-ini-flake-nix
plan: 02
subsystem: docs
tags: [tox, tox-uv, packaging, pytest, ast-hash, documentation]

# Dependency graph
requires:
  - phase: 65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves
    provides: the tox-uv~=1.35 revert this plan's comment now describes
provides:
  - tox.ini's requires comment rewritten to describe the landed tox-uv pin, with
    the SpecifierSet equivalence re-measured in-plan (the old SUMMARY citation no
    longer exists in the repository)
  - tests/test_toolchain_config_gate.py's D-13 docstring and assert-message tail
    moved to the post-Phase-68 state
  - tests/test_pdf_render_gate.py's D-14 docstring sentence added, noting the
    tox-uv revert and the Phase 64 FHS shims
affects: [68-04]

# Actuals (#2632)
actuals:
  tokens: 5013
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Historical fact kept, current-reasoning added idiom applied to tox.ini's requires comment"

key-files:
  created:
    - .planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-TOX-EVIDENCE.md
  modified:
    - tox.ini
    - tests/test_toolchain_config_gate.py
    - tests/test_pdf_render_gate.py

key-decisions:
  - "Cited evidence in archive-stable form (v0.9.3 Phase NN, filename) rather than a .planning/phases/... path, per D-09, since that directory moves at /gsd-complete-milestone."
  - "Re-measured the ~=1.35 / >=1.35,<2 SpecifierSet equivalence directly in this plan (SPECIFIER_EQUIV = True over an 11-version sample) since the old citation named a SUMMARY file that no longer exists in the repository."

requirements-completed: []  # DOC-20 closes in 68-04 on the merged tree (D-15 repo-wide grep classification)

coverage:
  - id: D1
    description: "tox.ini's requires comment describes the current tox-uv~=1.35 pin, the full ini-parser constraint, why tox-uv is safe under the Phase 64 FHS shims, and a short tox-uv-bare history"
    requirement: DOC-20
    verification:
      - kind: other
        ref: "68-TOX-EVIDENCE.md § tox.ini rewrite — tox config -e py312 --core -k requires read-back, sha256 byte-fence, required-token grep"
        status: pass
    human_judgment: false
  - id: D2
    description: "tests/test_toolchain_config_gate.py's D-13 docstring and assert-message tail moved to the post-Phase-68 state, text only"
    requirement: DOC-20
    verification:
      - kind: unit
        ref: "tests/test_toolchain_config_gate.py::test_dev_extra_pins_tox_uv_not_tox_uv_bare"
        status: pass
      - kind: other
        ref: "68-TOX-EVIDENCE.md § test_toolchain_config_gate.py strings — masked AST hash equality vs base"
        status: pass
    human_judgment: false
  - id: D3
    description: "tests/test_pdf_render_gate.py's _run_sphinx_build_typst docstring gains one sentence describing the tox-uv revert and Phase 64 FHS shims, between the QUA-04 sentence and the closing reasoning"
    requirement: DOC-20
    verification:
      - kind: other
        ref: "68-TOX-EVIDENCE.md § test_pdf_render_gate.py sentence — docstring order check, masked AST hash equality vs base"
        status: pass
    human_judgment: false

duration: 13min
completed: 2026-09-12
status: complete
---

# Phase 68 Plan 02: tox.ini and Test-File tox-uv-bare Rationale Rewrite Summary

**Replaced every current-tense `tox-uv-bare` rationale in `tox.ini` and two test files with text describing the landed `tox-uv~=1.35` pin, re-measuring the old `SpecifierSet` equivalence claim in place of a citation to a SUMMARY file that no longer exists — zero executable change, proven by masked-AST-hash equality and unchanged pytest pass/collect counts.**

## Performance

- **Duration:** 13 min
- **Started:** 2026-09-12T15:47:56Z
- **Completed:** 2026-09-12T16:01:13Z
- **Tasks:** 3
- **Files modified:** 3 (plus 1 evidence file created)

## Accomplishments
- `tox.ini`'s `requires` comment (old lines 4-10) rewritten: states the current `tox-uv~=1.35` pin, the full ini-list-loader comma-splitting constraint, why `tox-uv` is safe again under the Phase 64 FHS shims, a short `tox-uv-bare` history, and archive-stable citations (v0.9.3 Phase 65 / Phase 68) with no decision ID, no `SUMMARY.md` name and no `.planning/` path.
- `tests/test_toolchain_config_gate.py`'s D-13 docstring (former lines 302-304) and assertion-message tail (former lines 367-368) rewritten from "goes stale in Phase 68" framing to past-tense "Phase 68 rewrote it" framing, naming `Phase 68` and quoting `Conventions & gotchas` literally.
- `tests/test_pdf_render_gate.py`'s `_run_sphinx_build_typst` docstring gained one sentence between the QUA-04 historical sentence and the closing "kept regardless" sentence, stating that the `tox-uv` revert (v0.9.3 Phase 65) put `.venv/bin/uv` back and it now runs through the Phase 64 FHS shims.
- Re-measured the `~=1.35` / `>=1.35,<2` `SpecifierSet` equivalence directly (`SPECIFIER_EQUIV = True` over an 11-version sample), since the old comment's `04-01-SUMMARY.md` citation named a file that no longer exists in the repository.
- Zero executable change: masked-AST-hash (docstrings and assert messages replaced with a sentinel) of both edited test files equals the pre-edit base; the two-file pytest result (`35 passed`) and the full-suite collect count (`1548`) are identical before and after.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — head check/baseline, SpecifierSet re-measurement, D-16 tox.ini comment rewrite** - `c8df5e8d` (docs)
2. **Task 2: D-13 — rewrite self-referential docstring/assert-message tail in test_toolchain_config_gate.py** - `ec5506ff` (test)
3. **Task 3: D-14 — add revert/FHS sentence to test_pdf_render_gate.py, close plan gates** - `3865e953` (test)

**Plan metadata:** committed separately after this SUMMARY.

## Files Created/Modified
- `tox.ini` - `requires` comment (old lines 4-10) rewritten; `requires = tox-uv~=1.35` and everything below it byte-identical to base
- `tests/test_toolchain_config_gate.py` - D-13 docstring and assert-message tail moved to post-Phase-68 state; assertion logic untouched
- `tests/test_pdf_render_gate.py` - D-14 one-sentence addition to `_run_sphinx_build_typst`'s docstring; no code change
- `.planning/phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-TOX-EVIDENCE.md` - head check, baseline, SpecifierSet equivalence, tox.ini rewrite, both test-file string diffs, and post-edit gates, all with verbatim command transcripts

## Decisions Made
- Cited evidence in archive-stable form ("v0.9.3 Phase NN, `NN-NAME-EVIDENCE.md`") per D-09, since `.planning/phases/…` paths move to `.planning/milestones/v0.9.3-phases/` at `/gsd-complete-milestone`.
- Re-measured the `SpecifierSet` equivalence directly in this plan rather than attempting a self-contained restatement of an unverifiable historical claim, since the cited `04-01-SUMMARY.md` no longer exists anywhere in the repository (`find .planning -name` returns nothing).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Task 3's `<verify><automated>` collect-count extraction regex never matches this pytest version's padded summary line**
- **Found during:** Task 3 (closing the plan's gates)
- **Issue:** The plan's literal verify command extracts the suite collect count with `sed -n 's/^\([0-9][0-9]*\) tests\{0,1\} collected.*/\1/p'`, which anchors at the start of the line. This worktree's pytest always pads the final summary line with `=` to the fallback 80-column terminal width even when stdout is not a tty (`======================== 1548 tests collected in 0.26s =========================`), so the pattern never matches and the comparison against `COLLECT_BEFORE_68_02` fails with an empty string on the left-hand side, regardless of whether the underlying claim holds.
- **Fix:** Confirmed the substantive claim the check exists to protect using a corrected extraction (`grep -oE '[0-9]+ tests? collected' | grep -oE '^[0-9]+'`, and independently a `sed 's/^=* //;s/ =*$//'` pre-strip before the literal pattern): both yield `1548` before and after the Task 3 edit, matching `COLLECT_BEFORE_68_02` and `COLLECT_AFTER_68_02` exactly. This is documented in `68-TOX-EVIDENCE.md`'s "Gates after the edits" section as a note, not a silent skip.
- **Files modified:** None (verification-only; the plan's own `<verify>` text is immutable and was not edited).
- **Verification:** `uv run pytest --collect-only -q -p no:cacheprovider 2>/dev/null | grep -oE '[0-9]+ tests? collected' | grep -oE '^[0-9]+'` returns `1548` both before Task 2's edit and after Task 3's edit.
- **Committed in:** `3865e953` (evidence note added alongside the Task 3 commit).

---

**Total deviations:** 1 auto-fixed (1 bug, in the plan's own verify-text environment assumption, not in the edited files).
**Impact on plan:** No scope creep — the underlying acceptance criterion (collect count unchanged) is proven by a corrected extraction; no source file needed a fix.

## Issues Encountered
None beyond the deviation above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `tox.ini` and both test files now carry post-Phase-68 rationale; `68-04` re-runs the repository-wide `git grep -n tox-uv-bare -- ':!.planning' ':!uv.lock'` classification on the merged wave-1 tree (this plan plus `68-01`'s `CLAUDE.md` edit and `68-03`'s `flake.nix` edit) to confirm the "rationale presented as current" class is empty.
- No blockers. `68-TOX-EVIDENCE.md` carries `BASE_68_02`, `SPECIFIER_EQUIV`, `TWO_FILE_RESULT_BEFORE`/`AFTER`, `COLLECT_BEFORE_68_02`/`AFTER_68_02`, and `PYVENV_HOME_68_02`/`PYVENV_VERSION_68_02` for `68-04`'s cross-check.

## Self-Check: PASSED

- `tox.ini`, `tests/test_toolchain_config_gate.py`, `tests/test_pdf_render_gate.py`,
  `68-TOX-EVIDENCE.md`, and this `68-02-SUMMARY.md` all exist on disk.
- All four commits (`c8df5e8d`, `ec5506ff`, `3865e953`, `4353f5a1`) are present in
  `git log --oneline`.
- All task-level `<acceptance_criteria>` re-verified passing at Task 3 close (masked
  AST hashes equal base, two-file pytest result and full-suite collect count
  unchanged, black/ruff clean, diff footprint limited to this plan's files).
- Plan-level `<verification>` re-run: `tox.ini`'s comment states the current pin, the
  parser constraint, why `tox-uv` is safe, and short history with an unchanged
  `requires` read-back; both test files' stale self-references describe the
  post-Phase-68 state with unchanged executable content; pass/skip summary and
  collect count unchanged in this worktree.

---
*Phase: 68-documentation-follow-through-claude-md-tox-ini-flake-nix*
*Completed: 2026-09-12*
