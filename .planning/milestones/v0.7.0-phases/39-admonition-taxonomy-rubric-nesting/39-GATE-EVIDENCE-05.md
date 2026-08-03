# Phase 39, Plan 09 — GATE-01 Evidence (G-39-1 Red-Family Sub-Division RED)

## 1. Gap and reversal

**Gap:** G-39-1, recorded 2026-08-02. By owner decision, after a live A/B/C render comparison,
this gap **reverses locked decision D-03**: the red family stops being one collapsed
`error(...)` function and becomes three pairwise-distinct gentle-clues functions —
`danger(...)`, `memo(...)`, `error(...)` — one per Sphinx admonition type
(`danger`/`attention`/`error`). This is not a defect repair; D-03 was correctly implemented as
written, and the owner changed the requirement after seeing the rendered comparison.

## 2. Base commit

**Recorded against commit:** `7272bd6323b67bf48fff598715bca6c04a69ffa8`

```
$ git log --oneline -1 7272bd6323b67bf48fff598715bca6c04a69ffa8
7272bd6 docs(39): record G-39-1 gap-closure planning in STATE.md
```

This plan's own commits (`29f4247`, `791a4d5`) sit directly on top of this base commit and touch
only `tests/` and `.planning/`. No file under `typsphinx/` is modified — see §7.

---

## 3. `tests/test_admonition_bucket_render_gate.py` — verbatim RED (Task 1)

Command: `uv run pytest tests/test_admonition_bucket_render_gate.py -k "danger_routes or attention_routes or red_family" -q`

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab689e8af16e2b788
configfile: pyproject.toml
plugins: cov-7.1.0
collected 12 items / 9 deselected / 3 selected

tests/test_admonition_bucket_render_gate.py FFF                          [100%]

=================================== FAILURES ===================================
____________________ test_attention_routes_to_memo_function ____________________

admonition_bucket_typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...error-type>]\n\nerror({par({text("ADMONERRORSENTINEL This is an error admonition.")})\n\n}, title: "Error")\n\n\n\n}\n'

    def test_attention_routes_to_memo_function(admonition_bucket_typ_text: str) -> None:
        """G-39-1: attention resolves to its own 'memo' function, superseding
        D-03 -- the red family is three pairwise-distinct gentle-clues functions,
        not one collapsed function."""
        actual = _clue_open_before(admonition_bucket_typ_text, "ADMONATTENTIONSENTINEL")
>       assert actual == "memo", (
            f"G-39-1 violated: expected attention's box to open with 'memo' "
            f"(its own red-family function, superseding D-03's single-function "
            f"fold), got {actual!r}"
        )
E       AssertionError: G-39-1 violated: expected attention's box to open with 'memo' (its own red-family function, superseding D-03's single-function fold), got 'error'
E       assert 'error' == 'memo'
E
E         - memo
E         + error

tests/test_admonition_bucket_render_gate.py:383: AssertionError
____________________ test_danger_routes_to_danger_function _____________________

admonition_bucket_typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...error-type>]\n\nerror({par({text("ADMONERRORSENTINEL This is an error admonition.")})\n\n}, title: "Error")\n\n\n\n}\n'

    def test_danger_routes_to_danger_function(admonition_bucket_typ_text: str) -> None:
        """G-39-1: danger resolves to its own 'danger' function, superseding
        D-03 -- the red family is three pairwise-distinct gentle-clues functions,
        not one collapsed function."""
        actual = _clue_open_before(admonition_bucket_typ_text, "ADMONDANGERSENTINEL")
>       assert actual == "danger", (
            f"G-39-1 violated: expected danger's box to open with 'danger' "
            f"(its own red-family function, superseding D-03's single-function "
            f"fold), got {actual!r}"
        )
E       AssertionError: G-39-1 violated: expected danger's box to open with 'danger' (its own red-family function, superseding D-03's single-function fold), got 'error'
E       assert 'error' == 'danger'
E
E         - danger
E         + error

tests/test_admonition_bucket_render_gate.py:395: AssertionError
____________ test_red_family_types_route_to_distinct_clue_functions ____________

