---
status: resolved
trigger: "Corpus gate fatal #6: TypstError: expected comma at latex.typ:1507 (source: latex.rst:1131+). Root cause pre-diagnosed by prior debug pass: TypstTranslator has NO visit_substitution_definition. The node falls through to unknown_visit (logs a warning but does not skip), so its inline literal/text children get emitted at document TOP LEVEL as juxtaposed code-mode expressions (raw(...)raw(...)... ~57 stacked) -> Typst syntax error."
created: 2026-07-12T00:00:00
updated: 2026-07-12T00:00:00
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "TypstTranslator has no visit_substitution_definition method. substitution_definition nodes (from rST `.. |name| replace:: <content>`) fall through SphinxTranslator's dispatch to unknown_visit, which logs a warning but does NOT raise SkipNode/SkipChildren -- so the translator continues descending into the node's inline children (literal/text) and emits them via the normal visit_literal/visit_Text paths at whatever buffer context is currently active (document top level, since substitution_definition is a direct child of the document/section). Multiple substitution definitions in the same document produce N adjacent top-level code-mode expressions with no separator -> 'expected comma' (the def-list-term/target adjacency bug family, bug #6 in this campaign)."
  confirming_evidence:
    - "grep -n 'substitution' typsphinx/translator.py returns ZERO visit_/depart_ hits -- confirmed no handler exists for this node type."
    - "Sibling patterns in translator.py: visit_comment (line 564-577) raises bare nodes.SkipNode for another non-rendering node class, with no depart_ needed (SkipNode skips descent into children entirely)."
    - "docutils.nodes.substitution_definition IS a non-rendering node by design: its content is injected at substitution_reference use-sites by docutils' Substitutions transform BEFORE the writer ever runs; the definition node itself carries no visual content of its own. Sphinx's own HTML (SkipNode) and LaTeX (SkipNode) writers both skip it identically."
  falsification_test: "If, after adding visit_substitution_definition raising nodes.SkipNode, a fixture with a substitution definition (adjacent inline children in the replacement) plus a body paragraph using |name| STILL emits juxtaposed raw()/text() at top level, OR the substitution's replacement text stops appearing at the use site, the hypothesis is wrong."
  fix_rationale: "Add exactly one visit_substitution_definition(self, node) raising nodes.SkipNode, matching the visit_comment sibling pattern (non-rendering node, no depart_ needed since SkipNode prevents descent). This addresses the ROOT cause (missing handler causes fallthrough to unknown_visit, which is documented to warn-not-skip) rather than a symptom (e.g. patching the adjacency at the emission site would not fix the spurious warning or the wasted-work descent)."
  blind_spots: "unknown_visit's exact non-skip behavior is inferred from the described symptom (children ARE emitted) rather than re-reading Sphinx/docutils' unknown_visit source directly in this pass -- treated as already-confirmed by the prior debug pass per task framing. substitution_reference (the USE site) is a distinct, already-functioning node type (resolved to normal inline nodes by docutils' transform before the writer runs) and is out of scope for this fix."

hypothesis: CONFIRMED (see reasoning_checkpoint)
test: add visit_substitution_definition raising nodes.SkipNode near visit_comment; add fast offline regression fixture+test; rerun fast suite + lint + corpus gate
expecting: fixture compiles to %PDF with no 'expected comma'/TypstCompilationError; no top-level juxtaposed raw()raw() from the definition; substitution's replacement text appears at the |things| use site; corpus advances past latex.typ:1507
next_action: Add the visit_substitution_definition method in typsphinx/translator.py near visit_comment; create fixture project + test module; run fast suite/lint/mypy; rerun corpus gate.

## Symptoms

expected: Sphinx doc/ corpus compiles through -b typstpdf with no fatal TypstCompilationError; a `.. |name| replace:: ...` substitution definition produces NO output of its own, while `|name|` uses elsewhere in the body render the replacement content.
actual: "TypstError: expected comma" at latex.typ:1507 (source: latex.rst:1131+) -- substitution_definition nodes fall through to unknown_visit (warns, does not skip) and their inline literal/text children are emitted at document top level as ~57 stacked juxtaposed code-mode expressions with no separator.
errors: "error: expected comma\n   |-- latex.typ:1507   (source: latex.rst:1131+)"
reproduction: uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s
started: Pre-existing bug surfaced by Phase 15 corpus gate, after bugs #1-#5 (asset copy, target label, def-list-term concat, list-item nested-block adjacency, string-literal escape/target-label) were fixed and the compile path advanced further into the real doc/ corpus.

