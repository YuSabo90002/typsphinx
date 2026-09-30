# Phase 67 Plan 05 — Closure Evidence (SC#4 D-06, ordering, requirement closure)

This plan's own worktree, provisioned with the CLAUDE.md line; git and gh only; the main checkout
is never touched.

## Head check and provisioning

```
$ test -f .git; echo "exit:$?"
exit:0

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a39a582f04ace6f54

$ git log --oneline -1
a38a9256 docs(phase-67): update tracking after wave 3, mark wave 4 executing
```

```
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
... (91 resolved packages, including uv==0.12.13, tox==4.56.1, ruff==0.15.20, sphinx==9.1.0,
     typsphinx==0.9.2 built editable from this worktree)
```

```
$ gh auth status
github.com
  ✓ Logged in to github.com account YuSabo90002 (/home/yuta/.config/gh/hosts.yml)
  - Active account: true
```

```
$ git rev-parse HEAD
a38a9256f0c23f9bbf07b062f4e2cf2d97e958dc
```

BASE_67_05 = a38a9256f0c23f9bbf07b062f4e2cf2d97e958dc

## Wave gate and live re-assertion

Precondition keys, each read from the three wave evidence files with `sed -n 's/^KEY = //p' <file>
| head -n 1`:

```
$ sed -n 's/^DEP02_VERDICT = //p' .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-PROOF-EVIDENCE.md | head -n 1
MET

$ sed -n 's/^OWNER_DECISION_138 = //p' .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-RUFF-EVIDENCE.md | head -n 1
merge

$ sed -n 's/^OWNER_DECISION_123 = //p' .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-RUFF-EVIDENCE.md | head -n 1
close

$ sed -n 's/^OWNER_DECISION_128 = //p' .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-DOCUTILS-EVIDENCE.md | head -n 1
close
```

All four disposition keys read as required by this plan's `<precondition>`.

Every other key named in the precondition, each read the same way:

```
(cited from 67-RUFF-EVIDENCE.md / 67-DOCUTILS-EVIDENCE.md / 67-PROOF-EVIDENCE.md, not re-declared here)
MERGE_SHA_138 = cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a
MERGED_AT_138 = 2026-09-12T13:37:03Z
CLOSED_AT_123 = 2026-09-12T13:52:17Z
CLOSED_AT_128 = 2026-09-12T13:38:31Z
APPROVED_COMMENT_123 = Superseded by #138.
APPROVED_COMMENT_128 = Sphinx 9.1.0 caps docutils<0.23,>=0.21, so this range can't be exercised yet (uv resolution fails). Closing; dependabot will re-propose once Sphinx relaxes the cap.
DEP02_PROOF_AT = 2026-09-12T13:18:08Z
DECIDED_AT_138 = 2026-09-12T13:36:41Z
DECIDED_AT_128 = 2026-09-12T13:36:46Z
DECIDED_AT_123 = 2026-09-12T13:51:28Z
PROOF_RUN_ID = 34689041575
PROOF_SHA = 88088071e02a7411800f504e06b1ded9d6891cc7
```

`## HALT` heading count in each of the three files:

```
$ grep -c '^## HALT' .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-PROOF-EVIDENCE.md
0
$ grep -c '^## HALT' .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-RUFF-EVIDENCE.md
0
$ grep -c '^## HALT' .planning/phases/67-proof-on-a-real-dependabot-pr-then-disposal-of-123-and-128/67-DOCUTILS-EVIDENCE.md
0
```

Zero `## HALT` headings in all three files.

**Live re-assertion**, run fresh in this plan (not copied from the wave files):

```
$ gh pr view 138 --json state,mergeCommit,mergedAt
{"mergeCommit":{"oid":"cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a"},"mergedAt":"2026-09-12T13:37:03Z","state":"MERGED"}
```

#138 is MERGED at `cf3305ce52b72bb8ca3fa8f9d78fd12a50a3564a`, equal to `MERGE_SHA_138`.

```
$ gh pr view 123 --json state,closedAt,comments
{"state":"CLOSED","closedAt":"2026-09-12T13:52:17Z", "comments":[
  {"author":{"login":"dependabot"}, ...},
  {"author":{"login":"YuSabo90002"},"authorAssociation":"OWNER","body":"Superseded by #138.\n", "createdAt":"2026-09-12T13:52:14Z", ...},
  {"author":{"login":"dependabot"}, ...}
]}
```

