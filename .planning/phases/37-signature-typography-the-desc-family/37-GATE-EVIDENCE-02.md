# Phase 37 Plan 02 GATE-01 Evidence: SIG-06 / SIG-08 / D-11 RED Capture

This file is Plan 02's own GATE-01 evidence record. Per this plan's task
instructions it is NOT the shared `37-GATE-EVIDENCE-01..04.md` merge target
-- plan 37-08 merges the four sibling plans' evidence files at the end of
the phase; three sibling plans ran in the same wave and each owns its own
file.

Every command below was executed in this plan's own session, in this
worktree. No figure in this file was transcribed or recalled from planning
documents -- every string and every count was measured directly against the
fixture and the untouched translator.

## Commit measured

- **Commit:** `e846227df4e992a41843700d8b5b759a8c319f03` (`test(37-02): ship
  SIG-06/SIG-08/D-11 gate module, recorded RED` -- this plan's Task 2
  commit, immediately preceding this evidence file's own commit).
- **`typsphinx/` untouched:** `git status --porcelain typsphinx/` at this
  commit is empty (0 lines) -- confirmed directly.
- **Date:** 2026-08-01T04:59:37Z

## Verbatim `uv run pytest tests/test_signature_break_and_arrow_gate.py -v` output

Pass/fail summary (all 9 collected node ids):

```
tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_exact_break_count_after_fix FAILED [ 11%]
tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_no_adjacent_break_statements_anywhere FAILED [ 22%]
tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_content_follows_nested_member_stays_separated PASSED [ 33%]
tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_sibling_bodyless_control_keeps_one_break PASSED [ 44%]
tests/test_signature_break_and_arrow_gate.py::TestSigArrowPdfGate::test_sig06_arrow_glyph_present_ascii_arrow_absent FAILED [ 55%]
tests/test_signature_break_and_arrow_gate.py::TestD11SeparatorStructuralGate::test_d11_separator_lands_inside_the_bracket FAILED [ 66%]
tests/test_signature_break_and_arrow_gate.py::TestD11SeparatorStructuralGate::test_d11_explicit_concatenation_non_regression PASSED [ 77%]
tests/test_signature_break_and_arrow_gate.py::TestD11SeparatorPdfGate::test_d11_target_rendering_present_defective_rendering_absent FAILED [ 88%]
tests/test_signature_break_and_arrow_gate.py::TestD11SeparatorPdfGate::test_d11_nested_optional_control_unchanged PASSED [100%]
```

Verbatim failure assertion lines (the full `.typ`/PDF-text dumps embedded in
each pytest assertion message are elided below with a note -- they are
reproduced in full once, in the "Pre-phase `index.typ` quoted in full"
section further down, rather than four times over):

```
FAILED tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_exact_break_count_after_fix
E   AssertionError: SIG-08: expected exactly 8 parbreak() statements after the emission-position-marker fix (37-EMISSION-CONTRACT.md section 8) -- got 9. See this test's docstring for the full per-construct derivation.
E   assert 9 == 8

FAILED tests/test_signature_break_and_arrow_gate.py::TestSigBreakStructuralGate::test_sig08_no_adjacent_break_statements_anywhere
E   AssertionError: SIG-08: found adjacent parbreak() statements with nothing but whitespace between them at line(s) [43] -- the doubled-break defect (37-EMISSION-CONTRACT.md section 8) is present:
E     ... [full emitted .typ elided here; quoted in full below] ...
E   assert [43] == []
E     Left contains one more item: 43

FAILED tests/test_signature_break_and_arrow_gate.py::TestSigArrowPdfGate::test_sig06_arrow_glyph_present_ascii_arrow_absent
E   AssertionError: SIG-06: expected the real arrow glyph U+2192 in the compiled PDF's extracted text -- not found:
E     ... [full extracted PDF text elided; the relevant line is "sig_arrow_get_value() -> int" -- ASCII arrow present, glyph absent] ...
E   assert '→' in '...'

FAILED tests/test_signature_break_and_arrow_gate.py::TestD11SeparatorStructuralGate::test_d11_separator_lands_inside_the_bracket
E   AssertionError: D-11: expected the ', ' separator strictly between the last optional parameter ('timeout') and the closing bracket -- timeout_idx=123, separator_idx=-1, bracket_close_idx=141:
E     "connect")
E     text("(") + text("host") + text(", ") + text("port") + text("=") + text("8080") + text(", ") + text("[") + text("timeout") + text("]") + text("**kwargs") + text(")")})
E     [#metadata(none) <index:connect>]
E     par({text("Connect body.")})
E
E     parbreak()
E
E     [#heading(level: 1, {text("D-11 Nested Optional Non-Regression Control")})
E   assert 123 < -1

FAILED tests/test_signature_break_and_arrow_gate.py::TestD11SeparatorPdfGate::test_d11_target_rendering_present_defective_rendering_absent
E   AssertionError: D-11: expected the target rendering 'connect(host, port=8080, [timeout, ]**kwargs)' in the compiled PDF's extracted text:
E     ... [full extracted PDF text elided; the relevant line is "connect(host, port=8080, [timeout]**kwargs)" -- the DEFECTIVE rendering, target absent] ...
E   assert 'connect(host, port=8080, [timeout, ]**kwargs)' in '...'

========================= 5 failed, 4 passed in 2.26s ==========================
```

`separator_idx=-1` confirms `.find('", "', ...)` found no separator token
anywhere in the region -- the pre-phase translator emits no comma-in-string
at all between `"timeout"` and the closing bracket, exactly as
37-EMISSION-CONTRACT.md section 6.1's "pre-phase typsphinx" column states.

## RED vs CONTROL-GREEN table

| Test node id | Pre-phase result | Disposition | Flips GREEN in |
|---|---|---|---|
| `TestSigBreakStructuralGate::test_sig08_exact_break_count_after_fix` | FAILED (9 != 8) | RED | 37-05 (SIG-08 alone, Wave 2) |
| `TestSigBreakStructuralGate::test_sig08_no_adjacent_break_statements_anywhere` | FAILED (adjacency at line 43) | RED | 37-05 (SIG-08 alone, Wave 2) |
| `TestSigBreakStructuralGate::test_sig08_content_follows_nested_member_stays_separated` | PASSED | CONTROL-GREEN -- must stay green throughout | n/a (never a fix target) |
| `TestSigBreakStructuralGate::test_sig08_sibling_bodyless_control_keeps_one_break` | PASSED | CONTROL-GREEN -- must stay green throughout | n/a (never a fix target) |
| `TestSigArrowPdfGate::test_sig06_arrow_glyph_present_ascii_arrow_absent` | FAILED (arrow glyph absent) | RED | 37-07 (Wave 4, SIG-06 leg) |
| `TestD11SeparatorStructuralGate::test_d11_separator_lands_inside_the_bracket` | FAILED (`separator_idx=-1`) | RED | 37-07 (Wave 4, D-11 leg) |
| `TestD11SeparatorStructuralGate::test_d11_explicit_concatenation_non_regression` | PASSED | CONTROL-GREEN -- non-regression, no code change needed (contract section 6.2) | n/a (never a fix target) |
| `TestD11SeparatorPdfGate::test_d11_target_rendering_present_defective_rendering_absent` | FAILED (defective rendering present, target absent) | RED | 37-07 (Wave 4, D-11 leg) |
| `TestD11SeparatorPdfGate::test_d11_nested_optional_control_unchanged` | PASSED | CONTROL-GREEN -- must stay green throughout | n/a (never a fix target) |

Both fix-owning plans confirmed by reading their own frontmatter/must_haves
directly, not assumed: `37-05-PLAN.md` frontmatter `requirements: [SIG-08]`
(Wave 2, "Land SIG-08 alone... before the wrapper change"); `37-07-PLAN.md`
frontmatter `requirements: [SIG-05, SIG-06]` and its must_haves list
covering the D-11 optional-group separator and the D-11 non-regression
guard alongside SIG-06 (Wave 4, depends on 37-02/37-04/37-06).

## SIG-08 expected break count derivation

From the fixture's doctree (measured this session via
`env.get_and_resolve_doctree`, `tests/fixtures/signature_break_and_arrow_gate/`):

