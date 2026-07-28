---
phase: 35
slug: v0-6-5-release-prep
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-07-29
---

# Phase 35 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded by `/gsd-plan-phase 35` from `35-RESEARCH.md` § Validation Architecture.
> The Per-Task Verification Map is filled in once PLAN.md files exist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (verified live in 35-RESEARCH.md § Validation Architecture) |
| **Config file** | `pyproject.toml` — `[tool.pytest.ini_options]` (no separate `pytest.ini`) |
| **Quick run command** | Wave 1: `uv run pytest tests/test_inline_math_after_text_render_gate.py -q` · Wave 2: `uv run pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -q` |
| **Full suite command** | `uv run python -m pytest -q --tb=no -rf` |
| **Estimated runtime** | Quick set: render gate spawns 2 `sphinx-build` + `typst.compile()` subprocesses (~tens of seconds). Full suite: multi-minute — it **already includes** the `@pytest.mark.slow` full-corpus gate (see Pitfall below). |

**Pitfall (measured this phase, RESEARCH.md):** `tests/test_corpus_gate.py`'s docstring claims the slow
class is "excluded from the default/CI fast suite via `-m 'not slow'`". **That claim is false** — no
config in this repo applies that filter, so a plain `pytest -q` runs the corpus gate and every slow
test. Do not plan a separate "now also run the slow tests" step on the assumption they were skipped;
scope SC#3 evidence accordingly.

**Environment prerequisite (MANDATORY):** worktree-isolated execution is this repo's standing mode.
When `.git` is a FILE, every command below must be preceded by
`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` and run through `uv run`.
Sphinx is always invoked as `sys.executable -m sphinx` — never a compiled console script
(NixOS sandbox hazard; already handled inside the existing gate tests).

---

## Sampling Rate

- **After every task commit:** the wave's quick run command above.
- **After every plan wave:** `uv run python -m pytest -q --tb=no -rf` (full suite).
- **Before `/gsd-verify-work`:** full suite green, plus `uv run black --check .` /
  `uv run ruff check .` / `uv run mypy typsphinx/` clean, plus `tox -e docs-html` and
  `tox -e docs-pdf` (D-12), plus the SC#4 mechanical diff assertions and the SC#5 no-tag proof.
- **Max feedback latency:** ~tens of seconds (quick set), multi-minute (full suite / corpus gate).

---

## Phase Requirements → Test Map

| Req / SC | Behavior | Test Type | Automated Command | File Exists |
|----------|----------|-----------|-------------------|-------------|
| REL-03 · SC#1 | `pyproject.toml` / `uv.lock` / README version literals agree; `typsphinx.__version__` reports `0.6.5` | unit | `uv run pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -q` + `uv sync --extra dev --locked` | ✅ |
| REL-03 · SC#2 | CHANGELOG carries a curated `## [0.6.5]` entry **and** the tail link block rolled over | manual / prose | N/A — no machine check for CHANGELOG prose exists in this repo | N/A (expected) |
| REL-03 · SC#3 | Post-bump tree green end to end on a live run | integration / build | `uv run python -m pytest -q --tb=no -rf`; `uv run black --check .`; `uv run ruff check .`; `uv run mypy typsphinx/`; `uv run tox -e docs-html`; `uv run tox -e docs-pdf` | ✅ |
| REL-03 · SC#4 | Milestone invariants proven mechanically over the full diff | integration (git-diff) | `git diff eb696bb..HEAD -- pyproject.toml uv.lock`; `git diff eb696bb..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ examples/`; `uv run pytest tests/test_preview_version_sync.py -q` | ✅ |
| REL-03 · SC#5 | No irreversible publish action taken | integration (git state) | `git tag -l v0.6.5`; `git ls-remote --tags origin v0.6.5` — **both must print nothing** | ✅ |
| adjacent (D-05/06/07) | WR-02 / WR-03 / WR-04 gate-test gaps closed | unit / regression | `uv run pytest tests/test_inline_math_after_text_render_gate.py -q` | ✅ (file exists; needs Construct G + 3 assertions) |

