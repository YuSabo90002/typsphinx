# D-01 (Phase 47 plan 09, replacing CR-01): real-sphinx-build reproduction
# of an EXPLICIT typst_documents entry colliding with a real docname's own
# content path. Unlike derived_docname_collision_gate, the collision here
# comes from an explicit `typst_documents` target name naming an existing
# docname ("chapter1") as the master's target -- not from the
# derived-default project-name slugification. `project` is deliberately
# neutral (non-colliding) so the only source of the collision is the
# explicit entry. Since the content/wrapper split, this now FAILS the
# build with a single pre-write ExtensionError (D-01/D-02/D-03) instead of
# warning and keeping both documents (CR-01's old behaviour).
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising CR-01's explicit-path half:
#   - The typst_documents target name below must remain "chapter1.typ".
#   - `chapter1.rst` must keep its filename.

project = "Explicit Docname Collision Gate"
author = "Test Author"
release = "1.0.0"
copyright = "2026, Test Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "chapter1.typ", project, author),
]
