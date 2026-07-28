---
phase: 34
slug: inline-math-after-text-separator-fix
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-28
---

# Phase 34 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (verified in 34-RESEARCH.md "Validation Architecture") |
| **Config file** | `pyproject.toml` — `[tool.pytest.ini_options]`, `testpaths = ["tests"]` |
| **Quick run command** | `uv run pytest tests/test_inline_math_after_text_render_gate.py tests/test_math_mitex.py tests/test_math_native.py tests/test_math_fallback.py -q` |
| **Full suite command** | `uv run pytest -q --tb=no -rf` |
| **Estimated runtime** | ~5 s for the quick set (3 math modules measured at 0.04 s; the render gate spawns 2 `sphinx-build` + `typst.compile()` subprocesses); the full suite is multi-minute (many subprocess-spawning render gates) |

**Environment prerequisite (MANDATORY):** worktree-isolated execution is this repo's standing mode.
Every command above must be preceded by `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`
when `.git` is a FILE, and run through `uv run`. Sphinx is always invoked as
`sys.executable -m sphinx` — never a compiled console script (NixOS sandbox hazard).

---

## Sampling Rate

- **After every task commit:** Run the quick run command above.
- **After every plan wave:** Run the full suite command above.
- **Before `/gsd-verify-work`:** Post-fix failing node-ID set must be a subset of Plan 01's recorded
  pre-fix baseline (the suite is NOT expected to be all-green in this sandbox — see Manual-Only
  Verifications), plus `black --check .` / `ruff check .` / `mypy typsphinx/` clean and the
  full-corpus `-b typstpdf` gate result recorded honestly.
- **Max feedback latency:** ~5 s (quick set), multi-minute (full suite / corpus gate).

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 34-01-01 | 01 | 1 | MATH-01 | T-34-02 | Fixture drives the `-b typstpdf` compile path where the DoS-class fatal is observable | fixture creation | `test -f tests/fixtures/inline_math_after_text_render_gate/conf.py && grep -c ':math:' tests/fixtures/inline_math_after_text_render_gate/index.rst` | ❌ W0 (created here) | ⬜ pending |
| 34-01-02 | 01 | 1 | MATH-01 | T-34-02 | Gate asserts absence of the compile-abort signatures on both emission paths | real-compile gate | `uv run pytest tests/test_inline_math_after_text_render_gate.py --collect-only -q` | ❌ W0 (created here) | ⬜ pending |
| 34-01-03 | 01 | 1 | MATH-01 | T-34-02 | Fail-pre-fix proof recorded verbatim (SC#4) | RED evidence | `! uv run pytest tests/test_inline_math_after_text_render_gate.py -q` | ❌ W0 (created here) | ⬜ pending |
| 34-02-01 | 02 | 2 | MATH-01 | T-34-01 / T-34-04 | Separator inserted outside the math call; payload construction byte-unchanged | unit + source assertion | `uv run pytest tests/test_math_mitex.py tests/test_math_native.py tests/test_math_fallback.py -q` | ✅ | ⬜ pending |
| 34-02-02 | 02 | 2 | MATH-01 | T-34-01 / T-34-04 | Block math list-item separator; no concat operator around a block expression | unit + source assertion | `uv run pytest tests/test_math_mitex.py tests/test_math_native.py tests/test_math_fallback.py tests/test_integration_advanced.py -q` | ✅ | ⬜ pending |
| 34-02-03 | 02 | 2 | MATH-01 | T-34-02 | Gate GREEN on mitex and native builds; SHA-anchored RED→GREEN verdict | real-compile gate | `uv run pytest tests/test_inline_math_after_text_render_gate.py tests/test_math_mitex.py tests/test_math_native.py tests/test_math_fallback.py -q` | ✅ (after 34-01) | ⬜ pending |
| 34-03-01 | 03 | 3 | MATH-01 | T-34-06 / T-34-SC | Regression masking prevented by mechanical baseline set-difference; invariants asserted over the diff | full suite + lint + type | `uv run black --check . && uv run ruff check . && uv run mypy typsphinx/ && uv run pytest tests/test_preview_version_sync.py -q` | ✅ | ⬜ pending |
| 34-03-02 | 03 | 3 | MATH-01 | T-34-02 / T-34-05 | Corpus gate verdict constrained to PASSED/SKIPPED/FAILED; no skip reported as pass | slow / integration | `uv run pytest tests/test_corpus_gate.py -q -m slow` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/fixtures/inline_math_after_text_render_gate/conf.py` + `index.rst` — the GATE-01 fixture
      project (Plan 01 Task 1). Covers MATH-01 SC#1-SC#3.
- [ ] `tests/test_inline_math_after_text_render_gate.py` — the real-compile gate module driving both
      the mitex default and the `-D typst_use_mitex=0` native path (Plan 01 Task 2). Covers MATH-01
      SC#1-SC#4.
- [ ] `.planning/phases/34-inline-math-after-text-separator-fix/34-GATE-EVIDENCE.md` — the RED
      evidence artifact plus the pre-fix full-suite baseline (Plan 01 Task 3). Required by SC#4 and
      by Plan 03's regression comparison.

*No framework install is required: pytest, typst-py 0.15.0 and pypdf 6.14.2 are already installed
dev dependencies (34-RESEARCH.md "Environment Availability").*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual layout of prose + inline math on one continuous line, the centred display equation between its two list-item paragraphs, and the confval field body reading as one continuous sentence | MATH-01 (SC#3, beyond text extraction) | `pypdf` text extraction proves content presence and absence of Typst-source leakage, but not glyph placement, line breaking, or overlap | Plan 03 Task 2 `<human-check>`: open the docs PDF and the fixture PDF and confirm (a) list-item prose/equation/prose on one line with normal spacing and no visible `mi(` on the page, (b) the display equation centred between its paragraphs, (c) the confval `:default:` field body continuous. Reply "approved" or describe the defect. |
| Classification of a residual full-suite failure as NixOS-environmental | MATH-01 (SC#5) | The sandbox has ~45 environmentally-failing integration tests unrelated to code correctness | Automated by construction: Plan 01 records the pre-fix failing node-ID set BEFORE any source change and Plan 03 asserts the post-fix set is a subset. Only a NEW failure requires human judgement, and a non-empty NEW set stops the plan for escalation. |

`workflow.human_verify_mode` is `end-of-phase`, so the visual check is expressed as a
`<verify><human-check>` on the phase's final task rather than a blocking `checkpoint:human-verify`.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s for the per-commit quick set
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
