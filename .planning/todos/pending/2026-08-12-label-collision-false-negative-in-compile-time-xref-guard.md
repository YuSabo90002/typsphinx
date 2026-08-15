---
created: 2026-08-12T15:22:16+09:00
title: Label-collision false negative in the compile-time cross-reference guard — a reference whose real target is absent can render as a working link to a same-spelled decoy
area: translator
resolves_phase: 55
severity: minor
files:
  - typsphinx/translator.py  # TypstTranslator._label_existence_guard()
  - tests/fixtures/xref_label_collision_guard_gate/
---

## Problem

Phase 48's compile-time cross-reference guard (`_label_existence_guard()`) decides whether a
cross-document reference's target exists by asking Typst `query(<label>).len() > 0` inside the
compiling wrapper — "does a label with THIS SPELLING exist in this compile," not "does the
document I meant exist." Labels are namespaced `docname:id` via `_namespace_label`, and
`_sanitize_label` maps every character invalid in a Typst label to a distinct `_u{codepoint:x}_`
token — including `/` → `_u2f_`. That narrowing means two *different* docnames can sanitize to the
*same* label string if one docname literally contains the substring that another docname's `/`
transform produces: `a/b` (docname `a/b`, label id `nested-target` → `a_u2f_b:nested-target`) and
`a_u2f_b` (docname `a_u2f_b`, label id `nested-target` → `a_u2f_b:nested-target`) collide.

Measured in `48-EVIDENCE.md`'s "## Accepted limit — label-collision false negative" section against
`tests/fixtures/xref_label_collision_guard_gate/`: a reference whose real target (`a/b`) is absent
from the compiling master renders as a WORKING link to the wrong, included decoy (`a_u2f_b`)
instead of degrading to plain text — because the guard's `query()` finds the decoy's
identically-spelled label and cannot tell the two apart.

This is a genuinely new false-negative class introduced by this phase. The build-time mechanism
this phase deleted checked *docname membership* (was the target's docname in the reachable set),
which does not have this collision — two distinct docnames are never equal as strings unless they
already collide as raw docnames, which Sphinx itself would reject earlier. The compile-time guard
checks *label existence* instead, which is the source of the new class.

It is narrow: it requires the DOCNAME segment specifically to collide, realistically only via the
`/` → `_u2f_` sanitization transform (a directory-nested docname colliding with a top-level docname
whose name happens to spell out the sanitized form of some other docname's path). It is
characterized by a real, committed compile in `tests/fixtures/xref_label_collision_guard_gate/`
and `tests/test_xref_compile_time_guard_render_gate.py -k collision`, not merely argued.

Recorded as ACCEPTED for Phase 48 (owner sign-off item in `48-04-PLAN.md`'s human-check).

## Solution

The one obvious remediation direction: carry the target DOCNAME into the guard's decision, not
rely on label spelling alone. Concretely, this likely means widening the guard's query to also
confirm the queried element's own docname (via a Typst-side metadata/label-content check, or a
Typst `label()` value carrying the docname as structured data rather than folding it into the
label string) matches the reference's intended target docname — closing the gap between "a label
with this spelling exists" and "the document I actually meant is present." No such Typst-side
mechanism was designed or measured during Phase 48; this is a direction, not a spec.
