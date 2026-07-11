# Phase 10: Version-String Fix + v0.5.0 Release - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-11
**Phase:** 10-version-string-fix-v0-5-0-release
**Areas discussed:** Release timing (merge/tag), Version fix + drift prevention, Release notes & CHANGELOG, Publish path

---

## Area selection

User selected all four proposed areas via multiSelect AND added a scoping note:
"PRのマージはマイルストーンコンプリートのタイミングで実施することとし、このフェーズではマージを実施しないようにできないか" — surfacing the merge-timing decision that reshaped the phase.

---

## Merge & Tag strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Tag release branch, defer merge | Bump on `release/v0.5.0`, tag its HEAD, publish; PR #112 stays open; merge at `/gsd-complete-milestone` | |
| Merge then tag (D-03) | Add bump to PR #112, merge to `main`, tag on `main` | |

**User's choice:** "そもそもリリースも遅延すべきだ" — escalated further: **defer the entire release (tag + publish), not just the merge.**
**Notes:** Reshapes Phase 10 into release *preparation only*. Overrides Phase 9 D-03. Confirmed technically feasible to tag the release branch at milestone close (tags aren't main-bound; `release.yml` checks out the tagged commit; `v0.4.4` resolves as previous tag).

## Version fix + drift prevention

| Option | Description | Selected |
|--------|-------------|----------|
| Single-source via importlib.metadata | `__version__ = importlib.metadata.version("typsphinx")`; pyproject.toml is the only truth | ✓ |
| Equality test | Keep two strings; add a test asserting `__init__` == `pyproject` | |
| Just fix both to 0.5.0 | No guard, minimal change | |

**User's choice:** importlib.metadata single-sourcing (recommended).
**Notes:** Scout surfaced that `pyproject.toml` is `0.4.4` (not `0.5.0` as roadmap assumed) and `__init__.py` is `0.4.3` — both must reach `0.5.0`; single-sourcing makes the drift structurally impossible.

## Release notes & CHANGELOG

| Option | Description | Selected |
|--------|-------------|----------|
| CHANGELOG update + curated notes | Add v0.5.0 entry to CHANGELOG.md; use it for the GitHub Release body | ✓ |
| CHANGELOG only | Update CHANGELOG, let release.yml auto-generate notes | |
| Auto-generated only | No manual work; noisy 92-commit git-log notes | |

**User's choice:** CHANGELOG update + note curation (recommended).
**Notes:** Follow-up confirmed CHANGELOG.md is the single source of truth; no separate release-notes draft file. Curated section handed to `release.yml body_path` manually at publish (milestone close).

## Publish path (PyPI)

| Option | Description | Selected |
|--------|-------------|----------|
| Straight to production PyPI | Tag v0.5.0 direct to prod | |
| TestPyPI rc dry-run first | v0.5.0rc1 → TestPyPI, then v0.5.0 → prod | |

**User's choice:** "遅延" — defer the publish entirely (consistent with deferring the whole release to milestone close). The prod-vs-TestPyPI choice itself is therefore a milestone-close decision, not Phase 10's.

## Phase re-scope confirmation

**User's choice:** "はい、この再構成で確定" — Phase 10 = version fix + guard + CHANGELOG/notes prep only; tag/publish/merge at `/gsd-complete-milestone`. SC #2/#3 move to milestone close; REL-01 split accordingly.

---

## Claude's Discretion

- Exact `importlib.metadata` implementation (PackageNotFoundError fallback for source-tree runs) — deferred to research/planning.
- CHANGELOG entry formatting — follow existing CHANGELOG.md style.

## Deferred Ideas

- Actual v0.5.0 release execution (merge/tag/publish) → `/gsd-complete-milestone`.
- ROADMAP/REQUIREMENTS success-criteria reconciliation for the prepare-vs-publish split → planner/transition bookkeeping.
