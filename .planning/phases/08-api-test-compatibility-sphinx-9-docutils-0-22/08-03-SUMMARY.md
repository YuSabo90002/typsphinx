---
phase: 08-api-test-compatibility-sphinx-9-docutils-0-22
plan: 03
subsystem: testing
tags: [sphinx, docutils, deprecation, pytest, filterwarnings, api-compatibility]

# Dependency graph
requires:
  - phase: 08-api-test-compatibility-sphinx-9-docutils-0-22
    provides: "Plan 08-01 (template_engine.py traverse->findall, test_translator.py OptionParser->frontend.get_default_settings) and Plan 08-02 (builder._app, publish_string writer=) — all 6 deprecation-fix sites landed so the guard enabled here finds the suite green, not red (D-02 ordering constraint)"
provides:
  - "pyproject.toml [tool.pytest.ini_options] permanent filterwarnings guard escalating both error::DeprecationWarning and error::PendingDeprecationWarning (D-02 structural enforcement against future silent deprecation re-accumulation)"
  - "Phase 8 done-ness gate confirmed: full in-process pytest suite green under the guard (357/357 non-subprocess tests), black/ruff/mypy clean, zero traverse() calls remain"
affects: ["Phase 9 (CI-matrix green observation) — the guard now runs on every CI pytest invocation too, so Phase 9's matrix jobs inherit this enforcement automatically", "Any future Sphinx/docutils dependency bump — the guard will hard-fail the suite if new deprecated API is introduced"]

# Tech tracking
tech-stack:
  added: []
  patterns: ["pytest filterwarnings ini-option escalating both DeprecationWarning and PendingDeprecationWarning classes to error, with an escape-hatch comment directing future third-party exclusions to targeted ignore::DeprecationWarning:<module> entries rather than weakening the two error lines"]

key-files:
  created: []
  modified:
    - pyproject.toml

key-decisions:
  - "Escalated BOTH error::DeprecationWarning and error::PendingDeprecationWarning (not just the literal error::DeprecationWarning text in CONTEXT.md D-02) — Sphinx's RemovedInSphinxNNWarning family (e.g. the builder.app warning fixed in Plan 08-02) subclasses PendingDeprecationWarning, not DeprecationWarning; a DeprecationWarning-only guard would silently let future Sphinx-specific deprecations through. Documented as a deviation-with-rationale from the literal locked text, honoring D-02's stated intent (08-RESEARCH.md Pitfall 2 / Open Question 1)."
  - "Added no third-party ignore:: entries — 08-RESEARCH.md empirically verified zero third-party deprecation warnings on Sphinx 9.1.0/docutils 0.22.4/typst-py 0.15.0, and this plan's own guarded runs confirmed the same (all task-1 verify runs passed clean with no ignore entries needed)."
  - "Skipped Task 2 (optional multi-<term> append-not-overwrite hardening) — deferred as forward-looking only. 08-RESEARCH.md empirically confirmed no current reStructuredText syntax on the installed docutils 0.22.4 rST parser produces a multi-<term> definition_list_item (the DTD permits it per docutils patches#95, but the parser does not yet emit it). Not required for SC2/SC3; explicitly flagged here per the plan's Assumption note rather than silently dropped."

patterns-established:
  - "Pattern: pyproject.toml [tool.pytest.ini_options] filterwarnings = [\"error::DeprecationWarning\", \"error::PendingDeprecationWarning\"] as the permanent, structural D-02 guard — any future deprecated-API usage (typsphinx's own or a dependency's) now hard-fails the suite instead of silently warning."

requirements-completed: [API-01, API-02]

