# Phase 4: Refresh Dev Tooling - Context

**Gathered:** 2026-07-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Conservatively refresh **dev-tooling floors** (black / ruff / tox — plus a
deliberate, guarded posture for pytest / mypy) and **verify GitHub Actions
versions**, landing on top of the confirmed-green Phase 3 baseline so any new
failure is attributable to the tooling refresh alone. Close the phase with an
observed green CI run.

**In scope (TOOL-01, TOOL-02):**
- `pyproject.toml [project.optional-dependencies] dev` and `tox.ini` per-env
  `deps` (lint=black/ruff, type=mypy, testenv=pytest): bump floors and add
  upper bounds, kept in lockstep across both surfaces.
- Regenerate `uv.lock` minimal-diff to match the new constraints.
- Verify GitHub Actions versions for hosted-runner compatibility (no yaml edits
  expected — already at latest majors).
- Fold in the Phase-3 leftover: remove the two lingering `Python 3.9`
  references in `README.md` and update the stale ruff `UP035`/`UP006` comment
  text.
- Final proof: an observed green `ci.yml` (full 3.10–3.13 matrix + lint / type /
  coverage / build / integration) and `docs.yml` run on a PR targeting `main`.

**Out of scope (other phases / milestone):**
- SHA-pinning GitHub Actions to commit hashes (supply-chain hardening) — deferred
  to Phase 5 (durability guardrails).
- `uv sync --locked` gate, weekly drift job, dependabot grouping, CI badge —
  Phase 5.
- Jumping pytest / mypy to a new major beyond what CI already proves green — this
  cycle stays under the next major (see D-01).
- Any forward-port to sphinx 9 / typst 0.15 / configurable `@preview` versions —
  deferred to a future milestone.

</domain>

<decisions>
## Implementation Decisions

### pytest / mypy posture (TOOL-01)
- **D-01:** **Accept the already-green pytest 9.1.1 / mypy 2.1.0 as known-good;
  do NOT roll back to the requirement's literal `pytest~=8.4` / `mypy>=1.13,<2.0`.**
  Ground truth: `uv.lock` already resolves pytest 9.1.1 and mypy 2.1.0, and
  Phase 3's PR #104 CI (run 28709253590) went green on exactly that set. The
  requirement's caution was written before that green was observed; rolling back
  now would *reduce* the empirically-confirmed known-good set and add churn.
  Instead, honor the *spirit* of TOOL-01 ("avoid risky major-version flips") by
  raising the floors to the resolved versions and adding a **next-major ceiling**:
  `pytest>=8.4,<10` (or `>=9,<10`) and `mypy>=1.13,<3.0` (i.e. `<3`). This guards
  the next major flip while keeping the green baseline intact.
  - **Note for planner:** This is a deliberate, user-owned deviation from the
    literal wording of TOOL-01. Record it in PROJECT.md's Key Decisions table.
    The ceilings must not force a downgrade of the currently-resolved versions
    (9.1.1 < 10, 2.1.0 < 3 — both satisfied).

### Bound style for dev-tool floors (TOOL-01)
- **D-02:** **All refreshed dev tools get `floor + <next-major` upper bounds**,
  matching Phase 1's defensive pinning of runtime deps and the milestone's
  anti-drift theme — not bare `>=` floors. Apply to black, ruff, tox (and the
  pytest/mypy ceilings from D-01). Floors bump to the currently-resolved versions:
  black `>=26,<27` (resolved 26.5.1), ruff `>=0.15,<0.16` (resolved 0.15.20; ruff
  is 0.x so the "next-major" ceiling is the next 0.x minor), tox `>=4.56,<5`
  (resolved 4.56.1). Planner to pick the exact ceiling boundaries; the *rule* is
  floor-at-resolved + one guard ceiling.
- **D-02b:** These constraints live in **two surfaces that must stay in lockstep**:
  `pyproject.toml [project.optional-dependencies] dev` AND `tox.ini`'s per-env
  `deps` (`[testenv]` pytest, `[testenv:lint]` black/ruff, `[testenv:type]` mypy).
  Bump both together (established Phase 1 tox-mirror pattern) so there is no
  independent unbounded re-resolution path.

### GitHub Actions (TOOL-02)
- **D-03:** **Verify-only — no yaml edits.** All actions are already at their
  latest majors (`actions/checkout@v6`, `actions/setup-python@v6`,
  `astral-sh/setup-uv@v7`, `actions/upload-artifact@v5`, `codecov/codecov-action@v5`).
  TOOL-02 is satisfied by confirming hosted-runner compatibility; the phase makes
  no workflow-version changes. SHA-pinning is explicitly deferred to Phase 5.

