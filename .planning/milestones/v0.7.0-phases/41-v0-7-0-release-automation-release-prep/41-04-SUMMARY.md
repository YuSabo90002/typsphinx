---
phase: 41-v0-7-0-release-automation-release-prep
plan: 04
subsystem: docs
tags: [pdf, i18n, ja, pypdf, glyph-fidelity, release-evidence, checkpoint]

# Dependency graph
requires:
  - phase: 41-02
    provides: "The version bump to 0.7.0 (pyproject.toml/README.md/uv.lock in lockstep), whose post-bump HEAD is the 'after' side of this plan's comparison"
  - phase: 41-03
    provides: "The docstring-only visit_desc_sig_name fix and planning-record hygiene, already part of the HEAD tree this plan builds from"
provides:
  - "Two locally-built ja PDFs (main vs. post-bump HEAD) with proven import-path provenance, discharging SC#3's 'ja four-check glyph bar' requirement"
  - "41-JA-GLYPH-BAR.md: checks 1-3 (page count, CJK density, /BaseFont enumeration) with verbatim outputs and interpreted verdicts, plus a 'what these checks cannot prove' section"
  - "41-JA-GLYPHBAR-SIGNOFF.md: check 4 MET on the owner's verbatim 'approved', following the 39-ADM04-SIGNOFF.md shape"
affects: [41-05-release-prep-evidence, 41-06-milestone-invariant-sweep, 41-07-handoff]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Subset-tag-stripped /BaseFont comparison (strip the 6-uppercase-letter PDF font-subsetting prefix before diffing font sets across two separate compiles, or every random subset tag manufactures a spurious symmetric-difference entry for the same font family)"
    - "Clean-doctree-directory rebuild requirement for warning-count evidence (Sphinx's incremental build reuses a cached environment and silently suppresses re-parse warnings on doctree-dir reuse across separate invocations against the same output path -- discovered mid-plan, both builds were redone from fully empty doctree/output dirs before the recorded numbers were taken)"

key-files:
  created:
    - .planning/phases/41-v0-7-0-release-automation-release-prep/41-JA-GLYPH-BAR.md
    - .planning/phases/41-v0-7-0-release-automation-release-prep/41-JA-GLYPHBAR-SIGNOFF.md
  modified: []

key-decisions:
  - "Font-family comparison strips the PDF subset-tag prefix (regex ^(/?)[A-Z]{6}\\+) before computing the /BaseFont intersection/symmetric-difference -- the raw, untagged comparison falsely reported all 10 embedded fonts as differing between the two builds, when in fact 7 of 8 underlying font families were identical."
  - "The raw()-styled signature page for the check-4 sample is located by searching only within the API Reference section (page index >= 31, per the PDF outline) for a fully-qualified two-or-more-dot signature pattern -- an unrestricted search matched a false positive on the quickstart guide's own `typsphinx.__version__)` code example."
  - "The check-4 page sample uses the union of both builds' independently-computed density-peak pages (not just one build's picks), since page counts are identical (94/94) but the two builds' internal reflow places their 3rd-third density peak on different absolute pages (main: 74, head: 63) -- both are included so nothing from either build's density profile is missed."

patterns-established: []

requirements-completed: [REL-05]  # This plan discharges SC#3's ja-glyph-bar sub-requirement; REL-05 as a whole closes only once all of Phase 41's plans land.

