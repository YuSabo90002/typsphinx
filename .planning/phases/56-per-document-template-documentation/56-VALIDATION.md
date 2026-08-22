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

> Populated by `/gsd-plan-phase`. Requirement → test-type rows are fixed by research; Task ID / Plan /
> Wave / Threat Ref filled at plan time (2026-08-16).

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 56-01-T1 | 56-01 | 1 | DOC-15 | T-56-01, T-56-02 | AST parse only — never `exec`/`import` a scanned module; repo-relative paths only | static AST-scan of every `raise ExtensionError` in `typsphinx/*.py`, two-way against the published catalogue | `uv run pytest tests/test_registry_documentation_gate.py -x -q && uv run tox -e docs-html && uv run tox -e docs-pdf` | ❌ W0 — new module | ⬜ pending |
| 56-01-T2 | 56-01 | 1 | DOC-15 | T-56-01 | same | falsification self-tests over inline synthetic inputs (no files on disk) | `uv run pytest tests/test_registry_documentation_gate.py -q` | ❌ W0 | ⬜ pending |
| 56-01-T3 | 56-01 | 1 | DOC-15 | T-56-02, T-56-03 | bounded `rglob` over three repo-relative policed roots | repo-wide presence sweep for the retracted element-[4] phrase + teeth test | `uv run pytest tests/test_registry_documentation_gate.py -q` | ❌ W0 | ⬜ pending |
| 56-02-T1 | 56-02 | 2 | DOC-15 | — | N/A | prose ↔ existing same-line `templates_path` gate | `uv run pytest tests/test_docs_template_layout_gate.py tests/test_registry_documentation_gate.py tests/test_docs_contract_claims_gate.py -q` | ✅ + ❌ new class | ⬜ pending |
| 56-02-T2 | 56-02 | 2 | DOC-15 | T-56-06 | imports this repo's own production modules only | published key-naming rules ↔ imported `_KEY_SHAPE_REJECTION_CASES` enumeration + teeth test | `uv run pytest tests/test_registry_documentation_gate.py -q` | ❌ W0 | ⬜ pending |
| 56-02-T3 | 56-02 | 2 | DOC-17 | T-56-04, T-56-05 | test-authored `conf.py` under `tmp_path`; fixed subprocess argv | prose ↔ imported `REMOVED_CONFIG_VALUES`, plus a real `sphinx-build` proving one warning per name in declaration order | `uv run pytest tests/test_registry_documentation_gate.py tests/test_removed_config_deprecation_gate.py -q` | ❌ W0 + ✅ extend | ⬜ pending |
| 56-03-T1 | 56-03 | 2 | DOC-15 | — | N/A | existing prose-binding class over the rewritten layout page | `uv run pytest tests/test_output_layout_docs_gate.py -x -q` | ✅ exists | ⬜ pending |
| 56-03-T2 | 56-03 | 2 | SC#4 (`output_layout.rst` count rule) | — | N/A | existing prose-binding assertion, **updated in the same commit as the prose fix** | `uv run pytest tests/test_output_layout_docs_gate.py -q` | ✅ **update, don't create** | ⬜ pending |
| 56-03-T3 | 56-03 | 2 | DOC-15 (D-03 amended) | T-56-07, T-56-08, T-56-09 | runtime `conf.py` is a test-written literal; project root is always the `tmp_path` build dir | real `sphinx-build -b typst` + `typst.compile()` pinning BOTH root branches, plus a never-skipping prose check that the rule is published conditionally | `uv run pytest tests/test_hand_compile_root_gate.py tests/test_output_layout_docs_gate.py -q` | ❌ W0 — new module | ⬜ pending |
| 56-04-T1 | 56-04 | 2 | DOC-16 | T-56-10, T-56-12 | static committed BibTeX data, read never executed | real `sphinx-build -b typstpdf` → `typst.compile()`; new asset asserted at the measured bundle destination | `uv run pytest tests/test_user_template_relative_asset_gate.py -q` | ✅ extend fixture | ⬜ pending |
| 56-04-T2 | 56-04 | 2 | DOC-16 | — | N/A | prose correction validated by both doc builds and the existing layout gates | `uv run pytest tests/test_docs_template_layout_gate.py tests/test_docs_contract_claims_gate.py -q && uv run tox -e docs-html && uv run tox -e docs-pdf` | ✅ exists | ⬜ pending |
| 56-04-T3 | 56-04 | 2 | DOC-16 | T-56-11 | text read + containment only; no `exec`/import of read pages | prose-binding class (outside the `typst-py` skipif scope) tying both pages to the fixture's measured destination + teeth test | `uv run pytest tests/test_user_template_relative_asset_gate.py tests/test_docs_template_layout_gate.py tests/test_output_layout_docs_gate.py -q` | ❌ W0 — new class | ⬜ pending |
| 56-05-T1 | 56-05 | 3 | DOC-15, DOC-16, DOC-17 | T-56-16 | every sweep command and its full output recorded against a named commit | execution-time re-run of all five discovery greps + written per-hit disposition + real builds of both example projects | `uv run pytest tests/test_examples_charged_ieee_gate.py -q && uv run pytest -q` | ❌ W0 — new record | ⬜ pending |
| 56-05-T2 | 56-05 | 3 | SC#4 | T-56-13, T-56-14, T-56-15 | swept `.py` files are read as TEXT and regex-matched — never `exec`/imported; repo-relative roots only | run-time anchored repo-wide presence gate with reasoned exclusions, a staleness test and both-direction teeth tests | `uv run pytest tests/test_bundle_layout_sweep_gate.py -q && uv run pytest -q` | ❌ W0 — new module | ⬜ pending |
| 56-05-T3 | 56-05 | 3 | DOC-15, DOC-16, DOC-17 | — | N/A | phase-boundary gate: full suite + lint/type trio + both doc builds + empty `typsphinx/` diff | `uv run pytest -q && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/ && uv run tox -e docs-html && uv run tox -e docs-pdf && git diff --stat typsphinx/` | ✅ all exist | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Wave map:** W1 = `56-01` (the tracer: the two-way catalogue gate proven end-to-end before any
expansion prose is written) · W2 = `56-02` + `56-03` + `56-04` (zero `files_modified` overlap) ·
W3 = `56-05` (the sweep audit, deliberately one wave AFTER every prose fix it audits — an auditor
sharing a wave with the measurement abstains on its own criterion because the evidence does not yet
exist in its worktree).

**Same-wave coupling checked explicitly:** `56-03` owns `tests/test_output_layout_docs_gate.py`,
whose `test_helper_derived_wrapper_stem_matches_the_published_walkthroughs` also reads
`docs/source/user_guide/templates.rst`, which `56-04` owns. `56-04`'s edits are confined to the
`Template Assets` subsection and its acceptance criteria re-run that module, so the disjoint-files
merge hazard is covered rather than assumed. The `output_layout.rst` count clause and the assertion
quoting it are deliberately in the SAME task of the SAME plan, never split across a wave.

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
