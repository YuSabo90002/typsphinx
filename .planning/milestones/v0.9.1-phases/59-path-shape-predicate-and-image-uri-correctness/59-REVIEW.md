---
phase: 59-path-shape-predicate-and-image-uri-correctness
reviewed: 2026-08-28T21:38:20Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - typsphinx/builder.py
  - typsphinx/translator.py
  - tests/test_path_shape_predicate_gate.py
  - tests/test_track_image_key_construction.py
  - tests/test_copy_image_files_name_too_long.py
  - tests/test_image_literal_escaping_gate.py
  - tests/test_windows_image_uri_render_gate.py
  - tests/fixtures/windows_shaped_image_uri_gate/conf.py
  - tests/fixtures/windows_shaped_image_uri_gate/index.rst
findings:
  critical: 1
  warning: 1
  info: 1
  total: 3
status: issues_found
---

# Phase 59: Code Review Report

**Reviewed:** 2026-08-28T21:38:20Z
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

Reviewed the PATH-01 (`_escapes_outdir()` single-normalization), IMG-04/IMG-06
(`_build_relocation_key()` / `_bound_relocation_component()`), and IMG-05
(`visit_image()` escape-last wiring) changes in `typsphinx/builder.py` and
`typsphinx/translator.py`, plus the five new test files/fixtures that gate
them.

`_is_absolute_image_uri()`, `_escapes_outdir()`, `_build_relocation_key()`,
and `visit_image()`'s single-`escaped_uri` wiring were traced against the
project's own doctests, the new test suites, and hand-constructed edge
cases; all of that surface behaves as documented. The full test suite
(1469 passed, 1 skipped) and `mypy`/`ruff` both stay green after this
phase's changes.

However, direct execution of `_bound_relocation_component()` against an
input shape none of the new tests exercise — a stem that *starts* with a
multi-byte UTF-8 character and a budget tight enough to allocate the stem
only 1-2 bytes — reproducibly violates the function's own documented D-07
"the stem is never emptied" invariant: the stem is silently dropped to
`""` rather than surviving as at least one full character. This is exactly
the class of edge case the phase brief asked this review to scrutinize
("multi-byte truncation, empty-stem ... edge cases"), and no existing gate
(new or old) drives an input that reaches it, so it shipped uncaught.

## Critical Issues

### CR-01: `_bound_relocation_component()` empties the stem for a multi-byte leading character, violating its own documented D-07 invariant

**File:** `typsphinx/builder.py:334-343` (the reservation site is `builder.py:336`, `budget - len(ext_bytes)` is computed at `builder.py:330-332`)

**Issue:**

The function's docstring and inline comments state the truncation
precedence explicitly: the `{digest}-` prefix survives whole, "then at
least one byte of stem; then the extension" (`builder.py:278-282`), and
line 336's own comment reads `# D-07: never empty`. The arithmetic that
backs this claim (`stem_budget = budget - len(ext_bytes)`, guaranteed
`>= 1`) only reserves a **byte count**, not a **complete UTF-8 character**.
When the stem's first character requires more bytes than `stem_budget`
provides (common whenever `stem_budget` is 1-3 and the stem starts with a
non-ASCII character), `stem_bytes[: max(stem_budget, 1)]` slices mid
character. The boundary-walk-back loop at lines 337-342 then backs off
byte-by-byte looking for a valid UTF-8 prefix — but no valid non-empty
prefix exists below the character's own byte length, so the loop backs
all the way to `b""`, which decodes successfully as `""`. The stem is
dropped entirely, and — worse — the *extension* (lower priority per the
documented precedence) keeps nearly its whole allotment while the
*stem* (higher priority) gets nothing: the precedence order documented
at lines 278-282 is inverted in practice for this input class.

Reproduced directly against the shipped function (no builder, no
filesystem):

```python
>>> from typsphinx.builder import _bound_relocation_component
>>> digest = "a1b2c3d4"
>>> ext = "." + "e" * 244          # 245 bytes -- 1 byte under the 246-byte budget
>>> basename = "図" + ext          # "図" is a single 3-byte UTF-8 character
>>> result = _bound_relocation_component(digest, basename)
>>> result
'a1b2c3d4-.eeeeeeeeeeee...eeeeee'   # note: NO "図" survives -- stem is ""
>>> len(result.encode("utf-8"))
254
```

This does not require the "extension truncation" branch (lines 317-330)
at all — it reproduces in the plain `else` branch (line 331-332) whenever
an ordinary (non-truncated) extension happens to leave `stem_budget` below
the byte length of the stem's leading character. It also reproduces (with
`stem_budget == 1`) inside the extension-truncation branch, e.g. via
`_bound_relocation_component("a1b2c3d4", "図" + "." + "e" * 300)`.

