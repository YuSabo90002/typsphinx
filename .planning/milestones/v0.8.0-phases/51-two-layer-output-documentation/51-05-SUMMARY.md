---
phase: 51-two-layer-output-documentation
plan: 05
subsystem: docs
tags: [readme, sphinx, typst, documentation]

# Dependency graph
requires:
  - phase: 51-two-layer-output-documentation (plan 01)
    provides: "docs/source/user_guide/output_layout.rst — the page this plan links to and stays consistent with"
provides:
  - "README.md — corrected typst_documents claims (wrapper/content split) plus a link to output_layout.rst"
  - "examples/basic/README.md — corrected emitted-file list (basic-example.typ wrapper + index.typ content)"
  - "examples/advanced/README.md — corrected emitted-file list and the real state-guarded include emission"
affects: [51-06]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
actuals:
  tokens: 1356
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Publish only build-verified filenames in worked-example prose — every filename in this plan's edits was transcribed from a real uv run python -m sphinx -b typst build performed during execution, never predicted from source reading alone"

key-files:
  created: []
  modified:
    - README.md
    - examples/basic/README.md
    - examples/advanced/README.md

key-decisions:
  - "Did not touch examples/basic/conf.py or examples/advanced/conf.py — both already use collision-safe targets (basic-example.typ, advanced-example.typ) under the two-layer split, so only the READMEs needed correction (per phase_scope_fence)."

patterns-established: []

requirements-completed: [DOC-14]

coverage:
  - id: D1
    description: "README.md's typst_documents description states an entry produces a wrapper file plus a content file for its source document (not one emitted file), and the Configuration Options bullet says the target names the wrapper"
    requirement: "DOC-14"
    verification:
      - kind: unit
        ref: "tests/test_quickstart_docs_gate.py -q"
        status: pass
      - kind: other
        ref: "grep -c 'produces one emitted' README.md -> 0; grep -c 'wrapper' README.md -> 4"
        status: pass
    human_judgment: false
  - id: D2
    description: "README.md links to docs/source/user_guide/output_layout.rst inline (repo-relative) and in the documentation links list (RTD-absolute), with no worked example or two-layer explanation added to README.md itself"
    requirement: "DOC-14"
    verification:
      - kind: other
        ref: "grep -c 'output_layout' README.md -> 2; awk range typst_documents..Build Typst Output has 0 code-block markers"
        status: pass
    human_judgment: false
  - id: D3
    description: "examples/basic/README.md lists both .typ files a real build emits (basic-example.typ wrapper, index.typ content) and names which one to compile"
    requirement: "DOC-14"
    verification:
      - kind: unit
        ref: "tests/test_examples_basic.py -q"
        status: pass
      - kind: other
        ref: "grep -c 'with the Typst markup' -> 0; grep -c 'index.typ' -> 1; grep -c 'basic-example.typ' -> 2"
        status: pass
    human_judgment: false
  - id: D4
    description: "examples/advanced/README.md's generated-file list includes index.typ (master content), attributes chapter includes to the content file rather than the wrapper, and the Typst code block shows the real per-child compile-time state guard inside a relative heading-offset context"
    requirement: "DOC-14"
    verification:
      - kind: unit
        ref: "tests/test_integration_advanced.py -q"
        status: pass
      - kind: other
        ref: "grep -c 'directives to' -> 0; grep -c 'set heading(offset: 1)' -> 0; grep -c 'heading.offset + 1' -> 1; grep -c 'typsphinx:include-edges' -> 2 (verified against real index.typ build output)"
        status: pass
    human_judgment: false

# Metrics
duration: ~25min
completed: 2026-08-15
status: complete
---

# Phase 51 Plan 05: PyPI README and Bundled Example Walkthroughs Summary

**Corrected the false "one emitted .typ file per entry" claim in README.md's PyPI front page and rewrote both bundled example walkthroughs (`examples/basic/README.md`, `examples/advanced/README.md`) with real build-transcribed emitted-file lists, including the actual state-guarded compile-time include block replacing the stale unconditional `#include()` example.**

## Performance

- **Duration:** ~25 min active work
- **Tasks:** 2
- **Files modified:** 3

## Real Build Transcripts (per plan's mandatory-verbatim-transcript requirement)

Both builds were run via `uv run python -m sphinx -b typst <source> <build>` inside this
worktree, into `/tmp/claude-1000/.../scratchpad/build-{basic,advanced}` (outside the repository
working tree — nothing under `_build/` was committed).

**`examples/basic` build:**
```
$ find <tmpdir>/basic -name '*.typ' | sort
<tmpdir>/basic/_template.typ
<tmpdir>/basic/basic-example.typ
<tmpdir>/basic/index.typ
```
Log line: `typst: wrote 1 wrapper file(s) -- compile these: basic-example.typ`

**`examples/advanced` build:**
```
$ find <tmpdir>/advanced -name '*.typ' | sort
<tmpdir>/advanced/_template.typ
<tmpdir>/advanced/advanced-example.typ
<tmpdir>/advanced/chapter1.typ
<tmpdir>/advanced/chapter2.typ
<tmpdir>/advanced/index.typ
```
Log line: `typst: wrote 1 wrapper file(s) -- compile these: advanced-example.typ`

