# Phase 2: Verify the Green Baseline - Context

**Gathered:** 2026-07-04
**Status:** Ready for planning
**Source:** plan-phase inline context capture (verification-approach decision + version-sync deliverable)

<domain>
## Phase Boundary

Confirm the Phase 1 pin turns **every previously-red CI job green across the full
platform/Python matrix**, and protect the 3-way `@preview` version-sync hazard with
an automated test rather than manual memory. This phase is verification-first: its
core work is *observing* CI go green, with **one** concrete code deliverable (the
version-sync guard test).

**In scope:** the 12-job test matrix green (TEST-01), the 7 PDF-compilation
integration tests green (TEST-02), coverage job passing + Codecov upload (TEST-03),
Type Check + Build Package staying green with no regression (TEST-04), `docs.yml`
completing end-to-end including the multi-language PDF-copy step (DOCS-01), and a new
automated `@preview` version-sync test (ROADMAP §Phase 2 success criterion 5).

**Out of scope (other phases / milestone):** fixing any *new* failure unrelated to
the Phase 1 pin (surface it as a finding — do not silently expand scope), Python-floor
modernization 3.10–3.13 (Phase 3), dev-tooling / GitHub Actions version bumps
(Phase 4), durability guardrails incl. `uv sync --locked` / weekly drift job /
dependabot grouping / CI badge (Phase 5), and making the `@preview` versions
configurable (v2 / FWD-03 — this phase adds the *guard test only*, not configurability).
</domain>

<decisions>
## Implementation Decisions

### Verification Method
- **D-01:** Confirm green via **push + observe GitHub Actions** — this is the
  authoritative path and the phase's definition of done. The success criteria name
  Actions outcomes (12 matrix jobs across 3 OS, Codecov upload, `docs.yml`
  end-to-end) that a local `tox` run **cannot** fully prove (macOS/Windows runners,
  Codecov upload, Pages/artifact steps). Local `tox`/`pytest` runs are allowed as a
  cheap pre-check, but the phase is only "done" when the real Actions runs are
  observed green (e.g. via `gh run watch` / `gh run view`).

### CI Trigger Mechanics
- **D-02:** CI only fires on the right refs: `ci.yml` triggers on `push` to
  `main`/`develop` and PRs targeting them; `docs.yml` triggers on `push` to `main`
  and PRs targeting `main`. To exercise **all** required jobs — including `docs.yml`
  (DOCS-01) — **without** side effects, the recommended trigger is a **PR targeting
  `main`** from a work branch: PR mode runs `ci.yml` + `docs.yml` but skips the
  Pages-deploy / release-upload steps (those are gated on push-to-`main` / `v*`
  tags). A direct push to `main` also works but additionally fires the GitHub Pages
  deploy. The exact tactic (PR vs. develop push) is Claude's discretion **provided
  it exercises `docs.yml` for DOCS-01**.

### `@preview` Version-Sync Guard Test
- **D-03:** Add a **new automated test** asserting the four `@preview` package
  versions — `codly:1.3.0`, `codly-languages:0.1.1`, `mitex:0.2.4`,
  `gentle-clues:1.2.0` — declared in `typsphinx/writer.py`, `typsphinx/template_engine.py`,
  and `typsphinx/templates/base.typ` are **identical across all three files**, so a
  future desync fails CI loudly instead of silently. It must live in `tests/` and run
  under the standard `pytest` collection (so the matrix job TEST-01 and the coverage
  job TEST-03 both execute it — no separate CI wiring needed).

### Scope / Attribution Discipline
- **D-04 [informational]:** If the observed CI reveals a **new** red that is not
  attributable to the Phase 1 pin, surface it explicitly (finding / blocker) rather
  than silently patching it — Phase 2's job is to *confirm the pin's effect*
  unambiguously. A genuinely new, in-scope regression in a Phase-2-owned check (e.g.
  the sync test itself) is fixable here; unrelated pre-existing debt is not.

### Claude's Discretion
- Exact version-sync test file location/name and extraction technique — regex over
  the `@preview/<pkg>:<version>` string literals, or importing the writer /
  template-engine import-builder functions and diffing; `base.typ` is a static
  template parsed as text.
- Precise plan decomposition (how many plans, ordering of "write sync test" vs.
  "run local pre-check" vs. "push + observe").
