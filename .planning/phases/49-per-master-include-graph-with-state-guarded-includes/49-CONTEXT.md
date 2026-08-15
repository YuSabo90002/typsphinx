# Phase 49: Per-Master Include Graph with State-Guarded Includes - Context

**Gathered:** 2026-08-14
**Status:** Ready for planning

<domain>
## Phase Boundary

The include decision moves from **write time to compile time**. The builder computes each master's
include edge set by mirroring `sphinx/util/nodes.py:485` `inline_all_toctrees` (document-order
depth-first, first encounter wins, `traversed` re-initialised per master and seeded with the master's
own docname), the wrapper publishes that edge set as Typst `state` before including its master's
content, and `visit_toctree` stops emitting an unconditional `include()` — emitting instead a
state-guarded `include()` at the toctree's own position. `builder.py:231`'s build-scoped
`_included_docnames` ledger and its `write()` reset are deleted.

This is what lets **one shared content file behave differently for every master that includes it**,
which closes **defect A** (a document toctree'd by two masters reaches only the first-written one)
and the diamond `M → [p, q]`, `p → [c]`, `q → [c]`, `M' → [q]` that no write-time ledger can serve.

The design itself is **already locked** by ROADMAP.md and PROJECT.md and is not re-opened here. Two
rejected routes are recorded in PROJECT.md and must not be re-derived: (1) re-scoping the write-time
ledger per master (cannot serve the diamond — one file written once cannot both omit and emit the
same include), and (2) carrying the include graph flattened in the wrapper (solves the diamond, but
breaks document-order interleaving: prose after a toctree renders before the chapters).

**Not in this phase:** the PR #131 image path defects (Phase 50); documenting the two-layer output
shape and any `:numref:` limitation this phase records (Phase 51); the v0.8.0 CHANGELOG entry
(Phase 52); replacing Phase 48's `query(<L>)` guard with a `state` lookup (deferred — Phase 48's
D-11 measured the **bottom tier**, so no coupling obligation exists).

</domain>

<decisions>
## Implementation Decisions

### Response to SC#5's two measurements (fixed before measuring)

- **D-01:** If the `:numref:` measurement shows divergence, it is **recorded as a documented
  limitation and handed forward to Phase 51 (docs) and Phase 52 (CHANGELOG)** — it is not fixed in
  this phase — **Reversibility:** reversible — the alternative (folding the fix into Phase 49) stays
  available as a later scope decision, and nothing in this phase's code shape forecloses it. The
  divergence is expected: Sphinx numbers project-wide and bakes "Figure N" into the caption text,
  while Typst counts per compiled wrapper, so the same `:numref:`-targeted figure sitting at
  different DFS positions in two masters can produce two different numbers **with no compile error
  to catch it**. Phase 49's own work is therefore the measurement (a live two-master fixture,
  `pypdf`-compared against the Typst-rendered caption number) and the write-up, not a renumbering
  mechanism. If the measurement shows **no** divergence, that null result is recorded with the same
  evidence standard.

- **D-02:** If the full-corpus `state`/`context` multi-pass convergence fails, the phase **stops and
  escalates to the owner** — Phase 49 does not close, the minimal failing shape is isolated and
  reported, and the design-change call is the owner's — **Reversibility:** reversible as a process
  rule, but it can block the milestone by design. This is Phase 48 D-11's top tier applied to a
  design-level risk rather than a cost regression. **A partial write-time fallback for the shapes
  that fail is explicitly NOT available**: reintroducing a write-time include decision restores the
  exact two-competing-mechanisms shape Phase 48 spent a phase deleting, and brings back defect A's
  failure class in a second location. Executors must not "fix" a convergence failure by narrowing
  the design; ROADMAP binding constraint #5 already says a failure here is a design-level finding,
  not a fixture bug, and D-02 states what that means operationally.

### Derived from the locked "mirror `inline_all_toctrees`" mandate (owner delegated)

The owner reviewed the following and judged them uniquely determined by the locked design with no
room for preference. They are recorded here as decisions — not as open discretion — because
downstream agents need the derivation, not a re-derivation.

