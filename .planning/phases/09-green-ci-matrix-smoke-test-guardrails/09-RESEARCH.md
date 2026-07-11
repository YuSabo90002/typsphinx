# Phase 9: Green CI Matrix + Smoke Test + Guardrails - Research

**Researched:** 2026-07-11
**Domain:** GitHub Actions CI/CD (workflow observation), pytest-based Typst compile smoke testing, dependency-guardrail verification
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** The observed all-green run is produced via a **single PR `release/v0.5.0 → main`**, opened at the **end of Phase 9**. The PR's `pull_request` checks (ci.yml + docs.yml, both trigger on `pull_request: [main]`) running all-green *is* the CI-01 observation. CI-01 is closed within Phase 9 on the observed green PR checks.
  - **Rationale:** `ci.yml` and `docs.yml` do **not** trigger on the `release/v0.5.0` branch (push/PR triggers are `[main, develop]` only; `docs.yml` has no `workflow_dispatch`). A PR to `main` is the one path that fires **both** workflows against the release-branch content, and main's branch protection requires those checks green before merge anyway — so PR-based observation is both necessary and free.
  - PR checks run pre-merge on a simulated merge (the safety gate), distinct from the post-merge `push` run on main. Relying only on the post-merge run would mean merging blind.
- **D-02:** **No workflow trigger change.** Do NOT add `release/**` to ci.yml/docs.yml triggers and do NOT add `workflow_dispatch` to docs.yml. The PR-based path covers the need without a permanent workflow edit.
- **D-03:** **Merge is deferred to Phase 10.** Phase 10 adds the version-string-fix commit (`__version__` 0.4.3→0.5.0, REL-01) to the *same* PR, which re-triggers the PR checks green, then merges → tag `v*` → `release.yml` publishes to PyPI. Phase 9 opens and observes; Phase 9 does not merge.

### Claude's Discretion

- **D-04:** The smoke test **must exercise all four bundled `@preview` packages** — `codly`, `codly-languages`, `mitex`, `gentle-clues` — in one minimal `.typ` fixture, then `typst compile` it and assert no `unknown variable: kai` (or any) `TypstError`.
  - **Rationale (key scouting finding):** the existing `tests/test_pdf_render_gate.py` already runs a real `typst compile` cross-OS inside the matrix (`tox -e py312/py313` → `pytest tests/`, skipif only on missing typst/pypdf), **but its fixture only uses admonitions (gentle-clues)**. The `kai` break was in **mitex** — so today's gate would NOT catch a mitex `kai` regression. A smoke fixture that touches all four packages is the real guard.
- **D-05:** Form and placement (a promoted/new pytest test in the matrix vs. a dedicated CI job/step; 3-OS matrix vs. ubuntu-only) is left to **researcher/planner discretion**, provided D-04's all-package coverage holds. Reusing the `test_pdf_render_gate.py` pattern (sphinx-build → typst.compile → assert) is a sensible starting point.
- **D-06:** CI-03 is treated as **primarily verification** that the guardrails already reflect the new majors. Scouting confirms the pyproject ceilings (`sphinx>=9.1,<10`, `docutils>=0.21,<0.23`, `typst>=0.15.0,<0.16`) were **already set in Phases 6/7**; `drift.yml` hardcodes no ceilings; the `sphinx-typst-stack` Dependabot group carries no version constraints.
  - **Action:** researcher confirms whether any concrete change is actually required. If a real change is needed it is a minor Dependabot/drift follow-through only — do not manufacture busywork if the guardrails already reflect the majors.

### Deferred Ideas (OUT OF SCOPE)

- **XOS-01** (cross-OS docs-PDF CI on macOS/Windows) — already deferred to v2 at v0.5.0 scoping; docs-PDF stays ubuntu-only. Not in Phase 9.
- **FWD-03 → CFG-01** (user-configurable `@preview` versions) — deferred to v2.
- Making `drift.yml` a required check — explicitly kept advisory-only; revisit separately, not this phase.

None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CI-01 | Every CI job is green — lint, the 3-OS × Python 3.12–3.13 test matrix, type-check, coverage, build, and `docs.yml` (docs-PDF ubuntu-only) — confirmed by an observed Actions run | See "CI-01: Observed Green Matrix" — enumerates every job/trigger, confirms the PR-based path is the only way to fire `docs.yml` against release-branch content, and surfaces two concrete risks (first-ever cross-OS run on new majors; stale branch-protection required-checks list) that must be addressed or explicitly accepted before/while observing green |
| CI-02 | A `typst compile` smoke test is added that would catch a `kai`-class `@preview` break before release | See "CI-02: Smoke Test Design" — confirms via source read of `writer.py`/`translator.py` exactly why the existing gate misses mitex, and specifies the minimal fixture content (real `.. math::` block) needed to close the gap, plus a negative-control validation plan |
| CI-03 | The durability guardrails are updated to the new majors — `drift.yml` ceilings and the `sphinx-typst-stack` Dependabot group reflect `sphinx<10` / `typst<0.16` / `docutils<0.23` | See "CI-03: Guardrail Verification" — confirms via direct file reads that zero changes are required; documents the verification evidence so the planner can write a verification-only task instead of manufacturing a file edit |
</phase_requirements>

## Summary

This is a pure infrastructure/verification phase — no translator, writer, or `@preview`-version code changes. All three requirements were investigated by reading the actual workflow/config files in this repo and by querying the live GitHub API/Actions history for this repository (`YuSabo90002/typsphinx`), not by researching generic CI best-practice externally. The phase's risk is almost entirely in things that are NOT visible from a local `git diff` — GitHub Actions execution history and branch-protection configuration — which is why this research leaned on `gh` CLI/API calls rather than web search.

Three concrete, previously-undocumented findings emerged that materially affect planning:

