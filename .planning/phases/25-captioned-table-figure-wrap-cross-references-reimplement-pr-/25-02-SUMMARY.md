---
phase: 25-captioned-table-figure-wrap-cross-references-reimplement-pr
plan: 02
subsystem: testing
tags: [typst, docutils, table, figure, cross-reference, render-gate, typst.compile, pypdf]

# Dependency graph
requires:
  - phase: 25-01 (captioned-table figure-wrap translator fix)
    provides: "depart_table figure-wrap + single <label> anchor emission (TBL-01/TBL-02), shipped and merged into this worktree's base"
provides:
  - "GATE-01 real-compile regression fixture proving the shipped Plan 25-01 translator fix compiles green end-to-end: 2+ captioned tables (stale-buffer proof), caption+:width: composition, :numref:/:ref:-resolves, captioned csv-table/list-table (D-05)"
  - "Durable fail-pre-fix red->green proof (D-06) reconstructing the double-anchor and stale-buffer defect shapes from first principles, independent of the (now-deleted) buggy code"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Class-scoped real-compile artifact fixture returning a small plain container (typ_source + full_text) so multiple thin test methods assert disjoint slices of ONE sphinx-build/typst.compile() run, rather than re-running the pipeline per method (topic_line_block_render_gate_pdf_text precedent)."
    - "Reconstruct-the-pre-fix-basis-from-first-principles convention (TestPreFixBasisFailureProof precedent): after the buggy code is deleted, the fail-pre-fix proof survives by hand-assembling the defect's exact Typst/text shape rather than depending on removed source."

key-files:
  created:
    - tests/fixtures/captioned_table_render_gate/conf.py
    - tests/fixtures/captioned_table_render_gate/index.rst
  modified:
    - tests/test_pdf_render_gate.py

key-decisions:
  - "The :ref: role in the fixture must supply EXPLICIT link text (:ref:`Ref Link <first-table>`) rather than a bare :ref:`first-table` -- a bare :ref: to a captioned table defaults its link text to the target's OWN caption text, which would make that caption's sentinel appear a SECOND time in the extracted PDF and break the exactly-once assertion (discovered empirically via a real compile during authoring, not anticipated by the plan text)."
  - ":numref: must be used BARE (:numref:`first-table`, no custom <link text>) -- supplying arbitrary custom text (e.g. :numref:`Numref Link <first-table>`) is invalid numfig_format syntax (Sphinx requires a %s substitution placeholder for custom numref text) and silently degrades to a raw, unlinked text token instead of raising -- discovered empirically via a real compile."
  - "The double-anchor pre-fix-basis test needed an explicit link(<dup>, ...) reference resolving the duplicated label, not merely two <dup> definitions with no reference -- live-verified that Typst does NOT raise 'label occurs multiple times' merely from a duplicate definition; the fatal fires only when something tries to RESOLVE the ambiguous label, matching the real :numref:/:ref: xref shape that triggered the original bug."
  - "The two tasks were committed via a temporary truncate-then-restore of tests/test_pdf_render_gate.py (backed up before editing, truncated to Task 1's exact line boundary for the first commit, then restored in full for the second) rather than a partial git add -p, since both tasks land in the same file and the destructive-git-prohibition rules out git stash for this purpose."

patterns-established: []

requirements-completed: [TBL-01, TBL-02]

