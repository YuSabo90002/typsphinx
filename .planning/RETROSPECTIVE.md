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

## Milestone: v0.5.0 — forward-ecosystem

**Shipped:** 2026-07-11
**Phases:** 6 (6–10 + 8.1 inserted) | **Plans:** 13 | **Sessions:** ~6 days (2026-07-05 → 2026-07-11)

### What Was Built
- Runtime pins raised forward to the current ecosystem — `sphinx>=9.1,<10`, `docutils>=0.21,<0.23`, `typst>=0.15.0,<0.16`, Python floor 3.12–3.13 — across all 21 declaration sites, with `uv.lock` regenerated.
- The four bundled `@preview` packages bumped in lockstep (mitex 0.2.7, gentle-clues 1.3.1, codly-languages 0.1.10, codly 1.3.0), empirically closing the `unknown variable: kai` compile break — root-caused to mitex 0.2.6+, not the originally-suspected gentle-clues/codly.
- Soft-deprecated docutils/Sphinx API modernized (`traverse()`→`findall()`, `OptionParser`→`get_default_settings`, `builder.app`→`_app`, `writer_name`→`writer=get_writer_class`) with a permanent `filterwarnings` guard escalating both `DeprecationWarning` and `PendingDeprecationWarning`.
- A long-latent admonition markup/code-mode render bug fixed (Phase 8.1, inserted) — `info[...]`→`info({...})` code-mode blocks + inline-markup-preserving titles + five previously-missing admonition types + a real `sphinx-build → typst.compile → pypdf` acceptance gate.
- A `typst compile` smoke gate exercising all four `@preview` packages via real calls (incl. `.. math::` through mitex), closing the coverage gap the historical `kai` regression slipped through — proven with a negative control.
- Version single-sourced via `importlib.metadata` (stale `0.4.3` retired, `pyproject.toml` sole literal), curated `CHANGELOG.md` `[0.5.0]` entry, released to PyPI + GitHub Release.

### What Worked
- **Atomic risk-grouping.** FWD-02 (typst re-pin) was deliberately grouped with the `@preview` bump in one phase/wave rather than the pin-raise — raising typst alone would have left CI red on `kai`. The `kai` gate closed on the *first* real `docs-pdf` compile, no bisect needed.
- **Empirical gates over changelog inference.** The `kai` root cause (mitex 0.2.6+) was confirmed by a real compile, not trusted from changelogs — and it overturned the v0.4.4-era gentle-clues/codly suspicion.
- **Insert-a-phase for an orthogonal bug.** The admonition render bug surfaced mid-milestone (only visible once `docs-pdf` first compiled post-`kai`-fix); making it Phase 8.1 with its own acceptance gate kept it from contaminating the pin-raise phases.
- **Prep/publish split at the release boundary.** Phase 10 did prep-only; the irreversible publish (merge → tag → PyPI) was gated to milestone close on the exact CI-green merge commit — mirroring v0.4.4 and giving a clean go/no-go.
- **Milestone audit before close.** A dedicated `/gsd-audit-milestone` pass (14/14 requirements, 5/5 integration seams, E2E release-flow readiness) caught nothing broken but confirmed cross-phase wiring before the irreversible publish.

### What Was Inefficient
- **Sandbox environment friction.** The NixOS dynamically-linked `uv` binary couldn't launch in subprocess tests, producing ~45 environment-caused failures that had to be independently traced and distinguished from real regressions in every phase — a recurring per-phase verification tax. A documented in-sandbox `uv` shim/patch earlier would have saved repeated re-analysis.
- **VALIDATION.md drafts left non-compliant.** Every phase carries a `nyquist_compliant: false` draft VALIDATION.md; the Nyquist step-hook was inactive so they never gated, but they add audit noise. Either activate the hook or stop emitting the drafts.

### Patterns Established
- **Group the compiler bump with its package bumps.** A compiler-major raise and its ecosystem-package bumps must land atomically — splitting them guarantees a red intermediate state.
- **Every render-layer fix needs a real-render acceptance gate.** Unit asserts on emitted markup missed the admonition bug for months; only a `compile → extract-text → no-leak` gate proves typeset output.
- **Audit-then-publish for irreversible releases.** Run the milestone audit and confirm E2E release-flow readiness *before* the merge/tag/publish that can't be undone.

### Key Lessons
1. **Confirm root cause by reproduction, not changelog.** The `kai` culprit was misattributed for a whole prior milestone; one real compile settled it.
2. **A green unit suite ≠ correct rendered output.** Latent render bugs hide behind markup-level asserts until something actually compiles the output end-to-end.
3. **Split reversible prep from irreversible publish.** Keeping the PyPI/tag/merge step at milestone close, on the confirmed-green commit, makes the point of no return an explicit, auditable gate.
4. **Escalate the full deprecation-warning family.** `PendingDeprecationWarning` (Sphinx's `RemovedInSphinxNN`) must be caught alongside `DeprecationWarning` to see forward-deprecation signals early.

### Cost Observations
- Model mix: not tracked this milestone.
- Sessions: ~6 calendar days; wall-clock dominated by push→observe CI runs and repeated sandbox-failure triage.
- Notable: a mid-milestone inserted phase (8.1) absorbed an orthogonal bug without derailing the pin-raise sequence.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v0.4.4 | ~2 days | 5 | First GSD-managed milestone; established push→observe terminal gates and floor+ceiling dependency discipline |
| v0.5.0 | ~6 days | 6 (incl. 1 inserted) | Forward-port to Sphinx 9.1/typst 0.15; added real-render acceptance gates + a mid-milestone inserted phase; audit-then-publish for the irreversible release |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v0.4.4 | ~400 (existing suite) + `@preview` sync guard | uploaded to Codecov (green) | 0 new runtime deps |
| v0.5.0 | 413 (added smoke gate, PDF-render gate, version drift-guard, admonition structural asserts) | green (13/13 CI jobs on PR #112) | 0 new runtime deps (pypdf is dev-only) |

### Top Lessons (Verified Across Milestones)

1. Pin the whole dependency graph and commit the lockfile — reproducibility is the anti-rot mechanism. *(v0.4.4)*
2. Sequence changes so a red/green CI result is unambiguously attributable to one change. *(v0.4.4, reaffirmed v0.5.0 — atomic compiler+package bump)*
3. Confirm dependency root causes by reproduction, not changelog inference. *(v0.5.0 — overturned the v0.4.4-era `kai` attribution)*
4. A green unit suite doesn't prove correct rendered output — render-layer fixes need a compile→extract→assert acceptance gate. *(v0.5.0)*
5. Split reversible prep from the irreversible publish; gate the point-of-no-return at milestone close on a confirmed-green commit. *(v0.4.4 precedent, formalized v0.5.0)*
