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

**No active milestone.** v0.7.1 shipped 2026-08-11 (PyPI `typsphinx 0.7.1`, release run
`31462027486`, tag `v0.7.1` on merge commit `48bf135`) with 19/19 v1 requirements complete and zero
known gaps — REL-04, carried unmet from v0.7.0, closed here on generated evidence. Start the next
milestone with `/gsd-new-milestone`, which defines a fresh `REQUIREMENTS.md`.

Phase numbering is **continuous across milestones** — v0.7.1 ran Phases 43–46, so the next milestone
starts at **Phase 47**.

## Phases

**Phase Numbering:**

- Integer phases (47, 48, …): Planned milestone work
- Decimal phases (47.1, 47.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.7.1 ran Phases 43–46, so the next milestone starts at **Phase 47**.

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

**Todos and seeds promoted into v0.7.1** (2026-08-04) — **all shipped 2026-08-11**:

- `nested-table-clobbers-outer-table-state` → Phase 43 (TBL-04)
- `table-whitespace-only-title-anchor-divergence` → Phase 43 (TBL-05)
- `emit-id-anchors-docstring-claims-depart-figure-is-sole-skip-ids-user` → Phase 43 (QUA-01)
- `non-str-docname-typeerror-in-typstpdf-finish` → Phase 44 (BLD-01)
- `toctree-heading-offset-ignored-because-visit-title-emits-abs` → Phase 44.1 (TOC-01) — filed and
  promoted 2026-08-04, after the roadmap was created; the phase was inserted rather than folded into
  an existing one.

- `typst-documents-title-author-elements-ignored` → Phase 44.2 (CONF-09) — promoted 2026-08-04 by
  owner decision **reversing Phase 44's D-02**, which had placed it outside v0.7.1. See the Roadmap
  Evolution entry for what changed.

- `documented-custom-template-parameter-contract-is-wrong-and-t` → Phase 45.1 (DOC-13) — filed and
  promoted 2026-08-04 out of Phase 44.1's `<deferred>` block, after the roadmap was created; the
  phase was inserted rather than folded into Phase 45, because the fix may land in `writer.py` or
  `templates/base.typ` rather than in documentation alone and that route is not yet chosen.

- `SEED-001-readme-quickstart-typst-documents-pdf` → Phase 44 (CONF-08) + Phase 45 (DOC-11)
- `docs-changelog-page-stale-at-0-4-0` → Phase 45 (DOC-12)
- `derive-typst-lang-duplicated-warning-block` → Phase 45 (QUA-02)
- `project-md-unterminated-html-comments` → Phase 45 (QUA-03)
- `release-create-job-missing-uv-verify-end-to-end` → Phase 46 (REL-04) — carried as an **open
  requirement**, not merely a todo; it closes at the publish, not in the phase.

Each todo record stayed **pending** until its phase executed; the todo is the detail record, the
phase entry above is the sequencing record.

**Still open and deferred after the v0.7.1 close** (9 pending todos + 2 dormant seeds, see STATE.md
Deferred Items). Every one was enumerated and argued in `46-HANDOFF.md` § "Deferred by decision, not
oversight" before the close — none is an oversight:

- `modernize-typing-imports-drop-up006-up035-ignore` — deferred *doubly deliberately*, since
  `CLAUDE.md` independently instructs "don't modernize typing imports until that todo lands".
- `add-sphinx-linkcheck-ci-job` — tracked as Future requirement LNK-01, not milestone-candidate work;
  `links.yml`'s repo-wide lychee check already covers the links each release adds.
- **Three `typst_documents`-modelling defects**, a cluster worth promoting together:
  `duplicate-typst-documents-target-silently-drops-a-master` (re-measured live in Phase 46 — still
  reachable, because Phase 44's collision guard compares only against real docnames and the reserved
  `_template`, never against already-resolved `typst_documents` targets),
  `a-master-that-is-also-a-toctree-child-is-unrepresentable`, and
  `shared-document-silently-dropped-from-all-but-first-master`.
- **Two `TypstBuilder._track_image()` defects that ship in v0.7.1 unfixed** by owner decision D-27:
  `rehomed-converted-image-collides-with-srcdir-images-dir` (major — silent wrong picture, a
  regression in failure mode from a loud abort) and
  `track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri` (minor).
- `release-create-job-missing-uv-verify-end-to-end` — **this was REL-04, and it closed at the
  v0.7.1 publish**; the record can be filed to `todos/completed/`.
- `ruff-generic-linux-elf-unrunnable-on-nixos` — a `flake.nix`-side toolchain repair in the same
  family as QUA-04; CI holds lint authority, so it blocks nothing.
- Dormant seeds: `SEED-001-readme-quickstart-typst-documents-pdf` (substantially discharged by
  CONF-08 + DOC-11) and `SEED-003-tox-dependency-groups-per-env` (PEP 735 `[dependency-groups]`).

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25), v0.6.4 (2026-07-28), v0.6.5 (2026-07-29), v0.7.0 (2026-08-04), v0.7.1 (2026-08-11). Per-milestone phase detail, success criteria, and decisions for shipped milestones live in `milestones/vX.Y-ROADMAP.md`.*
