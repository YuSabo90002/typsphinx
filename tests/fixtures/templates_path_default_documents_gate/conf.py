# Phase 54.1 plan 04, task 3: WR-01/D-05's synthesized-entry gate.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops proving the synthesized entry is checked:
#   - The document-list config value that maps docnames to Typst wrapper
#     targets is deliberately NOT set anywhere in this file (the plan's
#     own acceptance criteria grep for that value's exact name and
#     require a zero count, so this comment intentionally never spells
#     it out either). Its absence is the entire point: Sphinx's config
#     machinery falls back to this extension's callable default, whose
#     single synthesized entry's fifth element is the built-in registry
#     key "typst" -- and it is THAT key's global template
#     (`typst_template` below) which must be checked pre-write.
#   - Setting that config value back would silently convert this fixture
#     into a duplicate of plan 54.1-01's own collision fixture, which
#     already covers the EXPLICIT-entry case -- this fixture exists to
#     prove the FALLBACK path is checked too.
#   - `templates_path` names "_templates", and the GLOBAL Typst template
#     (`typst_template`) resolves into that SAME directory -- the
#     identical collision shape plan 54.1-01's fixture uses, but reached
#     through the synthesized entry instead of an explicit one.

project = "Templates Path Default Documents Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

templates_path = ["_templates"]

typst_template = "_templates/custom.typ"
