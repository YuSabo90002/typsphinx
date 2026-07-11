# Architecture Research: Sphinx 9 + typst 0.15+ Forward Integration

**Domain:** Sphinx builder extension / Typst compiler integration (typsphinx v0.5.0 forward-ecosystem milestone)
**Researched:** 2026-07-09
**Confidence:** HIGH (all load-bearing claims verified against primary sources: PyPI JSON metadata, GitHub source/type-stubs, official Sphinx/docutils changelogs) with one MEDIUM-confidence item flagged explicitly (the `kai` root-cause package)

> Supersedes the prior (2026-07-04) version of this file, which was written for the *previous* milestone's backward-pinning fix (v0.4.4: pin down to typst 0.14.9/sphinx<9/docutils<0.22). This document is for the current milestone, which moves forward instead.

## Standard Architecture

### System Overview (unchanged by this milestone — no new components)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Sphinx Entry Point — typsphinx/__init__.py:setup()                 │
│  registers TypstBuilder, TypstPDFBuilder, 14 typst_* config values  │
│  NOT AFFECTED: add_config_value(name, default, rebuild, [types])    │
│  positional-list signature confirmed unchanged in Sphinx 9           │
└───────────────────────────┬───────────────────────────────────────────┘
                             │
        ┌────────────────────┴─────────────────────┐
        ▼                                            ▼
┌───────────────────────┐                 ┌──────────────────────────┐
│ TypstBuilder           │                 │ TypstPDFBuilder          │
│ builder.py              │                │ (extends TypstBuilder)   │
│ NOT AFFECTED:           │                │ NOT AFFECTED: same       │
│ Builder base-class API  │                │ base-class contract      │
│ (init/get_outdated_docs/│                │                          │
│ write/write_doc/finish) │                │                          │
│ unchanged in Sphinx 9   │                │                          │
└───────────┬─────────────┘                └────────────┬─────────────┘
            │                                            │
            └──────────────────┬─────────────────────────┘
                                ▼
                    ┌────────────────────────────┐
                    │ TypstWriter — writer.py     │
                    │ NOT AFFECTED (translator     │
                    │ base class stable) BUT        │
                    │ MODIFIED (version-bump only): │
                    │ 4 hardcoded #import lines      │
                    │ (included-doc branch)          │
                    └──────────────┬─────────────────┘
                                   ▼
                    ┌────────────────────────────┐
                    │ TypstTranslator             │
                    │ translator.py                │
                    │ extends SphinxTranslator      │
                    │ NOT AFFECTED at the API level;│
                    │ VERIFY-ONLY risk: typst 0.15   │
                    │ stdlib removals could invalidate│
                    │ *emitted* Typst syntax (not the │
                    │ Python translator code itself)  │
                    └──────────────┬─────────────────┘
                                   ▼
                    ┌────────────────────────────┐
                    │ TemplateEngine               │
                    │ template_engine.py            │
                    │ MODIFIED (version-bump):       │
                    │ 4 hardcoded #import lines       │
                    │ (render() master-doc branch)    │
                    │ OPTIONAL cleanup: doctree.       │
                    │ traverse() → findall() at        │
                    │ extract_toctree_options()        │
                    └──────────────┬─────────────────┘
                                   ▼
                    ┌────────────────────────────┐
                    │ base.typ template            │
                    │ templates/base.typ            │
                    │ MODIFIED (version-bump):       │
                    │ 4 hardcoded #import lines        │
                    └──────────────┬─────────────────┘
                                   ▼
                    ┌────────────────────────────┐
                    │ PDF Compilation — pdf.py      │
                    │ NOT AFFECTED: typst.compile()  │
                    │ signature (incl. `root=` kwarg)│
                    │ confirmed unchanged in typst-py│
                    │ 0.15.0. OPTIONAL enhancement:  │
                    │ TypstError now exposes          │
                    │ .hints/.trace/.diagnostic        │
                    │ (unused today, still works)      │
                    └────────────────────────────────┘
