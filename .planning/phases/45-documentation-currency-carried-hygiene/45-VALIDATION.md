---
phase: 45
slug: documentation-currency-carried-hygiene
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-09
---

# Phase 45 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `45-RESEARCH.md` § Validation Architecture. Task-level rows are filled
> once `45-*-PLAN.md` exists; `/gsd-validate-phase` promotes `status` to `validated`.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml`, `[tool.pytest.ini_options]`) |
| **Config file** | `pyproject.toml` (`testpaths = ["tests"]`) |
| **Quick run command** | `uv run pytest tests/test_changelog_extraction.py tests/test_template_engine.py::TestDeriveTypstLang tests/test_typst_lang_gate.py -v` |
| **Full suite command** | `uv run pytest` then `uv run black --check .` && `uv run ruff check .` && `uv run mypy typsphinx/` |
| **Estimated runtime** | ~60 seconds (quick ~5s; full suite + lint/type ~60s; `tox -e docs-pdf` adds ~1–2 min) |

> **Worktree note (CLAUDE.md):** executors run in isolated git worktrees. Provision first with
> `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, then run **every** command
> above via `uv run`. Without this, pytest imports the unchanged main-tree package and gates stay
> green/red misleadingly.

---

## Sampling Rate

- **After every task commit:** Run the quick run command, plus `uv run black --check .` and
  `uv run ruff check .` on touched files.
- **After every plan wave:** Run the full suite command (pytest + black + ruff + mypy).
- **Phase gate (before `/gsd-verify-work`):** both `uv run tox -e docs-html` and
  `uv run tox -e docs-pdf` run live, output captured as evidence for DOC-12's "build clean" bar;
  plus the QUA-03 opener-stack script output recorded verbatim.
- **Max feedback latency:** 60 seconds for the code path; docs builds are wave/phase-gated, not
  per-task.

---

## Per-Task Verification Map

*Seeded at requirement level — task IDs are bound after `45-*-PLAN.md` is written.*

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | DOC-11 | — | N/A (docs-only) | build-check | `uv run pytest tests/test_default_typst_documents_gate.py -v` (+ a Quick-Start-mirroring fixture asserting the emitted PDF is `<project>.pdf`, not `index.pdf`) | ✅ precedent: `tests/fixtures/default_typst_documents_gate/`, `tests/test_default_typst_documents_gate.py` | ⬜ pending |
| TBD | TBD | TBD | DOC-12 | — | N/A | build-check | `uv run tox -e docs-html` then grep rendered HTML for each of the 12 version strings (0.4.4 … 0.7.0); `uv run tox -e docs-pdf` then extract PDF text and grep the same | ❌ W0 — no test asserts changelog page content coverage | ⬜ pending |
| TBD | TBD | TBD | DOC-12 | — | N/A | build-check | Capture stdout/stderr of both `sphinx-build` invocations; assert zero `WARNING:` lines referencing `changelog`, as a **delta against a pre-phase baseline capture** (pre-existing unrelated warnings are out of fence — see RESEARCH Pitfall 2) | ❌ W0 — net-new | ⬜ pending |
| TBD | TBD | TBD | DOC-12 | — | N/A | structural | Inspect the diff: `docs/source/changelog.rst` after this phase contains ONLY the `include::` directive plus framing sections, zero release-specific content (proves the Phase 46 `0.7.1` entry is a one-line `CHANGELOG.md` addition) | N/A — code review of diff, no test possible pre-Phase-46 | ⬜ pending |
| TBD | TBD | TBD | QUA-02 | — | N/A | structural | Range-scoped grep over `derive_typst_lang()`'s line span in `typsphinx/template_engine.py` → exactly one `logger.warning(` call site | ❌ W0 (optional — see Wave 0 Requirements) | ⬜ pending |
| TBD | TBD | TBD | QUA-02 | — | N/A | regression | `uv run pytest tests/test_template_engine.py::TestDeriveTypstLang tests/test_typst_lang_gate.py -v` green **before and after** the refactor — both files assert warning content, not merely absence of crash, so a green run on both sides *is* the baseline-identity proof | ✅ existing coverage sufficient | ⬜ pending |
| TBD | TBD | TBD | QUA-03 | — | N/A | verification | Fence/backtick-aware opener-stack scan of `.planning/PROJECT.md` (script in RESEARCH § Code Examples) → `len(stack) == 0`. A naive `<!--`/`-->` count is **not** valid (D-09). | ✅ script exists in RESEARCH; re-run and record at execution time | ⬜ pending |
| TBD | TBD | TBD | (SC#5 regression guard) | — | N/A | full-suite | `uv run pytest` green + `black --check .` + `ruff check .` + `mypy typsphinx/` clean; no `typsphinx/` behaviour change beyond QUA-02 | ✅ existing full suite is the guard | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] A build-check asserting the rendered changelog page (HTML and/or extracted PDF text) contains
      all 12 previously-missing versions (`0.4.4` through `0.7.0`) — no such test exists today.
- [ ] A build-check capturing zero `WARNING:` lines attributable to the changelog page from both
      `docs-html` and `docs-pdf` builds — delta-against-baseline, since pre-existing warnings
      elsewhere in the docs build are outside this phase's fence.
- [ ] *(Optional, low value)* A structural one-liner asserting `derive_typst_lang()` contains exactly
      one `logger.warning(` call. The existing `caplog`/GATE-01 regression tests already prove
      behavioural identity; this only adds belt-and-suspenders coverage for the "exactly one site"
      grep requirement, which manual code review at plan-verification time equally satisfies.
- [ ] **No new test infrastructure for QUA-03.** D-07 explicitly declines a standing recurrence
      guard; the opener-stack scan is a one-off diagnostic — run once, record the result, do not add
      it to the pytest suite.

*Framework install: none needed — pytest is fully configured. The only new tooling dependency this
phase adds is `myst-parser>=5.0`, and it belongs in the `docs` extra of
`[project.optional-dependencies]` only — **not** `[project].dependencies` (D-01's zero-new-runtime-
dependency invariant). Note the version floor: `myst-parser` 4.x caps `sphinx<9`/`docutils<0.22`,
both violated by this repo's `sphinx>=9.1,<10` / `docutils>=0.21,<0.23` pins.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Quick Start reads accurately to a human | DOC-11 | "A reader is not surprised" is a comprehension property; the automated fixture proves the *behaviour* matches, not that the *prose* explains it | Read README Quick Start top-to-bottom against the real build output; confirm it states (a) what `typst_documents` does, (b) when it must be set, (c) the derived default incl. the `<project>.typ` name shape, (d) that an explicit setting overrides the default, (e) which documents become PDFs |
| Changelog page heading nesting in the PDF outline | DOC-12 | Cosmetic rendering quality under the myst include + Phase 44.1's relative heading-depth offset — no compile-fatal risk, but only a real build shows it (RESEARCH Open Question 1) | After `tox -e docs-pdf`, open the PDF outline and confirm changelog release headings nest sensibly rather than flattening or over-indenting |
| Shortcut-reference-link rendering of `[0.7.0]`-shaped headings | DOC-12 | CommonMark resolves these against `CHANGELOG.md`'s own tail link definitions; mechanically fine (translator handles `reference` nodes) but visual acceptability is a judgement call (RESEARCH Open Question 2) | Inspect the rendered HTML and PDF headings; confirm linked headings are acceptable or suppress the link definitions |
| Phase 46 one-line-addition property | DOC-12 | Cannot be tested before Phase 46 exists | Confirm by diff inspection that adding a `0.7.1` section to `CHANGELOG.md` alone would surface on the docs page with no `changelog.rst` edit |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
