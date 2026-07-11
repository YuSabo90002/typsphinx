# Phase 9: Green CI Matrix + Smoke Test + Guardrails - Context

**Gathered:** 2026-07-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 9 delivers three things for the v0.5.0 forward-ecosystem milestone:

1. **CI-01** — an *observed* all-green Actions run across the full matrix on the new majors (lint, 3-OS × Python 3.12–3.13 test matrix, type-check, coverage, build, and `docs.yml` docs-PDF ubuntu-only).
2. **CI-02** — a `typst compile` smoke test wired into CI that would fail loudly on a `kai`-class `@preview` break *before* release, closing the gap the internal-only `test_preview_version_sync.py` misses.
3. **CI-03** — the durability guardrails (`drift.yml` ceilings and the `sphinx-typst-stack` Dependabot group) reflect `sphinx<10` / `typst<0.16` / `docutils<0.23`.

This is an infrastructure/CI phase. It does **not** change translator/writer behavior or `@preview` versions — those are locked from Phases 6/7/8/8.1. Merge-to-main, the version-string fix, and the actual PyPI release are **Phase 10**, not here.

</domain>

<decisions>
## Implementation Decisions

### CI-01 — How the observed green run is produced (DISCUSSED)
- **D-01:** The observed all-green run is produced via a **single PR `release/v0.5.0 → main`**, opened at the **end of Phase 9**. The PR's `pull_request` checks (ci.yml + docs.yml, both trigger on `pull_request: [main]`) running all-green *is* the CI-01 observation. CI-01 is closed within Phase 9 on the observed green PR checks.
  - **Rationale:** `ci.yml` and `docs.yml` do **not** trigger on the `release/v0.5.0` branch (push/PR triggers are `[main, develop]` only; `docs.yml` has no `workflow_dispatch`). A PR to `main` is the one path that fires **both** workflows against the release-branch content, and main's branch protection requires those checks green before merge anyway — so PR-based observation is both necessary and free.
  - **PR checks run pre-merge on a simulated merge** (the safety gate), distinct from the post-merge `push` run on main. Relying only on the post-merge run would mean merging blind — the exact anti-pattern (long-undetected red CI) this milestone exists to fix.
- **D-02:** **No workflow trigger change.** Do NOT add `release/**` to ci.yml/docs.yml triggers and do NOT add `workflow_dispatch` to docs.yml. The PR-based path covers the need without a permanent workflow edit.
- **D-03:** **Merge is deferred to Phase 10.** Phase 10 adds the version-string-fix commit (`__version__` 0.4.3→0.5.0, REL-01) to the *same* PR, which re-triggers the PR checks green, then merges → tag `v*` → `release.yml` publishes to PyPI. Phase 9 opens and observes; Phase 9 does not merge.

### Claude's Discretion — CI-02 (smoke test) — NOT discussed, user approved default
- **D-04:** The smoke test **must exercise all four bundled `@preview` packages** — `codly`, `codly-languages`, `mitex`, `gentle-clues` — in one minimal `.typ` fixture, then `typst compile` it and assert no `unknown variable: kai` (or any) `TypstError`.
  - **Rationale (key scouting finding):** the existing `tests/test_pdf_render_gate.py` already runs a real `typst compile` cross-OS inside the matrix (`tox -e py312/py313` → `pytest tests/`, skipif only on missing typst/pypdf), **but its fixture only uses admonitions (gentle-clues)**. The `kai` break was in **mitex** — so today's gate would NOT catch a mitex `kai` regression. A smoke fixture that touches all four packages is the real guard.
- **D-05:** Form and placement (a promoted/new pytest test in the matrix vs. a dedicated CI job/step; 3-OS matrix vs. ubuntu-only) is left to **researcher/planner discretion**, provided D-04's all-package coverage holds. Reusing the `test_pdf_render_gate.py` pattern (sphinx-build → typst.compile → assert) is a sensible starting point.

### Claude's Discretion — CI-03 (guardrail ceilings) — NOT discussed, user approved default
- **D-06:** CI-03 is treated as **primarily verification** that the guardrails already reflect the new majors. Scouting confirms the pyproject ceilings (`sphinx>=9.1,<10`, `docutils>=0.21,<0.23`, `typst>=0.15.0,<0.16`) were **already set in Phases 6/7**; `drift.yml` hardcodes no ceilings (its `uv lock --upgrade` respects pyproject); the `sphinx-typst-stack` Dependabot group carries no version constraints.
  - **Action:** researcher confirms whether any concrete change is actually required. If a real change is needed it is a minor Dependabot/drift follow-through only — do not manufacture busywork if the guardrails already reflect the majors.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope & requirements
