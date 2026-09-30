---
phase: 48-compile-time-cross-reference-guard
plan: 07
subsystem: docs-build
tags: [typst, sphinx, cross-reference, pdf, gap-closure, tdd]

# Dependency graph
requires:
  - phase: 48-compile-time-cross-reference-guard (plans 01-06)
    provides: the D-07 compile-time label-existence guard contract and its three anchored-xref
      call sites, 48-05's write-expected-values-first design for the whole-document reference path
      (self-anchor token, definition/reference-site forms, expected PDF shape, the owner's option-a
      policy choice), and 48-06's real fixture plus two strict-xfail test modules recording the
      G-48-4 defect RED (9 flipping assertions)
provides:
  - The emitter fix: every content file emits a stable whole-document self-anchor
    (`_WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN`, `__tsx-doc__`), `_resolve_xref_docname` resolves a
    no-fragment refuri to an empty-anchor pair instead of `None`, and a new
    `_whole_document_reference_eligible` policy predicate (option-a: `found_docs` membership) gates
    whether that pair is exposed through `_reference_anchor_decision`'s `.xref` field -- routing a
    whole-document reference through the existing single D-07 guard instead of the external-link
    string-url branch.
  - All 9 strict-xfail gates plan 48-06 recorded RED flipped to plain passing assertions across
    `tests/test_whole_document_xref_unit.py` and `tests/test_xref_whole_document_guard_render_gate.py`
    -- zero XPASS, every invariance guard still green.
  - The rebuilt `docs/_build/pdf/typsphinx.pdf`'s dead-link population measured against
    `48-RED-EVIDENCE.md`'s Baseline 4: 40 URI actions / 20 targets -> 5 URI actions / 5 targets,
    matching `48-EXPECTED-STRUCTURE.md`'s pre-declared expected value exactly. The before/after
    comparison, the Quickstart-page re-check, and the closing G-48-4 narrative are appended to
    `48-EVIDENCE.md`.
affects: []

