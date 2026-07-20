# Phase 19: Block Separation Fixes (Cluster A) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-20
**Phase:** 19-Block Separation Fixes (Cluster A)
**Areas discussed:** Fidelity target level, Separator-fix structure, Verification strategy

---

## Area selection (multiSelect)

| Gray area | Description | Selected |
|-----------|-------------|----------|
| Fidelity target level | Match `-b html` full block spacing vs minimum anti-collision | ✓ |
| Shared primitive vs point-fixes | One shared separator helper vs 5 independent edits | ✓ |
| Visual separation verification | How a GATE-01 fixture "fails without the fix" for a non-fatal visual bug | ✓ |
| Fixture granularity/placement | Per-finding vs combined; new vs extend existing modules | (not selected → Claude's discretion) |

---

## Fidelity target level

| Option | Description | Selected |
|--------|-------------|----------|
| HTML-conformant (break kind per construct) | Match the break kind HTML renders for each construct: paragraph→parbreak, sibling signature→linebreak, rubric/term→own line, body-less confval→block separation. Aligns with ROADMAP goal. | ✓ |
| Minimum anti-collision (uniform light break) | One uniform light break/space everywhere; just prevent token collision. Smaller but diverges from HTML block structure; risks under-delivering FID "visible separation". | |

**User's choice:** HTML-conformant (break kind selected per construct)
**Notes:** ROADMAP goal is explicit ("renders with the visible separation the `-b html` authority shows"), so per-construct HTML matching is the target, not a uniform minimal break.

---

## Separator-fix structure

| Option | Description | Selected |
|--------|-------------|----------|
| Shared helper + per-site break kind | One small helper respecting `list_item_needs_separator`, emitting the caller-supplied `parbreak()`/`linebreak()`; reused at all 5 sites, break kind chosen per site. Matches ROADMAP "small shared set"; explicit blast radius; foundation for Phase 20. | ✓ |
| Fully independent 5-point fixes | Each handler implements its own break, zero sharing. Smallest per-edit blast radius but inconsistency/duplication risk and idiom drift for Phase 20. | |

**User's choice:** Shared helper + per-site break kind
**Notes:** Also implicitly rejected a single monolithic primitive emitting an identical break everywhere — break kind genuinely varies by construct (see fidelity decision), so one-size does not fit and carries the largest corpus-gate blast radius.

---

## Verification strategy (GATE-01)

| Option | Description | Selected |
|--------|-------------|----------|
| `.typ` structural assert + real compile | Assert generated `.typ` contains expected separator token (parbreak/linebreak) at the right site + real `typst.compile()` → `%PDF`. Deterministic, fast, network-free; pre-fix has only cosmetic `\n` so token absent = fails. Mirrors `test_desc_signature_concat_render_gate.py`. | ✓ |
| Above + pypdf text-extraction on flagship cases | Add pypdf extracted-text adjacency check (e.g. absence of "role.For") for F1/F13/F15. Stronger evidence but cannot detect paragraph vertical spacing. | |
| Rasterize and check glyph position/line count | Most direct but poppler-dependent, brittle, slow, inconsistent with other milestone gates. | |

**User's choice:** `.typ` structural assert + real compile
**Notes:** Lightweight/deterministic path chosen. pypdf remains an optional planner strengthening for observable cases; rasterize rejected for the milestone.

---

## Claude's Discretion

- **Fixture granularity/placement** (4th gray area, not selected): default to one render-gate
  fixture per finding — extend existing `test_desc_signature_concat_render_gate.py` (F7) and
  `test_deflist_term_concat_render_gate.py` (F14); new modules for F1/F13/F15 — per the repo's
  "one gate module = one concern" convention. Planner may consolidate if a shared fixture
  cleanly exercises multiple findings while each retains a pre-fix-failing assertion.
- **Exact break-token emission per site** (`parbreak()` vs `linebreak()` vs `par()`-wrap and its
  interaction with the list-item `{ }` block): intent fixed by the fidelity decision; precise
  Typst emission left to research/planning against real compiles.

## Deferred Ideas

- pypdf extracted-text adjacency assertions as an optional strengthening (F1/F13/F15).
- Rasterized glyph-position verification (rejected this milestone).
- Cluster B (Phase 20), Clusters C/D/E/F (Phase 21), Issue #117 PDF naming (Phase 22) — out of
  Phase 19 scope. No scope-creep ideas surfaced.
