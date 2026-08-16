---
phase: 55-v0-8-0-derived-defects
plan: 01
subsystem: translator
tags: [sphinx, typst, xref, label-sanitization, regex, injectivity]

# Dependency graph
requires:
  - phase: 48-compile-time-cross-reference-guard
    provides: "_label_existence_guard() and the xref_label_collision_guard_gate fixture this plan inverts"
provides:
  - "TypstTranslator._sanitize_label is injective: two distinct docnames can no longer sanitize to one Typst label"
  - "_LABEL_TOKEN_INTRODUCER_RE module-level pre-pass constant"
  - "tests/test_sanitize_label_injectivity_unit.py's exhaustive decoder-round-trip proof suite"
affects: [55-02, 55-03, 55-04, xref-guard, label-emission]

# Actuals (#2632)
actuals:
  tokens: 9200
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Escape an encoding token's own INTRODUCING character, not the whole literal token, to close the seam a downstream substitution would otherwise create"
    - "Prove a string-transform injective via a test-only decoder round-trip over an exhaustive adversarial alphabet plus a large seeded-random sample, rather than trusting one fixture"

key-files:
  created:
    - tests/test_sanitize_label_injectivity_unit.py
    - .planning/phases/55-v0-8-0-derived-defects/55-01-RED-EVIDENCE.md
  modified:
    - typsphinx/translator.py
    - tests/test_xref_compile_time_guard_render_gate.py
    - tests/fixtures/xref_label_collision_guard_gate/conf.py
    - tests/test_label_existence_guard_unit.py

key-decisions:
  - "D-01/D-02 honored exactly: the fix lives entirely inside _sanitize_label (no Typst-side existence mechanism, no second escaping primitive); the re-escape targets only a literal _u<hex>_ token shape, so ordinary ids stay byte-identical"
  - "Escaped the token's own INTRODUCING underscore via a lookahead pre-pass (_LABEL_TOKEN_INTRODUCER_RE, replacement _u5f_) rather than doubling a leading underscore or inserting an extra u -- both alternatives were measured non-injective this phase (a_/b collides with a_u2f_b under doubling; _u2f/ collides with /u2f_ under the extra-u repair)"
  - "collision_guard_build test fixture extended to also read a_u2f_b.typ (the decoy's own included content file) -- the decoy's re-escaped anchor label lives there, not in index.typ"

patterns-established:
  - "Injectivity proof via test-only decoder round-trip (tests/test_sanitize_label_injectivity_unit.py's _decode_label) -- future encoding-scheme changes in this codebase should follow the same exhaustive-plus-random proof shape rather than a single fixture"

requirements-completed: [XREF-05]

coverage:
  - id: D1
    description: "A cross-reference whose real target is absent from the compiling master degrades to plain text instead of linking to a same-spelled decoy (real two-master sphinx-build -b typstpdf + typst.compile())"
    requirement: "XREF-05"
    verification:
      - kind: integration
        ref: "tests/test_xref_compile_time_guard_render_gate.py::TestXrefCompileTimeGuardRenderGate::test_label_collision_no_longer_links_to_decoy"
        status: pass
    human_judgment: false
  - id: D2
    description: "_sanitize_label is injective in general, not merely on the one known collision fixture -- proven by exhaustive decoder round-trip plus 20,000 random adversarial strings, with both rejected constructions pinned by their own counterexamples"
    requirement: "XREF-05"
    verification:
      - kind: unit
        ref: "tests/test_sanitize_label_injectivity_unit.py (31 tests)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Full-suite churn scope measured (not assumed): exactly one docname in the repository spells the encoder's own token shape; full pytest suite, black, ruff and mypy all clean"
    requirement: "XREF-05"
    verification:
      - kind: unit
        ref: "uv run pytest -q (1349 passed, 5 skipped, 0 failed)"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-16
status: complete
---

# Phase 55 Plan 01: XREF-05 Label Collision Fix Summary

**Made `_sanitize_label` injective by re-escaping its own encoding token's introducing underscore, closing the label-collision false negative XREF-05 measured pre-fix on a real two-master `sphinx-build -b typstpdf` + `typst.compile()`, and proved the construction general by an exhaustive decoder round-trip over 66,430 adversarial strings plus 20,000 seeded-random strings.**

## Performance

