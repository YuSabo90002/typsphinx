---
phase: 51
slug: two-layer-output-documentation
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-14
---

# Phase 51 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> Derived from `51-RESEARCH.md` § "Validation Architecture" (measured 2026-08-14).
> This is a **documentation phase**: zero lines change under `typsphinx/`. The only net-new
> executable artifact is the SC#3 prose-vs-code gate mandated by D-10 / D-11 / D-12.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing `dev` extra; the project's sole test framework) |
| **Config file** | none — pytest config lives in `pyproject.toml` (existing, no change) |
| **Quick run command** | `uv run python -m pytest tests/test_output_layout_docs_gate.py -q` |
| **Full suite command** | `uv run python -m pytest -q -m "not slow"` |
| **Estimated runtime** | ~5s for the new gate alone (five measured `-b typst` builds each completed in well under a second); ~2–4 min for the full suite |

**Environment notes binding on every executor (CLAUDE.md + measured 2026-08-14):**

- Worktree isolation is the standing execution mode. Provision first with
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, then run everything via `uv run`.
- The new gate MUST invoke Sphinx as `sys.executable -m sphinx` (the `_run_sphinx_build()` pattern in
  `tests/test_quickstart_docs_gate.py`). It MUST NOT use `subprocess.run(["uv", "run", "sphinx-build", …])`
  — that form is the known NixOS stub-ld exec hazard and produces environmental false failures.
- `typst.compile()` does **not** run in this sandbox (`FileNotFoundError`, measured live). The gate takes
  no `typst-py` dependency and asserts at the `.typ` level only (D-12).
- Any executor that must build `docs/source` needs `uv sync --extra dev --extra docs` (`myst_parser` is
  not in the base `dev` sync).

---

## Sampling Rate

