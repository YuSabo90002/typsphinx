---
phase: 53-template-registry-foundation
plan: 02
subsystem: builder/writer
tags: [sphinx, typst, template-registry, tracer, byte-identity]

# Dependency graph
requires:
  - "53-01: 53-RED-EVIDENCE.md's pre-change SHA-256 baseline for the four configuration shapes"
provides:
  - "typsphinx/template_registry.py: TemplateRegistryEntry, RESERVED_REGISTRY_KEY, resolve_template_registry(), resolve_registry_key() -- no validation yet"
  - "typst_document_templates config value (default {})"
  - "TypstBuilder._document_template_registry, resolved once per build in write()"
  - "TypstWriter.render_wrapper(..., template_entry=...) -- builds TemplateEngine from a resolved registry entry, not raw config"
  - "tests/test_template_registry.py -- TPL-03/04/05 and D-10/D-11 coverage, plus a render_wrapper source-region invariant"
affects: [53-03, 53-04, 53-05]

# Actuals (#2632)
actuals:
  tokens: 6890
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "resolved-once-per-build registry, threaded like _master_include_edges (builder.py:730)"
    - "source-region invariant test via inspect.getsource(), scoped to one function"

key-files:
  created:
    - typsphinx/template_registry.py
    - tests/test_template_registry.py
  modified:
    - typsphinx/__init__.py
    - typsphinx/builder.py
    - typsphinx/writer.py

key-decisions:
  - "TPL-01 is NOT marked complete by this plan -- TPL-01's own text requires template XOR package enforcement, which this task's resolve_template_registry() deliberately performs NO validation for (that is plan 53-03's expansion). REQUIREMENTS.md's TPL-01 checkbox stays unchecked until 53-03 lands the xor check."
  - "The D-11 edge test (Task 2, test 3) monkeypatches TemplateEngine.__init__ inside a try/finally to capture the parameter_mapping kwarg render_wrapper() actually passes, since render_wrapper() returns a rendered string, not the TemplateEngine instance -- this proves the runtime behavior directly rather than only asserting on source text."

requirements-completed: [TPL-03, TPL-04, TPL-05]

coverage:
  - id: MH1
    description: "A conf.py that sets nothing new still builds, and the registry resolved for it contains exactly one key, the synthesized built-in \"typst\" (TPL-03)"
    requirement: TPL-03
    verification:
      - kind: test
        ref: "tests/test_template_registry.py::test_default_config_resolves_registry_with_only_the_typst_key"
        status: pass
    human_judgment: false
  - id: MH2
    description: "A four-element typst_documents tuple resolves to the same TemplateRegistryEntry object as the same tuple with a fifth element of the literal \"typst\" (TPL-04)"
    requirement: TPL-04
    verification:
      - kind: test
        ref: "tests/test_template_registry.py::test_four_element_tuple_and_explicit_typst_fifth_element_resolve_identically"
        status: pass
    human_judgment: false
  - id: MH3
    description: "Two typst_documents entries naming the same registry key resolve to the identical TemplateRegistryEntry object (TPL-05)"
    requirement: TPL-05
    verification:
      - kind: test
        ref: "tests/test_template_registry.py::test_two_entries_naming_same_user_defined_key_share_one_object"
        status: pass
    human_judgment: false
  - id: MH4
    description: "render_wrapper() builds its TemplateEngine from a resolved TemplateRegistryEntry; its own body no longer reads typst_template, typst_package, or typst_template_function off config"
    requirement: TPL-03
    verification:
      - kind: test
        ref: "tests/test_template_registry.py::test_render_wrapper_reads_none_of_the_three_promoted_globals_by_exact_name, ::test_render_wrapper_source_contains_template_entry_identifier"
        status: pass
    human_judgment: false
  - id: MH5
    description: "A user-defined registry key whose definition omits template_function resolves to template_function None -- no inheritance from global typst_template_function (D-10)"
    requirement: TPL-01
    verification:
      - kind: test
        ref: "tests/test_template_registry.py::test_user_defined_key_omitting_template_function_gets_none_not_inherited"
        status: pass
    human_judgment: false
  - id: MH6
    description: "Global typst_template_mapping reaches TemplateEngine only for the \"typst\" key's engine; every user-defined key passes parameter_mapping None (D-11)"
    requirement: TPL-01
    verification:
      - kind: test
        ref: "tests/test_template_registry.py::test_reserved_key_engine_gets_global_mapping_user_defined_key_gets_none"
        status: pass
    human_judgment: false
  - id: MH7
    description: "An empty or absent typst_document_templates dict is legal and resolves to a registry containing only the synthesized \"typst\" key (D-02, TPL-03)"
    requirement: TPL-03
    verification:
      - kind: test
        ref: "tests/test_template_registry.py::test_empty_typst_document_templates_resolves_to_only_the_typst_key"
        status: pass
    human_judgment: false
  - id: MH8
    description: "The registry is resolved once per build in write(), between _validate_output_path_collisions() and prepare_writing()"
    requirement: TPL-03
    verification:
      - kind: other
        ref: "typsphinx/builder.py write(): resolve_template_registry() call inserted between the _validate_output_path_collisions() call and the prepare_writing() call; confirmed by direct code read"
        status: pass
    human_judgment: false
  - id: MH9
    description: "Every test file matching grep -rl \"_template\\.typ\" tests/ still passes with its _template.typ assertions unmodified"
    requirement: TPL-03
    verification:
      - kind: test
        ref: "uv run pytest tests/ -q -- full suite: 1174 passed, 7 pre-existing failures unrelated to this plan; grep -rl \"_template\\.typ\" tests/ | wc -l returns 32 (unchanged from 53-01's measurement); git diff --name-only -- tests/ lists only tests/test_template_registry.py"
        status: pass
    human_judgment: false
  - id: MH10
    description: "The @preview package version declarations remain in exactly the three existing sites"
    requirement: TPL-03
    verification:
      - kind: test
        ref: "uv run pytest tests/test_preview_version_sync.py -q -- 3 passed"
        status: pass
    human_judgment: false
  - id: T3
    description: "Tracer byte-identity spot-check: shapes A and D rebuilt post-change match 53-01's pre-change SHA-256 baseline"
    requirement: TPL-03
    verification:
      - kind: other
        ref: "See \"Task 3: Tracer byte-identity spot-check\" section below -- 7 .typ files across 2 shapes, all SHA-256-identical to 53-RED-EVIDENCE.md"
        status: pass
    human_judgment: false

