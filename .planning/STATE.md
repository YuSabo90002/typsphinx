---
gsd_state_version: 1.0
milestone: v0.7.0
milestone_name: API rendering design overhaul
status: planning
last_updated: "2026-07-29T11:28:31.664Z"
last_activity: 2026-07-29
progress:
  total_phases: 0
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-29 at the v0.7.0 milestone start)

**Core value:** The `typst`/`typstpdf` builders produce correct, compilable, faithfully-rendered output — and the documented configuration actually takes effect, so a user who copies a documented `conf.py` example gets what the docs promise. The same standard applies to the *publishing* surface: a URL the project publishes must actually resolve, and the PDF a reader downloads must be the one typsphinx itself produced.
**Current focus:** Milestone v0.7.0 — API rendering design overhaul. Defining requirements; phase numbering starts at Phase 36.

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-07-29 — Milestone v0.7.0 started

## Active Milestone (v0.7.0 — API rendering design overhaul)

Started 2026-07-29. Phase numbering continues at **Phase 36** (v0.6.5 ended at 35).

**Goal:** Replace the provisionally-chosen Typst representations of the API-description and
admonition directive families with a real typographic design, so autodoc/API pages render as a
readable reference document instead of a flat wall of proportional bold text.

**Scope (owner-confirmed 2026-07-29, after a mid-scoping concept rethink):** `desc_*` +
`field_list` redesign; admonition / rubric / topic redesign; full-round-trip `citation` support
(greenfield — zero handlers exist today, and a citation currently fails the Typst compile
outright); the v0.6.5 WR-01 `visit_math_block` blank-line todo; `release.yml`'s release-notes body
sourced from the CHANGELOG section; v0.7.0 release prep.

**Dropped during the rethink (2026-07-29):**

- **User-overridable per-directive styling** — the original concept had typsphinx ship a Typst
  module whose functions users could restyle from their own template. Research measured that
  Typst's `show`/`set` selectors accept only genuine element functions (`typst error: only element
  functions can be used as selectors`), and user-defined element types are unimplemented upstream
  (`typst/typst#147`, open since 2023-03-22). Label selectors (`show <label>: …`) were verified to
  deliver the equivalent capability, but the owner narrowed the goal to "typsphinx itself produces
  good output," so the whole user-configurability axis is out
- **The bundled style module itself** — with user override no longer a goal, the translator emits
  complete Typst directly. Every generated `.typ` stays self-contained; no builder change; one
  fewer phase. Accepted costs: more verbose `.typ`, and the shared indent constant living only on
  the Python side
- **Typst Universe publication** — was only ever the module's future; moot now

**Reference (demoted from "authority" during the rethink):** Sphinx's own LaTeX-rendered PDF —
`https://app.readthedocs.org/projects/sphinx/downloads/pdf/master/`, measured live 2026-07-29 as
`200` / `application/pdf` / 3,227,122 B / **703 pages** / `pdfTeX-1.40.22` / `LaTeX with hyperref`,
built 2026-07-22. It renders the same Sphinx `doc/` corpus that `tests/test_corpus_gate.py` drives
through `-b typstpdf`, and needs **no TeX toolchain** (none is installed here). Its measured values
are the starting point — the ≈22–25pt indent quantum, the per-node font roles, the four admonition
colour buckets — but the milestone deliberately diverges where Typst can do better. Exact
parameters readable from the `.sty` sources in the venv (`sphinxlatexobjects.sty` 386 lines,
`sphinxlatexadmonitions.sty` 408, `sphinxpackageboxes.sty` 827).

