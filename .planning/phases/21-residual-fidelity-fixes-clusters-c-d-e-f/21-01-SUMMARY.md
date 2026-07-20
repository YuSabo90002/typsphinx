---
phase: 21-residual-fidelity-fixes-clusters-c-d-e-f
plan: 01
subsystem: rendering
tags: [typst, translator, uax14, line-breaking, codly, markup-mode, escaping]

# Dependency graph
requires:
  - phase: 20-rendering-fidelity-round-2
    provides: proven "code-mode whitespace is cosmetic / markup-mode newline is not" invariants this plan's Pitfall-3/D-Disc-2 reasoning builds on
provides:
  - "visit_literal: conditional leading-ZWSP break opportunity for colon-leading inline literal tokens (FID-10)"
  - "visit_literal_block: markup-aware '#{' list-item wrapper opening brace for captioned+list-item code blocks (FID-12)"
affects: [21-02, 21-03]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Conditional (character-class-gated) zero-width-space break-opportunity insertion, sibling to the existing self.in_table ZWSP primitive"
    - "Markup-mode-aware wrapper-prefix ('#{' vs '{') keyed to whether the immediately-preceding emission just opened Typst markup mode"

key-files:
  created:
    - tests/fixtures/inline_literal_overflow_render_gate/conf.py
    - tests/fixtures/inline_literal_overflow_render_gate/index.rst
    - tests/test_inline_literal_overflow_render_gate.py
    - tests/fixtures/codly_caption_listitem_leak_render_gate/conf.py
    - tests/fixtures/codly_caption_listitem_leak_render_gate/index.rst
    - tests/test_codly_caption_listitem_leak_render_gate.py
  modified:
    - typsphinx/translator.py

key-decisions:
  - "FID-10 A1 resolved: the conditional predicate code_content[0] in ':;,)]}!?' was verified against a real -b typstpdf compile of the :cpp:*: repro (structural ZWSP assert + pypdf content-loss assert both pass) and grep -rn 'raw(\"' tests/*.py confirms all 45 existing exact-match assertions (44 pre-existing + this plan's own needle-construction line) stay byte-unchanged -- none start a literal with a character in the gated class."
  - "Discovered empirically (not anticipated in RESEARCH.md/PATTERNS.md): once a raw() token carries the leading ZWSP fix, Typst's own line-breaking layout ALSO embeds additional invisible U+200B markers at internal UAX14 break-class boundaries within that same token when exporting PDF text (confirmed the .typ source itself contains exactly one leading ZWSP per token; the extra markers are a PDF-export-time artifact of Typst's line-breaker, not a translator bug). The pypdf content-loss adjacency test strips U+200B before the substring comparison to avoid a false content-loss signal from these invisible markers."
  - "FID-12: left the existing in_markup_context/codly_prefix predicate at ~1582-1587 completely unchanged per RESEARCH.md D-Disc-2 -- it was already correct; the bug was isolated to the list-item wrapper's own opening brace a few lines above it."

patterns-established:
  - "When a NEW markup/code-mode boundary bug is found adjacent to an EXISTING correct mode-conditional predicate in the same handler, apply the same conditional-prefix shape to the buggy statement rather than touching the correct one."

requirements-completed: [FID-10, FID-12]

coverage:
  - id: D1
    description: "A long run of colon-leading inline literal role tokens (:cpp:any: :cpp:class: ...) emits a leading-ZWSP raw() in the non-in_table branch of visit_literal, wraps at token boundaries in a real typst.compile(), and leaves no content loss (FID-10)"
    requirement: "FID-10"
    verification:
      - kind: integration
        ref: "tests/test_inline_literal_overflow_render_gate.py#TestInlineLiteralOverflowRenderGate::test_typstpdf_inline_literal_overflow_produces_pdf_with_leading_zwsp"
        status: pass
      - kind: integration
        ref: "tests/test_inline_literal_overflow_render_gate.py#TestInlineLiteralOverflowRenderGate::test_pdf_extracted_text_has_no_content_loss"
        status: pass
      - kind: unit
        ref: "tests/test_translator.py (full suite, all raw(\"...\") exact-match assertions)"
        status: pass
      - kind: unit
        ref: "tests/test_inline_references.py (full suite)"
        status: pass
    human_judgment: false
  - id: D2
    description: "A captioned code block nested in a list item opens its wrapper as '#{' and executes its codly config instead of leaking it as visible prose, while the pre-existing (differently-scoped) codly gate stays unaffected (FID-12)"
    requirement: "FID-12"
    verification:
      - kind: integration
        ref: "tests/test_codly_caption_listitem_leak_render_gate.py#TestCodlyCaptionListitemLeakRenderGate::test_typstpdf_captioned_listitem_wrapper_opens_with_hash"
        status: pass
      - kind: integration
        ref: "tests/test_codly_caption_listitem_leak_render_gate.py#TestCodlyCaptionListitemLeakRenderGate::test_pdf_extracted_text_has_no_leaked_codly_config"
        status: pass
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestCodlyConfigLeakRenderGate (full class, regression)"
        status: pass
    human_judgment: false