duration: ~45min
completed: 2026-08-15
status: complete
---

# Phase 53 Plan 02: Template Registry Tracer Summary

**Wired the end-to-end tracer for Phase 53: `typst_document_templates` config registration, a new `typsphinx/template_registry.py` resolver, `write()`'s once-per-build resolution, the wrapper loop, and `render_wrapper()` building its `TemplateEngine` from a resolved `TemplateRegistryEntry` instead of raw config reads -- proven byte-identical against 53-01's baseline for two of the four SC#2 shapes, with the full existing regression net (1174 tests, 32 `_template.typ`-asserting files) staying green unmodified.**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-08-15T08:12:00Z
- **Tasks:** 3/3
- **Files modified:** 5 (2 new: `template_registry.py`, `test_template_registry.py`; 3 modified: `__init__.py`, `builder.py`, `writer.py`)

## Accomplishments

- Registered `typst_document_templates` (default `{}`, rebuild `"html"`, types `[dict]`) in
  `typsphinx/__init__.py`, leaving `typst_template_assets` untouched (Phase 54's CONF-19).
- Built `typsphinx/template_registry.py`: a frozen `TemplateRegistryEntry` dataclass,
  `RESERVED_REGISTRY_KEY = "typst"`, `resolve_template_registry(config, srcdir)` (no validation
  this task -- 53-03's expansion), and `resolve_registry_key(registry, entry)`. The module
  docstring records why registry-key validation cannot reuse `_escapes_outdir()`/
  `_is_drive_qualified()` (opposite contract: legal multi-segment output path vs. legal single
  path segment).
- Threaded the resolved registry through `builder.py`: `self._document_template_registry`
  initialized in `init()`, resolved once in `write()` between `_validate_output_path_collisions()`
  and `prepare_writing()` (D-03/D-09), with a lazy-derivation fallback in `_write_typst_files()`
  mirroring the existing `_master_include_edges` pattern -- load-bearing for the many existing
  tests that call `write_doc()`/`_write_typst_files()` directly without ever calling `write()`.
  `_write_template_file()` (builder.py:1109-1179) is explicitly untouched this phase.
- Switched `writer.py`'s `render_wrapper()` to a `template_entry` keyword parameter: when absent
  (every existing direct caller), it derives the built-in `"typst"` entry through the SAME
  `resolve_template_registry()` function the builder's write path calls -- one derivation point,
  never two. `template_path`, `typst_package`, and `typst_template_function` now come from the
  resolved entry; `typst_template_mapping` is scoped to the `"typst"` key only (D-11);
  `typst_package_imports` stays a global read (unchanged).
- Wrote `tests/test_template_registry.py` with 15 tests: TPL-03/04/05 coverage, D-10/D-11 edge
  cases, an empty-registry-default test, a frozen-dataclass shape test, and (Task 2) three
  invariant tests pinning the promotion via `inspect.getsource(TypstWriter.render_wrapper)` --
  proven capable of failing by temporarily restoring `writer.py` to its pre-Task-1 state and
  observing both source-region tests fail with the expected messages, then restoring the file
  (confirmed via `git diff` showing zero changes after restore).
- Rebuilt two of the four SC#2 shapes (documented below) and confirmed every emitted `.typ` file's
  SHA-256 matches 53-01's pre-change `53-RED-EVIDENCE.md` baseline exactly.

## Task 3: Tracer byte-identity spot-check against the wave-1 baseline

**Shapes rebuilt:** `tests/fixtures/documented_params_contract_gate` (Shape A -- `typst_template`
set) and `tests/roots/test-basic` (Shape D -- nothing set), both via
`uv run python -m sphinx -b typstpdf <source> <scratch>`, matching the builder 53-01 recorded.

**Files compared:** 4 `.typ` files for Shape A (`_template.typ`, `chapter.typ`, `index.typ`,
`master.typ`) + 3 `.typ` files for Shape D (`_template.typ`, `index.typ`, `output.typ`) = **7
files total**.

**Result: identical.** Every post-change SHA-256 matched the corresponding pre-change hash
recorded in `53-RED-EVIDENCE.md` verbatim:

| File | Shape | SHA-256 (post-change, this session) | Matches 53-RED-EVIDENCE.md? |
|---|---|---|---|
| `_template.typ` | A | `22bc8c60c644fc5e809e58799fb52da82840c08b1e715c6fa8dab9d9d4571511` | yes |
| `chapter.typ` | A | `c160a6b5cd565ce452736d59b42b5f6d2a066e54608016dd9328232ff9b6e6d3` | yes |
| `index.typ` | A | `f9fbfa8cacf58676ec6963370bc635dafc61410c0c83613a66f9e894cd2210dc` | yes |
| `master.typ` | A | `ef419a0e6264f32a043c40154840ae926590495d1ec19c8241dce6a86579a21f` | yes |
| `_template.typ` | D | `3976ef36a1da147038b6dd51d6c73632a26454258733aac0c05502d91110a5cc` | yes |
| `index.typ` | D | `57b4af37eae8588497ecd0613d633facd0d3e1a24ad315802f4db469f638c43e` | yes |
| `output.typ` | D | `8613bc8366e60145da1c12fa1d50596cf54799bcf1adefd502d7de1248119f3d` | yes |

This is the tracer's real end-to-end signal: the architecture change (config -> registry ->
`write()` -> wrapper loop -> `render_wrapper()` -> `TemplateEngine`) produces byte-for-byte
identical output for both the custom-template shape and the nothing-set shape, confirming TPL-03's
zero-edit-equivalence claim structurally, not just by unit-test assertion. `53-RED-EVIDENCE.md`
was not modified (`git diff --name-only` does not list it) -- the full four-shape post-change
measurement remains plan 53-05's job.

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end "a wrapper is typeset from a resolved registry definition"** -
   `c35801b0` (feat)
2. **Task 2: Lock the promotion with an invariant test on render_wrapper's source region** -
   `200ec8d6` (test)
3. **Task 3: Tracer byte-identity spot-check against the wave-1 baseline** - this plan's own
   metadata commit (SUMMARY.md; no production code changed by Task 3 itself)

_No plan-metadata commit beyond the SUMMARY.md commit is included in this list -- per the
worktree-executor instructions, this plan runs inside an isolated worktree; the orchestrator
applies STATE.md/ROADMAP.md/REQUIREMENTS.md updates centrally after merge._

## Files Created/Modified

- `typsphinx/__init__.py` - registered `typst_document_templates` (default `{}`).
- `typsphinx/template_registry.py` - new module: `TemplateRegistryEntry`,
  `RESERVED_REGISTRY_KEY`, `resolve_template_registry()`, `resolve_registry_key()`.
- `typsphinx/builder.py` - `self._document_template_registry` attribute; resolution call in
  `write()`; lazy fallback and `template_entry` threading in `_write_typst_files()`.
- `typsphinx/writer.py` - `render_wrapper()`'s `template_entry` keyword parameter and the
  entry-based `TemplateEngine` construction (D-10/D-11).
- `tests/test_template_registry.py` - new test module, 15 tests.
- `.planning/phases/53-template-registry-foundation/53-02-SUMMARY.md` - this file.

## Decisions Made

- **TPL-01 is not marked complete.** TPL-01's own requirement text bundles two things: (a) named
  template definitions can be declared and resolved, and (b) `template` **xor** `package` is
  enforced. This plan's `resolve_template_registry()` deliberately performs NO validation (per the
  plan's own objective and `must_haves`) -- validation is plan 53-03's expansion (CONF-14..18).
  Only (a) is done here. `REQUIREMENTS.md`'s TPL-01 checkbox is left unchecked; the orchestrator
  should not flip it until 53-03 lands the xor check.
- The D-11 edge test (Task 2's third test) monkeypatches `TemplateEngine.__init__` inside a
  `try`/`finally` block to capture the `parameter_mapping` kwarg `render_wrapper()` actually
  passes at runtime, since `render_wrapper()` returns a rendered string, not the `TemplateEngine`
  instance itself -- this proves the D-11 behavior directly rather than relying solely on a
  source-text assertion.

## Deviations from Plan

### Auto-fixed Issues

None -- no bug, missing-critical-functionality, or blocking issue was found that required a
Rule 1/2/3 fix. Implementation followed 53-RESEARCH.md's and 53-PATTERNS.md's concrete code
sketches closely; `black` reformatted two newly-written files on first pass (whitespace/line-
wrap only, applied before commit), and `mypy typsphinx/` reported zero issues.

### Noted, Not Auto-fixed (out of scope)

**1. [Scope boundary, carried from 53-01] Pre-existing `test_state_guard_shapes_gate.py` failures**
- **Found during:** every full-suite run in this plan (`uv run pytest tests/ -q`).
- **Issue:** 7 parametrized tests fail with `FileNotFoundError` reading a path the v0.8.0
  milestone archival (`2ea4db0f`) relocated -- unrelated to this plan's scope, already logged in
  `deferred-items.md` and `WINDOWS.md` by plan 53-01.
- **Action taken:** none (already tracked). Re-confirmed the failure set is unchanged (still
  exactly these 7) across all three full-suite runs in this plan.

**2. `ruff check .` could not be run locally** -- NixOS's dynamic linker cannot execute the
`.venv`-installed `ruff` binary in this sandbox (`Could not start dynamically linked executable:
ruff`). This is a known, previously-documented CI-only defect class for this environment, not a
new finding. `black --check` and `mypy typsphinx/` were both run locally and are clean; `ruff`'s
result is deferred to the phase's CI run (SC#5).

---

**Total deviations:** 0 auto-fixed; 2 noted/deferred (both out of this plan's scope or
environment-only, neither a defect in this plan's own deliverable).

## Issues Encountered

None beyond the two noted deviations above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

The registry plumbing exists and is used end-to-end, with output unchanged for the two spot-
checked shapes and structurally unchanged for all four (via the unmodified 32-file regression
net). Plan 53-03 can now add CONF-14..18's validation on top of this proven slice without
re-deriving the resolution/threading architecture. Plan 53-05's full four-shape post-change
measurement against `53-RED-EVIDENCE.md` remains open (not this plan's job -- `53-RED-EVIDENCE.md`
was deliberately left unmodified).

One item carried forward from 53-01, unaffected by this plan: the 7 pre-existing
`test_state_guard_shapes_gate.py` failures (tracked in `WINDOWS.md`) remain unresolved.

---
*Phase: 53-template-registry-foundation*
*Completed: 2026-08-15*

## Self-Check: PASSED

- FOUND: `typsphinx/__init__.py`
- FOUND: `typsphinx/template_registry.py`
- FOUND: `typsphinx/builder.py`
- FOUND: `typsphinx/writer.py`
- FOUND: `tests/test_template_registry.py`
- FOUND: `.planning/phases/53-template-registry-foundation/53-02-SUMMARY.md`
- FOUND commit `c35801b0` (Task 1)
- FOUND commit `200ec8d6` (Task 2)
- FOUND commit `cd981e16` (Task 3 / this SUMMARY)
