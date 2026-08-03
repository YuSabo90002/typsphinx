# Phase 40: Citations — Full Round Trip - Context

**Gathered:** 2026-08-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Give docutils citations a real rendering: a document containing `.. [Label]` definitions and
`[Label]_` references stops aborting the Typst compile and instead produces a labelled,
hanging-indent reference list whose entries link back to every citing site docutils recorded, in
document order, with `examples/charged-ieee/` carrying its citation syntax again.

**In scope:**

- New handlers for `docutils.nodes.citation` and `docutils.nodes.label` in
  `typsphinx/translator.py`. Both are unhandled today — measured 2026-08-02, a real
  `sphinx-build -b typst` emits `WARNING: unknown node type: <citation …>` plus a second one for
  `<label>`, and the `.typ` it writes carries `text("Krizhevsky2012")par({…})`, two adjacent
  code-mode expressions.
- Anchoring the *citing* site so a back-reference has a target. Measured: the citing node is a
  plain `nodes.reference` carrying `ids=['id1']`, and `visit_reference`
  (`typsphinx/translator.py:3820`) does not emit an anchor for its own `ids` today.
- `examples/charged-ieee/approach1/source/index.rst` and
  `examples/charged-ieee/approach2/source/index.rst` — restoring what commits `8bed1a3` and
  `c014a0b` stripped.
- The citation half of the test suite: a GATE-01 RED fixture, the layout/back-reference/ordering
  assertions, and the full-corpus `-b typstpdf` gate.
- `.planning/ROADMAP.md` SC#3's wording (corrected by D-06 below).

**Out of scope:**

- Typst's native `bibliography()` / `cite()` machinery. Locked at v0.7.0 scoping — see
  `.planning/REQUIREMENTS.md` § CIT preamble. It consumes structured `.bib`/Hayagriva data in order
  to CSL-format and **reorder**, which is incompatible with CIT-06's "document order, unsorted", and
  there is no structured data to feed it: a docutils citation is already-written prose.
