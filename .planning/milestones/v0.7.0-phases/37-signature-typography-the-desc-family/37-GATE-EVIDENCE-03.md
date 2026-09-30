# Phase 37 Plan 03 GATE Evidence: SIG-07 / SIG-09 Geometric RED Capture

This file is Plan 03's own evidence record (three sibling plans run in this
wave -- `37-08` merges `37-GATE-EVIDENCE-01..04.md` at the end of the phase;
this file is not shared with 01/02/04).

Every command below was executed in this plan's own session, in this
worktree. No figure in this file was transcribed or recalled from planning
documents -- every width/page-count/probe result was read directly from a
real `typst.compile()` output this session.

## Commit measured

**`995c78d`** -- the last commit to touch `typsphinx/translator.py`
(`fix(36-03): clear list_item_needs_separator after block math, close
MATH-02`, Phase 36). `typsphinx/translator.py` is untouched by this plan:

```
$ git status --porcelain typsphinx/
(empty)
```

Both gate modules below were run against this exact, unmodified translator.

## Measurement method

Every geometric value (column width, segment widths, page count, per-page
sentinel location) was read from a real `typst.compile()` of the fixture's
own emitted, fully template-wrapped `.typ` -- not a hand-approximated
stand-in -- via one of two Typst-side mechanisms:

- **Typst-side `context measure(...)` / `context layout(size => ...)`**
  probes, compiled through `typst.compile()`, for every SIG-07 width (the
  available column width and every candidate segment's width). This is
  the *only* mechanism used for geometric (position/size) values.
- **Plain `pypdf.extract_text()`, per PAGE** (SIG-09's per-page loop over
  `reader.pages`) for content/ordering assertions only -- never the
  per-glyph position-callback extraction mode, which was measured this
  session (and independently in `37-RESEARCH.md`) to report `x=0, y=0`
  for every glyph on Typst-generated PDFs in this sandbox. `grep -c
  'visitor_text'` returns `0` in both test modules.

Every compiled-PDF text read strips U+200B first (`ZWSP` constant in both
modules) -- once a zero-width break opportunity exists anywhere in a
document, `pypdf` emits it spuriously at unrelated glyph boundaries too
(contract section 4.2). A second, independently discovered `pypdf` quirk
was handled the same way in the SIG-07 probe helper: `pypdf` also inserts
spurious whitespace/newlines between separate text-showing operations even
when they render on the same visual line, so the probe's own
`LABEL=VALUE` markers are parsed against a whitespace-flattened copy of
the extracted text.

## SIG-07 -- widths table (measured this session)

All widths measured at the project's real production template geometry
(A4, default margins, 11pt -- `typsphinx/templates/base.typ`, no margin
override), by compiling the real emitted `index.typ` from
`tests/fixtures/signature_overflow_render_gate/` plus an appended
`context measure(...)`/`context layout(...)` probe.

| Quantity | Width | Source |
|---|---|---|
| Probe-read available text column | **453.54pt** | `#context [COLWIDTH=#layout(size => size.width)]` -- matches `37-EMISSION-CONTRACT.md` section 10 exactly |
| Synthetic identifier (111 chars, `typsphinx.overflow...OverflowProbeDocumenter`), combined desc_addname+desc_name run, measured as `text(...)` (the actual pre-phase primitive) | **542.16pt** -- overflows by 88.62pt | `measure(text("..."))` |
| Same identifier, measured as `raw(...)` with no break opportunity | **588.08pt** -- overflows by 134.54pt | `measure(raw("..."))` |
| Same identifier, measured as `raw(...)` WITH a ZWSP inserted after every period | **588.08pt** -- IDENTICAL to the no-break form | `measure(raw("..."))`, confirms 37-RESEARCH.md's claim that ZWSP creates a break *opportunity*, not a narrower measured width |
| Its longest ZWSP-delimited segment, `OverflowProbeDocumenter` (desc_name, no dots) | **121.86pt** -- fits | `measure(raw("OverflowProbeDocumenter"))` |
| Real-corpus control (`sphinx.util.parsing.nested_parse_to_nodes`, 41-char qualname), combined desc_addname+desc_name run, one unbroken segment (no ZWSP pre-phase) | **217.22pt** -- fits | `measure(raw("sphinx.util.parsing.nested_parse_to_nodes"))` |

The 111-character synthetic identifier and its 453.54pt/542.16pt/588.08pt/
121.86pt figures are byte-for-byte the values recorded in
`37-EMISSION-CONTRACT.md` section 10 -- reproduced independently this
session against the real, live fixture (not copied from the contract
without re-measuring).

## SIG-09 -- chosen page-height override mechanism

No existing fixture in this project overrides page geometry
(`37-PATTERNS.md`'s "fixture-directory convention" warning). Three
candidates were evaluated per Task 2's action text, in order:

**(a) a `typst_elements`/template-parameter override reaching `project()`
via `conf.py`.** REJECTED without a probe: `template_engine.py`'s
`ELEMENTS_ALLOWLIST` (read directly) only declares `papersize`, `fontsize`,
and `lang` -- there is no page-height key, and adding one is configuration
surface this phase does not own.

**(b) a fixture-local custom `typst_template`.** REJECTED without a probe:
heavier than necessary (a whole parallel template file) for a single
geometry override this one gate needs.

**(c) compiling the emitted `index.typ` in the test with a small
page-geometry preamble prepended.** CHOSEN, and PROVEN by two real
`typst.compile()` probes this session before being committed to:

**Probe 1 -- override at the very TOP of the file (before `project()`'s own
`set page(paper: papersize, ...)` call). Result: CLOBBERED.**

```python
#set page(height: 200pt, margin: 20pt)

#let project(..., body) = {
  set page(paper: papersize, numbering: "1", number-align: center)
  ...
  body
}

#show: project.with(title: "Probe", authors: (), date: none)

#context [Page height is: #page.height]
```

Verbatim probe output:
```
num pages: 2
--- page 0 ---
Probe
1
mediabox height (pt): 841.8898
--- page 1 ---
Page height is: 841.89pt
2
mediabox height (pt): 841.8898
```

The override had NO effect -- page 1's height is still the full A4 height
(841.89pt), because Typst's `paper:` keyword sets width AND height
together, discarding the earlier explicit height set before `project()`
ran its own `set page(paper: ...)`.

**Probe 2 -- override inserted as the FIRST statement of the `body`
argument (i.e. chronologically AFTER `project()`'s own `set page()` call,
inside the same function execution). Result: TAKES EFFECT.**

```python
#let project(..., body) = {
  set page(paper: papersize, numbering: "1", number-align: center)
  ...
  body
}

#show: project.with(title: "Probe", authors: (), date: none)

#set page(height: 200pt, margin: 20pt)
#context [Page height is: #page.height]
```

Verbatim probe output:
```
num pages: 2
--- page 0 ---
Probe
1
mediabox height (pt): 841.8898
--- page 1 ---
Page height is: 200pt
2
mediabox height (pt): 200.0
```

The override took effect exactly where expected: page 0 (the title page,
rendered by `project()` before `body`) keeps the real A4 height; page 1
(the content that follows the override, matching where `body` -- the
fixture's own translated content -- is substituted) uses the overridden
200pt height.

**Conclusion, applied in `tests/test_signature_page_boundary_render_gate.py`'s
`_insert_page_override`:** insert `#set page(height:, margin:)` immediately
after the real `#show: project.with(...)` call's closing paren and blank
line (found by searching from the `#import "_template.typ"` line onward,
to skip the unrelated earlier `#show: codly-init.with()`). The emitted
`.typ` is otherwise UNMODIFIED apart from this inserted preamble -- the
artifact under test stays the translator's own output.

## Verbatim pytest output -- SIG-07

Command: `uv run pytest tests/test_signature_overflow_render_gate.py -v --tb=short`

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .../.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a08a2caf258922528
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 6 items

tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_fixture_identifier_is_synthetic_and_over_length PASSED [ 16%]
tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_primary_widest_segment_fits_column FAILED [ 33%]
tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_hanging_indent_present FAILED [ 50%]
tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_break_opportunity_after_every_period FAILED [ 66%]
tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_control_widest_segment_fits_column_before_and_after PASSED [ 83%]
tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_column_width_sanity PASSED [100%]

=================================== FAILURES ===================================
___ TestSignatureOverflowRenderGate.test_primary_widest_segment_fits_column ____
tests/test_signature_overflow_render_gate.py:288: in test_primary_widest_segment_fits_column
    assert widest < column_width, (
E   AssertionError: widest unbreakable segment (588.08pt) does not fit inside the available production column (453.54pt) -- segments measured: [('typsphinx.overflow.probe.deeply.nested.package.namespace.segment.alpha.beta.gamma.delta.OverflowProbeDocumenter', 588.08)]
E   assert 588.08 < 453.54
_________ TestSignatureOverflowRenderGate.test_hanging_indent_present __________
tests/test_signature_overflow_render_gate.py:312: in test_hanging_indent_present
    assert "par(hanging-indent: 2.5em" in typ_source, (
E   AssertionError: expected the desc_signature wrapper to carry par(hanging-indent: 2.5em, ...) -- D-06's chosen, non-negotiable overflow strategy (grid() and font-shrinking were measured and rejected).
E   assert 'par(hanging-indent: 2.5em' in '...strong({text("class")\ntext(" ")\ntext("typsphinx.overflow.probe.deeply.nested.package.namespace.segment.alpha.beta.gamma.delta.")\ntext("OverflowProbeDocumenter")\ntext("(") + text("directive") + text(")")})...'
__ TestSignatureOverflowRenderGate.test_break_opportunity_after_every_period ___
tests/test_signature_overflow_render_gate.py:337: in test_break_opportunity_after_every_period
    assert actual_zwsp == expected_periods, (
E   AssertionError: expected the break-opportunity escape ('\\u{200B}') after EVERY one of the 12 periods in the synthetic identifier; found 0 occurrence(s) in the emitted run 'typsphinx.overflow.probe.deeply.nested.package.namespace.segment.alpha.beta.gamma.delta.OverflowProbeDocumenter'.
E   assert 0 == 12
=========================== short test summary info ============================
FAILED tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_primary_widest_segment_fits_column
FAILED tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_hanging_indent_present
FAILED tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_break_opportunity_after_every_period
========================= 3 failed, 3 passed in 0.63s ==========================
```

(The `test_hanging_indent_present` failure message above is trimmed to the
load-bearing substring; the full assertion message additionally embeds the
entire emitted `.typ` source, elided here for readability -- re-run the
command above for the untruncated form.)

## Verbatim pytest output -- SIG-09

Command: `uv run pytest tests/test_signature_page_boundary_render_gate.py -v --tb=short`

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .../.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a08a2caf258922528
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 3 items

tests/test_signature_page_boundary_render_gate.py::TestSignaturePageBoundaryRenderGate::test_two_page_precondition_guard PASSED [ 33%]
tests/test_signature_page_boundary_render_gate.py::TestSignaturePageBoundaryRenderGate::test_page_count_does_not_inflate PASSED [ 66%]
tests/test_signature_page_boundary_render_gate.py::TestSignaturePageBoundaryRenderGate::test_primary_signature_and_body_share_a_page FAILED [100%]

=================================== FAILURES ===================================
_ TestSignaturePageBoundaryRenderGate.test_primary_signature_and_body_share_a_page _
tests/test_signature_page_boundary_render_gate.py:285: in test_primary_signature_and_body_share_a_page
    assert name_idx == param_idx == body_idx, (
E   AssertionError: signature name (page index 4), its parameter list (page index 4), and the first line of its description body (page index 5) are NOT all on the same page -- SIG-09 page-boundary defect.
E   assert 4 == 5
=========================== short test summary info ============================
FAILED tests/test_signature_page_boundary_render_gate.py::TestSignaturePageBoundaryRenderGate::test_primary_signature_and_body_share_a_page
========================= 1 failed, 2 passed in 0.49s ==========================
```

## RED-versus-CONTROL-GREEN table (by test node id)

| Test node id | Pre-phase (this commit, `995c78d`) | Plan that flips it | Role |
|---|---|---|---|
| `tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_fixture_identifier_is_synthetic_and_over_length` | PASSED | n/a -- static fixture-content check, not a translator gate | sanity |
| `tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_primary_widest_segment_fits_column` | **FAILED (RED)** | `37-06` | SIG-07 primary |
| `tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_hanging_indent_present` | **FAILED (RED)** | `37-06` | SIG-07 / D-06 |
| `tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_break_opportunity_after_every_period` | **FAILED (RED)** | `37-06` | SIG-07 / D-07 |
| `tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_control_widest_segment_fits_column_before_and_after` | PASSED (CONTROL) | must stay PASSED | non-regression control |
| `tests/test_signature_overflow_render_gate.py::TestSignatureOverflowRenderGate::test_column_width_sanity` | PASSED | must stay PASSED | sanity |
| `tests/test_signature_page_boundary_render_gate.py::TestSignaturePageBoundaryRenderGate::test_two_page_precondition_guard` | PASSED (GUARD) | must stay PASSED | vacuous-pass guard |
| `tests/test_signature_page_boundary_render_gate.py::TestSignaturePageBoundaryRenderGate::test_page_count_does_not_inflate` | PASSED (GUARD) | must stay PASSED (Pitfall 1) | non-inflation guard |
| `tests/test_signature_page_boundary_render_gate.py::TestSignaturePageBoundaryRenderGate::test_primary_signature_and_body_share_a_page` | **FAILED (RED)** | `37-06` | SIG-09 primary |

Later waves verify by set difference over these node ids (never by count),
per this plan's instructions.

## SYNTHETIC-by-necessity statement (SIG-07)

The SIG-07 RED case above (`typsphinx.overflow.probe.deeply.nested.package.
namespace.segment.alpha.beta.gamma.delta.OverflowProbeDocumenter`, 111
characters) is **SYNTHETIC by necessity**, not by convenience. Measured
this session and in `37-RESEARCH.md` (Pitfall 2): no signature in the real
Sphinx v9.1.0 `doc/` corpus (1,445 signatures scanned) overflows the
453.54pt production text column -- the corpus's own worst-case qualified
name, `sphinx.util.parsing.nested_parse_to_nodes` (41 characters),
measures only 217.22pt as an unbroken run, comfortably under the column.

**Warning, stated explicitly per Task 3's action text:** a "RED" fixture
built from the real corpus would be GREEN against the unfixed translator
-- that is not a fixture defect, it is a signal about the corpus (it does
not reach the failure mode at production page width), not about the
translator or the test. The corpus-derived construct in this plan's
fixture is deliberately kept as a **non-regression CONTROL**
(`test_control_widest_segment_fits_column_before_and_after`), labelled as
such in both the fixture's rST comments and this evidence file, and is
expected to remain green both before and after the `37-06` fix. It must
never be converted into the RED case, and the synthetic identifier must
never be replaced by a corpus-derived one.

## Files this plan created

```
tests/fixtures/signature_overflow_render_gate/conf.py
tests/fixtures/signature_overflow_render_gate/index.rst
tests/test_signature_overflow_render_gate.py
tests/fixtures/signature_page_boundary_render_gate/conf.py
tests/fixtures/signature_page_boundary_render_gate/index.rst
tests/test_signature_page_boundary_render_gate.py
.planning/phases/37-signature-typography-the-desc-family/37-GATE-EVIDENCE-03.md
```

`git diff --stat -- typsphinx/` for this plan's two task commits (`dab9a60`,
`6113429`) is empty -- confirmed no path under `typsphinx/` was touched.
