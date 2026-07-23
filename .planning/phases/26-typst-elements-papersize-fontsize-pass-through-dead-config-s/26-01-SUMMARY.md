---
phase: 26-typst-elements-papersize-fontsize-pass-through-dead-config-s
plan: 01
subsystem: config
tags: [sphinx, typst, template-engine, config-plumbing]

# Dependency graph
requires:
  - phase: 22.2
    provides: "sphinx.errors.ExtensionError fail-loud precedent (builder.py) and the config->output dead-config-sweep pattern (CONF-01..03)"
provides:
  - "RawTypst frozen-dataclass marker in typsphinx/template_engine.py, recognized by _format_typst_value() before the str branch for unquoted-length emission"
  - "ELEMENTS_ALLOWLIST module constant (papersize->string, fontsize->raw emission tags) hand-maintained against templates/base.typ's project() signature"
  - "map_parameters(sphinx_metadata, typst_elements=None) additive merge: validates against ELEMENTS_ALLOWLIST, raises sphinx.errors.ExtensionError on an unknown key before it reaches params"
  - "writer.py passes typst_elements to map_parameters() as its own keyword argument instead of laundering it through sphinx_metadata.update(); drops the dead copyright key"
affects: [26-02-PLAN (GATE-01 real-compile fixtures), phase-27 (docs examples referencing typst_elements papersize/fontsize)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "RawTypst marker pattern: any future config value needing unquoted Typst-literal emission wraps in RawTypst and gets a new isinstance branch in _format_typst_value(), checked before the str branch, to avoid the double-formatting trap"
    - "ELEMENTS_ALLOWLIST curated dict pattern: hand-maintained allowlist mapping a config key to an emission-kind tag (_ElementsEmissionKind.STRING / .RAW), validated before merge into params -- generalizes for future CONF-06 elements work"

key-files:
  created: []
  modified:
    - typsphinx/template_engine.py
    - typsphinx/writer.py
    - tests/test_template_engine.py

key-decisions:
  - "Marker class name: RawTypst (single str field `source`, frozen dataclass) -- matches RESEARCH.md's recommended default exactly"
  - "Allowlist constant name: ELEMENTS_ALLOWLIST (module-level dict[str, str]); emission tags are class attributes on a private _ElementsEmissionKind sentinel class (STRING/RAW), not bare string literals scattered inline"
  - "Elements merge runs as the LAST step inside map_parameters(), after the existing parameter_mapping / package-path back-fill guard / typst_authors override -- untouched by this change"
  - "sphinx.errors.ExtensionError chosen over ConfigError for the unknown-key raise, matching builder.py's existing idiom in this codebase"

patterns-established:
  - "Pattern 1 (RawTypst unquoted emission): reusable for any future config value needing a Typst literal rather than a quoted string"
  - "Pattern 2 (curated allowlist merged additively, after existing logic): reusable for any future curated (not auto-derived) pass-through config surface"

requirements-completed: [CONF-04]

coverage:
  - id: D1
    description: "map_parameters(md, typst_elements={'papersize': 'us-letter'}) returns papersize as a plain str; _format_typst_value emits it quoted (D-01)"
    requirement: "CONF-04"
    verification:
      - kind: unit
        ref: "tests/test_template_engine.py::TestTypstElementsPassThrough::test_map_parameters_papersize_is_plain_str"
        status: pass
      - kind: unit
        ref: "tests/test_template_engine.py::TestTypstElementsPassThrough::test_format_typst_value_str_unchanged"
        status: pass
    human_judgment: false
  - id: D2
    description: "map_parameters(md, typst_elements={'fontsize': '20pt'}) returns fontsize wrapped in RawTypst (not a plain str); _format_typst_value emits it unquoted (D-02)"
    requirement: "CONF-04"
    verification:
      - kind: unit
        ref: "tests/test_template_engine.py::TestTypstElementsPassThrough::test_map_parameters_fontsize_is_raw_typst"
        status: pass
      - kind: unit
        ref: "tests/test_template_engine.py::TestTypstElementsPassThrough::test_format_typst_value_raw_typst_emits_unquoted"
        status: pass
      - kind: unit
        ref: "tests/test_template_engine.py::TestTypstElementsPassThrough::test_render_papersize_and_fontsize_emission_shapes"
        status: pass
    human_judgment: false
  - id: D3
    description: "An unknown typst_elements key raises sphinx.errors.ExtensionError naming the offending key and listing both supported keys, before the key is ever added to params (D-06/D-07)"
    requirement: "CONF-04"
    verification:
      - kind: unit
        ref: "tests/test_template_engine.py::TestTypstElementsPassThrough::test_map_parameters_unknown_element_key_raises"
        status: pass
      - kind: unit
        ref: "tests/test_template_engine.py::TestTypstElementsPassThrough::test_map_parameters_unknown_key_does_not_emit_wrong_quoted_form"
        status: pass
    human_judgment: false
  - id: D4
    description: "copyright is never present in map_parameters()'s returned params -- structural non-leak, not a filter (D-08); writer.py drops the dead copyright key and no longer launders typst_elements through sphinx_metadata"
    requirement: "CONF-04"
    verification:
      - kind: unit
        ref: "tests/test_template_engine.py::TestTypstElementsPassThrough::test_map_parameters_copyright_never_in_params"
        status: pass
      - kind: unit
        ref: "tests/test_template_engine.py::TestTypstElementsPassThrough::test_map_parameters_copyright_never_leaks_even_with_elements"
        status: pass
      - kind: other
        ref: "grep -n 'sphinx_metadata.update' typsphinx/writer.py (returns nothing) + grep -n '\"copyright\"' typsphinx/writer.py (absent from the gather dict)"
        status: pass
    human_judgment: false
  - id: D5
    description: "templates/base.typ is byte-unchanged (SC#5) -- the fix is 100% Python-side"
    requirement: "CONF-04"
    verification:
      - kind: other
        ref: "git diff --exit-code typsphinx/templates/base.typ (exit 0) + sha256sum matches pre-change hash 1d2733642a6d5540e6d8ff6786f0d35516168a3301abef96e2125f60c04751ea"
        status: pass
    human_judgment: false
  - id: D6
    description: "Every existing map_parameters() call site (one positional arg) continues to work unmodified -- default None treated as empty (Pitfall 4)"
    requirement: "CONF-04"
    verification:
      - kind: unit
        ref: "tests/test_template_engine.py::TestTypstElementsPassThrough::test_map_parameters_no_typst_elements_argument_still_works"
        status: pass
      - kind: unit
        ref: "tests/test_template_engine.py -q (full 56/56 including ~13 pre-existing one-arg call sites)"
        status: pass
    human_judgment: false

duration: 2min
completed: 2026-07-24
status: complete
---

# Phase 26 Plan 01: `typst_elements` Python-side Pass-Through Summary

**RawTypst marker + ELEMENTS_ALLOWLIST curated merge in `template_engine.py`, wired from `writer.py` as a separate argument -- `papersize`/`fontsize` now reach `map_parameters()` with correct per-key typing, an unknown key fails loud via `ExtensionError`, and `copyright` is structurally unreachable.**

## Performance

- **Duration:** 2 min (task-commit timestamps 06:31:55 -> 06:33:27 JST)
- **Started:** 2026-07-23T21:31:00Z (approx, first commit)
- **Completed:** 2026-07-23T21:33:27Z
- **Tasks:** 2/2 completed
- **Files modified:** 3

## Accomplishments
- Added an immutable `RawTypst` marker class (`@dataclass(frozen=True)`, single `source: str` field) in `typsphinx/template_engine.py`, recognized by a new `isinstance` branch in `_format_typst_value()` placed BEFORE the existing `str` branch -- so a `RawTypst`-wrapped value is emitted verbatim (unquoted) and never re-enters string quoting (the double-formatting trap).
- Added a module-level `ELEMENTS_ALLOWLIST: Dict[str, str]` constant mapping exactly `papersize` -> string-emission and `fontsize` -> raw-emission, tagged via a small `_ElementsEmissionKind` sentinel class (`STRING`/`RAW`), hand-maintained against `templates/base.typ`'s `project()` signature.
- Gave `TemplateEngine.map_parameters()` a new `typst_elements: Dict[str, Any] | None = None` keyword parameter. After the existing parameter-mapping / package-path back-fill guard / `typst_authors` override logic (all untouched), it iterates `typst_elements`, raising `sphinx.errors.ExtensionError` (naming the offending key + listing both supported keys) for any key not in `ELEMENTS_ALLOWLIST` BEFORE the key is ever added to `params`, and otherwise adds the value -- wrapped in `RawTypst` for `fontsize`, passed through as a plain `str` for `papersize`.
- Rewired `typsphinx/writer.py`: removed the `sphinx_metadata.update(typst_elements)` laundering line, dropped the now-dead `"copyright"` entry from the gathered `sphinx_metadata` dict, and now calls `template_engine.map_parameters(sphinx_metadata, typst_elements=typst_elements)` -- `typst_elements` reaches `map_parameters()` as its own argument, structurally separate from baseline Sphinx metadata for the entire call chain.
- Appended 10 new unit tests to `tests/test_template_engine.py` (`TestTypstElementsPassThrough`) covering: `RawTypst` unquoted emission, unchanged `str` quoting, `papersize`-as-str, `fontsize`-as-`RawTypst`, unknown-key raise (message content + negative quoted-form guard), `copyright` non-leak (alone and combined with `typst_elements`), the no-argument backward-compat call site, and an end-to-end `render()` emission-shape assertion.
- Verified `templates/base.typ` byte-unchanged: `git diff --exit-code` exits 0 and its sha256 (`1d2733642a6d5540e6d8ff6786f0d35516168a3301abef96e2125f60c04751ea`) is unchanged from the plan's recorded pre-change hash.

## Task Commits

Each task was committed atomically:

1. **Task 1: RawTypst marker, ELEMENTS_ALLOWLIST, and the additive fail-loud merge in template_engine.py** - `b7083c9` (feat)
2. **Task 2: Wire writer.py to pass typst_elements separately, drop the dead copyright key, and freeze base.typ** - `67a40ca` (fix)

_No TDD multi-commit sequence was used -- both tasks were `type="auto"` (Task 1 declared `tdd="true"` in frontmatter but its `<action>` describes appending tests alongside the implementation in one pass, which is what was executed; unit tests were written and verified green together with the implementation in the single Task 1 commit)._

## Files Created/Modified
- `typsphinx/template_engine.py` - Added `RawTypst` marker class, `_ElementsEmissionKind` sentinel, `ELEMENTS_ALLOWLIST` constant, a new `isinstance(value, RawTypst)` branch in `_format_typst_value()`, and the additive `typst_elements` merge step in `map_parameters()`
- `typsphinx/writer.py` - Removed `sphinx_metadata.update(typst_elements)`; dropped `"copyright"` from the gathered `sphinx_metadata` dict; calls `map_parameters(sphinx_metadata, typst_elements=typst_elements)`
- `tests/test_template_engine.py` - Added `import pytest` + `TestTypstElementsPassThrough` (10 new unit tests)

## Decisions Made
- Marker class named `RawTypst` (not `_RawTypstValue`) -- matches RESEARCH.md's stated default and keeps the public-ish name discoverable for Plan 02's GATE-01 fixtures.
- Allowlist constant named `ELEMENTS_ALLOWLIST`; emission-kind tags are attributes on a small private `_ElementsEmissionKind` class (`STRING = "string"`, `RAW = "raw"`) rather than bare string literals, so a typo in a tag comparison would be a `NameError`/`AttributeError` at import time rather than a silent string mismatch.
- `sphinx.errors.ExtensionError` used for the unknown-key raise (over `ConfigError`) -- both are permitted per CONTEXT.md D-06; `ExtensionError` matches the existing `builder.py` precedent in this exact codebase.

**Identifiers for Plan 02 / future CONF-06 work to reuse:**
- Marker class: `typsphinx.template_engine.RawTypst` (field: `source`)
- Allowlist constant: `typsphinx.template_engine.ELEMENTS_ALLOWLIST` (keys: `"papersize"`, `"fontsize"`; values are `_ElementsEmissionKind.STRING` / `.RAW`)
- New `map_parameters()` keyword: `typst_elements: Dict[str, Any] | None = None`
- Error message shape: `f"typst_elements: unknown key {key!r} -- supported keys: {supported}"` where `supported = ", ".join(sorted(ELEMENTS_ALLOWLIST))`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Plan's Task 2 verify command referenced a nonexistent `tests/test_writer.py`**
- **Found during:** Task 2 (writer.py wiring)
- **Issue:** The plan's `<verify><automated>` step for Task 2 specified `uv run pytest tests/test_config.py tests/test_writer.py tests/test_template_engine.py -q` -- but `tests/test_writer.py` does not exist anywhere in this codebase (confirmed via `ls tests/` and a repo-wide grep for `TypstWriter`/`sphinx_metadata`/`typst_elements` references across all test files).
- **Fix:** Ran the actually-relevant test files instead: `tests/test_config.py tests/test_config_template_mapping.py tests/test_template_engine.py tests/test_package_template_routing.py tests/test_missing_and_malformed_master_gate.py tests/test_nested_master_render_gate.py tests/test_template_import_path.py` -- these are the suites that exercise `TypstWriter.translate()`, config registration, and template routing.
- **Files modified:** None (verification-only substitution; no source change).
- **Verification:** All 89 tests passed (`89 passed in 3.51s`).
- **Committed in:** 67a40ca (Task 2 commit; the substitution is a verification-step deviation, not a code change)

---

**Total deviations:** 1 auto-fixed (1 blocking -- missing test file reference in the plan's verify command)
**Impact on plan:** No scope creep; the substitution used only pre-existing test files whose coverage is at least as relevant as the phantom `test_writer.py` reference would have been.

## Issues Encountered
- `black --check` flagged `typsphinx/template_engine.py` for reformatting after the Task 1 edit (long lines from the new docstrings/constant). Ran `black` (no `--check`) to auto-format; re-ran the unit suite (56/56 still green) and `mypy typsphinx/` (clean) after formatting, before committing.
- `ruff check` and `python -m ruff check` both fail in this NixOS sandbox with `Could not start dynamically linked executable` -- this is the documented, pre-existing environmental limitation (project memory `nixos-sandbox-test-env.md`: compiled Rust/Go binaries invoked via `uv run <binary>` can't execute in the NixOS sandbox). Not something this plan can or should fix; `black --check`/`mypy` (both pure-Python, run fine) provide the lint/type signal instead.
- A broader `uv run pytest -q -m "not slow"` pass (excluding the 4 known environmentally-flaky integration files per project memory) showed 23 additional failures, all in `tests/test_integration_basic.py`/`tests/test_integration_advanced.py`, all with `subprocess.CalledProcessError: ... returncode 127` from a nested `["uv", "run", "sphinx-build", ...]` subprocess invocation -- the same class of NixOS-sandbox environmental failure (nested `uv run` subprocess spawning), unrelated to this plan's `writer.py`/`template_engine.py` changes. `516 passed` otherwise.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- CONF-04's Python-side wiring is complete: `papersize`/`fontsize` now reach `map_parameters()`'s returned `params` with the correct per-key emission typing, an unknown key fails loud, and `copyright` is structurally unreachable.
- `templates/base.typ` remains byte-unchanged, ready for Plan 02's real-`typst.compile()` GATE-01 fixtures (positive papersize, positive fontsize, negative unknown-key, copyright-non-leak) to consume the exact identifiers recorded above.
- No blockers. The unit-tier proof (this plan) and the real-compile proof (Plan 02, Wave 2) are cleanly separated per the plan's own scope split.

---
*Phase: 26-typst-elements-papersize-fontsize-pass-through-dead-config-s*
*Completed: 2026-07-24*
