---
phase: 53-template-registry-foundation
reviewed: 2026-08-15T09:19:15Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - typsphinx/template_registry.py
  - typsphinx/template_engine.py
  - typsphinx/writer.py
  - typsphinx/builder.py
  - typsphinx/__init__.py
  - tests/test_template_registry.py
  - tests/test_template_engine.py
  - tests/test_state_guard_shapes_gate.py
findings:
  critical: 2
  warning: 3
  info: 0
  total: 5
status: issues_found
---

# Phase 53: Code Review Report

**Reviewed:** 2026-08-15T09:19:15Z
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

This phase adds `typst_document_templates` registry resolution
(`typsphinx/template_registry.py`), threads a resolved `TemplateRegistryEntry`
through `writer.render_wrapper()` and `builder.py`'s write path, and adds a
`path` field to `TemplateEngine.TemplateResolution`. The byte-identity
requirement for an untouched `conf.py` is respected: the synthesized `"typst"`
key is built verbatim from the existing three globals, and every new
validation branch is gated behind `typst_document_templates` actually being
populated. The accumulate-then-raise-once shape mirrors
`_validate_output_path_collisions()` faithfully for the six checks it does
run (CONF-15/16/17/18, D-08).

Two things did not get the same rigor as the rest of the module, both
confirmed by direct execution against the reviewed code (not conjecture):

1. The seven-case key-shape denylist is missing an eighth case the codebase
   already knows it needs elsewhere (`_is_drive_qualified()` in
   `builder.py`) — a bare Windows drive-qualified key such as `"C:"` passes
   every one of the seven checks unrejected. Given the phase's own stated
   purpose ("registry keys become directory names in the next phase"), this
   is exactly the class of gap the phase exists to close.
2. `_violates_conf17()` calls `os.path.commonpath()` without handling the
   `ValueError` it raises for cross-drive paths on Windows — which crashes
   the build with an unhandled Python exception on exactly the scenario the
   module's own tests document as legal (`test_conf17_absolute_template_path_outside_srcdir_resolves`,
   just not cross-drive).

Additionally, CONF-14 key-reference validation (an `typst_documents` entry
naming an unregistered key) is deferred to a lazy, per-entry check reached
mid-write-loop, rather than validated up front alongside the other five
registry checks — breaking the "no output file is written when validation
fails" invariant `_validate_output_path_collisions()` established elsewhere
in this same builder. Two more accumulate-then-raise robustness gaps
(non-`str` registry keys, non-`dict` definition values) crash with a raw
`AttributeError` instead of the module's own clean `ExtensionError` contract.

## Critical Issues

### CR-01: Registry key-shape denylist does not reject drive-qualified keys (e.g. `"C:"`)

