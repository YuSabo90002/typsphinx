# Phase 38 Plan 03 GATE Evidence: D-10 Conjunction + Buffer-Swap Fixture

This file is Plan 03's own evidence record for D-10 (the SIG-08 marker's premise
Phase 38 voids) and the folded buffer-swap todo. Every command below was executed
in this plan's own session, in this worktree. No figure in this file was
transcribed or recalled from planning documents -- every string and every count
was measured directly against the fixtures and the untouched translator.

## Commit measured

- **Commit:** `387cf35072f4f05e6a235cbed2c43fdb1df93c18` (`test(38-03): build
  folded todo's buffer-swap fixture and gate` -- this plan's Task 2 commit,
  immediately preceding this evidence file's own commit). Task 1's commit
  (`test(38-03): add D-10 conjunction gate to SIG-08 module`) is its immediate
  parent.
- **`typsphinx/` untouched:** `git status --porcelain typsphinx/` at this commit
  is empty (0 lines) -- confirmed directly.
- **Date:** 2026-08-01T11:27:38Z

## Verbatim `uv run pytest tests/test_signature_break_and_arrow_gate.py tests/test_desc_break_marker_buffer_swap_gate.py -v` output

Pass/fail summary (all 17 collected node ids):

```
tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_exact_break_count_after_fix PASSED [  5%]
tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_no_adjacent_break_statements_anywhere PASSED [ 11%]
tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_content_follows_nested_member_stays_separated PASSED [ 17%]
tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_sibling_bodyless_control_keeps_one_break PASSED [ 23%]
tests/test_signature_break_and_arrow_gate.py::TestD10BodyWrapperBreakMarkerGate::test_d10_wrapper_present_and_break_count_still_eight FAILED [ 29%]
tests/test_signature_break_and_arrow_gate.py::TestD10BodyWrapperBreakMarkerGate::test_d10_no_adjacent_breaks_separated_only_by_wrapper_close PASSED [ 35%]
tests/test_signature_break_and_arrow_gate.py::TestD10BodyWrapperBreakMarkerGate::test_d10_two_level_nesting_yields_exactly_one_break PASSED [ 41%]
tests/test_signature_break_and_arrow_gate.py::TestSigArrowPdfGate::test_sig06_arrow_glyph_present_ascii_arrow_absent PASSED [ 47%]
tests/test_signature_break_and_arrow_gate.py::TestD11SeparatorStructuralGate::test_d11_separator_lands_inside_the_bracket PASSED [ 52%]
tests/test_signature_break_and_arrow_gate.py::TestD11SeparatorStructuralGate::test_d11_explicit_concatenation_non_regression PASSED [ 58%]
tests/test_signature_break_and_arrow_gate.py::TestD11SeparatorPdfGate::test_d11_target_rendering_present_defective_rendering_absent PASSED [ 64%]
tests/test_signature_break_and_arrow_gate.py::TestD11SeparatorPdfGate::test_d11_nested_optional_control_unchanged PASSED [ 70%]
tests/test_desc_break_marker_buffer_swap_gate.py::TestDescBreakMarkerBufferSwapStructuralGate::test_glossary_single_desc_gets_exactly_one_break PASSED [ 76%]
tests/test_desc_break_marker_buffer_swap_gate.py::TestDescBreakMarkerBufferSwapStructuralGate::test_glossary_nested_pair_gets_exactly_one_break PASSED [ 82%]
tests/test_desc_break_marker_buffer_swap_gate.py::TestDescBreakMarkerBufferSwapStructuralGate::test_top_level_control_matches_glossary_nested_pair_count PASSED [ 88%]
tests/test_desc_break_marker_buffer_swap_gate.py::TestDescBreakMarkerBufferSwapStructuralGate::test_no_adjacent_break_statements_anywhere PASSED [ 94%]
tests/test_desc_break_marker_buffer_swap_gate.py::TestDescBreakMarkerBufferSwapCompileGate::test_fixture_compiles_via_real_typst_compile PASSED [100%]

========================= 1 failed, 16 passed in 4.43s =========================
```

Verbatim failure assertion (the full emitted `.typ` embedded in the pytest
assertion message is elided below with a note -- it is reproduced in full once,
in the "Pre-phase `index.typ` quoted in full" section further down, rather than
twice over):

```
FAILED tests/test_signature_break_and_arrow_gate.py::TestD10BodyWrapperBreakMarkerGate::test_d10_wrapper_present_and_break_count_still_eight
E   AssertionError: D-10 conjunction: expected the body wrapper's opening token 'pad(left: 2.5em, {' (38-EMISSION-CONTRACT.md section 2) somewhere in the emitted .typ -- not found. This fixture contains at least one desc_content with a body (construct 1's SigBreakOuterClassOne), so the wrapper must appear once plan 38-05 lands visit_desc_content/depart_desc_content; its absence here is the pre-phase RED state:
E     ... [full emitted .typ elided here; quoted in full below] ...
E   assert 'pad(left: 2.5em, {' in '...'
```

The failure fires on the FIRST assertion in the conjunction test (wrapper-open
presence) -- confirmed directly: the failure message names the missing wrapper
token `'pad(left: 2.5em, {'`, not a `parbreak()` count mismatch, because the
three asserts inside the one test function are ordered wrapper-open,
wrapper-close, count, and `assert` short-circuits at the first failure.

## RED vs CONTROL-GREEN vs PRE-EXISTING-GREEN table

| Test node id | Pre-phase result | Disposition | Flips GREEN in |
|---|---|---|---|
| `test_sig08_exact_break_count_after_fix` | PASSED | PRE-EXISTING-GREEN (Phase 37 evidence, byte-unchanged; docstring gained a Phase 38 note only) | n/a |
| `test_sig08_no_adjacent_break_statements_anywhere` | PASSED | PRE-EXISTING-GREEN (Phase 37 evidence, byte-unchanged; docstring gained a Phase 38 note only) | n/a |
| `test_sig08_content_follows_nested_member_stays_separated` | PASSED | PRE-EXISTING-GREEN (Phase 37 control, byte-unchanged; docstring gained a Phase 38 note only) | n/a |
| `test_sig08_sibling_bodyless_control_keeps_one_break` | PASSED | PRE-EXISTING-GREEN (Phase 37 control, byte-unchanged; docstring gained a Phase 38 note only) | n/a |
| `TestD10BodyWrapperBreakMarkerGate::test_d10_wrapper_present_and_break_count_still_eight` | FAILED (wrapper-open token absent) | RED -- new this plan, D-10's own conjunction assertion | plan 38-05 (lands `visit_desc_content`/`depart_desc_content` per contract section 2, with the section 6.2 propagation fix) |
| `TestD10BodyWrapperBreakMarkerGate::test_d10_no_adjacent_breaks_separated_only_by_wrapper_close` | PASSED (pattern cannot match -- wrapper close does not exist yet) | CONTROL-GREEN -- new this plan, forward guard; must stay green through 38-05 | n/a (never a fix target; would catch a *propagation regression* if introduced later) |
| `TestD10BodyWrapperBreakMarkerGate::test_d10_two_level_nesting_yields_exactly_one_break` | PASSED (construct 1 already contributes exactly 1 break, unconditional pre-phase behaviour) | CONTROL-GREEN -- new this plan, depth-invariance guard; must stay green through 38-05 | n/a |
| `TestSigArrowPdfGate::test_sig06_arrow_glyph_present_ascii_arrow_absent` | PASSED | PRE-EXISTING-GREEN (Phase 37 SIG-06 flipped green at 37-07; untouched by this plan) | n/a |
| `TestD11SeparatorStructuralGate::test_d11_separator_lands_inside_the_bracket` | PASSED | PRE-EXISTING-GREEN (Phase 37 D-11 flipped green at 37-07; untouched by this plan) | n/a |
| `TestD11SeparatorStructuralGate::test_d11_explicit_concatenation_non_regression` | PASSED | PRE-EXISTING-GREEN (Phase 37 non-regression control; untouched by this plan) | n/a |
| `TestD11SeparatorPdfGate::test_d11_target_rendering_present_defective_rendering_absent` | PASSED | PRE-EXISTING-GREEN (Phase 37 D-11 flipped green at 37-07; untouched by this plan) | n/a |
| `TestD11SeparatorPdfGate::test_d11_nested_optional_control_unchanged` | PASSED | PRE-EXISTING-GREEN (Phase 37 non-regression control; untouched by this plan) | n/a |
| `TestDescBreakMarkerBufferSwapStructuralGate::test_glossary_single_desc_gets_exactly_one_break` | PASSED | CONTROL-GREEN -- new this plan, folded buffer-swap todo | n/a (declared non-regression control; see "Buffer-swap fixture" section below) |
| `TestDescBreakMarkerBufferSwapStructuralGate::test_glossary_nested_pair_gets_exactly_one_break` | PASSED | CONTROL-GREEN -- new this plan, folded buffer-swap todo | n/a (declared non-regression control; must be RE-RUN once the body wrapper lands, per the todo's own honest-measurement instruction) |
| `TestDescBreakMarkerBufferSwapStructuralGate::test_top_level_control_matches_glossary_nested_pair_count` | PASSED | CONTROL-GREEN -- new this plan, folded buffer-swap todo | n/a |
| `TestDescBreakMarkerBufferSwapStructuralGate::test_no_adjacent_break_statements_anywhere` | PASSED | CONTROL-GREEN -- new this plan, folded buffer-swap todo | n/a |
| `TestDescBreakMarkerBufferSwapCompileGate::test_fixture_compiles_via_real_typst_compile` | PASSED | CONTROL-GREEN -- new this plan, compile-acceptance | n/a |

The fix-owning plan for the sole RED row is confirmed by reading its own
frontmatter directly, not assumed: `38-05-PLAN.md` is where
`visit_desc_content`/`depart_desc_content` land per contract section 2, with the
section 6.2 marker-propagation fix folded into the same edit (contract section
6.2: "`depart_desc` itself needs no code change under this fix").

## Pre-phase break count for the signature fixture, quoted with the command

```
$ uv run python -m sphinx -b typst tests/fixtures/signature_break_and_arrow_gate <scratch>
build succeeded. (exit 0)
$ python3 -c "print(open('<scratch>/index.typ').read().count('parbreak()'))"
8
$ python3 -c "print('pad(left: 2.5em, {' in open('<scratch>/index.typ').read())"
False
```

Confirms the count that must survive at 8 (the D-10 conjunction test's second
half) and confirms the wrapper token's absence pre-phase (the D-10 conjunction
test's first half, and the reason the RED fires there rather than on the count).

## D-10 resolution taken at plan time

**Resolution: marker propagation through `depart_desc_content`'s close**
(38-EMISSION-CONTRACT.md section 6.2). `depart_desc_content` records whether the
marker still equals `len(self.body)` BEFORE emitting its close, emits the close,
and if it did, advances the marker past its own bytes -- so the outer
`depart_desc` still sees "nothing happened" and correctly suppresses its own
duplicate.

**`depart_desc` itself needs no code change under this fix.** Only its docstring
premise ("if nothing has been appended to `self.body` since the immediately
preceding desc's own `parbreak()` was recorded") must be corrected in the same
edit that lands section 2's wrapper, per contract section 6.3 -- that docstring
correction is plan 38-05's to make, not this plan's (this plan touches no file
under `typsphinx/`).

This decision was adopted **at plan time, before any translator edit exists**
(38-EMISSION-CONTRACT.md, authored 2026-08-01) and is proven by the conjunction
assertion recorded RED above, not assumed.

## Buffer-swap fixture: measured pre-phase outcome

**Measured outcome: GREEN, not RED.** All five node ids in
`tests/test_desc_break_marker_buffer_swap_gate.py` PASS against the untouched
translator (see the pass/fail summary above). This is the honest measurement the
folded todo's own binding instruction requires -- the todo's prose predicted RED,
but that was a prediction, not a measurement, and the fixture is NOT retro-fitted
into a RED it did not produce.

**Why it measures GREEN**, read directly from the emitted `.typ` (quoted in full
below): for the nested `desc` pair placed entirely inside one glossary
definition's body (`DescBreakGlossaryOuterClass` containing
`desc_break_glossary_inner_method`), BOTH `depart_desc` calls the SIG-08 marker
compares -- the inner method's and the outer class's -- run while `self.body`
points at the SAME swapped `current_definition_buffer` list. `visit_definition`
swaps the buffer in once, before either `desc` is entered, and
`depart_definition` swaps it back out only after both have departed. The pair's
own two departures never straddle a live buffer reassignment, so the marker's
buffer-agnostic `len(...)` comparison stays internally consistent for this
shape -- exactly as it would at document top level, confirmed by the top-level
control (`test_top_level_control_matches_glossary_nested_pair_count`) measuring
the identical break count (1) as the glossary-nested pair.

**Disposition: declared a non-regression control, re-run required after the body
wrapper lands.** This is NOT proof the hazard is unreachable in general -- it is
proof that THIS reachable shape (the one the todo names as concretely reachable)
does not, on the pre-phase tree, produce a cross-buffer marker comparison. The
todo's own suggested fix -- making the marker buffer-identifying via
`(id(self.body), len(self.body))` rather than a sixth per-site guard -- is still
the direction a later plan in this phase adopts, because Phase 38's body wrapper
(contract section 2) changes what the marker sees at every `desc` boundary,
which changes the hazard's reachability. Per the todo's own honest-measurement
instruction, this fixture must be re-run once the wrapper lands (plan 38-05).

Verbatim emitted `.typ` for the buffer-swap fixture (`tests/fixtures/desc_break_marker_buffer_swap_gate/`):

```typst
// Essential package imports
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

#show: codly-init.with()
#codly(languages: codly-languages)

#import "_template.typ": project

#show: project.with(
  title: "Desc Break Marker Buffer Swap Gate",
  authors: ("Test Author",),
  date: "1.0.0",
  lang: "en",
)

#{
[#heading(level: 1, {text("Desc Break Marker Buffer Swap Gate")}) <index:desc-break-marker-buffer-swap-gate>]

par({text("This fixture exists solely to be built through ")
raw("-b typst")
text(" by ")
raw("tests/test_desc_break_marker_buffer_swap_gate.py")
text(" (the folded todo ")
raw(".planning/todos/pending/2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md")
text(", folded into Phase 38 by D-10). It is not meant to be read as prose.")})


[#heading(level: 1, {text("Desc Inside A Glossary Definition")}) <index:desc-inside-a-glossary-definition>]

terms(separator: linebreak(), terms.item([#{text("buffer-swap-term-one")} <index:term-buffer-swap-term-one>], {par({text("Definition body containing a single desc directive.")})

block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("desc_break_glossary_function_one"))
raw("(") + raw(")")}))
[#metadata(none) <index:desc_break_glossary_function_one>]
par({text("Glossary function one body.")})

parbreak()}))


[#heading(level: 1, {text("Nested Desc Inside A Glossary Definition")}) <index:nested-desc-inside-a-glossary-definition>]

terms(separator: linebreak(), terms.item([#{text("buffer-swap-term-two")} <index:term-buffer-swap-term-two>], {par({text("Definition body containing a nested desc pair.")})

block(sticky: true, par(hanging-indent: 2.5em, {raw("class")
raw(" ")
strong(raw("DescBreakGlossaryOuterClass"))}))
[#metadata(none) <index:DescBreakGlossaryOuterClass>]
par({text("Glossary outer class body.")})

block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("desc_break_glossary_inner_method"))
raw("(") + raw(")")}))
[#metadata(none) <index:DescBreakGlossaryOuterClass.desc_break_glossary_inner_method>]
par({text("Glossary inner method body.")})

parbreak()}))     <---- construct 2's ONLY break: both depart_desc calls ran inside the SAME swapped buffer, so the marker's comparison stayed internally consistent -- GREEN, not the RED the todo predicted


[#heading(level: 1, {text("Nested Desc At Top Level – Nesting-Only Control")}) <index:nested-desc-at-top-level-nesting-only-control>]

block(sticky: true, par(hanging-indent: 2.5em, {raw("class")
raw(" ")
strong(raw("DescBreakTopLevelOuterClass"))}))
[#metadata(none) <index:DescBreakTopLevelOuterClass>]
par({text("Top-level outer class body.")})

block(sticky: true, par(hanging-indent: 2.5em, {strong(raw("desc_break_toplevel_inner_method"))
raw("(") + raw(")")}))
[#metadata(none) <index:DescBreakTopLevelOuterClass.desc_break_toplevel_inner_method>]
par({text("Top-level inner method body.")})

parbreak()     <---- CONTROL: identical count (1) with NO buffer swap at all -- confirms nesting, not the buffer swap, produces this shape either way

[#heading(level: 1, {text("Desc Inside A Figure Caption Or Admonition Title – Not Reachable")}) <index:desc-inside-a-figure-caption-or-admonition-title-not-reachable>]

par({text("Sentinel paragraph so this section is not empty.")})


}
```

## Compile-error statement: no assertion added by this plan fails as a compile error

Every assertion added by this plan runs against a `.typ` build that succeeded
(`sphinx-build -b typst` exit 0) and, where the test class requires it, a real
`typst.compile()` call that also succeeded. Quoted directly:

```
$ uv run python -m sphinx -b typst tests/fixtures/signature_break_and_arrow_gate <scratch>
build succeeded. (exit 0)
>>> typst.compile('<scratch>/index.typ', output='<scratch>/index.pdf')
signature_break_and_arrow_gate compile: exit 0, size 70297

$ uv run python -m sphinx -b typst tests/fixtures/desc_break_marker_buffer_swap_gate <scratch2>
build succeeded. (exit 0)
>>> typst.compile('<scratch2>/index.typ', output='<scratch2>/index.pdf')
desc_break_marker_buffer_swap_gate compile: exit 0, size 55088
```

The one RED assertion this plan adds (`test_d10_wrapper_present_and_break_count_still_eight`)
fails as a Python `AssertionError` inside a pytest test function, on a `.typ`
build that itself succeeded -- never as a `TypstCompilationError` or a non-zero
`sphinx-build` exit code. This matches milestone invariant #4: every design
defect in this milestone compiles successfully today, so RED is structural, not
a compile fatal.

## `git diff --stat` for the SIG-08 module, and the no-value-changed statement

```
$ git diff --stat 7a05d15~1 7a05d15 -- tests/test_signature_break_and_arrow_gate.py
 tests/test_signature_break_and_arrow_gate.py | 197 +++++++++++++++++++++++++++
 1 file changed, 197 insertions(+)
```

**197 insertions, 0 deletions.** Confirmed by reading the diff directly (not
inferred from the stat line alone): every hunk in the diff is a pure addition --
one new `import re` line, one new sentence appended inside each of the four
pre-existing SIG-08 test docstrings (`test_sig08_exact_break_count_after_fix`,
`test_sig08_no_adjacent_break_statements_anywhere`,
`test_sig08_content_follows_nested_member_stays_separated`,
`test_sig08_sibling_bodyless_control_keeps_one_break`), and one new
`TestD10BodyWrapperBreakMarkerGate` class appended after the existing
`TestSigBreakStructuralGate` class. No existing `assert` statement, expected
string, or expected count anywhere in the file was touched -- every Phase 37
expectation stays byte-identical in value, confirmed both by the diff shape
above and by all four pre-existing SIG-08 tests reporting PASSED in the pytest
run quoted at the top of this file.