# Metrics
duration: 13min
completed: 2026-07-20
status: complete
---

# Phase 21 Plan 01: FID-10 conditional-ZWSP wrapping + FID-12 markup-aware wrapper brace Summary

**Two isolated translator.py fixes ship real-compile GATE-01 evidence: a UAX14-aware leading zero-width space lets Typst wrap long colon-leading inline-literal runs at token boundaries (FID-10), and a markup-mode-aware `#{` list-item wrapper opening brace stops a captioned code block's codly config from leaking as visible prose (FID-12).**

## Performance

- **Duration:** 13 min
- **Started:** 2026-07-20T13:16:58Z (approx, first commit 22:16:58 +0900)
- **Completed:** 2026-07-20T13:29:46Z (approx, last commit 22:29:46 +0900)
- **Tasks:** 2
- **Files modified:** 1 (`typsphinx/translator.py`), 6 files created (2 fixture pairs + 2 test modules)

## Accomplishments
- FID-10: `visit_literal`'s non-`in_table` branch gained a new, independent `elif` sibling that prepends a zero-width space (U+200B) to a literal's `raw()` content when the literal's first character is in the narrow UAX14 no-break-before class `":;,)]}!?"`, giving Typst's line-breaker an explicit break opportunity before a colon-leading token that rule LB13 would otherwise suppress even after a real, breakable space. The existing `self.in_table` ZWSP primitive (`.`/`_` splitting) stays byte-unchanged and completely isolated (D-05).
- FID-12: `visit_literal_block`'s list-item `{ }` wrapper opening brace now carries a leading `#` iff the block is both captioned AND in a list item, re-entering Typst code mode from inside the captioned figure's markup content so the per-block `codly(...)` config call executes instead of leaking as literal prose. The existing `in_markup_context`/`codly_prefix` predicate immediately below it (already correct) is unchanged.
- Both fixes ship a Shape-B GATE-01 render-gate module (real `sphinx-build -b typstpdf` compile + pypdf extracted-text adjacency assert) that FAILS against the pre-fix translator and produces a valid `%PDF`.
- A1 (FID-10's conditional-predicate blast radius) is resolved with an explicit real-compile verification: the 45 `raw("` matches across `tests/*.py` (44 pre-existing exact-match assertions + this plan's own needle-construction line) were reviewed and confirmed byte-unaffected — none of the existing literal strings (`"code"`, `"make.bat"`, `"em"`, etc.) start with a character in the gated class.

## Task Commits

Each task was committed atomically:

1. **Task 1: FID-10 — conditional leading ZWSP in visit_literal (margin overflow) + render gate** - `982a13d` (fix)
2. **Task 2: FID-12 — markup-aware list-item wrapper opening brace in visit_literal_block (codly leak) + render gate** - `0e41a77` (fix)

_Note: both tasks were TDD (RED confirmed via a failing structural assert against the pre-fix translator, then GREEN via the minimal targeted translator.py edit) but committed as a single `fix` commit per task rather than separate test/feat commits, since the fixture + test + implementation are one indivisible unit of work per the plan's task boundaries._

## Files Created/Modified
- `typsphinx/translator.py` - `visit_literal` gained the FID-10 `elif` sibling branch (conditional leading ZWSP); `visit_literal_block` gained the FID-12 conditional `#` prefix on the list-item wrapper's opening brace
- `tests/fixtures/inline_literal_overflow_render_gate/conf.py` - minimal Sphinx fixture project (master `typst_documents`)
- `tests/fixtures/inline_literal_overflow_render_gate/index.rst` - a long run of colon-leading double-backtick inline-literal role tokens (`:cpp:any:` ... `:cpp:var:`), mirroring the audit's `usage/domains/cpp` p.85 repro
- `tests/test_inline_literal_overflow_render_gate.py` - Shape-B render-gate module (structural `.typ` ZWSP assert + pypdf no-content-loss adjacency assert) for FID-10
- `tests/fixtures/codly_caption_listitem_leak_render_gate/conf.py` - minimal Sphinx fixture project
- `tests/fixtures/codly_caption_listitem_leak_render_gate/index.rst` - a numbered list whose second item contains a captioned `.. code-block::`, mirroring the audit's `extdev/i18n` p.232 repro
- `tests/test_codly_caption_listitem_leak_render_gate.py` - Shape-B render-gate module (structural `#{` wrapper assert + pypdf leak-absence adjacency assert) for FID-12

