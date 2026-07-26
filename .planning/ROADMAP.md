# Roadmap: typsphinx

## Milestones

- ✅ **v0.4.4 — CI-repair + modernize** — Phases 1–5 (shipped 2026-07-05) → [archive](milestones/v0.4.4-ROADMAP.md)
- ✅ **v0.5.0 — forward-ecosystem** — Phases 6–10 + 8.1 (shipped 2026-07-11) → [archive](milestones/v0.5.0-ROADMAP.md)
- ✅ **v0.6.0 — real-world robustness** — Phases 11–15 (shipped 2026-07-13) → [archive](milestones/v0.6.0-ROADMAP.md)
- ✅ **v0.6.1 — rendering fidelity** — Phases 16–18 (shipped 2026-07-19) → [archive](milestones/v0.6.1-ROADMAP.md)
- ✅ **v0.6.2 — rendering fidelity round 2** — Phases 19–23 (+22.1–22.4) (shipped 2026-07-23) → [archive](milestones/v0.6.2-ROADMAP.md)
- ✅ **v0.6.3 — config & docs 実測整合 + captioned tables** — Phases 24–28 (+27.1) (shipped 2026-07-25) → [archive](milestones/v0.6.3-ROADMAP.md)
- 🚧 **v0.6.4 — Read the Docs migration** — Phases 29–33 (in progress, scoped 2026-07-25)

**Active milestone: v0.6.4 — Read the Docs migration.** 13 v1 requirements across 6 phases (29–33,
incl. the inserted 30.1).
Phase numbering continues from v0.6.3's last phase (28). Next: `/gsd-plan-phase 29`.

## Phases

**Phase Numbering:**

