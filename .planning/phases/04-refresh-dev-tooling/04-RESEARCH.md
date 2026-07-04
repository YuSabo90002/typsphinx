# Phase 4: Refresh Dev Tooling - Research

**Researched:** 2026-07-05
**Domain:** Python dev-tooling dependency floors (black/ruff/tox/pytest/mypy) + GitHub Actions version currency, on a `uv.lock`-driven tox project
**Confidence:** HIGH (all target versions and file locations verified directly against the repo and live registries; one MEDIUM-confidence finding requires planner/user attention — see the GitHub Actions section below)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01 (pytest/mypy posture):** Accept the already-green pytest 9.1.1 / mypy 2.1.0 as known-good; do NOT roll back to the requirement's literal `pytest~=8.4` / `mypy>=1.13,<2.0`. `uv.lock` already resolves pytest 9.1.1 and mypy 2.1.0, and Phase 3's PR #104 CI (run 28709253590) went green on exactly that set. Honor the spirit of TOOL-01 by raising floors to the resolved versions and adding a next-major ceiling: `pytest>=8.4,<10` (or `>=9,<10`) and `mypy>=1.13,<3.0`. Ceilings must not force a downgrade of the currently-resolved versions. This is a deliberate, user-owned deviation from the literal wording of TOOL-01 — record it in PROJECT.md's Key Decisions table.
- **D-02 (bound style for dev-tool floors):** All refreshed dev tools get `floor + <next-major` upper bounds, matching Phase 1's defensive pinning of runtime deps. Apply to black, ruff, tox (and the pytest/mypy ceilings from D-01). Floors bump to currently-resolved versions: black `>=26,<27` (resolved 26.5.1), ruff `>=0.15,<0.16` (resolved 0.15.20; ruff is 0.x so "next-major" ceiling is the next 0.x minor), tox `>=4.56,<5` (resolved 4.56.1). Planner picks exact ceiling boundaries; the rule is floor-at-resolved + one guard ceiling.
- **D-02b (two-surface lockstep):** These constraints live in two surfaces that must stay in lockstep: `pyproject.toml [project.optional-dependencies] dev` AND `tox.ini`'s per-env `deps` (`[testenv]` pytest, `[testenv:lint]` black/ruff, `[testenv:type]` mypy). Bump both together (established Phase 1 tox-mirror pattern) so there is no independent unbounded re-resolution path.
- **D-03 (GitHub Actions):** Verify-only — no yaml edits. All actions are already at their latest majors (`actions/checkout@v6`, `actions/setup-python@v6`, `astral-sh/setup-uv@v7`, `actions/upload-artifact@v5`, `codecov/codecov-action@v5`). TOOL-02 is satisfied by confirming hosted-runner compatibility; the phase makes no workflow-version changes. SHA-pinning is explicitly deferred to Phase 5. **This research found the "already at latest majors" premise no longer holds for 2 of these 6 actions — see the GitHub Actions findings below; this is new evidence for the planner/user to weigh, not an override of D-03.**
- **D-04 (Python 3.9 cleanup):** Remove the last `Python 3.9` references from `README.md` — line 36 ("Python 3.9 or higher") and line 323 ("Python: 3.9+") → `3.10`. Also update the stale ruff comment text on `pyproject.toml` `UP035`/`UP006` ("Python 3.9+ support"). Verified: CI test matrix, PyPI classifiers, `tox.ini` env_list, and black/ruff/mypy target-versions already contain no 3.9 (Phase 3 removed them); README + these two comment strings are the only survivors. Small related doc fix folded into the tooling PR, not new scope.
- **D-05 (verification gate / SC3):** Push a PR targeting `main` and observe an actual CI run (Phase 2/3 `push → observe = done` pattern), not local-tox-only. Regenerating `uv.lock` after floor/ceiling changes can shift transitive deps, so an observed `ci.yml` (3.10–3.13 matrix + lint/type/coverage/build/integration) and `docs.yml` green is the milestone-consistent proof.
- **D-06 (commit/batch granularity):** Land as per-surface commits within a single PR (Phase 3 D-04 pattern): e.g. (1) `pyproject.toml` dev deps + regenerated `uv.lock`, (2) `tox.ini` env deps, (3) README + ruff comment cleanup. Keep the `uv.lock` regeneration minimal-diff.

### Claude's Discretion

- Exact ceiling boundary syntax for each tool (`~=` vs explicit `>=x,<y`) — planner picks, honoring D-02's floor-at-resolved + one guard-ceiling rule.
- Whether a black floor bump triggers any reformat: resolved black is already 26.5.1 and the tree was formatted green under it in Phase 3, so raising only the floor to `>=26` should produce no new reformat. If a diff unexpectedly appears, include it in the same batch (Phase 3 D-03 precedent).

### Deferred Ideas (OUT OF SCOPE)

