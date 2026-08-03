# Phase 39: Admonition Taxonomy + Rubric Nesting - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-02
**Phase:** 39-admonition-taxonomy-rubric-nesting
**Areas discussed:** bucket colour source, greyscale distinguishability, generic admonition and topic, rubric

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Bucket colour source | The red bucket is split (`danger` peach `#fe640b` vs `error` red `#d20f39`); the green bucket is `tip` teal or `success` green | ✓ |
| Greyscale distinguishability | Header bands span only 5.4pp in greyscale; which `clue()` lever carries the distinction | ✓ |
| Generic admonition and topic | Both share `_visit_admonition(node, "clue")` — navy, no icon | ✓ |
| Rubric | SC#3 measured already passing; what does the phase actually do | ✓ |

**User's choice:** all four areas.

---

## Bucket colour source

| Option | Description | Selected |
|--------|-------------|----------|
| Ride gentle-clues' defaults | One clue function per bucket, colour = function default (`#04a5e5` / `#179299` / `#df8e1d` / `#d20f39`); `danger` folds into `error` so the red bucket is unambiguous; shortest emitted strings | ✓ |
| Pin Sphinx's measured palette | Pass `accent-color:` with `#145dea` / `#51ae80` / `#dd7a21` / `#ae5050`; bucket definition identical to Sphinx, independent of the package theme; colour literal on every admonition | |
| Minimal change — red bucket only | `seealso`→`tip`, `attention`→`error`, `danger`→`error`; leave note/warning alone; smallest migration; "green success" stays teal | |

**User's choice:** ride gentle-clues' defaults.
**Notes:** recorded as D-01 and D-03 in CONTEXT.md.

---

## Green bucket function

| Option | Description | Selected |
|--------|-------------|----------|
| `tip` (teal `#179299`) | `hint`/`tip` already emit it, so only `seealso` moves; smallest exact-string churn; ADM-01's "(green 'success')" is not taken literally | ✓ |
| `success` (green `#40a02b`) | Literal reading of ADM-01, closest to Sphinx's `#51ae80`; but `checkbox.svg` reads as "done", and `.. tip::`/`.. hint::` headers would default to "Success" | |

**User's choice:** `tip`.
**Notes:** D-02.

---

## Title handling after folding

| Option | Description | Selected |
|--------|-------------|----------|
| Let the folded defaults stand | `.. danger::` and `.. attention::` both titled "Error"; auto-localised through gentle-clues' `[lang.ja]`; shortest emitted strings; loses the severity distinction in the header | |
| Keep the source word via `custom_title` | `"Attention"` / `"Danger"` passed explicitly; not run through linguify, so English in the `ja` build | (superseded) |
| Use Sphinx's own translation catalog | `sphinx.locale.admonitionlabels`; verified live to resolve to Japanese under `language = "ja"`; identical to what Sphinx's HTML and LaTeX builders use | ✓ |

**User's choice:** Sphinx's translation catalog.
**Notes:** the user first selected `custom_title`, then retracted it and asked for a third path.
Measured and confirmed live before recording. D-04.

---

## Catalog scope

| Option | Description | Selected |
|--------|-------------|----------|
| All ten types | One source of truth for header text; matches every other Sphinx builder; costs a `ja` regression on `.. tip::` (「ヒント」→"Tip"), `.. note::` (「情報」→「注釈」) and `"See Also"`→`"See also"`; every admonition's emitted string changes | ✓ |
| Only the types whose title drifts | `seealso`/`important`/`attention`/`danger` only; keeps gentle-clues' better `ja` strings elsewhere; minimal migration; two title sources coexist and `caution` stays inconsistent with Sphinx | |

**User's choice:** all ten types.
**Notes:** D-05.

---

## Greyscale distinguishability

| Option | Description | Selected |
|--------|-------------|----------|
| Prove the defaults suffice | No code change; four icons differ by shape, accent strokes span 35.9pp in greyscale; verify against a greyscale render; risk is a UAT rejection mid-phase | ✓ |
| Per-bucket `stroke-width` | e.g. `error` 4pt / `warning` 3pt / `success` 2pt / `note` 1pt; thickness reads without hue and matches severity order; adds `stroke-width` to every emitted admonition | |
| Per-bucket `header-color` | Widen the measured 5.4pp band spread deliberately; large surface area so easy to read; sacrifices colour identity and contradicts the "ride the defaults" decision | |

**User's choice:** prove the defaults suffice.
**Notes:** a dashed stroke was investigated and found impossible — `clue()`'s left edge is
`(thickness:, paint:, cap:)` with no `dash` key. D-06.

---

## Producing the greyscale render

| Option | Description | Selected |
|--------|-------------|----------|
| Add Pillow to the `[dev]` extra | `typst.compile(format="png", ppi=…)` then `convert("L")`; a few lines; dev-only, no runtime impact | ✓ |
| Stdlib-only PNG desaturation | zlib + struct decode/re-encode of RGBA8; zero new dependencies; a hand-rolled codec to verify for no product value | |

