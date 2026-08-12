# Phase 48: Compile-Time Cross-Reference Guard - Context

**Gathered:** 2026-08-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Whether a cross-document reference's target label exists stops being decided by a build-time boolean
in Python and becomes decided by Typst at compile time, **per compiled wrapper**. Today
`translator.py:3071-3075` consults `builder.master_included_docnames` — a union across *all* masters
that cannot know which master is currently asking. After Phase 47 a content file is compiled zero,
one, or many times, once per wrapper that includes it, and the same degrade decision must come out
differently in each; that information genuinely does not exist until a specific wrapper is compiled.

The build-time mechanism is **deleted in the same change**, not left half-alive:
`_compute_master_included_docnames()`, its `write()` call site, and
`_ReferenceAnchorDecision.degrade_xref_to_text` all go, and no second degrade decision survives
anywhere that could disagree with the compile-time one.

This phase lands **before** Phase 49 because of binding constraint #1: fixing the include graph
converts today's silent omission into a hard compile failure for any shared document referencing a
target present in one master but not another. The guard is what makes the graph fix safe to ship.

**Not in this phase:** composition semantics, the per-master include graph, `state`-guarded includes,
`:numref:` divergence (Phase 49); the PR #131 image defects (Phase 50); documenting the two-layer
output shape (Phase 51).

</domain>

<decisions>
## Implementation Decisions

### Degrade visibility and reporting

- **D-01:** The build-time degrade warning is deleted outright, with no diagnostic replacement — **Reversibility:** costly — restoring it would require re-deriving the all-masters union that SC#3 requires be grep-zero, under a different name, which is the "second competing mechanism" this phase exists to remove. Measured during discussion: the warning at `translator.py:4995-5001` fires only for references Sphinx *did* resolve whose target docname is outside the union. Unresolvable `:doc:`/`:ref:` targets are already reported by Sphinx's own `unknown document`, and non-orphan documents outside every toctree are already reported by Sphinx's own `document isn't included in any toctree`. The only case this warning uniquely covers is a reference to a document the author explicitly marked `:orphan:` — i.e. a document the author deliberately excluded. Nothing user-facing documents this warning: `grep -rn "non-included\|degrade" docs/source/` returns zero, so no published contract changes.

- **D-02:** A degraded reference renders as exactly the same visible text as the linked form, with no visual marking — **Reversibility:** reversible — the else branch is a single expression in one shared helper. The alternative (marking degraded references in the PDF) was considered and rejected: the same shared content file would then look different depending on which master compiled it.

- **D-03:** Every gate whose assertion flips direction has its new expected value written down in a standalone phase artifact, derived from the fixture's `conf.py` and `.rst` alone, **before** the new emitter is run — **Reversibility:** reversible — this is the Phase 47 `47-EXPECTED-STRUCTURE.md` procedure applied to the one gate that flips. `tests/test_master_include_set_predicate_gate.py::TestBld03GhostEntryXref::test_ghost_entry_subtree_xref_degrades_typst` currently asserts that a `:ref:` into a phantom-included subtree degrades to plain text; after this phase the correct emission is a guarded `link`. Binding constraint #6 forbids deriving that new expected value by reading the new emitter's output.

### Scope of the guard

- **D-04:** `visit_pending_xref` is brought under the guard, not merely rewired — **Reversibility:** reversible — the site at `translator.py:4287-4291` emits `#link(<label>)[` for a `reftarget` Sphinx *failed* to resolve, namespaced to the current docname, with no existence check anywhere. This closes open question #1: it is a **fourth independent degradation site**, it does not route through `_reference_anchor_decision`, and it is a latent whole-document compile fatal that has nothing to do with multi-master composition. Existing coverage is two unit tests in `tests/test_translator.py` (1973, 2001) and no real-compile gate; the `_sanitize_label` note in its own docstring shows this path has already produced one real fatal. If a RED cannot be constructed — Sphinx resolves most unresolved xrefs to plain text with a warning rather than letting `pending_xref` reach the writer — follow the Phase 40.1 D-01 precedent: enumerate every plausible source shape and record why the topology is unconstructible, rather than accepting "not reproducible".