- Exact `gh` invocations and whether a work branch + PR or a `develop` push is used
  (subject to D-02's "must exercise `docs.yml`").
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & Scope (locked)
- `.planning/REQUIREMENTS.md` §Tests & Coverage / §Docs Build — TEST-01…04, DOCS-01
  exact acceptance text.
- `.planning/ROADMAP.md` §Phase 2 — goal + 5 success criteria (criterion 5 = the
  version-sync test).
- `.planning/PROJECT.md` §Key Decisions — Phase 1 outcome (the empirically-confirmed
  typst patch and whether the sphinx/docutils ceilings were load-bearing).
- `.planning/STATE.md` §Accumulated Context — pre-Phase decisions carried forward.

### CI / Docs Surfaces Verified (read to enumerate jobs + trigger rules)
- `.github/workflows/ci.yml` — 6 jobs: `test` (matrix 3 OS × Python 3.9–3.12 = 12,
  `tox -e py{ver}`), `lint` (`tox -e lint`), `type-check` (`tox -e type`), `coverage`
  (`tox -e cov -- --cov-report=xml` → Codecov, `fail_ci_if_error: false`), `build`
  (`uv build` + `twine check`), `integration` (basic/advanced examples).
- `.github/workflows/docs.yml` — `tox -e docs-multilang`, `tox -e docs-pdf`, then the
  `cp docs/_build/pdf/*.pdf docs/_build/multilang/en/` step (DOCS-01's previously-failing copy).
- `tox.ini` — env definitions the CI jobs invoke (`py39`–`py312`, `lint`, `type`,
  `cov`, `docs-pdf`, `docs-multilang`).

### The 3-Way `@preview` Version Sync Hazard (D-03 target)
- `typsphinx/writer.py` (≈ lines 94–97) — hardcoded `@preview` versions.
- `typsphinx/template_engine.py` (≈ lines 313–316) — same hardcoded versions.
- `typsphinx/templates/base.typ` (≈ lines 8–19) — same `@preview` versions in the template.

### The 7 PDF-Compilation Integration Tests (TEST-02)
- `tests/test_integration_advanced.py::TestPDFGenerationIntegration`
- `tests/test_integration_nested_toctree.py::TestE2ETypstCompilation`
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- All `@preview` versions are currently **in sync** (codly 1.3.0, codly-languages
  0.1.1, mitex 0.2.4, gentle-clues 1.2.0) — the D-03 test should pass on first run
  and only fail on a *future* desync.
- `tox.ini` uses `runner = uv-venv-lock-runner`, so every env resolves from `uv.lock`
  (Phase 1's pins already propagate to the test/cov/docs envs).

### Integration Points / Gotchas
- The coverage job sets `fail_ci_if_error: false` and needs the `CODECOV_TOKEN`
  secret — so the job **passes even if the Codecov upload is skipped/unauthenticated**.
  TEST-03's "uploads to Codecov" is therefore best-effort at the job level; treat the
  job going green (with an upload attempt) as the pass condition, and note if the token
  is absent.
- The `test` matrix is currently Python **3.9–3.12** (Phase 3 modernizes to 3.10–3.13).
  Phase 2 verifies the **current** matrix — do not pre-empt the Python bump here.
- The 7 PDF integration tests require the `typst` binary to actually compile; they are
  exactly the tests that were red from the `kai` break and must now be green.
</code_context>

<specifics>
## Specific Ideas

- The `docs.yml` PDF-copy step failed previously because `tox -e docs-pdf` produced
  **no** PDF (the `kai` break aborted compilation), so `cp docs/_build/pdf/*.pdf`
  errored on a missing file. Post-pin, `docs-pdf` should emit a PDF and the copy
  should succeed — DOCS-01 verifies this end-to-end.
- User decision (this phase): push + observe is the authoritative confirmation; a
  local `tox` pre-check first is welcome but is not sufficient on its own.
</specifics>

<deferred>
## Deferred Ideas

- **FWD-03** (make `@preview` versions configurable / single source of truth) — v2.
  Phase 2 adds only the *guard test* over the existing 3-way duplication; it does not
  refactor the duplication away.
</deferred>

---

*Phase: 2-Verify the Green Baseline*
*Context gathered: 2026-07-04 via plan-phase inline capture*
