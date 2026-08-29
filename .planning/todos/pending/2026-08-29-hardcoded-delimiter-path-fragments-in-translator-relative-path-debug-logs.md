---
created: 2026-08-29
title: "typsphinx/translator.py's two relative-path debug logs quote `up_path`/`down_path` with a hardcoded `'...'` delimiter, the same MSG-02-shaped defect Phase 60 fixed in builder.py/writer.py/template_registry.py -- but this is a fourth module, out of Phase 60's requirement scope"
area: translator
resolves_phase: null
source: Phase 60 plan 05's SC#2 repo-wide discovery grep, run REPO-WIDE per the phase's own
  execution-time-grep-is-discovery-authority rule. Found by the fourth grep pattern
  (`grep -rnoE "'\{[a-zA-Z_.]+\}'" typsphinx/`), the same pattern that originally found the
  three 57-11 message builders' hardcoded-delimiter defect in `builder.py`. MSG-02/03/04/05
  name only `builder.py`, `writer.py` and `template_registry.py`; `translator.py` is
  explicitly out of scope for Phase 60 (60-CONTEXT.md's Deferred Ideas section covers only
  translator.py's `!r`-conversion sites -- `master_docname!r`, `path[0]!r`, `path[-1]!r` at
  translator.py:417/420, all identifier-valued docnames -- not this hardcoded-delimiter
  pattern at a different pair of lines).
severity: minor
files:

  - typsphinx/translator.py:5047  # _compute_relative_include_path()'s cross-directory debug log
  - typsphinx/translator.py:5152  # _compute_relative_image_path()'s cross-directory debug log

audit_acknowledged:
  milestone: v0.9.1
  at: 2026-08-29
---

## Problem

Two `logger.debug()` calls in `typsphinx/translator.py` -- one in
`_compute_relative_include_path()` (the toctree `#include()` path resolver) and one in
`_compute_relative_image_path()` (the `image()` path resolver) -- interpolate `up_path` and
`down_path` with a hardcoded `'...'` delimiter rather than through a delimiter-aware helper:

```python
logger.debug(
    f"Cross-directory path calculation: up_count={up_count}, "
    f"up_path='{up_path}', down_path='{down_path}', "
    f"result: {relative_path}"
)
```

(identical shape at both `:5047` and `:5152`).

Under D-05's role rule ("does the reader read this value as a location on a filesystem, or as
a name in a namespace?"), both `up_path` and `down_path` are **path-valued**: `up_path` is a
run of `"../"` segments and `down_path` is `"/".join(down_parts)`, where `down_parts` is a
slice of `target_path.parts` (or `image_parts` in the image-path sibling) -- i.e. these are
computed relative-path fragments between two docname-tree locations, built for constructing a
Typst `#include()`/`image()` path. This is the exact defect shape `_conf17_violation_message()`,
`_templates_path_collision_message()` and `_bundle_destination_collision_message()` carried
before Phase 60's 60-02 plan routed them through `typsphinx/pathfmt.py`'s `quote_path()`: a
hardcoded apostrophe delimiter closes early if the interpolated value itself contains a literal
apostrophe.

**Concretely:** `down_parts` is derived from Sphinx docname path components (`target_path.parts`
/ `image_parts`), which in turn come from source file names on disk. A source file or directory
name containing a literal apostrophe (e.g. a docname segment like `guide's-notes`) would
produce a `down_path` value that closes the hardcoded `'...'` delimiter early in this debug
log, visually truncating the printed value -- the same "message misreads its own value"
symptom this phase's requirements fix everywhere in scope.

**Why this is NOT fixed in Phase 60:** MSG-02/03/04/05 name exactly three modules --
`typsphinx/builder.py`, `typsphinx/writer.py`, `typsphinx/template_registry.py`. Phase 60's
own CONTEXT.md (D-05 through D-08, and the Deferred Ideas section) scopes the rollout to those
three; widening the grep's findings into a fourth module mid-phase is explicitly forbidden
(`60-CONTEXT.md`'s own prohibition: "A repo-wide grep hit in a fourth module ... must be FILED
as a new requirement, never fixed here -- widening the grep's scope mid-phase is exactly what
CONTEXT.md's Deferred Ideas forbids"). This todo is that filing.

**Severity note:** both sites are `logger.debug()` calls, not `logger.warning()`/`ExtensionError`
-- visible only with verbose/debug-level Sphinx logging, not in a default build's output. This
keeps the defect at `minor` rather than the `moderate`/severe classification MSG-03/04/05's
warning- and error-level sites carried.

## Suggested fix

Route both interpolations through `typsphinx/pathfmt.py`'s `quote_path()` (the leaf module
Phase 60 created), exactly as `writer.py`'s wrapper-render debug log (MSG-04) was fixed:

```python
logger.debug(
    f"Cross-directory path calculation: up_count={up_count}, "
    f"up_path={quote_path(up_path)}, down_path={quote_path(down_path)}, "
    f"result: {relative_path}"
)
```

This requires `typsphinx/translator.py` to import `typsphinx.pathfmt.quote_path` -- a
module-scope import that is safe (translator.py is not one of the three modules `pathfmt.py`
was built to avoid an import cycle with; `pathfmt.py` itself has zero `typsphinx`-internal
imports either way). A new/extended `caplog`-based regression test following
`tests/test_writer_path_quoting_gate.py`'s established `TestWrapperDebugLogPathQuoting`
pattern would gate both sites, driving a docname containing a literal apostrophe through both
`_compute_relative_include_path()` and `_compute_relative_image_path()` and asserting the
apostrophe survives inside the rendered quote rather than closing it early.