- Integer phases (29, 30, 31): Planned milestone work
- Decimal phases (29.1, 29.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.6.4 continues from v0.6.3's last phase (28), so it starts at Phase 29.

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
- [x] Phase 22.4: README 記述の実測乖離解消 (INSERTED) (3/3 plans) — completed 2026-07-23
- [x] Phase 23: v0.6.2 Release Prep + Regression-Gate Close (3/3 plans) — completed 2026-07-23

</details>

<details>
<summary>✅ v0.6.3 — config & docs 実測整合 + captioned tables (Phases 24–28, +27.1) — SHIPPED 2026-07-25</summary>

Closed the gap between what the docs promised and what the build actually did. Three tracks: the
dead-config sweep round 2 — deleted the inert `typst_toctree_defaults` (CONF-05) and implemented the
`typst_elements` `papersize`/`fontsize` pass-through behind a curated allowlist that fails loudly on an
unknown key instead of silently dropping it (CONF-04); the reimplementation of external PR#98 so a
captioned `.. table::` renders as `figure(table(...), caption, kind: table)` with native "Table N"
numbering and resolvable `:numref:`/`:ref:` (TBL-01/TBL-02), fixing a stale-cell-buffer bug that had
been silently eating the second table's caption; and docs 実測整合 — the unreachable orphan
`docs/configuration.rst` deleted and every phantom `typst_*` name purged so config is documented in one
canonical place (DOC-06/DOC-07). An inserted Phase 27.1 wired Typst's typesetting `lang` to Sphinx's
own `language` conf (CONF-07), so a `language = "ja"` project's captioned tables read 「表 N」 rather
than "Table N" — the one change that amended the milestone's `base.typ`-byte-unchanged invariant, and
only for the two lines that add the `lang` parameter. Phase 28 (prep-only) bumped the version, curated
the CHANGELOG, and closed on the full-corpus regression gate. Full phase detail, success criteria,
decisions, and the GATE-01 evidence are preserved in
[`milestones/v0.6.3-ROADMAP.md`](milestones/v0.6.3-ROADMAP.md).

- [x] Phase 24: Delete `typst_toctree_defaults` (1/1 plan) — completed 2026-07-23
- [x] Phase 25: Captioned Table Figure Wrap + Cross-References (2/2 plans) — completed 2026-07-24
- [x] Phase 26: `typst_elements` papersize/fontsize Pass-Through (2/2 plans) — completed 2026-07-24
- [x] Phase 27: Docs 実測整合 — Orphan Delete + Phantom Names (1/1 plan) — completed 2026-07-24
- [x] Phase 27.1: Typst 組版 lang の Sphinx `language` 連動 (INSERTED) (3/3 plans) — completed 2026-07-25
- [x] Phase 28: v0.6.3 Release Prep + Regression-Gate Close (3/3 plans) — completed 2026-07-25

**Closed at milestone close (not a phase):** the bundled `examples/advanced` sample was found
unbuildable — five `typst_elements` keys outside the CONF-04 allowlist, and `_templates/custom.typ`
three milestones behind on its `@preview` pins (`unknown variable: kai`). Both repaired, the template
now declaring `papersize`/`fontsize`/`lang` so the sample demonstrates the allowlist, and
`test_preview_version_sync.py` extended over `examples/**/*.typ` so a bundled sample can no longer
drift unwatched.

</details>

### 🚧 v0.6.4 — Read the Docs migration (Phases 29–33) — IN PROGRESS

**Milestone goal:** Apply this project's own standard — "what the docs promise is what actually
happens" — to the *publishing* surface: a URL typsphinx publishes must actually resolve, and the PDF a
reader downloads must be the one typsphinx's own `typstpdf` builder produced. Six phases: (1) stand up
the RTD build for the English parent (`.readthedocs.yaml`, the `READTHEDOCS_LANGUAGE` seam in
`conf.py`, the `build.jobs.build.pdf` typstpdf override) and resolve the milestone's one genuinely open
empirical unknown by reading a real build log; (2) the deletion round that removes the hand-rolled
multilang machinery and the unreachable orphan doc pair; (2.1) the Japanese site, built from a
**separate** `typsphinx-doc-translations` repository registered as an RTD translation project — a
model adopted on 2026-07-26, replacing the original re-import-the-same-repository plan; (3) repoint
every published URL at RTD and install a repo-wide link guard that can see the files Sphinx never
scans; (4) the irreversible GitHub Pages teardown, ordered *after* every reversible piece; (5) prep-only
Release.

**Ordering rationale — irreversibility, not convenience.** The research's suggested order put the Pages
teardown *before* the URL rewrite (grouping both `docs.yml` edits together). This roadmap deliberately
**inverts** that: URL cutover (Phase 31) lands while both hosts are still live, so the README/PyPI
links are proven to resolve against RTD before anything is destroyed; only then does Phase 32 cut
Pages. Every reversible action therefore precedes the single action with no undo (deleting the
`gh-pages` branch and the served Pages site — no redirect stubs, owner decision 2026-07-25). CI-04 is
kept as its **own** phase rather than folded into a neighbour precisely so the teardown has a standing
gate in front of it: its first success criterion is a *freshly re-taken* observation that RTD is
serving English HTML, Japanese HTML, and the PDF-or-documented-fallback — not a citation of Phase
29/30's evidence.

**RTD-04 ownership (a deliberate choice, not an oversight).** RTD-04 — "the root URL lands on a version
that exists and serves real content **at every point during the migration**" — is mapped to **Phase
29**, not to the release phase and not split across both. The failure mode is *created* at
project-creation time: RTD's root redirect targets whatever Default Version says even when that version
has no build, and `stable` cannot exist until the `v0.6.4` tag (RTD has refused builds without a
`.readthedocs.yaml` since 2023-09-25, so no earlier tag can ever qualify). The only phase that can
*prevent* it is the one that creates the project, so Phase 29 discharges it by setting Default Version
= `latest` and proving the root resolves with a real HTTP fetch. The invariant then stands for the rest
of the milestone: **Phases 30, 30.1, 31 and 32 each re-fetch the documentation root as part of their own
verification**, and Phase 33 hands the `latest` → `stable` flip to the owner as an explicit post-tag
step. Mapping RTD-04 to Phase 33 would leave the middle of the milestone unowned; splitting it would
break one-requirement-one-phase.

**Two failure modes present as *successful builds*** (REQUIREMENTS.md invariant #7), so their criteria
are content-level, never status-level:

- **I18N-01** — a Japanese RTD project builds green while rendering 100% English. The original cause
  (RTD sets `READTHEDOCS_LANGUAGE`; `conf.py` read only `SPHINX_LANGUAGE`) was closed by Phase 29's
  `_resolve_language()` seam, but the failure mode outlives it: the ja catalogs are only **24.3%**
  translated (257/1058 msgids, measured 2026-07-26), with `api/index`, `contributing`, `changelog`
  and `user_guide/templates` at **zero**. **Phase 30.1's** criterion therefore matches actual
  translated strings in the served HTML *against a docname with full coverage* — probing one of the
  0% files would show all-English on a perfectly healthy site.

- **RTD-02** — Typst substitutes a missing font silently (no error, no warning), so a glyph-wrong PDF
  builds successfully. Phase 29's criterion content-compares the downloaded RTD PDF against the
  `tox -e docs-pdf` baseline for the same commit.

**RTD-03 is a conditional fallback, not a parallel deliverable.** The milestone's #1 empirical unknown
is whether `typst.compile()` can reach `packages.typst.org` from inside RTD's build sandbox — the four
`@preview` packages (mitex / codly / codly-languages / gentle-clues) must be fetched on a cold cache
and **no documentation source resolves RTD's egress policy**. The decision point is "read the raw RTD
build log," and the owner has pre-agreed the fallback (2026-07-25): if the fetch works, RTD-02 is
delivered and RTD-03 is satisfied vacuously; if it is blocked, RTD-02 degrades to HTML-only on RTD
(no regression — the PDF stays a `tox -e docs-pdf` CI artifact + tag-time Release asset) and RTD-03's
`releases/latest/download/` link path is taken. Phase 29 cannot deadlock on the unknown: both branches
are expressible in its success criteria.

**Two distinct verification bars for links — do not conflate them.** `sphinx-build -b linkcheck` is
**out of scope** (deferred as Future requirement LNK-01, owner decision 2026-07-25): a repo-wide grep
found **zero** `github.io` occurrences under `docs/source/`, so the 7 dead links live only in
`README.md` and `pyproject.toml` — files linkcheck structurally never scans. A green linkcheck job
would manufacture false confidence about exactly the bug class it was added to prevent. **CI-05** is a
repo-wide, real-HTTP link check covering those files, run advisory (`drift.yml` precedent, D-07).
**DOC-09** additionally needs a one-time real HTTP fetch proving each rewritten URL resolves. Phase 31
carries both bars separately, and its first criterion is a recorded **negative control**: the check is
run *before* the rewrite and shown to flag the live dead links.

**Deletion discipline (invariants #4 and #5).** Phase 30 is the milestone's deletion round and carries
both traps this project has already been burned by. (a) `tests/test_documentation_usage.py` and
`tests/test_documentation_installation.py` hard-assert the existence of the files DOC-08 removes — they
go in the **same commit** as their subjects, and the proof is a green full `pytest` run *after* the
deletion, not the deletion commit. (b) `docs/source/installation.rst` is a **live, toctree-reachable**
file, entirely distinct from the root orphan `docs/installation.rst`; it and its `.po` catalog stay
byte-unchanged. (c) I18N-02's deletion set has grown **twice** beyond the milestone brief: research's
grep added `docs/source/_templates/page.html` and `docs/Makefile`'s `multilang`/`serve-multilang`
targets, and Phase 30's discussion (2026-07-26) added `docs/Makefile`'s `html-ja` target (which would
silently render 100% English once the catalogs relocate) and `conf.py`'s `html_static_path` (left
pointing at a directory emptied by the `custom.css` delete) — on top of `build_multilang.py`,
`tox.ini`'s `[testenv:docs-multilang]`, `_templates/language-switcher.html`, `_static/custom.css`
(a **full** delete: all 40 lines are language-switcher CSS) and `conf.py`'s
`html_context`/`html_sidebars` wiring. Per invariant #4 the authoritative list is a **fresh repo-wide
grep at execution time**, not this one. (c2) That grep has two **measured** false positives which must
*survive*: `tests/fixtures/confval_field_body_render_gate/index.rst`'s `.. confval:: html_sidebars`
(an unrelated Sphinx-directive fixture) and `tests/test_readthedocs_config.py`'s four
`html_context["language"]` assertions, which get repointed at the `language` seam rather than deleted.
(d) A deletion-bearing branch trips this project's `worktree.cleanup-wave` deletion guard (Phase 27
precedent, PROJECT.md D-13) — Phase 30 should expect a **manual merge** step. (e) Ordering: Phase 30's
deletions wait on **Phase 30.1** having the replacement observed serving and the `docs/locale/ja/`
catalogs already relocated.

**Milestone invariants (every phase)** — REQUIREMENTS.md § Milestone Invariants: zero new runtime
dependencies; no `@preview` version bump; the now-**four**-surface version-sync guard (`writer.py`,
`template_engine.py`, `templates/base.typ`, `examples/**/*.typ`) untouched; and **no `typsphinx/`
runtime code change at all** — if a phase appears to need one, that is a re-scope signal, not a reason
to widen the diff. `docs/source/conf.py` is docs, not runtime.

**Eight owner-manual steps have no automated acceptance criterion** — seven RTD web-UI actions plus
one GitHub repository creation (REQUIREMENTS.md § Owner-Manual Steps): en project creation
(+ **slug confirmation before creation** — RTD slugs are not self-service changeable), creating the
`typsphinx-doc-translations` repository, a *separate* ja RTD project pointed at **that** repository
with Language=Japanese in **its own** Admin settings,
**linking ja under the en parent's Settings → Translations** (the step most likely to be missed —
creating both projects without linking leaves two working but *unswitchable* sites), independent
version activation on the ja project, the Default Version `latest` → `stable` flip **after** the tag,
disabling the repository's Pages site, and the About → Website field. Phases that depend on these say
so explicitly and carry **no** criterion pretending a test can assert them.