- `sphinxcontrib-bibtex` / the `:cite:` role — deferred as future requirement CIT-07.
- The footnote handlers (`visit_footnote` / `visit_footnote_reference`,
  `typsphinx/translator.py:2510, 2527`). They are the *nearest* prior art and the phase must check
  its separator behaviour against the three protocols directly rather than inheriting theirs by
  analogy (SC#5). Their emitted bytes must not change.
- The `desc_*` family, admonitions and the rubric — Phases 37/38/39 own them and are complete.

</domain>

<decisions>
## Implementation Decisions

Every value below was measured **this session (2026-08-02)** against Sphinx 9.1.0, typst-py 0.15.0
and pypdf, by four means, none from recall:

1. real `sphinx-build -b typst` / `-b html` / `-b latex` runs over a hand-written two-document probe
   with a forward reference, a repeated citation, a cross-document citation and an uncited entry;
2. dumping the pre- and post-transform doctrees (`env.get_doctree` vs
   `env.get_and_resolve_doctree`) to see which nodes actually reach the translator;
3. real `typst.compile()` runs over hand-written `.typ` probes, read back through `pypdf`'s
   `visitor_text` (`cm[4]+tm[4]` / `cm[5]+tm[5]`) and through the page's `/Annots` link
   destinations;
4. reading the built `basic.css` and the emitted `.tex` to see what Sphinx's own HTML and LaTeX
   builders do with the same input.

### The measured starting position (this is not a decision — it is the ground everything below stands on)

**`citation_reference` never reaches the translator under Sphinx.** Sphinx's citation domain
rewrites every `[Label]_` into a `pending_xref` (`refdomain='citation'`, `reftype='ref'`) and
resolves it to a plain `nodes.reference`: `refid='krizhevsky2012'` for a same-document citation,
`refuri='index.typ#krizhevsky2012'` for a cross-document one. CIT-03's premise — "`citation_reference.refid`
resolves directly to `citation.ids[0]`" — was verified against **bare docutils**, not Sphinx, and is
therefore not the mechanism this phase implements.

**Consequence: the citing side already works.** The probe's `-b typst` output already contained
`link(<index:krizhevsky2012>, text("[Krizhevsky2012]"))` for both the same-document and the
cross-document citing sites, via `visit_reference`'s existing refid and xref branches. CIT-03 is
discharged as soon as the definition anchors the matching label — no new forward-link machinery.

**The defect is entirely on the definition side.** Emitted today:
`text("Krizhevsky2012")par({text("Krizhevsky, A. …")})`. Compiling that with `typst.compile()`
raises verbatim:

```
TypstError: expected semicolon or line break
```

This is the phase's classic GATE-01 RED (SC#1) and it is available exactly as the milestone claims.

**The `citation` node carries a `docname` attribute** (Sphinx adds it; measured
`docname='index'` / `docname='second'`). With a duplicate key defined in two documents, Sphinx warns
`duplicate citation Same2020` but keeps **both** definitions, each with `ids=['same2020']` in its own
document — so namespacing by `node['docname']` yields `index:same2020` and `second:same2020` and the
duplicate-label fatal SC#3 names cannot occur.

**`backrefs` are same-document only.** Measured: with `[Krizhevsky2012]_` cited twice in `index.rst`
and once in `second.rst`, the index definition carries `backrefs=['id1','id2']` — the two index
sites only. The `second.rst` citing site is absent. Sphinx's own HTML has the same limitation.

**Sphinx's two other builders disagree with each other on back-references.** HTML renders them
(`<span class="backrefs">(<a href="#id1">1</a>,<a href="#id2">2</a>)</span>`); the LaTeX builder
renders none at all — plain `\bibitem[Krizhevsky2012]{index:krizhevsky2012}` inside
`\begin{sphinxthebibliography}{Krizhevs}`. So "does a PDF want back-references" was a genuine open
question, not a foregone conclusion. D-01 settles it.

### Round-trip navigation — CIT-03, CIT-04

- **D-01: typsphinx follows Sphinx's HTML convention, not its LaTeX one — back-references are rendered.** Owner's ruling after being shown both builders' measured output. Typst needs no bibliography machinery for this: a probe emitting `[#link(<index:krizhevsky2012>, text("[Krizhevsky2012]")) <index:id1>]` at the citing site and `link(<index:id1>, text("1"))` inside the definition compiled clean and produced **four `/Link` annotations** in the PDF — two forward (both citing sites → the definition at y=66.0) and two backward (`1` → x=68.125, `2` → x=199.025, byte-matching the two citing sites' measured x positions). Plain `link()` + `<label>` is sufficient; `bibliography()` is not involved.
- **D-02: the back-reference marker sits immediately after the label, in the same left column, in HTML's order.** Measured cost, accepted by the owner: the left column widens by 21.95pt, moving every entry's body from x=104.35 to x=126.3 — and because D-04 puts all entries in one grid, an entry with no back-references is pushed out just the same. Rejected alternatives, both measured to leave the body at x=104.35: `(1,2)` on its own line under the label inside the left column, and `(1,2)` trailing the entry body (which lands it at x=274.8, a position that moves per entry and does not match HTML's order).
- **D-03: an entry with exactly one citing site emits no `(1)` — the label text itself becomes the back-link.** This is Sphinx HTML's measured behaviour: two-or-more gives `<span class="label">[Krizhevsky2012]</span><span class="backrefs">(…)</span>`, exactly one gives `<span class="label">[<a role="doc-backlink" href="#id3">Forward2020</a>]</span>`. Accepted cost: the label has two emission shapes depending on `len(backrefs)`. The separator between markers is a bare comma with no space, matching HTML's `(<a>1</a>,<a>2</a>)`.
- **D-04: the grid the back-reference marker lives in is governed by D-05 below.**

### Reference-list layout — CIT-02

- **D-05: a run of consecutive `citation` siblings is emitted as ONE two-column grid, not one grid per entry.** The grid is `grid(columns: (auto, 1fr))`. Measured: with all entries in a single grid the `auto` column takes the widest label, so every entry's body starts at the same x (104.35 in the probe) **and** past the longest label — which is what CIT-02's "continuation lines aligned past the label" actually asks for. This is the same idea Sphinx's LaTeX builder uses with `\begin{sphinxthebibliography}{Krizhevs}` (a widest-label sample). Rejected, both measured: one grid per entry, where each entry aligns to its own label (bodies at x=104.35 and x=62.58 — CIT-02 holds per entry but the list has a ragged left edge); and a fixed indent (`par(hanging-indent: …)`), where continuation lines share one x (47.5 at 2.5em) but sit *inside* the label — `[Krizhevsky2012]` measures 84pt against 2.5em=27.5pt, and HTML's own 4em=44pt fails the same way, which is why HTML is not the model for this particular sub-decision.
- **D-06: a non-citation node between two citations breaks the run, and the next run realigns independently.** Direct consequence of D-05, recorded so it is not mistaken for a bug. The common shape — a `References` section holding nothing but citations — is one run.
- **D-07: an uncited citation definition still renders, with a plain (non-linked) label.** Measured: Sphinx HTML emits `<span class="label">[Never1999]</span>` with no anchor and Sphinx logs `WARNING: 引用 [Never1999] は参照されていません。 [ref.citation]`; the entry stays in the list. **This is the opposite of the footnote precedent** — Phase 14 D-09 silently drops a defined-but-never-referenced footnote. SC#5's instruction not to reason "by analogy to the footnote handlers" has a concrete instance here.

### Scope of the back-reference guarantee — SC#3, CIT-04

- **D-08: the guarantee is "every citing location docutils recorded in `backrefs`", i.e. same-document.** Owner's ruling. It matches REQUIREMENTS' CIT-04 wording ("from docutils' `backrefs`") and matches HTML. A cross-document citing site gets a working forward link and no back-reference.
- **D-09: ROADMAP.md SC#3's "back-references to every citing location" is corrected to say so, with the change recorded in the Roadmap Evolution section.** Same handling as Phase 36's SC#3 and Phase 39's D-12 — the criterion is amended against measurement rather than waived.
- **D-10: the 2+ document fixture stays, with its purpose changed.** It no longer proves cross-document back-references. It proves (a) that a cross-document citing site's forward link resolves — measured to arrive as `refuri='index.typ#krizhevsky2012'` and route through `visit_reference`'s xref branch — and (b) that a key defined in two documents separates into `index:same2020` / `second:same2020` instead of aborting the compile with a duplicate-label fatal. Both hazards were measured live this session.

### Sample restoration — CIT-05

- **D-11: `examples/charged-ieee/` is restored verbatim, not expanded.** What `8bed1a3` / `c014a0b` removed goes back exactly: the `[Krizhevsky2012]_` inline reference in the CNN paragraph (with the reworded sentence reverted), the `References` heading, and the one `.. [Krizhevsky2012]` entry. Accepted cost, stated at decision time: with one entry and one citing site the sample exercises only D-03's single-back-reference shape — neither `(1,2)` nor D-05's widest-label alignment is visible there, so those must be proven by the phase's own fixtures. Rejected: adding further real papers (VGGNet/ResNet, already named in the sample's prose) to exercise every shape — the owner preferred the diff to read as "restore what was broken".
- **D-12: the two samples go back to being byte-identical.** Measured: `approach1` and `approach2` differ today *only* in the wording of the five-line "no citations" RST comment at the top. Both comments are deleted, which makes `index.rst` identical across the two approaches and leaves the template wiring as the samples' only intended difference.

