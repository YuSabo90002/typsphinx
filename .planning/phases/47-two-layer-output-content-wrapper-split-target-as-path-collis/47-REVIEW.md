---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
reviewed: 2026-08-12T00:00:00Z
depth: standard
files_reviewed: 15
files_reviewed_list:
  - typsphinx/builder.py
  - typsphinx/writer.py
  - tests/test_collision_predicate_completeness_gate.py
  - tests/test_entry_metadata_precedence.py
  - tests/test_document_metadata_render_gate.py
  - tests/test_pdf_generation.py
  - tests/fixtures/bld02_path_shape_collision_gate/conf.py
  - tests/fixtures/bld02_path_shape_collision_gate/index.rst
  - tests/fixtures/bld02_path_shape_collision_gate/other.rst
  - tests/fixtures/bld02_template_clobber_gate/conf.py
  - tests/fixtures/bld02_template_clobber_gate/index.rst
  - tests/fixtures/bld03_under_length_entry_gate/conf.py
  - tests/fixtures/bld03_under_length_entry_gate/index.rst
  - tests/fixtures/bld03_under_length_entry_gate/other.rst
  - tests/fixtures/entry_title_author_render_gate/conf.py
findings:
  critical: 1
  warning: 1
  info: 1
  total: 3
status: issues_found
---

# Phase 47: Code Review Report (gap-closure supersedes prior 47-REVIEW.md)

**Reviewed:** 2026-08-12T00:00:00Z
**Depth:** standard
**Files Reviewed:** 15
**Status:** issues_found

## Summary

This is the gap-closure review for plans 47-11 and 47-12, which set out to
close CR-01 (per-entry collision fallback), CR-02 (predicted `_template.typ`
clobber), and WR-01 (dead `_resolve_entry_element`) from the prior
`47-REVIEW.md`. All three prior findings are verified fixed:

- **CR-01 (prior)**: `_resolve_target_stem()` no longer silently
  falls back per-entry; collisions are now caught structurally by
  `_validate_output_path_collisions()` before any file is written. Verified.
- **CR-02 (prior)**: `_collision_key()` now runs `posixpath.normpath()`
  before `casefold()`, so `./manual.typ` collides with `manual.typ` and a
  `./`-shaped target that resolves to `_template.typ` is caught. Verified
  via `tests/fixtures/bld02_path_shape_collision_gate/` and
  `tests/fixtures/bld02_template_clobber_gate/`, both of which drive a real
  `sphinx-build` subprocess and assert `returncode != 0` plus zero `.typ`
  files written on collision.
- **WR-01 (prior)**: `_resolve_entry_element()` is confirmed deleted from
  `typsphinx/writer.py` with no dangling references anywhere in
  `typsphinx/` (only historical/comment references survive in test
  docstrings, correctly describing it as removed). `_entry_element_value()`
  is the sole surviving positional resolver and is the only one
  `render_wrapper()` calls.

`_is_usable_typst_documents_entry()` is genuinely wired into the four
sites its own docstring claims cover (`_validate_output_path_collisions()`,
`write()`'s D-07 report, `_write_typst_files()`'s wrapper loop, and
`TypstPDFBuilder.finish()`) — confirmed by direct reading and by the
`git diff` against the pre-gap-closure commit. The eleven gate tests in
`tests/test_collision_predicate_completeness_gate.py` all currently pass,
and the commit history (`5491d65`) records that 9 of the 11 failed before
the fix, i.e. these are not vacuous assertions.

However, this same refactor left a **fifth, related site** —
`_compute_master_included_docnames()` — consuming raw `typst_documents`
entries with its own, weaker, hand-rolled predicate (`if entry`) instead of
the new single source of truth. This is exactly the class of defect BLD-03
existed to eliminate, just in a location the refactor's own docstring
didn't enumerate. I reproduced both a build-crashing and a silent-
correctness failure mode from it (see CR-01 below) with a standalone
script against the actual `TypstBuilder` class. This is a BLOCKER.

I also found that `_resolve_output_stem()` — the docname-based first-match
lookup this phase's own D-04 decision (in `_wrapper_output_relpath()`'s
docstring) says was deliberately bypassed for wrapper-path resolution — now
has **zero production call sites** anywhere in `typsphinx/`. It is reachable
only from `tests/test_builder_output_stem.py`'s ~25 direct unit-test
invocations. This is the same dead-code pattern the prior review's WR-01
already caught and this gap-closure wave fixed for `_resolve_entry_element()`
— the sibling case in `builder.py` was missed.

