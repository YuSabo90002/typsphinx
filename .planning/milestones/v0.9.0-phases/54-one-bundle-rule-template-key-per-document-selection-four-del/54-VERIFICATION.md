---
phase: 54-one-bundle-rule-template-key-per-document-selection-four-del
verified: 2026-08-16T00:00:00Z
status: passed
score: 8/8 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: no
---

# Phase 54: One Bundle Rule — `_template/<key>/`, Per-Document Selection, Four Deletions Verification Report

**Phase Goal:** The output layout changes to one rule with no exceptions — every used key's
template bundle, the resolved template's parent directory, is copied wholesale to
`<outdir>/_template/<key>/` — and element [4] therefore actually selects which template typesets
which document, because four mechanisms (`_write_template_file()`, `_copy_template_directory()`'s
`.typ` exclusion, `copy_template_assets()`'s three early returns, and `typst_template_assets` with
its two explicit-asset helpers) are deleted rather than extended.

**Verified:** 2026-08-16
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria, verbatim contract)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| SC#1 | Two masters, two templates, one build — import path independent of nesting depth (TPL-02/OUT-06) | ✓ VERIFIED | `tests/fixtures/two_key_selection_gate/` real `sphinx-build` fixture; `tests/test_two_key_selection_gate.py` (6 tests, genuinely run, no xfail) passes. `writer.py:78` `compute_template_import_path(key, filename)` returns a root-absolute `/_template/<key>/<file>.typ` string, independent of wrapper depth — verified by reading the function and its doctests, and by the passing `test_both_report_wrappers_emit_an_identical_import_string` assertion. |
| SC#2 | Every used key's bundle at `<outdir>/_template/<key>/`, `"typst"` under the same rule, no `_template.typ` anywhere, `_write_template_file()` gone, `"typst"` resolves via `importlib.resources` | ✓ VERIFIED | Repo-wide `git ls-files \| xargs grep -l "_write_template_file"` returns zero hits in tracked non-`.planning/` files. `typsphinx/template_engine.py:334-335` (`get_default_template_path()`) uses `importlib.resources.files("typsphinx") / "templates" / "base.typ"` + `as_file()`, not `Path(__file__).parent`. `builder.py:1491-1683` (`_copy_used_template_bundles()`/`_copy_bundle_directory()`) is the sole route, driven by `self._used_template_keys` (mirrors `self.images`, per ROADMAP constraint #4), correctly skipping package-only and unused keys (`tests/test_empty_typst_documents_optout_gate.py`, `tests/test_package_only_config_gate.py` — both pass). |
| SC#3 | A user template's own relative asset compiles; copy excludes exactly the four D-04 kinds via a manifest-diff test; re-run policy recorded; symlink clause retracted per D-03 | ✓ VERIFIED | `tests/fixtures/user_template_relative_asset_gate/` (genuine user `_typst/branded.typ` + `_typst/logo.png`, not the built-in template) real-compiles via `test_user_template_relative_asset_gate.py` (4 tests pass). `_is_excluded_bundle_entry()` (`builder.py:40-79`) implements exactly `.git`, `.DS_Store`, `Thumbs.db`, editor-backup suffixes — nothing more. `test_bundle_copy_exclusion_manifest_gate.py::test_bundle_manifest_is_exactly_the_expected_set` is a genuine set-equality (manifest-diff) assertion, not presence-only, and passes; `test_rerun_leaves_a_removed_source_file_in_place` proves the D-01 overwrite-in-place/no-delete policy. `grep -rn "symlink" typsphinx/*.py` (excluding `followlinks`) returns zero hits — no refusal code exists; `ROADMAP.md`'s SC#3 text and `REQUIREMENTS.md`'s BLD-06 text both carry the D-03 retraction language. |
| SC#4 | Built wheel carries the bundle; CI step opens the real wheel; package-data glob covers every file kind | ✓ VERIFIED | `pyproject.toml:77` declares `"templates/**/*"` (recursive, not `templates/*`). `.github/workflows/ci.yml` `build` job (after `uv build`) opens the built `.whl` and asserts `typsphinx/templates/README.md` is inside it. Independently reproduced: `uv build --wheel` into a scratch dir, then verified via `zipfile` that `typsphinx/templates/README.md` is present in the built wheel (not just the editable install). `typsphinx/templates/README.md` exists and documents the bundle/canary relationship. |
| SC#5 | `_template/` reserved wholesale (ExtensionError naming the docname); `template_named_dir_master` relocated with regression intent carried forward; `typst_template_assets` unregistered with a `config-inited` handler shipping in the same commit | ✓ VERIFIED | `TypstBuilder._reserves_template_prefix()` (`builder.py:573-621`) is a case-insensitive (via `_collision_key()`), plural-`_templates/`-excluding first-segment prefix check, wired into BOTH the content-path claim (step 1) and the wrapper-path claim (step 2) of `_validate_output_path_collisions()`; `tests/test_template_prefix_reservation_gate.py` (7 tests, including a case-variant test) passes. `tests/fixtures/template_named_dir_master/` no longer exists; its three regression intents (reserved-layout negative test, two-entry/two-target de-collision, per-master author-divergence) are split across `tests/fixtures/template_prefix_reservation_gate/` and `tests/fixtures/nested_dir_multi_master/`, referenced from `tests/test_multi_master_metadata_no_leak.py` and `tests/test_template_import_path.py` (both green). `git log` shows `typst_template_assets`'s `add_config_value` deletion and `app.connect("config-inited", check_config_at_init)` land in the SAME commit `0929d2da`. `typsphinx/removed_config.py` gives each of the three removed values (`typst_template_assets`, `typst_authors`, `typst_toctree_defaults`) its own bespoke message naming the replacement and the observable consequence; `tests/test_removed_config_deprecation_gate.py` (9 tests) passes. |