admonition_bucket_typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...error-type>]\n\nerror({par({text("ADMONERRORSENTINEL This is an error admonition.")})\n\n}, title: "Error")\n\n\n\n}\n'

    def test_red_family_types_route_to_distinct_clue_functions(
        admonition_bucket_typ_text: str,
    ) -> None:
        """
        G-39-1: the red family is three pairwise-distinct gentle-clues functions,
        not one collapsed function. Resolves all three red-family sentinels from
        ONE build (proving region-scope resolution stays stable when three
        equal-family boxes sit adjacent in the fixture), then asserts, in order:
        every resolved name is a member of ``_RED_FAMILY_FUNCTIONS``; the three
        names are pairwise distinct; and each of the three boxes carries a title
        argument, via ``_title_arg_after``, equal to the quoted
        ``sphinx.locale.admonitionlabels`` value for that type. RED today: all
        three sentinels resolve to ``error``, so the distinctness assertion
        fails even though the membership assertion (vacuously) does not.
        """
        sentinel_by_type = {
            "attention": "ADMONATTENTIONSENTINEL",
            "danger": "ADMONDANGERSENTINEL",
            "error": "ADMONERRORSENTINEL",
        }
        resolved = {
            node_type: _clue_open_before(admonition_bucket_typ_text, sentinel)
            for node_type, sentinel in sentinel_by_type.items()
        }

        non_members = {
            node_type: fn
            for node_type, fn in resolved.items()
            if fn not in _RED_FAMILY_FUNCTIONS
        }
        assert not non_members, (
            "G-39-1 violated: red-family type(s) resolved to a function outside "
            f"the hand-transcribed red-family set {_RED_FAMILY_FUNCTIONS!r}: "
            f"{non_members}"
        )

        resolved_functions = list(resolved.values())
>       assert len(set(resolved_functions)) == len(resolved_functions), (
            "G-39-1 violated: the red family is not three pairwise-distinct "
            f"gentle-clues functions -- resolved {resolved!r}"
        )
E       AssertionError: G-39-1 violated: the red family is not three pairwise-distinct gentle-clues functions -- resolved {'attention': 'error', 'danger': 'error', 'error': 'error'}
E       assert 1 == 3
E        +  where 1 = len({'error'})
E        +    where {'error'} = set(['error', 'error', 'error'])
E        +  and   3 = len(['error', 'error', 'error'])

tests/test_admonition_bucket_render_gate.py:455: AssertionError
=========================== short test summary info ============================
FAILED tests/test_admonition_bucket_render_gate.py::test_attention_routes_to_memo_function
FAILED tests/test_admonition_bucket_render_gate.py::test_danger_routes_to_danger_function
FAILED tests/test_admonition_bucket_render_gate.py::test_red_family_types_route_to_distinct_clue_functions
======================= 3 failed, 9 deselected in 0.28s ========================
```

### `tests/test_admonition_bucket_render_gate.py` — verbatim CONTROL

Command: `uv run pytest tests/test_admonition_bucket_render_gate.py -k "control_buckets or base_clue or catalog or clue_open_before or not_in_the_warning_bucket or seealso" -q`

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab689e8af16e2b788
configfile: pyproject.toml
plugins: cov-7.1.0
collected 12 items / 5 deselected / 7 selected

tests/test_admonition_bucket_render_gate.py .......                      [100%]

======================= 7 passed, 5 deselected in 0.24s ========================
```

### `--collect-only` (proves strictly more than the pre-task 10)

```
$ uv run pytest tests/test_admonition_bucket_render_gate.py --collect-only -q
collected 12 items

<Dir agent-ab689e8af16e2b788>
  <Dir tests>
    <Module test_admonition_bucket_render_gate.py>
      <Function test_clue_open_before_raises_on_missing_sentinel>
      <Function test_clue_open_before_raises_when_no_box_precedes_sentinel>
      <Function test_seealso_routes_to_tip_bucket>
      <Function test_attention_routes_to_memo_function>
      <Function test_danger_routes_to_danger_function>
      <Function test_red_family_types_route_to_distinct_clue_functions>
      <Function test_attention_is_not_in_the_warning_bucket>
      <Function test_generic_admonition_routes_to_notify>
      <Function test_topic_routes_to_abstract>
      <Function test_control_buckets_never_move>
      <Function test_admonition_titles_match_locale_catalog>
      <Function test_no_real_admonition_type_ever_uses_base_clue>

========================= 12 tests collected in 0.02s ==========================
```

### `_CLUE_OPEN_RE` memo-recognition interpreter check

