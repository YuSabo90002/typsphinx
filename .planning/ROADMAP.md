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
- 🚧 **v0.8.0 — multi-master composition** — Phases 47–52 (active, started 2026-08-11)

**Active milestone: v0.8.0 — multi-master composition.** Six phases (47–52): the content/wrapper
file-shape split that also reverses v0.7.1's target-name handling and makes every path collision
loud; the compile-time cross-reference guard, which must land ahead of the graph work; the per-master
include graph with state-guarded includes; the two PR #131 image defects; the two-layer output
documentation; then prep-only release. Phase numbering continues from v0.7.1's last phase (46), so
v0.8.0 starts at **Phase 47**.

Phase numbering is **continuous across milestones** — v0.7.1 ran Phases 43–46, so v0.8.0 starts at
**Phase 47**.

## Phases

**Phase Numbering:**

- Integer phases (47, 48, …): Planned milestone work
- Decimal phases (47.1, 47.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.7.1 ran Phases 43–46, so v0.8.0 starts at **Phase 47**.

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

## 🚧 v0.8.0 — multi-master composition (ACTIVE)

**Milestone Goal:** A `typst_documents` configuration declaring more than one master produces a
complete PDF for each of them — no silently dropped content, no compile failure. The unit of
composition moves from "one `.typ` shared by every master, with the include decision baked in at
write time" to "per-master wrapper files that publish their include edge set as Typst `state`, plus
template-less docname-named content files that emit state-guarded includes at the toctree's own
position". That single re-shaping cuts the root all three known multi-master defects grow from:
**B-1** (a master that is also another master's toctree child aborts with `file not found`), **B-2**
(an included master re-expands its template's title page and `#outline()` mid-body), and **defect A**
(a document toctree'd by two masters reaches only the one whose parent was written first, decided by
docname sort order).

**Every premise this roadmap rests on was measured live on the current tree, 2026-08-11** — see
PROJECT.md's "Current Milestone" Key context. Notably: masters are **not** concatenated (each
produces its own independent PDF, so a shared chapter appearing in both is correct); the composition
rule is `inline_all_toctrees`'s document-order depth-first traversal with first-encounter-wins, **not**
"prefer the deeper path"; the `context` + `query` label-existence guard is measured working; and two
alternative designs (a per-master write-time ledger, and a flattened include graph in the wrapper)
were measured, rejected and superseded — do not re-derive them.

**Binding constraints this roadmap is built on** (settled decisions and standing invariants, not
open questions):

1. **The compile-time cross-reference guard (Phase 48) must land no later than the per-master
   include-graph work (Phase 49). Non-negotiable.** Fixing the include graph turns a currently-silent
   content omission into a hard Typst compile failure (`label ... does not exist in the document`) for
   any shared document referencing a target present in one master but not another. Shipping the graph
   first produces builds that fail outright. Phases 48 and 49 are therefore **not** independently
   parallelizable, in either order.

2. **Push the milestone branch to `origin` from the FIRST phase, not at the release PR** (milestone
   invariant #5, adopted v0.7.1 and it paid immediately). The branch
   `gsd/v0.8.0-multi-master-composition` already exists locally with planning commits and has **not**
   been pushed. Both defects that cost v0.7.0 — a Windows-only encoding failure and an unexercised
   release job — came from the branch never being pushed until the end. Phase 47 carries this as
   SC#5; every later phase inherits it as a standing expectation. This milestone raises the stakes:
   Pitfall 5's case-insensitive-filesystem collision gap is invisible on Linux-only local runs.

3. **The final phase (52) is prep-only and takes zero irreversible action.** Version bump, curated
   CHANGELOG entry, evidence gathering, handoff checklist. No tag, no publish, no GitHub Release. This
   is the standing v0.5.0 Phase 10 pattern under `branching_strategy: milestone`; the publish half
   executes at `/gsd-complete-milestone`, where REL-07 closes.

4. **GATE-01 (standing since v0.6.0), with its non-fatal amendment.** Every node-handler / emission
   change ships a real `sphinx-build → typst.compile()` regression fixture recorded **red against the
   unfixed code** before being accepted as green. All three composition defects genuinely fail today,
   so the classic RED (a `TypstError`, or a measurably wrong emitted structure) is available — **but
   several requirements in this milestone are "compiles fine, produces wrong output" defects**
   (BLD-02/03/04, IMG-01, IMG-02, and possibly COMP-04 pending the open question below). Each of those
   must have its RED assertion — `pypdf` text/page comparison, or a structural assertion over the
   emitted `.typ` — **written down before implementation starts**, per v0.7.0's own amendment. A phase
   plan listing "GATE-01 fixture" as a checkbox without naming the pre-fix RED assertion for a
   non-fatal defect does not satisfy this constraint.

5. **GATE-02, the full Sphinx `doc/` corpus regression gate, is an explicit success criterion of the
   composition phase (49).** The state-guarded include design rests on Typst's `state`/`context`
   multi-pass layout convergence, which is measured on the diamond, interleaving, outline and label
   cases but **not** at corpus scale. Treat a convergence failure there as a **design-level finding**,
   not a fixture bug.

6. **No laundered gates.** This milestone moves every assertion that reads a master `.typ`'s contents
   (v0.7.0's comparable change measured 10 test files / 61 render-gate classes; this one is likely
   larger, since `_is_master_document` disappears entirely). Expected wrapper/content structure must
   be derived **from first principles** — from the `typst_documents` config plus the toctree source
   read literally from the `.rst` fixtures — and written down **before** running the new emitter.
   Prefer structural/regex assertions over full exact-string diffs; reserve exact strings for what is
   deterministic by construction (the `@preview` import lines, pinned independently by
   `test_preview_version_sync.py`). Every changed expected value must be traceable to a written-first
   rationale at review. Copy-pasting the new emitter's output into the "expected" block proves only
   that the code does what the code does.

7. **Standing invariants carried forward:** zero new runtime dependencies (every primitive needed —
   `include`, `set heading(offset:)`, `context`, `query`, `state` — is Typst 0.15 standard library);
   the `@preview` package count stays at **four** with no new version-lockstep site (`writer.py` /
   `template_engine.py` / `templates/base.typ` plus `examples/**/*.typ`); and **no new `typst_*`
   config value** — target-as-path (OUT-01) expresses both wrapper placements with no new config
   surface, and this project has removed config values in four consecutive milestones rather than
   adding them.

8. **Every phase closes green:** full pytest suite, `black` / `ruff` / `mypy`, and that phase's own
   gates. "Anywhere under X" success criteria are checked by a repo-wide grep at discovery time, never
   against the files a requirement happens to name (milestone invariant #4).

9. **Typing-import modernization is forbidden this milestone** — `CLAUDE.md` independently instructs
   "don't modernize typing imports until that todo lands", and the todo is not in scope. Neither is
   `add-sphinx-linkcheck-ci-job` (Future requirement LNK-01). Neither may be picked up
   opportunistically while touching an adjacent file.

**REQUIREMENTS.md's five "Open Questions for Planning" are not requirements and carry no REQ-IDs.**
Each is assigned to the phase that must close it **by measurement**, and named in that phase's
success criteria:

| Open question | Owning phase |
|---|---|
| 1. `translator.py:4291`'s nature — fourth independent degradation site, or already routed through `_reference_anchor_decision`? | **Phase 48** (cross-reference guard) |
| 2. `:numref:` project-wide vs. per-wrapper numbering divergence — no compile error catches it; needs a live two-master fixture | **Phase 49** (include graph) |
| 3. B-2's RED state — compile fatal, or compiles-fine-but-wrong-output? | **Phase 47** (file-shape split) |
| 4. CR-01 self-collision policy — a target resolving onto its own master's docname: allow, or refuse? | **Phase 47** (collision detection) |
| 5. Case-normalization scope — normalize collision comparisons, or refuse case-differing targets outright? | **Phase 47** (collision detection) |

**Not a frontend UI milestone** (standing project note): every phase below is builder, writer,
translator, documentation and release work. `ui.plan-gate` false-positives on words this milestone
cannot avoid — "page" (title page, `#outline()`), "layout" (Typst's layout convergence), "render",
"template". Each phase detail therefore carries an explicit `**UI hint**: no` line, the authoritative
override `ui-safety-gate.cjs` reads, rather than relying on a per-run `--skip-ui`.

- [x] **Phase 47: Two-Layer Output — Content/Wrapper Split, Target-as-Path, Collision Detection** - Every docname gets a template-less content `.typ`, every `typst_documents` entry gets a wrapper at the path the user actually wrote, B-1 and B-2 close, and any two logical files wanting one physical path are reported instead of silently overwriting (completed 2026-08-12)
- [x] **Phase 48: Compile-Time Cross-Reference Guard** - Whether a reference's target label exists is decided by Typst per compiled wrapper instead of by a build-time union across all masters, so a missing label degrades to plain text rather than aborting — landed before the graph work that would otherwise make it fatal (completed 2026-08-14)
- [x] **Phase 49: Per-Master Include Graph with State-Guarded Includes** - Each wrapper computes its own include edge set by mirroring `inline_all_toctrees` and publishes it as Typst `state`; content files emit state-guarded includes at their toctree's own position, closing defect A and the diamond, and holding at full-corpus scale (completed 2026-08-14)
- [x] **Phase 50: PR #131 Image Path Defects** - A converted image rehomed to `images/<basename>` no longer collides with a real source image of the same name, and an absolute image URI outside `doctreedir` no longer writes outside the output directory (completed 2026-08-14)
- [ ] **Phase 51: Two-Layer Output Documentation** - The published documentation says which file to compile, what a content file compiled standalone does, what target-as-path means, and exactly what changed from v0.7.x
- [ ] **Phase 52: v0.8.0 Release Prep (prep-only)** - The v0.8.0 tree is bumped, its CHANGELOG curated around the output-shape change and the target-as-path reversal, proven green on real multi-master evidence, and handed off with no irreversible action taken

## Phase Details

### Phase 47: Two-Layer Output — Content/Wrapper Split, Target-as-Path, Collision Detection

**Goal**: The unit of output stops being "one `.typ` per docname whose shape depends on whether that
docname is a master". Every document is written as a docname-named **content** file carrying no
template at all, and every `typst_documents` entry gains a **wrapper** file carrying the template
application and the include of its master's content — so `writer.py:96`'s `_is_master_document()`
binary, which today selects the output shape, disappears. This closes **B-1** (the parent includes
`guide/index.typ` from the docname while `_resolve_output_stem` names the file from the target, so
Typst aborts with `file not found`) and **B-2** (an included master re-expands its template's title
page and `#outline()` into the middle of the parent's body). Composition semantics are deliberately
**not** touched here — the wrapper reproduces today's include behaviour through the new file shape, so
"does the new file shape work at all" is isolated from "does the new graph algorithm work" (Phase 49).

**OUT-01 is a deliberate REVERSAL of three locked decisions from v0.7.1 Phase 44 — D-05, D-06 and
D-07 — and the phase's artifacts must state it as such so the executor does not treat the existing
guard code as sacred.** Today a path in a target is rejected and truncated to its basename (D-06/D-07)
and a nested docname's output is forced into that docname's own directory (D-05). Both rules go: a
target becomes a path relative to the output directory, so a bare name writes the wrapper at the
output root and an explicit path writes it where the user asked. **OUT-02 keeps the security half of
those same guards** — `..`, absolute, and drive-qualified targets stay refused with a warning and a
safe fallback. This project has precedent for reversing a locked decision within a milestone
(v0.7.1's Phase 44.2 reversed Phase 44's D-02); the reversal here is deliberate and is the reason no
new config value is needed for wrapper placement.

The collision work rides with the file-naming change rather than following it, because the split
**creates** the hazard: once every docname unconditionally gets a content file, a target resolving
onto its own master's docname is a real wrapper-vs-content collision on one physical path, and
whichever write runs last wins silently — a build that reports success and produces a PDF with no
title page, no `#outline()` and none of its children, with no `TypstError` to catch it. Deferring
that one phase would mean shipping a phase whose most common configuration is silently wrong.

**Depends on**: Nothing (first phase of the milestone)
**Requirements**: COMP-01, COMP-02, COMP-03, COMP-04, OUT-01, OUT-02, OUT-03, BLD-02, BLD-03, BLD-04
**Success Criteria** (what must be TRUE):

  1. **The two-layer file set exists and is placed where the user wrote it.** A real `sphinx-build`
     of a project configured `("index", "manual.typ", …)` writes the wrapper at `outdir/manual.typ`
     and the content at `outdir/index.typ`; a project configured `("guide/index",
     "manuals/guide.typ", …)` writes the wrapper at `outdir/manuals/guide.typ` while its content stays
     at `outdir/guide/index.typ` — a bare name at the output root, an explicit path where the user
     asked, content files docname-derived regardless of wrapper placement (COMP-01, COMP-02, OUT-01,
     OUT-03). The same project built `-b typst` and `-b typstpdf` produces **byte-identical** wrapper
     and content files, so the two `write_doc` overrides cannot silently diverge. `_is_master_document`
     is gone, verified by repo-wide grep rather than by reading `writer.py`.

  2. **B-1 closed, on the classic RED and on the shape that actually exercises it.** A docname listed
     in `typst_documents` that is **also** another master's toctree child builds and compiles to a PDF
     in both roles — with the fixture recorded RED (`TypstError`, `file not found`) against the unfixed
     tree first (COMP-03). The fixture uses a **nested** master whose target basename differs from its
     docname, so the wrapper's `#include()` paths are proven computed from the wrapper's **resolved**
     output location, not from the raw master docname — the exact way B-1 could otherwise be
     reintroduced one level up.

  3. **B-2 closed, with its RED shape chosen by measurement rather than assumed.** Open question #3
     closes here **before** any fix: it is measured on the unfixed tree whether the mid-body template
     re-expansion is a compile fatal or a compiles-fine-but-wrong-output defect, and that measurement
     selects the GATE-01 RED — classic `TypstError`, or a structural assertion over the emitted `.typ`
     plus `pypdf` text. Post-fix, an included document contributes no title page, no `#outline()` and
     no second template application anywhere in the parent's body (COMP-04).

  4. **Every "two logical files want one physical path" case is loud, and both policies are decided
     before code is written.** Two entries resolving to the same target path are detected and reported,
     never silently dropping one master's body (BLD-02); a wrapper target colliding with a content
     file's own path is detected (BLD-03) under a policy recorded first — open question #4, allow with
     forced-distinct paths versus refuse with a fallback, following CR-01's convention of never
     inventing a filename the user did not write; and collision comparisons behave identically on
     case-insensitive filesystems (BLD-04) under the recorded answer to open question #5 (normalize
     both sides, or refuse case-differing targets), proven by a case-varied fixture such as target
     `Manual.typ` against docname `manual`. **All three are non-fatal defects today**, so each ships
     its own pre-fix RED assertion — `pypdf`/structural proof that the body actually goes missing —
     per binding constraint #4; "does not compile" is unavailable here.

  5. **The security half of the reversed guards survives, and the milestone branch is on `origin`.** A
     target containing `..`, an absolute path, or a drive-qualified path is still refused with a
     warning and a safe fallback, with a fixture per escape shape (OUT-02) — only the
     "any separator means truncate to basename" and docname-directory-forcing rules are removed, and
     the phase's artifacts record this explicitly as a reversal of Phase 44's D-05/D-06/D-07.
     `gsd/v0.8.0-multi-master-composition` is pushed to `origin` **in this phase**, evidenced by a
     `git ls-remote --heads origin` hit plus at least one completed CI run over it including the
     Windows and macOS lanes (milestone invariant #5, binding constraint #2).
**Plans**: 14/14 plans executed — 12/12 executed, plus 2 further gap-closure plans (waves 7-8) added 2026-08-12
after re-verification scored 10/11 and returned BLD-03 BLOCKED on a newly-found BLOCKER
(`47-REVIEW.md` CR-01):

- [x] 47-01-PLAN.md .. 47-10-PLAN.md — the original ten, all executed and summarized
- [x] 47-11-PLAN.md — close the BLD-02/BLD-03 false negatives: path-shape normalization inside
      `_collision_key()`, one shared entry-usability predicate across all four wrapper-path sites,
      RED recorded on content before either fix

- [x] 47-12-PLAN.md — delete the WR-01 dead entry-element resolver and correct the six stale
      REQUIREMENTS.md checkboxes

- [x] 47-13-PLAN.md — BLOCKER: route `_compute_master_included_docnames()` (the fifth site consuming
      `typst_documents`) through the shared entry-usability predicate, closing a silent dangling-label
      defect and an uncaught `TypeError`, with RED recorded on content and traceback first

- [x] 47-14-PLAN.md — delete the WR-01 dead `_resolve_output_stem()` output-stem resolver, retarget
      its 22 surviving assertions onto the live resolvers, and flip BLD-02's checkbox

**Corpus migration cost measured at planning time (2026-08-11), not present in RESEARCH.md:** the
content/wrapper split makes the overwhelmingly common fixture shape `("index", "index", ...)` a
wrapper-vs-content collision. **87 of the 100 fixture projects under `tests/fixtures/` carry exactly
that shape**, and **68 test modules with 591 code-level `index.typ` / `index.pdf` references** read
the pre-split file shape. Binding constraint #8 requires the phase to close green, so plans 47-04
through 47-08 carry that migration; it is the single largest cost in the phase and is why the phase
has ten plans rather than three.

Plans:
**Wave 1**

- [x] 47-01-PLAN.md — Derive the expected two-layer structure from first principles and capture the pre-fix RED for all five defects (wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 47-02-PLAN.md — Two-layer emitter, tracer-led: content/wrapper split, OUT-01/OUT-02 disentangle, one shared write path (wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 47-03-PLAN.md — Move the OUT-01 unit expectations; pin all three OUT-02 escape shapes with an outdir-containment proof (wave 3)
- [x] 47-04-PLAN.md — Corpus migration group A: 17 modules / 34 fixtures (wave 3)
- [x] 47-05-PLAN.md — Corpus migration group B: 17 modules / 19 fixtures, toctree and multi-document suites (wave 3)
- [x] 47-06-PLAN.md — Corpus migration group C: 17 modules / 18 fixtures, entry-metadata and integration suites (wave 3)
- [x] 47-07-PLAN.md — Corpus migration group D: 17 modules / 16 fixtures, page-count and template-contract gates (wave 3)
- [x] 47-08-PLAN.md — Residual surface: template-routing suites, `typst_documents`-shape gates, dogfooding builds (wave 3)

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 47-09-PLAN.md — Unified pre-write collision validator (D-01/D-02/D-03/D-05), CR-01 inversion, phase green gate (wave 4, 2 blocking decision checkpoints)

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 47-10-PLAN.md — Push the milestone branch to `origin` and evidence a completed CI run over the Windows and macOS lanes (wave 5)

**Wave 6** *(gap closure, blocked on Wave 5 completion)*

- [x] 47-11-PLAN.md — Path-shape normalization in `_collision_key()` + one entry-usability predicate across the four wrapper-path sites (wave 6)
- [x] 47-12-PLAN.md — Delete the dead `writer.py::_resolve_entry_element()`, retarget its coverage, correct six REQUIREMENTS.md checkboxes (wave 6)

**Wave 7** *(gap closure, blocked on Wave 6 completion)*

- [x] 47-13-PLAN.md — BLOCKER/CR-01: wire the fifth `typst_documents` consumer (`_compute_master_included_docnames()`) onto the shared predicate; two new fixtures, an eight-test gate, RED-then-GREEN evidence (wave 7)

**Wave 8** *(blocked on Wave 7 completion — same file, `typsphinx/builder.py`)*

- [x] 47-14-PLAN.md — WR-01: delete the dead `builder.py::_resolve_output_stem()`, retarget 22 assertions onto `_resolve_target_stem()`, sweep the tracked tree, flip BLD-02 (wave 8)

**UI hint**: no

### Phase 48: Compile-Time Cross-Reference Guard

**Goal**: Whether a cross-document reference's target label exists is decided by **Typst at compile
time, per compiled wrapper**, instead of by a build-time boolean derived from `master_included_docnames`
— a union across *all* masters that cannot know which master is currently asking. A content file is
now compiled zero, one, or many times, once per wrapper that includes it, and the same degrade
decision must come out differently in each; that information genuinely does not exist until a specific
wrapper is compiled. The validated guard shape is already measured working against typst-py 0.15.0
(PROJECT.md records the exact snippet: `context { if query(<label>).len() > 0 { link(<label>, …) }
else { … } }` — without the target document included the compile **succeeds** and the PDF carries no
link annotation; the unguarded form fails outright with `label ... does not exist in the document`).

**This phase exists here, ahead of Phase 49, because of binding constraint #1.** Fixing the include
graph converts today's silent omission into a hard compile failure for any shared document referencing
a target present in one master but not another. The guard is what makes the graph fix safe to ship;
shipping them in the other order produces builds that fail outright. `:orphan:` targets and per-master
differences also become correct through this one mechanism rather than three.

**Depends on**: Phase 47
**Requirements**: XREF-03, XREF-04
**Success Criteria** (what must be TRUE):

  1. **A reference whose target is absent from the compiling master degrades to plain text and the
     compile succeeds.** Evidence: one two-master fixture built through `sphinx-build -b typstpdf`,
     where the master that includes the target produces a PDF carrying a real link annotation and the
     master that does not produces the same visible text with no link annotation and **no**
     `TypstError` — both read back through `pypdf`. The unguarded form is recorded first as the RED
     (`label <...> does not exist in the document`) (XREF-03).

  2. **Every label-reference emission site routes through one shared guard helper, and open question
     #1 is closed by reading the code.** A repo-wide grep enumerates the emission sites — the primary
     `visit_reference` cross-document branch, the `translator.py:3273`/`:3281` citation
     back-references, and `:4291` — and each is shown calling the shared helper rather than carrying
     its own derivation. `translator.py:4291` is **read** and its nature recorded in the phase's
     artifacts (a fourth independent degradation site, or already routed through
     `_reference_anchor_decision`); the answer, not an assumption, determines what XREF-04 has to
     change there.

  3. **The build-time mechanism is deleted in the same change, not left half-alive.**
     `grep -rn master_included_docnames typsphinx/` returns nothing; `_compute_master_included_docnames`
     and its call site in `write()` are gone; `_ReferenceAnchorDecision` no longer carries
     `degrade_xref_to_text` or its builder-state lookup. No second, competing degrade decision survives
     anywhere that could disagree with the compile-time one (XREF-04).

  4. **The guard is applied only where it is needed, and its cost is measured rather than assumed.**
     Same-document anchors — whose target is always present whenever the content file is included at
     all, since content files are included wholesale — keep their unguarded form, asserted explicitly.
     The full-corpus `-b typstpdf` compile time is recorded before and after, so a material regression
     from per-reference `query()`-driven introspection passes is a stated finding handed forward rather
     than a surprise discovered at corpus scale.
**Plans**: 7/7 plans executed (4 original plans + 3 gap-closure plans added 2026-08-13 for UAT gap G-48-4 — a whole-document `:doc:` reference emitted as a dead file link)

Plans:
**Wave 1**

- [x] 48-01-PLAN.md — Settle the body-mode question by real compile, write the flipped assertions'
      expected values first, capture both reachable pre-fix REDs, and record D-04's enumerated
      impossibility argument (wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 48-02-PLAN.md — TRACER: one cross-document reference guarded end to end through
      `sphinx-build -b typstpdf` → `typst.compile()` → `pypdf`, with the build-time union, its
      degrade field and its warning all deleted in the same change (wave 2)

**Wave 3** *(blocked on Wave 2 completion — same file, `typsphinx/translator.py`)*

- [x] 48-03-PLAN.md — Expand to the remaining two emission sites (citation back-references, D-05;
      `pending_xref`, D-04) and pin the helper contract, the D-06 exemption and the
      single-derivation-point property with direct unit tests (wave 3)

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 48-04-PLAN.md — D-11 cost measurement against pre-fixed tiers, D-09 citation-marker corpus
      delta, the accepted label-collision limit, SC#2/SC#3 repo-wide grep discharge, D-01
      published-contract re-check, phase green gate (wave 4)

**Wave 5** *(gap closure for UAT G-48-4 — blocked on Wave 4 completion)*

- [x] 48-05-PLAN.md — Enumerate the pre-fix dead-link population in the built documentation PDF,
      get the owner's decision on the Sphinx-generated pages that have no Typst counterpart, and
      write every post-fix expected value down before the emitter changes (wave 5)

**Wave 6** *(blocked on Wave 5 completion)*

- [x] 48-06-PLAN.md — Whole-document acceptance fixture plus two gates recorded RED against the
      unfixed emitter: a fast resolver/self-anchor unit gate and a real
      `sphinx-build → typst.compile() → pypdf` render gate (wave 6)

**Wave 7** *(blocked on Wave 6 completion — same file, `typsphinx/translator.py`)*

- [x] 48-07-PLAN.md — TRACER: every content file emits a stable self-anchor and the whole-document
      reference case routes through the existing shared guard against it, then the documentation
      PDF's dead-link count is re-measured against the pinned baseline (wave 7)

**UI hint**: no

### Phase 49: Per-Master Include Graph with State-Guarded Includes

**Goal**: The include decision moves from **write time to compile time**, which is what lets one
shared content file behave correctly for every master that includes it. The builder computes each
master's include graph by mirroring `sphinx/util/nodes.py:485` `inline_all_toctrees` — document-order
depth-first, first encounter wins, `traversed` re-initialised **per master** — and the wrapper emits
`#state("inc", ()).update((<edge keys>))` before including its master's content. `visit_toctree` stops
emitting an unconditional `include()` and instead emits `context { set heading(offset: heading.offset

+ 1); if "<parent>><child>" in state("inc", ()).get() { include("<child>.typ") } }` at the toctree's

own position, and `builder.py:99`'s build-scoped `_included_docnames` ledger becomes unnecessary. This
closes **defect A** and the diamond `M → [p, q]`, `p → [c]`, `q → [c]`, `M' → [q]` that no
write-time ledger can serve, while keeping heading offsets relative (no DFS-depth arithmetic in the
wrapper) and keeping conditionally-included content both `#outline()`-visible and `query`-able.

Two rejected designs are recorded in PROJECT.md and must not be re-derived: a per-master write-time
ledger (cannot serve the diamond — one file written once cannot both omit and emit the same include),
and a flattened include graph carried entirely by the wrapper (solves the diamond but breaks
document-order interleaving, rendering prose-after-toctree before the chapters instead of after them).

**Depends on**: Phase 48 (binding constraint #1 — the guard must already be in place; these two are
not independently parallelizable)
**Requirements**: COMP-05, COMP-06, COMP-07, COMP-08, COMP-09, COMP-10, COMP-11, COMP-12
**Success Criteria** (what must be TRUE):

  1. **Defect A closed on generated evidence, not on the code looking correct.** One real
     `sphinx-build -b typstpdf` of a two-master project where both masters toctree `shared` produces
     **two** PDFs, each containing the shared chapter's marker text, read back through `pypdf` —
     against the measured 2026-08-11 baseline where `index.pdf` reports `SHARED-CHAPTER-MARKER` **0**
     times and `bmaster.pdf` reports 1, at exit 0 with no warning. The pre-fix state is recorded as
     the RED first (COMP-07).

  2. **The diamond compiles correctly from one shared content file, and its neighbouring graph shapes
     each have a decided outcome.** For `M → [p, q]`, `p → [c]`, `q → [c]`, `M' → [q]`: `C-BODY`
     appears **exactly once** in `M`'s PDF and exactly once in `M'`'s PDF, produced by the same
     `q.typ` (COMP-09). The fix is proven not to be 2-master-specific or shape-specific: fixtures also
     cover ≥3 masters sharing ≥2 overlapping children, a 2-node toctree cycle, a self-referencing
     toctree, a `:glob:` toctree, and a reference to an `:orphan:` document — each with its expected
     outcome (include, skip, or degrade-to-text) decided during planning rather than discovered as a
     test failure.

  3. **The traversal matches Sphinx's own selection rule, and heading depth follows it.** The DFS is
     written fresh with an ordered `traversed` threaded through recursion, iterating each document's
     toctree entries in source order — **not** by generalizing `_compute_master_included_docnames`'s
     LIFO `stack.pop()`/`append()` walk, which silently reverses child order with no compile error
     (COMP-05). A mirror-pair fixture over PROJECT.md's own measured shape (`xmaster` listing
     `[zmid, shared]` versus `[shared, zmid]`) proves the resulting nesting **tracks source order**
     rather than a hardcoded "prefer deeper" rule, asserted on **resolved** heading levels via
     `typst.query(…, 'heading', field='level')` against the compiled document, not by grepping `.typ`
     (COMP-10).

  4. **Prose keeps its position relative to included content, and the write-time machinery is gone.**
     A master shaped like Sphinx's own default `index.rst` — prose, then a `.. toctree::`, then an
     "Indices and tables" section — renders `PROSE-BEFORE` → chapter bodies → `PROSE-AFTER` in the
     compiled PDF's text order (COMP-08), which is the property that selected the state-guarded design
     over the flattened one. `visit_toctree` emits no unconditional `include()`, and
     `builder._included_docnames` and its `init()`/`write()` resets are deleted — both verified by
     repo-wide grep (COMP-06, COMP-11).

  5. **It holds at real corpus scale, and the `:numref:` question is answered by measurement.** The
     full Sphinx `doc/` corpus compiles fatal-free through `-b typstpdf` under the new composition —
     valid `%PDF`, empty `unknown_visit` catalogue — demonstrating that the `state`/`context`
     multi-pass layout convergence holds beyond the small measured cases; **a convergence failure here
     is a design-level finding, not a fixture bug** (COMP-12, binding constraint #5). Open question #2
     closes here on a **live two-master fixture**, not by inference: the same `:numref:`-targeted
     figure sits at different DFS positions in two masters, and Sphinx's baked-in "Figure N" text is
     compared via `pypdf` against the Typst-rendered caption number in each master's PDF. If they
     diverge — expected, since Sphinx numbers project-wide while Typst counts per compiled wrapper,
     with **no compile error to catch it** — the divergence is either fixed or recorded as a
     documented limitation and handed forward to Phase 51 (docs) and Phase 52 (CHANGELOG).
**Plans**: 6/6 plans executed

Plans:
**Wave 1**

- [x] 49-01-PLAN.md — Emission contract measured against real compiles, plus the written-first expected structure: fixture specification, degenerate-shape outcome table and repo-wide assertion census (wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 49-02-PLAN.md — Two-master and mirror-pair fixtures, defect A's non-fatal pre-fix RED, and the composition gate recorded as strict xfails (wave 2)
- [x] 49-03-PLAN.md — Seven degenerate-shape and hazard fixtures, the `self`/external-URL classic RED, and the shapes gate recorded as strict xfails (wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 49-04-PLAN.md — TRACER: per-master include graph wired end to end (builder graph, wrapper `state` publication, guarded emission, ledger deleted) plus the full assertion migration in the same plan (wave 3)

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 49-05-PLAN.md — COMP-11 removal gate, the assumption-delta contract test, the SC#4 repo-wide sweep and the degenerate-shape closure record (wave 4)

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 49-06-PLAN.md — GATE-02 full-corpus convergence, the two-case `:numref:` measurement, and the owner checkpoint on the corpus result and the D-01 decision (wave 5)

**UI hint**: no

### Phase 50: PR #131 Image Path Defects

**Goal**: The two defects the PR #131 review filed against the code that PR introduced, both living in
`TypstBuilder._track_image()` and best fixed together. They ship unfixed in v0.7.1 by owner decision
D-27 and are independent of the composition work — nothing here touches `write_doc()`'s composition
shape, and content files staying docname-named means `_compute_relative_image_path` needs no change at
all. **IMG-01 is also a regression in failure mode**, not merely a defect: the same project used to
abort loudly, and now renders the wrong picture silently.

**Depends on**: Phase 49
**Requirements**: IMG-01, IMG-02
**Success Criteria** (what must be TRUE):

  1. **A rehomed converted image and a real source image of the same basename no longer destroy each
     other.** A project containing both a converted image rehomed to `images/<basename>` and an
     ordinary source image genuinely at `<srcdir>/images/<basename>` copies **both**, and each document
     renders its own picture — verified from the compiled PDFs, not from the copy list alone (IMG-01).
     This compiles fine today and is simply wrong, so the pre-fix RED is a written-first structural /
     embedded-image assertion proving that today one file is never copied and the other document
     embeds the wrong picture with no warning — not "does not compile" (binding constraint #4).

  2. **An absolute image URI outside `doctreedir` never escapes the output directory.**
     `copy_image_files()` writes every destination **under** `outdir`, and never collapses
     `src == dest` (Issue #130's original shape), for an absolute URI that `relpath(uri, doctreedir)`
     resolves with a `../` prefix (IMG-02). RED first: a fixture proving today's destination is
     `../`-prefixed; post-fix, every written destination is asserted to be inside `outdir`.

  3. **No collateral change to ordinary image handling.** Images that are neither rehomed-with-a-
     colliding-basename nor absolute-outside-`doctreedir` are copied to byte-identical destinations
     across the change, measured by a two-build comparison over `docs/source` and every root under
     `tests/roots`, and PR #131's own Issue #130 regression tests still pass unchanged.
**Plans**: 3/3 plans executed

Plans:
**Wave 1**

- [x] 50-01-PLAN.md — Wave 1: D-10 sibling fixture + the D-08 render gate, with both collision assertions recorded RED against the unfixed builder

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 50-02-PLAN.md — Wave 2: tracer — widen `_track_image()` end-to-end for IMG-01 and IMG-02 as one change, bracketed by the D-11 two-build measurement

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 50-03-PLAN.md — Wave 3: unit coverage for the three relocation branches, plus the cross-wave audit of the phase's evidence chain

**UI hint**: no

### Phase 51: Two-Layer Output Documentation

**Goal**: A user reading the published documentation can tell which of the two files typsphinx now
writes is the one to compile, and what happened to the file they used to compile. The output-shape
change is invisible until an existing `typst_documents` config produces a different set of files: with
`typst_documents = [("index", "manual.typ", …)]`, `manual.typ` stops being the whole document and
becomes the wrapper, while the body moves to `index.typ`. Anyone whose tooling expects `manual.typ` to
contain the full document finds a thin wrapper instead. That has to be documented, not discovered.

**Depends on**: Phase 50 (documentation describes behaviour that must have landed first — the same
ordering v0.7.1 used for Phase 45 after Phase 44)
**Requirements**: DOC-14
**Success Criteria** (what must be TRUE):

  1. **The published documentation names the two layers and says which one to compile.** For any
     `typst_documents` configuration, the docs state that the wrapper (at the entry's target path) is
     the file to compile, and that a content file compiled standalone sees an empty `state` and
     therefore includes **no children** — documented as intended, well-defined behaviour rather than
     left to be reported as a bug. `-b typst` users are told to compile the wrapper.

  2. **Target-as-path semantics are documented with worked examples, and the change from v0.7.x is
     stated in old→new file names.** A bare target writes at the output root; an explicit path writes
     where the user asked; a target containing `..`, absolute, or drive-qualified is refused with a
     warning and a safe fallback. The "what changed" section names a concrete config and its concrete
     before/after file set, alongside v0.7.1's own `index.typ` → `<project>.typ` default-derivation
     rename, so the two renames are not confused with each other.

  3. **Every documented claim is verified against the built code, not written from the design.** Each
     example configuration on the page is actually built through `sphinx-build` and the emitted file
     set compared against what the page claims; any limitation Phase 49 measured and chose to document
     rather than fix (open question #2's `:numref:` divergence, and any accepted ordering consequence)
     appears here in the user's language. No claim survives that a build does not reproduce.
**Plans**: TBD
**UI hint**: no

### Phase 52: v0.8.0 Release Prep (prep-only)

**Goal**: The v0.8.0 tree is ready to publish and proven green, with **zero irreversible action
taken** — no tag, nothing pushed to PyPI, no GitHub Release. This is the standing prep-only Release
phase (the v0.5.0 Phase 10 pattern under `branching_strategy: milestone`): bump, curate, prove, hand
off. The publish half — merge → tag → `release.yml` → PyPI + GitHub Release, plus the standing second
tag on `typsphinx-doc-translations` — executes at `/gsd-complete-milestone`, where **REL-07 closes**.

Two of this project's own recorded lessons apply directly here. **12a:** the release-prep phase is the
one phase whose `phase_complete=true` has, four milestones running, never been independently
machine-verified before close — "complete" has only ever meant "the code changes landed", not "the
release evidence was generated". **12b:** a requirement reported complete on the strength of the code
being correct is exactly how v0.7.0 lost REL-04. For v0.8.0 this generalizes past REL-07: the
milestone's own goal claim — "produces a complete PDF for each master, no silently dropped content" —
must rest on a real multi-master round trip, not on unit-level fixture passes.

**Depends on**: Phase 51
**Requirements**: REL-07
**Success Criteria** (what must be TRUE):

  1. **Version literals move in lockstep.** `pyproject.toml` is the sole `0.8.0` literal, with
     `uv.lock` and `README.md` moved with it and the editable-install metadata regenerated so
     `typsphinx.__version__` reports `0.8.0`; all three version-sync guard tests stay green.

  2. **`CHANGELOG.md` carries a curated `## [0.8.0]` entry covering every v1 requirement this
     milestone delivered, with both user-visible changes called out explicitly** — (a) the
     **output-shape change**: the target file is now a thin wrapper and the body moved to
     `<docname>.typ`, named with the measured before/after file pair for a concrete config and
     distinguished from v0.7.1's own `index.typ` → `<project>.typ` rename; and (b) the
     **target-as-path reversal** of v0.7.1 Phase 44's D-05/D-06/D-07, stated as a deliberate behaviour
     change with its security half retained. Any limitation Phase 49 measured and documented appears
     here too. The tail link block advances (new tag link + `Unreleased` compare), and
     `docs/source/changelog.rst` is confirmed still rendering live from the repo-root file (DOC-12's
     mechanism) rather than needing a second hand edit.

  3. **The post-bump tree is proven green live, not inherited — including the milestone goal itself.**
     Full pytest, `black`/`ruff`/`mypy`, the full-corpus `-b typstpdf` GATE-02 gate, and both docs
     builds (`docs-html`, `docs-pdf`) are re-run against the bumped tree. Alongside them, the goal
     claim is discharged on generated evidence: a real `sphinx-build -b typstpdf` over a **multi-master
     project with ≥2 masters and ≥1 shared child**, its PDFs opened via `pypdf`, with specific
     text/page assertions proving each master's full content is present — not "the code looks correct"
     and not "one representative fixture compiles".

  4. **The standing invariants are asserted mechanically over the SHA-anchored full milestone diff**
     (merge-base to HEAD, excluding `.planning/`), with a positive control: zero new runtime
     dependencies, and the `@preview` package count still **four** with no new version-lockstep site
     across `writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`. No new
     `typst_*` config value was added.

  5. **No irreversible action was taken, and the handoff is standalone.** `git tag -l v0.8.0` and
     `git ls-remote --tags origin v0.8.0` are both empty at phase end, and a standalone checklist
     exists for `/gsd-complete-milestone` covering merge → tag → `release.yml` (with an explicit item
     to observe `create-release` succeed) → PyPI + GitHub Release → the second tag on
     `typsphinx-doc-translations` → the Read the Docs `stable` measurement on both projects. The
     phase's artifacts state that **REL-07 remains open until the publish**, and do not report it
     complete on the strength of the prep being correct.
**Plans**: TBD
**UI hint**: no

## Progress

**Execution Order:**
Active milestone phases execute in numeric order (decimal insertions between their surrounding
integers), with the prep-only Release phase last so its CHANGELOG entry describes work already proven
by the preceding phases' gates.

**v0.8.0 (active)** runs 47 → 48 → 49 → 50 → 51 → 52. The 47 → 48 → 49 chain is genuinely
sequential, not merely numbered:

- **47 before 48/49** because both later phases operate on the new two-file shape — the guard is
  landed against it, and the include graph is computed for wrappers that only exist after 47.

- **48 before 49 is the milestone's one hard ordering constraint** (binding constraint #1). Fixing the
  include graph turns a currently-silent content omission into a hard `label ... does not exist`
  compile abort for any shared document referencing a target present in one master but not another.
  Shipping the graph first produces builds that fail outright. These two are **not** independently
  parallelizable, in either direction.

- **50 (images) is genuinely independent** — it touches `TypstBuilder._track_image()` only and could
  move anywhere in the sequence. It sits after the composition work so the composition phases' RED/
  GREEN evidence is not taken across a concurrent image-path change.

- **51 (docs) after 50** because documentation describes behaviour that must already have landed —
  the same ordering v0.7.1 used placing Phase 45 after Phase 44.

- **52 last and prep-only**, per binding constraint #3.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 47. Two-Layer Output — Content/Wrapper Split, Target-as-Path, Collision Detection | v0.8.0 | 14/14 | Complete    | 2026-08-12 |
| 48. Compile-Time Cross-Reference Guard | v0.8.0 | 7/7 | Complete    | 2026-08-14 |
| 49. Per-Master Include Graph with State-Guarded Includes | v0.8.0 | 6/6 | Complete    | 2026-08-14 |
| 50. PR #131 Image Path Defects | v0.8.0 | 3/3 | Complete    | 2026-08-14 |
| 51. Two-Layer Output Documentation | v0.8.0 | 0/TBD | Not started | - |
| 52. v0.8.0 Release Prep (prep-only) | v0.8.0 | 0/TBD | Not started | - |

Phases 1–46 shipped across v0.4.4 → v0.7.1; their per-phase plan counts, statuses and completion
dates are preserved in each milestone's archived roadmap under `milestones/`.

## Roadmap Evolution

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
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25), v0.6.4 (2026-07-28), v0.6.5 (2026-07-29), v0.7.0 (2026-08-04), v0.7.1 (2026-08-11) · v0.8.0 roadmap created 2026-08-11. Per-milestone phase detail, success criteria, and decisions for shipped milestones live in `milestones/vX.Y-ROADMAP.md`.*
