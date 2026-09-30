---
phase: "65"
slug: "tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-12"
---

# Phase 65 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> Seeded by plan-phase from `65-RESEARCH.md` § "Validation Architecture". This phase changes no
> `typsphinx/` behaviour and adds no test file. It edits `pyproject.toml:38`, `tox.ini`'s `requires`
> value, `uv.lock`, and — per D-06's AMENDED block — inverts one existing static gate in
> `tests/test_toolchain_config_gate.py`, all in one commit. Per Phase 64 D-05, TOX-03's proofs are
> recorded verbatim in evidence markdown, gated by commands that re-check the decisive lines.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (`pyproject.toml` `[tool.pytest.ini_options]`), run through `tox` (`uv-venv-lock-runner`); `gh` for the TOX-04 dispatch |
| **Config file** | `pyproject.toml`, `tox.ini` |
| **Quick run command** | `tox --showconfig -e py312` (exercises the `requires` ini-list parse; ~0.2 s — `tox --version` does NOT, see RESEARCH Pitfall 1) and `pytest tests/test_toolchain_config_gate.py -q` (~2 s) |
| **Full suite command** | `tox -vv -e py312 -r` through the shim in the executor worktree (the D-02 observation run doubles as the full suite): 1548 collected |
| **Estimated runtime** | quick ~2 s · full suite ~110 s cold · one CI dispatch ~7 min wall clock |

---

## Sampling Rate

- **After every task commit:** Run `tox --showconfig -e py312` and `pytest tests/test_toolchain_config_gate.py -q`
- **After every plan wave:** Run `tox -vv -e py312 -r` (full suite)
- **Before `/gsd-verify-work`:** Full suite must be green and TOX-04's CI run completed with every job transcribed
- **Max feedback latency:** 120 seconds (the one-off CI dispatch is outside the per-task loop)

---

## Per-Task Verification Map

*Filled from the PLAN.md tasks at plan time (2026-09-12). The full commands live in each task's `<automated>` block; this table names what each one checks.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 65-01-T1 | 65-01 | 1 | TOX-01, TOX-02 | T-65-SC, T-65-01, T-65-03, T-65-04 | lock sha256-pinned and accepted by `--locked`; `TOX_UV_PATH` unset and in no tracked file; scratch comma-form control never committed | integration (shell) + unit (inverted gate, RED then GREEN) | `REVERT_SHA` lists exactly the four files; `uv sync --extra dev --locked`; `uv lock --check`; `uv run pytest tests/test_toolchain_config_gate.py -q` reads `4 passed`; `tox config -e py312 --core -k requires` lists `  tox-uv~=1.35` | ✅ (existing test, inverted) | ⬜ |
| 65-01-T2 | 65-01 | 1 | TOX-03 | T-65-01, T-65-02, T-65-04 | uv observed from tox's own `-vv` log, never from a shell probe | integration (shell, evidence-recorded) | live `tox -vv -e py312 -r --notest` logs `using bundled uv from: <worktree>/.venv/bin/uv` and only `DEBUG uv <uv.lock version>`; the evidence D-02 section holds `py312: OK`, `collected 1548 items` and `1543 passed, 5 skipped`; `pytest --collect-only -q` reads `1548 tests collected` | ✅ (no new file) | ⬜ |
| 65-01-T3 | 65-01 | 1 | TOX-03 | T-65-03 | control venv outside the tree, lock-pinned, run outside FHS | integration (shell, evidence-recorded) | nix-interpreter provenance; four `uv pip list` pins equal to `uv.lock`; the live control logs bundled `<CTRL>/bin/uv`, and its first `exit N (` line is `exit 127` on `uv venv`; closure rows TOX-01..TOX-03 MET | ✅ (no new file) | ⬜ |
| 65-02-T1 | 65-02 | 2 | TOX-04 | T-65-05, T-65-06, T-65-08 | fast-forward push of the canonical ref only; no tag; push gated on wave 1's MET closure | CI (external) + git | upstream set; origin head = `PUSHED_SHA`; no decoy on origin; four-file fence on the tip; `RUN_ID` headSha = `PUSHED_SHA`, event `workflow_dispatch` | ✅ (no new file) | ⬜ |
| 65-02-T2 | 65-02 | 2 | TOX-04 | T-65-06, T-65-07, T-65-09 | one dispatch; no `release.yml` run; CI is the authority | CI (external) | run `completed`/`success`; 12 jobs all `success`; 2 windows-latest + 2 macos-latest lanes; `Lint and Format Check` success; one dispatched run at `PUSHED_SHA`; `## uv resolved on CI` with at least 7 `venv>` lines; TOX-04 closure MET | ✅ (existing `ci.yml`, unedited) | ⬜ |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No new test file or fixture; the one
test-side change is the D-06 AMENDED inversion of an existing gate, which lands in the revert commit.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Windows / macOS `uv` resolution under tox-uv's bundled branch | TOX-04 | No Windows/macOS host locally (RESEARCH A1/A2); only CI reaches those lanes | Read the completed dispatched run's job census via `gh run view <id> --json jobs`; transcribe every job's conclusion |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
