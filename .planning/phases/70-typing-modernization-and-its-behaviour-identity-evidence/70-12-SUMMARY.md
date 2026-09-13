---
phase: 70-typing-modernization-and-its-behaviour-identity-evidence
plan: 12
subsystem: docs
tags: [docs, sphinx, typst, viewcode, intersphinx, docs-diff, DOC-23]

# Dependency graph
requires:
  - phase: 70-02
    provides: PHASE_BASE_SHA, VENV_HOME, VENV_VERSION_INFO (baseline evidence)
  - phase: 70-03
    provides: DOCS_HTML_MANIFEST_SHA256_BEFORE, DOCS_TYP_MANIFEST_SHA256_BEFORE (docs base manifests, D-09)
  - phase: 70-09
    provides: the flip commit (0224b5ea) dropping the UP006/UP035 ignores
provides:
  - "70-DOCS-DIFF-EVIDENCE.md: three clean docs builds (base A, base B, post-flip C) in one detached worktree, an empty base-vs-base control, a base cross-check against wave 1, the confined differing-file list, all 83 raw hunks, and a full D-11 classification table with DOC23_VERDICT = MET"
affects: [70-13, ship/release-prep for v0.9.4]

# Actuals (#2632)
actuals:
  tokens: 24726
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns: ["masked A/B/C docs-diff evidence with a same-path control build, reused from the D-05 corpus-diff pattern"]

key-files:
  created:
    - .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-DOCS-DIFF-EVIDENCE.md
    - .planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-12-SUMMARY.md
  modified: []

key-decisions:
  - "Confirmed D-11 as amended: the five A-vs-C differing pages (api/index.html, api/index.typ, and four _modules/typsphinx/*.html viewcode pages) are exactly the shape Pitfall 8 predicted, and all 83 hunks trace to a converted Dict/List/Set/Tuple annotation, a typing import-line change, or the matching intersphinx link target."
  - "Documented (did not silently work around) a shell-semantics defect in both tasks' <verify><automated> oracles: a bare VAR=\"$(diff ...)\" assignment inherits diff's own nonzero exit status (files differ) and breaks the && chain before any content check runs, independent of locale. Confirmed correct only after adding `|| true` and running under LC_ALL=C (this host's default locale is ja_JP.UTF-8, which also breaks the English-text grep patterns `' differ$'` and `'^Only in'`). The literal, unmodified Task 2 verify command happened to have no such bare-assignment step and passed cleanly once evidence was correct."

requirements-completed: [DOC-23]

coverage:
  - id: D1
    description: "Three clean docs builds (base A, base B, post-flip C) in one detached worktree W, each exiting 0, with an empty base-vs-base control on both HTML and .typ outputs"
    requirement: DOC-23
    verification:
      - kind: other
        ref: "70-DOCS-DIFF-EVIDENCE.md ## Builds / ## Control (A vs B) (BUILD_EXITS = 0 0 0 0 0 0, DOCS_HTML_CONTROL = EQUAL, DOCS_TYP_CONTROL = EQUAL)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Base build A cross-checked against 70-03's wave-1 manifests (DOCS_BASE_CROSSCHECK)"
    requirement: DOC-23
    verification:
      - kind: other
        ref: "70-DOCS-DIFF-EVIDENCE.md ## Base cross-check (both SHA-256 hashes equal 70-CORPUS-DOCS-BASE-EVIDENCE.md's DOCS_HTML_MANIFEST_SHA256_BEFORE / DOCS_TYP_MANIFEST_SHA256_BEFORE)"
        status: pass
    human_judgment: false
  - id: D3
    description: "A-vs-C differing files confined to D-11's amended locations (api/ and _modules/typsphinx/), no file appears or vanishes"
    requirement: DOC-23
    verification:
      - kind: other
        ref: "70-DOCS-DIFF-EVIDENCE.md ## Differing files (A vs C) (5 DIFF_HTML lines, 1 DIFF_TYP line, all under api/ or _modules/typsphinx/)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every one of the 83 A-vs-C hunks (62 HTML + 21 .typ) recorded verbatim and classified TRACED against a converted annotation, import-line change, or intersphinx link target -- including the two Pitfall-9 Optional[...]->...|None shape changes"
    requirement: DOC-23
    verification:
      - kind: other
        ref: "70-DOCS-DIFF-EVIDENCE.md ## D-11 classification (TRACED_HUNKS = 83, UNTRACED_HUNKS = 0, DOC23_VERDICT = MET)"
        status: pass
    human_judgment: true
    rationale: "D-11's classification is a judgment call by design (Pitfall 9: no literal-substring matcher can verify a hunk traces to a converted annotation). The plan's own <human-check> requires the owner to read the classification table at end-of-phase and confirm each TRACED row's 'traces to' names a converted annotation or typing import line."
---

# Phase 70 Plan 12: DOC-23 Docs Diff Evidence Summary

