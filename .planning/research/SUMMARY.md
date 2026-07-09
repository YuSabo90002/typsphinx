# Project Research Summary

**Project:** typsphinx v0.5.0 — Forward-ecosystem milestone (Sphinx 9 + typst 0.15+, latest-only)  
**Domain:** Sphinx extension (docutils→Typst builder) — dependency forward-compat port  
**Researched:** 2026-07-09  
**Confidence:** MEDIUM (HIGH for stack/architecture; MEDIUM for `kai` root-cause identification — requires empirical verification)

## Executive Summary

The typsphinx v0.5.0 milestone is a forward-ecosystem port targeting the latest Sphinx 9.x and typst 0.15 compilers. This is **not a feature milestone** — it's a maintenance/durability exercise: raise four dependency ceilings (`sphinx`, `docutils`, `typst`, `@preview` packages), fix version mismatches, and empirically verify compilation under the new stack. The good news: **no builder/writer/translator API breaks were found in Sphinx 9**, so this is a pin-and-verify exercise, not a rewrite.

The bad news: **Sphinx 9 forces a hard Python-floor jump** from 3.10 to 3.12. Sphinx 9.0 requires Python >=3.11; Sphinx 9.1 (current latest) requires Python >=3.12. This is a blocking scope decision that must be made before roadmap phases are cut — it affects CI matrix width, tox `env_list`, classifiers, and mypy/ruff target-version in lockstep. Additionally, **the `kai`-symbol TypstError (blocked PDF builds in v0.4.4) has been traced to `mitex:0.2.4`**, which emits a deprecated symbol that typst 0.15 removed outright. Mitex v0.2.6+ has the fix (changelog confirms: *"Fix: fix 'kai is deprecated' warning for Typst v0.14.0"*), but empirical compilation is needed to confirm.

**Recommended approach:** (A) decide the Python floor + Sphinx-pin width question (9.0 vs 9.1, Python 3.11 vs 3.12); (B) raise all four dependency ceilings and regenerate lockfile; (C) bump the four `@preview` packages in lockstep across three hardcoded sites; (D) run `docs-pdf` build to verify the `kai` fix and catch any typst-0.15-stdlib-removal breaks; (E) full CI matrix validation; (F) guardrail-ceiling sync updates + version-string fix + release. No structural code rewrites expected in steps D/E unless empirical failures surface.

## Key Findings

### Recommended Stack

Per STACK.md research (cross-verified against PyPI JSON API, official changelogs, GitHub package registry):

**Core runtime dependencies — raise these ceilings:**
- **Sphinx** → `>=9.1,<10` (was `>=5.0,<9`): Latest Sphinx 9.1.0 (released 2025-12-31), but this forces Python `>=3.12` floor. Alternative: `>=9.0,<9.1` keeps Python `>=3.11` (softer landing, contradicts "latest-only" scope decision).
- **docutils** → `>=0.21,<0.23` (was `>=0.18,<0.22`): NOT `>=0.22` or allowing 0.23 — Sphinx 9.1 itself pins `docutils<0.23,>=0.21`, narrower than typsphinx's current range. Resolves to docutils 0.22.4.
- **typst** → `>=0.15.0,<0.16` (was `>=0.14.1,<0.15`): PyPI's `typst` package wraps the Typst compiler 1:1. Tight ceiling — typst 0.16 does not exist yet; allow Dependabot to file an issue when it lands.
- **Python** → `requires-python = ">=3.12"` (was `>=3.10`): **Blocking scope decision.** Sphinx 9.1.0's own metadata forces this. Must be decided before Phase A.

**Bundled Typst Universe `@preview` packages — version-sync across 3 files:**
- **`mitex`** → `0.2.7` (was `0.2.4`): **This is the `kai` fix.** Changelog: v0.2.6 = `"Fix: fix 'kai is deprecated' warning for Typst v0.14.0"`. Low risk (no `mi()` API break 0.2.4→0.2.7).
- **`gentle-clues`** → `1.3.1` (was `1.2.0`): Secondary suspect from PROJECT.md's earlier speculation; no breaking change to admonition functions (all remain `#let x(..args)` style). Changelog shows translation additions, no API change.
- **`codly-languages`** → `0.1.10` (was `0.1.1`): Largest version gap; internal icon rendering tweaked, but export dict shape unchanged. Safe drop-in.
- **`codly`** → `1.3.0` (stays same, no newer version published on Universe): **High-risk verification item.** Already at registry ceiling. If it breaks under typst 0.15, no version bump fallback; would require fork/patch/replacement. Must empirically verify.

