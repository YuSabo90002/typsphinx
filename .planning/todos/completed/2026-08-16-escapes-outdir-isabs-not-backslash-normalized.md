---
created: 2026-08-16
title: "`_escapes_outdir()` normalizes backslashes for its parent-traversal split but calls `posixpath.isabs()` on the RAW stem for its absolute-path branch -- it returns False for a driveless-absolute Windows stem"
area: builder
resolves_phase: 59
severity: minor
source: Phase 55 plan 55-03, filed while closing BLD-09; measured in
  .planning/phases/55-v0-8-0-derived-defects/55-03-RED-EVIDENCE.md
  §"Predicate measurement" ("_escapes_outdir(driveless-absolute stem) = False")
files:
  - typsphinx/builder.py  # _escapes_outdir() -- posixpath.isabs(stem) called on the raw stem
  - typsphinx/builder.py  # _is_absolute_image_uri() -- the sibling BLD-09 fixed, normalizing first
---

## Problem

`_escapes_outdir()` (`typsphinx/builder.py`) normalizes backslashes for its own
parent-traversal (`..`) split — `stem.replace("\\", "/").split("/")` — but its absolute-path
branch calls `posixpath.isabs(stem)` on the **raw, un-normalized** `stem`, not on the
backslash-normalized string it just built for the traversal check. This is the SAME shape of
gap BLD-09 (Phase 55 plan `55-03`) closed in the sibling call site, `_track_image()`'s
absolute-URI gate — but `_escapes_outdir()` was deliberately left untouched by that plan (its
scope fence names this function explicitly out of bounds).

**Measured this phase, in the `55-03` worktree**, against the pre-fix (and still-current, since
this function is untouched) tree:

```
>>> _escapes_outdir("\typsphinx_test\chart.png")
False
```

A driveless-absolute Windows-shaped `typst_documents` target stem (a leading separator, no
drive letter) is therefore NOT detected as an escape attempt by `_escapes_outdir()`, even though
the exact same string shape now IS correctly detected as absolute by
`_is_absolute_image_uri()` (`typsphinx/builder.py`, BLD-09's new predicate), which normalizes
backslashes to forward slashes FIRST and only then applies
`posixpath.isabs(...) or _is_drive_qualified(...)`.

## Why this was left alone in Phase 55 plan 55-03

`_escapes_outdir()`'s contract is OUT-02's target-stem escape test — a `typst_documents` config
value the project owner writes in `conf.py`, not an image URI a third-party Sphinx extension
plants. It has its own success criteria and its own gates (OUT-01/OUT-02, Phase 44/47), separate
from BLD-09's `_track_image()` scope. Widening it here, inside a plan scoped to
`_track_image()`'s two defects, would have been unplanned production-code churn outside this
plan's declared `files_modified` boundary and outside its threat model's disposed items —
`55-03-PLAN.md`'s scope fence names this function explicitly: "`_escapes_outdir()` is NOT
changed here. File the follow-up todo instead."

## Candidate repair (not attempted here)

Mirror `_is_absolute_image_uri()`'s own idiom: normalize backslashes to forward slashes FIRST,
then apply the same disjunction to the normalized string, for BOTH the parent-traversal split
(already effectively doing this) and the absolute-path check (not yet doing this):

```python
def _escapes_outdir(stem: str) -> bool:
    normalized = stem.replace("\\", "/")
    segments = normalized.split("/")
    return (
        ".." in segments
        or posixpath.isabs(normalized)
        or _is_drive_qualified(normalized)
    )
```

Needs its own RED-first fixture per this project's standing GATE-01 discipline — a driveless-
absolute Windows-shaped `typst_documents` target stem, asserted to be REJECTED by `OUT-02`'s
guard, failing against the unfixed function — before any fix lands. Also needs to reconfirm the
existing OUT-01/OUT-02 regression suite stays green (the drive-qualified and POSIX-absolute
branches are unchanged by this normalization, since `_is_drive_qualified()` and
`posixpath.isabs()` already agree with their normalized-string counterparts for those two
shapes — only the driveless-absolute shape's classification changes).

## Reachability

Low, same shape as BLD-09's own reachability note: a `typst_documents` `conf.py` entry
containing a driveless-absolute Windows-shaped target stem, authored (accidentally or
deliberately) by a project maintainer, evaluated on any platform (this is a pure string-shape
test, run identically everywhere) and any supported Python version.

## Owner decision (2026-08-16)

**Timing — AMENDED 2026-08-16, same day, before anything was created.** The final decision is:
**defer to the NEXT milestone, paired with its sibling
`2026-08-16-track-image-escape-branch-basename-not-normalized` (major). Nothing is inserted into
v0.9.0.**

~~**Timing: close inside v0.9.0 via an INSERTED phase (56.1).**~~ SUPERSEDED — retained
struck-through so the abandoned branch is not re-derived later. No `56.1` was ever created; the
ROADMAP, `STATE.md`, and `.planning/phases/` carry no trace of it.

The pairing is unchanged: these two close together whenever they close. And the reason this cannot be
fixed inline on the current branch survives the amendment unchanged — Phase 57's SC#4 requires that
`git diff` over the release-prep phase show no unintended `typsphinx/` change.

**Scope bar for the pair: the 3-OS CI lane including `windows-latest` green over the fix; residue
filed forward as a new todo.** For this defect specifically that bar is met by the one-function
change already sketched above, plus its RED-first fixture — a driveless-absolute Windows-shaped
`typst_documents` target stem asserted REJECTED by OUT-02's guard, failing against the unfixed
function first. Note this is a pure string-shape predicate that runs identically on every platform,
so the `windows-latest` lane is not where its evidence comes from; the RED fixture is.

Re-measured at HEAD 2026-08-16: `typsphinx/builder.py:238` still reads
`".." in segments or posixpath.isabs(stem) or _is_drive_qualified(stem)` — `segments` built from the
backslash-normalized string, the other two predicates applied to the raw `stem`. Unchanged since
filing.

## Related

- `.planning/todos/pending/2026-08-15-track-image-isabs-not-drive-aware-on-py313-windows.md` —
  BLD-09, the sibling defect this todo's gap was discovered alongside, in the SAME function
  family (`typsphinx/builder.py`'s platform-independent path-shape predicates).
- `.planning/phases/55-v0-8-0-derived-defects/55-03-PLAN.md` — Task 3's `<read_first>` and scope
  fence, which names this exact gap and directs it to be filed here rather than fixed in-phase.
- `.planning/phases/55-v0-8-0-derived-defects/55-03-RED-EVIDENCE.md` §"Predicate measurement" —
  the `_escapes_outdir()` measurement this todo is built from.
- `typsphinx/builder.py` — `_is_absolute_image_uri()` (BLD-09's new predicate) and
  `_is_drive_qualified()` — the existing platform-independent idiom this fix would reuse.
