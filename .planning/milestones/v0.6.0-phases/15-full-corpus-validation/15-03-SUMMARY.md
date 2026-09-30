---
phase: 15-full-corpus-validation
plan: 03
subsystem: validation
tags: [gate-02, corpus, measurement, report]
key-files:
  created:
    - .planning/phases/15-full-corpus-validation/15-CORPUS-REPORT.md
metrics:
  sc1_pdf_bytes: 15124122
  sc2_unknown_visit_total: 20
  sc3_empty_url_before: 1
  sc3_empty_url_after: 1
  sc3_empty_url_delta: 0
---

# Plan 15-03 Summary — Corpus Measurement Report (D-06)

## What was built

Ran the GATE-02 corpus measurements against the real Sphinx `doc/` corpus
(`v9.1.0`, clone SHA `cc7c6f435ad37bb12264f8118c8461b230e6830c`) and recorded
both results into the committed `15-CORPUS-REPORT.md` (D-06):

- **SC#1 (fatal-free compile):** `TestCorpusRenderGate` PASSED (not skipped —
  live network this session). `index.pdf` = 15,124,122 bytes (~14.4 MiB),
  `%PDF` magic present, `build succeeded, 66 warnings, 0 errors`, no
  `TypstCompilationError`.
- **SC#2 (`unknown_visit` catalogue):** `todo_node` ×10, `manpage` ×10 —
  recorded as the next milestone's node-handler backlog (the gate is "no fatal
  error," not "zero warnings").
- **SC#3 (empty-URL before/after, D-07):** before=1, after=1, delta=0, with an
  honest methodology note explaining (a) why the XREF-01 isolation used a
  HEAD-branched worktree (only `depart_term`'s anchor disabled) rather than the
  original `79c9d45~1` full checkout — the 55-commit campaign that followed
  would otherwise conflate the measurement — and (b) why delta=0 is expected
  (XREF-01 is a definition-side anchor fix, orthogonal to the reference-side
  empty-URL warning; the corpus has 1 genuinely-unresolvable residual reference
  in both builds).

## Task Commits

| Task | Description | Commit |
|------|-------------|--------|
| 1 | Run measurement + write 15-CORPUS-REPORT.md | `3816685` |
| 2 | Blocking human-verify checkpoint | operator approved 2026-07-13 |

## Deviations

- **D-07 measurement mechanism adjusted (documented in the report + 15-02-SUMMARY):**
  isolated XREF-01's `depart_term` anchor on top of HEAD instead of checking out
  `79c9d45~1`, because Phase 15's 25-bug campaign (55 commits after `79c9d45`)
  would otherwise conflate the XREF-01 delta with the whole campaign and predates
  the Phase 13–14 handlers. D-07's INTENT (quantify XREF-01's effect, corpus held
  constant) is preserved; the exact mechanism was Claude's Discretion per CONTEXT.
- **Measurement ran in-sandbox this session** (network was available and the corpus
  built for real), rather than the "outside sandbox" the plan assumed as a
  precaution — the numbers are real, not a `pytest.skip`.

## Self-Check: PASSED

- `15-CORPUS-REPORT.md` exists, committed (`3816685`), concrete integers, no placeholders
  (verified `grep -niE 'TBD|to be measured|placeholder|<count>|XXX'` → none).
- SC#2 catalogue table + SC#3 before/after table present with real counts; preamble
  records corpus tag + clone SHA.
- Blocking checkpoint approved by operator.
- `pytest -m "not slow"` (4 sandbox excludes) green: 427 passed.
- No `typsphinx/` source modified by this plan.
