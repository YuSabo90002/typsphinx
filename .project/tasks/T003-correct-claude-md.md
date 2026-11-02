---
id: T003
title: Correct CLAUDE.md architecture claims and drop the GSD Core worktree-execution text
wave: 1
deps: []
status: pending
agent: null
base: null
worktree: null
task_branch: null
files:
  - CLAUDE.md
---

# T003 — Correct CLAUDE.md architecture claims and drop the GSD Core worktree-execution text

## Context

CLAUDE.md is loaded into every coding agent and carries stale claims (DOCS-AUDIT #4–#8, all ruled fix-doc, "全部推奨で"). #4: the writer bullet says `TypstWriter.translate()` branches on master vs. included documents via `_is_master_document()`, which no longer exists — `writer.py:234-262` now writes every content file unconditionally with its `@preview` imports and template application moved to the per-document wrapper rendered by `render_wrapper()` (split landed in 36a5f588). #5: translator figures "~2700 lines, ~140 visit_/depart_ methods" — actual 8149 lines / 189 methods. #6: the `@preview` version-sync section names four packages; there are five (`codly` 1.3.0, `codly-languages` 0.1.10, `mitex` 0.2.7, `gentle-clues` 1.3.1, `diagraph` 0.3.7) across `typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ`, enforced by `tests/test_preview_version_sync.py`. #7: `typst_documents` format omits the optional fifth element (template registry key; see `typsphinx/__init__.py:58-62` and `examples/charged-ieee/approach2/conf.py:15`). #8: the "Applicability — worktree isolation is the STANDING execution mode" paragraph (around line 116) describes GSD Core tooling (`workflow.use_worktrees`, `#683`, `worktree base-check`, `baseref-head`) that is no longer the project's pipeline.

## Approach

- Remove the GSD Core-specific worktree text so `grep -nE "use_worktrees|#683|baseref-head|base-check" CLAUDE.md` prints nothing. Keep the "Worktree-isolated execution" detection rule, NixOS boundary, the per-worktree recipe (`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` + run everything via `uv run`) and its rationale — those are accurate.
- Rewrite the `writer.py` bullet for the content-file plus `render_wrapper()` split; verify the symbol names against `typsphinx/writer.py` / `typsphinx/builder.py` / `typsphinx/template_engine.py` before writing them. No `_is_master_document` mention may remain.
- Translator figures: drop them (preferred) or restate them to match `wc -l typsphinx/translator.py` and the count of `def visit_`/`def depart_` at your base. The stale `~2700` / `~140` must not remain.
- `@preview` section: say five packages and name `diagraph`; do not bump or touch any version anywhere (veto/constraint) — this is prose only.
- `typst_documents`: document the optional fifth element (template registry key), consistent with README.md.
- Remove `typst_debug` from the "Configuration surface" config list (T002 removes the value in the same wave; CLAUDE.md must not advertise it). Prose only — no code dependency.
- Do not disturb the toolchain-pin paragraphs (`tox-uv~=1.35`, the multi-place sync hazard and "this file's two mentions") or the NixOS shim section — they are verified. Do not touch `.planning/` references elsewhere in the repo.

## Interface contract

- None

## Intent coverage

- SC3

## Acceptance criteria

1. `grep -nE "use_worktrees|#683|baseref-head|base-check" CLAUDE.md` prints nothing.
2. The per-worktree recipe `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` plus running commands via `uv run` remains documented in CLAUDE.md.
3. `grep -n _is_master_document CLAUDE.md` prints nothing, and the writer bullet describes the content-file plus `render_wrapper()` split.
4. The `@preview` version-sync section names five packages including `diagraph`.
5. The translator line/method figures match the code or are removed (no `~2700` or `~140`).
6. The `typst_documents` description documents the optional fifth element (template registry key); `typst_debug` is no longer listed as a config value; the `tox-uv~=1.35` toolchain-pin text is intact.

## Verify

```bash
! grep -nE "use_worktrees|#683|baseref-head|base-check" CLAUDE.md && ! grep -n _is_master_document CLAUDE.md && grep -qF 'env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev' CLAUDE.md && grep -q 'uv run' CLAUDE.md && grep -q 'render_wrapper' CLAUDE.md && grep -q 'diagraph' CLAUDE.md && grep -qiE 'five .*@preview|@preview.* five|five Typst Universe' CLAUDE.md && ! grep -nE '~2700|~140' CLAUDE.md && grep -qiE 'fifth element|registry key' CLAUDE.md && ! grep -n 'typst_debug' CLAUDE.md && grep -q 'tox-uv~=1.35' CLAUDE.md
```

Heavy: no

## Log

- 2026-11-03 — created by planner
