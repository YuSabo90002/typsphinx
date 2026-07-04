# Phase 1: Pin Runtime Dependencies to Known-Good - Context

**Gathered:** 2026-07-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Pin the runtime dependency graph (`typst`, `sphinx`, `docutils`) back to a
reproducible, empirically-confirmed, mutually-compatible combination, and make
the tree lint-clean. This is the actual bug fix — it lands **alone** so a
red/green CI result is unambiguous.

**In scope:** `pyproject.toml` runtime pins (PIN-01/02), `uv.lock` regeneration
(PIN-03), `tox.ini` dep-ceiling mirroring (PIN-04), `sphinx-testing` removal
(PIN-05), empirical typst-patch confirmation + documentation (PIN-06),
`black`/`ruff` clean on the full tree (LINT-01/02).

**Out of scope (other phases / milestone):** CI-green verification across the
full matrix (Phase 2), the 3-way `@preview` sync test (Phase 2), Python-floor
modernization 3.10–3.13 (Phase 3), dev-tooling / GitHub Actions bumps
(Phase 4), durability guardrails incl. `uv sync --locked` / dependabot / badge
(Phase 5), and any forward-port to sphinx 9 / typst 0.15 / configurable
`@preview` versions (v2, deferred).
</domain>

<decisions>
## Implementation Decisions

### Pin Expression Style
- **D-01:** In `pyproject.toml`, add **upper bounds only** and keep existing
  floors: `typst>=0.14.1,<0.15`, `sphinx>=5.0,<9`, `docutils>=0.18,<0.22`. Do
  **not** raise floors and do **not** pin `typst==0.14.x` exactly in
  `pyproject.toml`.
- **D-02:** Strict reproducibility is carried by the regenerated `uv.lock`, not
  by exact `==` pins in `pyproject.toml`. `pyproject.toml` expresses the
  *compatible range*; `uv.lock` captures the exact resolved patch. (Lock
  currency is later enforced by DUR-01 in Phase 5, so a range here is safe.)

### PIN-06 — Load-Bearing Determination
- **D-03:** Apply all three ceilings per PIN-02 (they are required regardless).
  **Additionally**, empirically verify whether `typst<0.15` **alone** turns the
  `docs-pdf` target green — i.e. determine whether the `sphinx<9` /
  `docutils<0.22` ceilings are load-bearing or precautionary — and record that
  finding in `PROJECT.md`'s Key Decisions table alongside the confirmed-good
  typst patch (and any rejected candidates).

### Commit / Plan Granularity
- **D-04:** Land the **PIN change and the `black` reformat as separate commits**
  (separate landing units within Phase 1). This honors ROADMAP's directive that
  the pin fix land alone so a red/green result is unambiguous, and keeps
  `git blame` on the reformatted lines clean. The planner may split these into
  separate plans or separate atomic commits within one plan, but they must not
  be squashed into a single mixed commit.

### Ceiling Target Scope
- **D-05:** Add upper bounds to the **runtime three only** (`typst`, `sphinx`,
  `docutils`). Do **not** add precautionary ceilings to `docs` deps (`furo`,
  `sphinx-autodoc-typehints`, `sphinx-intl`) or `dev` deps in this phase — dev
  tooling is Phase 4, and minimizing the diff keeps the red/green attribution
  clean. `docs.yml` green is confirmed in Phase 2.

### Carried-Forward / Pre-Locked (do not re-open)
- Fallback if no single typst 0.14.x satisfies all four bundled `@preview`
  packages (codly 1.3.0, codly-languages 0.1.1, mitex 0.2.4, gentle-clues
  1.2.0): pin one `@preview` package to an older release rather than moving the
  typst pin. (STATE.md, Blockers/Concerns.)
- `tox.ini` `[testenv]` and `[testenv:type]` dep lists must mirror the same
  ceilings as `pyproject.toml` so no tox env independently re-resolves an
  unbounded version (PIN-04).
- Dead `sphinx-testing` dependency (unused since 2019) is removed from
  `pyproject.toml` **and** `tox.ini` `[testenv] deps` **and** `uv.lock`
  (PIN-05).