### Label anchoring

- **D-13: every label this phase emits goes through the existing `_namespace_label` / `_sanitize_label` helpers, namespaced by the CITATION's own `docname`, never by `_current_docname()`.** The helpers live at `typsphinx/translator.py:3576, 3519`. Required by SC#3 and load-bearing for D-10: for a definition the two happen to coincide, but writing it against `node['docname']` is what makes the duplicate-key case correct by construction rather than by coincidence. Back-reference targets use the definition document's docname too, which is correct precisely because `backrefs` only ever names same-document sites (D-08).
- **D-14: adding an anchor at the citing site must not change the emitted bytes of any reference that is not a citation target.** `visit_reference` is on the hot path for every link in the codebase. Measured: the toctree reference in the same probe carries `ids=[]` while citation-derived references carry `ids=['id1']`, so an `ids`-driven guard looks viable — but the planner must prove non-regression rather than assume it, with the full-corpus `-b typstpdf` gate as the evidence.

### Claude's Discretion

- The grid's `column-gutter` and `row-gutter` values, and whether entries carry any extra vertical
  separation beyond the grid's own row gutter.
- The implementation shape of run detection for D-05 (sibling look-ahead in `visit_citation` versus a
  pre-pass index like the footnote one) — provided the grid opens once per run and closes once.
- The mechanism for anchoring the citing site under D-14 (bracket-wrap in `visit_reference` versus a
  backrefs-driven index consulted there), subject to D-14's non-regression constraint.
- Whether `visit_label` is a real handler or the `label` child is skipped positionally the way
  `visit_footnote_reference` skips `footnote_node.children[1:]`. Measured: the `label` node is the
  citation's first child, carries no `ids`, and — because `visit_footnote` raises `SkipNode` — a
  `visit_label` handler would fire for citations only.
- Which document the SC#4 document-order assertion is taken from, and the exact `pypdf` extraction
  used for it.

### Folded Todos