```
Total desc nodes: 9
  desc ids=['SigBreakOuterClassOne'] nested_in_desc=False
  desc ids=['SigBreakOuterClassOne.sig_break_inner_method_one'] nested_in_desc=True
  desc ids=['SigBreakOuterClassTwo'] nested_in_desc=False
  desc ids=['SigBreakOuterClassTwo.sig_break_inner_method_two'] nested_in_desc=True
  desc ids=['confval-sig_break_confval_one'] nested_in_desc=False
  desc ids=['confval-sig_break_confval_two'] nested_in_desc=False
  desc ids=['sig_arrow_get_value'] nested_in_desc=False
  desc ids=['connect'] nested_in_desc=False
  desc ids=['printf'] nested_in_desc=False
```

9 `desc` nodes total, 2 of which are nested (`sig_break_inner_method_one`
inside `SigBreakOuterClassOne`; `sig_break_inner_method_two` inside
`SigBreakOuterClassTwo`).

Pre-phase (unconditional `parbreak()` per `desc` departure, no suppression
logic exists at all): `grep -c "parbreak()"` on the emitted `index.typ`
gives **9** -- exactly one per `desc` node, confirmed directly.

Post-fix expected count, per construct (37-EMISSION-CONTRACT.md section 8's
emission-position-marker rule -- suppress a `desc`'s own `parbreak()` only
when nothing was emitted since the immediately preceding `desc`'s own
`parbreak()`):

