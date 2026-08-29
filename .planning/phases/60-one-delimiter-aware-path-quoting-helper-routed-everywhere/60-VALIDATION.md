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

Task IDs below are the FINAL ones assigned at plan time (`{plan}-T{task}`). Test-module names beyond
D-11's placement rule were Claude's Discretion per CONTEXT.md; the names below are the ones the plans
actually create.

**Correction to `60-RESEARCH.md`'s proposed leaf-import proof (measured at plan time):**
`typsphinx/__init__.py` imports `typsphinx.builder` at module scope, so
`import typsphinx.pathfmt` + a `sys.modules` scan FAILS even for a perfect leaf module and would
prove the opposite of SC#1. The proof is therefore (a) an AST read of `pathfmt.py`'s import block and
(b) a fresh-interpreter load BY FILE PATH via `importlib.util.spec_from_file_location`, both inside
`tests/test_pathfmt.py::TestPathfmtLeafModule`.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 60-01-T1 | 01 | 1 | MSG-02 (RED) | T-60-01/02 | explicit `TypeError` at the helper's type boundary; delimiter selection prevents a path closing its own quote | unit | `! uv run pytest tests/test_pathfmt.py -x` (must FAIL — module absent) | ❌ W1 creates | ⬜ pending |
| 60-01-T2 | 01 | 1 | MSG-02 (GREEN) | T-60-01/02 | same | unit | `uv run pytest tests/test_pathfmt.py -q` | ❌ W1 creates | ⬜ pending |
| 60-01-T3 | 01 | 1 | MSG-02 (leaf-import proof, SC#1) | — | N/A | unit (import-graph, AST + fresh-interpreter path load) | `uv run pytest tests/test_pathfmt.py -q -k leaf` and `grep -nE '^(import\|from) ' typsphinx/pathfmt.py` | ❌ W1 creates | ⬜ pending |
| 60-02-T1 | 02 | 2 | MSG-03 (RED, 5 families + 3 single-quote methods) | T-60-04/05 | non-`str` target keeps warning rather than crashing; paths quoted unambiguously | unit | `! uv run pytest tests/test_builder_path_quoting_gate.py -q` and `! uv run pytest tests/test_templates_path_collision_gate.py -q -k disambiguates_embedded_single_quote` | ❌ W2 creates (new module) · ✅ exists (methods ADDED by **this plan only**, D-11) | ⬜ pending |
| 60-02-T2 | 02 | 2 | MSG-03 (GREEN) | T-60-04/05/06 | same | unit | `uv run pytest tests/test_builder_path_quoting_gate.py tests/test_templates_path_collision_gate.py -q` | ❌/✅ | ⬜ pending |
| 60-03-T1 | 03 | 2 | MSG-04 (RED + `None` pin) | T-60-07/08 | `quote_path(None)` keeps the package-alone build path alive | unit (`caplog` @ DEBUG) | `! uv run pytest tests/test_writer_path_quoting_gate.py -q` and `uv run pytest tests/test_writer_path_quoting_gate.py -q -k template_file_none` | ❌ W2 creates | ⬜ pending |
| 60-03-T2 | 03 | 2 | MSG-04 (GREEN + two-tree `None` byte-identity) | T-60-07 | same | unit (`caplog` @ DEBUG) | `uv run pytest tests/test_writer_path_quoting_gate.py -q` | ❌ W2 creates | ⬜ pending |
| 60-04-T1 | 04 | 2 | MSG-05 (RED shapes 1 and 2 + exclusion control) | T-60-10/11 | excluded type-check branch keeps reporting `list`/`bytes` values instead of raising | unit (`pytest.raises` + `str(excinfo.value)`) | `! uv run pytest tests/test_template_registry_path_quoting_gate.py -q` and `uv run pytest tests/test_template_registry_path_quoting_gate.py -q -k type_check_message_stays_repr_quoted` | ❌ W2 creates | ⬜ pending |
| 60-04-T2 | 04 | 2 | MSG-05 (GREEN + two-tree exclusion pin) | T-60-10/11/12 | same | unit | `uv run pytest tests/test_template_registry_path_quoting_gate.py tests/test_template_registry.py -q` | ❌/✅ | ⬜ pending |
| 60-05-T1 | 05 | 3 | SC#2 (repo-wide discovery grep) + SC#3 (over-reach) | T-60-16 | scope widening is filed as a new requirement, never fixed in-phase | audit (repo-wide grep) | `grep -rn` over the WHOLE `typsphinx/` package (four forms), then the routed-value negative grep prints nothing | ✅ tooling exists | ⬜ pending |
| 60-05-T2 | 05 | 3 | SC#5 (zero test edits) + final local gate | T-60-13/14 | no skipped gate recorded as a pass | audit | `git diff --name-status $PHASE_BASE_SHA..HEAD -- tests/` (only `A` plus one pure-addition `M`), plus green `uv run pytest tests/test_repr_census_guard.py -q` | ✅ exists | ⬜ pending |
| 60-05-T3 | 05 | 3 | SC#5 (consolidation + 3-OS matrix) | T-60-13/15 | per-plan evidence files are read-only to the consolidation | CI + audit | fresh `gh workflow run ci.yml --ref <branch>` dispatch on the post-fix tip; `windows-latest` / `ubuntu-latest` / `macos-latest` all green | ✅ `.github/workflows/ci.yml` | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No framework install, no new fixture, no new
`conftest.py` entry is needed — the `caplog` pattern (ten-plus modules today), the
`pytest.raises(ExtensionError)` + `str(excinfo.value)` pattern, and the `tests/_path_naming.py`
leaf-module precedent are all already established in this suite.

New **files** created by the phase's own waves (not Wave 0 prerequisites):

- [ ] `tests/test_pathfmt.py` — MSG-02's gate (wave 1, plan 01, alongside `typsphinx/pathfmt.py`)
- [ ] `tests/test_builder_path_quoting_gate.py` — MSG-03's gate for the INLINE (non-extracted) message
      sites in `builder.py` (wave 2, plan 02). The three 57-11 extracted builders are gated instead by
      three methods ADDED to `TestWindowsPathEscapingRegressionGuard` in the existing
      `tests/test_templates_path_collision_gate.py` — plan 02's exclusive privilege (D-11)
- [ ] `tests/test_writer_path_quoting_gate.py` — MSG-04's gate (wave 2, plan 03)
- [ ] `tests/test_template_registry_path_quoting_gate.py` — MSG-05's gate (wave 2, plan 04)

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