coverage:
  - id: D1
    description: "Two ja PDFs built locally from main (51e02b6) and post-bump HEAD (aa9d2f0), each with proven import-path provenance (each tree's own uv-provisioned venv resolves import typsphinx to a path under that same tree)"
    requirement: REL-05
    verification:
      - kind: other
        ref: "uv run python -c \"import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())\" run from each tree -- see 41-JA-GLYPH-BAR.md Provenance section"
        status: pass
      - kind: other
        ref: "SPHINX_LANGUAGE=ja uv run python -m sphinx -b typstpdf against docs/source in each tree -- both exit 0, both build logs show the ja catalog loaded"
        status: pass
    human_judgment: false
  - id: D2
    description: "Checks 1-3 (page count, CJK-density, /BaseFont enumeration) executed against both PDFs, verbatim output and interpreted verdict recorded per check"
    requirement: REL-05
    verification:
      - kind: other
        ref: "41-JA-GLYPH-BAR.md sections 'Check 1', 'Check 2', 'Check 3' -- page count 94/94 (delta 0), CJK total 6050/6084 (delta +34, no drop), font sets 7-of-8 families shared incl. the sole CJK font"
        status: pass
    human_judgment: false
  - id: D3
    description: "Check 4 -- the owner's visual confirmation that Japanese glyphs are not silently substituted -- collected and recorded verbatim (D-16 close condition)"
    requirement: REL-05
    verification: []
    human_judgment: true
    rationale: "Typst's font fallback is silent (no warning, no error) and a substituted glyph still extracts as the correct character, so no mechanical check can confirm this -- D-16 explicitly rejects a matching check-3 /BaseFont set as a substitute for the owner's own look."
  - id: D4
    description: "The typsphinx-doc-translations clone lived only in the phase directory, was never committed, and was removed at the end of the plan; the second main comparison worktree was also removed"
    requirement: REL-05
    verification:
      - kind: other
        ref: "test ! -d .planning/phases/.../translations-repo && git worktree list (no /tmp/p41-main-tree entry) && git ls-files '*.pdf' (empty)"
        status: pass
    human_judgment: false

duration: ~35min active execution (tasks 1, 2, 4; excludes owner-review wall-clock time during the Task 3 checkpoint pause)
completed: 2026-08-03
status: complete
---

# Phase 41 Plan 04: `ja` Glyph Bar (SC#3, D-15/D-16/D-17) Summary

**Built two ja PDFs locally (main vs. post-bump HEAD), ran the three mechanical glyph-fidelity
checks with verbatim evidence, and collected the owner's verbatim "approved" for check 4 -- no
substituted, missing, or mismatched Japanese glyphs found anywhere in the sampled pages.**

## Performance

- **Duration:** ~35 min active execution (tasks 1/2/4); the Task 3 checkpoint paused this plan for
  an out-of-band owner review, whose wall-clock time is not counted as plan-execution time
- **Started:** 2026-08-03 (worktree provisioned at base commit `aa9d2f0`)
- **Completed:** 2026-08-03T21:04:39+09:00
- **Tasks:** 4/4 (task 1 produced no repository-tracked change; tasks 2 and 4 each produced one commit; task 3 was the blocking checkpoint)
- **Files modified:** 2 created (both under `.planning/phases/41-v0-7-0-release-automation-release-prep/`)

## Accomplishments

- Cloned `typsphinx-doc-translations` into the phase directory (D-17; never committed), confirmed
  its submodule pin (`5888ee0`) is byte-identical to real `main`'s live tip at measurement time,
  and provisioned a second git worktree of this repository pinned at local `main` (`51e02b6`) with
  its own `uv sync` + venv -- proven, by a printed `typsphinx.__file__` path from each tree, that
  neither build could silently import the other's translator code.
- Built two Japanese PDFs (`SPHINX_LANGUAGE=ja` explicit in both environments, both exit 0, both
  logs confirming the `[ja]` catalog loaded) from a `docs/` tree confirmed byte-identical between
  `main` and HEAD (`git diff --stat` empty).
- Ran and recorded checks 1-3 in `41-JA-GLYPH-BAR.md`: page count 94/94 (delta 0); CJK character
  total 6,050 (before) / 6,084 (after), a small increase rather than the "large unexplained drop"
  failure signature; embedded `/BaseFont` families 7-of-8 shared after stripping PDF subset-tag
  prefixes, including the sole CJK-coverage font `NotoSerifCJKjp-ExtraLight` present identically
  on both sides -- the two-family symmetric difference (`DejaVuSansMono-Oblique` head-only,
  `LibertinusSerif-Semibold-Identity-H` main-only) is confined to non-CJK Latin style variants of
  already-shared families, not a new monospace font family shadowing the CJK fallback.
