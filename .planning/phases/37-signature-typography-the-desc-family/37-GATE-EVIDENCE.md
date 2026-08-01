# Phase 37 — Consolidated Gate Evidence

**Produced by:** `37-08-PLAN.md` (phase closeout), Task 1.
**Phase-start commit (before/after baseline):** `011b9265daf3389f3482b5efd96b4eaa16a94743`.
**This file is a consolidation, not a replacement.** The four Wave-1 evidence files
(`37-GATE-EVIDENCE-01.md`..`-04.md`) plus the Wave-5 gap-closure evidence file
(`37-GATE-EVIDENCE-09.md`) remain in place as the primary, per-plan record. This file adds the
milestone-invariant checks that only become answerable once every wave is done; Task 2 will add the
requirement verdict table, the ROADMAP SC mapping, and the control roster.

**Plan census note (read this first):** `37-08-PLAN.md` was authored before plan `37-09` existed.
`37-09` is a gap-closure plan the orchestrator authored mid-execution, on the owner's explicit
decision (2026-08-01), after the post-merge gate following Wave 3 caught a real defect — the
`block(above: 0pt, below: 0pt, sticky: true, ...)` wrapper made every signature's glyphs overlap the
first line of its own description body. `37-09` amended `37-EMISSION-CONTRACT.md` §3, corrected the
translator's wrapper emission, hand-re-derived every dependent expected string, and closed the whole
suite green for the first time in the phase. This document treats `37-09` as a first-class member of
the phase's evidence, not an afterthought.

---

## 1. Milestone invariants, verified by command (all run in this worktree, 2026-08-01)

### 1.1 Whole suite, default run

```
$ uv run pytest -m "not slow" -q
================== 658 passed, 29 deselected in 43.85s ==================
```

Zero failures, zero errors.

### 1.2 Full-corpus `-b typstpdf` gate (slow-marked, excluded from the default run)

```
$ uv run pytest tests/test_corpus_gate.py -m slow -v
tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED [ 50%]
tests/test_corpus_gate.py::test_empty_url_before_after SKIPPED (SC#3 before/after
  measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it) [100%]
================= 1 passed, 1 skipped, 3 deselected in 13.65s ==================
```

This is the run where 1,445 real `desc_signature` nodes from Sphinx v9.1.0's `doc/` corpus exercise
the new emission end to end — the corpus is cached at `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0`
(shared with the main tree), so this was a real recompile against the real corpus, not a cache-only
no-op. **`test_corpus_compiles_with_no_fatal_error` also asserts the `unknown_visit` catalogue is
EMPTY** (`tests/test_corpus_gate.py:361-365`) — it passed, so the corpus run surfaced **zero** new
unknown-node warnings from the `desc_sig_*` family (`desc_sig_literal_string` /
`desc_sig_literal_number` / `desc_sig_keyword_type` get correct styling "for free" via the
`in_signature_text` flag per contract §4.3, with no dedicated handler and no warning). No todo was
needed for that channel.

One unrelated, pre-existing docs-build finding was discovered while running `tox -e docs-pdf` for
§1.4 below — see that subsection.

### 1.3 Lint / type trio

```
$ uv run black --check .
All done! (183 files would be left unchanged.)

$ uv run ruff check .
All checks passed!

$ uv run mypy typsphinx/
Success: no issues found in 6 source files
```

### 1.4 `tox -e docs-pdf` — the project dogfooding its own builders

```
$ uv run tox -e docs-pdf
...
writing output... [api/index] done
...
Generated PDF: .../docs/_build/pdf/typsphinx.pdf
build succeeded, 4 warnings.
  docs-pdf: OK (3.91=setup[0.48]+cmd[3.42] seconds)
```

Runnable in this environment; it built and compiled successfully. Of the 4 warnings:

- 2 are Sphinx/`sphinx-autodoc-typehints` deprecation notices (`RemovedInSphinx10Warning`,
  unrelated to typsphinx or Phase 37).
- 1 (`visit_toctree`'s docstring, "Unexpected indentation") **pre-dates Phase 37** — confirmed by
  reading the same docstring at the phase-start commit (`011b926`); `visit_toctree` is untouched by
  this phase.
- 1 is **new, introduced by this phase's own docstring authoring** (plan `37-06`):
  `visit_desc_sig_name`'s docstring contains the phrase `"PyTypeObject *type, no intersphinx"`,
  whose bare `*` docutils parses as an unterminated inline-emphasis marker
  (`WARNING: Inline emphasis start-string without end-string`), which in turn produces a stray
  `problematic` node and an `unknown node type` warning during `writing output... [api/index]`
  (confirmed: `WARNING: unknown node type: <problematic ids="id2" refid="id1">*</problematic>`).
  This is a docs-build cosmetic defect, not a Phase 37 requirement failure — no SIG assertion covers
  a translator docstring's own prose, and `typsphinx/translator.py` is not in this plan's
  `files_modified`. Filed as a todo rather than fixed inline:
  `.planning/todos/pending/2026-08-01-visit-desc-sig-name-docstring-unbalanced-asterisk-warning.md`.

### 1.5 Standing invariant: zero new runtime dependencies

```
$ git diff 011b926..HEAD -- pyproject.toml
(empty)
```

No dependency was added, removed, or version-changed anywhere in the phase.

### 1.6 Standing invariant: `@preview` package count still four, no new lockstep site

```
$ uv run pytest tests/test_preview_version_sync.py -v
test_preview_versions_identical_across_declaration_sites PASSED
test_all_four_packages_declared PASSED
test_example_templates_match_canonical_versions PASSED
3 passed in 0.02s

$ git diff 011b926..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ
(empty)
```

None of the three `@preview`-version declaration sites CLAUDE.md names (`writer.py`,
`template_engine.py`, `templates/base.typ`) was touched by any Phase 37 plan. The package count and
versions are unchanged.

### 1.7 No new font selection

```
$ git diff 011b926..HEAD -- typsphinx/translator.py | grep -n "font"
299:+        and font-shrinking were both measured and rejected by the owner) --

$ grep -rn "set text(font\|text(font:" typsphinx/
(no matches)
```

The only "font" occurrence in the whole-phase diff is a docstring *comment* recording that font
shrinking was measured and rejected as an overflow strategy (D-06) — not a `set text(font: ...)`
call. D-04's prohibition holds: `raw(...)` is the only monospace primitive introduced this phase, and
a repo-wide search finds no font-family selection anywhere under `typsphinx/`. STATE.md's risk (a
font selection silently shadowing the `ja` build's CJK fallback) does not materialize.

### 1.8 No bundled Typst style module

```
$ git diff --name-only 011b926..HEAD -- typsphinx/
typsphinx/translator.py
```

`typsphinx/translator.py` is the **only** file under `typsphinx/` touched by the whole phase (all
eight executed plans, including the `37-09` gap closure). No new `.typ` file was added anywhere
under `typsphinx/`.

---

<!-- gsd:write-continue -->
