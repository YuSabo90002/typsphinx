---
phase: 15-full-corpus-validation
plan: 01
subsystem: testing
tags: [pytest, sphinx, typst, git-clone, corpus-validation, slow-marker]

# Dependency graph
requires:
  - phase: 11-14
    provides: TypstPDFBuilder, the GATE-01 sys.executable -m sphinx subprocess
      pattern, and the full translator.py node-handler surface this gate
      exercises end-to-end
provides:
  - "tests/test_corpus_gate.py: a new slow-marked pytest module that
    shallow-clones Sphinx's own doc/ tree at the tag matching the installed
    sphinx.__version__, wires typsphinx into the real conf.py, builds the
    FULL tree through -b typstpdf, and asserts no fatal TypstCompilationError
    (GATE-02 SC#1) plus a frequency-ranked unknown_visit catalogue (SC#2)"
affects: [15-02, 15-03]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Session-scoped, cache-by-tag git clone fixture with pytest.skip
      (never fail) on unavailability"
    - "conf.py augmentation via idempotent append-mode write, never
      overlay/replace"
    - "Corpus-scale real-compile gate reusing the GATE-01
      sys.executable -m sphinx subprocess convention, generalized to a
      builder parameter"

key-files:
  created: [tests/test_corpus_gate.py]
  modified: []

key-decisions:
  - "D-01..D-05 all encoded exactly as researched: shallow clone at
    f\"v{sphinx.__version__}\" cached by tag, full doc/ tree (no subset),
    real conf.py augmented by a 2-line idempotent append, slow-marked class
    excluded from the fast/CI suite, pytest.skip (never fail) on
    unavailable corpus"
  - "SC#1 assertion keys on outdir/index.pdf existing/non-empty/%PDF magic
    bytes -- never returncode == 0 alone (RESEARCH Pitfall 1: a missing
    typst_documents entry makes TypstPDFBuilder.finish() silently no-op)"
  - "UNKNOWN_NODE_RE anchors on ^WARNING: unknown node type: <(\\w+) with
    re.MULTILINE -- immune to both multi-line node dumps and prose false
    positives (RESEARCH Pitfall 4)"
  - "typst import in the TYPST_AVAILABLE try/except carries a # noqa: F401
    (matches the existing convention in typsphinx/pdf.py's
    check_typst_available) since the actual compile happens inside the
    sphinx-build subprocess, not via a direct typst.compile() call in this
    module"

patterns-established:
  - "Corpus-scale gate: clone/cache -> idempotent conf-augment ->
    parameterized sys.executable -m sphinx subprocess -> PDF
    exists/non-empty/%PDF triple -- reusable for any future full-tree
    real-world validation gate"

requirements-completed: [GATE-02]

coverage:
  - id: D1
    description: "tests/test_corpus_gate.py scaffolding (clone/cache,
      idempotent conf-augment, parameterized subprocess helper, and the
      re.MULTILINE-anchored unknown_visit catalogue parser) exists and is
      unit-tested"
    requirement: GATE-02
    verification:
      - kind: unit
        ref: "tests/test_corpus_gate.py::test_catalogue_unknown_visit_multiline"
        status: pass
      - kind: other
        ref: "pytest tests/test_corpus_gate.py --collect-only -q"
        status: pass
    human_judgment: false
  - id: D2
    description: "TestCorpusRenderGate (slow-marked) drives a real
      sphinx-build -b typstpdf of Sphinx's own full doc/ tree and asserts
      the SC#1 fatal-free PDF triple, with the SC#2 catalogue printed as a
      byproduct"
    requirement: GATE-02
    verification:
      - kind: integration
        ref: "pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s (network required)"
        status: fail
    human_judgment: true
    rationale: "The slow gate is designed to only be meaningful with network
      access to clone the real corpus. In this execution, network happened
      to be available and the gate ran for real (did not skip) -- and
      correctly caught a genuine PRE-EXISTING fatal bug in TypstBuilder's
      asset handling (missing _static/python-logo.png), unrelated to this
      plan's own changes and out of this plan's files_modified scope
      (tests/test_corpus_gate.py only). Whether/how to fix that builder bug
      is a judgment call for a follow-up plan/phase, not something this
      plan's scope covers -- flagging for human review rather than
      auto-fixing an out-of-scope production-code path."

