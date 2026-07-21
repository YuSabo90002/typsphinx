---
gsd_state_version: 1.0
milestone: v0.6.2
milestone_name: rendering fidelity round 2
current_phase: 22.1
current_phase_name: typstpdf Compile-Root Alignment for Nested Masters
status: executing
stopped_at: Phase 22.1 context gathered
last_updated: "2026-07-21T15:26:32.296Z"
last_activity: 2026-07-22
last_activity_desc: Phase 22.1 execution started
progress:
  total_phases: 6
  completed_phases: 4
  total_plans: 13
  completed_plans: 11
  percent: 67
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-21 after Phase 22)

**Core value:** The `typst`/`typstpdf` builders produce correct, compilable output for large real-world documentation sets — and output that *renders faithfully* to the source, not merely compiles fatal-free.
**Current focus:** Phase 22.1 — typstpdf Compile-Root Alignment for Nested Masters

## Current Position

Phase: 22.1 (typstpdf Compile-Root Alignment for Nested Masters) — EXECUTING
Plan: 1 of 2
Status: Executing Phase 22.1
Last activity: 2026-07-22 — Phase 22.1 execution started

Progress: [████████████████████] 11/11 plans (100%)

## Roadmap Summary (v0.6.2 — Phases 19–23)

| Phase | Goal | Requirements |
|-------|------|--------------|
| 19 — Block Separation Fixes (Cluster A) | Restore lost inter-block/inter-element separation (paragraphs-in-list-items, sibling signatures, rubric/option headings, definition terms, back-to-back confvals) — the dominant audit root cause, one coherent set of separator fixes | FID-02, FID-03, FID-04, FID-05, FID-06 |
| 20 — Signature Token Spacing (Cluster B) | Restore lost intra-signature token spacing: `class `/`exception ` prefix, C/C++ inter-token spaces, `:type:`/`:default:` colon-space | FID-07, FID-08, FID-09 |
| 21 — Residual Fidelity Fixes (Clusters C/D/E/F) | The remaining small-root-cause findings: inline-literal margin overflow, paragraph soft-newline reflow, codly config-wrapper leak, meaning-bearing inline styling | FID-10, FID-11, FID-12, FID-13, FID-14 |
| 22 — typstpdf Target-Name PDF Fix (Issue #117) | Independent `builder.py`/`pdf.py` fix: `TypstPDFBuilder.finish()` names the PDF after the `typst_documents` target, not the source docname | PDF-01 |
| 22.1 — typstpdf Compile-Root Alignment for Nested Masters (INSERTED) | `-b typstpdf` resolves `include()`/`image()` from the outdir root while the translator emits docname-relative paths; nested masters (`api/index`) are already broken. Align the two builders (temp file next to the master's `.typ`); no output moves | PDF-02 |
| 23 — v0.6.2 Release Prep + Regression-Gate Close | Prep-only: bump `pyproject.toml` → 0.6.2 + `CHANGELOG.md` `[0.6.2]` entry, close on the full-corpus regression gate; publish runs at `/gsd-complete-milestone` | (release/close — none) |

**Coverage:** 15/15 v1 requirements mapped (FID-02..FID-14 + PDF-01, PDF-02) — no orphans, no duplicates. Phase 23 carries no requirement (release/close phase).

**Standing bar (GATE-01):** every node-handler change (Phases 19, 20, 21) — and Phase 22 in its builder-test form — ships or extends a real `typst.compile()` regression fixture. String-agreement asserts alone never suffice. Local env runs real compiles (typst 0.15.0; corpus cached at `~/.cache/typsphinx-corpus-gate`).

**Milestone invariant (every phase):** zero new runtime deps, no `@preview` version bump — the 3-way version-sync surface (`writer.py`/`template_engine.py`/`templates/base.typ`) stays untouched. Flag during planning if a phase needs otherwise (none expected).

**Ship unit = milestone** (`branching_strategy: milestone`): Phase 23 is prep-only; the irreversible publish (tag `v0.6.2` → `release.yml` → PyPI) executes at `/gsd-complete-milestone`.

## Performance Metrics

**Velocity:**

- Total plans completed (project cumulative): 55 (15 v0.4.4, 13 v0.5.0, 15 v0.6.0, 9 v0.6.1, 3 additional v0.6.1 plans counted in-milestone; v0.6.2: 0 so far)
- v0.6.2 plans completed: 0 (roadmap just created)

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 20 P01 | 12min | 2 tasks | 4 files |
| Phase 20 P02 | 15min | 2 tasks | 5 files |

## Accumulated Context

### Decisions

Recent decisions affecting current work (full log in PROJECT.md Key Decisions):

- 2026-07-20: `branching_strategy: milestone` — ship unit is the milestone; the final phase is a prep-only Release phase, publish deferred to `/gsd-complete-milestone`. Push `main` to `origin` at every milestone close.
- v0.6.1: FID findings root-caused into clusters A–F in `17-AUDIT-CATALOGUE.md`; v0.6.2 delivers the 13 medium/low findings as one coherent translator-fix series.
- [Phase ?]: Phase 20 Plan 01: reused visit_Text dispatch (pass/pass) instead of a new space-emission helper for desc_sig_space, matching sibling desc_sig_* handlers
- [Phase ?]: Phase 20 Plan 02: reused depart_desc_parameter's am-I-last-sibling idiom for the field-list inter-field boundary; kept the colon-space edit inside the strong(...) content expression (single call site, no concat-context needed)
- 2026-07-21 [Phase 22]: `TypstBuilder._resolve_output_stem` is the single source of the `typst_documents` target-name rule, called from both builders' `write_doc` and from `TypstPDFBuilder.finish`; only a literal trailing `.typ` is stripped (never `os.path.splitext`, which would truncate `v1.2-manual` to `v1`).
- 2026-07-21 [Phase 22]: path-bearing / absolute / drive-qualified / `..` targets warn and reduce to `path.basename`; degenerate targets fall back to the docname — warn-and-degrade, never raise (`conf.py` is already executed code, so this is accident-defense + a UX signal).
- 2026-07-21 [Phase 22 UAT]: macOS/Linux filesystem Unicode normalization (HFS+/APFS NFD vs. byte-preserving NFC) accepted as an out-of-scope OS behavior; the typsphinx-controlled half (verbatim non-ASCII pass-through) is proven by `test_resolve_output_stem_preserves_non_ascii_target`. Adjacent to the standing XOS-01 item.

### Pending Todos

3 pending (`.planning/todos/pending/`):

- **死んだ設定 `typst_output_dir`** (builder) — **2026-07-21 決定: 即削除**（登録・ドキュメント・登録専用テスト・examples 一式を撤去、非推奨期間なし）。着手先は**バックログ 999.4 の scope 要素 1**。元は A/B/C 3件の todo で、**A は Phase 22.1 (PDF-02) に移管**、**B（マスター成果物の集約）は不採用として削除**。
- **`typst_package` (Typst Universe) パスが end-to-end で壊れている** (general) — **バックログ 999.4 の scope 要素 2**（旧 999.3 を merge）。BUG-A..BUG-D の証拠は ROADMAP §999.3 に残置。
- **ドキュメントのホスティング先を Read the Docs に変更** (docs) — 未検討

### Blockers/Concerns

None open. Phase 22 security review closed 9/9 threats (`22-SECURITY.md`, `threats_open: 0`); its 3 code-review findings are fixed (`22-REVIEW-FIX.md`). Phase 21's 3 advisory review warnings (WR-01/02/03 in `21-REVIEW.md`) remain non-blocking release-polish candidates. UI note: the v0.6.2 phases are Typst PDF typesetting / rendering-fidelity work, NOT frontend UI — no `### UI hint` annotations were added (the project's `ui.plan-gate` false-positives on PDF/rendering phases; use `--skip-ui` if it flags them).

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260720-p2w | Document worktree-isolated executor env provisioning (uv sync + uv run) in CLAUDE.md | 2026-07-20 | cc21f47 | [260720-p2w-add-a-worktree-isolated-execution-subsec](./quick/260720-p2w-add-a-worktree-isolated-execution-subsec/) |

### Roadmap Evolution

- 2026-07-20: v0.6.2 roadmap created — Phases 19–23, derived from 14 v1 requirements (FID-02..FID-14 + PDF-01). Phase numbering continues from v0.6.1 (ended at Phase 18). Shape: 3 root-cause-clustered translator-fix phases (A / B / C-D-E-F) + 1 independent builder-bug phase (Issue #117) + 1 prep-only Release/close phase.
- 2026-07-13: v0.6.1 roadmap created — Phases 16–18, derived from 6 named v1 requirements. Continued from v0.6.0.
- Phase 22.1 inserted after Phase 22: typstpdf compile-root alignment for nested masters (PDF-02) — split from the master-output-layout todo (item A only; B/C stay deferred) (URGENT)

## Deferred Items

Items acknowledged and carried forward from previous milestone closes:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Forward-ecosystem | CFG-01 (was FWD-03): user-configurable `@preview` versions | Deferred to v2 | v0.5.0 scoping |
| Cross-OS verification | XOS-01: cross-OS docs-PDF CI (macOS/Windows) | Deferred to v0.6.x+ | v0.5.0 scoping |
| Graceful-degrade | DEG-03: real rendering (not placeholder) for `graphviz` / `inheritance_diagram` | Deferred to v2 (image pipeline) | v0.6.1 scoping |
| Cross-reference | XREF-02: link `manpage` / xrefs to external URLs via a configured base URL | Deferred beyond v0.6.2 | v0.6.1 scoping |

## Session Continuity

Last session: 2026-07-21T14:43:33.269Z
Stopped at: Phase 22.1 context gathered
Resume file: .planning/phases/22.1-typstpdf-compile-root-alignment-for-nested-masters/22.1-CONTEXT.md

## Operator Next Steps

- Plan the first phase with `/gsd-plan-phase 19`
