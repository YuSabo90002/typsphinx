---
status: fixing
trigger: "TypstError: label `<xref-modifiers>` does not exist in the document (20th corpus fatal, GATE-02)"
created: 2026-07-12
updated: 2026-07-12
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "docutils PropagateTargets moves an explicit `.. _target:` id onto the following body element's node['ids']; visit_paragraph emits par({...}) but never reads node['ids'], so no <label> anchor is emitted, while a same-doc :ref: emits link(<id>) → dangling label → compile fatal."
  confirming_evidence:
    - "Probe: paragraph 'The behavior can be modified...' carries ids=['my-para-target']"
    - "Probe: emitted .typ has NO '[#metadata(none) <my-para-target>]' anchor, but DOES have 'link(<my-para-target>, '"
    - "Corpus: .. _xref-modifiers: (referencing.rst:24) precedes a paragraph (line 26); :ref:...<xref-modifiers> at 257"
  falsification_test: "If visit_paragraph already emitted the anchor, the probe would find the anchor-form present — it does not."
  fix_rationale: "Emit the proven [#metadata(none) <id>] anchor (bug #2 form) via _sanitize_label (bug #10) for every id on the paragraph, at paragraph block level, so the anchor byte-matches the link() reference and resolves."
  blind_spots: "Other body elements (list/table/image/admonition/line_block/literal_block/deflist) can also receive propagated ids and emit no anchor — audited empirically."

## Symptoms

expected: "typst.compile() on corpus doc/ produces %PDF"
actual: "TypstError: label `<xref-modifiers>` does not exist in the document"
errors: "label `<xref-modifiers>` does not exist"
reproduction: "sphinx-build -b typstpdf on corpus; or minimal: target before paragraph + same-doc :ref:"
started: "shadowed by earlier fatals #17/#18/#19; surfaced after those fixed"

## Resolution

root_cause: "PropagateTargets propagates explicit-target id onto following paragraph node['ids']; visit_paragraph emits no anchor for node['ids']"
fix: "visit_paragraph + audited body-element visitors emit [#metadata(none) <sanitized-id>] via shared _emit_id_anchors helper"
verification: "compile-probe: paragraph/bullet_list/enumerated_list/table/image/note/line_block/definition_list/block_quote all yield %PDF, anchor==link resolved. figure+literal_block DEFERRED (figure self-anchors caption-id not propagated-id; literal_block has PRE-EXISTING :name: join bug, confirmed on HEAD)."
files_changed: [typsphinx/translator.py]