## Decisions Made
- **A1 resolution (FID-10):** kept the conditional (narrow character-class) predicate rather than escalating to an unconditional-always fallback — it exactly targets the corpus repro (every `:cpp:xxx:` token starts with `:`) with zero blast radius on existing exact-match assertions, real-compile-verified.
- **pypdf ZWSP-stripping (empirical, unplanned):** the FID-10 pypdf content-loss test strips U+200B from extracted text before comparison, because Typst's own line-breaking layout embeds additional invisible ZWSP markers at internal UAX14 break-class boundaries within a now-breakable `raw()` run when exporting to PDF (confirmed via direct `.typ`-source inspection that exactly one leading ZWSP is emitted per token at the source level — the extra markers are a PDF-export-time Typst behavior, not a translator defect). This is a Rule-1-adjacent test-correctness fix scoped entirely to the new test file; it does not touch `typsphinx/translator.py`.
- **FID-12 wrapper-prefix predicate:** matched exactly `self.in_captioned_code_block and self.code_block_caption` (identical condition to `in_markup_context` minus the `not self.in_list_item` clause), keeping the two predicates symmetric and easy to reason about together.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] pypdf content-loss test needed ZWSP-stripping to avoid a false content-loss failure**
- **Found during:** Task 1 (FID-10 GREEN verification)
- **Issue:** After applying the FID-10 fix, the pypdf extracted-text adjacency test initially failed: the extracted PDF text contained additional U+200B characters interspersed *within* each colon-leading token (e.g. a U+200B marker appearing before each internal colon of ":cpp:any:", not just the leading one), not just the single leading ZWSP the translator emits. Direct inspection of the emitted `.typ` source confirmed only one leading ZWSP per `raw()` call — the extra markers are inserted by Typst's own line-breaking/PDF-export layer once a token becomes breakable, not by the translator. A naive exact-substring content check (`":cpp:any:" in full_text`) would have failed even though no visible content was lost.
- **Fix:** Strip `chr(0x200B)` from the extracted PDF text before the substring comparison in `test_pdf_extracted_text_has_no_content_loss`, with an explanatory docstring note. `typsphinx/translator.py` was NOT changed for this — the fix is confined entirely to the test module.
- **Files modified:** `tests/test_inline_literal_overflow_render_gate.py`
- **Verification:** Re-ran the full test module after the strip — both tests pass; the structural `.typ`-level assert (the true fail-pre-fix gate) is unaffected by this change.
- **Committed in:** `982a13d` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 test-correctness bug, Rule 1)
**Impact on plan:** No scope creep — the fix is a test-only correctness adjustment discovered during the mandated A1 real-compile verification step; it does not alter the translator.py fix, the fixture, or any acceptance criterion. Both structural fail-pre-fix gates (the actual A1/D-06 proof points) were unaffected and confirmed correct in both directions before and after this adjustment.

## Issues Encountered
None beyond the deviation documented above.

## Verification Results

- `uv run pytest tests/test_inline_literal_overflow_render_gate.py tests/test_codly_caption_listitem_leak_render_gate.py -x` — 4 passed (both new GATE-01 gates green).
- `uv run pytest tests/test_translator.py tests/test_inline_references.py tests/test_pdf_render_gate.py` — 146 passed (no regression to existing `raw("...")` assertions or the existing codly gate, including `TestCodlyConfigLeakRenderGate`).
- `grep -rn 'raw("' tests/*.py` — 45 matches reviewed; the 44 pre-existing exact-match assertions confirmed byte-unaffected (A1). The 45th match is this plan's own `needle = 'raw("' + zwsp + ":cpp"` construction line, which builds the expected string in Python rather than asserting a fixed literal.
- `uv run pytest tests/test_preview_version_sync.py` — 2 passed (version-sync surface untouched; this plan does not edit `base.typ`).
- `uv run pytest -m "not slow" -q` (excluding the 4 pre-existing NixOS-sandbox-environmental integration-test files documented in project MEMORY.md, which fail via `subprocess.run(["uv","run","sphinx-build",...])` unrelated to this plan) — 430 passed, 23 deselected, 0 failed.
- `nix-shell -p ruff --run "ruff check ..."` and `uv run black --check ...` and `uv run mypy typsphinx/translator.py` — all clean (black reformatted two files during authoring; re-verified green after).
- Phase-gate `tests/test_corpus_gate.py -m slow` is deferred to end-of-phase per the plan's own instruction (run once, not per-plan) — not run in this plan.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- FID-10 and FID-12 are fully resolved and gated. Plans 21-02 and 21-03 (remaining Cluster C/D/E/F findings: FID-11, FID-13, FID-14) are independent of this plan's changes per the phase's wave/depends_on structure (`depends_on: []`) and can proceed without any handoff blockers.
- The milestone invariant (zero new runtime deps, no `@preview` bump, version-sync surface untouched, pypdf test-only) held throughout — verified via `tests/test_preview_version_sync.py` staying green and no `pyproject.toml`/dependency changes in this plan's diff.
- No blockers for the phase-level corpus gate (`tests/test_corpus_gate.py -m slow`), to be run once at phase completion per plan instructions.

---
*Phase: 21-residual-fidelity-fixes-clusters-c-d-e-f*
*Completed: 2026-07-20*
