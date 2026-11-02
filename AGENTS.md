<!-- gsd-path:begin -->
# AGENTS.md — Operating Rules for the GSD Path Pipeline

These rules govern the router, inspectors, definition facilitators, researchers,
deciders, roadmappers, planners, orchestrators, coders, reviewers, and the discussion
sidecar. Role briefs are bundled with the installed skills. These rules win over role instructions except where the user says
otherwise.

## Authority order

1. The user, in chat.
2. `.project/CHARTER.md` (program flow): program scope, vetoes, and
   corrections bind every milestone. Vetoes may not be researched, planned,
   or built.
3. `.project/intent/INTENT.md`: constraints, vetoes, corrections, and success
   criteria are hard limits. Vetoes may not be researched, planned, or built.
   Only `$gsd-path-define` changes a success criterion, by appending
   `## Corrections`; a task Log or review cannot waive one.
4. `.project/SYNTHESIS.md` (program flow, top level) or
   `.project/research/SYNTHESIS.md` (single milestone): gated decisions are
   settled. Report conflicts; do not override them.
5. The current phase brief or task file.

If two sources disagree, stop and surface the conflict. Never average.

The orchestrator's isolated rerun of a task Verify is that task's evidence.
Wave and ship reviewers read that recorded output plus the isolated diff;
they do not re-run the task command. PLAN.md's project Verify runs once, at
ship, in one sidecar through `workflow_run.py prepare-final`. That runtime owns
execution, output recording, collection, and retry reuse. A complete quick-lane
single full wave with explicit final scope and walkthrough evidence may also
supply final review when the runtime proves unchanged product and contracts.
In that case FINAL.md is a generated view, not a new model assignment.
The project gap is always a view of its recorded command result.
Do not repeat a proven claim or write another narrative of the same evidence.
Verification effort follows uncovered contract claims and actual integration
risk; code line counts and token ratios are observations, never scope targets.
A task Verify must not copy the project command unless an
owned success criterion names it. Any other task Verify must name a path
from that task's `files`. INTENT constraints about not running the
full-repo suite on a tiny edit outrank the phase brief.

## Files are the only memory

- Start from disk, not conversation. If an input is absent from `.project/`,
  report it instead of inventing it.
- A discussion answer with `Status: final` or `NEEDS-USER`, `Follow-up:
  required`, and no later `Disposition X###` receipt is pending. Before phase
  work and again before a phase gate, the router and current phase run the
  active skill's bundled `scripts/discussion_records.py pending --repo
  <absolute-root>` helper; when `.project/discuss/` is absent it returns an
  empty list, so continue. Do not parse IDs, pair records, recover writes, or
  route pending receipts through model reasoning. The named owner either
  updates the target artifact through a legal current-phase gate and uses the
  helper's `dispose` command to append an `applied` disposition, or appends
  `acknowledged-no-change` with evidence. If applying it would rewrite an
  approved earlier-phase contract or the owner cannot legally enter, block the
  current phase with links to ANSWERS.md and the target artifact and ask the
  user; never auto-advance or archive it. Only the user may authorize
  `rejected-by-user`.
- After a phase completes its gate and state update, run the bundled
  `pipeline_state.py status --repo <absolute-root>` with the routed
  `--project-dir`. Its `handoff` is the shared phase handoff for chat and the
  dashboard. Present **Outcome** from `handoff.outcome` plus the completed
  work; **Review** links the phase artifact, or `handoff.review` when absent.
  An active router uses `handoff.router_next` for **Next** and follows the
  returned route. A directly invoked phase uses `handoff.phase_next` and
  stops. A status or plain-prompt reply uses `handoff.next` and stays read-only.
  Convert the `$` invocation prefix to the host's slash form when needed.
  Phase owners still stop for required input and approval before completion;
  a route is not approval. Return to an active caller instead of invoking an
  explicit-only sibling skill. Derive the next phase from this result, not
  from another lane table in prose.
- Phase skills bundle the remaining rules in `references/operating-rules.md`;
  read it before phase work.

## Plain-prompt re-entry

<!-- gsd-path/plain-prompt-reentry/v1 -->

- On a turn that did not explicitly invoke a GSD Path skill, check for
  `.project/STATE.md`. When it exists, first select the compatible interpreter:
  probe `python3 -B -c "import sys; raise SystemExit(sys.version_info < (3, 9))"`,
  then probe `python -B -c "import sys; raise SystemExit(sys.version_info < (3, 9))"`
  only if the first command fails. Run the first successful interpreter
  with `-B .gsd-path/status_runtime.py --repo <absolute-root>`
  before any requested repository mutation. Treat its JSON as the only route
  authority.
  When `completion.status` is `verified` and `git.branch` is an ordinary
  branch (not `gsd-path/M###`), requested product work may proceed normally.
  Archives and pipeline control files remain protected. Otherwise,
  a plain change request does not authorize work outside the pipeline: make no
  changes and report **Outcome**, link the returned `path` under **Review**, and
  under **Next** use `handoff.next`. An explicit request to leave
  or bypass the pipeline is a user ruling;
  route it through the router's undo or abandon flow instead of editing directly.