## Critical Issues

### CR-01: `_compute_master_included_docnames()` bypasses the single entry-usability predicate — crashes the build or silently corrupts cross-document link degradation

**File:** `typsphinx/builder.py:268-282`

**Issue:**

`_is_usable_typst_documents_entry()`'s own docstring (lines 106-153) states
it is "the SINGLE source of truth ... consulted by all FOUR sites that
resolve a wrapper path", and 47-11 wired it into those four. But
`_compute_master_included_docnames()` reads the same `typst_documents`
config list to build `self.master_included_docnames` (the set the
translator's cross-reference-degrade decision consults at
`typsphinx/translator.py:3073-3075` to decide whether a `:doc:`/`:ref:`
target gets a real Typst `link(<label>)` or degrades to plain text) and
still uses its own, pre-BLD-03, ad-hoc predicate:

```python
typst_documents = getattr(self.config, "typst_documents", []) or []
masters = [entry[0] for entry in typst_documents if entry]   # <-- not _is_usable_typst_documents_entry()
```

This diverges from the canonical predicate in two independently
demonstrable ways (both reproduced against the real `TypstBuilder` class):

1. **Silent correctness bug.** A `typst_documents` entry with fewer than
   two elements (e.g. `("other_master",)` — the exact BLD-03 shape this
   phase's own fixtures use, see
   `tests/fixtures/bld03_under_length_entry_gate/conf.py`) produces NO
   wrapper file anywhere (`_is_usable_typst_documents_entry` correctly
   rejects it at all four guarded sites). But because `if entry` alone is
   truthy for a 1-tuple, `_compute_master_included_docnames()` still walks
   its docname's toctree closure and adds every descendant to
   `master_included_docnames`. Any REAL master's cross-reference into that
   docname's subtree is then treated as "safe to link" and emits a real
   Typst `link(<label>)` — but the target file was never physically
   `#include()`d into any compiled wrapper, so `typst.compile()` fails
   with `label ... does not exist` on the very fatal this mechanism exists
   to prevent. Reproduced directly:

   ```
   >>> b.config.typst_documents = [
   ...     ('real_master', 'manual.typ', 'T', 'A'),
   ...     ('other_master',),
   ... ]
   >>> b._compute_master_included_docnames()
   {'real_master', 'other_master', 'other_child'}   # other_child wrongly included
   ```

2. **Uncaught crash.** `_is_usable_typst_documents_entry()` requires
   `isinstance(entry[0], str)` specifically because the SAME docname value
   is later used as a `dict`/`set` key throughout the collision validator.
   `_compute_master_included_docnames()` has no such check, and its BFS
   uses `docname in included` (a `set`) and `included.add(docname)`. An
   entry whose first element is an unhashable type (e.g. a user typo like
   `(["weird"], "t.typ")` in `conf.py` — config values are user-authored
   and not type-checked by Sphinx) crashes `write()` with an **uncaught
   `TypeError`**, not the graceful `logger.warning`-and-skip every other
   site in this file now guarantees:

   ```
   >>> b.config.typst_documents = [(['weird'], 'manual.typ', 'T', 'A')]
   >>> b._compute_master_included_docnames()
   TypeError: unhashable type: 'list'
   ```

   This directly contradicts this method's own docstring ("no masters /
   unknown" is the only documented degraded case) and the file-wide BLD-03
   design principle that a malformed `typst_documents` entry is "TOLERATED
   AND SKIPPED ... it never raises there" (from
   `_is_usable_typst_documents_entry()`'s own docstring, lines 127-131).

Neither failure mode is covered by any existing test —
`tests/test_citation_degradation_gate.py` and
`tests/test_xref_orphan_degrade_render_gate.py` construct
`master_included_docnames` directly on a stub builder rather than through
`_compute_master_included_docnames()`, so this method's own predicate
never gets exercised against a malformed entry anywhere in the suite.

**Fix:**

```python
def _compute_master_included_docnames(self) -> set[str]:
    typst_documents = getattr(self.config, "typst_documents", []) or []
    masters = [
        entry[0]
        for entry in typst_documents
        if _is_usable_typst_documents_entry(entry)
    ]
    ...
```

