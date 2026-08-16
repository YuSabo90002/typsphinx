# Phase 54.1 plan 04, task 2: WR-01's adjacency false-positive control.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops catching the regression it exists to catch:
#   - The registry key "custom"'s template lives at
#     "_templatesx/custom.typ" -- a SIBLING directory of the
#     `templates_path` entry below, whose name merely shares that
#     entry's name as a prefix. It is NOT the entry and is NOT under it.
#   - If this fixture ever starts refusing the build, the containment
#     predicate (`typsphinx.builder._paths_related()`) has been
#     "simplified" into a `str.startswith()` prefix comparison -- exactly
#     the false positive D-02 warns against. This fixture is that
#     tripwire.

project = "Templates Path Adjacent Control Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

templates_path = ["_templates"]

typst_document_templates = {
    "custom": {"template": "_templatesx/custom.typ"},
}

typst_documents = [
    ("index", "index_out.typ", "Adjacent Control", "Probe Author", "custom"),
]
