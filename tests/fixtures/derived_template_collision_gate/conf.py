# D-01 (Phase 47 plan 09, replacing CR-01): real-sphinx-build reproduction
# of a zero-`typst_documents`-configuration RESERVED-DIRECTORY collision.
# CONF-08's derived default (`_default_typst_documents()`) reads
# `root_doc` directly as the sole entry's docname when `typst_documents`
# is left completely unset -- so a project whose `root_doc` lives inside
# the reserved `_template/` output directory collides with the
# reservation even in the "zero configuration" case.
#
# Phase 54 plan 07 (OUT-07) update: pre-Phase-54-07, this fixture instead
# relied on `project = "_Template"` slugifying (`make_filename_from_project`
# preserves underscores) to the EXACT reserved basename `_template.typ`.
# That exact-name claim is gone -- Task 1 of Phase 54 plan 07 replaced it
# with a `_template/` PREFIX reservation covering the whole output
# DIRECTORY -- and a project-name slug can never contain a "/" separator,
# so the derived-default route can no longer reproduce a collision
# through `project` alone. `root_doc` is the lever instead.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising CR-01's derived-default template-clobber half:
#   - NO `typst_documents` line: the derived default (CONF-08) must be the
#     thing that produces the colliding docname.
#   - `root_doc` must remain "_template/index".

project = "Derived Template Collision Gate"
author = "Test Author"
release = "1.0.0"
copyright = "2026, Test Author"

extensions = ["typsphinx"]

root_doc = "_template/index"

# typst_documents intentionally left unset -- the derived default
# (CONF-08) reads root_doc directly, so the sole entry's docname
# ("_template/index") is what collides with the reserved `_template/`
# output directory.
