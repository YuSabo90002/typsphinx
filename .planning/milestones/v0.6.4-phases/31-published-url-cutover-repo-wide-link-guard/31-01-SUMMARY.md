---
phase: 31-published-url-cutover-repo-wide-link-guard
plan: 01
subsystem: ci
tags: [github-actions, lychee, link-checking, ci, advisory-workflow]

# Dependency graph
requires:
  - phase: 30.1-translations-repository-japanese-rtd-site
    provides: the live typsphinx-doc-translations submodule and ja RTD site whose URLs this job's scan surface now includes
provides:
  - ".github/workflows/links.yml — advisory, non-required repo-wide real-HTTP link check (job link-check)"
  - "a live red CI run proving the mechanism catches the 7 old-host README deep links, transcribed in 31-EVIDENCE.md"
  - "repaired pre-existing dead links in examples/ and docs/source/changelog.rst, unblocking the job from being permanently red"
affects: [31-02-about-website-and-issue-close, 31-04-doc09-url-rewrite, 31-05-post-rewrite-green-run]

# Tech tracking
tech-stack:
  added: ["lycheeverse/lychee-action@v2 (CI-only, never run locally per D-08)"]
  patterns:
    - "Advisory standalone workflow (never a required status check), same shape as .github/workflows/drift.yml"
    - "push-observe tuning loop: CI-only tool validated/tuned by pushing and reading GitHub Actions runs, not local execution"
    - "temporary diagnostic workflow (add -> observe -> remove) to get definitive log evidence for a false-negative trap, without changing the final deliverable's committed shape"

key-files:
  created:
    - .github/workflows/links.yml
    - .planning/phases/31-published-url-cutover-repo-wide-link-guard/31-EVIDENCE.md
  modified:
    - examples/basic/README.md
    - examples/basic/index.rst
    - examples/advanced/README.md
    - docs/source/changelog.rst

key-decisions:
  - "Negative-control evidence cites the run on the current HEAD (30205112477, SHA eaee760) as primary, with the earlier run (30204930428, SHA 7821f32) recorded as corroborating — both show the identical 7-deep-link failure set."
  - "A single --verbose does not print per-file OK-status lines in lychee's Info-level reporter, so pyproject.toml's clean scan is invisible in the real check run's log; a temporary --dump-inputs diagnostic workflow (added, observed, removed in three commits) was the only way to get affirmative proof it was scanned, per RESEARCH.md Pitfall 2 / Assumption A1."

requirements-completed: [CI-05]

coverage:
  - id: D1
    description: "Standalone advisory Link Check workflow (.github/workflows/links.yml): push+pull_request only, contents:read only, --scheme https/http, --extensions incl. toml, 3 regex --exclude-path excludes, no continue-on-error, no schedule, no .lycheeignore"
    requirement: "CI-05"
    verification:
      - kind: unit
        ref: "inline python/yaml structural assertion (see Task 1 <verify>) — links.yml structure OK"
        status: pass
      - kind: other
        ref: "9 grep-based acceptance criteria (continue-on-error=0, schedule:=0, bare --exclude=0, exclude-path=3, scheme=2, no .lycheeignore, issues:=0, comment-block strings present, git diff scoped to 1 file)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Repaired 4 placeholder-owner dead links across examples/ and 1 dead 'Project Roadmap' link in docs/source/changelog.rst so the new job is not permanently red on the rewritten tree"
    verification:
      - kind: other
        ref: "curl -s -o /dev/null -w '%{http_code}' -L https://github.com/YuSabo90002/typsphinx and .../issues -> 200/200; grep confirms zero 'your-repo' occurrences and zero 'typsphinx/projects' occurrences"
        status: pass
    human_judgment: false
  - id: D3
    description: "Live red CI run (D-09 negative control) proving the mechanism catches all 7 old-host README deep links, with the 4 false-negative traps (parse error, unscanned pyproject.toml, ineffective path exclusions, missing deep links) each explicitly ruled out with quoted log evidence in 31-EVIDENCE.md"
    requirement: "CI-05"
    verification:
      - kind: integration
        ref: "gh run view 30205112477 --json conclusion -> failure; gh run view --log grepped for the 7 deep-link 404s and the summary-table completion line"
        status: pass
      - kind: other
        ref: "diagnostic run 30205087374 (--dump-inputs) log line './pyproject.toml' and the full 26-file resolved-input dump (no .planning/, no root CHANGELOG.md, no tests/fixtures/ entry)"
        status: pass
    human_judgment: false