**SC#4 anchoring rule:** anchor on the merge-base **SHA `eb696bb`**, never on a commit count. The
count drifted from CONTEXT.md's recorded 33 to 36 between discuss-phase and planning (planning-only
commits); the substantive non-planning diff is unchanged.

---

## Per-Task Verification Map

Filled by `/gsd-plan-phase 35` once the five PLAN.md files existed. Every task carries an
`<automated>` verify; there are no Wave 0 gaps and no `MISSING` references.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 35-01/T1 | 35-01 | 1 | REL-03 (adjacent: D-05/D-06/D-07) | T-35-03 | Fixture growth cannot smuggle a `typsphinx/` edit | unit / regression | `uv run python -m pytest tests/test_inline_math_after_text_render_gate.py -q` + `grep -c 'construct-g-labeled-eq' tests/fixtures/inline_math_after_text_render_gate/index.rst` = 1 + `git diff --name-only -- typsphinx/` empty | ✅ | ⬜ pending |
| 35-01/T2 | 35-01 | 1 | REL-03 (adjacent: WR-02/03/04) | T-35-01, T-35-02 | Each new assertion is proven fail-capable; no existing assertion weakened | unit / regression | `uv run python -m pytest tests/test_inline_math_after_text_render_gate.py -q` + per-assertion one-character perturbation RED→GREEN recorded | ✅ | ⬜ pending |
| 35-02/T1 | 35-02 | 1 | REL-03 (D-05/D-10) | T-35-04 | Deferral is recorded, not lost | doc structure | `ls .planning/todos/pending/*-visit-math-block-redundant-blank-line-in-list-items.md` = 1 + frontmatter/section greps + `git diff --name-only -- typsphinx/ tests/ .github/` empty | ✅ | ⬜ pending |
| 35-02/T2 | 35-02 | 1 | REL-03 (D-11) | T-35-05, T-35-06 | `release.yml` recorded but never edited | doc structure | `ls .planning/todos/pending/*-release-notes-body-from-changelog-section.md` = 1 + frontmatter/section greps + `git diff --name-only -- .github/` empty | ✅ | ⬜ pending |
| 35-03/T1 | 35-03 | 2 | REL-03 · SC#1 | T-35-08 | Version identity is single-valued across surfaces | unit (source assertion) | `grep -c '^version = "0.6.5"$' pyproject.toml` = 1, old literal = 0, `grep -c 'Stable (v0.6.5)' README.md` = 1, old = 0 | ✅ | ⬜ pending |
| 35-03/T2 | 35-03 | 2 | REL-03 · SC#1, SC#4 | T-35-07, T-35-09, T-35-SC | Lock regeneration cannot silently re-resolve a transitive dependency | unit + CLI | `uv sync --extra dev --locked` exit 0; `uv run python -c "import typsphinx; print(typsphinx.__version__)"` = `0.6.5`; `uv run pytest tests/test_readme_version_sync.py tests/test_preview_version_sync.py -q`; `git diff --numstat uv.lock` = 1/1 | ✅ | ⬜ pending |
| 35-04/T1 | 35-04 | 3 | REL-03 · SC#2 (D-01–D-04) | T-35-10, T-35-11, T-35-12 | Entry cannot overstate the fix or carry a false invariant clause | doc structure (awk-scoped section greps) | section-scoped: `### Fixed` bullets = 1, `### Verified` bullets = 3, no Added/Changed/Removed, no break label, `## [Unreleased]` count = 2 | ✅ | ⬜ pending |
| 35-04/T2 | 35-04 | 3 | REL-03 · SC#2 | T-35-12, T-35-13 | Naming a tag is not creating one | doc structure + git state | `grep -c '^\[0\.6\.5\]: …/releases/tag/v0\.6\.5$'` = 1; `tail -n 1 CHANGELOG.md` compares from v0.6.5; `git diff --numstat CHANGELOG.md` = 1 deletion; `git tag -l v0.6.5` empty | ✅ | ⬜ pending |
| 35-05/T1 | 35-05 | 4 | REL-03 · SC#3 (D-12) | T-35-15, T-35-18, T-35-SC | Evidence is live-run only; docs builds leave the tree clean | integration / build | full `pytest -q --tb=no -rf`; `black --check .`; `ruff check .`; `mypy typsphinx/`; isolated corpus gate; `tox -e docs-html`; `tox -e docs-pdf`; `git status --porcelain -- docs/` empty | ✅ | ⬜ pending |
| 35-05/T2 | 35-05 | 4 | REL-03 · SC#4, SC#5 (D-04) | T-35-14, T-35-15, T-35-16 | Invariants anchored on SHA `eb696bb`, never on a commit count | integration (git-diff / git-state) | `git diff --numstat eb696bb..HEAD -- pyproject.toml` = 1/1 and same for `uv.lock`; four-surface diff empty; `uv run pytest tests/test_preview_version_sync.py -q`; `git tag -l v0.6.5` and `git ls-remote --tags origin v0.6.5` empty | ✅ | ⬜ pending |
| 35-05/T3 | 35-05 | 4 | REL-03 (D-08/D-09/D-10) | T-35-14, T-35-17 | Handoff stands alone; fence proof re-run at a second moment | doc structure + git state | `grep -c '^### [1-6]\.'` = 6; names `typsphinx-doc-translations`, `.planning/REQUIREMENTS.md`, both todo filenames; both no-tag checks empty; `git diff --name-only -- .planning/REQUIREMENTS.md typsphinx/ docs/ .github/` empty | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**SC#4 expected-result correction (measured at planning time, supersedes 35-RESEARCH.md's table):**
RESEARCH.md recorded `git diff eb696bb..HEAD -- pyproject.toml uv.lock` as **empty**. That was measured
*before* the version bump. After plan 35-03 lands, both diffs are **non-empty by exactly one line each**
(the package version key). The SC#4 assertion is therefore a numstat of `1` insertion / `1` deletion per
file plus an unchanged dependency array — not an empty diff. A plan or verifier expecting emptiness here
would report a false breach.

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No new fixture project, conftest fixture,
test framework, or test dependency is needed.

