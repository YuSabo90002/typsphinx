# Roadmap: typsphinx

## Milestones

- ✅ **v0.4.4 — CI-repair + modernize** — Phases 1–5 (shipped 2026-07-05) → [archive](milestones/v0.4.4-ROADMAP.md)
- ✅ **v0.5.0 — forward-ecosystem** — Phases 6–10 + 8.1 (shipped 2026-07-11) → [archive](milestones/v0.5.0-ROADMAP.md)
- ✅ **v0.6.0 — real-world robustness** — Phases 11–15 (shipped 2026-07-13) → [archive](milestones/v0.6.0-ROADMAP.md)
- ✅ **v0.6.1 — rendering fidelity** — Phases 16–18 (shipped 2026-07-19) → [archive](milestones/v0.6.1-ROADMAP.md)
- ✅ **v0.6.2 — rendering fidelity round 2** — Phases 19–23 (+22.1–22.4) (shipped 2026-07-23) → [archive](milestones/v0.6.2-ROADMAP.md)
- ✅ **v0.6.3 — config & docs measured fidelity + captioned tables** — Phases 24–28 (+27.1) (shipped 2026-07-25) → [archive](milestones/v0.6.3-ROADMAP.md)
- ✅ **v0.6.4 — Read the Docs migration** — Phases 29–33 (+30.1) (shipped 2026-07-28) → [archive](milestones/v0.6.4-ROADMAP.md)
- 🚧 **v0.6.5 — inline-math separator hotfix** — Phases 34–35 (active, started 2026-07-28)

**Active milestone: v0.6.5 — inline-math separator hotfix.** Two phases (34, 35): the backlog-999.1
inline-math separator fix, then prep-only release. Phase numbering continues from v0.6.4's last phase
(33), so v0.6.5 starts at Phase 34.

## Phases

**Phase Numbering:**

