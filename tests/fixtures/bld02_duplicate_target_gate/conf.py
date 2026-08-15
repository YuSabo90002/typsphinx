# Phase 47 plan 01, task 1: BLD-02's fixture -- two typst_documents entries,
# `index` and `other`, both targeting the SAME physical path `manual.typ`.
# On the unfixed tree this silently drops the first master's body (exit 0,
# no warning); post-fix (47-09) this must be a pre-write ExtensionError
# naming both entries.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising BLD-02:
#   - BOTH entries' target element MUST be the literal string `manual.typ`
#     -- if they differ, there is no collision at all.
#   - The two docnames MUST differ (`index` and `other`) -- BLD-02 is
#     specifically about two DIFFERENT logical files wanting one physical
#     path, distinct from D-04's "same docname, different targets is
#     allowed" case.
#   - `index.rst`'s body marker `INDEX-MASTER-MARKER-AAA` and `other.rst`'s
#     body marker `OTHER-MASTER-MARKER-BBB` must keep their exact spelling
#     -- the pre-fix RED evidence is a `grep -c` proof that the FIRST
#     entry's marker (INDEX-MASTER-MARKER-AAA) goes missing from the
#     surviving `manual.typ` while the SECOND (OTHER-MASTER-MARKER-BBB)
#     survives.

project = "Duplicate Target Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "manual.typ", "Index Master", "Probe Author"),
    ("other", "manual.typ", "Other Master", "Probe Author"),
]