**Score:** 5/5 ROADMAP Success Criteria verified; 8/8 requirement IDs (TPL-02, CONF-19, OUT-04,
OUT-05, OUT-06, OUT-07, BLD-05, BLD-06) traced to passing, genuine evidence.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/builder.py` — four deleted mechanisms absent | No `_write_template_file`, `copy_template_assets`, `_copy_template_directory` (old `.typ`-excluding form), `_copy_explicit_assets`, `_copy_single_asset` | ✓ VERIFIED | `grep -n "_write_template_file\|copy_template_assets\|_copy_explicit_assets\|_copy_single_asset" typsphinx/*.py` → zero hits. `finish()` (builder.py:1685-1703) body is exactly `copy_image_files()` + `_copy_used_template_bundles()`. |
| `typsphinx/__init__.py` — `typst_template_assets` unregistered | `add_config_value("typst_template_assets", ...)` line removed | ✓ VERIFIED | `grep -n "add_config_value" typsphinx/__init__.py` lists 9 registrations, none named `typst_template_assets`. |
| `typsphinx/removed_config.py` — CONF-19 detection | New module, `config-inited` handler | ✓ VERIFIED | Exists, substantive (93 lines), wired via `app.connect("config-inited", check_config_at_init)` in `__init__.py:73`. |
| `typsphinx/builder.py` — `_copy_used_template_bundles()`/`_copy_bundle_directory()` | New bundle-copy driver, `os.walk`+`copy2`, D-04 exclusions, D-05 fatal/non-fatal split | ✓ VERIFIED | Present, substantive (~270 lines with full docstrings), wired from `finish()`, exercised by 3 real-compile gate suites. |
| `typsphinx/writer.py` — `compute_template_import_path()` | Root-absolute import path generator | ✓ VERIFIED | Present (writer.py:78-110), wired at `writer.py:507` inside `render_wrapper()`, exercised by `test_template_import_path.py`. |
| `typsphinx/templates/README.md` | BLD-05 non-`.typ` canary | ✓ VERIFIED | Exists, substantive prose, present in the actual built wheel (independently reproduced). |
| `tests/fixtures/template_named_dir_master/` | Relocated | ✓ VERIFIED (absence confirmed) | Directory no longer exists (only a stray `__pycache__`); successors `template_prefix_reservation_gate/` and `nested_dir_multi_master/` exist and are referenced from the correct tests. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `typsphinx/__init__.py:73` | `typsphinx/removed_config.py::check_config_at_init` | `app.connect("config-inited", ...)` | ✓ WIRED | Same commit `0929d2da` as the `typst_template_assets` unregistration (git-log-confirmed, not SUMMARY-trusted). |
| `builder.py write()` (per-docname loop) | `self._used_template_keys` accumulator | `.add(template_entry.key)` only for actually-written wrappers | ✓ WIRED | `builder.py:1351`, inside the entry loop that already checks `entry[0] != docname` — only entries producing a real wrapper contribute a key. |
| `builder.py finish()` | `_copy_used_template_bundles()` | direct call | ✓ WIRED | `builder.py:1702`. |
| `_copy_used_template_bundles()` | `TypstBuilder._collision_key()` | destination-collision folding | ✓ WIRED | `builder.py:1637` routes bundle-destination comparison through the same folding primitive used everywhere else, per D-14/53's Deferred Ideas instruction. |
| `_validate_output_path_collisions()` | `_reserves_template_prefix()` | both the content-path claim and the wrapper-path claim | ✓ WIRED | `builder.py` steps 1 and 2 inside the method both call `_reserves_template_prefix()` on their resolved relpath before/alongside `_claim()`. |
| `writer.py render_wrapper()` | `compute_template_import_path()` | direct call, no depth-counting fallback | ✓ WIRED | `writer.py:507`; the depth-counting `_compute_template_import_path()` staticmethod is confirmed dead (zero non-docstring callers, verified independently via grep), left in place per an explicit, documented Phase-54 deferral (not a live code path). |

### Behavioral Spot-Checks / Real-Compile Gates

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| OUT-05 user-template relative asset compiles | `uv run pytest tests/test_user_template_relative_asset_gate.py -q` | 4 passed | ✓ PASS |
| TPL-02/OUT-06 two-key selection, depth-independent import | `uv run pytest tests/test_two_key_selection_gate.py -q` | 6 passed | ✓ PASS |
| BLD-06/OUT-04 manifest-diff exclusion + re-run policy | `uv run pytest tests/test_bundle_copy_exclusion_manifest_gate.py -q` | 4 passed | ✓ PASS |
| OUT-07 prefix reservation (both content and wrapper paths, case-insensitive) | `uv run pytest tests/test_template_prefix_reservation_gate.py -q` | 7 passed | ✓ PASS |
| CONF-19 removed-config detection | `uv run pytest tests/test_removed_config_deprecation_gate.py -q` | 9 passed | ✓ PASS |
| BLD-05 wheel actually carries the canary (not just editable install) | `uv build --wheel` into scratch dir, then inspected via `zipfile` | `typsphinx/templates/README.md` present in built `.whl` | ✓ PASS |
| Full suite, once | `uv run pytest tests/ -q` | 1294 passed, 5 skipped, 0 failed | ✓ PASS |
| Format/type gates | `uv run black --check .`; `uv run mypy typsphinx/` | both clean | ✓ PASS |
| `ruff check .` | N/A | Cannot execute in this NixOS sandbox (pre-existing, documented environment limitation — the installed wheel is a generic-linux ELF the sandbox refuses to exec) | ? SKIP — see note below |

**Note on ruff:** every one of the 7 plans' SUMMARY.md files records the same "ruff cannot run
here" limitation, and this verifier independently confirmed it cannot execute either. This means
**ruff lint conformance for all of Phase 54's changes rests entirely on CI (ubuntu-latest)**, never
locally exercised across any of the 7 plans or this verification. This is a pre-existing
environment limitation, not a phase defect, but it is recorded here as the one lint gate this
verification could not independently confirm.

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| TPL-02 | 54-01, 54-04 | Per-document template selection via element [4] | ✓ SATISFIED | SC#1 evidence above; `two_key_selection_gate` fixture. |
| CONF-19 | 54-06 | Removed-config warning naming replacement + consequence | ✓ SATISFIED | `removed_config.py`, same-commit wiring confirmed via git log. |
| OUT-04 | 54-01, 54-03, 54-04, 54-05 | Every used key's bundle copied wholesale, `"typst"` same rule | ✓ SATISFIED | `_copy_used_template_bundles()`, accumulator wiring. |
| OUT-05 | 54-01, 54-04 | Template-relative asset resolves | ✓ SATISFIED | `user_template_relative_asset_gate` real compile. |
| OUT-06 | 54-01, 54-04 | Import path independent of nesting depth | ✓ SATISFIED | `compute_template_import_path()`, root-absolute. |
| OUT-07 | 54-07 | `_template/` reserved output space | ✓ SATISFIED | `_reserves_template_prefix()`, both claim sites. |
| BLD-05 | 54-02 | Non-`.typ` bundle file present in built wheel | ✓ SATISFIED | Independently reproduced wheel build + inspection. |
| BLD-06 | 54-01, 54-03, 54-04, 54-05 | Bundle copy excludes VCS/OS metadata; symlink clause retracted | ✓ SATISFIED | `_is_excluded_bundle_entry()`, manifest-diff test, D-03 retraction confirmed absent from code and present in ROADMAP/REQUIREMENTS text. |

No orphaned requirements: `REQUIREMENTS.md`'s traceability table maps exactly these 8 IDs to
Phase 54, and all 8 appear in at least one plan's `requirements:` frontmatter.

### Anti-Patterns Found

None. `git diff --name-only <pre-relocation>..HEAD -- typsphinx/` piped through a `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` grep returns zero hits across all `typsphinx/*.py` files touched this phase, and zero hits across the touched `tests/` files. The one static method left with dead-code content (`writer.py`'s `_compute_template_import_path()`) is explicitly and honestly labeled `DEAD CODE (confirmed zero non-docstring callers...)` in its own docstring, per an explicit Phase-54-CONTEXT deferral — not a hidden stub.

### Re-Verified Specific Claims (from the launch prompt)

1. **Repo-wide grep, not `builder.py`-only, for `_write_template_file()`/root `_template.typ`
   writes.** Confirmed via `git ls-files | xargs grep -l "_write_template_file"` (zero hits outside
   `.planning/`) and by reading the actual bundle-copy code path, which never writes a bare
   `_template.typ` at the outdir root.
2. **The three RED-evidence gate modules carry no `xfail` and pass genuinely.** Confirmed:
   `grep -n xfail` on all three modules returns nothing, and `uv run pytest` on all three,
   run directly (not filtered from a full run), shows 14/14 passing.
3. **CONF-19's unregistration and detection handler ship in the same commit.** Confirmed via
   `git show 0929d2da --stat` and reading the diff directly — both changes are in one commit,
   not inferred from SUMMARY prose.
4. **54-05's `test_template_assets.py` deletion audit, item 6 ("with_typst_package" claim is
   FALSE, not merely obsolete).** Independently confirmed by reading the pre-deletion
   `copy_template_assets()` body (`if typst_package: return` — an unconditional early return
   whenever a package was set, regardless of whether a template was also set) against the
   deleted test's own docstring ("assets are NOT copied when using Typst Universe packages") and
   against the new `TestBothConfiguredRouting::test_both_configured_warns_once_and_template_wins`,
   which asserts the template (including its would-be bundle) IS now copied when both are
   configured. The audit's characterization is sound.
5. **`_reserves_template_prefix()` is a genuine prefix reservation, case-insensitive, excludes
   the plural `_templates/`, wired into both claim sites.** Confirmed by reading the function body
   and its doctests directly, and by reading both call sites inside
   `_validate_output_path_collisions()` (content-path claim and wrapper-path claim), plus the
   passing case-variant test.

### Deliberate Deferrals Confirmed Genuine (not silently dropped)

- `docs/source/user_guide/output_layout.rst`, `builders.rst`, `examples/advanced.rst` still
  describe the old root `_template.typ` layout — confirmed via grep; `REQUIREMENTS.md` maps
  DOC-15/16/17 to Phase 56, matching the stated deferral.
- The BLD-06/SC#3 symlink-refusal clause is genuinely absent from code, tests, and error
  messages — confirmed via `grep -rn "symlink"` across `typsphinx/*.py` returning zero
  non-`followlinks` hits — and both `ROADMAP.md` and `REQUIREMENTS.md` carry the retraction text.
- The D-15 runtime warning for the relocated shadow-template route is genuinely absent (no
  `config-inited` or other handler checks for `<srcdir>/base.typ` existing without
  `<srcdir>/_typst/base.typ`); `CHANGELOG.md`'s `[Unreleased]` entry explicitly states "there is
  **no build-time warning**" — matches the owner's retraction.

### Process Finding (not a code defect, recorded per launch-prompt instruction)

Several plans' declared `files_modified` frontmatter diverged from the branch's actual touched
files. Most notably, `54-05-PLAN.md` declared `tests/test_two_layer_output_gate.py`,
`tests/test_package_only_config_gate.py`, `tests/test_collision_predicate_completeness_gate.py`,
`tests/test_examples_charged_ieee_gate.py`, `tests/test_docs_contract_claims_gate.py`,
`tests/fixtures/bld02_template_clobber_gate/conf.py`, and
`tests/fixtures/explicit_template_collision_gate/conf.py` as files it would modify — none of
these appear in `54-05-SUMMARY.md`'s actual `key-files: modified` list. Independent inspection
shows all 7 of these files DID get updated to the correct new bundle-path assertions, just by
`54-07`'s commits instead of `54-05`'s (`54-07-SUMMARY.md`'s modified list includes
`bld02_template_clobber_gate/conf.py` and `explicit_template_collision_gate/conf.py`; the
remaining files carry correctly-updated `_template/`-prefixed assertions in the current tree and
all pass when run directly). This is a plan/summary bookkeeping inaccuracy — work landed in a
different plan's commits than declared — not a functional gap: the full suite is green, every
individually re-run test file listed above passes, and no assertion was found still expecting the
deleted root-level `_template.typ` layout.

### Human Verification Required

None. Every observable truth was verified against genuine, independently-re-run tests and direct
code/git-history inspection rather than SUMMARY.md claims.

### Gaps Summary

None. All 5 ROADMAP Success Criteria and all 8 requirement IDs are backed by real, substantive,
wired code, independently re-run passing tests (not merely SUMMARY.md assertions), and correct
git-history evidence for the same-commit CONF-19 requirement. The one open item — REQUIREMENTS.md
checkboxes for these 8 IDs and ROADMAP.md's Phase 54 checkbox remain unchecked, and STATE.md still
shows "Phase 54 planned" / 0 of 7 plans — reflects that this verification runs before the
phase-completion bookkeeping step, consistent with this project's normal workflow (compare Phase
53's pattern of dedicated "mark complete" commits landing after its own verification). It is not a
gap in the phase's actual deliverable.

---

_Verified: 2026-08-16_
_Verifier: Claude (gsd-verifier)_