# Metrics
duration: 15min
completed: 2026-07-12
status: complete
---

# Phase 15 Plan 01: Corpus Render Gate Scaffolding Summary

**New `tests/test_corpus_gate.py` slow-marked pytest module that shallow-clones Sphinx's own `doc/` tree, wires in typsphinx, builds the full tree through `typstpdf`, and asserts the fatal-free PDF triple plus a frequency-ranked `unknown_visit` catalogue.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-07-12T16:04:00+09:00 (approx.)
- **Completed:** 2026-07-12T16:19:00+09:00
- **Tasks:** 2
- **Files modified:** 1 (new)

## Accomplishments

- Created `tests/test_corpus_gate.py` (new sibling module, not appended to `test_pdf_render_gate.py` per RESEARCH Pitfall 5), containing:
  - `resolve_corpus_tag()` — returns `f"v{sphinx.__version__}"` (D-01)
  - `get_or_clone_corpus(cache_root)` — shallow clone + cache-by-tag, returns `Path | None`, never raises (D-01/D-05)
  - `corpus_doc_dir` — session-scoped fixture, `pytest.skip`s on unavailable corpus (D-05, Pitfall 3)
  - `wire_typsphinx_into_corpus_conf(corpus_doc_dir)` — idempotent 2-line append to the real `doc/conf.py` (D-03)
  - `_run_corpus_sphinx_build(builder, source_dir, build_dir, env=None)` — parameterized `sys.executable -m sphinx` subprocess helper
  - `UNKNOWN_NODE_RE` / `catalogue_unknown_visit(stderr_text)` — `re.MULTILINE`-anchored `unknown_visit` frequency parser (SC#2)
  - `test_catalogue_unknown_visit_multiline` — fast unit test proving the parser correctly handles a multi-line node dump, a nested-child double-count, and a prose false-positive immunity case
  - `TestCorpusRenderGate` (`@pytest.mark.slow`) — `test_corpus_compiles_with_no_fatal_error` builds the FULL corpus via `-b typstpdf`, asserts `outdir/index.pdf` exists/non-empty/`%PDF` (never `returncode == 0` alone), logs the resolved tag + clone commit SHA, and prints the SC#2 catalogue under the `Unknown Visit Catalogue:` label
- Verified the module collects cleanly and the fast unit test passes.
- Verified the full fast suite (389 tests, excluding the 4 known-environmentally-bad integration files) stays green with the new module included.
- Verified `black`/`ruff` clean on the new file; `mypy typsphinx/` unaffected (no production code touched).
- **In-sandbox network happened to be available**, so the slow gate ran for real (rather than skipping) and correctly caught a genuine pre-existing fatal bug — see Deviations below.

## Task Commits

Each task was committed atomically:

1. **Task 1: Scaffold tests/test_corpus_gate.py — clone/cache + conf-augment + subprocess + catalogue parser** - `f49d39c` (test)
2. **Task 2: TestCorpusRenderGate — SC#1 full-corpus typstpdf fatal-free build + SC#2 catalogue byproduct** - `19cdceb` (test)

**Plan metadata:** (this commit)

## Files Created/Modified

- `tests/test_corpus_gate.py` - New GATE-02 corpus render gate module (clone/cache, conf-augment, subprocess, catalogue parser, fast unit test, `TestCorpusRenderGate` slow class)

## Decisions Made

- Split the single new file into two atomic commits matching the plan's two tasks (Task 1's helpers/parser/fast-test, Task 2's `TestCorpusRenderGate` class), using a staged partial-content approach since `git add -p` on a brand-new untracked file does not cleanly split by hunk.
- Added `# noqa: F401` to the `import typst` inside the `TYPST_AVAILABLE` try/except, matching the existing convention in `typsphinx/pdf.py::check_typst_available` — the actual PDF compile happens inside the `sphinx-build` subprocess (via `TypstPDFBuilder.finish()`), not via a direct `typst.compile()` call in this test module, so the import is availability-check-only.

## Deviations from Plan

None from the plan's own scope — both tasks were executed exactly as specified (D-01 through D-05 all encoded, SC#1/SC#2 assertion shapes match the researched pattern exactly).

### Notable Finding (not a deviation — no code fix applied, out of plan scope)

**In-sandbox network was available**, so `pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s` was run manually as an extra check beyond this plan's required autonomous verification (fast unit test + `--collect-only` + fast suite). The gate did NOT skip (D-05's skip path was not exercised) — it cloned the real corpus, wired in typsphinx, and ran a real `sphinx-build -b typstpdf`. The build reached `TypstPDFBuilder.finish()`'s `typst.compile()` call and hit a genuine fatal error:

