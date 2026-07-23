---
status: resolved
trigger: "TypstError: label `<man_u2f_sphinx-build:make-mode>` does not exist in the document (22nd corpus fatal, GATE-02) — explicit-target-before-object-description propagated id on the `desc` container node"
created: 2026-07-12T23:53:51+09:00
updated: 2026-07-12T23:57:00+09:00
resolution: "#22 desc-container propagated-target class FIXED (commits pending below). Corpus advanced past fatal #22 to next DISTINCT fatal #23: explicit-target-before-`.. rubric::` (different node type, different fix site -- visit_rubric, not visit_desc). NOT GATE-02 GREEN. Reported per bounded-discipline scope; #23 out of this session's scope."
---

## Current Focus

corpus_outcome: "GATE-02 NOT green. #22 desc-container-propagated-target class RESOLVED (man/sphinx-build.rst:33 `.. _make_mode:` before `.. option:: -M` now resolves; man/sphinx-quickstart.rst:127 cross-doc :ref: to it compiles). NEXT DISTINCT FATAL (#23): TypstError: label `<man_u2f_sphinx-build:makefile-options>` does not exist in the document. Construct: man/sphinx-build.rst:337 `.. _makefile_options:` immediately precedes `.. rubric:: Makefile Options` (NOT an object-description directive -- a `rubric` node). Referenced cross-doc-safely at man/sphinx-build.rst:49 `:ref:`Makefile or Make.bat <makefile_options>``. grep: `def visit_rubric`/`def depart_rubric` (translator.py ~4287/4299) do not call _emit_id_anchors -- same missing-anchor family (#2/#17/#20/#22), but a DISTINCT node type/fix site (visit_rubric, not visit_desc). Occurrence: 2 in corpus (man/sphinx-build.rst:337 `.. _makefile_options:`+rubric; usage/restructuredtext/directives.rst:483 `.. _collapsible-admonitions:`+rubric) -- confirmed via corpus-wide scan for `.. _target:` immediately followed by `.. rubric::`."

reasoning_checkpoint:
  hypothesis: "docutils PropagateTargets moves the `.. _make_mode:` explicit-target id onto the FOLLOWING `.. option:: -M` object-description's outer `desc` node (not desc_signature, not index, not target). visit_desc is a no-op (`pass`) and depart_desc only appends spacing, so node['ids'] on the desc container is never read/anchored -- unlike desc_signature's OWN ids (bug #17) which desc_signature.ids anchors. A same-doc/cross-doc :ref: to that propagated id emits link(<namespaced-id>) with no matching anchor -> Typst semantic label-resolution fatal."
  confirming_evidence:
    - "XML doctree probe (`-b xml`) on `.. _my-opt-target:` + `.. option:: -M buildername`: emits `<desc ... ids=\"my-opt-target\" names=\"my-opt-target\" ...><desc_signature ... ids=\"cmdoption-M\">...`. The propagated id is on `desc`, a DIFFERENT id than desc_signature's own `cmdoption-M`."
    - "Control probe: plain `.. py:function:: foo(x)` + `.. option:: -M buildername` with NO preceding target -> both `<desc ...>` tags carry NO `ids` attribute at all (absent = empty list). Confirms desc.ids is normally empty; only becomes non-empty via PropagateTargets."
    - "grep translator.py: visit_desc = `pass`; depart_desc = `self.body.append(\"\\n\\n\")` only. No _emit_id_anchors call, no node['ids'] read anywhere in visit_desc/depart_desc."
  falsification_test: "If visit_desc already emitted an anchor for node['ids'], the XML-vs-typ diff would show a matching `[#metadata(none) <...:make-mode>]`. It does not (grep of emitted .typ for the corpus construct shows the id only inside link(...), never as an anchor)."
  fix_rationale: "Call the proven `_emit_id_anchors(node)` helper (bug #20) in `visit_desc`, mirroring its use in visit_bullet_list/visit_table/visit_block_quote/etc: at the very start of visit_desc, before any signature/content children are visited. Empty ids (the overwhelming common case) => no-op, byte-unchanged. Non-empty ids (this construct) => anchor emitted BEFORE desc_signature's own strong({...}) block, newline-separated -- structurally identical to the established container-anchor pattern, so no juxtaposition/stray-+ risk. Different id than desc_signature.ids (make-mode vs cmdoption-M) so no double-definition; _emit_id_anchors also dedupes defensively."
  blind_spots: "Assumes no OTHER existing desc-related test encodes a desc node with pre-existing non-empty ids and asserts a specific (anchorless) body string for it -- to verify via full fast-suite pass. Assumes _current_docname()/in_list_item bookkeeping works identically for desc as for other container types (same helper, same contract)."

hypothesis: CONFIRMED (see reasoning_checkpoint)
test: "Add self._emit_id_anchors(node) to visit_desc; add fast regression test (option directive + preceding target + :ref:); run fast suite; lint/type; re-run corpus gate."
expecting: "Regression fixture emits <docname:my-opt-target> anchor == link(<docname:my-opt-target>) ref; compiles to %PDF. Fast suite all-green. Corpus gate advances past fatal #22 to next distinct fatal or GATE-02 GREEN."
next_action: "Edit visit_desc (translator.py ~3931) to call self._emit_id_anchors(node) as first statement."

