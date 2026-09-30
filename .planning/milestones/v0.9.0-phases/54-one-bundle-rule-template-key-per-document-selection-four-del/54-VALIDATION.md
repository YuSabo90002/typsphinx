---
phase: 54
slug: one-bundle-rule-template-key-per-document-selection-four-del
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-15
---

# Phase 54 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded by plan-phase from `54-RESEARCH.md` § Validation Architecture. The Per-Task
> Verification Map is populated from the PLAN.md task IDs once planning completes.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest ≥8.4 (`pyproject.toml:35`) |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`, `pyproject.toml:75-84`) |
| **Quick run command** | `uv run pytest tests/test_<module>.py -x` |
| **Full suite command** | `uv run pytest tests/ -q` |
| **Estimated runtime** | ~110 seconds full suite (measured baseline: `1270 passed, 5 skipped in 109.29s`) |

**Worktree note (CLAUDE.md, standing execution mode):** every command above runs via `uv run`
inside the executor's own worktree, provisioned first with
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`. Without that, pytest imports the
unchanged main-tree package and gates stay RED after a correct fix.

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/test_<touched_module>.py -x`
- **After every plan wave:** Run `uv run pytest tests/ -q`, plus the three CI-matching gates —
  `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/`
- **Before `/gsd-verify-work`:** Full suite green, plus
  `git ls-remote --heads origin gsd/v0.9.0-per-document-templates` confirming the milestone branch
  is current (standing milestone invariant #5, paid every phase since Phase 43)
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-1 | 54-01 | 1 | OUT-05 | T-54-02 | user-template asset gate is a real compile, not a synthetic assertion | integration (RED-first) | `uv run pytest tests/test_user_template_relative_asset_gate.py -x` | ❌ created by this task | ⬜ pending |
| 01-2 | 54-01 | 1 | TPL-02, OUT-06, BLD-06, OUT-04 | T-54-02, T-54-11 | manifest-diff equality, excluded kinds materialised at runtime not committed | integration (RED-first) | `uv run pytest tests/test_two_key_selection_gate.py tests/test_bundle_copy_exclusion_manifest_gate.py` | ❌ created by this task | ⬜ pending |
| 01-3 | 54-01 | 1 | — | — | wave closes green with recorded xfails | suite | `uv run pytest tests/ -q` | ✅ | ⬜ pending |
| 02-1 | 54-02 | 1 | BLD-05 | T-54-12, T-54-14 | wheel content asserted by opening the artifact, not by reading the glob | packaging | `uv build` + `zipfile` namelist assertion | ✅ pyproject.toml | ⬜ pending |
| 02-2 | 54-02 | 1 | BLD-05 | T-54-13 | a later glob narrowing fails the CI job by name | CI config | YAML step-order assertion in `<verify>` | ✅ .github/workflows/ci.yml | ⬜ pending |
| 03-1 | 54-03 | 1 | BLD-06 | T-54-15, T-54-17, T-54-18 | scoped edits only; no checkbox flipped; diff capped | doc assertion | `grep -c symlink .planning/REQUIREMENTS.md` == 0 | ✅ | ⬜ pending |
| 03-2 | 54-03 | 1 | OUT-04 | T-54-16 | relocation announced in docs and changelog | doc assertion | `uv run pytest tests/test_docs_contract_claims_gate.py tests/test_output_layout_docs_gate.py -q` | ✅ | ⬜ pending |
| 04-1 | 54-04 | 2 | TPL-02, OUT-04, OUT-05, OUT-06 | T-54-01, T-54-02, T-54-04, T-54-06, T-54-07, T-54-10, T-54-19 | no resolved template's parent may be srcdir; destination case-collision refused; fatal-vs-warn split | integration (tracer) | `uv run pytest tests/test_user_template_relative_asset_gate.py tests/test_two_key_selection_gate.py tests/test_bundle_copy_exclusion_manifest_gate.py tests/test_template_engine.py --runxfail` | ❌ Wave 1 creates the gates | ⬜ pending |
| 04-2 | 54-04 | 2 | OUT-06 | T-54-01 | bare-filename template relocated out of srcdir root in-tree | suite migration | `uv run pytest tests/ -q --runxfail` | ✅ | ⬜ pending |
| 04-3 | 54-04 | 2 | TPL-02, OUT-05, OUT-06, BLD-06 | — | RED-recorded gates pass with no marker mediating | suite | `uv run pytest tests/ -q` | ✅ | ⬜ pending |
| 05-1 | 54-05 | 3 | OUT-04 | T-54-20 | the both-configured warning survives the method's deletion | source assertion + suite | `git grep -n "_write_template_file" -- typsphinx` == 0 | ✅ | ⬜ pending |
| 05-2 | 54-05 | 3 | OUT-04, BLD-06 | T-54-21 | eight-row coverage audit before the module is deleted | source assertion + suite | `uv run pytest tests/test_bundle_copy_exclusion_manifest_gate.py -q` | ✅ | ⬜ pending |
| 05-3 | 54-05 | 3 | OUT-04 | T-54-22 | fixture rationales preserved across comment rewrites | suite | `uv run pytest tests/ -q` | ✅ | ⬜ pending |
| 06-1 | 54-06 | 4 | CONF-19 | T-54-09, T-54-25, T-54-26 | warning severity, no subtype, defensive raw-namespace read | unit (introspection) | `uv run python -c` introspection block in `<verify>` | ❌ created by this task | ⬜ pending |
| 06-2 | 54-06 | 4 | CONF-19 | T-54-23, T-54-24 | loud test failure if the detection mechanism disappears | unit (caplog / subprocess) | `uv run pytest tests/test_removed_config_deprecation_gate.py -q` | ❌ created by this task | ⬜ pending |
| 06-3 | 54-06 | 4 | CONF-19 | T-54-09 | no page instructs setting a value the extension rejects | doc assertion | `git grep -n typst_template_assets -- docs/source/user_guide CLAUDE.md` == 0 | ✅ | ⬜ pending |
| 07-1 | 54-07 | 4 | OUT-07 | T-54-05, T-54-27, T-54-28 | prefix reservation is a separate predicate routed through the one folding primitive | unit + integration | `uv run pytest tests/test_typst_documents_collision_gate.py tests/test_collision_predicate_completeness_gate.py tests/test_two_key_selection_gate.py -q` | ✅ | ⬜ pending |
| 07-2 | 54-07 | 4 | OUT-07 | T-54-05, T-54-21, T-54-29 | refusal names every offender and leaves no partial output; three fixture intents preserved | integration (negative) | `uv run pytest tests/test_template_prefix_reservation_gate.py -q` | ❌ created by this task | ⬜ pending |
| 07-3 | 54-07 | 4 | OUT-07 | T-54-21 | both path references repointed in the same commit as the move | suite | `uv run pytest tests/ -q` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

### Requirement → verification shape (from 54-RESEARCH.md)

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TPL-02 | Two masters naming two different registry keys produce two visibly-different-template PDFs in one build | integration (real `sphinx-build -b typstpdf`) | `uv run pytest tests/<two-key-selection-gate>.py -x` | ❌ Wave 0 — new two-key fixture |
| CONF-19 | A `conf.py` still setting a removed value gets a named `logger.warning` | unit (caplog) | `uv run pytest tests/<removed-config-deprecation>.py -x` | ❌ Wave 0 |
| OUT-04 | Every used key's bundle lands at `_template/<key>/`; `"typst"` under the same rule; a `package`-only or unused key copies nothing | integration (real `sphinx-build`, filesystem assertions) | `uv run pytest tests/<bundle-copy-layout-gate>.py -x` | ❌ Wave 0 |
| OUT-05 | A NEW **user-supplied** template's `#image("logo.png")` compiles green via real `typst.compile()`, recorded RED pre-relocation | integration (GATE-01-shaped real compile) | `uv run pytest tests/<user-template-relative-asset-gate>.py -x` | ❌ Wave 0 — fixture does not exist yet |
| OUT-06 | Root master and nested master naming the SAME key emit an identical import string | unit or integration | Extends `tests/test_template_import_path.py` | ✅ file exists, needs new assertions |
| OUT-07 | A source tree writing under `_template/` stops the build, naming the docname | integration (negative) | Successor fixture to `template_named_dir_master` + its test | ❌ Wave 0 |
| BLD-05 | The built wheel contains a non-`.typ` bundle file | CI-only (not pytest) | New step in `.github/workflows/ci.yml`'s `build` job (D-13) | ❌ Wave 0 (CI step, not a test file) |
| BLD-06 | Copy excludes exactly the four D-04 kinds; asserted manifest-diff, not presence-only | integration (fixture containing `.git`, `.DS_Store`, `Thumbs.db`, an editor backup) | `uv run pytest tests/<bundle-copy-exclusion-manifest-gate>.py -x` | ❌ Wave 0 |
| D-14 | Shadow route resolves at `<srcdir>/_typst/base.typ`, never `<srcdir>/` itself | unit + integration | `tests/test_template_engine.py` (relocated plant dir) + `tests/test_typst_lang_gate.py:624,632` (relocated fixture) | ✅ files exist, need relocation + new assertions |

