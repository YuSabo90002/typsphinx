# Phase 38: Structural Indentation + Info Fields - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-01
**Phase:** 38-structural-indentation-info-fields
**Areas discussed:** Field-body parameter typography (FLD-03), block_quote's participation in
IND-04, FLD-02's "inline prose" reading, structural indent step value

Every option below was presented with numbers taken this session from a real `sphinx-build -b typst`
run, a real `typst.compile()` probe, or a working prototype (a scratchpad copy of `typsphinx/`,
patched and driven over this project's own `docs/source` to a real 87-page PDF — the repository was
never modified). Three of the four areas were decided against rendered images rather than
descriptions.

---

## Todo cross-reference

`todo.match-phase 38` returned 11 records; 8 were keyword false positives on the matcher's 0.4–0.6
band. The remaining 3 were presented.

| Option | Description | Selected |
|--------|-------------|----------|
| `desc_break_marker` buffer-swap bug | `_desc_break_marker` compares `len(self.body)` across two `depart_desc` calls, but `self.body` is reassigned at five sites and only `in_table` is guarded | ✓ |
| `EXPECTED_PAGE_COUNT_PRE_PHASE` rename | Constant name no longer matches its post-`37-09` value; pure naming hygiene | ✓ |
| `visit_desc_sig_name` docstring `*` | Unescaped asterisk emits a docutils warning and a stray `problematic` node in this project's own API-reference PDF | |
| Fold none of them | Keep Phase 38 to IND-01..05 / FLD-01..03 | |