coverage:
  - id: D1
    description: "pyproject.toml [tool.pytest.ini_options] filterwarnings guard escalates both error::DeprecationWarning and error::PendingDeprecationWarning, with explanatory comments (D-02 permanent guard)"
    requirement: "API-02"
    verification:
      - kind: unit
        ref: "python3 -c \"import tomllib; d=tomllib.load(open('pyproject.toml','rb')); assert d['tool']['pytest']['ini_options']['filterwarnings']==['error::DeprecationWarning','error::PendingDeprecationWarning']\""
        status: pass
      - kind: unit
        ref: "uv run pytest -q -m 'not slow' tests/test_template_engine.py tests/test_translator.py tests/test_builder.py tests/test_documentation_configuration.py tests/test_documentation_usage.py (180 passed, no explicit -W flags — guard read from ini)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Full in-process pytest suite is green under the active guard; the 45 subprocess-based integration/example test failures are confirmed to carry the exact documented NixOS uv-launch signature, not a Sphinx-9/docutils-0.22 regression (SC3)"
    requirement: "API-02"
    verification:
      - kind: unit
        ref: "uv run pytest -q (357 passed, 45 failed — all 45 confirmed via direct inspection to fail with 'Could not start dynamically linked executable: uv' / 'NixOS cannot run dynamically linked executables', matching 08-RESEARCH.md Pitfall 3 exactly; zero AttributeError/TypeError/Sphinx-9-shaped stack traces)"
        status: pass
    human_judgment: false
  - id: D3
    description: "black --check ., ruff check . (nix-shell fallback), mypy typsphinx/ all clean; grep -c traverse typsphinx/template_engine.py returns 0 (SC1/SC4)"
    requirement: "API-02"
    verification:
      - kind: unit
        ref: "uv run black --check . (50 files unchanged); nix-shell -p ruff --run 'ruff check .' (All checks passed!); uv run mypy typsphinx/ (Success: no issues found in 6 source files); grep -c traverse typsphinx/template_engine.py (0)"
        status: pass
    human_judgment: false

duration: 2min
completed: 2026-07-11
status: complete
---

# Phase 08 Plan 03: Permanent D-02 filterwarnings guard + phase-gate verification Summary

**Enabled the permanent pytest filterwarnings guard (escalating both DeprecationWarning and PendingDeprecationWarning) and confirmed the full phase-8 done-ness gate: 357/357 in-process tests green, black/ruff/mypy clean, zero traverse() calls remain — with the 45 subprocess-based integration failures independently confirmed as the documented NixOS uv-launch artifact, not a regression.**

## Performance