### Python 3.9 cleanup (Phase 3 leftover, folded in)
- **D-04:** **Remove the last `Python 3.9` references from `README.md`** — line 36
  ("Python 3.9 or higher") and line 323 ("Python: 3.9+") → `3.10`. Also update the
  stale ruff comment text on `pyproject.toml` `UP035`/`UP006` ("Python 3.9+
  support"). Verified: the CI test matrix, PyPI classifiers, `tox.ini` env_list,
  and black/ruff/mypy target-versions already contain **no** 3.9 (Phase 3 removed
  them); README + these two comment strings are the only survivors. This is a small
  related doc fix folded into the tooling PR, not new scope.

### Verification gate (SC3)
- **D-05:** **Push a PR targeting `main` and observe an actual CI run** (Phase 2/3
  `push → observe = done` pattern), not local-tox-only. Rationale: regenerating
  `uv.lock` after the floor/ceiling changes can shift transitive deps, so an
  observed `ci.yml` (3.10–3.13 matrix + lint/type/coverage/build/integration) and
  `docs.yml` green is the milestone-consistent proof.

### Commit / batch granularity (carried forward)
- **D-06:** Land as **per-surface commits within a single PR** (Phase 3 D-04
  pattern): e.g. (1) `pyproject.toml` dev deps + regenerated `uv.lock`, (2)
  `tox.ini` env deps, (3) README + ruff comment cleanup. Keep the `uv.lock`
  regeneration minimal-diff.

### Claude's Discretion
- Exact ceiling boundary syntax for each tool (`~=` vs explicit `>=x,<y`) — planner
  picks, honoring D-02's floor-at-resolved + one guard-ceiling rule.
- Whether a black floor bump triggers any reformat: resolved black is already
  26.5.1 and the tree was formatted green under it in Phase 3, so raising only the
  *floor* to `>=26` should produce no new reformat. If a diff unexpectedly appears,
  include it in the same batch (Phase 3 D-03 precedent).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — TOOL-01 (dev-tooling floors; note the D-01
  deliberate deviation from the literal `pytest~=8.4` / `mypy<2.0` wording),
  TOOL-02 (GitHub Actions versions).
- `.planning/ROADMAP.md` §Phase 4 — goal + 3 success criteria.
- `.planning/PROJECT.md` — Key Decisions table (Phase 1 pinning precedent, Phase 3
  green baseline); D-01 must be logged here at phase transition.

### Config surfaces to edit
- `pyproject.toml` — `[project.optional-dependencies] dev` (lines ~35-48) floors;
  ruff `UP035`/`UP006` comment text (lines ~111-112).
- `tox.ini` — `[testenv]` pytest, `[testenv:lint]` black/ruff, `[testenv:type]`
  mypy `deps` lists.
- `README.md` — lines 36 and 323 (Python 3.9 references).
- `.github/workflows/ci.yml`, `docs.yml`, `release.yml` — verify action versions
  only (no edits expected).

### Prior-phase context (patterns carried forward)
- `.planning/phases/01-pin-runtime-dependencies-to-known-good/01-CONTEXT.md` —
  tox↔pyproject mirror + upper-bound pinning precedent.
- `.planning/phases/03-modernize-python-floor-3-10-3-13/03-CONTEXT.md` — per-surface
  commits (D-04), reformat-in-batch (D-03), push→observe gate.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Phase 2/3 push→observe workflow on a PR targeting `main` — the established,
  cheap way to get an observed green CI run; reuse verbatim for D-05.
- `runner = uv-venv-lock-runner` in every tox env — tox resolves from `uv.lock`,
  so the lock regeneration is what actually pins the tooling versions CI runs.

### Established Patterns
- Dev-tooling constraints are duplicated across `pyproject.toml [dev]` and
  `tox.ini` per-env `deps`; both must move together (D-02b).
- Upper-bound pinning (`>=x,<next-major`) is the project's chosen defense against
  silent drift (Phase 1 runtime deps → now extended to dev tools in D-02).

### Integration Points
- `uv.lock` is the single source of truth CI/tox resolve from — every constraint
  change must be followed by a minimal-diff `uv.lock` regeneration.

</code_context>

<specifics>
## Specific Ideas

- Currently-resolved dev-tool versions (targets for the new floors): black 26.5.1,
  ruff 0.15.20, tox 4.56.1, tox-uv 1.35.2, pytest 9.1.1, mypy 2.1.0, pre-commit
  4.6.0.
- The `kai`-class break origin (runtime typst pin) is unrelated to this phase —
  dev-tooling refresh does not touch runtime deps.

</specifics>

<deferred>
## Deferred Ideas

- **SHA-pin GitHub Actions to commit hashes** (supply-chain hardening) → Phase 5
  (durability guardrails). Raised while confirming actions are already at latest
  majors; hardening beyond version-currency belongs with the guardrails work.

</deferred>

---

*Phase: 4-refresh-dev-tooling*
*Context gathered: 2026-07-04*
