---
phase: 54-one-bundle-rule-template-key-per-document-selection-four-del
plan: 06
subsystem: infra
tags: [sphinx, config-inited, deprecation, removed-config, docs]

# Dependency graph
requires:
  - phase: 54-05
    provides: "every consumer of typst_template_assets already deleted (copy_template_assets(), _copy_template_directory()'s .typ exclusion, _copy_explicit_assets(), _copy_single_asset(), tests/test_template_assets.py), leaving the value genuinely inert before this plan unregisters it"
provides:
  - "typsphinx/removed_config.py: REMOVED_CONFIG_VALUES (bespoke D-09 messages) and check_config_at_init(), this codebase's first config-inited handler"
  - "typst_template_assets unregistered from typsphinx/__init__.py's setup(), in the same commit as the detection handler's connection"
  - "tests/test_removed_config_deprecation_gate.py: 9 tests covering CONF-19 (per-value warning content, the A-03 None/empty-list boundary, the clean-conf negative case, the loud-failure Config._raw_config gate, genuine unregistration, and the D-08 no-subtype source assertion)"
  - "Published docs (configuration.rst, templates.rst) and CLAUDE.md no longer instruct a reader to set typst_template_assets"
affects: []

# Actuals (#2632)
actuals:
  tokens: 6100
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "This codebase's first Sphinx event-handler connection (app.connect), as a deliberate, documented exception to the standing 'config-shape errors raise from inside a Builder method' pattern -- justified because a removed config value has nothing left for a Builder to validate against; it can only be observed by reading the raw conf.py namespace before Sphinx drops unknown names, which happens at config-inited, before any Builder is selected."
    - "Defensive private-attribute read at runtime (getattr(config, '_raw_config', {})) paired with a dedicated test that does NOT degrade gracefully -- the runtime degrades silently if the attribute disappears in a future Sphinx; the test fails loudly and names the module to repair."

key-files:
  created:
    - typsphinx/removed_config.py
    - tests/test_removed_config_deprecation_gate.py
  modified:
    - typsphinx/__init__.py
    - tests/test_extension.py
    - docs/source/user_guide/configuration.rst
    - docs/source/user_guide/templates.rst
    - CLAUDE.md

key-decisions:
  - "tests/test_extension.py's three MockApp classes (test_setup_returns_metadata, test_setup_parallel_safety, test_setup_version_matches) each gained a no-op connect() method -- a direct Rule 3 blocking consequence of setup() now calling app.connect(), not scope creep. Not in this plan's declared files_modified, but the plan's own Task 1 read_first named this as 'this codebase's first event-handler connection' with no local precedent, so nothing in the plan text could have anticipated this specific test breakage ahead of writing the code."
  - "Test module uses subprocess sphinx-build + combined stdout/stderr text assertions (per Task 2's own read_first pointer to test_collision_predicate_completeness_gate.py, which uses that style rather than caplog), building temporary source directories inline via tmp_path rather than adding new tests/fixtures/ directories -- avoids five new near-duplicate static fixture directories for scenarios that only differ by one conf.py line."
  - "The loud-failure test instantiates sphinx.config.Config() and asserts hasattr(instance, '_raw_config') rather than hasattr(Config, '_raw_config') on the class -- measured that _raw_config is set in Config.__init__, not present as a class-level attribute, so a class-level hasattr check would give a false negative today, not just on some future Sphinx."

patterns-established:
  - "A private-Sphinx-attribute dependency gets a defensive runtime read AND a separate loud-failure test -- never just one or the other. The runtime read must not raise (users' builds must not break because Sphinx changed something internal); the test must not use the same defensive getattr, or its own graceful degradation would hide the exact regression it exists to catch."

requirements-completed: [CONF-19]