These three locations must be bumped together (atomic commit) or `tests/test_preview_version_sync.py` fails on desync:
- `typsphinx/writer.py` (lines ~94–97)
- `typsphinx/template_engine.py` (lines ~313–316)
- `typsphinx/templates/base.typ` (lines 8–19)

### Expected Features

Per FEATURES.md research — this is a **maintenance/compatibility cycle**, so "features" = required-to-compile work items:

**Table stakes (must-fix to compile/pass CI):**
- Bump all four `@preview` packages in lockstep across the 3-way sync sites (mitex is the root-cause fix; gentle-clues/codly-languages are hygiene; codly needs empirical verification).
- Update `tests/test_preview_version_sync.py` expected-version constants to match the new pins — it will fail CI if the three files disagree.
- Empirically verify `codly:1.3.0` compiles under typst 0.15 (no newer version available, cannot be version-bumped out of a break).
- Spot-audit `translator.py` for docutils 0.22 structural node changes (multi-`<term>` definition lists, `<reference>`-wrapped images inside `<figure>`). Integration-test check needed for multi-term lists; reference-wrapped figures traverse naturally (low risk).
- Verify no Sphinx 9 API breaks in builder/writer/translator/config-registration (expected: no breaks found, but re-verify against actual 9.x in CI).
- Fix black/ruff reformatting on 3 files already identified in PROJECT.md's CI failure evidence.

**Differentiators (nice-to-have, low cost):**
- Modernize `template_engine.py:239`'s deprecated `doctree.traverse()` → `doctree.findall()` for consistency with rest of codebase.
- Add regression test exercising the mitex construct that triggered `kai`.
- Refresh `README.md`/`docs/` example version strings once bumps are complete.

### Architecture Approach

Per ARCHITECTURE.md — **no architectural rewrite needed.** All layer boundaries (Builder → Writer → Translator → TemplateEngine → pdf.py) survive unchanged at the API-contract level. Sphinx 9's changelog audit found no breaking changes to `Builder` base class, `SphinxTranslator`, `add_config_value()`, or `typst.compile()` signature.

**Major components & impact summary:**
1. **`__init__.py` (setup/config-registration)** — `add_config_value()` signature unchanged; entry-point discovery mechanism unchanged. No code change needed.
2. **`builder.py` / builders** — `Builder` base-class methods unchanged in Sphinx 9. No code change needed.
3. **`writer.py`** — `Writer.translate()` contract unchanged; only the 4 hardcoded `#import "@preview/..."` lines need version strings updated (3-way sync hazard).
4. **`translator.py`** — `SphinxTranslator` base class stable; risk is emitted Typst syntax (if translator outputs any stdlib calls removed by typst 0.15, compilation will fail). Need empirical CI verification.
5. **`template_engine.py`** — `doctree.traverse()` call (line 239) is soft-deprecated but not yet removed; one of three hardcoded `@preview` version strings needs updating. Optional modernization: swap `traverse()` → `findall()`.
6. **`templates/base.typ`** — One of three hardcoded `@preview` version strings needs updating.
7. **`pdf.py`** — `typst.compile()` signature confirmed unchanged in typst-py 0.15.0.

**Integration risk:** The three-way version-sync hazard — because versions are duplicated across three files, editing all three to a wrong version will pass the sync test but fail compilation. Empirical `docs-pdf` verification is the critical gatekeeper.

### Critical Pitfalls

Per PITFALLS.md research, top 5 pitfalls to avoid:

1. **The `@preview` package trap** — bumping the wrong package or not confirming mutual compile-correctness (Pitfall 1)
   - *Avoid by:* Don't bump all four packages simultaneously. This research traced `kai` to **mitex** (v0.2.6+ fixes the deprecated `kai` symbol). Bump mitex first, verify with `docs-pdf`, then bump the others. If `kai` persists, bisect by reverting one package at a time.

