---
phase: 58
slug: repr-format-decoupling-test-side-only
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-27
---

# Phase 58 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> Seeded by plan-phase from `58-RESEARCH.md` § "Validation Architecture". This is a **test-side
> phase whose deliverable IS test code** — the validation question is not "what tests cover the
> feature" but "how do we prove the new/rewritten tests are themselves falsifiable, sound, and
> not tautological." SC#1–SC#3 are exactly that.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (`pyproject.toml:35` pins `>=8.4,<10`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` — `testpaths = ["tests"]`, `addopts = "-v --strict-markers"`, `filterwarnings` escalates `DeprecationWarning`/`PendingDeprecationWarning` to errors |
| **Quick run command** | `uv run pytest tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof tests/test_builder.py::test_post_process_images_rehome_escape_relocates_with_warning -q` |
| **Full suite command** | `uv run pytest` |
| **Estimated runtime** | quick ~15s · full suite ~3–5 min |

**Worktree note (CLAUDE.md § "Worktree-isolated execution", mandatory):** every command above runs
only after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` in the executor's own
worktree, and every command is prefixed `uv run`. `typst` is a **core** dependency
(`pyproject.toml:29`), so a correctly-provisioned worktree venv has `TYPST_AVAILABLE` true — a
`skipped` line on `test_out02_escape_target_gate.py` means the venv is wrong, **not** a pass.

---

## Sampling Rate

- **After every task commit:** Run `{quick run command}` plus any new predicate/guard test file the
  task touched.
- **After every plan wave:** Run `{full suite command}`. This phase adds shared test infrastructure
  (`tests/_path_naming.py` is importable from anywhere `tests/` is on `sys.path`), so a full-suite
  run at each wave boundary catches accidental collision with an unrelated test module.
- **Before `/gsd-verify-work`:** Full suite green, **and** `black --check .` + `ruff check .` clean
  (both scope the whole tree, so they cover the new `tests/` files). `mypy typsphinx/` is
  out of scope for this phase's changes and must be byte-identical to the pre-phase baseline.
- **Max feedback latency:** ~15 seconds (quick run).

---

## Per-Task Verification Map

Task IDs are assigned by the planner; the rows below are the requirement→verification contract each
task must map onto.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 58-01-T3 | 58-01 | 1 | MSG-01 | T-58-02 | `path_named_in` distinguishes "value named" from "value absent, same-basename sibling present" (D-01/D-03) | unit (meta-test) | `uv run pytest tests/test_path_naming_predicate.py -x` | ❌ W0 — new file | ⬜ pending |
| 58-01-T1 | 58-01 | 1 | MSG-01 | — | Escape-target-gate test passes pre- and post-rewrite against a real `sphinx-build` subprocess (D-02) | integration | `uv run pytest tests/test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof -q` | ✅ exists, rewritten in place | ⬜ pending |
| 58-01-T1 (pre) / 58-02-T1 (post) | 58-01, 58-02 | 1, 2 | MSG-01 | — | Image-rehome warning test passes pre- and post-rewrite against a real `builder.post_process_images()` call | integration | `uv run pytest tests/test_builder.py::test_post_process_images_rehome_escape_relocates_with_warning -q` | ✅ exists, rewritten in place | ⬜ pending |
| 58-01-T2 / 58-02-T2 | 58-01, 58-02 | 1, 2 | MSG-01 | T-58-01 | A real, recorded falsification (temporary `builder.py` edit dropping the path field) turns **both** rewritten tests RED (D-05b) | manual-only, recorded | Run the two commands above against the temporarily-edited `builder.py`; record RED verbatim in `58-DECOUPLING-EVIDENCE.md`; `git checkout typsphinx/builder.py`; record `git status --porcelain typsphinx/` empty | ❌ W0 — one-time recorded procedure, not a permanent test (by construction the falsifying edit must not survive) | ⬜ pending |
| 58-03-T1 | 58-03 | 3 | MSG-01 | T-58-02 | The `repr()`/`!r` pass-criterion set in `tests/` stays at exactly the recorded allowlist (D-08/D-09) | unit (static analysis) | `uv run pytest tests/test_repr_census_guard.py -x` | ❌ W0 — new file | ⬜ pending |
| 58-03-T3 | 58-03 | 3 | MSG-01 | T-58-01, T-58-06 | Phase gate green (full suite + `black --check .`), SC#4 proven at phase scope against the recorded base SHA, and the milestone branch on `origin` with a tracking upstream and no decoy sibling (D-10 / SC#5) | integration + CLI | `uv run pytest -q && uv run black --check . && git rev-parse --abbrev-ref 'gsd/v0.9.1-windows-path-correctness@{upstream}'` | ✅ suite exists; the push is a one-time recorded CLI action | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/_path_naming.py` — the shared format-agnostic naming predicate (D-04)
- [ ] `tests/test_path_naming_predicate.py` — permanent meta-tests, including the D-03 fallback-trap case (D-05a)
- [ ] `tests/test_repr_census_guard.py` — AST-based census guard (D-08/D-09); name kept as seeded (plan 58-03)
- [ ] `58-REPR-CENSUS.md` — the written, classified census table (D-08, SC#3) (plan 58-03)
- [ ] `58-DECOUPLING-EVIDENCE.md` — the recorded real-falsification procedure and its verbatim output (D-05b, D-06, D-07) (created by plan 58-01, appended by 58-02 and 58-03)
- [ ] `COVERAGE.md` — the reasoned, matrix-free external-API declaration the seal-time gate accepts (plan 58-01)
- [ ] No framework install needed — `pytest`, `ast`, `pathlib` are all already present.

**Planner resolution of RESEARCH.md Open Question 1** (one shared script vs. two independent ones):
one file. `tests/test_repr_census_guard.py` holds both the `ast` sweep (`_collect_pass_criterion_repr_sites()`)
and the recorded `PASS_CRITERION_REPR_ALLOWLIST`, and `58-REPR-CENSUS.md` transcribes that sweep's own
output. A separate `tests/_repr_census.py` would move the allowlist away from the sweep and make the
mandatory self-exclusion (D-09) span two files for no gain.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The recorded real falsification (D-05b) | MSG-01 / SC#2 | Cannot be a permanent automated test by construction — the falsifying edit to `typsphinx/builder.py` must be reverted and must not survive into any commit (SC#4). Automating it would require the phase to ship the very product change it forbids. | Temporarily drop the path field from `builder.py:697` and `builder.py:1767`; run each rewritten test; paste the RED output verbatim into `58-DECOUPLING-EVIDENCE.md`; `git checkout typsphinx/builder.py`; record `git status --porcelain typsphinx/` as empty in the same evidence file **before** the commit. A dirty `typsphinx/` at commit time is a halt, not a deviation. |
| Pre-rewrite green baseline (SC#2) | MSG-01 / SC#2 | Must be captured against the tree **before** the rewrite lands, so it cannot be re-derived by a later automated run. | Before editing either test, run the quick run command and paste the verbatim `passed` output (with the collected/skipped counts visible) into `58-DECOUPLING-EVIDENCE.md`. Confirm zero `skipped` — a skip is not a green. |
| Milestone branch on `origin` (SC#5 / D-10) | — | A remote-state side effect; not observable from the test suite. | `git push -u origin gsd/v0.9.1-windows-path-correctness`, then record `git branch -vv` showing the tracking entry. Do **not** create a `gsd/v0.9.1-milestone` decoy. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
