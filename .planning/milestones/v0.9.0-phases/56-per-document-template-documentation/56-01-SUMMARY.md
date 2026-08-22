---
phase: 56-per-document-template-documentation
plan: 01
subsystem: docs
tags: [sphinx, rst, ast, pytest, doc-gate, typst]

# Dependency graph
requires:
  - phase: 54-one-bundle-rule-template-key-per-document-selection-four-del
    provides: "the typst_document_templates registry, RESERVED_REGISTRY_KEY, and the _template/<key>/ bundle output rule this catalogue documents"
  - phase: 54.1-bundle-directory-safety-templates-path-collision-refusal-and
    provides: "the templates_path collision refusal (shape #6) and the CONF-17 hoisted pre-write check this catalogue's row 6 documents"
provides:
  - "docs/source/user_guide/configuration.rst's Per-Document Templates subsection: a lead paragraph naming typst_document_templates, and a When the Build Stops sub-subsection with a 7-row error-catalogue list-table plus a two-shape I/O note"
  - "tests/test_registry_documentation_gate.py: a never-skipping, AST-based two-way gate (catalogue<->code agreement) plus a repo-wide sweep proving the retracted element [4] definition is gone"
  - "configuration.rst's rewritten element [4] definition: the registry key into typst_document_templates, with the absent-element and exact-string-equality rules stated"
affects: [56-02, 56-03, 56-04, 56-05]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 8664
  tasks: 3
  commits: 4

# Tech tracking
tech-stack:
  added: []
  patterns: ["AST-based two-way doc<->code agreement gate (ast.parse over raise ExtensionError call sites, resolving one level of same-module call-through indirection)", "run-time repo-wide sweep with an inline-reasoned exclusion dict, never a hardcoded file list"]

key-files:
  created: [tests/test_registry_documentation_gate.py]
  modified: [docs/source/user_guide/configuration.rst]

key-decisions:
  - "D-02: element [4] is now described as the registry key into typst_document_templates, stating the absent-element fallback to the reserved \"typst\" key and the exact-never-case-folded lookup rule; every existing five-element example tuple stays byte-identical."
  - "D-05/D-06: the error catalogue quotes only the identifying leading clause of each message (never the aggregated {summary} body), pinned two-way by an AST scanner that resolves builder.py:2151's call-through helper and template_registry.py:422's implicit string concatenation."
  - "The ^^^^ heading nesting level (untested precedent in this corpus) was proven safe under both builders by direct inspection of the built HTML <h4> and the Typst #heading(depth: 4, ...) output — no fallback to a sibling ~~~~ subsection was needed."

patterns-established:
  - "Pattern 1: never-skipping doc-gate modules import no typst-py and spawn no sphinx-build subprocess, reading only .py/.rst text via ast/re/pathlib."
  - "Pattern 2: every doc gate carries synthetic 'patterns have teeth' self-tests calling the SAME pure helper functions the real assertions use, so a helper that stops detecting anything fails in both places at once."

requirements-completed: [DOC-15]

coverage:
  - id: D1
    description: "configuration.rst publishes a Per-Document Templates subsection with a When the Build Stops error catalogue (7 rows + I/O note), pinned two-way to typsphinx/*.py's real ExtensionError shapes"
    requirement: "DOC-15"
    verification:
      - kind: unit
        ref: "tests/test_registry_documentation_gate.py::TestErrorCatalogueAgreesWithCode"
        status: pass
      - kind: unit
        ref: "tests/test_registry_documentation_gate.py::TestCatalogueGateHasTeeth"
        status: pass
    human_judgment: false
  - id: D2
    description: "Rendered legibility of the error-catalogue table (column headers, 7 data rows, no overflow) in both furo HTML and the typstpdf PDF"
    requirement: "DOC-15"
    verification:
      - kind: automated_ui
        ref: "uv run tox -e docs-html && uv run tox -e docs-pdf (build succeeded); <thead> and table.header(...) content inspected directly, see Deviations"
        status: pass
    human_judgment: true
    rationale: "Layout/legibility is not expressible as a plain assertion (56-VALIDATION.md's Manual-Only Verifications table names this exact deliverable). This SUMMARY records the orchestrator's own programmatic verification of the rendered <thead>/table.header content as the closing evidence for this checkpoint."
  - id: D3
    description: "The retracted 'accepted and ignored' definition of typst_documents element [4] is rewritten as the registry key, and its absence is pinned by a repo-wide sweep over docs/source/, README.md, and examples/"
    requirement: "DOC-15"
    verification:
      - kind: unit
        ref: "tests/test_registry_documentation_gate.py::TestRetractedElementFourDefinitionIsGone"
        status: pass
    human_judgment: false

# Metrics
duration: 13min (across two sessions separated by an orchestrator verification checkpoint)
completed: 2026-08-16
status: complete
---

# Phase 56 Plan 01: Per-Document Template Error Catalogue & Element [4] Retraction Summary

