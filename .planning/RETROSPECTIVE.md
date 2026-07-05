# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v0.4.4 — CI-repair + modernize

**Shipped:** 2026-07-05
**Phases:** 5 | **Plans:** 15 | **Sessions:** ~2 days (2026-07-04 → 2026-07-05)

### What Was Built
- Runtime dependency graph pinned back to a known-good, reproducible combination (`typst>=0.14.1,<0.15`, `sphinx<9`, `docutils<0.22`), with regenerated `uv.lock` and mirrored tox ceilings — the actual bug fix for the `kai` PDF-compile break.
- A fully green CI pipeline confirmed by observed Actions runs: 3-OS × Python 3.10–3.13 matrix (19 jobs), coverage, and `docs.yml` end-to-end incl. the multi-language PDF-copy step.
- Modernized Python floor (3.10–3.13) and conservatively refreshed dev tooling + node24 artifact actions.
- Durability guardrails: `uv sync --locked` (DUR-01), standalone `drift.yml` weekly/dispatch detector (DUR-02), scoped `sphinx-typst-stack` Dependabot group (DUR-03), README CI badge (DUR-04).
- An automated `@preview` version-sync guard test protecting the 3-way hardcoded-version hazard.

### What Worked
- **Land-the-fix-alone sequencing.** Phase 1 pinned deps *alone* before any modernization, so the first green CI run was an unambiguous attribution of the fix. Every later phase rode on a confirmed-green baseline.
- **Empirical pin confirmation over assumption.** The exact typst 0.14.x patch was confirmed in CI rather than guessed, and PIN-06 explicitly recorded whether the sphinx/docutils ceilings were load-bearing vs precautionary.
- **Push→observe terminal gates.** Each phase closed with a real PR + observed CI run (PRs #104/#105/#106) rather than a local "should be green" assertion.
- **Guardrails as a first-class phase.** Making anti-recurrence its own phase (5) meant the milestone shipped with the drift class *actively prevented*, not just fixed.

### What Was Inefficient
- **Branch/main drift at close.** The milestone-finalization docs commits lived on the phase branch, 4 ahead of `origin/main`, while local `main` sat 74 behind — extra reconciliation was needed at milestone close. Fetch + fast-forward `main` immediately after each PR merge would avoid this.
- **Version-label mismatch.** GSD's internal milestone counter (`v1.0`) diverged from the project's real semver (`v0.4.4`), requiring a reconciliation pass across STATE/PROJECT at close. Set the milestone label to the intended release number at milestone *start*.
- **tox env-name mismatch surfaced late.** The `py3.10` vs `py310` mapping bug failed 9/12 matrix jobs and needed a Phase 2 gap-closure wave; a cheap local matrix-name lint could have caught it in Phase 1.

### Patterns Established
- **Floor + ceiling on every dependency bump.** After the unbounded-resolution rot, all deps (runtime and dev) now carry explicit upper bounds, mirrored between `pyproject.toml` and `tox.ini`.
- **Automated sync guards for hardcoded duplication.** Where a value is intentionally duplicated (the 3-way `@preview` versions), a CI test asserts equality rather than relying on human memory.
- **Release tag = live PyPI publish.** A `v*` tag triggers `release.yml`, which validates the tag against `pyproject.toml` version before publishing — so version bumps must precede tags.

### Key Lessons
1. **Pin the whole graph, not just the culprit.** The break came from a *transitive* `@preview` package under a new compiler major; only bounding the direct trio (typst/sphinx/docutils) *and* committing the lockfile makes CI reproducible.
2. **Sequence risk so red/green is attributable.** Landing the fix alone before modernization made every subsequent failure trivially traceable to the change that caused it.
3. **Set the milestone version label to the real release number up front** to avoid a rename pass at close.
4. **Guardrails belong in the milestone that fixed the rot**, not a vague "later" — `drift.yml` + `--locked` + scoped Dependabot make this exact class of silent drift fail loudly next time.

### Cost Observations
- Model mix: not tracked this milestone.
- Sessions: ~2 calendar days of focused work.
- Notable: heavy use of push→observe CI gates meant wall-clock was dominated by GitHub Actions runs, not local iteration.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v0.4.4 | ~2 days | 5 | First GSD-managed milestone; established push→observe terminal gates and floor+ceiling dependency discipline |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v0.4.4 | ~400 (existing suite) + `@preview` sync guard | uploaded to Codecov (green) | 0 new runtime deps |

### Top Lessons (Verified Across Milestones)

1. Pin the whole dependency graph and commit the lockfile — reproducibility is the anti-rot mechanism. *(v0.4.4)*
2. Sequence changes so a red/green CI result is unambiguously attributable to one change. *(v0.4.4)*
