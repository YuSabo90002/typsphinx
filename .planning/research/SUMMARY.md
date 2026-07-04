# Project Research Summary

**Project:** typsphinx — CI-repair / maintenance milestone
**Domain:** Python package (Sphinx extension) CI dependency-drift repair
**Researched:** 2026-07-04
**Confidence:** MEDIUM-HIGH (root cause is HIGH confidence; the exact typst patch pin and whether the sphinx/docutils ceilings are load-bearing require empirical CI confirmation during execution — not assumed)

## Executive Summary

typsphinx's CI went red because loose, unbounded `>=` dependency constraints let a fresh dependency resolution silently jump to `typst==0.15.0`, `sphinx==9.0.4`, and `docutils==0.22.4`. The confirmed root cause is narrow and well-understood: the hardcoded `@preview/mitex:0.2.4` package uses a `kai` symbol that Typst's own deprecation policy turned from a warning (under compiler 0.14.x) into a hard error (under compiler 0.15.0) — fixed upstream in mitex 0.2.6, but this project deliberately pins backward rather than porting forward. The fix is to reintroduce explicit upper bounds — `typst>=0.14.1,<0.15` (target `0.14.9`), `sphinx>=5.0,<9`, `docutils>=0.18,<0.22` — across every place these constraints are declared, not just `pyproject.toml`.

The recommended approach is a strictly phased rollout that isolates the bug fix from opportunistic modernization: (1) pin runtime dependencies and regenerate the lockfile, verified empirically against the actual PDF-compile path rather than guessed from pattern-matching; (2) verify (not edit) that the three hardcoded `@preview` version-string locations remain in sync; (3) bump the Python floor to 3.10–3.13 and every tool/CI config that encodes that floor, as one atomic batch; (4) add durability guardrails (lockfile enforcement, scheduled drift detection, Dependabot grouping, CI badge) that explicitly stop short of touching the deferred sphinx-9/typst-0.15 port. Do not fold Python-floor changes into the same commits as the pin fix — a red run must be unambiguously attributable to one or the other.

The key risks are: (a) guessing the typst patch version instead of empirically confirming it compiles cleanly against all four pinned `@preview` packages across all 3 OS runners; (b) fixing only `typst` and leaving `sphinx`/`docutils` open-ended, which reproduces the exact rot this milestone exists to close; (c) editing the `@preview` version strings in only 1-2 of their 3 hardcoded locations (`writer.py`, `template_engine.py`, `templates/base.typ`), causing silent master/included-document rendering divergence; and (d) declaring victory on a green CI without closing the `uv sync` (no `--locked`) drift hole that caused the silent breakage in the first place. None of these are hypothetical — they are the specific mechanisms PITFALLS.md traces back to this incident.

## Key Findings

### Recommended Stack

Pin, don't port. `typst` (typst-py) tracks the Rust Typst compiler 1:1 by version number; `typst>=0.14.1,<0.15` targeting `0.14.9` restores the deprecation-warning (not error) behavior for `kai` without touching any of the four hardcoded `@preview` packages. `sphinx>=5.0,<9` and `docutils>=0.18,<0.22` are defensive ceilings matching the project's "pin known-good" decision — HIGH confidence that these ceilings are safe and currently installable, but only MEDIUM confidence that sphinx 9 itself would have broken anything beyond the typst/`kai` cascade (no sphinx-9-specific failure was independently observed — this should be empirically isolated during execution, e.g. by testing whether `typst<0.15` alone is sufficient before deciding the sphinx ceiling is load-bearing or precautionary).

