---
phase: 56
slug: per-document-template-documentation
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-16
---

# Phase 56 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `56-RESEARCH.md` § "Validation Architecture" (all values measured at HEAD `f07e8cb8`).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (config in `pyproject.toml`) |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest tests/test_docs_contract_claims_gate.py tests/test_output_layout_docs_gate.py tests/test_docs_template_layout_gate.py tests/test_user_template_relative_asset_gate.py tests/test_quickstart_docs_gate.py tests/test_removed_config_deprecation_gate.py -q` (the six existing doc-gate modules; add the two new ones once written) |
| **Full suite command** | `uv run pytest -q` |
| **Estimated runtime** | ~122 seconds full suite (measured: 1366 passed, 5 skipped, 121.6s); doc-gate subset is seconds |
| **Doc build gate** | `uv run tox -e docs-html && uv run tox -e docs-pdf` (~3.3s each, both green at HEAD) |
| **Lint/type gate** | `uv run black --check . && uv run ruff check . && uv run mypy typsphinx/` (all clean at HEAD) |

**Baseline truth (do not attribute to this phase):** the full suite is green at HEAD — 1366 passed,
5 skipped, **0 failed**. The `tests/test_state_guard_shapes_gate.py` failures recorded in
`53-.../deferred-items.md` did **not** reproduce in this measurement. Any RED that appears during
this phase is therefore this phase's to fix; re-measure before claiming a pre-existing failure.

**Execution mode:** worktree isolation is the standing mode (`CLAUDE.md` § "Worktree-isolated
execution"). Every command above runs after
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, and through `uv run`.

---

## Sampling Rate

- **After every task commit:** run the specific gate module(s) the task's files touch — e.g.
  `uv run pytest tests/test_output_layout_docs_gate.py -x` after any `output_layout.rst` edit.
- **After every plan wave:** `uv run pytest -q` (full suite, ~122s) plus
  `uv run black --check . && uv run ruff check . && uv run mypy typsphinx/`.
- **Before `/gsd-verify-work`:** full suite green **and** `uv run tox -e docs-html && uv run tox -e docs-pdf`
  green (SC#4 names these two commands explicitly).
- **Max feedback latency:** ~10 seconds for the per-task doc-gate subset; ~122 seconds for the full suite.

---

## Per-Task Verification Map

> Populated by `/gsd-plan-phase` task IDs once PLAN.md files exist. Requirement → test-type rows below
> are fixed by research; the Task ID / Plan / Wave columns are filled at plan time.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | DOC-15 | — | N/A | static prose-scan + repo-wide grep self-test | new D-06 two-way catalogue gate module | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | DOC-15 | — | N/A | static AST-scan of `typsphinx/*.py` `ExtensionError` raises | same module | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | DOC-16 | — | N/A | real `sphinx-build -b typstpdf` → `typst.compile()` | `uv run pytest tests/test_user_template_relative_asset_gate.py -x` | ✅ extend | ⬜ pending |
| TBD | TBD | TBD | DOC-16 | — | N/A | prose-binding against the extended fixture's measured destination paths | same module or sibling gate | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | DOC-17 | — | N/A | prose ↔ `REMOVED_CONFIG_VALUES` dict binding | new module or extend `tests/test_removed_config_deprecation_gate.py` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | SC#4 | — | N/A | repo-wide grep self-test + both doc builds | `uv run tox -e docs-html && uv run tox -e docs-pdf` | ✅ tox envs exist | ⬜ pending |
| TBD | TBD | TBD | SC#4 (`output_layout.rst:159`) | — | N/A | existing prose-binding assertion, **updated in the same task as the prose fix** | `uv run pytest tests/test_output_layout_docs_gate.py -x` | ✅ **update, don't create** | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] New test module binding `configuration.rst`'s registry subsection + error table + key-naming
      rules + removed-values subsection to `typsphinx/template_registry.py`, `typsphinx/builder.py`,
      and `typsphinx/removed_config.py` — the **two-way** leading-clause gate (D-06) and the
      removed-config binding (DOC-17). Module name at the planner's discretion, subject to D-06's
      no-skip constraint (no `typst-py` import guard, no `sphinx-build` subprocess).
- [ ] `tests/fixtures/user_template_relative_asset_gate/_typst/refs.bib` — new fixture file plus a
      `#bibliography("refs.bib")` call in `_typst/branded.typ` (DOC-16).
- [ ] New or extended test method proving `templates.rst`/`advanced.rst`'s corrected asset prose
      matches the extended fixture's real build output (DOC-16).
- [ ] **Update, not create:** `tests/test_output_layout_docs_gate.py::test_page_states_the_shared_child_composition`
      asserts the literal `"writes ten ``.typ`` files"`. Correcting `output_layout.rst:159` to "nine"
      **must happen in the same task** or the suite goes RED.
- [ ] The D-06 shape scan must be **AST-based, not per-line regex**: `builder.py:2151` raises the
      CONF-17 message through the shared `_conf17_violation_message()` helper at a structurally
      different call site, and `template_registry.py:422` relies on implicit adjacent-string-literal
      concatenation. A naive line scan miscounts shapes.
- [ ] Each new gate carries a **"patterns have teeth" self-test** (the
      `tests/test_docs_contract_claims_gate.py` shape) proving the detector fires on a known-bad
      sentence. Without it a doc gate can pass vacuously.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Rendered readability of the error-catalogue table and key-naming subsection in both furo HTML and the typstpdf PDF | DOC-15 | Layout/legibility is not expressible as an assertion; the *build-green* half is automated by `tox -e docs-html` / `docs-pdf` | Open `docs/build/html/user_guide/configuration.html` and the `docs-pdf` output; confirm the table renders with all rows visible and no overflow |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 122s (full suite) / < 10s (doc-gate subset)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
