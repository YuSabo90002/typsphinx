# Phase 19: Block Separation Fixes (Cluster A) - Context

**Gathered:** 2026-07-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Restore lost inter-block / inter-element separation across five audit findings
(FID-02..FID-06 = F1/F7/F13/F14/F15) — the dominant v0.6.1-audit root cause — as
one coherent set of `visit_*`/`depart_*` separator fixes in `typsphinx/translator.py`,
so every affected construct renders with the visible separation the `-b html`
authority shows instead of concatenating.

**Root cause (confirmed in code):** all five findings share one mechanism — in Typst
**code mode**, a literal `\n`/`\n\n` (source newline) between two statements produces
**zero visual break**. The translator relies on `\n` for separation at these sites, so
the break never renders. The repo already knows this: `visit_desc_signature_line`
(translator.py ~4392) emits an explicit `linebreak()` with the comment "a source '\n'
between two code-mode statements is proven cosmetic-only." That is the fix idiom.

**The five sites (per node context — each needs a DIFFERENT break kind):**
- **FID-02 (F1)** — consecutive `paragraph`s inside a `list_item`: `visit_paragraph`/
  `depart_paragraph` (translator.py ~661–708) early-return when `in_list_item`, emitting
  neither `par()` nor any separator → "role.For example". Corpus-wide, highest blast radius.
- **FID-03 (F7)** — sibling `desc_signature`s (overloads / `alias` groups / multi-option
  directives): `depart_desc_signature` (~4339) appends only `\n` (cosmetic) → run together
  on one line.
- **FID-04 (F13)** — `rubric` option-group heading (and directive-option "Options" heading):
  `depart_rubric` (~4671) appends only `\n` (cosmetic) → merges onto the first following
  `option`/`:field:`.
- **FID-05 (F14)** — `definition_list` `term`↔`definition` when the list is nested in a
  `list_item`, or the definition body opens with a nested list: emitted `terms(...)` items
  put term and definition on one line (`depart_definition_list` ~1672).
- **FID-06 (F15)** — back-to-back body-less `confval` `desc` nodes: `depart_desc` (~4318)
  appends only `\n\n` (cosmetic) → four confvals merge into one unbroken blob.

**Out of scope:** intra-signature *token* spacing (Cluster B / Phase 20 — `class ` prefix,
C/C++ inter-token, `:type:`/`:default:` colon-space), and all Cluster C/D/E/F findings
(Phase 21). This phase is separator/break restoration only — no new constructs, no
`@preview` bump, no version-sync-surface changes.

</domain>

<decisions>
## Implementation Decisions

### Fidelity target level
- **D-01:** Match the `-b html` authority **per-construct** — do NOT apply a single uniform
  break everywhere. The break *kind* follows what HTML renders for that construct:
  - paragraphs-in-list-items (F1) → paragraph break (`parbreak()`, vertical space)
  - sibling `desc_signature`s (F7) → line break (`linebreak()`, stacked lines)
  - rubric/option heading (F13) → heading on its own line, then the option separately
  - definition `term` (F14) → term on its own line, definition indented below
  - back-to-back body-less confvals (F15) → block separation between entries
- **D-02:** Rejected the "minimum anti-collision" (one uniform light break / single space)
  approach. The ROADMAP goal is explicit: "renders with the visible separation the `-b html`
  authority shows." A weaker target risks under-delivering FID's "visible separation."

### Separator-fix structure
- **D-03:** Build **one small shared helper** reused at all five sites, parameterized by
  break kind. The helper respects the existing `list_item_needs_separator` machinery
  (translator.py — the `if self.in_list_item and self.list_item_needs_separator: add_text("\n")`
  … `self.list_item_needs_separator = True` idiom) and emits the caller-supplied break token
  (`parbreak()` / `linebreak()`). Each of the five call sites chooses its own break kind
  (per D-01).
- **D-04:** Rejected fully-independent 5-point fixes (zero sharing) — inconsistency/duplication
  risk, and Phase 20 will touch the same `desc_*`/signature surface, so a settled shared idiom
  is the foundation it builds on. Also rejected a single monolithic primitive that emits an
  identical break everywhere — the break kind genuinely varies by construct (D-01), so one-size
  does not fit and would carry the largest blast radius into the ~684-page corpus gate.

### Verification strategy (GATE-01)
- **D-05:** These are **non-fatal visual** fixes — the pre-fix translator compiles cleanly, so
  a bare `%PDF`-magic / compile-success assert proves nothing ("would fail without the fix" is
  unmet). Each fixture MUST **structurally assert the generated `.typ`** contains the expected
  separator token (`parbreak()` / `linebreak()`) at the correct site, AND run a real
  `typst.compile()` producing a valid `%PDF`. Pre-fix output has only cosmetic `\n` and no
  token → the assert fails; post-fix it passes. This mirrors the established repo idiom in
  `tests/test_desc_signature_concat_render_gate.py` (assert on emitted `.typ` structure +
  real-compile PDF magic).