**Core technologies / pins:**
- `typst>=0.14.1,<0.15` (target `0.14.9`) — fixes the `kai` hard-error; HIGH confidence on root cause, MEDIUM on the exact patch (0.14.2–0.14.9 not individually regression-tested against the pinned `@preview` combo — empirically confirm in CI).
- `sphinx>=5.0,<9` — excludes the sphinx-9 line that resolved during the failing CI run; HIGH confidence as a safe ceiling, MEDIUM confidence it's strictly necessary vs. precautionary.
- `docutils>=0.18,<0.22` — redundant-but-explicit; Sphinx 8.x already transitively constrains `docutils<0.22,>=0.20`, so this makes intent visible in typsphinx's own `pyproject.toml`.
- Python floor `requires-python>=3.10` (drop 3.9, no `<3.14` ceiling needed) — no blockers found in the core runtime path; `sphinx-testing` is the one dev dependency worth scrutinizing for both relevance and 3.13 support.
- Dev tooling: stay conservative this cycle — `mypy>=1.13,<2.0`, `pytest>=7.0,<9` (target ~8.4.x), `ruff>=0.8`, `tox>=4.6` — avoid jumping to the very latest majors (mypy 2.0, pytest 9.0) since both flip default behaviors that can surface new failures unrelated to the CI-repair goal.
- **Dead dependency to remove:** `sphinx-testing>=1.0` — zero usages in the test suite (verified by repo-wide grep), last released 2019, no `requires_python` metadata at all. Remove rather than "modernize."

### Expected Features (Milestone Acceptance Items)

This is a maintenance milestone — "features" means CI/release acceptance criteria mapped 1:1 to jobs in `.github/workflows/{ci,docs,release}.yml`.

**Must have (table stakes / Definition of Done):**
- `black --check .`, `ruff check .`, `mypy typsphinx/` all exit 0 (3 files currently need reformatting — do this *after* the target-version bump, not before, to avoid a second reformat pass).
- All 12 `ci.yml` test-matrix jobs (3 OS × py3.10–3.13) green, plus `coverage` and `docs.yml` PDF build — all currently blocked on the single typst/`@preview` root-cause fix.
- `build` and `integration` jobs stay green (no regression) — `integration` uses `-b typst` not `-b typstpdf`, so it likely doesn't invoke the Typst compiler at all; verify this assumption rather than assume it.
- `release.yml validate` job's four commands (pytest, black --check, ruff check, mypy) dry-run clean — can't be exercised live without a tag push.
- Runtime deps (typst/sphinx/docutils) pinned with upper bounds; `uv.lock` regenerated **once**, after both the pin decision and Python-floor decision are settled (not twice).
- `@preview` version strings stay identical across all 3 hardcoded locations.
- Python range consistent across 6+ files/locations (see Architecture below).

**Should have (durability, low cost, strongly recommended):**
- Enforce lockfile currency in CI (`uv sync --locked` or `uv lock --check`) — closes the exact silent-drift mechanism that caused this incident.
- Scheduled weekly `cron` job on `ci.yml` for early drift detection (non-blocking, detection-only).
- Dependabot grouping for the coupled `sphinx`/`docutils`/`typst` cluster so a future PR can't bump one without the others.
- CI status badge on README (only after CI is actually green).
- Inline comments on each pin explaining the incident, so a future "helpful" loosening doesn't reintroduce it.

**Defer (explicitly out of scope this cycle):**
- Porting to sphinx 9 / typst 0.15 / newest `@preview` majors.
- Configurable `@preview` package versions (the "proper" CONCERNS.md fix) — only build if pinning proves impossible without it.
- Incremental-build/rebuild-tracking refactor, broader exception-handling/translator refactors, new translation features — all orthogonal to green CI and out of scope per PROJECT.md.
- A typst-compiler×`@preview`-compatibility smoke-test check is a good idea but edges into new test infrastructure — flag for a future milestone, don't let it block this one.

### Architecture Approach: Edit Surface & Sequencing

Four independent edit *concerns* were identified, each with a different blast radius — they must be phased separately, not landed as one diff, so a red run is always attributable to a single cause:

