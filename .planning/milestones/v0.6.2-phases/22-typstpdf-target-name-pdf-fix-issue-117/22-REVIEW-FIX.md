---
phase: 22-typstpdf-target-name-pdf-fix-issue-117
fixed_at: 2026-07-21T14:16:42Z
review_path: .planning/phases/22-typstpdf-target-name-pdf-fix-issue-117/22-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 22: Code Review Fix Report

**Fixed at:** 2026-07-21T14:16:42Z
**Source review:** .planning/phases/22-typstpdf-target-name-pdf-fix-issue-117/22-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 3 (WR-01, WR-02, WR-03 -- `fix_scope: critical_warning`; IN-01/IN-02 excluded per instructions -- awareness-only / locked by D-07)
- Fixed: 3
- Skipped: 0

## Fixed Issues

### WR-01: `TypstPDFBuilder.finish()`'s per-entry loop can raise an uncaught `IndexError` before `_resolve_output_stem`'s own defenses ever run

**Files modified:** `typsphinx/builder.py`
**Commit:** `6f1c882`
**Applied fix:** Added a length guard (`if not doc_tuple: ... continue`) at the top of the `for doc_tuple in typst_documents:` loop in `TypstPDFBuilder.finish()`, mirroring the guard already present inside `_resolve_output_stem`. A malformed entry (e.g. an empty tuple from a misconfigured `typst_documents`) now logs a warning and is skipped instead of raising `IndexError: tuple index out of range` on `doc_tuple[0]` and crashing the entire `-b typstpdf` build.

### WR-02: D-05's directory-preserving behavior (`_directory_preserving_relpath`) has zero test coverage for its core case -- a nested docname combined with a non-identity target

**Files modified:** `tests/test_builder_output_stem.py`
**Commit:** `2ae7ff4`
**Applied fix:** Chose option (a) from the review's fix suggestion (direct unit test over extending a render-gate fixture, matching the file's existing unit-test-only scope). Added two tests: `test_directory_preserving_relpath_keeps_nested_docname_directory` asserts `_directory_preserving_relpath("sub/index", "manual") == "sub/manual"` (the exact D-05 documented example), and `test_directory_preserving_relpath_identity_stem_is_unchanged` asserts the `stem == docname` early-return branch does not double-prepend the directory (`_directory_preserving_relpath("sub/index", "sub/index") == "sub/index"`). No source change was needed -- the function's behavior was already correct, per the reviewer's own empirical verification; this closes the test-coverage gap only.

### WR-03: Degenerate path-bearing targets that reduce to an empty basename produce two confusing, back-to-back warnings instead of one

**Files modified:** `typsphinx/builder.py`, `tests/test_builder_output_stem.py`
**Commit:** `aa9dead`
**Applied fix:** In `_resolve_output_stem`'s path-guard branch, after computing `fallback = path.basename(...)`, added a check for `if not fallback.strip()`: when the path-guard's own basename fallback is itself empty (trailing separator, bare root, or bare drive prefix), the code now returns immediately with the single "empty typst_documents target name ... after removing an unsupported path" warning instead of falling through to also emit the "a path is not supported ... using '' instead" warning first. Verified manually (direct invocation) that the degenerate case now emits exactly one warning, and added `test_resolve_output_stem_warns_once_on_path_bearing_target_with_empty_basename` asserting `len(warnings) == 1` for the `"sub/manual.typ/"` input.

## Skipped Issues

None -- all in-scope findings (WR-01, WR-02, WR-03) were fixed. IN-01 and IN-02 were excluded per the fix-scope instruction (`critical_warning`) and the explicit note that both are "flagging for awareness only" / locked by decision D-07; they were not attempted.

---

_Fixed: 2026-07-21T14:16:42Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
