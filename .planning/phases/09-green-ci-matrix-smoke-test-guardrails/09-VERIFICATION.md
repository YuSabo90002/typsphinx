---
phase: 09-green-ci-matrix-smoke-test-guardrails
verified: 2026-07-11T07:59:34Z
status: passed
score: 8/8 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 9: Green CI Matrix + Smoke Test + Guardrails Verification Report

**Phase Goal:** Every CI lane goes green on an observed Actions run across the full matrix, a `typst compile`
smoke test guards against future `kai`-class breaks slipping past the internal-only sync test, and the
durability guardrails are bumped to the new majors.
**Verified:** 2026-07-11T07:59:34Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | An observed Actions run shows every job green — lint, 3-OS × Python 3.12–3.13 test matrix, type-check, coverage, build, docs.yml build-docs (Roadmap SC1 / CI-01) | ✓ VERIFIED | Live `gh pr checks 112 --repo YuSabo90002/typsphinx` re-run during this verification returns 13/13 `pass`: Lint and Format Check, Type Check, Code Coverage, Build Package, Integration Test basic/advanced, all 6 "Test Python {3.12,3.13} on {ubuntu,windows,macos}-latest" legs, and `build-docs` (docs.yml). `gh pr view 112` confirms `state=OPEN`, `mergeable=MERGEABLE`, `mergeStateStatus=CLEAN`. Matches SUMMARY 09-02 exactly. |
| 2 | A `typst compile` smoke test is wired into CI that would fail loudly on a `kai`-class `@preview` break (Roadmap SC2 / CI-02) | ✓ VERIFIED | `tests/test_preview_smoke_gate.py` exists, gates only on `TYPST_AVAILABLE` (no pypdf import — `grep` for `pypdf\|PdfReader\|extract_text` returns nothing), calls `typst.compile(...)` unwrapped (no try/except). `uv run pytest tests/test_preview_smoke_gate.py -v` → 1 passed locally. Confirmed running inside the observed PR #112 matrix legs (per SUMMARY, corroborated by job success). |
| 3 | `drift.yml` ceilings and the `sphinx-typst-stack` Dependabot group reflect `sphinx<10`/`typst<0.16`/`docutils<0.23` (Roadmap SC3 / CI-03) | ✓ VERIFIED | `pyproject.toml` L28-30 declares `sphinx>=9.1,<10`, `docutils>=0.21,<0.23`, `typst>=0.15.0,<0.16` exactly. `.github/workflows/drift.yml` has no hardcoded `sphinx<`/`typst<`/`docutils<` ceiling (`uv lock --upgrade` derives its ceiling from pyproject). `.github/dependabot.yml`'s `sphinx-typst-stack` group carries only `patterns`/`exclude-patterns`, no version fields. This is a documented no-op per pre-existing D-06 decision (09-CONTEXT.md), not a gap — the guardrails already reflected the new majors from Phases 6/7. |
| 4 | The smoke fixture's `.. math::` block genuinely routes through mitex's runtime code path (not merely `#import`) | ✓ VERIFIED | Independently reproduced the negative-control during this verification: built the fixture, forced `@preview/mitex:0.2.7` → `0.2.5` in a scratch copy of the generated `index.typ`, ran `typst.compile()` — reproduced `unknown variable: kai` exactly as claimed in 09-01-SUMMARY.md. Generated `index.typ` (unmodified) contains both `#import "@preview/mitex:0.2.7": mi, mitex` and a real invocation `mitex(`e^{i \pi} + 1 = 0`)`. |
| 5 | `main` branch-protection `required_status_checks.contexts` reconciled to current `ci.yml`/`docs.yml` job names — stale 3.10/3.11 contexts removed | ✓ VERIFIED | `gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks --jq '.contexts'` returns exactly `["Test Python 3.12 on ubuntu-latest","Lint and Format Check","Type Check","Code Coverage","Build Package","Test Python 3.13 on ubuntu-latest"]` — no stale 3.10/3.11 contexts, matches the documented AFTER state in 09-02-SUMMARY.md. Other protection fields (`enforce_admins`, `required_conversation_resolution`, `allow_force_pushes`, `allow_deletions`) confirmed unchanged from BEFORE. |
| 6 | The observation PR (#112) is open and NOT merged (D-03 — merge deferred to Phase 10) | ✓ VERIFIED | `gh pr view 112 --json state` returns `OPEN`. Correctly left unmerged per phase scope — this is the intended outcome, not a gap (per verification_notes). |
| 7 | No `.github/workflows/*.yml` trigger was edited during Phase 9 (D-02) | ✓ VERIFIED | `git log --oneline fa38214^..206288f -- .github/workflows/` (the full phase-9 commit range) returns zero commits touching `.github/workflows/`. The pre-existing `release/v0.5.0` vs `main` diff on `ci.yml` (3.10/3.11 → 3.12/3.13) predates Phase 9 (landed in Phase 6) and is unrelated to this phase's commits. |
| 8 | `tests/fixtures/preview_smoke/index.rst` contains all three directive types (note, code-block, math) exercising all four `@preview` packages | ✓ VERIFIED | `grep -n` confirms exactly one `.. note::`, one `.. code-block:: python`, and one `.. math::` block present. Full local suite regression: `uv run pytest tests/ -q` → 412 passed (matches SUMMARY's claimed count, includes the new test). `black --check`, `ruff check`, `mypy typsphinx/` all clean. |

**Score:** 8/8 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tests/fixtures/preview_smoke/conf.py` | Sphinx fixture config, `index` as master doc, `typst_use_mitex` left at default `True` | ✓ VERIFIED | Present, declares `typst_documents = [("index", "index", ...)]`, no `typst_use_mitex = False` override; contains rationale comment per D-04. |
| `tests/fixtures/preview_smoke/index.rst` | Fixture content with note/code-block/math directives | ✓ VERIFIED | Present, all three directive types confirmed. |
| `tests/test_preview_smoke_gate.py` | Pytest module: sphinx-build → typst.compile(), gated on TYPST_AVAILABLE only | ✓ VERIFIED | Present, 113 lines, no pypdf/PdfReader/extract_text; `typst.compile()` called unwrapped; test passes locally (`1 passed`). |
| PR `release/v0.5.0 → main` (#112) | Open, all-green process artifact | ✓ VERIFIED | Confirmed live via `gh pr view`/`gh pr checks` — OPEN, 13/13 checks pass, MERGEABLE/CLEAN. |
| `09-02-SUMMARY.md` with job conclusions, PR#, branch-protection decision | Documentation of process artifacts | ✓ VERIFIED | Present, matches live GitHub state exactly (cross-checked, no discrepancy found). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `.. math::` directive | `mitex(`...`)` invocation | translator → writer template → generated `.typ` | ✓ WIRED | Generated `index.typ` contains both the `#import "@preview/mitex:0.2.7"` and a real `mitex(`e^{i \pi} + 1 = 0`)` call — confirmed by direct build during this verification. |
| `tests/test_preview_smoke_gate.py` | existing `tox -e py312/py313` → `pytest tests/` glob in `ci.yml` | zero workflow-file edits | ✓ WIRED | No workflow file diff in phase-9 commit range; PR #112's matrix-leg job logs (per SUMMARY, corroborated by job success) show the new test executing inside the existing test job — rides the glob for free. |
| `main` branch protection `required_status_checks.contexts` | current `ci.yml`/`docs.yml` job names | `gh api ... PATCH` reconciliation | ✓ WIRED | Live GET confirms contexts list contains only real, currently-producible job names. |
| `pull_request:[main]` trigger | both `ci.yml` and `docs.yml` | PR #112 firing both workflows against release-branch content | ✓ WIRED | Confirmed two distinct run IDs observed on PR #112 (`29145206169` for ci.yml, `29145206171` for docs.yml), both showing all-green conclusions live. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Smoke test passes locally | `uv run pytest tests/test_preview_smoke_gate.py -v` | `1 passed` | ✓ PASS |
| Full suite has no regression | `uv run pytest tests/ -q` | `412 passed` (matches SUMMARY) | ✓ PASS |
| Lint/format/type clean | `uv run black --check`, `uv run ruff check`, `uv run mypy typsphinx/` | all clean | ✓ PASS |
| Negative-control reproduction (independent re-run) | build fixture → force `mitex:0.2.7`→`0.2.5` in scratch `.typ` → `typst.compile()` | `unknown variable: kai` (matches SUMMARY exactly) | ✓ PASS |
| PR #112 live state | `gh pr checks 112`, `gh pr view 112 --json state,mergeable,mergeStateStatus` | 13/13 pass; OPEN/MERGEABLE/CLEAN | ✓ PASS |
| Branch protection live state | `gh api repos/YuSabo90002/typsphinx/branches/main/protection/required_status_checks` | contexts match reconciled list, no stale 3.10/3.11 | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| CI-01 | 09-02-PLAN.md | Every CI job green, confirmed by observed Actions run | ✓ SATISFIED | PR #112 live re-check: 13/13 checks pass, matrix + lint + type + coverage + build + integration + docs all green. |
| CI-02 | 09-01-PLAN.md | `typst compile` smoke test catching `kai`-class breaks | ✓ SATISFIED | `tests/test_preview_smoke_gate.py` exists, passes, gated correctly, negative-control independently reproduced. |
| CI-03 | 09-02-PLAN.md | Durability guardrails reflect new majors | ✓ SATISFIED | `pyproject.toml` ceilings confirmed; `drift.yml`/`dependabot.yml` confirmed no conflicting ceilings — documented no-op per pre-existing D-06 decision. |

No orphaned requirements — REQUIREMENTS.md maps only CI-01/02/03 to Phase 9, and both plans jointly declare all three in frontmatter.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | None found | — | `grep` for TBD/FIXME/XXX/TODO/HACK/PLACEHOLDER/"not yet implemented" across all 3 new files returned no matches. |

### Human Verification Required

None. The two `checkpoint:human-verify` tasks in 09-02-PLAN.md (branch-protection reconciliation, PR observation) were executed under delegated orchestrator authorization during the phase and their outcomes are independently re-confirmed as live, current GitHub state in this verification pass (not merely trusted from SUMMARY narrative) — `gh api`/`gh pr` calls were re-run fresh, not read from cached SUMMARY text.

### Gaps Summary

No gaps found. All three phase requirements (CI-01, CI-02, CI-03) are independently verified against live GitHub state and the local codebase, not merely accepted from SUMMARY claims:

- The PR #112 checks were re-queried live (not read from SUMMARY) and match exactly.
- The branch-protection reconciliation was re-queried live and matches exactly.
- The negative-control proof (the one claim in the SUMMARIES that is inherently non-reproducible via static grep) was independently re-executed in this verification session and reproduced the identical `unknown variable: kai` error.
- The smoke test was re-run locally and passes.
- No workflow-trigger files were touched in the phase-9 commit range (D-02 honored).
- The PR being open/unmerged is the correct, intended state (D-03) — not treated as a gap.

Phase 9 goal is achieved: the full CI matrix is observed green on a real Actions run, the CI-02 smoke gate is proven (not just present) to catch the historical `kai`-class regression, and the CI-03 guardrails are confirmed already at the new majors with no conflicting ceilings elsewhere.

---

_Verified: 2026-07-11T07:59:34Z_
_Verifier: Claude (gsd-verifier)_