coverage:
  - id: D1
    description: "typst_template_assets is unregistered from setup(), and in the same commit a config-inited handler is connected that would have detected this exact removal -- detection cannot be retrofitted after a name is unregistered, so both changes had to land together"
    requirement: "CONF-19"
    verification:
      - kind: unit
        ref: 'git grep -n "add_config_value(\"typst_template_assets\"" -- typsphinx (0 hits)'
        status: pass
      - kind: unit
        ref: 'git grep -n "app.connect" -- typsphinx (exactly 1 hit, naming config-inited)'
        status: pass
    human_judgment: false
  - id: D2
    description: "All three removed values (typst_template_assets, typst_authors, typst_toctree_defaults) warn by their own name, with a bespoke replacement statement or explicit no-replacement statement, and the observable consequence -- through the one config-inited mechanism, since two of the three have been unregistered since earlier milestones"
    verification:
      - kind: integration
        ref: "tests/test_removed_config_deprecation_gate.py::TestEachRemovedValueWarnsByName (parametrized x3, real sphinx-build subprocess, asserts required phrases in combined stdout+stderr)"
        status: pass
      - kind: integration
        ref: "tests/test_removed_config_deprecation_gate.py::TestA03NoneValueStillWarns (2 tests: None and empty-list still trigger the warning)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The detection mechanism's private-attribute dependency fails loudly, not silently, if Config._raw_config ever disappears from a future Sphinx"
    verification:
      - kind: unit
        ref: "tests/test_removed_config_deprecation_gate.py::TestDetectionMechanismFailsLoudlyIfItDisappears::test_raw_config_attribute_still_exists_on_sphinx_config -- failure message names typsphinx/removed_config.py"
        status: pass
    human_judgment: false
  - id: D4
    description: "No published page or repository instruction file still tells a reader to set typst_template_assets; the historical CHANGELOG.md record (via docs/source/changelog.rst's include) is untouched"
    verification:
      - kind: unit
        ref: 'git grep -n "typst_template_assets" -- docs/source/user_guide CLAUDE.md (0 hits)'
        status: pass
      - kind: unit
        ref: "uv run pytest tests/test_docs_contract_claims_gate.py tests/test_output_layout_docs_gate.py -q -> 21 passed"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-08-16
status: complete
---

# Phase 54 Plan 06: Unregister `typst_template_assets`, Add This Codebase's First `config-inited` Handler Summary

**Deleted the `typst_template_assets` config-value registration and, in the same commit, connected `typsphinx/removed_config.py`'s `config-inited` handler -- this codebase's first Sphinx event-handler connection -- so a `conf.py` still setting any of three removed values (`typst_template_assets`, `typst_authors`, `typst_toctree_defaults`) gets a build warning naming the value, its replacement (or explicit absence of one), and the observable consequence, instead of building silently different output with zero diagnostic.**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-08-16
- **Tasks:** 3
- **Files modified:** 7 (2 created, 5 modified)

## Accomplishments

- `typsphinx/removed_config.py` (new): `REMOVED_CONFIG_VALUES`, a mapping of each removed name to its own bespoke message (D-09 -- not one template with a substituted replacement, since the replacement relationship is asymmetric and `typst_toctree_defaults` has no replacement at all), and `check_config_at_init(app, config)`, the handler itself. Reads `getattr(config, "_raw_config", {})` defensively (D-06), warns for a name present regardless of its assigned value (A-03 -- `None` and `[]` both still warn, since the author wrote the line), and emits a bare `logger.warning` carrying no keyword arguments at all (D-07/D-08 -- matching every other warning in this extension, so this one does not become the sole individually-suppressible warning).
- `typsphinx/__init__.py`: deleted the `add_config_value("typst_template_assets", ...)` line and added `app.connect("config-inited", check_config_at_init)` in the same commit, with a comment recording that this is the codebase's first event-handler connection and why it is a deliberate exception to the "config-shape errors raise from inside a Builder method" pattern -- a removed value has nothing left for a Builder to validate, since Sphinx has already dropped the unknown name from `config.values` by the time any Builder runs.
- `tests/test_removed_config_deprecation_gate.py` (new, 9 tests): one parametrized test asserting each removed value's warning contains its own name, replacement (or explicit no-replacement statement), and consequence phrase, via real `sphinx-build` subprocess builds; the A-03 boundary (`None` and `[]` still warn, 2 tests); the negative case (a clean `conf.py` emits none of the three warnings); the D-06 loud-failure test (`sphinx.config.Config()` instance still exposes `_raw_config`, failure message names `typsphinx/removed_config.py`); genuine-unregistration proof (`typst_template_assets` absent from a real built app's `config.values`); and the D-08 source-level assertion (no `subtype` or `type=` anywhere in the module).
- `docs/source/user_guide/configuration.rst` and `docs/source/user_guide/templates.rst`: replaced the removed value's three-mode explanation (automatic/explicit/disabled) with one or two sentences stating the whole bundle directory is now copied wholesale automatically, with no asset list needed. `templates.rst`'s remaining "Automatic Bundle Copying" example was also corrected to say the template `.typ` file itself is now copied too (the one-bundle rule from earlier plans in this phase, not something Task 3 needed to newly explain, but the old prose said "except `.typ` files" which is now false).
- `CLAUDE.md`'s configuration-surface sentence: dropped `typst_template_assets` from the enumeration and added a clause recording its Phase 54/CONF-19 removal, following the existing Phase 45.1/CONF-10 `typst_authors` precedent already in that sentence.