- **D-03:** Both the builder-side traversal and the translator-side emission iterate
  `toctreenode['includefiles']`, **not** `node['entries']` — **Reversibility:** reversible.
  Measured 2026-08-14 against the current tree: `sphinx/directives/other.py` `TocTree.parse_content`
  appends external URLs and `self` references to `entries` **only**, never to `includefiles`, while
  `inline_all_toctrees` iterates `includefiles`. Today `translator.py:5095`'s
  `for _title, docname in entries` loop therefore emits `include("self.typ")` and
  `include("https://example.com.typ")` for a toctree containing `self` and an external link, and the
  wrapper's `typst.compile()` aborts with
  `file not found (searched at .../self.typ)` — a live fatal with zero coverage in `tests/roots/`
  and zero occurrences in the Sphinx `doc/` corpus (154 `.rst`). Mirroring `includefiles` is what
  COMP-05 asks for and closes that fatal as a consequence.

- **D-04:** The guard key must be **unique per emission site within its parent document**, not a bare
  `"<parent>><child>"` docname pair — **Reversibility:** costly — the key shape is an emitted string
  present in every wrapper and every content file, so changing it later means moving both sides in
  lockstep across the whole test corpus. Measured: `parse_content` takes a **fresh**
  `all_docnames` copy per directive invocation, so two separate toctrees in one document listing the
  same child produce **no warning at all**, and a duplicate inside a single toctree is warned
  (`duplicated entry found in toctree`) but still appended to both `entries` and `includefiles`
  (measured live: the warning fires, the entry survives). Today `_included_docnames` is what
  suppresses the second `include()`. With that ledger deleted and a bare pair key, both emission
  sites would see the same key in the state array and both would fire → the same `.typ` included
  twice → every Typst `<label>` it defines emitted twice → compile fatal. The exact key spelling is
  Claude's discretion; uniqueness per emission site is not.

- **D-05:** Edge keys are produced by **one shared function**, called by both the builder's graph
  computation and the translator's guard emission, with a test asserting the two sides agree —
  **Reversibility:** reversible. A key mismatch does not fail the build: the guard simply never
  fires, the compile succeeds, and the content silently disappears — precisely the failure class
  this phase exists to close, reintroduced one layer up. This follows the project's standing rule
  from Phase 40.1 D-06/D-07 and Phase 47 D-03: one judgement, one derivation point, never two
  spellings of the same rule.

- **D-06:** Degenerate graph shapes take Sphinx's own outcome, decided here rather than discovered as
  a test failure (SC#2) — **Reversibility:** reversible:
  - **2-node toctree cycle** and **self-referencing toctree** → the child is **skipped** (no
    include). `traversed` is seeded with the master's own docname (measured:
    `sphinx/builders/latex/__init__.py:390` passes `[indexfile]`, `singlehtml.py:95` passes
    `[master]`) and appended before recursion, so Sphinx never inlines a document twice and never
    re-enters a cycle.
  - **`self` in a toctree and external-URL entries** → **skipped, silently**, with no include and no
    new warning. They are navigation constructs that Sphinx's own inlining builders drop by never
    putting them in `includefiles`; typsphinx adds no diagnostic Sphinx does not have.
  - **`:glob:` toctree** → **no special handling needed**. Measured: the directive expands globs at
    parse time into `sorted()` docnames appended to both `entries` and `includefiles`, so a glob
    toctree is indistinguishable from an explicit one by the time the writer sees it.
  - **`:orphan:` document referenced but not toctree'd** → **not included** (it is in no edge set),
    and a cross-reference to it **degrades to plain text** through Phase 48's compile-time guard,
    per compiled wrapper. No new mechanism.
  - **≥3 masters sharing ≥2 overlapping children** → the same algorithm with no special case; it is
    a coverage obligation (proving the fix is not 2-master-specific), not a design question.

- **D-07:** The Typst `state` key is **namespaced**, not the bare `"inc"` sketched in PROJECT.md —
  **Reversibility:** costly — same lockstep argument as D-04. A user-supplied `typst_template` is
  arbitrary Typst and may legitimately use `state("inc")`; a collision would corrupt the include set
  with no error. The exact namespace string is Claude's discretion.

