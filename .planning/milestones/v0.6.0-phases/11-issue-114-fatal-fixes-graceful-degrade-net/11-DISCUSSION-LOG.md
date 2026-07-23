# Phase 11: Issue #114 Fatal Fixes + Graceful-Degrade Net - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-11
**Phase:** 11-Issue #114 Fatal Fixes + Graceful-Degrade Net
**Areas discussed:** Graceful-degrade appearance, Length-unit fallback, `:target:` coverage, Acceptance-gate strictness

---

## Graceful-degrade appearance (DEG-01 / DEG-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Visible placeholder + one warning | Bordered block naming the node (e.g. `[graphviz diagram omitted]`) + one `logger.warning`; matches REQ DEG-01 "visible placeholder block" | ✓ |
| Reuse gentle-clues warning box | Render via existing `_visit_admonition` helper; visually confusable with real admonitions | |
| Silent skip + log only | Nothing in the PDF; `SkipNode` + `logger.warning`; satisfies roadmap SC#3 but not the "visible" wording | |

**User's choice:** Visible placeholder + one warning.
**Notes:** Reader must be able to tell a diagram was there; stronger than roadmap SC#3 minimum. No gentle-clues reuse, no raw DOT leak; DEG-01/02 share one helper.

---

## Length-unit fallback (FIG-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Unitless = px, unknown = warn-and-drop | Unitless treated as px (×0.75pt per HTML/CSS); unknown/unconvertible units (incl. `ex`) warned and dimension dropped (natural size); `pc`→`pt` | ✓ |
| Unitless = pt direct, unknown = warn-and-drop | Unitless treated as pt (no ×0.75); simpler but diverges from CSS convention | |

**User's choice:** Unitless = px, unknown = warn-and-drop.
**Notes:** `px`→`pt` = 0.75 confirmed. Never emit a raw unsupported unit. Centralize in `_convert_length_to_typst()`.

---

## `:target:` coverage (FIG-02)

| Option | Description | Selected |
|--------|-------------|----------|
| External URL + internal reference | Handle both `link("url")` and `link(<label>)` via the same buffer-swap path (branch refuri vs refid) | ✓ |
| External URL only | Fix just the Issue #114 external-URL reproduction; internal refs deferred | |

**User's choice:** External URL + internal reference.
**Notes:** Small added cost on the shared code path; Sphinx's own `doc/` corpus uses internal `:target:` refs heavily.

---

## Acceptance-gate strictness (GATE-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Runs in CI `cov` job, effectively required | Keep `slow` marker for local speed, but must not `skip` in CI (typst-py/pypdf present) and fails loudly on `TypstCompilationError` | ✓ |
| Skippable optional gate as before | Rely on docs.yml/drift.yml `docs-pdf` real compile; leave the fixture skippable | |

**User's choice:** Runs in CI `cov` job, effectively required.
**Notes:** Aligns with the milestone thesis that string-agreement tests alone are insufficient (pitfall #9). Extends `tests/test_pdf_render_gate.py`; standing bar for Phases 12–14.

---

## Claude's Discretion

- Exact placeholder-block styling (border/padding/wording) — reader must recognize an omitted diagram.
- Exact `logger.warning` message text (must name the node type).
- Internal structure of `_convert_length_to_typst()` and the shared DEG helper.
- Fixture document contents beyond the explicit success-criteria cases.

## Deferred Ideas

- Real `graphviz` / `inheritance_diagram` rendering (shell out to `dot`) — Out of Scope this milestone.
- LEN-01 — generalize the length converter beyond named units — Future Requirement.
- VER-01 / XREF-01 / DESC-* / BLK-* / FN-01 — Phases 12–14.