- **`.planning/todos/pending/2026-07-22-citation-node-support-untracked.md`** (`resolves_phase: 40`)
  — the original record that `translator.py` has no `visit_citation` / `visit_label` handler and that
  Phase 22.2 worked around it by deleting the samples' citation syntax rather than fixing it. Its
  three open questions are all answered by this phase: whether to support citations (yes — CIT-01..06),
  the Typst counterpart (`link()` + `<label>`, never `bibliography()` — see the Phase Boundary and
  D-01), and the graceful-degrade fallback (moot once the nodes are handled; the dangling-reference
  guard footnotes already carry is the residual case). Folding it closes the todo with the phase.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` § "Phase 40: Citations — Full Round Trip" — the five success criteria.
  **SC#3 is corrected by D-09**; treat its current "every citing location" wording as superseded by
  D-08's same-document scope.
- `.planning/REQUIREMENTS.md` § "Citations (CIT)" (lines 150–179) — CIT-01..CIT-06 verbatim, plus the
  preamble that locks out `bibliography()`/`cite()` and records CIT-07 as the future `.bib` path.
  **CIT-03's parenthetical about `citation_reference.refid` describes bare docutils, not Sphinx** —
  see the measured starting position above.
- `.planning/STATE.md` § "Current Position" — Phase 39 closed 13/13 with gap G-39-1 resolved; Phase 40
  is no longer deferred.

### Upstream phase decisions this phase must not re-open
- `.planning/milestones/v0.6.0-phases/14-footnotes-doctree-pre-pass/14-RESEARCH.md` — Verified Mechanism 1 (`<label>` attachment is
  markup-mode syntax and needs the `[#… <label>]` bracket-wrap inside this translator's code-mode
  wrapper; a `<label>` passed as a call *argument* is a plain code-mode Label value) and Pitfall 1
  (linking to a label that was never attached is a fatal compile abort, not a cosmetic issue). Both
  apply verbatim to citations. Phase 14's D-09 (drop unreferenced footnotes) does **not** carry over —
  see D-07.
- `.planning/phases/38-structural-indentation-info-fields/38-CONTEXT.md` — D-02 fixes
  `SHARED_INDENT_STEP` at `"2.5em"`. Measured too narrow to serve as a citation hanging indent
  (D-05); the citation grid does not consume it and does not redefine it.
- `.planning/phases/36-shared-emission-seam-cleanup/36-CONTEXT.md` — D-01/D-02 on the deliberate
  triplication of `visit_strong`'s body and the shared `_strong_was_*` attribute slots. Relevant only
  as a warning: do not add a fourth consumer of those slots.

### External sources measured for this phase
- `sphinx.domains.citation` (Sphinx 9.1.0, `.venv/lib/python3.13/site-packages/sphinx/domains/citation.py`)
  — the transform chain that turns `citation_reference` into `pending_xref` and then into a resolved
  `reference`. This is why the translator never sees `citation_reference`.
- The built `basic.css` (`div.citation > span { float: left }`, `div.citation > p { margin-left: 4em }`)
  — Sphinx HTML's citation layout, and the reason HTML is followed for D-01/D-02/D-03 but not for
  D-05's indent width.
- Sphinx's LaTeX builder output (`\begin{sphinxthebibliography}{Krizhevs}` + `\bibitem[…]{…}`) — the
  no-back-references precedent D-01 deliberately declines to follow, and the widest-label-sample idea
  D-05 adopts.

### Project conventions
- `CLAUDE.md` § "Worktree-isolated execution" — worktree isolation is the standing execution mode;
  per-worktree `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` plus running
  everything through `uv run` is mandatory.
- `CLAUDE.md` § "The `@preview` version-sync hazard" — this phase adds no package and must not move a
  pin; `tests/test_preview_version_sync.py` should stay green untouched.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `visit_reference` (`typsphinx/translator.py:3820`) already emits both citation link shapes with no
  change: the same-document branch (`not refuri and refid`) produces
  `link(<index:krizhevsky2012>, …)` and the cross-document branch resolves
  `refuri='index.typ#krizhevsky2012'` through `_resolve_xref_docname` to the same anchor. Verified in
  a real build.
- `_namespace_label` / `_sanitize_label` (`typsphinx/translator.py:3576, 3519`) — the single
  derivation point every anchor and every link already shares. D-13 routes all new labels through
  them.
- `visit_footnote_reference` (`typsphinx/translator.py:2527`) — the reference implementation of the
  three things this phase needs mechanically: the `[#… <label>]` bracket-wrap for label attachment,
  the buffer-swap body render (`self.body = []` … `"".join(self.body)`, never `node.astext()`) with
  `in_paragraph` / `paragraph_has_content` saved and restored around it, and the dangling-target
  guard that warns and skips rather than emitting a link to a non-existent label. Read it for
  mechanism; do **not** inherit its policy (D-07).
- `depart_term` (`typsphinx/translator.py:2249`) — the other precedent for wrapping buffered content
  in `[#{…} <label>]` when a docutils id has to become an anchor.