- **D-08:** The heading-offset emission is unchanged from today — one
  `set heading(offset: heading.offset + 1)` per toctree, inside the `context` block, with the
  per-entry guard **inside** that block rather than wrapped around it — **Reversibility:**
  reversible. This is Phase 44.1 D-07's relative-increment rule, which is exactly what removes the
  need for DFS-depth arithmetic in the wrapper (COMP-10): a shared document's rendered depth follows
  the include nesting, which follows traversal order.

### Verification obligations carried into research

- **D-09:** The `#state(<key>, ()).update((...))` / `if <key> in state(<key>, ()).get()` syntax is
  treated as **unmeasured** and must be verified against a real `typst.compile()` during research
  before any plan depends on it — **Reversibility:** reversible. PROJECT.md records the
  `context` + `query` snippet (Phase 48's) as measured *verbatim*, and asserts the state-guarded form
  measured correct on the diamond / interleaving / outline / label cases, but **does not record the
  snippet itself**. Note also that a one-element Typst array literal requires a trailing comma
  (`("bmaster>shared",)`), which a single-master wrapper will hit on every build. This mirrors
  Phase 48's D-08.

- **D-10:** The `self` / external-URL compile fatal (D-03) closes **inside this phase** with its own
  GATE-01 fixture and pre-fix RED, not as a separate todo — **Reversibility:** reversible. It is
  entailed by COMP-05 (mirroring `inline_all_toctrees` means iterating `includefiles`), so *not*
  closing it would mean deliberately preserving broken behaviour in a loop being rewritten anyway.
  The classic RED is available and already measured (`file not found (searched at .../self.typ)`),
  so binding constraint #4's non-fatal amendment does not apply to it.

### Claude's Discretion

- The exact spelling of the edge key (D-04) and of the namespaced `state` key (D-07), provided
  uniqueness-per-emission-site and one-shared-derivation (D-05) hold.
- Whether the builder's traversal walks `env.get_doctree()` doctrees or reads `env.toctree_includes`,
  provided the result is identical to `inline_all_toctrees`'s selection and the emission side derives
  its keys through D-05's shared function.
- Where the shared key-derivation function lives and what it is named.
- Whether the pre-fix REDs are recorded as `xfail(strict=True)` (the Phase 47 plan-13 convention) or
  as a separately-committed evidence transcript.
- The internal structure of the published state value (array vs. other membership-testable form), as
  long as D-09's syntax is verified and corpus-scale membership testing stays sane (the corpus is
  154 documents, so an array `in` test is not a performance concern).

### Folded Todos

- `.planning/todos/pending/2026-08-05-shared-document-silently-dropped-from-all-but-first-master.md`
  (`resolves_phase: 49`, severity high) — this **is** defect A / COMP-07. Its `files:` list cites
  pre-Phase-47 line numbers (`builder.py:99`, `:420`, `:432`, `translator.py:4776-4785`); the live
  locations after Phases 47–48 are `builder.py:231` (declaration), `builder.py:658` (the `write()`
  reset) and `translator.py:5094-5103` (the dedup read). Read the todo for the original measurement,
  not for the line numbers.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope and constraints

- `.planning/ROADMAP.md` lines 685-757 — §"Phase 49: Per-Master Include Graph with State-Guarded
  Includes": the goal, the five success criteria, and the `**UI hint**: no` override that
  `ui-safety-gate.cjs` reads (this is not a frontend phase; do not rely on a per-run `--skip-ui`)
