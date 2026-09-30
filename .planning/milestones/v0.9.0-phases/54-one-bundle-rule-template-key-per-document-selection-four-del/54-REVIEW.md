---
phase: 54-one-bundle-rule-template-key-per-document-selection-four-del
reviewed: 2026-08-16T00:00:00Z
depth: standard
files_reviewed: 18
files_reviewed_list:
  - typsphinx/builder.py
  - typsphinx/writer.py
  - typsphinx/template_engine.py
  - typsphinx/template_registry.py
  - typsphinx/__init__.py
  - typsphinx/removed_config.py
  - typsphinx/templates/README.md
  - pyproject.toml
  - .github/workflows/ci.yml
  - .readthedocs.yaml
  - CHANGELOG.md
  - CLAUDE.md
  - docs/source/user_guide/configuration.rst
  - docs/source/user_guide/templates.rst
  - tests/test_removed_config_deprecation_gate.py
  - tests/test_template_prefix_reservation_gate.py
  - tests/test_two_key_selection_gate.py
  - tests/test_user_template_relative_asset_gate.py
  - tests/test_bundle_copy_exclusion_manifest_gate.py
findings:
  critical: 1
  warning: 4
  info: 1
  total: 6
status: issues_found
---

# Phase 54: Code Review Report

**Reviewed:** 2026-08-16T00:00:00Z
**Depth:** standard
**Files Reviewed:** 18
**Status:** issues_found

## Summary

This review covers the deliberately-narrowed high-signal subset of Phase 54's 73-file diff
(production code, build/packaging config, user-facing docs, and the five new gate test modules;
the ~54 mechanically-retargeted fixture/test files are excluded from this review per the
workflow's own scoping note). The core mechanism — one bundle per used registry key, copied
wholesale to `<outdir>/_template/<key>/`, imported by a root-absolute path — is implemented
consistently across `builder.py`, `writer.py`, and `template_registry.py`, and the five new gate
tests (`test_two_key_selection_gate.py`, `test_user_template_relative_asset_gate.py`,
`test_bundle_copy_exclusion_manifest_gate.py`, `test_template_prefix_reservation_gate.py`,
`test_removed_config_deprecation_gate.py`) exercise the intended real-compile paths well.

Per the scope note, the following were confirmed as *intentional* and are **not** reported below:
absence of a symlink-refusal guard in `_copy_bundle_directory()` (D-03 retraction), absence of a
runtime warning for the `<srcdir>/base.typ` → `<srcdir>/_typst/base.typ` shadow relocation (D-15
retraction), and the stale `output_layout.rst`/`builders.rst`/`examples/advanced.rst` pages
(deferred to Phase 56).

The one finding classified Critical is a genuine, reachable violation of this codebase's own
"no partial write on a build-stopping error" invariant — an invariant enforced (and gate-tested)
everywhere else a build-stopping `ExtensionError` can be raised, but not here. The four Warnings
cover a documentation footgun that directly contradicts this repository's own dogfooded
`conf.py` convention, an under-documented breaking change in the Unreleased changelog entry, a
narrow cross-registry-key template-resolution coupling, and a source-level nit.

## Critical Issues

### CR-01: A CONF-17 violation on the built-in `"typst"` key is discovered only at `finish()`, after every content and wrapper `.typ` file has already been written

**File:** `typsphinx/template_registry.py:449-468`, `typsphinx/builder.py:1491-1639`, `typsphinx/builder.py:905-1019`, `typsphinx/builder.py:1685-1702`

**Issue:** `resolve_template_registry()` validates CONF-17 (a declared template's parent directory
must not be `srcdir` itself or an ancestor of it) only for keys pulled from the *declared*
`typst_document_templates` dict (the loop at `template_registry.py:321-434`). The synthesized
built-in `"typst"` key is assembled afterward, directly from `getattr(config, "typst_template",
None)`, with **no** CONF-17 check at all (`template_registry.py:463-468`) — confirmed
deliberately by `tests/test_template_registry.py::test_builtin_typst_key_nonexistent_global_template_does_not_raise`,
whose own docstring states "the built-in `typst` key's not-found path is UNCHECKED by this
module."

That check is instead deferred to `builder.py:_copy_used_template_bundles()`'s "A-01 guard"
(`builder.py:1628-1639`), which is called **only** from `finish()`
(`builder.py:1701-1702`). Sphinx's build lifecycle always runs `write()` to completion — writing
every docname's content file *and* every `typst_documents` entry's wrapper file
(`builder.py:980-1019`) — **before** `finish()` ever runs. So a project that sets a global
`typst_template` to a *bare filename with no directory component* (e.g.
`typst_template = "mytemplate.typ"` sitting directly at the source root — a very natural first
attempt before a user learns the "must live in its own subdirectory" rule) will:

1. Write every docname's content `.typ` file to `outdir`.
2. Write every `typst_documents` entry's wrapper `.typ` file to `outdir`.
3. Only then, inside `finish()`, discover the CONF-17 violation and raise `ExtensionError`.

This contradicts the exact invariant this codebase otherwise builds and gate-tests deliberately
elsewhere: `_validate_output_path_collisions()` and `_validate_registry_key_references()` are both
explicitly run "at the very top of `write()`… so a collision leaves ZERO `.typ` files on disk"
(`builder.py:935-941`, `954-961`), and `tests/test_template_prefix_reservation_gate.py` gates this
exact "no partial write" property for the sibling OUT-07 reservation check
(`test_no_typ_file_written_after_refusal`). No equivalent test exists for the A-01/CONF-17 path on
the built-in key — a build that "fails" here leaves a full but incomplete-and-broken `.typ` tree
on disk, which is misleading for any CI step that only checks build exit code before inspecting
output, and wastes the entire write pass before failing on a config mistake that could have been
caught immediately.

A second, related gap: the same lazy-discovery pattern applies to the destination
case-collision check in `_copy_used_template_bundles()` (`builder.py:1535-1544`,
`1643-1655`) — e.g. a declared key literally named `"Typst"` differs from the reserved `"typst"`
key only by case (deliberately allowed per `template_registry.py`'s own `RESERVED_REGISTRY_KEY`
docstring, D-04) and is *not* caught by CONF-18's case-collision check (which only compares
declared keys against each other, never against the synthesized key). If both are used in one
build, the collision is likewise discovered only at `finish()`, after every content/wrapper file
has already been written.

