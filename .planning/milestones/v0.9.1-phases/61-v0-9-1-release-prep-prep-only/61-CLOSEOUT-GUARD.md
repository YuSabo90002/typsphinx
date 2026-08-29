# Phase 61 — REL-09 Checkbox-Flip Closeout Guard

This task changes NO requirement state: REL-09 stays an unchecked box (`- [ ]`) and its
Traceability row stays `Pending`. `.planning/REQUIREMENTS.md` is read and quoted here and never
edited.

## Baseline

Recorded at phase head, inside this plan's isolated worktree (`worktree-agent-a9f8e61dc22c6d378`),
before any other plan in Phase 61 has run.

```
$ sha256sum .planning/REQUIREMENTS.md
4682f8cde6b068c2ebbe42201fdff4b0b4cf17558d68c889baaf2f4506d531e1  .planning/REQUIREMENTS.md

$ wc -l .planning/REQUIREMENTS.md
258 .planning/REQUIREMENTS.md

$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-08-29T15:04:23Z

$ git rev-parse HEAD
5e28fa9dac8576f1f1665560eb5c4ccbd2e13b41
```

**PHASE_BASE_SHA:**

```
5e28fa9dac8576f1f1665560eb5c4ccbd2e13b41
```

This is the phase-head commit — plan 61-04 reads this value back from this file to scope its
`typsphinx/` diff.

**Cross-check against the research-time values.** `61-PATTERNS.md` and `61-RESEARCH.md` supplied
the values measured at research time as a cross-check, not as the final answer: checksum
`4682f8cde6b068c2ebbe42201fdff4b0b4cf17558d68c889baaf2f4506d531e1`, line count `258`. Both commands
were re-run fresh above (not transcribed), and both values are byte-identical to the research-time
figures. No drift occurred between planning and execution; `.planning/REQUIREMENTS.md` has not
changed in the interim.

## The lines under guard

Verbatim output of `grep -n 'REL-09' .planning/REQUIREMENTS.md`, run against this worktree's tree
at the timestamp above:

```
$ grep -n 'REL-09' .planning/REQUIREMENTS.md
127:- [ ] **REL-09**: v0.9.1 released to PyPI with a curated `## [0.9.1]` CHANGELOG entry, the version
206:| REL-09 | Phase 61 | Pending |
220:Phase 60 → 4 (MSG-02, MSG-03, MSG-04, MSG-05) · Phase 61 → 1 (REL-09).
```

Three hits, as expected.

### REL-09's requirement bullet's checkbox line

**Observed at line 127 (byte-for-byte):**

```
- [ ] **REL-09**: v0.9.1 released to PyPI with a curated `## [0.9.1]` CHANGELOG entry, the version
```

(The bullet continues across lines 128-129 with prose describing the version-bump and GitHub
Release Body requirements — only line 127's leading `- [ ]` is the state-bearing token.)

### REL-09's Traceability row

**Observed at line 206 (byte-for-byte):**

```
| REL-09 | Phase 61 | Pending |
```

### The phase-totals line

**Observed at line 220 (byte-for-byte), cited for completeness since the `grep -n` output above
surfaces it, but it carries no checkbox or Pending/Complete state of its own:**

```
Phase 60 → 4 (MSG-02, MSG-03, MSG-04, MSG-05) · Phase 61 → 1 (REL-09).
```

## Why this file exists

`phase.complete`-family tooling has auto-flipped the release requirement's checkbox and
Traceability-row state against an explicit CONTEXT decision at **five consecutive** release-prep
closes. Phase 61 increments the running count that `57-CLOSEOUT-GUARD.md` recorded as four (the
v0.7.0, v0.7.1, v0.8.0, and v0.9.0 closes all flipped their respective release requirement before
this project caught and reverted the flip; the mechanism this file establishes is the same one
`57-CLOSEOUT-GUARD.md`, `52-CLOSEOUT-GUARD.md`, and `42-CLOSEOUT-GUARD.md` used successfully in
their own phases).

**This close is MORE exposed than prior ones, not less.** Per D-08, REL-09's wording is left
unchanged and still literally reads "v0.9.1 released to PyPI with a curated `## [0.9.1]` CHANGELOG
entry" — which is no longer what this phase, or this milestone, does (D-01, D-02: no version bump,
no `## [0.9.1]` section, v0.9.1 is never published). A generic close tool that pattern-matches "the
phase named in a requirement's Traceability row completed" against Phase 61's own eventual
`phase_complete` status has both the historical five-for-five track record AND a requirement whose
own text no longer describes reality working against it — flipping REL-09 here would be both wrong
and, superficially, plausible-looking to a tool that does not read `61-CONTEXT.md`'s D-08.

## Re-verification protocol (phase close)