None of this phase's new tests catch it:
`test_length_bound_encoding_cjk_round_trips_and_stays_at_most_255` uses a
CJK stem with a short `.png` extension, leaving `stem_budget=242` (far
above any single character's byte length), and
`test_length_bound_precision_budget_and_extension_truncation` drives
`stem_budget=1` but with an ASCII stem (`"s"`, 1 byte, survives fine) — the
two load-bearing conditions (multi-byte leading character *and* a tight
`stem_budget`) are never combined in the same test case.

**Impact:** For an absolute image URI whose relocated basename starts with
a non-ASCII character and has a long enough trailing "extension" (as
`posixpath.splitext()` defines it — everything after the last `.`), the
emitted relocation-key filename loses all trace of the original basename,
contradicting the function's documented contract and this phase's own
stated truncation precedence. It is not a crash and, because the `sha1`
digest is still derived from the full un-truncated `resolved_uri`, it does
not by itself cause a filename collision between two different URIs — but
it is a real, reproducible correctness defect against a decision (D-07)
this phase explicitly locked in and asked reviewers to verify.

**Fix:** When the boundary walk-back would empty the stem, borrow bytes
back from the extension's own allotment instead of accepting `""` — i.e.
guarantee the stem's *first character* survives whenever the total
budget can afford it, matching the documented "stem before extension"
precedence:

```python
stem_bytes = stem.encode("utf-8")
if len(stem_bytes) > stem_budget:
    truncated = stem_bytes[: max(stem_budget, 1)]
    while truncated:
        try:
            stem = truncated.decode("utf-8")
            break
        except UnicodeDecodeError:
            truncated = truncated[:-1]
    else:
        # D-07: stem_budget wasn't even enough to hold the stem's own
        # first UTF-8 character -- borrow bytes back from the
        # (lower-priority) extension so at least one full stem
        # character survives, per the documented precedence.
        first_char_bytes = stem[0].encode("utf-8")
        stem = stem[0]
        remaining_ext_budget = max(budget - len(first_char_bytes), 0)
        trimmed_ext_bytes = ext.encode("utf-8")[:remaining_ext_budget]
        while trimmed_ext_bytes:
            try:
                ext = trimmed_ext_bytes.decode("utf-8")
                break
            except UnicodeDecodeError:
                trimmed_ext_bytes = trimmed_ext_bytes[:-1]
        else:
            ext = ""
```

Add a regression test combining both load-bearing conditions, e.g.
`_bound_relocation_component("a1b2c3d4", "図" + "." + "e" * 244)` asserting
the result contains `"図"`.

## Warnings

### WR-01: Duplicated `stem_budget` formula across both branches of the extension-length check

**File:** `typsphinx/builder.py:317-332`

**Issue:** Both the `if len(ext_bytes) >= budget:` branch (line 330) and
its `else:` (line 332) compute the identical expression
`stem_budget = budget - len(ext_bytes)`. The only thing that differs
between the branches is whether `ext_bytes`/`ext` were reassigned above
it. This is harmless today, but it is exactly the kind of duplication
that let CR-01 hide: a future edit to one branch's formula (e.g. to fix
CR-01) is easy to apply to only one of the two copies, silently
reintroducing the bug in the other branch.

**Fix:** Hoist the shared computation once, after the `if/else` that
conditionally truncates `ext_bytes`, e.g.:

```python
if len(ext_bytes) >= budget:
    ext_bytes = ext_bytes[: max(budget - 1, 0)]
    while ext_bytes:
        ...
    else:
        ext = ""
stem_budget = budget - len(ext_bytes)
```

## Info

### IN-01: No test combines a multi-byte leading stem character with a tight `stem_budget`

**File:** `tests/test_track_image_key_construction.py:99-260`

**Issue:** `TestRelocationKeyLengthBound`'s CJK case
(`test_length_bound_encoding_cjk_round_trips_and_stays_at_most_255`) and
its tight-budget case
(`test_length_bound_precision_budget_and_extension_truncation`) each cover
one of CR-01's two load-bearing conditions (multi-byte stem; `stem_budget`
near 1) but never both together, which is why CR-01 shipped despite this
phase's otherwise thorough length-bound test coverage.

**Fix:** Add the regression case suggested in CR-01's fix section (or an
equivalent) to this class once CR-01 is fixed, so the invariant this
class's docstring already claims to cover ("D-08(a)'s pure-string
property gates") is actually exercised for this combination.

---

_Reviewed: 2026-08-28T21:38:20Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
