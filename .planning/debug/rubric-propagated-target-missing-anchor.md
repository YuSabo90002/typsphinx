---
status: resolved
trigger: "TypstError: label `<man_u2f_sphinx-build:makefile-options>` does not exist in the document (23rd corpus fatal, GATE-02) — explicit-target-before-`.. rubric::` propagated id on the rubric node; plus exhaustive body/container-visitor anchor sweep to end the missing-anchor sub-class."
created: 2026-07-13
updated: 2026-07-13
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "A whole sub-class of body/container visitors never emit (or emit a BROKEN) <label> anchor for node['ids'] that docutils' PropagateTargets (or an explicit :label:/:name:) places on them. visit_rubric (the #23 fatal), visit_container, visit_compound, visit_glossary, visit_transition, topic-contents branch emit NO anchor -> dangling 'does not exist'. visit_figure anchors only ids[0], leaving propagated ids[1:] dangling. visit_literal_block(:name:/propagated) and visit_math_block(:label:/propagated) emit a ` <label>` POSTFIX on a code-mode raw/math expression -> 'cannot join content with label' / 'expected semicolon or line break'. The reference side ALWAYS resolves to the docutils ID (refid), so anchoring node['ids'] via the proven _emit_id_anchors ([#metadata(none) <id>] markup block) fixes every case and byte-matches the link."
  confirming_evidence:
    - "Probe: `<rubric ids='my-rubric-target'>`; typ has link(<index:my-rubric-target>) + NO anchor; compile aborts 'label <index:my-rubric-target> does not exist'."
    - "Probe (same harness): container/transition/compound/glossary all dangle identically; figure `ids='figowncaption my-fig-target'` anchors figowncaption(ids[0]) but my-fig-target(ids[1]) dangles; literal_block/math_block emit broken ` <label>` postfix (proven compile errors)."
    - "Byte-compat probe: captioned code-block CONTAINER carries auto ids='id1' with NO names; plain compound/glossary/transition carry NO ids. => guard container on node.get('names'); others unguarded no-op."
    - "Ref resolves to ID: captioned :name: -> `<reference refid='my-fancy-label'>` == the id, not the name. Corpus has doc/usage/domains/mathematics.rst:17 `:label: euler` -> math_block IS reached."
  falsification_test: "If any fixed visitor already emitted a matching [#metadata(none) <namespaced-id>] anchor, the pre-fix probe would have found it -> it found ONLY the dangling link. If the fix were wrong-target, anchor-name != link-name and the regression test's dangling-set assertion would fail."
  fix_rationale: "Route node['ids'] through the shared _emit_id_anchors helper (proven byte-unchanged for empty ids in #20/#22). Add a skip_ids param so visit_figure anchors ids[1:] without double-defining its own ids[0] postfix. Replace the two BROKEN ` <label>` postfixes (literal_block, math_block) with the clean markup-block anchor form (joins cleanly, matches ref). Guard visit_container on names so the auto-id captioned-block case stays byte-unchanged."
  blind_spots: "sidebar/system_message/productionlist/compact_paragraph have NO visitor (hit unknown_visit) -> cannot add an anchor without a new handler; out of additive scope, noted. math_block loses lexical label-on-equation attachment (equation numbering) but that path did not compile before, so no functional regression. Verified via full fast suite + corpus gate."
test: "Implement all edits; probe-compile each construct to %PDF; add fast regression test(s); full fast suite; lint/type; re-run corpus gate."
expecting: "Every probed construct compiles to %PDF; anchor-name == link-name; no dangling/double-define; fast suite green (math substring tests still pass); corpus advances past #23 (GATE-02 green or next distinct fatal)."
next_action: "Edit _emit_id_anchors (add skip_ids) then the 9 visitor sites."

hypothesis: CONFIRMED (see reasoning_checkpoint above)

## Symptoms

expected: "sphinx-build -b typstpdf on Sphinx's real doc/ corpus, then typst.compile() on the master, produces %PDF with no fatal (GATE-02)."
actual: "TypstError: label `<man_u2f_sphinx-build:makefile-options>` does not exist in the document"
errors: "TypstError: label `<man_u2f_sphinx-build:makefile-options>` does not exist in the document"
reproduction: "uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow; or minimal: `.. _target:` immediately before `.. rubric:: Title`, plus `:ref:`target`` in same doc"
started: "shadowed by fatals #17-#22; surfaced after those fixed (predecessor desc-container-propagated-target.md identified this as fatal #23)"

## Eliminated

## Evidence

- timestamp: 2026-07-13
  checked: "Doctree + typ + typst.compile for `.. _t:` before `.. rubric::` (index docname)"
  found: "doctree `<rubric ids='my-rubric-target' names='my-rubric-target'>`; typ has `link(<index:my-rubric-target>)` but NO anchor; compile aborts `label <index:my-rubric-target> does not exist`."
  implication: "CONFIRMED rubric root cause. Fix: visit_rubric -> _emit_id_anchors(node) first."