- After any other plain-prompt turn with owned state, rerun the same read-only
  status command immediately before the final response and append the same
  **Outcome** / **Review** / **Next** handoff with the same shared handoff rule.
  Keep an informational turn read-only from start to finish: do not use repository
  mutation tools or run commands that can create or alter files. A GSD Path skill
  already supplies this handoff, so emit it once. With no STATE.md, respond
  normally and do not initialize the pipeline. A missing runtime or invalid
  status blocks mutation and routes to `$gsd-path-forensics`.

## Evidence and honesty

- Claims need checked sources, decisions need citations, and verdicts need
  reproduced evidence. Never report a command as passing unless it ran.
- Report partial or failed results plainly. Silent partial success is the
  worst outcome.
- Preserve uncertainty as `NEEDS-USER`, `RESEARCH`, or a confidence level.
  Questions never silently disappear between phases.
- Record user corrections and vetoes verbatim.

## Gates

- Same-wave dependencies execute in dependency order; a task dispatches as
  soon as its dependencies land, never idling behind unrelated
  in-flight tasks. Only ready tasks run.
- Parallel dispatch rounds use distinct linked worktrees, each created at the
  clean primary HEAD recorded as its task base at dispatch. A serial dispatch
  round (one ready task) works and lands on the bound branch in the primary
  worktree. Task and reviewer Verify run against that recorded base plus only
  the task patch; evidence from a shared worktree or combined branch tip does
  not count.
- A wave advances only after every task and the wave review pass.
- Final review blocks on any `not-met`, `unverifiable`, or blocked gap verdict.
- STATE.md becomes `shipped` only when every final verdict and the project
  verify pass; the router reports shipped only after the integration
  validator (`validate-integrated`) passes.
- Shipping archives the milestone: artifacts move to
  `.project/archive/<NNN>-<slug>/` with a manifest, and the ship phase
  records the ship commit (STATE.md, final reviews, archive) as its single
  commit on the bound branch. Archives are read-only —
  no agent may modify or delete them — and a new milestone may not begin
  while an un-archived shipped milestone's artifacts sit in the active paths.
- STATE.archive is the crash-recovery transaction id. It is persisted before
  moves and never recomputed. Keep review active until the prepared archive,
  canonical contents, carry-forward, and manifest pass the bundled precommit
  validator; report shipped only after the exact `.project/`-only ship commit
  passes the postcommit validator and `validate-integrated` proves the
  integration landing, its tag, and its ancestry on origin/main —
  while integration is pending the router routes back to ship instead of
  reporting shipped or starting the next milestone.

## Asking the user

- Ask through an interactive user-input tool when the runtime provides one;
  otherwise ask concise numbered questions in chat and stop for the reply.
- Before any approval, ruling, `NEEDS-USER` question, blocked escalation, or
  phase-completion handoff, present three things in order: **Outcome** — what
  was produced or learned; **Review** — a Markdown link to the primary
  canonical artifact using its resolved absolute path; **Next** — the one
  question or action now required. Any text the user is expected to send back
  verbatim — a ruling, an approval command, a reply — goes in its own fenced
  code block, never a blockquote or inline prose, so it pastes cleanly. If the
  host cannot render local links, print
  the resolved absolute path immediately after the link. On an output failure,
  link the malformed artifact when it exists; otherwise link STATE.md or the
  canonical log that proves the failure and say the expected artifact is
  missing. Never ask for approval before its reviewable artifact exists on
  disk, and never ask a bare "approve?" without its outcome and link.
- Every choice offered to the user names a recommended option — listed first
  and marked `(recommended)` — with a one-line reason grounded in evidence,
  intent, or the codebase, followed by the real alternatives. A pure values
  call with no evidence either way carries no recommendation; say so
  explicitly instead of inventing one.
- After a user decision, confirm what changed, link the updated artifact again,
  and state whether the active router continues automatically or which exact
  explicit skill the user should invoke next.

## Escalation

Stop and ask the user only when:

- proceeding would violate a hard constraint or veto;
- the review loop reaches its cycle cap;
- a `NEEDS-USER` item reaches a phase checkpoint; or
- sources of truth conflict and INTENT.md does not make the resolution clear.

Handle everything else autonomously and record it in the task log or
STATE.md.

## Style

- Write fixed-format data for the next agent, without pleasantries.
- Write short, plain-English outcomes for the user.
- Keep agent final messages to paths, statuses, verdicts, and evidence.

## Distribution layout

This section describes the GSD Path source checkout. These source paths and
the sync command do not apply to an application that only installs GSD Path.
In a consuming project, resolve roles, templates, and helpers from the active
installed skill's absolute paths; the application need not contain this layout.

| Path | Purpose |
|------|---------|
| `plugin.json` | Agent Plugins manifest (`agent-plugins.org` 1.0.0 schema) |
| `skills/` | Skills and aliases declared in `scripts/skill-resources.json` |
| `skills/gsd-path/templates/` | Required artifact formats |
| `skills/gsd-path/references/` | Agent role and dispatch contracts |
| `WORKFLOW.md` | Phase-by-phase SOP |

Edit canonical resources only: `skills/gsd-path/` templates and references,
each per-skill `SKILL.md`, `scripts/`, and
`platforms/shared-agents/dispatch.md`. Every per-skill `references/`,
`templates/`, and `scripts/` copy is generated — run `python3
scripts/sync_skill_resources.py` after editing a canonical source. Sync
overwrites divergent generated copies and warns when a divergent copy is
newer than its canonical source (the wrong-direction-edit signature); treat
that warning as a lost edit and re-apply it to the canonical path.
<!-- gsd-path:end -->
