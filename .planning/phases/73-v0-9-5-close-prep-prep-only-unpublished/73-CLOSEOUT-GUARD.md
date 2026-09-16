# Phase 73 — REL-14 Checkbox-Flip Closeout Guard

This file changes no requirement state: REL-14 stays an unchecked box (`- [ ]`) and its
Traceability row stays `Pending`. `.planning/REQUIREMENTS.md` is read and quoted here, never
edited (D-08: no Phase 73 plan writes it).

## Baseline

Recorded at phase head, inside this plan's isolated worktree
(`worktree-agent-a347b03dff012a923`), before this plan's first commit.

```
$ git rev-parse HEAD
c6bc641aa1745e6413b4f33c4d0c572a962da430

$ git log -1 --format='%H %s'
c6bc641aa1745e6413b4f33c4d0c572a962da430 docs(state): begin phase 73 execution
```

Subject `docs(state): begin phase 73 execution` — a phase-tracking commit that predates this
plan's own execution and carries no `(73-0N)` plan-level commit scope. No plan commit has landed
yet.

**The Phase 72 tie.** `PUSHED_SHA` read from
`.planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-CI-EVIDENCE.md`:

```
$ sed -n "s/^PUSHED_SHA = //p" .planning/phases/72-tox-e-linkcheck-and-root-toctree-deduplication/72-CI-EVIDENCE.md
0b2595df21399363f50e5e1a55935f470e0df00d

$ git merge-base --is-ancestor 0b2595df21399363f50e5e1a55935f470e0df00d c6bc641aa1745e6413b4f33c4d0c572a962da430; echo "exit:$?"
exit:0

$ git diff --name-only 0b2595df21399363f50e5e1a55935f470e0df00d c6bc641aa1745e6413b4f33c4d0c572a962da430 -- . ':(exclude).planning'
(no output)
```

Key line:

```
PHASE_BASE_PRODUCT_EQUALS_P72_TIP = yes
```

The product tree this phase starts from is byte-identical, outside `.planning/`, to the tree
Phase 72's CI run (`34761445288`, 12/12 green) actually tested — Phase 72's pushed tip is an
ancestor of this phase's base, and nothing outside `.planning/` differs between them.

**The REQUIREMENTS.md-last-touch tie.**

```
$ git log -1 --format=%H -- .planning/REQUIREMENTS.md
1b8d0884b05ab4d3326e92018c3ca9ca95d72082

$ git merge-base --is-ancestor 1b8d0884b05ab4d3326e92018c3ca9ca95d72082 c6bc641aa1745e6413b4f33c4d0c572a962da430; echo "exit:$?"
exit:0
```

Key line:

```
REQ_LAST_COMMIT = 1b8d0884b05ab4d3326e92018c3ca9ca95d72082
```

The last commit that touched `.planning/REQUIREMENTS.md` is an ancestor of `PHASE_BASE_SHA` — no
edit to the file has landed after the recorded phase base, and none can have landed before this
plan's own commit exists to compare against.

**The digest, line count and hit count.**

```
$ sha256sum .planning/REQUIREMENTS.md
7a21a1e48d7abfe4f1e8696dbcb40c5ffe0da4fc95bc9a790ee8501a5812bcad  .planning/REQUIREMENTS.md

$ wc -l .planning/REQUIREMENTS.md
70 .planning/REQUIREMENTS.md

$ grep -c 'REL-14' .planning/REQUIREMENTS.md
4

$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-09-16T09:55:15Z
```

Key lines:

```
PHASE_BASE_SHA = c6bc641aa1745e6413b4f33c4d0c572a962da430
REQ_SHA256_BASE = 7a21a1e48d7abfe4f1e8696dbcb40c5ffe0da4fc95bc9a790ee8501a5812bcad
REQ_LINES_BASE = 70
REL14_HITS_BASE = 4
GUARD_AT = 2026-09-16T09:55:15Z
```

**Cross-check against the planning-time census.** `73-02-PLAN.md`'s own frontmatter census
(2026-09-14, main checkout at `9d276727`) recorded 70 lines and 4 `REL-14` hits. The fresh
commands run above, inside this plan's own isolated worktree, agree digit-for-digit with both of
those values: same line count, same hit count. No drift occurred between planning and this plan's
own execution; `.planning/REQUIREMENTS.md` has not changed in the interim. The fresh values above
are kept as the baseline, per the plan's own instruction to prefer a freshly-measured value even
when it agrees with the census.

REL-14's checkbox reads `- [ ]` and its Traceability row reads `Pending` (both confirmed in
§ "The lines under guard" below) — the required precondition for this file to proceed rather than
halt.