*Test module names above are Claude's discretion per CONTEXT.md; only the shape is fixed here.*

---

## Wave 0 Requirements

- [ ] `tests/fixtures/<two-key-selection-fixture>/` + its test module — covers TPL-02
- [ ] `tests/<removed-config-deprecation-warning>.py` — covers CONF-19
- [ ] `tests/<bundle-copy-layout-gate>.py` — covers OUT-04, including the `package`-only-copies-nothing
      and unused-key-copies-nothing cases
- [ ] `tests/fixtures/<user-template-relative-asset-fixture>/` + its test module — covers OUT-05,
      **must be recorded RED against the pre-relocation tree** per SC#3 (a genuine GATE-01-shaped real
      `sphinx-build → typst.compile()` fixture, not a synthetic assertion). The built-in template is
      explicitly not accepted as evidence.
- [ ] `tests/fixtures/<template_named_dir_master successor>/` — covers OUT-07's negative case AND carries
      forward the three regression intents enumerated in CONTEXT.md § Claude's Discretion
      (G-22.1-4/CR-01, BLD-02/OUT-01, CONF-09)
- [ ] `tests/<bundle-copy-exclusion-manifest-gate>.py` — covers BLD-06, manifest-diff shaped, fixture
      containing `.git`, `.DS_Store`, `Thumbs.db`, and at least one editor-backup-shaped file
