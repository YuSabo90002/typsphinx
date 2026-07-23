---
phase: 19-block-separation-fixes-cluster-a
plan: 03
subsystem: translator
tags: [typst-codegen, block-separation, render-gate, tdd]
dependency-graph:
  requires:
    - "Plan 01/02 (Cluster A waves 1-2): established the render-gate/TDD idiom this plan follows; FID-05 itself is independent of the shared _emit_forced_break helper those plans introduced (Pitfall 3)"
  provides:
    - "FID-05 fix: terms(separator: linebreak(), ...) so a definition-list term renders on its own line, separated from its definition, in both sub-cases"
  affects:
    - "Phase 19 close: FID-02..FID-06 (Cluster A) now complete; corpus gate confirmed green"
tech-stack:
  added: []
  patterns:
    - "FID-05: a terms()-call-PARAMETER change (separator: linebreak(), added as the FIRST named argument in both the items and empty branches), NOT routed through the shared _emit_forced_break helper -- the bug is a Typst terms() layout default (weak h(0.6em) separator), not a missing statement-boundary."
key-files:
  created:
    - tests/fixtures/deflist_term_in_listitem_render_gate/conf.py
    - tests/fixtures/deflist_term_in_listitem_render_gate/index.rst
    - tests/fixtures/deflist_term_nested_list_render_gate/conf.py
    - tests/fixtures/deflist_term_nested_list_render_gate/index.rst
  modified:
    - typsphinx/translator.py
    - tests/test_deflist_term_concat_render_gate.py
decisions:
  - "Fixture RST prose initially contained a literal '``terms(separator: linebreak(), ...)``' backtick span describing the fix -- this collided with the D-05 structural assert exactly like Plan 02's documented deviation #3 (both fixtures showed a false-GREEN against the deliberately-reverted pre-fix translator, because the assert matched the prose's own literal raw(\"terms\") text, not the real terms(...) call). Reworded both fixtures' prose to describe the fix without the literal token before re-confirming RED/GREEN."
  - "Sub-case (b)'s fixture uses a nested definition_list (not a field_list) as the 'nested list' inside the outer definition -- confirmed via a real -b typst build that this reproduces the exact corpus pattern RESEARCH cited for the mecab case (terms.item(text(\"Options for \") + raw(\"'mecab'\") + text(\":\"), {terms(terms.item(...", i.e. the outer definition's first content is a bare, un-par()-wrapped nested terms(...) call."
metrics:
  duration: "~55m"
  completed: "2026-07-20"
status: complete
---

# Phase 19 Plan 03: Block Separation Fixes — FID-05 Summary

Fixed the definition-list `term`/`definition` separator (FID-05) by setting the emitted `terms(...)` call's own `separator:` parameter to `linebreak()`, unconditionally, in both the populated and empty branches of `depart_definition_list` — closing Cluster A (FID-02..FID-06).

## What Was Built

- **FID-05** (`depart_definition_list`, `typsphinx/translator.py` ~1749-1769): the `terms()` emission now reads `terms(separator: linebreak(), {items_str})` (items branch) and `terms(separator: linebreak())` (empty branch). Typst's built-in `terms()` `separator` parameter defaults to a *weak* `h(0.6em)` horizontal space, not a line break; when a definition's first content is bare inline (nested in a `list_item`, where `visit_paragraph` early-returns per FID-02, or when the definition opens with a nested list whose own first content is also inline) nothing forced a break, so the term flowed onto the same visual line as its definition. This is a `terms()`-call-**parameter** change, deliberately NOT routed through the shared `_emit_forced_break` helper (Pitfall 3) — the bug is a Typst layout default, not a missing statement-boundary.
- **New GATE-01 fixtures**:
  - `tests/fixtures/deflist_term_in_listitem_render_gate/` — mirrors the real corpus's `usage/configuration.rst` `texinfo_elements` case: a bullet `list_item` containing a two-entry definition list (`'paragraphindent'` / `'exampleindent'`), each definition a bare paragraph with no `par()` wrapping (sub-case a).
  - `tests/fixtures/deflist_term_nested_list_render_gate/` — mirrors the real corpus's `'mecab'` confval case: a definition list whose single definition opens with a nested definition list (`dic_enc` / `dic_dir`), so the outer term's definition content is itself a bare, un-`par()`-wrapped `terms(...)` call (sub-case b).
- **Extended `tests/test_deflist_term_concat_render_gate.py`** with two new test classes/methods (`TestDeflistTermInListitemRenderGate`, `TestDeflistTermNestedListRenderGate`), each asserting `"terms(separator: linebreak()" in typ_text` and a real `%PDF`-magic compiled PDF, without disturbing the existing `TestDeflistTermConcatRenderGate` (GATE-02) method.

## RED → GREEN Proof (D-05)

Verified in both directions by temporarily reverting the `depart_definition_list` hunk in-place (via the `Edit` tool, never `git stash`), re-running the extended gate module, and restoring the fix:

- **Pre-fix** (`terms({items_str})` / `terms()`, no `separator:`): both new methods FAILED with `AssertionError: Expected the terms() call to carry separator: linebreak()`, confirming the emitted `.typ`'s real `terms(...)` calls (`terms(terms.item(raw("'paragraphindent'"...` and `terms(terms.item(text("Options for ")...`) carry no separator. The existing GATE-02 method (unrelated to FID-05) still passed, unaffected.
- **Post-fix**: `uv run pytest tests/test_deflist_term_concat_render_gate.py -q` → `3 passed`.

