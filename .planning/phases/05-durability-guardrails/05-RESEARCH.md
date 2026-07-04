# Phase 5: Durability Guardrails - Research

**Researched:** 2026-07-05
**Domain:** GitHub Actions CI/CD hardening (lockfile-currency gate, scheduled drift detection, Dependabot grouping, status badge)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Add `--locked` to every `uv sync` call site, not a single dedicated `uv lock --check` gate job and not ci.yml-only. `uv.lock` is the single source of truth every workflow resolves from; forcing all jobs to fail on lock/pyproject desync is the milestone-consistent, zero-extra-job approach and closes the release/docs re-resolution path too.
- **D-02 (call-site inventory for planner):** 9 `uv sync` occurrences must all get `--locked`:
  - `ci.yml` lines 41, 71, 92, 113, 151 (`uv sync --extra dev`) and **179 (`uv sync`, no `--extra`)** — do not miss the bare one in the example-build job.
  - `docs.yml` line 31 (`uv sync --extra dev --extra docs`).
  - `release.yml` lines 36 and 93 (`uv sync --extra dev`).
  Preserve each line's existing `--extra` flags; append `--locked`.
- **D-03 (verify the gate actually gates):** `uv sync --locked` fails when `uv.lock` is out of sync with `pyproject.toml`. Because the lock is currently in sync (Phase 4 regenerated it), the green run alone doesn't prove the gate bites. Planner should note this — the proof that it fails-loud is inherent to `--locked` semantics; no need to intentionally desync in CI.
- **D-04:** Separate `.github/workflows/drift.yml` (not a `schedule:` + `continue-on-error` job bolted onto `ci.yml`) — keeps the scheduled/advisory concern out of the per-PR blocking pipeline and keeps `ci.yml` focused.
- **D-05:** The drift job resolves latest deps and exercises them: `uv lock --upgrade` (ignore the committed lock intentionally), then run the test/build to surface a `kai`-class break early. Does NOT commit the upgraded lock.
- **D-06:** On failure, auto-file/update a GitHub Issue so drift is a visible, persistent signal rather than a buried red X. Use a single-issue-update pattern (dedupe by title/label) so weekly runs don't spam duplicate issues. Planner picks the mechanism (e.g. `gh issue` in a step, or a maintained create-issue action) — the *rule* is: visible, deduplicated, non-spammy.
- **D-07:** Non-blocking — `drift.yml` must NOT be added to `main`'s required status checks. It reports; it never blocks a merge.
- **D-08:** Group exactly `sphinx`/`docutils`/`typst` into one dedicated group under the existing `pip` ecosystem in `.github/dependabot.yml` (append a `groups:` block; keep the `github-actions` ecosystem entry untouched). Suggested group name `sphinx-typst-stack` with patterns `sphinx*` / `docutils*` / `typst*`; planner confirms exact patterns. Do NOT broaden to whole-runtime or add a dev-tool group.
- **D-09 (Claude's discretion, pre-decided):** Add one CI-workflow status badge to the existing `README.md` badge row (lines 3–7). Badge URL form: `https://github.com/YuSabo90002/typsphinx/actions/workflows/ci.yml/badge.svg` linking to the workflow's Actions page. A single CI badge satisfies DUR-04; no separate docs-workflow badge unless the user later asks.
- **D-10:** Reuse the push→observe gate for the verifiable parts (DUR-01 `--locked` green, DUR-03/04 render correctly, D-11 action bump green) on a PR targeting `main`. DUR-02's scheduled job cannot be observed via a normal PR run — validate it by a manual `workflow_dispatch` trigger (add `workflow_dispatch:` to `drift.yml`) rather than waiting a week.
- **D-11:** Bump `softprops/action-gh-release@v2 → @v3` (node24) in `docs.yml` line 67 and `release.yml` line 177. This is the Phase-4 tracked node20 straggler (Node 20 removed from hosted runners 2026-09-16); `@v3` is a drop-in node24 release for this repo's usage. Log this in PROJECT.md Key Decisions at phase transition.

### Claude's Discretion

- Exact Issue-dedup mechanism/action for DUR-02 (D-06 rule stands: visible + deduplicated).
- Exact Dependabot `patterns` glob strings and group name (D-08).
- Badge markdown placement within the existing badge row (D-09).
- Whether `drift.yml` also runs the docs-pdf build in addition to the test matrix subset — planner scopes to a meaningful-but-cheap drift signal.

### Deferred Ideas (OUT OF SCOPE)

- **SHA-pin GitHub Actions to commit hashes** (supply-chain hardening) → future milestone (D-12). On the table for Phase 5 but consciously deferred: new category, high maintenance surface, outside DUR-01..04. Revisit as a dedicated security-hardening item.
- Broader Dependabot grouping (dev tools, whole runtime) → not needed; DUR-03 is scoped to the risk cluster (D-08).

None of the above expand this phase — discussion stayed within DUR-01..04 plus the explicitly-carried softprops item.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DUR-01 | CI uses `uv sync --locked` (or a `uv lock --check` gate) so a stale/rewritten lockfile fails the build instead of being silently regenerated | Confirmed exact 9-site line inventory (unchanged since CONTEXT.md was written — see Call-Site Drift Check below); confirmed `--locked` failure semantics via uv docs/community sources |
| DUR-02 | A weekly non-blocking scheduled (`schedule:`) drift-detection CI job resolves latest deps and reports breakage early | Confirmed `uv lock --upgrade` + `uv sync` semantics, tox-uv `uv-venv-lock-runner` runtime lock-reading behavior, GitHub's official `gh issue` dedupe pattern, and cron/`workflow_dispatch` syntax — concrete `drift.yml` skeleton provided below |
| DUR-03 | `dependabot.yml` groups the `sphinx`/`docutils`/`typst` cluster so a lone bump can't reintroduce the `kai` break | Confirmed Dependabot `groups:`/`patterns:` config syntax against official docs |
| DUR-04 | CI status badge added to `README.md` | Confirmed badge URL form against official GitHub docs; confirmed repo slug and workflow filename |

</phase_requirements>

## Summary

Phase 5 is a pure CI/CD-configuration phase: no application code changes, no new runtime or dev-tooling packages, no new imports. Every edit is to `.github/workflows/*.yml`, `.github/dependabot.yml`, or `README.md`. The four requirements are individually low-risk and well-precedented — `uv sync --locked` is a documented, intentional-failure safety flag; `uv lock --upgrade` is a documented re-resolution flag; Dependabot `groups:`/`patterns:` is a stable, long-established config surface; and GitHub Actions status badges are a first-party, zero-dependency feature. The one genuinely novel piece of engineering is `drift.yml`'s failure-reporting step (DUR-02/D-06): GitHub's own documentation (not a third-party Marketplace action) shows the currently-recommended, dependency-free pattern — call `gh issue list`/`gh issue create` directly in a `run:` step, gated by `permissions: issues: write` and deduplicated by label lookup. This avoids adding a new third-party Action to the trust surface for a single-step operation.

All call-site line numbers cited in `05-CONTEXT.md` (D-02, softprops locations) were re-verified against the current tree with `grep -n` and match exactly — no drift since context-gathering. The `softprops/action-gh-release@v2 → @v3` bump (D-11) is confirmed safe: `@v3` (v3.0.0/v3.0.1) exists, is Node 24, and is described upstream as a Node-runtime-only change with no API differences — a true drop-in for this repo's usage (`files:`, `draft:`, `prerelease:`, `body_path:`, `generate_release_notes:` — all present pre-v3 and unaffected).

**Primary recommendation:** Implement DUR-01 as a mechanical 9-site append (`--locked` after each existing `uv sync` invocation, preserving `--extra` flags exactly as listed in D-02). Implement DUR-02 as a new `drift.yml` with `schedule: cron: '0 0 * * 1'` + `workflow_dispatch:`, running `uv lock --upgrade && uv sync && uv run tox -e <fast subset>`, with an `if: failure()` step at the end that uses `gh issue list --label drift --json number --jq '.[0].number'` to find an existing open drift issue and either comments on it or creates a new one — never both, never silently. Implement DUR-03 as a `groups: sphinx-typst-stack: patterns: [sphinx*, docutils*, typst*]` block under the existing `pip` ecosystem entry. Implement DUR-04 as one badge line inserted into the existing README badge row. Implement D-11 as a literal `@v2` → `@v3` string swap at the two confirmed call sites.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Lockfile-currency enforcement (DUR-01) | CI / Build pipeline | — | `uv sync --locked` is a build-time gate; no runtime/application-tier involvement |
| Weekly drift detection (DUR-02) | CI / Scheduled automation | GitHub Issues (reporting sink) | Drift resolution + test execution happens in a CI job; failure signal is persisted to GitHub's issue-tracking surface, not the app |
| Dependency-update grouping (DUR-03) | CI / Dependabot config | — | Dependabot is a GitHub-hosted service reading a static config file; no code executes this logic in-repo |
| CI status badge (DUR-04) | Documentation / README | GitHub Actions (badge image source) | Static markdown pointing at a GitHub-hosted SVG endpoint; no build step needed |
| GH Action version currency (D-11) | CI / Build pipeline | — | Action-runtime (Node version) compatibility with hosted runners; config-only edit |

## Standard Stack

This phase introduces no new libraries, runtime dependencies, or dev-tooling packages. The "stack" is entirely the already-adopted CI toolchain, used in new configuration combinations.

### Core (already in use, no version change required by this phase)
| Tool | Version (confirmed in repo) | Purpose | Why Standard |
|------|------|---------|--------------|
| `uv` | `astral-sh/setup-uv@v7` in CI; `uv 0.11.25` locally | Dependency resolution/locking/sync | Already the project's sole package manager (Phase 1-4) |
| `tox` + `tox-uv` | `tox-uv~=1.35` (tox.ini `[tox] requires`) | Test/lint/type/docs env runner, `uv-venv-lock-runner` | Already the project's test-runner abstraction; every env installs from `uv.lock` at run time |
| `gh` (GitHub CLI) | Pre-installed on all GitHub-hosted runners; `GITHUB_TOKEN` auto-provisioned | Issue list/create/comment for DUR-02 dedup | First-party, zero-install-cost, officially documented pattern (see Code Examples) — no new Marketplace Action trust surface |
| Dependabot | GitHub-native (`.github/dependabot.yml` v2 schema) | Grouped dependency PRs (DUR-03) | Already configured (`pip` + `github-actions` ecosystems); `groups:` is a stable, GA (non-beta since 2023) feature of the same schema version already in use |

### Supporting
| Item | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| `softprops/action-gh-release` | `@v2` (current) → `@v3` (target, D-11) | Creates GitHub Releases in `docs.yml` and `release.yml` | Bump now — `@v2` remains on the deprecated Node 20 runtime; `@v3` is Node 24, drop-in, no config/API changes required |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `gh issue` in a `run:` step for DUR-02 dedup | A Marketplace action (e.g. a "create-issue-from-file"–style action) | Third-party actions add a new supply-chain trust dependency and a version to track for a single, simple CRUD operation `gh` already does natively and unversioned (bundled on the runner). GitHub's own docs recommend the native `gh` pattern for exactly this scheduled-issue use case — no reason to add an external action here. |
| Single dedicated `uv lock --check` job (ci.yml-only) | 9-site `--locked` append (D-01, chosen) | A single check-job would validate the lock is current but would NOT stop `docs.yml`/`release.yml` from independently re-resolving with a stale/rewritten lock if that single job weren't a blocking dependency of every other job. D-01 already locked this decision — documented here only to confirm the rejected alternative's weakness. |

**Installation:** No new package installations. All changes are to `.github/workflows/*.yml`, `.github/dependabot.yml`, and `README.md`.

**Version verification:**
```bash
# Confirm astral-sh/setup-uv and softprops/action-gh-release tags exist and are current
gh api repos/astral-sh/setup-uv/releases/latest --jq .tag_name
gh api repos/softprops/action-gh-release/releases --jq '.[0:3] | .[].tag_name'
```
`softprops/action-gh-release` v3.0.0 (Node 24 migration) and v3.0.1 (maintenance) were confirmed to exist via the project's GitHub Releases page during this research session [CITED: github.com/softprops/action-gh-release/releases]. `@v3` is the correct moving major tag to reference (matches this repo's existing convention of pinning to moving major tags, e.g. `actions/checkout@v6`, `astral-sh/setup-uv@v7`).

