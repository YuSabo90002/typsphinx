---
gsd_state_version: 1.0
milestone: v0.6.2
milestone_name: rendering fidelity round 2
current_phase: 20
current_phase_name: Cluster B
status: planning
stopped_at: Phase 20 context gathered
last_updated: "2026-07-20T10:33:35.262Z"
last_activity: 2026-07-20
last_activity_desc: Phase 19 complete, transitioned to Phase 20
progress:
  total_phases: 5
  completed_phases: 1
  total_plans: 3
  completed_plans: 3
  percent: 20
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-20 at v0.6.2 milestone start)

**Core value:** The `typst`/`typstpdf` builders produce correct, compilable output for large real-world documentation sets — and output that *renders faithfully* to the source, not merely compiles fatal-free.
**Current focus:** Phase 19 — Block Separation Fixes (Cluster A)

## Current Position

Phase: 20 — Signature Token Spacing (Cluster B)
Plan: Not started
Status: Ready to plan
Last activity: 2026-07-20 — Phase 19 complete, transitioned to Phase 20

Progress: [░░░░░░░░░░] 0%

## Roadmap Summary (v0.6.2 — Phases 19–23)

| Phase | Goal | Requirements |
|-------|------|--------------|
| 19 — Block Separation Fixes (Cluster A) | Restore lost inter-block/inter-element separation (paragraphs-in-list-items, sibling signatures, rubric/option headings, definition terms, back-to-back confvals) — the dominant audit root cause, one coherent set of separator fixes | FID-02, FID-03, FID-04, FID-05, FID-06 |
| 20 — Signature Token Spacing (Cluster B) | Restore lost intra-signature token spacing: `class `/`exception ` prefix, C/C++ inter-token spaces, `:type:`/`:default:` colon-space | FID-07, FID-08, FID-09 |
| 21 — Residual Fidelity Fixes (Clusters C/D/E/F) | The remaining small-root-cause findings: inline-literal margin overflow, paragraph soft-newline reflow, codly config-wrapper leak, meaning-bearing inline styling | FID-10, FID-11, FID-12, FID-13, FID-14 |
| 22 — typstpdf Target-Name PDF Fix (Issue #117) | Independent `builder.py`/`pdf.py` fix: `TypstPDFBuilder.finish()` names the PDF after the `typst_documents` target, not the source docname | PDF-01 |
| 23 — v0.6.2 Release Prep + Regression-Gate Close | Prep-only: bump `pyproject.toml` → 0.6.2 + `CHANGELOG.md` `[0.6.2]` entry, close on the full-corpus regression gate; publish runs at `/gsd-complete-milestone` | (release/close — none) |

**Coverage:** 14/14 v1 requirements mapped (FID-02..FID-14 + PDF-01) — no orphans, no duplicates. Phase 23 carries no requirement (release/close phase).

**Standing bar (GATE-01):** every node-handler change (Phases 19, 20, 21) — and Phase 22 in its builder-test form — ships or extends a real `typst.compile()` regression fixture. String-agreement asserts alone never suffice. Local env runs real compiles (typst 0.15.0; corpus cached at `~/.cache/typsphinx-corpus-gate`).

**Milestone invariant (every phase):** zero new runtime deps, no `@preview` version bump — the 3-way version-sync surface (`writer.py`/`template_engine.py`/`templates/base.typ`) stays untouched. Flag during planning if a phase needs otherwise (none expected).

**Ship unit = milestone** (`branching_strategy: milestone`): Phase 23 is prep-only; the irreversible publish (tag `v0.6.2` → `release.yml` → PyPI) executes at `/gsd-complete-milestone`.

## Performance Metrics

**Velocity:**

- Total plans completed (project cumulative): 55 (15 v0.4.4, 13 v0.5.0, 15 v0.6.0, 9 v0.6.1, 3 additional v0.6.1 plans counted in-milestone; v0.6.2: 0 so far)
- v0.6.2 plans completed: 0 (roadmap just created)

*Updated after each plan completion*

## Accumulated Context

### Decisions

Recent decisions affecting current work (full log in PROJECT.md Key Decisions):

- 2026-07-20: `branching_strategy: milestone` — ship unit is the milestone; the final phase is a prep-only Release phase, publish deferred to `/gsd-complete-milestone`. Push `main` to `origin` at every milestone close.
- v0.6.1: FID findings root-caused into clusters A–F in `17-AUDIT-CATALOGUE.md`; v0.6.2 delivers the 13 medium/low findings as one coherent translator-fix series.

### Pending Todos

None.

### Blockers/Concerns

None open. UI note: the v0.6.2 phases are Typst PDF typesetting / rendering-fidelity work, NOT frontend UI — no `### UI hint` annotations were added (the project's `ui.plan-gate` false-positives on PDF/rendering phases; use `--skip-ui` if it flags them).

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260720-p2w | Document worktree-isolated executor env provisioning (uv sync + uv run) in CLAUDE.md | 2026-07-20 | cc21f47 | [260720-p2w-add-a-worktree-isolated-execution-subsec](./quick/260720-p2w-add-a-worktree-isolated-execution-subsec/) |

### Roadmap Evolution

- 2026-07-20: v0.6.2 roadmap created — Phases 19–23, derived from 14 v1 requirements (FID-02..FID-14 + PDF-01). Phase numbering continues from v0.6.1 (ended at Phase 18). Shape: 3 root-cause-clustered translator-fix phases (A / B / C-D-E-F) + 1 independent builder-bug phase (Issue #117) + 1 prep-only Release/close phase.
- 2026-07-13: v0.6.1 roadmap created — Phases 16–18, derived from 6 named v1 requirements. Continued from v0.6.0.

## Deferred Items

Items acknowledged and carried forward from previous milestone closes:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Forward-ecosystem | CFG-01 (was FWD-03): user-configurable `@preview` versions | Deferred to v2 | v0.5.0 scoping |
| Cross-OS verification | XOS-01: cross-OS docs-PDF CI (macOS/Windows) | Deferred to v0.6.x+ | v0.5.0 scoping |
| Graceful-degrade | DEG-03: real rendering (not placeholder) for `graphviz` / `inheritance_diagram` | Deferred to v2 (image pipeline) | v0.6.1 scoping |
| Cross-reference | XREF-02: link `manpage` / xrefs to external URLs via a configured base URL | Deferred beyond v0.6.2 | v0.6.1 scoping |

## Session Continuity

Last session: 2026-07-20T10:33:35.257Z
Stopped at: Phase 20 context gathered
Resume file: .planning/phases/20-signature-token-spacing-cluster-b/20-CONTEXT.md

## Operator Next Steps

- Plan the first phase with `/gsd-plan-phase 19`
