# Phase 7: Bump @preview Packages + typst 0.15 (kai fix) - Context

**Gathered:** 2026-07-11
**Status:** Ready for planning

<domain>
## Phase Boundary

The empirical root-cause fix and **highest-risk gate** of the v0.5.0 milestone. This phase:

- Raises `typst` to `>=0.15.0,<0.16` (dropping the `<0.15` ceiling).
- Bumps the four bundled `@preview` packages **in lockstep**: `mitex 0.2.4→0.2.7`,
  `gentle-clues 1.2.0→1.3.1`, `codly-languages 0.1.1→0.1.10`. `codly` stays `1.3.0`
  (registry ceiling — no newer version exists).
- Updates the 3-way version-sync (`writer.py` / `template_engine.py` / `templates/base.typ`)
  so `tests/test_preview_version_sync.py` passes.
- Verifies empirically that `docs-pdf` compiles to PDF with **zero `unknown variable: kai`
  (or any other) `TypstError`** — via a real compile, not changelog inference.

Requirements covered: **FWD-02, PKG-01, PKG-02, PKG-03**.

**Locked scope anchors (carried forward — do NOT re-litigate):**
- **Exact versions are locked** in REQUIREMENTS.md (PKG-01/02): mitex→0.2.7, gentle-clues→1.3.1,
  codly-languages→0.1.10, codly stays 1.3.0. typst→`>=0.15.0,<0.16` (FWD-02).
- **bisect contingency is locked** (ROADMAP): if `kai` persists after the mitex bump, revert one
  package at a time. `codly 1.3.0` is the fallback suspect (registry ceiling → source-level
  workaround/patch/replacement is the escalation path if it breaks).
- **Branch strategy carried from Phase 6** (06-CONTEXT.md D-01/D-02): all work stays on
  `release/v0.5.0`; `main` stays green throughout; merge to main only at milestone completion
  via GitHub PR. The intentionally-red PDF/`docs-pdf` lanes turn green **here** when this fix lands.
- **NOT this phase:** `traverse()`→`findall()` + full-suite API compatibility is Phase 8 (API-*);
  the dedicated `typst compile` smoke test + drift/Dependabot ceiling bumps are Phase 9 (CI-02/CI-03).

</domain>

<decisions>
## Implementation Decisions

### Visual Regression Tolerance (the area discussed)

The package bumps (esp. `gentle-clues 1.2→1.3`, `codly-languages 0.1.1→0.1.10`) may change how
admonitions / code / math *render* even when they compile clean. The user set a deliberately
**lightweight, forward-port stance** (this is a forward-port, not a redesign; no golden-PDF
baseline infra exists):

- **D-01: Verification gate = clean compile (hard gate) + a light human eyeball of the PDF.**
  The hard, blocking gate is "`docs-pdf` compiles with no `kai`/any `TypstError`". A quick visual
  glance at the generated PDF is layered on top — but it is a sanity glance, **not** an
  element-by-element visual audit. No automated visual-snapshot / golden-PDF infra is built
  (rejected as over-engineering for a maintenance cycle).
- **D-02: Accept the new appearance as the new baseline — as long as nothing is broken.**
  If a bumped package changes icons/colors/spacing/highlighting, **accept the new look**. Do NOT
  spend effort restoring the old (pre-bump) appearance via config/overrides/show-rules. This keeps
  Phase 7 scope small and risk low. (User explicitly chose "accept new look" over "restore old look"
  and over "case-by-case".)
- **D-03: Judge the after-PDF standalone — no before/after comparison.**
  Do NOT compile a pre-bump "before" PDF (typst 0.14.9 + old packages) to diff against. Just inspect
  the post-bump PDF on its own. (User chose the lighter standalone check over a before/after diff.)
- **D-04: Pass criterion = "no error glyphs / no obviously-broken output" ONLY.**
  The eyeball passes if the PDF has no blank/broken boxes, no missing-glyph tofu (⬛), no error
  glyphs. It does **NOT** require per-element verification (i.e. no fixed "admonition has icon+color /
  code is language-highlighted / math is typeset" checklist — user chose the looser criterion over
  the 3-element checklist). The empirical `kai`-free compile is the real gate; the visual glance is
  only a coarse "nothing is visibly broken" backstop.

**Net effect for the planner:** the phase's done-ness gate is (a) `docs-pdf` compiles cleanly with
no `TypstError`, `test_preview_version_sync.py` green; plus (b) a quick "open the PDF, no tofu/broken
boxes" glance. Do not invest in visual baselines, before/after diffs, or restoring prior styling.

### Claude's Discretion (planner/researcher decide with these defaults)

Three gray areas were surfaced but the user routed them to the planner as already-locked by
ROADMAP/REQUIREMENTS. Carry these defaults forward unless research contradicts:

- **Verification corpus / rigor:** Use the existing `tox -e docs-pdf` as the real compile gate.
  Confirmed: the project's own `docs/` already exercise all four packages — admonitions
  (`gentle-clues`), math (`mitex`), and code blocks (`codly`/`codly-languages`) — so `docs-pdf` is a
  genuine end-to-end corpus for all four. Do NOT pull a dedicated all-4-package smoke fixture forward
  into Phase 7; the standalone `typst compile` smoke test is explicitly Phase 9 (CI-02).
- **Bump strategy:** Default to bumping all four packages + typst **together** (matches the "atomic"
  framing and is fastest), and only `bisect` package-by-package **if** `kai` (or another break)
  persists — per the ROADMAP contingency. Do not proactively bump one-at-a-time unless a failure
  forces isolation.
