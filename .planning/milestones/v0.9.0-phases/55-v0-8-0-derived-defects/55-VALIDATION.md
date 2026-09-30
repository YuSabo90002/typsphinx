---
phase: 55
slug: v0-8-0-derived-defects
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-16
---

# Phase 55 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded by plan-phase from `55-RESEARCH.md` § Validation Architecture. The Per-Task
> Verification Map is populated from the PLAN.md task IDs once planning completes.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest ≥8.4; `[tool.pytest.ini_options]` in `pyproject.toml:79-99` (`testpaths = ["tests"]`, markers `slow`/`integration`, `--strict-markers`); `sphinx.testing.fixtures` loaded as a plugin via `tests/conftest.py` |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `uv run pytest tests/test_<touched_module>.py -x` (e.g. `tests/test_include_edge_derivation_unit.py`, `tests/test_builder.py`) |
| **Full suite command** | `uv run pytest` |
| **Estimated runtime** | ~110 seconds full suite (Phase 54.1 measured baseline: 1318 passed / 5 skipped / 0 failed) |

**Worktree note (CLAUDE.md, standing execution mode):** every command above runs via `uv run`
inside the executor's own worktree, provisioned first with
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`. Without that, pytest imports the
unchanged main-tree package and gates stay RED after a correct fix.

**Green bar is UNCONDITIONAL ZERO FAILURES.** The `tests/test_state_guard_shapes_gate.py` carve-out
recorded under Phase 53's `deferred-items.md` was measured STALE on 2026-08-16 (that file now passes
18/18). Any plan or verification step citing "7 known-failing tests" as an accepted baseline is
misreading the baseline — see `55-RESEARCH.md` § Common Pitfalls, Pitfall 5.

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/test_<touched_module>.py -x`
- **After every plan wave:** Run `uv run pytest`, plus the three CI-matching gates —
  `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/` (STATE.md's own recorded
  Phase 54.1 lesson: a CI-only defect class escapes a pytest-only post-merge gate)
- **IMG-03 exception (Pitfall 2):** the IMG-03 plan runs the **full** `tests/test_builder.py` module,
  not only its own new test, at per-task level — its hashed-key change is expected to turn
  `tests/test_builder.py:561` and `:623` RED unless they are updated in the same change
- **Before `/gsd-verify-work`:** Full suite green (zero failures), all three lint/type gates green
- **Milestone invariant #9:** `git ls-remote --heads origin gsd/v0.9.0-per-document-templates`
  confirming the milestone branch is pushed (paid every phase since Phase 43)
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

*Populated from PLAN.md task IDs after planning completes. The requirement→test mapping below is
the contract each task's `<verify>` must satisfy; it is carried verbatim from
`55-RESEARCH.md` § Validation Architecture.*