- **D-06:** Rejected rasterize-and-check-glyph-position (poppler-dependent, brittle, slow,
  inconsistent with the milestone's other gates) and did NOT adopt pypdf text-extraction as a
  requirement (the lighter structural-assert path was chosen). A planner MAY optionally add a
  pypdf extracted-text adjacency check (e.g. absence of "role.For") for the observable cases
  (F1/F13/F15) as a *strengthening*, but it is not required and cannot detect paragraph
  vertical spacing anyway.

### Claude's Discretion
- **Fixture granularity/placement** (offered as a 4th gray area, not selected — planner's call):
  Recommended default is **one render-gate fixture per finding**, extending existing modules
  where a direct analog already exists — `tests/test_desc_signature_concat_render_gate.py`
  (F7) and `tests/test_deflist_term_concat_render_gate.py` (F14) — and adding new modules for
  F1/F13/F15. This follows the repo's "one gate module = one concern" convention. A planner may
  consolidate if a shared fixture project cleanly exercises multiple findings, provided each
  finding retains an assertion that would fail against the pre-fix translator.
- **Exact break-token choice per site** — `parbreak()` vs `linebreak()` vs a `par()`-wrap is
  fixed in intent by D-01 (kind per construct) but the precise Typst emission (and any
  interaction with the `{ }` list-item content block) is an implementation detail for
  research/planning to settle against real compiles.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Source of record for every FID finding
- `.planning/milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md` —
  the D-07 audit catalogue. Issue Table rows **1 (F1/FID-02)**, **7 (F7/FID-03)**,
  **13 (F13/FID-04)**, **14 (F14/FID-05)**, **15 (F15/FID-06)** carry docname + node kind +
  minimal repro + file/line pointers for each of this phase's five findings. Severity-final,
  D-01a human-confirmed at the 17-03 gate.

### Requirements + roadmap
- `.planning/REQUIREMENTS.md` §"Block Separation (Cluster A …)" — FID-02..FID-06 requirement
  text + F-number traceability; milestone invariant (zero new runtime deps, no `@preview`
  bump); GATE-01 standing bar.
- `.planning/ROADMAP.md` §"Phase 19: Block Separation Fixes (Cluster A)" — goal, 5 success
  criteria, and the standing real-`typst.compile()` acceptance-fixture bar.

### Code + established idioms to reuse (not modify beyond scope)
- `typsphinx/translator.py` — the five handler sites above; `list_item_needs_separator`
  machinery; the `visit_desc_signature_line` `linebreak()` cosmetic-newline precedent (~4392).
- `tests/test_desc_signature_concat_render_gate.py` — the canonical GATE-01 fixture shape
  (emitted-`.typ` structural assert + real `-b typstpdf` compile + `%PDF` magic; invoked via
  `sys.executable -m sphinx`, never `uv run`, per the NixOS-sandbox PATH hazard).
- `tests/test_corpus_gate.py` — the standing full-corpus (~684-page) regression gate the
  separator changes must not regress.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`list_item_needs_separator` machinery** (translator.py, ~30 call sites): the existing
  in-list-item separator flag pattern the shared helper (D-03) must respect and drive.
- **`linebreak()` cosmetic-newline idiom** (`visit_desc_signature_line`, ~4392): the proven
  precedent that a real Typst stdlib break — not `\n` — is required for a visible break in
  code mode. The shared helper generalizes this.
- **GATE-01 fixture template** (`test_desc_signature_concat_render_gate.py`): copy its shape
  for the new/extended cluster-A fixtures.

### Established Patterns
- **Code mode `\n` is cosmetic-only** — the invariant behind all five findings; the shared
  helper must emit `parbreak()`/`linebreak()`, never rely on `\n` for a visible break.
- **List-item `{ }` content blocks** (`visit_list_item`/`depart_list_item`, ~1410): paragraphs
  in list items are currently NOT wrapped in `par()` (early-return) to avoid invalid `- par(...)`;
  now that items use `{ }` blocks, the F1 fix must reconcile with this (par-wrap vs parbreak-inject
  is an implementation choice for research/planning).
- **`desc_signature` delegates to `visit_strong`/`depart_strong`** — the F7/F13 fixes sit around
  this delegation; `_is_first_desc_signature_line` reset already exists per signature.

### Integration Points
- All five fixes land in `typsphinx/translator.py` only. No `builder.py`/`writer.py`/
  `template_engine.py`/`templates/base.typ` changes (version-sync surface stays untouched).
- Phase 20 (Cluster B) builds directly on the settled separator idiom on the `desc_*`/signature
  surface — keep the shared helper clean and documented for that handoff.

</code_context>

<specifics>
## Specific Ideas

- Every fix ships or extends a **real** `typst.compile()` regression fixture that would FAIL
  against the pre-fix translator (structural `.typ` token assert + `%PDF` compile). String-
  agreement asserts alone never suffice (GATE-01).
- Milestone invariant reaffirmed: **zero new runtime dependencies, no `@preview` version bump,
  the 3-way version-sync surface (`writer.py` / `template_engine.py` / `templates/base.typ`)
  stays untouched.** Flag during planning if any target is found to need otherwise.
- Fidelity authority is `-b html` (with `-b text` as a secondary baseline), per the audit
  catalogue's D-04/D-08 convention.

</specifics>

<deferred>
## Deferred Ideas

- **pypdf extracted-text adjacency assertions** as an *optional* strengthening for the
  observable findings (F1/F13/F15) — not required this phase (D-06); a planner may add if cheap.
- **Rasterized glyph-position verification** — rejected for this milestone (D-06); would only be
  revisited if a future finding genuinely cannot be verified structurally.
- Cluster B token-spacing (FID-07..FID-09) → Phase 20; Clusters C/D/E/F (FID-10..FID-14) →
  Phase 21; Issue #117 PDF naming (PDF-01) → Phase 22. Explicitly out of Phase 19.

None from scope creep — discussion stayed within phase scope.

</deferred>

---

*Phase: 19-Block Separation Fixes (Cluster A)*
*Context gathered: 2026-07-20*
