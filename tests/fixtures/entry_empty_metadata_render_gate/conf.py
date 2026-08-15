# Sphinx configuration for the CONF-09 empty-entry-metadata render gate
# (Phase 44.2, plan 01, SC#1 / D-01).
#
# Pins D-01: an empty-string `entry[2]` / `entry[3]` is a VALUE, not a
# signal to fall back to `config.project` / `config.author`. `project` /
# `author` below are DELIBERATELY set to values that would be visibly wrong
# if the fallback fired -- if a regression made an empty entry element fall
# back to `config.project` / `config.author` instead of being honoured as an
# empty string, the compiled PDF's title/author would carry these sentinel
# values instead of Typst's own empty-string behaviour (an absent `/Title`
# key and a present, empty `/Author` value -- see RESEARCH.md Pitfall 6),
# and this gate would catch it.

project = "Config Fallback Must Not Fire For Empty Title"
author = "Config Fallback Must Not Fire For Empty Author"
release = "1.0.0"

extensions = ["typsphinx"]

# Phase 47 de-collision (47-EXPECTED-STRUCTURE.md "Fixture de-collision
# rule"): the original target "index" resolved to the SAME physical path
# as this docname's own content file (index.typ) under the two-layer
# split -- a self-collision (D-01). Retargeted to the canonical
# replacement "master.typ"; the docname and the empty title/author
# values are unchanged.
typst_documents = [
    ("index", "master.typ", "", ""),
]
