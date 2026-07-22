---
gsd_state_version: 1.0
milestone: v0.6.2
milestone_name: rendering fidelity round 2
current_phase: 23
current_phase_name: v0.6.2 Release Prep + Regression-Gate Close
status: executing
stopped_at: Phase 23 planned — ready to execute
last_updated: "2026-07-22T22:22:18.396Z"
last_activity: 2026-07-23
last_activity_desc: Phase 23 execution started
progress:
  total_phases: 9
  completed_phases: 8
  total_plans: 30
  completed_plans: 28
  percent: 89
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-21 after Phase 22)

**Core value:** The `typst`/`typstpdf` builders produce correct, compilable output for large real-world documentation sets — and output that *renders faithfully* to the source, not merely compiles fatal-free.
**Current focus:** Phase 23 — v0.6.2 Release Prep + Regression-Gate Close

## Current Position

Phase: 23 (v0.6.2 Release Prep + Regression-Gate Close) — EXECUTING
Plan: 1 of 3
Status: Executing Phase 23
Last activity: 2026-07-23 — Phase 23 execution started

Progress: [░░░░░░░░░░░░░░░░░░░░] 0/3 plans (planned, not started)

## Roadmap Summary (v0.6.2 — Phases 19–23)

| Phase | Goal | Requirements |
|-------|------|--------------|
| 19 — Block Separation Fixes (Cluster A) | Restore lost inter-block/inter-element separation (paragraphs-in-list-items, sibling signatures, rubric/option headings, definition terms, back-to-back confvals) — the dominant audit root cause, one coherent set of separator fixes | FID-02, FID-03, FID-04, FID-05, FID-06 |
| 20 — Signature Token Spacing (Cluster B) | Restore lost intra-signature token spacing: `class `/`exception ` prefix, C/C++ inter-token spaces, `:type:`/`:default:` colon-space | FID-07, FID-08, FID-09 |
| 21 — Residual Fidelity Fixes (Clusters C/D/E/F) | The remaining small-root-cause findings: inline-literal margin overflow, paragraph soft-newline reflow, codly config-wrapper leak, meaning-bearing inline styling | FID-10, FID-11, FID-12, FID-13, FID-14 |
| 22 — typstpdf Target-Name PDF Fix (Issue #117) | Independent `builder.py`/`pdf.py` fix: `TypstPDFBuilder.finish()` names the PDF after the `typst_documents` target, not the source docname | PDF-01 |
| 22.1 — typstpdf Compile-Root Alignment for Nested Masters (INSERTED) | `-b typstpdf` resolves `include()`/`image()` from the outdir root while the translator emits docname-relative paths; nested masters (`api/index`) are already broken. Align the two builders (temp file next to the master's `.typ`); no output moves | PDF-02 |
| 22.2 — Dead Config-Value Sweep (INSERTED) | Delete the dead `typst_output_dir`, repair the `typst_package` (Typst Universe) path end-to-end (BUG-A..BUG-D), and land a config→output regression fixture so registration-only asserts can no longer hide a dead feature | CONF-01, CONF-02, CONF-03 |
| 22.3 — typstpdf Builder Warning Hardening (INSERTED) | Close the two Phase 22.1 review warnings: `finish()` no longer "succeeds" while silently emitting no PDF for a master whose `.typ` is missing (resolved **behavioral** at discuss — D-01), and the nested-master render gate stops asserting on `typst-py` error-message substrings | WR-01, WR-02 |
| 22.4 — README 記述の実測乖離解消 (INSERTED) | README.md（+ `CLAUDE.md` / `pyproject.toml` コメント）の全記述を実測と突き合わせて再検証。検証機構を持てない数値（テスト数・カバレッジ）は書き戻さず**削除**、設定一覧は部分列と明示して実ビルドされる docs へ誘導、機能・制限・Status・方法論は測って書き直す。**プロースのみ・ソース非変更** | DOC-01..DOC-05 |
| 23 — v0.6.2 Release Prep + Regression-Gate Close | Prep-only: bump `pyproject.toml` → 0.6.2 + `CHANGELOG.md` `[0.6.2]` entry, close on the full-corpus regression gate; publish runs at `/gsd-complete-milestone` | (release/close — none) |

**Coverage:** 25/25 v1 requirements mapped (FID-02..FID-14 + PDF-01, PDF-02 + CONF-01..CONF-03 + WR-01, WR-02 + DOC-01..DOC-05) — no orphans, no duplicates. Phase 23 carries no requirement (release/close phase).

**Phase 22.4 は GATE-01 の対象外** — ノードハンドラを変更しないため実 `typst.compile()` の検証手段が無い。RESEARCH Task F / VALIDATION の記録どおり、**内容アンカーの `grep` 表明が誠実な到達点**であり新規テストファイルは追加しない（数値クレームの是正は「削除」なので不在 assert は張り合いが薄く、本当に価値のある自動化＝`sphinx-build -b linkcheck` の CI 化はそれ自体が 1 フェーズ級のため todo へ）。

**Phase 23 への申し送り（D-11）:** `pyproject.toml` を 0.6.2 にバンプする際、README の `**Status**: Stable (v0.6.1)` 行も同時に更新すること。

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

4 pending (`.planning/todos/pending/`):

- **ドキュメントのホスティング先を Read the Docs に変更** (docs) — 未検討
- **非文字列 docname が生 `TypeError` を投げる** (builder) — Phase 22.3 の D-06 で明示的に先送り。`typst_documents` に `(123, ...)` のようなエントリがあると `path.join` が `try` の外側で `TypeError` を投げ、集約 `ExtensionError` に乗らず生の traceback で落ちる。将来の入力バリデーション作業として。
- **`citation` ノード未対応が未追跡** (translator, examples) — Phase 22.2 で表面化（`visit_citation` ハンドラ不在のため rST citation が隣接式として出力され Typst 構文エラー）。22.2 ではサンプルから citation 構文を撤去して回避、恒久対応は未計画。
- **README の記述を全体的に見直す** (docs) — 2026-07-22 capture。実測で確認した乖離: テスト数 413→実測 577（`README.md:223,243`）、Status 行が `v0.5.0` のまま（`:322`、実際は 0.6.1）、Configuration Options が 5 件しか挙げず登録済み 12 件と乖離（`:203-211` vs `typsphinx/__init__.py:44-62`、`typst_documents` すら未掲載）。github.io リンクの修正は **RTD 移行 todo と競合するので着手順を先に決めること**。付随して **`CLAUDE.md` の Python 記述が stale**（3.10+/py310–313 と書いてあるが実際は `>=3.12`・py312/py313 のみ）と判明、別途要修正。

### Blockers/Concerns

None open. Phase 22 security review closed 9/9 threats (`22-SECURITY.md`, `threats_open: 0`); its 3 code-review findings are fixed (`22-REVIEW-FIX.md`). Phase 21's 3 advisory review warnings (WR-01/02/03 in `21-REVIEW.md`) remain non-blocking release-polish candidates. UI note: the v0.6.2 phases are Typst PDF typesetting / rendering-fidelity work, NOT frontend UI — no `### UI hint` annotations were added (the project's `ui.plan-gate` false-positives on PDF/rendering phases; use `--skip-ui` if it flags them).

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260720-p2w | Document worktree-isolated executor env provisioning (uv sync + uv run) in CLAUDE.md | 2026-07-20 | cc21f47 | [260720-p2w-add-a-worktree-isolated-execution-subsec](./quick/260720-p2w-add-a-worktree-isolated-execution-subsec/) |
| 260722-t3q | Remove stray .bg-shell directory (unreferenced) and gitignore it | 2026-07-22 | 58a5481 | [260722-t3q-remove-bg-shell-directory](./quick/260722-t3q-remove-bg-shell-directory/) |
| 3 | .ruff_cacheをgit管理から外す | 2026-07-22 | 62b7819 | — |

### Roadmap Evolution

- 2026-07-20: v0.6.2 roadmap created — Phases 19–23, derived from 14 v1 requirements (FID-02..FID-14 + PDF-01). Phase numbering continues from v0.6.1 (ended at Phase 18). Shape: 3 root-cause-clustered translator-fix phases (A / B / C-D-E-F) + 1 independent builder-bug phase (Issue #117) + 1 prep-only Release/close phase.
- 2026-07-13: v0.6.1 roadmap created — Phases 16–18, derived from 6 named v1 requirements. Continued from v0.6.0.
- Phase 22.1 inserted after Phase 22: typstpdf compile-root alignment for nested masters (PDF-02) — split from the master-output-layout todo (item A only; B/C stay deferred) (URGENT)
- 2026-07-22: backlog reviewed (`/gsd-review-backlog`) — 999.1 and 999.2 removed as delivered (Phases 19–21 / 22); 999.3 folded into 999.4; **999.4 promoted into v0.6.2 as Phase 22.2** (owner: 今マイルストーンで変更する), sequenced before the Phase 23 release prep so the `typst_output_dir` removal lands in the `[0.6.2]` CHANGELOG; 999.5 opened for the Phase 22.1 WR-01/WR-02 warnings
- 2026-07-22: backlog reviewed again (`/gsd-review-backlog`, 2nd pass) — the sole remaining item **999.5 promoted into v0.6.2 as Phase 22.3** (owner decision), sequenced after 22.2 (shared `builder.py` / render-gate surface) and before the Phase 23 release prep so any WR-01 behavior change lands in the `[0.6.2]` CHANGELOG. WR-01/WR-02 added to `REQUIREMENTS.md` (20/20 mapped). **The backlog is now empty.**
- Phase 22.4 inserted after Phase 22.3: README 記述の実測乖離解消 — テスト数・Status バージョン・Configuration Options・Known Limitations・docs リンクの全文再検証 (URGENT)

## Deferred Items

Items acknowledged and carried forward from previous milestone closes:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Forward-ecosystem | CFG-01 (was FWD-03): user-configurable `@preview` versions | Deferred to v2 | v0.5.0 scoping |
| Cross-OS verification | XOS-01: cross-OS docs-PDF CI (macOS/Windows) | Deferred to v0.6.x+ | v0.5.0 scoping |
| Graceful-degrade | DEG-03: real rendering (not placeholder) for `graphviz` / `inheritance_diagram` | Deferred to v2 (image pipeline) | v0.6.1 scoping |
| Cross-reference | XREF-02: link `manpage` / xrefs to external URLs via a configured base URL | Deferred beyond v0.6.2 | v0.6.1 scoping |

## Session Continuity

Last session: 2026-07-23T07:10:00.000Z
Stopped at: Phase 23 planned — ready to execute
Resume file: .planning/phases/23-v0-6-2-release-prep-regression-gate-close/23-01-PLAN.md

## Operator Next Steps

- Execute the release-prep phase with `/gsd-execute-phase 23` (3 plans / 3 sequential waves: version bump + sync test → corpus gate + evidence → `[0.6.2]` CHANGELOG)
- Then publish with `/gsd-complete-milestone` (tag `v0.6.2` → `release.yml` → PyPI → GitHub Release) — deliberately outside Phase 23's scope fence (SC#5)
