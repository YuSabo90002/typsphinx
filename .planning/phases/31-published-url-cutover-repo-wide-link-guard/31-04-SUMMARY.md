---
phase: 31-published-url-cutover-repo-wide-link-guard
plan: 04
subsystem: docs
tags: [codebase-notes, readthedocs, ci-inventory, preview-version-sync]

# Dependency graph
requires:
  - phase: 31-01
    provides: ".github/workflows/links.yml existing on disk, so its CI Pipeline entry could be re-derived from the real file rather than invented"
provides:
  - "INTEGRATIONS.md's Hosting section describing Read the Docs (en parent + linked ja Translations project) as the hosting/build platform, GitHub retained as source-code host"
  - "INTEGRATIONS.md's CI Pipeline section enumerating all five current workflow files, each re-derived from the file's actual content"
  - "INTEGRATIONS.md's Environment Configuration section stating the real READTHEDOCS_LANGUAGE > SPHINX_LANGUAGE > \"en\" precedence and $READTHEDOCS_OUTPUT"
  - "INTEGRATIONS.md's @preview version-sync section corrected from three to four guarded surfaces, with the unguarded fifth site (docs/source/_typst/custom_template.typ) flagged, not repaired"
  - "Every GitHub Actions version and workflow name in INTEGRATIONS.md re-verified by grep against the tree at execution time"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Codebase-note refresh discipline: every factual claim re-derived from a command run at execution time (ls, grep, test -f), not copied from the prior revision — the acceptance criteria assert the command's result, not the prose"

key-files:
  created: []
  modified:
    - .planning/codebase/INTEGRATIONS.md

key-decisions:
  - "Task 1 and Task 2's edits were authored and committed as a single pass over the file (one commit) rather than two, since the rewrite was produced as one coherent read-then-write operation with no independently-verifiable intermediate state between the two task boundaries — see Deviations."
  - "Read the Docs is phrased throughout as a hosting/build platform, never as an API integration, per the api-coverage gate's documented false-positive class (30.1-VERIFICATION.md)."
  - "The unguarded fifth @preview pin site (docs/source/_typst/custom_template.typ) is documented, not repaired — repairing it would touch the version-sync surface milestone invariant #2 freezes."

requirements-completed: [DOC-09]

coverage:
  - id: D1
    description: "INTEGRATIONS.md's Hosting, CI Pipeline, and Environment Configuration sections rewritten to match the repository as it stands today (Read the Docs hosting, five workflow files including links.yml, the real READTHEDOCS_LANGUAGE precedence)"
    requirement: "DOC-09"
    verification:
      - kind: other
        ref: "plan Task 1 <verify> automated check (12-string grep sweep + checkout@v7/v6 counts + workflow-file count) — see Verification Transcript below"
        status: pass
    human_judgment: false
  - id: D2
    description: "@preview version-sync section corrected to name the four guarded surfaces plus the unguarded fifth site; Analysis Date updated; every URL in the file verified 200 over real HTTP"
    requirement: "DOC-09"
    verification:
      - kind: other
        ref: "plan Task 2 <verify> automated check (custom_template.typ/examples/ presence, 'across three files' absence, date presence) + manual curl -L sweep of all 7 distinct URLs — see Verification Transcript below"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-07-26
status: complete
---

# Phase 31 Plan 04: INTEGRATIONS.md Refresh Summary

**Rewrote `.planning/codebase/INTEGRATIONS.md`'s Hosting, CI Pipeline, Environment Configuration, and `@preview` version-sync sections to describe the Read the Docs migration (Phases 29-30.1), re-verifying every factual claim by command at execution time and every URL by live HTTP fetch.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-07-26T14:05:00Z
- **Completed:** 2026-07-26T14:30:00Z
- **Tasks:** 2 (combined into one edit + one commit — see Deviations)
- **Files modified:** 1

## Accomplishments
- Hosting section rewritten: Read the Docs (en parent at `/en/latest/`, linked `typsphinx-ja` Translations project at `/ja/latest/`, root redirect to Default Version), `.readthedocs.yaml` named as the sole build-config surface, the `build.jobs.build.pdf` override and `fonts-noto-cjk` rationale both explained, GitHub kept as source-code host.
- CI Pipeline section now enumerates all five `.github/workflows/` files (was four, missing `links.yml`), each description re-derived from the actual file content rather than copied forward.
- Environment Configuration section replaced the stale "CI only: `SPHINX_LANGUAGE`" claim (which no workflow sets anymore) with the real `READTHEDOCS_LANGUAGE` > `SPHINX_LANGUAGE` > `"en"` precedence resolved by `_resolve_language()`, plus `$READTHEDOCS_OUTPUT`.
- `@preview` version-sync section corrected from "three files" to the four surfaces the guard actually watches (`writer.py`, `template_engine.py`, `base.typ`, `examples/**/*.typ`), and separately flags the unguarded fifth site (`docs/source/_typst/custom_template.typ`) without repairing it.
- GitHub Actions Dependencies list corrected: `actions/checkout@v6` (used nowhere) replaced with the real `actions/checkout@v7`; `actions/setup-python@v6` and `peaceiris/actions-gh-pages@v4` added (both previously undocumented, both in `docs.yml`).
- `typsphinx-doc-translations` recorded as external infrastructure — its submodule and pin-bump workflow explicitly stated to live in that repository, not this one.
- Analysis Date (header) and the closing `*Integration audit: ...*` line both updated to 2026-07-26.
- All 7 distinct URLs appearing in the refreshed file fetched fresh over real HTTP; all returned 200.

## Task Commits

