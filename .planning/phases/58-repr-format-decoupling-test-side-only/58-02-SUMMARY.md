---
phase: 58-repr-format-decoupling-test-side-only
plan: 02
subsystem: testing
tags: [pytest, ast-static-analysis, repr-decoupling, path-naming, msg-01]

requires:
  - phase: 58-repr-format-decoupling-test-side-only
    provides: "plan 58-01's tests/_path_naming.py path_named_in() predicate, consumed here as the second and final call site"
provides:
  - "tests/test_builder.py's rewritten image-rehome warning assertion, asserting meaning (naming) rather than repr()'s format"
  - "58-DECOUPLING-EVIDENCE.md's second SC#1/SC#2(b) post-rewrite green section and second SC#2(c) recorded falsification section, plus the closing SC#2 both-sites summary table"
  - "the whole-tree AST pass-criterion count reaching exactly 7 -- zero path-valued sites remain"
affects: [58-03]

actuals:
  tokens: 3500
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "same one-line substitution pattern as plan 58-01's escape-target-gate rewrite: assert repr(value) in text -> assert path_named_in(value, text), with a failure message that quotes both the value and the whole message"
    - "black's 88-column limit as a hard constraint on the literal-substring acceptance-criteria grep: a multi-line assert() call splits the exact literal the grep expects across a line break, so the failure-message f-string must be shortened rather than the call reformatted onto multiple lines"

key-files:
  created: []
  modified:
    - tests/test_builder.py
    - .planning/phases/58-repr-format-decoupling-test-side-only/58-DECOUPLING-EVIDENCE.md

key-decisions:
  - "Shortened the assert's failure-message f-string from the plan's suggested phrasing ('expected {abs_uri!r} to be named in warning message: {message!r}') to a terser one ('{abs_uri!r} not named in {message!r}') so the whole `assert path_named_in(abs_uri, message), f\"...\"` statement fits black's 88-column limit on ONE physical line -- measured live: the longer phrasing made black wrap the call across three lines, which split the literal substring `path_named_in(abs_uri, message)` the plan's own acceptance-criteria grep requires to appear intact. Both phrasings satisfy the plan's <action> instruction to name the URI and quote the whole message; only the shorter one also satisfies the plan's own <acceptance_criteria> grep as measured."

requirements-completed: [MSG-01]

coverage:
  - id: D1
    description: "tests/test_builder.py's image-rehome warning test pass criterion is rewritten from assert repr(abs_uri) in message onto assert path_named_in(abs_uri, message); every pre-existing assertion in the test survives byte-identical"
    requirement: MSG-01
    verification:
      - kind: unit
        ref: "tests/test_builder.py::test_post_process_images_rehome_escape_relocates_with_warning -- 1 passed, zero skipped"
        status: pass
      - kind: unit
        ref: "tests/test_builder.py (whole module) -- 31 passed, zero skipped"
        status: pass
      - kind: other
        ref: "AST pass-criterion count for the file: 1 -> 0; whole-tree count: 8 (after 58-01) -> 7"
        status: pass
    human_judgment: false
  - id: D2
    description: "SC#2's third required recorded run for this site -- a REAL recorded RED under a temporarily-falsified typsphinx/builder.py:1767, attributed to the naming assertion specifically, with the product file restored and re-proven green"
    requirement: MSG-01
    verification:
      - kind: manual_procedural
        ref: "58-DECOUPLING-EVIDENCE.md section: ## SC#2 (c) — recorded falsification: builder.py:1767 -- carries a verbatim pytest 1 failed transcript, an attribution statement naming the path_named_in assertion specifically, the revert transcript, and the re-proven 1 passed transcript"
        status: pass
    human_judgment: true
    rationale: "The plan's own <verify><human-check> block for Task 2 explicitly asks a human to confirm the pasted RED output is genuine pytest output (not a reconstruction) and that the failure is attributable to the right assertion -- this is a documented-evidence judgment call the automated grep checks cannot fully replace."
  - id: D3
    description: "SC#4 holds across this plan: typsphinx/ is byte-identical to the phase base at every commit, including through Task 2's temporary falsifying edit and revert"
    requirement: MSG-01
    verification:
      - kind: other
        ref: "git status --porcelain typsphinx/ and git diff --name-only -- typsphinx/ both empty after every task; git diff --name-only <phase-base-SHA>..HEAD -- typsphinx/ also empty"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-28
status: complete
---

# Phase 58 Plan 02: Second `repr()`-Decoupling Call Site — Image-Rehome Warning Summary

