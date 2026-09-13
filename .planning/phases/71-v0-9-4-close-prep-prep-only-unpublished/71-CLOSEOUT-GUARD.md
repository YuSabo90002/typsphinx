# Phase 71 — REL-13 Checkbox-Flip Closeout Guard

This file changes no requirement state: REL-13 stays an unchecked box (`- [ ]`) and its
Traceability row stays `Pending`. `.planning/REQUIREMENTS.md` is read and quoted here, never
edited (D-02: no Phase 71 plan writes it).

## Baseline

Recorded at phase head, inside this plan's isolated worktree
(`worktree-agent-a571bab6fc41395dc`), before this plan's first commit.

```
$ git rev-parse HEAD
f1f7d54a61d74c3972f1df0508ac994c001dda7e

$ git log -1 --format='%H %s'
f1f7d54a61d74c3972f1df0508ac994c001dda7e docs(phase-71): record planning completion and reconcile the validation map

$ git log --format=%H -1 -S 'AMENDED 2026-09-13 (Phase 71 discussion' -- .planning/REQUIREMENTS.md
5292a85b58b67c364faced564bdf8314426bca38

$ git merge-base --is-ancestor 5292a85b58b67c364faced564bdf8314426bca38 f1f7d54a61d74c3972f1df0508ac994c001dda7e; echo "exit:$?"
exit:0

$ sha256sum .planning/REQUIREMENTS.md
4d98e0287552d2dce8f45b7939dfcb0e729523c6869bfa1cd2d1d041119c5636  .planning/REQUIREMENTS.md

$ wc -l .planning/REQUIREMENTS.md
80 .planning/REQUIREMENTS.md

$ grep -c 'REL-13' .planning/REQUIREMENTS.md
4

$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-09-13T08:29:16Z
```

Key lines:

```
PHASE_BASE_SHA = f1f7d54a61d74c3972f1df0508ac994c001dda7e
AMENDED_COMMIT = 5292a85b58b67c364faced564bdf8314426bca38
REQ_SHA256_BASE = 4d98e0287552d2dce8f45b7939dfcb0e729523c6869bfa1cd2d1d041119c5636
REQ_LINES_BASE = 80
REL13_HITS_BASE = 4
GUARD_AT = 2026-09-13T08:29:16Z
```

Subject `docs(phase-71): record planning completion and reconcile the validation map` — a
phase-tracking commit that predates this plan's own execution and carries no `(71-0N)`
plan-level commit scope. `git merge-base --is-ancestor` confirms `AMENDED_COMMIT` is an ancestor
of `PHASE_BASE_SHA`: the phase head is after D-02's AMENDED commit, as D-09 requires.

**Cross-check against the planning-time census.** This plan's own frontmatter census (2026-09-13,
main checkout at `d8679b01`) recorded digest
`4d98e0287552d2dce8f45b7939dfcb0e729523c6869bfa1cd2d1d041119c5636`, 80 lines, and 4 `REL-13` hits
(classified 2 state-bearing / 2 informational). The fresh commands run above, inside this plan's
own isolated worktree, agree byte-for-byte and digit-for-digit with every one of those three
values: same digest, same line count, same hit count. No drift occurred between planning and this
plan's own execution; `.planning/REQUIREMENTS.md` has not changed in the interim. The fresh values
above are kept as the baseline, per the plan's own instruction to prefer a freshly-measured value
even when it agrees with the census.

REL-13's checkbox reads `- [ ]` and its Traceability row reads `Pending` (both confirmed in
§ "The lines under guard" below) — the required precondition for this file to proceed rather than
halt.

## The lines under guard

Verbatim output of `grep -n 'REL-13' .planning/REQUIREMENTS.md`, run against this worktree's tree
at the timestamp above:

```
$ grep -n 'REL-13' .planning/REQUIREMENTS.md
24:- [ ] **REL-13**: Close prep only, unpublished: one CHANGELOG bullet under the existing `## [Unreleased]`, in the register of the three bullets already there, naming the API-reference type-text change and noting that the ja translation catalogs pick it up at the next published release; `pyproject.toml` stays `0.9.2`; no tag, no PyPI upload, no GitHub Release. The milestone branch is merged to `main` through a PR, as v0.9.3's REL-12 was. This checkbox is checked only at `/gsd-complete-milestone`, on the observed merge — never by phase-completion tooling.
33:  wrong for the same reason. Every other part of REL-13 stands, including when this checkbox is
71:| REL-13 | Phase 71 | Pending — coverage only; checked at `/gsd-complete-milestone` on the observed merge, never by phase-completion tooling |
75:- Mapped to phases: 6 (Phase 70: 5 — QUA-09, QUA-11, QUA-12, DOC-22, DOC-23; Phase 71: 1 — REL-13)
```

Four hits, as expected from both the baseline probe and the planning-time census.

**Classification:**

- **State-bearing:** line 24 (the requirement bullet's checkbox — `- [ ] **REL-13**`, whose bullet
  continues with prose describing the no-tag / no-PyPI-upload / no-GitHub-Release /
  `pyproject.toml` still-`0.9.2` conditions — only the leading `- [ ]` token is state-bearing) and
  line 71 (the Traceability row — `| REL-13 | Phase 71 | Pending — coverage only; … |`). These are
  the two lines whose content would change if the checkbox flipped.
- **Informational:** line 33 (the tail of the AMENDED block's prose, continuing "wrong for the
  same reason. Every other part of REL-13 stands, including when this checkbox is …") and line 75
  (the "Mapped to phases" coverage-count line, listing Phase 71: 1 — REL-13). Neither line 33 nor
  75 carries a checkbox or a `Pending`/`Complete` token of its own; neither would change shape
  merely because line 24 or 71 flipped.

**Why the whole-file SHA-256 is the primary probe, not a scoped grep.** Two reasons, both drawn
from this project's own history rather than asserted abstractly:

1. A flip is line-count-neutral — `- [ ]` and `- [x]` are the same length, and a `Pending` →
   `Complete` Traceability-row edit does not add or remove a line. `wc -l` alone cannot detect it;
   only a byte-level digest can.
2. Phase 63's flip moved **three** requirements at once (REL-09, REL-10 and REL-11 together) — a
   grep scoped to `REL-13` alone would have missed the other two entirely. The whole-file digest
   catches any writer of `.planning/REQUIREMENTS.md`, regardless of which requirement ID it
   touches.

## Why this file exists

`phase.complete`-family tooling has auto-flipped the release requirement's checkbox and
Traceability-row state against an explicit CONTEXT decision at **eight consecutive** prior
release-prep closes (`ROADMAP.md` binding constraint 10; `69-CLOSEOUT-GUARD.md` §§ "Why this file
exists" and "Third observation (after phase.complete, orchestrator)"):

- The v0.7.0, v0.7.1, v0.8.0, v0.9.0 and v0.9.1 closes each flipped their respective release
  requirement before this project caught and reverted the flip; Phase 61 was the first to hold,
  using this exact procedure.
- The most recent was REL-12 at the Phase 69 close (v0.9.3): caught by the third observation after
  `phase.complete` and reverted before any commit.
- It has landed through both entry points, `phase.complete` from `/gsd-execute-phase` and
  `/gsd-verify-work`'s inline transition — the same underlying verb, reached through two different
  entry points. Phase 63's flip landed through both entry points in one close.
- REL-13 is again a requirement meant to close only at `/gsd-complete-milestone`, on the observed
  merge (D-09) — its checkbox is deliberately held at `- [ ]` through every plan in this phase.

## Re-verification protocol (phase close)

Plan 71-07 runs exactly these commands against the tree as it stands at its own point in the
phase, and reports whether the Baseline still holds:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare the printed digest against this file's Baseline:
# 4d98e0287552d2dce8f45b7939dfcb0e729523c6869bfa1cd2d1d041119c5636

wc -l .planning/REQUIREMENTS.md
# compare against this file's Baseline: 80

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-13' .planning/REQUIREMENTS.md
# expected: byte-identical to the four quoted lines above (24, 33, 71, 75)
```

## For the operator running phase.complete

This section applies after this phase's plans have finished, at **whichever of the two entry
points runs**: `/gsd-execute-phase`'s `phase.complete` step, or `/gsd-verify-work`'s inline
transition. Both entry points must be treated as equally likely to trigger the flip; neither is
safer to assume clean than the other.

**Before either runs:** back up `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` and
`.planning/STATE.md` to a scratch directory **outside the repository** (e.g.
`/tmp/scratch-71-closeout/`), so a hand-edited STATE.md or ROADMAP.md rewrite that the tooling
itself corrupts has a known-good copy to diff against, not only `.planning/REQUIREMENTS.md`.

**After it runs**, re-run the same probes as § "Re-verification protocol (phase close)" above,
with the baseline digest and grep lines written out inline here so the reader needs no other file
open:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare against: 4d98e0287552d2dce8f45b7939dfcb0e729523c6869bfa1cd2d1d041119c5636

wc -l .planning/REQUIREMENTS.md
# compare against: 80

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-13' .planning/REQUIREMENTS.md
# expected: byte-identical to:
#   24:- [ ] **REL-13**: Close prep only, unpublished: one CHANGELOG bullet under the existing `## [Unreleased]`, in the register of the three bullets already there, naming the API-reference type-text change and noting that the ja translation catalogs pick it up at the next published release; `pyproject.toml` stays `0.9.2`; no tag, no PyPI upload, no GitHub Release. The milestone branch is merged to `main` through a PR, as v0.9.3's REL-12 was. This checkbox is checked only at `/gsd-complete-milestone`, on the observed merge — never by phase-completion tooling.
#   33:  wrong for the same reason. Every other part of REL-13 stands, including when this checkbox is
#   71:| REL-13 | Phase 71 | Pending — coverage only; checked at `/gsd-complete-milestone` on the observed merge, never by phase-completion tooling |
#   75:- Mapped to phases: 6 (Phase 70: 5 — QUA-09, QUA-11, QUA-12, DOC-22, DOC-23; Phase 71: 1 — REL-13)
```

**On any divergence:** run `git checkout -- .planning/REQUIREMENTS.md`, re-run the probes above to
show a MATCH, and then diff `.planning/ROADMAP.md` and `.planning/STATE.md` against the scratch
backup — reverting either if it, too, carries an unwarranted change from the same tooling run.

**The rule: reverted and reported, never committed.** No `/gsd-complete-milestone` step starts
until every probe above shows MATCH. This is the explicit rule this project has followed at every
prior release-prep close where the flip was caught: revert first, report second, never ship the
flipped state as part of the phase's own close.

`71-HANDOFF.md` reproduces this section in full, so an operator following the handoff reaches it
without opening this file separately.

## This task's own effect on `.planning/REQUIREMENTS.md`

```
$ git diff --name-only -- .planning/REQUIREMENTS.md
(no output)

$ git status --porcelain .planning/REQUIREMENTS.md
(no output)
```

Byte-unchanged. REL-13 remains `- [ ]` and Pending, exactly as recorded in § "The lines under
guard" above.

---
*Phase: 71-v0-9-4-close-prep-prep-only-unpublished*
*Plan: 02*
