# Phase 39, Plan 01 — GATE-01 Evidence (Admonition Taxonomy RED)

**Recorded against commit:** `61c0ad9` (`test(39-01): add region-scoped bucket and catalog-title
gate module`), itself built directly on `92c0891` (`docs(phase-39): begin phase execution`), the
phase-start commit. `typsphinx/` is byte-identical between `92c0891` and `61c0ad9` — see
"No source changes" below — so both commits equally qualify as "the untouched translator" this
evidence is recorded against.

This plan touches only `tests/` and `.planning/`. No file under `typsphinx/` is modified.

---

## 1. `tests/test_admonition_bucket_render_gate.py` — verbatim RED

Command: `uv run pytest tests/test_admonition_bucket_render_gate.py -v`

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a34bd95c5b8202d57
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 10 items

tests/test_admonition_bucket_render_gate.py::test_clue_open_before_raises_on_missing_sentinel PASSED [ 10%]
tests/test_admonition_bucket_render_gate.py::test_clue_open_before_raises_when_no_box_precedes_sentinel PASSED [ 20%]
tests/test_admonition_bucket_render_gate.py::test_seealso_routes_to_tip_bucket FAILED [ 30%]
tests/test_admonition_bucket_render_gate.py::test_attention_routes_to_error_bucket FAILED [ 40%]
tests/test_admonition_bucket_render_gate.py::test_danger_routes_to_error_bucket FAILED [ 50%]
tests/test_admonition_bucket_render_gate.py::test_generic_admonition_routes_to_notify FAILED [ 60%]
tests/test_admonition_bucket_render_gate.py::test_topic_routes_to_abstract FAILED [ 70%]
tests/test_admonition_bucket_render_gate.py::test_control_buckets_never_move PASSED [ 80%]
tests/test_admonition_bucket_render_gate.py::test_admonition_titles_match_locale_catalog FAILED [ 90%]
tests/test_admonition_bucket_render_gate.py::test_no_real_admonition_type_ever_uses_base_clue PASSED [100%]

