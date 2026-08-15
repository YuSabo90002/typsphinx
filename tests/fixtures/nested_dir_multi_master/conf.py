# Sphinx configuration for the nested-dir-multi-master fixture.
#
# Positive successor to the former `template-named-dir-master` fixture
# (Phase 54 plan 07, OUT-07) -- see
# tests/fixtures/template_prefix_reservation_gate/conf.py for the
# negative successor that proves the OLD `_template`-named docname
# layout is now a build error, and for the full CR-01 history both
# successors share.
#
# What moved and why: the predecessor fixture's docname layout (a source
# subdirectory literally named `_template`) is now itself a build error
# under OUT-07's wholesale directory reservation, so this successor moves
# the SAME two docnames into a directory named `partials` instead
# (deliberately not the name Sphinx's own `templates_path` default uses)
# while keeping every OTHER regression property of the original fixture
# identical.
#
# BLD-02/OUT-01: two `typst_documents` entries against ONE docname tree,
# each with its own DISTINCT, bare (no path separator) target
# (`template-dir-master.typ`, `template-dir-sub.typ`). This is
# load-bearing, not a rename: OUT-01 makes a bare target resolve
# unconditionally at the outdir root, so if both entries shared one
# target (e.g. both "index"), the two wrappers would collide on one
# physical path (a BLD-02 duplicate-target error). The distinctness of
# these two target strings is what keeps this fixture buildable at all.
#
# CONF-09 (Phase 44.2, SC#3): the second entry's author deliberately
# diverges from the first ("Test Author (nested)" vs "Test Author") so a
# per-master author leak is detectable by
# tests/test_multi_master_metadata_no_leak.py -- both entries' titles
# already diverge (the title half of the leak was already detectable
# before Phase 44.2), but until Phase 44.2 both entries shared the SAME
# author, so an author leak between the two masters was undetectable.

project = "Template Named Dir Master"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# The depth-1 master is the project root, keeping nothing else at the
# outdir root that could mask the condition (mirrors
# tests/fixtures/nested_master_render_gate/conf.py's reasoning).
root_doc = "partials/index"

typst_documents = [
    (
        "partials/index",
        "template-dir-master.typ",
        "Template Named Dir Master",
        "Test Author",
    ),
    (
        "partials/sub/index",
        "template-dir-sub.typ",
        "Template Named Dir Master (nested)",
        "Test Author (nested)",
    ),
]
