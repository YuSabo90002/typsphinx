# Sphinx configuration for the GATE-01 package-alone config->output
# regression gate (Phase 22.2, CONF-02 / CONF-03).
#
# Pins FIVE pre-fix defect classes, each closed by an earlier plan in this
# phase and each given its own named assertion in
# tests/test_package_only_config_gate.py:
#
#   BUG-A: a package-alone master must NOT reference the shared
#          `_template.typ` file -- the builder deliberately never writes one
#          for this path (typsphinx/builder.py:_write_template_file()).
#   BUG-B: the package path must NOT back-fill an unrequested `date`
#          argument into the emitted `#show: ieee.with(...)` call.
#   BUG-C: an author entry declared on the `typst_template_function["params"]`
#          route must reach the output as a native Typst array of
#          dictionaries, never as a pre-rendered quoted string. (CONF-10/D-F
#          removed the dedicated dict-of-dicts author-details config value
#          this gate originally exercised; the same array-of-dicts shape
#          guarantee now lives entirely on the `params` route below.)
#   BUG-E: an EXPLICIT `typst_template_function["params"]` value must win
#          over an auto-derived Sphinx-metadata value on a colliding key
#          (here: "title").
#   BUG-F: all four essential `@preview` imports plus the codly
#          initialisation must be present exactly once, even on the
#          package-only path.
#
# CRITICAL: do NOT set `typst_template` here. Setting a custom template
# alongside `typst_package` routes this fixture onto the "both configured"
# path (D-03) instead of the package-ALONE path this gate exists to prove --
# that would invalidate every assertion below.
#
# NOTE (D-B, plan 45.1-01): this fixture declares `typst_template_function`
# with a non-empty `params` dict, which makes `params` the COMPLETE, EXCLUSIVE
# parameter set (render()'s wholesale-discard branch). This means the
# `typst_template_mapping = {"project": "title"}` line below no longer
# reaches the emitted call AT ALL -- it is retained only as evidence that a
# declared mapping is correctly discarded alongside every other auto-derived
# value once `params` is specified.

project = "Config Metadata Title Must Not Leak Into Output"
author = "Config Metadata Author Must Not Leak Into Output"
release = "1999-METADATA-RELEASE-CANARY-DO-NOT-LEAK-AS-DATE"
copyright = "2026, Fixture Author"

extensions = ["typsphinx"]

# index must be a master document (not merely an included one) so the writer
# applies the full package-alone template routing rather than the minimal
# included-document import set.
typst_documents = [
    ("index", "index", project, author),
]

# The package this fixture pins ALONE -- no typst_template is ever set.
typst_package = "@preview/charged-ieee:0.1.4"

# Single-key mapping: ONLY "project" -> "title" is honoured. "author" and
# "release" are deliberately left UNMAPPED, so if the package path ever
# back-filled them again (a BUG-B regression) it would show up as an
# unrequested "authors"/"date" argument -- exactly what this gate's BUG-B
# test checks for.
typst_template_mapping = {
    "project": "title",
}

# The package's entry function, with an EXPLICIT "title" that deliberately
# COLLIDES with the auto-derived "project" -> "title" mapping above (BUG-E),
# plus an abstract, index-terms and paper-size -- the same parameter shape
# examples/charged-ieee/approach1 uses. Deliberately no "bibliography"
# parameter: the package path has no asset-copying step, so a file-path
# parameter here would never resolve (see approach1/conf.py's own note).
#
# "authors" carries one entry with department/organization/location/email --
# proves this data reaches the output as a native Typst array of dictionaries
# (BUG-C), not a bare quoted string, now that it is declared here rather than
# through the removed dedicated author-details config value (CONF-10/D-F).
typst_template_function = {
    "name": "ieee",
    "params": {
        "title": "The Explicitly Configured Title Wins",
        "abstract": (
            "A fixture abstract proving the package-alone path compiles "
            "for real, end to end, through a genuine typst.compile() call."
        ),
        "index-terms": ["Fixture", "Gate", "Regression"],
        "paper-size": "a4",
        "authors": [
            {
                "name": "Ada Fixture Researcher",
                "department": "Department of Fixture Science",
                "organization": "Fixture Institute of Technology",
                "location": "Testville, TS",
                "email": "ada.fixture@example.test",
            },
        ],
    },
}
