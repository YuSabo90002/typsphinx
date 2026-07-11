# Pitfalls Research

**Domain:** Forward-porting a Sphinx builder/writer extension (typsphinx) to Sphinx 9 + typst 0.15+, with bundled Typst Universe `@preview` packages
**Researched:** 2026-07-09
**Confidence:** MEDIUM (mix of HIGH-confidence primary-source facts — PyPI package metadata — and MEDIUM/LOW-confidence web-search findings on `@preview` package changelogs that should be re-verified at execution time)

## Critical Pitfalls

### Pitfall 1: The `@preview` package trap — bumping one package silently breaks under the same compiler

**What goes wrong:**
Typst Universe packages declare only a *minimum* compiler version in their manifest (`compiler = "0.12.0"` etc.) — never a maximum or a "last tested against" version. A package can therefore claim to be installable under typst 0.15 while still calling a stdlib symbol, function, or CSL style name that typst 0.15 removed or renamed as part of its normal deprecation-cycle cleanup. That is exactly what happened in the v0.4.4 break: `typst.TypstError: unknown variable: kai` was not a typsphinx bug — it came from inside a bundled package's own Typst source. Bumping only the one package everyone assumes is the culprit (the CONTEXT note in PROJECT.md guessed "likely `gentle-clues:1.2.0` or `codly`") without confirming the real source risks bumping the wrong package, leaving the real one still broken, or worse, bumping a package to a version that introduces *its own* new incompatibility (e.g. codly 1.2.0 changed line-reference numbering from zero- to one-indexed and reworked its ref system — a breaking change unrelated to typst-version compatibility).

**Why it happens:**
The four packages (`codly`, `codly-languages`, `mitex`, `gentle-clues`) are developed independently by different maintainers on different release cadences. typsphinx pins exact versions in three source locations and treats "the bundle" as one unit, but each package's typst-0.15 readiness is only knowable by actually compiling with it — static version numbers tell you nothing about runtime compatibility.

**How to avoid:**
1. **Identify the actual origin before bumping anything.** Research for this milestone traced the `kai` deprecation specifically to **mitex** — its own changelog for v0.2.6 reads *"Fix: fix 'kai is deprecated' warning for Typst v0.14.0"* (mitex bundled today is 0.2.4, which predates that fix). This is a MEDIUM-confidence finding (single changelog source, not independently reproduced by compiling) and must be confirmed by actually compiling a `kai`-triggering document with `mitex>=0.2.6` under typst 0.15 before trusting it — but it means the fix is very likely "bump mitex," not "bump gentle-clues," contradicting the milestone's prior guess.
2. **Bump one package at a time and compile after each bump**, not all four simultaneously — if you bump all four together and it works, you don't know which one mattered (and if it fails, you don't know which one broke it).
3. Add a CI/dev step that actually invokes `typst compile` against a `.typ` fixture exercising every bundled package's key entry points (codly code block, codly-languages icon lookup, mitex inline+block math, gentle-clues admonition) — not just a static string-match test. `tests/test_preview_version_sync.py` only asserts the three declaration sites *agree with each other*; it cannot catch a case where all three agree on a version that is itself broken under the target compiler.
4. Pin exact tested versions (not floors) for all four packages once verified — this is a "known-good bundle," same philosophy as the runtime-pin decision already made for `typst`/`sphinx`/`docutils` in this project.

