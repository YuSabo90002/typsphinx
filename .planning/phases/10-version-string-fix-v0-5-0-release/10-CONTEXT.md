# Phase 10: Version-String Fix + v0.5.0 Release - Context

**Gathered:** 2026-07-11
**Status:** Ready for planning

<domain>
## Phase Boundary

**Phase 10 was RE-SCOPED during discussion** (user decision — see D-05/D-06). It is now
**release *preparation* only**, not the release itself.

**In scope (Phase 10, all on `release/v0.5.0`, no tag / no publish / no merge):**
1. Correct the version string to `0.5.0` and single-source it so it can never drift again
   (root-cause fix for the stale `0.4.3` this phase was created to correct).
2. Add a `v0.5.0` entry to `CHANGELOG.md` — the single source of truth for the release notes.
3. Prepare the curated GitHub-Release body content inside `CHANGELOG.md` (no separate notes file).

**Explicitly deferred to milestone completion (`/gsd-complete-milestone`), NOT Phase 10:**
- Merging `release/v0.5.0 → main` (PR #112 stays **open**).
- Tagging `v0.5.0`.
- `release.yml` running green on the tag → PyPI (wheel + sdist) + GitHub Release publish.

This mirrors the **v0.4.4 precedent**: v0.4.4 was published at its milestone close, not in a
dedicated release phase (PROJECT.md Key Decisions, D-11 "softprops@v3 confirmed at the v0.4.4 release").

**Out of scope (unchanged):** any new features, new reST constructs, or behavior changes — all
v0.5.0 implementation landed in Phases 6–9 + 8.1.

</domain>

<decisions>
## Implementation Decisions

### Release timing (RE-SCOPE — overrides Phase 9 D-03)
- **D-01:** **The release itself is deferred to milestone completion.** Phase 10 does NOT tag,
  publish, or merge. It only prepares the branch. The tag + `release.yml` publish + PR #112 merge
  all execute at `/gsd-complete-milestone`.
- **D-02:** This **overrides Phase 9's D-03**, which had assumed Phase 10 would add the version-bump
  commit to PR #112, merge to `main`, then tag. That assumption is retired by the user's decision.
  PR #112 (`release/v0.5.0 → main`, 13/13 jobs green, observed in Phase 9) remains **open/unmerged**.
- **D-03:** **Tag-on-release-branch is confirmed feasible** and is the intended publish mechanism at
  milestone close: git tags can point at any commit (no `main` requirement). `release.yml` fires on
  `v*` push and checks out the *tagged commit*, so tagging `release/v0.5.0` HEAD publishes correctly.
  The `git describe --tags --abbrev=0 v0.5.0^` in `release.yml`'s notes step resolves to `v0.4.4`
  because `release/v0.5.0` descends from the `v0.4.4` tag (92 commits ahead). Branch protection does
  not apply to tags. **Whether the milestone-close step tags the release branch directly or merges
  first is a milestone-close decision, not Phase 10's** — Phase 10 just leaves the branch ready.

### Version string fix + drift prevention
- **D-04:** **Single-source `__version__` via `importlib.metadata`.** Replace the hardcoded
  `__version__ = "0.4.3"` in `typsphinx/__init__.py:14` with
  `__version__ = importlib.metadata.version("typsphinx")` so `pyproject.toml`'s `version` becomes the
  **only** place a version string lives. This is the root-cause fix — the drift that left `0.4.3`
  stale becomes structurally impossible, not just corrected once.
- **D-05:** **`pyproject.toml` MUST be bumped `0.4.4 → 0.5.0`.** IMPORTANT correction surfaced during
  scout: the roadmap assumed `pyproject.toml` was already `0.5.0`, but it actually reads `0.4.4`
  (the v0.4.4 release bumped it; the v0.5.0 branch never bumped it). With single-sourcing (D-04),
  bumping `pyproject.toml` to `0.5.0` is what makes `__version__` report `0.5.0`. The `release.yml`
  version-verify gate compares tag vs `pyproject.toml`, so `0.5.0` here is also mandatory for the
  (deferred) publish to pass.

### Release notes & CHANGELOG
- **D-06:** **`CHANGELOG.md` is the single source of truth for the v0.5.0 release notes.** Add a
  v0.5.0 entry covering the milestone highlights: Sphinx 9.1 + docutils 0.22 support, typst 0.15 +
  `@preview` bumps (the `kai` fix), the admonition code-mode rendering fix (Phase 8.1), Python floor
  raised to 3.12–3.13, and the CI smoke-gate/guardrail work. At publish time (milestone close), the
  curated v0.5.0 section is passed manually to the GitHub Release body (`release.yml`'s
  `body_path`), avoiding the noisy 92-commit auto-generated `git log`. No separate release-notes
  draft file (avoids double-maintenance with CHANGELOG).

### Claude's Discretion
- Exact `importlib.metadata` implementation detail (e.g., `PackageNotFoundError` fallback for
  uninstalled/source runs) is left to research/planning — see code_context note below.
- CHANGELOG entry formatting/section granularity — follow the existing CHANGELOG.md style.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Version string sites (the core edit surface)
- `typsphinx/__init__.py` §14, §62 — hardcoded `__version__ = "0.4.3"`; `setup()` reports it as the
  extension metadata `version`. This is the string to single-source (D-04).
- `pyproject.toml` §7 — `version = "0.4.4"`; MUST bump to `0.5.0` (D-05); becomes the single source.
- `tests/test_extension.py` §56, §68 — asserts `metadata["version"] == __version__`. Today this is
  tautological (both trace to the hardcoded string) and did NOT catch the drift. Planner should
  reassess this test's value once `__version__` is single-sourced; consider a real guard that the
  built/installed distribution reports `0.5.0`.

### Release mechanism (deferred to milestone close, but plan must understand it)
- `.github/workflows/release.yml` — the publish pipeline. Key facts: fires on `v*` tag push; the
  `validate` job's "Verify version matches pyproject.toml" step compares tag vs `pyproject.toml`
  (NOT `__init__.py`); notes step uses `git describe`/`generate_release_notes`; GitHub Release uses
  `softprops/action-gh-release@v3` with `body_path: release_notes.md`. Green precedent: v0.4.4.
- `CHANGELOG.md` — the v0.5.0 entry lives here (D-06); its v0.5.0 section is the curated Release body.

### Requirements / roadmap
- `.planning/REQUIREMENTS.md` §44 (REL-01), §89, §103 — REL-01 spans BOTH the version-string fix
  AND the PyPI publish. Phase 10 completes the version-fix half; the publish half moves to milestone
  close. **REQUIREMENTS.md / ROADMAP.md Phase 10 success criteria #2 and #3 (release.yml green /
  published to PyPI) should be reconciled to reflect this split** — flag for the planner.
