---
phase: 48-compile-time-cross-reference-guard
plan: 06
subsystem: testing
tags: [pypdf, docutils, sphinx, typst, cross-reference, gap-closure, tdd]

# Dependency graph
requires:
  - phase: 48-compile-time-cross-reference-guard (plans 01-05)
    provides: the D-07 compile-time label-existence guard contract and its three anchored-xref
      call sites, and 48-05's write-expected-values-first design for the whole-document reference
      path (self-anchor token, definition/reference-site forms, fixture design, expected PDF shape,
      expected post-fix count) in 48-EXPECTED-STRUCTURE.md
provides:
  - A real two-outcome sphinx-build -> typst.compile() acceptance fixture
    (tests/fixtures/xref_whole_document_guard_gate/) exercising the whole-document reference form
    (`:doc:`) in both directions at once -- one reference to a toctree-reachable document, one to
    an `:orphan:` document -- built green today and demonstrably emitting the G-48-4 defect (two
    dead string-url `link("<target>.pdf", ...)` calls, no self-anchors).
  - A fast offline unit gate (tests/test_whole_document_xref_unit.py) on the resolver
    (`_resolve_xref_docname`), the policy predicate (`_reference_anchor_decision`'s option-a
    found_docs/internal gate), and the self-anchor emission (`visit_document`) -- 4 flipping
    assertions recorded `xfail(strict=True)`, 5 invariance/option-specific assertions plain.
  - A real sphinx-build -> typst.compile() -> pypdf render gate
    (tests/test_xref_whole_document_guard_render_gate.py) over the same fixture -- 5 flipping
    assertions recorded `xfail(strict=True)`, 3 invariance assertions plain, plus a locally-scoped
    `_classify_link_annotations` helper (named/positional/URI-action buckets) this module's own.
  - A "Phase 48 Plan 06" section appended to 48-RED-EVIDENCE.md: fixture topology, the Task 1
    probe transcript, verbatim pre-fix pytest output for both new modules with strict xfail
    markers temporarily removed, the measured 3-page PDF layout and the resulting
    destination-page-assertion honesty caveat, and a provenance header.
affects: [48-07]

# Actuals (#2632)
actuals:
  tokens: 17964
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Locally-scoped test stub per module (D-02: imitate, never import) -- this plan's own
      _StubBuilder/_MockEnv carry a found_docs set neither sibling stub module needs, added here
      rather than editing test_citation_degradation_gate.py or test_label_existence_guard_unit.py."
    - "getattr-resolved not-yet-existing module constant -- the self-anchor token constant
      (_WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN) is never imported at module top level (it does not exist
      pre-fix); resolved via getattr inside the one test that asserts it, so a missing constant
      fails that test instead of breaking collection for the whole file."
    - "Positional-vs-named PDF destination classification -- a locally-scoped
      _classify_link_annotations helper buckets /Link annotations into named/positional/URI-action,
      documented against a real measured probe (xref_orphan_degrade_render_gate's metadata-only
      anchor) rather than assumed, per this phase's own _link_annotation_dests precedent."

key-files:
  created:
    - tests/fixtures/xref_whole_document_guard_gate/conf.py
    - tests/fixtures/xref_whole_document_guard_gate/index.rst
    - tests/fixtures/xref_whole_document_guard_gate/included.rst
    - tests/fixtures/xref_whole_document_guard_gate/orphan.rst
    - tests/test_whole_document_xref_unit.py
    - tests/test_xref_whole_document_guard_render_gate.py
  modified:
    - .planning/phases/48-compile-time-cross-reference-guard/48-RED-EVIDENCE.md

