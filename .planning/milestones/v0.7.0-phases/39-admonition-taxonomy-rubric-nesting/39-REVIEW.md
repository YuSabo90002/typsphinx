---
phase: 39-admonition-taxonomy-rubric-nesting
reviewed: 2026-08-02T00:00:00Z
depth: standard
files_reviewed: 23
files_reviewed_list:
  - scripts/render_admonition_greyscale.py
  - tests/fixtures/admonition_greyscale_probe/_templates/minimal.typ
  - tests/fixtures/admonition_greyscale_probe/conf.py
  - tests/fixtures/admonition_greyscale_probe/index.rst
  - tests/fixtures/admonition_locale_title_gate/en/conf.py
  - tests/fixtures/admonition_locale_title_gate/en/index.rst
  - tests/fixtures/admonition_locale_title_gate/ja/conf.py
  - tests/fixtures/admonition_locale_title_gate/ja/index.rst
  - tests/fixtures/admonition_render_gate/index.rst
  - tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
  - tests/fixtures/rubric_indent_invariance_gate/conf.py
  - tests/fixtures/rubric_indent_invariance_gate/index.rst
  - tests/fixtures/rubric_strong_nesting_render_gate/conf.py
  - tests/fixtures/rubric_strong_nesting_render_gate/index.rst
  - tests/test_admonition_bucket_render_gate.py
  - tests/test_admonition_greyscale_pipeline.py
  - tests/test_admonition_locale_title_precedence_gate.py
  - tests/test_admonitions.py
  - tests/test_desc_rubric_decoupling_render_gate.py
  - tests/test_pdf_render_gate.py
  - tests/test_rubric_indent_invariance.py
  - tests/test_rubric_strong_nesting_render_gate.py
  - tests/test_topics.py
  - typsphinx/translator.py
findings:
  critical: 0
  warning: 1
  info: 2
  total: 3
status: issues_found
---

# Phase 39: Code Review Report

**Reviewed:** 2026-08-02T00:00:00Z
**Depth:** standard
**Files Reviewed:** 23
**Status:** issues_found

## Summary

This phase shipped in two tranches: plans 39-01..39-08 (the original
admonition taxonomy/rubric fixes, already reviewed) and plans 39-09..39-13
(gap closure G-39-1, which reverses locked decision D-03 and sub-divides
the red admonition family into three distinct gentle-clues functions —
`error`, `danger`, `memo` — instead of one collapsed `error` bucket). This
review covers the full listed file set at standard depth, concentrating on
the gap-closure delta (`git diff
7272bd6323b67bf48fff598715bca6c04a69ffa8..HEAD`).

**Delta verified directly, not assumed:**

