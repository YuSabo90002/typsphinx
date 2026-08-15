---
phase: 53-template-registry-foundation
reviewed: 2026-08-15T00:00:00Z
depth: standard
files_reviewed: 24
files_reviewed_list:
  - tests/fixtures/conf14_prewrite_bad_first_gate/aaa_bad.rst
  - tests/fixtures/conf14_prewrite_bad_first_gate/conf.py
  - tests/fixtures/conf14_prewrite_bad_first_gate/index.rst
  - tests/fixtures/conf14_prewrite_bad_first_gate/zzz_good.rst
  - tests/fixtures/conf14_prewrite_bad_last_gate/alpha.rst
  - tests/fixtures/conf14_prewrite_bad_last_gate/beta.rst
  - tests/fixtures/conf14_prewrite_bad_last_gate/conf.py
  - tests/fixtures/conf14_prewrite_bad_last_gate/index.rst
  - tests/fixtures/conf14_prewrite_control_gate/conf.py
  - tests/fixtures/conf14_prewrite_control_gate/five.rst
  - tests/fixtures/conf14_prewrite_control_gate/four.rst
  - tests/fixtures/conf14_prewrite_control_gate/index.rst
  - tests/fixtures/registry_container_shape_gate/conf.py
  - tests/fixtures/registry_container_shape_gate/index.rst
  - tests/test_registry_container_shape_gate.py
  - tests/test_registry_prewrite_validation_gate.py
  - tests/test_state_guard_shapes_gate.py
  - tests/test_template_engine.py
  - tests/test_template_registry.py
  - typsphinx/__init__.py
  - typsphinx/builder.py
  - typsphinx/template_engine.py
  - typsphinx/template_registry.py
  - typsphinx/writer.py
findings:
  critical: 0
  warning: 0
  info: 2
  total: 2
status: clean
---

# Phase 53: Code Review Report (Re-review — second gap-closure round)

**Reviewed:** 2026-08-15
**Depth:** standard
**Files Reviewed:** 24
**Status:** clean

## Summary

This is a targeted re-review of `typsphinx/template_registry.py` (and its callers/tests) after
plan 53-08 closed the two prior WARNING findings (WR-01: truthy non-`dict`
`typst_document_templates` container crashing with a raw `AttributeError`; WR-02: a truthy
non-consumable `template` field crashing with a raw `TypeError` from `os.path.join`). I traced
both fixes end to end against `resolve_template_registry()`'s actual source, the accompanying
unit tests (`tests/test_template_registry.py`, `tests/test_registry_container_shape_gate.py`)
and the real-`sphinx-build` subprocess gates (`tests/test_registry_prewrite_validation_gate.py`,
`tests/test_registry_container_shape_gate.py`), and re-derived the edge cases by hand (falsy vs.
truthy container values, `bytes`/`list`/`bool` template values, `os.PathLike` acceptance, the
CONF-15/type-guard/CONF-17/D-08 interaction inside the same accumulate loop, and the
declaration-order determinism of the accumulated message).

**Both WR-01 and WR-02 are correctly and completely fixed — no residual hole found.**

- **WR-01**: `resolve_template_registry()` now does `declared = getattr(config,
  "typst_document_templates", None) or {}` followed immediately by `if not isinstance(declared,
  dict): raise ExtensionError(...)`, placed *before* `declared.keys()` is ever touched. Because the
  preceding `or {}` has already normalized every falsy value, the `isinstance` check provably fires
  only for a truthy non-`dict` (verified this is exactly the crash surface `declared.keys()` would
  otherwise hit). Confirmed against both the unit test (`test_truthy_non_dict_container_unit_raises_extension_error`)
  and the subprocess gate, which explicitly asserts `"AttributeError" not in combined_output`.
- **WR-02**: a truthy `template` field is now type-checked against `(str, os.PathLike)` before
  `os.path.join(srcdir, template)` is ever called, joining the same accumulate-then-raise-once
  `failures` list as every other definition-level check (not a `continue`, so CONF-15's
  both-set check for the *same* key still fires in the same raise when applicable — confirmed by
  `test_bad_typed_template_and_package_both_reported_in_one_raise`). Falsy `template` values
  (`None`/`""`/`0`/`[]`) are untouched, and the accepted-type set (`str` and `os.PathLike`, not
  `str` alone) is deliberately wider than the WR-02 finding's own suggested fix, correctly measured
  against what `TemplateEngine.resolve_template()`'s `_try_load_file()`/`Path(...)` chain already
  accepts today (verified via `test_pathlike_template_field_still_resolves`, which proves the guard
  does not withdraw a working shape). `bytes` is correctly rejected (`test_bytes_template_field_raises_extension_error_not_typeerror`).

