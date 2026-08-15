# Phase 53 plan 06, task 1: CONF-14's "offending master sorts LAST" fixture
# -- pairs with conf14_prewrite_bad_first_gate, whose write order and
# declaration order are BOTH inverted relative to this one, so the two
# builds' error messages can be asserted byte-identical (ROADMAP SC#3).
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising CONF-14's zero-output guarantee:
#   - The bad key spelling `nope` and the registry key spelling `good` MUST
#     match conf14_prewrite_bad_first_gate/conf.py byte-for-byte, or the
#     message-identity assertion (test 3) stops meaning anything.
#   - `typst_document_templates["good"]` carries ONLY `package` -- no
#     `template` key -- so this fixture trips neither CONF-15's xor, nor
#     CONF-17's path arithmetic, nor D-08's existence check (all three run
#     only under `if template:`), and needs no template file on disk.
#   - Docnames are `alpha`, `beta`, `index`. Sorted alphabetically that is
#     `alpha`, `beta`, `index` -- the offending master (`beta`, key `nope`)
#     is written SECOND, after `alpha`'s content+wrapper already exist,
#     which is exactly the live verifier's build A. Do not rename the
#     docnames -- the alphabetical relationship is load-bearing.

project = "CONF-14 Prewrite Bad-Last Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

typst_document_templates = {
    "good": {"package": "@preview/example:0.1.0"},
}

typst_documents = [
    ("alpha", "alpha_out.typ", "Alpha Master", "Probe Author", "good"),
    ("beta", "beta_out.typ", "Beta Master", "Probe Author", "nope"),
]
