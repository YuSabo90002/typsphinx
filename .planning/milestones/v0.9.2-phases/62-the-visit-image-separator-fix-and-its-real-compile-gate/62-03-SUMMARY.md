---
phase: 62-the-visit-image-separator-fix-and-its-real-compile-gate
plan: 03
subsystem: core-translator
tags: [sphinx, typst, translator, red-evidence, golden-comparison, regression-gate]

# Dependency graph
requires:
  - phase: 62-the-visit-image-separator-fix-and-its-real-compile-gate
    provides: "plan 01's tracer fix (AMENDED D-08 triad hoist) and plan 02's full 16 FAIL / 9 PASS / 18-master fixture and gate module, extended here with RED-first evidence and golden binding"
provides:
  - "62-RED-EVIDENCE.md carrying the full verbatim RED transcript (17-master aggregate ExtensionError against a genuinely restored unfixed typsphinx/translator.py), the pass_parent positive control read from disk/stdout, per-golden provenance, and the byte-identical restore confirmation"
  - "10 committed goldens under tests/fixtures/inline_image_separator_render_gate/goldens/ -- 9 PASS-shape content .typ files plus a pre_fix capture of pass_c -- binding D-06/D-07"
  - "TestInlineImageSeparatorGoldens: 9 parametrized golden-comparison tests plus one exact-delta pin for pass_c's measured one-empty-line change"
  - "the phase's own defect todo closed under .planning/todos/completed/ against the extended 16-shape matrix, history preserved via git mv"
affects: [62-04]

# Actuals (#2632)
actuals:
  tokens: 13949
  tasks: 3
  commits: 4

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "RED-first evidence choreography (Phase 59 precedent): restore a product file to a measured PHASE_BASE_SHA, run the real build, transcribe the refusal verbatim with only the machine-specific paths substituted, restore the fix, prove the restore byte-identical via empty git status --porcelain -- <file>"
    - "Golden comparison via Path.read_text(encoding='utf-8') on both sides, never .read_bytes() -- required because the builder writes .typ files with a bare open(path, 'w', encoding='utf-8') and no newline='', so the windows-latest CI lane would spuriously fail a binary compare"
    - "An asymmetric golden pair (pre_fix.typ + the post-fix golden) pins a measured non-byte-identical shape to an EXACT delta assertion (difflib.unified_diff, exactly one added empty line, zero removed) rather than either waiving byte-identity or silently accepting any change"

key-files:
  created:
    - tests/fixtures/inline_image_separator_render_gate/goldens/pass_a_standalone_block_image.typ
    - tests/fixtures/inline_image_separator_render_gate/goldens/pass_b_figure_with_caption.typ
    - tests/fixtures/inline_image_separator_render_gate/goldens/pass_c_image_first_in_paragraph.typ
    - tests/fixtures/inline_image_separator_render_gate/goldens/pass_c_image_first_in_paragraph.pre_fix.typ
    - tests/fixtures/inline_image_separator_render_gate/goldens/pass_d_image_with_dimensions_and_scale_align.typ
    - tests/fixtures/inline_image_separator_render_gate/goldens/pass_e_image_with_propagated_target_id.typ
    - tests/fixtures/inline_image_separator_render_gate/goldens/pass_f_figure_with_plain_legend.typ
    - tests/fixtures/inline_image_separator_render_gate/goldens/pass_g_figure_in_list_item_after_paragraph.typ
    - tests/fixtures/inline_image_separator_render_gate/goldens/pass_h_figure_first_in_list_item.typ
    - tests/fixtures/inline_image_separator_render_gate/goldens/pass_i_bare_image_first_in_list_item.typ
  modified:
    - .planning/phases/62-the-visit-image-separator-fix-and-its-real-compile-gate/62-RED-EVIDENCE.md
    - tests/test_inline_image_separator_render_gate.py
    - .planning/todos/completed/2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md (moved from .planning/todos/pending/, history preserved)