1. **No CI run has ever exercised the Phase 6–8 stack.** `ci.yml`/`docs.yml` trigger only on `push`/`pull_request` to `[main, develop]` (docs.yml: `main` only), and all of Phases 6–8's commits live on `release/v0.5.0`, which has never pushed to `main`/`develop` and has no open PR. This means the 3-OS × Python 3.12–3.13 matrix, with Sphinx 9.1/docutils 0.22/typst 0.15, has **never run in GitHub Actions** — only locally. The PR that D-01 opens at the end of Phase 9 will be the *first* time Windows/macOS runners see this dependency set. `typst-py` 0.15.0 does ship prebuilt wheels for `win_amd64` and both macOS architectures (`cp38-abi3`, verified via the PyPI JSON API), so package installation itself is low-risk, but this is still the first real cross-OS exercise of the new majors and should be treated as the highest-risk item under CI-01.
2. **`main`'s branch protection `required_status_checks` context list is stale relative to `ci.yml`.** It still requires `"Test Python 3.10 on ubuntu-latest"` and `"Test Python 3.11 on ubuntu-latest"` — job names that stopped being produced when Phase 6 dropped the 3.10/3.11 matrix legs — and it never included the `windows-latest`/`macos-latest` variants or `build-docs` at all. Two required contexts can now never be satisfied by any future PR, so GitHub's merge-readiness UI will show unresolved/pending required checks indefinitely, even when every actual job in the Checks tab is green. This doesn't block *observing* green jobs (CI-01's literal ask), but it undermines the premise in D-01's rationale ("main's branch protection requires those checks green before merge anyway") and will block Phase 10's merge unless fixed. Recommend fixing as part of Phase 9 (a `gh api` call, not a git-tracked file change) — see Common Pitfalls and Security Domain below.
3. **CI-03 requires zero file changes.** Direct reads of `pyproject.toml`, `.github/workflows/drift.yml`, and `.github/dependabot.yml` confirm the ceilings (`sphinx>=9.1,<10`, `docutils>=0.21,<0.23`, `typst>=0.15.0,<0.16`) are already in place from Phases 6/7, `drift.yml` hardcodes no version ceilings of its own, and the `sphinx-typst-stack` Dependabot group has no version fields (it only groups by name pattern). D-06's default is confirmed correct: this requirement is verification-only.

For CI-02, source-reading `typsphinx/writer.py` and `typsphinx/translator.py` proves *precisely* why the existing `tests/test_pdf_render_gate.py` gate cannot catch a mitex regression: **all four `@preview` packages are unconditionally imported and codly is unconditionally initialized in every generated `.typ` file** (both master-document templates and included-document headers), so the existing fixture's `.. code-block:: python` already exercises `codly`/`codly-languages`'s real code paths and its `.. note::` admonitions exercise `gentle-clues`'s real code path. The only package whose *function* (not just its `#import`) is never invoked is `mitex` — its `mi()`/`mitex()` calls only fire when a `.. math::` directive or `:math:` role is present in the source, and the existing fixture has neither. The fix is narrow: add real math content to a smoke fixture, then `typst.compile()` it and let an uncaught `typst.TypstError` fail the test naturally.

**Primary recommendation:** Sequence the phase as (a) write and locally verify the CI-02 smoke test + negative control, (b) verify CI-03 is a no-op and document that verification, (c) pre-flight `ci.yml` on `release/v0.5.0` via its existing `workflow_dispatch` trigger (no trigger-file change — D-02 compliant) to catch cross-OS breakage before the observation PR is opened, (d) fix or explicitly flag the stale branch-protection required-checks list, then (e) open the `release/v0.5.0→ main` PR and observe every job green (CI-01 closes here). Do this in that order so CI-01's observation is the final, highest-confidence step, not a first attempt.

## Project Constraints (from CLAUDE.md)

`./CLAUDE.md` exists at the repo root and applies to this phase. Actionable directives relevant to Phase 9:

- **Lint/format/type commands must match CI exactly:** `black --check .`, `ruff check .`, `mypy typsphinx/` — the planner should verify Phase 9's own changes (new test files, fixtures) pass these before opening the observation PR, since `lint`/`type-check` are two of the jobs being observed.
- **The `@preview` version-sync hazard** (four package versions declared in `writer.py`, `template_engine.py`, `templates/base.typ`, guarded by `tests/test_preview_version_sync.py`) — Phase 9 does not change any of these three files or their versions; the new CI-02 smoke test is purely additive and must not touch the version-sync sites.
- **`tox` is the task runner** (`tox -e py312/py313/lint/type/cov/docs-html/docs-pdf`) — any new local verification command the plan specifies should route through `tox`/`uv run tox`, consistent with how `ci.yml`/`docs.yml` invoke tests, to keep local verification and CI behavior identical.
- **Discrepancy noted, not actioned:** `CLAUDE.md`'s prose still says "Python 3.10+ compatibility is required" and references a `py310..py313` `tox` env_list, but `pyproject.toml`/`tox.ini` (confirmed this session) show the floor was already raised to `>=3.12` with `env_list = py312, py313, ...` in Phase 6 (PIN-02). This is a stale-documentation mismatch predating Phase 9, not something CI-01/02/03 requires fixing — flagged here so the planner doesn't mistake it for a locked constraint that conflicts with the already-completed Phase 6 work. If this bothers the user, a documentation-freshness fix belongs in Phase 10 or a follow-up quick task, not Phase 9.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Observed all-green PR run (CI-01) | CI Workflow Orchestration (`ci.yml`/`docs.yml` triggers) | Branch Protection (GitHub repo setting, not a tracked file) | The workflow files own *which jobs run and when*; branch protection's `required_status_checks` list owns *whether GitHub considers the run's checks satisfied for merge*. These are two independent surfaces that must both be correct — the workflow trigger surface was already fixed by D-01/D-02, but the branch-protection surface was never touched by Phases 6–9 and has drifted stale (see Finding 2). |
| `kai`-class break detection (CI-02) | Test Suite (`tests/*.py`, pytest) | CI Workflow Orchestration (matrix auto-discovers new `test_*.py` files) | The smoke-test *logic* is pure pytest/typst-py code; wiring it into CI requires zero workflow-file changes because `tox -e py312/py313` already runs `pytest {posargs:tests/}`, which picks up any new `test_*.py` module automatically. |
| Guardrail ceilings (CI-03) | Dependency Configuration (`pyproject.toml`) | Durability Automation (`drift.yml`, `dependabot.yml`) | `pyproject.toml`'s version specifiers are the single source of truth for the ceilings; `drift.yml` and the Dependabot group both *respect* that source rather than declaring their own ceilings, so there is nothing in those two files to update once `pyproject.toml` is correct. |