- `.planning/ROADMAP.md` §"Phase 9" — goal + 3 success criteria (CI-01/02/03)
- `.planning/REQUIREMENTS.md` — CI-01, CI-02, CI-03 requirement text and traceability

### CI / workflow surface (the files this phase touches or observes)
- `.github/workflows/ci.yml` — matrix (3-OS × py3.12/3.13), lint, type-check, coverage, build, integration; triggers `[main, develop]` + `workflow_dispatch`
- `.github/workflows/docs.yml` — docs-multilang HTML + `docs-pdf` compile; triggers push `main` / tags `v*` / PR `main` (no `workflow_dispatch`)
- `.github/workflows/drift.yml` — weekly `uv lock --upgrade` forward-drift detector (advisory, not required)
- `.github/dependabot.yml` — `sphinx-typst-stack` group (patterns `sphinx*`/`docutils*`/`typst*`)
- `.github/workflows/release.yml` — referenced by Phase 10 (version-verify + PyPI publish); out of scope here

### Smoke-test prior art (reuse pattern for CI-02)
- `tests/test_pdf_render_gate.py` — Phase 8.1 D-04 gate: sphinx-build → `typst.compile()` → pypdf text-extraction; **admonition/gentle-clues-only** fixture (the coverage gap D-04 addresses)
- `tests/test_preview_version_sync.py` — the internal-only 3-way version-sync test whose gap CI-02 closes (proves the 3 files *agree*, not that they *compile*)
- `tests/fixtures/admonition_render_gate/` — existing minimal fixture project to model the smoke fixture on
- `pyproject.toml` (deps + `[tool.pytest.ini_options]` markers) — runtime ceilings already at new majors; `slow` marker available

### Package/version context (locked upstream; do not re-decide)
- `.planning/PROJECT.md` §Context — `kai` root cause = mitex (fixed 0.2.6+, bumped to 0.2.7 in Phase 7); codly 1.3.0 at registry ceiling
- `typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ` — the 3 `@preview` version-sync sites (unchanged this phase)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/test_pdf_render_gate.py` + `tests/fixtures/admonition_render_gate/`: the exact sphinx-build → `typst.compile()` → assert pattern the CI-02 smoke should reuse; extend the fixture to touch codly / codly-languages / mitex / gentle-clues (not just admonitions).
- `tox -e docs-pdf`: full-docs real compile that already exercises all four packages, but only runs in `docs.yml` (main/PR/tags) — heavier than a smoke; useful as a secondary confirmation, not the fast guard.

### Established Patterns
- CI observation is PR-gated: `ci.yml`/`docs.yml` fire on `pull_request: [main]`; main branch protection requires ubuntu 3.12–3.13 + Lint/Type/Coverage/Build green before merge. `docs.yml` build-docs runs on the PR but may not be a *required* check — it still executes and can be observed.
- Matrix tests run `tox -e py312/py313` → `pytest tests/`; any pytest-based smoke lands in all 3 OS automatically (skipif guards handle missing typst/pypdf, but both are present under `--extra dev`).
- Milestone git model (v0.5.0): all phase work accumulates on `release/v0.5.0`, `main` untouched; single release PR at the end. (Contrast v0.4.4, which did per-phase PRs to main — appropriate there because each phase left main releasable; inappropriate here because intermediate states were deliberately red, e.g. Phase 6 pre-`kai`-fix.)

### Integration Points
- New smoke test connects into either `ci.yml` (matrix `pytest tests/`) or a dedicated job/step; no new workflow file required.
- CI-03 touches at most `.github/dependabot.yml` / `.github/workflows/drift.yml`; pyproject ceilings are already correct.

</code_context>

<specifics>
## Specific Ideas

- The user explicitly reasoned through and confirmed the PR-based observation model: "PR を出せば PR 上でテストが走る → 観測できる." The team's mental model is "milestone 完了時にリリース PR" — Phase 9 opens that PR to observe (variant (a)); Phase 10 adds the version bump to the same PR and merges.
- CI-02's mitex-coverage point was surfaced as the one substantive smoke-test concern and explicitly approved by the user for the researcher/planner to implement.

</specifics>

<deferred>
## Deferred Ideas

- **XOS-01** (cross-OS docs-PDF CI on macOS/Windows) — already deferred to v2 at v0.5.0 scoping; docs-PDF stays ubuntu-only. Not in Phase 9.
- **FWD-03 → CFG-01** (user-configurable `@preview` versions) — deferred to v2.
- Making `drift.yml` a required check — explicitly kept advisory-only; revisit separately, not this phase.

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 9-green-ci-matrix-smoke-test-guardrails*
*Context gathered: 2026-07-11*
