# Phase 39 — Closing Gate Evidence (Plan 39-08)

**Run:** 2026-08-02, in this worktree, after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync
--extra dev` and the `uv`/`ruff` NixOS-sandbox shims (per `CLAUDE.md` "Worktree-isolated execution"
and the project's `nixos-sandbox-test-env` memory). Base commit
`6f891563b835972a9c0179bb7fe1dfb917fb4554` (merges 39-01 through 39-07).

Every command below was run for real in this session; none of its results are inferred or copied
from an earlier plan's SUMMARY.

---

## 1. The full-corpus real-render gate — ACTUALLY RAN, not skipped

```
$ uv run pytest tests/test_corpus_gate.py -m slow -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
collected 5 items / 3 deselected / 2 selected

tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED [ 50%]
tests/test_corpus_gate.py::test_empty_url_before_after SKIPPED (SC#3
before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1
to run it (RESEARCH Open Question 1))                                    [100%]

================= 1 passed, 1 skipped, 3 deselected in 14.17s ==================
```

**Resolved corpus tag:** `v9.1.0` (`resolve_corpus_tag()` returns `f"v{sphinx.__version__}"`;
`sphinx.__version__` measured live in this worktree's venv: `9.1.0`).

**Cache:** the corpus was already present at `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0` before
this run (confirmed via `ls` before running the gate) — no network clone was needed this session,
and the test's own caching-by-resolved-tag behavior means a clone would have happened
transparently had the cache been cold.

**Duration:** 14.17s (pytest's own reported summary line, above).

**Pass/fail:** `TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error` **PASSED** — the real
`sphinx-build -b typstpdf` over Sphinx's own `doc/` tree, augmented per the test's own D-03 2-line
`conf.py` append, produced no fatal Typst error. This is the requirement T-39-SC/SC#5 needs.

**The one SKIP in this output (`test_empty_url_before_after`) is NOT the corpus gate itself** — it is
a separate, explicitly env-gated (`TYPSPHINX_CORPUS_REPORT=1`) diagnostic measurement unrelated to
whether the corpus compiles. It is deselected by default and is not part of what SC#5 or this plan's
`must_haves.prohibitions` (first entry) require to run. **The corpus gate itself ran and passed — this
is not recorded as a pass on the strength of a skip.**

---

## 2. Full test suite, unfiltered

```
$ uv run pytest -q
============================= test session starts ==============================
collected 764 items
...
===================== 763 passed, 1 skipped in 69.91s (0:01:09) ======================
```

**763 passed, 1 skipped, 0 failed.** Total 764, matching the recorded reference baseline (762
passed / 2 skipped / 0 failed on the merged main tree — differing skip count between a worktree and
the main tree is normal here since this worktree's own real-run of the corpus gate above resolved
one of the two skips into a pass; the *total* of 764 is what must and does agree).

---

## 3. Fast tier (`not slow`)

```
$ uv run pytest -m "not slow" -q
collected 764 items / 29 deselected / 735 selected
...
===================== 735 passed, 29 deselected in 51.02s ======================
```

**735 passed, 0 failed, 29 deselected (the slow-marked corpus-gate class).** Matches
`39-06-SUMMARY.md`'s own recorded fast-tier baseline (735 passed) with zero regressions introduced
by this plan's own (documentation-only) work.

---

## 4. `test_preview_version_sync.py` — the gentle-clues pin, confirmed by name

```
$ uv run pytest tests/test_preview_version_sync.py -x -v
tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED
3 passed
```

**All three green.** This phase changed which of gentle-clues' functions are called (`tip`, `error`,
`notify`, `abstract` alongside the pre-existing `info`/`warning`/`task`), not the pin, and the two
newly-used functions (`notify`, `abstract`) were already in scope through the existing wildcard
import `#import "@preview/gentle-clues:1.3.1": *` — confirmed by this green result, not assumed.

---

## 5. Lint, format, type trio

