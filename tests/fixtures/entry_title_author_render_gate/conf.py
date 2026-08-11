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

typst_documents = [
    ("index", "index", "My Handbook", "Jane Doe"),
]