```
$ uv run python -c "import sys; sys.path.insert(0, 'tests'); from test_admonition_bucket_render_gate import _CLUE_OPEN_RE; m = _CLUE_OPEN_RE.search('memo({'); assert m and m.group(1) == 'memo'; print('memo open token recognized')"
memo open token recognized
```

---

## 4. `tests/test_admonition_locale_title_precedence_gate.py` — verbatim RED (Task 2)

Command: `uv run pytest tests/test_admonition_locale_title_precedence_gate.py -k "opens_with" -q`

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab689e8af16e2b788
configfile: pyproject.toml
plugins: cov-7.1.0
collected 9 items / 5 deselected / 4 selected

tests/test_admonition_locale_title_precedence_gate.py FFFF               [100%]

=================================== FAILURES ===================================
____________________ test_attention_box_opens_with_memo_en _____________________

locale_title_gate_en_typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...rror-type>]\n\nerror({par({text("LOCALEERRORSENTINEL This is an error admonition.")})\n\n}, title: "Error")\n\n\n\n}\n'

    def test_attention_box_opens_with_memo_en(locale_title_gate_en_typ_text: str) -> None:
        """G-39-1: in an English build, the attention box opens with the
        gentle-clues ``memo`` function. RED today: it opens with ``error``."""
        actual = _clue_open_before(locale_title_gate_en_typ_text, "LOCALEATTENTIONSENTINEL")
>       assert actual == "memo", (
            f"G-39-1 violated: expected attention's box to open with 'memo' "
            f"in the English build, got {actual!r}"
        )
E       AssertionError: G-39-1 violated: expected attention's box to open with 'memo' in the English build, got 'error'
E       assert 'error' == 'memo'
E
E         - memo
E         + error

tests/test_admonition_locale_title_precedence_gate.py:296: AssertionError
_____________________ test_danger_box_opens_with_danger_en _____________________

locale_title_gate_en_typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...rror-type>]\n\nerror({par({text("LOCALEERRORSENTINEL This is an error admonition.")})\n\n}, title: "Error")\n\n\n\n}\n'

    def test_danger_box_opens_with_danger_en(locale_title_gate_en_typ_text: str) -> None:
        """G-39-1: in an English build, the danger box opens with the
        gentle-clues ``danger`` function. RED today: it opens with ``error``."""
        actual = _clue_open_before(locale_title_gate_en_typ_text, "LOCALEDANGERSENTINEL")
>       assert actual == "danger", (
            f"G-39-1 violated: expected danger's box to open with 'danger' "
            f"in the English build, got {actual!r}"
        )
E       AssertionError: G-39-1 violated: expected danger's box to open with 'danger' in the English build, got 'error'
E       assert 'error' == 'danger'
E
E         - danger
E         + error

tests/test_admonition_locale_title_precedence_gate.py:306: AssertionError
____________________ test_attention_box_opens_with_memo_ja _____________________

locale_title_gate_ja_typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...:error-type>]\n\nerror({par({text("LOCALEERRORSENTINEL This is an error admonition.")})\n\n}, title: "エラー")\n\n\n\n}\n'

    def test_attention_box_opens_with_memo_ja(locale_title_gate_ja_typ_text: str) -> None:
        """G-39-1: in a Japanese build, the attention box opens with the
        gentle-clues ``memo`` function. RED today: it opens with ``error``."""
        actual = _clue_open_before(locale_title_gate_ja_typ_text, "LOCALEATTENTIONSENTINEL")
>       assert actual == "memo", (
            f"G-39-1 violated: expected attention's box to open with 'memo' "
            f"in the Japanese build, got {actual!r}"
        )
E       AssertionError: G-39-1 violated: expected attention's box to open with 'memo' in the Japanese build, got 'error'
E       assert 'error' == 'memo'
E
E         - memo
E         + error

tests/test_admonition_locale_title_precedence_gate.py:408: AssertionError
_____________________ test_danger_box_opens_with_danger_ja _____________________

locale_title_gate_ja_typ_text = '// Essential package imports\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#impor...:error-type>]\n\nerror({par({text("LOCALEERRORSENTINEL This is an error admonition.")})\n\n}, title: "エラー")\n\n\n\n}\n'

    def test_danger_box_opens_with_danger_ja(locale_title_gate_ja_typ_text: str) -> None:
        """G-39-1: in a Japanese build, the danger box opens with the
        gentle-clues ``danger`` function. RED today: it opens with ``error``."""
        actual = _clue_open_before(locale_title_gate_ja_typ_text, "LOCALEDANGERSENTINEL")