**Fix:** Extend `resolve_template_registry()` (or a call site immediately after it, before
`prepare_writing()` in `write()`) to run CONF-17 (and the reserved-key case-collision check)
against the *resolved* synthesized `"typst"` entry too, symmetrically with every declared key —
or, at minimum, hoist the A-01 guard itself into a pre-write validation pass (mirroring
`_validate_output_path_collisions()`/`_validate_registry_key_references()`'s placement at the top
of `write()`) so the check runs, and can raise, before any `.typ` file reaches disk:

```python
# in write(), immediately after resolve_template_registry() /
# _validate_registry_key_references(), and before prepare_writing():
self._validate_used_template_paths()  # new: A-01/CONF-17 + reserved-key
                                       # case-collision, run against every
                                       # DECLARED key up front (the
                                       # synthesized "typst" key's actual
                                       # USE is only known after the write
                                       # loop -- so at minimum this needs a
                                       # regression test asserting zero
                                       # .typ files survive an A-01 failure
                                       # on the built-in key, even if the
                                       # check itself must stay at
                                       # finish()-time).
```

If moving the check earlier is impractical (the *used* keys are only known after the write loop
completes), the check should at minimum be paired with a regression test proving the "zero `.typ`
files on failure" property does **not** hold here, so this is a documented, tested exception
rather than a silent gap — today it is neither.

## Warnings

### WR-01: Published template docs recommend `_templates/` — the exact directory this phase's own code goes out of its way to avoid, and whose entire contents the new bundle-copy will now publish

**File:** `docs/source/user_guide/templates.rst:91-92, 98-104, 123, 168, 321, 351`,
`docs/source/user_guide/configuration.rst:117`

**Issue:** Every worked example of `typst_template` in the published docs uses
`typst_template = "_templates/custom.typ"` (also `_templates/minimal.typ`,
`_templates/academic.typ`). `_templates/` is Sphinx's own default `templates_path` value for
Jinja HTML theme overrides — this repository's own `docs/source/conf.py` sets
`templates_path = ["_templates"]` (line 45) for exactly that purpose, and deliberately points its
own `typst_template` at `_typst/custom_template.typ` instead (line 96) to avoid the collision.
`typsphinx/template_engine.py`'s `TEMPLATE_SEARCH_SUBDIR` docstring (lines 20-38) explains this
exact hazard at length for the *auto-discovered* shadow route: "Deliberately NOT named
`_templates/` — that is Sphinx's own `templates_path` default and would collide with its
meaning."

Phase 54 makes this collision materially worse than before: the resolved template's *entire
parent directory* is now copied wholesale to `<outdir>/_template/<key>/`
(`builder.py:_copy_used_template_bundles`/`_copy_bundle_directory`). A user who follows the
published docs' own example and puts a real project's `_templates/` directory (containing Jinja
HTML overrides, possibly other unrelated project files) alongside `custom.typ` will now have that
entire directory's contents republished into the public `.typ`/PDF output tree — precisely the
"republish a user's entire directory as build output" hazard `TEMPLATE_SEARCH_SUBDIR`'s own
docstring was written to prevent for the shadow-search case.

**Fix:** Update every `typst_template = "_templates/..."` example in `templates.rst` and
`configuration.rst` to a name that does not collide with Sphinx's own `templates_path` default —
e.g. `_typst/custom.typ`, matching this repository's own dogfooded `docs/source/conf.py`
convention and the rationale already written for `TEMPLATE_SEARCH_SUBDIR`.