coverage:
  - id: D1
    description: "Real sphinx-build -> typst.compile() -> pypdf gate proves 2+ consecutive captioned tables each keep their own caption exactly once (stale-buffer fix), no stray heading() in the captioned-table region, and figure(..., kind: table) native numbering"
    requirement: "TBL-01"
    verification:
      - kind: unit
        ref: "tests/test_pdf_render_gate.py::TestCaptionedTableRenderGate::test_each_caption_sentinel_appears_exactly_once"
        status: pass
      - kind: unit
        ref: "tests/test_pdf_render_gate.py::TestCaptionedTableRenderGate::test_typ_source_uses_figure_kind_table_with_no_heading_above"
        status: pass
      - kind: unit
        ref: "tests/test_pdf_render_gate.py::TestCaptionedTableRenderGate::test_no_literal_source_leak"
        status: pass
    human_judgment: false
  - id: D2
    description: "A :numref:/:ref: cross-reference to a captioned table resolves to a real link(<label>, ...) anchor in a real compile, with no link(\"\", ...) leak and no duplicate/dangling-label fatal (TBL-02, Critical Pitfall 3)"
    requirement: "TBL-02"
    verification:
      - kind: unit
        ref: "tests/test_pdf_render_gate.py::TestCaptionedTableRenderGate::test_xref_numref_ref_resolve_no_empty_link"
        status: pass
    human_judgment: false
  - id: D3
    description: "Durable fail-pre-fix red->green proof (D-06): a reconstructed double-anchor Typst source (with a resolving link(<dup>, ...) xref) makes typst.compile() raise, and a reconstructed stale-buffer basis has its second caption sentinel count == 0"
    verification:
      - kind: unit
        ref: "tests/test_pdf_render_gate.py::TestCaptionedTablePreFixBasisFailureProof::test_double_anchor_basis_raises"
        status: pass
      - kind: unit
        ref: "tests/test_pdf_render_gate.py::TestCaptionedTablePreFixBasisFailureProof::test_stale_buffer_basis_second_sentinel_count_is_zero"
        status: pass
    human_judgment: false

# Metrics
duration: 23min
completed: 2026-07-23
status: complete
---

# Phase 25 Plan 02: Captioned Table Figure Wrap + Cross-References (real-compile GATE-01 gate) Summary

**Real `sphinx-build -> typst.compile() -> pypdf` GATE-01 fixture proves the shipped Plan 25-01 translator fix compiles green end-to-end — every captioned-table caption survives exactly once (including the previously stale-buffer-lost 2nd table), `:numref:`/`:ref:` resolve with no duplicate/dangling-label fatal, and a durable fail-pre-fix proof reconstructs both original defect shapes from first principles.**

## Performance

- **Duration:** ~23 min
- **Started:** 2026-07-23T15:05Z (worktree base e3a03108ef280332c2423261f30d2cb7a36e43ae)
- **Completed:** 2026-07-23T15:28Z
- **Tasks:** 2/2 completed
- **Files modified:** 3 (`tests/fixtures/captioned_table_render_gate/conf.py` [new], `tests/fixtures/captioned_table_render_gate/index.rst` [new], `tests/test_pdf_render_gate.py`)

## Accomplishments