**Verification culture (standing).** Prefer an honest `human_needed` abstention over asserting a truth
without direct evidence, and prefer empirical gates — real builds, real HTTP fetches, real greps, raw
build logs — over string assertions. Every criterion below is phrased so it can only be met with direct
evidence.

**UI note:** no phase in this milestone is frontend UI work. This is docs-hosting / CI / metadata work;
the `ui.plan-gate` false-positives on HTML/PDF/template wording (STATE.md standing note) — use
`--skip-ui` if it flags a phase.

**Ship unit = milestone** (`branching_strategy: milestone`): Phase 33 is prep-only — it bumps
`pyproject.toml` + adds the `CHANGELOG.md` entry and does **not** tag or publish. The irreversible
publish (tag `v0.6.4` → `release.yml` → PyPI + GitHub Release) executes at `/gsd-complete-milestone`
(v0.5.0 Phase 10 / v0.6.2 Phase 23 / v0.6.3 Phase 28 precedent).

- [x] **Phase 29: RTD Build Establishment (English Parent) + PDF Path Decision** - `.readthedocs.yaml` + the `READTHEDOCS_LANGUAGE` seam; the en project observed green from a raw build log (in-repo install, no `latexmk`); the `@preview`-egress unknown resolved either way; root URL owned at Default Version = `latest` (completed 2026-07-26)
- [ ] **Phase 30: Hand-Rolled Multi-Language Machinery & Orphan Removal** - One deletion round removing the multilang machinery (switcher, styling, `conf.py` wiring, `build_multilang.py`, every task-runner target that drove it) + the orphan doc pair with their collateral tests, on a green tree with `docs.yml` still internally consistent (expect a manual merge — deletion guard)
- [ ] **Phase 30.1: Translations Repository + Japanese RTD Site (INSERTED)** - `/ja/latest/` serving real Japanese prose behind RTD's own flyout, built from a separate `typsphinx-doc-translations` repository registered as an RTD translation project, with the submodule pin auto-advanced and the Japanese PDF proven glyph-correct (I18N-03, promoted to v1)
- [ ] **Phase 31: Published-URL Cutover + Repo-Wide Link Guard** - Every published documentation URL repointed at RTD and fetched over real HTTP; an advisory repo-wide link check installed with a recorded pre-rewrite negative control; Issue #119 closed and the About → Website field set
- [ ] **Phase 32: GitHub Pages Teardown (IRREVERSIBLE)** - Behind a freshly re-taken RTD-is-serving gate: the `actions-gh-pages` deploy step and the `gh-pages` branch deleted, no redirect stubs, with `tox -e docs-pdf` and the tag-time PDF Release attachment intact
- [ ] **Phase 33: v0.6.4 Release Prep** - Prep-only: bump 0.6.4 + `uv.lock` + README Status + `CHANGELOG` (incl. the tail link block), assert the milestone invariants over the full diff, hand the post-tag `stable` flip to the owner; publish at `/gsd-complete-milestone`

### Phase 29: RTD Build Establishment (English Parent) + PDF Path Decision

**Goal**: A reader can browse typsphinx's English documentation on Read the Docs, built from this
repository's own commit, and either download a PDF that typsphinx's own `typstpdf` builder produced or
follow a documented, edit-free link to the Release PDF — with the documentation root always landing on a
version that exists.
**Depends on**: Nothing (first phase of the milestone)
**Requirements**: RTD-01, RTD-02, RTD-03, RTD-04
**Success Criteria** (what must be TRUE):

  1. `/en/latest/` on Read the Docs serves this project's real documentation pages, and the **raw build
     log** for that same build shows `typsphinx` installed from the checked-out commit (a local path),
     not resolved from a PyPI index — so the silent variant, where a stale published wheel shadows the
     working tree, fails this criterion.

  2. The raw RTD build log for that build has been read end to end and answers the `@preview` question
     with a recorded log excerpt, not an inference: **either** the four Typst Universe packages resolve
     and the PDF step completes with **zero** `latexmk` / `pdflatex` / `.tex` lines anywhere in the log,
     **or** the registry fetch is shown blocked/failed and that excerpt is the recorded trigger for the
     pre-agreed fallback.

  3. **Branch A (registry reachable):** the PDF downloaded from RTD's own download menu is
     *content*-compared against the `tox -e docs-pdf` baseline for the same commit — page count and
     extracted text agree and no tofu / missing-glyph substitution is present — so a green build that
     silently substituted a font fails this criterion. **Branch B (registry blocked):** RTD serves no
     PDF at all, and the documentation instead links to a `releases/latest/download/` URL, fetched over
     real HTTP and confirmed to return the current release's PDF without any per-release editing.

  4. Fetching the documentation **root** URL over real HTTP (not reading the dashboard setting) lands on
     a version that serves real content, with Default Version deliberately left at `latest`, and the
     `latest` → `stable` flip recorded as an explicit precondition handed to Phase 33.

