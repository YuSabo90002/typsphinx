---
created: 2026-07-29T01:55:00+09:00
title: Two unterminated HTML comments in PROJECT.md's archived-footer tail
area: planning docs
files:
  - .planning/PROJECT.md (lines 492 and 506 as measured at commit 279aea5 — the two `<!-- Prior: ...` footers missing their closing token)
---

## Problem

`.planning/PROJECT.md` has two `<!--` openers with no matching `-->`. Measured at commit `279aea5`
by walking the file and tracking comment depth line by line:

| Line | Footer | Depth | Introduced by |
| --- | --- | --- | --- |
| 492 | `<!-- Prior: 2026-07-23 at v0.6.2 milestone close …` | 0 → 1 | `aec625b` (2026-07-23, `docs: start milestone v0.6.3 …`) |
| 506 | `<!-- Prior: 2026-07-11 after Phase 10 (Version-String Fix + v0.5.0 Release) …` | 1 → 2 | `05b35b8` (2026-07-11, `chore: archive v0.5.0 milestone files`) |

Both lines end with `Prior footer retained below.*` or `mirroring the v0.4.4 precedent.*` — the
trailing ` -->` was simply dropped. Final comment depth for the whole file is **2** (23 `<!--`
against 21 `-->`).

Note that line 468 is *not* a defect: it opens a genuinely multi-line comment that closes correctly
at line 481. Only 492 and 506 are unterminated.

**Impact is narrow but real.** HTML comments do not nest, so an unterminated `<!--` runs until the
next `-->` in the file — which is the closing token of the *following* footer. The concrete effect:

- Line 492's comment swallows lines 493–494, so the Phase 22 / Issue #117 footer (line 494) stops
  being its own comment.
- Line 506's comment swallows lines 507–508, so the Phase 9 footer (line 508) stops being its own
  comment.

Nothing visible is lost: everything from line 492 to the end of file (509) is either a comment or a
blank line, so no prose that was meant to render gets hidden. The cost is that four archived
footers become two mis-nested blobs — they are no longer independently greppable as
`<!-- Prior: … -->` units, and any tool that parses the footer archive by comment boundaries will
mis-attribute them.

This was noticed during Phase 35's `update_project_md` step. It predates that phase (the depth-2
imbalance is present at `f1558b6`, before Phase 35 touched the file) and was deliberately not fixed
there, because repairing historical footers is outside a release-prep phase's scope and the phase's
own edit was verified balanced (exactly one `<!--` and one `-->` added).

## Solution

1. Append ` -->` to the end of line 492 and line 506, matching the format every other archived
   footer already uses.
2. Re-run the depth check and confirm it lands on 0:

   ```bash
   node -e '
   const lines=require("fs").readFileSync(".planning/PROJECT.md","utf8").split("\n");
   let d=0; lines.forEach((l,i)=>{d+=(l.match(/<!--/g)||[]).length-(l.match(/-->/g)||[]).length;});
   console.log("final depth", d, d===0?"OK":"MISMATCH");'
   ```

3. Consider preventing recurrence. Both defects came from the same recurring edit: every phase
   completion prepends a new `*Last updated: …*` footer and demotes the previous one to
   `<!-- Prior: … -->`, and twice that demotion dropped the closing token. The cheapest guard is a
   test in the existing suite — the same shape as the other `.planning/`-adjacent structural
   guards — asserting that `.planning/PROJECT.md` has equal `<!--` and `-->` counts. That turns a
   silent drift channel into a red test at the moment it is introduced, instead of surfacing three
   milestones later.
