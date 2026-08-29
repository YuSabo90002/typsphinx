---
phase: 60
slug: one-delimiter-aware-path-quoting-helper-routed-everywhere
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-29
---

# Phase 60 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> Seeded by plan-phase from `60-RESEARCH.md` § "Validation Architecture". This is a **product-side
> phase gated RED-first**: every requirement ships with a gate recorded failing against the unfixed
> tree before the fix lands (ROADMAP constraint 1). A green run that was never first recorded RED is
> evidence of nothing here. Per D-12 the RED shape differs by site — the doubled backslash
> everywhere the site is still on `!r`, but the **single-quote** case at the three 57-11 message
> builders, whose backslash half Phase 57 already made green.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (pinned `>=8.4,<10` in `pyproject.toml`; exact version via `uv.lock`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` (`:79-101`) — `testpaths = ["tests"]`, `addopts = "-v --strict-markers"`, `filterwarnings` promotes `DeprecationWarning`/`PendingDeprecationWarning` to `error` |
| **Quick run command** | `uv run pytest tests/test_pathfmt.py -x` (wave 1); each wiring plan's own new module (wave 2) |
| **Full suite command** | `uv run pytest` |
| **Estimated runtime** | quick ~2–5 s · full suite several minutes (PDF-compiling integration tests dominate; `-m "not slow"` trims it) |

**Worktree note (CLAUDE.md § "Worktree-isolated execution", STANDING):** every executor first runs
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` in its own worktree, then runs
**every** command via `uv run`. Without this, pytest imports the unchanged main-tree package and
gates stay RED after a correct fix.

**`filterwarnings` constraint (measured, `pyproject.toml:89-101`):** a new test module must not trip
a `DeprecationWarning`/`PendingDeprecationWarning`. `pathfmt.py`'s stdlib-only surface
(`os.fspath()`, string methods) carries no deprecation risk on Python 3.12.

---

## Sampling Rate

- **After every task commit:** the relevant module's own new test file (`uv run pytest tests/test_pathfmt.py` in wave 1; each wiring module's new test file in wave 2)
- **After every plan wave:** `uv run pytest` (full suite) plus `uv run black --check . && uv run ruff check . && uv run mypy typsphinx/`
- **Before `/gsd-verify-work`:** full suite green, and a local RED→green recorded for every success criterion
- **Phase gate:** local RED→green complete **before** the fresh 3-OS CI dispatch on the post-fix tip (ROADMAP constraint 10 — CI is never first discovery)
- **Max feedback latency:** ~5 s for the per-task quick run

---

## Per-Task Verification Map

Task IDs are provisional — the planner assigns the final ones. Test-module names beyond D-11's
placement rule are Claude's Discretion per CONTEXT.md; the names below are the research's proposals.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 60-01-xx | 01 | 1 | MSG-02 | — | N/A | unit | `uv run pytest tests/test_pathfmt.py -x` | ❌ W1 creates | ⬜ pending |
| 60-01-xx | 01 | 1 | MSG-02 (leaf-import proof, SC#1) | — | N/A | unit (import-graph) | `uv run python -c "import sys; import typsphinx.pathfmt; assert not any(m.startswith('typsphinx.') and m not in ('typsphinx','typsphinx.pathfmt') for m in sys.modules)"` | ❌ W1 creates | ⬜ pending |
| 60-02-xx | 02 | 2 | MSG-03 | — | N/A | unit | `uv run pytest tests/test_templates_path_collision_gate.py::TestWindowsPathEscapingRegressionGuard -x` | ✅ exists (new methods added by **this plan only**, D-11) | ⬜ pending |
| 60-03-xx | 03 | 2 | MSG-04 | — | N/A | unit (`caplog` @ DEBUG) | `uv run pytest tests/test_writer_path_quoting_gate.py -x` | ❌ W2 creates | ⬜ pending |
| 60-04-xx | 04 | 2 | MSG-05 | — | N/A | unit (`pytest.raises` + `str(excinfo.value)`) | `uv run pytest tests/test_template_registry_path_quoting_gate.py -x` | ❌ W2 creates | ⬜ pending |
| 60-05-xx | 05 | 3 | MSG-03 (SC#2 audit) | — | N/A | audit (repo-wide grep) | grep over `typsphinx/{builder,writer,template_registry}.py` — no path-valued `!r` remains | ✅ tooling exists | ⬜ pending |
| 60-05-xx | 05 | 3 | SC#3 (over-reach) | — | N/A | audit | `template_registry.py:410` measurably still `!r`; registry keys / docnames / config tuples still `!r`; existing `repr(["a","b"])` / `repr(b"base.typ")` assertions green **unmodified** | ✅ exists | ⬜ pending |
| 60-05-xx | 05 | 3 | SC#5 (zero test edits) | — | N/A | audit | measured diff over the phase range vs `58-REPR-CENSUS.md`, plus green `uv run pytest tests/test_repr_census_guard.py` | ✅ exists | ⬜ pending |
| 60-05-xx | 05 | 3 | SC#5 (3-OS matrix) | — | N/A | CI | fresh `windows-latest` / `ubuntu-latest` / `macos-latest` dispatch on the post-fix tip | ✅ `.github/workflows/ci.yml` | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No framework install, no new fixture, no new
`conftest.py` entry is needed — the `caplog` pattern (ten-plus modules today), the
`pytest.raises(ExtensionError)` + `str(excinfo.value)` pattern, and the `tests/_path_naming.py`
leaf-module precedent are all already established in this suite.

New **files** created by the phase's own waves (not Wave 0 prerequisites):

- [ ] `tests/test_pathfmt.py` — MSG-02's gate (wave 1, alongside `typsphinx/pathfmt.py`)
- [ ] `tests/test_writer_path_quoting_gate.py` — MSG-04's gate (wave 2, name at planner discretion)
- [ ] `tests/test_template_registry_path_quoting_gate.py` — MSG-05's gate (wave 2, name at planner discretion)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 3-OS CI matrix green on the post-fix tip | SC#5 | Requires a GitHub Actions dispatch; cannot run inside a worktree. ROADMAP constraint 10 forbids treating CI as first discovery, so this runs **after** local RED→green is complete. | Push the phase tip, dispatch `ci.yml` fresh, confirm `windows-latest`, `ubuntu-latest` and `macos-latest` lanes all green; record the run URL in the wave-3 evidence file. |

Every other phase behavior has automated verification. Note that **nothing in this phase requires a
Windows runner to go RED** — every gate is a pure string assertion or a `caplog` / `ExtensionError`
read against a hand-built Windows-shaped string literal, never gated on `os.name`.

---

## Evidence-File Naming Constraint (D-10)

Evidence is **per plan**, named `60-0N-EVIDENCE.md`. Wave 3 writes
`60-PATH-QUOTING-EVIDENCE.md` by *referencing* those files read-only, never by rewriting them.
**No file in this phase may be named `60-VERIFICATION.md`** — that name is reserved and overwritten
wholesale by `gsd-verifier` (59 D-11, 58 D-07).

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (none — existing infrastructure suffices)
- [ ] No watch-mode flags
- [ ] Feedback latency < 5 s for the per-task quick run
- [ ] Every success criterion has a recorded local RED **before** its green
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
