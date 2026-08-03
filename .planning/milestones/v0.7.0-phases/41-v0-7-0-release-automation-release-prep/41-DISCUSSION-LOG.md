# Phase 41: v0.7.0 Release Automation + Release Prep - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-02
**Phase:** 41-v0-7-0-release-automation-release-prep
**Areas discussed:** CHANGELOG `[0.7.0]` granularity, `release.yml` extraction, scope of what this
phase closes, the `ja` four-check glyph bar

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| CHANGELOG `[0.7.0]` granularity | How to cut 5 phases / 32 requirements / a +1,699-line translator diff into bullets; BREAKING or not; what `### Verified` carries | ✓ |
| `release.yml` extraction | Inline shell vs committed script + pytest; how SC#1's "executed for real" is proven; `generate_release_notes` disposition | ✓ |
| How much this phase closes | Phase 40's WR-01/02/03, the docstring warning, todo hygiene, the four unrelated pending todos | ✓ |
| The `ja` four-check glyph bar | Where the "before" comes from, how the visual check is treated, where the translations repo clone lives | ✓ |

**User's choice:** all four.

---

## CHANGELOG `[0.7.0]` — bullet granularity

| Option | Description | Selected |
|--------|-------------|----------|
| User-visible change units (5–6 bullets) | Phase 33 D-09's rule extended: signature typography (SIG-01..09), body + field-list indentation (IND, FLD), admonition taxonomy + rubric (ADM), citation round trip (CIT), block-math blank line (MATH-02) | ✓ |
| One bullet per requirement ID (32) | Full traceability, but splits "what part of the signature line became what" across five bullets | |
| Feature-family units (3) | Shortest; buries single large changes like IND-02 | |

**User's choice:** user-visible change units.

## CHANGELOG `[0.7.0]` — announcing the visual change

| Option | Description | Selected |
|--------|-------------|----------|
| Lead paragraph states it; no BREAKING label | Extends 0.6.5 D-01's axis — no `typst_*` config, builder name, or template parameter changed | ✓ |
| A BREAKING bullet inside `### Changed` | For users holding golden `.typ` files or styling `#include()`d bodies from their own template | |
| A new `Upgrade notes` subheading | Enumerates the blast radius; adds a heading the CHANGELOG has never carried | |

**User's choice:** lead paragraph only.

## CHANGELOG `[0.7.0]` — `### Verified` contents

| Option | Description | Selected |
|--------|-------------|----------|
| The same three items as 0.6.5 | Zero new runtime deps / `@preview` version strings unchanged / full-corpus `-b typstpdf` fatal-free | ✓ |
| Those three plus the two docs dogfooding builds | SC#3 runs them anyway, and the translator moved +1,699 lines | |
| Plus ADM-04's owner visual sign-off | The milestone's only `[V]` requirement | |

**User's choice:** the same three items.

## CHANGELOG `[0.7.0]` — section split and lead axis

| Option | Description | Selected |
|--------|-------------|----------|
| `Added`: CIT / `Changed`: SIG,IND,FLD,ADM / `Fixed`: MATH-02 | Keep a Changelog semantics taken literally | ✓ |
| Everything under `Changed` | One "re-drawing" narrative; CIT-01 reads weakly as a change | |
| CIT in both `Added` and `Fixed` | Citations have both faces; duplicates the entry | |
| Lead: "API reference pages became readable" | Follows the milestone name and ROADMAP's goal sentence | ✓ |
| Lead: "correct → well typeset" | Quotes PROJECT.md's core value | |
| Lead: the change-surface facts first | Accurate, but defers what actually got better | |

**User's choice:** the Keep-a-Changelog split; the "readable API reference" lead.

---

## `release.yml` — where the extraction lives

| Option | Description | Selected |
|--------|-------------|----------|
| Committed script + pytest | Joins `test_readme_version_sync` / `test_preview_version_sync`; runs on every CI run | ✓ |
| Inline shell (awk/sed) in the workflow | Self-contained; unreachable from pytest | |
| Inline shell + a separately-implemented pytest | Two implementations; a divergence in the extraction itself stays invisible | |

**User's choice:** committed script + pytest.

## `release.yml` — how SC#1 is proven

| Option | Description | Selected |
|--------|-------------|----------|
| Hand-run transcribed verbatim into GATE-EVIDENCE | The project's standard evidence shape | ✓ |
| Transcript plus a recorded RED for the missing-section case | Directly exercises the todo's named failure mode | |
| Plus a diff against the real v0.6.5 release body | Answers REL-04's motivation directly; needs network access | |

**User's choice:** hand-run transcript.
**Notes:** the failure path is still covered — it moves into the pytest of D-06/D-10 rather than
into the SC#1 transcript.

## `release.yml` — `generate_release_notes` and fail-loud placement

| Option | Description | Selected |
|--------|-------------|----------|
| Keep `generate_release_notes: true` | v0.6.4's auto portion measured 5 lines; the bloat was the hand-rolled dump | ✓ |
| Drop it | Body becomes exactly the CHANGELOG section; compare link must be added by hand | |
| Fail loud in the `validate` job | Runs before `publish-pypi`, so "on PyPI but no GitHub Release" cannot happen | ✓ |
| Fail loud in `create-release` only | One job changed; fails after the PyPI upload | |
| Both jobs | Early warning plus an extraction-site guard; logic in two places | |

