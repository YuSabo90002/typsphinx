---
phase: 39-admonition-taxonomy-rubric-nesting
plan: 09
subsystem: testing
tags: [pytest, sphinx-locale, gentle-clues, typst-compile, gate-01, gap-closure]

# Dependency graph
requires:
  - phase: 39-admonition-taxonomy-rubric-nesting (plans 01-08)
    provides: the shipped bucket-routing gate module and the D-04/D-05 catalog-title mechanism this plan extends and reuses
provides:
  - The recorded G-39-1 RED that the red family (danger/attention/error) is three
    pairwise-distinct gentle-clues functions, not one collapsed error() function
  - The generalized red-family invariant (membership + distinctness + title provenance
    in one build) preventing a future silent re-collapse
  - A new locale title precedence gate proving the Sphinx catalog title still beats
    gentle-clues' own linguify default for both new red-family function ids (danger, memo)
    in both English and Japanese catalogs
  - 39-GATE-EVIDENCE-05.md recording every RED verbatim against a named commit
affects: [39-11 (the plan that flips this RED green by re-routing visit_danger/visit_attention)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Region-scoped structural gates (_clue_open_before/_title_arg_after) reused across
       sibling test modules via pytest's default prepend import mode (no package marker
       under tests/)"
    - "sphinx.locale translator explicitly (re-)installed and restored per catalog read
       in a test process that never runs a real Sphinx Application"

key-files:
  created:
    - tests/test_admonition_locale_title_precedence_gate.py
    - tests/fixtures/admonition_locale_title_gate/en/conf.py
    - tests/fixtures/admonition_locale_title_gate/en/index.rst
    - tests/fixtures/admonition_locale_title_gate/ja/conf.py
    - tests/fixtures/admonition_locale_title_gate/ja/index.rst
    - .planning/phases/39-admonition-taxonomy-rubric-nesting/39-GATE-EVIDENCE-05.md
  modified:
    - tests/test_admonition_bucket_render_gate.py
    - tests/fixtures/admonition_render_gate/index.rst

key-decisions:
  - "memo added to _CLUE_FUNCTION_NAMES before any assertion was re-targeted, proven with a direct _CLUE_OPEN_RE interpreter check, so the region-scoping helper cannot silently resolve attention's sentinel to a neighbouring box"
  - "The two red-family DEFECT-CASE tests were renamed (not duplicated) to state the routing the project now reverses: test_danger_routes_to_error_bucket -> test_danger_routes_to_danger_function, test_attention_routes_to_error_bucket -> test_attention_routes_to_memo_function"
  - "The generalized invariant test resolves all three red-family sentinels from ONE build so a neighbour-resolution bug surfaces as a distinctness failure rather than passing silently, and also proves region-scope resolution stays stable with three equal-family boxes adjacent"
  - "The danger title assertion in the new locale gate asserts presence only, never value, because the Sphinx catalog and gentle-clues' own default agree on danger's title string in both locales -- a value assertion there would be a false witness for which source produced it"
  - "The [lang.ja] memo value was re-measured directly against the installed gentle-clues lang.toml this session: it DOES carry an explicit entry (\"覚える\"), confirming the plan's own measurement correction and contradicting 39-UAT.md's original measured_context bullet"
  - "sphinx.locale.init() leaks its installed translator process-wide (this test process never runs a real Sphinx Application), so _catalog_title() saves and restores the prior sphinx.locale.translators[(\"general\",\"sphinx\")] entry around each read -- discovered via full-suite regression before committing, not left for a later phase to find"

patterns-established:
  - "A red-family invariant test asserts membership + pairwise distinctness + title provenance together from a single build, rather than as separate point assertions, so a future silent re-collapse of a function family fails structurally instead of passing by omission"

requirements-completed: [ADM-02]