**Plans**: 6/6 plans executed
each wave waits on an owner-performed RTD action or on the previous commit's build. Plans 05 and 06 are
mutually exclusive branches; exactly one does work and the other records a skip.)

Plans:
**Wave 1**

- [x] 29-01-PLAN.md — D-06 commit 1: HTML-only `.readthedocs.yaml`, the `READTHEDOCS_LANGUAGE` → `SPHINX_LANGUAGE` → `"en"` seam in `conf.py`, and `tests/test_readthedocs_config.py`

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 29-02-PLAN.md — owner creates the en RTD project (slug confirmed first); `/en/latest/` and the documentation root fetched over real HTTP; install-provenance log excerpt and the Phase 33 Default-Version handoff recorded

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 29-03-PLAN.md — D-06 commit 2: `formats: [pdf]` + `build.jobs.build.pdf` + `build.apt_packages: [fonts-noto-cjk]`, proven by a local run of the same command sequence, with the per-commit D-12 baseline recorded

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 29-04-PLAN.md — the PDF build's raw log read end to end; `@preview` verdict recorded verbatim; Branch A / Branch B selected on that evidence

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 29-05-PLAN.md — Branch A only: D-12 content comparison of the RTD-served PDF against the local baseline (pages, text, CJK font coverage), with the tofu look recorded as `human_needed`

**Wave 6** *(blocked on Wave 5 completion)*

- [x] 29-06-PLAN.md — Branch B only: the `releases/latest/download/` fallback fetched over real HTTP and published from both `docs/source/index.rst` and `README.md`, bound by a presence test

**Cross-cutting constraints:**

- No repository source file is modified by this plan — its only output is the evidence record under .planning/

**Owner-manual dependencies (no automated criterion possible):** creating the en RTD project and
connecting GitHub; **confirming the project slug before creation** (RTD slugs are not self-service
changeable — a wrong slug bakes into every URL this milestone is about to publish); setting that
project's Admin Language = English; leaving Default Version = `latest`. Criteria 1–4 verify the
*outcome* of these steps via real fetches and the raw build log; none of them asserts the web-UI action
itself.

**Notes**: `formats: [pdf]` **and** the `build.jobs.build.pdf` override are used **together** —
research settled this against RTD's own config reference (the override *replaces* the default LaTeX step
for that format rather than running alongside it), correcting PITFALLS.md's independent
omit-`formats:` reading. HTML is deliberately **not** overridden; RTD's `sphinx:` key already drives it.
RTD bypasses tox entirely — do not wrap `build.jobs` commands in `tox -e docs-*`. The `conf.py` seam
(`READTHEDOCS_LANGUAGE` → `SPHINX_LANGUAGE` → `"en"`) lands **here**, before the ja project exists, so
ja's very first build resolves correctly instead of needing a second pass; it is a zero-behavior-change
edit locally (both env vars unset → `"en"`, as today). `conf.py` is docs, not runtime — the
no-`typsphinx/`-change invariant holds.

### Phase 30: Hand-Rolled Multi-Language Machinery & Orphan Removal

