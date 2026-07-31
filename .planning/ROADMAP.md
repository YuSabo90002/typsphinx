# Roadmap: typsphinx

## Milestones

- ✅ **v0.4.4 — CI-repair + modernize** — Phases 1–5 (shipped 2026-07-05) → [archive](milestones/v0.4.4-ROADMAP.md)
- ✅ **v0.5.0 — forward-ecosystem** — Phases 6–10 + 8.1 (shipped 2026-07-11) → [archive](milestones/v0.5.0-ROADMAP.md)
- ✅ **v0.6.0 — real-world robustness** — Phases 11–15 (shipped 2026-07-13) → [archive](milestones/v0.6.0-ROADMAP.md)
- ✅ **v0.6.1 — rendering fidelity** — Phases 16–18 (shipped 2026-07-19) → [archive](milestones/v0.6.1-ROADMAP.md)
- ✅ **v0.6.2 — rendering fidelity round 2** — Phases 19–23 (+22.1–22.4) (shipped 2026-07-23) → [archive](milestones/v0.6.2-ROADMAP.md)
- ✅ **v0.6.3 — config & docs measured fidelity + captioned tables** — Phases 24–28 (+27.1) (shipped 2026-07-25) → [archive](milestones/v0.6.3-ROADMAP.md)
- ✅ **v0.6.4 — Read the Docs migration** — Phases 29–33 (+30.1) (shipped 2026-07-28) → [archive](milestones/v0.6.4-ROADMAP.md)
- ✅ **v0.6.5 — inline-math separator hotfix** — Phases 34–35 (shipped 2026-07-29) → [archive](milestones/v0.6.5-ROADMAP.md)
- 🚧 **v0.7.0 — API rendering design overhaul** — Phases 36–41 (in progress, started 2026-07-29)

## Phases

**Phase Numbering:**