# Coverage metadata
coverage:
  - id: D1
    description: "Red family (danger/attention/error) asserted as three pairwise-distinct gentle-clues functions, RED against the shipped folded routing"
    requirement: "ADM-02"
    verification:
      - kind: unit
        ref: "tests/test_admonition_bucket_render_gate.py#test_attention_routes_to_memo_function"
        status: fail
      - kind: unit
        ref: "tests/test_admonition_bucket_render_gate.py#test_danger_routes_to_danger_function"
        status: fail
      - kind: unit
        ref: "tests/test_admonition_bucket_render_gate.py#test_red_family_types_route_to_distinct_clue_functions"
        status: fail
    human_judgment: false
  - id: D2
    description: "Region-scoping helper recognizes the memo box-open token (proven directly via interpreter check), and ADM-02's surviving intent (attention never in the warning bucket) is asserted positively"
    requirement: "ADM-02"
    verification:
      - kind: unit
        ref: "tests/test_admonition_bucket_render_gate.py#test_attention_is_not_in_the_warning_bucket"
        status: pass
      - kind: other
        ref: "python -c interpreter check: _CLUE_OPEN_RE.search('memo({') matches group 'memo'"
        status: pass
    human_judgment: false
  - id: D3
    description: "Catalog title precedence gated for both new red-family function ids (danger, memo) in both English and Japanese catalogs, RED on box-open, GREEN on title source"
    requirement: "ADM-02"
    verification:
      - kind: unit
        ref: "tests/test_admonition_locale_title_precedence_gate.py#test_attention_box_opens_with_memo_en"
        status: fail
      - kind: unit
        ref: "tests/test_admonition_locale_title_precedence_gate.py#test_danger_box_opens_with_danger_en"
        status: fail
      - kind: unit
        ref: "tests/test_admonition_locale_title_precedence_gate.py#test_attention_box_opens_with_memo_ja"
        status: fail
      - kind: unit
        ref: "tests/test_admonition_locale_title_precedence_gate.py#test_danger_box_opens_with_danger_ja"
        status: fail
      - kind: unit
        ref: "tests/test_admonition_locale_title_precedence_gate.py#test_attention_title_is_catalog_value_en"
        status: pass
      - kind: unit
        ref: "tests/test_admonition_locale_title_precedence_gate.py#test_danger_title_argument_is_present_en"
        status: pass
      - kind: e2e
        ref: "tests/test_admonition_locale_title_precedence_gate.py#test_attention_pdf_text_carries_catalog_title_not_package_default_en"
        status: pass
      - kind: unit
        ref: "tests/test_admonition_locale_title_precedence_gate.py#test_attention_title_is_catalog_value_ja"
        status: pass
      - kind: unit
        ref: "tests/test_admonition_locale_title_precedence_gate.py#test_package_default_titles_never_appear_in_emitted_source_ja"
        status: pass
    human_judgment: false
  - id: D4
    description: "The G-39-1 RED is recorded verbatim against a named, resolvable commit, with the lang.toml correction and theme.typ provenance attached, in 39-GATE-EVIDENCE-05.md"
    requirement: "ADM-02"
    verification:
      - kind: other
        ref: "test -s + grep for 40-char SHA + grep 'lang.toml' + git diff --stat -- typsphinx/ empty (all verified individually)"
        status: pass
    human_judgment: false

# Metrics
duration: ~55min
completed: 2026-08-02
status: complete
---

# Phase 39 Plan 09: Red-Family Taxonomy Sub-Division RED (G-39-1) Summary

**Recorded the G-39-1 RED: danger/attention/error asserted as three pairwise-distinct gentle-clues functions (danger/memo/error), with a generalized non-re-collapse invariant and a new locale title-precedence gate proving the catalog title still beats gentle-clues' own linguify default in both English and Japanese for the two newly-used function ids.**

## Performance

- **Duration:** ~55 min
- **Tasks:** 3
- **Files modified:** 8 (2 modified, 6 created)

## Accomplishments

- Extended `tests/test_admonition_bucket_render_gate.py`: added `memo` to the region-scoping
  helper's recognized function set (proven directly), renamed and re-targeted the two red-family
  DEFECT-CASE tests to expect `danger`/`memo` instead of the folded `error`, added the
  generalized `test_red_family_types_route_to_distinct_clue_functions` invariant (membership +
  distinctness + title provenance in one build), and added
  `test_attention_is_not_in_the_warning_bucket` stating ADM-02's surviving intent positively.
  RED today on the three red-family assertions; all seven CONTROL rows, the base-clue absence
  guard, the ten-row catalog-title table, and both `_clue_open_before` self-checks stay GREEN.
- Created `tests/test_admonition_locale_title_precedence_gate.py` and its two-locale
  `tests/fixtures/admonition_locale_title_gate/{en,ja}` fixture project: gates that the Sphinx
  catalog title argument still beats gentle-clues' own per-id default for both `danger` and
  `memo` in both catalogs. RED on all four box-open assertions (attention/danger x en/ja); GREEN
  on every title-source control, including the English compiled-PDF discriminating case. The
  Japanese half is proven at the emitted-source tier only — no CJK glyph is ever extracted from a
  compiled PDF anywhere in this module.
