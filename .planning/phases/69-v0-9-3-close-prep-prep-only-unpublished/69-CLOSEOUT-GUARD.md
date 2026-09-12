# Phase 69 — REL-12 Checkbox-Flip Closeout Guard

This file changes no requirement state: REL-12 stays an unchecked box (`- [ ]`) and its
Traceability row stays `Pending`. `.planning/REQUIREMENTS.md` is read and quoted here, never
edited.

## Baseline

Recorded at phase head, inside this plan's isolated worktree (`worktree-agent-abe1318883a64e327`),
before this plan's first commit.

```
$ git rev-parse HEAD
2db4e803d36d5f7a5db0a92b08cac4988fa88957

$ git log -1 --format='%H %s'
2db4e803d36d5f7a5db0a92b08cac4988fa88957 docs(69): mark phase 69 executing (wave 1 of 3)

$ sha256sum .planning/REQUIREMENTS.md
02cb9deb614af2bd89e33adc5d0b640a489f85e616ba74aa1eb419e5b92a232a  .planning/REQUIREMENTS.md

$ wc -l .planning/REQUIREMENTS.md
172 .planning/REQUIREMENTS.md

$ grep -c 'REL-12' .planning/REQUIREMENTS.md
4

$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-09-12T22:33:44Z
```

**PHASE_BASE_SHA:**

```
2db4e803d36d5f7a5db0a92b08cac4988fa88957
```

Key lines:

```
PHASE_BASE_SHA = 2db4e803d36d5f7a5db0a92b08cac4988fa88957
REQ_SHA256_BASE = 02cb9deb614af2bd89e33adc5d0b640a489f85e616ba74aa1eb419e5b92a232a
REQ_LINES_BASE = 172
REL12_HITS_BASE = 4
GUARD_AT = 2026-09-12T22:33:44Z
```

Subject `docs(69): mark phase 69 executing (wave 1 of 3)` — a phase-tracking commit that predates
this plan's own execution and carries no `(69-0N)` plan-level commit scope.

**Cross-check against the planning-time census.** This plan's own frontmatter census (2026-09-13,
main checkout at `b2fea682`) recorded digest `02cb9deb614af2bd89e33adc5d0b640a489f85e616ba74aa1eb419e5b92a232a`,
172 lines, and 4 `REL-12` hits (classified 2 state-bearing / 2 informational). The fresh commands
run above, inside this plan's own isolated worktree, agree byte-for-byte and digit-for-digit with
every one of those three values: same digest, same line count, same hit count. No drift occurred
between planning and this plan's own execution; `.planning/REQUIREMENTS.md` has not changed in the
interim. The fresh values above are kept as the baseline, per the plan's own instruction to prefer a
freshly-measured value even when it agrees with the census.

REL-12's checkbox reads `- [ ]` and its Traceability row reads `Pending` (both confirmed in
§ "The lines under guard" below) — the required precondition for this file to proceed rather than
halt.

## The lines under guard

Verbatim output of `grep -n 'REL-12' .planning/REQUIREMENTS.md`, run against this worktree's tree
at the timestamp above:

```
$ grep -n 'REL-12' .planning/REQUIREMENTS.md
75:- [ ] **REL-12**: the milestone is merged to `main` via a PR, with no tag, no PyPI upload and no
147:| REL-12 | Phase 69 | Pending |
164:| 69 — v0.9.3 Close Prep (prep-only, unpublished) | REL-12 | 1 |
166:**REL-12 is mapped to Phase 69 for coverage purposes only.** Like every REL requirement in this
```

Four hits, as expected from both the baseline probe and the planning-time census.

**Classification:**

- **State-bearing:** line 75 (the requirement bullet's checkbox — `- [ ] **REL-12**`, whose bullet
  continues across lines 76 with prose describing the no-tag / no-PyPI-upload / no-GitHub-Release /
  `pyproject.toml` still-`0.9.2` conditions — only the leading `- [ ]` token on line 75 is
  state-bearing) and line 147 (the Traceability row — `| REL-12 | Phase 69 | Pending |`). These are
  the two lines whose content would change if the checkbox flipped.
- **Informational-only:** line 164 (the "Phase distribution" table row mapping Phase 69 to REL-12
  with a count of 1) and line 166 (the opening line of the "REL-12 is mapped to Phase 69 for
  coverage purposes only" explanatory paragraph, which continues onto line 167-168 stating REL-12
  closes at `/gsd-complete-milestone` and cites `ROADMAP.md` constraint 14). Neither line 164 nor
  166 carries a checkbox or a `Pending`/`Complete` token of its own; neither would change shape
  merely because line 75 or 147 flipped.

