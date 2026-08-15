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
| _(populated from PLAN.md task IDs after planning)_ | | | | | | | | | ⬜ pending |

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
| D-14/D-15 | Shadow route resolves at `<srcdir>/_typst/base.typ` (never `<srcdir>/` itself), and a stray `<srcdir>/base.typ` warns | unit + integration | `tests/test_template_engine.py` (relocated plant dir) + `tests/test_typst_lang_gate.py:624,632` (relocated fixture) + the CONF-19 warning test | ✅ files exist, need relocation + new assertions |

*Test module names above are Claude's discretion per CONTEXT.md; only the shape is fixed here.*

---

## Wave 0 Requirements

- [ ] `tests/fixtures/<two-key-selection-fixture>/` + its test module — covers TPL-02
- [ ] `tests/<removed-config-deprecation-warning>.py` — covers CONF-19 and D-15's stray-`base.typ` warning
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
CONTEXT.md D-14/D-15 — the guard is structural (the shadow moves into `_typst/`), so its regression
coverage is the two relocation items above plus D-15's warning test, not a separate guard fixture.*

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
