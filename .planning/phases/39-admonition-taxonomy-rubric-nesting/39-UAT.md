---
status: diagnosed
phase: 39-admonition-taxonomy-rubric-nesting
source: [39-01-SUMMARY.md, 39-02-SUMMARY.md, 39-03-SUMMARY.md, 39-04-SUMMARY.md, 39-05-SUMMARY.md, 39-06-SUMMARY.md, 39-07-SUMMARY.md, 39-08-SUMMARY.md]
started: 2026-08-02T04:10:00Z
updated: 2026-08-02T04:45:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Admonition buckets and titles in a compiled PDF
expected: All ten types plus generic admonition and topic render as styled boxes in the four buckets with catalog titles; seealso/danger/attention sit in their new buckets; generic admonition carries its own title
result: issue
reported: "うわ、デンジャーはgentle-clueのデンジャーに振った方が良かったかも" / "Bでもっかい再構成しないとまずいな"
severity: major
scope: only the `danger` routing. The rest of test 1 (info/warning/success buckets, seealso's move, attention → error, todo → task, generic admonition → notify with its own title, topic → abstract, and all ten catalog titles) was rendered, shown, and raised no objection.
coverage_ids: [39-08/D5 (partial — SC#1..SC#3 half)]

### 2. Rubric indentation inside description bodies
expected: A rubric inside a class body sits at the same left edge as that body's text (not the page margin); a rubric inside a nested method body sits at the deeper body's edge; a top-level rubric stays at the margin; paragraphs after a rubric with inline bold keep normal paragraph spacing document-wide
result: pass
evidence: "Live render of a py:class / nested py:method fixture built with the current tree (sphinx -b typst → typst.compile, 150ppi). Class-body rubric left edge = class body text edge; nested method rubric = nested body edge; top-level rubric at margin; paragraphs after a bold rubric keep par() spacing across an intervening heading."
coverage_ids: [39-02/D1, 39-02/D3 (superseded — flipped GREEN by 39-06/D1, 39-06/D2)]

### 3. ADM-04 greyscale sign-off still stands
expected: The recorded owner verdict in 39-ADM04-SIGNOFF.md — "MET on icon-shape grounds, title-band luminance uniform and recorded as an explicit caveat" — is still the owner's position and is not being re-opened by this UAT
result: pass
evidence: "Owner re-confirmed the recorded verdict as valid for Phase 39 as-built. Note: the artifact itself is queued for a re-render + fresh sign-off under gap G-39-1, because the committed PNG shows `danger` inside the red `error` bucket, which G-39-1 reverses."
coverage_ids: [39-04/D4, 39-07/D2, 39-08/D5 (SC#4 half)]

<!--
Coverage auto-passed entries (#1602) — deterministically covered by passing tests
in their `verification` refs, NOT presented as checkpoints. 23 entries across 8 SUMMARYs:

39-01: D1 D2 D3 D4 D5      (all auto — RED-gate fixture + region-scoped gates)
39-02: D2                  (CONTROLs isolating D-13)
39-03: D1                  (ADM-05 invariance guard, 6 tests)
39-04: D1 D2 D3            (pillow dev-extra, one-page probe, greyscale pipeline)
39-05: D1 D2 D3 D4         (bucket re-routing + catalog titles, RED→GREEN)
39-06: D1 D2 D3 D4         (D-13 state-corruption fix, D-11 separator fix, strong/desc untouched)
39-07: D1                  (post-fix greyscale render, mode L, 1240x1754)
39-08: D1 D2 D3 D4         (census, corpus gate green, full suite 763/1/0, milestone invariants)
-->

## Summary

total: 3
passed: 2
issues: 1
pending: 0
skipped: 0
blocked: 0
auto_covered: 23

## Gaps

- gap_id: G-39-1
  truth: "`.. danger::` renders in gentle-clues' own `danger()` bucket (peach `#fe640b`, lightning icon), distinct from `error()`"
  status: failed
  reason: "User reported: 「うわ、デンジャーはgentle-clueのデンジャーに振った方が良かったかも」→ 「Bでもっかい再構成しないとまずいな」. Owner chose option B after being shown the live A/B/C render comparison and the ADM-02 / D-03 conflict below."
  severity: major
  test: 1
  root_cause: >
    Not a defect — a deliberate design decision the owner is now reversing.
    39-CONTEXT.md's D-03 ("`danger` folds into `error` too") collapsed
    `attention`, `danger` and `error` onto a single `error()` call so that
    ADM-02's phrase "the same bucket as `danger`/`error` (red)" would be
    well-defined. `typsphinx/translator.py:4517` (`visit_danger`) therefore
    calls `_visit_admonition(node, "error")`.
  measured_context:
    - "gentle-clues 1.3.1 theme.typ: `danger` accent `#fe640b` (peach) + `danger.svg` (lightning); `error` accent `#d20f39` (red) + `crossmark.svg`."
    - "Sphinx's own sphinx.sty:853-860 puts attention/danger/error in ONE colour bucket (`sphinx-error-title-*`, hsl(0,37%)) but gives each a DISTINCT icon (sphinx.sty:933-943 — attention `triangle-exclamation`, danger `radiation`, error `circle-xmark`). Option B diverges from Sphinx on colour; option C (rejected by owner) would have matched Sphinx on both axes."
    - "Live A/B/C render comparison produced during this UAT and shown to the owner."
  artifacts:
    - path: "typsphinx/translator.py"
      issue: "`visit_danger` (line 4517) routes to `_visit_admonition(node, \"error\")`; must route to `\"danger\"`"
    - path: ".planning/REQUIREMENTS.md"
      issue: "ADM-02's wording — \"`attention` renders in the same bucket as `danger`/`error` (red)\" — presupposes danger is red. Under B, danger is peach. The requirement's text must be restated (e.g. \"`attention` renders in the red `error` bucket, not the orange warning bucket\") or ADM-02 becomes self-contradictory."
    - path: ".planning/phases/39-admonition-taxonomy-rubric-nesting/39-CONTEXT.md"
      issue: "D-03 and the resulting bucket table (lines 78, 87) record the folded routing as the locked contract; both need a recorded reversal, not a silent edit."
    - path: "tests/test_admonition_bucket_render_gate.py"
      issue: "`test_danger_routes_to_error_bucket` asserts the old routing; also `test_control_buckets_never_move` and the base-clue-absence guard reference the folded set"
    - path: "tests/test_admonitions.py"
      issue: "`test_danger_converts_to_error` asserts `error(` for danger"
    - path: "tests/test_pdf_render_gate.py"
      issue: "`TestAdmonitionPdfRenderGate::test_admonitionbuckettitlegate` asserts danger's compiled-PDF bucket"
  missing:
    - "Route `visit_danger` to the `danger` clue function"
    - "Confirm the catalog title still wins over gentle-clues' own `danger` default (linguify would otherwise supply \"Danger\"/「危険」 — the `custom_title` path must keep overriding it, and the `ja` catalog value 「危険」 must still be what is emitted)"
    - "Restate ADM-02 so it no longer asserts danger is red; record the D-03 reversal in 39-CONTEXT.md"
    - "Migrate the danger-specific expected strings in the three test files above; re-run the full-corpus `-b typstpdf` gate"
    - "Re-render 39-ADM04-GREYSCALE.png from post-change code and re-take the ADM-04 sign-off — the greyscale artifact currently on record shows danger inside the red bucket"