**Goal**: The repository no longer carries the hand-rolled multi-language publishing machinery or
the unreachable orphan docs it accumulated — the language switcher, its styling, its
`conf.py` wiring, the `build_multilang.py` builder and every task-runner target that drove it are
gone, together with the `docs/usage.rst` / root `docs/installation.rst` pair and the tests that
hard-assert them — while the documentation still builds green and `docs.yml` stays internally
consistent.
**Depends on**: Phase 29 (the `.readthedocs.yaml` + `language` seam must be proven sound before
anything here is deleted) and Phase 30.1 (its Japanese site must be observed serving before the
switcher and the locale tooling are deleted here — the replacement is confirmed working first, and
the `docs/locale/ja/` catalogs must already have been relocated, since this phase removes the
`docs/Makefile` targets that maintain them)
**Requirements**: I18N-02, DOC-08
**Success Criteria** (what must be TRUE):

  1. A **fresh repo-wide grep** run immediately before the deletion commit (not scoped to the files
     the requirement names) returns zero live references to `build_multilang`, `docs-multilang`,
     `serve-multilang`, `html-ja`, `language-switcher`, `page.html`'s `sessionStorage` key,
     `custom.css`, `html_static_path`, and the `html_context` / `html_sidebars` language wiring.
     Excluded from the count by standing precedent: `CHANGELOG.md` and `.planning/**` historical
     entries (D-02/D-10), and two **measured** false positives that must **survive** in the tree —
     `tests/fixtures/confval_field_body_render_gate/index.rst`'s `.. confval:: html_sidebars`
     (an unrelated Sphinx-directive fixture) and `tests/test_readthedocs_config.py`'s
     `html_context` assertions, which are repaired rather than deleted (SC#4).

  2. The `conf.py` surgery is **confined to the switcher wiring**: `html_context`, `html_sidebars`,
     `html_css_files`, and `html_static_path` are gone, while Phase 29's `_resolve_language()`
     helper and the `language = _resolve_language()` assignment are **byte-unchanged** — both RTD
     projects depend on that seam — and no file under `typsphinx/` is touched at all (milestone
     invariant #3).

  3. `docs/usage.rst` and the **root orphan** `docs/installation.rst` are gone together with
     `tests/test_documentation_usage.py` and `tests/test_documentation_installation.py` in the
     **same commit** as their subjects (milestone invariant #5); the live toctree-reachable
     `docs/source/installation.rst` and its `.po` catalog are byte-unchanged; and a **full `pytest`
     run after the deletions is green** — that run, not the deletion commit, is the proof.

  4. The collateral damage in `tests/test_readthedocs_config.py` is **repaired, not deleted**: its
     four `html_context["language"]` assertions are repointed at `module.language` /
     `_resolve_language()` so the seam stays covered, and the docstring on the PDF
     no-language-flag assertion no longer cites the superseded "not a step toward the deferred
     Japanese PDF (D-11)" rationale. The suite is green with the assertions still asserting
     something real.

  5. `tox -e docs-html` and `tox -e docs-pdf` are green on the post-deletion tree and an
     **observed** `docs.yml` CI run is green — no workflow step references a tox env or build path
     that no longer exists, and the `peaceiris/actions-gh-pages` step's `publish_dir` points at
     `./docs/_build/html` rather than the deleted multilang tree — and the documentation root URL
     still resolves (RTD-04 standing invariant).

**Plans**: TBD

**Owner-manual dependencies (no automated criterion possible):** none of the RTD web-UI work lands
here — creating the Japanese project, setting its Language, linking it under the English parent's
Settings → Translations, and activating its versions all belong to **Phase 30.1**. The only manual
step this phase owns is the merge: `worktree.cleanup-wave`'s **deletion guard** always blocks a
branch containing deletions with no bypass, and this phase is deletion-heavy on two independent
axes, so plan for a manual merge after measuring the deletion scope (Phase 27 precedent,
PROJECT.md D-13).

**Notes**: **Two statements that stood in this entry before 2026-07-26 are now reversed** by Phase
30's discussion (see `30-CONTEXT.md` § `<roadmap_amendments>`). (a) `docs/locale/ja/**/*.po` (13
files) are **no longer** unchanged in place — D-06 moves them into the new
`typsphinx-doc-translations` repository, which is **Phase 30.1's** work; this phase must not delete
them. (b) `docs/Makefile`'s `gettext` / `locale-init` / `locale-update` targets are **no longer**
unchanged — D-12 moves them to the translations repository, so this phase removes them from
`docs/Makefile` alongside `multilang`, `serve-multilang`, and `html-ja` (D-13, which fails silently
by rendering 100% English once the catalogs leave). **Ordering is load-bearing:** removing the
locale tooling here before Phase 30.1 has it working elsewhere leaves translation authoring with no
home — which is why the `Depends on` line above now names 30.1. Keep `docs.yml` internally
consistent as the multilang tree disappears — the `docs-multilang` → `docs-html` step swap,
deleting the PDF-copy step into `docs/_build/multilang/en/`, and the HTML artifact path — while the
`peaceiris/actions-gh-pages` **deploy step itself** stays for Phase 32 to delete (D-14 repoints its
`publish_dir`; it does not remove the step). Accepted, recorded loss: deleting `build_multilang.py`
removes the root-page `navigator.language` auto-redirect and RTD has no equivalent (it redirects to
a *version*, never auto-detects a *language*) — a Japanese-browser visitor now lands on English and
clicks the flyout.

### Phase 30.1: Translations Repository + Japanese RTD Site (INSERTED)

**Goal**: Japanese readers get typsphinx's documentation from Read the Docs as actual Japanese
prose, switchable through RTD's own flyout, served from a **separate translations repository**
(`typsphinx-doc-translations`) registered as an RTD translation project of the `typsphinx` parent —
with the `docs/locale/ja/` catalogs relocated there, the locale tooling moved with them, the
submodule pin kept current automatically, and the Japanese PDF proven glyph-correct rather than
merely built.
**Depends on**: Phase 29 (the `.readthedocs.yaml` + `language` seam must be proven sound before a
second project reads it). This phase must reach a confirmed-serving state **before** Phase 30
deletes the old switcher and the locale tooling — the replacement is observed working first.
**Requirements**: I18N-01, I18N-03
**Success Criteria** (what must be TRUE):

  1. A page fetched from `https://typsphinx.readthedocs.io/ja/latest/` contains **actual translated
     strings** from the relocated `ja` catalogs in its served body — matched against specific
     catalog msgstr values — so a Japanese project that builds green while rendering 100% English
     fails this criterion. **The probe docname must be one with full coverage** (`user_guide/builders`
     is 65/65, `examples/basic` is 30/30 — measured 2026-07-26); `changelog`, `contributing`,
     `api/index`, and `user_guide/templates` are 0% translated and would show all-English on a
     perfectly healthy site.

  2. RTD's own flyout offers the en↔ja switch **from both sites**, and the ja project's version
     list is independently activated (translation projects inherit nothing from the parent) —
     owner-observed, since creating the project, setting its Language, and linking it under the en
     parent's Settings → Translations is web-UI work no test in this repository can assert.

  3. The translations repository builds the **current** English source, not a frozen one: its
     submodule pin advances automatically (a GitHub Actions workflow modelled on
     `sphinx-doc-translations`'s `main.yml` but **without** its Transifex coupling — `submodule
     update --remote` → regenerate `.pot` → `sphinx-intl update` → commit if changed), demonstrated
     by an observed run that moves the pin and by `/ja/latest/` reflecting a source change made
     after the ja project was created.

  4. The Japanese PDF is **glyph-correct, not merely built**: compared against a local
     `SPHINX_LANGUAGE=ja` build of the same commit (94 pages / 1,811,337 bytes, measured
     2026-07-26), page count and extracted text match, the RTD-built PDF embeds at least one font
     with CJK coverage, and the owner confirms sampled pages render Japanese rather than tofu.
     Run by hand with commands and output pasted verbatim into the verification record; **no
     comparison script is committed** (the RTD-built PDF is unreachable from CI, so a committed
     script would look like a gate that never runs — Phase 29 D-15).

  5. `/ja/stable/` is reachable in the same way `/en/stable/` is: the translations repository is
     tagged in lockstep with the parent so RTD's `stable` resolves there too. Since `stable`
     cannot exist before the `v0.6.4` tag, this phase discharges it by leaving the ja project's
     Default Version at `latest` and **recording the two-repository tag step as an explicit
     handoff** into the release procedure — the same shape as Phase 29's `latest` → `stable`
     handoff, not an assertion that `/ja/stable/` already serves.

**Plans**: 10/11 plans executed
after `30.1-VERIFICATION.md` scored 3/5 (SC#3 and SC#4 FAILED, SC#2 and D-03 check 4 open).
Each wave waits on an owner action or on a real build completing, the same shape Phase 29 used and for
the same reason.

Plans:
**Wave 1**

- [x] 30.1-01-PLAN.md — the ja build manifest, the locale-tooling `Makefile` (D-12 arrival half) and the
      translations-repository README (incl. the two-repository release set, D-07), staged in-repo

- [x] 30.1-02-PLAN.md — the D-08 pin-bump workflow (staged) and the D-05 rationale amendment in
      `tests/test_readthedocs_config.py`, executable lines byte-unchanged

**Wave 2** *(blocked on Wave 1; owner creates the GitHub repository)*

- [x] 30.1-03-PLAN.md — `typsphinx-doc-translations` created, populated (branch-pinned submodule, 13
      `.po`, no `.mo`, all staged files) and proven from an independent clone; `30.1-EVIDENCE.md` created

**Wave 3** *(blocked on Wave 2; owner creates, links and version-activates the ja RTD project)*

- [x] 30.1-04-PLAN.md — SC#1's two content probes against 100%-coverage docnames, the first build log's
      answers, the RTD-04 root re-fetch, SC#2/SC#5 recorded honestly, and the D-15 gate for Phase 30

**Wave 4** *(blocked on Wave 3; needs the ja project to exist before the source change is made)*

- [x] 30.1-05-PLAN.md — SC#3: a `Translations` section in `docs/source/contributing.rst`, the milestone
      branch pushed, an observed pin-bump run that moves the gitlink, and the change observed on `/ja/`

**Wave 5** *(blocked on Wave 4; needs the ja PDF built from the advanced pin)*

- [x] 30.1-06-PLAN.md — SC#4: D-03's glyph gate (page count, extracted text, CJK font enumeration) plus
      the owner's tofu check held open as `human_needed`, and the phase's consolidated criterion status

**Wave 6** *(gap closure; blocked on Wave 5 — the owner's look must precede the pin bump, which reflows the PDF)*

- [x] 30.1-07-PLAN.md — the two open owner observations collected against a freshly SHA-identified
      artifact: H1 the flyout on both sites (SC#2), H2 the tofu check on the flagged pages (D-03 check 4),
      with the H1 contradiction preserved rather than resolved

**Wave 7** *(blocked on Wave 6)*

- [x] 30.1-08-PLAN.md — the SC#3 root cause repaired: an explicit submodule branch fetch inserted before
      `git submodule update --remote` in both the staged and live `update-pin.yml`, WR-01's clone command
      fixed and proven by a run with a negative control, and the parent's milestone branch advanced

**Wave 8** *(blocked on Wave 7; needs the repaired workflow live)*

- [x] 30.1-09-PLAN.md — SC#3 observed end to end: a triggered run watched to completion, the gitlink move
      proven by an exhibited `Subproject commit` diff hunk, and the parent's current source observed on
      `/ja/latest/contributing.html` by two independent probes

**Wave 9** *(blocked on Wave 8; the pin bump changes the artifact under diagnosis)*

- [x] 30.1-10-PLAN.md — SC#4 root-caused: per-occurrence font attribution and `/ToUnicode` forensics on
      the current artifact, the RTD container's own font inventory measured from inside a real build, the
      page-count reconciliation, the English-parent measurement, and a blocking scope decision

**Wave 10** *(blocked on Wave 9; executes the owner's chosen option)*

- [ ] 30.1-11-PLAN.md — SC#4 fixed and re-measured: the selected fix applied, the diagnostic block
      removed, the rebuild observed, D-03 checks 1-3 re-run against a freshly recompiled same-source
      baseline with the NUL count recorded on both sides, and the consolidated post-round status

**Planning decisions recorded in `30.1-01-PLAN.md`:** `docs/locale/ja/`'s deletion from this repository
is assigned to **Phase 30**, not here (one deletion-guard manual merge for the milestone instead of two,
and the local `SPHINX_LANGUAGE=ja` baseline SC#4 needs stays available); the submodule tracks
`gsd/v0.6.4-read-the-docs-migration` rather than `main`, because `origin/main` carries no
`.readthedocs.yaml` and no `_resolve_language()` (both measured 2026-07-26) — adding a third owed
post-merge flip; and the live-evidence file is `30.1-EVIDENCE.md`, deliberately not the
`/gsd-verify-work`-owned `30.1-VERIFICATION.md` name.

**Owner-manual dependencies (no automated criterion possible):** create the
`typsphinx-doc-translations` GitHub repository; create a **separate** RTD project pointed at *that*
repository and set Language = Japanese in **its own** Admin settings — this dropdown, not anything
in `conf.py`, is what makes RTD emit `READTHEDOCS_LANGUAGE=ja`; **link it under the English
parent's Settings → Translations** (the step most likely to be missed — two working but
unswitchable sites otherwise); activate versions on the ja project independently. Criterion 1
verifies the outcome by fetching real content; criteria 2 and the human half of 4 are explicitly
owner-observed. The ja project's **slug is not a decision** — enter `typsphinx-ja` (measured 404,
unclaimed, 2026-07-25; the form all 15 Sphinx translation projects use), and if it is taken pick
any other free name and continue: unlike the parent slug it is never published, since readers see
`/ja/latest/` under the parent domain.

**Notes**: This phase exists because the milestone's original plan — re-importing *this* repository
twice — was replaced on 2026-07-26 by the `sphinx-doc/sphinx-doc-translations` model (30-CONTEXT.md
D-06), measured from RTD's public API: the `sphinx` project has 15 translations, every one a
distinct RTD project building a *different* repository. **I18N-03 was promoted from Future to v1**
in the same discussion (D-04): the ja project emits a Japanese PDF, and D-01's decision to ship it
was re-confirmed on the post-split premise rather than inherited. Two consequences carry standing
cost: every release now tags **two** repositories (D-07), and the submodule pin needs automation or
the ja site silently serves translations of a stale English source (D-08). The ja catalogs ship at
**24.3% coverage** (257/1058 msgids, measured 2026-07-26) by owner decision — I18N-01's bar is
"actual Japanese prose is served," not "fully translated," and untranslated msgids fall back to
English by Sphinx's normal behaviour; raising coverage is separate, later work. `/ja/` is not
configurable: RTD derives the URL segment from the project's Language using ISO 639-1, and `jp` is
a country code that does not appear in its list (D-10). Phase 29's open question is **live here**:
`build.apt_packages: [fonts-noto-cjk]` installed successfully on RTD but the font Typst actually
embedded was `MSNUZX+HanaMinA` — whether that package is load-bearing was never established, and it
matters far more for a 94-page Japanese PDF than it did for four CJK strings in the English one.
Measure it before the ja manifest relies on it.

### Phase 31: Published-URL Cutover + Repo-Wide Link Guard

**Goal**: Every documentation URL typsphinx publishes points at Read the Docs and actually resolves,
the external bug report about the broken link is closed with the promised fix delivered, and a
mechanism now exists that would catch the next dead link instead of it surviving for months.
**Depends on**: Phase 30.1 (the final RTD URL must exist and be serving **both** languages —
rewriting to a not-yet-green project trades one broken-link class for another) and Phase 30
**Requirements**: DOC-09, DOC-10, CI-05
**Success Criteria** (what must be TRUE):

  1. Run **before** the rewrite, the new link check flags the live `github.io` URLs in `README.md` and
     `pyproject.toml` — a recorded **negative control** proving the mechanism sees the file class
     `sphinx-build -b linkcheck` structurally cannot, and that it would have caught the 7 dead deep
     links that motivated this milestone.

  2. After the rewrite, **every** documentation URL in `README.md`, `pyproject.toml`'s `Documentation`
     metadata, and `.planning/codebase/INTEGRATIONS.md` is fetched over **real HTTP** and returns a live
     page — the occurrence count taken from a fresh grep at execution time rather than from any prior
     tally (the brief said 9, research measured 10) — while `CHANGELOG.md`'s historical `github.io`
     mentions are deliberately left untouched.

  3. The link check runs in CI as an **advisory** (non-blocking, never a required check — `drift.yml`
     precedent, D-07) job, green on the rewritten tree, and its scope is documented where it lives:
     that **it**, not sphinx linkcheck, is what covers `README.md` / `pyproject.toml`.

  4. Issue #119 is closed with a reply that names the fix actually delivered, and a visitor to the
     GitHub repository can reach the documentation from the repository's own About → Website field —
     which resolves to the RTD root over real HTTP.

**Plans**: TBD

**Owner-manual dependency (no automated criterion possible):** setting the repository's About → Website
field. No test in this repository can assert it; criterion 4 verifies the URL it is set to resolves.

**Notes**: `.planning/codebase/INTEGRATIONS.md` contains no literal `github.io` string — it needs a
**paragraph-level** rewrite (hosting/build-system prose + the `SPHINX_LANGUAGE` →
`READTHEDOCS_LANGUAGE` seam), not a find-and-replace. Ordered **before** the Phase 32 teardown on
purpose: with both hosts briefly live, the rewritten links are proven against RTD before anything is
destroyed. Sphinx linkcheck stays out of scope (LNK-01, Future) and its pending todo
`add-sphinx-linkcheck-ci-job` stays open.

### Phase 32: GitHub Pages Teardown (IRREVERSIBLE)

**Goal**: typsphinx documentation is hosted by Read the Docs and only Read the Docs — the GitHub Pages
publish path and the branch that served it are gone — while the `typstpdf` regression gate and the
tag-time PDF Release attachment keep working.
**Depends on**: Phase 31, and by REQUIREMENTS.md invariant #6 on Phases 29–31 (30.1 included) having **observed** RTD
serving English HTML, Japanese HTML, and the PDF-or-documented-fallback. This phase is deliberately
**not** folded into a neighbour: it is the milestone's only action with no undo, so it gets its own
standing gate.
**Requirements**: CI-04
**Success Criteria** (what must be TRUE):

  1. A pre-teardown gate records **freshly re-taken** direct evidence — gathered in this phase, not
     cited from Phase 29/30 — that RTD is *currently* serving English HTML, Japanese HTML, and the
     PDF-or-documented-fallback, and that the documentation root URL resolves. The teardown proceeds
     only behind that evidence.

  2. `docs.yml` no longer contains a GitHub Pages deploy step (`peaceiris/actions-gh-pages`), and
     `origin/gh-pages` no longer exists — proven by `git ls-remote`, not by a local branch listing. The
     old `github.io` documentation URL returns 404 and **no redirect stub was added** (the
     owner-accepted SEO/inbound-link cost, decision 2026-07-25).

  3. An **observed** CI run on the post-teardown tree keeps `tox -e docs-pdf` green as the PR-blocking
     `typstpdf` regression gate, and the tag-time `Upload PDF to Release` step is **byte-unchanged** in
     the milestone diff — its live exercise is honestly deferred to the tag at
     `/gsd-complete-milestone`, since this phase cannot create a tag.

**Plans**: TBD

**Owner-manual dependency (no automated criterion possible):** disabling the GitHub Pages site in the
repository's Settings → Pages. Deleting the `gh-pages` branch removes the source but can leave the Pages
feature enabled against a missing source; criterion 2's 404 check is the observable outcome.

**Notes**: The repository-side multilang steps in `docs.yml` (the `docs-multilang` → `docs-html` swap,
the PDF-copy step, artifact paths) and the `tox.ini` / `docs/Makefile` cleanup belong to **Phase 30** —
they must land there to keep CI green when `build_multilang.py` disappears. What remains here is the
publish path itself: the deploy step and the branch. Recovery cost if this phase runs early is HIGH and
effectively total (the served site and any cached copies are gone the moment Pages is off) — which is
exactly why criterion 1 exists.

### Phase 33: v0.6.4 Release Prep

**Goal**: v0.6.4 is ready to publish — version bumped, CHANGELOG curated, PyPI metadata pointing at a
URL that resolves, milestone invariants asserted over the full diff — with the irreversible publish and
the post-tag `stable` flip handed off explicitly rather than claimed.
**Depends on**: Phase 32
**Requirements**: REL-02
**Success Criteria** (what must be TRUE):

  1. `pyproject.toml` is the **sole** `0.6.4` version literal with `uv.lock` in lockstep and
     `README.md`'s Status line updated; `typsphinx.__version__` reports `0.6.4`; and every version-sync
     guard test is green — including `tests/test_readme_version_sync.py` and the now-four-surface
     `tests/test_preview_version_sync.py`.

  2. A curated `## [0.6.4]` `CHANGELOG.md` entry covers this milestone's user-visible changes (hosting
     moved to Read the Docs, the Japanese site, the machinery/orphan removals, the URL rewrites, the
     accepted loss of browser-language auto-redirect), **and** the tail release/compare link block is
     updated in the same phase — the `Unreleased` compare carried forward.

  3. `pyproject.toml`'s `Documentation` metadata points at the Read the Docs URL and is confirmed by a
     **real HTTP fetch** on the prepared tree — the half of REL-02 this phase can actually satisfy.

  4. The milestone invariants hold over the **full milestone diff**, evidenced by `git diff` across the
     range: zero new runtime dependencies, no `@preview` version bump, the four version-sync surfaces'
     package strings untouched, and **zero changes under `typsphinx/`**.

  5. **No tag and no publish happen in this phase.** REL-02's remaining half — `typsphinx 0.6.4` live on
     PyPI, and `/en/stable/` **and** `/ja/stable/` both serving that released version after the owner
     flips Default Version `latest` → `stable` and re-checks the ja project's independent version
     activation — is recorded here as an explicit `/gsd-complete-milestone` + owner-manual handoff
     checklist, not asserted as satisfied. A criterion this phase structurally cannot meet is not
     written as if it could.

**Plans**: TBD

**Owner-manual dependencies (no automated criterion possible):** after the tag is pushed and built
green, setting Default Version = `stable` on the en project and confirming `/ja/stable/` exists and
points at the **same** tag as `/en/stable/` (translation projects do not inherit the parent's activated
versions — this is Pitfall 4's re-check requirement). Until then Default Version stays `latest`.

**Notes**: Prep-only by the established pattern (`branching_strategy: milestone`; v0.5.0 Phase 10 /
v0.6.2 Phase 23 / v0.6.3 Phase 28). `stable` becomes a real, buildable RTD version for the first time
at this tag — RTD has refused builds on tags lacking `.readthedocs.yaml` since 2023-09-25, so
documentation for `v0.6.3` and earlier is structurally unbuildable (Future requirement RTD-06).

## Progress

**Execution Order:**
Active milestone phases execute in numeric order (decimal insertions between their surrounding
integers). v0.6.4 executes 29 → 30 → 31 → 32 → 33, with the irreversible teardown (32) gated behind a
freshly re-taken "RTD is serving" observation and the prep-only Release (33) last.

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
| 22.4 README 記述の実測乖離解消 (INSERTED) | v0.6.2 | 3/3 | Complete | 2026-07-23 |
| 23. v0.6.2 Release Prep + Regression-Gate Close | v0.6.2 | 3/3 | Complete | 2026-07-23 |
| 24. Delete `typst_toctree_defaults` | v0.6.3 | 1/1 | Complete    | 2026-07-23 |
| 25. Captioned Table Figure Wrap + Cross-References | v0.6.3 | 2/2 | Complete    | 2026-07-24 |
| 26. `typst_elements` papersize/fontsize Pass-Through | v0.6.3 | 2/2 | Complete    | 2026-07-24 |
| 27. Docs 実測整合 — Orphan Delete + Phantom Names | v0.6.3 | 1/1 | Complete    | 2026-07-24 |
| 27.1 Typst 組版 lang の Sphinx `language` 連動 (INSERTED) | v0.6.3 | 3/3 | Complete    | 2026-07-25 |
| 28. v0.6.3 Release Prep + Regression-Gate Close | v0.6.3 | 3/3 | Complete    | 2026-07-25 |
| 29. RTD Build Establishment (English Parent) + PDF Path Decision | v0.6.4 | 6/6 | Complete    | 2026-07-26 |
| 30. Hand-Rolled Multi-Language Machinery & Orphan Removal | v0.6.4 | 0/TBD | Not started | - |
| 30.1 Translations Repository + Japanese RTD Site (INSERTED) | v0.6.4 | 10/11 | In Progress|  |
| 31. Published-URL Cutover + Repo-Wide Link Guard | v0.6.4 | 0/TBD | Not started | - |
| 32. GitHub Pages Teardown (IRREVERSIBLE) | v0.6.4 | 0/TBD | Not started | - |
| 33. v0.6.4 Release Prep | v0.6.4 | 0/TBD | Not started | - |

## Backlog

Candidate work not yet scoped into a milestone. Promote items with `/gsd-review-backlog`, or
pull a whole cluster into the next milestone via `/gsd-new-milestone`.
Numbered 999.x so milestone reorganization never renumbers or drops them.

**The backlog is currently empty.** New items land here as `999.x` entries. Three pending todos were
**promoted into v0.6.4** (Phases 29–33): `move-documentation-hosting-to-read-the-docs`,
`github-io-doc-links-404-missing-en-prefix`, and `docs-usage-installation-orphan-class`.
`add-sphinx-linkcheck-ci-job` stays **open and deferred** — sphinx linkcheck is out of v0.6.4 scope as
Future requirement LNK-01 (it structurally cannot see `README.md` / `pyproject.toml`, where the dead
links actually live); CI-05's repo-wide real-HTTP check covers that class instead. Remaining discrete
follow-up work stays in `.planning/todos/pending/` — citation-node support, non-str-docname TypeError
hardening, typing-import modernization, and `derive_typst_lang()` warning-block duplication — see also
STATE.md Deferred Items.

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25). v0.6.4 scoped 2026-07-25 (Phases 29–33). Per-milestone phase detail, success criteria, and decisions for shipped milestones live in `milestones/vX.Y-ROADMAP.md`.*