### Established Patterns

- **Every emitted label is docname-namespaced and sanitized at a single derivation point**, so a
  definition and a reference to it compute the identical token independently.
- **`<label>` attachment requires markup mode.** Inside the unified `#{ … }` code-mode wrapper, a
  bare `<label>` postfix is a parse error; the established fix is the bracket-wrap `[#expr <label>]`.
  A `<label>` used as a function *argument* (`link(<x>, …)`) needs no wrap.
- **GATE-01 (v0.7.0 amendment):** a structural / regex / `pypdf` assertion recorded RED before any
  code. This phase is the milestone's sole holder of the classic "does not compile" RED — the
  verbatim `TypstError: expected semicolon or line break` must be captured against the unfixed
  translator before the fix lands.
- Non-regression is proven by re-running the full-corpus `-b typstpdf` gate
  (`tests/test_corpus_gate.py`) green after the change.

### Integration Points

- `tests/test_corpus_gate.py:213-233, 503` already contains a `<citation>` node dump as fixture data
  for its unknown-node-warning catalogue parser. Once citations are handled the *live* corpus stops
  producing that warning; check whether those tests assert on real build output or on a frozen
  string, and update deliberately rather than by regenerating.
- `tests/test_desc_break_marker_buffer_swap_gate.py:246` carries a comment naming Phase 40's citation
  work as the milestone's sole "does not compile" exception. Keep it accurate.
- `examples/charged-ieee/{approach1,approach2}/source/index.rst` — the CIT-05 restoration targets.
  Both are built by the examples test suite.

</code_context>

<specifics>
## Specific Ideas

- The owner opened the discussion by challenging the requirement itself — "citation は本文で内容を
  ただ引用するだけのもので、バックリファレンスとは何なのか" — and then, on being shown that Sphinx's
  HTML and LaTeX builders disagree, ruled for HTML. The standing preference this reveals: **when
  Sphinx's own builders disagree, show both measured outputs and let the owner pick; do not assume
  the PDF builder (LaTeX) is automatically the closer analogue** even though typsphinx produces PDFs.
- The owner's second challenge was structural — "Typst の参考文献セクションは bibliography しかない
  のだから、それを作らないといけないのでは" — which was answered by compiling a probe and reading the
  PDF's link annotations rather than by argument. Continue to settle "is this even possible in Typst"
  questions with a real compile plus a `pypdf` read-back.
- On CIT-05 the owner chose the smaller diff over the better demo, so that the commit reads as
  restoring what was broken. Feature demonstration belongs in the phase's own fixtures, not in the
  shipped samples.

</specifics>

<deferred>
## Deferred Ideas

- **Cross-document back-references.** Rejected as D-08. Building a typsphinx-owned index over every
  document's doctree would give back-references that neither Sphinx HTML nor Sphinx LaTeX provides,
  at the cost of a new env-wide pre-pass and a rewrite of CIT-04's "from docutils' `backrefs`"
  wording. Revisit only if a user asks for it.
- **Expanding `examples/charged-ieee/` into a multi-entry reference list.** Rejected as D-11 in
  favour of a verbatim restore. The real papers already named in the sample's prose (VGGNet, ResNet,
  EfficientNet) are the natural material if this is ever wanted.
- **CIT-07 — `sphinxcontrib-bibtex` support (`:cite:` role, `.bib` files).** Already a future
  requirement. This is where Typst's `bibliography()` becomes the right tool; REQUIREMENTS records it
  as verified feasible via `bibliography(bytes(...))` with no file on disk.

### Reviewed Todos (not folded)

- `2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md` — scored highest on the matcher
  (0.9) but is a Phase 37/38 `desc_*` seam. Folding it would reopen Phase 37's completed golden file.
- `2026-07-29-release-notes-body-from-changelog-section.md` — Phase 41 (REL-04).
- `2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md` — a Phase 37 test-naming
  defect.
- `2026-08-01-visit-desc-sig-name-docstring-unbalanced-asterisk-warning.md` — `desc_*` docstring
  hygiene, untouched by this phase.
- `2026-07-25-derive-typst-lang-duplicated-warning-block.md` — `template_engine`, unrelated.
- `2026-07-22-non-str-docname-typeerror-in-typstpdf-finish.md` — builder input hardening, unrelated.
- `2026-07-29-project-md-unterminated-html-comments.md` — planning-doc hygiene, unrelated.
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` — deferred as future requirement LNK-01.

</deferred>

---

*Phase: 40-Citations — Full Round Trip*
*Context gathered: 2026-08-02*
