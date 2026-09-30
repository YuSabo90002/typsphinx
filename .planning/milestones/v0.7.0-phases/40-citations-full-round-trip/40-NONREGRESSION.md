# Phase 40, Plan 04 — Non-Regression Evidence

**Recorded against commit:** `b45045ab07a849220d276d888aa6e2d99765e645` (`docs(phase-40): update
tracking after wave 3`), the tip of the finished phase at the time this file was written
(2026-08-02T10:27:43Z). The phase-start commit is `ccb37b2e7099386462968177cf500a196db67c07`
(`docs(40): create phase plan`).

This plan (40-04) modifies no file under `typsphinx/`, `examples/`, or any test module other than
(conditionally) `tests/test_desc_break_marker_buffer_swap_gate.py` — see item 8 below, which records
that no edit was needed there either. Its only file output is this evidence file.

---

## 1. Commit hash and whole-phase diffstat

Everything this phase touched, and nothing else:

```
$ git diff --stat ccb37b2e7099386462968177cf500a196db67c07..b45045ab07a849220d276d888aa6e2d99765e645
 .planning/REQUIREMENTS.md                                        |   24 +-
 .planning/ROADMAP.md                                             |   39 +-
 .planning/STATE.md                                                |   16 +-
 .../40-citations-full-round-trip/40-01-SUMMARY.md                 |  225 ++++
 .../40-citations-full-round-trip/40-02-SUMMARY.md                 |  185 ++++
 .../40-citations-full-round-trip/40-03-SUMMARY.md                 |  266 +++++
 .../40-citations-full-round-trip/40-04-PLAN.md                    |    4 +-
 .../40-citations-full-round-trip/40-05-PLAN.md                    |  360 +++++++
 .../40-citations-full-round-trip/40-05-SUMMARY.md                 |  199 ++++
 .../40-GATE-EVIDENCE-01.md                                        |  662 ++++++++++++
 .../40-GATE-EVIDENCE-02.md                                        |  279 +++++
 examples/charged-ieee/approach1/source/index.rst                  |   15 +-
 examples/charged-ieee/approach2/source/index.rst                  |   15 +-
 tests/fixtures/citation_render_gate/conf.py                       |   34 +
 tests/fixtures/citation_render_gate/index.rst                     |  125 +++
 tests/fixtures/citation_render_gate/second.rst                    |   20 +
 tests/test_citation_render_gate.py                                | 1113 ++++++++++++++++++++
 typsphinx/translator.py                                           |  348 ++++++
 18 files changed, 3881 insertions(+), 48 deletions(-)
```

Split by area, confirming the plan-level scope claims independently:

```
$ git diff --stat ccb37b2..HEAD -- typsphinx/ examples/ pyproject.toml uv.lock
 examples/charged-ieee/approach1/source/index.rst | 15 +-
 examples/charged-ieee/approach2/source/index.rst | 15 +-
 typsphinx/translator.py                          | 348 +++++++++++++++++++++++
 3 files changed, 364 insertions(+), 14 deletions(-)

$ git diff --stat ccb37b2..HEAD -- tests/
 tests/fixtures/citation_render_gate/conf.py    |   34 +
 tests/fixtures/citation_render_gate/index.rst  |  125 +++
 tests/fixtures/citation_render_gate/second.rst |   20 +
 tests/test_citation_render_gate.py             | 1113 ++++++++++++++++++++++++
 4 files changed, 1292 insertions(+)
```

