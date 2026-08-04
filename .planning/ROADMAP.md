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
- 🚧 **v0.7.1 — bug-fix round** — Phases 43–46 (active, started 2026-08-04)

**Active milestone: v0.7.1 — bug-fix round.** Four phases (43–46): the two table defects Phase 42's
own review filed, the `typst_documents` first-run onboarding break plus the builder-input hardening
that sits in the same method, documentation currency and the carried hygiene todos, then prep-only
release. Phase numbering continues from v0.7.0's last phase (42), so v0.7.1 starts at **Phase 43**.

## Phases

**Phase Numbering:**

- Integer phases (43, 44, …): Planned milestone work
- Decimal phases (43.1, 43.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.7.0 ran Phases 36–42, so v0.7.1 starts at **Phase 43**.

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

## 🚧 v0.7.1 — bug-fix round (ACTIVE)

**Milestone Goal:** Close, in one cycle, everything v0.7.0 left owed — its single unmet requirement
(REL-04), the two table defects its own reviews filed, the first-run onboarding break recorded as
SEED-001, the documentation changelog page frozen at 0.4.0, and the four small carried todos — so
the next release starts from a clean ledger. This is a maintenance round over already-diagnosed
defects, not a feature cycle: every requirement below closes something already known to be broken,
and each carries a file/line-level todo or a measured basis.

**Binding constraints this roadmap is built on** (settled owner decisions and standing invariants,
not open questions):

1. **Push the milestone branch to `origin` from the FIRST phase, not at the release PR**
   (milestone invariant #5, new this milestone). Both defects that surfaced at the v0.7.0 close —
   REL-04's `create-release` failure and a Windows cp1252 test failure — share the single cause that
   the milestone branch was never pushed until the release PR, so neither Windows CI nor a real tag
   push ran against it during any of the eight phases. Phase 43 carries this as SC#5; every later
   phase inherits it as a standing expectation (CI runs on every push from that point on).

2. **REL-04 cannot be discharged inside a phase.** Its acceptance evidence — a real tag push whose
   `create-release` job runs to completion — is generated by the publish step, which happens *after*
   Phase 46. Phase 46 owns REL-04's in-phase share (verifying the already-on-`main` workflow fix and
   exercising the extractor against the new `## [0.7.1]` section) plus an explicit handoff item.
   **REL-04 closes at `/gsd-complete-milestone`, or carries again.** Reporting it complete on the
   strength of the workflow file being correct is the precise error v0.7.0 made.

3. **The final phase (46) is prep-only and takes zero irreversible action.** It bumps
   `pyproject.toml` + `uv.lock` + `README.md`, writes the curated `## [0.7.1]` CHANGELOG entry, proves
   the post-bump tree green, and hands off a checklist. No tag, no push to PyPI. This is the standing
   v0.5.0 Phase 10 pattern under `branching_strategy: milestone`; the publish executes at
   `/gsd-complete-milestone`.

4. **GATE-01 (standing since v0.6.0):** every node-handler change ships a real
   `sphinx-build → typst.compile()` regression fixture, recorded **red against the unfixed code**
   before it is accepted as green. TBL-04 and TBL-05 both fail observably today, so the classic RED
   (a `TypstError`, or a measurably wrong emitted structure) is available for them — v0.7.0's
   structural-assertion amendment applied only to defects that already compiled cleanly.

5. **Standing invariants carried forward:** zero new runtime dependencies; the `@preview` package
   count stays at **four** with no new version-lockstep site (`writer.py` / `template_engine.py` /
   `templates/base.typ` plus `examples/**/*.typ`, guarded by `tests/test_preview_version_sync.py`);
   "anywhere under X" success criteria are checked by a repo-wide grep at discovery time, never
   against the files a requirement happens to name.

6. **Typing-import modernization is forbidden this milestone** — `CLAUDE.md` instructs "don't
   modernize typing imports until that todo lands", and the todo is not in scope. Neither is
   `add-sphinx-linkcheck-ci-job` (Future requirement LNK-01). Neither may be picked up
   opportunistically while touching an adjacent file.

**Not a frontend UI milestone** (standing project note): every phase below is translator, builder,
config, documentation, and CI work. `ui.plan-gate` false-positives on "layout"/"page"/"render"/
"table" wording here — no phase carries a UI hint, and `/gsd-ui-phase` is not applicable.

- [ ] **Phase 43: Table State Correctness — Nested Tables + Empty-Title Anchors** - A table nested in a `list-table` cell no longer replaces the outer table's body, a figure nested in a figure no longer drops the outer caption (FIG-01, added 2026-08-04), and a captioned table whose title renders empty still anchors its ids
- [ ] **Phase 44: `typst_documents` Default Derivation + Builder Input Hardening** - Following the Quick Start exactly produces a PDF instead of zero output, and a malformed docname fails with an actionable typsphinx error
- [ ] **Phase 45: Documentation Currency + Carried Hygiene** - The README explains `typst_documents` and its new default, the published changelog page stops being two years stale, and the two remaining code/planning hygiene todos close
- [ ] **Phase 46: v0.7.1 Release Prep (prep-only)** - The v0.7.1 tree is bumped, its CHANGELOG curated (calling out the output-filename change), proven green, and handed off with no irreversible action taken

## Phase Details

### Phase 43: Table State Correctness — Nested Tables + Empty-Title Anchors

**Goal**: A document whose tables nest, or whose table caption renders to nothing, produces the
table the source describes. Today a table nested inside a `list-table` cell silently replaces the
enclosing table's body under the enclosing table's caption (the translator's table state is a set of
scalars with no notion of *which* table is being filled), and a captioned table whose title renders
to an empty string anchors its ids on neither path, leaving a surviving `:ref:`/`:numref:` dangling.
Both are pre-existing and both fail observably today, so both keep the classic GATE-01 RED. The
third item is the stale `_emit_id_anchors` docstring that sits in the same file, next to the same
code: it has claimed `depart_figure` is the sole `skip_ids` user since Phase 25, and Phase 42 made
that actively misleading by adding `depart_table` as a second caller.
**Depends on**: Nothing (first phase of the milestone)
**Requirements**: TBL-04, TBL-05, FIG-01, QUA-01
**Success Criteria** (what must be TRUE):

  1. A document containing a `list-table` with a table nested inside one of its cells compiles to a
     PDF in which **both** tables appear correctly — the outer table's own accumulated cells, column
     count, column widths and caption survive the inner table's visit and departure, and the inner
     table renders inside its own cell. Proven by a real `sphinx-build → typst.compile()` fixture
     recorded RED against the unfixed translator before the fix lands (GATE-01).

  2. A captioned table whose title renders to an empty or whitespace-only string emits its id
     anchors, so a `:ref:`/`:numref:` pointing at that table resolves instead of leaving a dangling
     label — proven on the same recorded-RED gate, with the dangling-label failure reproduced first.
     **Axis decided 2026-08-04 (Phase 43 discussion, D-05) by measuring Sphinx's own LaTeX builder
     on the identical input:** id anchoring is made independent of the captioned decision, exactly
     as LaTeX does it (empty-rendered caption → no `\sphinxcaption`, no table number, but
     `\phantomsection\label{...}` still emitted, no warning). So `depart_table` keeps its
     truthiness check for *rendering* — an empty-rendered caption stays a bare `table(...)`, is not
     figure-wrapped, and consumes no table number — while the id anchors are emitted on that path
     too. The two checks are therefore allowed to keep disagreeing about "captioned"; what must no
     longer be true is that a table's ids go unanchored on either path.

  3. `_emit_id_anchors`'s docstring names its actual callers, verified by a repo-wide grep for its
     call sites rather than by trusting the docstring — no surviving claim that `depart_figure` is
     the sole `skip_ids` user.

  4. No collateral change to existing output: the full pytest suite, `black`/`ruff`/`mypy`, and the
     full-corpus `-b typstpdf` gate are green, and documents containing neither a nested table, nor a
     nested figure, nor an empty-titled caption emit byte-identical `.typ` across the change.
     **Corpus decided 2026-08-04 (D-04):** the `42-GATE-EVIDENCE-05.md` two-build method (old tree
     exported with `git archive`, `typsphinx.__file__` asserted to point into it, plus a positive
     control) is run over **all of `docs/source` and every root under `tests/roots`** — the figure
     path is in scope this phase, so existing figure-bearing documents must be covered too, not only
     table-bearing ones.

  5. The milestone branch is on `origin` and CI has run against it — pushed during this phase, not
     at the release PR (milestone invariant #5). Evidence: a `git ls-remote --heads origin` hit for
     the milestone branch plus at least one completed CI run on it including the Windows lanes.

  6. **(FIG-01 — added 2026-08-04 by owner decision during phase discussion; appended rather than
     inserted so criteria 1-5 keep their numbers, which milestone invariant #5 and prior artifacts
     already cite.)** A document with a figure nested inside another figure compiles to a PDF in
     which **both** figures appear correctly: the outer figure's caption, its ids and its state all
     survive the inner figure's visit and departure, and the inner figure renders inside the outer
     figure's legend. `sphinx-build` emits no `unknown node type: <legend>` warning. Proven on a
     recorded-RED fixture, structural over the emitted `.typ` plus PDF text (today's output drops
     the outer caption entirely — measured 2026-08-04). Sphinx's own LaTeX builder is the reference
     behaviour for the same input (outer `\caption{...}\label{...}` survives; the inner figure is
     emitted inside a `sphinxlegend` environment; no warning).
**Plans**: 4/5 plans executed

Plans:
**Wave 1**

- [x] 43-01-PLAN.md — TBL-04: nested-table container state (tracer + shape/depth/header-cell expansion)
- [x] 43-02-PLAN.md — SC#5: push the milestone branch to `origin` and start CI (developer-confirmed)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 43-03-PLAN.md — FIG-01: `legend` node handler + figure-state save/restore across nesting

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 43-04-PLAN.md — TBL-05: id anchoring independent of rendered-caption truthiness; QUA-01 docstring

**Wave 4** *(blocked on Wave 3 completion)*

- [ ] 43-05-PLAN.md — SC#4 two-build byte invariance; SC#5 completed CI run + Phase 44 handoff

### Phase 44: `typst_documents` Default Derivation + Builder Input Hardening

**Goal**: A user who follows the Quick Start exactly gets a PDF. Today `typst_documents` defaults to
`[]` and `TypstPDFBuilder.finish()` returns early on it, so `sphinx-build -b typstpdf` exits 0, emits
one `WARNING`, and produces **zero PDFs**. Sphinx's own LaTeX builder does not require
`latex_documents` — it registers a callable default (measured live against Sphinx 9.1.0 with an empty
`conf.py`) — and typsphinx follows that precedent, deriving from `root_doc`/`project`/`author` with
the target name in LaTeX's own shape, `<project>.typ`. The accepted cost, stated by the owner and
owed to the CHANGELOG: for a user who has never set `typst_documents` this **renames** the existing
`-b typst` output. BLD-01 is grouped here rather than split out because it hardens the *same method*
the derivation touches — the change is made once, in one place, with one set of tests.
**Depends on**: Phase 43
**Requirements**: CONF-08, BLD-01
**Success Criteria** (what must be TRUE):

  1. A Sphinx project whose `conf.py` never mentions `typst_documents`, built with
     `sphinx-build -b typstpdf`, produces a PDF — measured on a real build, with the emitted target
     named from `make_filename_from_project(project)` (the `<project>.typ` → `<project>.pdf` shape)
     and the "no master documents" warning gone.

  2. An explicitly-set `typst_documents` always wins: the derived default never overrides, merges
     with, or reorders an explicit setting — proven by a build with an explicit single-entry
     `typst_documents` producing exactly the targets it names and nothing else.

  3. A non-`str` docname reaching `TypstPDFBuilder.finish()` fails with an actionable
     typsphinx-level error that names the offending value, rather than a raw `TypeError` escaping
     from `path.dirname()`.

  4. The output-filename rename is **measured, not assumed**: a before/after build of the same
     no-`typst_documents` project records the exact old and new filenames, and that measured pair is
     handed to Phase 46 as the source text for the CHANGELOG's user-visible-change callout.

  5. Every existing test that encoded the old `[]`-default behaviour is updated deliberately (each
     change traceable to this requirement rather than absorbed silently), and the full suite,
     `black`/`ruff`/`mypy`, and the full-corpus `-b typstpdf` gate are green.
**Plans**: TBD

### Phase 45: Documentation Currency + Carried Hygiene

**Goal**: What the project tells a reader matches what it now does, and the small carried todos stop
being carried. The README Quick Start must describe the behaviour Phase 44 actually shipped — which
is why this phase follows it rather than preceding it. The published changelog page
(`docs/source/changelog.rst`) is frozen at 0.4.0 with a "(Current)" marker on it and 12 releases
missing (0.4.4 through 0.7.0). The two remaining hygiene items ride along because they are small,
independent, and touch files nothing else in this milestone touches: `derive_typst_lang()`'s
verbatim-duplicated rejection warning in `template_engine.py`, and the unterminated HTML comments in
`.planning/PROJECT.md` (a planning-record edit with no code bearing).
**Depends on**: Phase 44 (DOC-11 documents CONF-08's landed, measured behaviour)
**Requirements**: DOC-11, DOC-12, QUA-02, QUA-03
**Success Criteria** (what must be TRUE):

  1. A reader following the README Quick Start exactly is not surprised by the output: it states what
     `typst_documents` does, when it must be set, the derived default including the `<project>.typ`
     name shape, that an explicit setting overrides the default, and which documents become PDFs —
     each statement checked against a real build of the Quick Start's own steps, not against the
     requirement text.

  2. The published changelog page carries every release from 0.4.4 through 0.7.0 (the 12 currently
     missing), no stale "(Current)" marker sits on 0.4.0, and both `tox -e docs-html` and
     `tox -e docs-pdf` build the page clean. *The `0.7.1` entry itself lands in Phase 46, in the same
     lockstep edit as `CHANGELOG.md` — DOC-12's mechanism must make that a one-line addition rather
     than a re-derivation.*

  3. `derive_typst_lang()` emits its rejection-path warning from exactly one site (verified by a grep
     over the function's branches), and a build over the existing `lang` test corpus produces
     warning-for-warning identical output to the pre-refactor baseline.

  4. `.planning/PROJECT.md` contains zero unterminated `<!--` — every opener in the file is closed,
     checked by scanning the whole file rather than only the two known sites in the archived-footer
     tail, so no downstream reader silently swallows the remainder.

  5. The full pytest suite and `black`/`ruff`/`mypy` are green, and no `typsphinx/` behaviour changed
     beyond QUA-02's single-site warning refactor.
**Plans**: TBD

### Phase 46: v0.7.1 Release Prep (prep-only)

**Goal**: The v0.7.1 tree is ready to publish and proven green, with **zero irreversible action
taken** — no tag, nothing pushed to PyPI, no GitHub Release. This is the standing prep-only Release
phase (the v0.5.0 Phase 10 pattern under `branching_strategy: milestone`): bump, curate, prove, hand
off. The publish half — merge → tag → `release.yml` → PyPI + GitHub Release, plus the standing second
tag on `typsphinx-doc-translations` — executes at `/gsd-complete-milestone`.

**REL-04 is deliberately scoped here as prep-plus-handoff, and does not close in this phase.** Its
acceptance evidence is a real tag push whose `create-release` job runs to completion, which only the
publish can generate. The workflow fix (the missing `astral-sh/setup-uv` / `Set up Python` steps) is
already on `main`; what is owed is the exercise. v0.7.0 reported this requirement's mechanism as done
and the release then failed — this phase must not repeat that. REL-04 closes at
`/gsd-complete-milestone`, or carries forward again.
**Depends on**: Phase 45
**Requirements**: REL-06, REL-04
**Success Criteria** (what must be TRUE):

  1. `pyproject.toml` is the sole `0.7.1` version literal, with `uv.lock` and `README.md` moved in
     lockstep and the editable-install metadata regenerated so `typsphinx.__version__` reports
     `0.7.1`; all three version-sync guard tests stay green.

  2. `CHANGELOG.md` carries a curated `## [0.7.1]` entry covering every v1 requirement this milestone
     delivered, which **explicitly calls out CONF-08's output-filename change** (using Phase 44's
     measured before/after filenames) as a user-visible behavioural change inside a patch release;
     the tail link block advances (new tag link + `Unreleased` compare); and `docs/source/changelog.rst`
     gains the matching `0.7.1` entry in the same edit, so DOC-12's page is current at the tag.

  3. The post-bump tree is proven green **live**, not inherited: full pytest, `black`/`ruff`/`mypy`,
     the full-corpus `-b typstpdf` gate, and both docs builds (`docs-html`, `docs-pdf`), with the
     milestone invariants (zero new runtime dependencies; `@preview` count still four with no new
     lockstep site) asserted mechanically over the SHA-anchored full milestone diff.

  4. REL-04's in-phase share is discharged and its remainder is explicitly owed: `release.yml`'s
     `create-release` job is verified on `main` to carry the `astral-sh/setup-uv` + `Set up Python`
     steps ahead of its `uv run python scripts/extract_changelog_section.py` call, and the extractor
     is run against the new `## [0.7.1]` section producing the intended release-body text. Both facts
     are recorded as *preconditions*, not as acceptance — the phase's own artifacts state that
     **REL-04 remains open until a real tag push runs `create-release` to completion**.

  5. No irreversible action was taken: `git tag -l v0.7.1` and `git ls-remote --tags origin v0.7.1`
     are both empty at phase end, and a standalone handoff checklist exists for
     `/gsd-complete-milestone` covering merge → tag → `release.yml` (with an explicit item to observe
     `create-release` succeed, closing REL-04) → PyPI + GitHub Release → the second tag on
     `typsphinx-doc-translations` → the RTD `stable` measurement on both projects.
**Plans**: TBD

## Progress

**Execution Order:**
Active milestone phases execute in numeric order (decimal insertions between their surrounding
integers), with the prep-only Release phase last so its CHANGELOG entry describes work already
proven by the preceding phases' gates.

**v0.7.1 (active)** runs 43 → 44 → 45 → 46. The chain is genuinely sequential, not merely numbered:
Phase 44 hardens the same `TypstPDFBuilder.finish()` method its own derivation rewrites, Phase 45's
README work documents behaviour that must already have landed in Phase 44, and Phase 46's CHANGELOG
describes all three. Phase 43 goes first because it carries milestone invariant #5 — the milestone
branch reaches `origin` there, so the remaining three phases run with CI (including the Windows
lanes) watching every push.

**v0.7.0 (shipped)** ran 36 → 37 → 38 → 39 → 40 → **40.1** → 41 → **42**. Phase 40 (citations) was
structurally independent of the 37 → 38 → 39 dependency chain. Phase 40.1 was inserted 2026-08-02
ahead of 41 because Phase 41's SC#4 sweep had to cover 40.1's node-handler changes. Phase 42 was
promoted out of the backlog on 2026-08-03 after Phase 41 had already completed, so it ran **after**
the release-prep phase — the one place this ordering rule is broken — and carried the reconciliation
(CHANGELOG entry + invariant sweep) Phase 41 would otherwise have owned.

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
| 36. Shared-Emission Seam Cleanup | v0.7.0 | 4/4 | Complete    | 2026-08-01 |
| 37. Signature Typography — the `desc_*` Family | v0.7.0 | 9/9 | Complete    | 2026-08-01 |
| 38. Structural Indentation + Info Fields | v0.7.0 | 9/9 | Complete    | 2026-08-02 |
| 39. Admonition Taxonomy + Rubric Nesting | v0.7.0 | 13/13 | Complete    | 2026-08-02 |
| 40. Citations — Full Round Trip | v0.7.0 | 5/5 | Complete    | 2026-08-02 |
| 40.1 Citation Degradation Hardening (INSERTED) | v0.7.0 | 4/4 | Complete    | 2026-08-02 |
| 41. v0.7.0 Release Automation + Release Prep | v0.7.0 | 7/7 | Complete    | 2026-08-03 |
| 42. Captioned Table Drops Preceding Target Label | v0.7.0 | 6/6 | Complete    | 2026-08-04 |
| 43. Table State Correctness — Nested Tables + Empty-Title Anchors | v0.7.1 | 4/5 | In Progress|  |
| 44. `typst_documents` Default Derivation + Builder Input Hardening | v0.7.1 | 0/TBD | Not started | - |
| 45. Documentation Currency + Carried Hygiene | v0.7.1 | 0/TBD | Not started | - |
| 46. v0.7.1 Release Prep (prep-only) | v0.7.1 | 0/TBD | Not started | - |

## Roadmap Evolution

One-bullet-per-amendment record of in-place corrections to this file, mirrored in STATE.md's
own "Roadmap Evolution" log. This section did not exist before 2026-08-02; it is created here to
hold the first ROADMAP.md-native entry (STATE.md's mirror already carried the Phase 36 SC#3
precedent this entry follows).

- **2026-08-02** — Phase 39's SC#1 corrected after UAT gap `G-39-1` reversed `39-CONTEXT.md` D-03
  by owner decision (`D-03-R`): the clause asserting `attention` sits in the same bucket as
  `danger`/`error` is superseded, since the red group is now three distinct clue functions
  (`danger`/`memo`/`error`) rather than one. The surviving requirement is that `attention` leaves
  the orange warning group for the red family. No requirement was added, removed, or re-assigned
  to a different phase.

- **2026-08-02** — Phase 40's SC#3 and Goal paragraph corrected from an unqualified "every citing
  location"/"every citing site" back-reference claim to the same-document scope
  `40-CONTEXT.md` D-08 established (recorded as D-09): docutils populates a citation definition's
  own `backrefs` with same-document citing sites only, measured against a real two-document build,
  and Sphinx's own HTML builder has the identical limitation (Sphinx's LaTeX builder renders no
  back-references at all). A cross-document citing site still resolves a working forward link, it
  simply gets no back-reference. No requirement was added, removed, or re-assigned to a different
  phase.

- **2026-08-03** — Backlog item **999.2** promoted into v0.7.0 as **Phase 42** at
  `/gsd-review-backlog`, by owner decision, *after* Phase 41 had already completed. This is the
  first amendment in this project's history that **adds a requirement to an already-complete
  milestone**: v0.7.0 goes from 7/7 to 7/8, the milestone line becomes Phases 36–42, and new
  requirement **TBL-03** is added to `REQUIREMENTS.md` (v1 total 32 → 33). The owner also decided
  the v0.7.0 publish **blocks on Phase 42** rather than shipping first and deferring the fix, so
  `/gsd-complete-milestone` no longer runs next. Phase 42's SC#6 carries the resulting
  reconciliation debt — Phase 41's CHANGELOG entry (SC#2) and invariant sweep (SC#4) were both
  measured against a tree that predates Phase 42. Nothing was removed or re-assigned away from
  another phase.

- **2026-08-04** — v0.7.0 closed and archived; **v0.7.1 roadmap created: Phases 43–46**, 11/11 v1
  requirements mapped, zero orphans. Derived from this milestone's REQUIREMENTS.md alone — research
  was deliberately skipped (owner decision 2026-08-04: a maintenance round over already-diagnosed
  defects, each carrying a file/line-level todo, with the one new-behaviour item CONF-08 resolved by
  direct measurement of Sphinx 9.1.0's LaTeX builder), so there is no `research/SUMMARY.md` for this
  milestone. Four pending todos and one dormant seed were promoted into requirements
  (`nested-table-clobbers-outer-table-state` → TBL-04, `table-whitespace-only-title-anchor-divergence`
  → TBL-05, `emit-id-anchors-docstring-claims-depart-figure-is-sole-skip-ids-user` → QUA-01,
  `non-str-docname-typeerror-in-typstpdf-finish` → BLD-01,
  `derive-typst-lang-duplicated-warning-block` → QUA-02,
  `project-md-unterminated-html-comments` → QUA-03,
  `docs-changelog-page-stale-at-0-4-0` → DOC-12, SEED-001 → CONF-08 + DOC-11), and
  `release-create-job-missing-uv-verify-end-to-end` remains an open requirement (REL-04) rather than
  a todo. **Milestone invariant #5 is new**: the milestone branch is pushed to `origin` from Phase 43
  rather than at the release PR, because both defects that surfaced at the v0.7.0 close share the
  cause that it never was.

- **2026-08-04** — **Phase 43 discussion amends Phase 43** (owner decision, `/gsd-discuss-phase 43`).
  New requirement **FIG-01** (a figure nested in a figure keeps the outer caption, ids and state)
  is added to `REQUIREMENTS.md` and mapped to Phase 43; v0.7.1 coverage goes 11/11 → **12/12**,
  still zero orphans. Phase 43 gains **SC#6** — appended, not inserted, so criteria 1-5 keep the
  numbers that milestone invariant #5 and prior artifacts cite. Two existing criteria were amended
  in place: **SC#2** now names the axis chosen for TBL-05 (id anchoring made independent of the
  captioned decision, matching Sphinx's LaTeX builder measured on the identical input — empty-
  rendered caption gets no caption line and no table number, but still gets its labels, and no
  warning), and **SC#4** widens the byte-invariance corpus to all of `docs/source` plus every root
  under `tests/roots` because the figure path is now in scope. The milestone's "no new node
  handlers" out-of-scope row keeps one stated exception: FIG-01's `legend` handler, admitted as the
  repair path for measured silent data loss rather than as new capability. Nothing was removed or
  re-assigned away from another phase.

## Backlog

Candidate work not yet scoped into a milestone. Promote items with `/gsd-review-backlog`, or
pull a whole cluster into the next milestone via `/gsd-new-milestone`.
Numbered 999.x so milestone reorganization never renumbers or drops them.

New items land here as `999.x` entries. **No item is open** — the backlog is empty as of 2026-08-04.
Item **999.1** (inline math after text: missing separator before `#mi()` causes a Typst error) was
promoted into v0.6.5 as Phase 34 / requirement MATH-01 and **shipped in v0.6.5** (2026-07-29). Item
**999.2** (a captioned table drops the id of an immediately preceding standalone target) was promoted
into v0.7.0 as **Phase 42 / requirement TBL-03** on 2026-08-03 and shipped in v0.7.0. Numbering does
not reuse retired numbers, so the next item filed here is **999.3** — this keeps each promoted item's
original number unambiguous. Three earlier pending todos were promoted into v0.6.4 (Phases 29–33):
`move-documentation-hosting-to-read-the-docs`, `github-io-doc-links-404-missing-en-prefix`, and
`docs-usage-installation-orphan-class`. `add-sphinx-linkcheck-ci-job` stays **open and deferred** —
sphinx linkcheck is out of scope as Future requirement LNK-01 (it structurally cannot see
`README.md` / `pyproject.toml`, where the dead links actually live); v0.6.4 CI-05's repo-wide
real-HTTP check covers that class instead.

**Pending todos and seeds promoted into v0.7.1** (2026-08-04):

- `nested-table-clobbers-outer-table-state` → Phase 43 (TBL-04)
- `table-whitespace-only-title-anchor-divergence` → Phase 43 (TBL-05)
- `emit-id-anchors-docstring-claims-depart-figure-is-sole-skip-ids-user` → Phase 43 (QUA-01)
- `non-str-docname-typeerror-in-typstpdf-finish` → Phase 44 (BLD-01)
- `SEED-001-readme-quickstart-typst-documents-pdf` → Phase 44 (CONF-08) + Phase 45 (DOC-11)
- `docs-changelog-page-stale-at-0-4-0` → Phase 45 (DOC-12)
- `derive-typst-lang-duplicated-warning-block` → Phase 45 (QUA-02)
- `project-md-unterminated-html-comments` → Phase 45 (QUA-03)
- `release-create-job-missing-uv-verify-end-to-end` → Phase 46 (REL-04) — carried as an **open
  requirement**, not merely a todo; it closes at the publish, not in the phase.

Each todo record stays **pending** until its phase executes; the todo is the detail record, the
phase entry above is the sequencing record.

**Still open and deferred** (1, see STATE.md Deferred Items):
`modernize-typing-imports-drop-up006-up035-ignore` — deferred *doubly deliberately*, since
`CLAUDE.md` independently instructs "don't modernize typing imports until that todo lands". Plus
`add-sphinx-linkcheck-ci-job`, which is tracked as Future requirement LNK-01 rather than as
milestone-candidate work.

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25), v0.6.4 (2026-07-28), v0.6.5 (2026-07-29), v0.7.0 (2026-08-04). v0.7.1 phases added 2026-08-04. Per-milestone phase detail, success criteria, and decisions for shipped milestones live in `milestones/vX.Y-ROADMAP.md`.*
