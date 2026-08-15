# Phase 47 gap-closure plan 11, task 1: BLD-02's reserved-infrastructure-file
# fixture -- a single typst_documents entry whose target, once "./"-shape
# normalized, is the reserved `_template.typ` infrastructure file every
# content and wrapper file imports. Not in `47-VERIFICATION.md` -- measured
# during this plan's own planning pass, same root cause (missing shape
# normalization in `_collision_key()`), and predicted by `47-REVIEW.md`
# CR-02.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the template-clobber gap:
#   - The target MUST keep the "./" prefix and the `_template` stem
#     (`./_template.typ`) -- this is the reserved-infrastructure collision
#     kind D-03 enumerates, defeated specifically by the missing shape
#     normalization (a bare `_template.typ` target, with no "./" prefix,
#     is ALREADY caught by the existing reserved-file claim in
#     `_validate_output_path_collisions()` and would not reproduce this
#     gap).
#   - `index.rst`'s body marker `TEMPLATE-CLOBBER-SENTINEL-DDD` must keep
#     its exact spelling -- the pre-fix RED evidence is a
#     `grep -c '^#let project'` proof that the written `_template.typ` no
#     longer defines the `project` symbol every content/wrapper file
#     imports.

project = "Template Clobber Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "./_template.typ", "Clobber Master", "Probe Author"),
]
