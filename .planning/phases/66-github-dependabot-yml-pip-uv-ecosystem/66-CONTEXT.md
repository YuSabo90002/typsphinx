# Phase 66: `.github/dependabot.yml` — `pip` → `uv` Ecosystem - Context

**Gathered:** 2026-09-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Switch the Python `updates` entry of `.github/dependabot.yml` from `package-ecosystem: "pip"` to
`"uv"`, carrying the `sphinx-typst-stack` group, the `dependencies` / `automated` labels, the
schedule and `open-pull-requests-limit: 5` across unchanged, and leaving the `github-actions` entry
untouched (DEP-01). Get that configuration onto `main` — the only branch dependabot reads — and
observe from a real `uv`-ecosystem dependabot PR that `pyproject.toml` and `uv.lock` change in the
same commit (SC#1). Measure dependabot's uv against CI's uv and this repo's lock (DEP-04), and
confirm or record divergence in grouping / labels / PR limit (DEP-03).

**State at discussion time (measured 2026-09-12):**
- `origin/main` and the milestone branch both carry the `pip` entry (last touched `0bf6b5a5`).
- Default branch is `main`; it is protected with 6 required status checks, `strict: true`,
  `enforce_admins: false`, no required reviews. `main`'s last three CI runs are `success`
  (latest `33321027353` on `6181768f`).
- Open dependabot PRs: #123 (`ruff`, `dependabot/pip/ruff-gte-0.15-and-lt-0.17`) and #128
  (`docutils`, **grouped** — `dependabot/pip/sphinx-typst-stack-12b5b89b5a`, title "…in the
  sphinx-typst-stack group across 1 directory"). Both touch `pyproject.toml` only.
- `uv.lock` header: `version = 1`, `revision = 3`. Latest uv release: 0.12.13 (2026-09-10).

Not in this phase: DEP-02 (CI observed passing on a real dependabot PR) and DEP-05 (disposal of
#123/#128 on their merits) — Phase 67. Any workflow edit (constraint 3). Documentation (Phase 68).
Anything under `typsphinx/` (constraint 13).

</domain>

<decisions>
## Implementation Decisions

### Getting the configuration onto `main`

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

### #123 / #128 exposure when the `pip` entry leaves `main`

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

### SC#1 — the real-PR observation

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

### DEP-04 — the uv version question

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

### DEP-03 — grouping, labels, PR limit

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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and binding constraints
- `.planning/ROADMAP.md` § "Phase 66" — goal and SC#1–SC#3.
- `.planning/ROADMAP.md` § binding constraints 2 (incl. its `AMENDED 2026-09-12` block), 3, 4, 13.
- `.planning/ROADMAP.md` § "Phase 67" — SC#2 (reads D-02's snapshots) and SC#4.
- `.planning/REQUIREMENTS.md` — DEP-01, DEP-03, DEP-04 (and DEP-02/DEP-05 for boundary).
- `.planning/PROJECT.md` — `AMENDED 2026-09-02` block (why the custom workflow was replaced).
- `.planning/todos/pending/2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md` — origin
  of the defect, measured failure shape.
- `.planning/phases/65-tox-uv-bare-tox-uv-revert-on-the-uv-path-tox-actually-resolves/65-CONTEXT.md` D-04
  — `uv lock --check` with uv 0.12.13 on this lock was a byte-identical no-op.

### Files touched / read
- `.github/dependabot.yml` — the only tree file this phase edits.
- `.github/workflows/ci.yml` — the `uv sync --locked` steps and `setup-uv` `version: "latest"`
  (read only; constraint 3).
- `uv.lock` header — `version = 1`, `revision = 3`.

### External (fetched via GitHub API 2026-09-12)
- `github/docs` `content/code-security/concepts/supply-chain-security/about-the-dependabot-yml-file.md:46,50`
  — default-branch requirement; config-change behaviour.
- `github/docs` `content/code-security/reference/supply-chain-security/dependabot-options-reference.md`
  — `versioning-strategy` (:983-1003), uv version row (:618), extra ecosystem label (:464).
- `github/docs` `data/reusables/dependabot/supported-package-managers.md` — `uv` row, `v0.11`.
- `github/docs` `content/code-security/how-tos/secure-your-supply-chain/manage-your-dependency-security/re-run-dependabot-jobs.md:20`
  — "Check for updates".
- `dependabot/dependabot-core` `uv/Dockerfile:15`, `uv/helpers/requirements.txt`, PR #15770,
  PR #15693.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `gh` CLI is authenticated in this environment and reaches `github/docs`, `dependabot-core`, PR
  state and branch protection — every external fact above was fetched this way.

### Established Patterns
- Evidence recorded verbatim in the phase's evidence markdown; no new script, no new test (Phase 64
  D-05 / Phase 65 D-03 convention).
- Versions and states recorded literally at execution time, not copied from this CONTEXT.
- Outward-facing text (PR title/body) in English and terse.

### Integration Points
- `ci.yml`'s `pull_request` trigger is scoped to `main`, so dependabot PRs (which target `main`)
  run CI — relevant to Phase 67, not a Phase 66 gate.
- `main` requires 6 checks with `strict: true`: the `main`-bound PR must be up to date with `main`.

</code_context>

<specifics>
## Specific Ideas

- The phase's premise was corrected before planning: the owner chose to land the config on `main`
  early (D-01) over deferring the real-PR proof past REL-12, and chose the outright replacement
  (D-02) over a transitional `pip` + `uv` dual entry, which would have contradicted SC#1's wording
  and kept producing `pip` PRs that always fail `--locked`.

</specifics>

<deferred>
## Deferred Ideas

- **Phase 67 SC#4 and PROJECT.md state "neither #123 nor #128 is a grouped bump" — false.** #128
  is a `sphinx-typst-stack` group PR (title and branch). Raise at Phase 67 discuss; not amended here.
- Setting `versioning-strategy` (e.g. `increase-if-necessary`) if lockfile-only PR volume under
  `uv` turns out to crowd the limit of 5 — only after D-06's observation, and as its own decision.

### Reviewed Todos (not folded)
- `2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md` — the source of this phase; its
  `resolves_phase: 67` stands (closure needs DEP-02).
- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`,
  `2026-08-16-root-toctree-duplicates-section-children-in-html-sidebar.md`,
  `2026-07-22-add-sphinx-linkcheck-ci-job.md`,
  `2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`,
  `2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md` —
  keyword-score matches only; unrelated to dependabot configuration.

</deferred>

---

*Phase: 66-github-dependabot-yml-pip-uv-ecosystem*
*Context gathered: 2026-09-12*