- Integer phases (34, 35): Planned milestone work
- Decimal phases (34.1, 34.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.6.5 continues from v0.6.4's last phase (33), so it starts at Phase 34.

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

### 🚧 v0.6.5 — inline-math separator hotfix (Phases 34–35) — IN PROGRESS

**Milestone goal:** Fix one reported defect and ship it. A paragraph that mixes prose and inline math
currently emits Typst with no valid separator between the preceding text emission and the `mi(...)` /
`$...$` call, so the build dies at `typst.compile()` — a document a user can legitimately write does
not compile at all. Two phases: (34) the fix, pinned by a real-compile regression fixture proven red
before the change; (35) prep-only release. Nothing else enters this milestone.

**Deliberately two phases, not more.** With one behavioural requirement and one release requirement,
the natural delivery boundary is exactly one fix phase plus the standing prep-only Release phase
(v0.5.0 Phase 10 / v0.6.2 Phase 23 / v0.6.3 Phase 28 / v0.6.4 Phase 33 precedent). Splitting the fix
from its regression fixture, or the mitex path from the native path, would create phases that cannot
be verified independently — the fixture *is* the proof the fix works, and both math paths flow through
the same separator seam.

**The root cause is NOT yet known — Phase 34 must measure it before fixing it.** The backlog capture
said "likely a translator-level emission issue (`translator.py` math/Text visit ordering)," but the
obvious hypothesis is already contradicted by the source: `visit_math` (`translator.py:3936`) *does*
call `_add_paragraph_separator()` (`translator.py:3954`). So the defect lives in what that separator
decides to emit when the immediately preceding sibling is a `Text` node inside an already-open
paragraph (`visit_Text`, `translator.py:1018`; `_add_paragraph_separator`, `translator.py:319`) — or
somewhere else entirely. Phase 34's first job is a reproduction that captures **the emitted `.typ`
text and the verbatim Typst error**, and only then a fix aimed at whatever that measurement shows.
A plan that starts by editing `visit_math` on the strength of the backlog note is planning against an
unverified premise. (Standing lesson: verify ROADMAP/backlog claims by measurement before treating
them as given.)

**Both math emission paths are in scope, because both are reachable by default users.** mitex is the
default (`typst_use_mitex=True` → `mi(...)`), and the native path is reached either per-node via the
`typst-native` class or globally via `typst_use_mitex=False` (→ `$...$`). A fix verified on one path
only would leave half the users broken, so MATH-01's criteria name both. The three existing math test
modules (`tests/test_math_mitex.py`, `test_math_native.py`, `test_math_fallback.py`) are the
non-regression surface, not the acceptance bar.

**Standing GATE-01 bar (unchanged since v0.6.0):** every node-handler change ships a real
`sphinx-build → typst.compile()` regression fixture, and the fixture must be **recorded red against
the unfixed translator** — a green-after-the-fact assertion is not proof. A fix that makes the compile
succeed but silently drops or garbles the surrounding prose also fails: this project's standard since
v0.6.1 is "renders faithfully," not "compiles fatal-free."

**Milestone invariants (every phase):** zero new runtime dependencies; no `@preview` version bump; the
three-way version-sync surface — the four bundled package version strings in `typsphinx/writer.py`,
`typsphinx/template_engine.py` and `typsphinx/templates/base.typ`, plus the fourth surface
`examples/**/*.typ` that `tests/test_preview_version_sync.py` now watches — unchanged. The diff this
milestone is expected to produce is a translator fix, its tests, and the release-prep files.

**Backlog promotion:** this milestone promotes backlog item **999.1** ("Inline math after text —
missing separator before `#mi()` causes Typst error") into Phase 34. It has been removed from the
Backlog section below and lives here as MATH-01.

**UI note:** neither phase is frontend UI work — this is translator/typesetting and release work.
`ui.plan-gate` false-positives on PDF/render/template wording (STATE.md standing note); use
`--skip-ui` if it flags a phase. Same caveat applies to `api-coverage.verify-pre` on prose describing
compile/render evidence.

**Ship unit = milestone** (`branching_strategy: milestone`): Phase 35 is prep-only — it bumps
`pyproject.toml` + `uv.lock`, updates README's Status line, and adds the `CHANGELOG.md` entry with its
tail link-block rollover, and does **not** tag or publish. The irreversible publish (tag `v0.6.5` →
`release.yml` → PyPI + GitHub Release, plus the standing second tag on `typsphinx-doc-translations`)
executes at `/gsd-complete-milestone`.

- [ ] **Phase 34: Inline Math After Text — Separator Fix** - Root-cause the missing separator by measurement, fix it so prose-then-inline-math paragraphs compile on both the mitex and native paths, and pin it with a real `typst.compile()` GATE-01 fixture recorded failing pre-fix
- [ ] **Phase 35: v0.6.5 Release Prep** - Prep-only: bump 0.6.5 (`pyproject.toml` sole literal + `uv.lock` lockstep + README Status), curated `## [0.6.5]` CHANGELOG entry with the tail link-block rollover, invariants asserted over the full milestone diff; publish at `/gsd-complete-milestone`

### Phase 34: Inline Math After Text — Separator Fix

**Goal**: A user can write a paragraph that mixes prose and inline math — including with no whitespace
between them — and `sphinx-build -b typstpdf` produces a PDF with both the prose and the math intact,
instead of aborting the Typst compile.
**Depends on**: Nothing (first phase of the milestone)
**Requirements**: MATH-01
**Success Criteria** (what must be TRUE):

  1. A reST document whose paragraph has inline math immediately following text (the reported
     999.1 shape, including the no-intervening-space form) builds through `sphinx-build -b typstpdf`
     and yields a valid PDF — the `TypstCompilationError` the backlog item reports no longer occurs.

  2. The same document compiles on **both** emission paths: the mitex default
     (`typst_use_mitex=True` → `mi(...)`) and the native path (`typst-native` class *or*
     `typst_use_mitex=False` → `$...$`). Fixing one path and leaving the other broken fails this
     criterion.

  3. The compiled PDF's extracted text contains the preceding prose **and** the math content, adjacent
     as authored — no dropped words, no swallowed math, and no Typst source leaking into the page as
     prose. An output that compiles but silently mis-renders fails this criterion (v0.6.1 standard).

  4. The fix is pinned by a real `typst.compile()` GATE-01 regression fixture whose **fail-pre-fix
     run is recorded** — the fixture shown red against the unfixed translator (and the verbatim Typst
     error captured), then green after — so the fixture is proven to be able to catch the regression
     rather than merely passing.

  5. Nothing else about math emission regresses: display math (`.. math::`), math in list items /
     tables / captions, the existing `tests/test_math_mitex.py` / `test_math_native.py` /
     `test_math_fallback.py` modules, the full pytest suite, and the full-corpus `-b typstpdf`
     regression gate all stay green.

**Plans**: 3 plans

Plans:

- [ ] 34-01-PLAN.md — GATE-01 fixture (list item + field body + def-list term + list-item block math + top-level control) on both emission paths, recorded RED against the unfixed translator
- [ ] 34-02-PLAN.md — separator-protocol fix in `visit_math` (3 protocols) and `visit_math_block` (list-item half), gate turned GREEN on both paths
- [ ] 34-03-PLAN.md — regression sweep: full suite vs. pre-fix baseline, lint/type, full-corpus `-b typstpdf` gate, docs dogfooding build, milestone invariants

### Phase 35: v0.6.5 Release Prep

**Goal**: v0.6.5 is ready to publish — someone reading the changelog can see, in their own terms, that
a document which used to fail to compile now compiles — and the only remaining step is the tag.
**Depends on**: Phase 34
**Requirements**: REL-03
**Success Criteria** (what must be TRUE):

  1. `pyproject.toml` declares `0.6.5` as the **sole** version literal with `uv.lock` in lockstep
     (`uv sync --extra dev --locked` green), `typsphinx.__version__` reports `0.6.5`, and README's
     Status line agrees — the existing version-sync guard tests (incl. the README↔pyproject ratchet)
     stay green.

  2. `CHANGELOG.md` carries a curated `## [0.6.5]` entry stating the inline-math fix in user-visible
     terms (what a user could not build before and can build now), and the **tail link block is rolled
     over**: a `[0.6.5]:` release-tag link added and `[Unreleased]:` advanced to `v0.6.5...HEAD`.

  3. The post-bump tree is green end to end on a live run: the full pytest suite, `black` / `ruff` /
     `mypy`, and the full-corpus `-b typstpdf` regression gate (fatal-free, valid `%PDF`).

  4. The milestone invariants are asserted **mechanically over the full milestone diff** (not by
     recollection): zero new runtime dependencies, no `@preview` version bump, and the four bundled
     package version strings unchanged across all four sync surfaces.

  5. No irreversible action was taken in this phase — no `v0.6.5` tag exists locally or on `origin`
     and nothing is published, proven by empty `git tag -l v0.6.5` / `git ls-remote --tags origin
     v0.6.5`. The publish half (tag → `release.yml` → PyPI + GitHub Release, plus the standing
     second-repository tag on `typsphinx-doc-translations`) executes at `/gsd-complete-milestone`.

**Plans**: TBD

Plans:

- [ ] TBD (created by `/gsd-plan-phase 35`)

## Progress

**Execution Order:**
Active milestone phases execute in numeric order (decimal insertions between their surrounding
integers). v0.6.5 executes 34 → 35, with the prep-only Release (35) last so the CHANGELOG entry
describes a fix that has already been proven by Phase 34's real-compile gate.

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
| 34. Inline Math After Text — Separator Fix | v0.6.5 | 0/3 | Planned | - |
| 35. v0.6.5 Release Prep | v0.6.5 | 0/TBD | Not started | - |

## Backlog

Candidate work not yet scoped into a milestone. Promote items with `/gsd-review-backlog`, or
pull a whole cluster into the next milestone via `/gsd-new-milestone`.
Numbered 999.x so milestone reorganization never renumbers or drops them.

New items land here as `999.x` entries. **The backlog is currently empty** — item **999.1** (inline
math after text: missing separator before `#mi()` causes a Typst error) was **promoted into v0.6.5**
as Phase 34 / requirement MATH-01 on 2026-07-28 and removed from this section. Three earlier pending
todos were promoted into v0.6.4 (Phases 29–33): `move-documentation-hosting-to-read-the-docs`,
`github-io-doc-links-404-missing-en-prefix`, and `docs-usage-installation-orphan-class`.
`add-sphinx-linkcheck-ci-job` stays **open and deferred** — sphinx linkcheck is out of scope as
Future requirement LNK-01 (it structurally cannot see `README.md` / `pyproject.toml`, where the dead
links actually live); v0.6.4 CI-05's repo-wide real-HTTP check covers that class instead. Remaining
discrete follow-up work stays in `.planning/todos/pending/` — citation-node support,
non-str-docname TypeError hardening, typing-import modernization, and `derive_typst_lang()`
warning-block duplication — see also STATE.md Deferred Items.

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23), v0.6.3 (2026-07-25), v0.6.4 (2026-07-28). v0.6.5 phases added 2026-07-28. Per-milestone phase detail, success criteria, and decisions for shipped milestones live in `milestones/vX.Y-ROADMAP.md`.*
