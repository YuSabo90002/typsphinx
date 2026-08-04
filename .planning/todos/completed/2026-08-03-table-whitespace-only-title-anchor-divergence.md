---
created: 2026-08-03T23:26:31+09:00
title: A captioned table whose title renders to an empty string may anchor its ids on neither the visit nor the depart path, leaving a dangling reference
area: translator
resolves_phase: 43
roadmap_entry: null
source: "Phase 42 / D-08 (2026-08-03) -- captioned-table-drops-preceding-target-label"
files:
  - typsphinx/translator.py (`visit_table` at line 3149 -- the structural captioned pre-check, `is_captioned = bool(node.children) and isinstance(node.children[0], nodes.title)`, line 3173)
  - typsphinx/translator.py (`visit_title` at line 613 -- the `self.in_table` branch at line 663 that buffers a table caption's title into `table_cell_content` via `self._in_table_caption`)
  - typsphinx/translator.py (`depart_title` at line 735 -- the `_in_table_caption` consumer at lines 753-760, which assigns `self.table_caption = "".join(self.table_cell_content).strip()`)
  - typsphinx/translator.py (`depart_table` at line 3249 -- the truthiness check `if self.table_caption:` at line 3304)
---

## Problem

`visit_table` and `depart_table` decide "is this table captioned?" on two DIFFERENT axes, and
those axes can disagree.

`visit_table` decides it STRUCTURALLY, at line 3173: `is_captioned = bool(node.children) and
isinstance(node.children[0], nodes.title)` — is the table's first child a `title` node at all?
When `is_captioned` is `True`, `visit_table` skips its own unconditional `_emit_id_anchors(node)`
call (line 3175), deferring anchoring entirely to `depart_table`'s captioned branch (see
`42-GATE-EVIDENCE-03.md` §1.5, the `depart_table` MISROUTED row this same phase's fix, plan
42-04, addresses).

`depart_table` decides the same question by TRUTHINESS, at line 3304: `if self.table_caption:`.
`self.table_caption` is assigned by `depart_title`'s `_in_table_caption` consumer (lines 753-760)
from the JOINED, STRIPPED `table_cell_content` buffer that `visit_title`'s `self.in_table` branch
(line 663-672) collected while visiting the title's children. A table whose title node renders to
the empty string after stripping — whitespace-only content, or content that strips to nothing —
produces `self.table_caption == ""`, which is falsy.

**The two axes disagree for a table that HAS a title node whose rendered content strips to the
empty string.** The visit side (`is_captioned`, structural) treats it as captioned and skips the
unconditional anchor call. The depart side (`self.table_caption`, truthiness) treats it as
caption-less and takes the `else:` branch (line 3342), which never calls `_emit_id_anchors` at
all — that call lives only inside the `if self.table_caption:` branch (line 3341, itself the
MISROUTED site plan 42-04 fixes). **The table's ids are anchored on NEITHER path.** Any reference
to a propagated target on such a table — the exact TBL-03 shape, reached by a different route —
dangles, and `typst.compile()` aborts the whole document at the semantic label-resolution pass.

## Status

Filed by Phase 42 per D-08, deliberately NOT fixed there. The phase's scope fence (D-05) was a
call-ordering change inside the table departure handler only — moving WHERE
`_emit_id_anchors` fires relative to `self.in_table`'s clear, touching no other logic. Changing
either captioned check (making `visit_table`'s structural test match `depart_table`'s truthiness
test, or vice versa) is a semantics change to WHICH tables count as "captioned" at all — outside
that fence, and outside D-06's narrower "sweep everywhere, but only an image-path finding is fixed
inside this phase" condition (this is a non-image finding by construction: it lives entirely in
the table path).

## Solution

Breadcrumbs only — explicitly NOT a diagnosis. The next investigator should start from
reachability, not from a fix shape.

**The probe already run (2026-08-03, Phase 42 research session):** a literal trailing-whitespace
`.. table:: ` directive argument. docutils produced **NO title child at all** for that input —
`is_captioned` (the structural check) returned `False`, so the table took the non-captioned path
and anchored correctly. This is a data point **AGAINST reachability**, but it is **NOT a proof of
unreachability** for every possible construct. Do not re-run this exact probe; it has already been
run and its result is recorded here.

**Untested constructs the next investigator should start from instead** (at least two, per this
todo's acceptance list below):

1. **Substitution references** (`.. |name| replace:: ...`) inside a `.. table::` title argument —
   docutils resolves these during a transform pass; whether a substitution that itself expands to
   empty (or whitespace-only) content produces a genuinely-present-but-empty-rendering `title`
   node (as opposed to no title node at all, which is what the trailing-whitespace probe found) is
   unverified.
2. **The `replace` directive**, or other title-producing constructs that build a `title` node
   programmatically rather than from a literal argument string — these may not go through the same
   docutils argument-parsing path the trailing-whitespace probe exercised, so the "no title child
   at all" outcome measured there may not generalize.
3. **Raw markup** (`.. raw:: html` or similar) inside a table title context, if docutils' grammar
   even permits it there — untested whether this could yield a `title` node whose `astext()`/
   rendered-child content strips to empty while the node itself still exists in `node.children[0]`.

Whichever construct (if any) reaches the divergent state, the fix shape is also unresolved: it
could mean making `depart_table`'s truthiness check match `visit_table`'s structural check (treat
"has a title node" as authoritative regardless of rendered content), or the reverse (make
`visit_table`'s pre-check also test renderability, not just node type) — this todo takes no
position on which axis should win.

## Acceptance

- [ ] Determine whether any rST construct can produce a table `title` node whose rendered content
      strips to the empty string (start from substitution references, the `replace` directive, or
      raw markup — see Solution above; do not re-run the trailing-whitespace `.. table:: ` probe,
      already measured negative)
- [ ] If reachable: decide which axis (`visit_table`'s structural check or `depart_table`'s
      truthiness check) is authoritative, and align the two checks so the table's ids are anchored
      on at least one path
- [ ] If unreachable: close this todo, recording the reachability evidence (the constructs tried
      and their outcomes) rather than leaving the question open indefinitely
