# Phase 31: Published-URL Cutover + Repo-Wide Link Guard - Context

**Gathered:** 2026-07-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Every documentation URL typsphinx publishes — in `README.md`, in the PyPI package metadata, and
in the codebase notes — points at Read the Docs and resolves over real HTTP, and a mechanism now
exists (an advisory CI link check) that would catch the next dead link instead of letting it
survive for months. **Requirements: DOC-09, DOC-10, CI-05.**

**Explicitly NOT this phase:** the GitHub Pages teardown — disabling Pages, deleting `gh-pages`,
removing the `docs.yml` deploy step (Phase 32 / CI-04); version bump + CHANGELOG (Phase 33);
`sphinx-build -b linkcheck` (Future LNK-01 — structurally blind to `README.md` /
`pyproject.toml` where the dead links actually live; decided out of scope 2026-07-25).
`CHANGELOG.md:393`'s github.io mention stays **untouched** (historical record, Phase 24 D-02
precedent). No `typsphinx/` runtime code change (milestone invariant #3).

**Timing structure (planning must assume this):** with `branching_strategy: milestone`, this
phase's rewrites do not reach `main` until the milestone merges. However, About → Website is a
repository-level setting and takes effect for every visitor the moment it is set. SC#2's
real-HTTP verification runs against the branch's file contents plus the already-live RTD URLs,
so it does not need to wait for the merge.

</domain>

<decisions>
## Implementation Decisions

### Link checker tooling (CI-05)

- **D-01: The tool is lychee (official `lychee-action` v2).** Scans markdown/HTML/rst/plain
  text and can treat TOML as text — covering exactly the file class sphinx linkcheck
  structurally cannot see (`README.md`, `pyproject.toml`; SC#1's reason for existing).
  URL-pattern excludes via `.lycheeignore` (regex), path excludes supported. Confirmed actively
  maintained 2026-07-26.
- **D-02: Triggers are PR and push only — no scheduled run.** Owner decision. The 7 dead links
  that motivated this milestone were wrong at the moment they were written — a PR-time check
  catches that class. **Accepted limitation:** an external URL that dies with no commits in
  flight goes undetected until the next PR/push.
- **D-03: Scan the whole repository; exclude by path, never by URL pattern.** Excludes:
  `.planning/` (many historical dead URLs; includes INTEGRATIONS.md — see D-19),
  `CHANGELOG.md` (its historical github.io URL 404s after Phase 32 and would leave the job
  permanently red), plus tests/fixtures fake URLs if needed. **Excluding the `github.io` URL
  pattern is forbidden** — it would blind SC#1's negative control.
- **D-04: Failure presentation is a red, non-required check.** The dedicated workflow fails
  normally; it is never registered as a GitHub Required check (SC#3 / drift.yml precedent,
  D-07). No `continue-on-error` always-green masking — that contradicts CI-05's purpose.
- **D-05: Location is a new standalone `.github/workflows/links.yml`.** Same shape as the
  advisory precedent drift.yml. SC#3's "scope documented where it lives" (that THIS job, not
  sphinx linkcheck, covers `README.md` / `pyproject.toml`) goes in a comment block at the top
  of the file.
- **D-06: Lenient false-positive posture.** Retries enabled + accept 429 + a reasonable
  timeout. The target signal is a persistent 404, not a transient 429. **Exact parameter values
  are Claude's discretion** (tuned via branch push → CI observation, per D-08).
- **D-07: HTTP(S) URLs only.** Local/relative file-link existence checking is out of scope
  (owner choice).
- **D-08: lychee is never run locally — CI only.** Explicit owner instruction (does not want to
  run Rust binaries locally in this environment). All lychee execution, including parameter
  tuning, happens via pushing to the branch and observing GitHub Actions. SC#2's real-HTTP
  verification uses `curl` (fine locally).
- **D-09: SC#1's negative control is recorded as "CI run + transcription."** Commit links.yml
  **before** the rewrite, let CI go red on the tree where the old github.io links are still
  live, then transcribe the failing run's URL and the list of flagged URLs into
  VERIFICATION.md. Proving "CI can detect it" with CI itself is the most faithful reading of
  SC#1. **Plan-ordering implication: the links.yml commit → observed red negative-control run →
  URL-rewrite commit sequence is structurally required.**

### RTD URL shapes to burn in (DOC-09)

- **D-10: The 7 README deep links use `/en/latest/` across the board.** `/en/stable/` does not
  exist until the v0.6.4 tag builds (RTD-06: no existing tag contains `.readthedocs.yaml`, no
  retroactive builds), so burning stable now fails SC#2's "alive over real HTTP, now." `latest`
  tracks `main`, keeping the links the same generation as the README that carries them. No
  rewrite needed in Phase 33 (`latest` never dies).
- **D-11: Top-level links use the bare root `https://typsphinx.readthedocs.io/`.** Applies to:
  README:12 and README:267 Documentation links, `pyproject.toml`'s `Documentation`, and
  About → Website. RTD's root redirects to the Default Version, so these follow Phase 33's
  `latest` → `stable` flip automatically with no re-editing.
- **D-12: README:8's badge becomes RTD's official build-status badge**
  (`https://app.readthedocs.org/projects/typsphinx/badge/?version=latest`). It flips
  passing → failing with the actual docs build — the badge itself becomes monitoring. The
  static shields.io badge is dropped.
- **D-13: README gains a one-line link to the Japanese documentation**
  (`https://typsphinx.readthedocs.io/ja/latest/`) — discoverability for Phase 30.1's
  deliverable. That URL joins SC#2's real-HTTP verification set. Exact placement and wording
  are Claude's discretion.
- **The rewrite-target count is taken from a fresh grep at execution time** (SC#2's explicit
  wording + milestone invariant #4). Measured 2026-07-26: 10 github.io occurrences in
  `README.md` (`:8`, `:12`, `:267`, `:271-277`), plus `pyproject.toml:56`'s
  `Documentation = "https://github.com/YuSabo90002/typsphinx#readme"` (not github.io, but it
  points at the old README — a rewrite target).

### Issue #119 close and About sequencing (DOC-10)

- **D-14: About → Website is set immediately during Phase 31 execution (owner-manual).** Value
  is D-11's bare root. This link is exactly what put101 hit, so the reported symptom is
  resolved the moment it is set. Criterion 4's second half (the About URL resolves over real
  HTTP) is verified with `curl` within Phase 31.
- **D-15: Issue #119 is closed after the milestone merge (at `/gsd-complete-milestone`).**
  Owner decision — close only once the README rewrite is visible on `main` and everything
  promised has landed. **The close half of ROADMAP SC#4 therefore moves outside Phase 31's
  verification window**: Phase 31's verification confirms "About set + resolving + close-reply
  draft prepared," and the close itself is recorded as a **handoff** to milestone close
  (managed alongside the three owed post-merge flips). The verifier must treat this as an
  owner-decided handoff, not a gap.
- **D-16: The close reply flow is draft → owner review → post.** Same flow as the PR#98
  precedent. English, terse, whole-thread-read (the owner's existing reply already promises
  "fix the Website link and the README deep links").
- **D-17: Reply content is the fulfillment report only.** The new (RTD) URL and the fact that
  About and README are fixed — kept short. No migration-background narrative, no old-URL-404
  announcement.

### INTEGRATIONS.md rewrite depth

- **D-18: `.planning/codebase/INTEGRATIONS.md` gets a full refresh.** Owner choice (beyond the
  ROADMAP-minimum option). Re-analyze the whole file and update its Analysis Date. Required
  updates (measured 2026-07-26): the Hosting section has zero RTD content / "CI only:
  SPHINX_LANGUAGE" must become Phase 29's `READTHEDOCS_LANGUAGE > SPHINX_LANGUAGE > "en"`
  seam / the docs.yml description predates Phase 30's changes / actions version drift (file
  says checkout@v6; drift.yml actually uses @v7) / the `typsphinx-doc-translations` repository +
  submodule + pin-bump workflow (Phase 30.1) are absent / links.yml (new in this phase) must be
  added. **Partial re-staling by Phase 32's docs.yml reduction is accepted** — Phase 32 updates
  its delta then.