## Eliminated

## Evidence

- timestamp: initial
  checked: grep -n "substitution" typsphinx/translator.py
  found: zero visit_*/depart_* hits for substitution_definition or substitution_reference.
  implication: confirms no handler exists; node falls through SphinxTranslator dispatch to unknown_visit.

- timestamp: initial
  checked: typsphinx/translator.py lines 564-589 (visit_comment/depart_comment)
  found: visit_comment raises bare nodes.SkipNode with a one-line docstring explaining it's a non-rendering node; depart_comment is a documented no-op (never called, SkipNode prevents descent).
  implication: this is the established sibling pattern for non-rendering nodes in this file -- placing visit_substitution_definition alongside it (no depart_ needed) matches existing conventions.

## Evidence (continued)

- timestamp: pre-fix-repro
  checked: manual scratch fixture (.. |things| replace:: ``a``, ``b``, ``c`` + a use paragraph), built via sphinx-build -b typst / -b typstpdf against the unmodified translator
  found: -b typst emits "WARNING: unknown node type: <substitution_definition ...>" and the .typ contains raw("a")text(", ")raw("b")text(", ")raw("c") at document top level immediately preceding the next block's par(. -b typstpdf fails with "TypstError: expected semicolon or line break" (same syntax-error class as the corpus's "expected comma" -- both are "two adjacent expressions with no separator", differing only in exact Typst parser message by context).
  implication: hypothesis confirmed empirically before the fix was applied.

- timestamp: fix-applied
  checked: added visit_substitution_definition raising nodes.SkipNode near visit_comment (typsphinx/translator.py); rebuilt the same scratch fixture
  found: no unknown_visit warning; .typ no longer contains the definition's raw()/text() calls at all (fully skipped, no depart_ needed); the use site (|things| in the paragraph) still emits raw("a")\ntext(", ")\nraw("b")\ntext(", ")\nraw("c") correctly (its own resolved inline nodes, untouched by this fix); -b typstpdf succeeds and produces a valid %PDF.
  implication: fix confirmed working; definition emits nothing, use site still resolves and renders.

- timestamp: regression-test-both-directions
  checked: tests/test_substitution_definition_render_gate.py (new fixture with 3 adjacent literal children in the definition + a use site) run with fix applied and with typsphinx/translator.py git-stashed back to pre-fix
  found: PASSES with the fix (no warning, no fatal signature, %PDF produced, each of the 3 literal tokens appears exactly once in extracted PDF text at the use site). FAILS pre-fix with the exact 'unknown node type: <substitution_definition ...>' warning AND 'TypstError: expected semicolon or line break' fatal.
  implication: regression test correctly reproduces and locks the fix, both directions confirmed.

- timestamp: full-suite-and-lint
  checked: uv run python -m pytest (fast suite, 4 environmentally-bad integration files ignored, -m "not slow"); uv run black --check; nix-shell -p ruff --run "ruff check"; uv run mypy typsphinx/ -- all on the changed files
  found: 407 passed, 15 deselected (no regressions, no expectation updates needed). black initially flagged the new method signature line (>88 cols) -- reformatted to black's 3-line form, all clean after. ruff and mypy clean throughout.
  implication: fix + new test are lint/format/type clean and introduce no regressions.

