---
phase: 17-rendering-fidelity-audit
plan: 02
subsystem: docs
tags: [typst, pdf, sphinx, rendering-fidelity, visual-audit, translator]

# Dependency graph
requires:
  - phase: 17-rendering-fidelity-audit
    provides: "Plan 17-01's docname→page-range mapping, progress tracker scaffold, and D-09 candidate-issue schema"
provides:
  - "Complete visual audit of all 151 docnames in the sphinx-doc/sphinx v9.1.0 corpus, cross-checked page-by-page against the -b html authority baseline"
  - "Populated, out-of-scope-filtered, severity-assigned, deterministically-ordered candidate issue catalogue (15 systemic findings F1-F15) in 17-AUDIT-CATALOGUE.md"
affects: [17-rendering-fidelity-audit, 18-rendering-fidelity-fixes]

# Tech tracking
tech-stack:
  added: []
  patterns: ["visual-audit-via-rasterize-and-read (pdftoppm + Read tool, no OCR/pypdf text extraction as substitute for a look)"]

key-files:
  created: []
  modified:
    - .planning/phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md
    - .planning/STATE.md

key-decisions:
  - "F1-F15 finding identifiers kept stable across the Task 2 re-sort; only row POSITION changed (sorted by PDF page = docname/toctree order), not the F-number labels, since those labels are referenced throughout the tracker's per-docname annotations"
  - "Out-of-scope sightings (graphviz/inheritance_diagram degrade placeholders) were never promoted into the Issue Table during Task 1 — they were recorded inline on the affected docname's tracker row at observation time — so Task 2's 'Excluded' subsection documents 5 confirmed sightings for auditability rather than moving rows out of the active table"
  - "F8 (external hyperlink flattened to plain text) extended with two new symptom variants this session: a stray space before the FOLLOWING WORD (not just before a period, changes/1.6 p.606) and a case with no visible artifact at all when the flattened link is immediately followed by a block boundary (examples p.678) — confirming the root cause is link-boundary space handling, not period-adjacency"
  - "Fixed a pre-existing markdown formatting defect in the Issue Table: rows 11-15 had spurious blank lines between them that would fragment the GFM table into separate tables under strict parsers; removed during the Task 2 re-sort rewrite"

requirements-completed: [AUD-01]

coverage:
  - id: D1
    description: "Every docname in the corpus toctree closure (151/151) visually reviewed page-by-page against the -b html authority baseline; zero '🔲 NOT YET AUDITED' progress-tracker rows remain"
    requirement: AUD-01
    verification:
      - kind: other
        ref: "grep -c 'NOT YET AUDITED' 17-AUDIT-CATALOGUE.md == 1 (the sole remaining match is the legend line defining the token, not a tracker row); grep -c '^| \\`.*\\` | .*AUDITED' == 151"
        status: pass
    human_judgment: false
  - id: D2
    description: "Candidate issue rows carry full D-09 schema fields (docname, node kind, description, severity, page, occurrence count, repro, uncertain flag); no out-of-scope signature in the active table; deterministic (docname/page) ordering"
    requirement: AUD-01
    verification:
      - kind: other
        ref: "python sweep restricted to the Issue Table span: 0/15 rows match inheritance.diagram|graphviz|py:meth; severity tally 1 high/12 medium/2 low (all exactly one of the three); PDF-page column strictly ascending across the 15 reordered rows (50,55,70,71,72,74,85,109,142,204,232,239,300,343,408)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every candidate row (and the finding catalogue as a whole) is ready for human accept/reject + severity confirmation at the Plan 17-03 gate"
    human_judgment: true
    rationale: "Whether each of the 15 systemic findings is truly worth fixing (vs. acceptable print-vs-web divergence) is a product/quality judgment call reserved for the human confirmation gate in Plan 17-03, not something this executor can auto-pass."

# Metrics
duration: ~25min (this session; continuation of a multi-session plan started earlier in Phase 17)
completed: 2026-07-19
status: complete
---

# Phase 17 Plan 02: Visual Rendering-Fidelity Audit Summary

**Full 151/151-docname visual audit of the sphinx-doc/sphinx v9.1.0 corpus PDF vs. its `-b html` baseline complete, yielding 15 classified systemic findings (1 high / 12 medium / 2 low severity) ready for the Plan 17-03 human confirmation gate.**

