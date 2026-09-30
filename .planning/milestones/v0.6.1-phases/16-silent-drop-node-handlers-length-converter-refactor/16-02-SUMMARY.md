---
phase: 16-silent-drop-node-handlers-length-converter-refactor
plan: 02
subsystem: rendering
tags: [sphinx, typst, translator, manpage, gate-01]

# Dependency graph
requires:
  - phase: 16-01
    provides: TestTodoRenderGate / todo_render_gate fixture precedent (GATE-01 pattern, _run_sphinx_build_typst with extra_args)
provides:
  - "visit_manpage/depart_manpage on TypstTranslator -- :manpage: role renders italic literal page text"
  - "manpage_render_gate fixture + TestManpageRenderGate -- real-compile GATE-01 acceptance test for MAN-01"
affects: [16-03, phase-17-audit]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Full delegation to an existing inline-node visitor (visit_emphasis/depart_emphasis) for a duck-typed node instead of a bespoke handler -- reuses the paragraph-separator/list-item/inline-concat-context/_in_markup_mode state machine for free"

key-files:
  created:
    - tests/fixtures/manpage_render_gate/conf.py
    - tests/fixtures/manpage_render_gate/index.rst
    - tests/fixtures/manpage_render_gate/image.png
  modified:
    - typsphinx/translator.py
    - tests/test_pdf_render_gate.py

key-decisions:
  - "visit_manpage/depart_manpage delegate 100% to visit_emphasis/depart_emphasis (no bespoke body) per 16-RESEARCH.md Pattern 2 -- verified safe by reading the full emphasis method bodies (no isinstance check on the node argument)"
  - "No linkification (D-02a): manpages_url left unset in the fixture; the .typ assert for absence of link( pins this as a permanent regression guard"

patterns-established:
  - "Delegation-only inline-node handler: visit_X(self, node) -> None: self.visit_emphasis(node) / depart_X mirrors -- applicable to any future duck-typed inline node needing the same italic/markup-mode machinery"

requirements-completed: [MAN-01]

coverage:
  - id: D1
    description: "The :manpage: role's literal page-reference text (e.g. ls(1)) renders italic in the compiled PDF across paragraph, list-item, and figure-caption contexts, with the unknown node type warning eliminated"
    requirement: "MAN-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestManpageRenderGate::test_manpage_pdf_renders_italic_text"
        status: pass
    human_judgment: false
  - id: D2
    description: "No link() fabrication -- manpage renders literal text only, never a link, with manpages_url unset (D-02a prohibition)"
    requirement: "MAN-01"
    verification:
      - kind: integration
        ref: "tests/test_pdf_render_gate.py::TestManpageRenderGate::test_manpage_pdf_renders_italic_text (asserts 'link(' not in typ_source)"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-07-16
status: complete
---

# Phase 16 Plan 02: Manpage Node Handler (MAN-01) Summary

**`visit_manpage`/`depart_manpage` delegate wholesale to `visit_emphasis`/`depart_emphasis`, rendering `:manpage:` page-reference text (e.g. `ls(1)`) italic in every separator/mode context, proven by a real `typst.compile()` + pypdf GATE-01 fixture spanning a paragraph, a list item, and a figure caption.**

## Performance

- **Duration:** ~6 min (RED commit to GREEN commit)
- **Started:** 2026-07-16T12:44:26Z
- **Completed:** 2026-07-16T12:45:57Z
- **Tasks:** 2 completed
- **Files modified:** 5 (2 new fixture files + 1 binary asset copy + translator.py + test_pdf_render_gate.py)

## Accomplishments

- Eliminated the `unknown node type: <manpage>` warning (×10 in the Sphinx corpus per PROJECT.md) by adding two new `TypstTranslator` methods that fully delegate to the existing `visit_emphasis`/`depart_emphasis` italic-wrapper machinery
- New GATE-01 real-compile fixture (`manpage_render_gate`) and `TestManpageRenderGate` test class prove the `:manpage:` role renders correctly in all three contexts a manpage role can appear in — plain paragraph (code-mode default), bullet list item, and figure caption (markup-mode, exercising the `#` prefix toggle) — via `sphinx-build -b typst` → `typst.compile()` → `pypdf` text extraction, never string-agreement alone
- Confirmed the D-02a no-linkification prohibition with a permanent `.typ`-level negative assert (`"link(" not in typ_source`)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create manpage_render_gate fixture + failing TestManpageRenderGate test (RED)** - `e437f29` (test)
2. **Task 2: Implement visit_manpage/depart_manpage via emphasis delegation (GREEN)** - `e31a79e` (feat)

