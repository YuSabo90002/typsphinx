# Phase 62: The `visit_image()` Separator Fix and Its Real-Compile Gate - Context

**Gathered:** 2026-08-30
**Status:** Ready for planning

<domain>
## Phase Boundary

`visit_image()`'s non-`in_figure` branch joins the separator discipline the rest of the translator
already runs on, so an image node preceded by any sibling content in its container no longer
juxtaposes onto a code-mode expression and aborts the whole Typst compile. The proof is a
regression gate that drives a real `typst.compile()` over the full measured trigger matrix
(16 failing shapes, 9 must-keep-passing shapes), recorded RED against the unfixed tree before the
fix lands. The milestone branch also reaches `origin` with a completed 3-OS CI run in this phase
(milestone invariant #5).

**Not in this phase:** the CHANGELOG entry, any version literal, any tag, any publish — those are
Phase 63 and `/gsd-complete-milestone`. Not in this milestone at all: auditing the other thirteen
inline constructs, refactoring the separator machinery, `:scale:`/`:align:` support, figure/legend
styling, a from-scratch line-boundary predicate (see REQUIREMENTS.md's Out of Scope table, binding).

</domain>

<decisions>
## Implementation Decisions

The owner selected **"おすすめ設定"** — every decision below is Claude's measured recommendation,
accepted en bloc. Each is grounded in a measurement taken during this discussion, not in prior
prose. Two measurements were taken specifically to settle D-01/D-02 and are recorded inline.

### Gate fixture architecture

- **D-01: One fixture project, 26 documents, 18 masters.** The gate uses a single new fixture
  project (suggested `tests/fixtures/inline_image_separator_render_gate/`) laid out as:
  - `index.rst` — the **no-image root master**. Contains a toctree and no image at all. This is
    SC#1's blast-radius document: it fails today only because Typst's `#include()` re-parses a
    poisoned content file.
  - **16 FAIL documents**, one per measured failing shape (`research/FEATURES.md` Q1 rows 1–16).
    **Each is also declared as its own master** in `typst_documents`.
  - **9 PASS documents**, one per must-keep-passing shape (`research/FEATURES.md` Q2 rows A–I),
    all toctree'd under **one** `pass_parent` document which is the 18th master.

  `typst_documents` therefore holds 18 entries: `index` + the 16 FAIL docs + `pass_parent`.
  — **Reversibility:** reversible — fixture layout is test-only data; changing it later costs one
  fixture rewrite and no product change.

- **D-02: Per-shape attribution is obtainable only one-master-per-shape — measured.**
  Two measurements taken 2026-08-30:
  1. `typst.compile()` on a probe file carrying **three** independent unseparated juxtapositions
     returned exactly one message: `expected semicolon or line break`. typst-py's `TypstError`
     carries **no file, no line, and no multiplicity**. Crowding several shapes into one document
     therefore collapses them into a single indistinguishable refusal.
  2. `TypstPDFBuilder.finish()` (`typsphinx/builder.py:2505-2642`) attempts **every** master, then
     raises a **single aggregate** `ExtensionError` whose message joins `f"{docname}: {err}"` for
     each failure.

  Together: one build against the unfixed tree yields one aggregate error naming **17** masters
  (`index` + the 16 FAIL docs), each carrying the verbatim refusal, with the docname supplying the
  per-shape attribution SC#2 requires.

- **D-03: `pass_parent` is a positive control inside the RED run.** Because the 9 PASS documents all
  compile today, the `pass_parent` master must come back **green in the same RED build** in which
  17 others are red. A RED run in which `pass_parent` also fails means the fixture is wrong, not
  that the defect is broader.

### RED-first evidence procedure

- **D-04: One RED build, transcribed verbatim, following Phase 59's choreography.** Restore
  `git checkout $PHASE_BASE_SHA -- typsphinx/translator.py`, run the gate, transcribe the aggregate
  `ExtensionError` **verbatim** (all 17 `docname: expected semicolon or line break` pairs plus the
  green `pass_parent`), restore the fix, record `git status --porcelain` empty. The gate module
  greps positive for `typst.compile` / `TYPST_AVAILABLE`.
- **D-05: The evidence file is `62-RED-EVIDENCE.md`, never `62-VERIFICATION.md`.**
  `{phase}-VERIFICATION.md` is `gsd-verifier`'s reserved output name and a phase artifact written
  there is clobbered at verify time. Follows the naming of
  `.planning/milestones/v0.9.1-phases/59-.../59-WINDOWS-URI-EVIDENCE.md`.

### What the 9 must-pass shapes are bound to

- **D-06: Byte-identity, not merely "compiles".** ROADMAP SC#3's literal text says the 9 shapes
  "all compiling"; `research/FEATURES.md` Q2 says they must stay **byte-identical**. We bind the
  stronger one. Rationale: the specific failure mode this fix risks is a cosmetic extra `\n` that
  still compiles — "compiles" cannot see it, byte-identity can. Byte-identity implies compiling, so
  SC#3 remains satisfied as written.
- **D-07: The goldens come from the unfixed tree, captured during the RED run.**
  They are committed as test data. During D-04's restore window, capture each of the 9 PASS
  documents' emitted **content** `.typ` and commit them; the gate asserts the fixed translator
  reproduces them byte-for-byte.
  **Content files only — never wrapper files**, which carry title/author/date and are not stable
  test data. Planning must first confirm content `.typ` output carries no build-volatile bytes; if
  it does, narrow the golden to the image-bearing region rather than abandoning byte-identity.
  — **Reversibility:** reversible — test data only.
- **D-08: The triad's insertion point is decided by D-06's goldens, not by fiat.**
  Measured hazard the planner must account for: `_emit_id_anchors()`
  (`typsphinx/translator.py:1023-1028`) already emits `\n[#metadata(none) <id>]\n` **and** sets
  `list_item_needs_separator = True` when `in_list_item`. A triad placed *after* that call
  therefore double-separates an id-carrying image inside a list item. Placement before vs. after
  `_emit_id_anchors(node)` is whichever keeps the 9 goldens byte-identical — measure, don't argue.

### Phase boundary hygiene

- **D-09: Phase 62 does not touch `CHANGELOG.md`.** The measured precedent is split — in v0.9.0 the
  fix phase wrote its own bullet (`d0394773 docs(55-04)`), in v0.9.1 the fix phases 59/60 wrote
  nothing and release-prep Phase 61 authored every bullet (`70b2823b`, `8bb0288e docs(61-01)`). We
  follow v0.9.1. Phase 63's SC already requires one curated `## [0.9.2]` entry covering both
  v0.9.1's accumulated bullets and this fix, and constraint 7 requires the scratch-block relocation
  to happen before the heading rename — keeping all of it in one phase is what prevents a
  half-written entry. Phase 62 leaving `CHANGELOG.md` untouched also keeps its diff purely
  `typsphinx/translator.py` + new test files.

### Branch, CI and lint authority

- **D-10: Push at phase head, dispatch the authority CI run at phase end.** Push
  `gsd/v0.9.2-inline-image-blocker-fix-and-release` with `-u` in the phase's first plan. Measured:
  `.github/workflows/ci.yml`'s `push`/`pull_request` triggers are scoped to `main`/`develop`, so an
  early push costs zero CI minutes and runs nothing. It satisfies constraint 10's
  "reaches `origin` in the FIRST phase" immediately and makes the canonical ref the only tracking
  branch, which is what disambiguates the decoy when it reappears.
- **D-11: Exactly one authority run, dispatched after the phase's last commit.**
  `gh workflow run CI --ref gsd/v0.9.2-inline-image-blocker-fix-and-release`, waited to
  **completion**, with `windows-latest` and `macos-latest` named individually. `ruff`'s verdict is
  taken from that run's `Run linters` step — never from this machine, where `ruff` is an unrunnable
  generic-linux ELF in any freshly `uv sync`-provisioned worktree venv (constraint 11).
- **D-12: Expect the decoy `gsd/v0.9.2-milestone` to be re-created by the next commit helper.**
  Measured at discussion time: `git branch -vv` shows exactly one
  `0.9.2` branch, the canonical one, at `6224298e`, local-only with no upstream. If the decoy
  reappears, advance the canonical pointer **before** deleting it (the pointer-advance that must
  precede any deletion, constraint 10).
- **D-13: Zero pre-existing test edits, measured.** `git diff --name-status` over this phase's own
  range scoped to `tests/` must show only `A` entries. Any `M` is reported as an over-reach signal
  with its justification — never absorbed as routine test maintenance.

### Claude's Discretion

The owner delegated all four presented gray areas at once ("おすすめ設定"). Every D-01..D-13 above
is Claude's recommendation. Planning may refine the fixture's internal file names and the exact
golden-comparison helper shape; it may **not** weaken D-06 (byte-identity), D-09 (no CHANGELOG in
this phase), or D-13 (zero test edits) without returning to the owner.

### Folded Todos

- **`.planning/todos/pending/2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md`**
  (`resolves_phase: 62`) — "An inline image inside a paragraph is emitted with no separator before
  `image(...)`, so Typst aborts the whole compile with `expected semicolon or line break` and no PDF
  is produced." This is the phase's own defect. Its 4-row matrix is a strict subset of the 16
  measured shapes; closing it must record the **extended** matrix so the audit trail matches what
  was actually fixed.

</decisions>

<amendments>
## Amendments (2026-08-30, planning time — owner-acknowledged)

Three items above were corrected by a live 27-document / 18-master probe run during planning
(real `sphinx-build -b typstpdf`, real `typst.compile()`, HEAD `42f385cb`, repo restored clean
afterwards). The locked text above is left as written; these are additive corrections. The full
measurement record is the `<amendments>` block at the top of `62-01-PLAN.md` — read it before
disputing any of the three.

1. **D-08 / IMG-10 — the triad's scope, not its placement, was wrong.** Confining the triad to
   `visit_image()`'s non-`in_figure` branch leaves 4 of 18 masters refused: both legend shapes
   (a legend image has `self.in_figure == True` and never reaches that branch), the field-list-body
   concat shape (`depart_image()`'s unconditional trailing newlines break the concat expression with
   `cannot apply unary '+' to content`, an error the unfixed tree never produced), and `index`
   transitively. Amended: the leading half is hoisted above the `if self.in_figure:` / `else:` split
   so it runs on both paths, and the trailing half becomes concat-aware. Measured 18/18 compiling,
   exit 0, full suite 1517 passed / 1 skipped, zero test edits. `_emit_id_anchors()`'s call site
   stays exactly where D-08 said it should; shape E remains byte-identical, reproducing D-08's own
   probe result. REQUIREMENTS.md's IMG-10 carries the same note.

2. **D-06 — 8 of the 9 must-pass shapes are byte-identical, not 9.** `pass_c` (image first in its
   paragraph, text after) gains **exactly one empty line**, zero removals, because
   `_add_paragraph_separator()` now marks the paragraph as having content so the following text node
   emits its own separator. D-06 is **not** weakened to "it compiles": `pass_c` is bound by two
   committed goldens (unfixed-tree and post-fix) plus an assertion that their diff is exactly one
   added empty line with zero removals — a stricter binding than byte-identity, applied to the one
   shape where byte-identity was measurably unachievable. The other 8 keep plain byte-identity.

3. **D-01 — the document count is 27, not 26.** D-01's own enumeration (`index` + 16 FAIL +
   `pass_parent` + 9 PASS) sums to 27; "26 documents" is an arithmetic slip in the prose. The
   load-bearing half — **18 masters** — is unchanged and is what the plans build and assert.
</amendments>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and binding constraints
- `.planning/ROADMAP.md` §"🚧 v0.9.2" constraints 1–14 and §"Phase Details → Phase 62" SC#1–SC#5 —
  the fixed phase boundary and the five success criteria. Constraints 3, 4, 5, 10, 11, 12, 13 bear
  directly on this phase.
- `.planning/REQUIREMENTS.md` — IMG-08, IMG-09, IMG-10, TEST-05 verbatim, plus the **Out of Scope**
  table, which is binding and is the answer to any "while we're in here" impulse.
- `.planning/PROJECT.md` §"Current Milestone: v0.9.2" — including the **2026-08-30 amendment**:
  `visit_target` is a **false precedent** (markup-mode zero-width content, not a code-mode operand),
  and the `in_figure` newline is **cosmetic** (byte-identical PDF), not a hazard. Neither is to be
  re-litigated.

### Measured defect and regression surface
- `.planning/research/FEATURES.md` §Q1 — the 16 failing shapes with rST source, emitted Typst and
  verdict, one table row per fixture document to be written.
- `.planning/research/FEATURES.md` §Q2 — the 9 must-keep-passing shapes (A–I) and, per row, *which*
  existing mechanism each one depends on staying undisturbed.
- `.planning/research/ARCHITECTURE.md` — the triad extracted from five working visitors with line
  citations, and the three eliminated candidate mechanisms.
- `.planning/research/PITFALLS.md` — ranked failure modes, each with a repo incident citation.
- `.planning/research/SUMMARY.md` — the synthesis; note its Phase A/B/C shape was deliberately
  adopted as two phases, not three.
- `.planning/todos/pending/2026-08-29-inline-image-in-paragraph-emits-unseparated-expression.md` —
  the todo being closed.

### Code under change
- `typsphinx/translator.py:4718-4783` — `visit_image()` / `depart_image()`, the only product code
  this phase edits.
- `typsphinx/translator.py:933-943` — `_add_paragraph_separator()`.
- `typsphinx/translator.py:1651-1690` — `_emit_inline_concat_separator()` /
  `_mark_inline_concat_content()`.
- `typsphinx/translator.py:1775-1788` and `:1790+` (`visit_Text`) — the canonical call shape of the
  triad, to be mirrored verbatim.
- `typsphinx/translator.py:945-1028` — `_emit_id_anchors()`; see D-08 for the ordering hazard its
  trailing `\n` and `list_item_needs_separator = True` create.
- `typsphinx/builder.py:2505-2642` — `TypstPDFBuilder.finish()`; the aggregate-`ExtensionError`
  behaviour D-02 depends on.

### Test idiom precedents
- `tests/test_paragraph_concat_render_gate.py` — the gate idiom to copy: `TYPST_AVAILABLE` guard +
  `pytest.mark.skipif`, `_run_sphinx_build_typstpdf()` via `sys.executable -m sphinx`,
  `returncode == 0`, `"Typst compilation failed" not in stderr`, structural `.typ` check, `%PDF`
  magic-byte check, `encoding="utf-8"` on every read.
- `tests/test_abbr_pep_separator_render_gate.py` — the multi-shape FAIL+PASS pairing variant.
- `tests/fixtures/state_guard_three_master_gate/conf.py` — the multi-master fixture shape (masters
  sharing toctree'd children) D-01's 18-master layout extends.
- `tests/test_nested_figure_render_gate.py:256` and `tests/test_pdf_render_gate.py:2303` — the two
  exact-byte figure assertions that must pass **unedited** (SC#3).
- `.planning/milestones/v0.9.1-phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md`
  — the RED-first evidence file's format and the restore/transcribe/restore choreography.

### Execution environment
- `CLAUDE.md` §"Worktree-isolated execution" — mandatory per-worktree
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` then everything via `uv run`.
  Not conditional, not degraded for low parallelism.
- `.github/workflows/ci.yml` — triggers scoped to `main`/`develop` plus `workflow_dispatch`; the
  3-OS × py312/py313 matrix and the `Run linters` step D-11 takes its `ruff` verdict from.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **The separator triad** — `_add_paragraph_separator()` (translator.py:933),
  `_emit_inline_concat_separator()` / `_mark_inline_concat_content()` (translator.py:1651, 1666),
  and the `in_list_item` / `list_item_needs_separator` pair. Driven ~15+ times in this file already;
  `visit_Text`'s call shape (translator.py:1775-1788) is the canonical form to mirror.
- **The render-gate idiom** — 56 existing `tests/test_*_render_gate.py` modules share one skeleton
  (`TYPST_AVAILABLE` + `skipif`, `_run_sphinx_build_typstpdf()` as a subprocess of
  `sys.executable -m sphinx`, returncode/stderr/`.typ`-structure/`%PDF` assertions). Nothing new is
  invented for TEST-05; the module is a new instance of a proven template.
- **Multi-master fixture precedent** — 52 fixtures already declare more than one `typst_documents`
  entry; `state_guard_three_master_gate` (3 masters, 6 documents, shared toctree'd children) is the
  closest structural analog to D-01's layout.

### Established Patterns
- **Wrappers compile, content files do not** (COMP-02). `finish()` resolves the wrapper's
  outdir-relative path through `_wrapper_output_relpath()` and only ever compiles that. This is why
  a poisoned *content* file takes down every master that `#include()`s it, and why D-07's goldens
  compare content `.typ` files while the `%PDF` assertions target wrapper output.
- **`_emit_id_anchors()` is a no-op for a node with no ids** (early `return` at translator.py:1007),
  so it is invisible to 15 of the 16 failing shapes and only interacts with the fix on the
  id-carrying shape E.
- **`depart_image()` currently emits only `"\n\n"` for the non-`in_figure` case** and does no
  bookkeeping at all — the `_mark_inline_concat_content()` / `list_item_needs_separator` half is
  entirely absent today, which is why rows 3, 4, 9 and 10 need it.

### Integration Points
- `visit_image()`'s non-`in_figure` branch (translator.py:4753-4755) — where the leading separator
  is emitted.
- `depart_image()`'s non-`in_figure` branch (translator.py:4782-4783) — where the trailing mark
  goes.
- `tests/fixtures/<new>/conf.py` `typst_documents` — the 18-entry master list D-01 defines.
- No `typsphinx/__init__.py` change: no new config value, no new dependency, no `@preview` bump.

</code_context>

<specifics>
## Specific Ideas

- **The RED run must show a mixed verdict, not a uniform one.** 17 red masters and 1 green
  (`pass_parent`) in the same aggregate `ExtensionError` is the shape that proves the fixture
  discriminates. A RED run that is uniformly red is not yet trustworthy.
- **"For each failing shape" is satisfied by docname attribution, not by message variety.** All 16
  refusals carry the identical string `expected semicolon or line break` — measured. The evidence
  file must make that explicit so a later reader does not mistake the repetition for a copy-paste
  error.
- **Do not name the evidence file `62-VERIFICATION.md`.** See D-05.
- **`grep` obligations for SC#3 are repo-wide over `typsphinx/translator.py`:**
  `endswith("\n")`, `rstrip().endswith`, `[-1:]` must all still return nothing after the fix.

</specifics>

<deferred>
## Deferred Ideas

- **A cheap string-level (non-compiling) regression test** asserting on regexes like
  `)text\(...\)image\(` alongside the real-compile gate — listed as a differentiator in
  `research/FEATURES.md` Q3. Not built: TEST-05 specifies **one** gate module, the real compile is
  the authority, and 144 `image(` substring assertions across 20 test files already cover the string
  level. Revisit only if a future environment genuinely cannot run `typst.compile()`.
- **A doc-comment in `visit_image()` cross-referencing `visit_Text`'s triad by name** — a
  research differentiator with zero behavioural risk. Fold in if it costs nothing; not a
  requirement.

### Reviewed Todos (not folded)

- **`2026-08-29-hardcoded-delimiter-path-fragments-in-translator-relative-path-debug-logs.md`**
  (matched at 0.9 on the `translator` area) — the same MSG-02 shape Phase 60 fixed in three other
  modules, in a fourth module. Deferred: it is REQUIREMENTS.md's v2 item **MSG-06** and touching it
  would break D-13's zero-`M`-entries diff property for no requirement in this phase.
- **`2026-08-04-release-create-job-missing-uv-verify-end-to-end.md`** (REL-04) — v2, and its
  `resolves_phase` is 46. A real tag push at `/gsd-complete-milestone` exercises it; a failure there
  is handled then, not here.
- **`2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`** (QUA-10) — v2. Its consequence is
  absorbed by D-11 (CI holds lint authority), not fixed.
- **`2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`**
  (NUM-01) — v2. Note for fixture design: the new fixture must not introduce `numref` usage, or it
  will collide with a known-open defect.
- **`2026-08-16-dependabot-prs-die-on-uv-lock-locked-mismatch.md`** (CI-01) — v2, and its lockstep
  obligation lands in Phase 63 via constraint 6, not here.

</deferred>

---

*Phase: 62-the-visit-image-separator-fix-and-its-real-compile-gate*
*Context gathered: 2026-08-30*
