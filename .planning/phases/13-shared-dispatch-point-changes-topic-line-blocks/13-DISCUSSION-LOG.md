# Phase 13: Shared Dispatch-Point Changes (topic + line blocks) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-12
**Phase:** 13-Shared Dispatch-Point Changes (topic + line blocks)
**Areas discussed:** topic rendering, line_block indentation, `.. contents::` handling, shared-dispatch reach

---

## topic rendering (BLK-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse admonition helper | gentle-clues base `clue` box (no icon/accent, bold title) via `_visit_admonition(node,"clue")`; extend `visit_title` buffer-swap to topic parents. Minimal change, consistent with admonitions, literal REQ BLK-02 wording. | ✓ |
| Box-less lightweight block | Bold label + body only (no icon/box). Most faithful to ROADMAP SC#1 "bold inline label" but needs net-new machinery. | |

**User's choice:** Reuse admonition helper (recommended)
**Notes:** Reconciles REQ BLK-02 ("reusing the admonition helper") with ROADMAP SC#1 — the `clue` box's title is bold and it never calls `heading()`, so the doc's heading/TOC structure is unchanged.

---

## line_block indentation (BLK-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Simple indent reproduction | `linebreak()` per line + fixed indent per nesting depth, preserving poetry-stanza / address structure; compile-verified in fixture. | ✓ |
| Breaks-only / flatten | Only `linebreak()` per line (SC#2 minimum); drops nested indentation. | |

**User's choice:** Simple indent reproduction (recommended)
**Notes:** SC#2 mandates only breaks; indentation chosen as default beyond the floor because an address/stanza without indentation loses meaning. Indent must be compile-safe (bracket-wrap if markup needed); fall back to breaks-only only if a construct risks an unavoidable fatal.

---

## `.. contents::` handling

| Option | Description | Selected |
|--------|-------------|----------|
| Box-less pass-through | Detect `'contents'` class; skip the `clue` box, emit a bold label + render the child `bullet_list` normally. Avoids boxed TOC and level-0 fatal. | ✓ |
| Same `clue` box as generic topic | No branch; but wraps the whole TOC in a box. | |
| Full skip | Drop the local TOC entirely. | |

**User's choice:** Box-less pass-through (recommended)
**Notes:** `.. contents::` is a `topic` node with the `'contents'` class and a Sphinx-resolved child `bullet_list`; its title is still buffer-swapped so it never hits the `else` heading branch.

---

## shared-dispatch reach (`visit_title`)

| Option | Description | Selected |
|--------|-------------|----------|
| topic/contents + level clamp | Handle topic/contents explicitly AND add `max(1, section_level)` to the `else` branch so no title ever emits `heading(level: 0)`. No sidebar-specific rendering. | ✓ |
| Strict scope only | topic/contents only; leave `else` branch as-is (known level-0 fatal class stays live). | |

**User's choice:** topic/contents only + level clamp (recommended)
**Notes:** The clamp is a pure safety net at the exact load-bearing method the phase already edits; directly serves the milestone's no-fatal bar. sidebar stays out of scope (only protected from being fatal, not styled).

---

## Claude's Discretion

- Exact indent unit/mechanism for nested `line_block` (`#h` vs `pad`), subject to compile-safety.
- Punctuation/spacing/label styling for the box-less contents-topic bold label.
- Whether `visit_topic` uses an instance flag or inline branch for the contents vs generic path.
- Fixture document contents beyond the explicit SC cases.
- Empty-`line`-node (blank line in a `line_block`) rendering (`linebreak()` vs `#v()`).

## Deferred Ideas

- Full `.. sidebar::` rendering (shares the dispatch but out of scope; only protected from being fatal by the level clamp).
- Native Typst `#outline()` for local TOCs (D-05 uses the Sphinx-resolved `bullet_list` pass-through for now).
