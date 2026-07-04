# Phase 3: Modernize Python Floor (3.10-3.13) - Context

**Gathered:** 2026-07-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Uniformly modernize the supported Python range to **3.10–3.13** across every
configuration surface, landing as **one atomic, CI-verified batch** on top of the
confirmed-green Phase 2 baseline — so any new failure is attributable to the Python
bump alone (drop EOL 3.9, add 3.13).

**In scope (PYVER-01..04):**
- `pyproject.toml`: `requires-python>=3.9` → `>=3.10`; PyPI classifiers (drop
  `3.9`, add `3.13`); `[tool.black] target-version`, `[tool.ruff] target-version`,
  `[tool.mypy] python_version` all aligned to the 3.10 floor (PYVER-01, PYVER-03).
- `ci.yml`: test matrix `['3.9'..'3.12']` → `['3.10'..'3.13']` including the
  `include:` python-version→tox-env mapping (drop `py39`, add `py313`); every
  hardcoded single-version `uv python install 3.11` reconciled with the floor
  (PYVER-02).
- `docs.yml` / `release.yml`: hardcoded single-version Python references
  reconciled with the floor (PYVER-02).
- `tox.ini`: `env_list = py39, py310, py311, py312, …` → `py310, py311, py312,
  py313, …` in lockstep with the CI matrix — no tox env without a CI caller and
  vice versa (PYVER-04).
- Final proof: the full CI matrix green again on 3.10–3.13 (ROADMAP §Phase 3
  success criterion 5).

**Out of scope (other phases / milestone):**
- Dev-tooling floor bumps (black/ruff/tox versions) and GitHub Actions version
  refreshes (`actions/checkout`, `setup-python`, `codecov-action`) — Phase 4
  (TOOL-01/02). This phase only changes Python *target/floor* config, not tool
  *versions*.
- Durability guardrails (`uv sync --locked`, weekly drift job, dependabot
  grouping, CI badge) — Phase 5.
- Any forward-port to sphinx 9 / typst 0.15 / configurable `@preview` versions —
  v2 (deferred).
- Re-verifying anything Phase 2 already proved green on the *current* matrix — this
  phase re-verifies only the *new* 3.10–3.13 matrix.

</domain>

<decisions>
## Implementation Decisions

### Single-Version Job Python Pin (PYVER-02)
- **D-01:** Pin **all single-version jobs to the floor 3.10**. Every hardcoded
  `uv python install 3.11` in `ci.yml` (lint / type-check / coverage / build /
  integration — ~5 occurrences), the `setup-python` `python-version: "3.11"` in
  `docs.yml`, and both `uv python install 3.11` lines in `release.yml` become
  **3.10**. Rationale: the `black`/`ruff` `target-version` (`py310`) and
  `mypy` `python_version` (`3.10`) then agree with the interpreter the tooling
  runs on, and the floor is actually exercised — the cleanest reading of PYVER-02's
  "reconcile with the floor." (Alternatives considered: keep 3.11 = smallest diff
  but leaves tool-config/interpreter mismatch; latest 3.13 = doesn't exercise the
  floor. Both rejected.)

### 3.13 Wheel-Availability Contingency (success criterion 5)
- **D-02:** If any dev/docs dependency (`furo`, `sphinx-autodoc-typehints`,
  `sphinx-intl`, `mypy`, etc.) turns out to **lack a 3.13 wheel**, **pin around it**
  — bump that specific dependency to a 3.13-supporting version to keep the matrix
  complete at 3.10–3.13. Do **not** silently drop 3.13. (Treated as an unlikely
  contingency for 2026 — most are pure-Python or already ship 3.13 wheels.) A
  minimal, targeted dep bump made *for 3.13 support* is in-scope here even though
  general dev-tooling bumps are Phase 4 — the trigger is the Python floor, so it
  belongs to the atomic batch.

### Reformatting from `target-version` Bump (success criterion 5)
- **D-03:** If raising `[tool.black] target-version` to `py310` causes any
  reformatting, **include that reformat in the same atomic batch**. Unlike Phase 1
  (where the `black` reformat was unrelated to the pin, hence split per D-04), here
  the reformat *is* a direct consequence of the Python bump — same root cause, so it
  stays in the one batch. (Note: `py39`→`py310` typically produces no black output
  change; this only applies if a diff actually appears.)

### Commit / Batch Granularity
- **D-04:** Land as **per-surface commits within a single PR**, not one giant
  commit. Suggested surface split: (1) `pyproject.toml` (requires-python +
  classifiers + tool target-versions), (2) `tox.ini` `env_list`, (3) CI/docs/release
  workflow YAML. ROADMAP's "one atomic batch" is satisfied at the **PR level** — a
  single green CI run over the whole change — while per-surface commits keep
  `git blame` clean and allow targeted partial revert if one surface regresses.

### Carried Forward (do not re-open)
- **Verification = push → observe GitHub Actions** is the authoritative definition
  of done (Phase 2 D-01). Success criterion 5 ("full CI matrix green on 3.10–3.13")
  is an Actions outcome that a local `tox` run cannot fully prove (macOS/Windows
  runners, all matrix lanes). Local `tox`/`pytest` is allowed as a cheap pre-check
  but is not sufficient on its own. The PR-vs-push trigger tactic is Claude's
  discretion provided it exercises the required jobs (`docs.yml` included).
