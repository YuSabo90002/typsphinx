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
- ✅ **v0.7.0 — API rendering design overhaul** — Phases 36–42 (+40.1) (shipped 2026-08-04) → [archive](milestones/v0.7.0-ROADMAP.md)
- ✅ **v0.7.1 — bug-fix round** — Phases 43–46 (+44.1, 44.2, 45.1, 45.2) (shipped 2026-08-11) → [archive](milestones/v0.7.1-ROADMAP.md)
- ✅ **v0.8.0 — multi-master composition** — Phases 47–52 (shipped 2026-08-15) → [archive](milestones/v0.8.0-ROADMAP.md)
- 🚧 **v0.9.0 — per-document templates** — Phases 53–57 (active, started 2026-08-15)

**Active milestone: v0.9.0 — per-document templates.** Six phases (53–57, plus 54.1 inserted): the
validated `typst_document_templates` registry with the built-in `"typst"` key deferring to today's
global configuration; the one output rule — every used key's template bundle copied wholesale to
`<outdir>/_template/<key>/` — which lets four mechanisms be deleted rather than extended; the two
bundle-directory safety defects that rule surfaced; the five v0.8.0-derived defects; the
documentation rewrite; then prep-only release.

Phase numbering is **continuous across milestones** — v0.8.0 ran Phases 47–52, so v0.9.0 starts at
**Phase 53**.

## Phases

**Phase Numbering:**