## Standard Stack

No new external dependencies are introduced by this phase. All tooling needed already exists in the repo:

### Core (already present — no bump needed)
| Library | Version (pyproject.toml) | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `typst` | `>=0.15.0,<0.16` [VERIFIED: repo file `pyproject.toml`] | `typst.compile()` used by the smoke test to prove real compilation | Already the project's PDF-compile dependency (Phase 7); no new install |
| `pypdf` | `>=6.14,<7` [VERIFIED: repo file `pyproject.toml`] | Available if the smoke test wants to assert on extracted text (optional — CI-02 only needs a successful compile, not text extraction) | Already a `dev` extra added in Phase 8.1 for `test_pdf_render_gate.py` |
| `pytest` | `>=8.4,<10` [VERIFIED: repo file `pyproject.toml`] | Test runner; smoke test is a plain pytest module | Already the project's test framework |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| A dedicated new GitHub Actions job for the smoke test | A promoted pytest test inside the existing matrix (`tests/test_*.py`) | A new job adds YAML surface, a 6th/7th CI lane to maintain, and duplicate `uv sync`/tox setup. A pytest test costs nothing extra — it rides the existing 3-OS × 2-Python matrix job for free, since `pytest {posargs:tests/}` already globs `test_*.py`. **Recommended: pytest test, not a new job** (resolves D-05 in favor of the lower-friction path). |
| Reusing/extending `tests/fixtures/admonition_render_gate/` in place | A **new**, separate fixture + test module dedicated to the 4-package smoke check | Reusing the admonition fixture conflates two different regression concerns (markup/code-mode leak-detection vs. compile-time `TypstError` detection) into one test's assertions, and the phase would be editing Phase 8.1's asset. A new `tests/fixtures/preview_smoke/` + `tests/test_preview_smoke_gate.py` keeps single responsibility and leaves 8.1's gate untouched. **Recommended.** |
| Fixing branch-protection staleness | Leaving it alone since it isn't in D-01..D-06's named files | Leaving it means Phase 10's merge will show unsatisfied required-checks (`3.10 ubuntu`, `3.11 ubuntu` — jobs that no longer exist) even though every real job is green, and the PR's summary box will misleadingly read as blocked. Fixing it is a `gh api`/Settings-UI action, not a git commit, so it doesn't conflict with D-02 ("no workflow trigger change" — this is a branch-protection setting, not a trigger). **Recommended as an in-phase action, or explicitly deferred to Phase 10 with a note in STATE.md if the planner prefers not to touch repo settings from Phase 9.** |

**Installation:** None required — `uv sync --extra dev` (already run in CI) covers everything the smoke test needs.

## Package Legitimacy Audit

**Not applicable.** This phase installs no new external packages (no `pip`/`npm`/`cargo` additions). All libraries used by the recommended smoke test (`typst`, `pypdf`, `pytest`) are pre-existing dev dependencies verified present in `pyproject.toml` and already installed in the project's `uv`-managed virtualenv (confirmed via `uv run python -c "import typst"` / `import pypdf"` — both resolved successfully in this session).

## Architecture Patterns

### System Architecture Diagram

```
                         ┌─────────────────────────────┐
                         │  release/v0.5.0 (all Phase   │
                         │  6-8 commits; never yet run  │
                         │  through GH Actions)         │
                         └───────────┬──────────────────┘
                                     │
                    (a) pre-flight (D-02 safe: uses
                        EXISTING workflow_dispatch
                        trigger on ci.yml, no new
                        trigger)
                                     │
                                     ▼
                    ┌────────────────────────────────┐
                    │  gh workflow run ci.yml         │
                    │  --ref release/v0.5.0           │
                    │  -> exercises 3-OS x py3.12/3.13 │
                    │     matrix for the FIRST TIME    │
                    │     against the new majors       │
                    └───────────────┬────────────────┘
                                     │ pass/fail observed
                                     │ (fix any cross-OS breaks
                                     │  before proceeding)
                                     ▼
                    ┌────────────────────────────────┐
                    │ (b) Write CI-02 smoke test:      │
                    │  tests/fixtures/preview_smoke/   │
                    │  + tests/test_preview_smoke_gate │
                    │  -> sphinx-build -> typst.compile │
                    │     -> assert no TypstError       │
                    │  Negative control: run against a  │
                    │  known-broken mitex (<=0.2.5) to  │
                    │  prove the test WOULD have caught │
                    │  the original kai break            │
                    └───────────────┬────────────────┘
                                     │ committed to release/v0.5.0
                                     ▼
                    ┌────────────────────────────────┐
                    │ (c) Verify CI-03 (no file change)│
                    │  grep pyproject.toml / drift.yml │
                    │  / dependabot.yml ceilings        │
                    └───────────────┬────────────────┘
                                     │
                                     ▼
                    ┌────────────────────────────────┐
                    │ (d) Fix branch-protection stale  │
                    │  required_status_checks list     │
                    │  (gh api, not a workflow file)    │
                    └───────────────┬────────────────┘
                                     │
                                     ▼
                    ┌────────────────────────────────┐
                    │ (e) Open PR release/v0.5.0->main │
                    │  -> ci.yml (pull_request) fires   │
                    │  -> docs.yml (pull_request) fires │
                    │  -> OBSERVE all jobs green         │
                    │     (CI-01 closes here)            │
                    │  Phase 9 STOPS HERE (no merge --   │
                    │  Phase 10 adds REL-01 commit and    │
                    │  merges)                            │
                    └────────────────────────────────┘
```