| Construct | `desc` departures | Suppressed? | Contributes |
|---|---|---|---|
| 1 (`SigBreakOuterClassOne` + nested `sig_break_inner_method_one`) | 2 | Outer's break IS suppressed -- nothing is emitted inside the outer class body after the nested method's own `parbreak()` | 1 |
| 2 (`SigBreakOuterClassTwo` + nested `sig_break_inner_method_two` + trailing paragraph) | 2 | Neither suppressed -- the trailing paragraph's `par(...)` is emitted between the inner `desc`'s break and the outer `desc`'s departure | 2 |
| 3 (two sibling body-less confvals) | 2 | Neither suppressed -- non-nested; each confval's own signature/field content precedes its own departure | 2 |
| 4 (`sig_arrow_get_value`) | 1 | Not suppressed -- non-nested | 1 |
| 5 (`connect`) | 1 | Not suppressed -- non-nested | 1 |
| 6 (`printf`) | 1 | Not suppressed -- non-nested | 1 |
| **Total** | **9** | | **8** |

Expected count after the fix: **8**. Pre-phase actual: **9**. The exact
count assertion (`test_sig08_exact_break_count_after_fix`) is RED by
exactly this one-suppression margin, matching the measured
`assert 9 == 8` failure above.

## Pre-phase `index.typ` quoted in full

Built via `uv run python -m sphinx -b typst
tests/fixtures/signature_break_and_arrow_gate <scratch>` against the commit
named above. The adjacent-break defect (construct 1, the SIG-08 RED case)
is marked inline.

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
  title: "Signature Break And Arrow Gate",
  authors: ("Test Author",),
  date: "1.0.0",
  lang: "en",
)

