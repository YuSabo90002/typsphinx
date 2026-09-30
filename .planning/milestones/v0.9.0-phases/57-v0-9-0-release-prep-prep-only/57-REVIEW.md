---
phase: 57-v0-9-0-release-prep-prep-only
reviewed: 2026-08-22T00:00:00Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - typsphinx/builder.py
  - tests/test_templates_path_collision_gate.py
  - tests/test_changelog_page_gate.py
  - pyproject.toml
  - CHANGELOG.md
  - docs/source/changelog.rst
  - README.md
findings:
  critical: 0
  warning: 1
  info: 1
  total: 2
status: issues_found
---

# Phase 57: Code Review Report

**Reviewed:** 2026-08-22
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

This phase is prep-only except for one deliberate, owner-approved exception: plan 57-11's
change to `typsphinx/builder.py`, which replaces `{value!r}` with explicit `'{value}'` quoting
for three PATH-valued interpolations in the pre-write template-refusal messages (the
`templates_path` collision refusal, the CONF-17 srcdir-ancestor refusal, and the
bundle-destination collision refusal), and extracts the two previously-inline messages into
named functions (`_templates_path_collision_message`, `_bundle_destination_collision_message`)
alongside the pre-existing `_conf17_violation_message`.

Verified directly against the git history (`699d4c0e`, `6cfdde70`):

- The task-1 commit (`699d4c0e`) touches **exactly** the three named f-strings — no other line
  in `typsphinx/builder.py` changed, and no test file was edited in that commit, confirming the
  POSIX-output-byte-identical claim structurally rather than by re-reading prose.
- The task-2 commit (`6cfdde70`) is a byte-for-byte extraction: the two newly-named functions'
  bodies are character-identical to the f-strings they replaced at their original call sites, and
  both call sites (`_validate_used_template_paths()` line ~1362, `_copy_used_template_bundles()`
  line ~2224) now call the extracted functions with argument order and types matching the
  functions' own signatures. There is no leftover inline duplicate of either message anywhere in
  the file — a `grep` for the message text found only the two function definitions and their two
  call sites.
- Every identifier-valued interpolation (`{key!r}`, `{existing_key!r}`, `{docname!r}`, etc.)
  correctly stayed `!r`; only the four PATH-valued interpolations across the three sites were
  changed.
- No control-flow, refusal-decision, or behavioral change beyond message text was found — the
  diff is confined to string literals inside `return`/`f"..."` expressions; every existing
  collision-gate behavioral assertion (which builds refuse, which don't, aggregation order,
  failure counts) is untouched and unaffected.

One genuine, if narrow, robustness regression was found in the new quoting scheme itself (see
WR-01 below): `repr()` — which the fix deliberately moves away from for path values — also had
the side effect of automatically escaping/re-delimiting an embedded quote character, a property
the new explicit `'{value}'` quoting does not preserve. The other reviewed files (packaging,
changelog, README, test additions) are internally consistent: the version bump is applied
identically in `pyproject.toml` and `README.md`, the `## [0.9.0]` CHANGELOG section still carries
exactly four `**Breaking` bullets as asserted elsewhere in this milestone, and the migration
guide's illustrative `ExtensionError` transcript (added earlier, in 57-04) uses only POSIX
example paths, which is why it needed no edit alongside 57-11's fix — confirmed by inspection
rather than assumed.

## Warnings

### WR-01: Explicit `'{value}'` quoting is ambiguous when a path value contains a literal single quote

**File:** `typsphinx/builder.py:329-334` (`_conf17_violation_message`), `typsphinx/builder.py:363-376` (`_templates_path_collision_message`), `typsphinx/builder.py:398-402` (`_bundle_destination_collision_message`)

**Issue:** The 57-11 fix intentionally replaces `{value!r}` with explicit `'{value}'` for every
PATH-valued interpolation, specifically to stop `repr()` from doubling backslashes on Windows.
That trade correctly solves the backslash problem, but it also throws away a property `repr()`
gave for free: `repr()` automatically chooses a delimiter that does not collide with the string's
own content (falling back to double quotes, or escaping, when the string contains a single
quote), so the previous messages were unambiguous even for a pathological input. The new
`'{value}'` form has no such guard — if `resolved_path`, `srcdir`, `bundle_dir`, `raw_tp_entry`,
`resolved_tp_entry`, or `dest_dir` contains a literal `'` (a legal character in a POSIX, macOS,
or Windows filename/directory name — e.g. a project checked out under `~/O'Brien's Projects/`),
the message reads with a quote appearing to close early:

```
resolved template bundle directory '/home/user/O'Brien's Projects/_templates' collides with...
```

A user reading this in a CI log can no longer tell where the path value ends and the surrounding
sentence resumes — exactly the "unambiguous delimiting" property the plan's own dispatch prompt
flags as `repr()`'s original job. This is a message-quality edge case, not a refusal-logic bug
(the build still refuses correctly regardless of what the message looks like), so it does not
rise to Critical, but it is a real, unhandled edge case in the very code this plan wrote to fix a
message-correctness defect.

**Fix:** Escape only the delimiter character on the way in, leaving every other character
(including backslashes) untouched, e.g.:

```python
def _quote_path_value(value: str) -> str:
    """Quote a filesystem-path value for a user-facing message without
    repr()'s backslash-doubling, while still disambiguating an embedded
    single quote."""
    return "'" + value.replace("'", "\\'") + "'"
```

and use `_quote_path_value(bundle_dir)` etc. in place of the bare `'{bundle_dir}'` f-string
segments in all three functions. This preserves the fix's Windows behavior (a lone backslash
stays a lone backslash) while restoring unambiguous delimiting for the embedded-quote case.

## Info

### IN-01: No regression test for a path value containing a single quote

**File:** `tests/test_templates_path_collision_gate.py` (`TestWindowsPathEscapingRegressionGuard`)

**Issue:** The new `TestWindowsPathEscapingRegressionGuard` class thoroughly covers the
backslash-doubling regression this plan fixes (four tests, all driving the real
message-construction functions), but does not exercise the embedded-single-quote case described
in WR-01 above. Given this class exists specifically to make a previously CI-only-visible defect
class locally detectable, it is a natural home for a sibling assertion once WR-01 is addressed.

**Fix:** Add a test alongside the existing four that passes a hand-built path value containing a
literal `'` (e.g. `"/home/o'brien/_templates"`) through each of the three message functions and
asserts the value is recoverable/unambiguous in the output (e.g. no unescaped `'` other than the
two delimiters, or whatever invariant the WR-01 fix establishes).

---

_Reviewed: 2026-08-22_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