```

**Net shape of the change:** this is *not* an architectural rewrite. Every layer boundary (Builder → Writer → Translator → TemplateEngine → pdf.py) survives the Sphinx 9 / docutils 0.22 / typst 0.15 / typst-py 0.15 jump unchanged at the API-contract level. The only *guaranteed* code edits are the three lockstep `#import "@preview/..."` blocks (version bump) and the dependency-pin ceilings. Everything else in `translator.py`/`builder.py`/`writer.py`/`pdf.py` is "verify via full CI matrix, fix reactively if something surfaces" — not "known to require a patch." Treat any speculative pre-emptive rewrite of those files as scope creep.

### Component Responsibilities (unchanged ownership, integration-risk column added)

| Component | Responsibility | File | Sphinx-9 risk | typst-0.15 risk |
|-----------|----------------|------|----------------|------------------|
| Extension setup | Register builders + config values | `typsphinx/__init__.py` | None (confirmed) | None |
| TypstBuilder | Build lifecycle, doc iteration, asset copy | `typsphinx/builder.py` | None (confirmed) | None |
| TypstPDFBuilder | PDF compile orchestration | `typsphinx/builder.py` | None | Indirect (calls pdf.py which calls typst-py) |
| TypstWriter | master/included branch, template invocation | `typsphinx/writer.py` | None | **Direct — hardcoded `@preview` versions** |
| TypstTranslator | doctree → Typst markup visitor | `typsphinx/translator.py` | None confirmed | **Verify-only — emitted syntax must still compile under typst 0.15** |
| TemplateEngine | template load/render/param-map | `typsphinx/template_engine.py` | Low (deprecated but working `traverse()` call) | **Direct — hardcoded `@preview` versions** |
| base.typ | default document template | `typsphinx/templates/base.typ` | None | **Direct — hardcoded `@preview` versions** |
| PDF utilities | typst-py wrapper, error parsing | `typsphinx/pdf.py` | None | None (signature-compatible); optional error-detail enhancement |

## Recommended Project Structure

No new files, folders, or modules are needed. This milestone is a **pin + lockstep-version + reactive-fix** exercise across the existing five-module pipeline (`__init__.py`, `builder.py`, `writer.py`, `translator.py`, `template_engine.py`) plus the bundled `templates/base.typ`, `pyproject.toml`, and `tox.ini`. Do not introduce a version-abstraction module, a compat shim layer, or config-driven `@preview` versions (FWD-03) — both are explicitly out of scope for v0.5.0 per PROJECT.md.

## Architectural Patterns (integration-specific)

### Pattern 1: Three-way lockstep version declaration

**What:** The four `@preview` package imports (`codly`, `codly-languages`, `mitex`, `gentle-clues`) are declared as literal `#import "@preview/<name>:<version>"` strings in three independent files: `typsphinx/writer.py` (included-document import block, ~lines 94–97), `typsphinx/template_engine.py` (master-document import block inside `render()`, ~lines 313–316), and `typsphinx/templates/base.typ`. `tests/test_preview_version_sync.py` parses all three files with the same regex and asserts the per-package version strings are identical across files (and that all four packages are declared in each file) — it does **not** hardcode expected version numbers, so it stays green through any lockstep rebump, and only fails on *divergence* between files.

**When to use:** Any time the bundled versions change (this milestone, and future dependency bumps).

**Trade-off:** Because the test is version-agnostic, it gives zero protection against picking a version that's wrong-but-consistent (e.g., bumping all three to a version that still doesn't compile under typst 0.15). It only prevents *desync*, not *incompatibility*. Compilation correctness must be verified separately via `tox -e docs-pdf` and the PDF-integration test suite.

### Pattern 2: Master vs. included document branching (unaffected, contextual)

**What:** `TypstWriter._is_master_document()` looks up `docname` in `typst_documents` config; master docs get the full `TemplateEngine.render()` treatment (which is where one of the three `@preview` blocks lives), included docs get a smaller literal import block (the second `@preview` block) because Typst's `#include()` does not inherit parent-file imports.

