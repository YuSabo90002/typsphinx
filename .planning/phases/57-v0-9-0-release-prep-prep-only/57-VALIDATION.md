---
phase: 57
slug: v0-9-0-release-prep-prep-only
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-16
---

# Phase 57 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded by plan-phase from `57-RESEARCH.md` § "Validation Architecture".

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (config in `pyproject.toml` `[tool.pytest.ini_options]`), `tox` as task runner |
| **Config file** | `pyproject.toml`, `tox.ini` |
| **Quick run command** | `uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` |
| **Full suite command** | `uv run pytest tests/ -v` (local spot-check) — **authority for lint/type/matrix is the dispatched CI run**, per D-13 |
| **Estimated runtime** | quick ~5s; full local suite ~4–6 min (1366 passed / 5 skipped at the Phase 56 baseline); a CI dispatch ~7 min |

**Authority note (D-12 / D-13, as amended).** The dispatched `ci.yml` run is SC#3's authority for
pytest / `black` / `ruff` / `mypy` because it is the only route to the **Windows and macOS lanes**,
which caught a real cp1252 defect at the v0.7.0 close and a real path-separator defect at the v0.7.1
close. This phase dispatches **twice** — once pre-bump, once post-bump — so "this milestone's code
fails on another platform" stays separable from "the bump broke something".

`ruff` **does** now run locally (`uv run ruff check .` → `All checks passed!`, exit 0, ruff 0.15.20 —
re-measured 2026-08-16; the CONTEXT's contrary premise is amended). Running it locally before a
dispatch is encouraged as a cheap pre-flight, but it does **not** move authority off CI.

**Hard sequencing constraint (D-13, count amended to 10).** `uv sync --extra dev --locked` opens
every CI job — 10 steps across four workflows (`ci.yml` ×6, `release.yml` ×2, `docs.yml` ×1,
`drift.yml` ×1). `uv.lock` must be regenerated **and committed before either dispatch**, or the
install step fails and no test, lint or type signal is produced at all. Two live dependabot PRs
(#128, #123) are failing in exactly this way.

---

## Sampling Rate

- **After every task commit:** the relevant guard-test subset — the version-sync trio for the bump
  task; `tests/test_changelog_page_gate.py` for the CHANGELOG tasks; `tests/test_two_key_selection_gate.py`
  for the D-14 re-run task.
- **After every plan wave:** `uv run pytest tests/ -v` locally as a spot-check — never presented as
  authority for lint/matrix (that is CI, per D-13). `uv run ruff check .` may accompany it.
- **Before `/gsd-verify-work`:** both dispatched CI runs all-green, **plus** `tox -e docs-html` and
  `tox -e docs-pdf`, **plus** `tests/test_corpus_gate.py` recorded as PASSED or honestly SKIPPED —
  never conflated. **A `pytest.skip` is not evidence.**
- **Max feedback latency:** ~5 s for the quick guard subset; ~7 min for a CI dispatch.

---

## Per-Task Verification Map

Task rows are filled in once `57-*-PLAN.md` files exist. The requirement-level map below is the
contract each task row must inherit from.

| Req / SC | Behavior | Test Type | Automated Command | File Exists |
|----------|----------|-----------|-------------------|-------------|
| REL-08 SC#1 | Version literals move in lockstep; `typsphinx.__version__` reports `0.9.0` | unit | `uv run pytest tests/test_extension.py::test_version_matches_pyproject_toml tests/test_readme_version_sync.py tests/test_preview_version_sync.py -v` | ✅ |
| REL-08 SC#2 | Curated `## [0.9.0]` entry, `### Removed` bullet, tail-block rollover, migration guide, `RELEASE_VERSIONS` current | integration | `uv run python scripts/extract_changelog_section.py 0.9.0` + `uv run pytest tests/test_changelog_page_gate.py -v` | ✅ |
| REL-08 SC#3 (toolchain) | Post-bump tree green: pytest / lint / type, both docs envs, built-wheel content check | integration/e2e | two dispatched `ci.yml` runs + `tox -e docs-html` + `tox -e docs-pdf` | ✅ |
| REL-08 SC#3 (goal claim) | Multi-template round trip proven on two differently-typeset PDFs | e2e/gate | `uv run pytest tests/test_two_key_selection_gate.py -v` — re-run per D-14, **no new gate authored** | ✅ permanent |
| REL-08 SC#4 (fence) | No `v0.9.0` tag local or remote; no publish — probed twice at separated times | script | `git tag -l v0.9.0` + `git ls-remote --tags origin v0.9.0` (×2) | ✅ commands |
| REL-08 SC#4 (invariants) | Milestone-diff invariants asserted; `REQUIREMENTS.md` checksum guards the auto-flip | script | `git diff v0.8.0..HEAD` hunk-level argument + `sha256sum .planning/REQUIREMENTS.md` at phase start and close | ✅ commands |
| REL-08 SC#5 | `57-HANDOFF.md` standalone and complete; REL-08 stays `[ ]` | manual + script | `git diff --name-only -- .planning/REQUIREMENTS.md` empty throughout | ✅ |
| D-10 (as amended) | Zero stale prerequisites / dead config links outside `.planning/` and historical `CHANGELOG.md` | script | repo-wide discovery grep re-run **at execution time**, against `pyproject.toml:10` / `:28` as truth source | ✅ commands |

*Status legend: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

**Existing infrastructure covers all phase requirements.** Every test module and fixture this phase
needs is already in the repository — `test_extension.py`, `test_readme_version_sync.py`,
`test_preview_version_sync.py`, `test_changelog_page_gate.py`, `test_two_key_selection_gate.py` (with
`tests/fixtures/two_key_selection_gate/`), `test_corpus_gate.py`, and
`scripts/extract_changelog_section.py`.

No Wave 0 is required. The only genuinely new authored content is prose — the
`Migrating from 0.8.x to 0.9.0` section in `docs/source/changelog.rst` — which **D-07 deliberately
leaves ungated**, and the `## [0.9.0]` CHANGELOG entry, which is bound only by
`test_changelog_page_gate.py`'s `RELEASE_VERSIONS` tuple once `"0.9.0"` is added to it.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The `## [0.9.0]` entry reads as curated prose, not a generated dump — headline names the registry, four `**Breaking:**` bullets each carry a migration sentence | REL-08 SC#2 (D-01…D-05) | Editorial quality is not machine-checkable; the gate only proves the section exists and is non-empty | Read the rendered `## [0.9.0]` section and the output of `scripts/extract_changelog_section.py 0.9.0` — they must be the same text, and it is the exact body that becomes the GitHub Release |
| The migration guide's "before" side matches a real pre-change tree | REL-08 SC#2 (D-08) | Deliberately ungated by D-07 | `git worktree add --detach <dir> v0.8.0`, provision it with its **own** `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, run one `-b typst` build, transcribe the actual file tree |
| `57-HANDOFF.md` is complete and standalone | REL-08 SC#5 | Completeness of a checklist against a future action is a judgement | Walk each item against `52-HANDOFF.md` / `46-HANDOFF.md`; confirm the second-repo pin advances via `update-pin.yml` `workflow_dispatch`, not by hand |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or are listed under Manual-Only above
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references — *N/A, none missing*
- [ ] No watch-mode flags
- [ ] Feedback latency < 420 s (one CI dispatch)
- [ ] `uv.lock` regenerated and committed **before** the first CI dispatch (D-13 sequencing)
- [ ] `test_corpus_gate.py` outcome recorded as PASSED or SKIPPED, never conflated
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
