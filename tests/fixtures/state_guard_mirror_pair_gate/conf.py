# Phase 49 plan 02 -- COMP-10 fixture: two masters differing ONLY in the
# order of one toctree's two entries (`zmid`, `shared`), so any divergence
# in resolved heading levels is attributable to that order alone -- plus a
# third, master-less (no-toctree) master (`soloist`) as the null-hypothesis
# control: a master with nothing to nest resolves its own heading at level
# 1 regardless of the offset mechanism. The third entry is an executor
# addition beyond 49-EXPECTED-STRUCTURE.md's literal fixture specification
# entry 2, derived by hand from the traversal rule (an empty
# `env.toctree_includes` list produces an empty edge set and no `context {
# ... }` block, so the master's own heading is emitted with no ancestor
# offset applied at all) per binding constraint #6 (never read off a
# build).
#
# Load-bearing properties -- do NOT touch any of these, or this fixture
# silently stops exercising the mirror-pair/no-nesting-control shapes:
#   - The ONLY permitted difference between `xmastera.rst` and
#     `xmasterb.rst` is the ORDER of their two toctree entries (`zmid`,
#     `shared`) -- `xmastera` lists `zmid` then `shared`; `xmasterb` lists
#     `shared` then `zmid`. Any other divergence (title wording, section
#     depth, additional entries) invalidates the "divergence is
#     attributable to traversal order alone" claim this fixture exists to
#     support.
#   - `zmid.rst` must keep its own toctree of exactly `shared` -- removing
#     it dissolves the first-encounter-wins contest for `shared` between
#     `xmastera`'s direct entry and `zmid`'s own claim.
#   - `root_doc` must stay pointed at `xmastera` -- there is no `index`
#     document in this fixture.
#   - Neither master's headings may gain or lose a nesting level: the gate
#     asserts EXACT resolved level sequences (`[1, 2, 3]` for `xmastera`,
#     `[1, 2, 2]` for `xmasterb`).
#   - `soloist.rst` must keep its `:orphan:` field (required by Sphinx
#     regardless of `typst_documents` membership -- any document not
#     reachable via toctree from `root_doc` needs it) and must carry NO
#     toctree of its own -- that absence is the entire point of the
#     no-nesting control.

project = "Mirror Pair Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]
root_doc = "xmastera"
typst_documents = [
    ("xmastera", "mastera.typ", "Mirror Pair A", "Probe Author"),
    ("xmasterb", "masterb.typ", "Mirror Pair B", "Probe Author"),
    ("soloist", "solomaster.typ", "Mirror Pair Solo", "Probe Author"),
]
