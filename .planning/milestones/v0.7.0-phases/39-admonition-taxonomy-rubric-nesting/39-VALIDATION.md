---
phase: 39
slug: admonition-taxonomy-rubric-nesting
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-02
---

# Phase 39 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `39-RESEARCH.md` § "Validation Architecture" (all commands verified against the
> project's real pytest configuration this session).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4+ (project pin `pytest>=8.4,<10`) |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`, `testpaths = ["tests"]`, markers `slow` / `integration`) |
| **Quick run command** | `uv run pytest tests/test_admonitions.py tests/test_topics.py -x` |
| **Full suite command** | `uv run pytest -m "not slow"` (fast tier) / `uv run pytest` (full, includes real-compile fixtures) |
| **Estimated runtime** | ~5 s quick tier; full tier dominated by `typst.compile()` render gates |

**Worktree note (CLAUDE.md "Worktree-isolated execution" — standing mode):** every executor worktree
runs `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` against **its own**
`pyproject.toml`, then runs everything through `uv run`. Because this phase adds `pillow` to the
`[dev]` extra (D-07), the `pyproject.toml` edit must be committed in the same plan as — or in a wave
strictly before — any code that does `import PIL`. A parallel worktree branched before that edit
will `uv sync` successfully **without** pillow and fail at `import PIL` with no obvious cause.

---

## Sampling Rate

- **After every task commit:** `uv run pytest tests/test_admonitions.py tests/test_topics.py -x` (<5 s, no compile)
- **After every plan wave:** `uv run pytest -m "not slow"` plus the render gates this phase touches
  directly — `uv run pytest tests/test_pdf_render_gate.py tests/test_desc_rubric_decoupling_render_gate.py tests/test_rubric_*.py -x`
- **Before `/gsd-verify-work`:** full suite green (`uv run pytest`)
- **Phase gate (SC#5):** `uv run pytest tests/test_corpus_gate.py -m slow` must **actually run** green
  at least once before phase close. It skips gracefully offline — **a skip is not a pass.**
- **Max feedback latency:** ~5 s (quick tier)

---

## Per-Task Verification Map

*Seeded by plan-phase; task IDs are filled in by `/gsd-execute-phase` once PLAN.md tasks exist. The
requirement→command mapping below is fixed and comes from RESEARCH.md.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | ADM-01 | — | N/A | unit | `uv run pytest tests/test_admonitions.py -k seealso -x` | ✅ | ⬜ pending |
| TBD | TBD | TBD | ADM-01 | — | N/A | integration (compiled PDF) | `uv run pytest tests/test_pdf_render_gate.py -k <new fixture> -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | ADM-02 | — | N/A | unit | `uv run pytest tests/test_admonitions.py -k "attention or danger" -x` | ✅ | ⬜ pending |
| TBD | TBD | TBD | ADM-02 | — | N/A | integration (compiled PDF) | shares ADM-01's new fixture | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | ADM-03 | T-39-01 | Title routed through `escape_typst_string` | unit | `uv run pytest tests/test_admonitions.py -k generic_admonition -x` | ✅ | ⬜ pending |
| TBD | TBD | TBD | ADM-03 | — | N/A | integration (compiled PDF) | `uv run pytest tests/test_pdf_render_gate.py -k AdmonitionTitleRegression -x` | ✅ (add `.typ`-call assert) | ⬜ pending |
| TBD | TBD | TBD | ADM-04 | — | N/A | **manual-only** | see "Manual-Only Verifications" | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | ADM-05 | — | N/A | `pypdf` geometry (invariance guard, D-12) | `uv run pytest tests/test_rubric_indent_invariance.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | D-13 (classic RED) | — | N/A | `.typ` string, real `-b typst` | `uv run pytest tests/test_rubric_strong_nesting_render_gate.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | D-11 (wart) | T-39-02 | Exactly one separator newline | regex/count, real `-b typst` | `uv run pytest tests/test_desc_rubric_decoupling_render_gate.py -x` | Partial (fixture shape exists) | ⬜ pending |
| TBD | TBD | TBD | SC#5 | — | N/A | integration (network) | `uv run pytest tests/test_corpus_gate.py -m slow` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] New/extended real-compile fixture covering `seealso` / `attention` / `danger` — **no existing
      fixture contains any of these three types** (confirmed by repo-wide grep of `tests/fixtures/`)
- [ ] New `.typ`-call assertion on the existing `topic_line_block_render_gate`-backed test for
      ADM-03's `notify({` emission (the compiled-PDF title half already exists)
- [ ] New small local fixture (`py:class::` + nested `py:method::`, each carrying `.. rubric::`) with
      `pypdf` x-position assertions — ADM-05's invariance guard
- [ ] New fixture `.. rubric:: A **bold** rubric` + trailing paragraph — D-13's classic RED
- [ ] New newline-count assertion extending a propagated-target rubric fixture — D-11's wart
- [ ] Non-pytest render-and-desaturate script producing the ADM-04 greyscale artifact
- [ ] `pyproject.toml` `[dev]` extra edit adding `pillow` — gated behind `checkpoint:human-verify`
      per the Package Legitimacy Audit's `SUS` disposition
- [ ] `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` regeneration once D-11's wart is
      fixed — **expected in-scope churn, not a regression**; regenerate by hand-derivation, never by
      copying the fixed code's own output (D-14)
- [ ] Rename 4 now-misleading test functions in `test_admonitions.py`
      (`test_danger_converts_to_danger`, `test_attention_converts_to_warning`,
      `test_generic_admonition_converts_to_clue`, `test_seealso_converts_to_info_with_title`)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The four admonition buckets (note / success / warning / error) remain distinguishable **without hue** | ADM-04 (`[V]`) | The measured header-band luminances span only 5.4 percentage points; the claim under test is that the icon shapes and the 2pt accent stroke carry the distinction. No mechanical assertion can stand in for the owner's eye — REQUIREMENTS.md's own `[V]` legend marks it human-only. | 1. Build a probe containing one instance of each of the four bucket types. 2. `typst.compile(..., format="png", ppi=...)` to rasterise. 3. `Image.open(...).convert("L")` to desaturate (Pillow, BT.601 luma). 4. Commit the render into the phase directory. 5. Owner inspects and records the sign-off in the phase artifacts. **If the owner cannot distinguish them, the phase stops here** — D-08 pre-agrees no fallback lever; it is chosen against the actual render. |

**Caveat carried from RESEARCH.md Pitfall 5:** CONTEXT.md's D-06 luminance table uses BT.709
weights; Pillow's `convert("L")` uses BT.601. The sign-off must be made against the **real rendered
artifact**, not against the table's numbers.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] SC#5 corpus gate actually ran (not skipped) and was green
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