**Why the whole-file SHA-256 is the primary probe, not a scoped grep.** Two reasons, both drawn
from this project's own history rather than asserted abstractly:

1. A flip is line-count-neutral — `- [ ]` and `- [x]` are the same length, and a `Pending` →
   `Complete` Traceability-row edit does not add or remove a line. `wc -l` alone cannot detect it;
   only a byte-level digest can.
2. Phase 63's flip moved **three** requirements at once (REL-09, REL-10 and REL-11 together, per
   `63-CLOSEOUT-GUARD.md` §§ "Third observation" and "Fourth observation") — a grep scoped to
   `REL-12` alone would have missed the other two entirely. The whole-file digest catches any writer
   of `.planning/REQUIREMENTS.md`, regardless of which requirement ID it touches.

## Why this file exists

`phase.complete`-family tooling has auto-flipped the release requirement's checkbox and
Traceability-row state against an explicit CONTEXT decision at **seven consecutive** prior
release-prep closes (`ROADMAP.md` binding constraint 14; `63-CLOSEOUT-GUARD.md` §§ "Third
observation" and "Fourth observation"):

- The v0.7.0, v0.7.1, v0.8.0, v0.9.0 and v0.9.1 closes each flipped their respective release
  requirement before this project caught and reverted the flip; Phase 61 was the first to hold,
  using this exact procedure (`61-CLOSEOUT-GUARD.md`).
- The last landing came **twice** at the Phase 63 close: once through `/gsd-execute-phase`'s
  `phase.complete` step (the "Third observation"), and once again through `/gsd-verify-work`'s
  inline transition (the "Fourth observation") — the same underlying verb, reached through two
  different entry points. Both times it flipped **three** requirements at once (REL-09, REL-10 and
  REL-11 together), and both times it was reverted with `git checkout -- .planning/REQUIREMENTS.md`
  and never committed in the flipped state.
- REL-12 is again a requirement meant to close only at `/gsd-complete-milestone`, per this
  project's standing convention (held for nine consecutive milestones per `ROADMAP.md`'s Phase 69
  section) — its checkbox is deliberately held at `- [ ]` through every plan in this phase.

## Re-verification protocol (phase close)