**Relevance to this milestone:** Both `@preview` blocks must be bumped together even though they live in structurally different code paths (`writer.py`'s hardcoded string list vs. `template_engine.py`'s hardcoded string list inside `render()`) — this is *why* the lockstep hazard exists in the first place, and it is unrelated to Sphinx/docutils version at all. No structural change to this pattern is needed or recommended.

### Pattern 3: Reactive verification over speculative fixing

**What:** Given that this research found **no confirmed API-signature breaks** in the Builder base class, `SphinxTranslator`, `docutils.writers.Writer`, `add_config_value()`, or `typst.compile()`, the correct engineering posture for `translator.py`, `builder.py`, and `pdf.py` is: raise the pins, run the full test suite + `docs-pdf` build, and fix only what actually breaks. Do not pre-emptively rewrite visitor methods or the PDF-compile wrapper on the theory that "Sphinx 9 probably changed something" — that inflates the diff and risks introducing regressions in code that was already correct.

**Trade-off:** This defers discovery of some breakage to CI-matrix time (Phase D below) rather than design time, but that's appropriate here — the actual reproducible failure evidence in PROJECT.md (`black` reformatting 3 files, the `kai` TypstError, matrix cascading failures) is entirely explained by (a) tooling drift unrelated to Sphinx/typst APIs and (b) the `@preview` incompatibility, not by a translator/writer API break.

## Data Flow

No change to the doctree → TypstTranslator → body string → TemplateEngine → `.typ` file → [PDF compile] pipeline shape. The only data-flow-relevant fact from this research: `typst.compile()`'s `root` keyword argument (used by `pdf.py:compile_typst_to_pdf()` to resolve `#include()` / relative asset paths against `self.outdir`) is confirmed present, in the same position/semantics, in typst-py 0.15.0's public signature — so the PDF-compile data path is unaffected.

### Key Data Flows (integration-relevant only)

1. **Version-bump propagation:** a single source-of-truth decision ("bump these four packages to these four versions") must be manually mirrored into 3 files (`writer.py`, `template_engine.py`, `templates/base.typ`) in the same commit/PR — there is no shared constant module today (that refactor is FWD-03, explicitly deferred).
2. **Dependency-ceiling propagation:** the `sphinx`/`docutils`/`typst` version ceilings are declared in `pyproject.toml` (`[project].dependencies`) and mirrored into `tox.ini` at 2 sites (`[testenv]` deps line and `[testenv:type]` deps lines) — all 3 sites must move together or `tox` environments will resolve inconsistent versions from what `uv sync` installs.

## Scaling Considerations

Not applicable in the traditional sense (this is a build-time doc-compiler, not a runtime service). The only "scale" axis relevant to this milestone is CI matrix breadth: 3 OS × 4 Python versions × (lint/type/cov/docs) — see the Python-floor collision below, which shrinks that matrix.

## Anti-Patterns

### Anti-Pattern 1: Version-conditional branching to span both majors

**What people might do:** Add `if sphinx.version_info >= (9, 0): ... else: ...` or try/except import fallbacks to support both the old (sphinx<9/typst<0.15) and new (sphinx 9/typst 0.15+) stacks simultaneously.

**Why it's wrong:** PROJECT.md's Scope Decisions explicitly lock this out — "LATEST-ONLY (no compat range — do NOT propose version-conditional branching to support both old and new)." It would also be unnecessary: this research found no API surface that actually requires such branching (Builder, SphinxTranslator, `add_config_value`, `typst.compile` are all stable across the jump).

**Do this instead:** Raise pins outright, drop the old ceiling, fix what breaks for the new stack only.

### Anti-Pattern 2: Fixing the `@preview` lockstep sites independently

**What people might do:** Bump `writer.py`'s versions in one PR/commit and `template_engine.py`/`base.typ` in a later one ("I'll get to the rest").

**Why it's wrong:** `test_preview_version_sync.py` will fail loudly the moment the three files disagree — by design (D-03 guardrail from the prior milestone) — so this anti-pattern is now caught by CI rather than silently shipping mismatched imports. Still, treat all three edits as one atomic change to avoid churn.