| Req ID | Behavior | Test Type | Automated Command | File Exists | Status |
|--------|----------|-----------|-------------------|-------------|--------|
| XREF-05 | With two docnames that sanitize to the same label (`a/b` vs `a_u2f_b`), a reference to the document absent from the compiling master degrades to plain text instead of linking to the decoy | integration (real `sphinx-build -b typstpdf` + `typst.compile()`, two-master compile) | `uv run pytest tests/test_xref_compile_time_guard_render_gate.py -k collision -x` | ✅ existing `test_label_collision_guard_links_to_decoy` — assertion direction to be inverted (D-04) | ⬜ pending |
| XREF-05 (injectivity property) | The re-escaping construction is injective in general, not merely on the one known fixture — probe ids containing `_u` + non-hex, the full `_u[0-9a-f]+_` token twice, and a trailing partial `_u2` | unit, property-style | `uv run pytest tests/test_<xref_label_injectivity>.py -x` | ❌ Wave 0 (Pitfall 3) | ⬜ pending |
| BLD-07 | `make_include_edge_key` escapes `#` and `>`, so two distinct edges whose docnames contain those characters produce distinct keys and the correct document is included in each master | integration (real compile, per D-05) **plus** a unit half for the pure-function property | new fixture dir + `uv run pytest tests/test_include_edge_derivation_unit.py -x` | ❌ Wave 0 — new fixture needed, nearest precedent `tests/fixtures/state_guard_substring_key_gate/` | ⬜ pending |
| BLD-08 | An include chain deeper than Python's recursion limit raises a named `ExtensionError` identifying the depth or cycle, not a raw `RecursionError` | unit | `uv run pytest tests/test_include_edge_derivation_unit.py -x` | ✅ module exists, ❌ test class needs adding | ⬜ pending |
| BLD-09 | The bare `path.isabs()` call (currently `builder.py:1561`, **not** the cited `:910` — Pitfall 1) is routed onto the same `posixpath.isabs(…) or _is_drive_qualified(…)` predicate its sibling call site uses, so a driveless-absolute Windows URI reaches the rehome/relocate/warn branch on Python 3.13. Fix is on the **product** side; the 52-09 test-side repair does not close this | unit, platform-independent string-shape assertion | `uv run pytest tests/test_builder.py -x` | ✅ module exists, ❌ test needs adding | ⬜ pending |
| IMG-03 | Two absolute image URIs in different directories sharing a basename, both escaping the output directory, relocate to two distinct keys instead of collapsing onto one | unit | `uv run pytest tests/test_builder.py -x` (full module, per Pitfall 2) | ✅ module exists (Phase 50 cluster at `:392-660`), ❌ test needs adding | ⬜ pending |
| IMG-03 (collateral) | `tests/test_builder.py:561` and `:623` — which assert the CURRENT pre-fix escape-branch key format — are updated in the SAME change as the hashed-key fix, not left to regress | unit regression | `uv run pytest tests/test_builder.py -k "escape_relocates_with_warning or cross_drive_value_error_relocates" -x` | ✅ currently green, must stay green | ⬜ pending |
| Binding constraint #6 (RED-before-fix) | Every one of the five defects has its pre-fix assertion written down and recorded BEFORE implementation starts, in the `55-0N-RED-EVIDENCE.md` shape used from Phase 54 onward (commit hash, fixture description, exact command, verbatim failure tail) | manual-once, evidence artifact | each gate run against the PRE-fix tree | N/A — evidence, not a repeatable gate | ⬜ pending |
| Cross-cutting | The `@preview` package count stays four and the 3-way version-sync surface (`writer.py`, `template_engine.py`, `templates/base.typ`) is untouched | existing gate | `uv run pytest tests/test_preview_version_sync.py -q` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] A new fixture directory for BLD-07's real-compile RED — a docname containing `#` (and one
      containing `>`), modeled on `tests/fixtures/state_guard_substring_key_gate/`'s shape
- [ ] BLD-08's synthesized-deep-chain test class inside `tests/test_include_edge_derivation_unit.py`
      (no new module — existing module, existing pattern)
- [ ] BLD-09's driveless-absolute-URI test inside `tests/test_builder.py`. Add a case; do **not**
      revert the Phase 52-09 drive-qualified fixture (Claude's Discretion, CONTEXT.md)
- [ ] IMG-03's two-same-basename-different-directory test inside `tests/test_builder.py`, beside the
      Phase 50 relocation cluster — plus the two collateral updates at `:561` and `:623`
- [ ] A property-style injectivity module for XREF-05's re-escaping construction (Pitfall 3)
- [ ] XREF-05 needs **no** new fixture — the existing `xref_label_collision_guard_gate` fixture and
      its already-passing characterization test ARE the RED evidence (D-04); only the fixture's
      `conf.py` comment block and the test's assertion direction change
- [ ] RED-evidence recording for all five defects, produced against the tree AS IT STANDS at the
      start of each plan, BEFORE any production code changes land

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| BLD-08's `ExtensionError` message reads as an *instruction* — it names the depth bound or the cycle so a user can find the offending toctree — not merely "too deep" | BLD-08 | Message quality is a judgement; the automated gate only pins the exception TYPE and that a depth/cycle identifier appears | Read the raised message from the BLD-08 unit test's captured `excinfo.value` and confirm it names the offending docname chain or the bound |
| The chosen BLD-08 depth-bound constant leaves usable headroom under Sphinx's own call-stack overhead | BLD-08 | The proposed value (900) is reasoned, not empirically measured against Sphinx's frame cost — see `55-RESEARCH.md` § Open Questions #2 | Run the deep-chain test at bound−1 and confirm it does NOT trip, and that a real `sphinx-build` of a legitimately deep project still completes |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