**Rewrote `tests/test_builder.py`'s image-rehome warning test off `repr(abs_uri) in message` onto the shared `path_named_in()` predicate plan 58-01 created, and proved the rewrite via a real, recorded RED against a temporarily-edited `typsphinx/builder.py:1766-1769` — bringing the whole-tree `repr()`/`!r` pass-criterion census to exactly 7, with zero path-valued sites left.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-08-28
- **Tasks:** 2 completed
- **Files modified:** 2 (`tests/test_builder.py`, `58-DECOUPLING-EVIDENCE.md`)

## Accomplishments
- `tests/test_builder.py`'s `test_post_process_images_rehome_escape_relocates_with_warning`
  no longer asserts `repr(abs_uri) in message`. It now asserts
  `path_named_in(abs_uri, message)`, format-agnostic across `!r` (today), a hardcoded
  `'{value}'`, and MSG-02's future delimiter-aware helper (Phase 60). Every other assertion
  in the test — `expected_key`, `img["uri"] == expected_key`, `".." not in img["uri"].split("/")`,
  `builder.images.get(expected_key) == abs_uri`, `len(warning_records) == 1`, and
  `"could not rehome image URI" in message` — is byte-identical to the phase base.
- A real, recorded falsification (D-05(b)): `typsphinx/builder.py:1766-1769`'s warning was
  temporarily edited to drop only the `resolved_uri` interpolation, keeping the same-basename
  `key` interpolation with its `!r` conversion intact — the analogue of the D-03 fallback-trap
  shape on this site. Measured RED (`1 failed`), attributed specifically to the `path_named_in`
  assertion (neither the record-count nor the warning-substring assertion failed), reverted via
  `git checkout`, and re-proven green (`1 passed`). `typsphinx/` is byte-identical to the phase
  base at every commit — both `git status --porcelain typsphinx/` and
  `git diff --name-only <phase-base-SHA>..HEAD -- typsphinx/` are empty.
- The whole-tree `repr()`/`!r` AST pass-criterion census moved from 8 (after plan 58-01) to 7 —
  the seven non-path sites, with zero path-valued pass-criterion sites remaining anywhere in
  `tests/`. This discharges ROADMAP Phase 58 SC#1 in full (both sites now at per-file count 0)
  and SC#3's measurable half (the whole-tree count is exactly 7).
- `58-DECOUPLING-EVIDENCE.md` gained two new sections — `## SC#1/SC#2 (b) — post-rewrite green:
  image-rehome warning` and `## SC#2 (c) — recorded falsification: builder.py:1767 (image-rehome
  warning)` — plus a closing `### SC#2 — the three recorded runs, both sites` table indexing
  where each of the six required runs (three per site) lives. All five headings plan 58-01 wrote
  remain present, in original order, unedited.

## Task Commits

Each task was committed atomically:

1. **Task 1: Rewrite the image-rehome warning test's pass criterion onto the shared predicate and record its post-rewrite green** — `43dab6a7` (feat)
2. **Task 2: D-05(b) — the recorded real falsification of the image-rehome test against a temporarily edited `typsphinx/builder.py`, reverted inside this task** — `a2f932ca` (test)

**Plan metadata:** (this commit, pending)

## Files Created/Modified
- `tests/test_builder.py` — pass criterion rewritten from `repr(abs_uri) in message` onto `path_named_in(abs_uri, message)`; `from _path_naming import path_named_in` import added
- `.planning/phases/58-repr-format-decoupling-test-side-only/58-DECOUPLING-EVIDENCE.md` — appended `## SC#1/SC#2 (b)` (image-rehome), `## SC#2 (c)` (builder.py:1767 falsification), and `### SC#2 — the three recorded runs, both sites` closing table

## Decisions Made