## The lines under guard

Verbatim output of `grep -n 'REL-14' .planning/REQUIREMENTS.md`, run against this worktree's tree
at the timestamp above:

```
$ grep -n 'REL-14' .planning/REQUIREMENTS.md
22:- [ ] **REL-14**: Close prep only, unpublished. CHANGELOG bullet(s) go under the existing `## [Unreleased]`, in the register of the four bullets already there, and name the docs sidebar fix and the new `tox -e linkcheck` environment (owner decision 2026-09-13; revised the same day when QUA-08, the CI job, was deferred — no bullet may claim a CI job that does not exist). `pyproject.toml` stays `0.9.2`. There is no tag, no PyPI upload and no GitHub Release. The milestone branch is merged to `main` through a PR, as REL-12 and REL-13 were. This checkbox is checked only at `/gsd-complete-milestone`, on the observed merge, and never by phase-completion tooling.
57:| REL-14 | Phase 73 | Pending |
62:- Mapped to phases: 4 (Phase 72: QUA-13, DOC-24, DOC-18 · Phase 73: REL-14)
65:- REL-14 is mapped to Phase 73 for coverage only; its checkbox is checked at
```

Four hits, as expected from both the baseline probe and the planning-time census.

**Classification:**

- **State-bearing:** line 22 (the requirement bullet's checkbox — `- [ ] **REL-14**`, whose bullet
  continues with prose describing the no-tag / no-PyPI-upload / no-GitHub-Release /
  `pyproject.toml` still-`0.9.2` conditions — only the leading `- [ ]` token is state-bearing) and
  line 57 (the Traceability row — `| REL-14 | Phase 73 | Pending |`). These are the two lines
  whose content would change if the checkbox flipped.
- **Informational:** line 62 (the "Mapped to phases" coverage-count line, listing Phase 73:
  REL-14) and line 65 (the "REL-14 is mapped to Phase 73 for coverage only" line, continuing onto
  the next line with "its checkbox is checked at `/gsd-complete-milestone`..."). Neither line
  carries a checkbox or a `Pending`/`Complete` token of its own; neither would change shape merely
  because line 22 or 57 flipped.

**Why the whole-file SHA-256 is the primary probe, not a scoped grep.** Two reasons, both drawn
from this project's own history rather than asserted abstractly:

1. A flip is line-count-neutral — `- [ ]` and `- [x]` are the same length, and a `Pending` →
   `Complete` Traceability-row edit does not add or remove a line. `wc -l` alone cannot detect it;
   only a byte-level digest can.
2. Phase 63's flip moved **three** requirements at once (REL-09, REL-10 and REL-11 together) — a
   grep scoped to `REL-14` alone would have missed the other two entirely. The whole-file digest
   catches any writer of `.planning/REQUIREMENTS.md`, regardless of which requirement ID it
   touches.

## Why this file exists

`phase.complete`-family tooling has auto-flipped the release requirement's checkbox and
Traceability-row state against an explicit CONTEXT decision at **8 of the 9** prior release-prep
closes (`ROADMAP.md` binding constraint 10; `71-CLOSEOUT-GUARD.md` §§ "Why this file exists" and
"Third observation (after phase.complete, orchestrator)"):

- It has fired at every prior release-prep close except one: it did **not** fire at Phase 71
  (v0.9.4's close, REL-13) — the third observation there recorded `phase.complete 71` returning
  `requirements_updated: false` and the REL-13 fence holding. One non-firing close is not treated
  as a fix; the mechanism that produced 8 flips before it is unchanged.
- It has landed through both entry points, `phase.complete` from `/gsd-execute-phase` and
  `/gsd-verify-work`'s inline transition — the same underlying verb, reached through two different
  entry points. Phase 63's flip landed through both entry points in one close.
- REL-14 is again a requirement meant to close only at `/gsd-complete-milestone`, on the observed
  merge (D-08) — its checkbox is deliberately held at `- [ ]` through every plan in this phase.

## Re-verification protocol (phase close)

Plan 73-07 runs exactly these commands against the tree as it stands at its own point in the
phase, and reports whether the Baseline still holds:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare the printed digest against this file's Baseline:
# 7a21a1e48d7abfe4f1e8696dbcb40c5ffe0da4fc95bc9a790ee8501a5812bcad

wc -l .planning/REQUIREMENTS.md
# compare against this file's Baseline: 70

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

git log --oneline "c6bc641aa1745e6413b4f33c4d0c572a962da430"..HEAD -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-14' .planning/REQUIREMENTS.md
# expected: byte-identical to § "The lines under guard" above (lines 22, 57, 62, 65), compared
# line by line in file order
```

