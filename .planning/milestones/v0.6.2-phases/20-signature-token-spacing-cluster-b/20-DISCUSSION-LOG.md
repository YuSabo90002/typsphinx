# Phase 20: Signature Token Spacing (Cluster B) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-20
**Phase:** 20-Signature Token Spacing (Cluster B)
**Areas discussed:** FID-09 rendering shape, C/C++ fix scope, space kind (wrap behavior), verification depth

---

## FID-09 rendering shape

| Option | Description | Selected |
|--------|-------------|----------|
| Inline + spacing | Keep current inline structure; restore colon-space + field boundary separation. Matches SC#3's pinned target string; minimal blast radius. | ✓ |
| Stacked definition list | Type:/Default: on separate lines, value indented — faithful to `-b html`/`-b text` but a larger structural change, diverges from the SC's inline target. | |

**User's choice:** Inline + spacing (recommended)
**Notes:** SC#3 explicitly pins the inline target `"Type: int (a number)  Default: 42"`, so
inline-with-spacing IS the acceptance bar (not an under-delivery). Contrast with Phase 19
D-01/D-02 where no SC pinned an inline form and the HTML-faithful block form won.

---

## C/C++ fix scope

| Option | Description | Selected |
|--------|-------------|----------|
| All audited forms | Fix every audited C/C++ inter-token form (`*`/`&`, type↔id, keyword prefix, `a * f(a)` operators, `const…*`, `template<typename T…>`). | ✓ |
| Space-node subset only | Fix only `desc_sig_space`-backed cases; defer rare operator/template forms to Phase 21. | |

**User's choice:** All audited forms (recommended)
**Notes:** SC#2 literally requires "preserve **all** inter-token spaces." If the root fix lands
at the shared `desc_sig_space` handler, most forms are covered uniformly at low cost. A
completeness check for non-space-node forms (`desc_sig_operator`/`desc_sig_punctuation`) is
required during research (CONTEXT D-08 discretion).

---

## Space kind (wrap behavior)

| Option | Description | Selected |
|--------|-------------|----------|
| Normal breakable space | `-b html` authority wraps signatures naturally; minimal blast radius; overflow is Cluster C's job (FID-10/Phase 21). | ✓ |
| Non-breaking space | Keep each signature on one line; risks re-introducing right-margin overflow this milestone fixes elsewhere. | |

**User's choice:** Normal breakable space (recommended)
**Notes:** Non-breaking would pre-empt Cluster C and risk introducing margin overflow on long
C/C++ signatures. Restore the natural space HTML uses.

---

## Verification depth

| Option | Description | Selected |
|--------|-------------|----------|
| D-05 + pypdf adjacency (required) | Structural `.typ` token assert (D-05 floor) PLUS required pypdf extracted-text adjacency assert ("class sphinx" present / "classsphinx" absent). | ✓ |
| D-05 baseline only | Structural `.typ` assert + real %PDF only, as in Phase 19. | |

**User's choice:** D-05 + pypdf adjacency required (recommended)
**Notes:** Cluster B is *horizontal* spacing, which pypdf CAN detect in extracted text — unlike
Phase 19's *vertical* spacing (not extractable, so pypdf was rejected there, D-06). The
adjacency assert is therefore cheap AND meaningful here and directly proves rendered-glyph
fidelity. Confirm pypdf is already a dev dependency before requiring it in a gate.

---

## Claude's Discretion

- Exact space-emission token (`text(" ")` vs `+ text(" ") +` vs `sym.space`/`~`) and its
  concat-context awareness — research/planning to settle against real compiles.
- Shared-idiom structure (Phase 19 D-03 reaffirmed as default) — one small shared space-emission
  idiom vs per-finding edits; FID-09 colon-space may stay separate as a distinct mechanism.
- Fixture granularity/placement — default one gate module per finding, extending existing
  modules; consolidation allowed if each finding retains a pre-fix-failing assertion.

## Deferred Ideas

- Stacked definition-list rendering for FID-09 fields — future fidelity enhancement if inline proves insufficient.
- Non-breaking-space signature cohesion — belongs to the Cluster C margin discussion (FID-10, Phase 21).
- Cluster C (FID-10) → Phase 21; Clusters D/E/F (FID-11..FID-14) → Phase 21; Issue #117 (PDF-01) → Phase 22.
