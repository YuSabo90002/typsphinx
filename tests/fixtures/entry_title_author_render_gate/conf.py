# Sphinx configuration for the CONF-09 entry-title/author render gate
# (Phase 44.2, plan 01, SC#1).
#
# Pins D-03: an explicit `typst_documents` entry's title (`entry[2]`) and
# author (`entry[3]`) must reach the COMPILED PDF's own metadata dictionary,
# overriding `config.project` / `config.author`. `entry[2]` and `entry[3]`
# are DELIBERATELY set to values that differ from `project` / `author` below
# -- if this fixture's entry title/author matched the project/author values,
# a regression that silently fell back to `config.project` / `config.author`
# (instead of consuming the entry) would compile an IDENTICAL PDF and this
# gate would pass by coincidence. The divergence is what makes the assertion
# able to distinguish "entry value used" from "config fallback used"
# unambiguously.

project = "Config Project Must Not Win"
author = "Config Author Must Not Win"
release = "1.0.0"

extensions = ["typsphinx"]

# Phase 47 de-collision (47-EXPECTED-STRUCTURE.md "Fixture de-collision
# rule"): the original single-entry target "index" resolved to the SAME
# physical path as this docname's own content file (index.typ) under
# the two-layer split -- a self-collision (D-01).
#
# The list below is now D-04's repeated-docname case, deliberately
# LOAD-BEARING: two typst_documents entries name the SAME docname
# ("index") with different targets and different titles. D-04 permits
# this -- the validator asks only whether two logical files want ONE
# physical path, and a repeated docname does not, by itself, collide.
#
# RESOLVED by plan 47-09's unified validator: `_wrapper_output_relpath()`
# used to resolve a wrapper's WRITE PATH via a docname-based FIRST-MATCH
# scan (`_resolve_output_stem(entry[0])`), not a per-entry-target
# computation -- so BOTH entries below used to physically write to the
# FIRST entry's resolved target, "second-handbook.typ" (never
# "master.typ", the second entry's own declared target), and the second
# entry's write (processed LAST, in list order) overwrote the first. Plan
# 47-09 fixed this: `_wrapper_output_relpath()` now resolves EACH entry's
# wrapper path directly from THAT entry's own target
# (`_resolve_target_stem(entry[0], entry[1])`), so both
# "second-handbook.typ" and "master.typ" now exist independently, each
# carrying its OWN entry's values -- "Second Handbook"/"Jane Doe" and "My
# Handbook"/"Jane Doe" respectively. D-08 makes each wrapper read ITS OWN
# entry's title/author positionally (via `_entry_element_value()`), never
# through a docname first-match search (`typsphinx/writer.py`'s
# `_resolve_entry_element()`, which named that scan; 47-12-PLAN.md deleted
# it as dead code once D-08 made it a superseded implementation with zero
# production call sites) -- see `tests/test_document_metadata_render_gate.py`'s
# `test_repeated_docname_wrapper_reads_its_own_entry_title_not_first_match`
# for the end-to-end proof.
typst_documents = [
    ("index", "second-handbook.typ", "Second Handbook", "Jane Doe"),
    ("index", "master.typ", "My Handbook", "Jane Doe"),
]