**File:** `typsphinx/template_registry.py:101-134`
**Issue:** `_validate_registry_key_shape()`'s seven checks reject a path
separator (`/`/`\`), Windows reserved device names, `.`/`..`, trailing
dot/space, empty/whitespace, and case collisions — but never test for a
drive-qualified prefix (`<ASCII letter><colon>`, e.g. `"C:"` or `"C:foo"`).
This is precisely the shape `builder.py`'s own `_is_drive_qualified()` /
`_escapes_outdir()` reject for `typst_documents` *target* stems, with the
docstring there noting drive-qualification must be checked "on every
platform" because "a Windows-authored conf.py is refused identically on
POSIX CI." That same platform-independence reasoning was not applied to
registry *keys* here, even though this module's own docstring says these
keys "become DIRECTORY NAMES in the next phase."

Verified directly against the reviewed code:
```
>>> from typsphinx.template_registry import _validate_registry_key_shape
>>> _validate_registry_key_shape("C:", set())
None   # accepted -- should be rejected
>>> _validate_registry_key_shape("C:foo", set())
None   # accepted -- should be rejected
```
Once Phase 54 joins a registry key into a directory path, a bare
drive-qualified key can silently redirect a Windows build's output onto a
different drive root (the exact class of escape `_is_drive_qualified` /
`_escapes_outdir` already exist to prevent for target stems) — this is a
real, not hypothetical, path-escape vector for the very feature this phase
says it is laying the foundation for.

The test suite's own "deliberately accepted shapes" list
(`test_registry_key_deliberately_accepted_shapes_resolve_without_raising`)
enumerates four intentionally-accepted shapes (`"paper:v2"`, a control
character, a leading dot, interior whitespace) but does not include a
drive-qualified key — this was not a conscious exclusion, it was never
considered.

**Fix:**
```python
# in typsphinx/template_registry.py
from typsphinx.builder import _is_drive_qualified  # or duplicate the 2-line predicate locally to avoid the existing circular-import concern

_KEY_SHAPE_REJECTION_CASES = (
    "empty_or_whitespace_only",
    "dot_or_dotdot",
    "contains_path_separator",
    "drive_qualified",          # new eighth case
    "windows_reserved_device_name",
    "trailing_dot",
    "trailing_space",
    "case_collision",
)

def _validate_registry_key_shape(key, other_keys):
    ...
    if len(key) >= 2 and key[0].isalpha() and key[1] == ":":
        return f"registry key {key!r} is drive-qualified, which is not legal in a single-segment registry key"
    ...
```
(This also means the module's own "exactly seven" invariant test,
`test_key_shape_validator_exposes_exactly_seven_distinct_rejection_reasons`,
must be updated to eight alongside the fix.)

### CR-02: `_violates_conf17()` crashes with an unhandled `ValueError` on a cross-drive absolute template path (Windows)

**File:** `typsphinx/template_registry.py:137-158`
**Issue:** `os.path.commonpath([norm_srcdir, parent])` raises `ValueError:
Paths don't have the same drive` when its two arguments are absolute paths
on different Windows drives. The function does not catch this. The
module's own docstring and test suite (`test_conf17_absolute_template_path_outside_srcdir_resolves`)
explicitly document "an absolute template path OUTSIDE srcdir stays legal"
as an accepted case — but that test only exercises a same-drive sibling
directory, never a genuine cross-drive path, so the crash path is untested.

Verified by replaying the exact function body against `ntpath` (i.e.
simulating real Windows path semantics, since this repo's CI runs a
`windows-latest` lane per its own comments elsewhere in `builder.py`):
```
>>> import ntpath as os_path
>>> os_path.commonpath([os_path.normpath(os_path.abspath("C:\\srcdir")),
...                      os_path.normpath(os_path.dirname(os_path.abspath("D:\\templates\\tpl.typ")))])
ValueError: Paths don't have the same drive
```
This crashes with a raw, unhandled Python exception (surfacing to the user
as an internal-error traceback, not this module's own clean
`ExtensionError`) on exactly the scenario the module documents as legal.
This is the same class of hazard `builder.py`'s `_track_image()` already
guards against explicitly (`except ValueError: # D-07: Windows cross-drive
relpath() crash`) — that established pattern was not carried over here.

**Fix:**
```python
def _violates_conf17(template_abs_path: str, srcdir: str) -> bool:
    parent = os.path.normpath(os.path.dirname(os.path.abspath(template_abs_path)))
    norm_srcdir = os.path.normpath(os.path.abspath(srcdir))
    try:
        return os.path.commonpath([norm_srcdir, parent]) == parent
    except ValueError:
        # Cross-drive paths (Windows) can never share an ancestor -- not
        # a CONF-17 violation, mirrors builder.py's own cross-drive
        # relpath() handling in _track_image().
        return False
```

## Warnings

### WR-01: CONF-14 (unregistered `typst_documents` registry-key reference) is validated too late, breaking the "no output written on failure" invariant

**File:** `typsphinx/builder.py:1111-1131`, `typsphinx/template_registry.py:333-389`
**Issue:** `_validate_output_path_collisions()` runs "once, called from
`write()` at the very top... so 'no output file is written when any
collision is found' is structural" (its own docstring, `builder.py:517-528`).
`resolve_template_registry()` mirrors that same up-front,
accumulate-then-raise-once pattern for CONF-15/16/17/18 and D-08
(`builder.py:730-739`, before `prepare_writing()`). CONF-14 — a
`typst_documents` entry whose fifth element names a key absent from the
resolved registry — is the one registry-related validation that does
*not* get this up-front treatment: `resolve_registry_key()` is only ever
called from inside `_write_typst_files()`'s per-entry wrapper loop
(`builder.py:1121`), which runs *after* that docname's own content file
(and any earlier docnames' content + wrapper files, since `write()`
processes `sorted(docnames)`) have already been written to disk.

Concretely: a build with masters `"alpha"` and `"beta"` (in that sort
order), where `"beta"`'s entry names a nonexistent registry key, will
write `alpha`'s content file, `alpha`'s wrapper file, and `beta`'s own
content file to disk *before* `resolve_registry_key()` raises for
`beta`'s wrapper. The build still fails loudly (an `ExtensionError` is
still raised), but it leaves partial `.typ` output on disk from a failed
build — exactly the state `_validate_output_path_collisions()`'s own
docstring says is structurally prevented for the sibling class of
registry problems it decided to validate up front. No existing test
(`tests/test_template_registry.py`'s own `test_resolve_registry_key_bad_key_fails_identically_regardless_of_master_order`
included) exercises this through the real `write()` path — it only calls
`resolve_registry_key()` directly against an in-memory registry, so the
partial-write behavior is unobserved by the test suite.