- Recorded `39-GATE-EVIDENCE-05.md`: gap statement, base commit `7272bd6`, verbatim pytest output
  for all four RED/CONTROL selectors, a RED/CONTROL inventory table for every test function added
  or renamed, the measured `lang.toml` `[lang.ja]` `memo` correction, the `theme.typ`
  accent/icon provenance for the red-family constant, and the empty `git diff --stat -- typsphinx/`
  proof that this plan touched zero translator source.

## Task Commits

1. **Task 1: Invert the red-family bucket assertions and add the generalized red-family invariant** - `29f4247` (test)
2. **Task 2: Gate the catalog title against gentle-clues' own defaults in both locales** - `791a4d5` (test)
3. **Task 3: Record the RED verbatim against a named commit** - `97537cb` (docs)

_No TDD RED/GREEN/REFACTOR cycle applies here — this is a GATE-01 RED-recording plan by design;
the GREEN flip is deliberately deferred to plan 39-11 (next wave)._

## Files Created/Modified

- `tests/test_admonition_bucket_render_gate.py` - added `memo` to `_CLUE_FUNCTION_NAMES`, renamed
  and re-targeted the two red-family point assertions, added the generalized invariant test and
  the "not in warning bucket" test, rewrote the module docstring's RED/CONTROL inventory for G-39-1
- `tests/fixtures/admonition_render_gate/index.rst` - corrected the danger/attention annotation
  comments (comment lines only; no directive, sentinel, or body text changed)
- `tests/test_admonition_locale_title_precedence_gate.py` - new locale title precedence gate
  module (9 tests)
- `tests/fixtures/admonition_locale_title_gate/en/conf.py`, `en/index.rst`, `ja/conf.py`,
  `ja/index.rst` - new two-locale fixture project (attention/danger/error, ASCII-only bodies)
- `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-GATE-EVIDENCE-05.md` - new gate
  evidence document

## Decisions Made

- **`memo` added to `_CLUE_FUNCTION_NAMES` first, before any assertion re-target**, and verified
  with a direct `_CLUE_OPEN_RE` interpreter check — the region-scoping helper resolves a
  sentinel's box by scanning backward for the nearest recognized open token, so an absent `memo`
  entry would have made the attention assertion silently resolve to a neighbouring box instead of
  raising or correctly matching.
- **Renamed, not duplicated**, the two red-family point assertions
  (`test_danger_routes_to_error_bucket` → `test_danger_routes_to_danger_function`,
  `test_attention_routes_to_error_bucket` → `test_attention_routes_to_memo_function`) — a test
  name stating a routing the project has reversed is stale documentation, per this phase's
  standing rename discipline (D-14).
- **The generalized invariant test resolves all three red-family sentinels from ONE build** —
  this is what makes a future silent re-collapse of the family fail rather than pass, and it also
  proves region-scope resolution stays stable when three equal-family boxes sit adjacent in the
  fixture (rather than proving distinctness across three separate, independently-built fixtures).
- **The danger title assertion in the locale gate asserts presence only, never a specific value**
  — the Sphinx catalog and gentle-clues' own default agree on danger's title string in both
  English and Japanese, so a value assertion there would pass regardless of which source produced
  it and would be a false witness for the precedence mechanism this gate exists to prove.
- **`lang.toml`'s `[lang.ja]` table was re-measured directly this session** rather than trusted
  from 39-UAT.md: it DOES carry an explicit `memo = "覚える"` entry — the 39-UAT.md bullet's "no
  `ja` entry → falls back to en" claim is wrong, and the plan's own `<planner_measurement_correction>`
  is confirmed. The Japanese negative guard (`test_package_default_titles_never_appear_in_emitted_source_ja`)
  therefore checks BOTH the English and Japanese gentle-clues memo defaults, not narrowed to English.
- **`sphinx.locale.init()` explicitly saves and restores the prior translator registry entry**
  around each catalog read in the new locale gate module. This test process never runs a real
  Sphinx `Application` (every build is a `sphinx-build` subprocess, which scopes its own
  translator to its own subprocess), so nothing else would have reset the global
  `sphinx.locale.translators` state between reads — discovered via a full-suite regression run
  (see Deviations below) and fixed before committing.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Test-isolation leak: `sphinx.locale.init("ja")` polluted alphabetically-later modules process-wide**

