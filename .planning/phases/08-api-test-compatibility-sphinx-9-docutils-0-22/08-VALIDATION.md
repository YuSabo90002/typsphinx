---
phase: 8
slug: api-test-compatibility-sphinx-9-docutils-0-22
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-11
---

# Phase 8 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `08-RESEARCH.md` → ## Validation Architecture (HIGH confidence, empirically verified against the resolved Sphinx 9.1.0 + docutils 0.22.4 stack).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (9.1.x) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (the `filterwarnings` guard from D-02 lands here) |
| **Quick run command** | `uv run pytest -q -m "not slow" -W "error::DeprecationWarning" -W "error::PendingDeprecationWarning"` |
| **Full suite command** | `uv run pytest` (402 tests; includes subprocess-based integration/example tests) |
| **Estimated runtime** | ~2 s (quick, 402 collected; no `-m slow` tests exist) / full suite dominated by subprocess integration tests |

> **Guard nuance (from research Open Question #1):** `RemovedInSphinx11Warning` subclasses `PendingDeprecationWarning`, NOT `DeprecationWarning`. The sampling commands escalate BOTH classes so the `builder.app`→`builder._app` deprecation is actually caught. The final `pyproject.toml` `filterwarnings` guard must decide (planner) whether to escalate both classes or only `DeprecationWarning` per the literal D-02 text.

---

## Sampling Rate

- **After every task commit:** `uv run pytest -q -m "not slow" -W "error::DeprecationWarning" -W "error::PendingDeprecationWarning" tests/<affected_file>.py` — fast, targeted at the specific fix site.
- **After every plan wave:** `uv run pytest -q -m "not slow"` plus `black --check . && mypy typsphinx/` (fallback `ruff check .` via `nix-shell -p ruff --run "ruff check ."` if the NixOS `uv`/`ruff` launch issue reproduces).
- **Before `/gsd-verify-work` (phase gate):** Full `uv run pytest` (all 402, incl. subprocess integration) green + `black --check .` + `ruff check .` + `mypy typsphinx/` all clean.
- **Max feedback latency:** ~2 s for the quick loop.

> **NixOS sandbox caveat (research Pitfall #3):** If the 45 subprocess-based tests fail with the exact `cannot start dynamically linked executable: uv` signature (`tox-uv`'s transitive `uv` wheel shadowing the system `uv`), that is a pre-existing environment issue — STATE.md records these 402 tests green as of Phase 7. The executor MUST confirm the failure signature is the NixOS launch error (not a Sphinx-9-shaped stack trace) before treating those 45 as non-blocking; never silently ignore.

---

## Per-Task Verification Map

> Task IDs (`8-NN-MM`) are assigned during planning; this seeds the requirement→test mapping the planner refines into per-task `<automated>` verify blocks.

| Task (seed) | Requirement | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|-------------|-----------------|-----------|-------------------|-------------|--------|
| API-01 findall swap | API-01 | N/A | unit + guard | `pytest tests/test_template_engine.py::TestToctreeOutlineIntegration -W error::DeprecationWarning -x` | ✅ existing | ⬜ pending |
| No `traverse()` warning suite-wide | API-01 | N/A | guard (whole-suite) | `pytest -q -W error::DeprecationWarning -W error::PendingDeprecationWarning` | ✅ existing | ⬜ pending |
| Builder/writer/config run clean on 9.1/0.22 | API-02 | N/A | integration | `python -m sphinx -b typst <fixture-src> <out>` under `-W error` | ✅ existing fixtures | ⬜ pending |
| Definition-list term/classifier unchanged | API-02 | N/A | unit | `pytest tests/test_translator.py -k definition_list` | ✅ existing | ⬜ pending |
| Full suite green w/ `filterwarnings` guard | API-02 | N/A | full suite | `uv run pytest` | ✅ existing + new `pyproject.toml` entries | ⬜ pending |
| Tree lint/type clean | API-02 | N/A | lint/type | `black --check .` · `ruff check .` · `mypy typsphinx/` | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers all phase requirements. The 402-test suite + `pyproject.toml` pytest config + `tox.ini` lint/type/docs envs already exercise every Phase 8 success criterion.
- The only new artifact is the `filterwarnings` ini-option addition to `pyproject.toml` — a config change, not a new test file.
- **Optional (only if the multi-`<term>` defensive hardening is adopted):** one new unit test in `tests/test_translator.py` that hand-constructs a multi-`<term>` `definition_list_item` doctree node (bypassing the rST parser, which cannot yet emit that shape) to exercise an append-not-overwrite path. Not required for SC2/SC3 — no current reST syntax triggers it.

---

## Manual-Only Verifications

*All phase behaviors have automated verification.* The deprecation guard, the findall swap, the definition-list handling, and the lint/type gates are all machine-checkable. The only human judgment required is confirming the NixOS subprocess-launch failure signature (above) is environmental, not a real Sphinx-9 regression.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (N/A — none)
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