- **Duration:** ~25 min
- **Tasks:** 3 (Task 1 tracer, Task 2 auto/tdd, Task 3 auto)
- **Files modified/created:** 6 (1 production, 3 test, 1 fixture comment block, 1 evidence artifact)

## Accomplishments

- `_sanitize_label` (`typsphinx/translator.py`) is now injective: a new module-level compiled
  pattern `_LABEL_TOKEN_INTRODUCER_RE` (`_(?=u[0-9a-f]+(?:_|[^A-Za-z0-9_.:-]))`) runs as a pre-pass
  before the existing character-class substitution, re-escaping any literal occurrence of the
  encoder's own `_u<hex>_` token shape via its introducing underscore (replacement `_u5f_` — itself
  exactly what the encoder emits for a literal underscore, since `ord("_") == 0x5f`, so no second
  escaping primitive is introduced).
- On the real two-master compile: `a/b:nested-target` still sanitizes to `a_u2f_b:nested-target`
  (the reference side, unmoved) while `a_u2f_b:nested-target` (the decoy's own raw id) now
  sanitizes to `a_u5f_u2f_b:nested-target` — the two docnames that used to collide now produce
  distinct labels, and the compiled `manual.pdf`'s link destinations no longer include the
  formerly-colliding spelling.
- `test_label_collision_guard_links_to_decoy` inverted to
  `test_label_collision_no_longer_links_to_decoy`; the fixture's `conf.py` comment block re-framed
  to stop describing an accepted limit and gained property (e) pinning the decoy's new label.
- Injectivity proven in general (not merely on the one fixture) by
  `tests/test_sanitize_label_injectivity_unit.py`: a test-only `_decode_label` helper recovers the
  original raw input from every sanitized output, verified over an exhaustive product across a
  9-character adversarial alphabet (lengths 0–5, 66,430 strings) plus 20,000 seeded-random strings
  (length 0–14) from a wider pool including Unicode, whitespace, quotes and backslashes — runs in
  under 0.3s.
- Both constructions the phase's own research/pattern documents proposed are pinned as REJECTED by
  their measured counterexamples: leading-underscore doubling collides `a_/b` with `a_u2f_b`
  (both → `a__u2f_b`); the extra-`u` repair collides `_u2f/` with `/u2f_` (both → `_u2f_u2f_`).
  This construction keeps all four pairs distinct.
- Full-suite churn scope measured, not assumed: `find tests examples docs -type f | grep -E
  '_u[0-9a-f]+_'` returns exactly one path
  (`tests/fixtures/xref_label_collision_guard_gate/a_u2f_b.rst`) both pre- and post-fix.
- Pre-fix link-to-decoy behaviour recorded verbatim against the real pre-fix commit
  (`3d8bdb10eb475c53666abab494d3cbf524eb6ff5`) in `55-01-RED-EVIDENCE.md` before any product edit
  (binding constraint #6), including the sorted destination list from a direct two-master compile.

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end "a collided label no longer links to a decoy"** — `026af474` (feat)
2. **Task 2: Prove the construction injective in general** — `9dda7fef` (test)
3. **Task 3: Full-suite sweep for label-byte churn** — `a1355adb` (docs)

_Task 1 carried this phase's tracer slice — a real end-to-end path from raw docname through
`_sanitize_label` to compiled PDF link destinations, production-quality from the start; Tasks 2 and
3 expand outward from that proven slice (unit-level injectivity proof, then full-suite/churn
measurement) rather than replacing any of it._

## Files Created/Modified

- `typsphinx/translator.py` — `_LABEL_TOKEN_INTRODUCER_RE` module-level constant; the pre-pass
  branch inside `_sanitize_label`; extended docstring recording the injectivity property and both
  rejected constructions.
- `tests/test_xref_compile_time_guard_render_gate.py` — inverted
  `test_label_collision_guard_links_to_decoy` → `test_label_collision_no_longer_links_to_decoy`;
  `collision_guard_build` fixture extended to also read `a_u2f_b.typ` (the decoy's own included
  content file).
- `tests/fixtures/xref_label_collision_guard_gate/conf.py` — comment block re-framed to describe a
  CLOSED defect; added property (e).
- `tests/test_sanitize_label_injectivity_unit.py` — new: the exhaustive/random injectivity proof
  suite, the test-only `_decode_label` decoder, both rejected-construction counterexample classes,
  boundary probes, and the empty/single-element and encoding edge probes.
- `tests/test_label_existence_guard_unit.py` — `TestNoAttachment` docstring updated to record the
  collision as CLOSED by XREF-05 (was "accepted as a limit in 48-04"); its literal probe label
  updated to `a_u5f_u2f_b:nested-target` (the fixture's real post-fix spelling).
- `.planning/phases/55-v0-8-0-derived-defects/55-01-RED-EVIDENCE.md` — new: pre-fix pytest and
  real-compile transcripts (Task 1), plus the post-fix churn/full-suite measurement (Task 3).

## Decisions Made

- Escaped the encoder's own token-INTRODUCING underscore via a lookahead regex pre-pass, rather
  than the two constructions the phase's research/pattern documents proposed (both measured
  non-injective this session — see counterexamples above). The lookahead means the pre-pass and the
  main substitution never have to agree on where a token-shaped run ends; only the introducing `_`
  is replaced.
- Extended `collision_guard_build`'s pytest fixture to read `a_u2f_b.typ` in addition to
  `index.typ`, since the decoy's own re-escaped anchor label is emitted in its own included content
  file, not the master's wrapper. (Discovered when the first draft of the inverted test asserted the
  new label against the wrong file and failed — fixed inline, no scope change.)
- The visible reference text assertion added to the inverted test checks for "Alpha Nested Section"
  (the label's real target's title, resolved by Sphinx's own domain data at build time) rather than
  the decoy's title "Nested Target" — verified against the fixture's actual `.rst` source before
  writing the assertion.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Inverted test initially asserted the decoy's new label against the wrong emitted file**
- **Found during:** Task 1 (Step C, writing the inverted test's new assertions)
- **Issue:** The plan's action text says to add an assertion that "the emitted `index.typ` contains
  the decoy's new anchor label `a_u5f_u2f_b:nested-target`" — but the decoy's own anchor is emitted
  in its own included content file (`a_u2f_b.typ`), not the master's `index.typ`. A first-draft
  assertion against `index_typ` failed immediately (the label genuinely isn't there).
- **Fix:** Extended the `collision_guard_build` fixture to also read and return `a_u2f_b.typ`'s
  text, and asserted the new label against that file instead.
- **Files modified:** `tests/test_xref_compile_time_guard_render_gate.py`
- **Verification:** `uv run pytest tests/test_xref_compile_time_guard_render_gate.py -k collision -x -q` passes.
- **Committed in:** `026af474` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** No scope creep — the fix keeps the plan's own stated intent (assert the decoy's
new label is emitted) while correcting which file it's emitted into.

## Issues Encountered

`uv run ruff check .` fails to exec on this NixOS worktree (`Could not start dynamically linked
executable: ruff` — a pre-existing, project-known environment hazard per `nixos-sandbox-test-env`
memory notes, unrelated to this plan). Worked around by invoking the nix-store-provided binary
directly (`/nix/store/rxq02ylzcbjpzk7k9s8n4y4xwlznm0zr-ruff-0.15.14/bin/ruff`), which produced the
identical clean result ("All checks passed!") the plan's `<verify>` block requires. Recorded in
`55-01-RED-EVIDENCE.md`'s churn-scope section so the workaround is visible alongside the result it
produced.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- XREF-05 fully closed: `_sanitize_label` injective, proven by property suite, verified end-to-end
  on a real compile, churn scope measured at exactly one fixture path, full suite green.
- `typsphinx/translator.py` is the only production file this plan touched (confirmed via
  `git diff --stat` against the plan's base commit) — leaves `translator.py` clear for `55-02`
  (BLD-07/BLD-08, also `translator.py`) in the next wave with no file-contention carryover beyond
  what the wave map already scheduled.
- `_LABEL_TOKEN_INTRODUCER_RE` and the injectivity proof pattern established here
  (`tests/test_sanitize_label_injectivity_unit.py`'s exhaustive-plus-random decoder round-trip) are
  available as a reference shape for `55-02`'s own injectivity requirement on
  `make_include_edge_key`'s separator escaping (BLD-07), should that plan want the same proof rigor.
- No blockers for `55-02`/`55-03` (Wave 2) or `55-04` (Wave 3).

## Self-Check: PASSED

All created/modified files exist and all four task/plan commit hashes
(`026af474`, `9dda7fef`, `a1355adb`, `7cc74da7`) resolve in `git log --oneline --all`.

---
*Phase: 55-v0-8-0-derived-defects*
*Completed: 2026-08-16*
