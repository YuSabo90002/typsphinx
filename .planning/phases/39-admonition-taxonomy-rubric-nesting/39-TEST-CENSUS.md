# Phase 39 — SC#5 Test Census

**Produced:** 2026-08-02, by `39-08-PLAN.md` Task 1, against the finished tree (base commit
`6f891563b835972a9c0179bb7fe1dfb917fb4554`, which merges 39-01 through 39-07).
**Method:** every count below was produced by running the greps and `git log`/`git diff` commands
shown inline, on the checked-out worktree, after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv
sync --extra dev` and the `uv`/`ruff` NixOS shims. This is a re-measurement, not a transcription of
`39-CONTEXT.md` D-14's discussion-time table or `39-RESEARCH.md`'s planning-time re-take — see
"Reconciliation" below for where the three censuses agree and where they were checked against each
other.

---

## Census table

One row per file. Roles: **in-process unit** (constructs a synthetic doctree, no compile), **real-
compile `.typ` gate** (`sphinx-build -b typst` + string/regex assertions), **compiled-PDF gate**
(`-b typstpdf` + `typst.compile()` + `pypdf`-extracted text), **fixture** (an `index.rst`/`golden.typ`
under `tests/fixtures/`), **golden** (a committed exact-byte artifact consumed by a byte-identity
assertion).

| # | File | Role | Assertions edited | Assertions deliberately untouched | Test functions renamed | Reason for untouched |
|---|---|---|---|---|---|---|
| 1 | `tests/test_admonitions.py` | in-process unit | 5 (across 4 functions) | 13 (of the 18 pre-phase clue-call assertions) | 4 | The other 13 assertions' admonition type does not change bucket (`note`→`info`, `warning`/`caution`/`important`→`warning`, `tip`/`hint`→`tip`, `error`→`error` all stay put), and where a title is checked (`important`'s `', title: "Important"'`) the English catalog value is byte-identical to the pre-phase hardcoded literal, so the string survives unedited. |
| 2 | `tests/test_topics.py` | in-process unit | 2 | 1 | 0 | The untouched assertion (`assert "clue({" not in output`) guards the box-less `.. contents::` path, which D-10 does not touch — only the non-contents `.. topic::` branch is re-routed to `abstract(`. |
| 3 | `tests/test_pdf_render_gate.py` (`TestAdmonitionPdfRenderGate::test_admonitiontitleregression_multichild`) | compiled-PDF gate | 0 | 4 | 0 | All four assertions check body sentinels (`ADMONITIONNOTESENTINEL`/`ADMONITIONWARNINGSENTINEL`/`ADMONITIONCUSTOMSENTINEL`) or a directive-supplied title (`"Custom Title"`), none of which are catalog defaults or bucket-dependent; `note`/`warning`/generic-`admonition` also don't change bucket. This file's own class (`TestAdmonitionPdfRenderGate`) gained a *new*, additive test method (`test_admonitionbuckettitlegate`, wave 1 / plan 39-01) and a shared class-scoped compile fixture — both additions, not edits to this row's four pre-existing assertions. |
| 4 | `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` | golden | 1 region (2 lines removed) | n/a (whole-file byte-identity gate; only the named region changed) | n/a | The only changed region is the "rubric carrying a propagated target inside a list item" section: two blank lines removed between the anchor's `]` and the rubric's `strong({` open, per D-11's separator-double-count fix (39-06 commit `d5205d4`). Every other section (top-level end-of-document rubric, markup-free "Options" rubric, both signature blocks, the plain-bold control paragraph) is byte-identical. |
| 5 | `tests/test_desc_rubric_decoupling_render_gate.py` | real-compile `.typ` gate | 0 | 5 (all pass) | 0 | Pre-existing since Phase 36 (SC#1/SC#2) plus the D-11 wart assertion plan 39-02 added as a new RED (`test_propagated_target_rubric_separator_run_is_not_yet_one`) — a new test function, not an edited pre-existing string, so it is not a Bucket-A-style migration row. Confirmed green post-fix (39-06). |
| 6 | `tests/test_rubric_option_concat_render_gate.py` | compiled-PDF gate | 0 | 2 (all pass) | 0 | Confirmed-green, untouched (`git log 8a37226..HEAD` shows zero commits touching this file). Its two rubrics (the autodoc "Options" heading and the true end-of-document rubric) are neither nested-with-`strong` nor list-item+propagated-target, so neither D-11 nor D-13 reaches them. |
| 7 | `tests/test_rubric_propagated_target_render_gate.py` | compiled-PDF gate | 0 | 1 (passes) | 0 | Confirmed-green, untouched. Its propagated-target rubric is a top-level rubric, not inside a list item, so D-11's double-count guard (which only fires for the list-item case) has no effect on its byte shape; it asserts PDF/link resolution, not an exact newline count. |
| 8 | `tests/test_signature_typography_multi_signature_page_count_gate.py` | compiled-PDF gate | 0 | 1 (passes) | 0 | Confirmed-green, untouched. Only *references* `desc_rubric_decoupling_render_gate/golden.typ` in a comment; carries no rubric content of its own. |
| 9 | `tests/test_translator.py::test_rubric_rendering` | in-process unit | 0 | 1 (passes) | 0 | Confirmed-green, untouched. A tautological `'strong({text("Methods")]' in output or "Methods" in output` assertion — practically unfalsifiable by this phase's changes regardless of fix. |
| 10 | `tests/fixtures/rubric_option_concat_render_gate/` | fixture | 0 | n/a | n/a | Untouched (`git log` shows zero commits). |
| 11 | `tests/fixtures/rubric_propagated_target_render_gate/` | fixture | 0 | n/a | n/a | Untouched. |
| 12 | `tests/fixtures/footnote_render_gate/` | fixture | 0 | n/a | n/a | Untouched. Contains a `.. rubric:: Footnotes` (line 36) but no `strong`-nested markup and not inside a list item, so neither D-11 nor D-13 reaches it — confirmed via `git log 8a37226..HEAD -- tests/fixtures/footnote_render_gate/` (no output) and a live `grep -rn rubric` on the fixture. |
| 13 | `tests/fixtures/signature_typography_gate/` | fixture | 0 | n/a | n/a | Untouched. |

**New GATE-01 fixture files (wave 1, plans 39-01/39-02 — not part of D-14's original 3-file
exact-string blast radius, listed here for completeness since this census's reconciliation section
below references them):** `tests/test_admonition_bucket_render_gate.py` (10 tests, all pass — the
phase's classic bucket/catalog-title REDs, flipped GREEN by 39-05), `tests/test_rubric_strong_nesting_render_gate.py`
(6 tests, all pass — D-13's classic `par()`-drop RED, flipped GREEN by 39-06),
`tests/test_rubric_indent_invariance.py` (7 tests, all pass — ADM-05's own D-12 invariance guard,
never RED since the property already held pre-phase).

---

## Reproducible measurement commands

```
$ grep -c '"info({" in output\|"tip({" in output\|"warning({" in output\|"error({" in output\|"notify({" in output\|"clue({" in output' tests/test_admonitions.py
19   # post-phase (18 pre-phase + 1 new precedence-test assertion, see below)

$ git show 8406b8a:tests/test_admonitions.py | grep -c '"info({"\|"tip({"\|"warning({"\|"error({"\|"danger({"\|"clue({"\|"notify({"'
18   # pre-phase baseline (8406b8a = "docs(38): transition ... advance to Phase 39")

$ grep -n "    def test_" tests/test_admonitions.py | wc -l
18   # post-phase function count (17 pre-phase + 1 new: test_note_with_own_title_wins_over_catalog)

$ grep -n "clue({\|abstract({\|clue\[" tests/test_topics.py
60:        assert "abstract({" in output
91:        assert "abstract({" in output
138-140: (comment + ) assert "clue({" not in output   # untouched, box-less .. contents:: control

$ git diff --stat 8406b8a..HEAD -- tests/test_admonitions.py tests/test_topics.py tests/test_pdf_render_gate.py
 tests/test_admonitions.py     |  88 +++++++++++++++-----
 tests/test_pdf_render_gate.py | 185 ++++++++++++++++++++++++++++++------------
 tests/test_topics.py          |  18 ++--
 3 files changed, 214 insertions(+), 77 deletions(-)

$ git diff 8406b8a..HEAD -- tests/test_pdf_render_gate.py | grep -c "ADMONITIONNOTESENTINEL\|ADMONITIONWARNINGSENTINEL\|ADMONITIONCUSTOMSENTINEL\|Custom Title"
0   # confirms the 4 admonition-title-regression assertions were never touched;
    # the 185-line diff is entirely the new class-scoped compile fixture +
    # the additive test_admonitionbuckettitlegate method (wave 1, plan 39-01)

$ git diff 8a37226..HEAD -- tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
@@ -73,8 +73,6 @@ text("First bullet text.")
 [#metadata(none) <index:decoupling-rubric-in-list-target>]
-
-
 strong({text("A Rubric In A List Item")})

$ git log --oneline 8a37226..HEAD -- tests/test_rubric_option_concat_render_gate.py \
    tests/test_rubric_propagated_target_render_gate.py \
    tests/test_signature_typography_multi_signature_page_count_gate.py \
    tests/test_translator.py \
    tests/fixtures/rubric_option_concat_render_gate/ \
    tests/fixtures/rubric_propagated_target_render_gate/ \
    tests/fixtures/footnote_render_gate/ \
    tests/fixtures/signature_typography_gate/
(empty — zero commits touch any of these eight paths across the whole phase)

$ grep -rn "rubric" tests/fixtures/footnote_render_gate/
tests/fixtures/footnote_render_gate/index.rst:36:.. rubric:: Footnotes

$ grep -rln "^\.\. topic::\|^\.\. admonition::" tests/fixtures/*/index.rst
tests/fixtures/topic_line_block_render_gate/index.rst

$ grep -rln "^\.\. danger::\|^\.\. attention::\|^\.\. seealso::" tests/fixtures/*/index.rst
tests/fixtures/admonition_greyscale_probe/index.rst
tests/fixtures/admonition_render_gate/index.rst
```

---

## Accepted regressions (D-05) — measured live, not recalled

Three measured changes D-05 explicitly accepted as designed, not bugs, so a future reader who spots
them in a diff does not open a defect:

1. **Japanese `.. note::` title regresses from gentle-clues' 「情報」 to the
   `sphinx.locale.admonitionlabels` catalog's 「注釈」.** Measured live this session:

   ```
   $ uv run python3 -c "
   import sphinx, os
   locale_dir = os.path.join(os.path.dirname(sphinx.__file__), 'locale')
   import sphinx.locale as sl
   sl.init([locale_dir], 'ja')
   print('note:', sl.admonitionlabels['note'])
   print('tip:', sl.admonitionlabels['tip'])
   "
   note: 注釈
   tip: Tip
   ```

2. **Japanese `.. tip::` title regresses from gentle-clues' 「ヒント」 to the catalog's
   untranslated English `"Tip"`** — same live measurement above; the `ja` catalog does not carry a
   translation for the `tip` key.

3. **`seealso`'s English title casing changes from `"See Also"` to the catalog's `"See also"`**
   (lowercase `a`) — visible directly in `tests/test_admonitions.py:155`,
   `assert ', title: "See also"' in output`.

All three are consequences of D-04/D-05's single decision (route every real admonition type's
static title through one `sphinx.locale.admonitionlabels` lookup, applied uniformly rather than
type-by-type), not independent defects.

---

## Reconciliation against the discussion-time and planning-time censuses

**`39-CONTEXT.md` D-14 (discussion-time, raw counts):** "18 clue-call assertions in
`test_admonitions.py`, 3 in `test_topics.py`, 4 in `test_pdf_render_gate.py`, plus the five named
rubric-touching modules and five fixtures." **Matched exactly** against this census's pre-phase
baseline measurement (`git show 8406b8a:tests/test_admonitions.py` → 18; `test_topics.py` → 3 total,
confirmed by the three line numbers in the reproducible-commands section above; `test_pdf_render_gate.py`
→ 4, the `test_admonitiontitleregression_multichild` assertions). No disagreement.

**`39-RESEARCH.md` "Blast-Radius Re-Take" (planning-time, refined):** predicted **5 of the 18**
`test_admonitions.py` assertions actually go RED, across **4** functions (`test_seealso_*` — 2
assertions, `test_danger_*` — 1, `test_attention_*` — 1, `test_generic_admonition_*` — 1); **2 of the
3** `test_topics.py` assertions go RED (lines 59, 90 in the finished tree — the two normal-topic
`"clue({"` checks); the box-less-contents negative assertion (then line 134, now line 138-140)
unaffected; **0 of the 4** `test_pdf_render_gate.py` assertions need to change, but flagged that the
`.typ`-string half of ADM-03's compiled-PDF fixture (a `notify(` assertion) was missing and would
need adding. **This census's finished-tree measurement matches every one of these predictions
exactly** — see the census table above (row 1: 5 edited/4 renamed; row 2: 2 edited/1 untouched/0
renamed; row 3: 0 edited/4 untouched). The one caveat: the missing `notify(` assertion RESEARCH
flagged landed not in `test_pdf_render_gate.py` itself but in the *new* GATE-01 fixture module
`tests/test_admonition_bucket_render_gate.py` (`test_generic_admonition_routes_to_notify`, created
by plan 39-01 as part of the phase's classic RED-then-GREEN gate) — a different file achieving the
same coverage RESEARCH asked for, not a disagreement about whether the coverage exists.

**Rubric-touching modules and fixtures:** RESEARCH predicted `test_desc_rubric_decoupling_render_gate.py`'s
`golden.typ` WOULD change (confirmed — row 4 above) and that the other four modules
(`test_rubric_option_concat_render_gate.py`, `test_rubric_propagated_target_render_gate.py`,
`test_signature_typography_multi_signature_page_count_gate.py`, `test_translator.py::test_rubric_rendering`)
and all fixtures except the decoupling one would stay unaffected. **Matched exactly** — confirmed by
`git log`/`git diff` showing zero commits touching any of those eight paths across the whole phase
(reproducible-commands section above).

**Explicitly stated, per this task's acceptance criteria: every count in this census matches both the
discussion-time raw counts and the planning-time refined predictions.** No disagreement was found in
either direction. This is itself a finding worth recording — a re-measurement that confirms an
earlier prediction is not redundant with that prediction; it is the evidence that the prediction held
through implementation, which a prediction alone cannot supply.

---

## Cross-check against 39-05-SUMMARY.md and 39-06-SUMMARY.md

- **39-05-SUMMARY.md** records: *"Migrated exactly four falsified test functions in
  `tests/test_admonitions.py` (renamed + re-derived: seealso, danger, attention, generic admonition)
  ... left the other 13 original assertions byte-unchanged. Added one new test locking the
  directive-title-wins-over-catalog precedence property"* and *"Migrated the two falsified assertions
  in `tests/test_topics.py` (clue->abstract) without renaming their functions ... Left the box-less
  `.. contents::` assertion byte-unchanged."* **Matches this census's row 1 and row 2 exactly**
  (4 functions renamed / 5 assertions edited / 13 untouched for `test_admonitions.py`; 2 edited / 1
  untouched / 0 renamed for `test_topics.py`).
- **39-05-SUMMARY.md**'s own "Next Phase Readiness" section pre-computed the same tallies this census
  independently re-derived: *"`tests/test_admonitions.py` (4 renamed, 1 added, 13 untouched of 17
  original) and `tests/test_topics.py` (2 moved, 1 untouched, 0 renamed)"* — the "17 original" there
  counts test *functions* (17 pre-phase + 1 new = 18 post-phase), not assertions (18 pre-phase clue
  calls, of which 5 across 4 functions were edited); both metrics agree with this census once the
  functions-vs-assertions distinction is made explicit, which this census does in its own column
  headers to avoid the ambiguity.
- **39-06-SUMMARY.md** records the golden-file diff verbatim (reproduced identically in row 4 above)
  and its own D-14 rubric census table, both of which this census's rows 4-13 reconcile against
  without disagreement — every module/fixture 39-06 marked "confirmed-green" or "confirmed" is
  confirmed-green again here, independently re-measured rather than copied.

**No disagreement found anywhere.** All counts in this census agree with 39-05-SUMMARY.md and
39-06-SUMMARY.md's own recorded tallies.