1. **Concern A — Runtime dependency pins** (the actual bug fix): `pyproject.toml` `[project].dependencies`, `uv.lock` (regenerate after), and — critically — `tox.ini`'s `[testenv]`/`[testenv:type]` `deps=` lists, which are **hand-maintained duplicate constraints, not derived from `pyproject.toml`**, and will silently reintroduce the same break in the `type` env if not mirrored explicitly.
2. **Concern B — The 3-way `@preview` sync hazard**: `typsphinx/writer.py` (lines 94-97), `typsphinx/template_engine.py` (lines 313-316), and `typsphinx/templates/base.typ` (lines 8,9,14,19) all independently hardcode the same four package versions with no shared source of truth. All three currently agree. For this milestone, since the fix pins the *compiler* not the packages, these sites need **verification, not edits** — but any future package-version bump must touch all three in the same commit, or a compiled document can pull two different versions of the same Typst package into one compilation graph (structurally the same failure class as `kai`).
3. **Concern C — CI/workflow matrix and action versions**: `ci.yml`'s `matrix.python-version` (drop 3.9, add 3.13); the per-job hardcoded `uv python install 3.11` lines across `ci.yml`/`docs.yml`/`release.yml` need no change (3.11 is inside the new floor/ceiling) unless standardizing on a different version. `flake.nix` uses an unpinned rolling `pkgs.python3` — not an edit site, but a flagged gap (local Nix dev isn't protected by the same floor/ceiling as CI).
4. **Concern D — Tool target-version alignment**: `requires-python`, `classifiers`, `[tool.black].target-version`, `[tool.ruff].target-version`, `[tool.mypy].python_version` in `pyproject.toml`, plus `tox.ini`'s `env_list` — six-plus locations that must move in lockstep or CI requests a tox env that doesn't exist (loud failure) or tox supports a version CI never exercises (silent gap).

**Suggested safe build order (from ARCHITECTURE.md), matching the roadmap phase suggestions below:**
Phase 1 (pin fix, alone) → Phase 2 (verify @preview sync, no edit expected) → Phase 3 (Python floor + CI matrix + tool targets, one atomic batch) → Phase 4 (optional low-risk action-version refresh, fully decoupled, can run anytime/in parallel).

### Critical Pitfalls

1. **Under-pinning** — fixing only `typst` and leaving `sphinx`/`docutils` unbounded reproduces the exact rot. Avoid by giving every runtime dependency an explicit upper bound in the same commit, and always regenerating + committing `uv.lock` alongside any `pyproject.toml` dependency edit — never one without the other.
2. **The 3-way `@preview` desync** — bumping a version string in 1-2 of the 3 hardcoded locations produces silent, hard-to-detect rendering inconsistency between master and included documents. Avoid by grepping all `@preview/` occurrences before any edit and adding a cross-file consistency test that asserts all three agree.
3. **Guessing the typst pin instead of empirically confirming it** — typst-py version numbers track the compiler 1:1, but each of the four `@preview` packages declares its own independent compiler-compatibility floor; there is no guarantee any single 0.14.x version satisfies all four simultaneously. The correct method: enumerate 0.14.x candidates, actually compile the `docs-pdf` target (which exercises the real `codly`+`codly-languages`+`mitex`+`gentle-clues` import block) against each candidate in isolation, and record which passed/failed — this is the milestone's core empirical deliverable, not a research-time conclusion.
4. **Cross-platform pins that pass on ubuntu but fail on windows/macos** — typst-py ships per-platform binary wheels; a version with a good manylinux wheel may lack matching Windows/macOS wheels at the same release. Don't declare the milestone done from an ubuntu-only view — watch the full 12-job matrix (3 OS × 4 Python) to green completion at least once after the pin lands.
5. **Green-but-frozen (silent re-rot)** — a milestone that goes green without lockfile enforcement (`uv sync --locked` or `uv lock --check`) and without a scheduled drift-detection job reproduces the exact silent-resolution mechanism that caused this incident in the first place. Durability guardrails must be scoped tightly to detection/enforcement — explicitly NOT triggering any sphinx-9/typst-0.15 remediation work.

## Implications for Roadmap

Based on combined research, the following phase structure is suggested. This maps directly onto the "safe build order" in ARCHITECTURE.md, cross-checked against PITFALLS.md's "phase to address" tags and FEATURES.md's dependency graph — all three research files converge on the same sequencing independently, which is a strong signal this order is correct.