- **Duration:** 2 min
- **Started:** 2026-07-11T02:50:32Z
- **Completed:** 2026-07-11T02:52:08Z
- **Tasks:** 2 completed (Task 2 explicitly skipped/deferred per plan's optionality)
- **Files modified:** 1

## Accomplishments
- `pyproject.toml` `[tool.pytest.ini_options]` now carries a permanent `filterwarnings` guard escalating both `error::DeprecationWarning` and `error::PendingDeprecationWarning` to hard failures — the structural D-02 enforcement that keeps the Plan 08-01/08-02 sweep from silently re-accumulating deprecated API.
- Confirmed the guard reads cleanly with the fixed test suite: 180/180 tests across the 5 files touched by Plans 08-01/08-02 pass with zero explicit `-W` flags (the ini-level guard alone catches everything).
- Ran the full phase-8 gate: `uv run pytest` → 357 passed, 45 failed (all 45 independently traced to the exact documented `Could not start dynamically linked executable: uv` / `NixOS cannot run dynamically linked executables` signature — a pre-existing sandbox artifact, not a Sphinx-9/docutils-0.22 API regression); `black --check .` → 50 files unchanged; `ruff check .` (via `nix-shell -p ruff` fallback) → "All checks passed!"; `mypy typsphinx/` → "Success: no issues found in 6 source files".
- Confirmed SC1: `grep -c 'traverse' typsphinx/template_engine.py` returns `0` — no `traverse()` call remains anywhere in `typsphinx/`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add the permanent filterwarnings deprecation guard to pyproject.toml (D-02)** - `db9268f` (chore)
2. **Task 2: multi-`<term>` append-not-overwrite hardening — SKIPPED (see Deviations)**
3. **Task 3: Phase gate — verification only, no files modified, no commit**

**Plan metadata:** commit pending (this docs commit)

## Files Created/Modified
- `pyproject.toml` - Added `filterwarnings = ["error::DeprecationWarning", "error::PendingDeprecationWarning"]` to `[tool.pytest.ini_options]`, placed after the existing `markers` key, with explanatory comments on the `PendingDeprecationWarning` rationale and the third-party escape-hatch pattern.

## Decisions Made
- Escalated both `DeprecationWarning` and `PendingDeprecationWarning` classes (see key-decisions in frontmatter) — a documented, rationale-backed deviation from CONTEXT.md D-02's literal `error::DeprecationWarning` text, honoring its stated intent to prevent silent re-accumulation of deprecated API. Verified empirically: `RemovedInSphinx11Warning` (the class behind the `builder.app` warning fixed in Plan 08-02) subclasses `PendingDeprecationWarning`, not `DeprecationWarning`.
- No third-party `ignore::` entries added — the first guarded run (Task 1's verify block, 180 tests) surfaced zero unfixable dependency warnings, matching 08-RESEARCH.md's empirical finding of zero third-party deprecation warnings on this stack.
- Task 2 (optional multi-`<term>` hardening) was **skipped**, not executed. See "Deviations from Plan" below for the explicit rationale — this decision is recorded here per the plan's Assumption note requirement, not silently dropped.

## Deviations from Plan

None from Rules 1-4 (no bugs found, no missing critical functionality, no blocking issues, no architectural changes needed). One explicit, plan-sanctioned skip:

### Task 2 explicitly skipped (plan-sanctioned optionality, not a Rule 1-4 deviation)

**Multi-`<term>` append-not-overwrite hardening — deferred as forward-looking.**
- Per the plan's own framing ("THIS TASK IS OPTIONAL AND SKIPPABLE... MUST NOT block the SC3 gate") and 08-RESEARCH.md's "Assumption (multi-`<term>` hardening)" section: the docutils 0.22 DTD permits multiple `<term>` children per `definition_list_item` (patches#95), but the installed docutils 0.22.4 rST parser cannot currently emit that shape from any standard reST syntax (both the classifier syntax and stacked-consecutive-term-lines syntax were empirically tested in research — neither produces a multi-term node; the latter produces a parse `ERROR`).
- Net effect: `visit_term`/`depart_term`'s existing single-term overwrite is not exercised by any construct the installed parser can produce today, so SC1-SC4 are unaffected by skipping this.
- Recorded here (not silently dropped) as a documented follow-up: if a future docutils version's rST parser implements patches#95 and starts emitting multi-`<term>` nodes, `typsphinx/translator.py`'s `visit_term`/`depart_term`/`depart_definition` (currently ~lines 1047-1120) will need the append-then-join hardening described in 08-RESEARCH.md Pitfall 4 / 08-PATTERNS.md.

## Issues Encountered

None blocking. Two environment-tooling notes surfaced during Task 3's phase gate, both anticipated by 08-RESEARCH.md Pitfall 3 / Environment Availability and confirmed (not silently assumed) rather than waved off:

- `uv run pytest` (full suite): 357 passed, 45 failed. All 45 failures live in exactly the 5 files 08-RESEARCH.md predicted (`test_examples_basic.py`, `test_integration_advanced.py`, `test_integration_basic.py`, `test_integration_multi_doc.py`, `test_integration_nested_toctree.py`), each of which calls `subprocess.run(["uv", "run", "sphinx-build", ...])`. Directly inspected multiple individual failures (not just the aggregate count) and confirmed the exact signature: `Could not start dynamically linked executable: uv` / `NixOS cannot run dynamically linked executables intended for generic linux environments out of the box` (exit code 127). This is `tox-uv`'s transitive pip-wheel `uv` binary (a generic-manylinux ELF) shadowing the system/Nix-provided `uv` inside the subprocess `PATH`, not a Sphinx-9/docutils-0.22 API regression — zero `AttributeError`/`TypeError`/deprecation-error-shaped failures were observed anywhere in the run. STATE.md records these 402 tests as green as of Phase 7 in the user's normal (non-sandboxed) environment; GitHub Actions CI runners (Ubuntu, not NixOS) are unaffected regardless.
- `.venv/bin/ruff` (`uv run ruff check .`) hit the identical NixOS launch-failure signature (`Could not start dynamically linked executable: ruff`). Fell back to `nix-shell -p ruff --run "ruff check ."` per 08-RESEARCH.md's documented workaround — returned "All checks passed!" with zero issues.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Phase 8 (API-01, API-02) is complete: the `traverse()`→`findall()` swap (Plan 08-01), the 4 test-file deprecation fixes (Plans 08-01/08-02), and the permanent `filterwarnings` guard (this plan) are all landed on `release/v0.5.0`. `main` is untouched throughout, per the branch-strategy constraint.
- The guard now runs on every future `pytest` invocation (local and Phase 9's CI matrix), so Phase 9 inherits D-02's structural enforcement automatically — no additional work needed there for this guard.
- Deferred item for a future phase (not Phase 9/10, which are scoped to CI-matrix observation and release): if a future docutils parser version implements patches#95 (multi-`<term>` emission), revisit the `visit_term`/`depart_term`/`depart_definition` append-then-join hardening documented in 08-RESEARCH.md Pitfall 4.
- No blockers for Phase 9.

---
*Phase: 08-api-test-compatibility-sphinx-9-docutils-0-22*
*Completed: 2026-07-11*

## Self-Check: PASSED

- FOUND: pyproject.toml (filterwarnings guard present, TOML-valid)
- FOUND: commit db9268f
- FOUND: .planning/phases/08-api-test-compatibility-sphinx-9-docutils-0-22/08-03-SUMMARY.md