- **D-05:** Citation back-references are guarded, and the reason SC#4 does not exempt them is recorded explicitly — **Reversibility:** reversible — SC#4 exempts same-document anchors because content files are included wholesale, so their targets are always present. Citation back-reference targets are **not** in that category: their presence depends on `visit_reference` having actually run on the citing node. Measured route during discussion — `visit_caption` raises `SkipNode` when `in_captioned_code_block` (`translator.py:2670-2671`), while `visit_citation`'s backref loop scans the whole doctree via `self.document.findall(nodes.reference)` (`_find_citing_reference`, `translator.py:3006`). A `[Cite]_` inside a `code-block` `:caption:` (Sphinx inline-parses that option) therefore yields a citing node that `_find_citing_reference` **finds** — so the Phase 40.1 `ref_node is None` guard never fires — that `_reference_anchor_decision` calls eligible, but whose anchor is never emitted. That is the WR-01 defect class recurring through a route the 40.1 fix does not cover. Cost is bounded by the number of bibliography entries; the failure mode is a whole-document compile fatal.

- **D-06:** Same-document anchors outside the citation back-reference case keep their unguarded form, asserted explicitly, per SC#4 — **Reversibility:** reversible.

### Shared helper contract

- **D-07:** The shared guard helper returns an **open string and a close string**, and the reference body keeps streaming between them exactly as it does today — **Reversibility:** costly — three emission sites consume this contract, and changing its shape later means rewriting all three plus their gates. The visit side emits `{prefix}context { let __b = [`, the children stream in unchanged, and the depart side emits `]; if query(<L>).len() > 0 { link(<L>, __b) } else { __b } }`. This keeps the body on disk **once** — the alternative of interpolating the body into both branches doubles it and risks duplicate labels or footnotes inside a link body — and requires no new buffering in `visit_reference` or `visit_pending_xref`, which currently stream (`visit_pending_xref` opens `#link(<L>)[` and `depart_pending_xref` closes `]`). A helper returning only a boolean was rejected on the Phase 40.1 D-06 precedent: unifying the judgement while leaving each site to build its own expression leaves the derivation drifting upstream.

- **D-08:** The exact Typst syntax of D-07's shape is treated as **unmeasured** and must be verified against a real `typst.compile()` during research before any plan depends on it — **Reversibility:** reversible — `PROJECT.md:108-113` records a measured guard snippet, but its body is a single string literal, not a `let`-bound markup block, and the interaction between `let` scope inside `context` and the translator's code/markup mode switching is not covered by that measurement.

### Consequences of deleting the build-time mechanism

- **D-09:** Removing `degrade_xref_to_text` makes `opens_wrapper` unconditional, and the resulting citation back-reference marker appearing where none appeared before is accepted as an intended behaviour fix — **Reversibility:** costly — this changes emitted PDF output. Today `opens_wrapper = bool(refuri or refid) and not degrade_xref_to_text`, so a citation-derived reference to a document outside the union is judged ineligible for its own anchor and `visit_citation` emits no back-reference marker for it. After the removal it is eligible, gets its anchor, and the marker appears. The anchor is `_current_docname()`-derived and therefore always same-document, so suppressing it because the *cross-document* target degraded was a category error. `tests/test_citation_degradation_gate.py`'s case (iii) (`_wr03_case_refuri_excluded_document`, line 1007) asserts the old behaviour and flips under D-03's write-expected-first rule.

- **D-10:** The four unit tests bound directly to the deleted function are removed with it; the three end-to-end tests in the same file survive unchanged — **Reversibility:** reversible — in `tests/test_master_include_set_predicate_gate.py`, lines 165, 260, 288 and 319 call `_compute_master_included_docnames()` directly and lose their subject. Lines 129 (`no_dangling_label_typstpdf`), 196 (`unhashable_docname_skipped_gracefully_typst`) and 227 (`reported_by_finish_typstpdf`) assert user-visible outcomes through a real `sphinx-build` without naming the deleted function, and keep passing — so the Phase 47 gap-9b regression protection is not lost. Line 103 is the one that flips, under D-03. `_is_usable_typst_documents_entry()` itself survives for its four remaining consumers, and its docstring's consumer count must be corrected from five to four in the same change (Phase 47's own durable lesson: the docstring said FOUR when there were five).

### Cost measurement

- **D-11:** The compile-time cost thresholds are written down **before** the measurement is taken, in three tiers — **Reversibility:** reversible — under `+20%` the number is recorded and nothing else happens; between `+20%` and `+100%` it is recorded as an explicit finding in the phase evidence and an improvement todo is filed; above `+100%` it is escalated to a blocker attached to Phase 49's scope. Fixing the tiers first removes the option of rationalising a measured regression after the fact. Measurement is a **one-off manual before/after record in the phase artifacts**, not a permanent assertion: `tests/test_corpus_gate.py` carries no timing instrumentation and a wall-clock assertion would be flaky across CI machines. The realistic remediation if the top tier is hit is to replace `query(<L>).len() > 0` with a lookup against Phase 49's `state("inc", ())` include set once that exists — abandoning the design is not available, since binding constraint #1 makes Phase 49 depend on the guard.

