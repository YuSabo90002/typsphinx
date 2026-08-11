# Sphinx configuration for the CONF-08 default-derivation gate.
#
# Deliberately has NO `typst_documents = ...` line -- this is the ONLY way
# to exercise the unset path; all 103 other conf.py files in this repo set
# typst_documents explicitly (repo-wide census, 44-CONTEXT.md /
# 44-PATTERNS.md). Do not add a typst_documents line here; doing so would
# silently stop this fixture from exercising CONF-08 at all.
#
# No other typst_* value is set either (no typst_template, no typst_package,
# no typst_template_function), so the gate cannot go red through an
# unrelated template interaction.
#
# make_filename_from_project("Quickstart Default Gate") resolves to the stem
# "quickstartdefaultgate" (measured live, Sphinx 9.1.0) -- CONF-08's
# derivation must resolve typst_documents to
# [('index', 'quickstartdefaultgate.typ', project, author, 'typst')].

project = "Quickstart Default Gate"
author = "Test Author"
release = "1.0.0"
copyright = "2026, Test Author"

extensions = ["typsphinx"]

# typst_documents intentionally left unset -- CONF-08's derivation must
# resolve it to [('index', 'quickstartdefaultgate.typ', project, author,
# 'typst')].
