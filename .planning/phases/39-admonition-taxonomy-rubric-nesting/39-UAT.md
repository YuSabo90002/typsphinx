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
  truth: >
    The red-family types stop being one collapsed function. `.. danger::` renders in
    gentle-clues' own `danger()` (peach `#fe640b` + `danger.svg` lightning);
    `.. attention::` renders in `memo()` (maroon `#e64553` + `excl.svg` exclamation);
    `.. error::` stays `error()` (red `#d20f39` + `crossmark.svg`). Three distinct
    clue functions where the phase shipped one.
  status: closed
  closed_at: 2026-08-02
  closed_by: [39-09, 39-10, 39-11, 39-12, 39-13]
  reason: >
    User reported: 「うわ、デンジャーはgentle-clueのデンジャーに振った方が良かったかも」
    → 「Bでもっかい再構成しないとまずいな」 → 「Attentionはgentle-cleuのmemoにすっか」.
    Owner chose option B for `danger` after being shown the live A/B/C render
    comparison and the ADM-02 / D-03 conflict, then extended it to `attention` →
    `memo()` after being shown Sphinx's own per-type icon assignment.
  severity: major
  test: 1
  root_cause: >
    Not a defect — a deliberate design decision the owner is now reversing.
    39-CONTEXT.md's D-03 ("`danger` folds into `error` too") collapsed
    `attention`, `danger` and `error` onto a single `error()` call so that
    ADM-02's phrase "the same bucket as `danger`/`error` (red)" would be
    well-defined. `typsphinx/translator.py:4517` (`visit_danger`) and `:4525`
    (`visit_attention`) therefore both call `_visit_admonition(node, "error")`.
    The owner's new taxonomy keeps all three in the red FAMILY but gives each its
    own clue function, which is what Sphinx itself does on the icon axis.
  measured_context:
    - "gentle-clues 1.3.1 lib/theme.typ: `danger` accent `#fe640b` (peach) + `danger.svg`; `error` accent `#d20f39` (red) + `crossmark.svg`; `memo` accent `#e64553` (maroon) + `excl.svg`. Verified by reading the installed package at ~/.cache/typst/packages/preview/gentle-clues/1.3.1."
    - "Rendered live during UAT: `memo`'s maroon title band is visually near-identical to `error`'s red band; the two separate almost entirely on icon shape (! vs ×). So attention stays in the red family — ADM-02's 'not the orange warning bucket' intent survives — while gaining a distinct glyph."
    - "Sphinx's own sphinx.sty:853-860 puts attention/danger/error in ONE colour bucket (`sphinx-error-title-*`, hsl(0,37%)) but sphinx.sty:933-943 gives each a DISTINCT icon (attention `triangle-exclamation`, danger `radiation`, error `circle-xmark`). The owner's taxonomy matches Sphinx on the icon axis and diverges on the colour axis (Sphinx: one red; owner: three red-family accents)."
    - "gentle-clues supplies its own linguify titles for these ids (`memo` = \"Memorize\" in en, no `ja` entry → falls back to en; `danger` = \"Danger\"/「危険」). The `custom_title` path from `sphinx.locale.admonitionlabels` must keep overriding all of them, or `.. attention::` would render as \"Memorize\"."
    - "CORRECTION (plan 39-09, confirmed in 39-CONTEXT.md's D-03-R section): the bullet directly above is wrong about `memo`'s Japanese entry. The installed `lang.toml` DOES carry `[lang.ja] memo = \"覚える\"` (line 168) — it does not fall back to `en`. This changes nothing functionally, since `custom_title` already overrides every predefined id's default title in both locales; see `39-GATE-EVIDENCE-05.md` for the measurement. The bullet above is left as originally written so this record shows what was believed at UAT time, not only what is true."
  artifacts:
    - path: "typsphinx/translator.py"
      issue: "`visit_danger` (line 4517) and `visit_attention` (line 4525) both route to `_visit_admonition(node, \"error\")`; must route to `\"danger\"` and `\"memo\"` respectively"
    - path: "typsphinx/writer.py:158, typsphinx/template_engine.py:615, typsphinx/templates/base.typ:19"
      issue: "CHECKED during UAT — all three import sites use the glob form `#import \"@preview/gentle-clues:1.3.1\": *`, so `memo` and `danger` are already in scope. No import change needed; no @preview version bump, so tests/test_preview_version_sync.py is unaffected."
    - path: ".planning/REQUIREMENTS.md"
      issue: "ADM-02's wording — \"`attention` renders in the same bucket as `danger`/`error` (red)\" — presupposes a single red bucket. Under the new taxonomy all three are distinct functions with distinct accents, so the requirement is self-contradictory as written. Restate it around the intent (attention leaves the orange warning bucket for the red family) rather than around function identity. ADM-01's preamble (\"four colour groups, not ten independent styles\") also needs a note that the red group is deliberately sub-divided."
    - path: ".planning/phases/39-admonition-taxonomy-rubric-nesting/39-CONTEXT.md"
      issue: "D-03 and the resulting bucket table (lines 78, 87) record the folded routing as the locked contract; both need a recorded reversal, not a silent edit."
    - path: "tests/test_admonition_bucket_render_gate.py"
      issue: "`test_danger_routes_to_error_bucket` and `test_attention_routes_to_error_bucket` assert the folded routing; `test_control_buckets_never_move` and `test_no_real_admonition_type_ever_uses_base_clue` reference the folded set; 39-05/D2's grep guard (`_visit_admonition([^)]*\"danger\"` returns 0) now inverts — it must assert exactly one danger call site, not zero"
    - path: "tests/test_admonitions.py"
      issue: "`test_danger_converts_to_error` and `test_attention_converts_to_error` assert `error(` for both types"
    - path: "tests/test_pdf_render_gate.py"
      issue: "`TestAdmonitionPdfRenderGate::test_admonitionbuckettitlegate` asserts danger's and attention's compiled-PDF bucket"
    - path: "tests/fixtures/admonition_greyscale_probe/"
      issue: "The one-page probe carries note/tip/seealso/warning/error/attention. With attention and danger now distinct, the probe should cover all three red-family types so the re-taken ADM-04 render actually evidences the new taxonomy. Watch the one-page constraint (39-RESEARCH.md Pitfall 4 — typst-py PNG export needs a page-number template above one page)."
  missing:
    - "Route `visit_danger` → `\"danger\"` and `visit_attention` → `\"memo\"`"
    - "Confirm the `sphinx.locale.admonitionlabels` `custom_title` path still wins over gentle-clues' own linguify defaults for BOTH new ids — otherwise `.. attention::` renders as \"Memorize\" (memo has no `ja` entry and falls back to en). The `ja` catalog values 「注意」/「危険」 must still be what is emitted."
    - "Restate ADM-02 (and note the red-group sub-division under ADM-01's preamble) so neither asserts a single collapsed red bucket; record the D-03 reversal in 39-CONTEXT.md"
    - "Migrate the danger/attention expected strings in the three test files above; invert 39-05/D2's zero-call-site grep guard; re-run the full-corpus `-b typstpdf` gate"
    - "Extend the greyscale probe fixture to cover attention/danger/error separately, re-render 39-ADM04-GREYSCALE.png from post-change code, and re-take the ADM-04 sign-off — the artifact currently on record shows all three folded into the red bucket. The new taxonomy is expected to IMPROVE the greyscale verdict (three distinct glyphs: ! / ⚡ / ×), which was the owner's original complaint."