2. **The Python-floor trap** — Sphinx 9 requires Python >=3.11/3.12, but typsphinx still declares floor as 3.10 (Pitfall 2)
   - *Avoid by:* Check Sphinx's PyPI `requires_python` metadata before raising the pin. Sphinx 9.0 = Python >=3.11; Sphinx 9.1 = Python >=3.12. Raise `requires-python`, drop py310/py311 from tox/CI/classifiers — all in the same commit as the sphinx bump.

3. **Removed/deprecated docutils APIs** — `doctree.traverse()` is soft-deprecated since docutils 0.18 (Pitfall 3)
   - *Avoid by:* Swap `traverse()` → `findall()` in `template_engine.py:239` as a preparatory commit. Re-scan for other raw-internals calls after pins are raised.

4. **Three-way (now N-way) `@preview` sync desync** — version-sync test proves agreement, not correctness (Pitfall 4)
   - *Avoid by:* Add empirical compile check (minimal `.typ` fixture exercising all four packages) run as required CI step. Also grep the whole repo for undocumented `@preview/` references.

5. **CI matrix and cross-OS gaps** — ceilings duplicated across 8 sites; `docs-pdf` only on Linux (Pitfall 5)
   - *Avoid by:* Use `grep` to enumerate all ceiling sites before starting the bump. Decide whether cross-OS PDF verification is in scope (typst 0.15 has font/text-shaping breaking changes).

## Implications for Roadmap

Based on research findings, suggested 5-phase structure (ordered by dependency):

### Phase A: Pin Raise + Python Floor Decision + Lockfile

**Rationale:** Must establish the Python floor and Sphinx-pin width *before* downstream phases — blocking scope decision.

**Delivers:** Decided Python floor (3.11 vs 3.12); updated all ceilings in `pyproject.toml` and `tox.ini` (8 sites total); updated CI matrix, classifiers, mypy/ruff/black target-version; regenerated `uv.lock`.

**Addresses:** Pitfalls 2, 5

**Expected state:** CI still red (PDF tests fail on `kai`). Goal is getting real stack installed so Phase B can diagnose.

**Research flags:** None — straightforward config. Re-verify PyPI metadata at execution time.

---

### Phase B: `@preview` Package Bump + 3-way Sync + Empirical Verification

**Rationale:** Depends on Phase A. Root-cause fix for `kai` and verification gate for mutual package compatibility.

**Delivers:** Bumped mitex 0.2.4→0.2.7, gentle-clues 1.2.0→1.3.1, codly-languages 0.1.1→0.1.10 (atomic commit); verified codly 1.3.0 compiles under typst 0.15+; updated version-sync test; confirmed `docs-pdf` builds clean (no `kai`).

**Addresses:** Pitfalls 1, 4

**Verification gate:** `test_preview_version_sync.py` passes AND `docs-pdf` succeeds. If `kai` persists, bisect per Pitfall 1.

**Research flags:**
- **MEDIUM confidence on mitex root-cause:** CHANGELOG.md claim is strong but unconfirmed. Mitex v0.2.6 should be the first hypothesis tested.
- **MEDIUM confidence on codly:1.3.0 compatibility:** Must empirically verify; no newer version fallback if it breaks.

---

### Phase C: Translator/Writer/API Fixes + Full Test Matrix

**Rationale:** Parallel-safe with Phase B for lint fixes (C1). C2 (full PDF integration) depends on Phase B's `kai`-free baseline.

**Delivers:** Fixed black/ruff/mypy reformatting; fixed docutils 0.22 multi-`<term>` edge case if found; verified non-PDF pytest suite green against Sphinx 9/docutils 0.22; optional `traverse()`→`findall()` modernization.

**Addresses:** Pitfall 3

**Research flags:** Sphinx 9 changelog audit found no API breaks, but re-verify empirically against actual resolved dependencies (runtime AttributeError/TypeError may surface).

---

### Phase D: Full CI Matrix Green + Docs PDF

**Rationale:** Verification-only. Depends on A+B+C. Ensures all lanes go green end-to-end.

**Delivers:** Observed 3-OS × Python matrix green; observed lint/type/coverage/docs jobs green; observed `docs.yml` PDF green; documented cross-OS PDF verification decision.

**Addresses:** Pitfall 5