- **SHA-pin GitHub Actions to commit hashes** (supply-chain hardening) → Phase 5 (durability guardrails). Raised while confirming actions are already at latest majors; hardening beyond version-currency belongs with the guardrails work.
- `uv sync --locked` gate, weekly drift job, dependabot grouping, CI badge → Phase 5.
- Jumping pytest/mypy to a new major beyond what CI already proves green — this cycle stays under the next major (D-01).
- Any forward-port to sphinx 9 / typst 0.15 / configurable `@preview` versions → deferred to a future milestone.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|--------------|--------------------|
| TOOL-01 | Dev-tooling floors refreshed conservatively — bump black/ruff/tox; deliberately stay under a new pytest/mypy major this cycle (D-01 supersedes the literal `pytest~=8.4`/`mypy<2.0` wording with a resolved-floor + next-major-ceiling approach) | Standard Stack table gives exact current/new constraint strings per tool, cross-verified against live PyPI; Architecture Patterns section documents the exact two-surface (pyproject.toml + tox.ini) mirror mechanics and the `[testenv:cov]` inheritance gotcha; Open Questions 2-3 flag the two genuinely ambiguous boundary-syntax calls (tox-uv scope, mypy floor value) the planner must resolve |
| TOOL-02 | GitHub Actions versions verified/refreshed (`actions/checkout`, `actions/setup-python`, `codecov/codecov-action`) against hosted-runner compatibility | Live-verified release history + `action.yml` runtime (`runs.using`) for all 6 actions used in this repo; found 4 are fully current/compatible as pinned, but 2 (`upload-artifact@v5`, `download-artifact@v6`) still run Node 20, which GitHub removes from hosted runners 2026-09-16 — Open Question 1 and Common Pitfall 5 give the planner the exact decision to make and why it matters for "hosted-runner compatibility" specifically (not just semver currency) |
</phase_requirements>

## Summary

This phase is narrow and mechanical: bump five dev-tool version constraints across two lockstep surfaces (`pyproject.toml [project.optional-dependencies] dev` and `tox.ini` per-env `deps`), regenerate `uv.lock` with a minimal diff, fix three leftover Python-3.9 text references, and prove it all with an observed green CI run. CONTEXT.md's D-01 through D-06 already resolved every substantive question about *what* versions to target and *how* to structure the ceilings — this research does not revisit those. Its job is to nail down the exact mechanics: precisely which lines change, how `uv-venv-lock-runner` makes `uv.lock` (not the constraint strings) the thing CI actually resolves from, a scoping clarification for which dev deps are and are not in play, and one live-verified discrepancy in CONTEXT.md's GitHub Actions premise that the planner must know about before writing tasks for TOOL-02.