- **Found during:** Task 2, verifying the new locale gate module against the full suite
  (`uv run pytest -m "not slow" -q`)
- **Issue:** An early version of `_catalog_title()` called `sphinx.locale.init(..., "ja")` to
  resolve the Japanese catalog value inside the test process, but never restored the prior
  translator afterward. This test process never runs a real Sphinx `Application` (every fixture
  build in this module is a `sphinx-build` subprocess, which scopes its own translator to its own
  process) — so the Japanese translator installed by my helper leaked process-wide for the rest
  of the pytest session. `tests/test_admonitions.py`'s English title assertions
  (`test_important_converts_to_warning_with_title`, `test_seealso_converts_to_tip_with_title`,
  which run later alphabetically) started asserting Japanese strings and failed.
- **Fix:** `_catalog_title()` now saves `sphinx.locale.translators[("general", "sphinx")]`'s
  pre-call value and restores it in a `finally` block after each read, so no cross-module global
  state survives past a single catalog-title lookup.
- **Files modified:** `tests/test_admonition_locale_title_precedence_gate.py`
- **Verification:** Re-ran `uv run pytest -m "not slow" -q` after the fix — `739 passed, 7 failed`
  (exactly the 7 RED tests this plan intentionally records; the two previously-broken
  `test_admonitions.py` tests now pass again).
- **Committed in:** `791a4d5` (Task 2 commit — fixed before the commit was made, not as a
  follow-up)

---

**Total deviations:** 1 auto-fixed (Rule 1 — bug in my own new test code, not in the shipped
translator or in any pre-existing test)
**Impact on plan:** Necessary for correctness of the new module's isolation; no scope creep — the
fix is entirely contained inside the one new helper function this plan introduces.

## Issues Encountered

- **Discovered during Task 2 verification:** the plan's own `<acceptance_criteria>`/`<verify>`
  text specifies `-k "title"` as the selector that isolates the 5 title-source CONTROL tests in
  the new module. Measured directly: pytest's `KeywordMatcher` matches a `-k` keyword as a
  case-insensitive substring against the name of every node in an item's chain, **including the
  Module node** — whose name is the bare filename. Because this plan's own mandated filename
  (`test_admonition_locale_title_precedence_gate.py`) itself contains the substring `"title"`,
  `-k "title"` matches all 9 tests in the module, not only the 5 intended ones — running it
  literally produces `4 failed, 5 passed`, not a clean pass. Verified the true partition instead
  with the refined selector `-k "title_is or title_argument or catalog_title or titles_never"`,
  which selects exactly the 5 title-source CONTROL tests and all pass. Recorded verbatim (both
  the literal command's actual result and the refined selector's clean pass) in
  `39-GATE-EVIDENCE-05.md` §4 so a later reader does not have to re-derive this. This is a
  structural property of pytest's Module-node keyword matching against the plan's own mandated
  filename, not a defect in any test body, and it does not affect the recorded RED/CONTROL
  evidence's correctness — only the convenience of that one specific selector command.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- This plan's RED is recorded and ready for plan 39-11 (next wave), which flips it GREEN by
  re-routing `visit_danger` (to `danger`) and `visit_attention` (to `memo`) in
  `typsphinx/translator.py`. No file under `typsphinx/` was touched by this plan — confirmed by
  empty `git diff --stat -- typsphinx/` over both task commits.
- No blockers. `tests/test_preview_version_sync.py` stays green (no `@preview` pin moved), and the
  full non-slow suite shows failures ONLY in the 7 intentionally-recorded RED tests (3 in
  `test_admonition_bucket_render_gate.py`, 4 in `test_admonition_locale_title_precedence_gate.py`).

## Self-Check: PASSED

- FOUND: tests/test_admonition_locale_title_precedence_gate.py
- FOUND: tests/fixtures/admonition_locale_title_gate/en/conf.py
- FOUND: tests/fixtures/admonition_locale_title_gate/ja/conf.py
- FOUND: .planning/phases/39-admonition-taxonomy-rubric-nesting/39-GATE-EVIDENCE-05.md
- FOUND: .planning/phases/39-admonition-taxonomy-rubric-nesting/39-09-SUMMARY.md
- FOUND commits: 29f4247, 791a4d5, 97537cb (all present in `git log --oneline -5`)

---
*Phase: 39-admonition-taxonomy-rubric-nesting*
*Completed: 2026-08-02*