The only test-file *content* gaps (WR-02 Construct G, WR-03 / WR-04 assertions) are this phase's own
Wave 1 deliverable, not a pre-phase infrastructure gap.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `## [0.6.5]` CHANGELOG entry reads correctly in user-visible terms | REL-03 · SC#2 | CHANGELOG prose is not machine-checked anywhere in this repo | Read the new entry against D-01–D-04: one general `### Fixed` sentence with representative contexts in parentheses, no BREAKING label, lead paragraph + `### Fixed` + `### Verified` (3 items) |
| Tail link block rollover is correct | REL-03 · SC#2 | Link-block shape is prose, not asserted by a test | Confirm a `[0.6.5]: …/releases/tag/v0.6.5` line was added and `[Unreleased]:` now points at `v0.6.5...HEAD` |
| `35-HANDOFF.md` is complete and readable standalone | D-09 | Document-quality judgement | Check the six known items from CONTEXT.md `<specifics>` are all present, including the second-repository tag (D-08) |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies — all 11 tasks carry `<automated>`
- [x] Sampling continuity: no 3 consecutive tasks without automated verify — zero gaps
- [x] Wave 0 covers all MISSING references — no `MISSING` reference exists; all machinery pre-exists
- [x] No watch-mode flags — every command is one-shot
- [x] Feedback latency acceptable (quick set ~tens of seconds; the 35-05 evidence set is multi-minute by nature)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** plan-phase (2026-07-29). `status` stays `draft` until `/gsd-validate-phase` sets it.