## Symptoms

expected: "sphinx-build -b typstpdf on Sphinx's real doc/ corpus, then typst.compile() on the master, produces %PDF with no fatal (GATE-02)."
actual: "TypstError: label `<man_u2f_sphinx-build:make-mode>` does not exist in the document"
errors: "TypstError: label `<man_u2f_sphinx-build:make-mode>` does not exist in the document"
reproduction: "uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s; or minimal: `.. _x:` immediately before `.. option:: --foo`, plus `:ref:`x`` in same doc"
started: "shadowed by fatals #17-#21; surfaced after those fixed (this session's predecessor, cross-document-label-collision-namespacing.md, identified this as fatal #22 in its corpus_outcome field)"

## Eliminated

## Evidence

- timestamp: 2026-07-12T23:53:51+09:00
  checked: "XML doctree (`-b xml`) for `.. _my-opt-target:` + `.. option:: -M buildername` + `:ref:`my-opt-target``"
  found: "`<desc ... ids=\"my-opt-target\" names=\"my-opt-target\" ...><desc_signature ... ids=\"cmdoption-M\">`. Propagated id lands on the desc CONTAINER node, not desc_signature/index/target."
  implication: "Confirms exact fix site: visit_desc must anchor node['ids'], distinct from desc_signature's own id-anchoring (bug #17)."
- timestamp: 2026-07-12T23:53:51+09:00
  checked: "XML doctree for plain `.. py:function:: foo(x)` + `.. option:: -M buildername` (no preceding target)"
  found: "Both `<desc ...>` tags carry NO ids attribute (absent/empty)."
  implication: "desc.ids is empty in the overwhelmingly common case; adding _emit_id_anchors(node) to visit_desc is byte-unchanged for all existing (non-propagated-target) desc/option/function tests."

## Resolution

root_cause: "docutils' PropagateTargets transform moves an explicit `.. _target:` id immediately preceding an object-description directive (e.g. `.. option::`) onto the OUTER `desc` CONTAINER node's ids -- a DIFFERENT id than the one desc_signature carries for itself (e.g. `make-mode` on `desc` vs `cmdoption-M` on `desc_signature`). visit_desc was a no-op (`pass`) and depart_desc only appended spacing (`\\n\\n`); neither read node['ids']. A same-doc/cross-doc :ref: to the propagated id renders `link(<namespaced-id>, ...)` with no matching anchor ever emitted, so typst.compile() aborted at the semantic label-resolution pass with 'label ... does not exist'. Confirmed via XML doctree probe (`-b xml`): normal desc nodes (no preceding target) carry NO ids attribute at all; only PropagateTargets makes it non-empty."
fix: "visit_desc now calls the shared _emit_id_anchors(node) helper (bug #20) as its first statement, mirroring its use in visit_bullet_list/visit_table/visit_block_quote/etc: anchor emitted BEFORE any signature/content children are visited. Empty ids (overwhelming common case) -> no-op, byte-unchanged (confirmed via control probe: plain `.. py:function::`/`.. option::` desc nodes carry no ids attribute). Non-empty ids (this construct) -> anchor emitted before desc_signature's own strong({...}) block, newline-separated, composing identically to the established container-anchor pattern -- no juxtaposition/stray-+ risk. Different id namespace-key than desc_signature.ids so no double-definition; _emit_id_anchors dedupes defensively regardless."
verification: "New tests/test_desc_container_propagated_target_render_gate.py PASSES with fix, FAILS pre-fix (git stash translator.py) with the exact 'label \\`<index:my-opt-target>\\` does not exist in the document' fatal (confirmed both directions). Asserts source-level: [#metadata(none) <index:my-opt-target>] anchor emitted, anchor-name == link(<index:my-opt-target> reference-name, no dangling same-doc links, control option (--bar, no preceding target) emits no spurious extra id, and index.pdf is a real non-empty %PDF. Manual minimal-repro probe (outside pytest) also confirmed both directions with typst.compile() directly. Fast suite: 424 passed, 15 deselected (423 prior + 1 new; NO existing expectation updated -- desc node ids were empty in every prior test, so the additive anchor call is byte-unchanged for all of them). black --check / ruff check / mypy clean on typsphinx/translator.py + new test file. Corpus gate: bug #22 FIXED -- corpus advances PAST the desc-container dangling label (man/sphinx-build.rst make-mode + man/sphinx-quickstart.rst cross-doc ref to it now resolve). NOT GATE-02 green. Next distinct fatal #23 = TypstError 'label \\`<man_u2f_sphinx-build:makefile-options>\\` does not exist' -- DISTINCT ROOT CAUSE/fix-site (visit_rubric, not visit_desc): `.. _makefile_options:` (man/sphinx-build.rst:337) precedes `.. rubric:: Makefile Options` (a rubric node, not an object-description). Occurrence: 2 in corpus (man/sphinx-build.rst:337, usage/restructuredtext/directives.rst:483). Reported per bounded-discipline scope, NOT fixed in this session."
files_changed: [typsphinx/translator.py, tests/test_desc_container_propagated_target_render_gate.py, tests/fixtures/desc_container_propagated_target_render_gate/conf.py, tests/fixtures/desc_container_propagated_target_render_gate/index.rst]
