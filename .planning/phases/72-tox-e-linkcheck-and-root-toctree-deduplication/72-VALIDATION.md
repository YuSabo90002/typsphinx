---
phase: "72"
slug: "tox-e-linkcheck-and-root-toctree-deduplication"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-13"
---

# Phase 72 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `72-RESEARCH.md` § Validation Architecture. This phase's proof surface is direct
> Sphinx/tox invocation with verbatim transcript evidence (no new committed script, no new test);
> pytest is the regression guard only.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing suite, regression only) + direct `sphinx-build` / `tox` runs with verbatim transcripts |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (unedited); `tox.ini` (gains `[testenv:linkcheck]`) |
| **Quick run command** | the task's own proof command (see map below) |
| **Full suite command** | `uv run pytest -q -p no:cacheprovider` (in the provisioned worktree venv) |
| **Estimated runtime** | linkcheck ~10 s; clean HTML build ~30–60 s; full pytest a few minutes |

---

## Sampling Rate

- **After every task commit:** re-run that task's proof command (e.g. after the `index.rst` edit, the SC#3 clean-HTML `LC_ALL=C` grep; after the `tox.ini` edit, `tox -e linkcheck` once from a clean `docs/_build/linkcheck`)
- **After every plan wave:** full pytest suite (regression only) + `black --check .`, `ruff check .`, `mypy typsphinx/`
- **Before `/gsd-verify-work`:** SC#5 local-gate quartet green and the dispatched CI run completed green
- **Max feedback latency:** ~60 seconds for per-task proofs

---

## Per-Task Verification Map

Task IDs are filled in by the plans; rows are keyed by requirement / success criterion.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 72-TBD | TBD | TBD | QUA-13 / SC#1 | — | N/A | integration | `rm -rf docs/_build/linkcheck && uv run tox -e linkcheck`, then stdlib census of `docs/_build/linkcheck/output.json` (total == working) | ✅ | ⬜ pending |
| 72-TBD | TBD | TBD | DOC-24 / SC#2 | — | N/A | grep | `git grep -n 'tox -e docs-pdf' -- ':!.planning'` re-run; each listing block carries a `tox -e linkcheck` line | ✅ | ⬜ pending |
| 72-TBD | TBD | TBD | DOC-18 / SC#3 | — | N/A | build | clean `LC_ALL=C sphinx-build -b html` at base and tip; `multiple toctrees` count base > 0, tip == 0; `build succeeded, N warnings.` N equal | ✅ | ⬜ pending |
| 72-TBD | TBD | TBD | DOC-18 / SC#4 | — | N/A | build | sidebar-scoped `html.parser` count over tip `index.html` (5 targets == 1, output_layout control == 1); clean `-b typst` base vs tip `include()` / include-edges comparison | ✅ | ⬜ pending |
| 72-TBD | TBD | TBD | SC#5 | — | N/A | gates / CI | `ruff check .`, `black --check .`, `mypy typsphinx/`, `uv run pytest`; scoped `git diff --stat`; `gh api …/required_status_checks`; dispatched CI job census | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The rendered HTML sidebar shows each User Guide / Examples page once, nested under its section | DOC-18 | SC#4 names the owner's visual look at UAT as the human check the 2026-08-16 todo asks for | Open the tip build's `index.html` and inspect the furo sidebar |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