All seven target dev-tool versions (black 26.5.1, ruff 0.15.20, tox 4.56.1, tox-uv 1.35.2, pytest 9.1.1, mypy 2.1.0, pre-commit 4.6.0) were independently re-verified against the live PyPI JSON API today and are still each project's latest published release — CONTEXT.md's version targets are current, not stale. The GitHub Actions picture is more nuanced: two of the six actions used in this repo (`actions/upload-artifact@v5`, `actions/download-artifact@v6`) still run on the **Node 20 runtime, which GitHub is actively deprecating** (Node 20 removed from hosted runners **2026-09-16**, i.e. within this project's likely CI lifetime) — this is new information that revises CONTEXT.md D-03's "already at latest majors, no yaml edits" premise for those two specific actions, even though the other four actions (`checkout@v6`, `setup-python@v6`, `setup-uv@v7`, `codecov-action@v5`) remain fine as pinned.

**Primary recommendation:** Execute D-01–D-06 exactly as scoped for the dev-tool floor/ceiling work (pyproject.toml + tox.ini, in that per-surface commit order), fold in the README/ruff-comment cleanup, and additionally raise a scoped, low-risk version bump for `actions/upload-artifact` (v5→v7) and `actions/download-artifact` (v6→v8) as part of TOOL-02, since these are the two actions with a genuine (not merely "newer major exists") hosted-runner-compatibility deadline. Treat this as new evidence for the planner/user to confirm — not a unilateral override of the locked D-03 decision.

## Architectural Responsibility Map

This phase touches build/tooling configuration, not application runtime tiers. Mapped to the config surfaces that actually own each capability:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Dev-tool version constraints (black/ruff/tox/pytest/mypy) | `pyproject.toml [project.optional-dependencies] dev` | `tox.ini` per-env `deps` (mirror) | pyproject is the package's canonical dependency declaration; tox.ini duplicates it per-env so `tox -e lint`/`type`/`py3xx` don't independently re-resolve unbounded versions (D-02b) |
| Actual pinned versions resolved into CI | `uv.lock` | — | Every tox env uses `runner = uv-venv-lock-runner`; tox does not do its own resolution — it materializes envs from `uv.lock`. The constraint *strings* in pyproject/tox.ini only bound what `uv lock` is allowed to resolve; the lockfile is what CI actually installs |
| Action-runtime hosted-runner compatibility | GitHub Actions workflow files (`.github/workflows/*.yml`) | GitHub-hosted runner (Node.js version) | Each action's `action.yml` declares `runs.using` (e.g. `node20`, `node24`, `composite`); compatibility risk is a function of that runtime declaration vs. GitHub's runner deprecation timeline, not the action's semver major alone |
| CI-observed proof of correctness | GitHub Actions (`ci.yml`, `docs.yml`) via PR to `main` | Local `tox` runs (pre-flight only) | D-05: `uv.lock` regeneration can shift transitive deps unpredictably; only an observed CI run proves the full matrix + lint/type/coverage/build/integration jobs are still green |
| Doc/comment text accuracy (Python 3.9 leftovers) | `README.md`, `pyproject.toml` ruff comment | — | Pure documentation drift, unrelated to dependency resolution; folded in as a small batch per D-04 |

## Standard Stack

### Core (dev-tool floor/ceiling bumps — TOOL-01, D-01/D-02)

| Library | Current constraint | New constraint (recommended) | Resolved version (uv.lock) | Verified current? |
|---------|--------------------|-------------------------------|------------------------------|--------------------|
| black | `>=23.0` | `>=26,<27` | 26.5.1 | [VERIFIED: PyPI registry — pypi.org/pypi/black/json, latest=26.5.1, published 2026-05-18] |
| ruff | `>=0.1.0` | `>=0.15,<0.16` | 0.15.20 | [VERIFIED: PyPI registry — latest=0.15.20, published 2026-06-25] |
| tox | `>=4.0` | `>=4.56,<5` | 4.56.1 | [VERIFIED: PyPI registry — latest=4.56.1, published 2026-06-25] |
| pytest | `>=7.0` | `>=8.4,<10` **or** `>=9,<10` (D-01 offers both; planner picks — see Open Questions) | 9.1.1 | [VERIFIED: PyPI registry — latest=9.1.1, published 2026-06-19] |
| mypy | `>=1.0` | `>=1.13,<3.0` (D-01's literal, single prescribed syntax — floor intentionally NOT raised to 2.1.0; see Open Questions) | 2.1.0 | [VERIFIED: PyPI registry — latest=2.1.0, published 2026-05-11] |

### Supporting (in scope only via tox-mirror requirement, not floor-bumped)

| Library | Purpose | In scope for this phase? |
|---------|---------|---------------------------|
| tox-uv | tox's `uv`-backed runner (`runner = uv-venv-lock-runner`); declared in **both** `pyproject.toml [dev]` (`tox-uv>=1.0`) **and** `tox.ini`'s top-level `[tox] requires = tox-uv>=1.0`) | **Not named in D-02** ("black, ruff, tox"). Resolved at 1.35.2. See Don't-Hand-Roll / Open Questions — this is a genuine 4th mirror point the planner should decide on, not silently skip. |
| pre-commit | Git hook runner | Out of scope — not named in D-02, resolved at 4.6.0, no tox.ini mirror exists for it |
| pytest-cov | Coverage plugin, listed alongside pytest in `[testenv]`/`[testenv:cov]` deps | Out of scope — not named in D-02; leave its `>=4.0` floor untouched |
| twine, build | Packaging/publish tooling in `[dev]` extra only | Out of scope — no tox.ini mirror, not named in D-02 |
| types-docutils | Type stubs, appears in **three** places (see Common Pitfalls) | Out of scope for TOOL-01's tool list, but flagged as a pre-existing drift risk |

### Alternatives Considered

None — CONTEXT.md D-01/D-02 already locked the target tool set and version strategy (floor-at-known-good + next-boundary ceiling, matching the Phase 1 runtime-dependency pinning precedent). No alternative tools or strategies apply.

**Installation / regeneration command:**
```bash
# After editing pyproject.toml [dev] and tox.ini deps in lockstep:
uv lock          # NOT `uv lock --upgrade` — keep the diff minimal (Phase 3 precedent, STATE.md)
git diff uv.lock # confirm only the intended constraint-driven changes appear, no incidental transitive bumps
```

**Version verification performed this session (2026-07-05):** Queried `https://pypi.org/pypi/<name>/json` directly for black, ruff, tox, tox-uv, pytest, mypy, pre-commit. All seven returned the exact version already resolved in `uv.lock`, confirming CONTEXT.md's specifics are still current as of today — no target has moved since context-gathering.

## Package Legitimacy Audit

No *new* packages are being introduced by this phase — all seven tools are pre-existing dev dependencies already resolved in `uv.lock`; this phase only widens/raises their version constraints. Ran the legitimacy gate anyway for completeness:

| Package | Registry | Published (latest) | Downloads | Source Repo | Verdict (seam) | Disposition |
|---------|----------|---------------------|-----------|--------------|-----------------|-------------|
| black | pypi | 2026-05-18 | unknown (seam has no download-stats source) | none returned by seam (actual: github.com/psf/black) | SUS (`unknown-downloads`, `no-repository`) | **Approved — false positive.** `black` is one of the most widely used Python formatters (PSF-maintained); the seam's heuristic lacks a downloads source and mis-resolved the repo URL. |
| ruff | pypi | 2026-06-25 | unknown | docs.astral.sh/ruff | SUS (`too-new`, `unknown-downloads`) | **Approved — false positive.** "Too-new" fires on the *release date* of the current version (routine point release), not on the project's age; ruff is a mainstream, Astral-maintained tool already resolved in the lockfile. |
| tox | pypi | 2026-06-25 | unknown | github.com/tox-dev/tox | SUS (`too-new`, `unknown-downloads`) | **Approved — false positive**, same reasoning. |
| tox-uv | pypi | 2026-05-05 | unknown | github.com/tox-dev/tox-uv | SUS (`unknown-downloads`) | **Approved.** |
| pytest | pypi | 2026-06-19 | unknown | github.com/pytest-dev/pytest | SUS (`too-new`, `unknown-downloads`) | **Approved — false positive**, same reasoning. |
| mypy | pypi | 2026-05-11 | unknown | mypy-lang.org | SUS (`unknown-downloads`) | **Approved.** |
| pre-commit | pypi | 2026-04-21 | unknown | github.com/pre-commit/pre-commit | SUS (`unknown-downloads`) | **Approved.** |

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** all seven flagged by the seam's heuristics, but all seven are dispositioned **Approved** above — the `too-new`/`unknown-downloads` signals are heuristic artifacts (the seam has no PyPI-download-stats source available and treats "most recent release published this year" as a proxy for project age, which misfires for actively-maintained, long-established tools). No `checkpoint:human-verify` is warranted for these; they are already installed, already resolved in `uv.lock`, and independently confirmed via the PyPI registry as each project's current stable release. This is a genuine limitation of the automated heuristic, not a legitimacy concern — document it so the plan-checker doesn't block on it.

## Architecture Patterns

### System Architecture Diagram — constraint flow from source to CI

```
 pyproject.toml [project.optional-dependencies] dev   tox.ini [testenv*] deps
  (black/ruff/tox/pytest/mypy floor+ceiling strings)    (mirrored floor+ceiling strings)
             │                                                    │
             └──────────────────┬─────────────────────────────────┘
                                 ▼
                         `uv lock` (resolver)
                                 │
                                 ▼
                            uv.lock  ◄── single source of truth for exact pinned versions
                                 │
                                 ▼
                  tox invocation: runner = uv-venv-lock-runner
                  (tox does NOT independently resolve — it builds
                   each env's venv directly from uv.lock)
                                 │
                 ┌───────────────┼────────────────┬─────────────────┐
                 ▼               ▼                ▼                 ▼
          [testenv:lint]   [testenv:type]    [testenv] py3.10-3.13   [testenv:cov]
          black --check    mypy typsphinx/    pytest {posargs}       {[testenv]deps}
          ruff check .                                               (inherits testenv
                                                                       deps automatically)
                                 │
                                 ▼
                  GitHub Actions: `uv sync --extra dev` then `uv run tox -e <env>`
                  (ci.yml jobs: test matrix, lint, type-check, coverage, build, integration)
                                 │
                                 ▼
                    Observed green PR run on branch → main (D-05 gate)
```

### Recommended edit sequence (per D-06 per-surface commits)

```
1. pyproject.toml  [project.optional-dependencies] dev  (lines ~36-48)  — bump black/ruff/tox/pytest/mypy strings
   + `uv lock` (minimal diff) regenerate uv.lock
2. tox.ini  [testenv] / [testenv:lint] / [testenv:type] deps            — mirror the same 5 strings
3. README.md lines 36 & 323 + pyproject.toml UP035/UP006 comment text   — Python 3.9 → 3.10 cleanup
```

### Pattern: tox↔pyproject "mirror, don't inherit" for dev tooling

**What:** Both `pyproject.toml [project.optional-dependencies] dev` and `tox.ini`'s per-env `deps=` lists independently spell out the same version constraint string for a given tool (e.g. `black>=26,<27` appears verbatim in both files).
**When to use:** Whenever a dev tool is used by both `uv sync --extra dev` (local/dev install) and a specific tox env (`[testenv:lint]`, `[testenv:type]`, `[testenv]`).
**Why it exists (not DRY, deliberately):** `tox.ini`'s `deps=` for `uv-venv-lock-runner`-backed envs feed into the *same* `uv.lock` resolution, so drift can't silently occur between "what pyproject allows" and "what tox's env believes it needs" — both bound the same lock. Established in Phase 1 (`01-CONTEXT.md`) and reused for Python-version work in Phase 3.
**Example (from this repo, `tox.ini`):**
```ini
# Source: /home/yuta/Documents/typsphinx/tox.ini — verified this session
[testenv:lint]
deps =
    black>=23.0    # → bump to black>=26,<27
    ruff>=0.1.0    # → bump to ruff>=0.15,<0.16
commands =
    black --check .
    ruff check .
```

### Pattern: `[testenv:cov]` inherits from `[testenv]` — do not duplicate

**What:** `tox.ini`'s `[testenv:cov]` deps block is literally `{[testenv]deps}` (a tox variable substitution), not its own list.
**When to use:** When bumping pytest's constraint in `[testenv]`, do **not** also look for a separate pytest line under `[testenv:cov]` — there isn't one; it inherits automatically.
**Example:**
```ini
# Source: /home/yuta/Documents/typsphinx/tox.ini lines 39-44 — verified this session
[testenv:cov]
deps =
    {[testenv]deps}
```

### Anti-Patterns to Avoid
- **Bumping the pyproject.toml `[dev]` floor without touching tox.ini (or vice versa):** creates an unbounded independent re-resolution path in whichever tox env wasn't updated — exactly what D-02b's lockstep rule exists to prevent.
- **Running `uv lock --upgrade` instead of plain `uv lock`:** pulls in unrelated transitive-dependency bumps beyond the intended constraint change, inflating the diff and reintroducing exactly the kind of unreviewed drift this milestone is trying to eliminate. Phase 3 explicitly used plain `uv lock` and verified the diff was constraint-driven only (STATE.md).
- **Treating ruff's `<0.16` ceiling as equivalent to black/tox's "next major" ceiling:** ruff has not reached 1.0 and uses a custom versioning scheme where **the minor version number carries breaking changes** (patch = bug fixes only) [CITED: docs.astral.sh/ruff/versioning]. A `<0.16` ceiling on ruff is the correct analogue of a "next major" ceiling on a post-1.0 tool — don't loosen it to `<1` or `<0.20` under the assumption minor bumps are safe for ruff the way they are for black/tox/pytest/mypy.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Detecting whether the currently-pinned dev-tool versions are still the latest release | A custom script hitting PyPI ad hoc | `pip index versions <pkg>` or the PyPI JSON API (`https://pypi.org/pypi/<pkg>/json`) — both already used this session | Authoritative, zero-dependency, and exactly what was used to verify all 7 targets above |
| Checking whether a GitHub Action's pinned major is still current / uses a soon-to-be-deprecated Node runtime | Guessing from the action's semver alone | `curl https://api.github.com/repos/<org>/<repo>/releases` for the version history, plus fetching the tag's `action.yml` (`raw.githubusercontent.com/<org>/<repo>/<tag>/action.yml`) for the `runs.using` field | Semver major currency and Node-runtime currency are two *different* signals — an action can be "not the latest major" yet fully safe (already on `node24`), or "the pinned major" yet at real risk (still on `node20`, per GitHub's own deprecation timeline). Verified directly this session for all 6 actions in this repo. |