## Package Legitimacy Audit

**Not applicable to this phase.** Phase 5 installs zero new pip/npm/crates packages — it only edits CI workflow YAML, Dependabot config, and README markdown. The one external-reference change (`softprops/action-gh-release@v2 → @v3`) is a GitHub Action version bump, not a package-registry install; it was verified directly against the action's own GitHub Releases page (see Standard Stack / Alternatives Considered above) rather than via `npm view`/`pip index`/`cargo search`, since GitHub Actions are not registry packages in that sense.

**Packages removed due to [SLOP] verdict:** none (no packages evaluated — none installed).
**Packages flagged as suspicious [SUS]:** none.

## Architecture Patterns

### System Architecture Diagram

```
                    ┌─────────────────────────────────────────────┐
                    │              Developer / PR                  │
                    └───────────────────┬───────────────────────────┘
                                        │ push / PR to main
                                        ▼
                    ┌─────────────────────────────────────────────┐
                    │   ci.yml (blocking, required checks)          │
                    │   every `uv sync` site now `--locked`         │
                    │   (test matrix, lint, type, coverage, build,  │
                    │    integration jobs)                          │
                    └───────────────────┬───────────────────────────┘
                                        │ uv.lock out of sync?
                                        │  YES → job fails loudly (DUR-01)
                                        │  NO  → proceeds as before
                                        ▼
                    ┌─────────────────────────────────────────────┐
                    │   docs.yml / release.yml (blocking)           │
                    │   `uv sync --locked` (same gate, same lock)   │
                    │   softprops/action-gh-release@v3 (D-11)       │
                    └─────────────────────────────────────────────┘

     (independent, time-triggered — not part of the PR path above)

  ┌──────────────┐   schedule: '0 0 * * 1'    ┌──────────────────────────┐
  │ GitHub cron   │ ─────────────────────────▶ │ drift.yml (non-blocking)  │
  │ scheduler     │   or workflow_dispatch      │  uv lock --upgrade       │
  └──────────────┘   (manual, D-10 validation)  │  uv sync (fresh lock)    │
                                                 │  uv run tox -e <subset> │
                                                 └───────────┬──────────────┘
                                                             │ if: failure()
                                                             ▼
                                                 ┌──────────────────────────┐
                                                 │  gh issue list --label   │
                                                 │  drift → found? comment  │
                                                 │  : else create (DUR-02/  │
                                                 │  D-06 dedup pattern)     │
                                                 └──────────────────────────┘

  ┌──────────────────────┐   dependency PR scan   ┌───────────────────────────┐
  │ Dependabot (GitHub-   │ ─────────────────────▶ │ dependabot.yml pip         │
  │ hosted service)       │   weekly, Mondays      │  ecosystem: groups:        │
  │                       │                        │  sphinx-typst-stack        │
  │                       │                        │  patterns: sphinx*/        │
  │                       │                        │  docutils*/typst* (DUR-03) │
  └──────────────────────┘                        └───────────────────────────┘

  ┌──────────────────────┐   badge.svg endpoint    ┌───────────────────────────┐
  │ README.md badge row   │ ◀───────────────────── │ ci.yml workflow status     │
  │ (DUR-04)              │  live image fetch       │ (GitHub-hosted, no build)  │
  └──────────────────────┘                        └───────────────────────────┘
```