# Actuals (#2632)
actuals:
  tokens: 8011
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Resolver/policy split (Phase 48 plan 06's own design, reconciled here): `_resolve_xref_docname`
      is the UNCONDITIONAL low-level resolver (any local no-fragment refuri ending in `out_suffix`
      resolves to `(docname, \"\")`), while `_reference_anchor_decision` applies the option-a
      `found_docs` policy gate one layer up, immediately after the resolver call, before exposing
      the pair through its own `.xref` field."
    - "One-expression policy predicate, read defensively: `_whole_document_reference_eligible`'s
      entire body is `target_docname in getattr(getattr(self.builder, \"env\", None), \"found_docs\",
      ())` -- a stub builder with no `env` (every hand-built-doctree test in the corpus) yields
      not-eligible rather than raising, keeping every existing test byte-unchanged."

key-files:
  created: []
  modified:
    - typsphinx/translator.py
    - tests/test_whole_document_xref_unit.py
    - tests/test_xref_whole_document_guard_render_gate.py
    - tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
    - tests/test_desc_rubric_decoupling_render_gate.py
    - .planning/phases/48-compile-time-cross-reference-guard/48-EVIDENCE.md
    - .planning/phases/48-compile-time-cross-reference-guard/48-EXPECTED-STRUCTURE.md

key-decisions:
  - "The whole-document self-anchor is emitted in `visit_document`, immediately after `self.add_text(\"#{\\n\")`,
    gated on `self._current_docname()` being truthy -- so hand-built test doctrees with no builder
    docname keep byte-identical output, matching every other `_current_docname()`-gated site."
  - "The policy gate lives at exactly one call site inside `_reference_anchor_decision`, immediately
    after the existing single `_resolve_xref_docname` call: when the resolved anchor is empty AND
    `_whole_document_reference_eligible` says no, `xref` is dropped back to `None`. An anchored
    cross-document `xref` (non-empty anchor) is untouched -- the gate only ever narrows the NEW
    empty-anchor case."
  - "The reference site's only change is the label argument: `_namespace_label(target_docname, anchor
    or _WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN)` -- the same one `_namespace_label` call, the same one
    `_label_existence_guard` call, no second guard-string derivation point and no second label
    helper (D-07/D-13)."

requirements-completed: [XREF-03, XREF-04]

coverage:
  - id: D1
    description: "Every whole-document reference whose target resolves onto a real, found_docs-member
      document is routed through the D-07 compile-time guard against that target's own
      per-document self-anchor, instead of a dead string-url link to a file the typstpdf builder
      never produces."
    requirement: XREF-03
    verification:
      - kind: integration
        ref: "tests/test_xref_whole_document_guard_render_gate.py -- 8 passed, 0 xfailed, 0 XPASS"
        status: pass
      - kind: unit
        ref: "tests/test_whole_document_xref_unit.py -- 9 passed, 0 xfailed, 0 XPASS"
        status: pass
    human_judgment: false
  - id: D2
    description: "No second guard-string derivation point, no second label helper, and no
      replacement build-time degrade mechanism reintroduced (single D-07/D-13 derivation points
      preserved)."
    requirement: XREF-04
    verification:
      - kind: other
        ref: "grep -c 'query(<{label}>)' typsphinx/translator.py == 1; grep -rn
          'master_included_docnames|degrade_xref_to_text' typsphinx/ returns nothing"
        status: pass
    human_judgment: false
  - id: D3
    description: "The rebuilt documentation PDF's dead-link population matches the pre-declared
      expected post-fix count exactly (5 URI actions ending in .pdf, down from the 40-annotation
      baseline), with the residue named individually rather than implied."
    requirement: XREF-03
    verification:
      - kind: other
        ref: "48-EVIDENCE.md 'G-48-4 post-fix re-measurement' section -- uv run tox -e docs-pdf +
          Baseline 4's own enumeration snippet re-run verbatim; measured count 5, matches
          48-EXPECTED-STRUCTURE.md section 6 exactly"
        status: pass
    human_judgment: false
  - id: D4
    description: "The phase closes green: full pytest suite, black, mypy clean; ruff recorded
      honestly against the documented NixOS deferral."
    requirement: XREF-04
    verification:
      - kind: other
        ref: "uv run pytest -q -- 1083 passed, 1 skipped, 0 failed/errors/xfailed/XPASS; uv run
          black --check . and uv run mypy typsphinx/ both clean"
        status: pass
    human_judgment: false

# Metrics
duration: ~45min
completed: 2026-08-14
status: complete
---

# Phase 48 Plan 07: Whole-Document Cross-Reference Guard (G-48-4 Gap Closure) Summary

**Every content file now emits a stable whole-document self-anchor and `:doc:`-role references route through the existing single D-07 compile-time guard, closing G-48-4: the rebuilt documentation PDF's dead-link population drops from 40 URI actions (20 targets) to exactly the pre-declared expected 5 (the Sphinx-generated genindex/py-modindex/search pages, kept by the owner's option-a policy) -- all 9 strict-xfail gates from plan 48-06 flip to plain passing assertions, full suite green (1083 passed, 1 skipped, 0 xfailed/XPASS).**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-08-14T13:36:29+09:00
- **Tasks:** 3 (Task 1 `type="tracer" tdd="true"`, Tasks 2-3 `type="auto"`)
- **Files modified:** 7

## Accomplishments

- **Load-bearing semantics probe (Task 1, Step 0):** confirmed via two throwaway `.typ` files
  compiled with `typst.compile()` under the scratchpad (never in the repository) that a
  zero-width `metadata`-attached label is findable by `query()` and linkable by `link()`: with the
  anchor present, the guard's positive branch fires and produces a real `/Link` annotation with a
  POSITIONAL destination; with it absent, the compile still succeeds, the reference's visible text
  is unchanged, and zero annotations exist. Both transcripts appended to `48-EVIDENCE.md`.
- **The module constant and definition site:** added `_WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN =
  "__tsx-doc__"` as one module-level constant (its docstring restates the collision-safety argument
  `48-EXPECTED-STRUCTURE.md` measured), and `visit_document` now emits
  `[#metadata(none) <{docname}:__tsx-doc__>]` immediately after the opening code-block brace, gated
  on `self._current_docname()` being truthy.
- **The resolver:** `_resolve_xref_docname` no longer returns `None` up front for a local
  no-fragment refuri -- it resolves via the SAME path arithmetic the anchored case already uses and
  returns `(target_docname, "")`. Every other `None` return (external schemes, protocol-relative,
  `mailto:`, wrong suffix, unknown current docname, same-document `#anchor` refs) is unchanged.
- **The policy predicate:** a new `_whole_document_reference_eligible(node, target_docname)` method,
  a one-expression `found_docs` membership test (read defensively via nested `getattr`), consulted
  exactly once inside `_reference_anchor_decision` immediately after the resolver call -- implements
  option-a, the owner's recorded checkpoint choice, and is documented as a ROUTING decision, never a
  second degrade decision.
- **The reference site:** `visit_reference`'s cross-document branch now hands `_namespace_label` the
  reference's own anchor when it has one, or the module constant when it does not -- the same one
  `_namespace_label` call, the same one `_label_existence_guard` call.
- **Flipped all 9 strict-xfail gates** (4 in `test_whole_document_xref_unit.py`, 5 in
  `test_xref_whole_document_guard_render_gate.py`) to plain passing assertions; every invariance
  guard (5 + 3) stayed green throughout.
- **Reconciled the one collateral test the corpus-wide self-anchor line moved:**
  `test_desc_rubric_decoupling_render_gate.py`'s byte-identity golden-fixture test -- updated
  `golden.typ` with the one new line, per `48-EXPECTED-STRUCTURE.md` section 2's derivation, and
  recorded the change (test name + sub-part) in a new section appended to
  `48-EXPECTED-STRUCTURE.md`. No real regressions found; every hand-built-doctree test stayed
  byte-unchanged.
- **Re-measured the built documentation PDF** via the SAME `uv run tox -e docs-pdf` invocation and
  the SAME enumeration snippet Baseline 4 pinned: URI actions ending in `.pdf` drop from 40 (20
  distinct targets) to 5 (5 distinct targets) -- agreeing EXACTLY with the single number
  `48-EXPECTED-STRUCTURE.md` fixed before the fix existed. Sub-population A (35 annotations, 15 real
  documents) fully converts to internal `/Dest` links; sub-population B (the 5 Sphinx-generated
  pages) remains string-url by the owner's option-a policy, named individually with counts. The
  Quickstart "What's Next?" page's four originally reported dead links are confirmed absent from the
  URI-action set with identical visible text (D-02). Full before/after comparison appended to
  `48-EVIDENCE.md`.

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end -- one whole-document reference resolves to a real destination in a compiled PDF** - `d3cb9eee` (feat)
2. **Task 2: Reconcile the corpus-wide emission change and close the quality trio** - `7b1e9e71` (test)
3. **Task 3: Re-measure the built documentation PDF and close the gap on numbers** - `101ebb14` (docs)

_Per this phase's own established convention: the RED (`xfail(strict=True)`) markers landed in
plan 48-06; this plan's Task 1 commit is the corresponding `feat(...)` GREEN, satisfying the
plan-level TDD gate sequence (test commit in 48-06, feat commit here)._

## Files Created/Modified

- `typsphinx/translator.py` - `_WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN` module constant; self-anchor
  emission in `visit_document`; unconditional empty-anchor resolution in `_resolve_xref_docname`;
  new `_whole_document_reference_eligible` policy predicate; the empty-anchor gate in
  `_reference_anchor_decision`; the reference-site label substitution in `visit_reference`.
- `tests/test_whole_document_xref_unit.py` - 4 strict-xfail markers removed (Flips 1-4), now plain
  passing assertions.
- `tests/test_xref_whole_document_guard_render_gate.py` - 5 strict-xfail markers removed (Flips
  5-9), now plain passing assertions.
- `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` - gained the one-line self-anchor
  the corpus-wide emission change predicted.
- `tests/test_desc_rubric_decoupling_render_gate.py` - docstring comment tracing the golden-fixture
  update to `48-EXPECTED-STRUCTURE.md` section 2.
- `.planning/phases/48-compile-time-cross-reference-guard/48-EVIDENCE.md` - appended the Task 1
  Step-0 probe transcripts and the Task 3 post-fix re-measurement section (before/after bucket
  totals, per-target table, sub-population subtotals, Quickstart re-check, closing narrative).
- `.planning/phases/48-compile-time-cross-reference-guard/48-EXPECTED-STRUCTURE.md` - appended the
  "Phase 48 Plan 07 -- Collateral Test Changes" section (the one moved test, no real regressions,
  quality-trio results).

## Decisions Made

See `key-decisions` in frontmatter: the resolver/policy split (unconditional resolver, one-layer-up
policy gate), the `_current_docname()`-gated definition-site emission, and the single-expression
defensive `found_docs` predicate.

## Deviations from Plan

None substantive -- plan executed as written. One minor, expected item:

**1. [Rule 1 - formatting] `black` reformatting after the policy-gate `if` statement.** Adding the
`_whole_document_reference_eligible` guard to `_reference_anchor_decision` produced an `if`
statement whose line-wrap `black` reformats differently than my first draft. Found during Task 2's
own `uv run black --check .` step (as the plan's own action anticipates); fixed by running
`uv run black typsphinx/translator.py`, re-verified clean, and the full suite re-run green
afterward -- a pure line-wrap, no behavioural change. Committed as part of Task 2's commit
(`7b1e9e71`).

## Issues Encountered

None. The worktree's own environment provisioning (`uv sync --extra dev --extra docs`,
`VIRTUAL_ENV`/`UV_PROJECT_ENVIRONMENT` unset) completed without incident; isolation was confirmed
before any edit. `uv` was symlinked from its nix-store path into `.venv/bin/uv` per the documented
NixOS hazard workaround; no standalone nix-store `ruff` package was available to symlink (matching
plan 48-06's own recorded finding), so `ruff check .` was run and its verbatim
`Could not start dynamically linked executable: ruff` output recorded honestly rather than claimed
clean.

## TDD Gate Compliance

Task 1 (`type="tracer" tdd="true"`) is this plan's GREEN: the RED half (9 assertions recorded
`xfail(strict=True)`, verbatim transcripts in `48-RED-EVIDENCE.md`) landed in plan 48-06's
`test(48-06): ...` commits. This plan's Task 1 commit (`d3cb9eee`, `feat(48-07): ...`) is the
corresponding GREEN commit, and it flips every one of the 9 flipping assertions to a plain passing
test with zero XPASS -- satisfying the plan-level RED/GREEN gate sequence across the two plans.

## Known Stubs

None. No hardcoded empty values, placeholder text, or unwired data sources were introduced.

## Threat Flags

None. Every threat this plan's own `<threat_model>` named (T-48-07-01 through T-48-07-04, T-48-SC)
was mitigated or accepted exactly as the plan's disposition column specified -- no new surface
outside that register was introduced.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- G-48-4 (XREF-03/XREF-04) is closed: the emitter change, the flipped gates, and the re-measurement
  are all committed. No follow-on plan is required by this gap.
- The phase closes green on the full quality gate: `uv run pytest -q` -> 1083 passed, 1 skipped, 0
  failed/errors/xfailed/XPASS; `black`/`mypy` clean; `ruff` recorded against the documented,
  pre-existing NixOS deferral.
- No blockers. `git diff --stat typsphinx/` shows only `translator.py` across this plan's three
  commits; the accepted label-collision false-negative limit
  (`.planning/todos/pending/2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md`)
  is untouched and not worsened, since the whole-document path's label token is unreachable from
  either collision source that limit's todo names.

---
*Phase: 48-compile-time-cross-reference-guard*
*Completed: 2026-08-14*

## Self-Check: PASSED

All 7 claimed files confirmed present on disk (`typsphinx/translator.py`,
`tests/test_whole_document_xref_unit.py`, `tests/test_xref_whole_document_guard_render_gate.py`,
`tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ`,
`tests/test_desc_rubric_decoupling_render_gate.py`, `48-EVIDENCE.md`, `48-EXPECTED-STRUCTURE.md`),
plus this SUMMARY.md itself; all 3 task commit hashes (`d3cb9eee`, `7b1e9e71`, `101ebb14`)
confirmed present in `git log --oneline --all`. No missing items.
