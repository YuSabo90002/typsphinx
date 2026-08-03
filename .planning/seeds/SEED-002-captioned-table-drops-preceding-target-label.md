---
id: SEED-002
status: promoted
planted: 2026-08-03
planted_during: v0.7.0 — API rendering design overhaul / Phase 41
promoted: 2026-08-03
promoted_to: .planning/todos/pending/2026-08-03-captioned-table-drops-preceding-target-label.md
trigger_when: when relevant
scope: unknown
---

> **Promoted 2026-08-03 — this seed is closed.** It was filed as a seed first, then promoted at the
> owner's request because it is a reproducible defect rather than a forward-looking idea. The live
> record is the todo at
> `.planning/todos/pending/2026-08-03-captioned-table-drops-preceding-target-label.md`; edit that,
> not this file. Kept for provenance only, and marked `status: promoted` so it no longer surfaces
> during `/gsd-new-milestone` scans.

# SEED-002: Captioned tables emit only the `:name:`-derived Typst label and drop the id of an immediately preceding standalone target, leaving a dangling label that fails the compile

## Captured statement (verbatim, as reported)

> キャプション付き表で typsphinx は Typst ラベルを `:name:` 由来の 1 個しか出さず、直前の独立ターゲットの id を捨てる。リンクだけ残り dangling label で失敗。キャプションなしの表は正常。

## Why This Matters

_Not yet enriched. Run `/gsd-capture --seed --enrich SEED-002` to add rationale, a narrowed trigger, and a scope estimate._

Provisional framing, from the statement above:

- The reported failure is a **hard compile failure**, not a cosmetic degradation — a reference survives in the output while its label does not, so Typst fails on a dangling label rather than rendering something merely wrong.
- It is **conditional on the caption**: a caption-less table is reported to behave correctly. That splits the two `depart_table` emission paths (see Breadcrumbs) as the natural place to look.
- This is squarely in the project's core-value territory ("a URL the project publishes must actually resolve") applied to intra-document references.

## When to Surface

**Trigger:** when relevant

This seed will surface during `/gsd-new-milestone` when the milestone scope matches. Content-wise it is closest to any future work touching tables, cross-references/labels, or the `figure()` wrap.

## Scope Estimate

**Unknown** — run `/gsd-capture --seed --enrich SEED-002` to estimate effort.

## Breadcrumbs

Collected 2026-08-03 against `typsphinx/translator.py` at the Phase 41 tree. **These are pointers for a future investigation, not a diagnosis — nothing below has been reproduced or verified in this session.**

- `typsphinx/translator.py:3249` — `depart_table`. The captioned path (`if self.table_caption:`) and the caption-less path (`else:`) diverge here, which matches the reported "caption-less tables are fine" asymmetry.
- `typsphinx/translator.py:3318-3328` — the captioned path self-anchors **`node["ids"][0]` only** as the figure's own `<label>`.
- `typsphinx/translator.py:3341` — `self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))`. Worth noting for whoever picks this up: this line *does* appear to emit remainder ids (`ids[1:]`), with an in-code rationale (TBL-02 / Critical Pitfall 3) that double-anchoring `ids[0]` would be a Typst "label occurs multiple times" fatal. So the drop may well originate **upstream** — i.e. the standalone target's id may never reach `node["ids"]` at all, or may land at an index/order that this logic then skips. Verify which before assuming the fix belongs at this line.
- `typsphinx/translator.py:3689` / `:3763` — `visit_target` / `depart_target`, the handlers for the standalone `.. _label:` that precedes the table.
- `typsphinx/translator.py:517` — existing note that a captioned **figure** self-anchors `ids[0]`; the table path was modelled on `depart_figure` (D-04), so the same class of issue may or may not apply to figures. Untested — worth checking as part of the same investigation.

Related history: the captioned-table `figure()` wrap is TBL-01/TBL-02 from Phase 25.

## Notes

Captured via one-shot seed capture during Phase 41 execution. Enrich with trigger, why, and scope at your convenience.

**On the choice of artifact:** this was filed as a seed as requested. It reads like a reproducible defect rather than a forward-looking idea, so if it should instead block or schedule work, `/gsd-capture` (todo) or a roadmap phase would carry it with more urgency than a dormant seed does.

**Not yet established** (open questions for whoever picks this up): a minimal reproducing `.rst` snippet, the actual `node["ids"]` / `node["names"]` contents in the failing case, the exact Typst error text, and whether the same failure reproduces for captioned figures.