- **Diff-minimization / clean red-green attribution** discipline (Phase 1
  D-04/D-05): touch only the Python-floor surfaces; no unrelated dep or tooling
  changes ride along (those are Phase 4).
- The `@preview` version-sync guard test added in Phase 2 must continue to pass —
  do not disturb it.

### Claude's Discretion
- Exact YAML shape of the `ci.yml` matrix `include:` mapping (add `py313` row,
  remove `py39` row).
- Whether the integration job's example matrix needs any per-version handling
  (currently single-version — pin to 3.10 per D-01).
- Ordering and exact number of the per-surface commits within the single PR.
- Exact `gh` invocations and the work-branch/PR-vs-push trigger tactic (subject to
  the carried-forward "must exercise the required jobs including `docs.yml`").

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & Scope (locked)
- `.planning/REQUIREMENTS.md` §Python Modernization — PYVER-01..04 exact acceptance
  text.
- `.planning/ROADMAP.md` §Phase 3 — goal + 5 success criteria (criterion 5 = full
  matrix green on 3.10–3.13, no reformatting regression, no 3.13 wheel gap).
- `.planning/PROJECT.md` §Key Decisions — "Modernize Python floor to 3.10–3.13"
  and "Defer sphinx 9 / typst 0.15" pre-commitments.
- `.planning/STATE.md` §Accumulated Context — pre-phase decisions carried forward.
- `.planning/phases/02-verify-the-green-baseline/02-CONTEXT.md` — Phase 2 D-01
  (push→observe Actions = done) and the current-matrix job enumeration.

### Config Surfaces To Modernize (read to enumerate every edit site)
- `pyproject.toml` — line 10 `requires-python = ">=3.9"`; lines 16–24 classifiers
  (`3.9`..`3.12`); `[tool.black]` line 87 `target-version = ["py39"..."py312"]`;
  `[tool.ruff]` line 102 `target-version = "py39"`; `[tool.mypy]` line 119
  `python_version = "3.9"`.
- `.github/workflows/ci.yml` — line 18 matrix `python-version`; lines 19–27
  `include:` python-version→tox-env mapping; single-version `uv python install 3.11`
  at lines 38 (matrix — uses `${{ matrix.python-version }}`, leave), 68, 89, 110,
  144, 176 (the hardcoded `3.11` ones → 3.10 per D-01).
- `.github/workflows/docs.yml` — line 24 `python-version: "3.11"` (setup-python)
  → 3.10.
- `.github/workflows/release.yml` — lines 33, 86 `uv python install 3.11` → 3.10.
- `tox.ini` — line 2 `env_list = py39, py310, py311, py312, lint, type, cov, docs`
  → `py310, py311, py312, py313, …`.

### Guard Not To Break
- `typsphinx/writer.py`, `typsphinx/template_engine.py`,
  `typsphinx/templates/base.typ` + the Phase 2 `@preview` version-sync test — must
  stay green (unaffected by a Python bump, but confirm).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tox.ini` uses `runner = uv-venv-lock-runner`, so each env resolves from
  `uv.lock`. Adding `py313` means the resolver must produce a clean 3.13 solution —
  `uv.lock` regeneration may be needed (verify it already covers 3.13 markers).
- The `ci.yml` matrix already uses an `include:` block mapping
  `python-version` → dotless `tox-env` (added in Phase 2 gap-closure). Extend that
  same pattern: add the `3.13 → py313` row, drop the `3.9 → py39` row. Do **not**
  reintroduce the dotted-vs-dotless mismatch that broke TEST-01 in Phase 2.

### Established Patterns
- Single-version jobs currently standardize on `3.11`; D-01 restandardizes them on
  `3.10`. Keep them uniform (one floor value everywhere) so there is a single knob.
- Phase 1/2 kept diffs minimal and attribution clean — mirror that: this batch
  touches Python-floor config only.

### Integration Points / Gotchas
- The coverage job sets `fail_ci_if_error: false` and needs `CODECOV_TOKEN` — the
  job passes even if the upload is skipped (carried over from Phase 2). Not a
  Phase-3 concern beyond keeping the job green on 3.10.
- The 7 PDF-compilation integration tests need the `typst` binary to compile; they
  ran green in Phase 2 on the old matrix and must stay green on the new one across
  all OSes.
- Watch for a **3.13 wheel gap** in dev/docs deps and a **black reformat** from the
  `target-version` bump — both are explicit success-criterion-5 risks (handled by
  D-02 and D-03 respectively).

</code_context>

<specifics>
## Specific Ideas

- "Reconcile with the floor" (PYVER-02) is interpreted concretely as **set every
  single-version job to 3.10** — not merely "≥3.10 is fine." One floor value across
  all surfaces, no lingering 3.11.
- The atomic-batch requirement is honored at the **PR** level (one green CI run),
  which is what makes "any new failure is attributable to the Python bump alone"
  true — per-surface commits inside that PR are for blame/revert hygiene only.

</specifics>

<deferred>
## Deferred Ideas

- Dev-tooling floor bumps and GitHub Actions version refreshes — Phase 4
  (TOOL-01/02). Only a *targeted* dep bump strictly required for 3.13 wheel support
  (D-02) may ride in Phase 3; general "freshen the tooling" work does not.
- Durability guardrails (`uv sync --locked`, weekly drift job, dependabot grouping,
  CI badge) — Phase 5.

None else — discussion stayed within phase scope.

</deferred>

---

*Phase: 3-Modernize Python Floor (3.10-3.13)*
*Context gathered: 2026-07-04*