>       assert actual == "danger", (
            f"G-39-1 violated: expected danger's box to open with 'danger' "
            f"in the Japanese build, got {actual!r}"
        )
E       AssertionError: G-39-1 violated: expected danger's box to open with 'danger' in the Japanese build, got 'error'
E       assert 'error' == 'danger'
E
E         - danger
E         + error

tests/test_admonition_locale_title_precedence_gate.py:418: AssertionError
=========================== short test summary info ============================
FAILED tests/test_admonition_locale_title_precedence_gate.py::test_attention_box_opens_with_memo_en
FAILED tests/test_admonition_locale_title_precedence_gate.py::test_danger_box_opens_with_danger_en
FAILED tests/test_admonition_locale_title_precedence_gate.py::test_attention_box_opens_with_memo_ja
FAILED tests/test_admonition_locale_title_precedence_gate.py::test_danger_box_opens_with_danger_ja
======================= 4 failed, 5 deselected in 0.52s ========================
```

### `tests/test_admonition_locale_title_precedence_gate.py` — verbatim CONTROL

Command: `uv run pytest tests/test_admonition_locale_title_precedence_gate.py -k "title_is or title_argument or catalog_title or titles_never" -q`

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ab689e8af16e2b788
configfile: pyproject.toml
plugins: cov-7.1.0
collected 9 items / 4 deselected / 5 selected

tests/test_admonition_locale_title_precedence_gate.py .....              [100%]

======================= 5 passed, 4 deselected in 0.79s ========================
```

**Selector note (discovered during this plan, worth recording so a later reader does not
re-derive it):** the plan's own `<acceptance_criteria>`/`<verify>` text specifies
`-k "title"` as the CONTROL selector for this module. Measured directly: pytest's
`KeywordMatcher` (`_pytest/mark/__init__.py`) matches a `-k` keyword as a case-insensitive
substring against the name of **every node in the item's chain**, including the **Module**
node — whose name is the bare filename `test_admonition_locale_title_precedence_gate.py`.
Because that mandated filename itself contains the substring `"title"`, `-k "title"` matches
**all 9 tests in this module, including the 4 RED box-open tests** — not only the 5
title-source tests the plan intended. Confirmed with `--collect-only`:

```
$ uv run pytest tests/test_admonition_locale_title_precedence_gate.py -k "title" --collect-only -q
collected 9 items
... (all 9 functions listed, including test_attention_box_opens_with_memo_en/_ja and
     test_danger_box_opens_with_danger_en/_ja)
========================== 9 tests collected in 0.05s ==========================
```