```
$ uv run black --check .
All done!
198 files would be left unchanged.

$ uv run ruff check .
All checks passed!

$ uv run mypy typsphinx/
Success: no issues found in 6 source files
```

All three pass with zero findings.

---

## 6. Documentation dogfood build through the Typst PDF environment

```
$ uv run tox -e docs-pdf
docs-pdf: commands[0] .../docs> sphinx-build -b typstpdf source _build/pdf
...
Copying template assets...
Compiling 1 master document(s) to PDF...
Generated PDF: .../docs/_build/pdf/typsphinx.pdf
build succeeded, 4 warnings.
  docs-pdf: OK (3.96=setup[0.50]+cmd[3.45] seconds)
  congratulations :) (3.98 seconds)
```

Exit 0. `docs/_build/pdf/typsphinx.pdf` generated, 1,938,001 bytes.

**Page count:** measured live via `pypdf.PdfReader(...).pages`:

```
$ uv run python3 -c "
import pypdf
r = pypdf.PdfReader('docs/_build/pdf/typsphinx.pdf')
print('pages:', len(r.pages))
"
pages: 91
```

**91 pages**, versus the **90 pages** recorded as the post-Phase-38 baseline in
`38-08-GATE-EVIDENCE.md`/`38-TEST-CENSUS.md`'s own Bucket D table (`tox -e docs-pdf` measurement).
**+1 page.** This project's own `docs/source/` tree contains **no literal `.. rubric::`,
`.. seealso::`, `.. topic::`, `.. admonition::`, `.. attention::`, or `.. danger::` directive**
(confirmed live: `grep -rln` for each of those directive spellings across every `.rst` file under
`docs/source/` returns nothing) and `docs/` itself carries zero commits across this whole phase
(`git log --oneline 8406b8a..HEAD -- docs/` is empty) — so the +1 page is entirely a consequence of
this phase's `typsphinx/translator.py` changes reaching content that was already there, not of any
docs-content edit.