**Key insight:** For this phase, "is this dependency current" has to be checked against *two* independent signals for GitHub Actions specifically — semver-major currency (marketing/feature currency) and Node-runtime currency (hosted-runner compatibility, which is what TOOL-02 actually asks about). CONTEXT.md's D-03 checked only the first signal.

## Common Pitfalls

### Pitfall 1: Assuming "already at latest major" implies "hosted-runner compatible" for GitHub Actions
**What goes wrong:** D-03 states all 6 actions used in this repo are "already at their latest majors" and concludes no yaml edits are needed. Live verification this session shows this premise is **inaccurate for 2 of the 6 actions** — see the dedicated section below.
**Why it happens:** "Latest major" and "hosted-runner compatible" are correlated but not identical; an action can lag its own latest major release yet still be fine (if its currently-pinned major already uses the current Node runtime), or vice versa.
**How to avoid:** Check each action's `runs.using` field in its pinned tag's `action.yml`, not just its release history, against GitHub's published Node-runtime deprecation timeline.
**Warning signs:** Any action pinned to a major that predates a documented platform-wide runtime deprecation announcement.

### Pitfall 2: Forgetting `tox-uv` is itself a mirrored constraint (4th surface, not named in D-02)
**What goes wrong:** A grep for "tox.ini ↔ pyproject.toml mirror" naturally lands on the per-env `deps=` blocks (`[testenv]`, `[testenv:lint]`, `[testenv:type]`) that D-02b explicitly calls out — but `tox-uv>=1.0` *also* appears twice: once in `pyproject.toml [dev]` and once in `tox.ini`'s top-level `[tox] requires = tox-uv>=1.0`. If the planner scopes strictly to "black, ruff, tox" per D-02's literal wording and skips this pair, that's a legitimate reading of the locked decision — but it should be a deliberate skip, not an oversight.
**Why it happens:** `[tox] requires` is a different tox.ini section (governs tox's own bootstrap, not a `[testenv*]` deps list), easy to miss when scanning only `[testenv*]` blocks.
**How to avoid:** Explicitly note in the plan whether tox-uv is in-scope-and-skipped-per-D-02 or in-scope-and-bumped; don't silently do neither.
**Warning signs:** `grep -n "tox-uv" pyproject.toml tox.ini` returns 2 hits with different constraint strings after the phase.

### Pitfall 3: A second, un-mirrored `[dependency-groups] dev` table also exists in `pyproject.toml`
**What goes wrong:** `pyproject.toml` has a **third** dev-dependency surface beyond the two D-02b names: a PEP 735 `[dependency-groups] dev = ["types-docutils>=0.22.2.20251006"]` block (lines 134-137). This is synced automatically by `uv sync` (uv treats the `dev` group as a default group included unless `--no-dev`/`--no-default-groups` is passed) [CITED: docs.astral.sh/uv/concepts/projects/dependencies], so it is live in CI even though every `uv sync` invocation in the workflows uses `--extra dev`/`--extra docs`, never `--group`.
**Why it happens:** uv's dependency-groups feature is additive to extras by default, not a Poetry-style alternative you opt into explicitly — the workflows' `uv sync --extra dev` commands don't need to (and don't) reference this table for it to be active.
**How to avoid:** No action required for *this* phase — `types-docutils` is not one of the 5 tools named in D-01/D-02 — but the planner should be aware this table exists so a future phase (or an over-eager grep-and-bump pass) doesn't miss it or double-declare it.
**Warning signs:** `grep -n "dependency-groups" -A3 pyproject.toml`.