## Task Commits

Each task was committed atomically:

1. **Task 1: The `config-inited` handler -- the three removed values** - `0929d2da` (feat)
2. **Task 2: The CONF-19 gate, including the loud failure if the detection mechanism disappears** - `9550fb75` (test)
3. **Task 3: Remove the published instructions for the configuration value that no longer exists** - `d3453eb2` (docs)

_No separate plan-metadata commit -- orchestrator owns STATE.md/ROADMAP.md writes for this worktree wave; this SUMMARY.md is committed as part of the worktree's own final commit._

## Files Created/Modified

- `typsphinx/removed_config.py` - new module: `REMOVED_CONFIG_VALUES`, `check_config_at_init()`
- `typsphinx/__init__.py` - deleted the `typst_template_assets` registration; added `app.connect("config-inited", check_config_at_init)` in the same commit, with a comment explaining the deliberate exception
- `tests/test_extension.py` - `MockApp`'s three classes gained a no-op `connect()` (Rule 3, direct blocking consequence)
- `tests/test_removed_config_deprecation_gate.py` - new, 9 tests
- `docs/source/user_guide/configuration.rst`, `docs/source/user_guide/templates.rst` - removed-value instructions replaced with the automatic-bundle-copy statement
- `CLAUDE.md` - configuration-surface sentence corrected

## Decisions Made