### Recommended Project Structure (additions only)
```
tests/
├── fixtures/
│   ├── admonition_render_gate/     # existing (Phase 8.1) — unchanged
│   └── preview_smoke/              # NEW — minimal fixture exercising all 4 @preview packages
│       ├── conf.py                 # mirrors admonition_render_gate/conf.py (master doc via typst_documents)
│       └── index.rst               # .. note:: (gentle-clues) + .. code-block:: python (codly/codly-languages)
│                                    #   + .. math:: with real LaTeX (mitex) -- the missing coverage
├── test_pdf_render_gate.py         # existing (Phase 8.1) — unchanged
├── test_preview_version_sync.py    # existing (Phase 7) — unchanged
└── test_preview_smoke_gate.py      # NEW — sphinx-build -> typst.compile() -> assert no TypstError
```

### Pattern 1: Reuse the sphinx-build → typst.compile() → assert pipeline
**What:** `tests/test_pdf_render_gate.py` already implements the exact 3-step pattern this phase needs: invoke `sphinx-build` as `sys.executable -m sphinx` (not `uv run sphinx-build`, to avoid a documented PATH-shadowing hazard with a stray non-Nix `uv` binary — see that file's inline comment), then `typst.compile(str(index_typ), output=str(pdf_output))`, then assert.
**When to use:** Any new real-compile regression gate in this repo.
**Example:**
```python
# Source: tests/test_pdf_render_gate.py (this repo, Phase 8.1)
result = subprocess.run(
    [sys.executable, "-m", "sphinx", "-b", "typst", str(fixture_dir), str(build_dir)],
    capture_output=True, text=True,
)
assert result.returncode == 0, f"sphinx-build failed:\n{result.stdout}\n{result.stderr}"

pdf_output = build_dir / "index.pdf"
typst.compile(str(build_dir / "index.typ"), output=str(pdf_output))  # raises typst.TypstError on failure
assert pdf_output.exists() and pdf_output.stat().st_size > 0
```
For CI-02, the assertion is simpler than the admonition gate's leak-detection: a bare, uncaught `typst.TypstError` from `typst.compile()` is sufficient to fail the test loudly with the exact Typst error message (e.g. `unknown variable: kai`) in the pytest failure output — no `try/except` wrapper is needed, though one can be added for a clearer custom message.

### Pattern 2: `skipif` on `typst`/`pypdf` availability, no `slow` marker
**What:** `test_pdf_render_gate.py` gates its whole test class with `@pytest.mark.skipif(not (TYPST_AVAILABLE and PYPDF_AVAILABLE), reason=...)` and carries no `slow`/`integration` marker.
**When to use:** The new smoke test should follow the identical convention — `typst` is a hard runtime dependency already (not `pypdf`, which the smoke test may not even need if it only checks compile success, not text content). Since `typst` is a required runtime dependency (`pyproject.toml` `dependencies`, not just `dev`), the skipif is close to always-true in CI, but keeps local dev environments without `typst`/`pypdf` installed from breaking.
**Note:** no test in this repo currently uses the declared `slow` marker (`grep` found zero uses) — do not introduce it for this test; a single-page fixture compile takes well under a second and doesn't warrant deselection.

### Pattern 3: Master-document fixture, not an included document
**What:** `tests/fixtures/admonition_render_gate/conf.py` deliberately declares `index` in `typst_documents` so the writer treats it as a master document (full template applied) rather than an included document (minimal-import header only).
**When to use:** The new `preview_smoke` fixture should copy this exact `conf.py` shape. **Important nuance discovered this session:** both code paths (master-document template via `template_engine.py`/`templates/base.typ`, and included-document header via `writer.py`) already unconditionally emit all four `#import "@preview/..."` statements and unconditionally call `#show: codly-init.with()` / `#codly(languages: codly-languages)` — so master-vs-included choice does not affect *which packages are imported*, only affects the surrounding template chrome. Either fixture shape would technically compile the imports; using a master document keeps parity with the existing 8.1 gate and produces a directly-compilable single-file `.typ`.

### Anti-Patterns to Avoid
- **Trusting `#import` presence as proof of coverage:** All four `@preview` packages are imported in every generated `.typ` file regardless of document content. A smoke test that merely confirms the import statements compile (e.g. an empty document) proves nothing about `mitex`'s actual math-rendering code path — the exact gap that let `kai` through undetected. The fixture MUST include real invocations: a `.. math::` block (→ `mitex(...)`) or `:math:` role (→ `mi(...)`) for mitex, a `.. code-block::` for codly/codly-languages, and a `.. note::`/other admonition for gentle-clues.
- **Adding a new CI workflow job for the smoke test:** Unnecessary YAML surface and duplicate environment setup; a plain `test_*.py` file already rides the existing matrix for free.
- **Editing `ci.yml`/`docs.yml` triggers to add `release/**` or `workflow_dispatch` on docs.yml:** Explicitly forbidden by D-02.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Proving a GitHub Actions PR run is all-green | A custom polling/status-aggregation script | `gh pr checks <PR#> --watch` or `gh run list --workflow=ci.yml/docs.yml --json conclusion` | `gh` CLI already exposes per-job conclusions; no need to hit the raw REST/GraphQL API directly for this |
| Detecting a `kai`-class compile break | Regex-scanning `.typ` output for suspicious tokens | A real `typst.compile()` call and letting `typst.TypstError` propagate | Static text scanning cannot catch runtime Typst evaluation errors (`kai` was a *runtime* "unknown variable" error inside mitex's compiled math, not a lexical pattern in the generated `.typ` source) |
| Verifying dependency ceilings match across 3 files | A new custom Python script that parses and compares `pyproject.toml`/`drift.yml`/`dependabot.yml` | Direct `grep`/manual read during planning + verification, since **no file needs to change** (D-06 confirmed) | Building a comparison script for a verification-only requirement is exactly the "manufactured busywork" D-06 warns against. If future durability wants machine-checked guardrail parity, that's a new, separate initiative — not in this phase's scope. |

**Key insight:** Every capability this phase needs already has a working reference implementation in this exact repo (`test_pdf_render_gate.py` for the compile pattern, `test_preview_version_sync.py` for the "assert 3 files agree" pattern, `gh` CLI for Actions observation). The research effort here is almost entirely about reading this codebase and its live GitHub state correctly, not about learning an external framework.

## Common Pitfalls

### Pitfall 1: Assuming the PR-based observation will show branch-protection-satisfied merge readiness
**What goes wrong:** The planner assumes that once every actual job (lint/test-matrix/type/coverage/build/docs) reports success, the PR's "Merge" panel will show a clean, mergeable state — matching D-01's rationale that "main's branch protection requires those checks green before merge anyway."
**Why it happens:** `main`'s `required_status_checks.contexts` (fetched live via `gh api repos/YuSabo90002/typsphinx/branches/main/protection`) still lists `"Test Python 3.10 on ubuntu-latest"` and `"Test Python 3.11 on ubuntu-latest"` — legs that stopped existing when Phase 6 dropped 3.10/3.11 from `ci.yml`'s matrix — and never included the `windows-latest`/`macos-latest` variants of the 3.12/3.13 jobs, nor `build-docs` (docs.yml). GitHub cannot receive a status post for a context that no job produces, so those two required checks will show "Expected — Waiting for status to be reported" **forever**.
**How to avoid:** Update the required-status-checks context list via `gh api --method PUT -f 'required_status_checks[contexts][]=Test Python 3.12 on ubuntu-latest' ... repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks` (or the Settings → Branches UI) to match the current `ci.yml` job-name set before or during Phase 9. This is a GitHub repo setting, not a git-tracked file, so it does not conflict with D-02 (which only forbids editing workflow *trigger* YAML).
**Warning signs:** The PR shows "Some checks haven't completed yet" or "Required" badges stuck in a pending/expected state next to job names that don't appear anywhere in the live Checks tab.

### Pitfall 2: Treating the Phase 9 observation PR as a routine re-run
**What goes wrong:** Assuming that because the test suite passes locally (Phase 8's `filterwarnings` guard, full pytest suite green, `tox -e docs-pdf` green — all confirmed in STATE.md/PROJECT.md history), the Actions run will trivially pass too.
**Why it happens:** `ci.yml`/`docs.yml` only trigger on `push`/`pull_request` to `[main, develop]` (docs.yml: `main` only). Every commit since Phase 6 has landed on `release/v0.5.0`, which never triggers either workflow. **No GitHub-hosted Windows or macOS runner has ever installed or exercised this dependency set** (Sphinx 9.1, docutils 0.22, typst 0.15, Python 3.12/3.13-only). Local verification (this repo's sandbox uses a patched `uv` binary per a documented `patchelf` workaround noted in STATE.md) does not guarantee cross-platform GitHub-runner behavior.
**How to avoid:** Before opening the observation PR, manually trigger `ci.yml` on `release/v0.5.0` via its existing `workflow_dispatch:` trigger (`gh workflow run ci.yml --ref release/v0.5.0`) — this uses a trigger that already exists (no D-02 violation) and surfaces any Windows/macOS-specific breakage in a disposable run, before it counts as "the" observation.
**Warning signs:** Windows-specific path-separator bugs, `tox-uv` runner differences, or `typst`/`sphinx` C-extension wheel resolution failures that only manifest on non-Linux runners.

### Pitfall 3: Conflating "package imported" with "package exercised" in the smoke fixture
**What goes wrong:** Building a smoke fixture that compiles successfully but doesn't actually prove mitex-specific coverage, because the fixture happens to compile fine even without math content (all 4 imports + codly-init already fire on every document).
**Why it happens:** `typsphinx/writer.py` (included-doc path) and `typsphinx/template_engine.py`/`templates/base.typ` (master-doc path) unconditionally emit `#import "@preview/mitex:0.2.7": mi, mitex` regardless of whether any math node exists in the source document. An `#import` of an unused function does not error — `mi()`/`mitex()` must actually be *called* (which only happens via `translator.py`'s `visit_math`/`visit_math_block`, themselves only triggered by a `.. math::` directive or `:math:` role in the rST source) to exercise the exact code path that broke under the old mitex version.
**How to avoid:** Confirm the fixture's `index.rst` contains a real `.. math::` block (which the translator maps to `mitex(\`...\`)`) or `:math:` inline role (mapped to `mi(\`...\`)`), not just admonitions/code-blocks.
**Warning signs:** The smoke test passes even when manually forcing an old, broken mitex version in a scratch venv — that's the negative-control signal that the fixture doesn't actually cover mitex (see Validation Architecture below).

### Pitfall 4: Manufacturing a CI-03 file change that isn't needed
**What goes wrong:** Editing `drift.yml` or `dependabot.yml` to add explicit version-ceiling fields "just to be safe," when D-06 explicitly warns against busywork.
**Why it happens:** `drift.yml`'s `uv lock --upgrade` step has no hardcoded ceiling (confirmed via direct read — zero matches for `sphinx<`/`typst<`/`docutils<`/version-literal patterns anywhere under `.github/`), and the Dependabot `sphinx-typst-stack` group config has no version fields at all — it groups PRs purely by name pattern (`sphinx*`, `docutils*`, `typst*`). Both correctly derive their effective ceiling from `pyproject.toml`'s specifiers, which are already correct.
**How to avoid:** Write CI-03 as a verification task (grep/read `pyproject.toml`, confirm `sphinx>=9.1,<10` / `docutils>=0.21,<0.23` / `typst>=0.15.0,<0.16`; confirm `drift.yml` and `dependabot.yml` have no conflicting hardcoded ceilings) and record the evidence — do not add a code/config diff unless verification actually finds a discrepancy.
**Warning signs:** A CI-03 plan task that proposes editing `.github/dependabot.yml` or `.github/workflows/drift.yml` without first showing what's currently wrong with them.

### Pitfall 5: An already-stale open Dependabot PR muddying the picture
**What goes wrong:** Open PR #108 (`chore(deps): bump the sphinx-typst-stack group...`, targeting `main`, opened 2026-07-05) proposes bumping `docutils` to `0.23` — a version the *new* v0.5.0 ceiling (`docutils>=0.21,<0.23`) explicitly excludes — because it was generated against `main`'s old (pre-Phase-6) pins. It is already failing CI (`gh pr checks 108` shows every job failing) for reasons unrelated to Phase 9.
**Why it happens:** Dependabot generated this PR before Phase 6–9's pin changes landed anywhere reachable from `main`.
**How to avoid:** This is informational, not a Phase 9 action item — flag it in STATE.md/PROJECT.md as something to close (superseded) once the v0.5.0 PR merges in Phase 10. Do not let it distract from or get conflated with the Phase 9 observation PR.
**Warning signs:** Confusing PR #108's pre-existing red CI with a regression introduced by this phase's work.

## Code Examples

### Minimal smoke fixture exercising all four `@preview` packages
```rst
.. Source: tests/fixtures/preview_smoke/index.rst (new, this phase)
.. Modeled on tests/fixtures/admonition_render_gate/index.rst (Phase 8.1)

Preview Smoke
=============

.. note::

   Exercises gentle-clues (admonition -> clue-type content block).

.. code-block:: python

   x = 1

Exercises codly + codly-languages (labeled code block -> codly()/codly-range()
calls, initialized globally via #codly(languages: codly-languages)).

.. math::

   e^{i \pi} + 1 = 0

Exercises mitex (block math -> a real ``mitex(`...`)`` call -- this is the
code path the ``kai`` regression broke, and the only one the existing
admonition_render_gate fixture never invokes).
```

### Smoke test module (compile-success assertion, no text extraction needed)
```python
# Source: adapted from tests/test_pdf_render_gate.py (this repo, Phase 8.1)
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst
    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False


@pytest.mark.skipif(not TYPST_AVAILABLE, reason="typst-py required for the CI-02 smoke gate")
def test_preview_smoke_all_four_packages_compile(tmp_path):
    fixture_dir = Path(__file__).parent / "fixtures" / "preview_smoke"
    build_dir = tmp_path / "_build"

    result = subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typst", str(fixture_dir), str(build_dir)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"sphinx-build failed:\n{result.stdout}\n{result.stderr}"

    index_typ = build_dir / "index.typ"
    pdf_output = build_dir / "index.pdf"
    # A typst.TypstError here (e.g. "unknown variable: kai") fails the test
    # loudly with the underlying Typst error message in the traceback --
    # no try/except wrapper needed for the core signal.
    typst.compile(str(index_typ), output=str(pdf_output))

    assert pdf_output.exists() and pdf_output.stat().st_size > 0
```

### Pre-flighting the matrix on `release/v0.5.0` without any trigger changes (D-02 safe)
```bash
# ci.yml already declares `workflow_dispatch:` with no branch restriction --
# this can be run against release/v0.5.0 right now, with zero YAML edits.
gh workflow run ci.yml --repo YuSabo90002/typsphinx --ref release/v0.5.0
gh run watch --repo YuSabo90002/typsphinx  # or: gh run list --workflow=ci.yml --branch release/v0.5.0
```
Note: `docs.yml` has **no** `workflow_dispatch` trigger (confirmed via direct read), so this pre-flight technique does not extend to the docs-PDF lane — that lane can only be observed via the actual PR (matches D-01's stated rationale exactly) or locally via `tox -e docs-pdf`.

### Verifying CI-03's guardrails require no change (verification commands, not a diff)
```bash
grep -E 'sphinx|docutils|typst' pyproject.toml
# dependencies = ["sphinx>=9.1,<10", "docutils>=0.21,<0.23", "typst>=0.15.0,<0.16"]  -- already correct

grep -E 'sphinx|docutils|typst|<[0-9]' .github/workflows/drift.yml
# no hardcoded ceilings found -- `uv lock --upgrade` respects pyproject.toml's specifiers

cat .github/dependabot.yml
# sphinx-typst-stack group: patterns only (sphinx*/docutils*/typst*), no version fields to update
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| CI-repair via per-phase PRs to `main` (v0.4.4 model) | Single accumulated release PR at milestone end (v0.5.0 model) | v0.5.0 scoping (STATE.md) | Intermediate phase states (e.g. Phase 6 pre-`kai`-fix) are deliberately red and never observed by GH Actions until this one final PR — this is why Phase 9 exists as a distinct "go observe it now" phase rather than each earlier phase self-verifying via CI |
| `test_pdf_render_gate.py` only covering gentle-clues | This phase extends real-compile coverage to all 4 `@preview` packages | Phase 9 (this research) | Closes the specific coverage gap named in D-04 |

**Deprecated/outdated:** None — no API or library deprecations are in scope for this phase.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | GitHub's branch-protection UI will show a required status check as indefinitely "pending/expected" if no job ever posts that exact context string (rather than, say, silently ignoring an unmatched required-check name) | Common Pitfalls #1, Summary Finding 2 | If wrong in the other direction (GitHub auto-prunes stale contexts), the recommended `gh api` fix is unnecessary but harmless; if GitHub instead treats an unmatched required context as an automatic pass, the risk is inverted (a false sense of "merge-ready" without the actual 3.10/3.11 legs — moot anyway since those legs no longer exist). Recommend the planner spot-check the PR's actual "Merge" panel state once the observation PR is open, rather than relying solely on this claim. |
| A2 | Dependabot's pip-ecosystem default versioning strategy respects the existing upper-bound specifier in `pyproject.toml` (i.e., it will not propose `docutils==0.24` while `<0.23` is declared) | CI-03 / Don't Hand-Roll | If Dependabot's actual behavior differs (e.g., a "widen ranges" strategy that proposes raising the ceiling itself), CI-03's "no file change needed" conclusion could be wrong for future drift, though it would not invalidate the *current* verification (which only asserts the three files agree today, confirmed by direct read) |

## Open Questions

1. **Should the branch-protection required-checks fix land inside Phase 9, or be flagged forward to Phase 10?**
   - What we know: The stale list (`3.10`/`3.11 ubuntu-latest` required, no OS-matrix/`build-docs` contexts) is a live, verified fact (`gh api .../branches/main/protection`). It doesn't block CI-01's literal "observe every job green" ask, but it does undermine D-01's "branch protection requires these checks anyway" premise and will block Phase 10's actual merge.
   - What's unclear: Whether the user wants Phase 9 (an "observe, don't merge" phase) to also touch a GitHub repo *setting* (not a git-tracked file), or whether that's cleanly Phase 10's problem since Phase 10 owns the merge.
   - Recommendation: Planner should surface this as an explicit task/checkpoint in the Phase 9 plan (e.g., a `checkpoint:human-verify` or a plain task using `gh api`) rather than silently deferring it — leaving it undocumented risks Phase 10 discovering a merge-blocked PR with no prior context.

2. **Does the negative-control validation (proving the CI-02 fixture would have caught the original `kai` break) need to run in CI, or is a one-time local/manual proof sufficient?**
   - What we know: The Validation Architecture section below proposes a one-time local check (temporarily force an old mitex version and confirm the new smoke test fails with the `kai` error) as the Nyquist-style independent signal that the fixture's coverage claim is real, not just plausible.
   - What's unclear: Whether this negative control should be codified as a repeatable script/test (e.g., a `tests/test_preview_smoke_gate_negative_control.py` that's normally skipped) or just documented as a manual verification step performed once during Phase 9 execution and recorded in the plan's SUMMARY.
   - Recommendation: A one-time manual/local proof, documented in the plan's execution summary, is sufficient and avoids adding permanent CI surface for a check that only needs to be true once (the fixture's *sensitivity*, not its ongoing behavior, is what's being proven).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `gh` CLI | Observing/pre-flighting Actions runs, inspecting branch protection | ✓ | 2.96.0 [VERIFIED: `gh --version`] | GitHub web UI |
| `typst` (typst-py) | CI-02 smoke test | ✓ | 0.15.0 (resolved in project venv) [VERIFIED: `uv run python -c "import typst"`] | — (already a required runtime dependency) |
| `pypdf` | Optional text-extraction assertions (not required for the minimal CI-02 design) | ✓ | 6.14.2 [VERIFIED: `uv run python -c "import pypdf"`] | Skip text-extraction; rely on `typst.compile()` raising `TypstError` alone |
| GitHub-hosted `windows-latest`/`macos-latest` runners with typst-py 0.15.0 wheels | CI-01 cross-OS matrix | Not directly testable from this sandbox — verified via PyPI JSON API that prebuilt wheels exist (`win_amd64`, `macosx_10_12_x86_64`, `macosx_11_0_arm64`, all `cp38-abi3`) [VERIFIED: PyPI JSON API `https://pypi.org/pypi/typst/0.15.0/json`] | 0.15.0 | None needed — wheels exist, so no source-build fallback should be required |

**Missing dependencies with no fallback:** None identified.

**Missing dependencies with fallback:** None identified — all tooling needed is already present.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest `>=8.4,<10` (project's existing framework) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `uv run pytest tests/test_preview_smoke_gate.py -v` (new file) |
| Full suite command | `uv run tox -e py312` (also exercises `test_preview_smoke_gate.py` automatically once added, since `testpaths = ["tests"]` globs `test_*.py`) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CI-01 | Every CI job green on the observed `release/v0.5.0 → main` PR | manual/process (GitHub Actions observation, not a pytest test) | `gh pr checks <PR#> --watch` and/or `gh run list --workflow=ci.yml --workflow=docs.yml --json conclusion` | N/A — process verification, not code |
| CI-02 | Smoke test compiles all 4 `@preview` packages via real Typst function calls with no `TypstError` | integration (real `typst.compile()`) | `uv run pytest tests/test_preview_smoke_gate.py -v` | ❌ Wave 0 — new fixture + test file needed |
| CI-03 | Guardrail ceilings already reflect `sphinx<10`/`typst<0.16`/`docutils<0.23` | manual verification (grep/read, no new test) | `grep -E 'sphinx|docutils|typst' pyproject.toml` | N/A — verification-only per D-06; no file/test needed unless a discrepancy is found |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_preview_smoke_gate.py -v` (new smoke test only — seconds)
- **Per wave merge:** `uv run tox -e py312` (full local suite, includes the new smoke test) plus `uv run tox -e docs-pdf` as the closest local proxy for the `docs.yml` lane
- **Phase gate:** Full local suite green (`tox -e py312`/`py313`, `lint`, `type`, `cov`, `docs-pdf`) BEFORE opening the observation PR, then the PR's own Actions run is the final live gate for CI-01

### Wave 0 Gaps
- [ ] `tests/fixtures/preview_smoke/conf.py` + `tests/fixtures/preview_smoke/index.rst` — new minimal fixture covering all 4 `@preview` packages (needed for CI-02)
- [ ] `tests/test_preview_smoke_gate.py` — new pytest module implementing the sphinx-build → typst.compile() → assert pattern (needed for CI-02)
- [ ] One-time negative-control proof (not a permanent test file): temporarily force an old, `kai`-broken mitex version (e.g. `mitex:0.2.4` or `0.2.5`, per PROJECT.md's root-cause note) in a scratch environment and confirm the new smoke test fails with the `kai` error — documented in the plan's execution summary, not committed as CI surface
- Framework install: none — pytest/typst-py/pypdf are all already dev dependencies

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | N/A — no auth surface touched |
| V3 Session Management | No | N/A |
| V4 Access Control | **Yes** | Branch protection `required_status_checks` is the access-control gate over `main` (only allows merges after named checks pass). Finding 2 above shows this gate is currently misconfigured (references non-existent job names), which **weakens** the intended access-control guarantee — a PR could reach an apparently-blocked-forever state, tempting an admin bypass (`enforce_admins.enabled: false`, confirmed via `gh api`, means repo admins CAN merge past unsatisfied required checks) without the intended verification actually having been the thing that was checked. |
| V5 Input Validation | No | N/A — no user-supplied input is processed by this phase's changes (the smoke-test fixture is static, developer-authored content) |
| V6 Cryptography | No | N/A |

### Known Threat Patterns for GitHub Actions / dependency-guardrail CI

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Stale/misconfigured branch-protection required-checks list allowing a merge without the intended verification having actually run | Tampering / Elevation of Privilege (bypassing intended access control) | Keep `required_status_checks.contexts` in lockstep with the workflow's actual job names whenever a matrix changes (this is the exact drift found in Finding 2) — treat it as part of "durability guardrails" even though it's a repo *setting*, not a git-tracked file |
| A compromised or malicious `@preview` package version silently entering the build via an un-pinned/overly-wide Dependabot bump | Tampering (supply chain) | Already mitigated by this project's existing upper-bound version ceilings (`pyproject.toml`) plus the 3-way version-sync test (`test_preview_version_sync.py`) plus (after this phase) the real-compile smoke test — Dependabot PRs still require human review before merge, which is out of this phase's scope to change |
| GitHub Actions pinned by mutable tag (e.g. `actions/checkout@v6`) rather than immutable commit SHA | Tampering (supply chain — a compromised action publisher could move the tag) | This repo already follows the tag-pinning convention project-wide (pre-existing, established before v0.5.0); pinning by SHA would be a separate, cross-cutting hardening initiative and is explicitly **out of scope** for CI-01/02/03 — noted here for completeness, not recommended as a Phase 9 task (would be scope creep beyond the three locked requirements) |

## Sources

### Primary (HIGH confidence — direct repo/live-API verification this session)
- `pyproject.toml` (this repo) — confirmed dependency ceilings and dev extras
- `.github/workflows/ci.yml`, `.github/workflows/docs.yml`, `.github/workflows/drift.yml`, `.github/dependabot.yml` (this repo) — confirmed job names, triggers, and absence of hardcoded ceilings
- `tests/test_pdf_render_gate.py`, `tests/test_preview_version_sync.py`, `tests/fixtures/admonition_render_gate/*` (this repo) — confirmed reusable patterns and the master-document import behavior
- `typsphinx/writer.py`, `typsphinx/translator.py` (this repo) — confirmed exactly why the existing gate misses mitex (unconditional imports vs. conditional real invocation)
- `gh api repos/YuSabo90002/typsphinx/branches/main/protection` (live GitHub API, this session) — confirmed the stale required-status-checks context list
- `gh run list` / `gh pr list` / `gh pr checks 108` (live GitHub API, this session) — confirmed no CI run has exercised the new stack yet, and surfaced the pre-existing stale Dependabot PR #108
- `https://pypi.org/pypi/typst/0.15.0/json` (live PyPI API, this session) — confirmed prebuilt wheel availability for Windows/macOS

### Secondary (MEDIUM confidence)
- None — no external web search was needed for this phase; all findings were code/API-grounded.

### Tertiary (LOW confidence)
- Dependabot's default pip-ecosystem versioning-strategy behavior (see Assumptions Log A2) — based on general platform knowledge, not fetched/verified against current GitHub docs this session.

## Metadata

**Confidence breakdown:**
- Standard Stack: HIGH — no new dependencies; existing versions confirmed via direct file read
- Architecture: HIGH — all patterns and the mitex-coverage-gap root cause confirmed via direct source reads of `writer.py`/`translator.py`, not inferred
- Pitfalls: HIGH — the two most load-bearing pitfalls (never-run-in-CI stack, stale branch protection) were discovered via live `gh api`/`gh run list` calls this session, not assumed

**Research date:** 2026-07-11
**Valid until:** Effectively bound to this repo's current state — if `ci.yml`'s matrix or `main`'s branch protection changes before Phase 9 executes, re-verify the two live-state findings (Finding 1: no-CI-run-yet; Finding 2: stale required-checks list) before relying on them.
