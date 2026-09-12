# Phase 67: Proof on a Real Dependabot PR, Then Disposal of #123 and #128 - Pattern Map

**Mapped:** 2026-09-12
**Files analyzed:** 4 (all evidence markdown under the phase directory; no product code, no workflow, no `.github/dependabot.yml`)
**Analogs found:** 4 / 4

## Scope Note

This phase creates **no source files**. Per CONTEXT.md and RESEARCH.md, every task is either a
read-only `gh`/`git`/`curl` query or a markdown write under `.planning/phases/67-.../`. The
`AMENDED` blocks in `ROADMAP.md`/`PROJECT.md` (D-06) are already committed and are read-only
citations here, not edits. Consequently there is no controller/service/component role
classification in the conventional sense — every "file to create" is an **evidence-file** role
with a **read-and-transcribe** data flow, or (for the three gated actions) a **one-way external
write** data flow recorded inline in the same evidence file. The closest analogs are Phase 66's own
evidence files and plans, which this phase reuses verbatim in structure.

## File Classification

| New File (to be created this phase) | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `67-01-PLAN.md` (Wave 1: D-01 transcription + D-02 citation/re-snapshot) | plan / evidence-producing task spec | read-only request-response (gh/git queries → markdown) | `.planning/phases/66-.../66-01-PLAN.md` | exact |
| `67-0N-EVIDENCE.md` (e.g. `67-PROOF-EVIDENCE.md` or similarly named — naming is Claude's Discretion) | evidence file, `KEY = value` layout | read-only transcription + one-way gated write (merge/close), recorded inline | `66-MAIN-PR-EVIDENCE.md` + `66-DEPENDABOT-EVIDENCE.md` | exact |
| `67-02-PLAN.md` (Wave 2: D-03/D-04 merge #138 + close #123) | plan / gated one-way action spec | request-response with owner `checkpoint:decision` gate, then one-way external write (`gh pr merge`, `gh pr close`) | `66-02-PLAN.md` (owner-gated merge) + `66-04-PLAN.md`'s D-02 snapshot pattern | exact |
| `67-03-PLAN.md` (Wave 3: D-05 close #128, with PyPI HALT re-check) | plan / gated one-way action spec with a HALT branch | request-response with a HALT-and-return-to-owner branch, then one-way external write (`gh pr close`) | `66-DEPENDABOT-EVIDENCE.md` § "uv update job conclusion (HALT resolved by owner ruling, AMENDED 2026-09-12)" (the project's only prior first-class HALT-and-resume instance) | exact |
| `67-04-PLAN.md` (Wave 4, or folded into 67-03: D-06 write-up, `REQUIREMENTS.md` checkbox closure, todo closure) | plan / requirement-closure evidence | read-only citation of already-committed `AMENDED` blocks + markdown checkbox edit | `66-04-PLAN.md` § "D-06", § "Owner Dependabot-tab read (D-04)" | role-match |

No component/controller/service/model/middleware files exist in this phase's scope — confirmed
against both CONTEXT.md (`## Specific Ideas`, `## Deferred Ideas`) and RESEARCH.md's
"Architectural Responsibility Map" table, which states explicitly: "There is no 'backend
implementation' task and no 'test-writing' task in the conventional sense."

## Pattern Assignments

### `67-0N-EVIDENCE.md` (evidence file, read-and-transcribe + gated one-way write)

**Analog:** `.planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/66-MAIN-PR-EVIDENCE.md` and
`66-DEPENDABOT-EVIDENCE.md`

**Header / provisioning pattern** (66-MAIN-PR-EVIDENCE.md:1-52):
```
executor worktree, provisioned with the CLAUDE.md line; git and gh only; the main checkout is never touched.

BASE_SHA = 6181768f64b4cee62a77ac4e26c60c3c976cbb6e
...

## Head check and provisioning

$ test -f .git; echo "exit:$?"
exit:0

$ pwd -P
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-...

$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
...

$ gh auth status
github.com
  ✓ Logged in to github.com account YuSabo90002 ...
```
Every 67-0N evidence file should open with this exact worktree-detection + provisioning +
`gh auth status` transcription before any `gh`/`git` query, per CLAUDE.md's "Worktree-isolated
execution" section.

**`KEY = value` evidence-line pattern** (66-DEPENDABOT-EVIDENCE.md:109, 149, 219, 452, 667-668,
etc.):
```
UV_RUN_ID = 34688990228
D03_POLL1 = uv-run-seen
UV_RUN_ACCEPTED = yes
UV_PR_CANDIDATES = 138 139 140 141 142
SC1_PR = 138
SC1_SHA = 88088071e02a7411800f504e06b1ded9d6891cc7
```
Every measured fact this phase records (`SC1_RUN_ID`, `SC1_SHA`, PR states, PyPI cap readings, the
owner's decision, the merge/close outcomes) must be written as a bare `KEY = value` line so a later
task or the verifier can `sed -n 's/^KEY = //p'` it and re-assert it live. Copy this idiom exactly
— do not embed the value only in prose.

**Re-assert-immediately-before-acting pattern** (66-MAIN-PR-EVIDENCE.md:506-538, "Gate re-asserted
after the decision"):
```
### Gate re-asserted after the decision

$ git fetch origin main
...
$ gh pr view 137 --json state,headRefOid
{"headRefOid":"...","state":"OPEN"}
$ gh pr view 137 --json statusCheckRollup --jq '.statusCheckRollup[] | [.name, .conclusion] | @tsv'
...
No difference from the pre-merge gate: ... The merge proceeds.
```
Copy this shape for #138: re-fetch `origin/main`, re-read `headRefOid`/`mergeStateStatus`/
`statusCheckRollup` immediately before `gh pr merge`, and state explicitly "no difference from
[the earlier snapshot]" or, if different, HALT (Pitfall 3's `--match-head-commit` guard, below).

**D-02 pre/post-merge PR snapshot pattern** (66-MAIN-PR-EVIDENCE.md:540-563;
66-DEPENDABOT-EVIDENCE.md:348-397, "D-02 post-merge snapshot"):
```
$ date -u +%FT%TZ
2026-09-12T10:38:17Z
$ gh pr view 123 --json number,state,closed,closedAt,comments,headRefName,headRefOid,updatedAt,labels
{"closed":false,"closedAt":null,"comments":[...],"headRefOid":"...","state":"OPEN", ...}
```
followed by an explicit diff-to-prior-snapshot statement ("unchanged from 66-01's planning-time
census — same `headRefOid`, same `updatedAt`") and, when checking for owner action, the
timeline-events emptiness check:
```
$ gh api repos/YuSabo90002/typsphinx/issues/123/events --jq '[.[] | select(.actor.login == "YuSabo90002" and .created_at > "<DECIDED_AT>")] | length'
0
```
Reuse this exact snapshot shape for D-02's Phase-67 re-snapshot of #123/#128 (read-only, before
touching either), and again as the pre-close snapshot immediately before each `gh pr close`.

**Merge invocation pattern** (66-DEPENDABOT-EVIDENCE.md:565-591 — note: this is the *MAIN-PR-EVIDENCE*
merge; also visible at 66-MAIN-PR-EVIDENCE.md-equivalent block above):
```
$ gh pr merge 137 --merge --match-head-commit 7cc85d28c6946434aa4fb14a0b9b5555d29275ef
(no stdout)

$ gh pr view 137 --json state,mergeCommit,mergedAt
{"mergeCommit":{"oid":"293f0c2684641f5d4b2f5ed021b565656e38d48c"},"mergedAt":"...","state":"MERGED"}
```
Use the identical invocation shape for #138: `gh pr merge 138 --merge --match-head-commit <fresh
head SHA>` — exactly those flags, no `--admin`/`--auto`/`--squash`/`--rebase`/`--delete-branch`
(RESEARCH.md Pitfall 3 and "Matching #126/#127's merge method" both confirm `--merge` is this
repo's convention, matching #126/#127/#137).

**Owner `checkpoint:decision` transcription pattern** (66-DEPENDABOT-EVIDENCE.md:494-505, "Owner
decision"):
```
## Owner decision

OWNER_DECISION = merge
DECIDED_AT = 2026-09-12T10:38:08Z

The owner replied, literally, "merge" to the Task 2 checkpoint (relayed by the coordinator), which
presented `PR_URL`, the six required checks (all `SUCCESS`), ...
```
Every one of the three gated actions in Phase 67 (merge #138, close #123, close #128) needs its own
such block: a `KEY = value` for the decision + timestamp, then a literal transcription of what was
presented to the owner and what the owner replied — never paraphrased.

### HALT-and-return-to-owner branch (D-05's Sphinx/docutils cap re-check)

**Analog:** `66-DEPENDABOT-EVIDENCE.md` § "uv update job conclusion (HALT resolved by owner ruling,
AMENDED 2026-09-12)" (lines 155-286) — this project's only precedent for a first-class HALT branch
that was later resolved and folded back into the evidence file with an `AMENDED` note rather than
silently rewritten.

**Pattern to copy** (structure, not content):
```
## uv update job conclusion (HALT resolved by owner ruling, AMENDED 2026-09-12)

This heading was originally `## HALT: uv update job failed`. The owner resolved that halt with
this ruling, relayed by the coordinator:

> Owner ruling on your HALT checkpoint: option A (proceed). ...

The body below is unchanged from the original halted text.

`UV_RUN_ID`'s conclusion is `failure`, not `success`. Per the plan's Task 1 step 5, this halts the
task at a blocking-human checkpoint rather than proceeding to Task 2's normal flow.
```
For D-05: write the heading as `## HALT: Sphinx has relaxed the docutils cap` **only if** the live
PyPI re-check (`curl https://pypi.org/pypi/sphinx/json`) shows `docutils>=0.23` is no longer
excluded; otherwise record the negative result plainly (as RESEARCH.md's own "Code Examples" section
already did) and proceed to the close action without ever writing a `## HALT` heading. The verifier
convention elsewhere in this phase (`grep -c '^## HALT' <file>` expecting `0`) depends on this
heading text being exact and appearing only when a real halt occurred.

### PyPI JSON re-check pattern (D-05 merit input)

**Analog:** `66-RESEARCH.md`/`67-RESEARCH.md` "Code Examples" § "D-05's HALT-condition re-check"
(this RESEARCH.md, lines 427-442):
```
curl -s https://pypi.org/pypi/sphinx/json | python3 -c \
  "import json,sys; d=json.load(sys.stdin); print(d['info']['version']); \
   [print(r) for r in d['info']['requires_dist'] if 'docutils' in r.lower()]"
# 9.1.0
# docutils<0.23,>=0.21
curl -s https://pypi.org/pypi/docutils/json | python3 -c \
  "import json,sys; print(json.load(sys.stdin)['info']['version'])"
# 0.23
```
Copy this exact query shape into the 67-03 evidence file, re-run fresh at execution time (not
copied from RESEARCH.md), immediately before drafting/posting the #128 close comment.

### Comment-and-close pattern (D-03/D-05 outward actions)

**Analog:** No prior `gh pr close --comment` invocation exists in Phase 66's evidence (RESEARCH.md
Open Question 2 flags this explicitly — Phase 66 only ever *merged*, never *closed*, a dependabot
PR). Closest analog is the merge-invocation transcription shape above, adapted:
```
$ gh pr close --help   # pre-flight capability check, read-only
$ gh pr close 123 --comment "Superseded by #138."
# or, if --comment is unsupported by the installed gh version:
$ gh pr comment 123 --body "Superseded by #138."
$ gh pr close 123
```
Present the draft text verbatim at the `checkpoint:decision` and let the owner edit/approve live
(RESEARCH.md Open Question 1) — do not hardcode a "final" string into the plan file itself.

## Shared Patterns

### Worktree provisioning (applies to every plan/task in this phase)
**Source:** CLAUDE.md § "Worktree-isolated execution"; transcribed at
`66-MAIN-PR-EVIDENCE.md:1-52` and `66-DEPENDABOT-EVIDENCE.md:1-30`
```
$ test -f .git; echo "exit:$?"
exit:0
$ env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
$ gh auth status
```
Apply to every 67-0N plan's first task, verbatim.

### `KEY = value` evidence-line convention (applies to every evidence file this phase writes)
**Source:** `66-DEPENDABOT-EVIDENCE.md` throughout (e.g. lines 109, 149, 452, 667-668, 909-911)
```
UV_RUN_ACCEPTED = yes
SC1_PR = 138
SC1_SHA = 88088071e02a7411800f504e06b1ded9d6891cc7
D05_LEG2 = PASS
```
Every measured fact (PR states, SHAs, PyPI readings, owner decisions, merge/close outcomes) is a
bare `KEY = value` line, re-assertable by `sed -n 's/^KEY = //p'`. Apply to all of D-01 through D-06's
recorded facts.

### `## HALT` heading convention, later resolved via `AMENDED` note (applies to D-05's conditional branch)
**Source:** `66-DEPENDABOT-EVIDENCE.md:155-167` ("This heading was originally `## HALT: ...`")
```
## HALT: <condition>
...
```
If it fires, the heading is later replaced in place with `## <resolved description> (HALT resolved
by owner ruling, AMENDED <date>)`, quoting the owner's literal ruling — never silently deleted or
rewritten without the "This heading was originally..." preface.

### Gate re-check before every `<automated>`/verifier assertion (applies to Wave gates)
**Source:** `66-DEPENDABOT-EVIDENCE.md:31-58` ("Wave-2 gate"), `:501-528` ("Wave-3 gate")
```
$ sed -n 's/^UV_PR_CANDIDATES = //p' .planning/phases/66-.../66-DEPENDABOT-EVIDENCE.md
138 139 140 141 142
$ grep -c '^## HALT' .planning/phases/66-.../66-MAIN-PR-EVIDENCE.md
0
```
Every 67-0N wave begins by re-reading the prior wave's evidence keys with `sed`/`grep`, not by
trusting the planner's own recollection of them.

## No Analog Found

None. All four files-to-be-produced classifications found an exact or role-match analog within
Phase 66's own evidence files and plans — no fallback to RESEARCH.md's general patterns was needed.

## Metadata

**Analog search scope:** `.planning/phases/66-github-dependabot-yml-pip-uv-ecosystem/` (all
tracked files); confirmed via `git ls-files` that every path cited above is git-tracked source, not
a gitignored mirror.
**Files scanned:** `66-MAIN-PR-EVIDENCE.md`, `66-DEPENDABOT-EVIDENCE.md`, `66-01-PLAN.md` (header
only), `66-02-PLAN.md`/`66-04-PLAN.md` (referenced by section, not separately read — their content
is already reflected inline in the two EVIDENCE files' own headers/gates).
**Pattern extraction date:** 2026-09-12