- **`tests/test_extension.py`'s `MockApp` fix, outside this plan's declared `files_modified`, treated as Rule 3 (blocking issue), not scope creep.** Task 1's own `read_first` named this as the codebase's first event-handler connection with no local precedent to check against for downstream test breakage -- the three `setup()`-calling unit tests use hand-written `MockApp` stand-ins (not `sphinx.testing`'s real app), so `app.connect(...)` raised `AttributeError` immediately. Fixed by adding a no-op `connect()` method to each of the three inline `MockApp` classes, with a comment naming why.
- **Test module built temporary source directories inline via `tmp_path` rather than adding static `tests/fixtures/` directories.** Task 2's own `read_first` pointed at both `test_typst_lang_gate.py` (subprocess runner) and `test_template_engine.py` ("temporary source directory with an inline `conf.py`"); combining both idioms avoided five near-duplicate fixture directories that would differ only by one `conf.py` line each.
- **The loud-failure test asserts against a constructed `Config()` instance, not the `Config` class.** Measured: `Config._raw_config` is set inside `Config.__init__`, not present as a class-level attribute (`hasattr(Config, "_raw_config")` is `False` even on the correct, unmodified Sphinx 9.1). A class-level assertion would have failed on today's Sphinx for a reason unrelated to the thing the test exists to catch.
- **`typst_documents`'s target in the test module's minimal `conf.py` is `"manual.typ"`, not `"index.typ"`.** The docname `"index"` already produces a content file at `index.typ` under the content/wrapper split (Phase 47+); an entry naming the same path as its own target collides pre-write and aborts the build with `ExtensionError`, unrelated to CONF-19. Discovered via the first test run (4 failures, `1 output path collision(s)`) and fixed inline before the module's own commit.

## Known Discrepancies

The overall plan `<verification>` block states `git grep -n "typst_template_assets" -- typsphinx docs/source/user_guide CLAUDE.md` should return no hits. It does not, by design, for a reason explicit in the plan's own Task 1 acceptance criteria one paragraph over:

1. **`typsphinx/removed_config.py`** (3 hits): `REMOVED_CONFIG_VALUES` must have `typst_template_assets` as a literal dict key, and its own bespoke D-09 message must name it by string -- Task 1's own acceptance criteria requires exactly this ("`REMOVED_CONFIG_VALUES` has exactly the three keys `typst_authors`, `typst_template_assets`, `typst_toctree_defaults`"). The overall plan's summary verification bullet combining `typsphinx` into the same grep scope as the two doc-only directories is a plan-text drift, not a defect in the implementation -- the detection module could not exist without naming the value it detects.

2. **Task 3's own `<verify>` block** expects `git grep -q 'typst_template_assets' -- docs/source/changelog.rst` to succeed (the historical record preserved). Measured: `docs/source/changelog.rst` contains `.. include:: ../../CHANGELOG.md` and a hand-written "Migration Guides" section, but no literal `typst_template_assets` text of its own -- the actual v0.4.3 historical entry (`Added Sphinx i18n...` era release introducing `typst_template_assets`, lines 606-616 of the included file) lives in the root `CHANGELOG.md`, rendered into the page at Sphinx build time via the `include` directive, not present as raw bytes in the `.rst` file `git grep` inspects. Task 3's own `<action>` text explicitly instructs "Do not touch `docs/source/changelog.rst`" -- honored literally; `CHANGELOG.md`'s historical entry (confirmed present, unmodified) is the actual thing SC#4/D-04's "historical record preserved" intent protects, and it is untouched. This is the same class of plan/measurement drift `54-05-SUMMARY.md`'s "Known Discrepancies" section recorded for its own two authorized exceptions.

Both are named here explicitly, not discovered ad hoc: (1) follows directly from Task 1's own literal acceptance criteria; (2) follows directly from Task 3's own literal "do not touch" instruction plus the measured file structure.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `tests/test_extension.py`'s hand-written `MockApp` stand-ins lacked `connect()`**
- **Found during:** Task 1's own full-suite verification run
- **Issue:** `setup(app)` now calls `app.connect("config-inited", check_config_at_init)`; the three unit tests calling `setup()` against a hand-written `MockApp` (not a real Sphinx app) raised `AttributeError: 'MockApp' object has no attribute 'connect'`.
- **Fix:** Added a no-op `connect(self, event, callback)` method to each of the three inline `MockApp` classes, with a comment explaining why.
- **Files modified:** `tests/test_extension.py`
- **Verification:** `uv run pytest tests/ -q` -> 1278 passed, 5 skipped (0 failed, matching the pre-plan baseline exactly)
- **Committed in:** `0929d2da` (Task 1 commit)

**2. [Rule 1 - Bug] Test module's minimal `conf.py` initially collided its own `typst_documents` target with the content-file path**
- **Found during:** Task 2's first test run (4 failures: `1 output path collision(s): 'index.typ'`)
- **Issue:** `typst_documents = [("index", "index.typ", ...)]` names a target identical to the docname `"index"`'s own content-file output path (`index.typ`), which the pre-write collision validator correctly rejects -- an unrelated failure mode to what this test module exists to exercise.
- **Fix:** Changed the target to `"manual.typ"`.
- **Files modified:** `tests/test_removed_config_deprecation_gate.py`
- **Verification:** `uv run pytest tests/test_removed_config_deprecation_gate.py -q` -> 9 passed (0 failed)
- **Committed in:** `9550fb75` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 Rule 3 -- direct blocking consequence of this plan's own first-of-its-kind change; 1 Rule 1 -- an unrelated pre-existing collision-validator interaction the test's own fixture conf.py tripped)
**Impact on plan:** Both fixes were necessary for this plan's own stated acceptance criteria ("full suite green", "at least 7 tests... 0 failed") to hold; neither touches behaviour outside this plan's scope.

