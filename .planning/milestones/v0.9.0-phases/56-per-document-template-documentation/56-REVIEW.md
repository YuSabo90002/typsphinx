---
phase: 56-per-document-template-documentation
reviewed: 2026-08-16T12:41:46Z
depth: standard
files_reviewed: 17
files_reviewed_list:
  - CLAUDE.md
  - docs/source/examples/advanced.rst
  - docs/source/user_guide/builders.rst
  - docs/source/user_guide/configuration.rst
  - docs/source/user_guide/output_layout.rst
  - docs/source/user_guide/templates.rst
  - examples/advanced/README.md
  - examples/basic/README.md
  - examples/charged-ieee/approach1/conf.py
  - examples/charged-ieee/approach2/conf.py
  - tests/fixtures/user_template_relative_asset_gate/_typst/branded.typ
  - tests/fixtures/user_template_relative_asset_gate/_typst/refs.bib
  - tests/test_bundle_layout_sweep_gate.py
  - tests/test_hand_compile_root_gate.py
  - tests/test_output_layout_docs_gate.py
  - tests/test_registry_documentation_gate.py
  - tests/test_removed_config_deprecation_gate.py
  - tests/test_user_template_relative_asset_gate.py
findings:
  critical: 0
  warning: 2
  info: 0
  total: 2
status: issues_found
---

# Phase 56: Code Review Report

**Reviewed:** 2026-08-16T12:41:46Z
**Depth:** standard
**Files Reviewed:** 17
**Status:** issues_found

## Summary

This is a documentation phase (zero `typsphinx/` production-code changes; confirmed `git diff f07e8cb8..HEAD -- typsphinx/` is empty). The review therefore focused on (1) whether the six new/updated pytest gate modules can actually fail — i.e. are not vacuously-passing rubber stamps like the Phase-54-era `_template.typ` file-count gate this phase was created to correct — and (2) whether the published prose's concrete, checkable claims (file counts, destination paths, error-message fragments, the `--root` rule, the `template`-xor-`package` rule, the reserved `"typst"` key, the registry error catalogue) actually match the shipped code.

**Gate load-bearing checks performed (not just read):**
- `tests/test_bundle_layout_sweep_gate.py`: temporarily reintroduced a `_template.typ` claim into `templates.rst` — the `test_no_reserved_template_basename_claim_survives` test failed as expected, then reverted (`git status --porcelain` clean afterward).
- `tests/test_output_layout_docs_gate.py`: temporarily changed the published "nine root-level" claim to "ten" in `output_layout.rst` — `test_page_states_the_shared_child_composition` failed as expected, then reverted (`git status --porcelain` clean afterward).
- `tests/test_registry_documentation_gate.py` and `tests/test_removed_config_deprecation_gate.py` each already carry synthetic self-tests (`TestCatalogueGateHasTeeth`, teeth tests) that exercise every comparison helper against known-bad inputs directly — read and traced rather than re-executed destructively.
- `tests/test_hand_compile_root_gate.py` and `tests/test_user_template_relative_asset_gate.py`: both compile real Typst documents via `typst-py` (confirmed a hard core dependency in `pyproject.toml`, not an optional extra, so their `skipif(not TYPST_AVAILABLE, ...)` guards cannot silently neuter them in the shipped CI matrix).

**Cross-checks of concrete prose claims against the shipped code**, all confirmed accurate: `_KEY_SHAPE_REJECTION_CASES` (7 cases, same order as the published table); `REMOVED_CONFIG_VALUES` (3 names, versions, and replacement text verbatim); the two-way error-catalogue fragments (`which is not a string -- registered …`, `not a registered typst_document_templates key -- registered …`, etc., grepped directly in `template_registry.py`); `TypstBuilder._collision_key()`'s casefold-with-no-Unicode-normalization behavior; the `#show: project.with(` wrapper/content discriminator string (`template_engine.py:729`); and the charged-ieee `bibliography` parameter's "result of a call, not a bare path string" claim (verified against the actual cached `@preview/charged-ieee:0.1.4` package source, `bibliography: none` doc comment: "The result of a call to the `bibliography` function or `none`").

**Example `conf.py` correctness**: both `examples/charged-ieee/approach1/conf.py` and `approach2/conf.py` were built end-to-end with `sphinx-build -b typstpdf -c . source <tmp>`, producing valid non-empty PDFs (`%PDF` header) via real network fetches of `@preview/charged-ieee:0.1.4` — both approaches compile successfully under the shipped registry, confirming the `typst_documents` 5-tuple naming the reserved `"typst"` key and the `typst_package`+`params`-route / `typst_template`-wrapping-a-package routes both work as documented.

**A full HTML docs build** (`sphinx-build -b html docs/source <tmp>`) produced zero warnings attributable to the reviewed files — all internal `:doc:` cross-references resolve, and the touched sections read consistently with the rest of the page tree. (Three pre-existing, unrelated docstring-formatting warnings surfaced from `typsphinx/translator.py`'s `visit_toctree` docstring — out of scope, not part of this phase's diff.)

No findings rise to BLOCKER/Critical: nothing in the reviewed scope is incorrect in a way that breaks a build, misleads a reader about a currently-supported code path, or reintroduces the Phase-54 vacuous-gate failure mode this phase exists to close. The two WARNING findings below are both pre-existing staleness issues in the example-project README files that happen to sit in this phase's reviewed file set but were not touched by this phase's own diff.

## Warnings

### WR-01: Broken relative link to the configuration reference in examples/advanced/README.md

**File:** `examples/advanced/README.md:270`
**Issue:** `See [Configuration Reference](../../docs/configuration.rst) for complete documentation of all options.` resolves to `docs/configuration.rst` relative to the repository root, which does not exist. The real file is at `docs/source/user_guide/configuration.rst`. This is a plain-Markdown link (GitHub rendering, not Sphinx `:doc:` resolution), so nothing catches it at build time — a reader following this link from GitHub gets a 404. Pre-existing (not touched by this phase's diff), but within this phase's reviewed file set and directly contradicted by the actual repo layout.
**Fix:**
```markdown
See [Configuration Reference](../../docs/source/user_guide/configuration.rst) for complete documentation of all options.
```

### WR-02: Stale Python/Sphinx prerequisite versions in the example READMEs

**File:** `examples/basic/README.md:7-8`, `examples/advanced/README.md:31-33`
**Issue:** Both files' "Prerequisites" sections state `Python 3.9 or higher` and `Sphinx 5.0 or higher`. `pyproject.toml` currently pins `requires-python = ">=3.12"` (line 10) and `sphinx>=9.1,<10` (line 28) — also independently reflected in CLAUDE.md's "Python 3.12+ is required." A reader on Python 3.9-3.11 or Sphinx 5-8 who follows this guidance will hit an immediate `pip install typsphinx` resolution failure, not a working install. (The same stale pair also appears in `docs/source/installation.rst:7-8`, outside this phase's reviewed file set, so the drift is wider than just these two files — noted for context, not itself a finding against this phase's diff.) Pre-existing, not touched by this phase's diff, but within scope and directly contradicted by the shipped dependency constraints — the same class of prose/code drift DOC-14/15/16/17 in this phase corrected elsewhere.
**Fix:** Update both Prerequisites sections (and, separately, `docs/source/installation.rst`) to state `Python 3.12 or higher` and `Sphinx 9.1 or higher`, matching `pyproject.toml`.

---

_Reviewed: 2026-08-16T12:41:46Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
