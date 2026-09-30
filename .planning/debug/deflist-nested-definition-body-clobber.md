---
status: resolved
trigger: "GATE-02 corpus fatal #18: TypstError: label `<sphinx.domains.Domain>` does not exist. autoclass Domain whose docstring begins with a nested definition list; single-slot saved_body/current_term_buffer/current_definition_buffer clobbered by the inner list, dropping the outer definition's content + the desc_signature anchor."
created: 2026-07-12
updated: 2026-07-12
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "visit_term/visit_definition save the main body through the SINGLE-SLOT self.saved_body (and single-slot current_term_buffer / current_definition_buffer). When a definition list is NESTED inside a definition, the inner list's visit_term/visit_definition overwrites all three single slots. On the outer depart_definition, saved_body is None (restore skipped -> self.body left pointing at the orphaned inner buffer), current_definition_buffer is None (content read as ''), and current_term_buffer is None (pairing skipped). The outer definition's content AND any body written afterward (e.g. a desc_signature + its <id> anchor) are silently dropped, so link(<sphinx.domains.Domain>) dangles -> semantic fatal."
  confirming_evidence:
    - "translator.py:1556/1615 both write the SAME self.saved_body slot; :1594/1632 restore is guarded by `if self.saved_body is not None`, so a nested clobber (which sets it None on the inner depart) makes the outer restore a no-op."
    - "translator.py:1616 sets self.current_definition_buffer to a NEW list and :1643 sets it None; a nested definition therefore orphans the outer buffer reference, and :1629 reads the (now None) slot -> ''."
    - "translator.py:1557/1603/1641 make current_term_buffer single-slot; a nested visit_term (:1557) overwrites the outer pending term before the outer depart_definition (:1637) pairs it."
    - "definition_list_items (:1413/1454) is reset by the nested visit_definition_list, and in_definition_list (:1424) is reset False by the inner depart -- both single-slot."
  falsification_test: "Trace a doubly-nested definition list AND a desc whose content begins with a nested def list through the stack-ified code; if outer content + anchor survive in emitted .typ and the corpus label resolves, hypothesis holds. If content still drops, hypothesis is wrong."
  fix_rationale: "Stack-ify every single-slot piece of term/definition state (body save, pending term, per-list item collection) exactly like bug #4 _list_item_stack and bug #5 _inline_concat_stack. Read the definition content from self.body (restored by the balanced body stack) instead of the clobberable current_definition_buffer slot. Each nesting level then saves/restores its own level; nothing is orphaned."
  blind_spots: "Block separation between a leading paragraph and a nested terms(...) inside one definition (must stay newline-separated for _wrap_definition_arg's {..}); interaction with in_list_item separator when the whole def list sits in a bullet item."

## Symptoms

expected: "Sphinx doc/ corpus compiles end-to-end through -b typstpdf; class Domain's signature + <sphinx.domains.Domain> anchor emitted; :class:/param-type xref resolves."
actual: "typst.compile() aborts: TypstError: label `<sphinx.domains.Domain>` does not exist in the document. Outer definition content + desc_signature anchor silently dropped."
errors: "TypstError: label `<sphinx.domains.Domain>` does not exist in the document"
reproduction: ".. module:: sphinx.domains + .. autoclass:: Domain (docstring begins with nested definition list), referenced as Index(domain: Domain) and via :class:. Corpus gate: tests/test_corpus_gate.py::TestCorpusRenderGate."
started: "Exposed after bug #17 (desc_signature anchor) unblocked the parse+first-semantic path."

## Eliminated

- hypothesis: "Anchor-emission gap on desc_signature (bug #17)."
  evidence: "The anchor IS emitted by depart_desc_signature; a body-id trace showed signature+anchor appended to self.body then orphaned by the term/definition buffer swap. The NAME is dropped too, not just the anchor -> this is a buffer-management bug, distinct from #17."
  timestamp: 2026-07-12

## Evidence

- timestamp: 2026-07-12
  checked: "grep of saved_body/current_term_buffer/current_definition_buffer/definition_list_items in translator.py"
  found: "All are single-slot; visit_term(:1556) and visit_definition(:1615) write the same self.saved_body; nested lists clobber each. Local `saved_body` at :1853 is an unrelated footnote local."
  implication: "Nested definition list inside a definition orphans the outer body -> content + anchor dropped."

## Resolution

root_cause: "Single-slot self.saved_body (+ current_term_buffer, current_definition_buffer, definition_list_items, in_definition_list) are not re-entrant; a definition list NESTED inside a definition clobbers all of them, dropping the outer definition's content and any body written afterward (the desc_signature + its <id> anchor), which dangles the cross-reference link."
fix: "Stack-ify: _saved_body_stack (push in visit_term/visit_definition, pop in depart), _pending_term_stack (capture pending term in visit_definition), _deflist_items_stack (per-list item collection; definition_list_items aliases the top). depart_definition reads content from self.body (restored by the balanced stack), not the clobberable slot."
verification: "Fast regression test tests/test_deflist_nested_definition_render_gate.py FAILS pre-fix (TypstError: label <WidgetGamma> does not exist; PREDEF_SENTINEL + Configuration term dropped) and PASSES post-fix (both sentinels survive, anchor+link resolve, %PDF). Fast suite: 420 passed, 15 deselected. black/ruff/mypy clean. Corpus gate: bug #18 fatal (<sphinx.domains.Domain> does not exist) is GONE; corpus advances to next distinct fatal (bug #19): TypstError: label <module-sphinx.ext.apidoc> occurs multiple times (duplicate anchor -- mirror of #17/#18)."
files_changed: [typsphinx/translator.py, tests/test_deflist_nested_definition_render_gate.py, tests/fixtures/deflist_nested_definition_render_gate/conf.py, tests/fixtures/deflist_nested_definition_render_gate/index.rst]
next_fatal: "TypstError: label `<module-sphinx.ext.apidoc>` occurs multiple times in the document. Construct: `.. py:module:: sphinx.ext.apidoc` (usage/extensions/apidoc.rst:6). A module-target id is emitted as a `<label>` anchor definition more than once in the compiled master. Mirror of #17/#18 (duplicate, not missing). Isolated single-doc/toctree/real-file reproductions all compile -- the 2nd emission arises only under the full corpus conf.py, so bug #19 needs its own session. Fix direction: dedupe emitted `<label>` anchor definitions per compiled master."