- **D-19: No carve-out of INTEGRATIONS.md from links.yml's `.planning/` exclusion.**
  INTEGRATIONS.md's URLs are verified once by SC#2's execution-time `curl`, not by ongoing CI.

### Claude's Discretion

- Exact lychee parameter values (retry count, timeout, precise accepted-status set, caching) —
  within D-06's lenient posture.
- Exact exclusion mechanics (`--exclude-path` vs `.lycheeignore` split) and whether
  tests/fixtures fake URLs need excluding.
- Placement and wording of the one-line ja link in README (D-13).
- Verifying the 7 deep-link target paths exist on RTD and adjusting shapes if needed
  (e.g. `user_guide/` → `user_guide/index.html`) — SC#2's curl checks them regardless.
- Section structure of the INTEGRATIONS.md full refresh.
- The #119 close-reply draft wording (owner reviews before posting, D-16).

### Folded Todos

- **`.planning/todos/pending/2026-07-22-github-io-doc-links-404-missing-en-prefix.md`** — the 7
  README github.io deep links 404 (missing `/en/` prefix). Already promoted to Phase 31
  (DOC-09) in STATE.md. Resolved by D-10's `/en/latest/` rewrite. **Close this todo when the
  rewrite commit lands.**

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope and constraints
- `.planning/ROADMAP.md` § "Phase 31" — goal, 4 success criteria, owner-manual dependency
  (About → Website), Notes (INTEGRATIONS.md needs a paragraph-level rewrite; why this phase is
  ordered before Phase 32). **SC#4's close half is moved post-merge by D-15 — this CONTEXT
  wins at verification time.**