- Integer phases (53, 54, …): Planned milestone work
- Decimal phases (53.1, 53.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.8.0 ran Phases 47–52, so v0.9.0 starts at **Phase 53**.

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

<details>
<summary>✅ v0.7.0 — API rendering design overhaul (Phases 36–42, incl. 40.1) — SHIPPED 2026-08-04</summary>

Replaced the provisionally-chosen Typst representations of the API-description and admonition
directive families with a real typographic design, so autodoc/API pages render as a readable
reference document — monospace signatures with hanging-indent wrapping, description bodies and field
lists indenting by nesting depth off one shared constant, and admonitions re-bucketed onto a taxonomy
that survives greyscale — instead of the flat wall of proportional bold text they were. Added
full-round-trip docutils citation support (greenfield: a citation failed the Typst compile outright
before), closed two compile-fatal defects (MATH-02's redundant list-item break and TBL-03's dropped
captioned-table target label), and built the machinery to source the GitHub Release body from the
curated CHANGELOG section. Zero new runtime dependencies; the `@preview` package count stayed at four
with no new version-lockstep site; every node-handler change carries its own recorded-RED GATE-01
fixture. **Shipped with one known gap: REL-04.** That machinery failed on its own first real tag push
(`create-release` calls `uv run` in the one release job with no `setup-uv` step); PyPI published, the
GitHub Release did not, and the v0.7.0 release was repaired by hand. `release.yml` is fixed on `main`;
REL-04 closes when a real tag push exercises it end to end — 32/33 requirements, carried to v0.7.1. Full phase detail, success criteria, decisions, and tech-debt notes are
preserved in [`milestones/v0.7.0-ROADMAP.md`](milestones/v0.7.0-ROADMAP.md).

- [x] Phase 36: Shared-Emission Seam Cleanup (4/4 plans) — completed 2026-08-01
- [x] Phase 37: Signature Typography — the `desc_*` Family (9/9 plans) — completed 2026-08-01
- [x] Phase 38: Structural Indentation + Info Fields (9/9 plans) — completed 2026-08-02
- [x] Phase 39: Admonition Taxonomy + Rubric Nesting (13/13 plans) — completed 2026-08-02
- [x] Phase 40: Citations — Full Round Trip (5/5 plans) — completed 2026-08-02
- [x] Phase 40.1: Citation Degradation Hardening (INSERTED) (4/4 plans) — completed 2026-08-02
- [x] Phase 41: v0.7.0 Release Automation + Release Prep (7/7 plans) — completed 2026-08-03
- [x] Phase 42: Captioned Table Drops Preceding Target Label (PROMOTED FROM BACKLOG) (6/6 plans) — completed 2026-08-04

**First milestone to add a requirement after completing** — Phase 42 was promoted out of backlog
item 999.2 on 2026-08-03, *after* Phase 41 had already closed, taking v0.7.0 from 7/7 to 7/8 and
`REQUIREMENTS.md` from 32 to 33 v1 requirements. The owner blocked the publish on it rather than
resequencing, so the "prep-only Release phase last" ordering is broken exactly once here.

**Standing cost carried forward (unchanged from v0.6.4):** every release tags two repositories — the
parent and `typsphinx-doc-translations` (`/ja/stable/` resolves against the translations repo's own
tags).

</details>

<details>
<summary>✅ v0.7.1 — bug-fix round (Phases 43–46, incl. 44.1, 44.2, 45.1, 45.2) — SHIPPED 2026-08-11</summary>

Closed, in one cycle, everything v0.7.0 left owed — its single unmet requirement (REL-04), the
defects its own reviews filed, and the first-run onboarding break. A maintenance round over
already-diagnosed defects, not a feature cycle: `typst_documents` gained a LaTeX-shaped default so
following the Quick Start produces a PDF, an explicit entry's title and author reached the rendered
document, nested tables and figures stopped corrupting the enclosing structure, and the published
custom-template parameter contract was made to agree with the code both ways. Full phase detail,
success criteria, decisions, and tech-debt notes are preserved in
[`milestones/v0.7.1-ROADMAP.md`](milestones/v0.7.1-ROADMAP.md).

- [x] Phase 43: Table State Correctness — Nested Tables + Empty-Title Anchors (6/6 plans) — completed 2026-08-04
- [x] Phase 44: `typst_documents` Default Derivation + Builder Input Hardening (5/5 plans) — completed 2026-08-04
- [x] Phase 44.1: Relative Heading Depth for Toctree Nesting (INSERTED) (3/3 plans) — completed 2026-08-05
- [x] Phase 44.2: `typst_documents` Title and Author Consumption (INSERTED) (6/6 plans) — completed 2026-08-07
- [x] Phase 45: Documentation Currency + Carried Hygiene (4/4 plans) — completed 2026-08-10
- [x] Phase 45.1: Custom-Template Parameter Contract Correction (INSERTED) (7/7 plans) — completed 2026-08-10
- [x] Phase 45.2: Local Toolchain Repair — tox-uv to tox-uv-bare (INSERTED) (6/6 plans) — completed 2026-08-11
- [x] Phase 46: v0.7.1 Release Prep (prep-only) (6/6 plans) — completed 2026-08-11

**Milestone invariant #5 held (new this milestone).** The milestone branch was pushed to `origin` in
Phase 43, not at the release PR — Phase 43's SC#5. Both defects that surfaced at the v0.7.0 close
shared the cause that the branch was never pushed until the release PR, so neither Windows CI nor a
real tag push ran against it during eight phases. This milestone's Windows-only claim-page defect
was consequently caught in Phase 46 by a dispatched CI run rather than at the release PR.

**REL-04 closed at the publish, not in a phase** — as the roadmap's binding constraint #2 required.
Phase 46 owned only its in-phase share; the acceptance evidence was generated by the real tag push
at `/gsd-complete-milestone` (release run `31462027486`, `create-release` success, Release body
measured byte-identical to the extractor's output).

**Standing cost carried forward (unchanged since v0.6.4):** every release tags two repositories —
the parent and `typsphinx-doc-translations`.

</details>

<details>
<summary>✅ v0.8.0 — multi-master composition (Phases 47–52) — SHIPPED 2026-08-15</summary>

Made multi-master composition actually work: a `typst_documents` configuration declaring more than
one master now produces a complete PDF for each of them. The unit of composition moved from "one
`.typ` shared by every master, with the include decision baked in at write time" to "per-master
wrapper files publishing their include edge set as Typst `state`, plus template-less docname-named
content files emitting state-guarded includes at the toctree's own position" — one re-shaping that
cut the root all three known multi-master defects grew from (B-1, B-2, and defect A). Full phase
detail, success criteria, decisions, and tech-debt notes are preserved in
[`milestones/v0.8.0-ROADMAP.md`](milestones/v0.8.0-ROADMAP.md).

- [x] Phase 47: Two-Layer Output — Content/Wrapper Split, Target-as-Path, Collision Detection (14/14 plans) — completed 2026-08-12
- [x] Phase 48: Compile-Time Cross-Reference Guard (7/7 plans) — completed 2026-08-14
- [x] Phase 49: Per-Master Include Graph with State-Guarded Includes (6/6 plans) — completed 2026-08-14
- [x] Phase 50: PR #131 Image Path Defects (3/3 plans) — completed 2026-08-14
- [x] Phase 51: Two-Layer Output Documentation (6/6 plans) — completed 2026-08-15
- [x] Phase 52: v0.8.0 Release Prep (prep-only) (9/9 plans) — completed 2026-08-15

**Binding constraint #1 held, and it was the milestone's one hard ordering constraint.** Phase 48's
compile-time cross-reference guard landed *before* Phase 49's include graph, because the graph is
what turns a silently-omitted document into a reachable-and-absent label — shipping the graph first
would have shipped a fatal-abort regression in between. No requirement forced this order; the
roadmap did.

**First milestone since v0.6.4 to ship with a zero-`typsphinx/`-change release phase, and it held
under pressure.** Four defects surfaced mid-phase from CI dispatch and all four were fixed
test-side, in two plans added on owner authorization, so `git diff --name-only -- typsphinx/` stayed
empty across the entire release phase.

**Milestone invariant #5 paid for the second consecutive milestone, four times over.** Phase 52's CI
history is three runs, not one — RED (8 of 12 jobs) → 11/12 → GREEN 12/12. Two of the four defects
were findable locally and nobody had run the command: a test comparing against hardcoded Japanese
Sphinx warning text (reproduces in 4 seconds under `LC_ALL=C`), and an `I001` unsorted import block
that survived because `ruff` has been unrunnable on this machine since Phase 45.2 (QUA-06).

**Four minor defects ship unfixed by owner decision D-01**, all new failure classes created by
features this milestone shipped, kept to internal disclosure only by D-03 (no `### Known
Limitations` CHANGELOG section, no GitHub issue, no backlog item) — the complete record is
`52-HANDOFF.md` § "Deferred by decision, not oversight" plus `.planning/todos/pending/`.

**Standing cost carried forward (unchanged since v0.6.4):** every release tags two repositories —
the parent and `typsphinx-doc-translations`. This close dispatched that repository's own
`update-pin.yml` rather than advancing the pin by hand.

</details>

## 🚧 v0.9.0 — per-document templates (ACTIVE)

**Milestone Goal:** every `typst_documents` entry can use its own template, Typst Universe package,
and template-function arguments — instead of one globally-configured template being applied to every
master. v0.8.0 made multi-master composition produce a complete PDF per master; every one of those
PDFs is still typeset by the same template, because template resolution is read entirely from global
config at `writer.py:324-351` and `builder.py:1124-1168` and never consults the entry. The entry is
already in hand at the exact point the template is chosen — what is missing is a per-entry way to
name a template and the ability to emit more than one template file.

**The shape is one registry plus one output rule.** `typst_document_templates` is a dict of named
definitions, each carrying `template` **xor** `package` plus an optional `template_function`;
`typst_documents` element [4] — the slot every config in this repository already fills with the
literal `"typst"`, and which `configuration.rst:80` currently defines as *"accepted and ignored"* —
becomes the registry key. Every used key's bundle (the resolved template's parent directory) is
copied wholesale to `<outdir>/_template/<key>/`, with `"typst"` handled by the same rule and not
special-cased. Unifying the route is what makes `_write_template_file()`, `_copy_template_directory()`'s
`.typ` exclusion, `copy_template_assets()`'s three early returns, and `typst_template_assets` itself
collapse into **deletions rather than additions**.

**Binding constraints this roadmap is built on** (settled decisions and standing invariants, not open
questions):

1. **`_template/` is reserved WHOLESALE, and the reservation costs an existing fixture.** A source
   tree that would write output under `_template/` is an `ExtensionError` (OUT-07), not a narrower
   exact-name claim on `_template.typ`. `tests/fixtures/template_named_dir_master/` has docnames
   `_template/index` and `_template/sub/index` and its own `conf.py` documents that layout as
   realistic — so **Phase 54 must move or rename it and decide what replaces its regression intent**
   (two entries against one docname tree, CR-01/G-22.1-4 coverage). This is an owner decision already
   taken; do not re-open it as "choose a different reserved directory name".

2. **The tree must be green at every phase boundary, and deleting `_write_template_file()` breaks 31
   test files** (grep-counted, listed in `research/ARCHITECTURE.md` §4). The additive → behaviour-
   preserving → layout-change → deletion sequence is why Phase 53 exists as a separate phase from
   Phase 54: "the plumbing exists", "the plumbing is used with output unchanged", "the output layout
   changes", and "the old mechanism is deleted" are four independently verifiable states, and
   collapsing them produces one multi-hundred-line commit that breaks 31 files with no intermediate
   green.

3. **`typst_template_assets`'s removal ships with its own detection, in the same commit.** Sphinx
   never surfaces an unregistered `conf.py` name, so the removal is otherwise permanently silent and
   the detection cannot be retrofitted later. CONF-19's `config-inited` handler also covers the two
   previously-removed values (`typst_authors`, `typst_toctree_defaults`). **This is this codebase's
   first use of `config-inited`** — every existing config-shape error is raised from inside a
   `Builder` method, so the handler is a new integration point, not a copy of an existing one.

4. **The bundle copy runs in `finish()`, fed by a write-time accumulator of used registry keys**,
   mirroring the existing `self.images` pattern. Nothing in the write phase reads template bytes —
   `render_wrapper()` computes only an import-path *string*, and Typst reads the bytes at compile
   time, later than the asset copy. `TemplateEngine.resolve_template()` currently discards the
   resolved file PATH and must be widened to return it, because the copy needs the parent directory.

5. **Registry keys are single path segments, and the existing guards are the WRONG contract.**
   `_escapes_outdir()`/`_is_drive_qualified()` were built for whole relative paths, where a `/` is
   legal — the opposite of what one segment needs. CONF-18 needs a narrower predicate, and its
   detection logic must be testable as platform-independent string-shape assertions: the 3-OS CI
   matrix (`ci.yml:17` — ubuntu/windows/macos) can reach the filesystem-level cases, but a local
   Linux run cannot, and this project's own D-05 precedent already validates Windows-shaped input on
   POSIX.

6. **Standing GATE-01 bar (since v0.6.0):** every node-handler or config→output change ships a real
   `sphinx-build → typst.compile()` regression fixture, recorded **RED against the unfixed code**
   before it is accepted as green. Several requirements here are "compiles fine, produces wrong
   output" shapes (TPL-03's zero-edit equivalence, XREF-05's decoy link, IMG-03's key collision) —
   each of those must have its RED assertion written down *before* implementation starts, per
   v0.7.0's amendment. Naming "GATE-01 fixture" as a checkbox without naming the pre-fix RED
   assertion does not satisfy this.

7. **Relocating the template changes Typst's file-relative resolution** for `#image()`,
   `#bibliography()` and `read()`. This repository's three real templates were measured to have ZERO
   path-relative references (fonts by family name only), so the known blast radius is genuinely zero
   — but that also means **no existing fixture proves the USER-template case survives the move**, and
   the built-in template cannot stand in for it. OUT-05 needs a new real-compile fixture whose user
   template contains a path-relative asset reference.

8. **`pyproject.toml:73` declares `"typsphinx" = ["templates/*.typ"]`.** The editable install this
   project develops and CI-tests against masks the gap entirely, so BLD-05 requires widening the glob
   **and** a built-wheel content check — inspection of the glob is not evidence.

9. **Push the milestone branch to `origin` from the FIRST phase, not at the release PR** (milestone
   invariant #5, adopted v0.7.1, paid four times over in v0.8.0). The milestone branch is
   `gsd/v0.9.0-per-document-templates` — the branch that actually carries this milestone's commits,
   named the same way v0.8.0's was (`gsd/v0.8.0-multi-master-composition`). It is **not** on
   `origin`. (Corrected 2026-08-15 during Phase 53 planning: this constraint originally named
   `gsd/v0.9.0-milestone`, a local branch measured to sit at the merge-base `aed773c9` with zero
   milestone commits. That stale branch is not the milestone branch.) Phase 53 carries this as SC#5;
   every later phase inherits it as a standing expectation.

10. **The final phase (57) is prep-only and takes zero irreversible action.** Version bump, curated
    CHANGELOG entry, evidence gathering, handoff checklist. No tag, no publish, no GitHub Release.
    **REL-08 closes at `/gsd-complete-milestone`, not in the phase** — and the `phase.complete`
    auto-flip has fired against the release-prep requirement four consecutive times, so Phase 57
    records a `REQUIREMENTS.md` checksum to catch and revert it.

11. **Standing invariants carried forward:** zero new runtime dependencies (`shutil`, `re`,
    `importlib.resources` are stdlib and this project's floor is 3.12); the `@preview` package count
    stays at **four** with no new version-lockstep site (`writer.py` / `template_engine.py` /
    `templates/base.typ` plus `examples/**/*.typ`); typing-import modernization is forbidden
    (`CLAUDE.md` independently instructs it); every phase closes green on the full pytest suite plus
    `black` / `ruff` / `mypy`; and "anywhere under X" success criteria are checked by a repo-wide grep
    at discovery time, never against the files a requirement happens to name (milestone invariant #4).

**Two open decisions from `research/SUMMARY.md` are already closed** and must not be re-litigated
during planning: the `_template/` prefix-vs-fixture collision (constraint #1) and whether the
`typst_template_assets` removal ships a warning (constraint #3). `research/SUMMARY.md`'s suggested
seven-phase structure was written before both were settled; its **sequence** is adopted, its phase
count is not — steps 3–5 (layout, test migration, deletion) are one phase here because they are one
green boundary, and step 6 (config cleanup) rides with them because Pitfall 5 requires the detection
handler in the identical commit as the removal.

**Not a frontend UI milestone** (standing project note): every phase below is builder, writer,
template-engine, packaging, documentation and release work. `ui.plan-gate` false-positives on words
this milestone cannot avoid — "template", "layout", "render", "page", "assets". Each phase detail
therefore carries an explicit `**UI hint**: no` line, the authoritative override `ui-safety-gate.cjs`
reads, rather than relying on a per-run `--skip-ui`.

- [x] **Phase 53: Template Registry Foundation** - A `conf.py` can declare named template definitions and every malformed registry stops the build by name, while the built-in `"typst"` key defers to today's global configuration so an untouched `conf.py` produces byte-identical output (completed 2026-08-15)
- [x] **Phase 54: One Bundle Rule — `_template/<key>/`, Per-Document Selection, Four Deletions** - Element [4] actually selects the template, every used key's bundle is copied wholesale to `<outdir>/_template/<key>/` with `"typst"` under the same rule, template-relative asset references start working, and `_write_template_file()` / `typst_template_assets` / the two explicit-asset helpers are gone (completed 2026-08-16)
- [ ] **Phase 54.1: Bundle Directory Safety — `templates_path` Collision Refusal and Pre-Write Path Validation (INSERTED)** - Close the two Phase 54 `/gsd-code-review` findings: the wholesale bundle copy can republish a project's Sphinx `templates_path` Jinja directory into public build output while the published docs actively recommend that layout (WR-01), and a CONF-17 violation on the built-in `"typst"` key is discovered only at `finish()`, after every content and wrapper `.typ` file has already been written (CR-01)
- [ ] **Phase 55: v0.8.0-Derived Defects** - The five defects v0.8.0 shipped unfixed by decision D-01, or fixed only test-side, are closed on the product side with a RED-recorded reproduction each
- [ ] **Phase 56: Per-Document Template Documentation** - The published documentation describes the registry that shipped: element [4] is the registry key, the asset examples work under the bundle layout, and the removed config values have migration guidance
- [ ] **Phase 57: v0.9.0 Release Prep (prep-only)** - The v0.9.0 tree is bumped, its CHANGELOG curated around the two breaking changes, proven green on live multi-template evidence, and handed off with no irreversible action taken

## Phase Details

### Phase 53: Template Registry Foundation

**Goal**: `typst_document_templates` exists as a validated, resolved-once-per-build data structure,
and `render_wrapper()` builds its `TemplateEngine` from the resolved definition instead of reading
`typst_template` / `typst_package` / `typst_template_function` straight off `config` — but the
built-in `"typst"` key synthesizes exactly those same global values, so **this phase changes no
output**. That is the point: it separates "does the registry plumbing work" from "does the output
layout change" (Phase 54) into two independently verifiable states, which is what keeps the tree
green while 32 test files still assert the old `_template.typ` path.

Resolution belongs **once per build in `write()`**, immediately after `_validate_output_path_collisions()`
and before `prepare_writing()` — mirroring `self._master_include_edges = self._build_include_edge_map()`,
which is the same "derive once, thread into the per-docname loop" pattern. Per-wrapper resolution
would repeat the validation work and, worse, make an `ExtensionError` for a bad registry entry
surface only when the first wrapper naming it happens to be written, so failure would be order-
dependent across a multi-master build.

`typst_template_mapping` stays global and untouched — `writer.py:348`'s `getattr(config,
"typst_template_mapping", None)` is the one field that does **not** move into the registry. Its
retirement is Future requirement TPL-06, and warning about it now would change behaviour for a value
this milestone does not touch.

**Depends on**: Nothing (first phase of the milestone)
**Requirements**: TPL-01, TPL-03, TPL-04, TPL-05, CONF-14, CONF-15, CONF-16, CONF-17, CONF-18
**Success Criteria** (what must be TRUE):

  1. **Named template definitions are declarable and resolve once per build.** A `conf.py` declaring
     `typst_document_templates` entries carrying `template` **xor** `package`, plus an optional
     `template_function` in either its `str` or its `{"name", "params"}` form, is accepted and
     resolved into a single per-build registry; a `typst_documents` whose entries name the **same**
     key resolves both to the one definition, with the existing `params`-exclusivity rule intact
     (TPL-01, TPL-05). Declaring `"params"` still selects the exclusive parameter set and omitting it
     still selects the auto-derived one — no new predicate is introduced for either.

  2. **An untouched `conf.py` produces byte-identical output, proven by identity rather than by
     inspection.** Real before/after `sphinx-build` runs at named commits show byte-identical `.typ`
     files and equal-page-count PDFs across the four existing shapes — `typst_template` set,
     `typst_package` set, `typst_template_function` set, and nothing set (bundled `base.typ`) — and a
     four-element `typst_documents` tuple produces output byte-identical to the same tuple with a
     fifth element of `"typst"` (TPL-03, TPL-04). The RED for this criterion is a recorded pre-change
     baseline, not a compile failure.

  3. **Every malformed registry stops the build with a message naming the specific reason.** An
     unregistered key referenced by an entry (the error names the registered keys), a definition
     carrying both `template` and `package`, a user-defined `"typst"` key, and a `template` pointing
     at a file directly under `srcdir` (no bundle directory to copy) each raise `ExtensionError`
     (CONF-14, CONF-15, CONF-16, CONF-17). Each fires **once per build and order-independently** —
     a multi-master config with a bad entry fails the same way regardless of which wrapper would have
     been written first — following `_validate_output_path_collisions()`'s "runs once, at the very
     top of `write()`" precedent.

  4. **Registry-key shape is validated as a single path segment, and the wrong guard is not reused.**
     Empty or whitespace-only, `.`/`..`, containing `/` or `\`, a Windows reserved device name
     (case-folded, with or without a trailing extension), a trailing dot or space, and a key
     differing from another registered key only by case each stop the build (CONF-18). Every one of
     these is asserted as a **platform-independent string-shape test** that passes on Linux CI, and
     the case-collision check runs through the same casefold comparison `_collision_key()` already
     uses rather than a second independently-written check that can drift. The phase's artifacts
     record explicitly **why `_escapes_outdir()`/`_is_drive_qualified()` are not reused** — their
     documented contract permits a `/`, which is the opposite of a single segment's contract.

  5. **The milestone branch is on `origin` with a completed 3-OS CI run.**
     `gsd/v0.9.0-per-document-templates` is pushed to `origin` **in this phase**, evidenced by a
     `git ls-remote --heads origin` hit plus at least one completed CI run over it including the
     `windows-latest` and `macos-latest` lanes (milestone invariant #5, binding constraint #9).
     The run is produced by **`workflow_dispatch`**, not by the push: `.github/workflows/ci.yml:3-8`
     scopes its `push`/`pull_request` triggers to `main`/`develop` only, so a feature-branch push
     alone runs no CI (measured — the `push` events on v0.8.0's milestone branch were the Link Check
     workflow; every completed `CI` run over that branch was `workflow_dispatch`). Sequence:
     `git push origin <branch>` → `gh workflow run CI --ref <branch>` → poll `gh run list --branch
     <branch>` → capture `gh run view <run-id> --json jobs`. This milestone raises the stakes again:
     CONF-18's reserved-device-name and case-collision failures are structurally invisible to a local
     Linux-only run.

     *(Branch name corrected 2026-08-15 during Phase 53 planning — see binding constraint #9. The
     original text named `gsd/v0.9.0-milestone`, which carries zero milestone commits.)*

**Plans**: 10/10 plans executed (8 waves) — 7/7 executed through Wave 6. 53-06/53-07 added 2026-08-15 by
`/gsd-plan-phase 53 --gaps` to close `53-VERIFICATION.md`'s SC#3 gap plus the two ⚠ WARNING robustness
defects the owner opted in to; 53-08…53-10 added 2026-08-15 by a second `--gaps` round to close the
re-verification's one scored gap (SC#5, stale CI evidence), the two new ⚠ WARNING crash paths
`53-REVIEW.md` found in `template_registry.py`, and `.planning/REQUIREMENTS.md`'s stale TPL-01/TPL-05/
CONF-16 tracking. `53-REVIEW.md` IN-01 was reviewed and declined by the owner and is deliberately
unplanned

**Wave 1**

- [x] 53-01-PLAN.md — SC#2 pre-change byte-identity baseline (`53-RED-EVIDENCE.md`) — wave 1

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 53-02-PLAN.md — Tracer: `typst_document_templates` registered, `template_registry.py`, resolution threaded from `write()` into `render_wrapper()`, output unchanged — wave 2

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 53-03-PLAN.md — Validation: CONF-14…CONF-18, denylist enumeration, accumulate-then-raise-once — wave 3
- [x] 53-04-PLAN.md — `TemplateResolution` widened to carry the resolved path through the single priority walk — wave 3

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 53-05-PLAN.md — SC#2 post-change identity diff + SC#5 branch push and dispatched 3-OS CI run — wave 4

**Wave 5** *(gap closure — blocked on Wave 4 completion)*

- [x] 53-06-PLAN.md — SC#3 gap: validate every `typst_documents` entry's registry key up front in `write()`, so a CONF-14 failure leaves ZERO `.typ` files in both master orders — wave 5

**Wave 6** *(gap closure — blocked on Wave 5 completion)*

- [x] 53-07-PLAN.md — Registry robustness: cross-drive `commonpath` crash (CR-02) and raw `AttributeError` on non-`str` keys / non-`dict` definitions (WR-02/WR-03) become clean accumulated `ExtensionError`s — wave 6

**Wave 7** *(second gap-closure round — blocked on Wave 6 completion)*

- [x] 53-08-PLAN.md — Registry robustness, one level up and one field deeper: a truthy non-`dict` `typst_document_templates` container (WR-01) and a truthy unusable `template` field (WR-02) become this module's own `ExtensionError` instead of a raw `AttributeError`/`TypeError` — wave 7
- [x] 53-09-PLAN.md — `.planning/REQUIREMENTS.md` tracking correction: TPL-01, TPL-05 and CONF-16 marked delivered in BOTH the checkbox list and the traceability table, six lines, no code — wave 7

**Wave 8** *(second gap-closure round — blocked on Wave 7 completion)*

- [x] 53-10-PLAN.md — SC#5 re-closure: push the re-measured milestone-branch tip, dispatch a fresh 3-OS CI run over it, and record evidence carrying a `git log <ci_head>..<tip> -- typsphinx/ tests/` staleness assertion plus a positive content proof of what the certified SHA carries — wave 8

**UI hint**: no

### Phase 54: One Bundle Rule — `_template/<key>/`, Per-Document Selection, Four Deletions

**Goal**: The output layout changes to one rule with no exceptions — **every used key's template
bundle, the resolved template's parent directory, is copied wholesale to `<outdir>/_template/<key>/`**
— and element [4] therefore actually selects which template typesets which document. Because the
bundle copy carries the template verbatim (`resolve_template()` reads the file with no substitution),
four mechanisms are **deleted rather than extended**: `_write_template_file()` entirely,
`_copy_template_directory()`'s `.typ` exclusion (it existed only to avoid double-writing),
`copy_template_assets()`'s three early returns ("has no bundle" becomes a per-key property), and
`typst_template_assets` with `_copy_explicit_assets()`/`_copy_single_asset()`.

This is the phase that pays binding constraints #1, #2, #7 and #8 simultaneously. The 32 test files
asserting the root `_template.typ` migrate here; the `template_named_dir_master` fixture moves here;
the user-template asset fixture is created here; the wheel-content check is added here. The copy is
driven from `finish()` by a write-time accumulator of used keys, because incremental builds pass a
subset of docnames to `write()` and only entries whose docname is in that set produce a wrapper — the
needed key set is not known until the write loop has run.

**Depends on**: Phase 53
**Requirements**: TPL-02, CONF-19, OUT-04, OUT-05, OUT-06, OUT-07, BLD-05, BLD-06
**Success Criteria** (what must be TRUE):

  1. **Two masters, two templates, one build — and the import path does not depend on nesting
     depth.** A single `sphinx-build -b typstpdf` over a `typst_documents` whose two entries name two
     different registry keys produces two PDFs typeset by two visibly different templates (TPL-02).
     A root master and a nested master (`guide/index` → `manuals/guide.typ`) that name the **same**
     key emit the **identical** import string for it, because the path resolves against the Typst
     project root — which `pdf.py:143` / `builder.py:1545` already fix at `root=self.outdir` for every
     compile call — rather than by counting `../` (OUT-06).

  2. **Every used key's bundle sits at `<outdir>/_template/<key>/`, with `"typst"` under the same
     rule.** The bundled default lands at `_template/typst/base.typ`; a global `typst_template` lands
     at `_template/typst/<its own filename>`; a `package`-only key copies nothing; an unused key
     copies nothing (OUT-04). No `_template.typ` is written anywhere in the output tree, and
     `_write_template_file()` no longer exists — both verified by repo-wide grep over the tracked
     tree rather than by reading `builder.py`. The `"typst"` bundle resolves through
     `importlib.resources`, not `Path(__file__).parent`.

  3. **A user template's own `#image("logo.png")` compiles, and the copy publishes nothing it
     shouldn't.** A new real-compile fixture whose **user-supplied** template references a
     same-directory asset by relative path builds and compiles green through `typst.compile()`,
     recorded RED against the pre-relocation tree (OUT-05) — the built-in template, which has zero
     path-relative references by measurement, is not accepted as evidence for this. The copy excludes
     VCS and OS metadata (`.git`, `.DS_Store`, `Thumbs.db`, editor backups), asserted by a
     **manifest-diff** test ("no file I didn't expect is present"), not a presence-only test, and the
     re-run/staleness policy for an existing destination bundle is a recorded decision rather than an
     inherited `dirs_exist_ok=True` default (BLD-06). The symlink-refusal clause originally paired
     with this criterion was retracted by owner decision D-03 at Phase 54 planning.

  4. **The built wheel carries the bundle — the editable install is not evidence.**
     `pyproject.toml`'s package-data declaration covers every file kind present in
     `typsphinx/templates/`, and a CI step builds the actual wheel and asserts a non-`.typ` file
     belonging to the `"typst"` bundle is present inside it (BLD-05). The check fails if the glob is
     narrowed again later.

  5. **`_template/` is reserved wholesale, and the removed config values announce themselves.** A
     source tree that would write any output under `_template/` stops the build with an
     `ExtensionError` naming the offending docname; `tests/fixtures/template_named_dir_master/` is
     relocated and the phase records what carries its regression intent forward — two entries against
     one docname tree — under the new name (OUT-07). `typst_template_assets` is unregistered, and a
     `config-inited` handler — this codebase's first — warns by name when a `conf.py` still sets it,
     `typst_authors`, or `typst_toctree_defaults`, naming the replacement and stating the observable
     consequence rather than only that the value "was removed" (CONF-19). The handler ships in the
     same commit as the removal; detection cannot be retrofitted later.

**Plans**: 7/7 plans executed (4 waves)

Plans:
**Wave 1**

- [x] 54-01-PLAN.md — Wave 1: the three real-compile gates (OUT-05 user-template asset, TPL-02/OUT-06 two-key selection, BLD-06/OUT-04 manifest diff), each recorded RED against the pre-relocation tree
- [x] 54-02-PLAN.md — Wave 1: BLD-05 packaging — the bundle's non-`.typ` canary, a recursive package-data glob, and a CI step that opens the built wheel
- [x] 54-03-PLAN.md — Wave 1: contract amendments — D-03's symlink retraction in REQUIREMENTS.md and SC#3, plus D-14's relocated shadow route in the docs and changelog

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 54-04-PLAN.md — Wave 2 (tracer): every used key's bundle at `<outdir>/_template/<key>/`, root-absolute import, `importlib.resources` resolution, shadow route moved to `<srcdir>/_typst/`, import-string migration

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 54-05-PLAN.md — Wave 3: the four deletions and the output-tree assertion migration

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 54-06-PLAN.md — Wave 4: CONF-19's `config-inited` handler shipping with the `typst_template_assets` unregistration, plus D-15's relocation warning
- [x] 54-07-PLAN.md — Wave 4: OUT-07's `_template/` prefix reservation and the `template_named_dir_master` fixture split

**UI hint**: no

### Phase 54.1: Bundle Directory Safety — templates_path Collision Refusal and Pre-Write Path Validation (INSERTED)

**Goal**: The two findings Phase 54's `/gsd-code-review` raised are closed. Phase 54 made the
resolved template's **parent directory** the unit of copying, which turned a pre-existing
documentation choice into a live hazard: `templates.rst` and `configuration.rst` recommend
`typst_template = "_templates/custom.typ"`, and `_templates/` is exactly the directory name
Sphinx's own `templates_path` defaults to — so a project following the published documentation has
its Jinja override directory copied wholesale into public build output. That directly violates
Phase 54's own stated prohibition ("A user's Sphinx source tree must never be republished as build
output", `54-01-PLAN.md`). The extension currently reads `templates_path` nowhere: the only mention
in the tree is the comment at `template_engine.py:36` explaining why `_typst/` was chosen over
`_templates/` — the collision was known and left undefended. Separately, the built-in `"typst"`
key's CONF-17 validation is the one path that never runs before `write()`, so a one-line config
mistake writes a full, broken output tree and only then fails.

Both are defects in what Phase 54 shipped, in the same `builder.py` bundle-copy surface, which is
why they are one inserted phase rather than two, and why it sits immediately after 54 rather than
after Phase 55 (translator/registry-independent work that only queues behind 54 for file
contention). It must land before Phase 56, which documents the settled layout.

**Depends on**: Phase 54
**Requirements**: WR-01, CR-01
**Success Criteria** (what must be TRUE):

  1. **A bundle that would republish the Sphinx template directory does not silently ship.** When a
     used key's resolved bundle directory is, contains, or is contained by any entry of Sphinx's
     `templates_path`, the build says so by name rather than copying it — the exact refusal-vs-warning
     shape is **open going in** and is decided at `/gsd-discuss-phase 54.1`. Whichever is chosen, the
     detection is new code: `templates_path` is read nowhere in `typsphinx/` today (WR-01).

  2. **The published documentation stops recommending the colliding layout.** No page under
     `docs/source/` instructs a user to put a Typst template in `_templates/` — verified by a
     repo-wide grep at discovery time, not only in the two pages this review named. The replacement
     guidance matches what this repository's own `docs/source/conf.py:96` already does
     (`_typst/custom_template.typ`), so the project's documentation and its own configuration agree
     (WR-01).

  3. **A CONF-17 violation costs zero written files.** A global `typst_template` naming a bare
     filename at the source root stops the build with **no** `.typ` file on disk — the A-01/CONF-17
     guard runs in the same pre-write position as `_validate_output_path_collisions()` and
     `_validate_registry_key_references()`, and is pinned by a test of the same shape as
     `test_template_prefix_reservation_gate.py::test_no_typ_file_written_after_refusal`, which is the
     sibling property that already has one (CR-01).

  4. **The reserved-key case collision is caught in the same pass.** A declared key differing from
     the reserved `"typst"` key only by case (e.g. `"Typst"`) — which CONF-18 does not catch, because
     it compares declared keys only against each other and never against the synthesized key — is
     detected before any file is written, not at `finish()` (CR-01).

  5. Each fix is pinned by a test that **fails against the pre-fix tree**, recorded RED before
     implementation (binding constraint #6). Zero new runtime deps, no `@preview` bump, the 3-way
     version-sync surface untouched. Any user-visible behaviour change is carried into the v0.9.0
     CHANGELOG that Phase 57 curates.

Source of record: `CR-01` and `WR-01` in
[`phases/54-one-bundle-rule-template-key-per-document-selection-four-del/54-REVIEW.md`](phases/54-one-bundle-rule-template-key-per-document-selection-four-del/54-REVIEW.md).
The same review's `WR-02` (CHANGELOG coverage of the `typst_template_assets` removal and the
curated-list→wholesale-copy change) belongs to Phase 57's CHANGELOG curation; `WR-03` (a declared
key with neither `template` nor `package` shares the reserved key's shadow search path), `WR-04`
and `IN-01` are **not** in this phase's scope.

**UI hint**: no

**Plans:** 5 plans

Plans:

- [ ] 54.1-01-PLAN.md — WR-01 tracer: pre-write `templates_path` collision refusal, end to end (RED recorded first)
- [ ] 54.1-02-PLAN.md — WR-01 docs half: retire the `_templates/` recommendation across `docs/source/`, `README.md` and `examples/`, pinned by an executable repo-wide-grep gate
- [ ] 54.1-03-PLAN.md — CR-01: hoist the A-01/CONF-17 check into the pre-write pass and refuse a reserved-key case collision
- [ ] 54.1-04-PLAN.md — WR-01 expansion: all three D-02 path relations, the three measured non-colliding shapes, and D-03's aggregated sorted raise
- [ ] 54.1-05-PLAN.md — cross-kind aggregation, the v0.9.0 `Unreleased` breaking-change entry, and the phase-boundary green evidence

### Phase 55: v0.8.0-Derived Defects

**Goal**: The four minor defects v0.8.0 shipped unfixed by owner decision D-01 — all new failure
classes created by features that milestone shipped — plus the fifth whose product side is still open
after plan 52-09 fixed only the test, are closed on the **product** side, each with its own
RED-recorded reproduction. Every one of these is a "compiles fine, produces wrong output" or "wrong
exception type" shape, so binding constraint #6's amended RED applies to all five: the pre-fix
assertion is written down before implementation starts.

This phase is independent of Phases 53–54 by subject matter (translator label emission, include-edge
key escaping, recursion bounding, image URI classification) and is sequenced after them only because
they concentrate their changes in the same two files, `builder.py` and `writer.py`. It carries no
dependency on the registry.

**Depends on**: Phase 54 (file-contention sequencing only — no functional dependency)
**Requirements**: XREF-05, BLD-07, BLD-08, BLD-09, IMG-03
**Success Criteria** (what must be TRUE):

  1. **A label collision no longer links to a decoy.** With two docnames that sanitize to the same
     label string (the shipped example: `a/b` and `a_u2f_b`), a reference to the document **absent**
     from the compiling master degrades to plain text instead of linking to the other document —
     proven on a real two-master compile with the pre-fix link-to-decoy behaviour recorded first
     (XREF-05).

  2. **Include-edge keys cannot collide through their own separators.** `make_include_edge_key`
     escapes `#` and `>`, so two distinct edges whose docnames contain those characters produce
     distinct keys and the correct document is included in each master (BLD-07).

  3. **A too-deep include chain fails by name.** An include chain deeper than Python's recursion
     limit raises a named `ExtensionError` identifying the depth or cycle, not a raw `RecursionError`
     escaping through Sphinx's traceback (BLD-08).

  4. **A driveless-absolute Windows image URI is classified like its sibling.** `builder.py:910`'s
     bare `path.isabs()` is routed onto the same `posixpath.isabs(…) or _is_drive_qualified(…)`
     predicate its sibling call site already uses, so such a URI reaches the rehome/relocate/warn
     branch on Python 3.13 (BLD-09). The fix is on the **product** side — the test-side repair from
     plan 52-09 is not accepted as closing this — and the predicate is asserted as a
     platform-independent string-shape test.

  5. **Two escaping images sharing a basename stay distinct.** Two absolute image URIs in different
     directories that share a basename and both escape the output directory relocate to two distinct
     keys instead of collapsing onto one, so neither image is silently replaced by the other
     (IMG-03).

**Plans**: TBD
**UI hint**: no

### Phase 56: Per-Document Template Documentation

**Goal**: The published documentation describes the registry that actually shipped. Documentation
lands after the code, per this project's own convention that docs describe what shipped rather than
what is planned — and this milestone makes stale documentation actively harmful in two specific
places: `configuration.rst:80` currently defines element [4] as *"accepted and ignored"*, and
`advanced.rst:129-138` instructs users to write an outdir-root-relative `"_templates/refs.bib"`,
which teaches a path the bundle layout no longer resolves.

**Depends on**: Phase 54 (documents the shipped bundle layout), Phase 55
**Requirements**: DOC-15, DOC-16, DOC-17
**Success Criteria** (what must be TRUE):

  1. **Element [4] is documented as the registry key and the retracted definition is gone
     everywhere.** `configuration.rst` describes the slot as the registry key, documents
     `typst_document_templates` (each key, the `template`-xor-`package` rule, the reserved `"typst"`
     key, and every fail-loud error a user can hit), and the "accepted and ignored" definition
     survives in **no** published surface — checked by a repo-wide grep at discovery time, not only
     in the file the requirement names (milestone invariant #4) (DOC-15).

  2. **The asset examples describe what actually works.** `templates.rst`'s asset example and
     `advanced.rst`'s `refs.bib` guidance describe the bundle layout — an asset referenced by a
     template lives in that template's own directory and is copied with it — and each published
     example is exercised by a real build rather than reviewed by eye (DOC-16).

  3. **Migration guidance for the removed values is published.** `typst_template_assets`,
     `typst_authors` and `typst_toctree_defaults` each have published guidance naming the replacement
     and the observable consequence for a `conf.py` that still sets them, matching what CONF-19's
     warning says (DOC-17).

  4. **No stale claim survives the sweep.** The documentation set as a whole — including
     `quickstart.rst`, `output_layout.rst`, `builders.rst`, `README.md`, `examples/**`, and the nine
     documentation examples that show the literal `"typst"` fifth element — is swept for claims the
     new layout invalidates, and the docs build (`tox -e docs-html` and `tox -e docs-pdf`) stays
     green. The sweep is run repo-wide at discovery time; the three requirements above name where the
     fixes are expected, not where the search is scoped.

**Plans**: TBD
**UI hint**: no

### Phase 57: v0.9.0 Release Prep (prep-only)

**Goal**: The v0.9.0 tree is bumped, its CHANGELOG curated, its claims re-proven on live runs against
the bumped tree, and handed off — with **zero irreversible action**. No tag, local or remote; no
publish; no GitHub Release. This is the standing v0.5.0 Phase 10 pattern under
`branching_strategy: milestone`, held for six consecutive milestones. **REL-08 closes at
`/gsd-complete-milestone`, not in this phase** — it is held at `[ ]` through every plan.

v0.9.0 is a **breaking minor release** on two independent axes and the CHANGELOG must say so on both:
the `_template.typ` → `_template/<key>/<file>` relocation (a template referencing an asset by
relative path must now keep that asset in its own directory) and the removal of
`typst_template_assets` (a `conf.py` that still sets it now warns, and the whole bundle is copied
regardless of what that list said). The registry itself is additive: no existing `conf.py` needs
editing.

**Depends on**: Phase 56
**Requirements**: REL-08
**Success Criteria** (what must be TRUE):

  1. **The version moves atomically to 0.9.0.** `pyproject.toml`, `uv.lock` and `README.md`'s Status
     line move in lockstep, the editable-install metadata is regenerated so `typsphinx.__version__`
     reports `0.9.0`, and every version-sync guard test stays green.

  2. **The CHANGELOG entry is curated, not generated.** A `## [0.9.0]` section names the registry as
     the headline, marks **BREAKING** on exactly the two changes above — each with its migration
     sentence — and the tail link-reference block is rolled over (the `[Unreleased]` compare link
     advanced and a `0.9.0` release/tag link added) in this same phase, since that block is
     release-prep work and not a version-bump side effect.

  3. **The bumped tree is proven green on live runs, not on the preceding phases' word.** Full pytest
     suite, `black` / `ruff` / `mypy`, both docs tox environments, a real multi-template
     `-b typstpdf` build producing two differently-typeset PDFs, and Phase 54's built-wheel content
     check — all re-run **after** the bump, with verbatim evidence recorded.

  4. **The fence is proven held.** No local or remote tag exists for `v0.9.0` and no release or
     publish has occurred — probed and recorded, twice, at separated times, as at every previous
     close. `git diff` over the phase shows no unintended `typsphinx/` change, and a checksum of
     `REQUIREMENTS.md` is recorded at the phase's start so the known `phase.complete` auto-flip of
     the release requirement — which has fired at four consecutive release-prep closes — is caught
     and reverted rather than shipped.

  5. **The handoff checklist is standalone and complete.** A `57-HANDOFF.md` enumerates every step
     `/gsd-complete-milestone` must execute, including the standing second-repository tag
     (`typsphinx-doc-translations`, advanced by dispatching that repository's own `update-pin.yml`
     rather than by hand), the RTD `stable` measurement for both projects, and the GitHub Release
     body being byte-identical to `scripts/extract_changelog_section.py 0.9.0`.

**Plans**: TBD
**UI hint**: no

## Progress

**Execution Order:**
Active milestone phases execute in numeric order (decimal insertions between their surrounding
integers), with the prep-only Release phase last so its CHANGELOG entry describes work already proven
by the preceding phases' gates. v0.9.0 executes 53 → 54 → 54.1 → 55 → 56 → 57. The one hard ordering
constraint is **53 before 54**: the registry plumbing must be in place and output-identical before
the output layout moves, because 32 test files still assert the old `_template.typ` path and the tree
must be green at every phase boundary. Phase 55 has no functional dependency on 53/54 and is
sequenced after them only to avoid contending for `builder.py` and `writer.py`.

Phase 54.1 was inserted on 2026-08-16 after Phase 54's `/gsd-code-review`, so v0.9.0 now executes
53 → 54 → 54.1 → 55 → 56 → 57. It sits immediately after 54 rather than after 55 for two reasons:
it repairs defects in what 54 itself shipped, on the same `builder.py` bundle-copy surface 54 just
rewrote; and it must precede Phase 56, which documents the settled bundle layout and would otherwise
publish guidance for behaviour 54.1 is about to change.

Phases 1–52 shipped across v0.4.4 → v0.8.0; their per-phase plan counts, statuses and completion
dates are preserved in each milestone's archived roadmap under `milestones/`. The table below tracks
the active milestone only.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 53. Template Registry Foundation | v0.9.0 | 10/10 | Complete    | 2026-08-15 |
| 54. One Bundle Rule — `_template/<key>/` | v0.9.0 | 7/7 | Complete    | 2026-08-16 |
| 54.1 Bundle Directory Safety (INSERTED) | v0.9.0 | 0/? | Not started | - |
| 55. v0.8.0-Derived Defects | v0.9.0 | 0/? | Not started | - |
| 56. Per-Document Template Documentation | v0.9.0 | 0/? | Not started | - |
| 57. v0.9.0 Release Prep (prep-only) | v0.9.0 | 0/? | Not started | - |

## Roadmap Evolution

- **2026-08-15** — v0.9.0 roadmap created: **Phases 53–57**, 26/26 v1 requirements mapped, zero
  orphans, zero duplicates. Derived from this milestone's own `REQUIREMENTS.md` (25 requirements)
  plus **REL-08**, added at roadmap creation as the release-prep requirement for the prep-only final
  phase — the same shape REL-07 held in v0.8.0. `research/SUMMARY.md`'s build order was adopted for
  its **sequence** but not its phase count: it proposes seven phases, written before the two owner
  decisions that close its own "Open Decisions Carried Forward" section were taken. Three deliberate
  divergences, each with a reason:
  **(a)** Its steps 3–5 (introduce the layout / migrate the 32 test files / delete
  `_write_template_file()`) are **one** phase (54), because they are one green boundary — the
  parallel-run state between them is deliberately wasteful scaffolding, not a shippable milestone
  state, and splitting it would create a phase boundary at which the outdir carries both the old
  `_template.typ` and the new bundle.
  **(b)** Its step 6 (config cleanup) also rides with Phase 54, because Pitfall 5 requires the
  `config-inited` detection handler in the **identical commit** as the `add_config_value()` removal;
  detection cannot be retrofitted, so the removal and its warning cannot be one phase apart.
  **(c)** The five v0.8.0-derived defects, which SUMMARY.md explicitly left to the roadmapper
  ("including where the five v0.8.0-derived defects land"), are their own phase (55) rather than
  being distributed across the registry phases — they share no subject matter with the registry, and
  folding them in would have hidden five independent RED-recorded reproductions inside a phase whose
  own RED is a byte-identity baseline.

- **2026-08-15** — Both of `research/SUMMARY.md`'s "Open Decisions Carried Forward" are **closed by
  owner decision** before roadmap creation and are recorded as binding constraints #1 and #3, not as
  planning questions: `_template/` is reserved wholesale (with `tests/fixtures/template_named_dir_master/`
  moving in Phase 54), and the `typst_template_assets` removal ships a `config-inited` warning that
  also covers `typst_authors` and `typst_toctree_defaults`. `research/ARCHITECTURE.md` §5 flags the
  fixture collision as "needs an owner decision, not an inference" — it has one; do not re-derive the
  alternative (a different reserved directory name).

- **2026-08-15** — Milestone invariant #5 (push the branch from the first phase) encoded as Phase
  53's SC#5, as v0.8.0 encoded it in Phase 47's and v0.7.1 in Phase 43's. The branch is **not** yet
  on `origin` (measured at roadmap creation by `git ls-remote --heads origin`, which returned empty).
  **Corrected 2026-08-15 during Phase 53 planning:** this entry, binding constraint #9, SC#5 and
  STATE.md all originally named `gsd/v0.9.0-milestone`. Measured: that branch sits at `aed773c9`
  (identical to `main`, and to the merge-base) and carries zero milestone commits, while all nine
  milestone commits are on `gsd/v0.9.0-per-document-templates`. The latter is the milestone branch,
  matching v0.8.0's `gsd/v0.8.0-multi-master-composition` and v0.7.1's `gsd/v0.7.1-bug-fix-round`
  naming — no `gsd/vX-milestone` branch has ever been pushed in this repository. Owner decision:
  retarget SC#5 to the working branch rather than rename it.

- **2026-08-15** — v0.8.0 closed and reorganized. Six phases (47–52), 45 plans, 121 tasks,
  24/24 v1 requirements complete, zero known gaps. Binding constraint #1 (48 before 49) held and was
  the milestone's only hard ordering constraint; the prep-only Phase 52 fence held with `typsphinx/`
  untouched despite four CI-surfaced defects, all fixed test-side. Phase detail moved to
  [`milestones/v0.8.0-ROADMAP.md`](milestones/v0.8.0-ROADMAP.md); requirements to
  [`milestones/v0.8.0-REQUIREMENTS.md`](milestones/v0.8.0-REQUIREMENTS.md); phase directories to
  `milestones/v0.8.0-phases/`.

- **2026-08-11** — v0.8.0 roadmap created: **Phases 47–52**, 24/24 v1 requirements mapped, zero
  orphans, zero duplicates. Derived from this milestone's own `REQUIREMENTS.md`, with
  `research/SUMMARY.md`'s build order adopted for its **sequence** but not its labels — SUMMARY.md
  proposes "Phase 47.1 … 47.6", which is wrong for this project, where decimals are reserved for
  phases *inserted* mid-milestone (44.1, 45.2). Three deliberate divergences from the research's
  suggested structure, each with a reason:
  **(a)** CR-02/CR-01 collision detection (BLD-02/03/04) is folded **into** Phase 47 rather than run
  as its own later phase, because the wrapper/content split is what *creates* the self-collision
  hazard — with target-as-path in the same phase, the common `("index", "index.typ", …)` config
  collides immediately, and deferring the guard one phase would ship a phase whose most common
  configuration is silently wrong (Pitfall 4).
  **(b)** OUT-01/OUT-02/OUT-03 ride with Phase 47 rather than standing alone, because B-1's fix is
  precisely "compute include paths from the wrapper's resolved location", which is the same
  computation OUT-01 changes; splitting them would implement wrapper placement twice.
  **(c)** COMP-12's full-corpus GATE-02 pass stays **inside** the composition phase rather than
  becoming a separate validation phase, per PROJECT.md's explicit instruction to make it a success
  criterion of that phase and to treat a convergence failure as a design-level finding.
  Also noted: `research/ARCHITECTURE.md` predates the design decision recorded in PROJECT.md and
  proposes a **flattened** include graph rendered wholly in the wrapper; PROJECT.md records that
  design as measured, rejected (it breaks document-order interleaving) and superseded by the
  state-guarded form. ARCHITECTURE.md's file:line integration inventory remains authoritative; its
  §"Suggested build order" flattening proposal does not.

- **2026-08-11** — Milestone invariant #5 (push the branch from the first phase) encoded as Phase
  47's SC#5, as v0.7.1 encoded it in Phase 43's. The branch `gsd/v0.8.0-multi-master-composition`
  exists locally with planning commits and is **not** yet on `origin`.

- **2026-08-11** — The five "Open Questions for Planning" in `REQUIREMENTS.md` were **not** given
  REQ-IDs and are **not** counted in coverage. Each is assigned to the phase that must close it by
  measurement and named in that phase's success criteria: #3 and #4/#5 → Phase 47, #1 → Phase 48,
  #2 → Phase 49.

## Backlog

Candidate work not yet scoped into a milestone. Promote items with `/gsd-review-backlog`, or
pull a whole cluster into the next milestone via `/gsd-new-milestone`.
Numbered 999.x so milestone reorganization never renumbers or drops them.

New items land here as `999.x` entries. **No item is open** — the backlog has been empty since
2026-08-04. Item **999.1** (inline math after text: missing separator before `#mi()` causes a Typst
error) was promoted into v0.6.5 as Phase 34 / requirement MATH-01 and shipped 2026-07-29. Item
**999.2** (a captioned table drops the id of an immediately preceding standalone target) was promoted
into v0.7.0 as **Phase 42 / requirement TBL-03** and shipped in v0.7.0. Numbering does not reuse
retired numbers, so the next item filed here is **999.3**.

**Todos and seeds promoted into v0.8.0** (2026-08-11) — the three-defect `typst_documents`-modelling
cluster the v0.7.1 close named first among next-milestone candidates, plus the two image defects that
shipped in v0.7.1 unfixed by owner decision D-27:

- `shared-document-silently-dropped-from-all-but-first-master` → Phase 49 (defect A: COMP-07, and the
  whole COMP-05..COMP-12 include-graph set that closes it)

- `a-master-that-is-also-a-toctree-child-is-unrepresentable` → Phase 47 (B-1: COMP-03)
- `duplicate-typst-documents-target-silently-drops-a-master` → Phase 47 (BLD-02) — re-measured live in
  Phase 46 and still reachable, because Phase 44's guard compares only against `env.found_docs` and
  the reserved `_template`, never against already-resolved targets

- `rehomed-converted-image-collides-with-srcdir-images-dir` → Phase 50 (IMG-01, major — a regression
  in failure mode: the same project used to abort loudly)

- `track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri` → Phase 50 (IMG-02, minor)

Each todo record stays **pending** until its phase executes; the todo is the detail record, the phase
entry above is the sequencing record.

**Still open and deferred, not in v0.8.0 scope:**

- `modernize-typing-imports-drop-up006-up035-ignore` — deferred *doubly deliberately*, since
  `CLAUDE.md` independently instructs "don't modernize typing imports until that todo lands", and
  binding constraint #9 forbids it this milestone.

- `add-sphinx-linkcheck-ci-job` — tracked as Future requirement LNK-01; `links.yml`'s repo-wide
  lychee check already covers the links each release adds.

- `ruff-generic-linux-elf-unrunnable-on-nixos` — a `flake.nix`-side toolchain repair in the same
  family as QUA-04 (Future requirement QUA-06); CI holds lint authority, so it blocks nothing.

- Dormant seeds: `SEED-001-readme-quickstart-typst-documents-pdf` (substantially discharged by v0.7.1's
  CONF-08 + DOC-11) and `SEED-003-tox-dependency-groups-per-env` (Future requirement QUA-07).

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25), v0.6.4 (2026-07-28), v0.6.5 (2026-07-29), v0.7.0 (2026-08-04), v0.7.1 (2026-08-11), v0.8.0 (2026-08-15). Per-milestone phase detail, success criteria, and decisions for shipped milestones live in `milestones/vX.Y-ROADMAP.md`.*
