# Phase 49: Per-Master Include Graph with State-Guarded Includes - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-14
**Phase:** 49-Per-Master Include Graph with State-Guarded Includes
**Areas discussed:** `:numref:` divergence response, full-corpus convergence-failure response

---

## Round 0 — design recap requested by the owner

Before any gray area was selected, the owner asked for a recap of the plan and then for the concrete
wrapper/content output shape. Both were produced from ROADMAP.md, PROJECT.md and live measurement,
not from memory. The recap is preserved in CONTEXT.md's `<specifics>` section (the `manual.typ` /
`bmanual.typ` / `index.typ` sketch and its derived edge sets). No decision was taken in this round.

---

## Round 1 — four candidate gray areas presented, three rejected as non-decisions

Areas offered:

| Area | Description | Selected |
|------|-------------|----------|
| Edge-key granularity and `self`/URL/duplicate handling | Whether `parent>child` alone suffices; `entries` vs `includefiles`; namespacing the `"inc"` state key | |
| Single source of truth for graph input | Whether builder-side and translator-side key derivation can drift, and how to prevent it structurally | |
| Degenerate graph shapes' expected outcomes | The five shapes SC#2 names (≥3 masters, cycle, self, `:glob:`, `:orphan:`) | |
| `:numref:` divergence and corpus-convergence tiers | Pre-written response to SC#5's two measurements | ✓ (split into the two questions below) |

**User's response:** "あんまり議論ポイント無くない？"

**Notes:** The owner was right, and this was accepted rather than argued. The first three areas are
uniquely determined by the already-locked "mirror `inline_all_toctrees`" mandate — there is no
preference to express, only a derivation to record. They were moved into CONTEXT.md's `<decisions>`
as D-03..D-08 (delegated, with the derivation and the supporting measurements written out) rather
than being dropped, because downstream agents need the answer and should not re-derive it. Only the
two measurement-response questions carry a genuine scope choice, and those were re-asked alone.

---

## `:numref:` divergence response (SC#5, open question #2)

| Option | Description | Selected |
|--------|-------------|----------|
| Record and hand to 51/52 | ROADMAP's default wording: record the divergence as a documented limitation, hand to Phase 51 (docs) and Phase 52 (CHANGELOG). Phase 49's work stays measurement + write-up | ✓ |
| Branch on the kind of divergence | Record if numbers merely shift; fix in-phase if body text "Figure N" and the rendered caption number disagree enough to point at a different figure. Thresholds fixed before measuring | |
| Always fix in-phase | Fold the fix into Phase 49 rather than carrying a defect that no compile error catches. Effort unbounded | |

**User's choice:** 記録して 51/52 に渡す
**Notes:** Recorded as D-01. The measurement itself is still mandatory and still on a live two-master
fixture (`pypdf` comparison of Sphinx's baked-in "Figure N" against the Typst-rendered caption number
in each master's PDF) — the decision governs only what happens to the result. A null result (no
divergence) is recorded to the same evidence standard.

---

## Full-corpus convergence-failure response (SC#5, binding constraint #5)

| Option | Description | Selected |
|--------|-------------|----------|
| Stop and escalate to owner | Phase 49 does not close; isolate the minimal failing shape, report it, and let the owner make the design call. Phase 48 D-11's top tier applied to a design risk | ✓ |
| Pre-write three tiers | Reuse D-11's exact three-tier form (record only / record + todo / blocker), thresholds fixed before measuring | |
| Allow a per-shape fallback | Return only the corpus-failing shapes to a write-time decision | |

**User's choice:** 止めて owner に上げる
**Notes:** Recorded as D-02. The third option was presented with its own counter-argument attached
and was not selected: a write-time include decision reintroduces the two-competing-mechanisms shape
Phase 48 spent a whole phase deleting, and brings defect A's failure class back in a second location.
CONTEXT.md states explicitly that executors must not narrow the design to make a convergence failure
go away.

---

## Claude's Discretion

Delegated by the owner in Round 1, with the derivation recorded in CONTEXT.md as D-03..D-08 rather
than left open:

- Iterating `toctreenode['includefiles']` instead of `node['entries']` (D-03)
- Making the guard key unique per emission site rather than a bare docname pair (D-04)
- One shared key-derivation function consumed by both builder and translator (D-05)
- The decided outcome for each of SC#2's five degenerate shapes (D-06)
- Namespacing the Typst `state` key (D-07)
- Keeping today's relative `set heading(offset: heading.offset + 1)` emission unchanged (D-08)

Left genuinely open in CONTEXT.md's "Claude's Discretion" subsection: the literal key spellings, the
choice between walking doctrees and reading `env.toctree_includes`, where the shared function lives,
the RED-recording format, and the internal structure of the published state value.

## Deferred Ideas

- Replacing Phase 48's `query(<L>).len() > 0` guard with a lookup against this phase's published
  include state — Phase 48 D-11 named it as a remediation path only if its top cost tier was hit, and
  `48-EVIDENCE.md` measured the bottom tier. No obligation exists; not this phase's work.

## Measurements taken during discussion

All option descriptions were written from live measurement on the current tree, not recall:

- A probe project whose single toctree contains `self`, `Ext <https://example.com>`, `child`, `child`
  emits `include("self.typ")`, `include("https://example.com.typ")` and one `include("child.typ")`;
  `typst.compile("manual.typ")` aborts with `file not found (searched at .../self.typ)`.
- `sphinx/util/nodes.py:485` iterates `toctreenode['includefiles']`;
  `sphinx/builders/latex/__init__.py:390` and `singlehtml.py:95` seed `traversed` with the master's
  own docname.
- `sphinx/directives/other.py` `TocTree.parse_content`: external URLs and `self` reach `entries`
  only; `:glob:` is expanded to `sorted()` docnames at parse time; `all_docnames` is copied fresh per
  directive invocation, so cross-toctree duplicates in one document are never warned.
- `tests/roots/` contains no `self`, external-URL, cycle or `:glob:` toctree fixture; the Sphinx
  `doc/` corpus (154 `.rst`) contains no `self` or external-URL toctree entry either.