**Do this instead:** Single commit touching all three files with the same four version strings; let the sync test be the acceptance check.

### Anti-Pattern 3: Guessing the `kai`-symbol root cause and shipping unverified

**What people might do:** Bump only `gentle-clues` (the prime suspect) to its latest version and declare the milestone done without actually running `tox -e docs-pdf` against typst 0.15.

**Why it's wrong:** This research could **not** conclusively identify which of the four bundled `@preview` packages emits the `kai` symbol from public sources (package changelogs don't mention it explicitly, and package source wasn't fully inspectable via the tools available). It is plausible but unconfirmed that `gentle-clues:1.2.0 → 1.3.1` alone resolves it; `codly` has *no newer published version* to bump to (1.3.0 is both currently pinned and currently latest), so if `codly` turns out to be the actual source of `kai`, a version bump alone won't fix it and a different remediation (patch, fork, or replacement package) would be needed.

**Do this instead:** Bump all four to latest in one lockstep commit, run `docs-pdf` locally, and if `kai` persists, bisect by reverting one package at a time to isolate which one still throws it (see Pitfalls / Phase B below).

## Integration Points

### Confirmed-safe (no code change required by the version jump itself)

| Integration point | File | Verified fact | Source confidence |
|---|---|---|---|
| `Sphinx.add_config_value(name, default, rebuild, [types])` positional-list signature | `typsphinx/__init__.py` (14 call sites) | Signature is `(name, default, rebuild, types=(), description='')`; `types` accepts a plain list like `[list]` / `[str, type(None)]` unchanged in Sphinx 9.1.1 docs; no deprecation of the tuple/list-based interface found | HIGH (official Sphinx docs) |
| `sphinx.builders.Builder` base-class contract (`init`, `get_outdated_docs`, `get_target_uri`, `prepare_writing`, `write`, `write_doc`, `finish`, `allow_parallel`) | `typsphinx/builder.py` | No changes to these methods listed in Sphinx 9.0 changelog's Incompatible Changes / Deprecated APIs sections | HIGH (official Sphinx 9.0 changelog) |
| `sphinx.util.docutils.SphinxTranslator` base class | `typsphinx/translator.py` | Not mentioned in Sphinx 9.0 changelog's breaking/deprecated lists | MEDIUM (absence of evidence, not exhaustive audit of the class itself) |
| `docutils.writers.Writer` base class, `translate()` contract | `typsphinx/writer.py` | Sphinx 9.0 explicitly adds "Support Docutils 0.22"; no `Writer`-level break identified | HIGH |
| `nodes.Node.traverse()` / `.findall()` | `typsphinx/template_engine.py:239`, `typsphinx/builder.py` (already uses `findall()`) | `traverse()` has been deprecated-but-functional since docutils 0.18.1 (returns a list); no removal found through docutils 0.22.4 release notes | MEDIUM (release-notes text search, not changelog line-item) |
| `typst.compile(input, output=None, root=None, font_paths=..., ignore_system_fonts=False, format=None, ppi=None, sys_inputs={}, pdf_standards=[], package_path=None, timestamp=None, pretty=False, package_cache_path=None)` | `typsphinx/pdf.py:compile_typst_to_pdf()` (`typst.compile(temp_file, root=root_dir)`) | Confirmed via `messense/typst-py` repo's `src/lib.rs` and `python/typst/__init__.pyi` for the 0.15.0-era source — `root` kwarg present, `input` still first positional/keyword param | HIGH (primary source: package's own type stubs and Rust binding source) |

### Confirmed-required changes (version-bump only, no logic change)

