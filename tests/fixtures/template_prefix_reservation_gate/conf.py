# Sphinx configuration for the template-prefix-reservation-gate fixture.
#
# Relocated from tests/fixtures/template_named_dir_master/ (Phase 22.1,
# gap G-22.1-4 / CR-01 closure) by Phase 54 plan 07 (OUT-07). This is
# that fixture's NEGATIVE successor -- it keeps the ORIGINAL docname
# layout verbatim (both docnames live inside a source subdirectory
# literally named `_template`), but where that layout used to compile
# successfully, it is now a build error.
#
# History (the intent this fixture originally proved): pre-Phase-22.1,
# TypstWriter.translate() computed the template import by relativizing
# the master's docname against a synthetic "_template" sentinel target
# docname. When the master's own directory portion was itself literally
# "_template", the sentinel collided with a real path component and
# produced a malformed, stem-less reference (e.g. "#import "..typ"" at
# depth 1, "#import "../.typ"" at depth 2). Phase 22.1's depth-based fix
# removed that string dependence.
#
# Why the original defect class is now structurally impossible: Phase 54
# plan 04's OUT-06 replaced the depth-based import with a ROOT-ABSOLUTE
# one (`compute_template_import_path(key, filename)`), which does not
# even accept a wrapper-directory argument -- no directory name,
# including one literally named "_template", can influence the import
# string in any way, because nothing about the wrapper's own location is
# ever consulted. There is no longer any string equality between a
# wrapper's directory and the reserved name left to collide.
#
# What replaces it (Phase 54 plan 07, OUT-07): this EXACT docname layout
# -- both docnames living inside a directory literally named `_template`
# -- is now itself a build error. `_validate_output_path_collisions()`'s
# `_reserves_template_prefix()` predicate refuses any content or wrapper
# file whose resolved output path's first segment is the reserved
# template-bundle directory, and both docnames' CONTENT files
# (`_template/index.typ`, `_template/sub/index.typ`, unconditional per
# COMP-01/OUT-03, regardless of where either entry's WRAPPER resolves)
# trip exactly that predicate. This fixture's role therefore inverts from
# POSITIVE (Phase 22.1 through Phase 54 plan 05 proved this layout
# compiles correctly) to NEGATIVE (Phase 54 plan 07 proves the build now
# refuses it, naming both offending docnames in one aggregated error) --
# see tests/test_template_prefix_reservation_gate.py.
#
# The multi-entry (two distinct bare targets) and per-master
# author-divergence regression intents this fixture ALSO carried
# (Phase 47/44.2) are NOT lost -- they move to the positive successor,
# tests/fixtures/nested_dir_multi_master/, whose docname layout the
# builder still accepts.

project = "Template Prefix Reservation Gate"
author = "Test Author"
release = "1.0.0"

extensions = [
    "typsphinx",
]

# The depth-1 master is the project root, keeping nothing else at the
# outdir root that could mask the condition.
root_doc = "_template/index"

typst_documents = [
    (
        "_template/index",
        "template-dir-master.typ",
        "Template Named Dir Master",
        "Test Author",
    ),
    (
        "_template/sub/index",
        "template-dir-sub.typ",
        "Template Named Dir Master (nested)",
        "Test Author (nested)",
    ),
]