I additionally traced the full validation pipeline order in `TypstBuilder.write()` (collision
validation → `resolve_template_registry()` → `_validate_registry_key_references()` →
`prepare_writing()`) and confirmed the "zero `.typ` files survive any of these three failure
classes" guarantee holds for the container-shape guard exactly as it already held for CONF-14
(both are validated before `prepare_writing()`'s `_write_template_file()` call, which is the first
thing that touches disk).

I also independently confirmed the Phase 53 scope boundary is intact: `render_wrapper()` reads a
per-key `TemplateRegistryEntry.template`/`.package`/`.template_function` and builds a
`TemplateEngine` from it, but the wrapper's own `#import` statement (`template_file`, computed in
`render()`) still always points at the single shared `_template.typ` written by
`_write_template_file()` from the *global* `typst_template`/`typst_package` config — a per-key
custom `template`/`template_function` is validated but not yet actually wired into wrapper output.
This is explicitly documented as intentional and deferred: ROADMAP Phase 53's own goal states "this
phase changes no output" and Phase 54 ("One Bundle Rule — `_template/<key>/`, Per-Document
Selection, Four Deletions") is the phase that performs that wiring. Not reported as a finding.

Only two Info-level items remain, both non-functional. No Critical or Warning findings.

## Info

### IN-01: `package` field is not type-validated (owner-declined, unchanged from prior review)

**File:** `typsphinx/template_registry.py:369, 451-456`
**Issue:** `TemplateRegistryEntry.package` is read via `definition.get("package")` with no
type check, unlike `template`, which now (post-WR-02) rejects a non-`str`/`os.PathLike` value
before it can reach `os.path.join`. A truthy, wrongly-typed `package` (e.g. a `list`) still flows
through `resolve_package_for_engine()` into `TemplateEngine.typst_package` and eventually into
`generate_package_import()`'s f-string (`f'#import "{self.typst_package}": ...'`), producing a
malformed Typst `#import` statement (e.g. `#import "['a', 'b']": ...`) rather than a clean,
actionable `ExtensionError` at config-validation time. This is the identical gap the prior
`53-REVIEW.md` reported as IN-01.
**Status:** Per this round's phase context, this was reviewed by the project owner and explicitly
declined as out of scope for Phase 53. Recorded here only because it remains observably true, not
as a request to fix it in this phase.
**Fix (if ever revisited):** Mirror the `template` guard — `if package and not isinstance(package,
str): failures.append(...)` — inside the same accumulate loop, immediately after the existing
`template`-type guard.

### IN-02: misleading "elif" description in the WR-02 fix's own comment block

**File:** `typsphinx/template_registry.py:380-407`
**Issue:** The comment block introducing the `template`-type guard states: "1. This branch is an
`elif` of `if template and package:` above, NOT a `continue`". The actual code has these as two
independent, sibling `if` statements at the same indentation level inside the `for key in
sorted(...)` loop —

```python
if template and package:                                  # line 374 (CONF-15)
    failures.append(...)

if template and not isinstance(template, (str, os.PathLike)):  # line 408 (type guard)
    failures.append(...)
elif template:
    ...
```

— not `if template and package: ... elif template and not isinstance(...): ...`. The described
*behavior* (CONF-15's both-set check still fires for the same key even when `template` is
bad-typed, so both failures land in one accumulated raise) is correct and is exactly what
`test_bad_typed_template_and_package_both_reported_in_one_raise` proves. Only the comment's
characterization of *how* that is achieved is inaccurate — describing two independent `if`
statements as one being "an `elif`" of the other. Purely a documentation-precision nit; no
behavioral impact.
**Fix:** Reword point 1 to something like: "This is a separate, sibling `if` (not chained via
`elif`, and not a `continue`) to the CONF-15 check above, so CONF-15's both-set check still
independently evaluates for the same definition regardless of this branch's outcome."

---

_Reviewed: 2026-08-15_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