| Integration point | File(s) | What changes | Depends on |
|---|---|---|---|
| Bundled `@preview` versions | `typsphinx/writer.py` (4 lines), `typsphinx/template_engine.py` (4 lines), `typsphinx/templates/base.typ` (4 lines) | Literal version strings for `codly`, `codly-languages`, `mitex`, `gentle-clues` | typst 0.15 compiler being installed to test against |
| Runtime dependency ceilings | `pyproject.toml` `[project].dependencies` (`sphinx>=5.0,<9` → raise; `docutils>=0.18,<0.22` → raise; `typst>=0.14.1,<0.15` → raise) | Ceiling values | none (first step) |
| tox dependency mirrors | `tox.ini` `[testenv]` deps line (`sphinx>=5.0,<9`), `[testenv:type]` deps lines (`sphinx>=5.0,<9`, `docutils>=0.18,<0.22`) | Must mirror `pyproject.toml`'s new ceilings exactly (2 sites, both in this one file) | pyproject.toml ceiling raise |
| `uv.lock` | repo root | Regenerate against new pins | pyproject.toml + tox.ini ceiling raise |

### High-risk / needs-empirical-verification (not confirmed safe, not confirmed broken)

| Integration point | File | Risk | Recommended verification |
|---|---|---|---|
| `codly` bundled version | `writer.py` / `template_engine.py` / `base.typ` | Currently pinned at 1.3.0, which is *also* the latest published version on Typst Universe as of this research — there is no newer version to bump to. If `codly` (not `gentle-clues`) is the actual `kai` emitter, a version bump alone cannot fix it | Bisect: temporarily drop `gentle-clues`/`mitex`/`codly-languages` imports from a minimal repro `.typ` file and compile with typst 0.15 to isolate which package throws `kai` before deciding remediation |
| `gentle-clues` bundled version | same 3 files | Prime suspect per PROJECT.md's own prior investigation; latest published (1.3.1, min typst 0.13.0) predates typst 0.15's official release, so "latest" is not the same as "confirmed 0.15-compatible" | Bump to 1.3.1 and run `tox -e docs-pdf`; if `kai` persists, escalate to bisection above |
| `mitex` / `codly-languages` bundled versions | same 3 files | Lower risk (both have newer published versions: `mitex` 0.2.4→0.2.7, `codly-languages` 0.1.1→0.1.10) but not independently confirmed as the `kai` source or ruled out | Bump alongside the other two; covered by the same `docs-pdf` verification pass |
| Typst 0.15 stdlib removals surfacing in translator-emitted syntax | `typsphinx/translator.py` (all `visit_*`/`depart_*` methods emitting raw Typst function calls, e.g. `heading()`, `par()`, `text()`) | Typst 0.15's own changelog states it "removes definitions from the standard library that were already deprecated in previous Typst versions" — if any translator-emitted Typst function/argument was one of those deprecated definitions, compilation will fail even after the `@preview` fix | Full PDF-integration test suite + `docs-pdf` build against the raised typst pin; grep translator.py for any Typst stdlib calls flagged deprecated in the [0.15.0 changelog](https://typst.app/docs/changelog/0.15.0/) if failures surface |
| `TypstError`'s new structured attributes (`.message`, `.diagnostic`, `.hints`, `.trace`) unused by `_parse_typst_error()` | `typsphinx/pdf.py` | Not a break (still `str(error)`-compatible, `TypstError` still subclasses `RuntimeError`) but a missed opportunity — richer error messages are now available for free | Optional, non-blocking: could enrich `_parse_typst_error()` to surface `.hints` in a follow-up, not required for v0.5.0 |

### Critical discovery not yet reflected in PROJECT.md: Sphinx 9's Python floor

**This is the highest-priority finding of this research and needs a roadmap-level decision, not just a code change.**

Verified directly against PyPI JSON metadata (`requires_python` field, HIGH confidence, primary source):