### Phase 1: Pin Runtime Dependencies to Known-Good (the actual bug fix)
**Rationale:** Everything blocking `test`, `coverage`, and `docs.yml`'s PDF job traces back to this single root cause. It must land alone, first, so a red or green result is unambiguous and not entangled with the unrelated Python-floor work.
**Delivers:** Explicit upper bounds in `pyproject.toml` (`typst>=0.14.1,<0.15`, `sphinx>=5.0,<9`, `docutils>=0.18,<0.22`), mirrored exactly in `tox.ini`'s `[testenv]`/`[testenv:type]` deps, plus a regenerated + committed `uv.lock`. Includes empirical verification (compile the actual `docs-pdf` target against each 0.14.x candidate) rather than a guessed pin, and removal of the dead `sphinx-testing` dependency.
**Addresses:** FEATURES.md's highest-priority table-stakes item ("Runtime dependencies pinned to a reproducible known-good set").
**Avoids:** Pitfall 1 (under-pinning), Pitfall 3 (guessing the pin), Pitfall 4 (cross-platform pin failure — gate this phase on the full 12-job matrix going green, not just ubuntu jobs).

### Phase 2: Verify `@preview` Sync (verification, not edit)
**Rationale:** Costs almost nothing but must happen before anyone assumes the three hardcoded `@preview` sites are "handled" — the cheapest place to catch a surprise incompatibility before it ships.
**Delivers:** Confirmation (via grep + diff) that `writer.py`, `template_engine.py`, and `templates/base.typ` still declare identical `codly`/`codly-languages`/`mitex`/`gentle-clues` versions after Phase 1's typst pin lands. Recommended: add a lightweight cross-file consistency test so this becomes an enforced invariant, not a manual check.
**Addresses:** FEATURES.md's "@preview version references stay in sync" acceptance item.
**Avoids:** Pitfall 2 (the 3-way desync).

### Phase 3: Modernize Python Floor to 3.10–3.13 (one atomic batch)
**Rationale:** Six-plus files/settings encode the Python floor; a partial bump is the default failure mode unless done as one explicit, checklisted change. Must land after Phase 1 is confirmed green, so any new failure here is known to be about the Python bump, not the dependency pins.
**Delivers:** `requires-python`, `classifiers`, `[tool.black]/[tool.ruff]/[tool.mypy]` target-versions in `pyproject.toml`; `tox.ini`'s `env_list`; `ci.yml`'s matrix `python-version` list — all updated together in a single commit/PR. Includes reformatting the 3 currently-black-noncompliant files (after, not before, the target-version bump).
**Uses:** STACK.md's dev-tooling floor recommendations (stay on mypy 1.x, pytest 8.x this cycle).
**Implements:** ARCHITECTURE.md's Concern C + D as one bundled change (they're two expressions of the same fact and must move together).

### Phase 4: Durability Guardrails (scoped tightly — no scope creep)
**Rationale:** A green CI today proves nothing about next month unless lockfile currency is enforced and drift is detected proactively. This phase is fully decoupled from Phases 1-3 and can run anytime, even in parallel, but should close the milestone since the CI badge depends on green status.
**Delivers:** Switch `uv sync` → `uv sync --locked` (or add `uv lock --check`) in `ci.yml`/`docs.yml`/`release.yml`; add a non-blocking scheduled (`cron`) drift-detection workflow that tests unpinned/latest versions and reports without failing the main pipeline; Dependabot grouping for the sphinx/docutils/typst/`@preview`-adjacent cluster; CI badge in README (only after green); inline pin-rationale comments referencing this incident; a release-workflow parity check (dry-run `release.yml`'s `validate` job commands locally against the new pins, since `release.yml` duplicates `tox.ini`'s checks independently and only triggers on tag push).
**Addresses:** FEATURES.md's Differentiators/Durability table.
**Avoids:** Pitfall 6 (green-but-frozen) and Pitfall 7 (release workflow drift) — explicitly does NOT touch sphinx-9/typst-0.15 port work.

### Phase Ordering Rationale

