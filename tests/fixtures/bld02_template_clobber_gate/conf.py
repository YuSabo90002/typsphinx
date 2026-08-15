# Phase 47 gap-closure plan 11, task 1: BLD-02's reserved-directory
# fixture -- a single typst_documents entry whose target, once "./"-shape
# normalized, resolves UNDER the reserved `_template/` output directory
# every used registry key's bundle is copied into. Not in
# `47-VERIFICATION.md` -- measured during that plan's own planning pass,
# same root cause (missing shape normalization in `_collision_key()`),
# and predicted by `47-REVIEW.md` CR-02.
#
# Phase 54 plan 07 (OUT-07) update: pre-Phase-54-07, the target named the
# EXACT reserved basename `_template.typ` (once "./"-normalized); Task 1
# of Phase 54 plan 07 replaced that exact-name claim with a `_template/`
# PREFIX reservation covering the whole output DIRECTORY, so the target
# below now resolves UNDER the reserved directory instead of equalling it
# exactly -- still exercising the SAME shape-normalization gap
# (`_collision_key()`'s `posixpath.normpath()` must strip the "./" prefix
# before the reservation predicate's first-segment comparison runs, or
# this collision would go undetected).
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the template-clobber gap:
#   - The target MUST keep the "./" prefix and resolve under the
#     `_template/` directory (`./_template/nested.typ`) -- a bare target
#     with no "./" prefix and no reserved-directory prefix would not
#     reproduce this shape-normalization gap.
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
    ("index", "./_template/nested.typ", "Clobber Master", "Probe Author"),
]