This makes `_compute_master_included_docnames()` the fifth site consuming
the single predicate, closes the crash (a non-`str`/unhashable `entry[0]`
is now rejected before it ever reaches the BFS), and closes the
dangling-label case (an entry that produces no wrapper is never treated as
contributing to a compiled master's include closure). Add a regression
test alongside `tests/test_collision_predicate_completeness_gate.py`
driving a real `sphinx-build` with a `typst_documents` mixing a valid
master and a `("docname",)` under-length entry whose toctree pulls in a
document a real master's content cross-references — asserting the build
either degrades that reference or excludes the under-length entry's
subtree from `master_included_docnames`, not both silently link and never
include.

## Warnings

### WR-01: `_resolve_output_stem()` is dead production code, mirroring the prior review's already-fixed `_resolve_entry_element()`

**File:** `typsphinx/builder.py:284-324`

**Issue:**

`_resolve_output_stem()` (docname-based first-match lookup over
`typst_documents`, delegating to `_resolve_target_stem()` once a match is
found) has no production call sites anywhere in `typsphinx/` —
confirmed by `grep -rn "_resolve_output_stem" typsphinx/`, which returns
only the method's own definition and docstring cross-references (none of
them a call). Every actual write/read-back site
(`_content_output_path()`, `_write_typst_files()`'s wrapper loop,
`_validate_output_path_collisions()`, `TypstPDFBuilder.finish()`) reaches
output paths via `_content_output_path()` (docname-derived, unconditional)
or `_wrapper_output_relpath()` → `_resolve_target_stem()` directly — the
very design `_wrapper_output_relpath()`'s own docstring (lines 934-960)
explains was deliberately introduced to bypass `_resolve_output_stem()`'s
docname-based first-match search, precisely so that D-04's
repeated-docname-different-target case resolves correctly.

This is structurally the same defect class as the prior review's WR-01
(`_resolve_entry_element()`, deleted by 47-12): a resolver superseded by a
per-entry-positional replacement, kept alive only by direct unit-test
invocation (`tests/test_builder_output_stem.py`, ~25 assertions calling
`builder._resolve_output_stem(...)` directly) rather than any real build
path. `test_entry_metadata_precedence.py`'s own module docstring states
the rationale for why this matters: "a green test suite exercising a
route no build ever reaches reports false confidence" — that concern
applies identically here and was not addressed by this gap-closure wave.

The method's own docstring also still describes itself in present-tense
production terms ("This is the docname-based entry lookup ... every
write/read-back site reaches that same normalization through one of these
two methods, never re-deriving the rule") — which is no longer accurate;
only `_resolve_target_stem()` is reached by write/read-back sites now.

**Fix:** Delete `_resolve_output_stem()` from `typsphinx/builder.py` and
retarget `tests/test_builder_output_stem.py`'s assertions onto
`_resolve_target_stem(docname, target)` directly (mirroring exactly how
`47-12-PLAN.md` retargeted `test_entry_metadata_precedence.py`'s Group 1
from `_resolve_entry_element()` onto `_entry_element_value()`). If any
call site is later found to still need docname-based lookup, reintroduce
it deliberately with a comment explaining the new need, rather than
leaving the superseded version in place "just in case."

## Info

### IN-01: `_is_drive_qualified()`'s docstring names the wrong caller

**File:** `typsphinx/builder.py:27-59` (specifically lines 33-40)

**Issue:** The docstring says "both `_escapes_outdir()` ... and
`_resolve_output_stem()` ... call this rather than each re-deriving the
... check independently". `_resolve_output_stem()` does not call
`_is_drive_qualified()` at all (it only delegates to
`_resolve_target_stem()`); the actual second caller is
`_resolve_target_stem()` (line 388: `is_drive_qualified =
_is_drive_qualified(stem)`). This is a symptom of the same drift WR-01
describes — the docstring was written when `_resolve_output_stem()` was
still doing the work `_resolve_target_stem()` now does alone.

**Fix:** Replace `` `_resolve_output_stem()` `` with `` `_resolve_target_stem()` ``
in the docstring text (and again if WR-01's fix removes
`_resolve_output_stem()` entirely, this reference becomes moot).

---

_Reviewed: 2026-08-12T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
