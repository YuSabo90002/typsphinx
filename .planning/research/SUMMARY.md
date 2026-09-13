# Project Research Summary

**Project:** typsphinx v0.9.4 Typing Modernization (QUA-09)
**Domain:** Mechanical Python typing-annotation modernization (contributor tooling, behaviour-preserving)
**Researched:** 2026-09-13
**Confidence:** HIGH — every claim backed by direct measurement against ruff 0.16.6 (pinned in `uv.lock`), not documentation alone

> Persisted by the orchestrator: the synthesizer returned this document inline after its Write
> call was refused (issue #222 self-heal). The orchestrator corrected four factual slips against
> the four source files while persisting it: the `typsphinx/` file count (6, not 7), the
> post-`--fix` residue (2 violations on `typsphinx/__init__.py:15`, not 19), which test file uses
> `ast.Dict` (only `tests/test_authors_pipeline_stage_gate.py:515`), and a fabricated timestamp.

## Executive Summary

QUA-09 is a **pure syntax rewrite** of Python typing imports and annotations: `typing.Dict`/`List`/`Set`/`Tuple` → builtin generics `dict`/`list`/`set`/`tuple`, plus `typing.Iterator` → `collections.abc.Iterator`. Removing the two ruff ignores exposes 113 violations (93 UP006 + 20 UP035) across **10 files — 6 in `typsphinx/` (92) and 4 in `tests/` (21)** — measured by `ruff check . --select UP006,UP035` against the actual tree, not by the stale 2026-07-22 todo. Runtime behaviour and emitted Typst output are unchanged; the only visible side effect is that the published API reference renders `dict[str, Any]` instead of `Dict[str, Any]`.

The critical risk is not the rewrite itself — one `ruff check . --fix` pass resolves 111 of 113 — but a genuine self-contradiction: `CLAUDE.md:75` currently forbids this exact work ("Don't 'modernize' typing imports until that todo lands"), and every executor auto-loads that document as a standing instruction. A secondary risk is the todo's stale file list, which names four `typsphinx/` files and no `tests/` files.

No new dependencies, no runtime hazards, no public API changes. mypy and black produce identical output before and after; the full pytest suite is green on the converted scratch tree.

## Key Findings

### Recommended Stack

**No new technologies.** Toolchain-native: ruff 0.16.6 (pinned in `uv.lock`), black 26.5.1, mypy (main-checkout `.venv` has 2.1.0 while `uv.lock` resolves 2.3.1 — pre-existing drift, out of scope; worktrees sync to the lock; both treat PEP 585 generics identically), Python ≥3.12.

**Conversion mechanics:**
- `ruff check . --fix` (ignores removed) resolves **111 of 113** in one pass: the UP006 usage rewrites, plus F401 removal of import names left unused.
- **Two violations remain, both on `typsphinx/__init__.py:15`** (`from typing import Any, Dict`): ruff treats package `__init__.py` imports as probable re-exports and gates the F401 fix behind `--preview`. It survives `--fix` and `--fix --unsafe-fixes`; only `--unsafe-fixes --preview` removes it, and CI / `tox -e lint` never pass `--preview`. **Hand-edit the one line** to `from typing import Any`. A second `--fix` pass is a no-op.
- `Iterator` migration: `tests/test_include_ledger_removal_gate.py:47` → `from collections.abc import Iterator` (the pattern `typsphinx/builder.py:11` already uses).
- No other rule starts firing: after the fix + hand edit, bare `ruff check .` reports `All checks passed!`. No I001 reorder issue; UP007/UP045 have nothing to do (zero `Optional[...]`/`Union[...]` in the codebase).
- black: `348 files would be left unchanged` before and after. mypy: `Success: no issues found in 9 source files` before and after.
- `sphinx-autodoc-typehints` 3.0.1: `sphinx.util.typing.stringify_annotation` renders `Dict[str, Any]` vs `dict[str, Any]` — the sole visible change.

### Expected Features

No user-facing feature; "features" here are the scope items that make the milestone done.

**Table stakes:**
- Remove `"UP035"`/`"UP006"` and their deferral comments from `pyproject.toml:128-129`.
- Zero UP006/UP035 findings, discovered repo-wide at execution time (`examples/`, `docs/`, `scripts/` are in `ruff check .` scope and currently clean). **Do not hard-code "113"** — it holds only for ruff 0.16.6.
- `Iterator` → `collections.abc`.
- Gate quartet green: `ruff check .`, `black --check .`, `mypy typsphinx/`, full `pytest`.
- `CLAUDE.md:75` prohibition rewritten to reflect completion; todo moved to `todos/completed/`.
- CHANGELOG bullet under the existing `## [Unreleased]`, in the register of the three existing bullets (bold summary + req ID + "no effect on installing or using typsphinx"), naming the API-reference type-text change.

**Differentiators (evidence that behaviour is unchanged):**
1. Zero pre-existing test-assertion edits (`git diff` shows only import and annotation lines in the 4 test files).
2. pytest collected / passed counts identical before vs after.
3. **AST comparison modulo annotation nodes**, reusing v0.9.3 Phase 68's masked-AST-hash harness (`68-TOX-EVIDENCE.md:248-326`; code at `68-02-PLAN.md:253` and `:305`). Phase 68 masked docstrings and assert messages; QUA-09 masks annotation subtrees (`arg.annotation`, `returns`, `AnnAssign.annotation`) plus the `typing` import line. Hash current tree vs `git show <base>:<path>`, equal per file.
4. Byte-identical `.typ` output over the existing golden/render-gate fixture corpus.
5. mypy output string-identical (not just exit code).
6. Clean docs build diff (`rm -rf docs/_build` first) confined to type text on the API reference pages.

**Anti-features (refuse):** PEP 604 `X | None` sweep (nothing to convert, no rule forces it); `from __future__ import annotations` (changes runtime annotation semantics); any public API / signature change; touching the `@preview` version-sync lines near the edited imports in `builder.py`/`writer.py`/`template_engine.py`; running `ruff --fix` / `black` beyond the ten files.

### Architecture Approach

**Build shape (ARCHITECTURE.md):** one code phase (70) with two waves, then close prep (71).

Wave 1 — five parallel, file-disjoint conversion plans, each lint-green on merge because the ignores are still in place:
- **A:** `typsphinx/translator.py` (42)
- **B:** `typsphinx/builder.py` (30; its existing `collections.abc.Iterator` import at line 11 is untouched)
- **C:** `typsphinx/template_engine.py` + `typsphinx/template_registry.py` (16)
- **D:** `typsphinx/writer.py` + `typsphinx/__init__.py` (4; includes the `__init__.py:15` hand edit)
- **E:** `tests/conftest.py`, `tests/test_bundle_layout_sweep_gate.py`, `tests/test_include_edge_derivation_unit.py`, `tests/test_include_ledger_removal_gate.py` (21; includes the `Iterator` move)

Wave 2 — **F:** the only plan touching `pyproject.toml` and `CLAUDE.md` (avoiding the "disjoint files still collide at merge" hazard): remove the ignores, rewrite `CLAUDE.md:75`, move the todo, re-measure `ruff check . --select UP006,UP035` repo-wide expecting zero, run the gate quartet.

`ruff check . --select UP006,UP035` on the CLI overrides the config ignore (the 113 was measured with the ignores present), so per-plan decreasing counts are observable during Wave 1.

**Never `sed`-replace.** `tests/test_authors_pipeline_stage_gate.py:515` uses `ast.Dict` (the stdlib `ast` dict-literal node, `isinstance(node.value, ast.Dict)`), unrelated to `typing.Dict`; that file has zero violations and is not in scope, but a blind substitution would corrupt it into a nonexistent `ast.dict`. Use `ruff --fix` (AST-aware) or reviewed manual edits.

No test introspects `__annotations__`, calls `get_type_hints`, or `isinstance`-checks against typing objects; no module uses `from __future__ import annotations`; no module-level type aliases, `cast("List[...]")` strings, or `TypeVar` bounds use these names.

**Orchestrator correction (ARCHITECTURE.md §3):** that file's claim that Phase 68 has no Python AST hashing is retracted — the masked-AST-hash prior art above exists and its harness shape is reusable.

### Critical Pitfalls

1. **`typsphinx/__init__.py:15` survives `ruff --fix`** — needs a planned one-line manual edit; verify with bare `ruff check .` (matching CI). Do not enable `--preview`.
2. **`CLAUDE.md:75` forbids this milestone** — auto-loaded into every executor's context. Either rewrite it before conversion starts or carry explicit written authorization (citing PROJECT.md's Current Milestone) in every Wave 1 plan.
3. **Multi-location sync** — `pyproject.toml:128-129`, `CLAUDE.md:75` and the todo move must end consistent; this project already recorded a Phase 65 → 68 drift of the same shape.
4. **Stale todo file list** — misses `template_registry.py` (postdates the todo), `writer.py`'s real `Tuple`, and all 21 `tests/` violations. Discovery is by fresh repo-wide `ruff check . --select UP006,UP035`, never by the todo's list.
5. **Dependabot can bump ruff mid-milestone** (on the `uv` ecosystem since v0.9.3; #138 moved 0.15 → 0.16 and widened the spec). Success criteria state "zero findings", and a ruff bump PR should not be merged while conversion is in flight; if one is, re-measure and treat the new count as authoritative.

Also carried: `phase.complete` has auto-flipped release/close checkboxes against CONTEXT decisions at eight prior close-prep phases (v0.9.3 REL-12 most recently) — diff and revert before committing in Phase 71. Locale-dependent assertions should be run under `LC_ALL=C` locally; CI holds lint authority.

## Implications for Roadmap

### Phase 70: Typing Modernization (QUA-09)

**Rationale:** mechanical, single-domain change; all plans file-disjoint.
**Delivers:** ignores removed, zero UP006/UP035 findings, `Iterator` on `collections.abc`, `CLAUDE.md` and todo bookkeeping, behaviour-neutrality evidence (AST-mask hash, test-count identity, zero assertion edits, `.typ` byte identity, mypy output identity, docs diff confined to type text).
**Avoids:** Pitfalls 1–5.

### Phase 71: v0.9.4 Close Prep (prep-only, unpublished)

**Rationale:** same shape as v0.9.3 Phase 69 — bookkeeping only, no `typsphinx/` or `tests/` change.
**Delivers:** CHANGELOG bullet under `## [Unreleased]` naming the API-reference type-text change; `pyproject.toml` stays `0.9.2`; no tag, PyPI upload or GitHub Release; CI evidence cited from real matrix runs (including `windows-latest` and `macos-latest` lanes).
**Avoids:** the `phase.complete` checkbox auto-flip.

### Phase Ordering Rationale

- Wave 1 before Wave 2: removing the ignores before every file is converted makes `ruff check .` red on the unconverted remainder.
- Phase 70 before Phase 71: close prep documents what landed.
- No research phase needed — scope and mechanics are measured.

### Key Open Decision for the Roadmapper

**Where the `CLAUDE.md:75` rewrite lands.** ARCHITECTURE.md puts it in Wave 2 (flip last); PITFALLS.md wants it first, because executors auto-load CLAUDE.md. The two are compatible — the `pyproject.toml` ignore flip must be last, but the prose rewrite need not be:
1. Rewrite `CLAUDE.md:75` in a Wave 0 / first plan before conversion (lint-neutral), flip the ignores in Wave 2.
2. Keep it in Wave 2 and give every Wave 1 plan explicit override authorization.
3. Put it as the first task of one Wave 1 plan (reintroduces a shared-file concern only if another plan also touches `CLAUDE.md`, which none does).

Note the multi-location-sync pitfall pulls toward landing the three edits together, which favours option 2 unless the CLAUDE.md rewrite is worded so it is true both before and after the flip.

### Research Flags

No phase needs `/gsd-research-phase`. Phase 70 planning should pilot the AST-mask hash on one file (e.g. `translator.py`) before wiring it into an automated verify block — the normalization is new code even though the harness is prior art.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | ruff/black/mypy/autodoc behaviour measured on a scratch copy of the real tree |
| Features | HIGH | scope measured by `ruff --output-format=json`; evidence mechanisms from this project's own prior art |
| Architecture | HIGH | file-disjoint wave plan derived from measured per-file counts; Phase 68 prior art confirmed by the orchestrator |
| Pitfalls | HIGH | each backed by command output or file:line; ja-translation drift is MEDIUM (translations repo not checked out locally) |

**Overall confidence:** HIGH

### Gaps to Address

- **ja translation drift:** API-reference type text will change; the `typsphinx-doc-translations` catalogs resync only at a publishing release, so any msgid drift surfaces at the next published release, not here. Note it in Phase 71's CHANGELOG bullet or handoff.
- **Worktree interpreter drift:** fresh worktree venvs may be uv-managed CPython 3.14.x vs the main checkout's 3.13.13 (no upper bound on `requires-python`, no `.python-version`). Compare `.venv/pyvenv.cfg` before attributing any RED to the typing change.
- **Dependabot ruff bump mid-Phase 70:** Plan F re-measures first; a changed ruff version is recorded in its evidence.

## Sources

### Primary (HIGH confidence)
- Direct measurement (ruff 0.16.6): `ruff check . --select UP006,UP035 --statistics`, `--output-format=json`, `--fix`, `--fix --unsafe-fixes`, `--fix --unsafe-fixes --preview`, run in scratch copies of the tree, 2026-09-13.
- `.planning/PROJECT.md` (Current Milestone: v0.9.4), `CLAUDE.md` (line 75; the `@preview` and toolchain-pin sync hazards), `pyproject.toml` (`[tool.ruff.lint]`, `[tool.mypy]`).
- `.planning/todos/pending/2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md`.
- `.planning/milestones/v0.9.3-phases/68-documentation-follow-through-claude-md-tox-ini-flake-nix/68-TOX-EVIDENCE.md:248-326` and `68-02-PLAN.md:253`, `:305`.
- `ruff rule F401` built-in documentation (the `__init__.py` carve-out).

### Secondary (MEDIUM confidence)
- `.planning/MILESTONES.md`, `.planning/milestones/v0.9.3-ROADMAP.md` (close-prep shape, `phase.complete` auto-flip history, dependabot #138).
- `.github/workflows/ci.yml`, `tox.ini`, `docs/source/conf.py`, `CHANGELOG.md` `## [Unreleased]`.

---
*Research completed: 2026-09-13*
*Ready for roadmap: yes*
