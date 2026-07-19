---
phase: 17-rendering-fidelity-audit
plan: 01
subsystem: docs
tags: [pypdf, sphinx-builders, corpus-gate, audit-tooling]

# Dependency graph
requires:
  - phase: 16-silent-drop-node-handlers
    provides: todo_node/manpage handlers landed, so the audit surfaces genuinely-silent divergence (empty unknown_visit catalogue confirmed fresh this session)
  - phase: 15-full-corpus-validation
    provides: tests/test_corpus_gate.py's corpus clone/cache + sphinx-build wiring helpers, reused unmodified
provides:
  - "17-AUDIT-CATALOGUE.md skeleton: fresh provenance header, D-08 severity rubric, D-09 issue schema (empty), SC#3 out-of-scope classification, docname->page-range mapping (151 docnames), D-02 per-docname progress tracker (all not-yet-audited)"
  - "Corrected docname->page mapping algorithm (position-ordered interleaved walk) for any future re-derivation"
affects: [17-02-visual-pass, 17-03-visual-pass, 17-04-requirements-append, phase-18-fidelity-fixes]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Position-ordered interleaved heading/include walk for docname->page mapping (supersedes a naive count-then-partition approach for multi-toctree-group landing pages)"

key-files:
  created:
    - .planning/phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md
  modified: []

key-decisions:
  - "Corrected RESEARCH Pattern 2's mapping recipe: walk each .typ file's own text position-ordered (heading() and include() calls interleaved by character offset, not grouped-then-partitioned), because 5 of 151 docnames (index, usage/domains/index, development/html_themes/index, man/index, usage/extensions/index) have own headings genuinely interleaved between multiple toctree groups — verified by the mandated boundary spot-check catching a real misattribution."
  - "Represented the 5 non-contiguous docnames with multiple page-range fragments in one table row (marked with a note) rather than forcing an artificial single contiguous range — matches D-02's actual need (locate a docname's content) more accurately than the plan's literal 'one contiguous range' framing."
  - "All build/rasterization artifacts (PDF, per-docname .typ/.html/.txt, rasterized PNGs) kept in a session-scratch directory outside the repo; only the catalogue skeleton is committed."

patterns-established:
  - "Docname->page mapping via pypdf outline API + position-ordered #include()/heading() interleave walk (scratch script, not committed — reproducible from the methodology documented in the catalogue)."

requirements-completed: []  # AUD-01 is not yet complete — this plan only builds the infrastructure; the visual pass (17-02+) completes AUD-01.

coverage:
  - id: D1
    description: "17-AUDIT-CATALOGUE.md exists with a fresh (this-session) provenance header — corpus tag/SHA, PDF byte size (15,153,646, differs from Phase 15's stale 15,124,122), page count (684), and an empty unknown_visit catalogue"
    requirement: AUD-01
    verification:
      - kind: unit
        ref: "grep -q cc7c6f435ad37bb12264f8118c8461b230e6830c && grep -q 'NOT YET AUDITED' 17-AUDIT-CATALOGUE.md"
        status: pass
      - kind: unit
        ref: "tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow"
        status: pass
    human_judgment: false
  - id: D2
    description: "Docname->page-range mapping (151 docnames) is exact, monotonic/non-overlapping at the fragment level, and covers pages 16-684; boundary spot-checks confirm correct attribution"
    requirement: AUD-01
    verification:
      - kind: manual_procedural
        ref: "Rasterized and visually read pages 16, 313, 675, 48, 49 via pdftoppm + Read tool; confirmed heading text matches mapped docname for index/usage/configuration/examples/tutorial-end/usage-index/usage-markdown/usage-referencing (the 4-way adjacency edge case)"
        status: pass
    human_judgment: true
    rationale: "The spot-check was performed by Claude reading rasterized page images, not by an independent human (D-01a's human-confirmation requirement applies to the actual audit findings in Plan 17-02+, not this infra plan) — flagging for downstream awareness that the mapping's correctness rests on this session's visual spot-check, not a second independent reviewer."

# Metrics
duration: 13min
completed: 2026-07-19
status: complete
---

# Phase 17 Plan 01: Audit Infrastructure Summary

**Built the rendering-fidelity audit scaffold — three same-corpus baselines (typstpdf/html/text), a corrected exact docname-to-page mapping for all 151 docnames, and the committed `17-AUDIT-CATALOGUE.md` skeleton with fresh provenance, so Plan 17-02's page-by-page visual pass can start immediately.**

## Performance

- **Duration:** 13 min
- **Started:** 2026-07-19T03:07:23Z
- **Completed:** 2026-07-19T03:20:05Z
- **Tasks:** 3
- **Files modified:** 1 (created)

## Accomplishments
- Environment smoke-checked (`nix-shell -p poppler-utils` + `tests/test_corpus_gate.py::TestCorpusRenderGate -m slow` both green) — no outside-sandbox fallback needed this session.
- Built the `typstpdf`, `html`, and `text` baselines from the SAME cached `v9.1.0` corpus (SHA `cc7c6f435ad37bb12264f8118c8461b230e6830c`) via `tests/test_corpus_gate.py`'s helpers, unmodified. Fresh provenance captured: `index.pdf` = 15,153,646 bytes / 684 pages / empty `unknown_visit` catalogue (confirms Phase 16 landed).
- Derived and spot-checked an exact docname→page-range mapping for all 151 docnames using `pypdf`'s outline API combined with a **position-ordered** recursive walk of `#include()`/`heading()` calls — a correction to the naive count-then-partition approach after the mandated boundary spot-check caught a real misattribution.
- Created `.planning/phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md`: provenance header, D-08 severity rubric (verbatim), SC#3 out-of-scope classification (graphviz/inheritance_diagram pre-flagged), empty D-09 issue table, the full page mapping, and a 151-row D-02 progress tracker (all "🔲 NOT YET AUDITED").