- `.planning/ROADMAP.md` lines 345-412 — binding constraints. #1 (Phase 48 must land first; the two
  are not independently parallelizable — satisfied, Phase 48 completed 2026-08-14), #4 (GATE-01 and
  its non-fatal amendment: every non-fatal defect names its pre-fix RED assertion **before**
  implementation starts), #5 (GATE-02 full-corpus pass is an explicit success criterion of this
  phase, and a convergence failure is a design-level finding — see D-02), #6 (no laundered gates:
  every changed expected value derived from `typst_documents` + the `.rst` fixtures read literally,
  written down **before** running the new emitter), #7 (zero new runtime dependencies, four
  `@preview` packages, **no new `typst_*` config value**), #8 (every phase closes green: full
  pytest + `black`/`ruff`/`mypy`, and "anywhere under X" criteria checked by repo-wide grep), #9
  (typing-import modernization and `sphinx linkcheck` both forbidden this milestone)
- `.planning/ROADMAP.md` line 420 — open question #2 (`:numref:` project-wide vs. per-wrapper
  numbering divergence), owned by this phase and answered by D-01
- `.planning/REQUIREMENTS.md` lines 31-53 — COMP-05 through COMP-12, this phase's eight requirements

### Design already locked — do not re-derive

- `.planning/PROJECT.md` lines 40-51 — the state-guarded include design as adopted: the wrapper's
  `#state(...).update(...)`, `visit_toctree`'s guarded emission, and why `builder.py`'s ledger
  becomes unnecessary
- `.planning/PROJECT.md` lines 88-104 — **the composition rule is `inline_all_toctrees`'s
  document-order DFS, first encounter wins — NOT "prefer the deeper path"**, measured both ways on
  the `xmaster` `[zmid, shared]` vs `[shared, zmid]` pair. Includes the explicit instruction **not**
  to port `_check_toc_parents`'s lexicographic `selecting: X <- Y` tiebreak, which governs none of
  this
- `.planning/PROJECT.md` lines 121-133 — the two measured-and-rejected designs (per-master write-time
  ledger; flattened wrapper graph) and why the state-guarded form was selected. Do not re-derive
- `.planning/PROJECT.md` lines 134-140 — the known residual risk (multi-pass layout convergence
  unmeasured at corpus scale) and the standalone-content-file behaviour (empty state → no children
  included), which Phase 51 documents
- `.planning/PROJECT.md` lines 74-87 — the measured defect-A baseline (`index.pdf` reports
  `SHARED-CHAPTER-MARKER` **0** times, `bmaster.pdf` 1, exit 0, no warning) and why a shared chapter
  appearing in **both** PDFs is the correct outcome (masters are not concatenated; each produces its
  own independent PDF, so the `label ... occurs multiple times` hazard holds only *within* one PDF)
