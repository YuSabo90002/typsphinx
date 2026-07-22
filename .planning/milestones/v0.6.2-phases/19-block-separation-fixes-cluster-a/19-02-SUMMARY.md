---
phase: 19-block-separation-fixes-cluster-a
plan: 02
subsystem: translator
tags: [typst-codegen, block-separation, render-gate, tdd]
dependency-graph:
  requires:
    - "TypstTranslator._emit_forced_break(break_token) shared helper (Plan 01)"
  provides:
    - "FID-03 fix: linebreak() between sibling desc_signatures (overloads/alias groups/multi-option directives)"
    - "FID-04 fix: linebreak() between a rubric option-group heading and the following option/field"
  affects:
    - "Plan 03 (FID-05 -- does NOT use the shared helper, per Pitfall 3; independent of this plan's two fixes)"
tech-stack:
  added: []
  patterns:
    - "FID-03: new per-desc scalar flag self._is_first_desc_signature (reset in visit_desc), checked in visit_desc_signature BEFORE creating the dummy strong node"
    - "FID-04: depart_rubric emits an explicit leading \"\\n\" before calling _emit_forced_break, because depart_strong's closing \"})\" carries no trailing separator of its own (unlike depart_desc_signature's unconditional trailing \"\\n\", which is what makes FID-03's placement safe without one)"
key-files:
  created:
    - tests/fixtures/desc_signature_siblings_render_gate/conf.py
    - tests/fixtures/desc_signature_siblings_render_gate/index.rst
    - tests/test_rubric_option_concat_render_gate.py
    - tests/fixtures/rubric_option_concat_render_gate/conf.py
    - tests/fixtures/rubric_option_concat_render_gate/index.rst
  modified:
    - typsphinx/translator.py
    - tests/test_desc_signature_concat_render_gate.py
    - tests/test_translator.py
decisions:
  - "FID-03's _is_first_desc_signature is a plain scalar (not a stack), mirroring the existing per-desc_signature _is_first_desc_signature_line precedent -- safe because a desc's own desc_signature children are always fully processed (doctree order) before its desc_content (which may hold nested desc children) is entered."
  - "FID-04 required an EXTRA leading \"\\n\" before _emit_forced_break that RESEARCH's proposed snippet did not include -- discovered via a real compile failure (\"expected semicolon or line break\") this session when calling the helper immediately after depart_strong with no intervening separator. This is a leading-boundary instance of the same class of bug Pitfall 1 documents for the trailing boundary; FID-03 avoided it only because depart_desc_signature already supplies an unconditional trailing \"\\n\" before the next desc_signature's leading linebreak() fires."
  - "Updated the pre-existing tests/test_translator.py::test_desc_signature_line_resets_per_signature unit test, whose old assertion (\"no linebreak() at all between two sibling desc_signatures\") encoded the FID-03 bug as expected behavior. Now asserts exactly ONE linebreak() (the FID-03 sibling separator), which still proves the original intent (the per-line flag resets correctly, contributing zero ADDITIONAL linebreak()s for two single-line signatures)."
metrics:
  duration: "~50m"
  completed: "2026-07-20"
status: complete
---

# Phase 19 Plan 02: Block Separation Fixes — FID-03 + FID-04 Summary

Landed the two remaining `linebreak()` (stacked-line) fixes on top of Plan 01's shared
`_emit_forced_break` helper: sibling `desc_signature`s (FID-03) and the rubric option-group
heading (FID-04). Both are proven RED pre-fix / GREEN post-fix via real-compile GATE-01
render-gate fixtures.

## What Was Built

- **FID-03** (`visit_desc`/`visit_desc_signature`, `typsphinx/translator.py`): a new per-`desc`
  scalar flag `self._is_first_desc_signature` is reset `True` in `visit_desc`. In
  `visit_desc_signature`, before creating the dummy `strong` node, `self._emit_forced_break("linebreak()")`
  fires when `not self._is_first_desc_signature`, then the flag is set `False`. Multiple sibling
  signatures (overloads / alias groups / multi-option directives) now stack on separate lines;
  a `desc` with a single signature emits zero extra bytes (byte-for-byte unchanged).
- **FID-04** (`depart_rubric`, `typsphinx/translator.py`): the cosmetic-only trailing
  `self.body.append("\n")` is replaced with an explicit `self.add_text("\n")` followed by
  `self._emit_forced_break("linebreak()")`, fired unconditionally. A rubric option-group heading
  (and the directive-option "Options" heading) now renders on its own line, separated from the
  first following option/field, instead of merging onto the same line. Verified harmless at true
  end-of-document.