```
Typst compilation failed at .../_build/tmp....typ: TypstError: file not found
  (searched at .../_build/_static/python-logo.png)
```

This is exactly the class of finding GATE-02 exists to surface (per D-06, "this report is the next milestone's backlog input"). It is a **pre-existing bug in `typsphinx/builder.py`'s image/static-asset copying** (not caused by this plan's changes — `files_modified` for this plan is `tests/test_corpus_gate.py` only, no `typsphinx/` production files were touched), surfacing only now because the full 154-file Sphinx `doc/` corpus references a static theme image (`_static/python-logo.png`) that `TypstBuilder.copy_image_files()` apparently does not track/copy (it's referenced outside `env.images`, likely via a substitution/raw reference the existing image-copy pass doesn't walk).

**Not auto-fixed** per the deviation-rule scope boundary ("Only auto-fix issues DIRECTLY caused by the current task's changes... Pre-existing warnings/failures in unrelated files are out of scope") and per this phase's own Architectural Responsibility Map (RESEARCH.md: "Test/CI scaffolding" tier only, "no translator.py behavior changes" — `typsphinx/builder.py`'s asset-copy pipeline was equally out of scope). Investigating/fixing the static-asset copy gap is a judgment call that likely needs its own root-cause investigation (Rule 4 territory: is it a missing `env.images` registration for theme-referenced-only assets, or a `html_static_path` vs. `_static` handling gap?) and is flagged here for the human/Plan 03's `15-CORPUS-REPORT.md` or a follow-up phase, rather than fixed inline.

This does not affect this plan's own success criteria (creating the gate, all D-01..D-05 encoded, fast suite green) — it demonstrates the gate works exactly as designed: it fails loudly on a real fatal compile error rather than passing trivially.

## Issues Encountered

None beyond the finding documented above.

## User Setup Required

None - no external service configuration required. (Network access to `github.com` is required to actually exercise `TestCorpusRenderGate` outside the skip path; this is expected per D-05 and requires no setup, just connectivity.)

## Next Phase Readiness

- `tests/test_corpus_gate.py` is ready for Plan 02 to extend with `checkout_pre_fix_translator`, `count_empty_url_warnings`, `FIX_COMMIT`, and `test_empty_url_before_after` (D-07 before/after measurement).
- Plan 03 can transcribe this plan's SC#2 catalogue (captured via the `Unknown Visit Catalogue:` stdout label) into `15-CORPUS-REPORT.md`.
- **Flag for Plan 03 / a follow-up phase:** the discovered `_static/python-logo.png` missing-asset fatal should be logged in `15-CORPUS-REPORT.md`'s findings and considered for a dedicated fix phase — it currently blocks SC#1 from passing against the real corpus (the gate correctly fails, which is by design, but the milestone's ultimate goal of a fatal-free corpus compile is not yet achieved).

---
*Phase: 15-full-corpus-validation*
*Completed: 2026-07-12*

## Self-Check: PASSED

- FOUND: tests/test_corpus_gate.py
- FOUND: f49d39c (Task 1 commit)
- FOUND: 19cdceb (Task 2 commit)
