---
phase: 16-silent-drop-node-handlers-length-converter-refactor
plan: 01
subsystem: translator
tags: [sphinx-ext-todo, gentle-clues, typst, docutils, tdd]

# Dependency graph
requires:
  - phase: 15-full-corpus-validation
    provides: GATE-02 full-corpus warning catalogue identifying todo_node/manpage as the only remaining typsphinx content-drops
provides:
  - "visit_todo_node/depart_todo_node on TypstTranslator, rendering .. todo:: as a gentle-clues task() box"
  - "todo_render_gate GATE-01 fixture + TestTodoRenderGate real-compile acceptance test class"
affects: [16-02, 16-03, 17-rendering-fidelity-audit]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Config-gated SkipNode admonition handler: raise nodes.SkipNode before _visit_admonition() when a Sphinx config flag is False, mirroring every official Sphinx builder's own todo_node visitor"

key-files:
  created:
    - tests/fixtures/todo_render_gate/conf.py
    - tests/fixtures/todo_render_gate/index.rst
  modified:
    - typsphinx/translator.py
    - tests/test_pdf_render_gate.py

key-decisions:
  - "Gate visit_todo_node on self.config.todo_include_todos via raise nodes.SkipNode, matching every official Sphinx builder (html/latex/text/man/texinfo) — a deliberate planner decision documented in 16-01-PLAN.md's flagged-assumption section, not left as an open question"
  - "custom_title=\"Todo\" is an inert non-i18n fallback; the actual rendered title comes from todo_node's own nodes.title child via visit_title's admonition-aware buffer-swap (16-RESEARCH.md Pitfall 2)"

patterns-established:
  - "GATE-01 real-compile fixture + test pattern extended to a config-gated (enabled/disabled) node handler pair in one test class, using extra_args on _run_sphinx_build_typst for the -D override build"

requirements-completed: [TODO-01]

coverage:
  - id: D1
    description: "A .. todo:: body renders inside a gentle-clues task() box with a dynamic title in the compiled PDF when todo_include_todos=True, with no 'unknown node type' warning"
    requirement: "TODO-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestTodoRenderGate::test_todo_pdf_renders_body_and_title"
        status: pass
    human_judgment: false
  - id: D2
    description: "Building the same fixture with todo_include_todos=False emits neither the todo body nor a task( call in the generated .typ (internal work-notes never leak into published output, T-16-01)"
    requirement: "TODO-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestTodoRenderGate::test_todo_typ_omits_body_when_todo_include_todos_false"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-07-16
status: complete
---

# Phase 16 Plan 01: TODO-01 todo_node handler Summary

**`.. todo::` now renders as a gentle-clues `task()` box with its own dynamic title, gated on `todo_include_todos` via `nodes.SkipNode` exactly like every official Sphinx builder — proven through a real `sphinx-build -> typst.compile() -> pypdf` round trip in both the enabled and disabled configurations.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-07-16T12:32:06Z (worktree base commit)
- **Completed:** 2026-07-16T12:38:21Z
- **Tasks:** 2 completed
- **Files modified:** 4 (2 new fixture files, 2 modified source/test files)

## Accomplishments
- Implemented `visit_todo_node`/`depart_todo_node` on `TypstTranslator`, closing the `unknown node type: <todo_node>` warning (×10 in the Sphinx corpus, TODO-01)
- Wired the `config.todo_include_todos` gate via `raise nodes.SkipNode`, matching every official Sphinx builder — no draft `.. todo::` content can leak into a published PDF when the config is False (the Sphinx default)
- Added a new GATE-01 real-compile fixture (`todo_render_gate`) and `TestTodoRenderGate` test class (2 tests) proving both the enabled-rendering path and the disabled no-leak path through a genuine `sphinx-build -> typst.compile() -> pypdf` round trip

## Task Commits

Each task was committed atomically:

1. **Task 1: Create todo_render_gate fixture + failing TestTodoRenderGate tests (RED)** - `e1c77e2` (test)
2. **Task 2: Implement visit_todo_node/depart_todo_node with todo_include_todos gate (GREEN)** - `5f3ec4c` (feat)

_TDD cycle: RED (e1c77e2) -> GREEN (5f3ec4c). No REFACTOR commit needed — the implementation matched the target shape from `16-PATTERNS.md` on the first pass._

## Files Created/Modified
- `typsphinx/translator.py` - `visit_todo_node`/`depart_todo_node` methods added adjacent to the `visit_hint`/`depart_hint` admonition pair (~line 3767)
- `tests/fixtures/todo_render_gate/conf.py` - new fixture: `sphinx.ext.todo` enabled, `todo_include_todos = True`
- `tests/fixtures/todo_render_gate/index.rst` - new fixture: one `.. todo::` block with sentinel body `TODOBODYSENTINEL9X4`
- `tests/test_pdf_render_gate.py` - `TODO_BODY_SENTINEL` constant, `todo_render_gate_dir` fixture, `extra_args` parameter on `_run_sphinx_build_typst`, `TestTodoRenderGate` class (2 tests)

