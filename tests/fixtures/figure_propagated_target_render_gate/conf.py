"""Sphinx config for the figure propagated-target render-gate fixture.

Permanent D-09/D-10 regression gate (Phase 42, TBL-03). Exercises docutils'
``PropagateTargets`` transform via standalone ``.. _label:`` target
directives placed immediately before a ``.. figure::`` directive -- the same
mechanism that, on the TABLE side, drops the propagated id and aborts the
Typst compile with a dangling-label fatal (this phase's defect). This
fixture proves the figure path is unaffected: ``add_text`` consults only
``self.in_table`` (never ``self.in_figure``), so ``depart_figure``'s own
self-anchor postfix and its trailing ``_emit_id_anchors(node,
skip_ids={ids[0]})`` call both land in ``self.body`` directly, whether they
fire before or after ``self.in_figure`` is cleared.

Deliberately distinct from ``tests/fixtures/figure_target_caption_render_gate/``:
that fixture's figures carry the ``:target:`` DIRECTIVE OPTION, which docutils
wraps as a ``reference`` node around the figure (handled by
``visit_reference``/``depart_reference``) -- a completely different mechanism
that never invokes ``PropagateTargets``. This fixture contains no ``:target:``
option anywhere; only standalone ``.. _label:`` target directives are used, so
the propagated-target mechanism under test is the one actually exercised.

``numfig = True`` is set so the named shape's ``:numref:`` resolves.

Fully offline and text-only -- no intersphinx, no network.
"""

project = "Figure Propagated Target Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# index must be a master document so the writer emits the full template and
# TypstPDFBuilder.finish() calls typst.compile() -- without this the gate
# proves nothing (it would only emit .typ, never compile it).
typst_documents = [
    ("index", "index", "Figure Propagated Target Render Gate", "typsphinx tests"),
]

numfig = True
