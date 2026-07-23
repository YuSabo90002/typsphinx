# Sphinx configuration for the GATE-01 missing/malformed-master must-fail
# regression gate (Phase 22.3, WR-01, D-11).
#
# This is the suite's FIRST fixture that deliberately encodes BAD
# configuration: the build below is EXPECTED to fail with a non-zero exit.
# Every other GATE-01 fixture in this suite proves a real compile succeeds;
# this one proves that TypstPDFBuilder.finish() (typsphinx/builder.py) now
# fails loudly instead of silently skipping a broken master (WR-01).
#
# `typst_documents` holds exactly three entries, and their ORDER is
# load-bearing -- the aggregate ExtensionError renders failures in
# typst_documents iteration order (D-02's ordering guarantee), so the two
# bad entries below must stay in this relative order for the gate's
# ordering assertions to hold:
#
#   1. ("index", "index", project, author) -- the ONE VALID master. Its
#      .typ is generated and it must still produce index.pdf even though
#      the build overall fails -- D-02's attempt-all-then-raise contract.
#   2. ("ghost", "ghost", project, author) -- a docname that is
#      deliberately NOT a real Sphinx document in this project. There is
#      no ghost.rst file anywhere in this fixture and "ghost" is never
#      referenced by any toctree. That absence from self.env.found_docs is
#      precisely what this gate measures (D-04's found_docs-discriminating
#      branch) -- do not ever add a ghost.rst file or a toctree entry for
#      it, or this condition stops being exercised.
#   3. () -- a malformed empty entry, exercising the D-05/D-07 branch,
#      reported by repr(doc_tuple) in the aggregate message.
#
# The fixture also contains a SECOND, non-master document (chapter1.rst,
# reached from index.rst's toctree and deliberately absent from the list
# below). Writing it forces TypstWriter._is_master_document("chapter1") to
# scan this whole list without matching, so the scan reaches the malformed
# () entry -- the condition behind code-review finding CR-01. Keep
# chapter1.rst out of typst_documents; adding it would make the scan match
# early and silently stop exercising that path.
#
# No other typst_* config value is set here -- in particular, no
# typst_template, no typst_package, and no typst_template_function. The
# valid master must compile through the bundled default template so this
# stays a pure WR-01 gate and cannot go red because of an unrelated
# template or package interaction.

project = "Missing and Malformed Master Gate"
author = "Test Author"
release = "1.0.0"
copyright = "2026, Test Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "index", project, author),
    ("ghost", "ghost", project, author),
    (),
]