**User's choice:** "claude おすすめ" — selection delegated.
**Notes:** Folded the first two, left the third. The `desc_break_marker` todo was folded on evidence
rather than judgement: the prototype proved Phase 38 voids the marker's premise (5 top-level
`parbreak()` statements before the change, 6 after), so the phase that re-derives the bookkeeping is
the phase that should make it buffer-safe. The page-count constant was folded because Phase 38
measurably moves page counts (97 → 87 on this project's own docs), so it must be re-measured
regardless. The docstring asterisk was left pending: `visit_desc_sig_name` is not a handler this
phase changes, and the defect gates no IND or FLD requirement.

---

## Field-body parameter typography (FLD-03)

Four candidates were compiled side by side with Phase 38's indent already applied and the Phase 37
signature line above each, so the owner could see how each recipe sits against the signature it
echoes.

| Option | Description | Selected |
|--------|-------------|----------|
| D — current | name `strong(text())` bold proportional, type `emph(text())` italic proportional. Shown as the control; FLD-03 requires monospace, so it could not stay | |
| A — reference-faithful | name `strong(raw())` bold monospace, type `emph(raw())` italic monospace, matching `sphinxlatexstyletext.sty:48,50` | ✓ |
| B — regular-mono type | name `strong(raw())`, type `raw()`. Avoids reusing italic monospace, which Phase 37 D-01 had already assigned to the signature's parameter name | |
| C — regular-mono name | name `raw()`, type `emph(raw())`. Strongest contrast against the plain-bold label, weakest cue for finding the parameter name inside a bullet | |

**User's choice:** A — reference-faithful.
**Notes:** The trade-off was stated explicitly before the choice: under A, the field body's **type**
lands on the same face as the signature's **parameter name**, and FLD-03's own prose warns that
"collapsing the two would be wrong". The owner saw that overlap in the rendering and accepted it.
CONTEXT.md D-06 records why A still satisfies FLD-03 as written — the two *recipes* differ (signature:
italic-mono name / regular-mono type; field body: bold-mono name / italic-mono type) even though one
face is shared — so verify-time does not re-open it.

A follow-up question during this area asked whether the four variants differed in line spacing and
width. Measured answer: leading is identical across all four (14.245 / 14.388 / 20.438pt at every
step, with a single 0.4pt difference on one step from the monospace line box), and within the
monospace family `raw`, `emph(raw)` and `strong(raw)` have identical advance widths (105.96pt for
`Iterable[str] | None`). The visible width difference is proportional-vs-monospace only
(`text()` 85.26pt for the same string). The apparent unevenness turned out to be the field-list
rhythm defect, which is the FLD-02 area below.

---

## FLD-02's "inline prose" reading

| Option | Description | Selected |
|--------|-------------|----------|
| Label and value on one line | Read "inline" as label and value sharing a line. Measured effect: one field 40.733pt → 20.438pt, one rhythm instead of three | ✓ |
| Bulleted-vs-prose contrast only | Read FLD-02 as contrasting bulleted with non-bulleted. Already satisfied; Phase 38 owes only a non-regression check, and the rhythm defect goes to a todo | |
| Even the spacing without inlining | Keep label and value on separate lines but pull the 40.733pt interval toward the 14.39pt bullet band | |

**User's choice:** Label and value on one line.
**Notes:** The measurement that drove this: the pre-phase build emits three different vertical
intervals inside one field-list block — 14.245pt from label to first bullet, 14.388pt between
bullets, and 40.733pt per single-value field, because the bare label becomes one paragraph and the
`par()` value becomes a second. REQUIREMENTS.md's parenthetical claim that "the inline half already
works via `_last_field_body_was_inline`" was checked and does not hold for the ordinary
`:param:`/`:returns:` docstring case — that flag only fires when docutils collapses the body, which
it does not do there. Whole-document consequence, measured on this project's own docs: 97 → 87 pages.

---

## block_quote's participation in IND-04

Presented once, dismissed, and re-presented after the real PDFs had been reviewed.

| Option | Description | Selected |
|--------|-------------|----------|
| Leave `quote()` untouched | `typsphinx/` has no indent literal at any IND-04 site today, so ROADMAP SC#4's grep property already holds and stays holding. Typst's `quote(block: true, …)` default measured at 11.0pt | ✓ |
| Wrap in `pad` | `pad(left: 2.5em, quote(block: true, …))` → 27.5 + 11.0 = 38.5pt; the constant's value would stop matching the depth it produces | |
| Replace `quote()` with `pad` | Reaches 27.5pt exactly, but loses `quote()`'s own vertical spacing and destroys `visit_attribution`'s right-aligned "— Author" | |

**User's choice:** Leave `quote()` untouched.
**Notes:** CONTEXT.md D-04 records the binding reading — IND-04 exists to forbid per-node magic
numbers, not to force every indent context onto one visual depth — so that verify-time does not read
IND-04's "drives block quotes" literally and reopen the question.

---

## Structural indent step value

Decided against four real PDFs of this project's own documentation, each cut to the same anchored
page (`TypstBuilder.write_doc` / `copy_image_files` / `copy_template_assets` / `finish`).

| Option | Description | Selected |
|--------|-------------|----------|
| 2.5em (unchanged) | Phase 37 D-06's owner-chosen value. Accumulates to 27.5 / 55.0 / 82.5pt against a 453.54pt column. Leaves Phase 37's `golden.typ` and emission contract untouched | ✓ |
| 2.0em | 22.0 / 44.0 / 66.0pt — the low end of REQUIREMENTS.md's ≈22–25pt reference quantum. Would force re-derivation of `golden.typ`'s 7 signature lines and `37-EMISSION-CONTRACT.md` §3/§9/§10 | |
| 1.5em | 16.5 / 33.0 / 49.5pt — gentlest accumulation, but one step approaches Typst's own bullet-marker indent (measured 9.36pt) and the hierarchy stops reading | |

**User's choice:** 2.5em, unchanged.
**Notes:** The owner initially asked for real PDF pages rather than mockups before answering; the
four pages were produced from the prototype and the control, and the decision was made against
those. It was stated at the time that 2.5em (27.5pt at 11pt body) sits just above the ≈22–25pt
reference quantum, and that 2.0em would land inside it — the divergence is deliberate.

---

## Claude's Discretion

- **D-12** — the indent primitive (`pad(left:)` vs `block(inset:)`) and all the emission mechanics
  around it: separator and `list_item_needs_separator` bookkeeping, and how D-07's inline field is
  actually implemented. The prototype achieved the inline field by post-processing the emitted
  `.typ`, which is explicitly **not** an acceptable implementation — it was a rendering device for
  the owner's review only. Binding constraints recorded in CONTEXT.md.
- **D-13** — the stray `parbreak()` at the head of each bulleted field-list item (measured +7.15pt
  before the first bullet, nothing between items). Not raised with the owner. Fix it or leave it,
  but say which.
- **D-14** — the exact-string migration strategy, bounded by ROADMAP SC#5 (hand-derived expected
  strings plus a recorded census) and milestone invariant #4 (never regenerate from the new code's
  output).
- **D-09**'s shape — whether `literal_strong` / `literal_emphasis` get a fourth and fifth verbatim
  copy of the `visit_strong` body (the Phase 36 D-01 precedent) or a shared helper.

## Deferred Ideas

None. Scope stayed inside IND-01..05 and FLD-01..03 plus the two folded todos, both of which live in
handlers this phase necessarily rewrites.
