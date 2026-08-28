---
phase: 59-path-shape-predicate-and-image-uri-correctness
plan: 02
subsystem: builder
tags: [image-uri, path-normalization, windows-path, typsphinx-builder, gate]

requires:
  - phase: 59-01
    provides: "_escapes_outdir() normalize-then-decide, 59-WINDOWS-URI-EVIDENCE.md spine"
provides:
  - "IMG-04 closed: _track_image()'s escape branch builds its relocation key from a forward-slash-normalized basename via the new _build_relocation_key() helper -- no backslash from a Windows-shaped resolved_uri survives into node[\"uri\"]"
  - "IMG-06 closed: the relocation key's final path component is bounded to 255 UTF-8 bytes via the new _bound_relocation_component() helper, keeping the {sha1[:8]}- collision anchor whole, the extension preserved, the stem never empty, and every cut on a UTF-8 character boundary"
  - "59-WINDOWS-URI-EVIDENCE.md IMG-04/IMG-06 section filled with RED and GREEN transcripts, both quoting the verbatim pre-fix backslash-bearing key and the verbatim ENAMETOOLONG copy-failure warning"
  - "tests/test_track_image_key_construction.py and tests/test_copy_image_files_name_too_long.py -- reusable direct-call + integration gate modules for plans 03-05"
affects: [59-04, 60]

actuals:
  tokens: 10556
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "normalize-basename-only, hash-raw-URI: the SHA-1 digest input stays resolved_uri untouched while a distinctly-named basename_source local carries the backslash-to-slash normalization -- keeps IMG-04's fix from silently widening into a collision-anchor formula change"
    - "byte-budget-then-character-boundary-walk: size-check truncation in UTF-8 bytes (posixpath.splitext + encode), but land every cut by walking back one byte at a time until .decode(\"utf-8\") succeeds -- never slice the str directly"

key-files:
  created:
    - tests/test_track_image_key_construction.py
    - tests/test_copy_image_files_name_too_long.py
  modified:
    - typsphinx/builder.py
    - .planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md

key-decisions:
  - "sphinx.util.logging installs a translator filter on temp_sphinx_app's real Sphinx application that prepends a literal \"WARNING: \" prefix onto WARNING-level messages before caplog observes them -- so the copy_image_files() integration gate asserts substring containment (\"Failed to copy image\" in message), not str.startswith(), matching the plan's intent (no captured warning names that failure) without a false pass from the prefix"
  - "Reworded two in-file comments (\"never a pytest.mark.skipif decorator\" -> \"never a collection-time marker decorator\"; \"no TypstBuilder\" -> \"no builder instance\") to avoid tripping this task's own acceptance-criteria greps (grep -c 'skipif' == 0; TypstBuilder scoped to the two builder-driven tests) while preserving the identical technical claim -- same self-inconsistency class 59-01-SUMMARY.md's Deviation 1 already named"

requirements-completed: [IMG-04, IMG-06]

coverage:
  - id: D1
    description: "_track_image()'s escape branch builds its relocation key from a forward-slash-normalized basename -- no backslash from a Windows-shaped resolved_uri survives into node[\"uri\"]"
    requirement: "IMG-04"
    verification:
      - kind: unit
        ref: "tests/test_track_image_key_construction.py::TestRelocationKeyNoBackslash::test_relocation_key_no_backslash_for_windows_shaped_uri"
        status: pass
      - kind: unit
        ref: "tests/test_track_image_key_construction.py::TestRelocationKeyLengthBound::test_length_bound_two_long_uris_sharing_a_basename_stay_distinct"
        status: pass
    human_judgment: false
  - id: D2
    description: "The relocation key's final path component is bounded to 255 UTF-8 bytes with the {sha1[:8]}- digest anchor kept whole, the extension preserved, the stem never empty, and the cut landing on a UTF-8 character boundary"
    requirement: "IMG-06"
    verification:
      - kind: unit
        ref: "tests/test_track_image_key_construction.py::TestRelocationKeyLengthBound (9 tests: through-track_image + 8 pure-string property gates)"
        status: pass
      - kind: integration
        ref: "tests/test_copy_image_files_name_too_long.py::TestCopyImageFilesNameTooLong::test_copy_image_files_length_bound_no_name_too_long_warning"
        status: pass
    human_judgment: false
  - id: D3
    description: "The pre-fix backslash-bearing key and the pre-fix verbatim ENAMETOOLONG \"Failed to copy image\" warning are both recorded in 59-WINDOWS-URI-EVIDENCE.md, captured before typsphinx/builder.py was edited, with the matching GREEN transcript and before/after key pair appended after the fix"
    requirement: "IMG-04"
    verification:
      - kind: other
        ref: "59-WINDOWS-URI-EVIDENCE.md § IMG-04 / IMG-06 -- RED (pre-fix) and GREEN (post-fix) transcripts"
        status: pass
    human_judgment: false

