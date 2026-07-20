# Roadmap: typsphinx

## Milestones

- ✅ **v0.4.4 — CI-repair + modernize** — Phases 1–5 (shipped 2026-07-05) → [archive](milestones/v0.4.4-ROADMAP.md)
- ✅ **v0.5.0 — forward-ecosystem** — Phases 6–10 + 8.1 (shipped 2026-07-11) → [archive](milestones/v0.5.0-ROADMAP.md)
- ✅ **v0.6.0 — real-world robustness** — Phases 11–15 (shipped 2026-07-13) → [archive](milestones/v0.6.0-ROADMAP.md)
- ✅ **v0.6.1 — rendering fidelity** — Phases 16–18 (shipped 2026-07-19) → [archive](milestones/v0.6.1-ROADMAP.md)

## Phases

**Phase Numbering:**

- Integer phases (16, 17, 18): Planned milestone work
- Decimal phases (16.1, 16.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
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

## Progress

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

---
*Roadmap created: 2026-07-04 · Reorganized: 2026-07-05 at v0.4.4 milestone close · v0.5.0 phases (6–10) added: 2026-07-09 · Reorganized: 2026-07-11 at v0.5.0 milestone close · v0.6.0 phases (11–15) added: 2026-07-11 · Reorganized: 2026-07-13 at v0.6.0 milestone close · v0.6.1 phases (16–18) added: 2026-07-13 · Reorganized: 2026-07-19 at v0.6.1 milestone close · Backlog seeded (999.1 — 13 medium/low fidelity findings, grouped A–F): 2026-07-20*