key-decisions:
  - "Split the resolver fix into two layers per Task 2's own behaviour list: _resolve_xref_docname
    becomes an UNCONDITIONAL low-level resolver (any whole-document refuri ending in out_suffix
    resolves to (docname, \"\")), while _reference_anchor_decision applies the option-a
    found_docs/internal POLICY gate one layer up before exposing that pair through its own .xref
    field. This reconciles Task 2's specific flip-1/flip-2 split with 48-EXPECTED-STRUCTURE.md
    §6's higher-level found_docs-gate description -- both land on the identical final label value."
  - "The option-specific test (internal reference onto an unknown target, option-a) is NOT an
    xfail: its assertion (decision.xref is None) is true both pre-fix (nothing is routed through
    the guard yet) and post-fix (option-a's predicate excludes it), so it never flips -- only its
    docstring needed to name the chosen option."
  - "Destination-page assertion recorded honestly as weak: the fixture's compiled master lays out
    on 3 PDF pages (title, TOC, one content page), and every body element collapses onto that
    single content page, so the positional-destination-resolves-to-included's-page assertion
    cannot distinguish a correct destination from one pointing at a different anchor on the SAME
    page -- it can only rule out the title/TOC pages. Stated in both the module's class docstring
    and the RED evidence, per 48-EXPECTED-STRUCTURE.md §5's own instruction not to overclaim."

requirements-completed: [XREF-03]

coverage:
  - id: D1
    description: "Real two-outcome sphinx-build -> typst.compile() acceptance fixture for the
      whole-document reference path, built green today and demonstrably emitting the G-48-4
      defect (probed, not asserted by a test in this plan -- Task 1 has no test module of its
      own, only the fixture plus its own verify command)."
    requirement: XREF-03
    verification:
      - kind: other
        ref: "Task 1 acceptance criteria: probe build exit 0, grep -c 'link(\"' index.typ == 2,
          grep -c 'metadata(none) <included:' included.typ == 0 -- all confirmed this session"
        status: pass
    human_judgment: false
  - id: D2
    description: "Fast offline unit gate on the resolver, the policy predicate, and the self-anchor
      emission -- 4 flipping assertions recorded RED (strict xfail), 5 invariance/option-specific
      assertions plain, zero XPASS."
    requirement: XREF-03
    verification:
      - kind: unit
        ref: "tests/test_whole_document_xref_unit.py -- 5 passed, 4 xfailed"
        status: pass
    human_judgment: false
  - id: D3
    description: "Real render gate (sphinx-build -> typst.compile() -> pypdf) over the same
      fixture -- 5 flipping assertions recorded RED (strict xfail), 3 invariance assertions plain,
      zero XPASS."
    requirement: XREF-03
    verification:
      - kind: integration
        ref: "tests/test_xref_whole_document_guard_render_gate.py -- 3 passed, 5 xfailed"
        status: pass
    human_judgment: false
  - id: D4
    description: "48-RED-EVIDENCE.md carries the new provenance-headed section with verbatim
      pre-fix transcripts for both new modules, additions-only against the file."
    requirement: XREF-03
    verification:
      - kind: other
        ref: ".planning/phases/48-compile-time-cross-reference-guard/48-RED-EVIDENCE.md -- 'Phase
          48 Plan 06' section; git diff shows 530 insertions(+), 0 deletions"
        status: pass
    human_judgment: false

# Metrics
duration: ~70min
completed: 2026-08-14
status: complete
---

# Phase 48 Plan 06: Whole-Document Cross-Reference Guard Gate Summary

**Built a real two-outcome sphinx-build acceptance fixture plus two test modules (9 strict-xfail
flips, 8 invariance/option-specific plains) proving the G-48-4 whole-document dead-link defect RED
against the unfixed translator, with the verbatim pre-fix transcripts pasted into
48-RED-EVIDENCE.md -- zero changes to typsphinx/, suite closes green (1070 passed, 5 skipped, 9
xfailed).**

## Performance

- **Duration:** ~70 min
- **Completed:** 2026-08-14T04:11:11Z
- **Tasks:** 3 (all `type="auto"`, Tasks 2-3 also `tdd="true"`)
- **Files modified:** 7 (6 created, 1 modified)

## Accomplishments

- Built `tests/fixtures/xref_whole_document_guard_gate/` per `48-EXPECTED-STRUCTURE.md` §4's
  paper design: master `index` (target `manual.typ`, de-collided from `index.typ`) toctrees
  `included` only and carries one `:doc:` reference to `included` (toctree-reachable) and one to
  `orphan` (`:orphan:`, in no toctree). Probed via `uv run python -m sphinx -b typstpdf`: exit 0,
  a valid compiled PDF, and both whole-document references emitting as plain string-url
  `link("included.pdf", ...)` / `link("orphan.pdf", ...)` calls with no self-anchors anywhere --
  the defect, demonstrated rather than asserted.
- Wrote `tests/test_whole_document_xref_unit.py`: a fast, offline unit gate splitting the fix into
  two layers per the plan's own Task 2 design -- `_resolve_xref_docname` as an unconditional
  low-level resolver (4 flip assertions: raw resolution, the policy-gated `.xref` field, the
  self-anchor's zero-width emission, and the token's single-derivation-point structural check) and
  `_reference_anchor_decision` as the option-a-gated policy layer (found_docs + internal). Every
  flip recorded `xfail(strict=True)`; 5 invariance/option-specific assertions (no builder docname,
  non-internal+unknown-target, anchored-xref unchanged, and the option-a divergent case, which
  never flips) land plain.
- Wrote `tests/test_xref_whole_document_guard_render_gate.py`: a slow, real
  `sphinx-build -> typst.compile() -> pypdf` render gate over the same fixture, with its own
  `_classify_link_annotations` helper bucketing `/Link` annotations into named/positional/
  URI-action, documented against a real measured probe of an existing sibling fixture's
  metadata-only anchor (not assumed). 5 flip assertions (both guard expressions present, no
  string-url links remain, both self-anchors present exactly once, zero URI actions ending in
  `.pdf`, exactly one positional destination resolving to `included`'s marker page) recorded
  `xfail(strict=True)`; 3 invariance assertions (clean exit/no dangling label, D-02 visible-text
  parity, orphan marker never leaks into the compiled master) land plain.
- Appended "Phase 48 Plan 06" to `48-RED-EVIDENCE.md`: fixture topology, the Task 1 probe
  transcript, the verbatim pre-fix pytest output for both new modules with their strict xfail
  markers temporarily removed (via a scratch copy inside `tests/`, deleted immediately after
  capture -- never part of the committed diff), the measured 3-page PDF layout and the resulting
  destination-page-assertion honesty caveat, and a provenance header (interpreter, typst-py
  0.15.0, pypdf 6.14.2, HEAD SHA). `git diff` on this file shows additions only.
- Confirmed the full suite closes green: `uv run pytest -q` -> 1070 passed, 5 skipped, 9 xfailed
  (baseline was 1062 passed, 5 skipped; +8 new invariance/option passes, +9 new strict xfails,
  zero regressions, zero XPASS).

## Task Commits

Each task was committed atomically:

1. **Task 1: Build the whole-document acceptance fixture and record what it emits today** -
   `79a18007` (test)
2. **Task 2: Fast offline unit gate for the resolver, the policy predicate and the self-anchor** -
   `67f28df0` (test)
3. **Task 3: Real sphinx-build -> typst.compile() -> pypdf render gate, recorded RED** -
   `b5c8c1ab` (test)

_Note: per this phase's own established convention (`48-CONTEXT.md` § "Established patterns"),
pre-fix REDs land as `xfail(strict=True)` with the verbatim transcript in
`48-RED-EVIDENCE.md`, committed with `test(48-06): ...` messages -- there is no `feat(...)` commit
in this plan, since the emitter fix (GREEN) is deliberately deferred to plan 48-07 by the wave
split (binding constraint #4's non-fatal amendment)._

## Files Created/Modified

- `tests/fixtures/xref_whole_document_guard_gate/conf.py` - Load-bearing-properties fixture config;
  single `typst_documents` master `index` -> `manual.typ`.
- `tests/fixtures/xref_whole_document_guard_gate/index.rst` - Master document: toctrees `included`
  only, carries one `:doc:` reference to each of `included` and `orphan`.
- `tests/fixtures/xref_whole_document_guard_gate/included.rst` - Toctree-reachable target, titled
  "Included Whole-Document Target", carries `INCLUDED_BODY_MARKER_TEXT`.
- `tests/fixtures/xref_whole_document_guard_gate/orphan.rst` - `:orphan:`, in no toctree, titled
  "Orphan Whole-Document Target", carries `ORPHAN_BODY_MARKER_TEXT`.
- `tests/test_whole_document_xref_unit.py` - Fast offline unit gate: resolver, policy predicate,
  self-anchor emission, single-derivation-point structural check.
- `tests/test_xref_whole_document_guard_render_gate.py` - Slow real-build render gate:
  guard-expression presence, string-url absence, self-anchor presence, PDF URI-action count,
  positional-destination page resolution.
- `.planning/phases/48-compile-time-cross-reference-guard/48-RED-EVIDENCE.md` - Appended "Phase 48
  Plan 06 -- Whole-Document Unit + Render Gate RED" section.

## Decisions Made

- **Resolver/policy split** (see `key-decisions` in frontmatter): `_resolve_xref_docname` becomes
  unconditional; `_reference_anchor_decision` applies the option-a found_docs/internal gate before
  exposing the pair through `.xref`. Both layers converge on the identical final label value
  regardless of which function does the gating, reconciling this plan's own Task 2 design with
  `48-EXPECTED-STRUCTURE.md` §6's higher-level description.
- **Option-specific test is not an xfail** — its assertion is true both pre- and post-fix (option-a
  never routes an unknown-target internal reference through the guard), so it was written as a
  plain test whose docstring names the option, rather than mislabelled as a flip (which would XPASS
  and fail the strict marker).
- **Destination-page assertion recorded as weak, honestly** — the fixture's 3-page compiled PDF
  collapses every body element onto one content page, so the assertion cannot distinguish a correct
  destination from a wrong anchor on the same page; stated in the module's own class docstring and
  in the RED evidence rather than overclaiming precision.

## Deviations from Plan

None - plan executed exactly as written. Two clarifications worth recording (neither a deviation,
both within Claude's discretion per the plan):

1. **rST double-backtick adjacency fix (Rule 1 - bug in my own fixture prose, not typsphinx).**
   The first draft of `included.rst`/`orphan.rst` used `` ``#include()``s it `` — docutils rejects
   a closing `` `` `` immediately followed by an alphanumeric character ("Inline literal
   start-string without end-string"), producing two spurious build warnings. Rephrased to "runs
   ``#include()`` on it" in both files before probing. Caught and fixed during Task 1, before any
   commit.
2. **xfail decorator formatting for the grep-count acceptance criterion.** `black` reformats
   `@pytest.mark.xfail(strict=True, reason=(...))` onto multiple lines when the reason string is
   long, which breaks the literal `grep -c 'xfail(strict=True'` substring the acceptance criteria
   require. Shortened every `reason=` to a one-line pointer into `48-RED-EVIDENCE.md`'s named
   section (the fuller rationale already lives in each test's own docstring), keeping the decorator
   on one physical line under black's line-length limit.

## Issues Encountered

None. Both fixture probe builds (`-b typstpdf`, Task 1) completed cleanly on the first attempt
after the rST literal-adjacency fix above. The worktree's own environment provisioning
(`uv sync --extra dev`, `VIRTUAL_ENV`/`UV_PROJECT_ENVIRONMENT` unset) was required and completed
without incident; isolation was independently confirmed (`import typsphinx` resolving to this
worktree's own copy) before any test was written. `ruff`'s generic-linux ELF (the documented
NixOS hazard) was not exec-runnable in this worktree and no standalone nix-store `ruff` package
was available to symlink; since this plan's own verification commands never invoke `ruff`/`black`
directly (only `pytest`/`sphinx-build`) and no pre-commit hook in this repo runs `ruff` on commit,
this was left unaddressed as out of scope for this plan -- `black` (which IS load-bearing for the
grep-count acceptance criterion) was run successfully via the `.venv`'s own pure-Python entry
point and required no ELF workaround.

## TDD Gate Compliance

Tasks 2 and 3 carry `tdd="true"`, but this plan is deliberately RED-only (binding constraint #4's
non-fatal amendment, this phase's own established convention): every flipping assertion was
verified to fail for the diagnosed reason against the unfixed tree (verbatim transcripts pasted
into `48-RED-EVIDENCE.md`), then landed committed as `xfail(strict=True)` rather than as an
unguarded failing test followed by a `feat(...)` GREEN commit. There is no `feat(48-06): ...`
commit in this plan by design -- the emitter fix is plan 48-07's own GREEN. This mirrors every
prior gap-closure plan in this phase (`test_xref_compile_time_guard_render_gate.py`'s own module
docstring records the identical pattern for plan 48-01/48-02).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 48-07 has two committed test modules (9 strict xfails total) plus a real acceptance
  fixture ready to flip: it must add `_WHOLE_DOCUMENT_SELF_ANCHOR_TOKEN` as a module-level
  constant in `typsphinx/translator.py`, extend `_resolve_xref_docname` to resolve a no-fragment
  whole-document refuri to `(docname, "")`, gate `_reference_anchor_decision`'s exposure of that
  pair on `node.get("internal")` + `env.found_docs` membership (option-a), emit the self-anchor
  immediately after `visit_document`'s opening `#{\n`, and route the whole-document case through
  the existing `_label_existence_guard` call using the self-anchor token in place of an empty
  anchor.
- The expected post-fix count (5 URI actions ending in `.pdf` in the rebuilt corpus PDF, per
  `48-EXPECTED-STRUCTURE.md` §6) and the full `48-RED-EVIDENCE.md` "Baseline 4" measurement remain
  plan 48-07's own re-measurement responsibility -- untouched by this plan.
- No blockers. `git status --porcelain typsphinx/` printed nothing throughout this plan's three
  tasks, confirmed after each commit.

---
*Phase: 48-compile-time-cross-reference-guard*
*Completed: 2026-08-14*

## Self-Check: PASSED

All 8 claimed files confirmed present on disk (4 fixture files, 2 test modules,
`48-RED-EVIDENCE.md`, this SUMMARY); all 3 task commit hashes (`79a18007`, `67f28df0`, `b5c8c1ab`)
confirmed present in `git log --oneline --all`. No missing items.
