# Phase 12: High-Volume Independent Node Handlers - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-12
**Phase:** 12-High-Volume Independent Node Handlers
**Areas discussed:** version node appearance & label source, XREF-01 remaining scope & safety, abbr expansion policy, desc_* signature fidelity

---

## Discussion mode

Four phase-specific gray areas were surfaced. The interactive picker (AskUserQuestion) was
presented twice and dismissed both times, then re-presented as a plain-text numbered list with a
Claude recommendation (★) per option. The user replied **"全部おまかせ"** (all up to you), electing
Claude's recommended default for every area. No area was left open.

---

## version node appearance & label source (VER-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Import Sphinx `versionlabels` | Wording follows installed Sphinx + inherits localization | ✓ (★) |
| Hardcode English map in translator.py | Independent, simple, but drifts from Sphinx | |
| Inline HTML-style layout (`*label:* body`) | Matches Sphinx HTML | ✓ (★) |
| Label on its own separate line | Block-style label | |

**User's choice:** all-Claude default → import `versionlabels`; Sphinx-HTML inline layout, unboxed italic.
**Notes:** Import path pinned by researcher; small internal fallback map documented if the symbol
is not importable on the supported Sphinx floor. Directly honors VER-01's "via the versionlabels map".

---

## XREF-01 remaining scope & dangling-label safety

| Option | Description | Selected |
|--------|-------------|----------|
| Safe-side: unresolvable refid → plain text + warn | Avoids Typst label-abort fatal | ✓ (★) |
| Emit link(<refid>) unconditionally | Simpler, risks fatal on dangling label | |

**User's choice:** all-Claude default → safe-side; confirm Phase-11 refid branch already covers
section/`:term:`/`:ref:`, add fixtures, never emit `link("", …)`.
**Notes:** Phase 11 (translator.py:2119) already added a general refid→link branch; Phase 12's
XREF-01 work is confirm-and-cover + fixtures, not a rebuild. Plain-text fallback stays gated on
"both refuri and refid absent" per the requirement; speculative dangling-refid degradation code is
deferred to whatever Phase 15's real corpus proves necessary.

---

## abbr expansion policy (BLK-06)

| Option | Description | Selected |
|--------|-------------|----------|
| Expand on every occurrence | Stateless; PDF has no hover, reader always sees expansion | ✓ (★) |
| Expand first occurrence only | Less repetition, needs a state variable | |

**User's choice:** all-Claude default → every occurrence, stateless.

---

## desc_* signature fidelity (DESC-01…04)

| Option | Description | Selected |
|--------|-------------|----------|
| Faithful to SC, reuse existing desc_* family, context-gated strong() suppression | Minimal new machinery | ✓ (★) |
| Broad new "inline mode" flag | Heavier | |

**User's choice:** all-Claude default → reuse existing `desc_*` visitors; suppress standalone
`strong()` for `desc_inline` via the existing nesting/parent-node signal.
**Notes:** Behaviour is largely locked by ROADMAP SC#3; only the `desc_inline` strong()-suppression
predicate carried real optionality, left as planner/executor discretion.

## Claude's Discretion

- Exact version-label punctuation/spacing and the `versionlabels` import path + fallback shape.
- The predicate distinguishing a standalone declaration from an inline `desc_inline` fragment.
- Fixture contents beyond the explicit success-criteria cases.
- `logger.warning` wording for any dangling-refid degradation, should it prove necessary.

## Deferred Ideas

- BLK-02 / BLK-03 (topic titles, line/line_block) — Phase 13.
- FN-01 (footnotes) — Phase 14.
- GATE-02 (full-corpus validation; where a genuinely-dangling refid would surface) — Phase 15.
- Real graphviz / inheritance_diagram rendering — out of scope for the milestone (Phase 11 settled placeholder-only).