- **New GATE-01 fixtures**:
  - `tests/fixtures/desc_signature_siblings_render_gate/` -- a `.. py:function::` with three
    sibling signature lines (`compile(source)` / `compile(source, filename)` /
    `compile(source, filename, symbol)`) plus a separate single-signature `.. py:function::
    solo(source)` exercising the lone-signature byte-unchanged edge.
  - `tests/fixtures/rubric_option_concat_render_gate/` -- a `.. rubric:: Structure Options`
    immediately followed by `.. option:: --sep` (mirroring `man/sphinx-quickstart.rst`), plus a
    trailing `.. rubric:: Trailing Heading` at true end-of-document with nothing after it.
- **Extended `tests/test_desc_signature_concat_render_gate.py`** with a new
  `TestDescSignatureSiblingsRenderGate` class asserting the emitted `.typ`'s total `linebreak()`
  count is exactly 2 (one between each of the 3 sibling signatures, zero around the lone
  signature), that both tokens sit strictly between the sibling `strong({...})` blocks, and that
  `index.pdf` begins with `%PDF`.
- **New `tests/test_rubric_option_concat_render_gate.py`** asserting a `linebreak()` token sits
  between the rubric's and the following option's `strong({...})` blocks, that the
  end-of-document rubric also emits its own trailing `linebreak()`, and that `index.pdf` begins
  with `%PDF` (the build succeeding at all proves the end-of-document rubric compiled cleanly).

## RED → GREEN Proof (D-05)

Both fixes were verified in both directions by temporarily reverting the corresponding
translator hunk in-place (via the `Edit` tool, never `git stash`), re-running the new test, and
restoring the fix:

- **FID-03**: pre-fix (no `_is_first_desc_signature` reset/check) →
  `TestDescSignatureSiblingsRenderGate::test_typstpdf_sibling_signatures_produce_pdf` FAILED with
  `assert 0 == 2` (zero `linebreak()` tokens present between the three sibling signatures).
  Post-fix → PASSED.
- **FID-04**: pre-fix (`depart_rubric` restored to the cosmetic `self.body.append("\n")`) →
  `TestRubricOptionConcatRenderGate::test_typstpdf_rubric_option_produces_pdf` FAILED with
  `assert 'linebreak()' in 'strong({text("Structure Options")})\n'` (the token absent between the
  rubric and the following option). Post-fix → PASSED.

## A discovery not anticipated by RESEARCH: FID-04 needs an extra leading separator

RESEARCH's proposed `depart_rubric` snippet called `_emit_forced_break("linebreak()")` directly
after `depart_strong`, with no separator in between. A real compile of that exact form failed
with `TypstError: expected semicolon or line break` at `strong({text("Structure
Options")})linebreak()` -- `depart_strong`'s closing `"})"` carries no trailing separator of its
own (unlike `depart_desc_signature`, whose unconditional trailing `"\n"` is what makes FID-03's
leading-`linebreak()`-at-the-next-signature placement safe without one). This is the same class
of bug Pitfall 1 documents for the *trailing* boundary of a forced break, encountered here at the
*leading* boundary instead. Fixed by adding an explicit `self.add_text("\n")` before the helper
call. Confirmed via real `typst.compile()` that the corrected form compiles cleanly and the
one-line-per-heading behavior matches the `-b text` authority's layout.

## Verification

- `uv run pytest tests/test_desc_signature_concat_render_gate.py tests/test_rubric_option_concat_render_gate.py -x` -- 3 passed.
- `uv run pytest tests/test_translator.py -q` -- 108 passed (no non-render structural regression;
  includes the updated `test_desc_signature_line_resets_per_signature`).
- `uv run pytest tests/test_rubric_propagated_target_render_gate.py -q` -- 1 passed (existing
  adjacent rubric gate, no regression).
- `uv run pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -q` -- 1 passed (~13s,
  corpus cache warm), run after EACH task commit (twice total) -- the full ~684-page Sphinx `doc/`
  corpus stays fatal-free after both fixes.
