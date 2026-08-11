---
phase: 43
slug: table-state-correctness-nested-tables-empty-title-anchors
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-04
---

# Phase 43 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `43-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest `>=8.4,<10` (`pyproject.toml:37`); config in `pyproject.toml` `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `python_files = ["test_*.py"]`) |
| **Config file** | `pyproject.toml` (no separate `pytest.ini`) |
| **Quick run command** | `uv run python -m pytest tests/test_nested_table_render_gate.py tests/test_table_empty_caption_anchor_render_gate.py tests/test_nested_figure_render_gate.py -x` |
| **Full suite command** | `uv run python -m pytest` (matches CI; per `CLAUDE.md`, run every command via `uv run` inside a worktree) |
| **Estimated runtime** | ~60 seconds quick (3 render gates, each a `sphinx-build` + `typst.compile()` subprocess); full suite several minutes |

---

## Sampling Rate

- **After every task commit:** Run the quick run command above.
- **After every plan wave:** Run `uv run python -m pytest` (full suite) plus `black --check .`, `ruff check .`, `mypy typsphinx/` — matching CI exactly.
- **Before `/gsd-verify-work`:** Full suite green, plus the D-04 two-build byte-invariance sweep over all of `docs/source` and every root under `tests/roots` (method: `42-GATE-EVIDENCE-05.md`, widened per D-04, positive control mandatory).
- **Max feedback latency:** 60 seconds (quick run).

---

## Per-Task Verification Map

> Task IDs are assigned by the planner. This table is filled in during `/gsd-validate-phase`
> (or by the executor as tasks land); the requirement→command mapping below is fixed now.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | 0 | TBL-04 | — | N/A | integration (structural RED — the broken output compiles cleanly, so there is no exception to assert on) | `uv run python -m pytest tests/test_nested_table_render_gate.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | TBL-05 | — | N/A | integration (classic `TypstError` RED — aborts at label resolution) | `uv run python -m pytest tests/test_table_empty_caption_anchor_render_gate.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | FIG-01 | — | N/A | integration (classic `TypstError` RED — `unexpected argument`, per RESEARCH Pitfall 4, which corrects the phase description's "silently dropped caption" framing) | `uv run python -m pytest tests/test_nested_figure_render_gate.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | TBL-04 / FIG-01 | T-43-01 | Stack/snapshot teardown must not underflow on an unbalanced `depart_*` — guard with `if stack:` rather than a bare `.pop()` (ASVS V5, RESEARCH § Security Domain) | unit | `uv run python -m pytest tests/test_translator.py -x` | ✅ | ⬜ pending |
| TBD | TBD | — | QUA-01 | — | N/A | documentation — comment-only diff, no runtime behavior change | `grep -n 'skip_ids' typsphinx/translator.py` (re-grep at fix time; do not trust the todo's recorded count) | ✅ N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/fixtures/nested_table_render_gate/{conf.py,index.rst}` — TBL-04, four shapes per D-01: `list-table` in `list-table`, grid `table` in `list-table`, `list-table` in grid `table`, and a three-level nest
- [ ] `tests/test_nested_table_render_gate.py` — structural assertions over the emitted `.typ` plus pypdf text
- [ ] `tests/fixtures/table_empty_caption_anchor_render_gate/{conf.py,index.rst}` — TBL-05, using the exact reproducing rST from CONTEXT `<specifics>` §1 (keep the explicit `:ref:` link text — a bare `` :ref:`tbl-target` `` makes Sphinx refuse first and the RED never reproduces)
- [ ] `tests/test_table_empty_caption_anchor_render_gate.py` — assert the pre-fix `TypstError: label <index:tbl-target> does not exist in the document`
- [ ] `tests/fixtures/nested_figure_render_gate/{conf.py,img.png,index.rst}` — FIG-01
- [ ] `tests/test_nested_figure_render_gate.py` — assert the pre-fix `TypstError: unexpected argument` substring, not merely a missing-caption structural check
- [ ] No new pytest fixture/conftest infrastructure needed — the established `_run_sphinx_build_typstpdf` subprocess helper pattern (`tests/test_table_in_list_item_render_gate.py`, `tests/test_wide_table_render_gate.py`) is copy-adapted per file; verified that no shared conftest helper exists for this today

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Milestone branch is on `origin` and CI has run against it, including the Windows lanes (SC#5, milestone invariant #5) | — (roadmap SC, not a REQ-ID) | Requires a real network push and a real GitHub Actions run; not assertable from pytest | `git push -u origin gsd/v0.7.1-bug-fix-round`, then `git ls-remote --heads origin` must hit, and `gh run list --branch gsd/v0.7.1-bug-fix-round` must show at least one completed run including Windows |
| SC#4 byte-invariance across the change | TBL-04, TBL-05, FIG-01 | Requires two builds of two different source trees (`git archive` export of the pre-fix tree) plus a positive control; harness-shaped, not a unit test | Follow `42-GATE-EVIDENCE-05.md` verbatim, widened per D-04 to all of `docs/source` and every root under `tests/roots`. Assert `typsphinx.__file__` resolves INTO the exported tree. An empty diff proves nothing without the positive control. |
| `sphinx-build` emits no `WARNING: unknown node type: <legend>` | FIG-01 | Warning-stream assertion — can be automated inside the FIG-01 render gate if the helper captures stderr; verify the helper does before relying on it | Capture `sphinx-build` stderr in the FIG-01 gate and assert the substring is absent |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
