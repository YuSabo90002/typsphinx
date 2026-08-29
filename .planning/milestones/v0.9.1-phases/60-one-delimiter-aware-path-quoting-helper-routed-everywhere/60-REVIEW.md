---
phase: 60-one-delimiter-aware-path-quoting-helper-routed-everywhere
reviewed: 2026-08-29T11:50:42Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - tests/test_builder_path_quoting_gate.py
  - tests/test_pathfmt.py
  - tests/test_template_registry_path_quoting_gate.py
  - tests/test_templates_path_collision_gate.py
  - tests/test_writer_path_quoting_gate.py
  - typsphinx/builder.py
  - typsphinx/pathfmt.py
  - typsphinx/template_registry.py
  - typsphinx/writer.py
findings:
  critical: 1
  warning: 0
  info: 1
  total: 2
status: issues_found
---

# Phase 60: Code Review Report

**Reviewed:** 2026-08-29T11:50:42Z
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

Reviewed `typsphinx/pathfmt.py`'s new `quote_path()` helper and every call site it was
routed into across `builder.py`, `writer.py`, and `template_registry.py`, plus the five
test modules that gate this rollout. The routing itself is careful: every call site was
checked against the actual diff (`git diff a0232ea7^..HEAD`), and every one is provably
safe — each value reaching `quote_path()` is either a `str` (guaranteed by an adjacent
`isinstance` narrowing, e.g. `builder.py`'s `target_text` binding and the
`isinstance(target, str)` branch inside `_resolve_target_stem`), an explicitly
`str()`'d value (the `_conf17_violation_message()`/`_templates_path_collision_message()`
callers), or `None` (`writer.py`'s package-alone `template_file`, which `quote_path()`
contractually renders as bare `None`). No IDENTIFIER-valued interpolation (registry
keys, docnames, `entry[4]`, sorted key lists, `template_registry.py`'s type-check
branch) was over-reached into `quote_path()` — every one of those correctly stayed on
`!r`, confirmed by grep against the diff and by the dedicated exclusion-control tests
(`TestRegistryTypeCheckMessageStaysReprQuoted`, `test_registry_keys_stay_repr_quoted`).

However, `quote_path()` itself has a genuine correctness defect in its "both quote
characters present" branch: escaping an embedded apostrophe with a single backslash can
merge with a backslash that already immediately precedes that apostrophe in the input,
producing a run of two consecutive backslashes in the output — the exact "doubled
separator" defect this whole phase exists to eliminate. This directly contradicts the
module's own documented contract ("never double a backslash") and its D-01a claim (also
documented as fact, also false). No test in the five gate modules constructs a value
that exercises this specific adjacency, so the gap is currently invisible to CI.

## Critical Issues

### CR-01: `quote_path()`'s both-quotes branch can itself produce a doubled backslash run

**File:** `typsphinx/pathfmt.py:83-84`

**Issue:** When a value contains both quote characters, `quote_path()` wraps it in
apostrophes and escapes each embedded apostrophe with a single inserted backslash:

```python
escaped = value_str.replace("'", "\\'")
return f"'{escaped}'"
```

This is correct only when no apostrophe in the value is *already* immediately preceded
by a backslash. When one is, the inserted escape backslash concatenates with the
pre-existing one, producing a run of **two** consecutive backslashes in the output —
which is precisely the "doubled separator" shape this whole phase (and the repository's
`_assert_no_doubled_separator`/`TestWindowsPathEscapingRegressionGuard` convention) was
built to eliminate.

Reproduction (verified by loading `pathfmt.py` standalone, mirroring
`tests/test_pathfmt.py::TestPathfmtLeafModule`'s own load technique):

```python
value = "C:" + chr(92) + chr(39) + "and" + chr(34) + "there"   # C:\'and"there
result = quote_path(value)
# result == "'C:\\\\'and\"there'"  -- i.e. 'C:\\'and"there'
# contains a run of TWO consecutive backslash characters
```

This directly falsifies the module's own docstring, which states as fact (not as an
open question):

