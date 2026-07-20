# Roadmap: typsphinx

## Milestones

- ✅ **v0.4.4 — CI-repair + modernize** — Phases 1–5 (shipped 2026-07-05) → [archive](milestones/v0.4.4-ROADMAP.md)
- ✅ **v0.5.0 — forward-ecosystem** — Phases 6–10 + 8.1 (shipped 2026-07-11) → [archive](milestones/v0.5.0-ROADMAP.md)
- ✅ **v0.6.0 — real-world robustness** — Phases 11–15 (shipped 2026-07-13) → [archive](milestones/v0.6.0-ROADMAP.md)
- ✅ **v0.6.1 — rendering fidelity** — Phases 16–18 (shipped 2026-07-19) → [archive](milestones/v0.6.1-ROADMAP.md)
- 🚧 **v0.6.2 — rendering fidelity round 2** — Phases 19–23 (planning, started 2026-07-20)

## Phases

**Phase Numbering:**

- Integer phases (19, 20, 21): Planned milestone work
- Decimal phases (19.1, 19.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.6.2 continues from v0.6.1's Phase 18, so it starts at Phase 19.

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

<details>
<summary>✅ v0.6.1 — rendering fidelity (Phases 16–18) — SHIPPED 2026-07-19</summary>

Moved `typstpdf` output from "compiles fatal-free" (achieved in v0.6.0) to "renders faithfully":
implemented the last two silently-dropped nodes (`todo_node` → gentle-clues `task()` box gated on
`todo_include_todos`; `manpage` → italic literal page text via `visit_emphasis` delegation),
generalized v0.6.0's `visit_image`-local px→pt fix into one shared `_convert_length_to_typst` helper
reused at every length-bearing figure/table site (LEN-01), then ran a full 151/151-docname
human-assisted visual audit of the Sphinx v9.1.0 `doc/` corpus PDF against its `-b html` baseline —
15 systemic findings catalogued, human-confirmed (14 accepted / 1 rejected), the sole high-severity
finding (F12 wide-table glyph collision + right-margin clip) fixed via fr-weighted `columns:` from
docutils colwidth + in-table U+200B break injection (FID-01a) with a real-compile regression fixture,
and the milestone closed on the full ~684-page corpus regression gate (fatal-free, `unknown_visit`
catalogue empty). Zero new runtime dependencies; the 3-way `@preview` version-sync surface untouched.
The 13 medium/low audit findings are recorded as a Future-Requirements pointer. Full phase detail,
success criteria, decisions, and tech-debt notes are preserved in
[`milestones/v0.6.1-ROADMAP.md`](milestones/v0.6.1-ROADMAP.md).

- [x] Phase 16: Silent-Drop Node Handlers + Length-Converter Refactor (3/3 plans) — completed 2026-07-16
- [x] Phase 17: Rendering-Fidelity Audit (4/4 plans) — completed 2026-07-19
- [x] Phase 18: Fidelity Fixes + Regression-Gate Close (2/2 plans) — completed 2026-07-19

</details>

### 🚧 v0.6.2 — rendering fidelity round 2 (Phases 19–23) — IN PROGRESS

**Milestone Goal:** Resolve the 13 medium/low silent mis-render findings the v0.6.1 audit left open
(F1–F15 minus the fixed high-severity F12 and the rejected F4), delivered as **one coherent series of
translator fixes grouped by root cause** (clusters A–F) rather than 13 unrelated tickets — a single
`translator.py` separator/spacing fix typically resolves several findings in a cluster — plus the
independent Issue #117 `typstpdf` target-name PDF bug (a `builder.py`/`pdf.py` change that does NOT
share the translator root causes). Source of record for every FID finding:
[`milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md`](milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md)
(D-01a human-confirmed at the 17-03 gate, severity-final).

**Standing bar (inherited GATE-01 convention):** every phase that changes a node handler ships or
extends a real `typst.compile()` acceptance fixture (the `tests/test_pdf_render_gate.py` /
`tests/test_corpus_gate.py` pattern) — string-agreement asserts alone never suffice. The local
environment runs real typst compiles (typst 0.15.0; corpus cached at `~/.cache/typsphinx-corpus-gate`),
so real-compile success criteria are achievable.

**Milestone invariant (every phase):** zero new runtime dependencies, no `@preview` version bump — the
3-way version-sync surface (`writer.py` / `template_engine.py` / `templates/base.typ`) stays untouched.
Every target maps to native Typst 0.15 or already-bundled packages; none is expected to need a bump.
Flag it during planning if a phase is found to need otherwise.