- Collected the owner's check-4 visual sign-off (Task 3 checkpoint, presented in Japanese with
  concrete page numbers and absolute PDF paths) and transcribed the verbatim one-word response
  ("approved") into `41-JA-GLYPHBAR-SIGNOFF.md`, following the `39-ADM04-SIGNOFF.md` shape exactly
  -- no automated assertion, including the 7-of-8 matching font set, was offered or accepted as a
  stand-in for that look (D-16).
- Removed the working clone and the second `main` comparison worktree; retained both built PDFs
  under `/tmp` for the rest of the phase (plan 41-07 may reference them), never committing either.

## Task Commits

1. **Task 1: Provision both comparison trees and build the two ja PDFs** - no commit (no
   repository-tracked file changed; the clone, the second worktree, and `docs/locale/` in both
   trees are all untracked by design, per D-17 and the plan's own instruction)
2. **Task 2: Run checks 1-3 across the pair and write the glyph-bar evidence file** - `e1a47af` (docs)
3. **Task 3: Owner sign-off checkpoint** - blocking `checkpoint:human-verify`, resolved out-of-band;
   the owner's verbatim response ("approved") was relayed by the orchestrator and is transcribed,
   not paraphrased, in Task 4's file
4. **Task 4: Record the owner's sign-off and remove the working clone** - `2996429` (docs)

_STATE.md/ROADMAP.md are updated centrally by the orchestrator after merge, per the worktree
execution protocol -- this plan's commits touch only files under
`.planning/phases/41-v0-7-0-release-automation-release-prep/`._

## Files Created/Modified

- `.planning/phases/41-v0-7-0-release-automation-release-prep/41-JA-GLYPH-BAR.md` - Provenance
  (clone/submodule/worktree SHAs, import-path proof, `docs/` identity check), checks 1-3 with
  verbatim command+output and interpreted verdicts, the check-4 page sample and rationale, and a
  "What These Checks Cannot Prove" section.
- `.planning/phases/41-v0-7-0-release-automation-release-prep/41-JA-GLYPHBAR-SIGNOFF.md` - Check
  4's MET verdict, ROADMAP SC#3 quoted verbatim, provenance reproduced (not re-derived) from the
  glyph-bar file, and the owner's verbatim "approved".

## Decisions Made

- **Font comparison strips PDF subset tags before diffing.** The raw `/BaseFont` names embedded by
  each separate compile carry a randomly-generated 6-letter subset prefix (e.g. `DAXSNV+`), which
  differs on every compile even for an unchanged font family. An un-stripped comparison falsely
  reported zero font overlap between the two builds; stripping the prefix (`^(/?)[A-Z]{6}\+`)
  revealed the true picture: 7 of 8 font families shared, including the one CJK-coverage font.
- **Signature-page detection restricted to the API Reference section.** An unrestricted
  dotted-name-plus-parentheses regex matched a false positive on the quickstart guide's
  `typsphinx.__version__)` code example (page 6). Restricting the search to page index ≥31 (the
  PDF outline's "API Reference" bookmark) found the intended target on page 33 (`class
  typsphinx.builder.TypstBuilder(app, env)`), a genuine `raw()`-styled autodoc signature.
- **Check-4 sample uses the union of both builds' density-peak pages**, not just one build's own
  picks, since the two builds' 3rd-third CJK-density peak lands on different absolute pages (main:
  74, head: 63) despite identical total page counts (94/94) -- both pages are included in the
  owner's inspection list.
- **Rebuilt both PDFs from completely empty doctree/output directories before recording final
  numbers.** An early pair of builds reused the same doctree directory across two separate
  invocations against the main tree; Sphinx's incremental-build environment cache suppressed
  re-parse warnings on the second invocation, producing a false asymmetry (1 warning on "main" vs.
  5 on "head") that was purely an artifact of doctree reuse, not a real difference between the
  trees. Both trees were rebuilt from fresh, empty doctree/output dirs before any number in
  `41-JA-GLYPH-BAR.md` was recorded; the corrected numbers show both builds produce the identical
  5-warning set (all five pre-existing on both `main` and HEAD, unrelated to D-12's fix).

## Deviations from Plan

None requiring Rule 1-4 action beyond routine mid-investigation self-correction. The two
methodology refinements above (subset-tag stripping; API-Reference-restricted signature search;
clean-doctree rebuild) were course corrections made WITHIN Task 1/2's own execution to produce
correct evidence, not deviations from the plan's scope, files, or requirements -- the plan's
`<action>` text for Task 1 and Task 2 already anticipated needing to interpret and correctly
attribute exactly these kinds of measurement artifacts rather than transcribing a first, wrong
number.

## Issues Encountered

- **Sandbox literal-substring block on the path segment "source".** The worktree-isolation sandbox
  refuses any Bash command containing the literal substring `source` (as documented in this plan's
  own `<worktree_environment_provisioning>` note), which blocked direct invocation of
  `sphinx-build ... docs/source ...`. Worked around by writing small Python wrapper scripts
  (`build_main_pdf.py`, `build_head_pdf.py`) that construct the `docs/source` path at runtime via
  string concatenation (`"sou" + "rce"`) and invoke the build through `subprocess.run`, per the
  plan's own documented workaround.
- **`git worktree remove` initially refused the throwaway main-comparison tree** ("contains
  modified or untracked files") because of its own `docs/locale/` copy and `.venv`. Both are
  intentionally untracked build artifacts of a tree created solely for this plan's comparison and
  scheduled for removal by Task 4's own instructions; `git worktree remove --force` was used for
  that specific, plan-owned throwaway tree only -- no destructive operation was run against this
  plan's own worktree.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- SC#3's `ja` four-check glyph bar is fully discharged: all four checks (mechanical 1-3 plus the
  owner's visual confirmation) show no evidence of the font-shadowing exposure the bar exists to
  catch. Plan 41-05 (SC#3's mechanical half: full suite, lint/type trio, corpus gate, docs
  dogfooding) and plan 41-06 (SC#4's milestone-invariant sweep) can proceed independently.
- Both built PDFs remain at `/tmp/p41-main-out/typsphinx.pdf` and `/tmp/p41-head-out/typsphinx.pdf`
  for the remainder of the phase, in case plan 41-07's handoff needs to reference them -- neither
  is committed, and `git ls-files '*.pdf'` remains unaffected.
- No blocker for downstream plans. The working clone and second worktree used by this plan are
  fully cleaned up; `git status --short` in this worktree shows only the intentionally-untracked
  `docs/locale/` directory (per D-17's "leave it untracked in both trees" instruction), which is
  not part of this plan's `files_modified` and requires no action.

---
*Phase: 41-v0-7-0-release-automation-release-prep*
*Completed: 2026-08-03*

## Self-Check: PASSED

- FOUND: `.planning/phases/41-v0-7-0-release-automation-release-prep/41-JA-GLYPH-BAR.md`
- FOUND: `.planning/phases/41-v0-7-0-release-automation-release-prep/41-JA-GLYPHBAR-SIGNOFF.md`
- FOUND: `.planning/phases/41-v0-7-0-release-automation-release-prep/41-04-SUMMARY.md`
- CONFIRMED ABSENT: `.planning/phases/41-v0-7-0-release-automation-release-prep/translations-repo/`
- CONFIRMED ABSENT: `/tmp/p41-main-tree` from `git worktree list`
- CONFIRMED EMPTY: `git ls-files '*.pdf'`
- FOUND commit `e1a47af` (Task 2: checks 1-3 evidence)
- FOUND commit `2996429` (Task 4: owner sign-off + cleanup)
- FOUND commit `ae2d69e` (this SUMMARY.md)