> D-01a: that one inserted backslash per escaped apostrophe can never form a run of two
> or more consecutive backslashes, so the existing
> `TestWindowsPathEscapingRegressionGuard._assert_no_doubled_separator` guard stays
> green over this function's output.

The value need not be Windows-specific to trigger this — Windows filenames cannot
contain a literal `"` at all (it is an NTFS-reserved character), so the "both quote
characters present" branch can only ever fire for a POSIX-style path (or an arbitrary
non-path config string routed through this general-purpose helper, e.g. a
`templates_path` entry, a `typst_documents` target, or a template filename). A POSIX
path containing a backslash character immediately followed by a directory/file name
that starts with an apostrophe (e.g. a directory named `` `\'s notes"` ``) is unusual
but entirely legal, and is exactly the kind of adversarial/edge-case value this review
was asked to trace.

**Why the test suite didn't catch it:** every "both quotes" fixture in
`tests/test_pathfmt.py` (`BOTH_QUOTES`, `COMBINED_BACKSLASH_AND_BOTH_QUOTES`) and in
`tests/test_templates_path_collision_gate.py`'s
`TestWindowsPathEscapingRegressionGuard` (`SINGLE_QUOTE_SHAPED_PATH`, which only has one
quote character present and therefore never even reaches this branch) places the
pre-existing backslash somewhere other than immediately before an apostrophe. None of
the routed call sites' tests happen to feed this specific adjacency through either. The
`TestQuotePathNoDoubledSeparator`/`_assert_no_doubled_separator` guards are exactly the
right regression tool for this — they simply were never pointed at the one input shape
that defeats the implementation.

**Fix:** The "no doubling, ever" and "escape every apostrophe with a backslash, touch
nothing else" requirements are mutually incompatible whenever a backslash already sits
immediately before an apostrophe — any backslash-based escape of that apostrophe will
necessarily produce two adjacent backslashes. A design that keeps the "no doubled
backslash run" invariant unconditionally true needs to stop reusing backslash as the
escape character for the apostrophe in this branch. A drop-in fix that keeps the
existing single-quote-wrapped output shape and needs no backslash at all is SQL-style
apostrophe doubling:

```python
escaped = value_str.replace("'", "''")
return f"'{escaped}'"
```

This can never interact with a pre-existing backslash (it never inserts one), so the
"no doubled backslash run" invariant becomes unconditionally true rather than true for
only the fixture shapes currently tested. Note this changes the exact escaped
character sequence the existing "both quotes" tests hard-code
(`tests/test_pathfmt.py::TestQuotePathDelimiterSelection::test_both_quote_characters_wraps_in_apostrophes_escaping_only_apostrophe`
and `test_combined_backslash_and_both_quotes`, plus
`tests/test_templates_path_collision_gate.py`'s single-quote-disambiguation tests only
exercise the apostrophe-only branch and are unaffected) — those assertions will need to
be updated to match whichever escaping convention is chosen, and a new regression test
covering the backslash-immediately-before-apostrophe adjacency should be added
regardless of which fix is chosen, since that is the exact shape that was missing
before.

## Info

### IN-01: `pathfmt.py`'s D-01a claim should not be stated as settled fact

**File:** `typsphinx/pathfmt.py:24-27`

**Issue:** Independent of the code defect in CR-01, the module docstring asserts D-01a
as a proven property ("that one inserted backslash per escaped apostrophe can never
form a run of two or more consecutive backslashes"). This is documentation debt on top
of the functional bug: once CR-01 is fixed, this paragraph should be corrected (or
removed) rather than left describing an invariant that was never actually true for the
implementation as shipped.

**Fix:** Update or delete the D-01a paragraph once CR-01's fix lands, so the docstring
accurately describes the implementation's real guarantees.

---

_Reviewed: 2026-08-29T11:50:42Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