- Real-compile fixture (`tests/fixtures/captioned_table_render_gate/`) with two consecutive `.. table::` captions (the stale-buffer proof — the 2nd table's caption cannot be exposed by a single-table fixture), one `.. table::` composing a caption with `:width: 50%`, a `:numref:`/`:ref:`-resolves paragraph, and a captioned `.. csv-table::` + `.. list-table::` pair (D-05).
- `captioned_table_render_gate_artifacts` class-scoped fixture runs `sphinx-build -b typst` -> `typst.compile()` -> pypdf text-extraction exactly once per class (mirroring the existing `topic_line_block_render_gate_pdf_text` idiom), returning both the emitted `.typ` source and the extracted PDF text for four thin test methods to assert against.
- `TestCaptionedTableRenderGate` (4 tests): each of the five caption sentinels appears exactly once in the extracted PDF text; the emitted `.typ` contains `figure(` + `kind: table` with no stray `heading(` in the captioned-table region; `link(<` is present and `link("",` is absent (proving the xref resolves); no `LEAK_SIGNATURES` token leaks.
- `TestCaptionedTablePreFixBasisFailureProof` (2 tests): a reconstructed double-anchor Typst source (a `<dup>` label defined twice, with a `link(<dup>, ...)` xref actually resolving it) makes a real `typst.compile()` raise; a reconstructed pre-fix stale-buffer two-table shape has its second caption sentinel's count at 0, proving the positive gate's `count(...) == 1` assertion is genuinely fail-pre-fix.
- Verified end-to-end: `uv run pytest tests/test_pdf_render_gate.py -k Captioned -x` (6 tests) green; the whole `tests/test_pdf_render_gate.py` file (30 tests) green; the full suite `uv run pytest -q` shows the same pre-existing 45 environmental failures documented for this worktree (all in `test_integration_{advanced,basic,multi_doc,nested_toctree}.py`/`test_examples_basic.py`, unrelated to this plan) with 550 passed, 1 skipped — identical to the pre-change baseline, i.e. zero regressions.
- `black --check tests/`, `mypy typsphinx/`, and `ruff check` (via the documented `nix-shell -p ruff` NixOS fallback) all clean. `templates/base.typ` untouched, `tests/test_preview_version_sync.py` green, no new runtime dependency.

## Task Commits

Each task was committed atomically:

1. **Task 1: captioned_table_render_gate fixture + TestCaptionedTableRenderGate (real compile)** — `7a9fd09` (test)
2. **Task 2: TestCaptionedTablePreFixBasisFailureProof (durable fail-pre-fix proof)** — `62f5ec6` (test)

_Both tasks land in the same file (`tests/test_pdf_render_gate.py`); since both classes were authored together during fixture development/iteration, the two commits were produced by backing up the fully-edited file, truncating it to Task 1's exact class boundary for the first commit (verified green in isolation: `-k CaptionedTableRenderGate` and the whole-file run both passed against the truncated version), then restoring the full file for Task 2's commit — never via `git stash` (prohibited in worktree mode) or a partial `git add -p`._

## Files Created/Modified

- `tests/fixtures/captioned_table_render_gate/conf.py` — minimal Sphinx config: `project`/`author`/`release`, `extensions = ["typsphinx"]`, `typst_documents` master tuple, `numfig = True` (Pitfall 4 — cleanest warning-free `:numref:` resolution)
- `tests/fixtures/captioned_table_render_gate/index.rst` — 5 captioned constructs (2 plain `.. table::`, 1 caption+`:width:` `.. table::`, 1 captioned `.. csv-table::`, 1 captioned `.. list-table::`) plus a `:numref:`/`:ref:` cross-reference paragraph
- `tests/test_pdf_render_gate.py` — new `captioned_table_render_gate_dir` fixture; new `_CaptionedTableRenderGateArtifacts` container + `captioned_table_render_gate_artifacts` class-scoped fixture; new `TestCaptionedTableRenderGate` class (4 tests); new `TestCaptionedTablePreFixBasisFailureProof` class (2 tests); 5 new sentinel constants (`TBLCAP_FIRST_SENTINEL`, `TBLCAP_SECOND_SENTINEL`, `TBLCAP_WIDTH_SENTINEL`, `TBLCAP_CSV_SENTINEL`, `TBLCAP_LIST_SENTINEL`)

## Decisions Made

- Split `TestCaptionedTableRenderGate` into four thin, disjoint-assertion methods (sentinel counts / figure+heading region / xref link presence / leak signatures) sharing one class-scoped compile artifact, rather than one large test method — matches the `TestTopicLineBlockRenderGate` precedent and keeps each failure message specific to its one concern.
- Used `typ_source.index("figure(")` to slice the "captioned-table region" for the no-stray-`heading(` assertion, rather than asserting zero `heading(` occurrences document-wide — the fixture's own top-level document title legitimately emits one `heading(` call before any table, and the plan's SC#1 wording ("no rendered section heading above the tables") is precisely about the table-caption region, not the unrelated document title.
- See `key-decisions` in frontmatter for the three empirically-discovered fixture/proof corrections (the `:ref:` explicit-text requirement, the `:numref:` bare-role requirement, and the double-anchor basis needing a resolving `link(<dup>, ...)` reference) — all found via real `typst.compile()`/`sphinx-build` runs during authoring, not assumed from the plan text alone.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixture initially double-counted `TBLCAPFIRSTSENTINEL`**
- **Found during:** Task 1 (manual smoke-build verification before wiring pytest code)
- **Issue:** The plan's action text describes `:numref:`/`:ref:` proving resolution, but a bare `:ref:`\`first-table\`` defaults its link text to the target's own caption text (Sphinx behavior) — this made `TBLCAPFIRSTSENTINEL` appear twice in the extracted PDF, which would have made the gate's own `count(...) == 1` assertion permanently red for a correct implementation (a self-inflicted false negative, not a translator regression).
- **Fix:** Rewrote the fixture's cross-reference paragraph to use explicit `:ref:`\`Ref Link <first-table>\`` text and bare `:numref:`\`first-table\`` (an earlier attempt at custom `:numref:` text was itself invalid numfig_format syntax and silently degraded to unlinked raw text — reverted to the bare form).
- **Files modified:** `tests/fixtures/captioned_table_render_gate/index.rst`
- **Verification:** Re-ran the manual `sphinx-build -b typst` + `typst.compile()` + pypdf smoke check; confirmed `full_text.count("TBLCAPFIRSTSENTINEL") == 1` and both cross-references still emit `link(<index:first-table>, ...)`.
- **Committed in:** `7a9fd09` (Task 1 commit; the fixture was corrected before it was ever committed, so no separate fix-up commit was needed).

**2. [Rule 1 - Bug] Double-anchor pre-fix-basis reconstruction needed a resolving reference**
- **Found during:** Task 2 (writing `test_double_anchor_basis_raises`)
- **Issue:** An initial reconstruction defined the label `<dup>` twice with no reference to it anywhere; a real `typst.compile()` on that source compiled successfully (Typst does not eagerly validate duplicate label definitions — only the act of resolving/linking to an ambiguous label raises "label ... occurs multiple times"). A test asserting `pytest.raises` against this shape would have been permanently false-green (never actually raising), defeating the purpose of the fail-pre-fix proof.
- **Fix:** Added an explicit `link(<dup>, ...)` reference in the reconstructed source (mirroring the real `:numref:`/`:ref:` xref shape that triggers the original bug) so the fatal genuinely fires.
- **Files modified:** `tests/test_pdf_render_gate.py`
- **Verification:** Manually confirmed via an ad hoc Python/typst.compile() smoke check (outside pytest) that the no-reference version compiles silently while the with-reference version raises `TypstError: label \`<dup>\` occurs multiple times in the document`; the shipped test asserts only `pytest.raises(Exception)` (D-06 — no message-text matching).
- **Committed in:** `62f5ec6` (Task 2 commit; corrected before the test was ever committed).

---

**Total deviations:** 2 auto-fixed (both Rule 1 — bugs in the test fixture/reconstruction discovered via real-compile verification during authoring, not translator regressions; both corrected before their respective commits, so neither left a red state in git history).
**Impact on plan:** Both corrections were necessary to make the gate assert what it was actually designed to prove (exactly-once caption survival; a genuinely-raising double-anchor fatal). No scope creep — no new files beyond the two named in the plan's `files_modified`, no architectural changes, no new runtime dependency.

## Issues Encountered

None beyond the two auto-fixed items above (both caught and resolved during fixture/proof authoring, before any commit).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Phase 25's D-06 mandatory real-compile bar is now fully discharged: Plan 25-01 shipped the translator-layer fix (unit-proven), and this plan (25-02) proves it compiles green end-to-end via a real `sphinx-build -> typst.compile() -> pypdf` round-trip, with a durable fail-pre-fix proof that survives the deletion of the original buggy code.
- `uv run pytest tests/test_pdf_render_gate.py -k Captioned -x` (6/6) and the whole `tests/test_pdf_render_gate.py` file (30/30) are green; `uv run pytest -q` shows 550 passed / 45 pre-existing environmental failures (documented, unrelated to this plan) / 1 skipped — byte-identical failure count to the pre-plan baseline, confirming zero regressions.
- `black --check`/`mypy typsphinx/`/`ruff check` (nix-shell fallback) all clean; `templates/base.typ` untouched; `tests/test_preview_version_sync.py` green; no new runtime dependency.
- No blockers for this phase's completion. This was the final planned plan for Phase 25 per the 25-02-PLAN.md wave assignment (Wave 2, `depends_on: ["25-01"]`).

## Self-Check: PASSED

- FOUND: `tests/fixtures/captioned_table_render_gate/conf.py`
- FOUND: `tests/fixtures/captioned_table_render_gate/index.rst`
- FOUND: `.planning/phases/25-captioned-table-figure-wrap-cross-references-reimplement-pr-/25-02-SUMMARY.md`
- FOUND commit: `7a9fd09` (Task 1)
- FOUND commit: `62f5ec6` (Task 2)
- FOUND commit: `d237cae` (this SUMMARY)

---
*Phase: 25-captioned-table-figure-wrap-cross-references-reimplement-pr-*
*Completed: 2026-07-23*