#{
[#heading(level: 1, {text("Signature Break And Arrow Gate")}) <index:signature-break-and-arrow-gate>]

par({text("This fixture exists solely to be built through ")
raw("-b typst")
text(" (structural assertions) and compiled to PDF via ")
raw("typst.compile()")
text(" (glyph and text-extraction assertions) by ")
raw("tests/test_signature_break_and_arrow_gate.py")
text(" (Phase 37, GATE-01, SIG-06/SIG-08/D-11). It is not meant to be read as prose.")})


[#heading(level: 1, {text("SIG-08 Nested Desc Break")}) <index:sig-08-nested-desc-break>]

strong({text("class")
text(" ")
text("SigBreakOuterClassOne")})
[#metadata(none) <index:SigBreakOuterClassOne>]
par({text("Outer class one body.")})

strong({text("sig_break_inner_method_one")
text("(") + text(")")})
[#metadata(none) <index:SigBreakOuterClassOne.sig_break_inner_method_one>]
par({text("Inner method one body.")})

parbreak()
parbreak()                          <---- SIG-08 RED: two adjacent parbreak() with nothing between, line 44-45 (inner desc's + outer desc's own unconditional breaks)

[#heading(level: 1, {text("SIG-08 Content Follows Nested Member")}) <index:sig-08-content-follows-nested-member>]

strong({text("class")
text(" ")
text("SigBreakOuterClassTwo")})
[#metadata(none) <index:SigBreakOuterClassTwo>]
par({text("Outer class two body.")})

strong({text("sig_break_inner_method_two")
text("(") + text(")")})
[#metadata(none) <index:SigBreakOuterClassTwo.sig_break_inner_method_two>]
par({text("Inner method two body.")})

parbreak()
par({text("Trailing paragraph after the nested member.")})

parbreak()

[#heading(level: 1, {text("SIG-08 Sibling Bodyless Control")}) <index:sig-08-sibling-bodyless-control>]

strong({text("sig_break_confval_one")})
[#metadata(none) <index:confval-sig_break_confval_one>]
strong(text("Type") + text(": "))
text("str")

text("  ")
strong(text("Default") + text(": "))
raw("\"a\"")

parbreak()
strong({text("sig_break_confval_two")})
[#metadata(none) <index:confval-sig_break_confval_two>]
strong(text("Type") + text(": "))
text("str")

text("  ")
strong(text("Default") + text(": "))
raw("\"b\"")

parbreak()

[#heading(level: 1, {text("SIG-06 Return Arrow")}) <index:sig-06-return-arrow>]

strong({text("sig_arrow_get_value")
text("(") + text(")")
text(" -> ")                        <---- SIG-06 RED: ASCII "->" literal, not the real arrow glyph
text("int")})
[#metadata(none) <index:sig_arrow_get_value>]
parbreak()

[#heading(level: 1, {text("D-11 Optional Group Separator Defect")}) <index:d-11-optional-group-separator-defect>]

strong({text("connect")
text("(") + text("host") + text(", ") + text("port") + text("=") + text("8080") + text(", ") + text("[") + text("timeout") + text("]") + text("**kwargs") + text(")")})
                                    <---- D-11 RED: no ", " between "timeout" and "]" (comma dropped);
                                          note "]" and "**kwargs" ARE already " + "-joined (section 6.2 non-regression control)
[#metadata(none) <index:connect>]
par({text("Connect body.")})

parbreak()

[#heading(level: 1, {text("D-11 Nested Optional Non-Regression Control")}) <index:d-11-nested-optional-non-regression-control>]

strong({text("printf")
text("(") + text("fmt") + text(", ") + text("[") + text("args") + text(", ") + text("[") + text("more") + text("]") + text("]") + text(")")})
[#metadata(none) <index:printf>]
parbreak()

}
```

## D-11: measured Sphinx-HTML target vs. pre-phase typsphinx rendering

Both rows are `[measured]` in 37-EMISSION-CONTRACT.md section 6.1 (this
plan re-reads and re-quotes them, does not re-derive from a fresh HTML
build):

| Source | Sphinx HTML renders | Pre-phase typsphinx (confirmed this session, compiled PDF text) | Phase 37 target |
|---|---|---|---|
| `connect(host, port=8080, [timeout], **kwargs)` | `connect(host, port=8080, [timeout, ]**kwargs)` | `connect(host, port=8080, [timeout]**kwargs)` | `connect(host, port=8080, [timeout, ]**kwargs)` |
| `printf(fmt[, args[, more]])` | -- | `printf(fmt, [args, [more]])` | **unchanged** -- both `desc_optional`s are last children, so neither gains a comma (the D-11 non-regression control) |

This plan's own compiled-PDF extraction of `signature_break_and_arrow_gate`
confirms the "pre-phase typsphinx" column directly: the extracted text for
construct 5 reads `connect(host, port=8080, [timeout]**kwargs)` (comma
missing) and for construct 6 reads `printf(fmt, [args, [more]])` (matches
the control target exactly, unchanged).

## Contract section 6.2 correction, restated

37-EMISSION-CONTRACT.md section 6.2 corrects `37-CONTEXT.md` D-11's claim
that the closing bracket (`]`) and the following parameter (`**kwargs`) are
emitted as two juxtaposed calls with **no** `+` joining them. **That claim
does not reproduce on the current tree.** This plan's own build of the
`connect(...)` region confirms the correction directly: the emitted `.typ`
already reads
`... + text("[") + text("timeout") + text("]") + text("**kwargs") + text(")")` --
an explicit `" + "` already joins `"]"` and `"**kwargs"`, because
`depart_desc_optional` already sets `_desc_parameter_has_content = True`,
and the next parameter's text emission therefore takes
`_emit_inline_concat_separator()`'s `" + "` branch unconditionally.

**Disposition:** the D-11 obligation for this half is **not** a fix -- it
converts into a **non-regression assertion**
(`test_d11_explicit_concatenation_non_regression`, CONTROL-GREEN in the
table above, PASSED pre-phase and must stay green through the D-11 fix in
37-07). No code change is required for it. Only the comma-inside-the-
bracket half (the `test_d11_separator_lands_inside_the_bracket` and
`test_d11_target_rendering_present_defective_rendering_absent` RED
assertions above) requires a `typsphinx/translator.py` change.
