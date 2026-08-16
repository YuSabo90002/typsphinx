# Phase 54.1 plan 04, task 2: WR-01's D-02 bullet 1 measured-shape
# control -- the layout the charged-ieee approach2 example historically
# had before its own rename.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising D-02 bullet 1's measured shape:
#   - This fixture deliberately sets NO Sphinx Jinja override directory
#     list at all (the config value this comment intentionally does not
#     name literally, so a repo-wide grep for that value's name never
#     matches this file -- see the plan's own acceptance criteria).
#   - The registry key "custom"'s template lives inside a directory
#     spelled exactly like Sphinx's own DEFAULT for that unset config
#     value -- proving detection is a relationship test against LIVE
#     config values, never a name match on a directory's literal
#     spelling. With nothing set, there is nothing to relate against, so
#     this build must succeed.

project = "Templates Path Absent Control Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_document_templates = {
    "custom": {"template": "_templates/custom.typ"},
}

typst_documents = [
    ("index", "index_out.typ", "Absent Control", "Probe Author", "custom"),
]
