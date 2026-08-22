# D-01 (Phase 47 plan 09, replacing CR-01): real-sphinx-build reproduction
# of an EXPLICIT typst_documents entry colliding with the reserved
# `_template/` output directory. `project` is deliberately neutral
# (non-colliding) so the only source of the collision is the explicit
# entry's own TARGET resolving under the reserved directory. Since the
# content/wrapper split, this now FAILS the build with a single pre-write
# ExtensionError (D-01/D-02/D-03), and NO `.typ` file is ever written.
#
# Phase 54 plan 07 (OUT-07) update: pre-Phase-54-07, the target named the
# EXACT reserved basename `_template.typ`; Task 1 of Phase 54 plan 07
# replaced that exact-name claim with a `_template/` PREFIX reservation
# covering the whole output DIRECTORY, so the target below now resolves
# UNDER the reserved directory instead of equalling it exactly.
#
# Load-bearing property -- do NOT touch, or this fixture silently stops
# exercising CR-01's explicit-template half:
#   - The typst_documents target name below must resolve under the
#     reserved `_template/` directory.

project = "Explicit Template Collision Gate"
author = "Test Author"
release = "1.0.0"
copyright = "2026, Test Author"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "_template/index.typ", project, author),
]