- Phase 1 must be isolated and first because it's the actual fix for the CI-red state; landing Python 3.13 support on top of a still-broken typst pin would make it impossible to bisect which change fixed what.
- Phase 2 is nearly free (verification only) but is sequenced right after Phase 1 because that's the first point at which the `@preview` sites could theoretically need to change.
- Phase 3 bundles three files that must move in lockstep (`pyproject.toml`, `tox.ini`, `ci.yml`) — splitting it risks a state where a tox env exists that CI never calls, or vice versa.
- Phase 4 is genuinely independent of the typst/Python work and carries zero risk of interacting with either — sequencing it last just keeps the higher-stakes phases' diffs minimal and easy to bisect; it could equally run in parallel with Phase 3.
- All 3 research dimensions (ARCHITECTURE's "safe build order," PITFALLS's "phase to address" tags, FEATURES' dependency graph) independently converge on this exact sequencing, which raises confidence in this specific ordering to HIGH even though several underlying facts (the exact typst patch, sphinx/docutils ceiling necessity) remain MEDIUM.

### Research Flags

Phases likely needing deeper research/verification during planning or execution (empirical, not desk research):
- **Phase 1:** Needs an empirical CI/local verification pass to confirm the exact typst 0.14.x patch (candidates 0.14.1–0.14.9) that compiles cleanly against all four pinned `@preview` packages across all 3 OS runners — this was NOT resolved by desk research and is explicitly the milestone's core deliverable. Also needs confirmation of whether the sphinx `<9` and docutils `<0.22` ceilings are load-bearing (caused real failures) or purely precautionary.
- **Phase 3:** Needs a quick wheel-availability check (`pip install --python 3.13 <pkg>`) for dev/docs optional dependencies, especially `sphinx-testing` (recommend removal instead) and any other long-dormant dev dependency, before committing to 3.13 in the CI matrix.

Phases with standard, well-documented patterns (research-phase can likely be skipped):
- **Phase 2:** Pure grep-and-diff verification against already-documented file/line locations (ARCHITECTURE.md pinpoints exact line numbers for all 3 `@preview` sites).
- **Phase 4:** Standard, well-known CI durability patterns (`--locked`, scheduled cron, Dependabot `groups:`, README badge) — no domain-specific research needed, just mechanical application.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM-HIGH | Root cause (mitex/kai/typst-0.15) is HIGH confidence, cross-checked via mitex's own changelog and the observed CI symptom. Exact patch pin (0.14.9 vs. any other 0.14.x) and whether sphinx/docutils ceilings are strictly necessary (vs. precautionary) are MEDIUM — explicitly flagged for empirical CI confirmation, not settled by desk research. |
| Features | HIGH (job/workflow mapping) / MEDIUM (exact known-good version combo) | Every acceptance item was mapped 1:1 against actual jobs read directly from `.github/workflows/*.yml`. The one MEDIUM item is identical to Stack's gap: the exact good `typst`+`@preview` combination requires empirical testing this research pass could not perform. |
| Architecture | HIGH | Every file/line-number claim was read directly from the repo at HEAD; this dimension is a codebase-topology question, not an ecosystem question, so no external uncertainty applies. |
| Pitfalls | HIGH (repo-specific findings) / MEDIUM (typst-py↔compiler version-correspondence claim) | Repo-specific pitfalls (lockfile drift, `@preview` desync, release.yml parity) are HIGH confidence, read directly from configs. The claim that typst-py version numbers track the compiler 1:1 is the consistent observed pattern but not stated in a single authoritative doc — hence the insistence on empirical verification as the core Phase 1 deliverable rather than trusting this inference. |

**Overall confidence:** MEDIUM-HIGH — the root cause, the fix mechanism, and the edit surface are all solidly established; the one genuine open question (exact typst patch + whether sphinx/docutils ceilings are load-bearing) is explicitly gated behind empirical CI verification in Phase 1, not assumed.

### Gaps to Address

- **Exact typst patch pin (0.14.1 vs. 0.14.9 vs. something in between):** No patch-by-patch regression testing exists against this project's exact `@preview` combo. Resolve during Phase 1 by compiling the `docs-pdf` target against each 0.14.x candidate and recording pass/fail — do not lock this pin without that empirical step.
- **Whether sphinx `<9` / docutils `<0.22` ceilings are load-bearing:** All observed CI failures trace to the `kai`/typst cascade, not a confirmed sphinx-9-specific break. Resolve by testing whether `typst<0.15` alone is sufficient before treating the sphinx/docutils ceilings as anything beyond precautionary/defensive (still recommended regardless, per the project's own "pin known-good" decision, but the distinction matters for how tightly future Dependabot/drift-job bounds should be set).
- **Whether all four `@preview` packages truly share a compatible compiler range within 0.14.x:** Each package's own `typst.toml` declares an independent compiler floor; it's possible no single typst-py version satisfies all four. If Phase 1's empirical check finds this, the documented fallback is to pin one `@preview` package to an older published version rather than move the typst pin — surface this as a real risk during planning, not a footnote.
- **CI runner Node version for `codecov/codecov-action@v6`:** Not directly confirmed; stay on v5.5.x unless the runner's Node 24 support is verified during Phase 4.
- **GitHub Action version pins (`actions/checkout`, `actions/setup-python`) recommended versions:** LOW-MEDIUM confidence, sourced from web search convergence rather than direct API read — verify current pins and changelogs against the actual `.github/workflows/*.yml` files during Phase 4 execution.

## Sources

### Primary (HIGH confidence)
- Direct repository reads at HEAD (2026-07-04): `pyproject.toml`, `tox.ini`, `flake.nix`, `uv.lock`, `.github/workflows/{ci,docs,release}.yml`, `.github/dependabot.yml`, `README.md`, `typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ`, `typsphinx/pdf.py`
- `.planning/PROJECT.md`, `.planning/codebase/{ARCHITECTURE,STRUCTURE,INTEGRATIONS,CONCERNS,STACK,TESTING,CONVENTIONS}.md` — existing codebase map and milestone scope of record
- PyPI JSON API — direct queries for `typst`, `sphinx`, `docutils`, `black`, `ruff`, `mypy`, `pytest`, `tox`, `sphinx-testing` release metadata and `requires_python`/`requires_dist`
- Repo-local grep verification: `grep -rn "sphinx_testing" tests/` (zero matches, confirms dead dependency)
- uv docs — Locking and syncing (https://docs.astral.sh/uv/concepts/projects/sync/) — confirms `uv sync` silently re-resolves a stale lock while `--locked` errors
- typst 0.15.0 changelog (https://typst.app/docs/changelog/0.15.0/) and Typst 0.15 blog post (https://typst.app/blog/2026/typst-0.15/)

### Secondary (MEDIUM confidence)
- `mitex-rs/mitex` CHANGELOG.md (GitHub) — the "fix 'kai is deprecated' warning for Typst v0.14.0" entry landed in mitex 0.2.6; single primary source, strongly corroborated by the observed CI symptom but the 0.14→0.15 warn-to-error transition itself is inferred from Typst's general deprecation policy, not an explicit joint mitex/typst statement
- typst/typst issue #4379 (https://github.com/typst/typst/issues/4379) — confirms each Typst Universe package declares its own compiler-compatibility floor
- messense/typst-py (https://github.com/messense/typst-py) — basis for the (unconfirmed-but-consistent) typst-py-version-tracks-compiler-version pattern
- astral-sh/uv issue #12372 (https://github.com/astral-sh/uv/issues/12372) — community discussion on `uv sync` default-to-`--locked` drift risk
- Web search on black/pytest/mypy changelog behavior-flip risks in newer majors

### Tertiary (LOW confidence)
- Typst Universe package pages (gentle-clues, codly, codly-languages, mitex) via WebSearch/WebFetch — single-source, not cross-verified, used only for declared minimum-compiler versions
- GitHub Actions marketplace info for actions/checkout, actions/setup-python, codecov/codecov-action — verify current pins/changelogs directly in .github/workflows/*.yml during execution

---
*Research completed: 2026-07-04*
*Ready for roadmap: yes*
