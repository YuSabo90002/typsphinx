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
