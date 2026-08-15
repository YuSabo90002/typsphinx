# Phase 49 plan 03, Task 2: SC#2's "not 2-master-specific" coverage
# obligation. Three `typst_documents` masters (m1, m2, m3), two shared
# children (common_a, common_b) and one mid-level document (mid), with
# toctree entry orders chosen so `common_b` is claimed by a DIFFERENT
# parent in each of the three masters -- `mid` (nested, in m1), `m2` itself
# (direct, in m2), `m3` itself (direct, in m3) -- with NO cross-master
# coordination in the algorithm (each master's `traversed` list is
# independently seeded with only its own docname). `common_a` is reachable
# only from m1 and m2 (deliberately not m3), so the fixture exercises both
# "shared by all three" (common_b) and "shared by two of three" (common_a)
# in one project. This fixture is unrelated to bld02_duplicate_target_gate
# (a target-collision gate) and missing_and_malformed_master_gate (a
# malformed-entry gate) -- it is the first genuine THREE-master
# composition fixture in the repository (template_named_dir_master has
# only two).
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the three-master coverage obligation:
#   - Each master's toctree entry ORDER must stay exactly as written --
#     m1 lists [mid, common_a]; m2 lists [common_a, common_b]; m3 lists
#     [common_b, mid] -- the orders are what make the three masters claim
#     common_b through three different parents.
#   - All three masters must stay in the same Sphinx project (splitting
#     them across projects would dissolve the "no cross-master
#     coordination" proof).
#   - common_a and common_b must both stay reachable from at least two
#     masters each.

project = "Three Master Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

root_doc = "m1"

typst_documents = [
    ("m1", "manual1.typ", "Three Master Gate — M1", "Probe Author"),
    ("m2", "manual2.typ", "Three Master Gate — M2", "Probe Author"),
    ("m3", "manual3.typ", "Three Master Gate — M3", "Probe Author"),
]
