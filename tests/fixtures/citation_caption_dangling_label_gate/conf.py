# Phase 48 plan 01, task 1: the D-05 pre-fix RED fixture (XREF-04). A
# citation reference living inside a `code-block` directive's `:caption:`
# option is the only route where `visit_caption` raises `SkipNode` (skipping
# the WALKER) while `document.findall(nodes.reference)` still structurally
# finds the citing node -- so `_find_citing_reference` judges it eligible and
# `visit_citation`'s back-reference loop emits a `link(<label>, ...)` to an
# anchor that `visit_reference` never actually attached (SkipNode pruned its
# emission). The defect is invisible at `-b typst` (exit 0, no warning) and
# fatal only at Typst compile time.
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising D-05:
#   (a) The citing reference MUST live inside a `code-block` directive's
#       `:caption:` option -- that is the only route where `visit_caption`
#       raises `SkipNode` while `document.findall` still finds the citing
#       node. A citation reference in ordinary prose does not reproduce this.
#   (b) The citation definition MUST stay in the SAME document as the
#       citing reference -- this fixture is about the citation-caption
#       route, not about cross-document citation resolution.

project = "Citation Caption Gate"
author = "Probe Author"
release = "1.0"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "manual.typ", "Citation Caption Gate", "Probe Author"),
]
