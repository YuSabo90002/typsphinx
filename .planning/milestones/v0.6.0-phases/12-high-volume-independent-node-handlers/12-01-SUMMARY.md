---
phase: 12-high-volume-independent-node-handlers
plan: 01
subsystem: translator
tags: [sphinx, typst, docutils, translator, versionmodified, gate-01]

# Dependency graph
requires:
  - phase: 11-issue-114-fatal-fixes-graceful-degrade-net
    provides: the real-compile GATE-01 acceptance-fixture pattern (sphinx-build -> typst.compile() -> pypdf) this plan extends
provides:
  - "visit_versionmodified/depart_versionmodified transparent pass-through pair"
  - "visit_inline/depart_inline classed-dispatch branch for 'versionmodified' CSS class, delegating to visit_emphasis/depart_emphasis"
  - "version_modified_render_gate fixture project (all four version-directive kinds + content-less case)"
  - "TestVersionModifiedRenderGate real-compile test class extending GATE-01"
affects: [12-02-xref-refid-handlers, 12-03-desc-signature-handlers, 12-04-trivial-block-handlers]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Classed-inline dispatch: detect a Sphinx-baked CSS class on a generic nodes.inline and delegate to an existing visitor via a dummy node instance, rather than importing Sphinx-internal label maps"

key-files:
  created:
    - tests/fixtures/version_modified_render_gate/conf.py
    - tests/fixtures/version_modified_render_gate/index.rst
    - .planning/phases/12-high-volume-independent-node-handlers/deferred-items.md
  modified:
    - typsphinx/translator.py
    - tests/test_pdf_render_gate.py

key-decisions:
  - "No sphinx.domains.changeset.versionlabels import: Sphinx's VersionChange.run() already bakes the exact localized label wording into the doctree as a classed nodes.inline at parse time, so the translator only needs to detect the class and italicize it (supersedes 12-CONTEXT.md D-01's speculated import mechanism while honoring its intent)"
  - "Delegate the classed-inline styling to the existing visit_emphasis/depart_emphasis dummy-node idiom instead of writing new escaping/separator logic"

patterns-established:
  - "Classed-inline dispatch via dummy-node delegation (visit_inline detecting 'versionmodified' in node.get('classes', []))"

requirements-completed: [VER-01]

coverage:
  - id: D1
    description: "versionadded/versionchanged/deprecated/versionremoved render as unboxed italic label + inline body, matching Sphinx's own label wording, with no gentle-clues callout box"
    requirement: "VER-01"
    verification:
      - kind: unit
        ref: "tests/test_pdf_render_gate.py::TestVersionModifiedRenderGate::test_version_modified_pdf_has_labels_bodies_and_no_source_leak"
        status: pass
    human_judgment: false
  - id: D2
    description: "A content-less versionadded directive renders label-only, period-terminated; a content-bearing directive renders label + body"
    requirement: "VER-01"
    verification:
      - kind: unit
        ref: "tests/test_pdf_render_gate.py::TestVersionModifiedRenderGate::test_version_modified_pdf_has_labels_bodies_and_no_source_leak"
        status: pass
    human_judgment: false
  - id: D3
    description: "versionmodified pass-through pair silences the x972 unknown_visit warning without altering already-correct body rendering"
    requirement: "VER-01"
    verification:
      - kind: unit
        ref: "grep -q 'def visit_versionmodified' typsphinx/translator.py"
        status: pass
    human_judgment: false

# Metrics
duration: ~15min
completed: 2026-07-12
status: complete
---

# Phase 12 Plan 01: Version-Modified Directive Handling Summary

**Unboxed italic version-directive labels (`versionadded`/`versionchanged`/`deprecated`/`versionremoved`) rendered by detecting Sphinx's own classed inline, with a real-compile GATE-01 fixture proving all four kinds plus the content-less case.**

## Performance

- **Duration:** ~15 min
- **Tasks:** 3 completed
- **Files modified:** 3 (`typsphinx/translator.py`, `tests/test_pdf_render_gate.py`, plus 2 new fixture files and 1 deferred-items note)

## Accomplishments
- Added a transparent `visit_versionmodified`/`depart_versionmodified` pass-through pair to `typsphinx/translator.py`, silencing the ×972 unknown_visit warning (the child paragraph already renders correctly)
- Extended the existing `visit_inline`/`depart_inline` with a classed-dispatch branch: when `"versionmodified" in node.get("classes", [])`, delegate to `visit_emphasis`/`depart_emphasis` via a dummy `nodes.emphasis()` instance — inheriting the file's proven paragraph/list-item state machinery with zero new escaping logic, and with zero `sphinx.domains.changeset` import
- Created `tests/fixtures/version_modified_render_gate/` (conf.py + index.rst), a minimal self-contained Sphinx fixture exercising all four version-directive kinds (`versionadded`, `versionchanged`, `deprecated`, `versionremoved`) plus a second content-less `versionadded` (the period-vs-colon wording branch), each body-bearing case carrying a distinct sentinel token
- Added `TestVersionModifiedRenderGate` to `tests/test_pdf_render_gate.py`, extending the GATE-01 real-compile acceptance bar: `sphinx-build -b typst` → `typst.compile()` (no try/except, any `TypstCompilationError` propagates) → `pypdf` text-extraction, asserting all four Sphinx-computed label wordings, every body sentinel, and no `LEAK_SIGNATURES` leak

