---
phase: 48
reviewers: [claude-sonnet, claude-fable]
reviewed_at: 2026-08-12T12:46:18+09:00
plans_reviewed:
  - 48-01-PLAN.md
  - 48-02-PLAN.md
  - 48-03-PLAN.md
  - 48-04-PLAN.md
reviewer_instances:
  claude-sonnet: { cli: claude, model: claude-sonnet-5 }
  claude-fable:  { cli: claude, model: claude-fable-5 }
---

# Cross-AI Plan Review — Phase 48

> **Shared-adapter caveat.** Both reviewers ran through the `claude` lane on different models
> (Sonnet 5, Fable 5), in separate headless sessions with repo read access. No third-party CLI
> (gemini/codex/opencode/qwen/cursor) is installed on this host and no local model server was
> reachable, so cross-*vendor* independence was not available for this pass. Two same-adapter
> instances share tokenizer, training lineage, and harness — treat their agreement as weaker
> evidence than agreement between distinct vendors would be.
>
> **Orchestrator verification.** Every HIGH and MEDIUM finding below was independently re-checked
> against the tree by the orchestrating session before being recorded. Each carries an explicit
> `Verified:` line. Findings are not passed through on the reviewer's word.

## Claude Review (claude-sonnet)

# Code Review: Phase 48 Plans (48-01 … 48-04)

`REVIEWED-WITH-REPO-ACCESS` — read `typsphinx/translator.py:3011-3103`, `:3240-3300`, `:4262-4310`,
`:2610-2705`, `:4930-5030`, `typsphinx/builder.py:90-170,240-260,730-760` and the referenced test
files.

### Summary

An unusually well-grounded plan set: nearly every claim about current code shape, line numbers, and
Typst syntax pitfalls was independently verified in RESEARCH.md via real `typst.compile()` and
`sphinx-build` runs rather than assumed. The four-plan structure (write-first REDs → tracer on the
primary site → expand to the other two sites → cost measurement and closeout) correctly sequences
risk: the riskiest unmeasured design element (D-08's body-mode question — code-mode `[#{`…`}]` vs.
markup-mode `[`…`]`) is deferred to a live measurement step inside 48-02 Task 1 rather than assumed
at planning time. The main residual risks are (1) that measurement being deferred to execution time
rather than closed in research, and (2) two structurally significant behavior changes shipping as
accepted regressions (D-09's new citation markers, D-01's warning removal) whose
backward-compatibility blast radius is asserted rather than measured against the real corpus.

### Strengths

- **The D-06 same-document exemption is defended by an explicit negative test, not just
  documentation.** 48-03 Task 3 assertion #7 renders both `visit_reference`'s bare-refid branch
  (`translator.py:4941-4950`) and the `#`-prefixed branch and asserts neither contains the guard's
  conditional — guarding the most likely scope-creep failure mode (an executor "fixing" all of
  `visit_reference` uniformly).
- **The tracer pattern (48-02 Task 1) fires before the expensive parts (48-03) run**, and the
  dependency chain 48-01 → 48-02 → 48-03 → 48-04 is correctly serialized.
- **Body-mode uncertainty is treated as a real open question, not hand-waved.** 48-02 Task 1 Step 1
  requires a throwaway compile probe of the `[#{...}]` code-mode spelling before writing any
  translator code, with an explicit fallback to bare `[...]`. RESEARCH.md itself only validated the
  markup-mode variant, not `visit_reference`'s actual code-mode child-streaming context.
- **The D-04/D-05 split correctly reflects RESEARCH.md's empirical findings** — D-04 (pending_xref)
  is treated as unconstructible-RED with an enumerated impossibility argument rather than a
  fabricated fixture, while D-05 (citation-in-caption) is a real reproduced fatal with a committed
  RED fixture. Confirmed against source: `visit_caption` at `translator.py:2670-2671` raises
  `SkipNode` when `in_captioned_code_block`, and `_find_citing_reference` (`:3006-3009`) scans via
  `document.findall`, independent of the walker.

### Concerns

- **MEDIUM — Label-collision false-negative is architecturally accepted, not just a corner case.**
  Nothing verifies that two distinct raw ids sanitizing to the same string can't make an *absent*
  target appear *present*. 48-03 Task 3 assertion #5 explicitly accepts this. A genuinely broken
  reference (coincidentally-colliding label) would silently render as a *working* link post-guard
  rather than degrading — a new false-negative class the build-time mechanism didn't have (it
  checked docname membership, not label existence).
- **MEDIUM — D-09's citation-marker regression is asserted backward-compatible-by-design but not
  verified against the full corpus.** No plan runs a citation-marker *count* delta pre/post-fix;
  `test_corpus_gate.py` only asserts no fatal, which wouldn't catch "an extra `[1]` marker now
  appears".