**Warning signs:**
- `typst.TypstError: unknown variable: <name>` or `unknown variable: <name> is deprecated` in PDF-integration tests or `docs-pdf` build, where `<name>` does not appear anywhere in typsphinx source (`grep -rn "<name>" typsphinx/` returns nothing) — this is the signature of a package-internal deprecated-symbol removal, not a typsphinx bug.
- A package version bump "fixes" the reported symptom locally but a *different* PDF-integration test starts failing — sign that the bump introduced its own breaking change (e.g. codly's ref/line-numbering rework).

**Phase to address:**
The FWD-02 (typst 0.15+) phase — specifically as its own verification step, sequenced *after* the typst compiler ceiling is raised and *before* the `@preview` version-sync files are edited, so the phase can prove causally which package(s) actually needed bumping.

---

### Pitfall 2: The Python-floor trap — Sphinx 9 requires Python ≥3.11, but typsphinx's floor is still 3.10

**What goes wrong:**
PyPI package metadata (authoritative, checked directly against the registry — HIGH confidence) shows Sphinx 9.0.4 declares `requires_python = ">=3.11"`. typsphinx currently declares `requires-python = ">=3.10"` in `pyproject.toml`, and CI's matrix (`ci.yml`), `tox.ini` `env_list`, and the classifiers list all still include a `py310` lane. If the sphinx pin is raised to `sphinx>=9` (or `sphinx>=9,<10`) without also raising `requires-python` to `>=3.11` and dropping the 3.10 lane everywhere, dependency resolution on the 3.10 CI job will have no valid solution — `uv sync --locked` (or plain `pip install`) will hard-fail on that lane with a resolution error, not silently downgrade to an older Sphinx. This is a total lane failure, not a subtle behavioral bug, so it will be loud — but if discovered late (e.g. mid-PR after the lockfile is already regenerated against 3.11+ only) it forces an awkward re-triage of "is this a real regression or just the known floor mismatch."

**Why it happens:**
Sphinx's own minimum-Python bar has been rising release-over-release (Sphinx 9.1 reportedly drops 3.11 support entirely per community reporting — track this if the milestone slips past a Sphinx 9.1 release). typsphinx's Python floor was deliberately modernized to 3.10 in the *previous* milestone (dropping EOL 3.9), which was correct at the time but is now stale relative to Sphinx 9's own requirement. The two floors (typsphinx's Python floor, Sphinx's Python floor) are declared independently and nothing currently checks that typsphinx's floor is `>=` whatever the pinned Sphinx major actually requires.

**How to avoid:**
1. Before raising the sphinx pin, run `curl -s https://pypi.org/pypi/Sphinx/<planned-version>/json | python3 -c "import json,sys;print(json.load(sys.stdin)['info']['requires_python'])"` and treat that as the new floor — don't assume 3.10 still works.
2. Raise `requires-python` in `pyproject.toml`, drop the `py310` env from `tox.ini` `env_list`, drop `'3.10'` from the CI matrix `python-version` list in `ci.yml`, drop the `Programming Language :: Python :: 3.10` classifier, and re-check `black`/`ruff` `target-version`/mypy `python_version` for the new floor — all in the same commit as the sphinx-pin bump, not as a follow-up.
3. Also check `docutils`'s own constraint on Sphinx: Sphinx 9.0.4 pins `docutils<0.23,>=0.20`, which is *tighter* than typsphinx's current `docutils>=0.18,<0.22` ceiling — these two ranges have an empty intersection above 0.22, meaning typsphinx's docutils ceiling must also move (to something like `>=0.20,<0.23`) or `uv sync` will report an unsatisfiable dependency conflict between typsphinx's own constraint and Sphinx 9's.
4. Re-run `drift.yml`'s `uv python install 3.10` line update in lockstep — the weekly drift job pins Python 3.10 explicitly; if the floor moves to 3.11 and this line isn't updated, the *drift detector itself* stops reflecting the supported floor.

**Warning signs:**
- `uv sync` / `pip install` reporting "No solution found when resolving dependencies" or "Because typsphinx depends on sphinx>=9 and sphinx>=9 depends on Python>=3.11, typsphinx requires Python>=3.11" on the 3.10 CI lane specifically (other lanes green).
- A "successful" resolution that quietly picks an *older* sphinx (e.g. 8.x) on the 3.10 lane while 3.11+ lanes get 9.x — this can happen if the sphinx constraint is left as a loose `>=5.0` rather than the intended `>=9`, defeating the entire purpose of the milestone on that one lane without erroring at all. Check the resolved `sphinx` version per-lane in CI logs, not just "job passed."

**Phase to address:**
The FWD-01 (Sphinx 9) phase, as the very first sub-step — establish the correct Python floor from Sphinx 9's own PyPI metadata before touching any other pin, since it gates which CI lanes are even valid for the rest of the milestone.

---

### Pitfall 3: Sphinx 9 / docutils 0.22 removed (not just deprecated) APIs still in use

**What goes wrong:**
`typsphinx/template_engine.py:239` calls `doctree.traverse(addnodes.toctree)`. `Node.traverse()` has been soft-deprecated since docutils 0.18 (with `nodes.Node.findall()` as the recommended iterator replacement) and docutils' release history shows a pattern of aggressively removing previously-deprecated methods each release (0.21 removed `nodes.reprunicode`, `Element.set_class()`, and several others; 0.22 removed `Publisher.setup_option_parser()`, `OptionParser.set_defaults_from_dict()`, and other transform/utility functions; 0.23 removed more). `traverse()` has not been removed as of the docutils versions checked in this research, but it is exactly the kind of long-deprecated call docutils has been removing on a rolling basis — every release is a candidate for it finally going away, and it is inconsistent with the rest of the codebase, which already uses `findall()` correctly in `builder.py:151` (`doctree.findall(image)`). Sphinx 9 itself also changed `SphinxComponentRegistry.create_source_parser` to drop its `app` parameter (now takes `config` and `env` instead) — not directly used in this codebase today, but a signal that Sphinx 9's internal registry/component APIs shifted shape, and any code reaching into Sphinx internals beyond the stable `SphinxTranslator`/`Builder`/`Writer` base classes is at risk.

**Why it happens:**
`TypstTranslator` subclasses `sphinx.util.docutils.SphinxTranslator` (a stable, documented extension point), which insulates most of the translator from churn — but `template_engine.py` reaches directly into `doctree.traverse()`, a raw docutils `Node` method, not a Sphinx-stabilized API. Code paths that go around the documented extension surface are the ones that break silently when the underlying library evolves.

**How to avoid:**
1. Replace `doctree.traverse(addnodes.toctree)` with `list(doctree.findall(addnodes.toctree))` before touching the Sphinx/docutils pins — this is a zero-risk, backward-compatible change (`findall()` has existed since 0.18.1) that removes one known deprecated call regardless of what docutils 0.22 turns out to actually break.
2. Grep the full translator/builder/writer/template_engine surface for other raw docutils/Sphinx internals reached outside the `SphinxTranslator`/`Builder`/`Writer` contract: `grep -rn "\.traverse(\|Publisher\|OptionParser\|set_defaults_from_dict\|setup_option_parser\|reprunicode\|ensure_str\|set_class(" typsphinx/` — none of these hit today except `traverse()`, but re-run this check after every dependency bump in this milestone, since new code written during the port could reintroduce a raw-internals call.
3. Treat `mypy typsphinx/` and the full pytest suite run against the *actual* resolved Sphinx 9 / docutils 0.22 (not the pinned known-good set) as the real signal — deprecated-API removals surface as `AttributeError`/`TypeError` at runtime, not at type-check time, since these are dynamically-typed docutils APIs; don't rely on mypy alone to catch this class of break.
4. Because Sphinx 9's changelog documents the autodoc subsystem as "substantially rewritten" with an `autodoc_use_legacy_class_based` escape hatch, if `sphinx.ext.autodoc` is exercised anywhere in the extension's own docs build (it likely isn't — typsphinx doesn't autodoc Python code, it *is* a builder extension) confirm that assumption explicitly rather than skipping this check.

**Warning signs:**
- `AttributeError: 'document' object has no attribute 'traverse'` (or a `DeprecationWarning`/`FutureWarning` promoted to an error under `pytest -W error`) is the direct signature of this pitfall.
- Test failures concentrated in `test_config_toctree_defaults.py`-style tests (toctree option extraction) rather than spread across the whole suite — `extract_toctree_options()` is the one call site that uses `traverse()`.

**Phase to address:**
The FWD-01 (Sphinx 9) phase — fix `traverse()` → `findall()` as a preparatory, low-risk commit before raising any pins, then re-scan for other raw-internals calls as part of the same phase's verification.

---

### Pitfall 4: The three-way `@preview` version-sync desync trap, now made worse by a new *fourth* class of drift

**What goes wrong:**
`writer.py`, `template_engine.py`, and `templates/base.typ` each independently hardcode the same four `#import "@preview/<pkg>:<version>"` lines, guarded today by `tests/test_preview_version_sync.py`. That test is solid for its narrow job (catching a human editing one of the three files and forgetting the other two) — but this milestone adds a related, *not yet guarded* failure mode: editing all three files consistently to the *wrong* version (a version that doesn't actually compile under typst 0.15). The existing test only proves internal agreement, not external correctness; it will pass cleanly on a synchronized-but-broken bump.

**Why it happens:**
The version-sync test was written to catch the *previous* incident's failure mode (single-file edits going out of sync) — a reasonable scope at the time. This milestone's failure mode is different: someone deliberately edits all three sites in lockstep (correctly, per the test) to a set of versions that hasn't actually been proven to mutually compile under the new typst compiler ceiling.

**How to avoid:**
1. Keep `test_preview_version_sync.py` as-is (it's still correctly guarding its original hazard) but treat it as necessary, not sufficient.
2. Add a companion check — either a new pytest integration test or a dedicated `docs-pdf`-style tox env — that actually compiles a fixture `.typ` document exercising all four packages using `typst-py` pinned to the *new* floor (0.15+), and runs it in CI as a required check, not just in the advisory `drift.yml` job. This is the test that would have caught the original `kai` break before it reached a release, since `drift.yml` is intentionally advisory (D-07, never a required check) and the milestone's own regular CI wasn't resolving unpinned versions at the time of the original incident.
3. When bumping, update all three sites plus verify the *fourth* implicit site: any example/fixture `.typ` files under `tests/roots/` or `examples/` that might have their own hardcoded `@preview` imports copy-pasted from the template rather than generated — grep for `@preview/` across the whole repo (not just the three known files) before considering the sync complete: `grep -rln "@preview/" --include="*.typ" --include="*.py" .`

**Warning signs:**
- `test_preview_versions_identical_across_declaration_sites` and `test_all_four_packages_declared` both green, but `docs-pdf` / PDF-integration tests still fail — direct evidence the sync test's scope (agreement) is insufficient and the compile-correctness gap (Pitfall 1) is what's actually broken.
- A `grep -rn "@preview/" .` turning up a `@preview/...` reference in a file not in `{writer.py, template_engine.py, templates/base.typ}` — an undocumented fourth site that the existing test structurally cannot see.

**Phase to address:**
The FWD-02 (typst 0.15+) phase, as part of the same work that edits the three sync sites — add the compile-verification check in the same commit/PR that performs the version bump, so the bump can never land "sync-passing but compile-broken."

---

### Pitfall 5: CI/matrix, cross-OS, and docs-PDF traps specific to a new compiler major

**What goes wrong:**
Several failure modes are specific to *this* CI topology (3-OS × 4-Python matrix, plus a separate `docs.yml` PDF build) rather than to the port itself:
- The `sphinx>=5.0,<9` and `docutils>=0.18,<0.22` ceilings are duplicated across **eight** call sites today (`pyproject.toml` ×3, `tox.ini` ×4 — `[testenv]`, `[testenv:type]` twice for sphinx+docutils), not just the well-known three `@preview` sites. Missing one during the bump (e.g. updating `pyproject.toml` but leaving `tox.ini`'s `[testenv:type]` `docutils>=0.18,<0.22`) produces a *type-check* job that silently keeps testing against the old docutils stub types (`types-docutils>=0.18`) while the runtime tests exercise the new one — a split-brain CI where `mypy` and `pytest` are validating against different dependency universes and neither catches it.
- `docs.yml`'s PDF job (`docs-pdf` tox env) is the single place that exercises `typstpdf` end-to-end against a real, non-trivial document (the project's own docs) including admonitions (gentle-clues), code blocks (codly), and math (mitex) all in one build — this is precisely the fixture that would reproduce a `kai`-class error, but it currently only runs on `ubuntu-latest` in `docs.yml`. If the `@preview` bump behaves differently across OS-specific font/Unicode handling (typst's text-shaping and font-fallback logic is a known source of macOS/Windows-vs-Linux rendering differences) that divergence won't be caught, because PDF compilation is never exercised on macOS or Windows — only the matrix's Python-level `pytest` suite runs there.
- `drift.yml` is the only workflow that resolves *unpinned* latest versions and is explicitly advisory (never a required check, per D-07 in PROJECT.md's Key Decisions) — meaning even after this milestone lands, a future `@preview`-ecosystem or Sphinx/typst drift will again only be reported as a non-blocking issue, not caught before merge, unless this milestone also tightens that decision for the newly-adopted majors.

**Why it happens:**
The matrix was built incrementally across several prior phases (Python-floor modernization, tooling-floor modernization, durability guardrails) each of which added its own duplication point without a single source of truth for "what sphinx/docutils/typst range is currently supported" — the same structural pattern that caused the `@preview` 3-way sync problem, just wider (8 sites instead of 3) and currently *unguarded* by any test (unlike the `@preview` versions, there is no `test_dependency_ceiling_sync.py` equivalent).

**How to avoid:**
1. Before starting, enumerate every ceiling site with `grep -rn "sphinx>=5.0,<9\|sphinx<9\|docutils>=0.18,<0.22\|docutils<0.22\|typst>=0.14.1,<0.15\|typst<0.15" --include="*.toml" --include="*.ini"` and treat that list as the literal edit checklist for the phase's plan/PR description — don't rely on memory or on `pyproject.toml` alone.
2. Consider adding a lightweight sync test analogous to `test_preview_version_sync.py` for the sphinx/docutils/typst ceilings across `pyproject.toml` and `tox.ini`, so this class of partial-bump mistake gets the same loud-CI-failure treatment the `@preview` versions already have, instead of relying on a human checklist alone.
3. Since `docs-pdf` is the only end-to-end reproduction of the actual `kai`-class failure mode and it only runs on ubuntu, explicitly decide (and document the decision) whether this milestone needs to add a Windows and/or macOS PDF-compile smoke check — even a minimal one-OS-extra addition specifically for the typst-0.15 cutover, given font/text-shaping is a documented typst 0.15 change area (variable-font family-name trimming was called out as a "minor breaking change" in the 0.15 release notes) — rather than assuming Linux green implies cross-OS green.
4. Revisit whether `drift.yml` should temporarily become a required check (or at minimum be run manually via `workflow_dispatch` and reviewed) during the first few weeks after this milestone ships, since the entire purpose of this milestone is escaping a rot cycle that an advisory-only drift detector already failed to prevent once.

**Warning signs:**
- CI green on `type-check` but red on the matrix `test` jobs (or vice versa) after a dependency-ceiling PR — the split-brain signature described above.
- `docs.yml`'s `docs-pdf` step green while a Windows/macOS-specific bug report surfaces post-release — the cross-OS PDF gap made concrete.
- Any future `drift.yml` run failing and only producing a GitHub issue (per its current design) rather than blocking a merge — expected behavior today, but worth re-confirming is still the desired posture once the newly-adopted majors are in place.

**Phase to address:**
Split across FWD-01/FWD-02 (fix the 8-site ceiling duplication as part of the pin-raising work, with the enumerate-first grep as a plan-level checklist item) and a closing "CI green across full matrix" phase (verify the docs-pdf cross-OS question explicitly, and decide on drift.yml's required-check posture) — mirroring how the previous milestone sequenced pin-raising then a dedicated full-matrix-verification phase.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|--------------------|-----------------|------------------|
| Bump all four `@preview` packages together "to be safe" without isolating which one caused `kai` | Faster to land one PR | Can't attribute a future regression to a specific package; may mask that one bump introduced its own breaking change (e.g. codly's ref/numbering rework) | Never for this milestone — the whole point is understanding root cause after the last cycle's guesswork ("likely gentle-clues or codly") turned out to be unconfirmed |
| Leave `sphinx<9`/`docutils<0.22` duplicated across 8 sites without a sync test | Saves writing one more test file | Repeats the exact class of mistake `test_preview_version_sync.py` was built to prevent, just for a different dependency set | Acceptable only if the enumerate-and-checklist discipline (Pitfall 5, prevention #1) is followed rigorously every time; a sync test is still the more durable fix |
| Skip cross-OS PDF compile verification for this cutover ("Linux green is good enough, matches last milestone's approach") | Less CI to add/maintain | typst 0.15's own release notes flag font/text-shaping changes as a breaking-change category; a macOS/Windows-only PDF bug ships silently to users on those platforms | Acceptable short-term if explicitly documented as a known gap in PROJECT.md, not acceptable as a silent omission |
| Treat `test_preview_version_sync.py` passing as proof the `@preview` bump is "done" | One green test suite is a satisfying finish line | The test only proves internal agreement, not that typst 0.15 actually compiles the bundle (Pitfall 4) | Never — always pair with an actual `typst compile` smoke test of a fixture exercising all four packages |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|-----------------|-------------------|
| Typst Universe `@preview` packages | Trusting a package's declared minimum-compiler-version (`compiler = "0.12.0"`) as proof of forward compatibility with 0.15+ | Minimum-version declarations say nothing about upper-bound compatibility; the package must actually be compiled with the target typst version — GitHub release changelogs (not the Universe listing page) are the more reliable source for explicit version-specific fixes, and even those (as seen with codly's GitHub-releases-vs-Universe-page version discrepancy found in this research) can disagree and need direct verification |
| `typst-py` (the Python wrapper) | Assuming `typst-py`'s own version ceiling (`typst>=0.14.1,<0.15`) is the only thing gating the compiler version — forgetting that `typst-py` itself must also be bumped to a release that bundles/targets the typst 0.15 compiler binary | Check `typst-py`'s own PyPI `requires_python`/changelog for which typst-core version each `typst-py` release embeds before assuming "just remove the `<0.15` ceiling" is sufficient |
| Sphinx's own `docutils` pin | Bumping typsphinx's `sphinx` ceiling without checking Sphinx's *own* transitive `docutils` constraint (Sphinx 9.0.4 requires `docutils<0.23,>=0.20`, tighter than typsphinx's current `>=0.18,<0.22`) | Always fetch the target Sphinx version's own `requires_dist` from PyPI JSON metadata before setting typsphinx's own docutils range, so the two ranges have a non-empty intersection |
| GitHub Actions artifact/action versions vs. new dependency majors | Assuming a dependency-pin milestone is unrelated to CI action versions | Not directly required by this milestone, but the prior milestone's D-03 amendment (artifact actions on node20 getting removed from hosted runners) is a reminder that GitHub's own runner deprecations run on an independent clock from this project's dependency pins — worth a quick recheck that nothing new has landed since Phase 4/5 closed |

## Performance Traps

Not the focus of this milestone (a CI/compatibility port, not a scale-sensitive feature), but two items carry over from the existing `CONCERNS.md` and interact with the port:

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|------------------|
| `TypstBuilder.get_outdated_docs()` always rebuilds every document | Full CI matrix + docs-pdf builds take longer than necessary while iterating on the `@preview`/pin bumps during this milestone | Out of scope for this milestone (explicitly listed as "orthogonal tech debt" in PROJECT.md) — just be aware iteration loops during the port will be slower than an incremental-aware builder would allow | Already true today; not new to this milestone |
| Template content reloaded/reprocessed on every document write (`template_engine.py`) | Marginal; not expected to change behaviorally under Sphinx 9/typst 0.15 | No action needed for this milestone | N/A |

## Security Mistakes

Not a primary concern for this milestone (a dependency-porting task with no new user-facing surface), but one item is directly relevant to the port:

| Mistake | Risk | Prevention |
|---------|------|------------|
| Bumping `@preview` package versions from Typst Universe without checking the package's own repository/maintainer activity | Typst Universe packages are community-published; an abandoned or compromised package version could be pulled into the "known-good bundle" without scrutiny beyond "does it compile" | When selecting the exact pinned versions for `codly`/`codly-languages`/`mitex`/`gentle-clues`, spot-check that the chosen version corresponds to a tagged release in the package's own GitHub repo (not just a Universe listing) before pinning it as the new known-good bundle |

## "Looks Done But Isn't" Checklist

- [ ] **Sphinx 9 pin raised:** Verify `requires-python` was *also* raised to match Sphinx 9's actual floor (`>=3.11` per PyPI metadata at research time — re-check against whatever Sphinx version is actually pinned) — a green `pip install`/`uv sync` on 3.11+ lanes alone does not prove the 3.10 lane was correctly removed everywhere (classifiers, tox env_list, CI matrix, mypy/black/ruff target-version).
- [ ] **`@preview` packages bumped:** Verify the bump was isolated/attributed (Pitfall 1) — not just "all four bumped, tests are green" — and that a real `typst compile` was exercised against typst 0.15+, not only the static version-sync test.
- [ ] **`traverse()` → `findall()`:** Verify no other raw docutils/Sphinx-internal calls were missed — re-run the grep checklist from Pitfall 3 after all other changes in the milestone land, not just once at the start.
- [ ] **Dependency ceilings synced:** Verify all eight `sphinx`/`docutils`/`typst` ceiling sites (not just the three well-known `@preview` sites) were updated together — `grep` the old ceiling strings repo-wide and confirm zero matches remain.
- [ ] **CI green "across the matrix":** Verify this means the *actual* target matrix (post Python-floor change) is green, not that the old 3.10-inclusive matrix happens to still pass by accident (e.g. because the sphinx constraint was left loose enough to silently resolve pre-9 on 3.10) — check the resolved `sphinx`/`typst`/`docutils` versions per-lane in CI logs.
- [ ] **`docs-pdf` build:** Verify it was actually exercised against the newly bumped `@preview` versions and typst 0.15+ (not against a stale local install) before calling this milestone done — and consider whether cross-OS PDF verification is an explicit accepted gap or an oversight (Pitfall 5).

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|-----------------|------------------|
| Wrong package bumped, `kai`-class error persists | LOW | Bisect by reverting to one-package-at-a-time bumps (Pitfall 1, prevention #2); the mitex-changelog lead (v0.2.6 fixes "kai is deprecated") is the strongest starting hypothesis found in this research |
| Python-floor mismatch discovered mid-PR (3.10 lane failing to resolve) | LOW | Raise `requires-python`, drop the 3.10 lane from `tox.ini`/`ci.yml`/classifiers/mypy-black-ruff target-version in a single follow-up commit; no data loss, just a CI-red state until fixed |
| `@preview` version-sync test green but `docs-pdf` still fails (compile-correctness gap) | MEDIUM | Add the missing compile-verification step (Pitfall 4, prevention #2) before attempting further version churn — otherwise every subsequent bump attempt repeats the same blind-guessing failure mode as the original incident |
| Ceiling desync discovered late (mypy and pytest validating against different docutils universes) | MEDIUM | Re-grep all eight sites (Pitfall 5), fix in one commit, re-run full matrix; consider adding the sync test at this point rather than deferring again |
| Cross-OS PDF regression discovered post-release (font/text-shaping divergence) | HIGH | Requires a patch release; retroactively add the Windows/macOS `docs-pdf` CI job that should have caught it, then bisect the specific `@preview` package/typst version combination causing the OS-specific rendering difference |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|-------------------|----------------|
| `@preview` package trap (wrong package bumped / mutual-compile not verified) | FWD-02 (typst 0.15+) | A fixture `.typ` exercising all four packages actually compiles via `typst-py` pinned to the new floor, run as a required CI check — not just `test_preview_version_sync.py` passing |
| Python-floor trap | FWD-01 (Sphinx 9), first sub-step | `requires-python`, tox `env_list`, CI matrix, classifiers, and mypy/black/ruff target-version all agree; `uv sync --locked` succeeds on every declared lane with the intended Sphinx major actually resolved (check logged version, not just exit code) |
| Removed/deprecated docutils API (`traverse()` etc.) | FWD-01 (Sphinx 9), preparatory commit | `grep` checklist (Pitfall 3) returns zero hits; full pytest suite green against actual (not pinned-back) Sphinx 9 / docutils 0.22 |
| Three-way (now effectively N-way) `@preview` sync desync | FWD-02 (typst 0.15+), same PR as the version bump | `test_preview_version_sync.py` green AND the new compile-verification check (above) green AND a repo-wide `grep -rn "@preview/"` shows no undocumented fourth site |
| 8-site dependency-ceiling desync + cross-OS/CI matrix gaps | FWD-01/FWD-02 plus a closing full-matrix-verification phase | Repo-wide grep for old ceiling strings returns zero hits; CI green on the *actual* target matrix with resolved versions confirmed in logs; explicit decision recorded (in PROJECT.md, as this milestone's other decisions have been) on cross-OS PDF verification and `drift.yml`'s required/advisory posture |

## Sources

- `pyproject.toml`, `tox.ini`, `.github/workflows/ci.yml`, `.github/workflows/docs.yml`, `.github/workflows/drift.yml` — direct repo inspection (HIGH confidence, primary source)
- `typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ`, `typsphinx/builder.py`, `typsphinx/translator.py` — direct repo inspection (HIGH confidence, primary source)
- `tests/test_preview_version_sync.py` — direct repo inspection (HIGH confidence, primary source)
- `.planning/PROJECT.md`, `.planning/codebase/CONCERNS.md`, `.planning/codebase/INTEGRATIONS.md` — direct repo inspection (HIGH confidence, primary source)
- PyPI JSON API, `Sphinx` 9.0.4 metadata (`requires_python`, `requires_dist`) — fetched directly via `pypi.org/pypi/Sphinx/9.0.4/json` (HIGH confidence, primary/official registry source)
- PyPI JSON API, `docutils` 0.22.4 and `typst` 0.15.0 metadata — fetched directly via `pypi.org/pypi/<pkg>/<ver>/json` (HIGH confidence, primary/official registry source)
- `mitex-rs/mitex` `CHANGELOG.md` (github.com) — v0.2.6 "fix 'kai is deprecated' warning for Typst v0.14.0" entry (MEDIUM confidence — single-source changelog claim, not independently reproduced by compiling in this research pass; **must be verified by actually compiling** before being treated as confirmed root cause)
- `jomaway/typst-gentle-clues` GitHub releases page, and `typst.app/universe/package/gentle-clues` — version/compatibility claims (LOW confidence — the two sources disagreed on the latest version number, 1.2.0 vs 1.3.1; re-verify at execution time)
- `Dherse/codly` GitHub releases page, and `typst.app/universe/package/codly` — version/compatibility claims (LOW confidence — same cross-source disagreement pattern; re-verify at execution time)
- `typst.app/docs/changelog/0.15.0/` and `typst.app/blog/2026/typst-0.15/` — typst 0.15 release notes, breaking-changes summary (MEDIUM confidence, web search synthesis of official changelog content)
- `docutils.sourceforge.io/RELEASE-NOTES.html` — docutils 0.21/0.22/0.23 API-removal history (MEDIUM confidence, web-fetched synthesis of official release notes)

---
*Pitfalls research for: Sphinx builder/writer extension forward-porting (typsphinx v0.5.0, Sphinx 9 + typst 0.15+)*
*Researched: 2026-07-09*