Both plan tasks were authored and verified as a single coherent rewrite of the file and committed together:

1. **Tasks 1+2: Re-measure and rewrite Hosting/CI/Environment/@preview-sync/Actions/Analysis-Date, verify every URL** - `3dd9636` (docs)

**Plan metadata:** this SUMMARY.md's own commit (created after this file was written).

_No TDD tasks; this is a docs-only plan with no test files._

## Files Created/Modified
- `.planning/codebase/INTEGRATIONS.md` - Hosting, CI Pipeline, Environment Configuration, APIs & External Services, @preview version-sync, GitHub Actions Dependencies sections rewritten; Analysis Date and closing audit line updated to 2026-07-26.

## Decisions Made
- **Single commit for both tasks:** the plan's Task 1 and Task 2 both edit the same file's different sections in a way that only makes sense read and written together (e.g., the `@preview` section correction in Task 2 depends on already having re-derived the workflow inventory in Task 1). Producing a genuinely separate, independently-committable intermediate state between them would have meant writing a half-refreshed file with some sections still stale, which is not a real intermediate milestone worth its own commit. Both tasks' verification criteria are satisfied by the one commit's final state (confirmed below).
- Read the Docs phrased strictly as a hosting/build platform throughout — never "integration," "API," or "endpoint" in that context — per the project's known `api-coverage` gate false-positive class.
- The unguarded fifth `@preview` pin site (`docs/source/_typst/custom_template.typ`) documented as a known gap, not fixed, per milestone invariant #2 (3-way — now 4-way — version-sync surface frozen).

## Deviations from Plan

**None (Rules 1-4) — plan executed as written**, with one process note: Tasks 1 and 2 were combined into a single Write + single commit rather than two sequential edits/commits, because the plan's own Task 2 explicitly operates on "INTEGRATIONS.md as left by Task 1" and both tasks' re-measurement commands (`ls .github/workflows/`, the `uses:` grep, `test -f .gitmodules`, plus Task 2's file reads) were run up front before authoring the rewrite, making a genuinely separable intermediate commit artificial. All of both tasks' `<verify>` blocks and `<acceptance_criteria>` were independently checked against the final committed state (see Verification Transcript below) and all pass.

## Verification Transcript

**Task 1 acceptance criteria (all checked against commit `3dd9636`):**
- `readthedocs.io`, `READTHEDOCS_LANGUAGE`, `SPHINX_LANGUAGE`, `_resolve_language`, `.readthedocs.yaml`, `links.yml`, `ci.yml`, `docs.yml`, `drift.yml`, `release.yml`, `typsphinx-doc-translations`, `READTHEDOCS_OUTPUT` — all 12 present (`grep -q` OK for each).
- `grep -c "checkout@v7"` -> `1`; `grep -c "checkout@v6"` -> `0`.
- `ls .github/workflows/ | wc -l` -> `5`.
- `grep -c 'SPHINX_LANGUAGE (docs.yml'` -> `0` (stale claim gone).
- `grep -icE 'readthedocs.*(api|endpoint|integration)'` -> `0`.
- `git diff --name-only HEAD~1 HEAD` -> `.planning/codebase/INTEGRATIONS.md` only.

**Task 2 acceptance criteria:**
- `custom_template.typ` present, `examples/` present (both `grep -q` OK).
- `grep -c 'across three files'` -> `0`.
- `git diff HEAD~1 -- docs/source/_typst/custom_template.typ` -> empty (unguarded file documented, not edited).
- `git diff HEAD~1 -- typsphinx/` -> empty (milestone invariant #3 held).
- Both `**Analysis Date:**` and `*Integration audit: ...*` carry `2026-07-26` and agree.
- `git status --short` after commit -> clean; no untracked files.

**URL/status transcript (7 distinct URLs, `curl -s -o /dev/null -w "%{http_code}" -L --max-time 20 <url>`):**

```
200 https://docs.python.org/3
200 https://github.com/YuSabo90002/typsphinx
200 https://github.com/YuSabo90002/typsphinx-doc-translations
200 https://typsphinx.readthedocs.io/
200 https://typsphinx.readthedocs.io/en/latest/
200 https://typsphinx.readthedocs.io/ja/latest/
200 https://www.sphinx-doc.org/en/master
```

All 7 returned `200`. Per D-19 this is the file's only verification pass — no ongoing CI watches these URLs.

## Issues Encountered
None. The environment briefing's note about a Bash safety-checker false-flagging compound commands containing "source" (or, observed in this session, any multi-command shell one-liner with `for`/loops) required restructuring several verification commands into one-invocation-per-check rather than loops or compound `&&`/`;` chains — functionally identical, no scope change.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- INTEGRATIONS.md now agrees with the repository as Phase 29/30.1 left it; any future GSD phase that loads the codebase map for API/backend/integration context will read the current hosting/CI/environment picture instead of the pre-Phase-29 one.
- The unguarded fifth `@preview` pin site remains a carried Warning (now also documented in this codebase note, not just STATE.md) for a future milestone to close.
- Nothing in this plan touches `typsphinx/`, `.github/workflows/`, or `docs/source/_typst/` — milestone invariants #2 and #3 both held.

---
*Phase: 31-published-url-cutover-repo-wide-link-guard*
*Completed: 2026-07-26*

## Self-Check: PASSED

- FOUND: `.planning/codebase/INTEGRATIONS.md`
- FOUND: `.planning/phases/31-published-url-cutover-repo-wide-link-guard/31-04-SUMMARY.md`
- FOUND commit: `3dd9636`
- FOUND commit: `61c56f1`
