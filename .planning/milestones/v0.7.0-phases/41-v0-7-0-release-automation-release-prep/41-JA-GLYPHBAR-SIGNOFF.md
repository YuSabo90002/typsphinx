# `ja` Glyph Bar Sign-off: Check 4 — Owner Visual Confirmation

**Date:** 2026-08-03
**Plan:** 41-04
**Status: MET — the owner inspected the sampled pages of both the `main` (before) and HEAD
(after) `ja` PDFs and reported no substituted, missing, or mismatched Japanese glyphs.**

## 1. Requirement under judgement

Quoted verbatim from `.planning/ROADMAP.md` § "Phase 41: v0.7.0 Release Automation + Release
Prep", Success Criterion 3:

> 3. The post-bump tree is green across the full suite, the lint/type trio, the full-corpus
>    `-b typstpdf` gate, and both docs dogfooding builds — including a re-run of the `ja` build's
>    four-check glyph bar, because any new font selection introduced by this milestone can shadow
>    the `Noto Serif CJK JP` fallback silently, with no warning or error.

This sign-off discharges the fourth of that glyph bar's four checks — the owner's visual
confirmation — which `41-CONTEXT.md` D-16 makes a Phase 41 close condition collected inside the
phase, following the same shape as `39-ADM04-SIGNOFF.md`. **No automated assertion exists anywhere
in this plan or its tooling for check 4 itself, and none was offered as a stand-in for the owner's
judgement** — consistent with this plan's `must_haves.prohibitions` and D-16's explicit rejection
of skipping the visual look when check 3's `/BaseFont` sets match.

## 2. Artifact provenance

(All values below are reproduced from `41-JA-GLYPH-BAR.md`, not re-derived.)

| Item | Value |
|---|---|
| "Before" PDF | `/tmp/p41-main-out/typsphinx.pdf` — 1,942,905 bytes, SHA-256 `495ced3ea21651c3301d6d4eda819ebf35a2f1c7c66b80d704cdb7115df27187` |
| "After" PDF | `/tmp/p41-head-out/typsphinx.pdf` — 2,206,751 bytes, SHA-256 `b64cf3563c04be2052eede5a629250a7c829db1118fdf44a82804746494f605f` |
| "Before" tree HEAD SHA | `51e02b6b61b314c99740883fb4bee7ce7b9be76b` (this repository's local `main`, provisioned in its own `git worktree add` at `/tmp/p41-main-tree`) |
| "After" tree HEAD SHA | `aa9d2f06ad854f6f96d285d669ba4bb91b053f31` (this plan's own worktree) |
| Pages inspected (1-indexed, same page numbers on both PDFs — both are 94 pages) | 1, 5, 32, 33, 63, 74 — the CJK-density sample (title page, overall density peak, per-third density peaks) unioned with the first `raw()`-styled API signature page located within the API Reference section (Pitfall 6) |
| Checks 1-3 (mechanical) | Page count: 94/94 (delta 0). CJK character total: 6,050 (before) / 6,084 (after), delta +34 (no drop). Embedded `/BaseFont` families: 7 of 8 shared, including the sole CJK-coverage font `NotoSerifCJKjp-ExtraLight` present identically on both sides; the two-family symmetric difference is confined to non-CJK Latin style variants (`DejaVuSansMono-Oblique` head-only, `LibertinusSerif-Semibold-Identity-H` main-only) — full detail in `41-JA-GLYPH-BAR.md`. |

**Presentation method (orchestrator-side fact, not an owner statement):** the owner was shown
before(`main`)/after(HEAD) rasterizations, at 110dpi, of all six sampled pages (p1, p5, p32, p33,
p63, p74) rendered from the two PDFs named above via `pdftoppm` (nix `poppler-utils`), alongside
the checks 1-3 figures recorded in `41-JA-GLYPH-BAR.md`. The owner's response below was given
after that inspection.

## 3. No automated stand-in was offered

Consistent with D-16 and this plan's `must_haves.prohibitions`: no glyph-coverage score, no
per-page image diff, no font-set similarity metric, and no other computed number was presented to
the owner before or in place of this question. **Checks 1-3 passing, and check 3's `/BaseFont`
sets being 7-of-8 identical (including the one CJK-coverage font matching exactly), was explicitly
NOT accepted as a substitute for the owner's own look** — D-16 rejects exactly that shortcut, and
`41-JA-GLYPH-BAR.md`'s own "What These Checks Cannot Prove" section states plainly why a font-set
match cannot settle the question: Typst's font fallback is silent, and a substituted glyph very
often still extracts as the correct character even when it visually renders wrong.

## 4. The owner's answer (verbatim)

The owner was shown the rasterized before/after page pairs described in §2 above and asked to
confirm whether Japanese glyphs are intact — not substituted, not rendered as empty boxes, not in
a mismatched typeface — on every sampled page, per the checkpoint's `<resume-signal>`.

**The owner's verbatim response, in full, was exactly one word:**

> approved

That is the complete response — no additional words, caveats, or reported issues were given. No
further commentary is attributed to the owner beyond this single word.

## 5. Outcome

**Check 4 is MET.** The owner inspected the sampled pages of both PDFs and reported no substituted,
missing, or mismatched Japanese glyphs — the response was an unqualified "approved" with no
reported defect on any page or in either build.

Consequences:

- **No styling change is made.** This plan takes no `typsphinx/` code action; `git diff --stat --
  typsphinx/` is empty for this plan's commits.
- **No fallback lever is considered.** The owner reported no indistinguishable or substituted
  glyph, so no font-selection change is warranted.
- **No pending todo is filed.** The outcome is positive; there is no follow-up work to defer.
- **SC#3's `ja` four-check glyph bar is discharged in full** — checks 1-3 in
  `41-JA-GLYPH-BAR.md`, check 4 here. All four checks show no evidence of the font-shadowing
  exposure the bar exists to catch.

**Date recorded:** 2026-08-03