**DOC23_VERDICT = MET: all 83 A-vs-C docs hunks (62 HTML, 21 .typ) trace to a converted Dict/List/Set/Tuple rename or typing import-line change; DOCS_BASE_CROSSCHECK = EQUAL; no owner finding beyond the two Pitfall-9 shape changes already anticipated by D-11 as amended.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-09-13T05:37:00Z (approx.)
- **Completed:** 2026-09-13T05:57:01Z
- **Tasks:** 2
- **Files modified:** 1 (`70-DOCS-DIFF-EVIDENCE.md`), plus this SUMMARY

## Accomplishments

- Built base A, base B (again at `PHASE_BASE_SHA`), and post-flip C in one detached worktree `W` at
  one scratch path, each preceded by `rm -rf _build`, all six builds (html+pdf x 3 rounds) exiting 0.
- Proved the base-vs-base control empty on both outputs: `diff -rq --exclude=.doctrees` over the A/B
  HTML trees was empty, and the A/B `.typ` SHA-256 manifests matched exactly via `cmp`.
- Cross-checked base build A against 70-03's wave-1 manifests: both `DOCS_HTML_MANIFEST_SHA256_BEFORE`
  and `DOCS_TYP_MANIFEST_SHA256_BEFORE` matched exactly (`DOCS_BASE_CROSSCHECK = EQUAL`) — no drift
  between wave-1's docs base and this plan's own re-measured base.
- Confined the A-vs-C differing files to exactly the five pages Research Pitfall 8 predicted:
  `api/index.html`, `api/index.typ`, and the four `sphinx.ext.viewcode` mirrors
  `_modules/typsphinx/{builder,template_engine,translator,writer}.html`. No file appeared or vanished.
- Recorded and classified all 83 hunks (62 across the five HTML pages, 21 in `api/index.typ`) in a
  `H-001`..`H-083` table. Every row traces to a specific converted source line (or its corresponding
  docstring/intersphinx link), and two rows on each side (`build_docnames`/`typst_elements`) show the
  Pitfall-9 `Optional[X]` -> `X | None` textual shape change, correctly classified as TRACED rather
  than escalated.
- Removed and pruned worktree `W`; `git worktree list` confirms it is gone.

## Task Commits

1. **Task 1: Tracer — build base A, base B and post-flip C clean, prove A/B control, cross-check
   against wave 1, confine A-vs-C files to D-11's locations** - `cd1d0fbe` (docs)
2. **Task 2: Record every A-vs-C hunk verbatim and classify each against D-11** - `178412b1` (docs)

_This is a `type: execute` plan (`tdd` not applicable); no test/feat/refactor split applies._

## Files Created/Modified

- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-DOCS-DIFF-EVIDENCE.md` -
  three clean docs builds, the A/B control, the base cross-check, the differing-file lists, all 83 raw
  diff hunks, the full D-11 classification table, and `DOC23_VERDICT = MET`.

## Decisions Made

- Confirmed D-11 as amended (owner's 2026-09-13 plan-phase decision on Research Contradiction C1): the
  location rule admits both `api/…` and `sphinx.ext.viewcode`'s `_modules/typsphinx/…` mirror pages.
  This measurement reproduces exactly the five pages Pitfall 8 predicted at research time — no new
  pages appeared, confirming the amendment was correctly scoped.
- Documented (not silently worked around) a shell-semantics defect present in both tasks' plan-authored
  `<verify><automated>` oracles, and a separate locale sensitivity — see Deviations below.

## Deviations from Plan

### Verify-Oracle Defects Found and Worked Around (not code/evidence defects)

**1. [Oracle defect — shell semantics] Bare `VAR="$(diff ...)"` assignment breaks the `&&` chain when
`diff` correctly reports differences**

- **Found during:** Task 1's `<verify><automated>` command, at the step
  `R="$(diff -rq --exclude=.doctrees "$S/A/html" "$S/C/html")" && ...`.
- **Issue:** In bash, a standalone assignment statement (`VAR=$(cmd)`, no other command on the line)
  adopts the exit status of the command substitution it contains. `diff -rq` exits `1` whenever it
  finds differences — which Task 1's own acceptance criteria *require* (`DOCS_HTML_DIFF_FILES > 0`).
  Because this assignment sits mid-chain in a long `&&`-joined verify script, the chain always
  short-circuits at this exact point with exit status `1`, before any of the content checks (`Only in`,
  hunk/diff-file counts, location-rule grep) ever run — regardless of whether the underlying evidence
  is correct. Empirically confirmed with a minimal repro:
  `bash -c 'x=$(false) && echo REACHED; echo $?'` prints only `1`, never `REACHED`.
- **How confirmed as oracle-only (not a real failure):** built a byte-for-byte copy of the literal
  verify string with only `|| true` appended to that one `diff` call (no other change, no weakening of
  any comparison), and re-ran it: it passed end-to-end (`EXITCODE:0`), proving every actual content
  check in the plan's Task 1 verify (control-equality, cross-check, location rule, file-list identity,
  hunk-count identity, `W` absence, section presence, no-HALT) is satisfied by the recorded evidence.
- **Fix:** none applied to the plan or the evidence file (out of this plan's declared file scope:
  `files_modified` names only `70-DOCS-DIFF-EVIDENCE.md`). No file was edited to work around this —
  the finding is reported here for the orchestrator/owner to decide whether to patch the verify
  template for future plans of this shape.
- **Verification:** `bash /tmp/.../verify_task1_fixed.sh` (the `|| true`-patched copy, under
  `LC_ALL=C`) → `EXITCODE:0`. The unmodified literal script → `EXITCODE:1` even under `LC_ALL=C`,
  confirming the failure is the shell-semantics bug, not a locale artifact.
- **Committed in:** not applicable (no plan file touched); documented here only.

**2. [Oracle defect — locale sensitivity] `diff`'s default-locale message text breaks
English-pattern `grep` checks on a non-C-locale host**

- **Found during:** the same Task 1 diff calls, and independently while diagnosing #1.
- **Issue:** this worktree's shell defaults to `LANG=ja_JP.UTF-8` (per CLAUDE.md's NixOS-shell note,
  the host's `LANG` passes through unchanged). Neither Task 1's `diff -rq` differing-file check nor its
  `R="$(diff ...)"` differing-hunk classification is wrapped in `LC_ALL=C`, unlike the plan's own build
  commands (which explicitly require `LC_ALL=C`). Under the default locale, `diff -rq` prints
  `ファイル … と … は異なります` instead of `Files … and … differ`, and `grep -c ' differ$'` /
  `grep -q '^Only in'` silently match zero lines instead of the real count.
- **How confirmed:** re-ran the same diff calls with and without `export LC_ALL=C`; the English-text
  form only appears under `LC_ALL=C`. This plan's own evidence recording (`## Differing files (A vs
  C)`) already used `LC_ALL=C diff -rq …` explicitly for this reason, so the evidence file itself is
  unaffected — only a literal, unmodified re-run of the plan's own verify block (which omits
  `LC_ALL=C` on this specific comparison) would be affected on this host.
- **Fix:** none applied to the plan; the evidence file's own recorded transcripts already use
  `LC_ALL=C` for every diff whose output is pattern-matched. Reported for the orchestrator/owner.
- **Verification:** side-by-side diff output with/without `LC_ALL=C`, shown in this SUMMARY's
  reasoning trail (not reproduced verbatim here — see the exact commands above).
- **Committed in:** not applicable.

---

**Total deviations:** 0 auto-fixed (Rules 1–3 did not apply — no code, evidence, or file needed a
fix). 2 oracle defects found and documented per the orchestrator's guidance: "do not edit other files
and do not weaken any check... let the orchestrator decide."
**Impact on plan:** None on the delivered evidence. Both tasks' literal, unmodified
`<verify><automated>` commands were also re-run for confirmation: Task 2's literal script passed
outright (`EXITCODE:0`) because it contains no bare failing-assignment step; Task 1's literal script
requires the two environment adjustments above (`|| true` on one diff call, `LC_ALL=C`) to reach a
pass, and passes fully once applied — the underlying evidence was correct throughout.

## Issues Encountered

None beyond the two verify-oracle defects documented above, which did not block completion of the
plan's actual deliverable (the evidence file and its content).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `70-DOCS-DIFF-EVIDENCE.md` is complete with `DOC23_VERDICT = MET`, ready for the end-of-phase human
  check (owner reads the D-11 classification table) alongside the other Wave 5 audits (70-10, 70-11).
- No blockers for 70-13 or ship/release-prep. The two verify-oracle defects are advisory findings for
  the orchestrator, not blockers on this plan's own deliverable.

## Self-Check: PASSED

- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-DOCS-DIFF-EVIDENCE.md` — FOUND
- `.planning/phases/70-typing-modernization-and-its-behaviour-identity-evidence/70-12-SUMMARY.md` — FOUND
- Task 1 commit `cd1d0fbe` — FOUND in `git log --oneline --all`
- Task 2 commit `178412b1` — FOUND in `git log --oneline --all`
- SUMMARY commit `18ab54bc` — FOUND in `git log --oneline --all`
- Both tasks' `<acceptance_criteria>` re-verified directly (BUILD_EXITS, control equality, base
  cross-check, location rule, hunk-count/table-row/TRACED-row identity) — all PASS
- Plan-level `<verification>` re-confirmed: differing files confined to `api/` and
  `_modules/typsphinx/`, every hunk classified TRACED, base-vs-base control empty

---
*Phase: 70-typing-modernization-and-its-behaviour-identity-evidence*
*Completed: 2026-09-13*
