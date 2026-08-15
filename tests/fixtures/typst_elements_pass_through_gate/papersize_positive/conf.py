# Sphinx configuration for the GATE-01 `typst_elements` papersize positive
# gate (Phase 26, CONF-04, SC#1) -- and, sharing this SAME build, the
# copyright-non-leak negative-shape gate (SC#4).
#
# Before this phase, `writer.py` laundered `typst_elements` through the
# SAME `sphinx_metadata` dict that also carried `copyright`, and
# `map_parameters()`'s narrow `DEFAULT_PARAMETER_MAPPING` (project/author/
# release only) silently dropped BOTH `papersize`/`fontsize` AND
# `copyright` on the floor -- so a documented
# `typst_elements = {"papersize": "us-letter"}` never reached the compiled
# PDF. This fixture proves the fix: a real `-b typstpdf` build must emit
# `papersize` as a QUOTED Typst string in the `#show: project.with(...)`
# region (D-01), and `copyright` -- set below to a distinctive canary
# string -- must NEVER appear anywhere in that same region (D-08).
#
# Uses the DEFAULT (unset `typst_package`/`typst_template`) template path,
# since `papersize`/`fontsize` are parameters of `templates/base.typ`'s own
# `project()` function (the byte-frozen receiving contract, SC#5) -- no
# Typst-Universe package or custom template is needed to exercise this.

project = "Typst Elements Papersize Positive Gate"
author = "Test Author"
release = "1.0.0"

# Copyright non-leak canary (SC#4): this string must NEVER appear in the
# emitted `#show: project.with(...)` region -- copyright is baseline
# Sphinx metadata, structurally unreachable by `map_parameters()` (D-08).
copyright = "2026, Copyright Non-Leak Canary -- Must Never Appear In Output"

extensions = ["typsphinx"]

# index must be a master document (not merely an included one) so the
# writer applies the full template routing and TypstPDFBuilder.finish()
# actually compiles it to PDF.
#
# Phase 47 (OUT-01/BLD-03): the target is "master", not the identity
# "index" -- since a typst_documents target is now a literal output path,
# an identity target would make the wrapper resolve onto this docname's
# own content file (index.typ) and silently overwrite it with a
# self-referential #include(), producing "TypstError: cyclic import".
# "master" is the canonical de-collision replacement
# (47-EXPECTED-STRUCTURE.md's fixture de-collision rule).
typst_documents = [
    ("index", "master", project, author),
]

typst_elements = {
    "papersize": "us-letter",
}