key-decisions:
  - "Split the todo-closing work (Task 3) into two commits -- a pure git mv, then a content-only edit -- after measuring that a single combined commit dropped below git's default 50% rename-similarity threshold (the Resolution section nearly tripled the file's line count), which made `git log --follow` lose the file's pre-move history. The two-commit split restored the traceable rename chain back to the todo's original 2026-08-29 capture commit."
  - "Redacted two pre-existing unredacted worktree/repo absolute paths that plan 01 had already committed in 62-RED-EVIDENCE.md's Phase base SHA and SC#5 sections (Rule 3 -- blocking issue), because this task's own acceptance criterion requires a whole-file grep for /home//Users/ to find zero matches. Substance (branch name, tip SHA, commit subject) is unchanged; only the literal local filesystem path was replaced with a placeholder, consistent with the <BUILD_DIR> substitution this same task already applies to the RED transcript."

requirements-completed: []  # IMG-08, IMG-09, IMG-10, TEST-05 close only after plan 04's phase-close measurements (per this plan's <output> directive)

coverage:
  - id: D1
    description: "The gate was observed RED against a genuinely restored unfixed typsphinx/translator.py: a 9-deletion/0-addition inverse diff was confirmed before the build, the build produced the aggregate ExtensionError naming 17 failed masters (index + all 16 fail_* docnames) with the identical 'expected semicolon or line break' refusal on every row, and the fix was restored byte-identically afterward (empty git status --porcelain / git diff)"
    requirement: "TEST-05"
    verification:
      - kind: other
        ref: "62-RED-EVIDENCE.md § 'RED run (unfixed tree, 18 masters)' -- full verbatim transcript, manually re-executed and cross-checked against the committed section during this task"
        status: pass
    human_judgment: false
  - id: D2
    description: "pass_parent's green verdict inside the same RED build is evidenced from disk (its own %PDF-prefixed wrapper) and stdout's Generated PDF: ... line, never from the aggregate exception, which never names a successful master"
    requirement: "TEST-05"
    verification:
      - kind: other
        ref: "62-RED-EVIDENCE.md § 'Positive control - pass_parent'"
        status: pass
    human_judgment: false
  - id: D3
    description: "8 of 9 PASS shapes emit byte-identically to their unfixed-tree capture; the 9th (pass_c) differs by exactly one added empty line and zero removed lines, pinned by a committed pre-fix golden and a dedicated diff-shape assertion rather than waived"
    requirement: "IMG-10"
    verification:
      - kind: integration
        ref: "tests/test_inline_image_separator_render_gate.py::TestInlineImageSeparatorGoldens::test_pass_shape_content_matches_committed_golden (parametrized over all 9 PASS_DOCNAMES)"
        status: pass
      - kind: integration
        ref: "tests/test_inline_image_separator_render_gate.py::TestInlineImageSeparatorGoldens::test_pass_c_delta_against_unfixed_capture_is_exactly_one_blank_line"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every golden comparison is a text-mode read with an explicit utf-8 encoding on both sides, never .read_bytes(), so the windows-latest CI lane's write-time newline translation cannot spuriously fail this gate"
    requirement: "TEST-05"
    verification:
      - kind: other
        ref: "grep -c read_bytes tests/test_inline_image_separator_render_gate.py == 0; grep -c 'read_text(encoding=\"utf-8\")' == 6"
        status: pass
    human_judgment: false
  - id: D5
    description: "-k golden selects at least 10 tests and all pass; -k fail (17) and -k full_matrix (3) selectors are unaffected by this plan's additions; the full suite, black --check and mypy all stay green"
    requirement: "IMG-10"
    verification:
      - kind: unit
        ref: "uv run pytest tests/test_inline_image_separator_render_gate.py -k golden -q (10 passed); -k fail -q (17 passed); -k full_matrix -q (3 passed)"
        status: pass
      - kind: unit
        ref: "uv run pytest -q (1543 passed, 5 skipped, 0 failed)"
        status: pass
      - kind: other
        ref: "uv run black --check . ; uv run mypy typsphinx/ (both clean)"
        status: pass
    human_judgment: false
  - id: D6
    description: "The phase's own defect todo is closed under .planning/todos/completed/ with a Resolution (Phase 62) section recording the extended 16-shape matrix (not the todo's original 4 rows), and its git history is preserved (git log --follow traces to the original 2026-08-29 capture commit)"
    requirement: null
    verification:
      - kind: other
        ref: "git log --follow --oneline -- .planning/todos/completed/2026-08-29-....md; grep -c 'fail_' == 19 (>= 16 required)"
        status: pass
    human_judgment: false

