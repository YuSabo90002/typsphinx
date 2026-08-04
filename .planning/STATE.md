---
gsd_state_version: 1.0
milestone: v0.7.1
milestone_name: bug-fix round
current_phase: 44.2
current_phase_name: "`typst_documents` Title and Author Consumption"
status: planning
stopped_at: "Phase 44.1 context revised: SC#2 = option-a (D-07); plans removed for regeneration"
last_updated: "2026-08-04T19:19:21.503Z"
last_activity: 2026-08-05
last_activity_desc: Phase 44.1 complete, transitioned to Phase 44.2
progress:
  total_phases: 7
  completed_phases: 3
  total_plans: 14
  completed_plans: 14
  percent: 43
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-04 at the start of milestone v0.7.1)

**Core value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered output — and the documented configuration actually takes effect, so a user who copies a documented `conf.py` example gets what the docs promise. The same standard applies to the *publishing* surface: a URL the project publishes must actually resolve, and the PDF a reader downloads must be the one typsphinx itself produced. From v0.7.0 the standard extends again: the output must be *well typeset*, not merely correct.
**Current focus:** Phase 44.1 — relative-heading-depth-for-toctree-nesting
15/15 v1 requirements mapped with zero orphans (FIG-01 added 2026-08-04 at Phase 43 discussion;
TOC-01 added 2026-08-04 with the Phase 44.1 insertion; DOC-13 added 2026-08-04 with the Phase 45.1
insertion; CONF-09 added 2026-08-04 with the Phase 44.2 insertion, reversing Phase 44's D-02).
Next action: `/gsd-execute-phase 44.1`.

## Current Position

Phase: 44.2 — `typst_documents` Title and Author Consumption
Plan: Not started
Status: Ready to plan
Progress: [######--------------] 29% (2/7 phases)
Last activity: 2026-08-05 — Phase 44.1 complete, transitioned to Phase 44.2
prior 4-plan set was deleted at `2c31b89`. SC#2 is locked as option-a, so **no plan carries a
blocking decision checkpoint** — the superseded note about one in `44.1-03` no longer applies.

## Active Milestone (v0.7.1 — bug-fix round)

**Roadmap created 2026-08-04: Phases 43-46** (plus **44.1**, **44.2** and **45.1**, all inserted
2026-08-04), derived from
`REQUIREMENTS.md` alone. Research was deliberately skipped (owner decision 2026-08-04 — a maintenance
round over already-diagnosed defects, each carrying a file/line-level todo, with the one
new-behaviour item CONF-08 resolved by direct measurement of Sphinx 9.1.0's LaTeX builder), so this
milestone has **no `research/SUMMARY.md`**.
Coverage: **15/15** v1 requirements mapped, zero orphans, zero duplicates (was 11/11; **FIG-01**
added 2026-08-04 by owner decision at Phase 43 discussion; **TOC-01** added 2026-08-04 with the
Phase 44.1 insertion; **DOC-13** added 2026-08-04 with the Phase 45.1 insertion; **CONF-09** added
2026-08-04 with the Phase 44.2 insertion, which **reverses Phase 44's D-02** — the entry
title/author wiring is back inside v0.7.1, and the milestone now owes **two** user-visible CHANGELOG
callouts rather than one).

| Phase | Goal | Requirements |
|-------|------|--------------|
| 43. Table State Correctness — Nested Tables + Empty-Title Anchors | A nested table stops replacing the outer table's body; a nested figure stops dropping the outer caption; an empty-titled caption still anchors its ids | TBL-04, TBL-05, FIG-01, QUA-01 |
| 44. `typst_documents` Default Derivation + Builder Input Hardening | The Quick Start produces a PDF; a malformed docname fails with an actionable typsphinx error | CONF-08, BLD-01 |
| 44.1 Relative Heading Depth for Toctree Nesting (INSERTED) | A toctree'd document's headings render one level deeper than its parent instead of flat — `visit_title` emits relative `depth:` so `set heading(offset: 1)` applies | TOC-01 |
| 44.2 `typst_documents` Title and Author Consumption (INSERTED) | An explicit entry's `[2]` title / `[3]` author actually reach the rendered PDF, overriding `project`/`author` as LaTeX does — reverses Phase 44's D-02 | CONF-09 |
| 45. Documentation Currency + Carried Hygiene | README explains `typst_documents` + its new default; the published changelog page stops being two years stale; two hygiene todos close | DOC-11, DOC-12, QUA-02, QUA-03 |
| 45.1 Custom-Template Parameter Contract Correction (INSERTED) | A custom template declaring exactly the documented parameters compiles; the published contract and the parameters typsphinx actually passes agree both ways | DOC-13 |
| 46. v0.7.1 Release Prep (prep-only) | The tree is bumped, curated, proven green, and handed off with zero irreversible action | REL-06, REL-04 |

**Three structural constraints this roadmap encodes:**

1. **Milestone invariant #5 (new).** The milestone branch is pushed to `origin` in **Phase 43**, not
   at the release PR — it is Phase 43's SC#5. Both defects that surfaced at the v0.7.0 close share
   the cause that the branch was never pushed until the release PR, so neither Windows CI nor a real
   tag push ran against it during eight phases.

2. **REL-04 does not close in Phase 46.** Phase 46 owns only its in-phase share — verifying the
   already-on-`main` `create-release` fix (the `astral-sh/setup-uv` + `Set up Python` steps) and
   exercising the extractor against the new `## [0.7.1]` section — plus an explicit handoff item.
   The requirement closes when a real tag push runs `create-release` to completion at
   `/gsd-complete-milestone`, or it carries again. Reporting it done on the strength of a correct
   workflow file is the precise error v0.7.0 made; `phase.complete` has a recorded habit of
   auto-flipping REL rows against a CONTEXT decision, so the Phase 46 close must diff before commit.

3. **Phase 46 is prep-only.** No tag, no PyPI, no GitHub Release — the standing v0.5.0 Phase 10
   pattern under `branching_strategy: milestone`. The publish executes at `/gsd-complete-milestone`,
   including the standing second tag on `typsphinx-doc-translations`.

**Sequencing note:** the chain 43 → 44 → 44.1 → 44.2 → 45 → 45.1 → 46 is genuinely dependent, not
merely numbered. Phase 44 hardens the same `TypstPDFBuilder.finish()` its own derivation rewrites
(so CONF-08 and BLD-01 are one change, not two); Phase 44.2 runs after 44.1 because
`tests/roots/test-basic/conf.py` is inside 44.1's SC#3 byte-invariance corpus and is one of the five
entries 44.2 changes; Phases 45 and 45.1 document behaviour, so everything they describe must have
landed first; the `0.7.1` entry for DOC-12's changelog page lands in Phase 46's lockstep edit
alongside `CHANGELOG.md`.

**Not a frontend UI milestone** — no phase carries a UI hint. `ui.plan-gate` false-positives on
"table"/"render"/"page" wording here; use `--skip-ui`.

## Shipped Milestone (v0.7.0 — archived)

Full phase detail, success criteria, and decisions: [`milestones/v0.7.0-ROADMAP.md`](milestones/v0.7.0-ROADMAP.md)
and [`milestones/v0.7.0-REQUIREMENTS.md`](milestones/v0.7.0-REQUIREMENTS.md). Phase artifacts are
under `milestones/v0.7.0-phases/`. The MILESTONES.md entry carries the stats, the curated
accomplishments, and the release record.

**Shipped 2026-08-04.** 8 phases (36–42, incl. inserted 40.1) · 57 plans · 158 tasks ·
**32/33** v1 requirements complete (REL-04 carried to v0.7.1) · `override_closeout` (no milestone
audit; 6 open artifacts acknowledged — see Deferred Items). Timeline 2026-07-29 → 2026-08-04
(7 days, 477 commits). Code delta excluding `.planning/`: 80 files, +14,619 / −339 lines.

**Published 2026-08-04.** PR #129 merged to `main` (15/15 CI checks green) and `v0.7.0` tagged on
merge commit `75fd8ed`. Release run `30848860064`: `validate` ✓ → `build` ✓ → `publish-pypi` ✓
(after owner approval of the `pypi` environment, 15-minute wait timer) → `create-release` ✗. PyPI
`typsphinx 0.7.0` is live (wheel 122,514 B + sdist 477,342 B). The GitHub Release
`Release v0.7.0` was repaired by hand and now carries all three assets (`.whl`, `.tar.gz`, and the
tag-time `typsphinx.pdf` from `docs.yml`) with the curated `## [0.7.0]` CHANGELOG body plus
GitHub's auto-generated notes. Second-repository tag done: `typsphinx-doc-translations` pin advanced
to `75fd8ed` by `update-pin.yml` run `30848873442` (commit `a2150b1f`) and tagged `v0.7.0` there.

**Read the Docs `stable` measured live 2026-08-04 (`41-HANDOFF.md` item 5, both projects):** root
`https://typsphinx.readthedocs.io/` → `/en/stable/` (302 → 200); `en` `stable` identifier
`75fd8ed5` (the v0.7.0 merge commit), `ja` `stable` identifier `a2150b1f` (the translations repo's
own v0.7.0 tag); both pages report `0.7.0`; both PDFs served (`en` 1,965,123 B / `ja` 2,152,807 B,
`application/pdf`). Both builds `finished` / `success`. No owner setting flips were needed — both
Default Versions were already `stable` from the v0.6.4 close.

**What shipped:** API reference pages became readable — monospace signatures with hanging-indent
wrapping and no margin overflow (SIG-01..09), description bodies and field lists indenting by
nesting depth off one shared `SHARED_INDENT_STEP` constant (IND-01..05, FLD-01..03), admonitions
re-bucketed onto a taxonomy the owner signed off against a desaturated render (ADM-01..06),
greenfield full-round-trip docutils citations with degradation hardening (CIT-01..06 + Phase 40.1),
two remaining compile fatals closed (MATH-02, TBL-03), and the GitHub Release body sourced from the
curated `## [0.7.0]` CHANGELOG section — the last of these delivered as a mechanism (REL-04) but
**not** exercised end to end by the release, see Blockers/Concerns; REL-05 (the release itself) is
complete.

**Standing invariants held:** zero new runtime dependencies; the `@preview` package count stayed at
four with no new version-lockstep site; every node-handler change carries its own recorded-RED
GATE-01 fixture — with v0.7.0's amended definition of RED (structural / regex / `pypdf`-text
assertions written before any code, since these defects compiled fine), and CIT-01 and TBL-03 as
the two classic-`TypstError` exceptions.

**Three durable lessons** (carried into PROJECT.md Key Decisions):

1. **The gate held under pressure rather than being laundered.** In Phase 40 four of nine gate
   selectors stayed RED after the handlers landed; all four were defects in the gate module itself,
   and the corrected module was re-proved 9/9 RED against the pre-fix translator three independent
   times before being trusted.

2. **A locked decision was reversed on evidence.** Shown a live render at UAT the owner overturned
   D-03 and re-opened an already-closed Phase 39 (5/5 verified) rather than filing the difference
   as debt.

3. **A recurring tooling hazard was made falsifiable.** `phase.complete` auto-flipping REL-04/REL-05
   against a CONTEXT decision was caught and reverted in Phase 41, then pre-empted in Phase 42 by
   `42-CLOSEOUT-GUARD.md`, which recorded the four at-risk lines verbatim with a file checksum. It
   did not recur — the hazard looks specific to release-prep phases rather than universal.

## Shipped Milestone (v0.6.5 — archived)

Full phase detail, success criteria, and decisions: [`milestones/v0.6.5-ROADMAP.md`](milestones/v0.6.5-ROADMAP.md)
and [`milestones/v0.6.5-REQUIREMENTS.md`](milestones/v0.6.5-REQUIREMENTS.md). Phase artifacts are
archived under `milestones/v0.6.5-phases/`.

**Delivered:** 2/2 v1 requirements across 2 phases / 8 plans — a document mixing prose and math no
longer aborts the Typst compile. The defect was root-caused **by measurement**, not from the
backlog's guess: `visit_math` participated in only one of the translator's three separator protocols
(paragraph, code-mode concat, list-item), so the fatal surfaced in list items, definition-list terms,
and collapsed confval field bodies rather than in plain paragraphs. Fixed on both the mitex and
native emission paths (+45 lines, `typsphinx/translator.py` only), pinned by a real-`typst.compile()`
GATE-01 fixture recorded RED pre-fix, and released as v0.6.5.

**Closeout type:** `override_closeout` — both phases were `phase_complete` with
`verification_status: passed` and both requirements complete, but no `v0.6.5-MILESTONE-AUDIT.md` was
produced (owner accepted at close, 2026-07-29: for a 2-phase / 2-requirement hotfix, Phase 35's
`35-RELEASE-EVIDENCE.md` had already discharged SC#1–SC#5 against live runs — full pytest, the
lint/type trio, the full-corpus `-b typstpdf` gate, and both docs dogfooding builds). 8 pending
todos acknowledged as deferred (below).

**Scope fence held:** Phase 35 was prep-only and took no irreversible action — `git tag -l v0.6.5`
and `git ls-remote --tags origin v0.6.5` were both empty when it finished. The publish half executed
here at close and is complete:

- PR #125 merged to `main` (13/13 CI checks green before merge); `v0.6.5` tagged on merge commit
  `839d77f` and pushed.

- Release run 30398631991 green end-to-end after owner approval of the `pypi` environment: PyPI
  `typsphinx 0.6.5` (wheel + sdist, uploaded 21:15:39–21:15:40Z) and GitHub Release `v0.6.5` with
  all three assets.

- `typsphinx-doc-translations` pin advanced to `839d77f` (`update-pin.yml` run 30398664663) and
  tagged `v0.6.5` at `1891a09` — the standing two-repository tagging cost, discharged.

- RTD `stable` measured live on both projects: en identifier `839d77f38ffa`, ja identifier
  `1891a0905322`; root → `/en/stable/` (302→200), `/ja/stable/` 200, both reporting `0.6.5`, both
  PDFs served. No owner setting flips were needed this time.

## Shipped Milestone (v0.6.4 — archived)

Full phase detail, success criteria, and decisions: [`milestones/v0.6.4-ROADMAP.md`](milestones/v0.6.4-ROADMAP.md),
[`milestones/v0.6.4-REQUIREMENTS.md`](milestones/v0.6.4-REQUIREMENTS.md), and
[`milestones/v0.6.4-MILESTONE-AUDIT.md`](milestones/v0.6.4-MILESTONE-AUDIT.md). Phase artifacts are
archived under `milestones/v0.6.4-phases/`.

**Delivered:** 13/13 v1 requirements across 6 phases / 33 plans — documentation hosting moved from
GitHub Pages to Read the Docs (en + ja behind RTD's flyout, the ja site built from the separate
`typsphinx-doc-translations` repository), the RTD-served PDFs proven to be `typstpdf`'s own artifacts,
the hand-rolled multilang machinery deleted (net −6.2k lines), every published URL rewritten and
real-HTTP-verified behind an advisory lychee guard, and the Pages host irreversibly torn down behind a
freshly re-taken serving gate.

**Closeout type:** `verified_closeout` — milestone audit passed (13/13 requirements, 6/6 phases
verified, integration all-wired); 5 pending todos acknowledged as deferred (see Deferred Items),
2 resolved todos filed to `todos/completed/`.

**Standing cost adopted this milestone:** every release tags **two** repositories — the parent and
`typsphinx-doc-translations` (`/ja/stable/` resolves against the translations repo's own tags).

## Performance Metrics

**Velocity:**

- Total plans completed (project cumulative): 108 (55 through v0.6.2 + 12 in v0.6.3 + 33 in v0.6.4 + 8 in v0.6.5)
- v0.6.3: 6 phases / 12 plans / 28 tasks, 2026-07-23 → 2026-07-25
- v0.6.4: 6 phases / 33 plans / 79 tasks, 2026-07-25 → 2026-07-28 (shipped)
- v0.6.5: 2 phases / 8 plans / 27 tasks, 2026-07-28 → 2026-07-29 (shipped) — the fastest milestone
  to date; a single-defect hotfix scope held end to end with zero scope creep.

- v0.7.0: 6 phases / 30 plans complete through Phase 39 (36: 4, 37: 9, 38: 9, 39: 8), started
  2026-07-29 — comparable in shape to v0.6.3/v0.6.4, but with a much higher test-migration load
  (10 files, 61 render-gate classes) carried per phase. Phase 37 alone migrated 9 exact-string
  assertions across 5 modules plus `golden.typ`'s 7 signature lines; Phase 39 re-measured its own
  census and found it matched both the discussion-time and planning-time counts exactly.

*Updated after each plan completion*

## Shipped Milestone (v0.6.3 — archived)

Full phase detail, success criteria, and decisions: [`milestones/v0.6.3-ROADMAP.md`](milestones/v0.6.3-ROADMAP.md)
and [`milestones/v0.6.3-REQUIREMENTS.md`](milestones/v0.6.3-REQUIREMENTS.md). Phase artifacts (PLAN /
SUMMARY / VERIFICATION / CONTEXT / RESEARCH) are archived under `milestones/v0.6.3-phases/`.

**Delivered:** 7/7 v1 requirements across 6 phases / 12 plans — the inert `typst_toctree_defaults`
deleted (CONF-05), captioned tables rendering as numbered, cross-referenceable Typst figures
(TBL-01/TBL-02), `typst_elements` `papersize`/`fontsize` reaching `project()` behind a fail-loud
allowlist (CONF-04), the orphan config doc and every phantom `typst_*` name purged (DOC-06/DOC-07),
and Typst's typesetting `lang` following Sphinx's own `language` conf (CONF-07). Closed on a live
full-corpus regression gate.

**Published 2026-07-25:** PR #121 merged to `main` (CI 13/13 green), tag `v0.6.3` pushed,
`release.yml` published `typsphinx==0.6.3` to PyPI (wheel + sdist) and created the GitHub Release.
Milestone branches deleted; only `main` and `gh-pages` remain — `gh-pages` is scheduled for deletion in
Phase 32 (CI-04).

**Closeout type:** `override_closeout` — all 6 phases were `phase_complete` with
`verification_status: passed` and all 7 requirements checked off, but no `v0.6.3-MILESTONE-AUDIT.md`
was produced (owner accepted at close, 2026-07-25: Phase 28's live re-run of the full-corpus gate,
full pytest suite, and both docs-build tox environments already covers the audit's requirement-coverage
and integration ground) and 9 pending todos were acknowledged as deferred (below).

**Closed at close, not deferred:** the bundled `examples/advanced` sample was unbuildable on two
independent axes — five `typst_elements` keys outside the CONF-04 allowlist, and `custom.typ` three
milestones behind on its `@preview` pins (`unknown variable: kai`). Repaired inline before the tag,
with `test_preview_version_sync.py` extended over `examples/**/*.typ` to close the drift channel.

## Accumulated Context

### Decisions

Cleared at v0.6.4 close — the full log lives in PROJECT.md Key Decisions (with outcomes) and the
archived `milestones/v0.6.4-ROADMAP.md`. Standing process decisions that carry forward:

- `branching_strategy: milestone` — ship unit is the milestone; final phase is prep-only Release;
  publish executes at `/gsd-complete-milestone`; push `main` to `origin` at every close.

- Every release tags **two** repositories (parent + `typsphinx-doc-translations`) — v0.6.4 D-07.
- Milestone invariant #4 (standing): "anywhere under X" success criteria are checked by a repo-wide
  grep at discovery time, never against the files a requirement happens to name.

- Run `/gsd-audit-milestone` before each close (v0.6.4 restored it; first verified_closeout since
  v0.4.4).

- Standing GATE-01 bar (since v0.6.0): every node-handler change ships a real
  `sphinx-build → typst.compile()` regression fixture, recorded **red against the unfixed code**
  before it is accepted as green. **v0.7.0 amends what "red" means** — see the Active Milestone
  section: every design defect in this milestone compiles fine today, so RED is a structural /
  regex / `pypdf`-text assertion defined before any code is written, except for CIT-01 (Phase 40),
  which keeps the classic `TypstError`.

### Pending Todos

**Eight of the ten open records are now v0.7.1 requirements** (promoted at roadmap creation
2026-08-04): `nested-table-clobbers-outer-table-state` → TBL-04,
`table-whitespace-only-title-anchor-divergence` → TBL-05,
`emit-id-anchors-docstring-claims-depart-figure-is-sole-skip-ids-user` → QUA-01,
`non-str-docname-typeerror-in-typstpdf-finish` → BLD-01,
`derive-typst-lang-duplicated-warning-block` → QUA-02, `project-md-unterminated-html-comments` →
QUA-03, `docs-changelog-page-stale-at-0-4-0` → DOC-12, and
`release-create-job-missing-uv-verify-end-to-end` → REL-04 (an open requirement, not merely a todo).
The dormant seed SEED-001 became CONF-08 + DOC-11. Each record stays **pending** until its phase
executes. Still deferred and NOT in scope: `add-sphinx-linkcheck-ci-job` (Future LNK-01) and
`modernize-typing-imports-drop-up006-up035-ignore` (forbidden by `CLAUDE.md`).

**Ten open in `.planning/todos/pending/`.** Nine when this close began: one
(`visit-desc-sig-name-docstring-unbalanced-asterisk-warning`) was filed to `todos/completed/` here
per `41-HANDOFF.md` item 7, and one was filed *by* this close
(`release-create-job-missing-uv-verify-end-to-end`, the REL-04 gap). A tenth was captured
post-release on 2026-08-04 (`docs-changelog-page-stale-at-0-4-0`, minor). All are acknowledged and
recorded in Deferred Items above; none blocks the release.

**Count as of 2026-08-04: 8 files in `.planning/todos/pending/`** (the "ten" above counts records
that have since been promoted to requirements or filed to `completed/`). The newest is
`toctree-heading-offset-ignored-because-visit-title-emits-abs` (translator, **major**), captured
2026-08-04: `visit_title` emits Typst's absolute `heading(level: N)`, which overrides the
`set heading(offset: 1)` that `visit_toctree` wraps its `include()`s in — so toctree'd documents
never nest and the PDF outline is flat. Fix is `depth:` instead of `level:`
(`level = offset + depth`), verified against typst-py 0.15.0. **Now mapped**: promoted to TOC-01 and
carried by the inserted Phase 44.1.

**Count as of 2026-08-04 (updated): 10 files in `.planning/todos/pending/`.** The newest is
`documented-custom-template-parameter-contract-is-wrong-and-t` (docs, writer, **major**), captured
2026-08-04 during the Phase 44.1 discussion. `docs/source/user_guide/templates.rst:187-192`
publishes the custom-template contract as `title` / `authors` / `date` / `body`, but
`writer.py:259-261` unconditionally also passes `toctree_maxdepth` / `toctree_numbered` /
`toctree_caption` whenever the master has a toctree — and Typst rejects undeclared named arguments.
Reproduced: the documented example verbatim fails with
`TypstError: unexpected argument: toctree_maxdepth`. Unrelated to TOC-01 and deliberately kept out
of Phase 44.1. Not mapped to a v0.7.1 requirement.

Deferred by explicit owner decision to v0.7.1+ (Phase 41 D-14, 4 items):

- **add-sphinx-linkcheck-ci-job** (ci, docs) — Future requirement LNK-01; `links.yml`'s repo-wide
  lychee check already covers the one new link this release adds.

- **non-str-docname-typeerror-in-typstpdf-finish** (builder, tests) — input-validation hardening.
- **derive-typst-lang-duplicated-warning-block** (template_engine) — refactor, no release bearing.
- **modernize-typing-imports-drop-up006-up035-ignore** (source) — **do not act on this until the
  todo lands**; `CLAUDE.md` carries the same instruction independently.

Planning-record hygiene (1):

- **project-md-unterminated-html-comments** (planning docs).

Filed at the v0.7.0 close (1):

- **release-create-job-missing-uv-verify-end-to-end** (ci, release) — the REL-04 gap above. Closes
  only when a real tag push runs `create-release` to completion.

Filed during v0.7.0 and still open (3):

- **table-whitespace-only-title-anchor-divergence** (translator, Phase 42).
- **emit-id-anchors-docstring-claims-depart-figure-is-sole-skip-ids-user** (translator, Phase 42
  review WR-01) — a stale docstring, deliberately not fixed in-phase so the change would not fall
  outside the SHA range Phase 42's SC#4/SC#6 evidence measured.

- **nested-table-clobbers-outer-table-state** (translator, Phase 42 review IN-02) — a real, severe,
  **pre-existing** bug: a table nested inside a `list-table` cell silently drops the outer table
  structure, because `in_table`/`table_cell_content` are scalars rather than a stack. Verified
  byte-identical pre- and post-Phase-42. **The strongest single candidate for the next milestone.**

One dormant seed: **SEED-001-readme-quickstart-typst-documents-pdf** (README Quick Start omits that
`.typ` output is not compiled to PDF unless `typst_documents` is set).

Promoted out of the backlog during v0.7.0 and now shipped: `citation-node-support-untracked`
(→ CIT-01..06), `visit-math-block-redundant-blank-line-in-list-items` (→ MATH-02),
`release-notes-body-from-changelog-section` (→ REL-04), `captioned-table-drops-preceding-target-label`
(→ TBL-03, backlog 999.2).

### Blockers/Concerns

**Phase 44.1 SC#2 rests on a falsified premise — a blocking decision waits in wave 2.** Measured
2026-08-04 during planning and re-measured independently by the orchestrator against the pinned
typst-py 0.15.0, through real `include()` calls on `tests/fixtures/integration_nested_toctree`:
Typst's `set heading(offset: N)` is an **absolute assignment** on the style chain, not an increment,
so a nested scope *replaces* its parent's offset instead of adding to it. `44.1-CONTEXT.md`
(`<code_context>` "Integration Points") and the source todo both assert that nested toctree scopes
"accumulate"; neither was verified and both are wrong. Consequence: the locked repair (emit `depth:`
in `visit_title`, leave `visit_toctree` untouched) satisfies **SC#1** — child resolves at 2 — but
leaves **SC#2 unmet**, the grandchild resolving at 2 rather than 3. Only
`context { set heading(offset: heading.offset + 1) }` yields 1 / 2 / 3 / 4. Meeting SC#2 therefore
requires widening a locked scope, which no planner or executor may do, so `44.1-03` stops as a
`checkpoint:decision` offering **option-a** (change `visit_toctree`; SC#2 met, scope widened, the two
`tests/test_toctree_requirement13.py` assertions change) or **option-b** (leave it; re-scope SC#2 as
unsatisfiable per the SC#3 precedent, file a todo, mark the SC#2 tests `xfail`). Both branches are
executable; the plan's acceptance criteria are split `Both options` / `Option-a only` /
`Option-b only`, and D-03's `templates/base.typ` fence holds either way.

**Owed from v0.7.0: REL-04.** The requirement — the GitHub Release body sourced from the curated
`## [X.Y.Z]` CHANGELOG section — is **not met**. The extractor Phase 41 wrote is correct and
hand-verified, but the `create-release` job calls `uv run …` with no `astral-sh/setup-uv` step
(`validate` and `build` both have one; `create-release` never needed uv until REL-04 wired the
extractor into it), so the first real tag push died at `uv: command not found`, exit 127. The
release body and its missing wheel/sdist were repaired by hand; `release.yml`'s `create-release` job
gained the two missing steps on `main` afterwards. **REL-04 closes only when a real tag push runs
`create-release` to completion** — carried to v0.7.1, and it is the only item in PROJECT.md's
Requirements Active.

**Both defects this close surfaced share one cause: the milestone branch was never pushed until the
release PR.** The Windows lanes went RED on PR #129 (three Phase 37 signature render-gate modules
read `.typ` with a bare `Path.read_text()`, so Windows' cp1252 could not decode UTF-8 — fixed in
`9a544db` before merge), and `create-release` had never run against a real tag. Neither Windows CI
nor a tag push touched the branch during any of the eight phases. Pushing the milestone branch early
— even without opening a PR — would have caught the first one eight phases sooner.

**Carried forward, non-blocking:** eight pending todos (Deferred Items) and one dormant seed. The
most significant is `nested-table-clobbers-outer-table-state` — a real, severe, pre-existing bug
where a table nested inside a `list-table` cell silently drops the outer table structure. It is not
a v0.7.0 regression (verified byte-identical pre- and post-Phase-42) and is the strongest single
candidate for the next milestone.

**Nothing owed from v0.6.5.** All six `35-HANDOFF.md` items are discharged, including item 4 (the
RTD `stable` confirmation), which was measured rather than left owner-manual: both projects'
`stable` rebuilt on the new tags and serve `0.6.5`. The only carried cost is cosmetic and filed —
the GitHub Release body is still `release.yml`'s commit dump (D-11) — and it is now scoped as
v0.7.0's REL-04 (Phase 41).

**Nothing owed from v0.6.4.** All owner-manual steps from `33-HANDOFF.md` completed at close
(2026-07-28, measured via the RTD public API + real fetches): both RTD Default branches → `main`, both
Default Versions → `stable`, `.gitmodules` `branch` → `main` in `typsphinx-doc-translations`; root URL
redirects to `/en/stable/` (200) and `/ja/stable/` serves the same release; Issue #119 closed.

**Three carried Warnings from 30.1's review (quality, not gaps):** `contributing.rst` Translations
section lacks a toolchain-install step; `docs/source/_typst/custom_template.typ` is an unguarded
FOURTH `@preview` version-lockstep site (the sync test watches 3 surfaces + `examples/`); the live
translations-repo manifests have no structural test coverage in this repository. Out of v0.7.0
scope, but note the second one is adjacent to Phase 41's invariant check — any new font selection
this milestone introduces touches that same file.

**v0.7.0 risk — SIG-07 RESOLVED at Phase 37 planning (2026-08-01), and the answer inverted the
premise.** The corpus was measured (1,445 real `desc_signature` nodes from Sphinx v9.1.0 `doc/`):
worst case is a 311-char signature / 41-char qualname / 143pt widest unbreakable token, against a
production column width of **453.54pt** read from Typst's own `layout()`/`measure()`. **Nothing in
the real corpus overflows.** The `2.5em` hanging-indent and ZWSP figures in `37-CONTEXT.md` came
from an artificially narrow 9cm probe frame. Phase 37 keeps the mechanism (`par(hanging-indent:)`

+ U+200B after each `.`) because it is cheap and correct, but its GATE-01 RED fixture is built from

a **synthetic ~90+ char dotted identifier** — a corpus-derived fixture cannot go RED. The real
corpus worst case serves as a non-regression control. Two further measured findings the executor
needs: `block()`'s default spacing adds ~26.5pt per boundary (so the wrapper must be
`block(above: 0pt, below: 0pt, sticky: true, …)` or SIG-08's defect returns), and ZWSP poisons
`pypdf` extraction (a spurious U+200B appears at an unrelated glyph boundary), so every compiled-PDF
assertion must strip U+200B first. Also open: any new `set text(font: ...)` for
monospace signatures can silently shadow the `Noto Serif CJK JP` fallback in the `ja` build — Typst
emits neither a warning nor an error, so the D-03 four-check bar is a Phase 41 success criterion.

UI note (standing): this project's phases are typesetting/config/docs/hosting work, **not** frontend
UI — `ui.plan-gate` false-positives on PDF/HTML/template wording; use `--skip-ui`. The v0.7.0
roadmap deliberately carries no `UI hint` annotations for this reason, even though phases 37–39 use
words like "layout", "page", and "render". Same for `api-coverage.verify-pre` false-positives on
prose describing compile/render/API-read evidence (three recorded overrides in v0.6.4). GATE-01
note: honest-verifier — abstain to `human_needed` rather than assert a truth without direct
evidence.

### Roadmap Evolution

- **2026-07-28** — v0.6.5 roadmap created: Phases 34–35, continuing numbering from v0.6.4's Phase 33.
  Backlog item **999.1** promoted into Phase 34 as requirement MATH-01 and removed from ROADMAP.md's
  Backlog section (the section itself retained with its preamble).

- **2026-07-29** — v0.6.5 closed and archived. ROADMAP.md collapsed to a one-line milestone entry
  plus a `<details>` block; the Backlog section is still empty of `999.x` items, and now names the
  8 pending todos as the next milestone's candidate pool. Next milestone starts at Phase 36.

- **2026-07-29** — v0.7.0 roadmap created: **Phases 36–41**, 32/32 v1 requirements mapped, zero
  orphans. Derived from this milestone's requirements rather than transcribed from
  `research/SUMMARY.md`'s "Reconciled Build Order", whose Phase 1 (style-module scaffolding) no
  longer exists after the owner dropped the bundled module. Three pending todos promoted into the
  milestone (citation support, `visit_math_block` blank line, `release.yml` CHANGELOG extraction).
  REQUIREMENTS.md's coverage tally was corrected from "29 total" to the measured **32** — a tally
  error only; no requirement was added, removed, or reworded.

- Phase 36 edited: SC#3 corrected from measurement: the redundant blank line is after the math, not before; PDF-extracted-text RED is impossible (fix yields a byte-identical PDF), so the PDF assertion becomes an invariance guard
- **2026-08-02** — Phase **40.1 inserted** after Phase 40 (URGENT): Citation Degradation Hardening.
  Closes `40-REVIEW.md`'s WR-01 / WR-02 / WR-03 — three graceful-degradation gaps in the citation
  code, of which WR-01 can reach a real Typst compile fatal (a `link()` to a label nothing attaches)
  — each with a recorded-RED fixture per milestone invariant #4. Kept **out of** Phase 41 by owner
  decision during Phase 41's discussion (`41-CONTEXT.md` D-11): closing them there would have made
  the release-prep phase enlarge the very proof obligation its own SC#4 discharges, on the
  translator, immediately before a release. Consequence recorded in both files: Phase 41's SC#4
  sweep must cover 40.1's node-handler changes, so 40.1 executes first. No requirement IDs were
  added, removed, or reworded — 40.1 hardens code CIT-01/CIT-03/CIT-04 already delivered.

- **2026-08-04** — v0.7.1 roadmap created: **Phases 43–46**, 11/11 v1 requirements mapped, zero
  orphans. Derived from `REQUIREMENTS.md` alone — no `research/SUMMARY.md` exists for this milestone
  (research deliberately skipped, owner decision 2026-08-04). Eight pending todos plus the dormant
  SEED-001 were promoted into requirements; `release-create-job-missing-uv-verify-end-to-end` is
  carried as the open requirement REL-04 rather than as a todo. Milestone invariant #5 is new and is
  encoded as Phase 43's SC#5 (push the milestone branch to `origin` from the first phase). The final
  phase (46) is prep-only, pairing REL-06 with REL-04's verification-and-handoff share only —
  REL-04 itself closes at the publish.

- **2026-08-03** — Backlog item **999.2 promoted into v0.7.0 as Phase 42** at `/gsd-review-backlog`,
  by owner decision, *after* Phase 41 had already completed. Unlike every prior amendment in this
  log, this one **adds a requirement to an already-complete milestone**: new requirement **TBL-03**
  (Tables and labels — a captioned table preceded by a standalone target must emit both labels),
  v1 total 32 → 33, milestone 7/7 → 7/8, milestone line Phases 36–41 → 36–42. The owner also decided
  the **v0.7.0 publish blocks on Phase 42** rather than shipping first and deferring the fix, so
  `/gsd-complete-milestone` is no longer the next action. Two consequences recorded in both files:
  Phase 41's curated `## [0.7.0]` CHANGELOG entry (SC#2) has no TBL-03 line, and its SC#4
  invariant sweep was measured over a SHA range ending before Phase 42 — Phase 42's own SC#6 owns
  reconciling both before the publish. TBL-03 also joins CIT-01 as milestone invariant #4's second
  classic-`TypstError`-RED exception, and invariant #4's wording was amended accordingly. Nothing was
  removed or re-assigned away from another phase. The ROADMAP Backlog section is now empty; the next
  item filed there is 999.3.

- Phase 44.1 inserted after Phase 44: Relative Heading Depth for Toctree Nesting — TOC-01 added; toctree set heading(offset: 1) is inert because visit_title emits absolute level: (URGENT)
- Phase 45.1 inserted after Phase 45: Custom-Template Parameter Contract Correction (DOC-13) — documented 4-param contract vs. the toctree_*/typst_elements parameters actually passed; fix route left open for discuss-phase (URGENT)
- Phase 44.2 inserted after Phase 44: typst_documents Title and Author Consumption (CONF-09) — REVERSES Phase 44's D-02; entry[2]/entry[3] wiring lands in v0.7.1 after all; second CHANGELOG callout owed (URGENT)

## Deferred Items

Items acknowledged and carried forward from milestone closes:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Forward-ecosystem | CFG-01 (was FWD-03): user-configurable `@preview` versions | Deferred to v2 | v0.5.0 scoping |
| Cross-OS verification | XOS-01: cross-OS docs-PDF CI (macOS/Windows) | Deferred to v0.6.x+ | v0.5.0 scoping |
| Graceful-degrade | DEG-03: real rendering (not placeholder) for `graphviz` / `inheritance_diagram` | Deferred to v2 (image pipeline) | v0.6.1 scoping |
| Cross-reference | XREF-02: link `manpage` / xrefs to external URLs via a configured base URL | Deferred beyond v0.6.2 | v0.6.1 scoping |
| Config | CONF-06: `typst_elements` keys beyond papersize/fontsize/**lang** — `lang` was split out as CONF-07 and promoted to v1 on 2026-07-25 (Phase 27.1); the remaining keys stay deferred | Deferred to future milestone | v0.6.3 scoping |
| Verification | No `v0.6.3-MILESTONE-AUDIT.md` produced (owner accepted; Phase 28's live gate re-run stood in) | Accepted at close | v0.6.3 close |
| Docs/CI | LNK-01: `sphinx-build -b linkcheck` CI job (structurally blind to README/pyproject — CI-05 covers the real class) | Deferred to Future | v0.6.4 scoping |
| i18n | I18N-03: a Japanese PDF | **Promoted to v1 2026-07-26** (Phase 30 discussion D-04) — assigned to Phase 30.1 | was v0.6.4 scoping |
| RTD | RTD-05: pull-request preview builds (one owner-side checkbox, no repo work, enable any time) | Deferred to Future | v0.6.4 scoping |
| RTD | RTD-06: documentation versions for tags before `v0.6.4` (structurally impossible — no pre-v0.6.4 tag contains `.readthedocs.yaml`) | Deferred to Future | v0.6.4 scoping |
| UX (accepted loss) | Browser-language auto-redirect at the documentation root — RTD redirects to a *version*, never auto-detects a *language*; reimplementing it would re-add the template code I18N-02 deletes | Accepted regression | v0.6.4 scoping |
| SEO (accepted loss) | Old `github.io` URLs 404 with no redirect stubs (owner decision 2026-07-25) | Accepted cost | v0.6.4 scoping |
| Quality (v0.6.4 review) | 30.1 Warnings: contributing.rst toolchain step; `custom_template.typ` fourth lockstep site; no structural tests over translations-repo manifests | Out of v0.6.5 and v0.7.0 scope | v0.6.5 scoping |
| Todo (ci, docs) | add-sphinx-linkcheck-ci-job | Pending backlog | v0.6.2 close |
| Todo (translator, examples) | citation-node-support-untracked | **Promoted to v0.7.0 Phase 40** (CIT-01..CIT-06) 2026-07-29 | v0.6.2 close |
| Todo (builder) | non-str-docname-typeerror-in-typstpdf-finish | Pending backlog | v0.6.2 close |
| Todo (typing) | modernize-typing-imports-drop-up006-up035-ignore | Pending backlog | v0.6.2 close |
| Todo (template_engine) | derive-typst-lang-duplicated-warning-block (review IN-01, Info) | Pending backlog | v0.6.3 close |
| Verification | No `v0.6.5-MILESTONE-AUDIT.md` produced (owner accepted; Phase 35's `35-RELEASE-EVIDENCE.md` live-run coverage stood in for a 2-phase hotfix) | Accepted at close | v0.6.5 close |
| Todo (translator) | visit-math-block-redundant-blank-line-in-list-items — Phase 34 review WR-01, deferred by D-05 (fixing it pre-release would force re-deriving the GATE-01 fixture) | **Promoted to v0.7.0 Phase 36** (MATH-02) 2026-07-29 | v0.6.5 close |
| Todo (ci) | release-notes-body-from-changelog-section — `release.yml` release body still a ~296-line commit dump (D-11) | **Promoted to v0.7.0 Phase 41** (REL-04) 2026-07-29 | v0.6.5 close |
| Todo (docs) | project-md-unterminated-html-comments | Pending backlog | v0.6.5 close |
| Styling (v0.7.0 scoping) | STY-01/STY-02/STY-03: user-overridable per-directive styling, the bundled Typst style module, and its Typst Universe publication | Deferred to Future (goal narrowed by owner) | v0.7.0 scoping |
| Rendering (v0.7.0 scoping) | TOP-01: box `.. contents::` (local TOC) as the reference does — D-05's box-less choice stands now that the reference is not an authority | Deferred to Future | v0.7.0 scoping |
| Citations (v0.7.0 scoping) | CIT-07: `sphinxcontrib-bibtex` support (`:cite:` role, `.bib` files) — a different node family; would use Typst's native `bibliography()`/`cite()` | Deferred to Future | v0.7.0 scoping |
| Verification | No `v0.7.0-MILESTONE-AUDIT.md` produced (owner accepted: `init.manager` reported all 8 phases `phase_complete=true` / `verification_status=passed`, and every v1 requirement except the two publish-gated REL rows was already Complete) | Accepted at close | v0.7.0 close |
| Todo (ci, docs) | add-sphinx-linkcheck-ci-job | Acknowledged, deferred to v0.7.1+ (Phase 41 D-14 #1; `links.yml`'s repo-wide lychee check already covers this release's one new link) | v0.7.0 close |
| Todo (builder, tests) | non-str-docname-typeerror-in-typstpdf-finish | Acknowledged, deferred to v0.7.1+ (Phase 41 D-14 #2 — a builder behaviour change unrelated to REL-04/REL-05) | v0.7.0 close |
| Todo (source) | modernize-typing-imports-drop-up006-up035-ignore | Acknowledged, deferred to v0.7.1+ (Phase 41 D-14 #4, **doubly deliberate** — `CLAUDE.md` independently instructs "don't modernize typing imports until that todo lands") | v0.7.0 close |
| Todo (template_engine) | derive-typst-lang-duplicated-warning-block | Acknowledged, deferred to v0.7.1+ (Phase 41 D-14 #3 — a refactor with no release bearing) | v0.7.0 close |
| Todo (planning docs) | project-md-unterminated-html-comments | Acknowledged, deferred — planning-record hygiene only, no code or published-output effect | v0.7.0 close |
| Todo (translator) | visit-desc-sig-name-docstring-unbalanced-asterisk-warning | **Resolved by Phase 41 plan 41-03 (D-12); filed to `todos/completed/` at this close** per `41-HANDOFF.md` item 7 | v0.7.0 close |
| Todo (translator) | table-whitespace-only-title-anchor-divergence | Acknowledged, filed during Phase 42 — a divergence adjacent to TBL-03 but outside its requirement | v0.7.0 close |
| Todo (translator) | emit-id-anchors-docstring-claims-depart-figure-is-sole-skip-ids-user | Acknowledged, filed during Phase 42 (review WR-01) — deliberately not fixed in-phase because touching `translator.py` after the SC#4/SC#6 artifacts were recorded would move the change outside the SHA range they measured | v0.7.0 close |
| Todo (translator) | nested-table-clobbers-outer-table-state | Acknowledged, filed during Phase 42 (review IN-02) — a real, severe, **pre-existing** bug verified byte-identical pre- and post-fix: a table nested in a `list-table` cell silently drops the outer table structure because `in_table`/`table_cell_content` are scalars, not a stack. Did not block v0.7.0; a strong candidate for the next milestone | v0.7.0 close |
| Seed (docs) | SEED-001-readme-quickstart-typst-documents-pdf — README Quick Start does not say that `.typ` files are not compiled to PDF unless `typst_documents` is configured | Dormant; never scoped into v0.7.0 | v0.7.0 close |
| Todo (ci, release) | release-create-job-missing-uv-verify-end-to-end — REL-04's `create-release` job failed on the v0.7.0 tag push (`uv: command not found`); workflow fixed on `main`, release repaired by hand, but the automation is still unproven | **Carried to v0.7.1 as an open requirement**, not merely a todo | v0.7.0 close |

## Session Continuity

**Resume file:** .planning/phases/44.1-relative-heading-depth-for-toctree-nesting/44.1-CONTEXT.md
`.planning/milestones/v0.7.0-phases/`.

Last session: 2026-08-04T16:55:13.963Z
Stopped at: Phase 44.1 context revised: SC#2 = option-a (D-07); plans removed for regeneration
Resume: `/gsd-plan-phase 43` (Table State Correctness — Nested Tables + Empty-Title Anchors).

## Operator Next Steps

- ✅ Done at the close: Read the Docs `stable` measured green at `v0.7.0` on both projects (see
  Shipped Milestone). Nothing owner-manual is outstanding.

- Plan the first phase with `/gsd-plan-phase 43`.
- **Phase 43 must push the milestone branch to `origin`** (milestone invariant #5) so CI — including
  the Windows lanes — runs against every subsequent phase rather than first meeting the branch at
  the release PR.