- **Shortened the assert's failure-message f-string to keep `path_named_in(abs_uri, message)` on one physical line.** The plan's `<action>` suggested phrasing (`f"expected {abs_uri!r} to be named in warning message: {message!r}"`) made the whole `assert` statement exceed black's 88-column limit; `black` reformatted it onto three lines, splitting the literal substring `path_named_in(abs_uri, message)` the plan's own `<acceptance_criteria>` grep requires intact. Measured live via the grep check itself (`grep -c 'path_named_in(abs_uri, message)' tests/test_builder.py` returned `0` after the reformat, `1` after shortening the message). Fix: `f"{abs_uri!r} not named in {message!r}"` — 12 characters shorter, semantically identical (names the URI, quotes the whole message), fits on one line, `black --check` reports the file unchanged.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] black's line-wrapping of the plan's suggested assert message split the literal substring the plan's own acceptance grep requires**
- **Found during:** Task 1, Step 3 (running `uv run black tests/test_builder.py` after writing the assertion with the plan's suggested failure-message phrasing)
- **Issue:** The plan's `<action>` text for Task 1 suggests a failure message naming the URI and quoting the whole captured message, without specifying exact wording. The natural phrasing (`f"expected {abs_uri!r} to be named in warning message: {message!r}"`) made the full `assert path_named_in(abs_uri, message), f"..."` line exceed 88 columns. `black` (run per this project's standard lint/format gate) reformatted it as `assert path_named_in(\n    abs_uri, message\n), f"..."`, which splits the literal substring `path_named_in(abs_uri, message)` across a line break — failing the plan's own `<acceptance_criteria>` requirement that this exact literal appear once, contiguous, in the file.
- **Fix:** Shortened the failure-message f-string to `f"{abs_uri!r} not named in {message!r}"`, which brings the whole statement to 83 characters (measured), fits on one physical line, and leaves `black --check` reporting no changes needed.
- **Files modified:** `tests/test_builder.py`
- **Verification:** `grep -c 'path_named_in(abs_uri, message)' tests/test_builder.py` → `1`; `uv run black --check tests/test_builder.py` → exit 0, "1 file would be left unchanged"; `uv run pytest tests/test_builder.py -q` → `31 passed`.
- **Committed in:** `43dab6a7` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug — a tooling interaction between black's formatting and the plan's own literal-substring acceptance grep).
**Impact on plan:** The fix is a cosmetic wording change to a test failure message with zero behavioral effect on the assertion itself. No scope creep; the plan's stated acceptance criteria and success criteria are satisfied exactly as written, once measured against the real formatter.

## Issues Encountered
None beyond the deviation documented above, resolved within Task 1's own execution.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- `tests/test_builder.py`'s pass criterion no longer hard-codes `repr()`'s output format; MSG-01's
  image-rehome-warning half is fully discharged (SC#1, SC#2 for this file, SC#4 held throughout).
- The whole-tree AST pass-criterion count is exactly `7` — zero path-valued sites remain anywhere
  in `tests/`. Plan 58-03's census guard (`PASS_CRITERION_REPR_ALLOWLIST`,
  `_collect_pass_criterion_repr_sites()`) can now be built against this exact, measured seven-site
  enumeration.
- `typsphinx/` remains byte-identical to the phase base; the one point this plan touched it
  (Task 2's temporary falsification of `builder.py:1766-1769`) is fully reverted and proven so
  both in the working tree and against the phase-base SHA in `58-DECOUPLING-EVIDENCE.md`.
- `58-DECOUPLING-EVIDENCE.md` now carries six of the phase's headings in order, ready for plan
  58-03 to append its own census/guard sections without disturbing any prior section.

## Self-Check: PASSED

- `tests/test_builder.py` modified as expected: FOUND (`git diff -- tests/test_builder.py` confined to import block and one assertion block)
- `.planning/phases/58-repr-format-decoupling-test-side-only/58-DECOUPLING-EVIDENCE.md` contains `## SC#1/SC#2 (b) — post-rewrite green: image-rehome warning`: FOUND
- `.planning/phases/58-repr-format-decoupling-test-side-only/58-DECOUPLING-EVIDENCE.md` contains `## SC#2 (c) — recorded falsification: builder.py:1767 (image-rehome warning)`: FOUND
- `.planning/phases/58-repr-format-decoupling-test-side-only/58-DECOUPLING-EVIDENCE.md` contains `### SC#2 — the three recorded runs, both sites`: FOUND
- Commit `43dab6a7` found in `git log --oneline --all`: FOUND
- Commit `a2f932ca` found in `git log --oneline --all`: FOUND
- All plan-level `<verification>` commands re-run and passing (see body above): PASS
  - `uv run pytest tests/test_builder.py tests/test_out02_escape_target_gate.py tests/test_path_naming_predicate.py -q` → `46 passed`
  - Whole-tree AST count → `7`; per-file counts for both target files → `0`
  - `git status --porcelain typsphinx/` and `git diff --name-only -- typsphinx/` → both empty
  - `uv run black --check .` → exit 0 (341 files unchanged); `nix-shell -p ruff --run "ruff check ."` → `All checks passed!` (ruff cannot exec directly in this worktree's venv on NixOS — documented, matches plan 58-01's precedent)
  - No `58-VERIFICATION.md` in the phase directory: confirmed
- All task-level `<acceptance_criteria>` re-verified: PASS
- `git status --porcelain typsphinx/` empty at final check: PASS

---
*Phase: 58-repr-format-decoupling-test-side-only*
*Completed: 2026-08-28*