## Issues Encountered

`uv run ruff check .` cannot execute in this NixOS sandbox -- `ruff`'s installed wheel is a generic-linux dynamically-linked ELF the sandbox refuses to exec. This is the same pre-existing, previously-documented environment limitation `54-01-SUMMARY.md` through `54-05-SUMMARY.md` all recorded -- not introduced or fixable by this plan's changes. `black --check .` (317 files) and `mypy typsphinx/` (8 source files) both ran clean throughout.

## Known Stubs

None -- every change this plan made is a real registration removal, a real detection handler, real tests against real `sphinx-build` subprocess output, or a real documentation edit; no placeholder or hardcoded-empty value was introduced.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `54-07` can now widen `_validate_output_path_collisions()`'s exact-name `_template.typ` claim into a `_template/` prefix reservation and relocate `tests/fixtures/template_named_dir_master/` -- this plan touched neither `builder.py` nor the collision validator (per the parallel-execution boundary), so `54-07` inherits its own starting point unchanged by this plan.
- CONF-19 is closed: all three removed configuration values (`typst_template_assets`, `typst_authors`, `typst_toctree_defaults`) now announce themselves by name at `config-inited`, for every builder including `-b html`, with detection shipped in the same commit as the last one's unregistration -- there is no longer a silent window where a `conf.py` upgrading past v0.9.0 loses behaviour with zero diagnostic.
- Full pytest suite (1287 passed, 5 skipped -- the 9-test increase from 54-05's 1278 baseline is exactly this plan's new gate module, zero new failures), `black --check .`, and `mypy typsphinx/` all green against the final state; `ruff check .` could not run in this environment (documented, pre-existing, unrelated).
- No coupling risk with 54-01 through 54-05's own artifacts -- this plan touched only `typsphinx/__init__.py` (one deletion, one addition, both explicitly this plan's job), a new standalone module, a new standalone test module, `tests/test_extension.py`'s three `MockApp` stand-ins, and doc/CLAUDE.md prose; `typsphinx/builder.py`, `writer.py`, and every fixture from earlier plans in this phase are unchanged.
- Milestone branch `gsd/v0.9.0-per-document-templates` confirmed still pushed to `origin` (`git ls-remote --heads origin` returns a non-empty SHA); this plan performed no push (worktree-isolated execution, orchestrator owns the merge).

## Self-Check: PASSED

- FOUND: `typsphinx/removed_config.py` exists and contains `check_config_at_init` and `REMOVED_CONFIG_VALUES`
- FOUND: `tests/test_removed_config_deprecation_gate.py` exists, 9 tests, all pass
- CONFIRMED: `git grep -n "add_config_value(\"typst_template_assets\"" -- typsphinx` -> zero hits
- CONFIRMED: `git grep -n "app.connect" -- typsphinx` -> exactly one hit, naming `config-inited`
- CONFIRMED: `git grep -n "typst_template_assets" -- docs/source/user_guide CLAUDE.md` -> zero hits
- FOUND commit `0929d2da` in `git log --oneline`
- FOUND commit `9550fb75` in `git log --oneline`
- FOUND commit `d3453eb2` in `git log --oneline`
- CONFIRMED: `uv run pytest tests/ -q` -> 1287 passed, 5 skipped, 0 failed
- CONFIRMED: `uv run black --check .` -> clean; `uv run mypy typsphinx/` -> clean

---
*Phase: 54-one-bundle-rule-template-key-per-document-selection-four-del*
*Completed: 2026-08-16*
