# Sphinx configuration for the DOC-11 published-Quick-Start gate.
#
# Mirrors docs/source/quickstart.rst's "Your First PDF" flow verbatim:
# project/author/release match the Configuration Options block the
# Quick Start publishes below its own steps. Deliberately has NO
# `typst_documents = ...` line -- the Quick Start's "Your First PDF" flow
# sets none, and that unset path is exactly what this fixture must exercise.
# Do not add a typst_documents line here; doing so would silently stop this
# fixture from exercising the published Quick Start's own steps.
#
# This fixture is NOT the same as tests/fixtures/default_typst_documents_gate/:
# that one exists to prove the CONF-08 derivation mechanism with a synthetic
# project name ("Quickstart Default Gate"); this one exists to prove the
# *published example* ("My Project") produces the *published filename*
# (myproject.pdf). Do not merge them and do not modify the existing fixture.
#
# make_filename_from_project("My Project") resolves to the stem "myproject"
# (measured live, Sphinx 9.1.0) -- the derivation must resolve
# typst_documents to [('index', 'myproject.typ', project, author, 'typst')].

project = "My Project"
author = "Your Name"
release = "1.0.0"
copyright = "2026, Your Name"

extensions = ["typsphinx"]

# typst_documents intentionally left unset -- the published Quick Start's
# "Your First PDF" flow sets none, and CONF-08's derivation must resolve it
# to [('index', 'myproject.typ', project, author, 'typst')].