**Published a two-way, AST-pinned error catalogue for the `typst_document_templates` registry in `configuration.rst`, and retracted the stale "accepted and ignored" definition of `typst_documents` element [4] in favor of naming it the registry key — both locked by a never-skipping gate module.**

## Performance

- **Duration:** 13 min (commit-to-commit; a checkpoint verification pause by the orchestrator is excluded)
- **Started:** 2026-08-16T11:19:13Z
- **Completed:** 2026-08-16T11:33:06Z
- **Tasks:** 3
- **Files modified:** 2 (1 created, 1 modified)

## Accomplishments

- New `Per-Document Templates` subsection in `docs/source/user_guide/configuration.rst`, with a nested `When the Build Stops` sub-subsection: a 3-column, 7-row `list-table` error catalogue (each row quoting a single-literal-chunk identifying fragment from the real `typsphinx/*.py` source), plus a `.. note::` covering the two I/O-caused `ExtensionError` shapes.
- New `tests/test_registry_documentation_gate.py`: a never-skipping, `ast`-based two-way gate discovering every `raise ExtensionError(...)` call site under `typsphinx/*.py` (13 discovered — resolving `builder.py:2151`'s call-through helper `_conf17_violation_message()` and `template_registry.py:422`'s implicit adjacent-string-literal concatenation), denylisting the 3 out-of-scope shapes with written reasons, and asserting code↔docs agreement plus the single-literal-chunk rule (D-05) — 5 real assertions + 5 synthetic falsification self-tests.
- `configuration.rst:80`'s element [4] rewritten from "Document class (usually 'typst') -- accepted and ignored" to the registry key into `typst_document_templates`, stating the absent-element fallback to the reserved `"typst"` key and the exact-string-equality (never case-folded) lookup rule, cross-referenced to the new subsection via `` `Per-Document Templates`_ ``.
- Repo-wide sweep (`TestRetractedElementFourDefinitionIsGone`, 3 tests) proving the retracted "accepted and ignored" phrase is absent from every `*.rst` under `docs/source/`, `README.md`, and every `*.md`/`*.rst`/`*.py` under `examples/` — discovered at run time via `rglob`, never a hardcoded file list.

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end — the published error catalogue, pinned two-way to typsphinx's real raise sites** - `49255e4c` (feat)
2. **Correction (checkpoint response): add the missing list-table header row** - `465e1a8c` (fix)
3. **Task 2: Give the gate teeth — four synthetic falsification self-tests** - `cb486224` (test)
4. **Task 3: Retract the element [4] definition and pin its absence repo-wide** - `2547aeb0` (feat)

**Plan metadata:** committed as part of this SUMMARY.md commit (worktree mode — STATE.md/ROADMAP.md excluded; the orchestrator owns those writes after the wave merges)

## Files Created/Modified

- `tests/test_registry_documentation_gate.py` - New never-skipping doc-gate module: `ErrorShape`/AST-based `_discover_error_shapes()`, `_catalogue_region_text()`/`_published_fragments()`, pure comparison helpers shared by both the real assertions and the teeth tests, `TestErrorCatalogueAgreesWithCode` (5 tests), `TestCatalogueGateHasTeeth` (5 tests), `TestRetractedElementFourDefinitionIsGone` (3 tests) — 13 tests total.
- `docs/source/user_guide/configuration.rst` - New `Per-Document Templates` / `When the Build Stops` subsections (error catalogue + I/O note), the corrected `list-table` header row, and the rewritten element [4] definition.

## Decisions Made

- **`^^^^` heading nesting is safe under both builders — no fallback needed.** Task 1's action text carried an explicit fallback (promote `When the Build Stops` to a sibling `~~~~` subsection) if the untested `^^^^` level mis-rendered. The orchestrator's checkpoint verification confirmed correct rendering in both HTML (`<h4>When the Build Stops</h4>`) and Typst (`#heading(depth: 4, {text("When the Build Stops")})`), so Task 3's downstream cross-reference text was written as originally planned, with no restructuring.
- **The "column three names what to change" sentence was left unchanged** after the header-row fix — re-read per the checkpoint response's item 4, it still reads naturally as a positional reference now that the columns carry labels.
- **`ruff check` runs from the main checkout against the worktree path**, per the orchestrator's guidance (`cd /home/yuta/Documents/typsphinx && uv run ruff check .claude/worktrees/agent-a09037250706ed40a/...`), since the worktree's own `.venv` ships a PyPI generic-linux ruff wheel that cannot exec under NixOS. All ruff checks passed clean this way; not treated as unverifiable.

## Deviations from Plan

### Auto-fixed Issues

