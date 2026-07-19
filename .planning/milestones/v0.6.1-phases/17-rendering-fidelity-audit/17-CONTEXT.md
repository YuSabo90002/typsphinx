# Phase 17: Rendering-Fidelity Audit - Context

**Gathered:** 2026-07-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Produce a written, severity-rated catalogue of *silent* mis-render issues — output that compiles
fatal-free AND emits no warning, yet diverges from the source — by visually diffing the compiled
Sphinx-`doc/` corpus PDF (v9.1.0, ~14.4 MiB, GATE-02 green) against the same corpus's rendered
HTML. This is the **discovery core** of milestone v0.6.1: warnings only surface *dropped* content,
so a human-assisted visual audit is the only way to find silent divergence.

**The phase's output is a catalogue artifact + a REQUIREMENTS.md append, not code.** No translator
changes, no new node handlers, no new runtime dependencies. Concretely (ROADMAP SC#1–4):

1. The full corpus is compiled to PDF via `typstpdf` and visually compared, page by page, against
   the baseline.
2. A catalogue artifact lists every silent mis-render with location (docname + node kind), a
   source-vs-output description, and a severity rating (high / medium / low).
3. In-scope silent mis-renders are distinguished from known out-of-scope degradations
   (graphviz/inheritance placeholders, non-included-doc xrefs, Sphinx-side autodoc/`py:meth`
   warnings — see REQUIREMENTS.md Out of Scope table).
4. Every "high" issue is enumerated as the FID-01 fix backlog and appended to
   `.planning/REQUIREMENTS.md` as `FID-01a`, `FID-01b`, … for Phase 18 to consume.

Depends on Phase 16 (already complete): the audit runs with the `todo_node`/`manpage` handlers
landed, so it surfaces genuinely-silent divergence.

</domain>

<decisions>
## Implementation Decisions

### Audit division of labor (human-assisted = Claude-first, human-confirmed)
- **D-01: Claude does the first pass; the human confirms.** Claude renders the corpus PDF pages to
  images, reads them itself, cross-checks against the baseline, and builds a candidate-issue list.
  The human's role is confirming candidates and finalizing severity — not paging through hundreds
  of pages themself.
- **D-01a: The human confirms ALL candidates + spot-checks the "clean" set.** Every candidate is
  human-reviewed for accept/reject and severity. Additionally the human spot-checks a few pages
  Claude marked clean, to estimate the miss rate. This is the evidentiary bar for FID-01 (Phase 18
  work is scoped by these confirmations).
- **D-02: Progress is tracked per docname.** Audit progress ("audited / not yet") is recorded per
  document (.rst file), matching the catalogue's location key and giving clean session-resume
  boundaries. Expect the audit to span multiple sessions; the tracking artifact must survive
  interruption.
- **D-03: Uncertain cases go INTO the candidate list, flagged "uncertain."** When Claude cannot
  tell whether a divergence is an in-scope mis-render or an acceptable media difference, it
  includes the item as a flagged candidate for human judgment. Bias toward false positives, never
  silent false negatives.

### Comparison baseline
- **D-04: The rendered HTML build is the authority; rST source is the tiebreaker.** "Faithful"
  means faithful to what Sphinx itself renders (post-toctree/xref-resolution, post-autodoc). Read
  the rST source only when intent needs confirming.
- **D-05: Build the HTML baseline locally from the SAME cached corpus.** `sphinx-build -b html`
  against `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc` (tag v9.1.0, SHA `cc7c6f4…`,
  the exact tree the PDF is built from — provenance per 15-CORPUS-REPORT.md). Never compare
  against www.sphinx-doc.org (version skew → false positives).
- **D-06: Divergence = content + structure + meaning-bearing style.** In scope: content
  loss/duplication/misordering; structural breakage (lists, tables, heading hierarchy); loss of
  meaning-bearing styling (literal/code text rendered as prose, lost emphasis, links flattened to
  plain text, table column misalignment). Out of scope: pure appearance differences (colors,
  fonts, margins, page breaks, theme chrome like sidebars/navigation) — these are expected
  PDF-vs-HTML media differences, not mis-renders.

### Catalogue format & severity rubric
- **D-07: Catalogue = `17-AUDIT-CATALOGUE.md` in the phase directory** (the 15-CORPUS-REPORT.md
  precedent): a single committed Markdown with a provenance header (corpus tag/SHA, typst version,
  build command) + the issue records. Phase 18's planner reads it directly. No GitHub issues, no
  committed screenshots.
- **D-08: Severity rubric — the axis is "what does the reader lose":**
  - **high** (locked by SC#4): content lost, unreadable, or grossly mis-structured.
  - **medium**: content readable but meaning or distinction lost (code-literal rendered as prose,
    lost emphasis, link flattened to plain text, table column shift, …).
  - **low**: meaning intact but finish is sloppy (stray whitespace, indentation wobble, …).
- **D-09: Per-issue record = SC#2's required 3 fields + reproduction info.** Each issue records:
  docname + node kind; source-vs-output description; severity; PDF page number; occurrence count
  (same root cause); and a minimal reproducing rST snippet (or a pointer to the corpus source
  line). Phase 18 fix-plans and their regression fixtures start directly from the catalogue.

### FID-01 backlog granularity
- **D-10: One FID-01x per ROOT CAUSE, not per occurrence.** The same translator defect appearing
  in N places is ONE requirement, with occurrence locations listed inside it. This matches Phase
  18's unit of work (handler-level fixes) and maps 1:1 to fix plans.
- **D-11: Only "high" issues become FID-01a…; medium/low go to Future Requirements.** The
  REQUIREMENTS.md append registers exactly the high-severity root causes as FID-01a, FID-01b, …
  (SC#4 as written). Medium/low stay fully recorded in the catalogue, referenced from
  REQUIREMENTS.md "Future Requirements" as a single pointer entry (next-milestone candidates) —
  v0.6.1 scope does not grow.

### Claude's Discretion
- PDF page-image extraction tooling and resolution (e.g. pdftoppm/mutool), and how pages are
  batched per session.
- Exact tabular schema/column layout of `17-AUDIT-CATALOGUE.md` and of the per-docname progress
  tracker (a checklist inside the catalogue or a sibling file — planner's choice, as long as it is
  committed and resumable, per D-02).
- How the HTML baseline build handles the corpus conf's doc-build-only extensions (same
  install-vs-degrade judgment Phase 15 already made for `typstpdf`; reuse its wiring approach).
- Any low-cost mechanical pre-filters (e.g. text-extraction diff) Claude uses internally to
  prioritize its own first pass — provided every page still gets a visual look (SC#1's
  page-by-page bar) and the D-01a confirmation flow is unchanged.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — AUD-01 (the phase's sole requirement), FID-01 (the append target,
  §"Rendering Fidelity Audit"), and the **Out of Scope table** that defines the known out-of-scope
  degradations SC#3 must exclude.
- `.planning/ROADMAP.md` §"Phase 17: Rendering-Fidelity Audit" — the four Success Criteria and the
  milestone invariants (no new deps, `@preview` sync surface untouched).

### Corpus provenance & tooling (Phase 15 artifacts this phase reuses)
- `.planning/phases/15-full-corpus-validation/15-CORPUS-REPORT.md` — corpus provenance (tag
  v9.1.0, SHA `cc7c6f435ad37bb12264f8118c8461b230e6830c`, cache path
  `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/doc`), the provenance-header precedent D-07
  follows, and the warning-audit baseline (only `todo_node`/`manpage` were content drops — both
  fixed in Phase 16).
- `tests/test_corpus_gate.py` — the working corpus acquisition/caching + `sphinx-build -b
  typstpdf` wiring (real `doc/conf.py` + 2-line typsphinx append). The audit's PDF build and the
  D-05 HTML baseline build should reuse this machinery/approach rather than reinvent it.
- `.planning/phases/15-full-corpus-validation/15-CONTEXT.md` — D-01/D-03 corpus decisions (pinned
  tag matching `sphinx.__version__`; real conf as-is) that carry forward to the HTML baseline
  build.

### Downstream consumer contract
- `.planning/ROADMAP.md` §"Phase 18" — what Phase 18 needs from the catalogue: per-high-issue fix
  plans, each with a real `typst.compile()` regression fixture (GATE-01 pattern). D-09's
  reproduction info exists to serve this.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/test_corpus_gate.py`: corpus clone/cache logic, conf wiring, and the full
  `sphinx-build -b typstpdf` drive — the audit compiles the PDF the same way (and the HTML
  baseline is the same tree with `-b html`).
- `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/`: the corpus is already cached locally; no
  network needed unless the cache was cleared.
- `.planning/phases/15-full-corpus-validation/15-CORPUS-REPORT.md`: the committed-report format
  precedent (provenance header + tables) that `17-AUDIT-CATALOGUE.md` mirrors.

### Established Patterns
- Discovery phases produce committed phase-directory artifacts, not code (15-CORPUS-REPORT.md
  precedent).
- Every Phase-18 fix will need a GATE-01 real-compile fixture — the catalogue's minimal-repro
  field (D-09) is deliberately shaped as fixture input.
- Known out-of-scope degradations are already enumerated in REQUIREMENTS.md's Out of Scope table
  and STATE.md's blocker note — the audit classifies against that list, it does not re-litigate it.

### Integration Points
- `17-AUDIT-CATALOGUE.md` → read by Phase 18's planner (per-issue fix plans).
- `.planning/REQUIREMENTS.md` → FID-01a… appended under §"Rendering Fidelity Audit" (high only,
  root-cause granularity); medium/low pointer added under §"Future Requirements".
- Environment note: the NixOS sandbox cannot run the real corpus builds (~45 integration tests
  fail environmentally); the actual compile + audit runs need the full local env, as Phase 15's
  measurement did.

</code_context>

<specifics>
## Specific Ideas

- Severity examples the user locked in (D-08): code-literal → prose, lost emphasis, link → plain
  text, table column shift are **medium**; stray whitespace / indentation wobble are **low**.
- The audit is explicitly biased toward false positives (D-03): "when in doubt, flag it" — the
  human confirmation step (D-01a) is the filter.
- PDF and HTML are different media: page breaks, fonts, theme colors, sidebars are never findings
  (D-06).

</specifics>

<deferred>
## Deferred Ideas

- **Medium/low fidelity fixes** — recorded in the catalogue and pointed to from Future
  Requirements (D-11), but NOT part of v0.6.1's Phase 18 obligation (high only, per SC#4).
- **Committed screenshot evidence per issue** — considered for the catalogue (D-07/D-09); rejected
  to keep the repo lean. Page numbers + repro snippets are the durable evidence; images stay
  session-local.

None of the above are blockers; captured so they are not lost.

</deferred>

---

*Phase: 17-rendering-fidelity-audit*
*Context gathered: 2026-07-16*