## Decisions Made
- Gated `visit_todo_node` on `self.config.todo_include_todos` per the plan's flagged-assumption section — every official Sphinx builder does this, and diverging would reintroduce exactly the fidelity-bug class this milestone hunts (T-16-01).
- Left `custom_title="Todo"` in place as documented inert fallback; the actually-rendered title flows through `todo_node`'s own `nodes.title` child via the existing `visit_title` admonition-aware buffer-swap (no new title-handling code needed).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Reworded the fixture's descriptive prose to remove incidental "Todo" occurrences**
- **Found during:** Task 2 (GREEN verification run)
- **Issue:** The fixture's own `index.rst` descriptive paragraph used the literal capitalized word "Todo" twice (`titled "Todo"` / `the literal word "Todo"`), inflating `full_text.count("Todo")` to 3 instead of the expected 1 (the box's own dynamic title). This was a test-fixture-authoring oversight introduced in Task 1, only surfaced once the handler existed and a real PDF could be extracted.
- **Fix:** Reworded the descriptive paragraph to avoid the literal capitalized substring "Todo" (kept lowercase `.. todo::` directive references, which don't match the case-sensitive count), while preserving the same explanatory intent.
- **Files modified:** `tests/fixtures/todo_render_gate/index.rst`
- **Verification:** `TestTodoRenderGate::test_todo_pdf_renders_body_and_title` passes; `full_text.count("Todo") == 1`.
- **Committed in:** `5f3ec4c` (Task 2 commit, alongside the handler implementation since both were needed together to reach GREEN)

---

**Total deviations:** 1 auto-fixed (Rule 1 — test-fixture bug fix)
**Impact on plan:** No scope creep. The fix was a one-line wording correction required to make the plan's own acceptance criterion (`full_text.count("Todo") == 1`) achievable.

## Issues Encountered

**Task 1's stated per-test RED/GREEN expectation for test (b) did not hold empirically, but the plan's actual `<verify>` gate (class-level nonzero exit) still passed correctly.**

The plan's Task 1 acceptance criteria expected `test_todo_typ_omits_body_when_todo_include_todos_false` to report "1 passed" immediately after Task 1 (pre-handler), reasoning that "body is absent today via unknown_visit drop." Empirically this is incorrect for the `"unknown node type" not in result.stderr` assertion specifically: reading `sphinx/ext/todo.py`'s `setup()` confirms `todo_node` instances are **never removed from the doctree** based on `todo_include_todos` — that config only gates each builder's own registered `visit_todo_node`/`depart_todo_node` handler (via `raise nodes.SkipNode`), which typsphinx did not yet have in Task 1. So before the fix, `todo_node` reaches the unknown-visit fallback and the "unknown node type" warning fires identically regardless of the config value — both tests in the class failed at Task 1 (RED), not just test (a).

This did not block progress: Task 1's actual `<verify>` command (`... -rs -q; test $? -ne 0`) only checks the class exits nonzero, which held true (2 failed). Task 2's acceptance criteria (`TestTodoRenderGate -q` reports "2 passed, 0 failed, 0 skipped") is the authoritative GREEN gate and was met exactly as written. No plan or code change was needed to resolve this — it self-resolved once the config-gated handler was implemented in Task 2, and is documented here purely for planning-accuracy traceability (a future planner writing a similar config-gated `nodes.SkipNode` test pair should expect BOTH the enabled and disabled pre-fix runs to share the same "no handler yet" warning, not just the enabled one).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `visit_todo_node`/`depart_todo_node` land cleanly next to the other admonition visitor pairs; `_visit_admonition`/`_depart_admonition` untouched, `@preview` version-sync surface untouched (`test_preview_version_sync.py` green).
- Full render-gate suite (20 tests, all classes) green; fast suite green except the 3 pre-existing, unrelated `tests/test_examples_basic.py` failures caused by this sandbox's documented `["uv", "run", ...]` PATH-shadowing issue (spawns `uv run sphinx-build` directly rather than the `sys.executable -m sphinx` idiom this plan's own test helper uses) — not a regression from this plan's changes.
- Ready for 16-02 (MAN-01 `manpage` handler) and 16-03 (LEN-01 length-converter refactor), both independent of this plan's changes per the roadmap.

---
*Phase: 16-silent-drop-node-handlers-length-converter-refactor*
*Completed: 2026-07-16*
