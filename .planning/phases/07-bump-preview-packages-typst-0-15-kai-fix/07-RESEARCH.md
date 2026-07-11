# Phase 7: Bump @preview Packages + typst 0.15 (kai fix) - Research

**Researched:** 2026-07-11
**Domain:** Typst compiler / Typst Universe `@preview` package version compatibility (dependency forward-port, not new architecture)
**Confidence:** MEDIUM-HIGH — the root-cause mechanism is now directly confirmed via the mitex CHANGELOG (not just inferred), the exact registry ceilings for all four packages are directly verified against `typst/packages`, and the `typst-py` 0.15.0 pin resolves cleanly locally. The one remaining unknown — whether `codly 1.3.0` compiles cleanly under typst 0.15 with zero errors — is explicitly an empirical question that only the real `docs-pdf` compile (this phase's hard gate) can answer; no doc/changelog source states this affirmatively for 0.15.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: Verification gate = clean compile (hard gate) + a light human eyeball of the PDF.**
  The hard, blocking gate is "`docs-pdf` compiles with no `kai`/any `TypstError`". A quick visual
  glance at the generated PDF is layered on top — but it is a sanity glance, **not** an
  element-by-element visual audit. No automated visual-snapshot / golden-PDF infra is built
  (rejected as over-engineering for a maintenance cycle).
- **D-02: Accept the new appearance as the new baseline — as long as nothing is broken.**
  If a bumped package changes icons/colors/spacing/highlighting, **accept the new look**. Do NOT
  spend effort restoring the old (pre-bump) appearance via config/overrides/show-rules.
- **D-03: Judge the after-PDF standalone — no before/after comparison.**
  Do NOT compile a pre-bump "before" PDF (typst 0.14.9 + old packages) to diff against. Just inspect
  the post-bump PDF on its own.
- **D-04: Pass criterion = "no error glyphs / no obviously-broken output" ONLY.**
  The eyeball passes if the PDF has no blank/broken boxes, no missing-glyph tofu, no error glyphs.
  It does NOT require per-element verification (no fixed "admonition has icon+color / code is
  language-highlighted / math is typeset" checklist). The empirical `kai`-free compile is the real
  gate; the visual glance is only a coarse "nothing is visibly broken" backstop.

**Net effect for the planner:** the phase's done-ness gate is (a) `docs-pdf` compiles cleanly with
no `TypstError`, `test_preview_version_sync.py` green; plus (b) a quick "open the PDF, no tofu/broken
boxes" glance. Do not invest in visual baselines, before/after diffs, or restoring prior styling.

Locked scope anchors (carried forward from ROADMAP/REQUIREMENTS, not to be re-litigated):
- Exact versions locked: `mitex 0.2.4→0.2.7`, `gentle-clues 1.2.0→1.3.1`, `codly-languages 0.1.1→0.1.10`,
  `codly` stays `1.3.0`. `typst→>=0.15.0,<0.16` (FWD-02).
- Bisect contingency locked: if `kai` persists after the mitex bump, revert one package at a time.
  `codly 1.3.0` is the fallback suspect (registry ceiling → source-level workaround is the escalation
  path if it breaks).
- Branch strategy carried from Phase 6: all work stays on `release/v0.5.0`; `main` stays green
  throughout; merge to main only at milestone completion via GitHub PR.
- NOT this phase: `traverse()`→`findall()` + full-suite API compatibility is Phase 8 (API-*); the
  dedicated `typst compile` smoke test + drift/Dependabot ceiling bumps are Phase 9 (CI-02/CI-03).

### Claude's Discretion

- **Verification corpus / rigor:** Use the existing `tox -e docs-pdf` as the real compile gate.
  Confirmed (this research): the project's own `docs/` exercises all four packages — admonitions
  (`gentle-clues` via `.. note::` in `quickstart.rst` and `templates.rst`), math (`mitex` via
  `:math:` inline role and `.. math::` block in `examples/basic.rst`, with `typst_use_mitex = True`
  set in `docs/source/conf.py`), and code blocks (`codly`/`codly-languages` via `.. code-block::` —
  9+ occurrences across `quickstart.rst`, `examples/basic.rst`, `user_guide/*.rst`). Do NOT pull a
  dedicated all-4-package smoke fixture forward into Phase 7; that's Phase 9 (CI-02).
- **Bump strategy:** Default to bumping all four packages + typst together (atomic), bisect
  package-by-package only if `kai` (or another break) persists.
- **codly-break escalation:** source-level patch/vendoring → alternate code-highlighting path → pin
  typst to the highest 0.15.x codly tolerates. Only invoked if the empirical compile actually breaks
  on codly.

### Planner implementation note (not a user decision, carried into this research)

- `writer.py:96` / `template_engine.py:315` import mitex with a **named** surface —
  `#import "@preview/mitex:0.2.4": mi, mitex` — while `templates/base.typ:14` uses a glob
  `#import "@preview/mitex:0.2.4": *`. This research (see "mitex export-surface stability" below)
  confirms `mi` and `mitex` remain the documented export names in `0.2.7`, so the named import should
  continue to resolve — but this was verified via package documentation/README, not a byte-level
  diff of `lib.typ` across versions, so it stays `[CITED]` not `[VERIFIED]`. The real gate is still
  the empirical compile (a renamed export would surface as an `unknown import` `TypstError` at
  compile time, which the `docs-pdf` gate would catch).

### Deferred Ideas (OUT OF SCOPE)

- Automated visual-regression / golden-PDF baseline — rejected as over-engineering for this
  maintenance cycle.
- Dedicated all-4-package `typst compile` smoke fixture — already scheduled as Phase 9 (CI-02).
- CFG-01 (user-configurable `@preview` versions) and XOS-01 (cross-OS docs-PDF CI) — tracked in
  REQUIREMENTS.md v2, not in this milestone.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FWD-02 | `typst` re-pinned to `>=0.15.0,<0.16`; `typstpdf` builder compiles project docs to PDF under typst 0.15 with no `kai`-class error | `typst-py` 0.15.0 confirmed on PyPI and resolves cleanly via `uv pip install --dry-run` locally (VERIFIED, this session). `pyproject.toml:30` currently pins `typst>=0.14.1,<0.15` — exact edit site identified. Root-cause mechanism for `kai` confirmed via mitex CHANGELOG (see below) — bumping mitex to 0.2.7 (which incorporates 0.2.6's explicit `kai` fix) is the correct empirical fix, not just a plausible one. |
| PKG-01 | `mitex` bumped `0.2.4`→`0.2.7`, empirically resolving `unknown variable: kai` (confirmed by real compile, not changelog alone) | mitex's own CHANGELOG.md (fetched raw from `mitex-rs/mitex`) states verbatim for v0.2.6: *"fix 'kai is deprecated' warning for Typst v0.14.0"* (PR #201). This directly confirms `kai` originates from **mitex**, not `gentle-clues`/`codly` as PROJECT.md's context speculated ("likely gentle-clues:1.2.0 or codly") — see Assumptions Log A1 for the correction. 0.2.7 is one release past the fix, so it inherits it. The compile-gate requirement (not changelog alone) remains binding per PKG-01's own wording. |
| PKG-02 | `gentle-clues` (`1.2.0`→`1.3.1`) and `codly-languages` (`0.1.1`→`0.1.10`) bumped; `codly` `1.3.0` confirmed to compile under typst 0.15 (no newer version exists) | `gentle-clues` 1.3.1 confirmed to exist in the `typst/packages` registry (directory listing fetched); its CHANGELOG shows only additive changes (translations, quotation-handling fix) between 1.2.0 and 1.3.1 — no function-signature changes to `info()`/`warning()`/`tip()` (the functions `translator.py` calls). `codly-languages` 0.1.10 confirmed to exist in the registry (data-only package: language definitions, not API surface). `codly` confirmed capped at `1.3.0` in the `typst/packages` registry (no 1.3.1 or later exists there, despite an upstream GitHub tag suggesting otherwise — see Common Pitfalls). Whether `codly 1.3.0` actually compiles clean under typst 0.15 is **not resolvable from documentation** — no changelog or forum post states 0.15 compatibility either way. This is the phase's core empirical unknown; the `docs-pdf` compile gate is the only way to know. |
| PKG-03 | 3-way `@preview` version sync (`writer.py` / `template_engine.py` / `templates/base.typ`) updated in lockstep; `tests/test_preview_version_sync.py` passes | Exact current line contents for all three sync sites read directly from source (see "Code Examples" below) — the plan can give the executor literal before/after strings. `test_preview_version_sync.py` read in full: it does a **regex-based, order-independent set comparison** of `#import "@preview/<name>:<version>"` matches across the three files — it does not care about surrounding code, only that all three files declare the same version string for each of the four package names. This means the edit is purely "find every `@preview/<pkg>:<old-version>` string across all three files, replace with `<new-version>`" — no reordering or restructuring needed. |
</phase_requirements>

## Summary

This phase is a **version-bump forward-port**, not new architecture. The core finding of this research
directly upgrades the confidence of the milestone's central hypothesis: mitex's own CHANGELOG.md
(fetched raw from GitHub, not a secondhand summary) states that version **0.2.6** shipped a fix
literally titled *"fix 'kai is deprecated' warning for Typst v0.14.0"* (PR #201). This is
independent, first-party confirmation — not changelog inference filtered through search snippets —
that the `unknown variable: kai` `TypstError` under typst 0.15 originates from **mitex**, and that
bumping past 0.2.6 (the locked target is 0.2.7) is a directly-targeted fix, not a shot in the dark.
This also **corrects** a speculative claim in `PROJECT.md`'s "`kai` origin" note, which guessed
"likely `gentle-clues:1.2.0` or `codly`" — the evidence now points specifically to mitex. See
Assumptions Log A1.

All four target versions were independently verified to exist in the `typst/packages` registry
(the actual source Typst's compiler resolves `@preview/*` imports against): `mitex` 0.2.7,
`gentle-clues` 1.3.1, `codly-languages` 0.1.10, and — critically — `codly` is confirmed **capped at
1.3.0** in that registry (matching the locked decision that it's a registry ceiling, not an
oversight). `typst-py` 0.15.0 is confirmed published on PyPI and was confirmed, in this session, to
resolve cleanly via `uv pip install --dry-run "typst>=0.15.0,<0.16"` against this repo's environment.

None of `gentle-clues` 1.2.0→1.3.1 or `codly-languages` 0.1.1→0.1.10 show breaking API changes in
their changelogs — both ranges are purely additive (new translations, a quotation-handling fix in
gentle-clues; new language definitions in codly-languages), so the translator's calls to
`#info()[]`, `#warning()[]`, `#tip()[]`, etc. and the `#codly(languages: codly-languages)` call site
should keep working unchanged. `mitex`'s documented export surface (`mi`, `mitex`/`mimath`,
`mitext`, `mitex-convert`) is unchanged in 0.2.7 per its own README/Universe page, so the named
import (`mi, mitex`) in `writer.py`/`template_engine.py` should keep resolving.

The one genuinely open question — whether `codly 1.3.0` (frozen at the registry ceiling) compiles
cleanly under typst 0.15 — has **no documentary answer**. Nothing in codly's changelog, GitHub
issues, or the Typst forum confirms or denies 0.15 compatibility. This is exactly why the phase's
hard gate is a real `docs-pdf` compile, not changelog inference, and why the ROADMAP's bisect
contingency names codly as the fallback suspect.

**Primary recommendation:** Make the version bump edit as one atomic change across all four
locations (`pyproject.toml`, `writer.py`, `template_engine.py`, `templates/base.typ`), run
`uv sync` / `uv lock`, then run `tox -e docs-pdf` as the single empirical gate. If it fails with a
`kai`-class or other `TypstError`, bisect by reverting one package version at a time (mitex is
extremely unlikely to be the culprit given the direct changelog confirmation — start bisection with
codly, the named fallback suspect) until the compile succeeds, per the locked contingency.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Runtime dependency pin (`typst` / `typst-py`) | Build/Packaging (`pyproject.toml` + `uv.lock`) | — | Governs which typst compiler binary is installed; not a runtime code concern |
| `@preview` package version declaration | Generated-Output Layer (`writer.py`, `template_engine.py`, `templates/base.typ`) | — | These three Python/Typst sites literally emit the `#import "@preview/<pkg>:<version>"` strings into every generated `.typ` file; there is no other place these versions are declared |
| Version-sync invariant enforcement | Test Layer (`tests/test_preview_version_sync.py`) | CI (`ci.yml`) | Guards the three declaration sites against drift; runs as part of the normal pytest suite, no new test infra needed |
| Compile-correctness verification | Build/CI (`tox -e docs-pdf` → `sphinx-build -b typstpdf`) | Typst compiler (`typst-py` binding) | The only tier that can observe whether a given `@preview` version graph actually compiles under a given typst version — this is why it's the hard gate, not the sync test |
| Visual sanity check | Human (manual PDF eyeball) | — | Explicitly NOT automated per D-01; deliberately kept out of the CI/test tier per locked decisions |

## Standard Stack

### Core (version bump targets — all locked by REQUIREMENTS.md, not researcher discretion)

| Package | Current | Target | Registry-confirmed | Why this exact version |
|---------|---------|--------|---------------------|-------------------------|
| `typst` (PyPI, `typst-py` binding) | `>=0.14.1,<0.15` (resolves 0.14.9) | `>=0.15.0,<0.16` | [VERIFIED: PyPI + local `uv pip install --dry-run`] 0.15.0 exists on PyPI, published 2026-06-16; resolves cleanly against this repo's lockfile constraints (`uv pip install --dry-run "typst>=0.15.0,<0.16"` → `+ typst==0.15.0`, tested this session) | FWD-02 target compiler; typst 0.15.0 released June 15 2026 (variable font support, HTML export improvements) |
| `@preview/mitex` | `0.2.4` | `0.2.7` | [VERIFIED: typst/packages registry via GitHub] Directory listing confirms 0.2.7 exists | [CITED: raw `CHANGELOG.md`, mitex-rs/mitex] v0.2.6 (one release below target) explicitly fixes *"kai is deprecated" warning for Typst v0.14.0* (PR #201) — this is the direct root-cause fix for the `unknown variable: kai` break |
| `@preview/gentle-clues` | `1.2.0` | `1.3.1` | [VERIFIED: typst/packages registry] Directory listing confirms versions 1.2.0, 1.3.0, 1.3.1 all exist in sequence | [CITED: raw `CHANGELOG.md`, jomaway/typst-gentle-clues] Only additive changes in this range (Czech/Danish/Japanese translations, a quotation-handling fix "to work without typst's quote function") — no signature changes to `info()`/`warning()`/`tip()` |
| `@preview/codly-languages` | `0.1.1` | `0.1.10` | [VERIFIED: typst/packages registry] Directory listing confirms 0.1.0 through 0.1.10 all exist sequentially | [ASSUMED] Package is a language-definition data table consumed via `#codly(languages: codly-languages)`; no changelog was directly readable, but the package's narrow purpose (data-only) and 9 sequential patch bumps in the same `0.1.x` line suggest additive language-list growth, not API change. Not independently confirmed via changelog text — flagged in Assumptions Log A2. |
| `@preview/codly` | `1.3.0` | `1.3.0` (unchanged — registry ceiling) | [VERIFIED: typst/packages registry] Directory listing confirms `1.3.0` is the highest version present; no `1.3.1` or later exists in `typst/packages/preview/codly/` | Locked: stays at 1.3.0. **Note:** a WebFetch of the upstream `Dherse/codly` GitHub *releases* page surfaced a mention of a "1.3.1" tag/release — but the authoritative Typst Universe registry (`typst/packages`, what the compiler actually resolves `@preview/codly:X` against) does NOT have 1.3.1 published. Treat the registry listing as ground truth; see Common Pitfalls. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Bumping mitex to 0.2.7 | Pinning at 0.2.6 (the exact fix commit) | REQUIREMENTS.md/ROADMAP lock 0.2.7 specifically — not researcher discretion. 0.2.7 is strictly newer and includes the 0.2.6 fix plus additive features (color-related optional args, `\smash` command), so no regression risk from taking the extra point release. |
| Accepting codly 1.3.0 as-is | Vendoring/patching codly source if it breaks under 0.15 | Locked escalation ladder (source-patch → alternate highlighter → pin typst to highest-tolerant 0.15.x) only triggers if the empirical compile fails — do not preemptively patch. |

**Installation (no code install needed — these are Typst Universe `@preview` packages resolved at
compile time by the `typst` compiler itself, not via `pip`/`uv`; only the `typst` PyPI package needs
a dependency-manager bump):**

```bash
# Edit pyproject.toml: "typst>=0.14.1,<0.15" -> "typst>=0.15.0,<0.16"
uv lock
uv sync --locked
```

**Version verification (already performed this session):**
```bash
uv pip install --dry-run "typst>=0.15.0,<0.16"
# Resolved 1 package in 249ms
# Would uninstall 1 package: - typst==0.14.9
# Would install 1 package:   + typst==0.15.0
```

## Package Legitimacy Audit

The four `@preview` packages are Typst Universe packages, not npm/PyPI packages — they are not
installed via a package manager and the `package-legitimacy check` seam's ecosystem support
(`npm|pypi|crates`) does not cover the Typst Universe registry directly. Legitimacy for these four
was instead established by directly querying the authoritative `typst/packages` GitHub registry
(the actual source the `typst` compiler resolves `@preview/*` imports against) — see the version
tables above, all four packages and their target versions are independently confirmed to exist
there, and all four are already-adopted, long-standing dependencies of this project (not new
additions), so slopsquatting risk is not applicable.

The one PyPI package this phase touches is `typst` (the `typst-py` binding), already a direct
dependency since Phase 1 of this project — this bump is a version-range change, not a new
dependency. Ran the legitimacy seam on it for completeness:

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|--------------|---------|-------------|
| `typst` (typst-py) | PyPI | Package itself: multi-year (already a project dependency since Phase 1); specific `0.15.0` release: ~1 month old at research time (published 2026-06-16) | not reported by seam (`weeklyDownloads: null`) | `github.com/messense/typst-py` | `SUS` (reasons: `too-new`, `unknown-downloads`) | **Approved with context** — the "too-new"/"unknown-downloads" signals reflect the specific 0.15.0 *release* recency, not the package's trustworthiness; `messense/typst-py` is the same repo this project has depended on since inception, and the version bump is locked by FWD-02/REQUIREMENTS.md, not a new-package decision. No `checkpoint:human-verify` needed for package *identity*, but the planner SHOULD still gate the typst 0.15.0 upgrade behind the empirical `docs-pdf` compile (already the phase's hard gate) since "too-new" is exactly the risk profile that justifies not trusting changelog claims alone. |

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** `typst` (typst-py) — flagged only on release-recency grounds, not identity/trust; already mitigated by this phase's existing empirical-compile-gate design. No additional checkpoint needed beyond the phase's own success criteria.

## Architecture Patterns

### System Architecture Diagram

```
docs/source/*.rst (admonitions, :math:/.. math::, .. code-block::)
        │
        ▼
Sphinx doctree  ──►  TypstTranslator (translator.py)
                         │  converts admonition/math/code nodes to
                         │  #info()/#warning()/#tip() , mitex calls,
                         │  codly-wrapped code fences
                         ▼
                   TypstWriter.translate() (writer.py)
                         │
              ┌──────────┴──────────┐
              │                     │
       is_master_document?    included document?
              │                     │
              ▼                     ▼
   TemplateEngine (template_engine.py)   writer.py inline imports
   emits #import "@preview/<pkg>:<ver>"  emits #import "@preview/<pkg>:<ver>"
   x4 (codly/codly-languages/mitex/      x4 (same four, no template)
   gentle-clues) + template.typ
              │                     │
              └──────────┬──────────┘
                         ▼
                 .typ file(s) written to build dir
                         │
                         ▼
              typst-py compiler (PyPI `typst` package)
              resolves @preview/<pkg>:<ver> against the
              Typst Universe registry (typst/packages) at
              compile time — THIS is where a version/compiler
              mismatch surfaces as `unknown variable: kai` or
              any other TypstError
                         │
                         ▼
                    compiled PDF  ◄── docs-pdf gate (tox -e docs-pdf)
                                       + test_preview_version_sync.py
                                       (checks the 3 declaration sites
                                       agree — does NOT check compile
                                       correctness)
```

### Recommended Project Structure

No new files or directories are needed — this phase edits four existing files in place:

```
pyproject.toml                          # typst PyPI pin: >=0.14.1,<0.15 -> >=0.15.0,<0.16
typsphinx/writer.py                     # ~line 94-97: 4x @preview import strings (included docs)
typsphinx/template_engine.py            # ~line 313-316: 4x @preview import strings (master docs)
typsphinx/templates/base.typ            # ~line 8-19: 4x @preview import strings (default template)
uv.lock                                 # regenerated via `uv lock` after the pyproject.toml edit
```

### Pattern: Lockstep version-string replacement (the only pattern this phase needs)

**What:** All four `@preview` version bumps are literal string replacements of the form
`@preview/<pkg>:<old-version>` → `@preview/<pkg>:<new-version>`, applied identically across three
files. There is no code-structure change — the surrounding import/init logic (codly-init, codly
config call) does not change.

**When to use:** Every one of the three sync sites, every one of the four packages (three of which
change version; `codly` stays `1.3.0` and its import line is untouched).

**Example — current state (verified by direct read this session):**
```python
# typsphinx/writer.py:94-97 (included-document import block)
imports.append('#import "@preview/codly:1.3.0": *')
imports.append('#import "@preview/codly-languages:0.1.1": *')
imports.append('#import "@preview/mitex:0.2.4": mi, mitex')
imports.append('#import "@preview/gentle-clues:1.2.0": *')
```
```python
# typsphinx/template_engine.py:313-316 (master-document import block)
output_parts.append('#import "@preview/codly:1.3.0": *')
output_parts.append('#import "@preview/codly-languages:0.1.1": *')
output_parts.append('#import "@preview/mitex:0.2.4": mi, mitex')
output_parts.append('#import "@preview/gentle-clues:1.2.0": *')
```
```typst
// typsphinx/templates/base.typ:8-19 (default template)
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.1": *
#import "@preview/mitex:0.2.4": *
#import "@preview/gentle-clues:1.2.0": *
```

**Target state (after the bump — literal strings for the executor):**
```
"@preview/codly:1.3.0"              -> unchanged (all 3 sites)
"@preview/codly-languages:0.1.1"    -> "@preview/codly-languages:0.1.10" (all 3 sites)
"@preview/mitex:0.2.4"              -> "@preview/mitex:0.2.7" (all 3 sites)
"@preview/gentle-clues:1.2.0"       -> "@preview/gentle-clues:1.3.1" (all 3 sites)
```

Note `base.typ`'s mitex import is a glob (`: *`) while `writer.py`/`template_engine.py` use the
named form (`: mi, mitex`) — only the version string changes in all three; the import *style*
(glob vs. named) is not part of this phase's scope and should not be touched (no evidence either
style is broken, and changing it is an unrelated refactor).

### Anti-Patterns to Avoid

- **Editing only one or two of the three sync sites:** `test_preview_version_sync.py` will catch
  this (it fails loudly on any single-package, single-file divergence), but don't rely on the test
  to catch it after the fact — grep for all four package name/version pairs across all three files
  as a self-check before considering the edit done.
- **Trusting the sync test as proof the compile works:** it only proves the three files *agree* with
  each other; it says nothing about whether the agreed-upon version actually compiles under typst
  0.15. The `docs-pdf` compile is the only source of truth for that (per D-01 and PKG-02's own
  wording).
- **Restoring old visual appearance via show-rules/config overrides if the bumped packages change
  rendering:** explicitly rejected by D-02. If `gentle-clues 1.3.1`'s quotation-handling change or
  any other cosmetic diff appears, accept it as the new baseline.
- **Building a before/after visual diff:** explicitly rejected by D-03. Do not compile a
  typst-0.14.9 "before" PDF for comparison.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| Verifying the `@preview` version bump actually compiles | A custom typst-compile smoke script/fixture scoped to just this phase | The existing `tox -e docs-pdf` env (`sphinx-build -b typstpdf source _build/pdf` from `docs/`) | Already exists, already exercises all four packages end-to-end (admonitions/math/code confirmed present in `docs/source/`), and is exactly the "real compile, not changelog inference" gate PKG-01/PKG-02 require. A dedicated smoke fixture is explicitly Phase 9's job (CI-02), not this phase's. |
| Detecting 3-way version desync | Hand-written grep/diff script in the plan | The existing `tests/test_preview_version_sync.py` (already in the suite, runs under normal `pytest`) | Already implements exactly the check needed (regex-extracts `@preview/<name>:<version>` from all three files, asserts set-equality per package) — re-implementing this in the plan would be pure duplication. |
| Visual verification of PDF output | Automated screenshot/pixel-diff tooling | A manual human PDF-open glance (D-01/D-04) | Explicitly rejected by the user as over-engineering for this maintenance cycle; building it now would violate the locked decision. |

**Key insight:** This phase has essentially zero net-new engineering surface — every piece of
infrastructure needed to both make and verify the change (the three declaration sites, the sync
test, the compile gate) already exists in the codebase. The work is a disciplined, literal
string-replacement across four files plus running the existing gates.

## Common Pitfalls

### Pitfall 1: Trusting a GitHub *releases* page over the Typst Universe registry for version ceilings
**What goes wrong:** A WebFetch of `github.com/Dherse/codly/releases` surfaced language suggesting a
"1.3.1" release exists for codly. If taken at face value, a planner might assume codly has a newer
version available and either try to bump past 1.3.0 or get confused about why `uv`/typst can't find
it.
**Why it happens:** The upstream *source* repository's release/tag history is not the same thing as
what's actually published to the Typst Universe package registry (`typst/packages` on GitHub, which
is what `typst.app/universe` and the compiler's `@preview` resolution both read from). A maintainer
can tag a GitHub release without submitting the corresponding PR to `typst/packages`.
**How to avoid:** Directorylisting-verified (this session) that `typst/packages/packages/preview/codly/`
only contains up to `1.3.0` — no `1.3.1` directory exists there. Always check the registry
(`github.com/typst/packages/tree/main/packages/preview/<name>`), not the upstream project's own
release page, when determining what version string is actually resolvable via `@preview/<name>:X`.
**Warning signs:** Any research claim about `@preview` package version availability that cites the
package's own GitHub repo/releases page instead of `typst/packages`.

### Pitfall 2: Assuming `test_preview_version_sync.py` passing means the compile will succeed
**What goes wrong:** After editing all three files with matching version strings, the sync test goes
green — but the `docs-pdf` compile still fails (e.g., because `codly 1.3.0` genuinely doesn't work
under typst 0.15, or an unrelated typst 0.15 syntax break surfaces).
**Why it happens:** The sync test is a pure string-equality check across three files; it has zero
awareness of the typst compiler or the Typst Universe registry. It was explicitly designed (per its
own docstring) to catch *desync*, not compile-correctness.
**How to avoid:** Always run `tox -e docs-pdf` (or `sphinx-build -b typstpdf source _build/pdf` from
`docs/`) as a separate, mandatory step after the sync test passes — never treat sync-test-green as
sufficient completion evidence for PKG-01/PKG-02.
**Warning signs:** A plan or verification step that only runs `pytest tests/test_preview_version_sync.py`
and calls the phase done.

### Pitfall 3: The named mitex import (`mi, mitex`) silently breaking on an export rename
**What goes wrong:** If a future mitex release renamed or removed the `mi`/`mitex` export names, the
version-sync test would still pass (it only compares version *strings*), but `writer.py`/
`template_engine.py`'s named import would fail to resolve, while `base.typ`'s glob import (`: *`)
would keep working — producing an inconsistent, confusing failure that only manifests for included
(non-master) documents.
**Why it happens:** The 3-way sync test's scope is deliberately narrow (version-string agreement
only); it was never designed to validate export-surface compatibility.
**How to avoid:** For *this* bump (0.2.4→0.2.7), the risk is empirically low — mitex's README and
Typst Universe page both document `mi`, `mitex`/`mimath`, `mitext`, `mitex-convert` as the current
exports for 0.2.7, unchanged from what `mi, mitex` expects [CITED, not independently diffed against
the WASM/lib.typ source — see Assumptions Log A3]. The `docs-pdf` compile — which exercises the
`:math:`/`.. math::` roles in `examples/basic.rst` via the included-document path — will surface an
`unknown import`-class `TypstError` at compile time if this assumption is wrong, so the existing gate
already covers this failure mode; no extra verification step is needed beyond running the full
`docs-pdf` compile (not just spot-checking the master document).
**Warning signs:** A `TypstError` mentioning `mi` or `mitex` as an unresolved identifier, specifically
localized to non-master (`#include`d) documents rather than the top-level document.

### Pitfall 4: Bisecting all four packages at once when only one is suspect
**What goes wrong:** If `docs-pdf` fails after the atomic 4-package bump, reverting all four to their
old versions to "start clean" wastes cycles — three of the four bumps (gentle-clues, codly-languages,
mitex) have strong changelog evidence of being safe or directly fix-bearing; only codly is genuinely
unverified for 0.15.
**Why it happens:** "Bisect by reverting one package at a time" (the locked contingency) can be
mis-read as "try all combinations" rather than "start with the named fallback suspect."
**How to avoid:** Per the locked contingency and this research's findings, if the compile fails,
first isolate whether `codly 1.3.0` is the failure by temporarily reverting *only* codly's
consuming logic — but codly has no fallback version to revert *to* (it's already at both the old
and new target version, `1.3.0` — there is no version bump to undo for codly specifically). "Bisect"
here more precisely means: temporarily revert `mitex`/`gentle-clues`/`codly-languages` one at a time
back to their pre-bump versions while keeping typst at 0.15, to determine whether the failure is
actually typst-0.15-vs-codly (unrelated to any of the three genuine bumps) or a regression
introduced by one of the three bumped packages themselves.
**Warning signs:** Spending bisection effort reverting `gentle-clues`/`codly-languages`/`mitex` before
first confirming (via the `TypstError` message itself) which package's `@preview` symbol is actually
implicated — the error message will almost always name the failing package directly (as it did for
`kai`/mitex originally).

## Code Examples

Verified patterns from direct source reads (this session) and CHANGELOG sources:

### Current three-way declaration sites (before state, verified by Read this session)
```python
# typsphinx/writer.py:94-97
imports.append('#import "@preview/codly:1.3.0": *')
imports.append('#import "@preview/codly-languages:0.1.1": *')
imports.append('#import "@preview/mitex:0.2.4": mi, mitex')
imports.append('#import "@preview/gentle-clues:1.2.0": *')
```
```python
# typsphinx/template_engine.py:313-316
output_parts.append('#import "@preview/codly:1.3.0": *')
output_parts.append('#import "@preview/codly-languages:0.1.1": *')
output_parts.append('#import "@preview/mitex:0.2.4": mi, mitex')
output_parts.append('#import "@preview/gentle-clues:1.2.0": *')
```
```typst
// typsphinx/templates/base.typ:8-19 (mitex glob-imports, unlike the other two files)
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.1": *
#import "@preview/mitex:0.2.4": *
#import "@preview/gentle-clues:1.2.0": *
```

### `pyproject.toml` typst dependency pin (before state, verified by grep this session)
```toml
# pyproject.toml:30 (dependencies list)
"typst>=0.14.1,<0.15",
```
Target: `"typst>=0.15.0,<0.16",`

### The compile gate (`tox.ini`, verified by Read this session)
```ini
[testenv:docs-pdf]
description = Build PDF documentation with typstpdf
runner = uv-venv-lock-runner
extras = docs
changedir = docs
commands =
    sphinx-build -b typstpdf source _build/pdf
```

### `test_preview_version_sync.py`'s actual check (verified by full Read this session)
The test extracts every `#import "@preview/<name>:<version>"` match via regex from all three files,
builds a `{filename: {package: version}}` map, then asserts that for every package name, all three
files report the same version string. A second test (`test_all_four_packages_declared`) guards
against an empty-set false pass by asserting all four expected package names (`codly`,
`codly-languages`, `mitex`, `gentle-clues`) are present in every file. Both tests are pure static
analysis — no typst compiler invocation.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|-------------------|---------------|--------|
| `typst==0.14.9` + `mitex==0.2.4` (Phase 6 known-good, pre-existing) | `typst>=0.15.0,<0.16` + `mitex==0.2.7` | This phase (2026-07, targeting typst 0.15.0 released 2026-06-15) | Unblocks the `docs-pdf`/PDF-integration CI lanes that Phase 6 intentionally left red; typst 0.15 brings variable font support and HTML export improvements per its official changelog (not otherwise load-bearing for this phase) |
| mitex 0.2.4–0.2.5 (pre-fix) | mitex 0.2.6+ (post-fix) | mitex PR #201 | Removes the `kai is deprecated` warning path that becomes a hard `unknown variable: kai` error once typst 0.15 actually removes the deprecated symbol mitex was still referencing |

**Deprecated/outdated:**
- `typst<0.15` ceiling in `pyproject.toml` — was a Phase-1/v0.4.4-era precautionary pin to escape the
  original `kai` break by reverting the compiler rather than fixing the package incompatibility;
  this phase replaces that workaround with the actual forward fix.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|----------------|
| A1 | `PROJECT.md`'s "`kai` origin" note speculated the symbol came from "likely `gentle-clues:1.2.0` or `codly`" — this research's direct mitex-CHANGELOG read instead attributes it to mitex (PR #201, v0.2.6, explicitly titled "fix 'kai is deprecated' warning for Typst v0.14.0"). This is presented as the more-likely-correct account because it is a first-party, named, PR-linked changelog entry rather than a guess, but it has NOT been independently reproduced by actually compiling mitex 0.2.4 under typst 0.15 and observing the exact `kai` error text match. | Summary, Phase Requirements (PKG-01) | Low-medium: if the CHANGELOG entry is coincidental (i.e., some *other* symbol also named/related to `kai` exists in gentle-clues/codly and the mitex fix is unrelated), the mitex bump alone would not resolve the compile error, and the bisect contingency would need to escalate to gentle-clues/codly investigation sooner than expected. The empirical `docs-pdf` compile gate catches this regardless — it does not depend on this attribution being correct, it just informs which package to suspect first during bisection. |
| A2 | `codly-languages` 0.1.1→0.1.10 changes are additive (language-definition data growth only, no API/structure change to the `languages` value consumed by `#codly(languages: codly-languages)`) | Standard Stack table | Low: `codly-languages` is a narrow, single-purpose data package (maps language identifiers to syntax-highlighting definitions); even if the internal structure changed, `codly`'s own `1.3.0` API (unchanged) is what defines the expected shape, and any incompatibility would surface immediately as a `TypstError` at the `docs-pdf` compile gate. |
| A3 | mitex 0.2.7's exported symbol names (`mi`, `mitex`, `mimath`, `mitext`, `mitex-convert`) are unchanged from what `writer.py`/`template_engine.py`'s named import (`: mi, mitex`) expects | Standard Stack, Common Pitfalls #3 | Medium if wrong, but self-detecting: an export rename would cause an immediate `TypstError` (unresolved import) at the `docs-pdf` compile gate, specifically on included (non-master) documents. This was verified via package documentation (README/Universe page text), not a line-level diff of the package's `lib.typ` source across 0.2.4→0.2.7, so it is `[CITED]` confidence, not `[VERIFIED]`. |
| A4 | codly-languages `0.1.10`'s `typst.toml` does not declare a `min-version`/compiler ceiling that would exclude typst 0.15 | Standard Stack table | Low: the `typst.toml` fetch for 0.1.10 succeeded and showed only name/entrypoint/author/license fields with no visible compiler-version constraint field, but this was not exhaustively cross-checked against every field the `typst.toml` schema supports. If a hidden ceiling exists, it would surface as an immediate resolution-time error (package not compatible with compiler), not a subtle runtime bug — again self-detecting at the `docs-pdf` gate. |

**If this table is empty:** N/A — see rows above. All four entries are self-detecting failure modes
covered by the phase's own hard gate (`docs-pdf` compile), which is why none of them block planning:
the plan should proceed with the locked version bumps and rely on the compile gate to surface any of
these assumptions being wrong, per the bisect contingency already locked in ROADMAP/CONTEXT.

## Open Questions

1. **Does `codly 1.3.0` actually compile clean under typst 0.15?**
   - What we know: `codly 1.3.0`'s `typst.toml` declares a `min-version` of `0.12.0` (no upper
     ceiling found), and it is the highest version available in the Typst Universe registry — there
     is no newer version to bump to even if it does break.
   - What's unclear: No changelog entry, GitHub issue, or forum post confirms or denies compatibility
     with typst 0.15 specifically (the most recent forum/changelog chatter found references typst
     0.13).
   - Recommendation: This is precisely why PKG-02 requires empirical confirmation, not changelog
     inference. Run the `docs-pdf` compile; if it fails on a codly-attributable error, follow the
     locked escalation ladder (source-level patch/vendor → alternate highlighting path → pin typst to
     the highest 0.15.x codly tolerates). Do not attempt to pre-emptively patch codly before the
     compile is actually observed to fail.

2. **Will the typst 0.15 migration guide's documented breaking changes (backslash path separators,
   stricter `array.slice`/`str`/`text.features` validation, renamed CSL citation styles) affect any
   `.rst`-sourced content or the `base.typ` template?**
   - What we know: The official typst 0.15 changelog documents these as the compiler's own breaking
     changes (independent of the four `@preview` packages).
   - What's unclear: Whether typsphinx's translator/template emits any Windows-style backslash paths,
     unusual `str`/`array.slice` calls, or citation-style-specific Typst syntax that would trip these
     validations. A source grep for backslash-containing path literals in `templates/base.typ` and
     `template_engine.py`'s image/asset path handling was not performed in this research pass (it
     falls slightly outside the four-package/typst-pin scope this research prioritized, per the
     research questions supplied).
   - Recommendation: The `docs-pdf` compile gate will surface any of these as a `TypstError` too
     (they are unrelated to `kai` but equally block the "zero `TypstError`" success criterion). If
     the compile fails on one of these instead of/in addition to a `@preview`-package issue, the
     plan should treat it as an in-scope FWD-02 fix (the success criterion is "no `unknown variable:
     kai` (or any other) `TypstError`" — explicitly not limited to `kai` alone).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|--------------|-----------|---------|----------|
| `typst` (PyPI binding) | Compile gate (`docs-pdf`) | ✓ (currently 0.14.9; confirmed 0.15.0 resolves via dry-run) | 0.14.9 → will become 0.15.0 after this phase's `pyproject.toml`/`uv.lock` edit | — |
| `uv` | Dependency resolution/lock regeneration | ✓ | (already the project's package manager per CLAUDE.md) | — |
| `tox` / `tox-uv` | Running `docs-pdf` env | ✓ (per CLAUDE.md, already the project's task runner) | — | — |
| Network access to Typst Universe registry (`packages.typst.org` / bundled cache) | `typst` compiler resolving `@preview/*` imports at compile time | Not directly probed this session (no `typst` CLI invocation was run); `typst-py`'s compile call will need to either fetch packages from the Typst Universe registry on first use or use a local package cache | Unknown — see note | If the compile environment lacks network access, `typst-py` may fail to download `@preview` packages; this is an existing behavior unrelated to this phase's version bump (Phase 6 already relies on the same package-resolution mechanism for the currently-pinned versions), so it is not treated as a new risk introduced by this phase. |

**Missing dependencies with no fallback:** none identified beyond the standing (pre-existing,
not phase-specific) Typst Universe network-access dependency noted above.

**Missing dependencies with fallback:** none.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (existing suite, ~400 tests per PROJECT.md) + tox-driven Typst compile (`sphinx-build -b typstpdf`) |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`), `tox.ini` (`[testenv:docs-pdf]`) |
| Quick run command | `pytest tests/test_preview_version_sync.py -x` |
| Full suite command | `tox -e docs-pdf` (real compile) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|--------------|
| FWD-02 | `typst` pin raised, `docs-pdf` compiles with zero `TypstError` | integration/compile | `tox -e docs-pdf` (equivalently `cd docs && sphinx-build -b typstpdf source _build/pdf`) | ✅ exists (`tox.ini:61-67`) |
| PKG-01 | mitex bump resolves `kai` empirically | integration/compile | same `tox -e docs-pdf` — the `docs/source/examples/basic.rst` `:math:`/`.. math::` content exercises mitex's code path | ✅ exists |
| PKG-02 | gentle-clues/codly-languages bump + codly 1.3.0 compiles | integration/compile | same `tox -e docs-pdf` — `.. note::` admonitions (`quickstart.rst`, `templates.rst`) exercise gentle-clues; `.. code-block::` blocks (9+ occurrences across docs) exercise codly/codly-languages | ✅ exists |
| PKG-03 | 3-way version sync agrees | unit/static | `pytest tests/test_preview_version_sync.py -x` | ✅ exists (`tests/test_preview_version_sync.py`) |

### Sampling Rate
- **Per task commit:** `pytest tests/test_preview_version_sync.py -x` (fast, seconds — run after each
  of the four-file edits to catch a partial/mistyped version bump immediately)
- **Per wave merge / phase gate:** `tox -e docs-pdf` (the real compile — this is the phase's actual
  hard gate; must be green, with the output PDF manually opened for the D-01/D-04 coarse visual
  glance, before the phase is considered done)

### Wave 0 Gaps

None — existing test infrastructure (`tests/test_preview_version_sync.py`, `tox -e docs-pdf`) fully
covers all three phase requirements' verification needs. No new test files, fixtures, or framework
installation are needed for this phase.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|----------------|---------|--------------------|
| V2 Authentication | No | Not applicable — this phase touches build/dependency configuration only, no auth surface |
| V3 Session Management | No | Not applicable |
| V4 Access Control | No | Not applicable |
| V5 Input Validation | No | No new user-facing input handling introduced; the translator's admonition/math/code conversion logic is unchanged by this phase (only the version strings it emits change) |
| V6 Cryptography | No | Not applicable |
| V14 Configuration (supply chain / dependency integrity) | Yes | Pin exact version ranges (already the project convention per `pyproject.toml`'s existing `>=X,<Y` guard-ceiling pattern, per PROJECT.md's Key Decisions table); verify package existence against the authoritative registry before pinning (performed in this research — all four `@preview` targets + `typst-py` 0.15.0 confirmed to exist); regenerate and commit `uv.lock` so the resolved dependency graph is reproducible (existing `PIN-03`-style convention, carried forward from Phase 6) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|-----------------------|
| Typo-squatted or malicious `@preview` package substituted for the intended one | Tampering / Spoofing | Typst Universe package names are content-addressed by name+version in the compiler's own cache; this phase only changes *version strings* for four already-vetted, already-adopted package *names* — no new package names are introduced, so typosquatting risk is not newly created by this phase. The existing `test_preview_version_sync.py` incidentally also guards against a stray typo in a package *name* across the three sync sites (via its `test_all_four_packages_declared` check). |
| Supply-chain drift (an unpinned or loosely-pinned dependency silently resolving to a compromised/broken future version) | Tampering | This project already follows a `>=floor,<next-major` guard-ceiling convention (per PROJECT.md's Key Decisions) — the `typst` PyPI pin bump in this phase (`>=0.15.0,<0.16`) follows that same established pattern; no bare `>=` floor is introduced. |

## Sources

### Primary (HIGH confidence)
- Direct `Read` of `typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ`, `pyproject.toml`, `tox.ini`, `tests/test_preview_version_sync.py` (this session) — exact current line contents and test logic
- `uv pip install --dry-run "typst>=0.15.0,<0.16"` (this session, local execution) — confirms typst-py 0.15.0 resolves cleanly
- `github.com/typst/packages/tree/main/packages/preview/{mitex,gentle-clues,codly-languages,codly}` (directory listings fetched this session) — authoritative registry version-existence confirmation for all four packages, including confirming codly's ceiling at 1.3.0

### Secondary (MEDIUM confidence)
- `raw.githubusercontent.com/mitex-rs/mitex/main/CHANGELOG.md` — direct fetch of mitex's own changelog; the "kai is deprecated" fix entry for v0.2.6 (PR #201) is the strongest single piece of evidence in this research
- `raw.githubusercontent.com/jomaway/typst-gentle-clues/main/CHANGELOG.md` — direct fetch confirming 1.2.0→1.3.1 is additive-only
- mitex README / Typst Universe package page (via WebSearch summaries, not a raw fetch of `lib.typ`) — export-surface names (`mi`, `mitex`, `mimath`, `mitext`, `mitex-convert`) for 0.2.7

### Tertiary (LOW confidence)
- WebFetch summary of `github.com/Dherse/codly/releases` — surfaced a misleading "1.3.1" mention that the authoritative registry check (Primary sources) directly contradicts; retained in this document only as a documented pitfall (Common Pitfalls #1), not as a version-availability claim
- WebSearch results on general codly/typst-0.15 compatibility — no direct confirmation found either way; documented as Open Question 1

## Metadata

**Confidence breakdown:**
- Standard stack (exact versions to bump to): HIGH — all four target versions independently confirmed to exist in the authoritative Typst Universe registry, plus `typst-py` 0.15.0 confirmed on PyPI and resolves locally
- `kai` root-cause attribution: MEDIUM-HIGH — upgraded from the incoming MEDIUM (changelog-based, not independently reproduced per STATE.md) by this session's direct-fetch confirmation of the exact mitex PR/changelog entry; still not independently reproduced by an actual compile (that remains this phase's own job)
- codly 1.3.0 / typst 0.15 compatibility: LOW — genuinely unknown from documentation; this is by design the phase's core empirical question, not a research gap
- Architecture / edit sites: HIGH — all three sync-site line numbers and exact current strings verified by direct file reads this session
- Pitfalls: MEDIUM-HIGH — grounded in direct registry/changelog fetches, with the GitHub-releases-vs-registry discrepancy itself surfaced as a first-order finding

**Research date:** 2026-07-11
**Valid until:** ~14 days (fast-moving: Typst Universe package versions and the typst compiler itself
are actively released; re-verify exact version numbers if planning is delayed materially past this
window)