**Release process (`branching_strategy: milestone`, decided 2026-07-20):** the ship unit is the
milestone. The final Phase 23 is a prep-only Release phase (version bump + CHANGELOG + closing
regression gate); the irreversible publish (tag `v0.6.2` → `release.yml` → PyPI) runs later at
`/gsd-complete-milestone`, mirroring the v0.5.0 Phase 10 / v0.6.1 pattern.

- [x] **Phase 19: Block Separation Fixes (Cluster A)** - Restore lost inter-block/inter-element separation across paragraphs-in-list-items, sibling signatures, rubric/option headings, definition terms, and back-to-back confvals — the dominant audit root cause (FID-02..FID-06) (completed 2026-07-20)
- [ ] **Phase 20: Signature Token Spacing (Cluster B)** - Restore lost intra-signature token spacing: the `class `/`exception ` annotation prefix, C/C++ inter-token spaces, and `:type:`/`:default:` colon-space (FID-07..FID-09)
- [ ] **Phase 21: Residual Fidelity Fixes (Clusters C/D/E/F)** - The remaining small-root-cause findings: inline-literal margin overflow, paragraph soft-newline reflow, the codly config-wrapper leak, and meaning-bearing inline styling (FID-10..FID-14)
- [ ] **Phase 22: typstpdf Target-Name PDF Fix (Issue #117)** - `TypstPDFBuilder.finish()` names the compiled PDF after the `typst_documents` target, not the source docname (PDF-01)
- [ ] **Phase 23: v0.6.2 Release Prep + Regression-Gate Close** - Bump `pyproject.toml` to 0.6.2 + add the `CHANGELOG.md` `[0.6.2]` entry, close on the full-corpus regression gate; prep-only (publish runs at `/gsd-complete-milestone`)

## Phase Details

### Phase 19: Block Separation Fixes (Cluster A)

**Goal**: The dominant audit root cause — adjacent block or sibling elements emitted with no separator
— is resolved as one coherent set of `visit_*`/`depart_*` separator fixes, so every affected construct
renders with the visible separation the `-b html` authority shows instead of concatenating.
**Depends on**: Nothing (first phase of the milestone; the block-separation cluster is the shared root
cause the rest of the translator series builds on)
**Requirements**: FID-02, FID-03, FID-04, FID-05, FID-06
**Success Criteria** (what must be TRUE):

  1. Consecutive `paragraph`s inside a `list_item` render with visible separation instead of concatenating ("role.For example" → "role. For example"), corpus-wide — proven by a real-compile fixture (FID-02).
  2. Multiple sibling `desc_signature`s (overloads / `alias` groups / multi-option directives) render on separate lines instead of running together on one line (FID-03).
  3. A `rubric` option-group heading (and a directive-option "Options" heading) renders separated from the first following `option`/`:field:` instead of merging onto it (FID-04).
  4. A `definition_list` `term` renders on its own line, separated from its `definition`, when the list is nested in a `list_item` or the definition body opens with a nested list (FID-05); and back-to-back body-less `confval` `desc` nodes render as distinct, separated entries instead of one unbroken blob (FID-06).
  5. Every separator fix ships or extends a real `typst.compile()` regression fixture (GATE-01) that would fail without the fix; zero new runtime deps, no `@preview` bump, the 3-way version-sync surface untouched.

**Plans**: 3/3 plans executed

Plans:
**Wave 1**

- [x] 19-01-PLAN.md — Shared `_emit_forced_break` helper + the two `parbreak()` sites (FID-02 paragraphs-in-list-item, FID-06 back-to-back body-less confvals)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 19-02-PLAN.md — The two `linebreak()` sibling sites (FID-03 sibling desc_signatures, FID-04 rubric/option heading)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 19-03-PLAN.md — The `terms(separator: linebreak())` site (FID-05 definition_list term/definition; the non-helper fix)

### Phase 20: Signature Token Spacing (Cluster B)

**Goal**: Intra-signature token spacing that is currently swallowed inside and around signature/field
tokens is restored, so Python and C/C++ signatures and object-description fields read with correct
inter-token spacing matching the `-b html` / `-b text` authority.
**Depends on**: Phase 19 (shares the `desc_*` / signature rendering surface; sequenced after the
block-separation cluster so the separator idiom is settled before token-level spacing is tuned)
**Requirements**: FID-07, FID-08, FID-09
**Success Criteria** (what must be TRUE):

  1. The `desc_annotation` "class "/"exception " keyword prefix keeps its trailing space ("classsphinx.builders…" → "class sphinx.builders…") on every `py:class`/`py:exception`/`autoclass` — proven by a real-compile fixture (FID-07).
  2. C/C++ `desc_signature` and inline `c/cpp:expr` preserve all inter-token spaces (around `*`/`&`, type↔identifier, after the keyword prefix): "Py_ssize_tnitems" → "Py_ssize_t nitems" (FID-08).
  3. `field_list` `:type:`/`:default:` object-description fields render with colon-space and preserved field boundaries ("Type:int (a number)Default:42" → "Type: int (a number)  Default: 42") (FID-09).
  4. Each spacing fix ships or extends a real `typst.compile()` regression fixture (GATE-01); zero new runtime deps, no `@preview` bump, the 3-way version-sync surface untouched.

**Plans**: TBD

Plans:

- [ ] TBD (enumerated at `/gsd-plan-phase 20`)

### Phase 21: Residual Fidelity Fixes (Clusters C/D/E/F)

**Goal**: The remaining smaller-root-cause fidelity findings — inline-literal right-margin overflow,
lost paragraph reflow, the codly config-wrapper leak, and meaning-bearing inline styling — are fixed as
the tail of the coherent translator series, each isolated to its own node handler.
**Depends on**: Phase 20 (sequenced last among the translator-fix phases; these are independent,
small-blast-radius edits that land after the two large clusters)
**Requirements**: FID-10, FID-11, FID-12, FID-13, FID-14
**Success Criteria** (what must be TRUE):

  1. A long run of inline `literal` roles wraps within the text margin instead of overflowing and clipping mid-token (clipping = content loss), kin to the fixed F12 — proven by a real-compile fixture (FID-10).
  2. reST soft/semantic line breaks inside a paragraph collapse to a single space instead of rendering as HARD line breaks (no ragged short lines), corpus-wide (FID-11).
  3. A `literal_block` with BOTH a `:caption:` AND nested in a `list_item` no longer leaks its codly config wrapper as visible text (`{ codly(number-format: none)` … `}`) (FID-12).
  4. External named `reference` hyperlinks render with distinguishing styling and correct boundary spacing — no stray space where adjacent inline text exists (FID-13); and `*`/`/` PEP 3102/570 separators render without injecting their hover-title text inline ("* (Keyword-only parameters separator …)" → "*") (FID-14).
  5. Every fix ships or extends a real `typst.compile()` regression fixture (GATE-01); zero new runtime deps, no `@preview` bump, the 3-way version-sync surface untouched.

**Plans**: TBD

Plans:

- [ ] TBD (enumerated at `/gsd-plan-phase 21`)

### Phase 22: typstpdf Target-Name PDF Fix (Issue #117)

**Goal**: `sphinx-build -b typstpdf` names the compiled PDF after the `typst_documents` target name
(`manual.pdf`), not the source docname (`index.pdf`) — an independent `builder.py`/`pdf.py` fix that
does NOT share the translator root causes of Phases 19–21.
**Depends on**: Independent of Phases 19–21 (separate `builder.py`/`pdf.py` surface); sequenced here
after the translator series and before Release.
**Requirements**: PDF-01
**Success Criteria** (what must be TRUE):

  1. With `typst_documents = [('index', 'manual.typ', 'User Manual', 'Development Team')]`, `sphinx-build -b typstpdf` emits `manual.pdf` (the target name), not `index.pdf` (the source docname) (PDF-01).
  2. `TypstPDFBuilder.finish()` derives the output PDF name from the `typst_documents` target tuple, consistent with the already-correct `.typ` filename mapping (Issue #117).
  3. A regression test asserts the emitted PDF filename matches the configured `typst_documents` target (extends the builder / render-gate test pattern) and would fail against the pre-fix `index.pdf` behavior.
  4. Zero new runtime deps, no `@preview` bump, the 3-way version-sync surface untouched.

**Plans**: TBD

Plans:

- [ ] TBD (enumerated at `/gsd-plan-phase 22`)

### Phase 23: v0.6.2 Release Prep + Regression-Gate Close

**Goal**: Prepare the v0.6.2 release — bump the version and curate the CHANGELOG — and close the
milestone on a full-corpus regression gate. **Prep-only:** the irreversible publish (tag `v0.6.2` →
`release.yml` → PyPI) is executed later at `/gsd-complete-milestone`, mirroring the v0.5.0 Phase 10 /
v0.6.1 pattern.
**Depends on**: Phases 19, 20, 21, 22 (all fidelity + Issue #117 fixes land before the version bump and
the closing corpus re-run)
**Requirements**: (none — release/close phase; all 14 v1 requirements are delivered by Phases 19–22)
**Success Criteria** (what must be TRUE):

  1. `pyproject.toml` version is bumped `0.6.1` → `0.6.2` as the sole version literal, and `uv.lock` is regenerated in lockstep (`uv sync --locked` green).
  2. `CHANGELOG.md` carries a curated `## [0.6.2]` entry (the single source for the eventual Release body) covering the 13 fidelity fixes (clusters A–F) and the Issue #117 target-name fix.
  3. The full ~684-page Sphinx `doc/` corpus re-run through `-b typstpdf` is fatal-free (valid `%PDF` magic, 0 errors) and the `unknown_visit` catalogue is still clean — the closing regression gate, mirroring v0.6.1's GATE-03.
  4. The milestone invariant is confirmed held: zero new runtime dependencies, no `@preview` version bump, the 3-way version-sync surface (`writer.py` / `template_engine.py` / `templates/base.typ`) untouched.
  5. Scope fence held — no tag, no PyPI publish, no GitHub Release in this phase (deferred to `/gsd-complete-milestone`).

**Plans**: TBD

Plans:

- [ ] TBD (enumerated at `/gsd-plan-phase 23`)

## Progress

**Execution Order:**
Active milestone (v0.6.2) phases execute in numeric order: 19 → 20 → 21 → 22 → 23

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
| 16. Silent-Drop Node Handlers + Length-Converter Refactor | v0.6.1 | 3/3 | Complete | 2026-07-16 |
| 17. Rendering-Fidelity Audit | v0.6.1 | 4/4 | Complete | 2026-07-19 |
| 18. Fidelity Fixes + Regression-Gate Close | v0.6.1 | 2/2 | Complete | 2026-07-19 |
| 19. Block Separation Fixes (Cluster A) | v0.6.2 | 3/3 | Complete    | 2026-07-20 |
| 20. Signature Token Spacing (Cluster B) | v0.6.2 | 0/TBD | Not started | - |
| 21. Residual Fidelity Fixes (Clusters C/D/E/F) | v0.6.2 | 0/TBD | Not started | - |
| 22. typstpdf Target-Name PDF Fix (Issue #117) | v0.6.2 | 0/TBD | Not started | - |
| 23. v0.6.2 Release Prep + Regression-Gate Close | v0.6.2 | 0/TBD | Not started | - |

## Backlog

Candidate work not yet scoped into a milestone. Promote items with `/gsd-review-backlog`, or
pull the whole rendering-fidelity cluster into the next milestone via `/gsd-new-milestone`.
Numbered 999.x so milestone reorganization never renumbers or drops them.

### 999.1 — Rendering-Fidelity Round 2 (v0.6.1 audit follow-up: the 13 medium/low findings)

Source of record: [`milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md`](milestones/v0.6.1-phases/17-rendering-fidelity-audit/17-AUDIT-CATALOGUE.md)
(D-01a human-confirmed, severity-final). v0.6.1 fixed only the sole **high** finding (F12 → FID-01a,
wide-table collision/clip). The remaining **11 medium + 2 low** silent mis-render findings are
enumerated below, grouped by root cause so they land as **one coherent series of translator fixes**,
not 13 unrelated tickets. Each retains its catalogue F-number for traceability. All share the
milestone invariant (zero new runtime deps, no `@preview` bump) and the standing GATE-01 bar (every
node-handler change ships/extends a real `typst.compile()` regression fixture).

> **Promoted to v0.6.2 (2026-07-20):** cluster A → Phase 19 (FID-02..FID-06), cluster B → Phase 20
> (FID-07..FID-09), clusters C/D/E/F → Phase 21 (FID-10..FID-14). Retained here as the source-of-record
> cluster grouping; the active roadmap entries live under §Phases / §Phase Details above.

**Cluster A — Lost inter-block / inter-element separation** (the dominant root cause; adjacent block
or sibling elements emitted with no separator/break — very likely a small shared set of
`visit_*`/`depart_*` separator fixes):

- [ ] **F1** (medium) — consecutive `paragraph`s inside a `list_item` concatenate with no space ("role.For example"); `visit_paragraph`/`depart_paragraph` early-return when `in_list_item` (translator.py ~678–704). Corpus-wide.
- [ ] **F7** (medium) — multiple sibling `desc_signature`s (overloads / `alias` groups / multi-option directives) run together on one line with no break.
- [ ] **F13** (medium) — `rubric` option-group heading concatenates onto the first following `option`; directive-option "Options" heading merges onto the first `:field:`. Likely shares F1's block-separation root cause in a different node context.
- [ ] **F14** (medium) — `definition_list` `term` merges onto its `definition` (when the list is nested in a `list_item`, or the definition body opens with a nested list).
- [ ] **F15** (medium) — back-to-back body-less `confval` `desc` nodes concatenate into one unbroken blob (4 confvals merged on `usage/extensions/coverage`).

**Cluster B — Lost intra-signature token spacing** (space swallowed inside/around signature tokens):

- [ ] **F2** (medium) — `desc_annotation` "class "/"exception " keyword prefix loses its trailing space ("classsphinx.builders…"). Every `py:class`/`py:exception`/`autoclass`.
- [ ] **F3** (medium) — C/C++ `desc_signature` & inline `c/cpp:expr` lose ALL inter-token spaces (around `*`/`&`, type↔identifier, after keyword prefix): "Py_ssize_tnitems".
- [ ] **F5** (medium) — `field_list` `:type:`/`:default:` (object-description fields) render inline with no colon-space and merged field boundaries ("Type:int (a number)Default:42").

**Cluster C — Right-margin overflow / no wrapping** (kin to the fixed F12; a shared "avoid right-margin
overflow" primitive may serve both — see catalogue D-10 kinship note):

- [ ] **F6** (medium) — a long run of inline `literal` roles overflows the right text margin and is clipped mid-token (trailing roles lost = content loss). `usage/domains/cpp` p.85.

**Cluster D — Paragraph reflow lost:**

- [ ] **F9** (medium) — reST semantic/soft line breaks inside a paragraph render as HARD line breaks (ragged short lines) instead of collapsing to a space; the translator preserves intra-paragraph source newlines. Systemic, corpus-wide.

**Cluster E — codly config wrapper leak:**

- [ ] **F11** (medium) — a `literal_block` with BOTH a `:caption:` AND nested in a `list_item` leaks its codly config wrapper as literal visible text (`{ codly(number-format: none)` … `}`). The `codly_prefix="#"` guard (translator.py ~1504–1520) misses the combined caption+list-item case.

**Cluster F — Meaning-bearing inline styling (low severity):**

- [ ] **F8** (low) — external named `reference` hyperlinks flatten to plain, undistinguished text (+ a stray boundary space where adjacent inline text exists). Link styling is meaning-bearing (D-06). Corpus-wide.
- [ ] **F10** (low) — `abbreviation`/`desc_sig_operator` for `*` (PEP 3102) and `/` (PEP 570) separators inject the hover-title text inline ("* (Keyword-only parameters separator …)"), cluttering every keyword-only/positional-only signature.

**Not backlog (recorded for context):** F4 was REJECTED at the 17-03 gate (Sphinx-side, builder-independent — not a typsphinx bug). F12 is DONE (FID-01a, Phase 18).

### 999.2 — Issue #117: typstpdf PDF uses source name instead of target name (BACKLOG)

**Goal:** [Captured for future planning]
**Requirements:** TBD
**Plans:** 0 plans

Source: [Issue #117](https://github.com/YuSabo90002/typsphinx/issues/117) (`bug`, OPEN, reported 2026-07-19 against v0.6.0 / Sphinx 9.1 / Python 3.14).

> **Promoted to v0.6.2 (2026-07-20):** → Phase 22 (PDF-01). Retained here as the source-of-record
> issue description; the active roadmap entry lives under §Phases / §Phase Details above.

**Reported behavior:** With `typst_documents = [('index', 'manual.typ', 'User Manual', 'Development Team')]`, running `sphinx-build -b typstpdf` emits the PDF named after the **source** docname (`index.pdf`) instead of the **target** name declared in `typst_documents` (`manual.pdf`). The `.typ` filename mapping appears honored; the PDF-compile step in `TypstPDFBuilder.finish()` likely re-derives the output name from the source docname rather than the target tuple. Investigate `builder.py` (`TypstPDFBuilder.finish()` / master-doc → PDF path derivation) and confirm against `pdf.py`.

Plans:

- [ ] TBD (promote with /gsd-review-backlog when ready)

---
*Roadmap created: 2026-07-04 · Reorganized: 2026-07-05 at v0.4.4 milestone close · v0.5.0 phases (6–10) added: 2026-07-09 · Reorganized: 2026-07-11 at v0.5.0 milestone close · v0.6.0 phases (11–15) added: 2026-07-11 · Reorganized: 2026-07-13 at v0.6.0 milestone close · v0.6.1 phases (16–18) added: 2026-07-13 · Reorganized: 2026-07-19 at v0.6.1 milestone close · Backlog seeded (999.1 — 13 medium/low fidelity findings, grouped A–F): 2026-07-20 · Backlog item 999.2 added (Issue #117 — typstpdf target-name bug): 2026-07-20 · v0.6.2 phases (19–23) added: 2026-07-20*