## A discovery not anticipated by RESEARCH/PATTERNS: fixture-prose literal collision (repeat of Plan 02's deviation #3)

Both new fixtures' `index.rst` initially described the fix in prose using a literal double-backtick span, `` ``terms(separator: linebreak(), ...)`` ``. docutils renders this as `raw("terms(separator: linebreak(), ...)")` in the emitted `.typ` body — a false match for the D-05 structural assert. This was caught during the mandatory RED-proof step: reverting the translator fix and re-running the tests unexpectedly stayed GREEN (both new methods still passed against the deliberately pre-fix translator), which is exactly the "false-GREEN gate" failure mode this phase's D-05 discipline exists to catch. Reworded both fixtures' prose to describe the fix without the literal token ("Fixed by adding a named separator argument to the emitted `terms` call.") and re-confirmed RED pre-fix / GREEN post-fix. This is the identical class of bug Plan 02's SUMMARY documented (deviation #3, a literal `` ``linebreak()`` `` in fixture prose polluting a `linebreak()`-count assertion) — recorded here as a reminder that this pitfall recurs whenever a fixture's own documentation-prose quotes the exact token its assertion checks for.

## Verification

- `uv run pytest tests/test_deflist_term_concat_render_gate.py -x` — 3 passed (existing GATE-02 method + both new FID-05 methods).
- `uv run pytest tests/test_translator.py -q` — 108 passed (no non-render structural regression).
- `uv run pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q` — 1 passed (~13s, corpus cache warm) — the full ~684-page Sphinx `doc/` corpus stays fatal-free after the fix. This closes Cluster A's phase-gate requirement (Pitfall 4).
- **Full Cluster-A regression sweep:** `uv run pytest tests/test_paragraph_concat_render_gate.py tests/test_desc_bodyless_concat_render_gate.py tests/test_desc_signature_concat_render_gate.py tests/test_rubric_option_concat_render_gate.py tests/test_deflist_term_concat_render_gate.py -q` — 8 passed. All five Cluster-A findings (FID-02..FID-06) verified green together.
- `uv run pytest -q -m "not slow"` — 438 passed, 45 failed. The 45 failures are the same pre-existing, documented NixOS-sandbox environmental failures in `tests/test_integration_multi_doc.py` and `tests/test_integration_nested_toctree.py` recorded in Plan 01/02's SUMMARYs (436 passed there; +2 here for the two new render-gate test methods added this plan) — unrelated to this plan's `translator.py` change.
- `uv run black --check typsphinx/translator.py tests/test_deflist_term_concat_render_gate.py tests/fixtures/deflist_term_in_listitem_render_gate/conf.py tests/fixtures/deflist_term_nested_list_render_gate/conf.py` — required one reformat of the test module (applied via `black`, not `--check`); all four files clean after.
- `uv run mypy typsphinx/translator.py` — `Success: no issues found in 1 source file`.
- `uv run ruff check` could not run in this NixOS sandbox (`Could not start dynamically linked executable: ruff` — the same pre-existing environmental limitation documented in Plan 01/02's SUMMARYs and project memory, not caused by this plan's changes).
- `git status --short` confirmed only the plan's declared `files_modified` changed — no touch to `writer.py` / `template_engine.py` / `templates/base.typ` (the `@preview` version-sync surface stays untouched, milestone invariant).

**Worktree provisioning:** ran `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` first (per CLAUDE.md's "Worktree-isolated execution" section) to provision this worktree's own `.venv`, then ran every subsequent test/build command via `uv run` so `import typsphinx` bound to this worktree's edited copy rather than the main checkout's editable install. GATE-01 was confirmed RED against the worktree's pre-fix code and GREEN post-fix (see "RED → GREEN Proof" above).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixture prose accidentally contained a literal double-backtick separator-fix description**
- **Found during:** the mandatory RED-proof step (temporarily reverting the translator fix and re-running the new gate methods) for both new fixtures
- **Issue:** both `index.rst` drafts described the fix using the literal text `` ``terms(separator: linebreak(), ...)`` ``, which docutils renders as `raw("terms(separator: linebreak(), ...)")` in the emitted `.typ` — a false positive for the D-05 structural assert (`"terms(separator: linebreak()" in typ_text` matched the prose's own literal text even against the deliberately-reverted pre-fix translator).
- **Fix:** reworded both fixtures' prose to describe the fix without the literal token.
- **Files modified:** `tests/fixtures/deflist_term_in_listitem_render_gate/index.rst`, `tests/fixtures/deflist_term_nested_list_render_gate/index.rst`
- **Commit:** `fb7594d` (folded into the single task commit; the literal-collision draft was never committed separately)

## Known Stubs

None.

## Threat Flags

None — the fix injects only the FIXED literal `separator: linebreak(),` into the `terms(...)` call, never user-controlled content; term/definition content still flows through the unchanged `escape_typst_string()` helper. Matches the plan's own threat model (T-19-01, disposition `mitigate`, confirmed satisfied by inspection of the diff).

## Self-Check: PASSED

- `typsphinx/translator.py` — FOUND (modified)
- `tests/test_deflist_term_concat_render_gate.py` — FOUND (modified)
- `tests/fixtures/deflist_term_in_listitem_render_gate/conf.py` — FOUND
- `tests/fixtures/deflist_term_in_listitem_render_gate/index.rst` — FOUND
- `tests/fixtures/deflist_term_nested_list_render_gate/conf.py` — FOUND
- `tests/fixtures/deflist_term_nested_list_render_gate/index.rst` — FOUND
- commit `fb7594d` — FOUND in `git log --oneline --all`
