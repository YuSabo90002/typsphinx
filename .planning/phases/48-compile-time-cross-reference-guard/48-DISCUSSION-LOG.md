# Phase 48: Compile-Time Cross-Reference Guard - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-12
**Phase:** 48-compile-time-cross-reference-guard
**Areas discussed:** Degrade visibility and warning, `visit_pending_xref` (:4291) guard coverage, citation back-reference guard coverage, compile-time cost budget

---

## Degrade visibility and warning

### Q1 — What happens to the build-time degrade warning

Presented with the measured finding that the warning at `translator.py:4995-5001` uniquely covers
only one case (a reference to an explicitly `:orphan:` document), because unresolvable targets and
non-orphan documents outside every toctree are both already reported by Sphinx itself.

| Option | Description | Selected |
|--------|-------------|----------|
| Delete outright | Most faithful to SC#3; deletion verifiable by grep | ✓ |
| Keep a diagnostic-only union | Preserves the `:orphan:` warning but resurrects the deleted computation under another name, and stays blind to per-master differences | |
| Visualise in the PDF | Surfaces degradation in the artifact rather than the log, but makes one shared content file look different per master | |

**User's choice:** Delete outright.
**Notes:** Rejecting the PDF-visualisation option also settled that a degraded reference renders
identically to the linked form (CONTEXT.md D-02) — no separate question was needed.

### Q2 — Disposition of the tests guarding the deleted mechanism

The first framing of this question was withdrawn at the user's request; they asked for the
background first. On re-reading the code the original premise was corrected: the claim that the
predicate's `isinstance` guard would lose its test coverage was overstated, because lines 196 and 227
of `tests/test_master_include_set_predicate_gate.py` prove the same user-visible outcome end to end
without naming the deleted function. The real residual issue is the single test whose assertion
flips direction (line 103).

| Option | Description | Selected |
|--------|-------------|----------|
| Write the new expected value first | Phase 47's `47-EXPECTED-STRUCTURE.md` procedure — derive from `conf.py` + `.rst`, then write the test | ✓ |
| Delete and rewrite from scratch | Avoids looking like a rewrite in the diff, but loses the record of where the old behaviour went | |
| Keep both, linked by xfail | Self-documents the flip in the file, but leaves a permanently dead test | |

**User's choice:** Write the new expected value first.
**Notes:** Binding constraint #6 is the governing rule here.

### Q3 — The `opens_wrapper` side effect

Presented with the concrete chain: deleting `degrade_xref_to_text` makes `opens_wrapper`
unconditional, which makes a citation-derived reference to a non-included document eligible for its
own anchor, which makes `visit_citation` emit a back-reference marker where it previously emitted
none. `tests/test_citation_degradation_gate.py` case (iii) (line 1007) asserts the old behaviour.

| Option | Description | Selected |
|--------|-------------|----------|
| Accept as an intended fix | The anchor is `_current_docname()`-derived and always same-document, so suppressing it because the cross-document target degraded was a category error | ✓ |
| Preserve current output | Would require reintroducing a build-time condition, colliding head-on with SC#3 | |
| Accept but split into a separate phase | Reduces this phase's verification load but carries an unverified output change into Phase 49 | |

**User's choice:** Accept as an intended fix.

### Q4 — Standalone content-file compilation

Presented that the guard extends PROJECT.md's recorded standalone-compile behaviour to
cross-references: compiling a content file outside any wrapper makes every cross-reference degrade,
now completely silently after Q1.

| Option | Description | Selected |
|--------|-------------|----------|
| Record as a Phase 51 handoff | Fold into Phase 51's "what a content file compiled standalone does" | |
| Do something in Phase 48 | Would require Phase 49's `state` mechanism, collapsing the 48/49 split | |
| Add a line to the `-b typst` output message | Cheap, but duplicates Phase 51's documentation | |
| *(free text)* | "手当の必要があると思えない" | ✓ |

**User's choice:** No mitigation and no handoff note.

---

## `visit_pending_xref` (:4291) guard coverage

Presented the code at `translator.py:4262-4292` verbatim: it formats an unresolved `reftarget` into
a label, namespaces it to the current docname, and emits `#link()` without ever checking the label
exists. Also presented that existing coverage is two unit tests and no real-compile gate, and the
honest caveat that a RED may not be constructible because Sphinx usually degrades unresolved xrefs
before they reach the writer.