The published Typst code block in `examples/advanced/README.md` was verified against the real
emitted `index.typ`'s own lines 45-49 (read directly from the build output):
```
context {
  set heading(offset: heading.offset + 1)
  if "index#0>chapter1" in state("typsphinx:include-edges", ()).get() { include("chapter1.typ") }
  if "index#0>chapter2" in state("typsphinx:include-edges", ()).get() { include("chapter2.typ") }
}
```
This is byte-identical to what the plan's edit publishes (both formatting and the two edge-key
literals `index#0>chapter1` / `index#0>chapter2`).

## Accomplishments

- Rewrote README.md's Quick Start `typst_documents` paragraph (Row 9): no longer claims "one
  emitted `.typ` file" per entry; now states an entry produces a wrapper `.typ` at the entry's
  target plus a content file for its source document, and every other document in the project
  also gets a content file. Added a repo-relative inline link to
  `docs/source/user_guide/output_layout.rst`.
- Extended README.md's Configuration Options `typst_documents` bullet (Row 10) with "The target
  names the entry's wrapper file" for consistency, without restating the derivation rules.
- Added an `Output Layout` entry to README.md's RTD-absolute documentation links list, adjacent
  to `Configuration Reference`.
- Rewrote `examples/basic/README.md`'s emitted-file sentence (Row 11): now names both files a
  real build writes (`basic-example.typ` wrapper, `index.typ` content) and says which to
  compile; left the already-correct `typst compile _build/typst/basic-example.typ output.pdf`
  command untouched.
- Rewrote `examples/advanced/README.md`'s generated-file list and prose (Row 12): the list now
  includes `index.typ` (previously missing entirely), and the sentence attributes chapter
  inclusion to the content file rather than to the wrapper's own target filename.
- Replaced `examples/advanced/README.md`'s stale unconditional-include Typst code block (Row 13)
  with the real state-guarded compile-time emission — a relative `heading.offset + 1` context
  wrapping one `if "<edge-key>" in state("typsphinx:include-edges", ()).get() { include(...) }`
  guard line per chapter — plus one sentence explaining why the guard exists (a document shared
  by multiple masters renders once per master).

## Task Commits

Each task was committed atomically:

1. **Task 1: README.md — correct the two typst_documents claims and link out (D-03)** - `dc8359b4` (docs)
2. **Task 2: The bundled example walkthroughs — build them, then publish what they actually emit** - `5e8e1c01` (docs)

## Files Created/Modified

- `README.md` - Corrected Quick Start `typst_documents` paragraph, Configuration Options bullet, and documentation links list
- `examples/basic/README.md` - Corrected emitted-file sentence naming both `.typ` files a build writes
- `examples/advanced/README.md` - Corrected generated-file list, chapter-inclusion prose, and the state-guarded include code block

## Decisions Made

- Left `examples/basic/conf.py` and `examples/advanced/conf.py` unmodified, per the plan's
  `phase_scope_fence`: both already use collision-safe explicit targets
  (`basic-example.typ`, `advanced-example.typ`) that neither self-collide nor need changing
  under the two-layer split — only their READMEs carried false claims.
- Kept the RTD-absolute link form (matching README.md's existing `Configuration Reference` /
  `Quick Start` link-list precedent) for the standalone documentation-links entry, and the
  repo-relative form (matching the existing line 226 precedent) for the inline correction —
  both forms were already precedented in the file, so no new link convention was introduced.

## Deviations from Plan

None - plan executed exactly as written. Both example builds were run fresh in this worktree
(not assumed from RESEARCH.md's prior-session measurements) and matched RESEARCH.md's Part C
findings exactly, confirming no drift occurred between research time and execution time.

## Sites Checked and Deliberately NOT Changed (per plan's sweep_rows_owned_by_this_plan)

- `README.md:100-103` — the toctree-child paragraph ("A document reached only through a toctree
  is not a separate PDF...") — still true in outcome; D-03 scopes README to false-claim
  correction only, so left untouched (verified still present, count 1, after edits).
- `examples/basic/README.md:57` — `typst compile _build/typst/basic-example.typ output.pdf` —
  `basic-example.typ` IS the wrapper, so this was already correct; left untouched (verified
  still present after edits).
- `examples/charged-ieee/README.md:107,116` — `typst compile paper.typ output.pdf` — out of this
  plan's `files_modified` scope (owned by no plan in this wave); not touched, per the plan's own
  note that `charged-ieee`'s configs target `paper` and are correct as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All five `51-RESEARCH.md` Part A sweep rows owned by this plan (9-13) are fixed; none deferred.
- `examples/advanced/README.md`'s new code block is verified byte-identical to a real build's
  emitted `index.typ`, so 51-06's completeness audit over the whole sweep should find no gap in
  this plan's `examples/` share.
- README.md's `Output Layout` RTD link (`https://typsphinx.readthedocs.io/en/latest/user_guide/output_layout.html`)
  resolves only after the docs rebuild that follows a merge to `main`; the repository's lychee
  link check is advisory, so this is a recorded consequence per the plan's threat register
  (T-51-06), not a defect.

## Self-Check: PASSED

All modified files confirmed present on disk (`README.md`, `examples/basic/README.md`,
`examples/advanced/README.md`, this SUMMARY.md). Both commits (`dc8359b4`, `5e8e1c01`)
confirmed present in `git log`.

---
*Phase: 51-two-layer-output-documentation*
*Completed: 2026-08-15*