```
$ gh pr view 128 --json state,closedAt,comments
{"state":"CLOSED","closedAt":"2026-09-12T13:38:31Z", "comments":[
  {"author":{"login":"dependabot"}, ...},
  {"author":{"login":"YuSabo90002"},"authorAssociation":"OWNER","body":"Sphinx 9.1.0 caps docutils<0.23,>=0.21, so this range can't be exercised yet (uv resolution fails). Closing; dependabot will re-propose once Sphinx relaxes the cap.\n", "createdAt":"2026-09-12T13:38:27Z", ...},
  {"author":{"login":"dependabot"}, ...}
]}
```

```
$ gh api user --jq .login
YuSabo90002
```

Both #123 and #128 are CLOSED. Excluding dependabot's own automated notices, each carries exactly
one owner-authored comment (`YuSabo90002`), byte-identical (modulo a trailing newline GitHub adds)
to `APPROVED_COMMENT_123` and `APPROVED_COMMENT_128` respectively.

**A-67-01 re-check.**

```
$ gh run view 34689041575 --json attempt,conclusion,headSha
{"attempt":1,"conclusion":"success","headSha":"88088071e02a7411800f504e06b1ded9d6891cc7"}
```

The run resolves at `PROOF_SHA` (`88088071e02a7411800f504e06b1ded9d6891cc7`) with `attempt: 1`.

A6701_STATUS = held

## SC#4 grouped-update coverage gap (D-06)

**Measurements**, each re-measured live in this plan:

```
$ grep -n 'AMENDED 2026-09-12 (Phase 67 discuss' .planning/ROADMAP.md .planning/PROJECT.md
.planning/ROADMAP.md:586:     > **AMENDED 2026-09-12 (Phase 67 discuss, owner-approved).** The premise "neither #123 nor #128
.planning/PROJECT.md:126:  > **AMENDED 2026-09-12 (Phase 67 discuss, owner-approved).** #128 **is** a `sphinx-typst-stack`
```

Both AMENDED blocks are present at least once each, cited by line number, and this plan has not
edited either file (confirmed by the protected-path `git diff --quiet` in the verify step below).

```
$ gh pr view 128 --json title,headRefName
{"headRefName":"dependabot/pip/sphinx-typst-stack-12b5b89b5a","title":"chore(deps): update docutils requirement from <0.23,>=0.21 to >=0.21,<0.24 in the sphinx-typst-stack group across 1 directory"}
```

`#128`'s title names "sphinx-typst-stack group" and its branch is `dependabot/pip/sphinx-typst-stack-12b5b89b5a` — it is a group PR.

```
$ gh pr view 138 --json title,headRefName
{"headRefName":"dependabot/uv/ruff-0.16.6","title":"chore(deps): bump ruff from 0.15.20 to 0.16.6"}
```

`#138`'s title and branch name no group — it is not grouped.

```
$ gh pr list --state all --author app/dependabot --limit 200 --json number,headRefName,state --jq '[.[] | select(.headRefName | startswith("dependabot/uv/sphinx-typst-stack"))]'
[]
```

UV_GROUP_PR_COUNT = 0

No `dependabot/uv/sphinx-typst-stack*` PR has ever existed, at any state, live-checked.

```
$ gh run view 34688990228 --log | grep -m3 'dependency_file_not_resolvable'
Dependabot	Run Dependabot	2026-09-12T10:39:32.0638606Z updater | 2026/09/12 10:39:32 INFO <job_1572468102> Handled error whilst updating docutils: dependency_file_not_resolvable {message: "× No solution found when resolving dependencies for split (markers:\n  │ python_full_version >= '3.15'):\n  ╰─▶ Because sphinx>=9.1.0 depends on docutils>=0.21,<0.23 and your project\n      depends on docutils==0.23, we can conclude that sphinx>=9.1.0 and your\n      project are incompatible. ...
Dependabot	Run Dependabot	2026-09-12T10:40:54.2710322Z | docutils   | dependency_file_not_resolvable | { ...
```

The `uv` updater's own attempt to bump `docutils` (the `sphinx-typst-stack` group's member) failed
with `dependency_file_not_resolvable`, re-confirming `66-DEPENDABOT-EVIDENCE.md` § "uv update job
conclusion (HALT resolved by owner ruling, AMENDED 2026-09-12)", which records the identical
resolver contradiction (Sphinx 9.1.0's `docutils<0.23,>=0.21` cap versus the group's proposed
`docutils==0.23`).