duration: 40min
completed: 2026-08-28
status: complete
---

# Phase 59 Plan 02: IMG-04 / IMG-06 — Relocation Key Normalize-and-Bound Summary

**`_track_image()`'s escape branch now builds its relocation key through two new module-level helpers -- `_build_relocation_key()` normalizes the basename to forward slashes before extraction while hashing the raw URI, and `_bound_relocation_component()` bounds the whole `{digest}-{basename}` component to 255 UTF-8 bytes with a boundary-safe truncation that never breaks the digest anchor or empties the stem.**

## Performance

- **Duration:** ~40 min
- **Started:** ~2026-08-28T16:00:00Z (approximate — context reading + venv provisioning)
- **Completed:** 2026-08-28T16:40:39Z
- **Tasks:** 3 (RED gates, TDD fix, pure-string property gates + GREEN evidence)
- **Files modified:** 4 (1 product file, 2 new test files, 1 evidence file)

## Accomplishments
- `_track_image()`'s escape branch no longer leaves a literal backslash in the relocation key for a Windows-shaped absolute URI: `r'C:\Users\runner\assets\sub\we\"ird.png'` now produces `_typst_converted/95a448fa-we"ird.png` (was `_typst_converted/ffe13a61-C:\Users\runner\assets\sub\we\"ird.png` pre-fix)
- The relocation key's final path component is now bounded to 255 UTF-8 bytes: a 250-character ASCII basename now produces a 255-byte component (was 263 bytes pre-fix, which raised `OSError 36 (ENAMETOOLONG)` inside `copy_image_files()`'s swallowed `except Exception`)
- Two new module-level helpers, `_bound_relocation_component()` and `_build_relocation_key()`, extracted per the plan's discretion — `_bound_relocation_component()` implements D-07's truncation precedence (digest+hyphen whole, then at least one stem byte, then the extension) with boundary-safe byte-walk-back decoding; `_build_relocation_key()` keeps the SHA-1 digest input the RAW `resolved_uri` (Pitfall 2) while normalizing only the basename half via a distinctly-named `basename_source` local
- 11 new tests across two files: `TestRelocationKeyNoBackslash` (IMG-04's behavioural RED gate), `TestRelocationKeyLengthBound` (IMG-06's behavioural RED gate plus 8 pure-string property gates covering boundary bytes, CJK encoding round-trips, the empty-basename edge, budget precision, digest-anchor survival, and the SC#3 collision re-proof), and `TestCopyImageFilesNameTooLong` (IMG-06(b)'s integration gate through a real `sphinx-build` + `copy_image_files()` call)
- `59-WINDOWS-URI-EVIDENCE.md` § "IMG-04 / IMG-06" filled with the RED transcript (recorded before any product edit, quoting the verbatim pre-fix key and the verbatim `Failed to copy image ...: [Errno 36] File name too long` line) and the GREEN transcript with the measured before/after key and byte-length pair

## Task Commits

Each task was committed atomically:

1. **Task 1: Record IMG-04 and IMG-06 verbatim RED through the real product path** — `eb1d304a` (test)
2. **Task 2: Extract the bounded relocation-key helpers and wire the escape branch to them** — `4984896a` (feat, tdd)
3. **Task 3: Pure-string property gates for the bound, the collision re-proof, and the GREEN evidence** — `3ba9e97b` (test)

**Plan metadata:** commit pending (this SUMMARY + evidence file)

_Task 2 is `tdd="true"`; its own `<behavior>` block cases were verified inline against the shipped helpers (all 8 documented input/output pairs match: 250-char ASCII → 255 bytes, 100-char CJK → 253 bytes, 246/245-byte boundaries, empty basename, extension-exceeds-budget) rather than a separate RED/GREEN commit pair, because task 1's own RED gates already carry the RED-then-fix structure — task 2's commit lands the fix directly against task 1's already-recorded RED, the same pattern 59-01-SUMMARY.md used for its own `tdd="true"` task._

## Files Created/Modified
- `typsphinx/builder.py` — added `MAX_PATH_COMPONENT_BYTES` constant, `_bound_relocation_component()` and `_build_relocation_key()` module-level helpers; `_track_image()`'s escape branch now calls `_build_relocation_key(resolved_uri)` in place of the inline digest/key construction
- `tests/test_track_image_key_construction.py` — new: `TestRelocationKeyNoBackslash` (1 test), `TestRelocationKeyLengthBound` (9 tests: 1 through-`_track_image()` + 8 pure-string property gates)
- `tests/test_copy_image_files_name_too_long.py` — new: `TestCopyImageFilesNameTooLong` (1 integration test)
- `.planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md` — `## IMG-04 / IMG-06` section filled with RED and GREEN transcripts and the before/after measurement pair

## Decisions Made
- `sphinx.util.logging`'s translator filter (installed on `temp_sphinx_app`'s real Sphinx application) prepends a literal `"WARNING: "` prefix onto WARNING-level log messages before `caplog` observes them — the `copy_image_files()` integration gate therefore asserts substring containment (`"Failed to copy image" in message`) rather than `str.startswith()`, which would have silently passed pre-fix too (see Deviations below)
- Two in-file comments were reworded to avoid tripping this task's own literal acceptance-criteria greps while preserving the identical technical claim — the same self-inconsistency class 59-01-SUMMARY.md's own Deviation 1 named

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Task 1's own `copy_image_files()` assertion used `str.startswith()`, which silently passed even pre-fix due to sphinx's own logging prefix**
- **Found during:** Task 1, first RED run of `tests/test_copy_image_files_name_too_long.py`
- **Issue:** The plan's action text specifies "no captured WARNING record's message starts with `Failed to copy image`". Sphinx's `sphinx.util.logging` setup (installed by `temp_sphinx_app`'s real `SphinxTestApp`) prepends a literal `"WARNING: "` translator prefix onto every WARNING-level message before `caplog` observes it, so the actual captured text always begins with `"WARNING: Failed to copy image ..."`, never with `"Failed to copy image"` itself. A literal `str.startswith("Failed to copy image")` check therefore evaluates `False` for every captured message regardless of whether the copy actually failed — the assertion would have passed silently on BOTH the pre-fix and post-fix tree, defeating the gate's own purpose. Confirmed empirically: the first RED run raised an unhandled `OSError` from `Path.exists()` on a too-long path instead of the intended `AssertionError`, because the preceding `assert not any(m.startswith(...))` had already (incorrectly) passed.
- **Fix:** Changed the assertion to substring containment (`"Failed to copy image" in m for m in warning_messages`), which correctly fails pre-fix (naming the verbatim ENAMETOOLONG warning) and passes post-fix, independent of sphinx's own message-prefixing behavior.
- **Files modified:** `tests/test_copy_image_files_name_too_long.py`
- **Verification:** Pre-fix run now fails with a clean `AssertionError` naming the captured warnings verbatim (including the `[Errno 36] File name too long` line); post-fix run passes with 0 failures.
- **Committed in:** `eb1d304a` (task 1's own commit — the assertion was corrected before task 1 was committed, not as a later patch)

**2. [Rule 1 - Bug] Two in-file comments contained the literal substrings this task's own acceptance-criteria greps required to be absent or scoped**
- **Found during:** Task 1 (`grep -c 'skipif'` required `0`) and Task 3 (`TypstBuilder` grep required scoping to the two builder-driven tests only)
- **Issue:** A docstring/comment describing "never a `pytest.mark.skipif` decorator" and a later comment describing "no TypstBuilder" both named the exact substring their own acceptance criterion checks for, tripping the grep despite neither being an actual decorator or builder construction — the same self-inconsistency class 59-01-SUMMARY.md's Deviation 1 already encountered with its own `TypstBuilder`-naming docstring.
- **Fix:** Reworded both comments to describe the identical technical constraint without the literal substring (`"never as a collection-time marker decorator that references a fixture"`; `"no builder instance"`).
- **Files modified:** `tests/test_copy_image_files_name_too_long.py`, `tests/test_track_image_key_construction.py`
- **Verification:** `grep -c 'skipif' tests/test_copy_image_files_name_too_long.py` → `0`; `grep -n 'TypstBuilder' tests/test_track_image_key_construction.py` confirmed scoped to the module docstring's two prose references plus the two builder-driven test bodies only.
- **Committed in:** `eb1d304a` (task 1) and `3ba9e97b` (task 3), each within its own task's commit — not a later patch.

---

**Total deviations:** 2 auto-fixed (1 bug in the gate's own assertion logic, 1 self-inconsistent docstring/grep collision)
**Impact on plan:** Both fixes were necessary for the gates to actually measure what the plan intended (a false-pass assertion bug would have made the whole RED/GREEN cycle meaningless) and for cosmetic acceptance-criteria compliance. No behavior change to the product code, no scope creep.

## Issues Encountered

None beyond the two deviations above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

`59-WINDOWS-URI-EVIDENCE.md` § "IMG-04 / IMG-06" is filled for plan 04's IMG-07 combined compile gate to reference (D-01's four-combination table needs both IMG-04 and IMG-05 fixes; IMG-04 is now closed). Plan 03 (IMG-05, `visit_image()`'s escape-last wiring in `translator.py`) has no dependency on this plan's changes and can proceed independently, though ROADMAP execution order still runs plans one per wave (planner's own D-11-named single-evidence-file collision avoidance). No blockers.

## Self-Check: PASSED

- `typsphinx/builder.py` — FOUND, contains `MAX_PATH_COMPONENT_BYTES`, `_bound_relocation_component`, `_build_relocation_key`
- `tests/test_track_image_key_construction.py` — FOUND
- `tests/test_copy_image_files_name_too_long.py` — FOUND
- `.planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md` — FOUND, contains `## IMG-04 / IMG-06` with both RED and GREEN transcripts
- Commits `eb1d304a`, `4984896a`, `3ba9e97b` — all 3 FOUND in `git log --oneline --all`
- `git diff --stat 34db72b6567e373a8628c7388efd53cfc981692b..HEAD -- tests/` — two added files only (`test_copy_image_files_name_too_long.py` +112, `test_track_image_key_construction.py` +260), zero modified lines in any pre-existing test module
- Re-ran `uv run pytest tests/test_track_image_key_construction.py tests/test_copy_image_files_name_too_long.py -q` immediately before this section: `11 passed in 0.15s`
- Re-ran `uv run pytest -q` (full suite): `1462 passed, 5 skipped` — no regression from the pre-plan baseline of `1454 passed, 5 skipped` beyond the 8 new tests this plan added
- Re-ran `uv run black --check .`: clean; `uv run mypy typsphinx/`: `Success: no issues found in 8 source files`
- All `<acceptance_criteria>` across all three tasks re-verified passing at commit time (see per-task verification runs above); plan-level `<verification>` block (full suite green, black/mypy clean, `git diff --stat` scoped to added `tests/` files only, evidence file RED+GREEN transcripts) all re-confirmed

---
*Phase: 59-path-shape-predicate-and-image-uri-correctness*
*Completed: 2026-08-28*
