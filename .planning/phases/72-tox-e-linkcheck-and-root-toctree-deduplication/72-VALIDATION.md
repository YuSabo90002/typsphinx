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
| 72-01-T1 | 72-01 | 1 | DOC-18 / SC#3 base (positive control) | T-72-01, T-72-02 | a localised or incremental build cannot fake a count | build | clean `LANG=C LC_ALL=C uv run sphinx-build -b html` of a `git archive` of `PHASE_BASE_SHA`; `multiple toctrees` count at least 1; English `build succeeded` N recorded | ✅ | ⬜ pending |
| 72-01-T2 | 72-01 | 1 | DOC-18 / SC#4 base; SC#5 head reads | T-72-04 | read-only remote queries | build / gh | base `-b typst`: 5 dead root guards, 0 matching edges; base sidebar counts at least 2; `gh api …/required_status_checks` at head; main baseline run | ✅ | ⬜ pending |
| 72-01-T3 | 72-01 | 1 | DOC-18 edit | T-72-03 | the edit touches only the five entries | diff / build | `git diff --numstat` `0 5` on index.rst; one commit holding `M index.rst` and `R100` of the todo (D-08); post-edit clean build count 0 | ✅ | ⬜ pending |
| 72-02-T1 | 72-02 | 1 | QUA-13 / SC#1 | T-72-07, T-72-09 | linkcheck stays out of `env_list` | integration | base `tox.ini` is a byte prefix; configparser section check; `uv run tox list`; `rm -rf docs/_build/linkcheck && uv run tox -e linkcheck`, census of `output.json` | ✅ | ⬜ pending |
| 72-02-T2 | 72-02 | 1 | QUA-13 / SC#1 verdict (D-01..D-04) | T-72-05, T-72-06 | no ignore-style key; no pass from a failed run | integration | live recount of `docs/_build/linkcheck/output.json`, total == working at least 1; conf.py key rule | ✅ | ⬜ pending |
| 72-03-T1 | 72-03 | 2 | DOC-24 / SC#2 | T-72-10, T-72-11 | no surface names a missing environment | grep | `git grep -n 'tox -e docs-pdf' -- ':!.planning'` at least 1 hit; CLAUDE.md numstat 1/0 and column check | ✅ | ⬜ pending |
| 72-03-T2 | 72-03 | 2 | DOC-24 / SC#2 | T-72-12 | discovery by grep | grep | README/contributing numstat 1/0, column and last-in-block checks; one disposition per hit; post-edit linkcheck line count == surfaces | ✅ | ⬜ pending |
| 72-03-T3 | 72-03 | 2 | D-07 | — | N/A | diff | todo stays pending, base content a byte prefix, note names `[testenv:linkcheck]`, QUA-08 and the side PR | ✅ | ⬜ pending |
| 72-04-T1 | 72-04 | 3 | DOC-18 / SC#3 | T-72-13, T-72-14 | same-venv pair with positive control | build | base and tip built back to back in one venv; base count at least 1, tip 0, warning N equal | ✅ | ⬜ pending |
| 72-04-T2 | 72-04 | 3 | DOC-18 / SC#4 HTML and Typst | T-72-13 | counts from markup, not prose | build | scratch `html.parser` over tip `index.html` (5 × count 1 under the section index, control 1); tip `index.typ` has no root guard; one edge per page | ✅ | ⬜ pending |
| 72-04-T3 | 72-04 | 3 | DOC-18 / SC#4 divergence | T-72-15, T-72-16 | no fix beyond re-measurement | build | unpickled env: `collect_relations()` and `_get_toctree_ancestors()` parents vs Typst edge parents; `DIVERGENCE_SURVIVES` disposition | ✅ | ⬜ pending |
| 72-05-T1 | 72-05 | 3 | QUA-13 on tip; DOC-18 corroboration | T-72-17, T-72-18 | tox drops LC_ALL, so LANG=C is forced | integration | `uv run tox -e linkcheck` census; `LANG=C LANGUAGE=C LC_ALL=C uv run tox -e docs-html`: English summary, 0 `multiple toctrees`, N == base | ✅ | ⬜ pending |
| 72-05-T2 | 72-05 | 3 | SC#5 local | T-72-19 | scope fence | gates | `uv run ruff check .`, `black --check .`, `mypy typsphinx/`, `pytest -q -p no:cacheprovider`; changelog gate 0 skipped; `git diff --stat PHASE_BASE_SHA..HEAD -- typsphinx/ .github/workflows/` empty | ✅ | ⬜ pending |
| 72-06-T1 | 72-06 | 4 | SC#5 push | T-72-20, T-72-21, T-72-24 | no decoy, tag, force or release trigger | git / gh | census before the push; `git push --no-follow-tags -u origin gsd/v0.9.5-docs-link-check-and-navigation`; one `gh workflow run CI --ref …` | ✅ | ⬜ pending |
| 72-06-T2 | 72-06 | 4 | SC#5 CI | T-72-22, T-72-23 | the run is bound to `PUSHED_SHA` | CI | run completed and success; every job success; 4 windows/macos lanes named; job set == run 34748483361; required checks unchanged | ✅ | ⬜ pending |

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
