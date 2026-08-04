# Sphinx configuration for the D-03 opt-out wording gate (Phase 44, plan
# 44-02).
#
# The empty list set below is a DELIBERATE opt-out, not an oversight.
# After CONF-08 (plan 44-01), this is the ONLY way to reach
# TypstPDFBuilder.finish()'s early-return branch -- an unset
# `typst_documents` now resolves through the derived default
# (_default_typst_documents) instead of ever being empty. Filling this list
# in would silently stop this fixture exercising that branch at all.
#
# make_filename_from_project("Empty Optout Gate") would yield the stem
# "emptyoptoutgate" -- that name must NEVER appear in this fixture's
# output, because the derived default must not be consulted when the user
# explicitly opted out.

project = "Empty Optout Gate"
author = "Test Author"
release = "1.0.0"

extensions = ["typsphinx"]

typst_documents = []
