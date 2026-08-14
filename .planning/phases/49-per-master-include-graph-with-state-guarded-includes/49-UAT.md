---
status: complete
phase: 49-per-master-include-graph-with-state-guarded-includes
source: [49-VERIFICATION.md]
started: 2026-08-14T20:20:00Z
updated: 2026-08-14T20:07:03+09:00
---

## Current Test

[testing complete]

## Tests

### 1. Decide disposition of code-review WR-01 — edge-key separator collision

`make_include_edge_key` builds `f"{parent}#{occurrence}>{child}"` and routes each component
through `escape_typst_string`, which escapes `\`, `"`, newlines and tabs — but not the structural
separators `#` and `>` themselves. Reproduced independently by both the orchestrator and the
verifier:

    make_include_edge_key('a',     'b#1>c', occurrence=0)  ->  'a#0>b#1>c'
    make_include_edge_key('a#0>b', 'c',     occurrence=1)  ->  'a#0>b#1>c'

A docname containing a literal `#` or `>` (legal on POSIX filesystems) can therefore collide two
structurally different include edges onto one key, firing a guard for the wrong edge with zero
diagnostic at any layer.

Why this needs a human: no stated Success Criterion and no requirement (COMP-05..COMP-12)
exercises a docname containing `#` or `>`, so this does not FAIL anything the roadmap contracted
for. But it is the same defect CLASS — silent mis-inclusion with no error and no warning — that
this phase's own prohibitions forbid trading one instance of for another. Fix-vs-track is an owner
judgment call.

expected: Fixed in this phase, or filed as a tracked pending todo before the phase ships.
result: pass
reason: |
  Owner chose TRACK, not fix (2026-08-14) — the "filed as a tracked pending todo" branch of the
  stated expectation, so the expectation is MET. Filed as
  `.planning/todos/pending/2026-08-14-include-edge-key-separators-unescaped-two-edges-can-collide.md`
  (`resolves_phase: null`, severity minor), carrying the reproduction, three candidate fixes, and the
  binding-constraint-#4 requirement to write the RED first.

### 2. Decide disposition of code-review WR-02 — unbounded recursion in the traversal

`derive_master_edge_keys`'s nested `walk()` recurses with no depth guard. A sufficiently deep or
long linear include chain raises an uncaught `RecursionError`, crashing the whole Sphinx build with
a raw Python traceback rather than a controlled `ExtensionError` naming the offending chain.

Why this needs a human: same reasoning as WR-01 — no SC or requirement exercises a chain anywhere
near Python's default recursion limit (1000), so nothing stated is FAILED, but it is an unhandled
crash path introduced by this phase's own new traversal function and it is currently untracked.

expected: Fixed (iterative traversal, or a guarded limit raising an actionable error), or filed as
a tracked pending todo before the phase ships.
result: pass
reason: |
  Owner chose TRACK, not fix (2026-08-14) — the "filed as a tracked pending todo" branch of the
  stated expectation, so the expectation is MET. Filed as
  `.planning/todos/pending/2026-08-14-unbounded-recursion-in-derive-master-edge-keys.md`
  (`resolves_phase: null`, severity minor), noting that the recursion shape itself is deliberate
  (a LIFO work-stack reverses sibling order and is a named forbidden shape) so the fix is a bound,
  not a rewrite.

## Summary

total: 2
passed: 2
issues: 0
pending: 0
skipped: 0
blocked: 0

Both items were disposition decisions rather than manual tests. The owner's decision (2026-08-14)
was to TRACK both rather than fix either inside Phase 49: neither fails a stated Success Criterion
or requirement, and neither is reachable without an unusual input (a docname containing a literal
`#`/`>` for WR-01; an include chain near Python's 1000-frame recursion limit for WR-02).

## Gaps

None. Both human-verification items are dispositioned and tracked.