### Pitfall 4: `black --check .` diff surfacing unexpectedly on the floor bump
**What goes wrong:** A tool version floor bump (not just target-version) can occasionally change formatting output even without a `target-version` change, if the new version alters default style rules.
**Why it happens:** Black does periodically change its "preview"-graduated stable style between versions.
**How to avoid:** Per CONTEXT.md's own discretion note — this is very unlikely here since the tree was already formatted green under the *resolved* 26.5.1 in Phase 3 (only the floor moves, not the resolved version), but run `black --check .` before committing the pyproject/tox.ini bump and after regenerating `uv.lock`, and fold any surprise reformat into the same batch (Phase 3 D-03 precedent) rather than opening a follow-up.
**Warning signs:** `uv run tox -e lint` fails immediately after the bump with formatting diffs, not just constraint-resolution errors.

### Pitfall 5: CI green today does not prove Node-20-runtime actions survive past 2026-09-16
**What goes wrong:** If the phase closes with an observed green CI run (D-05) while `upload-artifact@v5`/`download-artifact@v6` remain pinned, that green run only proves compatibility *as of today* — Node 20 is not yet removed from hosted runners. It provides no evidence about post-2026-09-16 behavior.
**Why it happens:** GitHub's runner-level Node deprecation is a rolling default-then-removal process (Node 24 became the default 2026-06-16; Node 20 support is removed 2026-09-16), not something that fails a workflow run today.
**How to avoid:** Treat "hosted-runner compatibility" (SC2 / TOOL-02) as requiring an explicit check of each action's declared runtime (`runs.using`) against this timeline, not just "did the workflow succeed."
**Warning signs:** None visible in CI output today — this is a silent, future-dated risk, which is exactly why it needs to be called out in research rather than discovered when the runner removes Node 20.