# Metrics
duration: 9min
completed: 2026-07-26
status: complete
---

# Phase 31 Plan 01: Repo-Wide Link Guard + Negative-Control Evidence Summary

**Advisory GitHub Actions link checker (lychee-action@v2) built and proven red on the unfixed tree, catching all 7 old-host README deep links before the URL rewrite lands.**

## Performance

- **Duration:** 9 min
- **Started:** 2026-07-26T22:51:45+09:00
- **Completed:** 2026-07-26T23:00:29+09:00
- **Tasks:** 3
- **Files modified:** 6 (5 deliverable files + 1 evidence file; a 7th file, a temporary diagnostic workflow, was added and removed within the same session)

## Accomplishments
- Built `.github/workflows/links.yml` — a standalone, advisory (never-required) real-HTTP link checker covering exactly the file class Sphinx's own `linkcheck` builder structurally cannot see (`README.md`, `pyproject.toml`), with `toml` added to lychee's extension allow-list and three regex path exclusions for `.planning/`, `CHANGELOG.md`, and `tests/fixtures/`.
- Repaired 5 pre-existing dead links unrelated to this milestone (4 placeholder-owner URLs in `examples/`, 1 dead GitHub Project board link in `docs/source/changelog.rst`) so the new job isn't permanently red on the rewritten tree.
- Pushed the branch and captured a live red CI run (D-09's negative control): the job failed exactly on the 7 old-host README deep links that motivated this milestone, proving SC#1's claim that the mechanism *would have* caught them.
- Closed RESEARCH.md's Pitfall 2 / Assumption A1 (was `pyproject.toml` silently skipped?) with a temporary `--dump-inputs` diagnostic workflow — added, observed, removed — that produced definitive log proof `pyproject.toml` is a scanned input, plus a full resolved-input dump proving `.planning/`, `CHANGELOG.md`, and `tests/fixtures/` are genuinely absent from the scan.
- Confirmed branch protection's required status checks do not include the new job (D-04) and that `--scheme https/http` correctly excludes every relative/local link (D-07) rather than silently checking it.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create the advisory repo-wide link-check workflow** - `fede6f0` (feat)
2. **Task 2: Repair the pre-existing dead links that would keep the job red** - `7821f32` (fix)
3. **Task 3: Push, observe the red negative-control run, transcribe the evidence** - `f92ce53` (docs)
   - Interleaved diagnostic sub-commits (added and removed within Task 3, not separate tasks): `ddf1b32` (chore: add temp diagnostic workflow), `eaee760` (chore: remove it)

**Plan metadata:** (none yet — this summary + STATE/ROADMAP updates are the orchestrator's responsibility per worktree isolation)

## Files Created/Modified
- `.github/workflows/links.yml` - New advisory Link Check workflow (job `link-check`)
- `examples/advanced/README.md` - Placeholder owner `your-repo` -> `YuSabo90002` (2 occurrences)
- `examples/basic/README.md` - Placeholder owner `your-repo` -> `YuSabo90002` (1 occurrence)
- `examples/basic/index.rst` - Placeholder owner `your-repo` -> `YuSabo90002` (1 occurrence)
- `docs/source/changelog.rst` - Removed the dead "Project Roadmap" link, kept the surviving GitHub Issues link
- `.planning/phases/31-published-url-cutover-repo-wide-link-guard/31-EVIDENCE.md` - D-09 negative-control transcription (run URL/SHA, summary counts, full flagged-URL list, all 4 false-negative rule-outs with quoted log evidence, reserved section for Plan 05)

## Decisions Made
- Cited the run on current HEAD (`30205112477`, SHA `eaee760`) as the evidence file's primary record, with the earlier run (`30204930428`, SHA `7821f32`, pre-diagnostic-detour) noted as corroborating — both show the identical 7-deep-link failure, so either is a valid "before the rewrite" observation, but the one matching final HEAD is the more defensible citation.
- Used a temporary, wholly separate diagnostic workflow file (`_diag-dump-inputs.yml`, added then removed) rather than modifying `links.yml` itself, to keep Task 1's committed file exactly matching its specified structure throughout, while still getting CI-only (D-08-compliant) proof of the scanned input set via lychee's `--dump-inputs` mode.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Single `--verbose` doesn't prove `pyproject.toml` was scanned; added a temporary diagnostic workflow to get real evidence**
- **Found during:** Task 3 (transcribing the negative-control evidence)
- **Issue:** The plan's Task 3 required "the log line(s) proving `pyproject.toml` was scanned" as one of four mandatory false-negative rule-outs. The real check run's log (both observed runs) contains zero occurrences of the string "pyproject" anywhere — confirmed by grep. Reading lychee's upstream source (`lychee-bin/src/verbosity.rs`, `formatters/`) explains why: `--verbose` sets Info-level logging, and lychee's Info-level reporter only prints excluded/error/redirect events, never successful ("OK") checks. Since `pyproject.toml`'s 4 URLs are all healthy, a clean scan of it produces literally zero log output under the job's own configuration — making it structurally impossible to distinguish "scanned and healthy" from "silently skipped by the `--extensions` filter" (exactly the false-negative RESEARCH.md Pitfall 2 warned about) from the real check run's log alone.
- **Fix:** Added a temporary `.github/workflows/_diag-dump-inputs.yml` invoking the same `lycheeverse/lychee-action@v2` with `--dump-inputs` (a lychee subcommand that lists every resolved input file, respecting the same `--extensions`/`--exclude-path` filters, without performing any HTTP checks). Pushed it, observed the run (`30205087374`, `success`), captured the definitive log line `./pyproject.toml` plus the full 26-file resolved-input list (proving `.planning/`, root `CHANGELOG.md`, and `tests/fixtures/` are absent too), then removed the temporary file in a follow-up commit so the merged tree carries no trace of it.
- **Files modified:** `.github/workflows/_diag-dump-inputs.yml` (added in commit `ddf1b32`, removed in commit `eaee760` — net zero change to the final tree)
- **Verification:** Diagnostic run log grep for `pyproject` returns the input-dump line; the real check run (re-observed post-removal, `30205112477`) still concludes `failure` with the identical 7-deep-link result, confirming the diagnostic detour didn't alter `links.yml`'s actual behavior.
- **Committed in:** `ddf1b32` (add), `eaee760` (remove); evidence transcribed in `f92ce53`

---

**Total deviations:** 1 auto-fixed (1 blocking — a verification-method gap in the plan's own assumption about what `--verbose` would show)
**Impact on plan:** No scope creep — the final committed `.github/workflows/links.yml` is byte-identical to what Task 1 produced and verified; the diagnostic workflow never persists in the merged tree. The extra push/observe cycle was the sanctioned D-08 "push-observe tuning loop," applied to evidence-gathering rather than parameter tuning.

## Issues Encountered
- The lychee-action's `entrypoint.sh` downloads the `lychee` binary fresh on every job run (no caching), so each CI iteration (2 real check runs + 1 diagnostic run, all in this plan) took a full ~5-second cold-start; not a blocker, just a minor per-iteration cost of the D-08 push-observe loop.

## User Setup Required
None - no external service configuration required. (Owner-manual "About -> Website" step belongs to a later plan in this phase, per `31-CONTEXT.md` D-14.)

## Next Phase Readiness
- `links.yml` is live on `main`'s eventual merge target and already proven to catch the exact bug class (dead docs deep-links) that motivated this milestone.
- The 7 old-host deep links in `README.md` are still unrewritten by design (D-09's ordering requirement) — the DOC-09 URL cutover is a later plan/wave in this same phase; that plan should expect `links.yml` to go green once it lands, and Plan 05 is where that green run gets transcribed into this evidence file's reserved closing section.
- `31-EVIDENCE.md`'s "Post-rewrite green run" section is present but empty, ready for Plan 05.

---
*Phase: 31-published-url-cutover-repo-wide-link-guard*
*Completed: 2026-07-26*

## Self-Check: PASSED

- FOUND: `.github/workflows/links.yml`
- FOUND: `.planning/phases/31-published-url-cutover-repo-wide-link-guard/31-EVIDENCE.md`
- FOUND commit: `fede6f0`
- FOUND commit: `7821f32`
- FOUND commit: `ddf1b32`
- FOUND commit: `eaee760`
- FOUND commit: `f92ce53`
