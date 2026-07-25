---
phase: 28
slug: v0-6-3-release-prep-regression-gate-close
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-25
---

# Phase 28 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `28-RESEARCH.md` §Validation Architecture (all values measured live in that session).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4+ (measured: pytest-9.1.1 running; `pyproject.toml` `dev` extras pin `pytest>=8.4,<10`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (`addopts = "-v --strict-markers"`; `slow` / `integration` markers registered) |
| **Quick run command** | `uv run python -m pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` |
| **Full suite command** | `uv run python -m pytest -q -rs` |
| **Estimated runtime** | quick ~sub-second · full ~57s (measured: `656 passed, 1 skipped in 56.64s`) |

---

## Sampling Rate

- **After every task commit:** Run `uv run python -m pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` (sub-second, no network, no real compile)
- **After every plan wave:** Run `uv run python -m pytest -q -rs` (full suite, ~57s)
- **Before `/gsd-verify-work`:** full suite green (`0 failed`), corpus gate reads `1 passed` (**not** `1 skipped`), and both docs builds within their own warning baselines
- **Max feedback latency:** ~57 seconds (full suite); ~13 seconds (corpus gate alone)

---

## Per-Task Verification Map

This phase carries **no requirement IDs** (release/close phase). The map below binds this phase's own
deliverables to their automated checks instead of to REQ-IDs. Threat Ref is `—` throughout: RESEARCH.md
§Security Domain found no attack-surface change (version-literal strings, CHANGELOG markdown, one README
line, a lockfile regeneration — no user input, no new network call, no auth/session/crypto surface).

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| version-sync | TBD | TBD | SC#1 | — | N/A | unit | `uv run python -m pytest tests/test_readme_version_sync.py -v` | ✅ existing (Phase 23) | ⬜ pending |
| lockfile-regen | TBD | TBD | SC#1 | — | N/A | other (CLI, not pytest) | `uv sync --extra dev --locked` | N/A — SC#1 acceptance is the exit code | ⬜ pending |
| corpus-gate | TBD | TBD | SC#3 | — | N/A | integration (slow, real `typst.compile()`) | `uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v -s` | ✅ existing | ⬜ pending |
| preview-sync | TBD | TBD | SC#4 | — | N/A | unit | `uv run python -m pytest tests/test_preview_version_sync.py -v` | ✅ existing | ⬜ pending |
| dep-invariant | TBD | TBD | SC#4 | — | N/A | other (`git diff`, not pytest) | `git diff main..HEAD -- pyproject.toml` (manual read) | N/A — no asserting test exists by design | ⬜ pending |
| base-typ-invariant | TBD | TBD | SC#4 | — | N/A | other (`git diff`, not pytest) | `git diff main..HEAD -- typsphinx/templates/base.typ` (expect exactly the 2 `lang` lines) | N/A — D-07 rules out a sha256 baseline | ⬜ pending |
| docs-baseline | TBD | TBD | SC#3 evidence (D-05/D-06) | — | N/A | other (tox, not pytest) | `uv run tox -e docs-pdf` and `uv run tox -e docs-multilang` (raw-log comparison) | N/A — D-06 deliberately declines a line-count assertion | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Task IDs are placeholders — the planner binds them to real `{phase}-{plan}-{task}` IDs. The rows are the
verification surface, and every row must be reachable from some plan's `<verify>` or acceptance criteria.*

---

## Wave 0 Requirements

**None.** Every test asset this phase relies on already exists and was confirmed green live during research:

- `tests/test_readme_version_sync.py` — exists (added Phase 23, D-13)
- `tests/test_preview_version_sync.py` — exists
- `tests/test_corpus_gate.py` — exists, `1 passed in 13.08s` with a cached `sphinx-v9.1.0` corpus

No new fixtures, no framework install. *Existing infrastructure covers all phase deliverables.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Zero new runtime deps across the milestone | SC#4 | No asserting test exists; adding one is test-infrastructure expansion, out of scope for release prep (D-07) | `git diff main..HEAD -- pyproject.toml` — expect empty; paste raw output into `28-VERIFICATION.md` |
| `base.typ` diff confined to the `lang` parameter and its wiring | SC#4 | D-07 explicitly declines a sha256 baseline (every deliberate future `base.typ` change would need it updated) | `git diff main..HEAD -- typsphinx/templates/base.typ` — expect exactly 2 changed lines; paste raw output |
| docs-build warnings have not increased from the phase-entry baseline | SC#3 evidence (D-05/D-06) | D-06 deliberately declines a line-count assertion test | Run both tox envs; compare warning lines against **per-environment** baselines — see caveat below; paste raw lines |

**Caveat carried from RESEARCH.md (finding not present in CONTEXT.md):** the "4 warning lines" figure in
CONTEXT.md D-06 applies only to `tox -e docs-multilang` (2 languages × 2 lines, both from the same
pre-existing `translator.py` `visit_toctree` docstring defect). `tox -e docs-pdf` is English-only and
structurally caps at 2 lines. The plan must write **two separate per-environment criteria**, not one
shared "4 lines" number.

**Second caveat:** the `1 skipped` in the full-suite baseline comes from `test_empty_url_before_after`
in `tests/test_corpus_gate.py`, gated behind `TYPSPHINX_CORPUS_REPORT=1`. It is **not** the SC#3 gate and
must not be conflated with it — the SC#3 gate itself reads `1 passed`.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references *(vacuous — no Wave 0 gaps)*
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
