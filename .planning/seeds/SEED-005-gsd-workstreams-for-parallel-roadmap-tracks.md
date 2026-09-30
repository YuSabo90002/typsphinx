---
id: SEED-005
status: dormant
planted: 2026-09-02
planted_during: v0.9.3 (Toolchain and dependency-update repair) — new-milestone roadmap approval
trigger_when: when a milestone's roadmap splits into two or more logically independent tracks AND the tracks are long enough that serializing them costs real calendar time
scope: medium
audit_acknowledged:
  milestone: v0.9.3
  at: 2026-09-13
  status: dormant
---

# SEED-005: Adopt GSD workstreams (`--ws`) so logically independent roadmap tracks can actually be worked in parallel

**Captured 2026-09-02**, immediately after the v0.9.3 roadmap was approved and the operator had to
retract a "you can start Phase 66 in parallel" recommendation as overstated. Planted **enriched** —
trigger, rationale and scope are filled in from measurements taken during that same session, rather
than left as a stub for a later `--enrich` pass. Two of the four seeds already in this directory
(SEED-001, SEED-004) have sat dormant with `_To be filled in_` bodies and would not support a
decision if they surfaced today; this one is meant to.

## Why This Matters

**The problem is structural, not a missing feature.** `.planning/STATE.md` has a **single**
`## Current Position` section and a **single** `current_phase` frontmatter field. Two phases cannot
both be "where the project is". Everything downstream — `state.advance-plan`, progress counters,
`state.json`'s `next` — reads that one slot.

gsd-core's own `milestone-lock.cjs` (issue **#3311**) says so in its module comment, and is worth
quoting because it is the authoritative statement of the limit:

> Problem it solves: two sessions running DIFFERENT phases in the same working tree both
> read-modify-write `## Current Position`. The byte-level STATE.md lock (#464) already serializes
> those writes, so no write is lost — but the SEMANTIC clobber is silent: `state.advance-plan` takes
> no phase argument and advances whatever plan the (possibly just clobbered) Current Position names,
> and nothing ever surfaces that two sessions claimed two different phases against the one
> single-slot field.

Its fix is an **advisory claim file keyed by (phase, session)** that **warns the second session
instead of blocking it** — the comment states plainly: *"It is an advisory claim file, not a mutex."*
So same-tree parallel phases are **detected**, not **supported**. Reading `milestone.lock`'s
existence as permission to run two phases at once is the exact misreading this seed exists to
prevent.

**Workstreams are the actual mechanism.** `gsd-core/references/workstream-flag.md` opens with:
"The `--ws <name>` flag scopes GSD operations to a specific workstream, enabling parallel milestone
work by multiple Claude Code instances on the same codebase." Each workstream gets its **own**
`.planning/workstreams/<name>/STATE.md`, `ROADMAP.md`, `REQUIREMENTS.md` and `phases/` — so the
single-slot problem disappears by giving each track its own slot. Session-scoped pointers (keyed on
`GSD_SESSION_KEY`, `CLAUDE_CODE_SESSION_ID`, `CODEX_THREAD_ID`, the controlling TTY, …) keep
concurrent sessions from repointing each other, which the shared `.planning/active-workstream` file
alone cannot do.

**Do not confuse this with the parallelism this project already uses.** Three distinct layers:

| Layer | What it parallelizes | State in this repo |
|---|---|---|
| Wave parallelism (`parallelization: true`, `workflow.use_worktrees: true`) | Plans **within one phase**, in isolated git worktrees | **In constant use.** CLAUDE.md calls worktree isolation the standing execution mode |
| `milestone.lock` (#3311) | Nothing — it *detects* two sessions claiming different phases in one tree and warns | Present, never yet fired here |
| Workstreams (`--ws`) | Whole tracks / milestones, each with its own STATE/ROADMAP/REQUIREMENTS/phases | **Never used.** This repo is flat mode |

## When to Surface

**Trigger:** when a milestone's roadmap splits into two or more logically independent tracks AND the
tracks are long enough that serializing them costs real calendar time.

The first half of that condition has now been met once, so it is not hypothetical — but it is also
not sufficient on its own, which is why the second half is in the trigger.

**Do not surface** for: a milestone with one linear track; a milestone where the "independent" tracks
are two phases each (v0.9.3's shape — see below); or work that only needs *wave* parallelism inside a
phase, which already works and needs nothing from this seed.

## Scope Estimate

**Medium.** No code changes to this repository — it is a `.planning/` layout and workflow-habit
change. The cost is in the migration and in the ongoing split:

- Creating the workstream (`workstream.create`) and moving each track's `ROADMAP.md`,
  `REQUIREMENTS.md` and `phases/` under `.planning/workstreams/<name>/`.
- Running two terminals with distinct session identities, and remembering `--ws` (or a session
  pointer) on every command — the routing-propagation contract requires `--ws` to chain to every
  downstream command, and a silently dropped flag routes writes to the wrong STATE.md.
- Reconciling at merge time: two `phases/` trees, two progress counters, one git history.

## Why it was declined at v0.9.3 (the concrete precedent)

v0.9.3's roadmap **is** two independent tracks — `{64 FHS + shims} → {65 tox-uv revert}` and
`{66 dependabot ecosystem} → {67 prove + dispose}` — with no shared file and no shared mechanism (the
CI-side track never touches NixOS). The roadmapper explicitly declared them parallelizable, and that
judgement stands as a statement about *logical* dependency.

It was still declined, for reasons that should be re-checked rather than inherited:

1. **Two phases per track.** The setup and reconciliation cost is not obviously smaller than the
   serialization it saves.
2. **A measured side effect on a shared file.** `new-milestone`'s Step 4 splits into Part A
   (`## Current Milestone` write) and Part B (`## Evolution` backfill). When a workstream is active,
   **Part A is skipped** — PROJECT.md is marked `# Shared` in the workstream directory diagram, and
   writing that heading from a workstream would clobber it, with whichever workstream ran
   `new-milestone` last silently winning (gsd-core **#2308**). Measured at v0.9.3 scoping: the
   `init.new-milestone` call returned
   `section_manifest.included: ['project-md-milestone-write']` **because flat mode was active**;
   under a workstream that entry moves to `excluded`. So PROJECT.md's Current Milestone section — the
   document this project leans on hardest for carrying binding measurements forward — would have to
   be written by hand or by a separate flat-mode pass.
3. **No prior art in this repo.** Zero workstreams have ever been created here, so the first adoption
   pays the whole learning cost inside a milestone that also has real work to do.

## Breadcrumbs

- `.claude/gsd-core/references/workstream-flag.md` — resolution priority, session-identity
  resolution, pointer lifecycle, the shared-vs-scoped directory diagram, and the `workstream.*` CLI
  surface (`create` / `list` / `status` / `complete`).
- `.claude/gsd-core/bin/lib/milestone-lock.cjs` — the #3311 module comment quoted above; the
  authoritative statement that same-tree parallel phases are advisory-warned, not supported.
- `.claude/gsd-core/workflows/new-milestone.md` Step 4 — the Part A / Part B split and the #2308
  rationale for skipping the `## Current Milestone` write under a workstream.
- `.claude/gsd-core/bin/lib/state.cjs` — `current_phase` resolution
  (frontmatter → legacy → Current Position prose); the single-slot field itself.
- `.planning/ROADMAP.md` (v0.9.3) — the two-track structure that first met half of this seed's
  trigger, with the tracks' independence stated in the phase `Depends on` fields.
- `.planning/config.json` — `parallelization: true`, `workflow.use_worktrees: true`; the *other*
  parallelism, already in use, not what this seed is about.
- The `gsd-workstreams` skill — "Manage parallel workstreams — list, create, switch, status,
  progress, complete, and resume."

## Notes

Captured enriched in one shot rather than as a stub, deliberately: the value of this seed is entirely
in the measurements above, and they were cheap to take today and expensive to reconstruct later.

If this surfaces and is again declined, **record why in the milestone's own artifacts rather than
editing this file's rationale** — the point of the trigger is to force a fresh judgement each time,
not to accumulate a case for or against.