- **codly-break escalation:** If `codly 1.3.0` breaks under typst 0.15 (it is at the Typst Universe
  registry ceiling — no newer version), the escalation ladder is: source-level patch/vendoring →
  swap to an alternate code-highlighting path → pin typst to the highest 0.15.x codly tolerates.
  Only invoked if the empirical compile actually breaks on codly.

### Planner implementation note (not a user decision)

- `writer.py:96` / `template_engine.py:315` import mitex with a **named** surface —
  `#import "@preview/mitex:0.2.4": mi, mitex` — while `templates/base.typ:14` uses a glob
  `#import "@preview/mitex:0.2.4": *`. When bumping mitex to `0.2.7`, verify the `mi`/`mitex`
  export names still exist in 0.2.7; a renamed/removed export would break the named import even if
  the version-sync test (which only checks the version *strings* agree) stays green.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & scope (locked)
- `.planning/REQUIREMENTS.md` — FWD-02, PKG-01/PKG-02/PKG-03: the exact locked version bumps and the
  "confirmed by a real `docs-pdf` compile, not changelog alone" gate. Read before planning.
- `.planning/ROADMAP.md` §"Phase 7" — success criteria + the bisect **Contingency** (codly is the
  fallback suspect; source-level workaround if it breaks).
- `.planning/PROJECT.md` — `kai` origin context (comes from inside a pinned `@preview` package under
  typst 0.15, not typsphinx source) + the Key Decisions table.
- `.planning/STATE.md` §"Blockers/Concerns" — the three carried Phase-7 landmines: (1) mitex `0.2.6+`
  `kai` attribution is MEDIUM confidence (CHANGELOG-based, not independently reproduced) → must
  confirm via real compile; (2) codly `1.3.0` registry-ceiling risk; (3) `test_preview_version_sync.py`
  proves the files *agree*, not that versions *compile* — the empirical compile is the real gatekeeper.

### Carried-forward context
- `.planning/phases/06-raise-runtime-pins-python-floor/06-CONTEXT.md` — branch strategy
  (D-01/D-02/D-03): `release/v0.5.0` integration branch, main stays green, accept the intentionally-red
  PDF lanes (Phase 7 is what turns them green).

### 3-way version-sync sites (must change in lockstep)
- `typsphinx/writer.py:94-97` — codly / codly-languages / mitex / gentle-clues imports for included docs.
- `typsphinx/template_engine.py:313-316` — same four imports for master docs.
- `typsphinx/templates/base.typ:8-19` — the default template's `@preview` imports.
- `tests/test_preview_version_sync.py` — asserts all three files agree (fails CI loudly on desync).
- `CLAUDE.md` §"The `@preview` version-sync hazard" — the three-places-must-stay-in-lockstep rule.

### Compile gate
- `tox.ini` §`[testenv:docs-pdf]` — the real end-to-end compile: `sphinx-build -b typstpdf source _build/pdf`
  from `docs/`. This is the empirical `kai`-free gate for this phase.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`tox -e docs-pdf`**: existing env that compiles the project's own docs to PDF via the `typstpdf`
  builder — the ready-made empirical compile corpus for the `kai` fix. Confirmed to exercise all four
  `@preview` packages (admonitions, math, code) so it validates every bumped package end-to-end.
- **`tests/test_preview_version_sync.py`**: existing guard that fails CI on 3-way version desync. Keep
  it green after the bumps — but note it validates *agreement*, not *compilation correctness*.

### Established Patterns
- **3-way version declaration**: the four `@preview` versions are hardcoded in three files
  (`writer.py`, `template_engine.py`, `templates/base.typ`). All four bumps must be applied to all
  three sites in one change (the FWD-03 "user-configurable versions" refactor is explicitly deferred
  to v2 / CFG-01).
- **mitex import surface asymmetry**: `writer.py` / `template_engine.py` use a named mitex import
  (`mi, mitex`); `base.typ` globs (`*`). See the planner note in `<decisions>`.

### Integration Points
- The bumped imports flow into every generated `.typ` (master docs via `template_engine.py` /
  `base.typ`; included docs via `writer.py`), then into the `typstpdf` PDF compile. A version
  incompatible with typst 0.15 surfaces as a `TypstError` at compile — which is exactly the `kai` break.

</code_context>

<specifics>
## Specific Ideas

- The user's stance throughout was "forward-port, not redesign" — minimize scope, trust the empirical
  `kai`-free compile as the real gate, and keep the visual check to a coarse "nothing is visibly
  broken (no tofu/error glyphs)" glance. Do not gold-plate the verification.

</specifics>

<deferred>
## Deferred Ideas

- **Automated visual-regression / golden-PDF baseline** — surfaced as a possible gate level; rejected
  as over-engineering for this maintenance cycle. If ever wanted, it's a standalone tooling effort,
  not part of Phase 7.
- **Dedicated all-4-package `typst compile` smoke fixture** — already scheduled as Phase 9 (CI-02);
  not pulled forward into Phase 7.
- (Already tracked in REQUIREMENTS.md v2) **CFG-01**: user-configurable `@preview` versions;
  **XOS-01**: cross-OS docs-PDF CI. Not in this milestone.

</deferred>

---

*Phase: 7-bump-preview-packages-typst-0-15-kai-fix*
*Context gathered: 2026-07-11*