Plan 69-06 (the SC#1-observation-2 and close-time fence owner) runs exactly these commands against
the tree as it stands at its own point in the phase, and reports whether the Baseline still holds:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare the printed digest against this file's Baseline:
# 02cb9deb614af2bd89e33adc5d0b640a489f85e616ba74aa1eb419e5b92a232a

wc -l .planning/REQUIREMENTS.md
# compare against this file's Baseline: 172

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-12' .planning/REQUIREMENTS.md
# expected: byte-identical to the four quoted lines above (75, 147, 164, 166)
```

## For the operator running phase.complete

This section applies after this phase's plans have finished, at **whichever of the two entry
points runs**: `/gsd-execute-phase`'s `phase.complete` step, or `/gsd-verify-work`'s inline
transition (`transition.md`'s `update_roadmap_and_state`, which calls the same `phase.complete`
verb unconditionally once UAT closes clean — the exact path that produced Phase 63's "Fourth
observation"). Both entry points must be treated as equally likely to trigger the flip; neither is
safer to assume clean than the other.

**Before either runs:** back up `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` and
`.planning/STATE.md` to a scratch directory **outside the repository** (e.g.
`/tmp/scratch-69-closeout/`), so a hand-edited STATE.md or ROADMAP.md rewrite that the tooling
itself corrupts (Phase 63's "Fourth observation" found STATE.md's rewrite dropping
`current_phase_name` and degrading descriptive fields) has a known-good copy to diff against, not
only `.planning/REQUIREMENTS.md`.

**After it runs**, re-run the same probes as § "Re-verification protocol (phase close)" above, with
the baseline digest and grep lines written out inline here so the reader needs no other file open:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare against: 02cb9deb614af2bd89e33adc5d0b640a489f85e616ba74aa1eb419e5b92a232a

wc -l .planning/REQUIREMENTS.md
# compare against: 172

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-12' .planning/REQUIREMENTS.md
# expected: byte-identical to:
#   75:- [ ] **REL-12**: the milestone is merged to `main` via a PR, with no tag, no PyPI upload and no
#   147:| REL-12 | Phase 69 | Pending |
#   164:| 69 — v0.9.3 Close Prep (prep-only, unpublished) | REL-12 | 1 |
#   166:**REL-12 is mapped to Phase 69 for coverage purposes only.** Like every REL requirement in this
```

**On any divergence:** run `git checkout -- .planning/REQUIREMENTS.md`, re-run the probes above to
show a MATCH, and then diff `.planning/ROADMAP.md` and `.planning/STATE.md` against the scratch
backup — reverting either if it, too, carries an unwarranted change from the same tooling run.

**The rule: reverted and reported, never committed.** No `/gsd-complete-milestone` step starts
until every probe above shows MATCH. This is the explicit rule this project has followed at every
prior release-prep close where the flip was caught: revert first, report second, never ship the
flipped state as part of the phase's own close.

`69-HANDOFF.md` reproduces this section in full, so an operator following the handoff reaches it
without opening this file separately.

## This task's own effect on `.planning/REQUIREMENTS.md`

```
$ git diff --name-only -- .planning/REQUIREMENTS.md
(no output)

$ git status --porcelain .planning/REQUIREMENTS.md
(no output)
```

Byte-unchanged. REL-12 remains `- [ ]` and Pending, exactly as recorded in § "The lines under
guard" above.

## Re-verification at phase close

Run inside plan 69-06's own isolated worktree (`worktree-agent-a6a7396dafbb4f7c5`), immediately
after Task 1's commit (`2a37ca9d`), running exactly the commands this file's own
§ "Re-verification protocol (phase close)" names.

```
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-09-12T23:05:00Z
```

```
CLOSE_AT = 2026-09-12T23:05:00Z
```

```
$ sha256sum .planning/REQUIREMENTS.md
02cb9deb614af2bd89e33adc5d0b640a489f85e616ba74aa1eb419e5b92a232a  .planning/REQUIREMENTS.md
```

```
REQ_SHA256_CLOSE = 02cb9deb614af2bd89e33adc5d0b640a489f85e616ba74aa1eb419e5b92a232a
```

| Digest | Value |
|---|---|
| `REQ_SHA256_BASE` | `02cb9deb614af2bd89e33adc5d0b640a489f85e616ba74aa1eb419e5b92a232a` |
| `REQ_SHA256_CLOSE` | `02cb9deb614af2bd89e33adc5d0b640a489f85e616ba74aa1eb419e5b92a232a` |

**MATCH.**

```
$ wc -l < .planning/REQUIREMENTS.md
172
```

```
REQ_LINES_CLOSE = 172
```

Equal to `REQ_LINES_BASE` (172). **MATCH.**

```
$ git diff --name-only -- .planning/REQUIREMENTS.md
(no output)
```

Empty. **MATCH.**

```
$ git log --oneline 2db4e803d36d5f7a5db0a92b08cac4988fa88957..HEAD -- .planning/REQUIREMENTS.md
(no output)
```

No commit in the phase touched the file since `PHASE_BASE_SHA`. **MATCH.**

```
$ grep -n 'REL-12' .planning/REQUIREMENTS.md
75:- [ ] **REL-12**: the milestone is merged to `main` via a PR, with no tag, no PyPI upload and no
147:| REL-12 | Phase 69 | Pending |
164:| 69 — v0.9.3 Close Prep (prep-only, unpublished) | REL-12 | 1 |
166:**REL-12 is mapped to Phase 69 for coverage purposes only.** Like every REL requirement in this
```

Byte-identical to § "The lines under guard" above, line for line (75, 147, 164, 166). **MATCH.**

| Comparison | Verdict |
|---|---|
| `REQ_SHA256_CLOSE` vs `REQ_SHA256_BASE` | MATCH |
| `REQ_LINES_CLOSE` vs `REQ_LINES_BASE` | MATCH |
| `git diff --name-only -- .planning/REQUIREMENTS.md` | MATCH (empty) |
| `git log` over the file since `PHASE_BASE_SHA` | MATCH (empty) |
| `grep -n 'REL-12'` line-by-line | MATCH |

```
REQ_VERDICT_CLOSE = MATCH
```

Every comparison holds. REL-12's checkbox, read directly from the file, is `- [ ]`
(`.planning/REQUIREMENTS.md:75`) and its Traceability row is `Pending`
(`.planning/REQUIREMENTS.md:147`) — never inferred from any SUMMARY frontmatter. Every plan of this
phase declares `requirements-completed: []`.

No divergence occurred, so § "Divergence detected and reverted" does not apply and is omitted.

**§ "For the operator running phase.complete" is present and unedited** (verified by re-reading it
above this section, unchanged from Plan 02's authoring). The decisive third observation runs after
this plan, outside any plan's reach, and `69-HANDOFF.md` reproduces this section in full so the
operator reaches it without opening this file separately.

---
*Phase: 69-v0-9-3-close-prep-prep-only-unpublished*
*Plan: 02, 06*