- `.planning/ROADMAP.md` — Phase 10 details + SC (written before the re-scope; SC #2/#3 now deferred).
- `.planning/phases/09-green-ci-matrix-smoke-test-guardrails/09-CONTEXT.md` — origin of D-03 (the
  merge-in-Phase-10 assumption now overridden by D-01/D-02).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `importlib.metadata` (stdlib, Python 3.12 floor — always available, no backport needed): the
  single-source mechanism for `__version__` (D-04).
- v0.4.4 release run (`release.yml`, tag `v0.4.4`, run 28731646924) is a green end-to-end precedent
  for the deferred publish — the pipeline is known-good on this exact workflow.

### Established Patterns
- **Version is currently duplicated** across `pyproject.toml` (`0.4.4`) and `typsphinx/__init__.py`
  (`0.4.3`) — the drift this phase eliminates. After D-04, `pyproject.toml` is canonical.
- `release.yml` version-verify only checks `pyproject.toml`, never `__init__.py` — single-sourcing
  (D-04) closes that blind spot without adding a second gate.

### Integration Points / research note
- **`importlib.metadata.version("typsphinx")` reads *installed distribution* metadata.** In the
  dev/CI flow (`uv sync` editable install) this resolves fine. Planner/researcher should confirm the
  behavior when running from an uninstalled source tree and decide whether a `PackageNotFoundError`
  fallback is warranted (common robust pattern). The package name in metadata is `typsphinx`
  (verify against `pyproject.toml [project].name`).

</code_context>

<specifics>
## Specific Ideas

- The curated CHANGELOG v0.5.0 entry should read as a user-facing summary of the milestone, not a
  commit dump. Highlight themes: "Sphinx 9 / typst 0.15 forward port", the `kai` compile fix,
  admonition rendering fix, Python 3.12–3.13 floor, CI smoke-gate + drift guardrails.

</specifics>

<deferred>
## Deferred Ideas

- **Actual v0.5.0 release execution** — merge PR #112 (or tag the release branch directly),
  tag `v0.5.0`, run `release.yml` → PyPI + GitHub Release. Deferred to `/gsd-complete-milestone`
  by explicit user decision (D-01). Not lost — it is the milestone-close deliverable.
- **ROADMAP/REQUIREMENTS SC reconciliation** — Phase 10 SC #2/#3 and REL-01's publish clause should
  be updated to reflect the prepare-vs-publish split. This is bookkeeping for the planner/transition,
  noted so it is not silently dropped.

</deferred>

---

*Phase: 10-version-string-fix-v0-5-0-release*
*Context gathered: 2026-07-11*