### Recommended Project Structure
```
.github/
├── workflows/
│   ├── ci.yml          # EDIT: append --locked to 6 uv sync sites (lines 41/71/92/113/151/179)
│   ├── docs.yml        # EDIT: --locked (line 31) + softprops@v2→v3 (line 67)
│   ├── release.yml     # EDIT: --locked (lines 36/93) + softprops@v2→v3 (line 177)
│   └── drift.yml       # NEW: weekly schedule + workflow_dispatch, uv lock --upgrade, issue-dedupe on failure
└── dependabot.yml      # EDIT: append groups: block to the existing pip ecosystem entry
README.md               # EDIT: insert one badge into the existing row (lines 3-7)
```

### Pattern 1: Append `--locked` while preserving existing flags
**What:** Every existing `uv sync [flags]` invocation becomes `uv sync [flags] --locked`, with `[flags]` unchanged.
**When to use:** All 9 call sites in D-02 — this is a mechanical, uniform transformation, not a redesign.
**Example:**
```yaml
# ci.yml:41 (and 71, 92, 113) — before:
      - name: Install dependencies
        run: uv sync --extra dev
# after:
      - name: Install dependencies
        run: uv sync --extra dev --locked

# ci.yml:151 (Build Package job's "Check package" step) — before:
      - name: Check package
        run: |
          uv sync --extra dev
          uv run twine check dist/*
# after:
      - name: Check package
        run: |
          uv sync --extra dev --locked
          uv run twine check dist/*

# ci.yml:179 (integration job — bare, no --extra) — before:
      - name: Install package and dependencies
        run: uv sync
# after:
      - name: Install package and dependencies
        run: uv sync --locked

# docs.yml:31 — before:
      - name: Install dependencies
        run: |
          uv sync --extra dev --extra docs
          uv pip install -e .
# after:
      - name: Install dependencies
        run: |
          uv sync --extra dev --extra docs --locked
          uv pip install -e .

# release.yml:36 and :93 — same --extra dev --locked pattern as ci.yml
```
[VERIFIED: codebase grep — line numbers re-confirmed 2026-07-05, unchanged from CONTEXT.md]

