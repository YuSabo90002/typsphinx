---
created: 2026-08-01
source: Phase 37 code review (37-REVIEW.md, WR-01)
area: translator
severity: warning
resolves_phase: 38
---

# `_desc_break_marker` goes stale across every `self.body` buffer swap except `in_table`

## What

Phase 37's SIG-08 fix (`typsphinx/translator.py`, `depart_desc` ~4851) suppresses a duplicate
`parbreak()` by comparing a recorded emission position against the live buffer length:

```python
if not self.in_table and self._desc_break_marker == len(self.body):
    return
self._desc_break_marker = len(self.body)
```

`len(self.body)` is an index into *whichever list `self.body` currently points at*. The `in_table`
guard exists because `add_text` routes into `table_cell_content` rather than `self.body` inside a
table — but that is only ONE of the translator's buffer-swap mechanisms. Verified 2026-08-01 by
grep, `self.body` is also reassigned at:

- `visit_term` / `depart_term` (~2150, ~2188) — via `_saved_body_stack`
- `visit_definition` / `depart_definition` (~2212, ~2239) — via `_saved_body_stack`
- admonition title (~591, ~652) — via `_saved_body_for_admonition_title`
- figure caption (~2383) — via `_saved_body_for_figure_caption`

If `self.body` is swapped between the two `depart_desc` calls the marker is compared against, the
comparison is meaningless: the recorded integer indexes a different list. It can spuriously match
(suppressing a break that was needed) or spuriously fail to match (emitting the doubled break
SIG-08 exists to remove).

## Why it matters

The concrete reachable case is an object-description directive nested inside a glossary definition
— legal reStructuredText, and the `_saved_body_stack` machinery exists precisely because that
nesting happens (bug #18's comment names it). Low real-world frequency, which is why Phase 37's
fixtures did not surface it, but it is a genuine hole in the new state machine rather than a
theoretical one.

## How to apply

Do **not** patch this without a GATE-01 fixture. The project's standing bar (STATE.md, since
v0.6.0) requires every node-handler change to ship a real `sphinx-build → typst.compile()`
regression fixture recorded **red against the unfixed code** before it is accepted as green. So:

1. Build a fixture with a `desc` nested inside a glossary definition (and a second with a nested
   `desc` inside that), drive it through `-b typst`, and assert the `parbreak()` count.
2. Record it RED against the current tree.
3. Then choose the fix. The likely shape is to make the marker identify the *buffer* as well as the
   position — e.g. record `(id(self.body), len(self.body))` — rather than adding a second
   special-case guard per swap site, since the `in_table` guard already shows that per-site guards
   do not generalise.

Related: [[gsd-execute-worktrees-unsafe-editable-install]] for how to run the fixture in an
isolated worktree.

## Resolved

Filed to `completed/` by Phase 41 (`.planning/phases/41-v0-7-0-release-automation-release-prep/`,
2026-08-03). Phase 41 files this record; the fix itself landed in an earlier phase (Phase 38,
per `resolves_phase: 38` above), not in Phase 41.

Re-verified in this worktree (commit range through `c81ca29`), by grep against
`typsphinx/translator.py`:

- `self._desc_break_marker: tuple[int, int] | None = None` — initialized at line 261, confirming
  the marker's shape is a 2-tuple, not a bare int.
- `depart_desc` (~line 5542-5548):
  ```python
  if not self.in_table and self._desc_break_marker == (
      id(self.body),
      len(self.body),
  ):
      return
  self._emit_forced_break("parbreak()")
  self._desc_break_marker = (id(self.body), len(self.body))
  ```
  Both the comparison (line 5542) and the reassignment (line 5548) use the `(id(self.body),
  len(self.body))` tuple shape.
- The second comparison/assignment site (~line 5885-5891):
  ```python
  marker_was_untouched = not self.in_table and self._desc_break_marker == (
      id(self.body),
      len(self.body),
  )
  self.add_text("})\n")
  if marker_was_untouched:
      self._desc_break_marker = (id(self.body), len(self.body))
  ```
  Same tuple shape at both the comparison (line 5885) and the reassignment (line 5891).

All three sites (init + two comparison/assignment pairs) carry the `(id(self.body),
len(self.body))` shape the "How to apply" section above proposed. The fix is in place; no code
change was made by Phase 41 for this item.
