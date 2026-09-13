# Phase 66: `.github/dependabot.yml` — `pip` → `uv` Ecosystem - Research

**Researched:** 2026-09-12
**Domain:** GitHub Dependabot configuration (`.github/dependabot.yml`), GitHub branch protection / CI
triggers, uv lockfile versioning
**Confidence:** HIGH — every load-bearing claim below is either a live `gh api`/`git`/`uv` measurement
taken this session or a direct quote from an authoritative source (GitHub's own docs repo, Astral's
own docs/dependabot-core repo), re-measured independently of CONTEXT.md's same-day figures.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: Phase 66 opens and merges a separate PR to `main` that changes only `.github/dependabot.yml`; the same bytes are committed on the milestone branch.** Reason (measured): GitHub docs,
  `about-the-dependabot-yml-file.md:46` — "You must store this file in the `.github` directory of
  your repository in the default branch (typically `main`)". Under the roadmap as written, `main`
  is reached only at REL-12, so no `uv`-ecosystem PR could open inside the milestone. ROADMAP
  constraint 2 carries an `AMENDED 2026-09-12` block (written and committed with this CONTEXT);
  REL-12 itself is unchanged. The PR branches from `origin/main`, carries one commit whose only
  file is `.github/dependabot.yml`, and its file content is byte-identical to the milestone
  branch's so the REL-12 merge is conflict-free (verify with `git diff` of the file between the two
  tips before merging). PR title/body in English and terse. Merge only after all 6 required checks
  are green. — **Reversibility:** one-way — once on `main`, dependabot acts on it (opens PRs, may
  change #123/#128's state); a revert PR cannot undo PRs dependabot has already opened or closed.
  The planner must put a `checkpoint:decision` (owner go-ahead) immediately before the merge.

- **D-02: Replace `pip` with `uv` outright (no transitional dual entry), and snapshot #123/#128 immediately before and after the merge.** Measured: neither GitHub's docs
  (`about-the-dependabot-yml-file.md`, `dependabot-pull-requests.md`, `dependabot-errors.md`) nor a
  dependabot-core issue search states what happens to open PRs when their ecosystem is removed from
  the configuration — unmeasured, and only observable by doing it. Accepted because the old PRs
  cannot prove DEP-02 anyway (they are `pip`-ecosystem and never regenerate `uv.lock`); the proof
  must come from fresh `uv` PRs, and fresh successors are expected because ruff 0.16 / docutils 0.23
  lie outside the current ranges. Snapshot = `gh pr view <n> --json state,closedAt,closed,comments,headRefName,updatedAt`
  (or equivalent) for both PRs, recorded verbatim with timestamps, before the merge and after the
  first post-merge dependabot run. Also record whether `uv`-ecosystem PRs open for `ruff` /
  `docutils` while the `pip` PRs are still open — that is Phase 67 SC#2's measurement, which this
  merge now exercises first; record it, do not judge it. Phase 66 does **not** close, merge,
  comment on, or `@dependabot`-command #123/#128. Any close dependabot performs is a **mechanical**
  close for Phase 67 to cite, never DEP-05's disposal.

- **D-03: Do not wait for the Monday 00:00 schedule. After the merge, check for a `uv`-ecosystem PR; if none has opened, the owner clicks "Check for updates" (Insights → Dependency graph → Dependabot, per `re-run-dependabot-jobs.md:20`).** There is no public API for triggering a
  version-update job, so this is a `checkpoint:human-action`. GitHub's docs are ambiguous on whether
  a config change triggers an immediate run (`about-the-dependabot-yml-file.md:50`); record which
  happened.

- **D-04: SC#1 is closed by reading a real `uv`-ecosystem PR's commit contents** — a PR whose head
  commit lists both `pyproject.toml` and `uv.lock` (e.g. `gh pr view --json commits,files` plus
  `git show --name-only <sha>`), branch prefix `dependabot/uv/…`. A lockfile-only PR (in-range
  update touching only `uv.lock`) does not close SC#1's "same commit" clause on its own; it is
  recorded under D-06 instead. "Dependabot accepts the configuration" is also recorded from
  dependabot's own output (how to read it — Dependabot tab / job log / PR existence — is a research
  item; if only the owner can see it, it is part of the D-03 human checkpoint).

- **D-05: The "v0.11 vs 0.12" gap is recorded as a stale-documentation finding, closed by two legs of evidence; REQUIREMENTS.md's wording stays literal.** Leg 1 (source, measured
  2026-09-12): dependabot-core `uv/Dockerfile:15` is `FROM ghcr.io/astral-sh/uv:0.12.7` and
  `uv/helpers/requirements.txt` pins `uv==0.12.7` (0.11.31 → 0.12.1 in dependabot-core #15770,
  2026-08-12), while GitHub's supported-ecosystems table (`supported-package-managers.md`,
  `dependabot-options-reference.md:618`) still says `v0.11`. Re-measure at execution time and
  record literally. Leg 2 (behaviour): the real `uv`-ecosystem PR's `uv.lock` still reads
  `version = 1` / `revision = 3`, and `uv lock --check` with CI's uv (`latest`, record the exact
  version) passes on that PR's head. Source of `dependabot-core`'s `main` is not proof of the
  image deployed on github.com, which is why leg 2 is required. The fallback custom workflow comes
  into play **only** if leg 2 fails; if it does, record it and HALT for the owner.

