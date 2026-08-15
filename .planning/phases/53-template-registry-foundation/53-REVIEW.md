---
phase: 53-template-registry-foundation
reviewed: 2026-08-15T11:11:04Z
depth: standard
files_reviewed: 20
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
  warning: 2
  info: 1
  total: 3
status: issues_found
---

# Phase 53: Code Review Report

**Reviewed:** 2026-08-15T11:11:04Z
**Depth:** standard
**Files Reviewed:** 20
**Status:** issues_found

## Summary

Re-review after gap closure (plans 53-06, 53-07). The prior report's CR-02
(Windows cross-drive `ValueError` crashing `_violates_conf17()`) and WR-02/
WR-03 (non-`str` registry key / truthy non-`dict` definition crashing with
raw `AttributeError`/`TypeError`) were verified fixed by direct code
inspection and by re-running their pinning tests
(`tests/test_template_registry.py`, `tests/test_registry_prewrite_validation_gate.py`,
168 tests, all green). `_validate_registry_key_references()` correctly
closes CONF-14's order-dependent partial-write gap: both `conf14_prewrite_bad_first_gate`
and `conf14_prewrite_bad_last_gate` leave zero `.typ` files on disk with a
byte-identical error message, matching `53-06-RED-EVIDENCE.md`'s claim, and
`conf14_prewrite_control_gate` proves the pass is a no-op for an ordinary
config.

While tracing the accumulate-then-raise-once validation pass in
`resolve_template_registry()` for cases NOT covered by the 53-07 guards, I
found and reproduced two further raw-exception crash paths in the same
function that are one level "up" from the ones just fixed: a non-`dict`
top-level `typst_document_templates` value, and a non-`str` `template`
field inside an otherwise well-formed definition. Both are live today
(reproduced against a real `sphinx-build` subprocess below) and both are
the identical defect class WR-02/WR-03 just closed for narrower inputs —
Sphinx only *warns* (not enforces) `typst_document_templates`'s
`[dict]` config-value type, so a user typo reaches this module's own code
with no earlier gate.

## Warnings

### WR-01: Non-`dict` `typst_document_templates` crashes with raw `AttributeError` instead of `ExtensionError`

**File:** `typsphinx/template_registry.py:261-262`
**Issue:** `resolve_template_registry()` does `declared = getattr(config, "typst_document_templates", None) or {}` then immediately calls `declared.keys()`. `app.add_config_value("typst_document_templates", {}, "html", [dict])` (`typsphinx/__init__.py:63`) only makes Sphinx *warn* on a type mismatch — it does not coerce or reject the value — so a truthy non-`dict` config value (e.g. a `list`, which is a plausible copy-paste-from-`typst_documents` typo) reaches this line unchanged and crashes with a raw `AttributeError: 'list' object has no attribute 'keys'`, producing an internal Sphinx traceback dump instead of this module's own `typst_document_templates: N invalid definition(s): ...` contract. Reproduced live:
```
$ python -m sphinx -b typst src build   # conf.py: typst_document_templates = ["a", "b"]
...
WARNING: 設定値 `typst_document_templates' に `list' 型が指定されていますが、 `dict' 型を指定してください。
...
AttributeError: 'list' object has no attribute 'keys'
```
An empty list (`[]`) does NOT trigger this — `[] or {}` is falsy so it silently resolves to `{}` — only a *truthy* non-`dict` value does. This is exactly the WR-02/WR-03 defect class ("raw internal exception instead of this module's own `ExtensionError`"), one level higher: the container itself, not a key or a definition inside it.
**Fix:**
```python
declared = getattr(config, "typst_document_templates", None) or {}
if not isinstance(declared, dict):
    raise ExtensionError(
        f"typst_document_templates must be a dict, got {declared!r}"
    )
all_keys = {key for key in declared.keys() if isinstance(key, str)}
```

### WR-02: Non-`str` `template` field crashes with raw `TypeError` instead of `ExtensionError`

**File:** `typsphinx/template_registry.py:334-340`
**Issue:** Once a definition passes the WR-03-fixed dict-shape guard, `template = definition.get("template")` is used unchecked: `if template:` only tests truthiness, then `template_abs_path = os.path.join(srcdir, template)` is called directly. A non-`str` truthy `template` value (e.g. a `list`, again a plausible typo such as writing `"template": ["a", "b"]` or forgetting to unwrap a one-element list) crashes `os.path.join()` with a raw `TypeError: join() argument must be str, bytes, or os.PathLike object, not 'list'` — an unhandled internal exception, not this module's accumulated `ExtensionError`. Reproduced live against `conf.py: typst_document_templates = {"key": {"template": ["a", "b"]}}`:
```
File "<frozen genericpath>", line 188, in _check_arg_types
TypeError: join() argument must be str, bytes, or os.PathLike object, not 'list'
```
This is the same defect class as WR-01 above and the just-fixed WR-02/WR-03, now found one field deeper: the `template` value itself is never type-checked before being handed to `os.path.join()`.
**Fix:**
```python
if template is not None and not isinstance(template, str):
    failures.append(
        f"registry key {key!r}'s template {template!r} must be a "
        "string, not a path list or other type"
    )
elif template:
    template_abs_path = os.path.join(srcdir, template)
    ...  # existing CONF-17 / D-08 checks unchanged
```

## Info

### IN-01: `package` field is never type-validated, silently emits malformed Typst on a non-`str` value

**File:** `typsphinx/template_registry.py:323`, `typsphinx/writer.py:530-554` (`TemplateEngine.generate_package_import()`)
**Issue:** Unlike `template`, a non-`str` `package` value (e.g. `{"package": 123}`) does not crash — it silently flows through to `generate_package_import()`, which f-string-interpolates it into `#import "{self.typst_package}"`, producing `#import "123"` in the emitted `.typ` file: syntactically valid but semantically nonsensical Typst that only surfaces as a confusing compile-time error far from the misconfiguration's source. This mirrors the pre-existing (out-of-scope) behavior of the global `typst_package` config value, so it is not a phase-53 regression, but since `resolve_template_registry()` already validates several other shapes of this same definition dict (CONF-15/CONF-17/D-08), a `str` type-check here would be a small, consistent addition rather than a new validation axis.
**Fix:** Optionally extend the same truthy-non-`str` guard pattern proposed for WR-02 to `package`, reporting it as an accumulated failure rather than leaving it to surface as an opaque Typst compile error.

---

_Reviewed: 2026-08-15T11:11:04Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
