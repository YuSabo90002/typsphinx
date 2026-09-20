# Phase 75 — Closeout Guard (REL-15 fence)

This file changes no requirement state: REL-15 stays an unchecked box (`- [ ]`) and its
Traceability row stays `Pending`. `.planning/REQUIREMENTS.md` is read and quoted here, never
edited — no plan in Phase 75 writes it.

## Head check and provisioning

- `date -u +%FT%TZ` -> `2026-09-20T08:36:33Z`
- `pwd -P` -> `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ac09f823902b6b804` (under
  `/home/yuta/Documents/typsphinx/.claude/worktrees/`)
- `test -f .git; echo "exit:$?"` -> `exit:0` (worktree confirmed — `.git` is a file)
- `command -v uv` -> `/nix/store/3vpzk25whpm7s8zq5flpk8gbpkggj9np-uv/bin/uv`
- `grep -c typsphinx-fhs-run "$(command -v uv)"` -> `2`

Provisioning line:

```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs
```

Exit status: `0`. `typsphinx==0.9.2` installed editable from this worktree's own checkout path,
along with `sphinx==9.1.0`, `myst-parser==5.1.0`, `furo==2025.12.19` and every other `docs`/`dev`
extra dependency — 90 packages installed.

- `sed -n 's/^home = //p;s/^version_info = //p' .venv/pyvenv.cfg` ->
  `PYVENV_HOME` = `/home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin`,
  `PYVENV_VERSION_INFO` = `3.14` — a fresh worktree resolves a uv-managed CPython 3.14 rather than
  the main checkout's nix-provided 3.13.13; both are otherwise compatible with this plan's tooling.

Key lines:

```
PYVENV_HOME = /home/yuta/.local/share/uv/python/cpython-3.14-linux-x86_64-gnu/bin
PYVENV_VERSION_INFO = 3.14
```

`mktemp -d` -> `/tmp/tmp.Ea8hUnFA4z`.

```
SCRATCH_75_01 = /tmp/tmp.Ea8hUnFA4z
```

## Baseline

Recorded at phase head, inside this plan's isolated worktree
(`worktree-agent-ac09f823902b6b804`), before this plan's first commit.

```
$ git rev-parse HEAD
526a21d352696cb65c570d07d75ef8c7e3aa96a1

$ git log -1 --format='%H %s'
526a21d352696cb65c570d07d75ef8c7e3aa96a1 docs(75): mark phase 75 execution started
```

Subject `docs(75): mark phase 75 execution started` — a phase-tracking commit that predates this
plan's own execution and carries no `(75-0N)` plan-level commit scope. No plan commit has landed
yet.

```
$ git fetch -q origin main && git merge-base HEAD origin/main
6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b
```

`MILESTONE_BASE` confirmed by `git merge-base HEAD origin/main` after fetching `origin main`.

```
$ sha256sum .planning/REQUIREMENTS.md
481e2091ced842747944e80c6e0bdaafc7b2a2385f5e179e77e6b1e62dca603f  .planning/REQUIREMENTS.md

$ wc -l .planning/REQUIREMENTS.md
81 .planning/REQUIREMENTS.md

$ grep -c 'REL-15' .planning/REQUIREMENTS.md
4

$ grep -c 'REL-16' .planning/REQUIREMENTS.md
5

$ git log -1 --format=%H -- .planning/REQUIREMENTS.md
3d6010ab3291a7d93251ceb7bacd5b6f8346b7f0

$ git merge-base --is-ancestor 3d6010ab3291a7d93251ceb7bacd5b6f8346b7f0 526a21d352696cb65c570d07d75ef8c7e3aa96a1; echo "exit:$?"
exit:0

$ date -u +%FT%TZ
2026-09-20T08:36:52Z
```

**Cross-check against the planning-time census.** `75-01-PLAN.md`'s own frontmatter census
(2026-09-20, HEAD `1048b73e`) recorded the same digest, 81 lines, 4 `REL-15` hits and 5 `REL-16`
hits. The fresh commands run above, inside this plan's own isolated worktree, agree digit-for-digit
and byte-for-byte with all four of those values — no drift occurred between planning and this
plan's own execution.

REL-15's checkbox reads `- [ ]` and its Traceability row reads `Pending` (both confirmed in
§ "The lines under guard" below) — the required precondition for this file to proceed rather than
halt.

Key lines:

```
PHASE_BASE_SHA = 526a21d352696cb65c570d07d75ef8c7e3aa96a1
MILESTONE_BASE = 6cc44f22a01f1e9d2080a8220fca2dc2cdcb264b
REQ_SHA256_BASE = 481e2091ced842747944e80c6e0bdaafc7b2a2385f5e179e77e6b1e62dca603f
REQ_LINES_BASE = 81
REL15_HITS_BASE = 4
REL16_HITS_BASE = 5
REQ_LAST_COMMIT = 3d6010ab3291a7d93251ceb7bacd5b6f8346b7f0
GUARD_AT = 2026-09-20T08:36:52Z
```

## The lines under guard

Verbatim output of `grep -n 'REL-15' .planning/REQUIREMENTS.md`, run against this worktree's tree
at the timestamp above:

```
$ grep -n 'REL-15' .planning/REQUIREMENTS.md
22:- [ ] **REL-15**: v0.9.6 is published. `pyproject.toml` goes `0.9.2` → `0.9.6` as the sole version literal, with `uv.lock` regenerated in the same change and `uv sync --extra dev --locked` green. The six bullets standing under `## [Unreleased]` — carried from v0.9.3, v0.9.4 and v0.9.5 — are promoted into a new `## [0.9.6]` section together with this milestone's own bullets, and the link block at the file's end is updated in the same phase: the `[Unreleased]` compare target moves up to `v0.9.6` and a `[0.9.6]` releases/tag link is added. The milestone branch merges to `main` through a PR with CI green across the Linux, Windows and macOS lanes; tag `v0.9.6` is pushed; `release.yml` publishes the wheel and sdist to PyPI and creates the GitHub Release. **This checkbox is checked only at `/gsd-complete-milestone`, against observed evidence (merge commit on `origin/main`'s first-parent history, `git ls-remote --tags origin`, a PyPI 200 for `0.9.6`, and `gh release list`), and never by phase-completion tooling** — `phase.complete` has flipped REL rows against an explicit decision before. Note that `release.yml`'s `create-release` job has end-to-end evidence from the v0.7.1 publish (run `31462027486`) and v0.8.0 (run `31861043480`) but has never run on a v0.9.x tag.
59:| REL-15 | Phase 75 | Pending |
73:**REL-15 is mapped to Phase 75 for coverage only.** Its checkbox is checked at
76:phase artifact — which is why that phase's `REQUIREMENTS.md` fence is line-scoped to REL-15 rather
```

Four hits, as expected from both the baseline probe and the planning-time census.

**Classification:**

- **State-bearing:** line 22 (the requirement bullet's checkbox — `- [ ] **REL-15**`; only the
  leading `- [ ]` token is state-bearing, the rest of the bullet is prose that does not change on a
  flip) and line 59 (the Traceability row — `| REL-15 | Phase 75 | Pending |`). These are the two
  lines whose content would change if the checkbox flipped.
- **Informational:** line 73 (the "REL-15 is mapped to Phase 75 for coverage only" sentence,
  continuing onto line 74 with "at `/gsd-complete-milestone`...") and line 76 (a continuation
  sentence naming why the fence is line-scoped). Neither line carries a checkbox or a
  `Pending`/`Complete` token of its own; neither would change shape merely because line 22 or 59
  flipped.

Both state-bearing lines must be byte-identical at every later observation, and the checkbox must
still read `- [ ] **REL-15**` and the row `| REL-15 | Phase 75 | Pending |`.

## Expected to move: REL-16

Verbatim output of `grep -n 'REL-16' .planning/REQUIREMENTS.md`, run at the same timestamp:

```
$ grep -n 'REL-16' .planning/REQUIREMENTS.md
23:- [ ] **REL-16**: The `### Known Limitations` question is settled on the record for this release. Either `## [0.9.6]` carries such a section naming the carried major defects (NUM-01's per-master `numref` divergence, the converted-image rehome collision, the `typst_documents` duplicate-target cluster), or the release-prep phase's decision record states that the owner declined it and why. v0.9.0's MILESTONES.md entry has a `### Known limitations shipped` precedent, and v0.7.1's D-27 has a precedent for declining one in full; v0.9.5 could leave the question open only because it published nothing. It cannot be left implicit here.
30:- **NUM-01**: `:numref:` numbers diverge per master and vanish for figures reachable only from a non-root master. Only its *disclosure* is in scope this milestone, via REL-16; the fix is not.
47:| Fixing NUM-01, the converted-image rehome collision, or the `typst_documents` duplicate-target cluster | Carried major defects, unchanged in scope. REL-16 decides whether they are *disclosed* in the `## [0.9.6]` notes, not whether they are fixed |
60:| REL-16 | Phase 75 | Pending |
75:(ROADMAP constraints 1 and 9). **REL-16 does close inside Phase 75** — "settled on the record" is a
```

Five hits, as expected from both the baseline probe and the planning-time census.

**Classification:**

- **State-bearing:** line 23 (the checkbox — `- [ ] **REL-16**`) and line 60 (the Traceability row
  — `| REL-16 | Phase 75 | Pending |`).
- **Informational:** line 30 (the NUM-01 bullet under § Future, mentioning REL-16 in passing), line
  47 (a table row in § Out of Scope), and line 75 (the "REL-16 does close inside Phase 75" sentence
  in § Traceability).

**REL-16 closes inside this phase**, so its checkbox and Traceability row **may** legitimately
change to `[x]` / `Complete` when phase-completion tooling runs — Task 3 of `75-07-PLAN.md`
(REL-16 settlement) writes exactly this via ordinary phase-completion tooling, not as an
unwarranted flip. **This is the reason constraint 9's fence is line-scoped to REL-15 this
milestone rather than whole-file**: a whole-file digest would fire on REL-16's own legitimate
completion, indistinguishable from an unwarranted REL-15 flip. No plan in this phase edits
`.planning/REQUIREMENTS.md` itself before phase completion, so `REQ_SHA256_BASE` is expected to
MATCH the live digest at every observation up to and including phase close (75-07's own
re-verification), and to change only after phase-completion tooling has run (at which point the
change is confined to REL-16's two lines).

## Why this file exists

`phase.complete`-family tooling, including `/gsd-verify-work`'s inline transition and
`/gsd-execute-phase`'s tail, has auto-flipped the release requirement's checkbox and
Traceability-row state against an explicit CONTEXT decision at **9 of the 10** prior release-prep
closes (`ROADMAP.md` binding constraint 9; `73-CLOSEOUT-GUARD.md` §§ "Why this file exists" and
"Third observation"). It has fired through both entry points, `phase.complete` from
`/gsd-execute-phase` and `/gsd-verify-work`'s inline transition — the same underlying verb, reached
through two different entry points.

SHA-256 is the primary probe rather than a scoped grep, because a checkbox flip is
line-count-neutral — `- [ ]` and `- [x]` are the same length, and a `Pending` → `Complete`
Traceability-row edit does not add or remove a line, so `wc -l` alone cannot detect it; only a
byte-level digest can. On any divergence the fix is `git checkout -- .planning/REQUIREMENTS.md`,
reported and never committed.

The same tooling has also rewritten other tracking fields at prior closes: `STATE.md`'s
`current_phase_name` field was deleted and `Plan: Not started` was written in its place at Phase
71's close, and `ROADMAP.md`'s Status-cell padding and wrapped list lines have been orphaned at
other closes. Those are not this fence's own guard target, but are why § "Scratch backups" below
also captures `ROADMAP.md` and `STATE.md`.

## Scratch backups

`.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` and `.planning/STATE.md` copied into
`$SCRATCH_75_01` (`/tmp/tmp.Ea8hUnFA4z`), outside the repository, before any later tooling can
rewrite them:

```
$ S=/tmp/tmp.Ea8hUnFA4z
$ cp .planning/REQUIREMENTS.md "$S/p7501_REQUIREMENTS.md"
$ cp .planning/ROADMAP.md "$S/p7501_ROADMAP.md"
$ cp .planning/STATE.md "$S/p7501_STATE.md"
$ sha256sum "$S/p7501_REQUIREMENTS.md" "$S/p7501_ROADMAP.md" "$S/p7501_STATE.md"
481e2091ced842747944e80c6e0bdaafc7b2a2385f5e179e77e6b1e62dca603f  /tmp/tmp.Ea8hUnFA4z/p7501_REQUIREMENTS.md
e4b466787d71ba3108b5853dfb761ce09f8d0e080b8905d83192a372306403a1  /tmp/tmp.Ea8hUnFA4z/p7501_ROADMAP.md
c5c652a23a906f031fd7ac7cca0f84f278adb6e6d7b06d229ada1c0555c77996  /tmp/tmp.Ea8hUnFA4z/p7501_STATE.md
```

The REQUIREMENTS.md backup's digest matches `REQ_SHA256_BASE`
(`481e2091ced842747944e80c6e0bdaafc7b2a2385f5e179e77e6b1e62dca603f`) exactly.

Key lines:

```
BACKUP_REQUIREMENTS = /tmp/tmp.Ea8hUnFA4z/p7501_REQUIREMENTS.md
BACKUP_ROADMAP = /tmp/tmp.Ea8hUnFA4z/p7501_ROADMAP.md
BACKUP_STATE = /tmp/tmp.Ea8hUnFA4z/p7501_STATE.md
```

These exist because the same tooling has orphaned wrapped lines in `ROADMAP.md` and flipped
`STATE.md` status fields (including `current_phase_name`) in prior phases, not only flipped a
checkbox — a hand-correction against these backups is how those side effects get reverted without
guessing at the pre-tooling text.

## Re-verification protocol (phase close)

Plan 75-07 runs exactly these commands against the tree as it stands at its own point in the
phase, and reports whether the Baseline still holds:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare the printed digest against this file's Baseline:
# 481e2091ced842747944e80c6e0bdaafc7b2a2385f5e179e77e6b1e62dca603f

wc -l .planning/REQUIREMENTS.md
# compare against this file's Baseline: 81

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

git log --oneline "526a21d352696cb65c570d07d75ef8c7e3aa96a1"..HEAD -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-15' .planning/REQUIREMENTS.md
# expected: byte-identical to § "The lines under guard" above (lines 22, 59, 73, 76), compared
# line by line in file order
```

## For the operator running phase.complete

This section applies after this phase's plans have finished, at **whichever of the two entry
points runs**: `/gsd-execute-phase`'s `phase.complete` step, or `/gsd-verify-work`'s inline
transition. Both entry points must be treated as equally likely to trigger the flip; neither is
safer to assume clean than the other.

**Three observations are named explicitly, not two:**

1. **Phase head** — this task, recorded above.
2. **Phase close** — Plan 75-07's own re-run of § "Re-verification protocol (phase close)".
3. **Once more, after `phase.complete`-family tooling has actually run** — outside any plan's
   reach, run by the orchestrator or the operator. This is the observation that actually catches
   the flip, because it happens after the tooling call that has fired at 9 of 10 prior
   release-prep closes; `/gsd-verify-work`'s inline transition counts as this tooling exactly as
   much as `/gsd-execute-phase`'s own `phase.complete` step does.

**Before any of the three runs `phase.complete`-family tooling:** `.planning/REQUIREMENTS.md`,
`.planning/ROADMAP.md` and `.planning/STATE.md` are already backed up outside the repository (see
§ "Scratch backups" above, `/tmp/tmp.Ea8hUnFA4z`), so a hand-edited `STATE.md` or `ROADMAP.md`
rewrite that the tooling itself corrupts has a known-good copy to diff against, not only
`.planning/REQUIREMENTS.md`.

**After it runs**, re-run the same four probes, with the baseline digest and grep lines written
out inline here so the reader needs no other file open:

```bash
sha256sum .planning/REQUIREMENTS.md
# compare against: 481e2091ced842747944e80c6e0bdaafc7b2a2385f5e179e77e6b1e62dca603f

wc -l .planning/REQUIREMENTS.md
# compare against: 81

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -n 'REL-15' .planning/REQUIREMENTS.md
# expected: byte-identical to:
#   22:- [ ] **REL-15**: v0.9.6 is published. ... **This checkbox is checked only at `/gsd-complete-milestone`, against observed evidence (merge commit on `origin/main`'s first-parent history, `git ls-remote --tags origin`, a PyPI 200 for `0.9.6`, and `gh release list`), and never by phase-completion tooling** — `phase.complete` has flipped REL rows against an explicit decision before. ...
#   59:| REL-15 | Phase 75 | Pending |
#   73:**REL-15 is mapped to Phase 75 for coverage only.** Its checkbox is checked at
#   76:phase artifact — which is why that phase's `REQUIREMENTS.md` fence is line-scoped to REL-15 rather
```

REL-16's lines (§ "Expected to move: REL-16" above) are **not** part of this guard — its checkbox
and row may legitimately read `[x]` / `Complete` after phase-completion tooling runs, per Task 3 of
`75-07-PLAN.md`.

**On any divergence in the REL-15 lines specifically:** run
`git checkout -- .planning/REQUIREMENTS.md`, re-run the probes above to show a MATCH, and then diff
`.planning/ROADMAP.md` and `.planning/STATE.md` against the scratch backup — reverting either if
it, too, carries an unwarranted change from the same tooling run. If the divergence is confined to
REL-16's two lines flipping to `[x]` / `Complete`, that is the phase's own intended completion
(REL-16 closes here) and is **not** reverted.

**Warning:** the same tooling has rewritten other tracking fields at prior closes — `STATE.md`'s
`current_phase_name` field has been deleted and `Plan: Not started` written in its place, and
`ROADMAP.md`'s Status-cell padding and wrapped list lines have been orphaned. Those are
hand-corrected against the backup; they are not the REL-15 guard's own failure, and correcting them
is not the same action as reverting a REL-15 flip.

**The rule: reverted and reported, never committed.** No `/gsd-complete-milestone` step starts
until the REL-15 probes above show MATCH. This is the explicit rule this project has followed at
every prior release-prep close where the flip was caught: revert first, report second, never ship
the flipped state as part of the phase's own close.

`75-HANDOFF.md` reproduces this section in full, so an operator following the handoff reaches it
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

Byte-unchanged. REL-15 remains `- [ ]` and Pending, exactly as recorded in § "The lines under
guard" above.

## Re-verification at phase close

Run by plan 75-07, inside its own isolated worktree, at `2026-09-20T11:26:20Z` — the second of the
three named observations (§ "For the operator running phase.complete" above; the third happens
after `phase.complete`-family tooling, outside any plan's reach).

```
$ sha256sum .planning/REQUIREMENTS.md
481e2091ced842747944e80c6e0bdaafc7b2a2385f5e179e77e6b1e62dca603f  .planning/REQUIREMENTS.md

$ wc -l < .planning/REQUIREMENTS.md
81

$ git diff --name-only -- .planning/REQUIREMENTS.md
(no output)

$ git diff --name-only 526a21d352696cb65c570d07d75ef8c7e3aa96a1 HEAD -- .planning/REQUIREMENTS.md
(no output)
```

```
REQ_SHA256_CLOSE = 481e2091ced842747944e80c6e0bdaafc7b2a2385f5e179e77e6b1e62dca603f
REQ_LINES_CLOSE = 81
```

Both equal `REQ_SHA256_BASE` (`481e2091ced842747944e80c6e0bdaafc7b2a2385f5e179e77e6b1e62dca603f`) and
`REQ_LINES_BASE` (`81`) exactly, and both diffs are empty — the working tree and the whole phase
range alike.

```
$ grep -n 'REL-15' .planning/REQUIREMENTS.md
22:- [ ] **REL-15**: v0.9.6 is published. `pyproject.toml` goes `0.9.2` → `0.9.6` as the sole version literal, with `uv.lock` regenerated in the same change and `uv sync --extra dev --locked` green. The six bullets standing under `## [Unreleased]` — carried from v0.9.3, v0.9.4 and v0.9.5 — are promoted into a new `## [0.9.6]` section together with this milestone's own bullets, and the link block at the file's end is updated in the same phase: the `[Unreleased]` compare target moves up to `v0.9.6` and a `[0.9.6]` releases/tag link is added. The milestone branch merges to `main` through a PR with CI green across the Linux, Windows and macOS lanes; tag `v0.9.6` is pushed; `release.yml` publishes the wheel and sdist to PyPI and creates the GitHub Release. **This checkbox is checked only at `/gsd-complete-milestone`, against observed evidence (merge commit on `origin/main`'s first-parent history, `git ls-remote --tags origin`, a PyPI 200 for `0.9.6`, and `gh release list`), and never by phase-completion tooling** — `phase.complete` has flipped REL rows against an explicit decision before. Note that `release.yml`'s `create-release` job has end-to-end evidence from the v0.7.1 publish (run `31462027486`) and v0.8.0 (run `31861043480`) but has never run on a v0.9.x tag.
59:| REL-15 | Phase 75 | Pending |
73:**REL-15 is mapped to Phase 75 for coverage only.** Its checkbox is checked at
76:phase artifact — which is why that phase's `REQUIREMENTS.md` fence is line-scoped to REL-15 rather
```

Byte-identical, line for line, to § "The lines under guard" above (lines 22, 59, 73, 76).

```
REL15_LINES_MATCH = yes
```

The two direct reads SC5 requires:

```
$ grep -m1 -E '^- \[.\] \*\*REL-15\*\*' .planning/REQUIREMENTS.md
- [ ] **REL-15**: v0.9.6 is published. ...

$ grep -m1 -E '^\| REL-15 \|' .planning/REQUIREMENTS.md
| REL-15 | Phase 75 | Pending |
```

```
REL15_CHECKBOX_AT_CLOSE = - [ ] **REL-15**
REL15_TRACEABILITY_AT_CLOSE = | REL-15 | Phase 75 | Pending |
```

REL-15's checkbox still reads unchecked and its traceability row still reads `Pending`, read
directly out of the file.

`grep -n 'REL-16' .planning/REQUIREMENTS.md` at the same timestamp:

```
23:- [ ] **REL-16**: The `### Known Limitations` question is settled on the record for this release. Either `## [0.9.6]` carries such a section naming the carried major defects (NUM-01's per-master `numref` divergence, the converted-image rehome collision, the `typst_documents` duplicate-target cluster), or the release-prep phase's decision record states that the owner declined it and why. v0.9.0's MILESTONES.md entry has a `### Known limitations shipped` precedent, and v0.7.1's D-27 has a precedent for declining one in full; v0.9.5 could leave the question open only because it published nothing. It cannot be left implicit here.
30:- **NUM-01**: `:numref:` numbers diverge per master and vanish for figures reachable only from a non-root master. Only its *disclosure* is in scope this milestone, via REL-16; the fix is not.
47:| Fixing NUM-01, the converted-image rehome collision, or the `typst_documents` duplicate-target cluster | Carried major defects, unchanged in scope. REL-16 decides whether they are *disclosed* in the `## [0.9.6]` notes, not whether they are fixed |
60:| REL-16 | Phase 75 | Pending |
75:(ROADMAP constraints 1 and 9). **REL-16 does close inside Phase 75** — "settled on the record" is a
```

REL-16's checkbox (line 23) and traceability row (line 60) have **not yet moved** — as expected, since
no plan in this phase edits the file and phase-completion tooling has not yet run.

```
FENCE_CLOSE_VERDICT = MATCH
```

The digest, the line count, both empty diffs, and the byte-identical REL-15 transcript all hold.

**`.planning/ROADMAP.md` and `.planning/STATE.md` against the scratch backups (75-01's).**

```
$ diff /tmp/tmp.Ea8hUnFA4z/p7501_ROADMAP.md .planning/ROADMAP.md
562c562
< **Plans**: 7 plans (4 waves)
---
> **Plans**: 6/7 plans executed (4 waves)
568c568
< - [ ] 75-01-PLAN.md — Closeout-guard baseline on REL-15, the clean C-locale documentation ledger at
---
> - [x] 75-01-PLAN.md — Closeout-guard baseline on REL-15, the clean C-locale documentation ledger at
570c570
< - [ ] 75-02-PLAN.md — Phase 74's leftovers: delete the five untracked `probe_*.typ` scratch files,
---
> - [x] 75-02-PLAN.md — Phase 74's leftovers: delete the five untracked `probe_*.typ` scratch files,
572c572
< - [ ] 75-03-PLAN.md — The one commit: version `0.9.6` across `pyproject.toml` / `uv.lock` /
---
> - [x] 75-03-PLAN.md — The one commit: version `0.9.6` across `pyproject.toml` / `uv.lock` /
579c579
< - [ ] 75-04-PLAN.md — Green-tree evidence on the bumped tip: lint trio, pytest twice, clean
---
> - [x] 75-04-PLAN.md — Green-tree evidence on the bumped tip: lint trio, pytest twice, clean
581c581
< - [ ] 75-05-PLAN.md — Non-committing trial merge against `origin/main`, `main`'s protection and
---
> - [x] 75-05-PLAN.md — Non-committing trial merge against `origin/main`, `main`'s protection and
586c586
< - [ ] 75-06-PLAN.md — Push the bumped tip and dispatch exactly one CI run, waited to completion with
---
> - [x] 75-06-PLAN.md — Push the bumped tip and dispatch exactly one CI run, waited to completion with
611c611
< | 75. v0.9.6 Release Prep (prep-only) | v0.9.6 | 0/TBD | Not started | - |
---
> | 75. v0.9.6 Release Prep (prep-only) | v0.9.6 | 6/7 | In Progress | - |
```

Every hunk is the expected, legitimate per-plan progress tracking (75-01 through 75-06 checkboxes
flipping to `[x]` and the progress table row advancing as each plan finished) — none of it is a
REQUIREMENTS-style unwarranted rewrite, no wrapped-line orphaning, no Status-cell mangling.

```
$ diff /tmp/tmp.Ea8hUnFA4z/p7501_STATE.md .planning/STATE.md
(no output, exit:0)
```

`STATE.md` is byte-identical to its 75-01 scratch backup — no drift at all.

---
*Phase: 75-v0-9-6-release-prep-prep-only*
*Plan: 01*
