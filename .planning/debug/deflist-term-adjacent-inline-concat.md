---
status: resolved
trigger: "Corpus gate fatal #3: TypstError: expected comma at tutorial/getting-started.typ:127:147 — terms.item(raw(\"make.bat\")text(\" and \")raw(\"Makefile\"), par({...})). Def-list term inline nodes juxtaposed with no + concatenation."
created: 2026-07-12T00:00:00
updated: 2026-07-12T00:00:00
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "A def-list TERM buffers its inline children into current_term_buffer via each child's visit_* add_text, then depart_term does ''.join(buffer). Adjacent top-level inline expressions (literal→text→literal = raw(\"make.bat\") text(\" and \") raw(\"Makefile\")) are concatenated with NO separator. In Typst code mode (the first arg of terms.item(TERM, DEF)) two juxtaposed function-call expressions are a syntax error: the parser reads the first expression as the argument then expects a comma → 'expected comma'. The translator inserts ' + ' between adjacent inline code-mode expressions in the _in_link and in_desc_parameter contexts (via visit_Text) but the term-buffer context sets no such flag, and visit_literal participates in NO +-concatenation context at all."
  confirming_evidence:
    - "Minimal fixture term `` `make.bat` and `Makefile` `` emits verbatim: terms.item(raw(\"make.bat\")text(\" and \")raw(\"Makefile\"), par({text(\"The two build entry points.\")})) — byte-identical to the corpus fatal at getting-started.typ:127."
    - "typst.compile of box(raw(\"make.bat\")text(\" and \")raw(\"Makefile\")) → FAIL 'expected comma'. box(raw(\"make.bat\") + text(\" and \") + raw(\"Makefile\")) → COMPILE OK. box(raw(\"make.bat\")) (single) → COMPILE OK (no leading/trailing + needed)."
    - "visit_Text (641-667) inserts ' + ' only under in_desc_parameter/_in_link; visit_literal (819-855) inserts NO + under any concat context. The term buffer sets neither flag → juxtaposition with no separator."
  falsification_test: "If, after setting an _in_term concat flag and routing visit_Text + visit_literal through it (' + ' before each expr after the first), the fixture term STILL emits raw(...)raw(...) with no + OR still fails typst.compile with 'expected comma', the hypothesis is wrong."
  fix_rationale: "Reuse the EXISTING _in_link/_has_content pattern: add an _in_term/_term_has_content pair set in visit_term, cleared in depart_term. Add an _in_term branch to visit_Text (mirroring _in_link exactly) AND to visit_literal (which currently has no concat branch). This inserts ' + ' between adjacent term inline expressions and none before the first / after the last. It addresses the ROOT (missing concat operator in the term code-mode context), not the symptom (one file). Definition (2nd arg) path wraps in par({...}) markup where juxtaposition is valid — untouched."
  blind_spots: "Only visit_Text + visit_literal participate. A term whose direct children include emphasis/strong/reference (which emit their own multi-fragment expressions) would still lack a + at those boundaries (visit_emphasis/visit_reference don't check _in_term). Corpus fatal is literal+text+literal only, so covered. Sibling risk reported, not fixed (fix_requirements #3)."

hypothesis: CONFIRMED (see reasoning_checkpoint)
test: add _in_term/_term_has_content; branch in visit_Text + visit_literal; rebuild fixture + fast suite + corpus gate
expecting: fixture term emits raw(\"make.bat\") + text(\" and \") + raw(\"Makefile\"); compiles to %PDF; corpus advances past getting-started.typ:127 comma fatal
next_action: Implement flag + branches, add fast regression test, run fast suite + lint + corpus gate.

## Symptoms

expected: Sphinx doc/ corpus compiles through -b typstpdf with no fatal TypstCompilationError; def-list terms with adjacent inline nodes emit valid Typst.
actual: "Typst compilation failed: TypstError: expected comma" at tutorial/getting-started.typ:127:147 — terms.item(raw("make.bat")text(" and ")raw("Makefile"), par({...})); adjacent inline term expressions have no + concatenation.
errors: "TypstError: expected comma"
reproduction: uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s
started: Pre-existing bug surfaced by Phase 15 corpus gate, after the asset-copy (bug #1) and target-label (bug #2) fixes unblocked the compile path.

## Eliminated

## Evidence

- timestamp: repro
  checked: Built minimal `` `make.bat` and `Makefile` `` term fixture via -b typst; inspected emitted index.typ
  found: terms.item(raw("make.bat")text(" and ")raw("Makefile"), par({text("The two build entry points.")})) — no + between the three inline expressions. Byte-match to corpus fatal.
  implication: Root cause = missing + concatenation in term buffer join. Confirmed reproducible offline.

- timestamp: compile-direction
  checked: typst.compile of box(...) with broken vs fixed vs single term expr (typst 0.15)
  found: broken (raw()text()raw()) → 'expected comma'; fixed (raw() + text() + raw()) → OK; single (raw()) → OK.
  implication: + concatenation is the exact fix; single-node terms need no + (has_content guard suffices).

## Resolution

root_cause: Def-list TERM inline children are buffered then ''.join'd in depart_term with NO separator. Adjacent top-level inline code-mode expressions (literal→text→literal) become raw("a")text("b")raw("c"), a Typst syntax error in the code-mode first arg of terms.item ('expected comma'). The translator's existing + concat lives only in visit_Text under _in_link/in_desc_parameter; the term buffer sets no concat flag and visit_literal has no concat branch at all.
fix: Added an _in_term / _term_has_content concat context mirroring the existing _in_link mechanism. visit_term sets _in_term=True / _term_has_content=False; depart_term clears both. visit_Text gained an _in_term elif branch (lowest priority, after in_desc_parameter/_in_link so nested link/desc win) that inserts ' + ' when _term_has_content, and sets _term_has_content=True after emitting. visit_literal — which previously participated in NO concat context — gained the same _in_term separator+tracking. Result: adjacent term inline expressions emit raw("make.bat") + text(" and ") + raw("Makefile"); single-node terms emit cleanly (no leading/trailing +); the definition (2nd arg, par({...}) markup) is untouched.
verification: Minimal fixture emits the + form and compiles to %PDF; new tests/test_deflist_term_concat_render_gate.py PASSES with fix and FAILS pre-fix with the exact 'expected comma' fatal (both directions via git stash). Fast suite 397 passed / 15 deselected (no expectation updates needed — existing term tests use single-node terms + substring asserts). black/ruff/mypy clean. Corpus gate advanced past getting-started.typ:127 comma fatal; now RED on a DISTINCT block-level fatal (bug #4): changes/1.6.typ:856 `})par(` — a nested list(...) immediately followed by par(...) with no separator → 'expected semicolon or line break' (17 juxtapositions across 8 files). Reported, not fixed (bounded scope, fix_requirements #5).
files_changed: [typsphinx/translator.py, tests/test_deflist_term_concat_render_gate.py, tests/fixtures/deflist_term_concat_render_gate/conf.py, tests/fixtures/deflist_term_concat_render_gate/index.rst]