`typsphinx/` carries exactly one touched file (`translator.py`, plan 40-03's implementation).
`examples/` carries exactly the two restored `charged-ieee` samples (plan 40-02). `pyproject.toml`
and `uv.lock` are absent from the diffstat entirely — zero new dependency. Under `tests/`, the ONLY
module touched across the whole phase is `tests/test_citation_render_gate.py` plus its own
`tests/fixtures/citation_render_gate/` fixture directory (plans 40-01 and 40-05); no other test
module — including `tests/test_desc_break_marker_buffer_swap_gate.py`,
`tests/test_examples_charged_ieee_gate.py`, and `tests/test_corpus_gate.py` — is present in this
diff at all.

---

## 2. The full-corpus `-b typstpdf` gate — ACTUALLY RUN, not skipped

Command: `uv run pytest tests/test_corpus_gate.py -m slow -v`

Verbatim output:

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-aabe067dd6ad4bbdf
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 5 items / 3 deselected / 2 selected

tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED [ 50%]
tests/test_corpus_gate.py::test_empty_url_before_after SKIPPED (SC#3
before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1
to run it (RESEARCH Open Question 1))                                    [100%]

================= 1 passed, 1 skipped, 3 deselected in 13.68s ==================
```

**Plain-words counts:** 2 tests selected by `-m slow`, 1 passed, 1 skipped, 0 failed. 3 further
tests in the same module are deselected (not marked `slow` — they are the fast, non-network
`catalogue_unknown_visit`/`count_empty_url_warnings` unit tests, unaffected).

**Which test is D-14's actual phase gate, and which is not:**

- **`TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error` — EXECUTED, PASSED.** This is
  the GATE-02 real-compile acceptance test: it clones (from the local cache — see below), augments,
  and builds the **entire** Sphinx `v9.1.0` `doc/` tree through `-b typstpdf`, then asserts the
  compiled `sphinx-corpus.pdf` exists, is non-empty, and starts with the `%PDF` magic bytes — never
  relying on `returncode == 0` alone. **This is the test `40-VALIDATION.md`'s D-14 row and D-01's
  non-regression guarantee are about, and it genuinely ran to completion and passed** — not a skip
  standing in for a pass.
- **`test_empty_url_before_after` — SKIPPED, and this is a DIFFERENT test with a DIFFERENT skip
  reason, not D-14's gate.** Its own skip message states the reason verbatim: *"SC#3 before/after
  measurement is env-gated — set `TYPSPHINX_CORPUS_REPORT=1` to run it (RESEARCH Open Question 1)"*.
  Reading `tests/test_corpus_gate.py:507-531` confirms this is an **intentional, by-design** env-var
  gate (`if os.environ.get("TYPSPHINX_CORPUS_REPORT") != "1": pytest.skip(...)`) unrelated to network
  or corpus availability — it exists to avoid doubling the corpus-build time on every `-m slow` run
  and measures a *different* success criterion (SC#3's XREF-01 empty-URL-warning-count reduction,
  Phase 15's concern, not Phase 40's). It was never claimed as D-14's evidence and is recorded here
  only so its skip is not mistaken for the phase gate skipping.

**No network-dependent skip occurred.** The corpus cache is present and matches the installed Sphinx
version:

```
$ ls ~/.cache/typsphinx-corpus-gate/
sphinx-v9.1.0

$ uv run python -c "import sphinx; print(sphinx.__version__)"
9.1.0
```

`get_or_clone_corpus`'s cache-hit path was exercised (a fresh clone was not needed), and the build
proceeded to a real `typst.compile()` call and a real PDF — confirmed by the 13.68 s wall time (a
`pytest.skip` on missing network/corpus would return in well under a second, before any build starts).

**A skip is not a pass, and none was recorded as one here:** the ONE test that is D-14's actual gate
(`test_corpus_compiles_with_no_fatal_error`) reports `PASSED`, in plain text, in the summary line
above (`1 passed`). No paraphrasing was applied.

---

## 3. GREEN flip — `tests/test_citation_render_gate.py` (the phase's own gate module)

**This section supersedes the plan's stale premise.** `40-04-PLAN.md`'s own `<verification>` block
states the module's "assertions are unchanged from the RED recorded in `40-GATE-EVIDENCE-01.md`" —
that was true when the plan was written (before 40-05 existed) and is **no longer literally true**.
Plan 40-05 (which landed after 40-04 was authored, in the same wave sequence) corrected six defective
assertions in this module — two `get_and_resolve_doctree` call sites missing `tags=`, a sentinel
column measurement reading the wrong quantity, a concat sub-check contradicting D-14, an
attached-anchor helper recognising only one of two equivalent Typst label-attachment forms, and an
unsound single-backref regex — all recorded, with full before/after evidence, in
`40-GATE-EVIDENCE-01.md` § 8 (added 2026-08-02). Sections 1–7 of that file (the original RED) are
byte-unchanged; nothing above the amendment line was rewritten.

**What replaces "assertions unchanged" is a stronger, independently-reproduced claim: the corrected
module is 9/9 green against the merged translator and 9/9 RED against `8b22bf6`** (the last commit at
which `typsphinx/translator.py` is byte-identical to the pre-phase translator — confirmed identical to
`ccb37b2`'s translator by 40-01's own GATE-EVIDENCE-01 §7 `git diff --stat` check). Both halves were
reproduced fresh in this plan, per the plan's own instruction, not merely copied from 40-05's summary.

### 3a. GREEN — merged translator

Command: `uv run pytest tests/test_citation_render_gate.py -v`

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-aabe067dd6ad4bbdf
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 9 items

tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_link_citing_site_targets_match_definition_anchors_and_own_ids PASSED [ 11%]
tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_namespace_duplicate_key_is_document_scoped PASSED [ 22%]
tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_separator_paragraph_concat_and_list_item_boundaries PASSED [ 33%]
tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_uncited_entry_renders_plain_label_in_shared_grid PASSED [ 44%]
tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_references_run_and_run_break_grid_counts PASSED [ 55%]
tests/test_citation_render_gate.py::TestCitationRenderGateRealCompile::test_citation_gate_compiles_via_real_typst_compile PASSED [ 66%]
tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_layout_hanging_indent_and_widest_label_alignment PASSED [ 77%]
tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_backref_markers_order_and_pdf_link_geometry PASSED [ 88%]
tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_order_references_sentinels_match_document_order PASSED [100%]

============================== 9 passed in 0.69s ===============================
```

**Selector-by-selector map back to the original `40-GATE-EVIDENCE-01.md` §5 RED table:**

| Selector | § 5 original RED reason | GREEN now | Amended in § 8? |
|---|---|---|---|
| `test_link_citing_site_targets_match_definition_anchors_and_own_ids` (`link`) | No attached anchor (CIT-01/D-13, no handler existed) | PASSED | Yes — § 8.1 (`tags=`) and § 8.4a (`#label(...)` form) |
| `test_namespace_duplicate_key_is_document_scoped` (`namespace`) | No attached `<index:same2020>` anchor | PASSED | No — unaffected by any of the six corrections |
| `test_separator_paragraph_concat_and_list_item_boundaries` (`separator`) | No `grid(` call between References/Run Break | PASSED | Yes — § 8.3 (concat bracket-wrap tolerance) |
| `test_uncited_entry_renders_plain_label_in_shared_grid` (`uncited`) | No `grid(` call between References/Run Break | PASSED | No |
| `test_references_run_and_run_break_grid_counts` (grid-count) | 0 grids found, expected exactly 1 | PASSED | No |
| `test_citation_gate_compiles_via_real_typst_compile` (`compile`) | `TypstError: expected semicolon or line break`, returncode 2 | PASSED | No — the classic RED, flipped purely by 40-03's handlers |
| `test_layout_hanging_indent_and_widest_label_alignment` (`layout`) | PDF not produced (aborted on the classic fatal) | PASSED | Yes — § 8.2 (`_marker_column` fix) |
| `test_backref_markers_order_and_pdf_link_geometry` (`backref`) | No `grid(` call found | PASSED | Yes — § 8.1 (`tags=`) and § 8.4b (marker-fragment scan) |
| `test_order_references_sentinels_match_document_order` (`order`) | PDF not produced | PASSED | No |

Four of nine selectors were touched by 40-05's corrections (`link`, `separator`, `layout`, `backref`);
the other five were already correctly measuring their target property and required no change. Every
correction is against a measured defect in the TEST's own logic (a stale Sphinx keyword, a wrong
column quantity, a contradicted-by-design tolerance, an incomplete anchor-form recognizer, an unsound
regex) — none altered what property the module verifies, and the classic CIT-01 compile RED (the
milestone's sole exception to the structural-RED rule) needed no test-side correction at all.

### 3b. RED re-proof — pre-40-03 translator (`8b22bf6`)

```
$ git checkout 8b22bf6 -- typsphinx/translator.py
$ uv run python -m pytest tests/test_citation_render_gate.py -v
```

Collection and per-test outcome (verbatim):

```
collecting ... collected 9 items
tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_link_citing_site_targets_match_definition_anchors_and_own_ids FAILED [ 11%]
tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_namespace_duplicate_key_is_document_scoped FAILED [ 22%]
tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_separator_paragraph_concat_and_list_item_boundaries FAILED [ 33%]
tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_uncited_entry_renders_plain_label_in_shared_grid FAILED [ 44%]
tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_references_run_and_run_break_grid_counts FAILED [ 55%]
tests/test_citation_render_gate.py::TestCitationRenderGateRealCompile::test_citation_gate_compiles_via_real_typst_compile FAILED [ 66%]
tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_layout_hanging_indent_and_widest_label_alignment FAILED [ 77%]
tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_backref_markers_order_and_pdf_link_geometry FAILED [ 88%]
tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_order_references_sentinels_match_document_order FAILED [100%]

FAILED tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_link_citing_site_targets_match_definition_anchors_and_own_ids - AssertionError: index.typ's Krizhevsky2012 DEFINITION carries no attached anchor <index:krizhevsky2012> yet -- CIT-01/D-13 RED (no citation handler exists to emit it). Attached anchors found: ['index:citation-render-gate', 'index:citing-sites', 'index:concat-protocol', 'index:nested-protocol', 'index:references', 'index:run-break']
FAILED tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_namespace_duplicate_key_is_document_scoped - AssertionError: index.typ's OWN Same2020 definition does not attach <index:same2020> -- CIT-01/D-13 RED (no citation handler exists yet). Found: ['index:citation-render-gate', 'index:citing-sites', 'index:concat-protocol', 'index:nested-protocol', 'index:references', 'index:run-break']
FAILED tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_separator_paragraph_concat_and_list_item_boundaries - AssertionError: No grid( call found between '{text("References")}' and '{text("Run Break")}' -- pre-fix RED: D-05's citation-run grid does not exist yet.
FAILED tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_uncited_entry_renders_plain_label_in_shared_grid - AssertionError: No grid( call found between '{text("References")}' and '{text("Run Break")}' -- pre-fix RED: D-05's citation-run grid does not exist yet.
FAILED tests/test_citation_render_gate.py::TestCitationRenderGateStructural::test_references_run_and_run_break_grid_counts - AssertionError: D-05: the References section's five citation definitions (separated only by a comment, which emits nothing) must land in exactly ONE grid, found 0:
FAILED tests/test_citation_render_gate.py::TestCitationRenderGateRealCompile::test_citation_gate_compiles_via_real_typst_compile - AssertionError: sphinx-build -b typstpdf failed (CIT-01 classic RED): ... TypstError: expected semicolon or line break ... (returncode=2)
FAILED tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_layout_hanging_indent_and_widest_label_alignment - AssertionError: index.pdf was not produced -- typst.compile() aborted pre-fix on the classic CIT-01 compile fatal: ...
FAILED tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_backref_markers_order_and_pdf_link_geometry - AssertionError: No grid( call found between '{text("References")}' and '{text("Run Break")}' -- pre-fix RED: D-05's citation-run grid does not exist yet.
FAILED tests/test_citation_render_gate.py::TestCitationRenderGateCompiledPdf::test_order_references_sentinels_match_document_order - AssertionError: index.pdf was not produced -- typst.compile() aborted pre-fix on the classic CIT-01 compile fatal: ...

============================== 9 failed in 0.51s ===============================
```

Restore:

```
$ git checkout HEAD -- typsphinx/translator.py
$ git status --porcelain
(empty -- no output)
$ git diff HEAD --stat
(empty -- no output)
```

All nine tests fail against the unfixed translator, every failure is a structural `AssertionError` or
the classic build fatal (no Python `TypeError`/`KeyError`/fixture `ERROR` anywhere in the output), and
the temporary substitution left nothing behind after the restore. **The corrected module's ability to
fail was verified, not assumed, independently of 40-05's own re-proof** — this plan reproduced the
whole RED/GREEN pair itself rather than trusting the prior plan's record.

---

## 4. GREEN flip — `tests/test_examples_charged_ieee_gate.py` (shipped samples, CIT-05)

Command: `uv run pytest tests/test_examples_charged_ieee_gate.py -v`

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-aabe067dd6ad4bbdf
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 2 items

tests/test_examples_charged_ieee_gate.py::TestChargedIeeeExamplesGate::test_approach1_package_alone_sample_builds_and_compiles PASSED [ 50%]
tests/test_examples_charged_ieee_gate.py::TestChargedIeeeExamplesGate::test_approach2_custom_template_sample_actually_uses_package PASSED [100%]

============================== 2 passed in 0.69s ===============================
```

**Mapped back to `40-GATE-EVIDENCE-02.md`:** both tests were RED there (§ 2, `2 failed`) on the
FIRST assertion each test method makes (`assert result.returncode == 0`), with the real cause captured
in `stderr` — the two `unknown node type: <citation>`/`<label>` warnings followed by
`TypstError: expected semicolon or line break`. Both now PASS at that same first assertion and
continue through every downstream assertion in the same test methods (the zero-warning helper, the
`paper.typ`/`paper.pdf` existence and non-empty-PDF checks, the package-import/authors-array content
assertions, and — for `approach2` — the shared-template provenance assertions) — none of which
executed on the RED run because pytest halts at the first failing assertion.

**Module provably unedited across the whole phase:**

```
$ git diff --stat ccb37b2..HEAD -- tests/test_examples_charged_ieee_gate.py tests/test_corpus_gate.py
(empty -- no output)
```

The same eleven assertions per test method that were RED in `40-GATE-EVIDENCE-02.md` are what just
passed here — the difference is attributable entirely to the translator change (40-03) and the sample
restoration (40-02), never to a change in what is being checked.

---

## 5. D-14 corpus byte-diff — restated alongside the full-corpus compile gate

Two independent non-regression proofs exist for D-14 (the guarded own-`ids` anchor added to
`visit_reference`/`depart_reference` must not change any non-citation reference's emitted bytes): the
full-corpus **compile** gate re-run for real in § 2 above, and the full-corpus **byte-diff**, produced
during plan 40-03 and restated here (not re-executed by this plan — this plan's own file scope is
`40-NONREGRESSION.md` and, conditionally, one test-comment fix; reproducing a fresh multi-minute
`docs/source` byte-diff build is outside that scope, and 40-03's own record already carries the exact
command and full result):

> `diff -rq -x ".doctrees" -x "*.pickle"` between a `-b typst` build of `docs/source` captured against
> the untouched translator (base commit `8b22bf6`, before 40-03 Task 1) and the same build against the
> final Task 1+2 translator: **one file differs**, `api/index.typ`, and the diff is **purely additive**
> (`1960a1961,2116` — lines ADDED only, nothing removed or changed) — new autodoc entries for the
> three new documented `visit_citation`/`depart_citation`/`visit_label` methods, which
> `sphinx-autodoc-typehints` picks up automatically because they are new PUBLIC methods on
> `TypstTranslator` (docutils' visitor-method naming convention requires this; they cannot be made
> private). No existing byte anywhere in the corpus changed. This is distinct from D-14's actual
> guarantee — no non-citation reference's own emitted link/anchor bytes changed — which the earlier,
> **Task-1-only** diff (fully empty, zero files differing) already proved in isolation, before the
> definition-side handlers (and their new public methods) existed at all.
>
> — `40-03-SUMMARY.md`, "D-14 non-regression: `docs/source` corpus diff"

Read together: the Task-1-only diff (empty) proves D-14's citing-side guard changes nothing for a
non-citation reference; the Task-1+2 diff (one purely-additive autodoc file) proves the definition-side
handlers' only visible effect on the project's own dogfooded corpus is new, correctly-generated
documentation for the new public methods — not a change to any existing rendered content. The
full-corpus **compile** gate in § 2 above is the third, independent, end-to-end confirmation: the same
real corpus that this byte-diff was taken from still compiles clean to a real PDF today.

---

## 6. Milestone invariants, each with its proving command

**Zero new runtime dependencies:**

```
$ git diff --stat ccb37b2..HEAD -- pyproject.toml uv.lock
(empty -- no output)
```

**`@preview` package count stays four, across all three declaration sites, lockstep confirmed:**

```
$ grep -n '@preview/' typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ
typsphinx/writer.py:155:            imports.append('#import "@preview/codly:1.3.0": *')
typsphinx/writer.py:156:            imports.append('#import "@preview/codly-languages:0.1.10": *')
typsphinx/writer.py:157:            imports.append('#import "@preview/mitex:0.2.7": mi, mitex')
typsphinx/writer.py:158:            imports.append('#import "@preview/gentle-clues:1.3.1": *')
typsphinx/templates/base.typ:8:#import "@preview/codly:1.3.0": *
typsphinx/templates/base.typ:9:#import "@preview/codly-languages:0.1.10": *
typsphinx/templates/base.typ:14:#import "@preview/mitex:0.2.7": *
typsphinx/templates/base.typ:19:#import "@preview/gentle-clues:1.3.1": *
typsphinx/template_engine.py:612:            output_parts.append('#import "@preview/codly:1.3.0": *')
typsphinx/template_engine.py:613:            output_parts.append('#import "@preview/codly-languages:0.1.10": *')
typsphinx/template_engine.py:614:            output_parts.append('#import "@preview/mitex:0.2.7": mi, mitex')
typsphinx/template_engine.py:615:            output_parts.append('#import "@preview/gentle-clues:1.3.1": *')
```

Four packages (`codly`, `codly-languages`, `mitex`, `gentle-clues`), identical versions across all
three sites.

```
$ uv run pytest tests/test_preview_version_sync.py -v
============================= test session starts ==============================
collecting ... collected 3 items

tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 33%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [ 66%]
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED [100%]

============================== 3 passed in 0.01s ===============================

$ git diff --stat ccb37b2..HEAD -- tests/test_preview_version_sync.py
(empty -- no output)
```

**Lint/type trio:**

```
$ uv run black --check .
All done! ✨ 🍰 ✨
203 files would be left unchanged.

$ uv run ruff check .
All checks passed!

$ uv run mypy typsphinx/
Success: no issues found in 6 source files
```

**Full suite (slow included):**

```
$ uv run pytest -q
[...]
================== 783 passed, 1 skipped in 71.29s (0:01:11) ===================
```

The 1 skip is the same `test_empty_url_before_after` env-gate from § 2 (SC#3 reporting, not this
phase's gate) — the only skip anywhere in the whole suite, and it is the same skip already explained
and is not this phase's gate. 783 = the 755 passed under `-m "not slow"` (40-05's own tally) plus the
28 slow-marked tests that ran under the unrestricted full run (29 deselected under `-m "not slow"`
minus the 1 that is itself skipped when actually selected).

---

## 7. Closed-out `40-VALIDATION.md` Per-Task Verification Map — all ten rows

`40-VALIDATION.md`'s own frontmatter flags (`wave_0_complete`, `nyquist_compliant`) are owned by
`/gsd-validate-phase`, not by this plan — this table records the evidence each row's command actually
produced; it does not flip those flags.

| # | Requirement | Owning plan/task | Command actually run | Status |
|---|---|---|---|---|
| 1 | CIT-01 (classic GATE-01 RED) | 40-01 (fixture/RED), 40-03 Task 2 (GREEN) | `uv run pytest tests/test_citation_render_gate.py -k compile -x -v` | ✅ green — `4 passed, 5 deselected` |
| 2 | CIT-02 | 40-01 (fixture/RED), 40-03 Task 2 (GREEN), 40-05 Task 2 (assertion repair) | `uv run pytest tests/test_citation_render_gate.py -k layout -x -v` | ✅ green — `1 passed, 8 deselected` |
| 3 | CIT-03 | 40-01 (fixture/RED), 40-03 Task 1+2 (GREEN), 40-05 Task 1 (`tags=` repair) | `uv run pytest tests/test_citation_render_gate.py -k link -x -v` | ✅ green — `2 passed, 7 deselected` |
| 4 | CIT-04 | 40-01 (fixture/RED), 40-03 Task 2 (GREEN), 40-05 Task 1+2 (`tags=` + marker-fragment repair) | `uv run pytest tests/test_citation_render_gate.py -k backref -x -v` | ✅ green — `1 passed, 8 deselected` |
| 5 | CIT-05 | 40-02 (restore/RED), 40-03 (GREEN) | `uv run pytest tests/test_examples_charged_ieee_gate.py -x -v` | ✅ green — `2 passed` (§ 4 above) |
| 6 | CIT-06 | 40-01 (fixture/RED), 40-03 Task 2 (GREEN) | `uv run pytest tests/test_citation_render_gate.py -k order -x -v` | ✅ green — `2 passed, 7 deselected` |
| 7 | D-13 (label namespacing) | 40-01 (fixture/RED), 40-03 Task 2 (GREEN) | `uv run pytest tests/test_citation_render_gate.py -k namespace -x -v` | ✅ green — `1 passed, 8 deselected` |
| 8 | D-14 (citing-site anchor, non-regression) | 40-03 Task 1 (implementation + byte-diff), THIS plan (real full-corpus re-run) | `uv run pytest tests/test_corpus_gate.py -m slow -v` | ✅ green — `test_corpus_compiles_with_no_fatal_error PASSED` (§ 2 above; not a skip) |
| 9 | SC#5 (three separator protocols) | 40-01 (fixture/RED), 40-03 Task 2 (GREEN), 40-05 Task 2 (concat sub-check repair) | `uv run pytest tests/test_citation_render_gate.py -k separator -x -v` | ✅ green — `1 passed, 8 deselected` |
| 10 | D-07 (uncited entry renders) | 40-01 (fixture/RED), 40-03 Task 2 (GREEN) | `uv run pytest tests/test_citation_render_gate.py -k uncited -x -v` | ✅ green — `1 passed, 8 deselected` |

All ten rows carry an executed command (run fresh by this plan, not merely transcribed from an earlier
plan's record) and a real status. All ten are green.

---

## 8. Stale-comment decision (Task 1)

`tests/test_desc_break_marker_buffer_swap_gate.py` is the ONLY file, other than this evidence file,
this plan's `<files_modified>` frontmatter names as a candidate for editing. Re-reading its
`TestDescBreakMarkerBufferSwapCompileGate` class docstring against the now-finished phase:

> "No `TypstCompilationError` may propagate -- milestone invariant #4 requires every
> node-handler-adjacent fixture in this phase to compile successfully both before and after any
> translator edit, since the RED/GREEN split in this phase is structural, never a compile fatal
> (Phase 40's citation work is the sole exception)."

**Conclusion: still accurate, left unmodified.** Checked against both hazards the plan named:

- **Tense:** the sentence is written entirely in the present tense, stating a standing milestone rule
  ("Phase 40's citation work is the sole exception") — it does not say "will be" or "is planned to be"
  the exception, so it never read as future work in the first place.
- **The claim itself:** ROADMAP.md's binding constraint #3 (`.planning/ROADMAP.md` § "Binding
  constraints this roadmap is built on", item 3) states verbatim: *"Phase 40 (citations) is the sole
  exception and keeps the classic `TypstError` RED."* Phase 40 has now shipped exactly that — CIT-01's
  RED (`40-GATE-EVIDENCE-01.md` §§ 1–3) was the classic `TypstError: expected semicolon or line break`
  syntax fatal, confirmed again fresh by this plan in § 3b above — and no other phase in the v0.7.0
  milestone (36, 37, 38, 39, 41) used a classic compile-fatal RED; every one of them defines a
  structural/regex/`pypdf` RED per the milestone's GATE-01 methodology change. "Sole exception" remains
  true as a completed, historical fact about the whole milestone, not a pending one.

No edit was made. `git status --short` and `git diff --stat -- tests/test_desc_break_marker_buffer_swap_gate.py`
are both empty for this plan's commits — an unmodified file is the correct, verified outcome, per the
plan's own instruction that this is a valid result.

`tests/test_corpus_gate.py`'s two `citation` mentions were independently re-derived from source, not
taken on trust from RESEARCH — confirmed at `tests/test_corpus_gate.py:217-227` (the multi-line
`<citation>...</citation>` dump fed to `catalogue_unknown_visit`, a synthetic string built entirely
inline inside `test_catalogue_unknown_visit_multiline`, asserting the warning-PARSER's own line-count
logic — never invoking a real Sphinx build) and `tests/test_corpus_gate.py:503`
(`zero_occurrences = "WARNING: unknown node type: <citation>\n"`, a synthetic zero-occurrence string
fed to `count_empty_url_warnings`, asserting that function returns `0` for input containing no
`Reference node has empty URL` text — again no live build involved). Both are literal Python string
constants defined in the test file itself, not values read from or compared against a live corpus
build's stderr; the live corpus no longer emitting the `unknown node type: <citation>` warning (since
40-03's handlers landed) cannot make either assertion stale, because neither ever depended on the live
corpus emitting it. The module is confirmed unmodified (§ 1 above, absent from the whole-phase `tests/`
diffstat) and needed no change, exactly as `40-VALIDATION.md`'s "Explicitly NOT Wave 0" note predicted.

---

## 9. Executed versus skipped — a skip is not a pass (summary across every command in this file)

| Command | Executed? | Skipped anything? |
|---|---|---|
| `uv run pytest tests/test_corpus_gate.py -m slow -v` | Yes — both selected tests ran | `test_empty_url_before_after` skipped BY DESIGN (env-var gate, unrelated to D-14; § 2) — `test_corpus_compiles_with_no_fatal_error` (the actual D-14 gate) executed and PASSED |
| `uv run pytest tests/test_citation_render_gate.py -v` (merged translator) | Yes — all 9 ran | None |
| `git checkout 8b22bf6 -- typsphinx/translator.py` + `pytest -v` (RED re-proof) | Yes — all 9 ran | None |
| `uv run pytest tests/test_examples_charged_ieee_gate.py -v` | Yes — both ran | None |
| `uv run pytest tests/test_preview_version_sync.py -v` | Yes — all 3 ran | None |
| `uv run pytest -q` (full suite, slow included) | Yes — all 784 collected ran | 1 skipped — the same env-gated `test_empty_url_before_after`, already accounted for above |
| `uv run black --check .` / `ruff check .` / `mypy typsphinx/` | Yes | N/A (not pytest) |
| All ten `40-VALIDATION.md` row commands (§ 7) | Yes — every row's command was run fresh by this plan | None |

**The only skip anywhere in this entire evidence file is `test_empty_url_before_after`, and it is
explained twice (§ 2 and here) as an intentional, by-design env-var gate for a DIFFERENT (Phase 15/
SC#3) concern, never claimed as evidence for D-14 or any Phase 40 requirement.** Every requirement and
every phase gate this plan closes is backed by a test that genuinely ran to a real `PASSED` outcome —
none is a skip standing in for a pass.
