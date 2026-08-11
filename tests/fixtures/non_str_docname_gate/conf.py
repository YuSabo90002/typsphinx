# Sphinx configuration for the BLD-01 non-str-docname must-fail regression
# gate (Phase 44, plan 44-02).
#
# This fixture deliberately encodes BAD configuration -- the build below is
# EXPECTED to exit non-zero. It proves that TypstPDFBuilder.finish()
# (typsphinx/builder.py) reports a non-str docname through the existing
# aggregate failures list instead of dying with a raw TypeError out of
# posixpath.dirname() (BLD-01).
#
# `typst_documents` holds exactly two entries, and their ORDER is
# load-bearing -- the aggregate ExtensionError renders failures in
# typst_documents iteration order, and the valid master must be attempted
# FIRST so the gate can assert it still compiles even though the build as a
# whole fails (D-02's attempt-all-then-raise contract, same as the sibling
# missing/malformed-master gate):
#
#   1. ("index", "master.typ", project, author) -- the ONE VALID master. Its
#      .typ is generated and it must still produce master.pdf even though
#      the second entry makes the build overall fail. Target renamed from
#      "index" to "master.typ": the stem "index" casefold-collided with the
#      docname's own content path "index.typ" (fixture de-collision rule,
#      47-EXPECTED-STRUCTURE.md).
#   2. (123, "manual.typ", "Bad Docname", author) -- BLD-01's exact trigger.
#      The docname is the integer 123, never a str. Do NOT "correct" 123
#      to a string -- the whole point of this fixture is that the guard
#      catches a non-str docname before it ever reaches
#      posixpath.dirname(). Left untouched by the de-collision rule: a
#      non-str docname has no content path to collide against, which is
#      exactly the guard this fixture proves.
#
# No other typst_* config value is set here -- in particular, no
# typst_template, no typst_package, and no typst_template_function. The
# valid master must compile through the bundled default template so this
# stays a pure BLD-01 gate and cannot go red because of an unrelated
# template or package interaction.

project = "Non Str Docname Gate"
author = "Test Author"
release = "1.0.0"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "master.typ", project, author),
    (123, "manual.typ", "Bad Docname", author),
]