## Task Commits

Tasks 1 and 2 produced no repo changes (all build/rasterization artifacts and the mapping derivation live in a session-scratch directory outside the repo, per the plan's prohibition on committing them) — no commit for those tasks.

1. **Task 3: Write the 17-AUDIT-CATALOGUE.md skeleton** - `00df8be` (docs)

**Plan metadata:** (this commit, following)

## Files Created/Modified
- `.planning/phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md` - Provenance header, severity rubric, out-of-scope classification, empty issue table, docname->page-range mapping (151 docnames), and the per-docname progress tracker.

## Decisions Made
- **Position-ordered mapping walk over count-then-partition.** RESEARCH Pattern 2's recipe ("first heading = start page, next docname's start − 1 = end page") implicitly assumes a docname's own headings are all textually contiguous before its first `#include()`. The mandated Pitfall-2 boundary spot-check caught a real violation: the master `index` docname's `doc/index.rst` has FOUR h2 sections ("Get started"/"User guide"/"Community guide"/"Reference guide"), each immediately followed by its own toctree — so `index`'s own headings are genuinely interleaved with four separate groups of child pages, not bunched at the start. A naive "count 5 own headings, take the first 5 outline entries" approach misattributed page 48's "User guide" heading (part of `index`'s own content) to `usage/index` instead. Fixed by walking each `.typ` file's own text position-ordered (heading/include calls sorted by character offset, recursing at the exact point an include() appears) — verified correct via 4 re-run spot-checks (corpus-start, mid-corpus, corpus-end, and the exact 4-way page-49 adjacency case).
- **Multi-fragment representation for 5 non-contiguous docnames** instead of forcing one misleading contiguous range. `index`, `usage/domains/index`, `development/html_themes/index`, `man/index`, and `usage/extensions/index` each have their own content split across 2+ separate page ranges (interleaved with their children's own subtrees). The catalogue lists each fragment explicitly rather than claiming e.g. `index` "spans pages 16-299" (which would be true only in the sense of first-to-last occurrence, not actual content coverage, and would overlap every doc nested inside it).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed the docname->page mapping algorithm's misattribution for multi-toctree-group landing pages**
- **Found during:** Task 2 (mapping derivation + mandated boundary spot-check)
- **Issue:** The first implementation of RESEARCH Pattern 2 ("count a docname's own headings, then take a contiguous slice of the flat pypdf outline in DFS order") silently misattributed headings whenever a docname's own headings were not all contiguous before its first `#include()` call. Confirmed via the required page-49 spot-check: page 48's "13.1 User guide" heading — genuinely part of the `index` docname's own content — was assigned to `usage/index` instead, and the whole mapping downstream of that point was shifted by one heading per affected docname.
- **Fix:** Rewrote the mapping walk to be **position-ordered**: within each `.typ` file, `heading(` and `include(` call sites are located by character offset and processed in that literal order (interleaved), recursing into an included child file at the exact point its `include()` appears — this matches Typst's actual sequential rendering order regardless of whether a docname's own headings are contiguous.
- **Files modified:** None in the repo (scratch-only helper script; the corrected methodology and its evidence are documented in `17-AUDIT-CATALOGUE.md`'s "Mapping Methodology" section).
- **Verification:** Re-ran all 4 mandated spot-checks (corpus-start `index` p.16, mid-corpus `usage/configuration` p.313, corpus-end `examples` p.675, and the `index`/`usage/index`/`usage/markdown`/`usage/referencing` 4-way page-49 adjacency edge case) by rasterizing each page and reading it via the `Read` tool — all 4 confirmed the corrected mapping's heading titles exactly match the rendered page content.
- **Committed in:** `00df8be` (Task 3 commit — the corrected methodology is what's documented; the buggy intermediate version was never committed).

---

**Total deviations:** 1 auto-fixed (1 bug fix, caught by the plan's own mandated verification step).
**Impact on plan:** The fix is exactly what RESEARCH Pitfall 2 anticipated ("assuming heading-encounter order always exactly matches #include() order without cross-checking") and the plan's spot-check requirement existed precisely to catch it. No scope creep — same deliverable, corrected algorithm.

## Issues Encountered
None beyond the mapping algorithm bug documented above (caught and fixed within Task 2, before finalizing the catalogue).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 17-02 (the page-by-page visual pass) can start immediately: for any of the 151 docnames it can look up an exact PDF page range (or fragment set, for the 5 multi-toctree-group landing pages) from `17-AUDIT-CATALOGUE.md`, open the corresponding `-b html` baseline, and record findings directly into the schema-correct D-09 issue table.
- No blockers. The environment (nix-shell + real `typst.compile()`) is confirmed working in this session; a future session should re-run the smoke check per RESEARCH's guidance since sandbox state is session-dependent.
- The `-b text` pre-filter baseline is available in the same session-scratch directory as an optional triage aid for Plan 17-02, per RESEARCH Pattern 3 (fully optional, never a substitute for the mandatory visual pass).

---
*Phase: 17-rendering-fidelity-audit*
*Completed: 2026-07-19*

## Self-Check: PASSED

- FOUND: `.planning/phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md`
- FOUND: `.planning/phases/17-rendering-fidelity-audit/17-01-SUMMARY.md`
- FOUND commit: `00df8be` (catalogue skeleton)
- FOUND commit: `3765954` (this summary)