### Claude's Discretion

- Where the shared helper lives and what it is named, as long as D-07's open/close contract holds and all three emission sites consume it.
- The exact identifier used for the `let`-bound body in D-07's emitted Typst (the `__b` in the sketch is illustrative, not fixed).
- Whether the pre-fix RED for XREF-03 is expressed as an `xfail(strict=True)` recording (the Phase 47 gap-closure convention) or as a separately-committed evidence transcript.
- The exact wording of any message text that changes.
- Whether the four deleted unit tests' file is removed entirely or kept holding only its three surviving end-to-end tests.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope and constraints

- `.planning/ROADMAP.md` §"Phase 48: Compile-Time Cross-Reference Guard" (lines 588-639) — the phase goal, the four success criteria, and the `**UI hint**: no` override
- `.planning/ROADMAP.md` §"Binding constraints" (lines 345-412) — #1 (this phase must land no later than Phase 49; the two are not independently parallelizable in either order), #4 (GATE-01 and its non-fatal amendment: every non-fatal defect names its pre-fix RED assertion before implementation starts), #6 (no laundered gates — expected values derived from first principles and written down before running the new emitter), #7 (zero new runtime dependencies, four `@preview` packages, no new `typst_*` config value), #8 (every phase closes green), #9 (typing-import modernization and `sphinx linkcheck` are both forbidden this milestone)
- `.planning/ROADMAP.md` lines 417-423 — the open-questions-to-owning-phase table; open question #1 is this phase's, and its answer is recorded in D-04 above
- `.planning/REQUIREMENTS.md` lines 68-74 — XREF-03 and XREF-04, this phase's two requirements
- `.planning/REQUIREMENTS.md` lines 213-218 — open question #1 as originally written
- `.planning/PROJECT.md` lines 105-120 — the **measured** `context` + `query` guard snippet (typst-py 0.15.0, 2026-08-11) and the three enumerated label-reference sites. Do not re-derive the snippet; do verify D-07's `let`-bound variant of it
- `.planning/PROJECT.md` lines 57-62 — why the build-time boolean must go and why `:orphan:` targets and per-master differences become correct through this one mechanism
- `.planning/PROJECT.md` lines 134-140 — the standalone-content-file behaviour note (empty state, no children included), which D-05 of Phase 47's discussion and Phase 51 both touch

### Prior phase decisions this phase reverses or consumes

- `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-CONTEXT.md` — Phase 47's D-01..D-09, in particular D-03 (one validator over one `_is_usable_typst_documents_entry()` predicate) whose FIFTH consumer is the function this phase deletes
- `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-EXPECTED-STRUCTURE.md` — the write-expected-values-first artifact D-03 above tells this phase to imitate
- `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-GAP2-RED-EVIDENCE.md` — the verbatim pre-fix transcripts behind the eight tests in `tests/test_master_include_set_predicate_gate.py`, needed to judge which of them lose their subject (D-10)

### Code this phase changes

- `typsphinx/translator.py:3011-3103` — `_reference_anchor_decision()`, whose `degrade_xref_to_text` field and `master_included_docnames` lookup are deleted (D-09)
- `typsphinx/translator.py:4985-5007` — `visit_reference`'s resolved cross-document branch, the primary XREF-03 site
- `typsphinx/translator.py:4941-4950` and `:4980-4984` — `visit_reference`'s two same-document branches, which stay unguarded (D-06)
- `typsphinx/translator.py:3267-3284` — `visit_citation`'s back-reference loop, guarded per D-05
- `typsphinx/translator.py:4262-4303` — `visit_pending_xref` / `depart_pending_xref`, guarded per D-04
- `typsphinx/translator.py:2659-2671` — `visit_caption`'s `SkipNode`, the measured route that makes D-05 necessary
- `typsphinx/builder.py:240-330` (approx.) — `master_included_docnames` attribute and `_compute_master_included_docnames()`, both deleted
- `typsphinx/builder.py:758` — the `write()` call site that populates it, deleted
- `typsphinx/builder.py:106-164` — `_is_usable_typst_documents_entry()`, which survives; its docstring's five-consumer count becomes four (D-10)

### Tests this phase changes