| Option | Description | Selected |
|--------|-------------|----------|
| Apply the guard | Closes a compile-fatal class unrelated to multi-master composition; satisfies SC#2 literally | ✓ |
| Rewire to the helper only | Smallest diff, satisfies SC#2's wording, leaves the latent fatal in place | |
| Split to a separate todo | Phase 48 would only read the site and record its nature (open question #1's minimum obligation) | |

**User's choice:** Apply the guard.
**Notes:** This answer also closes open question #1 — `:4291` is a fourth independent degradation
site that does not route through `_reference_anchor_decision`.

### Shared helper contract

Presented that all three emission sites stream their body between `visit_*` and `depart_*` (only
`visit_citation` buffers), so the helper's contract shape decides whether the other two sites must
grow new buffering. Three concrete code previews were shown.

| Option | Description | Selected |
|--------|-------------|----------|
| Return an open/close string pair | Body streams unchanged and lands on disk once; no new buffering | ✓ |
| Return a completed expression | Clear helper responsibility, but interpolates the body into both branches and forces buffering into two streaming sites | |
| Return only a boolean | Smallest diff, but is exactly the shape Phase 40.1's D-06 rejected — the judgement unifies while the derivation keeps drifting | |

**User's choice:** Return an open/close string pair.
**Notes:** Flagged during the question that PROJECT.md's measured snippet uses a string-literal body,
not a `let`-bound markup block, so the selected variant is unmeasured and must be verified against a
real `typst.compile()` during research (CONTEXT.md D-08).

---

## Citation back-reference guard coverage

Presented the measured route that breaks the "same-document means always present" assumption:
`visit_caption` raises `SkipNode` for captioned code blocks (`translator.py:2670-2671`) while
`visit_citation`'s backref loop scans the whole doctree, so a `[Cite]_` in a `code-block` `:caption:`
yields a citing node that `_find_citing_reference` finds — bypassing Phase 40.1's `ref_node is None`
fix — whose anchor `visit_reference` never emits.

| Option | Description | Selected |
|--------|-------------|----------|
| Guard them | SC#4's exemption covers anchors that exist whenever the file is included; these depend on visitor execution instead, so they are a different category | ✓ |
| Leave unguarded | Follows SC#4's literal wording, minimal change, knowingly leaves a compile-fatal route open | |
| Measure first, then decide | Same "close by measurement" style as open question #1, but leaves the planner without a locked decision | |

**User's choice:** Guard them.

---

## Compile-time cost budget

Presented that `tests/test_corpus_gate.py` has no timing instrumentation, so the SC#4 before/after
record is a one-off manual measurement rather than a permanent gate; and that the remediation space
is bounded — abandoning the design is unavailable under binding constraint #1, leaving "accept and
hand forward" or "file an improvement todo pointing at Phase 49's `state` mechanism".

| Option | Description | Selected |
|--------|-------------|----------|
| Fix thresholds before measuring | Removes the option of rationalising a regression after the fact | ✓ |
| Measure, then judge at verification | SC#4's literal wording; no unfounded numbers up front | |
| Judge on absolute wall-clock seconds | Robust to machine differences but blind to relative regressions on small projects | |

**User's choice:** Fix thresholds before measuring.

### Closing question — the threshold values

| Option | Description | Selected |
|--------|-------------|----------|
| Accept the proposed tiers | `<+20%` record only; `+20…100%` finding plus improvement todo; `>+100%` escalate to a Phase 49 blocker | ✓ |
| Specify different values | | |
| Discuss further gray areas | | |

**User's choice:** Accept the proposed tiers.

---

## Claude's Discretion

- Where the shared helper lives and what it is named, as long as the open/close contract holds.
- The identifier used for the `let`-bound body in the emitted Typst.
- Whether XREF-03's pre-fix RED is an `xfail(strict=True)` recording or a separate evidence transcript.
- The exact wording of any message text that changes.
- Whether `tests/test_master_include_set_predicate_gate.py` is deleted or kept holding only its
  three surviving end-to-end tests.

## Deferred Ideas

- Replacing `query(<L>).len() > 0` with a lookup against Phase 49's `state("inc", ())` include set —
  only possible once Phase 49 exists. Recorded as the named remediation path for the top cost tier.

## Todos reviewed but not folded

Six matches returned by `todo.match-phase 48`; none folded, all already owned elsewhere (two image
defects → Phase 50, defect A → Phase 49, the NixOS `ruff` toolchain issue → unrelated, the
`sphinx linkcheck` job → forbidden by binding constraint #9, the release `create-release` job →
closed at `/gsd-complete-milestone`).
