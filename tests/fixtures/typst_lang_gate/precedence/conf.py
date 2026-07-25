# Sphinx configuration for the GATE-01 typst `lang` gate's precedence
# proof (Phase 27.1, CONF-07, SC#2).
#
# Sets Sphinx `language = "de"` AND an EXPLICIT `typst_elements["lang"]`
# of "ja" -- proving the explicit value wins over the value that would
# otherwise be auto-derived from `language` (D-05: the elements merge
# runs LAST in `map_parameters()`, and `writer.py` pre-merges the
# auto-derived value UNDER the user's `typst_elements` via a plain dict
# union whose right-hand operand -- the user's own config -- always
# wins on collision).
#
# Built through the faster `-b typst` (source-only) builder -- no real
# compile is needed to prove which value reaches the emitted show-rule
# region.
#
# Uses the DEFAULT (unset `typst_template`/`typst_package`) template
# path -- `lang` is only auto-derived (and therefore only eligible to be
# overridden) on that path (D-06/CONF-07).

project = "Typst Lang Gate Precedence Proof"
author = "Test Author"
release = "1.0.0"

extensions = ["typsphinx"]

# index must be a master document (not merely an included one) so the
# writer applies the full template routing and the auto-derivation/
# precedence logic under test.
typst_documents = [
    ("index", "index", project, author),
]

# The Sphinx language that WOULD auto-derive to "de" if no explicit
# value were configured below.
language = "de"

# The explicit value that must win over the "de" that `language` alone
# would have derived (SC#2).
typst_elements = {
    "lang": "ja",
}