## For the operator running phase.complete

This section applies after this phase's plans have finished, at **whichever of the two entry
points runs**: `/gsd-execute-phase`'s `phase.complete` step, or `/gsd-verify-work`'s inline
transition. Both entry points must be treated as equally likely to trigger the flip; neither is
safer to assume clean than the other.

**Before either runs:** back up `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` and
`.planning/STATE.md` to a scratch directory **outside the repository** (e.g.
`/tmp/scratch-73-closeout/`), so a hand-edited STATE.md or ROADMAP.md rewrite that the tooling
itself corrupts has a known-good copy to diff against, not only `.planning/REQUIREMENTS.md`.

**After it runs**, re-run the same probes as § "Re-verification protocol (phase close)" above,
with the baseline digest and grep lines written out inline here so the reader needs no other file
open:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare against: 7a21a1e48d7abfe4f1e8696dbcb40c5ffe0da4fc95bc9a790ee8501a5812bcad

wc -l .planning/REQUIREMENTS.md
# compare against: 70

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-14' .planning/REQUIREMENTS.md
# expected: byte-identical to:
#   22:- [ ] **REL-14**: Close prep only, unpublished. CHANGELOG bullet(s) go under the existing `## [Unreleased]`, in the register of the four bullets already there, and name the docs sidebar fix and the new `tox -e linkcheck` environment (owner decision 2026-09-13; revised the same day when QUA-08, the CI job, was deferred — no bullet may claim a CI job that does not exist). `pyproject.toml` stays `0.9.2`. There is no tag, no PyPI upload and no GitHub Release. The milestone branch is merged to `main` through a PR, as REL-12 and REL-13 were. This checkbox is checked only at `/gsd-complete-milestone`, on the observed merge, and never by phase-completion tooling.
#   57:| REL-14 | Phase 73 | Pending |
#   62:- Mapped to phases: 4 (Phase 72: QUA-13, DOC-24, DOC-18 · Phase 73: REL-14)
#   65:- REL-14 is mapped to Phase 73 for coverage only; its checkbox is checked at
```

**On any divergence:** run `git checkout -- .planning/REQUIREMENTS.md`, re-run the probes above to
show a MATCH, and then diff `.planning/ROADMAP.md` and `.planning/STATE.md` against the scratch
backup — reverting either if it, too, carries an unwarranted change from the same tooling run.

**Warning:** the same tooling has also rewritten other tracking fields at Phase 71's close:
STATE.md's `current_phase_name` field was deleted and `Plan: Not started` was written in its
place, and ROADMAP.md's Status-cell padding was altered. Those are hand-corrected against the
backup; they are not the REL-14 guard's own failure, and correcting them is not the same action as
reverting a REL-14 flip.

**The rule: reverted and reported, never committed.** No `/gsd-complete-milestone` step starts
until every probe above shows MATCH. This is the explicit rule this project has followed at every
prior release-prep close where the flip was caught: revert first, report second, never ship the
flipped state as part of the phase's own close.

`73-HANDOFF.md` reproduces this section in full, so an operator following the handoff reaches it
without opening this file separately. The orchestrator appends a
`## Third observation (after phase.complete, orchestrator)` section here after
`phase.complete`-family tooling actually runs.

## This task's own effect on `.planning/REQUIREMENTS.md`

```
$ git diff --name-only -- .planning/REQUIREMENTS.md
(no output)

$ git status --porcelain .planning/REQUIREMENTS.md
(no output)
```

Byte-unchanged. REL-14 remains `- [ ]` and Pending, exactly as recorded in § "The lines under
guard" above.

## Re-verification at phase close

Plan 73-07's own re-run, inside this plan's isolated worktree
(`worktree-agent-a636a3db27a239f62`), of exactly the commands § "Re-verification protocol (phase
close)" names, against the tree as it stands at this plan's own point in the phase (wave 4, after
plans 73-01 through 73-06 have merged).

```
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-09-16T10:43:55Z
```

Key line:

```
CLOSE_AT = 2026-09-16T10:43:55Z
```

```
$ test -f .git; echo "exit:$?"
exit:0

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a636a3db27a239f62

$ git rev-parse HEAD
b716107f30a6180e9accb734011231010fe2a793
```

```
$ git merge-base --is-ancestor c6bc641aa1745e6413b4f33c4d0c572a962da430 HEAD; echo "exit:$?"
exit:0
```

`PHASE_BASE_SHA` is an ancestor of this plan's own HEAD.

```
$ sha256sum .planning/REQUIREMENTS.md
7a21a1e48d7abfe4f1e8696dbcb40c5ffe0da4fc95bc9a790ee8501a5812bcad  .planning/REQUIREMENTS.md
```

