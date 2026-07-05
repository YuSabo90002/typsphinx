# Phase 5: Durability Guardrails - Context

**Gathered:** 2026-07-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Close the milestone by making the silent multi-year dependency rot this cycle
fixed **structurally unable to recur unnoticed**. CI gains a lockfile-currency
gate, a weekly non-blocking drift-detection job, grouped Dependabot updates for
the `sphinx`/`docutils`/`typst` cluster, and a visible CI status badge. Lands on
top of the confirmed-green Phase 4 baseline.

**In scope (DUR-01..04 + one carried-over hardening item):**
- **DUR-01:** Add `uv sync --locked` to every `uv sync` call site across
  `ci.yml`/`docs.yml`/`release.yml` so a stale/silently-rewritten `uv.lock`
  fails the build loudly.
- **DUR-02:** New `.github/workflows/drift.yml` — weekly `schedule:`, resolves
  latest deps (`uv lock --upgrade`) and runs test/build, non-blocking (not in
  `main`'s required checks), auto-files/updates a GitHub Issue on breakage.
- **DUR-03:** Add a `groups:` entry to the existing `.github/dependabot.yml`
  `pip` ecosystem that bundles `sphinx`/`docutils`/`typst` into one PR.
- **DUR-04:** Add the CI workflow status badge to `README.md`'s badge row.
- **Carried-over hardening (D-11):** Bump `softprops/action-gh-release@v2 → @v3`
  (node24) in `docs.yml` (line 67) and `release.yml` (line 177) — the node20
  straggler Phase 4 explicitly deferred to Phase 5.

**Out of scope (this phase / milestone):**
- **SHA-pinning GitHub Actions to commit hashes** — deferred to a future
  milestone (D-12). New supply-chain-hardening category beyond DUR-01..04;
  would require rewriting every action ref + ongoing hash maintenance, inflating
  a maintenance cycle's scope.
- Broadening Dependabot grouping beyond the `sphinx`/`docutils`/`typst` cluster
  (dev-tool grouping, whole-runtime grouping) — DUR-03 scope is the risk cluster
  only (D-08).
- Any forward-port to sphinx 9 / typst 0.15 / configurable `@preview` versions —
  deferred to a future milestone (v2 FWD-01/02/03).

</domain>

<decisions>
## Implementation Decisions

### DUR-01 — Lockfile-currency gate
- **D-01:** **Add `--locked` to every `uv sync` call site**, not a single
  dedicated `uv lock --check` gate job and not ci.yml-only. Rationale: `uv.lock`
  is the single source of truth every workflow resolves from; forcing all jobs
  to fail on lock/pyproject desync is the milestone-consistent, zero-extra-job
  approach and closes the release/docs re-resolution path too.
- **D-02 (call-site inventory for planner):** 9 `uv sync` occurrences must all get
  `--locked`:
  - `ci.yml` lines 41, 71, 92, 113, 151 (`uv sync --extra dev`) and **179
    (`uv sync`, no `--extra`)** — do not miss the bare one in the example-build job.
  - `docs.yml` line 31 (`uv sync --extra dev --extra docs`).
  - `release.yml` lines 36 and 93 (`uv sync --extra dev`).
  Preserve each line's existing `--extra` flags; append `--locked`.
- **D-03 (verify the gate actually gates) [informational]:** `uv sync --locked`
  fails when `uv.lock` is out of sync with `pyproject.toml`. Because the lock is
  currently in sync (Phase 4 regenerated it), the green run alone doesn't prove
  the gate bites. Planner should note this — the proof that it fails-loud is
  inherent to `--locked` semantics; no need to intentionally desync in CI.
  Tagged `[informational]`: no separate implementable action beyond DUR-01's
  `--locked` edits (already acknowledged in plan 05-01); not separately tracked.

### DUR-02 — Weekly drift-detection job
- **D-04:** **Separate `.github/workflows/drift.yml`** (not a `schedule:` +
  `continue-on-error` job bolted onto `ci.yml`) — keeps the scheduled/advisory
  concern out of the per-PR blocking pipeline and keeps `ci.yml` focused.
- **D-05:** The job **resolves latest deps and exercises them**: `uv lock
  --upgrade` (ignore the committed lock intentionally — this job's purpose is to
  detect forward drift), then run the test/build to surface a `kai`-class break
  early. Does NOT commit the upgraded lock.
- **D-06:** **On failure, auto-file/update a GitHub Issue** so drift is a visible,
  persistent signal rather than a buried red X. Use a single-issue-update pattern
  (dedupe by title/label) so weekly runs don't spam duplicate issues. Planner
  picks the mechanism (e.g. `gh issue` in a step, or a maintained
  create-issue action) — the *rule* is: visible, deduplicated, non-spammy.
- **D-07:** **Non-blocking** — `drift.yml` must NOT be added to `main`'s required
  status checks (contrast the Phase-4 branch-protection fix which *added* required
  checks). It reports; it never blocks a merge.

### DUR-03 — Dependabot grouping
- **D-08:** **Group exactly `sphinx`/`docutils`/`typst`** into one dedicated group
  under the existing `pip` ecosystem in `.github/dependabot.yml` (append a
  `groups:` block; keep the `github-actions` ecosystem entry untouched). This is
  DUR-03 verbatim — one grouped PR prevents a lone `typst` bump from
  reintroducing the `kai` break. Suggested group name `sphinx-typst-stack` with
  patterns `sphinx*` / `docutils*` / `typst*`; planner confirms exact patterns.
  Do NOT broaden to whole-runtime or add a dev-tool group.

### DUR-04 — CI status badge
- **D-09 (Claude's discretion, pre-decided):** Add **one CI-workflow status badge**
  to the existing `README.md` badge row (lines 3–7, alongside PyPI/Python/License/
  black/Docs badges). Badge URL form:
  `https://github.com/YuSabo90002/typsphinx/actions/workflows/ci.yml/badge.svg`
  linking to the workflow's Actions page. A single CI badge satisfies DUR-04;
  no separate docs-workflow badge unless the user later asks.

### Carried-over hardening
- **D-11:** **Bump `softprops/action-gh-release@v2 → @v3`** (node24) in
  `docs.yml` line 67 and `release.yml` line 177. This is the Phase-4 tracked
  node20 straggler (Node 20 removed from hosted runners 2026-09-16); `@v3` is a
  drop-in node24 release for this repo's usage. Log this in PROJECT.md Key
  Decisions at phase transition.

### Claude's Discretion
- Exact Issue-dedup mechanism/action for DUR-02 (D-06 rule stands: visible +
  deduplicated).
- Exact Dependabot `patterns` glob strings and group name (D-08).
- Badge markdown placement within the existing badge row (D-09).
- Whether `drift.yml` also runs the docs-pdf build in addition to the test
  matrix subset — planner scopes to a meaningful-but-cheap drift signal.

### Verification gate (carried pattern)
- **D-10:** Reuse the **push→observe** gate for the verifiable parts (DUR-01
  `--locked` green, DUR-03/04 render correctly, D-11 action bump green) on a PR
  targeting `main`. DUR-02's scheduled job cannot be observed via a normal PR
  run — validate it by a manual `workflow_dispatch` trigger (add
  `workflow_dispatch:` to `drift.yml`) rather than waiting a week.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` §Durability Guardrails — DUR-01, DUR-02, DUR-03,
  DUR-04 (the four locked requirements).
- `.planning/ROADMAP.md` §Phase 5 — goal + 4 success criteria.
- `.planning/PROJECT.md` — Key Decisions table (Phase 1 upper-bound pinning,
  Phase 4 node20/softprops deferral row). D-11 (softprops bump) and D-12
  (SHA-pin deferral) must be logged here at phase transition.

### Config surfaces to edit
- `.github/workflows/ci.yml` — 6 `uv sync` sites (lines 41/71/92/113/151/179) → `--locked`.
- `.github/workflows/docs.yml` — `uv sync` line 31 → `--locked`; `softprops/action-gh-release@v2` line 67 → `@v3`.
- `.github/workflows/release.yml` — `uv sync` lines 36/93 → `--locked`; `softprops/action-gh-release@v2` line 177 → `@v3`.
- `.github/workflows/drift.yml` — NEW FILE (DUR-02).
- `.github/dependabot.yml` — existing; append `groups:` to the `pip` ecosystem entry (DUR-03).
- `README.md` — badge row lines 3–7 (DUR-04).

### Prior-phase context (patterns carried forward)
- `.planning/phases/04-refresh-dev-tooling/04-CONTEXT.md` — node20/softprops
  deferral (its `<deferred>`), push→observe gate (D-05), branch-protection
  required-check management.
- `.planning/phases/01-pin-runtime-dependencies-to-known-good/01-CONTEXT.md` —
  upper-bound anti-drift pinning philosophy that DUR-03 grouping reinforces.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.github/dependabot.yml` **already exists** (pip weekly + github-actions
  monthly, no groups) — DUR-03 is an *append*, not a new file.
- Phase 2/3/4 push→observe workflow on a PR targeting `main` — reuse verbatim for
  the D-10 verification of the observable changes.
- Every tox env uses `runner = uv-venv-lock-runner` (resolves from `uv.lock`), so
  the `--locked` gate at the `uv sync` layer is what actually pins what CI runs.

### Established Patterns
- `uv.lock` is the single source of truth CI/tox resolve from — DUR-01 hardens
  the "is the committed lock actually what we run?" invariant.
- Upper-bound pinning (`>=x,<next-major`) is the project's drift defense; DUR-03
  grouping is its Dependabot-layer complement (a lone bump can't slip through).
- README already carries a badge row (PyPI/Python/License/black/Docs) — DUR-04
  follows the existing convention.

### Integration Points
- `main` branch protection has a curated required-status-check set (Phase 4 fixed
  it to ubuntu 3.10–3.13 + Lint/Type/Coverage/Build). DUR-02's `drift.yml` must
  be kept OUT of that set (D-07). DUR-01's `--locked` rides inside existing
  required jobs, so no branch-protection change is needed for it.

</code_context>

<specifics>
## Specific Ideas

- Repo slug for badge/URLs: `YuSabo90002/typsphinx` (per README links).
- `softprops/action-gh-release` appears in exactly 2 files: `docs.yml:67`,
  `release.yml:177` (both `@v2`).
- The `kai`-class break (typst 0.15 ⇄ pinned `@preview` package) is the exact
  failure mode DUR-02 (early drift alarm) and DUR-03 (grouped bump) exist to
  catch next time — frame the drift job/grouping around that scenario.

</specifics>

<deferred>
## Deferred Ideas

- **SHA-pin GitHub Actions to commit hashes** (supply-chain hardening) → future
  milestone (D-12). On the table for Phase 5 but consciously deferred: new
  category, high maintenance surface, outside DUR-01..04. Revisit as a dedicated
  security-hardening item.
- Broader Dependabot grouping (dev tools, whole runtime) → not needed; DUR-03 is
  scoped to the risk cluster (D-08).

None of the above expand this phase — discussion stayed within DUR-01..04 plus
the explicitly-carried softprops item.

</deferred>

---

*Phase: 5-durability-guardrails*
*Context gathered: 2026-07-05*