- `black --check .` must pass on the **full tree** (reformats
  `docs/build_multilang.py`, `tests/test_config_other_options.py`,
  `tests/test_config_toctree_defaults.py`); `ruff` clean on the full tree
  (LINT-01/02).

### Claude's Discretion
- Exact `typst` patch within `0.14.x` (empirical — the planner/executor
  confirms in CI; not assumed at plan time).
- Precise plan decomposition (how many plans, ordering of pin vs lint within the
  separate-commit constraint of D-04).
- Mechanical details of `uv.lock` regeneration command invocation.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & Scope (locked)
- `.planning/REQUIREMENTS.md` §Dependency Pinning / Lint & Format — PIN-01…06,
  LINT-01/02 exact acceptance text for this phase.
- `.planning/ROADMAP.md` §Phase 1 — goal + 5 success criteria (what must be TRUE).
- `.planning/PROJECT.md` §Context / Key Decisions — failure evidence (CI run
  2026-07-04), the `kai` origin analysis, and the decision table to append the
  confirmed typst patch + PIN-06 finding into.
- `.planning/STATE.md` §Accumulated Context — pre-Phase-1 decisions and the two
  open Phase-1 blockers (typst patch empiricism; ceiling load-bearing question).

### The 3-Way `@preview` Version Sync Hazard (keep in sync when pinning)
- `typsphinx/writer.py` (≈ lines 94–97) — hardcoded `@preview` package versions.
- `typsphinx/template_engine.py` (≈ lines 313–316) — same hardcoded versions.
- `typsphinx/templates/base.typ` — same `@preview` versions in the template.
- `.planning/codebase/CONCERNS.md` §Tech Debt — documents the hardcoded-version
  hazard and the Typst-version coupling risk. (The automated sync-test that
  guards these three lives in **Phase 2**, not here — but any version change in
  this phase must touch all three consistently.)

### Config Surfaces Touched
- `pyproject.toml` — `[project].dependencies`, `[project.optional-dependencies].dev`.
- `tox.ini` — `[testenv]` and `[testenv:type]` `deps`.
- `uv.lock` — regenerated to match.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Existing `pyproject.toml` already declares `typst>=0.14.1` (floor is correct;
  only the `<0.15` ceiling is missing). `dev` extra already carries
  `sphinx-testing>=1.0` — the exact line to delete for PIN-05.
- `tox.ini` uses `runner = uv-venv-lock-runner` for every env, so all envs
  resolve from `uv.lock` — regenerating the lock propagates the new pins to
  test/type/cov/docs envs automatically. The `[testenv]` and `[testenv:type]`
  `deps` blocks still list `sphinx>=5.0` / `docutils>=0.18` unbounded, which is
  the independent re-resolution path PIN-04 closes.

### Established Patterns
- `@preview` versions are duplicated across three files (writer.py,
  template_engine.py, base.typ) with no single source of truth — this is a known
  landmine (CONCERNS.md). Any package-version fallback (the STATE.md fallback
  path) must edit all three.
- `[tool.black].target-version`, `[tool.ruff].target-version`,
  `[tool.mypy].python_version` currently target `py39`/`3.9` — leave these
  **untouched** this phase (Phase 3 owns the Python-floor bump, PYVER-03).

### Integration Points
- CI (`ci.yml`, `docs.yml`, `release.yml`) drives all checks via tox/uv; this
  phase's pins land in `pyproject.toml` + `uv.lock` + `tox.ini` and are
  *verified* by Phase 2, not this phase.
</code_context>

<specifics>
## Specific Ideas

- The `kai` break is understood as a typst 0.15 ⇄ `@preview/mitex:0.2.4`
  incompatibility (`mitex` uses `kai`, which typst 0.15 turned into a hard
  error). Reverting the compiler to the `0.14.x` line where the bundled packages
  compile is the intended fix — not bumping the packages.
- User accepted all four recommended defaults with no additional constraints —
  open to the standard, minimal-diff approach on each decision.
</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. (Forward-port to sphinx 9 /
typst 0.15, configurable `@preview` versions, dev-tooling bumps, and durability
guardrails are already tracked as v2 / later phases in REQUIREMENTS.md and
ROADMAP.md.)
</deferred>

---

*Phase: 1-Pin Runtime Dependencies to Known-Good*
*Context gathered: 2026-07-04*
