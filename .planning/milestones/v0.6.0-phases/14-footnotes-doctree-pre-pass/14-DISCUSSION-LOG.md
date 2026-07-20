# Phase 14: Footnotes (doctree pre-pass) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-12
**Phase:** 14-footnotes-doctree-pre-pass
**Areas discussed:** Pre-pass architecture, Label & reuse, Definition-node suppression, Scope & degradation

---

## Pre-pass architecture

### Index construction

| Option | Description | Selected |
|--------|-------------|----------|
| `visit_document` + `traverse` | Build `{id: node}` via `document.traverse(nodes.footnote)` at start of `visit_document`; no new class, rides existing walkabout, per-document | ✓ |
| Separate pre-walk in `writer.translate()` | Dedicated docutils NodeVisitor before main walkabout; explicit but extra state-handoff plumbing | |
| Sphinx/docutils existing tables | Reuse `document.footnotes`/`autofootnotes`; pickup gaps + version-coupling risk | |

**User's choice:** `visit_document` で traverse (推奨)

### Body render timing

| Option | Description | Selected |
|--------|-------------|----------|
| Lazy render at reference site | Index holds node refs; first `footnote_reference` renders children via buffer-swap in natural context | ✓ |
| Eager render in pre-pass | Pre-render each body to a stored string; risks dependence on mid-walk translator state | |

**User's choice:** 参照サイトで遅延レンダ (推奨)

---

## Label & reuse

### Label derivation

| Option | Description | Selected |
|--------|-------------|----------|
| `fn-{docutils id}` | Derive `<fn-{id}>` from `node['ids'][0]` (already `[a-z0-9-]`, doc-unique); ties to `refid` directly | ✓ |
| Monotonic counter `fn-1,2…` | Occurrence-order counter; needs `refid`↔counter side table | |

**User's choice:** docutils id 由来 fn-{id} (推奨)

### Numbering / auto-symbol

| Option | Description | Selected |
|--------|-------------|----------|
| Typst-native | `footnote[]` auto-numbers; document-order match falls out naturally; auto-symbol via same path | ✓ |
| Preserve docutils numbers/symbols | Force docutils labels; conflicts with native numbering (anti-pattern) | |

**User's choice:** Typst-native に一任 (推奨)

---

## Definition-node suppression

### Definition node handling

| Option | Description | Selected |
|--------|-------------|----------|
| `visit_footnote` → `SkipNode` | Definition node emits nothing at natural location (SC#1); body reached via index + lazy render | ✓ |
| Render but hide | Visit node and hide via `place`/`hide`; extra markup + fatal risk for no gain | |

**User's choice:** visit_footnote で SkipNode (推奨)

### `label` child on lazy render

| Option | Description | Selected |
|--------|-------------|----------|
| Skip `label`, render body only | Skip leading `label` child (docutils number/backref); Typst supplies its own marker; reference emits only `footnote[...]`/`footnote(<label>)` | ✓ |
| Include `label` in body | Renders docutils number alongside Typst mark — double marker | |

**User's choice:** label を skip し本文のみレンダ (推奨)

---

## Scope & degradation

### citation scope

| Option | Description | Selected |
|--------|-------------|----------|
| Out of scope | FN-01 = footnote only; retain existing behavior; add to backlog | ✓ |
| Handle together | Extend footnote plumbing to citations; scope creep beyond FN-01 | |

**User's choice:** バックログに追加 (out of scope, deferred to backlog)

### Dangling `footnote_reference`

| Option | Description | Selected |
|--------|-------------|----------|
| `logger.warning` + skip | refid not in index → warn, emit nothing, no fatal | ✓ |
| Emit reference text plain | Bodyless `footnote()` risks a Typst error | |

**User's choice:** warning を出し skip (推奨)

### Defined-but-unreferenced footnote

| Option | Description | Selected |
|--------|-------------|----------|
| Drop allowed | Bodies appear only at reference sites; unreferenced body never emits; outside SC | ✓ |
| Render at end | Fallback end-of-document placement; needs separate placement logic | |

**User's choice:** ドロップを許容 (推奨)

---

## Claude's Discretion

- **Exact label-attachment syntax under unified code-mode** — flagged as the core research task for
  `/gsd-plan-phase` (RESEARCH.md) and the GATE-01 render gate; likely a Phase 11 bracket-wrap of the
  `footnote[…] <label>` construct. The SC#2 no-duplication bar requires a proven compile-safe reuse
  form.

## Deferred Ideas

- `citation` / `citation_reference` node support — distinct requirement, out of FN-01 scope; noted
  for the backlog.
