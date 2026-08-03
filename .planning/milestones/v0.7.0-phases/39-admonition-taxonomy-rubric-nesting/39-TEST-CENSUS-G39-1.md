# Gap G-39-1 — Exact-String Blast-Radius Census

**Produced:** 2026-08-02, by `39-13-PLAN.md` Task 2, against the finished tree at base commit
`4e3128937416e8cc9b026e5715179adb9c5936e1` (merges plans 39-01 through 39-12, i.e. the tree with
gap G-39-1's routing change and ADM-04 re-take already landed).

**Method:** every count below was produced by running the `git log`/`git diff`/`grep` commands
shown inline, on the checked-out worktree, after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv
sync --extra dev --extra docs` and the `uv`/`ruff` NixOS shims. **This is a re-measurement scoped
to gap G-39-1, not a replacement for `39-TEST-CENSUS.md`.** `39-TEST-CENSUS.md` (produced by plan
39-08 against base `6f891563b835972a9c0179bb7fe1dfb917fb4554`) remains the authoritative record for
the shipped phase's own blast radius; this document reconciles against it row by row in the
"Reconciliation" section below, rather than superseding or re-deriving it wholesale.

The gap's own commit range used throughout this document is `7272bd6..HEAD` — `7272bd6` is the
last commit before this gap's plans began (`docs(39): record G-39-1 gap-closure planning in
STATE.md`), confirmed to be the parent of plan 39-09's first commit.

---

## Census table — files this gap touched

One row per file, using the same columns `39-TEST-CENSUS.md` uses. Roles: **in-process unit**
(constructs a synthetic doctree, no compile), **real-compile `.typ` gate** (`sphinx-build -b typst`
+ string/regex assertions), **compiled-PDF gate** (`-b typstpdf` + `typst.compile()` +
`pypdf`-extracted text), **fixture** (an `index.rst`/`conf.py` under `tests/fixtures/`).

| # | File | Role | Assertions edited | Assertions deliberately untouched | Test functions renamed | Reason for untouched / notes |
|---|---|---|---|---|---|---|
| 1 | `tests/test_admonition_bucket_render_gate.py` | real-compile `.typ` gate | 2 renamed + re-derived (`danger`/`attention` point assertions), 2 new tests added (`test_red_family_types_route_to_distinct_clue_functions`, `test_attention_is_not_in_the_warning_bucket`) | 8 of the 10 pre-gap functions (`test_clue_open_before_raises_on_missing_sentinel`, `test_clue_open_before_raises_when_no_box_precedes_sentinel`, `test_seealso_routes_to_tip_bucket`, `test_generic_admonition_routes_to_notify`, `test_topic_routes_to_abstract`, `test_control_buckets_never_move`, `test_admonition_titles_match_locale_catalog`, `test_no_real_admonition_type_ever_uses_base_clue`) | 2 (`test_danger_routes_to_error_bucket`→`test_danger_routes_to_danger_function`, `test_attention_routes_to_error_bucket`→`test_attention_routes_to_memo_function`) | The other 8 functions assert buckets/behavior this gap does not move (seealso→tip, generic admonition→notify, topic→abstract, the 7 CONTROL types, the catalog-title table, the base-clue absence guard). `memo` was added to the module's `_CLUE_FUNCTION_NAMES` region-scoping set before any assertion was re-targeted (39-09-SUMMARY.md decision). Function count: 10 pre-gap → 12 post-gap (measured: `grep -c '^def test_'` = 10 at `7272bd6`, 12 at HEAD). |
| 2 | `tests/test_admonition_locale_title_precedence_gate.py` | real-compile `.typ` gate + one compiled-PDF case | 9 (all new — this file did not exist before the gap) | n/a (new file) | n/a (new file, 9 functions) | New locale title-precedence gate proving the Sphinx catalog title still beats gentle-clues' own linguify default for both new red-family ids (`danger`, `memo`) in both English and Japanese. Created together with its two-locale fixture project `tests/fixtures/admonition_locale_title_gate/{en,ja}/`. |
| 3 | `tests/test_admonitions.py` | in-process unit | 2 (renamed + re-derived: `test_danger_converts_to_error`→`test_danger_converts_to_danger_function`, `test_attention_converts_to_error`→`test_attention_converts_to_memo_function`) | 16 of 18 pre-gap functions | 2 | The other 16 assertions' admonition type is untouched by this gap (`note`/`warning`/`caution`/`important`/`tip`/`hint`/`seealso`/`error`/generic-admonition all stay on their 39-08-era routing). Function count unchanged at 18 (measured: `grep -c '^    def test_'` = 18 at both `7272bd6` and HEAD). |
| 4 | `tests/test_pdf_render_gate.py` (`TestAdmonitionPdfRenderGate::test_admonitionbuckettitlegate`) | compiled-PDF gate | 0 of the 3 pre-gap assertions edited; 1 new negative assertion added | 3 (the seealso/attention/danger body-sentinel-and-catalog-title assertions) | 0 | The 3 pre-gap assertions are bucket-independent (the catalog `custom_title` always overrides whichever function's own default title would otherwise surface — D-04/D-05), so they needed no migration for this gap; measured directly: 3 `assert` statements in the method body at `7272bd6`, 4 at HEAD (the +1 is the new negative assertion, not an edit to the 3). The new assertion is meaningful only for `attention`/`memo` (gentle-clues' English default `"Memorize"` differs from the catalog's `"Attention"`); no equivalent guard is possible for `danger`, since gentle-clues' own English and Japanese defaults for the `danger` id (`"Danger"`/`"危険"`) are byte-identical to the Sphinx catalog's values for the same locale — documented in the test's own docstring and inline comment, not left implicit. |
| 5 | `tests/fixtures/admonition_render_gate/index.rst` | fixture | 0 sentinels/directives/bodies edited; 2 annotation *comments* corrected | n/a (comment-only) | n/a | Only the danger and attention annotation comments changed, to name G-39-1/D-03-R and state the corrected expected function (`danger`/`memo` instead of the folded `error`) and the corrected DEFECT-CASE description (today emits `error(...)`, not `danger(...)`/`warning(...)`). No directive, sentinel, or body text changed — confirmed via the diff below. |
| 6 | `tests/fixtures/admonition_greyscale_probe/index.rst` | fixture | Extended from 6 to 7 boxes (added a `.. danger::` box); every box's one-line body text reworded from `"This box is the X bucket[, Y type]"` to `"This box is the X directive"` (a wording normalization across all 7 boxes, not a bucket-identity change); one new header comment explaining the seven-box adjacency | n/a | n/a | The three red-family boxes (`error`, `danger`, `attention`) are now deliberately contiguous at the end, per plan 39-12's re-render requirement — adjacency is the point, since G-39-1 asks whether these near-hue title bands separate once desaturated. |

**Reproducible measurement commands for the table above:**

```
$ git log --oneline 7272bd6..HEAD -- tests/test_admonition_bucket_render_gate.py
29f4247 test(39-09): invert red-family bucket assertions, add G-39-1 invariant
# one commit only -- the RED-recording commit. No later commit in this gap touched this
# file again, meaning the RED assertions already targeted the correct final function
# names (danger/memo); the translator fix (39-11) flipped RED->GREEN with zero test edit.

$ grep -c '^def test_' tests/test_admonition_bucket_render_gate.py
12
$ git show 7272bd6:tests/test_admonition_bucket_render_gate.py | grep -c '^def test_'
10

$ git diff -U0 7272bd6..HEAD -- tests/test_admonitions.py | grep '^[-+].*def test_'
-    def test_danger_converts_to_error(self, temp_sphinx_app: SphinxTestApp):
+    def test_danger_converts_to_danger_function(self, temp_sphinx_app: SphinxTestApp):
-    def test_attention_converts_to_error(self, temp_sphinx_app: SphinxTestApp):
+    def test_attention_converts_to_memo_function(self, temp_sphinx_app: SphinxTestApp):

$ grep -c '^    def test_' tests/test_admonitions.py
18
$ git show 7272bd6:tests/test_admonitions.py | grep -c '^    def test_'
18

$ git show 7272bd6:tests/test_pdf_render_gate.py | sed -n '289,365p' | grep -c 'assert '
3
$ sed -n '/def test_admonitionbuckettitlegate/,/^    def test_figure_length/p' tests/test_pdf_render_gate.py | grep -c 'assert '
4

$ git diff 7272bd6..HEAD -- tests/fixtures/admonition_render_gate/index.rst
--- a/tests/fixtures/admonition_render_gate/index.rst
+++ b/tests/fixtures/admonition_render_gate/index.rst
@@ -50,7 +50,7 @@ Hint Type
 Danger Type
 -----------

-.. Requirement ADM-02 (D-03). Expected post-phase gentle-clues function: error. DEFECT CASE -- today emits danger(...).
+.. Requirement ADM-02 (G-39-1, supersedes D-03). Expected function: danger (its own red-family function, not the folded error). DEFECT CASE -- today emits error(...).

 .. danger::

@@ -112,7 +112,7 @@ See Also Type
 Attention Type
 ---------------

-.. Requirement ADM-02 (D-03). Expected post-phase gentle-clues function: error. DEFECT CASE -- today emits warning(...).
+.. Requirement ADM-02 (G-39-1, supersedes D-03). Expected function: memo (its own red-family function, not the folded error). DEFECT CASE -- today emits error(...).

 .. attention::
```

---

## Second table — shipped `39-TEST-CENSUS.md` rows this gap did NOT move

`39-TEST-CENSUS.md` rows 4 through 13 — the rubric modules, the golden file, and the five rubric
fixtures — proven untouched across this gap's whole commit range:

| Shipped-census # | File | Proof this gap did not move it |
|---|---|---|
| 4 | `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` | `git log --oneline 7272bd6..HEAD -- tests/fixtures/desc_rubric_decoupling_render_gate/` → empty |
| 5 | `tests/test_desc_rubric_decoupling_render_gate.py` | `git log --oneline 7272bd6..HEAD -- tests/test_desc_rubric_decoupling_render_gate.py` → empty |
| 6 | `tests/test_rubric_option_concat_render_gate.py` | `git log --oneline 7272bd6..HEAD -- tests/test_rubric_option_concat_render_gate.py` → empty |
| 7 | `tests/test_rubric_propagated_target_render_gate.py` | `git log --oneline 7272bd6..HEAD -- tests/test_rubric_propagated_target_render_gate.py` → empty |
| 8 | `tests/test_signature_typography_multi_signature_page_count_gate.py` | `git log --oneline 7272bd6..HEAD -- tests/test_signature_typography_multi_signature_page_count_gate.py` → empty |
| 9 | `tests/test_translator.py::test_rubric_rendering` | `git log --oneline 7272bd6..HEAD -- tests/test_translator.py` → empty |
| 10 | `tests/fixtures/rubric_option_concat_render_gate/` | `git log --oneline 7272bd6..HEAD -- tests/fixtures/rubric_option_concat_render_gate/` → empty |
| 11 | `tests/fixtures/rubric_propagated_target_render_gate/` | `git log --oneline 7272bd6..HEAD -- tests/fixtures/rubric_propagated_target_render_gate/` → empty |
| 12 | `tests/fixtures/footnote_render_gate/` | `git log --oneline 7272bd6..HEAD -- tests/fixtures/footnote_render_gate/` → empty |
| 13 | `tests/fixtures/signature_typography_gate/` | `git log --oneline 7272bd6..HEAD -- tests/fixtures/signature_typography_gate/` → empty |

**Combined proof, run once over all ten paths together:**

```
$ git log --oneline 7272bd6..HEAD -- tests/test_desc_rubric_decoupling_render_gate.py \
    tests/test_rubric_option_concat_render_gate.py \
    tests/test_rubric_propagated_target_render_gate.py \
    tests/fixtures/desc_rubric_decoupling_render_gate/ \
    tests/test_signature_typography_multi_signature_page_count_gate.py \
    tests/test_translator.py \
    tests/fixtures/rubric_option_concat_render_gate/ \
    tests/fixtures/rubric_propagated_target_render_gate/ \
    tests/fixtures/footnote_render_gate/ \
    tests/fixtures/signature_typography_gate/
(empty -- zero commits touch any of these ten paths across this gap's whole commit range)
```

This is the proof that keeps ADM-05 and Phase 37's golden file demonstrably out of play for this
gap: G-39-1 is a red-family taxonomy sub-division only, and the rubric/signature test surface the
phase already migrated (per `39-TEST-CENSUS.md`) is untouched a second time.

---

## Reproducible measurement command block

```
$ git rev-parse HEAD
4e3128937416e8cc9b026e5715179adb9c5936e1

$ git log --oneline 7272bd6..HEAD -- typsphinx/ tests/ | wc -l
5   # 29f4247 (39-09), 791a4d5 (39-09), 0430d47 (39-11), bf91cbe (39-11), c02d9ec (39-12)

$ git diff --stat 7272bd6..HEAD -- tests/
 .../fixtures/admonition_greyscale_probe/index.rst  |  25 +-
 .../admonition_locale_title_gate/en/conf.py        |  29 ++
 .../admonition_locale_title_gate/en/index.rst      |  33 ++
 .../admonition_locale_title_gate/ja/conf.py        |  31 ++
 .../admonition_locale_title_gate/ja/index.rst      |  34 ++
 tests/fixtures/admonition_render_gate/index.rst    |   4 +-
 tests/test_admonition_bucket_render_gate.py        | 235 +++++++---
 ...test_admonition_locale_title_precedence_gate.py | 471 +++++++++++++++++++++
 tests/test_admonitions.py                          |  27 +-
 tests/test_pdf_render_gate.py                      |  57 ++-
 10 files changed, 861 insertions(+), 85 deletions(-)

$ git diff --stat 7272bd6..HEAD -- typsphinx/
 typsphinx/translator.py | 21 +++++++++++++--------
 1 file changed, 13 insertions(+), 8 deletions(-)
```

---

## The inverted guard

`39-05-SUMMARY.md`'s coverage entry D2 recorded, as evidence for ADM-02, the exact command:

> `grep -vE '^\s*#' typsphinx/translator.py | grep -cE '_visit_admonition\([^)]*"danger"'` **returns
> 0** (danger never passed as clue_type after this plan)

`39-VERIFICATION.md`'s Truth #1 evidence cell repeats the same assertion: *"`grep -c
'_visit_admonition([^)]*"danger"'` returns 0 — `danger` is no longer emitted as a distinct
function."*

**That count is now measured, on the finished tree, as exactly one:**

```
$ grep -vE '^\s*#' typsphinx/translator.py | grep -cE '_visit_admonition\([^)]*"danger"'
1
```

```
$ grep -n '_visit_admonition(node, "danger")\|_visit_admonition(node, "memo")\|_visit_admonition(node, "error")\|_visit_admonition(node, "clue")' typsphinx/translator.py
4530:        self._visit_admonition(node, "error")
4544:        self._visit_admonition(node, "danger")
4559:        self._visit_admonition(node, "memo")
```

`grep -c '"error"' typsphinx/translator.py` (a superset check on the string literal alone, as
tracked in this plan's measured baseline) is now **1**, down from **3** pre-gap (when `visit_danger`
and `visit_attention` both passed `"error"` alongside `visit_error` itself).

**This inversion is the direct, intended consequence of decision D-03-R (`39-CONTEXT.md`, "Reversal
— recorded 2026-08-02 (gap G-39-1)"), which the owner made after a live A/B/C render comparison —
it is NOT a correction of an error in `39-05-SUMMARY.md`.** `39-05-SUMMARY.md`'s zero-count grep was
true when that plan shipped: at that time `visit_danger` and `visit_attention` both routed through
`_visit_admonition(node, "error")`, per the then-locked decision D-03 ("`danger` folds into `error`
too"). The owner subsequently reversed D-03 during conversational UAT (`39-UAT.md` gap G-39-1),
choosing to give `danger` its own gentle-clues `danger` id and `attention` its own `memo` id, leaving
`error` as the sole remaining call site passing `"error"`. **`39-05-SUMMARY.md` itself is
deliberately left unedited** — it is the historical record of what that plan delivered at the time,
and rewriting its recorded grep result to match today's code would erase the evidence that the
routing was reversed by a later, dated owner decision rather than having always been this way.
Confirmed no edit was made:

```
$ git diff --stat -- .planning/phases/39-admonition-taxonomy-rubric-nesting/39-05-SUMMARY.md
(empty)
$ git log --oneline 7272bd6..HEAD -- .planning/phases/39-admonition-taxonomy-rubric-nesting/39-05-SUMMARY.md
(empty)
```

---

## Reconciliation against `39-TEST-CENSUS.md`

**Where this census agrees with `39-TEST-CENSUS.md`:** all ten of the shipped census's rows 4-13
(rubric modules, golden file, rubric fixtures) are confirmed untouched a second time by this gap
(second table above) — full agreement, no drift. The shipped census's row 1
(`tests/test_admonitions.py`) and row 3 (`tests/test_pdf_render_gate.py`) are both files this gap
also touches; this census's rows 3 and 4 above are additive to those shipped rows (further,
different assertions edited on top of the ones `39-TEST-CENSUS.md` already recorded as migrated for
the shipped phase), not a replacement of them — the shipped phase's own 5-of-18 /
0-of-4-plus-1-strengthened tallies still stand for what plans 39-01 through 39-08 changed.

**Where this census necessarily differs:** this gap introduces one wholly new file
(`tests/test_admonition_locale_title_precedence_gate.py`, 9 new tests plus its two-locale fixture
project) that has no corresponding row in `39-TEST-CENSUS.md`, since that file did not exist at the
shipped phase's close. It also touches `tests/test_admonition_bucket_render_gate.py` a second time
(2 renames + 2 new tests, on top of the shipped phase's original 10-function module) and
`tests/fixtures/admonition_greyscale_probe/index.rst` a second time (extended from 6 to 7 boxes, on
top of the shipped phase's original 6-box fixture) — both expected, since G-39-1 sub-divides a
taxonomy the shipped phase had collapsed, and neither file's shipped-phase content is contradicted,
only extended.

**Explicitly stated, per this task's acceptance criteria: no unexplained disagreement was found
anywhere.** Every difference between this census and `39-TEST-CENSUS.md` is accounted for by G-39-1
being a strict superset of new/extended coverage on top of the shipped phase's own migration, never
a correction of it. This re-measurement's own internal counts (10→12 functions in the bucket-gate
module, 18→18 in `test_admonitions.py` with 2 renamed, 3→4 assertions in the PDF gate's
`test_admonitionbuckettitlegate`) match exactly what `39-09-SUMMARY.md` and `39-11-SUMMARY.md`
independently recorded at the time they were written — this is the evidence that those two plans'
own recorded tallies held through to the finished tree, which a plan-time recording alone cannot
supply.