## Performance

- **Duration:** ~25 min this session (continuation; total Plan 17-02 spanned multiple sessions per D-02 resumability design)
- **Started (this session):** resumed at docname 133/151 (`changes/1.7`, PDF p.596)
- **Completed:** 2026-07-19T11:26Z
- **Tasks:** 2 (Task 1: per-docname visual pass — finished this session; Task 2: classify/finalize/re-sort — this session)
- **Files modified:** 2 (`17-AUDIT-CATALOGUE.md`, `STATE.md`)

## Accomplishments

- Audited the final 18 docnames this session — 17 `changes/*` release-note pages (`1.7` down through `0.1`) plus `examples` (the corpus's last docname) — reaching **151/151 docnames visually reviewed**, zero docnames left "NOT YET AUDITED"
- Extended finding **F8** (external hyperlink flattened to plain text) with two new confirmed symptom variants: a stray space before the following *word* (not just a period) at `changes/1.6` p.606, and a case with no visible spacing artifact when the flattened link is immediately followed by a block boundary at `examples` p.678 — both consistent with F8's existing root-cause hypothesis, no new finding kind
- No new finding *kinds* (F16+) surfaced in this session's ~90-page changelog/examples pass — changelogs are dense definition/bullet lists that reliably reproduce only F1/F9-class paragraph/line-break issues, and none of those recurred visibly in this session's material (all 17 changelog docnames + `examples` came back clean except the two F8 recurrences)
- Ran **Task 2** (classification + severity finalization + deterministic re-sort): swept all 15 active candidate rows against the REQUIREMENTS.md Out-of-Scope table (SC#3) — confirmed zero active rows reference `graphviz`, `inheritance_diagram`, or `py:meth`/autodoc-import signatures; confirmed every active row carries an exact `high`/`medium`/`low` severity (tally: 1 high, 12 medium, 2 low); re-sorted rows deterministically by (docname/toctree order ≡ ascending PDF page)
- Added an **"Excluded (out-of-scope)"** subsection documenting 5 confirmed out-of-scope sightings (graphviz/inheritance_diagram degrade placeholders) observed inline during the audit but never promoted into the active Issue Table, for auditability per SC#3's "never silent" requirement
- Fixed a latent markdown-table defect discovered while re-sorting: findings F11–F15 had stray blank lines between table rows (likely from earlier incremental edits) that would fragment a strict GFM table parser into multiple sub-tables; the re-sort rewrite produced one contiguous 16-row table (header + 15 findings)

## Task Commits

Each per-docname batch and the Task 2 finalization were committed atomically (this session):

1. `145bcb9` — audit progress: 135/151 docnames; +F8 recurrence (`changes/1.6`); `changes/1.7,1.6,1.5` clean (docs)
2. `0547c85` — audit progress: 137/151 docnames; `changes/1.4,1.3` clean (docs)
3. `56a4e13` — audit progress: 140/151 docnames; `changes/1.2,1.1,1.0` clean (docs)
4. `ba7763c` — audit progress: 142/151 docnames; `changes/0.6,0.5` clean (docs)
5. `55af076` — audit progress: 146/151 docnames; `changes/0.4,0.3,0.2,0.1` clean — all changelogs done (docs)
6. `9920265` — audit progress: 151/151 docnames; visual pass COMPLETE (+F8 recurrences, `examples` pp.675,678) (docs)
7. `fd459b6` — Task 2 complete: classify out-of-scope, finalize severity, deterministic re-sort (docs)

**Plan metadata:** (this commit) `docs(17-02): visual audit complete — 151/151 docnames; Task 2 done; candidate catalogue finalized`

_Note: earlier-session commits for docnames 1–132 are recorded in prior git history and in the STATE.md session log; this SUMMARY covers the plan's completion, not every commit across all sessions._

## Files Created/Modified

- `.planning/phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md` — the D-07 deliverable: progress tracker (151/151 rows audited), Issue Table (15 systemic findings F1-F15, D-09 schema, re-sorted deterministically), new "Excluded (out-of-scope)" subsection, updated status header
- `.planning/STATE.md` — position/status updated to reflect Plan 17-02 completion and the next step (Plan 17-03 human confirmation gate)

## Decisions Made

- Kept F1-F15 identifiers stable through the Task 2 re-sort (only row *position* changed to reflect ascending PDF-page/docname order; the F-number labels stayed attached to their original content) because those labels are referenced by name throughout the progress tracker's per-docname annotations (e.g. "F13 recurs", "+F9"), and renumbering would have broken every cross-reference
- Treated the 5 graphviz/inheritance_diagram sightings recorded inline on tracker rows during Task 1 as already-excluded (never promoted to the Issue Table) rather than artificially adding them as rows just to remove them in Task 2 — the "Excluded" subsection instead documents these sightings directly for auditability, satisfying SC#3's "never silent" requirement without introducing meaningless churn
- Classified the `examples` p.678 flattened-link sighting (no visible stray-space artifact) as an F8 recurrence rather than a new finding, since the underlying node kind and root cause (external `reference` rendered as plain text, losing link styling) are identical to F8's existing description — the absence of a stray-space symptom in this instance is explained by F8's own text as a corpus content property (nothing textually adjacent), not a different defect

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed a markdown-table-breaking formatting defect in the Issue Table**
- **Found during:** Task 2 (deterministic re-sort)
- **Issue:** Findings F11 through F15 in the Issue Table had spurious blank lines separating them from adjacent rows (inconsistent with F1-F10, which had no such gaps) — a strict GFM table parser treats a blank line as terminating the table, which would have silently fragmented the 15-row Issue Table into multiple disconnected sub-tables when rendered
- **Fix:** Rewrote the table block via a precise line-reordering script that both re-sorted rows into deterministic (docname/page) order AND collapsed all rows into one contiguous block with no interior blank lines
- **Files modified:** `.planning/phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md`
- **Verification:** Re-read the rewritten table section (lines 82-98); confirmed all 15 rows plus header/separator are contiguous with a single blank line only *after* the table, before the next `##` heading
- **Committed in:** `fd459b6` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix, Rule 1)
**Impact on plan:** The formatting fix was necessary for the catalogue to render as a single coherent table for Phase 18's planner to consume; no scope creep — it was discovered and fixed as a direct consequence of the Task 2 re-sort work already required by the plan.

## Issues Encountered

- The plan's own Task 2 automated verify script (`t.split('Excluded')[0]` then grep for out-of-scope signatures) produces a **false positive** when run against the full file: it inadvertently scans the pre-existing "Out-of-Scope Classification (SC#3)" reference table near the top of the file (which legitimately *names* `graphviz`/`inheritance_diagram`/`py:meth` as concepts being pre-classified, not as active candidate rows), because that section predates the word "Excluded" in the document. Verified correctness by re-running an equivalent sweep restricted to the actual Issue Table span (`| # | Docname | Node Kind |` through `## Excluded`), which returns 0 matches as required. This is a scope artifact of the plan's inline verify one-liner, not a defect in the catalogue; documenting here so a future re-run of the literal script isn't mistaken for a regression.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The candidate issue catalogue (`17-AUDIT-CATALOGUE.md`) is complete, classified, severity-tagged, and deterministically ordered — ready for **Plan 17-03**, the human confirmation gate, where each of the 15 findings gets accept/reject and final severity sign-off.
- High-severity finding for Plan 17-04 prioritization: **F12** (`extdev/deprecated`, wide-table column collision + right-margin clip, pp.239-241) — the only `high`-severity finding; large portions of a multi-page reference table are rendered unreadable due to inter-column glyph collision.
- Medium-severity findings likely to have the broadest corpus-wide blast radius for a Phase 18 fix backlog: **F1** (paragraph-in-list-item concatenation, translator.py `visit_paragraph`/`depart_paragraph` root cause already identified), **F2**/**F3** (missing inter-token spaces in Python/C/C++ domain signatures), **F7** (multi-signature/option concatenation), **F9** (semantic-line-break hard-wrapping), and **F13** (rubric/option-heading concatenation, ~10 occurrences in one docname alone).
- No blockers for Plan 17-03.

---
*Phase: 17-rendering-fidelity-audit*
*Completed: 2026-07-19*

## Self-Check: PASSED

- FOUND: `.planning/phases/17-rendering-fidelity-audit/17-02-SUMMARY.md`
- FOUND commits: `145bcb9`, `0547c85`, `56a4e13`, `ba7763c`, `55af076`, `9920265`, `fd459b6`