## Code Examples

### Verifying a PyPI package's current version (used this session)
```bash
# Source: pypi.org JSON API (official registry endpoint)
curl -s "https://pypi.org/pypi/black/json" | python3 -c \
  "import json,sys; d=json.load(sys.stdin); print(d['info']['version'])"
# → 26.5.1
```

### Verifying a GitHub Action's runtime declaration for its pinned tag
```bash
# Source: raw.githubusercontent.com (official GitHub content host) — verified this session
curl -s https://raw.githubusercontent.com/actions/upload-artifact/v5/action.yml | grep -A2 "runs:"
# runs:
#   using: 'node20'      ← at risk (removed from runners 2026-09-16)
curl -s https://raw.githubusercontent.com/actions/checkout/v6/action.yml | grep -A2 "runs:"
# runs:
#   using: node24        ← current, no risk
```

### Regenerating `uv.lock` with a minimal diff after a constraint bump
```bash
# Source: this repo, Phase 3 precedent (STATE.md) — do NOT use --upgrade
uv lock
git diff uv.lock   # review before committing; should show only entries tied to the touched constraints
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|-------------------|---------------|--------|
| `actions/checkout@v6`, `actions/setup-python@v6`, `astral-sh/setup-uv@v7`, `codecov/codecov-action@v5` | Still the pinned majors in this repo; each is either already `node24` or a composite action — no forced action needed | n/a (verified still current 2026-07-05) | No change required for TOOL-02 on these 4 |
| `actions/upload-artifact@v5` (node20), `actions/download-artifact@v6` (node20) | `actions/upload-artifact@v7` (node24), `actions/download-artifact@v8` (node24) exist and, per public release notes, introduce no breaking change for this repo's default (zip-archive) usage pattern — only ESM-internal changes and a new opt-in unzipped-upload feature | v7/v8 released within the last few months (upload-artifact v7: 2026-02-26; download-artifact v8: 2026-02-26) [CITED: GitHub release notes / actions/upload-artifact issue #776] | GitHub is deprecating the Node 20 runtime these two actions currently run on (removed from hosted runners 2026-09-16) [CITED: github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners] — a low-risk, in-scope bump for TOOL-02 |

**Deprecated/outdated:**
- Node.js 20 as a GitHub Actions runtime: default already switched to Node 24 (2026-06-16); full removal 2026-09-16. Any action still declaring `runs.using: node20` in its pinned tag is on a clock, independent of that action's own semver major cadence.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Bumping `actions/upload-artifact` v5→v7 and `actions/download-artifact` v6→v8 requires no yaml input/parameter changes beyond the version tag, based on public release-note summaries (not a direct diff of this repo's actual usage against both action's full changelogs) | State of the Art / Common Pitfalls | Low — this repo's usage (`name`, `path`, `retention-days`) is the simplest, most common invocation pattern; if wrong, CI would fail loudly on the observed PR run (D-05 gate would catch it) |
| A2 | No other actions used anywhere in this repo (beyond the 6 checked: checkout, setup-python, setup-uv, codecov-action, upload-artifact, download-artifact) run on Node 20 | GitHub Actions section | Low-Medium — `pypa/gh-action-pypi-publish@release/v1`, `peaceiris/actions-gh-pages@v4`, `softprops/action-gh-release@v2` (used in release.yml/docs.yml) were not individually runtime-checked this session; if any runs Node 20, it's an additional TOOL-02 candidate the planner should verify before closing the phase |

**If this table is empty:** N/A — see entries above; both are LOW/LOW-MEDIUM risk and independently guarded by the D-05 observed-CI gate.

## Open Questions (RESOLVED)

> All three resolved 2026-07-05 (user-confirmed, recorded in CONTEXT.md): **OQ1 → bump
> both artifact actions now in Phase 4** (D-03 AMENDED); **OQ2 → tox-uv IS in scope**
> (`tox-uv>=1.35,<2`, D-07); **OQ3 → keep mypy's literal `>=1.13,<3.0` floor** (D-08).

1. **[RESOLVED → D-03 AMENDED] Should `actions/upload-artifact`/`download-artifact` be bumped in this phase, given D-03 locked "no yaml edits"?**
   - What we know: D-03's stated premise ("already at latest majors") is empirically false for these two actions specifically, and both currently run on a Node runtime GitHub is actively sunsetting within this project's active window (removed 2026-09-16).
   - What's unclear: Whether the user, on seeing this new evidence, wants to (a) amend D-03 to carve out these two actions for this phase (still "conservative" — it's a drop-in major bump with no reported breaking changes for this repo's usage pattern), or (b) explicitly defer even this to Phase 5 alongside SHA-pinning, accepting the Sept-2026 Node-20-removal risk as a known, tracked item.
   - Recommendation: Surface this to the user/planner before finalizing PLAN.md — this is new factual information CONTEXT.md's author didn't have (or the live check would have caught it). A `checkpoint:human-verify`-style confirmation, or a quick re-touch of discuss-phase, fits the project's established pattern of treating locked decisions as revisable when new evidence emerges (c.f. Phase 3's mid-batch ruff/tomllib fixes).

2. **[RESOLVED → D-07: in scope, `tox-uv>=1.35,<2`] Is `tox-uv` in scope for the floor+ceiling treatment (D-02), given it has its own tox.ini↔pyproject mirror point?**
   - What we know: `tox-uv>=1.0` is declared in both `pyproject.toml [dev]` and `tox.ini`'s `[tox] requires`, resolved at 1.35.2, and is the actual mechanism (`uv-venv-lock-runner`) every other bumped tool depends on.
   - What's unclear: D-02's literal wording only names "black, ruff, tox" — tox-uv is arguably "part of tox's operation" or arguably "a separate, unnamed package."
   - Recommendation: Planner picks; leaning toward including it (`tox-uv>=1.35,<2`) for consistency with the anti-drift theme, since leaving it as a bare `>=1.0` floor while everything else gets a ceiling is an odd asymmetry — but this is genuinely Claude's-Discretion-shaped, not a hard finding.

3. **[RESOLVED → D-08: keep literal `mypy>=1.13,<3.0`, floor NOT raised to `>=2`] Should mypy's pyproject/tox.ini floor be raised to `>=2` (matching the resolved 2.1.0, consistent with how black/ruff/tox's floors were raised) or kept at the literal `>=1.13` D-01 specifies?**
   - What we know: D-01 gives one exact syntax, `mypy>=1.13,<3.0`, not `mypy>=2,<3`. For pytest, D-01 explicitly offers both a keep-original-floor option (`>=8.4,<10`) and a raise-to-resolved-major option (`>=9,<10`) — for mypy only the keep-original-floor form is given.
   - What's unclear: Whether the omission of a `>=2,<3` alternative for mypy is deliberate (mypy's floor was already close to current, no need to raise it) or an oversight of CONTEXT.md's drafting.
   - Recommendation: Follow D-01's literal syntax (`mypy>=1.13,<3.0`) since it's the one concretely specified boundary in the locked decision — but planner should still verify this doesn't create tension with D-02's general "floor-at-resolved" framing before treating it as final.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|--------------|-----------|---------|----------|
| `uv` | `uv lock` regeneration, `uv sync`, `uv run tox` | ✓ | 0.11.25 | — |
| `git` | commits, diff review | ✓ | 2.54.0 | — |
| `gh` (GitHub CLI) | opening/observing the PR for D-05's push→observe gate | ✓ | 2.95.0 | — |
| `tox` (local CLI) | local pre-flight `tox -e lint`/`type`/`cov` | ✗ (not on PATH; project resolves it per-env via `uv run tox`) | — | Use `uv run tox -e <env>` instead of a bare `tox` invocation — matches how CI itself invokes tox |
| Local Python interpreters for `tox -e py3.11-3.13` | Full local matrix pre-check | Partially — NixOS cannot execute `tox-uv`'s downloaded standalone CPython builds (documented Phase 2 finding, STATE.md) | 3.13.13 (system) | Substitute `uv run tox -e cov` (system Python) for the full py3.11-3.13 local pre-check, same substitution Phase 2 already established; rely on the observed CI matrix (D-05) for full cross-version proof |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** local multi-version tox execution (NixOS constraint, pre-existing and already worked around per Phase 2).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (already resolved), invoked via `uv run tox -e <env>` |
| Config file | `pyproject.toml [tool.pytest.ini_options]` (testpaths=tests, strict-markers); `tox.ini` per-env deps/commands |
| Quick run command | `uv run tox -e lint` (black+ruff), `uv run tox -e type` (mypy), `uv run tox -e cov` (pytest+coverage, system-Python fallback per Phase 2) |
| Full suite command | Push a branch → PR against `main`; observe `ci.yml` (test matrix 3.10-3.13 × 3 OS, lint, type-check, coverage, build, integration) and `docs.yml` both green (D-05) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|--------------|
| TOOL-01 | `pyproject.toml`/`tox.ini` dev-tool constraints bump without breaking resolution or CI | integration (resolution + full CI) | `uv lock` (resolves cleanly) → `uv run tox -e lint` / `-e type` / `-e cov` locally → observed green `ci.yml` on PR | ✅ (existing workflow, no new test file needed) |
| TOOL-02 | GitHub Actions versions verified/refreshed for hosted-runner compatibility | manual verification + observed CI | `curl api.github.com/repos/<org>/<repo>/releases` + `action.yml runs.using` check (this session) → observed green `ci.yml`/`docs.yml` on PR | ✅ N/A — no test file; this is a config-currency check, not a code-path test |

**Note on TOOL-02's automatable proof:** unlike TOOL-01, "hosted-runner compatibility" for actions still on Node 20 (`upload-artifact@v5`, `download-artifact@v6`, if left unbumped) has **no automated test that would fail today** — the risk is future-dated (2026-09-16). If the phase leaves those two actions unbumped, the plan should explicitly record this as a tracked/deferred risk (not silently closed as "verified"), consistent with Pitfall 5 above.

### Sampling Rate
- **Per task commit:** `uv run tox -e lint` and/or `-e type` and/or `-e cov` depending on which surface the commit touches (pyproject-only commit → all three; README/comment-only commit → none needed, docs-only)
- **Per wave merge:** Full local `uv run tox -e lint,type,cov` pass before pushing
- **Phase gate:** Observed green `ci.yml` + `docs.yml` on the PR targeting `main` (D-05) — this is the actual phase-closing gate, not local tox alone, because `uv.lock` regeneration can shift transitive deps unpredictably

### Wave 0 Gaps
None — existing test/CI infrastructure (pytest suite, tox envs, `ci.yml`/`docs.yml` workflows) already covers everything this phase changes. This phase adds no new source code and needs no new test files; its "tests" are the resolution step (`uv lock`) and the existing CI jobs themselves.

## Security Domain

`security_enforcement: true`, ASVS level 1, block-on: high (`.planning/config.json`). This phase makes no changes to application code, authentication, input handling, or cryptography — it only bumps dev-tooling version constraints and verifies CI-runner compatibility. Applicability assessment:

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|----------------|---------|-------------------|
| V2 Authentication | No | Phase touches no auth surface (library has none) |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | No | No user-facing input path touched |
| V6 Cryptography | No | N/A |
| V1 Architecture (supply-chain integrity, adjacent) | Partially | Version-constraint pinning (floor+ceiling per D-02) is itself a supply-chain integrity control; **SHA-pinning GitHub Actions to commit hashes** (the stronger, complementary control) is explicitly deferred to Phase 5 per D-03/deferred-items and should not be pulled forward into this phase |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|------------------------|
| Dependency-confusion / typosquat on a dev-tool bump | Tampering | Version-string legitimacy checked this session against the official PyPI registry (see Package Legitimacy Audit) — all 7 confirmed as the genuine project's release, not a lookalike |
| Unpinned GitHub Action tag silently receiving a compromised update | Tampering / Elevation of Privilege | Out of scope for this phase (all actions are pinned to a major-version tag, not `@main`/`@latest`); SHA-pinning (the stronger mitigation) is Phase 5's explicit scope, not this phase's |

## Sources

### Primary (HIGH confidence)
- `https://pypi.org/pypi/{black,ruff,tox,tox-uv,pytest,mypy,pre-commit}/json` — direct registry queries, this session, confirming all 7 target versions are each project's current latest release
- `https://api.github.com/repos/{actions/checkout,actions/setup-python,codecov/codecov-action,astral-sh/setup-uv,actions/upload-artifact,actions/download-artifact}/releases` — direct GitHub API queries, this session, for release history and prerelease/draft status
- `https://raw.githubusercontent.com/{action}/{tag}/action.yml` — direct fetch of each pinned tag's actual runtime manifest (`runs.using`), this session
- Repo files read directly this session: `pyproject.toml`, `tox.ini`, `README.md`, `.github/workflows/{ci,docs,release}.yml`, `uv.lock`