- `typsphinx/translator.py`'s `visit_danger`/`visit_attention` now pass
  `"danger"`/`"memo"` as `clue_type` instead of the folded `"error"`. Traced
  every `_visit_admonition(node, ...)` call site in the file (13 call
  sites, 9 distinct `clue_type` values: `info`, `tip`, `warning`, `error`,
  `danger`, `memo`, `notify`, `abstract`, `task`) against
  `_CLUE_FUNCTION_NAMES` in `tests/test_admonition_bucket_render_gate.py`
  (10 entries, including the never-emitted `clue`) — the recognized-token
  set is complete; no clue-function name the translator can emit is
  missing from the region-scoping regex, so the false-green class the gap
  note warned about (a missing box-open token causing the backward scan in
  `_clue_open_before` to resolve past its own box to a neighbour's token)
  cannot currently occur.
- `#import "@preview/gentle-clues:1.3.1": *` in both
  `typsphinx/templates/base.typ` and the two in-code import-emission sites
  (`writer.py:158`, `template_engine.py:615`) is a wildcard import, so the
  two new function ids (`danger`, `memo`) need no additional import-list
  entry.
- Confirmed against the pinned `gentle-clues` 1.3.1 package actually cached
  on this machine (`~/.cache/typst/packages/preview/gentle-clues/1.3.1/lib/
  {theme,lang}.toml`) that the accent colors, icons, and per-locale default
  titles the test docstrings cite for `danger`/`memo`/`error` are accurate
  (`danger`'s English/Japanese default title, "Danger"/"危険", is indeed
  byte-identical to the Sphinx catalog value in both locales, while
  `memo`'s "Memorize"/"覚える" differs from the catalog's
  "Attention"/"注意" — verified directly against the installed
  `sphinx.locale.admonitionlabels` in both languages, not transcribed from
  the test file).
- `tests/test_admonition_locale_title_precedence_gate.py`'s `_catalog_title`
  helper saves/restores exactly one `sphinx.locale.translators` registry
  entry around a `sphinx.locale.init` call via `try/...finally`, which is
  unconditionally exception-safe (the restore is not gated on the body
  succeeding). Ran the full suite (774 passed, 1 skipped), not just the
  phase's own modules, to confirm this in practice — no cross-module
  locale leak reappeared; English-catalog reads in alphabetically-later
  modules (`test_admonitions.py`, `test_pdf_render_gate.py`) still resolve
  to English after this module's Japanese calls run earlier in the same
  session.
- Ran `ruff check .`, `black --check` (touched files), `mypy typsphinx/`,
  and the full test suite (774 passed, 1 skipped) — all clean.

No BLOCKER-level defects found. One WARNING (an unresolved test-coverage
gap the pre-gap review already flagged, which the gap closure touched but
did not close) and two INFO items, one new to this delta.

## Warnings

### WR-01: The renamed danger/attention unit tests still don't assert the `, title: "..."` argument, even though this delta specifically touched them

**File:** `tests/test_admonitions.py:364-419`
**Issue:** The pre-gap review flagged (as its own WR-01) that
`test_danger_converts_to_error`/`test_attention_converts_to_error` and
their siblings never asserted the `, title: "..."` argument
`_visit_admonition`'s catalog lookup attaches. The gap closure renamed
these two specific tests to `test_danger_converts_to_danger_function` and
`test_attention_converts_to_memo_function` and updated their box-open
assertions (`"danger({"`/`"memo({"` in, `"error({"` out) — but still does
not add a title assertion. This is precisely the pair of tests the
gap-closure plans touched, so the opportunity to close this gap for at
least these two types was present and not taken. Coverage of the title
argument for `danger`/`attention` still lives only in
`tests/test_admonition_bucket_render_gate.py`'s `_CATALOG_TITLE_SENTINELS`
table and `test_red_family_types_route_to_distinct_clue_functions`, and in
`tests/test_admonition_locale_title_precedence_gate.py` — so there is no
production defect today, but a future edit near these two unit tests that
regressed the title argument (e.g. reverting to no title, or
reintroducing unescaped interpolation) would not fail here, only in the
render-gate modules.
**Fix:** Add, to both renamed tests, an assertion like
`assert ', title: "Danger"' in output` /
`assert ', title: "Attention"' in output` (sourcing the expected string
from `str(admonitionlabels["danger"])` / `str(admonitionlabels["attention"])`
rather than a hardcoded literal, to stay consistent with how the
render-gate modules source their expected strings), so a regression fails
close to the unit under test.

## Info

### IN-01: `test_red_family_types_route_to_distinct_clue_functions`'s docstring overstates the fixture's adjacency

**File:** `tests/test_admonition_bucket_render_gate.py:418-431`
**Issue:** The docstring claims the test "[proves] region-scope resolution
stays stable when three equal-family boxes sit adjacent in the fixture."
Checked `tests/fixtures/admonition_render_gate/index.rst`'s actual
directive order: `note, warning, hint, danger, (nested note/warning,
unlabeled), tip, important, caution, seealso, attention, error`. Only two
of the three red-family sentinels (`attention`, `error`) are adjacent;
`danger` sits four sections earlier, separated from the other two by the
nested-admonition block, `tip`, `important`, `caution`, and `seealso`. The
genuinely-adjacent, three-box-in-a-row layout the docstring describes
exists only in `tests/fixtures/admonition_greyscale_probe/index.rst`
(`error, danger, attention`, deliberately adjacent per that fixture's own
comment) — but that fixture is exercised only by
`tests/test_admonition_greyscale_pipeline.py`'s image-rasterization smoke
tests, never by `_clue_open_before`-based region-scoping assertions. So the
specific "three adjacent same-family boxes" robustness property this
docstring claims to prove is not actually exercised by any structural
(string-based) assertion in the suite today. It happens not to matter
currently because the recognized-token set is independently verified
complete (see Summary), but the claim itself is inaccurate and could
mislead a future maintainer into skipping a real adjacency test when
extending the red family further.
**Fix:** Either correct the docstring to describe what is actually tested
(two adjacent + one non-adjacent red-family box, verified individually,
not as a three-in-a-row layout), or add a small synthetic-string case
(mirroring `test_clue_open_before_raises_on_missing_sentinel`'s style,
e.g. `_clue_open_before('error({...ERRSENT...})danger({...DNGSENT...})
memo({...ATTSENT...})', 'ATTSENT')`) that genuinely proves stability under
three-in-a-row adjacency, independent of what order the real fixture
happens to place its sections in.

### IN-02: `render_admonition_greyscale.py`'s `import tempfile` remains deferred to the `__main__` block

**File:** `scripts/render_admonition_greyscale.py:176`
**Issue:** Carried over unchanged from the pre-gap review (previously
IN-01): `import tempfile` is still placed inside `if __name__ == "__main__":`
rather than with the other stdlib imports at the top of the file. This
gap-closure tranche did not touch this script; still purely a style
inconsistency in dev/CI-only tooling, no functional impact.
**Fix:** Move `import tempfile` up to the top-level import block for
consistency with `io`, `subprocess`, `sys`, `pathlib.Path`.

## Notes on the pre-gap review's other findings

- Pre-gap IN-02 (`custom_title: str = None` implicit-`Optional`) is
  unaffected by this delta — still pre-existing, still out of scope, no
  change to report.
- The pre-gap review's WR-01 originally spanned seven unit tests (note,
  warning, tip, caution, hint, error, plus danger/attention). Only the
  danger/attention pair was touched by this gap closure (renamed); the
  other five (note/warning/tip/caution/hint/error) are unchanged by this
  delta and remain exactly as the pre-gap review described them — not
  re-itemized here to avoid duplicating that finding, but still open.

---

_Reviewed: 2026-08-02T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
