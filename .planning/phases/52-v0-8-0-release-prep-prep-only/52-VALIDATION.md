---
phase: 52
slug: v0-8-0-release-prep-prep-only
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-15
---

# Phase 52 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded by `/gsd-plan-phase` from `52-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml` `[tool.pytest.ini_options]`), `tox` (with `tox-uv-bare`) as task runner |
| **Config file** | `pyproject.toml`, `tox.ini` |
| **Quick run command** | `uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` |
| **Full suite command** | `uv run pytest tests/ -v` (local spot-check) — the **matrix / lint / type authority is the dispatched CI run** per CONTEXT D-08, not the local suite |
| **Estimated runtime** | quick ~10s; full local suite ~3–5 min; `tox -e docs-pdf` and `test_corpus_gate.py` are the slow tails |

**Worktree note (CLAUDE.md, mandatory):** every executor runs
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` first, then invokes **all** commands
through `uv run`. Without this, pytest imports the unchanged main-tree package and gates stay RED after a
correct fix.

---

## Sampling Rate

- **After every task commit:** the relevant guard-test subset — the version-sync trio for the bump task,
  `tests/test_changelog_page_gate.py` for the CHANGELOG task, the extended `TestThreeMasterGate` for the
  D-10 gate task.
- **After every plan wave:** `uv run pytest tests/ -v` locally as a spot-check. Never presented as
  authority for lint/type/matrix — that is the dispatched CI run (D-08; `ruff` cannot execute on this
  machine, `todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`).
- **Before `/gsd-verify-work`:** dispatched CI run all-green, both `tox -e docs-html` / `tox -e docs-pdf`
  green, and `tests/test_corpus_gate.py` recorded as **PASSED or honestly SKIPPED** — the two must never
  be conflated (`test_corpus_gate.py` `pytest.skip`s rather than fails when the corpus is unavailable, so
  a skip is *not* evidence).
- **Max feedback latency:** ~10s for the per-task guard subset.

---

## Phase Requirements → Test Map

| Req ID | Success criterion | Behavior | Test Type | Automated Command | File Exists |
|--------|-------------------|----------|-----------|-------------------|-------------|
| REL-07 | SC#1 | Version literals move in lockstep; `typsphinx.__version__` reports `0.8.0` | unit | `uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` | ✅ |
| REL-07 | SC#2 | Curated `## [0.8.0]` CHANGELOG entry, extractable, page gate current | integration | `uv run python scripts/extract_changelog_section.py 0.8.0` + `uv run --extra dev --extra docs pytest tests/test_changelog_page_gate.py -v` | ✅ |
| REL-07 | SC#3 (toolchain half) | Post-bump tree green: pytest / lint / type / docs builds / full-corpus gate | integration + e2e | dispatched `ci.yml` run + `tox -e docs-html` + `tox -e docs-pdf` + `uv run pytest tests/test_corpus_gate.py -v` | ✅ (CI workflow + local envs) |
| REL-07 | SC#3 (goal-claim half) | Multi-master round trip proven on generated PDF evidence (≥2 masters, ≥1 shared child, `pypdf` text/page assertions) | e2e / gate | `uv run pytest tests/test_state_guard_shapes_gate.py::TestThreeMasterGate -v` — **extended** per CONTEXT D-10 / RESEARCH Pattern 3 | ⚠️ module exists, PDF-level assertions to be added |
| REL-07 | SC#4 | Milestone invariants asserted mechanically over `v0.7.1..HEAD` with a **real** positive control | script + unit | the `git diff` / `grep` command set in RESEARCH Pattern 5 + `uv run pytest tests/test_preview_version_sync.py -v` | ⚠️ commands exist; the positive control is new authored work (RESEARCH A3 — no prior precedent) |
| REL-07 | SC#5 | No irreversible action taken; standalone handoff exists | manual + script | `git tag -l v0.8.0` and `git ls-remote --tags origin v0.8.0` both empty, asserted at phase head **and** phase close | ✅ |

---

## Per-Task Verification Map

*Filled by `/gsd-validate-phase` once PLAN.md task IDs exist. Seeded rows below carry the plan-level
mapping the planner must preserve.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | bump | 1 | REL-07 (SC#1) | — | N/A | unit | version-sync trio (above) | ✅ | ⬜ pending |
| TBD | changelog | 1 | REL-07 (SC#2) | T-52-01 | `extract_changelog_section.py`'s `version` arg stays a string-equality comparison, never interpolated | integration | extract + page gate (above) | ✅ | ⬜ pending |
| TBD | gate test | 1 | REL-07 (SC#3 goal half) | — | N/A | e2e | extended `TestThreeMasterGate` | ⚠️ | ⬜ pending |
| TBD | invariants | 2 | REL-07 (SC#4) | T-52-03 | positive control must fail if the sweep is vacuous | script | RESEARCH Pattern 5 command set | ⚠️ | ⬜ pending |
| TBD | green tree / CI | 2 | REL-07 (SC#3 toolchain half) | T-52-03 | no gate weakened to force green; `git diff` confined to intended lines | integration | CI dispatch + docs builds + corpus gate | ✅ | ⬜ pending |
| TBD | handoff | 3 | REL-07 (SC#5) | T-52-02 | REL-07 checkbox must **not** flip in this phase | manual | tag-absence assertions | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

**None.** Every test module and fixture this phase needs already exists in the repository
(`tests/test_extension.py`, `tests/test_readme_version_sync.py`, `tests/test_preview_version_sync.py`,
`tests/test_changelog_page_gate.py`, `tests/test_corpus_gate.py`, `tests/test_state_guard_shapes_gate.py`,
`tests/fixtures/state_guard_three_master_gate/`). The only new test content is additive assertions inside
— or a sibling to — an existing, already-passing test class.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The `## [0.8.0]` entry's *editorial content* — that its 8–9 bullets actually cover every v1 requirement the milestone delivered, with D-04's `**Breaking:**` marking and D-05's lead axis | REL-07 (SC#2) | Coverage of prose against a requirement set is a judgement, not an assertion; the page gate only proves the heading renders | Read `CHANGELOG.md` `## [0.8.0]` against `REQUIREMENTS.md`'s v1 rows and `docs/source/changelog.rst`'s "Migrating from 0.7.x to 0.8.0" section; confirm agreement and that `:numref:` appears nowhere |
| Dispatched CI run's per-lane conclusions (Windows / macOS lanes especially) | REL-07 (SC#3) | The run happens on GitHub; the evidence is the recorded run ID + per-lane conclusion | `gh run view <id>` — transcribe run ID, conclusion, and each lane verbatim into the CI evidence artifact |
| That **no irreversible action** was taken | REL-07 (SC#5) | Absence-proof over the whole phase, not a single command's exit code | `git tag -l v0.8.0` and `git ls-remote --tags origin v0.8.0` at phase head and phase close; no PR opened; no `release.yml` triggered |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references *(none — see above)*
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s for the per-task guard subset
- [ ] `test_corpus_gate.py` result recorded as PASSED or SKIPPED, never conflated
- [ ] No evidence artifact named `52-VERIFICATION.md` (reserved by the verifier — 46-CONTEXT D-15)
- [ ] REL-07 left **open**; not reported complete on the strength of the prep being correct
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
