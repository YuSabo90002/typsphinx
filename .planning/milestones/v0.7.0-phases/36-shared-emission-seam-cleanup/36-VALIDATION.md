---
phase: 36
slug: shared-emission-seam-cleanup
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-01
---

# Phase 36 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `36-RESEARCH.md` § "Validation Architecture" (all commands measured 2026-08-01).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`, `testpaths = ["tests"]`) |
| **Quick run command** | `uv run pytest tests/test_desc_rubric_decoupling_render_gate.py tests/test_inline_math_after_text_render_gate.py -q` |
| **Full suite command** | `uv run pytest -q --tb=no -rf` |
| **Estimated runtime** | ~180 seconds (full suite; measured baseline 649 passed / 1 skipped pre-Phase-36) |

**Worktree note (CLAUDE.md standing rule):** every command above runs inside the executor's own
worktree venv. Provision first with
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, then prefix every command with
`uv run`. This is mandatory, not conditional — without it pytest imports the *main* checkout's
package and gates stay RED after a correct fix.

---

## Sampling Rate

- **After every task commit:** Run the regression net — the five existing render gates that already
  exercise this seam, plus the two new/modified files:
  ```
  uv run pytest \
    tests/test_desc_rubric_decoupling_render_gate.py \
    tests/test_inline_math_after_text_render_gate.py \
    tests/test_desc_signature_concat_render_gate.py \
    tests/test_desc_signature_anchor_render_gate.py \
    tests/test_desc_sig_space_render_gate.py \
    tests/test_rubric_option_concat_render_gate.py \
    tests/test_rubric_propagated_target_render_gate.py -q
  ```
- **After every plan wave:** Run `uv run pytest -q --tb=no -rf`
- **Before `/gsd-verify-work`:** Full suite green, lint/type trio green
  (`uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/`), and the slow-marked
  full-corpus gate explicitly re-run: `uv run pytest tests/test_corpus_gate.py -q -m slow`
- **Max feedback latency:** 30 seconds (per-task regression net)

---

## Per-Task Verification Map

Task IDs are provisional pending the planner's decomposition; the requirement→signal mapping below
is binding regardless of how tasks are numbered.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 36-01-0x | 01 | 1 | ADM-06 (SC#2 fixture) | — | N/A | fixture | `uv run pytest tests/test_desc_rubric_decoupling_render_gate.py -q` | ❌ W0 | ⬜ pending |
| 36-01-0x | 01 | 1 | ADM-06 (SC#2 golden) | — | N/A | golden-diff regression | `uv run pytest tests/test_desc_rubric_decoupling_render_gate.py -q` | ❌ W0 | ⬜ pending |
| 36-01-0x | 01 | 1 | ADM-06 (SC#1 grep) | — | N/A | structural (scoped grep, wrapped in pytest) | `uv run pytest tests/test_desc_rubric_decoupling_render_gate.py -q -k grep` | ❌ W0 | ⬜ pending |
| 36-01-0x | 01 | 1 | ADM-06 (decoupling) | — | N/A | byte-identity | `uv run pytest tests/test_desc_rubric_decoupling_render_gate.py -q` | ❌ W0 | ⬜ pending |
| 36-02-0x | 02 | 2 | MATH-02 (SC#3 RED) | — | N/A | real-compile structural gate | `uv run pytest tests/test_inline_math_after_text_render_gate.py -q` | ✅ modify in place | ⬜ pending |
| 36-02-0x | 02 | 2 | MATH-02 (D-04 PDF) | — | N/A | invariance regression | `uv run pytest tests/test_inline_math_after_text_render_gate.py -q` | ✅ extend existing pypdf idiom | ⬜ pending |
| 36-02-0x | 02 | 2 | MATH-02 (fix) | — | N/A | structural GREEN | `uv run pytest tests/test_inline_math_after_text_render_gate.py -q` | ✅ | ⬜ pending |
| 36-0x-0x | — | last | SC#4 (census + gates) | — | N/A | full-suite + slow gate | `uv run pytest -q --tb=no -rf`; lint/type trio; `uv run pytest tests/test_corpus_gate.py -q -m slow` | ✅ all exist | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/fixtures/desc_rubric_decoupling_render_gate/{conf.py,index.rst}` — new fixture covering
      SC#2's four constructs: `desc_signature`, sibling signatures, rubric (including the
      `.. rubric:: Options` shape), and plain `**bold**` markup.
- [ ] `tests/test_desc_rubric_decoupling_render_gate.py` — new test file carrying both SC#1's scoped
      grep assertion and SC#2's byte-identity assertion against a captured pre-decoupling golden.
- [ ] `.planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md` — evidence artifact
      following Phase 34's `34-GATE-EVIDENCE.md` heading shape; a distinct deliverable, required
      before SC#4 can be marked complete.
- [ ] New assertions inside `tests/test_inline_math_after_text_render_gate.py`'s two existing test
      methods (Construct E plain / Construct G `:label:`) — no new fixture needed; the existing
      fixture already has the required shape and is already parameterised across mitex/native.

*No framework-install gap: pytest, typst-py, and pypdf are already installed dev dependencies.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| SC#2's "recorded diff of two real `sphinx-build -b typst` runs" | ADM-06 | The ROADMAP demands evidence of a *transition* (pre-decoupling vs post-decoupling), which a single-commit test run cannot observe by construction — the pre-state no longer exists once the fix lands. The automated golden-diff test is the durable proxy; the recorded diff is the one-time transition evidence. | Run `sphinx-build -b typst` against the new fixture on the commit *before* the decoupling, save the emitted `.typ`; repeat on the decoupling commit; `diff` them; paste the (empty) diff plus both commit SHAs into `36-GATE-EVIDENCE.md`. |
| SC#3's "assertion recorded RED against the unfixed translator" | MATH-02 | Same reason — RED is a property of a commit that ceases to exist. | Add the assertion, run it against the unfixed translator, capture the failure output verbatim into `36-GATE-EVIDENCE.md`, then land the fix and capture GREEN. |
| Environmental-failure triage | SC#4 | Per project memory, a set of integration tests fail for NixOS-sandbox reasons unrelated to this phase. Distinguishing environmental from real failures needs a human judgement against the recorded baseline. | Record the pre-change baseline failure set first; SC#4 is satisfied when the post-change failure set is *identical to* the baseline, not when it is empty. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