**Literal reading** (ROADMAP Phase 67 SC#4, quoted verbatim):

> **The grouped-update coverage gap is recorded explicitly rather than passed over.** Neither
> #123 (ruff) nor #128 (docutils) is a grouped bump, so **neither exercises the
> `sphinx-typst-stack` path** — a grouped multi-package update can hit a genuinely unresolvable
> dependency graph, a different failure from the stale-lockfile mismatch this milestone repairs.
> The phase states in writing that this milestone's proof does not cover that path, so a future
> grouped PR failing at resolution is recognized as an uncovered case rather than misread as a
> regression of this fix (DEP-05, Pitfall 7).

Taken at face value, SC#4's own premise ("neither #123 nor #128 is a grouped bump") is false — see
the `#128` measurement above. Independent of that premise error, the literal conclusion still
holds: this milestone's proof does not cover the `sphinx-typst-stack` grouped path under `uv`, and
a future grouped PR failing at resolution is an **uncovered case, not a regression** of this fix.

**Amended reading** (D-06, owner-approved, `ROADMAP.md` and `PROJECT.md` AMENDED 2026-09-12
blocks cited above):

- SC#4's premise "neither #123 nor #128 is a grouped bump" is **falsified** by the `#128`
  measurement above: `#128` **is** a `sphinx-typst-stack` group PR (title and branch quoted live).
- Under `uv`, no group PR opened (`UV_GROUP_PR_COUNT = 0`), because the group's `docutils` member
  hit `dependency_file_not_resolvable` (re-confirmed above, citing `66-DEPENDABOT-EVIDENCE.md` §
  "uv update job conclusion"). That failure is itself a **live instance** of the "genuinely
  unresolvable dependency graph" SC#4 names — not a different failure that SC#4 failed to
  anticipate, but exactly the shape SC#4 describes, observed once already.
- The PR that carries this milestone's proof, `#138`, is **not** grouped.
- The conclusion is **unchanged**: the milestone's proof does not cover a grouped `uv` update.
  A future grouped PR failing at resolution remains an **uncovered case, not a regression** of
  this fix.

`REQUIREMENTS.md` DEP-05 stays literal — its text is correct and is not edited by any Phase 67
plan.

`PROJECT.md`'s neighbouring claim (line ~132-135, "They will need closing so the `uv` ecosystem
opens fresh ones") is superseded by Phase 66's own measurement: `#138` opened at
`2026-09-12T10:39:49Z` while `#123` was still open, so the `uv` ecosystem did **not** require
`#123`/`#128` to close first. This is recorded here, without amending `PROJECT.md`, and is left
for the milestone-close `PROJECT.md` update per `67-CONTEXT.md` `<specifics>`.

## Handoff to Task 2

Task 1's sections are recorded above with no `## HALT` heading. Task 2 records the ordering proof,
the deferred-PR check, the folded-todo disposition, and the DEP-02/DEP-05 requirement closure
table.

## Ordering (constraint 4)

All comparisons are plain string comparisons of UTC `YYYY-MM-DDTHH:MM:SSZ` values (lexical order
equals chronological order for this fixed-width, zero-padded, single-timezone format).

```
DEP02_PROOF_AT = 2026-09-12T13:18:08Z   (67-PROOF-EVIDENCE.md)
DECIDED_AT_138 = 2026-09-12T13:36:41Z   (67-RUFF-EVIDENCE.md)
DECIDED_AT_128 = 2026-09-12T13:36:46Z   (67-DOCUTILS-EVIDENCE.md)
MERGED_AT_138  = 2026-09-12T13:37:03Z   (67-RUFF-EVIDENCE.md)
CLOSED_AT_123  = 2026-09-12T13:52:17Z   (67-RUFF-EVIDENCE.md)
```

- `DEP02_PROOF_AT` (`2026-09-12T13:18:08Z`) is earlier than `DECIDED_AT_138`
  (`2026-09-12T13:36:41Z`) and earlier than `DECIDED_AT_128` (`2026-09-12T13:36:46Z`): the proof
  preceded every merit decision (D-02).
- `MERGED_AT_138` (`2026-09-12T13:37:03Z`) is earlier than `CLOSED_AT_123`
  (`2026-09-12T13:52:17Z`): the merge preceded the close (D-03).

SC#2's branch is `can` (`SC2_BRANCH = can`, `67-PROOF-EVIDENCE.md` § "The 'can' branch, re-checked
live"): both stale PRs stayed open until the proof was recorded, and no close in this phase was
mechanical.

```
SC2_BRANCH = can
MECHANICAL_CLOSE = none
```

No comparison failed; no `## HALT: ordering violated` is written.

## Deferred PRs untouched

For each of #139, #140, #141 and #142, read live in this plan:

```
$ gh pr view 139 --json number,state,headRefName,headRefOid,updatedAt
{"headRefOid":"06f333fd5e1354f1f692f4191b3a26de172cd5d3","headRefName":"dependabot/uv/tox-4.61.4","number":139,"state":"OPEN","updatedAt":"2026-09-12T13:39:27Z"}

$ gh pr view 140 --json number,state,headRefName,headRefOid,updatedAt
{"headRefOid":"f28a35f4c1cd94ae016c3c34b2c116ce6e53225f","headRefName":"dependabot/uv/sphinx-intl-2.4.0","number":140,"state":"OPEN","updatedAt":"2026-09-12T13:39:26Z"}

$ gh pr view 141 --json number,state,headRefName,headRefOid,updatedAt
{"headRefOid":"e319f88b92cf4837dfe3034644e3a35076ed1c1e","headRefName":"dependabot/uv/pre-commit-4.6.2","number":141,"state":"OPEN","updatedAt":"2026-09-12T13:39:27Z"}

$ gh pr view 142 --json number,state,headRefName,headRefOid,updatedAt
{"headRefOid":"34a49560397889594a81f0ba59043494a5d54fa3","headRefName":"dependabot/uv/mypy-2.3.1","number":142,"state":"OPEN","updatedAt":"2026-09-12T13:39:22Z"}
```

All four `updatedAt` timestamps (`13:39:2*Z`) postdate `MERGED_AT_138` (`13:37:03Z`) — dependabot
rebased each of them onto the new `main` tip after the merge, which is a routine dependabot
rebase, not owner activity.

Owner-authored comment counts, each `0`:

```
$ gh pr view 139 --json comments -q '[.comments[] | select(.author.login == "YuSabo90002")] | length'
0
$ gh pr view 140 --json comments -q '[.comments[] | select(.author.login == "YuSabo90002")] | length'
0
$ gh pr view 141 --json comments -q '[.comments[] | select(.author.login == "YuSabo90002")] | length'
0
$ gh pr view 142 --json comments -q '[.comments[] | select(.author.login == "YuSabo90002")] | length'
0
```

Owner-authored timeline-event counts, each `0`:

```
$ gh api --paginate repos/YuSabo90002/typsphinx/issues/139/events --jq '.[] | select(.actor.login == "YuSabo90002") | .event' | wc -l
0
$ gh api --paginate repos/YuSabo90002/typsphinx/issues/140/events --jq '.[] | select(.actor.login == "YuSabo90002") | .event' | wc -l
0
$ gh api --paginate repos/YuSabo90002/typsphinx/issues/141/events --jq '.[] | select(.actor.login == "YuSabo90002") | .event' | wc -l
0
$ gh api --paginate repos/YuSabo90002/typsphinx/issues/142/events --jq '.[] | select(.actor.login == "YuSabo90002") | .event' | wc -l
0
```

Zero owner comments and zero owner timeline events on all four deferred PRs. Any change of state
on them (the dependabot rebases observed above, or a future supersession after #138's merge) is
recorded here, not acted on — per `67-CONTEXT.md` `<deferred>`.

Dependabot's own open-PR list at close, recorded verbatim, read-only:

```
$ gh pr list --state open --author app/dependabot --json number,title,headRefName,createdAt
[{"createdAt":"2026-09-12T10:40:18Z","headRefName":"dependabot/uv/mypy-2.3.1","number":142,"title":"chore(deps): bump mypy from 2.1.0 to 2.3.1"},{"createdAt":"2026-09-12T10:40:11Z","headRefName":"dependabot/uv/pre-commit-4.6.2","number":141,"title":"chore(deps): bump pre-commit from 4.6.0 to 4.6.2"},{"createdAt":"2026-09-12T10:40:04Z","headRefName":"dependabot/uv/sphinx-intl-2.4.0","number":140,"title":"chore(deps): bump sphinx-intl from 2.3.2 to 2.4.0"},{"createdAt":"2026-09-12T10:39:58Z","headRefName":"dependabot/uv/tox-4.61.4","number":139,"title":"chore(deps): bump tox from 4.56.1 to 4.61.4"}]
```

Only #139–#142 remain open under `app/dependabot`; #138 is merged, #123 and #128 are closed —
consistent with every disposition recorded across this phase.

## Folded todo

```
$ test -f .planning/todos/pending/2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md; echo "exit:$?"
exit:0

$ awk '/^---/{c++;next} c==1 && /^resolves_phase:/{print $2;exit} c==2{exit}' .planning/todos/pending/2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md
67
```

The todo is still in `pending/`, with `resolves_phase: 67`.

Its two asks, quoted from its own `## Solution` section:

> Whichever lands must be proven on a **real dependabot PR** — reopening/rerunning #123 or #128
> and observing the install step succeed — not on a hand-made branch that happens to carry a
> fresh `uv.lock`. The defect is specifically about what dependabot itself produces.
>
> Also decide what to do with the two PRs already open: they are ~3 weeks and ~2 weeks stale, and
> their bumps (`docutils <0.24`, `ruff <0.17`) may want re-evaluating on their merits rather than
> being merged just because CI finally goes green.

Mapped: "prove it on a real dependabot PR" → `67-01` (D-01/D-02, `DEP02_VERDICT = MET`). "decide
what to do with the two open PRs" → `67-02`/`67-03` (merge #138, close #128) and `67-04` (close
#123).

```
TODO_DISPOSITION = moved-at-phase-completion-by-execute-phase
```

`execute-phase.md`'s `close_phase_todos` step (line 1482, cited in this plan's Planning-time
census) moves every pending todo whose `resolves_phase` matches the completed phase to
`completed/` after `update_roadmap`. This plan neither moves nor edits the todo — its frontmatter
and body are unchanged, confirmed by the protected-path `git diff --quiet` in the verify step
below (`.planning/todos` is one of the checked paths).

## Requirement closure

| Requirement | Status | Deciding sections |
|-------------|--------|--------------------|
| DEP-02 | MET | `67-PROOF-EVIDENCE.md` § D-01 proof run, § Job census, § Check runs on PROOF_SHA, § Per-step reads, § DEP-02 verdict (`DEP02_VERDICT = MET`); this file's § "Wave gate and live re-assertion" (`A6701_STATUS = held`) |
| DEP-05 | MET | `67-RUFF-EVIDENCE.md` § SC#3 merits for #138, § Main after the merge, § #123 disposition (D-03); `67-DOCUTILS-EVIDENCE.md` § D-05 PyPI re-measurement, § Pre-close PyPI re-measurement, § #128 disposition (D-05); this file's § "Ordering (constraint 4)"; this file's § "SC#4 grouped-update coverage gap (D-06)" |

**DEP-02 is MET** because `DEP02_VERDICT = MET` (read from `67-PROOF-EVIDENCE.md`, re-asserted
live above) and `A6701_STATUS` is recorded (`held`).

**DEP-05 is MET** because: #138 merged on its merits and #123 closed as superseded (both re-read
live above, `#138` MERGED at `MERGE_SHA_138`, `#123` CLOSED with the owner-approved comment); #128
closed with its reason (`#128` CLOSED with the owner-approved comment, live-checked above); the
ordering holds (§ "Ordering (constraint 4)"); and the grouped-update gap is recorded (§ "SC#4
grouped-update coverage gap (D-06)").

**ROADMAP Phase 67 SC#1–SC#4 mapped:**

| SC | Section |
|----|---------|
| SC#1 | `67-PROOF-EVIDENCE.md` § "D-01 proof run" through § "Per-step reads" (DEP-02) |
| SC#2 | `67-PROOF-EVIDENCE.md` § "D-02 citations" through § "D-02 re-snapshot" (`SC2_BRANCH = can`, `MECHANICAL_CLOSE = none`); this file's § "Ordering (constraint 4)" |
| SC#3 | `67-RUFF-EVIDENCE.md` § "SC#3 merits for #138" |
| SC#4 (literal) | this file's § "SC#4 grouped-update coverage gap (D-06)", **Literal reading** — this milestone's proof does not cover the `sphinx-typst-stack` grouped path under `uv`; a future grouped resolution failure is an uncovered case, not a regression |
| SC#4 (amended) | this file's § "SC#4 grouped-update coverage gap (D-06)", **Amended reading** — SC#4's "neither #123 nor #128 is grouped" premise is falsified (`#128` is grouped); the conclusion is unchanged |

`.planning/REQUIREMENTS.md` is unedited by every Phase 67 plan; its DEP-02/DEP-05 checkboxes flip
at phase completion, as Phase 66's did.

No row above reads NOT MET.
