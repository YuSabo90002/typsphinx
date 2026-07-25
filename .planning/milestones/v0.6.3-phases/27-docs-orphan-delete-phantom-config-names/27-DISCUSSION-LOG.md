# Phase 27: Docs 実測整合 — Orphan Delete + Phantom Config Names - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-24
**Phase:** 27-docs-orphan-delete-phantom-config-names
**Mode:** `--auto` (autonomous — recommended option selected per question, no interactive prompts)
**Areas discussed:** Orphan delete scope, User-guide phantom rewrites, api/index.rst table + `.po`, Verification bar, Deletion-guard handling

---

## Orphan delete scope (DOC-06)

| Option | Description | Selected |
|--------|-------------|----------|
| Delete `docs/configuration.rst` only, per exact DOC-06 scope | Root `docs/` has no `conf.py` → true orphan; dangling `:doc:` refs in dead siblings are harmless | ✓ |
| Also fix dangling `:doc:` refs in `docs/usage.rst`/`installation.rst` | Touches non-scoped files | |
| Delete the whole legacy root-`docs/` cluster | Scope creep beyond DOC-06 | |

**Auto choice:** Delete only `docs/configuration.rst`; record the root-`docs/` dead-tree as a deferred cluster cleanup.
**Notes:** Verified root `docs/` has no `conf.py`; actual file is 489 lines (ROADMAP's 526 is stale). SC#1 "no live xref" is met because nothing Sphinx builds references it. "No unique content lost" → targeted salvage-check only (D-05), not a 489-line migration (would re-drift; file also uses wrong package name).

---

## User-guide phantom rewrites (DOC-07 surface A)

| Option | Description | Selected |
|--------|-------------|----------|
| Delete phantom knobs; rewrite papersize/fontsize as working `typst_elements` | Faithful to registered config; codly knobs & tuple author form removed | ✓ |
| Literal token-swap `typst_author`→`typst_authors` | Produces invalid tuple-typed `typst_authors` — new phantom | |

**Auto choice:** D-06 (remove codly phantoms), D-07 (delete tuple "Simple Format", keep dict "Detailed Format"), D-08 (`typst_elements = {"papersize": "us-letter", "fontsize": "20pt"}`), D-09 (drop phantom codly from Complete Example, keep real `typst_use_mitex`).
**Notes:** `typst_elements` keys verified against `template_engine.py:55-56` allowlist (papersize/fontsize) — real, not phantom.

---

## api/index.rst table + `.po` (DOC-07 surface B)

| Option | Description | Selected |
|--------|-------------|----------|
| Delete list-table (lines 45-84), keep `:doc:` pointer; regenerate `.po` via sphinx-intl | One canonical config place; multilang build stays green | ✓ |
| Hand-delete `.po` msgids | Risk of `.po`↔`.pot` drift | |

**Auto choice:** D-10 + D-11.
**Notes:** Config consolidated to `user_guide/configuration.rst`; api/index.rst becomes a pure pointer.

---

## Verification bar

| Option | Description | Selected |
|--------|-------------|----------|
| grep-zero phantoms + grep-cross-check registered set + green build + green suite | Docs-only, GATE-01 N/A per ROADMAP | ✓ |

**Auto choice:** D-12.

---

## Deletion-guard handling

| Option | Description | Selected |
|--------|-------------|----------|
| Plan for `worktree.cleanup-wave` block; manual merge after scope-measure | Deletion-bearing branch cannot auto-pass the gate (no bypass) | ✓ |

**Auto choice:** D-13.
**Notes:** Standing project constraint — exactly the Phase 27 recurrence flagged in prior memory.

## Claude's Discretion

- Exact prose of rewritten user-guide sections; whether Complete Example gains a `typst_elements` demo.
- Exact `.po` regeneration command.

## Deferred Ideas

- Legacy root-`docs/` dead-tree sweep (`usage.rst`, `installation.rst`, …) — own future phase.
- RTD hosting migration (~2026-07-30) — standing deferral.
- README github.io 404 link fixes — folded into RTD migration.
- `sphinx-build -b linkcheck` CI job — revisit with RTD move.