_TDD plan: RED confirmed FAILED (not skipped) against `main` with the exact three `unknown node type: <manpage>` warnings; GREEN confirmed all assertions pass after the two-method delegation was added._

## Files Created/Modified

- `typsphinx/translator.py` - added `visit_manpage`/`depart_manpage`, placed immediately after `depart_emphasis` (the delegation target), before `visit_strong`
- `tests/fixtures/manpage_render_gate/conf.py` - new GATE-01 fixture project config (no `manpages_url`, per D-02a)
- `tests/fixtures/manpage_render_gate/index.rst` - new fixture doc with three `:manpage:` uses (paragraph/list-item/figure-caption), no other emphasis markup
- `tests/fixtures/manpage_render_gate/image.png` - binary asset, byte-identical copy of `figure_length_render_gate/image.png`
- `tests/test_pdf_render_gate.py` - added `manpage_render_gate_dir` fixture and `TestManpageRenderGate.test_manpage_pdf_renders_italic_text`

## Decisions Made

- Delegation-only implementation (no bespoke emph wrapper) — matches the plan's locked recommendation and 16-RESEARCH.md Pattern 2/Anti-Patterns guidance; verified safe because `visit_emphasis`/`depart_emphasis` perform no `isinstance` check on their node argument
- Left `visit_manpage`/`visit_emphasis` themselves unmodified — pure additive change

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixture's own descriptive prose inflated the `emph({` count assertion**
- **Found during:** Task 2 (running `TestManpageRenderGate` after implementing the handler)
- **Issue:** `index.rst`'s explanatory paragraph used a double-backtick code span containing the literal string `` emph({ `` (describing the assertion the test makes). Once `visit_manpage` started emitting real `emph({` wrappers, the generated `.typ` source contained 4 occurrences instead of the expected 3 — one from this literal code-span text (rendered via `raw("emph({")`), not from a `:manpage:` use.
- **Fix:** Reworded the sentence to avoid embedding the literal string (`"italic-wrapper occurrences"` instead of quoting `` `emph({` ``).
- **Files modified:** `tests/fixtures/manpage_render_gate/index.rst`
- **Verification:** `TestManpageRenderGate` now asserts `typ_source.count("emph({") == 3` and passes; full render-gate suite (21 tests) green.
- **Committed in:** `e31a79e` (Task 2 commit — the fix landed alongside the GREEN implementation since it was discovered while verifying GREEN, not a separate task boundary)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Self-contained fixture-authoring bug caught by the plan's own acceptance criteria (exact count == 3); no scope creep, no change to `translator.py`'s intended shape.

## Issues Encountered

- `uv run python -m pytest -m "not slow" ...` (the plan's full fast-suite verification command) shows 3 pre-existing failures in `tests/test_examples_basic.py` (`TestBasicExampleBuild`) — these invoke `["uv", "run", "sphinx-build", ...]` as a subprocess and hit the documented NixOS sandbox PATH-shadowing hazard (a stray non-Nix `uv` binary in `.venv/bin` shadows the correct Nix-provided `uv`, causing exit 127 "Could not start dynamically linked executable"). This is a known environmental issue unrelated to this plan's changes (the file was untouched by this plan, and the failure mode is identical to the one `_run_sphinx_build_typst`'s own docstring describes and works around via `sys.executable -m sphinx`). Confirmed out of scope per the deviation rules' scope boundary — not fixed. `TestManpageRenderGate` and the full `tests/test_pdf_render_gate.py` suite (21 tests, which does use the `sys.executable -m sphinx` invocation form) are unaffected and fully green.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- MAN-01 requirement satisfied and verified via a real compile; `visit_manpage`/`depart_manpage` are additive-only, no risk to other node handlers
- Plan 16-03 (LEN-01 length-converter refactor) is independent of this plan's changes and can proceed
- Full render-gate suite (21 classes/tests) green; mypy/black/ruff clean; the pre-existing `test_examples_basic.py` environmental failure is unchanged by this plan and should be tracked separately if it needs fixing

---
*Phase: 16-silent-drop-node-handlers-length-converter-refactor*
*Completed: 2026-07-16*

## Self-Check: PASSED

All created/modified files verified present on disk; both task commits (`e437f29`, `e31a79e`) verified present in git log.
