---
phase: 7
slug: bump-preview-packages-typst-0-15-kai-fix
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-11
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing suite, ~400 tests) + tox-driven Typst compile (`sphinx-build -b typstpdf`) |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`), `tox.ini` (`[testenv:docs-pdf]`) |
| **Quick run command** | `pytest tests/test_preview_version_sync.py -x` |
| **Full suite command** | `tox -e docs-pdf` (real end-to-end compile — the phase's hard gate) |
| **Estimated runtime** | ~2s (quick) / ~30–90s (docs-pdf compile) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_preview_version_sync.py -x` (catches a partial/mistyped version bump across the 3 sync sites immediately)
- **After every plan wave:** Run `tox -e docs-pdf` (the real compile — the actual hard gate)
- **Before `/gsd-verify-work`:** `tox -e docs-pdf` green + the output PDF opened for the D-01/D-04 coarse visual glance
- **Max feedback latency:** ~90 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 7-01-01 | 01 | 1 | FWD-02 | T-7-V14 | typst pin `>=0.15.0,<0.16`, `uv.lock` regenerated & committed (reproducible resolve) | integration | `uv lock` resolves; `tox -e docs-pdf` | ✅ | ⬜ pending |
| 7-01-02 | 01 | 1 | PKG-01, PKG-02, PKG-03 | T-7-typo | 4 `@preview` versions bumped in lockstep across all 3 sync sites | unit/static | `pytest tests/test_preview_version_sync.py -x` | ✅ | ⬜ pending |
| 7-01-03 | 01 | 1 | FWD-02, PKG-01, PKG-02 | — | `docs-pdf` compiles with zero `unknown variable: kai` / any `TypstError`; coarse "no tofu / no broken boxes" PDF glance | integration/compile | `tox -e docs-pdf` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*(Task IDs are indicative — the planner owns final task decomposition; this map exists so every requirement has an automated verify with no 3-consecutive-task sampling gap.)*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements.* No new test files, fixtures, or framework installation are needed — `tests/test_preview_version_sync.py` (3-way sync guard) and `tox -e docs-pdf` (real compile) fully cover FWD-02, PKG-01, PKG-02, and PKG-03.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Coarse visual sanity of the compiled PDF | FWD-02, PKG-01, PKG-02 | Per CONTEXT.md D-01/D-03/D-04: deliberately lightweight forward-port — no golden-PDF/visual-baseline infra is built or wanted | Open `docs/_build/pdf/*.pdf` after a green `tox -e docs-pdf`. Pass = no blank/broken boxes, no missing-glyph tofu (⬛), no error glyphs. Do NOT do element-by-element auditing or before/after diffing (explicitly rejected). |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (none — existing infra suffices)
- [ ] No watch-mode flags
- [ ] Feedback latency < 90s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