- **MEDIUM — Performance risk (D-11) is real and unbounded until measured.** All three sites now do
  a `context`+`query` pass per reference; RESEARCH.md's assumption A3 flags the 28.93s/28.56s
  baseline as machine-specific. A top-tier (>100%) result hands Phase 49 — already carrying 8
  requirements — an unplanned performance-fix obligation.
- **LOW — `visit_pending_xref`'s hardcoded `#` prefix is preserved unfixed by explicit decision**
  (48-03 Task 2). Defensible per D-04's scope, but if Assumption A2 (no third-party extension
  reaches this path) is wrong, the guard's shape assumes a fixed prefix that may not match the
  surrounding mode.
- **LOW — 48-01's fixture assumes bravo's wrapper produces literally zero `/Link` annotations.** A
  fragile invariant coupled to template internals.

### Suggestions

- Add one real-compile check confirming a label collision across two documents does not cause the
  guard to falsely report "present".
- In 48-04 Task 2, add an explicit citation-marker-count assertion (before/after) so D-09 has a
  concrete transcript rather than resting solely on the same-document-anchor argument.
- Consider pulling the body-mode measurement forward out of 48-02 Task 1 — a failed probe mid-plan
  means re-deriving the guard shape under time pressure inside an already-large task.

### Risk Assessment

**MEDIUM.** Residual risk is concentrated in two design-inherent places: a new false-negative class
from label-collision masking, and an open-ended performance regression whose remediation depends on
Phase 49. Neither blocks proceeding, but both deserve explicit owner sign-off.

---

## Claude Review (claude-fable)

# Cross-AI Plan Review — Phase 48 (Plans 48-01 … 48-04)

### Summary

Unusually well-grounded plans: every cited line number checked resolves exactly
(`builder.py:255/257/758`, `translator.py:3071-3077/4941-4950/4980-4984/4985-5007/3267-3284/
4262-4303`), the "three demand-side emission sites plus `pending_xref`" claim survives an
independent repo-wide grep, and the write-expected-first / RED-evidence discipline is real,
enforced by concrete acceptance greps. However, there is one **HIGH** internal factual error: plan
48-01's characterization of the two-master fixture's pre-fix behavior is **inverted**, and this
propagates into a wrong xfail/plain-test assignment that will break Wave 1's own green gate.

### Strengths