- **After every task commit:** `uv run python -m pytest tests/test_output_layout_docs_gate.py -q`
  (once the gate module exists; before then, the task's own `<verify>` command)
- **After every plan wave:** `uv run python -m pytest -q -m "not slow"`
- **Before `/gsd-verify-work`:** Full suite must be green, and
  `grep -rn ':numref:' docs/source/ README.md CHANGELOG.md` must return empty (D-07)
- **Max feedback latency:** 300 seconds

---

## Per-Task Verification Map

*Populated by the planner 2026-08-14 from the six PLAN.md files. Execute-phase updates the Status column.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 51-01-01 | 01 | 1 | DOC-14 | T-51-01, T-51-02 | list-arg subprocess, no `shell=True`; only build-relative paths published | gate (tracer) | `uv run python -m pytest tests/test_output_layout_docs_gate.py -q` | ❌ W0 (creates it) | ⬜ pending |
| 51-01-02 | 01 | 1 | DOC-14 | T-51-02 | only build-relative paths published | gate | `uv run python -m pytest tests/test_output_layout_docs_gate.py -q` | ✅ | ⬜ pending |
| 51-02-01 | 02 | 2 | DOC-14 | T-51-04 | migration bullet names the still-refused target shapes | docs gate | `uv run python -m pytest tests/test_changelog_page_gate.py tests/test_docs_contract_claims_gate.py -q` | ✅ | ⬜ pending |
| 51-02-02 | 02 | 2 | DOC-14 | T-51-02 | build-relative path only | docs gate + negative grep | `uv run python -m pytest tests/test_changelog_page_gate.py -q && ! grep -q 'build/typst/index.typ' docs/source/changelog.rst` | ✅ | ⬜ pending |
| 51-03-01 | 03 | 2 | DOC-14 | T-51-01, T-51-03 | escape guard observed on the filesystem, not re-derived | gate | `uv run python -m pytest tests/test_output_layout_docs_gate.py -q` | ✅ | ⬜ pending |
| 51-03-02 | 03 | 2 | DOC-14 | T-51-05 | expected non-zero exit asserted, not treated as infra failure | gate | `uv run python -m pytest tests/test_output_layout_docs_gate.py tests/test_typst_documents_collision_gate.py -q` | ✅ | ⬜ pending |
| 51-04-01 | 04 | 2 | DOC-14 | T-51-02 | build-relative paths only | docs gate + negative greps | `uv run python -m pytest tests/test_output_layout_docs_gate.py tests/test_docs_contract_claims_gate.py -q` | ✅ | ⬜ pending |
| 51-04-02 | 04 | 2 | DOC-14 | T-51-03 | corrected element-2 text names all three still-refused shapes | docs gate + negative grep | `uv run python -m pytest tests/test_docs_contract_claims_gate.py tests/test_builder_output_stem.py -q` | ✅ | ⬜ pending |
| 51-04-03 | 04 | 2 | DOC-14 | — | N/A | docs gate + negative grep | `uv run python -m pytest tests/test_docs_contract_claims_gate.py -q` | ✅ | ⬜ pending |
| 51-05-01 | 05 | 2 | DOC-14 | T-51-06 | new RTD link shares the origin of every existing doc link | docs gate + negative grep | `uv run python -m pytest tests/test_quickstart_docs_gate.py -q` | ✅ | ⬜ pending |
| 51-05-02 | 05 | 2 | DOC-14 | T-51-02 | transcript directory path not published | real build + docs gate | `uv run python -m pytest tests/test_examples_basic.py tests/test_integration_advanced.py -q` | ✅ | ⬜ pending |
| 51-06-01 | 06 | 3 | DOC-14 | T-51-01 | list-arg subprocess over the reused fixture | gate | `uv run python -m pytest tests/test_output_layout_docs_gate.py -q` | ✅ | ⬜ pending |
| 51-06-02 | 06 | 3 | DOC-14 | T-51-02, T-51-07 | audit row count asserted mechanically; host paths elided | full suite + real docs build | `uv run python -m pytest -q -m "not slow"` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_output_layout_docs_gate.py` — the SC#3 gate module (D-10/D-11/D-12). Two-class shape
      per the `tests/test_quickstart_docs_gate.py` precedent: one class runs real `-b typst`
      `sys.executable -m sphinx` subprocess builds against `tests/fixtures/` projects and asserts the
      exact emitted `.typ` file set; one class reads the published page from disk with `Path` and
      asserts the prose names those exact filenames. **Never skips** — no `typst-py` import guard.
      Note: the precedent's own skip check is an *import* check, not a *compile* check, so copying it
      verbatim would misbehave here (`typst` imports but `typst.compile()` fails) — the new gate must
      omit the guard entirely rather than inherit it.
- [ ] `tests/fixtures/<gate-fixture-dirs>/` — fixture Sphinx projects for the worked-example shapes
      (bare target, explicit-path target, refusal cases). May reuse the existing
      `tests/fixtures/state_guard_{two,three}_master_gate` shapes for the shared-child case rather than
      inventing new ones.
- [ ] Expected values derived from the builder's own helpers (D-11), not hard-coded — see
      `51-RESEARCH.md` Part D for the exact helper names to import.

*No framework install needed: pytest and the `dev` extra already cover this phase.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Standalone content-file compile yields the document's own body with no children, no error, no warning | DOC-14 (SC#1) | Requires a real `typst.compile()`, which fails in this sandbox (`FileNotFoundError`, measured). Not re-measurable locally. | Evidence is Phase 49's already-recorded real-compile transcript, quoted in `51-RESEARCH.md` Part C § "Standalone-content-compile behaviour". Do not re-derive; cite it. |
| Shared child renders once per master, at that master's own traversal position and heading level | DOC-14 (SC#3) | PDF-marker counting needs a real compile (same constraint). | Evidence is Phase 49's `state_guard_three_master_gate` measurement (`COMMON-B-MARKER` count = 1 in all three masters; `common_b` heading levels `[3]` in m1, `[2]` in m2/m3). Cite, do not re-measure. |
| Repo-wide falsified-claim sweep completeness (D-04) | DOC-14 | One-time discovery grep, not a standing regression gate — no locked decision mandates a permanent "no stale `.typ` filename in docs/" test. | `51-RESEARCH.md` Part A's sweep table is the closed task list for this phase. Verify at phase close that every FALSE/MISLEADING row is either fixed or explicitly deferred with a reason — no silent drops. |
| `:numref:` absent from all published surfaces (D-07) | DOC-14 | Literal-absence check; cheaper as a scoped grep than a pytest module. | **CORRECTED AT PLANNING TIME (2026-08-14).** The single repo-wide grep this row originally proposed — `grep -rn ':numref:' docs/source/ README.md CHANGELOG.md` returning empty — is **unsatisfiable and would be wrong to satisfy**: `CHANGELOG.md` already carries two pre-existing occurrences (lines 68 and 246) in v0.7.x entries about a table anchor, entirely unrelated to the Phase 49 divergence D-07 excludes; satisfying it would mean rewriting shipped release history. Plan 51-06 Task 2 replaces it with three scoped checks: (a) `grep -rn ':numref:' docs/source/ README.md examples/` returns empty — measured empty at planning time and must stay empty; (b) `git diff --name-only HEAD -- CHANGELOG.md` is empty, so this phase adds no occurrence there and Phase 52's own amended SC#2 governs the new `## [0.8.0]` entry; (c) `grep -c ':numref:' CHANGELOG.md` is still exactly 2. **Planner decision: no standing pytest module** — D-07 forbids publishing, not testing, and the decision is rated `costly` because a later milestone is expected to reverse it. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 300s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