- timestamp: corpus-gate-rerun
  checked: uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s (real network, cached clone at ~/.cache/typsphinx-corpus-gate/)
  found: GATE-02 advanced past the substitution_definition fatal (no more latex.typ:1507 'expected comma' from this construct) but is STILL RED on a NEW, DISTINCT fatal (bug #7, out of this session's bounded scope): "TypstError: expected comma", first at usage/restructuredtext/directives.typ:1718:237 (compiled .typ location; corresponds to the `.. index::` directive's multi-entry description list in usage/restructuredtext/directives.rst). Reproduced the precise diagnostic by rebuilding the corpus with `-b typst` and calling `typst.compile()` directly on the emitted index.typ to capture typst's full source-span diagnostic (typst-py's TypstCompilationError message alone is just "expected comma" with no location -- the richer span/trace info is on the underlying typst.TypstError's `.diagnostic` attribute).
  implication: substitution_definition fix confirmed complete and correct; a separate, unrelated pre-existing bug blocks the NEXT stage of GATE-02. Reported precisely below per bounded-scope discipline (fix_requirements #4) -- NOT fixed in this session.

## Next Distinct Fatal (bug #7, reported not fixed -- bounded scope)

- **File:line:col (compiled .typ):** `usage/restructuredtext/directives.typ:1718:237`, with at least 12 further cascading "expected comma" locations in the SAME file/construct as typst's parser recovers and re-fails (1720:26, 1724:3, 1738:148, 1740:26, 1743:3, 1749:159, 1751:26, 1754:3, 1762:128, 1764:26, 1767:3, 1783:11, 1786:59, ...). Source: `usage/restructuredtext/directives.rst` (the `.. index::` directive's field-type description list, rendered by Sphinx as a `definition_list`).
- **TypstError:** `expected comma`.
- **Construct:** `terms.item(TERM, DEFINITION)` where the definition-list item's DEFINITION contains MULTIPLE block-level children (a paragraph, then a `literal_block` code example rendered as `codly(...)` + a ` ```rst...``` ` fence, then a `bullet_list`, sometimes another trailing paragraph). `visit_definition`/`depart_definition` (translator.py ~1481-1520) buffers ALL child output via simple string concatenation of each child's independently-emitted Typst source (each child's own `add_text()` calls, separated only by the blank lines each visitor already emits -- the same "sequential statement" style that is valid at the document's own top level, inside its outer `#{ ... }` code block). `depart_definition` then passes that raw multi-statement blob, UNWRAPPED, straight in as the second positional argument to `terms.item(term, definition)`. Typst requires a function argument to be a single value; multiple bare statements separated only by blank lines are not one argument -- the parser consumes the first statement (`par({...})`) as the complete argument, then expects a comma before the next token, finds the next statement's function call instead (`codly(...)`, a `\`\`\`` fence, `list({...})`, etc.) -> "expected comma", repeatedly, for every block boundary inside every multi-block definition in the file.
- **One-line hypothesis:** `depart_definition` needs to wrap the concatenated multi-block buffer in a single content-producing value (e.g. a `{ ... }` code block, which Typst auto-joins sequential content statements into one content value -- the same mechanism the top-level document already relies on) before passing it as `terms.item`'s second argument, instead of passing the raw concatenated-statements string directly.
- **Occurrence/file count (rough, bounded-scope estimate):** at least 13 distinct "expected comma" parse-error locations within this ONE file/construct alone (typst's error recovery kept re-triggering within the same `terms(...)` call across all its `terms.item(...)` entries). As an upper-bound proxy across the corpus: 20 compiled `.typ` files contain at least one `terms.item(` call, of which 16 also contain a code-fence marker ` ``` ` (glossary.typ, faq.typ, latex.typ, development/tutorials/autodoc_ext.typ, extdev/logging.typ, development/html_themes/templating.typ, internals/contributing.typ, man/sphinx-build.typ, tutorial/deploying.typ, usage/extensions/apidoc.typ, usage/theming.typ, tutorial/getting-started.typ, usage/extensions/autodoc.typ, usage/restructuredtext/field-lists.typ, usage/configuration.typ, usage/restructuredtext/directives.typ) -- a plausible but unconfirmed set of at-risk files for the same multi-block-definition class (not individually verified further, per bounded scope).
- **NOT fixed in this session.**

## Resolution

root_cause: TypstTranslator has no visit_substitution_definition handler. docutils.nodes.substitution_definition is a non-rendering node (content injected at substitution_reference use-sites by a pre-writer transform) but with no handler it falls through to unknown_visit, which logs a warning without skipping -- so the translator descends into and emits the definition's inline literal/text children via the normal visit_literal/visit_Text paths at document top level. Multiple such nodes/children in one document produce N adjacent top-level code-mode expressions with no separator, a Typst syntax error ("expected comma" in the corpus; "expected semicolon or line break" in the isolated fixture -- same adjacency class, different exact message by surrounding context).
fix: Added `visit_substitution_definition(self, node)` raising `nodes.SkipNode`, placed immediately after `depart_comment` (mirroring the `visit_comment` sibling non-rendering-node pattern; no `depart_` needed since SkipNode prevents descent into the definition's children entirely).
verification: tests/test_substitution_definition_render_gate.py PASSES with the fix, FAILS pre-fix with the exact warning+fatal (both directions confirmed via git stash). Manual scratch-fixture repro confirmed the mechanism directly before writing the automated test.
files_changed: [typsphinx/translator.py, tests/test_substitution_definition_render_gate.py, tests/fixtures/substitution_definition_render_gate/conf.py, tests/fixtures/substitution_definition_render_gate/index.rst]