**Consequence — success criteria split in two:** mechanically checkable structural properties
(emitted through `raw(...)` not `text(...)`; body indent non-zero; a nested member's left edge
strictly greater than its parent's, via `pypdf` bounding boxes) versus human visual UAT for the
aesthetic judgement. Requirements must draw that line per item. The reference's `master`-vs-`v9.1.0`
version skew mattered only under page-by-page comparison and is now moot.

**GATE-01 methodology change (this milestone):** every prior fixture proved a compile fatal. Every
design defect here **compiles successfully today**, so RED cannot be `TypstError` — each phase
defines a structural / regex / `pypdf` RED assertion before any code is written. Citation is the
exception and keeps the classic RED.

`.planning/REQUIREMENTS.md` was archived and removed at the v0.6.5 close; this milestone defines a
fresh one.

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
  before it is accepted as green.

### Pending Todos

Eight open in `.planning/todos/pending/`, all acknowledged as deferred at the v0.6.5 close and the
primary candidate pool for the next milestone's scoping.

Carried from v0.6.2–v0.6.4 (5) — named Out of Scope in v0.6.5's own REQUIREMENTS.md (minimal hotfix):

- **add-sphinx-linkcheck-ci-job** (ci, docs) — deferred as Future requirement LNK-01; CI-05's
  repo-wide real-HTTP check covers the real failure class.

- **citation-node-support-untracked** (translator, examples) — `visit_citation` handler absent.
- **non-str-docname-typeerror-in-typstpdf-finish** (builder) — input-validation hardening.
- **modernize-typing-imports-drop-up006-up035-ignore** (typing) — do not "modernize" until it lands.
- **derive-typst-lang-duplicated-warning-block** (template_engine) — review IN-01 (Info), waived.

Filed during v0.6.5 (3) — recorded deliberate deferrals, not oversights:

- **visit-math-block-redundant-blank-line-in-list-items** (translator) — Phase 34 review WR-01;
  `visit_math_block`'s pre-existing unconditional `"\n\n"` doubles with the new
  `list_item_needs_separator` flag, leaving one redundant blank line. Deferred by D-05 because
  fixing it would force re-deriving the GATE-01 fixture's expected strings and re-running the
  full-corpus gate immediately before a release.

- **release-notes-body-from-changelog-section** (ci) — D-11; `release.yml` should extract the
  `## [X.Y.Z]` CHANGELOG section instead of dumping `git log --pretty` (~296 lines at v0.6.4).

- **project-md-unterminated-html-comments** (docs) — PROJECT.md hygiene.

Resolved and filed at the v0.6.4 close: **github-io-doc-links-404-missing-en-prefix** (Phase 31) and
**docs-usage-installation-orphan-class** (Phase 30) → `todos/completed/`.

### Blockers/Concerns

**Nothing owed from v0.6.5.** All six `35-HANDOFF.md` items are discharged, including item 4 (the
RTD `stable` confirmation), which was measured rather than left owner-manual: both projects'
`stable` rebuilt on the new tags and serve `0.6.5`. The only carried cost is cosmetic and filed —
the GitHub Release body is still `release.yml`'s commit dump (D-11).

**Nothing owed from v0.6.4.** All owner-manual steps from `33-HANDOFF.md` completed at close
(2026-07-28, measured via the RTD public API + real fetches): both RTD Default branches → `main`, both
Default Versions → `stable`, `.gitmodules` `branch` → `main` in `typsphinx-doc-translations`; root URL
redirects to `/en/stable/` (200) and `/ja/stable/` serves the same release; Issue #119 closed.

**Three carried Warnings from 30.1's review (quality, not gaps):** `contributing.rst` Translations
section lacks a toolchain-install step; `docs/source/_typst/custom_template.typ` is an unguarded
FOURTH `@preview` version-lockstep site (the sync test watches 3 surfaces + `examples/`); the live
translations-repo manifests have no structural test coverage in this repository. All out of v0.6.5
scope.

UI note (standing): this project's phases are typesetting/config/docs/hosting work, **not** frontend
UI — `ui.plan-gate` false-positives on PDF/HTML/template wording; use `--skip-ui`. Same for
`api-coverage.verify-pre` false-positives on prose describing compile/render/API-read evidence (three
recorded overrides in v0.6.4). GATE-01 note: honest-verifier — abstain to `human_needed` rather than
assert a truth without direct evidence.

### Roadmap Evolution

- **2026-07-28** — v0.6.5 roadmap created: Phases 34–35, continuing numbering from v0.6.4's Phase 33.
  Backlog item **999.1** promoted into Phase 34 as requirement MATH-01 and removed from ROADMAP.md's
  Backlog section (the section itself retained with its preamble).

- **2026-07-29** — v0.6.5 closed and archived. ROADMAP.md collapsed to a one-line milestone entry
  plus a `<details>` block; the Backlog section is still empty of `999.x` items, and now names the
  8 pending todos as the next milestone's candidate pool. Next milestone starts at Phase 36.

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
| Quality (v0.6.4 review) | 30.1 Warnings: contributing.rst toolchain step; `custom_template.typ` fourth lockstep site; no structural tests over translations-repo manifests | Out of v0.6.5 scope | v0.6.5 scoping |
| Todo (ci, docs) | add-sphinx-linkcheck-ci-job | Pending backlog | v0.6.2 close |
| Todo (translator, examples) | citation-node-support-untracked | Pending backlog | v0.6.2 close |
| Todo (builder) | non-str-docname-typeerror-in-typstpdf-finish | Pending backlog | v0.6.2 close |
| Todo (typing) | modernize-typing-imports-drop-up006-up035-ignore | Pending backlog | v0.6.2 close |
| Todo (template_engine) | derive-typst-lang-duplicated-warning-block (review IN-01, Info) | Pending backlog | v0.6.3 close |
| Verification | No `v0.6.5-MILESTONE-AUDIT.md` produced (owner accepted; Phase 35's `35-RELEASE-EVIDENCE.md` live-run coverage stood in for a 2-phase hotfix) | Accepted at close | v0.6.5 close |
| Todo (translator) | visit-math-block-redundant-blank-line-in-list-items — Phase 34 review WR-01, deferred by D-05 (fixing it pre-release would force re-deriving the GATE-01 fixture) | Pending backlog | v0.6.5 close |
| Todo (ci) | release-notes-body-from-changelog-section — `release.yml` release body still a ~296-line commit dump (D-11) | Pending backlog | v0.6.5 close |
| Todo (docs) | project-md-unterminated-html-comments | Pending backlog | v0.6.5 close |

## Session Continuity

**Resume file:** — (no phase in flight)

Last session: 2026-07-29
Stopped at: Milestone v0.6.5 closed, archived, and published.
Resume: `/gsd-new-milestone`.

## Operator Next Steps

- Start the next milestone with /gsd-new-milestone