# Metrics
duration: ~40min
completed: 2026-08-30
status: complete
---

# Phase 62 Plan 03: The RED-First Evidence Choreography and the 9-Golden Byte-Identity Binding Summary

**Restored `typsphinx/translator.py` to a measured pre-fix SHA, transcribed the resulting 17-master aggregate `ExtensionError` verbatim into `62-RED-EVIDENCE.md`, captured 10 committed goldens (9 PASS content files plus a pre-fix capture of the one measurably non-byte-identical shape), bound all 9 to the gate module with an exact-delta pin, and closed the phase's own defect todo against the full 16-shape matrix.**

## Performance

- **Duration:** ~40 min
- **Completed:** 2026-08-30T08:30:35Z
- **Tasks:** 3
- **Files modified:** 14 (11 created, 3 modified/moved)

## Accomplishments

- Restored the unfixed `typsphinx/translator.py` from the measured `PHASE_BASE_SHA` (`5a837238`), confirmed the restore was real (9 deletions / 0 additions, the exact inverse of plan 01's insertion), and ran a real `sphinx-build -b typstpdf` over the full 18-master fixture. Exit code 2; the aggregate `ExtensionError` named exactly 17 failed masters (`index` plus all 16 `fail_*` docnames), each carrying the identical verbatim refusal `expected semicolon or line break` -- explained in the evidence file as measured behaviour (typst-py's `TypstError` carries no file/line/multiplicity), not a copy-paste artefact.
- Recorded `pass_parent`'s positive control entirely from the filesystem and stdout: exactly one `.pdf` in the RED build directory, `%PDF`-magic confirmed, and the verbatim `Generated PDF: ...` stdout line -- because the aggregate exception never names a successful master at all.
- Captured all 9 PASS-shape content `.typ` files from the unfixed tree as goldens (never the `-out.typ` wrapper), plus a `pass_c_image_first_in_paragraph.pre_fix.typ` twin. Restored the fix byte-identically (`git status --porcelain` and `git diff --stat` both empty afterward), then re-captured `pass_c` post-fix into a fresh build directory: the measured delta against its pre-fix twin is exactly one added empty line and zero removed lines, matching the `62-01-PLAN.md` amendment's prediction exactly. The other eight goldens were independently re-diffed against a fresh post-fix build and confirmed byte-identical.
- Added `TestInlineImageSeparatorGoldens` to the gate module: `test_pass_shape_content_matches_committed_golden` (parametrized over all 9 `PASS_DOCNAMES`, exact `str` equality, text-mode utf-8 reads on both sides, `difflib.unified_diff` on failure) and `test_pass_c_delta_against_unfixed_capture_is_exactly_one_blank_line` (asserts the pre-fix/post-fix golden diff is exactly one added empty line, zero removed). `-k golden` now selects 10 tests; `-k fail` (17) and `-k full_matrix` (3) are unaffected.
- Closed `.planning/todos/completed/2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md`: moved from `pending/` (history preserved), with a `## Resolution (Phase 62)` section recording all 16 measured failing shapes (not the todo's own original 4-row matrix), the 9 must-keep-passing shapes and `pass_c`'s pinned delta, the shipped mechanism including both plan-01 amendments (the `in_figure`-both-paths scope and the concat-aware trailing half), and pointers to the gate module, fixture directory and `62-RED-EVIDENCE.md`.

## Task Commits

Each task was committed atomically:

1. **Task 1: The RED choreography** - `d6776bfb` (docs)
2. **Task 2: Bind the 9 PASS shapes to their goldens** - `668422f2` (test)
3. **Task 3a: Move the todo (pure rename)** - `10f1af8d` (docs)
4. **Task 3b: Append the Resolution section** - `4931a3ac` (docs)

_Note: Task 3 was split into two commits after the combined commit dropped below git's rename-detection threshold and broke `git log --follow` -- see Deviations below._

**Plan metadata:** SUMMARY commit follows separately per worktree convention.

## Files Created/Modified

- `.planning/phases/62-the-visit-image-separator-fix-and-its-real-compile-gate/62-RED-EVIDENCE.md` - filled `## RED run`, `## Positive control - pass_parent`, `## Golden capture`, `## Restore confirmation`; also redacted two pre-existing unredacted paths in plan 01's sections (deviation, see below)
- `tests/fixtures/inline_image_separator_render_gate/goldens/pass_{a,b,c,d,e,f,g,h,i}*.typ` (9 files) - committed PASS-shape content goldens, D-07
- `tests/fixtures/inline_image_separator_render_gate/goldens/pass_c_image_first_in_paragraph.pre_fix.typ` - the unfixed-tree twin for the exact-delta pin
- `tests/test_inline_image_separator_render_gate.py` - added `TestInlineImageSeparatorGoldens` (2 test methods, 1 parametrized over 9 docnames)
- `.planning/todos/completed/2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md` - moved from `pending/`, `## Resolution (Phase 62)` appended, closure frontmatter fields added

## Decisions Made

- Split Task 3's todo-closing work into two commits (pure move, then content edit) after measuring that a single combined commit's similarity ratio fell below git's default 50% rename-detection threshold, breaking `git log --follow`'s ability to trace the file's pre-move history. Verified the fix: `git log --follow --oneline` now traces cleanly through the rename back to the todo's original 2026-08-29 capture commit.
- Redacted two pre-existing machine-specific absolute paths that plan 01 had already committed in `62-RED-EVIDENCE.md` (the `## Phase base SHA` worktree path and two `git branch -vv` lines in `## SC#5`), because this task's own acceptance criterion requires a whole-file grep for `/home/`/`/Users/` to find zero matches. Substance (branch name, tip SHA, commit message) is unchanged; only the literal filesystem path was replaced with a placeholder, following the same `<BUILD_DIR>`-substitution convention this task's own RED transcript uses.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Whole-file absolute-path grep failed on plan 01's pre-existing content**
- **Found during:** Task 1 (writing the RED-EVIDENCE.md sections and running the plan's own `<verify>` command)
- **Issue:** The task's acceptance criterion `grep -lF -e '/home/' -e '/Users/' 62-RED-EVIDENCE.md` finds no file requires the WHOLE file to carry no machine-specific home/user-directory path. Plan 01 had already committed a worktree path in `## Phase base SHA` and two `git branch -vv` lines in `## SC#5` (both legitimately measured evidence, but with an unredacted local filesystem path).
- **Fix:** Redacted the worktree path to `<WORKTREE_ROOT>` and the `git branch -vv` checkout-path column to `<REPO_ROOT>`, each with an inline note stating the substitution and why -- the same hygiene pattern this task's own RED transcript already applies to the build directory. No evidentiary substance was altered.
- **Files modified:** `.planning/phases/62-the-visit-image-separator-fix-and-its-real-compile-gate/62-RED-EVIDENCE.md`
- **Verification:** `grep -n '/home/\|/Users/' 62-RED-EVIDENCE.md` returns no match after the fix (re-run after two follow-up edits that had reintroduced the literal substrings in prose describing the redaction itself, also fixed).
- **Committed in:** `d6776bfb` (Task 1 commit)

**2. [Rule 3 - Blocking] A single combined move+edit commit broke `git log --follow`'s rename trace**
- **Found during:** Task 3 (closing the pending todo), verifying the acceptance criterion `git log --follow --oneline ... shows the file's pre-move history`
- **Issue:** `git mv`-ing the todo and appending the ~89-line Resolution section in the same commit nearly tripled the file's line count (104 -> 193), dropping the rename similarity below git's default 50% detection threshold. `git diff --cached --find-renames` reported a plain add+delete, not a rename, and `git log --follow` on the destination path returned only the single combined commit -- the pre-2026-08-29 history (capture, milestone archive, resolves_phase tagging) was invisible.
- **Fix:** `git reset --soft` the combined commit, re-staged the file at the completed path with its ORIGINAL byte-identical content first (git detected a clean 100% rename), committed that alone, then applied the Resolution-section content as a second, content-only commit at the already-moved path.
- **Files modified:** none beyond the todo file itself; no other task's files were touched by the reset (it only unwound the single Task 3 commit, `672`-generation commits for Tasks 1/2 were untouched).
- **Verification:** `git log --follow --oneline -- .planning/todos/completed/2026-08-29-....md` now lists 5 commits, tracing cleanly back through the rename to `ec6bd3a4` (the todo's original capture commit).
- **Committed in:** `10f1af8d` (pure move) + `4931a3ac` (content)

---

**Total deviations:** 2 auto-fixed (both Rule 3 - blocking issues that would have failed this task's own acceptance criteria without a fix; neither touches product code or any other plan's evidentiary substance).
**Impact on plan:** Both fixes are hygiene/process corrections local to this plan's own evidence and todo-closing artifacts. No scope creep; no weakening of any binding property.

## Issues Encountered

None beyond the two documented deviations above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 04 can proceed: `62-RED-EVIDENCE.md` is complete with the full RED transcript, positive control, golden provenance and restore confirmation; all 10 goldens are committed and bound; the phase's own defect todo is closed with a fully-traceable history.
- `typsphinx/translator.py` is confirmed byte-identical to its pre-plan-03 (post-fix) state -- `git status --porcelain` and `git diff` both empty at every commit boundary.
- The full suite is green (1543 passed, 5 skipped, 0 failed), `black --check` and `mypy typsphinx/` are both clean. `ruff`'s verdict remains deferred to plan 04's dispatched CI run (D-11).
- No blockers.

---
*Phase: 62-the-visit-image-separator-fix-and-its-real-compile-gate*
*Completed: 2026-08-30*

## Self-Check: PASSED

- `tests/fixtures/inline_image_separator_render_gate/goldens/pass_a_standalone_block_image.typ` - FOUND
- `tests/fixtures/inline_image_separator_render_gate/goldens/pass_b_figure_with_caption.typ` - FOUND
- `tests/fixtures/inline_image_separator_render_gate/goldens/pass_c_image_first_in_paragraph.typ` - FOUND
- `tests/fixtures/inline_image_separator_render_gate/goldens/pass_c_image_first_in_paragraph.pre_fix.typ` - FOUND
- `tests/fixtures/inline_image_separator_render_gate/goldens/pass_d_image_with_dimensions_and_scale_align.typ` - FOUND
- `tests/fixtures/inline_image_separator_render_gate/goldens/pass_e_image_with_propagated_target_id.typ` - FOUND
- `tests/fixtures/inline_image_separator_render_gate/goldens/pass_f_figure_with_plain_legend.typ` - FOUND
- `tests/fixtures/inline_image_separator_render_gate/goldens/pass_g_figure_in_list_item_after_paragraph.typ` - FOUND
- `tests/fixtures/inline_image_separator_render_gate/goldens/pass_h_figure_first_in_list_item.typ` - FOUND
- `tests/fixtures/inline_image_separator_render_gate/goldens/pass_i_bare_image_first_in_list_item.typ` - FOUND
- `.planning/todos/completed/2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md` - FOUND
- `.planning/todos/pending/2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md` - CONFIRMED ABSENT
- Commit `d6776bfb` - FOUND in `git log --oneline --all`
- Commit `668422f2` - FOUND in `git log --oneline --all`
- Commit `10f1af8d` - FOUND in `git log --oneline --all`
- Commit `4931a3ac` - FOUND in `git log --oneline --all`
- All task `<acceptance_criteria>` re-verified: PASS (RED transcript with 17 failed masters and pass_parent positive control recorded; 10 goldens with correct provenance and zero absolute paths; `-k golden` selects 10/10 passing, `-k fail` 17/17, `-k full_matrix` 3/3; full suite 1543 passed/5 skipped/0 failed; black + mypy clean; todo closed with `git log --follow` tracing 5 commits back to its 2026-08-29 capture)
