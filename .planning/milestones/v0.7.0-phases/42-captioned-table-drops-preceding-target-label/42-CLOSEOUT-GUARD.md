# Phase 42, Plan 06 — REL-04 / REL-05 Checkbox-Flip Guard

**Recorded:** 2026-08-03T14:53:15Z, inside worktree-agent worktree `worktree-agent-a487e99b3ae6ae3cd`.

**Purpose.** `phase.complete`-family tooling has been observed auto-flipping REL-04's and REL-05's
checkbox and Traceability-row state exactly once already this milestone — Phase 41 hit it on
2026-08-03 and reverted it before committing, as `41-HANDOFF.md` item 6 warned it would need. This
file makes the post-close diff check **falsifiable** rather than remembered: it records the four
at-risk lines' exact pre-close text with a checksum, so any future diff against `.planning/
REQUIREMENTS.md` can be compared against a concrete recorded baseline instead of relying on someone
recalling what REL-04/REL-05 "should" still say.

This task changes NO requirement state. REL-04 and REL-05 stay `[ ]` and Pending; TBL-03's own
checkbox is also NOT flipped here — flipping it is the phase-close step this guard protects, not
this plan's own work.

---

## 1. The four at-risk lines, recorded verbatim with observed line numbers

All four lines quoted below were read directly from `.planning/REQUIREMENTS.md` in THIS worktree at
the timestamp above.

### REL-04's requirement bullet's checkbox line

**Observed at line 208:**

```
- [ ] **REL-04** [M]: The GitHub Release body is the **curated `## [X.Y.Z]` CHANGELOG section**, not
```

(The bullet continues across lines 209-210 with prose that carries no checkbox state of its own —
only line 208's leading `- [ ]` is the state-bearing token.)

### REL-05's requirement bullet's checkbox line

**Observed at line 212:**

```
- [ ] **REL-05** [M]: v0.7.0 is released — version bumped as the sole literal in `pyproject.toml`
```

(Continues across lines 213-215 with prose; line 212's `- [ ]` is the state-bearing token.)

### REL-04's Traceability row

**Observed at line 337:**

```
| REL-04 | Phase 41 | Pending |
```

### REL-05's Traceability row

**Observed at line 338:**

```
| REL-05 | Phase 41 | Pending |
```

### File checksum, both lines' context confirmed together

```
$ sha256sum .planning/REQUIREMENTS.md
07a2f654a9f3fb81bc661f21aa5807922474449ca5070a66bb26b1c44bd72db0  .planning/REQUIREMENTS.md
```

Any future `git diff -- .planning/REQUIREMENTS.md` should be compared against a tree where this
checksum is the pre-close state. If the file's checksum no longer matches
`07a2f654a9f3fb81bc661f21aa5807922474449ca5070a66bb26b1c44bd72db0` at the point this guard is
consulted, that is expected (this plan's own Task 3 commit and any subsequent legitimate edit will
change it) — the checksum's role here is to anchor exactly what "the pre-close state" meant at the
moment this guard was written, not to assert the file must stay unchanged forever.

---

## 2. TBL-03's own lines, recorded for contrast (the legitimate flip this guard must NOT block)

So the procedure below can distinguish a legitimate TBL-03 flip from an illegitimate REL-04/REL-05
flip, TBL-03's current (pre-flip) state is recorded here too:

### TBL-03's requirement bullet's checkbox line

**Observed at line 195:**

```
- [ ] **TBL-03** [M]: A captioned table immediately preceded by a standalone target (`.. _label:`)
```

### TBL-03's Traceability row

**Observed at line 339:**

```
| TBL-03 | Phase 42 | Pending |
```

When Phase 42 closes (a step this plan does not take), the LEGITIMATE edit is: line 195's `- [ ]`
becomes `- [x]`, and line 339's `Pending` becomes `Complete`. Nothing else in the file should change
as part of that flip. Lines 208, 212, 337, and 338 (REL-04/REL-05) must remain byte-identical to
what section 1 above records.

---

## 3. The procedure — ordered, runnable steps

1. **After any `phase.complete`-family command runs and BEFORE committing, run:**

   ```
   git diff -- .planning/REQUIREMENTS.md
   ```

2. **If the diff touches the REL-04 or REL-05 checkbox bullets (lines 208 or 212 as recorded in
   §1) or their Traceability rows (lines 337 or 338 as recorded in §1), that change is
   unintended.** Revert `.planning/REQUIREMENTS.md` to its pre-command state, then re-apply BY HAND
   only the TBL-03 checkbox and Traceability-row flip that Phase 42 legitimately earns (§2's
   lines 195 and 339 — `- [ ]` to `- [x]`, `Pending` to `Complete`). Do not use the automated
   tool's own output for the TBL-03 lines either, if that output's diff also touched REL-04/REL-05 —
   revert the whole automated diff and hand-apply only the two TBL-03 line changes, to guarantee no
   REL-04/REL-05 drift rides along inside a diff that "mostly" looks right.

3. **Re-run `git diff -- .planning/REQUIREMENTS.md` and confirm only TBL-03's two lines changed**
   (the checkbox at line 195 and the Traceability row at line 339, per §2). If the diff still shows
   any change to REL-04's or REL-05's four lines (§1), repeat step 2 — do not commit.

---

## 4. Why REL-04 and REL-05 must stay unchecked

REL-04 and REL-05 are **close-side work owned by `/gsd-complete-milestone`**, not by this phase or
any phase's own close:

- **REL-05's own requirement text** (quoted in full in §1) requires "the publish executed at
  `/gsd-complete-milestone` (tag → `release.yml` → PyPI + GitHub Release, plus the standing second
  tag on `typsphinx-doc-translations`)." That publish has not happened — `41-HANDOFF.md`'s 7-item
  checklist is still un-executed, and `STATE.md`'s own record states local and remote `v0.7.0` tags
  are both empty (measured twice independently inside Phase 41, and again by its verifier).
  Checking REL-05 now would assert a fact that is not yet true.

- **REL-04's body swap is first exercised by that same tag push.** REL-04's requirement is that the
  GitHub Release body is sourced from the curated CHANGELOG section rather than the commit-dump
  default; the workflow change (`release.yml`) landed in Phase 41 (plan 41-01), but the change only
  takes effect the first time `release.yml` actually runs against a real tag push — which has not
  happened yet either. Checking REL-04 now would assert the mechanism was *exercised*, not merely
  *written*.

Neither condition is satisfied by this plan or by Phase 42 as a whole. Both stay `[ ]` and Pending
until `/gsd-complete-milestone` actually executes the publish.

---

## 5. Pointer — the publish checklist this guard protects, without duplicating it

`41-HANDOFF.md`'s 7-item publish checklist (`.planning/phases/41-v0-7-0-release-automation-release-
prep/41-HANDOFF.md`) is still valid and still un-executed. It runs only AFTER Phase 42 verifies —
this guard exists precisely so that when it does run, its own item 6 (the same REL-04/REL-05
checkbox-flip hazard, stated independently in that file) has a concrete pre-close baseline to diff
against rather than a fresh, unmeasured "current state." This file does not copy that checklist's
contents and does not modify `41-HANDOFF.md` — confirmed:

```
$ git status --porcelain .planning/phases/41-v0-7-0-release-automation-release-prep/
(no output)
```

---

## 6. This plan's own effect on `.planning/REQUIREMENTS.md`

```
$ git status --porcelain .planning/REQUIREMENTS.md
(no output)
```

`.planning/REQUIREMENTS.md` is byte-unchanged by this plan. REL-04 and REL-05 remain `- [ ]` and
Pending; TBL-03 remains `- [ ]` and Pending — its flip is deliberately left for the phase-close step
this guard protects, not taken here.
