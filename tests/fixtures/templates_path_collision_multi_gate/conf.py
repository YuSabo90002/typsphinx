# Phase 54.1 plan 04, task 1: WR-01's multi-relation collision gate
# fixture -- ONE build exercising all three of D-02's path relations at
# once (is / is-contained-by / contains), feeding D-03's
# accumulate-then-raise-once aggregation and sorted() ordering guarantee.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the multi-relation / aggregation gate:
#   - `templates_path` names TWO entries: "_templates" and "_typst/inner".
#     Neither directory needs to exist on disk for the second entry --
#     TypstBuilder._validate_used_template_paths() compares CONFIG
#     VALUES, not a filesystem listing.
#   - Registry key "alpha"'s template ("_templates/alpha.typ") resolves
#     into a bundle directory that IS the "_templates" templates_path
#     entry (equality relation).
#   - Registry key "beta"'s template ("_templates/nested/beta.typ")
#     resolves into a bundle directory that IS CONTAINED BY the
#     "_templates" templates_path entry.
#   - Registry key "gamma"'s template ("_typst/gamma.typ") resolves into
#     a bundle directory that CONTAINS the "_typst/inner" templates_path
#     entry.
#   - The key names "alpha" < "beta" < "gamma" sort alphabetically in
#     that exact order -- the ordering assertion in
#     tests/test_templates_path_collision_gate.py reads the aggregate
#     message's key-name positions and asserts they are strictly
#     increasing in THIS order. Do not rename any of the three keys.
#   - ONE docname ("index") carries THREE typst_documents entries with
#     THREE DISTINCT target filenames (alpha_out.typ / beta_out.typ /
#     gamma_out.typ), chosen over three separate .rst documents because
#     _validate_output_path_collisions()'s own docstring (D-04)
#     explicitly allows "two entries naming the SAME docname with
#     DIFFERENT targets" -- this sidesteps that guard entirely without
#     needing extra fixture documents.
#   - Every template lives in a subdirectory of the source tree, never at
#     the source-tree root, so this fixture trips WR-01's new check and
#     never CONF-17 (plan 54.1-03's hoisted check, same wave).
#   - No template below declares an "@preview" import (CLAUDE.md's
#     four-site version-lockstep hazard; this fixture must never become a
#     fifth site).

project = "Templates Path Collision Multi Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

templates_path = ["_templates", "_typst/inner"]

typst_document_templates = {
    "alpha": {"template": "_templates/alpha.typ"},
    "beta": {"template": "_templates/nested/beta.typ"},
    "gamma": {"template": "_typst/gamma.typ"},
}

typst_documents = [
    ("index", "alpha_out.typ", "Alpha Master", "Probe Author", "alpha"),
    ("index", "beta_out.typ", "Beta Master", "Probe Author", "beta"),
    ("index", "gamma_out.typ", "Gamma Master", "Probe Author", "gamma"),
]