- **The single-choke-point claim is true.** Demand-side emissions are exactly `translator.py:3273`,
  `:3281` (citation backrefs), `:4291` (`pending_xref`), and `:4950`/`:4984`/`:5007`
  (`visit_reference`'s three branches). Everything else is supply-side anchor attachment. The site
  inventory is complete.
- **D-10's test arithmetic checks out.** `tests/test_master_include_set_predicate_gate.py` has
  exactly 8 `def test_` (lines 103, 129, 165, 196, 227, 260, 288, 319); the four to delete (165,
  260, 288, 319) call `_compute_master_included_docnames()` directly.
- **Case (iii) flip is correctly located**: `test_citation_degradation_gate.py` parametrizes
  `("refuri_excluded_document", _wr03_case_refuri_excluded_document, False)` exactly as D-09
  describes.
- **The docstring correction (FIVE→FOUR) is real** — `builder.py:110-116` names
  `_compute_master_included_docnames()` as the fifth consumer verbatim.
- **Pitfall-1's syntax hazard (unbroken `if … {`) is baked into acceptance criteria as byte-level
  greps**, not prose guidance.
- **The tracer-first structure (48-02) is right** — proving the streaming open/close through
  `depart_reference` on one path is where an architectural dead end surfaces cheapest.

### Concerns

- **HIGH — Plan 48-01's pre-fix RED narrative for `xref_per_master_guard_gate` is inverted, and
  Task 3's xfail/plain split will fail Wave 1's own gate.** Task 1 claims "the build-time union
  suppresses the link for bravo and emits it for index … the two files DISAGREE at write time",
  prescribing a hand-edited reconstruction to demonstrate the fatal. But
  `_compute_master_included_docnames()` is a **union across all masters**: `index`'s toctree pulls
  `target` into the union, so bravo's byte-identical `:ref:` also resolves with
  `degrade_xref_to_text = False` and **bravo.typ emits a real `link(<target:…>, …)` too** — the two
  content files *agree* at write time, and bravo's wrapper compile fails directly with
  `label … does not exist in the document` on the unfixed tree (no hand-edit needed). Consequence:
  Task 3's test 4 ("neither compile raises a Typst error; build exits 0 — *already passes today*,
  written as a plain non-xfail invariance guard") is wrong — pre-fix `-b typstpdf` on this fixture
  exits nonzero, so the plain test fails and Task 3's verify cannot pass in Wave 1. Test 4 must be
  a strict xfail naming 48-02, and the RED evidence should record the direct fatal, which is
  *stronger* evidence.
- **MEDIUM — The "exactly zero `/Link` annotations in bravo.pdf" derivation conflates toctree with
  `outline()`.** `templates/base.typ` calls `outline(...)` **unconditionally**; Typst's `outline()`
  enumerates document *headings*, not toctrees, and each entry is a GoTo `/Link` annotation. If
  bravo contributes any heading, bravo.pdf carries outline link annotations and the zero-count
  assertion fails for reasons unrelated to the guard. Either pin "bravo.rst carries no section
  heading" as a load-bearing property, or assert destination-based (`target:…` ∉ dests) instead of
  `len == 0`.
- **MEDIUM — Guard close-string interplay with `_reference_own_anchor` is unverified.**
  `depart_reference` emits `)` then, when the reference owns an anchor, `#label("…")]` — a markup
  bracket-wrap opened back in `visit_reference`. Replacing `)` with the guard's close changes the
  nesting: the anchor's `#label(...)` and closing `]` must land *outside* the `context { … }` block,
  and that combined shape was never among the 34 compiled research probes. 48-02 says "leave the
  `_reference_own_anchor` bookkeeping unchanged" but never adds this combination to the Step-1 probe
  set.
- **MEDIUM — D-09 lands in Wave 2 but the citation guard lands in Wave 3.** Making `opens_wrapper`
  unconditional in 48-02 makes previously-degraded citing sites eligible immediately, while the
  backref-loop guard arrives only in 48-03. The gap is covered *only* because the citation-caption
  gate stays xfail through Wave 2 — acceptable, but never stated. Worth one sentence in 48-02
  confirming no non-xfail gate crosses the window.
- **LOW/MEDIUM — Brittle acceptance grep in 48-01 Task 3**: "`grep -Ec 'reason=' …` equals the count
  of lines matching `48-0`" — `skipif` decorators also carry `reason=` strings containing no
  `48-0`, so the criterion fails as literally written. Rephrase to count only `xfail` reasons.
- **LOW — edge/adjacency truth in 48-03 overstates what string-level tests prove.** Typst can error
  on a `link()` to an ambiguously-attached label even when `query().len() > 0`; no real compile
  covers this. The wording claims only "no *new* failure", which is true, but reads as verified
  behavior.
- **LOW — false-negative visibility loss is real but accepted.** Post-D-01 an `:orphan:`-target
  reference degrades with zero diagnostic at any layer. Deliberate, owner-locked (D-01); noted for
  completeness.

### Suggestions

1. Rewrite 48-01 Task 1 failure-mode-1 and Task 3's test allocation per the HIGH finding.
2. Change the bravo-side SC#1 assertion from count-zero to destination-based, and drop the "no
   toctree → no outline links" rationale.
3. Add the own-anchor combination to 48-02 Step 1's probe set.
4. Fix the `reason=` counting grep in 48-01 Task 3.
5. Optional: since the pre-fix fatal is directly reachable, RED-EVIDENCE failure mode 1 can be a
   single verbatim `-b typstpdf` transcript — less machinery, stronger evidence.

### Risk Assessment

**MEDIUM.** Risk is concentrated in Wave 1: the inverted pre-fix narrative will make 48-01 fail its
own verify as written, forcing the executor into deviation handling on the phase's foundational
evidence artifacts — recoverable, but exactly where binding constraint #6's pressure makes
improvisation most dangerous. Fix the HIGH and the two MEDIUMs and this drops to LOW.

---

## Consensus Summary

Both reviewers rate the plan set **unusually well-grounded** and both land on overall risk
**MEDIUM**. Neither recommends abandoning or restructuring the design; both say the phase goal
(XREF-03 / XREF-04, SC#1–4) is achieved by these plans as architected. The disagreement is about
*where* the risk sits — Fable found a concrete Wave-1 blocker, Sonnet found no blocker but two
unmeasured behavioural deltas.

### Blocking finding (verified by the orchestrator)

**Fix before execution — 48-01's pre-fix narrative is inverted (Fable HIGH).**

*Verified:* `_compute_master_included_docnames()` walks BFS "from every master source docname" and
returns "the set of docnames included in **some** compiled master" (`builder.py:257-266, 296-300`)
— a union across all masters. The fixture's own key_link states "only master alpha's toctree
reaches it" (`48-01-PLAN.md`), so `target` enters the union via alpha, and bravo's byte-identical
reference therefore takes the `degrade_xref_to_text = False` path (`translator.py:3070-3078`) and
emits a real `link(<target:…>, …)`. The plan's premise that "the build-time union suppresses the
link for `bravo`" (`48-01-PLAN.md:227-229`) is **wrong**, and test 4's "already passes today"
allocation (`48-01-PLAN.md:436-437`) is wrong with it. **CONFIRMED.**

Two consequences, both worth taking:
1. Wave 1 fails its own verify gate as written — test 4 must become a strict xfail naming 48-02.
2. The RED gets *simpler and stronger*: a direct `-b typstpdf` fatal replaces the hand-edited
   reconstruction at `48-01-PLAN.md:233-236`, which also better satisfies binding constraint #6
   (nothing is derived from a reconstructed artifact).

### Agreed Strengths

- **The site inventory is complete and the single-choke-point claim (SC#2) is true.** Both
  reviewers independently grepped the repo and arrived at the same six demand-side emissions —
  `translator.py:3273`, `:3281`, `:4291`, `:4950`, `:4984`, `:5007`. *Orchestrator-verified:* the
  same six, and note 48-03's must-have correctly names the multi-target *comprehension* at `:3281`
  separately from the single-target spelling at `:3273` — the easiest site to miss.
- **Tracer-first structure and wave serialization are correct** (48-01 → 48-02 → 48-03 → 48-04),
  proving the streaming open/close contract on one path before expanding to three.
- **D-08's body-mode uncertainty is treated as genuinely unmeasured**, with a live compile probe in
  48-02 Step 1 and a stated fallback — both reviewers flagged that RESEARCH.md validated only the
  markup-mode body, not `visit_reference`'s code-mode streaming context.
- **The write-expected-first / RED-evidence discipline is real**, enforced by byte-level acceptance
  greps rather than prose.

### Agreed Concerns

- **The duplicate/colliding-label edge is asserted at string level, never at compile level** (Sonnet
  MEDIUM; Fable LOW). Both note 48-03's edge/adjacency truth is discharged by inspecting the close
  string, with no real `typst.compile()` behind it. *Orchestrator nuance:* Sonnet's framing —
  "some other document in the same compile attaches the same sanitized label" — is **broader than
  the code supports**. Labels are namespaced `docname:id` with `/` → `_u2f_`
  (`translator.py:4579-4601`), so a cross-document false positive additionally requires the
  *docname* segment to collide, not just the id. The concern is real but narrower than Sonnet
  states; the cheap close is one real-compile fixture, which both reviewers recommend.
- **Both rate overall risk MEDIUM** and neither treats any concern as design-invalidating.

### Divergent Views

- **The Wave-1 blocker (HIGH) was found by Fable alone; Sonnet missed it entirely** and in fact
  praised the surrounding structure. Sonnet's LOW about bravo's zero-`/Link` assertion brushes the
  same fixture but stops at "fragile invariant coupled to template internals" without identifying
  the mechanism. Fable named it: `templates/base.typ` calls `outline()` **unconditionally**
  (*orchestrator-verified* at `base.typ:84-87` — only the caption heading above it is conditional),
  and outline entries are GoTo `/Link` annotations. Fable's destination-based fix
  (`target:…` ∉ dests) is the better remedy and should be adopted.
- **Performance (D-11) is Sonnet's top-three concern and Fable does not mention it at all.** Sonnet's
  point that a top-tier result silently hands Phase 49 an unplanned obligation is worth carrying
  even though Fable was silent — it is an argument about phase coupling, not about the code, so
  Fable's silence is not evidence against it.
- **D-09 verification:** Sonnet wants a corpus-wide citation-marker count delta; Fable instead flags
  the Wave-2/Wave-3 *timing window* where `opens_wrapper` goes unconditional before the citation
  guard lands. These are complementary, not competing — the first is about output correctness, the
  second about mid-phase gate colour. *Orchestrator-verified:* the D-09 mechanism is exactly as the
  plans describe — `eligible` gates on `opens_wrapper` and `anchor_label` is `_current_docname()`-
  derived (`translator.py:3086-3090`), so removing the degrade flag does make the marker appear.
  Sonnet's cited line 3251 is off; the substance is right.
- **`visit_pending_xref`'s hardcoded `#` prefix:** Sonnet flags it LOW as a latent bug preserved by
  intent; Fable does not raise it. Consistent with D-04's stated scope either way.

### Recommended action

Take Fable's items 1–4 into a replan before execution (`/gsd-plan-phase 48 --reviews`); they are
narrow, mechanical corrections to 48-01 and 48-02 that do not touch the architecture. Sonnet's two
measurement suggestions (label-collision real-compile fixture, D-09 marker-count delta) are worth
folding into 48-03 and 48-04 respectively. Nothing in either review argues against the phase's
design.