Plan 61-04 (the SC#4 fence-observation-2 owner) runs exactly these commands against the tree as it
stands at its own point in the phase, and reports whether the Baseline still holds:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare the printed digest against this file's Baseline:
# 4682f8cde6b068c2ebbe42201fdff4b0b4cf17558d68c889baaf2f4506d531e1

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-09' .planning/REQUIREMENTS.md
# expected: byte-identical to the three quoted lines above (127, 206, 220)
```

## Post-close detection and reversion (after phase.complete runs)

This section is reproduced in `61-HANDOFF.md` so an operator following the handoff reaches it
without opening this file.

After `phase.complete`-family tooling has run for Phase 61 — outside any plan's reach, and
precisely the moment at which the flip has historically landed — run the same three commands
again:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare against this file's Baseline: 4682f8cde6b068c2ebbe42201fdff4b0b4cf17558d68c889baaf2f4506d531e1

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-09' .planning/REQUIREMENTS.md
# expected: byte-identical to the three quoted lines above (127, 206, 220)
```

If the digest has moved, or `git diff --name-only -- .planning/REQUIREMENTS.md` shows a change
touching line 127's checkbox or line 206's Traceability row, that change is unintended. Revert it
by hand:

```bash
git checkout -- .planning/REQUIREMENTS.md
```

**The flip is reverted and reported, never accepted and never committed.** This is the explicit
rule this project has followed at every prior release-prep close where the flip was caught: revert
first, report second, never ship the flipped state as part of the phase's own close.

## This task's own effect on `.planning/REQUIREMENTS.md`

```
$ git status --porcelain .planning/REQUIREMENTS.md
(no output)
```

Byte-unchanged. REL-09 remains `- [ ]` and Pending, exactly as recorded in § "The lines under
guard" above.

## Re-verification at phase close

Run by plan 61-04 (the SC#4 fence-observation-2 owner), inside this plan's own worktree, at the
phase's own close, running exactly the commands this file's own "Re-verification protocol (phase
close)" section named above.

```
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-08-29T15:46:13Z
```

**Verdict: MATCH.** This is the close-time observation timestamp.

```
$ sha256sum .planning/REQUIREMENTS.md
4682f8cde6b068c2ebbe42201fdff4b0b4cf17558d68c889baaf2f4506d531e1  .planning/REQUIREMENTS.md
```

**Verdict: MATCH.** Byte-identical to the recorded Baseline digest
(`4682f8cde6b068c2ebbe42201fdff4b0b4cf17558d68c889baaf2f4506d531e1`).

```
$ wc -l .planning/REQUIREMENTS.md
258 .planning/REQUIREMENTS.md
```

**Verdict: MATCH.** Identical to the recorded Baseline line count (`258`).

```
$ git diff --name-only -- .planning/REQUIREMENTS.md
(no output)
```

**Verdict: MATCH.** No output — the file carries no uncommitted change against the tree's own HEAD.

```
$ grep -n 'REL-09' .planning/REQUIREMENTS.md
127:- [ ] **REL-09**: v0.9.1 released to PyPI with a curated `## [0.9.1]` CHANGELOG entry, the version
206:| REL-09 | Phase 61 | Pending |
220:Phase 60 → 4 (MSG-02, MSG-03, MSG-04, MSG-05) · Phase 61 → 1 (REL-09).
```

**Verdict: MATCH, line-for-line.** Byte-identical to the three quoted lines in § "The lines under
guard" above — line 127's checkbox is still `- [ ]`, line 206's Traceability row still reads
`Phase 61 | Pending`, and line 220's phase-totals line is unchanged.

**Overall verdict: no divergence detected.** REL-09 is still an unchecked box, its Traceability row
still reads `Phase 61` and `Pending`, and no plan in this phase — including this one — touched it.
Per D-08 it carries forward unmet to the v0.9.2 milestone with its literal wording unchanged,
including its `v0.9.1` version string, which the owner explicitly declined to rewrite and explicitly
declined to close as superseded. The only inconsistency this leaves behind is a version number
inside a requirement that has never been satisfied, which is accurate, because nothing was released.

No `### Divergence detected and reverted` subsection is needed — every comparison above is a
MATCH, so there is nothing to revert.

## For the operator running phase.complete

This section is reproduced in `61-HANDOFF.md` so an operator following the handoff reaches it
without opening this file.

After `phase.complete`-family tooling has run for Phase 61 — outside any plan's reach, and
precisely the moment at which the flip has historically landed at **five consecutive** prior
release-prep closes — run:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare against the Baseline: 4682f8cde6b068c2ebbe42201fdff4b0b4cf17558d68c889baaf2f4506d531e1

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-09' .planning/REQUIREMENTS.md
# expected: byte-identical to:
#   127:- [ ] **REL-09**: v0.9.1 released to PyPI with a curated `## [0.9.1]` CHANGELOG entry, the version
#   206:| REL-09 | Phase 61 | Pending |
#   220:Phase 60 → 4 (MSG-02, MSG-03, MSG-04, MSG-05) · Phase 61 → 1 (REL-09).
```

If any comparison diverges, revert it by hand:

```bash
git checkout -- .planning/REQUIREMENTS.md
```

**The flip is reverted and reported, never accepted and never committed.** Do not proceed with
`/gsd-complete-milestone` or any subsequent step until the reversion is confirmed by re-running the
three commands above and observing MATCH on all three.

---
*Phase: 61-v0-9-1-release-prep-prep-only*
*Plan: 02, 04*
