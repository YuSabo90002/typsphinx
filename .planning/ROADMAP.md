# Roadmap: typsphinx

## Milestones

- ✅ **v0.4.4 — CI-repair + modernize** — Phases 1–5 (shipped 2026-07-05) → [archive](milestones/v0.4.4-ROADMAP.md)
- ✅ **v0.5.0 — forward-ecosystem** — Phases 6–10 + 8.1 (shipped 2026-07-11) → [archive](milestones/v0.5.0-ROADMAP.md)
- ✅ **v0.6.0 — real-world robustness** — Phases 11–15 (shipped 2026-07-13) → [archive](milestones/v0.6.0-ROADMAP.md)
- 🚧 **v0.6.1 — rendering fidelity** — Phases 16–18 (planning, started 2026-07-13)

## Phases

**Phase Numbering:**

- Integer phases (16, 17, 18): Planned milestone work
- Decimal phases (16.1, 16.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — v0.6.1 continues from v0.6.0's Phase 15, so it starts at Phase 16
(never resets to 1).

<details>
<summary>✅ v0.4.4 — CI-repair + modernize (Phases 1–5) — SHIPPED 2026-07-05</summary>

Restored a fully green CI pipeline on `main` by pinning the runtime dependency graph back to a
known-good, reproducible combination, then modernized the Python floor (3.10–3.13) and dev tooling
and installed durability guardrails so the drift cannot silently recur. Full phase detail, success
criteria, decisions, and tech-debt notes are preserved in
[`milestones/v0.4.4-ROADMAP.md`](milestones/v0.4.4-ROADMAP.md).

- [x] Phase 1: Pin Runtime Dependencies to Known-Good (2/2 plans) — completed 2026-07-04
- [x] Phase 2: Verify the Green Baseline (3/3 plans) — completed 2026-07-04
- [x] Phase 3: Modernize Python Floor (3.10–3.13) (2/2 plans) — completed 2026-07-04
- [x] Phase 4: Refresh Dev Tooling (4/4 plans) — completed 2026-07-04
- [x] Phase 5: Durability Guardrails (4/4 plans) — completed 2026-07-05

</details>

<details>
<summary>✅ v0.5.0 — forward-ecosystem (Phases 6–10 + 8.1) — SHIPPED 2026-07-11</summary>

Ported typsphinx forward from the v0.4.4 known-good pins to the current ecosystem — Sphinx 9.1,
docutils 0.22, typst 0.15, Python 3.12–3.13 — bumping the four bundled `@preview` packages in
lockstep to compile cleanly (empirically closing the `unknown variable: kai` break), modernizing the
soft-deprecated docutils/Sphinx API, fixing a long-latent admonition markup/code-mode render bug,
adding a `typst compile` smoke gate, keeping the full 3-OS × Python 3.12–3.13 CI matrix green, and
releasing v0.5.0 to PyPI. Latest-only, no compatibility range. Full phase detail, success criteria,
decisions, and tech-debt notes are preserved in
[`milestones/v0.5.0-ROADMAP.md`](milestones/v0.5.0-ROADMAP.md).

- [x] Phase 6: Raise Runtime Pins + Python Floor (1/1 plan) — completed 2026-07-09
- [x] Phase 7: Bump @preview Packages + typst 0.15 (kai fix) (1/1 plan) — completed 2026-07-11
- [x] Phase 8: API & Test Compatibility (Sphinx 9 / docutils 0.22) (3/3 plans) — completed 2026-07-11
- [x] Phase 8.1: Admonition Rendering Fix (INSERTED) (4/4 plans) — completed 2026-07-11
- [x] Phase 9: Green CI Matrix + Smoke Test + Guardrails (2/2 plans) — completed 2026-07-11
- [x] Phase 10: Version-String Fix + v0.5.0 Release (2/2 plans) — completed 2026-07-11

</details>

<details>
<summary>✅ v0.6.0 — real-world robustness (Phases 11–15) — SHIPPED 2026-07-13</summary>

Compiled a large real-world documentation set (Sphinx's own `doc/` tree) end-to-end through the
`typstpdf` builder with no fatal Typst errors (GATE-02: ~14.4 MiB PDF, 0 errors), and added correct,
compilable rendering for the most-frequent previously-dropped docutils/Sphinx nodes. Driven by
Issue #114: fixed the two fatal figure/image bugs first (px→pt length conversion + `:target:`/caption
buffer-swap), stood up a standing real-`typst.compile()` acceptance gate (GATE-01) extended by every
node-handler phase, then landed the high-frequency handlers (versionmodified, `refid` cross-refs,
autodoc `desc_*`, footnotes via a doctree pre-pass, transition/topic/line_block/glossary/
tabular_col_spec/abbr) and a graphviz/inheritance_diagram graceful-degrade net. Zero new runtime
dependencies; the 3-way `@preview` version-sync surface untouched. Full phase detail, success
criteria, decisions, and tech-debt notes are preserved in
[`milestones/v0.6.0-ROADMAP.md`](milestones/v0.6.0-ROADMAP.md).

- [x] Phase 11: Issue #114 Fatal Fixes + Graceful-Degrade Net (3/3 plans) — completed 2026-07-12
- [x] Phase 12: High-Volume Independent Node Handlers (4/4 plans) — completed 2026-07-12
- [x] Phase 13: Shared Dispatch-Point Changes (topic + line blocks) (3/3 plans) — completed 2026-07-12
- [x] Phase 14: Footnotes (doctree pre-pass) (2/2 plans) — completed 2026-07-12
- [x] Phase 15: Full-Corpus Validation (3/3 plans) — completed 2026-07-12

</details>

### 🚧 v0.6.1 — rendering fidelity (Phases 16–18) — IN PROGRESS

**Milestone Goal:** Move `typstpdf` output from "compiles fatal-free" (achieved in v0.6.0) to
"renders faithfully" — implement the last two silently-dropped nodes (`todo_node`, `manpage`),
generalize the CSS-length converter (LEN-01 tech-debt), then run a human-assisted visual audit of the
compiled Sphinx-`doc/` corpus PDF against source to discover-and-fix the *silent* mis-render issues
(output that compiles fatal-free AND emits no warning, yet diverges from source) that a fatal-free
gate cannot catch.

**Standing bar (inherited GATE-01 convention):** every phase that changes a node handler ships or
extends a real `typst.compile()` acceptance fixture (the pattern in `tests/test_pdf_render_gate.py` /
`tests/test_corpus_gate.py`) — string-agreement asserts alone never suffice. The local environment
can run real typst compiles (typst 0.15.0 present; corpus cached at
`~/.cache/typsphinx-corpus-gate`), so real-compile success criteria are achievable.

**Milestone invariant:** zero new runtime dependencies and no `@preview` version bump are expected —
the 3-way version-sync surface (`writer.py` / `template_engine.py` / `templates/base.typ`) stays
untouched. Every target maps to native Typst 0.15 or already-bundled packages. Flag it during
planning if a phase is found to need otherwise.

- [ ] **Phase 16: Silent-Drop Node Handlers + Length-Converter Refactor** - Render `todo_node` and `manpage`, generalize the CSS-length → Typst-length helper
- [ ] **Phase 17: Rendering-Fidelity Audit** - Human-assisted visual diff of the corpus PDF vs. source → a severity-rated catalogue of silent mis-render issues (discovery)
- [ ] **Phase 18: Fidelity Fixes + Regression-Gate Close** - Fix every high-severity AUD-01 issue with real-compile fixtures, then close on the full-corpus regression gate

## Phase Details

### Phase 16: Silent-Drop Node Handlers + Length-Converter Refactor

**Goal**: The last two node types the v0.6.0 warning audit confirmed are still silently
`unknown_visit`-dropped in the Sphinx corpus (`todo_node` ×10, `manpage` ×10) render their content,
and v0.6.0's `visit_image`-local px→pt conversion is generalized into a single shared helper reused
at every length-bearing site.
**Depends on**: Nothing (first phase of the milestone; all three items are independent, additive,
low-risk translator changes that do NOT depend on the later audit)
**Requirements**: TODO-01, MAN-01, LEN-01
**Success Criteria** (what must be TRUE):

  1. A `.. todo::` directive (`todo_node`) renders its body content as an admonition-style block in the compiled PDF instead of being silently dropped.
  2. A `:manpage:` role (`manpage` node) renders as its literal page-reference text (e.g. `ls(1)`) instead of being silently dropped.
  3. The CSS-length → Typst-length conversion lives in one shared helper reused at every length-bearing site (`visit_image` now calls the shared helper), with no duplicated or divergent conversion logic remaining.
  4. Each of the three changes ships or extends a real `typst.compile()` acceptance fixture (GATE-01 pattern) proving the node renders / the converter round-trips through an actual compile — string-agreement asserts alone do not suffice.

**Plans**: 1/3 plans executed

Plans:
**Wave 1**

- [x] 16-01-PLAN.md — `todo_node` admonition-style `task` handler gated on `todo_include_todos` (TODO-01) + todo_render_gate real-compile fixture

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 16-02-PLAN.md — `manpage` italic literal-text handler via `visit_emphasis` delegation (MAN-01) + manpage_render_gate real-compile fixture

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 16-03-PLAN.md — Wire `_convert_length_to_typst` into figure `:figwidth:` + table `:width:` via `block(width:)` wrappers (LEN-01) + figwidth/table-width real-compile fixtures

### Phase 17: Rendering-Fidelity Audit

**Goal**: Produce a written, severity-rated catalogue of *silent* mis-render issues — output that
compiles fatal-free AND emits no warning, yet diverges from the source — by visually diffing the
compiled Sphinx-`doc/` corpus PDF against the rendered HTML / rST source. This is the discovery core
of the milestone; warnings only surface *dropped* content, so a human-assisted visual audit is the
only way to find silent divergence. The phase's output is a catalogue artifact, not code.
**Depends on**: Phase 16 (audit the corpus with the new `todo_node`/`manpage` handlers already
landed, so the audit surfaces genuinely-silent mis-renders rather than re-flagging the two drops
already scheduled for fixing)
**Requirements**: AUD-01
**Success Criteria** (what must be TRUE):

  1. The full Sphinx-`doc/` corpus is compiled to PDF via `typstpdf` and visually compared, page by page, against the rendered HTML / rST source.
  2. A written catalogue artifact exists listing every silent mis-render issue with its location (docname + node kind), a source-vs-output description, and a severity rating (high / medium / low).
  3. Genuine in-scope silent mis-renders are distinguished from already-known out-of-scope degradations (graphviz/inheritance placeholders, non-included-doc xrefs, Sphinx-side autodoc/`py:meth` warnings), so the FID-01 backlog targets only fidelity bugs typsphinx owns.
  4. Every issue rated "high" (content lost, unreadable, or grossly mis-structured) is enumerated as the FID-01 fix backlog and appended to `REQUIREMENTS.md` as `FID-01a`, `FID-01b`, … for Phase 18 to consume.

**Plans**: TBD (~1; human-assisted discovery)

Plans:

- [ ] 17-01: Compile corpus, visual source-vs-output diff, write the severity-rated catalogue + append FID-01a… to REQUIREMENTS.md

### Phase 18: Fidelity Fixes + Regression-Gate Close

**Goal**: Fix every high-severity issue in the AUD-01 catalogue — each fix proven by a real
`typst.compile()` regression fixture — then close the milestone by re-running the full-corpus gate to
confirm fatal-free non-regression and the elimination of the `todo_node`/`manpage` drops. This phase
is intentionally **discovery-sized**: its exact task list is enumerated by Phase 17 (AUD-01), so its
success criterion is "every high-severity issue fixed with a real-compile regression fixture," not a
fixed count, and its plan count stays TBD until the audit completes.
**Depends on**: Phase 17 (the concrete per-issue fix list IS the AUD-01 high-severity catalogue)
**Requirements**: FID-01 (expands to FID-01a, FID-01b, … from AUD-01), GATE-03
**Success Criteria** (what must be TRUE):

  1. Every AUD-01 issue at severity "high" is fixed in the translator, and each fix ships a real `typst.compile()` regression fixture (GATE-01 pattern) that would fail without the fix.
  2. The full Sphinx-`doc/` corpus still compiles fatal-free through `typstpdf` — GATE-02 non-regression: `index.pdf` produced, 0 errors (GATE-03).
  3. The re-run `unknown_visit` catalogue no longer contains `todo_node` or `manpage`, confirming Phase 16's handlers eliminated both drops on the real corpus (GATE-03).
  4. Zero new runtime dependencies and no `@preview` version bump — the 3-way version-sync surface (`writer.py` / `template_engine.py` / `templates/base.typ`) is unchanged.

**Plans**: TBD (audit-driven; enumerated by Phase 17)

Plans:

- [ ] 18-01: (per-issue fix plans enumerated by AUD-01) + GATE-03 corpus regression close

## Progress

**Execution Order:**
Active milestone (v0.6.1) phases execute in numeric order: 16 → 17 → 18

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Pin Runtime Dependencies to Known-Good | v0.4.4 | 2/2 | Complete | 2026-07-04 |
| 2. Verify the Green Baseline | v0.4.4 | 3/3 | Complete | 2026-07-04 |
| 3. Modernize Python Floor (3.10–3.13) | v0.4.4 | 2/2 | Complete | 2026-07-04 |
| 4. Refresh Dev Tooling | v0.4.4 | 4/4 | Complete | 2026-07-04 |
| 5. Durability Guardrails | v0.4.4 | 4/4 | Complete | 2026-07-05 |
| 6. Raise Runtime Pins + Python Floor | v0.5.0 | 1/1 | Complete | 2026-07-09 |
| 7. Bump @preview Packages + typst 0.15 (kai fix) | v0.5.0 | 1/1 | Complete | 2026-07-11 |
| 8. API & Test Compatibility (Sphinx 9 / docutils 0.22) | v0.5.0 | 3/3 | Complete | 2026-07-11 |
| 8.1 Admonition Rendering Fix (INSERTED) | v0.5.0 | 4/4 | Complete | 2026-07-11 |
| 9. Green CI Matrix + Smoke Test + Guardrails | v0.5.0 | 2/2 | Complete | 2026-07-11 |
| 10. Version-String Fix + v0.5.0 Release | v0.5.0 | 2/2 | Complete | 2026-07-11 |
| 11. Issue #114 Fatal Fixes + Graceful-Degrade Net | v0.6.0 | 3/3 | Complete | 2026-07-12 |
| 12. High-Volume Independent Node Handlers | v0.6.0 | 4/4 | Complete | 2026-07-12 |
| 13. Shared Dispatch-Point Changes (topic + line blocks) | v0.6.0 | 3/3 | Complete | 2026-07-12 |
| 14. Footnotes (doctree pre-pass) | v0.6.0 | 2/2 | Complete | 2026-07-12 |
| 15. Full-Corpus Validation | v0.6.0 | 3/3 | Complete | 2026-07-12 |
| 16. Silent-Drop Node Handlers + Length-Converter Refactor | v0.6.1 | 1/3 | In Progress|  |
| 17. Rendering-Fidelity Audit | v0.6.1 | 0/TBD | Not started | - |
| 18. Fidelity Fixes + Regression-Gate Close | v0.6.1 | 0/TBD | Not started | - |

---
*Roadmap created: 2026-07-04 · Reorganized: 2026-07-05 at v0.4.4 milestone close · v0.5.0 phases (6–10) added: 2026-07-09 · Reorganized: 2026-07-11 at v0.5.0 milestone close · v0.6.0 phases (11–15) added: 2026-07-11 · Reorganized: 2026-07-13 at v0.6.0 milestone close · v0.6.1 phases (16–18) added: 2026-07-13*
