# Phase 31: Published-URL Cutover + Repo-Wide Link Guard - Research

**Researched:** 2026-07-26
**Domain:** GitHub Actions link-checking (lychee), URL rewrite verification (curl/RTD), GitHub repo metadata (About/Issues)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Link checker tooling (CI-05)**
- D-01: The tool is lychee (official `lychee-action` v2). Scans markdown/HTML/rst/plain text and can treat TOML as text — covering exactly the file class sphinx linkcheck structurally cannot see (`README.md`, `pyproject.toml`; SC#1's reason for existing). URL-pattern excludes via `.lycheeignore` (regex), path excludes supported. Confirmed actively maintained 2026-07-26.
- D-02: Triggers are PR and push only — no scheduled run. Owner decision. The 7 dead links that motivated this milestone were wrong at the moment they were written — a PR-time check catches that class. Accepted limitation: an external URL that dies with no commits in flight goes undetected until the next PR/push.
- D-03: Scan the whole repository; exclude by path, never by URL pattern. Excludes: `.planning/` (many historical dead URLs; includes INTEGRATIONS.md — see D-19), `CHANGELOG.md` (its historical github.io URL 404s after Phase 32 and would leave the job permanently red), plus tests/fixtures fake URLs if needed. Excluding the `github.io` URL pattern is forbidden — it would blind SC#1's negative control.
- D-04: Failure presentation is a red, non-required check. The dedicated workflow fails normally; it is never registered as a GitHub Required check (SC#3 / drift.yml precedent, D-07). No `continue-on-error` always-green masking — that contradicts CI-05's purpose.
- D-05: Location is a new standalone `.github/workflows/links.yml`. Same shape as the advisory precedent drift.yml. SC#3's "scope documented where it lives" (that THIS job, not sphinx linkcheck, covers `README.md` / `pyproject.toml`) goes in a comment block at the top of the file.
- D-06: Lenient false-positive posture. Retries enabled + accept 429 + a reasonable timeout. The target signal is a persistent 404, not a transient 429. Exact parameter values are Claude's discretion (tuned via branch push → CI observation, per D-08).
- D-07: HTTP(S) URLs only. Local/relative file-link existence checking is out of scope (owner choice).
- D-08: lychee is never run locally — CI only. Explicit owner instruction (does not want to run Rust binaries locally in this environment). All lychee execution, including parameter tuning, happens via pushing to the branch and observing GitHub Actions. SC#2's real-HTTP verification uses `curl` (fine locally).
- D-09: SC#1's negative control is recorded as "CI run + transcription." Commit links.yml before the rewrite, let CI go red on the tree where the old github.io links are still live, then transcribe the failing run's URL and the list of flagged URLs into VERIFICATION.md. Proving "CI can detect it" with CI itself is the most faithful reading of SC#1. Plan-ordering implication: the links.yml commit → observed red negative-control run → URL-rewrite commit sequence is structurally required.

**RTD URL shapes to burn in (DOC-09)**
- D-10: The 7 README deep links use `/en/latest/` across the board. `/en/stable/` does not exist until the v0.6.4 tag builds (RTD-06: no existing tag contains `.readthedocs.yaml`, no retroactive builds), so burning stable now fails SC#2's "alive over real HTTP, now." `latest` tracks `main`, keeping the links the same generation as the README that carries them. No rewrite needed in Phase 33 (`latest` never dies).
- D-11: Top-level links use the bare root `https://typsphinx.readthedocs.io/`. Applies to: README:12 and README:267 Documentation links, `pyproject.toml`'s `Documentation`, and About → Website. RTD's root redirects to the Default Version, so these follow Phase 33's `latest` → `stable` flip automatically with no re-editing.
- D-12: README:8's badge becomes RTD's official build-status badge (`https://app.readthedocs.org/projects/typsphinx/badge/?version=latest`). It flips passing → failing with the actual docs build — the badge itself becomes monitoring. The static shields.io badge is dropped.
- D-13: README gains a one-line link to the Japanese documentation (`https://typsphinx.readthedocs.io/ja/latest/`) — discoverability for Phase 30.1's deliverable. That URL joins SC#2's real-HTTP verification set. Exact placement and wording are Claude's discretion.
- The rewrite-target count is taken from a fresh grep at execution time (SC#2's explicit wording + milestone invariant #4). Measured 2026-07-26: 10 github.io occurrences in `README.md` (`:8`, `:12`, `:267`, `:271-277`), plus `pyproject.toml:56`'s `Documentation = "https://github.com/YuSabo90002/typsphinx#readme"` (not github.io, but it points at the old README — a rewrite target).

**Issue #119 close and About sequencing (DOC-10)**
- D-14: About → Website is set immediately during Phase 31 execution (owner-manual). Value is D-11's bare root. This link is exactly what put101 hit, so the reported symptom is resolved the moment it is set. Criterion 4's second half (the About URL resolves over real HTTP) is verified with `curl` within Phase 31.
- D-15: Issue #119 is closed after the milestone merge (at `/gsd-complete-milestone`). Owner decision — close only once the README rewrite is visible on `main` and everything promised has landed. The close half of ROADMAP SC#4 therefore moves outside Phase 31's verification window: Phase 31's verification confirms "About set + resolving + close-reply draft prepared," and the close itself is recorded as a handoff to milestone close. The verifier must treat this as an owner-decided handoff, not a gap.
- D-16: The close reply flow is draft → owner review → post. Same flow as the PR#98 precedent. English, terse, whole-thread-read (the owner's existing reply already promises "fix the Website link and the README deep links").
- D-17: Reply content is the fulfillment report only. The new (RTD) URL and the fact that About and README are fixed — kept short. No migration-background narrative, no old-URL-404 announcement.

**INTEGRATIONS.md rewrite depth**
- D-18: `.planning/codebase/INTEGRATIONS.md` gets a full refresh. Owner choice (beyond the ROADMAP-minimum option). Re-analyze the whole file and update its Analysis Date. Required updates (measured 2026-07-26): the Hosting section has zero RTD content / "CI only: SPHINX_LANGUAGE" must become Phase 29's `READTHEDOCS_LANGUAGE > SPHINX_LANGUAGE > "en"` seam / the docs.yml description predates Phase 30's changes / actions version drift (file says checkout@v6; drift.yml actually uses @v7) / the `typsphinx-doc-translations` repository + submodule + pin-bump workflow (Phase 30.1) are absent / links.yml (new in this phase) must be added. Partial re-staling by Phase 32's docs.yml reduction is accepted — Phase 32 updates its delta then.
- D-19: No carve-out of INTEGRATIONS.md from links.yml's `.planning/` exclusion. INTEGRATIONS.md's URLs are verified once by SC#2's execution-time `curl`, not by ongoing CI.

**Folded Todos**
- `.planning/todos/pending/2026-07-22-github-io-doc-links-404-missing-en-prefix.md` — the 7 README github.io deep links 404 (missing `/en/` prefix). Already promoted to Phase 31 (DOC-09) in STATE.md. Resolved by D-10's `/en/latest/` rewrite. Close this todo when the rewrite commit lands.

### Claude's Discretion
- Exact lychee parameter values (retry count, timeout, precise accepted-status set, caching) — within D-06's lenient posture.
- Exact exclusion mechanics (`--exclude-path` vs `.lycheeignore` split) and whether tests/fixtures fake URLs need excluding.
- Placement and wording of the one-line ja link in README (D-13).
- Verifying the 7 deep-link target paths exist on RTD and adjusting shapes if needed (e.g. `user_guide/` → `user_guide/index.html`) — SC#2's curl checks them regardless.
- Section structure of the INTEGRATIONS.md full refresh.
- The #119 close-reply draft wording (owner reviews before posting, D-16).

### Deferred Ideas (OUT OF SCOPE)
- Weekly scheduled run for external-link rot — D-02 chose PR/push only, so URL death with no commits in flight goes undetected between pushes. If operation shows the need, extending links.yml is a one-block `schedule:` addition.
- Repo-internal relative file-link checking — limited to HTTP(S) by D-07; a lychee builtin that can be enabled later.
- Putting `.planning/codebase/` under ongoing link watch — declined in D-19.
- `CHANGELOG.md`'s github.io 404 after Phase 32 — excluded from links.yml, so no red job; revisit only if the keep-as-history decision is ever reversed.
- The GitHub Pages teardown, version bump + CHANGELOG, and `sphinx-build -b linkcheck` are explicitly out of this phase's boundary (see Phase Boundary in 31-CONTEXT.md).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|--------------------|
| DOC-09 | Every documentation URL the project publishes — in the README, in the PyPI package metadata, and in the codebase notes — resolves to a real page, proven by an actual HTTP fetch. | RTD URL shapes verified via curl this session (all 7 deep-link suffixes + root + ja root all return 200); `links.yml` skeleton in Code Examples covers ongoing/CI detection; hermetic regression-guard test recommended in Validation Architecture |
| DOC-10 | The external bug report about the broken documentation link (Issue #119) is closed with the promised fix actually delivered, and a visitor to the GitHub repository can reach the documentation from the repository's own Website field. | Issue #119 body/reply fetched via `gh issue view` (Sources); current `homepage: null` confirmed via `gh api`; badge/root URL verified resolving — see Architectural Responsibility Map and Code Examples |
| CI-05 | A broken published link anywhere in the repository — including files Sphinx never scans — surfaces automatically in CI instead of after months. | `links.yml` architecture (Architecture Patterns Pattern 1), lychee-action inputs/flags (Standard Stack), Pitfalls 1–3 (path-vs-URL exclusion, `.toml` extension gap, repo-wide-scan collisions), branch-protection confirmation that new jobs are non-required by default |
</phase_requirements>

## Summary

This phase has two independent halves that share one constraint: **lychee must never run
locally** (D-08) — every syntax decision below has to be right the first push, verified only by
reading a GitHub Actions run. Research therefore leaned on lychee's official docs
(`lychee.cli.rs`) and the lychee-action's own `action.yml` (fetched directly from GitHub raw
content — this *is* the source of truth, not a description of it) rather than local
experimentation.

Half one is a **repo-wide grep + curl** cutover: replace 10 `github.io` URLs in `README.md` plus
`pyproject.toml`'s `Documentation` field with RTD `/en/latest/` URLs, all of which were verified
this session to return HTTP 200. Half two is a **new advisory CI workflow** (`links.yml`) modeled
directly on the existing `drift.yml` precedent, using `lycheeverse/lychee-action@v2`.

**Two findings change the plan's shape and must reach the planner:**

1. **lychee's default file-extension allow-list does not include `.toml`.** The action's default
   `args` value only globs `./**/*.md ./**/*.html ./**/*.rst`. Without an explicit
   `--extensions` addition (or listing `pyproject.toml` as an unambiguous input), the tool may
   silently skip the exact file SC#1's negative control names. This must be verified by reading
   the first (negative-control) CI run's file list, not assumed.
2. **A repo-wide scan (D-03) will also flag pre-existing, unrelated dead links** in
   `examples/basic/README.md`, `examples/basic/index.rst`, and `examples/advanced/README.md`
   (`https://github.com/your-repo/typsphinx...` placeholder text, confirmed 404 this session) and
   in `tests/fixtures/*/index.rst` (fake URLs like `example.com/a`, `github.com/user/repo`,
   confirmed 404/200-but-wrong this session). Left unaddressed, these make links.yml **red on the
   rewritten tree**, directly failing SC#3's "green on the rewritten tree" criterion. This is
   **not covered by any CONTEXT.md decision** — D-03 names only `.planning/` and `CHANGELOG.md`
   as path excludes, and Claude's Discretion only explicitly covers "tests/fixtures fake URLs *if
   needed*." Research confirms it IS needed, and additionally surfaces the `examples/` case,
   which CONTEXT.md never mentions. Flagged as an Open Question for the planner.

**Primary recommendation:** Build `links.yml` as a standalone workflow (D-05) using
`lycheeverse/lychee-action@v2` with a custom `args` string that (a) explicitly adds `toml` to
`--extensions`, (b) excludes `.planning/`, `CHANGELOG.md`, `tests/fixtures/`, and
`examples/**/README.md` + `examples/**/*.rst` via repeated `--exclude-path`, (c) sets a lenient
`--accept`/`--max-retries`/`--timeout` triple, and (d) never sets `--exclude` (URL-pattern
exclusion is forbidden by D-03). Sequence commits per D-09: `links.yml` first (observe red
negative control), then the URL rewrite (observe green).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Published URL correctness (README/pyproject) | Repo content (docs/metadata) | — | Static text files; no runtime component involved (milestone invariant #3 forbids touching `typsphinx/`) |
| Repo-wide dead-link detection | CI / GitHub Actions | — | `links.yml` runs in GitHub's hosted runner tier, advisory only, never a required check |
| RTD URL resolution | External hosted service (Read the Docs) | — | Already live per Phase 29/30.1; this phase only verifies + points at it, does not configure it |
| GitHub repo metadata (About → Website) | GitHub platform / repo settings | — | Owner-manual, unassertable from inside the repo (D-14) |
| Issue #119 close | GitHub Issues API | — | Deferred to milestone close (D-15); this phase only drafts the reply |

## Standard Stack

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|---------------|
| `lycheeverse/lychee-action` | `v2` (major tag; action itself pinned at repo HEAD `v2.9.0`, released 2026-07-09) | GitHub Action wrapper that installs and runs the lychee CLI | Official action for the lychee link checker; D-01 confirmed actively maintained (`pushed_at: 2026-07-09`, non-archived, 501 stars) `[VERIFIED: github.com/lycheeverse/lychee-action]` |
| lychee CLI (installed transitively by the action) | Action's `lycheeVersion` default resolves to a pinned release (`v0.24.2`, released 2026-05-01, confirmed via `gh api repos/lycheeverse/lychee/releases/latest`) | Async link checker (Rust binary) that scans Markdown/HTML/reST/plain text for broken hyperlinks | Purpose-built for exactly the file classes `sphinx-build -b linkcheck` cannot reach (README.md, pyproject.toml) `[VERIFIED: github.com/lycheeverse/lychee]` |

**No `npm install` / `pip install` for lychee.** `[CRITICAL — anti-slopsquat note]` A `package-legitimacy check --ecosystem npm lychee` run this session returned `OK` for a real npm package named `lychee` (`vdemedes/lychee`, published 2013, ~1,200 weekly downloads) — but that package is **unrelated** to `lycheeverse/lychee` (a name collision). The tool this phase needs is consumed *exclusively* as a GitHub Action (`uses: lycheeverse/lychee-action@v2`) and its transitively-installed Rust binary — never as an npm or pip dependency. The plan must not contain any install-from-registry step for "lychee."

### Supporting
| Item | Purpose | When to Use |
|------|---------|-------------|
| `--extensions md,html,rst,txt,toml` (or similar explicit list) | Widens lychee's default extension allow-list to include `.toml` | Required — `pyproject.toml` is in scope (D-01/SC#2) but `.toml` is absent from lychee's default extension list (`md,mkd,mdx,mdown,mdwn,mkdn,mkdown,markdown,html,htm,css,txt,xml`), confirmed via `lychee.cli.rs/guides/cli` `[VERIFIED: lychee.cli.rs/guides/cli]` |
| `--exclude-path <regex>` (repeatable) | Path-based exclusion | For `.planning/`, `CHANGELOG.md`, and (per the Open Question above) `tests/fixtures/` and `examples/` |
| `--accept <codes>` | Marks specific HTTP status codes as non-failing | D-06's lenient posture — accept `429` alongside the default `100..=103,200..=299` range so a rate limit doesn't manufacture a false red |
| `--max-retries` / `--retry-wait-time` | Retry tuning | D-06 — defaults are 3 retries / 1s wait; D-08 means the actual tuned values are set via branch-push observation, not asserted here |
| `--timeout` | Per-request timeout | D-06 — default is 20s; raise only if the negative-control run shows timeouts on slow endpoints |
| `token: ${{ github.token }}` (action input, default) | Passed by the action as `--github-token`/`GITHUB_TOKEN` internally | Avoids GitHub API rate limiting when checking the many `github.com/...` URLs already in README/CHANGELOG `[VERIFIED: lycheeverse/lychee-action action.yml]` |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `lycheeverse/lychee-action@v2` | Raw `lychee` binary download + manual `run:` step | Action wraps the binary-download/install boilerplate the action.yml itself performs; no reason to hand-roll it (already decided D-01) |
| `.lycheeignore` for path excludes | `--exclude-path` flag or `lychee.toml`'s `exclude_path` array | `.lycheeignore` excludes **URLs**, not paths — using it for path exclusion silently does nothing (see Pitfall 1) |

**Installation:** No `npm install` / `pip install` step. The workflow step is:
```yaml
- uses: lycheeverse/lychee-action@v2
  with:
    args: >-
      --verbose --no-progress
      --extensions md,html,rst,txt,toml
      --exclude-path '.planning'
      --exclude-path 'CHANGELOG.md'
      --exclude-path 'tests/fixtures'
      --accept '100..=103,200..=299,429'
      --max-retries 3
      --timeout 20
      .
    fail: true
    jobSummary: true
```
(Exact flag values beyond this skeleton — Claude's discretion per CONTEXT.md, tuned via branch push.)

**Version verification:** `lychee-action` — `gh api repos/lycheeverse/lychee-action/releases/latest` → `v2.9.0`, published `2026-07-09` `[VERIFIED: GitHub API]`. `lychee` CLI — `gh api repos/lycheeverse/lychee/releases/latest` → `lychee-v0.24.2`, published `2026-05-01` `[VERIFIED: GitHub API]`. Neither is an npm/PyPI/crates package for this project's purposes — it is consumed exclusively via the `uses:` action reference, so ecosystem-registry `npm view`/`pip index versions` checks are not applicable here (see Package Legitimacy Audit below for the GitHub-Actions-specific equivalent).

## Package Legitimacy Audit

> This phase adds a GitHub Action dependency, not an npm/PyPI/crates package. The standard
> `package-legitimacy check` seam targets package registries; it was still run below for the
> closest analogous npm name as an explicit anti-slopsquat control, and the GitHub Action itself
> was independently audited via the GitHub API (maintenance signals) and its own `action.yml`
> (fetched directly, not described secondhand).

| Dependency | Registry | Age / Last Push | Stars | Source Repo | Verdict | Disposition |
|------------|----------|-----------------|-------|--------------|---------|--------------|
| `lycheeverse/lychee-action@v2` | GitHub Actions (marketplace) | Last push 2026-07-09; latest release `v2.9.0` same date | 501 | `github.com/lycheeverse/lychee-action` (self) | OK | Approved — non-archived, actively maintained `[VERIFIED: GitHub API]` |
| `lycheeverse/lychee` (CLI, installed transitively) | GitHub Releases | Last push 2026-07-20; latest release `lychee-v0.24.2` (2026-05-01) | 3,785 | `github.com/lycheeverse/lychee` (self) | OK | Approved — non-archived, actively maintained `[VERIFIED: GitHub API]` |
| `lychee` (npm) | npm | Published 2013; ~1,200 weekly downloads | n/a | `github.com/vdemedes/lychee` | OK (as an npm package) but **UNRELATED** | **Do not use** — name collision, not the tool this phase needs. Flagged explicitly to prevent a slopsquat-adjacent mistake in planning/execution. |

**Packages removed due to `[SLOP]` verdict:** none.
**Packages flagged as suspicious `[SUS]`:** none — the npm `lychee` collision above is not suspicious in itself, it is simply the wrong package; no install step should reference it at all.

## Architecture Patterns

### System Architecture Diagram

```
                    ┌─────────────────────────────────────────┐
                    │         Push / Pull Request              │
                    │   (any branch, per D-02 — no schedule)    │
                    └───────────────────┬───────────────────────┘
                                        │ triggers
                                        ▼
                    ┌─────────────────────────────────────────┐
                    │   .github/workflows/links.yml (new)       │
                    │   permissions: contents: read             │
                    │                                            │
                    │  1. actions/checkout@v7                    │
                    │  2. lycheeverse/lychee-action@v2            │
                    │     scans: repo root, all extensions        │
                    │       md/html/rst/txt/toml                 │
                    │     excludes (path): .planning/,            │
                    │       CHANGELOG.md, tests/fixtures/,        │
                    │       examples/ (see Open Question)         │
                    │     excludes (URL): NONE — github.io must   │
                    │       stay visible (D-03 negative control)  │
                    └───────────────────┬───────────────────────┘
                                        │ real HTTP GET per URL found
                                        ▼
                    ┌─────────────────────────────────────────┐
                    │   External targets over real network:      │
                    │   - github.io (pre-rewrite: 404s expected)  │
                    │   - typsphinx.readthedocs.io/en/latest/*    │
                    │     (post-rewrite: 200s, verified this      │
                    │      session)                               │
                    │   - github.com/... (existing links)         │
                    │   - pypi.org, typst.app, sphinx-doc.org...  │
                    └───────────────────┬───────────────────────┘
                                        │ exit_code output
                                        ▼
                    ┌─────────────────────────────────────────┐
                    │  Job result: red (broken links found) or    │
                    │  green — surfaced in the PR checks list,    │
                    │  NEVER added to branch protection's         │
                    │  required_status_checks (D-04). Verified    │
                    │  this session: current required checks are  │
                    │  only ci.yml's 6 jobs — a new job name is   │
                    │  automatically non-blocking by omission.    │
                    └─────────────────────────────────────────┘
```

Separately, the URL-rewrite half of this phase is a **file edit + curl verification** loop, not a
pipeline:

```
README.md / pyproject.toml (github.io / #readme URLs)
        │  edit (D-10/D-11/D-12/D-13 shapes)
        ▼
README.md / pyproject.toml (typsphinx.readthedocs.io/en/latest/... URLs)
        │  curl -w "%{http_code}" -L <url>   (local, D-08 exempts curl)
        ▼
Recorded 200 responses in VERIFICATION.md (SC#2 evidence)
```

### Recommended Project Structure
```
.github/workflows/
├── drift.yml          # existing precedent — advisory, standalone, weekly
├── links.yml          # NEW — advisory, standalone, PR + push triggered
├── ci.yml             # existing — required checks live here, untouched
└── docs.yml           # existing — untouched by this phase (Phase 30/32 own it)
```

### Pattern 1: Advisory Standalone Workflow (drift.yml precedent)
**What:** A workflow file that is never named in branch protection's `required_status_checks`,
so a failure shows red in the PR checks UI but does not block merge.
**When to use:** Any CI signal that should surface but not gate — established for `drift.yml`
(v0.6.4 D-07 lineage) and now extended to `links.yml` (D-04/D-05).
**Example:**
```yaml
# Source: .github/workflows/drift.yml (this repository, structural reference)
name: Dependency Drift Check
on:
  schedule:
    - cron: '0 0 * * 1'
  workflow_dispatch:
permissions:
  contents: read
  issues: write
jobs:
  drift-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      # ... job logic ...
```
`links.yml` follows the same shape but with `on: [push, pull_request]` (D-02) and no `issues:
write` permission needed (this phase's CONTEXT does not call for auto-filed issues on failure —
`contents: read` alone suffices for a checkout + lychee scan).

### Pattern 2: Negative-Control-Then-Fix Commit Sequence (D-09)
**What:** Commit the detection mechanism *before* the bug it detects is fixed, observe it fail
in CI, transcribe the failing run's URL + flagged-link list into VERIFICATION.md, *then* commit
the fix and observe the same mechanism go green.
**When to use:** Whenever a success criterion requires proving a mechanism "would have caught"
a historical bug — proving detection with a live run of the actual mechanism is more faithful
than a written description of what it would have done.
**Structural implication:** this constrains plan/task ordering into (at minimum) two sequential
commits with an observation step between them — cannot be parallelized within a single task.

### Anti-Patterns to Avoid
- **`continue-on-error: true` on the lychee step:** Would make the job always report green
  regardless of lychee's exit code — directly contradicts D-04's "never always-green masking."
- **Adding `links.yml`'s job name to branch protection:** Turns an advisory check into a blocking
  one, violating D-04/SC#3. Verified this session: current `required_status_checks.contexts`
  lists only ci.yml's six job names — no action is needed to keep `links.yml` non-required, but
  no action should ever be taken to add it either.
- **Using `.lycheeignore` for path excludes:** It only strips URLs from the check list, not
  paths from the scan — see Pitfall 1.
- **Excluding the `github.io` URL pattern via `--exclude`:** Explicitly forbidden by D-03 — it
  would blind SC#1's negative control, the entire reason this mechanism is being built.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| Broken-link detection across arbitrary file types | A custom grep-and-curl script in CI | `lycheeverse/lychee-action@v2` | Handles retries, timeouts, status-code acceptance, GitHub-token-aware rate-limit avoidance, and per-format link extraction (Markdown/HTML/reST/plain-text) — reimplementing this well is exactly the "deceptively complex" trap; a hand-rolled version would need to reinvent link extraction per file format |
| Repo-wide grep for `github.io` occurrences | Trusting the CONTEXT.md-recorded count (10) | A fresh `grep -rn "github\.io"` at execution time | Milestone invariant #4 — the brief said 9, research (and this session) measured 10; a stale count is a documented failure class in this project (Phase 27's `examples/` miss) |

**Key insight:** every "don't hand-roll" item above traces back to the same lesson this
milestone keeps re-learning (documented in STATE.md's Accumulated Context): a green check or a
remembered count is not evidence — only a freshly-run, real-network or real-grep observation is.

## Common Pitfalls

### Pitfall 1: Putting path excludes in `.lycheeignore` instead of `--exclude-path`
**What goes wrong:** A `.lycheeignore` file listing `.planning/` or `CHANGELOG.md` silently does
nothing — the excluded paths still get scanned, and the job stays red on `.planning/`'s many
known-historical-dead URLs.
**Why it happens:** The name `.lycheeignore` strongly suggests "files to ignore," but lychee's
own docs are explicit: *"you might think that you can just put the path in the `.lycheeignore`
file, but that won't work. The `.lycheeignore` file is used for excluding URLs, not paths."*
**How to avoid:** Use `--exclude-path <regex>` (repeatable) in the `args` input, or the
`exclude_path` array in a `lychee.toml` config file. Reserve `.lycheeignore`/`--exclude` for URL
patterns only — and per D-03, this phase must never populate that list with `github.io`.
**Warning signs:** The first (negative-control) CI run still flags URLs under `.planning/` or
`CHANGELOG.md:393` even though a `.lycheeignore` file was added.
`[VERIFIED: lychee.cli.rs/recipes/excluding-paths]`

### Pitfall 2: `pyproject.toml` silently skipped because `.toml` isn't a default extension
**What goes wrong:** lychee's default `--extensions` list is
`md,mkd,mdx,mdown,mdwn,mkdn,mkdown,markdown,html,htm,css,txt,xml` — no `toml`. If `links.yml`'s
`args` doesn't add it, the negative-control run may report success (nothing flagged) on
`pyproject.toml` for the wrong reason — not because the link resolves, but because the file was
never scanned. This would produce a **false-negative negative control**, the opposite of SC#1's
intent.
**Why it happens:** the lychee-action's own default `args` value only globs `.md`/`.html`/`.rst`
files; `pyproject.toml` was never in that path even before extension filtering is considered.
**How to avoid:** add `toml` to an explicit `--extensions` list AND/OR list `pyproject.toml` as
an explicit input path in `args` (not just a directory glob) so it is unambiguously included
regardless of how the extension filter applies to directly-named files (this nuance is
undocumented upstream — the safest posture given D-08's "no local testing" constraint is to do
both).
**Warning signs:** Read the negative-control CI run's `--verbose` output / job summary and
confirm `pyproject.toml` appears in the list of files actually scanned before trusting a "0
broken links" result on it.
`[VERIFIED: lychee.cli.rs/guides/cli — default extensions list]` `[ASSUMED: whether an
explicitly-named file argument bypasses the --extensions filter — undocumented upstream, treat
defensively]`

### Pitfall 3: A repo-wide scan surfaces unrelated pre-existing dead links that block SC#3
**What goes wrong:** `examples/basic/README.md`, `examples/basic/index.rst`, and
`examples/advanced/README.md` contain placeholder URLs
(`https://github.com/your-repo/typsphinx...`) that return HTTP 404 (confirmed this session).
`tests/fixtures/*/index.rst` contain intentionally-fake URLs (`example.com/a`,
`github.com/user/repo`, etc. — some 404, some resolve but to the wrong/unrelated page). None of
these are `github.io` URLs, so rewriting README.md's real links does not fix them — `links.yml`
would still show red on the rewritten tree, failing SC#3.
**Why it happens:** D-03's exclusion list only names `.planning/` and `CHANGELOG.md`; it does
not anticipate `examples/` or `tests/fixtures/`, and this project's example READMEs use
`your-repo` as an intentional fill-in-the-blank placeholder for forkers, not a real dead link
from this milestone.
**How to avoid:** See Open Questions below — the planner must decide (and CONTEXT.md does not
yet decide) whether to path-exclude `examples/**` and `tests/fixtures/**`, or leave `examples/`
in scope and treat its placeholder URLs as a separate, small fix.
**Warning signs:** The rewritten-tree CI run (SC#3's "green on the rewritten tree") is still red,
and the flagged URLs are `your-repo` or `example.com`/`github.com/user/repo`, not `github.io`.

### Pitfall 4: RTD deep-link suffix must exactly match what README currently uses
**What goes wrong:** Guessing at a suffix (e.g. `quick_start.html` instead of the actual
`quickstart.html`) produces a 404 on the *new* URL, trading one broken link for another.
**Why it happens:** README.md's existing suffixes were written against the old GitHub Pages
Sphinx build's URL structure; assuming a "clean" name instead of reading the actual current
suffix is an easy mistake.
**How to avoid:** This session curl-verified all 7 current README suffixes resolve on RTD when
prefixed with `/en/latest/`: `installation.html`, `quickstart.html`, `user_guide/`,
`user_guide/configuration.html`, `examples/`, `api/`, `contributing.html` — all returned `200`.
`quick_start.html` (an alternate guess with underscore) returns `404` — do not use it.
**Warning signs:** A curl check against the new URL returns anything other than `200`.
`[VERIFIED: curl, this session, 2026-07-26]`

## Code Examples

### `links.yml` skeleton (verified inputs/flags; exact tuning values are Claude's discretion)
```yaml
# Source: lycheeverse/lychee-action action.yml (github.com/lycheeverse/lychee-action, fetched
# directly this session) + lychee.cli.rs/guides/cli (flag semantics) + .github/workflows/drift.yml
# (this repo's advisory-workflow structural precedent)
#
# SCOPE NOTE (SC#3 requirement): this job, not `sphinx-build -b linkcheck`, is what covers
# README.md and pyproject.toml — Sphinx's linkcheck builder never scans files outside its
# `docs/source/` tree (see Future LNK-01 in REQUIREMENTS.md).
name: Link Check

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  link-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - name: Check links
        uses: lycheeverse/lychee-action@v2
        with:
          args: >-
            --verbose --no-progress
            --extensions md,html,rst,txt,toml
            --exclude-path '.planning'
            --exclude-path 'CHANGELOG.md'
            --exclude-path 'tests/fixtures'
            --accept '100..=103,200..=299,429'
            .
          fail: true
          jobSummary: true
```

### RTD deep-link verification (curl, run locally per D-08's carve-out)
```bash
# Source: this session's direct measurement against the live RTD project
curl -s -o /dev/null -w "%{http_code}\n" -L https://typsphinx.readthedocs.io/en/latest/installation.html   # 200
curl -s -o /dev/null -w "%{http_code}\n" -L https://typsphinx.readthedocs.io/en/latest/quickstart.html      # 200
curl -s -o /dev/null -w "%{http_code}\n" -L https://typsphinx.readthedocs.io/en/latest/user_guide/          # 200
curl -s -o /dev/null -w "%{http_code}\n" -L https://typsphinx.readthedocs.io/en/latest/user_guide/configuration.html  # 200
curl -s -o /dev/null -w "%{http_code}\n" -L https://typsphinx.readthedocs.io/en/latest/examples/            # 200
curl -s -o /dev/null -w "%{http_code}\n" -L https://typsphinx.readthedocs.io/en/latest/api/                 # 200
curl -s -o /dev/null -w "%{http_code}\n" -L https://typsphinx.readthedocs.io/en/latest/contributing.html    # 200
curl -s -o /dev/null -w "%{http_code}\n" -L https://typsphinx.readthedocs.io/ja/latest/                     # 200
curl -s -o /dev/null -w "%{http_code}\n" -L https://typsphinx.readthedocs.io/                                # 200 (redirects to /en/latest/)
curl -s -o /dev/null -w "%{http_code}\n" -L "https://app.readthedocs.org/projects/typsphinx/badge/?version=latest"  # 200
```

### Hermetic regression guard (recommended, following this repo's existing pattern)
```python
# Source: pattern mirrors tests/test_readme_version_sync.py (this repo) — parse raw text,
# assert absence, no network call, runs on every `pytest` invocation.
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

def test_readme_has_no_github_io_links():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "github.io" not in text, (
        "README.md still references a github.io URL -- Phase 31 rewrote these to "
        "typsphinx.readthedocs.io; a github.io link here is a regression."
    )

def test_pyproject_documentation_url_is_not_readme_anchor():
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "typsphinx#readme" not in text
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Documentation hosted on GitHub Pages (`yusabo90002.github.io/typsphinx`) | Read the Docs (`typsphinx.readthedocs.io`) | Phases 29–30.1 of this milestone | Every published URL must be rewritten to the new host; Pages itself is torn down in Phase 32, ordered after this phase deliberately |
| Static shields.io "docs-latest-blue" badge (never reflects actual build health) | RTD's official build-status badge (`app.readthedocs.org/projects/typsphinx/badge/?version=latest`) | This phase (D-12) | Badge becomes a live signal: it goes red if the RTD build breaks, instead of always showing blue |
| `SPHINX_LANGUAGE` set directly in CI workflow env | `READTHEDOCS_LANGUAGE > SPHINX_LANGUAGE > "en"` precedence resolved inside `conf.py`'s `_resolve_language()` | Phase 29 | `.planning/codebase/INTEGRATIONS.md`'s "CI only: SPHINX_LANGUAGE" line is now stale — confirmed this session: no current workflow file sets `SPHINX_LANGUAGE` at all |

**Deprecated/outdated:** `.planning/codebase/INTEGRATIONS.md`'s entire "Hosting" and "Environment
Configuration" sections predate this milestone (Analysis Date 2026-07-22, before Phase 29
started) — confirmed stale this session on three specific points: (1) zero RTD content anywhere
in the file, (2) `actions/checkout@v6` claimed for `drift.yml` while **every** workflow file in
this repo (`ci.yml`, `docs.yml`, `drift.yml`, `release.yml`) now uses `actions/checkout@v7`, (3)
no mention of the `typsphinx-doc-translations` repository/submodule that Phase 30.1 introduced.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | An explicitly-named file argument to lychee (e.g. `pyproject.toml` passed directly, not via a directory glob) bypasses the `--extensions` allow-list filter | Pitfall 2, Code Examples | If wrong, `pyproject.toml` could still be silently skipped even when passed as an explicit argument alongside `--extensions toml`; mitigated by reading the negative-control run's verbose output before trusting any "0 broken links" result on it — this is exactly what D-09's CI-run-transcription step is for |
| A2 | The RTD badge's click-through target should be the bare root (`https://typsphinx.readthedocs.io/`) rather than a version-suffixed URL | Code Examples (badge) | Low risk — cosmetic; the image URL (the actual monitoring signal) is independently verified at `200`, and CONTEXT.md leaves exact badge wording/placement to Claude's discretion anyway |
| A3 | `contents: read` alone is sufficient permission for `links.yml` (no `issues: write` needed, unlike `drift.yml`) | Architecture Patterns, Code Examples | Low risk — CONTEXT.md's decisions (D-01 through D-19) never call for auto-filing an issue on link-check failure; if execution later wants that behavior, the permission can be widened then |

## Open Questions

1. **Should `examples/**` and `tests/fixtures/**` be path-excluded from `links.yml`, alongside
   `.planning/` and `CHANGELOG.md`?**
   - What we know: both directories contain confirmed-404 or intentionally-fake URLs that are
     unrelated to this milestone's `github.io` rewrite (see Pitfall 3). Repo-wide scanning (D-03)
     will surface them regardless of the URL rewrite's success.
   - What's unclear: CONTEXT.md's Claude's-Discretion list only anticipated `tests/fixtures`
     ("if needed" — now confirmed needed) and never mentions `examples/` at all. Excluding
     `examples/` by path is a broader move than anything CONTEXT.md discussed, and touches files
     that are part of the project's dogfooded sample content (not test fixtures).
   - Recommendation: exclude both via `--exclude-path` (matching the `tests/fixtures` precedent
     CONTEXT.md already sanctioned in spirit), and record this exclusion plus its rationale
     explicitly in the plan and in `links.yml`'s own scope-documentation comment block (SC#3
     requires the file to document its own scope). This keeps SC#3's "green on the rewritten
     tree" achievable without fixing unrelated placeholder content that isn't part of this
     phase's boundary. If the owner would rather fix the `examples/` placeholder URLs directly
     (they are template fill-ins for forkers, so "fixing" them to a real repo URL may not even be
     correct), that is a decision for `/gsd-discuss-phase` follow-up, not something this research
     can resolve.

2. **Does lychee's `--extensions` filter apply to explicitly-named file inputs, or only to
   directory-glob traversal?**
   - What we know: the official docs describe `--extensions` as filtering "files not matching
     the specified extensions," without carving out an exception for explicitly-named files.
   - What's unclear: whether passing `pyproject.toml` directly (not via a glob) still gets
     filtered by `--extensions` if `toml` isn't in the list.
   - Recommendation: defensively add `toml` to `--extensions` regardless (cheap, no downside),
     and use the D-09 negative-control CI run as the actual verification instrument — read its
     verbose/job-summary output for `pyproject.toml`'s presence before treating any result on it
     as trustworthy.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|--------------|-----------|---------|----------|
| GitHub Actions (hosted runner) | `links.yml` | ✓ (existing CI already runs there) | ubuntu-latest | — |
| `lycheeverse/lychee-action@v2` | `links.yml` | ✓ (verified via GitHub API, non-archived, actively maintained) | v2.9.0 | — |
| `curl` | Local RTD URL verification (D-08's carve-out) | ✓ (used throughout this research session) | system curl | — |
| `gh` CLI | Issue #119 inspection, branch-protection inspection, package-legitimacy-adjacent checks | ✓ (used throughout this research session) | system gh, authenticated | — |
| Local `lychee` binary | N/A — explicitly forbidden | N/A (not installed, not needed) | — | D-08: all lychee execution happens via CI push/observe, never locally |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none — `lychee` is intentionally never installed locally per D-08; this is a decision, not a gap.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (existing, `pyproject.toml` `[tool.pytest.ini_options]`) |
| Config file | `pyproject.toml` (existing) |
| Quick run command | `uv run pytest tests/test_readme_version_sync.py tests/test_readthedocs_config.py -x` (pattern precedent for a new link-guard test module) |
| Full suite command | `uv run pytest` (or `uv run tox -e cov`) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|--------------|
| DOC-09 | Every documentation URL (README/pyproject/INTEGRATIONS.md) resolves over real HTTP | manual/CI (real network) | `curl -s -o /dev/null -w "%{http_code}" -L <url>` per URL (see Code Examples) | ❌ Wave 0 — no automated fetch-based test exists yet; this is inherently a real-network check, not a hermetic unit test |
| DOC-09 (regression guard) | README.md / pyproject.toml never regress back to a `github.io` string | unit (hermetic) | `uv run pytest tests/test_no_stale_github_io_links.py -x` | ❌ Wave 0 — recommended new file, mirrors `test_readme_version_sync.py` pattern |
| DOC-10 | About → Website field resolves; Issue #119 reply drafted | manual (owner-executed) + curl | `curl -s -o /dev/null -w "%{http_code}" -L https://typsphinx.readthedocs.io/` | N/A — About field is GitHub repo settings, no test file possible (owner-manual, D-14) |
| CI-05 | `links.yml` exists, is advisory, flags known-bad links pre-rewrite, is green post-rewrite | CI observation (not pytest) | Push branch, read Actions run output (D-08's mandated verification path) | ❌ Wave 0 — `links.yml` itself does not exist yet |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_no_stale_github_io_links.py -x` (once written) — fast, hermetic, catches regressions without needing network access.
- **Per wave merge:** `uv run pytest` (full suite) + push to observe `links.yml`'s CI result (this cannot be run locally per D-08).
- **Phase gate:** Full pytest suite green, PLUS the two required `links.yml` CI observations (red negative control, then green post-rewrite) transcribed into VERIFICATION.md per D-09.

### Wave 0 Gaps
- [ ] `.github/workflows/links.yml` — does not exist yet; this phase's primary CI deliverable.
- [ ] `tests/test_no_stale_github_io_links.py` (or similarly named) — recommended hermetic regression guard; not required by any CONTEXT.md decision but strongly aligned with this repo's existing `test_readme_version_sync.py` / `test_preview_version_sync.py` pattern of guarding against exactly this kind of silent drift.
- [ ] No pytest-based test can assert DOC-09's core claim (URLs resolve over real HTTP) — that is inherently outside a hermetic unit-test framework; CI-05's `links.yml` plus manual curl transcription is the correct instrument, not a gap to fill with pytest.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|----------------|---------|-------------------|
| V2 Authentication | no | No auth surface touched by this phase |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | no | No user-facing input parsing added |
| V6 Cryptography | no | N/A |
| N/A (CI/CD supply-chain, not a formal ASVS category but relevant here) | yes | Pin the new action reference to a major version tag (`@v2`) matching the existing repo convention (`actions/checkout@v7` etc.); grant `links.yml` only `permissions: contents: read` (least privilege — no `issues:`/`pull-requests:` write needed since CONTEXT.md's decisions do not call for auto-filed issues on failure) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|-----------------------|
| A CI workflow granted broader `permissions:` than it needs (e.g. copying `drift.yml`'s `issues: write` verbatim without needing it) | Elevation of Privilege | Set `permissions: contents: read` only, matching the actual capability `links.yml` needs (checkout + read-only link scan) |
| Token leakage via an overly broad `token:` input to a third-party action | Information Disclosure | Use the action's default `token: ${{ github.token }}` (already scoped to the workflow's own `permissions:` block) — no `secrets.CUSTOM_TOKEN` or PAT needed for this use case |
| Supply-chain risk from an unpinned or floating action tag | Tampering | `@v2` is a maintained major-version tag on an actively-updated, non-archived action (verified this session); this matches the existing repo convention of pinning to major version tags (`@v7`, `@v6`, `@v5`) rather than full SHAs — no deviation from established project practice |

## Sources

### Primary (HIGH confidence)
- `https://raw.githubusercontent.com/lycheeverse/lychee-action/master/action.yml` — fetched directly, full inputs/outputs table (args, fail, failIfEmpty, format, jobSummary, lycheeVersion, output, checkbox, token, workingDirectory; output: exit_code)
- `https://lychee.cli.rs/guides/cli` — fetched directly, `--exclude-path`, `--exclude`, `--accept`, `--extensions` (default list confirmed), `--max-retries`, `--retry-wait-time`, `--timeout`, `--github-token` semantics
- `https://lychee.cli.rs/recipes/excluding-paths` — fetched directly, confirms `.lycheeignore`/`--exclude` are URL-exclusion mechanisms, not path-exclusion (Pitfall 1)
- `gh api repos/lycheeverse/lychee-action` / `repos/lycheeverse/lychee` / `.../releases/latest` — maintenance signals (non-archived, push dates, star counts, latest release tags)
- `gh api repos/YuSabo90002/typsphinx/branches/main/protection` — confirmed current required status checks (only ci.yml's 6 jobs)
- `gh api repos/YuSabo90002/typsphinx` — confirmed `homepage: null` (About → Website currently unset)
- `gh issue view 119` — full issue body + owner's existing reply, confirmed OPEN
- Direct `curl` measurements this session against all RTD URL targets (root, `/en/latest/`, `/ja/latest/`, all 7 README deep-link suffixes, RTD badge URL) — all 200
- Direct repo `grep` measurements this session (github.io occurrence count = 10 in README.md matching D-10's measured figure; zero elsewhere except CHANGELOG.md:393; `examples/` and `tests/fixtures/` fake-URL discovery)

### Secondary (MEDIUM confidence)
- `mcp__tavily__tavily_search` results cross-referencing lychee-action usage examples (community marketplace listing, GitHub discussions) — used to corroborate, not as sole source, for every claim above
- `https://docs.readthedocs.com/platform/latest/badges.html` (via WebSearch summary + WebFetch) — general badge URL pattern confirmed; exact link-wrapping convention not confirmed verbatim (see Assumption A2)

### Tertiary (LOW confidence)
- None retained as authoritative — all load-bearing claims above were corroborated by a primary-source fetch or a direct measurement (`curl`/`gh api`/`grep`) this session.

## Metadata

**Confidence breakdown:**
- Standard stack (lychee-action/lychee CLI): HIGH — fetched `action.yml` and `lychee.cli.rs` directly, cross-checked with `gh api` maintenance signals
- Architecture (advisory workflow shape): HIGH — directly modeled on this repo's own `drift.yml`, verified against live branch-protection API response
- URL rewrite targets (RTD deep links, badge, root): HIGH — every target curl-verified this session, not assumed from CONTEXT.md's prior measurement
- Pitfalls (extension filtering nuance for explicitly-named files): MEDIUM — the specific edge case (does `--extensions` filter explicitly-named args) is undocumented upstream; treated defensively (Assumption A1) rather than asserted
- Repo-wide scope collision (`examples/`, `tests/fixtures/`): HIGH — directly measured via curl/grep this session, not present in any prior document

**Research date:** 2026-07-26
**Valid until:** 7 days (fast-moving: depends on live RTD build status and a third-party GitHub Action's current release; re-verify URLs and action version immediately before executing if more than a few days elapse)
