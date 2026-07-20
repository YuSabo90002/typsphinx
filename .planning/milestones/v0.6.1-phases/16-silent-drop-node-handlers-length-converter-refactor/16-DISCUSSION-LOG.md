# Phase 16: Silent-Drop Node Handlers + Length-Converter Refactor - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-13
**Phase:** 16-silent-drop-node-handlers-length-converter-refactor
**Areas discussed:** todo_node styling, manpage styling, LEN-01 scope

---

## todo_node styling

| Option | Description | Selected |
|--------|-------------|----------|
| task + "Todo" | gentle-clues `task` clue (checkbox/work icon) with custom_title="Todo"; closest semantic match | ✓ |
| generic clue + "Todo" | base `clue` (no icon/accent) with custom_title="Todo"; most neutral; the `task`-absent fallback | |
| info + "Todo" | same `info` clue as note; look matches existing admonitions but hard to distinguish from note | |

**User's choice:** task + "Todo"
**Notes:** Locked as `_visit_admonition(node, "task", custom_title="Todo")`. Fallback to generic
`clue` if gentle-clues 1.3.1 has no `task` clue (researcher to verify). `todolist` node out of scope.

---

## manpage styling

| Option | Description | Selected |
|--------|-------------|----------|
| emph (italic) | `#emph[ls(1)]`; matches Sphinx HTML `<em class=manpage>` + LaTeX italic | ✓ |
| plain text (no-op) | visit/depart no-op, Text child passes through; minimal but loses manpage distinction | |
| monospace (`raw`) | `raw("ls(1)")` since it's a command; diverges from Sphinx's italic rendering | |

**User's choice:** emph (italic), matching Sphinx
**Notes:** User first asked what the `:manpage:` role is for; after clarification (Unix man-page
reference, `name(section)`, italic in Sphinx HTML/LaTeX) chose emph to stay Sphinx-faithful.
No `manpages_url` linkification (out of scope).

---

## LEN-01 scope

| Option | Description | Selected |
|--------|-------------|----------|
| Audit + wire every length-bearing site | Researcher audits all CSS-length-bearing nodes (figure figwidth, table width, etc.) and routes each through the shared helper; satisfies SC#3 literally | ✓ |
| image-only formalization | Only formalize the existing helper; wire no new sites (they'd arguably be new capability) | |

**User's choice:** Audit + wire every length-bearing site (積極派)
**Notes:** User asked to clarify the scope-creep concern before deciding. Agreed boundary captured in
CONTEXT.md D-03a: sites currently emitting an un-/mis-converted length → route through helper;
sites currently ignoring the length entirely → wire in, because SC#3 mandates "every length-bearing
site" (this wiring IS the requirement, not scope creep). Single-source invariant (no duplicated
conversion) preserved (D-03b).

---

## Claude's Discretion

- Exact `emph` wrapper punctuation/whitespace for manpage.
- Precise audit order and per-site wiring shape for LEN-01 (single-source invariant must hold).
- Fixture document contents beyond the explicit SC cases.
- `logger.warning` wording for unsupported-unit drops at newly-wired sites.

## Deferred Ideas

- `todolist` (`.. todolist::`) node handling — future fidelity phase if needed.
- `manpages_url` linkification of `:manpage:` — separate Sphinx feature.
