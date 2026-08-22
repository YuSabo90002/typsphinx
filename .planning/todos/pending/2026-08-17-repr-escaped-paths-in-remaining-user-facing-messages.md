---
created: 2026-08-17
title: "Path-valued `!r` interpolations remain in user-facing messages OUTSIDE the three refusal sites 57-11 fixed -- each doubles backslashes in the emitted message on Windows"
area: builder, writer, template_registry
resolves_phase: unassigned
severity: minor
source: 57-11 task 1's whole-file `!r` census over typsphinx/, taken from the DEFECT PROPERTY
  ("a filesystem path interpolated with !r into a message a user is expected to read and act
  on") rather than from the single line CI named. Filed per 57-11-PLAN.md task 3 step 4.
files:
  - typsphinx/builder.py       # v0.8.0-era output-path collision family (lines ~875-948)
  - typsphinx/builder.py       # bundle-copy I/O failure messages (lines ~1992-2007, post-refactor line numbers)
  - typsphinx/builder.py       # docname target-name warnings (lines ~628-632)
  - typsphinx/builder.py       # image-rehome warning (line ~1706-1707)
  - typsphinx/writer.py        # wrapper-render debug log (lines ~511-513)
  - typsphinx/template_registry.py  # declared-template validation failures (lines ~410, ~422, ~433)
---

## Problem

57-11 fixed the Windows-only backslash-doubling defect (CI runs `31956166848` and
`31959060298`) at exactly THREE refusal sites in `typsphinx/builder.py` -- the ones in the
**pre-write template-path refusal family** this milestone's `typst_document_templates` registry
introduced: the `templates_path` collision refusal, the srcdir-ancestor refusal (both via the
shared `_conf17_violation_message()` / new `_templates_path_collision_message()` /
`_bundle_destination_collision_message()` helpers), and the bundle-destination collision
refusal.

Task 1's full `!r` census (taken from the property -- "the interpolated value is a filesystem
path or path fragment, so `repr()` will escape it on Windows" -- not from the single line CI
happened to name) found the SAME defect shape at several OTHER sites, all left unchanged by
57-11 because they fall outside the deliberately narrow fix scope (a release-prep phase should
not widen a message rewrite across the codebase). Each site below is path-valued `!r`, `repr()`
of a value that can contain `os.sep`:

1. **`typsphinx/builder.py`'s v0.8.0-era output-path collision family** (`_claim()`'s message,
   the content-file/wrapper-file reservation messages) -- `relpath!r`, `content_relpath!r`,
   `wrapper_relpath!r`, `TEMPLATE_OUTPUT_DIR!r`, and `target!r` (the raw `typst_documents`
   target, which `_escapes_outdir()` already treats as potentially path-bearing). This is a
   DIFFERENT, older refusal family (BLD-02/BLD-03/BLD-04/OUT-07) than the one 57-11 touched --
   explicitly out of scope per the plan's own exclusion of "v0.8.0-era output-path collision
   messages" from the fix.

2. **`typsphinx/builder.py`'s bundle-copy I/O failure messages** (inside the per-file copy loop
   and the "template never copied" check) -- `src_file!r`, `dest_file!r`, `src_dir!r`,
   `dest_dir!r`, `template_filename!r`. These are `raise ExtensionError(...)` sites, but for a
   different failure class (a copy operation failing, or the resolved template file
   unexpectedly absent after the copy loop) than the three "pre-write template-path refusal"
   sites this plan named.

3. **`typsphinx/builder.py`'s docname target-name warnings** (`_wrapper_output_relpath()` and
   its callers) -- `target!r`, `fallback!r` in `logger.warning(...)` calls when a
   `typst_documents` target contains an unsupported path. Explicitly out of scope: the plan
   names "debug/warning logs" as excluded from the fix.

4. **`typsphinx/builder.py`'s image-rehome warning** -- `resolved_uri!r` in a `logger.warning(...)`
   when an absolute image URI could not be rehomed relative to the doctree directory. Same
   debug/warning-log exclusion.

5. **`typsphinx/writer.py`'s wrapper-render debug log** -- `wrapper_relative_dir!r`,
   `include_path!r`, `template_file!r` in a `logger.debug(...)` call. Same exclusion.

6. **`typsphinx/template_registry.py`'s declared-template validation failures** -- `template!r`
   at three `raise ExtensionError`-feeding `failures.append(...)` sites (type-check failure,
   CONF-17 violation, existence check). These ARE refusal messages (not warnings/debug logs),
   and the interpolated `template` value is the user's declared, possibly path-separator-bearing
   string -- the same defect SHAPE as the three sites 57-11 fixed, but in a different file and a
   different validation path (`validate_registry()`, not the pre-write builder checks). Left
   unchanged because the plan's scope was bounded to `typsphinx/builder.py`'s three named sites.

Identifier-valued `!r` (registry keys via `{key!r}`, docnames via `{docname!r}`, config tuples
via `{entry!r}`/`{doc_tuple!r}`, and the toctree-depth `master_docname!r`/`path[0]!r`/`path[-1]!r`
in `typsphinx/translator.py`, which are docnames despite the variable being named `path`) is
CORRECTLY `!r` everywhere in the codebase and needs no change -- listed here only to record that
the census covered it and classified it out.

## Why this was deferred rather than fixed in 57-11

Phase 57 is release prep for v0.9.0 with a prep-only fence; 57-11 already knowingly breaks that
fence once, by explicit owner decision, to fix the one Windows-only defect two CI matrix
dispatches surfaced. Widening that single owner-approved exception into a codebase-wide message
rewrite during release prep is a materially larger and differently-shaped risk (T-57-73 in
57-11's threat register) -- each additional site changes more user-facing text nobody has
reviewed, for defects that have NOT been observed failing any test or CI run (unlike the three
sites that did).

## Suggested fix (future phase)

For each site above that is a genuine refusal (2 and 6), apply the same non-escaping quoting
57-11 used: replace `{value!r}` with `'{value}'` for path-valued interpolations only, leaving
`{key!r}`/`{docname!r}` untouched. For the warning/debug-log sites (3, 4, 5) and the v0.8.0-era
collision family (1), the same fix is a smaller behavioral risk (they are not refusal-blocking
messages) but should still go through the same "zero test edits proves POSIX-identical output"
discipline 57-11 task 1 step 3 established, plus a Windows-shape check per 57-11 task 2's
pattern, before landing.