- `.planning/REQUIREMENTS.md` — DOC-09 / DOC-10 / CI-05 text; § "Milestone Invariants"
  (especially #4 fresh grep); § "Out of Scope" LNK-01 (why sphinx linkcheck was dropped).
- `.planning/STATE.md` § "Accumulated Context" — advisory precedent (drift.yml, D-07), the
  `ui.plan-gate` false-positive note (use `--skip-ui`), the honest-verifier rule.

### Prior phase context (do not re-derive)
- `.planning/phases/30-japanese-rtd-site-hand-rolled-machinery-orphan-removal/30-CONTEXT.md` —
  D-14 (docs.yml `publish_dir` repoint; deletion is Phase 32's), advisory-CI precedent note.
- `.planning/phases/29-rtd-build-establishment-english-parent-pdf-path-decision/29-CONTEXT.md` —
  the parent slug `typsphinx` decision (D-01/D-02) — the base of every URL this phase burns
  into README/pyproject/About.
- `29-VERIFICATION.md` § "Phase 33 Handoff Precondition" — the owed Default Version
  latest→stable and Default branch → main flips. **D-15's #119 close joins this handoff list.**

### External tools measured during this discussion
- `https://github.com/lycheeverse/lychee-action` — lychee-action v2 (maintenance status,
  supported formats, `.lycheeignore` confirmed 2026-07-26). Implementation basis for D-01.
- `.github/workflows/drift.yml` — the advisory standalone-workflow precedent (structural
  reference).

### Files this phase touches or measures
- `README.md` — `:8` badge (D-12), `:12` / `:267` top links (D-11), `:271-277` the 7 deep
  links (D-10), one-line ja link added (D-13).
- `pyproject.toml:56` — `Documentation` → bare root (D-11). `:55` Homepage / `:57-58`
  Repository/Issues correctly point at GitHub and are NOT rewrite targets.
- `.planning/codebase/INTEGRATIONS.md` — full refresh (D-18).
- `.github/workflows/links.yml` — new (D-05).
- `CHANGELOG.md:393` — **untouched** (settled).
- Issue #119 (`https://github.com/YuSabo90002/typsphinx/issues/119`) — OPEN. The owner's
  existing reply promises the Website + README fixes. Close happens post-merge (D-15).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`.github/workflows/drift.yml`** — a live template for an advisory standalone workflow
  (minimal permissions, not Required). Structural basis for links.yml.
- **RTD public URLs/APIs need no auth and are curl-measurable** (established Phases 29/30.1) —
  every verification instrument SC#2 needs is already at hand.

### Established Patterns
- **Advisory CI (never a required check)** — drift.yml precedent (v0.6.4 D-07). links.yml gets
  the same treatment.
- **Fresh grep at execution time** (milestone invariant #4) — re-measure the rewrite-target
  count at execution. Already on record: the brief said 9, measurement says 10.
- **Verification evidence is verbatim command + output transcription** (Phase 29 D-15 form) —
  D-09's CI-run transcription follows the same convention.
- **Outward-facing artifacts: English, terse, whole-thread-read** (PR#98 lesson) — applies to
  the #119 reply (D-16/D-17).

### Integration Points
- **GitHub repository settings (owner-manual):** set About → Website to the bare root (D-14).
  Unassertable from inside the repo; only the URL's resolution is curl-verified (criterion 4).
- **Addition to the `/gsd-complete-milestone` procedure:** the #119 close (draft review → post
  → close) joins the milestone-close work items (D-15), managed on the same handoff list as
  the existing owed flips (RTD Default branch ×2, `.gitmodules` branch, Default Version flip).

### Environment constraint (must be briefed to every executor)
- **Never run lychee locally (D-08)** — owner instruction for this NixOS-sandbox dev
  environment (no local Rust binaries). Validate/tune links.yml by pushing to the branch and
  observing GitHub Actions. `curl` is fine locally.

</code_context>

<specifics>
## Specific Ideas

Measured 2026-07-26 (re-measure with a fresh grep at execution time):

- **github.io occurrences (excluding `.git` / `.planning`):** `README.md` 10 sites (`:8`,
  `:12`, `:267`, `:271` Installation, `:272` Quick Start, `:273` User Guide, `:274`
  Configuration, `:275` Examples, `:276` API, `:277` Contributing) + `CHANGELOG.md:393`
  (untouched). Zero occurrences under `docs/source/` (re-confirming the research-time grep).
- **`pyproject.toml` `[project.urls]`:** `Documentation = ".../typsphinx#readme"` (not
  github.io, but it points at the old README — rewrite target). Homepage/Repository/Issues
  correctly point at GitHub.
- **Issue #119:** put101 reported "go on link in github right hand side panel → 404". The
  owner's existing reply promises the Website-link + README-deep-link fixes; unfulfilled and
  OPEN.
- **INTEGRATIONS.md staleness (measured):** zero RTD content / only `SPHINX_LANGUAGE`
  documented / says actions/checkout@v6 while drift.yml uses @v7 / no translations-repository
  content.
- **Deep-link shapes after D-10:** e.g.
  `https://typsphinx.readthedocs.io/en/latest/installation.html`. Directory-style links
  (`user_guide/`, `examples/`, `api/`) must be curl-confirmed against RTD before burning in.

</specifics>

<deferred>
## Deferred Ideas

- **Weekly scheduled run for external-link rot** — D-02 chose PR/push only, so URL death with
  no commits in flight goes undetected between pushes. If operation shows the need, extending
  links.yml is a one-block `schedule:` addition.
- **Repo-internal relative file-link checking** — limited to HTTP(S) by D-07; a lychee builtin
  that can be enabled later.
- **Putting `.planning/codebase/` under ongoing link watch** — declined in D-19.
- **CHANGELOG.md's github.io 404 after Phase 32** — excluded from links.yml, so no red job;
  revisit only if the keep-as-history decision is ever reversed.

### Reviewed Todos (not folded)

- **`2026-07-21-move-documentation-hosting-to-read-the-docs.md`** — `resolves_phase: 32`. This
  phase executes its URL-rewrite slice, but the todo stays open until the Pages teardown
  (Phase 32).
- **`2026-07-22-add-sphinx-linkcheck-ci-job.md`** — stays deferred as Future LNK-01
  (structurally blind to README/pyproject). CI-05 (this phase) covers the real failure class.
- **`2026-07-22-citation-node-support-untracked.md`** /
  **`2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md`** /
  **`2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`** /
  **`2026-07-25-derive-typst-lang-duplicated-warning-block.md`** — all require `typsphinx/`
  runtime changes, forbidden by milestone invariant #3.

</deferred>

---

*Phase: 31-Published-URL Cutover + Repo-Wide Link Guard*
*Context gathered: 2026-07-26*