### Pattern 2: Scheduled, non-blocking drift job with deduplicated issue reporting
**What:** A standalone workflow triggered by `schedule:` + `workflow_dispatch:` that intentionally re-resolves dependencies past the committed lock, exercises them, and on failure files/updates exactly one tracking issue.
**When to use:** DUR-02 (drift.yml), and only there — this pattern must NOT be merged into `ci.yml`'s per-PR jobs (D-04/D-07).
**Example:**
```yaml
# Source: GitHub Docs "Scheduling issue creation" (docs.github.com/en/actions/use-cases-and-examples/project-management/scheduling-issue-creation)
# combined with uv docs (docs.astral.sh/uv/concepts/projects/sync) — synthesized for this repo, not copy-pasted verbatim
name: Dependency Drift Check

on:
  schedule:
    - cron: '0 0 * * 1'   # every Monday 00:00 UTC
  workflow_dispatch:        # D-10: manual trigger for verification without waiting a week

permissions:
  contents: read
  issues: write             # required for the gh issue steps below

jobs:
  drift-check:
    name: Resolve latest deps and exercise them
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Install uv
        uses: astral-sh/setup-uv@v7
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install 3.10

      - name: Resolve latest allowed dependency versions (ignore committed lock)
        run: uv lock --upgrade

      - name: Install from the freshly-resolved (uncommitted) lock
        run: uv sync --extra dev --extra docs --locked

      - name: Exercise the resolved dependency set
        run: uv run tox -e cov,docs-pdf

      - name: Report drift via a single deduplicated issue
        if: failure()
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GH_REPO: ${{ github.repository }}
        run: |
          existing=$(gh issue list --label drift --state open --json number --jq '.[0].number')
          run_url="${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
          if [ -n "$existing" ]; then
            gh issue comment "$existing" --body "Drift check failed again: $run_url"
          else
            gh issue create \
              --title "Dependency drift detected: latest resolvable versions break the build" \
              --label drift \
              --body "The weekly drift-detection job resolved to the latest allowed dependency versions and the build/test step failed. Run: $run_url"
          fi
```
Notes on this skeleton:
- `uv sync --extra dev --extra docs --locked` in the drift job's own second step is safe and intentional: `--locked` here validates that `uv sync` installs *exactly* what `uv lock --upgrade` just wrote seconds earlier in the same job (no cross-job desync), not that it matches the *committed* lock. It does not defeat D-05's "ignore the committed lock" intent, because `uv lock --upgrade` already ran first and rewrote the working-directory `uv.lock` before `--locked` is checked against it.
- `uv run tox -e cov,docs-pdf` exercises both the Python test suite and the exact `docs-pdf` target that triggered the `kai`-class break historically — this is the meaningful-but-cheap drift signal the planner has discretion to scope (see Claude's Discretion above). A full 3-OS × 4-Python matrix would be excessive for a non-blocking weekly signal; `cov` (ubuntu, one Python version, full pytest run with coverage) plus `docs-pdf` (the historically fragile PDF path) is a reasonable minimum. The planner may adjust the exact tox envs.
- The dedup label (`drift`) does not yet exist as a repo label; `gh issue create --label drift` auto-creates unknown labels the first time it's used — no separate label-creation step is required. [ASSUMED — based on `gh issue create` behavior; not independently re-verified in this session for the exact `gh` CLI version installed on hosted runners. Low risk: worst case is a one-time no-op label-creation failure that would surface immediately on the first manual `workflow_dispatch` validation run per D-10.]
- `tox-uv`'s `uv-venv-lock-runner` reads `uv.lock` from the working directory at the time `tox` runs, not a cached/committed copy — so running `uv lock --upgrade` then `uv run tox -e ...` in the same job correctly exercises the upgraded dependency set. [VERIFIED: codebase — `tox.ini` confirms every relevant env uses `runner = uv-venv-lock-runner`; this runtime-lock-reading behavior is the tox-uv plugin's documented purpose.]

### Pattern 3: Dependabot dependency-cluster grouping
**What:** A `groups:` map under a `package-ecosystem` entry that bundles matching dependency names into one PR instead of one-PR-per-dependency.
**When to use:** DUR-03 — append to the existing `pip` ecosystem block; do not touch the `github-actions` ecosystem block.
**Example:**
```yaml
# Source: docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference
# .github/dependabot.yml — existing pip block, with groups: appended
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "00:00"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "automated"
    groups:
      sphinx-typst-stack:
        patterns:
          - "sphinx*"
          - "docutils*"
          - "typst*"
```
Notes: `sphinx*` will also match `sphinx-testing`-style names, but that dependency was already removed in Phase 1 (PIN-05) — no live false-positive risk today. `typst*` matches the single `typst` (typst-py) runtime dependency; there is no other `typst`-prefixed package in this project's dependency tree to over-match. [VERIFIED: codebase — confirmed via Phase 1/pyproject.toml history in STATE.md; not re-grepped against current `pyproject.toml` in this session, low risk given Phase 1-4 already audited the full dependency list.]