| Sphinx version | `requires-python` |
|---|---|
| 9.0.4 (matches PROJECT.md's failure-evidence run) | `>=3.11` |
| 9.1.0 (current latest on PyPI as of this research) | `>=3.12` |

typsphinx's current `pyproject.toml` declares `requires-python = ">=3.10"` and CI runs a `py310` lane — both established as deliberate decisions in the *previous* milestone (Phase 3, "Modernize Python floor to 3.10–3.13"). **Raising to Sphinx 9 unconditionally drops Python 3.10 support**, and if the resolved Sphinx pin is left unbounded within the 9.x line (`sphinx>=9`), `uv lock` may resolve to 9.1.0 and force a Python 3.12 floor too — dropping 3.11 as well.

This is a genuine "latest-only" scope ambiguity: does "typst 0.15+ / Sphinx 9" mean *pin to the earliest 9.x that still supports the widest matrix* (`sphinx>=9.0,<9.1`, Python 3.11 floor, matrix becomes py311–py313) or *track true latest* (`sphinx>=9.1`, Python 3.12 floor, matrix becomes py312–py313)? Either is defensible under "latest-only, no compat range" — but it must be decided explicitly before Phase A (pin-raise) rather than discovered accidentally when `uv lock --upgrade` picks a version and a CI lane goes red for an unrelated-looking reason. Docutils floor is not a blocker either way: Sphinx 9.0.4's own `requires_dist` pins `docutils<0.23,>=0.20`, comfortably covering the 0.22.x line already validated in PROJECT.md's failure-evidence run.

### Pre-existing, unrelated bug surfaced during this research

`typsphinx/__init__.py:14` hardcodes `__version__ = "0.4.3"` while `pyproject.toml`'s `version` field is `"0.4.4"` (and the package is not using `dynamic = ["version"]` — the two are independently maintained strings). This drift already exists on `main` and should be corrected to `"0.5.0"` (not just re-synced to `"0.4.4"`) as part of this milestone's release step, since `setup()` returns this string as the extension's reported version metadata to Sphinx.

## Recommended Build Order

Ordered by dependency; steps in the same phase can run in parallel unless noted.

**Phase A — Pin raise + lockfile (no functional fixes yet)**
1. Decide the Sphinx 9.x pin-width question above (blocking prerequisite — affects `requires-python`, tox `env_list`, and the CI matrix, not just `pyproject.toml`'s `sphinx` line).
2. Raise ceilings in `pyproject.toml` (`[project].dependencies`) and mirror into `tox.ini` (`[testenv]` + `[testenv:type]` deps) — 3 sites, 1 file pair, must move together.
3. Regenerate `uv.lock`.
4. *Expected state after Phase A: CI still red* (typ-PDF tests fail on `kai`; possibly some lint/black reformatting per the failure evidence). This phase's only goal is getting the real Sphinx 9 / docutils 0.22 / typst 0.15 stack installed so Phase B/C can be diagnosed against reality instead of guesswork.

**Phase B — `@preview` package bump + 3-way sync (depends on Phase A)**
5. Bump all four bundled versions in lockstep across `writer.py`, `template_engine.py`, `templates/base.typ` in one commit (start with `gentle-clues→1.3.1`, `mitex→0.2.7`, `codly-languages→0.1.10`; `codly` has no newer version available — see risk table).
6. Run `tox -e docs-pdf` locally. `test_preview_version_sync.py` should pass automatically (it's version-agnostic) as long as all three files agree — it is not the compilation-correctness check.
7. If `kai` persists, bisect per the Anti-Pattern 3 procedure above to isolate the true source package before considering non-version remediations (patch/fork/replace).

**Phase C — translator/writer/API fixes (C1 parallel with Phase B; C2 depends on Phase B)**
- C1 (no dependency on B — can start immediately after Phase A): fix `black`/`ruff`/`mypy` findings on the 3 files already identified in PROJECT.md's failure evidence (`docs/build_multilang.py`, `tests/test_config_other_options.py`, `tests/test_config_toctree_defaults.py`); run the non-PDF pytest suite against Sphinx 9/docutils 0.22 and fix any incidental API-usage breakage; optionally modernize `template_engine.py`'s `doctree.traverse()` → `findall()`.
- C2 (depends on B completing so a `kai`-free PDF baseline exists): run the full PDF-integration test suite + `docs-pdf` build; fix any translator-emitted-syntax breakage against typst 0.15's stdlib removals (see risk table); if `pdf.py`'s error reporting needs the new `TypstError` structured fields to diagnose C2 failures faster, that's the moment to add them (still optional for shipping).

**Phase D — CI-matrix green + docs PDF (depends on A+B+C, verification-only)**
8. Push, observe the full OS × Python matrix (width determined by the Phase A decision) + lint/type/coverage/build + `docs.yml` (including its `docs-pdf` step) go green end-to-end, matching the previous milestone's "observed Actions run" validation bar.

**Phase E — guardrail-ceiling updates + release (depends on Phase D)**
9. Update any dependent guard ceilings that mirror the new majors — check `tox.ini`'s `types-docutils>=0.18` floor and `pyproject.toml`'s `[dependency-groups]` `types-docutils` pin against the new docutils floor; confirm the `sphinx-typst-stack` Dependabot group (from the prior milestone's D-03) doesn't need scope changes.
10. Fix the pre-existing `__version__ = "0.4.3"` vs. `pyproject.toml` `version = "0.4.4"` drift — set both to `"0.5.0"`.
11. Tag and release via the existing `release.yml` (unchanged from last milestone; already hardened for the `tomllib`/`tomli` fallback and `softprops/action-gh-release@v3`).

## Sources

- [Sphinx 9.0 Changelog](https://www.sphinx-doc.org/en/master/changes/9.0.html) — HIGH, official
- [Sphinx `add_config_value` / extdev appapi docs](https://www.sphinx-doc.org/en/master/extdev/appapi.html) — HIGH, official
- [Docutils Release Notes](https://docutils.sourceforge.io/RELEASE-NOTES.html) — HIGH, official (0.18.1 `traverse()`/`findall()` entry confirmed; no 0.22 removal found)
- PyPI JSON API, `https://pypi.org/pypi/sphinx/9.0.4/json` and `https://pypi.org/pypi/sphinx/json` (latest = 9.1.0) — HIGH, primary package metadata; confirms `requires_python` floors (`>=3.11` for 9.0.4, `>=3.12` for 9.1.0) and `docutils<0.23,>=0.20` dependency range
- PyPI JSON API, `https://pypi.org/pypi/typst/json` — HIGH, confirms typst-py 0.15.0, `requires_python = ">=3.8"` (no floor collision)
- `messense/typst-py` GitHub repo, `src/lib.rs` and `python/typst/__init__.pyi` (fetched directly via `gh api`) — HIGH, primary source for `typst.compile()` signature and `TypstError`/`TypstWarning` structured-exception shape
- [gentle-clues – Typst Universe](https://typst.app/universe/package/gentle-clues/) — HIGH for version/date facts, MEDIUM for the `kai` root-cause attribution (not independently confirmed)
- [codly – Typst Universe](https://typst.app/universe/package/codly/), [codly-languages – Typst Universe](https://typst.app/universe/package/codly-languages/), [mitex – Typst Universe](https://typst.app/universe/package/mitex/) — HIGH for version/date facts
- [Typst 0.15.0 changelog](https://typst.app/docs/changelog/0.15.0/) — MEDIUM (summarized via search; "removes deprecated stdlib definitions" claim not independently line-item verified against typsphinx's translator output)
- `jomaway/typst-gentle-clues` GitHub repo (releases page, source browse) — MEDIUM (release dates/version list confirmed; could not locate a `kai` symbol reference or full CHANGELOG.md content through available tooling)
- Project-local: `.planning/PROJECT.md`, `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/CONCERNS.md`, `.planning/codebase/INTEGRATIONS.md`, `typsphinx/builder.py`, `typsphinx/writer.py`, `typsphinx/translator.py`, `typsphinx/template_engine.py`, `typsphinx/pdf.py`, `typsphinx/__init__.py`, `tests/test_preview_version_sync.py`, `pyproject.toml`, `tox.ini`, `.github/workflows/{ci,drift}.yml` — HIGH, primary source (own repo)

---
*Architecture research for: typsphinx v0.5.0 forward-ecosystem (Sphinx 9 + typst 0.15+) integration*
*Researched: 2026-07-09*