- `uv run pytest -q -m "not slow"` -- 436 passed, 45 failed. The 45 failures are the same
  pre-existing, documented NixOS-sandbox environmental failures in
  `tests/test_integration_multi_doc.py` and `tests/test_integration_nested_toctree.py` recorded in
  Plan 01's SUMMARY (434 passed there; +2 here for the two new render-gate test methods added this
  plan) -- unrelated to this plan's `translator.py` changes.
- `uv run black --check typsphinx/translator.py <new/modified test+fixture files>` -- clean.
- `uv run mypy typsphinx/translator.py` -- `Success: no issues found in 1 source file`.
- `uv run ruff check` could not run in this NixOS sandbox (`Could not start dynamically linked
  executable: ruff` -- the same pre-existing environmental limitation documented in Plan 01's
  SUMMARY and project memory, not caused by this plan's changes).

**Worktree provisioning:** ran `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`
first (per CLAUDE.md's "Worktree-isolated execution" section) to provision this worktree's own
`.venv`, then ran every subsequent test/build command via `uv run` so `import typsphinx` bound to
this worktree's edited copy rather than the main checkout's editable install. Both GATE-01
fixtures were confirmed RED against the worktree's pre-fix code and GREEN post-fix.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] FID-04 needed an extra leading separator not in RESEARCH's proposed snippet**
- **Found during:** Task 2, first manual build of the rubric_option_concat_render_gate fixture
- **Issue:** calling `_emit_forced_break("linebreak()")` immediately after `depart_strong` (as
  RESEARCH's snippet showed) produced `strong({...})linebreak()` with zero separating whitespace,
  which fails to compile with `TypstError: expected semicolon or line break`.
- **Fix:** added an explicit `self.add_text("\n")` before the `_emit_forced_break` call in
  `depart_rubric`.
- **Files modified:** `typsphinx/translator.py`
- **Commit:** `6e587df`

**2. [Rule 1 - Bug] Stale unit-test assertion contradicted the intentional FID-03 fix**
- **Found during:** Task 1, running the broader `tests/test_translator.py` suite after the FID-03
  translator edit
- **Issue:** `test_desc_signature_line_resets_per_signature` asserted `"linebreak()" not in
  output` for a `desc` with two sibling `desc_signature`s -- this encoded the FID-03 bug (no
  separator between siblings) as expected behavior, and now correctly fails since the fix adds
  exactly one `linebreak()` between the two siblings.
- **Fix:** updated the assertion to `output.count("linebreak()") == 1`, preserving the test's
  original intent (proving `_is_first_desc_signature_line` resets correctly per signature, since
  neither signature is genuinely multi-line) while accepting the new correct sibling separator.
- **Files modified:** `tests/test_translator.py`
- **Commit:** `6ef2c57`

**3. [Rule 1 - Bug] Fixture prose accidentally contained a literal double-backtick "linebreak()"**
- **Found during:** Task 1, first manual build of the desc_signature_siblings_render_gate fixture
- **Issue:** the initial `index.rst` draft's prose read "no extra ``linebreak()`` for the lone
  signature", which docutils renders as a literal `raw("linebreak()")` in the emitted `.typ` --
  polluting the test's total-`linebreak()`-count assertion with an unrelated match.
- **Fix:** reworded the prose to "no extra separator token for the lone signature", removing the
  literal collision while preserving the fixture's documentation intent.
- **Files modified:** `tests/fixtures/desc_signature_siblings_render_gate/index.rst`
- **Commit:** `6ef2c57`

## Known Stubs

None.

## Threat Flags

None -- both fixes emit only fixed literal break tokens (`"linebreak()"`), never interpolate
document content into the break-token strings, and touch no new trust boundary (per the plan's
own threat model, reaffirmed by inspection of both diffs).

## Self-Check: PASSED

- `typsphinx/translator.py` -- FOUND (modified)
- `tests/test_desc_signature_concat_render_gate.py` -- FOUND (modified)
- `tests/fixtures/desc_signature_siblings_render_gate/conf.py` -- FOUND
- `tests/fixtures/desc_signature_siblings_render_gate/index.rst` -- FOUND
- `tests/test_translator.py` -- FOUND (modified)
- `tests/test_rubric_option_concat_render_gate.py` -- FOUND
- `tests/fixtures/rubric_option_concat_render_gate/conf.py` -- FOUND
- `tests/fixtures/rubric_option_concat_render_gate/index.rst` -- FOUND
- commit `6ef2c57` -- FOUND in `git log --oneline --all`
- commit `6e587df` -- FOUND in `git log --oneline --all`
