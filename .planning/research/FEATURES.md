# Feature Research

**Domain:** CI/CD maintenance & dependency-pin repair (Python package, Sphinx extension)
**Researched:** 2026-07-04
**Confidence:** HIGH (repo/workflow inspection) / MEDIUM (exact known-good `typst` + `@preview` version combo — needs empirical verification, not just research)

This is not a "what features does a docs tool need" landscape — it's a maintenance milestone. "Features" below means **CI/release acceptance items**: the concrete, checkable conditions that let a maintainer say "CI is repaired and durable" and close the milestone.

## Feature Landscape

### Table Stakes (Must Be True To Call CI Restoration Done)

Each row maps 1:1 to an actual job in `.github/workflows/{ci,docs,release}.yml`.

| Feature (acceptance item) | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| `black --check .` exits 0 on full tree | `ci.yml` job `lint` (`tox -e lint`); `release.yml` job `validate` runs the same check | TRIVIAL | 3 files currently fail: `docs/build_multilang.py`, `tests/test_config_other_options.py`, `tests/test_config_toctree_defaults.py`. Run `black .` to reformat, then verify `--check`. Do this **after** any black `target-version` bump (see Python modernization row) to avoid reformatting twice. |
| `ruff check .` exits 0 on full tree | Same `lint` job; same `release.yml validate` job | TRIVIAL | Currently passing per failure evidence (only black flagged 3 files); re-verify after Python floor bump since `UP035/UP006/UP028` ignores are justified by 3.9 support and may become removable (not required, just don't let removal introduce new failures if attempted). |
| `mypy typsphinx/` exits 0 | `ci.yml` job `type-check`; `release.yml validate` | TRIVIAL–LOW | Currently passing (per PROJECT.md failure evidence: "Type Check ... jobs currently pass"). Must not regress when `python_version` in `[tool.mypy]` is bumped from `"3.9"` to the new floor (`"3.10"`). |
| All 12 matrix jobs green: `test` (ubuntu/macos/windows × 3.10/3.11/3.12/3.13) | `ci.yml` job `test`; this is the job most directly broken (`unknown variable: kai`) | INVOLVED | Blocked on the `typst`/`@preview` package pin decision (see Dependencies). Also blocked on `tox.ini` env_list update (`py39,py310,...` → drop `py39`, add `py313`) and `ci.yml` matrix `python-version` list update. Cascades from a single root cause (typst 0.15 resolving) — once the pin lands, most of these should go green together. |
| `coverage` job green (`tox -e cov`) | `ci.yml` job `coverage`; same test suite as above plus coverage instrumentation | INVOLVED | Same root cause as matrix tests — the 7 failing PDF-integration tests invoke `typst` compilation. Blocked by the same pin fix; no independent work once matrix tests pass. |
| `build` job green (`uv build` + `twine check`) | `ci.yml` job `build`; also duplicated in `release.yml build` | TRIVIAL | Currently passing per failure evidence ("Build Package jobs currently pass"). Must not regress — verify after `requires-python`/classifiers changes (setuptools must still discover package correctly with `requires-python=">=3.10"`). |
| `integration` job green (basic + advanced examples) | `ci.yml` job `integration` | LOW | Uses `sphinx-build -b typst` (not `-b typstpdf`), so it does **not** invoke the Typst compiler and is likely unaffected by the `kai` compile error — verify this assumption holds; if it already passes, this is a "keep green" item, not a "fix" item. |
| `docs.yml build-docs` job green: HTML (multilang) + PDF build | Separate workflow, but PDF step (`tox -e docs-pdd`, i.e. `sphinx-build -b typstpdf`) hits the identical `typst` compile path as the failing tests | INVOLVED | Same root-cause dependency as matrix/coverage. `docs-multilang` (HTML) step runs `python build_multilang.py` — this file is one of the 3 needing a black reformat; reformatting must not change its runtime behavior. |
| `release.yml validate` job stays valid (tests, black, ruff, mypy all run and would pass if triggered) | This job duplicates the same lint/test/type checks inline (not via tox) — it is the release gate; a green `ci.yml` does not guarantee this job is equally green since it invokes tools directly (`uv run pytest`, `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/`) | LOW | Cannot be exercised end-to-end without pushing a real version tag; treat as "inspect for drift and dry-run the four commands locally/in a scratch branch" rather than a live CI run. No code changes expected here beyond what already fixes `ci.yml`. |
| Runtime dependencies pinned to a reproducible known-good set (`typst` back to a 0.14.x line compatible with `codly:1.3.0`, `codly-languages:0.1.1`, `mitex:0.2.4`, `gentle-clues:1.2.0`) plus `sphinx`/`docutils` upper bounds | Root cause of the entire breakage: loose `>=` pins let CI silently absorb `sphinx==9.0.4`, `docutils==0.22.4`, `typst==0.15.0` — none compatible with the bundled `@preview` packages | INVOLVED | The riskiest item — requires empirically testing `typst` 0.14.x patch versions against the pinned `@preview` packages (this research pass could not confirm the exact good combination from public docs/search; `kai` doesn't appear in typsphinx source, so it's internal to a `@preview` package as compiled by 0.15 — see PROJECT.md Context). Must land **before** matrix/coverage/docs-PDF jobs can go green. |
| `uv.lock` regenerated and committed to match the final pin set | Constraint from PROJECT.md: "`uv.lock` must be regenerated to match the new pins; tox/uv drives all CI checks" | TRIVIAL (mechanical) / LOW (verification) | Must be regenerated **once**, after both the runtime-dependency pins AND the Python floor change are decided — regenerating twice wastes a step and risks lock drift between the two changes. |
| Supported Python range modernized to 3.10–3.13 everywhere it's declared | Active requirement in PROJECT.md; 3.9 reached EOL Oct 2025 | MODERATE | Touches 6 files/locations in lockstep: `pyproject.toml` (`requires-python`, `classifiers`), `tool.black.target-version`, `tool.ruff.target-version`, `tool.mypy.python_version`, `tox.ini` `env_list` (and `[testenv]`/`[testenv:type]` deps), `ci.yml` matrix `python-version` list. Missing any one leaves a stale/inconsistent floor. |
| `@preview` version references stay in sync across all 3 hardcoded locations | `typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ` all hardcode the same 4 package versions (flagged in CONCERNS.md as tech debt) | LOW | Only relevant if the pin fix requires changing any `@preview` package version (not just the `typst` compiler version) to restore compatibility — if so, all 3 locations must be edited together or the translator and the default template will disagree. |

### Differentiators / Durability (Prevents Recurrence — Valuable, Not Blocking)

These don't gate "green CI" but directly address why this rot happened silently for a whole maintenance gap.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Scheduled (`cron`) CI run added to `ci.yml` | Root cause of the multi-month silent breakage: `ci.yml` currently only triggers on `push`/`pull_request`/`workflow_dispatch` (no `schedule:`) — if the repo goes quiet again, nobody notices until the next PR resolves newer transitive versions. A weekly cron run re-resolves dependencies and would surface drift within days, not months. | LOW | Add `schedule: - cron: '0 6 * * 1'` (or similar) to `ci.yml`'s `on:` block. Weigh CI-minutes cost against a private/low-traffic repo — weekly is a reasonable default given `dependabot.yml` already runs pip checks weekly. |
| Version-constraint hygiene: replace bare `>=` with explicit upper bounds on the same 3 critical runtime deps (`sphinx`, `docutils`, `typst`) | This *is* the mechanism that caused the incident — unbounded `>=` let a fresh resolve silently jump two major Sphinx versions and a Typst minor. Upper bounds turn "silent breakage" into "explicit, reviewable dependency PR." | LOW | Already implied by the table-stakes pin item above — call out explicitly as a durability principle (e.g. `sphinx>=5.0,<9.0`, `docutils>=0.18,<0.22`, `typst>=0.14.1,<0.15`) with an inline comment referencing the incident, so a future contributor doesn't "helpfully" loosen it back. |
| Dependabot grouping for the coupled ecosystem (`sphinx` + `docutils` + `typst` + `@preview`-adjacent) | Current `dependabot.yml` opens up to 5 independent pip PRs/week with no grouping — a maintainer could merge a `typst` bump alone and reintroduce `kai` without realizing `docutils` needs to move in lockstep. Grouping forces "these move together or not at all" review. | LOW–MODERATE | Add a `groups:` block under the pip entry (Dependabot v2 config) bundling the coupled packages; keep GitHub Actions updates ungrouped (they're independent). |
| CI status badge in `README.md` | README currently has PyPI, License, "Code style: black", and Documentation badges — **no CI/build-status badge** — so a visitor (or maintainer) can't see build health at a glance; this gap likely contributed to the rot going unnoticed. | TRIVIAL | One-line addition once `ci.yml` is green: `![CI](https://github.com/YuSabo90002/typsphinx/actions/workflows/ci.yml/badge.svg)`. |
| Inline comment/doc note on *why* each pin/upper-bound exists | Prevents a future "just bump it" PR from silently reintroducing the exact same incompatibility class | TRIVIAL | A short comment above the `dependencies` list in `pyproject.toml` (or a CONTRIBUTING note) referencing "pinned after the 2026-07 sphinx-9/typst-0.15 incident" is enough; no new document required. |
| Typst-version × `@preview`-package compatibility check (smoke test) as a distinct, fast CI/tox check | CONCERNS.md already flags this as a testing gap ("Hardcoded Package Version Resilience... Priority: High"); a minimal check (compile a trivial doc with the pinned packages against the pinned typst version) would catch this class of break before it reaches the full test matrix | MODERATE | Optional stretch — genuinely useful but edges toward "new test infrastructure" rather than pure CI repair. Recommend flagging for a near-future milestone rather than committing to it in this cycle; do not let it block "done." |

### Anti-Features (Explicitly Deferred This Cycle)

Directly sourced from PROJECT.md "Out of Scope" — listed here so the roadmap doesn't accidentally reintroduce them as "since we're in here anyway" scope creep.

| Feature | Why It Looks Tempting | Why Deferred This Cycle | Alternative |
|---------|---------------|-----------------|-------------|
| Porting/adapting code and templates to actually *support* Sphinx 9 / Typst 0.15 / newest `@preview` package majors | "Might as well fix it forward instead of pinning backward" | Large surface area (translator, writer, template engine all touch Sphinx/docutils APIs and Typst syntax); turns a bounded CI-repair cycle into an open-ended porting project; PROJECT.md explicitly chooses pin-backward as the lowest-risk path | Pin to the known-good combination now; open a dedicated future milestone to evaluate forward-porting once pinned CI is stable |
| Making `@preview` package versions configurable via `app.add_config_value()` (the CONCERNS.md tech-debt fix) | It's the "proper" fix for the exact tech debt that caused this incident, and you're already touching these 3 files to sync versions | Config-surface design work (naming, defaults, back-compat, docs) is feature work, not CI repair; only justified *if* it turns out to be required to unblock the pin (it likely isn't — hardcoded versions can be edited in place) | Only build this if pinning proves impossible without it; otherwise defer to a follow-up milestone |
| Incremental-build / rebuild-tracking refactor (`get_outdated_docs()` always returns all docs) | Also flagged in CONCERNS.md as tech debt, "High priority" for test coverage | Orthogonal to CI being green — a performance/DX improvement, not a build-breakage fix; refactoring translator/builder state management risks introducing new regressions right when the goal is stability | Track as backlog item for a future performance-focused milestone |
| New translation features / new reST construct support | Natural temptation once touching translator/writer files for version-sync edits | This is a maintenance cycle, not a feature cycle, per PROJECT.md; any new construct support needs its own test coverage and design discussion | Backlog for a future features milestone |
| Broader exception-handling cleanup, translator state-management refactor, nested-image-path rewrite (all flagged in CONCERNS.md) | Visible tech debt sitting right next to the files being touched for pin-sync | None of these block any CI job from going green; touching translator/writer beyond version-string edits multiplies the risk of introducing new test failures mid-repair | Leave for dedicated refactor milestones; this cycle's diff footprint should stay minimal (pins + config + version strings) |

## Feature Dependencies

```
[Diagnose known-good typst + @preview combo]  (INVOLVED, root-cause work)
    └──requires──> [Pin sphinx/docutils/typst in pyproject.toml with upper bounds]
                       └──requires──> [Sync @preview version strings across writer.py /
                                        template_engine.py / base.typ, IF the fix changes
                                        any @preview package version]
                       └──requires──> [Regenerate uv.lock]
                                          └──enables──> [test matrix job green]
                                          └──enables──> [coverage job green]
                                          └──enables──> [docs.yml PDF build green]

[Python floor modernization: pyproject.toml requires-python/classifiers,
 black/ruff/mypy target-version, tox.ini env_list, ci.yml matrix python-version]
    └──should land together with──> [Pin changes above]
                       (both changes should be resolved in ONE uv.lock regeneration,
                        not two, to avoid redundant lock churn)
    └──requires──> [test matrix job green on py3.10-3.13, drop py3.9]

[black/ruff/mypy target-version bump]
    └──must precede──> [black --check . / running black . to reformat 3 files]
                        (reformatting before the target-version bump risks a second,
                         avoidable reformatting pass)

[lint job green] ──independent of──> [test/coverage/docs jobs]
    (black+ruff fixes are self-contained; don't block on the typst pin)

[build job, integration job] ──already green──> [verify no regression only]
    (not on the critical path; just don't let Python-floor or pin changes break them)

[release.yml validate job] ──mirrors──> [ci.yml lint + test + type-check]
    (no independent code change needed; passively fixed once ci.yml is green;
     verify by dry-running its 4 commands, since it can't be triggered without a tag)

[Scheduled CI cron] ──independent, no dependency──> (durability, add anytime)
[Dependabot grouping] ──independent, no dependency──> (durability, add anytime)
[CI badge] ──should follow──> [ci.yml actually green]
    (adding a badge before CI is green is misleading)
```

### Dependency Notes

- **Everything blocking the `test`, `coverage`, and `docs.yml` PDF jobs traces back to one root-cause fix**: finding and pinning a `typst` version (0.14.x line) compatible with the 4 hardcoded `@preview` packages. This is the highest-complexity, highest-priority item — everything else in Table Stakes is either independent (lint, build, integration) or downstream of this fix (matrix/coverage/docs).
- **Pin decisions and Python-floor decisions should be resolved together before the one `uv.lock` regeneration** — doing them in two passes means two lock regenerations and two chances for the lock file to drift from what CI actually exercises.
- **Reformatting (black) should happen after target-version bumps**, not before, since a `target-version` change can itself alter what black considers correctly formatted.
- **Durability items (cron, Dependabot grouping, badge, comment hygiene) have zero dependency on the pin-fix work** — they can be delivered in parallel or even before the pin fix lands, except the badge, which should only be added once green (a red badge is worse than no badge).

## Milestone Definition of Done

### Required To Close This Milestone (Table Stakes)

- [ ] `black --check .` exits 0 on full tree
- [ ] `ruff check .` exits 0 on full tree
- [ ] `mypy typsphinx/` exits 0
- [ ] All 12 `ci.yml` `test` matrix jobs (3 OS × py3.10–3.13) pass
- [ ] `ci.yml` `coverage` job passes
- [ ] `ci.yml` `build` job still passes (no regression)
- [ ] `ci.yml` `integration` job still passes (no regression)
- [ ] `docs.yml` `build-docs` job passes, including the `typstpdf` PDF build step
- [ ] `release.yml validate` job's 4 commands verified clean (dry-run; can't trigger without a tag)
- [ ] `typst`, `sphinx`, `docutils` pinned to a mutually-compatible, upper-bounded set
- [ ] `@preview` package versions consistent across all 3 hardcoded locations
- [ ] `uv.lock` regenerated once, matching final pins + Python range
- [ ] `requires-python`, classifiers, tox env_list, ci.yml matrix, and black/ruff/mypy target-versions all read 3.10–3.13 consistently

### Add If Time Allows (Durability — Strongly Recommended, Not Blocking)

- [ ] Scheduled weekly `cron` trigger added to `ci.yml`
- [ ] Upper-bound version-constraint comments explaining the incident
- [ ] Dependabot grouping for the sphinx/docutils/typst cluster
- [ ] CI status badge added to `README.md` (only after green)

### Explicitly Out of Scope (Do Not Do This Cycle)

- [ ] Sphinx 9 / Typst 0.15 / newest `@preview` forward-porting
- [ ] Configurable `@preview` package versions
- [ ] Incremental-build / rebuild-tracking refactor
- [ ] New translation features or reST constructs
- [ ] Broader exception-handling / translator state-management / image-path refactors

## Feature Prioritization Matrix

| Feature | User Value (maintainer/CI-consumer) | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| typst/sphinx/docutils pin fix | HIGH | HIGH | P1 |
| Python floor modernization | HIGH | MEDIUM | P1 |
| black/ruff pass | HIGH | LOW | P1 |
| uv.lock regeneration | HIGH | LOW | P1 |
| `@preview` version sync | HIGH | LOW | P1 |
| release.yml dry-run verification | MEDIUM | LOW | P1 |
| Scheduled CI cron | HIGH (anti-recurrence) | LOW | P2 |
| Version-constraint hygiene comments | MEDIUM | LOW | P2 |
| Dependabot grouping | MEDIUM | LOW-MEDIUM | P2 |
| CI badge | LOW | TRIVIAL | P2 |
| Typst/`@preview` compatibility smoke check | MEDIUM | MEDIUM | P3 (future milestone) |
| Sphinx 9/Typst 0.15 forward-port | N/A this cycle | HIGH | Explicitly excluded |

**Priority key:**
- P1: Must have to close this milestone
- P2: Should have, adds durability against recurrence, low cost to include now
- P3: Nice to have, defer to a future milestone

## CI Job → Root Cause Mapping

| Workflow / Job | Currently | Root Cause | Fix Depends On |
|------|--------------|--------------|--------------|
| `ci.yml` / `lint` | FAIL | 3 files need `black` reformat | Nothing (independent, do first) |
| `ci.yml` / `type-check` | PASS | — | Must not regress on Python-floor bump |
| `ci.yml` / `test` (12 jobs) | FAIL (matrix-wide) | `typst==0.15.0` resolves; `kai` unknown-variable error from a `@preview` package incompatible with 0.15 | Pin fix + uv.lock regen + tox/ci.yml Python range update |
| `ci.yml` / `coverage` | FAIL | Same as `test` (7 PDF-integration tests fail) | Same as `test` |
| `ci.yml` / `build` | PASS | — | Must not regress on `requires-python`/classifiers change |
| `ci.yml` / `integration` | Likely PASS (uses `-b typst`, not `-b typstpdf`) | N/A — doesn't invoke Typst compiler | Verify assumption; no fix expected |
| `docs.yml` / `build-docs` | FAIL (PDF step) | Same `typst`/`@preview` incompatibility via `sphinx-build -b typstpdf` | Same pin fix |
| `release.yml` / `validate` | Not directly observed (no tag pushed) | Mirrors `ci.yml` lint/test/type-check inline | Passively fixed once `ci.yml` green; verify by dry-run |
| `release.yml` / `build`, `publish-pypi`, `create-release`, `publish-testpypi` | Not directly observed | Depend on `validate` passing first (`needs:`) | No independent code changes expected |

## Sources

- `.planning/PROJECT.md` (failure evidence, Active/Out-of-Scope requirements, Context section) — HIGH confidence, primary source of truth for this milestone's scope
- `.planning/codebase/CONCERNS.md` (tech-debt inventory: hardcoded `@preview` versions, incremental-build gap, dependency-at-risk analysis) — HIGH confidence, direct codebase inspection
- `.planning/codebase/STACK.md`, `.planning/codebase/TESTING.md`, `.planning/codebase/CONVENTIONS.md` — HIGH confidence, direct codebase inspection
- `.github/workflows/ci.yml`, `.github/workflows/docs.yml`, `.github/workflows/release.yml` — HIGH confidence, direct inspection of the actual CI configuration this milestone must repair
- `.github/dependabot.yml`, `README.md` badges — HIGH confidence, direct inspection
- `pyproject.toml`, `tox.ini` — HIGH confidence, direct inspection of current tool configs (black/ruff/mypy target versions, pytest markers, tox env_list)
- Web search: "typst 0.15 unknown variable kai error preview package" — LOW confidence, no direct public documentation found describing this specific incompatibility; treat the exact known-good `typst`/`@preview` combination as **unverified, requiring empirical local testing**, not a settled research fact
- Web search: "black target-version py313 support changelog" — MEDIUM confidence; confirms Black added `py313` as a valid `--target-version` value in a version after 24.8.0 (Oct 2024) — the currently pinned `black>=23.0` floor will resolve a version that supports `py313`, but the exact minimum version needed should be verified when bumping `target-version = [..., "py313"]`

---
*Feature research for: CI/CD maintenance & dependency-pin repair (typsphinx)*
*Researched: 2026-07-04*