**Research flags:** Decide explicitly whether cross-OS PDF verification is needed (typst 0.15 font/text-shaping changes may cause platform-specific regressions).

---

### Phase E: Guardrail Ceiling Sync + Version String Fix + Release

**Rationale:** Final cleanup. Depends on Phase D green.

**Delivers:** Synced dependent guard ceilings; fixed `__version__ = "0.4.3"` vs `pyproject.toml` `version = "0.4.4"` → both `"0.5.0"`; released via existing `release.yml`.

**Addresses:** None (housekeeping)

**Research flags:** None.

---

### Phase Ordering Rationale

- **A before B/C/D/E:** Python floor and Sphinx-pin decision gates everything (CI lanes must be valid).
- **B parallel-safe with C1:** Both depend only on A. C2 (PDF integration) depends on B.
- **D verifies A+B+C:** Confirmation phase; no shipping until all CI lanes green.
- **E depends on D:** Final release step.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| **Stack** | HIGH | Verified against PyPI JSON API — official registry metadata, no ambiguity. |
| **Features** | HIGH | Changelog verification + code inspection. Sphinx 9 changelog audit thorough; docutils 0.22 verified via source. |
| **Architecture** | HIGH | Sphinx 9.0 changelog found zero breaking changes to load-bearing APIs. All verified against official sources. |
| **Pitfalls** | MEDIUM | Mix of HIGH-confidence primary sources and MEDIUM-confidence inferred risks. **`kai` root-cause attribution to mitex** is MEDIUM — strong CHANGELOG evidence but not independently reproduced; empirical verification needed at Phase B. |

**Overall confidence:** **MEDIUM** (can proceed with roadmap phase planning; `kai` root-cause hypothesis is strong but must be empirically verified during Phase B).

### Gaps to Address

1. **`kai` root-cause empirical verification:** Mitex v0.2.6+ is the strongest hypothesis (CHANGELOG evidence), but not independently reproduced. Phase B must test this. If mitex alone doesn't fix it, bisect per Pitfall 1 recovery strategy.

2. **codly:1.3.0 typst-0.15 compatibility:** No newer version published (already at registry ceiling). No newer version means no bump fallback if it breaks. Phase B must empirically compile under typst 0.15. If it fails, immediate escalation (fork/patch/replace).

3. **Docutils 0.22 multi-`<term>` definition-list handling:** Spot-audit found potential edge case. Integration-test check recommended during Phase C but not strictly required; low risk.

4. **Cross-OS PDF compilation scope:** typst 0.15 has font/text-shaping breaking changes. Current CI only tests PDF on Linux. Should macOS/Windows verification be added? Explicit decision needed during Phase D.

5. **`drift.yml` required-check posture:** Currently advisory-only. Should it become required during the first weeks after v0.5.0 ships? Decision deferred to roadmap.

## Sources

### Primary (HIGH confidence)

- **PyPI JSON API** — official package metadata for Sphinx 9.0/9.1, docutils, typst (requires_python, requires_dist, versions)
- **Official Sphinx changelog** (`sphinx-doc.org/en/master/changes/9.0.html`) — incompatible changes, deprecated APIs
- **GitHub package registry** (`github.com/typst/packages/...`) — authoritative Typst Universe version listings
- **typsphinx source files** — direct inspection of builder.py, writer.py, translator.py, template_engine.py, tests/test_preview_version_sync.py

### Secondary (MEDIUM confidence)

- **mitex-rs/mitex CHANGELOG.md** — v0.2.6 release: "Fix: fix 'kai is deprecated' warning for Typst v0.14.0" (strong evidence, requires empirical verification)
- **Docutils Release Notes** — 0.22 API-removal history
- **Typst 0.15.0 changelog** — deprecation/removal summary

### Tertiary (LOW-MEDIUM confidence, needs validation)

- **Typst Universe web pages** — version/compatibility facts (noted cross-source disagreement in some cases; GitHub registry treated as ground truth)
- **gentle-clues, codly GitHub releases** — version history and dates

---

*Research completed: 2026-07-09*  
*Synthesized from: STACK.md, FEATURES.md, ARCHITECTURE.md, PITFALLS.md*  
*Ready for roadmap phase planning: yes (with noted MEDIUM-confidence gaps for empirical verification during Phase B)*