### Secondary (MEDIUM confidence)
- `https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/` — Node 20 deprecation timeline (default switch 2026-06-16, removal 2026-09-16) [CITED]
- `https://docs.astral.sh/ruff/versioning/` — ruff's custom versioning scheme (minor = breaking) [CITED]
- `https://docs.astral.sh/uv/concepts/projects/dependencies/` — uv's default-inclusion behavior for `[dependency-groups] dev` [CITED]
- `actions/upload-artifact` issue #776 and public release notes — no documented breaking changes in v6/v7 for default usage [CITED, not independently diffed against this repo's exact invocation]

### Tertiary (LOW confidence)
- None used as load-bearing claims — all findings above were cross-checked against at least one authoritative source.

## Metadata

**Confidence breakdown:**
- Standard stack (dev-tool versions): HIGH — every version independently re-verified against the live PyPI registry this session, matches `uv.lock` and CONTEXT.md exactly
- Architecture (tox↔pyproject mirror, uv.lock-as-source-of-truth): HIGH — verified by direct file inspection of `tox.ini`/`pyproject.toml`/`uv.lock`
- GitHub Actions currency/compatibility: MEDIUM — the Node-20-removal finding is well-sourced (official GitHub changelog + direct `action.yml` inspection) but its resolution (whether to bump upload-artifact/download-artifact in this phase or defer) requires a decision this research cannot make unilaterally
- Pitfalls: HIGH — each pitfall is grounded in a specific, verified repo fact (file content, uv default-group behavior, ruff versioning docs), not general training-knowledge speculation

**Research date:** 2026-07-05
**Valid until:** ~14 days for the dev-tool version table (fast-moving PyPI ecosystem, ruff/tox in particular release every few weeks); ~30 days for the GitHub Actions Node-deprecation timeline (fixed, published dates, unlikely to move, but re-check if the phase slips past 2026-09-16)