## Task Commits

Each task was committed atomically:

1. **Task 1: Add versionmodified pass-through + visit_inline classed-dispatch** - `5c38fcd` (feat)
2. **Task 2: Create the version_modified_render_gate fixture project** - `f525f76` (test)
3. **Task 3: Add TestVersionModifiedRenderGate real-compile class** - `354e1ed` (test)

_Note: this is a worktree-mode execution; the plan-metadata commit (SUMMARY.md) follows this file's own commit per the worktree protocol — STATE.md/ROADMAP.md are updated centrally by the orchestrator after merge._

## Files Created/Modified
- `typsphinx/translator.py` - Added `visit_versionmodified`/`depart_versionmodified` pass-through pair; extended `visit_inline`/`depart_inline` with the `versionmodified` classed-dispatch branch
- `tests/fixtures/version_modified_render_gate/conf.py` - Minimal Sphinx config (project/author/release, `typst_documents` master-doc tuple)
- `tests/fixtures/version_modified_render_gate/index.rst` - Five directive blocks: body-bearing `versionadded`, content-less `versionadded`, body-bearing `versionchanged`, body-bearing `deprecated`, label-only `versionremoved`
- `tests/test_pdf_render_gate.py` - Added `version_modified_render_gate_dir` fixture and `TestVersionModifiedRenderGate` real-compile test class
- `.planning/phases/12-high-volume-independent-node-handlers/deferred-items.md` - New file documenting pre-existing, out-of-scope sandbox verification caveats (see Issues Encountered)

## Decisions Made
- No `sphinx.domains.changeset.versionlabels` import (or any other Sphinx-internal label-map import): a live doctree dump (12-RESEARCH.md Part 1) confirmed Sphinx's `VersionChange.run()` already bakes the exact, already-localized label wording into the doctree as `nodes.inline(classes=["versionmodified", <kind>])` at directive-parse time. The translator's job is reduced to "detect the already-classed inline and italicize it" — this supersedes 12-CONTEXT.md D-01's speculated import mechanism while fully honoring its "sourced from Sphinx, not hardcoded" intent, and was documented in a code comment in `visit_inline`'s docstring (avoiding the literal string `versionlabels` in the source per the plan's own negative-grep acceptance criterion).
- Delegated the unboxed italic styling to the existing `visit_emphasis`/`depart_emphasis` dummy-node idiom (already used 4x elsewhere in the file: `visit_title_reference`, `visit_literal_strong`, `visit_literal_emphasis`, `visit_desc_signature`) rather than writing bespoke escaping/separator logic for the classed inline.

## Deviations from Plan

None - plan executed exactly as written. All three tasks' acceptance criteria were met without requiring architectural changes, bug fixes beyond what the plan specified, or missing-functionality additions.

## Issues Encountered

- **Pre-existing NixOS sandbox limitation (out of scope, not caused by this plan):** `pytest -m "not slow" -q` shows 45 pre-existing failures across `tests/test_integration_advanced.py`, `tests/test_integration_basic.py`, `tests/test_integration_multi_doc.py`, and `tests/test_integration_nested_toctree.py` — all failing identically with `Could not start dynamically linked executable: uv` (NixOS cannot run the `.venv`-installed `uv` wheel binary as a subprocess). These four files invoke `subprocess.run(["uv", "run", "sphinx-build", ...])` directly, hitting the exact hazard `tests/test_pdf_render_gate.py`'s own `_run_sphinx_build_typst` helper was already written to avoid (it uses `sys.executable -m sphinx` instead). None of these failing files were touched by this plan's Task 1 change, and `tests/test_translator.py` (104 tests covering the modified `visit_inline`/`visit_emphasis` interaction) passes cleanly. Documented in `deferred-items.md` per the SCOPE BOUNDARY rule; not fixed here.
- **Sandbox tooling note:** `uv run ruff` cannot execute in this sandbox for the same ELF/dynamic-linking reason. Verified lint compliance instead via `nix-shell -p ruff --run "ruff check ."` (ruff 0.15.14 from nixpkgs vs. the pinned 0.15.20 — same rule set for this diff). `uv run black --check` and `uv run mypy` both ran fine via `uv run` (only the ruff binary hit the issue).

## Next Phase Readiness

- `typsphinx/translator.py` and `tests/test_pdf_render_gate.py` are both touched by this plan and are shared-ownership files across Plans 02-04 of this phase (sequenced, not parallel, per the phase's wave note) — Plan 02 (XREF-01) can proceed against the current `main`/worktree-merged state.
- No blockers. VER-01 is fully satisfied: 3/3 tasks done, fast suite green (modulo the pre-existing, documented, unrelated sandbox failures), full render-gate suite (5/5) green, mypy/ruff/black clean.

## Self-Check: PASSED

- FOUND: tests/fixtures/version_modified_render_gate/conf.py
- FOUND: tests/fixtures/version_modified_render_gate/index.rst
- FOUND commit: 5c38fcd
- FOUND commit: f525f76
- FOUND commit: 354e1ed

---
*Phase: 12-high-volume-independent-node-handlers*
*Completed: 2026-07-12*