**1. [Checkpoint correction, orchestrator-directed] Missing `list-table` header row**
- **Found during:** Orchestrator's checkpoint verification of Task 1's tracer slice.
- **Issue:** The `list-table` set `:header-rows: 1` but its first child row was already a data row (`typst_document_templates is set to a truthy value that is not a dict`), so that row was silently consumed as the table header in both builders — the reader saw one error shape misrendered as a column header, and the table carried no `What went wrong` / `What the build says` / `What to change` labels at all.
- **Fix:** Added the three-label row as the new first row of the `list-table`, restoring all 7 catalogue entries to data rows.
- **Files modified:** `docs/source/user_guide/configuration.rst`
- **Verification:** Rebuilt both docs; confirmed `<thead>` now contains the three labels and `<tbody>` has 7 data rows (HTML), and `table.header(...)` now contains the three labels with the catalogue data as body cells (Typst). `uv run pytest tests/test_registry_documentation_gate.py -x -q` stayed green — the gate extracts fragments via regex over raw region text, not by table-row parsing, so it was never coupled to row position and needed no change.
- **Committed in:** `465e1a8c`

**2. [Rule 3 - blocking fix] `grep -c 'subprocess'` acceptance criterion tripped by the module docstring**
- **Found during:** Task 1's acceptance-criteria verification.
- **Issue:** The plan's Task 1 acceptance criteria require `grep -c 'subprocess' tests/test_registry_documentation_gate.py` to be `0`. My first draft's docstring said "spawns no `sphinx-build` subprocess", literally containing the word — a strict textual match failure with no behavioral impact (the module genuinely never spawns a subprocess).
- **Fix:** Reworded the sentence to "never spawns `sphinx-build` as a child process," preserving the intended meaning without the literal substring.
- **Files modified:** `tests/test_registry_documentation_gate.py`
- **Verification:** `grep -c 'subprocess' tests/test_registry_documentation_gate.py` returns `0`; `uv run pytest tests/test_registry_documentation_gate.py -x -q` still green.
- **Committed in:** `49255e4c` (fixed before the initial commit)

---

**Total deviations:** 2 (1 checkpoint correction directed by the orchestrator, 1 self-caught blocking fix). No scope creep — both are corrections to Task 1's own slice, not new functionality.

## Issues Encountered

- **A known false-positive on Task 3's own acceptance-criterion grep.** `git diff docs/source/user_guide/configuration.rst | grep -c '^-.*"typst")'` reports `1`, not `0` as the acceptance criteria state. The single match is the REMOVED prose line `-5. **Document class** (usually "typst") -- **accepted and ignored**:` — i.e. the retracted sentence Task 3 explicitly requires removing, which happens to contain the literal substring `"typst")` inside its own parenthetical `(usually "typst")`. This is not an edited example tuple: `git diff docs/source/user_guide/configuration.rst | grep '^-.*"typst")'` shows only that one prose line, and a direct check (`grep -n '"typst"),' docs/source/user_guide/configuration.rst`) confirms both real five-element example tuples (lines 40 and 447, in `.. code-block::` snippets) are untouched and byte-identical, satisfying D-02's actual prohibition ("No existing five-element `typst_documents` example anywhere in the repository is edited"). The acceptance-criterion grep pattern cannot distinguish this literal-substring coincidence from an actual edited code example; any correct retraction of the original sentence trips it, since the retracted text itself contains the pattern.
- **`ruff check` cannot run inside this worktree's own `.venv`** (generic-linux ELF wheel, unrunnable under NixOS — a pre-existing, project-documented limitation, not introduced by this plan). Resolved per the orchestrator's guidance by running `uv run ruff check` from the main checkout against the worktree path; all checks passed clean on every file this plan touched.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The two-way catalogue gate (`TestErrorCatalogueAgreesWithCode`) and its "patterns have teeth" self-tests (`TestCatalogueGateHasTeeth`) are now live and will police every later plan's prose additions to the same `When the Build Stops` region — this was the tracer's purpose (proving the scanner reaches all four awkward source shapes before more prose is written).
- Element [4]'s retraction (`TestRetractedElementFourDefinitionIsGone`) is proven end-to-end; Wave 2 plans (56-02/56-03/56-04) can proceed without re-deriving this sweep.
- No blockers. `git diff --stat typsphinx/` is empty across all four commits — no production code was touched, matching the phase's docs-only scope.
- Full-suite baseline moved from 1366 passed/5 skipped/0 failed to **1379 passed/5 skipped/0 failed**; `black --check .`, `ruff check .` (via main-checkout workaround), and `mypy typsphinx/` are all clean; `tox -e docs-html` and `tox -e docs-pdf` both report `build succeeded` (3 and 2 warnings respectively, matching the pre-existing baseline exactly).

## Self-Check: PASSED

- FOUND: `docs/source/user_guide/configuration.rst`
- FOUND: `tests/test_registry_documentation_gate.py`
- FOUND: commit `49255e4c`
- FOUND: commit `465e1a8c`
- FOUND: commit `cb486224`
- FOUND: commit `2547aeb0`

---
*Phase: 56-per-document-template-documentation*
*Completed: 2026-08-16*
