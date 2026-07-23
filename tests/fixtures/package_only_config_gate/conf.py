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
#   BUG-C: `typst_authors` must reach the output as a native Typst array of
#          dictionaries, never as a pre-rendered quoted string.
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

# One author, with department/organization/location/email -- proves
# typst_authors reaches the output as an array of dictionaries (BUG-C), not
# a bare quoted string.
typst_authors = {
    "Ada Fixture Researcher": {
        "department": "Department of Fixture Science",
        "organization": "Fixture Institute of Technology",
        "location": "Testville, TS",
        "email": "ada.fixture@example.test",
    },
}

# The package's entry function, with an EXPLICIT "title" that deliberately
# COLLIDES with the auto-derived "project" -> "title" mapping above (BUG-E),
# plus an abstract, index-terms and paper-size -- the same parameter shape
# examples/charged-ieee/approach1 uses. Deliberately no "bibliography"
# parameter: the package path has no asset-copying step, so a file-path
# parameter here would never resolve (see approach1/conf.py's own note).
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
    },
}