- timestamp: 2026-07-13
  checked: "Same probe across container, transition, compound, glossary, figure, literal_block(:name:), literal_block(propagated)"
  found: "ALL broken. container/transition/compound/glossary -> dangling 'does not exist'. figure `<figure ids='figowncaption my-fig-target'>` -> ids[0] self-anchored via `) <label>]`, ids[1:] propagated DANGLES. literal_block(:name: and propagated) -> emits ` <label>` postfix on code-mode ``` block -> 'cannot join content with label' (PRE-EXISTING, also anchors NAME not ID). Captioned :name: puts id on `literal-block-wrapper` CONTAINER (child literal_block has no ids); container reads child's empty names -> dangling."
  implication: "Whole missing-anchor sub-class confirmed empirically. Ref ALWAYS resolves to the docutils ID (refid='my-fancy-label'), never the name."
- timestamp: 2026-07-13
  checked: "Byte-compat: captioned code-block w/o :name: (numfig on/off); plain toctree compound / glossary / transition"
  found: "Captioned code-block CONTAINER carries auto `ids='id1'` with NO names (both numfig settings). Plain compound/glossary/transition carry NO ids at all."
  implication: "Blanket-anchoring visit_container would churn EVERY captioned block (auto id1, unreferenced). Guard container on `node.get('names')` (referenceable target signal) -> byte-unchanged for auto-id case. compound/glossary/transition can be unguarded (no auto-ids)."
- timestamp: 2026-07-13
  checked: "math_block labeled equation (:label: myeq) and propagated target before .. math::"
  found: "BOTH broken: `mitex(...) <index:equation-myeq>` -> compile 'expected semicolon or line break'. Same broken-postfix class as literal_block. doctree ids=equation-myeq (labeled) / mymath-target+names (propagated)."
  implication: "math_block is another member of the class (pre-existing labeled-equation bug). Fix with clean anchor form IF existing math tests permit; else scope-check via corpus."

## Resolution

root_cause: "PropagateTargets (and explicit :name:/:label:) place an id on a body/container node whose visitor never emitted a matching <label> anchor, or emitted a BROKEN one. #23 fatal: visit_rubric. Corpus then surfaced #24: propagated target BETWEEN bullet items lands on the list_item node (visit_list_item unanchored)."
fix: "Exhaustive sweep via shared _emit_id_anchors helper. NEW anchor calls added to: visit_rubric, visit_container (guarded on names -> auto-id captioned blocks byte-unchanged), visit_compound, visit_glossary, visit_transition, visit_topic (contents branch), visit_list_item, and depart_figure (skip_ids={ids[0]} so propagated ids[1:] anchor without double-defining the figure's own postfix anchor). REPLACED two broken ` <label>` postfixes with the clean [#metadata(none) <id>] form: visit_literal_block/depart_literal_block (:name:/propagated -> 'cannot join content with label', also anchored name not id) and visit_math_block (:label:/propagated -> 'expected semicolon or line break'). Helper gained an optional skip_ids param (byte-compatible restructure). Already-covered (verified): paragraph, bullet_list, enumerated_list, definition_list, table, image, block_quote, line_block, all admonition variants (via _visit_admonition), non-contents topic, desc, desc_signature. No-visitor nodes (unknown_visit): sidebar/system_message/productionlist/compact_paragraph -> out of additive scope (noted)."
verification: "Probe-compiled every construct to %PDF (rubric/container/transition/compound/glossary/figure/literal_block(:name: & propagated)/captioned-container/math(labeled & propagated)/list_item) -- 0 dangling, 0 double-define, byte-compat confirmed for auto-id captioned blocks & plain compound/glossary/transition. New tests/test_rubric_propagated_target_render_gate.py PASSES post-fix, FAILS pre-fix (both directions; pre-fix fatal 'expected semicolon or line break'). Updated existing test_code_block_with_name_only -> id-based joinable anchor. Fast suite 425 passed / 15 deselected (424 prior + 1 new regression; 1 existing expectation updated: test_code_block_with_name_only). black/ruff/mypy clean. Corpus gate: #23 rubric RESOLVED, advanced to #24 list_item (FIXED in same sweep), advanced to #25 = DISTINCT CLASS (NOT missing-anchor): TypstError label `<usage_u2f_extensions_u2f_example_google:example-google>` does not exist -- a :ref: from an INCLUDED doc (napoleon.rst:201-202) to a section in an :orphan: doc (usage/extensions/example_google.rst:3, example_numpy.rst:3) that is EXCLUDED from the master #include() tree. Section anchoring itself is CORRECT (depart_title anchors all ids); the anchor is simply never emitted into the master because the orphan doc is not included. 3 orphan docs, 2 triggering cross-refs. STOPPED per bounded-discipline (different class). GATE-02 NOT green; #25 out of this session's missing-anchor scope."
files_changed: [typsphinx/translator.py, tests/test_translator.py, tests/test_rubric_propagated_target_render_gate.py, tests/fixtures/rubric_propagated_target_render_gate/conf.py, tests/fixtures/rubric_propagated_target_render_gate/index.rst, tests/fixtures/rubric_propagated_target_render_gate/img.png]