- `tests/test_master_include_set_predicate_gate.py` — four unit tests deleted, one assertion flipped, three survive (D-10, D-03)
- `tests/test_xref_orphan_degrade_render_gate.py` — the existing fast offline regression gate for references to non-included documents; its whole premise moves from build-time to compile-time
- `tests/test_citation_degradation_gate.py` — case (iii) at line 1007 and the surrounding WR-03 route cases depend on `degrade_xref_to_text` (D-09)
- `tests/fixtures/bld03_ghost_entry_xref_gate/` and `tests/fixtures/bld03_unhashable_docname_gate/` — both carry load-bearing-property comment blocks in their `conf.py`; read those before touching either fixture
- `tests/test_corpus_gate.py` — the full-corpus `-b typstpdf` gate, which carries no timing instrumentation today (D-11)
- `tests/test_translator.py:1973` and `:2001` — the only existing `pending_xref` coverage (D-04)

### Published contracts

- No user-facing documentation describes the degrade behaviour. `grep -rn "non-included\|degrade" docs/source/` returns zero, so D-01 changes no published contract. Confirm this still holds at implementation time rather than assuming it.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets

- `_namespace_label(docname, raw_id)` (`translator.py:4579`) is D-13's single label-derivation point. Every guarded site must compute its label through it, never through a second spelling — this is the same rule Phase 40.1's D-07 established for the citation anchor.
- `_resolve_xref_docname(refuri)` survives untouched. It answers "is this a cross-document reference, and what are its target docname and anchor" — a question that is still a build-time question. Only the *safety* question moves to compile time.
- `_is_usable_typst_documents_entry()` (`builder.py:106-164`) survives for its four remaining consumers: the collision validator, `write()`'s D-07 wrapper report, `_write_typst_files()`'s wrapper loop, and `TypstPDFBuilder.finish()`.
- `tests/test_pdf_render_gate.py` established the `sphinx-build → typst.compile() → pypdf` acceptance-fixture pattern this phase's SC#1 needs (a real link annotation in one master's PDF, none in the other's, no `TypstError` in either).

### Established patterns

- Every emission site streams: `visit_*` opens, children walk, `depart_*` closes. `visit_citation` is the one exception (it buffer-swaps `self.body`). D-07 was chosen to preserve the streaming pattern rather than convert the streaming sites to buffering.
- Pre-fix REDs are recorded as `xfail(strict=True)` with the verbatim transcript in a separate `*-RED-EVIDENCE.md`, per Phase 47 plan 13's convention.
- Fixture `conf.py` files carry a "Load-bearing properties — do NOT touch any of these" comment block naming what would silently stop the fixture exercising its defect. Follow that convention for any new fixture.

### Integration points

- The three emission sites are the only places a Typst `<label>` is *referenced*. Sites that *attach* labels (`depart_term`, `_emit_id_anchors`, figure/table/footnote anchors) are unaffected — they are the supply side, and the guard is on the demand side.
- `builder.master_included_docnames` is read only from `_reference_anchor_decision`. Once that read is gone the attribute has no consumer, which is what makes SC#3's grep-zero achievable in one change.
- The `_StubBuilder` used across `tests/test_citation_degradation_gate.py` sets `master_included_docnames` explicitly; every such stub loses that attribute.

</code_context>

<specifics>
## Specific Ideas

- The exact emission shape the owner selected for D-07, as sketched during discussion:

  ```typst
  #context { let __b = [Only In X]
    ; if query(<onlyx:onlyx-label>).len() > 0
      { link(<onlyx:onlyx-label>, __b) } else { __b } }
  ```

  Body on disk once, no buffering, one contract for all three sites. Treat the syntax as a sketch to
  verify, not as measured fact (D-08).

- The owner's answer on standalone content-file compilation was that it needs no mitigation and no
  handoff note — the guard making all cross-references degrade silently in that mode is acceptable as
  is, and does not become a documentation obligation for this phase.

</specifics>

<deferred>
## Deferred Ideas

- **Replacing `query(<L>)` with a `state("inc", ())` lookup** — only becomes possible once Phase 49
  introduces the state-published include set. Filed here as the named remediation path for D-11's
  top tier, not as work for this phase.

### Reviewed Todos (not folded)

`gsd-tools query todo.match-phase 48` returned six matches; none were folded, because every one is
already owned elsewhere:

- `2026-08-10-rehomed-converted-image-collides-with-srcdir-images-dir.md` — ROADMAP assigns it to Phase 50 (IMG-01)
- `2026-08-10-track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri.md` — ROADMAP assigns it to Phase 50 (IMG-02)
- `2026-08-05-shared-document-silently-dropped-from-all-but-first-master.md` — this is defect A, owned by Phase 49 (COMP-07)
- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` — local toolchain, unrelated to this phase's scope
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` — explicitly forbidden this milestone by binding constraint #9
- `2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` — release automation, closed at `/gsd-complete-milestone`

</deferred>

---

*Phase: 48-Compile-Time Cross-Reference Guard*
*Context gathered: 2026-08-12*