| | Digest |
|---|---|
| `REQ_SHA256_BASE` (§ "Baseline") | `7a21a1e48d7abfe4f1e8696dbcb40c5ffe0da4fc95bc9a790ee8501a5812bcad` |
| `REQ_SHA256_CLOSE` (this section) | `7a21a1e48d7abfe4f1e8696dbcb40c5ffe0da4fc95bc9a790ee8501a5812bcad` |

Key line:

```
REQ_SHA256_CLOSE = 7a21a1e48d7abfe4f1e8696dbcb40c5ffe0da4fc95bc9a790ee8501a5812bcad
```

MATCH against `REQ_SHA256_BASE`.

```
$ wc -l .planning/REQUIREMENTS.md
70 .planning/REQUIREMENTS.md
```

Key line:

```
REQ_LINES_CLOSE = 70
```

MATCH against `REQ_LINES_BASE = 70`.

```
$ git diff --name-only -- .planning/REQUIREMENTS.md
(no output)
```

MATCH — empty.

```
$ git log --oneline "c6bc641aa1745e6413b4f33c4d0c572a962da430"..HEAD -- .planning/REQUIREMENTS.md
(no output)
```

MATCH — empty. No commit in the phase, through this plan's own tip, touched `.planning/REQUIREMENTS.md`.

```
$ git status --porcelain .planning/REQUIREMENTS.md
(no output)
```

**The REL-14 grep, compared line by line, in file order, against § "The lines under guard" (edge: ordering):**

```
$ grep -n 'REL-14' .planning/REQUIREMENTS.md
22:- [ ] **REL-14**: Close prep only, unpublished. CHANGELOG bullet(s) go under the existing `## [Unreleased]`, in the register of the four bullets already there, and name the docs sidebar fix and the new `tox -e linkcheck` environment (owner decision 2026-09-13; revised the same day when QUA-08, the CI job, was deferred — no bullet may claim a CI job that does not exist). `pyproject.toml` stays `0.9.2`. There is no tag, no PyPI upload and no GitHub Release. The milestone branch is merged to `main` through a PR, as REL-12 and REL-13 were. This checkbox is checked only at `/gsd-complete-milestone`, on the observed merge, and never by phase-completion tooling.
57:| REL-14 | Phase 73 | Pending |
62:- Mapped to phases: 4 (Phase 72: QUA-13, DOC-24, DOC-18 · Phase 73: REL-14)
65:- REL-14 is mapped to Phase 73 for coverage only; its checkbox is checked at
```

Byte-identical, line by line, in file order, to § "The lines under guard" above (lines 22, 57, 62,
65). MATCH.

```
$ grep -c 'REL-14' .planning/REQUIREMENTS.md
4
```

Equal to `REL14_HITS_BASE = 4`. MATCH.

| Probe | Baseline | Close | Verdict |
|---|---|---|---|
| `REQ_SHA256_*` | `7a21a1e4…12bcad` | `7a21a1e4…12bcad` | MATCH |
| `REQ_LINES_*` | 70 | 70 | MATCH |
| `git diff --name-only` | — | empty | MATCH |
| `git log … -- REQUIREMENTS.md` | — | empty | MATCH |
| `grep -n 'REL-14'` (4 lines) | lines 22, 57, 62, 65 | identical, line by line | MATCH |
| `grep -c 'REL-14'` | 4 | 4 | MATCH |

REL-14's checkbox and Traceability row, read directly from the file at this plan's own point in
the phase (never inferred from any SUMMARY frontmatter — every plan of this phase, including this
one, declares `requirements-completed: []`):

```
- [ ] **REL-14**: …
```

```
| REL-14 | Phase 73 | Pending |
```

Every comparison holds:

```
REQ_VERDICT_CLOSE = MATCH
```

No divergence occurred, so no `### Divergence detected and reverted` subsection is written and no
`git checkout -- .planning/REQUIREMENTS.md` was needed.

§ "For the operator running phase.complete" (above) is present and unedited by this task — it was
read in full as part of this task's `<read_first>` and confirmed to be the same section 73-02
wrote, byte for byte, with no re-ordering.

The decisive third observation — the one that runs after `phase.complete`-family tooling actually
executes, outside any plan's reach — is still owed. `73-HANDOFF.md` (plan 73-07, Task 2)
reproduces the procedure inline so the operator reaches it without opening this file separately.
The orchestrator appends the actual `## Third observation (after phase.complete, orchestrator)`
section here once that tooling has run.

---
*Phase: 73-v0-9-5-close-prep-prep-only-unpublished*
*Plan: 02, 07*