=================================== FAILURES ===================================
______________________ test_seealso_routes_to_tip_bucket _______________________
tests/test_admonition_bucket_render_gate.py:350: in test_seealso_routes_to_tip_bucket
    assert actual == "tip", (
E   AssertionError: D-02 violated: expected seealso's box to open with 'tip' (the success bucket), got 'info'
E   assert 'info' == 'tip'
E
E     - tip
E     + info
____________________ test_attention_routes_to_error_bucket _____________________
tests/test_admonition_bucket_render_gate.py:359: in test_attention_routes_to_error_bucket
    assert actual == "error", (
E   AssertionError: D-03 violated: expected attention's box to open with 'error' (the red bucket), got 'warning'
E   assert 'warning' == 'error'
E
E     - error
E     + warning
______________________ test_danger_routes_to_error_bucket ______________________
tests/test_admonition_bucket_render_gate.py:368: in test_danger_routes_to_error_bucket
    assert actual == "error", (
E   AssertionError: D-03 violated: expected danger's box to open with 'error' (the red bucket is a single function post-phase), got 'danger'
E   assert 'danger' == 'error'
E
E     - error
E     + danger
___________________ test_generic_admonition_routes_to_notify ___________________
tests/test_admonition_bucket_render_gate.py:377: in test_generic_admonition_routes_to_notify
    assert actual == "notify", (
E   AssertionError: D-09 violated: expected the generic admonition's box to open with 'notify', got 'clue'
E   assert 'clue' == 'notify'
E
E     - notify
E     + clue
________________________ test_topic_routes_to_abstract _________________________
tests/test_admonition_bucket_render_gate.py:386: in test_topic_routes_to_abstract
    assert actual == "abstract", (
E   AssertionError: D-10 violated: expected the topic's box to open with 'abstract', got 'clue'
E   assert 'clue' == 'abstract'
E
E     - abstract
E     + clue
_________________ test_admonition_titles_match_locale_catalog __________________
tests/test_admonition_bucket_render_gate.py:474: in test_admonition_titles_match_locale_catalog
    assert not mismatches, "Catalog title mismatch(es):\n" + "\n".join(mismatches)
E   AssertionError: Catalog title mismatch(es):
E     ADMONNOTESENTINEL (note): expected '"Note"', got None
E     ADMONWARNINGSENTINEL (warning): expected '"Warning"', got None
E     ADMONTIPSENTINEL (tip): expected '"Tip"', got None
E     ADMONCAUTIONSENTINEL (caution): expected '"Caution"', got None
E     ADMONSEEALSOSENTINEL (seealso): expected '"See also"', got '"See Also"'
E     ADMONHINTSENTINEL (hint): expected '"Hint"', got None
E     ADMONERRORSENTINEL (error): expected '"Error"', got None
E     ADMONDANGERSENTINEL (danger): expected '"Danger"', got None
E     ADMONATTENTIONSENTINEL (attention): expected '"Attention"', got None
E   assert not [...]

=========================== short test summary info ============================
FAILED tests/test_admonition_bucket_render_gate.py::test_seealso_routes_to_tip_bucket
FAILED tests/test_admonition_bucket_render_gate.py::test_attention_routes_to_error_bucket
FAILED tests/test_admonition_bucket_render_gate.py::test_danger_routes_to_error_bucket
FAILED tests/test_admonition_bucket_render_gate.py::test_generic_admonition_routes_to_notify
FAILED tests/test_admonition_bucket_render_gate.py::test_topic_routes_to_abstract
FAILED tests/test_admonition_bucket_render_gate.py::test_admonition_titles_match_locale_catalog
========================= 6 failed, 4 passed in 0.48s ==========================
```

**Failing-assertion → decision map:**

| Test | Decision | RED reason |
|---|---|---|
| `test_seealso_routes_to_tip_bucket` | D-02 | seealso's box opens `info(` today, must open `tip(` |
| `test_attention_routes_to_error_bucket` | D-03 | attention's box opens `warning(` today, must open `error(` |
| `test_danger_routes_to_error_bucket` | D-03 | danger's box opens `danger(` today (its own function), must open `error(` |
| `test_generic_admonition_routes_to_notify` | D-09 | generic `.. admonition::` opens `clue(` today, must open `notify(` |
| `test_topic_routes_to_abstract` | D-10 | `.. topic::` opens `clue(` today, must open `abstract(` |
| `test_admonition_titles_match_locale_catalog` | D-04/D-05 | 8/10 types emit no title argument at all; `seealso`'s static literal is `"See Also"` vs. the catalog's `"See also"` (casing) |

**GREEN-by-design (must never flip to a DEFECT CASE):**

- `test_control_buckets_never_move` — note→`info`, warning→`warning`, tip→`tip`,
  important→`warning`, caution→`warning`, hint→`tip`, error→`error`. All seven CONTROL types are
  already routed correctly and must stay that way.
- `test_no_real_admonition_type_ever_uses_base_clue` — none of the ten real Sphinx admonition
  types has ever routed through the base `clue` function (that is exclusive to the generic
  admonition/topic paths, tested separately above as D-09/D-10).
- `test_clue_open_before_raises_on_missing_sentinel` / `..._when_no_box_precedes_sentinel` — the
  region-scoping helper's own self-checks, independent of any fixture build.

Every failure above is a structural equality/absence mismatch inside a real, successfully
`sphinx-build -b typst`-compiled `.typ` string — none is a `sphinx-build` non-zero exit and none is
a `typst.compile()` error (confirmed: both session fixtures assert `returncode == 0` and
`index.typ` existence before any bucket/title assertion runs, and no exception aborted collection
or the fixture setup).

---

## 2. `tests/test_pdf_render_gate.py -k AdmonitionPdfRenderGate` — verbatim RED

Command: `uv run pytest tests/test_pdf_render_gate.py -k AdmonitionPdfRenderGate -v --tb=short`

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a34bd95c5b8202d57
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 31 items / 29 deselected / 2 selected

tests/test_pdf_render_gate.py::TestAdmonitionPdfRenderGate::test_admonition_pdf_has_no_literal_source_leak PASSED [ 50%]
tests/test_pdf_render_gate.py::TestAdmonitionPdfRenderGate::test_admonitionbuckettitlegate FAILED [100%]

=================================== FAILURES ===================================
__________ TestAdmonitionPdfRenderGate.test_admonitionbuckettitlegate __________
tests/test_pdf_render_gate.py:328: in test_admonitionbuckettitlegate
    assert expected_title in full_text, (
E   AssertionError: Expected the seealso admonition's catalog title 'See also'
E   (sphinx.locale.admonitionlabels) in extracted PDF text -- D-04/D-05
E   title-source regression
E   assert 'See also' in 'Admonition Render Gate\nTest Author\n1.0.0\n1\n1
E   Contents\n...\n2.9 See Also Type\nSee Also\nADMONSEEALSOSENTINEL This is a
E   seealso admonition.\n...' [full pypdf-extracted text elided here for
E   readability -- reproduce verbatim with the command above]

=========================== short test summary info ============================
FAILED tests/test_pdf_render_gate.py::TestAdmonitionPdfRenderGate::test_admonitionbuckettitlegate
========================= 1 failed, 1 passed, 29 deselected in 0.44s ==========================
```

The extracted PDF text (elided above for length -- reproduce verbatim by running the command)
confirms the pre-fix state directly: the rendered header for the "See Also Type" section reads
literally `See Also` (the pre-phase hardcoded `custom_title="See Also"` literal, wrong casing vs.
the catalog's `"See also"`), and the `Attention Type` / `Danger Type` sections render `Warning` /
`Danger` respectively -- gentle-clues' own linguified default titles for the `warning`/`danger`
functions, not a title argument passed by `_depart_admonition` at all (neither type passes
`custom_title` pre-phase). All three body sentinels (`ADMONSEEALSOSENTINEL`,
`ADMONATTENTIONSENTINEL`, `ADMONDANGERSENTINEL`) ARE present in the extracted text -- the
assertion loop over sentinels (which runs before the title-text loop) did not raise, so the RED is
isolated to the header-text expectations exactly as designed. The pre-existing literal-source-leak
assertion (`test_admonition_pdf_has_no_literal_source_leak`) remains green, unaffected by the
Phase 39 fixture extension.

Selector check: `uv run pytest tests/test_pdf_render_gate.py -k AdmonitionBucketTitleGate
--collect-only -q` selects exactly the one new method
(`TestAdmonitionPdfRenderGate::test_admonitionbuckettitlegate`) -- verified separately, output
below.

```
collected 31 items / 30 deselected / 1 selected
<Dir agent-a34bd95c5b8202d57>
  <Dir tests>
    <Module test_pdf_render_gate.py>
      <Class TestAdmonitionPdfRenderGate>
        <Function test_admonitionbuckettitlegate>
================ 1/31 tests collected (30 deselected) in 0.05s =================
```

---

## 3. RED-versus-CONTROL table

Per 39-CONTEXT.md's locked bucket table (§ "The bucket taxonomy", ADM-01/ADM-02) and § "Admonition
titles" (D-04/D-05):

| Type | Pre-phase function | Post-phase function | Bucket moves? | Pre-phase title | Post-phase title source |
|---|---|---|---|---|---|
| note | `info` | `info` | **CONTROL** | none (gentle-clues default "Info") | `admonitionlabels["note"]` = "Note" |
| warning | `warning` | `warning` | **CONTROL** | none (gentle-clues default "Warning") | `admonitionlabels["warning"]` = "Warning" |
| tip | `tip` | `tip` | **CONTROL** | none (gentle-clues default "Tip") | `admonitionlabels["tip"]` = "Tip" |
| important | `warning` | `warning` | **CONTROL** | `custom_title="Important"` (already matches catalog) | `admonitionlabels["important"]` = "Important" |
| caution | `warning` | `warning` | **CONTROL** | none (gentle-clues default "Warning") | `admonitionlabels["caution"]` = "Caution" |
| hint | `tip` | `tip` | **CONTROL** | none (gentle-clues default "Tip") | `admonitionlabels["hint"]` = "Hint" |
| error | `error` | `error` | **CONTROL** | none (gentle-clues default "Error") | `admonitionlabels["error"]` = "Error" |
| seealso | `info` | `tip` | **DEFECT (D-02)** | `custom_title="See Also"` | `admonitionlabels["seealso"]` = "See also" (casing regression fixed) |
| attention | `warning` | `error` | **DEFECT (D-03)** | none (gentle-clues default "Warning") | `admonitionlabels["attention"]` = "Attention" |
| danger | `danger` | `error` | **DEFECT (D-03)** | none (gentle-clues default "Danger") | `admonitionlabels["danger"]` = "Danger" |
| generic `.. admonition::` | `clue` | `notify` | **DEFECT (D-09)** | node-supplied (unchanged) | node-supplied (unchanged) |
| `.. topic::` | `clue` | `abstract` | **DEFECT (D-10)** | node-supplied (unchanged) | node-supplied (unchanged) |

The seven CONTROL types (note, warning, tip, important, caution, hint, error) are green
pre-phase in every assertion in this module (`test_control_buckets_never_move`,
`test_no_real_admonition_type_ever_uses_base_clue`) and MUST stay green post-phase -- converting
any of them into a defect case anywhere downstream in this phase is itself a regression against
39-CONTEXT.md's locked table, not a fix.

---

## 4. RESEARCH.md blast-radius correction

`.planning/phases/39-admonition-taxonomy-rubric-nesting/39-RESEARCH.md` states in two places
(lines 157 and 634) that "no existing real-compile fixture contains `seealso`, `attention`, or
`danger`" and cites "repo-wide grep of `tests/fixtures/` for `seealso`/`danger`/`attention` finds
zero hits" as the verifying evidence. **This is correct for `seealso` and `attention`, but wrong
for `danger`.**

Repo-wide grep at the phase-start commit `92c0891` (before this plan's own edits), scoped to every
`.rst` fixture under `tests/fixtures/`:

```
$ git grep -n "danger" 92c0891 -- 'tests/fixtures/*.rst' 'tests/fixtures/**/*.rst'
92c0891:tests/fixtures/admonition_render_gate/index.rst:48:.. danger::
92c0891:tests/fixtures/admonition_render_gate/index.rst:50:   This is a danger admonition (D-06 new type).

$ git grep -n "seealso\|attention" 92c0891 -- 'tests/fixtures/*.rst' 'tests/fixtures/**/*.rst'
(no output -- zero hits, confirming RESEARCH.md's claim for these two)
```

`tests/fixtures/admonition_render_gate/index.rst` already carried a `.. danger::` construct
(introduced by the pre-Phase-39 D-06 "new admonition type" work) before this plan touched the
file. This is precisely why Task 1 EXTENDS that existing fixture rather than creating a new one --
the danger construct, its section, and its body text pre-date this phase and are preserved
verbatim (only a sentinel and a routing/CONTROL-vs-DEFECT-CASE comment were added to it).
`seealso` and `attention` remain genuinely absent from every fixture pre-phase, confirmed by the
same grep, and are the two truly NEW constructs Task 1 adds.

---

## 5. No source changes

```
$ git diff --stat -- typsphinx/ 92c0891..HEAD
(empty -- no output)
```

Zero files under `typsphinx/` are touched by this plan's commits (`14c4330`, `61c0ad9`). Every RED
recorded above is against the translator exactly as it stood at the phase-start commit `92c0891`.
