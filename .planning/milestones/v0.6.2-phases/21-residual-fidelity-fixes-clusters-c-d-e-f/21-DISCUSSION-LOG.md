# Phase 21: Residual Fidelity Fixes (Clusters C/D/E/F) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-20
**Phase:** 21-Residual Fidelity Fixes (Clusters C/D/E/F)
**Areas discussed:** FID-13 link styling, FID-10 wrapping behavior, Verification strategy (GATE-01)

---

## Gray-area selection (multiSelect)

| Option | Description | Selected |
|--------|-------------|----------|
| FID-13 link styling | Visual treatment distinguishing external hyperlinks + boundary spacing | ✓ |
| FID-14 abbr expansion scope | Narrow (`*`/`/` only) vs broad (all abbreviations) | |
| FID-10 wrapping behavior | Token-boundary vs mid-token break; shared overflow primitive vs isolated | ✓ |
| Verification strategy (GATE-01) | pypdf adjacency vs structural `.typ`-only, per finding | ✓ |

**User's choice:** FID-13, FID-10, Verification. FID-14 left to SC-driven default (narrow scope).

---

## FID-13 — external link styling

### Q1 — visual treatment
| Option | Description | Selected |
|--------|-------------|----------|
| Color only | Color the link body (blue/teal); web+PDF-viewer convention | |
| Color + underline | Color plus underline; strongest link affordance | ✓ |
| Underline only | Underline, no color | |

**User's choice:** Color + underline — AND (elaborated in free text) the translator keeps emitting
`link()`, the appearance is delegated to a `show` rule in Typst's default template; i.e. edit the
default `base.typ`. This single answer resolved both the visual-treatment and the
implementation-location question (a separate location question had been drafted; the user asked to
return to Q1 and answered both at once — the drafted location question was withdrawn).
**Notes:** Template-delegated styling deliberately relaxes the phase's "translator-only" default
for FID-13's styling half.

### Q2 — scope of the `show link:` rule
| Option | Description | Selected |
|--------|-------------|----------|
| External URLs only | `it.dest` is a string → style; internal cross-refs unchanged | ✓ |
| All links uniformly | External + internal styled the same | |

**User's choice:** External URLs only.
**Notes:** Finding is external-only; the show rule distinguishes external vs internal by `it.dest`
type, so internal cross-refs avoid print noise.

---

## FID-10 — inline-literal wrapping

The initial behavior question was interrupted twice for clarification. The user asked to clarify
the root cause (item ①). Codebase investigation confirmed: each inline literal → `raw("…")`; the
Phase 18 F12 ZWSP break-point primitive already exists but is explicitly gated to `self.in_table`
(`translator.py:1224-1236`, "F6 out of scope"); FID-10 is precisely the prose case lacking that
safety net. This linked the "wrapping behavior" and "shared primitive" questions into a single
choice.

| Option | Description | Selected |
|--------|-------------|----------|
| Boundary-only fix | Make inter-literal spaces breakable; never break inside a role token; keep table ZWSP primitive isolated (kinship-note recommended) | ✓ |
| Reuse table primitive for prose | Also extend the `in_table` ZWSP primitive to prose; breaks even a single long token; broader blast radius, needs table-regression re-verify | |

**User's choice:** Boundary-only fix.
**Notes:** Honors the catalogue kinship note (F6 ≠ F12, don't conflate). Escape hatch recorded
(D-06): if a real compile shows boundary-only is insufficient, escalate rather than under-deliver.

---

## Verification strategy (GATE-01)

The user observed that the only genuinely problematic finding for verification is FID-11 (the
others' symptoms manifest directly in extracted text, so pypdf applicability is self-evident). The
FID-11 mechanism was confirmed at the `.typ` level: `visit_Text` → `escape_typst_string` turns an
intra-paragraph `\n` into a `\\n` escape which Typst decodes to a forced break — so a structural
`.typ` assert (no intra-paragraph `\n` escape post-fix) is deterministic and pypdf is unnecessary.

| Option | Description | Selected |
|--------|-------------|----------|
| FID-11 = Phase19 family (structural only); others = Phase20 family (pypdf) | FID-11 structural `.typ` assert + real compile, no pypdf; FID-10/12/13-boundary/14 add pypdf adjacency assert; FID-13-styling = show-rule structural assert | ✓ |
| FID-11 also tries pypdf | Add best-effort pypdf line-join assert for FID-11 too | |

**User's choice:** This classification confirmed.
**Notes:** Consistent with Phase 19 (pypdf rejected for non-extractable vertical/layout spacing)
and Phase 20 (pypdf required for extractable horizontal spacing).

---

## Claude's Discretion

- **FID-11** — mechanical: collapse intra-paragraph soft newlines to a single space in
  `visit_Text` (paragraph text only; not `in_literal_block`, not inline `raw()`, not explicit hard
  breaks). Mechanism confirmed in code.
- **FID-12** — pure bug fix: correct the `in_markup_context`/`codly_prefix` guard
  (`translator.py:1582`) so the captioned + list-item combined case no longer leaks the codly
  config wrapper.
- **FID-14** — narrow scope (SC#4-driven): suppress inline abbr-title injection only for the
  auto-generated `*` (PEP 3102) / `/` (PEP 570) separators; genuine `:abbr:` roles keep inline
  expansion (print has no hover). Broad suppression rejected.
- Per-finding fixture structure (these five findings are genuinely independent — no shared root
  cause); planner may consolidate provided each finding retains a pre-fix-failing assertion.

## Deferred Ideas

- Styling internal cross-references — deliberately not done (external-only per D-02).
- Extending the table ZWSP primitive to prose / a shared right-margin-overflow primitive —
  rejected (D-05), revisit only via the D-06 escape hatch.
- Broad abbr-title suppression across all `abbreviation` nodes — rejected (D-Disc-3).
- Issue #117 PDF naming (PDF-01) → Phase 22; Release phase (version bump + CHANGELOG) → final
  milestone phase.
