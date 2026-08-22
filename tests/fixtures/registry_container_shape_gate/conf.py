# Phase 53 plan 08, task 1: the truthy-non-dict container fixture for
# `resolve_template_registry()`'s container guard -- 53-REVIEW.md WR-01,
# reproduced live at HEAD 344b9510 and again during this plan's own
# 53-08-RED-EVIDENCE.md measurement.
#
# Load-bearing properties -- do NOT touch either, or this fixture silently
# stops exercising the crash path it exists to gate:
#   - `typst_document_templates` MUST stay a TRUTHY non-`dict` value. An
#     empty list is FALSY and the `or {}` normalization on the line before
#     the crash silently resolves it to `{}` -- that is the falsy-control
#     edge Task 1's test D covers separately, not this fixture's job.
#   - The value MUST stay list-shaped. A `list` is the plausible
#     copy-paste-from-`typst_documents` authoring mistake this gate exists
#     to catch (`typst_documents` is a list of tuples; a user copying that
#     shape into `typst_document_templates`, which wants a `dict`, is the
#     realistic typo).

project = "Registry Container Shape Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_document_templates = ["a", "b"]