- Integer phases (36, 37, …): Planned milestone work
- Decimal phases (36.1, 36.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.7.0 continues from v0.6.5's last phase (35), so it starts at Phase 36.

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

<details>
<summary>✅ v0.6.2 — rendering fidelity round 2 (Phases 19–23, +22.1–22.4) — SHIPPED 2026-07-23</summary>

Resolved the 13 medium/low silent mis-render findings the v0.6.1 audit left open, delivered as one
coherent series of `translator.py` fixes grouped by root cause (clusters A–F) rather than 13 unrelated
tickets — block separation (FID-02..FID-06), intra-signature token spacing (FID-07..FID-09), and the
residual inline-literal overflow / paragraph reflow / codly-wrapper leak / meaning-bearing inline
styling findings (FID-10..FID-14) — each pinned by a fail-pre-fix real-`typst.compile()` GATE-01
fixture. Alongside the translator series, five inserted builder/config/docs phases: Issue #117
`typstpdf` target-name PDF fix (PDF-01), nested-master compile-root alignment (PDF-02), a dead-config
sweep that deleted `typst_output_dir`/`typst_author_params` and repaired the broken `typst_package`
Typst-Universe path end-to-end (CONF-01..CONF-03), builder-warning hardening so a missing/malformed
master fails loudly instead of a silent successful build (WR-01/WR-02), and a full-text README/CLAUDE.md
accuracy pass that removed unverifiable numeric claims rather than re-measuring them (DOC-01..DOC-05).
Closed on the full ~684-page corpus regression gate (fatal-free, valid `%PDF`, `unknown_visit`
catalogue empty). Zero new runtime dependencies; the 3-way `@preview` version-sync surface untouched.
Closeout `override_closeout` — a single non-blocking pytest-xdist backstop item on Phase 22.3 abstained
to human per the honest-verifier rule (all ROADMAP SCs independently verified with direct evidence).
Full phase detail, success criteria, decisions, and tech-debt notes are preserved in
[`milestones/v0.6.2-ROADMAP.md`](milestones/v0.6.2-ROADMAP.md).

- [x] Phase 19: Block Separation Fixes (Cluster A) (3/3 plans) — completed 2026-07-20
- [x] Phase 20: Signature Token Spacing (Cluster B) (2/2 plans) — completed 2026-07-20
- [x] Phase 21: Residual Fidelity Fixes (Clusters C/D/E/F) (3/3 plans) — completed 2026-07-20
- [x] Phase 22: typstpdf Target-Name PDF Fix (Issue #117) (3/3 plans) — completed 2026-07-21
- [x] Phase 22.1: typstpdf Compile-Root Alignment for Nested Masters (INSERTED) (4/4 plans) — completed 2026-07-22
- [x] Phase 22.2: Dead Config-Value Sweep (INSERTED) (6/6 plans) — completed 2026-07-22
- [x] Phase 22.3: typstpdf Builder Warning Hardening (INSERTED) (3/3 plans) — completed 2026-07-22
- [x] Phase 22.4: README Claim-vs-Measured-Reality Drift Resolution (INSERTED) (3/3 plans) — completed 2026-07-23
- [x] Phase 23: v0.6.2 Release Prep + Regression-Gate Close (3/3 plans) — completed 2026-07-23

</details>

<details>
<summary>✅ v0.6.3 — config & docs measured fidelity + captioned tables (Phases 24–28, +27.1) — SHIPPED 2026-07-25</summary>

Closed the gap between what the docs promised and what the build actually did. Three tracks: the
dead-config sweep round 2 — deleted the inert `typst_toctree_defaults` (CONF-05) and implemented the
`typst_elements` `papersize`/`fontsize` pass-through behind a curated allowlist that fails loudly on an
unknown key instead of silently dropping it (CONF-04); the reimplementation of external PR#98 so a
captioned `.. table::` renders as `figure(table(...), caption, kind: table)` with native "Table N"
numbering and resolvable `:numref:`/`:ref:` (TBL-01/TBL-02), fixing a stale-cell-buffer bug that had
been silently eating the second table's caption; and docs measured fidelity — the unreachable orphan
`docs/configuration.rst` deleted and every phantom `typst_*` name purged so config is documented in one
canonical place (DOC-06/DOC-07). An inserted Phase 27.1 wired Typst's typesetting `lang` to Sphinx's
own `language` conf (CONF-07), so a `language = "ja"` project's captioned tables read 「表 N」
("Table N" in Japanese) rather than "Table N" — the one change that amended the milestone's `base.typ`-byte-unchanged invariant, and
only for the two lines that add the `lang` parameter. Phase 28 (prep-only) bumped the version, curated
the CHANGELOG, and closed on the full-corpus regression gate. Full phase detail, success criteria,
decisions, and the GATE-01 evidence are preserved in
[`milestones/v0.6.3-ROADMAP.md`](milestones/v0.6.3-ROADMAP.md).

- [x] Phase 24: Delete `typst_toctree_defaults` (1/1 plan) — completed 2026-07-23
- [x] Phase 25: Captioned Table Figure Wrap + Cross-References (2/2 plans) — completed 2026-07-24
- [x] Phase 26: `typst_elements` papersize/fontsize Pass-Through (2/2 plans) — completed 2026-07-24
- [x] Phase 27: Docs Measured Fidelity — Orphan Delete + Phantom Names (1/1 plan) — completed 2026-07-24
- [x] Phase 27.1: Typst Typesetting lang Follows Sphinx `language` (INSERTED) (3/3 plans) — completed 2026-07-25
- [x] Phase 28: v0.6.3 Release Prep + Regression-Gate Close (3/3 plans) — completed 2026-07-25

**Closed at milestone close (not a phase):** the bundled `examples/advanced` sample was found
unbuildable — five `typst_elements` keys outside the CONF-04 allowlist, and `_templates/custom.typ`
three milestones behind on its `@preview` pins (`unknown variable: kai`). Both repaired, the template
now declaring `papersize`/`fontsize`/`lang` so the sample demonstrates the allowlist, and
`test_preview_version_sync.py` extended over `examples/**/*.typ` so a bundled sample can no longer
drift unwatched.

</details>

<details>
<summary>✅ v0.6.4 — Read the Docs migration (Phases 29–33, +30.1) — SHIPPED 2026-07-28</summary>

Moved documentation hosting from GitHub Pages to Read the Docs, applying the project's own standard —
"what the docs promise is what actually happens" — to the publishing surface. Stood up the English RTD
site from `.readthedocs.yaml` with a `READTHEDOCS_LANGUAGE` → `SPHINX_LANGUAGE` → `"en"` seam in
`conf.py`, proved via the raw build log that RTD installs typsphinx from the checked-out commit, and
resolved the milestone's one open empirical unknown (Branch A: `@preview` egress from RTD's sandbox
works) so the served PDF is the one `typstpdf` produced — content-compared against the local
`tox -e docs-pdf` baseline. The Japanese site builds from a separate `typsphinx-doc-translations`
repository registered as an RTD translation project (submodule pin auto-advanced by `update-pin.yml`),
with the ja PDF's 10-NUL-byte glyph defect root-caused and fixed via a custom template's explicit
font selection. The hand-rolled multilang machinery, the orphan doc pair, and the relocated
`docs/locale/` tree were deleted (net −6,218 lines); every published URL was rewritten to
readthedocs.io behind an advisory lychee link guard proven red-then-green; and the GitHub Pages host
was irreversibly torn down only behind a freshly re-taken RTD-is-serving gate. Closed
verified_closeout on a passed milestone audit (13/13 requirements). Full phase detail, success
criteria, decisions, and evidence are preserved in
[`milestones/v0.6.4-ROADMAP.md`](milestones/v0.6.4-ROADMAP.md).

- [x] Phase 29: RTD Build Establishment (English Parent) + PDF Path Decision (6/6 plans) — completed 2026-07-26
- [x] Phase 30: Hand-Rolled Multi-Language Machinery & Orphan Removal (4/4 plans) — completed 2026-07-27
- [x] Phase 30.1: Translations Repository + Japanese RTD Site (INSERTED) (11/11 plans) — completed 2026-07-26
- [x] Phase 31: Published-URL Cutover + Repo-Wide Link Guard (5/5 plans) — completed 2026-07-27
- [x] Phase 32: GitHub Pages Teardown (IRREVERSIBLE) (3/3 plans) — completed 2026-07-28
- [x] Phase 33: v0.6.4 Release Prep (4/4 plans) — completed 2026-07-28

**Standing cost from this milestone:** every release now tags two repositories — the parent and
`typsphinx-doc-translations` (`/ja/stable/` resolves against the translations repo's own tags).

</details>

<details>
<summary>✅ v0.6.5 — inline-math separator hotfix (Phases 34–35) — SHIPPED 2026-07-29</summary>

Fixed the one reported compile-blocking defect and shipped it. A paragraph mixing prose and inline
math emitted Typst with no valid separator between the preceding text emission and the `mi(...)` /
`$...$` call, so the build died at `typst.compile()`. Phase 34 root-caused it **by measurement**
rather than from the backlog's guess — the real cause was that `visit_math` participated in only one
of the translator's three separator protocols (paragraph, code-mode concat, list-item), so the fatal
surfaced in list items, definition-list terms, and collapsed confval field bodies rather than in
plain paragraphs — and fixed it on both the mitex and native emission paths, pinned by a real
`typst.compile()` GATE-01 fixture recorded RED pre-fix. Phase 35 was prep-only. The runtime change is
confined to `typsphinx/translator.py` (+45 lines); zero new runtime dependencies and no `@preview`
version bump, both asserted mechanically over the SHA-anchored full milestone diff. Full phase
detail, success criteria, decisions, and tech-debt notes are preserved in
[`milestones/v0.6.5-ROADMAP.md`](milestones/v0.6.5-ROADMAP.md).

- [x] Phase 34: Inline Math After Text — Separator Fix (3/3 plans) — completed 2026-07-28
- [x] Phase 35: v0.6.5 Release Prep (5/5 plans) — completed 2026-07-29

**Standing cost carried forward (unchanged from v0.6.4):** every release tags two repositories — the
parent and `typsphinx-doc-translations` (`/ja/stable/` resolves against the translations repo's own
tags).

</details>

## 🚧 v0.7.0 — API rendering design overhaul (ACTIVE)

**Milestone Goal:** Replace the provisionally-chosen Typst representations of the API-description
and admonition directive families with a real typographic design, so autodoc/API pages render as a
readable reference document — monospace signatures, hanging-indented bodies, and visually
distinguishable nesting — instead of the flat wall of proportional bold text they are today. Adds
full-round-trip docutils citation support (greenfield: a citation fails the Typst compile outright
today), folds in the v0.6.5 `visit_math_block` spacing todo and the `release.yml` release-notes
rework, and closes with prep-only release work.

**Binding constraints this roadmap is built on** (settled owner decisions, not open questions):

1. **No bundled Typst style module.** The translator emits complete Typst directly, so every
   generated `.typ` stays self-contained. The shared indent constant lives on the Python side.
2. **Sphinx's LaTeX PDF is a reference, not an authority.** No success criterion below is "matches
   the reference page-by-page." The reference's measured values (the ≈22–25pt indent quantum, the
   per-node font roles, the four admonition colour buckets) are design inputs; the criteria are
   either mechanically checkable structural properties or explicit visual-UAT sign-offs, matching
   the `[M]`/`[V]` tag on each requirement.
3. **GATE-01's RED state is redefined for this milestone** (milestone invariant #4). Every prior
   fixture in this project proved a compile fatal; every design defect here **compiles successfully
   today**, so each phase defines a structural / regex / `pypdf`-text RED assertion **before** any
   code is written. **Phase 40 (citations) is the sole exception** and keeps the classic
   `TypstError` RED. Regenerating expected strings from the new code's own output is a violation of
   the invariant, not a shortcut.
4. **Test migration is owned per phase** (milestone invariant #5), never deferred to a blanket
   closing pass. Measured blast radius: 10 test files, 61 render-gate classes.
5. **Standing invariants carried forward:** zero new runtime dependencies; the `@preview` package
   count stays at four with no new version-lockstep site.

**Not a frontend UI milestone** (standing project note): every phase below is typesetting, PDF, and
CI work. `ui.plan-gate` false-positives on "layout"/"page"/"render" wording here — no phase carries
a UI hint, and `/gsd-ui-phase` is not applicable.

- [ ] **Phase 36: Shared-Emission Seam Cleanup** - Give `desc_signature` and `rubric` their own emission shape with byte-identical output, and drop `visit_math_block`'s redundant break
- [ ] **Phase 37: Signature Typography — the `desc_*` Family** - An API signature reads as a signature: monospace name and qualifier, distinguishable parameters, a real arrow, no margin overflow, no mid-signature page break
- [ ] **Phase 38: Structural Indentation + Info Fields** - Description bodies indent inside their signature, nesting accumulates so class membership is visible, and field lists follow the same single constant
- [ ] **Phase 39: Admonition Taxonomy + Rubric Nesting** - Admonitions land in the reference's four colour buckets with the generic directive styled and titled; a rubric inherits its container's indent
- [ ] **Phase 40: Citations — Full Round Trip** - A document with docutils citations compiles and renders a labelled, linked, back-referenced reference list; `examples/charged-ieee/` gets its citations back
- [ ] **Phase 41: v0.7.0 Release Automation + Release Prep** - The GitHub Release body comes from the curated CHANGELOG section, and the v0.7.0 tree is prepared and proven green with no irreversible publish

## Phase Details

### Phase 36: Shared-Emission Seam Cleanup
**Goal**: The two pre-existing emission-shape defects that would otherwise contaminate every later
phase's fixtures are settled first — `desc_signature` and `rubric` each own their open/close pair
instead of borrowing `visit_strong`'s via the dummy-node trick, and `visit_math_block` stops
stacking a redundant break on top of Phase 34's list-item separator flag. This is the milestone's
safe, provable first move: the decoupling's whole acceptance criterion is that **nothing changes
visually**, which makes it verifiable by diff rather than by judgement.
**Depends on**: Nothing (first phase of the milestone)
**Requirements**: ADM-06, MATH-02
**Success Criteria** (what must be TRUE):
  1. `desc_signature` and `rubric` each open and close through their own handler pair — a repo-wide
     grep finds no remaining dummy-node delegation to `visit_strong`/`depart_strong` from either —
     while plain `**bold**` markup still routes through `visit_strong` unchanged.
  2. The decoupling changes no rendering: for a fixture exercising signatures, sibling signatures,
     rubrics (including autodoc's "Options" rubric), and bold markup, the emitted `.typ` is
     **byte-identical** across the decoupling change alone, proven by a recorded diff of two real
     `sphinx-build -b typst` runs. This is the phase's RED-substitute — per milestone invariant #4,
     "does not compile" is unavailable, so equality-of-output is the assertion.
  3. Block math inside a list item is followed by exactly one blank line — the redundant second
     blank line between the math expression and the following `parbreak()` is gone — asserted
     structurally on the emitted `.typ`, on both the mitex and native emission paths and on both the
     plain and `:label:`-carrying forms, with the assertion recorded RED against the unfixed
     translator before the fix lands. The compiled PDF carries a companion **invariance** assertion
     rather than a RED one: measured 2026-07-30, the fix produces a byte-identical PDF (22,855
     bytes) and identical `pypdf`-extracted text, so the PDF's role here is to prove the change is
     inert, not to fail before the fix.
  4. The exact-string assertions this phase invalidates are re-derived by hand (never regenerated
     from the new output), the touched test files and render-gate classes are recorded as a census,
     and the full suite, the lint/type trio, and the full-corpus `-b typstpdf` gate are green with
     the pre-change baseline recorded alongside.
**Plans**: 4 plans

Plans:
**Wave 1**

- [ ] 36-01-PLAN.md — pre-change baselines against the untouched translator: the SC#2 combined-construct fixture, a committed golden `.typ`, the SC#1 (AST, `literal_strong`-tolerant) + SC#2 (byte-identity) gate module recorded RED/GREEN, and `36-GATE-EVIDENCE.md` with the pre-change full-suite and lint baselines

**Wave 2**

- [ ] 36-02-PLAN.md — ADM-06: `visit_desc_signature`/`depart_desc_signature` and `visit_rubric`/`depart_rubric` each get their own verbatim copy of `visit_strong`'s body (D-01/D-02/D-03), in one commit touching only `typsphinx/translator.py`, with the empty SC#2 diff recorded against two named commits (D-07)

**Wave 3**

- [ ] 36-03-PLAN.md — MATH-02: Construct H plus the two pre-fix PDF-text baselines, the SC#3 exactly-one-blank-line assertions recorded RED on both emission paths and both forms, then the one-token `visit_math_block` fix (D-06) and GREEN with a PDF text-invariance guard (D-04)

**Wave 4**

- [ ] 36-04-PLAN.md — SC#4: full suite compared by set-difference against the Plan 01 baseline, lint/type trio, milestone invariants, the full-corpus `-b typstpdf` gate, the test-migration census (invariant #5, re-measured not inherited), the deferred `par()`-loss todo routed to Phase 39 (D-02), and the phase verdict table

### Phase 37: Signature Typography — the `desc_*` Family
**Goal**: An API signature reads as a signature rather than as a run of proportional bold text —
each sub-part carries its own typographic role, the return arrow is a real glyph, a long
fully-qualified signature stays inside the text margin, and a signature is neither split by a page
break nor buried in doubled blank lines.
**Depends on**: Phase 36 (the decoupling is what lets `desc_signature` be restyled without touching
`rubric` or `**bold**`)
**Requirements**: SIG-01, SIG-02, SIG-03, SIG-04, SIG-05, SIG-06, SIG-07, SIG-08, SIG-09
**Success Criteria** (what must be TRUE):
  1. Each signature sub-part emits a distinct, asserted treatment on the emitted `.typ`: `desc_name`
     and `desc_annotation` in bold monospace, `desc_addname` in regular-weight monospace subordinate
     to the name, the parameter-list delimiters (`(`, `)`, `,`, `=`, and `desc_optional`'s brackets)
     in monospace, and `desc_parameter` (with any inline type annotation) visibly distinct from
     `desc_name`. Every one of these is a structural assertion — emitted through a monospace
     primitive rather than a bare `text(...)` — recorded RED against the pre-phase translator, whose
     output compiles fine today.
  2. `desc_returns` renders a real arrow glyph in the compiled PDF's extracted text, with no ASCII
     `->` remaining anywhere in the signature output.
  3. A long fully-qualified signature drawn from the real Sphinx `doc/` corpus stays inside the
     right text margin, measured with `pypdf` bounding boxes — with the overflow strategy derived
     from measurements of actual corpus signatures, not assumed to transfer from the v0.6.1 FID-01a
     wide-table fix.
  4. A signature positioned at a page boundary keeps its name, its parameter list, and the first
     line of its description body on the same page, proven by a fixture that pushes a signature near
     a break and a `pypdf` per-page check.
  5. Sibling signatures (overloads, alias groups, multi-option directives) and their surrounding
     blocks are separated by exactly one break — the doubled `parbreak()` runs measured on
     2026-07-29 are gone — and this phase's own exact-string blast radius is migrated within the
     phase, by hand-derived expected strings plus a recorded file/class census.
**Plans**: TBD

### Phase 38: Structural Indentation + Info Fields
**Goal**: The page shows structure. A description body sits one indent step inside its own
signature, indentation accumulates with nesting depth so a method's membership in its class is
visually recoverable, a nested member's own signature aligns with its parent's body rather than
over-indenting, and the field-list block follows the same single constant instead of a private
magic number.
**Depends on**: Phase 37 (shares the `desc_*` emission surface — the signature must own its shape
before the body wrapper is put around it)
**Requirements**: IND-01, IND-02, IND-03, IND-04, IND-05, FLD-01, FLD-02, FLD-03
**Success Criteria** (what must be TRUE):
  1. A `desc_content` body's left edge is strictly greater than its own `desc_signature`'s, measured
     from `pypdf` bounding boxes on a compiled PDF — recorded RED against the pre-phase build, where
     the two edges are equal because both `visit_desc_content` and `depart_desc_content` are `pass`.
  2. In a `py:class::` containing a `py:method::`, the method's body edge is strictly greater than
     the class's body edge, while the method's own **signature** aligns with the class body's margin
     and receives no further step — both measured on the same compiled page.
  3. Depth does not leak: a top-level `py:function::` following a three-level nest returns to the
     page margin, proven by a fixture with 3+ nesting levels plus a sibling top-level `desc`
     immediately after.
  4. One named indent constant drives desc nesting, field lists, and block quotes — a repo-wide grep
     over `typsphinx/` finds no second independent indent literal at those sites.
  5. A field list renders one step inside the surrounding description body; a multi-value field body
     renders as a bulleted list while a single-value body stays inline prose; and a parameter's name
     and type inside a field body carry monospace treatment distinct from the plain-bold field
     label — all asserted on the emitted `.typ` and the extracted PDF text, with this phase's
     exact-string blast radius migrated inside the phase by hand-derived expected strings and a
     recorded census.
**Plans**: TBD

### Phase 39: Admonition Taxonomy + Rubric Nesting
**Goal**: Admonitions carry the meaning their type implies — `seealso` grouped with the hints rather
than the notes, `attention` grouped with the dangers rather than the warnings, and a generic
`.. admonition::` styled and carrying its own title instead of falling through to the unstyled base
box — and a rubric sits at whatever indent level its container has reached rather than jumping back
to the page margin.
**Depends on**: Phase 36 (rubric must own its emission shape) and Phase 38 (a rubric can only
inherit an indent once the indent exists)
**Requirements**: ADM-01, ADM-02, ADM-03, ADM-04, ADM-05
**Success Criteria** (what must be TRUE):
  1. `seealso` renders in the same bucket as `hint`/`tip` and `attention` in the same bucket as
     `danger`/`error` — asserted on the emitted `.typ` call and confirmed in the compiled PDF, with
     the assertion recorded RED against the pre-phase mapping (which compiles fine today and simply
     picks the wrong bucket).
  2. A generic `.. admonition:: Custom Title` renders as a styled box carrying that title, asserted
     both on the emitted call and by the title text surviving into the compiled PDF's extracted
     text.
  3. A rubric inside a description body — including autodoc's "Options" heading on a real API
     page — has a left edge strictly greater than the page margin and equal to its containing body's
     edge, measured with `pypdf`.
  4. **Visual UAT (ADM-04, `[V]`):** the owner signs off, from a greyscale render of the compiled
     PDF, that the four admonition kinds remain distinguishable without hue — the distinction
     carried by icon and border rather than by the four mid-high-luminance title tints alone — with
     the render and the sign-off recorded in the phase artifacts.
  5. This phase's exact-string blast radius is migrated inside the phase by hand-derived expected
     strings plus a recorded file/class census, and the full-corpus `-b typstpdf` gate is re-run
     green after the admonition and rubric changes.
**Plans**: TBD

### Phase 40: Citations — Full Round Trip
**Goal**: A document containing docutils citations stops failing the Typst compile and instead
renders a real reference list — a labelled hanging-indent entry per citation, a working `[Label]` →
definition link, docutils' own back-references to every citing site, and document order preserved —
to the point where the citation syntax Phase 22.2 stripped out of `examples/charged-ieee/` is
restored and both samples build clean.
**Depends on**: Nothing in this milestone — citation is structurally independent of the `desc_*` and
admonition work, needs no document-order pre-pass, and is sequenced here only for convenience
**Requirements**: CIT-01, CIT-02, CIT-03, CIT-04, CIT-05, CIT-06
**Success Criteria** (what must be TRUE):
  1. A document containing a citation compiles to a valid PDF. **This phase keeps the classic
     GATE-01 RED** — the verbatim `TypstError` produced by the unfixed translator is captured and
     recorded before the fix. It is the sole requirement in the milestone where "does not compile"
     is available as the RED state.
  2. A citation definition renders as `[Label]` followed by its entry body, with continuation lines
     aligned past the label — the hanging indent measured from `pypdf` bounding boxes, not asserted
     by eye.
  3. An in-text `[Label]` reference resolves to its definition, and each definition carries
     back-references to every citing location — proven on a fixture that includes a forward
     reference (the definition placed after its first use), 2+ citations, and 2+ documents, with
     every label routed through the existing namespace/sanitize helpers so a repeated key across
     documents cannot abort the compile with a duplicate-label fatal.
  4. Citation entries appear in document order, unsorted, asserted against the compiled PDF's
     extracted text order.
  5. Both `examples/charged-ieee/` approaches carry their citation syntax again and build clean
     through `-b typstpdf`, and the new handlers are checked explicitly against all three separator
     protocols (paragraph, code-mode concat, list-item) rather than by analogy to the footnote
     handlers they superficially resemble.
**Plans**: TBD

### Phase 41: v0.7.0 Release Automation + Release Prep
**Goal**: The release surface matches the work — a reader of the GitHub Release sees the curated
CHANGELOG section rather than a ~296-line commit dump — and the v0.7.0 tree is bumped, documented,
and proven green, with every irreversible action still fenced off behind
`/gsd-complete-milestone`.
**Depends on**: Phases 36, 37, 38, 39, 40 (the CHANGELOG entry describes work those phases already
proved)
**Requirements**: REL-04, REL-05
**Success Criteria** (what must be TRUE):
  1. `release.yml` builds the release body from the `## [X.Y.Z]` section of `CHANGELOG.md` — proven
     by executing the extraction against the real file for a real version, with the `git log
     --pretty` commit dump removed rather than left as a fallback path.
  2. The version reads 0.7.0 as the sole literal in `pyproject.toml`, with `uv.lock` and `README.md`
     moved in lockstep and `typsphinx.__version__` reporting it, and a curated `## [0.7.0]`
     CHANGELOG entry is in place with the tail link block rolled over.
  3. The post-bump tree is green across the full suite, the lint/type trio, the full-corpus
     `-b typstpdf` gate, and both docs dogfooding builds — including a re-run of the `ja` build's
     four-check glyph bar, because any new font selection introduced by this milestone can shadow
     the `Noto Serif CJK JP` fallback silently, with no warning or error.
  4. The milestone invariants are proven mechanically over the SHA-anchored full milestone diff:
     zero new runtime dependencies, the `@preview` package count still four with no new
     version-lockstep site, and every node-handler change carrying its recorded-RED GATE-01 fixture.
  5. No irreversible action has been taken at phase close — local and remote `v0.7.0` tags are both
     empty — and a standalone handoff checklist records exactly what `/gsd-complete-milestone` will
     execute (merge, tag, `release.yml`, PyPI + GitHub Release, and the standing second tag on
     `typsphinx-doc-translations`).
**Plans**: TBD

## Progress

**Execution Order:**
Active milestone phases execute in numeric order (decimal insertions between their surrounding
integers), with the prep-only Release phase last so its CHANGELOG entry describes work already
proven by the preceding phases' gates. For v0.7.0: 36 → 37 → 38 → 39 → 40 → 41. Phase 40
(citations) is structurally independent and could be resequenced anywhere after Phase 36 if it
becomes convenient; Phases 37 → 38 → 39 are a genuine dependency chain.

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
| 19. Block Separation Fixes (Cluster A) | v0.6.2 | 3/3 | Complete | 2026-07-20 |
| 20. Signature Token Spacing (Cluster B) | v0.6.2 | 2/2 | Complete | 2026-07-20 |
| 21. Residual Fidelity Fixes (Clusters C/D/E/F) | v0.6.2 | 3/3 | Complete | 2026-07-20 |
| 22. typstpdf Target-Name PDF Fix (Issue #117) | v0.6.2 | 3/3 | Complete | 2026-07-21 |
| 22.1 typstpdf Compile-Root Alignment (INSERTED) | v0.6.2 | 4/4 | Complete | 2026-07-22 |
| 22.2 Dead Config-Value Sweep (INSERTED) | v0.6.2 | 6/6 | Complete | 2026-07-22 |
| 22.3 typstpdf Builder Warning Hardening (INSERTED) | v0.6.2 | 3/3 | Complete | 2026-07-22 |
| 22.4 README Claim-vs-Measured-Reality Drift Resolution (INSERTED) | v0.6.2 | 3/3 | Complete | 2026-07-23 |
| 23. v0.6.2 Release Prep + Regression-Gate Close | v0.6.2 | 3/3 | Complete | 2026-07-23 |
| 24. Delete `typst_toctree_defaults` | v0.6.3 | 1/1 | Complete    | 2026-07-23 |
| 25. Captioned Table Figure Wrap + Cross-References | v0.6.3 | 2/2 | Complete    | 2026-07-24 |
| 26. `typst_elements` papersize/fontsize Pass-Through | v0.6.3 | 2/2 | Complete    | 2026-07-24 |
| 27. Docs Measured Fidelity — Orphan Delete + Phantom Names | v0.6.3 | 1/1 | Complete    | 2026-07-24 |
| 27.1 Typst Typesetting lang Follows Sphinx `language` (INSERTED) | v0.6.3 | 3/3 | Complete    | 2026-07-25 |
| 28. v0.6.3 Release Prep + Regression-Gate Close | v0.6.3 | 3/3 | Complete    | 2026-07-25 |
| 29. RTD Build Establishment (English Parent) + PDF Path Decision | v0.6.4 | 6/6 | Complete    | 2026-07-26 |
| 30. Hand-Rolled Multi-Language Machinery & Orphan Removal | v0.6.4 | 4/4 | Complete    | 2026-07-27 |
| 30.1 Translations Repository + Japanese RTD Site (INSERTED) | v0.6.4 | 11/11 | Complete    | 2026-07-26 |
| 31. Published-URL Cutover + Repo-Wide Link Guard | v0.6.4 | 5/5 | Complete    | 2026-07-27 |
| 32. GitHub Pages Teardown (IRREVERSIBLE) | v0.6.4 | 3/3 | Complete    | 2026-07-28 |
| 33. v0.6.4 Release Prep | v0.6.4 | 4/4 | Complete    | 2026-07-28 |
| 34. Inline Math After Text — Separator Fix | v0.6.5 | 3/3 | Complete    | 2026-07-28 |
| 35. v0.6.5 Release Prep | v0.6.5 | 5/5 | Complete    | 2026-07-29 |
| 36. Shared-Emission Seam Cleanup | v0.7.0 | 0/TBD | Not started | - |
| 37. Signature Typography — the `desc_*` Family | v0.7.0 | 0/TBD | Not started | - |
| 38. Structural Indentation + Info Fields | v0.7.0 | 0/TBD | Not started | - |
| 39. Admonition Taxonomy + Rubric Nesting | v0.7.0 | 0/TBD | Not started | - |
| 40. Citations — Full Round Trip | v0.7.0 | 0/TBD | Not started | - |
| 41. v0.7.0 Release Automation + Release Prep | v0.7.0 | 0/TBD | Not started | - |

## Backlog

Candidate work not yet scoped into a milestone. Promote items with `/gsd-review-backlog`, or
pull a whole cluster into the next milestone via `/gsd-new-milestone`.
Numbered 999.x so milestone reorganization never renumbers or drops them.

New items land here as `999.x` entries. **The backlog is currently empty** — item **999.1** (inline
math after text: missing separator before `#mi()` causes a Typst error) was promoted into v0.6.5 as
Phase 34 / requirement MATH-01 and **shipped in v0.6.5** (2026-07-29). Three earlier
pending todos were promoted into v0.6.4 (Phases 29–33):
`move-documentation-hosting-to-read-the-docs`, `github-io-doc-links-404-missing-en-prefix`, and
`docs-usage-installation-orphan-class`. `add-sphinx-linkcheck-ci-job` stays **open and deferred** —
sphinx linkcheck is out of scope as Future requirement LNK-01 (it structurally cannot see
`README.md` / `pyproject.toml`, where the dead links actually live); v0.6.4 CI-05's repo-wide
real-HTTP check covers that class instead.

**Pending todos promoted into v0.7.0** (3 of the 8 open records, 2026-07-29):

- `citation-node-support-untracked` → Phase 40 (CIT-01..CIT-06)
- `visit-math-block-redundant-blank-line-in-list-items` → Phase 36 (MATH-02)
- `release-notes-body-from-changelog-section` → Phase 41 (REL-04)

**Still open and deferred** (5, see STATE.md Deferred Items): `add-sphinx-linkcheck-ci-job`
(LNK-01), `non-str-docname-typeerror-in-typstpdf-finish`,
`modernize-typing-imports-drop-up006-up035-ignore`, `derive-typst-lang-duplicated-warning-block`,
`project-md-unterminated-html-comments`.

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25), v0.6.4 (2026-07-28), v0.6.5 (2026-07-29). v0.7.0 phases added 2026-07-29. Per-milestone phase detail, success criteria, and decisions for shipped milestones live in `milestones/vX.Y-ROADMAP.md`.*