Consequently, running the plan's literal `-k "title"` command produces `4 failed, 5 passed`
(the same RED tests fail), not a clean pass. The refined selector above
(`-k "title_is or title_argument or catalog_title or titles_never"`) isolates exactly the 5
title-source CONTROL tests the plan's prose describes, with the same discriminating power
(`"gate"`, `"locale"`, `"precedence"`, and every other filename token exhibit the identical
whole-module-match behaviour — this is a structural property of pytest's Module-node keyword
matching against this plan's own mandated filename, not a defect in the test bodies).

### `--collect-only` (at least 9 tests)

```
$ uv run pytest tests/test_admonition_locale_title_precedence_gate.py --collect-only -q
collected 9 items

<Dir agent-ab689e8af16e2b788>
  <Dir tests>
    <Module test_admonition_locale_title_precedence_gate.py>
      <Function test_attention_box_opens_with_memo_en>
      <Function test_danger_box_opens_with_danger_en>
      <Function test_attention_title_is_catalog_value_en>
      <Function test_danger_title_argument_is_present_en>
      <Function test_attention_pdf_text_carries_catalog_title_not_package_default_en>
      <Function test_attention_box_opens_with_memo_ja>
      <Function test_danger_box_opens_with_danger_ja>
      <Function test_attention_title_is_catalog_value_ja>
      <Function test_package_default_titles_never_appear_in_emitted_source_ja>

========================== 9 tests collected in 0.04s ==========================
```

Both sub-project fixtures build without error (`uv run python -m sphinx -b typst
tests/fixtures/admonition_locale_title_gate/en /tmp/altg-en` and the `ja` equivalent both exit
0, verified separately). The `ja` fixture body is ASCII-only (`str.isascii()` check exits 0).
`en/conf.py` contains zero occurrences of `language`; `ja/conf.py` contains 3 (one in a comment
sentence, one in the actual `language = "ja"` statement, one in a trailing comment) — the two
sub-projects differ only in the locale setting, as required.

---

## 5. RED/CONTROL inventory — every test function this plan added or renamed

| Test | Module | RED/CONTROL | Reason |
|---|---|---|---|
| `test_attention_routes_to_memo_function` | `test_admonition_bucket_render_gate.py` | **RED** | Renamed from `test_attention_routes_to_error_bucket`; now expects `memo`, resolves to `error` today |
| `test_danger_routes_to_danger_function` | `test_admonition_bucket_render_gate.py` | **RED** | Renamed from `test_danger_routes_to_error_bucket`; now expects `danger`, resolves to `error` today |
| `test_red_family_types_route_to_distinct_clue_functions` | `test_admonition_bucket_render_gate.py` | **RED** | New. Distinctness assertion fails: all three red-family sentinels resolve to `error` today |
| `test_attention_is_not_in_the_warning_bucket` | `test_admonition_bucket_render_gate.py` | CONTROL | New. Green both before and after — attention (`error` today, `memo` after) never equals `warning` |
| `test_attention_box_opens_with_memo_en` | `test_admonition_locale_title_precedence_gate.py` | **RED** | New. Expects `memo`, resolves to `error` today (English build) |
| `test_danger_box_opens_with_danger_en` | `test_admonition_locale_title_precedence_gate.py` | **RED** | New. Expects `danger`, resolves to `error` today (English build) |
| `test_attention_title_is_catalog_value_en` | `test_admonition_locale_title_precedence_gate.py` | CONTROL | New. D-04/D-05 catalog-title mechanism already shipped; green regardless of which function boxes attention |
| `test_danger_title_argument_is_present_en` | `test_admonition_locale_title_precedence_gate.py` | CONTROL | New. Presence-only assertion; already green |
| `test_attention_pdf_text_carries_catalog_title_not_package_default_en` | `test_admonition_locale_title_precedence_gate.py` | CONTROL | New. Real-compile discriminating case; green today (attention rides `error`, whose own default "Warning" is also absent), must stay green after routing lands |
| `test_attention_box_opens_with_memo_ja` | `test_admonition_locale_title_precedence_gate.py` | **RED** | New. Expects `memo`, resolves to `error` today (Japanese build) |
| `test_danger_box_opens_with_danger_ja` | `test_admonition_locale_title_precedence_gate.py` | **RED** | New. Expects `danger`, resolves to `error` today (Japanese build) |
| `test_attention_title_is_catalog_value_ja` | `test_admonition_locale_title_precedence_gate.py` | CONTROL | New. Japanese catalog title mechanism already shipped; source-tier only |
| `test_package_default_titles_never_appear_in_emitted_source_ja` | `test_admonition_locale_title_precedence_gate.py` | CONTROL | New. Neither gentle-clues English nor Japanese memo default title ever leaks; source-tier only |

**Unchanged, verified against the new taxonomy and confirmed to need no edit (per Task 1's
instruction to record this positively, not by omission):**

- `_CONTROL_BUCKETS` — never contained `danger` or `attention` (only note/warning/tip/
  important/caution/hint/error), so the red-family sub-division does not touch this table.
- `_CATALOG_TITLE_SENTINELS` — keyed on the `admonitionlabels` catalog key (e.g. `"danger"`,
  `"attention"`), not on the gentle-clues function name, so moving which function boxes a type
  changes nothing about this table's rows or `test_admonition_titles_match_locale_catalog`'s
  logic.
- `_ALL_ADMONITION_FIXTURE_SENTINELS` and `test_no_real_admonition_type_ever_uses_base_clue` —
  neither `danger` nor `memo` is the base `clue` function, so this guard's "not clue" assertion
  is unaffected by which of the three red-family functions a sentinel now resolves to.
- `test_control_buckets_never_move` — its own table (`_CONTROL_BUCKETS`) is unaffected, so the
  test body needed no change.
- Both `_clue_open_before` self-checks — pure unit tests against literal strings, independent of
  any fixture build or taxonomy.

---

## 6. Measured `lang.toml` correction (planner's `measured_context` correction, confirmed)

File: `~/.cache/typst/packages/preview/gentle-clues/1.3.1/lib/lang.toml`

```
[lang.ja]
...
memo = "覚える"
...
danger = "危険"
```

**This CONFIRMS the 39-09-PLAN.md `<planner_measurement_correction>`, and CONTRADICTS
39-UAT.md's original `measured_context` bullet** ("memo = \"Memorize\" in en, no `ja` entry →
falls back to en"). The `[lang.ja]` table DOES carry an explicit `memo` entry
(`"覚える"`) — there is no fallback to English for the Japanese `memo` id. Every other part of
that 39-UAT.md bullet holds: `danger` is `"Danger"` in `[lang.en]` and `"危険"` in `[lang.ja]`.
Consequence, carried into Task 2: the Japanese negative assertion
(`test_package_default_titles_never_appear_in_emitted_source_ja`) covers BOTH gentle-clues'
English memo default (`"Memorize"`) AND its Japanese memo default (`"覚える"`), never narrowed
to the English string on the strength of the (incorrect) 39-UAT.md text.

---

## 7. Measured `theme.typ` provenance (red-family constant, NOT test data)

File: `~/.cache/typst/packages/preview/gentle-clues/1.3.1/lib/theme.typ`

| id | accent-color | icon |
|---|---|---|
| `error` | `rgb(210, 15, 57)` — `#d20f39` (red) | `crossmark.svg` |
| `danger` | `rgb(254, 100, 11)` — `#fe640b` (peach) | `danger.svg` |
| `memo` | `rgb(230, 69, 83)` — `#e64553` (maroon) | `excl.svg` |

These three values are recorded as an inline comment alongside `_RED_FAMILY_FUNCTIONS` in
`tests/test_admonition_bucket_render_gate.py` — explicitly labelled provenance, never asserted
against as test data (D-01: a bucket is a function name, never a colour argument).

---

## 8. No source changes

```
$ git diff --stat 7272bd6323b67bf48fff598715bca6c04a69ffa8..HEAD -- typsphinx/
(empty -- no output)

$ git diff --stat 7272bd6323b67bf48fff598715bca6c04a69ffa8..HEAD
 .../admonition_locale_title_gate/en/conf.py        |  29 ++
 .../admonition_locale_title_gate/en/index.rst      |  33 ++
 .../admonition_locale_title_gate/ja/conf.py        |  31 ++
 .../admonition_locale_title_gate/ja/index.rst      |  34 ++
 tests/fixtures/admonition_render_gate/index.rst    |   4 +-
 tests/test_admonition_bucket_render_gate.py        | 235 +++++++---
 .../test_admonition_locale_title_precedence_gate.py| 471 +++++++++++++++++++++
 7 files changed, 783 insertions(+), 54 deletions(-)
```

Zero files under `typsphinx/` are touched by this plan's commits (`29f4247`, `791a4d5`). Every
RED recorded above is against the translator exactly as it stood at the base commit
`7272bd6323b67bf48fff598715bca6c04a69ffa8`.

---

## 9. Test-isolation fix discovered during this plan (documented for transparency)

An early version of `_catalog_title()` in `test_admonition_locale_title_precedence_gate.py`
called `sphinx.locale.init(..., "ja")` to resolve the Japanese catalog value but never restored
the prior translator afterward. Because this test process never runs a real Sphinx
`Application` (every build in this module is a `sphinx-build` subprocess, which scopes its own
translator to its own process), the Japanese translator leaked process-wide and was picked up by
alphabetically-later modules in the same pytest session — `tests/test_admonitions.py`'s English
title assertions (`test_important_converts_to_warning_with_title`,
`test_seealso_converts_to_tip_with_title`) started asserting Japanese strings and failed. Fixed
before committing by saving and restoring the `sphinx.locale.translators[("general", "sphinx")]`
registry entry around each catalog read; the full suite (`uv run pytest -m "not slow" -q`) was
re-run afterward and confirmed clean except for the 7 RED tests this plan intentionally records
(3 in `test_admonition_bucket_render_gate.py`, 4 in
`test_admonition_locale_title_precedence_gate.py`) — `739 passed, 7 failed, 29 deselected`.