### Pattern 4: README CI status badge
**What:** A single markdown image badge pointing at GitHub's live workflow-status SVG endpoint.
**When to use:** DUR-04 — inserted into the existing badge row.
**Example:**
```markdown
<!-- Source: docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge -->
[![CI](https://github.com/YuSabo90002/typsphinx/actions/workflows/ci.yml/badge.svg)](https://github.com/YuSabo90002/typsphinx/actions/workflows/ci.yml)
```
Placement: insert as a new line among the existing badge lines (README.md:3-7); exact position is Claude's discretion (D-09) — placing it first (before PyPI) foregrounds the "is the build currently green" signal this whole milestone exists to restore, but any position in the existing row satisfies DUR-04.

### Anti-Patterns to Avoid
- **Adding `drift.yml` as a job inside `ci.yml` with `continue-on-error: true`:** Explicitly rejected by D-04 — this would couple the scheduled/advisory concern to the per-PR blocking pipeline's file and trigger surface, and risks accidentally becoming a required check later.
- **Adding a single `uv lock --check` job instead of per-call-site `--locked`:** Explicitly rejected by D-01 — a single job doesn't stop `docs.yml`/`release.yml` from independently re-resolving with a stale lock unless that job is a hard dependency (`needs:`) of every other workflow, which this repo's three separate workflow files don't naturally support.
- **Filing a new GitHub Issue on every single drift-job failure without a dedup check:** Explicitly rejected by D-06 — weekly runs would spam duplicate issues within weeks. Always `gh issue list --label ... --state open` first.
- **Adding `drift.yml` to `main`'s required status checks:** Explicitly rejected by D-07 — would make an intentionally-advisory, expected-to-sometimes-fail job block every merge.
- **Committing the `uv lock --upgrade` output from `drift.yml`:** Explicitly rejected by D-05 — the job's entire purpose is early detection without altering the actually-shipped, known-good lock.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Deduplicated issue-on-failure reporting | A custom script that diffs issue bodies, tracks state in a file/gist, or reimplements GitHub's issue API via raw `curl` | `gh issue list --label X --state open --json number --jq '.[0].number'` + `gh issue create`/`gh issue comment` | `gh` is pre-installed on every GitHub-hosted runner, auto-authenticated via `GITHUB_TOKEN`, and this exact list-then-create-or-comment pattern is GitHub's own documented recommendation for scheduled-issue use cases — no custom state-tracking needed |
| Lockfile-currency verification | A custom script that diffs `uv.lock`'s content hash against a stored value, or manually re-runs `uv lock` and `git diff --exit-code`-checks it | `uv sync --locked` (native flag) | `uv` already implements exactly this check internally (comparing resolved metadata against the lock), including handling of markers/extras/upper-bounds that a naive file-hash diff would get wrong |
| Dependency-cluster batching in Dependabot | A separate bot/script that watches multiple Dependabot PRs and merges/combines them post-hoc | Dependabot's native `groups:`/`patterns:` config | This is a first-party, GA Dependabot feature (public beta since June 2023, stable since); reinventing PR-combination logic outside Dependabot fights the platform instead of using it |

**Key insight:** Every requirement in this phase already has a first-party, zero-additional-dependency solution (a `uv` CLI flag, a `gh` CLI command sequence, a Dependabot config block, and a GitHub-hosted badge endpoint). The correct implementation approach throughout is "use the existing tool's documented feature," not "add a new script or Marketplace Action."

## Common Pitfalls