**User's choice:** Pillow in the `[dev]` extra.
**Notes:** measured that PIL, numpy, ImageMagick, ghostscript, `pdftoppm` and `mutool` are all
absent from this environment, and that desaturating inside Typst is impossible because the icon SVGs
carry baked-in fills. D-07.

---

## Fallback lever if greyscale UAT fails

| Option | Description | Selected |
|--------|-------------|----------|
| Pre-agree per-bucket `stroke-width` | Executor could apply it without returning to discuss; commits to a decision that will probably go unused | |
| Decide after seeing the rejection | Pick the lever against the actual render; the phase stops at the UAT checkpoint if it happens | ✓ |

**User's choice:** decide after seeing the rejection.
**Notes:** D-08.

---

## Generic `.. admonition::`

| Option | Description | Selected |
|--------|-------------|----------|
| Fold into the note bucket (`info`) | No new colour; fully consistent with riding the defaults; indistinguishable from a real `.. note::` | |
| Neutral grey fifth style | Matches Sphinx's grey band; gentle-clues has no grey clue, so it needs a colour literal | |
| `abstract` (sapphire) | Default colour, document icon; measured close to the success bucket's teal | (moved to topic) |
| `memo` | User's first pick; measured `#e64553` maroon, band L 91.1% against the error bucket's 88.5%, `excl.svg` "!" — reads as a warning | (withdrawn) |
| `notify` (blue `#1e66f5`, bell) | Colour clear of the four buckets; bell icon reads as neither a note nor a warning | ✓ |

**User's choice:** `notify`.
**Notes:** the user selected `memo` first; after being shown the measured proximity to the error
bucket they switched to `notify`. D-09.

---

## `.. topic::`

| Option | Description | Selected |
|--------|-------------|----------|
| Ride `notify` with the generic admonition | One change site; the base `clue` disappears; topic and generic admonition become visually identical | |
| `idea` | User's proposal; measured accent **byte-identical** to the warning bucket (`#df8e1d`, band `#faeedd`) — only the icon differs | (withdrawn) |
| `success` (green) | Furthest from every colour in use; checkbox icon means "done", unrelated to topic | |
| `quote` (lavender) | Colour clear of everything; quotation-mark icon is not strictly accurate | |
| `abstract` (sapphire `#209fb5`, document) | Document icon fits "a self-contained aside"; separates topic from the generic admonition as Sphinx does; sits near the success bucket's teal | ✓ |

**User's choice:** `abstract`.
**Notes:** the user rejected the first option set outright, proposed `idea`, and chose `abstract`
once the taken/free colour map was measured and laid out. D-10.

---

## Rubric — what the phase does

| Option | Description | Selected |
|--------|-------------|----------|
| Assertion only | Pin SC#3 as a non-regression guard, touch no handler bytes; lowest risk; leaves two known defects unfixed | |
| Assertion plus folding the known todos | Fix the `in_list_item` leak / `par()` drop and the double-blank-line wart; the docstring names Phase 39 as owner; rubric emitted bytes change and five modules plus five fixtures enter migration | ✓ |

**User's choice:** assertion plus folding the known todos.
**Notes:** D-11.

---

## SC#3's missing RED

| Option | Description | Selected |
|--------|-------------|----------|
| Invariance guard plus ROADMAP correction | SC#3 becomes "Phase 38 achieved it, this phase must not break it"; the RED comes from the folded todo; follows Phase 36 SC#3's recorded precedent | ✓ |
| Invariance guard, ROADMAP untouched | Same test posture, note the measurement in CONTEXT only; leaves SC#3's wording at odds with reality at verify time | |
| Manufacture a RED by removing the pad | Temporarily strip Phase 38's `pad` to observe the margin jump; measures Phase 38's work, not Phase 39's, and guards nothing | |

**User's choice:** invariance guard plus ROADMAP correction.
**Notes:** the `par()` drop was reproduced on a real build before this option was offered. D-12, D-13.

---

## Claude's Discretion

- How the `admonitionlabels` lookup is threaded into `_visit_admonition`.
- Escaping of now-possibly-non-ASCII titles inside the emitted Typst string literal.
- Which real API page SC#3's autodoc "Options" measurement is taken from.
- The greyscale render's PPI, page selection and file naming.

## Deferred Ideas

- Restoring 「ヒント」 for `.. tip::` in the `ja` build (Sphinx's own `ja` catalog leaves it
  untranslated) — a translation-quality question, possibly an upstream Sphinx contribution.
- A neutral grey bucket matching Sphinx's generic-admonition and topic band — blocked by the
  no-colour-literals decision and by gentle-clues having no grey clue.
- TOP-01 (boxing the `.. contents::` local TOC) — already deferred at v0.7.0 scoping.
