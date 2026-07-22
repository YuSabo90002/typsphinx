---
phase: 22
slug: typstpdf-target-name-pdf-fix-issue-117
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-21
---

# Phase 22 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `22-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml` `[tool.pytest.ini_options]`) |
| **Config file** | `pyproject.toml` (existing — no Wave 0 framework gap) |
| **Quick run command** | `uv run pytest tests/test_builder.py tests/test_config.py -q` |
| **Full suite command** | `uv run pytest` (network-dependent corpus gate is `-m slow`; `pytest -m "not slow"` skips it) |
| **Estimated runtime** | ~30 s quick · ~3–5 min full (`-m "not slow"`) · corpus gate adds several minutes + network |

**Execution mode:** CLAUDE.md mandates worktree-isolated execution. Every command above runs via
`uv run` inside the executor's own worktree, after
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`. Sphinx is invoked as
`sys.executable -m sphinx` inside fixtures — **never** `uv run <compiled-binary>` (NixOS sandbox PATH hazard).

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/test_builder.py tests/test_<new-gate-module>.py -q`
- **After every plan wave:** Run `uv run pytest -m "not slow"` (fast suite — includes the new GATE-01 module and the 5 named regression modules)
- **Before `/gsd-verify-work`:** `uv run pytest` (full suite including the `-m slow` corpus gate) **and** `tox -e docs-pdf` must both be green
- **Max feedback latency:** ~30 s (per-task quick run)

---

## Per-Task Verification Map

> Seeded at plan time; the planner/executor fills Task IDs as plans are written.
> Every row below is a **required** observable — a task must exist that owns it.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | 0 | PDF-01 | — | N/A | integration (real `typst.compile()`) | `uv run pytest tests/test_<new-gate-module>.py -q` | ❌ W0 — new GATE-01 module | ⬜ pending |
| TBD | TBD | 1 | PDF-01 | — | N/A | integration | `uv run pytest tests/test_<new-gate-module>.py -q` (asserts `output.typ`+`output.pdf` **present** AND `index.typ`+`index.pdf` **absent**, `%PDF` magic) | ❌ W0 | ⬜ pending |
| TBD | TBD | 1 | PDF-01 (regression guard) | — | N/A | unit/integration | `uv run pytest tests/test_builder.py tests/test_builder_requirement13.py tests/test_integration_nested_toctree.py tests/test_config_template_mapping.py tests/test_config_toctree_defaults.py -q` | ✅ existing, expected unmodified | ⬜ pending |
| TBD | TBD | 1 | D-12 (corpus-gate companion) | — | N/A | integration (slow, network) | `uv run pytest tests/test_corpus_gate.py -k TestCorpusRenderGate -m slow -q` | ✅ existing — **1-line assertion edit required** (`index.pdf` → `sphinx-corpus.pdf`, ~line 330) | ⬜ pending |
| TBD | TBD | 1 | D-12 (dogfood docs build) | — | N/A | integration (real docs build) | `tox -e docs-pdf` → emits `typsphinx.typ` / `typsphinx.pdf` | ✅ existing tox env | ⬜ pending |
| TBD | TBD | 1 | `get_target_uri` non-regression | — | N/A | integration (real `typst.compile()`) | cross-doc `:ref:`/`:doc:` into a `target != docname` master compiles with no `"label ... does not exist"` fatal | ❌ W0 — no existing fixture pairs `target != docname` with a cross-reference | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] **New GATE-01 module** (name planner's call, e.g. `tests/test_target_name_render_gate.py`) — real `-b typstpdf` compile driven by `tests/roots/test-basic` (which already declares `("index", "output.typ", …)`). Follows the fixture shape of `tests/test_desc_signature_concat_render_gate.py` verbatim. Must assert **both directions** (`output.*` present AND `index.*` absent) so it fails on both counts pre-fix.
- [ ] **Cross-document-reference-into-renamed-master coverage** — no current fixture pairs `target != docname` with a cross-doc reference. Cheapest route per RESEARCH.md: add a non-identity target name to an existing multi-doc fixture's `conf.py` (e.g. one of the `integration_*` fixtures) rather than building a new project.
- [ ] **`tests/test_corpus_gate.py` assertion update** (~line 330, `index.pdf` → `sphinx-corpus.pdf`) — not a new file, but easy to miss because the test is `@pytest.mark.slow`. It currently passes *because of* the bug this phase fixes.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `logger.warning` text for a path-bearing target name (D-06/D-07) | PDF-01 | Warning *text* is UX, not a contract — but its *emission* is automatable via `caplog` | Prefer automating emission with `caplog`; only the wording is a manual read |

*Otherwise: all phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (new GATE-01 module, cross-ref fixture, corpus-gate edit)
- [ ] No watch-mode flags
- [ ] Feedback latency < 60 s for the per-task quick run
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