### Pitfall 1: Forgetting the bare `uv sync` at ci.yml:179
**What goes wrong:** All 8 other `uv sync` sites have `--extra dev` (and docs.yml's has `--extra dev --extra docs`), making them easy to find with a search for `--extra dev`. The integration job's `uv sync` (line 179, no `--extra` flag) is easy to miss with that same search pattern.
**Why it happens:** Pattern-matching on `--extra dev` across the file will visually skip the one line that doesn't contain it.
**How to avoid:** Search for the literal string `uv sync` (not `uv sync --extra`) across all three workflow files before considering DUR-01 complete; cross-check against the exact 9-site D-02 inventory (re-verified in this research session, see Call-Site Drift Check below).
**Warning signs:** `grep -c "uv sync" .github/workflows/*.yml` should return `ci.yml: 6, docs.yml: 1, release.yml: 2` (total 9) both before and after the edit — after, every one of those 9 lines should also match `grep -c "\-\-locked"`.

### Pitfall 2: `--locked` in the drift job masking the intended re-resolution
**What goes wrong:** If `--locked` is (incorrectly) placed on the drift job's `uv sync` call *before* `uv lock --upgrade` runs, the job would fail immediately by design (the committed lock predates the upgrade) — defeating the entire purpose of the drift check.
**Why it happens:** Copy-pasting the DUR-01 `--locked` pattern into `drift.yml` without noticing the operation order matters here.
**How to avoid:** In `drift.yml`, always run `uv lock --upgrade` first; the subsequent `uv sync --locked` then validates against the *freshly-upgraded, uncommitted* lock (a same-job consistency check), not the committed one. See Pattern 2 above for the exact step order.
**Warning signs:** The drift job fails on every single run, immediately at the `uv sync` step, regardless of whether upstream dependencies actually changed — this is the tell that operation order is wrong.

### Pitfall 3: Softprops action bump silently breaking release automation if verified on the wrong environment
**What goes wrong:** `@v3` requires the Node 24 Actions runtime. All current GitHub-hosted runners (as of this research date) support Node 24, and this repo already runs Node 24 actions elsewhere (per Phase 4's `upload-artifact@v7`/`download-artifact@v8` bumps) — so this is low risk, but any future migration to older self-hosted runners without Node 24 support would break `docs.yml`'s and `release.yml`'s release steps.
**Why it happens:** Action major-version bumps for runtime reasons (not API reasons) are easy to verify as "just works" on hosted runners and easy to forget as an assumption if the CI environment ever changes.
**How to avoid:** The push→observe gate (D-10) on this phase's PR will empirically confirm `@v3` works end-to-end (docs.yml's tag-triggered release step and release.yml's release-creation step) — but note that neither of those steps runs on a normal `pull_request`-triggered CI run (docs.yml's release step only fires on `startsWith(github.ref, 'refs/tags/v')`; release.yml only fires on tag push or `workflow_dispatch`). A PR alone will NOT exercise these two edited lines.
**Warning signs:** If the planner's verification plan only checks `ci.yml`/`docs.yml`'s build steps and calls D-11 "verified," that's a false green — the softprops-using steps are tag-gated and need either a manual `workflow_dispatch` (release.yml supports this) or explicit human-verify sign-off deferring full confirmation to the next real tag-push release.

### Pitfall 4: Dependabot `groups:` over-matching via bare wildcard
**What goes wrong:** A pattern like `*sphinx*` (double-wildcard) could match unintended packages containing "sphinx" as a substring in a larger, unrelated name.
**Why it happens:** Overly broad glob patterns feel "safer" (catch more) but actually violate D-08's explicit "exactly sphinx/docutils/typst, do not broaden" instruction.
**How to avoid:** Use prefix-anchored patterns (`sphinx*`, `docutils*`, `typst*`) as specified in CONTEXT.md's suggested patterns, not `*sphinx*`-style substring wildcards.
**Warning signs:** The first Dependabot PR under the new group unexpectedly bundles an unrelated package — inspect the group's `patterns:` for accidental substring matching.

## Code Examples

### Verifying the 9-site `--locked` inventory before/after
```bash
# Before: confirm the exact call-site count matches D-02's inventory
grep -n "uv sync" .github/workflows/ci.yml .github/workflows/docs.yml .github/workflows/release.yml
# Expected: 6 in ci.yml (41,71,92,113,151,179), 1 in docs.yml (31), 2 in release.yml (36,93) = 9 total

# After: confirm every site now has --locked
grep -n "uv sync" .github/workflows/ci.yml .github/workflows/docs.yml .github/workflows/release.yml | grep -v -- "--locked"
# Expected: empty output (no uv sync line lacking --locked)
```

### Manually validating `drift.yml` without waiting a week (D-10)
```bash
# After pushing drift.yml with workflow_dispatch: added, trigger it manually:
gh workflow run drift.yml
gh run watch  # follow the run to completion
gh run view --log  # inspect output; on a deliberately-broken dependency set this proves the dedup-issue step fires
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `uv sync` with no `--locked` (implicit trust that `uv.lock` matches `pyproject.toml`) | `uv sync --locked` everywhere deps are installed in CI | Documented `uv` behavior, in place since early `uv` project-management releases; this phase is the repo's first adoption of it | A silently-rewritten or hand-edited `uv.lock` (this milestone's root cause pattern) now fails the build immediately instead of resolving to unexpected versions |
| One-PR-per-dependency-bump Dependabot updates | Grouped updates via `groups:`/`patterns:` | Dependabot grouping went GA in 2023 (public beta June 2023); this phase is the repo's first adoption | A lone `typst` bump can no longer land without its `sphinx`/`docutils` cluster-mates, directly preventing a repeat of the `kai`-class break |
| `softprops/action-gh-release@v2` (Node 20) | `@v3` (Node 24) | v3.0.0 released (Node 24 migration); GitHub is removing Node 20 from hosted runners 2026-09-16 | Keeps release automation on a supported runtime ahead of the deprecation deadline |

**Deprecated/outdated:**
- `softprops/action-gh-release@v2` and earlier: still functions today but runs on Node 20, which GitHub hosted runners will stop supporting 2026-09-16. `@v2.6.2` is the documented final Node-20-compatible release for anyone needing to stay on v2 temporarily.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `gh issue create --label drift` auto-creates the `drift` label on first use without a separate label-creation step | Architecture Patterns / Pattern 2 | Low — if wrong, the first manual `workflow_dispatch` validation run (D-10) would surface a `gh` error immediately, before any real drift week passes; trivial one-line fix (`gh label create drift` as a prior step) |
| A2 | The `sphinx*`/`docutils*`/`typst*` Dependabot patterns do not currently over-match any other dependency in `pyproject.toml`'s dependency tree | Architecture Patterns / Pattern 3 | Low — Phase 1 already audited and pinned the full dependency list (removed `sphinx-testing`); a quick `grep -i "sphinx\|docutils\|typst" pyproject.toml` at plan/execute time trivially confirms this before merging |
| A3 | Recommended `tox -e cov,docs-pdf` is a "meaningful but cheap" drift-signal scope | Architecture Patterns / Pattern 2 | Low — this is explicitly Claude's Discretion per CONTEXT.md; the planner may choose a different (e.g., broader or narrower) tox env subset without contradicting any locked decision |

**If this table is empty:** N/A — see entries above; all are low-risk implementation-detail assumptions, not requirement-level or compliance-level assumptions.

## Open Questions

1. **Should `drift.yml`'s failure step post a fresh comment every week it stays broken, or only comment once and rely on the issue staying open?**
   - What we know: D-06 requires dedup (no duplicate *issues*), not silence on repeat failures.
   - What's unclear: Whether repeated weekly comments on the same open issue are desired (keeps it "bumped"/visible) vs. noisy.
   - Recommendation: Comment on repeat failures (as shown in Pattern 2's skeleton) — this keeps the issue's "last updated" timestamp current so it doesn't look stale/abandoned, while still being exactly one issue (satisfies D-06's core rule). Planner may adjust.

2. **Does the `docs-pdf` tox env require the `--extra docs` install group, and does the drift job's `uv sync` need `--extra dev --extra docs` to match docs.yml's pattern?**
   - What we know: docs.yml installs `--extra dev --extra docs` before running `docs-pdf`; ci.yml's test jobs only install `--extra dev`.
   - What's unclear: Exact final tox-env selection is Claude's Discretion (see Claude's Discretion note in user_constraints); this affects which `--extra` flags the drift job's `uv sync` needs.
   - Recommendation: If the planner scopes `drift.yml` to include `docs-pdf` (recommended, since that's the exact historically-fragile path), install `--extra dev --extra docs` to match docs.yml's own pattern exactly (Pattern 2's skeleton already does this).

## Call-Site Drift Check

Re-verified 2026-07-05 against the current working tree (not assumed from CONTEXT.md):

```
.github/workflows/release.yml:36:        run: uv sync --extra dev
.github/workflows/release.yml:93:          uv sync --extra dev
.github/workflows/docs.yml:31:          uv sync --extra dev --extra docs
.github/workflows/ci.yml:41:        run: uv sync --extra dev
.github/workflows/ci.yml:71:        run: uv sync --extra dev
.github/workflows/ci.yml:92:        run: uv sync --extra dev
.github/workflows/ci.yml:113:        run: uv sync --extra dev
.github/workflows/ci.yml:151:          uv sync --extra dev
.github/workflows/ci.yml:179:        run: uv sync

.github/workflows/docs.yml:67:        uses: softprops/action-gh-release@v2
.github/workflows/release.yml:177:        uses: softprops/action-gh-release@v2
```

**Result: zero drift.** Every line number and content cited in `05-CONTEXT.md`'s D-02 inventory and softprops locations matches exactly. The planner can use the CONTEXT.md line numbers as-is without re-verification, though a final pre-edit `grep` immediately before implementation is still good practice given file contents can shift between research and execution sessions.

## Project Constraints (from CLAUDE.md)

No `./CLAUDE.md` or `./.claude/CLAUDE.md` file exists in this repository at research time. No project-specific directives to enforce beyond `.planning/config.json`'s workflow settings (already reflected in the Validation Architecture and Security Domain sections below).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|--------------|-----------|---------|----------|
| `uv` | Local dry-run of `uv sync --locked` / `uv lock --upgrade` before pushing | Yes | 0.11.25 (local nix store) | GitHub-hosted runners install `astral-sh/setup-uv@v7` independently — local availability only matters for a developer pre-check, not CI execution |
| `gh` (GitHub CLI) | Manual `workflow_dispatch` trigger of `drift.yml` (D-10); local testing of the issue-dedup `gh issue list/create` commands | Yes | 2.95.0 (nixpkgs) | GitHub-hosted runners have `gh` pre-installed with an auto-provisioned `GITHUB_TOKEN`; local `gh` is only needed for the developer to manually fire `workflow_dispatch` and inspect results |
| `git` | Standard repo operations | Yes | 2.54.0 | — |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none — all required tools are present both locally and (independently) on GitHub-hosted runners.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | This phase has no application-level test framework surface — it is a CI/CD-configuration phase. Verification is the CI pipeline itself (push→observe pattern, D-10), consistent with Phases 2-4. |
| Config file | `.github/workflows/ci.yml`, `docs.yml`, `release.yml`, new `drift.yml`; `.github/dependabot.yml` |
| Quick run command | `grep -c "uv sync" .github/workflows/*.yml` (call-site count sanity check, see Code Examples) |
| Full suite command | Push a branch, open a PR targeting `main`, observe `ci.yml`/`docs.yml` green (D-10); manually `gh workflow run drift.yml` + `gh run watch` for DUR-02 (cannot be observed via a normal PR) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|--------------|
| DUR-01 | Every `uv sync` call site has `--locked` appended, existing `--extra` flags preserved | config/static-check | `grep -n "uv sync" .github/workflows/*.yml \| grep -v -- "--locked"` (expect empty) | ✅ existing files |
| DUR-01 | `--locked` gate is provably load-bearing (fails when lock is desynced) | inherent-semantics (not re-tested; D-03 notes proving this is redundant since the lock is currently in sync) | — (no command needed; documented `uv` behavior is sufficient per D-03) | N/A |
| DUR-02 | `drift.yml` runs weekly, resolves latest deps, exercises them, reports via deduplicated issue on failure | manual smoke test (scheduled jobs can't be PR-observed) | `gh workflow run drift.yml && gh run watch` | ❌ Wave 0 — `drift.yml` is a new file, doesn't exist yet |
| DUR-02 | `drift.yml` is NOT in `main`'s required status checks | config/manual check | `gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq '.contexts'` (expect no `drift-check` entry) | N/A — branch-protection check, not a repo file |
| DUR-03 | `dependabot.yml` groups sphinx/docutils/typst | config/static-check | `grep -A6 "sphinx-typst-stack" .github/dependabot.yml` (or equivalent group-name check) | ❌ Wave 0 — group block doesn't exist yet |
| DUR-04 | CI badge renders and links correctly in README | manual visual check (GitHub renders markdown; badge SVG is served live by GitHub) | Open README on GitHub after merge, confirm badge image loads and links to `actions/workflows/ci.yml` | ❌ Wave 0 — badge line doesn't exist yet |
| D-11 | `softprops/action-gh-release@v3` runs successfully | tag-gated smoke test (NOT exercised by a normal PR — see Pitfall 3) | `docs.yml`'s release step only fires on `refs/tags/v*`; `release.yml` supports `workflow_dispatch` with a `tag` input for manual testing | N/A — existing workflow files, edited not created |

### Sampling Rate
- **Per task commit:** `grep`-based static checks (call-site counts, group-block presence) — near-instant.
- **Per wave merge / phase gate:** push→observe PR against `main` for DUR-01/03/04/D-11's CI-visible parts; separate manual `workflow_dispatch` of `drift.yml` for DUR-02 (per D-10 — cannot be folded into the same PR observation since scheduled/dispatch-only workflows don't run on `pull_request` events).
- **Phase gate:** All of ci.yml/docs.yml green on the PR (existing required checks) + drift.yml manually confirmed to (a) run to completion and (b) correctly dedupe/report on a forced-failure test run, before `/gsd-verify-work`. D-11's tag-gated softprops steps may need explicit human sign-off deferring full confirmation to the next real release tag, per Pitfall 3.

### Wave 0 Gaps
- [ ] `.github/workflows/drift.yml` — does not exist yet; entire file is new (DUR-02)
- [ ] `.github/dependabot.yml` `groups:` block — does not exist yet (DUR-03)
- [ ] README badge line — does not exist yet (DUR-04)
- [ ] No test-framework install needed — this phase has no pytest/jest-style automated test surface; verification is entirely CI-pipeline-observation and static config checks as mapped above.

## Security Domain

### Applicable ASVS Categories

This phase has no web-application attack surface (no auth, no session, no user input, no cryptography) — ASVS V2/V3/V4/V5/V6 as templated are not applicable. The relevant security domain here is **CI/CD supply-chain and workflow-permissions hygiene**, which the phase's own decisions already address:

| Concern | Applies | Standard Control |
|---------|---------|-------------------|
| V2 Authentication | No | N/A — no application auth surface touched |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | No | N/A — no user input processed |
| V6 Cryptography | No | N/A |
| Workflow token least-privilege | Yes | `drift.yml`'s new `permissions:` block should scope to exactly `contents: read` + `issues: write` — do NOT default to broad/unset permissions (unset `permissions:` on a workflow grants the default, broader token scope). This mirrors the repo's existing pattern in `docs.yml`/`release.yml`, which already declare explicit `permissions:` blocks. |
| Third-party Action supply-chain risk | Yes | D-06's chosen mechanism (native `gh` CLI in a `run:` step) avoids introducing any *new* third-party Marketplace Action for the issue-dedup logic — reduces, rather than expands, this phase's supply-chain surface. The one Action version *bump* in scope (`softprops/action-gh-release@v2→v3`) is a same-maintainer major-version bump already used elsewhere in the repo's trust boundary, not a new dependency. |
| SHA-pinning Actions to commit hashes | Explicitly deferred | D-12 (deferred to a future milestone) — this phase intentionally continues the repo's existing moving-major-tag convention (`@v6`, `@v7`, `@v3`), consistent with Phases 1-4; not a regression introduced by this phase. |

### Known Threat Patterns for GitHub Actions CI/CD

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Overly broad `permissions:` on a new workflow (`drift.yml`) granting write access beyond what's needed | Elevation of Privilege | Explicit minimal `permissions:` block (`contents: read`, `issues: write` only) — shown in Pattern 2's skeleton above |
| A scheduled job silently becoming a required check and blocking all merges when it (expectedly) sometimes fails | Denial of Service (self-inflicted) | D-07 — verify via `gh api .../branches/main/protection/required_status_checks` that `drift.yml`'s job name never appears in the required-checks list |
| Dependency-confusion / lone malicious-looking version bump slipping through unreviewed because Dependabot PRs for a tightly-coupled cluster (sphinx/docutils/typst) land separately and get rubber-stamped individually | Tampering | DUR-03's grouping (D-08) — a single grouped PR forces one combined review instead of N independent low-scrutiny reviews, directly the mitigation this milestone's `kai`-class break argues for |

## Sources

### Primary (HIGH confidence)
- [GitHub Docs — Scheduling issue creation](https://docs.github.com/en/actions/use-cases-and-examples/project-management/scheduling-issue-creation) — exact `gh issue list`/`create`/`close` dedup pattern, `permissions: issues: write` requirement
- [GitHub Docs — Adding a workflow status badge](https://docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge) — exact badge URL form and query-parameter options
- [GitHub Docs — Dependabot options reference](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference) — `groups:`/`patterns:`/`exclude-patterns:` syntax
- Codebase — `grep -n` verification of all 9 `uv sync` call sites and 2 softprops locations against the current working tree (2026-07-05)
- Codebase — `tox.ini` confirms `uv-venv-lock-runner` on every relevant env

### Secondary (MEDIUM confidence)
- [uv docs — Locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/) (via WebSearch synthesis) — `--locked` failure semantics, `--upgrade` re-resolution semantics
- [softprops/action-gh-release releases page](https://github.com/softprops/action-gh-release/releases) (via WebFetch) — confirmed v3.0.0/v3.0.1 exist, Node 24 migration, v2.6.2 as last Node-20 release
- WebSearch synthesis on GitHub Actions cron syntax (5-field, UTC, 5-minute minimum interval, 60-day inactivity auto-disable)

### Tertiary (LOW confidence)
- None — all claims in this document were either codebase-verified or sourced from official GitHub/Astral documentation pages during this session.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new packages; all tooling already in use, versions confirmed against official release pages
- Architecture: HIGH — every pattern sourced from official GitHub/uv documentation, cross-checked against the actual repo's existing conventions
- Pitfalls: HIGH — derived directly from CONTEXT.md's own explicit decision rationale (D-01/D-04/D-05/D-06/D-07) plus one independently-identified gap (Pitfall 3, tag-gated softprops verification)

**Research date:** 2026-07-05
**Valid until:** 30 days (stable domain — GitHub Actions/Dependabot/uv config surfaces change infrequently; re-verify `softprops/action-gh-release` tag currency and `uv` flag semantics if this research is reused past that window)
