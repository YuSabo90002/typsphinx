# Phase 50: PR #131 Image Path Defects - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-14
**Phase:** 50-PR #131 Image Path Defects
**Areas discussed:** none — the owner declined the gray-area selection

---

## Gray-area selection

Four gray areas were identified from measurement and offered for discussion.

| Option | Description | Selected |
|--------|-------------|----------|
| rehome 先の名前空間 | IMG-01's fix shape: always use a reserved namespace, probe the source tree and only relocate on collision, or suffix on dict collision. Flagged as colliding head-on with SC#3's "PR #131's own Issue #130 regression tests still pass unchanged", since two existing tests assert the current rehome string. | |
| doctreedir 外の退避方針 | IMG-02's fallback: warn and relocate inside the output directory, warn and abandon tracking, or silently clamp to the basename. Included whether the Windows cross-drive `ValueError` is closed at the same time. | |
| PDF 埋め込み画像の検証形 | How SC#1's "embeds the wrong picture" is proven from the compiled PDF — extracted-image dimensions, pixel content, or raw bytes — and whether the fixture is one master with two pictures or two masters with one each. | |
| SC#3 二回ビルド比較の置き場 | Whether the byte-identical-destination comparison becomes a permanent test, a one-time recorded measurement, or a hybrid. | |

**User's choice:** "議論ポイント無し" (free text) — no areas selected; nothing to discuss.

**Notes:** The answer was taken at face value: the discussion loop was skipped entirely and no
follow-up questions were asked. All four areas were resolved by Claude from measurement and written
into CONTEXT.md as D-01 through D-12, each with its rejected alternative and the measurement that
decided it, so a researcher can overturn one with evidence rather than by preference.

---

## Claude's Discretion

The whole decision set became Claude's discretion by the owner's answer. Within CONTEXT.md, these
were additionally left open for research and planning to settle:

- The exact spelling of the reserved namespace directory (`_typst_converted/` is the default,
  inherited from the filed todo).
- Second-order collision handling if the reserved namespace itself exists in the source tree.
- Whether the two defects land as one commit or two, and whether one helper or two guards express
  D-01 and D-05.
- Whether a debug-level log records a D-02 relocation (D-04 forbids a warning, not a debug line).
- The concrete pixel dimensions and file names in the D-09 fixture.

## Deferred Ideas

None — no new capability was raised, and the phase boundary was not challenged.