- **D-06: Carry the block across unchanged and add no keys (no `versioning-strategy`), then record observed behaviour.** Record from real PRs: whether grouped `sphinx*`/`docutils*`/`typst*`
  bumps arrive as one `sphinx-typst-stack` PR with the two exclusions honoured, whether the
  `dependencies` / `automated` labels are applied (and whether any extra ecosystem label appears —
  `dependabot-options-reference.md:464`), how many PRs open against the limit of 5, and whether
  in-range updates now arrive as lockfile-only PRs (new under `uv`, since `pip` had no lockfile).
  Expectation, to be confirmed not assumed: dependabot-core #15693 (merged 2026-08-18) makes `uv`
  inherit `pip`'s library detection, and typsphinx is on PyPI, so `auto` should resolve to the same
  range-widening behaviour `pip` showed (#123 widened `<0.16` → `<0.17`). Any divergence is written
  down, not fixed in this phase.

### Claude's Discretion

- Branch name for the `main`-bound PR; merge method (follow the style of recent merges on `main`).
- Whether the milestone-branch commit lands first and is cherry-picked, or vice versa (content
  must be byte-identical either way).
- Evidence file naming and plan split; how long to poll for the first `uv` PR before invoking the
  D-03 human checkpoint.

### Deferred Ideas (OUT OF SCOPE)

- **Phase 67 SC#4 and PROJECT.md state "neither #123 nor #128 is a grouped bump" — false.** #128
  is a `sphinx-typst-stack` group PR (title and branch). Raise at Phase 67 discuss; not amended here.
- Setting `versioning-strategy` (e.g. `increase-if-necessary`) if lockfile-only PR volume under
  `uv` turns out to crowd the limit of 5 — only after D-06's observation, and as its own decision.
- DEP-02 (CI observed passing on a real dependabot PR) and DEP-05 (disposal of #123/#128) — Phase 67.
- Any workflow edit (ROADMAP constraint 3). Documentation of the landed mechanism (Phase 68).
  Anything under `typsphinx/` (constraint 13).

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DEP-01 | `.github/dependabot.yml` uses `package-ecosystem: "uv"`, and dependabot opens PRs updating `pyproject.toml` and `uv.lock` in the same commit | See "The exact diff" (Code Examples), "Getting the configuration onto `main`" (Architecture Patterns), and "How to read dependabot's own output" (Pitfall 1) for the D-01/D-04 mechanics |
| DEP-03 | The `sphinx-typst-stack` grouping, `labels` and `open-pull-requests-limit` are confirmed to behave as before under the new ecosystem, or the divergence is recorded | See "Pre-existing label-application gap" (Pitfall 2), "`groups` is ecosystem-agnostic" and "`versioning-strategy` now covers `uv`" (State of the Art / Don't Hand-Roll) |
| DEP-04 | Dependabot's supported uv version (`v0.11`) is measured against the uv that CI installs (currently 0.12.x) and against this repo's lock (`revision = 3`), and the result recorded | See "The v0.11/v0.12 gap is smaller than it looks" (Summary, Pitfall 3) and "Re-measurement commands" (Environment Availability) |

</phase_requirements>

## Summary

This phase is a single-file YAML edit (`.github/dependabot.yml`) plus a merge-to-`main` operation;
there is no application code, no new dependency, and no workflow edit. The research burden is
therefore almost entirely **measurement of live GitHub/Astral/dependabot-core state**, not stack
selection. Re-measuring every claim CONTEXT.md and PROJECT.md made on 2026-09-02/2026-09-12
confirms them to be accurate as of today, with one important exception: **the "local uv 0.11.25"
figure quoted in PROJECT.md's `AMENDED 2026-09-02` block and ROADMAP's SC#2 text is now stale.**
Phase 65 (completed today, 2026-09-12) reverted `tox-uv-bare` → `tox-uv` and re-synced the main
checkout onto the lock-pinned uv, and this session's direct measurement shows the environment's
`uv --version` is now **0.12.13** — matching CI's `astral-sh/setup-uv@v7` `version: "latest"`, not
the 0.11.25 figure the roadmap text carries forward. This does not change any locked decision (D-05
already treats the number as "record literally, re-measure at execution time"), but the planner
should not copy "0.11.25" into a plan as current fact.

The uv-version compatibility question (DEP-04) is less risky than the roadmap's framing suggests.
Astral's own docs state that a uv.lock's `revision` field (ours is `3`) tracks **backwards-compatible**
changes and "will not cause older versions of uv to error" — only the `version` field (schema
version, ours is `1`, unchanged since well before the 0.11/0.12 split) can cause an older uv to
reject a lockfile outright `[CITED: docs.astral.sh/uv/concepts/resolution]`. Combined with the fact
that dependabot-core's `main` branch (re-measured today) pins `uv==0.12.7` — not the documented
`v0.11` — in both `uv/Dockerfile` and `uv/helpers/requirements.txt`, the practical risk that a real
`uv`-ecosystem dependabot job cannot parse this repo's `revision = 3` lockfile looks low. D-05's
"measure, don't assume" stance is still correct — dependabot-core's `main` branch is not proof of
what's deployed on github.com — but the fallback custom workflow is unlikely to be needed.

Every other config-carry-across item (DEP-03) was checked against both GitHub's documentation and
this repository's own dependabot PR history. One finding worth flagging plainly: **the `dependencies`
and `automated` labels dependabot.yml requests do not exist in this repository today** (`gh label
list` returns none of the four labels the two `updates` entries request), and both live dependabot
PRs (#123, #128) currently carry **zero labels** — confirming GitHub's documented behaviour ("If any
of these labels is not defined in the repository, it is ignored") is already firing under `pip`. This
is a **pre-existing** condition, not something the ecosystem switch introduces or fixes; DEP-03's
"confirmed to behave as before" bar is met by this being unchanged, but the planner should record it
rather than be surprised when the fresh `uv`-ecosystem PR also shows no labels.

Branch-protection and CI-trigger measurement closes the "will the PR even be mergeable" question
cleanly: `ci.yml`'s `push`/`pull_request` triggers carry **no `paths` or `paths-ignore` filter at
all**, so a PR touching only `.github/dependabot.yml` runs every job, including the 6 checks `main`
requires (`Test Python 3.12 on ubuntu-latest`, `Test Python 3.13 on ubuntu-latest`, `Lint and Format
Check`, `Type Check`, `Code Coverage`, `Build Package`) — no workaround is needed.

**Primary recommendation:** change only the four lines under the Python `updates` entry
(`package-ecosystem: "pip"` → `"uv"`; everything else byte-identical), open a normal PR from
`origin/main`, let CI run unmodified, merge with a standard two-parent merge commit (the convention
every recent PR into `main` — release and dependabot alike — already uses), and treat all of
D-03/D-04/D-05's "confirm or record divergence" language as literal: this research found no
documented reason grouping, labels, the PR limit, or the version gap should behave differently, but
none of that is provable except by reading dependabot's own output after the merge.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Dependency version scanning & PR authoring | GitHub Platform (Dependabot service, external SaaS) | — | Dependabot runs entirely on GitHub's infrastructure, driven by the `updates` entry's `package-ecosystem` key; typsphinx contributes only the config file, never the scanning logic |
| Ecosystem-specific manifest/lockfile parsing (`pyproject.toml` + `uv.lock`) | GitHub Platform (`dependabot-core`'s `uv` updater image) | — | The `uv/Dockerfile`-pinned `uv` binary inside dependabot-core's updater container does the actual resolve/lock; this repo has no control over which uv binary runs there |
| Repository config declaring what to scan | Repository config (`.github/dependabot.yml`, tracked in git, default branch only) | — | The only artifact this phase edits; GitHub explicitly requires it live on the default branch (`about-the-dependabot-yml-file.md:46`) |
| Verifying a proposed bump compiles/tests | CI (GitHub Actions, `ci.yml`) | — | `uv sync --extra dev --locked` is the gate that was previously refused by a stale lock; this phase does not touch `ci.yml` (ROADMAP constraint 3) but its behavior against dependabot PRs is what DEP-01/SC#1 observes |
| Local dev tooling parity (confirming lockfile compatibility) | Local dev tooling (`uv` CLI on the maintainer's/executor's machine) | CI | Used only to re-run `uv lock --check` as a sanity probe before/alongside the real-PR observation; not authoritative for DEP-04 (D-05 leg 2 requires the observation on the PR's own head, not a local proxy) |

## Standard Stack

### Core

No new library, package, or GitHub Action is introduced by this phase. The only "stack" element
that changes is a single YAML enum value.

| Config key | Old value | New value | Purpose | Why standard |
|------------|-----------|-----------|---------|---------------|
| `updates[0].package-ecosystem` | `"pip"` | `"uv"` | Tells dependabot which updater image parses the manifest/lockfile pair | `uv` has been a first-class dependabot ecosystem since GA (`dependabot-uv-support` feature flag is `fpt: '*'`, i.e. live on all github.com repositories) `[VERIFIED: gh api repos/github/docs/contents/data/features/dependabot-uv-support.yml — "versions: fpt: '*', ghec: '*', ghes: '> 3.16'"]` |

### Supporting

Not applicable — no supporting libraries. `versioning-strategy`, `groups`, `labels`, and
`open-pull-requests-limit` are all pre-existing config keys carried across unchanged (D-06); none is
newly added.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Native `uv` ecosystem | Custom GitHub Actions workflow running `uv lock` on dependabot PRs | Rejected by the owner 2026-09-02 (PROJECT.md `AMENDED` block) — every failure mode Pitfalls research found (forced read-only `GITHUB_TOKEN` on `pull_request`, `pull_request_target` exposure if moved to a write-capable trigger, pushed commits not retriggering CI, dependabot force-pushing over commits lacking `[dependabot skip]`) is specific to that workflow and disappears with the ecosystem switch. Retained only as a fallback if D-05 leg 2 fails. |
| Native `uv` ecosystem | Drop the Python `updates` entry entirely, rely on `drift.yml`'s weekly re-resolve | Considered in the source todo (`2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md`, solution shape 2) and superseded — loses per-package PR granularity and grouped updates; not revisited here since the ecosystem switch is strictly better and already owner-approved |
| Native `uv` ecosystem | Drop `--locked` from CI steps | Explicitly rejected in the source todo as "the worst of the three" — removes the exact-install reproducibility guarantee `--locked` exists for; ROADMAP constraint says `--locked` stays everywhere |

**Installation:** None — no package install, no `npm install`/`pip install`/`cargo install` step. The
change is a 1-line-changed, 0-line-added, 0-line-removed edit to a tracked YAML file (see Code
Examples for the exact diff).

**Version verification:** N/A — no package version to pin. The one "version" in play is the *uv
binary version dependabot itself runs*, which this repository cannot pin or select; DEP-04's
job is to measure it, not choose it (see Common Pitfalls #3 and Environment Availability).

## Package Legitimacy Audit

**Not applicable to this phase.** No `npm install`, `pip install`, `cargo install`, or any other
package-manager add command is executed by this phase's plan. The only "package" concept touched is
the `package-ecosystem` config enum value `"uv"`, which is not a downloadable artifact — it is a
string GitHub's own dependabot service interprets, verified directly against GitHub's documentation
repository (`github/docs`) rather than against an npm/PyPI/crates registry. The
`package-legitimacy check` seam is for verifying third-party packages a plan would install; skipping
it here does not weaken any claim in this document, since every "package"-shaped claim in this
research (`uv`, `pip`) is an *ecosystem identifier* GitHub defines, cross-checked against
`github/docs`' `dependabot-options-reference.md` and `supported-package-managers.md` directly.

## Architecture Patterns

### System Architecture Diagram

```
                    ┌─────────────────────────────────────────┐
                    │  This phase's only edit:                  │
                    │  .github/dependabot.yml on `main`          │
                    │  (package-ecosystem: "pip" → "uv")         │
                    └───────────────────┬─────────────────────┘
                                        │ read by (default branch only,
                                        │ about-the-dependabot-yml-file.md:46)
                                        ▼
                    ┌─────────────────────────────────────────┐
                    │  GitHub Dependabot service                 │
                    │  (external SaaS — no repo control)         │
                    │  - parses config on push to default branch │
                    │  - schedule: weekly, Monday 00:00           │
                    │  - "Check for updates" = only manual trigger│
                    │    (UI-only, Insights→Dependency graph→     │
                    │    Dependabot tab; NO public API — confirmed│
                    │    dependabot-core#3080)                    │
                    └───────────────────┬─────────────────────┘
                                        │ spins up dependabot-core's
                                        │ `uv` updater image
                                        │ (pins uv==0.12.7 on `main`,
                                        │  measured 2026-09-12,
                                        │  NOT the documented v0.11)
                                        ▼
                    ┌─────────────────────────────────────────┐
                    │  Resolve pyproject.toml + uv.lock,          │
                    │  apply groups/labels/PR-limit,              │
                    │  open PR: dependabot/uv/<branch>            │
                    │  Commit touches BOTH pyproject.toml         │
                    │  AND uv.lock (this is DEP-01's proof —      │
                    │  the `pip` path never touched uv.lock)      │
                    └───────────────────┬─────────────────────┘
                                        │ PR opened against `main`
                                        ▼
                    ┌─────────────────────────────────────────┐
                    │  ci.yml (unmodified, no paths filter)      │
                    │  6 required checks run unconditionally:    │
                    │  test×2(py312/py313 ubuntu), lint,          │
                    │  type-check, coverage, build                │
                    │  → `uv sync --extra dev --locked` now       │
                    │    succeeds because the lock is fresh       │
                    │    (Phase 67's DEP-02, not this phase)      │
                    └─────────────────────────────────────────┘
```

### Recommended Project Structure

Not applicable in the usual sense (no new source tree). The one file this phase edits:

```
.github/
└── dependabot.yml   # only the Python `updates[0].package-ecosystem` value changes:
                      # "pip" → "uv" — every other key (directory, schedule, groups,
                      # labels, open-pull-requests-limit) is byte-identical
```

### Pattern 1: Config-driven default-branch-only update

**What:** Dependabot reads `.github/dependabot.yml` *only* from the repository's default branch —
never from a feature/PR branch, even for the PR that introduces the change.
**When to use:** This is the reason D-01 requires opening and merging a standalone PR to `main`
rather than waiting for the milestone's own REL-12 merge; every downstream observation (SC#1,
DEP-04, DEP-03) is gated on this file existing on `main`, verbatim:

**Example (verified, quoted from `github/docs`):**
```
You must store this file in the `.github` directory of your repository in the default branch
(typically `main`), at `.github/dependabot.yml` or `.github/dependabot.yaml`.
```
`[VERIFIED: gh api repos/github/docs/contents/content/code-security/concepts/supply-chain-security/about-the-dependabot-yml-file.md — line 46, re-fetched 2026-09-12]`

### Pattern 2: Ecosystem switch is a value swap, not a schema migration

**What:** `package-ecosystem: "pip"` → `"uv"` is the entire config change for the Python
`updates` entry; `directory`, `schedule`, `open-pull-requests-limit`, `labels`, and `groups` are all
keys the `uv` ecosystem consumes identically to `pip` (per Astral's own dependabot guide, which shows
the identical `directory: "/"` / `schedule.interval` shape).
**When to use:** Whenever a project already has a working `pip`-ecosystem `dependabot.yml` and is
migrating to `uv` package management — this is the exact typsphinx scenario.
**Example:**
```yaml
# Source: astral-sh/uv docs/guides/integration/dependabot.md (fetched via GitHub API 2026-09-12)
version: 2

updates:
  - package-ecosystem: "uv"
    directory: "/"
    schedule:
      interval: "weekly"
```
`[VERIFIED: gh api repos/astral-sh/uv/contents/docs/guides/integration/dependabot.md]`

### Anti-Patterns to Avoid

- **Adding a transitional dual `pip` + `uv` entry:** Explicitly rejected by D-02. Two `updates`
  entries pointed at the same `directory: "/"` for two ecosystems that both read `pyproject.toml`
  would keep producing `pip`-ecosystem PRs that fail `--locked` (the defect this phase exists to
  fix) alongside the new `uv`-ecosystem ones, and would also contradict SC#1's "same commit" wording
  since a `pip` PR by definition never regenerates `uv.lock`.
- **Adding `versioning-strategy` speculatively:** D-06 explicitly says add no keys. `versioning-strategy`
  is now documented as supported by `uv` (`dependabot-options-reference.md:985` — "Supported by:
  `bundler`, `cargo`, `composer`, `helm`, `mix`, `npm`, `pip`, `pub`, and `uv`"), so it *would* work,
  but changing default behavior here is explicitly deferred to a future decision, contingent on
  observing whether lockfile-only PR volume crowds the `open-pull-requests-limit: 5` ceiling.
- **Assuming a config-error would be self-evident:** There is no dedicated "config accepted" green
  checkmark. Acceptance is inferred from the *absence* of a failed job in the "Recent update jobs"
  list and the *presence* of PRs opening on schedule/on-demand — see Common Pitfalls #1.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Keeping `pyproject.toml` and `uv.lock` in sync on dependency bumps | A custom GitHub Actions workflow that runs `uv lock` on dependabot PRs and pushes the result back | The native `uv` `package-ecosystem` | Dependabot's `uv` updater already does this atomically in the PR's own commit; the custom-workflow alternative inherits a forced read-only `GITHUB_TOKEN` on `pull_request`-triggered runs (GitHub always downgrades permissions to read-only for PRs from forks/dependabot regardless of the workflow's `permissions:` block), forcing either `pull_request_target` (a well-documented supply-chain risk surface — checking out and running code from an untrusted/bot-authored branch in a context that has write tokens) or a long-lived PAT; a `GITHUB_TOKEN`-authored push also does not retrigger the PR's required checks, so the workflow could report success while the checks the merge gate reads stay stale; and dependabot force-pushes over any commit on its own branches that lacks a `[dependabot skip]` marker in the commit message, so a fix proven once could silently vanish on the next rebase cycle. All four failure modes are specific to the custom-workflow shape and disappear entirely with the native ecosystem — this is why the owner approved replacing the originally-scoped workflow (PROJECT.md `AMENDED 2026-09-02`). |
| Detecting whether a PyPI-published package should widen vs. bump its version range | Custom "is this a library" heuristic in a bespoke workflow | Dependabot's built-in `versioning-strategy: auto` (default) | As of dependabot-core PR #15693 (merged 2026-08-18, `[VERIFIED: gh pr view 15693 --repo dependabot/dependabot-core]`), the `uv` ecosystem's `library?` check was fixed to inherit `pip`'s PyPI-lookup-based detection instead of a narrower uv-specific copy. typsphinx is published on PyPI with a `description` in `pyproject.toml`, so it lands in the "200, `summary` matches → library" row of that PR's own before/after table — unchanged behavior, the same row `pip` already used to widen ruff's constraint in #123 (`<0.16` → `<0.17`). |
| Manually triggering a dependency scan outside the weekly schedule | A script calling some imagined "trigger dependabot" REST endpoint | The "Check for updates" button (Insights → Dependency graph → Dependabot tab) | Confirmed there is **no public API** for this: `dependabot/dependabot-core` issue #3080 ("new Github insights dependency graph has no way of bumping dependencies via api") is open and unresolved, and the only documented path is the UI button `[CITED: github.com/dependabot/dependabot-core/issues/3080]`. This is why D-03 is a `checkpoint:human-action`, not an automatable step. |

**Key insight:** Every "hand-rolled" alternative this domain tempts (a lockfile-sync workflow, a
library-detection heuristic, an API trigger) already exists natively in either dependabot itself or
dependabot-core's `uv` support, and the native versions carry fewer security/reliability failure
modes than the custom equivalents this milestone originally scoped.

## Common Pitfalls

### Pitfall 1: There is no explicit "config accepted" signal — acceptance is read by absence and by result

**What goes wrong:** A plan might look for a "uv ecosystem: OK" badge that does not exist.
**Why it happens:** Dependabot's configuration-acceptance signal is negative evidence (no failed job
appears in the job-log list) plus positive evidence one step removed (a PR actually opens). There is
no REST/GraphQL endpoint that reports "config parsed successfully" for a given `dependabot.yml`
`[CITED: dependabot-core issue #3080 confirms no API surface for triggering or introspecting a
version-update job]`.
**How to avoid:** Read dependabot's own output via the paths GitHub documents, all of which are
UI-only (Insights → Dependency graph → Dependabot tab):
- "Recent update jobs" list per manifest file — shows completed jobs; a failed/errored job (e.g. an
  unparseable config) appears here as a failed entry with a "view logs" link
  `[VERIFIED: gh api repos/github/docs/contents/content/code-security/how-tos/view-and-interpret-data/view-dependabot-logs.md`
  — "The Dependabot job logs list is accessible from the dependency graph tab in your repository."]`.
- "Check for updates" button next to each manifest — this is also how D-03's manual trigger is
  performed `[VERIFIED: gh api repos/github/docs/contents/content/code-security/how-tos/secure-your-supply-chain/manage-your-dependency-security/re-run-dependabot-jobs.md`
  — line 20: "To the right of the affected manifest file, click **Check for updates**..."]`.
- The PR itself opening at all, with branch prefix `dependabot/uv/…` (vs. the old `dependabot/pip/…`).
Both the job-log list and the "Check for updates" button are reachable only in the browser — no
`gh api` call surfaces either. **This means D-04's "dependabot accepts the configuration" clause and
D-03's manual trigger both require the owner** to look at the Dependabot tab; the executor can only
observe the *result* (a PR opening, or not) via `gh pr list`.

**Warning signs:** If, after the config change lands on `main` and either the schedule fires or the
owner clicks "Check for updates", no `dependabot/uv/…` PR opens within a reasonable window and no
job appears in the log list at all (not even a failed one), that is itself worth recording as an
anomaly — GitHub's own docs do not explicitly state whether a bare config-push alone triggers an
immediate run (`about-the-dependabot-yml-file.md:50` is silent on this, matching D-03's framing).

### Pitfall 2: Pre-existing label-application gap will look like a new regression if not flagged first

**What goes wrong:** The `uv`-ecosystem PR opens with no labels, and someone reads this as the
ecosystem switch breaking DEP-03.
**Why it happens:** This repository's label set does **not** include `dependencies` or `automated`
— confirmed via `gh label list` (returns `bug`, `documentation`, `duplicate`, `enhancement`, `good
first issue`, `help wanted`, `invalid`, `question`, `wontfix`, `breaking-change`, `design` — none of
the four labels either `updates` entry in `dependabot.yml` requests). GitHub's documented behavior
for this exact situation: "If any of these labels is not defined in the repository, it is ignored."
`[VERIFIED: gh api repos/github/docs/contents/content/code-security/reference/supply-chain-security/dependabot-options-reference.md`
— line 472]`. This is **already** true today, under `pip`: both open dependabot PRs (#123, #128)
were fetched live via `gh pr view --json labels` and both return `"labels":[]`.
**How to avoid:** Record this as a pre-existing, ecosystem-independent condition when writing up
DEP-03 — the correct claim is "labels behave identically (i.e., identically absent) before and
after the switch," not "labels are now broken."
**Warning signs:** None specific to `uv` — this would need fixing (creating the two labels in the
repo, a one-line `gh label create` call) as a separate, out-of-scope improvement if the owner wants
labels to actually apply; not part of this phase's DEP-03 bar, which is "behaves as before."

### Pitfall 3: The v0.11/v0.12 gap is a documentation lag, not necessarily a functional break — but only a live PR proves it

**What goes wrong:** Treating GitHub's documented "`uv` supported version: v0.11" as meaning a real
job would fail against a `revision = 3` lockfile written by 0.12.x, and reaching for the fallback
custom workflow pre-emptively.
**Why it happens:** The natural reading of a version-support table is "anything outside this range
is unsupported." But two independent pieces of evidence point the other way:
1. dependabot-core's `main` branch (re-measured 2026-09-12, same values CONTEXT.md recorded)
   already pins a **newer** uv than the docs claim: `uv/Dockerfile:15` is
   `FROM ghcr.io/astral-sh/uv:0.12.7 AS uv` and `uv/helpers/requirements.txt:10` is `uv==0.12.7`
   `[VERIFIED: gh api repos/dependabot/dependabot-core/contents/uv/Dockerfile and .../requirements.txt]`
   — the documented "v0.11" in `dependabot-options-reference.md:618` and
   `supported-package-managers.md` looks stale relative to source, exactly as D-05 leg 1 states.
2. Astral's own uv docs explain that a lockfile's `revision` field (ours: `3`) is specifically
   designed **not** to break older uv: "The `revision` field of the lockfile is used to track
   backwards compatible changes to the lockfile. For example, adding a new field to distributions.
   Changes to the revision will not cause older versions of uv to error." Only the `version` field
   (schema version, ours: `1`, unchanged) is a breaking-change signal: "Any given version of uv can
   read and write lockfiles with the same schema version, but will reject lockfiles with a greater
   schema version." `[CITED: docs.astral.sh/uv/concepts/resolution — "Lockfile versioning" section]`
   So even a hypothetical uv 0.11 reading this repo's `version = 1, revision = 3` lock would, per
   Astral's own documented contract, not error on the revision alone.
**How to avoid:** Do not skip D-05 leg 2 because leg 1 looks reassuring. `dependabot-core`'s `main`
branch source is not proof of what image is actually deployed on github.com's production
infrastructure today; the only real proof is `uv lock --check` (or equivalent) succeeding against
CI's own uv version on the real PR's head commit, exactly as D-05 specifies. This session's local
`uv lock --check` against the current `uv.lock` (local uv 0.12.13, matching CI's `astral-sh/setup-uv
version: "latest"`) completed with `Resolved 91 packages` and exit code 0 — a clean no-op — which is
a reassuring proxy but is explicitly **not** a substitute for the real-PR observation.
**Warning signs:** If the real `uv`-ecosystem PR's `uv.lock` bumps the `revision` field to something
higher than `3` in a way that trips `--locked` on CI, or if the Dependabot job log for that PR shows
a parse/version error, that is D-05's failure branch — record it and HALT for the owner rather than
attempting a workaround inside this phase.

### Pitfall 4: The "6 required checks" name specific `ci.yml` job names, not job categories

**What goes wrong:** Assuming any green CI run satisfies the merge gate, when in fact GitHub's
branch protection pins exact job-name strings.
**Why it happens:** `main`'s branch protection `required_status_checks.contexts` is an exact list:
`["Test Python 3.12 on ubuntu-latest", "Lint and Format Check", "Type Check", "Code Coverage",
"Build Package", "Test Python 3.13 on ubuntu-latest"]` `[VERIFIED: gh api repos/YuSabo90002/typsphinx/branches/main/protection]`.
Renaming a job, or a job failing to run at all (e.g. due to a `paths` filter this phase does not add
but a future one might), would silently leave the PR unmergeable with no clear error beyond "checks
not complete."
**How to avoid:** This phase does not touch `ci.yml` (ROADMAP constraint 3), so the job names are
unaffected. Confirmed no `paths`/`paths-ignore` filter exists anywhere in `ci.yml`'s `on:` block
(`push`/`pull_request`/`workflow_dispatch` only — verbatim: `on:\n  push:\n    branches: [ main,
develop ]\n  pull_request:\n    branches: [ main, develop ]\n  workflow_dispatch:`
`[VERIFIED: /home/yuta/Documents/typsphinx/.github/workflows/ci.yml:3-8]`), so a PR touching only
`.github/dependabot.yml` runs every job unconditionally, including all 6 required ones. `main` also
requires `strict: true` (branch must be up to date before merge) and has **no required reviews**
and `enforce_admins: false` — matching CONTEXT.md's summary exactly, re-verified live.
**Warning signs:** N/A for this phase specifically — flagged so future phases that DO touch CI
triggers know branch protection is exact-string-matched, not pattern-matched.

## Code Examples

### The exact diff (verified against the live file, re-fetched this session)

```diff
--- a/.github/dependabot.yml
+++ b/.github/dependabot.yml
@@ -1,7 +1,7 @@
 version: 2
 updates:
   # Python dependencies (pyproject.toml)
-  - package-ecosystem: "pip"
+  - package-ecosystem: "uv"
     directory: "/"
     schedule:
       interval: "weekly"
```
Every other line — `open-pull-requests-limit: 5`, both `labels`, the entire `groups.sphinx-typst-stack`
block, and the whole `github-actions` entry — is untouched.
`[VERIFIED: Read /home/yuta/Documents/typsphinx/.github/dependabot.yml, full file, this session]`

### D-01 verification command (byte-identical content across branches)

```bash
git diff origin/main origin/gsd/v0.9.3-toolchain-and-dependency-update-repair -- .github/dependabot.yml
# Measured this session: empty output — both branches currently carry the identical `pip` config,
# confirming the milestone branch has not drifted from `main` on this file.
```

### D-04 "same commit" verification command

```bash
gh pr view <uv-pr-number> --json commits,files
git show --name-only <head-sha>
# DEP-01/SC#1 is satisfied only if the head commit's file list contains BOTH
# pyproject.toml AND uv.lock.
```

### D-05 leg 2 verification command (run against the real PR's head, not locally)

```bash
gh pr checkout <uv-pr-number>
uv lock --check
# Local pre-check this session (main, uv 0.12.13, uv.lock revision=3):
#   Resolved 91 packages in 0.68ms  (exit 0) — a clean no-op, reassuring but not a substitute
#   for running this against the real PR's head with whatever uv CI's setup-uv installs there.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `dependabot.yml` `package-ecosystem: "pip"` for a `uv`-managed project | `package-ecosystem: "uv"` | GA per `dependabot-uv-support` feature flag (`fpt: '*'`, referencing GitHub issue #16918); `astral-sh/uv#2512` ("Add dependabot support") closed 2026-04-23 `[VERIFIED: gh issue view 2512 --repo astral-sh/uv]` | `pip`-ecosystem dependabot never understands `uv.lock` and only ever edits `pyproject.toml`, which is the root cause this whole milestone exists to fix (source todo `2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md`) |
| Custom lockfile-regeneration workflow (originally scoped for this milestone) | Native `uv` ecosystem | Owner-approved 2026-09-02, superseding the original milestone scope (PROJECT.md `AMENDED` block) | Removes an entire class of `pull_request_target`/force-push/stale-token failure modes described in Don't Hand-Roll above |
| `uv`'s `library?` detection duplicated a stale pre-#14709 copy of `pip`'s logic | `uv`'s `library?` inherits `pip`'s parent implementation directly | dependabot-core PR #15693, merged 2026-08-18 | Published-on-PyPI projects (typsphinx included) now get the same range-widening `versioning-strategy: auto` behavior under `uv` that they already got under `pip` |
| `uv` pinned at 0.11.x inside dependabot-core | `uv` pinned at 0.12.7 inside dependabot-core | PR #15770, merged 2026-08-12 (0.11.31 → 0.12.1; further patch bumps since) | GitHub's own documentation table (`dependabot-options-reference.md:618`, `supported-package-managers.md`) has not been updated to reflect this and still reads "v0.11" as of this session's re-fetch |

**Deprecated/outdated:**
- The `pip`-ecosystem entry for a `uv`-managed Python project — structurally cannot regenerate
  `uv.lock`, which is the entire defect this phase closes.
- The documentation figure "dependabot's uv version is v0.11" — accurate to what GitHub's docs
  currently publish, but demonstrably behind what dependabot-core's own source ships (0.12.7).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | GitHub's published `dependabot-options-reference.md:618` "v0.11" row reflects what actually runs in production on github.com (as opposed to dependabot-core's `main` branch pin of 0.12.7, which could itself lag or lead the deployed image by some margin) | Pitfall 3, Summary | If production is genuinely running something incompatible with `revision = 3` lockfiles, D-05 leg 2's real-PR observation is the only way to know — this assumption is exactly what leg 2 exists to falsify, and is flagged `[ASSUMED]` rather than `[VERIFIED]` precisely because no `gh api` call can read GitHub's internal deployment state |
| A2 | The `uv.lock` schema `version` field (currently `1`) has not been bumped between whatever uv version dependabot actually deploys and the uv version (0.12.13, locally measured) that will most likely write the real PR's lockfile | Pitfall 3 | If a schema-version bump occurred, older uv would reject the lockfile outright regardless of the `revision` field's backwards-compatibility guarantee — again, only the real-PR observation (D-05 leg 2) can confirm this holds |
| A3 | A push of the isolated `.github/dependabot.yml` PR to `main` will itself be treated by dependabot as a config update worth acting on promptly (vs. waiting for the Monday 00:00 schedule) | Pitfall 1, D-03 | `about-the-dependabot-yml-file.md:50`'s wording is genuinely ambiguous on this per CONTEXT.md's own framing; if wrong, D-03's manual "Check for updates" checkpoint is simply exercised sooner rather than being skippable — no plan correctness is at risk, only timing |

**None of these assumptions block planning** — each is already covered by a locked decision (D-03,
D-05) that treats the underlying question as "measure at execution time," not "assume now."

## Open Questions

1. **Does a bare push to `main` (no PR merge event, if the executor ever tests differently) trigger
   an immediate dependabot run, or only the next scheduled/manual one?**
   - What we know: `about-the-dependabot-yml-file.md:50` says dependabot "begins monitoring the
     specified package ecosystems according to your defined schedules" when the config changes —
     wording that could mean either "starts monitoring going forward, on schedule" or "starts a run
     right away." GitHub's docs make no further distinction.
   - What's unclear: The literal event semantics.
   - Recommendation: D-03 already treats this as something to observe and record, not resolve in
     advance — the plan should include a short poll window (Claude's Discretion: how long) before
     falling back to the "Check for updates" human checkpoint, and record which branch happened.

2. **Will the fresh `uv`-ecosystem PR arrive as a single grouped `sphinx-typst-stack` PR, individual
   PRs, or some mix, given that no currently-open bump exercises the group path under `pip` either
   (per the CONTEXT.md deferred-items note that #128 actually IS a grouped bump, contradicting
   Phase 67 SC#4/PROJECT.md's claim)?**
   - What we know: #128 (`docutils`) is in fact a `sphinx-typst-stack` grouped PR under `pip`
     today (title: "…in the sphinx-typst-stack group across 1 directory", branch:
     `dependabot/pip/sphinx-typst-stack-12b5b89b5a`), confirmed via `gh pr view 128`. `groups`'
     `patterns`/`exclude-patterns` matching is ecosystem-agnostic per the docs (no "supported by"
     restriction on those two sub-keys, unlike `dependency-type` which is `pip`-and-others-only,
     not `uv`-listed).
   - What's unclear: Whether the successor `uv`-ecosystem PR for `docutils` reproduces the same
     grouping behavior — this is exactly D-06's open measurement.
   - Recommendation: Record from the real PR, per D-06; do not assume from the config being
     syntactically unchanged.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `gh` CLI (authenticated) | All measurement in this research; D-02's PR snapshots; D-04's PR content reads | ✓ | Session-verified reaching `github/docs`, `dependabot/dependabot-core`, `astral-sh/uv`, repo PRs, branch protection | — |
| `git` | Byte-identity diff between `main` and milestone branch (D-01) | ✓ | System git, session-verified against `origin/main` and `origin/gsd/v0.9.3-…` | — |
| `uv` CLI (local) | D-05 leg 2's local sanity probe (`uv lock --check`) | ✓ | **0.12.13** (re-measured this session; supersedes the stale "0.11.25" figure in PROJECT.md's `AMENDED 2026-09-02` block and ROADMAP SC#2 text — see Summary) | Not a hard requirement; the authoritative D-05 leg-2 observation runs against the real PR's own CI, not this local probe |
| Public API for triggering/inspecting a dependabot version-update job | D-03's manual trigger, D-04's "config accepted" read | ✗ | — | UI-only path (Insights → Dependency graph → Dependabot tab); confirmed via `dependabot-core` issue #3080 ("no way of bumping dependencies via api"), still open. **No fallback exists** — this is why D-03 is a `checkpoint:human-action` and part of D-04's acceptance-reading is folded into that same checkpoint. |

**Missing dependencies with no fallback:**
- A public API for the dependabot job-trigger/status surface. This is fundamental to the domain, not
  a gap in this environment — GitHub does not offer one anywhere. The plan must route these
  observations through a `checkpoint:human-action`/`checkpoint:decision`, exactly as D-01 and D-03
  already specify.

**Missing dependencies with fallback:** None beyond the above.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (`pyproject.toml`), tox (`tox.ini`) — but **not applicable to this phase's actual change**: this phase edits a GitHub-platform YAML config file with no Python import surface, so no unit/integration test exercises it |
| Config file | N/A for this phase's edit — `.github/dependabot.yml` has no schema the project's own test suite validates |
| Quick run command | N/A — see "Sampling Rate" below; this phase's verification is observation-based, not test-suite-based |
| Full suite command | `uv run tox -e py312` / `py313` / `lint` / `type` / `cov` continue to run unmodified on the PR this phase opens (they are exactly the 6 required checks) — this phase does not add or change any of them |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DEP-01 | Dependabot opens a `uv`-ecosystem PR whose head commit touches both `pyproject.toml` and `uv.lock` | manual-only (external-service observation) | `gh pr view <n> --json commits,files` + `git show --name-only <sha>` | N/A — no test file; verified against a real, externally-generated artifact (the PR itself), consistent with D-04's explicit rejection of a "hand-made branch" shortcut |
| DEP-03 | Grouping / labels / PR-limit behave as before, or divergence recorded | manual-only (external-service observation) | `gh pr view <n> --json labels,title,headRefName` across all PRs opened after the merge; `gh pr list --search "author:app/dependabot"` for the open-count vs. limit-of-5 | N/A — same rationale; behavior is defined by GitHub's dependabot service, not by this project's code |
| DEP-04 | Dependabot's supported uv version vs. CI's vs. this repo's lock revision, recorded either way | manual-only (external-service + local probe) | `uv lock --check` (local sanity, not authoritative) on the real PR's checked-out head, per the Code Examples section | N/A — no automatable equivalent exists (D-05 leg 1's `dependabot-core` source read is a `gh api` call, not a pytest) |

**Justification for manual-only classification:** every requirement in this phase concerns the
behavior of an external SaaS (GitHub Dependabot) reacting to a config file, not this repository's
own code. There is no import path, function, or module this project owns that the requirements
exercise — the "test" is reading dependabot's own real-world output, exactly as D-04's decision text
states. Wave 0 gaps below are therefore evidence-recording artifacts, not test files.

### Sampling Rate

- **Per task commit:** N/A (no code, no test to run per commit on this file). The one useful sanity
  check per commit that touches the milestone-branch copy of `.github/dependabot.yml` is `git diff`
  against `main`'s copy, to keep D-01's byte-identity invariant visibly true throughout the phase.
- **Per wave merge:** Re-run the D-01 byte-identity `git diff` command; after the `main`-bound PR
  merges, the 6 required CI checks (already running unmodified) are the closest thing to a
  "full suite" gate this phase has, and they gate the merge itself via branch protection.
- **Phase gate:** All 6 required checks green on the `main`-bound PR before merge (enforced by
  GitHub branch protection itself — `strict: true`, no admin bypass); DEP-04's real-PR observation
  completed and recorded (pass or HALT) before the phase is considered done.

### Wave 0 Gaps

- [ ] An evidence file (naming at Claude's Discretion per CONTEXT.md) to record the D-02 pre/post
  snapshots of #123/#128, the D-04 "config accepted" observation, and the D-05 leg-2 uv-version
  observation — none of these have a home yet since this phase produces no code artifact.
- [ ] No pytest/tox file gap — confirmed above, this phase's requirements have no automated-test
  equivalent by construction.

*(No framework install is needed — pytest/tox are already fully configured for the rest of the
project and untouched by this phase.)*

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No authentication surface is touched — dependabot's own auth to GitHub/PyPI is entirely GitHub-managed and outside this repository's control |
| V3 Session Management | no | Not applicable — no session concept in this phase |
| V4 Access Control | no | `main`'s branch protection (required checks, `strict: true`) already gates the merge; this phase adds no new access-control surface |
| V5 Input Validation | no | The single YAML value changed (`"pip"` → `"uv"`) is a closed enum GitHub itself validates on config parse; there is no user-facing input path in this phase |
| V6 Cryptography | no | Not applicable |

**Overall assessment:** this phase has no ASVS-relevant attack surface of its own. The one
security-relevant fact worth recording explicitly, because it is the *reason* this phase exists in
its current (native-ecosystem) shape rather than the originally-scoped custom-workflow shape:

### Known Threat Patterns for this domain

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A `pull_request`-triggered custom workflow needing write access to push a regenerated lockfile back onto a dependabot (or any external-contributor) branch | Elevation of Privilege | GitHub forces `GITHUB_TOKEN` to read-only on `pull_request` runs regardless of the workflow's declared `permissions:` block; the only ways around this are `pull_request_target` (checks out untrusted branch content in a privileged context — the canonical GitHub Actions supply-chain footgun) or a long-lived PAT. **Standard mitigation here: avoid the pattern entirely** by using dependabot's own native `uv` ecosystem support, which needs no repository-scoped write token at all — this is precisely why the milestone's PROJECT.md `AMENDED 2026-09-02` block replaced the originally-scoped custom workflow. |
| Dependabot force-pushing over manually-added commits on its own PR branches | Tampering (of a benign, documented kind) | Dependabot honors a `[dependabot skip]` marker in a commit message to avoid overwriting manual changes on rebase; this is a dependabot-owned convention, not something this repository configures. Relevant only if a future phase (e.g. the fallback custom workflow, if D-05 leg 2 ever fails) pushes commits onto dependabot's branches — not relevant to this phase's plain config edit. |

## Sources

### Primary (HIGH confidence — fetched live this session via `gh api`/`gh pr view`/`gh issue view`/local tool invocation)

- `github/docs` `content/code-security/concepts/supply-chain-security/about-the-dependabot-yml-file.md` (lines 46, 50) — default-branch requirement; config-change ambiguity
- `github/docs` `content/code-security/reference/supply-chain-security/dependabot-options-reference.md` — `labels` (457-475), `groups`/`patterns`/`exclude-patterns` (314-386), `package-ecosystem` uv row (618), `versioning-strategy` (983-1020)
- `github/docs` `data/reusables/dependabot/supported-package-managers.md` — uv row, "v0.11"
- `github/docs` `content/code-security/how-tos/secure-your-supply-chain/manage-your-dependency-security/re-run-dependabot-jobs.md` (line 20) — "Check for updates"
- `github/docs` `content/code-security/how-tos/view-and-interpret-data/view-dependabot-logs.md` — job log access path
- `github/docs` `content/code-security/reference/supply-chain-security/troubleshoot-dependabot/dependabot-errors.md` — "How to view errors" (version vs. security update error surfaces)
- `github/docs` `data/features/dependabot-uv-support.yml`, `dependabot-uv-security-support.yml`, `dependabot-on-actions-opt-in.yml` — feature-flag GA status (all `fpt: '*'`)
- `dependabot/dependabot-core` `uv/Dockerfile:15`, `uv/helpers/requirements.txt:10` — `uv==0.12.7` pin, re-measured
- `dependabot/dependabot-core` PR #15770 (merged 2026-08-12) — uv bump 0.11.31→0.12.1
- `dependabot/dependabot-core` PR #15693 (merged 2026-08-18) — `uv` library-detection fix, full before/after table read
- `dependabot/dependabot-core` issue #3080 — confirms no public API for triggering/inspecting jobs
- `astral-sh/uv` `docs/guides/integration/dependabot.md` — canonical minimal `uv`-ecosystem config
- `astral-sh/uv` issue #2512 (closed 2026-04-23) — "Add dependabot support"
- `docs.astral.sh/uv/concepts/resolution` — "Lockfile versioning" section, `version` vs. `revision` field semantics
- This repository: `.github/dependabot.yml` (full file, read this session), `uv.lock` (header, read this session), `.github/workflows/ci.yml` (full file, read this session), `gh api repos/YuSabo90002/typsphinx/branches/main/protection`, `gh label list`, `gh pr view 123`/`128`, `gh pr list --state merged`, `git diff origin/main origin/gsd/v0.9.3-…`, local `uv --version` / `uv lock --check`

### Secondary (MEDIUM confidence)

- None — every claim above was either directly read from an authoritative source this session or
  directly measured against this repository's live state.

### Tertiary (LOW confidence)

- None retained. The one WebSearch-sourced lead (uv lockfile revision history via a general search)
  was superseded by the direct `docs.astral.sh` fetch and is not cited independently.

## Metadata

**Confidence breakdown:**
- Standard stack: N/A (no new stack) — HIGH by construction, nothing to be wrong about
- Architecture: HIGH — every diagram node is either a `gh api`-confirmed fact about this repo or a
  directly-quoted GitHub/Astral documentation statement
- Pitfalls: HIGH for the label gap and CI-trigger findings (directly measured against this repo);
  MEDIUM-leaning-HIGH for the v0.11/v0.12 compatibility question specifically, because D-05 leg 2
  (the only fully authoritative proof) requires a real dependabot PR that does not exist yet —
  this research closes leg 1 completely and provides strong circumstantial support (Astral's own
  revision-compatibility guarantee) but cannot substitute for the live observation the phase itself
  must perform

**Research date:** 2026-09-12
**Valid until:** Short shelf life for the specific version numbers (dependabot-core's uv pin, uv's
latest release, this repo's local uv version) — re-measure at execution time exactly as D-05
requires; the structural claims (default-branch requirement, label-ignore behavior, no public
trigger API, lockfile revision-vs-version semantics) are stable documentation/design facts unlikely
to change within 30 days.