**User's choice:** keep the auto notes; move the check into `validate`.

---

## Scope — Phase 40's WR-01 / WR-02 / WR-03

| Option | Description | Selected |
|--------|-------------|----------|
| Insert a Phase 40.1 and close them there | Ships in v0.7.0; Phase 41's boundary stays REL-04/REL-05. Precedent: Phases 8.1, 30.1, 39's gap closure | ✓ |
| File as todos for v0.7.1+ | Phase 35 D-05's axis; measured not to fire against the real corpus | |
| Close them inside Phase 41 | No new phase, but Phase 41 would enlarge the proof obligation its own SC#4 discharges | |
| WR-01 only in Phase 41, the rest as todos | WR-01 is one line and the only compile-fatal route | |

**User's choice:** insert Phase 40.1.
**Notes:** the owner raised the inserted-phase option themselves — it was not on the original menu.
The deciding input was the measured RED problem: `40-REVIEW.md` records all three as unreproduced
against a real Sphinx build, while milestone invariant #4 demands a recorded-RED GATE-01 fixture per
node-handler change, and proving exactly that is Phase 41's own SC#4. Two consequences recorded in
CONTEXT: Phase 41's SC#4 sweep must cover Phase 40.1's changes, and inserting the phase is a
separate `/gsd-phase` action.

## Scope — the remaining items

| Option | Description | Selected |
|--------|-------------|----------|
| Close the docstring `*type` warning in Phase 41 | Docstring escape only; no `.typ` shape change; SC#3 runs `tox -e docs-pdf` anyway | ✓ |
| Put it in Phase 40.1 | Keeps Phase 41 free of any `typsphinx/` change; unrelated to that phase's subject | |
| Leave it as a todo | A malformed line stays in the published API reference | |
| Do both hygiene items in Phase 41 | File the two already-fixed todos to `completed/`; terminate PROJECT.md's two comments | ✓ |
| Todo filing only | Let `/gsd-complete-milestone` pick up PROJECT.md | |
| Neither | Ledger drift is the milestone-audit's job | |
| Defer all four unrelated todos to v0.7.1+ | linkcheck CI, non-`str` docname `TypeError`, `derive_typst_lang` duplication, typing modernization | ✓ |
| Pick up the linkcheck CI job | The release adds one link; `links.yml` already covers it | |

**User's choice:** close the docstring warning and both hygiene items here; defer the other four.

---

## The `ja` four-check glyph bar

| Option | Description | Selected |
|--------|-------------|----------|
| Build `main` and `HEAD` locally, both `ja` | Cleanest causality — same machine, toolchain, fonts | ✓ |
| Download RTD's served `ja` PDF as "before" | Phase 30.1's actual method; RTD's image differs from local | |
| Reuse Phase 30.1's recorded values | One build cheaper; v0.6.4-era values with v0.6.5 in between | |
| Owner visual sign-off is a Phase 41 close condition | Same shape as ADM-04's sign-off in Phase 39 | ✓ |
| Record check 4 as `human_needed` and hand it off | Phase 30.1's form | |
| Skip the visual look when the `/BaseFont` sets match | Font selection unchanged ⇒ no new tofu | |
| Clone the translations repo into the phase directory | Phase 30.1's precedent (a working clone, never committed) | ✓ |
| Clone into a scratch directory outside the repository | Keeps the repository clean; SHA recorded for reproducibility | |

**User's choice:** two local builds; visual sign-off inside the phase; clone in the phase directory.
**Notes:** measured mitigation presented during the discussion — the milestone never names a font
family (monospace goes only through `raw(...)`, and `base.typ` sets only `size` and `lang`) — but 24
new `raw(` call sites were added, and `raw()` resolves to Typst's default monospace family, which
has no CJK coverage. The exposure is real without any family name being written.

---

## Claude's Discretion

- The exact wording of the `[0.7.0]` entry and which 5–6 bullets D-01's rule resolves to.
- The extraction script's language, filename, and CLI shape, and how `release.yml` invokes it in
  both jobs.
- The pytest module's name and case list beyond the two directions fixed by D-10.
- Plan decomposition and ordering; the `uv.lock` regeneration procedure.
- The mechanical method for SC#4's "every node-handler change carries its recorded-RED GATE-01
  fixture" over the +1,699-line translator diff — explicitly left open by the owner.
- The format of `41-HANDOFF.md`, and the name of the evidence file (not `41-VERIFICATION.md`).

## Deferred Ideas

- **Phase 40.1** — WR-01/02/03, to be inserted into `ROADMAP.md` via `/gsd-phase` and executed
  before Phase 41's final invariant sweep. Its own open question: how to take a RED for defects
  recorded as unreproduced against a real Sphinx build.
- The four pending todos deferred to v0.7.1+: `sphinx-build -b linkcheck` CI job, non-`str` docname
  `TypeError` in `TypstPDFBuilder.finish()`, `derive_typst_lang()`'s duplicated warning block, and
  the typing modernization.