### WR-02: CHANGELOG's Unreleased section omits Phase 54's more consequential breaking change — the `typst_template_assets` removal and the asset-list-to-wholesale-copy behavior change

**File:** `CHANGELOG.md:8-20`

**Issue:** The Unreleased section's only `### Changed` entry documents the `<srcdir>/base.typ` →
`<srcdir>/_typst/base.typ` shadow relocation. It does not mention that `typst_template_assets` was
removed entirely (the entire subject of the new `typsphinx/removed_config.py` module), nor that
the underlying asset-copy *mechanism* changed from "copy an explicit, curated list of files the
user selected" to "copy the entire bundle directory wholesale, unconditionally" — a materially
different, and potentially more consequential, behavior change for any project that was relying on
`typst_template_assets` to select a curated subset of files rather than publish everything sitting
next to the template. `removed_config.py`'s own warning text for this value states the
consequence plainly ("MORE files now reach the output than the explicit list used to select"),
but that observable, security-adjacent behavior change (files a user did not explicitly opt in to
disclose can now reach the output tree) has no corresponding CHANGELOG bullet of its own.

**Fix:** Add a second `### Changed` (or `### Removed`) bullet to the Unreleased section
specifically for the `typst_template_assets` removal and the wholesale-copy behavior change,
independent of the shadow-relocation bullet — mirroring the level of detail the v0.8.0 entries
already give each of their own breaking changes.

### WR-03: A declared registry key with neither `template` nor `package` silently shares the reserved `"typst"` key's shadow-search file and filename

**File:** `typsphinx/template_registry.py:367-372`, `typsphinx/template_engine.py:39, 282-284`,
`typsphinx/writer.py:396`, `typsphinx/builder.py:1614`

**Issue:** `resolve_template_registry()` explicitly accepts a declared definition that sets
*neither* `template` nor `package` ("flagged assumption 3", `template_registry.py:371-372`
comment). For such a key, `render_wrapper()` (`writer.py:396`) and
`_copy_used_template_bundles()` (`builder.py:1614`) both build the `TemplateEngine` with
`search_paths=[<srcdir>/_typst]` and — because `template_name` is never threaded per-key through
either call site — `TemplateEngine.__init__`'s default `self.template_name = template_name or
"base.typ"` (`template_engine.py:283`) resolves to the literal filename `"base.typ"` regardless of
which registry key is being resolved. This is the *same* directory and *same* filename the
reserved `"typst"` key's own shadow-override route uses (`TEMPLATE_SEARCH_SUBDIR`,
`template_engine.py:20-38`).

Concretely: a project using the built-in `"typst"` key's shadow override
(`<srcdir>/_typst/base.typ`) that also declares an unrelated key with neither `template` nor
`package` set (e.g. a placeholder entry, or a config mistake) will have that unrelated key
silently resolve to the SAME shadow file as the reserved key, rather than falling straight through
to the packaged default template as its empty definition would suggest.

**Fix:** Either reject a definition with neither `template` nor `package` at
`resolve_template_registry()` time (removing "flagged assumption 3" as an accepted shape), or
scope `TEMPLATE_SEARCH_SUBDIR`'s search path (and/or the searched filename) per registry key so an
unrelated key's Priority 2 search cannot resolve to the reserved key's own shadow file.

### WR-04: Local re-import of `TEMPLATE_OUTPUT_DIR` duplicates the existing module-level import

**File:** `typsphinx/builder.py:28, 1571`

**Issue:** `TEMPLATE_OUTPUT_DIR` is already imported at module scope
(`from typsphinx.writer import TEMPLATE_OUTPUT_DIR, TypstWriter`, line 28) and used directly by
`_reserves_template_prefix()`. `_copy_used_template_bundles()` re-imports the same name locally
(`from typsphinx.writer import TEMPLATE_OUTPUT_DIR`, line 1571) for no functional reason — no
circular-import hazard requires it here (unlike the adjacent local import of
`typsphinx.template_registry._violates_conf17`, which plausibly could relate to import ordering).
This is a harmless but confusing duplicate binding of the same name in the same file.

**Fix:** Drop the local import at line 1571 and rely on the existing module-level binding.

## Info

### IN-01: `_copy_used_template_bundles()` imports a private (underscore-prefixed) helper from another module

**File:** `typsphinx/builder.py:1570`

**Issue:** `from typsphinx.template_registry import RESERVED_REGISTRY_KEY, _violates_conf17`
reaches into `template_registry.py`'s private (`_`-prefixed) namespace from outside that module.
This is consistent with one other existing cross-module private import in this codebase
(`template_registry.py`'s own local import of `typsphinx.builder.TypstBuilder` inside
`_has_case_collision()`), so it is not a new pattern, but a second instance widens the "private
helper used as a public API" surface between these two modules.

**Fix:** Consider renaming `_violates_conf17` to a public name (`violates_conf17`) now that it has
a legitimate second caller outside its defining module, or re-exporting it explicitly via
`template_registry.py`'s own public surface.

---

_Reviewed: 2026-08-16T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