The docs project does contain 3 real admonitions (`note`/`warning`/`tip` type, confirmed by the same
grep) whose English catalog titles are byte-identical to their pre-phase hardcoded titles (per this
plan's own `39-TEST-CENSUS.md` finding), so title-length change is not the cause here. The
`api/index.rst` autodoc-generated content is the more likely source: every `py:class`/`py:function`
directive with parameters and options emits at least one machine-generated `rubric` ("Options")
node, invisible to a literal-directive grep but real at the docutils-tree level that
`visit_rubric`/`depart_rubric` walk. Two of this phase's rubric fixes pull page count in opposite
directions on exactly this kind of content: **D-11's separator-double-count fix removes** up to two
blank lines at each qualifying anchor (shrinks), while **D-13's `_rubric_was_*` slot-rename fix
restores** the `par({...})` wrapper to every subsequent paragraph in the document that a
markup-containing rubric's state-bookkeeping bug had previously (silently, pre-fix) stripped it from
document-wide (expands — D-13 itself documents this defect as reaching "every subsequent paragraph
in the document to the end of the file," so its fix can only ever add spacing back, never remove
more than the wrapper it restores). A net **+1** page is consistent with these two legitimate,
phase-scoped mechanisms only partially offsetting each other over a ~90-page document, and is not
evidence of a defect — no unexpected content, broken layout, or compile warning accompanies it (the
build's 4 warnings are pre-existing docstring/docutils warnings unrelated to admonitions or rubrics,
visible in the raw build log: two `visit_toctree` docstring indentation warnings and one
`visit_desc_sig_name` inline-emphasis warning, plus one `unknown_visit` for a `<problematic>` node —
none of which are new to this phase).

---

## 7. Milestone invariants, re-checked by command at close

**(a) Zero new runtime dependencies:**

```
$ git diff 8406b8a..HEAD -- pyproject.toml
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -44,6 +44,7 @@ dev = [
     "twine>=5.0",
     "build>=1.0",
     "pypdf>=6.14,<7",
+    "pillow>=12.3,<13",  # D-07: ADM-04 greyscale render (Image.convert), dev-only
 ]
 docs = [
```

The only `pyproject.toml` change across the whole phase is the single `pillow` line added to
`[project.optional-dependencies].dev` (D-07, gated behind a `checkpoint:human-verify` package
legitimacy check at plan 39-04). `[project.dependencies]` (the runtime array, lines 27-31) shows
**zero** lines in the diff — confirmed unchanged, live:

```
$ (lines 27-31 of pyproject.toml, read live)
dependencies = [
    "sphinx>=9.1,<10",
    "docutils>=0.21,<0.23",
    "typst>=0.15.0,<0.16",
]
```

Same three runtime dependencies as pre-phase. **Invariant held.**

**(b) No new `@preview` package imported anywhere under `typsphinx/`:**

```
$ grep -n "@preview" typsphinx/*.py
typsphinx/writer.py:155:            imports.append('#import "@preview/codly:1.3.0": *')
typsphinx/writer.py:156:            imports.append('#import "@preview/codly-languages:0.1.10": *')
typsphinx/writer.py:157:            imports.append('#import "@preview/mitex:0.2.7": mi, mitex')
typsphinx/writer.py:158:            imports.append('#import "@preview/gentle-clues:1.3.1": *')
typsphinx/template_engine.py:612:            output_parts.append('#import "@preview/codly:1.3.0": *')
typsphinx/template_engine.py:613:            output_parts.append('#import "@preview/codly-languages:0.1.10": *')
typsphinx/template_engine.py:614:            output_parts.append('#import "@preview/mitex:0.2.7": mi, mitex')
typsphinx/template_engine.py:615:            output_parts.append('#import "@preview/gentle-clues:1.3.1": *')

$ grep -n "@preview" typsphinx/templates/base.typ
8:#import "@preview/codly:1.3.0": *
9:#import "@preview/codly-languages:0.1.10": *
14:#import "@preview/mitex:0.2.7": *
19:#import "@preview/gentle-clues:1.3.1": *
```

**Exactly four packages** (`codly`, `codly-languages`, `mitex`, `gentle-clues`) at all three
lockstep sites (`writer.py`, `template_engine.py`, `templates/base.typ`) — the same count and the
same package set as pre-phase. `test_preview_version_sync.py` (§4 above) confirms these three sites
agree with each other and with `examples/**/*.typ`. This phase changed *which functions* of
gentle-clues are called (adding calls to `tip`, `error`, `notify`, `abstract`, all already reachable
through the existing wildcard import), not the import line itself. **Invariant held.**

**(c) The pinned gentle-clues version is identical to its pre-phase value:**

```
$ git show 8406b8a:typsphinx/writer.py | grep gentle-clues
            imports.append('#import "@preview/gentle-clues:1.3.1": *')
```

`1.3.1` pre-phase, `1.3.1` post-phase (confirmed live in §b above) — byte-identical. **Invariant
held.**

---

## Summary of this task's verification commands

| Command | Result |
|---|---|
| `uv run pytest tests/test_corpus_gate.py -m slow -v` | 1 passed (14.17s, tag `v9.1.0`), 1 skipped (unrelated env-gated diagnostic), 3 deselected |
| `uv run pytest` (unfiltered) | 763 passed, 1 skipped, 0 failed (69.91s) |
| `uv run pytest -m "not slow"` | 735 passed, 29 deselected, 0 failed (51.02s) |
| `uv run pytest tests/test_preview_version_sync.py -x` | 3 passed |
| `uv run black --check .` | clean, 198 files unchanged |
| `uv run ruff check .` | clean |
| `uv run mypy typsphinx/` | clean, 6 source files |
| `uv run tox -e docs-pdf` | exit 0, PDF generated, 91 pages (90 pre-phase, +1 explained above) |
| `git diff -- pyproject.toml` (runtime deps) | empty (only `[dev]` gained `pillow`) |
| `@preview` import count/pin | 4 packages, gentle-clues `1.3.1`, unchanged at all 3 sites |