- [ ] `.github/workflows/ci.yml` `build` job step — covers BLD-05 (a CI step per D-13, not a pytest file)
- [ ] A test that fails loudly if `sphinx.config.Config._raw_config` disappears, per D-06
- [ ] Relocation of `tests/fixtures/typst_lang_gate/srcdir_shadow_lang/base.typ` →
      `.../srcdir_shadow_lang/_typst/base.typ`, keeping `tests/test_typst_lang_gate.py:624,632` green by
      relocation rather than rewrite (D-14)

*Open Question #1 from 54-RESEARCH.md (the `srcdir`-shadow whole-tree-copy risk) is **resolved** by
CONTEXT.md D-14 — the guard is structural (the shadow moves into `_typst/`), so its regression
coverage is the two relocation items above, not a separate guard fixture. The runtime warning
originally drafted as D-15 was removed by owner decision; the relocation is announced by docs and
changelog only.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| "Two **visibly different** templates" | TPL-02 | "Visibly different" is a rendering judgement a byte-comparison cannot make; the automated test asserts the two PDFs differ and that each imported its own key's bundle | Open both PDFs from the two-key fixture's build and confirm the two typeset differently (e.g. different fonts/margins), not merely that the bytes differ |
| Wheel contents in a real release | BLD-05 | The CI step asserts on a locally-built wheel; the published artifact is only observable after `release.yml` runs | After a release, `pip download typsphinx==<version> --no-deps` and confirm `typsphinx/templates/README.md` is inside the `.whl` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
