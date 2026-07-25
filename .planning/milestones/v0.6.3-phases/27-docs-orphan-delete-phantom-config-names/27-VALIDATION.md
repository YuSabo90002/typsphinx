---
phase: 27
slug: docs-orphan-delete-phantom-config-names
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-24
---

# Phase 27 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Docs-only, content-fidelity phase: validation is grep-assertion + build-green +
> full-suite-green, NOT unit tests of prose. Mirrors CONTEXT.md D-12.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing suite) for the collateral test-file deletion; grep/`comm` assertions + `tox` docs builds for `.rst` content |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`), `tox.ini` |
| **Quick run command** | `uv run pytest tests/test_documentation_usage.py tests/test_documentation_installation.py -q` (sibling doc-existence tests must stay green — NOT touched here) + phantom grep-zero checks |
| **Full suite command** | `uv run pytest` (must be fully green AFTER `tests/test_documentation_configuration.py` is deleted alongside the orphan) |
| **Estimated runtime** | full suite ~ a few minutes; grep checks near-instant; `tox -e docs-html` fast single-lang |

---

## Sampling Rate

- **After every task commit:** phantom-name grep-zero checks (near-instant) after each `.rst` edit
- **After every plan wave:** `uv run tox -e docs-html` (fast single-lang sanity)
- **Phase gate (before `/gsd-verify-work`):** `uv run tox -e docs-multilang` + `uv run tox -e docs-pdf` (mirrors CI `docs.yml`) + `uv run pytest` (full suite) all green
- **Max feedback latency:** grep near-instant; docs-html ~tens of seconds

---

## Per-Task Verification Map

*(Task IDs are assigned by the planner; rows below are requirement-level and will map onto plan tasks.)*

| Req | Behavior | Wave | Test Type | Automated Command | File Exists | Status |
|-----|----------|------|-----------|-------------------|-------------|--------|
| DOC-06 | Orphan `docs/configuration.rst` deleted + its collateral test file removed; no live `docs/source/` xref | 1 | grep + pytest | `grep -rn ':doc:\`configuration\`' docs/source/` (zero) · `git rm tests/test_documentation_configuration.py` · `uv run pytest` (green) | ✅ existing suite | ⬜ pending |
| DOC-07 A | Phantom names gone from `user_guide/configuration.rst`; working `typst_elements` example present | 1 | grep + build | phantom grep-zero over `user_guide/configuration.rst` + surviving-`typst_*` ⊆ registered set + `uv run tox -e docs-html` | ✅ | ⬜ pending |
| DOC-07 B | `list-table` deleted from `api/index.rst`; `.po` follows; multilang green | 1 | grep + build | phantom grep-zero over `api/index.rst` + scoped `.po` regen + `uv run tox -e docs-multilang` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements.* No new test files are needed — this is a
content-fidelity phase, not a behavior phase. The ONE test-infra change is a **deletion**:
`tests/test_documentation_configuration.py` (11 functions asserting the orphan exists/has content)
must be `git rm`'d in the SAME wave as the orphan `git rm`, or `uv run pytest` goes red.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| "No unique useful content lost" salvage-judgement | DOC-06 (SC#1) | Requires human/agent diff-judgement of orphan vs canonical | Diff the 489-line orphan against `docs/source/user_guide/configuration.rst`; the orphan's only "extra" registered names are `typst_template_mapping`/`typst_package_imports`/`typst_debug`, and its `typst_elements` example uses phantom `mainfont`/`monofont` keys → confirmed superseded; salvage nothing (deferred as a follow-up todo, not this phase) |
| Broken-xref check on SC#5 | DOC-07 (SC#5) | `sphinx-build` has no `-W`; broken `:doc:`/`:ref:` is a non-fatal `WARNING:` line | Compare `sphinx-build -b html` warning output against the established baseline of exactly ONE pre-existing unrelated warning (translator.py docstring spacing); any NEW warning fails the gate |

---

## Validation Sign-Off

- [ ] All tasks have automated grep/build verify or are explicitly manual (above)
- [ ] Sampling continuity: grep-zero after each `.rst` edit; docs-html per wave
- [ ] Wave 0: `tests/test_documentation_configuration.py` deletion is in the SAME wave as the orphan deletion
- [ ] No watch-mode flags
- [ ] Phase-gate commands mirror CI `docs.yml` (`docs-multilang` + `docs-pdf`) + full `pytest`
- [ ] `nyquist_compliant: true` set in frontmatter (by validate-phase after execution)

**Approval:** pending