**Fix:** Validate every `typst_documents` entry's registry-key reference
in the same up-front pass that already resolves the registry in `write()`,
before `prepare_writing()`:
```python
self._document_template_registry = resolve_template_registry(
    self.config, str(self.srcdir)
)
typst_documents = getattr(self.config, "typst_documents", []) or []
for entry in typst_documents:
    if _is_usable_typst_documents_entry(entry):
        resolve_registry_key(self._document_template_registry, entry)  # raises early
```

### WR-02: Non-`str` registry key crashes with a raw `AttributeError` instead of a clean `ExtensionError`

**File:** `typsphinx/template_registry.py:239-247`
**Issue:** `typst_document_templates` is registered with `[dict]` typing
only (`typsphinx/__init__.py:63`) — Sphinx validates the outer container is
a `dict`, not that its keys are `str`. `resolve_template_registry()`
filters `all_keys` to `isinstance(key, str)` for the case-collision set,
but the main validation loop iterates `sorted(declared.keys())` unfiltered
and immediately calls `key.strip()` inside `_validate_registry_key_shape()`,
which is not defined for a non-`str` key.

Verified directly:
```
>>> config.typst_document_templates = {42: {}}
>>> resolve_template_registry(config, "/tmp")
AttributeError: 'int' object has no attribute 'strip'
```
This is a misconfiguration a user could plausibly hit (e.g. a stray
integer or tuple key from a templated `conf.py`), and every other
malformed-input path in this module produces a clean, accumulated
`ExtensionError` — this one produces an unhandled internal crash instead.

**Fix:**
```python
for key in sorted(declared.keys(), key=lambda k: (not isinstance(k, str), repr(k))):
    if not isinstance(key, str):
        failures.append(f"registry key {key!r} is not a string")
        continue
    ...
```

### WR-03: Non-`dict` definition value crashes with a raw `AttributeError` instead of a clean `ExtensionError`

**File:** `typsphinx/template_registry.py:266-268` (and the mirrored
build-loop at `309-317`)
**Issue:** `definition = declared[key] or {}` only normalizes a *falsy*
definition (`None`, `""`, `0`) to `{}`; a truthy but non-`dict` definition
(e.g. a bare string, accidentally typed without the surrounding braces)
reaches `definition.get("template")` directly and crashes.

Verified directly:
```
>>> config.typst_document_templates = {"report": "not-a-dict"}
>>> resolve_template_registry(config, "/tmp")
AttributeError: 'str' object has no attribute 'get'
```
Same class of gap as WR-02 — a plausible authoring mistake
(`{"report": "template.typ"}` instead of `{"report": {"template":
"template.typ"}}`) produces an unhandled crash rather than this module's
own established clean-error contract.

**Fix:**
```python
definition = declared[key]
if not isinstance(definition, dict) and definition:
    failures.append(f"registry key {key!r}'s definition must be a dict, got {definition!r}")
    continue
definition = definition or {}
```

---

_Reviewed: 2026-08-15T09:19:15Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