- `.planning/PROJECT.md` lines 141-146 — the user-visible output-shape change and the expected large
  test blast radius (v0.7.0's comparable change measured 10 test files / 61 render-gate classes)

### Prior phase artifacts this phase builds on

- `.planning/phases/48-compile-time-cross-reference-guard/48-CONTEXT.md` — Phase 48's D-01..D-11.
  D-11's cost tiers and their **bottom-tier** outcome matter here: no Phase 49 coupling obligation
  was created
- `.planning/phases/48-compile-time-cross-reference-guard/48-EVIDENCE.md` lines 219-330 — the D-11
  measurement (corpus `-b typstpdf` at ~28.9s / 28.6s before, bottom tier after) and the
  "## Accepted limit — label-collision false negative" section
- `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-EXPECTED-STRUCTURE.md`
  — the write-expected-values-first artifact this phase must imitate at a larger scale (binding
  constraint #6). Phase 48's `48-EXPECTED-STRUCTURE.md` is the second instance of the same procedure
- `.planning/phases/47-two-layer-output-content-wrapper-split-target-as-path-collis/47-CONTEXT.md` —
  the two-layer output shape (content file per docname, wrapper per `typst_documents` entry) this
  phase's state publication rides on

### Sphinx sources the traversal mirrors (read, do not guess)

- `sphinx/util/nodes.py:485` `inline_all_toctrees` — walks `tree.findall(addnodes.toctree)` in
  document order, iterates `toctreenode['includefiles']`, appends to `traversed` **before**
  recursing, and replaces each toctree node **in place** with the inlined subtrees (which is why
  document-order interleaving is preserved)
- `sphinx/builders/latex/__init__.py:389-391` and `sphinx/builders/singlehtml.py:95` — the callers
  that seed `traversed` with the master's own docname (`[indexfile]` / `[master]`)
- `sphinx/directives/other.py` `TocTree.parse_content` — where `entries` and `includefiles` diverge
  (external URLs and `self` go to `entries` only), where `:glob:` is expanded to `sorted()` docnames,
  where the fresh per-directive `all_docnames` copy makes cross-toctree duplicates unwarned, and
  where `:reversed:` reverses both lists

### Code this phase changes

- `typsphinx/translator.py:5016-5121` — `visit_toctree`, the whole emission loop. Lines 5094-5103 are
  the `_included_docnames` dedup that goes; line 5095 is the `entries` iteration D-03 replaces
- `typsphinx/translator.py:4592-4620` — `_compute_relative_include_path()`, which survives and still
  computes the `include()` path
- `typsphinx/builder.py:231` — `self._included_docnames: set[str] = set()` declaration (deleted)
- `typsphinx/builder.py:658` — the per-`write()` reset (deleted)
- `typsphinx/writer.py:262-300` — `render_wrapper()`, whose body is currently
  `#include("<content>")`; the state publication is emitted here, before that include
- `typsphinx/writer.py:25` — `compute_content_include_path()`, the wrapper→content path helper
- `typsphinx/builder.py:859-920` — `_write_typst_files()`, the content-then-wrappers write loop and
  the site that would hand a per-entry edge set to `render_wrapper()`

### Tests whose expectations move

- `tests/test_corpus_gate.py` — the GATE-02 full-corpus `-b typstpdf` gate, SC#5's vehicle
- Every gate asserting on a master `.typ`'s contents — expect a blast radius at least as large as
  v0.7.0's measured 10 files / 61 classes. Binding constraint #6 governs all of them
- `tests/roots/` — measured 2026-08-14: **no** existing root exercises a `self` entry, an external
  URL entry, a toctree cycle, or a `:glob:` toctree. Every SC#2 shape needs a new fixture

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `_compute_relative_include_path()` (`translator.py:4592`) already answers "what path does this
  content file `include()` for that docname" and is unaffected by the guard — only the *decision* to
  emit moves, not the path computation.
- `compute_content_include_path()` (`writer.py:25`) does the same job for the wrapper→content edge.
- `render_wrapper()` (`writer.py:262`) is the single site where a wrapper's body is composed; today
  that body is one `#include()` line (`writer.py:300`). The state publication has exactly one natural
  insertion point.
- The `sphinx-build → typst.compile() → pypdf` acceptance-fixture pattern established by
  `tests/test_pdf_render_gate.py` is what SC#1, SC#2, SC#4 and SC#5's `:numref:` comparison all need.
- `typst.query(..., 'heading', field='level')` against the **compiled** document is SC#3's required
  assertion vehicle — resolved heading levels, not `.typ` greps.

### Established Patterns

- `visit_toctree` already emits `context { set heading(offset: heading.offset + 1) ... }` (D-07 of
  Phase 44.1). The guard goes inside that existing block; no new Typst construct is introduced at
  the outer level.
- Fixture `conf.py` files carry a "Load-bearing properties — do NOT touch any of these" comment block
  naming what would silently stop the fixture exercising its defect. Follow it for every new fixture.
- Pre-fix REDs are recorded as `xfail(strict=True)` plus a verbatim transcript in a separate
  `*-RED-EVIDENCE.md` (Phase 47 plan 13's convention, reused by Phase 48).
- One judgement → one derivation point (Phase 40.1 D-06/D-07, Phase 47 D-03). D-05 is this phase's
  instance of that rule.

### Integration Points

- `builder.write()` is where each master's edge set must be computed, because it is the only place
  that has both `typst_documents` and the environment; `_write_typst_files()` is where a per-entry
  edge set reaches `render_wrapper()`.
- `builder._included_docnames` has exactly one reader (`translator.py:5094`) and one writer
  (`visit_toctree`'s `.add()`), plus the declaration and the reset — which is what makes COMP-11's
  repo-wide-grep-zero achievable in one change.
- Phase 48's compile-time guard is the reason this phase is safe to ship: a shared content file
  referencing a label present in one master and absent in another now degrades per wrapper instead
  of aborting the compile.

</code_context>

<specifics>
## Specific Ideas

- The concrete output shape the owner reviewed and accepted during discussion, for the configuration
  `index` (master A → `manual.typ`, prose → toctree `[zmid, shared]` → Indices section),
  `zmid` (toctree `[shared]`), `bmaster` (master B → `bmanual.typ`, toctree `[shared]`):

  Edge sets, derived by mirroring `inline_all_toctrees` — master `index`:
  `index>zmid`, `zmid>shared` (`shared` is claimed by `zmid` because `zmid` is listed first and
  recursed into immediately, so `index`'s own `shared` entry loses on first-encounter-wins);
  master `bmaster`: `bmaster>shared`.

  ```typst
  // manual.typ (wrapper) — one line more than today
  #show: project.with(title: "T", authors: ("A",), ...)
  #state("inc", ()).update(("index>zmid", "zmid>shared"))
  #include("index.typ")
  ```

  ```typst
  // bmanual.typ (wrapper) — note the trailing comma on a 1-element array
  #state("inc", ()).update(("bmaster>shared",))
  #include("bmaster.typ")
  ```

  ```typst
  // index.typ (content) — the toctree block is the only thing that changes
  context {
    set heading(offset: heading.offset + 1)
    if "index>zmid"   in state("inc", ()).get() { include("zmid.typ") }
    if "index>shared" in state("inc", ()).get() { include("shared.typ") }
  }
  ```

  `shared.typ` is **byte-identical** in both compilations: it appears once nested under `zmid` in
  `manual.pdf` and once at the direct position in `bmanual.pdf`, its depth decided purely by the
  relative `heading.offset` increments of the includes above it.

  Treat the literal key spelling (`"index>zmid"`, the bare `"inc"` state name) as the **sketch from
  PROJECT.md**, not as the decided form — D-04 and D-07 override both, and D-09 requires the syntax
  itself to be verified against a real compile.

- The live measurement taken during this discussion, reusable as the D-10 RED: a single-document
  project whose one toctree contains `self`, `Ext <https://example.com>`, `child` and `child` again
  emits `include("self.typ")`, `include("https://example.com.typ")` and a **single**
  `include("child.typ")` (the ledger suppressing the duplicate), and
  `typst.compile("manual.typ")` aborts with
  `file not found (searched at .../self.typ)`. Sphinx's own build reports one warning
  (`duplicated entry found in toctree: child`) and exits 0.

</specifics>

<deferred>
## Deferred Ideas

- **Replacing Phase 48's `query(<L>).len() > 0` guard with a lookup against this phase's published
  include state** — Phase 48 D-11 named this as the remediation path *if* its top cost tier were hit.
  `48-EVIDENCE.md` measured the **bottom tier**, so no obligation was created. Not this phase's work.

### Reviewed Todos (not folded)

`gsd-tools query todo.match-phase 49` returned eight matches; one was folded (defect A, see
`<decisions>`). The remaining seven are owned elsewhere:

- `2026-08-10-rehomed-converted-image-collides-with-srcdir-images-dir.md` — Phase 50 (IMG-01)
- `2026-08-10-track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri.md` — Phase 50 (IMG-02)
- `2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md` — Phase 48's own recorded
  accepted limit (`_sanitize_label` maps `/` → `_u2f_`, so docnames `a/b` and `a_u2f_b` collide).
  Minor, deferred, and unaffected by the include-graph change
- `2026-07-22-add-sphinx-linkcheck-ci-job.md` — forbidden this milestone by binding constraint #9
- `2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` — release automation, closes at
  `/gsd-complete-milestone`
- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` — local toolchain, unrelated
- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — forbidden this milestone by
  binding constraint #9 and independently by `CLAUDE.md`

</deferred>

---

*Phase: 49-Per-Master Include Graph with State-Guarded Includes*
*Context gathered: 2026-08-14*
